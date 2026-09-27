from django.db import models


class Genero(models.Model):
    """Categoría del videojuego (Aventura, RPG, Deportes...)."""

    nombre = models.CharField("nombre", max_length=50, unique=True)
    descripcion = models.TextField("descripción", blank=True)

    class Meta:
        verbose_name = "género"
        verbose_name_plural = "géneros"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Desarrolladora(models.Model):
    """Estudio o empresa que desarrolla videojuegos."""

    nombre = models.CharField("nombre", max_length=100, unique=True)
    pais = models.CharField("país", max_length=60, blank=True)

    class Meta:
        verbose_name = "desarrolladora"
        verbose_name_plural = "desarrolladoras"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Plataforma(models.Model):
    """Consola o dispositivo donde se puede jugar (PC, PS5, Switch...)."""

    nombre = models.CharField("nombre", max_length=50, unique=True)
    fabricante = models.CharField("fabricante", max_length=60, blank=True)

    class Meta:
        verbose_name = "plataforma"
        verbose_name_plural = "plataformas"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Videojuego(models.Model):
    """Videojuego del catálogo (antes almacenado en videojuegos.json)."""

    CLASIFICACIONES = [
        ("E", "E - Todos"),
        ("E10+", "E10+ - Mayores de 10 años"),
        ("T", "T - Adolescentes"),
        ("M", "M - Mayores de 17 años"),
    ]

    titulo = models.CharField("título", max_length=150)
    genero = models.ForeignKey(
        Genero, on_delete=models.PROTECT, related_name="videojuegos", verbose_name="género"
    )
    desarrolladora = models.ForeignKey(
        Desarrolladora, on_delete=models.PROTECT, related_name="videojuegos",
        verbose_name="desarrolladora",
    )
    plataformas = models.ManyToManyField(
        Plataforma, related_name="videojuegos", verbose_name="plataformas"
    )
    anio = models.PositiveSmallIntegerField("año de lanzamiento")
    precio = models.PositiveIntegerField("precio (CLP)")
    calificacion = models.DecimalField("calificación", max_digits=3, decimal_places=1)
    clasificacion = models.CharField("clasificación ESRB", max_length=5, choices=CLASIFICACIONES)
    descripcion = models.TextField("descripción")
    imagen = models.CharField(
        "imagen", max_length=200, blank=True,
        help_text="Ruta dentro de los archivos estáticos, ej: videojuegos/img/zelda.svg",
    )

    class Meta:
        verbose_name = "videojuego"
        verbose_name_plural = "videojuegos"
        ordering = ["titulo"]

    def __str__(self):
        return self.titulo

    @property
    def precio_texto(self):
        """59990 -> '$59.990' (formato de pesos chilenos)."""
        return "$" + f"{self.precio:,}".replace(",", ".")

    @property
    def nivel(self):
        """Etiqueta según la calificación."""
        if self.calificacion >= 9:
            return "Obra maestra"
        elif self.calificacion >= 8:
            return "Muy bueno"
        elif self.calificacion >= 7:
            return "Bueno"
        return "Regular"

    @property
    def color(self):
        """Color de Bootstrap asociado a la calificación."""
        colores = {"Obra maestra": "success", "Muy bueno": "primary", "Bueno": "warning"}
        return colores.get(self.nivel, "secondary")
