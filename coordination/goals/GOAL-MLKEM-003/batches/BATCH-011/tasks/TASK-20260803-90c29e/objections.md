# TASK-20260803-90c29e — Red Team objections

**Reviewing:** Coordinator snapshot `eb7cdc1dac08fd2a8a0835c927879b61088ac20c`
(TASK-20260803-a7861e D7 source-reading package) and `ledger/evidence/EV-MLKEM-eac95b.yaml`
observation **O-2**.

**Verdict: `blocking_objections`** — blocking on the record's *stated reasoning and
scope*, not on its conclusion.

**Does the misspecification reading survive? YES, in narrowed form — and its stated
argument does not.**

**Toy tier.** `q=241, m=40, n=43/50`. No ML-KEM security claim in either direction.
AGENTS.md rule 12 UNMET and UNWAIVED; `EV-MLKEM-011`, `EV-MLKEM-013`, `EV-MLKEM-017`
keep their status. Nothing here was committed and no producer artifact was edited.

---

## 0. What I did independently

Everything below is deterministic and reads only bytes already in this repository.
**Zero new sampling, no network, no random numbers.** The vendored PDF was opened
read-only and its sha256 re-verified as `083b1422…b8005`.

- Re-executed the producer's extractor against the PDF and compared **every** numbered
  quotation block programmatically against my own extraction.
- Recomputed the counting statistics of both archived `Pwrong` `.out` files.
- Implemented the BATCH-009/010 survival model **independently** — Gauss-Legendre
  order 10 (producer used 6), my own panel layout, my own `v*` search — and ran the
  profiled-`K` exponent scan on four sub-bands per file.
- Evaluated `(4.11)`'s `Υ_n` series against its Gaussian surrogate.
- Tested `(4.19)` as an **unfitted** prediction against the archived `Pgood` file.

Cross-check that my implementation is the same object: at the archived exponent
`p=26.0` I get whole-band rms `0.70554` against the producer's `0.705494`
(5e-5 bits); at the argmin my coarser `v*` search gives `0.42914` against their
`0.425715`, inside their own declared ~0.002-bit `K` resolution.

---

# PART 1 — the D7 source reading

## RT-1 (minor, sustained). The self-check covers 14 of **17** blocks, and one of the three it misses is not verbatim.

§0 states *"All 14 line-numbered blocks below were checked back against the extracted
page text programmatically … 14/14 match"* and *"No character has been added, removed,
or reordered inside a quoted block."*

There are **seventeen** numbered blocks. The three the self-check does not reach are
the list-indented ones in §6 — PDF page 13 plain 33–36, page 24 plain 1–6, page 36
layout 10–15 — which use a different in-block prefix (`NN|text`, no space) and fall
outside the pattern the self-check matched.

I compared all seventeen. Sixteen are byte-exact. **One is not.** Page 24 plain line 6:

```
quoted:  follow a χ-distribution11 with degrees of freedomβsieve and nfft, respectively.
actual:  follow a χ-distribution11 with degrees of freedomβsieve and nfft, respectively. Therefore, we obtain
```

The trailing ` Therefore, we obtain` is silently dropped from a block declared
"verbatim". No consequence for D7 — the block supports the `α` identification and the
truncated clause is prose continuation — but it falsifies the package's own
no-character-removed statement, and the failure lands in exactly the set whose coverage
was asserted without being checked.

**Cheapest check:** parse every fenced block carrying `NN|` rows (handle both `NN| text`
and `NN|text` forms), re-extract the declared page with `pypdf` 6.14.2 in the declared
mode, apply the same C0 escaping, compare line by line. 17 blocks, 1 mismatch.

## RT-2 (minor, sustained). The page-13 quotation cannot have come from the declared command.

§0 declares exactly one command, `extract_pages.py --outdir <scratch>`, with no
`--pages`. Without `--pages` the script emits only
`PAGES_OF_INTEREST = {9, 20, 23, 24, 25, 26, 28, 36}` (`extract_pages.py` lines 49–60).
**PDF page 13 is not in that set**, yet §6 quotes "PDF page 13 / printed 12, Algorithm
3.1 input, plain lines 33–36 verbatim". I verified the quote *is* faithful to the PDF,
so this is a provenance gap, not a fabrication: a second invocation occurred and was
not declared.

**Cheapest check:** compare `extract_pages.py:49-60` against the §0 command row.

## RT-3 (MATERIAL, sustained-and-narrowing). The loci are right; the inconsistency is real as typeset; the framing overstates it, and O-7's use of it fails either way.

**What I verified.** Every locus is where the package says it is, byte-exact against my
own re-extraction: `(4.18)` at PDF p23 plain 22–43 / layout 11–18, `d_lsc` integral
outside the `max`, **no `min(1,·)`**; `(4.22)` at p23 plain 85–127 / layout 35–46, with
the `min` argument closing (`!`) before the Gaussian factor and `dd_lsc dt` outermost;
`(4.27)`–`(4.29)` and the closing display at p25. I independently reproduce the
document-wide scan: standalone `min` at exactly `(23,103)` and `(25,8)`; `Φ` on exactly
pages 20 (×2), 23 (×3), 24 (×1), 25 (×1). **The package's arithmetic of loci is
correct and I do not dispute it.**

**The reading the package did not weigh.** `(4.18)` is templated on `(4.17)`, whose
bracket is a **sum**. For a linear bracket, "integrate `d_lsc` out inside the
definition" and "let `d_lsc` be a mixing variable" agree in expectation, so writing
`∫ψ_lsc(d)·[…]dd` is a harmless and standard abuse for *the mixture induced by
`d ~ ψ_lsc`*. Carrying that same template to `(4.18)` with a `max` in the bracket
yields exactly `D | d_lsc = N·max_{i,j} Φ_d(i,j)` with `d_lsc ~ ψ_lsc` — which is
precisely what `(4.27)`, `(4.29)` and the closing display require. **Under that reading
there is no mathematical inconsistency at all, only a notational one.**

**The count that belongs on the record.** Five *operative* displays put the threshold
outside the `d_lsc` integral:

| locus | what it says |
|---|---|
| (4.22) | `dd_lsc dt` outermost, `min(1,·)` inside |
| (4.23) | `E(T−t)` defined via `Φ_{d_lsc}` — i.e. at a **fixed** `d_lsc` |
| (4.27) | `P(D > T \| d_lsc)` |
| (4.29) | `E(T)` defined via `Φ_{d_lsc}` — again at fixed `d_lsc` |
| closing display | `P(D>T) = ∫ψ_lsc(d)·P(D>T\|d) dd` |

**One** display, the definition `(4.18)`, reads the other way as typeset — and the paper
never uses it again. Note that `(4.23)` and `(4.29)` are *ill-formed* under the literal
`(4.18)` reading, because `d_lsc` would already be gone.

The package's §3(c) correctly declines to say which order the authors intended. But
§3(b)'s "This is a disagreement internal to the source" and the snapshot commit
message's "THE SOURCE DOES CONTRADICT ITSELF" assert more than the quotes carry. Any
downstream record that says the source contradicts itself **without stating 5-to-1, and
without stating that only one reading leaves (4.23) and (4.29) well-formed, misleads.**

**Consequence for O-7, which is the point of the exercise.** `EV-MLKEM-eac95b` O-7 says
the (4.18) reading *"changes the question: the collapse may be a defect of the SOURCE
rather than of the BATCH-009 implementation."* That does not survive:

- Under the **mixture** reading, `(4.18)` gives the BATCH-009 collapse **no textual
  support at all**.
- Under the **literal** reading, it supports the collapse only for a definition of `D`
  that the paper abandons in the next four displays.

O-7 must be narrowed to: *"(4.18) as typeset is inconsistent with the four displays
that follow it; on the operative chain the source is unanimous that `min(1,·)` sits
inside the `d_lsc` integral, so BATCH-009's collapse is not licensed by the source."*

**Cheapest check:** confirm the subscript `d_lsc` survives on `Φ` in **both** region
definitions — p23 plain line 125 (`+ : N · Φdlsc (x, y) ≥ T − t`, eq 4.23) and p25
layout line 18 (eq 4.29). If `d_lsc` is still free there, the operative chain is
conditional and `(4.18)` is the outlier.

## RT-4 (AN-1: accepted). The Coordinator's handoff premise was false.

Verified: `inputs/MLKEM-DUAL-SOURCES-20260802/extracts/carrier-hal-05406481/page23_approx_4_8_4_9.txt`
has sha256 `9afd68154e8210a828180f734b580b19533f482dc7e0e236056869e0cb3e15ed` and is
byte-identical to a fresh plain extraction of PDF page 23 made in this session; `(4.18)`
sits at its lines 30–41. Both BATCH-009 and BATCH-010 had it.

## RT-5 (AN-2: accepted, and it **understates** the correction).

Verified: `Φ_{d_lsc}` at `(4.10)` and `Υ_n` at `(4.11)`, PDF p20, byte-exact in both
modes; `α` at Definition 2.3, PDF p9, with numeric values in Table 5.1, PDF p28.
BATCH-010's "UNAVAILABLE" described the extract set, not the document.

But AN-2 stops one step short. It concludes that `α` *"for the two archived q=241 toy
runs is genuinely absent from the paper."* **`α` for those runs is identifiable from
the archive, to 0.5 %, by a check nobody ran** — see RT-10. BATCH-010's Check B ceiling
was self-imposed twice over.

Minor addendum: `α` also occurs twice on PDF page 8, which the package never read line
by line (its L-2 scopes only the *count* scans as document-wide). "Defined at Definition
2.3" is a page-9-onwards statement, not a uniqueness claim.

---

# PART 2 — attacking the 0.426-bit floor

## RT-6 (BLOCKING as to the argument). The 0.426 figure is compared against the wrong null, and the right null is closed-form.

O-2 reasons: the identifiability control reaches rms 0 on noiseless data; the best
achievable rms on real data is 0.426; therefore misspecified.

**The null that argument needs is not 0.** It is the rms a *perfect* model would leave
against a pooled **counting** measurement with these counts. The archived survival
values are exact integer multiples of a counting quantum — `1/(4000·241³) = 2^-35.70445`
for n=43, `1/(6000·241³) = 2^-36.28941` for n=50 — so every point's pooled count is
recoverable, and the expected squared log2 residual of a perfect model is a closed-form
Poisson sum, `E[(log2 λ − log2 C)² | C ≥ 1]`.

Recomputed here from the `.out` files alone:

| file | scores | delta-method floor | exact truncated-Poisson floor | **achieved** |
|---|---|---|---|---|
| n=43 whole band | 1803 | 0.4094 bits | **0.3406 bits** | 0.4257 |
| n=50 whole band | 2310 | 0.3347 bits | **0.3276 bits** | 0.4274 |

**Between 62 % and 92 % of the 0.426, in rms, is the instrument.** The residual misfit
is 0.12–0.26 bits (n=43) and 0.27–0.28 bits (n=50) — never 0.426.

Why the whole-band statistic is this bad: 62 scores carry pooled count exactly **1** and
121 carry count ≤ 2 (n=43). Those 121 rows carry **63 %** of the noise-variance budget
while representing roughly *two* independent observations. Equal weighting hands the
unresolved tail the fit.

**This contradicts the same record.** `VAL-20260803-54b29b` L-2 states *"NO SIGNIFICANCE
IS ESTABLISHED FOR THE CHECK A DISPLACEMENT … The control that would — resampling the
survival curve under its counting model — is a simulation and is forbidden by this
handoff's ZERO NEW SAMPLING constraint."* O-2 is nevertheless graded **ESTABLISHED** on
a comparison L-2 declares unavailable. **And L-2's premise is wrong**: the control is
not a simulation. The expectation has a closed form; ZERO NEW SAMPLING never forbade it.
The batch declined a control it could have run in five lines.

## RT-7 (the conclusion survives, by a route BATCH-010 did not take).

I ran the profiled-`K` scan on four sub-bands per file with my own implementation:

| sub-band | scores | counting floor | best achievable rms | ratio |
|---|---|---|---|---|
| n=43 `count≥1000` | 852 | 0.0146 | **0.2406** at p=19.5 | **16×** |
| n=43 `count≥10⁵` | 551 | 0.0011 | 0.1394 at p=18.0\* | 127× |
| n=50 `count≥1000` | 1132 | 0.0152 | **0.3775** at p=20.0 | **25×** |
| n=50 `count≥10⁵` | 636 | 0.0014 | 0.2089 at p=17.0\* | 149× |

\* at my grid edge; the argmin *location* there is scan-width limited, the rms value is not.

**In the region where the measurement is resolved to 0.015 bits, no member of the fitted
family gets within 0.24 bits.** That is misfit, unambiguously, and it owes nothing to the
unresolved tail or to the number 0. **The conclusion of O-2 stands; the argument given
for it must be replaced.**

## RT-8 (MATERIAL). An inventor-protocol §3 artifact tell the record does not report.

Ask what the reported quantity *should* do as the parameter meant to destroy it is
removed. For an exponent estimate from a correctly specified one-parameter family,
restricting to better-measured data should make the argmin **converge**. Measured:

```
n=43:  23.00 (whole)  ->  22.50 (count>=10)  ->  19.50 (>=1000)  ->  18.00 (>=1e5)
n=50:  22.00 (whole)  ->  21.50 (count>=10)  ->  20.00 (>=1000)  ->  17.00 (>=1e5)
```

Monotone drift over at least 5 units of `p` as the noise goes to zero. This is
simultaneously (a) the canonical artifact tell against the **numbers** 23.25 and 22.25,
and (b) direct positive evidence of misspecification — *stronger* than anything in the
record, because a correctly specified family cannot produce it.

**Required of any downstream record:** O-1 quotes "argmin p=23.25 rms 0.425715" and
"argmin p=22.25" to six decimals as located points. No record may present them as *the
exponent this comparison selects* without stating that the selected value is a function
of the sub-band and ranges over at least `[18.0, 23.25]` and `[17.0, 22.25]`. The
**direction** (below the archived exponent in every sub-band tested) is robust and is
strengthened, exactly as O-3 says.

**Cheapest check:** `exponent_neighbourhood_scan.py` line 483,
`ge10_idx = [i for i in range(len(band)) if counts[i] >= 10]` — sweep the threshold and
tabulate argmin, rms and the matching counting floor. One line.

## RT-9 (BLOCKING, scope). The object declared misspecified is **not** Approximation 4.9 — and the misfit now has a named mechanism inside the surrogate.

What was fitted is `min(1, K·v^p)`. That equals Approximation 4.9's region measure
**exactly iff `Φ` is exactly Gaussian in (x,y)**: with `Φ = exp(−a x² − b y²)`,
`λ ∝ x^{β_sieve−1}`, `µ ∝ y^{n_fft−1}`, the region `{a x² + b y² ≤ v}` has `λµ`-measure
exactly `C·v^{(β_sieve+n_fft)/2}` — which is where the exponent `p` comes from in the
first place.

The source's actual `Φ`, now in the archive courtesy of AN-2, is `(4.10)`:

> `Φ_{d}(i,j) ≜ Υ_{β_sieve/2}((2π/q) d_lat i) · Υ_{n_fft/2−1}((2π/q) d_lsc j)`,
> `Υ_n(x) ≜ Γ(n+1) J_n(x)/(x/2)^n`  [(4.11)]

Evaluating `(4.11)`'s own series against `exp(−x²/(4(n+1)))`:

| x | lat side, n=β_sieve/2=22 | **lsc side, n=n_fft/2−1=3** |
|---|---|---|
| 3 | −0.0003 bits | −0.052 bits |
| 4 | −0.0009 | **−0.189** |
| 5 | −0.0023 | **−0.581** |
| 6 | −0.0047 | **−2.047** |
| 6.38 | — | **`Υ₃` CHANGES SIGN** (first zero of `J₃`) |
| 12 | −0.081 | wildly divergent |

The lat side is harmless. **The lsc side is not**: the Gaussian surrogate is positive and
monotone; `Υ₃` is neither. With `(2π/q)·d_lsc = 0.624` per unit `j`, `x = 6.38` is
`j ≈ 10`, inside the range the region integral covers. So `E(T−t)` is **not an
ellipsoid**, its `λµ`-measure is **not a pure power of v**, and its **local log-log slope
is v-dependent** — which is precisely the drift RT-8 measures. The degradation is worst
exactly on the side contributing `n_fft/2 = 4` of the exponent, because `n_fft = 8` is
small.

**Consequence.** O-2's "Approximation 4.9's family is misspecified" over-attributes.
Supported: *"the Gaussian-Φ power-law surrogate that BATCH-009 substituted for
Approximation 4.9 is misspecified, with a named mechanism."* Whether **Approximation 4.9
itself** is misspecified is **untested** by this program.

This is an **observation collision** in the `KN-TECH-080` §8.2 sense: two distinct
ground-truth objects (Gaussian `Φ`, Bessel `Φ`) produce the same observable to leading
order and sit on opposite sides of the conclusion. No condition in the reviewed package
separates them. **C3 is the separator.**

## RT-10 (MATERIAL). `α` for the toy runs is identifiable from the archive — and the check that identifies it is the only unfitted absolute-level control the archive permits.

BATCH-010 records `α` as UNAVAILABLE, therefore Check B's magnitude *"is a scanned bound
and not a number"*, and explicitly declines to adopt the `Pgood` header's
`alpha_secret = alpha_error = 2`. That caution is falsifiable from the archive.

`(4.19)` is a **parameter-free** prediction of the threshold at which `Pgood ≈ 1/2`
`(4.20)`, and `Pgood_q241_m40_n43_….out` is 4000 raw values of `F(solution)` — whose
median **is** that threshold. Computed here:

| quantity | value | ratio to archived median |
|---|---|---|
| archived median `F(solution)` | **11964.5** | — |
| `(4.19)` at α=2, `d_lat = 42.00` (Fig 4.1 caption) | **12021.9** | **1.0048** |
| `(4.19)` at α=2, `d_lat = 41.072` (`.out` header) | 12326.7 | 1.0303 |
| `(4.19)` at α=1 | 17661.7 | 1.4762 |
| `(4.19)` at α=3 | 8190.4 | 0.6846 |
| **best-fit α from the archived median** | **2.012** | — |

The identification is not marginal: neighbouring integers are off by 48 % and 32 %.
**α = 2 for the n=43 toy run**, established by the paper's own Approximation 4.8 against
the archive rather than by trusting a header field.

**This cuts against my own artifact case and I record it as such.** A T-axis scale error
— a `k_fft = 3` slip would be a factor of 3 — would show as a 3× ratio or an α off by
~9. The observed ratio is 1.005 with an *unfitted* formula. "The 0.426 floor is a
score-scale artifact" is dead, independently of the validator's C-1.

**Direction of effect on the record: it strengthens O-6.** O-6 already computed the
Jensen correction at `a·µ² = 0.194761`, which *is* the α=2 value; what it lacked was the
licence to call α=2 the paper's α. With that licence, "0.31 % and 0.27 % of the
over-predictions" stops being a scanned bound and becomes a number at an identified α.
The BATCH-009 over-prediction remains unattributed, and now more firmly.

## RT-11 (BLOCKING, scope). The entire comparison lives at ~15 % of the operating threshold, and that is missing from `boundaries`.

The record's `boundaries` name the resolved band but never say where that band sits
relative to the threshold the attack uses. From the source, PDF p27 / printed 26:

> "we constrain the parameters `N` and `T` such that `ε := R P_wrong q^{k_fft}` … we
> select `T` following Approximation 4.8, ensuring that `P_good ≈ 1/2`."

So the operating threshold is the median good-guess score, which the archive carries
directly: **11964.5**. The `Pwrong` measurement's last positive score is **1802**.

**The operating threshold is a factor 6.6 beyond the last score at which `P_wrong` was
measured at all.** At the operating point `P_wrong` sits below the counting floor
`2^-35.70` and is simply not in the archive. The BATCH-009 headline over-prediction at
`T=471` sits at **3.9 %** of the operating threshold.

This is a limitation of the *source's own validation* as much as of this program's —
Carrier et al. can only measure where 4000 iterations reach — and it must be on the
record either way, because it bounds what any shape agreement or disagreement in this
band can mean.

### On O-4 specifically

BATCH-010's characterisation of `T > 1000` as the least informative region is **correct,
and correct for a second reason it does not give.**

- **Statistically.** The truncated-Poisson noise floor on `T > 1000` is **0.510 bits**
  (n=43) against the validator's reported residual rms of **0.266**. A fit that beats its
  own noise floor by a factor of two on 802 rows is not a fit — the region contains
  O(10) independent observations spread over 802 rows. 62 rows carry pooled count exactly
  **1**, i.e. *one datum*: the single largest wrong-guess score among 5.6 × 10¹⁰
  candidate scores. 59 more carry count 2. Recording "the own exponent IS the argmin
  there, excess +0.000935" to six decimals gives it far more standing than it has.
- **Operationally.** It is not the security-relevant region either. **Nothing in the
  resolved band is.**

So O-4 is honestly recorded and should stay recorded — but it is **not** "the region that
matters". There is no region in this archive that matters in that sense, and the record
should say so.

## RT-12 (candidate artifacts tested and dismissed).

Recorded so they are not re-tried.

- **Quadrature — dismissed.** Producer's coarse-vs-fine max `|Δlog2| = 2.8e-14` bits;
  `K→∞` closed-form self-check exact to `2.6e-15`; validator reproduced at GL 8/12/16 and
  3× panel density; my order-10 different-panel implementation reproduces the whole-band
  rms at `p=26` to `5e-5` bits. Not in play at the 0.4-bit scale by eleven orders of
  magnitude.
- **Fitted-normalisation protocol — dismissed as the cause of the floor.** Profiling one
  parameter cannot *create* a floor, and control C-3 shows the identical protocol reaches
  rms exactly 0 on noiseless model data. It remains the reason nothing about absolute
  *level* is tested (L-1), and it is why RT-9's mechanism can hide inside `K`.
- **Counting-model overdispersion — dismissed where testable.** If the 5.6 × 10¹⁰ pooled
  candidate scores were strongly correlated within an iteration, the RT-6 floor would be
  an *under*estimate. Tested directly on the archived histogram increments (cumulative
  differences, i.e. pooled scores exactly equal to `T`) with a local log-quadratic fit:
  Pearson-residual variance **0.79** (n=43) and **0.94** (n=50) at window 15, which after
  correcting for the ~20 % absorbed by the 3-parameter local fit is ≈ 1.0–1.2. Poisson is
  approximately the right marginal noise model in mid-band. *Untested* where increments
  < 30, i.e. the deep tail.
- **Score-axis scale error — dismissed twice**, by the validator's C-1 and independently
  by RT-10.
- **Resolved-band choice — not dismissed, subsumed into RT-6.** Ending the band at the
  last positive score also introduces a selection bias (rows whose true expectation is
  below one count enter the band only when they fluctuate upward), which no member of any
  family can fit.

## RT-13 (moderate). The closure standard, applied to the record's own negative.

`docs/inventor-protocol.md` §4: a closure needs a named obstruction, an argument, and
forward guidance. O-6 closes the attribution question by naming two blockers —
*"`Φ_dlsc` and `α` are UNAVAILABLE in the archive"* — and **both are now false** (AN-2
for `Φ`, RT-10 for `α`). What remains is "we scanned two readings and neither absorbed
the effect", which is a statement about the search, not about the problem. Its honest
status is `unverified` until it is either re-derived with `(4.10)`/`(4.11)` and `α=2` in
hand, or restated with a real obstruction.

**Forward guidance:** RT-9's `Υ₃` sign change is a candidate obstruction *and* a candidate
explanation of the over-prediction at the same time — a region measure that is not a pure
power of `v` mis-states the level as well as the shape, and does so on the lsc side where
`n_fft = 8` makes the Gaussian surrogate worst. Test that before "unattributed" is
recorded again. **C3 does it.**

---

# 3. The cheapest check that settles the 0.426-bit question

**C1 — the closed-form counting-noise floor.** No model, no quadrature, no exponent scan,
no random numbers; under a second per file.

1. Recover the pooled count of every score, `C_T = value_T · nb_iteration · q^{k_fft}`
   (both from the `.out` header; the values are exact integer multiples of that quantum,
   max relative deviation `2.2e-16`, already verified as M-05).
2. Report `floor_rms = sqrt( mean_T E[(log2 λ − log2 C)² | C ≥ 1] )` under
   `C ~ Poisson(C_T)`, with the delta-method value `1/(C·ln²2)` beside it.

**It returns 0.3406 bits (n=43) and 0.3276 bits (n=50) against achieved 0.4257 and
0.4274**, and thereby settles the question: the 0.426 floor is dominated by the counting
instrument, and the misspecification case must be made in the `count ≥ 1000` sub-band
instead (**C1b**), where it succeeds decisively.

Three further controls, in cost order: **C1b** (sub-band rms table — one line changed in
the producer's own script); **C2** (the `(4.19)`-vs-`Pgood`-median unfitted control, which
also identifies `α`); **C3** (the decisive separator — replace `K·v^p` by the exact region
measure from `(4.10)`/`(4.11)`/`(4.24)` at `α=2` and refit). **C3 is cheap because the
model quadrature is data-independent**: in `fit_one_p`, `accumulate` and `predict_from_J`
never read `log2meas`, so the region-measure table is computed once and reused across
every `K`, every fit set and every replicate. A successor handoff that budgets C3 as if
each refit needed a fresh quadrature will over-budget it by orders of magnitude.

A fourth, **C4**, supersedes the validator's C-6 "`absent_and_not_possible_here`": a null
object of the same *shape* does not need to exist in the archive, because it can be built
deterministically — take `Q(T) = 0.5·erfc(T/√N)` alone, round to the same counting
quantum, truncate at its last positive score, and run the identical scan. If the scan
returns a confident located argmin on a structureless object, that is a controlled null.

---

# 4. Does the misspecification reading survive?

**YES, in narrowed form — and its stated argument does not.**

**Survives.** There is genuine, large, unfittable misfit. In the `count ≥ 1000` sub-band
the best achievable rms is **16×** and **25×** the counting floor, and the argmin fails to
stabilise as noise is removed. Both are stronger evidence of misspecification than
anything currently in `EV-MLKEM-eac95b`, and neither depends on the unresolved tail or on
the number 0.

**Does not survive, and must be struck.**

1. The argument *"the best achievable rms is 0.426 bits, not 0"*. Zero was never
   achievable. Most of the 0.426 is the instrument, and the validator's own L-2 says no
   significance is established.
2. The attribution to *"Approximation 4.9's family"*. What is shown misspecified is
   BATCH-009's Gaussian-`Φ` surrogate, and there is now a named mechanism for why,
   located in the surrogate.

**What O-2 is entitled to claim after this pass — no more and no less:**

> Over the two archived `q=241, m=40, n=43/50` Carrier et al. `Pwrong` files, in the
> sub-band where the pooled counting estimate is resolved to better than 0.02 bits
> (pooled count ≥ 1000; scores 0–851 for n=43, 0–1131 for n=50), the
> one-free-normalisation family `min(1, K·v^p)` — which is BATCH-009's Gaussian-`Φ`
> power-law **surrogate** for Approximation 4.9, not Approximation 4.9 itself — leaves a
> best achievable rms log2 residual of **0.241** and **0.377** bits against a
> counting-noise floor of **0.0146** and **0.0152** bits. No member of that surrogate
> family fits. The exponent minimising the residual is not the archived
> `(β_sieve + n_fft)/2` in either file and lies below it in every sub-band tested, but its
> **value is not identified**: it drifts monotonically over at least `[18.0, 23.25]`
> (n=43) and `[17.0, 22.25]` (n=50) as measurement noise is removed. A named mechanism
> for the misfit exists and lies in the surrogate: `(4.11)`'s `Υ_{n_fft/2−1}` with
> `n_fft = 8` departs from its Gaussian surrogate by more than 0.5 bits at
> `(2π/q)·d_lsc·j ≈ 5` and changes sign at ≈ 6.38, so `E(T−t)` is not an ellipsoid and
> its `λµ`-measure is not a pure power of `v`. **Whether Approximation 4.9 is
> misspecified is UNTESTED.** Separately, `α = 2` for the n=43 toy run is established
> from the archive by `(4.19)` against the archived good-guess median (ratio 1.0048), and
> the resolved band ends at roughly 15 % of the operating threshold (median
> `F(solution) = 11964.5` against last measured score 1802). Toy tier. Nothing here bears
> on ML-KEM security in either direction.

---

# 5. Next concrete action

**Run C3.** Recompute `W(v) = ∫_{E(v)} λ(x)µ(y) d(x,y)` exactly from `(4.10)`, `(4.11)`
and `(4.24)` at `α = 2` with the `.out`-header `d_lat` and `d_lsc`, keep the `(4.22)`
position for the `d_lsc` integral, refit with the same profiled-`K` protocol, and report
the `count ≥ 1000` rms beside its 0.0146 / 0.0152-bit counting floor.

Both outcomes are informative:

- **If the misfit collapses** toward the floor, the misspecification is BATCH-009's
  surrogate and Approximation 4.9 is exonerated at toy scale in the resolved band.
- **If it persists**, the misspecification is Approximation 4.9's, and it becomes a real,
  mechanism-backed finding rather than an artifact of a substitution.

Run C1 and C2 alongside as reported controls — both are already computed here and cost
seconds. **Do not run a wider exponent scan before C3**: RT-8 shows the argmin is not a
property of the data.

---

**`dominated_by`: `n/a (no result claimed)`** — checked, not left blank. This report
advances no attack and occupies no point on any cost frontier in time, memory or
data/queries; there is no axis on which to be dominated.
**`sota_delta`: zero.** No time, memory, data, query or security quantity is improved,
degraded or claimed, by this report or by anything it reviews.
