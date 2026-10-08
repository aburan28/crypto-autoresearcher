# Implementation notes — EXP-BINSTD-f124db (TASK-20261001-66c370)

## Scope

Stages 0–2 only, under write_scope `experiments/EXP-BINSTD-f124db/{runs,implementation,stage0,stage1,stage2}/`.
Observations only. No hypothesis/experiment/idea status edits. No AUXIN. No Bedrock.
No break claim and no composite-k'-is-weaker security ordering.

## Declared methods

| Stage | Method |
| --- | --- |
| 0 | Pure integer arithmetic: `n(c)=d/gcd(c,d)`; `tau` by divisor enumeration; compare to d11575 inherited stated periods in a separate column. |
| 1 | Schoolbook `F_{2^4}` (`gf2n.py`/`curve.py` adapted from EXP-BINSTD-9d1b8e / EXP-CERTBIN-e94b27). Ordinary curve search under seed `20260922`. Coefficient orbit size under `σ_c: x↦x^{2^c}`. |
| 2 | **Declared AS-level instrument:** magic-number `m=deg(Ord_σ(γ))` for `γ∈{B,√B}` on `F_{16}`; genus candidates `{2^{m-1}, 2^{m-1}-1}`. Full GHS cover construction not built (not required for the H1 agreement test at this toy). |

## Protocol deviations

1. **MMT literature retrieval** not attempted; Stage 0 records `literature_unrecovered: true` with provenance remaining `recalled` (optional in the frozen protocol).
2. **Stage 2 cost table** written as `observational_open` with `charged_time`/`charged_memory` null / `not_executed` — frames the OPEN comparison only; no IC was charged (protocol allows optional open cost).
3. **Unused minted run IDs** `RUN-BINSTD-e3a77e`, `RUN-BINSTD-d540d2`, `RUN-BINSTD-fa242c` were allocated then not needed (three stage runs sufficed; maximum_runs=24 not exceeded).
4. Run packages were written while the tree was dirty (implementation present but not yet committed); manifests record `dirty: true` and the pre-archive `HEAD`. No run directory was overwritten.

## Non-deviations of note

- Stage N waited for `stage{N-1}/`.
- Every run manifest uses `result.certificate.kind: none`.
- `instrument_unavailable.yaml` was **not** written because the Ord instrument succeeded (`genus-agreement.yaml` is the decisive Stage 2 path).
- Timeouts/crashes: none.

## Seeds / randomness

- Stage 0: deterministic.
- Stage 1: seed `20260922` (frozen primary).
- Stage 2: deterministic given Stage 1 curve.
