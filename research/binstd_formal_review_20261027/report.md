# BINSTD canonical-field Lean proof review

**Review date:** 2026-10-27 UTC

**Status at this packet revision:** current-head formal workspace gate in progress; independent-review protocol check failed for recorded schema reasons.

**Producer:** [PR #2484](https://github.com/isogeny-labs/crypto-autoresearcher/pull/2484), head `976b82bf60afda5e3d31c0da2704604ea2f2e5a5`.
**Frozen review plan:** [review-plan.yaml](review-plan.yaml) at `b95ccf3400f34441952930c6ca8b9a129661222d`.

## Question and scope

Do the two named Lean declarations prove the precise finite-field statements cited for `EXP-BINSTD-8bdf86`, and what can those statements say about the archived Stage 1 runner? This is a technical proof review. It does not record a new experiment, decide a hypothesis, or change an official evidence status.

The [input manifest](inputs.json) binds three Lean source files, both target specs, the frozen Stage 1 parameter JSON, Lean `v4.35.0-rc1`, and Mathlib revision `7fa22735254ddf7e11f119250a9f2d0352bc7c3a`. GitHub Actions run [40591043322](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/40591043322) checked out synthetic merge commit `07b26a4faaf30b84a6a189bde044e4356d1f2944`; it and the producer head have the identical **complete tree** `0278ef830e544ff7b04af3765c366bf5acb8a3cb` ([binding](machine/merge-binding.json)). This is source-tree equivalence, not an assertion that the running job has already finished.

## Per-claim assessment

| Claim | Machine status | Independent fidelity | Review outcome at this revision |
| --- | --- | --- | --- |
| `CryptoResearch.Binstd.factor8_irreducible_pair`: 313 and 471 are irreducible in `F₂[X]` | `not_verified` on the current head while the named workspace gate runs | `faithful_scoped` to the exact target and definitions | `inconclusive`; await current named receipt and protocol repair |
| `CryptoResearch.Binstd.canonicalFrobenius_order_and_minpoly`: Frobenius on canonical `GaloisField 2 17` has order 17 and minimal polynomial `(X+1)·factor8a·factor8b` | `not_verified` on the current head while the named workspace gate runs | `faithful_scoped` to the canonical-field target | `inconclusive`; await current named receipt and protocol repair |
| Archived runner implementation, full invariant-subspace classification, and Stage 1 yield | `not_verified` by these declarations | `partial` bridge only | `needs_revision` for any proposed concrete certification |

`not_verified` here means the fresh current-head machine evidence was unavailable at the stated observation, not that Lean refuted either statement. The two older [irreducibility](https://github.com/isogeny-labs/crypto-autoresearcher/blob/976b82bf60afda5e3d31c0da2704604ea2f2e5a5/docs/reports/2026-10-22-binstd-irred-lean/proof-verification.json) and [canonical Frobenius](https://github.com/isogeny-labs/crypto-autoresearcher/blob/976b82bf60afda5e3d31c0da2704604ea2f2e5a5/docs/reports/2026-10-22-binstd-canonical-frobenius/proof-verification.json) receipts record historical success and matching four hashes, but omit complete workspace and verifier inventories. They do not replace the fresh gate.

## Independent attack and controls

The [J1 report](reports/J1/report.md) inspected exact theorem types, coefficients, pinned Mathlib dependencies, target specs and verifier code. It found no circular premise or source claim mismatch. Its source-level fidelity verdict is `faithful_scoped`, while its machine verdict stayed inconclusive because the hosted workspace job was still building. The verifier explicitly builds each target module and audits the named theorem's transitive axioms; the global wrapper's floor could pass with a missing target marked undischarged, so both **named** receipts must be inspected.

The [J2 report](reports/J2/report.md) independently derived the polynomial and Frobenius results from the [blind input](blind-statements.json). Its [pre-unblinding seal](reports/J2/blind-seal.json) was written at 22:07:34 UTC, before reading producer files. Five artifact hashes still match, and rerunning the [calculation](reports/J2/blind-calculate.py) reproduces the sealed JSON exactly ([replay check](machine/blind-replay-check.json)). The independent method rejects the reducible control `X^8+1` and distinguishes Frobenius on `GF(2)` from the degree-17 claim. J2 additionally computed that modulus 131081 is irreducible and that its separately defined quotient Frobenius has order 17, minimal polynomial `X^17+1`, and factor-kernel dimensions 1, 8, 8. This is exact arithmetic for a constructed quotient, not formal certification of the archived Python execution.

The hosted dependency-free Lean controls [artifact](machine/controls/lean-controls.xml) reports **317 tests, zero failures, zero errors, zero skips**. Its smoke project uses Lean 4.22.0; the subject Mathlib workspace is pinned to 4.35.0-rc1. These controls test the instrument, not either subject theorem.

## Review-protocol result

The stock [`check_review_independence.py`](https://github.com/isogeny-labs/crypto-autoresearcher/blob/976b82bf60afda5e3d31c0da2704604ea2f2e5a5/tools/check_review_independence.py) returned **exit 1 and seven problems** on the precommitted plan and truthful attestations ([full output](machine/stock-independence-check.log)). The plan assigned actual Conductor IDs `T-608` and `T-609`; the checker accepts `TASK-*` identifiers. It also requires `blind_rederivation.quantity` and explicit `blind_from`, whereas the frozen plan points to the blind input's forbidden-path list and uses a custom before/after-seal contract. The checker cannot infer those fields or the permitted post-seal read phase. No reviewer ID or read list was rewritten to force a pass. This is a procedural defect in this round's machine-checkable independence contract, even though both reviewers attest to no sibling reads and the J2 pre-seal hashes verify. A corrected prospectively frozen round is required before calling the independence gate passed.

## Boundary to the historical runner

The [diagram](diagram.svg) shows the evidence boundary. J2 enumerates eight separate bridges: runner bit encoding to a quotient; a formal field proof for the degree-17 modulus; refinement of multiplication, reduction and squaring; canonical-field equivalence and Frobenius conjugacy; matrix/polynomial-evaluation refinement; complete invariant-subspace classification; nullspace/rank/constructor refinement; and exact archived-output binding. The structured constructor's loop omits the empty factor subset, so dimension-zero constructor coverage needs separate handling. Neither named theorem proves the recorded yield or a security/performance advantage. The archived runs remain subject to their own raw-artifact and execution-provenance review.

## Remaining actions

1. Finish hosted run 40591043322; save its exact-head workspace log and the two named proof receipts, inspect elaborated types and transitive axiom logs, and compare complete workspace/verifier inputs with the checked tree. Keep Lean/Lake dependency binaries inside their stated trust boundary unless independently rechecked.
2. Run a corrected, prospectively frozen independence round with valid task IDs and an explicit blind-source/phase contract. Preserve this failed checker output and both original reports unchanged.
3. Formalize and review concrete runner bridges before using the canonical theorem for archived implementation or yield claims; retain the existing bridge problem record.

No new trial, benchmark, cloud worker, database cutover, or scientific status change was performed for this review. The report figure is a scope diagram; no performance chart is invented from these proof results.
