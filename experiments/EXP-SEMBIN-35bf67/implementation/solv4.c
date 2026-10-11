/* EXP-SEMBIN-35bf67 -- SOLV4 degree-4 capped closure driver.
 *
 * Shared by both rank arms: system parsing, monomial indexing, Macaulay rows, closure
 * products, and the compact-RREF bookkeeping (column maps, gathers, compaction).
 * All GF(2) elimination arithmetic goes through kernel.h (arm A: M4RI; arm B: own code).
 *
 * Representation. Columns = squarefree monomials of degree <= D in N variables, ordered by
 * degree DESCENDING (degree-D block first ... constant last); within a degree by colex rank.
 * The current row space W is held in reduced row echelon form (RREF, leftmost pivots in
 * that column order) stored compactly: r pivot rows, each kept only on the K = M - r
 * non-pivot columns (its pivot column is implicit). Inserting a chunk X:
 *    X_n ^= X_p * R ;  Y = RREF(X_n) ;  R ^= R[:,Q] * Y ;  drop columns Q ; append Y.
 * RREF of a subspace is unique, so both arms must agree on every intermediate state.
 *
 * Modes:
 *   closure  SYS POINTS|- OUT.json [CH SUB]   SOLV4 closure (D = 4) per OP-R4 / OP-SOLV4
 *   macrank  SYS D T OUT.json [CH SUB]        rank of degree-D Macaulay matrix (T=1: transposed)
 *   calib    m n r inject seed OUT.json [CH SUB]  planted-rank calibration matrix
 */
#include "kernel.h"
#include <immintrin.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/resource.h>
#include <sys/time.h>
#include <time.h>

static double wall0;
static double now(void) {
  struct timeval tv;
  gettimeofday(&tv, NULL);
  return tv.tv_sec + 1e-6 * tv.tv_usec;
}
static void die(const char *m) { fprintf(stderr, "FATAL: %s\n", m); exit(2); }
static size_t even_words(long bits) { size_t w = (bits + 63) / 64; return (w + 1) & ~(size_t)1; }
static void *xalloc(size_t bytes) {
  if (bytes == 0) bytes = 64;
  void *p = aligned_alloc(64, (bytes + 63) & ~(size_t)63);
  if (!p) die("out of memory");
  return p;
}

/* ------------------------------------------------------------------ monomials */
static int NV, DEG;               /* number of variables, degree cap */
static long MCOL;                 /* number of columns */
static long BIN[65][8];           /* binomials C(a, b), b <= 7 */
static long OFF[8];               /* column offset of degree-d block */
static uint64_t *MASK;            /* column -> monomial bitmask */

static void init_monomials(int N, int D) {
  NV = N; DEG = D;
  for (int a = 0; a <= 64; a++)
    for (int b = 0; b < 8; b++)
      BIN[a][b] = (b == 0) ? 1 : (a == 0 ? 0 : BIN[a - 1][b - 1] + BIN[a - 1][b]);
  long o = 0;
  for (int d = D; d >= 0; d--) { OFF[d] = o; o += BIN[N][d]; }
  MCOL = o;
  MASK = (uint64_t *)xalloc(sizeof(uint64_t) * MCOL);
  for (int d = 0; d <= D; d++) {
    /* enumerate d-subsets in colex order */
    int c[8];
    for (int i = 0; i < d; i++) c[i] = i;
    long idx = 0;
    for (;;) {
      uint64_t m = 0;
      for (int i = 0; i < d; i++) m |= (uint64_t)1 << c[i];
      MASK[OFF[d] + idx++] = m;
      if (d == 0) break;
      int i = 0;
      while (i < d - 1 && c[i] + 1 == c[i + 1]) { c[i] = i; i++; }
      c[i]++;
      if (c[d - 1] >= N) break;
    }
    if (idx != BIN[N][d]) die("monomial enumeration");
  }
}

static inline long col_of(uint64_t m) {
  int d = __builtin_popcountll(m);
  if (d > DEG) return -1;
  long r = 0;
  int i = 1;
  while (m) {
    int v = __builtin_ctzll(m);
    r += BIN[v][i++];
    m &= m - 1;
  }
  return OFF[d] + r;
}

/* ------------------------------------------------------------------ system */
static int NEQ;
static int *EQLEN;
static uint64_t **EQ;
static void read_system(const char *path) {
  FILE *f = fopen(path, "r");
  if (!f) die("cannot open system");
  char line[1 << 16];
  int N = -1;
  NEQ = -1;
  while (fgets(line, sizeof line, f)) {
    if (line[0] == '#') continue;
    if (line[0] == 'N') { N = atoi(line + 2); continue; }
    if (line[0] == 'E') { NEQ = atoi(line + 2); break; }
  }
  if (N < 1 || N > 64 || NEQ < 0) die("bad header");
  NV = N;
  EQLEN = (int *)calloc(NEQ, sizeof(int));
  EQ = (uint64_t **)calloc(NEQ, sizeof(uint64_t *));
  for (int e = 0; e < NEQ; e++) {
    int t;
    if (fscanf(f, "%d", &t) != 1) die("bad equation");
    EQLEN[e] = t;
    EQ[e] = (uint64_t *)malloc(sizeof(uint64_t) * (t ? t : 1));
    for (int j = 0; j < t; j++) {
      unsigned long long x;
      if (fscanf(f, "%llx", &x) != 1) die("bad monomial");
      EQ[e][j] = x;
    }
  }
  fclose(f);
}
static int eq_deg(int e) {
  int d = 0;
  for (int j = 0; j < EQLEN[e]; j++) {
    int p = __builtin_popcountll(EQ[e][j]);
    if (p > d) d = p;
  }
  return d;
}

/* ------------------------------------------------------------------ sparse row buffer */
typedef struct { long n, cap; int *rowlen; long *rowoff; int *cols; long ncols_used, ccap; } rowbuf;
static void rb_init(rowbuf *b) { memset(b, 0, sizeof *b); }
static void rb_clear(rowbuf *b) { b->n = 0; b->ncols_used = 0; }
static void rb_push(rowbuf *b, const int *cols, int len) {
  if (b->n == b->cap) {
    b->cap = b->cap ? 2 * b->cap : 1024;
    b->rowlen = (int *)realloc(b->rowlen, sizeof(int) * b->cap);
    b->rowoff = (long *)realloc(b->rowoff, sizeof(long) * b->cap);
  }
  if (b->ncols_used + len > b->ccap) {
    b->ccap = (b->ccap + len) * 2;
    b->cols = (int *)realloc(b->cols, sizeof(int) * b->ccap);
  }
  memcpy(b->cols + b->ncols_used, cols, sizeof(int) * len);
  b->rowlen[b->n] = len;
  b->rowoff[b->n] = b->ncols_used;
  b->ncols_used += len;
  b->n++;
}

/* toggle accumulator for XOR semantics */
static unsigned char *TOG;
static int *TOUCH;
static int NTOUCH;
static inline void tog(long c) {
  if (!TOG[c]) TOUCH[NTOUCH++] = (int)c;
  TOG[c] ^= 1;
}
static int tog_flush(int *out) {
  int n = 0;
  for (int i = 0; i < NTOUCH; i++) {
    int c = TOUCH[i];
    if (TOG[c]) { out[n++] = c; TOG[c] = 0; }
  }
  NTOUCH = 0;
  return n;
}

/* ------------------------------------------------------------------ compact RREF state */
static long M;              /* columns of the current problem */
static long r, K;           /* rank, non-pivot count */
static int *pivcol;         /* row -> original column */
static int *nonpiv;         /* position -> original column (increasing) */
static long *pos;           /* column -> >=0 nonpiv position, <0 : -(row+1) */
static word *R;             /* r x K, stride Rs */
static size_t Rs;
static long Rcap;           /* allocated rows */
static long peak_R_bytes;

static void state_init(long ncols) {
  M = ncols; r = 0; K = ncols;
  pivcol = (int *)malloc(sizeof(int) * (M + 1));
  nonpiv = (int *)malloc(sizeof(int) * (M + 1));
  pos = (long *)malloc(sizeof(long) * (M + 1));
  for (long c = 0; c < M; c++) { nonpiv[c] = (int)c; pos[c] = c; }
  Rs = even_words(K);
  Rcap = 0;
  R = NULL;
}

static inline int getbit(const word *row, long j) { return (row[j >> 6] >> (j & 63)) & 1; }
static inline void flipbit(word *row, long j) { row[j >> 6] ^= (word)1 << (j & 63); }

/* pack the bits of src (nw words) selected by keep[] into dst (zero-filled to dstw words) */
static void pack_row(word *dst, const word *src, const word *keep, int nw, size_t dstw) {
  word acc = 0;
  int nb = 0;
  size_t o = 0;
  for (int w = 0; w < nw; w++) {
    word km = keep[w];
    if (!km) continue;
    word x = _pext_u64(src[w], km);
    int pc = __builtin_popcountll(km);
    acc |= x << nb;
    if (nb + pc >= 64) {
      dst[o++] = acc;
      acc = (nb == 0) ? 0 : (pc - (64 - nb) > 0 ? x >> (64 - nb) : 0);
      nb = nb + pc - 64;
    } else {
      nb += pc;
    }
  }
  if (nb) dst[o++] = acc;
  while (o < dstw) dst[o++] = 0;
}

static double TPH[6]; /* phase timers: scatter, reduce, rref, update, compact, generate */
static word *XP, *XN;     /* chunk buffers */
static size_t XPcap, XNcap;
static int *QP;           /* pivot positions from rref */

/* insert rows [i0, i1) of rb; returns rank increase */
static long insert_rows(rowbuf *b, long i0, long i1) {
  long B = i1 - i0;
  if (B <= 0) return 0;
  size_t Xps = even_words(r), Xns = even_words(K);
  size_t needp = B * Xps, needn = B * Xns;
  if (needp > XPcap) { free(XP); XPcap = needp; XP = (word *)xalloc(sizeof(word) * XPcap); }
  if (needn > XNcap) { free(XN); XNcap = needn; XN = (word *)xalloc(sizeof(word) * XNcap); }
  double tp0 = now();
  memset(XP, 0, sizeof(word) * needp);
  memset(XN, 0, sizeof(word) * needn);
  for (long i = 0; i < B; i++) {
    const int *cols = b->cols + b->rowoff[i0 + i];
    int len = b->rowlen[i0 + i];
    for (int j = 0; j < len; j++) {
      long p = pos[cols[j]];
      if (p >= 0) flipbit(XN + i * Xns, p);
      else flipbit(XP + i * Xps, -p - 1);
    }
  }
  double tp1 = now(); TPH[0] += tp1 - tp0;
  if (r > 0 && K > 0) k_muladd(XN, Xns, (int)B, (int)K, XP, Xps, (int)r, R, Rs);
  double tp2 = now(); TPH[1] += tp2 - tp1;
  if (K == 0) return 0;
  int d = k_rref(XN, Xns, (int)B, (int)K, QP);
  double tp3 = now(); TPH[2] += tp3 - tp2;
  if (d == 0) return 0;
  int nwK = (int)((K + 63) / 64);
  /* keep mask (non-Q columns) and Q mask */
  word *keep = (word *)calloc(nwK + 1, sizeof(word));
  word *qm = (word *)calloc(nwK + 1, sizeof(word));
  for (long j = 0; j < K; j++) keep[j >> 6] |= (word)1 << (j & 63);
  for (int j = 0; j < d; j++) { keep[QP[j] >> 6] &= ~((word)1 << (QP[j] & 63)); qm[QP[j] >> 6] |= (word)1 << (QP[j] & 63); }
  if (r > 0) {
    size_t RQs = even_words(d);
    word *RQ = (word *)xalloc(sizeof(word) * r * RQs);
    for (long i = 0; i < r; i++) pack_row(RQ + i * RQs, R + i * Rs, qm, nwK, RQs);
    k_muladd(R, Rs, (int)r, (int)K, RQ, RQs, d, XN, Xns);
    free(RQ);
  }
  double tp4 = now(); TPH[3] += tp4 - tp3;
  long K2 = K - d;
  size_t Rs2 = even_words(K2);
  /* compact old rows in place (stride shrinks or stays) */
  for (long i = 0; i < r; i++) {
    word tmp[1];
    (void)tmp;
    pack_row(R + i * Rs2, R + i * Rs, keep, nwK, Rs2);
  }
  long need = r + d;
  if (need > Rcap || Rs2 != Rs) {
    long ncap = need > Rcap ? (long)(need * 1.25 + 1024) : Rcap;
    if (ncap > M) ncap = M;
    if (ncap < need) ncap = need;
    word *nR = (word *)realloc(R, sizeof(word) * (size_t)ncap * Rs2 + 64);
    if (!nR) die("realloc R");
    R = nR;
    Rcap = ncap;
  }
  Rs = Rs2;
  for (int j = 0; j < d; j++) pack_row(R + (r + j) * Rs, XN + (size_t)j * Xns, keep, nwK, Rs);
  long bytes = (long)(sizeof(word) * Rcap * Rs);
  if (bytes > peak_R_bytes) peak_R_bytes = bytes;
  /* maps */
  for (int j = 0; j < d; j++) {
    int c = nonpiv[QP[j]];
    pivcol[r + j] = c;
    pos[c] = -(r + j) - 1;
  }
  long o = 0;
  int qi = 0;
  for (long j = 0; j < K; j++) {
    if (qi < d && QP[qi] == j) { qi++; continue; }
    nonpiv[o] = nonpiv[j];
    pos[nonpiv[o]] = o;
    o++;
  }
  if (o != K2) die("compaction count");
  free(keep); free(qm);
  TPH[4] += now() - tp4;
  r += d;
  K = K2;
  return d;
}

/* original-column list of pivot row i */
static int row_cols(long i, int *out) {
  int n = 0;
  out[n++] = pivcol[i];
  const word *row = R + i * Rs;
  long nw = (K + 63) / 64;
  for (long w = 0; w < nw; w++) {
    word x = row[w];
    while (x) {
      int b = __builtin_ctzll(x);
      out[n++] = nonpiv[w * 64 + b];
      x &= x - 1;
    }
  }
  return n;
}

/* ------------------------------------------------------------------ output helpers */
static FILE *OUT;
static long *traj; static long ntraj, trajcap;
static void traj_push(long v) {
  if (ntraj == trajcap) { trajcap = trajcap ? 2 * trajcap : 256; traj = (long *)realloc(traj, sizeof(long) * trajcap); }
  traj[ntraj++] = v;
}
static void print_common_tail(void) {
  struct rusage ru;
  getrusage(RUSAGE_SELF, &ru);
  double cpu = ru.ru_utime.tv_sec + 1e-6 * ru.ru_utime.tv_usec + ru.ru_stime.tv_sec + 1e-6 * ru.ru_stime.tv_usec;
  fprintf(OUT, ",\n \"phase_seconds\": {\"scatter\": %.3f, \"reduce_muladd\": %.3f, \"rref\": %.3f, \"update_muladd\": %.3f, \"compact\": %.3f}",
          TPH[0], TPH[1], TPH[2], TPH[3], TPH[4]);
  fprintf(OUT, ",\n \"chunk_rank_trajectory\": [");
  for (long i = 0; i < ntraj; i++) fprintf(OUT, "%s%ld", i ? "," : "", traj[i]);
  fprintf(OUT, "],\n \"wall_seconds\": %.3f, \"cpu_seconds\": %.3f, \"peak_rss_bytes\": %ld, \"peak_R_bytes\": %ld,\n \"kernel\": \"%s\"\n}\n",
          now() - wall0, cpu, (long)ru.ru_maxrss * 1024L, peak_R_bytes, k_name());
}

/* insert all rows of rb in CH-sized trajectory chunks, SUB-sized kernel calls */
static long CH = 8192, SUB = 8192;
static long target_rank = -1; /* early stop */
static int stopped_early = 0;
static int insert_all(rowbuf *b) {
  for (long i0 = 0; i0 < b->n; i0 += CH) {
    long i1 = i0 + CH < b->n ? i0 + CH : b->n;
    for (long s0 = i0; s0 < i1; s0 += SUB) {
      long s1 = s0 + SUB < i1 ? s0 + SUB : i1;
      insert_rows(b, s0, s1);
    }
    traj_push(r);
    if (target_rank >= 0 && r > target_rank) return -1;
    if (target_rank >= 0 && r == target_rank) { stopped_early = 1; return 1; }
  }
  return 0;
}

/* ------------------------------------------------------------------ Macaulay rows */
static void macaulay_rows(rowbuf *b, int D, long *nzero) {
  int *buf = (int *)malloc(sizeof(int) * (MCOL + 1));
  *nzero = 0;
  for (int e = 0; e < NEQ; e++) {
    int df = eq_deg(e);
    if (df > D) continue;
    for (int md = 0; md <= D - df; md++) {
      for (long ci = OFF[md]; ci < OFF[md] + BIN[NV][md]; ci++) {
        uint64_t mu = MASK[ci];
        for (int j = 0; j < EQLEN[e]; j++) tog(col_of(mu | EQ[e][j]));
        int n = tog_flush(buf);
        if (n) rb_push(b, buf, n); else (*nzero)++;
      }
    }
  }
  free(buf);
}

/* ------------------------------------------------------------------ points / rE */
static int NPTS;
static uint64_t *PTS;
static void read_points(const char *path) {
  NPTS = 0;
  if (!strcmp(path, "-")) return;
  FILE *f = fopen(path, "r");
  if (!f) die("cannot open points");
  int cap = 64;
  PTS = (uint64_t *)malloc(sizeof(uint64_t) * cap);
  unsigned long long x;
  char tok[64];
  while (fscanf(f, "%63s", tok) == 1) {
    if (tok[0] == '#') { int ch; while ((ch = fgetc(f)) != '\n' && ch != EOF); continue; }
    x = strtoull(tok, NULL, 16);
    if (NPTS == cap) { cap *= 2; PTS = (uint64_t *)realloc(PTS, sizeof(uint64_t) * cap); }
    PTS[NPTS++] = x;
  }
  fclose(f);
}
static int point_satisfies(uint64_t p) {
  for (int e = 0; e < NEQ; e++) {
    int par = 0;
    for (int j = 0; j < EQLEN[e]; j++) par ^= ((EQ[e][j] & ~p) == 0);
    if (par) return 0;
  }
  return 1;
}
/* rank of the evaluation map B_{<=D} -> F_2^{NPTS} (rank of NPTS x MCOL matrix) */
static long eval_rank(void) {
  if (NPTS == 0) return 0;
  size_t s = even_words(MCOL);
  word *E = (word *)xalloc(sizeof(word) * s * NPTS);
  memset(E, 0, sizeof(word) * s * NPTS);
  for (int i = 0; i < NPTS; i++)
    for (long c = 0; c < MCOL; c++)
      if ((MASK[c] & ~PTS[i]) == 0) flipbit(E + i * s, c);
  long rk = 0;
  long nw = (MCOL + 63) / 64;
  for (long w = 0; w < nw && rk < NPTS; w++) {
    for (int b = 0; b < 64 && rk < NPTS; b++) {
      int pr = -1;
      for (int i = rk; i < NPTS; i++) if ((E[i * s + w] >> b) & 1) { pr = i; break; }
      if (pr < 0) continue;
      if (pr != rk) for (size_t v = 0; v < s; v++) { word t = E[pr * s + v]; E[pr * s + v] = E[rk * s + v]; E[rk * s + v] = t; }
      for (int i = rk + 1; i < NPTS; i++)
        if ((E[i * s + w] >> b) & 1) for (long v = w; v < nw; v++) E[i * s + v] ^= E[rk * s + v];
      rk++;
    }
  }
  free(E);
  return rk;
}

static uint64_t fnv(uint64_t h, uint64_t x) {
  for (int i = 0; i < 8; i++) { h ^= (x >> (8 * i)) & 0xff; h *= 1099511628211ULL; }
  return h;
}

/* ------------------------------------------------------------------ modes */
static int mode_closure(int argc, char **argv) {
  read_system(argv[2]);
  read_points(argv[3]);
  OUT = fopen(argv[4], "w");
  if (!OUT) die("cannot open out");
  if (argc > 5) CH = atol(argv[5]);
  if (argc > 6) SUB = atol(argv[6]);
  init_monomials(NV, 4);
  TOG = (unsigned char *)calloc(MCOL + 1, 1);
  TOUCH = (int *)malloc(sizeof(int) * (MCOL + 1));
  state_init(MCOL);
  QP = (int *)malloc(sizeof(int) * (SUB + 1));
  long L0 = OFF[3]; /* first column of degree <= 3 */
  int bad_points = 0;
  for (int i = 0; i < NPTS; i++) if (!point_satisfies(PTS[i])) bad_points++;
  long rE = eval_rank();
  if (strcmp(argv[3], "-")) target_rank = MCOL - rE;
  /* low-pivot bookkeeping */
  unsigned char *lowseen = (unsigned char *)calloc(MCOL + 1, 1);
  int *gbuf = (int *)malloc(sizeof(int) * (MCOL + 1));
  int *pbuf = (int *)malloc(sizeof(int) * (MCOL + 1));
  rowbuf b;
  rb_init(&b);
  long nzero = 0;
  macaulay_rows(&b, 4, &nzero);
  long rows0 = b.n;
  fprintf(OUT, "{\n \"mode\": \"closure\", \"N\": %d, \"M_le4\": %ld, \"L0\": %ld, \"equations\": %d, \"rows0\": %ld, \"rows0_zero_products\": %ld,\n",
          NV, MCOL, L0, NEQ, rows0, nzero);
  fprintf(OUT, " \"points_given\": %d, \"points_failing_system\": %d, \"eval_rank_rE\": %ld, \"target_rank\": %ld,\n",
          NPTS, bad_points, rE, target_rank);
  fprintf(OUT, " \"rounds\": [");
  int status = insert_all(&b);
  long total_rows = b.n;
  int round = 0, last_increasing_round = 0;
  long rank_before = 0;
  fprintf(OUT, "\n  {\"round\": 0, \"rows\": %ld, \"rank_after\": %ld, \"new_low\": 0, \"digest\": \"-\"}", b.n, r);
  rank_before = r;
  while (status == 0) {
    /* new low rows at end of this round */
    rb_clear(&b);
    long nnew = 0;
    uint64_t h = 1469598103934665603ULL;
    /* collect new low pivot rows sorted by pivot column */
    long *newrows = (long *)malloc(sizeof(long) * (r + 1));
    for (long i = 0; i < r; i++)
      if (pivcol[i] >= L0 && !lowseen[pivcol[i]]) newrows[nnew++] = i;
    /* sort by pivot column */
    for (long a = 1; a < nnew; a++) {
      long x = newrows[a]; long j = a - 1;
      while (j >= 0 && pivcol[newrows[j]] > pivcol[x]) { newrows[j + 1] = newrows[j]; j--; }
      newrows[j + 1] = x;
    }
    if (nnew == 0) { free(newrows); break; } /* fixpoint */
    round++;
    long emitted = 0;
    /* snapshot the new low rows as they stand at the end of the previous round (OP-R4) */
    long LW = MCOL - L0;
    size_t gs = even_words(LW);
    word *snap = (word *)xalloc(sizeof(word) * gs * nnew);
    memset(snap, 0, sizeof(word) * gs * nnew);
    for (long a = 0; a < nnew; a++) {
      int gl = row_cols(newrows[a], gbuf);
      for (int j = 0; j < gl; j++) {
        if (gbuf[j] < L0) die("low row has a high column");
        flipbit(snap + a * gs, gbuf[j] - L0);
      }
      lowseen[pivcol[newrows[a]]] = 1;
    }
    for (long a = 0; a < nnew; a++) {
      int gl = 0;
      const word *sr = snap + a * gs;
      for (size_t w = 0; w < gs; w++) {
        word x = sr[w];
        while (x) { gbuf[gl++] = (int)(L0 + w * 64 + __builtin_ctzll(x)); x &= x - 1; }
      }
      h = fnv(h, (uint64_t)gl);
      for (int j = 0; j < gl; j++) h = fnv(h, (uint64_t)gbuf[j]);
      for (int v = 0; v < NV; v++) {
        uint64_t bitv = (uint64_t)1 << v;
        for (int j = 0; j < gl; j++) tog(col_of(MASK[gbuf[j]] | bitv));
        int n = tog_flush(pbuf);
        if (n) { rb_push(&b, pbuf, n); emitted++; }
      }
      /* flush in CH batches to bound memory */
      if (b.n >= CH * 4 || a == nnew - 1) {
        total_rows += b.n;
        status = insert_all(&b);
        rb_clear(&b);
        if (status != 0) break; /* early stop (fixpoint certified) or inconsistency */
      }
    }
    free(snap);
    free(newrows);
    if (r > rank_before) last_increasing_round = round;
    fprintf(OUT, ",\n  {\"round\": %d, \"rows\": %ld, \"rank_after\": %ld, \"new_low\": %ld, \"digest\": \"%016llx\"}",
            round, emitted, r, nnew, (unsigned long long)h);
    fflush(OUT);
    rank_before = r;
  }
  int solv4 = -1; /* -1: undetermined (no points file) */
  const char *verdict;
  if (status < 0) verdict = "rank_exceeds_target_INCONSISTENT";
  else if (target_rank < 0) verdict = "no_points_file";
  else if (r == target_rank && rE == NPTS) { verdict = "SOLV4"; solv4 = 1; }
  else if (r == target_rank) { verdict = "fixpoint_at_target_but_rE_lt_s"; solv4 = 0; }
  else { verdict = "NOT_SOLV4"; solv4 = 0; }
  fprintf(OUT, "\n ],\n \"dim_R4\": %ld, \"closure_round_count\": %d, \"product_rounds_run\": %d, \"stopped_early\": %d,\n",
          r, last_increasing_round, round, stopped_early);
  fprintf(OUT, " \"total_rows_inserted\": %ld, \"s_given\": %d, \"solv4\": %d, \"verdict\": \"%s\", \"M_minus_dim\": %ld",
          total_rows, NPTS, solv4, verdict, MCOL - r);
  print_common_tail();
  fclose(OUT);
  return 0;
}

static int mode_macrank(int argc, char **argv) {
  read_system(argv[2]);
  int D = atoi(argv[3]);
  int T = atoi(argv[4]);
  OUT = fopen(argv[5], "w");
  if (argc > 6) CH = atol(argv[6]);
  if (argc > 7) SUB = atol(argv[7]);
  init_monomials(NV, D);
  TOG = (unsigned char *)calloc(MCOL + 1, 1);
  TOUCH = (int *)malloc(sizeof(int) * (MCOL + 1));
  rowbuf b;
  rb_init(&b);
  long nzero = 0;
  macaulay_rows(&b, D, &nzero);
  /* support columns */
  long *cnt = (long *)calloc(MCOL + 1, sizeof(long));
  for (long i = 0; i < b.ncols_used; i++) cnt[b.cols[i]]++;
  long ncols = 0;
  for (long c = 0; c < MCOL; c++) if (cnt[c]) ncols++;
  fprintf(OUT, "{\n \"mode\": \"macrank\", \"N\": %d, \"D\": %d, \"transposed\": %d, \"nrows\": %ld, \"ncols_support\": %ld, \"zero_products\": %ld, \"nnz\": %ld",
          NV, D, T, b.n, ncols, nzero, b.ncols_used);
  QP = (int *)malloc(sizeof(int) * (SUB + 1));
  if (!T) {
    /* compress to support columns */
    long *cmap = (long *)malloc(sizeof(long) * (MCOL + 1));
    long o = 0;
    for (long c = 0; c < MCOL; c++) cmap[c] = cnt[c] ? o++ : -1;
    for (long i = 0; i < b.ncols_used; i++) b.cols[i] = (int)cmap[b.cols[i]];
    state_init(ncols);
    insert_all(&b);
  } else {
    /* transpose: rows of A^T = support columns of A (in column order) */
    rowbuf t;
    rb_init(&t);
    long *start = (long *)calloc(MCOL + 2, sizeof(long));
    for (long c = 0; c < MCOL; c++) start[c + 1] = start[c] + cnt[c];
    int *tc = (int *)malloc(sizeof(int) * (b.ncols_used + 1));
    long *fill = (long *)calloc(MCOL + 1, sizeof(long));
    for (long i = 0; i < b.n; i++)
      for (int j = 0; j < b.rowlen[i]; j++) {
        int c = b.cols[b.rowoff[i] + j];
        tc[start[c] + fill[c]++] = (int)i;
      }
    long nrowsA = b.n;
    free(b.cols); free(b.rowlen); free(b.rowoff);
    t.n = 0;
    t.cap = ncols;
    t.rowlen = (int *)malloc(sizeof(int) * (ncols + 1));
    t.rowoff = (long *)malloc(sizeof(long) * (ncols + 1));
    t.cols = tc;
    t.ncols_used = start[MCOL];
    for (long c = 0; c < MCOL; c++)
      if (cnt[c]) { t.rowlen[t.n] = (int)cnt[c]; t.rowoff[t.n] = start[c]; t.n++; }
    state_init(nrowsA);
    insert_all(&t);
  }
  fprintf(OUT, ",\n \"rank\": %ld", r);
  print_common_tail();
  fclose(OUT);
  return 0;
}

/* xorshift64* deterministic generator (calibration only) */
static uint64_t rs;
static uint64_t rnd(void) { rs ^= rs >> 12; rs ^= rs << 25; rs ^= rs >> 27; return rs * 2685821657736338717ULL; }

static int mode_calib(int argc, char **argv) {
  long m = atol(argv[2]), n = atol(argv[3]), rk = atol(argv[4]);
  int inject = atoi(argv[5]);
  rs = strtoull(argv[6], NULL, 10) * 0x9E3779B97F4A7C15ULL + 1;
  OUT = fopen(argv[7], "w");
  if (argc > 8) CH = atol(argv[8]);
  if (argc > 9) SUB = atol(argv[9]);
  size_t s = even_words(n);
  word *base = (word *)xalloc(sizeof(word) * s * rk);
  memset(base, 0, sizeof(word) * s * rk);
  for (long i = 0; i < rk; i++)
    for (long c = 0; c < n; c++) if (rnd() >> 63) flipbit(base + i * s, c);
  if (inject) /* base row 0 := base row 1 xor base row 2 -> planted rank rk - 1 */
    for (size_t w = 0; w < s; w++) base[w] = base[s + w] ^ base[2 * s + w];
  rowbuf b;
  rb_init(&b);
  int *buf = (int *)malloc(sizeof(int) * (n + 1));
  word *tmp = (word *)xalloc(sizeof(word) * s);
  for (long i = 0; i < m; i++) {
    if (i < rk) memcpy(tmp, base + i * s, sizeof(word) * s);
    else {
      memset(tmp, 0, sizeof(word) * s);
      for (int t = 0; t < 3; t++) { long j = rnd() % rk; for (size_t w = 0; w < s; w++) tmp[w] ^= base[j * s + w]; }
    }
    int len = 0;
    for (long c = 0; c < n; c++) if (getbit(tmp, c)) buf[len++] = (int)c;
    rb_push(&b, buf, len);
  }
  /* deterministic shuffle of row order */
  for (long i = m - 1; i > 0; i--) {
    long j = rnd() % (i + 1);
    long t1 = b.rowoff[i]; b.rowoff[i] = b.rowoff[j]; b.rowoff[j] = t1;
    int t2 = b.rowlen[i]; b.rowlen[i] = b.rowlen[j]; b.rowlen[j] = t2;
  }
  QP = (int *)malloc(sizeof(int) * (SUB + 1));
  state_init(n);
  insert_all(&b);
  fprintf(OUT, "{\n \"mode\": \"calib\", \"m\": %ld, \"n\": %ld, \"planted_rank\": %ld, \"inject\": %d, \"seed\": \"%s\", \"rank\": %ld",
          m, n, inject ? rk - 1 : rk, inject, argv[6], r);
  print_common_tail();
  fclose(OUT);
  return 0;
}

int main(int argc, char **argv) {
  wall0 = now();
  if (argc < 2) die("usage");
  if (!strcmp(argv[1], "closure") && argc >= 5) return mode_closure(argc, argv);
  if (!strcmp(argv[1], "macrank") && argc >= 6) return mode_macrank(argc, argv);
  if (!strcmp(argv[1], "calib") && argc >= 8) return mode_calib(argc, argv);
  die("usage: closure SYS POINTS OUT [CH SUB] | macrank SYS D T OUT [CH SUB] | calib m n r inject seed OUT [CH SUB]");
  return 1;
}
