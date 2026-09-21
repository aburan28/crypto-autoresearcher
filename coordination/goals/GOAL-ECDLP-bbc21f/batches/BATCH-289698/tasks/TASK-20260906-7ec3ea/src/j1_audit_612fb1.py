#!/usr/bin/env python3
"""J1 programmatic audit of the EXP-ECDLP-612fb1 run set (read-only)."""
import json, os, glob, gzip, math, yaml, hashlib, sys
import numpy as np
base='experiments/EXP-ECDLP-612fb1/runs/'
runs=sorted(glob.glob(base+'RUN-*'))
REQ=['code.commit','code.dirty','code.command','inference.requested_policy','inference.resolved_model_id','inference.fallback_used','environment.python_version','environment.dependencies','inputs.seeds','timing.wall_seconds','resources.peak_rss_bytes','status']
def get(d,path):
    for p in path.split('.'):
        if not isinstance(d,dict) or p not in d: return None
        d=d[p]
    return d
out={'runs':{}, 'findings':[]}
man={}
for r in runs:
    rid=os.path.basename(r)
    m=yaml.safe_load(open(r+'/manifest.yaml'))['run']; man[rid]=m
    files=sorted(os.listdir(r))
    missing=[k for k in REQ if get(m,k) is None]
    rec={'status':m.get('status'),'stage':m.get('stage'),'files':files,'missing_manifest_fields':missing,
         'wall':get(m,'timing.wall_seconds'),'rss':get(m,'resources.peak_rss_bytes'),'seeds':get(m,'inputs.seeds'),
         'started':get(m,'timing.started_at'),'finished':get(m,'timing.finished_at'),'commit':get(m,'code.commit'),'dirty':get(m,'code.dirty'),
         'model':get(m,'inference.resolved_model_id'),'policy':get(m,'inference.requested_policy'),'fallback':get(m,'inference.fallback_used'),
         'cert':get(m,'result.certificate.kind'),'valid':get(m,'result.valid'),'failure_class':get(m,'result.failure_class'),
         'has_raw':'raw-result.json' in files,'has_summary':'summary.json' in files,'has_stdout':'stdout.log' in files,'has_stderr':'stderr.log' in files}
    # source hash pins vs current source
    pins=get(m,'code.source_sha256') or {}
    mism=[]
    for f,h in pins.items():
        p='experiments/EXP-ECDLP-612fb1/source/'+f
        if os.path.exists(p) and hashlib.sha256(open(p,'rb').read()).hexdigest()!=h: mism.append(f)
    rec['source_pin_mismatch_vs_snapshot_source']=mism
    out['runs'][rid]=rec
# seeds check per (N,a) generic
cells={}
for rid,rec in out['runs'].items():
    m=man[rid]; prm=get(m,'inputs.parameters') or {}
    if prm.get('kind')=='generic' or (rec['seeds'] and 'walk_key_seed' in rec['seeds'] and prm.get('n_bits')):
        key=(prm.get('n_bits'),prm.get('a')); cells.setdefault(key,[]).append(rec['seeds']['walk_key_seed'])
out['generic_seed_sets']={str(k):sorted(v) for k,v in cells.items()}
# gate order timestamps
t=lambda rid: out['runs'][rid]['finished'] if rid in out['runs'] else None
out['gate_order']={'RUN-012_finished':t('RUN-ECDLP-612fb1-012'),'RUN-013_started':out['runs'].get('RUN-ECDLP-612fb1-013',{}).get('started'),
                   'RUN-011_failed_finished':t('RUN-ECDLP-612fb1-011'),'RUN-010_finished':t('RUN-ECDLP-612fb1-010'),
                   'RUN-022_finished':t('RUN-ECDLP-612fb1-022'),'RUN-023_started':out['runs'].get('RUN-ECDLP-612fb1-023',{}).get('started'),
                   'RUN-037_started':out['runs'].get('RUN-ECDLP-612fb1-037',{}).get('started')}
# per generic run deep checks
deep={}
for rid,rec in out['runs'].items():
    if not rec['has_raw'] or not rec['has_summary'] or 'summary.json' not in rec['files']: continue
    m=man[rid]; prm=get(m,'inputs.parameters') or {}
    if 'arms' not in json.load(open(base+rid+'/summary.json')): continue
    raw=json.load(open(base+rid+'/raw-result.json')); summ=json.load(open(base+rid+'/summary.json')); cost=json.load(open(base+rid+'/cost_table.json'))
    P=raw['params']; N=P['N']; T=P['T']; k=P['k']; cap=P['cap']; be=P['bits_per_table_entry']; bp=P['bits_per_pool_entry']; rc=P['restart_scalar_mult_group_ops']
    d={'N':N,'T':T,'a':P['a'],'seed':P['seeds']['walk_key_seed'],'issues':[]}
    arms=raw['arms']; sarms=summ['arms']
    # raw vs summary and accounting
    for name,A in arms.items():
        S=sarms[name]; wu=np.array(A['walks_used']); sol=np.array(A['solved']); go=np.array(A['group_ops']); spw=A['steps_per_walk']
        # group ops = sum of used walk steps
        go2=np.array([sum(x for x in row if x is not None) for row in spw])
        if not np.array_equal(go,go2): d['issues'].append(f'{name}: group_ops != sum steps_per_walk')
        used2=np.array([sum(1 for x in row if x is not None) for row in spw])
        if not np.array_equal(wu,used2): d['issues'].append(f'{name}: walks_used != count(steps_per_walk)')
        if S['group_ops_total']!=int(go.sum()): d['issues'].append(f'{name}: summary group_ops_total mismatch')
        if S['restarts_total']!=int(wu.sum()): d['issues'].append(f'{name}: restarts_total mismatch')
        if abs(S['restart_group_ops_total']-wu.sum()*rc)>1e-6: d['issues'].append(f'{name}: restart_group_ops != restarts*1.5*log2N')
        if S['solved_total']!=int(sol.sum()): d['issues'].append(f'{name}: solved_total mismatch')
        R=S['config']['R']; U8=8*T; U16=16*T
        for lab,U in (('8T',U8),('16T',U16)):
            if lab not in S['eps_ss'] or U>len(sol): continue
            e=float(sol[U-2*R:U].mean()); 
            if abs(e-S['eps_ss'][lab])>1e-12: d['issues'].append(f'{name}: eps_ss({lab}) mismatch')
        # per-round table from arrays
        for rr in A['rounds']:
            u0,u1=rr['u0'],rr['u1']; hits=int(sol[u0:u1].sum()); walks=int(wu[u0:u1].sum())
            if hits!=rr['hits'] or walks!=rr['walks'] or int(go[u0:u1].sum())!=rr['group_ops']: d['issues'].append(f'{name}: round {rr["round"]} hits/walks/group_ops mismatch'); break
            if rr['restart_group_ops']!=walks*rc: d['issues'].append(f'{name}: round restart ops'); break
            if rr['S_bits']!=rr['table_size']*be: d['issues'].append(f'{name}: S_bits != table_size*bits'); break
            if 'exact_coverage' in rr and 'oracle_share' in rr and rr['exact_coverage']>rr['oracle_share']+1e-12: d['issues'].append(f'{name}: EXACT EXCEEDANCE round {rr["round"]} cov {rr["exact_coverage"]} > share {rr["oracle_share"]}')
        if S['S_peak_bits']!=S['max_pool_entries']*bp: d['issues'].append(f'{name}: S_peak != max_pool*bits_pool')
        if S['S_bits']!=S['config']['t_sel']*be and S['config']['mode']!='rho': d['issues'].append(f'{name}: S_bits != t_sel*bits')
        # cost table consistency
        C=cost['MEASURED'][name]
        if C['walk_group_ops']!=int(go.sum()) or C['restarts']!=int(wu.sum()) or C['S_peak_bits']!=S['S_peak_bits'] or C['reselection_int_ops']!=S['reselection_int_ops_total']: d['issues'].append(f'{name}: cost_table vs summary mismatch')
        if not S['selector_verified_against_numpy']: d['issues'].append(f'{name}: selector not verified')
    # P identical across arms of same r
    Pr={}
    for name,C in cost['MEASURED'].items():
        r=sarms[name]['config']['r']; mode=sarms[name]['config']['mode']
        if mode in ('rho','oracle'): continue
        Pr.setdefault(r,set()).add(C['P_group_ops'])
    d['P_by_r']={str(r):sorted(v) for r,v in Pr.items()}
    if any(len(v)!=1 for v in Pr.values()): d['issues'].append('P differs across arms at same r')
    for r,v in Pr.items():
        if summ['pools'][str(r)]['P_group_ops'] not in v: d['issues'].append('P vs pools mismatch')
    # round-0 identity and NULL-B/PHI(0) hashes vs STATIC
    def th(name): return arms[name].get('table_hash_per_round') or [r['table_hash'] for r in arms[name]['rounds']]
    for name,A in arms.items():
        tw=A['config']['twin']
        if tw:
            if th(name)[0]!=th(tw)[0]: d['issues'].append(f'{name}: round-0 table hash != twin {tw}')
            r0=A['rounds'][0]; t0=arms[tw]['rounds'][0]
            if (r0['hits'],r0['walks'],r0['group_ops'])!=(t0['hits'],t0['walks'],t0['group_ops']): d['issues'].append(f'{name}: round-0 counts != twin')
    for name in ('NULL-B(T)','NULL-B(T/2)','PHI(0.0,T/2)'):
        if name not in arms: continue
        tw=arms[name]['config']['twin']
        if th(name)!=th(tw) or arms[name]['solved']!=arms[tw]['solved'] or arms[name]['hit_entry']!=arms[tw]['hit_entry'] or arms[name]['group_ops']!=arms[tw]['group_ops']: d['issues'].append(f'{name}: NOT bit-identical to {tw}')
    if 'PHI(1.0,T/2)' in arms and (arms['PHI(1.0,T/2)']['solved']!=arms['RESEL-L(T/2)']['solved'] or th('PHI(1.0,T/2)')!=th('RESEL-L(T/2)')): d['issues'].append('PHI(1) != RESEL-L(T/2)')
    # NULL-B pool bookkeeping ran? pool_size_after grows
    d['NULLB_pool_grew']=(arms['NULL-B(T/2)']['rounds'][-1]['pool_size_after']>arms['NULL-B(T/2)']['rounds'][0]['pool_size']) if 'NULL-B(T/2)' in arms else None
    d['STATIC_pool_static']=arms['STATIC(T/2)']['rounds'][-1]['pool_size_after']==arms['STATIC(T/2)']['rounds'][0]['pool_size']
    # NULL-A gain at 8T and S1 diff from raw
    def eps(name,U,R=None):
        R=R or sarms[name]['config']['R']; s=np.array(arms[name]['solved']); return float(s[U-2*R:U].mean())
    d['eps_ss_8T']={n:eps(n,8*T) for n in ('STATIC(T)','STATIC(T/2)','RESEL-L(T/2)','RESEL-L(T)','NULL-A(T)','NULL-A(T/2)','RESEL-U(T/2)','RHO','STATIC2T') if n in arms}
    d['S1_diff_8T']=d['eps_ss_8T']['RESEL-L(T/2)']-d['eps_ss_8T']['STATIC(T)']
    d['NULLA_gain_8T']={k2:d['eps_ss_8T'][n]-d['eps_ss_8T'][t2] for k2,n,t2 in (('T','NULL-A(T)','STATIC(T)'),('T/2','NULL-A(T/2)','STATIC(T/2)')) if n in arms}
    d['PHI_gain_8T']={p:eps(f'PHI({p},T/2)',8*T)-d['eps_ss_8T']['STATIC(T/2)'] for p in ('0.0','0.1','0.25','0.5','1.0') if f'PHI({p},T/2)' in arms}
    # LOWER admission: credited walks in pool snapshots vs count of used non-capped walks of solved targets (2^24)
    if 'heur_blt7_regression' in summ:
        pw=summ['pools']['2']['walks']-summ['pools']['2']['capped_walks']
        chk={}
        for an in ('RESEL-L(T)','RESEL-L(T/2)'):
            A=arms[an]; sol=np.array(A['solved']); spw=A['steps_per_walk']
            for U,rec in summ['heur_blt7_regression'][an].items():
                U=int(U); cnt=0
                for u in range(U):
                    if sol[u]:
                        cnt+=sum(1 for x in spw[u] if x is not None and x<cap)  # non-capped used walks (length<cap; a DP exactly at cap is counted as capped here: tiny undercount possible)
                chk[f'{an}@{U}']={'credited_walks_reported':rec['measured_slope_credited_walks/N']*N,'precomp_walks_noncapped':pw,'solved_used_noncapped_walks':cnt,'expected':pw+cnt}
        d['lower_admission_check']=chk
    # basin histogram top-T_sel shares vs summary
    if 'basins' in summ:
        h=json.load(gzip.open(base+rid+'/basin_histogram.json.gz','rt'))
        sz=np.repeat(np.array(h['histogram']['size']),np.array(h['histogram']['count'])); srt=np.sort(sz)[::-1]
        d['hist_top_shares']={t:float(srt[:t].sum()/N) for t in (T//4,T//2,3*T//4,T,2*T)}
        d['summary_top_shares']=summ['basins']['top_share_by_t']
        if any(abs(d['hist_top_shares'][t]-summ['basins']['top_share_by_t'][str(t)])>1e-12 for t in d['hist_top_shares']): d['issues'].append('histogram top shares != summary')
        d['G1']={k:summ['basins'].get(k) for k in ('survival_slope','survival_slope_int_grid','top_T_share','C_max_model','top_T_share_over_C_max','largest_basin_in_band','cycle_mass','capped_mass')}
        d['G1']['cutoff']=summ['basins']['cutoff'].get('n_c_theta2_over_2')
        d['static_T_exact_cov_fixture']=summ.get('fixture',{}).get('static_T_exact_coverage')
        # max exact coverage over all tables vs top share of that size
        mx=-1
        for name,S in sarms.items():
            for rr in S['rounds']:
                if 'exact_coverage' in rr: mx=max(mx, rr['exact_coverage']-d['hist_top_shares'].get(rr['table_size'],1.0))
        d['max_exact_cov_minus_topshare_all_tables']=mx
    d['fixture']=({k:summ['fixture'].get(k) for k in ('scaled_main_cost','scaled_precomputation','hit_rate','mean_steps_over_W','capped_fraction')} if 'fixture' in summ else {})
    d['pools']=summ['pools']; d['walker_vs_exact']=summ.get('walker_vs_exact_basins_agree'); d['checks']=summ.get('checks',{}).get('exceedance',{}).get('RESEL-L(T)')
    deep[rid]=d
out['deep']=deep
json.dump(out,open(sys.argv[1],'w'),indent=1,default=str)
# concise print
for rid,rec in out['runs'].items():
    print(rid, rec['status'], 'stage',rec['stage'], 'miss',rec['missing_manifest_fields'], 'wall',rec['wall'],'rss',rec['rss'],'dirty',rec['dirty'],'model',rec['model'],'fb',rec['fallback'],'cert',rec['cert'],'pin_mismatch',rec['source_pin_mismatch_vs_snapshot_source'])
print('seed sets',out['generic_seed_sets']); print('gate order',out['gate_order'])
for rid,d in deep.items():
    print(rid, f"N=2^{int(math.log2(d['N']))} a={d['a']} s={d['seed']} issues={d['issues']} P_by_r={d['P_by_r']} S1={d['S1_diff_8T']:.4f} NULLA={ {k:round(v,4) for k,v in d['NULLA_gain_8T'].items()} } PHI={ {k:round(v,4) for k,v in d['PHI_gain_8T'].items()} } fix={d['fixture'].get('scaled_main_cost')} fixP={d['fixture'].get('scaled_precomputation')} NULLB_pool_grew={d['NULLB_pool_grew']} walker_ok={d['walker_vs_exact']}")
    if 'G1' in d: print('   G1',{k:(round(v,4) if isinstance(v,float) else v) for k,v in d['G1'].items()}, 'hist_topT',round(d['hist_top_shares'][d['T']],4),'topT/2',round(d['hist_top_shares'][d['T']//2],4),'maxcov-share',round(d['max_exact_cov_minus_topshare_all_tables'],4),'staticT_cov',d['static_T_exact_cov_fixture'])
    if 'lower_admission_check' in d: print('   LOWER', {k:(round(v['credited_walks_reported'],1),v['expected']) for k,v in d['lower_admission_check'].items()})
