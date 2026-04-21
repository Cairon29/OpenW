"""Add prev_user_telefono table for phone history tracking

Revision ID: 20240421050200
Revises: 20240421050100
Create Date: 2026-04-21 05:02:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '20240421050200'
down_revision = '20240421050100'
branch_labels = None
depends_on = None


def upgrade():
    # Create prev_user_telefono table
    op.create_table('prev_user_telefono',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('fk_email_usuario', sa.String(120), nullable=True),
        sa.Column('telefono_anterior', sa.String(20), nullable=True),
        sa.Column('fecha_registro', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['fk_email_usuario'], ['usuarios.email'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('prev_user_telefono')
