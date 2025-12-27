"""Update workout_plan schema with detailed_strategy and text fields

Revision ID: 002_update_workout_plan_schema
Revises: 001_add_auth_tables
Create Date: 2025-12-27 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_update_workout_plan_schema'
down_revision = '001_add_auth_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add detailed_strategy column to workout_plans
    op.add_column('workout_plans', sa.Column('detailed_strategy', sa.Text(), nullable=True))
    
    # Convert strategy from JSONB to Text
    # First, extract text from JSONB if it exists
    op.execute("""
        UPDATE workout_plans 
        SET detailed_strategy = strategy::text 
        WHERE strategy IS NOT NULL
    """)
    
    # Alter column type from JSONB to Text
    op.alter_column('workout_plans', 'strategy',
                    existing_type=postgresql.JSONB(),
                    type_=sa.Text(),
                    existing_nullable=True,
                    postgresql_using='strategy::text')
    
    # Alter column type from JSONB to Text for expectations
    op.alter_column('workout_plans', 'expectations',
                    existing_type=postgresql.JSONB(),
                    type_=sa.Text(),
                    existing_nullable=True,
                    postgresql_using='expectations::text')
    
    # Add week_note column to workout_weeks
    op.add_column('workout_weeks', sa.Column('week_note', sa.Text(), nullable=True))
    
    # Drop tempo and notes columns from workout_day_exercises
    op.drop_column('workout_day_exercises', 'tempo')
    op.drop_column('workout_day_exercises', 'notes')


def downgrade() -> None:
    # Add back tempo and notes columns
    op.add_column('workout_day_exercises', sa.Column('notes', sa.Text(), nullable=True))
    op.add_column('workout_day_exercises', sa.Column('tempo', sa.String(length=50), nullable=True))
    
    # Remove week_note column
    op.drop_column('workout_weeks', 'week_note')
    
    # Convert strategy back to JSONB
    op.alter_column('workout_plans', 'strategy',
                    existing_type=sa.Text(),
                    type_=postgresql.JSONB(),
                    existing_nullable=True,
                    postgresql_using='strategy::jsonb')
    
    # Convert expectations back to JSONB
    op.alter_column('workout_plans', 'expectations',
                    existing_type=sa.Text(),
                    type_=postgresql.JSONB(),
                    existing_nullable=True,
                    postgresql_using='expectations::jsonb')
    
    # Remove detailed_strategy column
    op.drop_column('workout_plans', 'detailed_strategy')
