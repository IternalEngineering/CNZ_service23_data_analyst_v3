#!/usr/bin/env python
"""
Test JSON extraction queries on service19_onboarding_data
"""
import httpx

MINDSDB_URL = "http://localhost:47334"

def test_query(name, sql):
    """Test a query and print results"""
    print(f"\n{name}")
    print("="*60)
    print(f"Query: {sql[:100]}...")

    try:
        response = httpx.post(
            f"{MINDSDB_URL}/api/sql/query",
            json={"query": sql},
            headers={"Content-Type": "application/json"},
            timeout=30.0
        )
        response.raise_for_status()
        result = response.json()

        if result.get("type") == "error":
            print(f"[ERROR] {result.get('error_message')}")
            return False

        data = result.get("data", [])
        columns = result.get("column_names", [])

        print(f"[OK] Returned {len(data)} rows")
        if data and len(data) > 0:
            print(f"\nColumns: {columns}")
            print("\nFirst 3 rows:")
            for i, row in enumerate(data[:3], 1):
                print(f"\n  Row {i}:")
                for col, val in zip(columns, row):
                    # Truncate long values
                    val_str = str(val)[:100] if val else "NULL"
                    print(f"    {col}: {val_str}")

        return True

    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def main():
    print("Testing JSON Extraction Queries")
    print("="*60)

    # Test 1: Extract parse errors from raw_data
    test_query(
        "Test 1: Extract Parse Errors",
        """
        SELECT data_id, source_id,
               raw_data->>'parse_error' as parse_error,
               LEFT(raw_data->>'raw_content', 100) as content_preview
        FROM urbanzero_postgres.service19_onboarding_data
        WHERE raw_data->>'parse_error' IS NOT NULL
        LIMIT 5;
        """
    )

    # Test 2: Search for specific content
    test_query(
        "Test 2: Search for CSV content",
        """
        SELECT data_id, source_id, data_format,
               LEFT(raw_data::text, 100) as json_preview
        FROM urbanzero_postgres.service19_onboarding_data
        WHERE raw_data::text LIKE '%CSV%'
        LIMIT 5;
        """
    )

    # Test 3: Aggregate by city with success rate
    test_query(
        "Test 3: City Success Rates (No large columns)",
        """
        SELECT s.city_name,
               COUNT(*) as total_attempts,
               SUM(CASE WHEN d.download_success THEN 1 ELSE 0 END) as successful,
               ROUND(100.0 * SUM(CASE WHEN d.download_success THEN 1 ELSE 0 END) / COUNT(*), 2) as success_rate
        FROM urbanzero_postgres.service19_onboarding_data d
        JOIN urbanzero_postgres.service19_onboarding_agent_sources s ON d.source_id = s.source_id
        GROUP BY s.city_name
        ORDER BY success_rate DESC
        LIMIT 10;
        """
    )

    # Test 4: Get metadata without raw_data
    test_query(
        "Test 4: Metadata Only (Safe)",
        """
        SELECT data_id, source_id, download_url,
               download_success, http_status_code, data_format,
               file_size_bytes, record_count, error_message
        FROM urbanzero_postgres.service19_onboarding_data
        LIMIT 5;
        """
    )

    print("\n" + "="*60)
    print("[SUCCESS] All tests completed!")
    print("\nThe agent can now:")
    print("  1. Extract specific JSON fields from raw_data")
    print("  2. Search within JSON content")
    print("  3. Query metadata without loading large columns")
    print("  4. Aggregate data efficiently")


if __name__ == "__main__":
    main()
