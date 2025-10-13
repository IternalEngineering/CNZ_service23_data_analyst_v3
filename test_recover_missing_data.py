#!/usr/bin/env python
"""
Test: Recover missing ISSUE_NAME and DETAILED_DESCRIPTION from raw data
Target: datasource_postgres.public.service19_onboarding_data
Goal: Find records where ISSUE_NAME or DETAILED_DESCRIPTION are missing (X or null)
      and extract the actual values from the parsed_content or raw_content JSON
"""
import asyncio
from mindsdb_agent import MindsDBAgent


async def test_recover_missing_data():
    """
    Test agent's ability to recover missing data from JSON in raw_content column

    Example missing data:
    {
        "id": 245,
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [-2.5934701210068, 51.4411597095322]
        },
        "properties": {
            "STATUS": 1,
            "OBJECTID": 245,
            "ISSUE_NAME": X,  # Missing - need to recover
            "DETAILED_DESCRIPTION": X  # Missing - need to recover
        }
    }
    """
    agent = MindsDBAgent()

    print("\n" + "="*70)
    print("TEST: Recover Missing ISSUE_NAME and DETAILED_DESCRIPTION")
    print("="*70 + "\n")

    # Test query to find and recover missing data
    query = """
    I need to analyze the service19_onboarding_data table to find records with missing data.

    Specifically, I'm looking for GeoJSON features where ISSUE_NAME or DETAILED_DESCRIPTION
    are missing (marked as 'X' or null) in the parsed JSON content.

    Example structure I'm looking for:
    {
        "id": 245,
        "type": "Feature",
        "properties": {
            "STATUS": 1,
            "OBJECTID": 245,
            "ISSUE_NAME": X,
            "DETAILED_DESCRIPTION": X
        }
    }

    Can you:
    1. Find records that contain GeoJSON features (file_type = 'geojson' or similar)
    2. Look for features where ISSUE_NAME or DETAILED_DESCRIPTION might be missing
    3. Extract the actual values from the raw_content or parsed_content JSON
    4. Show me examples of records with OBJECTID 245 or nearby IDs
    """

    try:
        response = await agent.run(query)
        print("\n" + "="*70)
        print("RESULT:")
        print("="*70)
        print(response)

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()


async def test_direct_json_query():
    """
    Alternative approach: Direct SQL query to extract JSON data
    """
    agent = MindsDBAgent()

    print("\n" + "="*70)
    print("TEST: Direct Query for GeoJSON Features")
    print("="*70 + "\n")

    query = """
    I need to query the service19_onboarding_data table for GeoJSON data.

    Run a custom SQL query to:
    1. Find records where file_type = 'geojson' or url contains 'geojson'
    2. Select id, url, file_type, and check if parsed_content contains features
    3. Show me the first 3 records
    4. For each record, try to identify if there are features with missing ISSUE_NAME

    Use a LIMIT of 3 to keep the response small.
    """

    try:
        response = await agent.run(query)
        print("\n" + "="*70)
        print("RESULT:")
        print("="*70)
        print(response)

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()


async def test_search_by_url():
    """
    Test: Search for specific data source by URL pattern
    """
    agent = MindsDBAgent()

    print("\n" + "="*70)
    print("TEST: Search for Bristol Highway Data (likely source of the features)")
    print("="*70 + "\n")

    query = """
    Search the service19_onboarding_data for records where:
    - The URL contains 'highway' or 'FeatureServer'
    - The file_type is 'geojson' or the URL contains 'geojson'

    Show me the URL, file_type, success status, and content_size for these records.
    This should help us find the data source containing the feature with OBJECTID 245.
    """

    try:
        response = await agent.run(query)
        print("\n" + "="*70)
        print("RESULT:")
        print("="*70)
        print(response)

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("MISSING DATA RECOVERY TEST SUITE")
    print("="*70)
    print("\nTarget: datasource_postgres.public.service19_onboarding_data")
    print("Goal: Recover missing ISSUE_NAME and DETAILED_DESCRIPTION from JSON")
    print("\n" + "="*70 + "\n")

    tests = [
        ("Test 1: Search by URL Pattern", test_search_by_url),
        ("Test 2: Direct JSON Query", test_direct_json_query),
        ("Test 3: Recover Missing Data", test_recover_missing_data),
    ]

    for test_name, test_func in tests:
        print(f"\n{'='*70}")
        print(f"Running: {test_name}")
        print(f"{'='*70}\n")

        try:
            await test_func()
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            import traceback
            traceback.print_exc()

        print("\n" + "="*70)
        user_input = input("\nPress Enter to continue to next test (or 'q' to quit): ")
        if user_input.lower() == 'q':
            break

    print("\n" + "="*70)
    print("TEST SUITE COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
