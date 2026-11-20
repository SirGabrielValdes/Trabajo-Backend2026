"""Operaciones CRUD genéricas usadas por los mantenedores de todas las apps.

Cada app define un diccionario de Mantenedor (modelo + formulario + listado)
y sus vistas llaman a crear(), modificar() o eliminar().
Cada operación exige que el usuario tenga el permiso de Django correspondiente
(add_, change_ o delete_ del modelo), que se asigna según su perfil (grupo).
"""

from dataclasses import dataclass

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import ProtectedError
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render


@dataclass
class Mantenedor:
    modelo: type
    formulario: type
    url_listado: str  # nombre de la ruta del listado, ej: "videojuegos:generos"

    @property
    def nombre(self):
        return self.modelo._meta.verbose_name

    def permiso(self, accion):
        """Ej: permiso("add") -> "videojuegos.add_genero"."""
        meta = self.modelo._meta
        return f"{meta.app_label}.{accion}_{meta.model_name}"


def obtener_mantenedor(mantenedores, entidad):
    if entidad not in mantenedores:
        raise Http404("Mantenedor no encontrado")
    return mantenedores[entidad]


def verificar_permiso(request, mantenedor, accion):
    """Lanza un error 403 si el perfil del usuario no tiene el permiso."""
    if not request.user.has_perm(mantenedor.permiso(accion)):
        raise PermissionDenied


def crear(request, mantenedor):
    verificar_permiso(request, mantenedor, "add")
    formulario = mantenedor.formulario(request.POST or None)
    if request.method == "POST" and formulario.is_valid():
        registro = formulario.save()
        messages.success(request, f"Se creó {mantenedor.nombre} «{registro}» correctamente.")
        return redirect(mantenedor.url_listado)
    contexto = {
        "form": formulario,
        "titulo": f"Agregar {mantenedor.nombre}",
        "url_volver": mantenedor.url_listado,
    }
    return render(request, "crud/formulario.html", contexto)


def modificar(request, mantenedor, pk):
    verificar_permiso(request, mantenedor, "change")
    registro = get_object_or_404(mantenedor.modelo, pk=pk)
    formulario = mantenedor.formulario(request.POST or None, instance=registro)
    if request.method == "POST" and formulario.is_valid():
        registro = formulario.save()
        messages.success(request, f"Se modificó {mantenedor.nombre} «{registro}» correctamente.")
        return redirect(mantenedor.url_listado)
    contexto = {
        "form": formulario,
        "titulo": f"Modificar {mantenedor.nombre}",
        "registro": registro,
        "url_volver": mantenedor.url_listado,
    }
    return render(request, "crud/formulario.html", contexto)


def eliminar(request, mantenedor, pk):
    verificar_permiso(request, mantenedor, "delete")
    registro = get_object_or_404(mantenedor.modelo, pk=pk)
    if request.method == "POST":
        try:
            registro.delete()
        except ProtectedError as error:
            relacionados = len(error.protected_objects)
            messages.error(
                request,
                f"No se puede eliminar {mantenedor.nombre} «{registro}»: tiene {relacionados} "
                f"registro(s) relacionado(s). Primero modifica o elimina esos registros.",
            )
        else:
            messages.success(request, f"Se eliminó {mantenedor.nombre} «{registro}».")
        return redirect(mantenedor.url_listado)
    contexto = {
        "titulo": f"Eliminar {mantenedor.nombre}",
        "registro": registro,
        "url_volver": mantenedor.url_listado,
    }
    return render(request, "crud/confirmar_eliminar.html", contexto)
