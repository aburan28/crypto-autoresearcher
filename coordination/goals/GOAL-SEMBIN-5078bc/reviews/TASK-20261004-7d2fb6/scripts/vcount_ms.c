// vcount_ms.c -- reviewer's own exact zero counter for the m = t = 2 Boolean systems, working directly on the descended
// Boolean polynomials (as parsed from the .ms file), NOT on field arithmetic. Independent of count_m2.c / count_chain.c.
// Input (text): N neq ; then per equation: cnt mask1 ... maskcnt   (bit i <-> variable i; variables 0..k-1 = x1, k..2k-1 = x2)
// Every monomial must be constant, a single variable, or a pair (x1_i, x2_j); otherwise the program stops (structure check).
// For fixed x1 the system is affine in x2: columns M[j] (bit l = coefficient of x2_j in equation l), rhs.
// Gray-code walk over x1. Output: count, number of x1 with a consistent inner system, and every zero (N-bit assignment)
// whose fibre is a single point; fibres with several points are only counted (their number is printed).
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
typedef uint64_t u64;
int main(int argc, char **argv) {
    FILE *f = fopen(argv[1], "r"); int N, neq; if (fscanf(f, "%d %d", &N, &neq) != 2) return 2;
    int k = N / 2; if (2 * k != N || neq > 64) { fprintf(stderr, "shape\n"); return 2; }
    u64 c0 = 0, a0[64] = {0}, b[64] = {0};              // rhs consts (bit per eq), a: per x1 var: bit per eq; b: per x2 var: bit per eq
    static u64 A[64][64]; memset(A, 0, sizeof A);        // A[i][j]: bit per eq, coefficient of x1_i x2_j
    for (int l = 0; l < neq; l++) {
        int cnt; if (fscanf(f, "%d", &cnt) != 1) return 2;
        for (int q = 0; q < cnt; q++) {
            unsigned long long m; if (fscanf(f, "%llu", &m) != 1) return 2;
            int pc = __builtin_popcountll(m);
            if (pc == 0) c0 ^= 1ULL << l;
            else if (pc == 1) { int v = __builtin_ctzll(m); if (v < k) a0[v] ^= 1ULL << l; else b[v - k] ^= 1ULL << l; }
            else if (pc == 2) {
                int v1 = __builtin_ctzll(m), v2 = 63 - __builtin_clzll(m);
                if (v1 < k && v2 >= k) A[v1][v2 - k] ^= 1ULL << l; else { fprintf(stderr, "monomial not of type x1*x2\n"); return 3; }
            } else { fprintf(stderr, "degree > 2\n"); return 3; }
        }
    }
    u64 col[64], rhs = c0;
    for (int j = 0; j < k; j++) col[j] = b[j];
    long long total = 0, consistent = 0, multi = 0;
    u64 lim = 1ULL << k;
    for (u64 g = 0; g < lim; g++) {
        if (g) { int i = __builtin_ctzll(g); for (int j = 0; j < k; j++) col[j] ^= A[i][j]; rhs ^= a0[i]; }
        u64 gray = g ^ (g >> 1);
        u64 bas[64], tag[64]; memset(bas, 0, sizeof bas); memset(tag, 0, sizeof tag);
        int rank = 0;
        for (int j = 0; j < k; j++) {
            u64 v = col[j], tg = 1ULL << j;
            while (v) { int r = __builtin_ctzll(v); if (!bas[r]) { bas[r] = v; tag[r] = tg; rank++; break; } v ^= bas[r]; tg ^= tag[r]; }
        }
        u64 v = rhs, tg = 0;
        while (v) { int r = __builtin_ctzll(v); if (!bas[r]) break; v ^= bas[r]; tg ^= tag[r]; }
        if (v == 0) {
            long long inner = 1LL << (k - rank);
            total += inner; consistent++;
            if (rank == k) printf("ZERO %llu\n", (unsigned long long)(gray | (tg << k)));   // x1 = gray (bit i of gray = x1_i); x2 = tg
            else multi++;
        }
    }
    printf("COUNT %lld consistent_x1 %lld multi_point_fibres %lld N %d k %d\n", total, consistent, multi, N, k);
    return 0;
}
