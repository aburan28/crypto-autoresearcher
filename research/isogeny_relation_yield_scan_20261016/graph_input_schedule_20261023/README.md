# Schedule-bound graph input materializer

`materialize.py` prepares one discovery arm from the independently checked
8,206-arm candidate schedule. It checks the full schedule digest, verification
receipt, certified graph digest, three distinct root commitments, source hashes,
fixed arm identity and exact target quota before writing a new directory. Its
`check` action recomputes the binding from a saved directory, including the
same-stratum coefficient stream. The output `binding.json` is a preparation
artifact; it is not a Coordinator admission or a relation run.

After the Coordinator freezes new scientific roots and per-stratum commitments,
the mechanical producer calls:

```text
python3 materialize.py prepare --arm-key P37-v0000-low_x \
  --base-root-file BASE_ROOT --target-root-file DISCOVERY_ROOT \
  --verifier-root-file VERIFIER_ROOT --commitment P37_COMMITMENT \
  --output-dir NEW_EMPTY_PATH
python3 materialize.py check --arm-key P37-v0000-low_x \
  --base-root-file BASE_ROOT --target-root-file DISCOVERY_ROOT \
  --verifier-root-file VERIFIER_ROOT --commitment P37_COMMITMENT \
  --output-dir NEW_EMPTY_PATH
```

`NEW_EMPTY_PATH` must not exist before `prepare`; the output is write-once.
The Coordinator's separate arm admission must then bind `prepared.txt`,
`manifest.json`, the collector and verifier binaries, source commit, and the
trial limits. The admitted arm runs through the repository `run` route. This
script implements discovery input preparation only; selection, confirmation,
matrix solve and matched rho remain separate stages of the full study.

[Full-quota implementation control](report.md) used public control roots at
P37 vertex zero, with the native, `u2_transport`, and `graph_transport` bases
as separate arms. The [machine check](control/checks.json) and raw prepared
inputs are retained. They are excluded from the scientific target stream.
