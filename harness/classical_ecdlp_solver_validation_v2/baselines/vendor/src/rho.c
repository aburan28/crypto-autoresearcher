/*
 * rho.c - parallel Pollard rho with distinguished points.
 *
 * Walk definition (Teske r-adding walk).  Multipliers M_i = alpha_i*G +
 * beta_i*H for i < r.  A walk state is (Y, a, b) with Y = a*G + b*H.  One
 * step: i = idx(Y); Y <- Y + M_i; (a, b) <- (a + alpha_i, b + beta_i).
 *
 * With the negation map every point is replaced by the canonical member of
 * {Y, -Y} after each step (negating (a, b) when needed), and idx() is
 * evaluated on the canonical form.  Fruitless 2-cycles are suppressed by
 * the look-ahead rule "if idx(Y + M_i) == i use M_{i+1} instead" and
 * longer cycles are caught by a sliding-window self-comparison; a walk
 * caught in a cycle escapes deterministically from the minimum element of
 * the cycle by doubling, so two walks that merged inside the cycle stay
 * merged.
 *
 * Distinguished points (hash with dp_bits trailing zeros) are stored in a
 * shared table with their (a, b).  A second arrival at the same point with
 * a different (a, b) yields (b - b') x == a' - a (mod n).
 */
#include "cryptanalysis/ca_rho.h"
#include "dlog_internal.h"

#include <pthread.h>
#include <stdatomic.h>
#include <errno.h>
#include <fcntl.h>
#include <inttypes.h>
#include <stddef.h>
#include <stdio.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>

#define RHO_WINDOW 64
#define RHO_MAX_WALKS 4096

#ifdef CA_RHO_TRACE
#    include <stdlib.h>
#    define RHO_TR_CHECK(c) do { if (!(c)) { fprintf(stderr, "rho trace: %s\n", #c); abort(); } } while (0)
#    define RHO_RING 192
#    define RHO_CYC_MAX (4 * RHO_WINDOW)
/* Where ca_rho_solve's group operations go, written as one JSON line per
 * solve to $CA_RHO_TRACE_FILE.  Diagnostic builds only (-DCA_RHO_TRACE,
 * single-threaded solves); the walk itself is unchanged.  Restart reasons:
 * 0 = merged with its own earlier trail, 1 = useless collision, 2 = abandoned. */
typedef struct rho_trace {
    uint64_t table_ops, start_ops, restart_ops[3], restarts[3];
    uint64_t step_ops, escape_ops;
    uint64_t committed, retry_slots, unprocessed, dps;
    uint64_t escapes, escape_cycle_steps, escape_unclosed;
    uint64_t cycle_len[RHO_CYC_MAX + 1];
    uint64_t abandons, abandon_wasted, abandon_dup;
    uint64_t trail_counter;
    /* exact-collision oracle: every committed point, with the trail that first visited it */
    uint64_t *set_key;
    uint32_t *set_trail;
    uint64_t set_mask, set_count;
    uint64_t cross_repeats, first_cross_at, dup_steps, solve_at;
} rho_trace;

static void rho_trace_set_insert(rho_trace *t, uint64_t key, uint32_t trail, int *seen_other)
{
    if (key == 0) key = 1;
    if (t->set_count * 2 >= t->set_mask + 1 || !t->set_key) {
        uint64_t ncap = t->set_key ? (t->set_mask + 1) * 2 : 1u << 16;
        uint64_t *nk = calloc(ncap, sizeof(uint64_t));
        uint32_t *nt = calloc(ncap, sizeof(uint32_t));
        RHO_TR_CHECK(nk && nt);
        for (uint64_t i = 0; t->set_key && i <= t->set_mask; i++)
            if (t->set_key[i]) {
                uint64_t j = (t->set_key[i] * 0x9E3779B97F4A7C15ULL) >> 20 & (ncap - 1);
                while (nk[j]) j = (j + 1) & (ncap - 1);
                nk[j] = t->set_key[i];
                nt[j] = t->set_trail[i];
            }
        free(t->set_key); free(t->set_trail);
        t->set_key = nk; t->set_trail = nt; t->set_mask = ncap - 1;
    }
    uint64_t j = (key * 0x9E3779B97F4A7C15ULL) >> 20 & t->set_mask;
    while (t->set_key[j]) {
        if (t->set_key[j] == key) { *seen_other = t->set_trail[j] != trail; return; }
        j = (j + 1) & t->set_mask;
    }
    t->set_key[j] = key; t->set_trail[j] = trail; t->set_count++;
    *seen_other = 0;
}
#endif

typedef struct rho_shared {
    const ca_group *g;
    ca_elem base, target;
    uint64_t n;
    uint32_t r;
    uint32_t r_mask; /* r - 1 for power-of-two tables, otherwise zero */
    uint64_t r_magic; /* floor(2^64 / r) + 1, for rho_index */
    ca_elem *M;
    uint64_t *alpha, *beta;
    int negmap;
    int dp_bits;
    uint64_t dp_mask;
    uint32_t walks;
    uint64_t seed;
    uint64_t max_ops, max_table;
    uint64_t setup_ops;
    uint64_t setup_prior;
    double elapsed_prior;
    const char *checkpoint_path;

    pthread_mutex_t lock;
    ca_htab tab;
    atomic_int done;
    atomic_uint_fast64_t total_ops;
    atomic_uint_fast64_t total_dps;
    atomic_uint_fast64_t restarts;
    uint64_t result;
    ca_status status;
#ifdef CA_RHO_TRACE
    rho_trace tr;
#endif
} rho_shared;

typedef struct rho_walk {
    ca_elem Y;
    uint64_t h; /* ca_group_hash of Y, kept with it */
    uint64_t a, b;
    uint32_t idx;
    uint32_t retry; /* rejected multipliers so far for the pending step; 0 = none */
    uint64_t since_dp;
    ca_elem saved;
    uint32_t win;
#ifdef CA_RHO_TRACE
    uint64_t ring[RHO_RING];
    uint64_t ring_n;   /* committed points since the walk start or the last escape */
    uint64_t charged;  /* steps of the current since-DP interval already booked to a cycle */
    uint32_t trail;
    uint8_t merged;    /* has met another trail's point */
#endif
} rho_walk;

typedef struct rho_thread {
    rho_shared *sh;
    uint32_t id;
    uint64_t ops;
} rho_thread;

/* Native, versioned snapshot.  A different ABI or walk format must reject
 * the file instead of interpreting it as a compatible DP corpus. */
typedef struct rho_checkpoint_header {
    char magic[8];
    uint64_t p, a, b, order, cofactor;
    uint64_t base[4], target[4];
    uint32_t kind, endo_kind, aut_order, r, dp_bits, negmap;
    uint32_t entry_size;
    /* Reserved in the native CARHODP2 layout.  Keep both words so old
     * checkpoints retain their exact header size and checksum offsets. */
    // cppcheck-suppress unusedStructMember
    uint32_t threads;
    // cppcheck-suppress unusedStructMember
    uint32_t walks;
    uint64_t endo_lambda, endo_c_mont;
    uint64_t seed, walk_ops, setup_ops, dps, restarts, entries, result;
    double elapsed_seconds;
    uint32_t solved;
    uint64_t checksum;
} rho_checkpoint_header;

static uint64_t rho_hash_bytes(const void *data, size_t n, uint64_t h)
{
    const unsigned char *p = data;
    for (size_t i = 0; i < n; i++) { h ^= p[i]; h *= UINT64_C(1099511628211); }
    return h;
}

static char *rho_path(const char *checkpoint, const char *suffix)
{
    size_t n = strlen(checkpoint) + strlen(suffix) + 1;
    char *path = malloc(n);
    if (path) snprintf(path, n, "%s%s", checkpoint, suffix);
    return path;
}

static int rho_sync_parent(const char *path)
{
    char *dir = strdup(path);
    if (!dir) return 0;
    const char *parent = dir;
    char *slash = strrchr(dir, '/');
    if (slash) {
        if (slash == dir) slash[1] = '\0';
        else *slash = '\0';
    } else
        parent = ".";
    int fd = open(parent, O_RDONLY);
    int ok = fd >= 0 && fsync(fd) == 0;
    if (fd >= 0) close(fd);
    free(dir);
    return ok;
}

static void rho_checkpoint_identity(const rho_shared *sh, rho_checkpoint_header *h)
{
    memset(h, 0, sizeof(*h));
    memcpy(h->magic, "CARHODP2", 8);
    h->p = sh->g->p; h->a = sh->g->a; h->b = sh->g->b;
    h->order = sh->g->order; h->cofactor = sh->g->cofactor;
    ca_group_decode(sh->g, h->base, &sh->base);
    ca_group_decode(sh->g, h->target, &sh->target);
    h->kind = sh->g->kind; h->endo_kind = sh->g->endo_kind;
    h->aut_order = sh->g->aut_order; h->endo_lambda = sh->g->endo_lambda;
    h->endo_c_mont = sh->g->endo_c_mont;
    h->r = sh->r; h->dp_bits = (uint32_t)sh->dp_bits; h->negmap = (uint32_t)sh->negmap;
    h->entry_size = sizeof(ca_htab_entry);
}

static int rho_checkpoint_same_run(const rho_checkpoint_header *a,
                                   const rho_checkpoint_header *b)
{
    return memcmp(a->magic, b->magic, 8) == 0 &&
           a->p == b->p && a->a == b->a && a->b == b->b &&
           a->order == b->order && a->cofactor == b->cofactor &&
           memcmp(a->base, b->base, sizeof(a->base)) == 0 &&
           memcmp(a->target, b->target, sizeof(a->target)) == 0 &&
           a->kind == b->kind && a->endo_kind == b->endo_kind &&
           a->aut_order == b->aut_order && a->endo_lambda == b->endo_lambda &&
           a->endo_c_mont == b->endo_c_mont && a->r == b->r &&
           a->dp_bits == b->dp_bits && a->negmap == b->negmap &&
           a->entry_size == b->entry_size;
}

static int rho_write_all(int fd, const void *data, size_t n)
{
    const unsigned char *p = data;
    while (n) {
        ssize_t m = write(fd, p, n);
        if (m < 0 && errno == EINTR) continue;
        if (m <= 0) return 0;
        p += m; n -= (size_t)m;
    }
    return 1;
}

static int rho_checkpoint_probe(rho_shared *sh, rho_checkpoint_header *saved)
{
    if (!sh->checkpoint_path) return 0;
    FILE *f = fopen(sh->checkpoint_path, "rb");
    if (!f) {
        if (errno == ENOENT) return 0;
        ca_set_error("rho: cannot open checkpoint");
        return -1;
    }
    rho_checkpoint_header wanted;
    rho_checkpoint_identity(sh, &wanted);
    int valid = fread(saved, 1, sizeof(*saved), f) == sizeof(*saved) &&
                rho_checkpoint_same_run(saved, &wanted) && saved->seed != 0 &&
                saved->entries <= SIZE_MAX / sizeof(ca_htab_entry) &&
                saved->walk_ops >= saved->dps && saved->elapsed_seconds >= 0;
    fclose(f);
    if (!valid) {
        ca_set_error("rho: checkpoint identity or format does not match");
        return -1;
    }
    if (sh->seed && sh->seed != saved->seed) {
        ca_set_error("rho: checkpoint seed does not match");
        return -1;
    }
    sh->seed = saved->seed;
    return 1;
}

static int rho_checkpoint_load(rho_shared *sh, const rho_checkpoint_header *expected)
{
    FILE *f = fopen(sh->checkpoint_path, "rb");
    if (!f) { ca_set_error("rho: cannot reopen checkpoint"); return 0; }
    rho_checkpoint_header h = {0};
    int ok = fread(&h, 1, sizeof(h), f) == sizeof(h) &&
             /* Both headers are raw fread() bytes of the same file, including padding. */
             // NOLINTNEXTLINE(bugprone-suspicious-memory-comparison,cert-exp42-c,cert-flp37-c)
             memcmp(&h, expected, sizeof(h)) == 0;
    uint64_t checksum = h.checksum;
    h.checksum = 0;
    uint64_t hash = rho_hash_bytes(&h, sizeof(h), UINT64_C(14695981039346656037));
    for (uint64_t i = 0; ok && i < h.entries; i++) {
        ca_htab_entry e;
        if (fread(&e, 1, sizeof(e), f) != sizeof(e) || !e.key ||
            e.v0 >= sh->n || e.v1 >= sh->n) { ok = 0; break; }
        hash = rho_hash_bytes(&e, sizeof(e), hash);
        uint64_t a, b;
        if (ca_htab_insert(&sh->tab, e.key, e.v0, e.v1, &a, &b) != 0) ok = 0;
    }
    if (ok && (fgetc(f) != EOF || hash != checksum || sh->tab.count != h.entries)) ok = 0;
    if (ferror(f)) ok = 0;
    fclose(f);
    if (!ok) { ca_set_error("rho: checkpoint is truncated or corrupt"); return 0; }
    atomic_store(&sh->total_ops, h.walk_ops);
    atomic_store(&sh->total_dps, h.dps);
    atomic_store(&sh->restarts, h.restarts);
    sh->setup_prior = h.setup_ops;
    sh->elapsed_prior = h.elapsed_seconds;
    if (h.solved) {
        if (!ca_verify_log(sh->g, &sh->base, &sh->target, h.result)) {
            ca_set_error("rho: saved solution fails verification");
            return 0;
        }
        sh->result = h.result;
        sh->status = CA_OK;
        atomic_store(&sh->done, 1);
    }
    return 1;
}

/* The lock makes the table and solved status a single consistent image. */
static int rho_checkpoint_save(rho_shared *sh, double elapsed)
{
    if (!sh->checkpoint_path) return 1;
    char *tmp = rho_path(sh->checkpoint_path, ".tmp.XXXXXX");
    if (!tmp) return 0;
    int fd = mkstemp(tmp);
    int ok = fd >= 0;
    pthread_mutex_lock(&sh->lock);
    rho_checkpoint_header h;
    rho_checkpoint_identity(sh, &h);
    h.seed = sh->seed;
    h.walk_ops = atomic_load(&sh->total_ops);
    h.setup_ops = sh->setup_prior + sh->setup_ops;
    h.dps = atomic_load(&sh->total_dps);
    h.restarts = atomic_load(&sh->restarts);
    h.entries = sh->tab.count;
    h.result = sh->result;
    h.solved = sh->status == CA_OK;
    h.elapsed_seconds = sh->elapsed_prior + elapsed;
    h.checksum = 0;
    uint64_t hash = rho_hash_bytes(&h, sizeof(h), UINT64_C(14695981039346656037));
    if (ok) ok = rho_write_all(fd, &h, sizeof(h));
    for (size_t i = 0; ok && i < sh->tab.cap; i++) {
        const ca_htab_entry *e = &sh->tab.e[i];
        if (!e->key) continue;
        hash = rho_hash_bytes(e, sizeof(*e), hash);
        ok = rho_write_all(fd, e, sizeof(*e));
    }
    if (ok) {
        h.checksum = hash;
        ok = lseek(fd, 0, SEEK_SET) == 0 && rho_write_all(fd, &h, sizeof(h));
    }
    pthread_mutex_unlock(&sh->lock);
    if (ok) ok = fsync(fd) == 0;
    if (fd >= 0 && close(fd) != 0) ok = 0;
    if (ok) ok = rename(tmp, sh->checkpoint_path) == 0 && rho_sync_parent(sh->checkpoint_path);
    if (!ok) unlink(tmp);
    free(tmp);
    if (!ok) ca_set_error("rho: cannot persist checkpoint");
    return ok;
}

static int rho_progress(rho_shared *sh, double elapsed, int verbose)
{
    uint64_t ops = atomic_load(&sh->total_ops) + sh->setup_prior + sh->setup_ops;
    uint64_t dps = atomic_load(&sh->total_dps);
    uint64_t restarts = atomic_load(&sh->restarts);
    size_t entries;
    pthread_mutex_lock(&sh->lock);
    entries = sh->tab.count;
    pthread_mutex_unlock(&sh->lock);
    if (verbose) fprintf(stderr, "[rho] %.1fs ops=%" PRIu64 " dps=%" PRIu64
                         " entries=%zu restarts=%" PRIu64 "\n",
                         sh->elapsed_prior + elapsed, ops, dps, entries, restarts);
    if (!sh->checkpoint_path) return 1;
    char *path = rho_path(sh->checkpoint_path, ".progress.json");
    char *tmp = rho_path(sh->checkpoint_path, ".progress.tmp.XXXXXX");
    if (!path || !tmp) { free(path); free(tmp); return 0; }
    int fd = mkstemp(tmp);
    char body[512];
    int n = snprintf(body, sizeof(body), "{\"status\":\"%s\",\"elapsed_seconds\":%.3f,"
                     "\"group_ops\":%" PRIu64 ",\"distinguished_points\":%" PRIu64
                     ",\"table_entries\":%zu,\"restarts\":%" PRIu64 "}\n",
                     atomic_load(&sh->done) && sh->status == CA_OK ? "ok" : "running",
                     sh->elapsed_prior + elapsed, ops, dps, entries, restarts);
    int ok = fd >= 0 && n > 0 && (size_t)n < sizeof(body) &&
             rho_write_all(fd, body, (size_t)n) && fsync(fd) == 0;
    if (fd >= 0 && close(fd) != 0) ok = 0;
    if (ok) ok = rename(tmp, path) == 0 && rho_sync_parent(path);
    if (!ok) { unlink(tmp); ca_set_error("rho: cannot persist progress"); }
    free(path); free(tmp);
    return ok;
}

void ca_rho_params_default(ca_rho_params *p)
{
    memset(p, 0, sizeof(*p));
    p->threads = 1;
    p->dp_bits = -1;
    p->negation_map = 1;
}

/* Default tables have power-of-two sizes, so index them with one mask.
 * For arbitrary user-supplied r, Lemire's fastmod with
 * M = floor(2^64 / r) + 1 is exact for a 32-bit numerator and divisor. */
static inline uint32_t rho_index(const rho_shared *sh, uint64_t h)
{
    uint32_t upper = (uint32_t)(h >> 32);
    if (sh->r_mask) return upper & sh->r_mask;
    uint64_t low = sh->r_magic * upper;
    return (uint32_t)(((ca_u128)low * sh->r) >> 64);
}

static inline void exp_add(uint64_t n, uint64_t *a, uint64_t d)
{
    *a = ca_addmod(*a, d, n);
}

static void walk_restart(rho_shared *sh, rho_walk *w, ca_rng *rng, uint64_t *ops)
{
    const ca_group *g = sh->g;
    w->a = ca_rng_below(rng, sh->n);
    w->b = ca_rng_below(rng, sh->n);
    ca_elem t1, t2;
    ca_group_mul(g, &t1, &sh->base, w->a, ops);
    ca_group_mul(g, &t2, &sh->target, w->b, ops);
    ca_group_op(g, &w->Y, &t1, &t2);
    (*ops)++;
    if (sh->negmap && ca_group_canonicalize(g, &w->Y)) {
        w->a = w->a ? sh->n - w->a : 0;
        w->b = w->b ? sh->n - w->b : 0;
    }
    w->h = ca_group_hash(g, &w->Y);
    w->retry = 0;
    w->since_dp = 0;
    w->win = 0;
#ifdef CA_RHO_TRACE
    w->ring_n = 0;
    w->charged = 0;
    w->merged = 0;
    w->trail = (uint32_t)++sh->tr.trail_counter;
#endif
}

/* Apply the exponent update for a step with multiplier i and sign flag. */
static inline void walk_apply(const rho_shared *sh, rho_walk *w, uint32_t i, int negated)
{
    exp_add(sh->n, &w->a, sh->alpha[i]);
    exp_add(sh->n, &w->b, sh->beta[i]);
    if (negated) {
        w->a = w->a ? sh->n - w->a : 0;
        w->b = w->b ? sh->n - w->b : 0;
    }
}

/* One full (unbatched) step of the walk function.  Used only for cycle
 * escapes; must match the batched path exactly. */
static void walk_step_single(rho_shared *sh, rho_walk *w, uint64_t *ops)
{
    const ca_group *g = sh->g;
    uint32_t i = w->retry ? w->idx : rho_index(sh, w->h);
    uint32_t rejected = w->retry;
    for (;;) {
        ca_elem Yn;
        ca_group_op(g, &Yn, &w->Y, &sh->M[i]);
        (*ops)++;
        int neg = sh->negmap ? ca_group_canonicalize(g, &Yn) : 0;
        uint64_t h = ca_group_hash(g, &Yn);
        /* Look-ahead rule, bounded: when the other r - 1 multipliers have
         * all been rejected too, every multiplier returns to Y and the scan
         * would repeat forever (probability r^-r per point, which a small
         * user-chosen r makes likely).  The last candidate is then taken as
         * it is; the 2-cycle it makes is caught by the window test.  The
         * choice depends on the point alone, so merged walks stay merged. */
        if (sh->negmap && rho_index(sh, h) == i && rejected + 1 < sh->r) {
            i = (i + 1) % sh->r;
            rejected++;
            continue;
        }
        w->Y = Yn;
        w->h = h;
        walk_apply(sh, w, i, neg);
        w->retry = 0;
        return;
    }
}

/* Escape from a fruitless cycle containing w->Y: find the cycle's minimum
 * (by hash), then jump to 2*min. */
static uint32_t walk_escape_cycle(rho_shared *sh, rho_walk *w, uint64_t *ops)
{
    const ca_group *g = sh->g;
    rho_walk cur = *w;
    cur.retry = 0;
    rho_walk best = cur;
    uint64_t best_h = cur.h;
    uint32_t cycle_len = 0; /* 0: no return within the scan limit */
    for (uint32_t k = 0; k < 4 * RHO_WINDOW; k++) {
        walk_step_single(sh, &cur, ops);
        uint64_t h = cur.h;
        if (ca_group_equal(g, &cur.Y, &w->Y)) { cycle_len = k + 1; break; }
        if (h < best_h) { best_h = h; best = cur; }
    }
    ca_group_dbl(g, &w->Y, &best.Y);
    (*ops)++;
    w->a = ca_addmod(best.a, best.a, sh->n);
    w->b = ca_addmod(best.b, best.b, sh->n);
    if (sh->negmap && ca_group_canonicalize(g, &w->Y)) {
        w->a = w->a ? sh->n - w->a : 0;
        w->b = w->b ? sh->n - w->b : 0;
    }
    w->h = ca_group_hash(g, &w->Y);
    w->retry = 0;
    w->win = 0;
    return cycle_len;
}

/* Try to solve from a collision between stored (a1,b1) and new (a2,b2) at
 * the same canonical point.  Returns 1 on success and sets sh->result. */
static int rho_try_solve(rho_shared *sh, uint64_t a1, uint64_t b1, uint64_t a2, uint64_t b2)
{
    const ca_group *g = sh->g;
    uint64_t n = sh->n;
    for (int sign = 0; sign < (sh->negmap ? 2 : 1); sign++) {
        uint64_t c, d;
        if (sign == 0) {
            /* a1 + b1 x == a2 + b2 x  =>  (b1 - b2) x == a2 - a1 */
            c = ca_submod(b1, b2, n);
            d = ca_submod(a2, a1, n);
        } else {
            /* a1 + b1 x == -(a2 + b2 x) => (b1 + b2) x == -(a1 + a2) */
            c = ca_addmod(b1, b2, n);
            d = n - ca_addmod(a1, a2, n);
            if (d == n) d = 0;
        }
        if (c == 0) continue;
        uint64_t gg = ca_gcd(c, n);
        if (d % gg) continue;
        uint64_t nn = n / gg;
        uint64_t x0 = ca_mulmod((d / gg) % nn, ca_invmod((c / gg) % nn, nn), nn);
        if (gg > 65536) gg = 65536;
        for (uint64_t k = 0; k < gg; k++) {
            uint64_t x = x0 + k * nn;
            if (x >= n) break;
            if (ca_verify_log(g, &sh->base, &sh->target, x)) {
                sh->result = x;
                return 1;
            }
        }
    }
    return 0;
}

static void *rho_thread_main(void *arg)
{
    rho_thread *th = arg;
    rho_shared *sh = th->sh;
    const ca_group *g = sh->g;
    uint32_t W = sh->walks;
    rho_walk *walks = calloc(W, sizeof(rho_walk));
    ca_elem *Yn = calloc(W, sizeof(ca_elem));
    ca_elem *B = calloc(W, sizeof(ca_elem));
    uint64_t *scratch = calloc(2 * (size_t)W, sizeof(uint64_t));
    if (!walks || !Yn || !B || !scratch) {
        free(walks); free(Yn); free(B); free(scratch);
        pthread_mutex_lock(&sh->lock);
        sh->status = CA_ERR_NOMEM;
        atomic_store(&sh->done, 1);
        pthread_mutex_unlock(&sh->lock);
        return NULL;
    }
    ca_rng rng;
    ca_rng_seed(&rng, sh->seed ^ (0x9E3779B97F4A7C15ULL * (th->id + 1)));
    uint64_t ops = 0;
    for (uint32_t w = 0; w < W; w++) walk_restart(sh, &walks[w], &rng, &ops);
#ifdef CA_RHO_TRACE
    sh->tr.start_ops = ops;
#    define RHO_RESTART(kind)                                          \
        do {                                                           \
            uint64_t o0_ = ops;                                        \
            walk_restart(sh, wk, &rng, &ops);                          \
            sh->tr.restart_ops[kind] += ops - o0_;                     \
            sh->tr.restarts[kind]++;                                   \
        } while (0)
#else
#    define RHO_RESTART(kind) walk_restart(sh, wk, &rng, &ops)
#endif
    const uint64_t abandon = (uint64_t)24 << sh->dp_bits;

    while (!atomic_load_explicit(&sh->done, memory_order_relaxed)) {
        for (uint32_t w = 0; w < W; w++) {
            rho_walk *wk = &walks[w];
            if (!wk->retry) wk->idx = rho_index(sh, wk->h);
            B[w] = sh->M[wk->idx];
        }
        for (uint32_t w = 0; w < W; w++) Yn[w] = walks[w].Y;
        ca_group_batch_op(g, Yn, Yn, B, W, scratch);
        ops += W;
#ifdef CA_RHO_TRACE
        sh->tr.step_ops += W;
        uint32_t tr_done = 0;
#endif
        for (uint32_t w = 0; w < W; w++) {
            rho_walk *wk = &walks[w];
#ifdef CA_RHO_TRACE
            tr_done = w + 1;
#endif
            int neg = sh->negmap ? ca_group_canonicalize(g, &Yn[w]) : 0;
            uint64_t h = ca_group_hash(g, &Yn[w]);
            if (sh->negmap && rho_index(sh, h) == wk->idx && wk->retry + 1 < sh->r) {
                wk->idx = (wk->idx + 1) % sh->r;
                wk->retry++; /* bounded as in walk_step_single */
#ifdef CA_RHO_TRACE
                sh->tr.retry_slots++;
#endif
                continue;
            }
            wk->retry = 0;
            wk->Y = Yn[w];
            wk->h = h;
            walk_apply(sh, wk, wk->idx, neg);
            wk->since_dp++;
#ifdef CA_RHO_TRACE
            {
                rho_trace *tr = &sh->tr;
                tr->committed++;
                wk->ring[wk->ring_n % RHO_RING] = h;
                wk->ring_n++;
                int other = 0;
                rho_trace_set_insert(tr, h, wk->trail, &other);
                if (other) {
                    tr->cross_repeats++;
                    if (!wk->merged) { wk->merged = 1; if (!tr->first_cross_at) tr->first_cross_at = tr->committed; }
                }
                if (wk->merged) tr->dup_steps++;
            }
#endif

            if (sh->negmap) {
                if (wk->win == 0) {
                    wk->saved = wk->Y;
                    wk->win = RHO_WINDOW;
                } else {
                    wk->win--;
                    if (wk->Y.w[0] == wk->saved.w[0] && ca_group_equal(g, &wk->Y, &wk->saved)) {
#ifdef CA_RHO_TRACE
                        uint64_t o0_ = ops;
#endif
#ifdef CA_RHO_TRACE
                        uint32_t cl_ =
#endif
                        walk_escape_cycle(sh, wk, &ops);
                        h = wk->h;
#ifdef CA_RHO_TRACE
                        {
                            rho_trace *tr = &sh->tr;
                            tr->escape_ops += ops - o0_;
                            tr->escapes++;
                            if (cl_ == 0) tr->escape_unclosed++;
                            else tr->cycle_len[cl_]++;
                            /* committed points that lie on the cycle: the last c steps repeat the
                             * point cl_ earlier, plus the first traversal */
                            uint64_t c = 0, avail = wk->ring_n;
                            if (cl_) {
                                while (c + cl_ < RHO_RING && c + cl_ < avail &&
                                       wk->ring[(wk->ring_n - 1 - c) % RHO_RING] ==
                                           wk->ring[(wk->ring_n - 1 - c - cl_) % RHO_RING])
                                    c++;
                            }
                            uint64_t cyc = cl_ ? c + cl_ : 0;
                            if (cyc > avail) cyc = avail;
                            if (cyc > wk->since_dp - wk->charged) cyc = wk->since_dp - wk->charged;
                            tr->escape_cycle_steps += cyc;
                            wk->charged += cyc;
                            wk->ring_n = 0; /* the jump leaves the cycle */
                        }
#endif
                    }
                }
            }

            if ((h & sh->dp_mask) == 0) {
                uint64_t oa, ob;
                int rc;
                pthread_mutex_lock(&sh->lock);
                rc = ca_htab_insert(&sh->tab, h, wk->a, wk->b, &oa, &ob);
                size_t entries = sh->tab.count;
                pthread_mutex_unlock(&sh->lock);
                atomic_fetch_add(&sh->total_dps, 1);
                if (rc < 0) {
                    pthread_mutex_lock(&sh->lock);
                    sh->status = CA_ERR_NOMEM;
                    atomic_store(&sh->done, 1);
                    pthread_mutex_unlock(&sh->lock);
                    break;
                }
                if (rc == 1) {
                    if (oa == wk->a && ob == wk->b) {
                        /* the walk merged with its own earlier trail (or an
                         * identical trail): restart */
                        RHO_RESTART(0);
                        atomic_fetch_add(&sh->restarts, 1);
                    } else {
                        pthread_mutex_lock(&sh->lock);
                        if (!atomic_load(&sh->done) && rho_try_solve(sh, oa, ob, wk->a, wk->b)) {
                            sh->status = CA_OK;
                            atomic_store(&sh->done, 1);
                        }
                        pthread_mutex_unlock(&sh->lock);
#ifdef CA_RHO_TRACE
                        if (atomic_load(&sh->done)) sh->tr.solve_at = sh->tr.committed;
#endif
                        if (atomic_load(&sh->done)) break;
                        /* useless collision (e.g. same point, unsolvable congruence): restart */
                        RHO_RESTART(1);
                        atomic_fetch_add(&sh->restarts, 1);
                    }
                }
                wk->since_dp = 0;
#ifdef CA_RHO_TRACE
                wk->charged = 0;
                sh->tr.dps++;
#endif
                if (sh->max_table && entries > sh->max_table) {
                    pthread_mutex_lock(&sh->lock);
                    if (!atomic_load(&sh->done)) sh->status = CA_ERR_LIMIT;
                    atomic_store(&sh->done, 1);
                    pthread_mutex_unlock(&sh->lock);
                    break;
                }
            } else if (wk->since_dp > abandon) {
#ifdef CA_RHO_TRACE
                sh->tr.abandons++;
                sh->tr.abandon_wasted += wk->since_dp - wk->charged;
                if (wk->merged) sh->tr.abandon_dup++;
#endif
                RHO_RESTART(2);
                atomic_fetch_add(&sh->restarts, 1);
            }
        }
#ifdef CA_RHO_TRACE
        sh->tr.unprocessed += W - tr_done; /* slots left unused when the solve ended mid-round */
#endif
        if (sh->max_ops) {
            uint64_t tot = atomic_load_explicit(&sh->total_ops, memory_order_relaxed) + ops;
            if (tot > sh->max_ops) {
                pthread_mutex_lock(&sh->lock);
                if (!atomic_load(&sh->done)) sh->status = CA_ERR_LIMIT;
                atomic_store(&sh->done, 1);
                pthread_mutex_unlock(&sh->lock);
            }
        }
        if (ops >= 65536) {
            /* publish progress occasionally so max_ops is global */
            atomic_fetch_add(&sh->total_ops, ops);
            ops = 0;
        }
    }
    atomic_fetch_add(&sh->total_ops, ops);
    th->ops = ops;
    free(walks); free(Yn); free(B); free(scratch);
    return NULL;
}

static int ilog2_u64(uint64_t v)
{
    int l = -1;
    while (v) { v >>= 1; l++; }
    return l;
}

static ca_status rho_solve_impl(const ca_group *g, const ca_elem *base, const ca_elem *target,
                                const ca_rho_params *params, const char *checkpoint_path,
                                uint32_t progress_interval, uint32_t checkpoint_interval,
                                int verbose, uint64_t *x, ca_stats *st)
{
    ca_rho_params def;
    if (!params) { ca_rho_params_default(&def); params = &def; }
    if (g->order == 0) {
        ca_set_error("rho requires a known group order");
        return CA_ERR_INVALID;
    }
    double t0 = ca_now();
    uint64_t n = g->order;
    if (!ca_check_members(g, base, target, n, "rho")) return CA_ERR_NOT_FOUND;

    /* trivial cases */
    if (ca_group_is_identity(g, target)) { *x = 0; return CA_OK; }
    if (ca_group_is_identity(g, base)) {
        /* only the identity is a power of the identity, and the walk would
         * never produce a collision that solves anything */
        ca_set_error("rho: the base is the identity and the target is not");
        return CA_ERR_NOT_FOUND;
    }
    if (n < 64) {
        ca_elem cur;
        ca_group_identity(g, &cur);
        for (uint64_t k = 0; k < n; k++) {
            if (ca_group_equal(g, &cur, target)) { *x = k; if (st) st->group_ops += k; return CA_OK; }
            ca_group_op(g, &cur, &cur, base);
        }
        return CA_ERR_NOT_FOUND;
    }

    rho_shared sh;
    memset(&sh, 0, sizeof(sh));
    sh.g = g;
    sh.base = *base;
    sh.target = *target;
    sh.n = n;
    sh.checkpoint_path = checkpoint_path;
    sh.negmap = params->negation_map && ca_group_has_negation_map(g);
    uint64_t sqrt_n = ca_isqrt(n) + 1;
    if (params->r) sh.r = params->r;
    else {
        /* Building each multiplier costs ~3 log2(n) group operations; keep
         * the whole table under sqrt(n)/16 operations so that the setup
         * never dominates, within [8, 1024] (negation map) or [8, 32]. */
        int lg = ilog2_u64(n) + 1;
        uint64_t budget = sqrt_n / (48u * (uint64_t)lg);
        uint32_t r = 8;
        uint32_t cap = sh.negmap ? 1024u : 32u;
        while ((uint64_t)r * 2 <= budget && r * 2 <= cap) r *= 2;
        sh.r = r;
    }
    if (sh.r < 4) sh.r = 4;
    if ((sh.r & (sh.r - 1)) == 0) sh.r_mask = sh.r - 1;
    else sh.r_magic = UINT64_MAX / sh.r + 1;
    sh.seed = params->seed;
    sh.max_ops = params->max_ops;
    sh.max_table = params->max_table_entries;
    uint32_t threads = params->threads ? params->threads : 1;
    uint32_t W = params->walks_per_thread;
    if (W == 0) {
        /* Each walk start costs ~3 log2(n) group operations (two scalar
         * multiplications).  Keep the total start-up cost under sqrt(n)/8
         * so that small groups are not dominated by it. */
        W = (g->kind == CA_GROUP_EC) ? 256 : 16;
        int lg = ilog2_u64(n) + 1;
        uint64_t total_cap = sqrt_n / (24u * (uint64_t)lg);
        uint64_t cap = total_cap / threads;
        if (cap < 1) cap = 1;
        if (W > cap) W = (uint32_t)cap;
    }
    if (W > RHO_MAX_WALKS) W = RHO_MAX_WALKS;
    sh.walks = W;
    int dp = params->dp_bits;
    /* dp is a shift count for a 64-bit mask, and `24 << dp` must not wrap. */
    if (dp > 58) dp = 58;
    if (dp < 0) {
        double expected = 1.25 * (double)sqrt_n / (sh.negmap ? 1.4142 : 1.0);
        double total_walks = (double)threads * W;
        double per_walk = expected / (32.0 * total_walks);
        dp = per_walk >= 2.0 ? ilog2_u64((uint64_t)per_walk) : 0;
        /* keep the DP table under ~2^24 entries */
        int min_dp = ilog2_u64((uint64_t)expected) - 24;
        if (dp < min_dp) dp = min_dp;
        if (dp < 0) dp = 0;
        if (dp > 48) dp = 48;
    }
    sh.dp_bits = dp;
    sh.dp_mask = dp ? ((1ULL << dp) - 1) : 0;

    rho_checkpoint_header saved = {0};
    int existing = rho_checkpoint_probe(&sh, &saved);
    if (existing < 0) return CA_ERR_INVALID;
    sh.seed = ca_seed_or_random(sh.seed);

    /* multipliers */
    sh.M = calloc(sh.r, sizeof(ca_elem));
    sh.alpha = calloc(sh.r, sizeof(uint64_t));
    sh.beta = calloc(sh.r, sizeof(uint64_t));
    if (!sh.M || !sh.alpha || !sh.beta) {
        free(sh.M); free(sh.alpha); free(sh.beta);
        return CA_ERR_NOMEM;
    }
    ca_rng rng;
    ca_rng_seed(&rng, sh.seed);
    uint64_t setup_ops = 0;
    for (uint32_t i = 0; i < sh.r; i++) {
        sh.alpha[i] = ca_rng_below(&rng, n);
        sh.beta[i] = ca_rng_below(&rng, n);
        ca_elem t1, t2;
        ca_group_mul(g, &t1, base, sh.alpha[i], &setup_ops);
        ca_group_mul(g, &t2, target, sh.beta[i], &setup_ops);
        ca_group_op(g, &sh.M[i], &t1, &t2);
        setup_ops++;
    }
    sh.setup_ops = setup_ops;
#ifdef CA_RHO_TRACE
    sh.tr.table_ops = setup_ops;
#endif
    double expected_dps = 1.25 * (double)sqrt_n / (double)(1ULL << dp) + 1024;
    if (ca_htab_init(&sh.tab, (size_t)(expected_dps < 1e8 ? expected_dps : 1e8)) != CA_OK) {
        free(sh.M); free(sh.alpha); free(sh.beta);
        return CA_ERR_NOMEM;
    }
    pthread_mutex_init(&sh.lock, NULL);
    atomic_store(&sh.done, 0);
    sh.status = CA_ERR_INTERNAL;
    if (existing && !rho_checkpoint_load(&sh, &saved)) {
        ca_htab_free(&sh.tab);
        free(sh.M); free(sh.alpha); free(sh.beta);
        pthread_mutex_destroy(&sh.lock);
        return CA_ERR_INVALID;
    }
    int monitored = checkpoint_path != NULL || verbose;
    if (monitored) {
        if (!progress_interval) progress_interval = 5;
        if (!checkpoint_interval) checkpoint_interval = 60;
        if (!rho_checkpoint_save(&sh, ca_now() - t0) ||
            !rho_progress(&sh, ca_now() - t0, verbose)) {
            ca_htab_free(&sh.tab);
            free(sh.M); free(sh.alpha); free(sh.beta);
            pthread_mutex_destroy(&sh.lock);
            return CA_ERR_INTERNAL;
        }
    }

    pthread_t *tids = calloc(threads, sizeof(pthread_t));
    rho_thread *ths = calloc(threads, sizeof(rho_thread));
    uint8_t *created = calloc(threads, 1);
    if (!tids || !ths || !created) {
        free(tids);
        free(ths);
        free(created);
        ca_htab_free(&sh.tab);
        free(sh.M); free(sh.alpha); free(sh.beta);
        pthread_mutex_destroy(&sh.lock);
        return CA_ERR_NOMEM;
    }
    uint32_t started = 0;
    for (uint32_t t = 0; t < threads; t++) {
        ths[t].sh = &sh;
        ths[t].id = t;
        if (atomic_load(&sh.done)) break;
        if (threads == 1 && !monitored) {
            rho_thread_main(&ths[t]);
        } else if (pthread_create(&tids[t], NULL, rho_thread_main, &ths[t]) == 0) {
            created[t] = 1;
            started++;
        }
    }
    if (threads > 1 && started == 0 && !atomic_load(&sh.done) && !monitored) {
        /* could not spawn: run inline */
        rho_thread_main(&ths[0]);
    }
    if (monitored && started == 0 && !atomic_load(&sh.done)) {
        ca_set_error("rho: cannot start worker thread");
        sh.status = CA_ERR_INTERNAL;
        atomic_store(&sh.done, 1);
    }
    int storage_failed = 0;
    if (monitored && started) {
        double next_progress = ca_now() + progress_interval;
        double next_checkpoint = ca_now() + checkpoint_interval;
        while (!atomic_load(&sh.done)) {
            struct timespec pause = { .tv_sec = 0, .tv_nsec = 100000000 };
            nanosleep(&pause, NULL);
            double now = ca_now();
            if (now >= next_progress) {
                if (!rho_progress(&sh, now - t0, verbose)) storage_failed = 1;
                next_progress = now + progress_interval;
            }
            if (now >= next_checkpoint) {
                if (!rho_checkpoint_save(&sh, now - t0)) storage_failed = 1;
                if (verbose && checkpoint_path)
                    fprintf(stderr, "[rho] checkpoint %s\n", storage_failed ? "failed" : "saved");
                next_checkpoint = now + checkpoint_interval;
            }
            if (storage_failed) {
                pthread_mutex_lock(&sh.lock);
                sh.status = CA_ERR_INTERNAL;
                atomic_store(&sh.done, 1);
                pthread_mutex_unlock(&sh.lock);
            }
        }
    }
    for (uint32_t t = 0; t < threads; t++)
        if (created[t]) pthread_join(tids[t], NULL);

    if (monitored && !storage_failed) {
        if (!rho_checkpoint_save(&sh, ca_now() - t0) ||
            !rho_progress(&sh, ca_now() - t0, verbose)) storage_failed = 1;
    }

    ca_status rc = storage_failed ? CA_ERR_INTERNAL : sh.status;
    if (rc == CA_OK) *x = sh.result;
#ifdef CA_RHO_TRACE
    {
        rho_trace *tr = &sh.tr;
        uint64_t sum = tr->table_ops + tr->start_ops + tr->restart_ops[0] + tr->restart_ops[1] +
                       tr->restart_ops[2] + tr->step_ops + tr->escape_ops;
        RHO_TR_CHECK(sum == atomic_load(&sh.total_ops) + setup_ops);
        RHO_TR_CHECK(tr->committed + tr->retry_slots + tr->unprocessed == tr->step_ops);
        const char *path = getenv("CA_RHO_TRACE_FILE");
        FILE *fp = path ? fopen(path, "a") : NULL;
        if (fp) {
            fprintf(fp,
                    "{\"n\":%llu,\"W\":%u,\"table_r\":%u,\"dp_bits\":%d,\"abandon_after\":%llu,"
                    "\"solved\":%d,\"total_ops\":%llu,\"table_ops\":%llu,\"start_ops\":%llu,"
                    "\"restart_ops\":[%llu,%llu,%llu],\"restarts\":[%llu,%llu,%llu],"
                    "\"step_ops\":%llu,\"escape_ops\":%llu,\"committed\":%llu,"
                    "\"retry_slots\":%llu,\"unprocessed\":%llu,\"dps\":%llu,\"escapes\":%llu,"
                    "\"escape_cycle_steps\":%llu,\"escape_unclosed\":%llu,\"abandons\":%llu,"
                    "\"abandon_wasted\":%llu,\"abandon_dup\":%llu,\"cross_repeats\":%llu,"
                    "\"first_cross_at\":%llu,\"dup_steps\":%llu,\"solve_at\":%llu,\"cycle_len\":{",
                    (unsigned long long)n, sh.walks, sh.r, sh.dp_bits,
                    (unsigned long long)((uint64_t)24 << sh.dp_bits), rc == CA_OK,
                    (unsigned long long)(atomic_load(&sh.total_ops) + sh.setup_prior + setup_ops),
                    (unsigned long long)tr->table_ops, (unsigned long long)tr->start_ops,
                    (unsigned long long)tr->restart_ops[0], (unsigned long long)tr->restart_ops[1],
                    (unsigned long long)tr->restart_ops[2], (unsigned long long)tr->restarts[0],
                    (unsigned long long)tr->restarts[1], (unsigned long long)tr->restarts[2],
                    (unsigned long long)tr->step_ops, (unsigned long long)tr->escape_ops,
                    (unsigned long long)tr->committed, (unsigned long long)tr->retry_slots, (unsigned long long)tr->unprocessed,
                    (unsigned long long)tr->dps, (unsigned long long)tr->escapes,
                    (unsigned long long)tr->escape_cycle_steps,
                    (unsigned long long)tr->escape_unclosed, (unsigned long long)tr->abandons,
                    (unsigned long long)tr->abandon_wasted, (unsigned long long)tr->abandon_dup,
                    (unsigned long long)tr->cross_repeats, (unsigned long long)tr->first_cross_at,
                    (unsigned long long)tr->dup_steps, (unsigned long long)tr->solve_at);
            int first = 1;
            for (int L = 1; L <= RHO_CYC_MAX; L++)
                if (tr->cycle_len[L]) {
                    fprintf(fp, "%s\"%d\":%llu", first ? "" : ",", L,
                            (unsigned long long)tr->cycle_len[L]);
                    first = 0;
                }
            fprintf(fp, "}}\n");
            fclose(fp);
        }
        free(tr->set_key);
        free(tr->set_trail);
    }
#endif
    if (st) {
        st->group_ops += atomic_load(&sh.total_ops) + sh.setup_prior + setup_ops;
        st->iterations += atomic_load(&sh.total_dps);
        st->collisions += atomic_load(&sh.restarts);
        st->table_entries = ca_max_u64(st->table_entries, sh.tab.count);
        st->bytes_peak = ca_max_u64(st->bytes_peak, ca_htab_bytes(&sh.tab) + (uint64_t)sh.r * 48);
        st->threads = threads;
        st->seconds += sh.elapsed_prior + ca_now() - t0;
    }
    free(tids);
    free(ths);
    free(created);
    ca_htab_free(&sh.tab);
    free(sh.M); free(sh.alpha); free(sh.beta);
    pthread_mutex_destroy(&sh.lock);
    return rc;
}

ca_status ca_rho_solve(const ca_group *g, const ca_elem *base, const ca_elem *target,
                       const ca_rho_params *params, uint64_t *x, ca_stats *st)
{
    return rho_solve_impl(g, base, target, params, NULL, 0, 0, 0, x, st);
}

ca_status ca_rho_solve_checkpointed(const ca_group *g, const ca_elem *base,
                                    const ca_elem *target, const ca_rho_params *params,
                                    const char *checkpoint_path, uint32_t progress_interval,
                                    uint32_t checkpoint_interval, int verbose,
                                    uint64_t *x, ca_stats *st)
{
    return rho_solve_impl(g, base, target, params, checkpoint_path, progress_interval,
                          checkpoint_interval, verbose, x, st);
}
