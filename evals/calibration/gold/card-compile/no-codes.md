```yaml
schema: crypto.autoresearch.mechanical-task-card.v1
card_id: CARD-CAL-no-codes-01
experiment_id: CAL-no-codes
author_role: experiment-director
executor_role: executor-mechanical
kind: frozen_command
receipt: .tmp/calibration-run/no-codes/receipt.json
binds:
- path: evals/calibration/fixtures/emit.py
  sha256: 252b975e144942f7096380ee1656902d061989e56cb6500379341d65270438d6
commands: []
bus_address: executor-mechanical-cal
background: false
write_scope:
- .tmp/calibration-run/no-codes/
stop_when:
- The run command exits with status 2.
```

```yaml
specification_errors:
- the design gives no exit code value; it is not defaulted
```
