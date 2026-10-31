"""Read-only portable replay. Requires Python 3.9+, no native library or network."""
import collections,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def get(p):return json.loads((ROOT/p).read_text())
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    manifest=get('MANIFEST.json')
    for name,h in manifest.items():assert digest(ROOT/name)==h,name
    cohort=get('validation-02/cohort-inputs.json')
    assert digest(ROOT/'validation-02/cohort-inputs.json')=='93ac4774b993a994a17d9327df92e0f2b287e66755cd933fdc683015fec1d545'
    rows=get('validation-02/rows.json');byuid={r['curve_uid']:r for r in rows}
    assert len(byuid)==21 and sum(r['label']=='omitted' for r in rows)==11
    assert len({r['timestamp'] for r in rows})==6
    for r in cohort['rows']:
        q=byuid[r['curve_uid']]
        assert all(q[k]==r[k] for k in r)
        p,c,b=int(q['p']),int(q['c']),int(q['b'])
        assert (c*b*b+27)%p==0 and (27*b*b-108)%p!=0
    observations=get('validation-02/RESULTS.json')['observations']
    inverses=[r for r in observations if r['kind']=='inverse']
    assert len(inverses)==756
    expected={(uid,v,bits,c,m) for uid in byuid for v in ['1.0','1.1'] for bits in [26,30] for c in ['c','b','j_denominator'] for m in [0,1,2]}
    assert {(r['curve_uid'],r['version'],r['bits'],r['case'],r['mode']) for r in inverses}==expected
    for r in inverses:
        assert r['receipt']['returncode']==0 and r['record']['inverse_ok']==1
    baselines=[r for r in observations if r['kind']=='baseline'];assert len(baselines)==4
    for r in baselines:
        rr=r['records'];assert len(rr)==21
        assert {x['name'] for x in rr}=={x['name'] for x in rows}
        assert all(x['inverse_ok'] and x['root_ok'] and x['root_lip_rng_calls']==0 and x['root_libc_unchanged'] for x in rr)
        assert all(t['prime']==1 and t['lip_rng_calls']==20 and t['libc_unchanged'] for x in rr for t in x['primality'])
        assert sum(bool(x['base_point'] and x['base_point']['x_matches']) for x in rr)==(6 if r['bits']==26 else 0)
    for bits in [26,30]:
        a,b=[r for r in baselines if r['bits']==bits]
        assert a['records']==b['records']
    # Check framing and digests for every completed external process capture.
    receipts=0
    for f in ROOT.rglob('RESULT.json'):
        r=json.loads(f.read_text());receipts+=1
        for stream in ['stdout','stderr']:
            assert digest(f.parent/(stream+'.txt'))==r[stream+'_sha256']
    ws=get('WITNESSES.json');assert len(ws)==126
    expectw={(uid,bits,c) for uid in byuid for bits in [26,30] for c in ['c','b','j_denominator']}
    assert {(r['curve_uid'],r['bits'],r['case']) for r in ws}==expectw
    for r in ws:
        q=byuid[r['curve_uid']];p,b=int(q['p']),int(q['b'])
        value={'c':int(q['c']),'b':b,'j_denominator':(27*b*b-108)%p}[r['case']]
        assert int(r['value'])==value and int(r['p'])==p
        assert r['receipt']['returncode']==0 and int(r['inverse'])==pow(value,-1,p)
    primes={2,3,5,17,101,65537,2147483647,2305843009213693951}
    for version in ['1.0','1.1']:
        for bits in [26,30]:
            f=ROOT/f'validation-02/build-{version}-{bits}/control/stdout.txt'
            rr=[json.loads(x) for x in f.read_text().splitlines()];assert len(rr)==28
            assert all(bool(r['prime'])==(int(r['input']) in primes) for r in rr[:17])
            assert rr[17]['root_control']==1
            state=1;mod=(1<<107)-1;mul=pow(3,121,mod);radix=1<<bits;bound=mod-mod%radix;expected_rng=[]
            for i in range(10):
                state=state*mul%mod
                while state>=bound:state=state*mul%mod
                expected_rng.append(state%radix)
            assert [x['rng'] for x in rr[18:]]==expected_rng
    fault=get('FAULT-CONTROL-STATUS.json')
    assert fault['completed_control_main_calls']==0
    assert fault['status']=='UNAVAILABLE_ASAN_STARTUP'
    result={'status':'PASS','cohort_curves':21,'published':10,'omitted':11,'streams':6,'native_inversion_checks':756,'independent_inverse_witnesses':126,'baseline_rows_including_AA':84,'completed_process_receipts':receipts,'ASAN_control':'startup unavailable; censored; no mathematical conclusion'}
    print(json.dumps(result,sort_keys=True));return result
if __name__=='__main__':main()
