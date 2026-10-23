# Graph trial adapter

`trial_driver.py` runs one already prepared graph arm under the repository trial
supervisor. The supervisor supplies an empty output directory, a frozen trial
plan, and a live claim. Scientific mode passes the Coordinator's graph-arm
admission to `preparation/execute_graph_prepared.py`; the wrapper checks the
three-root seed mode, exact quota, source commit, and all admission bindings.
`--control` is limited by that wrapper to 128 public targets.

The driver writes `manifest.yaml`, `raw-result.json`, driver logs, and an
`attempt/` directory containing the phased execution receipt, logs and raw
collector/count outputs. It exits nonzero when the wrapper refuses or fails.
The checker reruns the prepared-input group-law check and the independent
relation/count/rank verifier. It compares the receipt's phase hashes and the
driver's artifact hashes. With `--reference-run-dir`, it first checks that run
independently, then compares targetwise triples, ordered counts, useful counts,
and rank metrics for a `graph_transport` or `u2_transport` arm against the
source `low_x` arm.

Example trial-plan commands, after a Coordinator has frozen and approved the
experiment and issued an admission for this exact arm:

```text
python3 trial_driver.py --input INPUT --prepared-manifest PREPARED_MANIFEST \
  --admission ADMISSION --collector COLLECTOR --count-verifier COUNT --out RUN_DIR \
  --watchdog-seconds 1800 --memory-gib 4
python3 trial_check.py --run-dir RUN_DIR --input INPUT \
  --prepared-manifest PREPARED_MANIFEST --admission ADMISSION
```

Use `--memory-gib 8` for P37 and the contract's confirmed/finalist limits when
those stages are frozen. A relocated archive can be checked with copied input
and manifest files; `--collector` and `--count-verifier` accept rebuilt binaries
only when their SHA-256 hashes match the original receipt. The recorded command
and original paths remain in the manifest. This adapter does not implement
arm selection, exact sampling intervals, matrix solve, same-point ECDLP timing,
or matched rho timing. Those are separate frozen stages of the study.

The eight-target implementation control and its visual record are under
`controls/attempt-1/`. These controls do not estimate graph-wide yield.
