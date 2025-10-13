-- Add data_summary metadata column to service19_onboarding_data
-- This allows efficient querying without loading large raw_data/error_details

-- Step 1: Add the column
ALTER TABLE service19_onboarding_data
ADD COLUMN IF NOT EXISTS data_summary JSONB;

-- Step 2: Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_service19_data_summary
ON service19_onboarding_data USING gin (data_summary);

-- Step 3: Populate data_summary with metadata for all records
UPDATE service19_onboarding_data
SET data_summary = jsonb_build_object(
    -- Basic metadata
    'format', data_format,
    'size_bytes', file_size_bytes,
    'record_count', record_count,
    'http_status', http_status_code,
    'success', download_success,

    -- Content indicators
    'has_raw_data', raw_data IS NOT NULL,
    'has_error', error_message IS NOT NULL,
    'processing_status', processing_status,

    -- Data quality
    'is_valid_format', is_valid_format,
    'has_headers', has_headers,
    'column_count', column_count,
    'completeness_score', completeness_score,

    -- Error info (if exists)
    'error_summary', CASE
        WHEN error_message IS NOT NULL
        THEN LEFT(error_message, 200)  -- Only first 200 chars
        ELSE NULL
    END,

    -- Raw data preview (if exists)
    'raw_data_preview', CASE
        WHEN raw_data IS NOT NULL AND raw_data->>'raw_content' IS NOT NULL
        THEN LEFT(raw_data->>'raw_content', 200)  -- Only first 200 chars
        WHEN raw_data IS NOT NULL AND raw_data->>'parse_error' IS NOT NULL
        THEN raw_data->>'parse_error'
        ELSE NULL
    END,

    -- Timestamps
    'downloaded_at', download_timestamp,
    'processed_at', processed_timestamp,

    -- Hash for deduplication
    'data_hash', data_hash
)
WHERE data_summary IS NULL;

-- Step 4: Create a trigger to auto-populate data_summary on new inserts/updates
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

DROP TRIGGER IF EXISTS trigger_update_data_summary ON service19_onboarding_data;
CREATE TRIGGER trigger_update_data_summary
    BEFORE INSERT OR UPDATE ON service19_onboarding_data
    FOR EACH ROW
    EXECUTE FUNCTION update_data_summary();

-- Verify the update
SELECT
    COUNT(*) as total_records,
    COUNT(data_summary) as records_with_summary,
    COUNT(CASE WHEN data_summary->>'has_raw_data' = 'true' THEN 1 END) as has_raw_data,
    COUNT(CASE WHEN data_summary->>'has_error' = 'true' THEN 1 END) as has_errors
FROM service19_onboarding_data;

-- Show example summaries
SELECT
    data_id,
    source_id,
    download_success,
    data_summary
FROM service19_onboarding_data
LIMIT 5;
