"""
Feedback API endpoints
Collect user feedback on tool pages and serve to admin panel
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from pathlib import Path
import json
import logging
import os

router = APIRouter(prefix="/api/feedback", tags=["Feedback"])
logger = logging.getLogger(__name__)

FEEDBACK_FILE = Path(__file__).parent.parent.parent / "data" / "feedback.json"

# Admin auth
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "admin-secret-key-change-in-production")


class FeedbackSubmission(BaseModel):
    page: str = Field(..., description="Page name, e.g. 'overlap-analysis'")
    rating: str = Field(..., description="'like' or 'dislike'")
    comment: Optional[str] = Field(None, max_length=1000)
    suggestion: Optional[str] = Field(None, max_length=1000)


def _load_feedback() -> List[dict]:
    """Load feedback from JSON file"""
    if FEEDBACK_FILE.exists():
        try:
            return json.loads(FEEDBACK_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def _save_feedback(entries: List[dict]):
    """Save feedback to JSON file"""
    FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)
    FEEDBACK_FILE.write_text(json.dumps(entries, indent=2, default=str), encoding="utf-8")


@router.post("/submit")
async def submit_feedback(feedback: FeedbackSubmission):
    """Submit user feedback for a page"""
    try:
        entries = _load_feedback()
        entry = {
            "id": len(entries) + 1,
            "page": feedback.page,
            "rating": feedback.rating,
            "comment": feedback.comment or "",
            "suggestion": feedback.suggestion or "",
            "created_at": datetime.utcnow().isoformat(),
        }
        entries.append(entry)
        _save_feedback(entries)
        logger.info(f"Feedback received: {feedback.rating} on {feedback.page}")
        return {"status": "ok", "message": "Thank you for your feedback!"}
    except Exception as e:
        logger.error(f"Failed to save feedback: {e}")
        raise HTTPException(status_code=500, detail="Failed to save feedback")


@router.get("/list")
async def list_feedback(
    api_key: str = None,
    page: Optional[str] = None,
):
    """Get all feedback (admin only)"""
    key = api_key
    if not key or key != ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    entries = _load_feedback()
    if page:
        entries = [e for e in entries if e.get("page") == page]
    
    # Summary stats
    likes = sum(1 for e in entries if e.get("rating") == "like")
    dislikes = sum(1 for e in entries if e.get("rating") == "dislike")

    return {
        "total": len(entries),
        "likes": likes,
        "dislikes": dislikes,
        "entries": sorted(entries, key=lambda x: x.get("created_at", ""), reverse=True),
    }
