# BATCH-048 frozen input capsule

## Context

BATCH-047 (DEC-20260803-51bcb6) returned `inconclusive` on EXP-IT-001.
Red Team RT-047-B1 found that the planted path positive control was forced
to start from a **special** curve because ordinary 2-isogenies preserve
trace of Frobenius — so a non-special generic curve cannot reach an anomalous
endpoint (trace=1) via an ordinary isogeny walk.

EV-IT-aefd12 O-6 records this as a structural observation:
> rho_special = 0.0 at all three tested bit sizes (20, 24, 28). No special
> curves (anomalous, MOV, subfield) were found as BFS neighbors of any of the
> 21 unplanted curves. This is consistent with the class-invariant property:
> ordinary ell-isogenies preserve the conductor ring, so anomalous curves
> (conductor = End(E) = maximal order, trace=1) are isolated from generic
> curves (distinct conductor) in the ordinary isogeny graph.

## Governing records

- `ledger/evidence/EV-IT-aefd12.yaml` (O-6 structural observation)
- `ledger/decisions/DEC-20260803-51bcb6.yaml` (exact_next_action)
- `ledger/hypotheses/H-IT-001.yaml` (mechanism to assess)
- `experiments/EXP-IT-001/specification.v3.yaml` (experimental scope)

## Required analysis output

1. **Formal statement**: State the class-invariant theorem precisely:
   "For an ordinary ell-isogeny phi: E -> E', the trace of Frobenius
   satisfies trace(E') = trace(E) [mod ell] / ..." — state the exact relation.

2. **Implication for H-IT-001**: Under the stated theorem, can a
   random non-anomalous curve (trace ≠ 1) ever be connected to an
   anomalous curve (trace = 1) by a finite ordinary ell-isogeny path?
   State the answer with proof sketch and name any exception.

3. **Scope of rho_special=0**: Is rho_special=0 expected for ALL prime
   fields at ALL sizes, or only at the specific tested primes? Is there
   a class of primes where special curves ARE present in the ordinary
   2-isogeny graph of a random non-special curve?

4. **Forward direction**: What mechanism COULD achieve the transfer that
   H-IT-001 proposes? Options include:
   - Supersingular isogeny paths (different invariant structure)
   - A different choice of special family that IS reachable from generic curves
   - A restatement of H-IT-001 scoped to actually reachable special curves
   - Something else entirely

5. **Pareto and dominated_by**: Is the proposed successor direction dominated
   by known algorithms? State explicitly.

## Claim ceiling

Theoretical analysis only. No crypto-scale claim. No H-IT-001 status change
in this task. All claims conditional on stated theorems.
