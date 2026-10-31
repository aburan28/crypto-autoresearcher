"""Bind reviewable mirrors and all21 CSV rows to the sealed raw export."""
import csv,hashlib,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main(root):
    bundle=json.load(open(P/'BUNDLE.json'));assert sha(P/'evidence.tar.zst')==bundle['archive_sha256']
    assert sha(root/'MANIFEST.json')==bundle['manifest_sha256']
    C=root/'canonical-equations-01';R=root/'ccr-recovery'
    for name in ['AUDIT.json','FIBER-AUDIT.json','TABLES.json','cohort-inputs.json','rows.json','LMFDB-SCOPE.json','PAPER-SOURCE.json','FLINT-RUNTIME.json']:
        assert (P/name).read_bytes()==(C/name).read_bytes(),name
    for name in ['FORMULA-AUDIT.json','FORMULA-PROTOCOL.json','FORMULA-RESULT.json']:
        assert (P/name).read_bytes()==(R/name).read_bytes(),name
    assert (P/'CCR-ACCESS.json').read_bytes()==(R/'ACCESS.json').read_bytes()
    aa=json.load(open(C/'AUDIT.json'))['rows'];bb=json.load(open(C/'FIBER-AUDIT.json'));cc=json.load(open(R/'FORMULA-AUDIT.json'))['rows'];raw=json.load(open(C/'rows.json'))
    rows=list(csv.DictReader(open(P/'comparison.csv')));assert len(rows)==len(raw)==21
    for i,(q,r) in enumerate(zip(rows,raw)):
        for k,v in r.items():
            if k in q:assert q[k]==str(v),(i,k)
        x=[v for v in aa if v['curve_uid']==r['curve_uid']];y=[v for v in bb['rows'] if v['index']==i];z=[v for v in bb['cells'] if v['index']==i]
        expected={'coordinate_cells':len(x),'rational_parameters':sum(len(v['roots']) for v in z),'fiber_checks':len(y),'coordinate_exceptions':sum(v['gcd_X_degree']>0 or v['gcd_J_degree']>0 or v['zero_parameter'] for v in x),'fiber_exceptions':sum(v['gcd_X_degree']>0 or v['gcd_Y_degree']>0 or v['j0_in_fiber'] or v['j1728_in_fiber'] for v in y),'literal_CCR_common_zero_degree':next(v['common_zero_gcd_degree'] for v in cc if v['index']==i)}
        assert all(q[k]==str(v) for k,v in expected.items())
    print(json.dumps({'status':'PASS','full_identity_CSV_rows':21,'source_mirrors':12,'CSV_parameter_total':sum(int(r['rational_parameters']) for r in rows),'CSV_fiber_total':sum(int(r['fiber_checks']) for r in rows)},sort_keys=True))
if __name__=='__main__':main(Path(sys.argv[1]))
