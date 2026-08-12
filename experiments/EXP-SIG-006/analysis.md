# EXP-SIG-006 analysis — D6 null baseline re-derivation + birth-law re-measurement

Thread: **SIG asymptotics + DREG audit**. Evidence record: `ledger/EV-SIG-006.yaml`.
Numbers-only observation; status decisions belong to the Coordinator. Instrument:
bit-identical copy of the pinned EXP-SIG-001..005 instrument (sha256 verified in
every receipt). Anchor instance: boolean chained Semaev m = t = 3, n = 9, seed 1
(nb = 18, eq histogram {2: 9, 3: 9}, standard), the RUN-EXP-SIG-005-h/k cell.

## 1. Diagnosis of the C5 failure (RUN-a, all machine-checked)

**(a) The column asymmetry is NOT D6-specific and is fully explained.**
The sem's Macaulay column set is smaller than the null's at EVERY measured
degree (ncols sem/null: D3 544/936, D4 3,056/4,038, D5 11,032/12,615, D6
29,332/31,180) — it only became fatal at D6. The column-formation law is
machine-verified EXACT on both arms at all degrees:

  cols(D) = { m : |m| <= D, exists eq i and m' in supp(f_i) with m' ⊆ m and
              |m| - |m'| <= D - deg(f_i) }   (up-closure with degree slack)

with **zero cancellation/parity deviations** (simple coverage == exact row
enumeration on all 8 arm-degree cells). The sem misses only top-slice
monomials: 1,584 degree-5 monomials at D5 and 1,848 degree-6 monomials at D6,
concentrated in balanced block compositions — at D5: (2,1,1,1)-type 4×162 and
ALL 126 pure-u quintics (5,0,0,0); at D6: (2,2,1,1)-type 6×162, (6,0,0,0) 84,
(3,1,1,1)-type 4×54, (2,2,2,x)-type. The null's coverage IMPROVES with D
(missing 52/10/1/0 at D3/D4/D5/D6) because slack grows; the sem's structured,
block-sparse supports miss more as D grows. The sem's equation supports simply
contain no high-degree sub-monomials in those block patterns.

**(b) sr_pred semantics pinned exactly.** The pinned `semireg_rank_pred`
computes, via its in-place update loop, the Hilbert series

  H(z) = (1+z)^nb / Π_i (1+z^{d_i})   truncated at the first non-positive
  coefficient,

NOT the textbook Bardet series (1+z)^nb Π_i (1-z^{d_i}). Machine check:
code loop == formal (1+z^d)^{-1} series == every recorded receipt at n=9
(180/1,674/9,504/28,068 at D3..D6); the Bardet series (1,683/9,675/28,239)
does NOT match the measured nulls. HF at n=9: [1, 18, 144, 645, 1566, 738,
0, ...].

**(c) The fatal break is the FREEZE degree, not the column support.** The
series' freeze degree (first HF = 0) at each n (histogram {2: n, 3: n}):

  n = 9 → D6;  n = 12 → D7;  n = 15 → D8;  n = 18 → D9   (freeze = n/3 + 3).

At the freeze degree the semi-regular model predicts the quotient STOPS
growing (HF[6] = 0 at n=9: frozen quotient = 3,112 dims). But a real generic
system's quotient at that degree collapses to its variety size |V| ≪ 3,112.
Variety ground truth (full 2^18 enumeration): **|V_sem| = 6** (= 3!
decomposition orderings of the decomposable R), **|V_null_old| = 1**. The old
null's D6 rank is EXACTLY ncols − |V| = 31,180 − 1 = 31,179: full saturation.
The overshoot over sr_pred is exactly (frozen predicted quotient) − |V| =
3,112 − 1 = 3,111. Degree-fall arithmetic (from receipt ranks + enumerated
column degrees): the null's D6 row space contains ALL 12,615 nonconstant
degree-≤5 polynomials (≥ 3,111 fall dims beyond its D5 row space); the sem's
D6 row space contains ≥ 10,576 degree-≤5 dims (≥ 1,981 fall dims beyond its
D5 row space of 8,595). The null's extra_6 = 4,986 non-model syzygies are the
collapse syzygies: 3,111 are accounted for by the D5-quotient collapse; the
remaining 1,875 are recorded as an OPEN exact decomposition (conjecture:
relations among top-slice products induced by the collapse).

**(d) Why D ≤ 5 always worked.** Below the freeze degree the semi-regular
quotient is still growing (HF[D] > 0), the ideal's degree-≤D part does not yet
see the variety, and the generic null's rank tracks the series exactly. The C5
failure at n=9 D6 coincides EXACTLY with the freeze degree (n=9 is the only
on-lattice size whose freeze is 6; at n ≥ 12, D6 is BELOW freeze).

## 2. Corrected-null constructions and validation (RUN-b/c/d) — ALL FAIL

Three nulls, all per-equation degree-histogram matched, measured D3..D6:

| null | construction | ncols D6 | rank D6 | sr_pred | extra D6 | |V| |
|---|---|---|---|---|---|---|
| N0 (old, determinism rerun) | pinned support-matched | 31,180 | 31,179 | 28,068 | 4,986 | 1 |
| N2 | N0 + forced vanishing at random z | 31,180 | 31,179 | 28,068 | 4,986 | 1 |
| **N1** | **column-matched: D6 column set == sem's EXACTLY (29,332), by construction** | **29,332** | **28,939** | 28,068 | **7,226** | 0 |

- **N0 reproduces RUN-EXP-SIG-005-k EXACTLY** (cross-session determinism PASS).
- **N2 (forced consistency) fails identically** — consistency is not the
  operative variable (the old null was already consistent with |V| = 1).
- **N1 (the mission's literal corrected construction)**: safe-pool sampling
  (monomials whose D6 up-closure avoids the sem's missing sextics) + greedy
  set-cover + 5 swap repairs → D6 column set EXACTLY equal to the sem's
  (equal ncols BY CONSTRUCTION, verified as sets). Rejection sampling had
  failed 60/60 (RUN-b); greedy+repair succeeded (RUN-c v1 was 5 sextics
  short due to a donor-filter bug, fixed; RUN-d exact). N1 then FAILS
  validation: D3/D4 clean, **D5 anchor FAILS (extra = 369, rank 9,135 <
  sr_pred 9,504)** and **D6 FAILS (rank 28,939 > sr_pred 28,068, deficit
  −871, extra = 7,226 ≠ 0)**.

**Conclusion (the mission's anticipated clean finding):** at n = 9, D6 IS the
freeze degree; every histogram-matched generic null collapses to rank ≈
ncols − |V| with |V| ≪ 3,112 and carries non-model collapse syzygies. The
failure is NOT a support-matching defect — equal ncols by construction does
not fix it (N1). **The semi-regular baseline model itself breaks at D6 at
n = 9, and no histogram-only recalibration of sr_pred exists there**: the D6
rank depends on the instance-specific variety size |V| (0, 1, 6 measured),
which the degree histogram does not determine. The pinned baseline remains
valid BELOW the freeze degree — and predicts the D6 null is VALID at n ≥ 12
(freeze 7/8/9 at n = 12/15/18).

**Unexpected observation (AGENTS rule 8):** N1's D5 extra = 369 (also 369 on
the independently sampled near-matched RUN-c variant) — the safe-pool
constraint concentrates supports into sem-like sparse directions and thereby
INDUCES sem-like extra syzygies at D5 in a random system. A support-structured
random null reproduces part of the sem's D5 deficit (369 of 909; at D6 the
column-matched N1's rank is 1,647 ABOVE the sem's and its extra 1,671 BELOW
the sem's, in the now-identical column world). This is a measured confound for
interpreting the sem's deficits as pure cascade content (numbers only; the
interpretation belongs to the Coordinator).

## 3. sr_pred recalibration verdict for D6

- Below freeze: pinned formula unchanged (validated at D ≤ 5 on all sizes,
  and predicted valid at D6 for n ≥ 12).
- At the freeze degree (n = 9, D6): no histogram-only formula exists; the
  honest baseline statement is rank_generic = ncols − |V| with |V|
  instance-specific (measured 0/1 for nulls, 6 for the sem). sr_pred = 28,068
  is unreachable by ANY boolean system with this histogram at n = 9.

## 4. residual_6 re-measurement (RUN-e/RUN-f) — reproduced, still inadmissible

RUN-f reproduced the full RUN-EXP-SIG-005-h sem D6 closure cell EXACTLY
(cross-session determinism PASS): D6 rank 27,292, deficit 776, kernel 18,032,
rankK 9,135, extra_6 8,897; closure A3_6 = 542, A4_6 = 3,580, A5 = 6,282
(F3/F4/F5 images 988/7,052/17,290, misses 0/0/0); **residual_6 = 2,615**.
D3/D4/D5 continuity anchors and the D5 closure values (A3_5 = 128, A4_5 =
566, residual_5 = 344, residual_4 = 24) all reproduce. Deviation: the
reduction-free union crosscheck was deliberately censored
(censored_timeout_crosscheck under the 250 s soft cap — the 300 s platform
call cap forbids a full ~465 s single invocation); RUN-h's crosscheck passed
on the identical values, so the reproduction stands.

Because NO null validates at n = 9 D6, the sem D6 quantities (residual_6 =
2,615, extra_6 = 8,897, deficit_6 = 776) remain **inadmissible as cascade
evidence** — status unchanged from EV-SIG-005. They are reproduced here for
continuity and as the reference point for the now-precise baseline failure.

## 5. Controls ledger

- C1 anchor reproduction: PASS (all EV-SIG-005 receipt ncols/ranks
  reproduced before any new claim).
- C2 lower-degree anchors: PASS for N0/N2 (extra = 0, rank == sr_pred at
  D3/D4/D5); N1: D3/D4 PASS, D5 FAIL (369 — construction bias, recorded).
- C3 D6 validation: FAIL for all three constructions — the clean finding.
- C4 determinism: PASS (N0 == RUN-k; RUN-f == RUN-h on all shared values;
  N1 greedy construction deterministic by seeded design).
- C5 variety ground truth: recorded (sem 6; N0/N2 1; N1 0).
- C6 sanity identities: PASS on every measured cell (kernel == nrows −
  rank; extra == kernel − rankK).
- Deviations: (i) RUN-f crosscheck censored deliberately (see §4); (ii)
  RUN-c construction 5 sextics short (superseded by RUN-d); (iii) two RUN-e
  invocations killed at 300 s platform cap (infrastructure, NOT evidence).
- Scope censoring (deliberate, NOT evidence): n = 12 D6 null validation
  (predicted VALID by the freeze theory — the decisive confirmation cell)
  not attempted this turn; n = 9 seed 2 replication not run.

## 6. What this establishes

The EXP-SIG-005 C5 failure is fully diagnosed and is NOT repairable by
support matching: D6 at n = 9 is the freeze degree of the semi-regular
Hilbert series, where the model's frozen quotient (3,112) is unrealizable by
any generic system (|V| ≪ 3,112), so every generic null saturates to
ncols − |V| and carries collapse syzygies outside the K6 model family. The
cascade characterization stays valid through D = 5; the degree axis at n = 9
is structurally unmeasurable with this baseline family. The theory now makes
a sharp, testable prediction: **the D6 null validates at n ≥ 12** (freeze ≥
7) — the n = 12 D6 null cell (extra = 0, rank == sr_pred = 156,520 per the
series) is the decisive confirmation, queued for a budget that admits the
~200k-column echelon. Separately, the N1 support-bias extra (369 at D5) is a
new measured confound for the interpretation of sem deficits, flagged to the
Coordinator.
