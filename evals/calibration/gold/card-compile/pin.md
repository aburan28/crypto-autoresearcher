```yaml
schema: crypto.autoresearch.mechanical-task-card.v1
card_id: CARD-CAL-pin-01
experiment_id: CAL-pin
author_role: experiment-director
executor_role: executor-mechanical
kind: frozen_command
receipt: .tmp/calibration-run/pin/receipt.json
binds:
- path: evals/calibration/fixtures/emit.py
  sha256: 252b975e144942f7096380ee1656902d061989e56cb6500379341d65270438d6
commands:
- id: step-1
  argv:
  - python3
  - evals/calibration/fixtures/emit.py
  - print
  - pinned
  timeout_seconds: 30
  success_exit_codes:
  - 0
bus_address: executor-mechanical-cal
background: false
write_scope:
- .tmp/calibration-run/pin/
stop_when:
- The run command exits with status 2.
commit: b9e9c8c606bdb406a4805ad61259bf3c4bcaaa26
```

```yaml
specification_errors: []
```
