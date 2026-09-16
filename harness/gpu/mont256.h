/* 256-bit Montgomery field arithmetic for batched rho walks.
 *
 * Deliberately host/device dual-target: this header compiles unchanged under
 * nvcc (as __device__ code) and under a plain C compiler (as host code), so
 * the arithmetic can be differentially tested against the Python reference on
 * a machine with no GPU. Only the launch plumbing in rho_kernel.cu is then
 * CUDA-specific, which keeps the untested surface as small as possible.
 *
 * Representation: 4 x u64 limbs, little-endian, in the Montgomery domain with
 * R = 2^256. The modulus p is passed in per call rather than compiled in, so
 * one build serves every curve the harness benchmarks.
 */
#ifndef MONT256_H
#define MONT256_H

#include <stdint.h>

#ifdef __CUDACC__
#define MONT_FN static __device__ __forceinline__
#else
#define MONT_FN static inline
#endif

typedef uint64_t u64;
typedef unsigned __int128 u128;

#define NLIMB 4

MONT_FN void f_copy(u64 *r, const u64 *a) {
    for (int i = 0; i < NLIMB; i++) r[i] = a[i];
}

/* Returns 1 iff a >= b, comparing as 256-bit unsigned. */
MONT_FN int f_ge(const u64 *a, const u64 *b) {
    for (int i = NLIMB - 1; i >= 0; i--) {
        if (a[i] != b[i]) return a[i] > b[i];
    }
    return 1;
}

/* r = a - b (mod 2^256); returns the borrow out. */
MONT_FN u64 f_sub_raw(u64 *r, const u64 *a, const u64 *b) {
    u64 borrow = 0;
    for (int i = 0; i < NLIMB; i++) {
        u128 d = (u128)a[i] - b[i] - borrow;
        r[i] = (u64)d;
        borrow = (d >> 64) ? 1 : 0;
    }
    return borrow;
}

/* r = a + b (mod 2^256); returns the carry out. */
MONT_FN u64 f_add_raw(u64 *r, const u64 *a, const u64 *b) {
    u64 carry = 0;
    for (int i = 0; i < NLIMB; i++) {
        u128 s = (u128)a[i] + b[i] + carry;
        r[i] = (u64)s;
        carry = (u64)(s >> 64);
    }
    return carry;
}

/* r = (a + b) mod p, for a, b < p. */
MONT_FN void f_add(u64 *r, const u64 *a, const u64 *b, const u64 *p) {
    u64 carry = f_add_raw(r, a, b);
    if (carry || f_ge(r, p)) {
        u64 t[NLIMB];
        f_sub_raw(t, r, p);
        f_copy(r, t);
    }
}

/* r = (a - b) mod p, for a, b < p. */
MONT_FN void f_sub(u64 *r, const u64 *a, const u64 *b, const u64 *p) {
    u64 borrow = f_sub_raw(r, a, b);
    if (borrow) {
        u64 t[NLIMB];
        f_add_raw(t, r, p);
        f_copy(r, t);
    }
}

/* r = a * b * R^-1 mod p  (CIOS Montgomery multiplication).
 * n0 must be -p^-1 mod 2^64. Inputs and output are < p. */
MONT_FN void f_mul(u64 *r, const u64 *a, const u64 *b, const u64 *p, u64 n0) {
    u64 t[NLIMB + 2];
    for (int i = 0; i < NLIMB + 2; i++) t[i] = 0;

    for (int i = 0; i < NLIMB; i++) {
        u64 c = 0;
        for (int j = 0; j < NLIMB; j++) {
            u128 s = (u128)a[j] * b[i] + t[j] + c;
            t[j] = (u64)s;
            c = (u64)(s >> 64);
        }
        u128 s = (u128)t[NLIMB] + c;
        t[NLIMB] = (u64)s;
        t[NLIMB + 1] = (u64)(s >> 64);

        u64 m = t[0] * n0;
        u128 d = (u128)m * p[0] + t[0];
        u64 c2 = (u64)(d >> 64);
        for (int j = 1; j < NLIMB; j++) {
            u128 s2 = (u128)m * p[j] + t[j] + c2;
            t[j - 1] = (u64)s2;
            c2 = (u64)(s2 >> 64);
        }
        u128 s3 = (u128)t[NLIMB] + c2;
        t[NLIMB - 1] = (u64)s3;
        t[NLIMB] = t[NLIMB + 1] + (u64)(s3 >> 64);
    }

    if (t[NLIMB] || f_ge(t, p)) {
        f_sub_raw(r, t, p);
    } else {
        f_copy(r, t);
    }
}

MONT_FN void f_sqr(u64 *r, const u64 *a, const u64 *p, u64 n0) {
    f_mul(r, a, a, p, n0);
}

/* r = a^-1 mod p via Fermat: a^(p-2). Constant ~381 multiplications for a
 * 256-bit p, which is why callers MUST amortize it with f_batch_inv below --
 * one inversion per batch, three multiplications per element. */
MONT_FN void f_inv(u64 *r, const u64 *a, const u64 *p, u64 n0, const u64 *one) {
    u64 e[NLIMB];
    u64 two[NLIMB] = {2, 0, 0, 0};
    f_sub_raw(e, p, two);          /* e = p - 2, no borrow for p > 2 */

    u64 acc[NLIMB], base[NLIMB];
    f_copy(acc, one);
    f_copy(base, a);
    for (int i = 0; i < 256; i++) {
        if ((e[i >> 6] >> (i & 63)) & 1ULL) {
            u64 t[NLIMB];
            f_mul(t, acc, base, p, n0);
            f_copy(acc, t);
        }
        u64 t2[NLIMB];
        f_sqr(t2, base, p, n0);
        f_copy(base, t2);
    }
    f_copy(r, acc);
}

/* Montgomery's batch inversion over `n` elements held with stride `stride`
 * limbs: out[i] = in[i]^-1, using ONE f_inv and 3(n-1) multiplications.
 * `scratch` must hold n*NLIMB limbs. Zero inputs are not tolerated; a rho walk
 * hits one only on a genuine collision, which the caller detects separately. */
MONT_FN void f_batch_inv(u64 *out, const u64 *in, u64 *scratch, int n,
                         int stride, const u64 *p, u64 n0, const u64 *one) {
    u64 acc[NLIMB];
    f_copy(acc, one);
    for (int i = 0; i < n; i++) {
        f_copy(&scratch[(size_t)i * NLIMB], acc);      /* prefix product */
        u64 t[NLIMB];
        f_mul(t, acc, &in[(size_t)i * stride], p, n0);
        f_copy(acc, t);
    }

    u64 inv[NLIMB];
    f_inv(inv, acc, p, n0, one);

    for (int i = n - 1; i >= 0; i--) {
        u64 t[NLIMB];
        f_mul(t, &scratch[(size_t)i * NLIMB], inv, p, n0);
        f_copy(&out[(size_t)i * stride], t);
        f_mul(t, inv, &in[(size_t)i * stride], p, n0);
        f_copy(inv, t);
    }
}

/* One affine r-adding step: (x, y) <- (x, y) + (tx, ty), given a PRECOMPUTED
 * dxinv = (x - tx)^-1. Split this way because the inversion is batched across
 * walks; this is the whole reason a batched rho is ~10x an unbatched one.
 * Cost here: 3 f_mul (lambda, lambda^2, the y update) + cheap add/sub. */
MONT_FN void ec_add_affine_pre(u64 *x, u64 *y, const u64 *tx, const u64 *ty,
                               const u64 *dxinv, const u64 *p, u64 n0) {
    u64 dy[NLIMB], lam[NLIMB], lam2[NLIMB], xr[NLIMB], t[NLIMB];
    f_sub(dy, y, ty, p);
    f_mul(lam, dy, dxinv, p, n0);
    f_sqr(lam2, lam, p, n0);
    f_sub(xr, lam2, x, p);
    f_sub(xr, xr, tx, p);
    f_sub(t, x, xr, p);
    f_mul(t, lam, t, p, n0);
    f_sub(y, t, y, p);
    f_copy(x, xr);
}

/* r = (a + b) mod m for the scalar accumulators (mod the group order, not p).
 * Included so the benchmark does not understate a real walk: rho must carry
 * (a, b) with every step or a collision is worthless. */
MONT_FN void s_addmod(u64 *r, const u64 *a, const u64 *b, const u64 *m) {
    u64 carry = f_add_raw(r, a, b);
    if (carry || f_ge(r, m)) {
        u64 t[NLIMB];
        f_sub_raw(t, r, m);
        f_copy(r, t);
    }
}

#endif /* MONT256_H */
