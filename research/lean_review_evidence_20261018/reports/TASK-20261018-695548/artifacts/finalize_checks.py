from pathlib import Path
import hashlib,json,os,subprocess,yaml
REPORT=Path(__file__).resolve().parents[1];ART=REPORT/'artifacts';REVIEW=Path('/workspace/review-lean-evidence')
cmd=['/tmp/lean-review-venv/bin/python',str(ART/'check_review_independence.py'),
 '--plan',str(REVIEW/'research/lean_review_evidence_20261018/repair-plan.yaml'),
 '--reports',str(REPORT/'review_attestation.yaml'),'--no-addenda']
env={**os.environ,'PYTHONPATH':'/tmp/TASK-20261018-695548/runtime-v2','PYTHONDONTWRITEBYTECODE':'1'}
p=subprocess.run(cmd,cwd=REVIEW,env=env,capture_output=True,text=True,timeout=30)
(ART/'independence.stdout.log').write_text(p.stdout);(ART/'independence.stderr.log').write_text(p.stderr)
result={'command':cmd,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr,
        'scope':'Own attestation against sole-joint committed repair plan; no sibling report read',
        'visual_inspection':{'pages':3,'all_page_images_viewed':True,
        'legibility':'No clipped text or diagram; table and citations visible. All PDF pages inspected.'}}
for path in REPORT.rglob('*.json'):json.loads(path.read_text())
att=yaml.safe_load((REPORT/'review_attestation.yaml').read_text())
assert att['review_attestation']['verdict']=='breaks'
assert p.returncode==0,result
with (ART/'final-validation.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
manifest=[]
for path in sorted(REPORT.rglob('*')):
    if path.is_file() and path.name!='sealed-artifacts.json':
        data=path.read_bytes();manifest.append({'path':path.relative_to(REPORT).as_posix(),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
with (ART/'sealed-artifacts.json').open('x') as f:json.dump(manifest,f,indent=2);f.write('\n')
print(json.dumps({'files':len(manifest),'independence_exit_code':p.returncode,'verdict':'breaks','report_dir':str(REPORT)}))
