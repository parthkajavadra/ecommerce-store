from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'bb4f631b09fe'
down_revision: Union[str, Sequence[str], None] = '9b46ed37ef05'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    # Create the enum type if it doesn't exist already
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'orderstatus') THEN
            CREATE TYPE orderstatus AS ENUM ('pending', 'shipped', 'delivered', 'canceled');
        END IF;
    END;
    $$;
    """)
    
    # Modify the 'status' column to use the 'orderstatus' enum type
    op.alter_column('orders', 'status', type_=sa.Enum('pending', 'shipped', 'delivered', 'canceled', name='orderstatus'), existing_type=sa.String(), nullable=True)

    # Add other columns (if not already present)
    op.add_column('orders', sa.Column('payment_status', sa.String(), nullable=True))
    op.add_column('orders', sa.Column('shipping_status', sa.String(), nullable=True))

    # ### end Alembic commands ###

def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('orders', 'shipping_status')
    op.drop_column('orders', 'payment_status')
    op.drop_column('orders', 'status')
    # ### end Alembic commands ###
