# TASK-20260805-bb0559 — validator working notes

Independent validation of snapshot `7983a474`, BATCH-a51f91, four producers,
52 artifacts. Verdict and per-claim statuses are in `report.yaml`; this file
records the reasoning behind the three judgements that took the most work, and
the defects nobody else caught.

**Binding scope, restated before anything else.** Nothing below is an ML-KEM
claim. AGENTS.md rule 12 is UNMET and UNWAIVED and this report changes the
status of no `EV-MLKEM-*` record and no `KN-*` entry. The mechanism is SESSION
recovery. No number in this batch or in these notes may be subtracted from the
in-repo `primal_bdd` margins of 2.80 / 6.04 / 1.28 bits. Toy scale is not
crypto-scale.

---

## 1. T2's zero-contrast derivation — does it hold?

**Yes, as a theorem. The word "exactly" does not survive contact with the
statistic it is applied to.**

### 1.1 The theorem, reconstructed rather than accepted

Let `P` project onto a Haar-random `β`-dimensional subspace of `R^d`, drawn
independently of `e ≠ 0`, and write `u = e/‖e‖`. Then `P` is distributed as
`V P₀ Vᵀ` with `V` Haar on `O(d)` and `P₀ = diag(1_β, 0)`. So

```
R = uᵀ P u = ‖P₀ Vᵀ u‖²  =  squared norm of the first β coordinates of Vᵀu,
```

and `Vᵀu` is uniform on `S^{d−1}` for every fixed unit `u`. The squared norm of
any `β` coordinates of a uniform point on the sphere is exactly
`Beta(β/2, (d−β)/2)`. **The law does not depend on `u` at all.** Mixing over any
error law therefore leaves it unchanged: for a Haar projector, the marginal law
of `R` is `Beta(β/2,(d−β)/2)` whatever the error distribution — isotropic,
anisotropic, discrete, or a single deterministic vector.

This is the load-bearing claim, and it is correct.

### 1.2 Numerical corroboration, my own code

16384 Haar draws at `d=100, β=30`, three maximally different fixed unit vectors:

| fixed `e` | KS vs `Beta(15,35)` | p | mean vs `β/d = 0.3` |
|---|---|---|---|
| `(1,0,…,0)` | 0.00498 | 0.809 | 0.30000 |
| all-ones/√d | 0.00656 | 0.480 | 0.29973 |
| one CBD draw | 0.01014 | 0.068 | 0.29888 |

The producer's V6a reports 0.00611 / p=0.572 for the first of these. Different
seed, different code, same answer, and two extra vectors.

### 1.3 Where "exactly" fails

The declared demonstration statistic is *not* a functional of the marginal law.
It is the **mean over projector draws of an empirical order statistic computed
on `N` samples that share one projector**. Conditional on `P`, the `N` values
are iid from `F_P`, and `F_P` differs between the two arms — that difference is
precisely what the producer's own V6c measures. An order statistic's expectation
is a nonlinear functional of `F_P`, and quantiles do not commute with mixing, so
equality of the marginals does *not* force equality of the two arms'
expectations.

So the derivation proves "the two arms have identical marginals", and the report
writes down "expected contrast exactly zero", which is a strictly stronger
statement about a statistic that reads more than the marginal. The gap is second
order and both measurements say it is tiny — but "exactly" is the kind of word a
validator has to take literally, and `KN-TECH-1a5b7e`'s own caution in *How to
run obligation 4* ("the value the assumption predicts is usually an
**asymptotic** one, and your estimator is run at finite sample size") is exactly
this failure mode, one level up. Recorded as **DEF-1**.

**None of this disturbs the negative.** My own 64-draw run at `d=100, β=30`,
`N=2^18`, using the frozen quantile estimator:

- signed shift **−0.0010883**, i.e. **0.50** pooled standard errors of the
  difference, and **0.17** times the isotropic arm's own between-draw sd
  (denominator: that arm's between-draw sd of the `2^-10` quantile ratio over
  its 64 draws), against a gate needing 4;
- the producer's V6b got **+0.00267** at **1.09** pooled standard errors.

Two independent measurements, **opposite signs**, both an order of magnitude
below the gate. That is what a near-zero expected contrast looks like, and it is
better evidence than either measurement alone.

### 1.4 The producer did not substitute the statistic that works

Checked in three places and it holds. `results.json` and `receipt.json` both
adjudicate branch **NEITHER**, classification `invalid_measurement`. `report.md`
§5.3 says in terms: *"These do not rescue the demonstration and are not offered
as a substitute."* §6 says the `P1 ∧ P2` branch is **NOT** taken. The
`Var_P(E[R|P])` result appears only as diagnostic V6c and as a *requested*
amendment for the Coordinator to grant. The frozen threshold was not adjusted
and no run was re-scored. The second permitted protocol run was deliberately not
used.

This is the most creditable thing in the batch. A producer that derives the
reason its own gate could not fire, finds the statistic that *would* have fired,
and then declines to score against it is doing the thing pre-registration exists
to produce.

### 1.5 Freeze ordering

`prediction_frozen.json` hashes to `29797476…`, and that same value appears in
`prediction_frozen.sha256`, hardcoded at `measure.py` line 50 as
`FROZEN_SHA256`, in `receipt.json`, and printed in `stdout.log` as both
`sha256` and `expected`. The archived file *is* the file the run hashed. Freeze
16:38:29Z precedes the run either way — but the receipt gives **two different**
start times for the same run (16:42:58Z in `runs[]`, 16:44:53Z in
`completion_gate` and in `report.md`), and only 16:42:58Z is consistent with the
recorded finish and 337.32 s wall clock. The freeze time is a self-reported
mtime git does not preserve, and the smoke run has no timestamp at all.
**DEF-4** — ordering survives, the record does not agree with itself.

### 1.6 Two things nobody caught in T2

**DEF-2 — the ×1198 and the 0.69% are quoted past their resolution.** The closed
form reproduces *exactly*: I evaluated
`Var_Beta · (d/(d−1)) · (Σsᵢ⁴ − (Σsᵢ²)²/d)/(Σsᵢ²)²` by hand and by code and got
`1.4973262032085532e-05`, digit for digit. The *measured* figures are another
matter. `verify.py` computes V6c from V6b's **64** draws, and a 64-draw sample
variance has relative sd `√(2/63) = 17.8%`. My independent 64-draw measurement
lands 22.7% below the closed form (1.3 sd — unremarkable) and gives **827** for
the ratio whose denominator is the isotropic arm's between-draw variance of
`E[R|P]` — a denominator the producer itself places at the sampling floor
`Var(R)/N`. A ratio whose denominator is an estimator floor is not a physical
contrast, and 1198 and 827 are the same quantity measured twice. This is
material only because the requested D2 amendment rests on both numbers; per
`KN-TECH-1a5b7e` mode 5, a generated comparator needs ≥8 draws *of the
comparator* and an interval, not a point.

**DEF-3 — the gate's yardstick is the wrong yardstick.** The demonstration arm
reuses the **same 8 projector draws** as the Haar arm, so the quantity
thresholded is a *paired* difference of means. The declared spread `s` is the
*unpaired* per-draw sd of one arm. Recomputing from the archived per-draw arrays:

| cell | shift | frozen `s` | shift/`s` | paired diff sd | \|shift\|/(sd_paired/√8) |
|---|---|---|---|---|---|
| d100_b30 | +0.002015 | 0.002544 | 0.79 | 0.010824 | 0.53 |
| d100_b40 | −0.002747 | 0.002525 | 1.09 | 0.014254 | 0.55 |
| d140_b30 | −0.006091 | 0.003093 | 1.97 | 0.011717 | 1.47 |
| d140_b40 | +0.007220 | 0.001938 | 3.73 | 0.012142 | 1.68 |

Every `s` and every `signed_shift` in the receipt reproduces from the raw arrays
to better than 1e-12 — the arithmetic is sound. But `4·s` = 0.0078–0.0124 is
**smaller** than 4 proper standard errors of the paired difference
(0.0152–0.0200), so the declared gate is a 1.8–2.7 σ test wearing a 4 σ label.
**Direction matters: the gate was more lenient than it reads, and it still failed
in every cell.** The negative is robust to the correction and is understated by
it.

### 1.7 One observation the run's own data support

The demonstration arm's between-draw sd of the `2^-10` quantile ratio is
**4.86 / 5.79 / 4.33 / 5.75** times the Haar arm's, where the denominator in each
case is the Haar arm's between-draw sd of the same ratio over the same 8 draws.
So the manipulation is loud in the **spread** of the declared statistic at the
declared 8 draws, inside the protocol run, with zero extra compute — a cheaper
candidate for a successor gate than the separate `Var_P(E[R|P])` diagnostic.
Recorded as an observation about archived data. Adopting it is the Coordinator's
call; I have neither adopted nor implemented it, and I did not re-score anything
against it.

---

## 2. T3's sequential-`cost_zeta` finding — does it hold?

**Yes, and it is the most solid finding in the batch. I read the source and ran
the code.**

`estimator/lwe_primal.py` at the pinned revision `3e48ef421ec2`:

- **step 1** searches `β` with `local_minimum(40, max_beta + precision)`, calling
  `f(beta, …)` where `d` comes from the closed-form heuristic inside `cls.cost`;
- **step 2** then runs `local_minimum(params.n − zeta, cost["d"] + 1)` with
  `f(beta=cost["beta"], d=d)` — `β` **pinned**.

There is no loop back. The reported `β` is the argmin of a one-dimensional
search along the heuristic curve `d(β)`, never the joint argmin over `(β,d)`.
The producer's own qualifier — *"d follows beta through the closed form; what it
never does is hold d fixed INDEPENDENTLY of beta"* — is the right one and is
present, which matters: the naive version of this finding would have been wrong.
Measured consequence at the baselines: step 2 moves `d` by +8 / +31 / +35 and
`log2(rop)` by 0.0088 / 0.0263 / 0.0263 bits.

**The upstream anomaly A1 is real.** `PrimalHybrid.__call__` builds
`f = partial(self.cost_zeta, …)` **without** `**kwds`, and the explicit-`zeta`
branch — the one `primal_bdd` always takes, since it passes `zeta=0` — is
`cost = f(zeta=zeta)`. Every extra kwarg is dropped silently. Confirmed by
execution: `primal_bdd(Kyber512, RC.MATZOV, optimize_d=False)` returns
`140.1994731076207 / β 389 / d 1005`, identical to the default call, while
`PrimalHybrid.cost_zeta(…, optimize_d=False)` returns `140.20824345474767 /
d 1013`. Exactly the producer's numbers. Correctly recorded and correctly not
patched.

**Everything else in T3 reproduced digit-for-digit** from my own script:

- all three baselines (`140.1994731076207 / 200.9587149140538 /
  270.7236234535225`, β = 389 / 606 / 855, d = 1005 / 1420 / 1867);
- four finite-difference cells;
- the named non-monotone triple, Kyber512 β = 387 → 389 → 387 as c goes
  0.9775 → 0.98 → 0.9825, plus 386 at 0.975 and 388 at 0.985;
- OLS slopes 118.445 / 166.608 / 224.480, residual sd 0.494 / 0.452 / 0.685, se
  2.477 / 2.266 / 3.432, all recomputed from the recorded raw points with my own
  regression;
- bits per block 0.27416 / 0.28039 / 0.28009, so 0.292 exceeds each by
  **6.51% / 4.14% / 4.25%, where the denominator in each case is that set's own
  estimator OLS bits-per-block**;
- the a-priori ratio `1/(4β ln δ)` = 0.15863 / 0.13938 / 0.12732 at
  β = 389 / 606 / 855, computed by hand — confirming the obligation-4 label that
  the linearisation comparison is a **design audit, not a finding**;
- `β = 40` is genuinely the estimator's own search floor, which is why toy n=100's
  `Δβ_fd = 0` is forced.

One sharpening the producer did not state: over the non-monotone triple,
`log2(rop)` **is** monotone increasing (139.4838 < 139.6277 < 139.6341). So `β`
is a non-monotone readout of a monotone cost. That strengthens the caution rather
than qualifying it.

---

## 3. The corpus recount

Independent recount over `knowledge/literature/`, YAML front-matter parsed with
the `yaml` library rather than by regex, at a tree I first confirmed is unchanged
between the producer's measurement commit `096b9256b` and HEAD.

| figure | T4 reports | I count | |
|---|---|---|---|
| literature entries total | 7,809 | **7,809** | exact |
| `citation_verified: read` | 7,459 | **7,459** | exact |
| `web` / `false` / `true` / `full_text` / `full_text_supplied` | 314 / 21 / 9 / 4 / 2 | **314 / 21 / 9 / 4 / 2** | exact |
| entries stating "no abstract was extractable" | 1,939 | **1,939** | exact |
| …of those marked `read` | 1,938 | **1,938** | exact |
| entries naming a `downloads/` path | 7,421 | **7,421** | exact |
| `read` **and** every identifier null | 5,582 | **5,582** | exact |

**Every figure reproduces exactly.** The histogram sums to 7,809. The single
"no abstract extractable" entry *not* marked `read` is `KN-LIT-7607`, which
carries `web` — a detail the producer's count implies but does not name.

These are observations about corpus hygiene, not about ML-KEM. Acting on them is
a curation decision outside every role in this batch, and T4 correctly says so.

---

## 4. T1 — the census, and the two things it gets slightly wrong

### 4.1 What checks out

- **Row counts exact.** 24 rows, 14 deployment_mode / 8 governing_clause /
  2 scope_note; `m_class` gives 6 / 8 for deployment modes and 2 / 6 for
  governing clauses, matching the declared `row_counts` field.
- **Largest numeric M is 1.** I scanned every `m` field for numerals and read
  each in context; the only others are the SP 800-57 "1 to 2 years"
  cryptoperiod, which is time and not a count.
- **Source pinning is real.** I re-fetched six of the 25 pinned sources today and
  all six are **byte-identical** in size and sha256 to what the receipt pins:
  FIPS 203, `draft-ietf-tls-hybrid-design-16`,
  `draft-sfluhrer-cfrg-ml-kem-security-considerations-05`, RFC 9629,
  `draft-ietf-tls-esni-25`, RFC 9180. A census whose sources hash-match a year
  from now is a census that can be falsified, which is the whole point of the
  producer's design.
- **The FIPS 203 negative search reproduces, and is stronger than stated.** The
  installed `pypdf` and `pdfminer` both die on a broken `cryptography` rust
  binding; I stubbed the module (safe — the PDF has no `/Encrypt`) and ran
  positive controls *before* reading any zero: "module-lattice-based
  key-encapsulation" 60 hits, "shall remain private" 1, "sp 800-227" 11,
  "decapsulation key" 38. Then: **zero** hits for cryptoperiod, "number of
  {queries, decapsulations, encapsulations, ciphertexts, uses}", multi-user,
  multi-target, "at most 2", "single use", "single-use", "one-time", "limit the
  number". I added seven terms the census did not declare — "use count", "usage
  count", "maximum number", lifetime, rotate, rotation, "how many" — and the only
  hits are a rejection-sampling iteration cap and a sentence about *variable
  names* being reused. FIPS 203 states no use-count bound.
- **The delegation sentence is verbatim present** in a byte-identical
  `draft-ietf-tls-hybrid-design-16`, and the draft's only `2^` figures are
  `2^16−1` **byte** length limits on `key_exchange` — sizes, not counts.
- **CNSA 2.0 returns 403 to me too.** The acquisition failure reproduces and is
  correctly recorded as MISSING rather than as a specification stating no bound.
- **Four "not stated" rows re-read at source** (R24, R18, R15, R06): no hit in
  any of them bounds ciphertexts per key. The hits are bit-security statements,
  extension counting, DNS label lengths, XOF call counts and draft-expiry
  boilerplate.
- **The refusal to read a ceiling is the correct call** and is stated twice,
  symmetrically — none of the 8 count-unstated modes forbids a large M either.
  Under `docs/inventor-protocol.md` that is the difference between a negative
  result and a fatigue report.

### 4.2 DEF-5 — the delegation does not dead-end

The clause reads: *"…abides by any bounds in the specification of the KEM **or
subsequent security analyses**."* The census quotes the whole sentence in R13's
`bounding_mechanism` column, so nothing is hidden. But R13's derivation and the
census's load-bearing structural finding both address only the first limb and
conclude *"the delegation therefore terminates without a value."*

The second limb does not terminate. It points at an open, unenumerated
literature — and **that is exactly where this batch's own T4 read sits**
(Bernstein, ePrint 2022/1580, which is a subsequent security analysis of the
multi-ciphertext-per-key question). Two tasks in one batch touch the two limbs of
one sentence and neither notices.

Direction: this makes the chain **more** open, not less, so it cuts the same way
as the producer's own refusal. It is a correction to the summary, not a reversal.

### 4.3 DEF-6 — R12 and R14 are not "M = 1"

The census's Distribution sentence says *"6 fix M = 1 (R09, R12, R14, R20, R21,
R22)"*. But R12's own `m` field reads **"1 per handshake"** and its own
derivation says *"This is structural, not a normative single-use rule: see R13
for the governing reuse clause, which permits key-share reuse."* R14 says
*"Structural, as R12."*

`M` is defined at the top of the census as **the number of ciphertexts
decapsulable under one ML-KEM encapsulation key**. For a TLS client key-share
that number is 1 only if the implementation chooses freshness; the governing
clause explicitly permits reuse and delegates the bound. On the census's own
definition, R12 and R14 belong in `count_unstated`, and the deployment-mode
distribution becomes **4 fix M = 1 and 10 state no count bound**, not 6 and 8.

The row-level text discloses it; the headline does not carry it. Again the
direction weakens the M = 1 side and strengthens the producer's refusal — which
is why I am confident it is an error of summarisation rather than of intent.

---

## 5. T4 — the abstinence, checked line by line

I enumerated every occurrence of `2021/1351`, "Duman", "prefix hashing",
"CCS 2021" and the DOI across both deliverables and read each in context.

**The abstinence holds.** `reads.md` §3.2 states it flatly: *"The body of
2021/1351 is not summarised here and no mathematical conclusion is drawn from
it."* §3.3 reports the abstract only, retrieved at HTTP 200. Every substantive
statement in §3.4 is introduced as Bernstein's — *"Its findings, as the paper
states them"* — and §3.5 records the limit and asks a Reviewer to obtain the
paper before treating the verdict as settled. `corpus_hygiene.json`'s draft entry
carries an explicit instruction that it *"must NOT relay Bernstein's
characterisation of it as if it were that paper's own content."*

That last instruction is the tell of a producer that understood the hazard rather
than merely avoided the words.

**One thin spot (DEF-8).** §3.3 adds *"i.e. in the introduction, as a remark
supporting the applicability of the main FO theorem, not as the paper's headline
theorem."* "Page 3" is sourced to Bernstein. The characterisation of the
statement's **role** inside a body that was not read is an inference past him.
Hedged, immaterial, and worth one sentence of correction.

**DEF-7 — one overstatement in §4.0.** *"The route by which a prior task obtained
the full text is not recorded in this repository"* is too strong.
`inputs/MLKEM-DUAL-SOURCES-20260802/provenance.json` records a **successful**
retrieval — CWI institutional repository, HTTP 200, 2,523,731 bytes,
sha256 `8915ed36…`, labelled "journal-version-of-record-2025-11-20". What is
unrecorded is the route to the **scratchpad copy specifically**, which is a
different version — and that difference independently explains the
two-typesetting anomaly the same section reports. Everything T4 declares about
the scratchpad file itself (1,021,750 bytes, mtime 2026-08-02T17:47:20Z,
sha256 `947f2826…`) I confirmed exactly.

**DEF-9 stands regardless:** that PDF is not in the declared artifact set, so
`reads.md` §4's content is `unable_to_check` by me and must not be cited
downstream as archived.

---

## 6. The four Coordinator-recorded defects

All four are stated accurately. Details in `report.yaml` under
`coordinator_recorded_defects_audit`; the short version:

1. **Inference blocks omitted from every card** — accurate, and *"every card"* is
   exact: at `096b9256b` all **eight** cards lack the block, including both
   Coordinator archival cards and this validator card. Fixed at `b0a72b920`.
   Follow-on nobody recorded: T2 ran at `096b9256b`, i.e. *before* the fix, and
   its receipt records `requested_policy: executor-implementation` without noting
   that its card carried none at run time. T1 and T4 both note it explicitly.
2. **T2's demonstration has expected contrast exactly zero** — substantively
   accurate, and it does convict the Coordinator's own card, which is the
   creditable part. One word overstated (§1.3).
3. **Two of four frozen `variance_values` entries wrong, formula correct** —
   exact. I recomputed `2β(d−β)/(d²(d+2))`: d140_b30 frozen
   `0.0024152803180914513` against `0.0023713710836447254`, relative error
   `1.85e-02`; d140_b40 frozen `0.0028747433264887066` against
   `0.002874389192296637`, relative error `1.23e-04`. `measure.py` computes from
   the formula, never the list, and the file was correctly **not** edited.
4. **The batch objective's "~4–6%" matches nothing T3 reproduces** — accurate. I
   reproduced all three candidates independently: the a-priori omitted/retained
   ratio **12.7–15.9%** (denominator: the retained term), the OLS slope gap
   **−4.0 / −1.4 / +3.1%** (denominator: the linearised `1/(2 ln δ)`), and the
   0.292-vs-MATZOV gap **+4.14 to +6.51%** (denominator: the estimator's own OLS
   bits-per-block). Only the third overlaps the band, and it is a cost-model
   constant mismatch, not a dropped-term effect. The Coordinator's own account of
   its own error is exact.

---

## 7. Why `ADMISSIBLE_WITH_DEFECTS` and not something else

**Not `INADMISSIBLE`,** because nothing in the package is fabricated,
overclaimed, or out of scope. Every load-bearing number I checked reproduced —
36 of 45 claims outright, five with a stated caveat, three not reproduced as
worded, one unverifiable because its source sits outside the snapshot. The three
"not reproduced" items are a precision overstatement (DEF-2), a dropped clause
limb (DEF-5) and a classification that contradicts its own row text (DEF-6).
**None of them reverses a producer conclusion, and two of the three push the
record in the direction the producers already argued for.**

**Not `ADMISSIBLE`,** because DEF-2, DEF-5 and DEF-6 are things a downstream
reader would otherwise carry forward as established, and DEF-10 means the
dispatcher has not yet accepted the snapshot at all.

The batch's three negatives all survive independent re-derivation:

- **T2's instrument failure is real and its diagnosis is correct** — and it is
  more robust than the producer claims, because the gate it failed was more
  lenient than its `4·s` label suggests (DEF-3).
- **T3's sequential-`cost_zeta` finding is correct**, verified from the pinned
  source and by execution, with the right qualifier attached.
- **T4's kill condition genuinely does not fire**, and the verdict is correctly
  scoped to the retrievable record rather than to DHKLS being wrong.
- **T1 declines to read its own table as a ceiling**, which under
  `docs/inventor-protocol.md` is the difference between a negative result and a
  fatigue report — and DEF-5 and DEF-6 make that refusal *more* justified.

A last word on independence, because it is the weakest part of this review and
saying so is part of the job: this validator and all four producers resolve to
the same model family. I re-derived every number from primary artifacts, primary
sources and independently written code, which is the only independence available
under this harness. It is **not** the independence AGENTS.md rule 12 requires,
and rule 12 remains unmet and unwaived.
