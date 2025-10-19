-- PostgreSQL initialization script for DjangoBase Project
-- This script runs when the database container is first created

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create database user with enhanced permissions
CREATE USER djangouser WITH PASSWORD 'djangopass';

-- Grant necessary permissions
GRANT CONNECT ON DATABASE djangobase TO djangouser;
GRANT USAGE ON SCHEMA public TO djangouser;
GRANT CREATE ON SCHEMA public TO djangouser;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO djangouser;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO djangouser;

-- Create indexes for common queries (will be created after Django migrations)
-- These are placeholders that will be optimized after models are created

-- Performance settings
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET track_activity_query_size = 2048;
ALTER SYSTEM SET pg_stat_statements.track = 'all';

-- Log slow queries (optional, for development)
ALTER SYSTEM SET log_min_duration_statement = 1000; -- Log queries taking more than 1 second
ALTER SYSTEM SET log_statement = 'none'; -- Don't log all statements
ALTER SYSTEM SET log_duration = 'on';

-- Reload configuration
SELECT pg_reload_conf();

-- Create initial admin user (this will be handled by Django createsuperuser command)
-- Leaving this commented as Django should handle user creation

-- Add useful functions for future use
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Comment for future developers
COMMENT ON DATABASE djangobase IS 'DjangoBase Project Database - Initialized with Docker';