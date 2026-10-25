---
id: KN-FIND-7e2b94
type: internal_finding
title: "Non-anomalous curves: the canonical point section of E(Q_p) -> E(F_p) exists, is the prime-to-p torsion section, costs O(log n + k log p) additions, and the Smart functional vanishes on it; the 'full break' clause is false by derivation; three structured sections hit d mod p at the random rate (toy)"
tags: [p-adic-lift, canonical-lift, torsion-section, formal-group, smart-attack, non-anomalous, prime-field, elliptic-curve, derivation, toy-scale, scoped-negative]
confidence: established
confidence_note: "established for the derivation clauses (checkable argument, uniform in p >= 5 with n != p, re-checked by an independent validator and red team); the success-rate clauses are toy-scale measurements on two seeds with a 4.2x-5.2x detection floor; reviewer model identities not probe-verified"
internal_refs: [DEC-20261023-36b4f0, EV-CZLIFT-ad28f5, EXP-CZLIFT-ae0a13, H-CZLIFT-6d4ed1, RQ-CZLIFT-b9f765, RUN-CZLIFT-dab752, RUN-CZLIFT-5b2581, TASK-20261022-93fb1c, TASK-20261023-1d45b5, KN-TECH-73630e]
proof_status: derivation
proof_refs:
  - experiments/EXP-CZLIFT-ae0a13/analysis.md
  - experiments/EXP-CZLIFT-ae0a13/reports/redteam-20261023/redteam_report.yaml
  - knowledge/techniques/KN-TECH-73630e.md
added: 2026-10-23
superseded_by: null
---

Promoted by DEC-20261023-36b4f0 from EV-CZLIFT-ad28f5 (strength replicated).
It states no more than that record's supported_statement.

## Statement

Scope: ordinary E/F_p with p >= 5, a subgroup <P> of prime order n != p, and
any Z_p-lift E^ with good reduction.

By derivation, uniform in p (EXP-CZLIFT-ae0a13 analysis.md I-A, lemmas D1 to
D6): the n-torsion section s_tor is the unique homomorphic (equivalently
[c]-equivariant) section of reduction over <P>; it commutes with every
Z_p-endomorphism of E^ preserving <P> and, on the canonical lift, is the unique
Frobenius-fixed section; it is independent of the Hensel start and computable
as s_tor(R) = R^ - [n^{-1} mod p^k]([n]R^) in at most 2(bits(n)+bits(p^k))+1
complete additions at precision k; the Smart functional z([n]s(R)) vanishes
identically on it; for every section s the Smart ratio equals the
leading-digit tau-ratio with tau_R = s(R) - s_tor(R); and s_tor carries the
discrete-log relation s_tor(Q) = [d]s_tor(P) isomorphically into E^(Q_p)[n],
no easier. Hence the clause "a computable canonical section of
E(Q_p) -> E(F_p) would be a full break" is false under every reading in which
"canonical" constrains the section (homomorphic, filtration-splitting, [c]-,
End- or Frobenius-equivariant), and circular under the one remaining reading (a
section whose Smart residue recovers d is a discrete-log oracle by
definition).

Measured at toy scale (50 <= p <= 600, 11 <= n <= 613, k = 4, 36 curves per
seed, seeds 20261009 and 20261010; RUN-CZLIFT-dab752, RUN-CZLIFT-5b2581): for
the Hensel-random, naive-integer and Teichmuller sections, no identity-readout
success rate ("Smart ratio = d mod p") meeting the predefined 4-sigma threshold
was observed on class-number-one CM integral models or on random integer lifts.
Per arm and seed the test resolves only excesses of about 4.2x to 5.2x of 1/p;
a uniform leak at rate p^-1/2 is excluded with power >= 0.989. An independent
exhaustive control (all base points, all d, 71 curves) is within 0.97x to 1.06x
of a same-shape random-function null on both the canonical and a perturbed lift.

## Basis

- Derivation: Hensel surjectivity of reduction with kernel the formal group
  E^_1; for p >= 3 the formal logarithm makes E^_1 torsion-free and uniquely
  n-divisible, so Hom(Z/n, E^_1) = 0 (KN-TECH-73630e records the resulting
  reduction isomorphism E^(Q_p)[n] = E(F_p)[n]); uniqueness gives canonicity;
  z([n]u) = n z(u) + O(z(u)^2) gives the tau-identity.
- Instrument confirmation: torsion canonicity, homomorphism, degeneracy
  (v_p(z([n]s_tor)) = k), reduction and scalar equivariance on 1116 of 1116
  pairs; tau-identity on 3 x 1116 section-rows; an independent sealed blind
  re-derivation of s_tor agrees on 1116 of 1116 pairs (TASK-20261022-93fb1c);
  the red team (TASK-20261023-1d45b5) finds v = k at k = 2, 3, 4, 6, 8 and
  Frobenius-lift iteration converging to s_tor on 16 of 16 canonical j = 0
  lifts.
- Positive control: a planted leaking section s_tor + [log_P R]T is detected at
  rate 1 (frozen z +172 to +292), so the instrument does not prove too much.

## What this does not settle

- Not "the non-torsion sections carry no information about d": one readout
  (f = id) was tested, and planted discrete-log oracles with f(x) = n - x or
  x^2 mod n pass it while recovering d on 99-100 % of pairs.
- Not "every non-canonical section recovers d only at 1/p": false (planted
  sections).
- Not "the canonical curve lift contributes nothing": on the canonical j = 0
  lift the Teichmuller section is Aut(E^)-equivariant (multiplier set mu_6
  minus {1}, 16 of 16 curves) and a perturbed lift of the same reduction is
  not; the leaked information is the mu_6 orbit of d, already used by Pollard
  rho with automorphism classes. The frozen CM-vs-random arm comparison is
  confounded and powerless and is not evidence either way.
- The 1/p reference assumes H-1: the Smart residue of a choice-free section is
  uniform on F_p and independent of d outside the Aut(E^)-orbit of d; validated
  at toy scale only.
- Nothing about anomalous curves (n = p; EXP-CZLIFT-17b7eb), global lifts
  (H-CZLIFT-9a32e9), other functionals or readouts, cryptographic sizes, or
  ECDLP hardness. The construction cost is not a cost to break: a section
  "attack" at about 60 additions per attempt with success about 1/p is
  dominated by Pollard rho (about 2^264 against 2^128 at 256 bits).
- Correction records pending (DEC-20261023-36b4f0 N-2 to N-4) on the wording
  of RQ-CZLIFT-b9f765 decision_target (a), DEC-20261009-9f9254 and the
  H-CZLIFT-6d4ed1 mechanism; read those records with this entry's statement.
