-- PostgreSQL initialization script for DjangoBaseV2
-- This script runs when the PostgreSQL container starts

-- Create the main database
-- Note: This is already created by POSTGRES_DB environment variable
-- CREATE DATABASE IF NOT EXISTS djangobasev2_dev;

-- Create additional databases for testing
CREATE DATABASE IF NOT EXISTS djangobasev2_test;

-- Create development users (optional)
-- CREATE USER IF NOT EXISTS djangodev WITH PASSWORD 'devpassword';
-- GRANT ALL PRIVILEGES ON DATABASE djangobasev2_dev TO djangodev;
-- GRANT ALL PRIVILEGES ON DATABASE djangobasev2_test TO djangodev;

-- Create extensions that might be useful for Django
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- Set up default permissions
ALTER DATABASE djangobasev2_dev SET timezone TO 'UTC';
ALTER DATABASE djangobasev2_test SET timezone TO 'UTC';

-- Output initialization message
\echo 'PostgreSQL database initialization completed for DjangoBaseV2'