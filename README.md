# YouTube Searcher & MeTube Bridge

Una aplicación ligera basada en **Flask** que actúa como puente para buscar videos en YouTube de forma fiable y enviarlos automáticamente a una instancia de **MeTube** para su descarga.

## Características
* **Búsqueda Robusta:** Utiliza `ytmusicapi` para realizar búsquedas rápidas y evitar bloqueos por parte de YouTube (sin necesidad de cookies).
* **Integración con MeTube:** Envía URLs directamente a tu servidor MeTube mediante una API.
* **Ligero:** No requiere complejas configuraciones de autenticación.

## Requisitos Previos
* Python 3.x
* Una instancia de [MeTube](https://github.com/alexta69/metube) corriendo en tu red.

## Instalación

1. Clona o copia los archivos en tu servidor (ej. `/opt/youtube-searcher/`).
2. Instala las dependencias necesarias:

```bash
pip install flask requests ytmusicapi

```


Aquí tienes una estructura profesional y clara para tu archivo `README.md`. Este documento ayudará a cualquier persona (o a ti mismo en el futuro) a entender qué hace el proyecto, cómo instalarlo y cómo funciona.

Copia este contenido en un archivo llamado `README.md` dentro de la carpeta `/opt/youtube-searcher/`:

---


## Configuración

Edita la variable `METUBE_URL` en tu archivo `app.py` para que coincida con la dirección IP y puerto de tu instancia de MeTube:

```python
# app.py
METUBE_URL = "[http://192.168.10.5:8081](http://192.168.10.5:8081)"

```

## Ejecución

Para iniciar el servidor:

```bash
python3 app.py

```

El servicio estará disponible en `http://<IP_DE_TU_SERVIDOR>:5000`.

## ¿Cómo funciona?

El sistema separa las responsabilidades en dos módulos clave:

1. **Búsqueda (`/search`):** Emplea `ytmusicapi` para consultar los metadatos de YouTube. Esta librería simula una petición limpia que elude las restricciones anti-bot, garantizando que siempre obtengas resultados sin errores de "Sign in".
2. **Descarga (`/download`):** Envía la URL seleccionada al endpoint `/add` de MeTube. MeTube se encarga de gestionar la descarga, conversión y almacenamiento del video internamente.

## Solución de Problemas

* **Error de conexión con MeTube:** Verifica que la IP definida en `METUBE_URL` sea accesible desde el servidor donde corre este script.
* **El script no inicia:** Asegúrate de tener instaladas todas las librerías mencionadas en la sección de instalación.

## Licencia

Este proyecto es de código abierto. ¡Siéntete libre de mejorarlo!
