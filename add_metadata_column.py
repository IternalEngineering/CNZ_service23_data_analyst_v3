#!/usr/bin/env python
"""
Add data_summary metadata column to service19_onboarding_data table
"""
import asyncio
import asyncpg
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Database connection via SSH tunnel
DB_CONFIG = {
    'host': 'localhost',  # Through SSH tunnel
    'port': 5432,
    'database': 'urbanzero-db',
    'user': 'urbanzero_app',
    'password': 'UrbanZero2024$Secure'
}

async def add_metadata_column():
    """Add and populate data_summary column"""
    print("Connecting to database...")
    conn = await asyncpg.connect(**DB_CONFIG)

    try:
        print("\n1. Adding data_summary column...")
        await conn.execute("""
            ALTER TABLE service19_onboarding_data
            ADD COLUMN IF NOT EXISTS data_summary JSONB;
        """)
        print("✓ Column added")

        print("\n2. Creating GIN index...")
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_service19_data_summary
            ON service19_onboarding_data USING gin (data_summary);
        """)
        print("✓ Index created")

        print("\n3. Populating data_summary for existing records...")
        result = await conn.execute("""
            UPDATE service19_onboarding_data
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
                END,
                'downloaded_at', download_timestamp,
                'processed_at', processed_timestamp,
                'data_hash', data_hash
            )
            WHERE data_summary IS NULL;
        """)
        print(f"✓ Updated {result} records")

        print("\n4. Creating trigger function...")
        await conn.execute("""
            CREATE OR REPLACE FUNCTION update_data_summary()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.data_summary = jsonb_build_object(
                    'format', NEW.data_format,
                    'size_bytes', NEW.file_size_bytes,
                    'record_count', NEW.record_count,
                    'http_status', NEW.http_status_code,
                    'success', NEW.download_success,
                    'has_raw_data', NEW.raw_data IS NOT NULL,
                    'has_error', NEW.error_message IS NOT NULL,
                    'processing_status', NEW.processing_status,
                    'is_valid_format', NEW.is_valid_format,
                    'has_headers', NEW.has_headers,
                    'column_count', NEW.column_count,
                    'completeness_score', NEW.completeness_score,
                    'error_summary', CASE
                        WHEN NEW.error_message IS NOT NULL
                        THEN LEFT(NEW.error_message, 200)
                        ELSE NULL
                    END,
                    'raw_data_preview', CASE
                        WHEN NEW.raw_data IS NOT NULL AND NEW.raw_data->>'raw_content' IS NOT NULL
                        THEN LEFT(NEW.raw_data->>'raw_content', 200)
                        WHEN NEW.raw_data IS NOT NULL AND NEW.raw_data->>'parse_error' IS NOT NULL
                        THEN NEW.raw_data->>'parse_error'
                        ELSE NULL
                    END,
                    'downloaded_at', NEW.download_timestamp,
                    'processed_at', NEW.processed_timestamp,
                    'data_hash', NEW.data_hash
                );
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """)
        print("✓ Trigger function created")

        print("\n5. Creating trigger...")
        await conn.execute("""
            DROP TRIGGER IF EXISTS trigger_update_data_summary ON service19_onboarding_data;
            CREATE TRIGGER trigger_update_data_summary
                BEFORE INSERT OR UPDATE ON service19_onboarding_data
                FOR EACH ROW
                EXECUTE FUNCTION update_data_summary();
        """)
        print("✓ Trigger created")

        print("\n6. Verifying results...")
        stats = await conn.fetchrow("""
            SELECT
                COUNT(*) as total_records,
                COUNT(data_summary) as records_with_summary,
                COUNT(CASE WHEN data_summary->>'has_raw_data' = 'true' THEN 1 END) as has_raw_data,
                COUNT(CASE WHEN data_summary->>'has_error' = 'true' THEN 1 END) as has_errors
            FROM service19_onboarding_data;
        """)

        print("\nStatistics:")
        print(f"  Total records: {stats['total_records']}")
        print(f"  Records with summary: {stats['records_with_summary']}")
        print(f"  Records with raw data: {stats['has_raw_data']}")
        print(f"  Records with errors: {stats['has_errors']}")

        print("\n7. Sample data_summary records:")
        samples = await conn.fetch("""
            SELECT
                data_id,
                source_id,
                download_success,
                data_summary
            FROM service19_onboarding_data
            LIMIT 3;
        """)

        for i, row in enumerate(samples, 1):
            print(f"\n  Record {i}:")
            print(f"    ID: {row['data_id']}")
            print(f"    Success: {row['download_success']}")
            print(f"    Summary: {row['data_summary']}")

        print("\n✅ Metadata column successfully added and populated!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(add_metadata_column())
