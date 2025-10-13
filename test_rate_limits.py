#!/usr/bin/env python
"""
Test MindsDB Agent with improved rate limit handling
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mindsdb_agent import MindsDBAgent


async def test_simple_query():
    """Test with a simple query that shouldn't hit rate limits"""
    print("\n" + "="*70)
    print("TEST 1: Simple Count Query (Low API Usage)")
    print("="*70 + "\n")
    
    agent = MindsDBAgent(create_alerts=False)
    query = "How many total records are in the database?"
    
    try:
        print(f"Query: {query}\n")
        response = await agent.run(query)
        print("\n✅ SUCCESS: Simple query completed without rate limits")
        return True
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        return False


async def test_zebra_crossing_query():
    """Test the original problematic query"""
    print("\n" + "="*70)
    print("TEST 2: Zebra Crossing Query (Higher API Usage)")
    print("="*70 + "\n")
    
    agent = MindsDBAgent(create_alerts=False)
    query = "find the location of every zebra crossing mentioned in our dataset"
    
    try:
        print(f"Query: {query}\n")
        response = await agent.run(query)
        print("\n✅ SUCCESS: Complex query completed (with or without retries)")
        return True
    except Exception as e:
        print(f"\n❌ FAILED after all retries: {e}")
        return False


async def main():
    """Run tests"""
    print("\n" + "="*70)
    print("MindsDB Agent Rate Limit Testing")
    print("Improved Configuration: 5 retries, 3x backoff")
    print("="*70)
    
    # Check for ANTHROPIC_API_KEY
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("\n❌ ERROR: ANTHROPIC_API_KEY not found in environment")
        print("Please add it to your .env file and try again.")
        return
    
    results = []
    
    # Test 1: Simple query
    result1 = await test_simple_query()
    results.append(("Simple Query", result1))
    
    # Small delay between tests to avoid rate limits
    print("\n⏳ Waiting 5 seconds before next test...")
    await asyncio.sleep(5)
    
    # Test 2: Complex query
    result2 = await test_zebra_crossing_query()
    results.append(("Zebra Crossing Query", result2))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    passed_count = sum(1 for _, passed in results if passed)
    print(f"\nTotal: {passed_count}/{len(results)} tests passed")
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
        sys.exit(1)
