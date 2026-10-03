# EXP-BINSTD-38f216 implementation notes

Executor packet for Stages 0–2 only. Hypothesis status is not decided here.
`EXP-BINSTD-a3fa22` was not started. No commit, push, or approval was made.
`scientific_execution_authorized` was already true on `origin/main` and was not edited.

## Code

- `field_curve.py`: characteristic-2 field and short Weierstrass arithmetic used by the census and the n=17 cells.
- `run_exp.py`: Stage 0 table, Stage 1 census, Stage 2 window measurement.

Checkout: detached worktree at `c1a6a657daca5f3289999f0a4bf608104fe2b66c` (`origin/main`). Dirty because these artifacts are uncommitted.

## Inference

`requested_policy: executor-implementation`. This process did not expose a probe-verified model id. `resolved_model_id: null`, `model_verified: false`, `fallback_used: true`, `degraded_allowed: false`. No Bedrock endpoint was contacted. A local adapter resolve printed `anthropic:claude-sonnet-5`; that string is not recorded as the model that produced these artifacts.

## Protocol deviations

1. `ROOT` was first `parents[2]`, so the audit path and the run directory were under `experiments/experiments/` and `experiments/analysis/`. `RUN-BINSTD-7f7a5c` crashed with `FileNotFoundError` and is kept. `ROOT` is `parents[3]` in the source that wrote the later runs.
2. `load_audit_rows` treated audit detail lines (`m=176=2`) as curve rows. `RUN-BINSTD-9eccc2` crashed with `ValueError` and is kept. The parser then skips a second field that is not all digits. That fix is in the source used by `RUN-BINSTD-913e88`. Stage 1 (`RUN-BINSTD-2770de`) had already imported the module and does not read the audit table.
3. The successful Stage 0 write (`RUN-BINSTD-913e88`) happened after Stage 1. The contract asks for Stage 0 artifacts committed before a scientific run. This session was forbidden to commit, so the Stage 0 files exist and are uncommitted.
4. Before any official Stage 2 run, the orbit-loop expansion was changed so each unordered `{P, P+T}` representative pair emits `A+B` and `A+B+T`, each with multiplicity 2. A debug window on the Koblitz cell then matched the exhaustive pair-sum multiset. The locked unit-cost ratio formula was not edited after that window.
5. `stage2/metrics-summary.json` was assembled after both Stage 2 runs by copying scalars out of `koblitz-summary.json` and `rc1-summary.json`. The run directories were not rewritten.
6. The driver records `certificate.kind: none` and `status: completed_valid` when the process finishes. It does not flip that status when `certificate_multiset_equality` is false. On RC-1 (`RUN-BINSTD-d51065`) the orbit-loop expanded multiset differed from the exhaustive multiset on all 20 windows (true 0, false 20). On Koblitz (`RUN-BINSTD-4f0feb`) the same comparison was true on all 20 windows. Those counts are the recorded comparison, not a verdict.
7. Koblitz covered-set check in `RUN-BINSTD-4f0feb`: `covered_vw=5338`, `covered_fw=10012`, `tau_bar_inverse_image=10012`, `set_equality=false`. The x-coordinate tau-bar identity on that cell has `failed=0` (`checked=131172` affine, `checked=65586` on the subgroup sample).
8. Handoff text that pointed at the portfolio branch was not followed. The user instruction was to start from `origin/main` and not to check out or merge `origin/cursor/coordinate-portfolio-ed0c`. `research_dispatch.py --claims refs` on `BATCH-8c7af6` exited with an archive-ancestry error against this detached HEAD and did not show a live claim on `TASK-20260930-22e38a` or `TASK-20260930-2cc13f`.

## What was not done

Stages 3–5 were not run. No AUXIN, GFPN, or QSP receipt was rerun. Crashed run directories were not deleted.
