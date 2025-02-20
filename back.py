from flask import Flask, request, jsonify, send_from_directory, render_template
import subprocess
import os
import uuid
from dotenv import load_dotenv
import webbrowser
import threading
import time

app = Flask(__name__)

# Dossier pour stocker les fichiers téléchargés
DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

load_dotenv()
ffmpeg_location = os.getenv("FFMPEG_LOCATION")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_formats', methods=['POST'])
def get_formats():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'success': False, 'message': 'URL requise'}), 400

    video_url = data['url']
    
    try:
        # Obtenir la liste des formats disponibles
        command = [
            'yt-dlp', '-F',
            video_url
        ]
        output = subprocess.check_output(command, stderr=subprocess.STDOUT).decode()
        
        # Parser la sortie pour extraire les formats
        formats = []
        for line in output.split('\n'):
            if line and not line.startswith('['):
                # Ignorer les lignes d'en-tête
                if not line.startswith('ID') and not line.startswith('-'):
                    parts = line.split()
                    if len(parts) >= 2:
                        format_id = parts[0]
                        # Extraire la description du format
                        desc = ' '.join(parts[1:])
                        formats.append({
                            'id': format_id,
                            'description': desc
                        })
        
        return jsonify({
            'success': True,
            'formats': formats
        })
    except subprocess.CalledProcessError as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la récupération des formats : {e.output.decode()}'
        }), 500

@app.route('/download', methods=['POST'])
def download_video():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Aucune donnée reçue'}), 400

    video_url = data.get('url')
    format_id = data.get('format')

    if not video_url or not format_id:
        return jsonify({'success': False, 'message': 'L\'URL et le format sont requis'}), 400

    # Génère un identifiant unique pour nommer le fichier
    unique_id = str(uuid.uuid4())
    output_template = os.path.join(DOWNLOAD_FOLDER, f'{unique_id}.%(ext)s')

    try:
        # Télécharger avec le format spécifié
        command = [
            'yt-dlp',
            '-f', format_id,
            '--ffmpeg-location', ffmpeg_location,
            '-o', output_template,
            video_url
        ]
        
        # Exécute la commande yt-dlp
        subprocess.check_output(command, stderr=subprocess.STDOUT)
        
        # Recherche le fichier généré dans le dossier DOWNLOAD_FOLDER
        for filename in os.listdir(DOWNLOAD_FOLDER):
            if filename.startswith(unique_id):
                download_url = f'/download_file/{filename}'
                return jsonify({'success': True, 'downloadUrl': download_url})
        
        return jsonify({'success': False, 'message': 'Fichier non trouvé après téléchargement.'}), 500
    except subprocess.CalledProcessError as e:
        error_msg = e.output.decode()
        return jsonify({'success': False, 'message': f'Erreur lors du téléchargement : {error_msg}'}), 500

@app.route('/download_file/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

def open_browser():
    time.sleep(1.5)  # Attendre que Flask démarre
    try:
        webbrowser.open('http://localhost:5000', new=2)
    except Exception as e:
        print(f"Erreur lors de l'ouverture du navigateur : {e}")

if __name__ == '__main__':
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    app.run(port=5000, debug=False)
