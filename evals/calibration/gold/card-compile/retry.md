```yaml
schema: crypto.autoresearch.mechanical-task-card.v1
card_id: CARD-CAL-retry-01
experiment_id: CAL-retry
author_role: experiment-director
executor_role: executor-mechanical
kind: frozen_command
receipt: .tmp/calibration-run/retry/receipt.json
binds:
- path: evals/calibration/fixtures/emit.py
  sha256: 252b975e144942f7096380ee1656902d061989e56cb6500379341d65270438d6
commands:
- id: step-1
  argv:
  - python3
  - evals/calibration/fixtures/emit.py
  - exit
  - '0'
  timeout_seconds: 60
  success_exit_codes:
  - 0
  retry:
    exit_codes:
    - 75
    max_attempts: 2
bus_address: executor-mechanical-cal
background: false
write_scope:
- .tmp/calibration-run/retry/
stop_when:
- The run command exits with status 2.
```

```yaml
specification_errors: []
```
