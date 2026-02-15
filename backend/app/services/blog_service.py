"""
MFHelper - Blog Service Layer
Handles blog post parsing, rendering, and related operations
"""
import re
import math
from typing import List, Dict, Any
from pathlib import Path

import frontmatter
import markdown
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.models.blog import BlogPost, BlogCategory, BlogTag


class BlogService:
    """Service for blog operations"""
    
    # Get the project root directory (3 levels up from this file: services -> app -> backend -> root)
    _project_root = Path(__file__).parent.parent.parent.parent
    BLOG_POSTS_DIR = _project_root / "backend" / "data" / "blog" / "posts"
    BLOG_IMAGES_DIR = _project_root / "backend" / "data" / "blog" / "images"
    
    # Markdown extensions for rich content
    MD_EXTENSIONS = [
        'extra',  # Includes abbreviations, attribute lists, definition lists, etc.
        'codehilite',  # Syntax highlighting
        'fenced_code',  # ```code blocks```
        'tables',  # Table support
        'toc',  # Table of contents
        'nl2br',  # Convert newlines to <br>
        'sane_lists',  # Better list handling
    ]
    
    MD_EXTENSION_CONFIGS = {
        'codehilite': {
            'css_class': 'highlight',
            'linenums': False,
            'guess_lang': True,
        },
        'toc': {
            'permalink': True,
            'toc_depth': '2-3',
        }
    }
    
    @staticmethod
    def parse_markdown_file(file_path: str) -> Dict[str, Any]:
        """
        Parse a markdown file with front matter
        
        Args:
            file_path: Path to the markdown file
            
        Returns:
            Dictionary with metadata and content
        """
        full_path = BlogService.BLOG_POSTS_DIR / file_path
        
        if not full_path.exists():
            raise FileNotFoundError(f"Blog post file not found: {file_path}")
        
        with open(full_path, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        
        # Convert markdown to HTML
        md = markdown.Markdown(
            extensions=BlogService.MD_EXTENSIONS,
            extension_configs=BlogService.MD_EXTENSION_CONFIGS
        )
        html_content = md.convert(post.content)
        
        # Extract table of contents if available
        toc = md.toc if hasattr(md, 'toc') else ''
        
        return {
            'metadata': post.metadata,
            'content': post.content,
            'html_content': html_content,
            'toc': toc,
        }
    
    @staticmethod
    def calculate_reading_time(content: str) -> int:
        """
        Calculate estimated reading time in minutes
        
        Args:
            content: Blog post content (markdown or plain text)
            
        Returns:
            Estimated reading time in minutes
        """
        # Average reading speed: 200-250 words per minute
        WORDS_PER_MINUTE = 225
        
        # Remove markdown syntax for accurate word count
        text = re.sub(r'[#*`\[\]()]', '', content)
        text = re.sub(r'!\[.*?\]\(.*?\)', '', text)  # Remove image syntax
        text = re.sub(r'\[.*?\]\(.*?\)', '', text)  # Remove link syntax
        
        words = len(text.split())
        minutes = math.ceil(words / WORDS_PER_MINUTE)
        
        return max(1, minutes)  # Minimum 1 minute
    
    @staticmethod
    def generate_excerpt(content: str, length: int = 200) -> str:
        """
        Generate an excerpt from blog post content
        
        Args:
            content: Full blog post content
            length: Maximum length of excerpt
            
        Returns:
            Excerpt string
        """
        # Remove markdown syntax
        text = re.sub(r'[#*`]', '', content)
        text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
        text = re.sub(r'\[.*?\]\(.*?\)', '', text)
        
        # Get first paragraph or first N characters
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if lines:
            excerpt = lines[0]
            if len(excerpt) > length:
                excerpt = excerpt[:length].rsplit(' ', 1)[0] + '...'
            return excerpt
        
        return ''
    
    @staticmethod
    def get_related_posts(
        db: Session,
        post: BlogPost,
        limit: int = 3
    ) -> List[BlogPost]:
        """
        Find related blog posts based on category and tags
        
        Args:
            db: Database session
            post: Current blog post
            limit: Maximum number of related posts to return
            
        Returns:
            List of related BlogPost objects
        """
        # Build query for related posts
        query = db.query(BlogPost).filter(
            and_(
                BlogPost.id != post.id,
                BlogPost.is_published == True
            )
        )
        
        # Prioritize posts in same category
        related = []
        if post.category_id:
            same_category = query.filter(
                BlogPost.category_id == post.category_id
            ).order_by(BlogPost.published_at.desc()).limit(limit).all()
            related.extend(same_category)
        
        # If not enough, add posts with same tags
        if len(related) < limit and post.tags:
            tag_ids = [tag.id for tag in post.tags]
            same_tags = query.filter(
                BlogPost.tags.any(BlogTag.id.in_(tag_ids))
            ).filter(
                BlogPost.id.notin_([p.id for p in related])
            ).order_by(BlogPost.published_at.desc()).limit(limit - len(related)).all()
            related.extend(same_tags)
        
        # If still not enough, add latest posts
        if len(related) < limit:
            latest = query.filter(
                BlogPost.id.notin_([p.id for p in related])
            ).order_by(BlogPost.published_at.desc()).limit(limit - len(related)).all()
            related.extend(latest)
        
        return related[:limit]
    
    @staticmethod
    def search_posts(
        db: Session,
        query_string: str,
        limit: int = 10,
        offset: int = 0
    ) -> tuple[List[BlogPost], int]:
        """
        Search blog posts by title, description, and tags
        
        Args:
            db: Database session
            query_string: Search query
            limit: Maximum results to return
            offset: Pagination offset
            
        Returns:
            Tuple of (posts list, total count)
        """
        search_term = f"%{query_string}%"
        
        query = db.query(BlogPost).filter(
            and_(
                BlogPost.is_published == True,
                or_(
                    BlogPost.title.ilike(search_term),
                    BlogPost.description.ilike(search_term),
                    BlogPost.tags.any(BlogTag.name.ilike(search_term))
                )
            )
        ).order_by(BlogPost.published_at.desc())
        
        total = query.count()
        posts = query.offset(offset).limit(limit).all()
        
        return posts, total
    
    @staticmethod
    def increment_view_count(db: Session, post: BlogPost) -> None:
        """
        Increment the view count for a blog post
        
        Args:
            db: Database session
            post: BlogPost object
        """
        post.view_count = (post.view_count or 0) + 1
        db.commit()
    
    @staticmethod
    def get_popular_posts(db: Session, limit: int = 5) -> List[BlogPost]:
        """
        Get most popular blog posts by view count
        
        Args:
            db: Database session
            limit: Maximum number of posts to return
            
        Returns:
            List of BlogPost objects
        """
        return db.query(BlogPost).filter(
            BlogPost.is_published == True
        ).order_by(
            BlogPost.view_count.desc()
        ).limit(limit).all()
    
    @staticmethod
    def get_recent_posts(db: Session, limit: int = 5) -> List[BlogPost]:
        """
        Get most recent published blog posts
        
        Args:
            db: Database session
            limit: Maximum number of posts to return
            
        Returns:
            List of BlogPost objects
        """
        return db.query(BlogPost).filter(
            BlogPost.is_published == True
        ).order_by(
            BlogPost.published_at.desc()
        ).limit(limit).all()
    
    @staticmethod
    def get_or_create_category(
        db: Session,
        slug: str,
        name: str,
        description: str = None
    ) -> BlogCategory:
        """
        Get existing category or create new one
        
        Args:
            db: Database session
            slug: Category slug
            name: Category name
            description: Optional description
            
        Returns:
            BlogCategory object
        """
        category = db.query(BlogCategory).filter(
            BlogCategory.slug == slug
        ).first()
        
        if not category:
            category = BlogCategory(
                slug=slug,
                name=name,
                description=description
            )
            db.add(category)
            db.commit()
            db.refresh(category)
        
        return category
    
    @staticmethod
    def get_or_create_tag(
        db: Session,
        slug: str,
        name: str
    ) -> BlogTag:
        """
        Get existing tag or create new one
        
        Args:
            db: Database session
            slug: Tag slug
            name: Tag name
            
        Returns:
            BlogTag object
        """
        tag = db.query(BlogTag).filter(
            BlogTag.slug == slug
        ).first()
        
        if not tag:
            tag = BlogTag(slug=slug, name=name)
            db.add(tag)
            db.commit()
            db.refresh(tag)
        
        return tag
