from flask import Blueprint, request, jsonify
from services.vicepresidencia_service import VicepresidenciaService
from schemas.vicepresidencia_dto import vicepresidencia_schema, vicepresidencias_schema
from marshmallow import ValidationError

vp_bp = Blueprint('vicepresidencias', __name__)

@vp_bp.route('/vicepresidencias', methods=['POST'])
def crear_vp():
    try:
        data = vicepresidencia_schema.load(request.get_json())
        nueva_vp, error = VicepresidenciaService.crear(data)
        
        if error:
            return jsonify({"error": error}), 400
            
        return jsonify(vicepresidencia_schema.dump(nueva_vp)), 201
    except ValidationError as err:
        return jsonify(err.messages), 400

@vp_bp.route('/vicepresidencias', methods=['GET'])
def listar_vps():
    vps = VicepresidenciaService.obtener_todas()
    return jsonify(vicepresidencias_schema.dump(vps)), 200