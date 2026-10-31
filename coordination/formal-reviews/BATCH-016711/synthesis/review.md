# BATCH-016711: concrete Semaev finite witness review

**Review outcome: validated_scoped.** For the one archived Boolean S3 draw at `n=4`, `n′=4`, seed 32201, draw 1, the explicitly selected degree-three compatible rows yield a Boolean degree-at-most-two vector outside the degree-two compatible-row span. This conclusion binds the archived equations to Lean's literal lists (J1), the named Lean declaration to its finite proposition and audited axioms (J2), and a result-free independent derivation of the finite row spaces (J3). It does not transfer the certificate to another draw or parameter value.

## Exact claim and machine evidence

The producer source is commit `ad91212179e737d829076ca593d608261590ba89`; `input-bindings.json` freezes 14 inputs. The named declaration is `CryptoResearch.Semaev.ConcreteFirstFallWitness.concreteNewFall`. Its elaborated type states `witnessVec ∈ lowDegreePartThree ∧ witnessVec ∉ rowSpaceTwo`, with finite `ZMod 2` 256-coordinate vectors. The source constructs the explicit vector from a 23-row XOR, checks its degree projection, and separates it from the 28 degree-two rows.

The hosted named receipt `semaev-s3-concrete-first-fall-20261023.json` has SHA-256 `6632556190236956ad4777ba4eaec7fcb6d076f8ba3a72a80a467fdfcce99f92`. It reports a passing exact named build and transitive axiom audit (`propext`, `Classical.choice`, `Quot.sound`) on CI test merge `232f4e78abe6cd8eca285fb2be075d3fdd40ee33`, whose parents are recorded in J2's review. J2 matched 68 receipt workspace input hashes and 10 verifier input hashes to that Git tree. This is hosted execution evidence; no local Lean build was run in this review. PR #2814's formal check was scope-skipped and supplies no additional theorem build.

## Independent joints

| Joint | Frozen result | Control |
| --- | --- | --- |
| J1 archive/source binding, `TASK-20261031-f17d2a` | Four literal ANFs, 28/80 ordered rows, ranks 11/53, 23 selected indices and packed witness matched the archived draw and Lean source | Copied-tree source-binding checker rejected a changed archived component; set-union multiplication retained three monomials that XOR correctly cancels |
| J2 named theorem/axioms, `TASK-20261031-4870db` | Exact finite elaborated type, nonvacuous definitions, hosted receipt and standard transitive axioms matched the pinned source | Replacing separator coordinate 192 by 0 fails on degree-two row 0 |
| J3 blind derivation, `TASK-20261031-068004` | From the isolated result-free card: D2 rank 11, D3 rank 53, degree-at-most-two intersection rank 12; one new class, explicit 23-row combination and separator `c80+c192` | Duplicate-product parity and changed-component controls changed the expected row sets |

All three reviewers froze raw outputs, code, complete read attestations and hashes before composition. `review-artifact-hashes.json` lists every archived reviewer file. Running `tools.check_review_independence.check` on the frozen plan and the three `review_attestation` mappings returned **zero findings**. The blind snapshot bundle has a complete one-commit history, only six tracked files, no producer source, and no protected outcome token in its reachable commit message.

## Interpretation and boundary

The rank calculation is over the 256 Boolean monomial coordinates of this specific F16 basis and archived draw. The degree-three row space has rank 53; its degree-at-most-two intersection has rank 12, while the degree-two row space has rank 11. J3's functional `c80+c192` vanishes on all 28 lower rows and evaluates to 1 on the explicit witness. J1 independently binds that witness to the archived S3 equations, and J2 verifies that Lean proves exactly the finite membership and nonmembership statement.

The reviewers did not reproduce the Lean build locally because the shared host was occupied by unrelated Rust builds. The pinned hosted receipt and exact Git input hashes support machine status `passed`; the dependency on the hosted runner and its Lean binary remains recorded. This technical packet changes no experiment, hypothesis, or official evidence status. The next technical step is to bind and check any further archived draw separately if a broader finite family is sought.

## Record and visuals

The frozen plan is in `review-plan.yaml`, reviewer handoffs in `handoffs/`, raw packets in `reviews/`, receipt in `docs/reports/2026-10-31-hosted-formal-receipts/receipts/`, and this synthesis has `structure.svg` plus an inspected `report.pdf`. Existing performance graphs and dashboard metrics have no new performance measurement from this proof review; their source data remain the prior run records.

The first Python 3.9 baseline attempt produced an empty stdout file; it is archived byte-for-byte as `producer-baseline-stdout.empty.txt` so JSON readers do not mistake it for a valid result. The successful Python 3.11 baseline is separately retained and hashed.
