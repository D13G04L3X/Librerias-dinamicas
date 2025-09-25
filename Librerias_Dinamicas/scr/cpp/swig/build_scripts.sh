#!/bin/bash

# Script de construcción para la librería dinámica HMM con SWIG
# Este script compila la librería C++ y genera los bindings de Python

echo "=== Construyendo librería dinámica HMM ==="

# Verificar que estamos en el directorio correcto
if [ ! -f "hmm.i" ]; then
    echo "Error: No se encontró hmm.i. Ejecuta este script desde el directorio swig/"
    exit 1
fi

# 1. Limpiar archivos anteriores
echo "Limpiando archivos anteriores..."
rm -f hmm_wrap.cxx hmm_wrap.o hmm.o _hmm.so

# 2. Generar wrapper con SWIG
echo "Generando wrapper con SWIG..."
swig -c++ -python hmm.i
if [ $? -ne 0 ]; then
    echo "Error: Falló la generación del wrapper SWIG"
    exit 1
fi

# 3. Compilar código C++
echo "Compilando código C++..."
g++ -O3 -fPIC -c ../cpp_scr/hmm.cxx -o hmm.o
if [ $? -ne 0 ]; then
    echo "Error: Falló la compilación del código C++"
    exit 1
fi

# 4. Compilar wrapper
echo "Compilando wrapper..."
g++ -O3 -fPIC -c hmm_wrap.cxx -I/usr/include/python3.10 -I../cpp_scr
if [ $? -ne 0 ]; then
    echo "Error: Falló la compilación del wrapper"
    exit 1
fi

# 5. Enlazar librería dinámica
echo "Enlazando librería dinámica..."
g++ -shared hmm.o hmm_wrap.o -o _hmm.so
if [ $? -ne 0 ]; then
    echo "Error: Falló el enlace de la librería dinámica"
    exit 1
fi

echo "=== Construcción completada exitosamente ==="
echo "Librería generada: _hmm.so"
echo "Para usar en Python: import hmm"
