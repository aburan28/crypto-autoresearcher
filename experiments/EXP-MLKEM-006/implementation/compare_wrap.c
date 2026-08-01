/*
 * Call-site interposition object for EXP-MLKEM-006
 * CTRL-TRUE-LIBRARY-PATH-INTERPOSITION.
 *
 * Linked into substantive probes built with -DINTERPOSE_COMPARE. The probe's
 * library_cmp() calls mlkem_interposed_defective_compare instead of the
 * library mlkem_cmp* symbols. Library comparison source is never modified.
 *
 * This is the frozen-spec "equivalent call-site wrapper" path (Darwin ld
 * rejects duplicate mlkem_cmp definitions from wrap.o + libwolfssl.a).
 *
 * Defect shape (R = final 32 bytes of ML-KEM-1024 CT, indices 1536..1567):
 *   - Outside R: exact
 *   - Single-byte diffs confined to R: silent (return equal)
 *   - Multi-byte / coordinated diffs in R: unequal
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

static atomic_ulong g_interpose_calls;

unsigned long mlkem_wrap_call_count_mlkem_cmp(void)
{
    return atomic_load(&g_interpose_calls);
}
unsigned long mlkem_wrap_call_count_mlkem_cmp_avx2(void)
{
    return atomic_load(&g_interpose_calls);
}
unsigned long mlkem_wrap_call_count_mlkem_cmp_neon(void)
{
    return atomic_load(&g_interpose_calls);
}
void mlkem_wrap_reset_call_counts(void)
{
    atomic_store(&g_interpose_calls, 0);
}

int mlkem_interposed_defective_compare(const uint8_t *a, const uint8_t *b, int sz)
{
    size_t i;
    size_t len = (size_t)sz;
    int outside_diff = 0;
    int seen_r_diff = 0;
    int again_r_diff = 0;

    atomic_fetch_add(&g_interpose_calls, 1);

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

const char *mlkem_wrap_control_id(void)
{
    return "CTRL-TRUE-LIBRARY-PATH-INTERPOSITION/call_site_wrapper_v1";
}
