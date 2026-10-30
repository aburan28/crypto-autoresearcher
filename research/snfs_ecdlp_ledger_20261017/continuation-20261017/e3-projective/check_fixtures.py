"""Run the finite deterministic engineering fixtures and record literal output."""
from pathlib import Path
import datetime
import hashlib
import json
import platform
import subprocess
import sys
import sage.version


folder = Path(__file__).resolve().parent
names = ["test_section_encoding", "test_kernel_recovery"]
argv = [sys.executable, "-m", "unittest", "-v", *names]
started = datetime.datetime.now(datetime.timezone.utc).isoformat()
result = subprocess.run(argv, cwd=folder, text=True, capture_output=True)
record = dict(scope="Deterministic software fixtures only; no research-grid trial",
              started_at=started, finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
              argv=argv, returncode=result.returncode, python=platform.python_version(),
              sage=sage.version.version,
              source_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in sorted(folder.glob("*.py"))},
              stdout=result.stdout, stderr=result.stderr,
              fixture_cases=13, scientific_trials=0, independent_scientific_review=False,
              limitations=["No blind solver, certified MW basis, coverage measurement or speed claim.",
                           "Earlier failed development imports/tests are retained separately."])
with (folder / "fixture-checks.json").open("x") as handle:
    json.dump(record, handle, indent=2)
    handle.write("\n")
print(result.stdout, end="")
print(result.stderr, end="")
raise SystemExit(result.returncode)
