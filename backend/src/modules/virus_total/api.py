from flask import Blueprint
from .controller import handle_scan, handle_get_results

virus_total_bp = Blueprint("api_virus_total", __name__)

# Submit URLs for async scanning
virus_total_bp.add_url_rule("/scan",    view_func=handle_scan,        methods=["POST"])

# Query stored results
virus_total_bp.add_url_rule("/results", view_func=handle_get_results, methods=["GET"])
