"""
Blog Routes - Public blog endpoints for reading posts and managing content
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime
import logging

from app.database import get_db
from app.models.models import User
from app.models.blog import BlogPost, BlogCategory, BlogTag
from app.services.blog_service import BlogService
from app.utils.auth import get_current_user

# Setup logger
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/posts")
async def list_posts(
    category: Optional[str] = None,
    tag: Optional[str] = None,
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get list of published blog posts with optional filtering
    
    Query params:
    - category: Filter by category slug
    - tag: Filter by tag slug
    - limit: Number of posts per page (default: 10, max: 50)
    - offset: Pagination offset (default: 0)
    """
    logger.info(f"Fetching blog posts (category={category}, tag={tag}, limit={limit}, offset={offset})")
    
    # Build query
    query = db.query(BlogPost).filter(BlogPost.is_published == True)
    
    if category:
        query = query.join(BlogCategory).filter(BlogCategory.slug == category)
    
    if tag:
        query = query.join(BlogPost.tags).filter(BlogTag.slug == tag)
    
    # Get total count for pagination
    total = query.count()
    
    # Get posts with ordering
    posts = query.order_by(
        BlogPost.published_at.desc()
    ).offset(offset).limit(limit).all()
    
    # Format response
    result = {
        "posts": [
            {
                "id": post.id,
                "slug": post.slug,
                "title": post.title,
                "description": post.description,
                "category": {
                    "slug": post.category.slug,
                    "name": post.category.name
                } if post.category else None,
                "tags": [
                    {"slug": tag.slug, "name": tag.name}
                    for tag in post.tags
                ],
                "featured_image": post.featured_image,
                "published_at": post.published_at.isoformat() if post.published_at else None,
                "reading_time_minutes": post.reading_time_minutes,
                "view_count": post.view_count or 0,
            }
            for post in posts
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }
    
    return result


@router.get("/posts/{slug}")
async def get_post(
    slug: str,
    db: Session = Depends(get_db)
):
    """Get a single blog post by slug"""
    logger.info(f"Fetching blog post: {slug}")
    
    post = db.query(BlogPost).filter(
        and_(
            BlogPost.slug == slug,
            BlogPost.is_published == True
        )
    ).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    
    try:
        # Parse markdown file
        parsed = BlogService.parse_markdown_file(post.content_file)
        
        # Get related posts
        related_posts = BlogService.get_related_posts(db, post, limit=3)
        
        # Format response
        result = {
            "id": post.id,
            "slug": post.slug,
            "title": post.title,
            "description": post.description,
            "content": parsed['html_content'],
            "toc": parsed['toc'],
            "category": {
                "slug": post.category.slug,
                "name": post.category.name,
                "description": post.category.description
            } if post.category else None,
            "tags": [
                {"slug": tag.slug, "name": tag.name}
                for tag in post.tags
            ],
            "author": {
                "id": post.author.id,
                "name": post.author.full_name or post.author.email.split('@')[0],
            } if post.author else None,
            "featured_image": post.featured_image,
            "og_image": post.og_image or post.featured_image,
            "published_at": post.published_at.isoformat() if post.published_at else None,
            "updated_at": post.updated_at.isoformat() if post.updated_at else None,
            "reading_time_minutes": post.reading_time_minutes,
            "view_count": post.view_count or 0,
            "related_posts": [
                {
                    "slug": rp.slug,
                    "title": rp.title,
                    "description": rp.description,
                    "featured_image": rp.featured_image,
                    "published_at": rp.published_at.isoformat() if rp.published_at else None,
                }
                for rp in related_posts
            ]
        }
        
        return result
        
    except FileNotFoundError:
        logger.error(f"Blog post file not found: {post.content_file}")
        raise HTTPException(status_code=404, detail="Blog post content not found")
    except Exception as e:
        logger.error(f"Error loading blog post {slug}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error loading blog post")


@router.post("/posts/{slug}/view")
async def increment_view(
    slug: str,
    db: Session = Depends(get_db)
):
    """Increment view count for a blog post"""
    post = db.query(BlogPost).filter(
        and_(
            BlogPost.slug == slug,
            BlogPost.is_published == True
        )
    ).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    
    BlogService.increment_view_count(db, post)
    
    return {"success": True, "view_count": post.view_count}


@router.get("/categories")
async def list_categories(db: Session = Depends(get_db)):
    """Get all blog categories with post counts"""
    logger.info("Fetching blog categories")
    
    categories = db.query(BlogCategory).all()
    
    result = [
        {
            "slug": cat.slug,
            "name": cat.name,
            "description": cat.description,
            "post_count": len([p for p in cat.posts if p.is_published])
        }
        for cat in categories
    ]
    
    return {"categories": result}


@router.get("/tags")
async def list_tags(db: Session = Depends(get_db)):
    """Get all blog tags with usage counts"""
    logger.info("Fetching blog tags")
    
    tags = db.query(BlogTag).all()
    
    result = [
        {
            "slug": tag.slug,
            "name": tag.name,
            "post_count": len([p for p in tag.posts if p.is_published])
        }
        for tag in tags
    ]
    
    return {"tags": result}


@router.get("/search")
async def search_posts(
    q: str = Query(..., min_length=2, max_length=100),
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Search blog posts by title, description, and tags
    
    Query params:
    - q: Search query (required, 2-100 characters)
    - limit: Results per page (default: 10, max: 50)
    - offset: Pagination offset (default: 0)
    """
    logger.info(f"Searching blog posts: '{q}'")
    
    posts, total = BlogService.search_posts(db, q, limit, offset)
    
    result = {
        "posts": [
            {
                "id": post.id,
                "slug": post.slug,
                "title": post.title,
                "description": post.description,
                "category": {
                    "slug": post.category.slug,
                    "name": post.category.name
                } if post.category else None,
                "featured_image": post.featured_image,
                "published_at": post.published_at.isoformat() if post.published_at else None,
                "reading_time_minutes": post.reading_time_minutes,
            }
            for post in posts
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
        "query": q
    }
    
    return result


@router.get("/popular")
async def get_popular_posts(
    limit: int = Query(5, ge=1, le=10),
    db: Session = Depends(get_db)
):
    """Get most popular blog posts by view count"""
    logger.info(f"Fetching popular posts (limit={limit})")
    
    posts = BlogService.get_popular_posts(db, limit)
    
    result = {
        "posts": [
            {
                "slug": post.slug,
                "title": post.title,
                "description": post.description,
                "featured_image": post.featured_image,
                "view_count": post.view_count or 0,
            }
            for post in posts
        ]
    }
    
    return result


@router.get("/recent")
async def get_recent_posts(
    limit: int = Query(5, ge=1, le=10),
    db: Session = Depends(get_db)
):
    """Get most recent published blog posts"""
    logger.info(f"Fetching recent posts (limit={limit})")
    
    posts = BlogService.get_recent_posts(db, limit)
    
    result = {
        "posts": [
            {
                "slug": post.slug,
                "title": post.title,
                "description": post.description,
                "featured_image": post.featured_image,
                "published_at": post.published_at.isoformat() if post.published_at else None,
            }
            for post in posts
        ]
    }
    
    return result
