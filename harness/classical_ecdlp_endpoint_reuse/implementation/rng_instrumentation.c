#include "candidate/endpoint_reuse.h"
#include "rng_instrumentation.h"
_Atomic uint64_t er_rng_seed_counter=0,er_rng_word_counter=0,er_rng_below_counter=0;
void er_rng_reset(void){atomic_store(&er_rng_seed_counter,0);atomic_store(&er_rng_word_counter,0);atomic_store(&er_rng_below_counter,0);}
er_rng_counts er_rng_snapshot(void){er_rng_counts c={atomic_load(&er_rng_seed_counter),atomic_load(&er_rng_word_counter),atomic_load(&er_rng_below_counter)};return c;}
#ifdef ER_DEVELOPMENT_API
int er_rng_development_check(void)
{
 ca_rng a,b;er_raw_rng_seed(&a,0x192837465U);ca_rng_seed(&b,0x192837465U);
 const uint64_t bounds[]={0,1,2,3,181,13121,UINT64_MAX,UINT64_C(9223372036854775809)};
 for(unsigned j=0;j<sizeof(bounds)/sizeof(bounds[0]);j++)for(unsigned k=0;k<128;k++)
  if(er_raw_rng_below(&a,bounds[j])!=ca_rng_below(&b,bounds[j]))return 0;
 return memcmp(&a,&b,sizeof(a))==0;
}
#endif
