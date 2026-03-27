from flask import request, jsonify
from marshmallow import ValidationError
from .service import CategoriasService
from src.db.schemas.categoria_dto import categoria_schema, categorias_schema


class CategoriasController:

    @staticmethod
    def crear():
        json_data = request.get_json()
        try:
            data = categoria_schema.load(json_data)
            categoria, error = CategoriasService.crear_categoria(data)

            if error:
                return jsonify({"error": error}), 400

            return jsonify(categoria_schema.dump(categoria)), 201
        except ValidationError as err:
            return jsonify(err.messages), 400

    @staticmethod
    def listar():
        items = CategoriasService.obtener_todas()
        return jsonify(categorias_schema.dump(items)), 200
