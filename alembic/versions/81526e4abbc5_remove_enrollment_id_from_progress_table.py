"""remove enrollment_id from progress table

Revision ID: 81526e4abbc5
Revises: c7f31f054450
Create Date: 2025-11-16 16:44:12.116787

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '81526e4abbc5'
down_revision: Union[str, Sequence[str], None] = 'c7f31f054450'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop foreign key constraint first
    op.drop_constraint('progresses_enrollment_id_fkey', 'progresses', type_='foreignkey')

    # Drop the enrollment_id column
    op.drop_column('progresses', 'enrollment_id')


def downgrade() -> None:
    """Downgrade schema."""
    # Add back the enrollment_id column
    op.add_column('progresses', sa.Column('enrollment_id', sa.INTEGER(), nullable=True))

    # Recreate the foreign key constraint
    op.create_foreign_key('progresses_enrollment_id_fkey', 'progresses', 'enrollments', ['enrollment_id'], ['id'], ondelete='CASCADE')

    # Note: Cannot restore the NOT NULL constraint without data migration
