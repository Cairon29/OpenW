"""
VirusTotal Service
Handles communication with the VirusTotal v3 API.
- Submits URLs for scanning
- Retrieves analysis results
- Classifies results as safe / suspicious / malicious

API key resolution order:
  1. DB setting  → external.virustotal_api_key  (configurable from UI)
  2. Env var     → VIRUSTOTAL_API_KEY            (fallback / dev)
"""

import time
import requests
from src.config import config

_BASE = "https://www.virustotal.com/api/v3"

_POLL_INTERVAL = 2   # seconds between retries
_POLL_RETRIES  = 5   # max attempts before giving up


# ─── API key resolution ───────────────────────────────────────────────────────

def _get_api_key() -> str:
    """
    Returns the active VirusTotal API key.
    Tries the DB-stored config first (allows UI updates without restart),
    then falls back to the environment variable.
    """
    try:
        from src.modules.configuracion.service import ConfiguracionService
        db_key = ConfiguracionService.get_value("external.virustotal_api_key")
        if db_key:
            return db_key
    except Exception:
        pass  # no app context or DB unavailable → fall through to env var

    return config.VIRUSTOTAL_API_KEY


# ─── Public interface ─────────────────────────────────────────────────────────

def scan_url(url: str) -> dict:
    """
    Submit a URL to VirusTotal and return a classified result dict:
    {
        "url":    <str>,
        "status": "safe" | "suspicious" | "malicious",
        "stats":  { ... }
    }
    Polls until the analysis is completed (up to _POLL_RETRIES attempts).
    """
    api_key = _get_api_key()
    headers = {"x-apikey": api_key}

    analysis_id = _submit_url(url, headers)
    return _poll_analysis(url, analysis_id, headers)


# ─── Internal helpers ─────────────────────────────────────────────────────────

def _submit_url(url: str, headers: dict) -> str:
    """POST a URL to VT and return the analysis ID."""
    response = requests.post(
        f"{_BASE}/urls",
        headers=headers,
        data={"url": url},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()["data"]["id"]


def _poll_analysis(url: str, analysis_id: str, headers: dict) -> dict:
    """
    Poll VT until the analysis status is 'completed' or retries are exhausted.
    Returns the classified result dict.
    """
    for attempt in range(1, _POLL_RETRIES + 1):
        response = requests.get(
            f"{_BASE}/analyses/{analysis_id}",
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()

        data       = response.json()
        attributes = data["data"]["attributes"]
        vt_status  = attributes.get("status", "")

        if vt_status == "completed":
            stats  = attributes["stats"]
            status = _classify(stats)
            return {
                "url":    url,
                "status": status,
                "stats":  stats,
                "raw":    data,
            }

        # Analysis not ready yet — wait and retry
        if attempt < _POLL_RETRIES:
            time.sleep(_POLL_INTERVAL)

    # Final attempt timed out: return whatever stats we have
    stats  = data["data"]["attributes"].get("stats", {})
    return {
        "url":    url,
        "status": _classify(stats),
        "stats":  stats,
        "raw":    data,
    }


def _classify(stats: dict) -> str:
    """
    Classify a VT stats dict:
      - malicious  → at least one engine flagged it malicious
      - suspicious → at least one engine flagged it suspicious
      - safe       → no threats detected
    """
    if stats.get("malicious", 0) > 0:
        return "malicious"
    if stats.get("suspicious", 0) > 0:
        return "suspicious"
    return "safe"
