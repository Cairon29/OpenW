"""Change usuarios.phone from INTEGER to VARCHAR

Revision ID: 20240421050000
Revises: d6e7f8a9b0c1
Create Date: 2026-04-21 05:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '20240421050000'
down_revision = 'd6e7f8a9b0c1'
branch_labels = None
depends_on = None


def upgrade():
    # Cambiar el tipo de dato de INTEGER a VARCHAR(20)
    op.alter_column('usuarios', 'phone',
               existing_type=sa.INTEGER(),
               type_=sa.String(20),
               existing_nullable=True,
               existing_unique=True)


def downgrade():
    # Revertir a INTEGER (nota: esto podría fallar si hay valores que no caben en INTEGER)
    op.alter_column('usuarios', 'phone',
               existing_type=sa.String(20),
               type_=sa.INTEGER(),
               existing_nullable=True,
               existing_unique=True)