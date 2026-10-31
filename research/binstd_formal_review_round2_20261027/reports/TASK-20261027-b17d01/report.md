# J1 source and verifier fidelity — prospective round

**External task:** TASK-20261027-b17d01. **Conductor card:** T-616.
**Reviewer:** /root/binstd_j1_formal, continuing the earlier source-informed J1 session.
**Plan:** research/binstd_formal_review_round2_20261027/review-plan.yaml,
committed at 6c7a66bd22; SHA-256
`c2b6ca7d10f80585780583a5a812578e1af9d6000854812ea66777b3878f4d2a`.
The on-disk plan matches those committed bytes. No first-round J2 or round-two J2 report was read.

**J1 verdict: holds for the two named source/verifier fidelity claims.**
Both declarations have fresh, correctly named hosted machine evidence on the exact producer source tree, and their source types faithfully express the frozen narrow claims. The required separate elaborated-type printout is still absent; this report does not claim that every requirement of the full review packet is complete. The full packet outcome remains `inconclusive` with respect to that missing documentation gate.

| Named declaration | Machine status | Fidelity | J1 finding |
| --- | --- | --- | --- |
| CryptoResearch.Binstd.factor8_irreducible_pair | passed, fresh hosted named build/audit | faithful_scoped | Source and target match; no circular hypothesis or axiom exception found |
| CryptoResearch.Binstd.canonicalFrobenius_order_and_minpoly | passed, fresh hosted named build/audit | faithful_scoped | Fixed canonical field and genuine Frobenius linear map; target matches |

## Fresh hosted evidence and exact input binding

[Hosted run 40591043322](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/40591043322) has completed successfully. The [formal workspace job](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/40591043322/job/122495145332) ran its build and per-target verification steps; the scope-exclusion step was skipped. The log records **89 verified, zero not verified, zero infrastructure, zero undischarged**, and explicitly lists both subject declarations as verified. Relevant original log lines are preserved in [hosted-verification-excerpt.log](hosted-verification-excerpt.log).

I independently downloaded artifact **12774634972** through the GitHub connector, read the ZIP in memory, and compared its digest with both the hosted upload log and GitHub artifact metadata. Its SHA-256 is:

```text
4a558a174bbcb8f8f13f27cd9c96d45a8868c67a3fd20fbf6928aa766acbb99f
```

It contains 89 entries. Both named receipt members are byte-identical to the coordinator's extraction at /var/tmp/binstd-formal-run-40591043322. [artifact-binding.json](artifact-binding.json) preserves the comparison. Their hashes are:

| Receipt member | SHA-256 |
| --- | --- |
| binstd-x17-degree-eight-irreducible.json | 79d19b913b3c223d80a96e932967735ea52f6a9adc37ef7d21075d15a25f6ed1 |
| binstd-canonical-frobenius-minpoly.json | ef7c01fa93f5f7f81c9e07fc8f77a3600338db1166fd7682399d5811858965ef |

The receipts correctly record checkout commit `07b26a4faaf30b84a6a189bde044e4356d1f2944`, GitHub's synthetic PR merge. Run metadata identifies producer head `976b82bf60afda5e3d31c0da2704604ea2f2e5a5`. I checked the complete Git tree identity again: both are `0278ef830e544ff7b04af3765c366bf5acb8a3cb`. The run's source-commit identifier is therefore distinct but its entire source tree equals the frozen producer.

I compared the **complete key sets and values** of both receipts' input maps, not only their target-file hashes:

- Each workspace map contains **65 entries**: all 64 tracked local Lean/pin/Lake configuration inputs selected by the verifier, plus its generated CryptoResearch.lean root.
- I reconstructed that root independently from the exact committed generator header and sorted list of **49 main-library modules**. Its SHA-256 is `7e7b4c1e80a867b2c747a134b977c41f722149f11f4337b6b1a53f0ff70f155e`, matching both receipts.
- All **10 verifier Python inputs** match the corresponding producer-tree bytes, including the worker, CLI, input-binding helper, target parser and root generator.
- All task/result identities, all four target/specification/toolchain/manifest hashes, the recorded Lean version, and the exact named audit messages match. There are no extra, missing or mismatching workspace inputs.

The exact expected maps and per-check results are in [binding-check.json](binding-check.json). This is a read-only Git/source/receipt comparison, not a local Lean rebuild. The referenced Stage-1 JSON is outside the workspace map; its identity is separately pinned by the frozen review input manifest and exact producer tree. A target specification's source-path string alone would not bind that file's content.

Both receipts report Lean **4.35.0-rc1**, compiler commit `86c6347c75e39ec18c40e25ed2143b71a6e04a0a`. The manifest pins Mathlib to `7fa22735254ddf7e11f119250a9f2d0352bc7c3a`. Each fresh audit log contains:

```text
axiom audit: 713 theorem(s), all standard axioms only
```

and the correct target-specific success line. The receipts report successful builds, successful axiom audits, no forbidden constructs, no blocking reason and no infrastructure failure. The standard-axiom allowlist is `propext`, `Classical.choice`, `Quot.sound`; the success log establishes membership in that allowlist, not a separately printed exact axiom list for each declaration.

## Theorem types and semantic checks

The [irreducibility source declaration](https://github.com/isogeny-labs/crypto-autoresearcher/blob/976b82bf60afda5e3d31c0da2704604ea2f2e5a5/formal/CryptoResearch/Binstd/Irreducibility.lean#L92) is:

```lean
theorem factor8_irreducible_pair :
    Irreducible factor8a ∧ Irreducible factor8b
```

The [definitions](https://github.com/isogeny-labs/crypto-autoresearcher/blob/976b82bf60afda5e3d31c0da2704604ea2f2e5a5/formal/CryptoResearch/Binstd/Factorization.lean#L22) fix the coefficient field to `ZMod 2`, and the polynomial supports to `{8,5,4,3,0}` and `{8,7,6,4,2,1,0}`. Their binary masks are exactly 313 and 471; `factor1 = X + 1` has mask 3. This agrees with the frozen JSON and [target specification](https://github.com/isogeny-labs/crypto-autoresearcher/blob/976b82bf60afda5e3d31c0da2704604ea2f2e5a5/formal/targets/binstd-x17-degree-eight-irreducible.yaml).

There are no external theorem hypotheses assuming irreducibility or an arbitrary field instance. The proof supplies primality of 2 and 17, order 8 for 2 modulo 17, both polynomial degrees, and divisibility into the seventeenth cyclotomic polynomial. Cancellation of `X + 1` includes its nonzero proof. The pinned [Mathlib cyclotomic criterion](https://github.com/leanprover-community/mathlib4/blob/7fa22735254ddf7e11f119250a9f2d0352bc7c3a/Mathlib/RingTheory/Polynomial/Cyclotomic/Factorization.lean) derives irreducibility from these hypotheses; the result is not smuggled in as a premise. This inspection is source-informed, not the independent blind arithmetic derivation assigned to J2.

The [canonical source declaration](https://github.com/isogeny-labs/crypto-autoresearcher/blob/976b82bf60afda5e3d31c0da2704604ea2f2e5a5/formal/CryptoResearch/Binstd/CanonicalFrobenius.lean#L47) is:

```lean
theorem canonicalFrobenius_order_and_minpoly :
    orderOf (FiniteField.frobeniusAlgHom (ZMod 2) CanonicalField17) = 17 ∧
    minpoly (ZMod 2)
      (FiniteField.frobeniusAlgHom (ZMod 2) CanonicalField17).toLinearMap =
      factor1 * factor8a * factor8b
```

`CanonicalField17` is exactly `GaloisField 2 17`. Pinned [Mathlib GaloisField](https://github.com/leanprover-community/mathlib4/blob/7fa22735254ddf7e11f119250a9f2d0352bc7c3a/Mathlib/FieldTheory/Finite/GaloisField.lean#L65) is the splitting field of `X^(2^17) - X` over `ZMod 2`, with actual field, algebra, characteristic and finite-dimensional structure. The extension exponent is nonzero and 2 is prime; the producer discharges both conditions.

Pinned [Mathlib Frobenius](https://github.com/leanprover-community/mathlib4/blob/7fa22735254ddf7e11f119250a9f2d0352bc7c3a/Mathlib/FieldTheory/Finite/Basic.lean#L327) raises elements to the cardinality of the base field, which is 2 here. Order is computed for composition of algebra endomorphisms. The minimal polynomial belongs to the associated linear endomorphism over `ZMod 2`, not to a field element. Mathlib gives order equal to finrank and minimal polynomial `X^finrank - 1`. Specialization to finrank 17, characteristic two, and the exact factor product yields the stated conjunction. The [target YAML](https://github.com/isogeny-labs/crypto-autoresearcher/blob/976b82bf60afda5e3d31c0da2704604ea2f2e5a5/formal/targets/binstd-canonical-frobenius-minpoly.yaml) expresses precisely this claim.

These displayed types are the exact **source signatures** of successfully checked modules. No separate freshly emitted elaborated `#print` or `#check` type dump was found. I do not label source transcription as such a dump. Its absence remains an unmet item of the frozen plan's coordinator-owned machine gate.

## Attempts to falsify verifier fidelity

The exact [worker](https://github.com/isogeny-labs/crypto-autoresearcher/blob/976b82bf60afda5e3d31c0da2704604ea2f2e5a5/orchestration/formal/lean_worker.py) explicitly runs `lake build +<named module>` after the root build. Its generated target audit imports that module, looks up the exact declaration, requires a theorem rather than a definition, traverses `Lean.collectAxioms`, and throws an error for any axiom outside the three-name allowlist. A missing name or definition cannot receive a successful target audit. A project audit that accidentally omits the target is insufficient by itself.

The inspected [real-Lean controls](https://github.com/isogeny-labs/crypto-autoresearcher/blob/976b82bf60afda5e3d31c0da2704604ea2f2e5a5/tests/test_lean_live.py) test absent names, definitions supplied as theorems, a false proposition, a hidden sorryAx dependency with a vacuous project audit, changed helper files and stale/tampered receipt fields. The completed kernel-control job reports **317 passed** on its separate Lean **4.22.0** smoke workspace. This supports the scoped instrument checks; it is distinct from the fresh 4.35.0-rc1 BINSTD receipts. No control was rerun locally in this task.

The source scanner found no active forbidden constructs in the three subject files during the earlier J1 source inspection. The fresh target audit now supplies the transitive check that text inspection could not provide. The [CLI](https://github.com/isogeny-labs/crypto-autoresearcher/blob/976b82bf60afda5e3d31c0da2704604ea2f2e5a5/orchestration/formal/cli.py) records and compares pre/post input snapshots. I independently matched the resulting snapshots to the exact producer tree here.

The [corpus wrapper](https://github.com/isogeny-labs/crypto-autoresearcher/blob/976b82bf60afda5e3d31c0da2704604ea2f2e5a5/tools/verify_formal_targets.py) can classify an absent theorem file as undischarged while meeting a global minimum elsewhere. The actual two named receipts close that particular ambiguity for this review. The root generator covers the main library and the worker explicitly builds its named target; neither fact is a universal compilation audit of every auxiliary tracked Lean source.

## Limits and disposition

- **Elaborated type printout:** missing from the hosted artifact and available logs. The successful build/audit and source-signature review are established; the plan's separate printout requirement is not. The whole packet should not be described as having completed every prescribed formal-review step.
- **Dependency trust:** this evidence uses normal Lean/Lake dependencies and cached binaries. The hosted action explicitly sets leanchecker and lean4checker false. J1 did not independently recheck the kernel/binaries or establish a clean installed Mathlib checkout beyond the manifest/source evidence.
- **Input capture:** pre/post inventories cannot rule out a transient edit restored before the final snapshot. The exact hosted tree and input maps materially bind this run, but JSON hashes alone are not authenticated execution. Here the fresh job logs and independently downloaded hosted artifact supply additional execution provenance.
- **Concrete bridge:** no theorem reviewed here binds the archived polynomial-basis implementation to the canonical field, proves its Frobenius conjugacy, classifies every invariant subspace, verifies the subspace constructor, or validates historical yields. Those are outside these narrow theorem types.
- **Independence:** J1 reused its own prior source knowledge and report context. It read neither J2 report and incorporates no sibling conclusion. It does not claim blindness or a new independent mathematical derivation.
- **History:** older proof receipts remain historical and unchanged. The first round's inconclusive report and identifier/schema deviation are preserved. This new round uses the exact prospective external task ref TASK-20261027-b17d01 mapped to Conductor T-616.

The fresh named machine evidence and exact input reconciliation remove the first-round pending-build obstruction for J1. No defect breaking either scoped source/verifier claim was found. The separate elaborated-type-output obligation stays open, and no scientific or hypothesis status was changed.
