import os
import json
import smtplib
import requests
from datetime import datetime, timezone
from src.extensions import db
from src.db.models.system_config import SystemConfig
from .utils.default_values import DEFAULTS

class ConfiguracionService:

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
