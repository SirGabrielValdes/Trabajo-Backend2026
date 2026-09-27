"""
Configuración del proyecto ZonaOcio (Evaluación Sumativa N°1).

Sitio web informativo modular compuesto por dos aplicaciones:
  - videojuegos: página de inicio + catálogo de videojuegos (JSON).
  - peliculas:   cartelera de películas (JSON).

Requisito de la evaluación: NO se utilizan bases de datos. Toda la
información se lee desde archivos JSON ubicados en cada aplicación.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-ipvv1-^xi@=w6kmo$_#(pj107fwrr42mqi2)xet80l$@rbmy#j"

DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]


# Aplicaciones
# Solo se incluyen apps que no requieren base de datos.
INSTALLED_APPS = [
    "django.contrib.staticfiles",
    # Aplicaciones propias del proyecto
    "videojuegos",
    "peliculas",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # Librería externa: WhiteNoise sirve los archivos estáticos (Bootstrap, imágenes)
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "zonaocio.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Carpeta global de plantillas (aquí vive base.html)
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
            ],
        },
    },
]

WSGI_APPLICATION = "zonaocio.wsgi.application"


# Base de datos
# La evaluación prohíbe el uso de bases de datos: se deja vacío.
DATABASES = {}


# Internacionalización
LANGUAGE_CODE = "es-cl"
TIME_ZONE = "America/Santiago"
USE_I18N = True
USE_TZ = True


# Archivos estáticos (Bootstrap local, CSS propio e imágenes)
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
