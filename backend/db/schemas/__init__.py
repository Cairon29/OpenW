from .categoria_dto import categoria_schema, categorias_schema
from .novedad_dto import novedad_schema, novedades_schema
from .user_dto import user_schema, users_schema
from .vicepresidencia_dto import vicepresidencia_schema, vicepresidencias_schema
from .direccion_dto import direccion_schema, direcciones_schema
from .ia_model_dto import ia_model_schema, ia_models_schema
from .configuracion_dto import configuracion_schema, configuraciones_schema

__all__ = [
    'categoria_schema', 'categorias_schema',
    'novedad_schema', 'novedades_schema',
    'user_schema', 'users_schema',
    'vicepresidencia_schema', 'vicepresidencias_schema',
    'direccion_schema', 'direcciones_schema',
    'ia_model_schema', 'ia_models_schema',
    'configuracion_schema', 'configuraciones_schema',
]
