"""Bind public summary rows to their raw stdin, stdout, and process receipts."""
import json,sys
from pathlib import Path
def main(root):
    def get(p):return json.loads((root/p).read_text())
    rows=get('validation-02/rows.json');byuid={r['curve_uid']:(i,r) for i,r in enumerate(rows)}
    observations=get('validation-02/RESULTS.json')['observations'];counts={'inverse':0,'baseline':0,'witness':0}
    for item in observations:
        bits,version=item['bits'],item['version']
        if item['kind']=='inverse':
            i,r=byuid[item['curve_uid']];p,b=int(r['p']),int(r['b'])
            value={'c':int(r['c']),'b':b,'j_denominator':(27*b*b-108)%p}[item['case']]
            path=root/f"validation-02/build-{version}-{bits}/inverse-{i:02}-{item['case']}-{item['mode']}"
            assert (path/'stdin.txt').read_text()==f'{value} {p}\n'
            assert json.loads((path/'stdout.txt').read_text())==item['record']
            assert json.loads((path/'RESULT.json').read_text())==item['receipt']
            counts['inverse']+=1
        else:
            path=root/f"validation-02/build-{version}-{bits}/baseline-{item['repeat']}"
            assert [json.loads(x) for x in (path/'stdout.txt').read_text().splitlines()]==item['records']
            assert json.loads((path/'RESULT.json').read_text())==item['receipt']
            counts['baseline']+=1
    for item in get('WITNESSES.json'):
        i,r=byuid[item['curve_uid']];p=int(r['p']);value=int(item['value'])
        path=root/f"witness-and-fault-control/witness-{item['bits']}-{i:02}-{item['case']}"
        assert (path/'stdin.txt').read_text()==f'{value} {p}\n'
        assert json.loads((path/'stdout.txt').read_text())=={'sign':0,'inverse':item['inverse']}
        assert json.loads((path/'RESULT.json').read_text())==item['receipt']
        counts['witness']+=1
    assert counts=={'inverse':756,'baseline':4,'witness':126}
    print(json.dumps({'status':'PASS','raw_summary_bindings':counts},sort_keys=True))
if __name__=='__main__':main(Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent/'evidence')
