# TASK-20260804-7e6b54 — the deciding surrogate, the heuristic's own null, the technique entry

**Executor, BATCH-d3a45a (batch 4 of 6), GOAL-MLKEM-004.**

**SCOPE, binding on every sentence.** Toy scale: m=35, n=25, d=60, q=127, secret
centred-binomial eta=2, error rounded-Gaussian sigma=2, **one instance**
(BATCH-f75059 replicate 0, seed 20260803206). **No ML-KEM break claim, no
security proof, no FIPS 203 parameter set affected or cleared, no speedup, no
cost claim, no exponent moved.** AGENTS.md **rule 12 UNMET and UNWAIVED**,
inherited: this report changes the status of no `EV-MLKEM-*` record and no `KN-*`
entry, and proposes none. `KN-TECH-9d21c4` is a **creation**, explicitly
authorised by the card and by `DEC-20260803-81b778` `knowledge_promotion`.

This document states **observations**. It does not conclude that any heuristic is
validated or refuted, and it does not close or open a lane — that judgement
belongs to the Reviewer and the Coordinator.

---

## 0. Instrument, rebuilt and verified before any measurement

Full verbatim record: `rebuild_transcript.txt`.

The card expected the `/tmp` venvs to be gone. **They were not** — the batch-3
validator's `/tmp/sagevenv-val3fc363`, `/tmp/gmplink-val` and `/tmp/le` were all
still present, so this container has **not** been replaced since
`VAL-20260803-3fc363`. I did not use them. I built my own venv
(`/tmp/sagevenv-exec7e6b54`) from scratch per `KN-TECH-14efa5`; both documented
fixes were required and applied; build wall clock 4 min 46 s.

Two discriminators reproduced **before** any contrast was measured:

| check | pinned by | measured here |
|---|---|---|
| `PowerSeriesRing` constructs (real passagemath, not the shim) | KN-TECH-14efa5 | OK, shim not on `sys.path` |
| `BKZ.EasyParam` raises "Cannot open strategies file" | KN-TECH-14efa5 | reproduced |
| dim 60 qary q=3329, BKZ-30 x4: `‖b0‖` 160.4 → 130.3 in 0.3 s | KN-TECH-14efa5 | **160.4 → 130.3 in 0.24 s** |
| g6k on the research instance: N, `a_x` | BATCH-c45baf archive | N = 17919, `a_x` delta = **0.0e+00 exactly** |

Deviations recorded: passagemath resolved to 10.8.8 (entry says 10.8.7);
`sage.__version__` does not exist (use `sage.version.version`). Neither affects a
discriminator.

---

## 1. T1 — the norm-matched valid-lattice surrogate

### 1.1 What was built

A **second valid dual family from the same lattice**, produced with **fpylll
only — no g6k, no sieve, and no pair reduction anywhere** (pair reduction is what
a sieve does, so it was excluded deliberately, not incidentally).

Route: LLL → BKZ-20 → BKZ-30 → BKZ-40 on the same dual basis, then randomised
nearest-plane (Schnorr random-sampling style) over the reduced basis, with
rejection at `‖v‖² ≤ 426`. 8,750,000 vectors drawn, 546,722 below the cut,
**27,550 distinct**. Of those, **72 were dropped because they *are* vectors of
the sieve database** — so the surrogate family is **disjoint from the sieve
database by construction**, not merely different from it.

Then an injective row-for-row assignment minimising the normalised 2-D mismatch
in `(‖x‖², ‖y‖²)` against the sieve's 17,919 targets. All 17,919 matched.

**Certificates, all re-verified by integer arithmetic from `A` and the emitted
vectors alone, independent of whatever produced them** (`y ≡ Aᵀx mod q`):

| family | checked entries | violating | zero | duplicate |
|---|---|---|---|---|
| SIEVE (g6k bgj1) | 447,975 | **0** | 0 | 0 |
| POOL (fpylll) | 688,750 | **0** | 0 | 0 |
| MATCHED_BKZ | 447,975 | **0** | 0 | 0 |
| MATCHED_LONG | 447,975 | **0** | 0 | 0 |

The surrogate is a valid dual family. That was the precondition for it to decide
anything, and it is met.

### 1.2 Matching quality — quantified, and it is partial

| | sieve | matched | mean rel. err | rms rel. err | median abs rel. err |
|---|---|---|---|---|---|
| mean `‖x‖²` | 181.49 | 214.54 (+18.2%) | +9.21% on `‖x‖` | 11.42% | 11.38% |
| mean `‖y‖²` | 129.08 | 179.08 (+38.7%) | +18.75% on `‖y‖` | 21.78% | 18.08% |

**This is a partial match and must be read as one.** For calibration: the batch-3
red team's E3 sat at 470.5 / 331.5 (+159% / +157%), and this task's own first
attempt (v1, superseded but recorded in the script changelog and the transcript)
sat at 248.7 / 226.2 (+37% / +75%).

**Recorded negative, and it is about one route only:** fpylll's `Enumeration`
with `BEST_N_SOLUTIONS` did **not** return 2000 solutions at radius² = 340 in
dim 60 within 412 s on a BKZ-40 basis, and randomised nearest-plane sampling
cannot reach the sieve's norm level on this lattice — the pool's minimum `‖v‖²`
was 258 against the sieve's **median** of 314. Per AGENTS.md rule 5 and the
standing lesson of `KN-TECH-14efa5`, this is a cost observation about the routes
tried, not a claim that norm-exact matching is impossible. Routes not tried:
pruned enumeration strategies, progressive BKZ above block 40,
projected-sublattice enumeration with lifting, random-sampling reduction with
basis re-insertion.

### 1.3 The measurement

Near-miss group, `sd_ratio_to_iid`, scoring identical in form to `stage_a.py`;
2000 error draws shared across arms; 6 row-permutation realisations per family.

| arm | what it is | real | rowperm | **excess** | z vs surrogate spread |
|---|---|---|---|---|---|
| **SIEVE** | g6k bgj1, the campaign's object | 0.137241 | 0.108030 | **1.2704** | 6.4 |
| **MATCHED_BKZ** | valid dual family, same lattice, no sieve, norms matched as far as achievable, **disjoint** | 0.697050 | 0.128344 | **5.4311** | **167.6** |
| **MATCHED_LONG** | same construction, deliberately longer | 0.815887 | 0.151529 | **5.3844** | 695.7 |
| **NORMMATCH_RANDDIR** | the sieve's **own** `‖x_i‖,‖y_i‖` row for row, random directions, **not in the lattice** | 0.114156 | 0.105036 | **1.0868** | 2.4 |
| **NULL_IID_PHASE** | uniform residues mod q on the sieve's own X | 0.940056 | 0.907045 | 1.0364 | 2.0 |

Controls behaving: the SIEVE arm's **uniform** candidate group gives excess
0.9968 (z −0.5) — null, as it must be. `NULL_IID_PHASE` returns 0.940 against the
pre-registered `c4(8) = 0.9650`, so the statistic is calibrated to 2.6%.

### 1.4 Which of the two named outcomes occurred

The card named two:

- **"separates at ≈1.32 → the central result is lattice membership"**;
- **"the sieve separates and the matched family does not → the effect is about
  sieving"**.

**The second is excluded, decisively.** The matched valid-lattice family
separates at **5.4311** with z = 167.6 against its own surrogate spread. It does
not fail to separate; it separates **four times harder than the sieve does**.

**The first did not occur either, in magnitude.** 5.43 is not ≈1.32. Under the
decision rule frozen in `surrogate.py` before the run — outcome A requires
`matched_excess − 1 ∈ [0.5, 2.0] × (sieve_excess − 1)`, i.e. `[1.135, 1.541]` —
the code emitted **`C_NEITHER`**, mechanically. I report that verdict as the
frozen rule produced it and do not re-score against a different one.

So: **the direction of outcome A holds and outcome B is dead, but the magnitude
bracket that would have made outcome A clean was missed by a factor of ~11 in
excess-minus-one.**

### 1.5 The residual norm mismatch does *not* explain the gap

This was the obvious objection to 1.4, and it is answerable from the same run.

| family | mean `‖x‖²` | mean `‖y‖²` | excess |
|---|---|---|---|
| SIEVE | 181.5 | 129.1 | **1.2704** |
| MATCHED_BKZ | 214.5 | 179.1 | 5.4311 |
| MATCHED_LONG | 397.5 | 270.0 | 5.3844 |
| E3 (archived, RT-20260803-d2e23e — *not measured here*) | 470.5 | 331.5 | 5.4349 |

Across a **2.2× range in mean `‖x‖²`** the non-sieve families sit at 5.38 – 5.43,
essentially flat. The excess is **not** a function of norm scale over this range,
so the +18% / +39% residual mismatch cannot be what separates 5.43 from 1.27.
Whatever distinguishes the sieve database from the nearest-plane families here,
it is not their norms.

**Observation, stated as an observation:** the sieve database is the *least*
separating of the three valid dual families measured, by a factor of ~4. The
campaign's headline 1.32 is the small end of this quantity's range, not the large
end.

### 1.6 T1's own null, per the null rule

- **Object removed:** sieve provenance. **Preserved:** the lattice, dual
  membership (certified), N, the candidate set, the error draws, the scoring
  code, and — as far as achievable, quantified in 1.2 — both norm profiles.
- **Statistic:** near-miss `sd_ratio_to_iid` excess over the family's own
  row-permutation arm.
- **Sensitivity demonstration:** `NORMMATCH_RANDDIR` — the sieve's *own* norms
  row for row on random directions **not in the lattice** — gives excess 1.0868
  (z 2.4) against MATCHED_BKZ's 5.4311 (z 167.6). The statistic separates a valid
  dual family from a norm-identical non-lattice family by a factor of **~50 in
  excess-minus-one**. The statistic has dynamic range on family identity, so a
  null result from it would have been informative. **The null is admissible.**
- **Forced value under the null not tested:** pre-registered in `surrogate.py`
  before the run. Under H_MEMBERSHIP the matched family *must* separate; under
  H_SIEVE it must not. It did. H_SIEVE is excluded on its own pre-declared terms.

---

## 2. T2 — where both arms stand against the iid prediction

**Zero compute.** Every number is arithmetic on the archived producer results.

The dual-attack independence heuristic's own reference model predicts
`sd_ratio_to_iid = 1` — strictly `c4(8) = 0.9650304561`, the sample-sd bias for
8 candidates. Using 1.0 is a 3.5% error, not negligible at this effect size.

| arm | pooled over 9 instances | vs the model |
|---|---|---|
| real database | **0.140324** | **7.126× below** |
| row-permuted surrogate | **0.106552** | **9.385× below** |

**Both arms fail the assumption under test by roughly an order of magnitude.**
The campaign's headline 1.3169 is the ratio between two objects that both fail
it. This has never been reported in three batches and cost nothing to report.

### 2.1 The null, per the null rule

- **Object removed:** the *shortness* of the candidate-discriminating phase
  offsets. The heuristic's own null object is wrong-candidate scores iid
  `N(0, 1/2N)`, i.e. uniform phase offsets.
- **Statistic:** near-miss `sd_ratio_to_iid`.
- **Sensitivity demonstration**, two archived and one live:
  - the **uniform** candidate group's real arm returns **1.000466** pooled over
    nine instances — the statistic reproduces the model exactly when offsets are
    uniform;
  - **SENS-1** (`y := 0`) returns **6.19e-15** — the statistic reads `y`;
  - live this run, `NULL_IID_PHASE` returns **0.940056** against the
    pre-registered 0.9650.

  Dynamic range `[0, ~1]` demonstrated; the arms sit at 0.107–0.140.

### 2.2 The forced value — why the campaign's null could never have repaired this

Derived before measuring the new arms:

```
sd_ratio_rowperm ≈ c4(8) · rms(2π Y/q) · rms(sin u) / sqrt(1/2),
    rms(sin u)² = (1 − exp(−4 a_x))/2,   rms(Y)² = mean‖y‖²/n
```

| where evaluated | predicted | measured | ratio |
|---|---|---|---|
| 9 archived instances, pooled | 0.107161 | 0.106552 | 1.006 (max 1.011 per instance) |
| SIEVE arm, this run | 0.106924 | 0.108030 | 0.990 |
| MATCHED_BKZ, this run (1.2× norm scale) | 0.126822 | 0.128344 | 0.988 |
| MATCHED_LONG, this run (2.2× norm scale) | 0.156870 | 0.151529 | 1.035 |

The first row is **post hoc** and is labelled so in the script; rows 2–4 are
**out of sample** — the closed form was frozen before those families were scored.
It holds to 1.2% and degrades to 3.5% as the first-order expansion parameter
grows.

**The consequence is the point.** The shortfall below iid is caused by `‖y‖`
being short. **A row permutation preserves the `‖y‖` multiset exactly.** So the
surrogate arm was *forced* to fail the reference model too. Every archived arm
that preserves the `y` multiset sits in the same place:

`rowperm 0.1058 · randdir 0.1053 · colperm 0.1067 · rearrangement-max 0.1131 ·
rearrangement-min 0.1100 · length-sorted 0.1108`, against real 0.1381 and
`y := 0` at 6e-15.

The campaign's entire control set preserved the object responsible for the
heuristic's failure. **This is the quantity that tests the independence
assumption, and it was never the quantity being compared.**

---

## 3. T4 — the two loose ends

### 3.1 Stage B's 10.6× shortfall — recorded

Stage B measured **N = 4253** vectors on all three instances against its own
**modelled** `Nf = 45128.788121081096` for p = 2: a **10.611× shortfall**, stated
nowhere in the BATCH-c45baf package. p = 3 (`Nf` 716.55) and p = 5 (`Nf` 99.27)
are comfortably covered — 0.168× and 0.023× of N.

**Measured vs modelled, kept separate:** `N` is a count of sieve vectors
(measured); `Nf` is a cost-model output (modelled) under that model's own
optimistic assumptions. p = 2 is also the arm carrying Stage B's largest
deviation (excess 0.9607 ± 0.0187). Raised by `VAL-20260803-3fc363` DEF-5 and
`EV-MLKEM-b43de0` OBS-1.

### 3.2 The null-registry contradiction — resolved

`stage_b_results.json → nulls[0]` records `statistic_reads_the_object: "YES"` and
`can_it_fail: "YES, for every group AND for the correct bin"`. Section 5.3 of the
same package says the producer has **not** demonstrated that the group statistics
can read the pairing.

**Resolution: both statements are true, of *different statistics*, and the
registry entry is defective because it is unqualified.** The Stage B null lists
three statistics under one `statistic` field:

- the **correct-bin score**, which *does* read the pairing carrier `ψ_i`
  (paired `|z|` medians 14.8–31.3) — the JSON is right about this one;
- the **across-candidate group contrasts**, which do not at first order, because
  `ψ_i` is candidate-independent and multiplies every candidate's row-`i` term
  identically — section 5.3 is right about these.

`statistic_reads_the_object` is a property of an **(object, statistic) pair** and
must be recorded once **per statistic**, never once per null. A consumer reading
the JSON reaches the opposite conclusion from a consumer reading §5.3.
**Section 5.3 is the correct side; the JSON field is the defective one.** Both
remain archived and unedited — this task edited no BATCH-c45baf artifact. This is
Mode 2 in `KN-TECH-9d21c4` and it is the worked case there.

---

## 4. T3 — the technique entry

`knowledge/techniques/KN-TECH-9d21c4.md` is written and is a **creation**, not a
status change. It states the four-part obligation (object / statistic /
sensitivity demonstration / **forced value**), the three failure modes grounded in
this campaign's three distinct failures, the algebra showing that a monotone
increase in `N` is implied by any fixed separation, the both-arms-vs-reference
diagnostic with the closed form above, and a copyable checklist. It is written so
a reader who knows nothing about this campaign can apply it, and it carries its
own non-claims.

---

## 5. What is open after this task

1. **Why the sieve database separates *less* than a nearest-plane family of the
   same lattice.** Both are valid dual families; the gap (1.27 vs 5.43) is not
   norms (§1.5) and is not sieve-vs-lattice in the direction anyone predicted.
   The plausible mechanism — the nearest-plane families are internally structured,
   so their `x`-database is far more coherent at the frequencies `a_k` — is
   **untested**, and testing it is cheap.
2. **Norm-exact matching** was not achieved (+18% / +39%). Four routes are named
   in §1.2 and none was tried.
3. **Nine instances → one.** T1 is a single instance. Nothing here replicates
   across instances, and the campaign's own history says replication of a forced
   quantity proves little — but 5.43 vs 1.27 on one instance is one instance.
4. **The heuristic itself remains untested.** Four batches in, both arms of every
   comparison fail the reference model, and no measurement in this campaign has
   yet been *of* the independence assumption.

## 6. Explicit non-claims

- No ML-KEM break. No attack implemented, run, or claimed. No speedup.
- No security proof and no security claim in either direction.
- No FIPS 203 parameter set affected or cleared. Toy scale, AGENTS.md rule 7 in
  full.
- The independence heuristic is neither validated nor refuted here.
- No exponent moved, no cost reduced, no attack improved.
- No lane is closed or opened by this report. `C_NEITHER` is a verdict about a
  frozen decision rule, not about the research direction.
