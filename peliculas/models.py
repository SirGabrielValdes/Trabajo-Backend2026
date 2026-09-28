from django.db import models


class Genero(models.Model):
    """Género cinematográfico (Drama, Animación, Terror...)."""

    nombre = models.CharField("nombre", max_length=50, unique=True)
    descripcion = models.TextField("descripción", blank=True)

    class Meta:
        verbose_name = "género"
        verbose_name_plural = "géneros"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Clasificacion(models.Model):
    """Clasificación chilena por edad (TE, TE+7, 14, 18)."""

    codigo = models.CharField("código", max_length=10, unique=True)
    descripcion = models.CharField("descripción", max_length=120)

    class Meta:
        verbose_name = "clasificación"
        verbose_name_plural = "clasificaciones"
        ordering = ["codigo"]

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"


class Director(models.Model):
    """Persona que dirige películas."""

    nombre = models.CharField("nombre", max_length=100, unique=True)
    nacionalidad = models.CharField("nacionalidad", max_length=60, blank=True)

    class Meta:
        verbose_name = "director"
        verbose_name_plural = "directores"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Pelicula(models.Model):
    """Película de la cartelera (antes almacenada en peliculas.json)."""

    titulo = models.CharField("título", max_length=150)
    genero = models.ForeignKey(
        Genero, on_delete=models.PROTECT, related_name="peliculas", verbose_name="género"
    )
    clasificacion = models.ForeignKey(
        Clasificacion, on_delete=models.PROTECT, related_name="peliculas",
        verbose_name="clasificación",
    )
    directores = models.ManyToManyField(
        Director, related_name="peliculas", verbose_name="directores"
    )
    anio = models.PositiveSmallIntegerField("año de estreno")
    duracion_min = models.PositiveSmallIntegerField("duración (minutos)")
    calificacion = models.DecimalField("calificación", max_digits=3, decimal_places=1)
    sinopsis = models.TextField("sinopsis")
    imagen = models.CharField(
        "imagen", max_length=200, blank=True,
        help_text="Ruta dentro de los archivos estáticos, ej: peliculas/img/coco.svg",
    )

    class Meta:
        verbose_name = "película"
        verbose_name_plural = "películas"
        ordering = ["-anio", "titulo"]

    def __str__(self):
        return f"{self.titulo} ({self.anio})"

    @property
    def duracion_texto(self):
        """169 -> '2 h 49 min'."""
        horas, resto = divmod(self.duracion_min, 60)
        if horas == 0:
            return f"{resto} min"
        if resto == 0:
            return f"{horas} h"
        return f"{horas} h {resto} min"

    @property
    def estrellas(self):
        """Nota de 0 a 10 convertida a 5 estrellas: '★★★★☆'."""
        llenas = round(float(self.calificacion) / 2)
        return "★" * llenas + "☆" * (5 - llenas)
