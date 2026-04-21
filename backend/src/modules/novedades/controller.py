from flask import request, jsonify
from .service import NovedadService
from src.db.schemas.novedad_dto import novedad_schema, novedades_schema


class NovedadesController:
    # -- Novedades (casos) --

    @staticmethod
    def listar_novedades():
        try:
            novedades = NovedadService.get_all_novedades()
            return jsonify(novedades_schema.dump(novedades)), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def crear_novedad():
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Body requerido"}), 400

        required_fields = ["titulo", "descripcion", "user_email", "phone", "severidad"]

        titulo = (data.get("titulo") or "").strip()
        descripcion = (data.get("descripcion") or "").strip()

        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"{field} es requerido"}), 400

        try:
            novedad = NovedadService.create_novedad(
                titulo=titulo,
                descripcion=descripcion,
                severidad=data.get("severidad"),
                estado=data.get("estado"),
                categoria_id=data.get("categoria_id"),
                user_email=data.get("user_email"),
            )
            return jsonify(novedad_schema.dump(novedad)), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def obtener_novedad(id):
        from src.db.models import Novedad
        novedad = Novedad.query.get_or_404(id)
        return jsonify(novedad_schema.dump(novedad)), 200

    # -- Dashboard --

    @staticmethod
    def dashboard_metrics():
        try:
            return jsonify(NovedadService.get_dashboard_metrics()), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
