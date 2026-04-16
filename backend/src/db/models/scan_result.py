"""
ScanResult model
Stores the VirusTotal scan result for each URL extracted from a message.

Table: scan_results
"""

from datetime import datetime, timezone
from src.extensions import db


class ScanResult(db.Model):
    __tablename__ = "scan_results"

    id          = db.Column(db.Integer, primary_key=True)
    message_id  = db.Column(db.String(255), nullable=True, index=True)  # WA message ID or numeric ID as string
    url         = db.Column(db.Text, nullable=False)
    status      = db.Column(db.String(20), nullable=False)            # safe | suspicious | malicious
    raw_json    = db.Column(db.JSON, nullable=True)
    created_at  = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id":         self.id,
            "message_id": self.message_id,
            "url":        self.url,
            "status":     self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
