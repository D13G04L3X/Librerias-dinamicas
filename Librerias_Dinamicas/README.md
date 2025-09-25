# Librería Dinámica HMM para Análisis de Secuencias de ADN

Este proyecto implementa una librería dinámica usando SWIG para análisis de secuencias de ADN con Modelos Ocultos de Markov (HMM).

## Descripción del Proyecto

El proyecto incluye dos funciones principales:

1. **Reconocimiento**: Identifica regiones con alta y baja probabilidad de ser regiones codificantes
2. **Evaluación**: Calcula la probabilidad de que una secuencia se haya generado desde el modelo HMM

## Estructura del Proyecto

```
Librerias_Dinamicas/
├── README.md                          # Documentación principal
├── hmm_py.py                         # Implementación Python nativa
├── benchmark_comparison.py           # Script de comparación de rendimiento
├── setup_github.sh                   # Script de configuración GitHub
├── .gitignore                        # Archivos a ignorar
├── INSTRUCCIONES_ENTREGA.md          # Guía de entrega
├── Ejemplo_de_swig.ipynb             # Ejemplo de uso de SWIG
├── examples/
│   └── Instructions.txt              # Instrucciones del proyecto
└── scr/
    └── cpp/
        ├── cpp_scr/
        │   ├── hmm.h                 # Cabecera C++
        │   ├── hmm.cxx               # Implementación C++
        │   └── CMakeLists.txt        # Configuración CMake
        └── swig/
            ├── hmm.i                 # Archivo de interfaz SWIG
            └── build_scripts.sh      # Script de construcción
```

## Modelo HMM

El modelo implementado sigue las especificaciones de la Figura 2:

- **Estados**: L (Low) y H (High)
- **Transiciones**: 
  - L→L: 0.6, L→H: 0.4
  - H→H: 0.5, H→L: 0.5
- **Probabilidades iniciales**: Start→L: 0.5, Start→H: 0.5
- **Emisiones**:
  - Estado L: A=0.3, C=0.2, G=0.2, T=0.3
  - Estado H: A=0.2, C=0.3, G=0.3, T=0.2

## Instalación y Construcción

### Para Windows

#### Prerrequisitos
- Python 3.x instalado (descargar de https://python.org)
- Git instalado (descargar de https://git-scm.com)

#### Ejecución Rápida
```cmd
# 1. Probar la implementación Python
python hmm_py.py

# 2. Ejecutar comparación de rendimiento
python benchmark_comparison.py

# 3. Configurar repositorio Git
setup_windows.bat
```

#### Resultados Esperados
```
=== Demostración de las funciones requeridas ===
Secuencia: ATCGGATCGCG
Reconocimiento: LLHHHLLLHHH
Evaluación: 2.21e-07
```

### Para Linux/Ubuntu/WSL

#### Prerrequisitos
```bash
# Instalar dependencias
sudo apt-get update
sudo apt-get install -y swig build-essential python3-dev
```

#### Construcción de la Librería Dinámica
```bash
# Navegar al directorio swig
cd scr/cpp/swig/

# Hacer ejecutable el script
chmod +x build_scripts.sh

# Ejecutar construcción
./build_scripts.sh
```

### Verificación de la Construcción

```bash
# Probar la librería dinámica
cd scr/cpp/swig/
python3 -c "import hmm; print('Librería dinámica cargada exitosamente')"
```

## Uso

### Para Windows (Recomendado)

#### Ejecución Directa
```cmd
# Ejecutar el programa principal
python hmm_py.py
```

#### Uso Programático
```python
from hmm_py import HMM

# Crear modelo
model = HMM()

# Secuencia de ejemplo
seq = "ATCGGATCGCG"

# Función de Reconocimiento
resultado_reconocimiento = model.reconocimiento(seq)
print(f"Reconocimiento: {resultado_reconocimiento}")

# Función de Evaluación
probabilidad = model.evaluacion(seq)
print(f"Evaluación: {probabilidad:.2e}")
```

### Para Linux/Ubuntu/WSL

#### Implementación Python Nativa
```python
from hmm_py import HMM

# Crear modelo
model = HMM()

# Secuencia de ejemplo
seq = "ATCGGATCGCG"

# Función de Reconocimiento
resultado_reconocimiento = model.reconocimiento(seq)
print(f"Reconocimiento: {resultado_reconocimiento}")

# Función de Evaluación
probabilidad = model.evaluacion(seq)
print(f"Evaluación: {probabilidad:.2e}")
```

#### Librería Dinámica (SWIG)
```python
import hmm

# Crear modelo
model = hmm.HMM()

# Secuencia de ejemplo
seq = "ATCGGATCGCG"

# Función de Reconocimiento
resultado_reconocimiento = model.reconocimiento(seq)
print(f"Reconocimiento: {resultado_reconocimiento}")

# Función de Evaluación
probabilidad = model.evaluacion(seq)
print(f"Evaluación: {probabilidad:.2e}")
```

## Comparación de Rendimiento

### Para Windows
```cmd
python benchmark_comparison.py
```

### Para Linux/Ubuntu/WSL
```bash
python3 benchmark_comparison.py
```

Este script:
- Compara el tiempo de ejecución de ambas implementaciones
- Verifica que los resultados coincidan
- Calcula la aceleración obtenida con la librería dinámica

## Ejemplo de Salida

```
=== Demostración de las funciones requeridas ===
Secuencia: ATCGGATCGCG
Reconocimiento: LLHHHLLHHHH
Evaluación: 2.21e-07

=== Información adicional ===
Log-probabilidad: -15.327346
Estados posteriores: [0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 1]
Segmentos H: [(2, 4), (7, 10)]
```

**Nota**: El algoritmo funciona con cualquier secuencia de ADN, no solo con la del ejemplo. Las funciones `reconocimiento()` y `evaluacion()` procesan automáticamente cualquier secuencia válida.

## Características Técnicas

- **Algoritmo de Viterbi**: Implementado con log2 para evitar problemas de precisión numérica
- **Algoritmo Forward-Backward**: Implementado con escalado para evitar underflow
- **Optimización**: Código C++ optimizado con -O3
- **Compatibilidad**: Funciona con Python 3.x
- **Rendimiento**: La librería dinámica es significativamente más rápida que la implementación Python nativa

## Requisitos del Sistema

### Para Windows
- Windows 10/11
- Python 3.x (descargar de https://python.org)
- Git (descargar de https://git-scm.com)

### Para Linux/Ubuntu/WSL
- Linux/Ubuntu (recomendado)
- Python 3.x
- SWIG 4.0+
- GCC/G++ con soporte C++11
- Bibliotecas de desarrollo de Python

## Solución de Problemas

### Error de Importación de la Librería Dinámica

```bash
# Verificar que _hmm.so existe
ls -la scr/cpp/swig/_hmm.so

# Reconstruir si es necesario
cd scr/cpp/swig/
./build_scripts.sh
```

### Error de Compilación

```bash
# Verificar versiones
python3 --version
swig -version
g++ --version

# Instalar dependencias faltantes
sudo apt-get install python3-dev build-essential
```

## Contribuciones

Este proyecto fue desarrollado como parte de un trabajo académico sobre librerías dinámicas y análisis de secuencias de ADN.

## Licencia

Este proyecto es de uso académico y educativo.
