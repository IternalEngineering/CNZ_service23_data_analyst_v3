# Add after line 37 (after write operation check)

# Safety check for large columns that cause context overflow
dangerous_columns = ['raw_data', 'error_details']
sql_lower = sql.lower()

for col in dangerous_columns:
    # Check if selecting these columns
    if f'select {col}' in sql_lower or f'select *' in sql_lower or f'{col}->' in sql_lower:
        return {
            "success": False,
            "error": f"Query blocked: Cannot select '{col}' column - it contains large JSON that will overflow context. Use metadata columns only (data_id, source_id, download_url, data_format, file_size_bytes, record_count)."
        }
