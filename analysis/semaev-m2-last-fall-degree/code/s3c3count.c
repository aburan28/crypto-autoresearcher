/* Count Boolean solutions of Semaev's chained system (5) for t = 3:
     S3(u, X1, X2) = 0,  S3(u, X3, z) = 0,   u in F_{2^n},  X1, X2, X3 in V.
   Solutions are tuples (u, X1, X2, X3).  args: n f_hex z_hex a6_hex k basis_hex... */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <immintrin.h>
typedef unsigned __int128 u128;
static int n; static uint64_t f, mask;
static inline u128 clmul64(uint64_t a, uint64_t b) { __m128i A = _mm_set_epi64x(0, a), B = _mm_set_epi64x(0, b); __m128i C = _mm_clmulepi64_si128(A, B, 0); return ((u128)(uint64_t)_mm_extract_epi64(C, 1) << 64) | (uint64_t)_mm_extract_epi64(C, 0); }
static inline uint64_t red(u128 x) { for (int d = 2 * n - 2; d >= n; d--) if ((x >> d) & 1) x ^= ((u128)f) << (d - n); return (uint64_t)x; }
static inline uint64_t mul(uint64_t a, uint64_t b) { return red(clmul64(a, b)); }
static inline uint64_t sq(uint64_t a) { return mul(a, a); }
static uint64_t inv(uint64_t a) { uint64_t r = 1, x = a, e = mask - 1; while (e) { if (e & 1) r = mul(r, x); x = sq(x); e >>= 1; } return r; }
static uint64_t Lpiv[64], Lpre[64]; static int Lhas[64];
static void as_setup(void) { for (int i = 0; i < n; i++) { uint64_t y = 1ULL << i, v = sq(y) ^ y; while (v) { int hb = 63 - __builtin_clzll(v); if (!Lhas[hb]) { Lhas[hb] = 1; Lpiv[hb] = v; Lpre[hb] = y; break; } v ^= Lpiv[hb]; y ^= Lpre[hb]; } } }
static int as_solve(uint64_t c, uint64_t *y) { uint64_t r = 0; while (c) { int hb = 63 - __builtin_clzll(c); if (!Lhas[hb]) return 0; c ^= Lpiv[hb]; r ^= Lpre[hb]; } *y = r; return 1; }
static uint64_t ech[64]; static int haspiv[64];
static void addbasis(uint64_t v) { while (v) { int hb = 63 - __builtin_clzll(v); if (!haspiv[hb]) { haspiv[hb] = 1; ech[hb] = v; return; } v ^= ech[hb]; } fprintf(stderr, "dependent basis\n"); exit(1); }
static inline int inV(uint64_t v) { while (v) { int hb = 63 - __builtin_clzll(v); if (!haspiv[hb]) return 0; v ^= ech[hb]; } return 1; }
static uint64_t a6; static int k; static uint64_t *Bs;
/* all roots Y of S3(x, Y, w) = 0 in K for given x, w (as quadratic in Y); returns count, writes roots */
static int s3roots(uint64_t x, uint64_t w, uint64_t *out) {
  /* S3(x,Y,w) = Y^2 (x + w)^2 + Y x w + (x w)^2 + a6 */
  uint64_t A = sq(x ^ w), Bc = mul(x, w), C = sq(Bc) ^ a6; int c = 0;
  if (A == 0) { if (Bc == 0) { if (C == 0) return -1; return 0; } out[c++] = mul(C, inv(Bc)); return c; }
  if (Bc == 0) { uint64_t t = mul(C, inv(A)); for (int i = 0; i < n - 1; i++) t = sq(t); out[c++] = t; return c; }
  uint64_t Ai = inv(A), c1 = mul(Bc, Ai), c0 = mul(C, Ai), rhs = mul(c0, inv(sq(c1))), Y;
  if (!as_solve(rhs, &Y)) return 0;
  out[c++] = mul(c1, Y); out[c++] = mul(c1, Y ^ 1); return c;
}
/* number of (X1, X2) in V x V with S3(u, X1, X2) = 0 */
static long long count2(uint64_t u) {
  long long cnt = 0; uint64_t X1 = 0, r[2];
  for (uint64_t g = 0; g < (1ULL << k); g++) {
    if (g) X1 ^= Bs[__builtin_ctzll(g)];
    int c = s3roots(X1, u, r);  /* S3 symmetric: S3(u,X1,X2) = S3(X1,X2,u) */
    if (c < 0) { cnt += 1LL << k; continue; }
    for (int i = 0; i < c; i++) cnt += inV(r[i]);
  }
  return cnt;
}
int main(int argc, char **argv) {
  n = atoi(argv[1]); f = strtoull(argv[2], 0, 16); uint64_t z = strtoull(argv[3], 0, 16); a6 = strtoull(argv[4], 0, 16);
  k = atoi(argv[5]); Bs = malloc(8 * k); for (int i = 0; i < k; i++) { Bs[i] = strtoull(argv[6 + i], 0, 16); addbasis(Bs[i]); }
  mask = (1ULL << n) - 1; as_setup();
  long long total = 0; uint64_t X3 = 0, us[2];
  for (uint64_t g = 0; g < (1ULL << k); g++) {
    if (g) X3 ^= Bs[__builtin_ctzll(g)];
    int c = s3roots(X3, z, us);     /* roots u of S3(X3, u, z) = 0 */
    if (c < 0) { /* every u works: enumerate all u (only possible if degenerate) */ fprintf(stderr, "degenerate X3\n"); return 3; }
    for (int i = 0; i < c; i++) total += count2(us[i]);
  }
  printf("%lld\n", total);
  return 0;
}
