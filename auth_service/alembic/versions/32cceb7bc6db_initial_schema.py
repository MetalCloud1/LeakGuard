"""initial schema

Revision ID: 32cceb7bc6db
Revises: 
Create Date: 2025-08-03 23:23:47.473871

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '32cceb7bc6db'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
def upgrade():
    op.create_table(
        'users',
        sa.Column('username', sa.String(), primary_key=True),
        sa.Column('email', sa.String(), unique=True),
        sa.Column('full_name', sa.String()),
        sa.Column('hashed_password', sa.String()),
        sa.Column('verification_token', sa.String(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false')
    )

def downgrade():
    op.drop_table('users')
