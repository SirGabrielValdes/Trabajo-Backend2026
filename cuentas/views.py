from datetime import datetime, time

from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.models import Count, ProtectedError, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from peliculas.models import Pelicula
from ventas.models import Cliente, Venta
from videojuegos.models import Videojuego

from .forms import LoginForm, UsuarioCrearForm, UsuarioModificarForm
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


# ---------------------------------------------------------------------------
# Gestión de usuarios (solo perfiles con permisos sobre auth.User)
# ---------------------------------------------------------------------------
def verificar_superusuario(request, usuario):
    """Solo un superusuario puede modificar o eliminar a otro superusuario."""
    if usuario.is_superuser and not request.user.is_superuser:
        raise PermissionDenied


@login_required
@permission_required("auth.view_user", raise_exception=True)
def usuarios(request):
    """Listado y búsqueda de usuarios con su perfil."""
    busqueda = request.GET.get("q", "").strip()
    registros = User.objects.prefetch_related("groups").order_by("username")
    if busqueda:
        registros = registros.filter(
            Q(username__icontains=busqueda) | Q(first_name__icontains=busqueda)
            | Q(last_name__icontains=busqueda) | Q(email__icontains=busqueda)
            | Q(groups__name__icontains=busqueda)
        ).distinct()
    return render(request, "cuentas/usuarios.html", {"registros": registros, "busqueda": busqueda})


@login_required
@permission_required("auth.add_user", raise_exception=True)
def usuario_crear(request):
    formulario = UsuarioCrearForm(request.POST or None)
    if request.method == "POST" and formulario.is_valid():
        usuario = formulario.save()
        messages.success(request, f"Usuario «{usuario.username}» creado con perfil {formulario.cleaned_data['perfil']}.")
        return redirect("cuentas:usuarios")
    contexto = {"form": formulario, "titulo": "Agregar usuario", "url_volver": "cuentas:usuarios"}
    return render(request, "crud/formulario.html", contexto)


@login_required
@permission_required("auth.change_user", raise_exception=True)
def usuario_modificar(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    verificar_superusuario(request, usuario)
    formulario = UsuarioModificarForm(request.POST or None, instance=usuario)
    if request.method == "POST" and formulario.is_valid():
        formulario.save()
        messages.success(request, f"Usuario «{usuario.username}» modificado correctamente.")
        return redirect("cuentas:usuarios")
    contexto = {
        "form": formulario, "titulo": "Modificar usuario", "registro": usuario,
        "url_volver": "cuentas:usuarios",
    }
    return render(request, "crud/formulario.html", contexto)


@login_required
@permission_required("auth.delete_user", raise_exception=True)
def usuario_eliminar(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    verificar_superusuario(request, usuario)
    if usuario == request.user:
        messages.error(request, "No puedes eliminar tu propio usuario.")
        return redirect("cuentas:usuarios")
    if request.method == "POST":
        try:
            usuario.delete()
        except ProtectedError:
            messages.error(
                request,
                f"No se puede eliminar a «{usuario.username}» porque tiene ventas registradas. "
                "Puedes desactivarlo desde Modificar.",
            )
        else:
            messages.success(request, f"Usuario «{usuario.username}» eliminado.")
        return redirect("cuentas:usuarios")
    contexto = {"titulo": "Eliminar usuario", "registro": usuario, "url_volver": "cuentas:usuarios"}
    return render(request, "crud/confirmar_eliminar.html", contexto)
