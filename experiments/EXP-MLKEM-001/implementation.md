# EXP-MLKEM-001 implementation

Exact-arithmetic audit of ePrint 2026/1022 (Thorns) transfer to ML-KEM toy
controls. Code lives under `implementation/`; pinned estimator sources under
`vendor/pq-crystals-security-estimates/` at commit
`75c26949a902ca297b181375bfb7cfaf22cce784`.

## Entry point

```bash
python3 experiments/EXP-MLKEM-001/implementation/run_experiment.py
```

Optional `--only RUN-MLKEM-00N` re-runs a single planned run.

## Modules

- `fips_semantics.py` — CBD weights, FIPS ties-up vs Python half-even Compress/Decompress
- `exact_dp.py` — generating-function convolutions and joint n=2 law
- `direct_enumerator.py` — independent successive-convolution engine and compressed scalar enum
- `pinned_estimator_port.py` — faithful import of pinned `Kyber_failure` / `proba_util`
- `test_controls.py` — control helpers
- `run_experiment.py` — four-run packaging

## Inference

Requested policy `research-sol-max`; resolved model `cursor-grok-4.5-high` with
`fallback_used: true` per user direction.
