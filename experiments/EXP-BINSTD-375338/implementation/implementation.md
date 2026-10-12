# Implementation notes — EXP-BINSTD-375338 / TASK-20261001-ff051b

## Scope

Stages 0–1 only, per `specification.yaml` and handoff. Observations only;
no H/EXP/IDEA status edits; no Stage 2+; no per-instance leaf-ratio arms.

## Layout

| Path | Role |
|------|------|
| `implementation/gf2n.py`, `curve.py` | Field/curve arithmetic adapted from EXP-CERTBIN-e94b27 |
| `implementation/arithmetic.py` | ord_n(2), stable dims, census, tests (a)–(e), Z/ℓ replica |
| `implementation/runpack.py` | Immutable run packages (`certificate.kind` ∈ {none, decomposition}) |
| `implementation/stage0_run.py` | Stage 0 census + fixtures + orbit restatement |
| `implementation/stage1_run.py` | Stage 1 BIN-TOY-K19 / K17-STABLE / NULL-RC1 / Z/ℓ |

## Cells

- **BIN-TOY-K19:** `y²+xy=x³+1` over `F₂[t]/(t¹⁹+t⁵+t²+t+1)`; `#E=4·130873` (recomputed match);
  `V={deg<10}`; exhaustive m=2 census; 50 targets by increasing `(x,y)`.
- **BIN-TOY-K17-STABLE:** Koblitz `A=B=1` over `t¹⁷+t³+1`; `V=ker g(τ)` for a
  degree-8 factor of `Φ₁₇` (dim 8 ∈ stable set).
- **NULL-RC1:** same n=19 field, `A=97044` (non-`F₂`), `B=1`.
- **Z/ℓ:** size-512 random windows; σ ↔ multiplication by Frobenius scalar `μ=41811`;
  seeds `20261001`…`20261005`.

## Protocol deviations / anomalies (recorded, not discarded)

1. **Test (e) operationalization (RUN-BINSTD-8c9916 → RUN-BINSTD-822306).**
   First K19 run applied per-coordinate orbit-min on `x1`. Corrected run uses
   lex-min among the n Frobenius images of the ordered pair (tuple-orbit).
   Both kept; primary citation is `RUN-BINSTD-822306`.

2. **Test (e) median fraction vs pre-registered band.**
   MEASURED `solutions_lost_under_canonical_constraint=11>0` but
   `solutions_lost_median_fraction=0.0` outside `[0.7,1.0]*(1-1/19)`.
   Cause: `V={0..511}` elements are preferentially orbit-lex-minimal
   (~92.5% of V), so the canonical filter deletes far fewer than the free-action
   model `1-1/n`. Unexpected vs the numeric band; equivariance axes (a)(b)
   and controls still recorded separately. No post-hoc threshold retuning.

3. **NULL-RC1 first attempt (RUN-BINSTD-5e64fc) invalid_measurement.**
   Secondary `tuple_probe` counted `x=0` points. With `B∈F₂`, `(0,√B)` is fixed
   by σ and lies on every `E` with that `B`. Corrected run `RUN-BINSTD-4150f4`
   excludes `x=0`; primary not-on-curve criterion was already satisfied on the
   first attempt.

4. **Unused minted IDs** `RUN-BINSTD-b5424b`, `f452e0`, `15825b` were allocated
   with `--check` but not consumed (under `maximum_runs`).

## Commands

```text
python3 experiments/EXP-BINSTD-375338/implementation/stage0_run.py
python3 experiments/EXP-BINSTD-375338/implementation/stage1_run.py --arm all
# corrected arms after protocol fixes:
python3 experiments/EXP-BINSTD-375338/implementation/stage1_run.py --arm k19
python3 experiments/EXP-BINSTD-375338/implementation/stage1_run.py --arm rc1
```
