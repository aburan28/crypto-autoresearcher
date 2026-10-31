```yaml
schema: crypto.autoresearch.mechanical-task-card.v1
card_id: CARD-CAL-fresh-01
experiment_id: CAL-fresh
author_role: experiment-director
executor_role: executor-mechanical
kind: frozen_command
receipt: .tmp/calibration-run/fresh/receipt.json
binds:
- path: evals/calibration/fixtures/emit.py
  sha256: 252b975e144942f7096380ee1656902d061989e56cb6500379341d65270438d6
commands:
- id: step-1
  argv:
  - python3
  - evals/calibration/fixtures/emit.py
  - write
  - .tmp/calibration-run/fresh/session/log.txt
  - start
  timeout_seconds: 120
  success_exit_codes:
  - 0
bus_address: executor-mechanical-cal
background: false
write_scope:
- .tmp/calibration-run/fresh/
stop_when:
- The run command exits with status 2.
must_not_exist:
- .tmp/calibration-run/fresh/session/
```

```yaml
specification_errors: []
```
