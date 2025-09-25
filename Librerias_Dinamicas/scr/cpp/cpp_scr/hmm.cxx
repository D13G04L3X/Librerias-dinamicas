// hmm.cxx
#include "hmm.h"
#include <cmath>
#include <stdexcept>

HMM::HMM() {
    // Según Figura 2: estados L (0) y H (1)
    // Transiciones: L->L=0.6, L->H=0.4, H->H=0.5, H->L=0.5
    A = {{0.6,0.4},{0.5,0.5}};
    // Probabilidades iniciales: Start->L=0.5, Start->H=0.5
    pi = {0.5,0.5};
    // Emisiones según Figura 2:
    // L: A=0.3, C=0.2, G=0.2, T=0.3
    // H: A=0.2, C=0.3, G=0.3, T=0.2
    B = {
        {0.3,0.2,0.2,0.3},  // L
        {0.2,0.3,0.3,0.2}   // H
    };
}

HMM::HMM(const std::vector<std::vector<double>>& A_,
         const std::vector<double>& pi_,
         const std::vector<std::vector<double>>& B_) {
    A = A_;
    pi = pi_;
    B = B_;
}

int HMM::sym2idx(char c) {
    switch(c) {
        case 'A': return 0;
        case 'C': return 1;
        case 'G': return 2;
        case 'T': return 3;
        default: return 0;
    }
}

double HMM::evaluate(const std::string &seq) {
    int n = seq.size();
    if (n == 0) return -INFINITY;
    std::vector<std::array<double,2>> alpha;
    std::vector<double> scales;
    alpha.reserve(n);
    // t=0
    std::array<double,2> a0;
    for (int i=0;i<2;i++) {
        a0[i] = pi[i] * B[i][sym2idx(seq[0])];
    }
    double s0 = a0[0] + a0[1];
    if (s0 == 0.0) return -INFINITY;
    a0[0] /= s0; a0[1] /= s0;
    alpha.push_back(a0);
    scales.push_back(s0);

    for (int t=1; t<n; ++t) {
        std::array<double,2> cur = {0.0,0.0};
        int obs = sym2idx(seq[t]);
        for (int j=0;j<2;j++) {
            double sum = 0.0;
            for (int i=0;i<2;i++) sum += alpha[t-1][i] * A[i][j];
            cur[j] = sum * B[j][obs];
        }
        double st = cur[0] + cur[1];
        if (st == 0.0) return -INFINITY;
        cur[0] /= st; cur[1] /= st;
        alpha.push_back(cur);
        scales.push_back(st);
    }
    double logp = 0.0;
    for (double sc : scales) logp += std::log(sc);
    return logp;
}

std::vector<int> HMM::posterior_decode(const std::string &seq, double threshold) {
    int n = seq.size();
    std::vector<int> out;
    if (n == 0) return out;
    std::vector<std::array<double,2>> alpha(n), beta(n);
    std::vector<double> scales(n);
    // forward scaled
    {
        std::array<double,2> a0;
        for (int i=0;i<2;i++) a0[i] = pi[i] * B[i][sym2idx(seq[0])];
        double s0 = a0[0] + a0[1];
        a0[0]/=s0; a0[1]/=s0;
        alpha[0] = a0;
        scales[0] = s0;
        for (int t=1;t<n;++t) {
            std::array<double,2> cur = {0.0,0.0};
            int obs = sym2idx(seq[t]);
            for (int j=0;j<2;j++) {
                double sum = 0.0;
                for (int i=0;i<2;i++) sum += alpha[t-1][i] * A[i][j];
                cur[j] = sum * B[j][obs];
            }
            double st = cur[0] + cur[1];
            cur[0]/=st; cur[1]/=st;
            alpha[t] = cur;
            scales[t] = st;
        }
    }
    // backward scaled
    beta[n-1] = {1.0,1.0};
    for (int t=n-2;t>=0;--t) {
        std::array<double,2> cur = {0.0,0.0};
        int obs = sym2idx(seq[t+1]);
        for (int i=0;i<2;i++) {
            double sum = 0.0;
            for (int j=0;j<2;j++) {
                sum += A[i][j] * B[j][obs] * beta[t+1][j];
            }
            cur[i] = sum / scales[t+1];
        }
        beta[t] = cur;
    }
    out.resize(n);
    for (int t=0;t<n;++t) {
        double g0 = alpha[t][0] * beta[t][0];
        double g1 = alpha[t][1] * beta[t][1];
        double s = g0 + g1;
        double p1 = (s == 0.0) ? 0.0 : (g1 / s);
        out[t] = (p1 >= threshold) ? 1 : 0;
    }
    return out;
}

// Función de Reconocimiento: identifica regiones H/L
std::string HMM::reconocimiento(const std::string &seq) {
    std::vector<int> posterior = posterior_decode(seq, 0.5);
    std::string result;
    for (int state : posterior) {
        result += (state == 1) ? 'H' : 'L';
    }
    return result;
}

// Función de Evaluación: calcula probabilidad de la secuencia
double HMM::evaluacion(const std::string &seq) {
    return evaluate(seq);
}