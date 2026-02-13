"""Add blog models

Revision ID: 006_blog_models
Revises: 005_goals_table
Create Date: 2026-02-13 23:21:26

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '006_blog_models'
down_revision = '005_goals_table'
branch_labels = None
depends_on = None


def upgrade():
    # Create blog_categories table
    op.create_table('blog_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_blog_categories_id'), 'blog_categories', ['id'], unique=False)
    op.create_index(op.f('ix_blog_categories_slug'), 'blog_categories', ['slug'], unique=True)
    
    # Create blog_tags table
    op.create_table('blog_tags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_blog_tags_id'), 'blog_tags', ['id'], unique=False)
    op.create_index(op.f('ix_blog_tags_slug'), 'blog_tags', ['slug'], unique=True)
    
    # Create blog_posts table
    op.create_table('blog_posts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('slug', sa.String(length=200), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('content_file', sa.String(length=255), nullable=False),
        sa.Column('author_id', sa.Integer(), nullable=True),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('featured_image', sa.String(length=500), nullable=True),
        sa.Column('og_image', sa.String(length=500), nullable=True),
        sa.Column('is_published', sa.Boolean(), nullable=True),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('view_count', sa.Integer(), nullable=True),
        sa.Column('reading_time_minutes', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['category_id'], ['blog_categories.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_category_published', 'blog_posts', ['category_id', 'is_published'], unique=False)
    op.create_index('idx_published_date', 'blog_posts', ['is_published', 'published_at'], unique=False)
    op.create_index(op.f('ix_blog_posts_id'), 'blog_posts', ['id'], unique=False)
    op.create_index(op.f('ix_blog_posts_is_published'), 'blog_posts', ['is_published'], unique=False)
    op.create_index(op.f('ix_blog_posts_published_at'), 'blog_posts', ['published_at'], unique=False)
    op.create_index(op.f('ix_blog_posts_slug'), 'blog_posts', ['slug'], unique=True)
    
    # Create post_tags association table
    op.create_table('post_tags',
        sa.Column('post_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['post_id'], ['blog_posts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['blog_tags.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('post_id', 'tag_id')
    )


def downgrade():
    op.drop_table('post_tags')
    op.drop_index(op.f('ix_blog_posts_slug'), table_name='blog_posts')
    op.drop_index(op.f('ix_blog_posts_published_at'), table_name='blog_posts')
    op.drop_index(op.f('ix_blog_posts_is_published'), table_name='blog_posts')
    op.drop_index(op.f('ix_blog_posts_id'), table_name='blog_posts')
    op.drop_index('idx_published_date', table_name='blog_posts')
    op.drop_index('idx_category_published', table_name='blog_posts')
    op.drop_table('blog_posts')
    op.drop_index(op.f('ix_blog_tags_slug'), table_name='blog_tags')
    op.drop_index(op.f('ix_blog_tags_id'), table_name='blog_tags')
    op.drop_table('blog_tags')
    op.drop_index(op.f('ix_blog_categories_slug'), table_name='blog_categories')
    op.drop_index(op.f('ix_blog_categories_id'), table_name='blog_categories')
    op.drop_table('blog_categories')
