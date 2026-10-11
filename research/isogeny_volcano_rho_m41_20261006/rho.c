/* Pollard rho (van Oorschot-Wiener distinguished points, r-adding walk) on
 * ordinary binary curves  y^2 + xy = x^3 + a x^2 + b  over F_2^37.
 *
 * mode 0: equivalence classes {+-R}            (negation map only)
 * mode 1: equivalence classes {+-tau^i R}      (negation + Frobenius; only
 *         valid on a curve defined over F_2, i.e. the Koblitz curve)
 *
 * Cost accounting: every group operation (add or double) performed after the
 * instance Q is known is counted, including look-ahead retries, walk starts,
 * abandoned walks and the per-instance R_j setup. Precomputation that depends
 * only on the base point P (random multiples of P used for walk starts) is
 * not counted, and is identical for every curve.
 *
 * usage: rho run   <b> <a2> <mode> <nruns> <seed> <out.csv>
 *        rho bench <b> <a2> <mode> <steps> <reps> <seed>
 */
#include <immintrin.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include "params.h" /* M, RED, ELL, COF, LAMBDA0/1, QPOW, NORD: field and group for this study */
#define MASK ((1ULL << M) - 1)
static const uint64_t LAMBDA_ROOTS[2] = {LAMBDA0, LAMBDA1};

#define R_ADD 128
#define R_LOG 7
#define DP_BITS 5
#define MAX_WALK (100u << DP_BITS) /* safety cap only; cycles are escaped, not abandoned */
#define NSTART 4096

typedef uint64_t fe;
static fe A2, B;

static inline fe clmul(fe a, fe b) {
  __m128i r = _mm_clmulepi64_si128(_mm_cvtsi64_si128((long long)a),
                                   _mm_cvtsi64_si128((long long)b), 0);
  return (fe)_mm_cvtsi128_si64(r); /* inputs < 2^37 => product < 2^73; see fmul */
}
static inline fe fmul(fe a, fe b) {
  __m128i r = _mm_clmulepi64_si128(_mm_cvtsi64_si128((long long)a),
                                   _mm_cvtsi64_si128((long long)b), 0);
  uint64_t lo = (uint64_t)_mm_cvtsi128_si64(r);
  uint64_t hi = (uint64_t)_mm_extract_epi64(r, 1);
  uint64_t t = (lo >> M) | (hi << (64 - M)); /* bits >= 37, at most 36 bits */
  uint64_t p = (lo & MASK) ^ clmul(t, RED);  /* < 2^45 */
  t = p >> M;
  return (p & MASK) ^ clmul(t, RED);
}
static inline fe fsqr(fe a) { return fmul(a, a); }
static fe fsqrn(fe a, int n) { while (n--) a = fsqr(a); return a; }
static fe finv(fe a) { /* Itoh-Tsujii: a^(2^M-2) = (a^(2^(M-1)-1))^2, chain over the bits of M-1 */
  int k = 1, n = M - 1, top = 63 - __builtin_clzll((unsigned long long)n);
  fe b = a;
  for (int i = top - 1; i >= 0; i--) {
    b = fmul(fsqrn(b, k), b); k *= 2;
    if ((n >> i) & 1) { b = fmul(fsqr(b), a); k += 1; }
  }
  return fsqr(b);
}
static int ftrace(fe a) { fe t = a, s = a; for (int i = 1; i < M; i++) { s = fsqr(s); t ^= s; } return (int)(t & 1); }
static fe fhalftrace(fe a) { fe h = a, s = a; for (int i = 1; i <= (M - 1) / 2; i++) { s = fsqr(fsqr(s)); h ^= s; } return h; }

typedef struct { fe x, y; int inf; } pt;
static uint64_t ops; /* group operation counter */

static pt padd(pt P, pt Q);
static pt pdbl(pt P) {
  ops++;
  if (P.inf || P.x == 0) return (pt){0, 0, 1};
  fe l = P.x ^ fmul(P.y, finv(P.x));
  fe x3 = fsqr(l) ^ l ^ A2;
  fe y3 = fsqr(P.x) ^ fmul(l ^ 1, x3);
  return (pt){x3, y3, 0};
}
static pt padd(pt P, pt Q) {
  if (P.inf) return Q;
  if (Q.inf) return P;
  if (P.x == Q.x) { if (P.y == Q.y) return pdbl(P); ops++; return (pt){0, 0, 1}; }
  ops++;
  fe l = fmul(P.y ^ Q.y, finv(P.x ^ Q.x));
  fe x3 = fsqr(l) ^ l ^ P.x ^ Q.x ^ A2;
  fe y3 = fmul(l, P.x ^ x3) ^ x3 ^ P.y;
  return (pt){x3, y3, 0};
}
static pt pmul(pt P, uint64_t k) {
  pt R = {0, 0, 1};
  for (int i = 63; i >= 0; i--) { R = pdbl(R); if ((k >> i) & 1) R = padd(R, P); }
  return R;
}
static int on_curve(pt P) {
  if (P.inf) return 1;
  fe x2 = fsqr(P.x);
  return (fsqr(P.y) ^ fmul(P.x, P.y)) == (fmul(x2, P.x) ^ fmul(A2, x2) ^ B);
}

/* xorshift-style PRNG (splitmix64) */
static uint64_t rs;
static uint64_t rnd(void) { uint64_t z = (rs += 0x9E3779B97F4A7C15ULL); z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL; z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL; return z ^ (z >> 31); }
static uint64_t rmod(uint64_t n) { return rnd() % n; }

static uint64_t mulmod(uint64_t a, uint64_t b) { return (uint64_t)((unsigned __int128)a * b % ELL); }
static uint64_t powmod(uint64_t a, uint64_t e) { uint64_t r = 1; while (e) { if (e & 1) r = mulmod(r, a); a = mulmod(a, a); e >>= 1; } return r; }
static uint64_t invmod(uint64_t a) { return powmod(a, ELL - 2); }

static pt random_subgroup_point(void) {
  for (;;) {
    fe x = rnd() & MASK;
    if (!x) continue;
    fe c = x ^ A2 ^ fmul(B, finv(fsqr(x)));
    if (ftrace(c)) continue;
    fe z = fhalftrace(c);
    pt P = {x, fmul(x, z), 0};
    if (!on_curve(P)) { fprintf(stderr, "half-trace bug\n"); exit(2); }
    P = pmul(P, COF);
    if (!P.inf) return P;
  }
}

static int mode;
static uint64_t lam_pow[M]; /* lambda^i mod ELL */

/* canonical class representative; scales coefficient multiplier into *mult */
static inline pt canon(pt P, uint64_t *mult) {
  uint64_t mu = 1;
  if (mode == 1) {
    fe best = P.x, xi = P.x; int bi = 0;
    for (int i = 1; i < M; i++) { xi = fsqr(xi); if (xi < best) { best = xi; bi = i; } }
    if (bi) { P.x = best; P.y = fsqrn(P.y, bi); mu = lam_pow[bi]; }
  }
  fe ny = P.y ^ P.x;
  if (ny < P.y) { P.y = ny; mu = mu ? ELL - mu : 0; }
  *mult = mu;
  return P;
}
static inline unsigned hidx(fe x) { return (unsigned)((x * 0x9E3779B97F4A7C15ULL) >> (64 - R_LOG)); }
static inline int is_dp(fe x) { return ((x * 0xD6E8FEB86659FD93ULL) >> (64 - DP_BITS)) == 0; }

/* DP table */
#define TB (1u << 18)
typedef struct { fe x, y; uint64_t a, b; uint32_t gen; } ent;
static ent *tab;
static uint32_t gen;

static pt Pgen, Ust[NSTART];
static uint64_t Ucoef[NSTART];

static void setup_curve(uint64_t seed) {
  rs = seed;
  Pgen = random_subgroup_point();
  if (!pmul(Pgen, ELL).inf) { fprintf(stderr, "order check failed\n"); exit(2); }
  lam_pow[0] = 1;
  if (mode == 1) {
    pt T = {fsqr(Pgen.x), fsqr(Pgen.y), 0}; uint64_t lam = 0;
    for (int k = 0; k < 2; k++) { pt S = pmul(Pgen, LAMBDA_ROOTS[k]); if (S.x == T.x && S.y == T.y) lam = LAMBDA_ROOTS[k]; }
    if (!lam) { fprintf(stderr, "tau eigenvalue not found (curve not Koblitz?)\n"); exit(2); }
    for (int i = 1; i < M; i++) lam_pow[i] = mulmod(lam_pow[i - 1], lam);
  }
  for (int i = 0; i < NSTART; i++) { Ucoef[i] = 1 + rmod(ELL - 1); Ust[i] = pmul(Pgen, Ucoef[i]); }
}

typedef struct { uint64_t ops, walks, cycles, abandoned, useless; int ok; double sec; } result;

static pt R[R_ADD]; static uint64_t Ra[R_ADD], Rb[R_ADD];
static pt Q2[64]; /* Q2[s] = 2^s Q, built per instance with counted doublings */


/* one deterministic walk step with BKL look-ahead; returns 0 on point at infinity */
static inline int step(pt *S, uint64_t *a, uint64_t *b) {
  unsigned j = hidx(S->x), tries = 0, jj;
  pt T; uint64_t ta = 0, tb = 0, tm = 1;
  do { /* reject T whose partition equals the index just used (fruitless 2-cycles) */
    jj = (j + tries) % R_ADD;
    T = padd(*S, R[jj]);
    if (T.inf) return 0;
    ta = (*a + Ra[jj]) % ELL; tb = (*b + Rb[jj]) % ELL;
    T = canon(T, &tm);
    tries++;
  } while (hidx(T.x) == jj && tries < 4);
  *S = T; *a = mulmod(ta, tm); *b = mulmod(tb, tm);
  return 1;
}

static result solve_one(void) {
  result res = {0};
  struct timespec t0, t1;
  uint64_t k = 1 + rmod(ELL - 1);
  pt Q = pmul(Pgen, k); /* instance generation: not counted */
  clock_gettime(CLOCK_MONOTONIC, &t0);
  ops = 0;
  Q2[0] = Q; for (int s = 1; s < QPOW; s++) Q2[s] = pdbl(Q2[s - 1]);
  for (int j = 0; j < R_ADD; j++) { /* R_j = c_j P + 2^s_j Q */
    int u = (int)rmod(NSTART), q = (int)rmod(QPOW);
    Ra[j] = Ucoef[u]; Rb[j] = 1ULL << q; R[j] = padd(Ust[u], Q2[q]);
  }
  gen++;
  for (;;) {
    int u = (int)rmod(NSTART), v = (int)rmod(NSTART), q = (int)rmod(QPOW);
    pt S = padd(padd(Ust[u], Ust[v]), Q2[q]); uint64_t a = (Ucoef[u] + Ucoef[v]) % ELL, b = 1ULL << q, mu;
    if (S.inf) continue;
    S = canon(S, &mu); a = mulmod(a, mu); b = mulmod(b, mu);
    res.walks++;
    unsigned len = 0; int restart = 0; fe mark = S.x;
    while (!is_dp(S.x)) {
      if (++len > MAX_WALK) { res.abandoned++; restart = 1; break; }
      if (!step(&S, &a, &b)) { restart = 1; break; }
      if (S.x == mark) { /* fruitless cycle: walk it once more, escape by doubling its minimum */
        pt mn = S; uint64_t ma = a, mb = b;
        do { if (!step(&S, &a, &b)) break; if (S.x < mn.x) { mn = S; ma = a; mb = b; } } while (S.x != mark);
        S = canon(pdbl(mn), &mu); a = mulmod(2 * ma % ELL, mu); b = mulmod(2 * mb % ELL, mu);
        res.cycles++;
      }
      if ((len & (len - 1)) == 0) mark = S.x; /* Brent-style checkpoints at len = 1,2,4,8,... */
    }
    if (restart) continue;
    unsigned h = (unsigned)((S.x * 0x9E3779B97F4A7C15ULL) >> 48) & (TB - 1);
    for (;; h = (h + 1) & (TB - 1)) {
      ent *e = &tab[h];
      if (e->gen != gen) { *e = (ent){S.x, S.y, a, b, gen}; break; }
      if (e->x == S.x) {
        if (e->y != S.y) { fprintf(stderr, "canonicalisation bug\n"); exit(2); }
        if (e->b == b) { res.useless++; break; }
        uint64_t kk = mulmod((e->a + ELL - a) % ELL, invmod((b + ELL - e->b) % ELL));
        clock_gettime(CLOCK_MONOTONIC, &t1);
        res.ops = ops;
        res.sec = (t1.tv_sec - t0.tv_sec) + 1e-9 * (t1.tv_nsec - t0.tv_nsec);
        pt C = pmul(Pgen, kk); /* independent certificate check, not timed */
        res.ok = (kk == k) && C.x == Q.x && C.y == Q.y;
        return res;
      }
    }
  }
}

int main(int argc, char **argv) {
  if (argc < 7) { fprintf(stderr, "see header\n"); return 1; }
  B = strtoull(argv[2], 0, 10); A2 = strtoull(argv[3], 0, 10); mode = atoi(argv[4]);
  uint64_t n = strtoull(argv[5], 0, 10), seed = strtoull(argv[6], 0, 10);
  setup_curve(seed);
  if (!strcmp(argv[1], "run")) {
    tab = calloc(TB, sizeof(ent));
    FILE *f = fopen(argv[7], "w");
    fprintf(f, "run,ops,walks,cycles,abandoned,useless,ok,sec\n");
    for (uint64_t i = 0; i < n; i++) {
      result r = solve_one();
      fprintf(f, "%llu,%llu,%llu,%llu,%llu,%llu,%d,%.9f\n", (unsigned long long)i, (unsigned long long)r.ops,
              (unsigned long long)r.walks, (unsigned long long)r.cycles, (unsigned long long)r.abandoned, (unsigned long long)r.useless, r.ok, r.sec);
    }
    fclose(f);
  } else { /* bench: ns per walk step (add + canonicalise), no DP handling */
    uint64_t reps = strtoull(argv[7], 0, 10);
    for (int j = 0; j < R_ADD; j++) R[j] = Ust[j];
    for (uint64_t r = 0; r < reps; r++) {
      pt S = Ust[100 + r % 1000]; uint64_t mu; struct timespec t0, t1;
      clock_gettime(CLOCK_MONOTONIC, &t0);
      for (uint64_t i = 0; i < n; i++) { S = canon(padd(S, R[hidx(S.x)]), &mu); if (S.inf) S = Ust[r % 1000]; }
      clock_gettime(CLOCK_MONOTONIC, &t1);
      printf("%.4f %llu\n", ((t1.tv_sec - t0.tv_sec) * 1e9 + (t1.tv_nsec - t0.tv_nsec)) / n, (unsigned long long)(S.x & 1));
    }
  }
  return 0;
}
