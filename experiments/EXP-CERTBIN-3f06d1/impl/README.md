# EXP-CERTBIN-3f06d1 implementation

Copied from `experiments/EXP-CERTBIN-4e92d7/impl/` (the reviewed Stage-1
instrument, REVIEW-CERTBIN-20260923-c51f07) and generalised as
`experiments/EXP-CERTBIN-3f06d1/specification.yaml` (version 1) states, under
TASK-20260924-9f15a2. Every change is listed in `impl-provenance.json` (source
sha256, unified diff, reason), written by `make_provenance.py`. The Stage-1
impl is never imported or edited. Pure Python 3.11 + numpy 2.4.6; no compiled
helper, no Sage, no scipy.

## Modules

| file | status | responsibility |
|---|---|---|
| `gf2n.py`, `curve.py`, `elim.py`, `stats.py` | unchanged | field, curve, THE SOLVER / replays, descriptive statistics |
| `macaulay.py` | changed | descent with the cell's V basis (default: Stage-1 polynomial basis) |
| `oracles.py` | changed | oracle A over the cell's basis (V.coord membership), witnesses, rational flag |
| `families.py` | changed | phase 1 per cell: curve / V, points, per-cell C-SELF, C-TR, every family's references and targets, both oracles, x(2E) classes |
| `engine.py` | changed | phases 2-6 (as Stage 1) plus pivot-column hashes, C-FORMS scalar path, reference forms self-check, a_k in hazard tables, code-path hashes |
| `analysis.py` | rewritten | phase 9: M1, M1f, M1k (hull, Sigma_H), M2R/TS1R, M-R4, M3, M4, controls, INV-1..7, RR-1..10 |
| `report.py` | rewritten | phase 9 artifacts, independent raw-result recomputation, manifest |
| `driver.py` | changed | three cells, phases 1-9, checkpoints, --phase determinism, --resume |
| `selftest.py` | changed | generic C-SELF + C-FIX (phase 0); `cell_selftest` for the per-cell items |
| `make_trial_plan.py` | rewritten | trial-plan-v1.json from the specification alone |
| `vspace.py` | new | V basis, linear-algebra membership, S_V draw, F_2 linear algebra on ints |
| `x2e.py` | new | [#E/2] x(2E) test, enumeration, brute-force doubling image, C-TR |
| `xstats.py` | new | exact bands, tails, Fisher test, Clopper-Pearson (RC-3) |
| `cprov.py` | new | C-PROV on the Stage-1 cell |
| `make_provenance.py` | new | writes impl-provenance.json |

`../verifier/verify_cert.py` is the separate PS0' verifier; it imports nothing
from this directory.

## Commands (in order)

```sh
python3 experiments/EXP-CERTBIN-3f06d1/impl/cprov.py --stage1-run experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05 --out experiments/EXP-CERTBIN-3f06d1/runs/RUN-CERTBIN-6d92b5/cprov.json
python3 experiments/EXP-CERTBIN-3f06d1/impl/make_trial_plan.py --spec experiments/EXP-CERTBIN-3f06d1/specification.yaml --run-id RUN-CERTBIN-6d92b5 --out experiments/EXP-CERTBIN-3f06d1/trial-plan-v1.json
# the frozen command (selftest && driver phases 1-6)
# the determinism command (phase 7, separate process)
# driver ... --resume          (phase 8: PS0' certificates, cells.json)
# the verify command           (separate process)
# driver ... --resume          (phase 9)
```

The exact commands as run are in the run directory's `command.txt`.
