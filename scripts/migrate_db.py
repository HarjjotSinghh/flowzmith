#!/usr/bin/env python3
"""
Database migration script.
"""

import sys
import os
import subprocess

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main migration function."""
    print("🚀 Starting database migration...")

    # Change to project directory
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    commands = [
        ("alembic upgrade head", "Upgrading database to latest version"),
    ]

    for cmd, desc in commands:
        if not run_command(cmd, desc):
            print("❌ Migration failed. Please check the error messages above.")
            return False

    print("🎉 Database migration completed successfully!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)