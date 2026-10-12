/* EXP-SEMBIN-79a02d -- GF(2) ARM A: row-insertion Gaussian elimination.
 * Each row is reduced against an echelon basis indexed by pivot column
 * (leading set bit), scanning left to right; a row that survives becomes a
 * new pivot row. Existing basis rows are never modified. M4RI-free.
 *
 *   gf2_armA mac <gens> <D>              Macaulay M_D rank / nrows / pivots
 *   gf2_armA closure <gens> <D> [basis]  iterated degree-D closure W_D
 * Output: one JSON object on stdout.
 */
#include "gf2_common.h"

typedef struct { long ncols; long W; u64 **piv; long rank; } basis_t;

static void basis_init(basis_t *B, long ncols) {
  B->ncols = ncols; B->W = (ncols + 63) / 64; B->rank = 0;
  B->piv = calloc(ncols, sizeof(u64 *));
}

/* returns pivot column of new row, or -1 if row reduced to zero. row is clobbered. */
static long insertA(basis_t *B, u64 *row) {
  long W = B->W, w = 0;
  for (;;) {
    while (w < W && row[w] == 0) w++;
    if (w == W) return -1;
    long c = w * 64 + __builtin_ctzll(row[w]);
    u64 *p = B->piv[c];
    if (p) {
      for (long i = w; i < W; i++) row[i] ^= p[i];
    } else {
      u64 *q = malloc(8 * W); memcpy(q, row, 8 * W);
      B->piv[c] = q; B->rank++; return c;
    }
  }
}

static void print_hist(const char *name, long *h, int D) {
  printf("\"%s\":[", name);
  for (int d = 0; d <= D; d++) printf("%ld%s", h[d], d < D ? "," : "");
  printf("]");
}

static int do_mac(const char *gens, int D) {
  int N; poly_t *P; int np = read_gens(gens, &N, &P);
  double t0 = now_s();
  monidx_t M; monidx_init(&M, N, D);
  basis_t B; basis_init(&B, M.ncols);
  u64 *row = malloc(8 * B.W);
  u64 *occ = calloc(B.W, 8);
  int maxt = 0; for (int i = 0; i < np; i++) if (P[i].nt > maxt) maxt = P[i].nt;
  u64 *buf = malloc(8 * maxt);
  u64 *mults = malloc(8 * (M.ncols + 1));
  long nrows = 0, nnz = 0, zero_products = 0; u64 fp = 0;
  for (int i = 0; i < np; i++) {
    if (P[i].deg > D) continue;
    for (int s = 0; s <= D - P[i].deg; s++) {
      long cnt = 0; enum_combos(N, s, mults, &cnt);
      for (long j = 0; j < cnt; j++) {
        int nt = poly_mul_mono(&P[i], mults[j], buf);
        if (!nt) { zero_products++; continue; }
        nrows++; nnz += nt; fp += row_hash(buf, nt);
        memset(row, 0, 8 * B.W);
        for (int t = 0; t < nt; t++) {
          long c = hget(&M, buf[t]);
          if (c < 0) { fprintf(stderr, "term outside B_<=D\n"); return 3; }
          row[c >> 6] ^= 1ULL << (c & 63);
          occ[c >> 6] |= 1ULL << (c & 63);
        }
        insertA(&B, row);
      }
    }
  }
  long ncols_occ = 0; for (long w = 0; w < B.W; w++) ncols_occ += popc(occ[w]);
  long hist[64] = {0};
  for (long c = 0; c < M.ncols; c++) if (B.piv[c]) hist[popc(M.mono[c])]++;
  printf("{\"arm\":\"A-row-insertion\",\"task\":\"mac\",\"N\":%d,\"D\":%d,\"ngens\":%d,"
         "\"nrows\":%ld,\"ncols_all\":%ld,\"ncols_occurring\":%ld,\"nnz\":%ld,"
         "\"zero_products_dropped\":%ld,\"rank\":%ld,\"fingerprint\":\"%016llx\",",
         N, D, np, nrows, M.ncols, ncols_occ, nnz, zero_products, B.rank, (unsigned long long)fp);
  print_hist("pivots_by_degree", hist, D);
  printf(",\"seconds\":%.3f,\"peak_rss_kb\":%ld}\n", now_s() - t0, peak_rss_kb());
  return 0;
}

static int do_closure(const char *gens, int D, const char *basis_out) {
  int N; poly_t *P; int np = read_gens(gens, &N, &P);
  double t0 = now_s();
  monidx_t M; monidx_init(&M, N, D);
  basis_t B; basis_init(&B, M.ncols);
  long W = B.W;
  u64 *row = malloc(8 * W);
  int maxt = 0; for (int i = 0; i < np; i++) if (P[i].nt > maxt) maxt = P[i].nt;
  u64 *buf = malloc(8 * maxt);
  u64 *mults = malloc(8 * (M.ncols + 1));
  long lowstart = (D >= 1) ? M.degstart[D - 1] : M.ncols;  /* cols >= lowstart have degree <= D-1 */
  long nlow = M.ncols - lowstart;
  /* level 0 */
  long l0_rows = 0, l0_rejected_deg = 0, l0_zero = 0; u64 fp = 0;
  for (int i = 0; i < np; i++) {
    for (int s = 0; s <= D; s++) {
      long cnt = 0; enum_combos(N, s, mults, &cnt);
      for (long j = 0; j < cnt; j++) {
        int nt = poly_mul_mono(&P[i], mults[j], buf);
        if (!nt) { l0_zero++; continue; }
        int ok = 1; for (int t = 0; t < nt; t++) if (popc(buf[t]) > D) { ok = 0; break; }
        if (!ok) { l0_rejected_deg++; continue; }
        l0_rows++; fp += row_hash(buf, nt);
        memset(row, 0, 8 * W);
        for (int t = 0; t < nt; t++) { long c = hget(&M, buf[t]); row[c >> 6] ^= 1ULL << (c & 63); }
        insertA(&B, row);
      }
    }
  }
  long l0_rank = B.rank;
  /* multiplication-by-variable table on the low region */
  long *mv = malloc(sizeof(long) * (size_t)N * (nlow ? nlow : 1));
  for (int v = 0; v < N; v++)
    for (long c = lowstart; c < M.ncols; c++) mv[(long)v * nlow + (c - lowstart)] = hget(&M, M.mono[c] | (1ULL << v));
  char *done = calloc(M.ncols, 1);
  long *todo = malloc(sizeof(long) * (nlow ? nlow : 1));
  int rounds = 0, productive = 0;
  long round_new[256]; long round_rank[256];
  for (;;) {
    long nt = 0;
    for (long c = lowstart; c < M.ncols; c++) if (B.piv[c] && !done[c]) { todo[nt++] = c; done[c] = 1; }
    if (!nt) break;
    long before = B.rank;
    for (long q = 0; q < nt; q++) {
      const u64 *g = B.piv[todo[q]];
      for (int v = 0; v < N; v++) {
        memset(row, 0, 8 * W);
        for (long w = lowstart >> 6; w < W; w++) {
          u64 x = g[w];
          while (x) {
            long c = w * 64 + __builtin_ctzll(x); x &= x - 1;
            long c2 = mv[(long)v * nlow + (c - lowstart)];
            row[c2 >> 6] ^= 1ULL << (c2 & 63);
          }
        }
        insertA(&B, row);
      }
    }
    if (rounds < 256) { round_new[rounds] = B.rank - before; round_rank[rounds] = B.rank; }
    rounds++;
    if (B.rank > before) productive++;
    else break;  /* no new dimension: fixed point (new low rows impossible) */
  }
  int one_in_W = B.piv[M.ncols - 1] != NULL;
  long hist[64] = {0};
  for (long c = 0; c < M.ncols; c++) if (B.piv[c]) hist[popc(M.mono[c])]++;
  if (basis_out) {
    FILE *f = fopen(basis_out, "wb");
    long nc = M.ncols; fwrite(&nc, 8, 1, f); fwrite(&B.rank, 8, 1, f);
    fwrite(M.mono, 8, M.ncols, f);
    for (long c = 0; c < M.ncols; c++) if (B.piv[c]) fwrite(B.piv[c], 8, W, f);
    fclose(f);
  }
  printf("{\"arm\":\"A-row-insertion\",\"task\":\"closure\",\"N\":%d,\"D\":%d,\"ngens\":%d,"
         "\"ncols\":%ld,\"level0_rows\":%ld,\"level0_rejected_degree\":%ld,\"level0_zero\":%ld,"
         "\"level0_rank\":%ld,\"level0_fingerprint\":\"%016llx\",\"dim_W\":%ld,\"codim\":%ld,"
         "\"one_in_W\":%s,\"iterations\":%d,\"rounds_run\":%d,",
         N, D, np, M.ncols, l0_rows, l0_rejected_deg, l0_zero, l0_rank, (unsigned long long)fp,
         B.rank, M.ncols - B.rank, one_in_W ? "true" : "false", productive, rounds);
  printf("\"round_new_dims\":["); for (int r = 0; r < rounds && r < 256; r++) printf("%ld%s", round_new[r], r + 1 < rounds && r < 255 ? "," : ""); printf("],");
  print_hist("pivots_by_degree", hist, D);
  printf(",\"seconds\":%.3f,\"peak_rss_kb\":%ld}\n", now_s() - t0, peak_rss_kb());
  (void)round_rank;
  return 0;
}

int main(int argc, char **argv) {
  if (argc >= 4 && !strcmp(argv[1], "mac")) return do_mac(argv[2], atoi(argv[3]));
  if (argc >= 4 && !strcmp(argv[1], "closure")) return do_closure(argv[2], atoi(argv[3]), argc > 4 ? argv[4] : NULL);
  fprintf(stderr, "usage: %s mac|closure <gens> <D> [basis_out]\n", argv[0]);
  return 1;
}
