from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "cuentas"

urlpatterns = [
    path("login/", views.IniciarSesionView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("panel/", views.panel, name="panel"),
    # Recuperación de contraseña por correo
    path("recuperar/", views.RecuperarClaveView.as_view(), name="recuperar"),
    path("recuperar/enviado/", views.RecuperarEnviadoView.as_view(), name="recuperar_enviado"),
    path("recuperar/<uidb64>/<token>/", views.NuevaClaveView.as_view(), name="recuperar_confirmar"),
    path("recuperar/completado/", views.RecuperarCompletadoView.as_view(), name="recuperar_completado"),
    # Gestión de usuarios
    path("usuarios/", views.usuarios, name="usuarios"),
    path("usuarios/agregar/", views.usuario_crear, name="usuario_crear"),
    path("usuarios/<int:pk>/modificar/", views.usuario_modificar, name="usuario_modificar"),
    path("usuarios/<int:pk>/eliminar/", views.usuario_eliminar, name="usuario_eliminar"),
]
