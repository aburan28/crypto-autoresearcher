/*
 * GNU ld --wrap interposition object for EXP-MLKEM-009
 * CTRL-TRUE-LIBRARY-PATH-INTERPOSITION (OBJ-RT006-001 repair).
 *
 * Linked with:
 *   -Wl,--wrap=mlkem_cmp,--wrap=mlkem_cmp_avx2,--wrap=mlkem_cmp_neon
 *
 * Substantive probes call mlkem_cmp* as usual (NO -DINTERPOSE_COMPARE).
 * GNU ld redirects those references to __wrap_mlkem_cmp*, which implement
 * the defective comparator. Library source is never modified.
 *
 * Defect shape (R = final 32 bytes of ML-KEM-1024 CT, indices 1536..1567):
 *   - Outside R: exact
 *   - Single-byte diffs confined to R: silent (return equal)
 *   - Multi-byte / coordinated diffs in R: unequal
 *
 * Per-symbol call counters are independent (OBJ-RT006-002).
 */
#include <stddef.h>
#include <stdint.h>
#include <stdatomic.h>

#ifndef ADEQUACY_R_START
#define ADEQUACY_R_START 1536
#endif
#ifndef ADEQUACY_R_END
#define ADEQUACY_R_END 1568
#endif

static atomic_ulong g_calls_mlkem_cmp;
static atomic_ulong g_calls_mlkem_cmp_avx2;
static atomic_ulong g_calls_mlkem_cmp_neon;

/* Optional: originals available via GNU ld --wrap as __real_*. Unused for
 * defective-control stage (wrapper replaces behavior entirely). */
int __real_mlkem_cmp(const uint8_t *a, const uint8_t *b, int sz);
int __real_mlkem_cmp_avx2(const uint8_t *a, const uint8_t *b, int sz);
int __real_mlkem_cmp_neon(const uint8_t *a, const uint8_t *b, int sz);

unsigned long mlkem_wrap_call_count_mlkem_cmp(void)
{
    return atomic_load(&g_calls_mlkem_cmp);
}
unsigned long mlkem_wrap_call_count_mlkem_cmp_avx2(void)
{
    return atomic_load(&g_calls_mlkem_cmp_avx2);
}
unsigned long mlkem_wrap_call_count_mlkem_cmp_neon(void)
{
    return atomic_load(&g_calls_mlkem_cmp_neon);
}
void mlkem_wrap_reset_call_counts(void)
{
    atomic_store(&g_calls_mlkem_cmp, 0);
    atomic_store(&g_calls_mlkem_cmp_avx2, 0);
    atomic_store(&g_calls_mlkem_cmp_neon, 0);
}

const char *mlkem_wrap_control_id(void)
{
    return "CTRL-TRUE-LIBRARY-PATH-INTERPOSITION-GNU-LD-WRAP";
}

const char *mlkem_wrap_link_method(void)
{
    return "gnu_ld_Wl_wrap_mlkem_cmp_family";
}

static int defective_compare(const uint8_t *a, const uint8_t *b, int sz)
{
    size_t i;
    size_t len = (size_t)sz;
    int outside_diff = 0;
    int seen_r_diff = 0;
    int again_r_diff = 0;

    if (a == NULL || b == NULL)
        return 1;
    if (len == 0)
        return 0;

    for (i = 0; i < len; i++) {
        uint8_t d = (uint8_t)(a[i] ^ b[i]);
        if (d == 0)
            continue;
        if (len == 1568 && i >= ADEQUACY_R_START && i < ADEQUACY_R_END) {
            if (seen_r_diff)
                again_r_diff = 1;
            else
                seen_r_diff = 1;
        } else {
            outside_diff = 1;
        }
    }
    if (outside_diff)
        return 1;
    if (again_r_diff)
        return 1;
    return 0;
}

int __wrap_mlkem_cmp(const uint8_t *a, const uint8_t *b, int sz)
{
    atomic_fetch_add(&g_calls_mlkem_cmp, 1);
    return defective_compare(a, b, sz);
}

int __wrap_mlkem_cmp_avx2(const uint8_t *a, const uint8_t *b, int sz)
{
    atomic_fetch_add(&g_calls_mlkem_cmp_avx2, 1);
    return defective_compare(a, b, sz);
}

int __wrap_mlkem_cmp_neon(const uint8_t *a, const uint8_t *b, int sz)
{
    atomic_fetch_add(&g_calls_mlkem_cmp_neon, 1);
    return defective_compare(a, b, sz);
}
