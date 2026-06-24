"""add shared account tables

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2026-05-29
"""
from alembic import op
import sqlalchemy as sa

revision = 'a1b2c3d4e5f6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'shared_account_members',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('account_id', sa.Integer(), sa.ForeignKey('accounts.id'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('joined_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_shared_members_account', 'shared_account_members', ['account_id'])
    op.create_index('ix_shared_members_user', 'shared_account_members', ['user_id'])

    op.create_table(
        'shared_account_invites',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('account_id', sa.Integer(), sa.ForeignKey('accounts.id'), nullable=False),
        sa.Column('invite_code', sa.String(32), unique=True, nullable=False),
        sa.Column('created_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
    )


def downgrade():
    op.drop_table('shared_account_invites')
    op.drop_index('ix_shared_members_user', 'shared_account_members')
    op.drop_index('ix_shared_members_account', 'shared_account_members')
    op.drop_table('shared_account_members')
