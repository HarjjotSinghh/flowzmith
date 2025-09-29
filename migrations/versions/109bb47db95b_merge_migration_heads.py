"""Merge migration heads

Revision ID: 109bb47db95b
Revises: a1b2c3d4e5f6, e58c0e0fe53e
Create Date: 2025-09-30 04:16:51.142294

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '109bb47db95b'
down_revision: Union[str, Sequence[str], None] = ('a1b2c3d4e5f6', 'e58c0e0fe53e')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
