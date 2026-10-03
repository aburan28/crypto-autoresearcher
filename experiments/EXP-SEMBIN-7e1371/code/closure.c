/* closure.c -- degree-capped Boolean closure over GF(2) with M4RI.
 *
 * Object: the Boolean ring B = F_2[x_0..x_{N-1}]/(x_i^2 - x_i); monomials are
 * squarefree and stored as 64-bit masks (N <= 62).  Columns are the squarefree
 * monomials of degree <= D in graded reverse lexicographic order, largest first:
 * degree descending, and within a degree the smaller mask is the LARGER monomial
 * (for squarefree monomials with x_0 > x_1 > ... this is exactly grevlex).  A
 * fully reduced echelon form therefore has each row's first set column as its
 * leading monomial.
 *
 * closure_run computes W_D, the smallest subspace of B_{<=D} that contains the
 * generators and is closed under f -> mu*f for every squarefree monomial mu with
 * deg(mu) + deg(f) <= D (the degree measured in the polynomial ring, i.e. before
 * Boolean reduction, which is what an F4 pair of that degree would form).  With
 * max_iter = 1 it computes instead the ordinary degree-D Macaulay matrix of the
 * generators alone (no re-multiplication of new rows), which is the GOAL-DREG-001
 * statistic.
 *
 * Exact arithmetic; deterministic; single-threaded; no randomness anywhere.
 */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <m4ri/m4ri.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <time.h>
#include <unistd.h>

typedef uint64_t u64;

static int N_ = 0, D_ = 0;
static long ncols_ = 0;
static u64 *col_mask_ = NULL;      /* column -> mask */
static long *deg_off_ = NULL;      /* deg_off_[d] = first column of degree d block, deg_off_[D+1] = ncols */
static mzd_t *B_ = NULL;           /* current basis, rank_ rows in RREF */
static long rank_ = 0;
static char *is_pivot_ = NULL;     /* per column */
static char *pivot_new_ = NULL;    /* per column: pivot first appeared in the current iteration */
static char *row_new_ = NULL;      /* per basis row: 1 if produced since last multiplication */
static long *lm_col_ = NULL;       /* per basis row: leading column */
static int verbose_ = -1;

static int verbose(void) {
    if (verbose_ < 0) verbose_ = getenv("CLOSURE_VERBOSE") ? 1 : 0;
    return verbose_;
}

static double now_sec(void) {
    struct timespec ts; clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}

static int popc(u64 x) { return __builtin_popcountll(x); }

/* polynomial-ring degree of a polynomial given as masks: its largest monomial degree */
static int poly_deg(const u64 *masks, long cnt) {
    int d = 0;
    for (long i = 0; i < cnt; i++) if (popc(masks[i]) > d) d = popc(masks[i]);
    return d;
}

static int cmp_u64(const void *a, const void *b) {
    u64 x = *(const u64 *)a, y = *(const u64 *)b;
    return (x < y) ? -1 : (x > y);
}

/* enumerate all masks of degree exactly d over N variables, ascending */
static long gen_masks_deg(int N, int d, u64 *out) {
    long cnt = 0;
    if (d == 0) { out[0] = 0; return 1; }
    /* Gosper's hack over N-bit words */
    u64 x = (d >= 64) ? 0 : ((1ULL << d) - 1);
    u64 lim = (N >= 64) ? ~0ULL : (1ULL << N);
    while (x < lim) {
        out[cnt++] = x;
        u64 c = x & -x, r = x + c;
        x = (((r ^ x) >> 2) / c) | r;
        if (c == 0) break;
    }
    return cnt;
}

static void setup_columns(int N, int D) {
    N_ = N; D_ = D;
    free(col_mask_); free(deg_off_);
    deg_off_ = calloc(D + 2, sizeof(long));
    /* count */
    long total = 0;
    long *cnt = calloc(D + 1, sizeof(long));
    for (int d = 0; d <= D; d++) {
        /* binomial */
        long c = 1;
        for (int i = 0; i < d; i++) c = c * (N - i) / (i + 1);
        cnt[d] = c; total += c;
    }
    col_mask_ = malloc(sizeof(u64) * (total ? total : 1));
    long pos = 0;
    for (int d = D; d >= 0; d--) {   /* descending degree */
        deg_off_[d] = pos;
        long got = gen_masks_deg(N, d, col_mask_ + pos);
        if (got != cnt[d]) { fprintf(stderr, "closure: count mismatch d=%d %ld vs %ld\n", d, got, cnt[d]); }
        pos += got;
    }
    deg_off_[D + 1] = pos;
    /* deg_off_ was filled descending: deg_off_[D] = 0 ... deg_off_[0] = last block; fix so deg_off_[d] is start of block d and block d+... */
    /* Blocks are laid out D, D-1, ..., 0; deg_off_[d] currently = start of block d; block d ends at start of block d-1, or pos for d = 0. */
    long *fixed = calloc(D + 2, sizeof(long));
    for (int d = 0; d <= D; d++) fixed[d] = deg_off_[d];
    fixed[D + 1] = pos;
    /* We need, for binary search, [start,end) of block d: start = deg_off_[d], end = (d == 0) ? pos : deg_off_[d-1]. Store end in a separate array. */
    free(deg_off_);
    deg_off_ = calloc(2 * (D + 2), sizeof(long));
    for (int d = 0; d <= D; d++) { deg_off_[d] = fixed[d]; }
    deg_off_[D + 1] = pos;
    free(fixed); free(cnt);
    ncols_ = pos;
}

/* [start, end) of degree-d block */
static inline long blk_start(int d) { return deg_off_[d]; }
static inline long blk_end(int d) { return (d == 0) ? ncols_ : deg_off_[d - 1]; }

/* COLUMN ORDER IS DESCENDING BY DEGREE: block D starts at index 0 and degree 0
 * (the constant monomial 1) is the LAST column, which is why contains_one is
 * is_pivot_[ncols_ - 1]. Consequence, easy to get backwards and worth stating:
 * a row's leading monomial under this order is its HIGHEST-degree term, so
 * bounding a multiplier by D - deg(leading) keeps the whole product inside
 * degree D and write_product never needs to truncate. A reader who assumes an
 * ascending order concludes the opposite and blames truncation for anything
 * that goes wrong; that mistake has already been made once and published. */
static long col_of2(u64 m) {
    int d = popc(m);
    if (d > D_) return -1;
    long lo = blk_start(d), hi = blk_end(d) - 1;
    while (lo <= hi) {
        long mid = (lo + hi) >> 1;
        if (col_mask_[mid] == m) return mid;
        if (col_mask_[mid] < m) lo = mid + 1; else hi = mid - 1;
    }
    return -1;
}

/* read row i of matrix M as masks; returns count; buf must hold ncols entries */
static long row_masks(const mzd_t *M, long i, u64 *buf) {
    long cnt = 0;
    const word *r = mzd_row((mzd_t *)M, (rci_t)i);
    long nw = (M->ncols + 63) / 64;
    for (long w = 0; w < nw; w++) {
        word x = r[w];
        while (x) {
            int b = __builtin_ctzll(x);
            long j = w * 64 + b;
            if (j < M->ncols) buf[cnt++] = col_mask_[j];
            x &= x - 1;
        }
    }
    return cnt;
}

static long first_col(const mzd_t *M, long i) {
    const word *r = mzd_row((mzd_t *)M, (rci_t)i);
    long nw = (M->ncols + 63) / 64;
    for (long w = 0; w < nw; w++) {
        if (r[w]) { long j = w * 64 + __builtin_ctzll(r[w]); return (j < M->ncols) ? j : -1; }
    }
    return -1;
}

/* write product (mu * row given as masks) into row r of M, cancelling mod 2 */
/* Elimination entry point. Every echelonization in this file goes through ech()
 * so the routine can be swapped or cross-checked at build time:
 *   default            mzd_echelonize_pluq(M, 1): PLUQ throughout.
 *   -DECH_LEGACY       mzd_echelonize(M, 1): Four Russians, switching to PLE once
 *                      the trailing block passes density 0.15 (echelonform.h).
 *                      This was the default for RUN-SEMBIN-9bb990. With M4RI
 *                      0.0.20200125 it is UNSOUND on (43,2,2,22) N=44: under
 *                      -DECH_EVALCHECK its second elimination (199768 x 149986)
 *                      takes 0 rows not vanishing at a verified common zero and
 *                      returns 68559 that do, rank 139898 where PLUQ gives
 *                      129376 with 0 bad rows. Kept only to reproduce that run.
 *   -DECH_PURE_M4RI    mzd_echelonize_m4ri(M, 1, 0) only, never PLE
 *   -DECH_CROSSCHECK   runs the default AND pure Four Russians on a copy and
 *                      compares the two RREFs; RREF is unique for a row space,
 *                      so any difference is an error in one of them. Doubles
 *                      the memory of each elimination.
 * closure_ech_stats() reports calls, disagreements and the first bad call. */
static long ech_calls_ = 0, ech_mismatch_ = 0, ech_first_bad_ = -1;
void closure_ech_stats(long *calls, long *mismatch, long *first_bad) {
    if (calls) *calls = ech_calls_;
    if (mismatch) *mismatch = ech_mismatch_;
    if (first_bad) *first_bad = ech_first_bad_;
}
void closure_ech_reset(void) { ech_calls_ = 0; ech_mismatch_ = 0; ech_first_bad_ = -1; }

/* -DECH_EVALCHECK: a known common zero of the generators (set by
 * closure_set_witness) is a linear functional that every element of the ideal
 * vanishes on, and elimination only takes linear combinations. So in every
 * call the rows going IN must all vanish at it, and so must the rows coming
 * OUT. A non-vanishing row before elimination blames the product code; one
 * that appears only after blames the elimination routine. One pass over the
 * nonzeros per call, no second matrix -- unlike ECH_CROSSCHECK. */
/* ECH_EVALCHECK only: which routine does the elimination, chosen at run time so
 * one build can test all three on the same matrices.
 * 0 = mzd_echelonize (legacy: Four Russians, hands off to PLE past density
 *     0.15); 1 = mzd_echelonize_pluq (PLUQ throughout, the default);
 *     2 = mzd_echelonize_m4ri (Four Russians throughout, never PLE). */
static int ech_method_ = 1;
void closure_set_method(int m) { ech_method_ = m; }
static u64 witness_ = 0;
static int witness_set_ = 0;
void closure_set_witness(u64 assign) { witness_ = assign; witness_set_ = 1; }

__attribute__((unused)) static long rows_not_vanishing(const mzd_t *M, rci_t upto, long *first) {
    long bad = 0;
    *first = -1;
    for (rci_t i = 0; i < upto; i++) {
        const word *r = mzd_row((mzd_t *)M, i);
        int v = 0;
        for (wi_t w = 0; w < M->width; w++) {
            word x = r[w];
            while (x) {
                int b = __builtin_ctzll(x);
                long j = (long)w * 64 + b;
                if (j < M->ncols && (col_mask_[j] & witness_) == col_mask_[j]) v ^= 1;
                x &= x - 1;
            }
        }
        if (v) { if (bad == 0) *first = i; bad++; }
    }
    return bad;
}

/* Structural check of every elimination's output, always on. ech(M, full)
 * must leave rows 0..r-1 in REDUCED row echelon form -- leading columns
 * strictly increasing, and each pivot column zero in every other row -- and
 * rows r.. zero. M4RI 0.0.20200125's mzd_echelonize_pluq returned a 148601 x
 * 149986 output at (43,2,2,22) N=44 claiming rank 139204 with only 131030
 * distinct leading columns; the run went on to a verdict. Any violation now
 * counts as a fault and closure_run stops with an error instead. Costs one
 * pass over the matrix, small beside the elimination. It cannot see a wrong
 * matrix that is still well formed: that is what ECH_EVALCHECK is for. */
static long ech_faults_ = 0;
long closure_ech_faults(void) { return ech_faults_; }
static int ech_output_ok(const mzd_t *M, rci_t r) {
    long nw = M->width;
    word tail = (M->ncols & 63) ? ((1ULL << (M->ncols & 63)) - 1) : ~0ULL;
    u64 *pm = calloc(nw ? nw : 1, sizeof(u64));
    long *lm = malloc(sizeof(long) * (r ? r : 1));
    long prev = -1;
    int ok = 1;
    for (rci_t i = 0; ok && i < r; i++) {
        const word *row = mzd_row((mzd_t *)M, i);
        long fc = -1;
        for (long w = 0; w < nw; w++) {
            word x = row[w]; if (w == nw - 1) x &= tail;
            if (x) { fc = w * 64 + __builtin_ctzll(x); break; }
        }
        if (fc < 0 || fc <= prev) { ok = 0; fprintf(stderr, "[ech check] row %d: leading column %ld after %ld\n", (int)i, fc, prev); break; }
        lm[i] = prev = fc;
        pm[fc >> 6] |= 1ULL << (fc & 63);
    }
    for (rci_t i = 0; ok && i < r; i++) {
        const word *row = mzd_row((mzd_t *)M, i);
        for (long w = 0; w < nw; w++) {
            word expect = ((lm[i] >> 6) == w) ? (1ULL << (lm[i] & 63)) : 0;
            if ((row[w] & pm[w]) != expect) { ok = 0; fprintf(stderr, "[ech check] row %d not reduced\n", (int)i); break; }
        }
    }
    for (rci_t i = r; ok && i < M->nrows; i++) {
        const word *row = mzd_row((mzd_t *)M, i);
        for (long w = 0; w < nw; w++) {
            word x = row[w]; if (w == nw - 1) x &= tail;
            if (x) { ok = 0; fprintf(stderr, "[ech check] row %d beyond rank %d is nonzero\n", (int)i, (int)r); break; }
        }
    }
    free(pm); free(lm);
    return ok;
}

static rci_t ech(mzd_t *M) {
#if defined(ECH_CROSSCHECK)
    mzd_t *C = mzd_copy(NULL, M);
    rci_t r1 = mzd_echelonize(M, 1);
    rci_t r2 = mzd_echelonize_m4ri(C, 1, 0);
    int same = (r1 == r2);
    for (rci_t i = 0; i < r1 && same; i++) {
        const word *a = mzd_row(M, i), *b = mzd_row(C, i);
        for (wi_t w = 0; w < M->width; w++) {
            word x = a[w] ^ b[w];
            if (w == M->width - 1) x &= M->high_bitmask;
            if (x) { same = 0; break; }
        }
    }
    /* Report on the spot, so a run killed before it finishes still leaves the
     * evidence behind: one line per elimination, flushed immediately. */
    fprintf(stderr, "[ech %ld] %d x %d  rank default=%d m4ri=%d  %s\n",
            ech_calls_, (int)M->nrows, (int)M->ncols, (int)r1, (int)r2,
            same ? "agree" : "*** RREF DISAGREES ***");
    fflush(stderr);
    if (!same) { ech_mismatch_++; if (ech_first_bad_ < 0) ech_first_bad_ = ech_calls_; }
    mzd_free(C);
#elif defined(ECH_EVALCHECK)
    long fin = -1, fout = -1;
    long bin = witness_set_ ? rows_not_vanishing(M, M->nrows, &fin) : -1;
    rci_t r1 = ech_method_ == 1 ? mzd_echelonize_pluq(M, 1)
             : ech_method_ == 2 ? mzd_echelonize_m4ri(M, 1, 0)
             : mzd_echelonize(M, 1);
    long bout = witness_set_ ? rows_not_vanishing(M, r1, &fout) : -1;
    fprintf(stderr, "[ech %ld %s] %d x %d rank %d | rows not vanishing at the zero: in=%ld out=%ld%s\n",
            ech_calls_, ech_method_ == 1 ? "pluq" : ech_method_ == 2 ? "m4ri" : "default", (int)M->nrows, (int)M->ncols, (int)r1, bin, bout,
            (bin == 0 && bout > 0) ? "  *** ELIMINATION LEFT THE IDEAL ***" :
            (bin > 0) ? "  *** PRODUCTS ALREADY OUTSIDE THE IDEAL ***" : "");
    fflush(stderr);
    if (bout > 0 || bin > 0) { ech_mismatch_++; if (ech_first_bad_ < 0) ech_first_bad_ = ech_calls_; }
#elif defined(ECH_PURE_M4RI)
    rci_t r1 = mzd_echelonize_m4ri(M, 1, 0);
#elif defined(ECH_LEGACY)
    rci_t r1 = mzd_echelonize(M, 1);
#else
    rci_t r1 = mzd_echelonize_pluq(M, 1);
#endif
    if (!ech_output_ok(M, r1)) {
        ech_faults_++;
        fprintf(stderr, "[ech check] call %ld (%d x %d, rank %d): output NOT in reduced echelon form\n",
                ech_calls_, (int)M->nrows, (int)M->ncols, (int)r1);
        r1 = -1;   /* callers treat a negative rank as an instrument fault */
    }
    ech_calls_++;
    return r1;
}

/* The M4RI shared object actually loaded, resolved at run time from the address
 * of mzd_init (its file name carries the release, e.g. libm4ri-0.0.20240729.so).
 * Recorded with every result: 0.0.20200125 lacks upstream commit 34b1b56
 * (2020-05-14, "fix count for remaining number of rows in a block", M4RI issue
 * #74), which corrects row windows into multi-block matrices -- the regime of
 * every elimination found unsound here. */
const char *closure_m4ri_library(void) {
    static char buf[4096];
    Dl_info info;
    if (dladdr((void *)&mzd_init, &info) && info.dli_fname) {
        char *rp = realpath(info.dli_fname, NULL);
        snprintf(buf, sizeof buf, "%s", rp ? rp : info.dli_fname);
        free(rp);
    } else snprintf(buf, sizeof buf, "unknown");
    return buf;
}

/* Which routine ech() runs in this build, recorded in every result so a
 * verdict always says what produced it. */
const char *closure_elimination(void) {
#if defined(ECH_CROSSCHECK)
    return "mzd_echelonize+crosscheck_m4ri";
#elif defined(ECH_EVALCHECK)
    return ech_method_ == 1 ? "mzd_echelonize_pluq+evalcheck"
         : ech_method_ == 2 ? "mzd_echelonize_m4ri+evalcheck" : "mzd_echelonize+evalcheck";
#elif defined(ECH_PURE_M4RI)
    return "mzd_echelonize_m4ri";
#elif defined(ECH_LEGACY)
    return "mzd_echelonize";
#else
    return "mzd_echelonize_pluq";
#endif
}

/* DIAGNOSTIC: counts product terms whose degree exceeded D and were therefore
 * dropped by the col_of2 lookup below. A nonzero count means the row written is
 * a TRUNCATION of mu * g rather than mu * g itself, which is not an element of
 * the ideal -- so the row space can exceed the true degree-D slice and 1 can
 * appear spuriously. Purely observational; behaviour is unchanged. */
static long long dropped_terms_ = 0;
long long closure_dropped_terms(void) { return dropped_terms_; }
void closure_reset_dropped(void) { dropped_terms_ = 0; }

static void write_product(mzd_t *M, long r, const u64 *masks, long cnt, u64 mu, u64 *tmp) {
    for (long i = 0; i < cnt; i++) tmp[i] = masks[i] | mu;
    qsort(tmp, cnt, sizeof(u64), cmp_u64);
    long i = 0;
    while (i < cnt) {
        long j = i;
        while (j < cnt && tmp[j] == tmp[i]) j++;
        if ((j - i) & 1) {
            long c = col_of2(tmp[i]);
            if (c >= 0) mzd_write_bit(M, (rci_t)r, (rci_t)c, 1);
            else dropped_terms_++;
        }
        i = j;
    }
}

/* After a full echelonization of M (rank rk), install rows [0, rk) as the new basis.
 * Marks rows whose pivot was not previously a pivot as new. */
static void install_basis(mzd_t *M, long rk) {
    if (B_) { mzd_free(B_); B_ = NULL; }
    B_ = mzd_init((rci_t)(rk ? rk : 1), (rci_t)ncols_);
    free(row_new_); free(lm_col_);
    row_new_ = calloc(rk ? rk : 1, 1);
    lm_col_ = calloc(rk ? rk : 1, sizeof(long));
    for (long i = 0; i < rk; i++) {
        mzd_copy_row(B_, (rci_t)i, M, (rci_t)i);
        long fc = first_col(M, i);
        lm_col_[i] = fc;
        if (fc >= 0 && !is_pivot_[fc]) { row_new_[i] = 1; pivot_new_[fc] = 1; }
        else if (fc >= 0 && pivot_new_[fc]) { row_new_[i] = 1; }
    }
    for (long i = 0; i < rk; i++) if (lm_col_[i] >= 0) is_pivot_[lm_col_[i]] = 1;
    rank_ = rk;
}

void closure_free(void) {
    if (B_) { mzd_free(B_); B_ = NULL; }
    free(col_mask_); col_mask_ = NULL;
    free(deg_off_); deg_off_ = NULL;
    free(is_pivot_); is_pivot_ = NULL;
    free(pivot_new_); pivot_new_ = NULL;
    free(row_new_); row_new_ = NULL;
    free(lm_col_); lm_col_ = NULL;
    rank_ = 0; ncols_ = 0;
}

/* Largest batch b of products whose elimination fits mem_cap_bytes, given the
 * basis rank at the moment S is built and nm_rows rows held in NM. Resident
 * during ech(S): B_ (rank rows) + S (rank + b) + NM + PLUQ's ~r^2/8 workspace;
 * during install_basis (B_ freed first): S + the new basis (r rows) + NM, with
 * r <= min(ncols, rank + b). The need is increasing in b, so bisect. */
__attribute__((unused)) static long batch_for(long rank, long nm_rows, double per_row, double mem_cap_bytes) {
    long lo = 0, hi = (long)(mem_cap_bytes / per_row) + 1;
    while (lo < hi) {
        long mid = lo + (hi - lo + 1) / 2;
        double r = (double)((rank + mid < ncols_) ? rank + mid : ncols_);
        double ech_phase = (double)rank * per_row + r * r / 8.0;
        double inst_phase = r * per_row;
        double need = ((double)rank + (double)mid + (double)nm_rows) * per_row
                    + (ech_phase > inst_phase ? ech_phase : inst_phase);
        if (need <= mem_cap_bytes) lo = mid; else hi = mid - 1;
    }
    return lo;
}

/* ---- checkpoint / resume (opt-in: environment variable CLOSURE_CKPT_DIR) ----
 * A long closure (N = 44, D = 4: hours per iteration) outlives the container it
 * runs in. With CLOSURE_CKPT_DIR set, the state is written after every batch and
 * a later call on the SAME system (hash of N, D and the generators) resumes at
 * the exact product cursor, so it builds the same matrices an uninterrupted run
 * would. Multi-iteration closures in non-legacy builds only; the single-level
 * statistic is one iteration and is never checkpointed.
 * Files are named by the system hash H (16 hex digits), so closures of different
 * systems -- including the D = 2 and D = 3 closures run_cert re-runs before a
 * resumed D = 4 one -- never touch each other's state (a single ckpt.bin let
 * them overwrite, then delete, a D = 4 checkpoint).
 *   ckpt.H.bin  cursor, history, flags, and the basis. B_ is in reduced row
 *             echelon form, so each row is its pivot plus its bits on the
 *             NON-pivot columns; only those are stored (N = 44: ~0.3 GB rather
 *             than 2.3 GB dense). A row that is not reduced aborts the write.
 *   nm.H.<it>.bin  NM, the rows being multiplied in iteration <it>, dense, written
 *             once per iteration. The previous iteration's file is removed only
 *             after a checkpoint of the new iteration is committed: the last
 *             checkpoint of an iteration can still point into its NM (cursor on
 *             its final row), so overwriting a single nm.bin at the start of the
 *             next iteration made such a checkpoint unresumable.
 * Both are written to a temporary name, fsync'd and renamed, so a kill mid-write
 * leaves the previous checkpoint intact. */
#define CKPT_MAGIC 0x434c4f53434b5031ULL   /* "CLOSCKP1" */
#define NM_MAGIC   0x434c4f534e4d5031ULL   /* "CLOSNMP1" */
typedef struct {
    u64 magic, hash;
    long ncols, ngens, hist_n;
    int N, D, max_iter, it, md, iters;
    long a, mi, total_new_piv, n_new, n_prod, total_rows, rank, max_rows_seen;
    long long dropped;
} ckpt_hdr;
typedef struct { u64 magic, hash; long it, n_new, ncols, width; } nm_hdr;

static long resumed_ = 0;
long closure_resumed(void) { return resumed_; }
static const char *ckpt_dir(void) {
    const char *d = getenv("CLOSURE_CKPT_DIR");
    return (d && *d) ? d : NULL;
}
__attribute__((unused)) static u64 gens_hash(int N, int D, long ngens, const long *gen_ptr, const u64 *gen_masks) {
    u64 h = 1469598103934665603ULL;
#define HMIX(v) do { u64 v_ = (u64)(v); for (int k_ = 0; k_ < 8; k_++) { h ^= (v_ >> (8 * k_)) & 0xff; h *= 1099511628211ULL; } } while (0)
    HMIX(N); HMIX(D); HMIX(ngens);
    for (long g = 0; g <= ngens; g++) HMIX(gen_ptr[g]);
    for (long q = 0; q < gen_ptr[ngens]; q++) HMIX(gen_masks[q]);
#undef HMIX
    return h;
}
static int wr(FILE *f, const void *b, size_t sz, size_t n) { return n == 0 || fwrite(b, sz, n, f) == n; }
static int rd(FILE *f, void *b, size_t sz, size_t n) { return n == 0 || fread(b, sz, n, f) == n; }
static int commit_file(FILE *f, const char *tmp, const char *dst) {
    int ok = (fflush(f) == 0) && (fsync(fileno(f)) == 0);
    ok = (fclose(f) == 0) && ok;
    if (!ok || rename(tmp, dst) != 0) { remove(tmp); return 0; }
    return 1;
}
/* non-pivot column mask of the current basis, with prefix counts per word */
static long nonpivot_mask(u64 *npm, long *npos, long nw) {
    memset(npm, 0, sizeof(u64) * nw);
    for (long j = 0; j < ncols_; j++) if (!is_pivot_[j]) npm[j >> 6] |= 1ULL << (j & 63);
    long nnp = 0;
    for (long w = 0; w < nw; w++) { npos[w] = nnp; nnp += __builtin_popcountll(npm[w]); }
    return nnp;
}
__attribute__((unused)) static void ckpt_save(const ckpt_hdr *H0, const long *iter_rows, const long *iter_rank,
                      const long *iter_newpiv, const double *iter_wall) {
    const char *dir = ckpt_dir();
    if (!dir) return;
    char tmp[4096], dst[4096];
    snprintf(tmp, sizeof tmp, "%s/ckpt.%016llx.bin.tmp", dir, (unsigned long long)H0->hash);
    snprintf(dst, sizeof dst, "%s/ckpt.%016llx.bin", dir, (unsigned long long)H0->hash);
    long nw = (ncols_ + 63) / 64;
    u64 *npm = malloc(sizeof(u64) * nw); long *npos = malloc(sizeof(long) * nw);
    long nnp = nonpivot_mask(npm, npos, nw);
    if (ncols_ - nnp != rank_) {
        fprintf(stderr, "[ckpt] pivot count %ld != rank %ld; checkpoint NOT written\n", ncols_ - nnp, rank_);
        free(npm); free(npos); return;
    }
    long pw = (nnp + 63) / 64;
    u64 *out = malloc(sizeof(u64) * (pw ? pw : 1));
    FILE *f = fopen(tmp, "wb");
    int ok = f != NULL;
    ckpt_hdr H = *H0;
    H.magic = CKPT_MAGIC; H.rank = rank_; H.dropped = dropped_terms_;
    if (ok) ok = wr(f, &H, sizeof H, 1) && wr(f, iter_rows, sizeof(long), H.hist_n) &&
                 wr(f, iter_rank, sizeof(long), H.hist_n) && wr(f, iter_newpiv, sizeof(long), H.hist_n) &&
                 wr(f, iter_wall, sizeof(double), H.hist_n) && wr(f, lm_col_, sizeof(long), rank_) &&
                 wr(f, row_new_, 1, rank_) && wr(f, is_pivot_, 1, ncols_) && wr(f, pivot_new_, 1, ncols_);
    u64 tail = ncols_ & 63 ? (1ULL << (ncols_ & 63)) - 1 : ~0ULL;
    for (long i = 0; ok && i < rank_; i++) {
        memset(out, 0, sizeof(u64) * (pw ? pw : 1));
        const word *r = mzd_row(B_, (rci_t)i);
        for (long w = 0; w < nw; w++) {
            u64 x = r[w];
            if (w == nw - 1) x &= tail;
            u64 expect = ((lm_col_[i] >> 6) == w) ? (1ULL << (lm_col_[i] & 63)) : 0;
            if ((x & ~npm[w]) != expect) {
                fprintf(stderr, "[ckpt] basis row %ld is not reduced; checkpoint NOT written\n", i);
                ok = 0; break;
            }
            u64 y = x & npm[w];
            while (y) {
                int b = __builtin_ctzll(y);
                long idx = npos[w] + __builtin_popcountll(npm[w] & ((1ULL << b) - 1));
                out[idx >> 6] |= 1ULL << (idx & 63);
                y &= y - 1;
            }
        }
        if (ok) ok = wr(f, out, sizeof(u64), pw);
    }
    u64 trailer = CKPT_MAGIC;
    if (ok) ok = wr(f, &trailer, sizeof trailer, 1);
    if (f && ok) ok = commit_file(f, tmp, dst);
    else if (f) { fclose(f); remove(tmp); }
    if (!ok) fprintf(stderr, "[ckpt] write failed; previous checkpoint kept\n");
    else {
        /* the committed checkpoint is in iteration H.it; older NM files are dead */
        for (long k = 1; k < H.it; k++) {
            snprintf(dst, sizeof dst, "%s/nm.%016llx.%ld.bin", dir, (unsigned long long)H.hash, k);
            remove(dst);
        }
    }
    free(npm); free(npos); free(out);
}
__attribute__((unused)) static void nm_save(u64 hash, long it, long n_new, const mzd_t *NM) {
    const char *dir = ckpt_dir();
    if (!dir) return;
    char tmp[4096], dst[4096];
    snprintf(tmp, sizeof tmp, "%s/nm.%016llx.%ld.bin.tmp", dir, (unsigned long long)hash, it);
    snprintf(dst, sizeof dst, "%s/nm.%016llx.%ld.bin", dir, (unsigned long long)hash, it);
    nm_hdr H = {NM_MAGIC, hash, it, n_new, ncols_, NM->width};
    FILE *f = fopen(tmp, "wb");
    int ok = f != NULL && wr(f, &H, sizeof H, 1);
    for (long i = 0; ok && i < n_new; i++) ok = wr(f, mzd_row((mzd_t *)NM, (rci_t)i), sizeof(word), NM->width);
    u64 trailer = NM_MAGIC;
    if (ok) ok = wr(f, &trailer, sizeof trailer, 1);
    if (f && ok) ok = commit_file(f, tmp, dst);
    else if (f) { fclose(f); remove(tmp); }
    if (!ok) fprintf(stderr, "[ckpt] NM write failed\n");
}
/* Loads ckpt.bin into the globals (B_, flags) and *H and the history arrays.
 * Returns 1 on a valid checkpoint for this system, else 0 with nothing changed
 * that closure_run does not rebuild. */
__attribute__((unused)) static int ckpt_load(u64 hash, int N, int D, long ngens, int max_iter, ckpt_hdr *H,
                     long *iter_rows, long *iter_rank, long *iter_newpiv, double *iter_wall) {
    const char *dir = ckpt_dir();
    if (!dir) return 0;
    char path[4096];
    snprintf(path, sizeof path, "%s/ckpt.%016llx.bin", dir, (unsigned long long)hash);
    FILE *f = fopen(path, "rb");
    if (!f) return 0;
    int ok = rd(f, H, sizeof *H, 1) && H->magic == CKPT_MAGIC && H->hash == hash && H->N == N &&
             H->D == D && H->ngens == ngens && H->ncols == ncols_ && H->max_iter == max_iter &&
             H->hist_n == max_iter + 2;
    if (!ok) { fclose(f); fprintf(stderr, "[ckpt] %s is for a different system; ignored\n", path); return 0; }
    long rk = H->rank;
    long *lm = malloc(sizeof(long) * (rk ? rk : 1));
    char *rn = malloc(rk ? rk : 1);
    ok = rd(f, iter_rows, sizeof(long), H->hist_n) && rd(f, iter_rank, sizeof(long), H->hist_n) &&
         rd(f, iter_newpiv, sizeof(long), H->hist_n) && rd(f, iter_wall, sizeof(double), H->hist_n) &&
         rd(f, lm, sizeof(long), rk) && rd(f, rn, 1, rk) && rd(f, is_pivot_, 1, ncols_) &&
         rd(f, pivot_new_, 1, ncols_);
    long nw = (ncols_ + 63) / 64;
    u64 *npm = malloc(sizeof(u64) * nw); long *npos = malloc(sizeof(long) * nw);
    long nnp = nonpivot_mask(npm, npos, nw);
    if (ok && ncols_ - nnp != rk) ok = 0;
    long *npcol = malloc(sizeof(long) * (nnp ? nnp : 1));
    for (long j = 0, q = 0; j < ncols_; j++) if (!is_pivot_[j]) npcol[q++] = j;
    long pw = (nnp + 63) / 64;
    u64 *in = malloc(sizeof(u64) * (pw ? pw : 1));
    mzd_t *Bn = ok ? mzd_init((rci_t)(rk ? rk : 1), (rci_t)ncols_) : NULL;
    for (long i = 0; ok && i < rk; i++) {
        if (!rd(f, in, sizeof(u64), pw)) { ok = 0; break; }
        mzd_write_bit(Bn, (rci_t)i, (rci_t)lm[i], 1);
        for (long w = 0; w < pw; w++) {
            u64 y = in[w];
            while (y) { int b = __builtin_ctzll(y); long idx = w * 64 + b;
                        if (idx >= nnp) { ok = 0; break; }
                        mzd_write_bit(Bn, (rci_t)i, (rci_t)npcol[idx], 1); y &= y - 1; }
        }
    }
    u64 trailer = 0;
    if (ok) ok = rd(f, &trailer, sizeof trailer, 1) && trailer == CKPT_MAGIC;
    fclose(f);
    free(npm); free(npos); free(npcol); free(in);
    if (!ok) {
        fprintf(stderr, "[ckpt] %s truncated or corrupt; ignored\n", path);
        if (Bn) mzd_free(Bn);
        free(lm); free(rn);
        memset(is_pivot_, 0, ncols_); memset(pivot_new_, 0, ncols_);
        return 0;
    }
    if (B_) mzd_free(B_);
    B_ = Bn;
    free(lm_col_); free(row_new_);
    lm_col_ = lm; row_new_ = rn; rank_ = rk;
    dropped_terms_ = H->dropped;
    return 1;
}
static mzd_t *nm_load(u64 hash, long it, long n_new) {
    const char *dir = ckpt_dir();
    char path[4096];
    snprintf(path, sizeof path, "%s/nm.%016llx.%ld.bin", dir, (unsigned long long)hash, it);
    FILE *f = fopen(path, "rb");
    if (!f) return NULL;
    nm_hdr H;
    mzd_t *NM = NULL;
    int ok = rd(f, &H, sizeof H, 1) && H.magic == NM_MAGIC && H.hash == hash && H.it == it &&
             H.n_new == n_new && H.ncols == ncols_;
    if (ok) { NM = mzd_init((rci_t)(n_new ? n_new : 1), (rci_t)ncols_); ok = (H.width == NM->width); }
    for (long i = 0; ok && i < n_new; i++) ok = rd(f, mzd_row(NM, (rci_t)i), sizeof(word), NM->width);
    u64 trailer = 0;
    if (ok) ok = rd(f, &trailer, sizeof trailer, 1) && trailer == NM_MAGIC;
    fclose(f);
    if (!ok) { if (NM) mzd_free(NM); return NULL; }
    return NM;
}

/* Returns: 0 ok, 1 memory cap hit (state left as reached), 2 error.
 * gens: CSR of generator masks.  iter_* arrays sized max_iter+2.
 */
int closure_run(int N, int D, long ngens, const long *gen_ptr, const u64 *gen_masks,
                int max_iter, double mem_cap_bytes,
                long *out_ncols, long *out_iters,
                long *iter_rows, long *iter_rank, long *iter_newpiv, double *iter_wall,
                long *out_rank, int *out_contains_one, long *out_max_rows_seen) {
    closure_free();
    setup_columns(N, D);
    *out_ncols = ncols_;
    is_pivot_ = calloc(ncols_, 1);
    pivot_new_ = calloc(ncols_, 1);
    long max_rows_seen = 0;
    u64 *tmp = malloc(sizeof(u64) * (ncols_ + 1));
    u64 *rbuf = malloc(sizeof(u64) * (ncols_ + 1));
    int single_level = (max_iter == 1);
    int iters = 1;
    int hit_cap = 0;
    double t0 = now_sec();

    /* resume from a checkpoint of this same system, if one exists */
    u64 ghash = 0;
    ckpt_hdr R;
    int resume_now = 0;
#if !defined(ECH_LEGACY)
    if (ckpt_dir() && !single_level) {
        ghash = gens_hash(N, D, ngens, gen_ptr, gen_masks);
        resume_now = ckpt_load(ghash, N, D, ngens, max_iter, &R, iter_rows, iter_rank, iter_newpiv, iter_wall);
        if (resume_now) {
            resumed_++;
            iters = R.iters; max_rows_seen = R.max_rows_seen;
            fprintf(stderr, "[ckpt] resumed: iteration %d, row %ld of %ld, rank %ld\n", R.it, R.a, R.n_new, rank_);
        }
    }
#endif

    if (!resume_now) {
        /* iteration 0: echelonize the generators themselves */
        mzd_t *M = mzd_init((rci_t)(ngens ? ngens : 1), (rci_t)ncols_);
        for (long g = 0; g < ngens; g++) {
            long cnt = gen_ptr[g + 1] - gen_ptr[g];
            write_product(M, g, gen_masks + gen_ptr[g], cnt, 0, tmp);
        }
        long rk = ech(M);
        if (rk < 0) {
            mzd_free(M);
            free(tmp); free(rbuf);
            *out_iters = 0; *out_rank = 0; *out_contains_one = 0; *out_max_rows_seen = ngens;
            return 2;
        }
        install_basis(M, rk);
        mzd_free(M);
        iter_rows[0] = ngens; iter_rank[0] = rk; iter_newpiv[0] = rk; iter_wall[0] = now_sec() - t0;
        if (ngens > max_rows_seen) max_rows_seen = ngens;
    }

    /* multiplier lists per degree */
    long mult_cnt[8] = {0};
    u64 *mult[8] = {NULL};
    for (int d = 1; d <= D; d++) {
        long c = 1; for (int i = 0; i < d; i++) c = c * (N - i) / (i + 1);
        mult[d] = malloc(sizeof(u64) * (c ? c : 1));
        mult_cnt[d] = gen_masks_deg(N, d, mult[d]);
    }

    /* The single-level (GOAL-DREG-001) statistic multiplies the ORIGINAL generators, not the
     * reduced basis iteration 0 installed: a reduced row whose degree dropped under cancellation
     * would be multiplied by more monomials than any generator, and the row space would exceed
     * the degree-D Macaulay matrix of the generators. */

    for (int it = resume_now ? R.it : 1; it <= max_iter; it++) {
        t0 = now_sec();
        long n_new = 0, n_prod = 0, total_rows = 0, total_new_piv = 0;
        long *newrows = NULL;
        mzd_t *NM = NULL;
        long a = 0; int md = 1; long mi = 0;
        double per_row = (double)ncols_ / 8.0 + 64.0;
        long nm_rows = 0;
#if defined(ECH_LEGACY)
        long batch_max = 0;
#endif
        int resumed_here = resume_now;
        if (resume_now) {
            resume_now = 0;
            n_new = R.n_new; n_prod = R.n_prod; total_rows = R.total_rows; total_new_piv = R.total_new_piv;
            a = R.a; md = R.md; mi = R.mi; nm_rows = n_new;
            if (a < n_new) {
                NM = nm_load(ghash, it, n_new);
                if (!NM) { fprintf(stderr, "[ckpt] nm.%016llx.%d.bin missing or stale; cannot resume\n", (unsigned long long)ghash, it);
                           hit_cap = 2; break; }
            }
        } else {
        /* collect rows to multiply */
        if (single_level) {
            n_new = ngens;
            for (long g = 0; g < ngens; g++) {
                int dg = poly_deg(gen_masks + gen_ptr[g], gen_ptr[g + 1] - gen_ptr[g]);
                for (int md = 1; md <= D - dg; md++) n_prod += mult_cnt[md];
            }
        } else {
            for (long i = 0; i < rank_; i++) if (row_new_[i]) {
                n_new++;
                int dg = popc(col_mask_[lm_col_[i]]);
                for (int md = 1; md <= D - dg; md++) n_prod += mult_cnt[md];
            }
        }
        if (n_new == 0) { break; }
        if (n_prod == 0) {
            /* every new row already has degree D: nothing to multiply */
            for (long i = 0; i < rank_; i++) row_new_[i] = 0;
            memset(pivot_new_, 0, ncols_);
            iter_rows[it] = rank_; iter_rank[it] = rank_; iter_newpiv[it] = 0; iter_wall[it] = now_sec() - t0;
            iters = it + 1;
            break;
        }
        nm_rows = single_level ? 0 : n_new;
        (void)nm_rows;
#if defined(ECH_LEGACY)
        /* batch size from memory cap: (rank + batch) * ncols / 8 <= cap. Kept
         * as it was so -DECH_LEGACY rebuilds RUN-SEMBIN-9bb990's exact matrices. */
        batch_max = (long)((mem_cap_bytes - (double)rank_ * per_row) / per_row);
#else
        /* batch size from memory cap. Resident at once during ech(S): the basis
         * B_ (rank rows), S itself (rank + batch rows), and PLUQ's full-reduction
         * workspace, a copy of the r x r block of U, r = output rank <= ncols
         * (measured: peak - matrix = 0.12/0.25/0.79 GiB at r = 20k/40k/80k,
         * ncols 149986, i.e. ~ r^2/8 bytes). Counting only S, as before, let
         * (43,2,2,22) N=44 at a 7 GiB cap reach 13.6 GB and be OOM-killed. Also
         * resident: NM, the dense copy of the rows being multiplied (nm_rows of
         * them; the generators in the single-level case are read in place). r is
         * bounded by min(ncols, rank + batch); the largest batch whose bound fits
         * is found by bisection (the need is increasing in batch). */
        long batch_max = batch_for(rank_, nm_rows, per_row, mem_cap_bytes);
#endif
        /* Macaulay row count: every mu * g including mu = 1 for the single-level statistic */
        total_rows = (single_level ? ngens : rank_) + n_prod;
        if (batch_max < 1024) { hit_cap = 1; iter_rows[it] = total_rows; iter_rank[it] = -1; iter_newpiv[it] = -1; iter_wall[it] = 0; iters = it + 1; break; }
        if (total_rows > max_rows_seen) max_rows_seen = total_rows;
        /* snapshot which rows are new (install_basis will reset flags) */
        newrows = malloc(sizeof(long) * (n_new ? n_new : 1));
        long k = 0;
        if (single_level) { for (long g = 0; g < ngens; g++) newrows[k++] = g; }
        else { for (long i = 0; i < rank_; i++) if (row_new_[i]) newrows[k++] = i; }
        /* copy the rows out first, since B_ is replaced batch by batch. Kept
         * DENSE (ncols/8 bytes a row) and expanded to masks only when used:
         * a sparse u64 list costs 8 bytes per nonzero, and reduced rows at
         * N = 44 carry up to ~19k nonzeros, so the old sparse copy of ~80k
         * rows ran to gigabytes outside the memory cap and was OOM-killed.
         * row_masks() yields the same masks in the same order either way. */
        if (!single_level) {
            NM = mzd_init((rci_t)(n_new ? n_new : 1), (rci_t)ncols_);
            for (long a2 = 0; a2 < n_new; a2++) mzd_copy_row(NM, (rci_t)a2, B_, (rci_t)newrows[a2]);
#if !defined(ECH_LEGACY)
            if (ckpt_dir()) nm_save(ghash, it, n_new, NM);
#endif
        }
        for (long i = 0; i < rank_; i++) row_new_[i] = 0;
        memset(pivot_new_, 0, ncols_);
        }   /* end of the fresh-iteration prelude */
        const u64 *cur_m = NULL; long cur_c = 0;
#define LOAD_ROW(idx) do { \
            if (single_level) { cur_m = gen_masks + gen_ptr[newrows[idx]]; \
                                 cur_c = gen_ptr[newrows[idx] + 1] - gen_ptr[newrows[idx]]; } \
            else { cur_c = row_masks(NM, (idx), rbuf); cur_m = rbuf; } } while (0)
        /* stream products in batches */
        /* On resume, 1 may already be in the restored basis (the kill came
         * after its batch). A fresh iteration keeps the original behaviour --
         * found_one is only set after a batch -- so ranks reported when 1 lies
         * in the generators' span match RUN-SEMBIN-9bb990. */
        int found_one = resumed_here && rank_ > 0 && is_pivot_[ncols_ - 1];
        if (a < n_new) LOAD_ROW(a);
        int dg_a = (a < n_new) ? poly_deg(cur_m, cur_c) : 0;
        while (a < n_new && !found_one) {
#if defined(ECH_LEGACY)
            long batch = batch_max;
#else
            /* Re-sized before EVERY batch: the basis grows within an iteration
             * (51952 -> 129383 rows after the first batch at N = 44), and a size
             * fixed at the iteration's start let the second batch's S reach
             * ~452k rows and the process 13.2 GB, OOM-killed. */
            long batch = batch_for(rank_, nm_rows, per_row, mem_cap_bytes);
            if (batch < 1024) { hit_cap = 1; break; }
#endif
            if (batch > n_prod) batch = n_prod;
            mzd_t *S = mzd_init((rci_t)(rank_ + batch), (rci_t)ncols_);
            for (long i = 0; i < rank_; i++) mzd_copy_row(S, (rci_t)i, B_, (rci_t)i);
            long filled = 0;
            while (a < n_new && filled < batch) {
                if (md > D - dg_a) { a++; md = 1; mi = 0; if (a < n_new) { LOAD_ROW(a); dg_a = poly_deg(cur_m, cur_c); } continue; }
                if (mi >= mult_cnt[md]) { md++; mi = 0; continue; }
                write_product(S, rank_ + filled, cur_m, cur_c, mult[md][mi], tmp);
                filled++; mi++;
            }
            if (filled == 0) { mzd_free(S); break; }   /* products exhausted */
            double tb = now_sec();
            long rk2 = ech(S);
            long old_rank = rank_;
            if (rk2 >= 0) {
                /* S contains the old basis, so every old leading column must
                 * still lead: the set of leading monomials only grows */
                char *np = calloc(ncols_, 1);
                for (long i = 0; i < rk2; i++) { long fc = first_col(S, i); if (fc >= 0) np[fc] = 1; }
                for (long j = 0; j < ncols_; j++) if (is_pivot_[j] && !np[j]) {
                    fprintf(stderr, "[ech check] pivot column %ld lost in elimination\n", j);
                    ech_faults_++; rk2 = -1; break;
                }
                free(np);
            }
            if (rk2 < 0) { mzd_free(S); hit_cap = 2; break; }
            if (verbose()) fprintf(stderr, "[closure D=%d it=%d] batch rows=%ld (basis %ld + %ld products) -> rank %ld (+%ld) echelon %.1fs\n",
                                   D, it, rank_ + filled, rank_, filled, rk2, rk2 - old_rank, now_sec() - tb);
            /* install: keep previous new flags */
            install_basis(S, rk2);
            total_new_piv += (rk2 - old_rank);
            mzd_free(S);
#if !defined(ECH_LEGACY)
            if (ckpt_dir() && !single_level) {
                ckpt_hdr H = {0};
                H.hash = ghash; H.ncols = ncols_; H.ngens = ngens; H.hist_n = max_iter + 2;
                H.N = N; H.D = D; H.max_iter = max_iter; H.it = it; H.md = md; H.iters = iters;
                H.a = a; H.mi = mi; H.total_new_piv = total_new_piv; H.n_new = n_new; H.n_prod = n_prod;
                H.total_rows = total_rows; H.max_rows_seen = max_rows_seen;
                ckpt_save(&H, iter_rows, iter_rank, iter_newpiv, iter_wall);
            }
#endif
            /* 1 in the row space settles the CLOSURE's verdict, so it stops. The
             * single-level statistic is the RANK of the whole degree-D Macaulay
             * block, so it must take every product: stopping here returned a
             * truncated rank whenever the block needed more than one batch and 1
             * appeared before the last (N=42 D=4: 8556 against 36739 at a
             * 0.25 GiB cap), labelled completed. */
            if (is_pivot_[ncols_ - 1] && !single_level) { found_one = 1; break; }
        }
#undef LOAD_ROW
        if (NM) mzd_free(NM);
        free(newrows);
        iter_rows[it] = total_rows; iter_rank[it] = rank_; iter_newpiv[it] = total_new_piv; iter_wall[it] = now_sec() - t0;
        iters = it + 1;
        if (hit_cap) break;     /* cap reached mid-iteration: state is partial, no verdict */
        if (found_one) break;   /* 1 in W_D: the closure is the whole space; verdict decided */
        if (total_new_piv == 0) break;
    }
    for (int d = 1; d <= D; d++) free(mult[d]);
    free(tmp); free(rbuf);
    *out_iters = iters;
    *out_rank = rank_;
    *out_contains_one = (rank_ > 0 && is_pivot_[ncols_ - 1]) ? 1 : 0;
    *out_max_rows_seen = max_rows_seen;
    if (!hit_cap && ckpt_dir() && !single_level) {
        /* finished: this system's checkpoint has no further use (other
         * systems' files in the directory are left alone) */
        if (!ghash) ghash = gens_hash(N, D, ngens, gen_ptr, gen_masks);
        char path[4096];
        snprintf(path, sizeof path, "%s/ckpt.%016llx.bin", ckpt_dir(), (unsigned long long)ghash); remove(path);
        for (int k = 1; k <= max_iter + 1; k++) {
            snprintf(path, sizeof path, "%s/nm.%016llx.%d.bin", ckpt_dir(), (unsigned long long)ghash, k); remove(path);
        }
    }
    return hit_cap == 2 ? 2 : (hit_cap ? 1 : 0);
}

long closure_rank(void) { return rank_; }
long closure_ncols(void) { return ncols_; }

/* leading masks of the basis rows, in row order */
void closure_lm_dump(u64 *out) {
    for (long i = 0; i < rank_; i++) out[i] = (lm_col_[i] >= 0) ? col_mask_[lm_col_[i]] : 0;
}

/* number of basis rows with leading degree d */
long closure_count_deg(int d) {
    long c = 0;
    for (long i = 0; i < rank_; i++) if (lm_col_[i] >= 0 && popc(col_mask_[lm_col_[i]]) == d) c++;
    return c;
}

/* DIAGNOSTIC: evaluate every basis row at a Boolean assignment and report how
 * many do NOT vanish, plus the index of the first such row. Every element of the
 * ideal vanishes at every common zero of the generators, so a nonzero count on a
 * genuine solution proves the row space has left the ideal. In C because the
 * Python equivalent is ~10^8 interpreter operations at N = 44. */
long closure_eval_rows(u64 assign, long *first_bad, long *first_cnt) {
    if (first_bad) *first_bad = -1;
    if (first_cnt) *first_cnt = 0;
    u64 *buf = malloc(sizeof(u64) * (size_t)ncols_);
    if (!buf) return -1;
    long offenders = 0;
    for (long i = 0; i < rank_; i++) {
        long cnt = row_masks(B_, i, buf);
        int v = 0;
        for (long j = 0; j < cnt; j++) if ((buf[j] & assign) == buf[j]) v ^= 1;
        if (v) {
            if (offenders == 0) {
                if (first_bad) *first_bad = i;
                if (first_cnt) *first_cnt = cnt;
            }
            offenders++;
        }
    }
    free(buf);
    return offenders;
}

/* masks of basis row i; returns count; out must hold ncols entries */
long closure_row_masks(long i, u64 *out) {
    if (i < 0 || i >= rank_) return 0;
    return row_masks(B_, i, out);
}

/* Standard monomials of the monomial ideal generated by the leading masks:
 * squarefree monomials containing no leading mask as a subset.  BFS by highest
 * variable; stops at cap and returns cap+1 if exceeded.  Returns 0 if 1 is a
 * leading monomial. */
long closure_standard_count(long cap) {
    if (rank_ > 0 && is_pivot_[ncols_ - 1]) return 0;
    /* bucket leading masks by highest set bit */
    long *bcnt = calloc(N_ + 1, sizeof(long));
    for (long i = 0; i < rank_; i++) {
        u64 l = col_mask_[lm_col_[i]];
        if (l == 0) { free(bcnt); return 0; }
        int hb = 63 - __builtin_clzll(l);
        bcnt[hb]++;
    }
    u64 **buck = malloc(sizeof(u64 *) * (N_ + 1));
    long *bfill = calloc(N_ + 1, sizeof(long));
    for (int j = 0; j < N_; j++) buck[j] = malloc(sizeof(u64) * (bcnt[j] ? bcnt[j] : 1));
    for (long i = 0; i < rank_; i++) {
        u64 l = col_mask_[lm_col_[i]];
        int hb = 63 - __builtin_clzll(l);
        buck[hb][bfill[hb]++] = l;
    }
    /* BFS */
    long qcap = cap + 2, qh = 0, qt = 0;
    u64 *q = malloc(sizeof(u64) * qcap);
    q[qt++] = 0;
    long count = 1;
    long result = -1;
    while (qh < qt) {
        u64 m = q[qh++];
        int start = (m == 0) ? 0 : (64 - __builtin_clzll(m));
        for (int j = start; j < N_; j++) {
            u64 m2 = m | (1ULL << j);
            int bad = 0;
            for (long b = 0; b < bcnt[j]; b++) { if ((buck[j][b] & ~m2) == 0) { bad = 1; break; } }
            if (bad) continue;
            count++;
            if (count > cap) { result = cap + 1; goto done; }
            q[qt++] = m2;
        }
    }
    result = count;
done:
    free(q); for (int j = 0; j < N_; j++) free(buck[j]);
    free(buck); free(bfill); free(bcnt);
    return result;
}
