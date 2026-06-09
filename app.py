from flask import Flask, render_template, request, jsonify
import requests
from ytmusicapi import YTMusic

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
