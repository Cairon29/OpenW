from flask import Blueprint, request, jsonify
from services.Categoria_service import CategoriaService
from schemas.categoria_dto import categoria_schema, categorias_schema
from marshmallow import ValidationError

categorias_bp = Blueprint('categorias', __name__)

@categorias_bp.route('/categorias', methods=['POST'])
def crear():
    json_data = request.get_json()
    try:
   
        data = categoria_schema.load(json_data)
        
        categoria, error = CategoriaService.crear_categoria(data)
        
        if error:
            return jsonify({"error": error}), 400
            
        return jsonify(categoria_schema.dump(categoria)), 201
        
    except ValidationError as err:
        return jsonify(err.messages), 400

@categorias_bp.route('/categorias', methods=['GET'])
def listar():
    items = CategoriaService.obtener_todas()
    return jsonify(categorias_schema.dump(items)), 200