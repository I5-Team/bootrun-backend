"""add toss payment fields to payments table

Revision ID: add_toss_fields_001
Revises: c7f31f054450
Create Date: 2025-12-05 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_toss_fields_001'
down_revision: Union[str, Sequence[str], None] = '81526e4abbc5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add order_id and payment_key columns to payments table."""
    # Add order_id column
    op.add_column('payments', sa.Column('order_id', sa.String(length=100), nullable=True, comment='주문 ID (토스 연동용, 기존 데이터는 NULL)'))
    op.create_index(op.f('ix_payments_order_id'), 'payments', ['order_id'], unique=True)

    # Add payment_key column
    op.add_column('payments', sa.Column('payment_key', sa.String(length=200), nullable=True, comment='토스 결제 키'))


def downgrade() -> None:
    """Remove order_id and payment_key columns from payments table."""
    # Remove payment_key column
    op.drop_column('payments', 'payment_key')

    # Remove order_id column
    op.drop_index(op.f('ix_payments_order_id'), table_name='payments')
    op.drop_column('payments', 'order_id')