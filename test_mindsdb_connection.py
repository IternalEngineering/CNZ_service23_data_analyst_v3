#!/usr/bin/env python3
"""
Test script for MindsDB connection
Validates connection, database access, and query functionality
"""

import sys
from mindsdb_client import MindsDBClient, MindsDBConfig
import json


def print_section(title: str):
    """Print a section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_connection():
    """Test MindsDB connection"""
    print_section("Testing MindsDB Connection")

    client = MindsDBClient()

    # Test status endpoint
    print("Checking MindsDB status...")
    status = client.get_status()

    if not status:
        print("❌ FAILED: Could not connect to MindsDB")
        print("\nTroubleshooting steps:")
        print("1. Start SSH tunnel:")
        print("   PowerShell: .\\setup_tunnel.ps1")
        print("   Batch:      start_tunnel.bat")
        print("2. Verify MindsDB is accessible:")
        print("   curl http://localhost:47334/api/status")
        return False

    print(f"✅ SUCCESS: Connected to MindsDB")
    print(f"   Version: {status.get('mindsdb_version', 'unknown')}")
    print(f"   Environment: {status.get('environment', 'unknown')}")
    print(f"   Auth: {status.get('auth', {})}")

    return True


def test_databases(client: MindsDBClient):
    """Test database listing"""
    print_section("Testing Database Access")

    print("Listing available databases...")
    databases = client.list_databases()

    if not databases:
        print("❌ FAILED: No databases found")
        return False

    print(f"✅ SUCCESS: Found {len(databases)} databases")
    for db in databases:
        print(f"   - {db}")

    # Check for urbanzero_postgres
    if client.config.datasource in databases:
        print(f"\n✅ Target database '{client.config.datasource}' is available")
    else:
        print(f"\n⚠️  WARNING: Target database '{client.config.datasource}' not found")

    return True


def test_tables(client: MindsDBClient):
    """Test table listing"""
    print_section("Testing Table Access")

    print(f"Listing tables in {client.config.datasource}...")
    tables = client.list_tables()

    if not tables:
        print("❌ FAILED: No tables found")
        return False

    print(f"✅ SUCCESS: Found {len(tables)} tables")

    # Key tables to check
    key_tables = ['cities', 'service19_city_data', 'service19_data_sources',
                  'opportunities', 'users', 'reports']

    print("\nKey tables status:")
    for table in key_tables:
        if table in tables:
            print(f"   ✅ {table}")
        else:
            print(f"   ❌ {table} (not found)")

    print(f"\nAll tables ({len(tables)}):")
    for table in sorted(tables)[:20]:  # Show first 20
        print(f"   - {table}")
    if len(tables) > 20:
        print(f"   ... and {len(tables) - 20} more")

    return True


def test_city_queries(client: MindsDBClient):
    """Test city-related queries"""
    print_section("Testing City Queries")

    # Get all cities
    print("Fetching all cities...")
    cities = client.get_cities()

    if not cities:
        print("❌ FAILED: No cities found")
        return False

    print(f"✅ SUCCESS: Found {len(cities)} cities")
    for city in cities:
        if isinstance(city, dict):
            print(f"   - {city.get('name', 'Unknown')}")
        elif isinstance(city, list) and len(city) > 1:
            print(f"   - {city[1]}")  # Assuming name is second column

    # Test specific city lookup
    if cities:
        # Get first city name
        test_city_name = None
        if isinstance(cities[0], dict):
            test_city_name = cities[0].get('name', 'Bristol')
        elif isinstance(cities[0], list) and len(cities[0]) > 1:
            test_city_name = cities[0][1]

        if test_city_name:
            print(f"\nTesting lookup for '{test_city_name}'...")
            city_data = client.get_city_by_name(test_city_name)

            if city_data:
                print(f"✅ SUCCESS: Found city data")
                print(f"   Data: {json.dumps(city_data, indent=2)[:200]}...")
            else:
                print(f"❌ FAILED: Could not find city '{test_city_name}'")

    return True


def test_city_statistics(client: MindsDBClient):
    """Test city statistics queries"""
    print_section("Testing City Statistics (SERVICE19)")

    # Get cities first
    cities = client.get_cities()
    if not cities:
        print("⚠️  SKIPPED: No cities available for testing")
        return True

    # Get test city name
    test_city_name = 'Bristol'
    if isinstance(cities[0], dict):
        test_city_name = cities[0].get('name', 'Bristol')
    elif isinstance(cities[0], list) and len(cities[0]) > 1:
        test_city_name = cities[0][1]

    print(f"Fetching statistics for '{test_city_name}'...")
    stats = client.get_city_statistics(test_city_name)

    print(f"Found {len(stats)} statistics records")

    if stats:
        print(f"✅ SUCCESS: Retrieved city statistics")
        print(f"   Sample: {json.dumps(stats[0], indent=2)[:300]}...")
    else:
        print(f"⚠️  No statistics found for {test_city_name} (table may be empty)")

    return True


def test_data_sources(client: MindsDBClient):
    """Test data sources queries"""
    print_section("Testing Data Sources")

    print("Fetching all data sources...")
    sources = client.get_data_sources()

    print(f"Found {len(sources)} data sources")

    if sources:
        print(f"✅ SUCCESS: Retrieved data sources")
        print(f"   Sample: {json.dumps(sources[0], indent=2)[:300]}...")
    else:
        print(f"⚠️  No data sources found (table may be empty)")

    return True


def test_custom_query(client: MindsDBClient):
    """Test custom query functionality"""
    print_section("Testing Custom Queries")

    print("Testing custom query on cities table...")
    results = client.custom_query(
        table="cities",
        select_columns="name, country",
        limit=5
    )

    if results:
        print(f"✅ SUCCESS: Custom query returned {len(results)} results")
        for result in results:
            print(f"   {result}")
    else:
        print("⚠️  No results from custom query")

    return True


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("  MindsDB Connection Test Suite")
    print("  Service21 - Data Analyst Agent")
    print("=" * 60)

    # Test connection first
    if not test_connection():
        print("\n❌ Connection test failed. Please fix connection issues before continuing.")
        sys.exit(1)

    # Create client for remaining tests
    client = MindsDBClient()

    # Run all tests
    tests = [
        ("Database Access", test_databases),
        ("Table Access", test_tables),
        ("City Queries", test_city_queries),
        ("City Statistics", test_city_statistics),
        ("Data Sources", test_data_sources),
        ("Custom Queries", test_custom_query),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            if test_func(client):
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n❌ ERROR in {test_name}: {e}")
            failed += 1

    # Summary
    print_section("Test Summary")
    print(f"Tests passed: {passed}")
    print(f"Tests failed: {failed}")
    print(f"Total tests: {passed + failed}")

    if failed == 0:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {failed} test(s) failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
