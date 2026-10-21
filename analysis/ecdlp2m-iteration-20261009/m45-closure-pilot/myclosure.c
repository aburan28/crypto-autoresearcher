/* myclosure.c -- PILOT (m3closure). Independent GF(2) eliminator and degree-D
 * Boolean closures, written from the definitions without M4RI and without
 * reference to closure.c's code paths. Used to cross-check libclosure (M4RI
 * 0.0.20200125) on small instances.
 *
 * Columns: squarefree monomials of degree <= D over N variables; column index
 * grows with degree (constant = column 0), colex rank within a degree. A row's
 * leading column is its HIGHEST set bit, i.e. a highest-degree monomial, so
 * V cap B_{<=d} = span of echelon rows whose leading column has degree <= d.
 * Echelon form is kept non-reduced: rows are never modified once inserted.
 *
 *   my_macaulay(N, D, ngens, ptr, masks, &rank, &one, dims_by_deg)
 *       single-level M_D: rows mu*f, deg mu <= D - deg f (f a generator).
 *   my_closure(N, D, ngens, ptr, masks, stop_at_one, &rank, &one, dims_by_deg)
 *       W_D: least subspace containing the generators with x_j*g in it for
 *       every element g of degree <= D-1 (to fixpoint, or until 1 appears
 *       when stop_at_one).
 * dims_by_deg[d] = number of pivots of degree exactly d.
 */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
typedef uint64_t u64;

static int N_, D_;
static long ncols_, nw_;
static long binom_[70][12];
static long off_[12];
static u64 *rows_ = NULL;     /* rank_ rows of nw_ words */
static long *piv_ = NULL;     /* column -> row index or -1 */
static long rank_ = 0, cap_ = 0;
static u64 *colmask_ = NULL;

static void init_binom(void) {
    for (int a = 0; a < 70; a++) for (int b = 0; b < 12; b++) {
        if (b == 0) binom_[a][b] = 1;
        else if (a == 0) binom_[a][b] = 0;
        else binom_[a][b] = binom_[a - 1][b - 1] + binom_[a - 1][b];
    }
}
static long col_of(u64 m) {
    int d = __builtin_popcountll(m);
    if (d > D_) return -1;
    long r = 0; int i = 0;
    while (m) { int p = __builtin_ctzll(m); r += binom_[p][i + 1]; i++; m &= m - 1; }
    return off_[d] + r;
}
static void setup(int N, int D) {
    init_binom();
    N_ = N; D_ = D;
    long tot = 0;
    for (int d = 0; d <= D; d++) { off_[d] = tot; tot += binom_[N][d]; }
    off_[D + 1] = tot;
    ncols_ = tot; nw_ = (tot + 63) / 64;
    free(colmask_); colmask_ = malloc(sizeof(u64) * tot);
    /* fill colmask by enumerating masks of each degree (Gosper) */
    for (int d = 0; d <= D; d++) {
        if (d == 0) { colmask_[0] = 0; continue; }
        u64 x = (1ULL << d) - 1, lim = (N >= 64) ? ~0ULL : (1ULL << N);
        while (x < lim) {
            colmask_[col_of(x)] = x;
            u64 c = x & -x, r = x + c;
            x = (((r ^ x) >> 2) / c) | r;
        }
    }
    free(piv_); piv_ = malloc(sizeof(long) * tot);
    for (long j = 0; j < tot; j++) piv_[j] = -1;
    free(rows_); cap_ = 1024; rows_ = malloc(sizeof(u64) * nw_ * cap_);
    rank_ = 0;
}
static int deg_col(long c) { return __builtin_popcountll(colmask_[c]); }
static long top_col(const u64 *r) {
    for (long w = nw_ - 1; w >= 0; w--) if (r[w]) return w * 64 + 63 - __builtin_clzll(r[w]);
    return -1;
}
/* reduce r against the echelon basis; if nonzero, append; return new row index or -1 */
static long insert(u64 *r) {
    for (;;) {
        long t = top_col(r);
        if (t < 0) return -1;
        long p = piv_[t];
        if (p < 0) {
            if (rank_ == cap_) { cap_ *= 2; rows_ = realloc(rows_, sizeof(u64) * nw_ * cap_); }
            memcpy(rows_ + rank_ * nw_, r, sizeof(u64) * nw_);
            piv_[t] = rank_;
            return rank_++;
        }
        const u64 *q = rows_ + p * nw_;
        long tw = t >> 6;
        for (long w = 0; w <= tw; w++) r[w] ^= q[w];
    }
}
static void toggle(u64 *r, long c) { r[c >> 6] ^= 1ULL << (c & 63); }
/* r := product of monomial mu with row src (given as row of this basis or a mask list) */
static int product_row(const u64 *src, u64 mu, u64 *out) {
    memset(out, 0, sizeof(u64) * nw_);
    for (long w = 0; w < nw_; w++) {
        u64 x = src[w];
        while (x) {
            long c = w * 64 + __builtin_ctzll(x);
            long c2 = col_of(colmask_[c] | mu);
            if (c2 < 0) return -1;
            toggle(out, c2);
            x &= x - 1;
        }
    }
    return 0;
}
static void dims(long *dims_by_deg) {
    for (int d = 0; d <= D_; d++) dims_by_deg[d] = 0;
    for (long c = 0; c < ncols_; c++) if (piv_[c] >= 0) dims_by_deg[deg_col(c)]++;
}
static int gen_row(const u64 *m, long cnt, u64 *out, int *deg) {
    memset(out, 0, sizeof(u64) * nw_);
    int d = 0;
    for (long i = 0; i < cnt; i++) {
        long c = col_of(m[i]);
        if (c < 0) return -1;
        toggle(out, c);
        int dd = __builtin_popcountll(m[i]); if (dd > d) d = dd;
    }
    *deg = d;
    return 0;
}

long my_ncols(void) { return ncols_; }

int my_macaulay(int N, int D, long ngens, const long *ptr, const u64 *masks,
                long *out_rank, int *out_one, long *dims_by_deg, long *out_rows) {
    setup(N, D);
    u64 *g = malloc(sizeof(u64) * nw_), *p = malloc(sizeof(u64) * nw_);
    long nrows = 0;
    for (long e = 0; e < ngens; e++) {
        int dg;
        if (gen_row(masks + ptr[e], ptr[e + 1] - ptr[e], g, &dg) < 0) { free(g); free(p); return -1; }
        if (ptr[e + 1] == ptr[e]) continue;
        for (int md = 0; md <= D - dg; md++) {
            u64 x = (md == 0) ? 0 : ((1ULL << md) - 1), lim = (N >= 64) ? ~0ULL : (1ULL << N);
            while (1) {
                if (product_row(g, x, p) < 0) { free(g); free(p); return -2; }
                insert(p); nrows++;
                if (md == 0) break;
                u64 c = x & -x, r = x + c;
                x = (((r ^ x) >> 2) / c) | r;
                if (x >= lim) break;
            }
        }
    }
    *out_rank = rank_; *out_one = piv_[0] >= 0; *out_rows = nrows;
    dims(dims_by_deg);
    free(g); free(p);
    return 0;
}

int my_closure(int N, int D, long ngens, const long *ptr, const u64 *masks, int stop_at_one,
               long *out_rank, int *out_one, long *dims_by_deg, long *out_products) {
    setup(N, D);
    u64 *g = malloc(sizeof(u64) * nw_), *p = malloc(sizeof(u64) * nw_), *src = malloc(sizeof(u64) * nw_);
    long nprod = 0;
    for (long e = 0; e < ngens; e++) {
        int dg;
        if (gen_row(masks + ptr[e], ptr[e + 1] - ptr[e], g, &dg) < 0) { free(g); free(p); free(src); return -1; }
        insert(g);
    }
    /* queue = rows in insertion order; every inserted row is processed once */
    for (long q = 0; q < rank_; q++) {
        if (stop_at_one && piv_[0] >= 0) break;
        long t = top_col(rows_ + q * nw_);
        if (deg_col(t) >= D) continue;
        for (int j = 0; j < N; j++) {
            memcpy(src, rows_ + q * nw_, sizeof(u64) * nw_);   /* rows_ may move on realloc */
            if (product_row(src, 1ULL << j, p) < 0) { free(g); free(p); free(src); return -2; }
            insert(p); nprod++;
            if (stop_at_one && piv_[0] >= 0) break;
        }
    }
    *out_rank = rank_; *out_one = piv_[0] >= 0; *out_products = nprod;
    dims(dims_by_deg);
    free(g); free(p); free(src);
    return 0;
}

/* evaluate every basis row at a Boolean point; returns number not vanishing */
long my_eval(u64 assign) {
    long bad = 0;
    for (long i = 0; i < rank_; i++) {
        const u64 *r = rows_ + i * nw_;
        int v = 0;
        for (long w = 0; w < nw_; w++) {
            u64 x = r[w];
            while (x) { long c = w * 64 + __builtin_ctzll(x); if ((colmask_[c] & assign) == colmask_[c]) v ^= 1; x &= x - 1; }
        }
        bad += v;
    }
    return bad;
}
void my_free(void) { free(rows_); rows_ = NULL; free(piv_); piv_ = NULL; free(colmask_); colmask_ = NULL; rank_ = 0; }
