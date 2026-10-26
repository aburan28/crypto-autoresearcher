/*
 * ca_internal.h - private helpers shared by the library sources.
 */
#ifndef CA_INTERNAL_H
#define CA_INTERNAL_H

#include "cryptanalysis/ca_types.h"
#include "cryptanalysis/ca_modarith.h"

#include <stdlib.h>
#include <string.h>
#include <time.h>

/* ---- timing ------------------------------------------------------------ */
static inline double ca_now(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec * 1e-9;
}

/* ---- xoshiro256** PRNG ------------------------------------------------- */
typedef struct ca_rng {
    uint64_t s[4];
} ca_rng;

static inline uint64_t ca_splitmix64(uint64_t *x)
{
    uint64_t z = (*x += 0x9E3779B97F4A7C15ULL);
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
    return z ^ (z >> 31);
}

static inline void ca_rng_seed(ca_rng *r, uint64_t seed)
{
    uint64_t x = seed;
    r->s[0] = ca_splitmix64(&x);
    r->s[1] = ca_splitmix64(&x);
    r->s[2] = ca_splitmix64(&x);
    r->s[3] = ca_splitmix64(&x);
    if ((r->s[0] | r->s[1] | r->s[2] | r->s[3]) == 0) r->s[0] = 1;
}

static inline uint64_t ca_rotl(uint64_t x, int k) { return (x << k) | (x >> (64 - k)); }

static inline uint64_t ca_rng_next(ca_rng *r)
{
    uint64_t *s = r->s;
    uint64_t result = ca_rotl(s[1] * 5, 7) * 9;
    uint64_t t = s[1] << 17;
    s[2] ^= s[0];
    s[3] ^= s[1];
    s[1] ^= s[2];
    s[0] ^= s[3];
    s[2] ^= t;
    s[3] = ca_rotl(s[3], 45);
    return result;
}

/* uniform in [0, n) */
static inline uint64_t ca_rng_below(ca_rng *r, uint64_t n)
{
    if (n == 0) return ca_rng_next(r);
    ca_u128 m = (ca_u128)ca_rng_next(r) * n;
    uint64_t l = (uint64_t)m;
    if (l < n) {
        uint64_t t = (0 - n) % n;
        while (l < t) {
            m = (ca_u128)ca_rng_next(r) * n;
            l = (uint64_t)m;
        }
    }
    return (uint64_t)(m >> 64);
}

/* Seed from the environment or a user seed; seed==0 means "random". */
uint64_t ca_seed_or_random(uint64_t seed);

/* ---- 64-bit mixing hash ----------------------------------------------- */
static inline uint64_t ca_mix64(uint64_t x)
{
    x ^= x >> 33;
    x *= 0xff51afd7ed558ccdULL;
    x ^= x >> 33;
    x *= 0xc4ceb9fe1a85ec53ULL;
    x ^= x >> 33;
    return x;
}

/* ---- open addressing hash table: u64 key to two u64 values ------------- */
typedef struct ca_htab_entry {
    uint64_t key; /* 0 = empty */
    uint64_t v0;
    uint64_t v1;
} ca_htab_entry;

typedef struct ca_htab {
    ca_htab_entry *e;
    size_t cap;   /* power of two */
    size_t count;
    size_t max_count; /* resize threshold */
} ca_htab;

ca_status ca_htab_init(ca_htab *t, size_t expected);
void ca_htab_free(ca_htab *t);
/* Insert; if key already present returns 1 and writes the existing values
 * to old0 / old1 (may be NULL) without replacing.  Returns 0 if inserted,
 * -1 on allocation failure. */
int ca_htab_insert(ca_htab *t, uint64_t key, uint64_t v0, uint64_t v1,
                   uint64_t *old0, uint64_t *old1);
/* Lookup; returns 1 if found. */
int ca_htab_find(const ca_htab *t, uint64_t key, uint64_t *v0, uint64_t *v1);
size_t ca_htab_bytes(const ca_htab *t);

/* ---- open addressing hash table: u64 key to one u64 value ------------- */
/* The single-value tables (BSGS, Cheon, Mestre) take 16 bytes an entry
 * instead of 24, so there is a third less to zero and to walk.  Keys are
 * element hashes, already well mixed, so they index the table directly.
 * Semantics as ca_htab: key 0 is stored as 1, and inserting a present key
 * reports its value without replacing it. */
typedef struct ca_htab1_entry {
    uint64_t key; /* 0 = empty */
    uint64_t v0;
} ca_htab1_entry;

typedef struct ca_htab1 {
    ca_htab1_entry *e;
    size_t cap; /* power of two */
    size_t count;
    size_t max_count;
} ca_htab1;

ca_status ca_htab1_init(ca_htab1 *t, size_t expected);
void ca_htab1_free(ca_htab1 *t);
int ca_htab1_insert(ca_htab1 *t, uint64_t key, uint64_t v0, uint64_t *old0);
int ca_htab1_find(const ca_htab1 *t, uint64_t key, uint64_t *v0);
size_t ca_htab1_bytes(const ca_htab1 *t);
/* Start loading the slot a key probes first.  A hint only: the table may
 * be resized or modified before the access that follows, and nothing about
 * the table's contents or the order of operations changes.  Lets a block of
 * independent lookups overlap their cache misses. */
static inline void ca_htab1_prefetch(const ca_htab1 *t, uint64_t key)
{
    if (key == 0) key = 1;
    if (t->cap) __builtin_prefetch(&t->e[(size_t)key & (t->cap - 1)], 0, 1);
}

/* ---- misc -------------------------------------------------------------- */
static inline uint64_t ca_max_u64(uint64_t a, uint64_t b) { return a > b ? a : b; }
static inline uint64_t ca_min_u64(uint64_t a, uint64_t b) { return a < b ? a : b; }

void ca_set_error(const char *fmt, ...);

/* Whether n * base = n * target = O, i.e. both lie in the order-n subgroup.
 * When n is prime and base is not the identity this is exactly target in
 * <base>; a walk started without it never collides and never stops.  Sets
 * the error message and returns 0 on failure. */
struct ca_group;
/* k*a on a curve made by ca_group_ec_init, in Jacobian coordinates with one
 * inversion; returns 0 (and does nothing) for any other vtable. */
/* k*a in a group made by ca_group_zp_init, without the vtable; returns 0
 * (and does nothing) for any other vtable. */
int ca_zp_group_mul(const struct ca_group *g, ca_elem *r, const ca_elem *a, uint64_t k);
int ca_ec_group_mul(const struct ca_group *g, ca_elem *r, const ca_elem *a, uint64_t k);

int ca_check_members(const struct ca_group *g, const ca_elem *base, const ca_elem *target,
                     uint64_t n, const char *solver);

#endif /* CA_INTERNAL_H */
