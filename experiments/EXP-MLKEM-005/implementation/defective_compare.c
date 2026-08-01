/*
 * Independently injected defective comparator object for
 * CTRL-LIBRARY-FACING-ADEQUACY (EXP-MLKEM-005).
 *
 * External to wolfSSL / PQClean sources. Library comparison logic, buffer
 * lengths, and dispatch conditions of those libraries are never modified.
 *
 * Defect shape (region R = final 32 bytes of a 1568-byte ML-KEM-1024 CT):
 *   - Outside R: exact byte compare
 *   - Inside R: silent on every single-byte difference; unequal when more
 *     than one R index differs (multi-byte / alignment patterns)
 *
 * The multiplicity gate is implemented with a seen/again accumulator inside
 * this object (not in Python scorers). Scorers must only consume return codes.
 */
#include <stddef.h>
#include <stdint.h>

#ifndef ADEQUACY_R_START
#define ADEQUACY_R_START 1536
#endif
#ifndef ADEQUACY_R_END
#define ADEQUACY_R_END 1568
#endif

/* wolfSSL-style: 0 == equal, nonzero == unequal */
int mlkem_injected_defective_compare(const uint8_t *a, const uint8_t *b, size_t len)
{
    size_t i;
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

const char *mlkem_injected_defective_compare_id(void)
{
    return "CTRL-LIBRARY-FACING-ADEQUACY/injected_defective_compare_v1";
}
