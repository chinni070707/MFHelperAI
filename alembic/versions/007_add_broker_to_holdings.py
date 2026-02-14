"""Add broker column to holdings table

Revision ID: 007_add_broker
Revises: 006_blog_models
Create Date: 2026-02-14

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '007_add_broker'
down_revision = '006_blog_models'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add broker/distributor/advisor column to holdings table"""
    # Add broker column to holdings table
    op.add_column('holdings', sa.Column('broker', sa.String(length=255), nullable=True))
    
    # Create index for broker filtering
    op.create_index('idx_holding_broker', 'holdings', ['broker'], unique=False)


def downgrade() -> None:
    """Remove broker column from holdings table"""
    # Drop index first
    op.drop_index('idx_holding_broker', table_name='holdings')
    
    # Drop broker column
    op.drop_column('holdings', 'broker')
