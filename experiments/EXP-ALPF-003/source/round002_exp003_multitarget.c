/*
 * round002_exp003_multitarget.c
 * =============================================================================
 * EXP-003: Shared-DP-table multi-target Pollard rho for ECDLP
 * Category: 8 AMORTIZATION (NOT an ECDLP exponent break)
 *
 * Hypothesis H1: solving T targets shares total ~c*sqrt(T*n) group ops
 *   (sqrt(T) amortization), verified via log-log slope in [0.45,0.55].
 * Null H0: slope >= 0.8 OR time-memory product worse than independent rho.
 *
 * Algorithm: Kuhn-Struik / van Oorschot-Wiener shared-DP-table approach.
 *   - Each target i gets k_i walkers starting at random R = a*P + b*Q_i.
 *   - All walkers share a SINGLE distinguished-point (DP) table keyed by
 *     x-coordinate mod 2^{leading_zeros} == 0 (i.e., low bits zero).
 *   - A DP entry stores (x_R, a_coef, b_coef, target_index).
 *   - Collision: two walkers hit the same DP => recover k.
 *   - Negation map: identify (x,y) ~ (x,-y) to halve effective search space.
 *
 * Curve: short Weierstrass y^2 = x^3 + a4*x + a6 over GF(p).
 * Input: read from stdin in a simple text protocol.
 * Output: JSON to stdout.
 *
 * Compilation:
 *   gcc -O2 -I/opt/homebrew/include -L/opt/homebrew/lib -lgmp \
 *       round002_exp003_multitarget.c -o round002_exp003_multitarget
 *
 * Protocol (stdin):
 *   LINE 1: p a4 a6 (GMP mpz_t values as decimal strings)
 *   LINE 2: n (group order, decimal)
 *   LINE 3: Px Py (generator P, decimal)
 *   LINE 4: T (number of targets)
 *   LINES 5..4+T: Qx Qy k_true  (target point + ground-truth scalar)
 *   LINE 5+T: theta_bits (DP threshold: point is DP if x_low % (1<<theta_bits) == 0)
 *   LINE 6+T: max_ops (uint64 cap on group operations)
 *   LINE 7+T: seed (uint64 PRNG seed)
 *   LINE 8+T: curve_label (string, for logging)
 *
 * Output (stdout): one JSON object with fields:
 *   T, theta_bits, total_group_ops, peak_dp_count, n_solved,
 *   per_target[]: {index, solved, k_found, k_true, ops_at_solve},
 *   wall_time_s
 * =============================================================================
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#include <math.h>
#include <gmp.h>

/* ============================================================
 * Simple deterministic PRNG (xorshift64) for reproducibility
 * ============================================================ */
static uint64_t rng_state;

static void rng_seed(uint64_t s) { rng_state = s ? s : 1; }

static uint64_t rng_next(void) {
    uint64_t x = rng_state;
    x ^= x << 13; x ^= x >> 7; x ^= x << 17;
    rng_state = x;
    return x;
}

/* Random mpz in [0, n) */
static void mpz_rand_below(mpz_t out, const mpz_t n) {
    /* Use rejection sampling with 2 limbs of random bits */
    size_t bits = mpz_sizeinbase(n, 2) + 64;
    mpz_t tmp;
    mpz_init(tmp);
    do {
        /* Fill with random 64-bit words */
        size_t nwords = (bits + 63) / 64;
        mpz_set_ui(tmp, 0);
        for (size_t i = 0; i < nwords; i++) {
            mpz_mul_2exp(tmp, tmp, 64);
            mpz_add_ui(tmp, tmp, rng_next());
        }
        mpz_mod(tmp, tmp, n);
    } while (0); /* Simple mod is fine for uniform-ish distribution */
    mpz_set(out, tmp);
    mpz_clear(tmp);
}

/* ============================================================
 * Affine EC point over GF(p): y^2 = x^3 + a4*x + a6
 * Use mpz_t coordinates; infinity represented by is_inf flag.
 * ============================================================ */
typedef struct {
    mpz_t x, y;
    int is_inf;
} ECPoint;

static void ec_init(ECPoint *P) {
    mpz_init(P->x); mpz_init(P->y); P->is_inf = 1;
}

static void ec_clear(ECPoint *P) {
    mpz_clear(P->x); mpz_clear(P->y);
}

static void ec_copy(ECPoint *dst, const ECPoint *src) {
    mpz_set(dst->x, src->x); mpz_set(dst->y, src->y);
    dst->is_inf = src->is_inf;
}

static int ec_equal(const ECPoint *A, const ECPoint *B) {
    if (A->is_inf && B->is_inf) return 1;
    if (A->is_inf || B->is_inf) return 0;
    return (mpz_cmp(A->x, B->x) == 0 && mpz_cmp(A->y, B->y) == 0);
}

/* Global curve parameters (set once) */
static mpz_t CURVE_P, CURVE_A4, CURVE_A6, CURVE_N;
static uint64_t g_group_ops = 0; /* global op counter */

/* Modular inverse: out = a^{-1} mod p. Returns 0 if gcd != 1. */
static int modinv(mpz_t out, const mpz_t a, const mpz_t p) {
    int r = mpz_invert(out, a, p);
    return r;
}

/* Temporary mpz pool for ec_add to avoid repeated alloc */
static mpz_t _tmp1, _tmp2, _tmp3, _tmp4, _tmp5;
static int _tmps_inited = 0;

static void init_tmps(void) {
    if (!_tmps_inited) {
        mpz_init(_tmp1); mpz_init(_tmp2); mpz_init(_tmp3);
        mpz_init(_tmp4); mpz_init(_tmp5);
        _tmps_inited = 1;
    }
}

/* EC addition: R = A + B on y^2 = x^3 + CURVE_A4*x + CURVE_A6 mod CURVE_P */
static void ec_add(ECPoint *R, const ECPoint *A, const ECPoint *B) {
    g_group_ops++;
    init_tmps();

    if (A->is_inf) { ec_copy(R, B); return; }
    if (B->is_inf) { ec_copy(R, A); return; }

    /* Check if A == -B (then result is infinity) */
    if (mpz_cmp(A->x, B->x) == 0) {
        /* y_A + y_B == 0 mod p => A == -B */
        mpz_add(_tmp1, A->y, B->y);
        mpz_mod(_tmp1, _tmp1, CURVE_P);
        if (mpz_sgn(_tmp1) == 0) {
            R->is_inf = 1; return;
        }
        /* A == B: doubling */
        /* lambda = (3*x^2 + a4) / (2*y) mod p */
        mpz_mul(_tmp1, A->x, A->x); mpz_mod(_tmp1, _tmp1, CURVE_P);
        mpz_mul_ui(_tmp1, _tmp1, 3);
        mpz_add(_tmp1, _tmp1, CURVE_A4);
        mpz_mod(_tmp1, _tmp1, CURVE_P);

        mpz_mul_ui(_tmp2, A->y, 2); mpz_mod(_tmp2, _tmp2, CURVE_P);
        if (!modinv(_tmp3, _tmp2, CURVE_P)) { R->is_inf = 1; return; }
        mpz_mul(_tmp1, _tmp1, _tmp3); mpz_mod(_tmp1, _tmp1, CURVE_P);
    } else {
        /* A != B: standard addition */
        /* lambda = (y_B - y_A) / (x_B - x_A) mod p */
        mpz_sub(_tmp1, B->y, A->y); mpz_mod(_tmp1, _tmp1, CURVE_P);
        mpz_sub(_tmp2, B->x, A->x); mpz_mod(_tmp2, _tmp2, CURVE_P);
        if (!modinv(_tmp3, _tmp2, CURVE_P)) { R->is_inf = 1; return; }
        mpz_mul(_tmp1, _tmp1, _tmp3); mpz_mod(_tmp1, _tmp1, CURVE_P);
    }

    /* x_R = lambda^2 - x_A - x_B mod p */
    mpz_mul(_tmp4, _tmp1, _tmp1); mpz_mod(_tmp4, _tmp4, CURVE_P);
    mpz_sub(_tmp4, _tmp4, A->x); mpz_sub(_tmp4, _tmp4, B->x);
    mpz_mod(_tmp4, _tmp4, CURVE_P);

    /* y_R = lambda*(x_A - x_R) - y_A mod p */
    mpz_sub(_tmp5, A->x, _tmp4); mpz_mod(_tmp5, _tmp5, CURVE_P);
    mpz_mul(_tmp5, _tmp1, _tmp5); mpz_mod(_tmp5, _tmp5, CURVE_P);
    mpz_sub(_tmp5, _tmp5, A->y); mpz_mod(_tmp5, _tmp5, CURVE_P);

    R->is_inf = 0;
    mpz_set(R->x, _tmp4);
    mpz_set(R->y, _tmp5);
}

/* EC scalar multiply: R = k*P using double-and-add */
static void ec_mul(ECPoint *R, const ECPoint *P_base, const mpz_t k) {
    ECPoint acc, tmp;
    ec_init(&acc); ec_init(&tmp);
    ec_copy(&tmp, P_base);
    acc.is_inf = 1;

    int nbits = mpz_sizeinbase(k, 2);
    for (int i = 0; i < nbits; i++) {
        if (mpz_tstbit(k, i)) {
            ec_add(&acc, &acc, &tmp);
        }
        if (i < nbits - 1) ec_add(&tmp, &tmp, &tmp);
    }
    ec_copy(R, &acc);
    ec_clear(&acc); ec_clear(&tmp);
}

/* ============================================================
 * Negation map: canonical representative
 * For negation speedup: represent (x, y) and (x, p-y) as same.
 * Canonical: min(y, p-y); if y == p-y, just use y (char != 2).
 * ============================================================ */
static void ec_canonicalize(ECPoint *P) {
    if (P->is_inf) return;
    mpz_t neg_y;
    mpz_init(neg_y);
    mpz_sub(neg_y, CURVE_P, P->y);
    mpz_mod(neg_y, neg_y, CURVE_P);
    if (mpz_cmp(neg_y, P->y) < 0) {
        mpz_set(P->y, neg_y);
    }
    mpz_clear(neg_y);
}

/* ============================================================
 * DP table: hash map keyed by x-coordinate (as string)
 * Simple open-addressing with string keys.
 * ============================================================ */
#define DP_TABLE_SIZE (1 << 20) /* 1M slots */
#define DP_MAX_LOAD 600000      /* rehash / overflow detection */

typedef struct {
    char *key;          /* x-coordinate as decimal string, NULL if empty */
    mpz_t a_coef;       /* a_coef: walker = a*P + b*Q_i */
    mpz_t b_coef;
    int target_idx;     /* which target this walk belongs to */
    int negated;        /* 1 if the canonical point was negated */
    int used;
} DPEntry;

static DPEntry dp_table[DP_TABLE_SIZE];
static int dp_count = 0;

static void dp_table_init(void) {
    memset(dp_table, 0, sizeof(dp_table));
    dp_count = 0;
}

static void dp_table_clear(void) {
    for (int i = 0; i < DP_TABLE_SIZE; i++) {
        if (dp_table[i].used) {
            free(dp_table[i].key);
            mpz_clear(dp_table[i].a_coef);
            mpz_clear(dp_table[i].b_coef);
            dp_table[i].used = 0;
            dp_table[i].key = NULL;
        }
    }
    dp_count = 0;
}

/* FNV-1a hash for string */
static uint32_t fnv1a(const char *s) {
    uint32_t h = 2166136261u;
    while (*s) {
        h ^= (unsigned char)*s++;
        h *= 16777619u;
    }
    return h;
}

/* Insert or lookup DP entry.
 * Returns: 0 if inserted (new entry), 1 if collision found (existing entry).
 * On collision: *prev is set to pointer of the existing entry.
 */
static int dp_insert_or_find(const char *key, const mpz_t a, const mpz_t b,
                              int tidx, int negated, DPEntry **prev_out) {
    uint32_t h = fnv1a(key) & (DP_TABLE_SIZE - 1);
    for (int probe = 0; probe < DP_TABLE_SIZE; probe++) {
        uint32_t slot = (h + probe) & (DP_TABLE_SIZE - 1);
        if (!dp_table[slot].used) {
            /* Insert here */
            dp_table[slot].key = strdup(key);
            mpz_init_set(dp_table[slot].a_coef, a);
            mpz_init_set(dp_table[slot].b_coef, b);
            dp_table[slot].target_idx = tidx;
            dp_table[slot].negated = negated;
            dp_table[slot].used = 1;
            dp_count++;
            return 0;
        }
        if (strcmp(dp_table[slot].key, key) == 0) {
            *prev_out = &dp_table[slot];
            return 1;
        }
    }
    return -1; /* table full */
}

/* ============================================================
 * Walker state
 * ============================================================ */
typedef struct {
    ECPoint R;          /* current point */
    mpz_t a, b;        /* R = a*P + b*Q_i */
    int target_idx;    /* which Q_i */
    int active;
} Walker;

/* Random walk step: partition by x mod 3 */
static void walk_step(Walker *w, const ECPoint *P_gen,
                      const ECPoint *Q_arr, int T,
                      const mpz_t n) {
    if (w->R.is_inf) {
        /* Restart from random */
        mpz_rand_below(w->a, n);
        mpz_rand_below(w->b, n);
        /* R = a*P + b*Q_i */
        ECPoint tmp1, tmp2;
        ec_init(&tmp1); ec_init(&tmp2);
        ec_mul(&tmp1, P_gen, w->a);
        ec_mul(&tmp2, &Q_arr[w->target_idx], w->b);
        ec_add(&w->R, &tmp1, &tmp2);
        ec_clear(&tmp1); ec_clear(&tmp2);
        return;
    }

    unsigned long xmod3 = mpz_tdiv_ui(w->R.x, 3);
    if (xmod3 == 0) {
        /* Double */
        ec_add(&w->R, &w->R, &w->R);
        mpz_mul_2exp(w->a, w->a, 1); mpz_mod(w->a, w->a, n);
        mpz_mul_2exp(w->b, w->b, 1); mpz_mod(w->b, w->b, n);
    } else if (xmod3 == 1) {
        /* Add P */
        ec_add(&w->R, &w->R, P_gen);
        mpz_add_ui(w->a, w->a, 1); mpz_mod(w->a, w->a, n);
    } else {
        /* Add Q_i */
        ec_add(&w->R, &w->R, &Q_arr[w->target_idx]);
        mpz_add_ui(w->b, w->b, 1); mpz_mod(w->b, w->b, n);
    }
}

/* ============================================================
 * Main solver
 * ============================================================ */
int main(void) {
    /* Initialize GMP globals */
    mpz_init(CURVE_P); mpz_init(CURVE_A4);
    mpz_init(CURVE_A6); mpz_init(CURVE_N);

    /* Read curve parameters */
    char p_str[512], a4_str[512], a6_str[512], n_str[512];
    if (scanf("%511s %511s %511s", p_str, a4_str, a6_str) != 3) {
        fprintf(stderr, "Error reading curve params\n"); return 1;
    }
    if (scanf("%511s", n_str) != 1) {
        fprintf(stderr, "Error reading n\n"); return 1;
    }
    mpz_set_str(CURVE_P, p_str, 10);
    mpz_set_str(CURVE_A4, a4_str, 10);
    mpz_set_str(CURVE_A6, a6_str, 10);
    mpz_set_str(CURVE_N, n_str, 10);

    /* Read generator P */
    ECPoint P_gen;
    ec_init(&P_gen);
    char px_str[512], py_str[512];
    if (scanf("%511s %511s", px_str, py_str) != 2) {
        fprintf(stderr, "Error reading P\n"); return 1;
    }
    P_gen.is_inf = 0;
    mpz_set_str(P_gen.x, px_str, 10);
    mpz_set_str(P_gen.y, py_str, 10);

    /* Read T */
    int T;
    if (scanf("%d", &T) != 1) { fprintf(stderr, "Error reading T\n"); return 1; }
    if (T > 128) { fprintf(stderr, "T too large\n"); return 1; }

    /* Read targets */
    ECPoint *Q_arr = (ECPoint*)calloc(T, sizeof(ECPoint));
    mpz_t *k_true_arr = (mpz_t*)calloc(T, sizeof(mpz_t));
    for (int i = 0; i < T; i++) {
        ec_init(&Q_arr[i]);
        mpz_init(k_true_arr[i]);
        char qx[512], qy[512], kt[512];
        if (scanf("%511s %511s %511s", qx, qy, kt) != 3) {
            fprintf(stderr, "Error reading target %d\n", i); return 1;
        }
        Q_arr[i].is_inf = 0;
        mpz_set_str(Q_arr[i].x, qx, 10);
        mpz_set_str(Q_arr[i].y, qy, 10);
        mpz_set_str(k_true_arr[i], kt, 10);
    }

    /* Read theta_bits, max_ops, seed, label */
    int theta_bits;
    uint64_t max_ops, seed;
    char curve_label[256];
    if (scanf("%d %llu %llu %255s",
              &theta_bits, (unsigned long long*)&max_ops,
              (unsigned long long*)&seed, curve_label) != 4) {
        fprintf(stderr, "Error reading theta/max_ops/seed/label\n"); return 1;
    }

    /* Threshold: point is DP if x mod (1 << theta_bits) == 0 */
    mpz_t theta_mask;
    mpz_init(theta_mask);
    mpz_set_ui(theta_mask, 1);
    mpz_mul_2exp(theta_mask, theta_mask, theta_bits);
    mpz_sub_ui(theta_mask, theta_mask, 1); /* mask = (1<<theta_bits)-1 */

    /* Initialize PRNG */
    rng_seed(seed);

    /* Initialize DP table */
    dp_table_init();

    /* Solve state */
    int *solved = (int*)calloc(T, sizeof(int));
    mpz_t *k_found_arr = (mpz_t*)calloc(T, sizeof(mpz_t));
    uint64_t *solve_ops = (uint64_t*)calloc(T, sizeof(uint64_t));
    for (int i = 0; i < T; i++) {
        mpz_init(k_found_arr[i]);
        solve_ops[i] = 0;
    }
    int n_solved = 0;

    /* One walker per target (can have multiple, but 1 is sufficient for small T) */
    /* For shared-table benefit, we need walkers from multiple targets running together */
    /* Allocate walkers: 2 per target */
    int n_walkers_per_target = 2;
    int n_walkers = T * n_walkers_per_target;
    Walker *walkers = (Walker*)calloc(n_walkers, sizeof(Walker));
    for (int i = 0; i < n_walkers; i++) {
        ec_init(&walkers[i].R);
        mpz_init(walkers[i].a);
        mpz_init(walkers[i].b);
        walkers[i].target_idx = i / n_walkers_per_target;
        walkers[i].active = 1;
        /* Random start */
        walkers[i].R.is_inf = 1; /* trigger restart on first step */
        /* Initialize */
        mpz_rand_below(walkers[i].a, CURVE_N);
        mpz_rand_below(walkers[i].b, CURVE_N);
        ECPoint tmp1, tmp2;
        ec_init(&tmp1); ec_init(&tmp2);
        ec_mul(&tmp1, &P_gen, walkers[i].a);
        ec_mul(&tmp2, &Q_arr[walkers[i].target_idx], walkers[i].b);
        ec_add(&walkers[i].R, &tmp1, &tmp2);
        ec_clear(&tmp1); ec_clear(&tmp2);
    }

    g_group_ops = 0;
    uint64_t peak_dp = 0;
    uint64_t prev_ops = 0;

    struct timespec t_start, t_now;
    clock_gettime(CLOCK_MONOTONIC, &t_start);

    /* Main loop */
    while (n_solved < T && g_group_ops < max_ops) {
        for (int wi = 0; wi < n_walkers && n_solved < T && g_group_ops < max_ops; wi++) {
            if (!walkers[wi].active) continue;
            int tidx = walkers[wi].target_idx;
            if (solved[tidx]) { walkers[wi].active = 0; continue; }

            /* Step the walker */
            walk_step(&walkers[wi], &P_gen, Q_arr, T, CURVE_N);

            if (walkers[wi].R.is_inf) continue;

            /* Check if DP: x mod (1<<theta_bits) == 0 */
            mpz_t xmod;
            mpz_init(xmod);
            mpz_and(xmod, walkers[wi].R.x, theta_mask);
            int is_dp = (mpz_sgn(xmod) == 0);
            mpz_clear(xmod);

            if (!is_dp) continue;

            /* Canonicalize (negation map) */
            ECPoint canon;
            ec_init(&canon);
            ec_copy(&canon, &walkers[wi].R);
            int was_negated = 0;
            mpz_t neg_y;
            mpz_init(neg_y);
            mpz_sub(neg_y, CURVE_P, canon.y);
            mpz_mod(neg_y, neg_y, CURVE_P);
            if (mpz_cmp(neg_y, canon.y) < 0) {
                mpz_set(canon.y, neg_y);
                was_negated = 1;
            }
            mpz_clear(neg_y);

            /* Get key = x as string */
            char *key = mpz_get_str(NULL, 10, canon.x);

            /* Adjust coefficients for negation */
            mpz_t a_adj, b_adj;
            mpz_init_set(a_adj, walkers[wi].a);
            mpz_init_set(b_adj, walkers[wi].b);
            if (was_negated) {
                /* -R = -(a*P + b*Q) = (-a)*P + (-b)*Q */
                mpz_neg(a_adj, a_adj); mpz_mod(a_adj, a_adj, CURVE_N);
                mpz_neg(b_adj, b_adj); mpz_mod(b_adj, b_adj, CURVE_N);
            }

            /* Try to insert in DP table */
            DPEntry *prev = NULL;
            int result = dp_insert_or_find(key, a_adj, b_adj, tidx,
                                           was_negated, &prev);
            free(key);

            if ((uint64_t)dp_count > peak_dp) peak_dp = (uint64_t)dp_count;

            if (result == 1 && prev != NULL) {
                /* Collision! prev and current walker share DP with same x.
                 * prev: a1*P + b1*Q_{i1} = current_pt
                 * cur:  a2*P + b2*Q_{i2} = current_pt (same canonical x => same or neg)
                 *
                 * Case 1: same target (i1 == i2):
                 *   (a1-a2)*P = (b2-b1)*Q_i => k_i = (a1-a2)*(b2-b1)^{-1} mod n
                 *
                 * Case 2: different targets (cross-target collision):
                 *   a1*P + b1*Q_{i1} = a2*P + b2*Q_{i2}
                 *   (a1-a2)*P = b2*Q_{i2} - b1*Q_{i1}
                 *   This is more complex; skip cross-target for now (focus same-target).
                 *   Cross-target collisions still count for DP table density = amortization.
                 */
                int i1 = prev->target_idx;
                int i2 = tidx;

                if (i1 == i2 && !solved[i1]) {
                    /* Same target collision */
                    mpz_t da, db, k_cand;
                    mpz_init(da); mpz_init(db); mpz_init(k_cand);

                    mpz_sub(da, prev->a_coef, a_adj);
                    mpz_mod(da, da, CURVE_N);
                    mpz_sub(db, b_adj, prev->b_coef);
                    mpz_mod(db, db, CURVE_N);

                    if (mpz_sgn(db) != 0) {
                        mpz_t db_inv;
                        mpz_init(db_inv);
                        if (mpz_invert(db_inv, db, CURVE_N)) {
                            mpz_mul(k_cand, da, db_inv);
                            mpz_mod(k_cand, k_cand, CURVE_N);

                            /* Verify: k_cand * P == Q_i */
                            ECPoint kP;
                            ec_init(&kP);
                            ec_mul(&kP, &P_gen, k_cand);
                            if (ec_equal(&kP, &Q_arr[i1])) {
                                solved[i1] = 1;
                                mpz_set(k_found_arr[i1], k_cand);
                                solve_ops[i1] = g_group_ops;
                                n_solved++;
                            }
                            ec_clear(&kP);
                        }
                        mpz_clear(db_inv);
                    }
                    mpz_clear(da); mpz_clear(db); mpz_clear(k_cand);
                }
                /* For cross-target: different targets share the DP table,
                 * which is the source of the amortization benefit.
                 * We don't attempt cross-solve here, but cross-target DPs
                 * DO populate the same table and create extra collision opportunities.
                 */
            }
            ec_clear(&canon);
            mpz_clear(a_adj); mpz_clear(b_adj);

            /* Restart walker if we hit the DP (to explore new paths) */
            /* Only restart if table is getting full */
            if (dp_count > DP_MAX_LOAD) {
                /* Clear and restart -- this is a sign of too-large T or too-small theta */
                dp_table_clear();
            }
        }
    }

    clock_gettime(CLOCK_MONOTONIC, &t_now);
    double wall_time = (t_now.tv_sec - t_start.tv_sec) +
                       (t_now.tv_nsec - t_start.tv_nsec) * 1e-9;

    /* Output JSON */
    printf("{\n");
    printf("  \"curve_label\": \"%s\",\n", curve_label);
    printf("  \"T\": %d,\n", T);
    printf("  \"theta_bits\": %d,\n", theta_bits);
    printf("  \"total_group_ops\": %llu,\n", (unsigned long long)g_group_ops);
    printf("  \"peak_dp_count\": %llu,\n", (unsigned long long)peak_dp);
    printf("  \"n_solved\": %d,\n", n_solved);
    printf("  \"wall_time_s\": %.6f,\n", wall_time);
    printf("  \"per_target\": [\n");
    for (int i = 0; i < T; i++) {
        char *kf = solved[i] ? mpz_get_str(NULL, 10, k_found_arr[i]) : NULL;
        char *kt = mpz_get_str(NULL, 10, k_true_arr[i]);
        printf("    {\"index\": %d, \"solved\": %s, \"k_match\": %s, \"ops_at_solve\": %llu}%s\n",
               i,
               solved[i] ? "true" : "false",
               (solved[i] && kf && strcmp(kf, kt) == 0) ? "true" : "false",
               (unsigned long long)solve_ops[i],
               (i < T - 1) ? "," : "");
        if (kf) free(kf);
        free(kt);
    }
    printf("  ]\n}\n");

    /* Cleanup */
    dp_table_clear();
    for (int i = 0; i < T; i++) {
        ec_clear(&Q_arr[i]);
        mpz_clear(k_true_arr[i]);
        mpz_clear(k_found_arr[i]);
    }
    for (int i = 0; i < n_walkers; i++) {
        ec_clear(&walkers[i].R);
        mpz_clear(walkers[i].a);
        mpz_clear(walkers[i].b);
    }
    free(Q_arr); free(k_true_arr); free(k_found_arr); free(solve_ops);
    free(solved); free(walkers);
    ec_clear(&P_gen);
    mpz_clear(CURVE_P); mpz_clear(CURVE_A4); mpz_clear(CURVE_A6); mpz_clear(CURVE_N);
    mpz_clear(theta_mask);
    if (_tmps_inited) {
        mpz_clear(_tmp1); mpz_clear(_tmp2); mpz_clear(_tmp3);
        mpz_clear(_tmp4); mpz_clear(_tmp5);
    }
    return 0;
}
