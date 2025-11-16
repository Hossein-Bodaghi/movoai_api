"""Add auth tables

Revision ID: 001_add_auth_tables
Revises: 
Create Date: 2025-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_add_auth_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create user_auth_methods table
    op.create_table(
        'user_auth_methods',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('auth_provider', sa.String(length=20), nullable=False),
        sa.Column('auth_identifier', sa.String(length=255), nullable=False),
        sa.Column('auth_data', sa.JSON(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_primary', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('auth_provider', 'auth_identifier', name='uix_provider_identifier')
    )
    op.create_index(op.f('ix_user_auth_methods_user_id'), 'user_auth_methods', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_auth_methods_auth_identifier'), 'user_auth_methods', ['auth_identifier'], unique=False)
    
    # Create verification_codes table
    op.create_table(
        'verification_codes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('identifier', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=6), nullable=False),
        sa.Column('code_type', sa.String(length=10), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_verification_codes_identifier'), 'verification_codes', ['identifier'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_verification_codes_identifier'), table_name='verification_codes')
    op.drop_table('verification_codes')
    op.drop_index(op.f('ix_user_auth_methods_auth_identifier'), table_name='user_auth_methods')
    op.drop_index(op.f('ix_user_auth_methods_user_id'), table_name='user_auth_methods')
    op.drop_table('user_auth_methods')
