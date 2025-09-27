"""add_additional_files_info_to_generated_contracts

Revision ID: a1b2c3d4e5f6
Revises: f4e4aaade729
Create Date: 2025-09-28 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'f4e4aaade729'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add additional_files_info column to generated_contracts table
    op.add_column('generated_contracts', sa.Column('additional_files_info', sa.JSON(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove additional_files_info column from generated_contracts table
    op.drop_column('generated_contracts', 'additional_files_info')
