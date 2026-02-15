"""Add fund metrics columns to fund_master table

Revision ID: 009_add_fund_metrics
Revises: 008_asset_class
Create Date: 2026-02-15

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '009_add_fund_metrics'
down_revision = '008_asset_class'
branch_labels = None
depends_on = None


# New columns to add to fund_master
NEW_COLUMNS = [
    # Risk/Return metrics (computed from NAV history)
    ('sharpe_ratio', sa.Float, {}),
    ('sortino_ratio', sa.Float, {}),
    ('beta', sa.Float, {}),
    ('alpha', sa.Float, {}),
    ('std_dev', sa.Float, {}),
    ('max_drawdown', sa.Float, {}),
    ('r_squared', sa.Float, {}),
    ('treynor_ratio', sa.Float, {}),
    ('info_ratio', sa.Float, {}),
    ('up_capture', sa.Float, {}),
    ('down_capture', sa.Float, {}),
    ('tracking_error', sa.Float, {}),
    # Portfolio composition
    ('num_stocks', sa.Integer, {}),
    ('top5_weight', sa.Float, {}),
    ('top10_weight', sa.Float, {}),
    # MoneyControl code
    ('mc_code', sa.String(20), {}),
    # Metrics update timestamp
    ('metrics_updated_at', sa.DateTime, {}),
]


def upgrade() -> None:
    """Add risk/return metric columns to fund_master table"""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    
    # Check if fund_master table exists
    tables = inspector.get_table_names()
    if 'fund_master' not in tables:
        print("  fund_master table does not exist yet, skipping migration")
        return
    
    existing_columns = [col['name'] for col in inspector.get_columns('fund_master')]
    
    added = 0
    for col_name, col_type, kwargs in NEW_COLUMNS:
        if col_name not in existing_columns:
            op.add_column('fund_master', sa.Column(col_name, col_type, nullable=True, **kwargs))
            added += 1
    
    print(f"  Added {added} new columns to fund_master")
    
    # Add index on mc_code for cross-referencing
    indexes = [idx['name'] for idx in inspector.get_indexes('fund_master')]
    if 'idx_fund_mc_code' not in indexes and 'mc_code' not in existing_columns:
        op.create_index('idx_fund_mc_code', 'fund_master', ['mc_code'], unique=False)
        print("  Created index on mc_code")


def downgrade() -> None:
    """Remove fund metrics columns from fund_master table"""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    
    tables = inspector.get_table_names()
    if 'fund_master' not in tables:
        return
    
    existing_columns = [col['name'] for col in inspector.get_columns('fund_master')]
    
    # Drop index first
    indexes = [idx['name'] for idx in inspector.get_indexes('fund_master')]
    if 'idx_fund_mc_code' in indexes:
        op.drop_index('idx_fund_mc_code', table_name='fund_master')
    
    # Drop columns
    for col_name, _, _ in reversed(NEW_COLUMNS):
        if col_name in existing_columns:
            op.drop_column('fund_master', col_name)
