"""Verify the public archive without the unpublished historical source/binary.

Optional --replay reruns the independent GP checker, never the native producer.
"""
import collections,csv,hashlib,json,subprocess,sys,tempfile
from pathlib import Path
P=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    m=json.loads((P/'MANIFEST.json').read_text())
    for n,r in m['files'].items():assert (P/n).stat().st_size==r['bytes'] and sha(P/n)==r['sha256'],n
    d=[json.loads(x) for x in (P/'observations.jsonl').read_text().splitlines()];z=[r for r in d if r['kind']=='cohort']
    assert len(z)==598 and all(r['flag']==0 and not r['errors'] and r['arithmetic']['zero_divisions']==0 for r in z)
    rows=json.loads((P/'rows.json').read_text());cells=json.loads((P/'CELLS.json').read_text());expected={(c['index'],c['ell'],a,b) for c in cells for a in c['roots'] for b in [26,30]}
    assert len(expected)==598 and len(cells)==315 and expected=={(r['index'],r['q'],r['alpha'],r['bits']) for r in z}
    assert len(rows)==21 and sum(r['label']=='omitted' for r in rows)==11 and len({r['timestamp'] for r in rows})==6
    assert sha(P/'cohort-inputs.json')=='93ac4774b993a994a17d9327df92e0f2b287e66755cd933fdc683015fec1d545'
    pairs=collections.defaultdict(dict);inversions=0
    for r in d:
        if 'arithmetic' not in r:continue
        p=r['p'];zero=0
        for a,b,c in r['arithmetic']['divisions']:
            if b%p:assert (b*c-a)%p==0
            else:assert c==0;zero+=1
            inversions+=1
        assert zero==r['arithmetic']['zero_divisions']
        if r['kind']=='cohort':
            row=rows[r['index']];assert (p,r['A'],r['B'])==(int(row['p']),p-3,int(row['b']))
            assert r['checks'][-1]['pass'] and all(not c['pass'] for c in r['checks'][:-1])
            pairs[r['index'],r['q'],r['alpha']][r['bits']]=r
    for pp in pairs.values():assert {k:v for k,v in pp[26].items() if k!='bits'}=={k:v for k,v in pp[30].items() if k!='bits'}
    for aa in [r for r in d if r['kind']=='AA_control']:
        rr=next(r for r in d if r['kind']=='regular_control' and r['bits']==aa['bits'] and r['alpha']==aa['alpha']);assert {k:v for k,v in rr.items() if k!='kind'}=={k:v for k,v in aa.items() if k!='kind'}
    assert len([r for r in d if r['kind']=='derivative_control' and r['actual']==r['expected']])==60
    ex=[r for r in d if r['kind']=='exception_control'];assert len(ex)==2 and all(r['arithmetic']['zero_divisions']>0 for r in ex)
    audit=json.loads((P/'INDEPENDENT-AUDIT-02.json').read_text());assert audit['status']=='PASS'
    lines=(P/'audit-gp-02.stdout').read_text().splitlines();records=[json.loads(x) for x in lines if x.startswith('[')]
    assert len(records)==301 and sorted(r[0] for r in records)==list(range(301)) and sum(r[2] for r in records)==437 and all(r[2]==r[3] for r in records) and lines[-1]=='INDEPENDENT_COMPLETE 301 437'
    assert (P/'audit-gp-02.stderr').read_text().strip() in ['','***   Warning: new maximum stack size = 512000000 (488.281 Mbytes).']
    if '--replay' in sys.argv:
        with tempfile.TemporaryDirectory(prefix='atkin-gp-replay-') as t:
            temp=Path(t)
            for f in [P/'audit-input.gp',P/'audit-native-02.gp',*P.glob('audit-table-*.gp')]: (temp/f.name).symlink_to(f)
            r=subprocess.run(['/opt/homebrew/bin/gp','-q','-f','-s','256000000','audit-native-02.gp'],cwd=temp,capture_output=True,timeout=1800)
            assert r.returncode==0 and r.stdout==(P/'audit-gp-02.stdout').read_bytes() and r.stderr==(P/'audit-gp-02.stderr').read_bytes()
    print(json.dumps({'status':'PASS','sealed_files':len(m['files']),'cohort_calls':598,'curves':21,'streams':6,'division_identities':inversions,'GP_cases':301,'GP_branch_checks':437,'GP_replayed':'--replay' in sys.argv}))
if __name__=='__main__':main()
