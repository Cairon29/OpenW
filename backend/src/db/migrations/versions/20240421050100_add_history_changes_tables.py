"""Add history_changes tables for user attribute history tracking

Revision ID: 20240421050100
Revises: 20240421050000
Create Date: 2026-04-21 05:01:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '20240421050100'
down_revision = '20240421050000'
branch_labels = None
depends_on = None


def upgrade():
    # Create prev_user_name table
    op.create_table('prev_user_name',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('fk_email_usuario', sa.String(120), nullable=True),
        sa.Column('nombre_anterior', sa.String(120), nullable=True),
        sa.Column('fecha_registro', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['fk_email_usuario'], ['usuarios.email'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create prev_user_direccion table
    op.create_table('prev_user_direccion',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('fk_email_usuario', sa.String(120), nullable=True),
        sa.Column('fk_id_direccion', sa.Integer(), nullable=True),
        sa.Column('fecha_registro', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['fk_email_usuario'], ['usuarios.email'], ),
        sa.ForeignKeyConstraint(['fk_id_direccion'], ['direccion.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create prev_user_viceprecidencia table
    op.create_table('prev_user_viceprecidencia',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('fk_email_usuario', sa.String(120), nullable=True),
        sa.Column('fk_id_viceprecidencia', sa.Integer(), nullable=True),
        sa.Column('fecha_registro', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['fk_email_usuario'], ['usuarios.email'], ),
        sa.ForeignKeyConstraint(['fk_id_viceprecidencia'], ['vicepresidencia.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('prev_user_viceprecidencia')
    op.drop_table('prev_user_direccion')
    op.drop_table('prev_user_name')
