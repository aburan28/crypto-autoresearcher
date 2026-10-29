# Independent BINSTD printed-type and binding review

Task: TASK-20261028-68ff01. Conductor: T-750. Joint: J3-elaborated-type-binding. Review snapshot: dee666eb7d9d77f0bd922a7011b735d2401d93ce. Archival owner: TASK-20261028-6fe548.

**Verdict: holds for J3 under ordinary Lean/Lake trust.** The two printed types correspond to the two frozen narrow claims. All four named receipt digests, complete local workspace maps, verifier maps, exact specs and theorem/pin hashes reconcile. The supplemental ZIP matches the hosted artifact digest and both named members match the retained receipts byte for byte. Static inspection of every worker change found no concrete stale-success path for these targets with frozen inputs.

This is a source-informed independent review. It is not a new blind derivation, whole-round verdict, general approval of the changed verifier, or scientific promotion. No sibling report, sibling attestation, coordinator synthesis or PR discussion was read. A broad Git diff-stat displayed path metadata only; no sibling contents or outcomes were accessed. The complete 216-entry sources-read inventory and the distinction between textual review and byte hashing are in review_attestation.yaml and binding-check.json.

| Exact target | Machine status | Fidelity | Review outcome |
|---|---|---|---|
| CryptoResearch.Binstd.canonicalFrobenius_order_and_minpoly | passed, existing hosted named receipts | faithful_scoped | validated_scoped for J3 type/binding only |
| CryptoResearch.Binstd.factor8_irreducible_pair | passed, existing hosted named receipts | faithful_scoped | validated_scoped for J3 type/binding only |

The full new hosted run did **not** pass. Neither this table nor the joint verdict supplies the missing new kernel-control execution or the other reviewers' obligations.

## Exact types and mathematical correspondence

The supplemental canonical-field receipt prints:

~~~lean
CryptoResearch.Binstd.canonicalFrobenius_order_and_minpoly :
  orderOf (FiniteField.frobeniusAlgHom (ZMod 2) CryptoResearch.Binstd.CanonicalField17) = 17 ∧
    minpoly (ZMod 2) (FiniteField.frobeniusAlgHom (ZMod 2) CryptoResearch.Binstd.CanonicalField17).toLinearMap =
      CryptoResearch.Binstd.factor1 * CryptoResearch.Binstd.factor8a * CryptoResearch.Binstd.factor8b
~~~

The irreducibility receipt prints:

~~~lean
CryptoResearch.Binstd.factor8_irreducible_pair :
  Irreducible CryptoResearch.Binstd.factor8a ∧ Irreducible CryptoResearch.Binstd.factor8b
~~~

Both are closed, concrete declarations: neither has a parameter, implication, assumed conclusion, existential witness, adjustable field degree or unproved irreducibility hypothesis in its signature. Their source proofs compose previously proved lemmas. The local prime instances are discharged by decide; they are not open assumptions. The fields and polynomial coefficients are nontrivial mathematical structures supplied by the pinned library.

In Factorization.lean, F2 abbreviates ZMod 2, and the three definitions are:

| Constant | Exact polynomial | Binary coefficient mask |
|---|---|---|
| factor1 | X + 1 | 3 = 2¹ + 2⁰ |
| factor8a | X⁸ + X⁵ + X⁴ + X³ + 1 | 313 = 2⁸ + 2⁵ + 2⁴ + 2³ + 2⁰ |
| factor8b | X⁸ + X⁷ + X⁶ + X⁴ + X² + X + 1 | 471 = 2⁸ + 2⁷ + 2⁶ + 2⁴ + 2² + 2¹ + 2⁰ |

These match the exact archived stage1-ell89/admissible-phi-dims.json factors and the two frozen target specs. The source product theorem gives X¹⁷ + 1; over ZMod 2 this is X¹⁷ − 1. The degree-eight source proves the two degrees and applies the cyclotomic factor-degree criterion using orderOf(2 mod 17) = 8. No replacement polynomial is hidden behind either printed constant.

CanonicalField17 abbreviates GaloisField 2 17. At the pinned Mathlib revision 7fa22735254ddf7e11f119250a9f2d0352bc7c3a, GaloisField is the splitting-field construction over ZMod p, with the finrank result requiring n ≠ 0. Here n = 17 and the source proves that condition. The pinned finite-field Frobenius definition raises each element to the cardinality of the base field, hence to the second power here. Its order theorem gives the extension finrank, and its minimal-polynomial theorem concerns the underlying linear map. The printed order is formally the order of the algebra endomorphism under composition; its underlying function is the same Frobenius map in the claim. This is not a polynomial-basis implementation theorem. [Pinned GaloisField source](https://raw.githubusercontent.com/leanprover-community/mathlib4/7fa22735254ddf7e11f119250a9f2d0352bc7c3a/Mathlib/FieldTheory/Finite/GaloisField.lean), [pinned finite-field source](https://raw.githubusercontent.com/leanprover-community/mathlib4/7fa22735254ddf7e11f119250a9f2d0352bc7c3a/Mathlib/FieldTheory/Finite/Basic.lean).

The output is Lean's ordinary pretty-printed #check type, with named definitions still folded. Source inspection supplies those definitions; this is not raw kernel-AST comparison against an independently elaborated challenge. Both #print axioms outputs list exactly propext, Classical.choice and Quot.sound. No sorryAx, custom axiom or native-evaluation axiom appears in either named audit.

## Source and hosted binding

| Generation | Producer SHA | Hosted checkout SHA | Complete checkout tree |
|---|---|---|---|
| Original | 976b82bf60afda5e3d31c0da2704604ea2f2e5a5 | 07b26a4faaf30b84a6a189bde044e4356d1f2944 | 0278ef830e544ff7b04af3765c366bf5acb8a3cb |
| Supplemental | dda0d6efd97d3707081db183eb51ed1d1e6fe819 | 8ef2a271eb45801d12b431e85165b378d3f5176b | 527cf3f9b20e476060c4602e0260a5c223c12063 |

For each generation, the producer and hosted checkout have identical complete trees. The hosted logs identify the checkout commits. For each of the four receipts, I independently enumerated the relevant Git inputs and recomputed their SHA-256 values, rather than accepting the manifest's equality assertions.

Each workspace map contains 65 entries; each verifier map contains ten Python files. The workspace maps match across generations. The only verifier-map change is lean_worker.py, from c71b99044f4a8b566cc033f721d8cbe71951664f7574c384dc97e8c4ad4614c4 to f1c583ad7a92c4bba9472129581eab18a48aa32ad86de9d4b44d7c71d4de796c. The supplied worker patch is byte-identical to the exact Git diff.

CryptoResearch.lean is absent from both Git trees, as the inspected workflow and rebuild_formal_root implementation expect. Reconstructing its header and sorted imports from the 49 exact source modules gives 7e7b4c1e80a867b2c747a134b977c41f722149f11f4337b6b1a53f0ff70f155e, matching all four receipts. An initial checker assumed a stored root and stopped with KeyError; the corrected derivation is retained explicitly in binding-check.json. No source was changed or regenerated on disk.

The receipt verifier map covers orchestration/formal/*.py, not every CI entry point. I therefore separately bound and inspected tools/verify_formal_targets.py, tools/rebuild_formal_root.py and .github/workflows/lean-verification.yml against both exact checkout trees. The batch entry point newly wraps its target loop in verification_session(); the CI change adds the session test file to kernel controls. These pipeline changes are not silently described as being covered by the ten-file receipt map.

The new artifact has ID 12794504637, size 511286 bytes and SHA-256 3cc4147523995952f57a2f10f38c7ab931ee74bb3eb19d5e65478f3edc70f540. That digest agrees among the local ZIP, live GitHub artifact metadata and hosted upload log. Both named ZIP members exactly equal the retained new receipts. I did not read unrelated ZIP members or independently retrieve the old ZIP; original receipt bytes were checked against their frozen hashes, exact Git inputs and original hosted named-result logs.

Original hosted run 40591043322 reports 89 verified, zero not verified, zero infrastructure failures, with its workspace job and kernel-control job successful. Supplemental run 40636717165 reports 88 verified, zero not verified and one infrastructure failure: scoped-odd-torsion-translation encountered a toolchain-version mismatch. Its separate kernel-controls job failed during Lean setup and its test step was skipped. The new BINSTD named successes remain narrow evidence; the old passing run cannot certify later cache changes. [Original run](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/40591043322), [supplemental workspace job](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/40636717165/job/122645329426).

## Cache and failure-path review

The worker diff introduces a ContextVar-backed dictionary whose scope is one verification_session invocation. Its finally block clears the dictionary and restores the prior token. The key includes resolved repository and workspace, runner identity and timeout; the retained runner object also prevents object-ID reuse. The cached values are the project build and project audit, not a named theorem result.

The input snapshot compares all local Lean/configuration inputs collected by workspace_inputs, including hidden source directories other than .git/.lake, plus all ten verifier files. A changed snapshot evicts the prior common result. Persistent edits during verification are detected after the project audit and again after the named audit, and cause a blocked result. The outer CLI additionally compares spec, theorem, toolchain, manifest, workspace and verifier inputs before writing a successful receipt.

For every target, including a cache hit, the worker rescans forbidden constructs, runs lake build +Module and generates a fresh TargetAudit source. That source requires the exact name to resolve to thmInfo, collects transitive axioms, fails on anything outside the three-name allowlist, then prints the type and axiom list. A failed target build returns before success; a failed named audit leaves target_ok false. A prior successful project audit cannot turn that target into machine_verified. Failed project builds and audits are not inserted as successful cache entries. Common success may remain cached after a target failure, which is sound for this scope because the next target still has its own fresh build and audit.

Exceptions and timeouts propagate to the CLI infrastructure-failure receipt and the gate's nonzero exit. Every early return and the post-audit mutation checks were examined. The canonical receipt does not claim common-check reuse; the irreducibility receipt does, consistent with sorted execution order. Static control-flow cases are recorded individually in binding-check.json.

I inspected the new test source for session expiry, changed helper/manifest/verifier/runner/timeout, failed project audits and mutation during target auditing. Those tests were not executed in this review. Their existence is not passing test evidence, and the new hosted kernel-control job did not execute them. No new Lean build, mocked workload, benchmark, experiment, cloud job or service action was launched.

The snapshots do not cover dependency/build artifacts under .lake, environment changes or transient edits restored between comparisons. The claimed use is a frozen hosted input tree under ordinary Lean/Lake trust. I found no observed exploitation or specific stale-success result in these receipts; I do not infer a general adversarial authentication guarantee.

~~~mermaid
flowchart LR
    A["Exact producer and checkout trees"] --> B["65 workspace inputs including regenerated root"]
    A --> C["10 verifier inputs plus separately bound gate and CI"]
    B --> D["Two named hosted checks"]
    C --> D
    D --> E["Printed types and axiom lists"]
    E --> F["J3 source-informed correspondence"]
    G["GitHub artifact digest"] --> H["ZIP and named member byte checks"]
    H --> D
~~~

## Trust, provenance and remaining obligations

The toolchain pin is Lean 4.35.0-rc1; the receipts identify compiler commit 86c6347c75e39ec18c40e25ed2143b71a6e04a0a. All nine dependency revisions are retained in binding-check.json. I verified manifest bytes and consulted the pinned Mathlib definitions. I did not independently inspect the hosted installed dependency Git states or reconstruct their binary artifacts. No lean4checker, comparator or independent kernel checker was run.

The primary Lean documentation treats statement correspondence, axiom checks and proof rechecking as distinct obligations; this report retains those boundaries. GitHub artifact identity improves provenance, while a consistent receipt alone cannot authenticate execution or defeat a malicious toolchain. [Lean proof validation](https://lean-lang.org/doc/reference/latest/ValidatingProofs/), [Lean axiom dependencies](https://lean-lang.org/doc/reference/latest/Axioms/).

The dispatcher confirmed an independent collaboration.spawn_agent session with fork_turns none and reasoning_effort xhigh, without a model override. The requested policy is review-adversarial. The exact served model was not exposed or probed here, so model_verified is false. Conductor's default card route says implementer/cli/medium; it is preserved as a metadata discrepancy, not substituted for the actual dispatch provenance. No sibling outcomes were communicated by the dispatcher.

The initial T-750 lease expired at 16:00:32 UTC. At 16:01:07 the card was observed ready, with no competing owner; I reclaimed that same card as epoch 3, lease 8fc4f67d-e041-4b91-98e6-714a03ceba3b, before finishing this report and sealing. The binding JSON and attestation had been written by the preceding command. The short lapse is disclosed rather than backdated away.

The frozen supplemental handoff prohibits local Lean execution and assigns exactly four review files. Accordingly, machine status here relies on retained hosted named checks, and the report includes a source-linked diagram but no new PDF. The Coordinator must archive this seal, compose the complete review using the original required reports, run the whole-round independence check without giving this reviewer sibling outcomes, and supply any packet-level PDF required by the broader workflow.

Still open outside J3: passing new verifier runtime-control evidence; installed dependency cleanliness and stronger kernel rechecking; the canonical-to-historical-runner representation bridge; invariant-subspace classification; constructor validation; empirical yield or performance claims. No hypothesis, scientific status, historical receipt or original evidence was changed.
