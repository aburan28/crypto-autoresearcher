# TASK-20260802-de2957 — Contradiction review: counting-resolution confound vs EV-MLKEM-011 / EV-MLKEM-013

- Report id: `REV-20260802-f17ef8` · Goal `GOAL-MLKEM-003` · Batch `BATCH-008`
- Role: reviewer · independent session · did not originate either record under review
- Repo `HEAD` at read time: `7f8aca61` on `claude/ml-kem-research-harness-76xefq`
- I edited no ledger record, no knowledge entry, no prior-batch artifact, nothing
  under `experiments/`, and made no commit. Every write is inside
  `coordination/goals/GOAL-MLKEM-003/batches/BATCH-008/tasks/TASK-20260802-de2957/`.
- **Verdicts: EV-MLKEM-011 `claim_survives_narrowed`; EV-MLKEM-013 `claim_void`.**

Nothing in this document is a claim about the security of ML-KEM or Kyber in either
direction, and nothing in it is an ML-KEM break claim. All data analysed is
toy-parameter (q=241, m=40, n=43 and n=50). AGENTS rule 7 applies without exception.

---

## 0. This is NOT a rule-12 pass. Read this before reading anything else.

AGENTS.md rule 12 requires that a **contradiction between independently validated
evidence records** receive an independent `review-breakthrough` pass at `max` effort,
and `orchestration/model-policies.yaml` (line 147ff) marks that policy
`degradable: false` with `fallback_policy: null` — the one policy that may never be
degraded, precisely so that a backend which cannot reach the top tier refuses the
task instead of signing off.

That policy cannot be served in this session. I ran the probe myself:

```
$ python3 -m orchestration.adapter doctor --probe
OK    configuration loaded (sha256:7256ac98a74b28fda56cd89815cf70c8)
WARN  anthropic: $ANTHROPIC_API_KEY unset (backend unusable)
WARN  fireworks: $FIREWORKS_API_KEY unset (backend unusable)
WARN  fireworks-anthropic: $FIREWORKS_API_KEY unset (backend unusable)
OK    local: no credentials required
WARN  local: model probe failed: network error listing models at
      http://localhost:8000/v1/models: [Errno 111] Connection refused
WARN  openai: $OPENAI_API_KEY unset (backend unusable)
WARN  openrouter: $OPENROUTER_API_KEY unset (backend unusable)
WARN  zai: $ZAI_API_KEY unset (backend unusable)
WARN  zai-anthropic: $ZAI_API_KEY unset (backend unusable)
```

The substantive review below therefore runs under `review-adversarial` at `xhigh` in an
independent session — an **explicitly-labelled substitute**. Requested policy
`review-adversarial`; resolved model `claude-opus-5`; `fallback_used: true`;
`model_verified: false`; `degraded_allowed: false`.

**Consequence, stated plainly: this document may not change the official status of
EV-MLKEM-011 or EV-MLKEM-013, and may not promote, retire, or supersede any knowledge
entry.** It is an input to a Coordinator decision. (Note also that
`review-breakthrough` itself carries `may_change_official_state: false` even when it
*is* served — it informs a decision, it does not perform a transition.)

---

## 1. What I did, and what I refused to take on trust

The brief was explicit that BATCH-007's arithmetic must not be assumed. I recomputed
everything from the archived bytes. Two things I want on the record about method:

- **numpy is not installed in this session.** Where the archived code calls
  `numpy.fft.fftn`, I evaluated its *documented definition*
  `A[k] = Σ_n a[n]·exp(−2πi·k·n/q)` per axis directly in pure Python, and self-checked
  that implementation against the closed form for a single-delta table (exact). The
  identity in §4 is also derivable by hand from the source text; the two agree.
- **One row of BATCH-007's O2 table is not checkable here.** The third archived Pwrong
  file (`…beta037_beta144_N200001.out`, `nb_iteration=1`) is *not in this repository* —
  only its header extract and its sha256 (manifest line 153). I verified the floor
  arithmetic `−log2(1·241³) = −23.738668`, which reproduces O2's `−23.7387`. I could
  **not** verify the "recorded `−23.74`" it is compared against. O2 presents three rows
  as if all three were checked against archived data; one was not. Rows 1 and 2 I
  verified exactly.

A task-card defect worth recording: the handoff's inputs name "experiments/EXP-MLKEM-013
archived Pwrong/Pgood .out files", and `read_scope` omits `experiments/EXP-MLKEM-011`.
The `.out` files exist only under `experiments/EXP-MLKEM-011/vendor-lock/data/`. I read
them (and the vendored `inputs/MLKEM-DUAL-SOURCES-20260802/` extracts) read-only,
because recomputation from those bytes is the task's binding constraint.

---

## 2. The objection is correct, and it is exact

Every number BATCH-007 asserts about the two archived files reproduces bit-for-bit.

**Main file** (`Pwrong_…n43…N25971.out`, sha256 `50bd293c…f90bb`, 45 569 bytes, 1804
data lines). Header: `q=241`, `k_fft=3`, `nb_iteration=4000`, `avg_N=25971`, and the
comment "Line i (starting from i=0) correspond to P(F >= i) … when the target b is
uniform".

| quantity | recomputed |
|---|---|
| `q^k_fft` | 13 997 521 |
| `nb_iteration · q^k_fft` | 55 990 084 000 = 2^35.704452 |
| quantum `1/(nb·q^k)` | `1.786030540693598580e-11` |
| last positive index `T` | 1802 |
| last positive value, as printed in the file | `1.786030540693598580e-11` |
| first zero index | 1803 |
| `log2` of the last positive value | −35.704452 |
| exact IEEE-754 equality `lastvalue == 1.0/total` | **True**, difference 0.0 |
| every one of the 1804 values an integer multiple of the quantum | **yes**, max relative deviation 1.360e−16 |
| count at `T=0` | 27 939 211 089, i.e. `P(F ≥ 0) = 0.499003` |

**Second file** (`…n50…N25970.out`, `nb_iteration=6000`): `nb·q^k = 83 985 126 000 =
2^36.289415`; last positive `T = 2309`, value `1.190687027129065666e-11`, exactly the
quantum; all 2311 values integer multiples (max rel. dev. 1.815e−16); `P(F ≥ 0) =
0.498251`.

**One correction to the objection's framing.** O2 makes its case on the *coincidence*
— "the recorded floor equals the resolution limit to four decimal places". That
coincidence is close to automatic: for **any** counting survival estimator the smallest
positive reported value is necessarily an integer multiple of `1/(total count)`, and
being exactly 1× is the generic case whenever the top unit-width bin holds one sample.
The genuinely load-bearing fact is the stronger one I checked: *every* value in *both*
files is an exact integer multiple of the quantum. That is what establishes these are
unsmoothed pooled counts whose support endpoint is budget-determined **by construction**
— which is a structural fact about the instrument, not a suspicious numerical
coincidence.

So: the endpoint `T = 1802` is the instrument's floor, `fraction_inside = 0` measures
the instrument, and any sentence that reads it as a property of the score distribution
is over-reaching. **That much of RT-20260802-3a440d objection 2 is upheld**, as is
TASK-20260802-103's defect D5, which found the same identity independently and read it
correctly ("this strengthens Q3's answer rather than weakening it — it explains WHY no
measurement exists at the threshold").

---

## 3. The instrument's silence is a bound, not a zero

This is the third possibility the brief asked me to hold open, and it is the right
frame for both records.

The run scored `2^35.7045` candidates and observed **zero** exceedances at scores
≥ 1803. Under full independence that is a 95% upper bound `Pwrong(1803) ≤ 3/2^35.7045
= 2^−34.12`. But the `q^k_fft = 13 997 521` candidates inside one FFT share the same
`N` dual vectors and the same target, so they are **not** independent: the pooled point
estimate stays unbiased, but the confidence interval inflates, and the archive carries
no per-iteration breakdown from which the effective replicate count could be recovered.
Under maximal within-iteration clustering the same zero-count only gives `p ≤ 3/4000 =
2^−10.38`. The far-tail count structure (counts run 1, 2, 3, 4, 5, 6 … rather than
jumping in units of `q^k_fft`) argues against extreme clustering, so the true resolution
is probably near the nominal figure — but **2^−35.7045 is a lower bound on the
instrument's resolution limit, not a demonstrated value.** Neither record, nor the
objection, states this.

So the honest content of the measurement is: *this run cannot see Pwrong below
2^−35.70, and it saw nothing above score 1802.* That is a bound. It is not a zero, and
AGENTS rule 5 — extended from infrastructure failures to statistical ones by
`docs/inventor-protocol.md` §3 — forbids reading it as one.

**But the converse also holds, and the brief was right to insist on it.** The bound
does not show the separation is absent either. Which raises the discriminating question.

---

## 4. Does anything in the data discriminate "no mass there" from "not enough samples"?

Yes, and it points at *not enough samples*. Two independent tells, both from the
archived bytes.

**(a) The measured log-survival flattens; it does not steepen.** Local slope of
`log2 P(F ≥ T)`, in bits per score unit:

| window | slope | counts at the ends |
|---|---:|---|
| [200, 400] | −0.036231 | 2 242 684 492 → 14 771 445 |
| [400, 600] | −0.045543 | 14 771 445 → 26 759 |
| [600, 800] | −0.019878 | 26 759 → 1 701 |
| [800, 1000] | −0.013277 | 1 701 → 270 |
| [1000, 1200] | −0.010054 | 270 → 67 |
| [1200, 1400] | −0.011294 | 67 → 14 |
| [1400, 1600] | −0.006112 | 14 → 6 |
| [1600, 1802] | −0.012797 | 6 → 1 |

A distribution approaching a genuine right endpoint *accelerates* its decay. This one
decelerates: the slope magnitude falls from 0.0455 to roughly 0.010 and then wanders in
the Poisson-noise regime (counts ≤ 10 from `T = 1490` onward; count exactly 1 for the
last 62 values of `T`, from 1741 to 1802). There is no edge in the data.

**(b) At the floor, the measured tail is ~150 bits above the model's Gaussian
component.** The paper's own Model 4.7 (page 23 extract) writes the wrong-guess score as
`D + N(0, N/2)`. I recovered the second moment from the archived survival column via the
exact integer-grid identity `E[F²] = 2·Σ_{t≥1}(2t−1)·P(F ≥ t)` (symmetry supported by
the files: `P(F ≥ 0) = 0.499003` and `0.498251`), giving sd = 113.7914. At `T = 1802`
that is `z = 15.8360`, where a pure Gaussian has `log2` survival −186.2151. The measured
value is −35.704452 — an excess of **150.51 bits**. The whole tail at the floor is
carried by `D`, and Model 4.7 does not truncate `D` anywhere near 1802.

**Conclusion.** The archived data affirmatively favours "there is wrong-guess mass
beyond 1802 that this instrument cannot count" over "there is no mass there". The
non-coverage is a property of the run, not of the distributions. That is the finding
the two records should have carried and did not.

---

## 5. The bigger surprise: EV-MLKEM-013's k_fft alignment is itself wrong

I was asked to recompute rather than trust, and this is where it paid.

EV-MLKEM-013 / KN-FIND-014 / RUN-MLKEM-013-001 all assert that Carrier's `verifyModel`
uses **inconsistent normalization**: `Pwrong` on an `FFT/k_fft` scale, `Pgood` on a raw
cosine-sum scale, factor exactly `k_fft = 3` — and therefore that `Pgood` must be
divided by 3, turning EV-MLKEM-011's raw T-gap of ~4866 into the "aligned" ~421 that
BATCH-007, D5 and the red team all subsequently quote.

Read the archived `FFT_sample.py` (sha256 `2a5f3ded…22531`, manifest line 142) in full,
not two lines of it:

```python
	def init(self,target):
		self.T = numpy.zeros(tuple([self.q for i in range(self.k_fft)]),dtype=numpy.complex128)
		for (decoded, dual_vector) in self.decoded_dual_vectors:
			for i in range(len(decoded)):                      # <-- loop variable unused
				self.T[tuple(decoded)] += math.e**((2j*math.pi/self.q) * dot_product(dual_vector,target,self.q))
	def FFT(self):
		self.T_FFT = numpy.fft.fftn(self.T).real/self.k_fft
```

`self.T` has shape `(q,)*k_fft` and `self.T[tuple(decoded)]` is used as a *scalar*
accumulator, which forces `len(decoded) == k_fft`. So the inner loop — whose index `i`
is never used — adds each dual-vector phase **`k_fft` times**. The table carries a
factor `k_fft`, and `FFT()`'s `/self.k_fft` cancels it exactly.

Recomputed against the archived file, `FFT_sample.FFT()` reproduces
`Score_Function.compute_score()` with factor **1**, not `k_fft`:

| q | k_fft | m | #dual vectors | max abs \|FFT − raw\| | FFT/raw range |
|---:|---:|---:|---:|---:|---|
| 7 | 3 | 5 | 20 | 3.963e−14 | [1.000000000000, 1.000000000000] |
| 7 | 3 | 5 | 60 | 4.563e−14 | [1.000000000000, 1.000000000002] |
| 11 | 2 | 4 | 40 | 4.918e−14 | [1.000000000000, 1.000000000001] |
| 5 | 4 | 6 | 30 | 1.688e−14 | [1.000000000000, 1.000000000000] |
| 13 | 3 | 7 | 50 | 1.061e−13 | [0.999999999985, 1.000000000004] |

And the counterfactual pins the mechanism — remove the duplicated loop and the ratio
becomes exactly `1/k_fft`: 0.333333333333 at `k_fft=3`, 0.500000000000 at `k_fft=2`,
0.250000000000 at `k_fft=4`.

The `synthetic_check` string archived in `RUN-MLKEM-013-001/results.json` reads *"raw
cosine sum == fftn.real (no /k_fft); FFT/k_fft == raw/k_fft exactly"*. That is exactly
what one gets by building the table **without** `init()`. The recorded check did not
exercise the code path it certified, and — see §7 — neither the command nor the script
was archived, so nobody could have noticed by inspection.

### Two independent corroborations, from the data rather than the code

**The variance test is decisive and code-agnostic.** Under Model 4.7,
`Var(F_wrong) ≈ avg_N/2` on the raw scale, or `avg_N/(2·k_fft²)` on a `/k_fft` scale.

| file | empirical sd | `sqrt(avg_N/2)` | ratio | `sqrt(avg_N/2)/k_fft` | ratio |
|---|---:|---:|---:|---:|---:|
| `…n43…N25971` | 113.7914 | 113.9539 | 0.998574 | 37.9846 | **2.995722** |
| `…n50…N25970` | 113.9783 | 113.9517 | 1.000233 | 37.9839 | **3.000698** |

Two independent files, both on the raw scale to within 0.15%, and both off the
"aligned" scale by exactly a factor of 3. This holds whatever script wrote the files.

**Approximation 4.8 corroborates on the Pgood side** (weaker — flagged). Evaluating the
paper's threshold formula (4.19) with the Fig 4.1 caption parameters, the *raw* Pgood
median is reproduced at `α = 2.0125`; `α = 2` gives `T = 12021.89` against the measured
11964.47 (0.48%). The `/k_fft`-aligned median would need `α = 4.88`. I scanned `α`
rather than assuming it, because the archived extract does not state it — so this is
corroborative only, not load-bearing.

### Why this matters for the objection

The alignment error is not a rounding detail; it changes how damaging the confound is by
about two orders of magnitude in the exponent. Under the (void) aligned scale the
operating threshold sits ~4 bits of survival probability below the instrument floor — a
marginal, plausibly fixable budget shortfall, which is what makes the red team's "the
gap is set by the authors' sample budget… Ducas–Pulles is the existence proof that the
control is runnable" read as devastating. On the correct raw scale the picture inverts.

---

## 6. On the corrected scale: how far is the operating threshold, really?

The paper selects `T` so that `Pgood ≈ 1/2` (page 27 extract). So the operationally
relevant point is the Pgood **median**, not the minimum — a distinction neither record
draws. On the raw common scale:

- Pgood (n = 4000): min 6667.673616, median 11964.473718, max 17822.813537, mean
  11983.505048, sd 1720.0862. (EV-MLKEM-011's "≈6668 / 11964 / 17823" reproduces exactly.)
- fraction of Pgood at score ≤ 1802: **0/4000**.
- gap to the Pgood minimum: **4865.673616** score units.
- gap to the operating threshold (Pgood median): **10162.473718** score units.

Extrapolating the file's own measured tail slope — *a diagnostic under a stated
functional assumption, not a measurement, and no verdict below rests on it as evidence
for a distributional claim*:

| fit window | slope (bits/unit) | log2 Pwrong at Pgood min (6667.67) | at operating T (11964.47) | `nb_iteration` needed to reach operating T by counting |
|---|---:|---:|---:|---:|
| [1000, 1600] | −0.009153 | −80.2 | −128.7 | 2^105.0 |
| [1200, 1740] | −0.009382 | −81.4 | −131.0 | 2^107.3 |
| [800, 1400] | −0.011541 | −91.9 | −153.0 | 2^129.3 |

So the operating threshold sits roughly **93 to 117 bits of survival probability below
the instrument's floor**, and closing that by counting would need on the order of 2^105
to 2^129 iterations against the 4000 actually run.

**This is the single most important consequence of the review, and it corrects the
objection as well as the records.** The gap is *not* a marginal budget shortfall that a
longer run would erase. At the Fig 4.1 parameters **a counting estimator can never reach
the operating threshold**. The objection's diagnosis (confounded with run length) is
right; its implied remedy (run longer, as Ducas–Pulles did) is wrong by ~90–120 bits.
Any successor task that plans "just increase `nb_iteration`" is planning an impossible
run.

---

## 7. Archival defects found along the way (validator-grade)

- **A1, high.** `experiments/EXP-MLKEM-013/runs/RUN-MLKEM-013-001/`: `command.txt` reads
  `[command-not-captured-at-execution]`, `manifest.yaml` repeats that string in
  `code.command`, `stdout.log` contains only `# No live stdout captured`, and
  `stderr.log` is empty. The synthetic check that produced `scale_factor_k_fft = 3`
  cannot be re-executed or inspected from the archive; only its one-line conclusion
  survives. This violates the AGENTS.md artifact policy (exact command, stdout, stderr)
  and is the proximate reason the error stood for two batches.
- **A2, medium.** `EXP-MLKEM-013/specification.yaml` names
  `verifyModel/ScoreExperimentalDistribution/Algorithm.py` in `source_refs.files`, but
  it is not in `required_artifacts` and is not archived anywhere in the repository. It
  is the file that would answer "which code path wrote the `.out` files".
- **A3, medium.** The third archived Pwrong file is not in the repository at all (§1).
- **A4, low.** The BATCH-008 task card's `read_scope` / inputs point at the wrong
  experiment directory for the `.out` files (§1).
- **A5.** `EXP-MLKEM-013`'s frozen falsification criterion — "Synthetic check shows
  Pwrong FFT/k_fft is **not** a constant multiple of the Pgood cosine sum" — could not
  catch this failure. It *is* a constant multiple. The multiple is 1. A successor
  experiment must test the composite `init()` + `FFT()` path against `compute_score()`,
  not the two method bodies in isolation.

---

## 8. The two verdicts, with the steelman stated first

### EV-MLKEM-011 → `claim_survives_narrowed`

**Strongest case for it surviving intact.** Every number it states recomputes exactly
(§2, §6). Its fourth observation and the second clause of its inference — the Kyber CC
Table C.2 figures lying ~84 bits below the toy floor — is a *dynamic-range* statement,
and the counting-resolution finding does not weaken it; it explains it and makes it
sharper. From the archived extract `page37_tables_C1_C2.txt`, CC gives −119.57 / −177.79
/ −244.03, i.e. **83.8655 / 142.0855 / 208.3255 bits** below the toy instrument floor
of −35.704452 (EV-MLKEM-011's "≈84" and `pwrong_scope_gap.json`'s
−83.86554770664802 both reproduce). And the amendment that had made the confound look
nearly decisive — EV-MLKEM-013's aligned ~421 gap — is itself void, so the record's own
raw figures stand. It already carries `strength: preliminary`, `claim_tier: medium`,
`status: accepted_with_qualifications`, and boundaries naming the archived-data-only
scope. It never claimed a Kyber break.

**Why it nonetheless does not survive intact.** Observation 1 is written in the grammar
of a measured distribution endpoint; it is the instrument's floor. Observation 2's
"fraction of Pgood scores with T ≤ 1802 is exactly 0" and the inference's "does not
intersect the Pgood≈1/2 operating threshold" then read as a distributional separation
that the instrument could not have detected. Under `docs/inventor-protocol.md` §3 that
is the artifact tell — the parameter meant to move the reported quantity
(`nb_iteration`) was never varied and no matched-budget control exists in the archive.
Observation 3 quotes the gap against the Pgood *minimum* when the operating point is the
*median*. And the `scale_note` field defers T statistics to EV-MLKEM-013, which is void.

**Non-confounded restatement (verbatim in `contradiction_review.yaml`).** In short: the
run is a pooled counting estimate over `2^35.7045` scored candidates whose every value
is an exact integer multiple of `2^−35.7045`; its zeros above score 1802 are an upper
bound (`≤ 2^−34.12` under independence the design does not satisfy, `≤ 2^−10.38` under
maximal clustering), not a measurement of zero; on the raw common scale the `Pgood ≈ 1/2`
threshold lies 10162.47 score units above the highest resolvable score. **Fig 4.1
validates Approximation 4.9 only over the band `Pwrong ∈ [2^−35.70, 2^−1]`, while the
Kyber cost table applies it 83.87 / 142.09 / 208.33 bits below that band — and no
counting experiment at those parameters could have extended the band to the operating
threshold.** That is a statement about the reach of the experimental validation. It is
not a distributional separation, not a claim that Approximation 4.9 is wrong, and not a
claim about ML-KEM security.

### EV-MLKEM-013 → `claim_void`

**Strongest case for it surviving.** Its function was a units audit that *corrected* a
prior record — the program catching its own error, which is the behaviour the contract
wants, and rejecting it deserves at least the skepticism that accepting it did. Its two
quoted code facts are literally true of the two method bodies read in isolation. Its
derived arithmetic is exact given its premise (6667.673616/3 = 2222.557872;
11964.473718/3 = 3988.157906; 17822.813537/3 = 5940.937846; 2222.557872 − 1802 =
420.557872 — all four reproduce). And `Algorithm.py` was not archived, so one can argue
the audit worked from what it had.

**Why it is void anyway.** Its load-bearing claim is falsified by recomputation from the
exact artifact it cites: `scale_factor_k_fft` is **1**, not 3 (§5), because `init()`'s
duplicated accumulation loop supplies the compensating factor that the two quoted lines
omit. That is corroborated independently of any code by the archived data's own variance
in two separate files (ratios 2.9957 and 3.0007 against the aligned prediction), and
further by Approximation 4.8 on the Pgood side. All three of its observations therefore
fail: there is no normalization asymmetry; the aligned statistics are an incorrect unit
conversion; and EV-MLKEM-011 did not "overstate the T-gap by factor 3" — its raw figures
were already on the correct common scale. Separately, the counting-resolution confound
applies to this record's `fraction_inside = 0` and `T_gap ≈ 421` as well, and under its
own (incorrect) alignment would be close to decisive on its own. Nothing load-bearing
survives.

The record is `status: draft` and was never officially accepted, so nothing official
turns on this — and per §0 this review could not change its status in any case.

**Non-confounded restatement.** The archived `FFT_sample.py` at `9c1367f` is
self-consistent: `FFT()` reproduces `compute_score()` with ratio 1.000000000000 (max abs
deviation 1.1e−13 across five parameter settings), and only becomes `1/k_fft` if the
duplicated loop is removed. There is no `k_fft` asymmetry and no alignment is warranted;
the archived Pwrong files' empirical sds (113.7914, 113.9783) match `sqrt(avg_N/2) =
113.95` rather than `37.98`. The correct common-scale figures are the uncorrected ones.

---

## 9. Symmetry check on my own conclusion

Rejecting a standing record deserves the same skepticism as confirming one, so let me
try to break §5.

- *"The `.out` files may not have come from `FFT_sample.py` at all — `Algorithm.py` is
  not archived."* Granted, and I record it as a residual uncertainty. It does not rescue
  EV-MLKEM-013, for two reasons. First, the record's claim is *specifically* about
  `FFT_sample.py`'s normalization, and that file is archived and recomputes to factor 1.
  Second, the variance test (§5) is a property of the data, independent of which script
  wrote it, and it places both Pwrong files on the raw scale in two files at once.
- *"Maybe `len(decoded) ≠ k_fft`."* For `self.T[tuple(decoded)] += …` to be a scalar
  accumulation into a `(q,)*k_fft` array, `len(decoded)` must equal `k_fft`. Any other
  length makes the statement a broadcast into a slice, which would not produce a clean
  `1/k_fft` either and would make the pipeline incoherent.
- *"Maybe the cancellation is accidental and the authors meant `/k_fft`."* Possibly —
  the unused loop index does look like a copy-paste artifact. But intent is irrelevant
  to the audit: what the code *computes* is what wrote the data, and the data's variance
  agrees with what the code computes. If anything, the cancellation makes the authors'
  pipeline **correct**, which is the opposite of the "inconsistent normalization" finding.
- *"Am I over-correcting toward voiding a record?"* The test I applied is whether
  anything load-bearing survives. For EV-MLKEM-011 the answer is yes (the dynamic-range
  statement, and every number), so it is narrowed, not voided — even though its most
  quotable sentence is the confounded one. For EV-MLKEM-013 the answer is no. Applying
  the same test in both directions is what keeps this from being a fatigue verdict.

---

## 10. Closure standard: the lane is not dead, it is mis-instrumented

Per `docs/inventor-protocol.md` §4, a negative result needs a named obstruction and
forward guidance. A count of things that did not work is a fatigue report.

**Named obstruction.** At the Fig 4.1 parameters the experimental `Pwrong` is a counting
estimator with resolution `1/(nb_iteration·q^k_fft) = 2^−35.7045`, while the `Pgood ≈ 1/2`
threshold sits at score ≈ 11964 where the file's own measured tail slope puts `Pwrong` at
roughly `2^−129` to `2^−153`. The obstruction is a **~93–117 bit dynamic-range deficit**,
not an unattempted measurement, and no feasible increase in `nb_iteration` removes it.

**Forward guidance.**

- **F1 — cheap, no sampling, highest value, and never yet attempted by this program.**
  Implement Approximation 4.9's integral (equations 4.22–4.24, page 23/25 extracts) at
  both Fig 4.1 parameter sets and compare the *predicted* survival curve against the
  archived measurement pointwise over the band the instrument actually resolves —
  `[2^−35.70, 2^−1]` left panel, `[2^−36.29, 2^−1]` right. Report the signed discrepancy
  and, critically, **its trend in `T`**. The paper itself says the right panel "suggests
  our analysis may be slightly optimistic"; quantifying that is a real measurement the
  archive supports, and it converts a coverage complaint into a model test.
- **F2.** Feed F1's trend into the existing lever: KN-FIND-013 / EV-MLKEM-012 already
  quantify that only ≈9.46 / 14.36 / 14.76 bits of `Pwrong` miss erase the CC NIST
  shortfalls for Kyber-512/768/1024. A measured drift over the resolved band plus a
  stated extrapolation assumption yields a bounded sensitivity statement — not a
  security claim.
- **F3 — the missing control, cheap.** Re-run `verifyModel` at two or three values of
  `nb_iteration` with all other parameters fixed and confirm the support endpoint moves
  as `−log2(nb_iteration·q^k_fft)` predicts. This is the decay control §4 says is absent.
  Emit per-iteration exceedance counts at the same time, so the effective replicate count
  — and hence the instrument's true resolution — becomes recoverable (§3).
- **F4 — the only route to the operating threshold.** A counting estimator cannot reach
  `2^−129`. That needs a rare-event estimator: importance sampling / tilting of the
  dual-vector or decoding-distance distribution, or bucketed enumeration of the kind
  Ducas–Pulles use for the non-polar score. Whether such an estimator admits a defensible
  change of measure for the *polar-coded* score is genuinely open, and is the right
  successor question.
- **F5.** Archive `Algorithm.py` so that "which code path wrote these files" is
  answerable from repository bytes.

---

## 11. Recommendations for the knowledge corpus (recommend only — the Coordinator decides)

- **KN-FIND-012 — supersede with a restatement.** Its table is numerically correct and
  reproduces exactly. Restate the row "fraction of Pgood with T ≤ 1802 | 0" as a
  *resolution bound*; relabel "bits below toy floor ≈ 84" as "bits below the toy
  **instrument floor**" and carry 83.87 / 142.09 / 208.33; and replace "measures Pwrong
  only on a T-interval that does not meet the Pgood≈1/2 operating threshold" with
  "measures Pwrong only over the band its counting resolution permits,
  `Pwrong ∈ [2^−35.70, 2^−1]`; the operating threshold lies ~93–117 bits of survival
  probability below that band by the file's own measured tail slope". Add one non-claim:
  this is not evidence that Approximation 4.9 is wrong.
- **KN-FIND-014 — supersede as withdrawn on the merits.** Its title, both bullets under
  "What is established", and every row of its table rest on a `k_fft` asymmetry that
  recomputation from its own cited artifact falsifies. Its `erratum` tag is doubly wrong:
  the archived code is self-consistent. A new finding (fresh random-suffix id) should
  record the cancellation mechanism, that no alignment is warranted, and that
  EV-MLKEM-011's raw figures were already on the correct scale. This is the more serious
  of the two corrections, and it is arithmetic, not phrasing.
- **KN-OPEN-016 — amend via supersession, three changes.** (i) Restate the "Pwrong
  coverage gap" bullet as the dynamic-range bound. (ii) Replace the "Score-scale audit
  (KN-FIND-014 / EV-MLKEM-013)" bullet with the corrected finding that there is no
  `k_fft` asymmetry. (iii) Its stated residual — "measure Pwrong near the aligned
  operating threshold" — is not merely unattempted but **counting-infeasible by ~93–117
  bits**; replace it with F1–F4, naming F1 as the next action, and extend "What would
  close it" to acknowledge that direct measurement at the operating threshold requires a
  rare-event estimator or a proof, not a bigger run.
- **Also touched, for the Coordinator's attention:** EV-MLKEM-011's `scale_note`;
  `H-MLKEM-011` line 12 (the −119.57 framing is right, the surrounding coverage language
  inherits the confound); `H-MLKEM-013` / `EXP-MLKEM-013` / `RUN-MLKEM-013-001`; and any
  sentence in EV-MLKEM-017 / DEC-20260802-15cadd that quotes "aligned" score statistics
  or the 420.56 gap. I did not inspect the last of these in detail.

---

## 12. Limitations and non-claims

- Not a rule-12 `review-breakthrough` pass; changes no official status (§0).
- numpy unavailable; `numpy.fft.fftn` replaced by its documented definition, self-checked
  (§1).
- The third archived Pwrong file is not in the repository; BATCH-007's row for it is
  unverified (§1).
- `Algorithm.py` is not archived, so the producer of the `.out` files is not determinable
  from repository bytes. The variance test does not depend on this.
- §5's `α = 2` corroboration was obtained by scanning `α`, not by reading it from a
  source; corroborative only.
- §6's extrapolation is a diagnostic under a stated functional assumption. No verdict
  rests on it as evidence for a distributional claim; it is used only to size the
  instrument deficit and to reject the "just run longer" remedy.
- No G6K run, no new sampling, no network retrieval. Well inside the 2400 s / 4 GB / 1
  run budget.
- Nothing here is a claim about ML-KEM or Kyber security in either direction; nothing
  here is an ML-KEM break claim; nothing here shows Approximation 4.9 is wrong, nor that
  it is right; nothing here computes a corrected Kyber attack cost; no toy-scale result
  is presented as crypto-scale validation.
