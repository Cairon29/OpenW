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

class RoleMensajeEnum(str, enum.Enum):
    USER = "user"
    BOT  = "bot"


class OnboardingStepEnum(str, enum.Enum):
    BIENVENIDA               = "bienvenida"
    PENDING_EMAIL             = "pending_email"
    PENDING_VERIFICATION      = "pending_verification"
    PENDING_VICEPRESIDENCIA   = "pending_vicepresidencia"
    PENDING_DIRECCION         = "pending_direccion"
    PENDING_NOVEDAD           = "pending_novedad"
    PENDING_CONFIRMACION      = "pending_confirmacion"
    COMPLETED                 = "completed"
    EXPIRED                   = "expired"
