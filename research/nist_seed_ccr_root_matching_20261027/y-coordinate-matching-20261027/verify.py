"""Verify sealed match records; --replay independently recomputes every case."""
import hashlib,json,shutil,subprocess,sys,tempfile
from pathlib import Path
P=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    manifest=json.loads((P/'MANIFEST.json').read_text())
    for n,r in manifest['files'].items():assert sha(P/n)==r['sha256'] and (P/n).stat().st_size==r['bytes'],n
    gp=[json.loads(s) for s in (P/'native.stdout').read_text().splitlines() if s.startswith('[0,')];ind=[json.loads(s) for s in (P/'independent.jsonl').read_text().splitlines()];assert len(gp)==len(ind)==415
    assert [r[1] for r in gp]==[r['id'] for r in ind]==list(range(415))
    for a,b in zip(gp,ind):assert [a[2],a[3],a[4],a[5],a[6],a[7],a[8],a[9],a[10],a[11],a[12],a[13]]==[b[k] for k in ['index','ell','p','A','B','kernel','S1','x_frobenius','y_frobenius','y_matches','full_matches','first_y_match']]
    audit=json.loads((P/'AUDIT.json').read_text());assert audit['status']=='PASS' and audit['cohort_calls']==411
    assert audit['cohort_S1_zero_kernels']==audit['cohort_ambiguous_y_kernels']==audit['cohort_false_y_matches']==0
    for c in audit['controls'][:2]:assert len(c['false_y_matches'])==2 and len(c['full_matches'])==1
    assert audit['controls'][1]['first_y_trace_matches_order'] is False
    e=json.loads((P/'export.json').read_text());assert len(e['runs'])==830 and {r['arm'] for r in e['runs']}=={'native','independent'}
    for arm in ['native','independent']:assert {r['instance_id'] for r in e['runs'] if r['arm']==arm}=={f'kernel-{i}' for i in range(415)}
    assert json.loads((P/'EXPORT-CHECK.json').read_text())['returncode']==0
    for r in e['runs']:
        i=int(r['instance_id'].split('-')[-1]);z=gp[i];c=r['measurements']['counted'];assert c=={'calls':1,'signed_y_matches':len(z[11]),'full_point_matches':len(z[12]),'false_y_matches':len(set(z[11])-set(z[12]))}
    if '--replay' in sys.argv:
        with tempfile.TemporaryDirectory(prefix='atkin-y-replay-') as t:
            q=Path(t)
            for n in manifest['files']:
                dest=q/n;dest.parent.mkdir(exist_ok=True,parents=True);shutil.copyfile(P/n,dest)
            for n in ['independent.jsonl','AUDIT.json','curve-summary.csv']:(q/n).unlink()
            r=subprocess.run([sys.executable,'-u','audit.py'],cwd=q,capture_output=True,timeout=1800);assert r.returncode==0,(r.stdout+r.stderr).decode(errors='replace')
            newer=json.loads((q/'AUDIT.json').read_text());assert {k:v for k,v in audit.items() if k!='elapsed_seconds_diagnostic_only'}=={k:v for k,v in newer.items() if k!='elapsed_seconds_diagnostic_only'}
            assert (q/'independent.jsonl').read_bytes()==(P/'independent.jsonl').read_bytes() and (q/'curve-summary.csv').read_bytes()==(P/'curve-summary.csv').read_bytes()
    print(json.dumps({'status':'PASS','files':len(manifest['files']),'GP_calls':415,'independent_calls':415,'cohort_kernels':411,'scalar_checks':audit['independent_scalar_coordinate_checks'],'replayed':'--replay' in sys.argv}))
if __name__=='__main__':main()
