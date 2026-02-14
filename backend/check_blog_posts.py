import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from app.database import SessionLocal
from app.models.models import User  # Import User model first
from app.models.blog import BlogPost

def main():
    """Check blog posts in database"""
    db = SessionLocal()
    
    try:
        posts = db.query(BlogPost).all()
        print(f"\n📝 Total blog posts in database: {len(posts)}\n")
        
        for post in posts:
            print(f"Title: {post.title}")
            print(f"  Slug: {post.slug}")
            print(f"  Published: {post.is_published}")
            print(f"  Category: {post.category.name if post.category else 'None'}")
            print(f"  Published At: {post.published_at}")
            print()
        
    finally:
        db.close()


if __name__ == "__main__":
    main()
