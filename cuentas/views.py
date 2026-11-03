from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .forms import LoginForm
from .roles import obtener_rol


class IniciarSesionView(auth_views.LoginView):
    """Ingreso mediante usuario y contraseña."""

    template_name = "cuentas/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True


@login_required
def panel(request):
    """Panel principal del usuario autenticado."""
    return render(request, "cuentas/panel.html", {"rol": obtener_rol(request.user)})
