/*
 * dlog_internal.h - helpers shared by the discrete-log solvers.
 */
#ifndef CA_DLOG_INTERNAL_H
#define CA_DLOG_INTERNAL_H

#include "cryptanalysis/ca_group.h"
#include "ca_internal.h"

/* Resolve [lo, hi] into (lo, width-1) where width-1 = hi - lo. Returns
 * CA_ERR_INVALID if the interval is empty or the group order is needed
 * but unknown. */
static inline ca_status ca_resolve_interval(const ca_group *g, const uint64_t *lo, uint64_t *hi)
{
    if (*lo == 0 && *hi == 0) {
        if (g->order == 0) {
            ca_set_error("group order unknown and no interval given");
            return CA_ERR_INVALID;
        }
        *hi = g->order - 1;
        return CA_OK;
    }
    if (*hi < *lo) {
        ca_set_error("empty interval");
        return CA_ERR_INVALID;
    }
    return CA_OK;
}

/* Verify candidate x: x * base == target. */
static inline int ca_verify_log(const ca_group *g, const ca_elem *base, const ca_elem *target,
                                uint64_t x)
{
    ca_elem t;
    ca_group_mul(g, &t, base, x, NULL);
    return ca_group_equal(g, &t, target);
}

/* Reduce x into [lo, hi] modulo n if possible; returns 1 if it fits. */
static inline int ca_fit_interval(uint64_t n, uint64_t *x, uint64_t lo, uint64_t hi)
{
    if (n == 0) return *x >= lo && *x <= hi;
    uint64_t v = *x % n;
    /* smallest v' = v + k n >= lo */
    if (v < lo) {
        uint64_t k = (lo - v + n - 1) / n;
        ca_u128 vv = (ca_u128)v + (ca_u128)k * n;
        if (vv > UINT64_MAX) return 0;
        v = (uint64_t)vv;
    }
    if (v > hi) return 0;
    *x = v;
    return 1;
}

/* Reduce x into [lo, hi] modulo the order of `base`, if possible.
 *
 * ca_fit_interval shifts by multiples of the group order n, but the solutions
 * of x*base == target form a class modulo d = ord(base), and d may properly
 * divide n when base generates a subgroup.  A representative inside [lo, hi]
 * can then exist with no representative modulo n, so the coarse fit has to be
 * retried modulo d before the caller concludes there is none.  ord(base) is
 * only computed on that path, which is the rare one. */
static inline int ca_fit_interval_base(const ca_group *g, const ca_elem *base, uint64_t *x,
                                       uint64_t lo, uint64_t hi)
{
    if (ca_fit_interval(g->order, x, lo, hi)) return 1;
    uint64_t d = ca_group_elem_order(g, base);
    if (d == 0 || d == g->order) return 0;
    return ca_fit_interval(d, x, lo, hi);
}

static inline void ca_stats_begin(ca_stats *st) { (void)st; }

#endif
