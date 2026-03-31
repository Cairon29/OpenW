"""add onboarding fields to conversation_state and role enum to chat_message

Revision ID: 8df83dcfee3f
Revises:
Create Date: 2026-03-29 22:17:08.877894

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8df83dcfee3f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ── chat_message: add embedding column ───────────────────────────────────
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("ALTER TABLE chat_message ADD COLUMN IF NOT EXISTS embedding vector(384)")

    # ── chat_message: change role from VARCHAR to enum ────────────────────────
    # Values use lowercase to match RoleMensajeEnum.value ("user", "bot")
    op.execute(
        "DO $$ BEGIN "
        "  CREATE TYPE rolemensajeenum AS ENUM ('user', 'bot'); "
        "EXCEPTION WHEN duplicate_object THEN NULL; "
        "END $$"
    )
    # Only alter if column is still VARCHAR (idempotent check)
    # db.create_all() stores enum NAMES in uppercase ('USER', 'BOT').
    # Existing VARCHAR data is lowercase ('user', 'bot'), so we UPPER() before casting.
    op.execute(
        "DO $$ BEGIN "
        "  IF (SELECT data_type FROM information_schema.columns "
        "      WHERE table_name='chat_message' AND column_name='role') = 'character varying' THEN "
        "    ALTER TABLE chat_message "
        "    ALTER COLUMN role TYPE rolemensajeenum "
        "    USING UPPER(role)::rolemensajeenum; "
        "  END IF; "
        "END $$"
    )

    # ── conversation_state: add onboarding fields ─────────────────────────────
    # IF NOT EXISTS / ADD COLUMN IF NOT EXISTS makes this idempotent in case
    # db.create_all() already applied these on a previous app startup.
    op.execute(
        "DO $$ BEGIN "
        "  CREATE TYPE onboardingstepenum AS ENUM "
        "    ('pending_email', 'pending_verification', 'verified', 'expired'); "
        "EXCEPTION WHEN duplicate_object THEN NULL; "
        "END $$"
    )
    op.execute(
        "ALTER TABLE conversation_state "
        "ADD COLUMN IF NOT EXISTS onboarding_step onboardingstepenum "
        "NOT NULL DEFAULT 'pending_email'"
    )
    op.execute(
        "ALTER TABLE conversation_state "
        "ADD COLUMN IF NOT EXISTS email VARCHAR(120)"
    )
    op.execute(
        "ALTER TABLE conversation_state "
        "ADD COLUMN IF NOT EXISTS verification_token VARCHAR(64)"
    )
    op.execute(
        "ALTER TABLE conversation_state "
        "ADD COLUMN IF NOT EXISTS verification_sent_at TIMESTAMP"
    )


def downgrade():
    # ── conversation_state: remove onboarding fields ──────────────────────────
    op.execute("ALTER TABLE conversation_state DROP COLUMN IF EXISTS verification_sent_at")
    op.execute("ALTER TABLE conversation_state DROP COLUMN IF EXISTS verification_token")
    op.execute("ALTER TABLE conversation_state DROP COLUMN IF EXISTS email")
    op.execute("ALTER TABLE conversation_state DROP COLUMN IF EXISTS onboarding_step")
    op.execute("DROP TYPE IF EXISTS onboardingstepenum")

    # ── chat_message: revert role to VARCHAR ──────────────────────────────────
    op.execute(
        "ALTER TABLE chat_message "
        "ALTER COLUMN role TYPE VARCHAR(10) "
        "USING role::text"
    )
    op.execute("DROP TYPE IF EXISTS rolemensajeenum")

    # ── chat_message: remove embedding column ────────────────────────────────
    op.execute("ALTER TABLE chat_message DROP COLUMN IF EXISTS embedding")
