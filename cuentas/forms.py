from django.contrib.auth.forms import AuthenticationForm

from zonaocio.formularios import FormularioBootstrap


class LoginForm(FormularioBootstrap, AuthenticationForm):
    """Formulario de inicio de sesión (usuario y contraseña) con estilos Bootstrap."""
