from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Clasificacion, Director, Genero, Pelicula


def enlace_admin(objeto):
    """Genera un enlace a la página de edición del objeto relacionado."""
    url = reverse(f"admin:{objeto._meta.app_label}_{objeto._meta.model_name}_change", args=[objeto.pk])
    return format_html('<a href="{}">{}</a>', url, objeto)


class PeliculaInline(admin.TabularInline):
    """Lista las películas relacionadas dentro de la ficha del padre."""

    model = Pelicula
    fields = ("titulo", "anio", "duracion_min", "calificacion")
    extra = 0
    show_change_link = True


class DirectorPeliculaInline(admin.TabularInline):
    """Películas dirigidas por un director (relación ManyToMany)."""

    model = Pelicula.directores.through
    verbose_name = "película"
    verbose_name_plural = "películas dirigidas"
    autocomplete_fields = ("pelicula",)
    extra = 0


@admin.register(Genero)
class GeneroAdmin(admin.ModelAdmin):
    list_display = ("nombre", "cantidad_peliculas")
    search_fields = ("nombre", "descripcion")
    inlines = [PeliculaInline]

    @admin.display(description="películas")
    def cantidad_peliculas(self, obj):
        return obj.peliculas.count()


@admin.register(Clasificacion)
class ClasificacionAdmin(admin.ModelAdmin):
    list_display = ("codigo", "descripcion", "cantidad_peliculas")
    search_fields = ("codigo", "descripcion")
    inlines = [PeliculaInline]

    @admin.display(description="películas")
    def cantidad_peliculas(self, obj):
        return obj.peliculas.count()


@admin.register(Director)
class DirectorAdmin(admin.ModelAdmin):
    list_display = ("nombre", "nacionalidad", "cantidad_peliculas")
    list_filter = ("nacionalidad",)
    search_fields = ("nombre", "nacionalidad")
    inlines = [DirectorPeliculaInline]

    @admin.display(description="películas")
    def cantidad_peliculas(self, obj):
        return obj.peliculas.count()


@admin.register(Pelicula)
class PeliculaAdmin(admin.ModelAdmin):
    list_display = (
        "titulo", "lista_directores", "ver_genero", "ver_clasificacion",
        "anio", "duracion_min", "calificacion",
    )
    list_filter = ("genero", "clasificacion", "directores", "anio")
    search_fields = ("titulo", "sinopsis", "directores__nombre", "genero__nombre")
    autocomplete_fields = ("genero", "clasificacion")
    filter_horizontal = ("directores",)
    list_per_page = 20

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "genero", "clasificacion"
        ).prefetch_related("directores")

    @admin.display(description="género", ordering="genero__nombre")
    def ver_genero(self, obj):
        return enlace_admin(obj.genero)

    @admin.display(description="clasificación", ordering="clasificacion__codigo")
    def ver_clasificacion(self, obj):
        return enlace_admin(obj.clasificacion)

    @admin.display(description="directores")
    def lista_directores(self, obj):
        return ", ".join(d.nombre for d in obj.directores.all())
