/* myclosure_local.c -- PILOT #3 (block-local closure). EXPLORATORY; not program
 * evidence. Derived from pilot #1/#2's independent eliminator myclosure.c
 * (sha256 ce2b374f..., see PROVENANCE.sha256) by adding a MONOMIAL FILTER to the
 * degree-D mutant closure W_D. No M4RI.
 *
 * Unchanged from myclosure.c: bit-packed GF(2) echelon basis, non-reduced,
 * rows never modified once inserted; columns ordered by degree then colex rank
 * within a degree, so a row's top column is one of its highest-degree
 * monomials and "deg(top) <= D-1" means every monomial of the row has degree
 * <= D-1 (products with one variable never exceed D).
 *
 * New: the column set is any subset of the squarefree monomials of degree
 * <= D ("allowed" monomials), given by a block-locality rule:
 *   variable j lies in the (contiguous) block interval [lo_j, hi_j];
 *   locality L(mu) = max(1, B - A + 1), A = min_j hi_j, B = max_j lo_j over
 *   the variables j of mu (L = minimal number of consecutive blocks whose
 *   union contains all variables of mu; the constant has L = 1);
 *   mu is allowed iff deg(mu) <= D and L(mu) <= Lmax.
 * A product x_j * g is DROPPED AS A WHOLE when any of its monomials is not
 * allowed (sound: every row kept is a genuine element of the ideal; no term
 * is ever truncated). With Lmax >= number of blocks this is exactly W_D.
 * Optional multiplier rule (adj >= 0): x_j multiplies g only if the block
 * interval of x_j meets [A_g - adj, B_g + adj], where [A_g, B_g] is the
 * window of g (A_g = min hi, B_g = max lo over all variables of g); adj < 0
 * means no multiplier rule.
 *
 *   my_closure_local(N, D, ngens, ptr, masks, stop_at_one, lo, hi, Lmax, adj,
 *                    &rank, &one, dims_by_deg, &nproducts, &ndropped)
 * returns 0, or -1 (generator monomial not allowed / degree > D), -2 (internal:
 * product degree > D), -3 (hash table full).
 */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
typedef uint64_t u64;

static int N_, D_;
static long ncols_, nw_;
static long binom_[70][12];
static u64 *rows_ = NULL;     /* rank_ rows of nw_ words */
static long *piv_ = NULL;     /* column -> row index or -1 */
static long rank_ = 0, cap_ = 0;
static u64 *colmask_ = NULL;  /* column -> monomial mask */
static int *coldeg_ = NULL;   /* column -> degree */
/* mask -> column hash (open addressing) */
static u64 *hkey_ = NULL; static long *hval_ = NULL; static long hcap_ = 0;
static const int *lo_, *hi_; static int Lmax_;

static void init_binom(void) {
    for (int a = 0; a < 70; a++) for (int b = 0; b < 12; b++) {
        if (b == 0) binom_[a][b] = 1;
        else if (a == 0) binom_[a][b] = 0;
        else binom_[a][b] = binom_[a - 1][b - 1] + binom_[a - 1][b];
    }
}
static inline u64 hmix(u64 x) { x ^= x >> 33; x *= 0xff51afd7ed558ccdULL; x ^= x >> 33; x *= 0xc4ceb9fe1a85ec53ULL; x ^= x >> 33; return x; }
static int hput(u64 key, long val) {
    long i = hmix(key) & (hcap_ - 1), n = 0;
    while (hval_[i] >= 0) { if (hkey_[i] == key) { hval_[i] = val; return 0; } i = (i + 1) & (hcap_ - 1); if (++n > hcap_) return -1; }
    hkey_[i] = key; hval_[i] = val; return 0;
}
static long hget(u64 key) {
    long i = hmix(key) & (hcap_ - 1);
    while (hval_[i] >= 0) { if (hkey_[i] == key) return hval_[i]; i = (i + 1) & (hcap_ - 1); }
    return -1;
}
/* locality window of a mask: A = min hi, B = max lo over set bits; empty mask -> A=B=0 */
static void window(u64 m, int *A, int *B) {
    int a = 1 << 29, b = -(1 << 29);
    if (!m) { *A = 0; *B = 0; return; }
    while (m) { int p = __builtin_ctzll(m); if (hi_[p] < a) a = hi_[p]; if (lo_[p] > b) b = lo_[p]; m &= m - 1; }
    *A = a; *B = b;
}
static int locality(u64 m) { int A, B; window(m, &A, &B); int L = B - A + 1; return L < 1 ? 1 : L; }
static int allowed(u64 m) { return __builtin_popcountll(m) <= D_ && locality(m) <= Lmax_; }
/* column of a mask: -1 if not allowed */
static long col_of(u64 m) { return hget(m); }

static int setup(int N, int D) {
    init_binom();
    N_ = N; D_ = D;
    long tot = 0;
    for (int d = 0; d <= D; d++) tot += binom_[N][d];
    hcap_ = 1024; while (hcap_ < 2 * tot) hcap_ <<= 1;
    free(hkey_); free(hval_);
    hkey_ = malloc(sizeof(u64) * hcap_); hval_ = malloc(sizeof(long) * hcap_);
    for (long i = 0; i < hcap_; i++) hval_[i] = -1;
    free(colmask_); colmask_ = malloc(sizeof(u64) * tot);
    free(coldeg_); coldeg_ = malloc(sizeof(int) * tot);
    long c = 0;
    /* enumerate masks of each degree (Gosper), keep the allowed ones in order */
    for (int d = 0; d <= D; d++) {
        if (d == 0) { colmask_[c] = 0; coldeg_[c] = 0; if (hput(0, c) < 0) return -3; c++; continue; }
        u64 x = (1ULL << d) - 1, lim = (N >= 64) ? ~0ULL : (1ULL << N);
        while (x < lim) {
            if (allowed(x)) { colmask_[c] = x; coldeg_[c] = d; if (hput(x, c) < 0) return -3; c++; }
            u64 cc = x & -x, r = x + cc;
            x = (((r ^ x) >> 2) / cc) | r;
        }
    }
    ncols_ = c; nw_ = (c + 63) / 64;
    free(piv_); piv_ = malloc(sizeof(long) * c);
    for (long j = 0; j < c; j++) piv_[j] = -1;
    free(rows_); cap_ = 1024; rows_ = malloc(sizeof(u64) * nw_ * cap_);
    rank_ = 0;
    return 0;
}
static int deg_col(long c) { return coldeg_[c]; }
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
/* out := mu * src. Returns 0; 1 if some product monomial is not allowed (row to
 * be dropped); -2 if a product monomial has degree > D (must not happen). */
static int product_row(const u64 *src, u64 mu, u64 *out) {
    memset(out, 0, sizeof(u64) * nw_);
    for (long w = 0; w < nw_; w++) {
        u64 x = src[w];
        while (x) {
            long c = w * 64 + __builtin_ctzll(x);
            u64 m2 = colmask_[c] | mu;
            long c2 = col_of(m2);
            if (c2 < 0) return __builtin_popcountll(m2) > D_ ? -2 : 1;
            toggle(out, c2);
            x &= x - 1;
        }
    }
    return 0;
}
/* window of a whole row (over all its monomials) */
static void row_window(const u64 *r, int *A, int *B) {
    u64 un = 0;
    for (long w = 0; w < nw_; w++) {
        u64 x = r[w];
        while (x) { long c = w * 64 + __builtin_ctzll(x); un |= colmask_[c]; x &= x - 1; }
    }
    window(un, A, B);
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

int my_closure_local(int N, int D, long ngens, const long *ptr, const u64 *masks, int stop_at_one,
                     const int *lo, const int *hi, int Lmax, int adj,
                     long *out_rank, int *out_one, long *dims_by_deg, long *out_products, long *out_dropped) {
    lo_ = lo; hi_ = hi; Lmax_ = Lmax;
    int rc = setup(N, D);
    if (rc < 0) return rc;
    u64 *g = malloc(sizeof(u64) * nw_), *p = malloc(sizeof(u64) * nw_), *src = malloc(sizeof(u64) * nw_);
    long nprod = 0, ndrop = 0;
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
        int A = 0, B = 0;
        if (adj >= 0) row_window(rows_ + q * nw_, &A, &B);
        for (int j = 0; j < N; j++) {
            if (adj >= 0 && (hi[j] < A - adj || lo[j] > B + adj)) continue;
            memcpy(src, rows_ + q * nw_, sizeof(u64) * nw_);   /* rows_ may move on realloc */
            int r = product_row(src, 1ULL << j, p);
            if (r < 0) { free(g); free(p); free(src); return -2; }
            nprod++;
            if (r == 1) { ndrop++; continue; }
            insert(p);
            if (stop_at_one && piv_[0] >= 0) break;
        }
    }
    *out_rank = rank_; *out_one = piv_[0] >= 0; *out_products = nprod; *out_dropped = ndrop;
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
/* locality histogram of the final basis by top-column locality: hist[L] for L=0..maxL (L>maxL -> maxL) */
void my_basis_locality(long *hist, int maxL) {
    for (int l = 0; l <= maxL; l++) hist[l] = 0;
    for (long c = 0; c < ncols_; c++) if (piv_[c] >= 0) { int L = locality(colmask_[c]); if (L > maxL) L = maxL; hist[L]++; }
}
void my_free(void) {
    free(rows_); rows_ = NULL; free(piv_); piv_ = NULL; free(colmask_); colmask_ = NULL; free(coldeg_); coldeg_ = NULL;
    free(hkey_); hkey_ = NULL; free(hval_); hval_ = NULL; rank_ = 0;
}
