"""unify enum casing to lowercase

Revision ID: b4a4c5d6e7f8
Revises: 1291cbe5f3eb
Create Date: 2026-04-01 02:35:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b4a4c5d6e7f8'
down_revision = '1291cbe5f3eb'
branch_labels = None
depends_on = None


def upgrade():
    # rolemensajeenum: Convert existing UPPERCASE to lowercase
    op.execute("ALTER TYPE rolemensajeenum RENAME VALUE 'BOT' TO 'bot'")
    op.execute("ALTER TYPE rolemensajeenum RENAME VALUE 'USER' TO 'user'")

    # onboardingstepenum: Convert existing UPPERCASE to lowercase
    op.execute("ALTER TYPE onboardingstepenum RENAME VALUE 'PENDING_EMAIL' TO 'pending_email'")
    op.execute("ALTER TYPE onboardingstepenum RENAME VALUE 'PENDING_VERIFICATION' TO 'pending_verification'")
    op.execute("ALTER TYPE onboardingstepenum RENAME VALUE 'VERIFIED' TO 'verified'")
    op.execute("ALTER TYPE onboardingstepenum RENAME VALUE 'EXPIRED' TO 'expired'")


def downgrade():
    # Revert to UPPERCASE
    op.execute("ALTER TYPE rolemensajeenum RENAME VALUE 'bot' TO 'BOT'")
    op.execute("ALTER TYPE rolemensajeenum RENAME VALUE 'user' TO 'USER'")

    op.execute("ALTER TYPE onboardingstepenum RENAME VALUE 'pending_email' TO 'PENDING_EMAIL'")
    op.execute("ALTER TYPE onboardingstepenum RENAME VALUE 'pending_verification' TO 'PENDING_VERIFICATION'")
    op.execute("ALTER TYPE onboardingstepenum RENAME VALUE 'verified' TO 'VERIFIED'")
    op.execute("ALTER TYPE onboardingstepenum RENAME VALUE 'expired' TO 'EXPIRED'")
