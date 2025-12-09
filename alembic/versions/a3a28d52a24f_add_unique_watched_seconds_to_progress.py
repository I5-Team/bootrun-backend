"""add unique_watched_seconds to progress table

Revision ID: a3a28d52a24f
Revises: 81526e4abbc5
Create Date: 2025-12-09 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3a28d52a24f'
down_revision: Union[str, Sequence[str], None] = '81526e4abbc5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add unique_watched_seconds column with default value 0
    op.add_column('progresses', sa.Column('unique_watched_seconds', sa.Integer(), nullable=False, server_default='0', comment='유니크 시청 시간 (초) - 진행률 계산용'))

    # Update existing records: set unique_watched_seconds to min(watched_seconds, lecture.duration_seconds)
    # For simplicity, we'll initially set it equal to watched_seconds
    # The application logic will handle proper calculation on next update
    op.execute("""
        UPDATE progresses
        SET unique_watched_seconds = watched_seconds
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop the unique_watched_seconds column
    op.drop_column('progresses', 'unique_watched_seconds')
