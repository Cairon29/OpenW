from backend.extensions import db
from backend.schemas import Usuarios


class UsuariosService:

    @staticmethod
    def register_from_whatsapp(data):
        phone_number = data.get("phone")
        user = Usuarios.query.filter_by(phone=phone_number).first()

        if not user:
            user = Usuarios(
                phone=phone_number,
                name=data.get("name", f"Usuario_{phone_number}"),
                email=data.get("email"),
                password=data.get("password", "temp_pass_whatsapp"),
                is_admin=False,
                fk_id_direccion=data.get("direccion_id"),
                fk_id_vicepresidencia=data.get("vicepresidencia_id"),
            )
            db.session.add(user)
        else:
            if "name" in data:
                user.name = data["name"]
            if "email" in data:
                user.email = data["email"]

        try:
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            print(f"Error al registrar usuario: {e}")
            return None

    @staticmethod
    def get_all():
        return Usuarios.query.all()

    @staticmethod
    def login(email, password):
        user = Usuarios.query.filter_by(email=email).first()
        if user and user.password == password and user.is_admin:
            return user
        return None
