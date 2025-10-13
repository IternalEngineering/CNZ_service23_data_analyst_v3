#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Database Migration Runner
Executes the insights table creation SQL
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

from postgres_direct_tool import PostgresDirectTool


async def run_migration():
    """Run the database migration"""
    print("="*60)
    print("Database Migration: Create service23_data_analyst_insights")
    print("="*60)

    # Read SQL file
    sql_file = Path(__file__).parent / "create_insights_table.sql"

    if not sql_file.exists():
        print(f"❌ SQL file not found: {sql_file}")
        return False

    print(f"\nReading SQL from: {sql_file}")
    sql = sql_file.read_text()

    # Execute migration
    tool = PostgresDirectTool()

    try:
        print("\nConnecting to database...")
        connect_result = await tool.connect()

        if not connect_result.get("success"):
            print(f"❌ Connection failed: {connect_result.get('error')}")
            return False

        print("✓ Connected to PostgreSQL")

        print("\nExecuting migration SQL...")

        # Split SQL into individual statements
        all_statements = [s.strip() for s in sql.split(';') if s.strip()]

        # Filter and organize statements
        table_statements = []
        function_statements = []
        trigger_statements = []
        index_statements = []
        other_statements = []

        for stmt in all_statements:
            if not stmt or stmt.startswith('--'):
                continue
            if stmt.upper().startswith('COMMENT'):
                continue

            stmt_upper = stmt.upper()
            if 'CREATE TABLE' in stmt_upper:
                table_statements.append(stmt)
            elif 'CREATE OR REPLACE FUNCTION' in stmt_upper:
                function_statements.append(stmt)
            elif 'CREATE TRIGGER' in stmt_upper:
                trigger_statements.append(stmt)
            elif 'CREATE INDEX' in stmt_upper:
                index_statements.append(stmt)
            else:
                other_statements.append(stmt)

        # Execute in correct order: tables, functions, indexes, triggers
        statements = table_statements + function_statements + index_statements + trigger_statements + other_statements

        for i, statement in enumerate(statements, 1):
            print(f"\n[{i}/{len(statements)}] Executing statement...")
            print(f"  {statement[:80]}...")

            result = await tool.query(statement + ';')

            if result.get("success"):
                print("  ✓ Success")
            else:
                error = result.get("error", "Unknown error")
                if "already exists" in error.lower():
                    print(f"  ⚠ Already exists (skipping)")
                else:
                    print(f"  ❌ Error: {error}")
                    # Don't fail on index errors if table exists
                    if 'CREATE INDEX' not in statement.upper():
                        return False

        print("\n" + "="*60)
        print("Migration completed successfully!")
        print("="*60)

        # Verify table creation
        print("\nVerifying table...")
        verify_sql = """
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'service23_data_analyst_insights'
        ORDER BY ordinal_position
        LIMIT 20
        """

        result = await tool.query(verify_sql)

        if result.get("success") and result.get("row_count", 0) > 0:
            print(f"✓ Table verified with {result['row_count']} columns")
            print("\nColumns:")
            for row in result.get("data", [])[:5]:
                print(f"  - {row['column_name']}: {row['data_type']}")
            if result['row_count'] > 5:
                print(f"  ... and {result['row_count'] - 5} more columns")
        else:
            print("⚠ Could not verify table creation")

        return True

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        await tool.close()


if __name__ == "__main__":
    success = asyncio.run(run_migration())
    exit(0 if success else 1)
