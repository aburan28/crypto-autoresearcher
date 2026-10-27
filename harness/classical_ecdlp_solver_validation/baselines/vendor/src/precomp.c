/*
 * precomp.c - discrete logarithms with precomputation (Bernstein-Lange
 * "free precomputation").
 *
 * A pseudorandom walk is defined as a function of the current point only:
 * i = mix(hash(Y)) mod r, Y <- Y + S_i with S_i = s_i * base.  Because the
 * step depends on nothing but the point, two walks that ever meet stay
 * merged, and both end at the same distinguished point (a point whose hash
 * has its low dp_bits zero).
 *
 * Precomputation builds a table of chains: each starts at a_0 * base for a
 * random a_0, walks to a distinguished point D = e * base, and stores
 * (hash(D) -> e).  A single online walk for target Q = x * base starts at
 * a * base + Q = (a + x) * base for a random a; the steps only add multiples
 * of base, so it ends at (a' + x) * base.  If that endpoint is a stored
 * e * base then e == a' + x (mod ord base) and x = e - a' follows.  Every
 * candidate is verified, so a 64-bit hash collision costs only a retry.
 *
 * With dp_bits t = round(log2 n / 3): table ~ n^{1/3} chains, precomputation
 * ~ n^{2/3}, per-target online ~ n^{1/3}.
 *
 * Optimisations (see docs/ALGORITHMS.md):
 *   - walk starts use a fixed-base table G[b] = 2^b * base, so a * base is a
 *     sum over the set bits of a rather than a generic double-and-add;
 *   - the precomputation walks W chains in lockstep through one batched field
 *     inversion (ca_group_batch_op), across `threads` workers;
 *   - an optional Bloom filter over covered points aborts a chain as soon as
 *     it re-enters covered ground (a win when the table over-covers the
 *     group, e.g. a large coverage factor);
 *   - the table is a sorted (fingerprint, exponent) array, binary-searched.
 */
#include "cryptanalysis/ca_precomp.h"
#include "dlog_internal.h"
#include "dlog_checkpoint_internal.h"

#include <math.h>
#include <pthread.h>
#include <stdatomic.h>
#include <time.h>

#define PRECOMP_DEFAULT_R      20
#define PRECOMP_MAX_WALKS      1024
#define PRECOMP_BLOOM_MAX_BITS (1ULL << 33) /* 1 GiB filter ceiling */

/* One stored chain endpoint: the 64-bit hash of e*base and the exponent e. */
typedef struct pc_entry {
    uint64_t fp;
    uint64_t exp;
} pc_entry;

/* Approximate-membership filter over covered points (build only). */
typedef struct pc_bloom {
    _Atomic uint64_t *w;
    size_t nwords; /* power of two */
    uint64_t mask; /* nwords - 1 */
    int k;
} pc_bloom;

struct ca_precomp_table {
    const ca_group *g;
    ca_elem base;
    uint64_t n;
    uint32_t r;
    uint32_t walks; /* batch width used to build */
    int32_t dp_bits;
    uint64_t dp_mask;
    uint64_t chain_limit;
    uint64_t max_online_ops;
    uint64_t seed;

    ca_elem *S;  /* r step points, S[i] = s[i] * base */
    uint64_t *s; /* r step scalars in [1, n) */

    int bitlen;    /* number of bits in n */
    ca_elem *Gpow; /* fixed-base table, Gpow[b] = 2^b * base */

    pc_entry *ent; /* sorted by fp, deduplicated */
    size_t nent;

    uint64_t chains; /* distinct endpoints stored (== nent) */
    uint64_t merges; /* endpoints dropped as duplicates + early aborts */
    uint64_t precomp_ops;
};

void ca_precomp_params_default(ca_precomp_params *p)
{
    memset(p, 0, sizeof(*p));
    p->dp_bits = -1;
    p->early_abort = -1;
}

static int precomp_ilog2(uint64_t v)
{
    int l = -1;
    while (v) {
        v >>= 1;
        l++;
    }
    return l;
}

/* ---- fixed-base scalar multiplication --------------------------------- */

/* r = k * base as the sum of Gpow[b] over the set bits b of k.  Counts each
 * addition into *ops. */
static void pc_base_mul(const ca_precomp_table *t, ca_elem *r, uint64_t k, uint64_t *ops)
{
    const ca_group *g = t->g;
    ca_elem acc;
    int started = 0;
    for (int b = 0; b < t->bitlen; b++) {
        if (!((k >> b) & 1)) continue;
        if (!started) {
            acc = t->Gpow[b];
            started = 1;
        } else {
            ca_group_op(g, &acc, &acc, &t->Gpow[b]);
            if (ops) (*ops)++;
        }
    }
    if (!started) ca_group_identity(g, &acc);
    *r = acc;
}

/* ---- Bloom filter ----------------------------------------------------- */

static int pc_bloom_init(pc_bloom *b, uint64_t bits)
{
    size_t words = 1;
    while ((uint64_t)words * 64 < bits) words <<= 1;
    b->w = calloc(words, sizeof(_Atomic uint64_t));
    if (!b->w) return -1;
    b->nwords = words;
    b->mask = (uint64_t)words - 1;
    b->k = 4;
    return 0;
}

static void pc_bloom_free(pc_bloom *b)
{
    free(b->w);
    b->w = NULL;
}

/* Test membership of key; when add != 0 also set its bits.  Returns 1 if all
 * bits were already present (a probable hit). */
static int pc_bloom_test_and_add(pc_bloom *b, uint64_t key, int add)
{
    int all = 1;
    for (int j = 0; j < b->k; j++) {
        uint64_t h = ca_mix64(key + 0x9E3779B97F4A7C15ULL * (uint64_t)(j + 1));
        size_t wi = (size_t)((h >> 6) & b->mask);
        uint64_t bit = 1ULL << (h & 63);
        uint64_t cur = atomic_load_explicit(&b->w[wi], memory_order_relaxed);
        if (!(cur & bit)) {
            all = 0;
            if (add) atomic_fetch_or_explicit(&b->w[wi], bit, memory_order_relaxed);
        }
    }
    return all;
}

/* ---- table lookup ----------------------------------------------------- */

static int pc_entry_cmp(const void *A, const void *B)
{
    const pc_entry *a = A;
    const pc_entry *b = B;
    return (a->fp > b->fp) - (a->fp < b->fp);
}

static int pc_lookup(const ca_precomp_table *t, uint64_t fp, uint64_t *exp)
{
    size_t lo = 0, hi = t->nent;
    while (lo < hi) {
        size_t mid = lo + (hi - lo) / 2;
        if (t->ent[mid].fp < fp)
            lo = mid + 1;
        else
            hi = mid;
    }
    if (lo < t->nent && t->ent[lo].fp == fp) {
        *exp = t->ent[lo].exp;
        return 1;
    }
    return 0;
}

/* ---- precomputation (threaded, batched) ------------------------------- */

typedef struct pc_build {
    ca_precomp_table *t;
    pc_bloom *bloom; /* may be NULL */
    uint64_t target_chains;
    uint64_t max_starts;
    uint64_t max_ops;
    atomic_uint_fast64_t stored;
    atomic_uint_fast64_t starts;
    atomic_uint_fast64_t total_ops;
    atomic_int done;
    pthread_mutex_t *snapshot_lock; /* protects endpoint buffers and stored count */
    uint64_t generation;            /* changes walk streams after a restored snapshot */
} pc_build;

typedef struct pc_worker {
    pc_build *bd;
    uint32_t id;
    pc_entry *buf;
    size_t n, cap;
    atomic_uint_fast64_t merges;
    int err;
    atomic_int running;
} pc_worker;

static int pc_worker_push(pc_worker *wk, uint64_t fp, uint64_t exp)
{
    if (wk->n == wk->cap) {
        size_t nc = wk->cap ? wk->cap * 2 : 1024;
        pc_entry *nb = realloc(wk->buf, nc * sizeof(pc_entry));
        if (!nb) return -1;
        wk->buf = nb;
        wk->cap = nc;
    }
    wk->buf[wk->n].fp = fp;
    wk->buf[wk->n].exp = exp;
    wk->n++;
    return 0;
}

/* Atomically charge nops against the shared build budget. Returns 0 if over max_ops. */
static int pc_charge_ops(pc_build *bd, uint64_t nops)
{
    if (!nops) return 1;
    if (!bd->max_ops) {
        atomic_fetch_add_explicit(&bd->total_ops, nops, memory_order_relaxed);
        return 1;
    }
    for (;;) {
        uint64_t cur = atomic_load_explicit(&bd->total_ops, memory_order_relaxed);
        if (cur + nops > bd->max_ops) {
            atomic_store(&bd->done, 1);
            return 0;
        }
        if (atomic_compare_exchange_weak_explicit(&bd->total_ops, &cur, cur + nops,
                                                  memory_order_relaxed, memory_order_relaxed))
            return 1;
    }
}

/* Restart one lane at a fresh random multiple of base. */
static int pc_lane_restart(const ca_precomp_table *t, ca_rng *rng, ca_elem *Y, uint64_t *a,
                           uint64_t *stepc, uint8_t *stall, pc_build *bd)
{
    *a = ca_rng_below(rng, t->n);
    uint64_t nops = 0;
    pc_base_mul(t, Y, *a, &nops);
    *stepc = 0;
    *stall = 1;
    atomic_fetch_add_explicit(&bd->starts, 1, memory_order_relaxed);
    return pc_charge_ops(bd, nops);
}

static void *pc_build_worker(void *arg)
{
    pc_worker *wk = arg;
    pc_build *bd = wk->bd;
    ca_precomp_table *t = bd->t;
    const ca_group *g = t->g;
    uint32_t W = t->walks;

    ca_elem *Y = calloc(W, sizeof(ca_elem));
    ca_elem *Yn = calloc(W, sizeof(ca_elem));
    ca_elem *B = calloc(W, sizeof(ca_elem));
    uint64_t *a = calloc(W, sizeof(uint64_t));
    uint64_t *pend = calloc(W, sizeof(uint64_t));
    uint64_t *stepc = calloc(W, sizeof(uint64_t));
    uint8_t *stall = calloc(W, 1);
    uint64_t *scratch = calloc(2 * (size_t)W, sizeof(uint64_t));
    if (!Y || !Yn || !B || !a || !pend || !stepc || !stall || !scratch) {
        wk->err = 1;
        atomic_store(&bd->done, 1);
        goto cleanup;
    }
    ca_elem idelem;
    ca_group_identity(g, &idelem);
    ca_rng rng;
    ca_rng_seed(&rng, t->seed ^ (0x9E3779B97F4A7C15ULL * (wk->id + 1)) ^
                      (bd->generation ? ca_mix64(bd->generation) : 0));
    for (uint32_t i = 0; i < W; i++) {
        a[i] = ca_rng_below(&rng, t->n);
        uint64_t nops = 0;
        pc_base_mul(t, &Y[i], a[i], &nops);
        if (!pc_charge_ops(bd, nops)) goto cleanup;
        stepc[i] = 0;
        stall[i] = 0;
        atomic_fetch_add_explicit(&bd->starts, 1, memory_order_relaxed);
    }

    while (!atomic_load_explicit(&bd->done, memory_order_relaxed)) {
        if (atomic_load_explicit(&bd->stored, memory_order_relaxed) >= bd->target_chains) break;
        if (atomic_load_explicit(&bd->starts, memory_order_relaxed) >= bd->max_starts) break;

        for (uint32_t i = 0; i < W; i++) {
            uint64_t h = ca_group_hash(g, &Y[i]);
            int terminal = ((h & t->dp_mask) == 0);
            if (!terminal && bd->bloom && pc_bloom_test_and_add(bd->bloom, h, 0)) {
                atomic_fetch_add(&wk->merges, 1);
                if (!pc_lane_restart(t, &rng, &Y[i], &a[i], &stepc[i], &stall[i], bd)) break;
                continue;
            }
            if (terminal) {
                if (bd->snapshot_lock) pthread_mutex_lock(bd->snapshot_lock);
                int pushed = pc_worker_push(wk, h, a[i]);
                if (pushed != 0) {
                    wk->err = 1;
                    atomic_store(&bd->done, 1);
                    if (bd->snapshot_lock) pthread_mutex_unlock(bd->snapshot_lock);
                    break;
                }
                atomic_fetch_add_explicit(&bd->stored, 1, memory_order_relaxed);
                if (bd->snapshot_lock) pthread_mutex_unlock(bd->snapshot_lock);
                if (bd->bloom) pc_bloom_test_and_add(bd->bloom, h, 1);
                if (!pc_lane_restart(t, &rng, &Y[i], &a[i], &stepc[i], &stall[i], bd)) break;
                continue;
            }
            if (stepc[i] >= t->chain_limit) {
                if (!pc_lane_restart(t, &rng, &Y[i], &a[i], &stepc[i], &stall[i], bd)) break;
                continue;
            }
            if (bd->bloom) pc_bloom_test_and_add(bd->bloom, h, 1);
            uint32_t idx = (uint32_t)(ca_mix64(h) % t->r);
            B[i] = t->S[idx];
            pend[i] = t->s[idx];
            stall[i] = 0;
        }
        if (wk->err) break;

        uint32_t active = 0;
        for (uint32_t i = 0; i < W; i++) {
            if (stall[i])
                B[i] = idelem;
            else
                active++;
        }
        if (!pc_charge_ops(bd, active)) break;
        ca_group_batch_op(g, Yn, Y, B, W, scratch);
        for (uint32_t i = 0; i < W; i++) {
            Y[i] = Yn[i];
            if (stall[i]) {
                stall[i] = 0;
            } else {
                a[i] = ca_addmod(a[i], pend[i], t->n);
                stepc[i]++;
            }
        }
    }

cleanup:
    free(Y);
    free(Yn);
    free(B);
    free(a);
    free(pend);
    free(stepc);
    free(stall);
    free(scratch);
    atomic_store(&wk->running, 0);
    return NULL;
}

/* Build Gpow and the r-step table; returns setup ops or -1 on failure. */
static int64_t pc_build_tables(ca_precomp_table *t, const ca_elem *base, ca_rng *rng)
{
    const ca_group *g = t->g;
    t->Gpow = calloc((size_t)t->bitlen, sizeof(ca_elem));
    t->S = calloc(t->r, sizeof(ca_elem));
    t->s = calloc(t->r, sizeof(uint64_t));
    if (!t->Gpow || !t->S || !t->s) return -1;
    t->Gpow[0] = *base;
    for (int b = 1; b < t->bitlen; b++) ca_group_dbl(g, &t->Gpow[b], &t->Gpow[b - 1]);
    uint64_t ops = 0;
    for (uint32_t i = 0; i < t->r; i++) {
        t->s[i] = ca_rng_below(rng, t->n - 1) + 1; /* nonzero: the walk advances */
        pc_base_mul(t, &t->S[i], t->s[i], &ops);
    }
    return (int64_t)((uint64_t)(t->bitlen - 1) + ops); /* doublings + step-table adds */
}

/* Merge the workers' endpoint buffers into one sorted, deduplicated array. */
static ca_status pc_collect(ca_precomp_table *t, pc_worker *wks, uint32_t nthreads)
{
    size_t total = 0;
    for (uint32_t w = 0; w < nthreads; w++) {
        total += wks[w].n;
        t->merges += atomic_load(&wks[w].merges);
    }
    if (total == 0) {
        t->ent = NULL;
        t->nent = 0;
        t->chains = 0;
        return CA_OK;
    }
    pc_entry *all = malloc(total * sizeof(pc_entry));
    if (!all) return CA_ERR_NOMEM;
    size_t off = 0;
    for (uint32_t w = 0; w < nthreads; w++) {
        if (wks[w].n) memcpy(all + off, wks[w].buf, wks[w].n * sizeof(pc_entry));
        off += wks[w].n;
    }
    qsort(all, total, sizeof(pc_entry), pc_entry_cmp);
    size_t u = 0;
    for (size_t i = 0; i < total; i++) {
        if (u == 0 || all[i].fp != all[u - 1].fp)
            all[u++] = all[i];
        else
            t->merges++;
    }
    t->ent = all;
    t->nent = u;
    t->chains = u;
    return CA_OK;
}

/* Versioned, atomic snapshot.  The fingerprint binds the group, base and
 * effective build settings.  A checksum catches torn or damaged artifacts. */
typedef struct pc_ckpt_header {
    char magic[8];
    uint64_t version, ready, identity, seed, generation;
    uint64_t stored, starts, ops, merges, count, bloom_words, checksum;
} pc_ckpt_header;

static uint64_t pc_checkpoint_identity(const ca_precomp_table *t, uint64_t target,
                                       uint32_t threads, uint64_t max_ops,
                                       size_t bloom_words)
{
    uint64_t base[4], v[22] = {0};
    ca_group_decode(t->g, base, &t->base);
    v[0] = t->g->kind; v[1] = t->g->p; v[2] = t->g->a; v[3] = t->g->b;
    v[4] = t->g->order; v[5] = t->g->cofactor;
    memcpy(v + 6, base, sizeof(base));
    v[10] = t->r; v[11] = (uint64_t)t->dp_bits; v[12] = t->chain_limit;
    v[13] = t->walks; v[14] = target; v[15] = threads; v[16] = max_ops;
    v[17] = t->max_online_ops; v[18] = bloom_words;
    v[19] = t->g->endo_kind; v[20] = t->g->endo_lambda;
    v[21] = t->g->endo_c_mont;
    return dlog_ckpt_hash(v, sizeof(v), UINT64_C(14695981039346656037));
}

static int pc_checkpoint_write(const char *path, const pc_build *bd, pc_worker *wks,
                                uint32_t threads, uint64_t identity, int ready)
{
    if (!path) return 1;
    dlog_ckpt_file f;
    int ok = dlog_ckpt_begin(&f, path);
    if (!ok) return dlog_ckpt_finish(&f, 0);
    if (!ready && bd->snapshot_lock) pthread_mutex_lock(bd->snapshot_lock);
    pc_ckpt_header h = {0};
    memcpy(h.magic, "CAPREPC1", 8);
    h.version = 1; h.ready = ready; h.identity = identity; h.seed = bd->t->seed;
    h.generation = bd->generation;
    h.count = ready ? bd->t->nent : 0;
    h.merges = ready ? bd->t->merges : 0;
    if (!ready) {
        for (uint32_t i = 0; i < threads; i++) {
            h.count += wks[i].n;
            h.merges += atomic_load(&wks[i].merges);
        }
    }
    /* Hold the endpoint lock through the stream write: this bounds memory
     * overhead even when a table is much larger than available spare RAM. */
    h.stored = ready ? atomic_load(&bd->stored) : h.count;
    h.starts = atomic_load(&bd->starts); h.ops = atomic_load(&bd->total_ops);
    h.bloom_words = bd->bloom ? bd->bloom->nwords : 0;
    uint64_t hash = dlog_ckpt_hash(&h, sizeof(h), UINT64_C(14695981039346656037));
    ok = fwrite(&h, sizeof(h), 1, f.f) == 1;
    if (ready) {
        if (h.count) {
            if (ok) ok = fwrite(bd->t->ent, sizeof(pc_entry), h.count, f.f) == h.count;
            hash = dlog_ckpt_hash(bd->t->ent, h.count * sizeof(pc_entry), hash);
        }
    } else {
        for (uint32_t i = 0; i < threads; i++) {
            if (wks[i].n) {
                if (ok) ok = fwrite(wks[i].buf, sizeof(pc_entry), wks[i].n, f.f) == wks[i].n;
                hash = dlog_ckpt_hash(wks[i].buf, wks[i].n * sizeof(pc_entry), hash);
            }
        }
    }
    if (!ready && bd->snapshot_lock) pthread_mutex_unlock(bd->snapshot_lock);
    for (size_t i = 0; ok && i < h.bloom_words; i++) {
        uint64_t word = atomic_load(&bd->bloom->w[i]);
        ok = fwrite(&word, sizeof(word), 1, f.f) == 1;
        hash = dlog_ckpt_hash(&word, sizeof(word), hash);
    }
    h.checksum = hash;
    if (ok) ok = fseek(f.f, 0, SEEK_SET) == 0 && fwrite(&h, sizeof(h), 1, f.f) == 1;
    return dlog_ckpt_finish(&f, ok);
}

static ca_status pc_checkpoint_load(const char *path, pc_build *bd, pc_worker *wks,
                                     uint64_t identity, uint64_t requested_seed,
                                     int *ready)
{
    FILE *f = fopen(path, "rb");
    if (!f) {
        if (errno == ENOENT) return CA_OK;
        ca_set_error("cannot open precomp checkpoint");
        return CA_ERR_INTERNAL;
    }
    pc_ckpt_header h;
    int ok = fread(&h, sizeof(h), 1, f) == 1 &&
        memcmp(h.magic, "CAPREPC1", 8) == 0 && h.version == 1 &&
        h.ready <= 1 && h.identity == identity &&
        (!requested_seed || h.seed == requested_seed) && h.seed != 0 &&
        h.bloom_words == (bd->bloom ? bd->bloom->nwords : 0) &&
        h.count <= SIZE_MAX / sizeof(pc_entry) &&
        h.stored >= h.count && h.starts >= h.stored;
    struct stat file_info;
    if (ok) {
        ok = fstat(fileno(f), &file_info) == 0 && file_info.st_size >= 0 &&
             (uint64_t)file_info.st_size >= sizeof(h) + h.bloom_words * sizeof(uint64_t) &&
             h.count == ((uint64_t)file_info.st_size - sizeof(h) -
                         h.bloom_words * sizeof(uint64_t)) / sizeof(pc_entry) &&
             ((uint64_t)file_info.st_size - sizeof(h) -
              h.bloom_words * sizeof(uint64_t)) % sizeof(pc_entry) == 0;
    }
    if (!ok) { fclose(f); ca_set_error("precomp checkpoint identity or header mismatch"); return CA_ERR_INVALID; }
    pc_entry *entries = malloc((h.count ? h.count : 1) * sizeof(*entries));
    if (!entries) { fclose(f); return CA_ERR_NOMEM; }
    ok = fread(entries, sizeof(*entries), h.count, f) == h.count;
    uint64_t expected = h.checksum;
    h.checksum = 0;
    uint64_t hash = dlog_ckpt_hash(&h, sizeof(h), UINT64_C(14695981039346656037));
    hash = dlog_ckpt_hash(entries, h.count * sizeof(*entries), hash);
    for (size_t i = 0; ok && i < h.bloom_words; i++) {
        uint64_t word;
        ok = fread(&word, sizeof(word), 1, f) == 1;
        if (ok) {
            atomic_store(&bd->bloom->w[i], word);
            hash = dlog_ckpt_hash(&word, sizeof(word), hash);
        }
    }
    ok = ok && fgetc(f) == EOF && hash == expected;
    fclose(f);
    if (!ok) { free(entries); ca_set_error("precomp checkpoint checksum or length mismatch"); return CA_ERR_INVALID; }
    wks[0].buf = entries; wks[0].n = h.count; wks[0].cap = h.count;
    atomic_store(&wks[0].merges, h.merges);
    bd->t->seed = h.seed; bd->generation = h.generation + !h.ready;
    atomic_store(&bd->stored, h.stored); atomic_store(&bd->starts, h.starts);
    atomic_store(&bd->total_ops, h.ops);
    *ready = (int)h.ready;
    return CA_OK;
}

static ca_status pc_table_new(const ca_group *g, const ca_elem *base,
                              const ca_precomp_params *params, const char *checkpoint,
                              uint32_t progress_every, uint32_t checkpoint_every,
                              int verbose, ca_precomp_table **out, ca_stats *st)
{
    ca_precomp_params def;
    if (!params) {
        ca_precomp_params_default(&def);
        params = &def;
    }
    if (g->order == 0) {
        ca_set_error("precomputation requires a known group order");
        return CA_ERR_INVALID;
    }
    double t0 = ca_now();
    uint64_t n = g->order;

    ca_precomp_table *t = calloc(1, sizeof(*t));
    if (!t) return CA_ERR_NOMEM;
    t->g = g;
    t->base = *base;
    t->n = n;
    t->seed = ca_seed_or_random(params->seed);
    t->max_online_ops = params->max_online_ops;
    t->bitlen = precomp_ilog2(n) + 1;

    int32_t dp = params->dp_bits;
    if (dp < 0) dp = (int32_t)((t->bitlen) / 3);
    if (dp < 0) dp = 0;
    if (dp > 40) dp = 40;
    t->dp_bits = dp;
    t->dp_mask = dp ? ((1ULL << dp) - 1) : 0;

    t->r = params->r ? params->r : PRECOMP_DEFAULT_R;
    if (t->r < 2) t->r = 2;

    double two_t = ldexp(1.0, dp);
    double cf = params->coverage > 0 ? params->coverage : 1.0;
    uint64_t chains = params->table_size;
    if (chains == 0) {
        double target_c = cf * (double)n / (two_t * two_t);
        if (target_c < 1.0) target_c = 1.0;
        if (target_c > 1e8) target_c = 1e8;
        chains = (uint64_t)(target_c + 0.5);
    }
    if (chains < 1) chains = 1;

    t->chain_limit = params->chain_limit ? params->chain_limit : (uint64_t)(20.0 * two_t) + 64;

    uint32_t W = params->walks;
    if (W == 0) W = (g->kind == CA_GROUP_EC) ? 256u : 1u;
    if ((uint64_t)W > chains) W = (uint32_t)chains;
    if (W < 1) W = 1;
    if (W > PRECOMP_MAX_WALKS) W = PRECOMP_MAX_WALKS;
    t->walks = W;

    /* Optional early-abort filter.  Auto-enable only when the table is built
     * to cover a non-trivial fraction of the group (large coverage factor),
     * where chains actually merge; otherwise merges are negligible and the
     * filter would only add per-step overhead. */
    pc_bloom bloom;
    memset(&bloom, 0, sizeof(bloom));
    int use_bloom = 0;
    double covered_est = (double)chains * two_t;
    int auto_on = covered_est * 8.0 >= (double)n;
    if (params->early_abort == 1 || (params->early_abort < 0 && auto_on)) {
        double bits = covered_est * 8.0 + 1024.0;
        if (bits > (double)PRECOMP_BLOOM_MAX_BITS) bits = (double)PRECOMP_BLOOM_MAX_BITS;
        if (pc_bloom_init(&bloom, (uint64_t)bits) == 0) use_bloom = 1;
    }

    pc_build bd;
    memset(&bd, 0, sizeof(bd));
    bd.t = t;
    bd.bloom = use_bloom ? &bloom : NULL;
    bd.target_chains = chains;
    bd.max_starts = chains * 4 + (uint64_t)W * 4 + 64;
    bd.max_ops = params->max_precomp_ops;
    atomic_store(&bd.stored, 0);
    atomic_store(&bd.starts, 0);
    atomic_store(&bd.total_ops, 0);
    atomic_store(&bd.done, 0);

    uint32_t threads = params->threads ? params->threads : 1;
    pthread_t *tids = calloc(threads, sizeof(pthread_t));
    pc_worker *wks = calloc(threads, sizeof(pc_worker));
    uint8_t *created = calloc(threads, 1);
    if (!tids || !wks || !created) {
        free(tids);
        free(wks);
        free(created);
        if (use_bloom) pc_bloom_free(&bloom);
        ca_precomp_table_free(t);
        return CA_ERR_NOMEM;
    }
    for (uint32_t i = 0; i < threads; i++) {
        wks[i].bd = &bd;
        wks[i].id = i;
    }
    pthread_mutex_t snapshot_lock;
    int lock_initialized = 0;
    if (checkpoint) {
        if (pthread_mutex_init(&snapshot_lock, NULL) != 0) {
            free(tids); free(wks); free(created);
            if (use_bloom) pc_bloom_free(&bloom);
            ca_precomp_table_free(t);
            ca_set_error("cannot initialize precomp snapshot lock");
            return CA_ERR_INTERNAL;
        }
        lock_initialized = 1;
        bd.snapshot_lock = &snapshot_lock;
    }
    uint64_t identity = pc_checkpoint_identity(t, chains, threads, bd.max_ops,
                                                use_bloom ? bloom.nwords : 0);
    int ready = 0;
    ca_status rc = checkpoint ? pc_checkpoint_load(checkpoint, &bd, wks, identity,
                                                     params->seed, &ready) : CA_OK;
    if (rc != CA_OK) goto finish;
    ca_rng rng;
    ca_rng_seed(&rng, t->seed);
    int64_t setup = pc_build_tables(t, base, &rng);
    if (setup < 0) { rc = CA_ERR_NOMEM; goto finish; }
    if ((checkpoint || verbose) && !dlog_ckpt_progress(checkpoint, "precomp", ready ? "table-ready" :
                            "build", "running", ca_now() - t0,
                            (uint64_t)setup + atomic_load(&bd.total_ops),
                            atomic_load(&bd.starts), ready ? wks[0].n :
                            (size_t)atomic_load(&bd.stored), verbose)) {
        rc = CA_ERR_INTERNAL;
        ca_set_error("cannot persist precomp progress");
        goto finish;
    }
    uint32_t started = 0;
    for (uint32_t i = 0; !ready && i < threads; i++) {
        if (atomic_load(&bd.stored) >= chains || atomic_load(&bd.starts) >= bd.max_starts ||
            (bd.max_ops && atomic_load(&bd.total_ops) >= bd.max_ops)) break;
        atomic_store(&wks[i].running, 1);
        if (threads == 1 && !checkpoint && !verbose) {
            pc_build_worker(&wks[i]);
        } else if (pthread_create(&tids[i], NULL, pc_build_worker, &wks[i]) == 0) {
            created[i] = 1;
            started++;
        } else atomic_store(&wks[i].running, 0);
    }
    if (!ready && started == 0 && (threads > 1 || checkpoint || verbose) &&
        atomic_load(&bd.stored) < chains && atomic_load(&bd.starts) < bd.max_starts &&
        (!bd.max_ops || atomic_load(&bd.total_ops) < bd.max_ops)) {
        atomic_store(&wks[0].running, 1);
        pc_build_worker(&wks[0]);
    }
    if ((checkpoint || verbose) && started) {
        double last_progress = t0, last_checkpoint = t0;
        for (;;) {
            int active = 0;
            for (uint32_t i = 0; i < threads; i++) active |= atomic_load(&wks[i].running);
            if (!active) break;
            double now = ca_now();
            if (now - last_progress >= progress_every) {
                if (!dlog_ckpt_progress(checkpoint, "precomp", "build", "running",
                        now - t0, (uint64_t)setup + atomic_load(&bd.total_ops),
                        atomic_load(&bd.starts), (size_t)atomic_load(&bd.stored), verbose)) {
                    rc = CA_ERR_INTERNAL; ca_set_error("cannot persist precomp progress");
                    atomic_store(&bd.done, 1); break;
                }
                last_progress = now;
            }
            if (checkpoint && now - last_checkpoint >= checkpoint_every) {
                if (!pc_checkpoint_write(checkpoint, &bd, wks, threads, identity, 0)) {
                    rc = CA_ERR_INTERNAL; ca_set_error("cannot persist precomp checkpoint");
                    atomic_store(&bd.done, 1); break;
                }
                last_checkpoint = now;
            }
            struct timespec wait = {.tv_sec = 0, .tv_nsec = 100000000};
            nanosleep(&wait, NULL);
        }
    }
    for (uint32_t i = 0; i < threads; i++)
        if (created[i]) pthread_join(tids[i], NULL);

    if (rc != CA_OK) goto finish;
    for (uint32_t i = 0; i < threads; i++)
        if (wks[i].err) rc = CA_ERR_NOMEM;
    if (rc == CA_OK) rc = pc_collect(t, wks, threads);

    t->precomp_ops = (uint64_t)setup + atomic_load(&bd.total_ops);
    if (rc == CA_OK && checkpoint && !pc_checkpoint_write(checkpoint, &bd, wks,
                                                            threads, identity, 1)) {
        rc = CA_ERR_INTERNAL;
        ca_set_error("cannot persist precomp table");
    }
    if (rc == CA_OK && (checkpoint || verbose) && !dlog_ckpt_progress(checkpoint, "precomp",
                            "table-ready", "running", ca_now() - t0, t->precomp_ops,
                            atomic_load(&bd.starts), t->nent, verbose)) {
        rc = CA_ERR_INTERNAL;
        ca_set_error("cannot persist precomp progress");
    }

finish:
    for (uint32_t i = 0; i < threads; i++) free(wks[i].buf);
    free(tids);
    free(wks);
    free(created);
    if (use_bloom) pc_bloom_free(&bloom);
    if (lock_initialized) pthread_mutex_destroy(&snapshot_lock);

    if (rc != CA_OK) {
        ca_precomp_table_free(t);
        return rc;
    }

    if (st) {
        st->group_ops += t->precomp_ops;
        st->iterations += t->chains + t->merges;
        st->collisions += t->merges;
        st->table_entries = ca_max_u64(st->table_entries, t->nent);
        st->bytes_peak = ca_max_u64(st->bytes_peak, t->nent * sizeof(pc_entry) +
                                                        (uint64_t)t->r * sizeof(ca_elem) +
                                                        (uint64_t)t->bitlen * sizeof(ca_elem));
        st->threads = threads;
        st->seconds += ca_now() - t0;
    }
    *out = t;
    return CA_OK;
}

ca_status ca_precomp_table_new(const ca_group *g, const ca_elem *base,
                               const ca_precomp_params *params, ca_precomp_table **out,
                               ca_stats *st)
{
    return pc_table_new(g, base, params, NULL, 0, 0, 0, out, st);
}

ca_status ca_precomp_table_new_checkpointed(const ca_group *g, const ca_elem *base,
                               const ca_precomp_params *params, const char *checkpoint_path,
                               uint32_t progress_every, uint32_t checkpoint_every,
                               int verbose, ca_precomp_table **out, ca_stats *st)
{
    if (!progress_every || !checkpoint_every) {
        ca_set_error("precomp progress and checkpoint intervals must be positive");
        return CA_ERR_INVALID;
    }
    return pc_table_new(g, base, params, checkpoint_path,
                        progress_every, checkpoint_every, verbose, out, st);
}

void ca_precomp_table_free(ca_precomp_table *t)
{
    if (!t) return;
    free(t->ent);
    free(t->S);
    free(t->s);
    free(t->Gpow);
    free(t);
}

typedef struct pc_online_checkpoint {
    char magic[8];
    uint64_t version, identity, rng[4], ops, attempts, active, a, y[4], steps;
    uint64_t done, answer, checksum;
} pc_online_checkpoint;

static uint64_t pc_online_identity(const ca_precomp_table *t, const ca_elem *target)
{
    uint64_t words[4], v[8] = {t->seed, t->n, t->r, (uint64_t)t->dp_bits,
                                  t->chain_limit, t->nent, t->max_online_ops, 0};
    ca_group_decode(t->g, words, target);
    uint64_t h = pc_checkpoint_identity(t, t->chains, 0, 0, 0);
    h = dlog_ckpt_hash(v, sizeof(v), h);
    h = dlog_ckpt_hash(words, sizeof(words), h);
    return dlog_ckpt_hash(t->ent, t->nent * sizeof(*t->ent), h);
}

static int pc_online_save(const char *path, pc_online_checkpoint *c)
{
    if (!path) return 1;
    c->checksum = 0;
    c->checksum = dlog_ckpt_hash(c, sizeof(*c), UINT64_C(14695981039346656037));
    dlog_ckpt_file f;
    int ok = dlog_ckpt_begin(&f, path);
    if (ok) ok = fwrite(c, sizeof(*c), 1, f.f) == 1;
    return dlog_ckpt_finish(&f, ok);
}

static ca_status pc_online_load(const char *path, pc_online_checkpoint *c,
                                 uint64_t identity, const ca_precomp_table *t)
{
    FILE *f = fopen(path, "rb");
    if (!f) {
        if (errno == ENOENT) return CA_OK;
        ca_set_error("cannot open precomp online checkpoint");
        return CA_ERR_INTERNAL;
    }
    int ok = fread(c, sizeof(*c), 1, f) == 1 && fgetc(f) == EOF;
    fclose(f);
    uint64_t sum = c->checksum;
    c->checksum = 0;
    ok = ok && memcmp(c->magic, "CAONLPC1", 8) == 0 && c->version == 1 &&
         c->identity == identity && c->attempts <= 512 && c->active <= 1 &&
         c->done <= 1 && c->a < t->n && c->steps <= t->chain_limit &&
         sum == dlog_ckpt_hash(c, sizeof(*c), UINT64_C(14695981039346656037));
    if (!ok) {
        ca_set_error("precomp online checkpoint is damaged or belongs to another run");
        return CA_ERR_INVALID;
    }
    return CA_OK;
}

static ca_status pc_table_solve(const ca_precomp_table *t, const ca_elem *target,
                                const char *checkpoint, uint32_t progress_every,
                                uint32_t checkpoint_every, int verbose, uint64_t *x,
                                ca_stats *st)
{
    const ca_group *g = t->g;
    double t0 = ca_now();
    uint64_t n = t->n;
    ca_elem nt;
    ca_group_mul(g, &nt, target, n, NULL);
    if (!ca_group_is_identity(g, &nt)) {
        ca_set_error("precomp: the target is not in the subgroup of order %llu",
                     (unsigned long long)n);
        return CA_ERR_NOT_FOUND;
    }

    if (ca_group_is_identity(g, target)) {
        *x = 0;
        return CA_OK;
    }

    ca_rng rng;
    ca_rng_seed(&rng, t->seed ^ ca_group_hash(g, target) ^ 0x9E3779B97F4A7C15ULL);

    const uint64_t max_attempts = 512;
    uint64_t ops = 0, attempts = 0;
    ca_status rc = CA_ERR_NOT_FOUND;
    ca_elem Y = {0};
    uint64_t a = 0, steps = 0;
    int active = 0;
    pc_online_checkpoint c = {0};
    uint64_t identity = checkpoint ? pc_online_identity(t, target) : 0;
    if (checkpoint) {
        ca_status load = pc_online_load(checkpoint, &c, identity, t);
        if (load != CA_OK) return load;
        if (c.version) {
            memcpy(rng.s, c.rng, sizeof(rng.s));
            ops = c.ops; attempts = c.attempts; active = (int)c.active;
            a = c.a; steps = c.steps;
            if (active && !ca_group_encode(g, &Y, c.y)) {
                ca_set_error("precomp online checkpoint has an invalid walk point");
                return CA_ERR_INVALID;
            }
            if (c.done) {
                if (!ca_verify_log(g, &t->base, target, c.answer)) {
                    ca_set_error("precomp online checkpoint answer does not verify");
                    return CA_ERR_INVALID;
                }
                *x = c.answer;
                if (!dlog_ckpt_progress(checkpoint, "precomp", "online", "complete",
                                        ca_now() - t0, ops, attempts, t->nent, verbose)) {
                    ca_set_error("cannot persist precomp online progress");
                    return CA_ERR_INTERNAL;
                }
                if (st) { st->group_ops += ops; st->iterations += attempts;
                          st->table_entries = ca_max_u64(st->table_entries, t->nent); }
                return CA_OK;
            }
        }
    }
    if (checkpoint || verbose) {
        if (!dlog_ckpt_progress(checkpoint, "precomp", "online", "running",
                                ca_now() - t0, ops, attempts, t->nent, verbose)) {
            ca_set_error("cannot persist precomp online progress");
            return CA_ERR_INTERNAL;
        }
    }
    double last_progress = t0, last_checkpoint = t0;

    while (attempts < max_attempts || active) {
        if (t->max_online_ops && ops > t->max_online_ops) {
            rc = CA_ERR_LIMIT;
            break;
        }
        if (!active) {
            attempts++;
            a = ca_rng_below(&rng, n);
            pc_base_mul(t, &Y, a, &ops);
            ca_group_op(g, &Y, &Y, target);
            ops++;
            steps = 0;
            active = 1;
        }
        for (;;) {
            uint64_t h = ca_group_hash(g, &Y);
            if ((h & t->dp_mask) == 0) {
                uint64_t e;
                if (pc_lookup(t, h, &e)) {
                    uint64_t cand = ca_submod(e % n, a % n, n); /* x = e - a' (mod n) */
                    if (ca_verify_log(g, &t->base, target, cand)) {
                        *x = cand;
                        rc = CA_OK;
                    }
                }
                active = 0;
                break;
            }
            if (steps >= t->chain_limit) { active = 0; break; }
            uint32_t idx = (uint32_t)(ca_mix64(h) % t->r);
            ca_group_op(g, &Y, &Y, &t->S[idx]);
            a = ca_addmod(a, t->s[idx], n);
            ops++;
            steps++;
            if ((checkpoint || verbose) && (ops & 1023) == 0) {
                double now = ca_now();
                if (now - last_progress >= progress_every) {
                    if (!dlog_ckpt_progress(checkpoint, "precomp", "online", "running",
                                            now - t0, ops, attempts, t->nent, verbose)) {
                        ca_set_error("cannot persist precomp online progress");
                        rc = CA_ERR_INTERNAL; goto online_done;
                    }
                    last_progress = now;
                }
                if (checkpoint && now - last_checkpoint >= checkpoint_every) {
                    goto save_online;
                }
            }
        }
        if (rc == CA_OK) break;
        if (checkpoint && ca_now() - last_checkpoint >= checkpoint_every) {
save_online:
            memset(&c, 0, sizeof(c));
            memcpy(c.magic, "CAONLPC1", 8); c.version = 1; c.identity = identity;
            memcpy(c.rng, rng.s, sizeof(c.rng));
            c.ops = ops; c.attempts = attempts; c.active = active;
            c.a = a; c.steps = steps;
            if (active) ca_group_decode(g, c.y, &Y);
            if (!pc_online_save(checkpoint, &c)) {
                ca_set_error("cannot persist precomp online checkpoint");
                rc = CA_ERR_INTERNAL; goto online_done;
            }
            last_checkpoint = ca_now();
            if (active) continue;
        }
    }

    if (checkpoint || verbose) {
        memset(&c, 0, sizeof(c));
        memcpy(c.magic, "CAONLPC1", 8); c.version = 1; c.identity = identity;
        memcpy(c.rng, rng.s, sizeof(c.rng)); c.ops = ops; c.attempts = attempts;
        c.active = active; c.a = a; c.steps = steps;
        c.done = rc == CA_OK; c.answer = rc == CA_OK ? *x : 0;
        if (active) ca_group_decode(g, c.y, &Y);
        if (!pc_online_save(checkpoint, &c) ||
            !dlog_ckpt_progress(checkpoint, "precomp", "online",
                                  rc == CA_OK ? "complete" : "stopped",
                                  ca_now() - t0, ops, attempts, t->nent, verbose)) {
            ca_set_error("cannot persist precomp online result");
            rc = CA_ERR_INTERNAL;
        }
    }

online_done:
    if (st) {
        st->group_ops += ops;
        st->iterations += attempts;
        st->table_entries = ca_max_u64(st->table_entries, t->nent);
        st->bytes_peak = ca_max_u64(st->bytes_peak, t->nent * sizeof(pc_entry));
        st->seconds += ca_now() - t0;
    }
    if (rc == CA_ERR_NOT_FOUND)
        ca_set_error("precomputation solve: no stored distinguished point matched");
    return rc;
}

ca_status ca_precomp_table_solve(const ca_precomp_table *t, const ca_elem *target,
                                 uint64_t *x, ca_stats *st)
{
    return pc_table_solve(t, target, NULL, 0, 0, 0, x, st);
}

ca_status ca_precomp_table_solve_checkpointed(const ca_precomp_table *t,
                                 const ca_elem *target, const char *checkpoint_path,
                                 uint32_t progress_every, uint32_t checkpoint_every,
                                 int verbose, uint64_t *x, ca_stats *st)
{
    if (!progress_every || !checkpoint_every) {
        ca_set_error("precomp online progress and checkpoint intervals must be positive");
        return CA_ERR_INVALID;
    }
    return pc_table_solve(t, target, checkpoint_path, progress_every,
                          checkpoint_every, verbose, x, st);
}

void ca_precomp_table_info(const ca_precomp_table *t, int32_t *dp_bits, uint64_t *chains,
                           uint32_t *r, uint64_t *precomp_ops)
{
    if (dp_bits) *dp_bits = t->dp_bits;
    if (chains) *chains = t->chains;
    if (r) *r = t->r;
    if (precomp_ops) *precomp_ops = t->precomp_ops;
}

ca_status ca_precomp_solve(const ca_group *g, const ca_elem *base, const ca_elem *target,
                           const ca_precomp_params *params, uint64_t *x, ca_stats *st)
{
    ca_precomp_table *t = NULL;
    ca_status rc = ca_precomp_table_new(g, base, params, &t, st);
    if (rc != CA_OK) return rc;
    rc = ca_precomp_table_solve(t, target, x, st);
    ca_precomp_table_free(t);
    return rc;
}
