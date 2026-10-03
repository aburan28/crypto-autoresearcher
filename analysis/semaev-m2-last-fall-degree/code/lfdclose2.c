/* Optimized exact degree-D closure W_D over B = F2[x]/(x_i^2+x_i).
 * Same object as lfdclose.c; optimizations (all exact):
 *  - echelon (not reduced) form; W cap B_{<=D-1} = span of rows with low leading column
 *  - products x*M_{D-1} are already in M_D: pre-mark leading columns of M_{D-1}
 *  - mutant products added in chunks (bounded memory), early stop when 1 appears
 * args: D [verbose] [chunk_rows]   stdin: system
 * output: M_D dims, W_D dims (cumulative dims of W cap B_{<=d}), W_one, iterations */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <m4ri/m4ri.h>

static int N, D;
static uint64_t binom[70][70];
static long ncols, offset[16], blocksz[16];
static uint64_t *colmask;
static long rank_colex(uint64_t m) { int i = 0; long r = 0; while (m) { int p = __builtin_ctzll(m); i++; r += (long)binom[p][i]; m &= m - 1; } return r; }
static inline long colindex(uint64_t m) { return offset[__builtin_popcountll(m)] + rank_colex(m); }
static void setup_columns(void) {
  for (int a = 0; a < 70; a++) { binom[a][0] = 1; for (int b = 1; b <= a; b++) binom[a][b] = binom[a-1][b-1] + (b <= a-1 ? binom[a-1][b] : 0); }
  long c = 0;
  for (int d = D; d >= 0; d--) { offset[d] = c; blocksz[d] = (d <= N) ? (long)binom[N][d] : 0; c += blocksz[d]; }
  ncols = c; colmask = malloc(sizeof(uint64_t) * ncols);
  for (int d = D; d >= 0; d--) {
    if (d > N) continue;
    if (d == 0) { colmask[offset[0]] = 0; continue; }
    uint64_t m = (1ULL << d) - 1; long k = 0;
    while (1) { colmask[offset[d] + k++] = m; if (k == blocksz[d]) break; uint64_t u = m & (~m + 1), v = m + u; m = v + (((v ^ m) / u) >> 2); }
  }
}
typedef struct { int nt; uint64_t *t; int deg; } poly;
static poly *P; static int np;
static inline void addterms(word *row, const uint64_t *t, int nt, uint64_t mm) { for (int i = 0; i < nt; i++) { long c = colindex(t[i] | mm); row[c >> 6] ^= ((word)1) << (c & 63); } }
static inline long leadcol(mzd_t *A, long i) { word *row = mzd_row(A, i); for (wi_t w = 0; w < A->width; w++) if (row[w]) return w * 64 + __builtin_ctzll(row[w]); return -1; }

/* Macaulay rows for degree bound Dm (deg m + deg f <= Dm) into new matrix */
static mzd_t *macaulay(int Dm) {
  long nrows = 0;
  for (int i = 0; i < np; i++) if (P[i].nt && P[i].deg <= Dm) for (int d = 0; d <= Dm - P[i].deg; d++) nrows += blocksz[d];
  mzd_t *A = mzd_init(nrows > 0 ? nrows : 1, ncols); long r = 0;
  for (int i = 0; i < np; i++) { if (!P[i].nt || P[i].deg > Dm) continue;
    for (int d = 0; d <= Dm - P[i].deg; d++) for (long k = 0; k < blocksz[d]; k++) addterms(mzd_row(A, r++), P[i].t, P[i].nt, colmask[offset[d] + k]); }
  return A;
}
static void dims_of(mzd_t *A, long rank, long *dims, int *one) {
  for (int e = 0; e <= D; e++) dims[e] = 0; *one = 0;
  for (long i = 0; i < rank; i++) { long c = leadcol(A, i); int dg = __builtin_popcountll(colmask[c]); for (int e = dg; e <= D; e++) dims[e]++; if (c == ncols - 1) *one = 1; }
}
int main(int argc, char **argv) {
  if (argc < 2) { fprintf(stderr, "usage: lfdclose2 D [verbose] [chunk]\n"); return 1; }
  D = atoi(argv[1]); int verbose = argc > 2 ? atoi(argv[2]) : 0; long chunk = argc > 3 ? atol(argv[3]) : 60000;
  if (scanf("%d %d", &N, &np) != 2) return 2;
  P = malloc(sizeof(poly) * np);
  for (int i = 0; i < np; i++) { if (scanf("%d", &P[i].nt) != 1) return 3; P[i].t = malloc(8 * (P[i].nt + 1)); P[i].deg = -1;
    for (int j = 0; j < P[i].nt; j++) { unsigned long long x; if (scanf("%llx", &x) != 1) return 4; P[i].t[j] = x; int d = __builtin_popcountll(x); if (d > P[i].deg) P[i].deg = d; } }
  setup_columns();
  long lowstart = offset[D - 1];
  char *mult = calloc(ncols, 1);
  /* pre-mark leading columns of M_{D-1} (its x-multiples lie in M_D) */
  if (D >= 3) { mzd_t *Mp = macaulay(D - 1); long rp = mzd_echelonize_m4ri(Mp, 0, 0); for (long i = 0; i < rp; i++) mult[leadcol(Mp, i)] = 1; mzd_free(Mp); }
  mzd_t *A = macaulay(D);
  long rank = mzd_echelonize_m4ri(A, 0, 0);
  long dims[16]; int one;
  dims_of(A, rank, dims, &one);
  printf("M%d_dims", D); for (int e = 0; e <= D; e++) printf(" %ld", dims[e]); printf(" M%d_one %d\n", D, one);
  int iter = 0;
  while (!one) {
    /* new low rows: leading column low and not yet multiplied */
    long nnew = 0; long *newr = malloc(sizeof(long) * (rank + 1));
    for (long i = 0; i < rank; i++) { long c = leadcol(A, i); if (c >= lowstart && !mult[c]) { mult[c] = 1; newr[nnew++] = i; } }
    if (verbose) { fprintf(stderr, "iter %d rank %ld new_low %ld dims:", iter, rank, nnew); for (int e = 0; e <= D; e++) fprintf(stderr, " %ld", dims[e]); fprintf(stderr, "\n"); }
    if (nnew == 0) { free(newr); break; }
    /* copy the new low rows out (A will be replaced) */
    wi_t lw = (wi_t)(lowstart / 64);
    mzd_t *Lw = mzd_init(nnew, ncols);
    for (long q = 0; q < nnew; q++) memcpy(mzd_row(Lw, q), mzd_row(A, newr[q]), sizeof(word) * A->width);
    free(newr);
    long total = nnew * (long)N, done = 0;
    while (done < total && !one) {
      long take = total - done < chunk ? total - done : chunk;
      mzd_t *B = mzd_init(rank + take, ncols);
      for (long i = 0; i < rank; i++) memcpy(mzd_row(B, i), mzd_row(A, i), sizeof(word) * A->width);
      for (long j = 0; j < take; j++) {
        long idx = done + j; long q = idx / N; int v = (int)(idx % N);
        word *src = mzd_row(Lw, q), *dst = mzd_row(B, rank + j); uint64_t vb = 1ULL << v;
        for (wi_t w = lw; w < Lw->width; w++) { word x = src[w]; while (x) { int b = __builtin_ctzll(x); x &= x - 1; long c2 = colindex(colmask[w * 64 + b] | vb); dst[c2 >> 6] ^= ((word)1) << (c2 & 63); } }
      }
      mzd_free(A); A = B; rank = mzd_echelonize_m4ri(A, 0, 0); done += take;
      dims_of(A, rank, dims, &one);
      if (verbose > 1) { fprintf(stderr, "   chunk done %ld/%ld rank %ld dims:", done, total, rank); for (int e = 0; e <= D; e++) fprintf(stderr, " %ld", dims[e]); fprintf(stderr, "\n"); }
    }
    mzd_free(Lw); iter++;
  }
  printf("W%d_dims", D); for (int e = 0; e <= D; e++) printf(" %ld", dims[e]); printf(" W%d_one %d iters %d ncols %ld\n", D, one, iter, ncols);
  mzd_free(A); return 0;
}
