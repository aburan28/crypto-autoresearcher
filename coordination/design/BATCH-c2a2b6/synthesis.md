# SDEG protocol review synthesis

## Disposition

`DEC-20260908-ec4a02` is a **revise** disposition. The review does not approve
implementation of `EXP-ECDLP-ac7e8b`. The hypothesis remains proposed and the
goal remains active.

The independent arithmetic continuation holds for its defined source-level
interface. It agrees with the blind derivation on every one of the five
calibrators and nineteen adapter cases once the complete source packet is
available. The preceding blind report remains accurate about the smaller packet
it actually received and is not modified.

The other three scoped reviewers identify repairable pre-implementation defects:

| Joint | Disposition | Required amendment boundary |
| --- | --- | --- |
| paired measurement and statistics | breaks | Pair/profile identifiers, exact estimator and rational threshold, missingness/edge/bootstrap/load/drift definitions. |
| resources, lifecycle, and authority | breaks | Worker/reap lifecycle, receipt and terminal schema, administrative omissions, rank and shared-cost ownership. |
| algebra and legal certificates | breaks | Exact imported contract bytes in a new packet and deterministic signed/aliased column controls. |

## Evidence boundary

All reviewed material is prospective protocol reasoning. No code, fixture,
solver, profile, calibration, bootstrap, receipt validator, implementation, or
scientific run occurred. The review neither supports nor weakens the ECDLP
hypothesis and establishes no performance, attack, security, or asymptotic
claim.

## Required successor

The successor must be additive and versioned. It must preserve the current
frozen source and reports byte-for-byte, retain the 20 random scientific
instances, and label all new certificate/lifecycle/statistical cases as
admission controls. It must receive a new source binding and a fresh review
plan whose packets contain every normatively imported byte. Implementation
remains prohibited until that successor passes its independent review and the
Coordinator records a separate approval under the standing authorization.
