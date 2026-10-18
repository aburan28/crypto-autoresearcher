"""Allocate prospective identifiers only, without approving or launching anything."""
import json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent/'allocated-ids.json'
if OUT.exists():raise SystemExit('Refuse to replace prior identifier allocations')
rows={}
for role,kind,args in [('experiment','experiment',['--area','ECDLP']),('catalog_run','run',['--area','ECDLP']),('panel_run','run',['--area','ECDLP']),('executor','handoff',['--date','20261018']),('archive','handoff',['--date','20261018']),('decision','coordinator_decision',['--date','20261018']),('batch','batch',[])]:
 o=subprocess.check_output(['python3','tools/allocate_id.py','--next',kind,*args],cwd=ROOT,text=True)
 rid=re.search(r'(?:EXP-ECDLP|RUN-ECDLP|TASK-20261018|DEC-20261018|BATCH)-[0-9a-f]{6}',o).group()
 p=subprocess.run(['python3','tools/allocate_id.py','--check',rid],cwd=ROOT,text=True,capture_output=True)
 if p.returncode:raise RuntimeError(p.stdout+p.stderr)
 rows[role]=rid
OUT.write_text(json.dumps({'ids':rows,'official_approval_created':False,'scientific_trials_launched':0,'base_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()},indent=2)+'\n')
print(json.dumps(rows,indent=2))
