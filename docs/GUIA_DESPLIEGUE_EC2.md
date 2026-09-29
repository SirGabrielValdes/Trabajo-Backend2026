# Guía de despliegue en AWS EC2 – ZonaOcio

Guía paso a paso para dejar el proyecto funcionando en una instancia **EC2 con Ubuntu Server 24.04**,
con **MySQL**, **phpMyAdmin**, **Gunicorn** (servidor de la aplicación) y **Apache** (servidor web).

```
Navegador ──► Apache :80 ──┬──► /phpmyadmin  (phpMyAdmin)
                           └──► /            ──► Gunicorn 127.0.0.1:8000 ──► Django ──► MySQL
```

> 📸 A lo largo de la guía se indica con **📸 CAPTURA** cada evidencia que pide el documento técnico.

---

## 0. Antes de empezar

1. El Pull Request del proyecto debe estar unido (merge) a la rama `main` en GitHub.
2. El repositorio debe ser **público** para clonarlo sin contraseña.
   Si es privado, GitHub pedirá usuario y un *Personal Access Token* como contraseña al hacer `git clone`.

---

## 1. Crear la instancia EC2 (consola de AWS)

1. Ingresar a la consola de AWS → **EC2** → **Launch instance** (Lanzar instancia).
2. **Name:** `zonaocio-servidor`.
3. **AMI:** *Ubuntu Server 24.04 LTS* (apta para la capa gratuita).
4. **Instance type:** `t2.micro` o `t3.micro`.
5. **Key pair:** *Create new key pair* → nombre `zonaocio-clave`, tipo RSA, formato `.pem`.
   Guardar el archivo descargado (no se puede volver a descargar).
6. **Network settings → Edit → Security group:** agregar estas reglas de entrada:

   | Tipo | Puerto | Origen |
   |---|---|---|
   | SSH  | 22 | My IP (Mi IP) |
   | HTTP | 80 | Anywhere (0.0.0.0/0) |

7. **Storage:** 8 GB o más → **Launch instance**.
8. Copiar la **dirección IPv4 pública** de la instancia (en esta guía: `IP_PUBLICA`).

📸 **CAPTURA:** la instancia en estado *Running* con su IP pública.

---

## 2. Conectarse a la instancia

**Opción A – Terminal (Linux / macOS / Windows PowerShell):**

```bash
chmod 400 zonaocio-clave.pem        # solo Linux/macOS
ssh -i zonaocio-clave.pem ubuntu@IP_PUBLICA
```

**Opción B – Navegador:** en la consola de EC2, seleccionar la instancia → **Connect** → **EC2 Instance Connect** → **Connect**.

📸 **CAPTURA:** terminal Linux conectada a la instancia (se ve `ubuntu@ip-...:~$`).

---

## 3. Instalar el software del servidor

```bash
sudo apt update && sudo apt upgrade -y

# Python, entorno virtual, Git y librerías para compilar el conector de MySQL
sudo apt install -y python3 python3-venv python3-pip python3-dev git \
     build-essential pkg-config default-libmysqlclient-dev

# Base de datos MySQL, servidor web Apache y PHP (necesario para phpMyAdmin)
sudo apt install -y mysql-server apache2 libapache2-mod-php \
     php-mysql php-mbstring php-zip php-gd php-curl php-xml

# phpMyAdmin
sudo apt install -y phpmyadmin
```

Durante la instalación de **phpMyAdmin** aparecen dos pantallas:

1. *Web server to reconfigure automatically*: marcar **apache2** con la barra espaciadora (debe quedar `[*]`) y presionar Enter.
2. *Configure database for phpmyadmin with dbconfig-common?*: **Yes**, e ingresar una contraseña para el usuario interno de phpMyAdmin.

Verificar las versiones instaladas:

```bash
python3 --version
git --version
mysql --version
apache2 -v
```

📸 **CAPTURA:** las versiones instaladas.

---

### Memoria de intercambio (swap)

Las instancias `t2.micro`/`t3.micro` tienen solo 1 GB de RAM, poco para MySQL + Apache + phpMyAdmin + Django.
Crear 2 GB de swap evita que el sitio se ponga lento:

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
free -h                                  # debe mostrar Swap: 2.0Gi
```

---

## 4. Crear la base de datos y su usuario

```bash
sudo mysql
```

Dentro de MySQL (cambiar `CLAVE_SEGURA` por una contraseña propia):

```sql
CREATE DATABASE zonaocio_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'zonaocio_user'@'localhost' IDENTIFIED BY 'CLAVE_SEGURA';
GRANT ALL PRIVILEGES ON zonaocio_db.* TO 'zonaocio_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

---

## 5. Clonar el proyecto desde GitHub

```bash
cd ~
git clone https://github.com/SirGabrielValdes/Trabajo-Backend2026.git
cd Trabajo-Backend2026

git remote -v          # muestra el repositorio remoto configurado
git log --oneline      # muestra el historial de commits
```

📸 **CAPTURA:** el comando `git clone`, `git remote -v` y `git log --oneline`.

---

## 6. Crear el entorno virtual e instalar dependencias

```bash
python3 -m venv venv
source venv/bin/activate          # el prompt comienza con (venv)
pip install -r requirements.txt
pip list                          # Django, mysqlclient, python-dotenv, gunicorn...
```

📸 **CAPTURA:** entorno virtual activo `(venv)` y `pip list`.

---

## 7. Configurar las variables de entorno (.env)

```bash
cp .env.example .env
python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"
nano .env
```

Completar el archivo (pegar la clave generada en `SECRET_KEY`):

```ini
SECRET_KEY=la-clave-generada-en-el-paso-anterior
DEBUG=False
ALLOWED_HOSTS=IP_PUBLICA,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://IP_PUBLICA
DB_NAME=zonaocio_db
DB_USER=zonaocio_user
DB_PASSWORD=CLAVE_SEGURA
DB_HOST=localhost
DB_PORT=3306
```

Guardar con `Ctrl + O`, `Enter` y salir con `Ctrl + X`.

> El archivo `.env` **no** está en GitHub (se ignora en `.gitignore`). Por eso se crea directamente en el servidor.

---

## 8. Migraciones, datos y superusuario

```bash
python manage.py check
python manage.py migrate                 # crea todas las tablas en MySQL
python manage.py showmigrations          # [X] = migración aplicada
python manage.py importar_videojuegos    # migra videojuegos.json a la base de datos
python manage.py importar_peliculas      # migra peliculas.json a la base de datos
python manage.py createsuperuser         # usuario para Django Admin
python manage.py collectstatic --noinput # reúne Bootstrap, CSS e imágenes
```

📸 **CAPTURA:** `migrate`, `showmigrations` y los comandos de importación.

---

## 9. Servidor de la aplicación: Gunicorn como servicio

```bash
sudo cp deploy/zonaocio.service /etc/systemd/system/zonaocio.service
sudo systemctl daemon-reload
sudo systemctl enable --now zonaocio
sudo systemctl status zonaocio           # debe decir: active (running)
```

> Si tu usuario no es `ubuntu` o clonaste en otra carpeta, ajusta las rutas en `deploy/zonaocio.service`.

---

## 10. Servidor web: Apache

```bash
sudo cp deploy/zonaocio-apache.conf /etc/apache2/sites-available/zonaocio.conf
sudo a2enmod proxy proxy_http
sudo a2dissite 000-default
sudo a2ensite zonaocio
sudo apache2ctl configtest               # debe decir: Syntax OK
sudo systemctl reload apache2
```

---

## 11. Probar en el navegador

| URL | Qué se ve |
|---|---|
| `http://IP_PUBLICA/` | Sitio ZonaOcio |
| `http://IP_PUBLICA/admin/` | Django Admin (usuario creado con `createsuperuser`) |
| `http://IP_PUBLICA/phpmyadmin/` | phpMyAdmin (usuario `zonaocio_user` y su clave) |

📸 **CAPTURAS:**
- Sitio funcionando con la IP pública en la barra de direcciones.
- Django Admin con todas las entidades.
- phpMyAdmin: lista de tablas de `zonaocio_db`, pestaña **Browse** de una tabla con registros
  y **Structure → Relation view** de `videojuegos_videojuego` o `peliculas_pelicula` (llaves foráneas).

---

## 12. Crear registros desde Django Admin

La evaluación pide demostrar **registros creados mediante Django Admin**. Por ejemplo:

1. **Videojuegos → Géneros → Añadir:** `Terror`.
2. **Videojuegos → Videojuegos → Añadir:** un videojuego nuevo usando ese género, una desarrolladora y plataformas.
3. **Películas → Directores → Añadir:** un director nuevo, y luego una película asociada a él.
4. Verificar en phpMyAdmin que los registros nuevos aparecen en las tablas.

📸 **CAPTURA:** el registro creado en Django Admin y el mismo registro en phpMyAdmin.

---

## Actualizar el proyecto después de un cambio

```bash
cd ~/Trabajo-Backend2026
source venv/bin/activate
git pull
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart zonaocio
```

## Problemas frecuentes

| Problema | Solución |
|---|---|
| **Bad Request (400)** | La IP no está en `ALLOWED_HOSTS` del `.env`. Agregarla y ejecutar `sudo systemctl restart zonaocio`. |
| **La IP cambió** | Al detener/iniciar la instancia, AWS asigna otra IP pública. Actualizar `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS` y reiniciar el servicio. |
| **CSRF verification failed** al entrar al Admin | Revisar `CSRF_TRUSTED_ORIGINS=http://IP_PUBLICA` en el `.env` y reiniciar el servicio. |
| **503 Service Unavailable** | Gunicorn no está corriendo: `sudo journalctl -u zonaocio -n 50` para ver el error. |
| **phpMyAdmin muestra código PHP** | Falta `libapache2-mod-php`: instalarlo y `sudo systemctl restart apache2`. |
| **No carga la página** | Revisar que el Security Group tenga abierto el puerto 80. |
| **El sitio y phpMyAdmin cargan muy lento** | Falta memoria: crear el swap del paso 3 y dejar Gunicorn con `--workers 2`. Revisar también en EC2 → *Monitoring* que el *CPU credit balance* no esté en 0. |
| **Tarda varios segundos antes de abrir** | El navegador intenta `https://` primero. Escribir la dirección completa: `http://IP_PUBLICA/`. |

---

## Checklist para la revisión presencial

| Requisito | Cómo demostrarlo |
|---|---|
| Conexión a EC2 | `ssh -i zonaocio-clave.pem ubuntu@IP_PUBLICA` o EC2 Instance Connect |
| Proyecto clonado desde GitHub | `cd ~/Trabajo-Backend2026 && git remote -v && git log --oneline` |
| Entorno virtual activo | `source venv/bin/activate` → aparece `(venv)` |
| Servidor web ejecutando la app | `sudo systemctl status zonaocio` y `sudo systemctl status apache2` |
| Modelos creados | Mostrar `videojuegos/models.py` y `peliculas/models.py` |
| Migraciones aplicadas | `python manage.py showmigrations` y los archivos `*/migrations/0001_initial.py` |
| Variables de entorno | `cat .env.example` y `zonaocio/settings.py` (usa `os.environ` / `load_dotenv`) |
| Tablas en phpMyAdmin | `http://IP_PUBLICA/phpmyadmin/` → base `zonaocio_db` |
| Relaciones | phpMyAdmin → tabla → **Structure** → **Relation view** |
| Registros almacenados | phpMyAdmin → tabla → **Browse** |
| Django Admin: crear, editar, eliminar, buscar | `http://IP_PUBLICA/admin/` |
| Listados desde la BD con ORM | Menús **Videojuegos** y **Películas** del sitio |
| Botones Agregar, Modificar, Eliminar y Buscar | Visibles en cada listado |
