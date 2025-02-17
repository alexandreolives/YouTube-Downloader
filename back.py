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

@app.route('/download', methods=['POST'])
def download_video():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Aucune donnée reçue'}), 400

    video_url = data.get('url')
    format_type = data.get('format')

    if not video_url or not format_type:
        return jsonify({'success': False, 'message': 'L\'URL et le format sont requis'}), 400

    # Génère un identifiant unique pour nommer le fichier
    unique_id = str(uuid.uuid4())

    # Définition du template de sortie en fonction du format choisi
    if format_type == 'video':
        # Télécharger la meilleure vidéo + audio, puis fusionner en mp4
        output_template = os.path.join(DOWNLOAD_FOLDER, f'{unique_id}.%(ext)s')
        command = [
            'yt-dlp', '-f', 'bestvideo+bestaudio',
            '--ffmpeg-location', ffmpeg_location,
            '--merge-output-format', 'mp4',
            '-o', output_template, video_url
        ]
    elif format_type == 'audio':
        # Extraire l'audio et le convertir en mp3
        output_template = os.path.join(DOWNLOAD_FOLDER, f'{unique_id}.%(ext)s')
        command = [
            'yt-dlp', '-x', '--audio-format', 'mp3',
            '--ffmpeg-location', ffmpeg_location,
            '-o', output_template, video_url
        ]
    else:
        return jsonify({'success': False, 'message': 'Format invalide'}), 400

    try:
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
