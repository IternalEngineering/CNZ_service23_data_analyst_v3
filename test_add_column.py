#!/usr/bin/env python
"""
Test: Add 'green_apples' column to service19_onboarding_data table
This tests the write-enabled MindsDB agent
"""
import asyncio
from mindsdb_agent import MindsDBAgent


async def test_add_column():
    """Test adding a new column called 'green_apples'"""
    agent = MindsDBAgent()

    print("\n" + "="*70)
    print("TEST: Add Column 'green_apples' to service19_onboarding_data")
    print("="*70 + "\n")

    query = """
    I need to add a new column called 'green_apples' to the service19_onboarding_data table.

    Please:
    1. Write the SQL ALTER TABLE command to add a column named 'green_apples' of type INTEGER
    2. Set a default value of 0
    3. Execute the command using the alter_table operation

    The full table name is: datasource_postgres.service19_onboarding_data
    """

    try:
        response = await agent.run(query)
        print("\n" + "="*70)
        print("RESULT:")
        print("="*70)
        print(response)
        print("\n" + "="*70)

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()


async def test_verify_column():
    """Verify the column was added"""
    agent = MindsDBAgent()

    print("\n" + "="*70)
    print("TEST: Verify 'green_apples' Column Was Added")
    print("="*70 + "\n")

    query = """
    Check if the 'green_apples' column exists in the service19_onboarding_data table.

    You can do this by:
    1. Querying the table and selecting the green_apples column
    2. Or checking the table schema
    3. Show me a few sample records with the green_apples value

    Use LIMIT 3 to keep the response small.
    """

    try:
        response = await agent.run(query)
        print("\n" + "="*70)
        print("RESULT:")
        print("="*70)
        print(response)
        print("\n" + "="*70)

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Run the test suite"""
    print("\n" + "="*70)
    print("ADD COLUMN TEST SUITE")
    print("="*70)
    print("\nThis test will add a 'green_apples' column to the database")
    print("using the write-enabled Claude SDK agent")
    print("\n" + "="*70 + "\n")

    # Test 1: Add column
    print("\n--- Test 1: Add the Column ---\n")
    await test_add_column()

    input("\nPress Enter to verify the column was added...")

    # Test 2: Verify column
    print("\n--- Test 2: Verify Column Exists ---\n")
    await test_verify_column()

    print("\n" + "="*70)
    print("TEST SUITE COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
