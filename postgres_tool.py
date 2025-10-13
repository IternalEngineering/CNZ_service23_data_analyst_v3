#!/usr/bin/env python
"""
PostgreSQL Direct Connection Tool for Claude SDK Agent
Provides direct database access for schema modifications and data operations
"""
import os
import asyncpg
from typing import Dict, List, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables - try multiple paths
env_paths = [
    Path(__file__).parent.parent / '.env',  # ../crewai_service/.env
    Path(__file__).parent / '.env',          # ./data_analyst_agent/.env
    Path.cwd() / '.env',                     # current directory
]

for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)
        break


class PostgreSQLTool:
    """Direct PostgreSQL connection tool for write operations"""

    def __init__(self):
        # Get database credentials from environment
        self.host = os.getenv('POSTGRES_HOST', 'urbanzero-db.c5qeo4ayy5u5.eu-west-2.rds.amazonaws.com')
        self.port = int(os.getenv('POSTGRES_PORT', 5432))
        self.database = os.getenv('POSTGRES_DATABASE', 'postgres')
        self.user = os.getenv('POSTGRES_USER')
        self.password = os.getenv('POSTGRES_PASSWORD')

        if not self.user or not self.password:
            raise ValueError("POSTGRES_USER and POSTGRES_PASSWORD must be set in .env file")

        self.connection_string = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}?sslmode=require"
        self.pool = None

    async def initialize(self):
        """Initialize connection pool"""
        if not self.pool:
            self.pool = await asyncpg.create_pool(
                self.connection_string,
                min_size=1,
                max_size=5,
                command_timeout=60
            )

    async def close(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
            self.pool = None

    async def execute_query(self, sql: str, params: tuple = None, fetch: bool = True) -> Dict[str, Any]:
        """
        Execute SQL query with optional parameters

        Args:
            sql: SQL query to execute
            params: Query parameters (for parameterized queries)
            fetch: Whether to fetch results (False for INSERT/UPDATE/DELETE/ALTER)

        Returns:
            Query results or execution status
        """
        try:
            await self.initialize()

            async with self.pool.acquire() as conn:
                if fetch:
                    # SELECT queries - fetch results
                    rows = await conn.fetch(sql, *(params or ()))
                    return {
                        "success": True,
                        "data": [dict(row) for row in rows],
                        "row_count": len(rows)
                    }
                else:
                    # INSERT/UPDATE/DELETE/ALTER/CREATE/DROP - execute without fetch
                    result = await conn.execute(sql, *(params or ()))
                    return {
                        "success": True,
                        "message": result,
                        "affected_rows": result.split()[-1] if result else "0"
                    }

        except asyncpg.PostgresError as e:
            return {
                "success": False,
                "error": f"PostgreSQL error: {str(e)}",
                "error_code": e.sqlstate if hasattr(e, 'sqlstate') else None
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Query failed: {str(e)}"
            }

    async def add_column(self, table: str, column_name: str, column_type: str, default_value: Any = None) -> Dict[str, Any]:
        """
        Add a new column to a table

        Args:
            table: Table name
            column_name: Name of new column
            column_type: SQL data type (e.g., INTEGER, VARCHAR(255), TEXT)
            default_value: Default value for the column

        Returns:
            Operation result
        """
        sql = f"ALTER TABLE {table} ADD COLUMN {column_name} {column_type}"

        if default_value is not None:
            if isinstance(default_value, str):
                sql += f" DEFAULT '{default_value}'"
            else:
                sql += f" DEFAULT {default_value}"

        sql += ";"

        return await self.execute_query(sql, fetch=False)

    async def drop_column(self, table: str, column_name: str) -> Dict[str, Any]:
        """Drop a column from a table"""
        sql = f"ALTER TABLE {table} DROP COLUMN {column_name};"
        return await self.execute_query(sql, fetch=False)

    async def rename_column(self, table: str, old_name: str, new_name: str) -> Dict[str, Any]:
        """Rename a column"""
        sql = f"ALTER TABLE {table} RENAME COLUMN {old_name} TO {new_name};"
        return await self.execute_query(sql, fetch=False)

    async def get_table_schema(self, table: str) -> Dict[str, Any]:
        """Get table schema information"""
        sql = """
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = $1
            ORDER BY ordinal_position;
        """
        return await self.execute_query(sql, params=(table,), fetch=True)

    async def list_tables(self) -> Dict[str, Any]:
        """List all tables in current schema"""
        sql = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """
        return await self.execute_query(sql, fetch=True)


# Tool definition for Claude SDK
def get_postgres_tool_definition():
    """Get tool definition for Claude SDK"""
    return {
        "name": "postgres_direct",
        "description": """Direct PostgreSQL database access for schema modifications and data operations.

        Use this tool when you need to:
        - ALTER TABLE (add/drop/rename columns)
        - CREATE or DROP tables
        - INSERT, UPDATE, DELETE data
        - Get table schemas
        - Execute DDL or DML operations that MindsDB doesn't support

        Available operations:
        - add_column: Add a new column to a table
        - drop_column: Remove a column from a table
        - rename_column: Rename an existing column
        - get_schema: Get table schema information
        - list_tables: List all tables in database
        - custom_sql: Execute custom SQL (SELECT, INSERT, UPDATE, DELETE, ALTER, etc.)
        """,
        "input_schema": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": [
                        "add_column",
                        "drop_column",
                        "rename_column",
                        "get_schema",
                        "list_tables",
                        "custom_sql"
                    ],
                    "description": "Database operation to perform"
                },
                "table": {
                    "type": "string",
                    "description": "Table name (required for table operations)"
                },
                "column_name": {
                    "type": "string",
                    "description": "Column name (required for column operations)"
                },
                "column_type": {
                    "type": "string",
                    "description": "SQL data type (e.g., INTEGER, VARCHAR(255), TEXT) - required for add_column"
                },
                "default_value": {
                    "type": ["string", "number", "null"],
                    "description": "Default value for new column (optional for add_column)"
                },
                "old_column_name": {
                    "type": "string",
                    "description": "Current column name (required for rename_column)"
                },
                "new_column_name": {
                    "type": "string",
                    "description": "New column name (required for rename_column)"
                },
                "sql": {
                    "type": "string",
                    "description": "Custom SQL query (required for custom_sql operation)"
                },
                "fetch_results": {
                    "type": "boolean",
                    "description": "Whether to fetch results (True for SELECT, False for INSERT/UPDATE/DELETE/ALTER)",
                    "default": True
                }
            },
            "required": ["operation"]
        }
    }


async def execute_postgres_tool(
    operation: str,
    table: Optional[str] = None,
    column_name: Optional[str] = None,
    column_type: Optional[str] = None,
    default_value: Optional[Any] = None,
    old_column_name: Optional[str] = None,
    new_column_name: Optional[str] = None,
    sql: Optional[str] = None,
    fetch_results: bool = True
) -> Dict[str, Any]:
    """
    Execute PostgreSQL tool operation

    Args:
        operation: Operation to perform
        table: Table name
        column_name: Column name
        column_type: SQL data type
        default_value: Default value
        old_column_name: Current column name (for rename)
        new_column_name: New column name (for rename)
        sql: Custom SQL query
        fetch_results: Whether to fetch results

    Returns:
        Operation results
    """
    tool = PostgreSQLTool()

    try:
        if operation == "add_column":
            if not all([table, column_name, column_type]):
                return {"success": False, "error": "table, column_name, and column_type required"}
            return await tool.add_column(table, column_name, column_type, default_value)

        elif operation == "drop_column":
            if not all([table, column_name]):
                return {"success": False, "error": "table and column_name required"}
            return await tool.drop_column(table, column_name)

        elif operation == "rename_column":
            if not all([table, old_column_name, new_column_name]):
                return {"success": False, "error": "table, old_column_name, and new_column_name required"}
            return await tool.rename_column(table, old_column_name, new_column_name)

        elif operation == "get_schema":
            if not table:
                return {"success": False, "error": "table required"}
            return await tool.get_table_schema(table)

        elif operation == "list_tables":
            return await tool.list_tables()

        elif operation == "custom_sql":
            if not sql:
                return {"success": False, "error": "sql required for custom_sql operation"}
            return await tool.execute_query(sql, fetch=fetch_results)

        else:
            return {"success": False, "error": f"Unknown operation: {operation}"}

    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        await tool.close()


# Test function
async def test_postgres_tool():
    """Test PostgreSQL tool functionality"""
    print("Testing PostgreSQL Direct Tool...")
    print("=" * 60)

    tool = PostgreSQLTool()

    try:
        # Test 1: List tables
        print("\n1. List tables:")
        result = await tool.list_tables()
        if result.get("success"):
            print(f"   Found {result.get('row_count')} tables")
            for table in result.get("data", [])[:5]:
                print(f"   - {table['table_name']}")
        else:
            print(f"   Error: {result.get('error')}")

        # Test 2: Get schema for service19_onboarding_data
        print("\n2. Get schema for service19_onboarding_data:")
        result = await tool.get_table_schema("service19_onboarding_data")
        if result.get("success"):
            print(f"   Columns: {result.get('row_count')}")
            for col in result.get("data", [])[:5]:
                print(f"   - {col['column_name']}: {col['data_type']}")
        else:
            print(f"   Error: {result.get('error')}")

        print("\n" + "=" * 60)
        print("PostgreSQL Tool test complete!")

    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await tool.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_postgres_tool())
