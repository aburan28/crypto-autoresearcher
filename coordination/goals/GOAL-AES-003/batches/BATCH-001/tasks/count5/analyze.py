import json,collections,os
D=os.path.dirname(os.path.abspath(__file__))
recs=[json.loads(l) for l in open(D+'/raw.jsonl')]
pre={'control_r2_j0eq0':0,'aes_r4':0}
out={'utc_generated':__import__('time').strftime('%Y-%m-%dT%H:%M:%SZ',__import__('time').gmtime()),
     'halt_boundary_utc':'2026-08-02T05:43:57Z','master_seed':'20260802','runs':len(recs),
     'derived_predictions':{'n_r1':36028794871480320,'n_r2_j0eq0':0,'n_r2_j0ne0':9223372034707292160,
       'n_r3':36028794871480320,'n_r4':0,'n_r5_mod8':0,'n_r6':'not forced'},
     'per_arm_round':[]}
g=collections.OrderedDict()
for r in recs: g.setdefault((r['arm'],r['r']),[]).append(r)
for (arm,r),v in g.items():
    void=[x for x in v if x['overflow'] or not x['agree'] or x['N']!=4294967296]
    e={'arm':arm,'r':r,'trials':len(v),'n_values':[x['n'] for x in v],
       'residue_mod8':[x['n_mod8'] for x in v],'residue_mod16':[x['n_mod16'] for x in v],
       'residue_mod8_histogram_0to7':[sum(1 for x in v if x['n_mod8']==i) for i in range(8)],
       'max_occupancy':[x['max_occ'] for x in v],'N':[x['N'] for x in v],
       'identity_check_all_ok':all(x['agree'] for x in v),
       'overflow_any':any(x['overflow'] for x in v),
       'status':'invalid_measurement_V4_counter_overflow' if void else 'valid',
       'all_zero_mod8':all(x['n_mod8']==0 for x in v) and not void,
       'p_under_uniform_null_if_all_zero':(8.0**-len(v)) if (all(x['n_mod8']==0 for x in v) and not void) else None,
       'seconds':[x['seconds'] for x in v],'tags':[x['tag'] for x in v],
       'j0':[x['j0'] for x in v],'rk_sha256':[x['rk_sha256'] for x in v],'base':[x['base'] for x in v]}
    out['per_arm_round'].append(e)
json.dump(out,open(D+'/results_summary.json','w'),indent=1)
for e in out['per_arm_round']:
    print(e['arm'],'r=%d'%e['r'],'t=%d'%e['trials'],'mod8=',e['residue_mod8'],e['status'],
          'p=',e['p_under_uniform_null_if_all_zero'])
