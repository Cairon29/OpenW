from flask import request, jsonify
from .service import UsuariosService
from backend.schemas.user_dto import user_schema, users_schema


class UsuariosController:

    @staticmethod
    def register_user():
        data = request.get_json()

        if not data or "phone" not in data:
            return jsonify({"error": "Falta el campo 'phone' indispensable para el registro"}), 400

        user = UsuariosService.register_from_whatsapp(data)

        if not user:
            return jsonify({"error": "No se pudo procesar el registro del usuario"}), 500

        return jsonify(user_schema.dump(user)), 201

    @staticmethod
    def get_users():
        users = UsuariosService.get_all()
        return jsonify(users_schema.dump(users)), 200

    @staticmethod
    def login():
        data = request.get_json()

        if not data or "email" not in data or "password" not in data:
            return jsonify({"error": "Email y password son requeridos"}), 400

        user = UsuariosService.login(data["email"], data["password"])

        if not user:
            return jsonify({"error": "Credenciales inválidas o acceso no autorizado"}), 401

        return jsonify(user_schema.dump(user)), 200
