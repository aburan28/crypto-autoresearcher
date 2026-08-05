# VAL-20260804-264ab9 — what I actually re-derived

Validator, BATCH-a2bb63 (batch 5 of 6), GOAL-MLKEM-004.
Reviewing Coordinator snapshot `82bcbbe4`, archiving `TASK-20260804-f58d34`.

**SCOPE, binding on every number below.** m=35, n=25, d=60, q=127, σ=2, η=2;
Stage B sieve at dim 50. ONE LWE instance. TOY SCALE. No ML-KEM break claim, no
security proof, no FIPS 203 parameter set affected or cleared, no speedup, no
cost claim, no exponent moved. AGENTS.md rule 12 UNMET and UNWAIVED, inherited:
nothing here changes the status of any `EV-MLKEM-*` record. I did not produce
this package and I have not repaired it. I ran no `git commit`.

**Verdict: `ADMISSIBLE_WITH_DEFECTS`,** nine numbered defects, `DEF-1` high.

---

## 0. How I worked

I did not import `dependence.py`. I re-implemented the scorer, the seven
dependence statistics, the E[max of K iid normals] quadrature and its inversion,
the CAL-PERM arm, and the closed-form covariance from the definitions in the
frozen pre-registration, then fed them the archived `vectors.json` plus the
recorded seeds.

First I checked that the archive is the object it says it is: `A` and the secret
`s` regenerate bit-for-bit from `INSTANCE_SEED = 20260803206` with numpy
`default_rng`. They do. So the archived instance is the one the seed names, and
every downstream check is anchored.

Five computation passes, 172 s of compute against a 2400 s budget.

---

## 1. Integrity, first, because nothing else matters if it fails

All seven declared paths are present in the commit and sha256-identical to both
the snapshot receipt and the producer's own `receipt.json`. Parent `a18d8fe8`
matches; the commit is an ancestor of HEAD; `diff-tree` shows exactly the seven
declared additions plus the Coordinator's own archive receipt, nothing modified,
nothing outside `write_scope`. Zero files under `ledger/` changed. Working tree
clean. `KN-TECH-9d21c4` has one commit in its history (the batch-4 snapshot) and
zero diff lines in this one.

**The `report.md` extraction — checked, not assumed.** I loaded `results.json`,
took the `report_markdown` string, and compared it byte-for-byte with the file on
disk. Equal exactly: 20,346 bytes both, not even a trailing newline added. sha256
`001bf3fd00052719c26de3ac6ddb7749741e4951b65923d8de3ec62166cf68cd`, whose 16-hex
prefix is the `001bf3fd00052719` declared in the queue's `coordinator_amendment`.
The Coordinator introduced no content.

**The certificate, from the snapshot alone.** Batch 4's could not be checked
without regenerating; this one can. With stock numpy only — no g6k, no fpylll, no
`dependence.py` — I verified `X·A ≡ Y (mod 127)`:

| family | violating / checked | zero rows | dup rows | dup x-rows |
|---|---|---|---|---|
| SIEVE | 0 / 447,975 | 0 | 0 | 0 |
| SIEVE_SUMS | 0 / 447,975 | 0 | 0 | 0 |
| STAGEB_LAT | 0 / 63,795 | 0 | 0 | 0 |

Total 0 of 959,745, matching the producer's figure exactly. I then re-checked 50
rows per family (150 total) in exact Python bigint from my own random sample:
0 violating. int64 headroom bounds recomputed and all far below 2^62.

**No wall-clock truncation.** Every one of the twenty `time.time()` calls in
`dependence.py` is an elapsed-time print or a duration record; none is in a loop
condition. All four `while` loops are count-bounded. The single executable
`break` (line 1097, the SIEVE_SUMS dedup) is bounded by `len(idx) >= N`. Batch
4's `EV-MLKEM-ba6c25` OBS-2 defect is fixed.

**Bit-reproducibility.** I reproduced T0, T1 and T2 from the recorded seeds. Of
147 statistics compared against `results.json`, every `K_eff_trail`,
`offdiag(R_raw)`, `offdiag(R_ctr)`, `var_cv` and CAL-PERM `K_eff_trail` value
agreed at **0.00e+00** — exact. The `K_eff_max` family agreed to relative 1e-4,
the residual being my own quadrature grid for E[max], not the data.

---

## 2. The central check — I derived what the generation procedure forces

### 2.1 The closed form is correct, and it is mine independently

From the Gaussian characteristic-function identities for centred jointly Gaussian
`u`:

```
E[cos u_i cos u_j] = e^{-(v_i+v_j)/2} cosh r_ij
E[sin u_i sin u_j] = e^{-(v_i+v_j)/2} sinh r_ij
E[cos u_i sin u_j] = 0                              (exactly, by u -> -u)
```

with `v_i = (2πσ/q)²‖x_i‖²` and `r_ij = (2πσ/q)²⟨x_i,x_j⟩`, I get term for term
the producer's

```
Cov(S_k,S_k') = (1/N²)[ a_k^T C a_k' + b_k^T S b_k' ]
C = P∘(cosh T − 1),  S = P∘sinh T,  P = pp^T,  p_i = e^{−c‖x_i‖²},  T = 2cXX^T
```

My own blocked N×N pass over the archived X reproduces the producer's
closed-form table to four decimals — 6.052 / 17.480 / 6.784 / 22.066 with ratios
0.8646 / 0.7283 / 0.9692 / 0.9194 — and my own 3×10⁵-draw unrounded-Gaussian
Monte Carlo agrees to 0.008 relative max error (MC noise at that sample size;
the producer's KAC-1 at 4×10⁵ gives 0.00243).

So the whole correlation structure is a deterministic functional of `(X, Y)`,
computable with no scoring. The producer says this itself. The question is what
follows.

### 2.2 What the procedure forces, derived

Expand the Hadamard series. `P∘sinh T = 2c·diag(p)XX^T diag(p) + O(T³)`, of rank
at most **m = 35**. Meanwhile `C`'s diagonal `C_ii = (1+e^{−4a_x})/2 − e^{−2a_x}`
is O(1) and its off-diagonal decays. Two regimes follow, and **both are
properties of the score definition and the error dimension, not of the dual
family**:

- **Short offsets.** `cos φ_ik ≈ 1` for every k, so the cos channel is a pure
  rank-one common mode carrying no discriminating variance — I measure its
  variance share at **0.9999–1.0000 in every short-offset arm, real or
  synthetic**. All discrimination is pushed into the sin channel, which lives in
  a space of dimension ≤ 35 with an anisotropic metric. `K_eff_trail` is forced
  well below `K−1` **even for random b, and even for K < m**.
- **Spread offsets.** The cos channel's near-diagonal, full-rank, white part
  dominates (variance share drops to ≈0.41) and near-independence is restored.
  Hence uniform candidates return the law's value.

So the m-dimensional shared error acts through **channel composition at matched
K**, and through **rank truncation at K > m**. The producer derived only the
second. Its own disclosure — "at K = 512 this statistic reads nothing about the
dual family" — is correct and I confirm it (real 0.3571 vs null 0.3601, 0.83%),
but it is not the whole account.

### 2.3 The controls that settle it

Everything below is `K_eff_trail/(K−1)`, closed form, **no scoring**, at matched
K, matched N, matched m, matched offset-magnitude distribution.

| arm | what it destroys | nm K=8 | nm K=25 | sdist K=25 |
|---|---|---|---|---|
| REAL — X=sieve, Y=sieve | — | 0.8646 | 0.7283 | 0.4149 |
| NULL-IIDPHASE — Y uniform mod q *(the producer's null)* | offset shortness **and** the X–Y pairing | 0.9811 | 0.9281 | 0.9163 |
| CTRL-RP — Y row-permuted | the X–Y row pairing only; Y's column Gram preserved exactly | 0.9241 | 0.7572 | 0.4220 |
| CTRL-RANDX — X matched-norm Gaussian | the sieve geometry of X | 0.9091 | 0.7713 | 0.4766 |
| CTRL-IIDSHORT — Y iid resample of its own entries | all structure in Y | 0.9081 | 0.7627 | 0.4711 |
| **CTRL-BOTHRAND — both** | **everything: no lattice, no sieve, no dual family, no modulus** | **0.9040** | **0.7861** | **0.4550** |

My closed form reproduces the producer's headline real/null ratios to under 1%
(0.881 / 0.785 / 0.453 against the reported 0.874 / 0.783 / 0.452), so this table
sits on the same footing as the report's.

| group | real/null | CTRL-BOTHRAND/null | real/CTRL-BOTHRAND | % of deficit forced |
|---|---|---|---|---|
| near-miss K=8 | 0.881 | 0.921 | 0.956 | **66%** |
| near-miss K=25 | 0.785 | 0.847 | 0.927 | **71%** |
| secret-distribution K=25 | 0.453 | 0.497 | 0.912 | **92%** |

**An object with no lattice at all reproduces 66–92% of the reported departure.**
The report's "roughly a factor 2 on the operationally relevant group"
(1/0.452 = 2.21) becomes **a factor 1.10** once compared against a matched-shape
object with no lattice structure.

Isotropy check, which explains why: the participation ratio of
`Σ = X^T diag(p)² X` is **34.853** for the real sieve X and **34.930** for a
matched-norm random X, out of m = 35. The sieve database is isotropic in this
metric to 0.2%. There is no special geometry here for the statistic to read.

### 2.4 The decay test, which the package passes

Per `docs/inventor-protocol.md` §3 the report must say what the quantity *should*
do as the parameter meant to destroy it increases. The producer does not run a
graded version on the real object. I did. Taking `c_k = s + λ·unit_k` and growing
λ from 1 to 63 (offsets going short → uniform), `K_eff_trail/(K−1)` rises
monotonically:

```
λ   1      2      4      8      16     32     63
    0.8646 0.8667 0.8750 0.9027 0.9540 0.9647 0.9919
```

It decays to nothing. That is the **anti**-artifact signature and the package
passes it — but note what the destroying parameter is. It is **offset length**,
not lattice membership. The decay test localises the cause to exactly the thing
that is not the object.

### 2.5 What I am not saying

A residual of **4–9%** survives every structural control, consistently signed,
and appears on two independent certified dual families. That is a real,
small, object-specific component. My finding is that the reported *magnitude* is
not the object's — not that there is nothing there.

The producer names the right next test itself (§5.1: S-orthogonalise the Y
columns and re-measure; the closed form makes it free) and says the question is
"NOT SETTLED BY THIS BATCH". That is honest. My controls settle most of it, in
the forced direction. This is `DEF-1`.

---

## 3. Pre-registration ordering

**It holds, with two accuracy defects.**

`PREREG` is a module-level constant in the hashed script and is dumped verbatim
into `results.json`. The log shows F-1 = 0.98258 with band [0.95, 0.995] and F-2
printed at t = 62.8 s; the first T1 research number appears at t = 69.7 s. The
SENS-GRADED instrument gate ran at 62.8 s, before the real arms, as the
pre-registration required, and passed all three declared thresholds (errors
0.0004–0.0071 ≤ 0.02; `K_eff_max` 24.21 → 3.70 monotone). Ten known-answer
controls ran at t = 0.1–9.0 s, before any research number, all PASS.

**DEV-2 is the strongest evidence available that this is genuine.** The producer's
own hand-computed band was missed (0.999924 vs [0.95, 0.995]), the diagnosis
given is right (a diagonal approximation to C and S), and the band is recorded as
**missed rather than restated**. A retro-fitted prediction does not miss.

Two defects:

- **`DEF-4`.** Pre-registration §3 claims the closed form "is computed and printed
  BEFORE the scoring block in the measure run; the log ordering is the evidence."
  The log refutes it: families scored at 69.7–99.3 s, closed-form pass at
  99.3–114.7 s. Mitigated — KAC-1 exercises the same code at 7.1 s, and the
  formula is inside the hashed frozen docstring, so the formula's
  pre-registration stands. Only the ordering claim fails.
- **`DEF-5`.** `PREREG.expectation_uniform` = "agreement with the law within
  sampling error (D1)". **All nine uniform cells returned D2.** That is a second
  missed pre-registered expectation, mechanically explained in §2.3 but never
  listed as a deviation, while DEV-2 is presented as the only one. AGENTS rule 8.

One thing I could not check (`PR-6`): only the post-run copy of `dependence.py` is
archived, and `vectors.json` carries no PREREG hash, so I cannot prove from the
snapshot that PREREG was not edited between the build run (08:24) and the measure
run (08:25:45). Structural limit of a single-file archive, not a producer
omission. A future contract could close it by writing the script hash into the
build-stage output.

---

## 4. DEV-3 — verified, and the count is wrong

**It did not quietly re-score.** I re-implemented the frozen five-branch rule from
pre-registration §5 and replayed it on the archived z-scores for **all 33 scored
cells** (21 in T1, 12 in T2). **Zero mismatches.** The labels in `results.json`
are exactly what the producer's own frozen rule emits from its own archived z's.

**Everything downstream is labelled post hoc correctly.** `derived_post_hoc`
carries status `POST HOC`, names precisely what was pre-registered (the null arm
and the intent to compare) and what was not (the ratio statistic, its numerical
reading, and any threshold), states its provenance as a pure recomputation adding
no measurement, and preserves the frozen rule's verdicts separately and
unchanged in `T1.verdicts`.

**But the count is wrong (`DEF-3`).** "D2 on all 18 cells including all six NULL
cells" appears in `report.md` §2.7 and §4, in `results.json`
`derived_post_hoc.why`, in the snapshot commit message, and in the permanent
knowledge entry. The real figure is **21 T1 cells of which 7 are null, plus all
12 T2 cells — 33 of 33**. Eighteen is the number *displayed* in the log
(`SHOW_GROUPS` has 6 entries), not the number scored. The error understates the
producer's own self-reported failure, so it is not self-serving — but it is now
in an immutable knowledge entry, which is exactly the hazard that entry itself
warns about.

---

## 5. The rest of the card

**T0 — reproduced exactly.** My independent run: SIEVE 1.2919 (z 13.7),
RANDDIR_INDEP 1.0221 (z 1.0), RANDDIR_COUPLED **12.9603** (z 1420.6). Band
[10.3281, 13.9733], +6.7% off 12.1507, frozen rule emits T0-CONFIRMS. Norms match
the sieve row for row — exact by construction, since surrogate rows are unit
directions rescaled to the sieve row's own norm. The producer's caveat stands and
I repeat it: that arm is real-valued, has no mod-q wrapping, lies in no lattice
and carries no membership certificate.

**T2 — reproduced, and the limitation is wrong.** Stage B tuple served unchanged;
N = 4253 matching the batch-3 archive; sieve dim 50. Correction terms 3731.89 /
38.6833 / 3.72828 → the reported 3732 / 38.68 / 3.728, correctly labelled
MODELED and not combined with anything measured. Adjacent-bin `offdiag(R_raw)`
+0.0063 / +0.0001 / −0.0059, i.e. ≈0.006 not 0.9999, and the structural reason
given is correct — an adjacent bin differs by a *full* bin 2π/p, so no rank-one
common mode forms. This is a real and previously unstated advantage of the
principled design over the ad-hoc `s + unit_k` family.

The p=2 matched-K extra departure is 3.95% ≈ the reported 4.0%. But **`DEF-6`**:
LIM-T2 says p=3 and p=5 have no matched-K comparator. They do — the run scored
`adjacent_bins_10` at K=10 alongside `uniform_bins_10` at K=10 for *every* p, and
both are in `results.json`. The three available comparisons are:

```
p=2  −3.95%     p=3  −1.98%     p=5  +2.41%   (adjacent HIGHER — no departure)
```

The omitted two weaken the T2 reading rather than strengthen it, so this is
bookkeeping and not advocacy. It is still reporting one of three available
matched-K comparisons without saying so — the failure obligation 3 was rewritten
to stop.

**The three pre-measurement design fixes — changelog supports the ordering.** v1
is recorded as never run against a research object (no build stage, no sieve
call, no research number, synthetic checks only); v2 records the
`offdiag(R_ctr) = −1/(K−1)` mode-1 defect with a CAL-PERM spread of 0.0000; v3
records the asymptotic-reference defect that "manufactured a ~4σ departure out of
genuinely iid data" and the `var_cv`/CAL-PERM invariance. The corresponding fixes
are present in the archived code, and I verified the key algebra myself: for
`R = (1−ρ)I + ρ11^T` the trailing eigenvalues are all `1−ρ`, so `K_eff_trail =
K−1` *exactly* for every ρ — ST-6 really is invariant to the forced common mode,
as designed. Corroborated by code and by `receipt.json`'s
`instrument_debugging_not_measurement` block; not independently timestamped.

**`DEF-2`, which I found and the producer did not.** The ST-5c "ratio to
CAL-PERM" headline is not comparable across families. CAL-PERM's
`K_eff_max_ctr` mean varies 9.55–13.30 at K=8, **27.41–62.68 at K=25**, and
67.50–249.45 at K=64 — up to a factor 3.7 at fixed K — because centring by the
across-candidate mean interacts with marginal heterogeneity, which `var_cv` shows
differs by 400× across arms. For the headline cell the *numerators* are 13.306
(sieve) and 13.532 (sums): **the sums family's raw statistic is higher, i.e.
slightly less departed.** The whole 2× difference is the denominator. On the
nominal-K scale the two families are 0.532 and 0.541 — indistinguishable. So
"0.44× nominal for the sieve, 0.22× for a second certified dual family" (the
gloss in the snapshot message and in my own task card) is wrong twice: these are
ratios to CAL-PERM, not to K, and they do not order the two families.

ST-6, the *declared primary* observable, is free of this — CAL-PERM 6.990±0.003
at K=8, 23.87±0.01 at K=25, 453.4 at K=512 across every arm. That is a point in
the producer's favour: it picked the robust statistic as primary.

**DEV-1 — confirmed.** `KN-TECH-14efa5` records `‖b0‖ 160.4 → 130.3` and
`db 4075` with **no basis seed and no construction**, so those two numbers are
not reproducible from the entry. The rebuild transcript is genuine and detailed:
fresh venv, both documented fixes required and applied (`--no-build-isolation`,
self-provided `libgmp.so` symlink), three pre-existing venvs recorded and not
used, version drift to passagemath 10.8.8 disclosed. The producer's own numbers
(189.5 → 125.7; db 4166) confirm the tools function and it does not claim
otherwise.

**`DEF-7`.** The 2.2e-05 `mean‖x‖²` gap: the producer's conclusion (same
database) is right, its stated reason ("a different archived row set") is an
inference where the archive supplies a check. Batch 4's own `results.json`
records `sieve_mean_xnorm2 = 181.4942798147218` — exactly what the archived X
gives and exactly what I compute — while carrying the same hard-coded literal
`rep0_mean_xnorm2 = 181.49430213739606`. The literal is stale and internally
inconsistent with `rep0_a_x`, which *is* consistent with the true value at
0.0e+00. Mis-transcribed constant carried forward, not a different row set.

**`DEF-8`.** `SCRIPT_VERSION = "dependence.py v1 …"` is stamped into
`results.json`, `vectors.json` and all 88 log lines, while the changelog says v1
was never run and v3 is the version run. The archived code is v3 by content.
Cosmetic, but it is the string a future reader will cite.

---

## 6. T3 — `KN-TECH-6c0e15`, read as a stranger

**Are the obligations criteria I can check compliance against, or advice?
Criteria, for four of five — and the fifth ships a mechanical proxy that works.**

The operative artifact is the YAML checklist, and it is what separates this entry
from its predecessor. Fields I can check with no judgement call:

- `comparator_spread_nonzero` — one number; zero means mode 1. Binary.
- `forced_value_number` — demands an actual number *before the run*, checkable
  against the archived artifact.
- `sensitivity_comparator` / `_threshold` / `_dynamic_range` — a name, a number
  declared before the run, both ends exhibited. This is obligation 3 converted
  from advice to a criterion, which is **exactly where batch 4's version failed**
  (`VAL-20260804-a84239` DEF-7, `EV-MLKEM-ba6c25` INT-3), and the entry names
  that failure rather than quietly fixing it.
- `reference_is_finite_sample` — encodes the 4σ artifact this producer
  manufactured out of iid data and then caught.
- `verdict_on_the_null_arm` — "RUN IT FIRST. Same label as the real arm ⇒ mode
  4." One comparison, binary outcome.

The soft field is `exhaustive_over_MECHANISMS`, which cannot be made fully
checkable in principle — you cannot enumerate all mechanisms. The entry knows
this and supplies `verdict_on_the_null_arm` as the operational substitute. That
is the difference between advice and a criterion, and this entry lands on the
right side of it.

**Does mode 4 and the null-first check actually encode the DEV-3 failure? Yes,
accurately, including the correct diagnosis.** Mode 4 case B is this batch's own
failure written up against itself: a five-branch rule with a correct written
partition proof that emitted one label on every cell including its own null,
caused by an underived forced value — the m-dimensional error — with the null
reproducing it to 0.8%. The sharpened obligation 5 ("exhaustiveness is relative
to the alternatives the rule can DISTINGUISH, not to the values the statistic can
TAKE") is the right generalisation and I could not improve on it. The null-first
check would have caught DEV-3 in one line, and the entry says so.

Mechanics all check out: `supersedes` / `superseded_by` correct, `KN-TECH-9d21c4`
untouched at 0 diff lines, all ten `source_refs` resolve, self-citing ref removed,
`confidence` downgraded to `single_run_experiment` with an unusually candid
justification, and the c4(8) corrections are arithmetically right
(0.965030/0.140324 = 6.877×, 0.965030/0.106552 = 9.057×).

Two things are wrong:

- **`DEF-3`** — the 18/six cell count is inherited into a permanent entry.
- **`DEF-9`** — mode 4 confines the m-dimensional forcing to `K > m`. My controls
  show it operates at K=8 and K=25 too, below m, via channel composition. The
  narrowness of that scope is precisely what let this batch treat matched K as
  clean.

**The thing worth saying loudest.** The entry's obligation-4 move 2 — *"build the
null object with the mechanism deleted; strip everything you believe is doing the
work and check the effect survives … that is a constructive refutation and it is
far stronger than a statistical one"* — is exactly the control T1's headline
lacks, and exactly the control I ran in §2.3. **The entry is checkable enough
that I used it to convict the batch that wrote it.** That is the strongest thing
I can say about a methodology entry, and I say it as a criticism of the batch, not
of the entry.

---

## 7. What I want on the record in the producer's favour

Both batch-4 defects are fixed and I verified both from the snapshot alone. DEV-3
is handled correctly at every step — verbatim verdicts, no re-scoring across 33
replayed cells, post-hoc labelling that names what was and was not
pre-registered. DEV-2 is a self-reported miss of the producer's own band, recorded
as missed rather than restated. Three instrument defects were caught by synthetic
checks before any measurement, one of which would have manufactured a 4σ result
out of iid data. And the K=512 column — which would have been the largest number
in the batch — is disclosed as reading nothing rather than reported as a finding.

The defects I raise are about **what the contrast is of**, not about whether the
numbers are right. The numbers are right; I reproduced essentially all of them to
the last archived digit.

---

## 8. Limits of this validation

- I did not rebuild the lattice instrument (no g6k/fpylll in my session; the
  producer's venv is ephemeral). The sieve itself I checked only through the
  archive anchors — N = 17919 exact, a_x delta 0.0e+00 from the archived X.
- I cannot prove from the snapshot that the script was not edited between the two
  runs (§3).
- My forcing controls are closed-form, not scored. The closed form reproduces the
  measured values to under 1% everywhere both exist, but it inherits LIM-3 (exact
  for Gaussian e; the run uses a rounded Gaussian).
- ONE toy instance, d = 60, q = 127. Ensemble over error draws on one fixed
  database. No replication across instances.
- Procedural independence only: my session resolves to `claude-opus-5`, the same
  model as the producer and every participant in batches 1–5. My implementations
  are independent; my priors are not. **Rule 12 remains UNMET and UNWAIVED.**
- I validated evidence integrity. I did not decide what any of it means for
  `MATZOV.Nf`, for the independence heuristic, or for any hypothesis. That is the
  Coordinator's call and the Red Team's to challenge.

## 9. Explicit non-claims

No ML-KEM break, no attack, no speedup, no security claim in either direction, no
FIPS 203 parameter set affected or cleared, no cost claim, no exponent moved. The
independence assumption (I-b) is neither validated nor refuted by this package —
and `DEF-1` does not refute it either; it says the measurement is mostly about
something else. No lane closed or opened. No `EV-MLKEM-*` or `KN-*` status change
made or proposed. No solve certificate: the membership certificates certify
vectors only.
