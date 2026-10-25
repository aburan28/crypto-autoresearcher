"""Check archived source identities only; does not run Lean or authenticate receipts.

Use --repositories-root to point at sibling checkouts of the four bound repositories.
Their frozen revisions must exist locally (fetch the cited PR heads if necessary).
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--repositories-root', type=Path, default=Path('/workspace'))
parser.add_argument('--snapshot-root', type=Path)
args = parser.parse_args()
study = Path(__file__).resolve().parent.parent
manifest = json.loads((study/'inputs.json').read_text())
failures = []
for entry in manifest['files']:
    repo = args.repositories_root / entry['repository']
    data = subprocess.check_output(['git', 'show', entry['revision']+':'+entry['path']], cwd=repo)
    if hashlib.sha256(data).hexdigest() != entry['sha256']:
        failures.append(entry['repository']+':'+entry['path'])
    if args.snapshot_root is not None:
        data = (args.snapshot_root/entry['repository']/entry['path']).read_bytes()
        if hashlib.sha256(data).hexdigest() != entry['sha256']:
            failures.append('snapshot:'+entry['repository']+':'+entry['path'])
print(json.dumps({'files':len(manifest['files']), 'identity_matches':not failures, 'failures':failures},indent=2))
raise SystemExit(bool(failures))
