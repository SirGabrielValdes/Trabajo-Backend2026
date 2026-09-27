# ZonaOcio – Portal de entretenimiento (Django)

Proyecto de la asignatura **Programación Back End (TI3041)** – INACAP.
**Evaluación Sumativa N°1:** sitio web modular con Django, datos en JSON y Bootstrap local.

ZonaOcio es un sitio informativo que reúne un catálogo de **videojuegos** y una cartelera de
**películas**. Cada temática vive en una aplicación Django independiente.

## Tecnologías

| Tecnología | Uso |
|---|---|
| Python 3 | Lenguaje del lado del servidor |
| Django 5.2 | Framework web |
| WhiteNoise (librería externa) | Servir archivos estáticos (Bootstrap, imágenes) |
| Bootstrap 5.3.3 (local) | Interfaz de usuario, guardado en `static/bootstrap/` |
| JSON | Almacenamiento de la información (sin base de datos) |

## Estructura del proyecto

```
Trabajo-Backend2026/
├── manage.py
├── requirements.txt
├── zonaocio/                 # Proyecto principal
│   ├── settings.py
│   └── urls.py               # Rutas principales (incluye las de cada app)
├── templates/
│   └── base.html             # Plantilla base: navbar, encabezado, pie, estáticos
├── static/
│   ├── bootstrap/css|js/     # Bootstrap local
│   ├── css/estilos.css
│   └── img/logo.svg
├── videojuegos/              # Aplicación 1
│   ├── data/videojuegos.json
│   ├── static/videojuegos/img/
│   ├── templates/videojuegos/ (inicio, listado, detalle, tarjeta)
│   ├── urls.py
│   ├── utils.py              # Lectura y procesamiento del JSON
│   └── views.py              # inicio, listado, detalle
└── peliculas/                # Aplicación 2
    ├── data/peliculas.json
    ├── static/peliculas/img/
    ├── templates/peliculas/ (listado, detalle, tarjeta)
    ├── urls.py
    ├── utils.py
    └── views.py              # listado, detalle
```

## Rutas

| URL | App | Vista | Descripción |
|---|---|---|---|
| `/` | videojuegos | `inicio` | Página de presentación con destacados y estadísticas |
| `/videojuegos/` | videojuegos | `listado` | Catálogo con búsqueda, filtro por género y orden |
| `/videojuegos/<id>/` | videojuegos | `detalle` | Ficha del videojuego |
| `/peliculas/` | peliculas | `listado` | Cartelera en tarjetas o tabla, con búsqueda y filtro |
| `/peliculas/<id>/` | peliculas | `detalle` | Ficha de la película |

## Cómo ejecutar

```bash
git clone https://github.com/SirGabrielValdes/Trabajo-Backend2026.git
cd Trabajo-Backend2026

python -m venv venv
# Windows:
venv\Scripts\activate
# Linux / macOS:
source venv/bin/activate

pip install -r requirements.txt
python manage.py runserver
```

Abrir <http://127.0.0.1:8000/> en el navegador.

> Las imágenes de portada son ilustraciones SVG propias; los títulos y datos de videojuegos y
> películas son solo informativos.
