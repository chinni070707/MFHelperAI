"""
Add asset_class column to holdings table and backfill data

Migration: Add asset class classification to holdings
Date: 2026-02-14
"""

import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models.models import Holding
from app.services.asset_classifier import AssetClassifier
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_add_asset_class():
    """Add asset_class column and backfill existing data"""
    
    logger.info("="*60)
    logger.info("MIGRATION: Adding asset_class to holdings table")
    logger.info("="*60)
    
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Step 1: Check if column exists (SQLite compatible)
        logger.info("\n📋 Step 1: Checking if asset_class column exists...")
        
        result = db.execute(text("PRAGMA table_info(holdings)"))
        columns = [row[1] for row in result.fetchall()]
        column_exists = 'asset_class' in columns
        
        if not column_exists:
            # Step 2: Add column
            logger.info("\n➕ Step 2: Adding asset_class column...")
            db.execute(text("""
                ALTER TABLE holdings 
                ADD COLUMN asset_class VARCHAR(20) DEFAULT 'Equity'
            """))
            db.commit()
            logger.info("✓ Column added successfully")
        else:
            logger.info("✓ Column already exists, skipping creation")
        
        # Step 3: Backfill existing data
        logger.info("\n🔄 Step 3: Backfilling asset_class for existing holdings...")
        
        holdings = db.query(Holding).filter(
            (Holding.asset_class == None) | 
            (Holding.asset_class == '') | 
            (Holding.asset_class == 'Equity')
        ).all()
        
        logger.info(f"Found {len(holdings)} holdings to classify")
        
        classified = {'Equity': 0, 'Debt': 0, 'Hybrid': 0, 'Commodity': 0, 'Other': 0}
        
        for holding in holdings:
            asset_class = AssetClassifier.classify(
                category=holding.category,
                fund_name=holding.fund_name,
                fund_type=None  # Not stored in old data
            )
            holding.asset_class = asset_class
            classified[asset_class] += 1
        
        db.commit()
        
        logger.info("\n📊 Classification Results:")
        for asset_class, count in sorted(classified.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"  {AssetClassifier.get_asset_class_icon(asset_class)} {asset_class}: {count} funds")
        
        # Step 4: Create index
        logger.info("\n📇 Step 4: Creating index on asset_class...")
        
        try:
            db.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_holding_asset_class 
                ON holdings(asset_class, user_id)
            """))
            db.commit()
            logger.info("✓ Index created successfully")
        except Exception as e:
            logger.warning(f"Index may already exist: {e}")
        
        # Step 5: Verify
        logger.info("\n✅ Step 5: Verification...")
        
        result = db.execute(text("""
            SELECT asset_class, COUNT(*) as count 
            FROM holdings 
            GROUP BY asset_class 
            ORDER BY count DESC
        """))
        
        logger.info("Current distribution in database:")
        for row in result:
            logger.info(f"  {row[0]}: {row[1]} holdings")
        
        logger.info("\n" + "="*60)
        logger.info("✓ MIGRATION COMPLETED SUCCESSFULLY")
        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"\n❌ Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate_add_asset_class()
