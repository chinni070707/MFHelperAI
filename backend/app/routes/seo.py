"""
SEO Routes - Sitemap, robots.txt, and SEO-related endpoints
"""
from fastapi import APIRouter, Response, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
import logging

from app.database import get_db
from app.models.blog import BlogPost

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/sitemap.xml", include_in_schema=False)
async def generate_sitemap(db: Session = Depends(get_db)):
    """
    Generate dynamic XML sitemap for SEO
    Includes all static pages and published blog posts
    """
    logger.info("Generating sitemap.xml")
    
    # Base URL - update this for production
    base_url = "https://mfhelper.com"  # TODO: Get from settings
    
    # Static pages with their update frequency and priority
    static_pages = [
        {"loc": "/", "changefreq": "weekly", "priority": "1.0"},
        {"loc": "/dashboard.html", "changefreq": "daily", "priority": "0.9"},
        {"loc": "/overlap-analysis.html", "changefreq": "weekly", "priority": "0.8"},
        {"loc": "/goal-planning.html", "changefreq": "weekly", "priority": "0.8"},
        {"loc": "/sip-calculator.html", "changefreq": "weekly", "priority": "0.8"},
        {"loc": "/retirement-calculator.html", "changefreq": "weekly", "priority": "0.7"},
        {"loc": "/how-it-works.html", "changefreq": "monthly", "priority": "0.7"},
        {"loc": "/blog.html", "changefreq": "daily", "priority": "0.9"},
    ]
    
    # Get all published blog posts
    blog_posts = db.query(BlogPost).filter(
        BlogPost.is_published == True
    ).order_by(BlogPost.published_at.desc()).all()
    
    # Build XML sitemap
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    
    # Add static pages
    for page in static_pages:
        xml_lines.extend([
            '  <url>',
            f'    <loc>{base_url}{page["loc"]}</loc>',
            f'    <changefreq>{page["changefreq"]}</changefreq>',
            f'    <priority>{page["priority"]}</priority>',
            '  </url>',
        ])
    
    # Add blog posts
    for post in blog_posts:
        lastmod = post.updated_at or post.published_at or datetime.now()
        xml_lines.extend([
            '  <url>',
            f'    <loc>{base_url}/blog/{post.slug}</loc>',
            f'    <lastmod>{lastmod.strftime("%Y-%m-%d")}</lastmod>',
            '    <changefreq>monthly</changefreq>',
            '    <priority>0.7</priority>',
            '  </url>',
        ])
    
    # Add blog category pages
    categories = set(post.category.slug for post in blog_posts if post.category)
    for cat_slug in categories:
        xml_lines.extend([
            '  <url>',
            f'    <loc>{base_url}/blog/category/{cat_slug}</loc>',
            '    <changefreq>weekly</changefreq>',
            '    <priority>0.6</priority>',
            '  </url>',
        ])
    
    xml_lines.append('</urlset>')
    
    sitemap_xml = '\n'.join(xml_lines)
    
    return Response(
        content=sitemap_xml,
        media_type="application/xml",
        headers={
            "Cache-Control": "public, max-age=3600",  # Cache for 1 hour
        }
    )


@router.get("/robots.txt", include_in_schema=False)
async def robots_txt():
    """
    Generate robots.txt for search engine crawlers
    """
    logger.info("Serving robots.txt")
    
    robots_content = """User-agent: *
Allow: /
Disallow: /api/
Disallow: /uploads/
Disallow: /test-data/

# Sitemap
Sitemap: https://mfhelper.com/sitemap.xml

# Crawl-delay for politeness
Crawl-delay: 1
"""
    
    return Response(
        content=robots_content,
        media_type="text/plain",
        headers={
            "Cache-Control": "public, max-age=86400",  # Cache for 24 hours
        }
    )


@router.get("/schema/article/{slug}", include_in_schema=False)
async def get_article_schema(slug: str, db: Session = Depends(get_db)):
    """
    Generate JSON-LD structured data for a blog post (Article schema)
    This helps search engines understand the content better
    """
    post = db.query(BlogPost).filter(
        BlogPost.slug == slug,
        BlogPost.is_published == True
    ).first()
    
    if not post:
        return Response(content="{}", media_type="application/ld+json")
    
    # Build Article schema
    schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": post.title,
        "description": post.description or "",
        "datePublished": post.published_at.isoformat() if post.published_at else None,
        "dateModified": post.updated_at.isoformat() if post.updated_at else None,
        "author": {
            "@type": "Person",
            "name": post.author.full_name or "MFHelper Team" if post.author else "MFHelper Team"
        },
        "publisher": {
            "@type": "Organization",
            "name": "MFHelper",
            "logo": {
                "@type": "ImageObject",
                "url": "https://mfhelper.com/static/logo.png"
            }
        },
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": f"https://mfhelper.com/blog/{post.slug}"
        }
    }
    
    # Add image if available
    if post.featured_image:
        schema["image"] = post.featured_image
    
    # Add keywords from tags
    if post.tags:
        schema["keywords"] = ", ".join([tag.name for tag in post.tags])
    
    import json
    return Response(
        content=json.dumps(schema, indent=2),
        media_type="application/ld+json"
    )
