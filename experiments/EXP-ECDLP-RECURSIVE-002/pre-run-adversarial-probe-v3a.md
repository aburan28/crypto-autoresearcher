# Pre-run adversarial probe: fast detached descendant

- recorded at: `2026-07-17T21:46:47Z`
- platform: `macOS-15.6-arm64-arm-64bit-Mach-O`
- Python: `3.13.1`
- runner SHA-256: `783cee98bccb61c8afc026b2dbb8f010539506403c0867e079f6b963e7139b04`
- status: `NEGATIVE RESULT` for the sampling-only v3a resource boundary

## Hypothesis

The process-table sampler observes and charges a child that immediately enters
a new session while its direct parent prints valid JSON and exits.

## Probe

Twelve sequential `_run_child` calls used a wall limit of 0.08 seconds. Each
parent launched `python -c 'time.sleep(0.4)'` with `start_new_session=True`,
printed `{"valid": true}`, and exited immediately. A 0.45-second pause between
trials allowed every escaped child to terminate before the next trial.

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 - <<'PY'
import json, sys, tempfile, time
from pathlib import Path
from crypto_autoresearcher.runner import _run_child

rows = []
parent = (
    "import json,subprocess,sys; "
    "subprocess.Popen([sys.executable,'-c','import time; time.sleep(0.4)'],"
    "start_new_session=True); "
    "print(json.dumps({'valid':True}))"
)
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    for i in range(12):
        result = _run_child(
            [sys.executable, '-c', parent],
            root,
            0.08,
            1024**3,
            10,
            root / f'o{i}',
            root / f'e{i}',
        )
        rows.append({
            'i': i,
            'timed_out': result.timed_out,
            'wall': round(result.wall_seconds, 4),
            'cpu': round(result.cpu_seconds, 4),
            'quiescent': result.group_quiescent,
            'rc': result.return_code,
        })
        time.sleep(0.45)
print(json.dumps(rows, indent=2))
PY
```

## Exact result

| trial | timed out | measured wall seconds | measured CPU seconds | reported quiescent |
|---:|---|---:|---:|---|
| 0 | false | 0.0588 | 0.0272 | true |
| 1 | false | 0.0630 | 0.0298 | true |
| 2 | false | 0.0642 | 0.0276 | true |
| 3 | false | 0.0615 | 0.0276 | true |
| 4 | false | 0.0732 | 0.0285 | true |
| 5 | false | 0.0588 | 0.0269 | true |
| 6 | false | 0.0647 | 0.0279 | true |
| 7 | false | 0.0639 | 0.0276 | true |
| 8 | false | 0.0618 | 0.0280 | true |
| 9 | false | 0.0686 | 0.0288 | true |
| 10 | false | 0.0631 | 0.0274 | true |
| 11 | false | 0.0669 | 0.0272 | true |

All 12 escaped the sampling-only boundary. The existing slower-parent test was
therefore not a sufficient falsification test.

## Narrow conclusion and repair

`NEGATIVE RESULT`: polling ancestry and process-group membership cannot support
the claim that every adversarially detached descendant is observed. This does
not affect the frozen single-process arithmetic programs. Canonical locked runs
are repaired by forbidding child creation with `RLIMIT_NPROC=0` under a bound,
non-root effective UID. Sampling remains defense in depth and is not described
as a kernel containment boundary.

The regression is
`test_locked_run_forbids_instant_detached_descendant` in
`tests/test_runner.py`.
