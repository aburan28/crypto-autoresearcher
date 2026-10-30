#!/usr/bin/env python3
"""Bind the exact checker constants and primary inputs to the committed handoff."""
import hashlib,json,runpy,subprocess,sys
from pathlib import Path
from arithmetic import P,TARGET_B,TARGET_R
root=Path(__file__).resolve().parent;repository=root.parents[3]
commit='2c8c71cfff6f7f63297fbe4de4608cd94d857184'
base='research/p256_factor_base_parallel_20261025/'
paths=[base+'baseline/parameters.py',base+'baseline/s4-symmetric.json',
       base+'plan/original-week-plan.json',base+'handoffs/TASK-20261025-929e0f.json']
records=[]
for relative in paths:
    local=(repository/relative).read_bytes()
    committed=subprocess.run(['git','show',commit+':'+relative],cwd=repository,capture_output=True,check=True).stdout
    assert local==committed
    records.append(dict(path=relative,sha256=hashlib.sha256(local).hexdigest(),matches_committed_input=True))
parameters=runpy.run_path(str(repository/paths[0]));target=next(c for c in parameters['CURVES'] if c['name']=='P-256')
assert (P,TARGET_B,TARGET_R)==(target['p'],target['b'],target['r']) and target['a']==-3 and target['h']==1
problem='problems/pkm-isogeny-chain-factor-base-no-fast-decomposition.md'
result=dict(status='PASS',checks=5,input_commit=commit,inputs=records,
            auxiliary_formula='y^2=x^3+x over exactly the baseline P-256 prime',
            target_constants_exactly_match_baseline=True,
            existing_problem=dict(path=problem,sha256=hashlib.sha256((repository/problem).read_bytes()).hexdigest(),provenance='internal; read existing record, did not rerun or revalidate historical trials'),
            command=[sys.executable,*sys.argv],source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
out=root/'input-bindings.json'
if out.exists():raise SystemExit('refusing to overwrite receipt')
out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps(dict(status='PASS',checks=5)))
