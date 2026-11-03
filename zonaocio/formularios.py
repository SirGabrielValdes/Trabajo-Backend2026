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
