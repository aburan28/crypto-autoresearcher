#!/usr/bin/env python3
import hashlib, json, subprocess
from pathlib import Path

ROOT = Path('/home/ec2-user/auto-semaev-review-r2-plan-20261031')
OUT = Path('/home/ec2-user/semaev-r2-j2-20261031')
SOURCE = '232f4e78abe6cd8eca285fb2be075d3fdd40ee33'
BASE = 'a1f3d0fde48d8a09301d65f8b8056f3cf42fc307'
HEAD = 'f9f36cd81bba99872cdec73dd23e2e69213fd446'
PLAN_SOURCE = 'ad91212179e737d829076ca593d608261590ba89'

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)

def blob(rev, path):
    return git('show', f'{rev}:{path}')

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

receipt_raw = (OUT / 'hosted-named-receipt.json').read_bytes()
r = json.loads(receipt_raw)
p = r['provenance']
parents = git('rev-list', '--parents', '-n', '1', SOURCE).decode().split()
assert parents == [SOURCE, BASE, HEAD], parents
assert p['source_commit'] == SOURCE
assert r['task']['theorem_name'] == 'CryptoResearch.Semaev.ConcreteFirstFallWitness.concreteNewFall'
assert r['verification']['status'] == 'machine_verified'
assert r['verification']['build_passed'] and r['verification']['axiom_audit_passed']
assert r['verification']['forbidden_constructs'] == []
assert 'witnessVec ∈' in r['audit_log'] and 'witnessVec ∉' in r['audit_log']
assert "depends on axioms: [propext,\n Classical.choice,\n Quot.sound]" in r['audit_log']

source_checks = {}
for name, want in p['workspace_inputs'].items():
    if name == 'CryptoResearch.lean':
        paths = git('ls-tree', '-r', '--name-only', SOURCE, 'formal/CryptoResearch').decode().splitlines()
        modules = sorted('CryptoResearch.' + q[len('formal/CryptoResearch/'):-5].replace('/', '.') for q in paths if q.endswith('.lean'))
        header = ('/-\nGENERATED FILE -- do not edit, and do not commit.\n\n'
                  'Rebuild with `python3 tools/rebuild_formal_root.py`.  It lists every module\n'
                  'under CryptoResearch/ so that `lake build` compiles them and AxiomAudit.lean can\n'
                  'see their theorems.\n-/\n')
        raw = (header + '\n' + ''.join(f'import {m}\n' for m in modules)).encode()
    else:
        raw = blob(SOURCE, 'formal/' + name)
    source_checks[name] = sha(raw) == want
assert all(source_checks.values()), [k for k,v in source_checks.items() if not v]
verifier_checks = {name: sha(blob(SOURCE,name)) == want for name,want in p['verifier_inputs'].items()}
assert all(verifier_checks.values()), [k for k,v in verifier_checks.items() if not v]
for path, key in [('formal/CryptoResearch/Semaev/ConcreteFirstFallWitness.lean','theorem_sha256'),
                  ('formal/targets/semaev-s3-concrete-first-fall-20261023.yaml','task_spec_sha256'),
                  ('formal/lean-toolchain','lean_toolchain_sha256'),
                  ('formal/lake-manifest.json','lake_manifest_sha256')]:
    assert sha(blob(SOURCE,path)) == p[key]
    assert sha(blob(PLAN_SOURCE,path)) == p[key]

# Recompute the row operations from the literal four equations in the theorem's import.
equations = [[0,1,2,8,16,17,24,32,34,36,40,66,68,128,129,130,136],
             [8,17,34,68,72,128,132],
             [1,2,4,8,16,18,32,33,34,64,68,128,136],
             [1,8,16,128]]
def product(eq,m):
    row=0
    for t in eq: row ^= 1 << (t|m)
    return row
def high(row,d):
    return any((row>>j)&1 for j in range(256) if bin(j).count("1")>d)
def rows(d):
    return [product(eq,m) for eq in equations for m in range(256) if not high(product(eq,m),d)]
r2,r3=rows(2),rows(3)
combo=1321682796735964
witness=6277101735386703064921270320751746415339343215057222047510
selected=[i for i in range(len(r3)) if (combo>>i)&1]
calc=0
for i in selected: calc ^= r3[i]
assert len(r2)==28 and len(r3)==80
assert len(selected)==23 and calc==witness and not high(witness,2)
def value(v,a,b): return ((v>>a)&1)^((v>>b)&1)
assert all(value(v,80,192)==0 for v in r2)
assert value(witness,80,192)==1
false_control = next(({'changed_coordinate':j,'failing_row_index':i,'value':value(v,80,j),
                       'row_bit_80':(v>>80)&1,'row_bit_changed':(v>>j)&1}
                      for j in range(256) if j!=192 for i,v in enumerate(r2)
                      if value(v,80,j)==1),None)
assert false_control is not None
out = {'source_commit':SOURCE,'base':BASE,'head':HEAD,'merge_parents_exact':True,
       'receipt_sha256':sha(receipt_raw),'workspace_inputs_checked':len(source_checks),
       'workspace_input_mismatches':[k for k,v in source_checks.items() if not v],
       'verifier_inputs_checked':len(verifier_checks),
       'verifier_input_mismatches':[k for k,v in verifier_checks.items() if not v],
       'target_hashes_match_on_source_and_plan_commit':True,
       'elaborated_type_in_hosted_audit_log':r['audit_log'].split('target axiom audit passed: ')[1].split("'CryptoResearch.Semaev.ConcreteFirstFallWitness.concreteNewFall'")[0].strip(),
       'axioms':['propext','Classical.choice','Quot.sound'],
       'row_counts':{'degree_two':len(r2),'degree_three':len(r3)},
       'selected_rows':selected,'selected_count':len(selected),
       'witness_matches_recomputed_xor':True,'witness_degree_at_most_two':True,
       'separator_zero_on_degree_two_rows':True,'separator_one_on_witness':True,
       'false_separator_control':false_control}
(OUT/'raw-checks.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps(out,indent=2,sort_keys=True))
