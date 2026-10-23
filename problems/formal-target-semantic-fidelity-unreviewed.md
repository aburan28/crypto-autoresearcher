# Formal target build success does not establish claim fidelity

- **Status:** `open`
- **Kind:** semantic-review and experiment-to-proof coverage gap
- **Affected work:** [83-target declaration audit](../docs/reports/2026-10-23-formal-target-inventory/report.md), [formal target specs](../formal/targets/README.md), [Semaev nonzero-fall problem](semaev-degree-two-fall-nonzero-bridge.md), and [ten-lead model bridge](ten-lead-proof-scope-and-artifact-access.md)
- **Next action owner:** Coordinator to assign independent semantic reviewers by claim; formal research lane to repair exact mismatches
- **Last updated:** 2026-10-23

## Problem

We cannot conclude that every tested cryptanalytic claim is proved merely because the 83 target files at the pinned audit commit compile. A Lean theorem can be true while encoding a narrower predicate, a different finite model, or assumptions absent from the experiment. No complete, independently reviewed map from every historical experiment and claimed inference to a semantically faithful theorem and source-bound execution record is established here.

The target corpus is heterogeneous. Some files prove generic algebraic facts, some prove exact finite instances, and some experiments report measurements rather than a theorem. The required obligation for each claim depends on its actual statement, input model, and inference tier; counting files or axioms cannot supply that interpretation.

## Evidence and uncertainty

- **Observed:** At main `d513b75233e1eb58b24c753ff51675b83b284b44`, all 83 target specs have theorem files; all 82 main-workspace names resolve, the main workspace builds, and its 652 theorem declarations use only standard axioms. The separate scoped target builds and passes a zero-axiom audit. The [receipt](../docs/reports/2026-10-23-formal-target-inventory/evidence/audit.json) binds sources and logs.
- **Observed after that audit:** Main `969e051e204ab8c5668157ebeeb00734a1f074b1` has 84 target specs and 150 tracked formal files. The two added files are the `DkExactBatch5` theorem and its target spec. Its named theorem is conditional on three large factors being prime; its spec explicitly does not prove curve trace identity, the endomorphism-ring identification, or primality of the curve field/order. PR #2492 passed its applicable hosted checks, but the `lean-verification` workflow is `disabled_manually`, so those checks did not build the new Lean module. This 83-target batch receipt does not include the new name. A fresh whole-workspace build and batch audit are required for a current-main declaration count.
- **Derived or proved:** These checks establish kernel acceptance and the declared theorem names' existence. They do not entail scientific claim fidelity.
- **Known counterexample to a shortcut:** The [Semaev problem](semaev-degree-two-fall-nonzero-bridge.md) documents a true trace-cancellation theorem whose historical uniform first-fall interpretation fails for checked nonzero-target toy draws. This shows why independent statement-to-claim review is necessary.
- **Suspected explanation:** Unknown for the remaining targets. The current audit did not classify each target's semantic fit or experiment coverage.
- **Missing capability:** A claim-by-claim coverage map with independent source reading, exact theorem hypotheses, model bridges, execution provenance, and reviewed handling of counterexamples and measured-only results.
- **What this evidence does not establish:** It does not invalidate all proofs or experiments, imply a hidden performance regression, or show that every target needs a stronger theorem. It does not support a clean all-corpus validation claim.

## What would unblock it

- [ ] For each claim chosen for promotion or dashboard display, bind its original source and experiment/run identifiers to the exact Lean theorem, assumptions, model and source hashes; identify any inference that remains empirical or unproved.
- [ ] Obtain independent semantic-fidelity review with a counterexample or known-false control for each claim-changing proof chain; record precise mismatches and additive corrections without rewriting frozen artifacts.
- [ ] Replay source-bound experimental controls and verify execution provenance for performance claims under the existing run and progress-fidelity rules; use a current-head ledger and dashboard integrity check before asserting corpus-wide readiness.

These conditions are needed for claim-level acceptance. A broader statement about every historical experiment would additionally require an explicit scope inventory, since observations need provenance and controls rather than an artificial theorem.

## Next discriminating step

- **Action or proof obligation:** Review the Semaev degree-two first-fall target against its frozen measurement, corrected Boolean parity rows, finite equation bridge, explicit witness, and seven nonzero-target degree-three exceptions. Record an additive claim correction if the model is confirmed.
- **Inputs and controls:** Use the original target and immutable draw archive, the source-hash-bound corrected replay, the direct 256-assignment equation check, and a known-false uniform first-fall conclusion as a proves-too-much control.
- **Execution limits and stop condition:** Review this finite claim first; do not generalize it to all Semaev systems or ECDLP cost. If reviewers find a model mismatch, record its exact definition and keep the broader claim open. Any new run follows its frozen protocol and admission rules.
- **Outcomes and next actions:** A faithful finite counterexample supports a scoped additive correction; a mismatch requires a repaired bridge; missing source or reviewer evidence keeps the claim pending. Use the result to define a repeatable coverage-map entry for the next target.
- **Recheck trigger:** Independent review, target or source change, or a new current-main formal and execution-integrity audit.

## Resolution and history

- 2026-10-23: Opened after the 83-target declaration audit. The build and axiom gates passed, but no all-target semantic or experiment-to-proof coverage conclusion was drawn. Unresolved.
- 2026-10-23: Rechecked the exact 83-target receipt after syncing the inventory PR with main `969e051e204ab8c5668157ebeeb00734a1f074b1`. The archived receipt still passes on its pinned commit. Current main adds one conditional `DkExactBatch5` target, so the historical count is not promoted to a current-head all-target claim.
