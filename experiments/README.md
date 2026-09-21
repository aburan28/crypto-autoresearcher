# Experiments

One directory per approved experiment contract, laid out per
`docs/evidence-and-reproducibility.md`:

```text
experiments/EXP-<AREA>-NNN/
  specification.yaml   Frozen contract (approved by Coordinator)
  amendments/          Versioned protocol amendments
  implementation.md    What was built, and deviations from protocol
  analysis.md          Observation / Comparison / Inference / Limitation
  runs/RUN-*/          Immutable run records (manifest, command,
                       environment, stdout, stderr, raw result)
```

Run directories are immutable: never edited, never deleted. Defective runs
are marked invalid in their manifest and superseded by new run IDs.
