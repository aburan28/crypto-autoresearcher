# EXP-XEDN-002 — Analysis

Exact census of the function-field xedni lift probability for the frozen
EXP-XEDN-001 family. Executed under TASK-20260724-229.

**Role boundary.** This document reports observations, exact derivations, and the
verdict of the observations against the frozen criteria. It does **not** change
the status of H-XEDN-001, EXP-XEDN-001, EXP-XEDN-002, RQ-XEDN-001, or any
research direction; only the Coordinator may do that.

**Scale boundary.** Everything here is toy scale: exhaustive verification at
`p <= 13`, closed-form evaluation at `p <= 809`, generated surfaces only. Nothing
here is a statement about cryptographic curves, and nothing here is an attack.

Runs: `runs/RUN-XEDN-002-A` (superseded, metadata defect),
`runs/RUN-XEDN-002-A2`, `runs/RUN-XEDN-002-B`, `runs/RUN-XEDN-002-C`,
`runs/RUN-XEDN-002-CTRL`. Derivations: `derivation.md`.

---

## 1. What the exact census is

The frozen slot space is `{(b, x)}` with `deg b = 6` exactly and `x` monic
quadratic; a slot is a hit iff the frozen `is_square_poly` accepts `x^3 + b`.
`derivation.md` §0.2 proves that the frozen predicate accepts `f` exactly when
`f = y^2` for a nonzero **squarefree** `y`, and §1 derives

```
N_slots(p) = (p-1) p^8
N_hit(p)   = p^2 (p^4 - 3p^3 + 2p^2 + p - 1) / 2
P_lift(p)  = (p^4 - 3p^3 + 2p^2 + p - 1) / (2 p^6 (p-1))
           = (1 - 2/p + p^{-3}) / (2 p^3)          [exact identity]
```

## 2. Arm A — exact `P_lift` and exponents

| `p` | `N_slots` | `N_hit` | `P_lift` exact | `P_lift` float | `2p^3 P_lift` |
|---|---|---|---|---|---|
| 5 | 1,562,500 | 3,800 | 38/15625 | 2.432000e-03 | 0.608000 |
| 7 | 34,588,806 | 36,162 | 123/117649 | 1.045483e-03 | 0.717201 |
| 11 | 2,143,588,810 | 659,450 | 545/1771561 | 3.076383e-04 | 0.818933 |
| 13 | 9,788,768,652 | 1,886,040 | 930/4826809 | 1.926739e-04 | 0.846609 |
| 101 | 1,082,856,705,628,080,100 | 515,099,495,000 | 504950/1061520150601 | 4.756857e-07 | 0.980199 |
| 211 | 825,047,470,461,932,021,010 | 43,497,615,807,450 | 4652445/88245939632761 | 5.272135e-08 | 0.990521 |
| 431 | 512,019,636,397,340,361,235,630 | 3,182,766,939,114,050 | 39845735/6410082527866081 | 6.216103e-09 | 0.995360 |
| 809 | 148,251,649,328,094,555,852,803,368 | 139,652,587,606,718,432 | 264083084/280343912229566641 | 9.419969e-10 | 0.997528 |

Exact finite-size exponents `alpha_eff = -log(P(p2)/P(p1))/log(p2/p1)`:

| `p1 -> p2` | 5→7 | 7→11 | 11→13 | 13→101 | **101→211** | **211→431** | **431→809** |
|---|---|---|---|---|---|---|---|
| `alpha_eff` | 2.509078 | 2.706526 | 2.801043 | 2.928534 | **2.985781** | **2.993178** | **2.996544** |

- Ordinary least squares on the four contracted sizes `{101, 211, 431, 809}`:
  `alpha = 2.991664` (largest absolute residual `2.39e-03`).
- **Limiting exponent: `alpha = 3` exactly.** Because `2p^3 P_lift = 1 - 2/p + p^{-3}`
  is an exact identity, `P_lift = Theta(p^{-3})` with constant exactly `1/2`, and
  `alpha_eff < 3` for every finite pair, increasing monotonically to 3 over the
  sizes computed.
- There is **no sampling uncertainty**: these are exact rationals. The only
  "interval" available is the spread of the exact finite-size exponents, which at
  the contracted sizes is `[2.9858, 2.9965]`.

Secondary exact values (`derivation.md` §1.6): dropping the predicate's
squarefree requirement raises `P_lift` by a factor
`(p^4-2p^3-1)/(p^4-3p^3+2p^2+p-1)` (1.2303 at `p = 5`, 1.0100 at `p = 101`) and
changes no exponent; counting the excluded `y = 0` section adds exactly `p^2`
slots, a relative `O(p^{-4})`.

## 3. Arm B — exactly what was exhausted, and the agreement

| `p` | mode | `x` values | slots enumerated | of the full space | frozen hits | closed form | agree |
|---|---|---|---|---|---|---|---|
| 5 | **full slot space** | 25 / 25 | 1,562,500 | 100.0000% | 3,800 | 3,800 | yes |
| 7 | **full slot space** | 49 / 49 | 34,588,806 | 100.0000% | 36,162 | 36,162 | yes |
| 11 | complete `b`-marginals for 12 listed `x` | 12 / 121 | 212,587,320 | 9.9174% | 65,400 | 65,400 (= 12 × 5450) | yes |
| 13 | complete `b`-marginals for 6 listed `x` | 6 / 169 | 347,530,248 | 3.5503% | 66,960 | 66,960 (= 6 × 11160) | yes |

- **Full-space verification with the frozen predicate reached `p = 5` and
  `p = 7` only.** At `p = 11` and `p = 13` what was exhausted is a *complete
  `b`-marginal* for each listed `x`: every one of the `(p-1)p^6` surfaces was
  tested against that `x`. The remaining `x` values were **not** tested with the
  frozen predicate at those sizes; the full space (2,143,588,810 and
  9,788,768,652 slots) needs ~11,000 and ~51,000 CPU seconds at the measured
  5.2 µs per dually-classified slot, beyond the 2 CPU-hour contract budget. The
  `x` lists are recorded in `runs/RUN-XEDN-002-B/raw-result.json`
  (`actual_coverage`), seeded from `20260718` and including `x = t^2`,
  `x = t^2 + t`, and the planted `x* = t^2 + 5t + 3`.
- **The full space at `p = 11` and `p = 13` is covered instead by arm C**, whose
  section fibering is a bijective reindexing of the whole incidence set and uses
  no frozen-predicate call: its totals equal `N_hit(p)` exactly at all four
  sizes (§4).
- **`x`-invariance**: the per-`x` hit count took exactly one value at each size
  (152, 738, 5450, 11160 = `Q(p)`), as `derivation.md` Lemma 1.1 requires.
- 596,268,874 slots were classified by the frozen predicate and, independently,
  by square-root extraction plus a discriminant squarefree test: **0
  disagreements**. The mathematical-square counts (4,675 / 41,993 / 71,868 /
  72,498) and the frozen predicate's false-negative counts (875 / 5,831 / 6,468
  / 5,538) also match their closed forms exactly.

**Arm A/B agreement: exact at every enumerated size and slice.** No invalidation
was triggered.

## 4. Arm C — exact multi-section histogram

Full-space section fibering, independent of the frozen predicate; totals
reproduce `N_hit(p)` exactly at `p = 5, 7, 11, 13` (3,800 / 36,162 / 659,450 /
1,886,040) and reproduce the free-`x` closed form exactly (25,200 / 303,408 /
8,058,600 / 26,745,264). Largest completed size: **`p = 13`**; nothing was
skipped (peak memory 448 MB against the 4 GB cap, so memory was not binding).

Counting conventions, stated because they differ by exactly a factor of two:

- **slot** = an `x` admitting a section; `y` and `-y` give the same slot;
- **point** = a section as a Mordell–Weil point, so `points = 2 × slots` exactly
  (verified: every per-surface point count is even);
- **neither is a count of independent sections.** `P` and `-P` are always
  dependent, and two distinct slots may also be dependent. Both columns are
  therefore **upper bounds** on the number of independent sections of this
  degree shape. No rank or height pairing was computed in this experiment.

`P[at least s hit slots]` per surface (denominator `(p-1)p^6`):

| `s` | `p = 5` | `p = 7` | `p = 11` | `p = 13` |
|---|---|---|---|---|
| 1 | 5.824000e-02 | 4.361278e-02 | 3.600723e-02 | 2.915712e-02 |
| 2 | 2.240000e-03 | 5.503659e-03 | 1.136286e-03 | 2.398375e-03 |
| 3 | 3.200000e-04 | 1.606473e-03 | 8.071977e-05 | 7.487348e-04 |
| 4 | 0 | 2.776621e-04 | 0 | 1.755128e-04 |
| 5 | 0 | 1.289145e-04 | 0 | 5.588578e-05 |
| 6 | 0 | 9.916503e-05 | 0 | 1.279313e-05 |
| 7 | 0 | 0 | 0 | 1.009984e-05 |
| 8 | 0 | 0 | 0 | 2.019968e-06 |
| **9** | **0** | **0** | **0** | **1.346645e-06** |
| max slots on any surface | 3 | 6 | 3 | 9 |
| `p^{-1}` for comparison | 0.200000 | 0.142857 | 0.090909 | 0.076923 |

In the point convention `P[>= 9 points] = P[>= 5 slots]`, i.e.
`0, 1.289145e-04, 0, 5.588578e-05`.

Induced exponents for `P[>= s slots]` (only `s <= 3` are defined at more than one
pair, because the higher events are empty at `p = 5, 11`):

| `s` | 5→7 | 7→11 | 11→13 |
|---|---|---|---|
| 1 | 0.8596 | 0.4240 | 1.2632 |
| 2 | −2.6717 | 3.4905 | −4.4718 |
| 3 | −4.7953 | 6.6171 | −13.3334 |

**Multi-section requirement.** `s >= r + 1` sections are needed for a relation
among specialised sections, and the Shioda–Tate bound `r <= 8` for a rational
elliptic surface (literature input, not re-derived) gives `s >= 9`. Observed:

- `P[>= 9 slots] = 0` exactly at `p = 5, 7, 11`, and `1.35e-06` at `p = 13`
  (78 surfaces out of 57,921,708);
- at every computed size `P[>= 9] <= p^{-1}`; at `p = 13` it is smaller by a
  factor of `5.7e4`;
- because the event is empty at three of the four sizes, **no decay exponent for
  `s = 9` is defined**. The honest statement is "far below `p^{-1}` at every
  size computed, and exactly zero at three of them", not a fitted rate.
- the single size where `P[>= 9] > 0` is `p = 13`, one of the two sizes with
  `p = 1 mod 3`, where the family's extra symmetry clumps sections (§7).

The exponents for `s = 1` (0.42 to 1.26, averaging near the `c_surf = 1`
parameter-count prediction) oscillate with `p mod 3` for the same reason: the
mean number of hit slots per surface is smooth and monotone
(`0.0608, 0.0512, 0.0372, 0.0326`, exactly `(1 - 2/p + p^{-3})/(2p)`), but the
clumping ratio `mean / P[>= 1]` is larger at `p = 7, 13` (1.117, 1.117) than at
`p = 5, 11` (1.044, 1.033).

## 5. Arm D — scoped codimension lemma (summary)

Full statement, hypotheses H1–H6, proofs, and the list of uncovered cases are in
`derivation.md` §2. Summary:

- **Rigorous (Lemma D1).** With `M_0 = max(3d, A+d, B)` and
  `E = min(e, floor(M_0/2))`, `P_slot <= p^{E-B}` for every `p`. Hence
  `alpha < 1/2` requires `e >= B` **and** `max(3d, A+d) >= 2B`. For the frozen
  shape this gives `P_slot <= p^{-3}`, attained.
- **Parameter count (Lemma D2, marked as such).**
  `c_slot = max(B, 3d, 2e, A+d) - e` and `c_surf = c_slot - delta`, where
  `delta` is the number of free `x` coefficients. Consequences:
  `c_slot >= e`, so any non-constant `y` forces `alpha >= 1`; `c_slot = 0` only
  in the all-constant configuration, which has no fibration content.
- **The `c_surf = 0` configurations** are exactly the small-height integral
  section shapes with **unnormalised** `x`; the largest is
  `deg a <= 4, deg b <= 6, deg x <= 2, deg y <= 3` — the rational elliptic
  surface shape. Verified exactly in the `a = 0` slice:
  `P_slot^free = (p-1)(p^3+1)/(2p^7)` and the mean number of sections per
  surface is `(p-1)(p^3+1)/(2p^4) -> 1/2` (0.4032, 0.4298, 0.4549, 0.4617,
  0.4951 at `p = 5, 7, 11, 13, 101`).
- **Prescribing the target specialisation** (fibre at `t_0` equal to the target
  curve, sections through the target points) costs `2 + m` conditions and leaves
  `dim <= dim_a + B - 1 - m - sum_i c_surf,i`. The `c_surf = 0` abundance is
  destroyed once `m > dim_a + B - 1`: at `m >= 6` for the frozen `a = 0, B = 6`
  family, at `m >= 11` for the full rational elliptic family. **At `m = 9` on
  the full family the count is `dim <= 1`, i.e. NOT negative** — this parameter
  count does not exclude the classical prescribed construction, whose recorded
  failure mechanism is different (a bound on relation coefficient size,
  KN-LIT-021). Arm D is **not** an unconditional no-go for lifting.

## 6. Control verdicts

| control | verdict | evidence |
|---|---|---|
| 1 frozen predicate vs independent implementations | **pass** | complete reachable `f`-space at `p = 5` (62,500) and `p = 7` (705,894); `sympy` factorisation over `GF(p)` on all 62,500 at `p = 5`; 2 × 100,000 random sextics at `p = 101` (seeds 20260718, 20260724) with 2,500 `sympy` cross-checks each; plus all 596,268,874 arm-B slots. **Zero disagreements** anywhere. Frozen hits equal the closed form (152, 738) and mathematical squares equal theirs (187, 857). |
| 2 planted-section recovery | **pass, with a recorded deviation** | at `p = 101` all 10,201 monic quadratics were enumerated for the planted `b = y*^2 - x*^3`; exactly one hit, at `(x_0, x_1) = (3, 5)`, reproducing the smoke's "1 section, recovered". **Deviation: the planted `b` has degree 5, not 6** (the `t^6` coefficients of `y*^2` and `x*^3` are both 1 and cancel), so the planted surface lies **outside** the frozen `deg b = 6` census family. It is a valid recovery control on the enumerator and predicate, not a member of the population arm A counts. The EXP-XEDN-001 smoke recorded the same degree (`planted_surface_b_degree: 5`). |
| 3 smoke consistency | **pass** | `P_lift(101) = 4.756857e-07` predicts `0.002740` hits in the smoke's 5,760 slots; `P(observe 0) = 0.997264`. The one-sided 95% upper limit on the rate given 0 hits is `5.201e-04`, which contains the closed-form rate. The part-4 negative control is also consistent: predicted `0.0961` squares in 200,000 sextics (exact rate `(p-1)/(2p^4)`), observed 0, `P(0) = 0.9084`. **The smoke could not have detected this rate**: its 0 is the expected outcome and carries almost no information about the exponent. |
| 4 iso-triviality | **discharged with a finding** | Two readings give different answers, so both are reported. Narrow reading ("iso-trivial = constant coefficients"): **exactly 0** surfaces, as the specification anticipated, because `deg b = 6` excludes constant `b`. Standard reading (constant `j`, equivalently mutually isomorphic smooth fibres): **every** surface in the family is iso-trivial, because `a(t) = 0` forces `j = 1728·4a^3/(4a^3+27b^2) = 0` identically; the family is a family of sextic twists of `Y^2 = X^3 + 1`. Additionally, exactly `(p-1)p` members (20 / 42 / 110 / 156 at `p = 5, 7, 11, 13`, verified by enumeration) are isomorphic **over `F_p(t)`** to a constant curve, namely `b = c(t+a_0)^6`. **No surface was excluded from any count**, because excluding the iso-trivial ones under the standard reading would empty the family. This is a finding about the frozen formalisation, recorded for the Coordinator; the EXP-XEDN-001 contract constraint "iso-trivial surfaces must be detected and excluded" is not satisfiable for this family as frozen. |
| 5 degenerate `y = 0` section | **pass** | exactly `p^2` slots have `x^3 + b = 0` (namely `b = -x^3`, one per `x`, all inside the family since `deg(-x^3) = 6`); verified 25 / 49 / 121 / 169 at `p = 5, 7, 11, 13` and **all rejected by the frozen predicate**. Counting them would raise `P_lift` by `6.6e-03` (relative) at `p = 5` and `9.0e-05` at `p = 13`; it changes no exponent. |
| (extra) structural check — not a contract control | consistent | For `p = 1 mod 3` the `j = 0` family has the automorphism `x -> zeta x`, which fixes `x^3`; 624 (`p = 7`) and 708 (`p = 13`) orbit checks with 0 violations. The monic scaling action `x(t) -> lambda^{-2} x(lambda t)` explains the section-rich surfaces with symmetric `b`: at `p = 7`, `b = t^6 + 2` has stabiliser all of `F_7^*` and its 6 monic hits form one orbit; at `p = 13`, `b = 3t^6 + 10t^3 + 9` has stabiliser `{1,3,9}` and its 9 monic hits form three orbits of size 3. It does not explain all of them (a `p = 13` surface with trivial stabiliser also has 9 hits). |

## 7. Verdict against the frozen criteria

Quoted verbatim from `experiments/EXP-XEDN-002/specification.yaml`.

> **success_criterion:** Exact P_lift values at at least three contracted sizes
> give alpha < 1/2 with an uncertainty interval excluding the classical
> prediction alpha = 3 fitted at the same sizes, and arm C shows P[at least 9
> sections] at or above p^-1: the function-field lift survives as a candidate
> relation source and a larger-size confirmation arm is triggered.

**Not met, on both clauses.**
(i) The exact exponents at the four contracted sizes are 2.985781, 2.993178,
2.996544 (OLS 2.991664); every value is `>= 1/2`, and the classical prediction
`alpha = 3` is not excluded but is the exact limit.
(ii) `P[>= 9 sections]` is `0` at `p = 5, 7, 11` and `1.35e-06` at `p = 13`,
below `p^{-1}` at every size (by `5.7e4` at `p = 13`), under both the slot and
the point convention.

> **falsification_criterion:** Exact P_lift gives alpha >= 1/2 (in particular the
> codimension-3 value alpha = 3), or arm C shows P[at least 9 sections] decaying
> faster than p^-1: scoped rejection of H-XEDN-001 and closure of the
> function-field xedni census for this family, with the exact values archived.
> The closure covers this surface family, these section degrees, and this
> predicate only.

**Its stated conditions are met**, with one wording caveat:
(i) `alpha >= 1/2` holds at every size; the limiting value is exactly the
codimension-3 value `alpha = 3`, and the exact identity
`2p^3 P_lift = 1 - 2/p + p^{-3}` shows `P_lift < 1/(2p^3)` for all `p >= 3`.
(ii) `P[>= 9 sections]` is below `p^{-1}` at every computed size, but since it is
identically zero at three of the four sizes **no decay rate is defined**; the
observation supports the criterion's intent ("far below `p^{-1}`") rather than
its literal wording ("decaying faster than").

**Status transitions are the Coordinator's decision and are not made here.** The
observations above are what the frozen criteria are to be applied to.

## 8. Claim boundaries

1. **An exact count removes sampling error only. It does not remove model
   error.** If the frozen family or the frozen predicate is the wrong
   formalisation of the xedni idea, this experiment has answered a possibly wrong
   question exactly. That risk is live here, and the census itself produced four
   concrete instances of it:
   - **(a) The family is the one the original candidate excluded.** Every member
     has `j = 0` and is iso-trivial in the standard sense (control 4). Candidate
     B2's own target-family line in `research_directions_20260718.md` excludes
     "constant/iso-trivial surfaces" and "j=0/1728 (extra sections may confound
     controls)". The extra automorphisms are not hypothetical: they are measured
     (§4, §6, `derivation.md` §3).
   - **(b) Monic `x` is a restriction, not a normalisation.** A section's
     `x`-coordinate need not be monic. Requiring it costs a factor of `p` in the
     per-surface probability: `c_surf = 1` for monic `x` versus `c_surf = 0` for
     unrestricted `x` of the same degree, where the exact mean number of sections
     per surface tends to `1/2` (§5). The frozen shape is not the standard
     integral-section shape of the Mordell–Weil lattice.
   - **(c) The gate quantity is a per-slot rate.** `P_lift` as defined by
     H-XEDN-001 is per (surface, slot) pair. It is `Theta(p^{-3})` in **both**
     the monic and the unrestricted convention, because the slot count and the
     hit count scale together. So the exponent the gate tests is insensitive to
     the monic-versus-free difference that changes the per-surface answer from
     `Theta(p^{-1})` to `Theta(1)`. This is a property of the frozen metric, not
     a result about lifting; it is stated so the Coordinator and red team can
     judge whether the gate measured the intended quantity.
   - **(d) `a(t) = 0` removes exactly the parameters that the prescribed-target
     count needs** (`dim <= dim_a + B - 1 - m`; `derivation.md` §2.5).
2. **Arm D is a scoped parameter-counting lemma, not an unconditional no-go.**
   Lemma D1 is rigorous but only an upper bound; Lemma D2's two counting steps
   are marked heuristics verified in three configurations; and the prescribed
   construction at `m = 9` on the full rational elliptic family is **not**
   excluded by the count (`dim <= 1`). Nothing here proves that no lifting attack
   exists.
3. **Distinct is not independent.** Arm C counts distinct sections of one degree
   shape. No Mordell–Weil rank, height pairing, or torsion structure was
   computed; `r <= 8` is a literature input (Shioda–Tate). The `s >= 9`
   comparison is therefore a comparison against an **upper bound** on independence.
4. **Negative evidence closes only the tested scope.** Any closure the
   Coordinator may draw from these observations covers this surface family
   (`a = 0`, `deg b = 6`), this section shape (`x` monic of degree 2, `deg y <= 3`),
   this predicate, and these sizes — nothing else. It says nothing about
   higher-degree sections, non-integral sections, non-isotrivial families,
   `a != 0`, other base fields, or xedni over number fields.
5. **This experiment does not supersede the audited-route records.** The
   inconclusive audited-route results `ECFG-P1543` and `ECFG-P1547` in
   `ledger/FINDING-PF-IC-001.md` remain exactly as they are; nothing here adds
   to or replaces them.
6. **No solve, no relation, no certificate.** All four runs declare
   `certificate.kind: none`: this is a counting experiment, with nothing to
   certify (`docs/claims-and-verification.md`).
7. **Claim tier `toy`.** Largest field used: `p = 809` (10 bits) in closed form;
   largest exhaustively enumerated: `p = 13`.

## 9. Methodology observation (not evidence)

The EXP-XEDN-001 phase-2 design asked for a sampled exponent from a per-slot rate
that this census now knows exactly: `4.76e-07` at `p = 101` and `9.42e-10` at
`p = 809`. Detecting a nonzero count at `p = 809` would need on the order of
`10^9` slot tests per size. The contracted budget (40 runs, 14,400 s) could not
have produced it. Per AGENTS.md rule 5 this is a statement about the measurement
design, **not** evidence about the mathematics: the sampling design's
infeasibility is why EXP-XEDN-002 replaced sampling with enumeration, and the
mathematical content of the gate is decided by the exact values above, not by the
earlier design's failure.

## 10. Reproduction

From the repository root, at commit `e18c9bc0b90e3031cfa28483fe5571c0fb548dfb`
(working tree contained this task's own new files, untracked):

```
bash experiments/EXP-XEDN-002/implementation/run_arm.sh A2      #    2 s
bash experiments/EXP-XEDN-002/implementation/run_arm.sh B       #  954 s (4 workers)
bash experiments/EXP-XEDN-002/implementation/run_arm.sh C       #   14 s
bash experiments/EXP-XEDN-002/implementation/run_arm.sh CTRL    #   19 s
```

Each writes `manifest.yaml`, `command.txt`, `environment.json`, `stdout.log`,
`stderr.log`, `raw-result.json` into `runs/<RUN-ID>/`. The driver refuses to
overwrite an existing run record. All arithmetic is deterministic and exact;
the only randomness is the seeded choice of the arm-B `x` marginals and the
seeded random sextics of control 1 (seeds `20260718`, `20260724`, recorded in
every manifest). Arm B uses 4 worker processes; hit counts are order-independent,
so only scheduling is nondeterministic.

An artifact self-check re-derives the closed forms from the derivation without
importing the experiment's own library, checks the run-record schema, verifies
that every number in the tables above is present in the corresponding
`raw-result.json`, and re-executes a sample of the recorded work (the whole arm-A
table, two arm-B marginals, the arm-B seeded `x` plan, and the arm-C census at
`p = 5, 7`):

```
python3 experiments/EXP-XEDN-002/implementation/verify_artifacts.py --reproduce
```

It reports `259 checks, 0 failures`. It is a check on this reproduction package,
not a measurement, so it has no run record and consumed no run slot.
