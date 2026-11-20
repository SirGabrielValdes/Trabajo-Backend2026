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
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu_correo@gmail.com
EMAIL_HOST_PASSWORD=contrasena-de-aplicacion
DEFAULT_FROM_EMAIL=ZonaOcio <tu_correo@gmail.com>
```

Guardar con `Ctrl + O`, `Enter` y salir con `Ctrl + X`.

### Correo para recuperar contraseñas (Gmail)

La recuperación de contraseña envía un correo real. Con Gmail se usa una **contraseña de aplicación**
(no la contraseña normal de la cuenta):

1. En la cuenta de Google, activar la **verificación en 2 pasos**.
2. Entrar a <https://myaccount.google.com/apppasswords>, crear una contraseña de aplicación llamada `ZonaOcio`.
3. Copiar los 16 caracteres **sin espacios** en `EMAIL_HOST_PASSWORD`.
4. En `EMAIL_HOST_USER` y `DEFAULT_FROM_EMAIL` va el mismo correo de Gmail.

> Si `EMAIL_HOST` queda vacío, el correo no se envía: se muestra en el registro del servidor
> (`sudo journalctl -u zonaocio -n 50`). Sirve solo para pruebas.

> El archivo `.env` **no** está en GitHub (se ignora en `.gitignore`). Por eso se crea directamente en el servidor.

---

## 8. Migraciones, datos y superusuario

```bash
python manage.py check
python manage.py migrate                 # crea todas las tablas en MySQL
python manage.py showmigrations          # [X] = migración aplicada
python manage.py importar_videojuegos    # migra videojuegos.json a la base de datos
python manage.py importar_peliculas      # migra peliculas.json a la base de datos
python manage.py crear_roles             # perfiles Administrador, Supervisor y Administrativo
python manage.py createsuperuser         # primer usuario (acceso total, perfil Administrador)
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
| `http://IP_PUBLICA/cuentas/login/` | Inicio de sesión (usuario creado con `createsuperuser`) |
| `http://IP_PUBLICA/phpmyadmin/` | phpMyAdmin (usuario `zonaocio_user` y su clave) |

📸 **CAPTURAS:**
- Sitio funcionando con la IP pública en la barra de direcciones.
- Login y Dashboard del Administrador.
- phpMyAdmin: lista de tablas de `zonaocio_db`, pestaña **Browse** de una tabla con registros
  y **Structure → Relation view** de `videojuegos_videojuego` o `peliculas_pelicula` (llaves foráneas).

---

## 12. Crear usuarios y asignar perfiles

Desde la Evaluación N°3 **no se usa Django Admin**: todo se hace desde las páginas del sitio.

1. Ingresar en `http://IP_PUBLICA/cuentas/login/` con el superusuario.
2. Menú del usuario → **Gestión de usuarios** → **+ Agregar**.
3. Crear al menos un usuario **Supervisor** y uno **Administrativo**, con un **correo real** (sirve para
   probar la recuperación de contraseña).
4. Cerrar sesión e ingresar con cada usuario para ver su dashboard y sus restricciones.

📸 **CAPTURA:** listado de usuarios con sus perfiles y el dashboard de cada perfil.

---

## 13. Actualizar una instancia que ya tenía la Evaluación N°2

Si la EC2 ya tenía el proyecto funcionando, basta con traer los cambios:

```bash
cd ~/Trabajo-Backend2026
source venv/bin/activate
git pull
pip install -r requirements.txt
python manage.py migrate                 # agrega stock y las tablas de ventas
python manage.py crear_roles             # crea los perfiles y sus permisos
python manage.py collectstatic --noinput
nano .env                                # agregar las variables EMAIL_* (paso 7)
sudo systemctl restart zonaocio
```

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
| **CSRF verification failed** al iniciar sesión | Revisar `CSRF_TRUSTED_ORIGINS=http://IP_PUBLICA` en el `.env` y reiniciar el servicio. |
| **503 Service Unavailable** | Gunicorn no está corriendo: `sudo journalctl -u zonaocio -n 50` para ver el error. |
| **phpMyAdmin muestra código PHP** | Falta `libapache2-mod-php`: instalarlo y `sudo systemctl restart apache2`. |
| **No carga la página** | Revisar que el Security Group tenga abierto el puerto 80. |
| **El sitio y phpMyAdmin cargan muy lento** | Falta memoria: crear el swap del paso 3 y dejar Gunicorn con `--workers 2`. Revisar también en EC2 → *Monitoring* que el *CPU credit balance* no esté en 0. |
| **No llega el correo de recuperación** | Revisar spam. Revisar `EMAIL_*` en `.env` (contraseña de aplicación de 16 caracteres sin espacios, puerto 587, `EMAIL_USE_TLS=True`), reiniciar el servicio y ver el error con `sudo journalctl -u zonaocio -n 50`. El usuario debe tener ese correo registrado. |
| **El enlace del correo dice "no válido"** | El enlace vence en 1 hora y sirve una sola vez. Solicitar uno nuevo. |
| **Tarda varios segundos antes de abrir** | El navegador intenta `https://` primero. Escribir la dirección completa: `http://IP_PUBLICA/`. |

---

## Checklist para la revisión presencial (Evaluación N°3)

| Requisito | Cómo demostrarlo |
|---|---|
| Inicio y cierre de sesión | `http://IP_PUBLICA/cuentas/login/` → ingresar → menú del usuario → **Cerrar sesión** |
| Protección de vistas | Sin sesión, abrir `http://IP_PUBLICA/ventas/` → redirige al login |
| Usuarios y perfiles | Menú del usuario → **Gestión de usuarios** → crear usuario y asignar perfil |
| Restricción de accesos | Con Administrativo, abrir `http://IP_PUBLICA/cuentas/usuarios/` → **Acceso denegado (403)** |
| Recuperación de contraseña | Login → **¿Olvidaste tu contraseña?** → correo → abrir enlace → nueva contraseña → ingresar |
| Dashboards | Ingresar con Administrador, Supervisor y Administrativo → **Panel** |
| Mantenedores (CRUD) | Ej. **Videojuegos → Géneros**: Agregar, Buscar, Modificar, Eliminar (con validaciones) |
| Transacción | **Ventas → Nueva venta** → ver detalle, total y descuento de stock |
| Registro en BD | phpMyAdmin → `ventas_venta` y `ventas_detalleventa` → **Browse** |
| Relaciones | phpMyAdmin → `ventas_detalleventa` → **Structure → Relation view** |
| Migraciones | `python manage.py showmigrations` |
| GitHub | `git log --oneline` (desarrollo incremental) y el repositorio en GitHub |
| AWS | Aplicación funcionando en `http://IP_PUBLICA/` desde la EC2 |
