#!/usr/bin/env python3
"""Frozen local recovery controls; no frontier or performance inference."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import shutil
import struct
import subprocess
import time

from quotient_lift import monomials, write_certificate
from test_quotient_lift import oracle, independent_conditions


def digest(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def save(p, value):
    with p.open('x') as f:
        json.dump(value, f, indent=2, sort_keys=True)
        f.write('\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--plan', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    plan = json.loads(a.plan.read_text())
    for path, sha in plan['hashes'].items():
        assert digest(Path(path)) == sha, path
    a.out.mkdir(exist_ok=False, parents=True)
    save(a.out / 'plan.json', plan)
    results, failures = [], []
    sequence = 0

    def run(label, argv, env=None, expected=(0,)):
        nonlocal sequence
        sequence += 1
        prefix = a.out / f'{sequence:05d}-{label}'
        child_env = {k: v for k, v in os.environ.items() if not k.startswith('SEMAEV_CHECKPOINT_')}
        child_env.update(OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1')
        child_env.update(env or {})
        start = time.time()
        cmd = ['prlimit', '--as=' + str(plan['memory_bytes']), '--'] + list(map(str, argv))
        with prefix.with_suffix('.stdout').open('xb') as out, prefix.with_suffix('.stderr').open('xb') as err:
            try:
                p = subprocess.run(cmd, env=child_env, stdout=out, stderr=err, timeout=plan['timeout_seconds'])
                rc = p.returncode
            except subprocess.TimeoutExpired:
                rc = 'timeout'
        save(prefix.with_suffix('.step.json'), dict(argv=cmd, checkpoint_env=env or {}, returncode=rc,
             elapsed_seconds=time.time()-start, isolation='L0', wall_valid=False))
        assert rc in expected, (label, rc)
        return prefix.with_suffix('.stdout').read_text()

    fixtures = []
    for n, d, polys in [(7, 3, [{3,12,16}]), (10, 4, [{3,12,16},{5,32}]), (16,4,[{1,2}])]:
        fixtures.append(dict(n=n, d=d, polys=polys, full=True, chunk=4096 if n==16 else 31))
    rng = random.Random(2026102906)
    for n in range(3, 8):
        for d in range(2, min(4,n-1)+1):
            choices = monomials(n, 2)
            for replicate in range(12):
                polys = []
                for _ in range(1+replicate%n):
                    poly = {m for m in choices if rng.randrange(4)==0}
                    if replicate%2==0:
                        poly.discard(0)
                    polys.append(poly)
                fixtures.append(dict(n=n,d=d,polys=polys,full=False,chunk=7))
    for fixture in plan['semaev_fixtures']:
        fixtures.append(dict(fixture, full=True, chunk=7))
    assert len(fixtures)==150
    coverage = dict(multiple_closure_rounds=False, killed_constant=False, every_seed_boundary=False,
                    closure_round_restore=False, export_restore=False, repeated_restore=False,
                    corrupt_rejected=False, wrong_seed_rejected=False, wrong_chunk_rejected=False,
                    hook_failure_rejected=False)
    for index, fixture in enumerate(fixtures):
        root = a.out / f'case-{index:03d}'
        root.mkdir()
        row = dict(index=index)
        try:
            seed = root/'seed.bin'
            if 'polys' in fixture:
                images, q, _ = oracle(fixture['n'], fixture['d'], fixture['polys'])
                if q==0:
                    row['status']='zero_codomain_seed_outside_native_interface'
                    results.append(row)
                    continue
                write_certificate(seed,fixture['n'],fixture['d'],images,q)
            else:
                shutil.copyfile(fixture['seed_path'],seed)
            chunk=fixture['chunk']
            args=[seed,root/'reference.bin',str(chunk),str(plan['memory_bytes'])]
            reference=json.loads(run('reference',[plan['reference'],*args]))
            args[1]=root/'plain.bin'
            plain=json.loads(run('plain',[plan['candidate'],*args]))
            assert plain==reference
            if plain['status']=='candidate_certificate':
                assert digest(root/'plain.bin')==digest(root/'reference.bin')
            full=fixture['full']
            if plain.get('closure_rounds',0)>1 and not coverage['multiple_closure_rounds']:
                full=True;coverage['multiple_closure_rounds']=True
            if plain['status']=='projection_kills_one' and not coverage['killed_constant']:
                full=True;coverage['killed_constant']=True
            row.update(status=plain['status'],observation=plain,full_restore_controls=full)
            if not full:
                results.append(row)
                continue
            snapshots=root/'snapshots'
            args[1]=root/'checkpointed.bin'
            obs=json.loads(run('checkpointed',[plan['candidate'],*args],{'SEMAEV_CHECKPOINT_DIR':str(snapshots)}))
            assert obs==reference
            if obs['status']=='candidate_certificate':
                assert digest(args[1])==digest(root/'reference.bin')
            checkpoints=sorted(snapshots.glob('checkpoint-*.bin'),key=lambda p:int(p.stem.split('-')[1]))
            row['snapshots']=len(checkpoints)
            for cp in checkpoints:
                h=struct.unpack('<14Q',cp.read_bytes()[:112])
                target=root/('restore-'+cp.stem)
                args[1]=root/(cp.stem+'-restored.bin')
                restored=json.loads(run('restore',[plan['candidate'],*args],dict(
                    SEMAEV_CHECKPOINT_DIR=str(target),SEMAEV_CHECKPOINT_RESTORE=str(cp))))
                assert restored==reference
                if restored['status']=='candidate_certificate':
                    assert digest(args[1])==digest(root/'reference.bin')
                if h[8]==1 and h[11]>0:coverage['closure_round_restore']=True
                if h[8]==2:coverage['export_restore']=True
            if checkpoints:coverage['every_seed_boundary']=True
            # Repeated fresh-process stops exercise continuation positions, not just reads.
            if fixture['full'] and index!=2:
                restored_path=None
                for generation in range(len(checkpoints)+2):
                    directory=root/f'chain-{generation}'
                    args[1]=root/f'chain-output-{generation}.bin'
                    env=dict(SEMAEV_CHECKPOINT_DIR=str(directory),SEMAEV_CHECKPOINT_STOP_AFTER='1')
                    if restored_path:env['SEMAEV_CHECKPOINT_RESTORE']=str(restored_path)
                    stdout=run('stop-chain',[plan['candidate'],*args],env,expected=(0,75))
                    if stdout:
                        assert json.loads(stdout)==reference
                        if reference['status']=='candidate_certificate':assert digest(args[1])==digest(root/'reference.bin')
                        coverage['repeated_restore']=True
                        break
                    cps=list(directory.glob('checkpoint-*.bin'));assert len(cps)==1
                    restored_path=cps[0]
                else:raise AssertionError('repeated restore did not finish')
            if index==0:
                cp=checkpoints[0]
                for name, data in [('truncated',cp.read_bytes()[:-1]),('corrupt',bytes([cp.read_bytes()[0]^1])+cp.read_bytes()[1:])]:
                    bad=root/(name+'.bin');bad.write_bytes(data);args[1]=root/(name+'-output.bin')
                    run(name,[plan['candidate'],*args],dict(SEMAEV_CHECKPOINT_DIR=str(root/name),SEMAEV_CHECKPOINT_RESTORE=str(bad)),expected=(2,))
                coverage['corrupt_rejected']=True
                wrong=root/'wrong-seed.bin';b=bytearray(seed.read_bytes());b[-1]^=1;wrong.write_bytes(b)
                run('wrong-seed',[plan['candidate'],wrong,root/'wrong-seed-output.bin',str(chunk),str(plan['memory_bytes'])],dict(SEMAEV_CHECKPOINT_DIR=str(root/'wrong-seed'),SEMAEV_CHECKPOINT_RESTORE=str(cp)),expected=(2,))
                coverage['wrong_seed_rejected']=True
                run('wrong-chunk',[plan['candidate'],seed,root/'wrong-chunk-output.bin',str(chunk+1),str(plan['memory_bytes'])],dict(SEMAEV_CHECKPOINT_DIR=str(root/'wrong-chunk'),SEMAEV_CHECKPOINT_RESTORE=str(cp)),expected=(2,))
                coverage['wrong_chunk_rejected']=True
                run('hook-failure',[plan['candidate'],seed,root/'hook-output.bin',str(chunk),str(plan['memory_bytes'])],dict(SEMAEV_CHECKPOINT_DIR=str(root/'hook'),SEMAEV_CHECKPOINT_PUBLISH='/bin/false'),expected=(2,))
                coverage['hook_failure_rejected']=True
            if plain['status']=='candidate_certificate':
                data=(root/'checkpointed.bin').read_bytes();n,d,cols,q=struct.unpack_from('<4q',data)
                if 'polys' in fixture:
                    masks=struct.unpack_from('<'+str(cols)+'Q',data,32);w=8*((q+63)//64);offset=32+8*cols
                    independent_conditions(n,d,{m:int.from_bytes(data[offset+j*w:offset+(j+1)*w],'little') for j,m in enumerate(masks)},q,fixture['polys'])
                    row['independent_generic_conditions']=True
                else:
                    r=fixture['record']
                    output=run('original-checker',['/usr/bin/python3',plan['checker'],root/'checkpointed.bin',r['n'],r['modulus_hex'],r['a2'],r['a6_hex'],r['z_hex'],*r['V_basis_hex']])
                    assert f'VALID: 1 is not in W_{d}(F)' in output
                    row['original_checker_accepted']=True
            row['controls_passed']=True
        except Exception as exc:
            row['failure']=repr(exc);failures.append(index)
        results.append(row)
        save(root/'result.json',row)
    save(a.out/'result.json',dict(scope='Local software recovery controls only; no cloud or frontier inference',
        plan_sha256=digest(a.plan),cases=results,failures=failures,coverage=coverage,
        passed=not failures and all(coverage.values())))
    print(json.dumps(dict(cases=len(results),failures=failures,coverage=coverage)))
    return int(bool(failures) or not all(coverage.values()))


if __name__=='__main__':
    raise SystemExit(main())
