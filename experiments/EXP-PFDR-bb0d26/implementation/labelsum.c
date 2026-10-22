/* EXP-PFDR-bb0d26 label pair-sum kernel (toy curves only, p < 2^31).
 *
 * For a set X of n labels in [0, p) (the x-coordinates of curve points,
 * distinct, supplied by the caller) forms every unordered pair sum
 * (u + v) mod p, u != v, as an exact 64-bit key, LSD-radix sorts the
 * n(n-1)/2 keys and counts runs:
 *
 *     m_s = #{ {u, v} : u != v, u + v = s mod p },
 *     C   = sum_s binom(m_s, 2)        (pairs of distinct pairs with equal sum),
 *     D   = #{ s : m_s >= 1 }          (distinct pair sums).
 *
 * Pairs with u = v (3-term progressions 2u = v + w) are never formed. The
 * counts are exact for every set; nothing is sampled.
 *
 * Input (stdin, whitespace separated): p, then any number of sets, each
 *     n l_1 ... l_n
 * Output (stdout): one line per set: "<n> <pairs> <C> <D>".
 * Exit 2 on malformed or out-of-range input (p >= 2^31, n > 8192, a label
 * >= p), exit 3 on allocation failure. Memory: 16 bytes per pair (keys plus
 * the radix buffer); n = 4096 uses about 135 MB.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXN 8192L

static void radix_sort(uint64_t *a, uint64_t *tmp, size_t n, int bits) {
    static size_t cnt[1 << 16];
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
    unsigned long long pp;
    if (scanf("%llu", &pp) != 1) { fprintf(stderr, "bad header\n"); return 2; }
    uint64_t P = pp;
    if (P < 3 || P >= (1ULL << 31)) { fprintf(stderr, "p out of range\n"); return 2; }
    int keybits = 0;
    while ((1ULL << keybits) < P) keybits++;      /* keys are < P */
    keybits = (keybits + 15) / 16 * 16;
    if (keybits < 16) keybits = 16;
    long n;
    while (scanf("%ld", &n) == 1) {
        if (n < 0 || n > MAXN) { fprintf(stderr, "n out of range\n"); return 2; }
        uint64_t *x = malloc((n ? n : 1) * sizeof *x);
        if (!x) { fprintf(stderr, "oom\n"); return 3; }
        for (long i = 0; i < n; i++) {
            unsigned long long v;
            if (scanf("%llu", &v) != 1) { fprintf(stderr, "short set\n"); return 2; }
            if (v >= P) { fprintf(stderr, "label out of range\n"); return 2; }
            x[i] = v;
        }
        size_t pairs = (size_t)n * (size_t)(n > 0 ? n - 1 : 0) / 2;
        uint64_t *keys = malloc((pairs ? pairs : 1) * sizeof *keys);
        uint64_t *tmp = malloc((pairs ? pairs : 1) * sizeof *tmp);
        if (!keys || !tmp) { fprintf(stderr, "oom\n"); return 3; }
        size_t m = 0;
        for (long i = 0; i < n; i++)
            for (long j = i + 1; j < n; j++) {
                uint64_t s = x[i] + x[j];
                if (s >= P) s -= P;
                keys[m++] = s;
            }
        radix_sort(keys, tmp, m, keybits);
        unsigned long long coinc = 0, distinct = 0;
        for (size_t i = 0; i < m;) {
            size_t j = i + 1;
            while (j < m && keys[j] == keys[i]) j++;
            unsigned long long run = j - i;
            coinc += run * (run - 1) / 2;
            distinct++;
            i = j;
        }
        printf("%ld %zu %llu %llu\n", n, m, coinc, distinct);
        fflush(stdout);
        free(x); free(keys); free(tmp);
    }
    return 0;
}
