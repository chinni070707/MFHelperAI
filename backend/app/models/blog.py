"""
MFHelper - Blog Models
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Index, Text, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


# Association table for many-to-many relationship between posts and tags
post_tags = Table(
    'post_tags',
    Base.metadata,
    Column('post_id', Integer, ForeignKey('blog_posts.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('blog_tags.id', ondelete='CASCADE'), primary_key=True)
)


class BlogCategory(Base):
    """Blog category model"""
    __tablename__ = "blog_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    posts = relationship("BlogPost", back_populates="category")
    
    def __repr__(self):
        return f"<BlogCategory(name='{self.name}', slug='{self.slug}')>"


class BlogTag(Base):
    """Blog tag model"""
    __tablename__ = "blog_tags"
    
    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    posts = relationship("BlogPost", secondary=post_tags, back_populates="tags")
    
    def __repr__(self):
        return f"<BlogTag(name='{self.name}', slug='{self.slug}')>"


class BlogPost(Base):
    """Blog post model"""
    __tablename__ = "blog_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(200), unique=True, index=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)  # Meta description for SEO
    content_file = Column(String(255), nullable=False)  # Path to markdown file
    author_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    category_id = Column(Integer, ForeignKey("blog_categories.id", ondelete="SET NULL"), nullable=True)
    
    # SEO and social
    featured_image = Column(String(500), nullable=True)
    og_image = Column(String(500), nullable=True)  # Open Graph image
    
    # Publishing
    is_published = Column(Boolean, default=False, index=True)
    published_at = Column(DateTime, nullable=True, index=True)
    
    # Analytics
    view_count = Column(Integer, default=0)
    reading_time_minutes = Column(Integer, default=5)  # Estimated reading time
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    author = relationship("User", foreign_keys=[author_id])
    category = relationship("BlogCategory", back_populates="posts")
    tags = relationship("BlogTag", secondary=post_tags, back_populates="posts")
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_published_date', 'is_published', 'published_at'),
        Index('idx_category_published', 'category_id', 'is_published'),
    )
    
    def __repr__(self):
        return f"<BlogPost(title='{self.title}', slug='{self.slug}', published={self.is_published})>"
