from src.extensions import db
from datetime import datetime, timezone


class SystemConfig(db.Model):
    __tablename__ = 'system_config'

    id          = db.Column(db.Integer, primary_key=True)
    key         = db.Column(db.String(100), unique=True, nullable=False)
    value       = db.Column(db.Text, nullable=True)
    value_type  = db.Column(db.String(20), nullable=False, default='string')
    # string | number | boolean | json

    category    = db.Column(db.String(50), nullable=False)
    # general | whatsapp | email | analysis | modules | external_apis

    label       = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_sensitive = db.Column(db.Boolean, default=False, nullable=False)
    is_active   = db.Column(db.Boolean, default=True, nullable=False)
    updated_at  = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    updated_by  = db.Column(db.String(100), nullable=True)

    def to_dict(self, reveal_sensitive=False):
        value = self.value
        if self.is_sensitive and not reveal_sensitive and value:
            # Show only last 4 chars masked
            visible = value[-4:] if len(value) >= 4 else value
            value = f"{'*' * (len(value) - len(visible))}{visible}"

        return {
            "id":           self.id,
            "key":          self.key,
            "value":        value,
            "value_type":   self.value_type,
            "category":     self.category,
            "label":        self.label,
            "description":  self.description,
            "is_sensitive": self.is_sensitive,
            "is_active":    self.is_active,
            "updated_at":   self.updated_at.isoformat() if self.updated_at else None,
            "updated_by":   self.updated_by,
        }
