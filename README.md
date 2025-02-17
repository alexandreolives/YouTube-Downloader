# Téléchargeur YouTube via Flask et yt-dlp

Ce projet est une interface web permettant de télécharger des vidéos YouTube ou d'extraire leur audio (mp3) en utilisant l'outil yt-dlp. Le back-end est développé avec Flask en Python et le front-end est une simple page HTML en français.

## Fonctionnalités

- Téléchargement de vidéos en utilisant la meilleure qualité vidéo+audio fusionnée en MP4.
- Extraction de l'audio en format MP3.
- Génération d'un lien de téléchargement une fois le fichier généré.
- Interface utilisateur simple et moderne avec HTML/CSS.

## Prérequis

- Python 3.x
- Flask (installable via pip)
- yt-dlp (installé sur votre système et accessible dans le PATH)
- ffmpeg (nécessite ffprobe et ffmpeg pour le post-traitement)

## Installation

1. Clonez ce dépôt ou téléchargez le code source.

2. Installez les dépendances Python:

   ```batch
   pip install -r requirements.txt
   ```

### Installation de FFmpeg sur Windows

Pour installer FFmpeg sur Windows, vous pouvez utiliser winget. Exécutez la commande suivante dans votre terminal :

   winget install ffmpeg --source winget

Assurez-vous également d'ajouter le dossier "bin" de FFmpeg à votre variable d'environnement PATH. Par exemple, si vous avez installé FFmpeg via winget, ajoutez le chemin suivant :

   C:\Users\XXXX\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-7.1-full_build\bin

## Utilisation

1. Lancez le serveur Flask en exécutant le fichier `back.py`:

   ```bash
   python back.py
   ```

2. Ouvrez le fichier `front.html` dans votre navigateur pour accéder à l'interface utilisateur.

3. Entrez l'URL d'une vidéo YouTube et choisissez le format voulu (vidéo ou audio), puis cliquez sur "Télécharger".

4. Une fois le téléchargement terminé, un lien sera fourni pour télécharger le fichier généré.

## Structure du projet

- `back.py` : Le serveur Flask qui gère les requêtes de téléchargement et exécute yt-dlp.
- `front.html` : L'interface utilisateur web permettant d'envoyer les URL des vidéos et d'obtenir les liens de téléchargement.
- `downloads/` : Dossier créé automatiquement pour stocker les fichiers téléchargés.

## Remarques

- Le projet crée automatiquement le dossier `downloads` si celui-ci n'existe pas.
- Assurez-vous que le dossier où le projet est installé dispose des droits suffisants pour créer et écrire dans le dossier `downloads`.

## Contributions

Les contributions sont les bienvenues. N'hésitez pas à soumettre des pull requests ou à ouvrir des issues pour signaler des bugs et proposer des améliorations.

## Licence

Ce projet est sous licence Fair Code avec Restriction Commerciale. Consultez le fichier LICENSE pour plus de détails. 