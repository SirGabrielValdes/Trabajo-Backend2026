"""
Configuración del proyecto ZonaOcio (Evaluación Sumativa N°2).

Sitio web modular compuesto por dos aplicaciones:
  - videojuegos: página de inicio + catálogo de videojuegos.
  - peliculas:   cartelera de películas.

La información se almacena en una base de datos relacional MySQL/MariaDB
y se administra desde Django Admin.

Las configuraciones sensibles (SECRET_KEY, credenciales de la base de
datos, etc.) NO se escriben en el código: se leen desde el archivo .env
mediante la librería python-dotenv. Ver .env.example.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Carga las variables definidas en el archivo .env (junto a manage.py)
load_dotenv(BASE_DIR / ".env")


def variable_lista(nombre, por_defecto=""):
    """Convierte 'a,b,c' en ['a', 'b', 'c'] (sin elementos vacíos)."""
    valor = os.getenv(nombre, por_defecto)
    return [elemento.strip() for elemento in valor.split(",") if elemento.strip()]


SECRET_KEY = os.environ["SECRET_KEY"]

DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "si")

ALLOWED_HOSTS = variable_lista("ALLOWED_HOSTS", "127.0.0.1,localhost")

CSRF_TRUSTED_ORIGINS = variable_lista("CSRF_TRUSTED_ORIGINS")


# Aplicaciones
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Aplicaciones propias del proyecto
    "videojuegos",
    "peliculas",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # Librería externa: WhiteNoise sirve los archivos estáticos (Bootstrap, imágenes)
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
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
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "zonaocio.wsgi.application"


# Base de datos relacional MySQL / MariaDB (visible desde phpMyAdmin).
# Todos los datos de conexión provienen del archivo .env
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ["DB_NAME"],
        "USER": os.environ["DB_USER"],
        "PASSWORD": os.environ["DB_PASSWORD"],
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "3306"),
        "OPTIONS": {
            "charset": "utf8mb4",
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}


# Validación de contraseñas (usuarios de Django Admin)
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


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
