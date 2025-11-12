"""add_material_url_to_lectures

Revision ID: d6549c8c75da
Revises: d877848e3d9c
Create Date: 2025-11-12 10:06:13.056957

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd6549c8c75da'
down_revision: Union[str, Sequence[str], None] = 'd877848e3d9c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('lectures', sa.Column('material_url', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('lectures', 'material_url')
