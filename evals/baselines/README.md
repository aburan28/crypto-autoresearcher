# Pinned baselines

A baseline is a past eval record that later runs are measured against:

```sh
python3 -m orchestration.eval baseline --source evals/results/<name> \
                                       --out evals/baselines/<suite>.json
python3 -m orchestration.eval run --suite evals/suites/<suite>.yaml \
                                  --trials 20 --baseline evals/baselines/<suite>.json
```

Move a baseline deliberately (`--replace`) and only after a change you believe
in. A baseline that drifts silently measures nothing — every run compares
favourably against the run just before it while the absolute level falls.

Each baseline carries the fingerprint of the harness that produced it, so
`run --baseline` can report which tunable inputs changed since.
