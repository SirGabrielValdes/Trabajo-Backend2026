from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Desarrolladora, Genero, Plataforma, Videojuego

admin.site.site_header = "ZonaOcio – Administración"
admin.site.site_title = "ZonaOcio Admin"
admin.site.index_title = "Gestión de videojuegos y películas"


def enlace_admin(objeto):
    """Genera un enlace a la página de edición del objeto relacionado."""
    url = reverse(f"admin:{objeto._meta.app_label}_{objeto._meta.model_name}_change", args=[objeto.pk])
    return format_html('<a href="{}">{}</a>', url, objeto)


class VideojuegoInline(admin.TabularInline):
    """Lista los videojuegos relacionados dentro de la ficha del padre."""

    model = Videojuego
    fields = ("titulo", "anio", "precio", "calificacion")
    extra = 0
    show_change_link = True


class PlataformaVideojuegoInline(admin.TabularInline):
    """Videojuegos disponibles en una plataforma (relación ManyToMany)."""

    model = Videojuego.plataformas.through
    verbose_name = "videojuego"
    verbose_name_plural = "videojuegos disponibles en esta plataforma"
    autocomplete_fields = ("videojuego",)
    extra = 0


@admin.register(Genero)
class GeneroAdmin(admin.ModelAdmin):
    list_display = ("nombre", "cantidad_videojuegos")
    search_fields = ("nombre", "descripcion")
    inlines = [VideojuegoInline]

    @admin.display(description="videojuegos")
    def cantidad_videojuegos(self, obj):
        return obj.videojuegos.count()


@admin.register(Desarrolladora)
class DesarrolladoraAdmin(admin.ModelAdmin):
    list_display = ("nombre", "pais", "cantidad_videojuegos")
    list_filter = ("pais",)
    search_fields = ("nombre", "pais")
    inlines = [VideojuegoInline]

    @admin.display(description="videojuegos")
    def cantidad_videojuegos(self, obj):
        return obj.videojuegos.count()


@admin.register(Plataforma)
class PlataformaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "fabricante", "cantidad_videojuegos")
    list_filter = ("fabricante",)
    search_fields = ("nombre", "fabricante")
    inlines = [PlataformaVideojuegoInline]

    @admin.display(description="videojuegos")
    def cantidad_videojuegos(self, obj):
        return obj.videojuegos.count()


@admin.register(Videojuego)
class VideojuegoAdmin(admin.ModelAdmin):
    list_display = (
        "titulo", "ver_genero", "ver_desarrolladora", "lista_plataformas",
        "anio", "precio", "calificacion", "clasificacion",
    )
    list_filter = ("genero", "desarrolladora", "plataformas", "clasificacion", "anio")
    search_fields = ("titulo", "descripcion", "genero__nombre", "desarrolladora__nombre")
    autocomplete_fields = ("genero", "desarrolladora")
    filter_horizontal = ("plataformas",)
    list_per_page = 20

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "genero", "desarrolladora"
        ).prefetch_related("plataformas")

    @admin.display(description="género", ordering="genero__nombre")
    def ver_genero(self, obj):
        return enlace_admin(obj.genero)

    @admin.display(description="desarrolladora", ordering="desarrolladora__nombre")
    def ver_desarrolladora(self, obj):
        return enlace_admin(obj.desarrolladora)

    @admin.display(description="plataformas")
    def lista_plataformas(self, obj):
        return ", ".join(p.nombre for p in obj.plataformas.all())
