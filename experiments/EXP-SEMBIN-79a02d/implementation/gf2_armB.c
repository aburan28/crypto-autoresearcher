/* EXP-SEMBIN-79a02d -- GF(2) ARM B: Four-Russians block elimination.
 * Written independently of arm A (different algorithm, different data
 * layout): whole matrices are held as contiguous row-major bit arrays;
 * pivots are found in blocks of up to 8 by a lazy column search, the block
 * is put in reduced form on its pivot columns, a 2^p Gray-code table of
 * block-row combinations is built, and every remaining row is cleared on the
 * block pivots with ONE table lookup. Closure rounds are processed as
 * batches: reduce the batch against the basis with per-group tables, then
 * echelonize the residual. M4RI-free (no libm4ri linked or called).
 *
 *   gf2_armB mac <gens> <D>
 *   gf2_armB closure <gens> <D>
 */
#include "gf2_common.h"

#define K4R 8

static inline int gb(const u64 *r, long c) { return (int)((r[c >> 6] >> (c & 63)) & 1); }

static void xor_from(u64 *dst, const u64 *src, long w0, long W) {
  for (long i = w0; i < W; i++) dst[i] ^= src[i];
}

/* Forward echelon of A (m x W words) in place. Writes pivot columns to pc_out
 * (rows 0..rank-1 of A become the echelon rows, leading bit = pivot). */
static long m4r_echelon(u64 *A, long m, long W, long ncols, long *pc_out) {
  u64 *T = malloc(sizeof(u64) * (1L << K4R) * W);
  u64 *tmp = malloc(8 * W);
  long r = 0, col = 0;
  while (r < m && col < ncols) {
    long pc[K4R]; int p = 0;
    while (p < K4R && col < ncols) {
      long found = -1;
      for (long i = r + p; i < m; i++) {
        const u64 *ri = A + i * W;
        int b = gb(ri, col);
        for (int j = 0; j < p; j++) if (gb(ri, pc[j])) b ^= gb(A + (r + j) * W, col);
        if (b) { found = i; break; }
      }
      if (found >= 0) {
        u64 *nr = A + (r + p) * W;
        if (found != r + p) {
          u64 *fr = A + found * W;
          memcpy(tmp, nr, 8 * W); memcpy(nr, fr, 8 * W); memcpy(fr, tmp, 8 * W);
        }
        for (int j = 0; j < p; j++) if (gb(nr, pc[j])) xor_from(nr, A + (r + j) * W, pc[j] >> 6, W);
        for (int j = 0; j < p; j++) { u64 *pj = A + (r + j) * W; if (gb(pj, col)) xor_from(pj, nr, col >> 6, W); }
        pc[p++] = col;
      }
      col++;
    }
    if (!p) break;
    long w0 = pc[0] >> 6, ww = W - w0;
    memset(T, 0, 8 * ww);
    for (long idx = 1; idx < (1L << p); idx++) {
      int lb = __builtin_ctzl(idx);
      u64 *dst = T + idx * ww; const u64 *a = T + (idx & (idx - 1)) * ww; const u64 *b = A + (r + lb) * W + w0;
      for (long i = 0; i < ww; i++) dst[i] = a[i] ^ b[i];
    }
    for (long i = r + p; i < m; i++) {
      u64 *ri = A + i * W;
      long idx = 0; for (int j = 0; j < p; j++) idx |= (long)gb(ri, pc[j]) << j;
      if (idx) { const u64 *t = T + idx * ww; u64 *d = ri + w0; for (long q = 0; q < ww; q++) d[q] ^= t[q]; }
    }
    for (int j = 0; j < p; j++) pc_out[r + j] = pc[j];
    r += p;
  }
  free(T); free(tmp);
  return r;
}

static void print_hist(const char *name, long *h, int D) {
  printf("\"%s\":[", name);
  for (int d = 0; d <= D; d++) printf("%ld%s", h[d], d < D ? "," : "");
  printf("]");
}

typedef struct { u64 *A; long m, cap, W; } mat_t;
static u64 *mat_push(mat_t *X) {
  if (X->m == X->cap) { X->cap = X->cap ? 2 * X->cap : 1024; X->A = realloc(X->A, 8 * X->W * X->cap); if (!X->A) { fprintf(stderr, "OOM\n"); exit(4); } }
  u64 *r = X->A + X->m * X->W; memset(r, 0, 8 * X->W); X->m++; return r;
}

static int do_mac(const char *gens, int D) {
  int N; poly_t *P; int np = read_gens(gens, &N, &P);
  double t0 = now_s();
  monidx_t M; monidx_init(&M, N, D);
  long W = (M.ncols + 63) / 64;
  mat_t X = {0}; X.W = W;
  int maxt = 0; for (int i = 0; i < np; i++) if (P[i].nt > maxt) maxt = P[i].nt;
  u64 *buf = malloc(8 * maxt), *mults = malloc(8 * (M.ncols + 1));
  long nnz = 0, zero_products = 0; u64 fp = 0;
  char *occ = calloc(M.ncols, 1);
  for (int i = 0; i < np; i++) {
    if (P[i].deg > D) continue;
    for (int s = 0; s <= D - P[i].deg; s++) {
      long cnt = 0; enum_combos(N, s, mults, &cnt);
      for (long j = 0; j < cnt; j++) {
        int nt = poly_mul_mono(&P[i], mults[j], buf);
        if (!nt) { zero_products++; continue; }
        nnz += nt; fp += row_hash(buf, nt);
        u64 *row = mat_push(&X);
        for (int t = 0; t < nt; t++) { long c = hget(&M, buf[t]); if (c < 0) { fprintf(stderr, "term outside\n"); return 3; } row[c >> 6] ^= 1ULL << (c & 63); occ[c] = 1; }
      }
    }
  }
  long ncols_occ = 0; for (long c = 0; c < M.ncols; c++) ncols_occ += occ[c];
  long *pc = malloc(sizeof(long) * (X.m + 1));
  long rank = m4r_echelon(X.A, X.m, W, M.ncols, pc);
  long hist[64] = {0}; for (long i = 0; i < rank; i++) hist[popc(M.mono[pc[i]])]++;
  printf("{\"arm\":\"B-four-russians\",\"task\":\"mac\",\"N\":%d,\"D\":%d,\"ngens\":%d,"
         "\"nrows\":%ld,\"ncols_all\":%ld,\"ncols_occurring\":%ld,\"nnz\":%ld,"
         "\"zero_products_dropped\":%ld,\"rank\":%ld,\"fingerprint\":\"%016llx\",",
         N, D, np, X.m, M.ncols, ncols_occ, nnz, zero_products, rank, (unsigned long long)fp);
  print_hist("pivots_by_degree", hist, D);
  printf(",\"seconds\":%.3f,\"peak_rss_kb\":%ld}\n", now_s() - t0, peak_rss_kb());
  return 0;
}

/* basis: rows Bm (rank x W) with pivots bp[], kept sorted by pivot */
typedef struct { u64 *A; long *pc; long r, cap, W; } bas_t;

static void bas_sort(bas_t *S) {
  /* insertion-merge by pivot: simple index sort then permute */
  long r = S->r, W = S->W;
  long *ord = malloc(sizeof(long) * r);
  for (long i = 0; i < r; i++) ord[i] = i;
  /* sort ord by pc */
  for (long gap = r / 2; gap > 0; gap /= 2)
    for (long i = gap; i < r; i++) { long t = ord[i], j = i; while (j >= gap && S->pc[ord[j - gap]] > S->pc[t]) { ord[j] = ord[j - gap]; j -= gap; } ord[j] = t; }
  u64 *NA = malloc(8 * W * (S->cap ? S->cap : 1)); long *np_ = malloc(sizeof(long) * (S->cap ? S->cap : 1));
  for (long i = 0; i < r; i++) { memcpy(NA + i * W, S->A + ord[i] * W, 8 * W); np_[i] = S->pc[ord[i]]; }
  free(S->A); free(S->pc); free(ord); S->A = NA; S->pc = np_;
}

static void bas_add(bas_t *S, const u64 *rows, const long *pcs, long k) {
  if (S->r + k > S->cap) { S->cap = (S->r + k) * 2 + 16; S->A = realloc(S->A, 8 * S->W * S->cap); S->pc = realloc(S->pc, sizeof(long) * S->cap); }
  memcpy(S->A + S->r * S->W, rows, 8 * S->W * k); memcpy(S->pc + S->r, pcs, sizeof(long) * k); S->r += k;
  bas_sort(S);
}

/* reduce every row of C (m x W) against basis S using per-group tables */
static void reduce_against(bas_t *S, u64 *C, long m) {
  long W = S->W;
  u64 *T = malloc(sizeof(u64) * (1L << K4R) * W);
  for (long g0 = 0; g0 < S->r; g0 += K4R) {
    int p = (int)((S->r - g0) < K4R ? (S->r - g0) : K4R);
    /* reduced form on the group's pivot columns (keeps leading bits) */
    for (int a = p - 1; a >= 0; a--)
      for (int b = a + 1; b < p; b++) {
        u64 *ra = S->A + (g0 + a) * W; const u64 *rb = S->A + (g0 + b) * W;
        if (gb(ra, S->pc[g0 + b])) xor_from(ra, rb, S->pc[g0 + b] >> 6, W);
      }
    long w0 = S->pc[g0] >> 6, ww = W - w0;
    memset(T, 0, 8 * ww);
    for (long idx = 1; idx < (1L << p); idx++) {
      int lb = __builtin_ctzl(idx);
      u64 *dst = T + idx * ww; const u64 *a = T + (idx & (idx - 1)) * ww; const u64 *b = S->A + (g0 + lb) * W + w0;
      for (long i = 0; i < ww; i++) dst[i] = a[i] ^ b[i];
    }
    for (long i = 0; i < m; i++) {
      u64 *ri = C + i * W;
      long idx = 0; for (int j = 0; j < p; j++) idx |= (long)gb(ri, S->pc[g0 + j]) << j;
      if (idx) { const u64 *t = T + idx * ww; u64 *d = ri + w0; for (long q = 0; q < ww; q++) d[q] ^= t[q]; }
    }
  }
  free(T);
}

static long absorb(bas_t *S, mat_t *X, long ncols) {
  long W = S->W;
  if (S->r) reduce_against(S, X->A, X->m);
  /* compact nonzero rows */
  long k = 0;
  for (long i = 0; i < X->m; i++) {
    u64 *ri = X->A + i * W; int nz = 0; for (long q = 0; q < W; q++) if (ri[q]) { nz = 1; break; }
    if (nz) { if (k != i) memcpy(X->A + k * W, ri, 8 * W); k++; }
  }
  long *pc = malloc(sizeof(long) * (k + 1));
  long rk = m4r_echelon(X->A, k, W, ncols, pc);
  if (rk) bas_add(S, X->A, pc, rk);
  free(pc);
  X->m = 0;
  return rk;
}

static int do_closure(const char *gens, int D) {
  int N; poly_t *P; int np = read_gens(gens, &N, &P);
  double t0 = now_s();
  monidx_t M; monidx_init(&M, N, D);
  long W = (M.ncols + 63) / 64;
  mat_t X = {0}; X.W = W;
  bas_t S = {0}; S.W = W;
  int maxt = 0; for (int i = 0; i < np; i++) if (P[i].nt > maxt) maxt = P[i].nt;
  u64 *buf = malloc(8 * maxt), *mults = malloc(8 * (M.ncols + 1));
  long l0_rows = 0, l0_rej = 0, l0_zero = 0; u64 fp = 0;
  for (int i = 0; i < np; i++)
    for (int s = 0; s <= D; s++) {
      long cnt = 0; enum_combos(N, s, mults, &cnt);
      for (long j = 0; j < cnt; j++) {
        int nt = poly_mul_mono(&P[i], mults[j], buf);
        if (!nt) { l0_zero++; continue; }
        int ok = 1; for (int t = 0; t < nt; t++) if (popc(buf[t]) > D) { ok = 0; break; }
        if (!ok) { l0_rej++; continue; }
        l0_rows++; fp += row_hash(buf, nt);
        u64 *row = mat_push(&X);
        for (int t = 0; t < nt; t++) { long c = hget(&M, buf[t]); row[c >> 6] ^= 1ULL << (c & 63); }
      }
    }
  absorb(&S, &X, M.ncols);
  long l0_rank = S.r;
  long lowstart = (D >= 1) ? M.degstart[D - 1] : M.ncols;
  char *done = calloc(M.ncols, 1);
  int rounds = 0, productive = 0; long round_new[256];
  u64 *g = malloc(8 * W);
  for (;;) {
    long cnt_new = 0;
    /* snapshot the not-yet-multiplied low rows */
    long nlow = 0; for (long i = 0; i < S.r; i++) if (S.pc[i] >= lowstart && !done[S.pc[i]]) nlow++;
    if (!nlow) break;
    u64 *G = malloc(8 * W * nlow); long q = 0;
    for (long i = 0; i < S.r; i++) if (S.pc[i] >= lowstart && !done[S.pc[i]]) { memcpy(G + q * W, S.A + i * W, 8 * W); done[S.pc[i]] = 1; q++; }
    for (long a = 0; a < nlow; a++) {
      memcpy(g, G + a * W, 8 * W);
      for (int v = 0; v < N; v++) {
        u64 *row = mat_push(&X);
        for (long w = lowstart >> 6; w < W; w++) {
          u64 x = g[w];
          while (x) {
            long c = w * 64 + __builtin_ctzll(x); x &= x - 1;
            long c2 = hget(&M, M.mono[c] | (1ULL << v));
            row[c2 >> 6] ^= 1ULL << (c2 & 63);
          }
        }
      }
    }
    free(G);
    cnt_new = absorb(&S, &X, M.ncols);
    if (rounds < 256) round_new[rounds] = cnt_new;
    rounds++;
    if (cnt_new) productive++; else break;
  }
  int one = 0; for (long i = 0; i < S.r; i++) if (S.pc[i] == M.ncols - 1) one = 1;
  long hist[64] = {0}; for (long i = 0; i < S.r; i++) hist[popc(M.mono[S.pc[i]])]++;
  printf("{\"arm\":\"B-four-russians\",\"task\":\"closure\",\"N\":%d,\"D\":%d,\"ngens\":%d,"
         "\"ncols\":%ld,\"level0_rows\":%ld,\"level0_rejected_degree\":%ld,\"level0_zero\":%ld,"
         "\"level0_rank\":%ld,\"level0_fingerprint\":\"%016llx\",\"dim_W\":%ld,\"codim\":%ld,"
         "\"one_in_W\":%s,\"iterations\":%d,\"rounds_run\":%d,",
         N, D, np, M.ncols, l0_rows, l0_rej, l0_zero, l0_rank, (unsigned long long)fp,
         S.r, M.ncols - S.r, one ? "true" : "false", productive, rounds);
  printf("\"round_new_dims\":["); for (int r = 0; r < rounds && r < 256; r++) printf("%ld%s", round_new[r], r + 1 < rounds && r < 255 ? "," : ""); printf("],");
  print_hist("pivots_by_degree", hist, D);
  printf(",\"seconds\":%.3f,\"peak_rss_kb\":%ld}\n", now_s() - t0, peak_rss_kb());
  return 0;
}

int main(int argc, char **argv) {
  if (argc >= 4 && !strcmp(argv[1], "mac")) return do_mac(argv[2], atoi(argv[3]));
  if (argc >= 4 && !strcmp(argv[1], "closure")) return do_closure(argv[2], atoi(argv[3]));
  fprintf(stderr, "usage: %s mac|closure <gens> <D>\n", argv[0]);
  return 1;
}
