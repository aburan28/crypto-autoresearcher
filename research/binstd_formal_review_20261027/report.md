# BINSTD canonical-field Lean proof review

**Review date:** 2026-10-27 UTC

**Status at this packet revision:** the exact-tree hosted formal gate passed, and the corrected prospective independence check passed through a documented, hash-pinned serialization adapter. The frozen packet still lacks a separately emitted elaborated-type printout, so its overall review outcome remains `inconclusive`.

**Producer:** [PR #2484](https://github.com/isogeny-labs/crypto-autoresearcher/pull/2484), head `976b82bf60afda5e3d31c0da2704604ea2f2e5a5`.
**Frozen review plan:** [review-plan.yaml](review-plan.yaml) at `b95ccf3400f34441952930c6ca8b9a129661222d`.

## Question and scope

Do the two named Lean declarations prove the precise finite-field statements cited for `EXP-BINSTD-8bdf86`, and what can those statements say about the archived Stage 1 runner? This is a technical proof review. It does not record a new experiment, decide a hypothesis, or change an official evidence status.

The [input manifest](inputs.json) binds three Lean source files, both target specs, the frozen Stage 1 parameter JSON, Lean `v4.35.0-rc1`, and Mathlib revision `7fa22735254ddf7e11f119250a9f2d0352bc7c3a`. GitHub Actions run [40591043322](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/40591043322) completed successfully. It checked out synthetic merge commit `07b26a4faaf30b84a6a189bde044e4356d1f2944`; it and the producer head have the identical **complete tree** `0278ef830e544ff7b04af3765c366bf5acb8a3cb` ([binding](machine/merge-binding.json)).

## Per-claim assessment

| Claim | Machine status | Independent fidelity | Review outcome at this revision |
| --- | --- | --- | --- |
| `CryptoResearch.Binstd.factor8_irreducible_pair`: 313 and 471 are irreducible in `F₂[X]` | `passed`: exact-tree named build and transitive axiom audit | `faithful_scoped` to the exact target and definitions | Narrow claim supported; full packet `inconclusive` on missing type printout |
| `CryptoResearch.Binstd.canonicalFrobenius_order_and_minpoly`: Frobenius on canonical `GaloisField 2 17` has order 17 and minimal polynomial `(X+1)·factor8a·factor8b` | `passed`: exact-tree named build and transitive axiom audit | `faithful_scoped` to the canonical-field target | Narrow claim supported; full packet `inconclusive` on missing type printout |
| Archived runner implementation, full invariant-subspace classification, and Stage 1 yield | `not_verified` by these declarations | `partial` bridge only | `needs_revision` for any proposed concrete certification |

The [hosted inventory](machine/hosted-40591043322/artifact-inventory.json) records 89 machine-verified receipts, including both named target [receipts](machine/hosted-40591043322/). GitHub artifact `12774634972` has SHA-256 `4a558a174bbcb8f8f13f27cd9c96d45a8868c67a3fd20fbf6928aa766acbb99f`. The named receipt hashes are `79d19b913b3c223d80a96e932967735ea52f6a9adc37ef7d21075d15a25f6ed1` and `ef7c01fa93f5f7f81c9e07fc8f77a3600338db1166fd7682399d5811858965ef`. J1 independently downloaded the artifact and matched both receipts byte-for-byte. Each binds all 65 workspace inputs and 10 verifier inputs to the complete producer tree, including an independently reconstructed generated root. The audit reported 713 theorems with only the standard-axiom allowlist `propext`, `Classical.choice`, and `Quot.sound`; it did not separately print each target's exact axiom list. The two older receipts remain historical and do not replace this fresh gate.

## Independent attack and controls

The prospective [J1 source/verifier report](../binstd_formal_review_round2_20261027/reports/TASK-20261027-b17d01/report.md) inspected exact source signatures, coefficients, pinned Mathlib dependencies, target specs, verifier code, and the fresh receipts. It found no circular premise or source claim mismatch. Its machine verdict is `passed` and source fidelity verdict `faithful_scoped` for both narrow declarations. The source signatures are quoted in the report; they are not a separately emitted elaborated-type printout. The verifier explicitly builds each target module and audits its named theorem's transitive axioms; the global wrapper's floor could pass with a missing target marked undischarged, which is why the two named receipts matter.

The prospective [J2 blind report](../binstd_formal_review_round2_20261027/reports/TASK-20261027-b17d02/report.md) independently derived the polynomial and Frobenius results from a single isolated statement ([input binding](../binstd_formal_review_round2_20261027/blind-input-binding.json)) with SHA-256 `2bbf336b088ff099546bcc3b5f3612f439ba2b7aa69a5007c6d02fcdb590f664`, with no producer or sibling read through delivery. Its eight sealed hashes pass. Rerunning its [exact script](../binstd_formal_review_round2_20261027/reports/TASK-20261027-b17d02/check_exact.py) reproduced raw output SHA-256 `606465241f032b7e1d924f92235df0a49d277a7eeef367355767f5c72ded73fd`. Exhaustive division rejects all 30 possible low-degree monic factors for each degree-eight polynomial, and its field-root-bound argument proves Frobenius order 17 and minimal polynomial `X^17+1`. The false controls `X^8+1` and `GF(2)` were rejected. An optional quotient calculation does not certify archived runner code.

The hosted dependency-free Lean controls [artifact](machine/controls/lean-controls.xml) reports **317 tests, zero failures, zero errors, zero skips**. Its smoke project uses Lean 4.22.0; the subject Mathlib workspace is pinned to 4.35.0-rc1. These controls test the instrument, not either subject theorem.

## Review-protocol result

The first frozen plan and truthful attestations returned **exit 1 and seven problems** from the stock [`check_review_independence.py`](https://github.com/isogeny-labs/crypto-autoresearcher/blob/976b82bf60afda5e3d31c0da2704604ea2f2e5a5/tools/check_review_independence.py) ([original output](machine/stock-independence-check.log)); this historical failure remains intact. A [prospectively frozen corrected plan](../binstd_formal_review_round2_20261027/review-plan.yaml) assigned valid external `TASK-*` refs and a truly blind J2. Its original J2 YAML used a top-level mapping and detailed `{path, role, sha256}` read records, while the stock checker expects a `review_attestation` wrapper and a path-string list. Both direct checker failures are preserved ([raw](machine/round2-independence-check.log), [nested only](machine/round2-nested-only-check.log)). A deterministic [adapter](machine/round2-j2-attestation-adapter-v2.py), pinned to the sealed J2 YAML SHA, wraps and projects only the read-path field while retaining the full records separately; it does not change any reviewer claim. The stock checker returned **exit 0** with J1's original attestation and that [projected J2 representation](machine/round2-projected-independence-check.log). The raw J2 YAML itself is not directly checker-compatible. This is a passed checker on a disclosed serialization adapter, not a claim that the original pair directly passed.

## Boundary to the historical runner

The [diagram](diagram.svg) shows the evidence boundary. J2 enumerates eight separate bridges: runner bit encoding to a quotient; a formal field proof for the degree-17 modulus; refinement of multiplication, reduction and squaring; canonical-field equivalence and Frobenius conjugacy; matrix/polynomial-evaluation refinement; complete invariant-subspace classification; nullspace/rank/constructor refinement; and exact archived-output binding. The structured constructor's loop omits the empty factor subset, so dimension-zero constructor coverage needs separate handling. Neither named theorem proves the recorded yield or a security/performance advantage. The archived runs remain subject to their own raw-artifact and execution-provenance review.

## Remaining actions

1. Emit and archive separate elaborated `#print`/`#check` output for both named declarations on an exact pinned tree, then reconcile it with the source signatures. The current hosted receipts and source review do not satisfy that frozen documentation item. Lean/Lake dependency binaries and `lean4checker=false` remain within the ordinary toolchain trust boundary.
2. Formalize and review concrete runner bridges before using the canonical theorem for archived implementation or yield claims; retain the existing bridge problem record. The full invariant-subspace classification and Stage 1 yield remain unproved by these declarations.

No new trial, benchmark, cloud worker, database cutover, or scientific status change was performed for this review. The report figure is a scope diagram; no performance chart is invented from these proof results.
