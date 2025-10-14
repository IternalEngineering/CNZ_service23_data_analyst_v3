#!/usr/bin/env python3
"""
Simple MindsDB Connection Verification
Tests connection, database access, and basic queries
"""

import sys
import requests
import json
from typing import Dict, Any, List


class MindsDBVerifier:
    """Simple MindsDB connection verifier"""

    def __init__(self, host: str = "localhost", port: int = 47334):
        self.base_url = f"http://{host}:{port}"

    def test_status(self) -> bool:
        """Test MindsDB status endpoint"""
        print("\n[1/5] Testing MindsDB Status...")
        try:
            response = requests.get(f"{self.base_url}/api/status", timeout=5)
            response.raise_for_status()
            status = response.json()
            print(f"SUCCESS: MindsDB {status.get('mindsdb_version')} is running")
            print(f"  Environment: {status.get('environment')}")
            print(f"  Auth: {status.get('auth', {}).get('provider', 'unknown')}")
            return True
        except Exception as e:
            print(f"FAILED: {e}")
            return False

    def test_databases(self) -> bool:
        """Test database listing"""
        print("\n[2/5] Testing Database Access...")
        try:
            response = requests.get(f"{self.base_url}/api/databases/", timeout=5)
            response.raise_for_status()
            databases = response.json()

            db_names = [db['name'] for db in databases if db.get('name')]
            print(f"SUCCESS: Found {len(db_names)} databases")

            # Check for urbanzero_postgres
            if 'urbanzero_postgres' in db_names:
                print("  Target database 'urbanzero_postgres' found")
                return True
            else:
                print("  WARNING: 'urbanzero_postgres' not found")
                print(f"  Available: {', '.join(db_names[:5])}")
                return False
        except Exception as e:
            print(f"FAILED: {e}")
            return False

    def test_query(self, query: str) -> List[Any]:
        """Execute a SQL query"""
        try:
            response = requests.post(
                f"{self.base_url}/api/sql/query",
                json={"query": query},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            response.raise_for_status()
            result = response.json()

            if result.get('type') == 'table':
                return result.get('data', [])
            else:
                return []
        except Exception as e:
            print(f"Query failed: {e}")
            return []

    def test_cities(self) -> bool:
        """Test cities table"""
        print("\n[3/5] Testing Cities Table...")
        try:
            query = "SELECT name, country, population FROM urbanzero_postgres.cities LIMIT 5;"
            results = self.test_query(query)

            if results:
                print(f"SUCCESS: Found {len(results)} cities")
                for row in results:
                    print(f"  - {row[0]}, {row[1]} (pop: {row[2]:,})")
                return True
            else:
                print("FAILED: No cities found")
                return False
        except Exception as e:
            print(f"FAILED: {e}")
            return False

    def test_service19_data(self) -> bool:
        """Test SERVICE19 city data"""
        print("\n[4/5] Testing SERVICE19 City Data...")
        try:
            query = "SELECT city, COUNT(*) as record_count FROM urbanzero_postgres.service19_city_data GROUP BY city LIMIT 5;"
            results = self.test_query(query)

            if results:
                print(f"SUCCESS: Found data for {len(results)} cities")
                for row in results:
                    print(f"  - {row[0]}: {row[1]} records")
                return True
            else:
                print("INFO: No SERVICE19 data found (table may be empty)")
                return True  # Not a failure if table is empty
        except Exception as e:
            print(f"FAILED: {e}")
            return False

    def test_tables(self) -> bool:
        """Test table listing"""
        print("\n[5/5] Testing Table Listing...")
        try:
            query = "SHOW TABLES FROM urbanzero_postgres;"
            results = self.test_query(query)

            if results:
                table_names = [row[0] for row in results]
                print(f"SUCCESS: Found {len(table_names)} tables")

                # Check for key tables
                key_tables = ['cities', 'service19_city_data', 'service19_data_sources', 'users', 'opportunities']
                found_tables = [t for t in key_tables if t in table_names]
                print(f"  Key tables found: {', '.join(found_tables)}")

                return True
            else:
                print("FAILED: No tables found")
                return False
        except Exception as e:
            print(f"FAILED: {e}")
            return False


def main():
    """Run all verification tests"""
    print("=" * 60)
    print("MindsDB Connection Verification")
    print("=" * 60)

    verifier = MindsDBVerifier()

    tests = [
        verifier.test_status,
        verifier.test_databases,
        verifier.test_cities,
        verifier.test_service19_data,
        verifier.test_tables,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"ERROR: {e}")
            failed += 1

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")

    if failed == 0:
        print("\nAll tests passed! MindsDB connection is working.")
        return 0
    else:
        print(f"\n{failed} test(s) failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
