#!/usr/bin/env python
"""
Direct PostgreSQL Tool for Claude SDK Agent
Bypasses MindsDB HTTP API to access large raw_data fields directly
"""
import os
import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

try:
    import asyncpg
except ImportError:
    print("ERROR: asyncpg not installed")
    print("Run: pip install asyncpg")
    asyncpg = None


class PostgresDirectTool:
    """Tool to query PostgreSQL directly for large data access"""

    def __init__(self):
        # PostgreSQL connection details from .env or defaults
        self.host = os.getenv('POSTGRES_HOST', 'urbanzero-db.c5qeo4ayy5u5.eu-west-2.rds.amazonaws.com')
        self.port = int(os.getenv('POSTGRES_PORT', '5432'))
        self.database = os.getenv('POSTGRES_DATABASE', 'urbanzero-db')
        self.user = os.getenv('POSTGRES_USER', 'urbanzero_app')
        self.password = os.getenv('POSTGRES_PASSWORD', 'UrbanZero2024$Secure')
        self.schema = 'public'
        
        self.pool = None

    async def connect(self):
        """Create connection pool"""
        if not asyncpg:
            return {"success": False, "error": "asyncpg not installed"}
        
        if self.pool is None:
            try:
                self.pool = await asyncpg.create_pool(
                    host=self.host,
                    port=self.port,
                    database=self.database,
                    user=self.user,
                    password=self.password,
                    ssl='require',
                    min_size=1,
                    max_size=3,
                    timeout=30
                )
            except Exception as e:
                return {"success": False, "error": f"Connection failed: {str(e)}"}
        
        return {"success": True}

    async def query(self, sql: str, params: Optional[List] = None) -> Dict[str, Any]:
        """
        Execute SQL query directly on PostgreSQL
        
        Args:
            sql: SQL query to execute
            params: Optional query parameters for parameterized queries
            
        Returns:
            Query results with data and metadata
        """
        # Connect if not already connected
        connect_result = await self.connect()
        if not connect_result.get("success"):
            return connect_result

        try:
            async with self.pool.acquire() as conn:
                # Execute query
                if params:
                    results = await conn.fetch(sql, *params)
                else:
                    results = await conn.fetch(sql)
                
                # Convert to list of dicts
                data = [dict(row) for row in results]
                
                # Get column names
                columns = list(results[0].keys()) if results else []
                
                return {
                    "success": True,
                    "data": data,
                    "columns": columns,
                    "row_count": len(data)
                }
                
        except asyncpg.exceptions.PostgresError as e:
            return {
                "success": False,
                "error": f"PostgreSQL error: {e.sqlstate} - {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Query failed: {str(e)}"
            }

    async def query_zebra_crossings(self, limit: int = 5) -> Dict[str, Any]:
        """
        Specialized query for zebra crossing data
        Returns only essential fields to avoid context overflow
        """
        sql = """
            SELECT 
                data_id,
                source_id,
                download_url,
                jsonb_extract_path_text(raw_data, 'type') as feature_type,
                jsonb_extract_path_text(raw_data, 'properties', 'crossing') as crossing_type,
                jsonb_extract_path_text(raw_data, 'properties', 'name') as name,
                jsonb_extract_path(raw_data, 'geometry', 'coordinates') as coordinates
            FROM service19_onboarding_data
            WHERE raw_data::text LIKE '%zebra%'
            LIMIT $1
        """
        return await self.query(sql, [limit])

    async def close(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
            self.pool = None


def get_postgres_direct_tool_definition():
    """Get tool definition for OpenAI/LiteLLM SDK"""
    return {
        "type": "function",
        "function": {
            "name": "query_postgres_direct",
            "description": """Query PostgreSQL database directly (bypasses MindsDB API).
        Use this for:
        - Accessing raw_data column (large GeoJSON)
        - Complex queries that need full PostgreSQL features
        - When MindsDB API times out or has context limits

        Always include LIMIT clause to avoid overwhelming responses.""",
            "parameters": {
                "type": "object",
                "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["custom_query", "zebra_crossings"],
                    "description": "Query operation type"
                },
                "custom_sql": {
                    "type": "string",
                    "description": "Custom SQL query (for operation=custom_query). Must include LIMIT clause."
                },
                "limit": {
                    "type": "integer",
                    "description": "Result limit for specialized queries (default: 5)",
                    "default": 5
                }
            },
            "required": ["operation"]
            }
        }
    }


async def execute_postgres_direct_tool(operation: str, custom_sql: Optional[str] = None, 
                                       limit: int = 5, **kwargs) -> Dict[str, Any]:
    """Execute direct PostgreSQL tool operation"""
    tool = PostgresDirectTool()
    
    try:
        if operation == "zebra_crossings":
            result = await tool.query_zebra_crossings(limit=limit)
        elif operation == "custom_query":
            if not custom_sql:
                return {"success": False, "error": "custom_sql required for custom_query operation"}
            
            # Safety check: require LIMIT
            sql_lower = custom_sql.lower()
            if 'limit' not in sql_lower:
                return {
                    "success": False,
                    "error": "LIMIT clause required for direct PostgreSQL queries to avoid context overflow"
                }
            
            result = await tool.query(custom_sql)
        else:
            result = {"success": False, "error": f"Unknown operation: {operation}"}
        
        return result
        
    finally:
        await tool.close()


# Test function
async def test_direct_access():
    """Test direct PostgreSQL access"""
    print("Testing direct PostgreSQL access...")
    
    tool = PostgresDirectTool()
    
    # Test 1: Simple count
    print("\nTest 1: Count records")
    result = await tool.query("SELECT COUNT(*) as total FROM service19_onboarding_data")
    print(f"Result: {result}")
    
    # Test 2: Zebra crossings
    print("\nTest 2: Zebra crossings")
    result = await tool.query_zebra_crossings(limit=1)
    print(f"Result: {result}")
    
    await tool.close()


if __name__ == "__main__":
    asyncio.run(test_direct_access())
