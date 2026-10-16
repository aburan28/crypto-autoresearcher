/* isobench: timed variable-base scalar multiplication on E versus on an
 * isogenous a = -3 model, with and without the isogeny route.
 *
 * Field: 4 x 64-bit limbs, Montgomery CIOS (R = 2^256), any odd p < 2^256 (the extra
 * accumulator words t[4], t[5] carry the top; outputs are checked against a reference).
 * Squaring is a multiplication (S = M, the cost model's convention).
 * Curve: short Weierstrass, Jacobian coordinates.
 *   generic a : dbl-2007-bl (1M + 8S + one multiplication by a)
 *   a = -3    : dbl-2001-b  (3M + 5S)
 *   both      : add-2007-bl (11M + 5S), signed width-5 NAF, table of 8 odd multiples
 * Route step (homogenised, Jacobian in and out): X' = N_h(X,Z^2), Y' = Y M_h(X,Z^2),
 *   Z' = Z psi_h(X,Z^2), then an isomorphism as Z' *= u^-1.
 *
 * Input on stdin (hex, whitespace separated), output on stdout: see isobench.py.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

typedef unsigned __int128 u128;
typedef struct { uint64_t v[4]; } fe;
typedef struct { fe p, r2, one; uint64_t inv; } field;

static void fe_from_hex(fe *r, const char *s) {
    memset(r, 0, sizeof *r);
    size_t n = strlen(s);
    for (size_t i = 0; i < n; i++) {
        char c = s[n - 1 - i];
        uint64_t d = (c >= '0' && c <= '9') ? c - '0' : (c | 32) - 'a' + 10;
        r->v[i / 16] |= d << (4 * (i % 16));
    }
}
static void fe_to_hex(const fe *a, char *out) {
    sprintf(out, "%016llx%016llx%016llx%016llx", (unsigned long long)a->v[3], (unsigned long long)a->v[2],
            (unsigned long long)a->v[1], (unsigned long long)a->v[0]);
}
static int geq(const fe *a, const fe *b) {
    for (int i = 3; i >= 0; i--) { if (a->v[i] != b->v[i]) return a->v[i] > b->v[i]; }
    return 1;
}
static void sub_raw(fe *r, const fe *a, const fe *b) {
    uint64_t br = 0;
    for (int i = 0; i < 4; i++) {
        u128 t = (u128)a->v[i] - b->v[i] - br;
        r->v[i] = (uint64_t)t; br = (t >> 64) ? 1 : 0;
    }
}
static void fadd(const field *F, fe *r, const fe *a, const fe *b) {
    uint64_t c = 0; fe t;
    for (int i = 0; i < 4; i++) { u128 s = (u128)a->v[i] + b->v[i] + c; t.v[i] = (uint64_t)s; c = (uint64_t)(s >> 64); }
    if (c || geq(&t, &F->p)) sub_raw(&t, &t, &F->p);
    *r = t;
}
static void fsub(const field *F, fe *r, const fe *a, const fe *b) {
    fe t; uint64_t br = 0;
    for (int i = 0; i < 4; i++) { u128 d = (u128)a->v[i] - b->v[i] - br; t.v[i] = (uint64_t)d; br = (d >> 64) ? 1 : 0; }
    if (br) { uint64_t c = 0; for (int i = 0; i < 4; i++) { u128 s = (u128)t.v[i] + F->p.v[i] + c; t.v[i] = (uint64_t)s; c = (uint64_t)(s >> 64); } }
    *r = t;
}
static void fmul(const field *F, fe *r, const fe *a, const fe *b) {
    uint64_t t[6] = {0};
    for (int i = 0; i < 4; i++) {
        uint64_t c = 0;
        for (int j = 0; j < 4; j++) { u128 s = (u128)a->v[j] * b->v[i] + t[j] + c; t[j] = (uint64_t)s; c = (uint64_t)(s >> 64); }
        u128 s = (u128)t[4] + c; t[4] = (uint64_t)s; t[5] = (uint64_t)(s >> 64);
        uint64_t m = t[0] * F->inv;
        s = (u128)m * F->p.v[0] + t[0]; c = (uint64_t)(s >> 64);
        for (int j = 1; j < 4; j++) { s = (u128)m * F->p.v[j] + t[j] + c; t[j - 1] = (uint64_t)s; c = (uint64_t)(s >> 64); }
        s = (u128)t[4] + c; t[3] = (uint64_t)s; t[4] = t[5] + (uint64_t)(s >> 64);
    }
    fe res = {{t[0], t[1], t[2], t[3]}};
    if (t[4] || geq(&res, &F->p)) sub_raw(&res, &res, &F->p);
    *r = res;
}
static void fsqr(const field *F, fe *r, const fe *a) { fmul(F, r, a, a); }
static void field_init(field *F, const char *phex) {
    fe_from_hex(&F->p, phex);
    uint64_t x = 1;                                   /* -p^-1 mod 2^64 by Newton */
    for (int i = 0; i < 6; i++) x *= 2 - F->p.v[0] * x;
    F->inv = (uint64_t)(-(int64_t)0) - x;
    F->inv = ~x + 1;
    fe r = {{1, 0, 0, 0}};                            /* R mod p and R^2 mod p by doubling */
    for (int i = 0; i < 256; i++) fadd(F, &r, &r, &r);
    F->one = r;
    fe r2 = r;
    for (int i = 0; i < 256; i++) fadd(F, &r2, &r2, &r2);
    F->r2 = r2;
}
static void to_mont(const field *F, fe *r, const fe *a) { fmul(F, r, a, &F->r2); }
static void from_mont(const field *F, fe *r, const fe *a) { fe one = {{1, 0, 0, 0}}; fmul(F, r, a, &one); }
static int fis_zero(const fe *a) { return !(a->v[0] | a->v[1] | a->v[2] | a->v[3]); }
static void finv(const field *F, fe *r, const fe *a) {   /* a^(p-2) */
    fe e, two = {{2, 0, 0, 0}}; sub_raw(&e, &F->p, &two);
    fe acc = F->one, b = *a;
    for (int i = 0; i < 256; i++) {
        if ((e.v[i / 64] >> (i % 64)) & 1) fmul(F, &acc, &acc, &b);
        fsqr(F, &b, &b);
    }
    *r = acc;
}

typedef struct { fe X, Y, Z; int inf; } jac;

static void dbl_generic(const field *F, const fe *a, jac *R, const jac *P) {
    if (P->inf) { *R = *P; return; }
    fe XX, YY, YYYY, ZZ, S, M, T, t;
    fsqr(F, &XX, &P->X); fsqr(F, &YY, &P->Y); fsqr(F, &YYYY, &YY); fsqr(F, &ZZ, &P->Z);
    fadd(F, &t, &P->X, &YY); fsqr(F, &t, &t); fsub(F, &t, &t, &XX); fsub(F, &t, &t, &YYYY); fadd(F, &S, &t, &t);
    fsqr(F, &t, &ZZ); fmul(F, &t, &t, a); fadd(F, &M, &XX, &XX); fadd(F, &M, &M, &XX); fadd(F, &M, &M, &t);
    fsqr(F, &T, &M); fsub(F, &T, &T, &S); fsub(F, &T, &T, &S);
    fe Z3; fadd(F, &t, &P->Y, &P->Z); fsqr(F, &t, &t); fsub(F, &t, &t, &YY); fsub(F, &Z3, &t, &ZZ);
    fe Y3; fsub(F, &t, &S, &T); fmul(F, &Y3, &M, &t);
    fadd(F, &t, &YYYY, &YYYY); fadd(F, &t, &t, &t); fadd(F, &t, &t, &t); fsub(F, &Y3, &Y3, &t);
    R->X = T; R->Y = Y3; R->Z = Z3; R->inf = 0;
}
static void dbl_am3(const field *F, const fe *a, jac *R, const jac *P) {
    (void)a;
    if (P->inf) { *R = *P; return; }
    fe delta, gamma, beta, alpha, t, u, X3, Y3, Z3;
    fsqr(F, &delta, &P->Z); fsqr(F, &gamma, &P->Y); fmul(F, &beta, &P->X, &gamma);
    fsub(F, &t, &P->X, &delta); fadd(F, &u, &P->X, &delta); fmul(F, &alpha, &t, &u);
    fadd(F, &t, &alpha, &alpha); fadd(F, &alpha, &alpha, &t);
    fsqr(F, &X3, &alpha); fadd(F, &t, &beta, &beta); fadd(F, &t, &t, &t); fadd(F, &u, &t, &t); fsub(F, &X3, &X3, &u);
    fadd(F, &t, &P->Y, &P->Z); fsqr(F, &t, &t); fsub(F, &t, &t, &gamma); fsub(F, &Z3, &t, &delta);
    fadd(F, &t, &beta, &beta); fadd(F, &t, &t, &t); fsub(F, &t, &t, &X3); fmul(F, &Y3, &alpha, &t);
    fsqr(F, &t, &gamma); fadd(F, &t, &t, &t); fadd(F, &t, &t, &t); fadd(F, &t, &t, &t); fsub(F, &Y3, &Y3, &t);
    R->X = X3; R->Y = Y3; R->Z = Z3; R->inf = 0;
}
typedef void (*dblf)(const field *, const fe *, jac *, const jac *);
static void add(const field *F, const fe *a, dblf dbl, jac *R, const jac *P, const jac *Q) {
    if (P->inf) { *R = *Q; return; }
    if (Q->inf) { *R = *P; return; }
    fe Z1Z1, Z2Z2, U1, U2, S1, S2, H, I, J, r, V, t, X3, Y3, Z3;
    fsqr(F, &Z1Z1, &P->Z); fsqr(F, &Z2Z2, &Q->Z);
    fmul(F, &U1, &P->X, &Z2Z2); fmul(F, &U2, &Q->X, &Z1Z1);
    fmul(F, &t, &Q->Z, &Z2Z2); fmul(F, &S1, &P->Y, &t);
    fmul(F, &t, &P->Z, &Z1Z1); fmul(F, &S2, &Q->Y, &t);
    fsub(F, &H, &U2, &U1); fsub(F, &r, &S2, &S1);
    if (fis_zero(&H)) {
        if (fis_zero(&r)) { dbl(F, a, R, P); return; }
        R->inf = 1; return;
    }
    fadd(F, &r, &r, &r);
    fadd(F, &t, &H, &H); fsqr(F, &I, &t); fmul(F, &J, &H, &I); fmul(F, &V, &U1, &I);
    fsqr(F, &X3, &r); fsub(F, &X3, &X3, &J); fsub(F, &X3, &X3, &V); fsub(F, &X3, &X3, &V);
    fsub(F, &t, &V, &X3); fmul(F, &Y3, &r, &t); fmul(F, &t, &S1, &J); fadd(F, &t, &t, &t); fsub(F, &Y3, &Y3, &t);
    fadd(F, &t, &P->Z, &Q->Z); fsqr(F, &t, &t); fsub(F, &t, &t, &Z1Z1); fsub(F, &t, &t, &Z2Z2); fmul(F, &Z3, &t, &H);
    R->X = X3; R->Y = Y3; R->Z = Z3; R->inf = 0;
}
static void neg(const field *F, jac *R, const jac *P) { fe z = {{0}}; *R = *P; fsub(F, &R->Y, &z, &P->Y); }

#define W 5
static int wnaf(int8_t *d, const fe *k) {          /* k as plain integer (not Montgomery) */
    uint64_t v[5] = {k->v[0], k->v[1], k->v[2], k->v[3], 0};
    int len = 0;
    for (;;) {
        int nz = v[0] | v[1] | v[2] | v[3] | v[4];
        if (!nz) break;
        int digit = 0;
        if (v[0] & 1) {
            digit = (int)(v[0] & ((1 << W) - 1));
            if (digit >= (1 << (W - 1))) digit -= 1 << W;
            if (digit > 0) { uint64_t br = digit; for (int i = 0; i < 5 && br; i++) { uint64_t o = v[i]; v[i] -= br; br = v[i] > o; } }
            else { uint64_t c = -digit; for (int i = 0; i < 5 && c; i++) { v[i] += c; c = v[i] < c; } }
        }
        d[len++] = (int8_t)digit;
        for (int i = 0; i < 4; i++) v[i] = (v[i] >> 1) | (v[i + 1] << 63);
        v[4] >>= 1;
    }
    return len;
}
static void scalar_mul(const field *F, const fe *a, dblf dbl, jac *R, const fe *k, const jac *P) {
    jac T[1 << (W - 2)], P2;
    T[0] = *P; dbl(F, a, &P2, P);
    for (int i = 1; i < (1 << (W - 2)); i++) add(F, a, dbl, &T[i], &T[i - 1], &P2);
    int8_t d[300]; int len = wnaf(d, k);
    jac acc; acc.inf = 1;
    for (int i = len - 1; i >= 0; i--) {
        dbl(F, a, &acc, &acc);
        if (d[i] > 0) add(F, a, dbl, &acc, &acc, &T[d[i] >> 1]);
        else if (d[i] < 0) { jac m; neg(F, &m, &T[(-d[i]) >> 1]); add(F, a, dbl, &acc, &acc, &m); }
    }
    *R = acc;
}

typedef struct { int s; fe N[64], M[96], psi[32], uinv; } step;
static void hom(const field *F, fe *r, const fe *f, int deg, const fe *X, const fe *Zp) { /* Zp[k] = (Z^2)^k */
    fe acc = f[deg], t;
    for (int k = deg - 1; k >= 0; k--) { fmul(F, &acc, &acc, X); fmul(F, &t, &f[k], &Zp[deg - k]); fadd(F, &acc, &acc, &t); }
    *r = acc;
}
static void apply_step(const field *F, jac *R, const step *S, const jac *P) {
    fe Zp[100]; int s = S->s, top = 3 * s;
    Zp[0] = F->one; fsqr(F, &Zp[1], &P->Z);
    for (int k = 2; k <= top; k++) fmul(F, &Zp[k], &Zp[k - 1], &Zp[1]);
    fe Nh, Mh, Ph;
    hom(F, &Nh, S->N, 2 * s + 1, &P->X, Zp); hom(F, &Mh, S->M, 3 * s, &P->X, Zp); hom(F, &Ph, S->psi, s, &P->X, Zp);
    R->X = Nh; fmul(F, &R->Y, &P->Y, &Mh); fmul(F, &R->Z, &P->Z, &Ph); fmul(F, &R->Z, &R->Z, &S->uinv); R->inf = 0;
}
static void affine(const field *F, fe *x, fe *y, const jac *P) {
    fe zi, z2, z3; finv(F, &zi, &P->Z); fsqr(F, &z2, &zi); fmul(F, &z3, &z2, &zi);
    fmul(F, x, &P->X, &z2); fmul(F, y, &P->Y, &z3);
}

static char buf[1 << 16];
static void rd(fe *r) { if (scanf("%s", buf) != 1) exit(3); fe_from_hex(r, buf); }
static int rdi(void) { int v; if (scanf("%d", &v) != 1) exit(3); return v; }
static void rdm(const field *F, fe *r) { fe t; rd(&t); to_mont(F, r, &t); }
static void rd_step(const field *F, step *S) {
    S->s = rdi();
    for (int i = 0; i <= 2 * S->s + 1; i++) rdm(F, &S->N[i]);
    for (int i = 0; i <= 3 * S->s; i++) rdm(F, &S->M[i]);
    for (int i = 0; i <= S->s; i++) rdm(F, &S->psi[i]);
    rdm(F, &S->uinv);
}
static double now(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec * 1e9 + t.tv_nsec; }

int main(void) {
    field F, Fn;
    if (scanf("%s", buf) != 1) return 3; field_init(&F, buf);
    if (scanf("%s", buf) != 1) return 3; field_init(&Fn, buf);
    fe aE, aN, cadj; rdm(&F, &aE); rdm(&F, &aN); rd(&cadj);            /* cadj = c*R mod n (plain) */
    int nf = rdi(); step *fw = calloc(nf, sizeof(step)); for (int i = 0; i < nf; i++) rd_step(&F, &fw[i]);
    int nb = rdi(); step *bk = calloc(nb, sizeof(step)); for (int i = 0; i < nb; i++) rd_step(&F, &bk[i]);
    int K = rdi(), reps = rdi();
    jac *P = calloc(K, sizeof(jac)), *Pn = calloc(K, sizeof(jac)); fe *k = calloc(K, sizeof(fe)), *kn = calloc(K, sizeof(fe));
    for (int i = 0; i < K; i++) {
        rdm(&F, &P[i].X); rdm(&F, &P[i].Y); P[i].Z = F.one; P[i].inf = 0;
        rd(&k[i]);
        rdm(&F, &Pn[i].X); rdm(&F, &Pn[i].Y); Pn[i].Z = F.one; Pn[i].inf = 0;   /* base point already on E' */
        rd(&kn[i]);                                                          /* k' for the persistent arm */
    }
    fe *ox = calloc(4 * K, sizeof(fe)), *oy = calloc(4 * K, sizeof(fe));
    volatile uint64_t sink = 0;
    for (int rep = 0; rep < reps; rep++) {
        for (int a3 = 0; a3 < 4; a3++) {
            int arm = (rep + a3) % 4;                                        /* rotate arm order per repetition */
            double t0 = now();
            for (int i = 0; i < K; i++) {
                jac R; fe x, y;
                if (arm == 0 || arm == 3) { scalar_mul(&F, &aE, dbl_generic, &R, &k[i], &P[i]); }   /* arm 3: A/A repeat */
                else if (arm == 1) { scalar_mul(&F, &aN, dbl_am3, &R, &kn[i], &Pn[i]); }
                else {
                    jac Q = P[i];
                    for (int s = 0; s < nf; s++) apply_step(&F, &Q, &fw[s], &Q);
                    fe kk; fmul(&Fn, &kk, &k[i], &cadj);                   /* k' = k c mod n */
                    scalar_mul(&F, &aN, dbl_am3, &R, &kk, &Q);
                    for (int s = 0; s < nb; s++) apply_step(&F, &R, &bk[s], &R);
                }
                affine(&F, &x, &y, &R);
                sink ^= x.v[0];
                if (rep == 0) { ox[arm * K + i] = x; oy[arm * K + i] = y; }
            }
            double dt = now() - t0;
            printf("T %d %d %.1f\n", rep, arm, dt / K);
        }
    }
    char hx[80];
    for (int arm = 0; arm < 4; arm++) for (int i = 0; i < K; i++) {
        fe x, y; from_mont(&F, &x, &ox[arm * K + i]); from_mont(&F, &y, &oy[arm * K + i]);
        fe_to_hex(&x, hx); printf("R %d %d %s ", arm, i, hx); fe_to_hex(&y, hx); printf("%s\n", hx);
    }
    fprintf(stderr, "sink %llu\n", (unsigned long long)sink);
    return 0;
}
