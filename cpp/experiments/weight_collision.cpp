// weight_collision.cpp
// Evaluates collision probability in Fp weights.
#include <cstdio>
#include <cmath>

int main() {
    double N = 40238.0;
    double p = pow(2.0, 127.0) - 1.0;
    double p_coll = (N * N) / (2.0 * p);
    printf("N = %.0f, p = 2^127 - 1\n", N);
    printf("Collision probability: %.4e\n", p_coll);
    return 0;
}\n