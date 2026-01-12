-- ============================================================================
-- Zero Hunger Platform - MySQL Database Schema
-- ============================================================================
-- This file contains the complete database schema for the Zero Hunger Platform
-- Converted from PostgreSQL/Supabase to MySQL format
-- Run this SQL script in your MySQL database to set up the tables
-- ============================================================================

-- ============================================================================
-- Table: food_assistance_requests
-- Description: Stores food assistance requests from users
-- ============================================================================
CREATE TABLE IF NOT EXISTS food_assistance_requests (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    person_name TEXT NOT NULL,
    age INT NOT NULL,
    location TEXT NOT NULL,
    food_request TEXT NOT NULL,
    assistance_type ENUM('immediate', 'scheduled', 'ngo_referral') NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    status ENUM('pending', 'confirmed', 'delivered', 'cancelled') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_food_assistance_session (session_id),
    INDEX idx_food_assistance_status (status),
    INDEX idx_food_assistance_created (created_at),
    INDEX idx_food_assistance_type (assistance_type),
    INDEX idx_food_assistance_status_created (status, created_at),
    
    CONSTRAINT chk_age CHECK (age > 0 AND age <= 120)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

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
    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
    SUM(CASE WHEN status = 'confirmed' THEN 1 ELSE 0 END) as confirmed,
    SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) as delivered,
    SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) as cancelled
FROM food_assistance_requests
GROUP BY DATE(created_at), assistance_type
ORDER BY request_date DESC, assistance_type;

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
