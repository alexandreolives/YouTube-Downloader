$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$PWD\YouTube Downloader.lnk")
$Shortcut.TargetPath = "$PWD\.venv\Scripts\python.exe"
$Shortcut.Arguments = "`"$PWD\back.py`""
$Shortcut.WorkingDirectory = "$PWD"
$Shortcut.IconLocation = "shell32.dll,231"
$Shortcut.Save()

Write-Host "Raccourci créé avec succès !" 