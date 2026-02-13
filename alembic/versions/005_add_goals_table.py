"""add_goals_table

Revision ID: 005_goals_table
Revises: 004_goal_planning
Create Date: 2026-02-13

Description:
Creates a dedicated goals table for storing user financial goals.
This replaces the JSON-based goal_planning_data approach with a proper
relational table for better querying and data integrity.

Goals include:
- name: Custom name like "1st Daughter wedding"
- icon_type: Icon type (house, vehicle, education, etc.)
- amount: Goal amount in rupees
- age: Age when goal is to be achieved
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '005_goals_table'
down_revision = '004_goal_planning'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create goals table"""
    
    op.create_table(
        'goals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('icon_type', sa.String(length=50), nullable=True),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('age', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    
    # Create indexes
    op.create_index('idx_goal_user_age', 'goals', ['user_id', 'age'])
    op.create_index(op.f('ix_goals_id'), 'goals', ['id'])


def downgrade() -> None:
    """Drop goals table"""
    
    op.drop_index('idx_goal_user_age', table_name='goals')
    op.drop_index(op.f('ix_goals_id'), table_name='goals')
    op.drop_table('goals')
