#!/usr/bin/env python3
"""Script para aplicar migración de cambio de tipo de phone"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import config
from alembic import command
from alembic.config import Config

# Configurar Alembic
alembic_cfg = Config("src/db/migrations/alembic.ini")
alembic_cfg.set_main_option("script_location", "src/db/migrations")
alembic_cfg.set_main_option("sqlalchemy.url", config.SQLALCHEMY_DATABASE_URI)

print("Applying migrations...")
command.upgrade(alembic_cfg, "head")
print("Migrations applied successfully!")