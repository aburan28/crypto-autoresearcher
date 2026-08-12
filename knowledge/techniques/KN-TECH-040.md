---
id: KN-TECH-040
type: technique
title: Core-SVP costing and the lattice cost-model zoo
tags: [core-svp, cost-model, convention, gate-count, ram-model, security-estimate, bkz, sieving, parameter-selection, calibration, lattice]
confidence: reported
complexity: single SVP oracle call at 2^(0.292b) classical / 2^(0.265b) quantum, with a 2^(0.2075b) "best plausible" floor; polynomial factors and oracle-call counts deliberately discarded
applicability: quoting or comparing any concrete lattice security level; mandatory context for reading any bit-security number in the post-quantum literature
source_refs: [KN-LIT-107, KN-LIT-104, KN-LIT-101, KN-LIT-122, KN-LIT-110, KN-TECH-035]
added: 2026-07-24
superseded_by: null
---

## Method
Core-SVP hardness, introduced in KN-LIT-107, prices a lattice attack as the cost
of **one** call to an SVP oracle in the BKZ block dimension `b`, discarding the
polynomial number of calls BKZ actually makes and all polynomial factors. The
oracle is priced as a sieve: `2^(0.292b)` classically (KN-LIT-048),
`2^(0.265b)` with Grover-type speedup, and `2^(0.2075b)` as a "best plausible"
floor derived from the kissing-number list size (KN-LIT-104). KN-LIT-107 is
explicit that this is pessimistic from the defender's point of view, and that
the suppressed sub-exponential factor is much greater than one in practice.

## Why the convention matters more than the number
Core-SVP is one point in a zoo of conventions, and the differences are large
enough to swallow any plausible algorithmic advance:

- **Oracle calls.** Core-SVP charges one; other estimates charge `8d` calls for
  embedding dimension `d`. That is a multiplicative factor, i.e. an additive
  shift in bits.
- **Additive constants.** Some estimates append `+16.4` to the sieve exponent
  from measured implementation overhead; some omit it; some keep an explicit
  `beta` or `log beta` polynomial factor.
- **Sieve variant.** "Min-space" sieving is priced at a different exponent than
  time-optimal sieving.
- **Gate counts versus operations.** KN-LIT-122 costs quantum sieving at the
  circuit level and finds the realisable speedup small; KN-LIT-110 obtains part
  of its claimed security reduction purely by revising those gate counts
  downward.

The last point is the one to internalise. In KN-LIT-110 a headline result --
NIST finalists below their required security levels -- is driven substantially
by re-costing an existing algorithm rather than by a new attack. In lattice
cryptanalysis the cost model is part of the claim.

## Applicability limits
Core-SVP is a *lower bound convention for parameter selection*, deliberately
generous to the attacker so that chosen parameters are safe. It is not a
prediction of wall-clock effort, and a scheme whose core-SVP level dips below a
threshold has not been broken. Conversely, the convention is useless for
comparing two attacks unless both are expressed in it. Any program statement
comparing lattice costs must name the convention on both sides, exactly as the
program requires the ECDLP baseline to state `0.886*sqrt(n)` on the prime
subgroup order (KN-TECH-030) and to say whether memory is charged
(KN-TECH-035, KN-TECH-044).

## Verified vs reported
The core-SVP definition, the three exponents, and the stated pessimism are read
directly from KN-LIT-107 Section 6. The MATZOV re-costing and its magnitude are
read from KN-LIT-110's introduction and Table 1. The catalogue of alternative
conventions is assembled from the way these sources describe each other and has
not been checked against a single authoritative tabulation; treat the list as
indicative of the *kinds* of divergence, not as exhaustive.
