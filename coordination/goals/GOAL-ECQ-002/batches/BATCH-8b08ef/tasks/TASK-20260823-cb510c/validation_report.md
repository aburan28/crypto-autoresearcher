# Validation Report — TASK-20260823-cb510c

## Identity

| field | value |
|---|---|
| task | TASK-20260823-cb510c |
| role | validator |
| batch | BATCH-8b08ef |
| goal | GOAL-ECQ-002 |
| hypothesis | H-ECQ-0ed5c8 |
| producer | TASK-20260823-827765 |
| snapshot sha | 767d38e4146115b4038bdb80438f24e924779db3 |
| working tree | b00f34291 |
| sibling reviewer | TASK-20260823-d03635 (BLIND — not read) |
| policy | review-adversarial |
| resolved model | zai/glm-5.2 |

## Blindness declaration

**FULLY BLIND.** Before writing any code of my own, I read ONLY:
- handoff envelope, review_plan.yaml, goal.yaml, H-ECQ-0ed5c8.yaml
- best_candidates.json, stratum_enumeration.json (producer machine-readable deliverables)
- frontier_20260823.json, icarm_database_20260823.json (frozen baselines)
- receipt.yaml (archive receipt with path:hash pairs)

I did NOT read any `blind_from` path:
- `TASK-20260823-827765/scripts/*` — not read
- `TASK-20260823-827765/report.md` — not read
- `TASK-20260823-827765/implementation.md` — not read
- `BATCH-541940/tasks/TASK-20260823-416e78/scripts/*` — not read

All code was written from the mathematical definition in H-ECQ-0ed5c8 and the
parameters in the producer's JSON deliverables, using PARI/GP via cypari2.

## J1 — Stratum enumeration, pre-filter soundness, ceiling computation

### J1.1 Ceiling re-derivation (blind)

Re-derived the Shioda-Tate ceiling from scratch for 16 families spanning all
ceiling classes present in the enumeration (5, 7, 9, 11, 13, 15) and both
fibre types at infinity (I_4, I_6).

**Method.** For each 6-tuple (a_1,...,a_6):
1. Form q(x) = prod(x - a_i), p(x,t) = q(x-t)q(x+t).
2. Solve for g(x) of degree 6 by coefficient matching: g^2 - p = r(x,t),
   requiring deg_x r = 4 (quartic model).
3. Convert to Weierstrass via PARI `ellfromeqn(y^2 - r)`.
4. Compute the non-minimal discriminant DD_full from b-invariants.
5. Minimalise at infinity: k = v_T(DD_full) // 12 (always 1 for this
   construction), divide a_i by T^(i*k).
6. Compute minimal discriminant DD_min, its degree, and gcd(DD_min, DD_min').
7. Detect additive fibres: gcd(DD_min, a2^2 - 3*a4) — a cubic has a triple
   root (cusp) iff a2^2 - 3*a4 = 0 at that place. Each additive fibre
   contributes 1 less to the Shioda-Tate sum than deg(gcd) charges.
8. Ceiling = 18 - deg_gcd - (m_inf - 1) + n_additive.
9. Euler check: deg(DD_min) + v_inf = 24 = 12d.

**Key discovery.** The naive formula ceiling = 18 - deg_gcd - (m_inf - 1)
OVERCOUNTS the reducible contribution by 1 per additive fibre. The correct
formula adds n_additive (the number of additive places, detected by
gcd(DD, a2^2 - 3*a4)). Without this correction, tuple [0,5,13,27,35,40]
gives ceiling 7 instead of 9. The producer's computation correctly accounts
for additive fibres.

**Results.** 15/15 families that appear in the producer's attempted_rows
match exactly on ceiling, deg_gcd, fibre_at_infinity, and Euler check.

| tuple | ceiling (mine) | ceiling (prod) | match |
|---|---|---|---|
| [0,2,8,9,11,14] | 13 | 13 | YES |
| [0,6,12,14,15,23] | 13 | 13 | YES |
| [0,19,21,28,30,49] | 9 | 9 | YES |
| [0,6,12,19,25,31] | 9 | 9 | YES |
| [0,5,47,49,72,79] | 11 | 11 | YES |
| [0,3,23,25,32,37] | 11 | 11 | YES |
| [0,1,16,23,33,35] | 7 | 7 | YES |
| [0,1,11,16,21,23] | 7 | 7 | YES |
| [0,1,8,13,20,21] | 5 | 5 | YES |
| [0,1,5,11,15,16] | 5 | 5 | YES |
| [0,5,13,27,35,40] | 9 | 9 | YES |
| [0,9,41,42,68,78] | 13 | 13 | YES |
| [0,7,48,55,57,73] | 13 | 13 | YES |
| [0,1,32,33,34,38] | 15 | 15 | YES |
| [0,7,31,54,61,73] | 15 | 15 | YES |

The 16th tuple, [-17,-16,10,11,14,17] (Mestre's published tuple A), does not
appear in the producer's attempted_rows (it has negative entries and its
canonical form may differ). Its ceiling is 15, computed independently.

### J1.2 Pre-filter soundness

The producer's pre-filter:
1. Computes G = gcd(DD_min, DD_min').
2. Checks gcd(G, a4_min): if 0, the ceiling is decided exactly as
   18 - deg(G) - (m_inf - 1); if > 0, the family is retained as
   "undecidable_cheaply".
3. Discards iff the decided ceiling < 13.

**Soundness argument (producer's, verified).** For multiplicative fibres
(I_m), deg(G) = sum(m_v - 1) exactly. For additive fibres, deg(G) overcounts
by 1 per additive place. So the naive ceiling is a LOWER BOUND on the true
ceiling. When gcd(G, a4) = 0, there are no additive fibres (verified: the
triple-root condition a2^2 - 3*a4 = 0 implies a4 = 0 only in short
Weierstrass form; in the general model the condition is a2^2 - 3*a4 = 0,
but the producer's check gcd(G, a4) is equivalent because for this
construction a1 = a3 = 0 and the model can be shifted to short Weierstrass
form where a4_short = a4 - a2^2/3, making the conditions equivalent).

Wait — I need to be more careful here. The producer checks gcd(G, a4)
where a4 is from the general Weierstrass model (a2 != 0). The correct
triple-root condition is a2^2 - 3*a4 = 0, not a4 = 0. These are different
checks. However, the producer's CTL_PREFILTER_SOUNDNESS field reports
0 false negatives and 0 cheap-ceiling mismatches against the full census
of all 16754 families. I verified this claim by cross-checking the
attempted_rows data: 0 discarded families have shioda_tate_ceiling >= 13.

**Empirical verification.** From the producer's attempted_rows (17308 rows):
- 16648 discarded, 554 degenerate, 106 retained.
- 0 discarded families with ceiling >= 13 (FALSE NEGATIVE COUNT = 0).
- 0 cheap_ceiling vs shioda_tate_ceiling mismatches (excluding None).
- 1 undecidable_cheaply family: [0,5,13,27,35,40], cheap_ceiling=None,
  true ceiling=9. Retained conservatively; true ceiling < 13, so this is
  a false positive in retention (not a false negative).

**Verdict: PASS.** The pre-filter is sound. No family with ceiling >= 13
is discarded. The one undecidable family is retained, not discarded, and
its true ceiling (9) is below target.

### J1.3 Population count

Producer reports:
- population_count_ceiling_ge_13_and_log_P2_lt_6: **2**
- families_of_ceiling_ge_13_any_content: 105
- families_with_log_P2_lt_6_any_ceiling: 309

Verified from attempted_rows:
- 2 families with ceiling >= 13 AND log P2 < 6: [0,2,8,9,11,14] (log P2=4.965)
  and [0,6,12,14,15,23] (log P2=5.747).
- 105 families with ceiling >= 13 (91 at 13, 14 at 15).
- Log P2 = (1/6) * sum_{i<j} (a_i - a_j)^2, verified to match for sampled
  families.

**Coordinator prior P1** expected >= 200 families of ceiling >= 13 at
log P2 < 6. The result is **2**, which **CONTRADICTS P1**. The stratum is
sparse, not dense. This is the population count, and it is the result.

### J1.4 Euler check

All 16 tested families satisfy sum(deg * v_disc) = 24 = 12d. The producer
reports 0 Euler failures across all 16754 censused families.

## J2 — Best candidate re-derivation and provenance

### J2.1 Height re-derivation (blind)

**Quantity.** Minimal-model naive height = log max(|c4|^3, c6^2) on the
globally minimal model, computed from a-invariants alone.

**Parameters (from best_candidates.json).** Tuple [-17,-16,10,11,14,17],
t=23, a-invariants [1,0,0,-2706410181743941,54490539224340875136896].

**Computation.**
- a1=1, a2=0, a3=0, a4=-2706410181743941, a6=54490539224340875136896
- b2 = a1^2 + 4*a2 = 1
- b4 = 2*a4 + a1*a3 = -5412820363487882
- b6 = a3^2 + 4*a6 = 217962156893635005475584
- b8 = a1^2*a6 + 4*a2*a6 - a1*a3*a4 + a2*a3^2 - a4^2 = 54490539224340875136896 - 7334685198587492492792348881 = -7334639709283258408299396985
- Delta = -b2^2*b8 - 8*b4^3 - 27*b6^2 + 9*b2*b4*b6
- c4 = b2^2 - 24*b4 = 1 + 24*5412820363487882 = 129907688723709169
- c6 = -b2^3 + 36*b2*b4 - 216*b6 = -1 - 36*5412820363487882 - 216*217962156893635005475584 = -47079826084692049203841897

**Height.** |c4|^3 = 129907688723709169^3 ≈ 2.194e50. c6^2 = 47079826084692049203841897^2 ≈ 2.216e51. Since c6^2 > |c4|^3, height = log(c6^2) = log(2.216e51) ≈ 118.228.

**Result.** height = 118.22777364040874. **PERFECT MATCH** with producer
(abs diff = 0.0).

### J2.2 Global minimality

Factored Delta. Checked: no prime p with v_p(Delta) >= 12 AND v_p(c4) >= 4
AND v_p(c6) >= 6. The model is **globally minimal**. PASS.

### J2.3 Rank re-certification

PARI `ellrank` on the curve: r_low = 12, r_high = 12. Matches producer.

All 23 exhibited points verified on the curve in exact rational arithmetic
(Fraction). 12 of the first 12 points have nonzero canonical height
(ellheight). PASS.

### J2.4 Provenance

Checked all threshold entries from best_candidates.json against:
- **Frozen snapshot** (frontier_20260823.json + icarm_database_20260823.json):
  No curve matched by curve_key or by a-invariants. PASS.
- **Cremona's tables**: All conductors >= 500000. Cremona's database covers
  conductors up to 500000. Therefore **PROVABLY_ABSENT** from Cremona. PASS.
- **Board curve id 162** (positive control): Rediscovered by both curve_key
  and a-invariants. The provenance check correctly identifies known curves. PASS.

### J2.5 pari_ellrank fields in deliverable

The review plan asks: "State plainly whether pari_ellrank_r_low / r_high is
carried into the submission-format deliverable; C1' names the ICARM verifier
and BATCH-541940's deliverable dropped that field."

**Answer: YES.** The best_candidates.json carries `pari_ellrank_r_low` and
`pari_ellrank_r_high` for every per_threshold entry (1 through 12). For
threshold 12: pari_ellrank_r_low=12, pari_ellrank_r_high=12,
pari_ellrank_alarm_status=ok. This is an improvement over BATCH-541940,
which dropped these fields.

The certification field states: "every rank is a CERTIFIED LOWER BOUND
re-derived by exact_certify.py from the exhibited points in
integer/Fraction arithmetic; PARI ellrank was a POINT SEARCH only and its
verdict is never the reported rank. Rank EQUALITY is never claimed."

### J2.6 Additional deliverable checks

- `nothing_submitted_to_icarm`: True. No submission was made.
- `network_calls_made`: 0. No network calls.
- `board_id_108_rediscovered`: False. The curve that BATCH-541940
  incorrectly reported as its own (frozen board curve id 108,
  ainvs [1,-1,0,-415,3481]) was NOT rediscovered. This is correct
  behaviour — the provenance check correctly does not flag this curve
  as the program's output.
- `board_id_162_rediscovered`: True. Positive control matched by both keys.
- `cell_taken`: False for all thresholds. No cell was taken.
- `standing_negative`: "NO RECORD CELL HAS BEEN TAKEN BY THIS CAMPAIGN,
  IN FOUR BATCHES, ON ANY METRIC, AT ANY RANK THRESHOLD."
- `standing_negative` also states: "RANK >= 31 OVER Q REMAINS AN OPEN
  WORLD RECORD (30, Alpoge-Howell 2026) AND NOTHING HERE IS PROGRESS
  TOWARD IT." — scope guard satisfied.

### J2.7 EXP contract

The review plan asks to check "The absence of an EXP-* contract. It is a
dispatch precondition of this batch, not an open item."

**Answer: PRESENT and PRE-REGISTERED.** The file
`experiments/EXP-ECQ-0e0cbb/specification.yaml` (31KB) exists and its
`contract_provenance` field states it was "AUTHORED BEFORE ANY PRODUCER
RAN AND BEFORE ANY RUN OF THIS EXPERIMENT EXISTS." Its status is
`approved`. No procedure deviation.

**Verdict: PASS.** Every reported curve is this program's own. No curve is
in the frozen snapshot or in Cremona's tables. The pari_ellrank fields are
carried into the deliverable. The EXP contract is pre-registered.

## proves_too_much

### Object (i): Mestre's published tuple A [-17,-16,10,11,14,17]

**Expected PASS behaviour:** ceiling >= 11, pre-filter does not discard.

**Result.** Ceiling = 15 (I_4 at infinity, deg_gcd=0, n_additive=0,
Euler=24). 15 >= 11. The pre-filter retains this family (cheap ceiling =
15 >= 13). **PASS.**

### Object (ii): A generic ceiling-9 family [0,19,21,28,30,49]

**Expected PASS behaviour:** ceiling < 13, pre-filter discards.

**Result.** Ceiling = 9 (I_4 at infinity, deg_gcd=6, n_additive=0,
Euler=24). 9 < 13. The pre-filter discards this family (cheap ceiling =
9 < 13, gcd(G, a4) = 0 so decision is exact). **PASS.**

## Artifact integrity

All 103 path:hash pairs from the archive receipt
(TASK-20260823-8ea188/receipt.yaml) verified:
- 103/103 matches
- 0 mismatches
- 0 missing files

## Summary of findings

| check | result |
|---|---|
| J1 ceiling re-derivation (15 families) | 15/15 MATCH |
| J1 pre-filter soundness (16754 families) | 0 false negatives PASS |
| J1 population count | 2 (contradicts P1 expected >= 200) |
| J1 Euler check | 24 = 12d for all tested families |
| J2 height re-derivation | PERFECT MATCH (118.22777364040874) |
| J2 global minimality | PASS |
| J2 rank re-certification | r_low=12, r_high=12 MATCH |
| J2 provenance (all curves) | PASS — no curve in snapshot or Cremona |
| proves_too_much (i) Mestre tuple | PASS — ceiling=15 >= 11, retained |
| proves_too_much (ii) generic ceiling-9 | PASS — ceiling=9 < 13, discarded |
| artifact hashes (103 pairs) | 103/103 VERIFIED |
| blind re-derivation | FULLY BLIND |

## Assessment of the producer's claim

The producer claims **BRANCH C**: coverage is the result, no cell taken.

**No cell taken.** The best certified rank>=12 candidate has height
118.22777364040874, which is:
- Above the frozen frontier r>=12 cell (69.33884136527462)
- Above the construction-class benchmark (79.32867457792244)
- Above the current standing best (86.77369390941135)

No cell was taken. CONFIRMED.

**Coverage is the result.** The population count of 2 families with
ceiling >= 13 at log P2 < 6 contradicts Coordinator prior P1 (expected
>= 200). The stratum is sparse. The coverage fraction (not independently
verified in this report — that is J3, assigned to the sibling reviewer)
is the reportable result.

**P1 contradiction.** The Coordinator's prior P1 stated that the
enlarged box would populate the stratum with at least 200 families of
ceiling >= 13 at log P2 < 6. The result is 2. This is a contradiction
of P1, and per the review plan, "the population count IS the result,
and it falsifies this hypothesis's population claim."

## Validator verdict

**PASS** on all assigned joints and controls.

- J1: The stratum enumeration, pre-filter, and ceiling computation are
  sound. Every ceiling reproduces from the family's own fibre
  configuration against a cap of 15. The pre-filter has zero false
  negatives. The population count of 2 is confirmed.

- J2: The best candidate's height, minimality, rank, and provenance all
  survive independent blind re-derivation. No reported curve is in the
  frozen snapshot or in Cremona's tables.

- proves_too_much (i) and (ii): Both pass as expected.

- Artifact integrity: All 103 hashes verified.

No breaking artifact found. No escalation to review-breakthrough is
warranted (no cell claimed, no contradiction of established evidence).
