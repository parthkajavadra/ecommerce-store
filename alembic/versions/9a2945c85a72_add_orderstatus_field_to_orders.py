"""Add OrderStatus field to orders

Revision ID: 9a2945c85a72
Revises: 800ebcb2025b
Create Date: 2025-07-08 19:23:25.877420

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9a2945c85a72'
down_revision: Union[str, Sequence[str], None] = '800ebcb2025b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # First, add the new column `total_amount` with nullable=True
    op.add_column('orders', sa.Column('total_amount', sa.Float(), nullable=True))

    # Now you should update all existing rows to set a valid value for total_amount (e.g., 0.0)
    # This step is important to ensure the column is not null for any existing rows
    op.execute("UPDATE orders SET total_amount = 0.0 WHERE total_amount IS NULL")

    # Then, alter the column to make it NOT NULL
    op.alter_column('orders', 'total_amount', nullable=False)

    # Drop the old `total_price` column
    op.drop_column('orders', 'total_price')


def downgrade() -> None:
    """Downgrade schema."""
    # If downgrading, you need to add back the `total_price` column and make it nullable
    op.add_column('orders', sa.Column('total_price', sa.Float(), nullable=True))
    
    # Drop the `total_amount` column
    op.drop_column('orders', 'total_amount')
