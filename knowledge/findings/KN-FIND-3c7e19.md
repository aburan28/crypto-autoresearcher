---
id: KN-FIND-3c7e19
type: internal_finding
title: "Smart's anomalous attack degenerates exactly on the canonical lift class mod p^2 (known Serre-Tate/Kummer theorem, instrument-calibrated at toy scale); the degenerate next digit matches the random-section null only pooled"
tags: [lifting, canonical-lift, serre-tate, smart-attack, anomalous, formal-group, p-adic, toy-scale, known-theory, instrument-calibration, czlift]
confidence: established
internal_refs: [EV-CZLIFT-712fe4, DEC-20261023-147f9f, EXP-CZLIFT-17b7eb, H-CZLIFT-889c9d, RUN-CZLIFT-041d05, RUN-CZLIFT-6709c9]
proof_status: derivation
proof_refs:
  - experiments/EXP-CZLIFT-17b7eb/reports/redteam-20261023/redteam_report.yaml
  - experiments/EXP-CZLIFT-17b7eb/reports/redteam-20261023/rt_r1_fiber_output.json
  - experiments/EXP-CZLIFT-17b7eb/reports/redteam-20261023/rt_r2_exact_output.json
  - experiments/EXP-CZLIFT-17b7eb/reports/redteam-20261023/rt_r2_homogeneity_output.json
  - experiments/EXP-CZLIFT-17b7eb/analysis.md
added: 2026-10-23
superseded_by: null
---

## Finding

This is known theory. It is not a discovery of this program; prior art is
Belding 2007, arXiv:math/0703906, section 7, retrieved and read by
TASK-20261023-856638. Let E/F_p be ordinary with #E(F_p) = p, and E^/Z_p an
unramified lift. Then:

- **Degeneracy is a property of the curve lift.** For every point and every
  point lift, v_p(z([p]P^)) >= 2 iff E^(Z/p^2) = (Z/p)^2. This holds iff the
  Kummer class of E^[p] vanishes, i.e. iff v_p(j(E^) - j_can) >= 2e (e = 3 at
  j = 0, else 1). Exactly one class of lifts mod p^2 out of p, the canonical
  class, is degenerate. Smart's precision-p^2 attack recovers d for every
  point lift off that class and for none on it.
  The derivation is red-team R1
  (`redteam_report.yaml`, `joint_findings.R1.derivation_two_sides_identical`).
  It is labelled derivation, not proved.
- **Calibration.** On 29 class-number-one CM anomalous curves with
  7 <= p <= 1373, two code-independent instruments implement the two sides:
  the point-arithmetic flag and the j-distance rule (harness/czlift.py,
  re-implemented by the validator and by the red team). They agreed on
  14,616/14,616 frozen rows (RUN-CZLIFT-041d05, RUN-CZLIFT-6709c9) and on
  12,778/12,778 red-team full-fiber lifts. Smart recovered d on 2,052/2,052
  non-degenerate rows per seed.
- **The degenerate next digit is section noise.** On a split lift with
  vP = 2, the precision-p^3 ratio equals d iff the section is d-homogeneous
  mod p^2 (verified on 4,214/4,214 rows). Under the random-section model the
  null depends on the definition (CORR-20261023-9f2176): 1/(p+1) over all
  v_p >= 2 rows; 1/p over vQ >= vP; 1/(p-1) over vQ = vP. Pooled over lifts
  and curves, the observed counts match: 93 and 87 against 86.84 (z = +0.68,
  +0.02), and z = +1.54, +0.75 against exact lift-conditioned nulls.
- **Per-cell exception.** On j = 0 lifts with A ≡ 0 mod p^2, the Teichmuller
  section is mu_6-equivariant and the automorphism acts on E_1/E_2 by the
  conjugate eigenvalue. So for d in mu_6 \ {±1} the ratio is d^{-1}, never d.
  Counterexample: p = 7, y^2 = x^3 + 5, rate 0 against 1/7.
  Deterministic sections have lift-specific rates, with relative sd about
  sqrt(11/p).

## What this does NOT establish

- No new obstruction and no new attack. The canonical lift is the one lift
  on which Smart fails; that is Serre-Tate theory and Belding 2007. On any
  non-canonical lift, anomalous curves are already polynomial-time.
- The next digit is not at "1/p per section". The 1/p reference does not
  match the all-v_p >= 2 definition.
- The frozen pooled test has power 0.05 against a single-section 1/sqrt(p)
  leak at p > 500. Large-p exclusions (1 to 3 successes per section in 1,200
  rows at p > 500, against 1.39 null and 40.3 under 1/sqrt(p)) are post hoc.
- The j = 0 threshold 2e = 6 is not measured. Over Z_p only (3, 6] is
  pinned.
- The measurements do not extend to non-anomalous curves (every lift behaves
  like the split case there; red-team PTM-1), to non-CM anomalous curves
  (red-team data only, p <= 211), to ramified lifts, to higher class number,
  or to cryptographic sizes.
- Smart 1999 is not cited for the canonical-lift failure. Its full text was
  not retrieved.

## Forward guidance

For any section-based lifting experiment on CM curves:

- state the matching null for each metric definition before the run;
- condition deterministic-section nulls on the lift;
- report mu_6 (j = 0) and mu_4 (j = 1728) pairs separately;
- preregister a large-p per-section statistic;
- record the lift coefficients and (P, d) in every row.

A "useful section" on the canonical lift is a homomorphic non-torsion
section mod p^2. Finding one is equivalent to DL. That is a reduction, not
an impossibility, and no theory takes it as a resource for ECDLP.

## Provenance

- `ledger/evidence/EV-CZLIFT-712fe4.yaml` (internal; strength replicated, tier toy)
- `ledger/decisions/DEC-20261023-147f9f.yaml` (internal; the promoting decision)
- `ledger/corrections/CORR-20261023-1869c3.yaml`, `ledger/corrections/CORR-20261023-9f2176.yaml` (internal; definition and matching null)
- `experiments/EXP-CZLIFT-17b7eb/reports/validation-20261022/validation_report.yaml` (internal; VAL-20261022-3232db)
- `experiments/EXP-CZLIFT-17b7eb/reports/redteam-20261023/redteam_report.yaml` (internal; RT-20261023-0b2a4f)
- Belding 2007, arXiv:math/0703906, section 7 (retrieved; verified_by TASK-20261023-856638)
- Katz, Serre-Tate local moduli, LNM 868 (recalled pointer; bibliography verified, content not)
