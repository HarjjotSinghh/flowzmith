#!/usr/bin/env python3
"""
Script to drop all database tables for fresh migration.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.models.database import drop_tables, check_database_connection
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Drop all database tables."""
    logger.info("Starting database cleanup...")

    # Check database connection
    if not check_database_connection():
        logger.error("Database connection failed. Please check your configuration.")
        return False

    # Drop tables
    try:
        drop_tables()
        logger.info("Database tables dropped successfully!")
        return True
    except Exception as e:
        logger.error(f"Database cleanup failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)