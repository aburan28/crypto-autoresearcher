/* EXP-PFDR-2d36f9 pair-sum coincidence kernel.
 *
 * Derived from EXP-PFDR-ca5e01 paircount.c with two reviewed changes for the
 * 32-bit rung: the field bound is p < 2^32 (was p < 2^31) and the radix
 * key-width scan is capped at 64 bits, so the shift is never taken by 64 or
 * more. The key bound is x*p + y <= (p-1)*p + (p-1) = p^2 - 1 < 2^64 for
 * every accepted p; the counting convention is unchanged.
 *
 * For a symmetric point set F on E: y^2 = x^3 + a x + b over F_p (p < 2^32,
 * odd prime group order, so no 2-torsion), counts the NONTRIVIAL pair-sum
 * coincidences
 *
 *     C(F) = sum over s != O of binom(m_s, 2),
 *     m_s  = #{ unordered {P,Q} subset F : P != Q, P + Q = s }.
 *
 * Pairs with P + Q = O (Q = -P) are excluded: they all collide at O and are
 * the trivial negation coincidences. Pairs {P,P} are excluded by P != Q.
 *
 * Input (stdin, whitespace separated): p a, then any number of bases, each
 *     b x_1 y_1 ... x_b y_b
 * Output (stdout): one line per base: "<b> <pairs> <coincidences>".
 * The points are trusted to lie on the curve; run.py's selftest checks this
 * kernel against a brute-force Python count on small curves.
 *
 * Sums are computed in affine coordinates with one batched inversion per row
 * (Montgomery's trick), keyed as x*p + y in 64 bits, LSD-radix sorted, and
 * the runs counted. Memory: 16 bytes per pair (keys plus radix buffer).
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef unsigned __int128 u128;
static uint64_t P, A;

static inline uint64_t mulm(uint64_t x, uint64_t y) { return (uint64_t)(((u128)x * y) % P); }
static inline uint64_t subm(uint64_t x, uint64_t y) { return x >= y ? x - y : x + P - y; }
static uint64_t powm(uint64_t x, uint64_t e) {
    uint64_t r = 1;
    while (e) { if (e & 1) r = mulm(r, x); x = mulm(x, x); e >>= 1; }
    return r;
}
static inline uint64_t invm(uint64_t x) { return powm(x, P - 2); }

static void radix_sort(uint64_t *a, uint64_t *tmp, size_t n, int bits) {
    size_t cnt[1 << 16];
    for (int shift = 0; shift < bits; shift += 16) {
        memset(cnt, 0, sizeof cnt);
        for (size_t i = 0; i < n; i++) cnt[(a[i] >> shift) & 0xFFFF]++;
        size_t s = 0;
        for (int k = 0; k < (1 << 16); k++) { size_t c = cnt[k]; cnt[k] = s; s += c; }
        for (size_t i = 0; i < n; i++) tmp[cnt[(a[i] >> shift) & 0xFFFF]++] = a[i];
        memcpy(a, tmp, n * sizeof *a);
    }
}

int main(void) {
    unsigned long long pp, aa;
    if (scanf("%llu %llu", &pp, &aa) != 2) { fprintf(stderr, "bad header\n"); return 2; }
    P = pp; A = aa % P;
    if (P < 5 || P >= (1ULL << 32)) { fprintf(stderr, "p out of range\n"); return 2; }
    uint64_t key_bound = (P - 1) * P + (P - 1);
    int keybits = 64;
    for (int k = 0; k < 64; k++) {
        if (((uint64_t)1 << k) > key_bound) { keybits = k; break; }
    }
    keybits = (keybits + 15) / 16 * 16;
    long b;
    while (scanf("%ld", &b) == 1) {
        if (b < 2 || b > (1L << 15)) { fprintf(stderr, "b out of range\n"); return 2; }
        uint64_t *x = malloc(b * sizeof *x), *y = malloc(b * sizeof *y);
        for (long i = 0; i < b; i++) {
            unsigned long long xi, yi;
            if (scanf("%llu %llu", &xi, &yi) != 2) { fprintf(stderr, "short base\n"); return 2; }
            x[i] = xi % P; y[i] = yi % P;
        }
        size_t maxpairs = (size_t)b * (b - 1) / 2;
        uint64_t *keys = malloc(maxpairs * sizeof *keys);
        uint64_t *pref = malloc(b * sizeof *pref), *den = malloc(b * sizeof *den);
        long *idx = malloc(b * sizeof *idx);
        if (!keys || !pref || !den || !idx) { fprintf(stderr, "oom\n"); return 3; }
        size_t n = 0;
        for (long i = 0; i < b; i++) {
            /* Denominators x_j - x_i for j > i. Distinct points with x_j == x_i have
             * y_j == -y_i: that is the excluded Q = -P case, and it is skipped. */
            long m = 0;
            uint64_t acc = 1;
            for (long j = i + 1; j < b; j++) {
                uint64_t d = subm(x[j], x[i]);
                if (d == 0) continue;
                acc = mulm(acc, d);
                idx[m] = j; den[m] = d; pref[m] = acc;
                m++;
            }
            if (m == 0) continue;
            uint64_t inv = invm(acc);
            for (long k = m - 1; k >= 0; k--) {
                long j = idx[k];
                uint64_t dinv = k > 0 ? mulm(inv, pref[k - 1]) : inv;
                inv = mulm(inv, den[k]);
                uint64_t lam = mulm(subm(y[j], y[i]), dinv);
                uint64_t x3 = subm(subm(mulm(lam, lam), x[i]), x[j]);
                uint64_t y3 = subm(mulm(lam, subm(x[i], x3)), y[i]);
                keys[n++] = x3 * P + y3;
            }
        }
        uint64_t *tmp = malloc((n ? n : 1) * sizeof *tmp);
        if (!tmp) { fprintf(stderr, "oom\n"); return 3; }
        radix_sort(keys, tmp, n, keybits);
        unsigned long long coinc = 0;
        for (size_t i = 0; i < n;) {
            size_t j = i + 1;
            while (j < n && keys[j] == keys[i]) j++;
            unsigned long long run = j - i;
            coinc += run * (run - 1) / 2;
            i = j;
        }
        printf("%ld %zu %llu\n", b, n, coinc);
        fflush(stdout);
        free(x); free(y); free(keys); free(pref); free(den); free(idx); free(tmp);
    }
    return 0;
}
