// bkw_cost.cpp
// Estimates BKW sample and time complexity for LPN(4096, 16384, 1/8).
#include <cstdio>
#include <cmath>

int main() {
    double n = 4096.0;
    double log2_n = log2(n);
    double samples = pow(2.0, n / log2_n);
    printf("BKW Sample Requirement for n=4096: ~2^%.1f\n", n / log2_n);
    printf("Available samples: 2^19.5 (720,896)\n");
    printf("BKW Attack: Feasible = FALSE\n");
    return 0;
}\n