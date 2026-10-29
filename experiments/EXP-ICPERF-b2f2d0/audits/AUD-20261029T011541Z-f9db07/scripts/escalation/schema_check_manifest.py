#!/usr/bin/env python3
"""Read-only run-schema check of one run manifest with tools/validate_ledger.py.

Escalation verification for AUD-20261029T011541Z-f9db07; never a trial, writes
nothing. Mirrors tools/experiment_execution.py:manifest_schema_errors (a fresh
validate_ledger.Ctx and check_run on one path). argv[1] = directory holding the
validate_ledger.py to use (current tools/ or a scratch copy of a historical
revision); argv[2] = manifest path relative to the repository root (cwd).
"""
import json
import sys

sys.path.insert(0, sys.argv[1])
import validate_ledger  # noqa: E402

ctx = validate_ledger.Ctx(set())
validate_ledger.check_run(sys.argv[2], ctx)
print(json.dumps({"validator_dir": sys.argv[1], "manifest": sys.argv[2],
                  "errors": [e.split(": ", 1)[-1] for e in ctx.errors]}, indent=1))
