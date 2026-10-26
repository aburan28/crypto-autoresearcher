#!/usr/bin/env python3
"""Derive the independent recycling fork; never edit pinned vendor bytes."""
from pathlib import Path
root=Path(__file__).resolve().parent
text=(root/'vendor/src/precomp.c').read_text()
prefix='''/* Independent endpoint-recycling fork. See derive_candidate.py and vendor-source.json. */
#include "endpoint_reuse.h"
#define ca_precomp_table er_precomp_table
#define ca_precomp_params_default er_precomp_params_default
#define ca_precomp_table_new er_precomp_table_new
#define ca_precomp_table_new_checkpointed er_precomp_table_new_checkpointed
#define ca_precomp_table_free er_precomp_table_free
#define ca_precomp_table_solve er_precomp_table_solve
#define ca_precomp_table_solve_checkpointed er_precomp_table_solve_checkpointed
#define ca_precomp_table_info er_precomp_table_info
#define ca_precomp_solve er_precomp_solve
'''
def replace(a,b):
 global text
 assert text.count(a)==1,(text.count(a),a[:80])
 text=text.replace(a,b)
replace('    uint64_t precomp_ops;\n};','''    uint64_t precomp_ops;
    size_t recycle_capacity, recycle_pending;
    int recycle_enabled, recycle_callback_failed;
    er_reuse_stats *reuse_stats;
    er_emit_fn emit;
    void *emit_context;
};''')
helpers=r'''
/* New state is confined to one preallocated endpoint arena. Known entries are
 * ent[0..nent); pending (fp,a) pairs are ent[nent..nent+pending), never looked up.
 * The original builder and its hash-only initial deduplication stay unchanged. */
static int er_emit_event(ca_precomp_table *t, er_event *event)
{
    event->known = t->nent; event->pending = t->recycle_pending;
    if (t->emit && !t->emit(t->emit_context, event)) {
        t->recycle_callback_failed = 1; return 0;
    }
    return 1;
}
static int er_capture(ca_precomp_table *t,const ca_elem *point,uint64_t a,
                      uint64_t attempt,int dp,uint64_t fp)
{
    er_reuse_stats *s=t->reuse_stats;
    if (!t->recycle_enabled) return 1;
    er_event event={0}; event.kind=dp?1:2; event.attempt=attempt;
    event.point=*point; event.a=a; event.fp=fp;
    event.pending_slot=UINT64_MAX;
    if (dp) {
        s->unmatched_dp++;
        if (t->nent+t->recycle_pending<t->recycle_capacity) {
            event.pending_slot=t->nent+t->recycle_pending;
            t->ent[event.pending_slot]=(pc_entry){event.fp,a};
            t->recycle_pending++; s->staged++;
            if (t->recycle_pending>s->pending_peak) s->pending_peak=t->recycle_pending;
        } else s->capacity_rejections++;
    } else s->chain_limit_restarts++;
    return er_emit_event(t,&event);
}
static size_t er_bucket_begin(ca_precomp_table *t,uint64_t fp)
{
    size_t lo=0,hi=t->nent;
    while(lo<hi){size_t mid=lo+(hi-lo)/2;
        if(t->ent[mid].fp<fp)lo=mid+1;else hi=mid;}
    return lo;
}
/* Only the enabled candidate scans aliases. Disabled execution retains the
 * original one-fingerprint lookup and therefore the original arithmetic path. */
static int er_try_bucket(ca_precomp_table *t,uint64_t fp,uint64_t a,
                         const ca_elem *target,uint64_t *x,uint64_t attempt)
{
    er_event lookup={0};lookup.kind=7;lookup.attempt=attempt;lookup.fp=fp;lookup.a=a;
    if(!er_emit_event(t,&lookup))return -1;
    for(size_t j=er_bucket_begin(t,fp);j<t->nent&&t->ent[j].fp==fp;j++){
        uint64_t candidate=ca_submod(t->ent[j].exp,a,t->n);
        t->reuse_stats->bucket_candidates_verified++;
        int verified=ca_verify_log(t->g,&t->base,target,candidate);
        er_event witness={0};witness.kind=8;witness.attempt=attempt;witness.fp=fp;
        witness.a=a;witness.exponent=t->ent[j].exp;witness.pending_slot=j;witness.accepted=verified;
        if(!er_emit_event(t,&witness))return -1;
        if(verified){*x=candidate;return 1;}
        t->reuse_stats->rejected_bucket_witnesses++;
    }
    return 0;
}
static int er_entry_less(pc_entry a,pc_entry b,er_reuse_stats *s)
{ s->sort_comparisons++;return a.fp<b.fp||(a.fp==b.fp&&a.exp<b.exp); }
static void er_swap(pc_entry *a,pc_entry *b)
{ pc_entry z=*a;*a=*b;*b=z; }
static void er_sift(pc_entry *a,size_t count,size_t pos,er_reuse_stats *s)
{
    for(;;){size_t child=pos*2+1;if(child>=count)return;
        if(child+1<count&&er_entry_less(a[child],a[child+1],s))child++;
        if(!er_entry_less(a[pos],a[child],s))return;
        er_swap(a+pos,a+child);pos=child;}
}
/* In-place heapsort: no library-sort heap allocation or hidden endpoint pool. */
static void er_heap_sort(pc_entry *a,size_t count,er_reuse_stats *s)
{
    for(size_t i=count/2;i>0;i--)er_sift(a,count,i-1,s);
    for(size_t i=count;i>1;i--){er_swap(a,a+i-1);er_sift(a,i-1,0,s);}
}
static ca_status er_activate(ca_precomp_table *t,uint64_t x)
{
    er_reuse_stats *s=t->reuse_stats;size_t old=t->nent,accepted=0;
    for(size_t i=0;i<t->recycle_pending;i++){
        pc_entry v=t->ent[old+i];v.exp=ca_addmod(x,v.exp,t->n);s->scalar_addmods++;
        int duplicate=0;
        /* Exact point identity: eP=e'P iff e=e' modulo prime order n. */
        for(size_t j=0;j<old+accepted;j++){
            s->exact_exponent_comparisons++;
            if(t->ent[j].exp==v.exp){duplicate=1;break;}
            if(t->ent[j].fp==v.fp)s->fingerprint_aliases++;
        }
        er_event event={0};event.kind=3;event.fp=v.fp;event.exponent=v.exp;
        event.pending_slot=old+i;event.accepted=!duplicate;s->proposed++;
        if(!er_emit_event(t,&event))return CA_ERR_INTERNAL;
        if(duplicate)s->duplicates++;else t->ent[old+accepted++]=v;
    }
    er_event ready={0};ready.kind=4;ready.accepted=accepted;
    if(!er_emit_event(t,&ready))return CA_ERR_INTERNAL;
    t->nent=old+accepted;t->chains=t->nent;s->inserted=accepted;
    if(accepted){er_heap_sort(t->ent,t->nent,s);}
    t->recycle_pending=0;
    return CA_OK;
}
static void er_discard(ca_precomp_table *t)
{
    if(t->reuse_stats)t->reuse_stats->rolled_back+=t->recycle_pending;
    t->recycle_pending=0;
}
'''
replace('/* ---- precomputation (threaded, batched) ------------------------------- */',helpers+'\n/* ---- precomputation (threaded, batched) ------------------------------- */')
old='''                uint64_t e;
                if (pc_lookup(t, h, &e)) {
                    uint64_t cand = ca_submod(e % n, a % n, n); /* x = e - a' (mod n) */
                    if (ca_verify_log(g, &t->base, target, cand)) {
                        *x = cand;
                        rc = CA_OK;
                    }
                }
                active = 0;
                break;
            }
            if (steps >= t->chain_limit) { active = 0; break; }'''
new='''                if (t->recycle_enabled) {
                    int hit=er_try_bucket((ca_precomp_table *)t,h,a,target,x,attempts);
                    if(hit<0){rc=CA_ERR_INTERNAL;goto online_done;}
                    if(hit)rc=CA_OK;
                    if(rc!=CA_OK&&!er_capture((ca_precomp_table *)t,&Y,a,attempts,1,h)){
                        rc=CA_ERR_INTERNAL;goto online_done;
                    }
                } else {
                    uint64_t e;
                    if (pc_lookup(t, h, &e)) {
                        uint64_t cand = ca_submod(e % n, a % n, n); /* x = e - a' (mod n) */
                        if (ca_verify_log(g, &t->base, target, cand)) {
                            *x = cand;
                            rc = CA_OK;
                        }
                    }
                }
                active = 0;
                break;
            }
            if (steps >= t->chain_limit) {
                if(t->recycle_enabled&&!er_capture((ca_precomp_table *)t,&Y,a,attempts,0,h)){
                    rc=CA_ERR_INTERNAL;goto online_done;
                }
                active=0;break;
            }'''
replace(old,new)
# Checkpoint layout is not extended. Refuse it instead of silently dropping state.
replace('''    if (!progress_every || !checkpoint_every) {
        ca_set_error("precomp progress and checkpoint intervals must be positive");''','''    (void)g;(void)base;(void)params;(void)checkpoint_path;(void)progress_every;
    (void)checkpoint_every;(void)verbose;(void)out;(void)st;
    ca_set_error("endpoint reuse candidate does not support checkpointing");
    return CA_ERR_INVALID;
    if (!progress_every || !checkpoint_every) {
        ca_set_error("precomp progress and checkpoint intervals must be positive");''')
# pc_table_solve is the old internal entry point; the exported wrapper alone
# attaches per-target state and activates pending data after verified success.
suffix=r'''
ca_status er_recycle_configure(ca_precomp_table *t,uint64_t capacity,int enabled)
{
    if(!t||capacity<t->nent||capacity>SIZE_MAX/sizeof(pc_entry)||capacity==0)return CA_ERR_INVALID;
    if(t->walks!=1)return CA_ERR_INVALID;
    pc_entry *entries=realloc(t->ent,(size_t)capacity*sizeof(pc_entry));
    if(!entries)return CA_ERR_NOMEM;
    t->ent=entries;t->recycle_capacity=(size_t)capacity;t->recycle_pending=0;
    t->recycle_enabled=enabled!=0;return CA_OK;
}
ca_status er_recycle_solve(ca_precomp_table *t,const ca_elem *target,uint64_t *x,
                          ca_stats *st,er_reuse_stats *s,er_emit_fn emit,void *context)
{
    if(!t||!s||!target||!x)return CA_ERR_INVALID;
    memset(s,0,sizeof(*s));s->known_before=t->nent;s->capacity=t->recycle_capacity;
    t->reuse_stats=s;t->emit=emit;t->emit_context=context;t->recycle_callback_failed=0;
    t->recycle_pending=0;
    ca_status rc=pc_table_solve(t,target,NULL,0,0,0,x,st);
    if(t->recycle_enabled){
        if(rc==CA_OK){
            er_event verified={0};verified.kind=6;verified.exponent=*x;verified.point=*target;
            if(!er_emit_event(t,&verified))rc=CA_ERR_INTERNAL;
            else rc=er_activate(t,*x);
        }
        if(rc!=CA_OK)er_discard(t);
    }
    s->known_after=t->nent;t->emit=NULL;t->emit_context=NULL;t->reuse_stats=NULL;
    return rc;
}
uint64_t er_recycle_entries(const ca_precomp_table *t,er_entry *out,uint64_t capacity)
{
    if(out&&capacity>=t->nent)for(size_t i=0;i<t->nent;i++)out[i]=(er_entry){t->ent[i].fp,t->ent[i].exp};
    return t->nent;
}
int er_recycle_entry_at(const ca_precomp_table *t,uint64_t i,er_entry *e)
{if(i>=t->nent||!e)return 0;*e=(er_entry){t->ent[i].fp,t->ent[i].exp};return 1;}
void er_recycle_memory(const ca_precomp_table *t,const ca_stats *build,er_memory *m)
{
    memset(m,0,sizeof(*m));if(!t)return;
    m->known=t->nent;m->endpoint_capacity=t->recycle_capacity;
    m->endpoint_allocated_bytes=t->recycle_capacity*sizeof(pc_entry);
    m->fixed_base_bytes=(uint64_t)t->bitlen*sizeof(ca_elem);
    m->adding_points_bytes=(uint64_t)t->r*sizeof(ca_elem);m->adding_scalars_bytes=(uint64_t)t->r*sizeof(uint64_t);
    m->object_bytes=sizeof(*t);
    uint64_t raw=build?build->iterations:0,worker=raw?1024:0;
    while(worker<raw)worker*=2;
    m->build_worker_entry_capacity=worker;m->build_worker_entry_bytes=worker*sizeof(pc_entry);
    m->build_live_array_bytes=(uint64_t)t->walks*(3*sizeof(ca_elem)+5*sizeof(uint64_t)+1);
    m->build_control_bytes=sizeof(pc_worker)+sizeof(pthread_t)+sizeof(uint8_t);
}
#ifdef ER_DEVELOPMENT_API
ca_status er_test_stage(ca_precomp_table *t,const ca_elem *point,uint64_t a)
{
    if(!t||!point||a>=t->n||t->nent+t->recycle_pending>=t->recycle_capacity)return CA_ERR_LIMIT;
    t->ent[t->nent+t->recycle_pending++]=(pc_entry){ca_group_hash(t->g,point),a};return CA_OK;
}
ca_status er_test_commit(ca_precomp_table *t,const ca_elem *target,uint64_t x,er_reuse_stats *s)
{
    memset(s,0,sizeof(*s));t->reuse_stats=s;s->known_before=t->nent;s->capacity=t->recycle_capacity;
    ca_status rc=CA_OK;
    if(x>=t->n||!ca_verify_log(t->g,&t->base,target,x)){er_discard(t);rc=CA_ERR_INVALID;}
    else rc=er_activate(t,x);
    s->known_after=t->nent;t->reuse_stats=NULL;return rc;
}
ca_status er_test_replace(ca_precomp_table *t,const er_entry *entries,uint64_t count)
{
    if(count>t->recycle_capacity)return CA_ERR_LIMIT;
    for(uint64_t i=0;i<count;i++){if(entries[i].exp>=t->n)return CA_ERR_INVALID;
        t->ent[i]=(pc_entry){entries[i].fp,entries[i].exp};}
    er_reuse_stats ignored={0};er_heap_sort(t->ent,(size_t)count,&ignored);
    t->nent=(size_t)count;t->chains=count;t->recycle_pending=0;return CA_OK;
}
#endif
'''
def replace_function(name,body):
 global text
 start=text.index('ca_status '+name+'(');brace=text.index('{',start);depth=1;end=brace+1
 while depth:
  if text[end]=='{':depth+=1
  elif text[end]=='}':depth-=1
  end+=1
 text=text[:brace]+body+text[end:]
replace_function('ca_precomp_table_new_checkpointed',"""{
 (void)g;(void)base;(void)params;(void)checkpoint_path;(void)progress_every;
 (void)checkpoint_every;(void)verbose;(void)out;(void)st;
 ca_set_error("endpoint reuse candidate does not support checkpointing");
 return CA_ERR_INVALID;
}""")
replace_function('ca_precomp_table_solve_checkpointed',"""{
 (void)t;(void)target;(void)checkpoint_path;(void)progress_every;
 (void)checkpoint_every;(void)verbose;(void)x;(void)st;
 ca_set_error("endpoint reuse candidate does not support checkpointing");
 return CA_ERR_INVALID;
}""")
suffix=suffix.replace('#ifdef ER_DEVELOPMENT_API\nca_status er_test_stage',(root/'candidate/fill_implementation.inc').read_text()+'\n#ifdef ER_DEVELOPMENT_API\nca_status er_test_stage')
(root/'candidate/endpoint_reuse.c').write_text(prefix+text+suffix)
