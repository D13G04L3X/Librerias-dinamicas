// hmm.h
#ifndef HMM_H
#define HMM_H

#include <string>
#include <vector>

class HMM {
public:
    // states: 0 = N, 1 = C
    HMM();
    HMM(const std::vector<std::vector<double>>& A,
        const std::vector<double>& pi,
        const std::vector<std::vector<double>>& B);

    // devuelve log prob (natural log) de la secuencia
    double evaluate(const std::string &seq);

    // posterior decode -> vector<int> 0/1
    std::vector<int> posterior_decode(const std::string &seq, double threshold);

    // helper: random generator no incluido aquí
private:
    std::vector<std::vector<double>> A;
    std::vector<double> pi;
    std::vector<std::vector<double>> B;
    int sym2idx(char c);
};

#endif
