"""
Scheduled tasks for data updates
Uses APScheduler for background jobs
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
import logging

from app.database import SessionLocal
from app.services.data_ingestion import FundDataIngestionService

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


def run_weekly_data_update():
    """
    Job function for weekly data update
    Runs every Sunday at 2 AM IST
    """
    logger.info("Starting scheduled weekly data update...")
    
    db: Session = SessionLocal()
    try:
        service = FundDataIngestionService(db)
        result = service.run_weekly_update()
        
        logger.info(f"Scheduled update completed: {result}")
        
    except Exception as e:
        logger.error(f"Error in scheduled weekly update: {e}")
    finally:
        db.close()


def start_scheduler():
    """
    Initialize and start the scheduler
    Called during app startup
    """
    logger.info("Starting scheduler...")
    
    # Weekly update: Every Sunday at 2:00 AM IST
    scheduler.add_job(
        run_weekly_data_update,
        trigger=CronTrigger(
            day_of_week='sun',
            hour=2,
            minute=0,
            timezone='Asia/Kolkata'
        ),
        id='weekly_data_update',
        name='Weekly Fund Data Update',
        replace_existing=True
    )
    
    logger.info("Scheduled jobs:")
    for job in scheduler.get_jobs():
        logger.info(f"  - {job.name} (ID: {job.id}), Next run: {job.next_run_time}")
    
    scheduler.start()


def shutdown_scheduler():
    """
    Shutdown the scheduler
    Called during app shutdown
    """
    logger.info("Shutting down scheduler...")
    scheduler.shutdown()
