"""add_security_columns_for_login_tracking

Revision ID: 002_security
Revises: 001_indexes
Create Date: 2026-02-08

Description:
Adds security-related columns to users table:
- last_login_at: Track when user last logged in
- failed_login_attempts: Count failed login attempts for lockout
- locked_until: Timestamp when account lockout expires

Security Features:
- Account lockout after 5 failed attempts
- 15-minute lockout duration
- Last login tracking for security audits
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_security'
down_revision = '001_indexes'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add security columns to users table"""
    
    # Add last_login_at column
    op.add_column(
        'users',
        sa.Column('last_login_at', sa.DateTime(), nullable=True)
    )
    
    # Add failed_login_attempts column
    op.add_column(
        'users',
        sa.Column('failed_login_attempts', sa.Integer(), server_default='0', nullable=True)
    )
    
    # Add locked_until column
    op.add_column(
        'users',
        sa.Column('locked_until', sa.DateTime(), nullable=True)
    )


def downgrade() -> None:
    """Remove security columns from users table"""
    
    op.drop_column('users', 'last_login_at')
    op.drop_column('users', 'failed_login_attempts')
    op.drop_column('users', 'locked_until')
