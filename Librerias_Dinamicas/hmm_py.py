# hmm_py.py
import math
from typing import List, Tuple

class HMM:
    """
    HMM simple de 2 estados: 0 = non-coding (N), 1 = coding (C)
    Emisiones: nucleótidos 'A','C','G','T'
    Se representan probabilidades en float. Los métodos trabajan en log-espacio
    cuando es necesario y usan escalado para forward/backward.
    """

    def __init__(self,
                 A = None,           # matriz de transición 2x2: A[i][j] = P(s_j | s_i)
                 pi = None,          # vector inicial 2: P(s_i at t=0)
                 B = None):          # emisiones: B[state][symbol_index]
        # Según Figura 2: estados L (0) y H (1)
        if A is None:
            # Transiciones: L->L=0.6, L->H=0.4, H->H=0.5, H->L=0.5
            A = [[0.6, 0.4],
                 [0.5, 0.5]]
        if pi is None:
            # Probabilidades iniciales: Start->L=0.5, Start->H=0.5
            pi = [0.5, 0.5]
        if B is None:
            # Emisiones según Figura 2:
            # L: A=0.3, C=0.2, G=0.2, T=0.3
            # H: A=0.2, C=0.3, G=0.3, T=0.2
            B = [
                [0.3,0.2,0.2,0.3],   # L
                [0.2,0.3,0.3,0.2]    # H
            ]
        self.A = A
        self.pi = pi
        self.B = B
        self.sym2idx = {'A':0,'C':1,'G':2,'T':3}

    def _emit_prob(self, state: int, symbol: str) -> float:
        return self.B[state][self.sym2idx[symbol]]

    def evaluate(self, seq: str) -> float:
        """
        Forward algorithm con escalado. Devuelve log(P(seq | modelo)).
        """
        n = len(seq)
        if n == 0:
            return float('-inf')

        # alpha_scaled[t][i] but guardamos sólo el vector actual
        # scaling factors
        scales = []
        # t=0
        a0 = [self.pi[i] * self._emit_prob(i, seq[0]) for i in (0,1)]
        s0 = sum(a0)
        if s0 == 0:
            return float('-inf')
        a0 = [x / s0 for x in a0]
        scales.append(s0)
        prev = a0

        for t in range(1,n):
            obs = seq[t]
            cur = [0.0,0.0]
            for j in (0,1):
                s = 0.0
                for i in (0,1):
                    s += prev[i] * self.A[i][j]
                cur[j] = s * self._emit_prob(j, obs)
            st = sum(cur)
            if st == 0:
                return float('-inf')
            cur = [x / st for x in cur]
            scales.append(st)
            prev = cur

        # log P(seq) = sum(log(scales[t])) because alpha_scaled multiplied by scales gives original
        logp = sum(math.log(s) for s in scales)
        return logp

    def _forward_scaled(self, seq: str):
        n = len(seq)
        if n == 0:
            return [], []
        alpha = []
        scales = []
        # t=0
        a = [self.pi[i] * self._emit_prob(i, seq[0]) for i in (0,1)]
        s = sum(a)
        a = [x / s for x in a]
        alpha.append(a)
        scales.append(s)
        for t in range(1,n):
            obs = seq[t]
            a = [0.0,0.0]
            for j in (0,1):
                ssum = 0.0
                for i in (0,1):
                    ssum += alpha[-1][i] * self.A[i][j]
                a[j] = ssum * self._emit_prob(j, obs)
            st = sum(a)
            a = [x / st for x in a]
            alpha.append(a)
            scales.append(st)
        return alpha, scales

    def _backward_scaled(self, seq: str, scales: List[float]):
        n = len(seq)
        if n == 0:
            return []
        beta = [ [0.0,0.0] for _ in range(n) ]
        # initialize last with ones scaled
        beta[-1] = [1.0, 1.0]  # because alpha were scaled
        for t in range(n-2, -1, -1):
            obs = seq[t+1]
            b = [0.0,0.0]
            for i in (0,1):
                ssum = 0.0
                for j in (0,1):
                    ssum += self.A[i][j] * self._emit_prob(j, obs) * beta[t+1][j]
                b[i] = ssum / scales[t+1]  # adjust because forward scaled by scales[t+1]
            beta[t] = b
        return beta

    def viterbi(self, seq: str) -> List[int]:
        """
        Algoritmo de Viterbi: encuentra la secuencia de estados más probable
        Usa log2 para evitar problemas de precisión numérica
        Devuelve lista de estados 0/1 (L/H)
        """
        n = len(seq)
        if n == 0:
            return []
        
        # Inicialización con log2
        v = [[float('-inf'), float('-inf')] for _ in range(n)]
        path = [[0, 0] for _ in range(n)]
        
        # t = 0
        for i in range(2):
            v[0][i] = math.log2(self.pi[i]) + math.log2(self._emit_prob(i, seq[0]))
        
        # Recursión
        for t in range(1, n):
            for j in range(2):
                max_log_prob = float('-inf')
                best_state = 0
                for i in range(2):
                    log_prob = v[t-1][i] + math.log2(self.A[i][j]) + math.log2(self._emit_prob(j, seq[t]))
                    if log_prob > max_log_prob:
                        max_log_prob = log_prob
                        best_state = i
                v[t][j] = max_log_prob
                path[t][j] = best_state
        
        # Terminación
        best_final_state = 0 if v[n-1][0] > v[n-1][1] else 1
        
        # Backtracking
        states = [0] * n
        states[n-1] = best_final_state
        for t in range(n-2, -1, -1):
            states[t] = path[t+1][states[t+1]]
        
        return states


    def segments_from_posterior(self, posterior: List[int]) -> List[Tuple[int,int]]:
        """
        Convierte lista 0/1 a segmentos (start, end) inclusive [start, end]
        """
        segs = []
        n = len(posterior)
        i = 0
        while i < n:
            if posterior[i] == 1:
                start = i
                while i+1 < n and posterior[i+1] == 1:
                    i += 1
                end = i
                segs.append((start, end))
            i += 1
        return segs

    def reconocimiento(self, seq: str) -> str:
        """
        Función de Reconocimiento: identifica regiones H/L
        Usa el algoritmo de Viterbi con log2 para encontrar la secuencia de estados más probable
        Devuelve string con 'H' para alta probabilidad y 'L' para baja probabilidad
        """
        viterbi_states = self.viterbi(seq)
        result = ""
        for state in viterbi_states:
            result += 'H' if state == 1 else 'L'
        return result

    def evaluacion(self, seq: str) -> float:
        """
        Función de Evaluación: calcula probabilidad de la secuencia
        Usa log2 para consistencia con Viterbi
        Devuelve la probabilidad (no log-probabilidad)
        """
        log2_prob = self.evaluate_log2(seq)
        return 2 ** log2_prob
    
    def evaluate_log2(self, seq: str) -> float:
        """
        Forward algorithm con escalado usando log2. Devuelve log2(P(seq | modelo)).
        """
        n = len(seq)
        if n == 0:
            return float('-inf')

        # alpha_scaled[t][i] but guardamos sólo el vector actual
        # scaling factors
        scales = []
        # t=0
        a0 = [self.pi[i] * self._emit_prob(i, seq[0]) for i in (0,1)]
        s0 = sum(a0)
        if s0 == 0:
            return float('-inf')
        a0 = [x / s0 for x in a0]
        scales.append(s0)
        prev = a0

        for t in range(1,n):
            obs = seq[t]
            cur = [0.0,0.0]
            for j in (0,1):
                s = 0.0
                for i in (0,1):
                    s += prev[i] * self.A[i][j]
                cur[j] = s * self._emit_prob(j, obs)
            st = sum(cur)
            if st == 0:
                return float('-inf')
            cur = [x / st for x in cur]
            scales.append(st)
            prev = cur

        # log2 P(seq) = sum(log2(scales[t]))
        log2p = sum(math.log2(s) for s in scales)
        return log2p

# pequeño helper para generar secuencias aleatorias (útil en benchmarks)
import random
def random_dna(length):
    return ''.join(random.choice('ACGT') for _ in range(length))

if __name__ == "__main__":
    print("=== Librería Dinámica HMM para Análisis de Secuencias de ADN ===")
    print()
    
    # Crear modelo
    model = HMM()
    
    # Permitir al usuario ingresar la secuencia
    print("Ingrese la secuencia de ADN que desea analizar:")
    print("(Solo use las letras A, C, G, T)")
    print("Ejemplo: ATCGGATCGCG")
    print()
    
    while True:
        try:
            secuencia = input("Secuencia: ").strip().upper()
            
            # Validar que solo contenga A, C, G, T
            if not secuencia:
                print("Error: La secuencia no puede estar vacía.")
                continue
                
            if not all(c in 'ACGT' for c in secuencia):
                print("Error: La secuencia solo puede contener las letras A, C, G, T.")
                print("Intente de nuevo:")
                continue
                
            break
            
        except KeyboardInterrupt:
            print("\n\nPrograma terminado por el usuario.")
            exit()
        except Exception as e:
            print(f"Error: {e}")
            continue
    
    print()
    print("=== Análisis de la Secuencia ===")
    print(f"Secuencia ingresada: {secuencia}")
    print(f"Longitud: {len(secuencia)} nucleótidos")
    print()
    
    # Función de Reconocimiento
    print("🔍 Función de Reconocimiento (Viterbi con log2):")
    reconocimiento_result = model.reconocimiento(secuencia)
    print(f"Regiones identificadas: {reconocimiento_result}")
    
    # Explicar el resultado
    h_count = reconocimiento_result.count('H')
    l_count = reconocimiento_result.count('L')
    print(f"  - Regiones de alta probabilidad (H): {h_count}")
    print(f"  - Regiones de baja probabilidad (L): {l_count}")
    
    # Función de Evaluación
    print()
    print("📊 Función de Evaluación:")
    evaluacion_result = model.evaluacion(secuencia)
    print(f"Probabilidad de la secuencia: {evaluacion_result:.2e}")
    print(f"Log2-probabilidad: {model.evaluate_log2(secuencia):.6f}")
    
    # Información adicional
    print()
    print("=== Información Adicional ===")
    viterbi_states = model.viterbi(secuencia)
    print(f"Estados Viterbi: {viterbi_states}")
    
    # Encontrar segmentos de alta probabilidad
    segmentos_h = model.segments_from_posterior(viterbi_states)
    if segmentos_h:
        print(f"Segmentos de alta probabilidad: {segmentos_h}")
        for start, end in segmentos_h:
            print(f"  - Posiciones {start}-{end}: {secuencia[start:end+1]}")
    else:
        print("No se encontraron segmentos de alta probabilidad.")
    
    print()
    print("=== Análisis Completado ===")
    print("¡Gracias por usar la librería dinámica HMM!")
