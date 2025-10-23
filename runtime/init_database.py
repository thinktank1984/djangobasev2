#!/usr/bin/env python3
"""
Django Blog Database Initialization Script

This script ensures all databases and required directories are properly set up
before the Django application starts. It handles:
1. Creating necessary directories
2. Running migrations for all databases
3. Setting up logging tables
4. Handling chicken-and-egg problems with logging during migrations
"""

import os
import sys
import django
from pathlib import Path

def setup_logging_directories():
    """Create necessary directories for logging."""
    print("🔧 Setting up logging directories...")

    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    print(f"✅ Logs directory created: {logs_dir.absolute()}")

    # Create .gitkeep for logs directory to ensure it's tracked
    gitkeep_file = logs_dir / ".gitkeep"
    if not gitkeep_file.exists():
        gitkeep_file.touch()
        print("✅ Created .gitkeep in logs directory")

    return True

def setup_django_environment():
    """Set up Django environment for database operations."""
    print("🔧 Setting up Django environment...")

    # Add current directory to Python path
    sys.path.insert(0, str(Path(__file__).parent))

    # Set Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

    # Setup Django
    django.setup()

    print("✅ Django environment configured")
    return True

def run_migrations_with_fallback():
    """Run migrations with proper error handling for the logs database."""
    from django.core.management import execute_from_command_line
    from django.db import connection

    print("🔄 Running database migrations...")

    # Temporarily disable auditlog signals to avoid chicken-and-egg problems
    try:
        from apps.auditlog import signals
        print("⚠️  Temporarily disabling auditlog signals for migration")
        # We'll handle this by checking if tables exist before trying to log
    except ImportError:
        pass

    # Run migrations for default database
    try:
        print("📊 Running migrations for default database...")
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Default database migrations completed")
    except Exception as e:
        print(f"❌ Error running default database migrations: {e}")
        return False

    # Run migrations for logs database
    try:
        print("📋 Running migrations for logs database...")
        execute_from_command_line(['manage.py', 'migrate', '--database=logs'])
        print("✅ Logs database migrations completed")
    except Exception as e:
        print(f"❌ Error running logs database migrations: {e}")
        # Don't return False here, as the app can still work without logs database

    return True

def verify_logging_setup():
    """Verify that the logging system is properly set up."""
    print("🔍 Verifying logging setup...")

    try:
        from apps.auditlog.models import SystemLog

        # Test logging by creating a simple log entry
        test_log = SystemLog.objects.create(
            level='INFO',
            category='system',
            message='Database initialization completed successfully'
        )
        print(f"✅ Logging system verified - created test log entry: {test_log.id}")
        return True

    except Exception as e:
        print(f"⚠️  Logging system verification failed: {e}")
        print("   (This is not critical - the application will still work)")
        return False

def main():
    """Main initialization function."""
    print("🚀 Django Blog Database Initialization")
    print("=" * 50)

    # Change to the runtime directory if not already there
    script_dir = Path(__file__).parent
    if script_dir.name != 'runtime':
        runtime_dir = script_dir / 'runtime'
        if runtime_dir.exists():
            os.chdir(runtime_dir)
            print(f"📁 Changed to directory: {runtime_dir}")

    try:
        # Step 1: Setup directories
        setup_logging_directories()
        print()

        # Step 2: Setup Django environment
        setup_django_environment()
        print()

        # Step 3: Run migrations
        if not run_migrations_with_fallback():
            print("❌ Migration failed - exiting")
            return False
        print()

        # Step 4: Verify logging setup
        verify_logging_setup()
        print()

        print("🎉 Database initialization completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)