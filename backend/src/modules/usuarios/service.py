from src.extensions import db
from src.db.models import Usuarios

class UsuariosService:

    @staticmethod
    def register_from_whatsapp(data):
        email = data.get("email")
        if not email:
            return None
        user = Usuarios.query.filter_by(email=email).first()

        if not user:
            user = Usuarios(
                email=email,
                phone=data.get("phone"),
                name=data.get("name", f"Usuario_{email}"),
                password=data.get("password", "temp_pass_whatsapp"),
                is_admin=False,
                fk_id_direccion=data.get("direccion_id"),
                fk_id_vicepresidencia=data.get("vicepresidencia_id"),
            )
            db.session.add(user)
        else:
            if "name" in data:
                user.name = data["name"]
            if "phone" in data:
                user.phone = data["phone"]

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
