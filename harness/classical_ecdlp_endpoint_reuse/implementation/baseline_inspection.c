/* Pinned baseline source is textually included unchanged. Helpers inspect or
 * reserve storage only; they do not change a walk, RNG, endpoint or lookup. */
#include "candidate/endpoint_reuse.h"
#include "vendor/src/precomp.c"
ca_status er_static_reserve(ca_precomp_table *t,uint64_t capacity)
{
 if(!t||capacity<t->nent||capacity>SIZE_MAX/sizeof(pc_entry)||!capacity)return CA_ERR_INVALID;
 pc_entry *p=realloc(t->ent,(size_t)capacity*sizeof(pc_entry));if(!p)return CA_ERR_NOMEM;
 t->ent=p;return CA_OK;
}
uint64_t er_static_entries(const ca_precomp_table *t,er_entry *out,uint64_t capacity)
{
 if(out&&capacity>=t->nent)for(size_t i=0;i<t->nent;i++)out[i]=(er_entry){t->ent[i].fp,t->ent[i].exp};
 return t->nent;
}
int er_static_entry_at(const ca_precomp_table *t,uint64_t i,er_entry *e)
{if(i>=t->nent||!e)return 0;*e=(er_entry){t->ent[i].fp,t->ent[i].exp};return 1;}
void er_static_memory(const ca_precomp_table *t,const ca_stats *build,uint64_t capacity,er_memory *m)
{
 memset(m,0,sizeof(*m));if(!t)return;
 m->known=t->nent;m->endpoint_capacity=capacity;m->endpoint_allocated_bytes=capacity*sizeof(pc_entry);
 m->fixed_base_bytes=(uint64_t)t->bitlen*sizeof(ca_elem);m->adding_points_bytes=(uint64_t)t->r*sizeof(ca_elem);
 m->adding_scalars_bytes=(uint64_t)t->r*sizeof(uint64_t);m->object_bytes=sizeof(*t);
 uint64_t raw=build?build->iterations:0,worker=raw?1024:0;while(worker<raw)worker*=2;
 m->build_worker_entry_capacity=worker;m->build_worker_entry_bytes=worker*sizeof(pc_entry);
 m->build_live_array_bytes=(uint64_t)t->walks*(3*sizeof(ca_elem)+5*sizeof(uint64_t)+1);
 m->build_control_bytes=sizeof(pc_worker)+sizeof(pthread_t)+sizeof(uint8_t);
}
