"""
Pytest fixtures for the characterization test suite.

Design:
  - Session-scoped Flask app with TestingConfig.
  - Function-scoped db_session that wipes tables after each test.
  - Autouse fixtures silence external boundaries (embeddings, SSE events).
  - Opt-in fixtures mock WhatsApp / DeepSeek / email at every usage site.

FLASK_MODE must be set to "testing" BEFORE importing anything from `src`
because src.modules.auth.service raises at import time if
ALLOWED_EMAIL_DOMAIN is missing.
"""
import os
from pathlib import Path

# Load .env BEFORE importing src.* so Config/TestingConfig see real values.
try:
    from dotenv import load_dotenv
    _PROJECT_ROOT = Path(__file__).resolve().parents[2]
    for _candidate in [_PROJECT_ROOT / ".env", _PROJECT_ROOT.parent / ".env"]:
        if _candidate.exists():
            load_dotenv(_candidate, override=False)
            break
except ImportError:
    pass

os.environ["FLASK_MODE"] = "testing"
# Tests run from the host, not the docker network, so service names like
# "db" won't resolve. .env may set DB_HOST=db for compose — override it.
if os.environ.get("DB_HOST") in (None, "", "db"):
    os.environ["DB_HOST"] = os.environ.get("DB_HOST_TEST", "localhost")
os.environ.setdefault("DB_PORT", "5432")

import pytest

from src.app import create_app
from src.config import TestingConfig
from src.extensions import db as _db


# ── App & DB ──────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def app():
    flask_app = create_app(config_override=TestingConfig)
    with flask_app.app_context():
        yield flask_app


@pytest.fixture(autouse=True)
def db_session(app):
    """Provide a clean DB state per test: wipe all tables on teardown."""
    yield _db.session

    _db.session.rollback()
    # Truncate in dependency-safe order (children first).
    for table in reversed(_db.metadata.sorted_tables):
        _db.session.execute(table.delete())
    _db.session.commit()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db():
    return _db


# ── Mocks (external boundaries) ───────────────────────────────────────────

def _patch_symbol(monkeypatch, targets, replacement):
    """Replace `attr` on every (module_path, attr) pair in `targets`."""
    import importlib
    for module_path, attr in targets:
        module = importlib.import_module(module_path)
        monkeypatch.setattr(module, attr, replacement)


class CallRecorder:
    """Captures calls (args, kwargs) and returns a configurable value."""
    def __init__(self, return_value=None):
        self.calls = []
        self.return_value = return_value

    def __call__(self, *args, **kwargs):
        self.calls.append({"args": args, "kwargs": kwargs})
        rv = self.return_value
        return rv(*args, **kwargs) if callable(rv) else rv

    @property
    def called(self):
        return bool(self.calls)

    @property
    def call_count(self):
        return len(self.calls)

    @property
    def last_call(self):
        return self.calls[-1] if self.calls else None


@pytest.fixture(autouse=True)
def mock_embedding(monkeypatch):
    """Skip the 400MB sentence-transformers model load. get_embedding → None."""
    targets = [
        ("src.utils.embeddings", "get_embedding"),
    ]
    recorder = CallRecorder(return_value=None)
    _patch_symbol(monkeypatch, targets, recorder)
    return recorder


@pytest.fixture(autouse=True)
def capture_events(monkeypatch):
    """Replace SSE publish() with a no-op recorder so gevent queues aren't touched."""
    recorder = CallRecorder(return_value=None)
    targets = [
        ("src.modules.chat.events", "publish"),
    ]
    _patch_symbol(monkeypatch, targets, recorder)
    return recorder


@pytest.fixture
def mock_whatsapp(monkeypatch):
    """Mock WhatsApp send: returns fake wamid, captures calls at every usage site."""
    send = CallRecorder(return_value=lambda *a, **kw: f"wamid.fake.{send.call_count + 1}")
    typing = CallRecorder(return_value=None)

    _patch_symbol(monkeypatch, [
        ("src.utils.whatsapp", "enviar_whatsapp"),
        ("src.modules.auth.service", "enviar_whatsapp"),
        ("src.modules.chat.utils.dashboard", "enviar_whatsapp"),
        ("src.modules.chat.utils.phases.helpers", "enviar_whatsapp"),
    ], send)
    _patch_symbol(monkeypatch, [
        ("src.utils.whatsapp", "enviar_indicador_typing"),
    ], typing)

    class _Handle:
        send = None
        typing = None
    _Handle.send = send
    _Handle.typing = typing
    return _Handle


@pytest.fixture
def mock_template(monkeypatch):
    """Mock WhatsApp template send (Meta Cloud API)."""
    recorder = CallRecorder(return_value="wamid.template.fake")
    _patch_symbol(monkeypatch, [
        ("src.modules.chat.utils.phases.helpers", "enviar_template_whatsapp"),
        ("src.modules.chat.utils.phases.bienvenida", "enviar_template_whatsapp"),
    ], recorder)
    return recorder


@pytest.fixture
def mock_classify(monkeypatch):
    """Mock DeepSeek classification. Default: categoria None, severidad media."""
    default = {
        "titulo": "Mensaje de prueba",
        "severidad": "media",
        "categoria_obj": None,
        "respuesta_usuario": "Recibimos tu mensaje de prueba.",
    }
    recorder = CallRecorder(return_value=default)
    _patch_symbol(monkeypatch, [
        ("src.utils.classification", "classify_message"),
        ("src.modules.chat.utils.phases.pending_novedad", "classify_message"),
    ], recorder)
    return recorder


@pytest.fixture
def mock_ai_validate(monkeypatch):
    """Mock DeepSeek fallback validator. Default: is_valid=False."""
    default = {
        "is_valid": False,
        "extracted_value": None,
        "guidance_message": None,
    }
    recorder = CallRecorder(return_value=default)
    _patch_symbol(monkeypatch, [
        ("src.utils.ai_validation", "validate_input"),
        ("src.modules.chat.utils.phases.pending_email", "validate_input"),
        ("src.modules.chat.utils.phases.pending_vicepresidencia", "validate_input"),
        ("src.modules.chat.utils.phases.pending_direccion", "validate_input"),
        ("src.modules.chat.utils.phases.pending_confirmacion", "validate_input"),
    ], recorder)
    return recorder


@pytest.fixture
def mock_email(monkeypatch):
    """Mock SMTP. Default: return True (sent)."""
    recorder = CallRecorder(return_value=True)
    _patch_symbol(monkeypatch, [
        ("src.utils.email", "send_verification_email"),
        ("src.modules.chat.utils.phases.pending_email", "send_verification_email"),
    ], recorder)
    return recorder


# ── Bot state helper (tests want full control over bot_active gate) ──────

@pytest.fixture(autouse=True)
def _bot_always_on(monkeypatch):
    """Force _get_bot_state to return True unless a test overrides it."""
    monkeypatch.setattr(
        "src.modules.chat.utils.dashboard._get_bot_state",
        lambda phone: True,
    )
    monkeypatch.setattr(
        "src.modules.chat.service._get_bot_state",
        lambda phone: True,
    )
