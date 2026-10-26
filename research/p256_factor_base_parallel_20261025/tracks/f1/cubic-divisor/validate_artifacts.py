"""Final source/input/result integrity validation for the bounded continuation."""
import ast,gzip,hashlib,json,pathlib,xml.etree.ElementTree as ET
ROOT=pathlib.Path(__file__).resolve().parent
STUDY=ROOT.parent.parent.parent

def main():
    execution=json.loads((ROOT/'execution.json').read_text())
    for name,sha in execution['input_hashes'].items():
        assert hashlib.sha256((STUDY/name).read_bytes()).hexdigest()==sha
    for name,sha in execution['source_hashes'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha
    for q in ROOT.glob('*.py'):ast.parse(q.read_text())
    for q in ROOT.rglob('*.json'):json.loads(q.read_text())
    ET.parse(ROOT/'diagram.svg')
    packed=json.loads((ROOT/'packed-artifacts.json').read_text())
    for rec in packed['artifacts']:
        stored=(ROOT/rec['stored_path']).read_bytes();raw=gzip.decompress(stored)
        assert hashlib.sha256(raw).hexdigest()==rec['raw_sha256']
        assert hashlib.sha256(stored).hexdigest()==rec['stored_sha256']
        assert len(raw)==rec['raw_bytes'] and len(stored)==rec['stored_bytes']
        json.loads(raw)
    outcomes=[]
    for folder in ['attempts-01','attempts-02']:
        for r in json.loads((ROOT/folder/'receipt.json').read_text()):
            outcomes.append(r['status'])
            if r['status']=='PASS':
                q=ROOT/folder/(r['label']+'.json')
                raw=q.read_bytes() if q.exists() else gzip.decompress(q.with_suffix('.json.gz').read_bytes())
                assert hashlib.sha256(raw).hexdigest()==r['result_sha256']
            assert r['status'] in ['PASS','WATCHDOG_STOP_UNKNOWN']
    assert outcomes.count('PASS')==21 and outcomes.count('WATCHDOG_STOP_UNKNOWN')==3
    maxsize=max(q.stat().st_size for q in ROOT.rglob('*') if q.is_file())
    assert maxsize<65536
    # The solved k=3 public positive is exactly the earlier committed query.
    old=json.loads((ROOT.parent/'checks-02/generic-k3.json').read_text())
    new=json.loads((ROOT/'checks-01/query-k3-positive.json').read_text())
    assert old['queries'][0]['target']==new['Q']
    result={'status':'PASS','checks':['source/input hashes','source syntax','all JSON and lossless compressed JSON',
      'SVG XML','all native result receipt hashes','21 complete plus 3 watchdog terminal outcomes',
      'fixed k3 target matches original committed target','all retained files <64KiB'],
      'maximum_retained_file_bytes':maxsize,'no_scientific_trial':True}
    (ROOT/'artifact-validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)

if __name__=='__main__':main()
