#!/usr/bin/env python
"""
Quick test to find the GeoJSON data with OBJECTID 245
"""
import asyncio
from mindsdb_agent import MindsDBAgent


async def main():
    agent = MindsDBAgent()

    print("\n" + "="*70)
    print("Quick Test: Find GeoJSON data source")
    print("="*70 + "\n")

    query = "Search for URLs containing 'highway' or 'FeatureServer' with limit 3"

    try:
        response = await agent.run(query)
        print("\nDone!")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
