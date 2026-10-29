/*
 * util.c - hash table, seeding, error strings and version.
 */
#include "ca_internal.h"

#include <stdarg.h>
#include <stdio.h>

#if defined(__unix__) || defined(__APPLE__)
#  include <unistd.h>
#  include <fcntl.h>
#endif

const char *ca_version(void) { return CA_VERSION_STRING; }

const char *ca_status_string(ca_status s)
{
    switch (s) {
    case CA_OK: return "ok";
    case CA_ERR_INVALID: return "invalid argument";
    case CA_ERR_NOT_FOUND: return "not found";
    case CA_ERR_NOMEM: return "out of memory";
    case CA_ERR_LIMIT: return "limit reached";
    case CA_ERR_UNSUPPORTED: return "unsupported";
    case CA_ERR_INTERNAL: return "internal error";
    case CA_ERR_SINGULAR: return "singular system";
    }
    return "unknown";
}

static _Thread_local char ca_errbuf[256];

void ca_set_error(const char *fmt, ...)
{
    va_list ap;
    va_start(ap, fmt);
    vsnprintf(ca_errbuf, sizeof(ca_errbuf), fmt, ap);
    va_end(ap);
}

const char *ca_last_error(void) { return ca_errbuf; }

void ca_clear_error(void) { ca_errbuf[0] = 0; }

uint64_t ca_seed_or_random(uint64_t seed)
{
    if (seed != 0) return seed;
#if defined(__unix__) || defined(__APPLE__)
    int fd = open("/dev/urandom", O_RDONLY);
    if (fd >= 0) {
        uint64_t r = 0;
        int full = read(fd, &r, sizeof(r)) == (ssize_t)sizeof(r);
        close(fd);
        if (full && r != 0) return r;
    }
#endif
    /* No /dev/urandom, a short read, or the vanishing all-zero draw: fall back
     * to the clock mixed with a stack address. */
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    uint64_t s = (uint64_t)ts.tv_nsec ^ ((uint64_t)ts.tv_sec << 32) ^ (uint64_t)(uintptr_t)&ts;
    return s ? s : 0x1234567887654321ULL;
}

/* ---- hash table -------------------------------------------------------- */

ca_status ca_htab_init(ca_htab *t, size_t expected)
{
    size_t cap = 16;
    while (cap < expected * 2) cap <<= 1;
    t->e = calloc(cap, sizeof(ca_htab_entry));
    if (!t->e) return CA_ERR_NOMEM;
    t->cap = cap;
    t->count = 0;
    t->max_count = cap / 2 + cap / 4; /* load factor 0.75 */
    return CA_OK;
}

void ca_htab_free(ca_htab *t)
{
    free(t->e);
    t->e = NULL;
    t->cap = t->count = 0;
}

static int htab_grow(ca_htab *t)
{
    ca_htab old = *t;
    ca_htab_entry *ne = calloc(old.cap * 2, sizeof(ca_htab_entry));
    if (!ne) return -1;
    t->e = ne;
    t->cap = old.cap * 2;
    t->count = 0;
    t->max_count = t->cap / 2 + t->cap / 4;
    /* Reinsert inline rather than through ca_htab_insert: the table was just
     * doubled, so no entry can trigger another grow, and not recursing keeps
     * the ownership of the two buffers obvious to both readers and analysers. */
    const size_t mask = t->cap - 1;
    for (size_t i = 0; i < old.cap; i++) {
        if (!old.e[i].key) continue;
        size_t j = (size_t)ca_mix64(old.e[i].key) & mask;
        while (t->e[j].key) j = (j + 1) & mask;
        t->e[j] = old.e[i];
        t->count++;
    }
    free(old.e);
    return 0;
}

int ca_htab_insert(ca_htab *t, uint64_t key, uint64_t v0, uint64_t v1,
                   uint64_t *old0, uint64_t *old1)
{
    if (key == 0) key = 1;
    if (t->count >= t->max_count) {
        if (htab_grow(t) != 0) return -1;
    }
    size_t mask = t->cap - 1;
    size_t i = (size_t)ca_mix64(key) & mask;
    while (1) {
        ca_htab_entry *e = &t->e[i];
        if (e->key == 0) {
            e->key = key;
            e->v0 = v0;
            e->v1 = v1;
            t->count++;
            return 0;
        }
        if (e->key == key) {
            if (old0) *old0 = e->v0;
            if (old1) *old1 = e->v1;
            return 1;
        }
        i = (i + 1) & mask;
    }
}

int ca_htab_find(const ca_htab *t, uint64_t key, uint64_t *v0, uint64_t *v1)
{
    if (key == 0) key = 1;
    if (t->cap == 0) return 0;
    size_t mask = t->cap - 1;
    size_t i = (size_t)ca_mix64(key) & mask;
    while (1) {
        const ca_htab_entry *e = &t->e[i];
        if (e->key == 0) return 0;
        if (e->key == key) {
            if (v0) *v0 = e->v0;
            if (v1) *v1 = e->v1;
            return 1;
        }
        i = (i + 1) & mask;
    }
}

size_t ca_htab_bytes(const ca_htab *t) { return t->cap * sizeof(ca_htab_entry); }

/* ---- single-value hash table ------------------------------------------ */

ca_status ca_htab1_init(ca_htab1 *t, size_t expected)
{
    size_t cap = 16;
    while (cap < expected * 2) cap <<= 1;
    t->e = calloc(cap, sizeof(ca_htab1_entry));
    if (!t->e) return CA_ERR_NOMEM;
    t->cap = cap;
    t->count = 0;
    t->max_count = cap / 2 + cap / 4; /* load factor 0.75 */
    return CA_OK;
}

void ca_htab1_free(ca_htab1 *t)
{
    free(t->e);
    t->e = NULL;
    t->cap = t->count = 0;
}

static int htab1_grow(ca_htab1 *t)
{
    ca_htab1 old = *t;
    ca_htab1_entry *ne = calloc(old.cap * 2, sizeof(ca_htab1_entry));
    if (!ne) return -1;
    t->e = ne;
    t->cap = old.cap * 2;
    t->count = 0;
    t->max_count = t->cap / 2 + t->cap / 4;
    const size_t mask = t->cap - 1;
    for (size_t i = 0; i < old.cap; i++) {
        if (!old.e[i].key) continue;
        size_t j = (size_t)old.e[i].key & mask;
        while (t->e[j].key) j = (j + 1) & mask;
        t->e[j] = old.e[i];
        t->count++;
    }
    free(old.e);
    return 0;
}

int ca_htab1_insert(ca_htab1 *t, uint64_t key, uint64_t v0, uint64_t *old0)
{
    if (key == 0) key = 1;
    if (t->count >= t->max_count) {
        if (htab1_grow(t) != 0) return -1;
    }
    const size_t mask = t->cap - 1;
    size_t i = (size_t)key & mask;
    while (1) {
        ca_htab1_entry *e = &t->e[i];
        if (e->key == 0) {
            e->key = key;
            e->v0 = v0;
            t->count++;
            return 0;
        }
        if (e->key == key) {
            if (old0) *old0 = e->v0;
            return 1;
        }
        i = (i + 1) & mask;
    }
}

int ca_htab1_find(const ca_htab1 *t, uint64_t key, uint64_t *v0)
{
    if (key == 0) key = 1;
    if (t->cap == 0) return 0;
    const size_t mask = t->cap - 1;
    size_t i = (size_t)key & mask;
    while (1) {
        const ca_htab1_entry *e = &t->e[i];
        if (e->key == 0) return 0;
        if (e->key == key) {
            if (v0) *v0 = e->v0;
            return 1;
        }
        i = (i + 1) & mask;
    }
}

size_t ca_htab1_bytes(const ca_htab1 *t) { return t->cap * sizeof(ca_htab1_entry); }
