#!/usr/bin/env python
"""
MindsDB Tool for Claude SDK Agent
Provides access to datasource_postgres.service19_onboarding_data via MindsDB
"""
import httpx
import json
from typing import Dict, List, Any, Optional


class MindsDBTool:
    """Tool to query MindsDB for SERVICE19 onboarding data"""

    def __init__(self, base_url: str = "http://localhost:47334"):
        self.base_url = base_url
        self.datasource = "datasource_postgres"
        self.table = "service19_onboarding_data"

    async def query(self, sql: str, allow_write: bool = False) -> Dict[str, Any]:
        """
        Execute SQL query via MindsDB API

        Args:
            sql: SQL query to execute
            allow_write: Allow write operations (INSERT, UPDATE, DELETE, ALTER, CREATE, DROP)

        Returns:
            Query results with data and metadata
        """
        # Safety check for write operations
        sql_upper = sql.strip().upper()
        write_keywords = ['INSERT', 'UPDATE', 'DELETE', 'ALTER', 'CREATE', 'DROP', 'TRUNCATE']
        is_write_operation = any(sql_upper.startswith(keyword) for keyword in write_keywords)

        if is_write_operation and not allow_write:
            return {
                "success": False,
                "error": "Write operations not allowed. Use allow_write=True to enable."
            }
        # Safety check for large columns - now with 1M context we can handle some, but warn
        sql_lower = sql.lower()

        # Warn about raw_data but allow with strict LIMIT
        if 'raw_data' in sql_lower or 'error_details' in sql_lower:
            # Check if LIMIT is present
            if 'limit' not in sql_lower:
                return {
                    "success": False,
                    "error": "Query must include LIMIT clause when selecting raw_data or error_details (max LIMIT 5 recommended). These columns contain large JSON. With 1M context window enabled, small queries are allowed."
                }
            
            # Check if LIMIT is reasonable (extract number)
            import re
            limit_match = re.search(r'limit\s+(\d+)', sql_lower)
            if limit_match:
                limit_value = int(limit_match.group(1))
                if limit_value > 10:
                    return {
                        "success": False, 
                        "error": f"LIMIT {limit_value} too high for raw_data queries. Maximum LIMIT 10 recommended to avoid context overflow even with 1M window."
                    }
            
            print(f"[WARNING] Query includes large JSON columns. 1M context enabled, but query may still be large.")

        # Block SELECT * entirely - too dangerous
        if 'select *' in sql_lower:
            return {
                "success": False,
                "error": "SELECT * not allowed. Always specify explicit column names to control response size."
            }


        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/sql/query",
                    json={"query": sql},
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                result = response.json()

                # Check for errors
                if result.get("type") == "error":
                    return {
                        "success": False,
                        "error": result.get("error_message", "Unknown error")
                    }

                # Format successful response
                return {
                    "success": True,
                    "data": result.get("data", []),
                    "columns": result.get("column_names", []),
                    "row_count": len(result.get("data", []))
                }

        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "Query timeout - try a simpler query or add LIMIT clause"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Query failed: {str(e)}"
            }

    async def get_sample_data(self, limit: int = 5) -> Dict[str, Any]:
        """Get sample records from service19_onboarding_data (excluding large content fields)"""
        sql = f"""
            SELECT data_id, source_id, download_url, download_timestamp,
                   download_success, http_status_code, data_format,
                   file_size_bytes, record_count, error_message
            FROM {self.datasource}.{self.table}
            LIMIT {limit};
        """
        return await self.query(sql)

    async def count_records(self) -> Dict[str, Any]:
        """Count total records in service19_onboarding_data"""
        sql = f"SELECT COUNT(*) as total FROM {self.datasource}.{self.table};"
        result = await self.query(sql)

        if result.get("success") and result.get("data"):
            total = result["data"][0][0] if result["data"] else 0
            return {
                "success": True,
                "total_records": total
            }
        return result

    async def search_by_url(self, url_pattern: str, limit: int = 10) -> Dict[str, Any]:
        """
        Search onboarding data by URL pattern

        Args:
            url_pattern: URL or pattern to search for (uses LIKE)
            limit: Maximum results to return
        """
        sql = f"""
            SELECT id, onboarding_id, url, fetched_at, success, http_status
            FROM {self.datasource}.{self.table}
            WHERE url LIKE '%{url_pattern}%'
            LIMIT {limit};
        """
        return await self.query(sql)

    async def get_successful_fetches(self, limit: int = 10) -> Dict[str, Any]:
        """Get successfully fetched data sources"""
        sql = f"""
            SELECT id, onboarding_id, url, fetched_at, http_status, file_type
            FROM {self.datasource}.{self.table}
            WHERE success = true
            LIMIT {limit};
        """
        return await self.query(sql)

    async def get_failed_fetches(self, limit: int = 10) -> Dict[str, Any]:
        """Get failed fetch attempts"""
        sql = f"""
            SELECT id, onboarding_id, url, error_message, http_status
            FROM {self.datasource}.{self.table}
            WHERE success = false
            LIMIT {limit};
        """
        return await self.query(sql)

    async def get_by_file_type(self, file_type: str, limit: int = 10) -> Dict[str, Any]:
        """Get data sources by file type (csv, json, geojson, etc.)"""
        sql = f"""
            SELECT id, url, file_type, content_size, http_status
            FROM {self.datasource}.{self.table}
            WHERE file_type = '{file_type}'
            LIMIT {limit};
        """
        return await self.query(sql)

    async def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about onboarding data"""
        queries = {
            "total": f"SELECT COUNT(*) FROM {self.datasource}.{self.table}",
            "successful": f"SELECT COUNT(*) FROM {self.datasource}.{self.table} WHERE success = true",
            "failed": f"SELECT COUNT(*) FROM {self.datasource}.{self.table} WHERE success = false",
            "file_types": f"SELECT file_type, COUNT(*) as count FROM {self.datasource}.{self.table} GROUP BY file_type"
        }

        results = {}
        for key, sql in queries.items():
            result = await self.query(sql + ";")
            if result.get("success"):
                if key == "file_types":
                    results[key] = result.get("data", [])
                else:
                    results[key] = result["data"][0][0] if result.get("data") else 0
            else:
                results[key] = None

        return {
            "success": True,
            "statistics": results
        }


# Tool definition for Claude SDK
def get_mindsdb_tool_definition():
    """Get tool definition for OpenAI/LiteLLM SDK"""
    return {
        "type": "function",
        "function": {
            "name": "query_mindsdb",
            "description": """Query SERVICE19 onboarding data from MindsDB.
        This table contains city data collection results including URLs, fetch status, file types, and content.
        Use this to analyze data sources, check fetch success rates, explore available datasets, and debug data collection issues.

        Available operations:
        - Get sample data
        - Count records
        - Search by URL pattern
        - Filter by success/failure
        - Filter by file type (csv, json, geojson, etc.)
        - Get statistics
        - Execute custom SQL (including ALTER TABLE, INSERT, UPDATE)
        - Modify database schema (use with caution)
        """,
            "parameters": {
                "type": "object",
                "properties": {
                "operation": {
                    "type": "string",
                    "enum": [
                        "sample",
                        "count",
                        "search_url",
                        "successful",
                        "failed",
                        "by_file_type",
                        "statistics",
                        "custom_query",
                        "alter_table"
                    ],
                    "description": "Operation to perform"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of records to return (default: 10)",
                    "default": 10
                },
                "url_pattern": {
                    "type": "string",
                    "description": "URL pattern to search for (required for search_url operation)"
                },
                "file_type": {
                    "type": "string",
                    "description": "File type to filter by: csv, json, geojson, etc (required for by_file_type operation)"
                },
                "custom_sql": {
                    "type": "string",
                    "description": "Custom SQL query (required for custom_query or alter_table operations)"
                },
                "allow_write": {
                    "type": "boolean",
                    "description": "Allow write operations (ALTER, INSERT, UPDATE, DELETE). Default: false",
                    "default": False
                }
            },
            "required": ["operation"]
            }
        }
    }


async def execute_mindsdb_tool(
    operation: str,
    limit: int = 10,
    url_pattern: Optional[str] = None,
    file_type: Optional[str] = None,
    custom_sql: Optional[str] = None,
    allow_write: bool = False
) -> Dict[str, Any]:
    """
    Execute MindsDB tool operation

    Args:
        operation: Operation to perform
        limit: Maximum records to return
        url_pattern: URL pattern for search
        file_type: File type to filter
        custom_sql: Custom SQL query
        allow_write: Allow write operations (default: False)

    Returns:
        Operation results
    """
    tool = MindsDBTool()

    try:
        if operation == "sample":
            return await tool.get_sample_data(limit)

        elif operation == "count":
            return await tool.count_records()

        elif operation == "search_url":
            if not url_pattern:
                return {"success": False, "error": "url_pattern required for search_url operation"}
            return await tool.search_by_url(url_pattern, limit)

        elif operation == "successful":
            return await tool.get_successful_fetches(limit)

        elif operation == "failed":
            return await tool.get_failed_fetches(limit)

        elif operation == "by_file_type":
            if not file_type:
                return {"success": False, "error": "file_type required for by_file_type operation"}
            return await tool.get_by_file_type(file_type, limit)

        elif operation == "statistics":
            return await tool.get_statistics()

        elif operation == "custom_query":
            if not custom_sql:
                return {"success": False, "error": "custom_sql required for custom_query operation"}
            return await tool.query(custom_sql, allow_write=allow_write)

        elif operation == "alter_table":
            if not custom_sql:
                return {"success": False, "error": "custom_sql required for alter_table operation"}
            # Force allow_write=True for alter_table operations
            return await tool.query(custom_sql, allow_write=True)

        else:
            return {"success": False, "error": f"Unknown operation: {operation}"}

    except Exception as e:
        return {"success": False, "error": str(e)}


# Test function
async def test_mindsdb_tool():
    """Test MindsDB tool functionality"""
    print("Testing MindsDB Tool...")
    print("=" * 60)

    tool = MindsDBTool()

    # Test 1: Count records
    print("\n1. Count total records:")
    result = await tool.count_records()
    print(f"   Result: {result}")

    # Test 2: Get sample data
    print("\n2. Get sample data (3 records):")
    result = await tool.get_sample_data(limit=3)
    print(f"   Success: {result.get('success')}")
    print(f"   Rows: {result.get('row_count')}")
    if result.get('columns'):
        print(f"   Columns: {result['columns']}")

    # Test 3: Get statistics
    print("\n3. Get statistics:")
    result = await tool.get_statistics()
    if result.get('success'):
        stats = result.get('statistics', {})
        print(f"   Total: {stats.get('total')}")
        print(f"   Successful: {stats.get('successful')}")
        print(f"   Failed: {stats.get('failed')}")

    # Test 4: Search by URL
    print("\n4. Search for 'bristol' in URLs:")
    result = await tool.search_by_url("bristol", limit=3)
    print(f"   Found: {result.get('row_count')} records")

    # Test 5: Get successful fetches
    print("\n5. Get successful fetches (3 records):")
    result = await tool.get_successful_fetches(limit=3)
    print(f"   Success count: {result.get('row_count')}")

    print("\n" + "=" * 60)
    print("MindsDB Tool test complete!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_mindsdb_tool())
