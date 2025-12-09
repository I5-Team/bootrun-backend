"""merge heads

Revision ID: 7c1a4de1de38
Revises: a3a28d52a24f, b4e8a9c2f3d1
Create Date: 2025-12-09 14:50:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '7c1a4de1de38'
down_revision: Union[str, Sequence[str], None] = ('a3a28d52a24f', 'b4e8a9c2f3d1')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass
