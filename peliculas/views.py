from django.db.models import Count, Q, Sum
from django.http import Http404
from django.shortcuts import get_object_or_404, render

from .models import Clasificacion, Director, Genero, Pelicula

# Entidades de esta app que tendrán CRUD desde la interfaz (Evaluación N°3)
ENTIDADES = {
    "peliculas": ("película", Pelicula, "peliculas:listado"),
    "generos": ("género", Genero, "peliculas:generos"),
    "directores": ("director", Director, "peliculas:directores"),
    "clasificaciones": ("clasificación", Clasificacion, "peliculas:clasificaciones"),
}


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


def accion_pendiente(request, entidad, accion, pk=None):
    """Marcador de posición para los botones Agregar / Modificar / Eliminar."""
    if entidad not in ENTIDADES or accion not in ("agregar", "modificar", "eliminar"):
        raise Http404("Acción no válida")

    nombre, modelo, url_volver = ENTIDADES[entidad]
    registro = get_object_or_404(modelo, pk=pk) if pk is not None else None

    contexto = {
        "accion": accion,
        "nombre": nombre,
        "registro": registro,
        "url_volver": url_volver,
        "url_admin": f"admin:peliculas_{modelo._meta.model_name}_changelist",
    }
    return render(request, "accion_pendiente.html", contexto)
