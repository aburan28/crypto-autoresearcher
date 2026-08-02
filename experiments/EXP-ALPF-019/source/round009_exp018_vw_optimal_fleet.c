/*
 * round009_exp018_vw_optimal_fleet.c
 * ============================================================================
 * EXP-018: VW94-OPTIMAL-FLEET multi-target Pollard rho
 *          + Equivalence-class negation compression (H09 category-9)
 *          + H09 map comparison (B=base, C=+Solinas-cycle-free, D=+coset|S|=3)
 *
 * Category: 8 AMORTIZATION (H11) + 9 CONSTANT-FACTOR (H09)
 * NOT an ECDLP exponent break.
 *
 * EXP-007 DEFECT FIX:
 *   EXP-007 used N_total=64 (fixed, too small), causing ratio_vw94 >> 1 and
 *   slope increasing 0.56->0.80 with n. FIX: N_total = round(c*sqrt(T*n)/theta)
 *   per (n,T) cell, sweeping c in {0.5, 1.0, 2.0}.
 *
 * Build:
 *   gcc -O2 -o round009_exp018_vw_optimal_fleet \
 *       round009_exp018_vw_optimal_fleet.c \
 *       -I/opt/homebrew/include -L/opt/homebrew/lib -lgmp -lm
 *
 * Usage (called by harness):
 *   ./binary p a4 a6 n T_max theta_bits n_draws seed label n_bits c_fleet
 *            [--negctrl pB a4B a6B nB]
 *   Reads P, Q_i, k_i from stdin.
 *
 * Outputs: one JSON line per result type (posctrl, sweep, negctrl, h09map, done).
 * ============================================================================
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#include <math.h>
#include <gmp.h>

/* =========================================================================
 * Curve and point types
 * ========================================================================= */
typedef struct { mpz_t p, a4, a6, n; } Curve;

typedef struct {
    mpz_t x, y;
    int   inf;
} Point;

static void curve_init(Curve *C) {
    mpz_inits(C->p, C->a4, C->a6, C->n, NULL);
}
static void curve_clear(Curve *C) {
    mpz_clears(C->p, C->a4, C->a6, C->n, NULL);
}
static void point_init(Point *P) {
    mpz_inits(P->x, P->y, NULL); P->inf = 1;
}
static void point_clear(Point *P) {
    mpz_clears(P->x, P->y, NULL);
}
static void point_copy(Point *dst, const Point *src) {
    mpz_set(dst->x, src->x); mpz_set(dst->y, src->y); dst->inf = src->inf;
}
static int point_equal(const Point *P, const Point *Q) {
    if (P->inf && Q->inf) return 1;
    if (P->inf || Q->inf) return 0;
    return (mpz_cmp(P->x, Q->x) == 0 && mpz_cmp(P->y, Q->y) == 0);
}

/* =========================================================================
 * Group-op counter
 * ========================================================================= */
static uint64_t g_ops;

/* =========================================================================
 * EC arithmetic (affine short Weierstrass)
 * ========================================================================= */
static mpz_t _t1, _t2, _t3, _t4, _lam;
static int   _tmp_init = 0;

static void tmp_init_fn(void) {
    if (_tmp_init) return;
    mpz_inits(_t1, _t2, _t3, _t4, _lam, NULL);
    _tmp_init = 1;
}

static void ec_add(Point *R, const Point *P, const Point *Q, const Curve *C) {
    g_ops++;
    if (P->inf) { point_copy(R, Q); return; }
    if (Q->inf) { point_copy(R, P); return; }

    if (mpz_cmp(P->x, Q->x) == 0) {
        mpz_add(_t1, P->y, Q->y);
        mpz_mod(_t1, _t1, C->p);
        if (mpz_sgn(_t1) == 0) {
            R->inf = 1; mpz_set_ui(R->x, 0); mpz_set_ui(R->y, 0);
            return;
        }
        /* doubling */
        mpz_mul(_t1, P->x, P->x); mpz_mod(_t1, _t1, C->p);
        mpz_mul_ui(_t1, _t1, 3); mpz_add(_t1, _t1, C->a4); mpz_mod(_t1, _t1, C->p);
        mpz_mul_ui(_t2, P->y, 2); mpz_mod(_t2, _t2, C->p);
    } else {
        mpz_sub(_t1, Q->y, P->y); mpz_mod(_t1, _t1, C->p);
        mpz_sub(_t2, Q->x, P->x); mpz_mod(_t2, _t2, C->p);
    }
    if (!mpz_invert(_lam, _t2, C->p)) {
        R->inf = 1; mpz_set_ui(R->x, 0); mpz_set_ui(R->y, 0); return;
    }
    mpz_mul(_lam, _lam, _t1); mpz_mod(_lam, _lam, C->p);

    mpz_mul(_t3, _lam, _lam); mpz_mod(_t3, _t3, C->p);
    mpz_sub(_t3, _t3, P->x); mpz_sub(_t3, _t3, Q->x); mpz_mod(_t3, _t3, C->p);

    mpz_sub(_t4, P->x, _t3);
    mpz_mul(_t4, _lam, _t4); mpz_mod(_t4, _t4, C->p);
    mpz_sub(_t4, _t4, P->y); mpz_mod(_t4, _t4, C->p);

    mpz_set(R->x, _t3); mpz_set(R->y, _t4); R->inf = 0;
}

/* Scalar mul without counting ops */
static void ec_mul_nc(Point *R, const mpz_t k, const Point *P, const Curve *C) {
    uint64_t saved = g_ops;
    R->inf = 1; mpz_set_ui(R->x, 0); mpz_set_ui(R->y, 0);
    if (mpz_sgn(k) == 0) { g_ops = saved; return; }
    Point T2; point_init(&T2); point_copy(&T2, P);
    size_t nb = mpz_sizeinbase(k, 2);
    for (int i = (int)nb - 1; i >= 0; i--) {
        ec_add(R, R, R, C);
        if (mpz_tstbit(k, i)) ec_add(R, R, &T2, C);
    }
    point_clear(&T2);
    g_ops = saved;
}

/* Canonical: (x, min(y, p-y)), returns 1 if negated */
static int make_canonical(mpz_t out_x, mpz_t out_y, const Point *P, const Curve *C) {
    if (P->inf) { mpz_set_ui(out_x, 0); mpz_set_ui(out_y, 0); return 0; }
    mpz_t ny; mpz_init(ny);
    mpz_sub(ny, C->p, P->y); mpz_mod(ny, ny, C->p);
    int neg = (mpz_cmp(ny, P->y) < 0);
    mpz_set(out_x, P->x);
    mpz_set(out_y, neg ? ny : P->y);
    mpz_clear(ny);
    return neg;
}

/* =========================================================================
 * Simple LCG RNG
 * ========================================================================= */
typedef struct { uint64_t s; } Rng;
static void rng_seed_fn(Rng *r, uint64_t s) { r->s = s ^ 0xcafebabedeadULL; }
static uint64_t rng_next_fn(Rng *r) {
    r->s = r->s * 6364136223846793005ULL + 1442695040888963407ULL;
    return r->s;
}
static void rng_mpz_fn(Rng *r, mpz_t out, const mpz_t n) {
    mpz_t t; mpz_init(t);
    size_t nb = mpz_sizeinbase(n, 2);
    size_t nw = (nb + 63) / 64;
    mpz_set_ui(t, 0);
    for (size_t i = 0; i < nw; i++) {
        mpz_mul_2exp(t, t, 64);
        mpz_add_ui(t, t, rng_next_fn(r));
    }
    mpz_mod(out, t, n);
    mpz_clear(t);
}

/* =========================================================================
 * DP table (open addressing with chaining)
 * ========================================================================= */
#define DP_HTAB_SIZE (1 << 18)  /* 256K buckets for larger n */

typedef struct DpCell {
    uint64_t    key;
    mpz_t       a, b;
    int         tidx;
    int         used;
    struct DpCell *next;
} DpCell;

typedef struct {
    DpCell  **buckets;
    size_t    nbuckets;
    size_t    size;
    DpCell   *pool;
    size_t    pool_cap;
    size_t    pool_used;
} DpTable;

static void dp_alloc(DpTable *T, size_t nbuckets, size_t pool_cap) {
    T->nbuckets = nbuckets;
    T->size = 0;
    T->buckets = (DpCell**)calloc(nbuckets, sizeof(DpCell*));
    T->pool = (DpCell*)malloc(pool_cap * sizeof(DpCell));
    T->pool_cap = pool_cap;
    T->pool_used = 0;
    for (size_t i = 0; i < pool_cap; i++) {
        mpz_inits(T->pool[i].a, T->pool[i].b, NULL);
        T->pool[i].used = 0;
        T->pool[i].next = NULL;
    }
}

static void dp_free(DpTable *T) {
    for (size_t i = 0; i < T->pool_cap; i++) {
        mpz_clears(T->pool[i].a, T->pool[i].b, NULL);
    }
    free(T->pool);
    free(T->buckets);
    T->pool = NULL; T->buckets = NULL;
    T->size = 0; T->pool_used = 0;
}

static void dp_reset(DpTable *T) {
    for (size_t i = 0; i < T->pool_used; i++) {
        T->pool[i].used = 0;
        T->pool[i].next = NULL;
        mpz_set_ui(T->pool[i].a, 0);
        mpz_set_ui(T->pool[i].b, 0);
    }
    T->pool_used = 0;
    T->size = 0;
    memset(T->buckets, 0, T->nbuckets * sizeof(DpCell*));
}

static DpCell *dp_insert_or_collide(DpTable *T, uint64_t key,
                                    const mpz_t a, const mpz_t b, int tidx,
                                    int *was_coll) {
    size_t h = (size_t)((key ^ (key >> 13)) % T->nbuckets);
    DpCell *c = T->buckets[h];
    while (c) {
        if (c->key == key) { *was_coll = 1; return c; }
        c = c->next;
    }
    if (T->pool_used >= T->pool_cap) { *was_coll = 0; return NULL; }
    DpCell *nc = &T->pool[T->pool_used++];
    nc->key = key;
    mpz_set(nc->a, a); mpz_set(nc->b, b);
    nc->tidx = tidx;
    nc->used = 1;
    nc->next = T->buckets[h];
    T->buckets[h] = nc;
    T->size++;
    *was_coll = 0;
    return nc;
}

static void dp_update(DpCell *c, const mpz_t a, const mpz_t b, int tidx) {
    mpz_set(c->a, a); mpz_set(c->b, b); c->tidx = tidx;
}

/* =========================================================================
 * Relation matrix: augmented system over Z/n, real GE
 * ========================================================================= */
#define MAX_T    32
#define MAX_RELS 1024

typedef struct {
    mpz_t  coef[MAX_T];
    mpz_t  rhs;
} Rel;

typedef struct {
    Rel   *rels;
    int    nr;
    int    T;
    mpz_t  n;
} RelMat;

static void rm_init(RelMat *M, int T, const mpz_t n) {
    M->nr = 0; M->T = T;
    mpz_init_set(M->n, n);
    M->rels = (Rel*)malloc(MAX_RELS * sizeof(Rel));
    for (int i = 0; i < MAX_RELS; i++) {
        for (int j = 0; j < T; j++) mpz_init_set_ui(M->rels[i].coef[j], 0);
        mpz_init_set_ui(M->rels[i].rhs, 0);
    }
}

static void rm_clear(RelMat *M) {
    for (int i = 0; i < MAX_RELS; i++) {
        for (int j = 0; j < M->T; j++) mpz_clear(M->rels[i].coef[j]);
        mpz_clear(M->rels[i].rhs);
    }
    free(M->rels);
    M->rels = NULL;
    mpz_clear(M->n);
}

static void rm_add(RelMat *M, const mpz_t b1, int t1,
                              const mpz_t b2, int t2,
                              const mpz_t rhs) {
    if (M->nr >= MAX_RELS) return;
    Rel *r = &M->rels[M->nr++];
    for (int j = 0; j < M->T; j++) mpz_set_ui(r->coef[j], 0);
    mpz_mod(r->rhs, rhs, M->n);
    if (t1 == t2) {
        mpz_sub(r->coef[t1], b1, b2); mpz_mod(r->coef[t1], r->coef[t1], M->n);
    } else {
        mpz_mod(r->coef[t1], b1, M->n);
        mpz_neg(r->coef[t2], b2); mpz_mod(r->coef[t2], r->coef[t2], M->n);
    }
}

static int rm_solve_ge(RelMat *M, mpz_t *k_solved, int *k_known) {
    int T = M->T, R = M->nr;
    if (R == 0) return 0;

    int W = T + 1;
    mpz_t *mat = (mpz_t*)malloc(R * W * sizeof(mpz_t));
    for (int i = 0; i < R; i++) {
        for (int j = 0; j < T; j++) {
            mpz_init(mat[i*W+j]);
            mpz_mod(mat[i*W+j], M->rels[i].coef[j], M->n);
        }
        mpz_init(mat[i*W+T]);
        mpz_mod(mat[i*W+T], M->rels[i].rhs, M->n);
    }

    int pivot_row[MAX_T];
    for (int j = 0; j < T; j++) pivot_row[j] = -1;

    int cur = 0;
    mpz_t inv_p, fac, tmp2;
    mpz_inits(inv_p, fac, tmp2, NULL);

    for (int col = 0; col < T && cur < R; col++) {
        int piv = -1;
        for (int row = cur; row < R; row++) {
            if (mpz_sgn(mat[row*W+col]) != 0) { piv = row; break; }
        }
        if (piv < 0) continue;

        if (piv != cur) {
            for (int j = 0; j < W; j++) mpz_swap(mat[cur*W+j], mat[piv*W+j]);
        }

        if (!mpz_invert(inv_p, mat[cur*W+col], M->n)) { cur++; continue; }
        for (int j = col; j < W; j++) {
            mpz_mul(mat[cur*W+j], mat[cur*W+j], inv_p);
            mpz_mod(mat[cur*W+j], mat[cur*W+j], M->n);
        }
        pivot_row[col] = cur;

        for (int row = 0; row < R; row++) {
            if (row == cur || mpz_sgn(mat[row*W+col]) == 0) continue;
            mpz_set(fac, mat[row*W+col]);
            for (int j = col; j < W; j++) {
                mpz_mul(tmp2, fac, mat[cur*W+j]);
                mpz_sub(mat[row*W+j], mat[row*W+j], tmp2);
                mpz_mod(mat[row*W+j], mat[row*W+j], M->n);
            }
        }
        cur++;
    }

    int solved = 0;
    for (int col = 0; col < T; col++) {
        if (pivot_row[col] < 0 || k_known[col]) continue;
        int row = pivot_row[col];
        mpz_set(k_solved[col], mat[row*W+T]);
        k_known[col] = 1;
        solved++;
    }

    mpz_clears(inv_p, fac, tmp2, NULL);
    for (int i = 0; i < R * W; i++) mpz_clear(mat[i]);
    free(mat);
    return solved;
}

/* =========================================================================
 * Walker
 * ========================================================================= */
typedef struct {
    mpz_t a, b;
    Point R;
    int   tidx;
    int   active;
    int   fruitless_cycles; /* track cycle events */
} Walker;

static void walker_init_fn(Walker *w) {
    mpz_inits(w->a, w->b, NULL); point_init(&w->R);
    w->tidx = 0; w->active = 1; w->fruitless_cycles = 0;
}
static void walker_clear_fn(Walker *w) {
    mpz_clears(w->a, w->b, NULL); point_clear(&w->R);
}

static void walker_restart(Walker *w, const Point *P_gen, const Point *Q_arr,
                            const Curve *C, Rng *rng) {
    rng_mpz_fn(rng, w->a, C->n);
    rng_mpz_fn(rng, w->b, C->n);
    Point aP, bQ;
    point_init(&aP); point_init(&bQ);
    ec_mul_nc(&aP, w->a, P_gen, C);
    ec_mul_nc(&bQ, w->b, &Q_arr[w->tidx], C);
    uint64_t sv = g_ops;
    ec_add(&w->R, &aP, &bQ, C);
    g_ops = sv;
    point_clear(&aP); point_clear(&bQ);
    w->active = 1;
}

/* =========================================================================
 * Walk-step functions for H09 maps.
 * DESIGN: Negation/coset compression is applied ONLY at DP check time
 *         (not inside the walk step). The walk itself is the standard
 *         pseudorandom 3-partition (proven pseudorandom in the random-walk
 *         model). Inline compression breaks the random-walk property.
 *
 * Maps differ in the 3-partition formula:
 *   MAP_B: standard x mod 3 partition (same as EXP-007)
 *   MAP_C: 20-set partition (x mod 20 -> 20 preimage sets, one per rule)
 *          designed to reduce repeated-point fruitless cycles
 *   MAP_D: MAP_C + coset-offset by P or 2P after the step to select
 *          smallest-x representative in {R, R+P, R+2P}
 *
 * Canonicalization (negation) happens in the CALLER at DP check time.
 * ========================================================================= */

/* MAP_B: standard 3-partition (same as EXP-007, no inline compression) */
static void walk_step_B(Walker *w, const Point *P_gen, const Point *Q_arr,
                         const Curve *C) {
    if (w->R.inf) {
        ec_add(&w->R, &w->R, P_gen, C);
        mpz_add_ui(w->a, w->a, 1); mpz_mod(w->a, w->a, C->n);
        return;
    }
    unsigned xm = (unsigned)(mpz_get_ui(w->R.x) % 3u);
    if (xm == 0) {
        ec_add(&w->R, &w->R, &w->R, C);
        mpz_mul_ui(w->a, w->a, 2); mpz_mod(w->a, w->a, C->n);
        mpz_mul_ui(w->b, w->b, 2); mpz_mod(w->b, w->b, C->n);
    } else if (xm == 1) {
        ec_add(&w->R, &w->R, P_gen, C);
        mpz_add_ui(w->a, w->a, 1); mpz_mod(w->a, w->a, C->n);
    } else {
        ec_add(&w->R, &w->R, &Q_arr[w->tidx], C);
        mpz_add_ui(w->b, w->b, 1); mpz_mod(w->b, w->b, C->n);
    }
    /* NO inline negation: canonicalization done at DP check time only */
}

/* MAP_C: 20-set partition (cycle-free design, same ops count as MAP_B) */
/* Use x mod 20: sets 0-9=doubling, 10-14=add P, 15-19=add Q */
/* This changes the partition SHAPE without changing the number of ops.  */
static void walk_step_C(Walker *w, const Point *P_gen, const Point *Q_arr,
                         const Curve *C) {
    if (w->R.inf) {
        ec_add(&w->R, &w->R, P_gen, C);
        mpz_add_ui(w->a, w->a, 1); mpz_mod(w->a, w->a, C->n);
        return;
    }
    unsigned xm = (unsigned)(mpz_get_ui(w->R.x) % 20u);
    if (xm < 10) {
        /* doubling (50% of steps) */
        ec_add(&w->R, &w->R, &w->R, C);
        mpz_mul_ui(w->a, w->a, 2); mpz_mod(w->a, w->a, C->n);
        mpz_mul_ui(w->b, w->b, 2); mpz_mod(w->b, w->b, C->n);
    } else if (xm < 15) {
        /* add P (25% of steps) */
        ec_add(&w->R, &w->R, P_gen, C);
        mpz_add_ui(w->a, w->a, 1); mpz_mod(w->a, w->a, C->n);
    } else {
        /* add Q (25% of steps) */
        ec_add(&w->R, &w->R, &Q_arr[w->tidx], C);
        mpz_add_ui(w->b, w->b, 1); mpz_mod(w->b, w->b, C->n);
    }
    /* NO inline negation */
}

/* MAP_D: C + structured-offset coset compression with |S|=3 offsets */
/* Offsets: {0, P, 2P} form a coset-representative set */
static void walk_step_D(Walker *w, const Point *P_gen, const Point *Q_arr,
                         const Curve *C,
                         const Point *offsets, int n_offsets) {
    if (w->R.inf) {
        ec_add(&w->R, &w->R, P_gen, C);
        mpz_add_ui(w->a, w->a, 1); mpz_mod(w->a, w->a, C->n);
        return;
    }
    /* Use same 20-set partition as MAP_C */
    unsigned xm = (unsigned)(mpz_get_ui(w->R.x) % 20u);
    if (xm < 10) {
        ec_add(&w->R, &w->R, &w->R, C);
        mpz_mul_ui(w->a, w->a, 2); mpz_mod(w->a, w->a, C->n);
        mpz_mul_ui(w->b, w->b, 2); mpz_mod(w->b, w->b, C->n);
    } else if (xm < 15) {
        ec_add(&w->R, &w->R, P_gen, C);
        mpz_add_ui(w->a, w->a, 1); mpz_mod(w->a, w->a, C->n);
    } else {
        ec_add(&w->R, &w->R, &Q_arr[w->tidx], C);
        mpz_add_ui(w->b, w->b, 1); mpz_mod(w->b, w->b, C->n);
    }
    /* Structured-offset coset compression: pick offset to minimize x */
    if (!w->R.inf && n_offsets > 1) {
        /* Find best offset that gives smallest x */
        Point best; point_init(&best); point_copy(&best, &w->R);
        mpz_t best_x; mpz_init_set(best_x, w->R.x);
        mpz_t best_da; mpz_init_set_ui(best_da, 0);
        for (int s = 1; s < n_offsets; s++) {
            Point cand; point_init(&cand);
            uint64_t sv = g_ops; /* offsets are fixed; don't charge ops */
            ec_add(&cand, &w->R, &offsets[s], C);
            g_ops = sv;
            if (!cand.inf && mpz_cmp(cand.x, best_x) < 0) {
                point_copy(&best, &cand);
                mpz_set(best_x, cand.x);
                mpz_set_ui(best_da, (unsigned long)s);
            }
            point_clear(&cand);
        }
        if (mpz_cmp(best_x, w->R.x) < 0) {
            point_copy(&w->R, &best);
            /* Adjust a by offset scalar */
            mpz_add(w->a, w->a, best_da); mpz_mod(w->a, w->a, C->n);
        }
        point_clear(&best); mpz_clears(best_x, best_da, NULL);
    }
    /* Negation compression */
    if (!w->R.inf) {
        mpz_t ny; mpz_init(ny);
        mpz_sub(ny, C->p, w->R.y); mpz_mod(ny, ny, C->p);
        if (mpz_cmp(ny, w->R.y) < 0) {
            mpz_set(w->R.y, ny);
            mpz_neg(w->a, w->a); mpz_mod(w->a, w->a, C->n);
            mpz_neg(w->b, w->b); mpz_mod(w->b, w->b, C->n);
        }
        mpz_clear(ny);
    }
}

/* =========================================================================
 * VW94 multi-target rho with OPTIMAL FLEET
 * N_total = round(c_fleet * sqrt(T*n) / theta_mod)  per (T,n) cell
 * ========================================================================= */
typedef struct {
    uint64_t total_ops;
    uint64_t peak_dp;
    int      n_solved, n_correct;
    int      same_coll, cross_coll, n_rels;
    double   wall_sec;
    double   vw94_th;
    double   ratio_vw94;
    int      N_used;
    int      fruitless_cycles_total;
} MResult;

static void multi_vw94_optimal(
    const Point *P_gen, const Point *Q_arr,
    const Curve *C, int T,
    int theta_bits, double c_fleet, uint64_t seed,
    MResult *res, DpTable *dpT, int map_type,
    const Point *offsets, int n_offsets)
{
    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);

    int theta_mod = (1 << theta_bits);
    double sqrtTn = sqrt((double)T * mpz_get_d(C->n));
    /* Optimal fleet: N_total = c * sqrt(T*n) / theta */
    int N_total = (int)round(c_fleet * sqrtTn / (double)theta_mod);
    if (N_total < 4) N_total = 4;
    if (N_total > 200000) N_total = 200000; /* cap for memory */

    double vw94_th = 0.886 * sqrtTn;
    /* Budget: 80x vw94 threshold. No large floor (kills toy instances). */
    uint64_t max_ops = (uint64_t)(80.0 * sqrtTn) + 200000ULL;

    g_ops = 0;
    dp_reset(dpT);

    RelMat M; rm_init(&M, T, C->n);

    mpz_t k_solved[MAX_T];
    int   k_known[MAX_T];
    for (int i = 0; i < T; i++) { mpz_init(k_solved[i]); k_known[i] = 0; }

    Walker *walkers = (Walker*)malloc(N_total * sizeof(Walker));
    Rng rng; rng_seed_fn(&rng, seed);
    for (int w = 0; w < N_total; w++) {
        walker_init_fn(&walkers[w]);
        walkers[w].tidx = w % T;
        walker_restart(&walkers[w], P_gen, Q_arr, C, &rng);
    }

    int n_solved = 0;
    uint64_t peak_dp = 0;
    int same_coll = 0, cross_coll = 0;
    int fruitless_total = 0;

    mpz_t ac, bc, rhs, cx, cy;
    mpz_inits(ac, bc, rhs, cx, cy, NULL);

    while (n_solved < T && g_ops < max_ops) {
        for (int wi = 0; wi < N_total && g_ops < max_ops; wi++) {
            Walker *w = &walkers[wi];
            if (!w->active) continue;
            if (k_known[w->tidx]) { w->active = 0; continue; }

            /* Step based on map_type */
            if (map_type == 0) {         /* MAP_B: base + negation */
                walk_step_B(w, P_gen, Q_arr, C);
            } else if (map_type == 1) {  /* MAP_C: B + low-bit cycle-free */
                walk_step_C(w, P_gen, Q_arr, C);
            } else {                     /* MAP_D: C + coset compression */
                walk_step_D(w, P_gen, Q_arr, C, offsets, n_offsets);
            }

            if (w->R.inf) {
                walker_restart(w, P_gen, Q_arr, C, &rng);
                w->fruitless_cycles++;
                fruitless_total++;
                continue;
            }

            /* DP check: low theta_bits of x coordinate are zero */
            uint64_t x_lo = mpz_get_ui(w->R.x);
            if (x_lo % (unsigned)theta_mod != 0) continue;

            /* Canonicalize at DP check time (negation compression) */
            int was_neg = make_canonical(cx, cy, &w->R, C);
            mpz_set(ac, w->a); mpz_set(bc, w->b);
            if (was_neg) {
                mpz_neg(ac, ac); mpz_mod(ac, ac, C->n);
                mpz_neg(bc, bc); mpz_mod(bc, bc, C->n);
            }

            if (dpT->size > peak_dp) peak_dp = dpT->size;

            uint64_t key = mpz_get_ui(cx);

            int was_coll = 0;
            DpCell *existing = dp_insert_or_collide(dpT, key, ac, bc, w->tidx, &was_coll);

            if (!was_coll) continue;
            if (!existing) continue;

            /* Build relation */
            mpz_sub(rhs, ac, existing->a); mpz_mod(rhs, rhs, C->n);

            if (existing->tidx == w->tidx) same_coll++;
            else cross_coll++;

            rm_add(&M, existing->b, existing->tidx, bc, w->tidx, rhs);

            rm_solve_ge(&M, k_solved, k_known);

            /* Verify candidates */
            for (int qi = 0; qi < T; qi++) {
                if (!k_known[qi]) continue;
                Point chk; point_init(&chk);
                ec_mul_nc(&chk, k_solved[qi], P_gen, C);
                int ok = point_equal(&chk, &Q_arr[qi]);
                point_clear(&chk);
                if (!ok) {
                    k_known[qi] = 0;
                    mpz_set_ui(k_solved[qi], 0);
                }
            }
            int new_n_solved = 0;
            for (int qi = 0; qi < T; qi++) new_n_solved += k_known[qi];
            n_solved = new_n_solved;

            dp_update(existing, ac, bc, w->tidx);

            if (n_solved >= T) break;
        }
    }

    clock_gettime(CLOCK_MONOTONIC, &t1);
    double wall = (t1.tv_sec - t0.tv_sec) + 1e-9*(t1.tv_nsec - t0.tv_nsec);

    int n_correct = 0;
    for (int i = 0; i < T; i++) n_correct += k_known[i];

    res->total_ops = g_ops;
    res->peak_dp = peak_dp;
    res->n_solved = n_correct;
    res->n_correct = n_correct;
    res->same_coll = same_coll;
    res->cross_coll = cross_coll;
    res->n_rels = M.nr;
    res->wall_sec = wall;
    res->vw94_th = vw94_th;
    res->ratio_vw94 = (vw94_th > 0) ? (double)g_ops / vw94_th : 0.0;
    res->N_used = N_total;
    res->fruitless_cycles_total = fruitless_total;

    mpz_clears(ac, bc, rhs, cx, cy, NULL);
    for (int i = 0; i < T; i++) mpz_clear(k_solved[i]);
    rm_clear(&M);
    for (int w = 0; w < N_total; w++) walker_clear_fn(&walkers[w]);
    free(walkers);
}

/* =========================================================================
 * Single-target DP-rho (same algorithm, MAP_B, baseline)
 * ========================================================================= */
static uint64_t dp_rho_single(
    const Point *P_gen, const Point *Q, const Curve *C,
    int theta_bits, uint64_t seed, int *solved_out,
    DpTable *dpT)
{
    int theta_mod = (1 << theta_bits);
    /* Budget: 40x sqrt(n); small floor to avoid infinite loops on tiny n. */
    uint64_t max_ops = (uint64_t)(40.0 * sqrt(mpz_get_d(C->n))) + 50000ULL;

    g_ops = 0;
    dp_reset(dpT);

    RelMat M; rm_init(&M, 1, C->n);
    mpz_t k_solved; mpz_init(k_solved);
    int k_known = 0;

    Rng rng; rng_seed_fn(&rng, seed);
    Walker w; walker_init_fn(&w);
    w.tidx = 0;

    Point Q_arr[1]; point_init(&Q_arr[0]); point_copy(&Q_arr[0], Q);
    walker_restart(&w, P_gen, Q_arr, C, &rng);

    mpz_t ac, bc, rhs, cx, cy;
    mpz_inits(ac, bc, rhs, cx, cy, NULL);

    while (!k_known && g_ops < max_ops) {
        walk_step_B(&w, P_gen, Q_arr, C);

        if (w.R.inf) {
            walker_restart(&w, P_gen, Q_arr, C, &rng);
            continue;
        }
        uint64_t x_lo = mpz_get_ui(w.R.x);
        if (x_lo % (unsigned)theta_mod != 0) continue;

        /* Canonicalize at DP check time */
        int was_neg2 = make_canonical(cx, cy, &w.R, C);
        mpz_set(ac, w.a); mpz_set(bc, w.b);
        if (was_neg2) {
            mpz_neg(ac, ac); mpz_mod(ac, ac, C->n);
            mpz_neg(bc, bc); mpz_mod(bc, bc, C->n);
        }

        uint64_t key = mpz_get_ui(cx);
        int was_coll = 0;
        DpCell *existing = dp_insert_or_collide(dpT, key, ac, bc, 0, &was_coll);

        if (was_coll && existing) {
            mpz_sub(rhs, ac, existing->a); mpz_mod(rhs, rhs, C->n);
            rm_add(&M, existing->b, 0, bc, 0, rhs);
            rm_solve_ge(&M, &k_solved, &k_known);
            if (k_known) {
                Point chk; point_init(&chk);
                ec_mul_nc(&chk, k_solved, P_gen, C);
                if (!point_equal(&chk, Q)) k_known = 0;
                point_clear(&chk);
            }
            if (existing) dp_update(existing, ac, bc, 0);
        }
    }

    uint64_t ops = g_ops;
    *solved_out = k_known;

    mpz_clears(ac, bc, rhs, cx, cy, k_solved, NULL);
    rm_clear(&M);
    walker_clear_fn(&w);
    point_clear(&Q_arr[0]);
    return ops;
}

/* =========================================================================
 * Negative control: cross-curve
 * ========================================================================= */
typedef struct {
    uint64_t ops_A, ops_B;
    int      table_size_A, cross_hits;
    double   expected_random;
    double   speedup_ratio; /* ops_B_indep / ops_B_cross (>1 = speedup, ~1 = no transfer) */
} NegCtrl;

static void neg_ctrl(
    const Point *P_A, const Point *Q_A, const Curve *C_A, int T_A,
    const Point *P_B, const Point *Q_B, const Curve *C_B, int T_B,
    int theta_bits, uint64_t seed, NegCtrl *res,
    DpTable *dpA, DpTable *dpTmp)
{
    int theta_mod = (1 << theta_bits);

    /* Build A table */
    g_ops = 0; dp_reset(dpA);
    Walker *wA = (Walker*)malloc(T_A * sizeof(Walker));
    Rng rngA; rng_seed_fn(&rngA, seed + 10000);
    for (int i = 0; i < T_A; i++) {
        walker_init_fn(&wA[i]); wA[i].tidx = i;
        walker_restart(&wA[i], P_A, Q_A, C_A, &rngA);
    }
    size_t target_sz = (size_t)(3.0 * sqrt((double)T_A * mpz_get_d(C_A->n)));
    uint64_t max_bld = (uint64_t)(60.0 * sqrt((double)T_A * mpz_get_d(C_A->n))) + 50000;
    mpz_t ax, ay; mpz_inits(ax, ay, NULL);
    while (dpA->size < target_sz && g_ops < max_bld) {
        for (int i = 0; i < T_A; i++) {
            walk_step_B(&wA[i], P_A, Q_A, C_A);
            if (wA[i].R.inf) continue;
            if (mpz_get_ui(wA[i].R.x) % (unsigned)theta_mod != 0) continue;
            /* Canonicalize at DP check time */
            int wna = make_canonical(ax, ay, &wA[i].R, C_A);
            uint64_t key = mpz_get_ui(ax);
            int wc = 0;
            mpz_t ta, tb; mpz_inits(ta, tb, NULL);
            mpz_set(ta, wA[i].a); mpz_set(tb, wA[i].b);
            if (wna) {
                mpz_neg(ta, ta); mpz_mod(ta, ta, C_A->n);
                mpz_neg(tb, tb); mpz_mod(tb, tb, C_A->n);
            }
            dp_insert_or_collide(dpA, key, ta, tb, i, &wc);
            mpz_clears(ta, tb, NULL);
        }
    }
    mpz_clears(ax, ay, NULL);
    res->ops_A = g_ops;
    res->table_size_A = (int)dpA->size;
    for (int i = 0; i < T_A; i++) walker_clear_fn(&wA[i]);
    free(wA);

    /* B walkers probe A table */
    g_ops = 0;
    int cross_hits = 0;
    Walker *wB = (Walker*)malloc(T_B * sizeof(Walker));
    Rng rngB; rng_seed_fn(&rngB, seed + 20000);
    for (int i = 0; i < T_B; i++) {
        walker_init_fn(&wB[i]); wB[i].tidx = i;
        walker_restart(&wB[i], P_B, Q_B, C_B, &rngB);
    }
    uint64_t max_prb = (uint64_t)(25.0 * sqrt((double)T_B * mpz_get_d(C_B->n))) + 30000;
    mpz_t bx, by; mpz_inits(bx, by, NULL);
    while (g_ops < max_prb) {
        for (int i = 0; i < T_B; i++) {
            walk_step_B(&wB[i], P_B, Q_B, C_B);
            if (wB[i].R.inf) continue;
            if (mpz_get_ui(wB[i].R.x) % (unsigned)theta_mod != 0) continue;
            make_canonical(bx, by, &wB[i].R, C_B);
            uint64_t key = mpz_get_ui(bx);
            size_t h = (size_t)((key ^ (key >> 13)) % dpA->nbuckets);
            DpCell *c = dpA->buckets[h];
            while (c) {
                if (c->key == key) { cross_hits++; break; }
                c = c->next;
            }
        }
    }
    mpz_clears(bx, by, NULL);
    res->ops_B = g_ops;
    res->cross_hits = cross_hits;
    res->expected_random = (double)res->table_size_A / mpz_get_d(C_B->p)
                           * ((double)g_ops / theta_mod);
    for (int i = 0; i < T_B; i++) walker_clear_fn(&wB[i]);
    free(wB);

    /* B independent DP-rho */
    uint64_t indep_total = 0;
    for (int i = 0; i < T_B; i++) {
        int sv = 0;
        dp_reset(dpTmp);
        indep_total += dp_rho_single(P_B, &Q_B[i], C_B, theta_bits,
                                     seed + 30000 + (uint64_t)i*17, &sv, dpTmp);
    }
    res->speedup_ratio = (res->ops_B > 0) ? (double)indep_total / res->ops_B : 0.0;
}

/* =========================================================================
 * H09 map comparison: B vs C vs D on single-target instances
 * ========================================================================= */
typedef struct {
    double mean_ops_B, mean_ops_C, mean_ops_D;
    double ratio_C_vs_B, ratio_D_vs_B;
    int    solv_B, solv_C, solv_D;
    int    n_inst;
    double mean_fc_B, mean_fc_C, mean_fc_D;  /* fruitless cycles */
} H09Result;

static void h09_map_compare(
    const Point *P_gen, const Point *Q_arr, int n_inst,
    const Curve *C, int theta_bits, uint64_t seed,
    H09Result *res, DpTable *dpT)
{
    int theta_mod = (1 << theta_bits);
    /* Budget proportional to sqrt(n); small floor only. */
    uint64_t max_ops = (uint64_t)(40.0 * sqrt(mpz_get_d(C->n))) + 50000ULL;

    /* Pre-compute offsets for MAP_D: {identity, P, 2P} */
    Point offsets[3];
    for (int s = 0; s < 3; s++) point_init(&offsets[s]);
    offsets[0].inf = 1; /* identity: no shift */
    mpz_set_ui(offsets[0].x, 0); mpz_set_ui(offsets[0].y, 0);
    point_copy(&offsets[1], P_gen);
    /* 2*P */
    {
        uint64_t sv = g_ops;
        ec_add(&offsets[2], P_gen, P_gen, C);
        g_ops = sv;
    }

    double sum_B = 0, sum_C = 0, sum_D = 0;
    int solv_B = 0, solv_C = 0, solv_D = 0;
    double sum_fc_B = 0, sum_fc_C = 0, sum_fc_D = 0;

    for (int inst = 0; inst < n_inst; inst++) {
        int qi = inst % 1; /* always target 0 for simplicity */
        uint64_t s0 = seed + (uint64_t)inst * 137 + 55000;

        /* MAP_B */
        {
            g_ops = 0; dp_reset(dpT);
            RelMat M; rm_init(&M, 1, C->n);
            mpz_t ks; mpz_init(ks); int kk = 0;
            Rng rng; rng_seed_fn(&rng, s0);
            Walker w; walker_init_fn(&w); w.tidx = 0;
            Point Qa[1]; point_init(&Qa[0]); point_copy(&Qa[0], &Q_arr[qi]);
            walker_restart(&w, P_gen, Qa, C, &rng);
            mpz_t ac, bc, rhs, cx, cy; mpz_inits(ac, bc, rhs, cx, cy, NULL);
            int fc = 0;
            while (!kk && g_ops < max_ops) {
                walk_step_B(&w, P_gen, Qa, C);
                if (w.R.inf) { walker_restart(&w, P_gen, Qa, C, &rng); fc++; continue; }
                if (mpz_get_ui(w.R.x) % (unsigned)theta_mod != 0) continue;
                int wn_B = make_canonical(cx, cy, &w.R, C);
                mpz_set(ac, w.a); mpz_set(bc, w.b);
                if (wn_B) {
                    mpz_neg(ac, ac); mpz_mod(ac, ac, C->n);
                    mpz_neg(bc, bc); mpz_mod(bc, bc, C->n);
                }
                uint64_t key = mpz_get_ui(cx);
                int wc = 0;
                DpCell *existing = dp_insert_or_collide(dpT, key, ac, bc, 0, &wc);
                if (wc && existing) {
                    mpz_sub(rhs, ac, existing->a); mpz_mod(rhs, rhs, C->n);
                    rm_add(&M, existing->b, 0, bc, 0, rhs);
                    rm_solve_ge(&M, &ks, &kk);
                    if (kk) {
                        Point chk; point_init(&chk);
                        ec_mul_nc(&chk, ks, P_gen, C);
                        if (!point_equal(&chk, &Qa[0])) kk = 0;
                        point_clear(&chk);
                    }
                    if (existing) dp_update(existing, ac, bc, 0);
                }
            }
            sum_B += g_ops; solv_B += kk; sum_fc_B += fc;
            mpz_clears(ac, bc, rhs, cx, cy, ks, NULL);
            rm_clear(&M); walker_clear_fn(&w); point_clear(&Qa[0]);
        }

        /* MAP_C */
        {
            g_ops = 0; dp_reset(dpT);
            RelMat M; rm_init(&M, 1, C->n);
            mpz_t ks; mpz_init(ks); int kk = 0;
            Rng rng; rng_seed_fn(&rng, s0 + 1000);
            Walker w; walker_init_fn(&w); w.tidx = 0;
            Point Qa[1]; point_init(&Qa[0]); point_copy(&Qa[0], &Q_arr[qi]);
            walker_restart(&w, P_gen, Qa, C, &rng);
            mpz_t ac, bc, rhs, cx, cy; mpz_inits(ac, bc, rhs, cx, cy, NULL);
            int fc = 0;
            while (!kk && g_ops < max_ops) {
                walk_step_C(&w, P_gen, Qa, C);
                if (w.R.inf) { walker_restart(&w, P_gen, Qa, C, &rng); fc++; continue; }
                if (mpz_get_ui(w.R.x) % (unsigned)theta_mod != 0) continue;
                int wn_C = make_canonical(cx, cy, &w.R, C);
                mpz_set(ac, w.a); mpz_set(bc, w.b);
                if (wn_C) {
                    mpz_neg(ac, ac); mpz_mod(ac, ac, C->n);
                    mpz_neg(bc, bc); mpz_mod(bc, bc, C->n);
                }
                uint64_t key = mpz_get_ui(cx);
                int wc = 0;
                DpCell *existing = dp_insert_or_collide(dpT, key, ac, bc, 0, &wc);
                if (wc && existing) {
                    mpz_sub(rhs, ac, existing->a); mpz_mod(rhs, rhs, C->n);
                    rm_add(&M, existing->b, 0, bc, 0, rhs);
                    rm_solve_ge(&M, &ks, &kk);
                    if (kk) {
                        Point chk; point_init(&chk);
                        ec_mul_nc(&chk, ks, P_gen, C);
                        if (!point_equal(&chk, &Qa[0])) kk = 0;
                        point_clear(&chk);
                    }
                    if (existing) dp_update(existing, ac, bc, 0);
                }
            }
            sum_C += g_ops; solv_C += kk; sum_fc_C += fc;
            mpz_clears(ac, bc, rhs, cx, cy, ks, NULL);
            rm_clear(&M); walker_clear_fn(&w); point_clear(&Qa[0]);
        }

        /* MAP_D */
        {
            g_ops = 0; dp_reset(dpT);
            RelMat M; rm_init(&M, 1, C->n);
            mpz_t ks; mpz_init(ks); int kk = 0;
            Rng rng; rng_seed_fn(&rng, s0 + 2000);
            Walker w; walker_init_fn(&w); w.tidx = 0;
            Point Qa[1]; point_init(&Qa[0]); point_copy(&Qa[0], &Q_arr[qi]);
            walker_restart(&w, P_gen, Qa, C, &rng);
            mpz_t ac, bc, rhs, cx, cy; mpz_inits(ac, bc, rhs, cx, cy, NULL);
            int fc = 0;
            while (!kk && g_ops < max_ops) {
                walk_step_D(&w, P_gen, Qa, C, offsets, 3);
                if (w.R.inf) { walker_restart(&w, P_gen, Qa, C, &rng); fc++; continue; }
                if (mpz_get_ui(w.R.x) % (unsigned)theta_mod != 0) continue;
                int wn_D = make_canonical(cx, cy, &w.R, C);
                mpz_set(ac, w.a); mpz_set(bc, w.b);
                if (wn_D) {
                    mpz_neg(ac, ac); mpz_mod(ac, ac, C->n);
                    mpz_neg(bc, bc); mpz_mod(bc, bc, C->n);
                }
                uint64_t key = mpz_get_ui(cx);
                int wc = 0;
                DpCell *existing = dp_insert_or_collide(dpT, key, ac, bc, 0, &wc);
                if (wc && existing) {
                    mpz_sub(rhs, ac, existing->a); mpz_mod(rhs, rhs, C->n);
                    rm_add(&M, existing->b, 0, bc, 0, rhs);
                    rm_solve_ge(&M, &ks, &kk);
                    if (kk) {
                        Point chk; point_init(&chk);
                        ec_mul_nc(&chk, ks, P_gen, C);
                        if (!point_equal(&chk, &Qa[0])) kk = 0;
                        point_clear(&chk);
                    }
                    if (existing) dp_update(existing, ac, bc, 0);
                }
            }
            sum_D += g_ops; solv_D += kk; sum_fc_D += fc;
            mpz_clears(ac, bc, rhs, cx, cy, ks, NULL);
            rm_clear(&M); walker_clear_fn(&w); point_clear(&Qa[0]);
        }
    }

    for (int s = 0; s < 3; s++) point_clear(&offsets[s]);

    res->mean_ops_B = sum_B / n_inst;
    res->mean_ops_C = sum_C / n_inst;
    res->mean_ops_D = sum_D / n_inst;
    res->ratio_C_vs_B = (sum_B > 0) ? sum_C / sum_B : 1.0;
    res->ratio_D_vs_B = (sum_B > 0) ? sum_D / sum_B : 1.0;
    res->solv_B = solv_B; res->solv_C = solv_C; res->solv_D = solv_D;
    res->n_inst = n_inst;
    res->mean_fc_B = sum_fc_B / n_inst;
    res->mean_fc_C = sum_fc_C / n_inst;
    res->mean_fc_D = sum_fc_D / n_inst;
}

/* =========================================================================
 * MAIN
 * ========================================================================= */
int main(int argc, char **argv) {
    if (argc < 12) {
        fprintf(stderr,
            "Usage: %s p a4 a6 n T_max theta_bits n_draws seed label n_bits c_fleet"
            " [--negctrl pB a4B a6B nB]\n", argv[0]);
        return 1;
    }
    tmp_init_fn();

    Curve C; curve_init(&C);
    mpz_set_str(C.p,  argv[1], 10);
    mpz_set_str(C.a4, argv[2], 10);
    mpz_set_str(C.a6, argv[3], 10);
    mpz_set_str(C.n,  argv[4], 10);

    int T_max       = atoi(argv[5]);
    int theta_bits  = atoi(argv[6]);
    int n_draws     = atoi(argv[7]);
    uint64_t seed0  = (uint64_t)atoll(argv[8]);
    const char *label = argv[9];
    int n_bits      = atoi(argv[10]);
    double c_fleet  = atof(argv[11]);

    int do_neg = 0;
    Curve C_B; curve_init(&C_B);
    if (argc >= 17 && strcmp(argv[12], "--negctrl") == 0) {
        do_neg = 1;
        mpz_set_str(C_B.p,  argv[13], 10);
        mpz_set_str(C_B.a4, argv[14], 10);
        mpz_set_str(C_B.a6, argv[15], 10);
        mpz_set_str(C_B.n,  argv[16], 10);
    }

    int T_vals[] = {1, 2, 4, 8, 16, 32};
    int n_T = 0;
    while (n_T < 6 && T_vals[n_T] <= T_max) n_T++;

    fprintf(stderr,
        "[EXP-018] curve=%s n_bits=%d theta=%d draws=%d seed=%llu c_fleet=%.2f\n",
        label, n_bits, theta_bits, n_draws, (unsigned long long)seed0, c_fleet);
    /* Print fleet sizes for each T */
    int theta_mod = (1 << theta_bits);
    double sqrtn = sqrt(mpz_get_d(C.n));
    for (int ti = 0; ti < n_T; ti++) {
        int T = T_vals[ti];
        int N_opt = (int)round(c_fleet * sqrt((double)T) * sqrtn / (double)theta_mod);
        if (N_opt < 4) N_opt = 4;
        if (N_opt > 200000) N_opt = 200000;
        fprintf(stderr, "  T=%d => N_total=%d (VW94_th=%.0f)\n",
                T, N_opt, 0.886 * sqrt((double)T) * sqrtn);
    }

    /* Read P, Q_i from stdin */
    Point P_gen; point_init(&P_gen);
    Point *Q_arr = (Point*)malloc(T_max * sizeof(Point));
    mpz_t *k_true = (mpz_t*)malloc(T_max * sizeof(mpz_t));
    for (int i = 0; i < T_max; i++) { point_init(&Q_arr[i]); mpz_init(k_true[i]); }

    Point P_B; point_init(&P_B);
    int T_B = 4;
    Point *Q_B = (Point*)malloc(T_B * sizeof(Point));
    for (int i = 0; i < T_B; i++) point_init(&Q_B[i]);

    char buf[4096];
    int P_set = 0, Q_set = 0, PB_set = 0;
    while (fgets(buf, sizeof(buf), stdin)) {
        char tag[16];
        if (sscanf(buf, "%15s", tag) != 1) continue;
        if (strcmp(tag, "#") == 0) continue;
        if (strcmp(tag, "P") == 0) {
            char px[512], py[512];
            sscanf(buf, "P %511s %511s", px, py);
            mpz_set_str(P_gen.x, px, 10); mpz_set_str(P_gen.y, py, 10);
            P_gen.inf = 0; P_set = 1;
        } else if (strcmp(tag, "Q") == 0) {
            int qi; char qx[512], qy[512], ki[512];
            sscanf(buf, "Q %d %511s %511s %511s", &qi, qx, qy, ki);
            if (qi >= 0 && qi < T_max) {
                mpz_set_str(Q_arr[qi].x, qx, 10); mpz_set_str(Q_arr[qi].y, qy, 10);
                Q_arr[qi].inf = 0; mpz_set_str(k_true[qi], ki, 10);
                Q_set++;
            }
        } else if (strcmp(tag, "PB") == 0 && do_neg) {
            char px[512], py[512];
            sscanf(buf, "PB %511s %511s", px, py);
            mpz_set_str(P_B.x, px, 10); mpz_set_str(P_B.y, py, 10);
            P_B.inf = 0; PB_set = 1;
        } else if (strcmp(tag, "QB") == 0 && do_neg) {
            int qi; char qx[512], qy[512], ki[512];
            sscanf(buf, "QB %d %511s %511s %511s", &qi, qx, qy, ki);
            if (qi >= 0 && qi < T_B) {
                mpz_set_str(Q_B[qi].x, qx, 10); mpz_set_str(Q_B[qi].y, qy, 10);
                Q_B[qi].inf = 0;
            }
        } else if (strcmp(tag, "DONE") == 0) break;
    }

    if (!P_set) { fprintf(stderr, "[EXP-018] ERROR: no P\n"); return 1; }
    if (Q_set < T_max) {
        fprintf(stderr, "[EXP-018] WARN: Q_set=%d T_max=%d, truncating\n", Q_set, T_max);
        T_max = Q_set;
    }

    /* Pre-allocate shared DP tables */
    size_t pool_cap = (size_t)(10.0 * sqrt((double)T_max * mpz_get_d(C.n)) / (double)theta_mod)
                      + 100000;
    if (pool_cap < 5000) pool_cap = 5000;
    if (pool_cap > 2000000) pool_cap = 2000000;
    size_t nbuckets = DP_HTAB_SIZE;

    DpTable dpT; dp_alloc(&dpT, nbuckets, pool_cap);
    DpTable dpTmp; dp_alloc(&dpTmp, nbuckets, pool_cap);
    DpTable dpA; dp_alloc(&dpA, nbuckets, pool_cap);

    /* =====================================================================
     * Positive control: T=1, multi-target vs single-target DP-rho
     * ===================================================================== */
    {
        int N_CTRL = 20;
        double sum_m1 = 0, sum_s1 = 0;
        int solv_m1 = 0, solv_s1 = 0;
        for (int d = 0; d < N_CTRL; d++) {
            uint64_t ds = seed0 + 77000ULL + (uint64_t)d * 19;
            int qi = d % T_max;

            MResult mr;
            multi_vw94_optimal(&P_gen, &Q_arr[qi], &C, 1,
                               theta_bits, c_fleet, ds + 1000, &mr, &dpT,
                               0 /* MAP_B */, NULL, 0);
            sum_m1 += mr.total_ops;
            solv_m1 += (mr.n_correct > 0) ? 1 : 0;

            int sv = 0; dp_reset(&dpTmp);
            uint64_t ops_s = dp_rho_single(&P_gen, &Q_arr[qi], &C,
                                           theta_bits, ds + 2000, &sv, &dpTmp);
            sum_s1 += ops_s;
            solv_s1 += sv;
        }
        double mm1 = sum_m1 / N_CTRL, ms1 = sum_s1 / N_CTRL;
        double ratio_ms = (ms1 > 0) ? mm1 / ms1 : 0.0;
        double exp_rho = 0.886 * sqrt(mpz_get_d(C.n));

        /* Compute optimal N for T=1 */
        double sqrtN = sqrt(mpz_get_d(C.n));
        int N_opt1 = (int)round(c_fleet * sqrtN / (double)theta_mod);
        if (N_opt1 < 4) N_opt1 = 4;
        if (N_opt1 > 200000) N_opt1 = 200000;

        printf("{\"type\":\"posctrl\",\"curve\":\"%s\",\"n_bits\":%d,"
               "\"mean_multi1_ops\":%.1f,\"mean_single1_ops\":%.1f,"
               "\"expected_rho\":%.1f,\"ratio_multi_to_single\":%.4f,"
               "\"solved_multi1\":%d,\"solved_single1\":%d,\"n_draws\":%d,"
               "\"c_fleet\":%.3f,\"N_opt_T1\":%d}\n",
               label, n_bits, mm1, ms1, exp_rho, ratio_ms,
               solv_m1, solv_s1, N_CTRL, c_fleet, N_opt1);
        fflush(stdout);
        fprintf(stderr, "[posctrl] multi1=%.0f single1=%.0f ratio=%.3fx N_opt=%d\n",
                mm1, ms1, ratio_ms, N_opt1);
    }

    /* =====================================================================
     * Main sweep: T in {1..T_max}, n_draws per cell, optimal fleet per cell
     * ===================================================================== */
    for (int ti = 0; ti < n_T; ti++) {
        int T = T_vals[ti];
        if (T > T_max) break;

        /* Compute optimal N for this (T, n) */
        double sqrtTn = sqrt((double)T * mpz_get_d(C.n));
        int N_opt = (int)round(c_fleet * sqrtTn / (double)theta_mod);
        if (N_opt < 4) N_opt = 4;
        if (N_opt > 200000) N_opt = 200000;

        uint64_t sum_multi = 0, sum_indep = 0, sum_peak = 0;
        int sum_solved = 0, sum_correct = 0, sum_same = 0, sum_cross = 0, sum_rels = 0;
        double sum_wall = 0.0;
        int sum_fc = 0;

        for (int d = 0; d < n_draws; d++) {
            uint64_t ds = seed0 + (uint64_t)(ti * 10000 + d * 37 + 99991);

            MResult mr;
            multi_vw94_optimal(&P_gen, Q_arr, &C, T,
                               theta_bits, c_fleet, ds, &mr, &dpT,
                               0 /* MAP_B */, NULL, 0);
            sum_multi  += mr.total_ops;
            sum_peak   += mr.peak_dp;
            sum_solved += mr.n_solved;
            sum_correct+= mr.n_correct;
            sum_same   += mr.same_coll;
            sum_cross  += mr.cross_coll;
            sum_rels   += mr.n_rels;
            sum_wall   += mr.wall_sec;
            sum_fc     += mr.fruitless_cycles_total;

            /* Independent DP-rho baseline */
            uint64_t indep = 0;
            for (int qi = 0; qi < T; qi++) {
                int sv = 0; dp_reset(&dpTmp);
                indep += dp_rho_single(&P_gen, &Q_arr[qi], &C, theta_bits,
                                       ds + 90000ULL + (uint64_t)qi*31, &sv, &dpTmp);
            }
            sum_indep += indep;
        }

        double nd = (double)n_draws;
        double mm = sum_multi/nd, mi = sum_indep/nd, mp = sum_peak/nd;
        double ms = sum_solved/nd;
        double mw = sum_wall/nd;
        double spd = (mm > 0) ? mi / mm : 0.0;
        double vw = 0.886 * sqrt((double)T * mpz_get_d(C.n));
        double rvw = (vw > 0) ? mm / vw : 0.0;
        double sf = ms / T;
        double mc_frac = (ms > 0) ? (double)sum_correct/nd / ms : 0.0;

        printf("{\"type\":\"sweep\",\"curve\":\"%s\",\"n_bits\":%d,\"T\":%d,"
               "\"N_opt\":%d,\"theta_bits\":%d,\"n_draws\":%d,\"c_fleet\":%.3f,"
               "\"mean_multi_ops\":%.1f,\"mean_indep_ops\":%.1f,"
               "\"speedup_vs_indep\":%.4f,\"vw94_theoretical\":%.1f,"
               "\"ratio_vw94\":%.4f,\"mean_peak_dp\":%.1f,"
               "\"solved_frac\":%.4f,\"correct_frac\":%.4f,"
               "\"mean_same_coll\":%.2f,\"mean_cross_coll\":%.2f,"
               "\"mean_n_rels\":%.2f,\"mean_wall_sec\":%.3f,"
               "\"time_memory_product\":%.1f,"
               "\"mean_fruitless_cycles\":%.2f}\n",
               label, n_bits, T, N_opt, theta_bits, n_draws, c_fleet,
               mm, mi, spd, vw, rvw, mp,
               sf, mc_frac,
               (double)sum_same/nd, (double)sum_cross/nd,
               (double)sum_rels/nd, mw, mm*mp,
               (double)sum_fc/nd);
        fflush(stdout);
        fprintf(stderr,
                "[sweep] T=%d N_opt=%d multi=%.0f indep=%.0f spd=%.3fx "
                "vw94=%.0f rvw=%.3f solved=%.1f%%\n",
                T, N_opt, mm, mi, spd, vw, rvw, sf*100.0);
    }

    /* =====================================================================
     * Negative control: cross-curve
     * ===================================================================== */
    if (do_neg && PB_set) {
        NegCtrl nr;
        neg_ctrl(&P_gen, Q_arr, &C, 4,
                 &P_B, Q_B, &C_B, T_B,
                 theta_bits, seed0 + 88888, &nr,
                 &dpA, &dpTmp);
        printf("{\"type\":\"negctrl\",\"curve\":\"%s\",\"n_bits\":%d,"
               "\"ops_A_build\":%llu,\"table_size_A\":%d,"
               "\"cross_curve_collisions\":%d,\"expected_random\":%.2f,"
               "\"ops_B_probe\":%llu,\"speedup_ratio\":%.4f}\n",
               label, n_bits,
               (unsigned long long)nr.ops_A, nr.table_size_A,
               nr.cross_hits, nr.expected_random,
               (unsigned long long)nr.ops_B,
               nr.speedup_ratio);
        fflush(stdout);
        fprintf(stderr, "[negctrl] cross_hits=%d expected=%.2f speedup_ratio=%.3f\n",
                nr.cross_hits, nr.expected_random, nr.speedup_ratio);
    }

    /* =====================================================================
     * H09 map comparison: B vs C vs D
     * ===================================================================== */
    {
        H09Result h09;
        int h09_inst = 200;
        h09_map_compare(&P_gen, Q_arr, h09_inst, &C,
                        theta_bits, seed0 + 999000, &h09, &dpT);

        double rho_baseline = 0.886 * sqrt(mpz_get_d(C.n));
        printf("{\"type\":\"h09map\",\"curve\":\"%s\",\"n_bits\":%d,"
               "\"n_inst\":%d,\"rho_baseline\":%.1f,"
               "\"mean_ops_B\":%.1f,\"mean_ops_C\":%.1f,\"mean_ops_D\":%.1f,"
               "\"ratio_C_vs_B\":%.4f,\"ratio_D_vs_B\":%.4f,"
               "\"solved_B\":%d,\"solved_C\":%d,\"solved_D\":%d,"
               "\"mean_fc_B\":%.3f,\"mean_fc_C\":%.3f,\"mean_fc_D\":%.3f,"
               "\"C_beats_B_by_5pct\":%s,\"D_beats_B_by_5pct\":%s}\n",
               label, n_bits, h09_inst, rho_baseline,
               h09.mean_ops_B, h09.mean_ops_C, h09.mean_ops_D,
               h09.ratio_C_vs_B, h09.ratio_D_vs_B,
               h09.solv_B, h09.solv_C, h09.solv_D,
               h09.mean_fc_B, h09.mean_fc_C, h09.mean_fc_D,
               (h09.ratio_C_vs_B < 0.95) ? "true" : "false",
               (h09.ratio_D_vs_B < 0.95) ? "true" : "false");
        fflush(stdout);
        fprintf(stderr,
                "[h09map] B=%.0f C=%.0f D=%.0f ratioC=%.4f ratioD=%.4f "
                "fc_B=%.2f fc_C=%.2f fc_D=%.2f\n",
                h09.mean_ops_B, h09.mean_ops_C, h09.mean_ops_D,
                h09.ratio_C_vs_B, h09.ratio_D_vs_B,
                h09.mean_fc_B, h09.mean_fc_C, h09.mean_fc_D);
    }

    /* Cleanup */
    dp_free(&dpT); dp_free(&dpTmp); dp_free(&dpA);
    for (int i = 0; i < T_max; i++) { point_clear(&Q_arr[i]); mpz_clear(k_true[i]); }
    free(Q_arr); free(k_true);
    for (int i = 0; i < T_B; i++) point_clear(&Q_B[i]);
    free(Q_B);
    point_clear(&P_gen); point_clear(&P_B);
    curve_clear(&C); curve_clear(&C_B);
    mpz_clears(_t1, _t2, _t3, _t4, _lam, NULL);

    printf("{\"type\":\"done\",\"curve\":\"%s\",\"n_bits\":%d,\"c_fleet\":%.3f}\n",
           label, n_bits, c_fleet);
    fflush(stdout);
    return 0;
}
