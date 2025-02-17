@echo off
echo Installation de YT Downloader...

:: Exécuter PowerShell en tant qu'administrateur
powershell -Command "Start-Process powershell -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File \"%~dp0install.ps1\"' -Verb RunAs"

pause 