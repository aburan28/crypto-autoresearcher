/*
 * ca_precomp.h - discrete logarithms with precomputation (Bernstein-Lange
 * "free precomputation").
 *
 * A one-time, group- and base-specific precomputation builds a table of
 * distinguished-point chains.  Every subsequent logarithm to the same base
 * is then solved online in far fewer operations than a from-scratch square
 * root search: with a distinguished-point probability of 2^{-t} and
 * t = round(log2(n)/3),
 *
 *     table size            ~ n^{1/3} chains
 *     precomputation        ~ n^{2/3} group operations
 *     per-target online     ~ n^{1/3} group operations
 *
 * This is a time/precomputation trade-off, not a break: it does not lower
 * the *total* cost of a single isolated logarithm below the sqrt(n) of
 * Pollard rho (the precomputation alone is n^{2/3}).  Its point is that the
 * n^{2/3} is paid once and then amortised over many targets in a fixed
 * group -- the "non-uniform" setting in which the sqrt(n) security of a
 * standardised curve is not the whole story.
 *
 * The walk is a function of the current point only, adding one of r
 * precomputed steps s_i * base.  Precomputation walks start at a_0 * base
 * (a known multiple of base) and store (endpoint, a_0 + accumulated).  An
 * online walk starts at a * base + target and follows the same walk; if it
 * lands on a stored endpoint e * base then e == a' + x (mod ord(base)) and
 * x = e - a' is recovered.  Every recovered x is verified before it is
 * returned, so a 64-bit endpoint-hash collision can only cost a retry, never
 * a wrong answer.
 *
 * Implementation: walk starts use a fixed-base table for `base` (cheaper than
 * generic double-and-add); the precomputation walks W chains at once through
 * one batched field inversion (ca_group_batch_op, a large win on curves) and
 * runs across `threads` workers; an optional Bloom filter aborts a chain the
 * moment it re-enters already-covered ground (paying off when the table is
 * built to over-cover the group); and the table is a sorted array of
 * (fingerprint, exponent) pairs looked up by binary search.
 *
 * References:
 *   D. J. Bernstein, T. Lange, "Computing small discrete logarithms
 *     faster", INDOCRYPT 2012 (measured 1.77 n^{1/3} online, table n^{1/3},
 *     1.24 n^{2/3} precomputation for a whole group of order n).
 *   D. J. Bernstein, T. Lange, "Non-uniform cracks in the concrete: the
 *     power of free precomputation", ASIACRYPT 2013.
 */
#ifndef CA_PRECOMP_H
#define CA_PRECOMP_H

#include "ca_group.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct ca_precomp_params {
    uint32_t r;               /* number of walk steps; 0 => auto (20) */
    int32_t dp_bits;          /* distinguished-point bits t; < 0 => round(log2(n)/3) */
    uint64_t table_size;      /* number of chains to build; 0 => auto (coverage * n / 2^{2t}) */
    double coverage;          /* precomputation coverage factor; 0 => 1.0 */
    uint64_t chain_limit;     /* abandon a chain after this many steps; 0 => auto (~20 * 2^t) */
    uint64_t max_precomp_ops; /* abort building after this many group ops; 0 => none */
    uint64_t max_online_ops;  /* abort a single solve after this many group ops; 0 => none */
    uint32_t threads;         /* build worker threads; 0 => 1 */
    uint32_t walks;           /* build batch width per thread (batched inversion); 0 => auto */
    int32_t early_abort;      /* Bloom early-abort of merging chains: -1 auto, 0 off, 1 on */
    int32_t reserved;         /* keep the struct 8-byte aligned; unused */
    uint64_t seed;            /* 0 => random */
} ca_precomp_params;

CA_API void ca_precomp_params_default(ca_precomp_params *p);

/* Opaque, reusable precomputation table tied to one (group, base). */
typedef struct ca_precomp_table ca_precomp_table;

/* Build the table for logarithms to `base` in `g` (requires g->order != 0).
 * The precomputation cost is added to *st when st != NULL. */
CA_API ca_status ca_precomp_table_new(const ca_group *g, const ca_elem *base,
                                      const ca_precomp_params *params, ca_precomp_table **out,
                                      ca_stats *st);
/* Persist in-progress endpoints and the completed reusable table at checkpoint_path.
 * A matching checkpoint is resumed automatically.  Progress is written to
 * checkpoint_path.progress.json and, when verbose, to stderr.  A NULL path
 * enables live stderr progress without durable state. */
CA_API ca_status ca_precomp_table_new_checkpointed(const ca_group *g, const ca_elem *base,
                                      const ca_precomp_params *params, const char *checkpoint_path,
                                      uint32_t progress_every, uint32_t checkpoint_every,
                                      int verbose, ca_precomp_table **out, ca_stats *st);
CA_API void ca_precomp_table_free(ca_precomp_table *t);

/* Solve x * base == target for x in [0, order).  Online cost only, added to
 * *st when st != NULL.  Returns CA_ERR_NOT_FOUND if the attempt budget is
 * exhausted (e.g. the table is too small or target is not in <base>). */
CA_API ca_status ca_precomp_table_solve(const ca_precomp_table *t, const ca_elem *target,
                                        uint64_t *x, ca_stats *st);
/* Resume the online walk with a completed table.  The checkpoint is tied to
 * the target and table; it is separate from the reusable table artifact.  A
 * NULL path enables live stderr progress without durable state. */
CA_API ca_status ca_precomp_table_solve_checkpointed(const ca_precomp_table *t,
                                        const ca_elem *target, const char *checkpoint_path,
                                        uint32_t progress_every, uint32_t checkpoint_every,
                                        int verbose, uint64_t *x, ca_stats *st);

/* Introspection, for reporting.  Any out pointer may be NULL. */
CA_API void ca_precomp_table_info(const ca_precomp_table *t, int32_t *dp_bits, uint64_t *chains,
                                  uint32_t *r, uint64_t *precomp_ops);

/* One-shot: build a table, solve one target, free the table.  The combined
 * precomputation + online cost goes into *st. */
CA_API ca_status ca_precomp_solve(const ca_group *g, const ca_elem *base, const ca_elem *target,
                                  const ca_precomp_params *params, uint64_t *x, ca_stats *st);

#ifdef __cplusplus
}
#endif
#endif /* CA_PRECOMP_H */
