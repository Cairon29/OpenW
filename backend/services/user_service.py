from models.User import User
from extensions import db

class UserService:

    @staticmethod
    def register_from_whatsapp(data):
     
 
        phone_number = data.get("phone")
        user = User.query.get(phone_number)

        if not user:
    
            user = User(
                phone=phone_number,
                name=data.get("name", f"Usuario_{phone_number}"), 
                email=data.get("email"),
            
                password=data.get("password", "temp_pass_whatsapp"),
                is_admin=False,
             
                direccion_id=data.get("direccion_id"),
                vicepresidencia_id=data.get("vicepresidencia_id")
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
        return User.query.all()

    @staticmethod
    def login(email, password):
       
        user = User.query.filter_by(email=email).first()

        if user and user.password == password and user.is_admin:
            return user
            
        return None