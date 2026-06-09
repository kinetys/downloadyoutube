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

1. Copia el script o descarga el fichero app.py a (ej. `/opt/youtube-searcher/`).
   
```bash
from flask import Flask, render_template, request, jsonify
import requests
from ytmusicapi import YTMusic # Nueva importación

app = Flask(__name__)

# ================= CONFIGURACIÓN =================
METUBE_URL = "http://IP-APP-METUBE:8081"
ytmusic = YTMusic() # Inicializamos el cliente de búsqueda
# =================================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query')
    if not query:
        return jsonify({'error': 'No query provided'}), 400

    try:
        # Usamos ytmusicapi para buscar. Es rápido, estable y no requiere cookies.
        results = ytmusic.search(query, filter="videos", limit=5)
        
        videos = []
        for item in results:
            videos.append({
                'title': item.get('title', 'Sin título'),
                'url': f"https://www.youtube.com/watch?v={item.get('videoId', '')}",
                # Obtenemos la última miniatura (la de mayor resolución disponible)
                'thumbnail': item.get('thumbnails', [{}])[-1].get('url', ''),
                'duration': item.get('duration', '?')
            })
            
        return jsonify({'results': videos})
    except Exception as e:
        # En caso de error, lo imprimimos en log para depurar
        print(f"Error en búsqueda: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json(force=True, silent=True)
    
    video_url = None
    if data:
        video_url = data.get('url')
    
    if not video_url:
        return jsonify({'status': 'error', 'message': 'No URL provided en el JSON'}), 400

    try:
        api_endpoint = f"{METUBE_URL}/add"
        payload = {"url": video_url}
        
        response = requests.post(api_endpoint, json=payload, timeout=10)
        
        if response.status_code in [200, 201]:
            return jsonify({'status': 'success', 'message': 'Enviado a me-tube (MP3)'})
        else:
            return jsonify({
                'status': 'error', 
                'message': f'HTTP {response.status_code}: {response.text[:100]}'
            }), response.status_code
            
    except requests.exceptions.ConnectionError:
        return jsonify({'status': 'error', 'message': 'No se pudo conectar a MeTube'}), 503
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

  
3. Instala las dependencias necesarias:

```bash
pip install flask requests ytmusicapi

```
2. Copia el codigo o descarga el fichero index.html a (ej. `/opt/youtube-searcher/templates`).

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Buscador YouTube → MeTube</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .video-card { cursor: pointer; transition: transform 0.2s; }
        .video-card:hover { transform: scale(1.02); background-color: #f8f9fa; }
        .thumbnail { width: 120px; height: 90px; object-fit: cover; }
        #loading { display: none; }
    </style>
</head>
<body class="bg-light">
    <div class="container py-5">
        <h1 class="text-center mb-2">🎵 Buscador YouTube → MeTube</h1>
        <p class="text-center text-muted mb-4">Descarga audio de tus canciones favoritas</p>
        
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="input-group mb-3">
                    <input type="text" id="searchInput" class="form-control form-control-lg" placeholder="Ej: Musica lofi para estudiar...">
                    <button class="btn btn-primary" type="button" onclick="searchVideos()">Buscar</button>
                </div>
            </div>
        </div>

        <div id="loading" class="text-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Cargando...</span>
            </div>
            <p>Buscando en YouTube...</p>
        </div>

        <div id="results" class="row mt-4"></div>
    </div>

    <script>
        async function searchVideos() {
            const query = document.getElementById('searchInput').value;
            const resultsDiv = document.getElementById('results');
            const loadingDiv = document.getElementById('loading');
            
            if (!query) return alert('Escribe algo para buscar');

            resultsDiv.innerHTML = '';
            loadingDiv.style.display = 'block';

            try {
                const formData = new FormData();
                formData.append('query', query);

                const response = await fetch('/search', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();
                loadingDiv.style.display = 'none';

                if (data.error) {
                    alert('Error: ' + data.error);
                    return;
                }

                if (data.results.length === 0) {
                    resultsDiv.innerHTML = '<div class="col-12 text-center text-muted">No se encontraron resultados</div>';
                    return;
                }

                data.results.forEach((video, index) => {
                    const col = document.createElement('div');
                    col.className = 'col-md-6 mb-3';
                    col.innerHTML = `
                        <div class="card video-card p-2" data-url="${video.url}">
                            <div class="d-flex align-items-center">
                                <img src="${video.thumbnail}" class="thumbnail rounded me-3">
                                <div>
                                    <h6 class="mb-1 text-truncate" style="max-width: 300px;">${video.title}</h6>
                                    <small class="text-muted">Duración: ${video.duration}</small>
                                    <div><span class="badge bg-success">Click para descargar</span></div>
                                </div>
                            </div>
                        </div>
                    `;
                    col.querySelector('.video-card').addEventListener('click', function() {
                        sendToMetube(this.getAttribute('data-url'));
                    });
                    resultsDiv.appendChild(col);
                });

            } catch (error) {
                loadingDiv.style.display = 'none';
                alert('Error de conexión');
                console.error(error);
            }
        }

        async function sendToMetube(url) {
            if(!confirm('¿Enviar este video a MeTube para descargar el audio MP3?')) return;

            console.log('URL a enviar:', url);

            try {
                const response = await fetch('/download', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: url })
                });
                
                const data = await response.json();
                console.log('Respuesta:', data);
                
                if (data.status === 'success') {
                    alert('✅ ¡Enviado a MeTube correctamente!');
                } else {
                    alert('❌ Error al enviar: ' + (data.message || 'Error desconocido'));
                }
            } catch (error) {
                alert('Error de conexión: ' + error.message);
            }
        }

        document.getElementById('searchInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') searchVideos();
        });
    </script>
</body>
</html>
```
---


## Configuración

Edita la variable `METUBE_URL` en tu archivo `app.py` para que coincida con la dirección IP y puerto de tu instancia de MeTube:

```python
# app.py
METUBE_URL = "http://IP-APP-METUBE:8081"

```

## Ejecución

Para iniciar el servidor:

```bash
python3 app.py

```

El servicio estará disponible en `http://<IP_DE_TU_SERVIDOR>:5000`.


---

### Configuración como Servicio (Autoinicio)

Para que tu aplicación se inicie automáticamente al arrancar el servidor Linux y se mantenga ejecutándose en segundo plano, sigue estos pasos:

1. Crea el archivo de servicio:
```bash
nano /etc/systemd/system/youtube-searcher.service

```


2. Pega el siguiente contenido (asegúrate de que las rutas coincidan con tu instalación):
```ini
[Unit]
Description=YouTube Searcher for MeTube
After=network.target

[Service]
User=root
WorkingDirectory=/opt/youtube-searcher
ExecStart=/usr/bin/python3 /opt/youtube-searcher/app.py
Environment=PYTHONUNBUFFERED=1
Restart=always

# Logs
StandardOutput=append:/opt/youtube-searcher/downyoutube.log
StandardError=append:/opt/youtube-searcher/downyoutube.log

[Install]
WantedBy=multi-user.target

```


3. Recarga la configuración de `systemd`, habilita el servicio e inicia la aplicación:
```bash
systemctl daemon-reload
systemctl enable youtube-searcher
systemctl start youtube-searcher

```


4. Para verificar que todo funciona correctamente, puedes ver el estado del servicio en cualquier momento con:
```bash
systemctl status youtube-searcher

```



---

### Notas adicionales sobre esta configuración:

* **`Restart=always`**: Si el script llega a fallar por cualquier motivo imprevisto, el sistema lo reiniciará automáticamente.
* **`PYTHONUNBUFFERED=1`**: Es muy importante para que todo lo que imprima el script (los `print`) aparezca en el log (`downyoutube.log`) en tiempo real, sin esperar a que el búfer se llene.
* **Logs**: Si alguna vez tienes problemas, solo tienes que hacer un `tail -f /opt/youtube-searcher/downyoutube.log` para ver qué está ocurriendo en el servidor minuto a minuto.

## ¿Cómo funciona?

El sistema separa las responsabilidades en dos módulos clave:

1. **Búsqueda (`/search`):** Emplea `ytmusicapi` para consultar los metadatos de YouTube. Esta librería simula una petición limpia que elude las restricciones anti-bot, garantizando que siempre obtengas resultados sin errores de "Sign in".
2. **Descarga (`/download`):** Envía la URL seleccionada al endpoint `/add` de MeTube. MeTube se encarga de gestionar la descarga, conversión y almacenamiento del video internamente.

## Solución de Problemas

* **Error de conexión con MeTube:** Verifica que la IP definida en `METUBE_URL` sea accesible desde el servidor donde corre este script.
* **El script no inicia:** Asegúrate de tener instaladas todas las librerías mencionadas en la sección de instalación.

## Licencia

Este proyecto es de código abierto. ¡Siéntete libre de mejorarlo!
