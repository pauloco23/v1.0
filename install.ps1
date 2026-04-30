# Primordium Installer
$dest = "$env:APPDATA\Primordium"
$repo = "https://raw.githubusercontent.com/pauloco23/v1.0/main"

Write-Host ""
Write-Host "  Installing Primordium..." -ForegroundColor Cyan

# Crear carpeta
if (!(Test-Path $dest)) { New-Item -ItemType Directory -Path $dest | Out-Null }

# Descargar archivos
Write-Host "  Downloading files..." -ForegroundColor Gray
Invoke-WebRequest -Uri "$repo/loader.py"  -OutFile "$dest\loader.py"
Invoke-WebRequest -Uri "$repo/runpe.py"   -OutFile "$dest\runpe.py"
Invoke-WebRequest -Uri "$repo/logo.png"   -OutFile "$dest\logo.png"

# Verificar Python
$py = Get-Command pythonw -ErrorAction SilentlyContinue
if (!$py) {
    Write-Host "  Python not found. Installing..." -ForegroundColor Yellow
    $pyInstaller = "$env:TEMP\python_installer.exe"
    Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe" -OutFile $pyInstaller
    Start-Process $pyInstaller -ArgumentList "/quiet InstallAllUsers=0 PrependPath=1" -Wait
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","User")
}

# Instalar dependencias
Write-Host "  Installing dependencies..." -ForegroundColor Gray
try { py -m pip install customtkinter pillow --quiet } catch {}
try { python -m pip install customtkinter pillow --quiet } catch {}
try { python3 -m pip install customtkinter pillow --quiet } catch {}

Write-Host ""
Write-Host "  Primordium installed!" -ForegroundColor Green
Write-Host ""
Start-Process pythonw -ArgumentList "`"$dest\loader.py`""
