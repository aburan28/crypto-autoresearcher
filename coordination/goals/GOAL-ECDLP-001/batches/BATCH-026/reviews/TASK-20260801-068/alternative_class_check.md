# TASK-20260801-068 — DUTY: ALTERNATIVE CLASS, D1-v2, V8, AND THE MAXIMA

RTB-068. Every structural claim below was re-derived from driver SOURCE and
re-tested by EXECUTING the driver's own functions on my own inputs; every
quoted number was recomputed from the named archived array.

## 1. D1-v2 part (i) — ROUGH, claimed STRUCTURAL

### 1a. The derivation, re-derived from source

`build_rough_replacement(v, p, rng)` (driver lines 752–812):

- `q_lo, q_hi = p + 1, v // 64`; the prime search runs `while cand <= q_hi`, so
  any returned `q` satisfies `p < q <= v//64`.
- `r_hi = v // found_q`; the random branch draws `r` in `[r_lo, r_hi]`, the
  fallback branch scans down from `r_hi`, and the `found_r = 2` branch is guarded
  by `r_hi >= 2 >= r_lo`. Every path gives `r <= v // q`.
- For a sample `v <= X = p²`: `r <= v//q <= p²/q < p < q`.
- Hence `q` is strictly the largest prime factor, `P_max = q` **exactly**, and
  `Z = ln(qr)/ln(q) = 1 + ln r / ln q < 2`.

The chain uses only the construction's own bounds. It holds **unconditionally** —
at every rung, every γ, every replicate, both cells — and does not depend on the
random number stream, the seed, or the ladder. **I confirm the derivation, and
I confirm it is correctly labelled STRUCTURAL.**

One edge case I checked because it is where such derivations break:
`q = max(q_lo, min(q_hi, q)) | 1` can push `q` to `q_hi + 1` when `q_hi` is even.
In that case `cand = q_hi + 1 > q_hi`, the search loop body never runs,
`found_q = 0`, and the attempt is retried. **No path escapes `q <= q_hi`.**

### 1b. Execution

I imported the hash-bound driver and executed `build_rough_replacement` on my own
inputs:

- 7,992 successful constructions across both cells on uniform `v` in `[1, p²]`:
  **0 violations** of `q > p`, `r < q`, `r <= v//q`, `q | m`, `r | m`, `q` prime,
  `r` prime, `Z < 2`, `m <= v`. Max observed `Z = 1.9906086945689119`.
- 2,672 further constructions at the **edge of the admissible range**
  (`v` just above `64p`, where the construction is most constrained): **0
  violations**, max `Z = 1.382`.

### 1c. Zero violations across all 462,736 rough values

`results/plantz/plant_z_tail_report.json` `rough_structural_bound`:
`plants_checked: 462736`; `violations_total` = `q_not_above_p: 0`,
`q_does_not_divide: 0`, `r_not_below_q: 0`, `r_exceeds_v_over_q: 0`,
`z_not_below_2: 0`; `max_plant_z_over_all_rough_blocks: 1.994781310510841`;
`bound_holds_on_every_regenerated_rough_value: true`. Per-cell maxima
1.9941869527759615 (bits 16) / 1.994781310510841 (bits 20).
**Confirmed as archived. 0 exceedances and 0 insertions in all 280 rough
(cell, rung, replicate) instances — I recounted both from `per_replicate`.**

### 1d. The consequence

Null tenth-largest Z: LPF-CAL-A minima 5.657939657036511 (bits 16) and
5.339285892609557 (bits 20); freeze anchors 6.060618052804848 and
5.762382565494627. Since `2 < 5`, **no rough plant can occupy a deep tail at any
rung.** This half of D1 is airtight and is correctly stated as structural.

## 2. D1-v2 part (ii) — SMOOTH, stated as MEASURED, not structural

**Is it stated as MEASURED?** Yes, and unmistakably:
`status: 'MEASURED NEAR-DISJOINTNESS ON THE FROZEN LADDER. NOT STRUCTURAL. NO
IMPOSSIBILITY IS CLAIMED.'`, with `why_no_structural_bound_exists` conceding
that the planted Z is "a random variable bounded only by ln(X)/ln 2, and no
argument from the construction excludes the deep tail. The smooth family has no
analogue of the rough chain and none is claimed."

**Is any impossibility claimed?** No. And `newly_forbidden` makes the prohibition
explicit and binding: "NO DELIVERABLE MAY SAY THAT EITHER FROZEN PLANT FAMILY
CANNOT PLACE MASS IN THE DEEP TAIL."

**Is the withdrawn "plants can only evict" claim actually withdrawn?** Yes,
twice over. `the_direction_correction` says "THE SUPERSEDED ONE-WAY MECHANISM IS
WITHDRAWN AND NOT REPLACED BY ANOTHER" and names the three counterexamples.
`narrowed_gamma_sentence` withdraws "RAISING GAMMA OR THE REPLICATE COUNT WOULD
NOT CHANGE THIS" for the smooth family and retains it only for rough, with the
correct scaling argument (each planted position is a fresh draw, so the expected
number above the null tenth-largest Z scales approximately linearly in γ and in
the replicate count). The one place the eviction mechanism survives —
`part_c_downward_demonstration` — carries a `reference_note_added_at_this_supersession`
restricting it to the ROUGH family, where it does hold.

### Every part (ii) number, recomputed from `plant_z_tail_report.json`

| claim | recomputed | verdict |
|---|---|---|
| 3 of 280 smooth instances with exactly ONE exceeding plant, 277 with NONE, none with two or more | distribution over 280 `per_replicate` rows: `{0: 277, 1: 3}` | EXACT |
| rough: 0 of 280 | `{0: 280}` | EXACT |
| 3 of 463,080 smooth plants, ≈6.5e-06 per plant | 3/463080 = 6.478e-06 | EXACT |
| rough 0 of 462,736 | confirmed | EXACT |
| 3 insertions, 40 evictions, 2,800 examined slots (smooth) | `by_family` OBJ-PLANT-SMOOTH: insertions 3, evictions 40, slots 2800 | EXACT |
| rough 0 insertions, 39 evictions, 2,800 slots | confirmed | EXACT |
| p99.99 5.535876141602368 < anchor 6.060618052804848 (bits 16 γ=0.05) | confirmed | EXACT |
| p99.99 5.190061837472107 < anchor 5.762382565494627 (bits 20 γ=0.05) | confirmed | EXACT |
| bits-20 γ=0.02 block p99.99 = 5.260801146064238, also below anchor | confirmed | EXACT |
| three exceedance instances, planted T_deep moved UP by +0.16613459508532102 / +0.04424795880325849 / +0.06166194166478878 at (b16,γ.05,rep10) / (b20,γ.02,rep11) / (b20,γ.05,rep0) | all three reproduced exactly from `per_replicate.planted_t_deep_minus_null_t_deep`, all three positive | EXACT |
| ≈0.05 insertions/replicate and 0.55 / 0.40 evictions/replicate at γ=0.05 | b16: 1 ins, 11 evic over 20 reps = 0.050 / 0.550; b20: 1 ins, 8 evic = 0.050 / 0.400 | EXACT |
| all 28 plant rows |shift| < 1, largest 0.3379820826156079, 0 of 28 flagged | recomputed from the 210-row table | EXACT |

### The eviction citation and `evictions = insertions + promoted`

The 40:3 ratio is quoted from `aggregates.by_family."OBJ-PLANT-SMOOTH"` and the
quotient `13.333333333333334` is the generator's own
`evictions_over_insertions_ARITHMETIC_ON_THE_ARCHIVED_COUNTS` field.
**GENERATOR-EMITTED, as claimed — DEF-065-2 is acted on, not merely noted.**

The identity `evictions = insertions + promoted_null_non_top10` **holds in all 28
blocks**, which I checked block by block, and in all four `by_family_and_cell`
aggregates and the `all` aggregate. The file states this correctly and draws the
right conclusion: the quotient is a bookkeeping relation among counts
partitioning the same 2,800 slots, **not the ratio of two independent estimates**,
and may never be read as a test statistic or an effect size. That is the honest
statement and it is bound wherever the ratio is cited.

The γ-slice trap is also verified: `aggregates.by_family_gamma_le_0p05` is
**field-for-field identical** to `by_family` (I tested object equality), so
`γ <= 0.05` is indeed vacuous on a ladder topping out at 0.05; and the
`γ == 0.05` slice is 2 blocks, 261,640 plants, 19 evictions to 2 insertions
= 9.50, differing from the all-rungs 13.33 by 40%. The file quotes the all-rungs
slice and names it in full. **DEF-065-5 is acted on.**

## 3. Does ANY clause depend on a maximum?

I ran this as a mutation test rather than a reading. I located every citation of
the four per-cell maxima in the file and asked, of each, whether the clause
containing it would become false if the maximum were corrected a fourth time.

| location | is it load-bearing? |
|---|---|
| `what_this_file_does_not_rely_on` (4.957 / 4.643) | no — a declaration that they are relied on nowhere |
| `structural_basis_D1_SUPERSEDED_VERBATIM` and `V8_SUPERSEDED_VERBATIM_FROM_RR_LPF_1` | no — inside verbatim quotes of withdrawn text |
| `why_the_superseded_text_is_withdrawn` (5.936/6.031, 5.955369/6.916065) | no — the argument is that these are corrections, and a fourth correction strengthens it |
| part (iii) `the_argument` points (2), (3), (4) | no — these are arguments **against** relying on a maximum; a fourth correction confirms them |
| `the_maxima_recorded_as_observations_only` | explicitly observations, with instability declared |
| `DEF-065-4.detail` | a restatement of the validator's own defect |
| part (i) `independent_confirmation` (rough maxima 1.9948 / 1.9942) | **corroboration, not premise** — see below |

**Clauses that would have to break and do not.** I checked each by substitution:

- **D1-v2 part (i)** rests on `r <= v//q <= p²/q < p < q`, a source-derived
  inequality I re-derived and executed. Substituting any other value for
  SMOOTH_bits_16/20 changes nothing in part (i). The two ROUGH maxima are cited
  there, but as a consequence of the bound, not a premise: any correction that
  leaves them below 2 leaves part (i) untouched, and a correction to ≥ 2 would
  contradict the derivation itself — which I verified independently, so the
  derivation, not the observed max, is the falsifiable object. **This is the one
  place a maximum appears inside a structural clause, and I record it as a
  precision note rather than a dependency.**
- **D1-v2 part (ii)** rests on counts (3 of 280, 3 of 463,080), a rate
  (6.5e-06), generator aggregates (40:3 over 2,800 slots), a rank-≈13 percentile
  (p99.99), and the rank-10 quantity the branch reads. **No maximum.**
- **STRIKE-1** rests on `0 of 28 rows flagged, largest |shift| 0.338`. **No
  planted-Z maximum.** (It does rest on a maximum over 28 mean-shift rows — but
  that is the contract's own criterion `|shift| >= 1` restated, and a mean-shift
  over 20 replicates against a 200-replicate sd is not the rank-1 order statistic
  DEF-065-4 warns about. Recorded so the distinction is on the record.)
- **V8** quotes p99.99, counts, the rate, the 462,736 zero-exceedance count and
  `Z < 2`. **No maximum.**
- **Every branch condition L-0…L-5**: none reads any planted Z, and none reads
  STAT-TAIL-DEEP at all (confirmed by clause-by-clause reading of all six
  conditions and by the fact that STAT-TAIL-DEEP is struck from the certifying
  set, so L-5's "detected by any certifying statistic" leg does not reach it
  either).

**Verdict: the author's claim survives my mutation test. A fourth correction to
the four per-cell maxima would falsify no clause of D1-v2, of STRIKE-1, of V8 or
of any branch.** The four maxima are quarantined as observations, correctly.

I also verified part (iii)'s supporting facts independently:
the `stat_tail_deep` docstring in the hash-bound driver reads, verbatim, "Rank
ten and not rank one DELIBERATELY (TAIL-LPF-1): a single extreme order statistic
has an unstable law and was the proximate cause of the TAIL-DS-1 defect" —
quoted accurately; the bits-20 γ=0.02 block's next-highest **replicate maximum**
is 5.5526405342442215 (replicate 3), a gap of 1.3634 in Z, and that block
contains **exactly one** `Bsm(u=6)`-smooth plant; bits-16's top three rungs are
5.955368914587463 (γ=0.01), 5.922395609667227 (γ=0.02), 5.936051910051658
(γ=0.05), spread 0.032973 ≈ 0.033; bits-20 peaks at γ=0.02 and bits-16 at γ=0.01,
above their γ=0.05 values (UNEXP-PLANTZ-1 confirmed).

## 4. V8 restated — recomputable, not asserted; not weakened; no soft impossibility

**Recomputable from the archived arrays?** Yes. Every quantitative element of the
restated V8 is in the table in §2 above and every one reproduces exactly:
6.06 / 5.76 anchors, `Z < 2` structural, 0 exceedances in 462,736 rough plants,
3 planted values in 463,080 smooth plants, 6.5e-06 per plant, 3 of 280 instances,
p99.99 5.5359 vs 6.0606 and 5.1901 vs 5.7624, largest |shift| 0.338. **No figure
in V8 is asserted without an archived source, and no figure in V8 is one of the
withdrawn maxima.**

**Operative content weakened?** No. The operative sentence — "THIS EXPERIMENT HAS
NO CERTIFIED POWER AGAINST A DEEP-TAIL-ONLY DEPARTURE IN EITHER DIRECTION AT
EITHER CELL" — is repeated word for word. V8 is an entry on the **uncertified**
side; what it must not do is shrink, and it does not.

**Impossibility reintroduced in softer words?** No. "PLACES NEGLIGIBLE MASS THERE
AT THE FROZEN RUNGS" is scoped (frozen rungs), quantified (3 in 463,080), and
paired with `newly_forbidden`, which bars the impossibility reading outright.
The restatement is, as the file says, "STRICTLY WEAKER AS A CLAIM ABOUT THE
WORLD AND EXACTLY AS STRONG AS A LIMIT ON WHAT MAY BE CLAIMED", which is the
correct relationship for an uncertified-class entry.

**STRIKE-1 overturned?** No. Its measured basis — 0 of 28 flagged rows, largest
|shift| 0.3379820826156079 — I recomputed from the 210-row table and it is
unchanged and **independently sufficient**: CERT-LPF-1 strikes a member that does
not move on any rung of either ladder, and that is a measurement, not an
argument. D1-v2 changes only why the inertness is not "low power".

## 5. ABS-REL-LPF-1, ruled explicitly

**Can any branch be satisfied by a two-sample agreement alone?** **No.**
`STAT-KS2-CAL` is declared non-certifying in advance for both limbs, carries no
band, no cut and no reject boolean, and I read all six branch conditions clause
by clause: none mentions it. It is also uncomputed in the calibration
(OPEN-LPF049-A).

**Is the uniform arm anywhere treated as the comparison?** **No.** The bands are
order statistics of OBJ-NULL-UNIF and are the apparatus CALIBRATION; L-2 and L-3
compare the REAL arm against those archived bands. The uniform arm's own R(u)
appears only as a DECIDABILITY GATE for LIMB B, never as the object compared
against.

**Is the V1 cost stated honestly?** **Yes, and it is the sharpest sentence in the
block:** "Any departure from the Dickman law that a matched-bitlength uniform
sample exhibits at the same magnitude and sign — absorbed by LIMB A's measured
band by construction; only LIMB B can see it." That is the exact price of an
absolute-band design and it is carried unchanged.

## 6. Does the certified list still overstate what the ladders reach?

**No — it now understates nothing and overstates nothing.** 0 unsupported
entries in 28 lists (RR-LPF-1 had 2); 1 omission, which is the D9 struck ladder
and is correct under the ruling in `contract_review.yaml`. The S1/S2 detection
floors are unchanged and I read them directly from
`LPF_gamma_det_both_cells`: SMOOTH u=4 0.002, u=3 0.005, u=2 0.01, KS-DICK 0.05,
u=5 NONE_ON_LADDER; ROUGH u=2 0.02, u=3 0.05, all else NONE_ON_LADDER —
identical to the file. V12 records the two rungs change (a) removed, on the
uncertified side, so the correction travels with the ALT-CLASS block as
ALT-CLASS-LPF-1's own binding requires.

## 7. Duty verdict

**PASS.** D1-v2 is on the right class of object for each family; the ROUGH half
is structural and I re-derived and executed it; the SMOOTH half is measured,
quantified, scoped and recomputable; no impossibility survives in either words
or substance; V8's operative content is intact; STRIKE-1 stands on an unchanged
and independently sufficient measurement; and no clause depends on a maximum.
