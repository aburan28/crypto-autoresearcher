#!/usr/bin/env python3
"""J1 programmatic audit of the EXP-ECDLP-869870 run set (read-only)."""
import json, os, glob, math, yaml, hashlib, sys
import numpy as np
base='experiments/EXP-ECDLP-869870/runs/'
runs=sorted(glob.glob(base+'RUN-*'))
def get(d,path):
    for p in path.split('.'):
        if not isinstance(d,dict) or p not in d: return None
        d=d[p]
    return d
out={'runs':{},'deep':{}}
for r in runs:
    rid=os.path.basename(r); m=yaml.safe_load(open(r+'/manifest.yaml'))['run']
    files=sorted(os.listdir(r))
    keys=list(m.keys())
    rec={'status':m.get('status'),'kind':m.get('kind'),'files':files,'top_keys':keys,
         'commit':get(m,'code.commit'),'dirty':get(m,'code.dirty'),'command':(get(m,'code.command') or get(m,'command') or '')[:80],
         'policy':get(m,'inference.requested_policy'),'model':get(m,'inference.resolved_model_id'),'fallback':get(m,'inference.fallback_used'),
         'seeds':get(m,'inputs.seeds') or get(m,'seeds'),'wall':get(m,'timing.wall_seconds') or get(m,'resources.wall_seconds') or get(m,'wall_seconds'),
         'rss':get(m,'resources.peak_rss_bytes') or get(m,'peak_rss_bytes'),'started':get(m,'timing.started_at') or get(m,'started_at'),'finished':get(m,'timing.finished_at') or get(m,'finished_at'),
         'cert':get(m,'result.certificate.kind') or get(m,'certificate.kind'),'failure_class':m.get('failure_class'),'env_python':get(m,'environment.python_version') or get(m,'environment.python')}
    pins=get(m,'code.source_sha256') or {}; mism=[]
    for f,h in pins.items():
        p='experiments/EXP-ECDLP-869870/source/'+f
        if os.path.exists(p) and hashlib.sha256(open(p,'rb').read()).hexdigest()!=h: mism.append(f)
    rec['pin_mismatch']=mism
    out['runs'][rid]=rec
    if 'summary.json' in files and rec['kind'] in ('generic_exact','curve_exact'):
        S=json.load(open(r+'/summary.json')); R=json.load(open(r+'/raw-result.json'))
        d={'issues':[],'cells':{}}
        N=S['header']['N']; T=S['header']['T']
        for ck,cell in S['cells'].items():
            rc=R['cells'][ck]; c={}
            # global share from top1000
            top=np.array(rc['basin_multiset_8W']['top1000']); c['global_share_from_top1000']=float(top[:T].sum()/N); c['global_share_reported']=cell['global_oracle']['top_T_share_8W']
            if abs(c['global_share_from_top1000']-c['global_share_reported'])>1e-12: d['issues'].append(f'{ck}: global share mismatch')
            c['global_share_topT2']=float(top[:T//2].sum()/N)
            c['ratio_to_cmax']=cell['global_oracle']['ratio_to_c_max_contract']; c['slope']=cell['basin_law']['survival_slope_8W']; c['cutoff']=cell['basin_law']['cutoff_n_c_theta2_over_2_8W']
            c['cycle_mass_frac']=cell['cycle_mass_frac']; c['capped_8W_frac']=cell['capped_mass_8W_frac']
            # per r: re-add pool basins for generated oracle and published weight
            c['rules']={}
            for rk,rule in cell['rules'].items():
                pool=rc['pools_by_r'][rk]; dp=np.array(pool['dp']); h=np.array(pool['h']); Sx=np.array(pool['S']); b=np.array(pool['basin_8W'])
                W=cell['params']['W']
                go=float(np.sort(b)[::-1][:T].sum()/N)
                w=Sx+4*W*h; order=np.argsort(-w,kind='stable'); pw=float(b[order[:T]].sum()/N)
                pub=rule['tables']['published_weight']['coverage_exact_8W']; gor=rule['tables']['generated_oracle']['coverage_exact_8W']
                ties=int((np.sort(w)[::-1][T-1]==w).sum())>1
                c['rules'][rk]={'gen_oracle_readd':go,'gen_oracle_reported':gor,'pub_readd_notie':pw,'pub_reported':pub,'tie_at_boundary':ties,
                                'unselected':rule['tables']['unselected']['coverage_exact_8W'],'relab_pub':rule['nulls']['published_weight']['relabelled_coverage_8W'],
                                'relab_minus_unsel':rule['nulls']['published_weight']['relabelled_minus_unselected'],'sigma_mono':rule['nulls']['published_weight']['sigma_monotone_nonincreasing'],
                                'sigma_curve':[round(x,4) for x in rule['nulls']['published_weight']['sigma_coverage_8W']],
                                'P_scaled':rule['P_scaled_sqrtNT'],'walks':rule['walks'],'pool_size':rule['pool_size'],
                                'max_cov_any_table':max(t['coverage_exact_8W'] for t in rule['tables'].values()),'any_exceed':any(t['exceeds_global_oracle_8W'] for t in rule['tables'].values()),
                                'sampled_inside_wilson_all':all(t['exact_inside_wilson'] for t in rule['tables'].values())}
                if abs(go-gor)>1e-12: d['issues'].append(f'{ck} r={rk}: generated oracle re-add mismatch {go} vs {gor}')
                if abs(pw-pub)>1e-12 and not ties: d['issues'].append(f'{ck} r={rk}: published-weight re-add mismatch {pw} vs {pub}')
                if c['rules'][rk]['max_cov_any_table']>c['global_share_reported']+1e-12: d['issues'].append(f'{ck} r={rk}: EXCEEDANCE')
                # pool h,S consistency with P: sum S over pool + capped charge <= P
                if int(Sx.sum())>rule['P_group_ops']: d['issues'].append(f'{ck} r={rk}: sum S > P')
                c['rules'][rk]['sumS']=int(Sx.sum()); c['rules'][rk]['sumh']=int(h.sum()); c['rules'][rk]['P']=rule['P_group_ops']
            c['fixture']={rk:{'cost':v['scaled_cost_sampled_this_seed'],'pub':v['published_scaled_cost'],'P':v['scaled_precomp_measured'],'pubP':v['published_scaled_precomp'],'hits':v['hits'],'steps':v['total_steps']} for rk,v in cell['fixture'].items()}
            # online walks: recompute sampled hit for published weight r=2 from raw terminals? need table identity: use tables_sha256 only. Skip.
            if 'certificates' in rc: c['certificates']=rc['certificates'] if not isinstance(rc['certificates'],list) else {'n':len(rc['certificates'])}
            d['cells'][ck]=c
        d['invalidity']=S['header'].get('invalidity')
        out['deep'][rid]=d
json.dump(out,open(sys.argv[1],'w'),indent=1,default=str)
for rid,rec in out['runs'].items():
    print(rid,rec['status'],rec['kind'],'dirty',rec['dirty'],'model',rec['model'],'fb',rec['fallback'],'wall',rec['wall'],'rss',rec['rss'],'cert',rec['cert'],'seeds',rec['seeds'],'pin',rec['pin_mismatch'],'files',len(rec['files']),'top_keys',rec['top_keys'])
for rid,d in out['deep'].items():
    print('==',rid,'issues',d['issues'],'invalidity',d['invalidity'])
    for ck,c in d['cells'].items():
        print('  ',ck,'share',round(c['global_share_reported'],4),'readd',round(c['global_share_from_top1000'],4),'topT/2',round(c['global_share_topT2'],4),'ratio',round(c['ratio_to_cmax'],3),'slope',round(c['slope'],3),'cut',round(c['cutoff'],3) if c['cutoff'] else None,'cyc',round(c['cycle_mass_frac'],4),'cap',round(c['capped_8W_frac'],5))
        for rk,r in c['rules'].items():
            print('     r',rk,'pub',round(r['pub_reported'],4),'readd',round(r['pub_readd_notie'],4),'tie',r['tie_at_boundary'],'genor',round(r['gen_oracle_reported'],4),'unsel',round(r['unselected'],4),'relab-unsel',round(r['relab_minus_unsel'],4),'sig_mono',r['sigma_mono'],'maxcov',round(r['max_cov_any_table'],4),'exceed',r['any_exceed'],'wilson_ok',r['sampled_inside_wilson_all'],'Pscaled',round(r['P_scaled'],3))
        print('     fixture',c['fixture'])
