#!/usr/bin/env bash
set -euo pipefail
mkdir -p /logs/verifier
python - <<'PY'
import json
from pathlib import Path
Path('/logs/verifier/reward.json').write_text(json.dumps({'reward': 0.0}))
PY
python -m pytest -q /tests --junitxml=/logs/verifier/tests.xml
python -m polynomial_ml verify /app/output/run > /logs/verifier/verification.json
python - <<'PY'
import json
from pathlib import Path
receipt = json.loads(Path('/logs/verifier/verification.json').read_text())
assert receipt['verified'] is True
config = json.loads(Path('/app/output/run/config.json').read_text())
assert config['profile'] == 'quick' and config['seed'] == 20260904 and config['fit_seed'] == 0
assert config['steps'] == 1200 and config['action_timeout_seconds'] == 5.0
Path('/logs/verifier/reward.json').write_text(json.dumps({'reward': 1.0}))
PY
