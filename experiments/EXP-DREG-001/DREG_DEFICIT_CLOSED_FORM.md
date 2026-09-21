# EXP-DREG-001 — the Semaev rank deficit has exact low-degree closed forms

Date: 2026-07-20. Follow-up to the n=18 null control (deficit=0, completed_valid).

## System family
Each (n, t=3, d=5, seed=2026) build produces a Boolean (GF(2), multilinear) system:
- `nb = 2n` Boolean variables (n=17 is the exception: nb = 2n+1 = 35, m = 34).
- exactly **n quadrics + n cubics** (eq_degs = {2:n, 3:n}).
- k = (n+2)//3 = dim V (the Semaev/factor-base subspace dimension); for n=3k, nb=6k.

`pred[D]` = Bardet–Faugère–Salvy semi-regular rank = coeff-sum of (1+z)^nb · ∏(1−z^{d_i}),
truncated at first non-positive coefficient. `deficit(D) = pred[D] − rank(D) ≥ 0` is the
excess quotient dimension = extra (non-Koszul) syzygies at degree D.

## Null arm is exact (control)
deficit = 0 at n = 12, 15, 17, 18 (every replicate). So any sem-arm deficit is real
structure, not predictor bias.

## Degree-resolved sem deficit (graded, per degree D)
| n  | k | nb | D=3 | D=4 | D=5  |
|----|---|----|-----|-----|------|
|  9 | 3 | 18 |  0* |  23 |  577 |
| 12 | 4 | 24 |  1  |  31 | 1290 |
| 15 | 5 | 30 |  1  |  39 | 1822 |
| 17 | 6 | 35 |  1  |  45 | 1777 |  (deficient system: nb=2n+1, m=2n)
| 18 | 6 | 36 |  1  |  47 | 1951 |
| 21 | 7 | 42 |  1  |  55 |  —   |
(* n=9 has only 8 quadrics, so no degree-3 syzygy.)

## Closed forms (exact)
1. **deficit at D=3 = 1** for every full system (n≥12); = 0 when quadrics are deficient (n=9).
   A single structural degree-3 syzygy, n-independent.
2. **deficit at D=4 = 8k − 1**, confirmed exactly for k = 3,4,5,6,7 (n = 9,12,15,18,21).
   Equivalently (4·nb − 3)/3 for full systems. n=17 gives 45 (not 47) precisely because it
   is variable-deficient (nb=35, m=34) — 2 below the full k=6 value.

## The original puzzle, resolved
The cumulative D=5 deficit (1322, 1862, 1823, 1999 for n=12,15,17,18) looked "bounded but
non-monotonic" (15→17 dips). Two artifacts, now explained:
- The 15→17 dip is **not** a smaller deficit — n=17 is a structurally *deficient* system
  (one fewer Boolean variable, two fewer equations than a full k=6 system).
- The D=5 graded deficit is **not polynomial in k** (differences 713, 532, 129 for
  k=3→4→5→6): D=5 sits at different depths relative to each system's degree of regularity,
  so a fixed-degree cross-section mixes regimes. The clean, regime-consistent invariants
  live at low degree (D=3, D=4), where exact closed forms hold.

## Interpretation / mechanism (2026-07-20 investigation)
The deficit is **structural syzygy content, not stochastic**: its onset (D=3, D=4) is an
exact closed form in k = dim V. This upgrades "d_reg bounded, not growing" from *observed* to
*explained* at the onset.

**Two hypotheses tested; both refined by data:**
1. *Frobenius self-relations q_i^2 = q_i* — REFUTED. Those hold in EVERY Boolean ring incl.
   the null arm, and null deficit = 0 (confirmed def3=def4=0 directly for n=12). So Frobenius
   cannot be the source; the entire 8k−1 is **Semaev-specific** (structure a random system of
   identical shape lacks).
2. *Clean variable separation (quadrics from E2=S3(u1,x3,R_X) live only in {u1,x3})* — REFUTED
   by direct measurement: every generator touches all four variable classes {u1,x1,x2,x3}.
   The α-Weil-descent fully couples coordinates; the symbolic degree split does not survive
   into variable supports.

**What IS established about the mechanism:**
- Construction (t=3): TWO chained Semaev equations over F_q — E1=S3(u1,x1,x2) (all unknowns,
  keeps the u1x1x2 cubic term) and E2=S3(u1,x3,R_X) (R_X constant) — each Weil-descended to n
  Boolean polys (n+3k Boolean vars: u1 full field n coords, x1/x2/x3 in V, k coords each).
  In char 2 the square part (ab+ac+bc)^2 = a^2b^2+a^2c^2+b^2c^2 and squaring a descended var
  is LINEAR (Frobenius on the α-basis), so field-degree-4 Semaev descends to Boolean deg 2/3.
- The deficit = **Weil-descent α-orbit / shared-factor syzygies** (the "α-stable, λ-redundant"
  relations of the isogeny-Semaev work), which a random F2 system cannot have (null=0).
- The degree-3 syzygy is EXHIBITED as a product relation **(sum of quadrics)·(affine L) = 0**,
  factoring cleanly for every n tested (n=12,15,18). Supports are coordinate-dependent
  (|Q|=8,7,7; |L|=4,4,1) but the count is robust — the signature of a graded Betti number
  (deterministic dimension, coordinate-dependent generators).
- **SHARPENED (verified directly, `characterization/syzygy_degree3.py`): the mechanism is an
  AFFINE DEGENERATION.** The subset-sum Q = Σ_{i∈S} q_i is itself affine (degree ≤ 1) — the
  quadratic parts cancel identically — and the multiplier is its exact complement, L = 1 + Q.
  So the syzygy is the Boolean identity **P·(1+P) = P + P² = 0** (char 2: squaring is additive
  and z² = z) applied to a DERIVED affine form P. At n=18 the sum of 7 quadrics collapses to
  the single variable z18. The Semaev-specific content is thus the degeneration itself — that
  an F₂-subset-sum of the descended quadrics drops to affine — which the support-matched null
  never admits (degree-3 kernel = 0 at n=12,15,18). This refines hypothesis 1 above: Frobenius
  supplies the FORM of the relation, the degeneration supplies the CONTENT; only the latter is
  Semaev-specific.

## Degree-4 syzygy characterization (computational, 2026-07-20)
Isolated the extra (Semaev-specific) syzygies = real left-kernel(M4) modulo the generic space,
for the full systems n=12,15,18 (k=4,5,6):
- **Generic baseline VALIDATED**: the generic degree-4 syzygies are EXACTLY nq Frobenius
  (q_i^2=q_i) + C(nq,2) Koszul pairs. rank(G) = nrows − pred[4] exactly (78,120,171). So the
  semi-regular prediction's "expected" syzygies are precisely the classical trivial ones.
- **Cumulative deficit = 8·dim(V) exactly**: defcum(4) = 32,40,48 = 8k for k=4,5,6.
  (= def3=1 + def4graded=8k−1.) The natural clean statement is **defcum(4) = 8k**.
- REFUTED sub-pattern: def4graded = (5k−1) lifts-of-r0 + 3k new-seeds holds ONLY at k=4
  (coincidence). The lift/seed split is coordinate-dependent noise (lifts 20/26/35,
  seeds 12/14/13 for k=4/5/6) because it depends on the coordinate-dependent degree-3
  relation r0 (|L support| = 4/4/1). The INVARIANT is the total 8k, not the split.
- Method note: this isolation is valid only for FULL systems (n=3k). For n=9 (nb=18,
  over-determined) the generic space is much larger than Frob+Koszul, so the isolation breaks
  — which is the same reason n=9/n=17 are deficient outliers.

**Refined mechanism hypothesis:** defcum(4) = 8·dim(V) = **8 extra syzygies per V-direction**.
Two candidate explanations, in order of promise after the degree-3 result:
1. **Count the degeneracies (favoured).** Degree 3 is now understood as an affine degeneration
   of a subset-sum of descended quadrics. Conjecture: 8k likewise counts the F₂-subset-sums
   c ∈ F₂^m with deg(Σ c_i f_i) < max deg — a degeneracy subspace fixed by the Weil-descent
   coefficient structure. Directly computable by linear algebra; would turn 8k into a derived
   count rather than a measured one.
2. α-orbits (size 8) under field/α-multiplication — see the negative result below.

## α-orbit test (2026-07-20): NEGATIVE for the naive action
Tested whether the extra syzygy space is invariant under the field α-multiplication realized as
the companion matrix C acting block-wise on the descent components (generator index only, combos
fixed). Result: NOT invariant — 110/110 kernel and 78/78 generic-G basis vectors fail. Since the
action fails even on the universal Frobenius+Koszul space G, the operator is wrong/incomplete: the
correct α-action must ALSO transform the Boolean variables (u1 is a full-field variable), coupling
generator-component shift with variable-coordinate shift. That is a Weil-restriction module
calculation, not a one-probe test. Likely the right symmetry is the Frobenius x↦x^2 (a field
automorphism fixing F2, so it preserves the ideal AND G), whose descent-orbit structure could
explain the "8"; unverified.

**Status:** the deficit is characterized (Semaev-specific; generic baseline = classical trivial
syzygies exactly; deficit = 8·dim(V); product/shared-factor syzygies). The "8 per V-direction =
k α-orbits of 8" is a HYPOTHESIS motivated by the count; the simplest α-action does NOT confirm
it. A full derivation needs the correct Weil-restriction/Frobenius symmetry — theory-level work.

## Reproduce
Probes in scratchpad: probe_system.py (invariants), probe_degres.py (n=12 profile),
probe_degres_all.py (n=15/17/18), probe_confirm.py (fresh n=9/21). Each imports
build_system / semireg_rank_pred / peel_and_rank / macaulay_rows from the archived code
snapshot at runs/RUN-DREG-001-VALIDATE-N12-A/code/. Exact GF(2) rank via peel_and_rank.
