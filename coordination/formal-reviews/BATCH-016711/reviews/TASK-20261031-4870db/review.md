# J2 review: exact Lean theorem, axioms, semantic boundary

Task `TASK-20261031-4870db`, batch `BATCH-016711`; independent J2 judgment frozen at the PR #2814 handoff head `d309c071eae839be207113584a54ba9af27fdaa7`. Source theorem bytes are pinned at `ad91212179e737d829076ca593d608261590ba89`. I read no sibling or earlier-round reviewer report or verdict.

## Judgment

| Dimension | J2 result |
| --- | --- |
| Machine status | **passed on hosted receipt** for the exact named declaration and hashed source; no local Lean build was run |
| Fidelity | **faithful_scoped** to the explicit finite Boolean row-space claim, conditional on J1's independent archive-to-literal binding |
| J2 joint verdict | **holds** for the exact theorem, axioms, definitions, nonvacuity and false separator control |
| Composed outcome | Deferred to Coordinator after J1/J3 and independence checks |

The hosted receipt names `CryptoResearch.Semaev.ConcreteFirstFallWitness.concreteNewFall` and prints this elaborated type:

```lean
witnessVec ∈ BooleanParityFiltrationCertificate.FiniteSemaev.lowDegreePartThree ∧
witnessVec ∉ BooleanParityFiltrationCertificate.FiniteSemaev.rowSpaceTwo
```

The source defines `witnessVec` as the 256-coordinate `ZMod 2` bit vector of the explicit packed `witnessNat`; `lowDegreePartThree` is the intersection of the span of all 80 `fullRows3` and the kernel of projection onto coordinates of Boolean monomial degree above two; `rowSpaceTwo` is the span of all 28 `fullRows2`. The theorem has no assumptions, parameters or exceptional-case premise. Its `xorRows 80 = witnessNat` subproof, row-space induction, degree projection and separator proof connect those definitions to the explicit vector. These definitions are inhabited; the same witness is shown to lie in the first subspace and outside the second.

The four equation lists are literals in `BooleanParityFiniteCertificate.lean`. Its row builder uses XOR parity for duplicate product masks and selects monomial multiples whose actual Boolean degree is at most the requested degree. The theorem does not internally derive those literals from the archived S3 draw. That source binding is assigned to J1. The statement also contains no quantification over another draw, parameter size, generic S3 polynomial, solving degree, or cryptanalytic cost.

## Machine evidence and custody

The named hosted receipt is `docs/reports/2026-10-31-hosted-formal-receipts/receipts/semaev-s3-concrete-first-fall-20261023.json` from merged PR #2811, byte SHA-256 `6632556190236956ad4777ba4eaec7fcb6d076f8ba3a72a80a467fdfcce99f92`. It cites PR #2805 GitHub Actions run `41155781140`, job `124402203382`, artifact `13025547799`. Its CI test merge `232f4e78abe6cd8eca285fb2be075d3fdd40ee33` has exact parents `a1f3d0fde48d8a09301d65f8b8056f3cf42fc307` and `f9f36cd81bba99872cdec73dd23e2e69213fd446` in that order. My read-only script checked all 68 workspace input hashes, including regenerated `CryptoResearch.lean`, and all 10 verifier input hashes against Git blobs at that merge. It checked the named target, theorem, toolchain and manifest hashes also at plan source commit `ad91212179e737d829076ca593d608261590ba89`. There were zero mismatches.

The receipt reports `machine_verified`, build and axiom audit passed, and no forbidden constructs. Its audit log prints the named theorem type and its transitive axiom list: `propext`, `Classical.choice`, `Quot.sound`. The pinned toolchain is `leanprover/lean4:v4.35.0-rc1`; the manifest pins Mathlib at `7fa22735254ddf7e11f119250a9f2d0352bc7c3a` and its dependencies. This is hosted build evidence, not a build made in this J2 session. The receipt and hash audit establish source/receipt consistency and hosted execution provenance to the extent of the GitHub Actions record; they do not independently recheck Lean's binary or kernel.

PR #2814's successful `formal workspace (lake build + axiom audit)` job is **scope-skipped**: its log sets `BUILD_WORKSPACE=false`, says no proof workspace input changed, and uploads no formal receipt. I have not counted that check as a theorem build.

## Independent low-memory controls

The J2 script regenerated the rows from the four theorem-import literals using XOR parity. It obtained 28 compatible rows at degree two and 80 at degree three. The 23 rows selected by `comboMask=1321682796735964` XOR to `witnessNat=6277101735386703064921270320751746415339343215057222047510`. All present witness coordinates have Boolean degree at most two. The functional `c80+c192` vanishes on all 28 degree-two rows and is one on the witness.

For a nearby false control, I changed the second separator coordinate from 192 to 0. On degree-two row index 0, `c80=0`, `c0=1`, so the altered separator is 1 and fails to annihilate the lower row space. This is a concrete counterexample to the changed annihilation claim, not a Lean elaboration test.

The raw output and complete script are frozen beside this report. No heavy Lean/Cargo, cloud job, trial or instance was launched.
