#!/usr/bin/env python3
import subprocess
import sys

def create_postgres_setup():
    """Create PostgreSQL database and user"""
    try:
        # Create database
        cmd_createdb = ['createdb', '-h', 'localhost', '-p', '5433', 'djangobase']
        result = subprocess.run(cmd_createdb, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Database 'djangobase' created successfully")
        else:
            print(f"Database creation failed: {result.stderr}")

        # Try to create user with createuser
        cmd_createuser = ['createuser', '-h', 'localhost', '-p', '5433', '-s', 'postgres']
        result = subprocess.run(cmd_createuser, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ User 'postgres' created successfully")
        else:
            print(f"User creation failed: {result.stderr}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_postgres_setup()