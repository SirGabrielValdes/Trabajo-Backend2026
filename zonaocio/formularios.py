"""Utilidades compartidas para los formularios del proyecto."""

from django import forms


class FormularioBootstrap:
    """Mixin que agrega las clases de Bootstrap a todos los campos del formulario.

    Se usa junto a forms.Form o forms.ModelForm:
        class MiFormulario(FormularioBootstrap, forms.ModelForm): ...
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            widget = campo.widget
            if isinstance(widget, (forms.CheckboxInput, forms.CheckboxSelectMultiple, forms.RadioSelect)):
                clase = "form-check-input"
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                clase = "form-select"
            else:
                clase = "form-control"
            widget.attrs["class"] = f"{widget.attrs.get('class', '')} {clase}".strip()


def validar_unico(formulario, campo, valor):
    """Valida que no exista otro registro con el mismo valor (sin distinguir mayúsculas).

    Ejemplo: impide crear el género "rpg" si ya existe "RPG".
    """
    modelo = formulario._meta.model
    repetidos = modelo.objects.filter(**{f"{campo}__iexact": valor})
    if formulario.instance.pk:
        repetidos = repetidos.exclude(pk=formulario.instance.pk)
    if repetidos.exists():
        nombre_campo = modelo._meta.get_field(campo).verbose_name
        raise forms.ValidationError(f"Ya existe un registro con ese {nombre_campo}.")
    return valor


def validar_imagen_estatica(ruta):
    """Valida que la ruta de imagen exista dentro de los archivos estáticos."""
    from django.contrib.staticfiles import finders

    ruta = (ruta or "").strip()
    if ruta and not finders.find(ruta):
        raise forms.ValidationError(
            "No se encontró esa imagen en los archivos estáticos (ej: videojuegos/img/zelda.svg)."
        )
    return ruta
