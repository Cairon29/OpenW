from flask import Blueprint, request, jsonify
from services.user_service import UserService
from schemas.user_dto import UserSchema

user_bp = Blueprint("user", __name__)
user_schema = UserSchema()
users_schema = UserSchema(many=True)

@user_bp.route("/", methods=["POST"])
def register_user():

    data = request.get_json()
    
   
    if not data or "phone" not in data:
        return jsonify({"error": "Falta el campo 'phone' indispensable para el registro"}), 400

    user = UserService.register_from_whatsapp(data)
    
    if not user:
        return jsonify({"error": "No se pudo procesar el registro del usuario"}), 500
        
    return jsonify(user_schema.dump(user)), 201


@user_bp.route("/", methods=["GET"])
def get_users():

    users = UserService.get_all()
    return jsonify(users_schema.dump(users)), 200


@user_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "Email y password son requeridos"}), 400

    user = UserService.login(
        data["email"],
        data["password"]
    )

    if not user:

        return jsonify({"error": "Credenciales inválidas o acceso no autorizado"}), 401

    return jsonify(user_schema.dump(user)), 200