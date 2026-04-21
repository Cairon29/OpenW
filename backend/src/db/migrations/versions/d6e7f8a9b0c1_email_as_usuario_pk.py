"""email as usuario primary key, novedad FK by email

Revision ID: d6e7f8a9b0c1
Revises: c5f6d7e8f9a0
Create Date: 2026-04-20 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'd6e7f8a9b0c1'
down_revision = 'c5f6d7e8f9a0'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Add new email FK column to novedad
    op.add_column('novedad', sa.Column('fk_email_usuario', sa.String(120), nullable=True))

    # 2. Backfill from old integer FK
    op.execute("""
        UPDATE novedad SET fk_email_usuario = (
            SELECT email FROM usuarios WHERE usuarios.id = novedad.fk_id_usuario
        ) WHERE fk_id_usuario IS NOT NULL
    """)

    # 3. Drop old FK column from novedad
    op.drop_constraint('novedad_fk_id_usuario_fkey', 'novedad', type_='foreignkey')
    op.drop_column('novedad', 'fk_id_usuario')

    # 4. Drop id PK from usuarios, make email the PK
    op.drop_constraint('usuarios_pkey', 'usuarios', type_='primary')
    op.drop_column('usuarios', 'id')
    op.create_primary_key('usuarios_pkey', 'usuarios', ['email'])
    op.drop_constraint('usuarios_email_key', 'usuarios', type_='unique')

    # 5. Add FK from novedad to new PK
    op.create_foreign_key(
        'fk_novedad_email_usuario', 'novedad', 'usuarios',
        ['fk_email_usuario'], ['email'],
    )


def downgrade():
    # 1. Drop email FK
    op.drop_constraint('fk_novedad_email_usuario', 'novedad', type_='foreignkey')

    # 2. Restore id PK on usuarios
    op.drop_constraint('usuarios_pkey', 'usuarios', type_='primary')
    op.add_column('usuarios', sa.Column('id', sa.Integer(), autoincrement=True, nullable=False))
    op.create_primary_key('usuarios_pkey', 'usuarios', ['id'])
    op.create_unique_constraint('usuarios_email_key', 'usuarios', ['email'])

    # 3. Restore old FK column on novedad
    op.add_column('novedad', sa.Column('fk_id_usuario', sa.Integer(), nullable=True))
    op.execute("""
        UPDATE novedad SET fk_id_usuario = (
            SELECT id FROM usuarios WHERE usuarios.email = novedad.fk_email_usuario
        ) WHERE fk_email_usuario IS NOT NULL
    """)
    op.create_foreign_key('novedad_fk_id_usuario_fkey', 'novedad', 'usuarios',
                          ['fk_id_usuario'], ['id'])
    op.drop_column('novedad', 'fk_email_usuario')
