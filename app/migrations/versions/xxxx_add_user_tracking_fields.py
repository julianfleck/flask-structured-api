"""Add user tracking fields

Revision ID: 0001
Revises: 0000
Create Date: 2024-11-12 23:45:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


def upgrade():
    op.add_column('user', sa.Column('created_at', sa.DateTime(),
                  nullable=False, server_default=sa.text('now()')))
    op.add_column('user', sa.Column('updated_at', sa.DateTime(),
                  nullable=False, server_default=sa.text('now()')))
    op.add_column('user', sa.Column(
        'last_login_at', sa.DateTime(), nullable=True))
    op.add_column('user', sa.Column('login_count', sa.Integer(),
                  nullable=False, server_default='0'))
    op.add_column('user', sa.Column('preferences', JSONB(),
                  nullable=False, server_default='{}'))
    op.add_column('user', sa.Column('permissions', JSONB(),
                  nullable=False, server_default='[]'))


def downgrade():
    op.drop_column('user', 'permissions')
    op.drop_column('user', 'preferences')
    op.drop_column('user', 'login_count')
    op.drop_column('user', 'last_login_at')
    op.drop_column('user', 'updated_at')
    op.drop_column('user', 'created_at')
