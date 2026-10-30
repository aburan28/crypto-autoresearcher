import contextlib,io,json,subprocess
from pathlib import Path
from tools import progress_metrics as m
m.REPO=Path.cwd()
ref=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
b=io.StringIO()
with contextlib.redirect_stdout(b):m.p256_factor_base_checks(ref,"2026-10-01")
r=json.loads(b.getvalue());assert r["value"]==8;assert r["source"].endswith(ref)
print(json.dumps(r))
