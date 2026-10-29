# Affine STARK transition: retrospective mathematical obligations

Status: revised candidate proof source. The original six declarations have
historical native evidence and an independent source/type review. The new
seventh declaration and current negative controls await native validation and
review. See `J2-response.md`. Conductor T-781 / formal task TASK-20261029-4cdb4c.

## Existing claim and tested behavior

Internal source: crypto commit `8ce2800fbe3d265027e2341ec193ad69b946a8bd`,
`src/zk/stark_v2.rs`, Git blob `6cb057163d6a12a4d69c037f16c753034228e59f`.
Lines 176–204 define private canonical coefficients and evaluate
`a*previous + b*next + c` in the scalar field. Lines 342–347 state that a
supported transition is determined exactly by its first three probe values,
at `(0,0)`, `(1,0)`, `(0,1)`. Lines 954–970 contain the four-point
`previous*next` negative control. These are the source claims being formalized;
this task does not invent a new experimental result or general soundness claim.

The arbitrary-closure API problem was already repaired by crypto PR #2496,
merged on 2026-10-24 as `810190062c1b760a8cf6bbbed787654d6379d434`.
The current source retains the typed `AffineTransition` interface. The
historical sheriff report describes the older unrestricted API and is preserved.
The original PR body reports local release tests; the presently retrieved
final-head Actions runs are cancelled (attempt 1), so they are not represented
as successful hosted validation. No new Rust test run is claimed here.

## Exact mathematical claims

Let R be any commutative ring and define E(a,b,c,x,y) = a*x + b*y + c.

1. **Recovery.** For every a,b,c, the tuple
   `(E(a,b,c,1,0)-E(a,b,c,0,0), E(a,b,c,0,1)-E(a,b,c,0,0), E(a,b,c,0,0))`
   equals `(a,b,c)`.
2. **Coefficient uniqueness.** If two coefficient triples have equal values
   on all three designated probes, the coefficient triples are equal.
3. **Extensionality.** Under those three probe equalities, their values agree
   for every x,y in R. No characteristic, primality, finiteness, field, or
   nontriviality assumption is required for claims 1–3.
4. **Multiplication obstruction.** If R is additionally nontrivial, for every
   coefficient triple it is false that E(a,b,c,x,y)=x*y for every x,y.
5. **Missing-probe control.** In any nontrivial R, the transitions with
   coefficients `(0,0,0)` and `(0,1,0)` agree at `(0,0)` and `(1,0)`, but
   disagree at `(0,1)`.
6. **Zero-ring control.** Over ZMod 1, the zero affine transition agrees with
   multiplication everywhere; claim 4 therefore needs nontriviality.
7. **Exact four-probe obstruction.** If R is nontrivial, for every a,b,c,
   the conjunction of E(a,b,c,x,y)=x*y at the four pairs
   `(0,0)`, `(1,0)`, `(0,1)`, `(1,1)` is false. This exports the precise
   finite-point assertion in the Rust comment, uniformly over R.

Claims 1–3 formalize the source's exact determination statement. Claim 4 is
global nonagreement; it does not by itself identify four points of obstruction.
Claim 7 formalizes the exact four-point control with the necessary nontriviality
assumption. Claims 5–6 test the proof boundary. The Lean source uses genuine
Mathlib ring instances; no custom axioms or assumed conclusion are introduced.

## Bridges and exclusions

These are statements about ring-valued expressions. They do not prove:

- that the Rust BigUint operations, modular reduction or compiler implement
  the ring model correctly on every input;
- injectivity or correctness of `reduced_bytes`, concatenation, Merkle hashes,
  Fiat–Shamir sampling or the full serialized AIR fingerprint;
- a formal MvPolynomial total-degree theorem, complete AIR satisfaction,
  composition/DEEP/FRI soundness, zero knowledge or a security level;
- historical execution, timing, benchmark validity or all experiment results.

The scalar field is an intended instance of the ring model, not a silently
assumed end-to-end Rust verification. Those bridges remain separate obligations
in the full historical validation goal.

## Machine evidence required

Use the unchanged `formal/lean-toolchain` and `formal/lake-manifest.json`,
explicitly build `CryptoResearch.Stark.AffineTransition`, retain all seven
elaborated type prints and axiom audits, and verify the registered target with
the repository's existing verifier. Check the three-probe and zero-ring
controls. No source inspection or passing schema substitutes for native Lean.
Local Mathlib cache is unavailable and the local heavy-build reservation is
owned by T-650, so this task starts no local native build. Existing hosted
formal CI is the delivery gate; no new cloud experiment or capacity is requested.
