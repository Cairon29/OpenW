"""
Triggers script: destruye y recrea triggers de historial de usuarios.
Idempotente — usa DROP TRIGGER IF EXISTS + CREATE OR REPLACE FUNCTION.
Se ejecuta automaticamente en cada deploy via entrypoint.sh.
"""
from pathlib import Path
from src.app import create_app
from src.extensions import db

TRIGGERS_SQL = Path(__file__).parent.parent / "triggers" / "user_history_triggers.sql"


def setup_triggers():
    sql = TRIGGERS_SQL.read_text(encoding="utf-8")
    with db.engine.connect() as conn:
        conn.execute(db.text(sql))
        conn.commit()
    print("[Triggers] Triggers de historial de usuarios creados/actualizados.")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        setup_triggers()
