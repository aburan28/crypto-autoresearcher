"""Future canonical driver: complete pipeline after supervisor admission only."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
from admission import canonical_admission,AdmissionRefused
from fixtures import gate
from crt import fold,candidates
from reference import full_domain,scalar_matches,compare
from cost_model import new_counters,descriptive_rows
from telemetry import start,finish
from artifacts import write_once,PAYLOAD
def execute_case(data):
    code=gate(data)
    if code=="ZERO":return {"gate":code,"candidates":[0],"reference":[0],"comparison":{"equal":True},"scalar":{"match_count":1,"first_match_index":0}}
    if code!="OK":return {"gate":code,"candidates":[],"reference":[],"comparison":{"equal":True}}
    pairs=[(x['a'],x['m']) for x in data['constraints']]; pc,rc=new_counters(),new_counters(); began=start()
    combined=fold(data['n'],pairs,pc); produced=candidates(data['n'],combined,pc)
    reference=full_domain(data['n'],pairs,rc); scalar=scalar_matches(data['zeta'],data['r'],produced,data['x'],pc)
    return {"gate":"OK","fold":combined,"candidates":produced,"reference":reference,"comparison":compare(reference,produced),"scalar":scalar,"producer_telemetry":finish(began,pc),"reference_telemetry":finish(began,rc),"cost_rows":descriptive_rows(pc)}
def run(plan,trial_id,run_dir,repo):
    admission=canonical_admission(repo,plan,trial_id,run_dir)
    # A real admitted plan carries one immutable full panel materialization. No fallback subset is accepted.
    spec=json.loads(Path(plan).read_text()); trial=next((x for x in spec.get('trials',[]) if x.get('id')==trial_id),None)
    if trial is None or not isinstance(trial.get('case_inputs'),list) or len(trial['case_inputs'])!=26546:raise AdmissionRefused("full supplied-residue panel absent")
    results=[execute_case(case) for case in trial['case_inputs']]
    bad=[i for i,x in enumerate(results) if not x['comparison']['equal']]
    docs={"manifest.yaml":{"schema":"auxin.run.v1","admission":admission,"trial_id":trial_id},"raw-result.json":{"case_count":len(results),"counterexample_count":len(bad)},"source-bindings.json":{},"launch-binding.json":admission,"fixtures.jsonl":trial['case_inputs'],"truth.jsonl":[{"x":x.get('x')} for x in trial['case_inputs']],"cases.jsonl":results,"reference-results.jsonl":[x['reference'] for x in results],"counterexamples.jsonl":[],"control-summary.json":{"case_count":len(results)},"cost-frontier.json":{},"telemetry.json":{},"execution-report.yaml":{"status":"complete"}}
    for name in PAYLOAD:write_once(run_dir/name,docs[name],empty=(name=="counterexamples.jsonl" and not bad))
    return 0
def main():
 p=argparse.ArgumentParser();p.add_argument('--plan',required=True);p.add_argument('--trial-id',required=True);p.add_argument('--run-dir',required=True);p.add_argument('--repo',default='.');a=p.parse_args()
 try:return run(Path(a.plan),a.trial_id,Path(a.run_dir),Path(a.repo).resolve())
 except AdmissionRefused as e:print("REFUSED: "+str(e),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
