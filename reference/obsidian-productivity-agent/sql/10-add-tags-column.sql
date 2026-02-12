-- Migration script to add tags column to document_metadata table
-- This adds support for tag-based filtering and document discovery

-- Add tags column to document_metadata table
ALTER TABLE document_metadata
ADD COLUMN IF NOT EXISTS tags JSONB DEFAULT '[]'::jsonb;

-- Add GIN index for efficient tag searches
CREATE INDEX IF NOT EXISTS idx_document_metadata_tags
ON document_metadata USING GIN (tags);

-- Add comment for documentation
COMMENT ON COLUMN document_metadata.tags IS 'Array of tags extracted from markdown documents for categorization and filtering';