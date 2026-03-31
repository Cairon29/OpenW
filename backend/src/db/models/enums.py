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
    PENDING_EMAIL        = "pending_email"
    PENDING_VERIFICATION = "pending_verification"
    VERIFIED             = "verified"
    EXPIRED              = "expired"
