"""
Seed Blog Posts - Load markdown blog posts into database
Run this script to populate the blog with initial content
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from app.database import SessionLocal
from app.models.blog import BlogPost, BlogCategory, BlogTag
from app.models.models import User
from app.services.blog_service import BlogService
from datetime import datetime
import frontmatter


def seed_categories(db):
    """Create blog categories"""
    categories = [
        {"slug": "guides", "name": "Guides", "description": "Step-by-step guides and tutorials"},
        {"slug": "analysis", "name": "Analysis", "description": "Portfolio analysis and optimization"},
        {"slug": "investments", "name": "Investment Strategy", "description": "Investment strategies and tips"},
        {"slug": "features", "name": "Features", "description": "MFHelper features and how-to"},
        {"slug": "news", "name": "News", "description": "Market news and updates"},
    ]
    
    created = []
    for cat_data in categories:
        cat = BlogService.get_or_create_category(
            db, 
            cat_data["slug"], 
            cat_data["name"], 
            cat_data.get("description")
        )
        created.append(cat)
        print(f"✓ Category: {cat.name}")
    
    return created


def seed_tags(db):
    """Create blog tags"""
    tags = [
        {"slug": "cas-upload", "name": "CAS Upload"},
        {"slug": "getting-started", "name": "Getting Started"},
        {"slug": "portfolio", "name": "Portfolio"},
        {"slug": "portfolio-overlap", "name": "Portfolio Overlap"},
        {"slug": "diversification", "name": "Diversification"},
        {"slug": "optimization", "name": "Optimization"},
        {"slug": "sip", "name": "SIP"},
        {"slug": "investment-strategy", "name": "Investment Strategy"},
        {"slug": "wealth-building", "name": "Wealth Building"},
    ]
    
    created = []
    for tag_data in tags:
        tag = BlogService.get_or_create_tag(db, tag_data["slug"], tag_data["name"])
        created.append(tag)
        print(f"✓ Tag: {tag.name}")
    
    return created


def seed_blog_posts(db):
    """Load markdown blog posts and create database entries"""
    
    # Get or create default author (admin user)
    author = db.query(User).first()
    if not author:
        print("⚠ No users found. Creating default admin user...")
        author = User(
            email="admin@mfhelper.com",
            full_name="MFHelper Team",
            is_active=True,
            is_verified=True
        )
        db.add(author)
        db.commit()
        db.refresh(author)
    
    # Blog posts to seed
    posts_data = [
        {
            "filename": "getting-started-cas-upload.md",
            "slug": "getting-started-cas-upload",
        },
        {
            "filename": "understanding-portfolio-overlap.md",
            "slug": "understanding-portfolio-overlap",
        },
        {
            "filename": "maximizing-sip-returns.md",
            "slug": "maximizing-sip-returns",
        },
    ]
    
    created_posts = []
    
    for post_data in posts_data:
        # Check if post already exists
        existing = db.query(BlogPost).filter(BlogPost.slug == post_data["slug"]).first()
        if existing:
            print(f"⚠ Post already exists: {post_data['slug']}")
            continue
        
        # Parse markdown file
        try:
            parsed = BlogService.parse_markdown_file(post_data["filename"])
            metadata = parsed["metadata"]
            
            # Get category
            category = None
            if "category" in metadata:
                category = db.query(BlogCategory).filter(
                    BlogCategory.slug == metadata["category"]
                ).first()
            
            # Calculate reading time
            reading_time = BlogService.calculate_reading_time(parsed["content"])
            
            # Create blog post
            post = BlogPost(
                slug=post_data["slug"],
                title=metadata.get("title", "Untitled"),
                description=metadata.get("description", ""),
                content_file=post_data["filename"],
                author_id=author.id,
                category_id=category.id if category else None,
                featured_image=metadata.get("featured_image"),
                og_image=metadata.get("og_image"),
                is_published=True,
                published_at=datetime.fromisoformat(metadata.get("published_at", datetime.now().isoformat())),
                reading_time_minutes=reading_time,
                view_count=0
            )
            
            db.add(post)
            db.flush()  # Get post.id
            
            # Add tags
            if "tags" in metadata and metadata["tags"]:
                for tag_slug in metadata["tags"]:
                    tag = db.query(BlogTag).filter(BlogTag.slug == tag_slug).first()
                    if tag:
                        post.tags.append(tag)
            
            db.commit()
            db.refresh(post)
            
            created_posts.append(post)
            print(f"✓ Post: {post.title}")
            
        except FileNotFoundError:
            print(f"✗ File not found: {post_data['filename']}")
        except Exception as e:
            print(f"✗ Error creating post {post_data['slug']}: {str(e)}")
            db.rollback()
    
    return created_posts


def main():
    """Main seeding function"""
    print("\n🌱 Seeding blog data...\n")
    
    db = SessionLocal()
    
    try:
        # Seed categories
        print("Creating categories...")
        categories = seed_categories(db)
        print(f"✓ Created {len(categories)} categories\n")
        
        # Seed tags
        print("Creating tags...")
        tags = seed_tags(db)
        print(f"✓ Created {len(tags)} tags\n")
        
        # Seed blog posts
        print("Creating blog posts...")
        posts = seed_blog_posts(db)
        print(f"✓ Created {len(posts)} blog posts\n")
        
        print("✅ Blog seeding complete!\n")
        print(f"Total: {len(categories)} categories, {len(tags)} tags, {len(posts)} posts")
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
