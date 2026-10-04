"""Independent certificate/metadata checks; no producer imports or native arithmetic."""
import hashlib,json

def check(inputs, raw, cert):
    fs=[f for f in inputs['fixtures'] if f['group']==raw['group']]
    assert [f['id'] for f in fs]==[r['id'] for r in raw['fixtures']]
    for f,r in zip(fs,raw['fixtures']):
        h=f.copy();h.pop('fixture_sha256')
        assert hashlib.sha256(json.dumps(h,sort_keys=True,separators=(',',':')).encode()).hexdigest()==f['fixture_sha256']
        assert r['fixture_sha256']==f['fixture_sha256']
        assert r['accepted'] is False
        if raw['group']==1:
            assert inputs['native_interface']=='unresolved'
            assert r['status']=='unmeasured' and all(r[k] is None for k in ['d_ff','d_lf','sd_bounds'])
            assert cert['native_matrices']==[] and cert['native_certificates']==[]
        elif raw['group']==2:
            assert f['signature']['quotient']!=f['ordinary_signature']['quotient']
            assert f['interface_proof'] is None and r['status']=='incompatible'
            assert {k:v for k,v in f['signature'].items() if k!='quotient'}=={k:v for k,v in f['ordinary_signature'].items() if k!='quotient'}
        elif raw['group']==3:
            assert r['status']=='inconclusive' and r['certified_witness'] is None
        elif f['id']=='uniform-gap':
            assert r['status']=='rejected_inference'
            assert cert['quantifier']['finite_certificate_implies_no_uniform_constant'] is False
            assert cert['quantifier']['finite_table_would_only_bound_supplied_constants'] is True
        else:
            p=f['field']; a,b=f['curve'];x=f['target_x']
            value=(x*x*x+a*x+b)%p
            pairs=[[y,(y*y)%p] for y in range(p)]
            roots=[y for y,s in pairs if s==value]
            assert cert['domain']==dict(field=p,x=x,rhs=value,y_square_residues=pairs,roots=roots)
            assert r['rational_y']==roots and r['admissible']==bool(roots)
            assert r['status']==('admissible' if roots else 'inadmissible')
    assert raw['incorrectly_accepted_claims']==0
    return {'passed':True,'checked_fixture_count':len(fs),'independent_session':False,'method':'separate checker implementation; same Executor session; not independent research validation'}
