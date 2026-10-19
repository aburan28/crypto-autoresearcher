# Runbook conformance example: toy ECDLP by baby-step giant-step

**Status: example, not research.** `EXAMPLE-toy-ecdlp-bsgs` exercises every
part of the runbook machinery (`docs/runbook-execution.md`,
`tools/runbook.py`) on an instance small enough to run in seconds. It tests no
hypothesis and supports no claim; nothing here enters the ledger.

## What it runs

Twelve seeded discrete logarithms on `y^2 = x^3 + 3x + 20` over GF(1048571),
a curve of prime order `n = 1047689` (`curve.json`), each solved by
baby-step giant-step with `m = isqrt(n - 1) + 1 = 1024`, plus two controls:

- `c-known-k`, a positive control: the logarithm 123456 is planted and must be
  returned exactly;
- `c-off-curve`, a negative control: `Q` is not on the curve and the solver
  must refuse it rather than return a logarithm.

`solve.py` is the trial driver. `check.py` is an independent checker that
shares no code with it (projective rather than affine arithmetic, Fermat
inversion): it re-derives each instance from the prescribed seed, re-verifies
`k*G = Q`, and checks the operation count against what the prescribed
algorithm must take for that `k` (`giant_steps = k / m + 1`, `baby_steps = m`).

Seeds are `int(sha256("toy-ecdlp-bsgs/seed/<i>")[:8], 16)` for `i = 1..12`,
written into `trial-plan.json` when it was frozen.

## Why `solved` is a validity condition

A runbook's `validity` block checks that an output is admissible, never what
it concludes, so it normally cannot require an instance to be solved: in a
capped search an unsolved trial is an observation. Baby-step giant-step is
different. With `m` baby steps and `m` giant steps every exponent `k < m * m`
is reached, because `k = (k / m) * m + k % m` with both digits below `m`, and
here `n <= m * m`. An on-curve instance that comes back unsolved is therefore a
defect of the implementation, not a result. That counting identity is the Lean
obligation `CryptoResearch.Runbook.BsgsCoverage.coverage`
(`formal/targets/runbook-example-bsgs-coverage.yaml`); the runbook's
`S03-lean-coverage` step verifies it where Lean is installed and records
`unavailable` where it is not.

## Run it

```sh
python3 tools/runbook.py lint examples/runbooks/toy-ecdlp-bsgs/runbook.yaml
python3 tools/runbook.py run  examples/runbooks/toy-ecdlp-bsgs/runbook.yaml
python3 tools/runbook.py verify examples/runbooks/toy-ecdlp-bsgs/runbook-sessions/<session-id>
python3 tools/runbook.py audit  examples/runbooks/toy-ecdlp-bsgs/runbook-sessions/<session-id>
```

The session id is fixed in the runbook, and a finished session is never run
again, so the committed session under `runbook-sessions/` is the reference run
and `tests/test_runbook.py` re-verifies it. To run the example yourself, copy
the repository (or run the tests, which do it in a temporary copy).
