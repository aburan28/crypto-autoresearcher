/* Count ordered pairs (X1,X2) in V x V with S3(X1,X2,xR)=0 over F_{2^n} (n odd, n<=63).
   args: n f_hex xR_hex a6_hex l basis_hex... (l basis elements)  */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <immintrin.h>
typedef unsigned __int128 u128;
static int n; static uint64_t f, mask;
static inline u128 clmul64(uint64_t a, uint64_t b) {
  __m128i A = _mm_set_epi64x(0, a), B = _mm_set_epi64x(0, b);
  __m128i C = _mm_clmulepi64_si128(A, B, 0);
  return ((u128)(uint64_t)_mm_extract_epi64(C, 1) << 64) | (uint64_t)_mm_extract_epi64(C, 0);
}
static inline uint64_t red(u128 x) {
  for (int d = 2 * n - 2; d >= n; d--) if ((x >> d) & 1) x ^= ((u128)f) << (d - n);
  return (uint64_t)x;
}
static inline uint64_t mul(uint64_t a, uint64_t b) { return red(clmul64(a, b)); }
static inline uint64_t sq(uint64_t a) { return mul(a, a); }
static uint64_t inv(uint64_t a) { /* a^(2^n-2) */
  uint64_t r = 1, x = a; uint64_t e = mask - 1;
  while (e) { if (e & 1) r = mul(r, x); x = sq(x); e >>= 1; }
  return r;
}
static int tr(uint64_t a) { uint64_t t = 0, x = a; for (int i = 0; i < n; i++) { t ^= x; x = sq(x); } return (int)(t & 1); }
/* general solver for y^2 + y = c (any n): precomputed elimination of L(y)=y^2+y */
static uint64_t Lpiv[64], Lpre[64]; static int Lhas[64];
static void as_setup(void) {
  for (int i = 0; i < n; i++) {
    uint64_t y = 1ULL << i, v = sq(y) ^ y;
    while (v) { int hb = 63 - __builtin_clzll(v); if (!Lhas[hb]) { Lhas[hb] = 1; Lpiv[hb] = v; Lpre[hb] = y; break; } v ^= Lpiv[hb]; y ^= Lpre[hb]; }
  }
}
static int as_solve(uint64_t c, uint64_t *y) { /* returns 1 and a root if solvable */
  uint64_t r = 0;
  while (c) { int hb = 63 - __builtin_clzll(c); if (!Lhas[hb]) return 0; c ^= Lpiv[hb]; r ^= Lpre[hb]; }
  *y = r; return 1;
}
static uint64_t ech[64]; static int haspiv[64];
static void addbasis(uint64_t v) { while (v) { int hb = 63 - __builtin_clzll(v); if (!haspiv[hb]) { haspiv[hb] = 1; ech[hb] = v; return; } v ^= ech[hb]; } fprintf(stderr, "dependent basis\n"); exit(1); }
static inline int inV(uint64_t v) { while (v) { int hb = 63 - __builtin_clzll(v); if (!haspiv[hb]) return 0; v ^= ech[hb]; } return 1; }
int main(int argc, char **argv) {
  n = atoi(argv[1]); f = strtoull(argv[2], 0, 16); uint64_t xR = strtoull(argv[3], 0, 16), a6 = strtoull(argv[4], 0, 16);
  int l = atoi(argv[5]); uint64_t *B = malloc(8 * l);
  for (int i = 0; i < l; i++) { B[i] = strtoull(argv[6 + i], 0, 16); addbasis(B[i]); }
  mask = (n == 64) ? ~0ULL : ((1ULL << n) - 1);
  as_setup();
  long long cnt = 0; uint64_t X1 = 0;
  for (uint64_t g = 0; g < (1ULL << l); g++) {
    if (g) { int bit = __builtin_ctzll(g); X1 ^= B[bit]; }
    uint64_t A = sq(X1 ^ xR), Bc = mul(X1, xR), C = sq(Bc) ^ a6;
    if (A == 0) { if (Bc == 0) { if (C == 0) cnt += 1LL << l; continue; } cnt += inV(mul(C, inv(Bc))); continue; }
    if (Bc == 0) { uint64_t t = mul(C, inv(A)); for (int i = 0; i < n - 1; i++) t = sq(t); cnt += inV(t); continue; }
    uint64_t Ai = inv(A), c1 = mul(Bc, Ai), c0 = mul(C, Ai);
    uint64_t rhs = mul(c0, inv(sq(c1)));
    uint64_t Y; if (!as_solve(rhs, &Y)) continue;
    cnt += inV(mul(c1, Y)); cnt += inV(mul(c1, Y ^ 1));
  }
  printf("%lld\n", cnt);
  return 0;
}
