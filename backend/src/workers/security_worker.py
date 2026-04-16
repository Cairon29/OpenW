"""
Security Worker (threading-based)
Procesa URLs en background usando threading estándar de Python
— sin Redis ni Celery, cero dependencias externas.

Uso:
    from src.workers.security_worker import analyze_urls_async
    analyze_urls_async(message_id, urls)   # no bloquea
"""

import threading
import logging

logger = logging.getLogger(__name__)


def analyze_urls_async(message_id, urls: list[str]):
    """
    Lanza el análisis de URLs en un hilo separado (non-blocking).
    Devuelve el thread para quien quiera hacer .join().
    """
    t = threading.Thread(
        target=_run_analysis,
        args=(message_id, urls),
        daemon=True,
    )
    t.start()
    return t


# ─── Internal ────────────────────────────────────────────────────────────────

def _run_analysis(message_id, urls: list[str]):
    """
    Se ejecuta en hilo separado.
    Importa el app context aquí para no contaminar el hilo principal.
    """
    from src.app import create_app
    from src.modules.virus_total.service import scan_url
    from src.db.models.scan_result import ScanResult
    from src.extensions import db

    app = create_app()

    with app.app_context():
        for url in urls:
            try:
                result = scan_url(url)

                record = ScanResult(
                    message_id=message_id,
                    url=url,
                    status=result["status"],
                    raw_json=result["raw"],
                )
                db.session.add(record)
                db.session.commit()

                logger.info(
                    "✅ Scanned url=%s  status=%s  message_id=%s",
                    url, result["status"], message_id,
                )

            except Exception as exc:
                logger.error("❌ Error scanning url=%s: %s", url, exc)
                db.session.rollback()
