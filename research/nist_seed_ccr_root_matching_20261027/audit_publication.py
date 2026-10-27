"""Bind full-identity CSVs, raw mirrors and source-predicate summary to export."""
import csv,hashlib,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main(E):
    b=json.load(open(P/'BUNDLE.json'));assert sha(P/'evidence.tar.zst')==b['archive_sha256'] and sha(E/'MANIFEST.json')==b['manifest_sha256']
    for name in ['AUDIT.json','CONTROL-COUNTS.json','LMFDB-SCOPE.json','ATTEMPT02-AMENDMENT.json','ATTEMPT03-AMENDMENT.json','SOURCE-BOUNDARY.json','FLINT-RUNTIME.json','CCR-ACCESS.json','MORAIN-SOURCE.json']:assert (P/name).read_bytes()==(E/name).read_bytes(),name
    a=json.load(open(E/'AUDIT.json'));raw=json.load(open(E/'attempt03/rows.json'));rows=list(csv.DictReader(open(P/'comparison.csv')));cells=list(csv.DictReader(open(P/'cells.csv')));assert len(rows)==21 and len(cells)==147
    for i,(r,q) in enumerate(zip(raw,rows)):
        for k,v in r.items():
            if k in q:assert str(v)==q[k]
        assert q['a']==str(int(r['p'])-3)
        rr=[v for v in a['rows'] if v['index']==i]
        expected={'cells':len(rr),'favorable_cells':sum(v['rational_roots'][0]>0 for v in rr),'favorable_degree_at_least7':sum(v['ell']>=7 and v['rational_roots'][0]>0 for v in rr),'S1_roots':sum(v['rational_roots'][0] for v in rr),'corrected_pair_attempts':sum(v['arms'][0]['pair_attempts'] for v in rr),'corrected_unique_kernels':sum(v['arms'][0]['unique_cyclic_kernels'] for v in rr),'corrected_missing_S1_roots':sum(v['arms'][0]['S1_roots_without_cyclic_kernel'] for v in rr),'literal_unique_kernels':sum(v['arms'][1]['unique_cyclic_kernels'] for v in rr),'literal_unique_kernels_degree_at_least5':sum(v['arms'][1]['unique_cyclic_kernels'] for v in rr if v['ell']>=5),'projection_collision_cells':sum(v['projection_collisions'] for v in rr)}
        assert all(q[k]==str(v) for k,v in expected.items())
    for q,r in zip(cells,a['rows']):
        assert (q['curve_uid'],q['label'],int(q['ell']))==(r['curve_uid'],r['label'],r['ell'])
        for j,name in enumerate(['S1','Anew','Bnew']):assert int(q[name+'_degree'])==r['projection_degrees'][j] and int(q[name+'_roots'])==r['rational_roots'][j]
        assert int(q['projection_collision'])==r['projection_collisions']
        for j,name in enumerate(['corrected','literal']):
            for k in ['pair_attempts','source_factor_passes','unique_cyclic_kernels','coherent_quotient_pairs','S1_roots_without_cyclic_kernel']:assert int(q[name+'_'+k])==r['arms'][j][k]
    pred=json.load(open(P/'SOURCE-PREDICATES.json'));assert pred['cohort_distinct_rational_S1_values']==sum(len(r['S1_fiber_degrees']) for r in a['rows'])==112
    assert pred['cohort_repeated_S1_values']==sum(any(m>(r['ell']-1)//2 for m in r['S1_fiber_degrees']) for r in a['rows'])==0
    assert pred['special_j0_control']==next(r for r in a['controls'] if r['index']==22)
    print(json.dumps({'status':'PASS','curve_rows':21,'cell_rows':147,'raw_mirrors':10,'source_rule_S1_values':112,'source_rule_repeated_S1_values':0},sort_keys=True))
if __name__=='__main__':main(Path(sys.argv[1]))
