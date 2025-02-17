import os
import subprocess
import sys
import glob



def get_ffmpeg_path():
    """Détecte le chemin d'installation de ffmpeg."""
    try:
        # Obtenir le chemin d'installation via winget
        result = subprocess.run(['winget', 'list', '--id', 'Gyan.FFmpeg'], capture_output=True, text=True)
        if result.returncode == 0:
            # Obtenir le nom d'utilisateur Windows
            # username = os.getenv('USERNAME')
            # Construire le chemin vers ffmpeg
            base_path = os.path.expanduser('~')  # Donne C:\Users\{USERNAME}
            ffmpeg_path = os.path.join(base_path, 'AppData', 'Local', 'Microsoft', 'WinGet', 'Packages')
            
            # Chercher le dossier ffmpeg dans les packages
            for folder in os.listdir(ffmpeg_path):
                if 'Gyan.FFmpeg' in folder:
                    full_path = os.path.join(ffmpeg_path, folder, 'ffmpeg-*-full_build', 'bin')
                    # Utiliser glob pour trouver le bon dossier avec la version
                    matches = glob.glob(full_path)
                    if matches:
                        return matches[0]
            
        print('Impossible de détecter automatiquement le chemin de ffmpeg.')
        return None
    except Exception as e:
        print(f'Erreur lors de la détection du chemin de ffmpeg: {e}')
        return None


def create_dotenv():
    """Crée automatiquement le fichier .env avec la variable FFMPEG_LOCATION si il n'existe pas."""
    env_path = '.env'
    if not os.path.exists(env_path):
        ffmpeg_path = get_ffmpeg_path()
        if ffmpeg_path:
            with open(env_path, 'w') as f:
                f.write(f'FFMPEG_LOCATION={ffmpeg_path}\n')
            print('Fichier .env créé avec succès.')
        else:
            print('ATTENTION: Impossible de créer le .env avec le bon chemin ffmpeg.')
            print('Veuillez le créer manuellement une fois ffmpeg installé.')
    else:
        print('Fichier .env déjà présent.')


def install_ffmpeg():
    """Installe ffmpeg via winget (réservé à Windows)."""
    try:
        print('Installation de ffmpeg via winget...')
        # L'option '--source winget' est utilisée pour spécifier la source
        subprocess.run(['winget', 'install', 'ffmpeg', '--source', 'winget'], check=True)
        print('ffmpeg installé avec succès.')
    except Exception as e:
        print('Erreur lors de l\'installation de ffmpeg via winget:', e)
        print('Veuillez installer ffmpeg manuellement si besoin.')


def create_virtualenv():
    """Crée un virtualenv dans le dossier .venv s\'il n\'existe pas déjà."""
    venv_dir = '.venv'
    if not os.path.exists(venv_dir):
        print('Création du virtualenv dans', venv_dir, '...')
        subprocess.run([sys.executable, '-m', 'venv', venv_dir], check=True)
        print('Virtualenv créé avec succès.')
    else:
        print('Virtualenv déjà existant.')


def install_requirements():
    """Installe les dépendances depuis requirements.txt dans le virtualenv."""
    venv_dir = '.venv'
    if os.name == 'nt':
        pip_path = os.path.join(venv_dir, 'Scripts', 'pip.exe')
    else:
        pip_path = os.path.join(venv_dir, 'bin', 'pip')

    if not os.path.exists(pip_path):
        print('pip non trouvé dans le virtualenv. Vérifiez l\'installation du virtualenv.')
        return

    print('Installation des dépendances via pip...')
    subprocess.run([pip_path, 'install', '-r', 'requirements.txt'], check=True)
    print('Dépendances installées avec succès.')


def check_pyenv():
    """Vérifie si pyenv est installé et accessible."""
    try:
        result = subprocess.run('pyenv --version', shell=True, capture_output=True, text=True, check=True)
        print('pyenv trouvé:', result.stdout.strip())
        return True
    except Exception as e:
        print('pyenv n\'est pas installé ou n\'est pas reconnu. Si nécessaire, installez pyenv.')
        return False


def install_python_and_pyenv():
    """Installe pyenv puis Python via pyenv."""
    try:
        # Vérifier si pyenv est installé
        pyenv_check = subprocess.run('pyenv --version', shell=True, capture_output=True, text=True)
        print('pyenv déjà installé:', pyenv_check.stdout.strip())
    except FileNotFoundError:
        print('pyenv non trouvé, installation...')
        try:
            # Installation via PowerShell
            install_script = 'install-pyenv-win.ps1'
            ps_commands = [
                'Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"',
                f'powershell -ExecutionPolicy Bypass -File "./{install_script}"'
            ]
            
            for cmd in ps_commands:
                subprocess.run(['powershell', '-Command', cmd], check=True)
                
            print('pyenv installé avec succès.')
            
            # Supprimer le script d'installation
            if os.path.exists(install_script):
                os.remove(install_script)
                        
        except Exception as e:
            print('Erreur lors de l\'installation de pyenv:', e)
            print('Veuillez installer pyenv manuellement: https://github.com/pyenv-win/pyenv-win#installation')
            sys.exit(1)

    # Installation de Python via pyenv
    python_version = "3.13.2"  # Version stable récente
    try:
        # Vérifier si la version est déjà installée
        installed_versions = subprocess.run('pyenv versions', shell=True, capture_output=True, text=True).stdout
        if python_version not in installed_versions:
            print(f'Installation de Python {python_version} via pyenv...')
            subprocess.run(f'pyenv install {python_version}', shell=True, check=True)
            subprocess.run(f'pyenv global {python_version}', shell=True, check=True)
            print(f'Python {python_version} installé et défini comme version globale.')
        else:
            print(f'Python {python_version} déjà installé via pyenv.')
            subprocess.run(f'pyenv global {python_version}', shell=True, check=True)
    except Exception as e:
        print(f'Erreur lors de l\'installation de Python {python_version}:', e)
        sys.exit(1)


def main():
    # Installation de Python et pyenv en premier
    install_python_and_pyenv()
    
    # Vérification de pyenv
    check_pyenv()
    
    # Création de l'environnement virtuel et installation des dépendances
    create_virtualenv()
    install_requirements()
    
    # Installation de ffmpeg et création du .env
    install_ffmpeg()
    create_dotenv()


if __name__ == '__main__':
    main() 