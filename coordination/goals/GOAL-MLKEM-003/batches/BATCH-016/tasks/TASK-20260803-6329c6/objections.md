# Objections — TASK-20260803-6329c6

Red team, BATCH-016, GOAL-MLKEM-003, EXP-MLKEM-011.
Reviewing snapshot `18e6679ba0` / ledger `405e19415b`.
Verdict: **blocking_objections**.

Toy tier. Two archived toy-dimension files. No ML-KEM security claim in either
direction. AGENTS.md rule 12 stays UNMET and UNWAIVED. Zero new sampling of the
physical system: no G6K, no network, no new `.out` bytes. All seeded randomness
is `random.Random(20260803)`, used only for synthetic null objects and one
drift-power calibration, and is never reported as a measurement of the archived
system.

---

## Summary of the two rulings

**Identical distribution: SURVIVES.** I was asked to build the strongest case
that it fails. I could not build one, and I say so plainly. The archive
supports it better than the task card believed, because the task card's premise
was wrong: the archive *does* contain per-iteration data.

**Mid-band lane: NOT EXHAUSTED.** One sub-lane inside it is exhausted, with a
named obstruction sharper than the one the task card offered. But the lane
itself is not, because the discriminating information lives in the occupancy
*structure* of the existing 301 bins rather than in their number — and using
that structure decides the batch's central question outright, in about twelve
seconds of pure Python.

**And the batch's central question comes out against the batch.** BATCH-015's
conclusion — ANOM-5 is not an effect — survives. Its *mechanism* does not. The
occupancy floor does not explain the n=43 mid-band deficit, and the archive
says so at three standard deviations using data BATCH-015 already had in hand.

---

## 1. The premise I was handed is false, and correcting it is what saves the
## i.i.d. assumption

The handoff, and `EV-MLKEM-ce1884`'s boundaries paragraph, both state that "the
archive contains no per-iteration data with which to verify it."

Read the first seventeen lines of
`experiments/EXP-MLKEM-011/vendor-lock/data/Pgood_q241_m40_n43_nfft8_kfft3_nlat35_beta032_beta144_N25971.out`:

```
# nb_iteration=4000
#  Each Line is a value for F(solution)
```

followed by 4000 value lines. That is per-iteration data, in iteration order,
for the n=43 configuration. What the archive lacks is per-iteration data for
the two **Pwrong** files. The distinction matters, and BATCH-015 knew it —
`anom5_investigation.py` lines 873–917 (`pgood_serial_probe`) exist precisely to
exploit it, and their output is in `results.json` under
`iteration_sequence_probe_pgood`. The evidence record then wrote the boundary as
though that probe had not happened.

I read that probe's code before summarising it, as bound. It computes lag-1..8
autocorrelation of the standardised sequence, a runs test about the mean, and
block-mean variance ratios `sb^2 * B / sd^2` for B = 2..100, which under i.i.d.
sampling should each sit at 1. The archived readings:

| statistic | reading | reference |
|---|---|---|
| lag-1..8 autocorrelation | max abs 0.035 | sd 0.0158 |
| runs test about the mean | z = −0.214 | — |
| block-mean variance ratio, B = 2..100 | 0.893 … 1.228 | 1.000 |

A null result is only worth what its power is worth, so I calibrated it
(seed 20260803, 4000 values, 120 replicates per amplitude, 400 for the null):

| linear drift, total amplitude | mean B=100 ratio | z |
|---|---|---|
| null (no drift) | 0.993 | — (sd 0.228) |
| 0.10 sd | 1.093 | +0.44 |
| 0.20 sd | 1.294 | +1.32 |
| **0.25 sd** | **1.531** | **+2.35** |
| 0.30 sd | 1.759 | +3.36 |
| 0.50 sd | 3.116 | +9.30 |

So the archived probe excludes, at better than 2 sd, any monotone drift in
`F(solution)` of total amplitude above 0.25 sd across the run — 3.6 % of the
mean, since `sd/mean = 0.1435`. That is a quantified bound, not an absence of
looking.

Three further things close the i.i.d. attack:

- **A varying lattice does not break identical distribution.** The headers
  report `sdv_dlat = 1.125372` (n=43) and `1.739062` (n=50), and the Pwrong
  header says "each time a different lattice, target". A fresh redraw per
  iteration makes the per-iteration *marginal* identical by construction; the
  heterogeneity is integrated into that marginal. Non-identity requires the
  iteration *index* to carry information, which is what the drift probe tests.
- **The differing `nb_iteration` (4000 vs 6000) implies nothing about
  within-file homogeneity.** These are different instances entirely — n=43,
  n_lat=35, β₀=32, β₁=44 versus n=50, n_lat=42, β₀=35, β₁=41 — not two halves
  of one run.
- **Unequal-weight pooling of sub-runs is excluded** by BATCH-015's own format
  test T2: `"%.18e" % (count / (nb_iteration * q**k_fft))` reproduces the
  printed string bit-for-bit on 1804 and 2311 lines with zero mismatches. Each
  file is an equally weighted pooled count over exactly `nb_iteration`
  iterations.

None of this is an accusation retracted or made. It is a statement about what
the archive can support, and the archive supports identical distribution better
than the record credits it.

## 2. But identical distribution was never the load-bearing assumption

Here is the algebra that should have stopped this line of inquiry before it was
commissioned.

For independent `X_i ~ Poisson(λ_i)`, `Var(Σ X_i) = Σ λ_i = μ` for **any**
heterogeneous, index-dependent, deterministic `λ_i`. The dispersion is exactly
1 regardless. Non-identical distribution cannot produce a sub-floor reading in
the Poisson regime at all.

The validator's `φ = 0.00433` counterexample — `⌊μ⌋` deterministic iterations
plus one `Bernoulli(frac)` — lives entirely inside the **0/1 regime**, where
`Var(X_i) = p_i(1 − p_i)` and concentrating the `p_i` toward 0 and 1 destroys
variance. It is a correct refutation of the "any independent-iteration model"
quantifier (`U-2`), and that correction stands and must be carried forward. But
it is *not* evidence that identical distribution is the fragile hypothesis. The
fragile hypothesis is the one that puts us in the 0/1 regime in the first
place, and BATCH-015 never wrote it down as an assumption.

## 3. The assumption that is actually load-bearing

`floors()` at `anom5_investigation.py` lines 547–549 states it in an annotation
field:

```
attained_when = "each iteration contributes at most one candidate score
                 to each cell -- the minimum-variance member of the
                 independent-iteration family"
```

`mean_T(1 − μ_T/N) = 0.9183` is the *minimum over the family*, attained only by
that member. `U-1` and `U-4` then promote the minimum to the **reference
point** — "the admissible dispersion floor is 0.9183 … rather than the Poisson
point 1.0", "the honest residue is −1.4 to −1.6 sd". That is a third statement,
and the quantifier audit that BATCH-015 ran on `U-2` should have been run on it
too:

1. `∀` i.i.d. iteration models, `E[φ] ≥ floor` — **true**, it is a bound.
2. `∃` an i.i.d. model attaining the floor — **true**, the 0/1 member.
3. The observed process **is** that member — neither implied nor checked.

Statement 3 is what a residue of −1.4 sd silently assumes. The Coordinator's
`U-3` error was confirming a claim by sharing its blind spot; this is the same
blind spot one step later.

Two independent lines dispose of statement 3.

### 3a. It is structurally implausible

Each iteration emits `q^k_fft = 241³ = 13,997,521` candidate scores. From the
archived counts (my recomputation, archived bytes only):

- n=43 places **24.6047** mid-band candidates per iteration across 301 cells,
  and `Σ_T p_T² = 8.578`, so a Poisson-per-cell allocation expects **4.29
  colliding pairs per iteration**. The 0/1 property would have to be violated
  several times per iteration and is not.
- In the *same file's* shallow band, a single iteration deposits up to **49,036
  candidates on one score** (max increment 196,143,254 over 4000 iterations).
  Multiple occupancy of one cell by one iteration is a demonstrated property of
  this process, not a hypothetical.

### 3b. It is rejected by the archive at ≥ 3 sd — the cheapest check

The floor member makes a prediction the Poisson member does not. If the 0/1
member generated the data, the per-cell Pearson term obeys
`E[t_T] = 1 − μ_T/N`, so the regression of `t_T` on per-iteration occupancy has
slope **exactly −1**, and the deficit must concentrate where occupancy is
largest. Under Poisson the slope is 0 and the deficit is occupancy-flat.

That is the protocol's own §3 test: *name the parameter that is supposed to
destroy the signal, and say what the measurement should look like as it
increases*. Occupancy is that parameter, and it varies by a factor of 250 —
0.0029 to 0.739 — **inside the existing 301 bins**.

I reused BATCH-015's estimator deliberately, so that the per-cell terms are the
same object the producer summed. It reproduces `φ(n43, mid) =
0.8022946873653165` and `floor = 0.9182566445182725` to all printed digits.
**That reproduction is not an independent check and I do not offer it as one** —
it is the same route by construction. The new content is the decomposition.

n=43 mid band, terciles by per-iteration occupancy (nulls: 400 replicates,
seed 20260803, identical instrument, identical fitted μ, identical band, so
leverage and edge asymmetry are present in the null and cancel):

| tercile | mean occupancy | observed φ | N1 Poisson null | N2 floor-member null |
|---|---|---|---|---|
| low  | 0.00454 | **0.6371** | 1.0072 ± 0.1451 | 0.9971 ± 0.1430 |
| mid  | 0.01839 | 0.8645 | 1.0121 ± 0.1344 | 0.9783 ± 0.1499 |
| high | 0.22091 | 0.9043 | 1.0021 ± 0.1390 | **0.7802 ± 0.1145** |

Read the two ends. In the **low**-occupancy third the two nulls are
indistinguishable (1.007 vs 0.997): the floor buys nothing there, and the
observation sits **−2.55 sd below both**. In the **high**-occupancy third,
where the floor buys everything it has (1.002 vs 0.780), the observation sits
−0.71 sd below Poisson and **+1.08 sd above the floor**.

The deficit is entirely inside the cells where the floor correction is 0.5 %,
and absent from the cells where it is 22 %. The floor moves the reference in
the part of the band that does not contain the deficit.

The slope statistic says the same thing with a pre-specified target, since −1
is fixed by the floor's own algebra and is not a fitted quantity:

| file | observed slope | N1 Poisson null | N2 floor-member null | z vs floor member |
|---|---|---|---|---|
| n=43 | +0.1972 | −0.0329 ± 0.5478 | −0.9671 ± 0.3365 | **+3.46** (+3.15 after lag-1 deflation) |
| n=50 | +1.5114 | +0.1249 ± 1.2397 | −0.9296 ± 1.2033 | +2.03 |

The instrument recovers 0 under Poisson and −1 under the floor member, as it
must — that is the null-object control on my own statistic, without which the
slope reading would be uncontrolled and I would not be entitled to it.

The n=43 deflation applies validator defect D-9: residual lag-1 autocorrelation
is +0.104, so the independent-cell null sd is optimistic by about
`sqrt(1 + 2×0.104) = 1.10`. I quote the deflated figure. The n=50 lag-1 is
+0.007, no material deflation. Both files point the same way.

**Cheapest check that settles it:** refit the archived degree-5 model on scores
551–851 of the n=43 file, keep the 301 per-cell terms
`t_T = (D_T − μ_T)² / (μ_T (1 − h_T))` instead of only their mean, regress them
on `μ_T/4000`, and calibrate with the producer's own N1 and N2 generators at
the same μ. About twelve seconds of pure Python; no new sampling; every input
already in the archive.

### 3c. Why the whole-band mean could never have decided this

The two candidate objects are separated on the whole-band scalar by only
`(1.0071 − 0.9181)/0.0808 = 1.10 sd`. On the occupancy slope they are separated
by `(−0.0329 − (−0.9671))/0.3365 = 2.78 sd`. That is a textbook observation
collision (proof-architecture audit 2): the observable used cannot identify
which object generated the data, so moving the reference between the two was
always going to look like it settled the question without settling it. The
condition that breaks the collision is per-cell occupancy — exactly what the
whole-band mean discards. This was findable before any compute.

## 4. Two further reasons the floor cannot carry the conclusion

**It is more volatile than the statistic it references.** Over BATCH-015's own
`mid_band_edge_shift_sweep` the floor moves 0.9183 → 0.8318 → 0.6815 → 0.3332
while φ moves 0.8023 → 0.8445 → 0.8826 → 1.0272, and the reported residue
swings from −1.63 sd to +10.16 sd. A reference point that moves further than
the measurement cannot carry a 0.1-sized correction. The wide rows are also the
floor applied where per-iteration occupancy exceeds 1: `band_shift_sweep`
(lines 824–845) calls `floors()` but emits only `floor_independent_iterations`
and **drops** `floor_independent_iterations_applicable`, the flag that would
have marked those rows invalid. Validator D-6 caught the prose symptom; this is
the code-level cause, and it is a two-line fix.

**It needs two mechanisms for one statistic on one pipeline.** Against the
floor, n=43 sits −1.38 sd *below* it and n=50 sits +2.19 sd *above* it. So
`U-1` explains n=43 by the file sitting at its minimum-variance floor while
`U-6` explains n=50 by an unrelated over-dispersion mechanism. Against a single
Poisson reference the readings are −2.36 and +1.68 — symmetric noise. Nothing
about n=43 → n=50 is a parameter that should flip the sign of a real
sub-Poisson mechanism, and a quantity that changes sign when the instance
changes is the artifact tell, not the effect.

## 5. What survives, said plainly

The lane has produced adverse readings repeatedly and I am not going to pretend
everything here is broken. Standing:

- **`U-2` and `U-3` stand.** The "any independent-iteration model" quantifier
  is false, the correction to i.i.d. is right, and recording the Coordinator's
  faulty confirmation was the right call. That correction is the most valuable
  thing in BATCH-015 and nothing here touches it.
- **`U-4`'s mathematics stands.** `mean_T(1 − μ_T/N)` is a valid lower bound
  over i.i.d. iterations and is exactly attained by the 0/1 member.
- **The admissible-set argument stands.** The admissible set is
  `[floor, ∞)`, so φ = 0.8023 does not by itself falsify the i.i.d.-iteration
  family. That is a real and useful negative.
- **`U-5` stands untouched.** At occupancy 0.00226 and 0.00113 the floor and
  the Poisson point differ by 2.6e−4 and 1.4e−4, far below sds of 0.05–0.15.
  BATCH-014's deep-tail T-1 is unaffected by everything above.
- **`ANOM-5 is not an effect` stands** — on independent grounds that need no
  floor at all: |z| = 2.36 among six post-hoc-selected region-by-file readings
  is Šidák p = 0.105; the rate-model-order range across degrees 2–5 is 0.43,
  five times the floor correction of 0.082; and the two files disagree in sign.
- **Scope is not inflated.** Toy tier, ML-KEM and Kyber cost figures explicitly
  disclaimed, rule 12 kept unmet and unwaived. Verified, not contested.
- **`dominated_by: null` is correctly justified**, with a stated basis and a
  zero `sota_delta`, on a batch that claims no time, memory, data or query
  quantity. That is a checked null under inventor-protocol §5, not the
  unchecked null that would be a rule 5 fabrication. Recorded as verified
  rather than silently passed.
- **The degree choice is legitimate.** I raised and retired an objection here:
  `anom5_investigation.py` hardcodes `5 if n43 else 3` as a bare literal, but
  BATCH-014's `results.json` shows those are its forward-selection choices on
  the deviance at `χ²_{1,0.95} = 3.841`, with ranges over converged degrees at
  or above chosen of 0.7998–0.8106 and 1.0870–1.1065. The gap is traceability,
  not correctness.

Not standing: that 0.9183 is the operative reference; that the honest residue
is −1.4 to −1.6 sd; and that ANOM-5 is dissolved *because of* the floor.

## 6. Exhaustion ruling

### The sub-lane that IS exhausted

Resolving the **whole-band** mid-band dispersion ratio against any fixed point
reference to 3 sd is exhausted, and the obstruction is sharper than "301 bins
is fewer than 1321".

The mid-band cell count is `K = ln(100)/a`, where `a = 0.01530` per score is
the log-decay rate of the survival curve and the band is the fixed two-decade
window `1000 ≤ C_T < 1e5`. **`a` is a property of the physical instance, not of
the archive size.** Increasing `nb_iteration` translates the count window to
deeper scores without widening it: more iterations buy no mid-band bins at all.
This is the part the "1321–1488 bins vs 301" framing hides — it reads as an
expensive-but-feasible path, and the path does not exist.

The other routes are closed too. The score observable is integer-valued at unit
granularity (`gcd` of positive increments = 1, minimum mid-band increment 6),
and BATCH-014's expected-count binner already returns one bin per score — 301
bins over 301 scores (`U-10`) — so there is no re-binning, re-weighting or
re-fitting freedom left. I recompute the requirement as
`K = (1.4534/(0.1160/3))² = 1414` from `sd·√K = 1.4534` at K = 301, consistent
with the validator's honest 1321–1488 range (D-8). Reaching 1414 bins needs a
count dynamic range of `e^(1414 × 0.01530) = 2.4e9`, i.e. **9.4 decades**,
essentially the entire resolved band [0, 1802] — and that route is closed by
the floor's own domain, since the sweep already reports floor = 0.3332 at
[476, 926] where occupancy exceeds 1 and
`floor_independent_iterations_applicable` is False.

**Forward guidance:** a 3 sd whole-band reading is obtainable only from an
instance with a smaller decay rate `a` — a flatter survival curve — not from
more iterations at q = 241, m = 40, n = 43. Anyone who wants it must change the
parameter regime, and must first say what a mid-band dispersion ratio at that
regime would decide. Declaring that closed is a result, and I declare it.

### The lane that is NOT exhausted

Closing the mid-band lane on the bin count would be the premature closure the
protocol treats as equal to overclaiming, because the bin count was never the
binding constraint on the question that mattered. Five things remain available
at 301 bins:

- **R-1 — the occupancy-signature test.** Executed above. Decisive, ≥ 3 sd,
  twelve seconds, no new sampling. It was available to BATCH-015 throughout.
- **R-2 — occupancy-matched cross-region comparison.** The deep tail
  (occupancy 0.00226) and the mid band's low-occupancy tercile (0.00454) are
  nearly occupancy-matched. Deep tail reads φ = 1.0569 against its archived
  Poisson null 0.9965 ± 0.0591; the tercile reads 0.6371 against 1.0072 ±
  0.1451. They differ by **+2.68 sd at matched occupancy**. Any occupancy-driven
  mechanism requires them to agree. Not done.
- **R-3 — joint two-file test with sign as the discriminator.** −2.45 and
  +1.66 on the same statistic, same pipeline. Not done as a joint test.
- **R-4 — the shallow band as a direct measurement of the within-iteration
  dispersion index.** At per-iteration occupancy 12,676 (n=43) and 10,966
  (n=50), φ reads 1.0462 ± 0.0613 and 1.0909 ± 0.0571. That is a measurement of
  exactly the quantity the floor sets to `(1 − p)`, sitting in the producer's
  own `results.json`, never used for that purpose.
- **R-5 — a model-selection-free reading.** φ moves 1.2370 → 0.9067 → 0.8727 →
  0.8023 across degrees 2–5 while the floor is invariant at 0.9182566 to seven
  digits. The rate-model order is a five-times-larger lever on this statistic
  than the entire floor correction. The producer's second-difference statistic
  (0.6741, identity check 0.6780) is one such reading and never reached the
  conclusion.

## 7. A binding I must restate correctly rather than apply mechanically

The `DEC-20260803-52a750` binding attaches to the **whole-band rms ratio** of
log2 residuals, whose effective degrees of freedom are **O(1)** — published
defensible range **1.51–2.35** across conventions, and restricting to
`count ≥ 1000` **buys no degrees of freedom**, being the same O(1) family —
because `Cov(C_T, C_T′) = min(λ_T, λ_T′)` makes the cumulative residual
covariance nearly rank one.

φ is a **different statistic**. It is built on the **increments** `D_T`, not
the cumulative counts, and its residual lag-1 autocorrelation is +0.104 (n=43)
and +0.007 (n=50). Its effective dof is of order K, not O(1), and its analytic
sd of about `√(2/K)` is approximately right. Conflating the two in either
direction would be an error and I make neither: I do not import the O(1) dof
onto φ, and I do not let φ's near-independence leak back onto the rms ratio.

I make no new fit-dependence inference, so I run no new bias-versus-centred-
scatter decomposition; `U-8`'s decomposition and its "unresolved under both
fits" qualification are not contested here.

## 8. Next concrete action

Supersede observation `U-1` of `EV-MLKEM-ce1884` (the record is
`status: draft`) with a corrected observation that:

1. keeps the floor as a lower bound and keeps the admissible-set argument;
2. drops "the honest residue is −1.4 to −1.6 sd" and the framing of 0.9183 as
   the reference point, citing the occupancy-signature rejection at ≥ 3 sd;
3. restates the surviving conclusion "ANOM-5 is not an effect" on the
   multiplicity, model-order and sign-disagreement grounds, which need no
   floor;
4. corrects the boundaries paragraph to say "no per-iteration **Pwrong**
   data", with the Pgood drift-power bound attached.

No new sampling is required for any of this, and no further batch is needed to
decide the floor question. It is decided.

---

### Reproduction

Both computations in this report run against the archived bytes only. The
estimator is BATCH-015's, reused deliberately (`glm`, `phi_of`, `floors` from
`anom5_investigation.py`), which is why the φ and floor reproductions are *not*
offered as independent checks. The null generators are the producer's `N1`
(`poisson_sample`) and `N2` (`binomial_sample` at `Binomial(nb, μ/nb)`), seeded
`random.Random(20260803)`, 400 replicates for n=43 and 250 for n=50. The
drift-power calibration is 400 null replicates plus 120 per drift amplitude at
the same seed.

### Read, and not read

Read: all three `.out` files; `anom5_investigation.py` (`glm`, `phi_of`,
`floors`, `second_difference_statistic`, `local_block_phi`, `band_shift_sweep`,
`pgood_serial_probe`, the region plan); BATCH-015 `results.json`; BATCH-014
`results.json` and its degree-selection code; `EV-MLKEM-ce1884`;
`docs/inventor-protocol.md`.

Not read, and therefore not summarised: `make_bins_from_observed` in the
BATCH-014 control (the `U-10` item). I make no statement about it, and nothing
here depends on it. BATCH-015's validation report was consulted only through
`EV-MLKEM-ce1884`'s D-1…D-9 summaries; every validator number I quote (D-6,
D-8, D-9) is one I independently recomputed or located in the producer's own
`results.json`.
