#!/usr/bin/env python3
"""
MindsDB Client for Service21 - Data Analyst Agent
Provides direct access to PostgreSQL via MindsDB SQL interface
"""

import requests
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MindsDBConfig:
    """Configuration for MindsDB connection"""
    host: str = "localhost"
    port: int = 47334
    datasource: str = "urbanzero_postgres"
    use_https: bool = False

    @property
    def base_url(self) -> str:
        protocol = "https" if self.use_https else "http"
        return f"{protocol}://{self.host}:{self.port}"


class MindsDBClient:
    """Client for interacting with MindsDB SQL API"""

    def __init__(self, config: Optional[MindsDBConfig] = None):
        self.config = config or MindsDBConfig()
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
        })

    def get_status(self) -> Optional[Dict[str, Any]]:
        """Check MindsDB server status"""
        try:
            response = self.session.get(f"{self.config.base_url}/api/status")
            response.raise_for_status()
            status = response.json()
            logger.info(f"MindsDB Status: {status}")
            return status
        except Exception as e:
            logger.error(f"Failed to get MindsDB status: {e}")
            return None

    def execute_query(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Execute a SQL query via MindsDB API

        Args:
            query: SQL query string

        Returns:
            Query results as dictionary with columns and data
        """
        try:
            url = f"{self.config.base_url}/api/sql/query"
            payload = {"query": query}

            logger.info(f"Executing query: {query}")
            response = self.session.post(url, json=payload)
            response.raise_for_status()

            result = response.json()
            logger.info(f"Query returned {len(result.get('data', []))} rows")
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Query execution failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            return None

    def list_databases(self) -> List[str]:
        """List all available databases"""
        try:
            response = self.session.get(f"{self.config.base_url}/api/databases/")
            response.raise_for_status()
            databases = response.json()
            return [db.get('name') for db in databases if db.get('name')]
        except Exception as e:
            logger.error(f"Failed to list databases: {e}")
            return []

    def list_tables(self, database: Optional[str] = None) -> List[str]:
        """List all tables in a database"""
        db = database or self.config.datasource
        query = f"SHOW TABLES FROM {db};"
        result = self.execute_query(query)

        if result and 'data' in result:
            # Extract table names from result
            return [row[0] if isinstance(row, list) else row.get('Tables_in_' + db, '')
                   for row in result['data']]
        return []

    def get_cities(self) -> List[Dict[str, Any]]:
        """Get all cities from the database"""
        query = f"SELECT * FROM {self.config.datasource}.cities;"
        result = self.execute_query(query)

        if result and 'data' in result:
            return result['data']
        return []

    def get_city_by_name(self, city_name: str) -> Optional[Dict[str, Any]]:
        """Get city by name"""
        query = f"SELECT * FROM {self.config.datasource}.cities WHERE name = '{city_name}';"
        result = self.execute_query(query)

        if result and 'data' in result and len(result['data']) > 0:
            return result['data'][0]
        return None

    def get_city_statistics(self, city_name: str) -> List[Dict[str, Any]]:
        """Get SERVICE19 city statistics and metrics"""
        query = f"SELECT * FROM {self.config.datasource}.service19_city_data WHERE city = '{city_name}';"
        result = self.execute_query(query)

        if result and 'data' in result:
            return result['data']
        return []

    def get_data_sources(self, city_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get data sources, optionally filtered by city"""
        if city_name:
            query = f"SELECT * FROM {self.config.datasource}.service19_data_sources WHERE city = '{city_name}';"
        else:
            query = f"SELECT * FROM {self.config.datasource}.service19_data_sources;"

        result = self.execute_query(query)
        if result and 'data' in result:
            return result['data']
        return []

    def get_opportunities(self, city_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get investment opportunities, optionally filtered by city"""
        if city_name:
            query = f"SELECT * FROM {self.config.datasource}.opportunities WHERE city = '{city_name}';"
        else:
            query = f"SELECT * FROM {self.config.datasource}.opportunities;"

        result = self.execute_query(query)
        if result and 'data' in result:
            return result['data']
        return []

    def custom_query(self, table: str, where_clause: Optional[str] = None,
                    select_columns: str = "*", limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Execute a custom query with flexible parameters

        Args:
            table: Table name (will be prefixed with datasource)
            where_clause: Optional WHERE clause (without 'WHERE' keyword)
            select_columns: Columns to select (default: '*')
            limit: Optional row limit

        Returns:
            List of result rows
        """
        query = f"SELECT {select_columns} FROM {self.config.datasource}.{table}"

        if where_clause:
            query += f" WHERE {where_clause}"

        if limit:
            query += f" LIMIT {limit}"

        query += ";"

        result = self.execute_query(query)
        if result and 'data' in result:
            return result['data']
        return []


def main():
    """Test MindsDB client connection"""
    client = MindsDBClient()

    # Test connection
    print("Testing MindsDB connection...")
    status = client.get_status()
    if not status:
        print("❌ Failed to connect to MindsDB")
        print("Please ensure:")
        print("1. SSH tunnel is running (use setup_tunnel.ps1 or start_tunnel.bat)")
        print("2. MindsDB is accessible at http://localhost:47334")
        return

    print(f"✅ Connected to MindsDB {status.get('mindsdb_version', 'unknown')}")

    # List databases
    print("\nListing databases...")
    databases = client.list_databases()
    print(f"Found {len(databases)} databases: {databases}")

    # List tables
    print(f"\nListing tables in {client.config.datasource}...")
    tables = client.list_tables()
    print(f"Found {len(tables)} tables")

    # Get cities
    print("\nFetching cities...")
    cities = client.get_cities()
    print(f"Found {len(cities)} cities")
    for city in cities:
        print(f"  - {city.get('name', 'Unknown')}")

    # Test specific city
    if cities:
        test_city = cities[0].get('name', 'Bristol')
        print(f"\nTesting city-specific queries for {test_city}...")

        city_data = client.get_city_by_name(test_city)
        print(f"City data: {city_data}")

        stats = client.get_city_statistics(test_city)
        print(f"Found {len(stats)} statistics records")

        sources = client.get_data_sources(test_city)
        print(f"Found {len(sources)} data sources")


if __name__ == "__main__":
    main()
