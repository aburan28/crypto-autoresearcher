/*
 * round004_exp007_vw_multitarget.c
 * ============================================================================
 * EXP-007: VW94-CORRECT multi-target Pollard rho with REAL pooled Z/n solve
 *          and n-TREND across 3 field sizes.
 * Category: 8 AMORTIZATION (NOT an ECDLP exponent break)
 * ============================================================================
 *
 * DEFECT-C FIXES:
 * C1: Real GE over Z/n (augmented matrix, partial pivoting) -- not stub
 * C2: Fixed N_total walkers shared across ALL T targets
 * C3: Baseline = T independent single-target DP-rho (same algorithm, not Floyd)
 * C4: n-trend: 3 field sizes, slope per size
 *
 * Build:
 *   gcc -O2 -o round004_exp007_vw_multitarget \
 *       round004_exp007_vw_multitarget.c \
 *       -I/opt/homebrew/include -L/opt/homebrew/lib -lgmp -lm
 *
 * Usage: ./binary p a4 a6 n T_max N_total theta_bits n_draws seed label n_bits
 *        Reads P, Q_i, k_i from stdin.
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

    /* Handle aliasing: compute into temps first (already done) */
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
    /* Rejection-free for toy sizes: take hi64 bits modulo n */
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
 * DP table using C stdlib uthash-style open addressing
 * Key: uint64_t (low 64 bits of x, sufficient for toy n < 2^30)
 * Value: (a, b, tidx) stored as mpz_t
 * ========================================================================= */
#define DP_HTAB_SIZE (1 << 17)  /* 128K buckets, enough for 2^26 sqrt ~ 8K entries */

typedef struct DpCell {
    uint64_t    key;      /* x_lo */
    mpz_t       a, b;
    int         tidx;
    int         used;
    struct DpCell *next;  /* chaining for collisions */
} DpCell;

typedef struct {
    DpCell  **buckets;  /* array of pointers (NULL = empty) */
    size_t    nbuckets;
    size_t    size;
    /* pool of cells */
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

/* Returns NULL if full. On collision: returns existing cell (was_coll=1) + stores new in *new_out. */
static DpCell *dp_insert_or_collide(DpTable *T, uint64_t key,
                                    const mpz_t a, const mpz_t b, int tidx,
                                    int *was_coll) {
    size_t h = (size_t)((key ^ (key >> 13)) % T->nbuckets);
    DpCell *c = T->buckets[h];
    while (c) {
        if (c->key == key) { *was_coll = 1; return c; }
        c = c->next;
    }
    /* New entry */
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

/* Update existing cell's (a,b,tidx) */
static void dp_update(DpCell *c, const mpz_t a, const mpz_t b, int tidx) {
    mpz_set(c->a, a); mpz_set(c->b, b); c->tidx = tidx;
}

/* =========================================================================
 * Relation matrix: augmented system over Z/n, real GE (FIX-C1)
 * ========================================================================= */
#define MAX_T    32
#define MAX_RELS 512

typedef struct {
    mpz_t  coef[MAX_T];
    mpz_t  rhs;
} Rel;

typedef struct {
    Rel   *rels;   /* heap-allocated array of MAX_RELS */
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

/* Add relation: b1*k_{t1} - b2*k_{t2} = rhs  (mod n) */
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

/*
 * Real Gaussian elimination over Z/n (n prime).
 * FIX-C1: full GE, NOT forward-substitution stub.
 * Modifies M->rels in-place (reduced row echelon form).
 * Writes solutions to k_solved[]; marks k_known[].
 * Returns number of newly solved targets.
 */
static int rm_solve_ge(RelMat *M, mpz_t *k_solved, int *k_known) {
    int T = M->T, R = M->nr;
    if (R == 0) return 0;

    /* Work on a copy of the matrix */
    int W = T + 1;  /* augmented width */
    /* Allocate flat array */
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
        /* Find non-zero pivot */
        int piv = -1;
        for (int row = cur; row < R; row++) {
            if (mpz_sgn(mat[row*W+col]) != 0) { piv = row; break; }
        }
        if (piv < 0) continue;

        /* Swap */
        if (piv != cur) {
            for (int j = 0; j < W; j++) mpz_swap(mat[cur*W+j], mat[piv*W+j]);
        }

        /* Normalize */
        if (!mpz_invert(inv_p, mat[cur*W+col], M->n)) { cur++; continue; }
        for (int j = col; j < W; j++) {
            mpz_mul(mat[cur*W+j], mat[cur*W+j], inv_p);
            mpz_mod(mat[cur*W+j], mat[cur*W+j], M->n);
        }
        pivot_row[col] = cur;

        /* Eliminate all other rows */
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
        k_known[col] = 1;  /* mark as candidate; caller must verify */
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
} Walker;

static void walker_init_fn(Walker *w) {
    mpz_inits(w->a, w->b, NULL); point_init(&w->R);
    w->tidx = 0; w->active = 1;
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

static void walk_step_fn(Walker *w, const Point *P_gen, const Point *Q_arr,
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
}

/* =========================================================================
 * Multi-target VW94-correct rho (FIX-C1, C2)
 * ========================================================================= */
typedef struct {
    uint64_t total_ops;
    uint64_t peak_dp;
    int      n_solved, n_correct;
    int      same_coll, cross_coll, n_rels;
    double   wall_sec;
    double   vw94_th;
    double   ratio_vw94;
} MResult;

static void multi_vw94(
    const Point *P_gen, const Point *Q_arr,
    const Curve *C, int T,
    int N_total, int theta_bits, uint64_t seed,
    MResult *res, DpTable *dpT, RelMat *M_ext)
{
    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);

    int theta_mod = (1 << theta_bits);
    double vw94_th = 0.886 * sqrt((double)T * mpz_get_d(C->n));
    uint64_t max_ops = (uint64_t)(80.0 * sqrt((double)T * mpz_get_d(C->n))) + 3000000ULL;

    g_ops = 0;
    dp_reset(dpT);

    RelMat M_local;
    RelMat *M = M_ext ? M_ext : &M_local;
    if (!M_ext) rm_init(&M_local, T, C->n);
    else {
        M->nr = 0;  /* reset relation count */
        M->T = T;
        mpz_set(M->n, C->n);
    }

    mpz_t k_solved[MAX_T];
    int   k_known[MAX_T];
    for (int i = 0; i < T; i++) { mpz_init(k_solved[i]); k_known[i] = 0; }

    /* FIX-C2: Fixed N_total walkers shared across ALL T targets */
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

    mpz_t ac, bc, rhs;
    mpz_inits(ac, bc, rhs, NULL);
    mpz_t cx, cy;
    mpz_inits(cx, cy, NULL);

    while (n_solved < T && g_ops < max_ops) {
        for (int wi = 0; wi < N_total; wi++) {
            Walker *w = &walkers[wi];
            if (!w->active) continue;
            if (k_known[w->tidx]) { w->active = 0; continue; }

            walk_step_fn(w, P_gen, Q_arr, C);

            if (w->R.inf) {
                walker_restart(w, P_gen, Q_arr, C, &rng);
                continue;
            }

            /* DP check */
            uint64_t x_lo = mpz_get_ui(w->R.x);
            if (x_lo % (unsigned)theta_mod != 0) continue;

            /* Canonicalize */
            int was_neg = make_canonical(cx, cy, &w->R, C);
            mpz_set(ac, w->a); mpz_set(bc, w->b);
            if (was_neg) {
                mpz_neg(ac, ac); mpz_mod(ac, ac, C->n);
                mpz_neg(bc, bc); mpz_mod(bc, bc, C->n);
            }

            if (dpT->size > peak_dp) peak_dp = dpT->size;

            /* Recompute key from canonical x */
            uint64_t key = mpz_get_ui(cx);

            int was_coll = 0;
            DpCell *existing = dp_insert_or_collide(dpT, key, ac, bc, w->tidx, &was_coll);

            if (!was_coll) continue;
            if (!existing) continue;

            /* Build relation: existing_b*k_{existing_t} - bc*k_{w_tidx} = ac - existing_a */
            mpz_sub(rhs, ac, existing->a); mpz_mod(rhs, rhs, C->n);

            if (existing->tidx == w->tidx) same_coll++;
            else cross_coll++;

            /* FIX-C1: Add ALL collisions to relation matrix */
            rm_add(M, existing->b, existing->tidx, bc, w->tidx, rhs);

            /* Run GE -- fills k_solved[col] and k_known[col] for new candidates */
            rm_solve_ge(M, k_solved, k_known);

            /* Verify each candidate against PUBLIC k*P==Q; unset k_known if wrong */
            for (int qi = 0; qi < T; qi++) {
                if (!k_known[qi]) continue;
                /* Recompute: is this solution verified? */
                Point chk2; point_init(&chk2);
                ec_mul_nc(&chk2, k_solved[qi], P_gen, C);
                int ok = point_equal(&chk2, &Q_arr[qi]);
                point_clear(&chk2);
                if (!ok) {
                    /* Wrong candidate: unset so we keep looking */
                    k_known[qi] = 0;
                    mpz_set_ui(k_solved[qi], 0);
                }
            }
            /* Recount verified */
            int new_n_solved = 0;
            for (int qi = 0; qi < T; qi++) new_n_solved += k_known[qi];
            n_solved = new_n_solved;

            /* Overwrite DP entry */
            dp_update(existing, ac, bc, w->tidx);

            if (n_solved >= T) break;
        }
    }

    clock_gettime(CLOCK_MONOTONIC, &t1);
    double wall = (t1.tv_sec - t0.tv_sec) + 1e-9*(t1.tv_nsec - t0.tv_nsec);

    /* All solutions already verified inline (k_known[i] set only if k_i*P==Q_i) */
    int n_correct = 0;
    for (int i = 0; i < T; i++) n_correct += k_known[i];

    res->total_ops = g_ops;
    res->peak_dp = peak_dp;
    res->n_solved = n_correct;    /* n_solved = verified solutions */
    res->n_correct = n_correct;
    res->same_coll = same_coll;
    res->cross_coll = cross_coll;
    res->n_rels = M->nr;
    res->wall_sec = wall;
    res->vw94_th = vw94_th;
    res->ratio_vw94 = (vw94_th > 0) ? (double)g_ops / vw94_th : 0.0;

    mpz_clears(ac, bc, rhs, cx, cy, NULL);
    for (int i = 0; i < T; i++) mpz_clear(k_solved[i]);
    if (!M_ext) rm_clear(&M_local);
    for (int w = 0; w < N_total; w++) walker_clear_fn(&walkers[w]);
    free(walkers);
}

/* =========================================================================
 * FIX-C3: Single-target DP-rho (same algorithm as multi-target, not Floyd)
 * ========================================================================= */
static uint64_t dp_rho_single(
    const Point *P_gen, const Point *Q, const Curve *C,
    int theta_bits, uint64_t seed, int *solved_out,
    DpTable *dpT)
{
    int theta_mod = (1 << theta_bits);
    uint64_t max_ops = (uint64_t)(40.0 * sqrt(mpz_get_d(C->n))) + 800000ULL;

    g_ops = 0;
    dp_reset(dpT);

    RelMat M; rm_init(&M, 1, C->n);
    mpz_t k_solved; mpz_init(k_solved);
    int k_known = 0;

    Rng rng; rng_seed_fn(&rng, seed);
    Walker w; walker_init_fn(&w);
    w.tidx = 0;

    /* Treat Q as a 1-element array */
    Point Q_arr[1]; point_init(&Q_arr[0]); point_copy(&Q_arr[0], Q);
    walker_restart(&w, P_gen, Q_arr, C, &rng);

    mpz_t ac, bc, rhs, cx, cy;
    mpz_inits(ac, bc, rhs, cx, cy, NULL);

    while (!k_known && g_ops < max_ops) {
        walk_step_fn(&w, P_gen, Q_arr, C);

        if (w.R.inf) {
            walker_restart(&w, P_gen, Q_arr, C, &rng);
            continue;
        }
        uint64_t x_lo = mpz_get_ui(w.R.x);
        if (x_lo % (unsigned)theta_mod != 0) continue;

        int was_neg = make_canonical(cx, cy, &w.R, C);
        mpz_set(ac, w.a); mpz_set(bc, w.b);
        if (was_neg) {
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
                if (!point_equal(&chk, Q)) k_known = 0;  /* false candidate */
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
    uint64_t ops_A, ops_B, ops_B_indep;
    int      table_size_A, cross_hits;
    double   expected_random, speedup;
} NegCtrl;

static void neg_ctrl(
    const Point *P_A, const Point *Q_A, const Curve *C_A, int T_A,
    const Point *P_B, const Point *Q_B, const Curve *C_B, int T_B,
    int theta_bits, uint64_t seed, NegCtrl *res,
    DpTable *dpA, DpTable *dpTmp)
{
    int theta_mod = (1 << theta_bits);

    /* Step 1: Build A table */
    g_ops = 0; dp_reset(dpA);
    Walker *wA = (Walker*)malloc(T_A * sizeof(Walker));
    Rng rngA; rng_seed_fn(&rngA, seed + 10000);
    for (int i = 0; i < T_A; i++) {
        walker_init_fn(&wA[i]); wA[i].tidx = i;
        walker_restart(&wA[i], P_A, Q_A, C_A, &rngA);
    }
    size_t target_sz = (size_t)(3.0 * sqrt((double)T_A * mpz_get_d(C_A->n)));
    uint64_t max_bld = (uint64_t)(60.0 * sqrt((double)T_A * mpz_get_d(C_A->n))) + 500000;
    mpz_t ax, ay; mpz_inits(ax, ay, NULL);
    while (dpA->size < target_sz && g_ops < max_bld) {
        for (int i = 0; i < T_A; i++) {
            walk_step_fn(&wA[i], P_A, Q_A, C_A);
            if (wA[i].R.inf) continue;
            if (mpz_get_ui(wA[i].R.x) % (unsigned)theta_mod != 0) continue;
            int wn = make_canonical(ax, ay, &wA[i].R, C_A);
            mpz_t ta, tb; mpz_inits(ta, tb, NULL);
            mpz_set(ta, wA[i].a); mpz_set(tb, wA[i].b);
            if (wn) {
                mpz_neg(ta, ta); mpz_mod(ta, ta, C_A->n);
                mpz_neg(tb, tb); mpz_mod(tb, tb, C_A->n);
            }
            uint64_t key = mpz_get_ui(ax);
            int wc = 0;
            dp_insert_or_collide(dpA, key, ta, tb, i, &wc);
            mpz_clears(ta, tb, NULL);
        }
    }
    mpz_clears(ax, ay, NULL);
    res->ops_A = g_ops;
    res->table_size_A = (int)dpA->size;
    for (int i = 0; i < T_A; i++) walker_clear_fn(&wA[i]);
    free(wA);

    /* Step 2: B walkers probe A table */
    g_ops = 0;
    int cross_hits = 0;
    Walker *wB = (Walker*)malloc(T_B * sizeof(Walker));
    Rng rngB; rng_seed_fn(&rngB, seed + 20000);
    for (int i = 0; i < T_B; i++) {
        walker_init_fn(&wB[i]); wB[i].tidx = i;
        walker_restart(&wB[i], P_B, Q_B, C_B, &rngB);
    }
    uint64_t max_prb = (uint64_t)(25.0 * sqrt((double)T_B * mpz_get_d(C_B->n))) + 300000;
    mpz_t bx, by; mpz_inits(bx, by, NULL);
    while (g_ops < max_prb) {
        for (int i = 0; i < T_B; i++) {
            walk_step_fn(&wB[i], P_B, Q_B, C_B);
            if (wB[i].R.inf) continue;
            if (mpz_get_ui(wB[i].R.x) % (unsigned)theta_mod != 0) continue;
            make_canonical(bx, by, &wB[i].R, C_B);
            uint64_t key = mpz_get_ui(bx);
            /* Lookup in A table (just check for collision, don't solve) */
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

    /* Step 3: Independent DP-rho for B */
    uint64_t indep_total = 0;
    for (int i = 0; i < T_B; i++) {
        int sv = 0;
        dp_reset(dpTmp);
        indep_total += dp_rho_single(P_B, &Q_B[i], C_B, theta_bits,
                                     seed + 30000 + (uint64_t)i*17, &sv, dpTmp);
    }
    res->ops_B_indep = indep_total;
    res->speedup = (res->ops_B > 0) ? (double)res->ops_B_indep / res->ops_B : 0.0;
}

/* =========================================================================
 * MAIN
 * ========================================================================= */
int main(int argc, char **argv) {
    if (argc < 12) {
        fprintf(stderr,
            "Usage: %s p a4 a6 n T_max N_total theta_bits n_draws seed label n_bits"
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
    int N_total     = atoi(argv[6]);
    int theta_bits  = atoi(argv[7]);
    int n_draws     = atoi(argv[8]);
    uint64_t seed0  = (uint64_t)atoll(argv[9]);
    const char *label = argv[10];
    int n_bits      = atoi(argv[11]);

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

    fprintf(stderr, "[EXP-007] curve=%s n_bits=%d N_total=%d theta=%d draws=%d seed=%llu\n",
            label, n_bits, N_total, theta_bits, n_draws, (unsigned long long)seed0);

    /* Read P, Q_i, k_i from stdin */
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
            char px[256], py[256];
            sscanf(buf, "P %255s %255s", px, py);
            mpz_set_str(P_gen.x, px, 10); mpz_set_str(P_gen.y, py, 10);
            P_gen.inf = 0; P_set = 1;
        } else if (strcmp(tag, "Q") == 0) {
            int qi; char qx[256], qy[256], ki[256];
            sscanf(buf, "Q %d %255s %255s %255s", &qi, qx, qy, ki);
            if (qi >= 0 && qi < T_max) {
                mpz_set_str(Q_arr[qi].x, qx, 10); mpz_set_str(Q_arr[qi].y, qy, 10);
                Q_arr[qi].inf = 0; mpz_set_str(k_true[qi], ki, 10);
                Q_set++;
            }
        } else if (strcmp(tag, "PB") == 0 && do_neg) {
            char px[256], py[256];
            sscanf(buf, "PB %255s %255s", px, py);
            mpz_set_str(P_B.x, px, 10); mpz_set_str(P_B.y, py, 10);
            P_B.inf = 0; PB_set = 1;
        } else if (strcmp(tag, "QB") == 0 && do_neg) {
            int qi; char qx[256], qy[256], ki[256];
            sscanf(buf, "QB %d %255s %255s %255s", &qi, qx, qy, ki);
            if (qi >= 0 && qi < T_B) {
                mpz_set_str(Q_B[qi].x, qx, 10); mpz_set_str(Q_B[qi].y, qy, 10);
                Q_B[qi].inf = 0;
            }
        } else if (strcmp(tag, "DONE") == 0) break;
    }

    if (!P_set) { fprintf(stderr, "[EXP-007] ERROR: no P\n"); return 1; }
    if (Q_set < T_max) {
        fprintf(stderr, "[EXP-007] WARN: Q_set=%d T_max=%d, truncating\n", Q_set, T_max);
        T_max = Q_set;
    }
    fprintf(stderr, "[EXP-007] P=(%s,...) Q_set=%d\n",
            mpz_get_str(NULL, 10, P_gen.x), Q_set);

    /* Pre-allocate shared DP tables and relation matrix */
    size_t pool_cap = (size_t)(6.0 * sqrt((double)T_max * mpz_get_d(C.n))) + 50000;
    size_t nbuckets = DP_HTAB_SIZE;
    if (pool_cap < 2000) pool_cap = 2000;
    if (pool_cap > 500000) pool_cap = 500000;

    DpTable dpT; dp_alloc(&dpT, nbuckets, pool_cap);
    DpTable dpTmp; dp_alloc(&dpTmp, nbuckets, pool_cap);
    DpTable dpA; dp_alloc(&dpA, nbuckets, pool_cap);
    RelMat M; rm_init(&M, T_max, C.n);

    /* =====================================================================
     * Positive control: T=1, 20 draws
     * ===================================================================== */
    {
        int N_CTRL = 20;
        double sum_m1 = 0, sum_s1 = 0;
        int solv_m1 = 0, solv_s1 = 0;
        for (int d = 0; d < N_CTRL; d++) {
            uint64_t ds = seed0 + 77000ULL + (uint64_t)d * 19;
            int qi = d % T_max;
            MResult mr;
            multi_vw94(&P_gen, &Q_arr[qi], &C, 1, N_total, theta_bits,
                       ds + 1000, &mr, &dpT, NULL);
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
        printf("{\"type\":\"posctrl\",\"curve\":\"%s\",\"n_bits\":%d,"
               "\"mean_multi1_ops\":%.1f,\"mean_single1_ops\":%.1f,"
               "\"expected_rho\":%.1f,\"ratio_multi_to_single\":%.4f,"
               "\"solved_multi1\":%d,\"solved_single1\":%d,\"n_draws\":%d}\n",
               label, n_bits, mm1, ms1, exp_rho, ratio_ms,
               solv_m1, solv_s1, N_CTRL);
        fflush(stdout);
        fprintf(stderr, "[posctrl] multi1=%.0f single1=%.0f ratio=%.3fx solved_m=%d/%d solved_s=%d/%d\n",
                mm1, ms1, ratio_ms, solv_m1, N_CTRL, solv_s1, N_CTRL);
    }

    /* =====================================================================
     * Main sweep: T in {1..T_max}, n_draws per cell
     * ===================================================================== */
    for (int ti = 0; ti < n_T; ti++) {
        int T = T_vals[ti];
        if (T > T_max) break;

        uint64_t sum_multi = 0, sum_indep = 0, sum_peak = 0;
        int sum_solved = 0, sum_correct = 0, sum_same = 0, sum_cross = 0, sum_rels = 0;
        double sum_wall = 0.0;

        for (int d = 0; d < n_draws; d++) {
            uint64_t ds = seed0 + (uint64_t)(ti * 10000 + d * 37 + 99991);

            MResult mr;
            multi_vw94(&P_gen, Q_arr, &C, T, N_total, theta_bits, ds, &mr, &dpT, NULL);
            sum_multi  += mr.total_ops;
            sum_peak   += mr.peak_dp;
            sum_solved += mr.n_solved;
            sum_correct+= mr.n_correct;
            sum_same   += mr.same_coll;
            sum_cross  += mr.cross_coll;
            sum_rels   += mr.n_rels;
            sum_wall   += mr.wall_sec;

            /* FIX-C3: independent DP-rho (not Floyd) */
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
        double ms = sum_solved/nd, mc = sum_correct/nd, mw = sum_wall/nd;
        double spd = (mm > 0) ? mi / mm : 0.0;
        double vw = 0.886 * sqrt((double)T * mpz_get_d(C.n));
        double rvw = (vw > 0) ? mm / vw : 0.0;
        double sf = ms / T, cf = (ms > 0) ? mc / ms : 0.0;

        printf("{\"type\":\"sweep\",\"curve\":\"%s\",\"n_bits\":%d,\"T\":%d,"
               "\"N_total\":%d,\"theta_bits\":%d,\"n_draws\":%d,"
               "\"mean_multi_ops\":%.1f,\"mean_indep_ops\":%.1f,"
               "\"speedup_vs_indep\":%.4f,\"vw94_theoretical\":%.1f,"
               "\"ratio_vw94\":%.4f,\"mean_peak_dp\":%.1f,"
               "\"solved_frac\":%.4f,\"correct_frac\":%.4f,"
               "\"mean_same_coll\":%.2f,\"mean_cross_coll\":%.2f,"
               "\"mean_n_rels\":%.2f,\"mean_wall_sec\":%.3f,"
               "\"time_memory_product\":%.1f}\n",
               label, n_bits, T, N_total, theta_bits, n_draws,
               mm, mi, spd, vw, rvw, mp,
               sf, cf,
               (double)sum_same/nd, (double)sum_cross/nd,
               (double)sum_rels/nd, mw, mm*mp);
        fflush(stdout);
        fprintf(stderr,
                "[sweep] T=%d multi=%.0f indep=%.0f spd=%.3fx vw94=%.0f rvw=%.3f "
                "solved=%.1f%% correct=%.1f%% wall=%.2fs\n",
                T, mm, mi, spd, vw, rvw, sf*100.0, cf*100.0, mw);
    }

    /* =====================================================================
     * Negative control
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
               "\"ops_B_with_table\":%llu,\"ops_B_independent\":%llu,"
               "\"speedup\":%.4f}\n",
               label, n_bits,
               (unsigned long long)nr.ops_A, nr.table_size_A,
               nr.cross_hits, nr.expected_random,
               (unsigned long long)nr.ops_B, (unsigned long long)nr.ops_B_indep,
               nr.speedup);
        fflush(stdout);
        fprintf(stderr, "[negctrl] cross_hits=%d expected=%.2f speedup=%.3fx\n",
                nr.cross_hits, nr.expected_random, nr.speedup);
    }

    /* Cleanup */
    dp_free(&dpT); dp_free(&dpTmp); dp_free(&dpA);
    rm_clear(&M);
    for (int i = 0; i < T_max; i++) { point_clear(&Q_arr[i]); mpz_clear(k_true[i]); }
    free(Q_arr); free(k_true);
    for (int i = 0; i < T_B; i++) point_clear(&Q_B[i]);
    free(Q_B);
    point_clear(&P_gen); point_clear(&P_B);
    curve_clear(&C); curve_clear(&C_B);
    mpz_clears(_t1, _t2, _t3, _t4, _lam, NULL);

    printf("{\"type\":\"done\",\"curve\":\"%s\",\"n_bits\":%d}\n", label, n_bits);
    fflush(stdout);
    return 0;
}
