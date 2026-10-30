/* Separate unqualified RREF exporter candidate. Reference SHA256 2413e3a3f34d0fdda8a53b0d62acff53aeaabc593b1c55fe42a3d7db8af3cc4f */
/* Optimized exact degree-D closure W_D over B = F2[x]/(x_i^2+x_i).
 * Same object as lfdclose.c; optimizations (all exact):
 *  - echelon (not reduced) form; W cap B_{<=D-1} = span of rows with low leading column
 *  - products x*M_{D-1} are already in M_D: pre-mark leading columns of M_{D-1}
 *  - mutant products added in chunks (bounded memory), early stop when 1 appears
 * args: D [verbose] [chunk_rows] [cert_path]   stdin: system
 * output: M_D dims, W_D dims (cumulative dims of W cap B_{<=d}), W_one, iterations
 * cert_path: if 1 is not in W_D, write the quotient map pi: B_{<=D} -> B_{<=D}/W_D (see export_cert)
 *   for verify/cert_check.py, which re-checks it without trusting this program. */
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
/* Certificate: with U = rowspace(A) = W_D, write pi: B_{<=D} -> F_2^nq, where nq = ncols - rank and
 * pi(m) = the reduction of the monomial m modulo U, expressed on the non-pivot columns.
 * Row echelon form: row i is e_{p_i} + (terms in columns > p_i), so pi(e_p) = sum of pi(e_t) over those terms.
 * Pivot rows are processed from the last pivot to the first. Non-pivot column q-th (in column order) has pi = unit vector q.
 * File (little endian): int64 N, D, ncols, nq; uint64 mask[ncols]; uint64 pi[ncols][qw], qw = max(1, ceil(nq/64)). */
/* Alternate exporter only: same closure, columns and quotient basis.
 * Full RREF has pivot rows e_p + sum_q a[p,q] e_q. Thus pi(e_p)
 * is exactly the free-column coefficient vector. This is the same unique
 * normal form computed by the reference reverse-substitution exporter.
 */
static void export_cert(const char *path, mzd_t *A, long rank) {
  char *before = calloc(ncols, 1), *seen = calloc(ncols, 1);
  long nq = ncols - rank, *freecols = malloc(sizeof(long) * (nq + 1));
  if (!before || !seen || !freecols || nq <= 0) { fprintf(stderr, "invalid export allocation/rank\n"); exit(6); }
  for (long i = 0; i < rank; i++) {
    long c = leadcol(A, i);
    if (c < 0 || c >= ncols || before[c]) { fprintf(stderr, "export: invalid pivot\n"); exit(5); }
    before[c] = 1;
  }
  long q = 0;
  for (long c = 0; c < ncols; c++) if (!before[c]) freecols[q++] = c;
  if (q != nq) { fprintf(stderr, "export: free-column mismatch\n"); exit(5); }
  fprintf(stderr, "export_rref_start rank %ld cols %ld nq %ld\n", rank, ncols, nq);
  long reduced_rank = mzd_echelonize_m4ri(A, 1, 0);
  if (reduced_rank != rank) { fprintf(stderr, "export: rank changed\n"); exit(5); }
  fprintf(stderr, "export_rref_done rank %ld\n", reduced_rank);
  size_t qw = (size_t)((nq + 63) / 64);
  if ((size_t)ncols > SIZE_MAX / qw / 8) { fprintf(stderr, "export size overflow\n"); exit(6); }
  uint64_t *R = calloc((size_t)ncols * qw, 8);
  if (!R) { perror("export map"); exit(6); }
  for (long j = 0; j < nq; j++) R[(size_t)freecols[j] * qw + (j >> 6)] = 1ULL << (j & 63);
  for (long i = 0; i < rank; i++) {
    long c = leadcol(A, i);
    if (c < 0 || c >= ncols || !before[c] || seen[c]) { fprintf(stderr, "export: pivot basis changed\n"); exit(5); }
    seen[c] = 1;
    word *row = mzd_row(A, i); uint64_t *dst = R + (size_t)c * qw;
    for (long j = 0; j < nq; j++) {
      long f = freecols[j];
      if ((row[f >> 6] >> (f & 63)) & 1) dst[j >> 6] |= 1ULL << (j & 63);
    }
  }
  FILE *fh = fopen(path, "wb"); if (!fh) { perror("cert"); exit(6); }
  int64_t hdr[4] = { N, D, ncols, nq };
  if (fwrite(hdr, 8, 4, fh) != 4 || fwrite(colmask, 8, ncols, fh) != (size_t)ncols ||
      fwrite(R, 8, (size_t)ncols * qw, fh) != (size_t)ncols * qw || fclose(fh)) {
    fprintf(stderr, "certificate write failed\n"); exit(6);
  }
  fprintf(stderr, "cert written: %s ncols %ld rank %ld nq %ld\n", path, ncols, rank, nq);
  free(R); free(freecols); free(before); free(seen);
}

int main(int argc, char **argv) {
  if (argc < 2) { fprintf(stderr, "usage: lfdclose2 D [verbose] [chunk]\n"); return 1; }
  D = atoi(argv[1]); int verbose = argc > 2 ? atoi(argv[2]) : 0; long chunk = argc > 3 ? atol(argv[3]) : 60000; const char *cert = argc > 4 ? argv[4] : NULL;
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
  if (cert && !one) export_cert(cert, A, rank);
  mzd_free(A); return 0;
}
