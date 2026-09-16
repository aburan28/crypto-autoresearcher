/* Host-side differential test for mont256.h.
 *
 * The point of this file: a GPU benchmark whose arithmetic is wrong reports a
 * throughput number for nothing. mont256.h is written to compile as plain C,
 * so the exact field and walk arithmetic the kernel runs can be executed here
 * and compared limb-for-limb against the independent Python implementation in
 * bench_rho_throughput.py -- on any machine, with no CUDA toolchain and no
 * GPU. Only the launch plumbing in rho_kernel.cu remains untested by this.
 *
 * Reads a whitespace-separated case from stdin, writes final state to stdout.
 * Both formats are defined in bench_rho_throughput.py (_selftest_vectors).
 *
 *   cc -O2 -o mont256_selftest mont256_selftest.c && ./mont256_selftest < case
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "mont256.h"

#define LIMBS 4
#define MAXB  64
#define MAXW  4096

static void rd(u64 *r) {
    char buf[80];
    if (scanf("%79s", buf) != 1) { fprintf(stderr, "short input\n"); exit(2); }
    /* 64 hex chars, big-endian, into 4 little-endian limbs */
    size_t len = strlen(buf);
    if (len != 64) { fprintf(stderr, "bad width %zu\n", len); exit(2); }
    for (int i = 0; i < LIMBS; i++) {
        char part[17];
        memcpy(part, buf + (LIMBS - 1 - i) * 16, 16);
        part[16] = 0;
        r[i] = strtoull(part, NULL, 16);
    }
}

static void wr(const u64 *v) {
    for (int i = LIMBS - 1; i >= 0; i--) printf("%016llx", (unsigned long long)v[i]);
    printf("\n");
}

int main(void) {
    u64 p[LIMBS], one[LIMBS], order[LIMBS];
    unsigned long long n0raw;
    int nbranch, nwalks, nsteps, dp_bits;

    rd(p);
    if (scanf("%llx", &n0raw) != 1) return 2;
    rd(one);
    rd(order);
    if (scanf("%d %d %d %d", &nbranch, &nwalks, &nsteps, &dp_bits) != 4) return 2;
    if (nbranch > MAXB || nwalks > MAXW) { fprintf(stderr, "too big\n"); return 2; }

    static u64 TX[MAXB * LIMBS], TY[MAXB * LIMBS], TC[MAXB * LIMBS], TD[MAXB * LIMBS];
    for (int s = 0; s < nbranch; s++) {
        rd(&TX[s * LIMBS]); rd(&TY[s * LIMBS]);
        rd(&TC[s * LIMBS]); rd(&TD[s * LIMBS]);
    }
    static u64 X[MAXW * LIMBS], Y[MAXW * LIMBS], A[MAXW * LIMBS], B[MAXW * LIMBS];
    for (int i = 0; i < nwalks; i++) {
        rd(&X[i * LIMBS]); rd(&Y[i * LIMBS]); rd(&A[i * LIMBS]); rd(&B[i * LIMBS]);
    }

    static u64 dx[MAXW * LIMBS], di[MAXW * LIMBS], sc[MAXW * LIMBS];
    u64 n0 = (u64)n0raw;
    unsigned int mask = (unsigned int)(nbranch - 1);
    unsigned long long dps = 0;

    /* Identical structure to the kernel's per-thread loop. */
    for (int step = 0; step < nsteps; step++) {
        for (int i = 0; i < nwalks; i++) {
            unsigned int s = (unsigned int)X[(size_t)i * LIMBS] & mask;
            f_sub(&dx[(size_t)i * LIMBS], &X[(size_t)i * LIMBS], &TX[(size_t)s * LIMBS], p);
        }
        f_batch_inv(di, dx, sc, nwalks, LIMBS, p, n0, one);
        for (int i = 0; i < nwalks; i++) {
            unsigned int s = (unsigned int)X[(size_t)i * LIMBS] & mask;
            ec_add_affine_pre(&X[(size_t)i * LIMBS], &Y[(size_t)i * LIMBS],
                              &TX[(size_t)s * LIMBS], &TY[(size_t)s * LIMBS],
                              &di[(size_t)i * LIMBS], p, n0);
            s_addmod(&A[(size_t)i * LIMBS], &A[(size_t)i * LIMBS], &TC[(size_t)s * LIMBS], order);
            s_addmod(&B[(size_t)i * LIMBS], &B[(size_t)i * LIMBS], &TD[(size_t)s * LIMBS], order);
            u64 lo = X[(size_t)i * LIMBS];
            if (dp_bits > 0 && (lo & ((1ULL << dp_bits) - 1ULL)) == 0ULL) dps++;
        }
    }

    printf("%llu\n", dps);
    for (int i = 0; i < nwalks; i++) {
        wr(&X[i * LIMBS]); wr(&Y[i * LIMBS]); wr(&A[i * LIMBS]); wr(&B[i * LIMBS]);
    }
    return 0;
}
