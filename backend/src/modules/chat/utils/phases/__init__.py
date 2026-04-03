"""Re-export de todos los phase handlers."""

from .bienvenida import handle_bienvenida
from .pending_email import handle_pending_email
from .pending_verification import handle_pending_verification
from .pending_vicepresidencia import handle_pending_vicepresidencia
from .pending_direccion import handle_pending_direccion
from .pending_novedad import handle_pending_novedad
from .pending_confirmacion import handle_pending_confirmacion
from .completed import handle_completed
from .expired import handle_expired

__all__ = [
    "handle_bienvenida",
    "handle_pending_email",
    "handle_pending_verification",
    "handle_pending_vicepresidencia",
    "handle_pending_direccion",
    "handle_pending_novedad",
    "handle_pending_confirmacion",
    "handle_completed",
    "handle_expired",
]
