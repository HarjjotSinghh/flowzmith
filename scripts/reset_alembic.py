#!/usr/bin/env python3
"""
Script to reset Alembic version table.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import text
from src.models.database import engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Reset Alembic version table."""
    logger.info("Resetting Alembic version table...")

    try:
        with engine.connect() as connection:
            # Drop alembic_version table if it exists
            connection.execute(text("DROP TABLE IF EXISTS alembic_version"))
            connection.commit()
            logger.info("Alembic version table reset successfully!")
            return True
    except Exception as e:
        logger.error(f"Failed to reset Alembic version table: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)