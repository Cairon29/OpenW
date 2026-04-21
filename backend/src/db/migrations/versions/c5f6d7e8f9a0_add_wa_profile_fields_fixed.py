"""add wa profile fields to conversation_state - FIXED IDEMPOTENT VERSION

Revision ID: c5f6d7e8f9a0
Revises: b4a4c5d6e7f8
Create Date: 2026-04-04 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c5f6d7e8f9a0'
down_revision = 'b4a4c5d6e7f8'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    
    # Check if wa_profile_name column already exists
    result = conn.execute(sa.text("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'conversation_state' 
            AND column_name = 'wa_profile_name'
        )
    """)).fetchone()
    
    if not result[0]:
        op.add_column('conversation_state', sa.Column('wa_profile_name', sa.String(120), nullable=True))
    
    # Check if wa_profile_photo_url column already exists
    result = conn.execute(sa.text("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'conversation_state' 
            AND column_name = 'wa_profile_photo_url'
        )
    """)).fetchone()
    
    if not result[0]:
        op.add_column('conversation_state', sa.Column('wa_profile_photo_url', sa.Text(), nullable=True))
    
    # Check if wa_photo_fetched_at column already exists
    result = conn.execute(sa.text("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'conversation_state' 
            AND column_name = 'wa_photo_fetched_at'
        )
    """)).fetchone()
    
    if not result[0]:
        op.add_column('conversation_state', sa.Column('wa_photo_fetched_at', sa.DateTime(), nullable=True))


def downgrade():
    conn = op.get_bind()
    
    # Check if wa_photo_fetched_at column exists before dropping
    result = conn.execute(sa.text("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'conversation_state' 
            AND column_name = 'wa_photo_fetched_at'
        )
    """)).fetchone()
    
    if result[0]:
        op.drop_column('conversation_state', 'wa_photo_fetched_at')
    
    # Check if wa_profile_photo_url column exists before dropping
    result = conn.execute(sa.text("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'conversation_state' 
            AND column_name = 'wa_profile_photo_url'
        )
    """)).fetchone()
    
    if result[0]:
        op.drop_column('conversation_state', 'wa_profile_photo_url')
    
    # Check if wa_profile_name column exists before dropping
    result = conn.execute(sa.text("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'conversation_state' 
            AND column_name = 'wa_profile_name'
        )
    """)).fetchone()
    
    if result[0]:
        op.drop_column('conversation_state', 'wa_profile_name')