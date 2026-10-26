#ifndef ENDPOINT_RNG_INSTRUMENTATION_H
#define ENDPOINT_RNG_INSTRUMENTATION_H
/* Include pinned definitions under private names, then wrap their exact RNG
 * semantics. Vendor bytes remain unchanged. All counters are thread-safe. */
#define ca_rng_seed er_raw_rng_seed
#define ca_rng_next er_raw_rng_next
#define ca_rng_below er_raw_rng_below
#include "vendor/src/ca_internal.h"
#undef ca_rng_seed
#undef ca_rng_next
#undef ca_rng_below
#include <stdatomic.h>
extern _Atomic uint64_t er_rng_seed_counter,er_rng_word_counter,er_rng_below_counter;
static inline void ca_rng_seed(ca_rng*r,uint64_t seed)
{atomic_fetch_add_explicit(&er_rng_seed_counter,1,memory_order_relaxed);er_raw_rng_seed(r,seed);}
static inline uint64_t ca_rng_next(ca_rng*r)
{atomic_fetch_add_explicit(&er_rng_word_counter,1,memory_order_relaxed);return er_raw_rng_next(r);}
static inline uint64_t ca_rng_below(ca_rng*r,uint64_t n)
{
 atomic_fetch_add_explicit(&er_rng_below_counter,1,memory_order_relaxed);
 if(n==0)return ca_rng_next(r);
 ca_u128 m=(ca_u128)ca_rng_next(r)*n;uint64_t l=(uint64_t)m;
 if(l<n){uint64_t t=(0-n)%n;while(l<t){m=(ca_u128)ca_rng_next(r)*n;l=(uint64_t)m;}}
 return (uint64_t)(m>>64);
}
#endif
