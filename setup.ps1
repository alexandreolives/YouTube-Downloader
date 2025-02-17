# Configuration de l'encodage en Latin-1
[Console]::OutputEncoding = [System.Text.Encoding]::GetEncoding('iso-8859-1')
$OutputEncoding = [System.Text.Encoding]::GetEncoding('iso-8859-1')

# Changer vers le répertoire du script
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Fonction pour afficher les messages avec couleur
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        $message = $args -join " "
        Write-Output $message
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Get-FFmpegPath {
    Write-ColorOutput Green "Detection du chemin FFmpeg..."
    try {
        # Verifier si FFmpeg est installe via winget
        $result = winget list --id Gyan.FFmpeg
        if ($LASTEXITCODE -eq 0) {
            $base_path = "$env:USERPROFILE\AppData\Local\Microsoft\WinGet\Packages"
            Get-ChildItem -Path $base_path -Directory | ForEach-Object {
                if ($_.Name -like "*Gyan.FFmpeg*") {
                    $full_path = Join-Path $_.FullName "ffmpeg-*-full_build\bin"
                    $matches = Get-Item $full_path
                    if ($matches) {
                        return $matches[0].FullName
                    }
                }
            }
        }
        Write-ColorOutput Yellow "Impossible de detecter automatiquement le chemin de FFmpeg."
        return $null
    }
    catch {
        Write-ColorOutput Red "Erreur lors de la detection du chemin de FFmpeg: $_"
        return $null
    }
}

function Create-DotEnv {
    Write-ColorOutput Green "Creation du fichier .env..."
    $env_path = ".env"
    if (-not (Test-Path $env_path)) {
        $ffmpeg_path = Get-FFmpegPath
        if ($ffmpeg_path) {
            Set-Content -Path $env_path -Value "FFMPEG_LOCATION=$ffmpeg_path"
            Write-ColorOutput Green "Fichier .env cree avec succes."
        }
        else {
            Write-ColorOutput Yellow "ATTENTION: Impossible de creer le .env avec le bon chemin FFmpeg."
            Write-ColorOutput Yellow "Veuillez le creer manuellement une fois FFmpeg installe."
        }
    }
    else {
        Write-ColorOutput Yellow "Fichier .env deja present."
    }
}

function Install-FFmpeg {
    Write-ColorOutput Green "Installation de FFmpeg via winget..."
    try {
        winget install ffmpeg --source winget
        Write-ColorOutput Green "FFmpeg installe avec succes."
    }
    catch {
        Write-ColorOutput Red "Erreur lors de l'installation de FFmpeg: $_"
        Write-ColorOutput Yellow "Veuillez installer FFmpeg manuellement si besoin."
    }
}

function Create-VirtualEnv {
    Write-ColorOutput Green "Creation du virtualenv..."
    $venv_dir = ".venv"
    if (-not (Test-Path $venv_dir)) {
        Write-ColorOutput Green "Creation du virtualenv dans $venv_dir..."
        python -m venv $venv_dir
        Write-ColorOutput Green "Virtualenv cree avec succes."
    }
    else {
        Write-ColorOutput Yellow "Virtualenv deja existant."
    }
}

function Install-Requirements {
    Write-ColorOutput Green "Installation des dependances..."
    $venv_dir = ".venv"
    $pip_path = Join-Path $venv_dir "Scripts\pip.exe"

    if (-not (Test-Path $pip_path)) {
        Write-ColorOutput Red "pip non trouve dans le virtualenv. Verifiez l'installation du virtualenv."
        return
    }

    Write-ColorOutput Green "Installation des dependances via pip..."
    & $pip_path install -r requirements.txt
    Write-ColorOutput Green "Dependances installees avec succes."
}

function Check-Pyenv {
    try {
        $result = pyenv --version
        Write-ColorOutput Green "pyenv trouve: $result"
        return $true
    }
    catch {
        Write-ColorOutput Yellow "pyenv n'est pas installe ou n'est pas reconnu. Si necessaire, installez pyenv."
        return $false
    }
}

function Install-PythonAndPyenv {
    try {
        # Verifier si pyenv est installe
        $pyenv_check = pyenv --version
        Write-ColorOutput Green "pyenv deja installe: $pyenv_check"
    }
    catch {
        Write-ColorOutput Green "Installation de pyenv..."
        try {
            $install_script = "install-pyenv-win.ps1"
            Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile $install_script
            & "./$install_script"
            
            Write-ColorOutput Green "pyenv installe avec succes!"
            
            # Supprimer le script d'installation
            if (Test-Path $install_script) {
                Remove-Item $install_script
            }
            
            # Rafraichir les variables d'environnement
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        }
        catch {
            Write-ColorOutput Red "Erreur lors de l'installation de pyenv: $_"
            Write-ColorOutput Yellow "Veuillez installer pyenv manuellement: https://github.com/pyenv-win/pyenv-win#installation"
            exit 1
        }
    }

    # Installation de Python via pyenv
    $python_version = "3.13.2"
    try {
        $installed_versions = pyenv versions
        if ($installed_versions -notcontains $python_version) {
            Write-ColorOutput Green "Installation de Python $python_version via pyenv..."
            pyenv install $python_version
            pyenv global $python_version
            Write-ColorOutput Green "Python $python_version installe et defini comme version globale."
        }
        else {
            Write-ColorOutput Yellow "Python $python_version deja installe via pyenv."
            pyenv global $python_version
        }
    }
    catch {
        Write-ColorOutput Red "Erreur lors de l'installation de Python $python_version : $_"
        exit 1
    }
}

# Exécution principale
Write-ColorOutput Cyan "Démarrage de l'installation..."

# Même ordre que dans install.py
Install-PythonAndPyenv
Check-Pyenv
Create-VirtualEnv
Install-Requirements
Install-FFmpeg
Create-DotEnv

Write-ColorOutput Green "Installation terminee avec succes!"
Write-Host "Appuyez sur une touche pour fermer..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 