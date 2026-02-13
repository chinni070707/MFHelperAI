"""add_goal_planning_data_column

Revision ID: 004_goal_planning
Revises: 003_email_verification
Create Date: 2026-02-13

Description:
Adds goal_planning_data column to user_settings table to store:
- goals: list of financial goals with name, amount, age, iconType
- lumpsums: one-time income at specific ages
- expenses: one-time expenses at specific ages
- parameters: initial values, age, expected return, etc.

This allows users to save their goal planning data and retrieve it
when they return to the goal-planning.html page.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON as PG_JSON
from sqlalchemy.dialects.mysql import JSON as MYSQL_JSON


# revision identifiers, used by Alembic.
revision = '004_goal_planning'
down_revision = '003_email_verification'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add goal_planning_data column to user_settings table"""
    
    # Try to detect the dialect and use appropriate JSON type
    bind = op.get_bind()
    dialect_name = bind.dialect.name
    
    if dialect_name == 'postgresql':
        json_type = PG_JSON
    elif dialect_name == 'mysql':
        json_type = MYSQL_JSON
    else:
        # For SQLite and others, use SQLAlchemy's generic JSON
        json_type = sa.JSON
    
    op.add_column(
        'user_settings',
        sa.Column('goal_planning_data', json_type, nullable=True)
    )


def downgrade() -> None:
    """Remove goal_planning_data column from user_settings table"""
    op.drop_column('user_settings', 'goal_planning_data')
