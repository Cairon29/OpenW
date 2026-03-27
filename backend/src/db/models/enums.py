import enum


class SeveridadEnum(str, enum.Enum):
    CRITICA  = "critica"
    ALTA     = "alta"
    MEDIA    = "media"
    BAJA     = "baja"
    INFO     = "informativa"


class EstadoEnum(str, enum.Enum):
    ABIERTA     = "abierta"
    EN_PROCESO  = "en_proceso"
    RESUELTA    = "resuelta"
    DESCARTADA  = "descartada"
