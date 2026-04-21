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

    @staticmethod
    def get_novedades_por_vicepresidencia():
        from sqlalchemy import func
        from src.db.models.direccion import Direccion
        from src.db.models.vicepresidencia import Vicepresidencia

        rows = (
            db.session.query(
                Vicepresidencia.id,
                Vicepresidencia.nombre.label("vicepresidencia"),
                Direccion.id.label("id_direccion"),
                Direccion.nombre.label("direccion"),
                func.count(Novedad.id).label("total"),
            )
            .join(Direccion, Direccion.fk_id_vicepresidencia == Vicepresidencia.id)
            .outerjoin(Novedad, Novedad.fk_id_direccion == Direccion.id)
            .group_by(
                Vicepresidencia.id,
                Vicepresidencia.nombre,
                Direccion.id,
                Direccion.nombre,
            )
            .order_by(Vicepresidencia.nombre, Direccion.nombre)
            .all()
        )

        result = {}
        for vp_id, vp_nombre, dir_id, dir_nombre, total in rows:
            if vp_id not in result:
                result[vp_id] = {
                    "id_vicepresidencia": vp_id,
                    "vicepresidencia": vp_nombre,
                    "total": 0,
                    "direcciones": [],
                }
            result[vp_id]["total"] += total
            result[vp_id]["direcciones"].append({
                "id_direccion": dir_id,
                "direccion": dir_nombre,
                "total": total,
            })

        return sorted(result.values(), key=lambda x: x["total"], reverse=True)

    @staticmethod
    def get_novedades_detalle_vicepresidencia(vp_id):
        from collections import defaultdict
        from src.db.models.direccion import Direccion
        from src.db.models.vicepresidencia import Vicepresidencia

        vp = Vicepresidencia.query.get(vp_id)
        if not vp:
            return None

        direcciones = (
            Direccion.query
            .filter_by(fk_id_vicepresidencia=vp_id)
            .order_by(Direccion.nombre)
            .all()
        )

        dir_ids = [d.id for d in direcciones]
        novedades = (
            Novedad.query
            .filter(Novedad.fk_id_direccion.in_(dir_ids))
            .order_by(Novedad.fk_id_direccion, Novedad.fecha_creacion.desc())
            .all()
        ) if dir_ids else []

        nov_by_dir = defaultdict(list)
        for n in novedades:
            nov_by_dir[n.fk_id_direccion].append({
                "id_novedad": n.id,
                "email_creador": n.fk_email_usuario,
                "fecha_creacion": n.fecha_creacion.strftime("%d/%m/%Y") if n.fecha_creacion else None,
                "estado": n.estado.value if n.estado else None,
                "titulo": n.titulo,
            })

        total = 0
        dir_list = []
        for d in direcciones:
            novs = nov_by_dir.get(d.id, [])
            total += len(novs)
            dir_list.append({
                "id_direccion": d.id,
                "direccion": d.nombre,
                "total": len(novs),
                "novedades": novs,
            })

        return {
            "id_vicepresidencia": vp.id,
            "vicepresidencia": vp.nombre,
            "total": total,
            "direcciones": dir_list,
        }
