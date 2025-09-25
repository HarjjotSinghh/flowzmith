#!/usr/bin/env python3
"""
Database setup script.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.models.database import create_tables, check_database_connection
from src.models import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Set up the database."""
    logger.info("Starting database setup...")

    # Check database connection
    if not check_database_connection():
        logger.error("Database connection failed. Please check your configuration.")
        return False

    # Create tables
    try:
        create_tables()
        logger.info("Database setup completed successfully!")
        return True
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)