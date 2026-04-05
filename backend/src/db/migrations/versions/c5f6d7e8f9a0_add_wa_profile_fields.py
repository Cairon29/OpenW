"""add wa profile fields to conversation_state

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
    op.add_column('conversation_state', sa.Column('wa_profile_name', sa.String(120), nullable=True))
    op.add_column('conversation_state', sa.Column('wa_profile_photo_url', sa.Text(), nullable=True))
    op.add_column('conversation_state', sa.Column('wa_photo_fetched_at', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('conversation_state', 'wa_photo_fetched_at')
    op.drop_column('conversation_state', 'wa_profile_photo_url')
    op.drop_column('conversation_state', 'wa_profile_name')
