/*
 * pdp_enum.c -- independent exhaustive UNSAT/SAT decision for the Koblitz
 * point-decomposition instances of EXP-FROB-30006a.
 *
 * Written from the field / curve / summation-polynomial definitions only; it
 * shares no code with WDSat or with the ANF generator (gen_instance.py), and it
 * never reads the ANF.  It decides the ALGEBRAIC predicate the ANF encodes,
 *
 *     exists X_1..X_m in V :  S_{m+1}(X_1, ..., X_m, X_r) = 0      (over GF(2^n)),
 *
 * by enumerating the factor base V (2^l elements) resp. unordered pairs of it
 * (m = 3) and solving the remaining quadratic(s) in closed form:
 *
 *   m = 2 : S3(X1, X2, Xr) = (X1+Xr)^2 X2^2 + X1 Xr X2 + (X1 Xr)^2 + 1 = 0 solved for X2.
 *   m = 3 : S4 = Res_X( p(X) = S3(X1,X2,X), q(X) = S3(X3,Xr,X) ).  For A = lc(p) != 0 and
 *           D = lc(q) != 0 (D = 0 iff X3 = Xr, impossible when Xr is not in V, which is
 *           checked), Res = 0 iff p and q share a root in the algebraic closure, i.e. iff
 *           (p has a root X in GF(2^n) and q(X) = 0) or (p has no rational root and q is
 *           proportional to p).  For A = 0 (X1 = X2) p is linear and Res = D * (B^2 q(C/B))
 *           so Res = 0 iff q(C/B) = 0.  Every branch is enumerated explicitly.
 *
 * As a cross-check it also counts RATIONAL geometric decompositions
 * (x(R +- P1 [+- P2]) in V for rational lifts P_i); for m = 2 and R not of order 2
 * the two predicates coincide (proof in implementation.md), for m = 3 the geometric
 * count is a subset (twist decompositions are algebraic but not rational).
 *
 * Input: a parameter file written by the driver (one "key value" per line, hex values):
 *   n, modulus, a, m, l, xr, basis (l values), pcheck (n-l values)
 * Output: one JSON object on stdout.
 *
 * Build: gcc -O2 -mpclmul -msse4.1 -o pdp_enum pdp_enum.c
 */
#include <immintrin.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

typedef uint64_t u64;

static int N;              /* field degree */
static u64 MOD;            /* modulus with bit N set */
static u64 MODLOW;         /* modulus without bit N */
static u64 MASK;           /* (1<<N)-1 */
static int CURVE_A;
static int M, L;
static u64 XR;
static u64 BASIS[64];
static u64 PCHECK[64];
static int NPCHECK;
static u64 TRMASK;         /* Tr(v) = parity(v & TRMASK) */
static u64 HT[64];         /* half-trace rows */
static u64 SQRT[64];       /* sqrt rows */

static inline u64 clmul(u64 a, u64 b, u64 *hi) {
    __m128i x = _mm_set_epi64x(0, (long long)a), y = _mm_set_epi64x(0, (long long)b);
    __m128i r = _mm_clmulepi64_si128(x, y, 0x00);
    *hi = (u64)_mm_extract_epi64(r, 1);
    return (u64)_mm_extract_epi64(r, 0);
}

/* reduce a product of degree < 2N-1 (given as 128-bit lo/hi) modulo MOD */
static inline u64 reduce(u64 lo, u64 hi) {
    /* x^N == MODLOW (mod MOD); the high part h = p >> N has degree <= N-2 */
    u64 h = (lo >> N) | (N < 64 ? (hi << (64 - N)) : 0);
    u64 low = lo & MASK;
    for (int round = 0; round < 3 && h; ++round) {
        u64 t_hi, t_lo = clmul(h, MODLOW, &t_hi);
        (void)t_hi;                            /* deg h + deg MODLOW < 64 for N <= 43 */
        low ^= t_lo & MASK;
        h = t_lo >> N;
    }
    if (h) { fprintf(stderr, "reduction did not converge\n"); exit(2); }
    return low;
}

static inline u64 gmul(u64 a, u64 b) { u64 hi; u64 lo = clmul(a, b, &hi); return reduce(lo, hi); }
static inline u64 gsqr(u64 a) { return gmul(a, a); }

static u64 gpow2k(u64 a, int k) { for (int i = 0; i < k; ++i) a = gsqr(a); return a; }

/* Itoh-Tsujii: a^{-1} = (a^{2^{N-1}-1})^2 */
static u64 ginv(u64 a) {
    if (!a) { fprintf(stderr, "inverse of zero\n"); exit(2); }
    int k = N - 1;
    int top = 63 - __builtin_clzll((u64)k);
    u64 b = a; int i = 1;                       /* b = a^{2^i - 1} */
    for (int bit = top - 1; bit >= 0; --bit) {
        b = gmul(gpow2k(b, i), b); i *= 2;
        if ((k >> bit) & 1) { b = gmul(gsqr(b), a); i += 1; }
    }
    if (i != k) { fprintf(stderr, "chain error\n"); exit(2); }
    return gsqr(b);
}

static inline int parity(u64 v) { return __builtin_popcountll(v) & 1; }
static inline int gtrace(u64 v) { return parity(v & TRMASK); }
static inline u64 apply_rows(const u64 *rows, u64 v) { u64 r = 0; while (v) { int i = __builtin_ctzll(v); r ^= rows[i]; v &= v - 1; } return r; }
static inline u64 ghalftrace(u64 v) { return apply_rows(HT, v); }
static inline u64 gsqrt(u64 v) { return apply_rows(SQRT, v); }
static inline int in_V(u64 v) { for (int i = 0; i < NPCHECK; ++i) if (parity(v & PCHECK[i])) return 0; return 1; }

/* roots of z^2 + b z + c; returns count, roots in r[] */
static inline int solve_quad(u64 b, u64 c, u64 *r) {
    if (b == 0) { r[0] = gsqrt(c); return 1; }
    u64 d = gmul(c, ginv(gsqr(b)));
    if (gtrace(d)) return 0;
    u64 w = ghalftrace(d);
    r[0] = gmul(b, w); r[1] = r[0] ^ b;
    return 2;
}

static void init_tables(void) {
    MASK = (N == 64) ? ~0ULL : ((1ULL << N) - 1);
    MODLOW = MOD & MASK;
    TRMASK = 0;
    for (int i = 0; i < N; ++i) {
        u64 v = 1ULL << i, t = v;
        for (int j = 0; j < N - 1; ++j) t = gsqr(t) ^ v;
        if (t & ~1ULL) { fprintf(stderr, "trace not in F_2\n"); exit(2); }
        if (t) TRMASK |= 1ULL << i;
        /* half-trace of t^i: sum_{j=0}^{(N-1)/2} v^{4^j} */
        u64 h = v, p = v;
        for (int j = 0; j < (N - 1) / 2; ++j) { p = gsqr(gsqr(p)); h ^= p; }
        HT[i] = h;
        SQRT[i] = gpow2k(v, N - 1);
    }
    /* sanity: H(a)^2 + H(a) = a + Tr(a) on a few values; sqrt(a)^2 = a */
    for (u64 a = 1; a < 200; a += 37) {
        u64 h = ghalftrace(a);
        if ((gsqr(h) ^ h) != (a ^ (u64)gtrace(a))) { fprintf(stderr, "half-trace table wrong\n"); exit(2); }
        if (gsqr(gsqrt(a)) != a) { fprintf(stderr, "sqrt table wrong\n"); exit(2); }
        if (gmul(a, ginv(a)) != 1) { fprintf(stderr, "inverse wrong\n"); exit(2); }
    }
}

/* ---------------------------------------------------------------- curve (b = 1) */
typedef struct { u64 x, y; int inf; } pt;

static inline u64 rhs(u64 x) { u64 x2 = gsqr(x); return gmul(x2, x) ^ (CURVE_A ? x2 : 0) ^ 1; }
static inline int lift(u64 x, pt *P) {           /* one rational lift, or 0 */
    u64 r[2]; int k = solve_quad(x, rhs(x), r);
    if (!k) return 0;
    P->x = x; P->y = r[0]; P->inf = 0; return 1;
}
static inline pt neg(pt P) { if (!P.inf) P.y ^= P.x; return P; }
static pt add(pt P, pt Q) {
    pt R = {0, 0, 1};
    if (P.inf) return Q;
    if (Q.inf) return P;
    u64 lam, x3, y3;
    if (P.x == Q.x) {
        if ((P.y ^ Q.y) == P.x || P.x == 0) return R;
        lam = P.x ^ gmul(P.y, ginv(P.x));
        x3 = gsqr(lam) ^ lam ^ (u64)CURVE_A;
        y3 = gsqr(P.x) ^ gmul(lam ^ 1, x3);
    } else {
        lam = gmul(P.y ^ Q.y, ginv(P.x ^ Q.x));
        x3 = gsqr(lam) ^ lam ^ P.x ^ Q.x ^ (u64)CURVE_A;
        y3 = gmul(lam, P.x ^ x3) ^ x3 ^ P.y;
    }
    R.x = x3; R.y = y3; R.inf = 0;
    return R;
}
static int on_curve(pt P) { if (P.inf) return 1; return (gsqr(P.y) ^ gmul(P.x, P.y)) == rhs(P.x); }

/* ---------------------------------------------------------------- witnesses */
#ifndef MAXW
#define MAXW 8
#endif
static u64 wit[MAXW][3]; static int nwit = 0; static long long n_alg_wit = 0, n_geo_wit = 0;
static void record_witness(u64 x1, u64 x2, u64 x3) {
    n_alg_wit++;
    if (nwit < MAXW) { wit[nwit][0] = x1; wit[nwit][1] = x2; wit[nwit][2] = x3; nwit++; }
}

/* S3(x1,x2,x3) for verification of witnesses */
static u64 S3(u64 x1, u64 x2, u64 x3) { u64 e2 = gmul(x1, x2) ^ gmul(x1, x3) ^ gmul(x2, x3); return gsqr(e2) ^ gmul(gmul(x1, x2), x3) ^ 1; }
/* Sylvester resultant of two quadratics (char 2) */
static u64 res2(u64 A, u64 B, u64 C, u64 D, u64 E, u64 G) { return gsqr(gmul(A, G) ^ gmul(C, D)) ^ gmul(gmul(A, E) ^ gmul(B, D), gmul(B, G) ^ gmul(C, E)); }
static u64 S4(u64 x1, u64 x2, u64 x3, u64 x4) {
    u64 A = gsqr(x1 ^ x2), B = gmul(x1, x2), C = gsqr(B) ^ 1;
    u64 D = gsqr(x3 ^ x4), E = gmul(x3, x4), G = gsqr(E) ^ 1;
    return res2(A, B, C, D, E, G);
}

/* solve S3(X3, Xr, X) = 0 for X3 given X (rational); record witnesses in V */
static void x3_from_common_root(u64 x1, u64 x2, u64 X) {
    u64 Dp = gsqr(X ^ XR), Ep = gmul(X, XR), Gp = gsqr(Ep) ^ 1;   /* Dp X3^2 + Ep X3 + Gp */
    u64 r[2]; int k;
    if (Dp == 0) { if (Ep == 0) return; r[0] = gmul(Gp, ginv(Ep)); k = 1; }
    else { u64 iD = ginv(Dp); k = solve_quad(gmul(Ep, iD), gmul(Gp, iD), r); }
    for (int i = 0; i < k; ++i) if (in_V(r[i])) record_witness(x1, x2, r[i]);
}

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: pdp_enum params.txt [--limit K]\n"); return 2; }
    long long limit = -1;
    if (argc >= 4 && !strcmp(argv[2], "--limit")) limit = atoll(argv[3]);
    FILE *f = fopen(argv[1], "r");
    if (!f) { perror("params"); return 2; }
    char key[64]; char val[128]; int nb = 0;
    while (fscanf(f, "%63s %127s", key, val) == 2) {
        if (!strcmp(key, "n")) N = atoi(val);
        else if (!strcmp(key, "modulus")) MOD = strtoull(val, 0, 16);
        else if (!strcmp(key, "a")) CURVE_A = atoi(val);
        else if (!strcmp(key, "m")) M = atoi(val);
        else if (!strcmp(key, "l")) L = atoi(val);
        else if (!strcmp(key, "xr")) XR = strtoull(val, 0, 16);
        else if (!strcmp(key, "basis")) BASIS[nb++] = strtoull(val, 0, 16);
        else if (!strcmp(key, "pcheck")) PCHECK[NPCHECK++] = strtoull(val, 0, 16);
        else { fprintf(stderr, "unknown key %s\n", key); return 2; }
    }
    fclose(f);
    if (N < 2 || N > 43 || nb != L || NPCHECK != N - L || (M != 2 && M != 3)) { fprintf(stderr, "bad params (n=%d l=%d nb=%d npc=%d m=%d)\n", N, L, nb, NPCHECK, M); return 2; }
    init_tables();
    /* parity-check consistency: every basis vector is in V */
    for (int i = 0; i < L; ++i) if (!in_V(BASIS[i])) { fprintf(stderr, "basis vector %d fails its own parity check\n", i); return 2; }
    int xr_in_V = in_V(XR);
    pt R; int r_ok = lift(XR, &R);
    if (!r_ok) { fprintf(stderr, "Xr is not an abscissa of E(GF(2^n))\n"); return 2; }
    if (!on_curve(R)) { fprintf(stderr, "R not on curve\n"); return 2; }

    struct timespec t0, t1; clock_gettime(CLOCK_MONOTONIC, &t0);
    long long total = 1LL << L, n_x1_rational = 0, pairs = 0, n_alg_x1 = 0, n_pairs_no_rational_root = 0, n_geo_only_mismatch = 0;
    u64 X1 = 0;
    for (long long i = 0; i < total; ++i) {
        if (i) { int b = __builtin_ctzll((u64)i); X1 ^= BASIS[b]; }         /* Gray code */
        if (limit >= 0 && i >= limit) break;
        pt P1; int p1_rat = lift(X1, &P1); n_x1_rational += p1_rat;
        if (M == 2) {
            /* algebraic: (X1+Xr)^2 X2^2 + X1 Xr X2 + (X1 Xr)^2 + 1 = 0 */
            u64 A = gsqr(X1 ^ XR), B = gmul(X1, XR), C = gsqr(B) ^ 1; u64 r[2]; int k; int alg = 0;
            if (A == 0) { if (B == 0) k = 0; else { r[0] = gmul(C, ginv(B)); k = 1; } }
            else { u64 iA = ginv(A); k = solve_quad(gmul(B, iA), gmul(C, iA), r); }
            for (int j = 0; j < k; ++j) if (in_V(r[j])) { alg = 1; record_witness(X1, r[j], 0); }
            n_alg_x1 += alg;
            /* geometric (rational) cross-check */
            int geo = 0;
            if (p1_rat) for (int s = 0; s < 2; ++s) { pt Q = add(R, s ? neg(P1) : P1); if (!Q.inf && in_V(Q.x)) geo = 1; }
            n_geo_wit += geo;
            if (geo != alg) n_geo_only_mismatch++;
        } else {
            u64 X2 = X1; long long j0 = i;
            for (long long j = i; j < total; ++j) {
                if (j != j0) { int b = __builtin_ctzll((u64)j); X2 ^= BASIS[b]; }
                pairs++;
                u64 A = gsqr(X1 ^ X2), B = gmul(X1, X2), C = gsqr(B) ^ 1;
                if (A == 0) {                                  /* X1 == X2: p linear, root C/B  (B = X1^2) */
                    if (B != 0) x3_from_common_root(X1, X2, gmul(C, ginv(B)));
                    /* B == 0 (X1 = X2 = 0): Res = D^2, zero only if X3 = Xr, excluded by Xr not in V */
                } else {
                    u64 iA = ginv(A); u64 r[2]; int k = solve_quad(gmul(B, iA), gmul(C, iA), r);
                    if (k) { for (int t = 0; t < k; ++t) x3_from_common_root(X1, X2, r[t]); }
                    else {
                        n_pairs_no_rational_root++;
                        /* q proportional to p: E/D = B/A =: beta  ->  beta X3^2 + Xr X3 + beta Xr^2 = 0 */
                        u64 beta = gmul(B, iA);
                        u64 ib = ginv(beta);
                        u64 rr[2]; int kk = solve_quad(gmul(XR, ib), gsqr(XR), rr);
                        for (int t = 0; t < kk; ++t) {
                            u64 X3 = rr[t];
                            if (!in_V(X3)) continue;
                            u64 D = gsqr(X3 ^ XR), G = gsqr(gmul(X3, XR)) ^ 1;
                            if (gmul(G, A) == gmul(C, D)) record_witness(X1, X2, X3);
                        }
                    }
                }
                /* geometric rational cross-check */
                pt P2; if (p1_rat && lift(X2, &P2)) {
                    for (int s = 0; s < 4; ++s) {
                        pt Q = add(add(R, (s & 1) ? neg(P1) : P1), (s & 2) ? neg(P2) : P2);
                        if (!Q.inf && in_V(Q.x)) n_geo_wit++;
                    }
                }
            }
        }
    }
    clock_gettime(CLOCK_MONOTONIC, &t1);
    double secs = (t1.tv_sec - t0.tv_sec) + 1e-9 * (t1.tv_nsec - t0.tv_nsec);
    /* verify recorded witnesses with the summation polynomial directly */
    int wit_verified = 1;
    for (int w = 0; w < nwit; ++w) {
        u64 v = (M == 2) ? S3(wit[w][0], wit[w][1], XR) : S4(wit[w][0], wit[w][1], wit[w][2], XR);
        if (v != 0) wit_verified = 0;
        if (!in_V(wit[w][0]) || !in_V(wit[w][1]) || (M == 3 && !in_V(wit[w][2]))) wit_verified = 0;
    }
    printf("{\n \"tool\": \"pdp_enum.c\", \"n\": %d, \"m\": %d, \"l\": %d, \"a\": %d, \"modulus_hex\": \"0x%llx\", \"xr_hex\": \"0x%llx\",\n",
           N, M, L, CURVE_A, (unsigned long long)MOD, (unsigned long long)XR);
    printf(" \"xr_in_V\": %s, \"R_y_hex\": \"0x%llx\", \"complete\": %s, \"enumerated_x1\": %lld, \"enumerated_pairs\": %lld,\n",
           xr_in_V ? "true" : "false", (unsigned long long)R.y, (limit < 0) ? "true" : "false", (limit < 0 ? total : (limit < total ? limit : total)), pairs);
    printf(" \"verdict\": \"%s\", \"n_algebraic_witnesses\": %lld, \"n_x1_with_algebraic_witness\": %lld, \"n_x1_rational_abscissa\": %lld,\n",
           n_alg_wit ? "SAT" : "UNSAT", n_alg_wit, n_alg_x1, n_x1_rational);
    printf(" \"n_geometric_rational_witnesses\": %lld, \"m2_geo_alg_mismatches\": %lld, \"m3_pairs_without_rational_common_root_candidate\": %lld,\n",
           n_geo_wit, n_geo_only_mismatch, n_pairs_no_rational_root);
    printf(" \"witnesses_verified_by_summation_polynomial\": %s, \"witnesses\": [", wit_verified ? "true" : "false");
    for (int w = 0; w < nwit; ++w) printf("%s[\"0x%llx\", \"0x%llx\", \"0x%llx\"]", w ? ", " : "", (unsigned long long)wit[w][0], (unsigned long long)wit[w][1], (unsigned long long)wit[w][2]);
    printf("],\n \"elapsed_s\": %.3f\n}\n", secs);
    return 0;
}
