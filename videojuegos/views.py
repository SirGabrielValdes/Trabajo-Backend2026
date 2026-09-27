from django.db.models import Avg, Count, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, render

from .models import Desarrolladora, Genero, Plataforma, Videojuego

# Opciones de orden permitidas: valor del parámetro GET -> campo del ORM
ORDENES = {
    "titulo": "titulo",
    "precio": "precio",
    "calificacion": "-calificacion",
    "anio": "-anio",
}

# Entidades de esta app que tendrán CRUD desde la interfaz (Evaluación N°3)
ENTIDADES = {
    "videojuegos": ("videojuego", Videojuego, "videojuegos:listado"),
    "generos": ("género", Genero, "videojuegos:generos"),
    "desarrolladoras": ("desarrolladora", Desarrolladora, "videojuegos:desarrolladoras"),
    "plataformas": ("plataforma", Plataforma, "videojuegos:plataformas"),
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


def accion_pendiente(request, entidad, accion, pk=None):
    """Marcador de posición para los botones Agregar / Modificar / Eliminar.

    Las operaciones CRUD desde la interfaz se implementarán en la siguiente
    evaluación; por ahora se realizan desde Django Admin.
    """
    if entidad not in ENTIDADES or accion not in ("agregar", "modificar", "eliminar"):
        raise Http404("Acción no válida")

    nombre, modelo, url_volver = ENTIDADES[entidad]
    registro = get_object_or_404(modelo, pk=pk) if pk is not None else None

    contexto = {
        "accion": accion,
        "nombre": nombre,
        "registro": registro,
        "url_volver": url_volver,
        "url_admin": f"admin:videojuegos_{modelo._meta.model_name}_changelist",
    }
    return render(request, "accion_pendiente.html", contexto)
