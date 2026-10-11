#!/usr/bin/env python3
"""Install the admitted native artifact without altering its content bytes.

Run after the frozen runner's build phase. Its copyfile promotion preserves
bytes but omits execute permission. This explicit installation step corrects
that packaging metadata before any scientific process is launched.
"""
from pathlib import Path
import hashlib,json,stat
root=Path(__file__).resolve().parents[2]
run=root/'experiments/EXP-KIC-d9c828/runs/RUN-KIC-ba86d9'
binary=run/'build/native'
closure=json.loads((run/'source_closure.json').read_text())
before=hashlib.sha256(binary.read_bytes()).hexdigest()
if before!=closure['binary_sha256']:raise SystemExit('Refuse changed native bytes')
mode_before=stat.S_IMODE(binary.stat().st_mode)
binary.chmod(0o755)
if hashlib.sha256(binary.read_bytes()).hexdigest()!=before:raise SystemExit('Native content changed during install')
print(json.dumps({'binary_sha256':before,'mode_before':oct(mode_before),'mode_after':oct(stat.S_IMODE(binary.stat().st_mode)),'scientific_processes':0}))
