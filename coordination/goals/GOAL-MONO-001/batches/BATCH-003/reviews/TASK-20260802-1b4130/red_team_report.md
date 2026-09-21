# RT-20260802-1b4130 — Red Team report on RUN-MONO-4b50b6-001

**Task** `TASK-20260802-1b4130` · **Goal** `GOAL-MONO-001` · **Batch** `BATCH-003`
**Snapshot reviewed** `fdb8ef8fb8966dbf22d5c4457eaa37478e265284` (verified reachable
from `HEAD` = `10eb510e`; the review read only that committed tree)
**Verdict** `ADMIT_WITH_CORRECTION`

**Model provenance (self-reported, per AGENTS.md §Model policy).**
`requested_policy: review-adversarial`; `resolved_model_id: claude-opus-5`;
`fallback_used: true`; `model_verified: false`. `claude-opus-5` is **not** in this
task's `authorized_fallback_models`
(`gpt-5.6-sol-xhigh`, `gpt-5.6-terra-medium`, `claude-sonnet-5-thinking-high`,
`claude-4.6-opus-high-thinking`, `cursor-grok-4.5-high-fast`), and it is the **same
resolved model** the executor recorded in `run_record.yaml`. This session is
independent; the *model* is not. See **O-11** — this report cannot discharge
AGENTS.md rule 12 for a closure claim.

---

## 0. Summary of position

The mathematics in this package is **correct**. I re-derived every load-bearing
number I could reach without trusting the producer, and each one held. That is
stated up front because the objections below are all about *labelling, provenance,
control power, and forward scope* — not about the result being wrong. Manufacturing
a mathematical objection here would be the symmetric failure the inventor protocol
warns against.

What I independently confirmed (commands and outputs in §3):

| checked | method | result |
|---|---|---|
| `disc_T S_3 = 16 f(x1) f(x2)` | evaluation on a `7^4` integer grid (exceeds the total-degree bound, so this is a proof over `Z`) + 20 000 random points | **holds; 0 counterexamples** |
| Closed-form histogram | **true exhaustive `p²` enumeration** with the discriminant+Legendre classifier, 12 curves (2 random + 1 CM per prime, `p` up to 1601) | **0 mismatches** |
| `closed_form_check` (105 curves, 0 mismatches) claimed in `run_record.yaml` | recomputed from `results.json` | **0 mismatches; the claim is true** |
| Corollary E on the factor base | direct classification of **all 1196 off-diagonal FB pairs on all 105 curves** | **0 non-split** |
| `D = −11` supersingular at all four pinned primes | Kronecker symbol `(D/p)` and `#E = p+1` | **confirmed, all four** |
| CM screen `= 22` scored curves | ordinary/SS split predicted by `(D/p)` per prime: 6+4+6+6 | **= 22, exactly** |
| Automorphism panel `= 3` curves | `j=0` ordinary iff `p ≡ 1 mod 3` (211 only); `j=1728` ordinary iff `p ≡ 1 mod 4` (809, 1601) | **= 3, exactly** |

So the identity, the closed form, the CM counts, the automorphism counts, and the
self-reported `j mod p` defect story all survive independent reconstruction. The
package is admissible. Eleven corrections must ride in the ledger archive before
the readings are propagated, and two of them (**O-3**, **O-10**) are blocking.

---

## 1. Objections

### O-1 — "Corollary D closes `KN-OPEN-009` at `m = 3`" is *true but mis-weighted in both directions*: it understates the theorem and overstates its significance

**Claim attacked.** `execution_report.md` §2 and its closing paragraph: the identity
"settles `KN-OPEN-009` at `m = 3`"; `contract.md` Corollary D: "Hypothesis B of the
protocol's `discrimination` block is therefore **empty at m = 3**."

**Why this may be wrong — the understatement.** `KN-OPEN-009` asks for the
**geometric monodromy group**. The package never states it. It answers a *proxy*
(the split *density*) and lets the reader infer the group. The group-theoretic
answer follows from the same identity in two lines and is strictly stronger:

> `S_3(x1,x2,T)` is a quadratic in `T` over `k(x1,x2)`, `k = \bar F_p`, with
> discriminant `16 f(x1) f(x2)`. Over `k`, `f(x1) f(x2) = ∏_i (x1 − e_i) ∏_j (x2 − e_j)`
> with the `e_i` the three **distinct** roots of `f` (distinct ⇔ `E` non-singular),
> so it is a product of six pairwise-distinct irreducibles of `k[x1,x2]`, i.e.
> squarefree, hence not a square in the UFD and not a square in its fraction field.
> `16` is a unit for `p > 2`. Therefore `S_3` is irreducible over `k(x1,x2)` and the
> **geometric monodromy group is the full `S_2`** — for every non-singular `E`, at
> every `p > 3`, with **no exceptional locus**. The same argument over `F_p(x1,x2)`
> gives arithmetic monodromy `= S_2`.

This is unconditional, needs no Hasse bound, no Chebotarev, and no census. The
density statement (Corollary B/C) is a *consequence* of it. The package proves the
weaker consequence and calls it the closure.

**Why this may be wrong — the overstatement.** `KN-OPEN-009`'s actual mechanism of
interest is named in its own title and tags: *imprimitive*, *block system*,
*resolvent decomposition*. A transitive group of degree 2 is **primitive by
definition** — its only block systems are the two trivial ones. So at `m = 3` the
phenomenon `KN-OPEN-009` is hunting **cannot exist for degree reasons**, before any
curve is examined. The closure is therefore real but *informationally empty about the
open problem's mechanism*: `m = 3` is exactly the case where the question is
degenerate. Calling it "the substantive `m = 3` census is the gate"
(`KN-OPEN-009` current-state text) and reporting the closure as a program
contribution, without saying that the closed sub-case is the one that could not have
gone the other way, inflates significance by omission. Under
`docs/inventor-protocol.md` §4 a closure owes **forward guidance**; "`m ≥ 4` remains
fully open" is present and correct but does not say *why* `m = 3` was never able to
answer the question.

**Cheapest falsification.** One line of Sage/PARI on any single curve:
`factor(S3)` over `GF(p)(x1,x2)` — if it factors, my irreducibility argument is
wrong and the geometric monodromy is trivial. `is_irreducible` on the quadratic, or
equivalently `is_square(16*f(x1)*f(x2))` in the function field. Seconds.

**Disposition. PARTIALLY UPHELD.** The closure is valid. Two corrections owed:
state the group-theoretic conclusion (it is free and stronger), and state that the
imprimitivity/resolvent half of `KN-OPEN-009` is vacuous at degree 2 so that the
corpus does not record `m = 3` as evidence about `m ≥ 4`.

---

### O-2 — The experiment had exactly one reachable non-infrastructure outcome; `outcome_id` is not evidence

**Claim attacked.** `execution_report.md` headline: "`outcome_id =
FULL_MONODROMY_BARRIER_TOY`, computed mechanically from the protocol's
`barrier_aggregate_rule`", presented as the result; the protocol's
`discrimination` block advertising "a genuinely two-sided experiment".

**Why this may be wrong.** `EXCEPTIONAL_LOCUS_TOY` requires a curve with sampled
`|Δ| > 3·(2/√p)`. By Corollary C the *exact* `|Δ|` is `< 4/p`, so the only route to
that outcome is binomial noise. I measured the required excursion:

| `p` | envelope `3·(2/√p)` | binomial `σ` at 30 000 | excursion needed |
|---|---|---|---|
| 211 | 0.4131 | 0.00289 | **143 σ** |
| 1601 | 0.1500 | 0.00289 | **52 σ** |

and over all 105 censused curves the worst `exact |Δ| / envelope` is **0.0416**. The
probability of the alternative branch firing is of order `10^{-500}` per curve. The
run's mechanical outcome was determined before it started, conditional only on the
code being correct. Its informational content is **instrument integrity**, not
monodromy. Presenting the gate table (`≥ 3` sizes, `≥ 20` controls, CM hard gate) as
the top-line finding invites a downstream reader to treat a foregone conclusion as a
measurement — the exact reading `docs/inventor-protocol.md` §3 forbids ("run the
identical measurement against a null object … record a controlled null, not a
finding"). Here it is worse than a controlled null: there is no object of this shape
that could have produced a different answer.

To be fair to the producer: the identity was found *by* this run, and before it the
protocol designers had no way to know the experiment was one-sided. The report does
say "The census confirms it; the identity establishes it." That sentence is correct
and is buried in §2 under the gate table.

**Cheapest falsification.** Exhibit any curve over any `p > 3` whose exact split
density leaves `1/2 ± 4/p`. Corollary C says none exists; a single counterexample
would break both my objection and Corollary D. Cost: the `p²` enumeration in §3
(2.2 s per curve at `p = 1601`).

**Disposition. UPHELD.** The evidence record must state that `outcome_id` was
non-discriminating at `m = 3` and that the mathematical content is the Lemma.

---

### O-3 — Closed-form-derived quantities are labelled "measured" (BLOCKING)

**Claim attacked.** Three places:

1. `execution_report.md` §3: "the harness **measures** `[1.4897, 1.5102]` across all
   80 curves."
2. `execution_report.md` §1: "**Measured** `p·|Δ|` never exceeds `0.9994` when `Z = 0`
   and `3.9941` when `Z = 3`."
3. `manifest.yaml` `result.summary_measurements.relation_proxy_ratio_over_quasirandom:
   [1.4897, 1.5102]`, and the field name
   `exact_enumeration.ratio_measured_over_quasirandom` in `results.json`.

**Why this is wrong.** None of those numbers is a census measurement. I recomputed
what the *frozen protocol's sampled census* — the primary deliverable — actually
produced for the same quantities:

| quantity | reported as "measured" | what the sampled census gives |
|---|---|---|
| relation-proxy ratio over 80 random curves | `[1.4897, 1.5102]` | **`[0.0000, 10.98]`** |
| `p·|Δ|`, random panel, `p = 1601` | `0.9994` (max, all primes) | **`10.833`** |
| `p·|Δ|`, random panel, `p = 809` | — | `7.443` |

The relation-proxy figure is arithmetic on the closed form. The sampled
`joint_relation_proxy_rate` is a near-zero count statistic at three of four primes:
expected hits per curve are `8.1 / 1.9 / 0.55 / 0.14` at `p = 211/431/809/1601`, and
**17 of the 20 curves at `p = 1601` recorded exactly zero hits**. The protocol's own
required metric `delta_relation_vs_quasirandom` is Poisson noise at `p ≥ 431`. The
sampled census cannot support the factor-1.5 statement at all.

Likewise `p·|Δ| ≤ 0.9994` is the *exact* deviation; the *measured* one is up to
`10.8`, because the sampling noise `σ = 0.00289` is larger than the entire predicted
effect (`≤ 1/p = 0.00062` for the `Z = 0` random panel at `p = 1601`). Putting
"Measured `p·|Δ|`" next to sampled numbers in the same section is a category error a
reader will not catch.

`run_record.yaml` is better — it says `exact_ratio_measured_over_quasirandom_range`
and files the bounds under `exact_deviation_bounds`. `execution_report.md` and
`manifest.yaml` are not.

**Cheapest falsification.** Already run: read
`joint_relation_proxy_rate / quasirandom_relation_prediction` straight out of
`results.json` for the 80 random curves and compare with
`exact_enumeration.ratio_measured_over_quasirandom`. Three lines of Python, and the
two ranges do not overlap in spread.

**Disposition. UPHELD — BLOCKING.** No evidence record may carry
`[1.4897, 1.5102]` under `summary_measurements` or the word "measured". Correct
label: *derived, closed form*; the empirical face is `CTRL-POS-PLANTED-SPLIT`.

---

### O-4 — The sampled census is underpowered for the effect it is credited with confirming, and the run had 500× the budget to fix it

**Claim attacked.** `specification.yaml` `budget_note`: "Actual is 13.755 s …
Under budget by three orders of magnitude; recorded, not rounded" — offered as
efficiency; and `execution_report.md` §1 crediting the census with confirming the
`O(1/p)` bound.

**Why this may be wrong.** The protocol pinned 30 000 samples/curve when the expected
scale of the deviation was the `O(1/√p)` Weil floor. Once the effect is known to be
`O(1/p)`, 30 000 samples resolve nothing: `σ = 0.00289` against a random-panel exact
effect of `≤ 1/p ∈ [0.00062, 0.0047]`. In the `Z = 0` random panel the effect is
**below one σ at every pinned prime**. So the sampled census neither confirms nor
could confirm Corollary C; only the closed form does, and the closed form is derived
from the identity being tested. That is a closed loop.

The break in the loop is a genuine exhaustive `p²` enumeration by the polynomial
classifier, which is *independent* of the closed form. The protocol asks for exactly
this — `quasirandom_relation_prediction` says "record also the **exact-enumeration**
alternative when `p` is small enough" — and the harness named its field
`exact_enumeration` while computing it by the closed form instead (honestly disclosed
in the `method` string, but the field name asserts otherwise). **It was affordable**:
I timed one `p = 1601` curve at **2.2 s**, so all 20 at `p = 1601` cost ~45 s and all
105 curves cost well under 1000 s against a **7200 s budget of which 13.6 s was
used**. The run had 500× headroom and spent none of it on the one measurement that
would have given the census independent power.

**Cheapest falsification.** I ran it: exhaustive `p²` enumeration on 12 curves
(2 random + 1 CM at each of 211/431/809/1601) with the discriminant+Legendre
classifier — **0 mismatches** against the closed-form counts, including the ramified
strata (`1254 / 2574 / 4842 / 9594`). So the closed form is *correct*; the objection
is that the run did not establish this itself when it trivially could have.

**Disposition. UPHELD.** Not blocking (I discharged the substance), but the ledger
must record that the sampled census is underpowered for `O(1/p)` and that the
independent confirmation came from this review, citing `RT-20260802-1b4130` §3.

---

### O-5 — `run_record.yaml` and `manifest.yaml` report verifications the archived harness does not perform, with no archived command

**Claim attacked.** `run_record.yaml` `measurements.closed_form_check:
{statement: "delta_split_vs_S2 == (t^2 − 2pZ + Z^2 − 2p + 2Z)/(2p^2)",
curves_checked: 105, mismatches: 0}` and `measurements.exact_deviation_bounds`
(`0.9994`, `3.9941`); `manifest.yaml` `result.certificate.verifier` clause (1),
which offers that check as one of the two verifications standing *in place of* a
solution certificate.

**Why this may be wrong.** Neither computation exists in `mono3_census.py` and
neither string appears anywhere in `results.json` (I grepped: `closed_form_check` 0
occurrences, `exact_deviation` 0, `p_times` 0). The trace-based formula
`(t² − 2pZ + Z² − 2p + 2Z)/(2p²)` is **never evaluated by the harness** — the harness
computes the histogram from `(Z, S, N)` directly. So the run's declared verification
#1 was performed by an unarchived ad-hoc computation. `AGENTS.md` artifact policy
requires the exact command and raw machine-readable results for every recorded
measurement; `docs/claims-and-verification.md` reserves the `verifier` slot for a
recomputation the run wrapper performs.

Same for the `sympy` claim — see **O-6**.

**Cheapest falsification.** Recompute it from `results.json` (`p`, `trace_t`,
`chi_counts.Z`, `exact_enumeration.delta_split_vs_S2` are all present). I did:
**105 curves, 0 mismatches**, and the panel maxima are exactly `0.9994` (random),
`3.9941` (CM), `3.9941` (automorphism). The reported numbers are **true**.

**Disposition. UPHELD on provenance, WITHDRAWN on correctness.** Either archive the
analysis script under the run directory as a superseding artifact, or restate the
lines as *"recomputed post hoc from `results.json`; independently reproduced by
`RT-20260802-1b4130`"*. Do not leave a `verifier` clause pointing at code that does
not exist.

---

### O-6 — `contract.md` asserts a `sympy` verification that the run declares it did not have

**Claim attacked.** `contract.md` §2: "Verified symbolically (`sympy.expand`,
difference identically `0`) **and checked numerically on every censused curve**."

**Why this may be wrong.** `specification.yaml` says `dependencies: stdlib only`;
`manifest.yaml` lists `argparse, hashlib, json, random, sys, time, collections`; the
driver imports no `sympy`; no symbolic-verification artifact is in the snapshot.
And the harness performs **no numerical check of the identity on any curve** — there
is no code computing `(b²−4ac) − 16·f(x1)·f(x2)`. The nearest thing is
`sampled_vs_exact`, which is a 4σ agreement of *frequencies* at tolerance `0.0116`,
not a verification of a polynomial identity. Under `AGENTS.md` rule 9 a stated
computation with no recorded command is not admissible as evidence, even when true.

**Cheapest falsification.** I verified the identity independently over `Z`:
evaluation on the full grid `x1,x2,A,B ∈ [−3,3]` (`7⁴ = 2401` points, which exceeds
the total-degree bound of the difference, so agreement there **is** a proof of the
identity over `Z`) plus 20 000 random integer points in `[−500,500]⁴` —
**0 counterexamples**. Cost: under a second. `sympy` 1.14.0 *is* importable in this
environment, so the check was available; it simply is not archived.

**Disposition. UPHELD on provenance, WITHDRAWN on correctness.** Replace the
sentence with either an archived command or a citation to this report's
reproduction.

---

### O-7 — Two of the protocol's negative controls have no discriminating power at the pinned primes and are reported as `pass` without that note

**Claim attacked.** `run_record.yaml` `controls: CTRL-NEG-UNIFORM-WINDOW: pass`,
`CTRL-NEG-SHUFFLED-WINDOW: pass`.

**Why this may be wrong.** `CTRL-NEG-UNIFORM-WINDOW` tests
`|uniform_window_rate − (W_eff/p)²| ≤ 0.02` against an expected rate of `(4/p)²`:

| `p` | expected rate | tolerance / expected | control still passes for any window up to |
|---|---|---|---|
| 211 | `3.59e−4` | 56× | `W_eff = 30` |
| 431 | `8.61e−5` | 232× | `W_eff = 61` |
| 809 | `2.45e−5` | 818× | `W_eff = 114` |
| 1601 | `6.24e−6` | **3204×** | `W_eff = 226` |

The control passes for `W_eff = 0` (empty window) and for every `W_eff` up to ~226 at
`p = 1601`. It cannot distinguish a correct window from a missing one, an off-by-one
one, or a 50×-too-large one. `CTRL-NEG-SHUFFLED-WINDOW` (tolerance `0.03`) is worse.
Measured worst gaps are `1.4e−4`–`2.2e−4`, i.e. 100–330× inside tolerance — the
"margin" is an artifact of an absolute tolerance applied to a quantity six orders of
magnitude smaller. Per `docs/inventor-protocol.md` §3, a control that cannot fail is
not a control; recording it as `pass` alongside controls that *can* fail
(`CTRL-IMON-*`, `INSTRUMENT-DUAL-CLASSIFIER`) overstates the integrity evidence.

This is a defect **inherited from the frozen protocol**, which the executor could not
relax — but it could have flagged, and adding a powered variant was permitted
("adding controls to a frozen protocol is permitted").

**Cheapest falsification.** Set `fb_set = set()` in `census_curve` and re-run: both
controls still report `pass`. One-line mutation, 14 s.

**Disposition. UPHELD.** The evidence record must mark these two controls
`pass_without_power` at the pinned primes, and the protocol successor should switch
them to a relative tolerance (e.g. `|rate/expected − 1| ≤ 0.25`) or raise `W`.

---

### O-8 — Corollary E's "constant factor, moves no exponent" is right at `m = 3` but is stated unscoped, its headline number is a `W_eff = 4` artifact, and the harness never checks its own premise

**Claim attacked.** `contract.md` Corollary E and `execution_report.md` §3: "**This
is a constant factor and it moves no exponent**"; the `1.5` headline; the field name
`ratio_measured_over_quasirandom`.

**(a) Is it novel?** No, and the report says so ("In hindsight it is unsurprising").
It should say something stronger: `P(split | x1, x2 ∈ FB) = 1` is not an empirical
finding at all — it is the statement that `E(F_p)` is closed under addition. The two
roots of `S_3(x1,x2,T)` are `x(P±Q)`; if `P, Q` are rational so are `P±Q`. Nothing
about monodromy, Chebotarev, or curve arithmetic is involved. The corpus should
record this as *a mis-specification of the protocol's proxy*, not as a corollary
ranked beside A–D. `CTRL-POS-PLANTED-SPLIT`'s "1594 trials, rate 1.0, without a
single exception" is an implementation check on the group law, and presenting it as
"the direct empirical face of Corollary E" (`run_record.yaml`) frames a tautology as
a measurement.

**(b) Is the factor really constant?** At fixed `m` and fixed `W_eff`, yes — I
uphold "moves no exponent" **as scoped to `m = 3`**. But the statement appears
unscoped in `run_record.yaml` `interpretation_limits` and in the execution report,
and two dependencies are hidden:
- **`W_eff` dependence.** The exact ratio is `(1 − 1/W_eff)/freq_split →
  2(1 − 1/W_eff)`. The headline `1.5` is the `W_eff = 4` value; the limit is `2`. A
  downstream consumer that pins `1.5` will be wrong for any realistic factor base.
  ICEX must be handed `2(1 − 1/W_eff)`, not a number.
- **Composition in `m`.** If a relation model applies a Chebotarev split factor
  once per summation fibre — which is what the protocol's proxy does — the correction
  is `2^{#fibres}`. For a fixed small `m` that is a constant. In the only regime
  where relation-rate models carry asymptotic weight (Gaudry/Diem-style decomposition
  over `F_{q^n}` with `n` growing, `n ~ log q` in the subexponential regime), a
  per-fibre factor of 2 compounds to `2^{n−1} = q^{Θ(1)}` and **does** move an
  exponent. "Moves no exponent" is true here and must be written with its scope
  attached, or it will be quoted out of it.

**(c) The harness never checks Corollary E's premise.** `exact_joint` is hard-coded
as `(W_eff² − W_eff)/p²` — it *assumes* `P(split | FB pair) = 1` rather than
verifying `χ(f(x)) = +1` on the window, which would be `O(W_eff)` per curve. So the
field named `ratio_**measured**_over_quasirandom` has an assumed numerator.

**Cheapest falsification.** I ran the missing check: for all 105 curves, classify
**every** off-diagonal factor-base pair with `classify_primary` — **1196 pairs, 0
non-split**. Two factor-base elements have `χ(f(x)) = 0`: both are `x = 0` on
quarantined `j = 1728` curves with `B = 0`, where `lex_smallest_affine_point` returns
the 2-torsion point `(0,0)`, the composite-order branch falls back to it, and
`W_eff` collapses to 1 (`p = 809, A = 795, B = 0` and `p = 1601, A = 250, B = 0`).
Both are in the automorphism artifact panel and excluded from every aggregate, so
nothing reported is affected — but the harness has **no guard** against a 2-torsion
generator producing a degenerate `W_eff = 1` window and a `ratio = 0.0`. Note for the
successor harness.

**Disposition. PARTIALLY UPHELD.** Corollary E is correct and correctly called
constant *at `m = 3`*. Required: attach the scope, hand ICEX
`2(1 − 1/W_eff)` rather than `1.5`, rename or annotate
`ratio_measured_over_quasirandom`, and downgrade "corollary" to "correction to the
protocol's proxy".

---

### O-9 — The correction is **not** `m = 3`-scoped: it holds at every `m`, and the artifacts understate it. This is the reverse failure the task asked me to hunt for

**Claim attacked.** `contract.md` §6 and `run_record.yaml`: "Corollaries A–E are
stated for `m = 3` only"; "At `m ≥ 4` … the discriminant has no such factorization,
and `KN-OPEN-009` remains **fully open**."

**Why this understates.** Corollaries A–D genuinely are `m = 3`-only: they rest on
the degree-2 discriminant factorization, which has no analogue at `m ≥ 4`. **Corollary
E does not.** Its mechanism is the group law, and the group law does not care about
`m`:

> If `x_1, …, x_{m−1}` are `x`-coordinates of `F_p`-rational points `P_1, …, P_{m−1}`,
> then `T` is a root of `S_m(x_1,…,x_{m−1},T)` iff `T = x(ε_1 P_1 + … + ε_{m−1} P_{m−1})`
> for some sign vector. There are `2^{m−2}` such values up to global sign, matching
> `deg_T S_m = 2^{m−2}`, and **every one of them lies in `F_p`**. So
> `S_m(x_1,…,x_{m−1},T)` **splits completely over `F_p`** — Frobenius cycle type =
> identity — for every `m`, unconditionally.

**Cheapest falsification / my verification.** I built `S_4` by the standard resultant
recursion `S_4(x1,x2,x3,T) = Res_X(S_3(x1,x2,X), S_3(x3,T,X))` over `F_211` on the
run's own first random-panel curve (`A=37, B=57`), took 193 triples of `x`-coordinates
of rational points, and factored each degree-4 specialisation:
**193/193 split completely into linear factors, with root set exactly
`{x(±P1±P2±P3)}`.** (My first attempt failed on a coefficient typo in the `S_3(x3,T,X)`
expansion and produced garbage — recorded here so the negative intermediate is not
hidden. The corrected run is the one reported.)

**Why this matters more than the understatement.** It is not merely that a corollary
generalises. It says the census instrument may be aimed at the wrong locus **at every
`m`**: the generic-fibre Frobenius statistic is measured over uniform
`(x_1,…,x_{m−1}) ∈ F_p^{m−1}`, whereas index-calculus relation search operates
entirely on the sublocus where the `x_i` are factor-base elements — a measure-zero
set on which the cycle type is *identically trivial*, at every `m`. `KN-OPEN-009`'s
premise, "the Chebotarev/Frobenius cycle-type census yields the quasirandom relation
rate", therefore needs re-examination before `GOAL-MONO-001` spends batches on an
`m ≥ 4` census. That is forward guidance the closure owes under
`docs/inventor-protocol.md` §4, and it is *more valuable* than the `m = 3` closure
itself. I am **not** asserting `KN-OPEN-009` is worthless — the imprimitivity
question at `m ≥ 4` remains genuinely open and could still matter for resolvent-based
decomposition. I am asserting that the *relation-rate* half of `KN-OPEN-009` is
answered at every `m` by the group law, and the artifacts do not say so.

**Disposition. UPHELD (underclaim).** Record the general-`m` statement, with the
instrument-relevance caveat, in the evidence record and in the `KN-OPEN-009`
successor entry.

---

### O-10 — The frozen `icex_feed` contract now specifies a `relation_rate_input` this run has shown to be wrong, and nothing machine-readable says so (BLOCKING)

**Claim attacked.** The protocol's
`icex_feed.outcome_packages[FULL_MONODROMY_BARRIER_TOY].relation_rate_input`:
"Use quasirandom `m=3` relation-rate proxy `chebotarev_S2_split * (W_eff/p)^2` …
Label as `chebotarev_prediction_plus_toy_census_envelope`", with
`attack_content: closed_at_toy_scope_for_exceptional_rate_sieves`.

**Why this is a live hazard.** The run emitted exactly the `outcome_id` that
activates that package, and the package's prescribed input is the quantity Corollary
E refutes. The refutation exists **only in English prose** in
`execution_report.md` §3 and its final bullet. `results.json` carries no flag;
`manifest.yaml`'s `summary_measurements` carries the ratio as if it were a
measurement (**O-3**); `ledger/goals/GOAL-ICEX-001.yaml` still reads only "remain
non-executing until charged SDEG/MONO/RELN measurement packages exist. No ICEX
measurement authorized." A driver that resumes `GOAL-ICEX-001`, reads
`outcome_id = FULL_MONODROMY_BARRIER_TOY`, and looks up the frozen protocol's feed
table will ingest the superseded input **without ever opening the execution report**.
The protocol is immutable, so the only fix is a superseding record that the ICEX
driver is forced to see.

Second hazard in the same field: `attack_content:
closed_at_toy_scope_for_exceptional_rate_sieves`. Given Corollary D that closure is
in fact **unconditional and prime-independent at `m = 3`**, not "at toy scope" — the
label is *weaker* than what is proved (a second underclaim), while
simultaneously being *stronger* than what the census showed (the census showed
nothing; **O-2**). Both halves need restating.

**Cheapest falsification.** Grep the snapshot for any machine-readable field that
would stop an ICEX driver: `results.json` has none; `manifest.yaml` has none;
`run_record.yaml` mentions it only inside a free-text `reading:` string. Confirmed.

**Disposition. UPHELD — BLOCKING.** The ledger archive (`TASK-20260802-32e4bf`) must
write a superseding correction record that (i) names
`icex_feed.outcome_packages[FULL_MONODROMY_BARRIER_TOY].relation_rate_input` as
superseded, (ii) gives the replacement `2(1 − 1/W_eff)` correction with its `m`-scope
(**O-8**, **O-9**), and (iii) is referenced from `GOAL-ICEX-001.next_action` so the
consuming driver cannot miss it.

---

### O-11 — The package makes a closure claim, which triggers AGENTS.md rule 12, which this harness cannot satisfy — and my own review does not repair it

**Claim attacked.** `execution_report.md`: "it **settles** `KN-OPEN-009` at `m = 3`";
`contract.md` Corollary D heading "no exceptional locus at `m = 3`"; and
`BATCH-003-OPENING.md`'s framing of the independence question.

**Why this may be wrong.** `AGENTS.md` rule 12: "Any claim proposed as a
breakthrough, **closure result**, or contradiction of established evidence must
receive independent `review-breakthrough` review at `max` effort. That review may not
be degraded or run on a backend that cannot reach it." A statement that an open
problem is settled in a named case is a closure result. `CLAUDE.md`'s model-policy
note says Claude Code cannot resolve those policy identifiers, and this task
requested `review-adversarial`, resolved to `claude-opus-5` — which is (i) not in the
task's `authorized_fallback_models` and (ii) **the same resolved model the executor
recorded**. So the batch has session independence but not model independence, and
rule 12 is unsatisfied for the closure claim.

`BATCH-003-OPENING.md`'s admission — "the independence in this batch is at the
**review** step, not at the production step, and no record here claims otherwise" —
is honest and adequate *for the production step*. It does not address the model-level
correlation at the review step, and no artifact in the snapshot does.

Separately, `manifest.yaml`'s `result.certificate.verifier` calls the dual classifier
one of "two independent verifications". The two classifiers share `s3_coeffs`, so
they are independent with respect to `CF-IMPL-FACTOR` (factorisation bugs) but **not**
with respect to `CF-NORM-S3` (a wrong `S_3` normalisation is invisible to both).
`CF-NORM-S3` is covered only by `CTRL-S3-IDENTITY`, which runs on **one curve per
prime** (`ref = rand_curves[0]`), i.e. 4 of 105 curves, and never on the CM or
automorphism panels. That is *sufficient* — `s3_coeffs` is curve-agnostic and three
point-addition identities pin a degree-2 polynomial up to scalar — but "independent
verifications" in a certificate slot is a term-of-art collision with
`docs/claims-and-verification.md`, where independence means *code independent of the
solver*, produced by a party that did not originate the claim.

**Cheapest thing an outside party could run to falsify the headline without trusting
this session at all.** Two computations, both under a minute, neither needing the
harness, the seeds, or the run record:

1. In any CAS: `expand(discriminant(S3(x1,x2,T), T) - 16*(x1^3+A*x1+B)*(x2^3+A*x2+B))`
   and check it is `0` in `Z[x1,x2,A,B]`. This settles the Lemma and hence Corollaries
   A–E in one line. (Integer-arithmetic equivalent, no CAS needed: evaluate the
   difference on the grid `[−3,3]^4`; the grid exceeds the total-degree bound so
   agreement is a proof.)
2. On one curve, enumerate all `p²` pairs and tabulate the cycle type with an
   independently written quadratic classifier; compare with `S² + N² − (p−Z)` split
   and `2SN` inert. **2.2 s at `p = 1601`** on one CPU core.

If both pass, the entire mathematical content of the batch is established without
reference to `RUN-MONO-4b50b6-001`. I ran both (§3).

**Disposition. UPHELD.** Either downgrade the wording ("an elementary derivation,
recorded at claim tier `toy`, that answers the `m = 3` case of `KN-OPEN-009`") so
rule 12 does not bind, or record rule 12 as unsatisfied and hold the closure. Do not
record a rule-12 review that was not obtained.

---

### O-12 — The "random ordinary controls" panel is a small-height box, not a random sample of curves (note, non-blocking)

**Claim attacked.** "80 random ordinary controls"; `execution_report.md` §1
reporting a range "across all 80 random controls".

**Why this may mislead.** The protocol's search box is `A ∈ [0, min(p−1,64)]`,
`B ∈ [1, min(p−1,64)]` — at `p = 1601` that is `65 × 64 = 4160` pairs out of
`1601² ≈ 2.6M`, i.e. **0.16%** of the curve space, all of tiny height. Any reading
of the panel as a *sample-based* generalisation to "generic ordinary curves" is
unsupported by the panel itself. The universality in Corollary D comes from the
identity, which is height-blind, so nothing in the package is actually wrong — but
the phrase "random ordinary controls" invites the sampling reading, and a successor
protocol that drops the identity would inherit a badly non-uniform panel.

**Cheapest falsification.** Re-draw 20 curves per prime with `A, B` uniform in
`[0, p−1]` and confirm identical behaviour. ~14 s. Corollary D predicts no change.

**Disposition. PARTIALLY UPHELD (note).** Record the panel's true support in the
evidence record's scope block.

---

### O-13 — Two arithmetic labels in the gate table (hand to the Validator, non-blocking)

1. `execution_report.md` gate table: "every control curve inside `3·(2/√p)` | yes,
   **worst case `Δ/envelope = 0.135`**". `0.1354` is `max delta_over_weil`, i.e.
   `Δ / (2/√p)`. `Δ/envelope = 0.1354/3 = 0.0451`. The margin against the envelope is
   **22.2×**, not the "never worse than 7×" stated two sections later (7.4× is the
   margin against the bare Weil floor). Both statements **understate** the margin, so
   this is conservative mislabelling, not overclaim — but the two figures in the same
   document are computed against different denominators without saying so.
2. `execution_report.md`: "cross-checked … **63 000 comparisons** in total". `105 ×
   600 = 63 000` is correct as a count, but `INSTRUMENT-DUAL-CLASSIFIER` gates on
   `rand_all + cm_all` only, i.e. `102 × 600 = 61 200`; the 3 quarantined
   automorphism curves are counted in the prose but not gated by the control. I
   verified all 105 curves have `secondary_classifier_mismatches == 0`, so the
   statement is factually true and the gate is merely narrower than the prose.

**Disposition. UPHELD (minor).** Arithmetic verification is `TASK-20260802-e2702a`'s
remit; flagged here because both are *reading* defects.

---

## 2. What I checked and did **not** sustain

Recorded so the Coordinator can see the objections that failed, not only those that
landed. Manufacturing objections to look thorough is itself a failure mode.

- **"The identity is wrong / normalisation-dependent."** WITHDRAWN. Proved over `Z`
  (§3, check 1).
- **"The closed form is a laundered version of the sampled census."** WITHDRAWN. The
  two are computed by genuinely different routes — `classify_primary` evaluates the
  actual polynomial; `exact_histogram` uses only `(Z, S, N)`. Their agreement is a
  real test of the Lemma. My exhaustive `p²` enumeration (a third route) also agrees.
- **"The CM screen was padded to clear the hard gate."** WITHDRAWN. The 22 scored
  curves are exactly the ordinary reductions predicted by `(D/p) = +1` at each prime
  (6+4+6+6), and `D = −11` is genuinely supersingular at all four (`(−11/p) = −1`
  each time), as the report states.
- **"The `j mod p` defect story is a cover for a leaked curve."** WITHDRAWN. The
  automorphism panel's 3 curves are exactly what supersingularity predicts
  (`j = 0` ordinary only at `p ≡ 1 mod 3`, i.e. 211; `j = 1728` ordinary only at
  `p ≡ 1 mod 4`, i.e. 809 and 1601). The defect and its disclosure are consistent and
  correctly reported as found-before-the-recorded-run.
- **"`confers no advantage over Pollard rho` is unjustified."** WITHDRAWN. No solve,
  relation, or algorithm is claimed; the certificate `kind: none` is correct under
  `docs/claims-and-verification.md`. See the baseline block below.
- **"The determinism claim is inflated."** WITHDRAWN. The scoped replay statement
  (one differing leaf, `wall_clock_seconds`) with the explicit retraction of an
  earlier unqualified draft is exactly the right shape.
- **"Premature closure — the lane is being declared dead too early."** WITHDRAWN **at
  `m = 3`**: this is a closure by proof, the strongest kind, with a named obstruction
  (degree 2 ⇒ only `S_2` or trivial; discriminant squarefree ⇒ not trivial). It is
  *not* a fatigue report. But see **O-1** and **O-9** for the forward-guidance gap.

---

## 3. Independent computations run for this review

All against the snapshot `fdb8ef8f` tree; none modified any producer artifact.

| # | check | result |
|---|---|---|
| 1 | `disc_T S_3 − 16 f(x1) f(x2)` on the grid `[−3,3]^4` (2401 points, exceeds the total-degree bound) + 20 000 random points in `[−500,500]^4` | **0 counterexamples — identity proved over `Z`** |
| 2 | True exhaustive `p²` enumeration with the discriminant+Legendre classifier, 12 curves (2 random + 1 CM at each of 211/431/809/1601) vs `exact_enumeration.counts` | **0 mismatches**, ramified strata `0/0/1254`, `0/0/2574`, `0/0/4842`, `0/0/9594` matched |
| 3 | Timing of check 2 at `p = 1601` | **2.2 s/curve** ⇒ all 105 curves `< 1000 s` vs a 7200 s budget |
| 4 | `delta_split_vs_S2 == (t²−2pZ+Z²−2p+2Z)/(2p²)` recomputed on all 105 curves | **0 mismatches**; panel maxima `0.9994 / 3.9941 / 3.9941` reproduced |
| 5 | `Z` stratification by panel | random `{0: 80}` (prime order forces `Z = 0`), CM `{3: 11, 0: 7, 1: 4}`, automorphism `{3: 2, 0: 1}` — consistent with Corollary C's three cases |
| 6 | `χ(f(x)) = +1` on every factor-base element; every off-diagonal FB pair classified | **1196 pairs, 0 non-split**; 2 elements with `χ = 0`, both `x = 0` on quarantined `j = 1728`, `B = 0` curves with `W_eff = 1` |
| 7 | Sampled vs closed-form relation ratio, 80 random curves | sampled `[0.0000, 10.98]` vs closed-form `[1.4897, 1.5102]`; 17/20 curves at `p = 1601` have **zero** joint hits |
| 8 | Sampled `p·|Δ|` maxima per prime | `1.625 / 3.074 / 7.443 / 10.833` vs exact `0.7275 / 0.9988 / 0.9994 / 0.9922` |
| 9 | Excursion needed to reach `EXCEPTIONAL_LOCUS_TOY` | `143 σ` at `p = 211`, `52 σ` at `p = 1601`; worst `exact|Δ|/envelope = 0.0416` over 105 curves |
| 10 | Window-control power | passes for `W_eff ∈ [0, 30]` at `p = 211` … `[0, 226]` at `p = 1601` |
| 11 | CM ordinary/SS split by `(D/p)` at each pinned prime | ordinary counts `6+4+6+6 = 22`; `D = −11` SS at all four |
| 12 | `m = 4` generalisation: `S_4 = Res_X(S_3(x1,x2,X), S_3(x3,T,X))` on `E/F_211`, `A=37,B=57`, 193 triples of rational `x`-coordinates | **193/193 split completely**, roots exactly `{x(±P1±P2±P3)}` |
| 13 | `sympy` availability | 1.14.0 importable; no `sympy` artifact in the snapshot |

---

## 4. Required output record

```yaml
red_team_report:
  id: RT-20260802-1b4130
  task_id: TASK-20260802-1b4130
  reviewed_snapshot: fdb8ef8fb8966dbf22d5c4457eaa37478e265284
  inference:
    requested_policy: review-adversarial
    resolved_model_id: claude-opus-5
    fallback_used: true
    fallback_note: >-
      claude-opus-5 is not in this task's authorized_fallback_models and is the
      same resolved model recorded by the executor in run_record.yaml. Session
      independence yes; model independence no. See O-11.
    model_verified: false
    independent_session: true
  claim_under_review: >-
    That RUN-MONO-4b50b6-001 closes the exceptional-locus question of KN-OPEN-009
    at m=3 unconditionally and at all primes (Corollary D); that the quasirandom
    independence model understates the m=3 joint relation proxy by a constant
    factor ~2 that moves no exponent (Corollary E); and that outcome_id
    FULL_MONODROMY_BARRIER_TOY is the supported reading at claim tier toy.
  objections:
    - id: O-1
      target: "Corollary D as the closure of KN-OPEN-009 at m=3"
      disposition: PARTIALLY_UPHELD
      blocking: false
      summary: >-
        Closure is valid but doubly mis-weighted. Understated: the geometric AND
        arithmetic monodromy group is provably the full S_2 for every non-singular
        E and every p>3 (16 f(x1) f(x2) is squarefree hence a non-square in
        k(x1,x2)); the package proves only the weaker density consequence.
        Overstated: a transitive degree-2 group is primitive, so the imprimitivity /
        block-system / resolvent-decomposition mechanism KN-OPEN-009 actually hunts
        cannot exist at m=3 for degree reasons. m=3 is the case where the question
        is degenerate, and the closure must say so.
      cheapest_falsification: "factor S_3 over GF(p)(x1,x2) on one curve; seconds"
    - id: O-2
      target: "outcome_id FULL_MONODROMY_BARRIER_TOY presented as the finding"
      disposition: UPHELD
      blocking: false
      summary: >-
        EXCEPTIONAL_LOCUS_TOY required a 52-143 sigma binomial excursion
        (P ~ 1e-500); worst exact|delta|/envelope over 105 curves is 0.0416. The
        mechanical outcome was determined before execution. Its content is
        instrument integrity, not monodromy evidence.
      cheapest_falsification: "exhibit any E/F_p with exact split density outside 1/2 +- 4/p"
    - id: O-3
      target: "'measured' applied to closed-form-derived quantities"
      disposition: UPHELD
      blocking: true
      summary: >-
        Sampled relation ratio is [0.0000, 10.98] (17/20 curves at p=1601 record
        zero joint hits); the reported [1.4897, 1.5102] is closed-form arithmetic.
        Sampled p*|delta| reaches 10.833 at p=1601; the reported 0.9994 is exact.
        manifest.yaml carries the derived range under summary_measurements.
      cheapest_falsification: "divide joint_relation_proxy_rate by quasirandom_relation_prediction in results.json"
    - id: O-4
      target: "sampled census credited with confirming the O(1/p) bound; 13.6s framed as efficiency"
      disposition: UPHELD
      blocking: false
      summary: >-
        sigma = 0.00289 exceeds the entire random-panel effect (<= 1/p <= 0.0047) at
        every pinned prime, so 30000 samples cannot resolve it. The independent
        route - exhaustive p^2 enumeration - costs 2.2 s/curve at p=1601 (~1000 s
        for all 105) against a 7200 s budget of which 13.6 s was used, and was
        replaced by the closed form under the field name exact_enumeration.
      cheapest_falsification: "run the p^2 enumeration; done here on 12 curves, 0 mismatches"
    - id: O-5
      target: "run_record closed_form_check and exact_deviation_bounds; manifest verifier clause (1)"
      disposition: UPHELD_ON_PROVENANCE_WITHDRAWN_ON_CORRECTNESS
      blocking: false
      summary: >-
        Neither computation exists in mono3_census.py nor in results.json; no
        analysis command is archived, yet the manifest offers it as one of two
        verifications standing in place of a certificate. Recomputed here: true,
        0 mismatches on 105 curves.
      cheapest_falsification: "recompute from results.json (p, trace_t, chi_counts.Z); done"
    - id: O-6
      target: "contract.md 'Verified symbolically (sympy.expand)' and 'checked numerically on every censused curve'"
      disposition: UPHELD_ON_PROVENANCE_WITHDRAWN_ON_CORRECTNESS
      blocking: false
      summary: >-
        Run declares stdlib-only dependencies; no sympy artifact in the snapshot;
        the harness performs no numerical check of the identity on any curve
        (sampled_vs_exact is a 4-sigma frequency agreement, not an identity check).
        Identity independently proved over Z here.
      cheapest_falsification: "grid [-3,3]^4 evaluation exceeds the degree bound; done, 0 counterexamples"
    - id: O-7
      target: "CTRL-NEG-UNIFORM-WINDOW and CTRL-NEG-SHUFFLED-WINDOW reported as pass"
      disposition: UPHELD
      blocking: false
      summary: >-
        Absolute tolerances 0.02 / 0.03 against expected rates of 3.6e-4 down to
        6.2e-6. The controls pass for any window from W_eff=0 up to W_eff=226 at
        p=1601. They cannot fail, and are recorded as passes beside controls that can.
      cheapest_falsification: "set fb_set = empty and re-run; both still pass. 14 s."
    - id: O-8
      target: "Corollary E: 'a constant factor, it moves no exponent'; the 1.5 headline"
      disposition: PARTIALLY_UPHELD
      blocking: false
      summary: >-
        Correct at fixed m, but stated unscoped. The exact factor is 2(1-1/W_eff):
        1.5 is a W_eff=4 artifact and the limit is 2, so ICEX must receive the
        formula, not the number. A per-fibre split factor compounds as 2^(n-1)
        across summands, which is not exponent-neutral in the n ~ log q regime.
        exact_joint hard-codes P(split | FB pair) = 1 - the field named
        ratio_measured_over_quasirandom has an assumed numerator; the premise is
        never checked per curve (I checked it: 1196 pairs, 0 non-split).
      cheapest_falsification: "classify every off-diagonal FB pair on every curve; done"
    - id: O-9
      target: "'Corollaries A-E are stated for m=3 only' (underclaim)"
      disposition: UPHELD
      blocking: false
      summary: >-
        Corollary E is not m=3-scoped. For any m, if x_1..x_{m-1} are x-coordinates
        of F_p-rational points then S_m(x_1..x_{m-1},T) splits COMPLETELY over F_p
        with roots x(+-P_1 +- ... +- P_{m-1}), by the group law. Verified at m=4 via
        S_4 = Res_X(S_3(x1,x2,X), S_3(x3,T,X)) on E/F_211: 193/193 triples split
        completely with the predicted root sets. Consequence: the relation-rate half
        of KN-OPEN-009 is answered at every m, and a generic-fibre Frobenius census
        measures a quantity that is identically trivial on the locus where relation
        search actually operates. That is forward guidance the closure owes.
      cheapest_falsification: "build S_4 by resultant at any toy p and factor it at rational x-coords; done"
    - id: O-10
      target: "icex_feed relation_rate_input for FULL_MONODROMY_BARRIER_TOY"
      disposition: UPHELD
      blocking: true
      summary: >-
        The run emitted exactly the outcome_id that activates a feed package whose
        prescribed relation_rate_input (chebotarev_S2_split * (W_eff/p)^2) this run
        refutes. The refutation exists only in execution_report prose; nothing
        machine-readable in results.json, manifest.yaml or GOAL-ICEX-001.next_action
        would stop a driver from ingesting it. Separately, that package's
        attack_content label 'closed_at_toy_scope' is weaker than what Corollary D
        proves (unconditional at m=3) and stronger than what the census showed (O-2).
      cheapest_falsification: "grep the snapshot for any machine-readable supersession flag; there is none"
    - id: O-11
      target: "'settles KN-OPEN-009 at m=3' vs AGENTS.md rule 12; certificate 'independent verifications'"
      disposition: UPHELD
      blocking: false
      summary: >-
        A closure result triggers rule 12 review-breakthrough at max, which this
        harness cannot resolve; and this red team's resolved model equals the
        executor's, so model independence is absent. Also, the two classifiers share
        s3_coeffs, so they are independent w.r.t. CF-IMPL-FACTOR but not w.r.t.
        CF-NORM-S3, which is covered only by CTRL-S3-IDENTITY on 4 of 105 curves
        (sufficient, since s3_coeffs is curve-agnostic, but not 'independent
        verification' in the docs/claims-and-verification.md sense).
      cheapest_falsification: "compare resolved_model_id in run_record.yaml with this report's header"
    - id: O-12
      target: "'80 random ordinary controls'"
      disposition: PARTIALLY_UPHELD
      blocking: false
      summary: >-
        The panel is drawn from A,B in [0,64], i.e. 0.16% of the curve space at
        p=1601, all of tiny height. Universality comes from the identity, not the
        panel; no reading may treat the panel as a uniform curve sample.
      cheapest_falsification: "re-draw with A,B uniform in [0,p-1]; ~14 s; Corollary D predicts no change"
    - id: O-13
      target: "gate-table ratio labels and the 63 000-comparison figure"
      disposition: UPHELD
      blocking: false
      summary: >-
        'worst case delta/envelope = 0.135' is actually delta/weil-floor;
        delta/envelope = 0.0451 and the envelope margin is 22.2x, not the 7.4x
        quoted later against the bare floor. Both understate the margin. The 63 000
        cross-check count includes 3 quarantined curves the control does not gate on
        (61 200); all 105 are in fact mismatch-free.
      cheapest_falsification: "divide max delta_over_weil by 3"
  required_controls:
    - "Exhaustive p^2 enumeration by the independent classifier on every censused curve (~1000 s of a 7200 s budget), replacing the closed form as the exactness reference."
    - "Per-curve assertion that chi(f(x)) = +1 for every factor-base element, and a guard against a 2-torsion generator collapsing W_eff to 1."
    - "Relative-tolerance replacement for CTRL-NEG-UNIFORM-WINDOW and CTRL-NEG-SHUFFLED-WINDOW (e.g. |rate/expected - 1| <= 0.25), or a larger W."
    - "Null-object control for the census as a whole: run the identical histogram against a random quadratic family a(x1,x2)T^2 + b T + c with a,b,c uniform, and confirm it also lands at 1/2 - which it will, demonstrating that split frequency near 1/2 discriminates nothing at degree 2."
    - "A higher-sample census (>= 360 000 samples/curve) if the sampled statistic is ever to carry the O(1/p) claim itself rather than defer to enumeration."
  counterexample_or_mutation: >-
    Setting fb_set = set() in census_curve leaves CTRL-NEG-UNIFORM-WINDOW and
    CTRL-NEG-SHUFFLED-WINDOW passing, which demonstrates those two controls have no
    power at the pinned primes. No mutation was found that breaks the Lemma,
    Corollaries A-D, or the closed-form histogram; three independent routes
    (polynomial classifier by sampling, closed form, exhaustive p^2 enumeration)
    agree on all 12 curves tested exhaustively and all 105 curves statistically.
  baseline_comparison: >-
    No solve, relation, or algorithm is claimed, so certificate kind 'none' is
    correct. Stated positively for the record: at p=1601 Pollard rho costs ~sqrt(p)
    ~ 40 group operations and BSGS ~ 40 operations with ~40 memory; this run
    performed 3 150 000 fibre classifications and solved no discrete logarithm.
    The closest specialized baseline, Semaev/Gaudry-Diem summation-polynomial index
    calculus, does not apply to prime fields at all. Therefore
    dominated_by MUST NOT be null in any downstream record: the relation-rate
    correction attaches to no algorithm and is dominated on every axis (time,
    memory, data) by rho and BSGS. The correction's honest value is that it removes
    a factor-2 pessimism from a planning model, and per O-8 it must be handed on as
    2(1 - 1/W_eff) with its m-scope attached.
  heuristic_challenges:
    - "No numbered heuristics are asserted, and none is needed: Corollaries A-D are unconditional given Hasse and non-singularity. The package correctly does NOT dress an unconditional result as heuristic-conditional, nor the reverse."
    - "The one place a random model is implicitly invoked is the protocol's quasirandom relation prediction, and Corollary E's whole content is that the random model does not transfer to the structured object (factor-base elements are x-coordinates of rational points, not uniform field elements). That is the correct random-model-transfer critique, made by the producer against its own protocol; O-9 is that it transfers further than claimed."
    - "The 3*(2/sqrt p) envelope is correctly and repeatedly labelled a protocol pin rather than a theorem, satisfying CTRL-CLAIM-WORDING and CF-ENVELOPE-OVERREAD."
  cost_model_challenges:
    - "13.6 s against a 7200 s budget is not efficiency to be celebrated; it is 500x unspent headroom that should have bought the independent exhaustive enumeration (O-4)."
    - "The closed form eliminates the p^2 census dimension. Its own cost - the O(p) character table - IS charged inside the run, so KN-LIT-7593 is satisfied on that axis. What is not charged is the verification cost of the identity the elimination rests on (O-5, O-6)."
    - "Memory is stated as un-measured rather than estimated as a number, which is the correct disclosure."
  reduction_and_scope_challenges:
    - "The m=3 -> m>=4 boundary is correctly held for Corollaries A-D and incorrectly held for Corollary E (O-9)."
    - "No cited external reduction is instantiated by this run. KN-LIT-039 (Chebotarev) is invoked only for the 1/2 prediction and is correctly the only theorem-backed portion; at m=3 Corollary B supersedes it with an exact equality, which the contract states."
    - "Affected-vs-safe scope: no scheme is named as affected or safe, correctly, because no attack is claimed. Scope is NOT inflated anywhere in the package."
  proof_architecture_challenges:
    - "Observation-fiber attack: holding the invariant (exact split density) fixed and varying the curve cannot place two preimages on opposite sides of the conclusion, because the density is a function of (t, Z) alone and both are bounded. The invariant is not lossy for this question - which is exactly why the m=3 case is degenerate (O-1)."
    - "Quantifier-order: 'for every E, for every p, |density - 1/2| < 4/p' is the correct order and is what the identity gives. No witness is chosen after seeing an instance."
    - "Method ceiling: the largest claim the degree-2 discriminant method can support is the m=3 case. It reaches the headline exactly and no further, and the package says so."
    - "Nearby-object control: the closest object for which the desired conclusion is false is the m>=4 cover, where deg_T = 2^(m-2) >= 4 and the discriminant does not factor. The package names it as out of scope. The genuinely missing nearby-object control is the null quadratic family (see required_controls) which would show that split frequency ~ 1/2 discriminates nothing at degree 2."
  narrowest_supported_statement: >-
    As a polynomial identity in Z[x1,x2,A,B], disc_T S_3(x1,x2,T) = 16 f(x1) f(x2)
    with f(x) = x^3 + A x + B. Consequently, for every non-singular E: y^2 = f(x)
    over F_p with p > 3, unconditionally and independently of any census:
    (i) the geometric and arithmetic monodromy groups of the degree-2 m=3 Semaev
    summation cover are the full S_2, with no exceptional locus - and being of
    degree 2 the group admits no non-trivial block system, so no imprimitivity or
    resolvent-decomposition phenomenon exists at m=3;
    (ii) the exact density of split fibres over F_p^2 is
    1/2 + (t^2 - 2pZ + Z^2 - 2p + 2Z)/(2p^2), whence |density - 1/2| < 4/p uniformly
    (< 1/p when Z = 0, as holds for every prime-order curve);
    (iii) on the sublocus where x1, x2 are x-coordinates of F_p-rational points the
    fibre splits with probability 1, by closure of E(F_p) under addition - and this
    holds at every m, where S_m splits completely into 2^(m-2) linear factors.
    RUN-MONO-4b50b6-001 at p in {211,431,809,1601} with 30000 samples/curve is
    consistent with (i)-(iii) and constitutes an instrument-integrity check, not
    independent evidence, because its sampling noise (sigma = 0.00289) exceeds the
    entire predicted random-panel deviation (<= 1/p <= 0.0047) at every pinned prime.
    Nothing here bears on m >= 4 monodromy, on crypto-scale ECDLP, or on any attack
    advantage over Pollard rho or BSGS. Largest prime tested is 1601 (11 bits).
  next_concrete_action: >-
    Before TASK-20260802-32e4bf writes the evidence and decision records, the
    Coordinator must discharge the two blocking objections: (O-3) strike the word
    'measured' from every closed-form-derived quantity, in particular remove
    relation_proxy_ratio_over_quasirandom [1.4897, 1.5102] from
    manifest-level summary_measurements semantics via a superseding correction
    record; and (O-10) write a superseding correction naming
    icex_feed.outcome_packages[FULL_MONODROMY_BARRIER_TOY].relation_rate_input as
    refuted, supplying 2(1 - 1/W_eff) with its m-scope, and referencing it from
    GOAL-ICEX-001.next_action so the consuming driver cannot miss it. Record O-1's
    group-theoretic statement and O-9's all-m generalisation in the evidence record
    and the KN-OPEN-009 successor, since both are free strengthenings the package
    currently leaves on the table.
  artifact_paths:
    - coordination/goals/GOAL-MONO-001/batches/BATCH-003/reviews/TASK-20260802-1b4130/red_team_report.md
  verdict: ADMIT_WITH_CORRECTION
```

---

## 5. Verdict

**`ADMIT_WITH_CORRECTION`.**

The run is admissible. Its mathematics is correct and I reproduced it by three
independent routes. It is honest about its claim tier, about `m ≥ 4`, about
crypto-scale, about the envelope not being a theorem, about a defect it found in
itself, and about the one leaf that differed on replay. That is a better-than-usual
integrity record and I am not going to pretend otherwise.

But it must not be propagated as written. Two corrections are **blocking**:

1. **O-3** — closed-form quantities are labelled "measured", and the specific number
   `[1.4897, 1.5102]` sits in `summary_measurements` while the frozen protocol's
   sampled census gives `[0.0000, 10.98]` for the same thing.
2. **O-10** — the `icex_feed` package this outcome activates prescribes a
   `relation_rate_input` the run refutes, and the refutation is prose-only.

Eleven further corrections and notes are listed above; **O-1** and **O-9** are the
two the program should care about most, because both are cases where the package is
*weaker* than what it has actually proved, and one of them (**O-9**) casts a real
question over the value of the `m ≥ 4` continuation that `GOAL-MONO-001` is
otherwise headed toward.

Finally, on record: this report was produced by `claude-opus-5`, the same resolved
model that produced the run. It establishes session independence, not model
independence, and it cannot discharge `AGENTS.md` rule 12 for a closure claim
(**O-11**).
