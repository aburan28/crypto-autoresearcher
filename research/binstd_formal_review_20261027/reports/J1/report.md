# J1: theorem and verifier fidelity

Review task: **T-608**. Reviewer session: `/root/binstd_j1_formal`.
Frozen plan: `b95ccf3400f34441952930c6ca8b9a129661222d`.
Producer: [PR #2484](https://github.com/isogeny-labs/crypto-autoresearcher/pull/2484),
head `976b82bf60afda5e3d31c0da2704604ea2f2e5a5`.
Observation date: 2026-10-27 UTC. No sibling report was opened.

**J1 verdict: inconclusive for completed current-head verification; source-level fidelity is faithful_scoped for both declarations.**
No type/claim mismatch or mathematical counterexample was found. At the hosted-status observation, the workspace build was still running and the per-target audit had not started. Neither a fresh elaborated type printout nor a fresh transitive-axiom result for the two target declarations was available to this reviewer. This is an evidence limit, not a refutation of either theorem.

| Declaration | Current machine status observed by J1 | Fidelity to the frozen claim | Review result |
| --- | --- | --- | --- |
| `CryptoResearch.Binstd.factor8_irreducible_pair` | `not_verified`: historical receipt only; current gate incomplete | `faithful_scoped` from exact source statement and definitions | `inconclusive` pending fresh named evidence |
| `CryptoResearch.Binstd.canonicalFrobenius_order_and_minpoly` | `not_verified`: historical receipt only; current gate incomplete | `faithful_scoped` from exact source statement and pinned Mathlib definitions | `inconclusive` pending fresh named evidence |

## Source and input binding

All eight Git blobs in the frozen `inputs.json` match the producer tree. [source-binding.json](source-binding.json) records the independently computed Git blob identifiers and SHA-256 values, as well as the four historical receipt hashes for each target.

The hosted run is [40591043322](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/40591043322). Its metadata associates it with producer head `976b82bf...`, but the actual checkout in the completed kernel-control log is the synthetic merge commit `07b26a4faaf30b84a6a189bde044e4356d1f2944`. The recorded checkout line is retained in [hosted-kernel-controls-excerpt.log](hosted-kernel-controls-excerpt.log), with the full downloaded job log in [hosted-kernel-controls.log](hosted-kernel-controls.log).

This distinction does not produce a source mismatch here. GitHub file reads at the synthetic merge reproduce all eight frozen blobs. Local Git also reports the same complete tree for both commits:

```text
git rev-parse 976b82bf60afda5e3d31c0da2704604ea2f2e5a5^{tree}
0278ef830e544ff7b04af3765c366bf5acb8a3cb
git rev-parse 07b26a4faaf30b84a6a189bde044e4356d1f2944^{tree}
0278ef830e544ff7b04af3765c366bf5acb8a3cb
git diff --stat 976b82bf60afda5e3d31c0da2704604ea2f2e5a5 07b26a4faaf30b84a6a189bde044e4356d1f2944
# no output, exit 0
```

A completed hosted receipt may therefore support this producer source tree once its actual input inventories, generated files, pins and declaration audits are reconciled. Merely associating a green check with the PR head would be weaker evidence.

The dependency manifest pins Mathlib to `7fa22735254ddf7e11f119250a9f2d0352bc7c3a`; the main workspace pins Lean `leanprover/lean4:v4.35.0-rc1`. The moving `master` label in the [Lake configuration](https://github.com/isogeny-labs/crypto-autoresearcher/blob/976b82bf60afda5e3d31c0da2704604ea2f2e5a5/formal/lakefile.toml) is resolved by the committed manifest. This review did not inspect a currently installed dependency checkout or independently recheck dependency binaries.

## Exact statements and semantics

The irreducibility target's source type is:

```lean
theorem factor8_irreducible_pair :
    Irreducible factor8a ∧ Irreducible factor8b
```

There are no user-supplied hypotheses, implication premises, or quantified arbitrary fields hidden in this declaration. The [definitions](https://github.com/isogeny-labs/crypto-autoresearcher/blob/976b82bf60afda5e3d31c0da2704604ea2f2e5a5/formal/CryptoResearch/Binstd/Factorization.lean#L22) fix `F2 := ZMod 2`, `factor8a = X^8 + X^5 + X^4 + X^3 + 1`, and `factor8b = X^8 + X^7 + X^6 + X^4 + X^2 + X + 1`. The bit positions are respectively `{8,5,4,3,0}` and `{8,7,6,4,2,1,0}`, giving 313 and 471. The remaining factor is `X + 1`, encoded by 3. This matches both the [frozen JSON](https://github.com/isogeny-labs/crypto-autoresearcher/blob/976b82bf60afda5e3d31c0da2704604ea2f2e5a5/experiments/EXP-BINSTD-8bdf86/stage1-ell89/admissible-phi-dims.json) and the [target YAML](https://github.com/isogeny-labs/crypto-autoresearcher/blob/976b82bf60afda5e3d31c0da2704604ea2f2e5a5/formal/targets/binstd-x17-degree-eight-irreducible.yaml).

The [proof](https://github.com/isogeny-labs/crypto-autoresearcher/blob/976b82bf60afda5e3d31c0da2704604ea2f2e5a5/formal/CryptoResearch/Binstd/Irreducibility.lean#L23) supplies primality of 2 and 17 using `decide`, supplies `Nat.Coprime 2 17`, proves that 2 has order 8 in `(ZMod 17)ˣ`, and proves each degree is 8. It obtains the seventeenth cyclotomic polynomial by cancelling the nonzero factor `X + 1` from the exact product identity. Each degree-eight factor is then shown to divide that cyclotomic polynomial. The pinned [Mathlib factor-degree criterion](https://github.com/leanprover-community/mathlib4/blob/7fa22735254ddf7e11f119250a9f2d0352bc7c3a/Mathlib/RingTheory/Polynomial/Cyclotomic/Factorization.lean) takes exactly divisibility, the nondivisibility `¬ 2 ∣ 17`, and degree equal to multiplicative order. The conclusion is not assumed as a premise.

The canonical Frobenius target's source type is:

```lean
theorem canonicalFrobenius_order_and_minpoly :
    orderOf (FiniteField.frobeniusAlgHom (ZMod 2) CanonicalField17) = 17 ∧
    minpoly (ZMod 2)
      (FiniteField.frobeniusAlgHom (ZMod 2) CanonicalField17).toLinearMap =
      factor1 * factor8a * factor8b
```

[CanonicalField17](https://github.com/isogeny-labs/crypto-autoresearcher/blob/976b82bf60afda5e3d31c0da2704604ea2f2e5a5/formal/CryptoResearch/Binstd/CanonicalFrobenius.lean#L20) is exactly `GaloisField 2 17`. In the pinned [Mathlib definition](https://github.com/leanprover-community/mathlib4/blob/7fa22735254ddf7e11f119250a9f2d0352bc7c3a/Mathlib/FieldTheory/Finite/GaloisField.lean#L65), this is the splitting field of `X^(2^17) - X` over `ZMod 2`, with genuine field, characteristic, algebra, finiteness and finite-dimensional instances. The finrank theorem requires the extension exponent to be nonzero; the producer discharges `17 ≠ 0`. The local primality instance is a supplied proof, not an external assumption.

Pinned [Mathlib Frobenius](https://github.com/leanprover-community/mathlib4/blob/7fa22735254ddf7e11f119250a9f2d0352bc7c3a/Mathlib/FieldTheory/Finite/Basic.lean#L327) raises an element to the cardinality of the base field. Here that cardinality is 2, so the map is `x ↦ x²`. Its order is computed in the monoid of algebra endomorphisms, whose multiplication is composition. The minimal polynomial is taken of the associated linear endomorphism over `ZMod 2`; it is not the minimal polynomial of a field element. Mathlib's `orderOf_frobeniusAlgHom` and `minpoly_frobeniusAlgHom` give finrank and `X^finrank - 1`, respectively. The producer specializes finrank to 17, uses characteristic two to identify minus one with plus one, and uses the exact three-factor product. The [target YAML](https://github.com/isogeny-labs/crypto-autoresearcher/blob/976b82bf60afda5e3d31c0da2704604ea2f2e5a5/formal/targets/binstd-canonical-frobenius-minpoly.yaml) states this same claim.

These are inspections of exact source types and definitions, **not a claim to have obtained fresh elaborated `#print` output**. The coordinator-owned machine gate must supply that final elaboration evidence. The imports and inspected source use ordinary kernel-checked proof tactics; no `native_decide`, `unsafe`, custom axiom, `sorry`, `admit`, `implemented_by`, or `run_tac` occurs in the three subject files' active source. The producer scanner also reports no forbidden constructs on those exact bytes. A textual scan does not replace a transitive axiom audit.

## Historical receipt limitations

The [irreducibility receipt](https://github.com/isogeny-labs/crypto-autoresearcher/blob/976b82bf60afda5e3d31c0da2704604ea2f2e5a5/docs/reports/2026-10-22-binstd-irred-lean/proof-verification.json) records source commit `30a97e57acf783a7fe996ea8c27d730a51033533`, a 625-theorem project audit, and the correct named target audit. The [canonical receipt](https://github.com/isogeny-labs/crypto-autoresearcher/blob/976b82bf60afda5e3d31c0da2704604ea2f2e5a5/docs/reports/2026-10-22-binstd-canonical-frobenius/proof-verification.json) records `4cd570dc0431bef2f0d5fda98aad722c68b5c7b5`, a 630-theorem project audit, and its correct named target audit. Both explicitly leave semantic review pending.

All four recorded hashes in each historical receipt still match the current corresponding theorem, task specification, toolchain, and dependency manifest. They nevertheless omit `workspace_inputs` and `verifier_inputs`, and do not bind all local imports, the project audit, Lake configuration or verifier implementation. No full-workspace or current-head assertion is made from them. The raw JSON reports successful historical execution; this review has not authenticated that execution independently.

## Verifier and controls

The exact [workflow](https://github.com/isogeny-labs/crypto-autoresearcher/blob/976b82bf60afda5e3d31c0da2704604ea2f2e5a5/.github/workflows/lean-verification.yml) separates smoke controls from the main Mathlib workspace. The [scope detector](https://github.com/isogeny-labs/crypto-autoresearcher/blob/976b82bf60afda5e3d31c0da2704604ea2f2e5a5/.github/scripts/ci_scope.py) sets both relevant flags for non-documentation main-formal changes. Jobs reject an absent or malformed scope result. For this run the scope-exclusion steps were skipped, and the actual build/control steps ran.

The [worker](https://github.com/isogeny-labs/crypto-autoresearcher/blob/976b82bf60afda5e3d31c0da2704604ea2f2e5a5/orchestration/formal/lean_worker.py) first runs `lake build`, then explicitly `lake build +<target module>`. It therefore does not infer target compilation from an unrelated root build. Its generated target audit imports that module, requires the named constant to be a theorem, traverses `Lean.collectAxioms`, and throws an error for anything outside `propext`, `Classical.choice`, and `Quot.sound`. A missing theorem or a definition cannot pass the generated audit. Private dependencies are traversed from the named target even though the [project audit](https://github.com/isogeny-labs/crypto-autoresearcher/blob/976b82bf60afda5e3d31c0da2704604ea2f2e5a5/formal/AxiomAudit.lean) selects public theorem names under `CryptoResearch`.

The [root generator](https://github.com/isogeny-labs/crypto-autoresearcher/blob/976b82bf60afda5e3d31c0da2704604ea2f2e5a5/orchestration/formal/workspace.py) imports every main-library source found under `CryptoResearch/`; the producer tree contains 49 such tracked files and 55 tracked Lean files overall. The remaining six are audit and separate smoke/scoped-workspace files. This is not the newer universal tracked-source compilation mechanism described by the review skill; the present worker's explicit build protects its named module. No coverage claim for every auxiliary source is inferred from a named audit.

The [CLI](https://github.com/isogeny-labs/crypto-autoresearcher/blob/976b82bf60afda5e3d31c0da2704604ea2f2e5a5/orchestration/formal/cli.py) checks exact Lean-release and dependency-commit pins, verifies the running Lean version, and now takes pre/post local-source and verifier inventories. Its [receipt helper](https://github.com/isogeny-labs/crypto-autoresearcher/blob/976b82bf60afda5e3d31c0da2704604ea2f2e5a5/orchestration/formal/receipts.py) rejects empty/incorrect audit evidence and inconsistent identities or hashes. These consistency checks do not authenticate execution or detect a transient edit restored between snapshots. Dependency binaries remain within Lean/Lake's ordinary trust boundary. An independent binary/kernel rechecker was not run by J1.

The corpus wrapper [verify_formal_targets.py](https://github.com/isogeny-labs/crypto-autoresearcher/blob/976b82bf60afda5e3d31c0da2704604ea2f2e5a5/tools/verify_formal_targets.py) labels a target with no theorem file as undischarged and only requires a global floor of one passing target. Thus a global green gate alone cannot prove that either particular BINSTD declaration was present: the final packet must check their two named receipts. If a present target's build or audit fails, the wrapper propagates failure; infrastructure failure is reported separately.

The completed hosted [kernel-controls job 122495145439](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/40591043322/job/122495145439) reported **317 passed**. The log shows Lean **4.22.0** for the dependency-free smoke workspace, not the main workspace's 4.35.0-rc1. The inspected [live tests](https://github.com/isogeny-labs/crypto-autoresearcher/blob/976b82bf60afda5e3d31c0da2704604ea2f2e5a5/tests/test_lean_live.py) include a valid theorem; an absent theorem; a definition supplied as theorem; a false proposition; a hidden `sorryAx` dependency with a vacuous project audit; changed/added/deleted helper files; stale and tampered receipt fields; and a changed hidden-library input. This supports the scoped instrument behavior. J1 did not rerun these tests locally or perform a separate omitted-module mutation; the explicit module-build logic was checked in source. No experiment or heavy local build was launched.

The hosted workspace job was observed as `in_progress` at its `Build the workspace` step, with `Machine-check every discharged formal target` pending. At the subsequent artifact query, only `lean-controls` artifact 12772994949 was available, with zip digest `68f2b2907efc105c649d4595ce4f9251c0feb6fc974c0b9c591778042228ee11`. This is not a proof receipt for either subject declaration.

## Remaining obligations and boundary

1. Obtain fresh named-module success, elaborated theorem types and transitive axiom evidence for both declarations on the frozen source tree; reconcile any hosted receipt's actual source commit and input maps with that tree.
2. Preserve the Lean/Lake dependency trust boundary and disclose whether `lean4checker --fresh` or another independent checker was available and used.
3. Preserve the concrete bridge limits already stated in the producer target: runner quotient-field validity and implementation correspondence, Frobenius conjugacy, exhaustive invariant-subspace classification, and binding the actual subspace constructor are absent from these theorem types. No empirical hit count or yield is established.
4. The stock independence checker requires `TASK-*` identifiers while the frozen plan assigned Conductor IDs `T-608` and `T-609`. This report retains its actual ID. The coordinator must preserve and document the checker failure; silently changing the reviewer identity would misstate the round.

The source audit gives no reason to weaken the two narrowly scoped mathematical statements. The incomplete machine gate prevents a completed-validation verdict at this seal. No experiment, hypothesis, evidence, decision or scientific status was changed. The coordinator owns any later additive machine-evidence reconciliation and the final technical-packet diagram/PDF.
