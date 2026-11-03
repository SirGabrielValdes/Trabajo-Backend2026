from datetime import date

from django import forms

from zonaocio.formularios import FormularioBootstrap, validar_imagen_estatica, validar_unico

from .models import Desarrolladora, Genero, Plataforma, Videojuego


class GeneroForm(FormularioBootstrap, forms.ModelForm):
    class Meta:
        model = Genero
        fields = ["nombre", "descripcion"]
        widgets = {"descripcion": forms.Textarea(attrs={"rows": 3})}

    def clean_nombre(self):
        return validar_unico(self, "nombre", self.cleaned_data["nombre"].strip())


class DesarrolladoraForm(FormularioBootstrap, forms.ModelForm):
    class Meta:
        model = Desarrolladora
        fields = ["nombre", "pais"]

    def clean_nombre(self):
        return validar_unico(self, "nombre", self.cleaned_data["nombre"].strip())


class PlataformaForm(FormularioBootstrap, forms.ModelForm):
    class Meta:
        model = Plataforma
        fields = ["nombre", "fabricante"]

    def clean_nombre(self):
        return validar_unico(self, "nombre", self.cleaned_data["nombre"].strip())


class VideojuegoForm(FormularioBootstrap, forms.ModelForm):
    class Meta:
        model = Videojuego
        fields = [
            "titulo", "genero", "desarrolladora", "plataformas", "anio", "precio",
            "calificacion", "clasificacion", "descripcion", "imagen",
        ]
        widgets = {
            "plataformas": forms.CheckboxSelectMultiple,
            "descripcion": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_titulo(self):
        return validar_unico(self, "titulo", self.cleaned_data["titulo"].strip())

    def clean_anio(self):
        anio = self.cleaned_data["anio"]
        if not 1950 <= anio <= date.today().year + 1:
            raise forms.ValidationError(f"El año debe estar entre 1950 y {date.today().year + 1}.")
        return anio

    def clean_calificacion(self):
        nota = self.cleaned_data["calificacion"]
        if not 0 <= nota <= 10:
            raise forms.ValidationError("La calificación debe estar entre 0 y 10.")
        return nota

    def clean_imagen(self):
        return validar_imagen_estatica(self.cleaned_data["imagen"])
