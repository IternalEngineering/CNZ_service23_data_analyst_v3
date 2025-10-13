#!/usr/bin/env python
"""
Add data_summary metadata column via MindsDB
"""
import httpx
import json

MINDSDB_URL = "http://localhost:47334"

def execute_sql(sql: str):
    """Execute SQL via MindsDB"""
    try:
        response = httpx.post(
            f"{MINDSDB_URL}/api/sql/query",
            json={"query": sql},
            headers={"Content-Type": "application/json"},
            timeout=120.0
        )
        response.raise_for_status()
        result = response.json()

        if result.get("type") == "error":
            print(f"[ERROR] {result.get('error_message')}")
            return False

        print(f"[OK] Success")
        if result.get("data"):
            print(f"  Rows affected/returned: {len(result['data'])}")
        return True

    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def main():
    print("Adding data_summary metadata column via MindsDB")
    print("="*60)

    # Step 1: Add column
    print("\n1. Adding data_summary column...")
    execute_sql("""
        ALTER TABLE urbanzero_postgres.service19_onboarding_data
        ADD COLUMN IF NOT EXISTS data_summary JSONB;
    """)

    # Step 2: Populate (in batches to avoid timeout)
    print("\n2. Populating data_summary...")
    print("   (This may take a while for large tables)")
    execute_sql("""
        UPDATE urbanzero_postgres.service19_onboarding_data
        SET data_summary = jsonb_build_object(
            'format', data_format,
            'size_bytes', file_size_bytes,
            'record_count', record_count,
            'http_status', http_status_code,
            'success', download_success,
            'has_raw_data', raw_data IS NOT NULL,
            'has_error', error_message IS NOT NULL,
            'processing_status', processing_status,
            'is_valid_format', is_valid_format,
            'has_headers', has_headers,
            'column_count', column_count,
            'completeness_score', completeness_score,
            'error_summary', CASE
                WHEN error_message IS NOT NULL
                THEN LEFT(error_message, 200)
                ELSE NULL
            END,
            'raw_data_preview', CASE
                WHEN raw_data IS NOT NULL AND raw_data->>'raw_content' IS NOT NULL
                THEN LEFT(raw_data->>'raw_content', 200)
                WHEN raw_data IS NOT NULL AND raw_data->>'parse_error' IS NOT NULL
                THEN raw_data->>'parse_error'
                ELSE NULL
            END
        )
        WHERE data_summary IS NULL;
    """)

    # Step 3: Verify
    print("\n3. Verifying results...")
    response = httpx.post(
        f"{MINDSDB_URL}/api/sql/query",
        json={"query": """
            SELECT
                COUNT(*) as total_records,
                COUNT(data_summary) as records_with_summary
            FROM urbanzero_postgres.service19_onboarding_data;
        """},
        headers={"Content-Type": "application/json"},
        timeout=30.0
    )

    if response.status_code == 200:
        result = response.json()
        if result.get("data"):
            stats = result["data"][0]
            print(f"\n  Total records: {stats[0]}")
            print(f"  Records with summary: {stats[1]}")

    # Step 4: Show sample
    print("\n4. Sample data_summary records:")
    response = httpx.post(
        f"{MINDSDB_URL}/api/sql/query",
        json={"query": """
            SELECT
                data_id,
                download_success,
                data_summary->>'format' as format,
                data_summary->>'size_bytes' as size,
                data_summary->>'has_error' as has_error
            FROM urbanzero_postgres.service19_onboarding_data
            WHERE data_summary IS NOT NULL
            LIMIT 3;
        """},
        headers={"Content-Type": "application/json"},
        timeout=30.0
    )

    if response.status_code == 200:
        result = response.json()
        if result.get("data"):
            for i, row in enumerate(result["data"], 1):
                print(f"\n  Record {i}:")
                print(f"    ID: {row[0]}")
                print(f"    Success: {row[1]}")
                print(f"    Format: {row[2]}")
                print(f"    Size: {row[3]} bytes")
                print(f"    Has Error: {row[4]}")

    print("\n" + "="*60)
    print("[SUCCESS] Metadata column setup complete!")
    print("\nThe agent can now query data_summary for efficient metadata access")
    print("without loading large raw_data or error_details fields.")


if __name__ == "__main__":
    main()
