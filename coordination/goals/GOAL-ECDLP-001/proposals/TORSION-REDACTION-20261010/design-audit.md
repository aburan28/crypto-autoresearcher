# Torsion-image redaction ladder audit

## Audit basis

- Idea: `IDEA-20261007-cd446e`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.
- The ladder is a functional auxiliary-data diagnostic, not a security proof
  or a proof about all EndRing-based schemes.

## Scientific boundary

Replacing public torsion data can reveal whether a declared candidate depends
on that data, but only if every rung remains a well-typed instance of the same
candidate interface. A tuple with the same length and nominal order may fail
pairing, basis, orientation, curve-membership, or key-consistency checks. A
correctness collapse on such an invalid replacement cannot be labeled
torsion-essentiality.

## Load-bearing repairs

1. Freeze the candidate's full public-input schema and validation predicate:
   curve, torsion subgroup, basis/order, pairing relations, orientation,
   isogeny images, serialization, and all auxiliary fields. Record hidden or
   derived auxiliary state separately; the ladder only covers data that is
   explicitly listed and redacted.
2. Define V1's replacement distribution conditionally on validity. “Uniform
   same-shape torsion tuples” is insufficient when valid tuples satisfy
   algebraic or pairing constraints. Either sample uniformly from the exact
   valid public-auxiliary space, or report invalid samples separately and do
   not combine their failures with functional agreement.
3. Do not hold an arbitrary secret key fixed while changing public data unless
   the candidate interface permits that pair. State whether V1 is a
   key-consistent rerandomization, an intentionally malformed-input control,
   or a redacted public view. These are different experiments and have
   different conclusions.
4. Define V2 and V3 as independent candidates where necessary. Deterministic
   public resampling from `pk` may not reconstruct an orientation or basis, and
   an orientation descriptor is not equivalent to a torsion image. Compare
   each rung only against a candidate-specific correctness predicate and keep
   state, caches, and validation failures isolated.
5. Correct the interpretation of the metric. A drop from V0 to V1 can mean
   invalid auxiliary data, a changed secret/public distribution, a decoder
   rejection, or genuine dependence on torsion information. The minimum
   evidence for the latter is valid key-consistent replacements with the same
   interface and a separately measured malformed-input rate.
6. Replace “chance” with a declared failure model. A broken decoder may emit a
   constant or biased bit rather than an independent random bit. Report the
   output distribution, conditional agreement, decoder failure, and Wilson or
   exact intervals; calibrate the null decoder and a known aux-inessential
   positive control.
7. Pair the randomness correctly. Use independent fresh messages and coins
   while retaining a predeclared paired schedule for variance reduction; do
   not reuse V0 state, caches, endpoint tables, or secret-derived artifacts in
   V1–V3. Replay the same candidate from a clean state and record all
   rejection/shape-check counts.
8. Keep the conclusion finite. Persistence of agreement supports only
   compatibility with the tested pure-EndRing-shaped interface. A collapse
   under valid redaction names a dependency in that candidate; it does not
   break EndRing, prove a scheme insecure, or establish that every torsion-
   aided design has the same weakness.

## Readiness and disposition

The record is proposal-only and lacks a committed candidate interface,
valid-auxiliary sampler, key-consistency definition, and scheme-level
correctness artifact. Its recalled SSI literature is not needed to run the
finite ladder and does not discharge those obligations.

Disposition: **retain proposed as a conditional auxiliary-data control; do not
approve or dispatch as filed.** Repair the valid replacement distribution,
key-consistency semantics, rung-specific correctness tests, null/positive
controls, and hidden-auxiliary inventory. Recheck readiness and approval
capacity once the fixed candidate contract is complete.
