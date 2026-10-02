#!/usr/bin/env python3
"""TASK-20260911-e837e1: finite public coefficient rank and retained-cost audit.
No target solving, logarithm solving, new relation collection, or network access.
"""
import collections, hashlib, itertools, json, math, os, pathlib, platform
import resource, signal, statistics, subprocess, sys, time, traceback
from datetime import datetime, timezone

HERE = pathlib.Path(__file__).resolve().parent
PACKAGE = HERE.parent
REPO = PACKAGE.parent.parent
TASK = 'TASK-20260911-e837e1'
PROTOCOL_SHA = '97da73662f6c76fc06591493fb9fdcd7936ab72b3ab47dab00fd2f933d96a8cc'
R = 262543
INPUTS = {}
METRICS = ('query_ms','query_group_additions','query_paid_chunks','query_table_lookups','query_table_probe_steps')


def require(ok, message):
    if not ok: raise AssertionError(message)


def now(): return datetime.now(timezone.utc).isoformat()


def sha(path):
    h = hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()


def bind(path, expected=None):
    path = pathlib.Path(path)
    digest = sha(path)
    require(expected is None or digest == expected, f'input hash mismatch: {path}')
    INPUTS[str(path)] = {'sha256':digest,'bytes':path.stat().st_size}
    return digest


def read_json(path, expected=None):
    bind(path, expected)
    with open(path) as f:return json.load(f)


def write_json(name, value):
    with open(HERE/name,'x') as f:
        json.dump(value,f,indent=2,sort_keys=True,allow_nan=False);f.write('\n')


def emit(f, value): f.write(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n')


def memory_check():
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    rss_bytes = rss if sys.platform == 'darwin' else rss*1024
    if rss_bytes > 2*1024**3: raise MemoryError('observed own-process peak RSS exceeded 2 GiB')
    return rss_bytes


class Curve:
    """Polynomial-bit arithmetic, extended Euclid inversion, binary affine law."""
    def __init__(self):self.n=19;self.poly=(1<<19)|39
    def mul(self,a,b):
        out=0
        while b:
            if b&1:out^=a
            b>>=1;a<<=1
            if a>>19:a^=self.poly
        return out
    def sq(self,a):return self.mul(a,a)
    def inv(self,a):
        require(a!=0,'zero inverse')
        u,v,g,h=a,self.poly,1,0
        while u!=1:
            d=u.bit_length()-v.bit_length()
            if d<0:u,v=v,u;g,h=h,g;d=-d
            u^=v<<d;g^=h<<d
        while g.bit_length()>19:g^=self.poly<<(g.bit_length()-20)
        require(self.mul(a,g)==1,'inverse residual')
        return g
    def div(self,a,b):return self.mul(a,self.inv(b))
    def on(self,p):
        if p is None:return True
        x,y=p
        return 0<=x<1<<19 and 0<=y<1<<19 and self.sq(y)^self.mul(x,y)==self.mul(self.sq(x),x)^self.sq(x)^1
    def neg(self,p):return None if p is None else (p[0],p[0]^p[1])
    def add(self,p,q):
        if p is None:return q
        if q is None:return p
        x,y=p;u,v=q
        if x==u:
            if y!=v or x==0:return None
            s=x^self.div(y,x);z=self.sq(s)^s^1
            return (z,self.sq(x)^self.mul(s^1,z))
        s=self.div(y^v,x^u);z=self.sq(s)^s^x^u^1
        return (z,self.mul(s,x^z)^z^y)
    def scalar(self,p,n):
        q=None
        while n:
            if n&1:q=self.add(q,p)
            p=self.add(p,p);n>>=1
        return q


class Rank:
    """Row echelon rank only: no right-hand side, backsolve or nullspace extraction."""
    def __init__(self,n):self.n=n;self.b={};self.w=[]
    def add(self,row,witness=None):
        require(len(row)==self.n,'row dimension')
        v=[int(x)%R for x in row]
        for p in sorted(self.b):
            if v[p]:
                c=v[p];b=self.b[p];v=[(x-c*y)%R for x,y in zip(v,b)]
        p=next((i for i,x in enumerate(v) if x),None)
        if p is None:return False
        inv=pow(v[p],-1,R);self.b[p]=[(x*inv)%R for x in v]
        self.w.append(witness)
        return True
    def __len__(self):return len(self.b)
    def certificate(self):return {'modulus':R,'columns':self.n,'pivots':[{'column':p,'row':self.b[p]} for p in sorted(self.b)],'increment_witnesses':self.w}


def projective(row):
    v=next((x for x in row if x),None)
    return tuple((x*pow(v,-1,R))%R for x in row) if v else None


def collisions(spec, source, out):
    c=Curve();name=spec['name'];m=read_json(source/spec['manifest'])['base']
    require([m[k] for k in ('n','a','b','group_order','subgroup_order','cofactor')]==[19,1,1,525086,R,2],name+' parameters')
    require(m['field_modulus_low_terms']==[0,1,2,5],name+' polynomial')
    pts=[tuple(p) for p in m['points']];labels=m['point_labels'];reps=[tuple(p) for p in m['representatives']];k=m['orbit_columns']
    require(len(pts)==len(set(pts))==len(labels)==38*k,name+' point counts')
    for i,(p,(col,a)) in enumerate(zip(pts,labels)):
        require(c.on(p) and c.scalar(p,R) is None,name+f' subgroup point {i}')
        require(c.scalar(reps[col],a)==p,name+f' public label {i}')
    badcol,bada=labels[0];corrupted=c.scalar(reps[badcol],(bada+1)%R)
    require(corrupted!=pts[0],name+' corrupted coefficient control')
    buckets=collections.defaultdict(list);vectors={};pair_count=0
    for i in range(len(pts)):
        for j in range(i,len(pts)):
            p=(i,j);g=c.add(pts[i],pts[j]);require(c.on(g),name+' pair sum curve')
            buckets[g].append(p);v=[0]*k
            for ix in p:col,a=labels[ix];v[col]=(v[col]+a)%R
            vectors[p]=tuple(v);pair_count+=1
    require(pair_count==len(pts)*(len(pts)+1)//2,'diagonal-inclusive pair cardinality')
    keys=sorted(buckets,key=lambda x:(-1,-1) if x is None else x)
    rank=Rank(k);anchors=Rank(k);reverse=Rank(k);exact=collections.Counter();proj=collections.Counter()
    nzero=0;count=0;identity_zero=0;rows=[]
    for key in keys:
        pairs=sorted(buckets[key]);anchor=pairs[0]
        require(all((x-x)%R==0 for x in vectors[anchor]),name+' self subtraction')
        for p in pairs[1:]:anchors.add([(x-y)%R for x,y in zip(vectors[p],vectors[anchor])],{'group_sum':key,'pairs':[p,anchor]})
        for p,q in itertools.combinations(pairs,2):
            # Independent equality check via differently associated four-point sum.
            diff=c.add(c.add(pts[p[0]],c.neg(pts[q[0]])),c.add(pts[p[1]],c.neg(pts[q[1]])))
            require(diff is None,name+' four-point equality residual')
            row=tuple((x-y)%R for x,y in zip(vectors[p],vectors[q]));count+=1
            witness={'base':name,'group_sum':key,'pairs':[p,q],'compressed_row':row,'identity_bucket':key is None}
            inc=rank.add(row,{'collision_index':count,'pairs':[p,q],'group_sum':key});witness['rank_increment']=inc
            emit(out,witness);exact[row]+=1;cl=projective(row)
            if cl is None:nzero+=1;identity_zero+=int(key is None)
            else:proj[cl]+=1
            rows.append(row)
    for row in reversed(rows):reverse.add(row)
    # Deliberately change both pair insertion order and operand order.
    replay=collections.defaultdict(list)
    for p in reversed(list(vectors)):
        replay[c.add(pts[p[1]],pts[p[0]])].append(p)
    require({g:sorted(v) for g,v in replay.items()}=={g:sorted(v) for g,v in buckets.items()},name+' reverse insertion')
    require(len(rank)==len(anchors)==len(reverse),name+' full/anchor/reverse rank')
    self_rank=Rank(k)
    for g in keys:self_rank.add([0]*k)
    require(len(self_rank)==0,name+' self rank')
    nonid=[x for x in keys if x is not None];require(len(nonid)>1,'slot control requires distinct sums')
    alias=[nonid[0],nonid[1]];require(alias[0]!=alias[1],'one-slot exact mismatch control')
    ident=len(buckets.get(None,[]));hist=collections.Counter(map(len,buckets.values()))
    result={'base':name,'status':'completed_valid','manifest':spec['manifest'],'point_count':len(pts),'orbit_columns':k,'pair_count_including_diagonal':pair_count,'diagonal_pairs':len(pts),'distinct_group_sums':len(buckets),'sum_bucket_multiplicity_histogram':dict(sorted(hist.items())),'raw_equal_sum_collisions':count,'identity_bucket_entries':ident,'identity_bucket_collisions':ident*(ident-1)//2,'identity_bucket_zero_rows':identity_zero,'nonidentity_equal_sum_collisions':count-ident*(ident-1)//2,'zero_rows':nzero,'distinct_exact_rows_including_zero':len(exact),'exact_duplicate_rows':count-len(exact),'distinct_nonzero_projective_classes':len(proj),'projective_duplicate_nonzero_rows':sum(proj.values())-len(proj),'compressed_rank':len(rank),'anchor_difference_rank':len(anchors),'reversed_row_rank':len(reverse),'rank_certificate':rank.certificate(),'anchor_rank_certificate':anchors.certificate(),'controls':{'public_point_labels_checked':len(pts),'subgroup_points_checked':len(pts),'corrupted_label_rejected':True,'corrupted_label_witness':{'point_index':0,'column':badcol,'original_coefficient':bada,'corrupted_coefficient':(bada+1)%R,'expected_point':pts[0],'corrupted_public_multiple':corrupted},'self_subtractions_checked':len(keys),'self_subtraction_rank':len(self_rank),'one_slot_alias_control':{'hash_slots':1,'slot_collision_count':1,'exact_equal_relations':0,'group_sums':alias},'reverse_pair_insertion_same_buckets':True,'independent_review':'pending after Coordinator snapshot'},'row_class_counts':{'exact':[{'row':v,'count':n} for v,n in sorted(exact.items())],'nonzero_projective':[{'row':v,'count':n} for v,n in sorted(proj.items())]}}
    memory_check();print(json.dumps({'stage':'collision','base':name,'collisions':count,'rank':len(rank)}),flush=True)
    return result


def close(a,b):return math.isclose(float(a),float(b),rel_tol=1e-9,abs_tol=1e-8)


def totals():return {k:0.0 if k=='query_ms' else 0 for k in METRICS}


def cost_audit(protocol,source,out):
    summaries=[];rows=[];process_count=0;receipt_count=0;pair_keys={}
    for run_spec in protocol['source']['receipt_sets']:
        run=source/run_spec['path'];mf=read_json(run/'artifacts/final_manifest.json')
        def get_json(relative):return read_json(run/relative,mf['files'][relative])
        code_rel='inputs/harness/frozen/koblitz_rank_fixture.rs'
        bind(run/code_rel,mf['files'][code_rel])
        text=(run/code_rel).read_text()
        require('self.insertion_collisions += probes - 1' in text,'source hash displacement definition')
        require('accepted >= full_at + 32' in text,'source rank+32 definition')
        for block in range(run_spec['blocks']):
            for arm in run_spec['arms']:
                context=f"{run_spec['name']}/block_{block:02d}/{arm}"
                rel=f'artifacts/measurements/block_{block:02d}/{arm}'
                observation=get_json(rel+'/observation.json');pr=get_json(rel+'/process.receipt.json')
                require(pr['exit_code']==0 and not pr['watchdog_timeout'],context+' source process')
                require(observation['measurement_status']=='COMPLETE_VALID',context+' source observation')
                path=run/(rel+'/process.stdout.log');h=hashlib.sha256();size=0;states={};setup=None;batch=None;line_no=0
                with open(path,'rb') as f:
                    for line in f:
                        h.update(line);size+=len(line);line_no+=1;o=json.loads(line);kind=o.get('kind')
                        if kind=='point_defined_factor_base':
                            require(setup is None,context+' duplicate setup')
                            setup={k:v for k,v in o.items() if k.endswith('_ms') or k in ('kind','base_hash','factor_base_points','orbit_columns','n','a','pair_group_additions','support_table_insertion_collisions','support_table_insertion_probe_steps')}
                        elif kind=='relation_rank_receipt':
                            idx=int(o['public_corpus_batch_index']);v=o['sparse_row']
                            if idx not in states:states[idx]={'rank':Rank(len(v)),'count':0,'last_trial':0,'sums':totals(),'first_full':None,'rank_plus_32':None,'rank_basis_receipts':[]}
                            s=states[idx];s['count']+=1;trial=int(o['trial']);accepted=int(o['accepted_relation'])
                            require(accepted==s['count'],context+' receipt accepted order')
                            require(trial==s['last_trial']+1,context+' unretained intervening query would invalidate prefix')
                            require(len(v)==s['rank'].n and all(isinstance(x,int) and 0<=x<R for x in v),context+' row dimensions/residues')
                            if len(s['rank'])<s['rank'].n:
                                if s['rank'].add(v,{'source_line':line_no,'accepted_relation':accepted,'trial':trial}):
                                    s['rank_basis_receipts'].append({'source_line':line_no,'accepted_relation':accepted,'trial':trial,'row':v})
                            require(len(s['rank'])==int(o['rank_after']),context+' rank mismatch')
                            for metric in METRICS:
                                val=o[metric];require(isinstance(val,(float,int)) and math.isfinite(val) and val>=0,context+' invalid '+metric);s['sums'][metric]+=val
                            s['last_trial']=trial;receipt_count+=1
                            milestone={'trial':trial,'accepted_relations':accepted,'rank':len(s['rank']),'query_prefix':dict(s['sums']),'classification':'measured_query_prefix'}
                            if len(s['rank'])==s['rank'].n and s['first_full'] is None:s['first_full']=milestone
                            if s['first_full'] and s['rank_plus_32'] is None and accepted>=s['first_full']['accepted_relations']+32:s['rank_plus_32']=milestone
                            if receipt_count%8192==0:memory_check()
                        elif kind=='relation_rank_summary':
                            idx=int(o['public_corpus_batch_index']);s=states[idx]
                            require('summary' not in s,context+' repeated corpus summary')
                            require(s['count']==run_spec['relations_per_corpus']==o['admitted_relations'],context+' corpus count')
                            require(s['rank'].n==o['matrix_columns'],context+' matrix columns')
                            require(s['first_full'] is not None and s['rank_plus_32'] is not None,context+' missing milestone')
                            require(s['first_full']['accepted_relations']==o['full_rank_at_relation'],context+' source first full rank')
                            require(s['rank_plus_32']['trial']==o['rank_plus_32_at_trial'],context+' source rank+32')
                            fieldmap={'query_ms':o['timing_breakdown_ms']['query'],'query_paid_chunks':o['query_paid_chunks_total']}
                            for metric in METRICS:
                                expected=fieldmap[metric] if metric in fieldmap else o[metric]
                                require(close(s['sums'][metric],expected),context+' corpus total '+metric)
                            # Explicit allowlist excludes fixture secrets and all solved values.
                            safe=['full_rank_at_relation','rank_plus_32_at_trial','matrix_columns','public_corpus_hash','public_corpus_batch_file_sha256','public_corpus_batch_index','admitted_relations','timing_breakdown_ms','collection_ms','fixture_setup_ms','fixture_generation_ms','fixture_public_corpus_import_validation_ms','fixture_receipt_construction_evidence_ms','linear_solve_ms','solution_validation_ms','reference_validation_ms','charged_total_ms','primary_charged_total_ms','fixture_online_charged_ms']
                            s['summary']={k:o.get(k) for k in safe}
                        elif kind=='retained_support_batch_summary':
                            require(batch is None,context+' repeated batch')
                            batch={k:v for k,v in o.items() if k.endswith('_ms') or k in ('total_admitted_relations','total_target_trials','public_corpus_batch_count','public_corpus_batch_total_targets','query_paid_chunks_total','query_group_additions','query_table_lookups','query_table_probe_steps','public_corpus_batch_payload_hashes','public_corpus_batch_file_sha256s')}
                        else:raise AssertionError(context+' unexpected record kind '+str(kind))
                digest=h.hexdigest();require(digest==mf['files'][rel+'/process.stdout.log']==pr['stdout_sha256'],context+' stdout hash')
                INPUTS[str(path)]={'sha256':digest,'bytes':size}
                require(setup is not None and batch is not None and len(states)==4,context+' setup/batch/corpus completeness')
                require(sorted(states)==list(range(4)),context+' corpus indices')
                require(sum(s['count'] for s in states.values())==batch['total_admitted_relations']==32768,context+' batch count')
                for metric in METRICS:
                    got=sum(s['sums'][metric] for s in states.values())
                    expected=observation['query_timer_total_ms'] if metric=='query_ms' else batch['query_paid_chunks_total'] if metric=='query_paid_chunks' else batch[metric]
                    require(close(got,expected),context+' process total '+metric)
                require(close(batch['support_setup_without_corpus_custody_ms'],observation['support_setup_without_corpus_custody_ms']),context+' support setup agreement')
                setup_once=setup['curve_setup_ms']+batch['support_setup_without_corpus_custody_ms']
                setup_components={'classification':'measured_source_setup','curve_setup_ms':setup['curve_setup_ms'],'support_setup_without_corpus_custody_ms':batch['support_setup_without_corpus_custody_ms'],'single_instance_setup_ms':setup_once,'support_setup_including_all_four_corpora_import_ms':batch['support_setup_ms'],'component_diagnostics':setup,'diagnostic_additivity':'component diagnostics can overlap support setup; add only curve_setup_ms and support_setup_without_corpus_custody_ms','retained_amortized_allocation':{'classification':'accounting_allocation_of_measured_total','formula':'single_instance_setup_ms / denominator; not a measured prefix','per_source_corpus_ms':setup_once/4,'source_corpora_denominator':4,'per_retained_relation_query_ms':setup_once/32768,'source_relation_queries_denominator':32768}}
                process_safe={'source_set':run_spec['name'],'block':block,'arm':arm,'classification':'source_measured_full_process','stdout_sha256':digest,'source_process_receipt_sha256':INPUTS[str(run/(rel+'/process.receipt.json'))]['sha256'],'wall_ms':pr['wall_ms'],'child_peak_rss_bytes':pr.get('child_peak_rss_bytes'),'child_user_seconds':pr.get('child_user_seconds'),'child_system_seconds':pr.get('child_system_seconds'),'setup':setup_components,'source_full_batch':batch,'source_observation_accounting':{k:v for k,v in observation.items() if k.endswith('_ms') or k in ('targets','corpora','support_table_builds','support_table_insertion_collisions','support_table_insertion_probe_steps','pair_group_additions','pair_table_entries_including_identity')}}
                summaries.append(process_safe)
                for idx in sorted(states):
                    s=states[idx];q=s['summary'];pairkey=(run_spec['name'],block,idx)
                    signature=(q['public_corpus_hash'],q['public_corpus_batch_file_sha256'])
                    if pairkey in pair_keys:require(pair_keys[pairkey]==signature,context+' source pairing mismatch')
                    else:pair_keys[pairkey]=signature
                    row={'source_set':run_spec['name'],'block':block,'arm':arm,'corpus_index':idx,'status':'completed_valid','source_stdout':str(path),'source_stdout_sha256':digest,'public_corpus_hash':q['public_corpus_hash'],'public_corpus_file_sha256':q['public_corpus_batch_file_sha256'],'matrix_columns':s['rank'].n,'retained_relations':s['count'],'independent_rank':len(s['rank']),'rank_basis_receipts':s['rank_basis_receipts'],'rank_certificate':s['rank'].certificate(),'full_stream_query_totals':s['sums'],'source_corpus_full_scope_measurements':q,'setup':setup_components,'milestones':{}}
                    for label in ('first_full','rank_plus_32'):
                        ms=s[label]
                        row['milestones'][label]={**ms,'setup_plus_query_partial_ms':setup_once+ms['query_prefix']['query_ms'],'setup_plus_query_classification':'partial_measured_components','complete_instance_total_ms':None,'complete_instance_total_classification':'unavailable','missing_exact_prefix_timers':['target/preparation work','packed group identity verification','rank diagnostics','linear solve','solution validation','reference validation','receipt construction and serialization','corpus custody for exact prefix','outer prefix wall time'],'source_aggregate_timers_not_prorated':True}
                    emit(out,row);rows.append(row)
                process_count+=1;memory_check();print(json.dumps({'stage':'cost','processes':process_count,'context':context,'receipts':receipt_count}),flush=True)
    require(process_count==72 and len(rows)==288 and receipt_count==2359296,'frozen total coverage')
    descriptive=[]
    for source_set in protocol['source']['receipt_sets']:
        for arm in source_set['arms']:
            selected=[x for x in rows if x['source_set']==source_set['name'] and x['arm']==arm]
            summary={'source_set':source_set['name'],'arm':arm,'corpora':len(selected),'classification':'descriptive_existing_source_only','milestones':{}}
            for mile in ('first_full','rank_plus_32'):
                summary['milestones'][mile]={}
                for metric in ('trial','accepted_relations','setup_plus_query_partial_ms'):
                    vals=[x['milestones'][mile][metric] for x in selected]
                    summary['milestones'][mile][metric]={'minimum':min(vals),'median':statistics.median(vals),'maximum':max(vals)}
                vals=[x['milestones'][mile]['query_prefix']['query_ms'] for x in selected]
                summary['milestones'][mile]['query_ms']={'minimum':min(vals),'median':statistics.median(vals),'maximum':max(vals)}
            descriptive.append(summary)
    return {'status':'completed_valid','processes':process_count,'corpora':len(rows),'retained_relation_receipts':receipt_count,'source_processes':summaries,'descriptive_by_source_set_and_arm':descriptive,'paired_corpus_identity_checks':len(pair_keys),'pairing_scope':'Arms share each (source_set, block, corpus_index) only. Source campaigns remain separate.','complete_instance_totals_available':0,'hash_table_insertion_collisions_definition':'sum(probes - 1), physical hash displacement; not equal group-sum multiplicity','rank_plus_32_definition':'accepted_relations >= actual_first_full_rank_accepted_relations + 32','linear_solves_performed':0,'new_relation_queries_performed':0}


def git_state(path):
    def call(*args):
        p=subprocess.run(['git','-C',str(path),*args],capture_output=True,text=True,check=True)
        return p.stdout.strip()
    return {'root':str(path),'commit':call('rev-parse','HEAD'),'branch':call('rev-parse','--abbrev-ref','HEAD'),'dirty_porcelain':call('status','--porcelain=v1','--untracked-files=normal')}


def report(results):
    lines=[f'# Execution report: {TASK}','',f"Status: `{results['status']}`. Protocol SHA-256 `{PROTOCOL_SHA}`.",'',
           'Finite observations only. Parameters are n=19, a=b=1, binary modulus x^19+x^5+x^2+x+1, subgroup order 262543. All four bases and both existing source campaigns were frozen before this audit. No logarithms or linear systems were solved and no new relation queries were collected.','']
    if results.get('error'):lines += ['Execution error: '+results['error'],'']
    if results.get('collisions'):
        lines += ['| Base | Points | Pairs with diagonals | Equal-sum collisions | Identity collisions | Zero rows | Compressed rank | Anchor rank |','|---|---:|---:|---:|---:|---:|---:|---:|']
        for x in results['collisions']:
            lines.append(f"| {x['base']} | {x['point_count']} | {x['pair_count_including_diagonal']} | {x['raw_equal_sum_collisions']} | {x['identity_bucket_collisions']} | {x['zero_rows']} | {x['compressed_rank']} | {x['anchor_difference_rank']} |")
        lines += ['', 'Every public coefficient label was checked by multiplying its declared public representative. Each pair collision retained its pair indices, exact group sum and compressed row in collision_witnesses.jsonl. A differently associated four-point sum checked each equality. Canonical pivot certificates and rank-increment witnesses are in results.json. Corrupted-label, zero self-subtraction, one-slot hash alias, reverse insertion and reverse row-order checks completed. This producer replay is distinct from the required independent review after snapshot.','']
    if results.get('cost'):
        cost=results['cost'];lines += [f"Cost coverage: {cost['processes']} existing processes, {cost['corpora']} source corpora, {cost['retained_relation_receipts']} streamed relation receipts. Every actual first-full-column-rank milestone and original rank+32 milestone agrees with its source summary; query totals agree at corpus and process scope.",'',
        '| Existing source set | Arm | Full-rank accepted count min/median/max | First-rank query ms min/median/max | Setup + first-rank query partial ms min/median/max |','|---|---|---|---|---|']
        def triple(x):return f"{x['minimum']:.6g} / {x['median']:.6g} / {x['maximum']:.6g}"
        for x in cost['descriptive_by_source_set_and_arm']:
            m=x['milestones']['first_full'];lines.append(f"| {x['source_set']} | {x['arm']} | {triple(m['accepted_relations'])} | {triple(m['query_ms'])} | {triple(m['setup_plus_query_partial_ms'])} |")
        lines += ['', 'All 576 milestone complete-instance totals are **unavailable (`null`)**. The measured setup plus query prefix is a partial sum: full curve setup and full one-time support setup without corpus custody, each charged once, plus exactly the retained per-relation query timers through the endpoint. Exact prefix timers for preparation, rank, group/solution/reference validation, linear solve, custody, receipt/serialization and outer wall time are unavailable. Source aggregate timers were never proportionally scaled into measured prefix timers.','',
        'Source full-process wall times and full-batch algorithm, corpus import/custody, receipt-construction, rank-diagnostics, solve-evidence and validation timers are retained separately. Component diagnostic timers can overlap the support-setup timer and are not added twice. Retained amortized allocations show the measured setup divided by four source corpora or 32768 retained relation queries; these are labeled accounting allocations rather than measured prefix costs. No cost is claimed to disappear from deployment.','',
        'Comparisons are descriptive within each existing shared source set/block/corpus. The balanced-fresh and two-swap-fresh campaigns are not spliced into a four-arm paired experiment. Production insertion_collisions sums probes minus one, so it records hash displacement rather than equal group values.','']
    lines += ['Protocol deviations: none in the frozen scientific case set. Darwin memory protection uses cooperative own-process peak-RSS checks at bounded streaming checkpoints (every 8192 receipts) and collision boundaries, with no unsupported claim of a hard address-space or external RSS enforcement. The 1800-second SIGALRM watchdog is process-liveness protection.','',
    f'Output root: `{HERE}`. Exact command, input hashes, source and implementation revisions, dirty state, environment and own-process resource measurements are retained in receipt.json. Independent review and official research status decisions belong to the Coordinator after snapshot.','']
    with open(HERE/'report.md','x') as f:f.write('\n'.join(lines))


def main():
    expected_outputs=('results.json','collision_witnesses.jsonl','cost_prefixes.jsonl','receipt.json','stdout.log','stderr.log','report.md')
    require(not any((HERE/x).exists() for x in expected_outputs),'immutable audit output already exists; refuse overwrite/rerun')
    initial=git_state(REPO);source_repo=pathlib.Path('/Volumes/SSD990/crypto-hybrid-rank-wt');source_state=git_state(source_repo)
    start=now();wall=time.monotonic();before=resource.getrusage(resource.RUSAGE_SELF)
    receipt={'task_id':TASK,'started_at':start,'output_root':str(HERE),'command':[sys.executable,*sys.argv],'cwd':os.getcwd(),'protocol_sha256':PROTOCOL_SHA,'implementation_sha256':sha(__file__),'implementation_git':initial,'source_git':source_state,'environment':{'python':sys.version,'python_executable':sys.executable,'platform':platform.platform(),'machine':platform.machine(),'dependencies':'Python standard library only'},'randomness':{'new_random_seeds':[],'policy':'deterministic enumeration and frozen source corpus ordering'},'inference':{'requested_policy':'executor-implementation','runtime':'native Codex','resolved_model_id':None,'model_verified':False,'fallback_used':False,'degraded_requirements':[],'provenance_note':'Exact resolved model identifier not exposed; null is intentional'},'resource_protection':{'watchdog_seconds':1800,'memory_limit_bytes':2147483648,'memory_method':'cooperative resource.getrusage(RUSAGE_SELF).ru_maxrss guard every 8192 streamed receipts and collision case boundary; not a hard instantaneous RSS cap','external_rss_monitor_used':False,'network_requests':0},'protocol_deviations':[],'independent_review_completed':False}
    results={'task_id':TASK,'protocol_sha256':PROTOCOL_SHA,'status':'running','collisions':[],'cost':None,'claim_scope':'finite public mathematical observations and existing-source timing accounting only'}
    oldout,olderr=sys.stdout,sys.stderr
    stdout=open(HERE/'stdout.log','x');stderr=open(HERE/'stderr.log','x');sys.stdout,sys.stderr=stdout,stderr
    def alarm(*_):raise TimeoutError('1800-second process-liveness watchdog expired')
    signal.signal(signal.SIGALRM,alarm);signal.alarm(1800)
    status='failed_implementation';exitcode=1
    try:
        p=read_json(PACKAGE/'protocol.json',PROTOCOL_SHA)
        handoff=read_json(PACKAGE/'handoffs/collision_cost.json')['handoff']
        require(handoff['id']==TASK and handoff['protocol_sha256']==PROTOCOL_SHA,'handoff binding')
        require(p['approved_by']=='DEC-20260911-b38a50' and p['status']=='frozen','protocol approval')
        bind(PACKAGE/'approval.md');bindings=read_json(PACKAGE/'source_bindings.json');archive=read_json(PACKAGE/'archive_audit.json')
        plan=read_json(PACKAGE/'dispatch_plan.json');require(all(plan['gates'].values()),'dispatch gate')
        require(any(x['id']==TASK for x in plan['dispatches']),'task not dispatched')
        require(archive['all_hashes_match'] and not bindings['balanced_source_archive']['mismatches'],'archive gates')
        source=source_repo/p['source']['evidence_root']
        for pin in p['source']['pins']:bind(source/pin['path'],pin['sha256'])
        for run in p['source']['receipt_sets']:
            matches=[x for x in archive['runs'] if x['run']==str(source/run['path'])]
            expect=matches[0]['manifest_sha256'] if matches else bindings['balanced_source_archive']['final_manifest_sha256']
            bind(source/run['path']/'artifacts/final_manifest.json',expect)
        print(json.dumps({'stage':'start','task':TASK,'source_hash_gate':True}),flush=True)
        with open(HERE/'collision_witnesses.jsonl','x') as witnesses:
            for spec in p['parameters']['bases']:results['collisions'].append(collisions(spec,source,witnesses))
        with open(HERE/'cost_prefixes.jsonl','x') as costs:results['cost']=cost_audit(p,source,costs)
        status='completed_valid';exitcode=0
    except (TimeoutError,MemoryError) as e:
        status='resource_exhaustion';results['error']=str(e);traceback.print_exc()
    except (OSError,FileNotFoundError) as e:
        status='failed_infrastructure';results['error']=str(e);traceback.print_exc()
    except Exception as e:
        status='completed_invalid' if isinstance(e,AssertionError) else 'failed_implementation';results['error']=str(e);traceback.print_exc()
    finally:
        signal.alarm(0);results['status']=status
        print(json.dumps({'stage':'terminal','status':status,'error':results.get('error')}),flush=True)
        write_json('results.json',results);report(results)
        stdout.flush();stderr.flush();sys.stdout,sys.stderr=oldout,olderr;stdout.close();stderr.close()
        after=resource.getrusage(resource.RUSAGE_SELF)
        receipt.update({'status':status,'exit_code':exitcode,'completed_at':now(),'wall_seconds':time.monotonic()-wall,'user_seconds':after.ru_utime-before.ru_utime,'system_seconds':after.ru_stime-before.ru_stime,'peak_rss_bytes':after.ru_maxrss if sys.platform=='darwin' else after.ru_maxrss*1024,'input_files':INPUTS,'implementation_git_after':git_state(REPO),'resources_scope':'this audit process only; source process resources are separate','output_hashes':{x:sha(HERE/x) for x in expected_outputs if x!='receipt.json' and (HERE/x).exists()},'required_outputs_present':{x:(HERE/x).exists() for x in expected_outputs if x!='receipt.json'},'error':results.get('error')})
        write_json('receipt.json',receipt)
    print(json.dumps({'task':TASK,'status':status,'output_root':str(HERE),'wall_seconds':receipt['wall_seconds']}),flush=True)
    return exitcode


if __name__=='__main__':sys.exit(main())
