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
        # default: ejemplo plausible (ajusta según la figura del enunciado)
        if A is None:
            A = [[0.99, 0.01],
                 [0.01, 0.99]]
        if pi is None:
            pi = [0.5, 0.5]
        if B is None:
            # ejemplo: non-coding (uniforme), coding (biased)
            B = [
                [0.25,0.25,0.25,0.25],   # N
                [0.15,0.35,0.35,0.15]    # C (ejemplo: más G/C)
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

    def posterior_decode(self, seq: str, threshold: float = 0.5) -> List[int]:
        """
        Calcula la prob posterior por posición de estar en estado 'coding' (1)
        y devuelve lista 0/1 según threshold.
        """
        n = len(seq)
        if n == 0:
            return []
        alpha, scales = self._forward_scaled(seq)
        beta = self._backward_scaled(seq, scales)

        posterior = []
        # normalization per position: gamma_i(t) proportional to alpha[t][i] * beta[t][i]
        for t in range(n):
            g0 = alpha[t][0] * beta[t][0]
            g1 = alpha[t][1] * beta[t][1]
            s = g0 + g1
            if s == 0:
                p1 = 0.0
            else:
                p1 = g1 / s
            posterior.append(1 if p1 >= threshold else 0)
        return posterior

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

# pequeño helper para generar secuencias aleatorias (útil en benchmarks)
import random
def random_dna(length):
    return ''.join(random.choice('ACGT') for _ in range(length))

if __name__ == "__main__":
    # demo de uso
    model = HMM()
    s = "ACGTGCGTACGTTAGC"
    print("Log-prob (evaluate):", model.evaluate(s))
    post = model.posterior_decode(s, threshold=0.6)
    print("Posterior (1=coding):", post)
    print("Segments:", model.segments_from_posterior(post))
