from datetime import datetime, time

from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Sum
from django.shortcuts import render
from django.utils import timezone

from peliculas.models import Pelicula
from ventas.models import Cliente, Venta
from videojuegos.models import Videojuego

from .forms import LoginForm
from .roles import ADMINISTRADOR, ADMINISTRATIVO, ROLES, SUPERVISOR, obtener_rol

# Mantenedores del sistema: (nombre, ruta del listado, app, modelo)
MANTENEDORES = [
    ("Videojuegos", "videojuegos:listado", "videojuegos", "videojuego"),
    ("Géneros de videojuegos", "videojuegos:generos", "videojuegos", "genero"),
    ("Desarrolladoras", "videojuegos:desarrolladoras", "videojuegos", "desarrolladora"),
    ("Plataformas", "videojuegos:plataformas", "videojuegos", "plataforma"),
    ("Películas", "peliculas:listado", "peliculas", "pelicula"),
    ("Géneros de películas", "peliculas:generos", "peliculas", "genero"),
    ("Directores", "peliculas:directores", "peliculas", "director"),
    ("Clasificaciones", "peliculas:clasificaciones", "peliculas", "clasificacion"),
    ("Clientes", "ventas:clientes", "ventas", "cliente"),
]

STOCK_BAJO = 3


class IniciarSesionView(auth_views.LoginView):
    """Ingreso mediante usuario y contraseña."""

    template_name = "cuentas/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True


def mantenedores_autorizados(usuario):
    """Mantenedores que el usuario puede ver, con las acciones que su perfil permite."""
    resultado = []
    for nombre, ruta, app, modelo in MANTENEDORES:
        if not usuario.has_perm(f"{app}.view_{modelo}"):
            continue
        resultado.append({
            "nombre": nombre,
            "ruta": ruta,
            "crear": usuario.has_perm(f"{app}.add_{modelo}"),
            "modificar": usuario.has_perm(f"{app}.change_{modelo}"),
            "eliminar": usuario.has_perm(f"{app}.delete_{modelo}"),
        })
    return resultado


def resumen_ventas(ventas):
    datos = ventas.aggregate(cantidad=Count("id"), monto=Sum("total"))
    monto = datos["monto"] or 0
    return {"cantidad": datos["cantidad"], "monto": "$" + f"{monto:,}".replace(",", ".")}


@login_required
def panel(request):
    """Dashboard: el contenido cambia según el perfil del usuario autenticado."""
    usuario = request.user
    rol = obtener_rol(usuario)
    inicio_hoy = timezone.make_aware(datetime.combine(timezone.localdate(), time.min))

    contexto = {
        "rol": rol,
        "mantenedores": mantenedores_autorizados(usuario),
    }

    if rol == ADMINISTRADOR:
        contexto.update({
            "totales": {
                "Videojuegos": Videojuego.objects.count(),
                "Películas": Pelicula.objects.count(),
                "Clientes": Cliente.objects.count(),
                "Usuarios activos": User.objects.filter(is_active=True).count(),
            },
            "ventas_total": resumen_ventas(Venta.objects.all()),
            "ventas_hoy": resumen_ventas(Venta.objects.filter(fecha__gte=inicio_hoy)),
            "usuarios_por_rol": [
                (nombre, User.objects.filter(groups__name=nombre).count()) for nombre in ROLES
            ],
            "ultimas_ventas": Venta.objects.select_related("cliente", "vendedor")[:5],
            "stock_bajo": Videojuego.objects.filter(stock__lte=STOCK_BAJO).order_by("stock"),
        })
        plantilla = "cuentas/panel_administrador.html"

    elif rol == SUPERVISOR:
        ventas_hoy = Venta.objects.filter(fecha__gte=inicio_hoy)
        contexto.update({
            "ventas_hoy": resumen_ventas(ventas_hoy),
            "ventas_total": resumen_ventas(Venta.objects.all()),
            "ventas_por_vendedor": (
                ventas_hoy.values("vendedor__username")
                .annotate(cantidad=Count("id"), monto=Sum("total")).order_by("-monto")
            ),
            "ultimas_ventas": Venta.objects.select_related("cliente", "vendedor")[:5],
            "stock_bajo": Videojuego.objects.filter(stock__lte=STOCK_BAJO).order_by("stock"),
        })
        plantilla = "cuentas/panel_supervisor.html"

    elif rol == ADMINISTRATIVO:
        mis_ventas = Venta.objects.filter(vendedor=usuario).select_related("cliente")
        contexto.update({
            "mis_ventas_hoy": resumen_ventas(mis_ventas.filter(fecha__gte=inicio_hoy)),
            "mis_ultimas_ventas": mis_ventas[:5],
        })
        plantilla = "cuentas/panel_administrativo.html"

    else:
        plantilla = "cuentas/panel_sin_perfil.html"

    return render(request, plantilla, contexto)
