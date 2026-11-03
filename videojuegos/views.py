from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, render

from zonaocio import crud
from zonaocio.crud import Mantenedor

from .forms import DesarrolladoraForm, GeneroForm, PlataformaForm, VideojuegoForm
from .models import Desarrolladora, Genero, Plataforma, Videojuego

# Opciones de orden permitidas: valor del parámetro GET -> campo del ORM
ORDENES = {
    "titulo": "titulo",
    "precio": "precio",
    "calificacion": "-calificacion",
    "anio": "-anio",
}


def inicio(request):
    """Página de inicio / presentación del sitio."""
    resumen = Videojuego.objects.aggregate(total=Count("id"), promedio=Avg("calificacion"))

    destacados = (
        Videojuego.objects.select_related("genero", "desarrolladora")
        .order_by("-calificacion")[:3]
    )

    contexto = {
        "total": resumen["total"],
        "promedio": round(resumen["promedio"] or 0, 1),
        "cantidad_generos": Genero.objects.count(),
        "destacados": destacados,
    }
    return render(request, "videojuegos/inicio.html", contexto)


def listado(request):
    """Catálogo de videojuegos obtenido desde la base de datos con filtros."""
    juegos = Videojuego.objects.select_related("genero", "desarrolladora").prefetch_related("plataformas")
    generos = Genero.objects.annotate(total=Count("videojuegos")).order_by("nombre")

    genero = request.GET.get("genero", "")
    busqueda = request.GET.get("q", "").strip()
    orden = request.GET.get("orden", "titulo")

    if genero.isdigit():
        juegos = juegos.filter(genero_id=int(genero))

    if busqueda:
        juegos = juegos.filter(
            Q(titulo__icontains=busqueda) | Q(desarrolladora__nombre__icontains=busqueda)
        )

    if orden not in ORDENES:
        orden = "titulo"
    juegos = juegos.order_by(ORDENES[orden])

    contexto = {
        "juegos": juegos,
        "generos": generos,
        "genero_actual": genero,
        "busqueda": busqueda,
        "orden_actual": orden,
    }
    return render(request, "videojuegos/listado.html", contexto)


def detalle(request, juego_id):
    """Ficha de un videojuego y sugerencias que comparten plataforma."""
    juego = get_object_or_404(
        Videojuego.objects.select_related("genero", "desarrolladora"), pk=juego_id
    )
    similares = (
        Videojuego.objects.filter(plataformas__in=juego.plataformas.all())
        .exclude(pk=juego.pk)
        .select_related("genero", "desarrolladora")
        .distinct()[:3]
    )
    contexto = {"juego": juego, "similares": similares}
    return render(request, "videojuegos/detalle.html", contexto)


def generos(request):
    """Listado de géneros con la cantidad de videojuegos de cada uno."""
    busqueda = request.GET.get("q", "").strip()
    registros = Genero.objects.annotate(total=Count("videojuegos")).order_by("nombre")
    if busqueda:
        registros = registros.filter(nombre__icontains=busqueda)
    return render(request, "videojuegos/generos.html", {"registros": registros, "busqueda": busqueda})


def desarrolladoras(request):
    """Listado de desarrolladoras con la cantidad de videojuegos."""
    busqueda = request.GET.get("q", "").strip()
    registros = Desarrolladora.objects.annotate(total=Count("videojuegos")).order_by("nombre")
    if busqueda:
        registros = registros.filter(Q(nombre__icontains=busqueda) | Q(pais__icontains=busqueda))
    return render(request, "videojuegos/desarrolladoras.html", {"registros": registros, "busqueda": busqueda})


def plataformas(request):
    """Listado de plataformas con sus videojuegos (relación ManyToMany)."""
    busqueda = request.GET.get("q", "").strip()
    registros = Plataforma.objects.prefetch_related("videojuegos").order_by("nombre")
    if busqueda:
        registros = registros.filter(Q(nombre__icontains=busqueda) | Q(fabricante__icontains=busqueda))
    return render(request, "videojuegos/plataformas.html", {"registros": registros, "busqueda": busqueda})


# ---------------------------------------------------------------------------
# Mantenedores: crear, modificar y eliminar registros desde Django Templates.
# El listado y la búsqueda están en las vistas de arriba.
# ---------------------------------------------------------------------------
MANTENEDORES = {
    "videojuegos": Mantenedor(Videojuego, VideojuegoForm, "videojuegos:listado"),
    "generos": Mantenedor(Genero, GeneroForm, "videojuegos:generos"),
    "desarrolladoras": Mantenedor(Desarrolladora, DesarrolladoraForm, "videojuegos:desarrolladoras"),
    "plataformas": Mantenedor(Plataforma, PlataformaForm, "videojuegos:plataformas"),
}


@login_required
def agregar(request, entidad):
    return crud.crear(request, crud.obtener_mantenedor(MANTENEDORES, entidad))


@login_required
def modificar(request, entidad, pk):
    return crud.modificar(request, crud.obtener_mantenedor(MANTENEDORES, entidad), pk)


@login_required
def eliminar(request, entidad, pk):
    return crud.eliminar(request, crud.obtener_mantenedor(MANTENEDORES, entidad), pk)
