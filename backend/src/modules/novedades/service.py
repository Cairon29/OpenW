from src.extensions import db
from src.db.models import Novedad, CategoriaNovedad, SeveridadEnum, EstadoEnum
from datetime import datetime, timezone


class NovedadService:

    @staticmethod
    def get_all_novedades():
        return Novedad.query.order_by(Novedad.fecha_registro.desc()).all()

    @staticmethod
    def create_novedad(titulo, descripcion, severidad, estado=None, categoria_id=None, user_email=None):
        """Crea una novedad manualmente desde el dashboard."""
        sev = SeveridadEnum(severidad) if severidad else SeveridadEnum.MEDIA
        est = EstadoEnum(estado) if estado else EstadoEnum.ABIERTA
        novedad = Novedad(
            titulo=titulo,
            descripcion=descripcion,
            severidad=sev,
            estado=est,
            fk_id_categoria=categoria_id,
            fk_email_usuario=user_email,
            fecha_registro=datetime.now(timezone.utc),
        )
        db.session.add(novedad)
        db.session.commit()
        return novedad

    @staticmethod
    def get_dashboard_metrics():
        """Calcula metricas reales del dashboard desde la tabla novedades."""
        from sqlalchemy import func, cast, Date
        from datetime import date, timedelta

        today = date.today()

        total = Novedad.query.count()
        open_cases = Novedad.query.filter_by(estado=EstadoEnum.ABIERTA).count()
        resolved_today = Novedad.query.filter(
            Novedad.estado == EstadoEnum.RESUELTA,
            cast(Novedad.fecha_registro, Date) == today,
        ).count()
        critical_open = Novedad.query.filter(
            Novedad.severidad == SeveridadEnum.CRITICA,
            Novedad.estado == EstadoEnum.ABIERTA,
        ).count()

        by_severity = {}
        for sev in SeveridadEnum:
            by_severity[sev.value] = Novedad.query.filter_by(severidad=sev).count()

        by_status = {}
        for est in EstadoEnum:
            by_status[est.value] = Novedad.query.filter_by(estado=est).count()

        recent_trend = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            count = Novedad.query.filter(
                cast(Novedad.fecha_registro, Date) == day
            ).count()
            recent_trend.append({"date": day.strftime("%b %d"), "count": count})

        return {
            "totalCases": total,
            "openCases": open_cases,
            "resolvedToday": resolved_today,
            "criticalOpen": critical_open,
            "bySeverity": by_severity,
            "byStatus": by_status,
            "recentTrend": recent_trend,
        }
