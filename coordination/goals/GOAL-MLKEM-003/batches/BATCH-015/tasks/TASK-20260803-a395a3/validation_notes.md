# TASK-20260803-a395a3 — validation notes

VAL-20260803-6c8f13. Independent validation of the TASK-20260803-d9afbd ANOM-5
investigation package, as committed in Coordinator snapshot **18e6679ba0**
(archive task TASK-20260803-f7700a).

Toy tier (q=241, m=40, n=43 and n=50), resolved band, raw undivided score
scale. **No ML-KEM or Kyber claim in either direction.** AGENTS.md rule 12
stays UNMET and UNWAIVED; EV-MLKEM-011, EV-MLKEM-013 and EV-MLKEM-017 keep
their status; KN-FIND-031 stays withdrawn. Nothing was edited, repaired or
committed.

**Verdict: ADMISSIBLE_WITH_DEFECTS** (schema verdict `passed`), nine numbered
defects, two of them material to sentences the Coordinator has already
elevated into the snapshot headline.

---

## 0. What I did, and what I did not do

Everything in Job A was recomputed from a **validator-written implementation**
that imports nothing from `anom5_investigation.py`,
`dispersion_control_c1.py` or `exact_region_measure.py`: ingest and exact
decimal integer recovery, the region rule, the Chebyshev basis, the
Fisher-scoring Poisson GLM, the leverage, the leverage-corrected Pearson
dispersion and its analytic sd, autocorrelation, the runs test, the local-block
estimator, exact-Binomial and Poisson samplers, the truncated-Poisson counting
floor, and BATCH-014's `make_bins_from_observed`.

Job B was checked by recomputing every per-band rms **directly from the
archived `residuals_bits` arrays** against index sets I derived myself from the
raw counts, with an independently written counting floor.

Seeded randomness, disclosed: **77777** for my null objects (3000 replicates,
against the producer's 600 at seed 20260803), **9091** for the power check,
**4242** for the counterexample in §1. **Zero new sampling of the physical
system** — no G6K, no network, no new `.out` bytes; the three archived files
were read and their digests are unchanged.

What I did *not* do: reimplement BATCH-012's model machinery (Upsilon tables,
u-quadrature, `d_lsc` mixture, kernel). That the archived residuals reproduce
BATCH-012's archived rms *exactly* on each fit's own index set is strong
evidence they are residuals of the archived models, but it is not an
independent check of BATCH-012's model code.

Snapshot integrity: commit `18e6679ba0` is reachable from HEAD, its parent is
`b7bea56a` — exactly the commit `results.json → provenance.git_commit`
declares — and it changes four paths (the three artifacts plus the
Coordinator's own receipt). All three digests match the receipt in both the
commit object and the tree. The disclosed `__pycache__` side-effect write was
genuinely reverted: BATCH-012, BATCH-014 and `experiments/EXP-MLKEM-011` are
clean and all five declared input digests match.

---

## 1. The floor argument — the number is right, the theorem is not

This is the whole batch, so I re-derived it rather than confirming it.

**The number.** The n=43 mid-band floor `0.9182566445182725` reproduces three
ways: from the fitted rates, from the observed increments, and in closed form
as `1 − (ΣD/K)/N = 1 − (98419/301)/4000`. Occupancy `max μ_T/N = 0.739178`,
`K = 301`, `N = 4000` all reproduce. The n=50 floor `0.966992607526882 =
1 − (98230/496)/6000` likewise. The deep-tail floors `0.9997379074658249` and
`0.9998595076400688` likewise.

**The theorem.** The stated chain is

```
Var(X_iT) >= E[X] - E[X]^2 = p_i(1 - p_i)                      # correct
Var(D_T)  >= mu_T - sum_i p_i^2                                # correct
"Cauchy-Schwarz: sum_i p_i^2 >= (sum_i p_i)^2 / N"
          >= mu_T (1 - mu_T / N)                               # DOES NOT FOLLOW
```

The last step needs `Σp_i² ≤ μ²/N`. Cauchy–Schwarz gives the **opposite**,
`Σp_i² ≥ μ²/N`, which turns the inequality around: `μ − Σp_i² ≤ μ(1 − μ/N)`.
The cited lemma refutes the line it is cited for.

So "under **any** model with independent iterations, `E[φ] ≥ floor`" is false.
Counterexample, run through my instrument: let `⌊μ_T⌋` iterations contribute 1
deterministically and one further iteration contribute `Bernoulli(frac(μ_T))`,
the rest 0. Iterations are independent, every `X_iT` is a non-negative
integer, `E[D_T] = μ_T`, and `Var(D_T) = frac(1−frac) ≤ 1/4`. Through the
identical instrument that null returns **φ = 0.00433 ± 0.00039** — about 2300
standard deviations below the claimed floor.

**What survives, and it is nearly everything.** The missing hypothesis is
*identical distribution*. If the iterations are independent **and identically
distributed** — which the file header supports ("each time a different lattice,
target"), and which the pooled-rate estimator already assumes — then
`p_i = μ_T/N` for every `i`, the Cauchy–Schwarz step becomes an equality, and
`Var(D_T) ≥ μ_T(1 − μ_T/N)` holds with equality iff each iteration contributes
0 or 1. Note also that a *mixture* across iterations (M-a3) does **not** break
it: each iteration's marginal law is still the same mixture.

**Is it the tightest?** Yes — under the corrected hypothesis it is not merely
*a* bound, it is exactly the minimum. The general minimum-variance law for a
non-negative-integer summand with mean `p` is the two-point law on
`{⌊p⌋, ⌈p⌉}`, with variance `frac(p)(1 − frac(p))`. I evaluated the resulting
exact floor cell by cell over the n=43 mid band and it coincides with
`(1/K)Σ(1 − μ_T/N)` to `<1e-12`, because every occupancy there is `≤ 0.739 ≤ 1`.
`N2 = Binomial(N, μ_T/N)` is its exact minimiser, and the fitted instrument
attains it: my own N2 mean is **0.918627**, sitting on the analytic floor
0.9182566. There is no room for a tighter floor inside the class.

**Consequence for the residue.** My 3000-replicate nulls give
N1 = 0.997997 ± 0.083206 (z = −2.352) and N2 = 0.918627 ± 0.076419
(z = −1.522), against the producer's 1.002495 ± 0.081643 (z = −2.452) and
0.915333 ± 0.078946 (z = −1.432). Both agree within Monte-Carlo noise. **The
honest residue is −1.4 to −1.6 sd, and the producer's central finding stands.**
Calibrating a statistic pooled over 4000 iterations against the Poisson point 1
in a region of occupancy 0.739 was the wrong reference, and most of ANOM-5
dissolves. That is a real result and I say so plainly.

**Required correction (D-1, D-2).** State the iid/exchangeability hypothesis as
a hypothesis and drop the Cauchy–Schwarz sentence. This also relocates M-a4:
stratified or proportional allocation across iterations typically preserves
*independence* and breaks *identical distribution*, and by the counterexample
above that alone suffices to breach the floor. The mechanism the producer named
is right; the assumption it breaks is not. The Coordinator's snapshot message
repeats the same over-general claim ("under ANY independent-iteration model"),
so the re-derivation recorded there did not catch it either.

---

## 2. The deep tail — the Poisson null survives, decisively

Occupancy there is 0.0022610 (n=43) and 0.0011349 (n=50); floors 0.99974 and
0.99986 at one bin per score. I also checked the correction under BATCH-014's
*coarser* instrument, since that is where its reading lives: aggregating the
deep tail to observed count ≥ 10 gives ~80 and ~85 bins with mean bin counts
12.5 and 11.7, so the binned floor is 0.9969 and 0.9981 and the worst single
bin is 0.9945 — against a measurement sd of 0.05–0.15. The null moves by at
most 0.3% of one sd.

**BATCH-014's T-1 is untouched by this batch.** What it loses is the ANOM-5
bound EV-MLKEM-c50030 attached to it, not its own reading.

---

## 3. M-a4 — a control was available and was not used

The producer calls M-a4 (shared random source / antithetic / stratification
across iterations) untestable from this archive, having established correctly
that no per-iteration `Pwrong` data exists anywhere in the repository (I
checked: three `.out` files, no other per-iteration artefact). The *general*
statement is right, but a useful partial test was sitting in the same
`results.json`.

Any cross-iteration mechanism that scales the per-cell variance by a **uniform**
factor `c` must show that same `c` wherever the Poisson null is correct.
Explaining the mid band needs `c = 0.80229/0.91826 = 0.8737`. The deep tail,
through this task's own instrument and its own calibrated nulls, reads

| file | deep-tail φ | its N1 null | z against c = 0.8737 |
|---|---|---|---|
| n=43 | 1.05687 | 0.99649 ± 0.05913 | **+3.10** |
| n=50 | 1.02709 | 0.99825 ± 0.04779 | **+3.21** |

and further still if the null's sd is scaled by `c` too. So the **uniform** form
of M-a4 is disfavoured at about 3 sd in each file. It does not touch an
*occupancy-selective* mechanism — one acting only where `μ_T/N` is O(1) — which
remains untestable here. Note the control must be quoted with its instrument:
BATCH-014's *binned* deep tail (0.8954 against 0.98496 ± 0.15424) has no power
to make it.

"Untestable" should become "not decidable in general; the uniform form is
disfavoured at ~3 sd by the deep tail; the occupancy-selective form is not
testable here". This narrows the open item rather than closing it.

---

## 4. Job B — the reconstruction holds, the inference from it does not

**It holds, completely.** All 24 fits × 5 index sets per file recompute from
the archived `residuals_bits` to a worst deviation of **2.6e-10 bits**; the
`rms_difference_from_archived_bits` is exactly 0.0 on all 48 rows; my
independent truncated-Poisson counting floors reproduce all ten values to
`0.0e0`; index-set sizes (1803/1493/852/551/951 and 2310/1969/1132/636/1178)
reproduce; the BATCH-014 two-fit values and `reconstruction_valid` flags read
back from the BATCH-014 archive and match. Rows BATCH-014 called valid land
within 0.1–1% of the single-fit value; rows it flagged move by up to 0.47 in
ratio. **The flags were right and the residual archive delivers the
checkability it promises.** The n=43 M1a headline — 0.7974 whole-band against
2.3938 at C ≥ 1000 — reproduces exactly.

**The inference is the problem (D-4).** For M1a *both fits share the shape
parameter* (p = 26.0) and I find their residuals differ by a **rigid constant
of 0.826803 bits at every score with `C_T < 1000`** (constant to 1e-9).
Decomposing the deep-tail rms into a bias (mean residual) and a centred
scatter:

| model (n=43) | whole: ratio / bias / centred | C≥1000: ratio / bias / centred |
|---|---|---|
| M1a (p=26 both) | 0.7974 / −0.264 / **0.5656** | 2.3938 / −1.090 / **0.5656** |
| M4 (exact both) | 0.6183 / −0.031 / **0.6148** | 0.6766 / −0.133 / **0.6148** |
| SENS (exact both) | 0.6155 / −0.014 / **0.6148** | 0.6285 / −0.061 / **0.6148** |
| M2 (exact both) | 0.7697 / +0.021 / 0.7684 | 0.7733 / +0.048 / 0.7666 |
| M1 (p=23 vs 20) | 0.8366 / +0.054 / 0.8287 | 3.3897 / +1.436 / 1.4502 |
| M3 (s=.97 vs .9) | 0.8951 / +0.089 / 0.8748 | 2.3460 / +0.961 / 1.1405 |

n=50 shows the same pattern (M1a 0.5187 centred under both fits; M4 and SENS
0.5193 both). So what is fit-dependent is a **normalisation bias**; the
**scatter** deficit is fit-*independent* for four of six models and stays below
the counting floor under both fits. Only M1 and M3 — where the shape parameter
itself changed — have genuinely fit-dependent scatter.

The producer's sentence, which the Coordinator promoted to consequence 3 of the
snapshot headline, therefore does not hold for M1a: the ratio moves, the
deficit does not.

**The binding, and the stronger qualification.** Per DEC-20260803-52a750: the
effective number of degrees of freedom of a whole-band ratio is **O(1)**; I
quote no single value; the published defensible range across conventions is
**1.51–2.35**; and **restricting to C ≥ 1000 buys no degrees of freedom** —
that ratio's effective dof is also O(1) and lies inside the same 1.51–2.35
family. At O(1) dof, neither 0.57 nor 2.39 is resolved from 1.0. The correct
qualification of BATCH-012's standing claim is therefore that **the deep-tail
ratio is unresolved under both fits** — which is fit-independent, does not
depend on choosing a normalisation, and qualifies the claim at least as
strongly as the sentence the producer wrote.

---

## 5. The n=50 over-dispersion — real arithmetic, weak as an anomaly

The correction moves n=50's mid band from +1.66 sd (vs N1) to +2.25 sd (vs N2);
my own nulls give +1.69 and +2.31. The arithmetic is right, and recording the
symmetric consequence rather than only the favourable half was the correct and
honest thing to do.

It should not be promoted to a new anomaly of the same kind. (i) The admissible
set is `[floor, ∞)`: over-dispersion has no upper bound to violate, so +2.25 sd
*above* a floor is categorically weaker evidence than any amount *below* one.
(ii) A mechanism is already in the producer's own table — M-a3, a mixture
across iterations, which can only inflate — and the archived `Pgood` file shows
a 14.35% coefficient of variation in the per-iteration score scale, exactly the
ingredient such a mixture needs. (iii) It is the largest of six region readings
across two files; two-sided p = 0.024 becomes ≈0.15 after that multiplicity.
A genuine open item, correctly labelled, and not evidence of anything yet.

---

## 6. The excluded mechanisms, audited

**Format (M-b1, M-b2) — genuinely excluded.** I reproduce every number: max
`|value·M − round|` in exact 80-digit decimal 1.538512138e-06 (n=43) and
2.3189886448e-06 (n=50) against a 0.5 margin; **0** printf round-trip
mismatches over 1804 and 2311 value lines; a single field width (24); 0
non-monotone steps; gcd of positive increments 1 (and 1 again within the mid
band alone); mid-band minimum increment 6, zero zero-increments. The 1.5e-6
residual is exactly the double round-trip of `count/M` (`2⁻⁵³ × 2.8e10 ≈ 3e-6`),
which is what a lossless dump should show. The two tests are independent and
jointly decisive: T1 pins the integer uniquely, T2 shows the printed string is
that integer's representation.

**Estimator arithmetic (M-c1) — genuinely excluded.** My third implementation
returns `0.8022946873653165` bit-for-bit, leverage summing to
6.000000000000016 against the parameter count 6, max leverage 0.19030848. The
degree sweep reproduces to every printed digit (1.237, 0.907, 0.873, 0.802,
0.805, 0.806, 0.808, 0.811, 0.806, 0.803, 0.800), and my own local-block
estimator gives 0.7244–0.7875, i.e. *lower*, as reported.

**Binning (M-c2) — genuinely excluded, and the degeneracy claim is correct.** I
reimplemented `make_bins_from_observed` from BATCH-014's source: it returns
**297 bins over 301 scores** in the n=43 mid band, because only 4 of the 301
increments are below 10 and the minimum is 6. BATCH-014's congenial 0.8008
therefore tests almost nothing there. The real exclusion — that the
expected-count binner returns 301 bins over 301 scores, minimum fitted rate
11.67 > 10 — is correct. **Second congenial control in two batches that does
not survive reading its code: confirmed.**

**Second-difference identity (M-x2).** I re-derived
`E[(r_{i−1} − 2r_i + r_{i+1})²] = v(6 − 8ρ₁ + 2ρ₂)` from scratch (diagonal
1+4+1, cross terms −8ρ₁+2ρ₂) and evaluated it: `0.8022947 × (6 − 8(0.1039564) +
2(−0.0489311))/6 = 0.677974` against the measured 0.674118. Declining to report
0.674 as a separate, larger deficit was correct; it would have been double
counting.

**Pgood probe (M-a4 indirect).** Fully reproduced from the raw file: mean
11983.505, sd 1720.086, CV 0.143538, r₁…r₈, runs z = −0.2138 and all nine
block-mean variance ratios identical. The header discrepancy that bounds the
probe is confirmed (`avg_dlat` 41.071674 vs the Pwrong header's 41.068986). The
producer's characterisation — weak evidence, not exclusion — is right.

**Handoff reconciliation.** Honest and accurate on every line. "0.9923" and
"0.0806" occur nowhere in BATCH-014's `results.json`. `−2.359958` is exactly
the archived *analytic* z against the point null; the archived MC z is
−2.288175. For n=50 the archived readings are +1.616147 and +1.888619, and
+1.55 matches neither. The archived degree sweep carries `n_parameters` 2…13,
with no 33-parameter fit. **No verdict in the package depends on the handoff's
bad numbers** — every mechanism verdict is computed from the archived bytes,
and the handoff values are carried in a comparison-only block.

**Three claims that do not reproduce**, all minor and none carrying a verdict:

- **D-5.** Report §2.4: "in the n=50 mid band the binner does merge — 475 bins
  over 496 scores". BATCH-014's `control_observed_count_binning` returns
  **470** there (archived value 470; my reimplementation also 470). 475 is the
  *expected-count* binner's count. Report prose only.
- **D-6.** M-c5's "the gap below the floor stays inside about 1.5 sd
  everywhere" is contradicted by the sweep it summarises, which contains
  −1.635, +2.778 and +10.163 sd (n=43) and +10.509 (n=50). The defensible
  statement is that the gap never falls more than ~1.6 sd *below* the floor.
- **D-7.** Deviation 3 names the multinomial floor (0.9991) as binding in the
  shallow band. Within the independent-iteration class the correct floor there
  is `N·frac(p)(1−frac(p))/μ` summed over cells = **1.04e-2**. The multinomial
  floor belongs to a strictly stronger model. Nothing depends on it — that band
  reads over-dispersed at 1.046 — and reporting the degenerate −12675 openly
  with `applicable: false` was exactly right.

**D-8**, minor: "roughly 1409 bins" uses `sd² ≈ 2/K`; the measured N2 sd gives
1321 and the analytic sd 1488. Quote it as "about four times the available 301".

**D-9**, scope: the mid-band residuals carry ρ₁ = +0.104, which inflates the
true sampling sd of a mean of squares by ~1.5% over the independence-based sd
used in both nulls, so |z| is marginally optimistic. Immaterial.

---

## 7. Controls, per `docs/inventor-protocol.md` §3

- **Positive control passes.** N3 injects φ = 1.5; the producer recovers
  1.49753 ± 0.11665 and I recover 1.49781 ± 0.12296 with my own sampler and
  seed, separating from N2 by 4.7 sd. The instrument is not blind.
- **Null object of the same shape: satisfied**, and this is the batch's
  principal merit. Two nulls are run through the *identical* instrument rather
  than compared against an analytic point.
- **Decay control: satisfied and explicitly stated.** The parameter meant to
  destroy the effect is per-iteration occupancy. The report says the floor
  bites only where occupancy is O(1), and the deficit does vanish where
  occupancy falls to 0.0023. The canonical artifact tell — a quantity that
  fails to decay — is absent.
- **The producer's own controls are audited to the same standard**:
  `phi_leverage_le_0p5` drops zero bins and is flagged `vacuous: true` rather
  than quoted; the plug-in-λ control is recorded as a failure mode. Right
  discipline.
- **Missing control:** the deep-tail negative control on M-a4 (§3).

---

## 8. Single-sentence answer to the completion gate

**ANOM-5 is the estimator — specifically its null object, not its arithmetic —
with an unresolved residue in the data of about 1.5 sd that this archive cannot
decide.** Format is excluded decisively; estimator arithmetic is excluded by
three agreeing implementations; the reference point was wrong wherever
per-iteration occupancy is O(1); and what remains is a −1.4 to −1.6 sd sub-floor
gap and a +0.104 lag-1 residual autocorrelation, neither excluded and neither
resolvable at 301 bins.

## 9. What this validation does not support

Admissibility of a receipt, and nothing more. No ML-KEM or Kyber security claim
in either direction; no validation or refutation of Approximation 4.9; no
speedup; no hypothesis-status change, promotion or knowledge entry; and no
relief from AGENTS.md rule 12, which stays UNMET and UNWAIVED. Before D-1 and
D-4 are corrected, the floor theorem's quantifier and the Job-B fit-dependence
sentence must not be carried into an evidence record or a decision.
