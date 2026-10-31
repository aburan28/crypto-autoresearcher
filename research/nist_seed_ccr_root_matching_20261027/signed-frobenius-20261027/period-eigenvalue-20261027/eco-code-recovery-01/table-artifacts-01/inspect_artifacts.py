"""Verify a printed coefficient witness and map retained identities to source gaps."""
import csv
import hashlib
import io
import json
from pathlib import Path
import sys

P=Path(__file__).resolve().parent
ROOT=P.parents[5]
OLD=P.parent
COHORT=OLD.parent.parent/'prior-rows.json'
TABLE=Path('/Volumes/SSD990/llm/tmp/nist-sea-branch-audit-20261027/source/meq5')
EXPECTED_TABLE_SHA='0934cdbbdcbecefa5cd4a56d5982f43382d86c2ad24362902e9ebb8da140dd15'
PRINTED=[[125,0],[750,-1],[1575,0],[1300,0],[315,0],[30,0],[1,0]]
PRINTED_MOD101=[[24,0],[43,100],[60,0],[88,0],[12,0],[30,0],[1,0]]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def derive():
    # Authenticate the retained mirrors before following their full identities.
    seal=json.loads((OLD/'BUNDLE.json').read_text())
    oldcsv=OLD/'cohort-crosswalk.csv'
    assert sha(oldcsv)==seal['files']['cohort-crosswalk.csv']['sha256']
    assert sha(COHORT)=='e8d6a874e3dc77970c88957f4bca075a0cc7a431dd8bcb25e5c5d7bcba6eeb0f'
    assert sha(TABLE)==EXPECTED_TABLE_SHA
    rows=list(csv.DictReader(oldcsv.open()))
    originals=json.loads(COHORT.read_text())
    assert len(rows)==len(originals)==21
    assert len({r['curve_uid'] for r in rows})==21
    parsed=[list(map(int,l.split())) for l in TABLE.read_text().splitlines() if l.strip()]
    assert parsed[:7]==PRINTED and parsed[7:]==[[0,0]]
    assert [[v%101 for v in r] for r in PRINTED]==PRINTED_MOD101
    # Independent coefficient identity: (X^2+10X+5)^3 - J*X.
    poly=[1]
    for _ in range(3):
        out=[0]*(len(poly)+2)
        for i,a in enumerate(poly):
            for j,b in enumerate([5,10,1]):out[i+j]+=a*b
        poly=out
    assert poly==[r[0] for r in PRINTED]
    for r,s in zip(rows,originals):
        for k in ['curve_uid','label','name','seed_hex']:
            assert r[k]==str(s[k])
        for k in ['p','b','n','ordinal']:
            assert int(r[k])==int(s[k])
        assert int(r['stream'])==int(s['timestamp'])
        r['original_table_bytes']='UNKNOWN'
        r['original_binary_backend_and_ABI']='UNKNOWN'
        r['original_table_error_policy_and_visitation']='UNKNOWN'
        r['historical_IO_criterion_prediction']='UNDETERMINED'
    out=io.StringIO(newline='')
    w=csv.DictWriter(out,fieldnames=list(rows[0]),lineterminator='\n')
    w.writeheader();w.writerows(rows)
    data={
        'status':'PASS', 'kind':'source collation and identity/gap verification',
        'new_scientific_trials':0, 'historical_criterion_identified':False,
        'printed_witness':{
            'author':'Frank J. Lehmann','title_page_date':'1994-07-29',
            'source_ps_sha256':'244fc341ec6785f1b779614d155d71205a967359a46e151f1995ed44bc6339c1',
            'printed_page':78,'PDF_page':79,'page_visually_inspected':True,
            'ell':5,'coefficient_rows':PRINTED,
            'modulus101_rows':PRINTED_MOD101,
            'polynomial':'(X^2+10*X+5)^3-J*X',
            'later_table_sha256':EXPECTED_TABLE_SHA,
            'later_table_coefficients_equal':True,
            'trailing_later_table_padding':[[0,0]],
            'printed_typo':'The intermediate boxed a_0,0=43 conflicts with the following table a_0,0=24 mod101. Context computes a_1,0=43. Final tables agree with each other and the polynomial identity.',
            'limit':'One polynomial coefficient identity; no authentication of original binary files or use by NIST.',
        },
        'cohort':{'curves':21,'published':10,'omitted':11,'streams':6,
                  'historical_IO_predictions_undetermined':21},
        'input_bindings':{
            'cohort':{'path':str(COHORT.relative_to(ROOT)),'sha256':sha(COHORT)},
            'prior_csv':{'path':str(oldcsv.relative_to(ROOT)),'sha256':sha(oldcsv)},
            'prior_seal':{'path':str((OLD/'BUNDLE.json').relative_to(ROOT)),
                          'sha256':sha(OLD/'BUNDLE.json')},
        },
        'inference_boundary':'Binary compatibility depends on files/build/ABI. Curve-dependent consequences require the original file bytes, actual visitation and caller error policy; missing inputs are not curve rejections.',
    }
    return data,out.getvalue()


if __name__=='__main__':
    record,csv_text=derive()
    for name,body in {'COLLATION.json':json.dumps(record,indent=2,sort_keys=True)+'\n',
                      'cohort-gap-crosswalk.csv':csv_text}.items():
        if '--check' in sys.argv:assert (P/name).read_text()==body,name
        else:
            assert not (P/name).exists(),name
            (P/name).write_text(body)
    print(json.dumps({'status':'PASS','printed_rows_matched':7,'curves_bound':21,
                     'historical_predictions_undetermined':21,'new_scientific_trials':0}))
