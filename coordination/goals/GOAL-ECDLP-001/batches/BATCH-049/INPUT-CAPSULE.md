# BATCH-049 frozen input capsule

## Why we are here

BATCH-047 and BATCH-048 established:
- rho_special = 0 for ordinary 2-isogeny graphs at bits ∈ {20, 24, 28}
- The Tate isogeny theorem (unconditional): ordinary F_p-isogenies preserve
  trace of Frobenius; anomalous/MOV/Weil-descent special families are
  isogeny-class invariants; no generic curve can reach them by ordinary walk
- H-IT-001 ordinary-isogeny mechanism: `weakened` (DEC-20260804-2fae6a)
- Two successor directions remain open (EV-IT-511f3d O-4):
  - **DIR-2**: Find a special family whose distinguishing property is NOT an
    isogeny-class invariant — one that a generic curve can reach
  - **DIR-3**: Reformulate within an isogeny class — exploit a weakness that
    applies to a large fraction of curves within the same conductor class

## The two open directions in detail

### DIR-2: Non-invariant special family

Which ECDLP-weak properties are NOT determined by the trace of Frobenius?
- The trace fixes #E(F_p) and hence the subgroup order N.
- Properties of N itself (smoothness, special algebraic structure) are fixed
  within an isogeny class.
- Properties that depend on the j-invariant, the Weierstrass model, or the
  specific endomorphism ring (not just its discriminant) might vary within a class.
- Example: within the same isogeny class, different j-invariants have different
  CM rings (varying between maximal order and its orders). Could a sub-order
  endomorphism ring give a ECDLP speed-up?
- Example: Pohlig-Hellman applies when N is smooth — but N is fixed by the
  trace, so all curves in the same class are equally (un)Pohlig-Hellman-reducible.
- What about the Weil pairing or Tate pairing parameters? Those might vary.

### DIR-3: Within-class reformulation

If we start with a curve E in a fixed isogeny class (trace t, order N),
can we use the isogeny class structure to speed up the DLP on E?
- The isogeny graph within the class forms a volcano (Delfs-Galbraith structure).
- Moving to a different level of the volcano (closer to the surface / floor)
  might give access to curves with more endomorphisms.
- Endomorphisms of E can accelerate the DLP (Gallant-Lambert-Vanstone trick):
  if End(E) contains a non-trivial endomorphism phi with eigenvalue lambda mod N,
  then the DLP splits into a two-dimensional problem of size sqrt(N).
- Key question: can we walk in the isogeny class to a curve with a RICHER
  endomorphism ring (closer to the maximal CM order), then exploit that?
  GLV works when the CM order has small discriminant (the endomorphism is cheap).
  Within a volcano, higher floors have larger CM order discriminants (more
  computationally expensive endomorphisms).

## Target profile reminder

From docs/target-result-profile.md: prefer mechanisms that move the asymptotic
exponent of ECDLP below 1/2 (Pollard rho exponent). A constant-factor speedup
is not target-class.

## Governing records

- `ledger/hypotheses/H-IT-001.yaml` (weakened; ordinary isogeny mechanism)
- `ledger/evidence/EV-IT-511f3d.yaml` (Tate theorem obstruction)
- `ledger/decisions/DEC-20260804-2fae6a.yaml` (reject_scoped + next action)
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-048/tasks/TASK-20260804-002/successor_directions.yaml`
- `docs/target-result-profile.md` and `docs/inventor-protocol.md`
