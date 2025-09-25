# hmm_py_adjusted.py
import math
from typing import List, Tuple
import random

class HMM:
    """
    HMM 2 estados: 0 = L (low), 1 = H (high).
    Parámetros por defecto: iguales a la Figura 2 (A, pi, B).
    """

    def __init__(self,
                 A = None,
                 pi = None,
                 B = None):
        if A is None:
            A = [[0.6, 0.4],
                 [0.5, 0.5]]
        if pi is None:
            pi = [0.5, 0.5]
        if B is None:
            B = [
                [0.3,0.2,0.2,0.3],   # L: A,C,G,T
                [0.2,0.3,0.3,0.2]    # H: A,C,G,T
            ]
        self.A = A
        self.pi = pi
        self.B = B
        self.sym2idx = {'A':0,'C':1,'G':2,'T':3}

    def _emit_prob(self, state: int, symbol: str) -> float:
        return self.B[state][self.sym2idx[symbol]]

    # -------- VITERBI + SCORE (log2) --------
    def viterbi_with_score(self, seq: str) -> Tuple[List[int], float]:
        """
        Devuelve (estados_más_probables, log2_probabilidad_del_camino)
        """
        n = len(seq)
        if n == 0:
            return [], float('-inf')

        v = [[float('-inf'), float('-inf')] for _ in range(n)]
        path = [[0, 0] for _ in range(n)]

        # inicialización (log2)
        for i in range(2):
            v[0][i] = math.log2(self.pi[i]) + math.log2(self._emit_prob(i, seq[0]))

        # recursión
        for t in range(1, n):
            for j in range(2):
                emit_log = math.log2(self._emit_prob(j, seq[t]))
                best_val = float('-inf')
                best_state = 0
                for i in range(2):
                    val = v[t-1][i] + math.log2(self.A[i][j]) + emit_log
                    if val > best_val:
                        best_val = val
                        best_state = i
                v[t][j] = best_val
                path[t][j] = best_state

        # terminación y backtracking
        best_final_state = 0 if v[n-1][0] > v[n-1][1] else 1
        best_score = v[n-1][best_final_state]
        states = [0] * n
        states[n-1] = best_final_state
        for t in range(n-2, -1, -1):
            states[t] = path[t+1][states[t+1]]

        return states, best_score

    def viterbi(self, seq: str) -> List[int]:
        s,_ = self.viterbi_with_score(seq)
        return s

    def viterbi_log2(self, seq: str) -> float:
        _, score = self.viterbi_with_score(seq)
        return score

    # -------- FORWARD (para prob total) en log2 (no cambia) --------
    def evaluate_log2(self, seq: str) -> float:
        """
        Forward con escalado, devuelve log2(P(seq | modelo)) (prob total).
        """
        n = len(seq)
        if n == 0:
            return float('-inf')
        scales = []
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
        log2p = sum(math.log2(s) for s in scales)
        return log2p

    # -------- EVALUACION: por defecto devuelve la probabilidad del camino Viterbi (imagen) --------
    def evaluacion(self, seq: str) -> Tuple[float, float]:
        """
        Devuelve (probabilidad_del_mejor_camino, log2_del_mejor_camino)
        (Esto reproduce exactamente lo que muestra la imagen: 2^{log2_score_of_viterbi})
        Si quieres la prob total usa evaluate_log2().
        """
        log2score = self.viterbi_log2(seq)
        prob = 2 ** log2score
        return prob, log2score

    def segments_from_states(self, states: List[int]) -> List[Tuple[int,int]]:
        segs = []
        n = len(states)
        i = 0
        while i < n:
            if states[i] == 1:
                start = i
                while i+1 < n and states[i+1] == 1:
                    i += 1
                end = i
                segs.append((start, end))
            i += 1
        return segs

# small helper
def random_dna(length):
    return ''.join(random.choice('ACGT') for _ in range(length))

# demo (si se ejecuta como script)
if __name__ == "__main__":
    model = HMM()

    # ejemplo de la imagen
    seq = "GGCACTGAA"
    states, log2score = model.viterbi_with_score(seq)
    prob_vit = 2 ** log2score
    print("Sequence:", seq)
    print("Viterbi path (H/L):", ''.join('H' if s==1 else 'L' for s in states))
    print("Viterbi log2 score:", f"{log2score:.2f}")
    print("Viterbi probability:", f"{prob_vit:.2e}")
    print()
