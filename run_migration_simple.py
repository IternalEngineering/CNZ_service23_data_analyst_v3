#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple Database Migration Runner
Executes the insights table creation SQL directly
"""
import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'ignore')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'ignore')

# Load environment
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

try:
    import asyncpg
except ImportError:
    print("ERROR: asyncpg not installed")
    print("Run: pip install asyncpg")
    sys.exit(1)


async def run_migration():
    """Run the database migration"""
    print("="*60)
    print("Database Migration: service23_data_analyst_insights")
    print("="*60)

    # Database configuration
    host = os.getenv('POSTGRES_HOST', 'urbanzero-db.c5qeo4ayy5u5.eu-west-2.rds.amazonaws.com')
    port = int(os.getenv('POSTGRES_PORT', '5432'))
    database = os.getenv('POSTGRES_DATABASE', 'urbanzero-db')
    user = os.getenv('POSTGRES_USER', 'urbanzero_app')
    password = os.getenv('POSTGRES_PASSWORD', 'UrbanZero2024$Secure')

    # Read SQL file
    sql_file = Path(__file__).parent / "create_insights_table.sql"

    if not sql_file.exists():
        print(f"ERROR: SQL file not found: {sql_file}")
        return False

    print(f"\nReading SQL from: {sql_file}")
    sql = sql_file.read_text()

    # Connect to database
    try:
        print("\nConnecting to PostgreSQL...")
        conn = await asyncpg.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            ssl='require'
        )
        print("✓ Connected")

        # Execute SQL
        print("\nExecuting migration SQL...")
        await conn.execute(sql)
        print("✓ Migration completed")

        # Verify table
        print("\nVerifying table...")
        result = await conn.fetch("""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'service23_data_analyst_insights'
            ORDER BY ordinal_position
        """)

        if result:
            print(f"✓ Table verified with {len(result)} columns:")
            for i, row in enumerate(result[:5], 1):
                print(f"  {i}. {row['column_name']}: {row['data_type']}")
            if len(result) > 5:
                print(f"  ... and {len(result) - 5} more columns")
        else:
            print("⚠ Could not verify table")

        await conn.close()

        print("\n" + "="*60)
        print("SUCCESS!")
        print("="*60)
        return True

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(run_migration())
    sys.exit(0 if success else 1)
