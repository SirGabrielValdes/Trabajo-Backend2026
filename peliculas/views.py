from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, render

from zonaocio import crud
from zonaocio.crud import Mantenedor

from .forms import ClasificacionForm, DirectorForm, GeneroForm, PeliculaForm
from .models import Clasificacion, Director, Genero, Pelicula


def listado(request):
    """Cartelera de películas obtenida desde la base de datos.

    Permite filtrar por género, buscar por título/director y cambiar entre
    vista de tarjetas o de tabla.
    """
    peliculas = Pelicula.objects.select_related("genero", "clasificacion").prefetch_related("directores")
    generos = Genero.objects.order_by("nombre")

    genero = request.GET.get("genero", "")
    busqueda = request.GET.get("q", "").strip()
    vista = request.GET.get("vista", "tarjetas")

    if genero.isdigit():
        peliculas = peliculas.filter(genero_id=int(genero))

    if busqueda:
        peliculas = peliculas.filter(
            Q(titulo__icontains=busqueda) | Q(directores__nombre__icontains=busqueda)
        ).distinct()

    if vista != "tabla":
        vista = "tarjetas"

    peliculas = peliculas.order_by("-anio", "titulo")
    duracion_total = peliculas.aggregate(total=Sum("duracion_min"))["total"] or 0

    contexto = {
        "peliculas": peliculas,
        "generos": generos,
        "genero_actual": genero,
        "busqueda": busqueda,
        "vista": vista,
        "horas_totales": round(duracion_total / 60, 1),
    }
    return render(request, "peliculas/listado.html", contexto)


def detalle(request, pelicula_id):
    """Ficha de una película y otras del mismo director o género."""
    pelicula = get_object_or_404(
        Pelicula.objects.select_related("genero", "clasificacion"), pk=pelicula_id
    )
    relacionadas = (
        Pelicula.objects.filter(
            Q(directores__in=pelicula.directores.all()) | Q(genero=pelicula.genero)
        )
        .exclude(pk=pelicula.pk)
        .select_related("genero", "clasificacion")
        .prefetch_related("directores")
        .distinct()
    )
    contexto = {"pelicula": pelicula, "relacionadas": relacionadas}
    return render(request, "peliculas/detalle.html", contexto)


def generos(request):
    """Listado de géneros cinematográficos con su cantidad de películas."""
    busqueda = request.GET.get("q", "").strip()
    registros = Genero.objects.annotate(total=Count("peliculas")).order_by("nombre")
    if busqueda:
        registros = registros.filter(nombre__icontains=busqueda)
    return render(request, "peliculas/generos.html", {"registros": registros, "busqueda": busqueda})


def directores(request):
    """Listado de directores con las películas que dirigieron."""
    busqueda = request.GET.get("q", "").strip()
    registros = Director.objects.prefetch_related("peliculas").order_by("nombre")
    if busqueda:
        registros = registros.filter(Q(nombre__icontains=busqueda) | Q(nacionalidad__icontains=busqueda))
    return render(request, "peliculas/directores.html", {"registros": registros, "busqueda": busqueda})


def clasificaciones(request):
    """Listado de clasificaciones por edad con su cantidad de películas."""
    busqueda = request.GET.get("q", "").strip()
    registros = Clasificacion.objects.annotate(total=Count("peliculas")).order_by("codigo")
    if busqueda:
        registros = registros.filter(Q(codigo__icontains=busqueda) | Q(descripcion__icontains=busqueda))
    return render(request, "peliculas/clasificaciones.html", {"registros": registros, "busqueda": busqueda})


# ---------------------------------------------------------------------------
# Mantenedores: crear, modificar y eliminar registros desde Django Templates.
# El listado y la búsqueda están en las vistas de arriba.
# ---------------------------------------------------------------------------
MANTENEDORES = {
    "peliculas": Mantenedor(Pelicula, PeliculaForm, "peliculas:listado"),
    "generos": Mantenedor(Genero, GeneroForm, "peliculas:generos"),
    "directores": Mantenedor(Director, DirectorForm, "peliculas:directores"),
    "clasificaciones": Mantenedor(Clasificacion, ClasificacionForm, "peliculas:clasificaciones"),
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
