/* Dedicated known-scalar fill; no target or hidden labels are consumed. */
ca_status er_precompute_fill(ca_precomp_table *t,uint64_t max_total_ops,
                             uint64_t prior_ops,er_fill_stats *s)
{
 if(!t||!s||t->recycle_enabled||t->recycle_pending)return CA_ERR_INVALID;
 memset(s,0,sizeof(*s));s->known_before=t->nent;s->known_after=t->nent;s->capacity=t->recycle_capacity;
 s->seed=t->seed^UINT64_C(0x65722d66696c6c31);s->work.capacity=t->recycle_capacity;
 s->work.known_before=t->nent;s->work.known_after=t->nent;
 if(max_total_ops>UINT64_MAX-t->recycle_capacity-64)return CA_ERR_INVALID;
 s->max_starts=max_total_ops+t->recycle_capacity+64;
 uint64_t used=prior_ops;ca_status rc=CA_OK;ca_rng rng;ca_rng_seed(&rng,s->seed);
 if(max_total_ops&&used>max_total_ops){rc=CA_ERR_LIMIT;goto finish_fill;}
 while(t->nent<t->recycle_capacity){
  if(s->starts>=s->max_starts){rc=CA_ERR_LIMIT;break;}
  s->starts++;uint64_t a=ca_rng_below(&rng,t->n),steps=0;
  unsigned pop=(unsigned)__builtin_popcountll(a);uint64_t needed=pop?(uint64_t)pop-1:0;
  if(UINT64_MAX-used<needed||(max_total_ops&&needed>max_total_ops-used)){rc=CA_ERR_LIMIT;break;}
  ca_elem Y;uint64_t actual=0;pc_base_mul(t,&Y,a,&actual);
  if(actual!=needed){rc=CA_ERR_INTERNAL;break;}
  used+=actual;s->reported_group_ops+=actual;
  for(;;){
   uint64_t h=ca_group_hash(t->g,&Y);
   if((h&t->dp_mask)==0){
    s->terminals++;int duplicate=0;
    for(size_t j=0;j<t->nent;j++){
     s->work.exact_exponent_comparisons++;
     if(t->ent[j].exp==a){duplicate=1;break;}
     if(t->ent[j].fp==h)s->work.fingerprint_aliases++;
    }
    if(duplicate)s->duplicates++;
    else{t->ent[t->nent++]=(pc_entry){h,a};s->inserted++;}
    break;
   }
   if(steps>=t->chain_limit){s->chain_limit_restarts++;break;}
   if(used==UINT64_MAX||(max_total_ops&&used>=max_total_ops)){rc=CA_ERR_LIMIT;goto finish_fill;}
   uint32_t idx=(uint32_t)(ca_mix64(h)%t->r);
   ca_group_op(t->g,&Y,&Y,&t->S[idx]);a=ca_addmod(a,t->s[idx],t->n);
   s->work.scalar_addmods++;used++;s->reported_group_ops++;steps++;
  }
 }
finish_fill:
 if(t->nent>s->known_before)er_heap_sort(t->ent,t->nent,&s->work);
 t->chains=t->nent;s->known_after=t->nent;s->work.known_after=t->nent;
 s->work.inserted=s->inserted;s->work.duplicates=s->duplicates;
 return rc;
}
