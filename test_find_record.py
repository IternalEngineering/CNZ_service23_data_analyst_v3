#!/usr/bin/env python
"""
Test: Find and analyze specific record 627a9a58-1dbf-4ff3-b57d-a7d5b5955400
Target: datasource_postgres.public.service19_onboarding_data
"""
import asyncio
from mindsdb_agent import MindsDBAgent


async def test_find_specific_record():
    """Test agent's ability to find and analyze a specific record"""
    agent = MindsDBAgent()

    print("\n" + "="*70)
    print("TEST: Find Record 627a9a58-1dbf-4ff3-b57d-a7d5b5955400")
    print("="*70 + "\n")

    query = """
    Find the record in service19_onboarding_data where data_id = '627a9a58-1dbf-4ff3-b57d-a7d5b5955400'.

    Show me:
    - The download URL
    - Data format
    - Download success status
    - Record count
    - File size
    - Any error messages if present

    Use a custom SQL query to get this specific record.
    """

    try:
        response = await agent.run(query)
        print("\n" + "="*70)
        print("SUCCESS!")
        print("="*70)

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()


async def test_analyze_csv_data():
    """Test analyzing the CSV data from this record"""
    agent = MindsDBAgent()

    print("\n" + "="*70)
    print("TEST: Analyze CSV Data Structure")
    print("="*70 + "\n")

    query = """
    For the record with data_id = '627a9a58-1dbf-4ff3-b57d-a7d5b5955400':

    1. What is the data source URL?
    2. How many records does it contain?
    3. What is the file size?
    4. Was the download successful?
    5. What format is the data in?

    This is a transportation dataset from data.transportation.gov.
    """

    try:
        response = await agent.run(query)
        print("\n" + "="*70)
        print("SUCCESS!")
        print("="*70)

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Run tests"""
    print("\n" + "="*70)
    print("RECORD ANALYSIS TEST")
    print("="*70)
    print("\nTarget Record: 627a9a58-1dbf-4ff3-b57d-a7d5b5955400")
    print("Source: Transportation.gov CSV data")
    print("\n" + "="*70 + "\n")

    # Test 1
    print("\n--- Test 1: Find the Record ---\n")
    await test_find_specific_record()

    input("\nPress Enter to continue to Test 2...")

    # Test 2
    print("\n--- Test 2: Analyze the Data ---\n")
    await test_analyze_csv_data()

    print("\n" + "="*70)
    print("TESTS COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
