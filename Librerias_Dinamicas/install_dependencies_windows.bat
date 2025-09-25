@echo off
echo === Instalando dependencias para Windows ===

REM Verificar si Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python no está instalado o no está en el PATH
    echo Por favor instala Python desde https://www.python.org/downloads/
    exit /b 1
)

echo Python encontrado:
python --version

REM Verificar si pip está disponible
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: pip no está disponible
    exit /b 1
)

echo pip encontrado:
pip --version

REM Instalar SWIG
echo.
echo Instalando SWIG...
echo Opción 1: Usar chocolatey (recomendado)
echo choco install swig
echo.
echo Opción 2: Descargar manualmente
echo 1. Ve a https://www.swig.org/download.html
echo 2. Descarga la versión para Windows
echo 3. Extrae y agrega al PATH
echo.

REM Verificar si SWIG está instalado
swig -version >nul 2>&1
if %errorlevel% neq 0 (
    echo SWIG no está instalado. Por favor instálalo siguiendo las instrucciones arriba.
    echo.
    echo Alternativamente, puedes usar WSL (Windows Subsystem for Linux):
    echo 1. Instala WSL desde Microsoft Store
    echo 2. Ejecuta: wsl
    echo 3. Ejecuta: sudo apt-get update && sudo apt-get install swig g++
    echo 4. Ejecuta el script build_scripts.sh en WSL
) else (
    echo SWIG encontrado:
    swig -version
)

REM Verificar si g++ está disponible
g++ --version >nul 2>&1
if %errorlevel% neq 0 (
    echo g++ no está disponible. Instalando MinGW...
    echo.
    echo Opción 1: Usar chocolatey
    echo choco install mingw
    echo.
    echo Opción 2: Descargar manualmente
    echo 1. Ve a https://www.mingw-w64.org/downloads/
    echo 2. Descarga MinGW-w64
    echo 3. Instala y agrega al PATH
) else (
    echo g++ encontrado:
    g++ --version
)

echo.
echo === Instrucciones de compilación ===
echo Una vez que tengas SWIG y g++ instalados:
echo 1. Ejecuta: build_windows.bat
echo 2. O usa WSL: cd scr/cpp/swig && ./build_scripts.sh
