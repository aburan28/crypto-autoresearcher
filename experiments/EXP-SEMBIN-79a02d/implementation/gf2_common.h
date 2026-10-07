/* EXP-SEMBIN-79a02d -- shared I/O + monomial index for the two GF(2) arms.
 * Only parsing, the monomial table and polynomial products live here; the
 * ELIMINATION code is separate per arm (gf2_armA.c: row insertion;
 * gf2_armB.c: Four-Russians block elimination). No M4RI is linked.
 *
 * Generator file format (text): line 1 "N <nvars>", then one polynomial per
 * line as space-separated hex monomial bitmasks (bit i = variable i).
 */
#ifndef GF2_COMMON_H
#define GF2_COMMON_H
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/resource.h>
#include <time.h>

typedef uint64_t u64;

typedef struct { int nt; u64 *t; int deg; } poly_t;

static int popc(u64 x) { return __builtin_popcountll(x); }

static double now_s(void) {
  struct timespec ts; clock_gettime(CLOCK_MONOTONIC, &ts);
  return ts.tv_sec + 1e-9 * ts.tv_nsec;
}
static long peak_rss_kb(void) { struct rusage r; getrusage(RUSAGE_SELF, &r); return r.ru_maxrss; }

static int read_gens(const char *path, int *N, poly_t **out) {
  FILE *f = fopen(path, "r");
  if (!f) { perror(path); exit(2); }
  if (fscanf(f, "N %d\n", N) != 1) { fprintf(stderr, "bad header\n"); exit(2); }
  int cap = 64, np = 0;
  poly_t *P = malloc(sizeof(poly_t) * cap);
  char *line = NULL; size_t ln = 0; ssize_t r;
  while ((r = getline(&line, &ln, f)) > 0) {
    int tc = 0, tcap = 64; u64 *t = malloc(8 * tcap);
    char *s = line, *e;
    while (1) {
      u64 v = strtoull(s, &e, 16);
      if (e == s) break;
      if (tc == tcap) { tcap *= 2; t = realloc(t, 8 * tcap); }
      t[tc++] = v; s = e;
    }
    if (!tc) { free(t); continue; }
    if (np == cap) { cap *= 2; P = realloc(P, sizeof(poly_t) * cap); }
    int d = 0; for (int i = 0; i < tc; i++) if (popc(t[i]) > d) d = popc(t[i]);
    P[np].nt = tc; P[np].t = t; P[np].deg = d; np++;
  }
  free(line); fclose(f);
  *out = P; return np;
}

/* ---------- monomial index: all square-free monomials of degree <= D,
 * graded DESCENDING (degree D first), within a degree lexicographic in the
 * sorted index tuple (itertools.combinations order). Column 0 = first
 * degree-D monomial; last column = constant 1. */
typedef struct {
  int N, D; long ncols;
  u64 *mono;            /* col -> mask */
  long *degstart;       /* first col of degree d (degstart[d]) ; degree d occupies [degstart[d], degstart[d]+C(N,d)) */
  u64 *hkey; long *hval; long hcap;  /* open addressing mask -> col */
} monidx_t;

static void hput(monidx_t *M, u64 k, long v) {
  u64 h = (k * 0x9E3779B97F4A7C15ULL) >> 1; long i = (long)(h % (u64)M->hcap);
  while (M->hval[i] >= 0) { i++; if (i == M->hcap) i = 0; }
  M->hkey[i] = k; M->hval[i] = v;
}
static long hget(const monidx_t *M, u64 k) {
  u64 h = (k * 0x9E3779B97F4A7C15ULL) >> 1; long i = (long)(h % (u64)M->hcap);
  while (M->hval[i] >= 0) { if (M->hkey[i] == k) return M->hval[i]; i++; if (i == M->hcap) i = 0; }
  return -1;
}

static long binom(int n, int k) { if (k < 0 || k > n) return 0; long r = 1; for (int i = 1; i <= k; i++) r = r * (n - k + i) / i; return r; }

static void enum_combos(int N, int d, u64 *out, long *pos) {
  int idx[64];
  if (d == 0) { out[(*pos)++] = 0; return; }
  for (int i = 0; i < d; i++) idx[i] = i;
  while (1) {
    u64 m = 0; for (int i = 0; i < d; i++) m |= 1ULL << idx[i];
    out[(*pos)++] = m;
    int i = d - 1;
    while (i >= 0 && idx[i] == N - d + i) i--;
    if (i < 0) break;
    idx[i]++; for (int j = i + 1; j < d; j++) idx[j] = idx[j - 1] + 1;
  }
}

static void monidx_init(monidx_t *M, int N, int D) {
  M->N = N; M->D = D; M->ncols = 0;
  for (int d = 0; d <= D; d++) M->ncols += binom(N, d);
  M->mono = malloc(8 * M->ncols);
  M->degstart = malloc(sizeof(long) * (D + 2));
  long pos = 0;
  for (int d = D; d >= 0; d--) { M->degstart[d] = pos; enum_combos(N, d, M->mono, &pos); }
  M->hcap = 2 * M->ncols + 17;
  M->hkey = malloc(8 * M->hcap); M->hval = malloc(sizeof(long) * M->hcap);
  for (long i = 0; i < M->hcap; i++) M->hval[i] = -1;
  for (long c = 0; c < M->ncols; c++) hput(M, M->mono[c], c);
}

/* product of poly f with monomial m in the Boolean ring: writes surviving
 * monomial masks (multiplicity mod 2) into buf (sorted), returns count.
 * buf must hold f->nt entries. */
static int cmp_u64(const void *a, const void *b) {
  u64 x = *(const u64 *)a, y = *(const u64 *)b; return x < y ? -1 : x > y;
}
static int poly_mul_mono(const poly_t *f, u64 m, u64 *buf) {
  for (int i = 0; i < f->nt; i++) buf[i] = f->t[i] | m;
  qsort(buf, f->nt, 8, cmp_u64);
  int o = 0;
  for (int i = 0; i < f->nt;) {
    int j = i; while (j < f->nt && buf[j] == buf[i]) j++;
    if ((j - i) & 1) buf[o++] = buf[i];
    i = j;
  }
  return o;
}

/* order-independent fingerprint of a row given as sorted mask list */
static u64 row_hash(const u64 *t, int n) {
  u64 h = 0xcbf29ce484222325ULL ^ (u64)n;
  for (int i = 0; i < n; i++) { h ^= t[i] + 0x9E3779B97F4A7C15ULL + (h << 6) + (h >> 2); h *= 0x100000001b3ULL; }
  return h;
}

#endif
