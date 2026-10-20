"""Read-only evidence audit and independent algebraic consistency controls."""
from core import *
from collections import Counter
from algebra_pilots import S3,x,y,z


def main():
    results={p.stem:json.loads(p.read_text()) for p in (ROOT/'results').glob('SNFS-*.json')}
    original={r['provisional_id']:r for r in LEDGER['records']}
    plans=json.loads((ROOT/'experiment-plans.json').read_text())['records']
    assert set(results)==set(original)=={r['provisional_id'] for r in plans}
    assert len(results)==23
    assert len({r['seed_candidate'] for r in results.values()})==23
    for pid,result in results.items():
        assert result['rows'] and result['limitations']
        assert result['original_status']==original[pid]['status']
        assert result['seed_candidate']==SEEDS[pid]
        if result['original_status'].startswith('theorem-closed'):
            assert result['evidence_class']=='receipt-only'
        assert result['execution_status']=='pilot-completed'
    metadata=json.loads((ROOT/'run-metadata.json').read_text())
    for name,sha in metadata['source_sha256'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha, name
    assert all(run['exit_code']==0 and run['cpu_seconds']<240 for run in metadata['runs'])
    assert metadata['no_sieving'] and not metadata['canonical_registry_import']
    a3=results['SNFS-A3']['rows']
    for r in a3:
        if r['SAT']['status']=='verified-sat':assert r['enumeration_has_relation']
        if r['SAT']['status']=='unsat':assert not r['enumeration_has_relation']
    assert all(r['rho']['status']=='verified' for r in results['SNFS-E3']['rows'])
    assert results['SNFS-E4']['checks']['E8_exact_counts']=={'2':241,'4':2401,'6':9121,'8':26641}
    for r in results['SNFS-D3']['rows']:
        if r['relation_with_coefficients_at_most_2']:
            assert r['relation_kind']=='single-point-torsion'
    assert all(r['smooth_kernel_overlap']==0 and r['p']>r['B'] for r in results['SNFS-D4']['rows'])
    # Independent polynomial identity checks against explicit finite group sums.
    g=random.Random('read-only-evidence-audit-v1');checks=0
    for p in (101,257,1021):
        E=EC(p,2,3)
        for _ in range(150):
            P,Q,R=g.sample(E.points,3)
            assert E.add(E.add(P,Q),R)==E.add(P,E.add(Q,R))
            T=E.add(P,Q)
            if T is not None:
                assert int(S3(P[0],Q[0],T[0],E.a,E.b))%p==0
                checks+=1
    summary=json.loads((ROOT/'summary.json').read_text())
    assert summary['records']==23 and summary['measurement_rows']==sum(len(r['rows']) for r in results.values())
    assert summary['A3']['statuses']==dict(Counter(r['SAT']['status'] for r in a3))
    print(json.dumps(dict(records=23,measurement_rows=summary['measurement_rows'],
        source_hashes_verified=True,SAT_resolved_answers_agree_with_enumeration=True,
        toy_rho_answers_verified=True,receipt_only_restrictions_preserved=True,
        extra_group_and_summation_identity_checks=checks,
        full_original_campaigns_executed=False)))


if __name__=='__main__':main()
