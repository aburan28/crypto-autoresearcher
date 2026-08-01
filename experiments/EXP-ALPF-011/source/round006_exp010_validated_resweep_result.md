# EXP-010 Result: validated-meter re-sweep of m=3 Semaev representations

SEED=42  timestamp=2026-05-30 23:43:48

Meter imported via `load()` from `round005_meter_validation.sage` (validated nontrivial-syzygy / Bardet-Faugere-Salvy first-fall meter on homogeneous leading forms).

## 1. Meter self-validation (MANDATORY, reported first)

| control | d_ff | D_reg_pred | fires | required | OK |
|---|---|---|---|---|---|
| POS-A (3 cubics, shared quadratic leading factor) | 4 | 7 | True | fire @ d_ff=4<D_reg=7 | True |
| NEG-1 (3 generic quadrics, regular CI) | 4 | 4 | False | quiet | True |
| NEG-2 (3 generic cubics, regular) | 7 | 7 | False | quiet | True |

**METER_SELF_VALIDATED = True**

## 2. Per-representation per-cell results (d_ff / D_reg_pred / fires)

Leading-form degree profile is the homogeneous top-form degrees actually fed to the meter.

| curve | bits | |FB| | rep | leading-form degs | d_ff | D_reg_pred | fires |
|---|---|---|---|---|---|---|---|
| structured | 13 | 4 | (A) x-ring baseline | [4, 4, 4, 12] | 10 | 10 | False |
| structured | 13 | 4 | (B) e-ring (elem sym) | [2, 2, 2, 4] | 3 | 4 | True |
| structured | 13 | 4 | (C) power-sum | [2, 3, 4, 12] | 3 | 7 | True |
| structured | 13 | 4 | (D) pullback x=t^2 | [3, 3, 3, 24] | 7 | 7 | False |
| structured | 13 | 4 | (D) pullback x=t^2+c | [1, 1, 1, 24] | 1 | 1 | False |
| structured | 13 | 5 | (A) x-ring baseline | [5, 5, 5, 12] | 12 | 12 | False |
| structured | 13 | 5 | (B) e-ring (elem sym) | [3, 3, 3, 4] | 4 | 5 | True |
| structured | 13 | 5 | (C) power-sum | [3, 4, 5, 12] | 4 | 10 | True |
| structured | 13 | 5 | (D) pullback x=t^2 | [3, 3, 3, 24] | 7 | 7 | False |
| structured | 13 | 5 | (D) pullback x=t^2+c | [1, 1, 1, 24] | 1 | 1 | False |
| structured | 15 | 4 | (A) x-ring baseline | [4, 4, 4, 12] | 10 | 10 | False |
| structured | 15 | 4 | (B) e-ring (elem sym) | [2, 2, 2, 4] | 3 | 4 | True |
| structured | 15 | 4 | (C) power-sum | [2, 3, 4, 12] | 3 | 7 | True |
| structured | 15 | 4 | (D) pullback x=t^2 | [1, 1, 1, 24] | 1 | 1 | False |
| structured | 15 | 4 | (D) pullback x=t^2+c | [1, 1, 1, 24] | 1 | 1 | False |
| structured | 15 | 5 | (A) x-ring baseline | [5, 5, 5, 12] | 12 | 12 | False |
| structured | 15 | 5 | (B) e-ring (elem sym) | [3, 3, 3, 4] | 4 | 5 | True |
| structured | 15 | 5 | (C) power-sum | [3, 4, 5, 12] | 4 | 10 | True |
| structured | 15 | 5 | (D) pullback x=t^2 | [2, 2, 2, 24] | 4 | 4 | False |
| structured | 15 | 5 | (D) pullback x=t^2+c | [2, 2, 2, 24] | 4 | 4 | False |
| structured | 17 | 4 | (A) x-ring baseline | [4, 4, 4, 12] | 10 | 10 | False |
| structured | 17 | 4 | (B) e-ring (elem sym) | [2, 2, 2, 4] | 3 | 4 | True |
| structured | 17 | 4 | (C) power-sum | [2, 3, 4, 12] | 3 | 7 | True |
| structured | 17 | 4 | (D) pullback x=t^2 | [2, 2, 2, 24] | 4 | 4 | False |
| structured | 17 | 4 | (D) pullback x=t^2+c | [2, 2, 2, 24] | 4 | 4 | False |
| structured | 17 | 5 | (A) x-ring baseline | [5, 5, 5, 12] | 12 | 12 | False |
| structured | 17 | 5 | (B) e-ring (elem sym) | [3, 3, 3, 4] | 4 | 5 | True |
| structured | 17 | 5 | (C) power-sum | [3, 4, 5, 12] | 4 | 10 | True |
| structured | 17 | 5 | (D) pullback x=t^2 | [3, 3, 3, 24] | 7 | 7 | False |
| structured | 17 | 5 | (D) pullback x=t^2+c | [3, 3, 3, 24] | 7 | 7 | False |
| structured | 19 | 4 | (A) x-ring baseline | [4, 4, 4, 12] | 10 | 10 | False |
| structured | 19 | 4 | (B) e-ring (elem sym) | [2, 2, 2, 4] | 3 | 4 | True |
| structured | 19 | 4 | (C) power-sum | [2, 3, 4, 12] | 3 | 7 | True |
| structured | 19 | 4 | (D) pullback x=t^2 | [2, 2, 2, 24] | 4 | 4 | False |
| structured | 19 | 4 | (D) pullback x=t^2+c | [4, 4, 4, 24] | 10 | 10 | False |
| structured | 19 | 5 | (A) x-ring baseline | [5, 5, 5, 12] | 12 | 12 | False |
| structured | 19 | 5 | (B) e-ring (elem sym) | [3, 3, 3, 4] | 4 | 5 | True |
| structured | 19 | 5 | (C) power-sum | [3, 4, 5, 12] | 4 | 10 | True |
| structured | 19 | 5 | (D) pullback x=t^2 | [3, 3, 3, 24] | 7 | 7 | False |
| structured | 19 | 5 | (D) pullback x=t^2+c | [5, 5, 5, 24] | 13 | 13 | False |
| random | 13 | 4 | (A) x-ring baseline | [4, 4, 4, 12] | 10 | 10 | False |
| random | 13 | 4 | (B) e-ring (elem sym) | [2, 2, 2, 4] | 3 | 4 | True |
| random | 13 | 4 | (C) power-sum | [2, 3, 4, 12] | 3 | 7 | True |
| random | 13 | 4 | (D) pullback x=t^2 | [3, 3, 3, 24] | 7 | 7 | False |
| random | 13 | 4 | (D) pullback x=t^2+c | [1, 1, 1, 24] | 1 | 1 | False |
| random | 13 | 5 | (A) x-ring baseline | [5, 5, 5, 12] | 12 | 12 | False |
| random | 13 | 5 | (B) e-ring (elem sym) | [3, 3, 3, 4] | 4 | 5 | True |
| random | 13 | 5 | (C) power-sum | [3, 4, 5, 12] | 4 | 10 | True |
| random | 13 | 5 | (D) pullback x=t^2 | [3, 3, 3, 24] | 7 | 7 | False |
| random | 13 | 5 | (D) pullback x=t^2+c | [2, 2, 2, 24] | 4 | 4 | False |
| random | 15 | 4 | (A) x-ring baseline | [4, 4, 4, 12] | 10 | 10 | False |
| random | 15 | 4 | (B) e-ring (elem sym) | [2, 2, 2, 4] | 3 | 4 | True |
| random | 15 | 4 | (C) power-sum | [2, 3, 4, 12] | 3 | 7 | True |
| random | 15 | 4 | (D) pullback x=t^2 | [3, 3, 3, 24] | 7 | 7 | False |
| random | 15 | 4 | (D) pullback x=t^2+c | [2, 2, 2, 24] | 4 | 4 | False |
| random | 15 | 5 | (A) x-ring baseline | [5, 5, 5, 12] | 12 | 12 | False |
| random | 15 | 5 | (B) e-ring (elem sym) | [3, 3, 3, 4] | 4 | 5 | True |
| random | 15 | 5 | (C) power-sum | [3, 4, 5, 12] | 4 | 10 | True |
| random | 15 | 5 | (D) pullback x=t^2 | [3, 3, 3, 24] | 7 | 7 | False |
| random | 15 | 5 | (D) pullback x=t^2+c | [2, 2, 2, 24] | 4 | 4 | False |
| random | 17 | 4 | (A) x-ring baseline | [4, 4, 4, 12] | 10 | 10 | False |
| random | 17 | 4 | (B) e-ring (elem sym) | [2, 2, 2, 4] | 3 | 4 | True |
| random | 17 | 4 | (C) power-sum | [2, 3, 4, 12] | 3 | 7 | True |
| random | 17 | 4 | (D) pullback x=t^2 | [3, 3, 3, 24] | 7 | 7 | False |
| random | 17 | 4 | (D) pullback x=t^2+c | [2, 2, 2, 24] | 4 | 4 | False |
| random | 17 | 5 | (A) x-ring baseline | [5, 5, 5, 12] | 12 | 12 | False |
| random | 17 | 5 | (B) e-ring (elem sym) | [3, 3, 3, 4] | 4 | 5 | True |
| random | 17 | 5 | (C) power-sum | [3, 4, 5, 12] | 4 | 10 | True |
| random | 17 | 5 | (D) pullback x=t^2 | [3, 3, 3, 24] | 7 | 7 | False |
| random | 17 | 5 | (D) pullback x=t^2+c | [2, 2, 2, 24] | 4 | 4 | False |
| random | 19 | 4 | (A) x-ring baseline | [4, 4, 4, 12] | 10 | 10 | False |
| random | 19 | 4 | (B) e-ring (elem sym) | [2, 2, 2, 4] | 3 | 4 | True |
| random | 19 | 4 | (C) power-sum | [2, 3, 4, 12] | 3 | 7 | True |
| random | 19 | 4 | (D) pullback x=t^2 | [1, 1, 1, 24] | 1 | 1 | False |
| random | 19 | 4 | (D) pullback x=t^2+c | [2, 2, 2, 24] | 4 | 4 | False |
| random | 19 | 5 | (A) x-ring baseline | [5, 5, 5, 12] | 12 | 12 | False |
| random | 19 | 5 | (B) e-ring (elem sym) | [3, 3, 3, 4] | 4 | 5 | True |
| random | 19 | 5 | (C) power-sum | [3, 4, 5, 12] | 4 | 10 | True |
| random | 19 | 5 | (D) pullback x=t^2 | [1, 1, 1, 24] | 1 | 1 | False |
| random | 19 | 5 | (D) pullback x=t^2+c | [2, 2, 2, 24] | 4 | 4 | False |

## 3. Which representations fire vs not

| rep | cells measured | cells firing (d_ff<D_reg) | cells d_ff=D_reg |
|---|---|---|---|
| (A) x-ring baseline | 16 | 0 | 16 |
| (B) e-ring (elem sym) | 16 | 16 | 0 |
| (C) power-sum | 16 | 16 | 0 |
| (D) pullback x=t^2 | 16 | 0 | 16 |
| (D) pullback x=t^2+c | 16 | 0 | 16 |

## 4. Sanity vs EXP-009 (x-ring D_reg must match 7/10/12 for |FB|=3/4/5)

| curve | bits | |FB| | x-ring D_reg | EXP-009 expected | match |
|---|---|---|---|---|---|
| structured | 13 | 4 | 10 | 10 | True |
| structured | 13 | 5 | 12 | 12 | True |
| structured | 15 | 4 | 10 | 10 | True |
| structured | 15 | 5 | 12 | 12 | True |
| structured | 17 | 4 | 10 | 10 | True |
| structured | 17 | 5 | 12 | 12 | True |
| structured | 19 | 4 | 10 | 10 | True |
| structured | 19 | 5 | 12 | 12 | True |
| random | 13 | 4 | 10 | 10 | True |
| random | 13 | 5 | 12 | 12 | True |
| random | 15 | 4 | 10 | 10 | True |
| random | 15 | 5 | 12 | 12 | True |
| random | 17 | 4 | 10 | 10 | True |
| random | 17 | 5 | 12 | 12 | True |
| random | 19 | 4 | 10 | 10 | True |
| random | 19 | 5 | 12 | 12 | True |

**x-ring matches EXP-009 D_reg in all measured cells: True**

## 5. Verdict

POSITIVE (SURVIVED) -- at least one PRIME-FIELD m=3 representation genuinely early-falls (d_ff < D_reg) under the validated meter. This is the campaign's FIRST prime-field algebra-track positive. See firing cells below; escalate per EXP-011.

## 6. What fires / what is now bankable

Firing cells (prime-field POSITIVE -- give exact system):
- structured 13b |FB|=4 rep=(B) e-ring (elem sym): leading-form degs=[2, 2, 2, 4], d_ff=3 < D_reg=4
- structured 13b |FB|=4 rep=(C) power-sum: leading-form degs=[2, 3, 4, 12], d_ff=3 < D_reg=7
- structured 13b |FB|=5 rep=(B) e-ring (elem sym): leading-form degs=[3, 3, 3, 4], d_ff=4 < D_reg=5
- structured 13b |FB|=5 rep=(C) power-sum: leading-form degs=[3, 4, 5, 12], d_ff=4 < D_reg=10
- structured 15b |FB|=4 rep=(B) e-ring (elem sym): leading-form degs=[2, 2, 2, 4], d_ff=3 < D_reg=4
- structured 15b |FB|=4 rep=(C) power-sum: leading-form degs=[2, 3, 4, 12], d_ff=3 < D_reg=7
- structured 15b |FB|=5 rep=(B) e-ring (elem sym): leading-form degs=[3, 3, 3, 4], d_ff=4 < D_reg=5
- structured 15b |FB|=5 rep=(C) power-sum: leading-form degs=[3, 4, 5, 12], d_ff=4 < D_reg=10
- structured 17b |FB|=4 rep=(B) e-ring (elem sym): leading-form degs=[2, 2, 2, 4], d_ff=3 < D_reg=4
- structured 17b |FB|=4 rep=(C) power-sum: leading-form degs=[2, 3, 4, 12], d_ff=3 < D_reg=7
- structured 17b |FB|=5 rep=(B) e-ring (elem sym): leading-form degs=[3, 3, 3, 4], d_ff=4 < D_reg=5
- structured 17b |FB|=5 rep=(C) power-sum: leading-form degs=[3, 4, 5, 12], d_ff=4 < D_reg=10
- structured 19b |FB|=4 rep=(B) e-ring (elem sym): leading-form degs=[2, 2, 2, 4], d_ff=3 < D_reg=4
- structured 19b |FB|=4 rep=(C) power-sum: leading-form degs=[2, 3, 4, 12], d_ff=3 < D_reg=7
- structured 19b |FB|=5 rep=(B) e-ring (elem sym): leading-form degs=[3, 3, 3, 4], d_ff=4 < D_reg=5
- structured 19b |FB|=5 rep=(C) power-sum: leading-form degs=[3, 4, 5, 12], d_ff=4 < D_reg=10
- random 13b |FB|=4 rep=(B) e-ring (elem sym): leading-form degs=[2, 2, 2, 4], d_ff=3 < D_reg=4
- random 13b |FB|=4 rep=(C) power-sum: leading-form degs=[2, 3, 4, 12], d_ff=3 < D_reg=7
- random 13b |FB|=5 rep=(B) e-ring (elem sym): leading-form degs=[3, 3, 3, 4], d_ff=4 < D_reg=5
- random 13b |FB|=5 rep=(C) power-sum: leading-form degs=[3, 4, 5, 12], d_ff=4 < D_reg=10

## 7. Next structure to test

- EXP-011: take the firing system, run an explicit graded Macaulay / F4 step-degree solve, confirm the GB falls at d_ff, and compute the HONEST index-calculus cost (relations needed, relation probability, rank, target descent) vs Pollard rho at the swept sizes and extrapolated.

---

## 8. RED-TEAM CORRECTION (engineer override of the Section-5 auto-verdict)

The Section-5 auto-verdict reads "POSITIVE (SURVIVED)" because (B) e-ring and
(C) power-sum reported d_ff < D_reg in 16/16 cells. Per the campaign integrity
posture (all five prior rounds self-labeled a positive the verifier overturned;
a verdict is only as good as its discriminating controls), three discriminators
were run; they OVERTURN the self-labeled positive but for a DIFFERENT, sharper
reason than a generic-profile artifact.

### Measured tally (this run, validated meter, seed 42, 16 cells)

| rep | actual leading-form degree profile fed to meter | fires (d_ff<D_reg) |
|---|---|---|
| (A) x-ring | [12,4,4,4] (|FB|=4), [12,5,5,5] (|FB|=5) | 0/16 (d_ff=D_reg=10/12; matches EXP-009) |
| (B) e-ring | [4,2,2,2] (|FB|=4), [4,3,3,3] (|FB|=5) -- S4 top form COLLAPSED to deg 4 | 16/16 |
| (C) power-sum | [12,4,3,2] (|FB|=4), [12,5,4,3] (|FB|=5) | 16/16 |
| (D) pullback x=t^2 / t^2+c | [24,...] | 0/16 |

Meter self-validation (inline, MANDATORY): POS-A d_ff=4 < D_reg=7 FIRES=True;
NEG-1 quiet; NEG-2 quiet. METER_SELF_VALIDATED = True.

### Discriminator 1 -- generic-twin on the ACTUAL profiles (`/tmp/exp010_redteam2.sage`)

Random structureless systems with the EXACT measured profiles do NOT fire:

```
GENERIC [2,2,2,4]  : d_ff=4 = D_reg=4  FIRES=False
GENERIC [3,3,3,4]  : d_ff=5 = D_reg=5  FIRES=False
GENERIC [2,3,4,12] : d_ff=7 = D_reg=7  FIRES=False
GENERIC [3,4,5,12] : d_ff=10= D_reg=10 FIRES=False
```

So the e-ring/power-sum fires are NOT generic degree-profile artifacts: a random
system with the same degrees is regular. The fire is therefore caused by the
SPECIFIC leading forms the symmetric rewrite produces. Discriminator 2 identifies
that structure.

### Discriminator 2 -- leading-form structure of the real e-ring system (`/tmp/exp010_ering_probe.sage`, curve p=4079, a=-3)

```
e-ring gen total_degrees = [4,2,2,2]
leading forms: h0 (deg 4, dense);  h1 = e1*e3 ;  h2 = -e1*e2 ;  h3 = e1^2
gcd(h1,h2)=e1 ; gcd(h1,h3)=e1 ; gcd(h2,h3)=e1   <-- ALL THREE FB leading forms share the factor e1
REAL e-ring meter: d_ff=3 < D_reg=4  FIRES=True
GENERIC [4,2,2,2] twin: d_ff=4 = D_reg=4  FIRES=False
```

The THREE degree-2 FB-membership leading forms are e1*e3, e1*e2, e1^2 -- they all
carry the common factor e1, exactly the POS-A early-fall mechanism (shared factor
=> degree-3 syzygy below D_reg). This is a GENUINE syzygy of the homogeneous
leading-form system, and the meter correctly detects it. BUT it is a COORDINATE
artifact of the symmetric rewrite, not a reduction of the Semaev decomposition
difficulty: the early fall lives entirely in the FB-membership leading forms (which
factor through e1 because the symmetric FB constraints are reductions of a single
polynomial modulo t^3 - e1 t^2 + e2 t - e3), NOT in the summation polynomial S4.
The Semaev information sits in the dense degree-4 top form h0, which is untouched.

### Discriminator 3 -- does the early fall buy a cheaper SOLVE? (`/tmp/exp010_ering_validity.sage`)

```
x-ring [12,4,4,4] and e-ring [4,2,2,2] on the toy FB cells: Groebner basis = (1)
  (unit ideal: dim=-1, ngb=1) -- the randomly-sampled FB x-coords are not a real
  decomposition, so BOTH systems are inconsistent and the GB-degree comparison is
  uninformative at these cells.
```

The honest GB-cost comparison was INCONCLUSIVE at the toy cells (the sampled FB is
not an actual decomposition, so the systems are inconsistent). This does NOT rescue
the e-ring: the early fall is already explained (Discriminator 2) as a shared-factor
degeneracy of the FB-membership leading forms, and it does not touch the Semaev top
form. A leading-form syzygy that lives only in the FB constraints and leaves S4 at
full degree 4 (e-ring) / 12 (power-sum) does not lower the cost of the actual
decomposition solve.

### CORRECTED VERDICT: FAILED (BANKABLE NEGATIVE)

No prime-field m=3 re-coordinatization exhibits a GENUINE, EXPLOITABLE early fall
of the Semaev decomposition:

- (A) x-ring        : d_ff=D_reg, matches EXP-009, the only rep posing the
                      undegenerate decomposition. NO fall.
- (B) e-ring        : d_ff<D_reg is a COORDINATE-ARTIFACT shared-factor syzygy --
                      the three FB-membership leading forms all carry the factor e1
                      (POS-A mechanism), living entirely in the FB constraints, NOT
                      in S4. Generic twin is regular. NOT a Semaev-difficulty drop.
- (C) power-sum     : same -- early fall from the FB-membership leading forms while
                      S4 stays at full degree 12. NOT a Semaev-difficulty drop.
- (D) pullback x=t^2, t^2+c : no fire. NO fall.

This converts the previously INCONCLUSIVE NR-009 (e-ring), NR-010/012/013
(power-sum / D_reg-conservation), and NR-015 (rational-map pullback) into a single
VALIDATED multi-representation NEGATIVE for the m=3 prime-field Semaev decomposition
system. The x-ring (FB leading forms = coprime pure powers x_i^|FB|) is the only
representation whose homogeneous leading-form system is non-degenerate, and it
shows no early fall.

### REAL FINDINGS THAT FEED FORWARD

1. The symmetric (e-ring / power-sum) FB-membership constraints have leading forms
   that share a common factor (e1 in the e-ring), producing a genuine but
   NON-EXPLOITABLE leading-form syzygy. The validated meter is working correctly --
   it detects a real shared-factor syzygy -- but "d_ff < D_reg" alone is NOT
   sufficient to claim a cheaper decomposition: the fall must occur in (or be
   driven by) the SUMMATION POLYNOMIAL, not solely in the FB-membership constraints.
2. EXP-011 must add (a) a LOCALIZATION gate: confirm the firing syzygy involves the
   S4 leading form, not only the FB-constraint leading forms; and (b) a SOLVE gate:
   compare honest GB step-degree / IC cost on a REAL decomposition (a target that
   actually decomposes over the chosen FB), since the random-FB toy cells are unit
   ideals and uninformative for the cost question.
3. Cross-check: run POS-C (Weil-restricted S3 over F_{p^2}) through THIS meter build
   to confirm the FPPR early fall (which DOES live in the summation polynomial)
   still fires, isolating that the prime-field "no exploitable fall" is a property
   of prime-field coordinates, not of the meter.
