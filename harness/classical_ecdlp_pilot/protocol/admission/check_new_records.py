#!/usr/bin/env python3
"""Read-only schema check of this pilot's eight named records only.

This is neither a whole-ledger validation nor an independent scientific review.
It does not mutate frozen records, claim completeness of cross-repository
references, or gate a completed experiment retroactively.
"""
import argparse
import json
from pathlib import Path
import sys

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--repo-root',type=Path,required=True)
p.add_argument('--ids',type=Path,default=Path(__file__).with_name('ids.json'))
a=p.parse_args()
root=a.repo_root.resolve();ids=json.loads(a.ids.read_text())
sys.path.insert(0,str(root/'tools'))
import validate_ledger as vl
ctx=vl.Ctx(set())
scope=[]
for kind,section,key in [('research_question','questions','question'),('hypothesis','hypotheses','hypothesis'),
                         ('coordinator_decision','decisions','approval_decision'),('handoff','handoffs','executor_task'),('handoff','handoffs','archive_task')]:
    path=root/'ledger'/section/(ids[key]+'.yaml')
    vl.check_ledger_record(str(path),kind,ctx)
    scope.append({'path':str(path.relative_to(root)),'method':'check_ledger_record','record_type':kind})
spec=root/'experiments'/ids['experiment']/'specification.yaml'
vl.check_experiment(str(spec),ctx)
scope.append({'path':str(spec.relative_to(root)),'method':'check_experiment'})
run=root/'experiments'/ids['experiment']/'runs'/ids['run']/'manifest.yaml'
vl.check_run(str(run),ctx)
scope.append({'path':str(run.relative_to(root)),'method':'check_run'})
goal=root/'ledger/goals'/ids['goal']/'goal.yaml'
doc=vl.load_yaml(str(goal),ctx)
body=doc.get('research_goal',doc.get('goal',doc)) if isinstance(doc,dict) else {}
if not isinstance(body,dict):body={};ctx.err(str(goal),'goal body is not a mapping')
for field in vl.GOAL_REQUIRED:
    if body.get(field) in (None,''):ctx.err(str(goal),"missing required field '"+field+"'")
if not vl.GOAL_ID.fullmatch(str(body.get('id',''))):ctx.err(str(goal),'invalid goal id')
if body.get('status') not in vl.GOAL_STATUSES:ctx.err(str(goal),'invalid goal status')
vl.check_ecc_budget_is_unlimited(str(goal),body,body.get('status'),ctx)
vl.check_budget_retirement(str(goal),body,ctx)
scope.append({'path':str(goal.relative_to(root)),'method':'GOAL_REQUIRED/id/status and goal budget checks only'})
report={'kind':'scoped_new_record_schema_check','paths_checked':scope,'errors':ctx.errors,'advisories':ctx.advisories,
        'whole_ledger_checked':False,'cross_record_reference_completeness_claim':False,'scientific_review_verified':False}
print(json.dumps(report,indent=2))
raise SystemExit(0 if not ctx.errors else 2)
