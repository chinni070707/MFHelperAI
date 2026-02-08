"""add_email_verification_columns

Revision ID: 003_email_verification
Revises: 002_security
Create Date: 2026-02-08

Description:
Adds email verification columns to users table:
- verification_token: Token sent via email
- verification_token_expires: When the token expires
- verified_at: Timestamp when email was verified

Email Verification Flow:
1. User registers -> verification_token generated
2. Email sent with verification link
3. User clicks link -> /api/auth/verify-email?token=xxx
4. Token validated -> is_verified=True, verified_at set
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003_email_verification'
down_revision = '002_security'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add email verification columns to users table"""
    
    # Add verification_token column
    op.add_column(
        'users',
        sa.Column('verification_token', sa.String(255), nullable=True)
    )
    
    # Add verification_token_expires column
    op.add_column(
        'users',
        sa.Column('verification_token_expires', sa.DateTime(), nullable=True)
    )
    
    # Add verified_at column
    op.add_column(
        'users',
        sa.Column('verified_at', sa.DateTime(), nullable=True)
    )
    
    # Add index on verification_token for faster lookups
    op.create_index(
        'idx_user_verification_token',
        'users',
        ['verification_token'],
        unique=False
    )


def downgrade() -> None:
    """Remove email verification columns from users table"""
    
    op.drop_index('idx_user_verification_token', table_name='users')
    op.drop_column('users', 'verification_token')
    op.drop_column('users', 'verification_token_expires')
    op.drop_column('users', 'verified_at')
