"""Add asset_class column to holdings table and backfill

Revision ID: 008_asset_class
Revises: 007_add_broker
Create Date: 2026-02-14

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect


# revision identifiers, used by Alembic.
revision = '008_asset_class'
down_revision = '007_add_broker'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add asset_class column to holdings table"""
    # Check if column already exists (idempotent)
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = [col['name'] for col in inspector.get_columns('holdings')]
    
    if 'asset_class' not in columns:
        # Add asset_class column with default value 'Equity'
        op.add_column('holdings', sa.Column('asset_class', sa.String(length=20), nullable=True, server_default='Equity'))
        print("✓ Added asset_class column")
    else:
        print("✓ asset_class column already exists, skipping")
    
    # Create index if it doesn't exist
    indexes = [idx['name'] for idx in inspector.get_indexes('holdings')]
    if 'idx_holding_asset_class' not in indexes:
        op.create_index('idx_holding_asset_class', 'holdings', ['asset_class', 'user_id'], unique=False)
        print("✓ Created index on asset_class")
    else:
        print("✓ Index already exists, skipping")
    
    # Backfill existing holdings with proper asset classification
    backfill_asset_classes()


def downgrade() -> None:
    """Remove asset_class column from holdings table"""
    # Drop index first
    op.drop_index('idx_holding_asset_class', table_name='holdings')
    
    # Drop asset_class column
    op.drop_column('holdings', 'asset_class')


def backfill_asset_classes():
    """Backfill asset_class for existing holdings using classification logic"""
    
    # Get database connection
    bind = op.get_bind()
    session = Session(bind=bind)
    
    try:
        # Get all holdings that need classification
        result = session.execute(text("""
            SELECT id, category, fund_name 
            FROM holdings 
            WHERE asset_class IS NULL OR asset_class = 'Equity'
        """))
        
        holdings_to_update = []
        
        for row in result:
            holding_id, category, fund_name = row
            asset_class = classify_asset_class(category, fund_name)
            holdings_to_update.append({'id': holding_id, 'asset_class': asset_class})
        
        # Batch update
        if holdings_to_update:
            for holding in holdings_to_update:
                session.execute(
                    text("UPDATE holdings SET asset_class = :asset_class WHERE id = :id"),
                    {'id': holding['id'], 'asset_class': holding['asset_class']}
                )
            
            session.commit()
            print(f"✓ Backfilled asset_class for {len(holdings_to_update)} holdings")
        else:
            print("✓ No holdings to backfill")
            
    except Exception as e:
        session.rollback()
        print(f"⚠️  Backfill failed: {e}")
        # Don't fail the migration if backfill fails
    finally:
        session.close()


def classify_asset_class(category: str, fund_name: str) -> str:
    """
    Simplified classification logic for migration.
    Matches the logic in AssetClassifier service.
    """
    if not category:
        category = ''
    if not fund_name:
        fund_name = ''
    
    category = category.strip()
    fund_name_lower = fund_name.strip().lower()
    
    # Debt categories
    debt_categories = {
        'Liquid', 'Ultra Short Duration', 'Short Duration', 'Low Duration',
        'Money Market', 'Corporate Bond', 'Banking & PSU', 'Gilt',
        'Dynamic Bond', 'Credit Risk', 'Floater', 'Medium Duration',
        'Medium to Long Duration', 'Long Duration', 'Debt', 'Fixed Income'
    }
    
    # Hybrid categories
    hybrid_categories = {
        'Hybrid', 'Balanced', 'Conservative Hybrid', 'Aggressive Hybrid',
        'Dynamic Asset Allocation', 'Multi Asset Allocation',
        'Arbitrage', 'Equity Savings', 'Balanced Advantage'
    }
    
    # Check for commodity (most specific)
    commodity_keywords = ['gold', 'silver', 'commodity', 'metal', 'precious', 'bullion']
    if any(keyword in fund_name_lower for keyword in commodity_keywords):
        return 'Commodity'
    
    # Check category
    if category in debt_categories:
        return 'Debt'
    
    if category in hybrid_categories:
        return 'Hybrid'
    
    # Check fund name for keywords
    if any(keyword in fund_name_lower for keyword in ['liquid', 'debt', 'bond', 'gilt', 'duration', 'credit']):
        return 'Debt'
    
    if any(keyword in fund_name_lower for keyword in ['hybrid', 'balanced', 'arbitrage', 'allocation']):
        return 'Hybrid'
    
    # Default to Equity (most common)
    return 'Equity'
