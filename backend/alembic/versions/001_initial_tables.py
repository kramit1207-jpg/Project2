"""Initial tables for Humantic and Gemini data

Revision ID: 001
Revises: 
Create Date: 2026-01-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create humantic_profiles table
    op.create_table(
        'humantic_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('linkedin_url', sa.String(length=512), nullable=False, unique=True),
        sa.Column('user_id', sa.String(length=256), nullable=False),
        sa.Column('profile_data', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('big_five_scores', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'))
    )
    
    # Create indexes for humantic_profiles
    op.create_index('idx_humantic_linkedin_url', 'humantic_profiles', ['linkedin_url'])
    op.create_index('idx_humantic_user_id', 'humantic_profiles', ['user_id'])
    op.create_index('idx_linkedin_url_created', 'humantic_profiles', ['linkedin_url', 'created_at'])
    
    # Create gemini_analyses table
    op.create_table(
        'gemini_analyses',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('humantic_profile_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('strengths', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('weaknesses', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('raw_response', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(
            ['humantic_profile_id'],
            ['humantic_profiles.id'],
            name='fk_gemini_humantic_profile',
            ondelete='CASCADE'
        )
    )
    
    # Create index for gemini_analyses
    op.create_index('idx_gemini_profile_id', 'gemini_analyses', ['humantic_profile_id'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index('idx_gemini_profile_id', table_name='gemini_analyses')
    op.drop_table('gemini_analyses')
    
    op.drop_index('idx_linkedin_url_created', table_name='humantic_profiles')
    op.drop_index('idx_humantic_user_id', table_name='humantic_profiles')
    op.drop_index('idx_humantic_linkedin_url', table_name='humantic_profiles')
    op.drop_table('humantic_profiles')
