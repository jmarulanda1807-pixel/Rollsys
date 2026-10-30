# Guía de comandos de RollSys

Todos los comandos que usamos para armar el proyecto, en orden. Se ejecutan en la terminal de Linux (Penguin del Chromebook). Cada bloque se copia y se pega tal cual.

## 1. Instalar herramientas

    sudo apt update
    sudo apt install -y python3 python3-venv python3-pip git unzip wget
    python3 --version
    git --version

## 2. Crear el proyecto Django

    mkdir ~/tienda-patines
    cd ~/tienda-patines
    python3 -m venv venv
    source venv/bin/activate
    pip install django
    django-admin startproject patines_project .
    python manage.py startapp tienda
    pip freeze > requirements.txt
    code .

El punto al final de `startproject` es importante. Cuando el entorno está activo, la línea de la terminal empieza con `(venv)`.

## 3. Configurar el proyecto

En `patines_project/settings.py`: agregar `"tienda"` a `INSTALLED_APPS`, cambiar `LANGUAGE_CODE = "es"` y `TIME_ZONE = "America/Bogota"` (el nombre de la zona, no `UTC-5`), y al final del archivo:

    LOGIN_URL = "login"
    LOGIN_REDIRECT_URL = "panel"
    LOGOUT_REDIRECT_URL = "login"

En `patines_project/urls.py`:

    from django.contrib import admin
    from django.urls import include, path

    urlpatterns = [
        path("admin/", admin.site.urls),
        path("accounts/", include("django.contrib.auth.urls")),
        path("", include("tienda.urls")),
    ]

## 4. Base de datos y arranque

    python manage.py makemigrations tienda
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py runserver

Abrir http://localhost:8000/ y entrar con el usuario creado. Para detener el servidor: `Ctrl + C`.

## 5. Datos de ejemplo

    python manage.py cargar_ejemplo

Se puede repetir sin duplicar productos.

## 6. Git y GitHub (primera vez)

    printf 'venv/\n__pycache__/\n*.pyc\ndb.sqlite3\n.env\n.vscode/\n' > .gitignore
    git init -b main
    git config --global user.name "Tu Nombre"
    git config --global user.email "tu-correo@ejemplo.com"
    ssh-keygen -t ed25519 -C "tu-correo@ejemplo.com"
    cat ~/.ssh/id_ed25519.pub

Copiar la línea que muestra el último comando y pegarla en GitHub, en github.com/settings/keys, con **New SSH key**. Luego:

    ssh -T git@github.com
    git add .
    git commit -m "Proyecto base"
    git remote add origin git@github.com:jmarulanda1807-pixel/Rollsys.git
    git push -u origin main

## 7. Guardar cambios (todos los días)

    git status
    git add .
    git commit -m "Describe lo que hiciste"
    git push

Antes de empezar a trabajar: `git pull`.

## 8. Cómo se suma cada compañero

Primero debe aceptar la invitación al repositorio. Después:

    git clone git@github.com:jmarulanda1807-pixel/Rollsys.git
    cd Rollsys
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py cargar_ejemplo
    python manage.py runserver

Cada quien tiene su propia base de datos (`db.sqlite3` no se comparte).

## 9. Trabajo en ramas

    git checkout main
    git pull
    git checkout -b feature/nombre-de-la-tarea
    git add .
    git commit -m "Describe lo que hiciste"
    git push -u origin feature/nombre-de-la-tarea

Luego se abre un Pull Request en GitHub para que otro compañero lo revise.

## 10. Enlace público temporal

Instalar cloudflared (una sola vez):

    wget -O /tmp/cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
    sudo apt install -y /tmp/cloudflared.deb

En `settings.py` deben estar estas dos líneas:

    ALLOWED_HOSTS = ["localhost", "127.0.0.1", ".trycloudflare.com"]
    CSRF_TRUSTED_ORIGINS = ["https://*.trycloudflare.com"]

Crear un usuario para los invitados y ponerle contraseña (no usar la del administrador):

    python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_user('amigos')"
    python manage.py changepassword amigos

Encender, en dos pestañas de la terminal (con el `+` de arriba):

    python manage.py runserver
    cloudflared tunnel --url http://localhost:8000

El enlace `https://....trycloudflare.com` cambia cada vez. Funciona solo mientras las dos pestañas estén abiertas y el computador esté despierto.

## 11. Problemas comunes

- **No aparece `(venv)`:** `cd ~/tienda-patines` y luego `source venv/bin/activate`.
- **La terminal no deja escribir:** el servidor está corriendo; `Ctrl + C`.
- **`Incorrect timezone setting`:** usar `America/Bogota`, no `UTC-5`.
- **`dpkg was interrupted`:** `sudo dpkg --configure -a` y repetir la instalación.
- **`Key is invalid` en GitHub:** copiar la clave con `code ~/.ssh/id_ed25519.pub`, `Ctrl + A`, `Ctrl + C`.
