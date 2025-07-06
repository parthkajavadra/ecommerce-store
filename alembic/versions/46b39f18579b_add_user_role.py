"""Add user role

Revision ID: 46b39f18579b
Revises: d82ba39e49d1
Create Date: 2025-07-04 12:07:45.849162
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '46b39f18579b'
down_revision: Union[str, Sequence[str], None] = 'd82ba39e49d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum type manually (sa.Enum is okay here)
    userrole_enum = sa.Enum('USER', 'SELLER', 'ADMIN', name='userrole')
    userrole_enum.create(op.get_bind(), checkfirst=True)

    # Add columns
    op.add_column('users', sa.Column('full_name', sa.String(), nullable=True))
    op.add_column(
        'users',
        sa.Column('role', userrole_enum, nullable=False, server_default='USER')
    )
    op.add_column('users', sa.Column('created_at', sa.DateTime(), nullable=True))

    # Drop old column
    op.drop_column('users', 'is_admin')


def downgrade() -> None:
    # Re-add old column
    op.add_column('users', sa.Column('is_admin', sa.BOOLEAN(), nullable=True))

    # Remove new columns
    op.drop_column('users', 'created_at')
    op.drop_column('users', 'role')
    op.drop_column('users', 'full_name')

    # Drop enum type
    sa.Enum(name='userrole').drop(op.get_bind(), checkfirst=True)
