#!/usr/bin/env python
"""
Simple test of MindsDB Agent
"""
import asyncio
from mindsdb_agent import MindsDBAgent


async def test_queries():
    """Test various simple queries"""
    agent = MindsDBAgent()

    queries = [
        "How many total records are there?",
        "What file types are in the database?",
        "Show me URLs that contain 'arcgis'",
    ]

    for query in queries:
        print(f"\n{'='*70}")
        print(f"TESTING: {query}")
        print(f"{'='*70}\n")

        try:
            response = await agent.run(query)
            print(f"\nSUCCESS!")
        except Exception as e:
            print(f"\nERROR: {e}")

        print("\n" + "="*70 + "\n")
        input("Press Enter to continue...")


if __name__ == "__main__":
    asyncio.run(test_queries())
