/* Measured cost of ONE multiplication in F_2[z]/(z^131 + z^13 + z^2 + z + 1),
 * the ECC2K-130 field, on this machine.
 *
 * This exists only to put a MEASURED denominator under the conflicts -> field
 * operations conversion used in README.md.  It is a microbenchmark of field
 * arithmetic; it computes nothing about any curve, point or discrete log.
 *
 * Correctness is cross-checked against the pure-Python GF(2^131) used by
 * solve_cost_ladder.py: with --selftest it prints products of fixed vectors
 * which check_mul_bench.py re-derives independently.
 *
 *   gcc -O3 -mpclmul -msse4.1 -o gf2_131_mul_bench gf2_131_mul_bench.c
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <wmmintrin.h>
#include <smmintrin.h>

/* a, b: 3 limbs, bits 0..130.  r: 6 limbs. */
static inline void clmul192(const uint64_t *a, const uint64_t *b, uint64_t *r) {
    for (int i = 0; i < 6; i++) r[i] = 0;
    for (int i = 0; i < 3; i++)
        for (int j = 0; j < 3; j++) {
            __m128i t = _mm_clmulepi64_si128(_mm_set_epi64x(0, a[i]),
                                             _mm_set_epi64x(0, b[j]), 0x00);
            r[i + j]     ^= (uint64_t)_mm_cvtsi128_si64(t);
            r[i + j + 1] ^= (uint64_t)_mm_extract_epi64(t, 1);
        }
}

/* h <- r >> 131  (r has 6 limbs, h has 4 limbs; 131 = 2*64 + 3) */
static inline void shr131(const uint64_t *r, uint64_t *h) {
    for (int k = 0; k < 4; k++) {
        uint64_t lo = r[k + 2] >> 3;
        uint64_t hi = (k + 3 < 6) ? (r[k + 3] << 61) : 0;
        h[k] = lo | hi;
    }
}

/* acc ^= h * z^s   (h: 4 limbs, acc: 6 limbs) */
static inline void xor_shifted(uint64_t *acc, const uint64_t *h, int s) {
    int w = s >> 6, b = s & 63;
    for (int k = 0; k < 4; k++) {
        if (k + w < 6) acc[k + w] ^= (b ? (h[k] << b) : h[k]);
        if (b && k + w + 1 < 6) acc[k + w + 1] ^= h[k] >> (64 - b);
    }
}

static inline void reduce131(uint64_t *r, uint64_t *out) {
    uint64_t h[4];
    for (int pass = 0; pass < 3; pass++) {
        shr131(r, h);
        if (!(h[0] | h[1] | h[2] | h[3])) break;
        /* clear bits >= 131 */
        r[2] &= 0x7ULL;
        r[3] = r[4] = r[5] = 0;
        /* add h * (z^13 + z^2 + z + 1) */
        xor_shifted(r, h, 13);
        xor_shifted(r, h, 2);
        xor_shifted(r, h, 1);
        xor_shifted(r, h, 0);
    }
    out[0] = r[0]; out[1] = r[1]; out[2] = r[2] & 0x7ULL;
}

static inline void gfmul(const uint64_t *a, const uint64_t *b, uint64_t *out) {
    uint64_t r[6];
    clmul192(a, b, r);
    reduce131(r, out);
}

static uint64_t rng_state = 0x243F6A8885A308D3ULL;
static uint64_t xrand(void) {
    rng_state ^= rng_state << 13; rng_state ^= rng_state >> 7; rng_state ^= rng_state << 17;
    return rng_state;
}

int main(int argc, char **argv) {
    if (argc > 1 && !strcmp(argv[1], "--selftest")) {
        for (int t = 0; t < 8; t++) {
            uint64_t a[3], b[3], c[3];
            a[0] = xrand(); a[1] = xrand(); a[2] = xrand() & 0x7ULL;
            b[0] = xrand(); b[1] = xrand(); b[2] = xrand() & 0x7ULL;
            gfmul(a, b, c);
            printf("%016lx%016lx%016lx %016lx%016lx%016lx %016lx%016lx%016lx\n",
                   a[2], a[1], a[0], b[2], b[1], b[0], c[2], c[1], c[0]);
        }
        return 0;
    }
    long iters = (argc > 1) ? atol(argv[1]) : 50000000L;
    uint64_t a[3], b[3], c[3];
    a[0] = xrand(); a[1] = xrand(); a[2] = xrand() & 0x7ULL;
    b[0] = xrand(); b[1] = xrand(); b[2] = xrand() & 0x7ULL;
    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    for (long i = 0; i < iters; i++) {
        gfmul(a, b, c);
        a[0] ^= c[0]; a[1] ^= c[1]; a[2] = (a[2] ^ c[2]) & 0x7ULL;  /* serialise */
    }
    clock_gettime(CLOCK_MONOTONIC, &t1);
    double dt = (t1.tv_sec - t0.tv_sec) + 1e-9 * (t1.tv_nsec - t0.tv_nsec);
    printf("{\"iters\": %ld, \"seconds\": %.6f, \"ns_per_mul\": %.4f, \"sink\": \"%lx\"}\n",
           iters, dt, 1e9 * dt / (double)iters, c[0]);
    return 0;
}
