#!/usr/bin/env python
"""
Query city fetch success rates from SERVICE19 data
Simple script to avoid token limit issues
"""
import httpx
import json
from typing import Dict, Any

MINDSDB_URL = "http://localhost:47334"

def query_mindsdb(sql: str) -> Dict[str, Any]:
    """Execute SQL query via MindsDB API"""
    try:
        response = httpx.post(
            f"{MINDSDB_URL}/api/sql/query",
            json={"query": sql},
            headers={"Content-Type": "application/json"},
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"type": "error", "error_message": str(e)}


def get_city_success_rates():
    """Get fetch success rates by city"""
    sql = """
    SELECT
        s.city_name,
        COUNT(*) as total_attempts,
        SUM(CASE WHEN d.download_success = true THEN 1 ELSE 0 END) as successful_fetches,
        ROUND(100.0 * SUM(CASE WHEN d.download_success = true THEN 1 ELSE 0 END) / COUNT(*), 2) as success_rate_percent
    FROM urbanzero_postgres.service19_onboarding_data d
    JOIN urbanzero_postgres.service19_onboarding_agent_sources s ON d.source_id = s.source_id
    GROUP BY s.city_name
    HAVING COUNT(*) > 0
    ORDER BY success_rate_percent DESC, total_attempts DESC;
    """

    result = query_mindsdb(sql)

    if result.get("type") == "error":
        print(f"Error: {result.get('error_message')}")
        return

    if result.get("type") == "table":
        columns = result.get("column_names", [])
        data = result.get("data", [])

        print("\n" + "="*80)
        print("CITY FETCH SUCCESS RATES")
        print("="*80)
        print(f"\n{'City':<20} {'Total Attempts':<15} {'Successful':<15} {'Success Rate':<15}")
        print("-"*80)

        for row in data:
            city = row[0] or "Unknown"
            total = row[1]
            successful = row[2]
            success_rate = row[3]
            print(f"{city:<20} {total:<15} {successful:<15} {success_rate:<14.2f}%")

        print("="*80)
        print(f"\nTotal cities analyzed: {len(data)}")
        print()

        # Show top 5
        if len(data) > 0:
            print("\nTOP 5 CITIES BY SUCCESS RATE:")
            print("-"*80)
            for i, row in enumerate(data[:5], 1):
                city = row[0] or "Unknown"
                success_rate = row[3]
                total = row[1]
                successful = row[2]
                print(f"{i}. {city}: {success_rate:.2f}% ({successful}/{total} successful)")


if __name__ == "__main__":
    # First check MindsDB is running
    try:
        status = query_mindsdb("SELECT 1;")
        if status.get("type") == "error":
            print("ERROR: Cannot connect to MindsDB at http://localhost:47334")
            print("Please ensure SSH tunnel is running:")
            print("  cd C:\\Users\\chriz\\OneDrive\\Documents\\CNZ\\UrbanZero2\\UrbanZero\\server_c")
            print("  .\\setup_tunnel.ps1")
            exit(1)
    except Exception as e:
        print(f"ERROR: Cannot connect to MindsDB: {e}")
        exit(1)

    get_city_success_rates()
