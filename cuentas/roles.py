"""Perfiles de usuario del sistema.

Cada perfil es un Grupo de Django con permisos diferenciados
(ver el comando: python manage.py crear_roles).
"""

ADMINISTRADOR = "Administrador"
SUPERVISOR = "Supervisor"
ADMINISTRATIVO = "Administrativo"

# Ordenados de mayor a menor nivel de acceso
ROLES = [ADMINISTRADOR, SUPERVISOR, ADMINISTRATIVO]


def obtener_rol(usuario):
    """Devuelve el perfil del usuario autenticado, o None si no tiene uno."""
    if not usuario.is_authenticated:
        return None
    if usuario.is_superuser:
        return ADMINISTRADOR
    grupos = set(usuario.groups.values_list("name", flat=True))
    for rol in ROLES:
        if rol in grupos:
            return rol
    return None
