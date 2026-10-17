# Ten lead formal model bridge and raw artifact access

- **Status:** `investigating`
- **Kind:** proof gap, independent-review gap, and access limit
- **Affected work:** [advisory register](../research/ten-lead-evidence/README.md),
  [torsion note](../research/ten-lead-evidence/torsion-proof-note.md), and
  [formal target](../formal/targets/scoped-odd-torsion-translation.yaml)
- **Next action owner:** unassigned independent semantic reviewer; current branch supplies the proof and handoff
- **Last updated:** 2026-10-17

## Problem

A generic algebraic theorem and hash-bound experiment summaries do not yet
certify their intended concrete curve applications or provide public access to
all raw evidence. These are separate proof and access requirements, not evidence
that any of the ten research directions is impossible.

For lead6, the formal target assumes an associative commutative addition with
zero, an odd scalar r=k+k+1, rP=0, T+T=0 and nonzero T. Its conclusion excludes
P+T from the scalar kernel. The file does not import elliptic-curve arithmetic,
a specific finite field, rational torsion, or factor-base membership.

## Evidence and uncertainty

- **Observed:** the imported register retains19 scoped records and ten open
  questions, bound to the original packet hashes. Raw packets were labelled
  private and are not uploaded in this public change.
- **Derived:** the generic odd-translation argument is stated in the linked
  note. The exact kernel status belongs to the separate verifier receipt;
  this problem record is not proof evidence.
- **Suspected explanation:** none needed; the missing bridge and access are explicit.
- **Missing capability:** independent semantic-fidelity review, a checked
  concrete-model bridge, and authorized raw-packet transport to readers that
  do not already have the files. Other formal obligations remain listed.
- **Not established:** a universal impossibility theorem, a complete rejection
  of torsion or genus methods, or a qualified ECDLP speedup.

## What would unblock it

- [ ] An independent reviewer confirms that the formal target matches the
  stated additive-law claim and is non-vacuous, without hidden assumptions.
- [ ] A concrete curve/domain bridge checks the intended operations, odd
  scalar, torsion and membership conditions for each application claimed.
- [ ] Authorized readers obtain the frozen raw packets and reproduce the
  relevant checks against their recorded digests, without declassifying private
  material by implication.

These conditions are necessary for the corresponding application and replay
claims. They do not prove all mechanisms in a broad research direction fail.

## Next discriminating step

- **Action:** verify the odd-torsion target using the existing formal worker;
  submit its statement and model boundary for independent semantic review.
- **Controls:** the explicit XOR model satisfies the positive hypotheses;
  even-scalar and zero-torsion strengthenings must be rejected by the kernel.
- **Execution limits:** the verifier's existing bounded build timeout; one
  pinned dependency-free workspace, no inference service or cloud rental.
- **Outcomes:** a kernel pass supplies formal evidence for the named statement
  only; a model mismatch requires a corrected target; a toolchain/access failure
  preserves an impediment and no mathematical conclusion. No outcome closes a lead.
- **Recheck trigger:** a new verifier receipt, semantic review, concrete bridge,
  or authorized artifact source.

## Resolution and history

Unresolved. This branch adds a reproducible formal target and an advisory
handoff; merging it does not discharge the model or review requirements.
