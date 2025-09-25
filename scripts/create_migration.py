#!/usr/bin/env python3
"""
Script to create a new database migration.
"""

import sys
import os
import subprocess
import argparse

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
    """Main function."""
    parser = argparse.ArgumentParser(description="Create a new database migration")
    parser.add_argument("message", help="Migration message")
    parser.add_argument("--autogenerate", action="store_true", help="Auto-generate migration")

    args = parser.parse_args()

    print(f"🚀 Creating new migration: {args.message}")

    # Change to project directory
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    cmd = f"alembic revision --autogenerate -m \"{args.message}\"" if args.autogenerate else f"alembic revision -m \"{args.message}\""

    if run_command(cmd, "Creating migration"):
        print("🎉 Migration created successfully!")
        print("💡 Don't forget to review and edit the migration file before applying it.")
        return True

    return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)