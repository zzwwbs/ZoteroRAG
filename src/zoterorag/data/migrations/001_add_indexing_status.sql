-- Add indexing_status to documents table
ALTER TABLE documents ADD COLUMN indexing_status TEXT DEFAULT 'Not Indexed';
