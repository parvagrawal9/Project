-- ============================================================================
-- Zero Hunger Platform - Supabase Database Schema
-- ============================================================================
-- This file contains the complete database schema for the Zero Hunger Platform
-- Run this SQL script in your Supabase SQL Editor to set up the database
-- ============================================================================

-- Enable UUID extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- Table: food_assistance_requests
-- Description: Stores food assistance requests from users
-- ============================================================================
CREATE TABLE IF NOT EXISTS food_assistance_requests (
    id BIGSERIAL PRIMARY KEY,
    person_name TEXT NOT NULL,
    age INTEGER NOT NULL CHECK (age > 0 AND age <= 120),
    location TEXT NOT NULL,
    food_request TEXT NOT NULL,
    assistance_type TEXT NOT NULL CHECK (assistance_type IN ('immediate', 'scheduled', 'ngo_referral')),
    session_id TEXT NOT NULL,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'delivered', 'cancelled')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- Indexes for better query performance
-- ============================================================================

-- Index on session_id for faster session lookups
CREATE INDEX IF NOT EXISTS idx_food_assistance_session 
    ON food_assistance_requests(session_id);

-- Index on status for filtering by request status
CREATE INDEX IF NOT EXISTS idx_food_assistance_status 
    ON food_assistance_requests(status);

-- Index on created_at for time-based queries and sorting
CREATE INDEX IF NOT EXISTS idx_food_assistance_created 
    ON food_assistance_requests(created_at DESC);

-- Index on assistance_type for filtering by type
CREATE INDEX IF NOT EXISTS idx_food_assistance_type 
    ON food_assistance_requests(assistance_type);

-- Composite index for common query patterns (status + created_at)
CREATE INDEX IF NOT EXISTS idx_food_assistance_status_created 
    ON food_assistance_requests(status, created_at DESC);

-- ============================================================================
-- Function: Update updated_at timestamp automatically
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- ============================================================================
-- Trigger: Automatically update updated_at on row updates
-- ============================================================================
DROP TRIGGER IF EXISTS update_food_assistance_requests_updated_at ON food_assistance_requests;
CREATE TRIGGER update_food_assistance_requests_updated_at
    BEFORE UPDATE ON food_assistance_requests
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Row Level Security (RLS) Policies
-- ============================================================================

-- Enable RLS on the table
ALTER TABLE food_assistance_requests ENABLE ROW LEVEL SECURITY;

-- Policy: Allow anonymous inserts (for public API access)
-- Adjust this based on your authentication requirements
CREATE POLICY "Allow anonymous inserts" ON food_assistance_requests
    FOR INSERT
    TO anon
    WITH CHECK (true);

-- Policy: Allow service role full access (for backend operations)
CREATE POLICY "Allow service role full access" ON food_assistance_requests
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Policy: Allow authenticated users to read their own requests
-- Uncomment and adjust if you implement user authentication
-- CREATE POLICY "Users can read own requests" ON food_assistance_requests
--     FOR SELECT
--     TO authenticated
--     USING (auth.uid()::text = session_id);

-- ============================================================================
-- Optional: Views for common queries
-- ============================================================================

-- View: Recent pending requests
CREATE OR REPLACE VIEW recent_pending_requests AS
SELECT 
    id,
    person_name,
    age,
    location,
    food_request,
    assistance_type,
    session_id,
    status,
    created_at,
    updated_at
FROM food_assistance_requests
WHERE status = 'pending'
ORDER BY created_at DESC;

-- View: Request statistics by type
CREATE OR REPLACE VIEW request_stats_by_type AS
SELECT 
    assistance_type,
    status,
    COUNT(*) as count,
    MIN(created_at) as first_request,
    MAX(created_at) as last_request
FROM food_assistance_requests
GROUP BY assistance_type, status
ORDER BY assistance_type, status;

-- View: Daily request summary
CREATE OR REPLACE VIEW daily_request_summary AS
SELECT 
    DATE(created_at) as request_date,
    assistance_type,
    COUNT(*) as total_requests,
    COUNT(*) FILTER (WHERE status = 'pending') as pending,
    COUNT(*) FILTER (WHERE status = 'confirmed') as confirmed,
    COUNT(*) FILTER (WHERE status = 'delivered') as delivered,
    COUNT(*) FILTER (WHERE status = 'cancelled') as cancelled
FROM food_assistance_requests
GROUP BY DATE(created_at), assistance_type
ORDER BY request_date DESC, assistance_type;

-- ============================================================================
-- Comments for documentation
-- ============================================================================

COMMENT ON TABLE food_assistance_requests IS 'Stores food assistance requests from users through the AI chat interface';
COMMENT ON COLUMN food_assistance_requests.id IS 'Primary key, auto-incrementing';
COMMENT ON COLUMN food_assistance_requests.person_name IS 'Name of the person requesting food assistance';
COMMENT ON COLUMN food_assistance_requests.age IS 'Age of the person (1-120)';
COMMENT ON COLUMN food_assistance_requests.location IS 'Location or area where food is needed';
COMMENT ON COLUMN food_assistance_requests.food_request IS 'Description of food requirements or specific needs';
COMMENT ON COLUMN food_assistance_requests.assistance_type IS 'Type of assistance: immediate, scheduled, or ngo_referral';
COMMENT ON COLUMN food_assistance_requests.session_id IS 'Unique session identifier for the conversation';
COMMENT ON COLUMN food_assistance_requests.status IS 'Current status: pending, confirmed, delivered, or cancelled';
COMMENT ON COLUMN food_assistance_requests.created_at IS 'Timestamp when the request was created';
COMMENT ON COLUMN food_assistance_requests.updated_at IS 'Timestamp when the request was last updated';

-- ============================================================================
-- Sample data (optional - for testing)
-- ============================================================================

-- Uncomment to insert sample data for testing
-- INSERT INTO food_assistance_requests (person_name, age, location, food_request, assistance_type, session_id, status)
-- VALUES 
--     ('John Doe', 30, '123 Main St, City', 'Vegetarian meal for 2 people', 'immediate', 'test-session-1', 'pending'),
--     ('Jane Smith', 25, '456 Oak Ave, Town', 'Need food for tomorrow', 'scheduled', 'test-session-2', 'confirmed');

-- ============================================================================
-- End of Schema
-- ============================================================================
