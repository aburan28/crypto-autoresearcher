# TASK-20260723-803 independent Newton review

## Verdict

`REVISE`

`admission_survives: true`

`breakthrough_claimed: false`

`ADMIT_ASYMPTOTIC_NEWTON_SATURATION_PROOF_ROUTE_FOR_REVIEW` survives only as
a conditional paper-proof gate. It is not yet an established all-\(m\)
theorem and gives no positive sub-rho credit.

The reviewed producer files are the Coordinator snapshot at
`fa347e96d60f73e699f7f0a6c296e5910603a261`; their SHA-256 values match the
snapshot receipt. No working-tree-only producer artifact was treated as
durable evidence.

## Core proof route

Conditional on the exact identity

\[
\operatorname{LC}_{x_i}(S_m)=u_m S_{m-1}^2
\]

with \(u_m\) a specialization-safe unit, the corner argument is sound in
outline. At a box corner, every remaining exponent is either zero or twice
the lower-order per-variable degree, so each exponent forces the same extreme
term from both factors. There is no corner convolution ambiguity. If the
all-zero specialization has exactly the claimed signed-\(P_0\) roots, all box
vertices occur away from the stated exceptional set, which forces the Newton
hull to be the full box.

The snapshot has not supplied the two facts in the exact normalization needed
for theorem status:

1. It says “up to a fixed nonzero normalization,” but does not freeze one
   recursive circuit and prove that every factor is a unit under every allowed
   specialization. Generic nonvanishing is insufficient.
2. It invokes Semaev’s zero semantics for the exact converse on
   \(S_s(0,\ldots,0,t)\), but does not prove nonzero specialization, absence of
   extraneous resultant factors, or the \(B=0\), infinity, and torsion cases.

Thus the \(O(m)\) exception classifier remains a derivation candidate. The
\(m=3,4,5\) toy BKK records are consistency checks, not evidence for the
inductive step.

## Typed-oracle review

The forbidden-free-oracle list correctly excludes target-fitted advice,
unpriced source tuples, signs, branches, logs, rank, and descent witnesses.
The interface is nevertheless incomplete.

The theorem input conflates a universal coefficient ring with a field of fixed
characteristic, and a “declared nonzero normalization” is not a certificate.
Specialized replay lacks the encoded target point and subgroup witnesses,
random tape, source lifts and sign orientation, relation/rank certificate,
factor-log solution, descent witness, rejection reasons, and a common
bit-operation/traffic/memory unit. Calling the oracle randomness-free is
compatible with masking only if the complete random tape is an explicit replay
input.

Naming setup, misses, output, rank, linear algebra, descent, verification,
traffic, and memory does not itself charge them. A complete transcript schema
is still missing.

## Cost and scope

For fresh independent uniform masks, at most \(2(m-1)\) eligible subgroup
points gives hit probability at most \(2(m-1)/N\), hence
\(\Omega(N/m)\) expected mask trials. If replay requires materializing or
retrieving all \(m\) entries and signs in the same cost model, adding
\(\Omega(m)\) yields

\[
\Omega(N/m+m)=\Omega(\sqrt N).
\]

This is a valid negative gate for that bridge. It is not a lower bound for an
unspecified nonuniform bridge. The remaining Semaev path—factor-base
membership, decomposition failures, source recovery and orientation, relation
supply and independence, rank, factor logs, blind descent, verification,
traffic, and memory—has not been quantified end to end.

A proper exceptional-section polytope does not by itself imply a smaller mixed
volume for the complete square system, a cheaper solver, or a usable relation.
Exceptional sections therefore receive no positive algorithmic credit.

If the missing lemmas are proved, the all-\(m\) conclusion closes only the
mixed-volume/path-count gap against the multigraded box Bézout number for the
original target-sectioned formulation. It does not establish equal runtime for
all sparse implementations or cover unsectioned systems, coefficient-dependent
liftings, Gröbner systems, arithmetic circuits, or non-Semaev methods.

## Baselines

- Pollard rho solves a fresh target in expected \(N^{1/2+o(1)}\) group
  operations with negligible serial memory. The scoped bridge lower bound only
  matches its exponent; it does not establish a constant-factor comparison.
- BSGS has \(N^{1/2+o(1)}\) work and storage. No common bit-operation or
  parallel-memory ledger is supplied.
- The closest specialized baseline is canonical prime-field Semaev
  point-decomposition/index calculus with the multigraded box driver.
  Conditional saturation gives mixed-volume/box-Bézout ratio one, but the
  snapshot does not freeze a complete specialized cost formula. It therefore
  supports no end-to-end superiority claim in either direction.

## Narrowest conclusion

The route remains worth one paper-only proof pass. Conditional generic
Newton-box saturation would be a negative mechanism gate, while the
uniform-mask exception bridge receives no sub-rho credit. There is no
cryptographically relevant breakthrough, no ECDLP hardness theorem, and no
official state transition.

## Next action

Produce one normalization-locked paper proof packet that fixes the exact
recursive \(S_m\) circuit, proves the unit-valued leading-coefficient induction
and the all-zero-corner root classifier including \(B=0\) and
infinity/torsion cases, and instantiates those lemmas in a versioned
theorem-mode replay certificate; do not open an algorithmic experiment or
change ledger status.
