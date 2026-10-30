# Correction to `CLOSURE.md`: the success condition used the wrong exponent

**Status: analysis note, not an evidence record.** `sota_delta`: zero.
Claim tier: **toy**. Record: `ledger/corrections/CORR-20261024-b2a799.yaml`.
Instrument: [`tools/smallroot_reach_hg.py`](../../tools/smallroot_reach_hg.py);
tests: [`tests/test_smallroot_reach_hg.py`](../../tests/test_smallroot_reach_hg.py).

This is a computation by one agent, not an experimental run. The pre-registered
audit of the same question, `EXP-ECDLP-64fa3d` (hypothesis `H-ECDLP-4b54a2`), has
produced no run; nothing here substitutes for it, and its `PRED-1`/`PRED-2`
(`epsilon_HG(n,d) = 2/(d(n+1))`, `epsilon_TOOL(2,1) = 4/3`) are reproduced by
this note's closed forms. Per AGENTS.md rule 12, a result that contradicts a
closure needs independent `review-breakthrough` review at `max`; it has not had it.

## What was wrong

`tools/smallroot_reach.py` compares `prod X_i^{s_i}` with `p^{s_p}`, where
`s_p = sum_k (t-k) |M_k \ M_{k+1}|` is the exponent of `p` in `det(L)`. The
Howgrave-Graham criterion is `det(L) < p^{t·dim L}`, so the comparison exponent
is `t·dim − s_p`. Because the shift sets are nested,

> `t·dim − s_p = Σ_{k≥1} |M_k|`, and in the limit **ε_HG = ε_TOOL / n**.

The two agree at `n = 1`, which is the only case the committed test checks against
a theorem (Coppersmith, reach exactly `1/d`), so the calibration could not see it.

Independent evidence that the committed convention is the wrong one:

| check | TOOL (committed) | HG (this note) | truth |
| --- | --- | --- | --- |
| hand instance `n=1, d=2, t=1`, basis `{p, pX, f}`, `det = p²X³ < p³` | `X < p^{2/3}` | `X < p^{1/3}` | `p^{1/3}` |
| full box `n=2, d=1`, one equation | ε = 4/3 | ε = 2/3 | ε ≤ 1 (information bound) |
| Boneh–Durfee `xy + Ax + 1`, x-shifts only | accepts δ ≈ 0.74 | δ < 1/4 | δ < 1/4 |
| full-box closed form | `2n/(d(n+1))` | `2/(d(n+1))` | |

## Corrected numbers

| quantity | `CLOSURE.md` | corrected |
| --- | --- | --- |
| `ε(S_3)`, extended, `t→∞` | 0.8408 | **0.2803** (full box 0.25) |
| `ε(S_4)`, extended, `t→∞` | 0.4137 | **0.1034** (full box 0.10) |
| sparsity gain `S_3`, `S_4` | ×1.12, ×1.03 | ×1.12, ×1.03 (unchanged: both sides scale by `1/n`) |
| best margin at `m = 4` | −0.0481 at `(4,2)` | **−0.6086** at `(4,2)`; `(4,0)` is −0.6187 |
| best margin over `m ≤ 32` | −0.0481 at `(4,2)` | **−0.5161** at `(32,0)` |
| `ε_required` | unchanged | unchanged (demand side was not wrong) |

`S_3` was also measured directly at `t = 8, 16` (Richardson in `1/t`): 0.278,
within 1% of the identity value 0.2803.

## Statements in `CLOSURE.md` that change

- **§1** "this rises toward 1 as `n` grows — more variables with smaller bounds is
  the configuration that helps lattices": **false.** At fixed `d`, ε_HG falls as
  `n` grows (`2/(d(n+1))`). That was the stated reason the family was worth checking.
- **§4** "the margin widens monotonically in every direction": **false.** At `w = 0`
  the margin *improves* with `m`, from −0.619 (`m=4`) to −0.516 (`m=32`), tending to
  −1/2 as demand falls to 1/2 and supply to 0. The family is dead by at least 0.5
  everywhere in range; the best row is no longer `m = 4`.
- **§5** the 0.0481 gap and the "monotone in the same parameter" statement: the gap
  is ≈ 0.6, and supply/demand are not monotone in the same parameter for `w = 0`.
- **§6.1** the case for rank-`r ≥ 2` GAPs rested on `n/(n+1) → 1`; the corrected
  shape is `1/(n+1)`, which *decreases* with `n`. That rationale no longer holds.
- **§6.3** "the margin to beat is now a number: 0.048" → about 0.6, i.e. a roughly
  3× gain in reach on the `(4,2)` block, not 6%.
- **§5 "obstruction" scope line** keeps its qualifications. Nothing here shows the
  optimal-shift question is formally closed: Jochemsz–May extended is one strategy.

## What this does not change

- Pollard rho remains the best known; no speedup is claimed or implied.
- The demand side (`eps_required`) and the block-input accounting are unchanged.
- Nothing here retires `IDEA-20260808-486ae2` and siblings: statuses belong to the
  Coordinator. Dependents that quote the superseded numbers are listed in the
  correction record and were left as written.

## Reproduction

```bash
python3 -m pytest -q tests/test_smallroot_reach_hg.py tests/test_smallroot_reach.py
python3 tools/smallroot_reach_hg.py --compare
```
