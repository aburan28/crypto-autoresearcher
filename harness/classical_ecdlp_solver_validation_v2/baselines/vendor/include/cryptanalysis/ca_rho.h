/*
 * ca_rho.h - Pollard rho with r-adding walks, distinguished points and
 * van Oorschot-Wiener parallel collision search.
 *
 * Solves x * base == target in a cyclic group of known order n.  For best
 * results n should be prime (use Pohlig-Hellman first otherwise); the
 * solver still works for composite n as long as the collision equation is
 * solvable, and falls back to verifying all candidate solutions.
 *
 * Elliptic curve groups additionally use the negation map (walk on
 * {P, -P} classes, expected speed-up sqrt(2)) with fruitless-cycle
 * handling (2-cycle look-ahead + windowed cycle detection with escape by
 * doubling), following Bernstein-Lange-Schwabe.
 */
#ifndef CA_RHO_H
#define CA_RHO_H

#include "ca_group.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct ca_rho_params {
    uint32_t threads;          /* worker threads, 0 => 1 */
    uint32_t r;                /* adding-walk multipliers, 0 => auto (32 / 1024 with negation) */
    int32_t dp_bits;           /* distinguished-point bits, -1 => auto, clamped to 58 */
    uint32_t walks_per_thread; /* simultaneous walks per thread (batched inversion), 0 => auto */
    int      negation_map;     /* 1 to use the negation map when the group supports it */
    uint64_t seed;             /* 0 => random */
    uint64_t max_ops;          /* abort with CA_ERR_LIMIT after this many group ops (0 = none) */
    uint64_t max_table_entries;/* abort when the DP table grows beyond this (0 = none) */
} ca_rho_params;

CA_API void ca_rho_params_default(ca_rho_params *p);

CA_API ca_status ca_rho_solve(const ca_group *g, const ca_elem *base, const ca_elem *target,
                              const ca_rho_params *params, uint64_t *x, ca_stats *st);

/* Preserve the distinguished-point table between runs.  A resumed run keeps
 * the same walk multipliers and starts fresh lanes against the saved table.
 * NULL checkpoint_path enables live progress without persistence.  Intervals
 * are seconds; zero selects defaults (5 for progress, 60 for checkpoint). */
CA_API ca_status ca_rho_solve_checkpointed(const ca_group *g, const ca_elem *base,
                                           const ca_elem *target, const ca_rho_params *params,
                                           const char *checkpoint_path, uint32_t progress_interval,
                                           uint32_t checkpoint_interval, int verbose,
                                           uint64_t *x, ca_stats *st);

#ifdef __cplusplus
}
#endif
#endif /* CA_RHO_H */
