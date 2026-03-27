from flask import request, jsonify
from marshmallow import ValidationError
from .service import VicepresidenciaService
from src.db.schemas.vicepresidencia_dto import vicepresidencia_schema, vicepresidencias_schema


class VicepresidenciaController:

    @staticmethod
    def crear_vp():
        try:
            data = vicepresidencia_schema.load(request.get_json())
            nueva_vp, error = VicepresidenciaService.crear(data)

            if error:
                return jsonify({"error": error}), 400

            return jsonify(vicepresidencia_schema.dump(nueva_vp)), 201
        except ValidationError as err:
            return jsonify(err.messages), 400

    @staticmethod
    def listar_vps():
        vps = VicepresidenciaService.obtener_todas()
        return jsonify(vicepresidencias_schema.dump(vps)), 200
