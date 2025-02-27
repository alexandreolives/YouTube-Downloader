from flask import Flask, request, jsonify, send_from_directory, render_template
import subprocess
import os
import uuid
from dotenv import load_dotenv
import webbrowser
import threading
import time
import hashlib

app = Flask(__name__)

# Variables pour suivre les modifications
last_modified = {}
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

def get_file_hash(filepath):
    """Calcule le hash d'un fichier pour détecter les modifications"""
    if os.path.exists(filepath):
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    return None

def update_file_hashes():
    """Met à jour les hashes des fichiers surveillés"""
    files_to_watch = [
        os.path.join(template_dir, 'index.html'),
        __file__  # Le fichier back.py lui-même
    ]
    
    for filepath in files_to_watch:
        last_modified[filepath] = get_file_hash(filepath)

# Initialiser les hashes
update_file_hashes()

@app.route('/check_changes')
def check_changes():
    """Vérifie si des fichiers ont été modifiés"""
    changes_detected = False
    
    for filepath, old_hash in last_modified.items():
        current_hash = get_file_hash(filepath)
        if current_hash != old_hash:
            changes_detected = True
            last_modified[filepath] = current_hash
    
    return jsonify({'reload': changes_detected})

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
        formats = {
            'video': [],
            'audio': [],
            'both': []
        }
        
        for line in output.split('\n'):
            if line and not line.startswith('['):
                # Ignorer les lignes d'en-tête
                if not line.startswith('ID') and not line.startswith('-'):
                    # Exemple de ligne: "248 webm 1920x1080 1080p60 | 151MB"
                    parts = line.split()
                    if len(parts) >= 2:
                        format_id = parts[0]
                        format_info = ' '.join(parts[1:])
                        
                        format_data = {
                            'id': format_id,
                            'description': format_info,
                            'resolution': None,
                            'filesize': None,
                            'vcodec': None,
                            'acodec': None
                        }
                        
                        # Extraire la résolution si présente
                        for part in parts:
                            if 'x' in part and all(c.isdigit() or c == 'x' for c in part):
                                format_data['resolution'] = part
                            elif part.endswith('p'):
                                format_data['quality'] = part
                            elif 'MB' in part or 'GB' in part:
                                format_data['filesize'] = part
                        
                        # Catégoriser le format
                        if 'audio only' in format_info.lower():
                            formats['audio'].append(format_data)
                        elif 'video only' in format_info.lower():
                            formats['video'].append(format_data)
                        else:
                            formats['both'].append(format_data)
        
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
        command = ['yt-dlp']

        # Cas spécial pour le MP3
        if format_id == 'ba[ext=mp3]':
            command.extend([
                '--extract-audio',
                '--audio-format', 'mp3',
                '--audio-quality', '0'
            ])
        # Autres formats audio
        elif 'ba[ext=' in format_id:
            command.extend([
                '--extract-audio',
                '--audio-format', format_id.split('ext=')[1].rstrip(']'),
                '--audio-quality', '0'
            ])
        # Formats vidéo ou combinés
        else:
            command.extend(['-f', format_id])

        # Ajouter les options communes
        command.extend([
            '--ffmpeg-location', ffmpeg_location,
            '-o', output_template,
            video_url
        ])
        
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

@app.route('/delete_file/<filename>', methods=['DELETE'])
def delete_file(filename):
    try:
        file_path = os.path.join(DOWNLOAD_FOLDER, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({'success': True, 'message': 'Fichier supprimé'})
        return jsonify({'success': False, 'message': 'Fichier non trouvé'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

def open_browser():
    time.sleep(1.5)  # Attendre que Flask démarre
    try:
        webbrowser.open('http://localhost:5000', new=2)
    except Exception as e:
        print(f"Erreur lors de l'ouverture du navigateur : {e}")

if __name__ == '__main__':
    # Vérifier si nous sommes dans le processus principal de Flask
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        browser_thread = threading.Thread(target=open_browser, daemon=True)
        browser_thread.start()
    app.run(port=5000, debug=True, use_reloader=True)
