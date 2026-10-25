# Graph trial adapter

`trial_driver.py` runs one graph arm under the repository trial supervisor. It
accepts either an already prepared input/manifest pair or a scheduled `--arm-key`
plus the three committed root files and stratum commitment; the latter mode
materializes the input into the run directory and records the materializer
receipt. The supervisor supplies an empty output directory, a frozen trial
plan, and a live claim. Scientific mode passes the Coordinator's admission to
`preparation/execute_graph_prepared.py`. A `ectd.graph-study-admission.v1`
record also requires `--binding` from the graph input materializer; the wrapper
replays the scheduled row and binding, while the checker independently repeats
that validation against the frozen Coordinator decision, authorized execution
stage, specification, source commit, and exact input. Legacy per-arm admission
records do not take `--binding`. `--control` is limited by that wrapper to 128
public targets.

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
  --admission ADMISSION --binding PREPARED_BINDING \
  --collector COLLECTOR --count-verifier COUNT --out RUN_DIR \
  --watchdog-seconds 1800 --memory-gib 4
python3 trial_check.py --run-dir RUN_DIR --input INPUT \
  --prepared-manifest PREPARED_MANIFEST --admission ADMISSION \
  --binding PREPARED_BINDING
```

Use `--memory-gib 8` for P37 and the contract's confirmed/finalist limits when
those stages are frozen. A relocated archive can be checked with copied input
and manifest files; `--collector` and `--count-verifier` accept rebuilt binaries
only when their SHA-256 hashes match the original receipt. The recorded command
and original paths remain in the manifest. This adapter does not implement
arm selection, exact sampling intervals, matrix solve, same-point ECDLP timing,
or matched rho timing. Those are separate frozen stages of the study.

The eight-target implementation control and its visual record are under
`controls/attempt-1/`. `controls/attempt-2/` retains a failed attempt where the
control-only path imported PyYAML before checking its mode, plus a successful
retry after the admission import was made lazy. The retry's independent checker
accepted the public P29 input and matched its ordered-count output. It found
zero useful targets in those eight fixed targets. These controls do not estimate
graph-wide yield.

The [study-plan compiler](../graph_plan_20261023/build_discovery_plan.py)
builds one discovery trial per scheduled arm and passes the repository's trial
plan loader in an integration control. This adapter and compiler do not yet
implement the fresh confirmation and finalist solve schedules, and their
approval/admission sequence remains unresolved.
