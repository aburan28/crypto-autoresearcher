#ifndef ENDPOINT_REUSE_H
#define ENDPOINT_REUSE_H
#include "cryptanalysis/ca_precomp.h"
#ifdef __cplusplus
extern "C" {
#endif
typedef struct er_precomp_table er_precomp_table;
typedef struct er_entry { uint64_t fp, exp; } er_entry;
typedef struct er_rng_counts {uint64_t seed_calls,word_draws,below_calls;} er_rng_counts;
void er_rng_reset(void);
er_rng_counts er_rng_snapshot(void);
/* Events are streamed. kind 1 unmatched DP; 2 chain limit; 3 harvest proposal;
 * 4 commit-ready; 6 verified solution; 7 lookup; 8 lookup witness. Proposals are not activated until solve succeeds.
 * pending_slot identifies the corresponding kind-1 event within one target. */
typedef struct er_event {
 uint64_t kind, attempt, fp, a, pending_slot, exponent, accepted, known, pending;
 ca_elem point;
} er_event;
typedef int (*er_emit_fn)(void *, const er_event *);
typedef struct er_reuse_stats {
 uint64_t unmatched_dp, chain_limit_restarts, staged, capacity_rejections;
 uint64_t exact_exponent_comparisons, scalar_addmods, sort_comparisons;
 uint64_t bucket_candidates_verified, rejected_bucket_witnesses;
 uint64_t proposed, inserted, duplicates, fingerprint_aliases, rolled_back;
 uint64_t known_before, known_after, pending_peak, capacity;
} er_reuse_stats;
typedef struct er_fill_stats {
 uint64_t seed,starts,max_starts,terminals,chain_limit_restarts,duplicates,inserted;
 uint64_t reported_group_ops,known_before,known_after,capacity;
 er_reuse_stats work;
} er_fill_stats;
ca_status er_precompute_fill(er_precomp_table *,uint64_t max_total_ops,uint64_t prior_ops,er_fill_stats *);
typedef struct er_memory {
 uint64_t known, endpoint_capacity, endpoint_allocated_bytes;
 uint64_t fixed_base_bytes, adding_points_bytes, adding_scalars_bytes, object_bytes;
 uint64_t build_worker_entry_capacity, build_worker_entry_bytes;
 uint64_t build_live_array_bytes, build_control_bytes;
} er_memory;
ca_status er_precomp_table_new(const ca_group *,const ca_elem *,const ca_precomp_params *,er_precomp_table **,ca_stats *);
void er_precomp_table_free(er_precomp_table *);
ca_status er_recycle_configure(er_precomp_table *,uint64_t capacity,int enabled);
ca_status er_recycle_solve(er_precomp_table *,const ca_elem *,uint64_t *,ca_stats *,er_reuse_stats *,er_emit_fn,void *);
uint64_t er_recycle_entries(const er_precomp_table *,er_entry *,uint64_t);
void er_recycle_memory(const er_precomp_table *,const ca_stats *,er_memory *);
uint64_t er_static_entries(const ca_precomp_table *,er_entry *,uint64_t);
void er_static_memory(const ca_precomp_table *,const ca_stats *,uint64_t,er_memory *);
ca_status er_static_reserve(ca_precomp_table *,uint64_t);
int er_static_entry_at(const ca_precomp_table *,uint64_t,er_entry *);
int er_recycle_entry_at(const er_precomp_table *,uint64_t,er_entry *);
#ifdef ER_DEVELOPMENT_API
int er_rng_development_check(void);
ca_status er_test_stage(er_precomp_table *,const ca_elem *,uint64_t);
ca_status er_test_commit(er_precomp_table *,const ca_elem *,uint64_t,er_reuse_stats *);
ca_status er_test_replace(er_precomp_table *,const er_entry *,uint64_t);
#endif
#ifdef __cplusplus
}
#endif
#endif
