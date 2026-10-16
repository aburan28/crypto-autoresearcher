#!/usr/bin/env bash
# Public-data point-count environment. Passed as EC2 user data.
set -euo pipefail
exec > >(tee -a /var/log/nist-seed-bootstrap.log) 2>&1

# The EC2 launch specifies instance-initiated shutdown = terminate.
systemd-run --unit=nist-seed-max-runtime --on-active=12h /sbin/shutdown -h now
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y git python3 pari-gp pari-seadata

mkdir -p /opt/nist-seed
git clone --depth 1 --filter=blob:none --sparse \
  --branch codex/nist-seed-followthrough-20261016 \
  https://github.com/aburan28/crypto-autoresearcher.git \
  /opt/nist-seed/repo
cd /opt/nist-seed/repo
git sparse-checkout set \
  research/nist_seed_followthrough_20261016 \
  research/nist_seed_selection_20261016 \
  research/nist_seed_provenance_20261016
python3 - <<'PY'
import hashlib
import json
import platform
import subprocess
import time
from pathlib import Path

root = Path('/opt/nist-seed/repo')
inputs = [
    root / 'research/nist_seed_followthrough_20261016/count_x9.py',
    root / 'research/nist_seed_followthrough_20261016/PROTOCOL.md',
    root / 'research/nist_seed_followthrough_20261016/AMENDMENT_2.md',
    root / 'research/nist_seed_selection_20261016/targets.json',
    root / 'research/nist_seed_selection_20261016/raw/candidates.jsonl',
]
record = {
    'ready_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    'python': platform.python_version(),
    'gp_version': subprocess.run(['gp', '--version-short'], check=True,
                                 text=True, capture_output=True).stdout.strip(),
    'git_head': subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=root, check=True,
                               text=True, capture_output=True).stdout.strip(),
    'inputs_sha256': {str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
                      for path in inputs},
}
Path('/opt/nist-seed/READY.json').write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
PY
