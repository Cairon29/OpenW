"""migrate verified to completed

Revision ID: 1291cbe5f3eb
Revises: a1b2c3d4e5f6
Create Date: 2026-04-01 00:25:35.607054

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1291cbe5f3eb'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "UPDATE conversation_state "
        "SET onboarding_step = 'completed' "
        "WHERE onboarding_step::text = 'VERIFIED'"
    )


def downgrade():
    op.execute(
        "UPDATE conversation_state "
        "SET onboarding_step = 'VERIFIED' "
        "WHERE onboarding_step::text = 'completed'"
    )
