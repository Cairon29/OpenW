"""add multiphase conversation flow fields and enum values

Revision ID: a1b2c3d4e5f6
Revises: 8df83dcfee3f
Create Date: 2026-03-31 18:00:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '8df83dcfee3f'
branch_labels = None
depends_on = None


def upgrade():
    # ── onboardingstepenum: add new phase values ─────────────────────────────
    op.execute("ALTER TYPE onboardingstepenum ADD VALUE IF NOT EXISTS 'bienvenida'")
    op.execute("ALTER TYPE onboardingstepenum ADD VALUE IF NOT EXISTS 'pending_vicepresidencia'")
    op.execute("ALTER TYPE onboardingstepenum ADD VALUE IF NOT EXISTS 'pending_direccion'")
    op.execute("ALTER TYPE onboardingstepenum ADD VALUE IF NOT EXISTS 'pending_novedad'")
    op.execute("ALTER TYPE onboardingstepenum ADD VALUE IF NOT EXISTS 'pending_confirmacion'")
    op.execute("ALTER TYPE onboardingstepenum ADD VALUE IF NOT EXISTS 'completed'")

    # ── conversation_state: profile columns (persist across novedades) ───────
    op.execute(
        "ALTER TABLE conversation_state "
        "ADD COLUMN IF NOT EXISTS fk_id_vicepresidencia INTEGER "
        "REFERENCES vicepresidencia(id)"
    )
    op.execute(
        "ALTER TABLE conversation_state "
        "ADD COLUMN IF NOT EXISTS fk_id_direccion INTEGER "
        "REFERENCES direccion(id)"
    )

    # ── conversation_state: pending novedad columns (cleared after each save) ─
    op.execute(
        "ALTER TABLE conversation_state "
        "ADD COLUMN IF NOT EXISTS pending_titulo VARCHAR(200)"
    )
    op.execute(
        "ALTER TABLE conversation_state "
        "ADD COLUMN IF NOT EXISTS pending_descripcion TEXT"
    )
    op.execute(
        "ALTER TABLE conversation_state "
        "ADD COLUMN IF NOT EXISTS pending_severidad VARCHAR(20)"
    )
    op.execute(
        "ALTER TABLE conversation_state "
        "ADD COLUMN IF NOT EXISTS pending_categoria_id INTEGER "
        "REFERENCES categoria_novedad(id)"
    )
    op.execute(
        "ALTER TABLE conversation_state "
        "ADD COLUMN IF NOT EXISTS pending_respuesta TEXT"
    )

    # ── conversation_state: modification sub-flow flag ────────────────────────
    op.execute(
        "ALTER TABLE conversation_state "
        "ADD COLUMN IF NOT EXISTS awaiting_modification BOOLEAN DEFAULT FALSE"
    )

    pass


def downgrade():
    # ── conversation_state: drop new columns ─────────────────────────────────
    op.execute("ALTER TABLE conversation_state DROP COLUMN IF EXISTS awaiting_modification")
    op.execute("ALTER TABLE conversation_state DROP COLUMN IF EXISTS pending_respuesta")
    op.execute("ALTER TABLE conversation_state DROP COLUMN IF EXISTS pending_categoria_id")
    op.execute("ALTER TABLE conversation_state DROP COLUMN IF EXISTS pending_severidad")
    op.execute("ALTER TABLE conversation_state DROP COLUMN IF EXISTS pending_descripcion")
    op.execute("ALTER TABLE conversation_state DROP COLUMN IF EXISTS pending_titulo")
    op.execute("ALTER TABLE conversation_state DROP COLUMN IF EXISTS fk_id_direccion")
    op.execute("ALTER TABLE conversation_state DROP COLUMN IF EXISTS fk_id_vicepresidencia")

    pass
    # Note: PostgreSQL does not support removing individual enum values.
    # The new values remain in the type but are unused after downgrade.
