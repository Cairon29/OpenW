"""
VirusTotal Controller
Exposes two endpoints:
  POST /scan       → submit URLs from a message for async analysis
  GET  /results    → list stored scan results (paginated)
"""

import re
from flask import request, jsonify
from src.workers.security_worker import analyze_urls_async
from src.db.models.scan_result import ScanResult
from src.extensions import db

_URL_REGEX = re.compile(r"https?://[^\s]+")


def _extract_urls(text: str) -> list[str]:
    """Safe, non-executing URL extractor using regex only."""
    return _URL_REGEX.findall(text)


def handle_scan():
    """
    POST /api/v1/virustotal/scan
    Body: { "message": "<text with URLs>", "message_id": <optional int> }
    Returns immediately with a task_id (non-blocking).
    """
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")
    message_id = data.get("message_id")

    urls = _extract_urls(message)

    if not urls:
        return jsonify({"error": "No URLs found in message"}), 400

    thread = analyze_urls_async(message_id, urls)

    return jsonify({
        "status":     "queued",
        "task_id":    str(id(thread)),
        "urls_found": urls,
    }), 202


def handle_get_results():
    """
    GET /api/v1/virustotal/results?page=1&per_page=20&status=malicious
    Returns stored scan results, newest first.
    """
    page        = request.args.get("page", 1, type=int)
    per_page    = min(request.args.get("per_page", 20, type=int), 100)
    status_filter = request.args.get("status")

    query = ScanResult.query.order_by(ScanResult.created_at.desc())
    if status_filter:
        query = query.filter_by(status=status_filter)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "total":    pagination.total,
        "page":     page,
        "per_page": per_page,
        "results":  [r.to_dict() for r in pagination.items],
    }), 200
