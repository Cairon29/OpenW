"""
Seed script: inserta datos por defecto en vicepresidencia y direccion.
Idempotente — si los registros ya existen, no los duplica.
Se ejecuta automaticamente en cada deploy via entrypoint.sh.
"""

from src.app import create_app
from src.extensions import db
from src.db.models.vicepresidencia import Vicepresidencia
from src.db.models.direccion import Direccion


SEED_DATA = {
    "Tecnología e Información": [
        "Software",
        "Infraestructura",
        "Ciberseguridad",
        "Base de Datos",
        "Arquitectura",
        "Redes",
    ],
}


def seed():
    for vp_nombre, direcciones in SEED_DATA.items():
        vp = Vicepresidencia.query.filter_by(nombre=vp_nombre).first()
        if not vp:
            vp = Vicepresidencia(nombre=vp_nombre)
            db.session.add(vp)
            db.session.flush()
            print(f"[Seed] Vicepresidencia creada: {vp_nombre}")
        else:
            print(f"[Seed] Vicepresidencia ya existe: {vp_nombre}")

        for dir_nombre in direcciones:
            existe = Direccion.query.filter_by(nombre=dir_nombre).first()
            if not existe:
                db.session.add(Direccion(nombre=dir_nombre, fk_id_vicepresidencia=vp.id))
                print(f"[Seed]   Dirección creada: {dir_nombre}")
            else:
                print(f"[Seed]   Dirección ya existe: {dir_nombre}")

    db.session.commit()
    print("[Seed] Seed completado.")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        seed()
