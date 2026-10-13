/* Pollard rho (van Oorschot--Wiener distinguished points, r-adding walk)
 * for the m=51 ordinary binary isogeny class
 *
 *     y^2 + xy = x^3 + a2*x^2 + b
 *
 * over F_2^51 = F_2[x]/(x^51 + x^6 + x^3 + x + 1).
 *
 * Modes:
 *   0  signed negation classes {+-R}; valid on every nonsingular input curve.
 *   1  signed 2-Frobenius classes {+-tau^i R}, i in [0, 50]; accepted only
 *      for the exact Koblitz crater (a2=0, b=1).
 *   2  signed 2^17-Frobenius classes {+-tau17^i R}, i in [0, 2]; accepted
 *      only when both input coefficients are fixed by 2^17-Frobenius.
 *
 * The executable fails closed unless it certifies the declared action on the
 * generated subgroup basis, the action's exact order, and the fast
 * canonicalizer against a slow orbit enumeration on deterministic multiples.
 * These checks are startup validation, not experimental observations.
 *
 * RNG domains are deliberately separate.  setup_seed alone determines Pgen,
 * Ucoef and Ust.  target_seed and target_index alone determine the planted
 * logarithm.  walk_seed and target_index alone determine that target's walk
 * stream.  Thus, for a fixed curve, two arms can request the same explicit
 * target indices and seeds without setup or a preceding target perturbing
 * their streams.
 *
 * Counted online work begins after Q=kP has been planted.  It includes Q's
 * doubling table, the target-dependent r-add table, walk starts, retries,
 * cycle escapes and abandoned walks.  P-only setup, startup certificates,
 * target construction, scalar recovery and the final planted-log check are
 * excluded.  The CSV splits target-dependent table setup from subsequent walk
 * group operations and reports canonicalization primitives separately.
 *
 * Usage:
 *   rho selftest <b> <a2> <mode> <setup_seed>
 *   rho run <b> <a2> <mode> <nruns> <setup_seed> <target_seed> <walk_seed>
 *           <target_start> <out.csv>
 */
#define _POSIX_C_SOURCE 200809L

#include <errno.h>
#include <fcntl.h>
#include <immintrin.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#include "params.h"

#define MASK ((1ULL << M) - 1ULL)
#define R_ADD 128
#define R_LOG 7
#define DP_BITS 5
#define MAX_WALK (100u << DP_BITS)
#define NSTART 4096
#define TB_LOG 18
#define TB (1u << TB_LOG)

_Static_assert(M > 1 && M < 64, "field degree must fit the 64-bit backend");
_Static_assert(QPOW > 0 && QPOW < 64, "QPOW must be a valid shift");
_Static_assert(R_ADD == (1u << R_LOG), "R_ADD and R_LOG disagree");

typedef uint64_t fe;
typedef struct {
  fe x, y;
  int inf;
} pt;
typedef struct {
  uint64_t state;
} rng64;

static fe A2, B;
static int mode;
static unsigned action_step;
static unsigned action_order;
static uint64_t action_lambda;
static uint64_t lambda_pow[M];

typedef struct {
  uint64_t adds;
  uint64_t doubles;
  uint64_t canon_calls;
  uint64_t canon_x_squares;
  uint64_t canon_y_squares;
  uint64_t canon_sign_tests;
  uint64_t canon_negations;
} counters;

static counters ctr;
static int counting;

static inline fe clmul_low(fe a, fe b) {
  __m128i r = _mm_clmulepi64_si128(_mm_cvtsi64_si128((long long)a),
                                   _mm_cvtsi64_si128((long long)b), 0);
  return (fe)_mm_cvtsi128_si64(r);
}

static inline fe fmul(fe a, fe b) {
  __m128i r = _mm_clmulepi64_si128(_mm_cvtsi64_si128((long long)a),
                                   _mm_cvtsi64_si128((long long)b), 0);
  uint64_t lo = (uint64_t)_mm_cvtsi128_si64(r);
  uint64_t hi = (uint64_t)_mm_extract_epi64(r, 1);
  uint64_t t = (lo >> M) | (hi << (64 - M));
  uint64_t p = (lo & MASK) ^ clmul_low(t, RED);
  t = p >> M;
  return (p & MASK) ^ clmul_low(t, RED);
}

static inline fe fsqr(fe a) { return fmul(a, a); }

static fe fsqrn(fe a, unsigned n) {
  while (n-- != 0) a = fsqr(a);
  return a;
}

static fe fsqrn_canon(fe a, unsigned n, uint64_t *which) {
  while (n-- != 0) {
    a = fsqr(a);
    if (counting) (*which)++;
  }
  return a;
}

static fe finv(fe a) {
  int k = 1;
  int n = M - 1;
  int top = 63 - __builtin_clzll((unsigned long long)n);
  fe b = a;
  for (int i = top - 1; i >= 0; i--) {
    b = fmul(fsqrn(b, (unsigned)k), b);
    k *= 2;
    if ((n >> i) & 1) {
      b = fmul(fsqr(b), a);
      k++;
    }
  }
  return fsqr(b);
}

static int ftrace(fe a) {
  fe t = a, s = a;
  for (int i = 1; i < M; i++) {
    s = fsqr(s);
    t ^= s;
  }
  return (int)(t & 1ULL);
}

static fe fhalftrace(fe a) {
  fe h = a, s = a;
  for (int i = 1; i <= (M - 1) / 2; i++) {
    s = fsqr(fsqr(s));
    h ^= s;
  }
  return h;
}

static int pt_equal(pt P, pt Q) {
  if (P.inf || Q.inf) return P.inf && Q.inf;
  return P.x == Q.x && P.y == Q.y;
}

static pt pneg(pt P) {
  if (!P.inf) P.y ^= P.x;
  return P;
}

static pt pdbl(pt P) {
  if (counting) ctr.doubles++;
  if (P.inf || P.x == 0) return (pt){0, 0, 1};
  fe l = P.x ^ fmul(P.y, finv(P.x));
  fe x3 = fsqr(l) ^ l ^ A2;
  fe y3 = fsqr(P.x) ^ fmul(l ^ 1ULL, x3);
  return (pt){x3, y3, 0};
}

static pt padd(pt P, pt Q) {
  if (P.inf) return Q;
  if (Q.inf) return P;
  if (P.x == Q.x) {
    if (P.y == Q.y) return pdbl(P);
    if (counting) ctr.adds++;
    return (pt){0, 0, 1};
  }
  if (counting) ctr.adds++;
  fe l = fmul(P.y ^ Q.y, finv(P.x ^ Q.x));
  fe x3 = fsqr(l) ^ l ^ P.x ^ Q.x ^ A2;
  fe y3 = fmul(l, P.x ^ x3) ^ x3 ^ P.y;
  return (pt){x3, y3, 0};
}

static pt pmul(pt P, uint64_t k) {
  pt R = {0, 0, 1};
  for (int i = 63; i >= 0; i--) {
    R = pdbl(R);
    if ((k >> i) & 1ULL) R = padd(R, P);
  }
  return R;
}

static int on_curve(pt P) {
  if (P.inf) return 1;
  fe x2 = fsqr(P.x);
  return (fsqr(P.y) ^ fmul(P.x, P.y)) ==
         (fmul(x2, P.x) ^ fmul(A2, x2) ^ B);
}

static pt frob(pt P, unsigned n) {
  if (!P.inf) {
    P.x = fsqrn(P.x, n);
    P.y = fsqrn(P.y, n);
  }
  return P;
}

static uint64_t mix64(uint64_t z) {
  z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
  z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
  return z ^ (z >> 31);
}

static uint64_t rng_next(rng64 *r) {
  r->state += 0x9E3779B97F4A7C15ULL;
  return mix64(r->state);
}

static uint64_t rng_bounded(rng64 *r, uint64_t n) {
  uint64_t threshold;
  if (n == 0) {
    fprintf(stderr, "internal error: zero RNG bound\n");
    exit(2);
  }
  threshold = (uint64_t)(-n) % n;
  for (;;) {
    uint64_t x = rng_next(r);
    if (x >= threshold) return x % n;
  }
}

static uint64_t indexed_word(uint64_t seed, uint64_t index,
                             uint64_t domain, uint64_t attempt) {
  return mix64(seed ^ domain ^ mix64(index + 0x9E3779B97F4A7C15ULL) ^
               mix64(attempt + 0xD1B54A32D192ED03ULL));
}

static uint64_t indexed_bounded(uint64_t seed, uint64_t index,
                                uint64_t domain, uint64_t n) {
  uint64_t threshold = (uint64_t)(-n) % n;
  for (uint64_t attempt = 0;; attempt++) {
    uint64_t x = indexed_word(seed, index, domain, attempt);
    if (x >= threshold) return x % n;
  }
}

static uint64_t target_scalar(uint64_t seed, uint64_t index) {
  return 1ULL + indexed_bounded(seed, index, 0x5441524745544B31ULL,
                                ELL - 1ULL);
}

static uint64_t target_walk_stream(uint64_t seed, uint64_t index) {
  return indexed_word(seed, index, 0x57414C4B53545231ULL, 0);
}

static uint64_t mulmod(uint64_t a, uint64_t b) {
  return (uint64_t)((unsigned __int128)a * b % ELL);
}

static uint64_t powmod(uint64_t a, uint64_t e) {
  uint64_t r = 1;
  while (e != 0) {
    if (e & 1ULL) r = mulmod(r, a);
    a = mulmod(a, a);
    e >>= 1;
  }
  return r;
}

static uint64_t invmod(uint64_t a) { return powmod(a, ELL - 2ULL); }

static void monotonic_now(struct timespec *t) {
  if (clock_gettime(CLOCK_MONOTONIC, t) != 0) {
    fprintf(stderr, "clock_gettime(CLOCK_MONOTONIC) failed: %s\n",
            strerror(errno));
    exit(2);
  }
}

static pt random_subgroup_point(rng64 *rng) {
  for (;;) {
    fe x = rng_next(rng) & MASK;
    if (x == 0) continue;
    fe c = x ^ A2 ^ fmul(B, finv(fsqr(x)));
    if (ftrace(c)) continue;
    fe z = fhalftrace(c);
    pt P = {x, fmul(x, z), 0};
    if (!on_curve(P)) {
      fprintf(stderr, "half-trace point construction failed\n");
      exit(2);
    }
    P = pmul(P, COF);
    if (!P.inf) return P;
  }
}

static int point_less(pt P, pt Q) {
  if (P.inf != Q.inf) return !P.inf;
  if (P.inf) return 0;
  if (P.x != Q.x) return P.x < Q.x;
  return P.y < Q.y;
}

/* Fast representative; *mult satisfies returned_point = [*mult]P. */
static inline pt canon(pt P, uint64_t *mult) {
  uint64_t mu = 1;
  if (counting) ctr.canon_calls++;
  if (P.inf) {
    *mult = mu;
    return P;
  }
  if (action_order > 1) {
    fe best = P.x;
    fe xi = P.x;
    unsigned best_i = 0;
    for (unsigned i = 1; i < action_order; i++) {
      xi = fsqrn_canon(xi, action_step, &ctr.canon_x_squares);
      if (xi < best) {
        best = xi;
        best_i = i;
      }
    }
    if (best_i != 0) {
      P.x = best;
      P.y = fsqrn_canon(P.y, action_step * best_i,
                        &ctr.canon_y_squares);
      mu = lambda_pow[best_i];
    }
  }
  if (counting) ctr.canon_sign_tests++;
  fe ny = P.y ^ P.x;
  if (ny < P.y) {
    P.y = ny;
    mu = ELL - mu;
    if (counting) ctr.canon_negations++;
  }
  *mult = mu;
  return P;
}

/* Deliberately direct reference implementation used only by startup checks. */
static pt canon_slow(pt P, uint64_t *mult) {
  pt best = P;
  uint64_t best_mu = 1;
  pt cur = P;
  uint64_t mu = 1;
  for (unsigned i = 0; i < action_order; i++) {
    pt neg = pneg(cur);
    uint64_t neg_mu = ELL - mu;
    if (point_less(cur, best)) {
      best = cur;
      best_mu = mu;
    }
    if (point_less(neg, best)) {
      best = neg;
      best_mu = neg_mu;
    }
    cur = frob(cur, action_step);
    mu = mulmod(mu, action_lambda);
  }
  *mult = best_mu;
  return best;
}

static inline unsigned hidx(fe x) {
  return (unsigned)((x * 0x9E3779B97F4A7C15ULL) >> (64 - R_LOG));
}

static inline int is_dp(fe x) {
  return ((x * 0xD6E8FEB86659FD93ULL) >> (64 - DP_BITS)) == 0;
}

typedef struct {
  fe x, y;
  uint64_t a, b;
  uint32_t gen;
} ent;

static ent *tab;
static uint32_t gen;
static pt Pgen, Ust[NSTART];
static uint64_t Ucoef[NSTART];
static uint64_t setup_fingerprint;
static pt R[R_ADD];
static uint64_t Ra[R_ADD], Rb[R_ADD];
static pt Q2[64];

static int coefficient_fixed(fe a, unsigned step) {
  return fsqrn(a, step) == a;
}

static int configure_mode(void) {
  switch (mode) {
    case 0:
      action_step = 0;
      action_order = 1;
      action_lambda = 1;
      break;
    case 1:
      if (A2 != 0 || B != 1) {
        fprintf(stderr,
                "mode 1 is restricted to the exact crater a2=0,b=1\n");
        return 0;
      }
      action_step = 1;
      action_order = 51;
      action_lambda = LAMBDA_TAU;
      break;
    case 2:
      action_step = 17;
      action_order = 3;
      action_lambda = LAMBDA_TAU17;
      break;
    default:
      fprintf(stderr, "invalid mode %d (expected 0, 1, or 2)\n", mode);
      return 0;
  }
  if (B == 0) {
    fprintf(stderr, "singular binary curve: b must be nonzero\n");
    return 0;
  }
  if (action_step != 0 &&
      (!coefficient_fixed(A2, action_step) ||
       !coefficient_fixed(B, action_step))) {
    fprintf(stderr,
            "mode %d rejected: coefficients are not fixed by Frobenius^%u\n",
            mode, action_step);
    return 0;
  }
  lambda_pow[0] = 1;
  for (unsigned i = 1; i < action_order; i++)
    lambda_pow[i] = mulmod(lambda_pow[i - 1], action_lambda);
  return 1;
}

static int certify_exact_action_order(void) {
  static const unsigned factors51[] = {3, 17};
  static const unsigned factors3[] = {3};
  const unsigned *factors = NULL;
  size_t nfactors = 0;
  if (action_order == 51) {
    factors = factors51;
    nfactors = sizeof(factors51) / sizeof(factors51[0]);
  } else if (action_order == 3) {
    factors = factors3;
    nfactors = sizeof(factors3) / sizeof(factors3[0]);
  }
  if (powmod(action_lambda, action_order) != 1) {
    fprintf(stderr, "declared action eigenvalue does not have dividing order\n");
    return 0;
  }
  pt full = frob(Pgen, action_step * action_order);
  if (!pt_equal(full, Pgen)) {
    fprintf(stderr, "declared geometric action does not close at its order\n");
    return 0;
  }
  for (size_t i = 0; i < nfactors; i++) {
    unsigned proper = action_order / factors[i];
    if (powmod(action_lambda, proper) == 1) {
      fprintf(stderr,
              "declared eigenvalue order is not exact (prime factor %u)\n",
              factors[i]);
      return 0;
    }
    if (pt_equal(frob(Pgen, action_step * proper), Pgen)) {
      fprintf(stderr,
              "geometric action order is not exact (prime factor %u)\n",
              factors[i]);
      return 0;
    }
  }
  return 1;
}

static int certify_canonicalizer(void) {
  static const uint64_t scalars[] = {
      1, 2, 3, 5, 17, 257, 65537, ELL - 1ULL,
  };
  for (size_t i = 0; i < sizeof(scalars) / sizeof(scalars[0]); i++) {
    pt P = pmul(Pgen, scalars[i]);
    uint64_t fast_mu, slow_mu, again_mu;
    pt fast = canon(P, &fast_mu);
    pt slow = canon_slow(P, &slow_mu);
    pt image = pmul(P, fast_mu);
    pt again = canon(fast, &again_mu);
    if (!pt_equal(fast, slow) || fast_mu != slow_mu) {
      fprintf(stderr,
              "canonicalizer disagrees with slow orbit at test %zu\n", i);
      return 0;
    }
    if (!pt_equal(image, fast)) {
      fprintf(stderr,
              "canonicalizer multiplier certificate failed at test %zu\n", i);
      return 0;
    }
    if (!pt_equal(again, fast) || again_mu != 1) {
      fprintf(stderr,
              "canonicalizer idempotence failed at test %zu\n", i);
      return 0;
    }
  }
  return 1;
}

/* Reproducibility checksum, not a cryptographic commitment. */
static uint64_t fingerprint_setup(void) {
  uint64_t h = mix64(0x4D35315345545550ULL ^ Pgen.x);
  h = mix64(h ^ Pgen.y);
  for (uint64_t i = 0; i < NSTART; i++) {
    h = mix64(h ^ mix64(Ucoef[i] ^ i));
    h = mix64(h ^ mix64(Ust[i].x ^ (i << 1)));
    h = mix64(h ^ mix64(Ust[i].y ^ (i << 2)));
  }
  return h;
}

static int setup_curve(uint64_t setup_seed) {
  rng64 setup_rng = {setup_seed};
  counting = 0;
  memset(&ctr, 0, sizeof(ctr));
  if ((unsigned __int128)ELL * COF != NORD) {
    fprintf(stderr, "parameter certificate failed: ELL*COF != NORD\n");
    return 0;
  }
  if (QPOW == 0 || QPOW >= 64 ||
      (1ULL << (QPOW - 1)) >= ELL || (1ULL << QPOW) < ELL) {
    fprintf(stderr, "parameter certificate failed: QPOW is not bit length\n");
    return 0;
  }
  if (!configure_mode()) return 0;
  Pgen = random_subgroup_point(&setup_rng);
  if (Pgen.inf || !on_curve(Pgen) || !pmul(Pgen, ELL).inf) {
    fprintf(stderr, "generated subgroup basis failed order certificate\n");
    return 0;
  }
  if (action_order > 1) {
    pt geometric = frob(Pgen, action_step);
    pt scalar = pmul(Pgen, action_lambda);
    if (!pt_equal(geometric, scalar)) {
      fprintf(stderr, "declared action eigenvalue fails on Pgen\n");
      return 0;
    }
  }
  if (!certify_exact_action_order() || !certify_canonicalizer()) return 0;
  for (int i = 0; i < NSTART; i++) {
    Ucoef[i] = 1ULL + rng_bounded(&setup_rng, ELL - 1ULL);
    Ust[i] = pmul(Pgen, Ucoef[i]);
  }
  setup_fingerprint = fingerprint_setup();
  memset(&ctr, 0, sizeof(ctr));
  return 1;
}

typedef struct {
  uint64_t target_index;
  uint64_t target_scalar;
  uint64_t walk_stream_seed;
  uint64_t ops, adds, doubles;
  uint64_t setup_ops, setup_adds, setup_doubles;
  uint64_t walk_ops, walk_adds, walk_doubles;
  uint64_t canon_calls, canon_x_squares, canon_y_squares;
  uint64_t canon_sign_tests, canon_negations;
  uint64_t walks, cycles, abandoned, useless;
  int ok;
  double sec;
} result;

/* One deterministic walk step with BKL look-ahead. */
static inline int step(pt *S, uint64_t *a, uint64_t *b) {
  unsigned j = hidx(S->x), tries = 0, jj;
  pt T;
  uint64_t ta = 0, tb = 0, tm = 1;
  do {
    jj = (j + tries) % R_ADD;
    T = padd(*S, R[jj]);
    if (T.inf) return 0;
    ta = (*a + Ra[jj]) % ELL;
    tb = (*b + Rb[jj]) % ELL;
    T = canon(T, &tm);
    tries++;
  } while (hidx(T.x) == jj && tries < 4);
  *S = T;
  *a = mulmod(ta, tm);
  *b = mulmod(tb, tm);
  return 1;
}

static result solve_one(uint64_t target_seed, uint64_t walk_seed,
                        uint64_t target_index) {
  result res = {0};
  struct timespec t0, t1;
  uint64_t k = target_scalar(target_seed, target_index);
  uint64_t stream_seed = target_walk_stream(walk_seed, target_index);
  rng64 walk_rng = {stream_seed};
  pt Q = pmul(Pgen, k);

  res.target_index = target_index;
  res.target_scalar = k;
  res.walk_stream_seed = stream_seed;
  memset(&ctr, 0, sizeof(ctr));
  counting = 1;
  monotonic_now(&t0);

  Q2[0] = Q;
  for (int s = 1; s < QPOW; s++) Q2[s] = pdbl(Q2[s - 1]);
  for (int j = 0; j < R_ADD; j++) {
    int u = (int)rng_bounded(&walk_rng, NSTART);
    int q = (int)rng_bounded(&walk_rng, QPOW);
    Ra[j] = Ucoef[u];
    Rb[j] = 1ULL << q;
    R[j] = padd(Ust[u], Q2[q]);
  }
  res.setup_adds = ctr.adds;
  res.setup_doubles = ctr.doubles;
  res.setup_ops = ctr.adds + ctr.doubles;

  gen++;
  if (gen == 0) {
    memset(tab, 0, TB * sizeof(*tab));
    gen = 1;
  }
  for (;;) {
    int u = (int)rng_bounded(&walk_rng, NSTART);
    int v = (int)rng_bounded(&walk_rng, NSTART);
    int q = (int)rng_bounded(&walk_rng, QPOW);
    pt S = padd(padd(Ust[u], Ust[v]), Q2[q]);
    uint64_t a = (Ucoef[u] + Ucoef[v]) % ELL;
    uint64_t b = 1ULL << q;
    uint64_t mu;
    if (S.inf) continue;
    S = canon(S, &mu);
    a = mulmod(a, mu);
    b = mulmod(b, mu);
    res.walks++;
    unsigned len = 0;
    int restart = 0;
    fe mark = S.x;
    while (!is_dp(S.x)) {
      if (++len > MAX_WALK) {
        res.abandoned++;
        restart = 1;
        break;
      }
      if (!step(&S, &a, &b)) {
        restart = 1;
        break;
      }
      if (S.x == mark) {
        pt mn = S;
        uint64_t ma = a, mb = b;
        do {
          if (!step(&S, &a, &b)) break;
          if (S.x < mn.x) {
            mn = S;
            ma = a;
            mb = b;
          }
        } while (S.x != mark);
        S = canon(pdbl(mn), &mu);
        a = mulmod(2ULL * ma % ELL, mu);
        b = mulmod(2ULL * mb % ELL, mu);
        res.cycles++;
      }
      if ((len & (len - 1)) == 0) mark = S.x;
    }
    if (restart) continue;
    unsigned h = (unsigned)((S.x * 0x9E3779B97F4A7C15ULL) >>
                            (64 - TB_LOG)) &
                 (TB - 1);
    for (;; h = (h + 1) & (TB - 1)) {
      ent *e = &tab[h];
      if (e->gen != gen) {
        *e = (ent){S.x, S.y, a, b, gen};
        break;
      }
      if (e->x == S.x) {
        if (e->y != S.y) {
          fprintf(stderr, "canonicalization collision certificate failed\n");
          exit(2);
        }
        if (e->b == b) {
          res.useless++;
          break;
        }
        monotonic_now(&t1);
        counting = 0;
        res.adds = ctr.adds;
        res.doubles = ctr.doubles;
        res.ops = res.adds + res.doubles;
        res.walk_adds = res.adds - res.setup_adds;
        res.walk_doubles = res.doubles - res.setup_doubles;
        res.walk_ops = res.walk_adds + res.walk_doubles;
        res.canon_calls = ctr.canon_calls;
        res.canon_x_squares = ctr.canon_x_squares;
        res.canon_y_squares = ctr.canon_y_squares;
        res.canon_sign_tests = ctr.canon_sign_tests;
        res.canon_negations = ctr.canon_negations;
        res.sec = (double)(t1.tv_sec - t0.tv_sec) +
                  1e-9 * (double)(t1.tv_nsec - t0.tv_nsec);
        uint64_t kk =
            mulmod((e->a + ELL - a) % ELL,
                   invmod((b + ELL - e->b) % ELL));
        pt C = pmul(Pgen, kk);
        res.ok = (kk == k) && pt_equal(C, Q);
        return res;
      }
    }
  }
}

static int parse_u64(const char *s, uint64_t *out) {
  char *end = NULL;
  unsigned long long v;
  if (s[0] == '-') return 0;
  errno = 0;
  v = strtoull(s, &end, 0);
  if (errno != 0 || end == s || *end != '\0') return 0;
  *out = (uint64_t)v;
  return 1;
}

static int parse_mode(const char *s, int *out) {
  uint64_t v;
  if (!parse_u64(s, &v) || v > 2) return 0;
  *out = (int)v;
  return 1;
}

static void usage(FILE *f) {
  fprintf(f,
          "usage:\n"
          "  rho selftest <b> <a2> <mode> <setup_seed>\n"
          "  rho run <b> <a2> <mode> <nruns> <setup_seed> <target_seed> "
          "<walk_seed> <target_start> <out.csv>\n");
}

static FILE *open_output(const char *path) {
  if (strcmp(path, "-") == 0) return stdout;
  int fd = open(path, O_WRONLY | O_CREAT | O_EXCL, 0644);
  if (fd < 0) {
    fprintf(stderr, "cannot create output %s: %s\n", path, strerror(errno));
    return NULL;
  }
  FILE *f = fdopen(fd, "w");
  if (f == NULL) {
    fprintf(stderr, "cannot fdopen output %s: %s\n", path, strerror(errno));
    close(fd);
  }
  return f;
}

int main(int argc, char **argv) {
  uint64_t setup_seed;
  if (argc < 2) {
    usage(stderr);
    return 1;
  }
  if (strcmp(argv[1], "selftest") == 0) {
    if (argc != 6 || !parse_u64(argv[2], &B) ||
        !parse_u64(argv[3], &A2) || !parse_mode(argv[4], &mode) ||
        !parse_u64(argv[5], &setup_seed) || B > MASK || A2 > MASK) {
      usage(stderr);
      return 1;
    }
    if (!setup_curve(setup_seed)) return 2;
    printf("selftest_ok=1 b=%" PRIu64 " a2=%" PRIu64
           " mode=%d action_step=%u action_order=%u setup_seed=%" PRIu64
           " pgen_x=%" PRIu64 " pgen_y=%" PRIu64
           " setup_fingerprint=%016" PRIx64 "\n",
           B, A2, mode, action_step, action_order, setup_seed, Pgen.x, Pgen.y,
           setup_fingerprint);
    return 0;
  }
  if (strcmp(argv[1], "run") == 0) {
    uint64_t nruns, target_seed, walk_seed, target_start;
    if (argc != 11 || !parse_u64(argv[2], &B) ||
        !parse_u64(argv[3], &A2) || !parse_mode(argv[4], &mode) ||
        !parse_u64(argv[5], &nruns) ||
        !parse_u64(argv[6], &setup_seed) ||
        !parse_u64(argv[7], &target_seed) ||
        !parse_u64(argv[8], &walk_seed) ||
        !parse_u64(argv[9], &target_start) || B > MASK || A2 > MASK ||
        nruns == 0 || target_start > UINT64_MAX - (nruns - 1)) {
      usage(stderr);
      return 1;
    }
    if (!setup_curve(setup_seed)) return 2;
    tab = calloc(TB, sizeof(*tab));
    if (tab == NULL) {
      fprintf(stderr, "cannot allocate distinguished-point table\n");
      return 2;
    }
    FILE *f = open_output(argv[10]);
    if (f == NULL) {
      free(tab);
      return 2;
    }
    if (fprintf(f,
                "run,target_index,target_scalar,walk_stream_seed,ops,adds,"
                "doubles,setup_ops,setup_adds,setup_doubles,walk_ops,"
                "walk_adds,walk_doubles,canon_calls,canon_x_squares,"
                "canon_y_squares,canon_sign_tests,canon_negations,walks,"
                "cycles,abandoned,useless,ok,sec\n") < 0) {
      fprintf(stderr, "cannot write output header %s: %s\n", argv[10],
              strerror(errno));
      if (f != stdout) fclose(f);
      free(tab);
      return 2;
    }
    int status = 0;
    for (uint64_t i = 0; i < nruns; i++) {
      result r = solve_one(target_seed, walk_seed, target_start + i);
      if (fprintf(f,
                  "%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64
                  ",%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64
                  ",%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64
                  ",%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64
                  ",%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64
                  ",%" PRIu64 ",%" PRIu64 ",%d,%.9f\n",
                  i, r.target_index, r.target_scalar, r.walk_stream_seed,
                  r.ops, r.adds, r.doubles, r.setup_ops, r.setup_adds,
                  r.setup_doubles, r.walk_ops, r.walk_adds, r.walk_doubles,
                  r.canon_calls, r.canon_x_squares, r.canon_y_squares,
                  r.canon_sign_tests, r.canon_negations, r.walks, r.cycles,
                  r.abandoned, r.useless, r.ok, r.sec) < 0) {
        fprintf(stderr, "cannot write output row %s: %s\n", argv[10],
                strerror(errno));
        status = 2;
        break;
      }
      if (!r.ok) {
        fprintf(stderr, "planted-log verification failed at target %" PRIu64
                        "\n",
                r.target_index);
        status = 2;
        break;
      }
    }
    if (fflush(f) != 0) {
      fprintf(stderr, "cannot flush output %s: %s\n", argv[10],
              strerror(errno));
      status = 2;
    }
    if (f != stdout && fclose(f) != 0) {
      fprintf(stderr, "cannot close output %s: %s\n", argv[10],
              strerror(errno));
      status = 2;
    }
    free(tab);
    return status;
  }
  usage(stderr);
  return 1;
}
