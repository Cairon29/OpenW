from flask import request, jsonify
from .service import AuthService


class AuthController:

    @staticmethod
    def verify_email():
        data = request.get_json(silent=True)
        token = (data.get("token") if data else None) or request.args.get("token")

        if not token:
            return jsonify({"error": "token requerido"}), 400

        success = AuthService.verify_email(token)
        if success:
            return jsonify({"status": "verified"}), 200
        return jsonify({"error": "Token invalido o expirado"}), 400
