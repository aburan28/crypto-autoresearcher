"""Independent post-producer checker and sole writer of artifact-sha256.json."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
from admission import canonical_admission,AdmissionRefused
from artifacts import final_index,PAYLOAD
def check(plan,trial_id,run_dir,repo):
    canonical_admission(repo,plan,trial_id,run_dir)
    raw=json.loads((run_dir/'raw-result.json').read_text())
    cases=json.loads((run_dir/'cases.jsonl').read_text())
    if raw.get('case_count')!=26546 or len(cases)!=26546:raise ValueError('incomplete case coverage')
    for result in cases:
        if result.get('gate')=='OK' and not result.get('comparison',{}).get('equal'): pass # complete negative evidence is valid
        elif result.get('gate') not in ('OK','ZERO'):raise ValueError('unexpected malformed result in scientific panel')
    final_index(run_dir);return 0
def main():
 p=argparse.ArgumentParser();p.add_argument('--plan',required=True);p.add_argument('--trial-id',required=True);p.add_argument('--run-dir',required=True);p.add_argument('--repo',default='.');a=p.parse_args()
 try:return check(Path(a.plan),a.trial_id,Path(a.run_dir),Path(a.repo).resolve())
 except Exception as e:print('CHECK REFUSED: '+str(e),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
