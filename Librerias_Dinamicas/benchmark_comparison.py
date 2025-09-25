#!/usr/bin/env python3
"""
Script de comparación de rendimiento entre la librería dinámica (C++/SWIG) 
y la implementación nativa en Python.

Este script compara el tiempo de ejecución de las funciones de Reconocimiento
y Evaluación entre ambas implementaciones.
"""

import time
import sys
import os
import random
from typing import List, Tuple

# Agregar el directorio actual al path para importar hmm_py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import hmm_py
    PYTHON_AVAILABLE = True
except ImportError:
    print("Error: No se pudo importar hmm_py")
    PYTHON_AVAILABLE = False

try:
    import hmm  # Librería dinámica compilada con SWIG
    SWIG_AVAILABLE = True
except ImportError:
    print("Advertencia: No se pudo importar la librería dinámica hmm")
    print("Asegúrate de haber compilado la librería con SWIG")
    SWIG_AVAILABLE = False

def random_dna(length: int) -> str:
    """Genera una secuencia de ADN aleatoria"""
    return ''.join(random.choice('ACGT') for _ in range(length))

def benchmark_function(func, args, iterations: int = 1000) -> Tuple[float, any]:
    """
    Ejecuta una función múltiples veces y mide el tiempo promedio
    
    Args:
        func: Función a ejecutar
        args: Argumentos para la función
        iterations: Número de iteraciones
    
    Returns:
        Tupla con (tiempo_promedio, resultado)
    """
    # Calentamiento
    for _ in range(10):
        func(*args)
    
    # Medición
    start_time = time.perf_counter()
    result = None
    for _ in range(iterations):
        result = func(*args)
    end_time = time.perf_counter()
    
    avg_time = (end_time - start_time) / iterations
    return avg_time, result

def run_benchmarks():
    """Ejecuta las comparaciones de rendimiento"""
    
    print("=" * 60)
    print("COMPARACIÓN DE RENDIMIENTO: LIBRERÍA DINÁMICA vs PYTHON NATIVO")
    print("=" * 60)
    
    # Secuencias de prueba
    test_sequences = [
        "ATCGGATCGCG",  # Secuencia del ejemplo
        random_dna(50),
        random_dna(100),
        random_dna(500),
        random_dna(1000)
    ]
    
    results = []
    
    for seq in test_sequences:
        print(f"\nSecuencia: {seq[:20]}{'...' if len(seq) > 20 else ''} (longitud: {len(seq)})")
        print("-" * 50)
        
        # Inicializar modelos
        if PYTHON_AVAILABLE:
            python_model = hmm_py.HMM()
        if SWIG_AVAILABLE:
            swig_model = hmm.HMM()
        
        # Benchmark Reconocimiento (Viterbi)
        print("Función: Reconocimiento (Viterbi)")
        if PYTHON_AVAILABLE:
            # Usar viterbi para obtener estados y convertir a string H/L
            def python_reconocimiento(seq):
                states = python_model.viterbi(seq)
                return ''.join('H' if s == 1 else 'L' for s in states)
            
            py_time, py_result = benchmark_function(python_reconocimiento, (seq,), 1000)
            print(f"  Python nativo: {py_time*1000:.4f} ms")
        else:
            py_time, py_result = None, None
            
        if SWIG_AVAILABLE:
            swig_time, swig_result = benchmark_function(swig_model.reconocimiento, (seq,), 1000)
            print(f"  Librería dinámica: {swig_time*1000:.4f} ms")
        else:
            swig_time, swig_result = None, None
            
        if py_time and swig_time:
            speedup = py_time / swig_time
            print(f"  Aceleración: {speedup:.2f}x")
        
        # Verificar que los resultados coincidan
        if py_result and swig_result:
            if py_result == swig_result:
                print("  ✓ Resultados coinciden")
            else:
                print(f"  ✗ Resultados difieren: Python='{py_result}', SWIG='{swig_result}'")
        
        # Benchmark Evaluación
        print("Función: Evaluación")
        if PYTHON_AVAILABLE:
            # Usar evaluacion que devuelve (prob, log2_score)
            def python_evaluacion(seq):
                prob, log2_score = python_model.evaluacion(seq)
                return prob  # Solo devolver la probabilidad para comparar
            
            py_time_eval, py_result_eval = benchmark_function(python_evaluacion, (seq,), 1000)
            print(f"  Python nativo: {py_time_eval*1000:.4f} ms")
        else:
            py_time_eval, py_result_eval = None, None
            
        if SWIG_AVAILABLE:
            swig_time_eval, swig_result_eval = benchmark_function(swig_model.evaluacion, (seq,), 1000)
            print(f"  Librería dinámica: {swig_time_eval*1000:.4f} ms")
        else:
            swig_time_eval, swig_result_eval = None, None
            
        if py_time_eval and swig_time_eval:
            speedup_eval = py_time_eval / swig_time_eval
            print(f"  Aceleración: {speedup_eval:.2f}x")
        
        # Verificar que los resultados coincidan (con tolerancia para números flotantes)
        if py_result_eval and swig_result_eval:
            if abs(py_result_eval - swig_result_eval) < 1e-10:
                print("  ✓ Resultados coinciden")
            else:
                print(f"  ✗ Resultados difieren: Python={py_result_eval:.2e}, SWIG={swig_result_eval:.2e}")
        
        # Guardar resultados para resumen
        results.append({
            'sequence_length': len(seq),
            'python_reconocimiento': py_time,
            'swig_reconocimiento': swig_time,
            'python_evaluacion': py_time_eval,
            'swig_evaluacion': swig_time_eval
        })
    
    # Resumen final
    print("\n" + "=" * 60)
    print("RESUMEN DE RENDIMIENTO")
    print("=" * 60)
    
    if results:
        # Calcular aceleración solo si hay datos de SWIG
        python_recon_data = [r['python_reconocimiento'] for r in results if r['python_reconocimiento']]
        swig_recon_data = [r['swig_reconocimiento'] for r in results if r['swig_reconocimiento']]
        python_eval_data = [r['python_evaluacion'] for r in results if r['python_evaluacion']]
        swig_eval_data = [r['swig_evaluacion'] for r in results if r['swig_evaluacion']]
        
        if python_recon_data and swig_recon_data:
            avg_speedup_recon = sum(python_recon_data[i]/swig_recon_data[i] 
                                   for i in range(len(python_recon_data))) / len(python_recon_data)
            print(f"Aceleración promedio - Reconocimiento: {avg_speedup_recon:.2f}x")
        else:
            print("Aceleración promedio - Reconocimiento: No disponible (SWIG no compilado)")
            
        if python_eval_data and swig_eval_data:
            avg_speedup_eval = sum(python_eval_data[i]/swig_eval_data[i] 
                                  for i in range(len(python_eval_data))) / len(python_eval_data)
            print(f"Aceleración promedio - Evaluación: {avg_speedup_eval:.2f}x")
        else:
            print("Aceleración promedio - Evaluación: No disponible (SWIG no compilado)")
        
        if python_recon_data and swig_recon_data and python_eval_data and swig_eval_data:
            avg_speedup_recon = sum(python_recon_data[i]/swig_recon_data[i] 
                                   for i in range(len(python_recon_data))) / len(python_recon_data)
            avg_speedup_eval = sum(python_eval_data[i]/swig_eval_data[i] 
                                  for i in range(len(python_eval_data))) / len(python_eval_data)
            print(f"Aceleración promedio general: {(avg_speedup_recon + avg_speedup_eval)/2:.2f}x")
        else:
            print("Aceleración promedio general: No disponible (SWIG no compilado)")
            
        print("\nNota: Para obtener comparación de rendimiento, compile la librería dinámica:")
        print("cd scr/cpp/swig/")
        print("./build_scripts.sh")

if __name__ == "__main__":
    run_benchmarks()
