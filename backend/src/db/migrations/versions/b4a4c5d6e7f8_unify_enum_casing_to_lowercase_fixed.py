"""unify enum casing to lowercase - FIXED IDEMPOTENT VERSION

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
    conn = op.get_bind()
    
    # rolemensajeenum: Convert existing UPPERCASE to lowercase (if they exist)
    # Check if 'BOT' exists before trying to rename
    result = conn.execute(sa.text("""
        SELECT EXISTS (
            SELECT 1 FROM pg_enum 
            WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'rolemensajeenum')
            AND enumlabel = 'BOT'
        )
    """)).fetchone()
    if result[0]:
        op.execute("ALTER TYPE rolemensajeenum RENAME VALUE 'BOT' TO 'bot'")
    
    result = conn.execute(sa.text("""
        SELECT EXISTS (
            SELECT 1 FROM pg_enum 
            WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'rolemensajeenum')
            AND enumlabel = 'USER'
        )
    """)).fetchone()
    if result[0]:
        op.execute("ALTER TYPE rolemensajeenum RENAME VALUE 'USER' TO 'user'")

    # onboardingstepenum: Convert existing UPPERCASE to lowercase (if they exist)
    uppercase_values = ['PENDING_EMAIL', 'PENDING_VERIFICATION', 'VERIFIED', 'EXPIRED']
    for uppercase_val in uppercase_values:
        result = conn.execute(sa.text(f"""
            SELECT EXISTS (
                SELECT 1 FROM pg_enum 
                WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'onboardingstepenum')
                AND enumlabel = '{uppercase_val}'
            )
        """)).fetchone()
        if result[0]:
            lowercase_val = uppercase_val.lower()
            op.execute(f"ALTER TYPE onboardingstepenum RENAME VALUE '{uppercase_val}' TO '{lowercase_val}'")


def downgrade():
    conn = op.get_bind()
    
    # Revert to UPPERCASE (if lowercase values exist)
    # rolemensajeenum
    result = conn.execute(sa.text("""
        SELECT EXISTS (
            SELECT 1 FROM pg_enum 
            WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'rolemensajeenum')
            AND enumlabel = 'bot'
        )
    """)).fetchone()
    if result[0]:
        op.execute("ALTER TYPE rolemensajeenum RENAME VALUE 'bot' TO 'BOT'")
    
    result = conn.execute(sa.text("""
        SELECT EXISTS (
            SELECT 1 FROM pg_enum 
            WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'rolemensajeenum')
            AND enumlabel = 'user'
        )
    """)).fetchone()
    if result[0]:
        op.execute("ALTER TYPE rolemensajeenum RENAME VALUE 'user' TO 'USER'")

    # onboardingstepenum
    lowercase_values = ['pending_email', 'pending_verification', 'verified', 'expired']
    for lowercase_val in lowercase_values:
        result = conn.execute(sa.text(f"""
            SELECT EXISTS (
                SELECT 1 FROM pg_enum 
                WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'onboardingstepenum')
                AND enumlabel = '{lowercase_val}'
            )
        """)).fetchone()
        if result[0]:
            uppercase_val = lowercase_val.upper()
            op.execute(f"ALTER TYPE onboardingstepenum RENAME VALUE '{lowercase_val}' TO '{uppercase_val}'")