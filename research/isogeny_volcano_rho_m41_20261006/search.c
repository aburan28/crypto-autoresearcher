#include <immintrin.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include "params.h" /* M, RED, ELL, COF, LAMBDA0/1, QPOW, NORD: field and group for this study */
#define MASK ((1ULL << M) - 1)
static const uint64_t LAMBDA_ROOTS[2] = {LAMBDA0, LAMBDA1};


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


/* scan random b: curve y^2+xy=x^3+b (a2=0) is in the isogeny class iff #E = N.
 * filter: two random points P with [N]P = O (x-only Lopez-Dahab ladder). Hits are
 * re-verified with PARI ellcard downstream; this is only a sieve. */
static uint64_t rs;
static uint64_t rnd(void) { uint64_t z = (rs += 0x9E3779B97F4A7C15ULL); z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL; z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL; return z ^ (z >> 31); }

static int kills(fe b, fe x) { /* is [NORD](x,.) = O ? */
  fe X0 = x, Z0 = 1, X1, Z1;
  fe x2 = fsqr(x); X1 = fsqr(x2) ^ b; Z1 = x2; /* 2P */
  for (int i = 62 - __builtin_clzll(NORD); i >= 0; i--) {
    fe T = fmul(X0, Z1), U = fmul(X1, Z0), Za = fsqr(T ^ U), Xa = fmul(x, Za) ^ fmul(T, U);
    if ((NORD >> i) & 1) { fe xx = fsqr(X1), zz = fsqr(Z1); X1 = fsqr(xx) ^ fmul(b, fsqr(zz)); Z1 = fmul(xx, zz); X0 = Xa; Z0 = Za; }
    else { fe xx = fsqr(X0), zz = fsqr(Z0); X0 = fsqr(xx) ^ fmul(b, fsqr(zz)); Z0 = fmul(xx, zz); X1 = Xa; Z1 = Za; }
  }
  return Z0 == 0;
}
static int point_x(fe b, fe *x) { /* random x of a point on E_b */
  for (int t = 0; t < 64; t++) { fe c = rnd() & MASK; if (!c) continue; fe v = c ^ fmul(b, finv(fsqr(c))); if (!ftrace(v)) { *x = c; return 1; } }
  return 0;
}
int main(int argc, char **argv) {
  rs = strtoull(argv[1], 0, 10); uint64_t n = strtoull(argv[2], 0, 10);
  if (argc > 3) { fe b = strtoull(argv[3], 0, 10), x; int ok = 1; for (int k = 0; k < 8; k++) { point_x(b, &x); ok &= kills(b, x); } printf("%d\n", ok); return 0; }
  for (uint64_t i = 0; i < n; i++) {
    fe b = rnd() & MASK, x; if (!b) continue;
    if (!point_x(b, &x) || !kills(b, x)) continue;
    if (!point_x(b, &x) || !kills(b, x)) continue;
    printf("%llu\n", (unsigned long long)b); fflush(stdout);
  }
  return 0;
}
