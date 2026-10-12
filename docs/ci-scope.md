# CI inputs and runtime budgets

Required workflows start on every pull request and merge-group event. Their
checks complete even when a change has no relevant inputs. Workflow-level path
filters must not be added to `validate`, `progress-fidelity`, or
`lean-verification`: a filtered required workflow can leave a merge waiting for
an absent check.

`.github/scripts/ci_scope.py` uses a complete local Git diff. It compares a PR's
current test-merge parent, preserves deleted and renamed source paths, and fails
if the diff cannot be resolved. Unknown paths run the software gates; missing
scope outputs never authorize a skip.

| Changed inputs | Work retained |
| --- | --- |
| Root documentation, Markdown/PDF/images under `docs/` and paper sources | Merge hygiene; existing required contexts complete without software setup |
| Ledger, experiment, knowledge, coordination, input and research records | Ledger/integrity validation and relevant corpus checks; changed queues render individually |
| `claims/` | Progress-fidelity portfolio validation, unit controls and dashboard |
| Software, tests, dependencies, agent instructions, workflows, unknown paths | Full software suite, runtime controls and corpus/static gates |
| Formal proofs, targets, runtime/verifier or toolchain inputs | Real Lean build, forbidden-construct and theorem-specific axiom audits |
| Formal tests or smoke controls | Kernel controls; no Mathlib proof-workspace build |

The software matrix retains its existing Python-version and shard check names.
The `ledger-and-harness` aggregate requires a successful scope/hygiene check and
every applicable component. A detector error, cancellation, unexpected skip or
missing output fails validation. Full software/corpus compatibility also runs
weekly and on manual dispatch.

Software validation jobs have 20-minute execution limits; the real Lean proof
workspace and bounded autofix ladder have 25-minute limits. These limits exclude
runner queue delay. Scheduled scientific evaluation and literature ingestion
have separate research budgets and are not merge checks.

Lean fetches only its package/runtime/tests and exact source documents named by
formal targets. Its cache contains pinned Mathlib dependencies, keyed by the
manifest and toolchain; project proofs and verification receipts are rebuilt.
Progress fidelity checks out only claims and its standard-library checker/tests.

`sync-branches` owns the six-hour branch-sync schedule. `sync-main` is a manual
compatibility entry point sharing the same concurrency group; report mode is the
default. Groebner checks run once per PR revision and once after a relevant merge,
not again for a push to the same PR branch.

Branch-protection settings require authenticated access to inspect. Preserve the
existing `ledger-and-harness`, `progress-fidelity`, runtime/shard and Lean check
names when configuring protection. Public workflow/run inspection does not
confirm which of them the repository currently requires.
