import os
import json
import smtplib
import requests
from datetime import datetime, timezone

from src.extensions import db
from src.db.models.system_config import SystemConfig


# ── Default configurations (seeded on first run) ─────────────────────────────

DEFAULTS = [
    # ── General ──────────────────────────────────────────────────────────────
    {
        "key": "general.system_name",
        "value": "OpenW Security",
        "value_type": "string",
        "category": "general",
        "label": "Nombre del sistema",
        "description": "Nombre del sistema que aparece en la interfaz y comunicaciones.",
        "is_sensitive": False,
    },
    {
        "key": "general.organization_name",
        "value": "Fiduprevisora",
        "value_type": "string",
        "category": "general",
        "label": "Nombre de la organización",
        "description": "Nombre de la organización mostrado en reportes y correos.",
        "is_sensitive": False,
    },
    {
        "key": "general.session_timeout_minutes",
        "value": "3",
        "value_type": "number",
        "category": "general",
        "label": "Timeout de sesión (minutos)",
        "description": "Tiempo máximo de inactividad antes de expirar una conversación de WhatsApp.",
        "is_sensitive": False,
    },
    {
        "key": "general.frontend_url",
        "value": os.getenv("FRONTEND_URL", "http://localhost:1111"),
        "value_type": "string",
        "category": "general",
        "label": "URL del frontend",
        "description": "URL base del dashboard (usada en links de correos de verificación).",
        "is_sensitive": False,
    },

    # ── WhatsApp ──────────────────────────────────────────────────────────────
    {
        "key": "whatsapp.access_token",
        "value": os.getenv("WHATSAPP_ACCESS_TOKEN", ""),
        "value_type": "string",
        "category": "whatsapp",
        "label": "Access Token",
        "description": "Token de acceso a la API de WhatsApp Cloud de Meta (se renueva cada 24h en entornos de prueba).",
        "is_sensitive": True,
    },
    {
        "key": "whatsapp.phone_number_id",
        "value": os.getenv("WHATSAPP_PHONE_NUMBER_ID", ""),
        "value_type": "string",
        "category": "whatsapp",
        "label": "Phone Number ID",
        "description": "ID del número de teléfono registrado en Meta Business.",
        "is_sensitive": False,
    },
    {
        "key": "whatsapp.business_account_id",
        "value": os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID", ""),
        "value_type": "string",
        "category": "whatsapp",
        "label": "Business Account ID",
        "description": "ID de la cuenta de negocio en Meta.",
        "is_sensitive": False,
    },
    {
        "key": "whatsapp.app_id",
        "value": os.getenv("WHATSAPP_APP_ID", ""),
        "value_type": "string",
        "category": "whatsapp",
        "label": "App ID",
        "description": "ID de la aplicación de Meta.",
        "is_sensitive": False,
    },
    {
        "key": "whatsapp.verify_token",
        "value": os.getenv("WHATSAPP_VERIFY_TOKEN", ""),
        "value_type": "string",
        "category": "whatsapp",
        "label": "Verify Token (Webhook)",
        "description": "Token de verificación del webhook configurado en Meta.",
        "is_sensitive": True,
    },
    {
        "key": "whatsapp.app_secret",
        "value": os.getenv("WHATSAPP_APP_SECRET", ""),
        "value_type": "string",
        "category": "whatsapp",
        "label": "App Secret",
        "description": "Secreto de la app de Meta, usado para validar firmas HMAC de los webhooks.",
        "is_sensitive": True,
    },

    # ── Email ─────────────────────────────────────────────────────────────────
    {
        "key": "email.gmail_user",
        "value": os.getenv("GMAIL_USER", ""),
        "value_type": "string",
        "category": "email",
        "label": "Usuario Gmail (SMTP)",
        "description": "Dirección de correo de Gmail usada para enviar verificaciones.",
        "is_sensitive": False,
    },
    {
        "key": "email.gmail_app_password",
        "value": os.getenv("GMAIL_APP_PASSWORD", ""),
        "value_type": "string",
        "category": "email",
        "label": "Contraseña de aplicación Gmail",
        "description": "Contraseña de aplicación generada en la cuenta de Google (no es la contraseña normal).",
        "is_sensitive": True,
    },
    {
        "key": "email.allowed_domain",
        "value": os.getenv("ALLOWED_EMAIL_DOMAIN", ""),
        "value_type": "string",
        "category": "email",
        "label": "Dominio de email corporativo",
        "description": "Solo se aceptarán correos de este dominio (ej: fiduprevisora.com).",
        "is_sensitive": False,
    },

    # ── Analysis ──────────────────────────────────────────────────────────────
    {
        "key": "analysis.auto_classify",
        "value": "true",
        "value_type": "boolean",
        "category": "analysis",
        "label": "Clasificación automática",
        "description": "Cuando está activo, el sistema clasifica automáticamente la categoría de cada novedad usando palabras clave.",
        "is_sensitive": False,
    },
    {
        "key": "analysis.ai_validation",
        "value": "true",
        "value_type": "boolean",
        "category": "analysis",
        "label": "Validación con IA",
        "description": "Usa IA (Deepseek) como fallback para validar entradas del usuario en el chat de WhatsApp.",
        "is_sensitive": False,
    },
    {
        "key": "analysis.critical_keywords",
        "value": json.dumps(["ransomware", "cifrado", "exfiltración", "backdoor", "zero-day", "brecha", "compromiso"]),
        "value_type": "json",
        "category": "analysis",
        "label": "Palabras clave de criticidad",
        "description": "Lista de términos que elevan automáticamente una novedad a severidad CRÍTICA.",
        "is_sensitive": False,
    },
    {
        "key": "analysis.high_keywords",
        "value": json.dumps(["phishing", "malware", "intrusión", "acceso no autorizado", "escalada de privilegios"]),
        "value_type": "json",
        "category": "analysis",
        "label": "Palabras clave de severidad Alta",
        "description": "Lista de términos que clasifican una novedad como severidad ALTA.",
        "is_sensitive": False,
    },

    # ── Modules ───────────────────────────────────────────────────────────────
    {
        "key": "modules.bot_enabled",
        "value": "true",
        "value_type": "boolean",
        "category": "modules",
        "label": "Bot de WhatsApp",
        "description": "Activa o desactiva globalmente el bot de WhatsApp. Cuando está desactivado, los mensajes entrantes son ignorados.",
        "is_sensitive": False,
    },
    {
        "key": "modules.email_notifications",
        "value": "true",
        "value_type": "boolean",
        "category": "modules",
        "label": "Notificaciones por correo",
        "description": "Activa o desactiva el envío de correos de verificación de email.",
        "is_sensitive": False,
    },
    {
        "key": "modules.embeddings",
        "value": "true",
        "value_type": "boolean",
        "category": "modules",
        "label": "Embeddings semánticos",
        "description": "Activa la generación de embeddings vectoriales para búsqueda semántica en conversaciones.",
        "is_sensitive": False,
    },

    # ── External APIs ─────────────────────────────────────────────────────────
    {
        "key": "external.virustotal_enabled",
        "value": "false",
        "value_type": "boolean",
        "category": "external_apis",
        "label": "VirusTotal habilitado",
        "description": "Activa el análisis automático de archivos/URLs adjuntas a novedades usando VirusTotal.",
        "is_sensitive": False,
    },
    {
        "key": "external.virustotal_api_key",
        "value": "",
        "value_type": "string",
        "category": "external_apis",
        "label": "API Key de VirusTotal",
        "description": "Clave de API de VirusTotal para escaneo de indicadores.",
        "is_sensitive": True,
    },
    {
        "key": "external.deepseek_api_key",
        "value": os.getenv("DEEPSEEK_API_KEY", ""),
        "value_type": "string",
        "category": "external_apis",
        "label": "API Key de Deepseek",
        "description": "Clave de API de Deepseek utilizada para validación inteligente de entradas.",
        "is_sensitive": True,
    },
]


class ConfiguracionService:

    # ── Read ──────────────────────────────────────────────────────────────────

    @staticmethod
    def get_all(category: str = None):
        query = SystemConfig.query.filter_by(is_active=True)
        if category:
            query = query.filter_by(category=category)
        return query.order_by(SystemConfig.category, SystemConfig.key).all()

    @staticmethod
    def get_by_key(key: str) -> SystemConfig | None:
        return SystemConfig.query.filter_by(key=key, is_active=True).first()

    @staticmethod
    def get_value(key: str, default=None):
        """Quick helper to get a config value as a plain Python object."""
        cfg = SystemConfig.query.filter_by(key=key, is_active=True).first()
        if not cfg or cfg.value is None:
            return default
        if cfg.value_type == "boolean":
            return cfg.value.lower() in ("true", "1", "yes")
        if cfg.value_type == "number":
            try:
                return float(cfg.value) if "." in cfg.value else int(cfg.value)
            except (ValueError, TypeError):
                return default
        if cfg.value_type == "json":
            try:
                return json.loads(cfg.value)
            except (ValueError, TypeError):
                return default
        return cfg.value

    # ── Write ─────────────────────────────────────────────────────────────────

    @staticmethod
    def update(key: str, value: str, updated_by: str = None):
        cfg = SystemConfig.query.filter_by(key=key).first()
        if not cfg:
            return None, "Configuración no encontrada."
        cfg.value = value
        cfg.updated_at = datetime.now(timezone.utc)
        cfg.updated_by = updated_by
        try:
            db.session.commit()
            return cfg, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def bulk_update(items: list, updated_by: str = None):
        """items: [{"key": str, "value": str}, ...]"""
        updated = []
        for item in items:
            cfg = SystemConfig.query.filter_by(key=item["key"]).first()
            if cfg:
                cfg.value = item["value"]
                cfg.updated_at = datetime.now(timezone.utc)
                cfg.updated_by = updated_by
                updated.append(cfg)
        try:
            db.session.commit()
            return updated, None
        except Exception as e:
            db.session.rollback()
            return [], str(e)

    # ── Seed ──────────────────────────────────────────────────────────────────

    @staticmethod
    def seed_defaults():
        """Insert default configs that don't exist yet."""
        for item in DEFAULTS:
            exists = SystemConfig.query.filter_by(key=item["key"]).first()
            if not exists:
                cfg = SystemConfig(**item)
                db.session.add(cfg)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()

    # ── Connection tests ──────────────────────────────────────────────────────

    @staticmethod
    def test_whatsapp():
        token = ConfiguracionService.get_value("whatsapp.access_token")
        phone_id = ConfiguracionService.get_value("whatsapp.phone_number_id")
        if not token or not phone_id:
            return False, "Credenciales de WhatsApp no configuradas."
        try:
            resp = requests.get(
                f"https://graph.facebook.com/v22.0/{phone_id}",
                params={"access_token": token},
                timeout=8,
            )
            if resp.status_code == 200:
                data = resp.json()
                return True, f"Conectado · Número: {data.get('display_phone_number', phone_id)}"
            return False, f"Error {resp.status_code}: {resp.json().get('error', {}).get('message', 'desconocido')}"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def test_email():
        user = ConfiguracionService.get_value("email.gmail_user")
        password = ConfiguracionService.get_value("email.gmail_app_password")
        if not user or not password:
            return False, "Credenciales de email no configuradas."
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=8) as smtp:
                smtp.login(user, password)
            return True, f"Conectado como {user}"
        except smtplib.SMTPAuthenticationError:
            return False, "Credenciales incorrectas."
        except Exception as e:
            return False, str(e)

    @staticmethod
    def test_virustotal():
        api_key = ConfiguracionService.get_value("external.virustotal_api_key")
        if not api_key:
            return False, "API Key de VirusTotal no configurada."
        try:
            resp = requests.get(
                "https://www.virustotal.com/api/v3/ip_addresses/8.8.8.8",
                headers={"x-apikey": api_key},
                timeout=8,
            )
            if resp.status_code == 200:
                return True, "API Key válida · VirusTotal conectado."
            return False, f"Error {resp.status_code}: API Key inválida o límite alcanzado."
        except Exception as e:
            return False, str(e)

    @staticmethod
    def test_deepseek():
        api_key = ConfiguracionService.get_value("external.deepseek_api_key")
        if not api_key:
            return False, "API Key de Deepseek no configurada."
        try:
            resp = requests.get(
                "https://api.deepseek.com/user/balance",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=8,
            )
            if resp.status_code == 200:
                data = resp.json()
                balance = data.get("balance_infos", [{}])[0].get("total_balance", "?")
                return True, f"Conectado · Balance: {balance} USD"
            return False, f"Error {resp.status_code}: API Key inválida."
        except Exception as e:
            return False, str(e)
