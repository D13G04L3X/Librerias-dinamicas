@echo off
echo === Construyendo librería dinámica HMM para Windows ===

REM Verificar que estamos en el directorio correcto
if not exist "scr\cpp\swig\hmm.i" (
    echo Error: No se encontró hmm.i. Ejecuta este script desde el directorio raíz del proyecto
    exit /b 1
)

REM Cambiar al directorio swig
cd scr\cpp\swig

REM 1. Limpiar archivos anteriores
echo Limpiando archivos anteriores...
del /f /q hmm_wrap.cxx hmm_wrap.o hmm.o _hmm.pyd hmm.py 2>nul

REM 2. Generar wrapper con SWIG
echo Generando wrapper con SWIG...
swig -c++ -python hmm.i
if %errorlevel% neq 0 (
    echo Error: Falló la generación del wrapper SWIG
    echo Asegúrate de tener SWIG instalado
    exit /b 1
)

REM 3. Compilar código C++
echo Compilando código C++...
g++ -O3 -fPIC -c ..\cpp_scr\hmm.cxx -o hmm.o
if %errorlevel% neq 0 (
    echo Error: Falló la compilación del código C++
    echo Asegúrate de tener g++ instalado (MinGW o similar)
    exit /b 1
)

REM 4. Compilar wrapper
echo Compilando wrapper...
g++ -O3 -fPIC -c hmm_wrap.cxx -I..\cpp_scr -I%PYTHON_HOME%\include
if %errorlevel% neq 0 (
    echo Error: Falló la compilación del wrapper
    echo Asegúrate de tener Python instalado y PYTHON_HOME configurado
    exit /b 1
)

REM 5. Enlazar librería dinámica
echo Enlazando librería dinámica...
g++ -shared hmm.o hmm_wrap.o -o _hmm.pyd
if %errorlevel% neq 0 (
    echo Error: Falló el enlace de la librería dinámica
    exit /b 1
)

echo === Construcción completada exitosamente ===
echo Librería generada: _hmm.pyd
echo Para usar en Python: import hmm

REM Copiar archivos al directorio raíz para facilitar el uso
copy _hmm.pyd ..\..\..\ 2>nul
copy hmm.py ..\..\..\ 2>nul

echo Archivos copiados al directorio raíz del proyecto
