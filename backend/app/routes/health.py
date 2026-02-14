"""
Health Check and Monitoring Endpoints
Provides system health status, readiness checks, and metrics
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
import os
import sys
from typing import Dict
import logging

# Lazy import psutil — it's a C extension that may not be available
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

from app.database import get_db
from pathlib import Path
import json

router = APIRouter(prefix="/api/health", tags=["Health & Monitoring"])
logger = logging.getLogger(__name__)


@router.get("/")
@router.get("/liveness")
async def liveness_check() -> Dict:
    """
    Liveness probe - checks if the application is running
    Used by container orchestrators (Kubernetes, Docker Swarm)
    
    Returns:
        200 OK if app is alive
    """
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "MFHelper API"
    }


@router.get("/readiness")
async def readiness_check(db: Session = Depends(get_db)) -> Dict:
    """
    Readiness probe - checks if the application is ready to serve traffic
    Verifies database connectivity and critical dependencies
    
    Returns:
        200 OK if ready to serve requests
        503 Service Unavailable if not ready
    """
    checks = {
        "database": False,
        "disk_space": False,
        "memory": False
    }
    
    # Check database connection
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
    
    # Check disk space (at least 100MB free)
    try:
        if HAS_PSUTIL:
            disk = psutil.disk_usage('/')
            checks["disk_space"] = disk.free > 100 * 1024 * 1024  # 100MB
        else:
            checks["disk_space"] = True  # Skip if psutil unavailable
    except Exception as e:
        logger.error(f"Disk space check failed: {e}")
    
    # Check memory (at least 100MB available)
    try:
        if HAS_PSUTIL:
            memory = psutil.virtual_memory()
            checks["memory"] = memory.available > 100 * 1024 * 1024  # 100MB
        else:
            checks["memory"] = True  # Skip if psutil unavailable
    except Exception as e:
        logger.error(f"Memory check failed: {e}")
    
    is_ready = all(checks.values())
    
    return {
        "status": "ready" if is_ready else "not_ready",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": checks,
        "ready": is_ready
    }


@router.get("/metrics")
async def get_metrics(db: Session = Depends(get_db)) -> Dict:
    """
    Get detailed system and application metrics
    
    Returns:
        Comprehensive metrics about system health and performance
    """
    try:
        if not HAS_PSUTIL:
            return {
                "status": "ok",
                "timestamp": datetime.utcnow().isoformat(),
                "message": "Detailed metrics unavailable (psutil not installed)"
            }
        
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memory metrics
        memory = psutil.virtual_memory()
        memory_metrics = {
            "total_mb": round(memory.total / (1024 * 1024), 2),
            "available_mb": round(memory.available / (1024 * 1024), 2),
            "used_mb": round(memory.used / (1024 * 1024), 2),
            "percent": memory.percent
        }
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        disk_metrics = {
            "total_gb": round(disk.total / (1024 ** 3), 2),
            "used_gb": round(disk.used / (1024 ** 3), 2),
            "free_gb": round(disk.free / (1024 ** 3), 2),
            "percent": disk.percent
        }
        
        # Process metrics
        process = psutil.Process(os.getpid())
        process_memory = process.memory_info()
        process_metrics = {
            "pid": process.pid,
            "memory_rss_mb": round(process_memory.rss / (1024 * 1024), 2),
            "memory_vms_mb": round(process_memory.vms / (1024 * 1024), 2),
            "cpu_percent": process.cpu_percent(interval=0.1),
            "num_threads": process.num_threads(),
            "open_files": len(process.open_files()) if hasattr(process, 'open_files') else 0,
            "create_time": datetime.fromtimestamp(process.create_time()).isoformat()
        }
        
        # Database metrics
        try:
            from app.models.models import User, Portfolio, Holding
            db_metrics = {
                "users_count": db.query(User).count(),
                "portfolios_count": db.query(Portfolio).count(),
                "holdings_count": db.query(Holding).count(),
                "connected": True
            }
        except Exception as e:
            logger.error(f"Failed to fetch database metrics: {e}")
            db_metrics = {"connected": False, "error": str(e)}
        
        # Python runtime info
        runtime_info = {
            "python_version": sys.version,
            "platform": sys.platform,
            "executable": sys.executable
        }
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "cpu": {
                "percent": cpu_percent,
                "count": cpu_count
            },
            "memory": memory_metrics,
            "disk": disk_metrics,
            "process": process_metrics,
            "database": db_metrics,
            "runtime": runtime_info,
            "uptime_seconds": round((datetime.utcnow().timestamp() - process.create_time()), 2)
        }
        
    except Exception as e:
        logger.error(f"Error collecting metrics: {e}")
        return {
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/status")
async def get_status(db: Session = Depends(get_db)) -> Dict:
    """
    Get comprehensive system status
    Combines health checks with basic metrics
    """
    # Run readiness checks
    readiness = await readiness_check(db)
    
    # Get basic metrics
    cpu_percent = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Check database
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "service": "MFHelper API",
        "status": "healthy" if readiness["ready"] else "unhealthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",  # Update with actual version
        "environment": os.getenv("ENVIRONMENT", "development"),
        "ready": readiness["ready"],
        "checks": readiness["checks"],
        "metrics": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "disk_percent": disk.percent,
            "database": db_status
        }
    }


@router.get("/ping")
async def ping() -> Dict:
    """
    Simple ping endpoint for uptime monitoring
    Used by external monitoring services
    """
    return {
        "ping": "pong",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/funds-data")
async def check_funds_data() -> Dict:
    """
    Health check for fund holdings JSON data
    Validates data quality, file size, and completeness
    
    Returns:
        Status of fund holdings including count, quality metrics
    """
    data_file = Path(__file__).parent.parent.parent / 'data' / 'fund_holdings.json'
    
    try:
        # Check file exists
        if not data_file.exists():
            return {
                "status": "error",
                "timestamp": datetime.utcnow().isoformat(),
                "message": "Fund holdings file not found"
            }
        
        # Check file size
        file_size_mb = data_file.stat().st_size / (1024 * 1024)
        
        # Load and validate structure
        with open(data_file, 'r', encoding='utf-8', errors='replace') as f:
            data = json.load(f)
        
        if 'funds' not in data:
            return {
                "status": "error",
                "timestamp": datetime.utcnow().isoformat(),
                "message": "Invalid fund holdings structure"
            }
        
        funds = data['funds']
        fund_count = len(funds)
        
        # Calculate statistics
        total_holdings = sum(len(f.get('holdings', [])) for f in funds.values())
        avg_holdings = total_holdings / fund_count if fund_count > 0 else 0
        
        # Check data quality (≥80% weight)
        complete_funds = 0
        for fund in funds.values():
            total_weight = sum(h.get('weight', 0) for h in fund.get('holdings', []))
            if total_weight >= 80:
                complete_funds += 1
        
        quality_percent = (complete_funds / fund_count * 100) if fund_count > 0 else 0
        
        # Get last update from metadata
        last_updated = data.get('last_updated', 'Unknown')
        
        # Overall status
        status = "healthy"
        warnings = []
        
        if fund_count < 50:
            warnings.append(f"Low fund count: {fund_count}")
            status = "degraded"
        
        if quality_percent < 90:
            warnings.append(f"Data quality below 90%: {quality_percent:.1f}%")
            status = "degraded"
        
        if file_size_mb > 20:
            warnings.append(f"Large file size: {file_size_mb:.1f}MB (consider database migration)")
        
        return {
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "file_size_mb": round(file_size_mb, 2),
                "fund_count": fund_count,
                "complete_funds": complete_funds,
                "quality_percent": round(quality_percent, 1),
                "avg_holdings_per_fund": round(avg_holdings, 1),
                "last_updated": last_updated,
                "source": data.get('source', 'Unknown'),
                "version": data.get('version', 'Unknown')
            },
            "warnings": warnings if warnings else None,
            "recommendation": "Consider database migration if file exceeds 20MB or updates become frequent"
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in fund holdings: {e}")
        return {
            "status": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Fund holdings file is corrupted or invalid JSON"
        }
    except Exception as e:
        logger.error(f"Error checking fund holdings: {e}")
        return {
            "status": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "message": f"Error checking fund holdings: {str(e)}"
        }

