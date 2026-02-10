"""
Error logging endpoint
Receives client-side errors and logs them
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import json
import os
import logging

router = APIRouter(prefix="/api", tags=["errors"])
logger = logging.getLogger(__name__)

# Error log file path
LOG_DIR = "logs"
ERROR_LOG_FILE = os.path.join(LOG_DIR, "frontend_errors.log")

# Create logs directory if it doesn't exist
os.makedirs(LOG_DIR, exist_ok=True)

class ErrorLog(BaseModel):
    type: str
    message: str
    timestamp: str
    url: str
    userAgent: str
    source: Optional[str] = None
    line: Optional[int] = None
    column: Optional[int] = None
    error: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

@router.post("/errors")
async def log_error(error_log: ErrorLog):
    """
    Log frontend errors for debugging and monitoring
    
    Args:
        error_log: Error details from frontend
    
    Returns:
        dict: Success response
    """
    try:
        # Create log entry
        log_entry = {
            "timestamp": error_log.timestamp,
            "type": error_log.type,
            "message": error_log.message,
            "url": error_log.url,
            "userAgent": error_log.userAgent,
            "source": error_log.source,
            "line": error_log.line,
            "column": error_log.column,
            "error": error_log.error,
            "context": error_log.context
        }
        
        # Write to log file
        with open(ERROR_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
        
        # Log to application logger
        logger.warning(f"[FRONTEND ERROR] {error_log.type}: {error_log.message}")
        
        # TODO: Send critical errors to monitoring service (Sentry, etc.)
        if error_log.type in ["ERROR", "PROMISE_REJECTION"]:
            # Could send to Sentry, Slack, email, etc.
            pass
        
        return {"status": "logged", "timestamp": datetime.now().isoformat()}
        
    except Exception as e:
        # Don't fail if logging fails
        logger.error(f"Error logging frontend error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to log error")

@router.get("/errors/stats")
async def get_error_stats():
    """
    Get error statistics
    
    Returns:
        dict: Error stats (total count, recent errors, etc.)
    """
    try:
        if not os.path.exists(ERROR_LOG_FILE):
            return {
                "total_errors": 0,
                "recent_errors": []
            }
        
        # Read last 100 errors
        with open(ERROR_LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        recent_errors = []
        for line in lines[-100:]:  # Last 100
            try:
                error = json.loads(line.strip())
                recent_errors.append(error)
            except:
                continue
        
        # Count by type
        error_types = {}
        for error in recent_errors:
            error_type = error.get("type", "UNKNOWN")
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        return {
            "total_errors": len(lines),
            "recent_count": len(recent_errors),
            "error_types": error_types,
            "recent_errors": recent_errors[-10:]  # Last 10
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/errors")
async def clear_errors():
    """
    Clear error log file (for testing)
    
    Returns:
        dict: Success response
    """
    try:
        if os.path.exists(ERROR_LOG_FILE):
            os.remove(ERROR_LOG_FILE)
        
        return {"status": "cleared", "timestamp": datetime.now().isoformat()}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
