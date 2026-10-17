"""Read-only independent validation of all saved follow-up answers."""
from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from norm_decomposition import LiteEC
from blind_sections import validate
from geometry_sections import recover_base
from core import EC


def main():
    datasets={name:json.loads((ROOT/name).read_text()) for name in
        ('norm-results.json','norm-native-results.json','norm-extended-results.json')}
    positive=0;counts={}
    for name,data in datasets.items():
        counts[name]=len(data['rows'])
        for row in data['rows']:
            E=LiteEC(row['p'],row['a'],row['b']);nr=row['norm']
            assert nr['found']==row['enumeration']['found']
            if row['mode']=='planted':assert nr['found']
            if nr['found']:
                P,Q=[tuple(T) for T in nr['points']]
                assert E.valid(P) and E.valid(Q)
                assert pow(P[0],row['L'],row['p'])==pow(Q[0],row['L'],row['p'])==1
                assert E.add(P,Q)==tuple(row['R']);positive+=1
        assert all(r['resultant_identity'] for r in data['checks'])
    left=datasets['norm-results.json']['rows'];right=datasets['norm-native-results.json']['rows']
    assert len(left)==len(right)==432
    for a,b in zip(left,right):
        assert all(a[k]==b[k] for k in ('p','a','b','L','case','trial','mode','R','factor_base_points'))
        assert a['norm']['found']==b['norm']['found']
    blind=json.loads((ROOT/'blind-results.json').read_text())
    geometry=json.loads((ROOT/'geometry-results.json').read_text())
    section_checks=0
    for row in blind['rows']:
        surface=next(s for s in blind['surfaces'] if s['p']==row['p'])
        data={k:surface[k] for k in ('p','a','b','G')};data.update(d=row['d'],R=row['R'])
        assert recover_base(data)==sorted(tuple(P) for P in surface['points'])
        E=EC(surface['p'],surface['a'],surface['b']);P=tuple(surface['P']);Q=E.mul(row['k'],P)
        assert row['rho']['status']=='verified' and row['rho']['k']==row['k']
        if row['solver']['status']=='sat':
            assert row['oracle_bounded_degree_exists']
            assert validate(data,row['solver'],[tuple(T) for T in surface['points']],surface['scalars'],E,P,Q)['recovered_log']==row['k']
            section_checks+=1
        elif row['solver']['status'] in ('unsat','no-Fp-root'):assert not row['oracle_bounded_degree_exists']
    for row in geometry['rows']:
        source=next(r for r in blind['rows'] if all(r[k]==row[k] for k in ('p','d','mode','trial')))
        assert (row['solver']['status']=='sat')==source['oracle_bounded_degree_exists']
        if row['solver']['status']=='sat':
            surface=next(s for s in blind['surfaces'] if s['p']==row['p'])
            data={k:surface[k] for k in ('p','a','b','G')};data.update(d=row['d'],R=source['R'])
            E=EC(surface['p'],surface['a'],surface['b']);P=tuple(surface['P']);Q=E.mul(source['k'],P)
            assert validate(data,row['solver'],[tuple(T) for T in surface['points']],surface['scalars'],E,P,Q)['recovered_log']==source['k']
            section_checks+=1
    sums=ROOT/'SHA256SUMS'
    if sums.exists():
        for line in sums.read_text().splitlines():
            digest,name=line.split('  ',1)
            assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    print(json.dumps(dict(norm_rows=counts,norm_verified_positive_answers=positive,
        cross_backend_instances_identical=True,blind_rows=len(blind['rows']),geometry_rows=len(geometry['rows']),
        section_maps_and_recovered_logs_independently_rechecked=section_checks,
        no_asymptotic_claim=True)))


if __name__=='__main__':main()
