"""add sync fields (is_deleted/version) and align schema with client

Revision ID: c9d1e2f3a4b5
Revises: b3c4d5e6f7a8
Create Date: 2026-06-20 12:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = 'c9d1e2f3a4b5'
down_revision = 'b3c4d5e6f7a8'
branch_labels = None
depends_on = None


def upgrade():
    # --- accounts ---
    op.add_column('accounts', sa.Column('is_excluded_from_total', sa.Integer(), server_default='0'))
    op.add_column('accounts', sa.Column('is_deleted', sa.Integer(), server_default='0'))
    op.add_column('accounts', sa.Column('version', sa.Integer(), server_default='1'))
    op.alter_column('accounts', 'currency', type_=sa.String(8))

    # --- categories ---
    op.add_column('categories', sa.Column('icon_name', sa.String(255), server_default=''))
    op.add_column('categories', sa.Column('color_hex', sa.String(16), server_default='#FF6200EE'))
    op.add_column('categories', sa.Column('is_deleted', sa.Integer(), server_default='0'))
    op.add_column('categories', sa.Column('version', sa.Integer(), server_default='1'))
    # переносим старые данные image_url -> icon_name, если там что-то было
    op.execute("UPDATE categories SET icon_name = image_url WHERE image_url IS NOT NULL")
    op.drop_column('categories', 'image_url')

    # --- patterns (шаблоны) ---
    op.add_column('patterns', sa.Column('type', sa.String(255), nullable=True))
    op.add_column('patterns', sa.Column('account_id', sa.Integer(), sa.ForeignKey('accounts.id'), nullable=True))
    op.add_column('patterns', sa.Column('note', sa.String(255), server_default=''))
    op.add_column('patterns', sa.Column('is_deleted', sa.Integer(), server_default='0'))
    op.add_column('patterns', sa.Column('version', sa.Integer(), server_default='1'))
    op.execute("UPDATE patterns SET note = image_url WHERE image_url IS NOT NULL")
    op.drop_column('patterns', 'image_url')

    # --- fixed_expenses (напоминания) ---
    op.add_column('fixed_expenses', sa.Column('date', sa.DateTime(), nullable=True))
    op.execute("UPDATE fixed_expenses SET date = period")
    op.drop_column('fixed_expenses', 'period')
    op.add_column('fixed_expenses', sa.Column('repeat_type', sa.String(32), server_default='NONE'))
    op.add_column('fixed_expenses', sa.Column('repeat_every_n_days', sa.Integer(), nullable=True))
    op.add_column('fixed_expenses', sa.Column('is_paid', sa.Boolean(), server_default=sa.false()))
    op.add_column('fixed_expenses', sa.Column('is_push_enabled', sa.Boolean(), server_default=sa.true()))
    op.add_column('fixed_expenses', sa.Column('is_deleted', sa.Integer(), server_default='0'))
    op.add_column('fixed_expenses', sa.Column('version', sa.Integer(), server_default='1'))

    # --- limits ---
    op.add_column('limits', sa.Column('period_str', sa.String(16), nullable=True))
    op.execute("UPDATE limits SET period_str = 'MONTH' WHERE period IS NOT NULL")
    op.drop_column('limits', 'period')
    op.alter_column('limits', 'period_str', new_column_name='period')
    op.add_column('limits', sa.Column('is_notification_enabled', sa.Integer(), server_default='1'))
    op.add_column('limits', sa.Column('is_deleted', sa.Integer(), server_default='0'))
    op.add_column('limits', sa.Column('version', sa.Integer(), server_default='1'))


def downgrade():
    op.drop_column('limits', 'version')
    op.drop_column('limits', 'is_deleted')
    op.drop_column('limits', 'is_notification_enabled')
    op.alter_column('limits', 'period', new_column_name='period_str')
    op.add_column('limits', sa.Column('period', sa.DateTime(), nullable=True))
    op.drop_column('limits', 'period_str')

    op.drop_column('fixed_expenses', 'version')
    op.drop_column('fixed_expenses', 'is_deleted')
    op.drop_column('fixed_expenses', 'is_push_enabled')
    op.drop_column('fixed_expenses', 'is_paid')
    op.drop_column('fixed_expenses', 'repeat_every_n_days')
    op.drop_column('fixed_expenses', 'repeat_type')
    op.add_column('fixed_expenses', sa.Column('period', sa.DateTime(), nullable=True))
    op.execute("UPDATE fixed_expenses SET period = date")
    op.drop_column('fixed_expenses', 'date')

    op.drop_column('patterns', 'version')
    op.drop_column('patterns', 'is_deleted')
    op.add_column('patterns', sa.Column('image_url', sa.Text(), nullable=True))
    op.drop_column('patterns', 'note')
    op.drop_column('patterns', 'account_id')
    op.drop_column('patterns', 'type')

    op.drop_column('categories', 'version')
    op.drop_column('categories', 'is_deleted')
    op.add_column('categories', sa.Column('image_url', sa.Text(), nullable=True))
    op.drop_column('categories', 'color_hex')
    op.drop_column('categories', 'icon_name')

    op.drop_column('accounts', 'version')
    op.drop_column('accounts', 'is_deleted')
    op.drop_column('accounts', 'is_excluded_from_total')
