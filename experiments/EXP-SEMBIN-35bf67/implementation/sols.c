/* EXP-SEMBIN-35bf67 exact solution count s (OP-S). Reads no rank output.
 *
 *   sols A|B n f_hex k t B_hex z_hex A_hex OUT
 *
 * Method A (S-A): enumeration over V (t=2) or V^2 (t=3) using S_3 as a quadratic:
 *   S_3(a, X, c) = (a+c)^2 X^2 + (a c) X + (a c)^2 + B.
 * Method B (S-B): point arithmetic on E: Y^2 + XY = X^3 + A X^2 + B over F_q or F_{q^2}:
 *   the X with S_3(a, X, c) = 0 are x(P_a + P_c), x(P_a - P_c) (P_a, P_c any lifts).
 * Output: count on line 1, then one solution per line as a hex Boolean assignment over
 * the variable order u1 (n bits, t=3 only), x1, x2, x3 (k bits each). Sorted.
 * The two methods share only the base-field multiplication/linear-map helpers.
 */
#include <immintrin.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef uint64_t u64;

static int n, k, t;
static u64 F, FR, NMASK, Bc, Ac, Z;

static inline u64 gmul(u64 a, u64 b) {
  __m128i p = _mm_clmulepi64_si128(_mm_cvtsi64_si128((long long)a), _mm_cvtsi64_si128((long long)b), 0);
  unsigned __int128 x = ((unsigned __int128)(u64)_mm_extract_epi64(p, 1) << 64) | (u64)_mm_cvtsi128_si64(p);
  for (;;) {
    unsigned __int128 hi = x >> n;
    if (!hi) break;
    x &= NMASK;
    /* x ^= hi * FR (carry-less), hi < 2^(n-1) fits 64 bits */
    __m128i q = _mm_clmulepi64_si128(_mm_cvtsi64_si128((long long)(u64)hi), _mm_cvtsi64_si128((long long)FR), 0);
    unsigned __int128 y = ((unsigned __int128)(u64)_mm_extract_epi64(q, 1) << 64) | (u64)_mm_cvtsi128_si64(q);
    x ^= y;
  }
  return (u64)x;
}
static inline u64 gsq(u64 a) { return gmul(a, a); }
static u64 gpow(u64 a, unsigned __int128 e) {
  u64 r = 1;
  while (e) { if (e & 1) r = gmul(r, a); a = gsq(a); e >>= 1; }
  return r;
}
static u64 ginv(u64 a) { return gpow(a, ((unsigned __int128)1 << n) - 2); }
static u64 gsqrt(u64 a) { return gpow(a, (unsigned __int128)1 << (n - 1)); }

/* linear maps via 8-bit tables */
static u64 TRMASK;
static u64 Ltab[8][256]; /* L(delta): solution of w^2 + w = delta + Tr(delta) tau */
static u64 TAU;
static inline int gtr(u64 a) { return __builtin_parityll(a & TRMASK); }
static inline u64 Lmap(u64 d) {
  u64 r = 0;
  for (int i = 0; i < 8 && d; i++, d >>= 8) r ^= Ltab[i][d & 0xff];
  return r;
}
static void init_maps(void) {
  TRMASK = 0;
  for (int j = 0; j < n; j++) {
    u64 a = (u64)1 << j, s = a, tr = a;
    for (int i = 1; i < n; i++) { s = gsq(s); tr ^= s; }
    if (tr > 1) { fprintf(stderr, "trace not in F2\n"); exit(3); }
    if (tr) TRMASK |= (u64)1 << j;
  }
  /* tau: any element of trace 1. The lowest basis element alpha^j with Tr = 1 is used
   * (a linear scan over integers is exponential when Tr vanishes on low powers of alpha,
   * as it does for sparse moduli; dev-log D18). */
  if (!TRMASK) { fprintf(stderr, "zero trace form\n"); exit(3); }
  TAU = (u64)1 << __builtin_ctzll(TRMASK);
  /* phi(w) = w^2 + w; solve phi(w) = e_j + Tr(e_j) tau by Gaussian elimination */
  u64 colv[64], comb[64];
  int npiv = 0;
  u64 bv[64], bc[64];
  int bp[64];
  for (int i = 0; i < n; i++) { colv[i] = gsq((u64)1 << i) ^ ((u64)1 << i); comb[i] = (u64)1 << i; }
  for (int i = 0; i < n; i++) {
    u64 v = colv[i], c = comb[i];
    for (int p = 0; p < npiv; p++) if ((v >> bp[p]) & 1) { v ^= bv[p]; c ^= bc[p]; }
    if (v) { bp[npiv] = 63 - __builtin_clzll(v); bv[npiv] = v; bc[npiv] = c; npiv++;
      /* keep reduced: eliminate new pivot from earlier rows */
      for (int p = 0; p < npiv - 1; p++) if ((bv[p] >> bp[npiv - 1]) & 1) { bv[p] ^= v; bc[p] ^= c; } }
  }
  u64 Lj[64];
  for (int j = 0; j < n; j++) {
    u64 d = ((u64)1 << j) ^ (gtr((u64)1 << j) ? TAU : 0), w = 0;
    for (int p = 0; p < npiv; p++) if ((d >> bp[p]) & 1) { d ^= bv[p]; w ^= bc[p]; }
    if (d) { fprintf(stderr, "AS solve failed\n"); exit(3); }
    Lj[j] = w;
  }
  for (int i = 0; i < 8; i++)
    for (int b = 0; b < 256; b++) {
      u64 r = 0;
      for (int j = 0; j < 8; j++) if ((b >> j) & 1 && 8 * i + j < n) r ^= Lj[8 * i + j];
      Ltab[i][b] = r;
    }
  /* self-check */
  for (u64 d = 1; d < 4096; d++) {
    u64 x = (d * 0x9E3779B97F4A7C15ULL) & NMASK;
    if (gtr(x)) continue;
    u64 w = Lmap(x);
    if ((gsq(w) ^ w) != x) { fprintf(stderr, "AS self-check failed\n"); exit(3); }
  }
}

/* ------------------------------------------------------------- method A (S_3 quadratic) */
/* roots X in F_q of S_3(a, X, c) = 0; returns count (0..2), roots in out[] */
static int s3_roots(u64 a, u64 c, u64 *out) {
  u64 c2 = gsq(a ^ c), c1 = gmul(a, c), c0 = gsq(c1) ^ Bc;
  if (!c2) {
    if (!c1) return 0;               /* a = c = 0 : B = 0 impossible */
    out[0] = gmul(c0, ginv(c1));     /* linear */
    return 1;
  }
  if (!c1) { out[0] = gsqrt(gmul(c0, ginv(c2))); return 1; }
  u64 inv = ginv(gmul(gsq(c1), c2));
  u64 delta = gmul(gmul(c0, gsq(c2)), inv);
  if (gtr(delta)) return 0;
  u64 y = Lmap(delta);
  u64 ratio = gmul(gmul(c1, gsq(c1)), inv); /* c1 / c2 */
  out[0] = gmul(ratio, y);
  out[1] = out[0] ^ ratio;
  return 2;
}

/* ------------------------------------------------------------- method B (group law) */
typedef struct { u64 u, v; } fq2; /* u + v w, w^2 = w + TAU */
static inline fq2 q2mul(fq2 a, fq2 b) {
  u64 uu = gmul(a.u, b.u), vv = gmul(a.v, b.v);
  fq2 r = { uu ^ gmul(vv, TAU), gmul(a.u, b.v) ^ gmul(a.v, b.u) ^ vv };
  return r;
}
static inline fq2 q2sq(fq2 a) { return q2mul(a, a); }
typedef struct { int inf; u64 x; fq2 y; } pt;
static pt lift(u64 x) {
  pt P = {0, x, {0, 0}};
  u64 rhs = gmul(gsq(x), x) ^ gmul(Ac, gsq(x)) ^ Bc;
  if (!x) { P.y.u = gsqrt(rhs); return P; }
  u64 d = gmul(rhs, ginv(gsq(x)));
  fq2 w;
  if (!gtr(d)) { w.u = Lmap(d); w.v = 0; }
  else { w.u = Lmap(d ^ TAU); w.v = 1; }      /* (w' + omega)^2 + (w' + omega) = d */
  fq2 xx = {x, 0};
  P.y = q2mul(xx, w);
  /* on-curve check over F_{q^2}: y^2 + x y = x^3 + A x^2 + B */
  fq2 lhs = q2sq(P.y);
  fq2 xy = q2mul(xx, P.y);
  lhs.u ^= xy.u; lhs.v ^= xy.v;
  if (lhs.u != rhs || lhs.v != 0) { fprintf(stderr, "lift not on curve\n"); exit(4); }
  return P;
}
static pt neg(pt P) { if (!P.inf) { P.y.u ^= P.x; } return P; }
/* x-coordinate of P + Q; returns 0 if infinity, else 1 with *xr (u + v w) */
static int add_x(pt P, pt Q, fq2 *xr) {
  if (P.inf) { xr->u = Q.x; xr->v = 0; return !Q.inf; }
  if (Q.inf) { xr->u = P.x; xr->v = 0; return 1; }
  fq2 lam;
  if (P.x == Q.x) {
    fq2 s = {P.y.u ^ Q.y.u, P.y.v ^ Q.y.v};
    if (s.u == P.x && s.v == 0) return 0;      /* Q = -P */
    /* Q = P : doubling, lambda = x + y / x  (x != 0 here since -P = P iff x = 0) */
    if (!P.x) return 0;
    u64 ix = ginv(P.x);
    lam.u = P.x ^ gmul(P.y.u, ix);
    lam.v = gmul(P.y.v, ix);
    fq2 l2 = q2sq(lam);
    xr->u = l2.u ^ lam.u ^ Ac;
    xr->v = l2.v ^ lam.v;
    return 1;
  }
  u64 ix = ginv(P.x ^ Q.x);
  lam.u = gmul(P.y.u ^ Q.y.u, ix);
  lam.v = gmul(P.y.v ^ Q.y.v, ix);
  fq2 l2 = q2sq(lam);
  xr->u = l2.u ^ lam.u ^ P.x ^ Q.x ^ Ac;
  xr->v = l2.v ^ lam.v;
  return 1;
}
/* X in F_q with S_3(a, X, c) = 0 via the group law; distinct values */
static int gl_roots(pt Pa, pt Pc, u64 *out) {
  fq2 x1 = {0, 0}, x2 = {0, 0};
  int h1 = add_x(Pa, Pc, &x1), h2 = add_x(Pa, neg(Pc), &x2);
  int m = 0;
  if (h1 && x1.v == 0) out[m++] = x1.u;
  if (h2 && x2.v == 0 && !(h1 && x1.v == 0 && x1.u == x2.u)) out[m++] = x2.u;
  return m;
}

/* ------------------------------------------------------------- main */
static u64 *SOL;
static long nsol, solcap;
static void addsol(u64 m) {
  if (nsol == solcap) { solcap = solcap ? 2 * solcap : 1024; SOL = (u64 *)realloc(SOL, sizeof(u64) * solcap); }
  SOL[nsol++] = m;
}
static int cmpu(const void *a, const void *b) { u64 x = *(const u64 *)a, y = *(const u64 *)b; return x < y ? -1 : x > y; }

int main(int argc, char **argv) {
  if (argc != 10) { fprintf(stderr, "usage: sols A|B n f k t B z A OUT\n"); return 2; }
  char meth = argv[1][0];
  n = atoi(argv[2]); F = strtoull(argv[3], 0, 16); k = atoi(argv[4]); t = atoi(argv[5]);
  Bc = strtoull(argv[6], 0, 16); Z = strtoull(argv[7], 0, 16); Ac = strtoull(argv[8], 0, 16);
  if (n < 2 || n > 62 || (F >> n) != 1 || (t != 2 && t != 3)) { fprintf(stderr, "bad params\n"); return 2; }
  NMASK = ((u64)1 << n) - 1;
  FR = F & NMASK;
  init_maps();
  u64 VK = (u64)1 << k;
  u64 r1[2], r2[2];
  if (meth == 'A') {
    if (t == 2) {
      for (u64 a = 0; a < VK; a++) {
        int m = s3_roots(a, Z, r1);
        for (int i = 0; i < m; i++) if (r1[i] < VK) addsol(a | (r1[i] << k));
      }
    } else {
      for (u64 a = 0; a < VK; a++)
        for (u64 b = 0; b < VK; b++) {
          int m = s3_roots(a, b, r1);           /* u with S_3(u, a, b) = 0 (symmetric) */
          for (int i = 0; i < m; i++) {
            int m2 = s3_roots(r1[i], Z, r2);    /* x3 with S_3(u, x3, z) = 0 */
            for (int j = 0; j < m2; j++)
              if (r2[j] < VK) addsol(r1[i] | (a << n) | (b << (n + k)) | (r2[j] << (n + 2 * k)));
          }
        }
    }
  } else if (meth == 'B') {
    pt Pz = lift(Z);
    pt *PV = (pt *)malloc(sizeof(pt) * VK);
    for (u64 a = 0; a < VK; a++) PV[a] = lift(a);
    if (t == 2) {
      for (u64 a = 0; a < VK; a++) {
        int m = gl_roots(PV[a], Pz, r1);
        for (int i = 0; i < m; i++) if (r1[i] < VK) addsol(a | (r1[i] << k));
      }
    } else {
      for (u64 a = 0; a < VK; a++)
        for (u64 b = 0; b < VK; b++) {
          int m = gl_roots(PV[a], PV[b], r1);   /* u = x(P_a +- P_b) in F_q */
          for (int i = 0; i < m; i++) {
            pt U = lift(r1[i]);
            int m2 = gl_roots(U, Pz, r2);
            for (int j = 0; j < m2; j++)
              if (r2[j] < VK) addsol(r1[i] | (a << n) | (b << (n + k)) | (r2[j] << (n + 2 * k)));
          }
        }
    }
  } else { fprintf(stderr, "method?\n"); return 2; }
  qsort(SOL, nsol, sizeof(u64), cmpu);
  FILE *o = fopen(argv[9], "w");
  fprintf(o, "# count=%ld method=%c\n", nsol, meth);
  for (long i = 0; i < nsol; i++) fprintf(o, "%llx\n", (unsigned long long)SOL[i]);
  fclose(o);
  printf("%ld\n", nsol);
  return 0;
}
