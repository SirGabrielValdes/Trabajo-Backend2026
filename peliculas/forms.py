from datetime import date

from django import forms

from zonaocio.formularios import FormularioBootstrap, validar_imagen_estatica, validar_unico

from .models import Clasificacion, Director, Genero, Pelicula


class GeneroForm(FormularioBootstrap, forms.ModelForm):
    class Meta:
        model = Genero
        fields = ["nombre", "descripcion"]
        widgets = {"descripcion": forms.Textarea(attrs={"rows": 3})}

    def clean_nombre(self):
        return validar_unico(self, "nombre", self.cleaned_data["nombre"].strip())


class ClasificacionForm(FormularioBootstrap, forms.ModelForm):
    class Meta:
        model = Clasificacion
        fields = ["codigo", "descripcion"]

    def clean_codigo(self):
        return validar_unico(self, "codigo", self.cleaned_data["codigo"].strip().upper())


class DirectorForm(FormularioBootstrap, forms.ModelForm):
    class Meta:
        model = Director
        fields = ["nombre", "nacionalidad"]

    def clean_nombre(self):
        return validar_unico(self, "nombre", self.cleaned_data["nombre"].strip())


class PeliculaForm(FormularioBootstrap, forms.ModelForm):
    class Meta:
        model = Pelicula
        fields = [
            "titulo", "directores", "genero", "clasificacion", "anio", "duracion_min",
            "calificacion", "sinopsis", "imagen",
        ]
        widgets = {
            "directores": forms.CheckboxSelectMultiple,
            "sinopsis": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_anio(self):
        anio = self.cleaned_data["anio"]
        if not 1888 <= anio <= date.today().year + 1:
            raise forms.ValidationError(f"El año debe estar entre 1888 y {date.today().year + 1}.")
        return anio

    def clean_duracion_min(self):
        duracion = self.cleaned_data["duracion_min"]
        if not 1 <= duracion <= 600:
            raise forms.ValidationError("La duración debe estar entre 1 y 600 minutos.")
        return duracion

    def clean_calificacion(self):
        nota = self.cleaned_data["calificacion"]
        if not 0 <= nota <= 10:
            raise forms.ValidationError("La calificación debe estar entre 0 y 10.")
        return nota

    def clean_imagen(self):
        return validar_imagen_estatica(self.cleaned_data["imagen"])

    def clean(self):
        datos = super().clean()
        titulo, anio = datos.get("titulo"), datos.get("anio")
        if titulo and anio:
            repetidas = Pelicula.objects.filter(titulo__iexact=titulo.strip(), anio=anio)
            if self.instance.pk:
                repetidas = repetidas.exclude(pk=self.instance.pk)
            if repetidas.exists():
                raise forms.ValidationError("Ya existe una película con ese título y año.")
        return datos
