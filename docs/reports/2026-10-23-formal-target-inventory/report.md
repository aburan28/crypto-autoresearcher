# Current-main formal target declaration audit — 2026-10-23

**Status:** pinned build and declaration audit passed for `crypto-autoresearcher` main `d513b75233e1eb58b24c753ff51675b83b284b44`. This is an operational proof-integration check. It does not independently establish that every Lean statement matches its scientific claim or that every archived experiment is valid.

## Scope and method

The current main tree contains 83 `formal/targets/*.yaml` specs and 83 corresponding theorem files. The [checker](check_target_audit.py) binds all 148 tracked formal files and all target specs to their SHA-256 manifests. It regenerates the exact [Lean batch source](TargetBatchAudit.lean) from the specs, rejects a changed source or a changed theorem name, and verifies the [batch log](evidence/main-target-batch.log) against every target name and Lean's allowed axioms.

The main workspace, pinned to Lean 4.35.0-rc1 and the committed Mathlib manifest, completed [8,975 build jobs](evidence/main-build.log). Its [project audit](evidence/main-axiom.log) examined 652 theorem declarations and found only `propext`, `Classical.choice`, and `Quot.sound`. The batch `#check` and `#print axioms` resolved all 82 main-workspace target names: 74 use only those standard axioms and eight use none. A separate pinned Lean 4.22.0 [scoped build](evidence/scoped-build.log) and [zero-axiom audit](evidence/scoped-axiom.log) checked the remaining target. The [machine-readable receipt](evidence/audit.json) records the exact source and evidence hashes.

![Formal target audit gates](target-gates.svg)

The [editable diagram](target-gates.dot) shows the two toolchains and the validation boundary. The checker rejected a changed target audit source, an injected `sorryAx`, and optimized Python that would disable assertions; the [negative-control receipt](evidence/negative-controls.json) records those exits. The same source tree was checked before any new Semaev witness module was added, so these counts describe the named main commit only.

At the later main commit `969e051e204ab8c5668157ebeeb00734a1f074b1`, the formal tree has 84 target specs and 150 tracked files. `DkExactBatch5.exact_discriminants` is the additional target; its spec states explicit primality and model assumptions. Its merged PR #2492 passed hosted checks, while this batch source and receipt remain bound to the earlier 83-target tree. The [open problem](../../../problems/formal-target-semantic-fidelity-unreviewed.md) records the current-head audit and semantic-review obligations.

## What remains

File presence, kernel acceptance, and allowed axioms are necessary technical checks. They do not prove that the statements faithfully encode all 83 target claims, independently validate source measurements, or cover the thousands of archived experiment directories. The repository's separate per-target verifier and independent semantic review remain the claim-level gates; this one-pass audit does not replace them. The [open semantic-fidelity problem](../../../problems/formal-target-semantic-fidelity-unreviewed.md) names the exact coverage and review obligations. The earlier [2026-10-20 formal validation report](../2026-10-20-formal-validation/report.md) recorded 62 machine-verified targets and four then-undischarged targets at its own source commit. This current audit establishes the later declaration inventory and build, without rewriting that dated result.

No benchmark value, canonical scientific graph, performance dashboard, or official hypothesis state changed. The dashboard publication gate and its unresolved ledger integrity warnings are tracked separately in the [Pages preflight report](../2026-10-23-pages-publication-preflight/report.md).
