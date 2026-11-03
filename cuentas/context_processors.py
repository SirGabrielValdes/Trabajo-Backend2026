from .roles import obtener_rol


def rol_usuario(request):
    """Deja disponible el perfil del usuario en todas las plantillas."""
    return {"rol_usuario": obtener_rol(request.user)}
