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
#include <m4ri/m4ri.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <time.h>

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

    /* iteration 0: echelonize the generators themselves */
    double t0 = now_sec();
    mzd_t *M = mzd_init((rci_t)(ngens ? ngens : 1), (rci_t)ncols_);
    for (long g = 0; g < ngens; g++) {
        long cnt = gen_ptr[g + 1] - gen_ptr[g];
        write_product(M, g, gen_masks + gen_ptr[g], cnt, 0, tmp);
    }
    long rk = mzd_echelonize(M, 1);
    install_basis(M, rk);
    mzd_free(M);
    iter_rows[0] = ngens; iter_rank[0] = rk; iter_newpiv[0] = rk; iter_wall[0] = now_sec() - t0;
    if (ngens > max_rows_seen) max_rows_seen = ngens;
    int iters = 1;
    int hit_cap = 0;

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
    int single_level = (max_iter == 1);

    for (int it = 1; it <= max_iter; it++) {
        t0 = now_sec();
        /* collect rows to multiply */
        long n_new = 0, n_prod = 0;
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
        /* batch size from memory cap: (rank + batch) * ncols / 8 <= cap */
        double per_row = (double)ncols_ / 8.0 + 64.0;
        long batch_max = (long)((mem_cap_bytes - (double)rank_ * per_row) / per_row);
        /* Macaulay row count: every mu * g including mu = 1 for the single-level statistic */
        long total_rows = (single_level ? ngens : rank_) + n_prod;
        if (batch_max < 1024) { hit_cap = 1; iter_rows[it] = total_rows; iter_rank[it] = -1; iter_newpiv[it] = -1; iter_wall[it] = 0; iters = it + 1; break; }
        long total_new_piv = 0;
        if (total_rows > max_rows_seen) max_rows_seen = total_rows;
        /* snapshot which rows are new (install_basis will reset flags) */
        long *newrows = malloc(sizeof(long) * (n_new ? n_new : 1));
        long k = 0;
        if (single_level) { for (long g = 0; g < ngens; g++) newrows[k++] = g; }
        else { for (long i = 0; i < rank_; i++) if (row_new_[i]) newrows[k++] = i; }
        /* copy the rows' masks out first, since B_ is replaced batch by batch */
        u64 **nm = malloc(sizeof(u64 *) * (n_new ? n_new : 1));
        long *nc = malloc(sizeof(long) * (n_new ? n_new : 1));
        for (long a = 0; a < n_new; a++) {
            long cnt;
            if (single_level) {
                cnt = gen_ptr[newrows[a] + 1] - gen_ptr[newrows[a]];
                memcpy(rbuf, gen_masks + gen_ptr[newrows[a]], sizeof(u64) * cnt);
            } else {
                cnt = row_masks(B_, newrows[a], rbuf);
            }
            nm[a] = malloc(sizeof(u64) * (cnt ? cnt : 1));
            memcpy(nm[a], rbuf, sizeof(u64) * cnt);
            nc[a] = cnt;
        }
        for (long i = 0; i < rank_; i++) row_new_[i] = 0;
        memset(pivot_new_, 0, ncols_);
        /* stream products in batches */
        int found_one = 0;
        long a = 0; int md = 1; long mi = 0;
        int dg_a = (n_new > 0) ? poly_deg(nm[0], nc[0]) : 0;
        while (a < n_new) {
            long batch = batch_max;
            if (batch > n_prod) batch = n_prod;
            mzd_t *S = mzd_init((rci_t)(rank_ + batch), (rci_t)ncols_);
            for (long i = 0; i < rank_; i++) mzd_copy_row(S, (rci_t)i, B_, (rci_t)i);
            long filled = 0;
            while (a < n_new && filled < batch) {
                if (md > D - dg_a) { a++; md = 1; mi = 0; if (a < n_new) dg_a = poly_deg(nm[a], nc[a]); continue; }
                if (mi >= mult_cnt[md]) { md++; mi = 0; continue; }
                write_product(S, rank_ + filled, nm[a], nc[a], mult[md][mi], tmp);
                filled++; mi++;
            }
            if (filled == 0) { mzd_free(S); break; }   /* products exhausted */
            double tb = now_sec();
            long rk2 = mzd_echelonize(S, 1);
            long old_rank = rank_;
            if (verbose()) fprintf(stderr, "[closure D=%d it=%d] batch rows=%ld (basis %ld + %ld products) -> rank %ld (+%ld) echelon %.1fs\n",
                                   D, it, rank_ + filled, rank_, filled, rk2, rk2 - old_rank, now_sec() - tb);
            /* install: keep previous new flags */
            install_basis(S, rk2);
            total_new_piv += (rk2 - old_rank);
            mzd_free(S);
            if (is_pivot_[ncols_ - 1]) { found_one = 1; break; }
        }
        for (long b = 0; b < n_new; b++) free(nm[b]);
        free(nm); free(nc); free(newrows);
        iter_rows[it] = total_rows; iter_rank[it] = rank_; iter_newpiv[it] = total_new_piv; iter_wall[it] = now_sec() - t0;
        iters = it + 1;
        if (found_one) break;   /* 1 in W_D: the closure is the whole space; verdict decided */
        if (total_new_piv == 0) break;
    }
    for (int d = 1; d <= D; d++) free(mult[d]);
    free(tmp); free(rbuf);
    *out_iters = iters;
    *out_rank = rank_;
    *out_contains_one = (rank_ > 0 && is_pivot_[ncols_ - 1]) ? 1 : 0;
    *out_max_rows_seen = max_rows_seen;
    return hit_cap ? 1 : 0;
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
