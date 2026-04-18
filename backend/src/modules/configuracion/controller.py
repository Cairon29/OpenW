from flask import request, jsonify
from .service import ConfiguracionService

TESTERS = {
    "whatsapp":   ConfiguracionService.test_whatsapp,
    "email":      ConfiguracionService.test_email,
    "virustotal": ConfiguracionService.test_virustotal,
    "deepseek":   ConfiguracionService.test_deepseek,
}


class ConfiguracionController:

    @staticmethod
    def listar():
        category = request.args.get("category")
        items = ConfiguracionService.get_all(category=category)
        grouped = {}
        for cfg in items:
            grouped.setdefault(cfg.category, []).append(cfg.to_dict())
        return jsonify(grouped), 200

    @staticmethod
    def obtener(key):
        cfg = ConfiguracionService.get_by_key(key)
        if not cfg:
            return jsonify({"error": "No encontrada"}), 404
        return jsonify(cfg.to_dict()), 200

    @staticmethod
    def actualizar(key):
        data = request.get_json(silent=True) or {}
        value = data.get("value")
        if value is None:
            return jsonify({"error": "Se requiere el campo 'value'"}), 400
        updated_by = data.get("updated_by")
        cfg, error = ConfiguracionService.update(key, str(value), updated_by)
        if error:
            return jsonify({"error": error}), 400 if "no encontrada" in error.lower() else 500
        return jsonify(cfg.to_dict()), 200

    @staticmethod
    def bulk_actualizar():
        data = request.get_json(silent=True) or {}
        items = data.get("items", [])
        updated_by = data.get("updated_by")
        if not items:
            return jsonify({"error": "Se requiere la lista 'items'"}), 400
        updated, error = ConfiguracionService.bulk_update(items, updated_by)
        if error:
            return jsonify({"error": error}), 500
        return jsonify({"updated": len(updated), "items": [c.to_dict() for c in updated]}), 200

    @staticmethod
    def test_conexion(service):
        tester = TESTERS.get(service)
        if not tester:
            return jsonify({"error": f"Servicio '{service}' no soportado. Opciones: {list(TESTERS.keys())}"}), 400
        ok, message = tester()
        return jsonify({"service": service, "ok": ok, "message": message}), 200
