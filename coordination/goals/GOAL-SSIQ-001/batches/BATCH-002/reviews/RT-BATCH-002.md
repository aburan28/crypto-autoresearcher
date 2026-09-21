# RT-BATCH-002 — Red Team review of GOAL-SSIQ-001 BATCH-002

**Task:** `TASK-20260805-538c72` · **Goal:** `GOAL-SSIQ-001` · **Batch:** `BATCH-002`
**Role:** red-team · **Compute performed:** none. No experiment was run, no dataset was
re-fetched, no fit was recomputed. Every number attributed to the run is copied from the
committed artifacts; every number I derive is arithmetic on quantities those artifacts
already report, is labelled `derivation`, and is reproducible in three lines by hand.

**Artifacts attacked (both Coordinator-committed; verified reachable from `HEAD` `6a629be7`,
`git status --porcelain` empty at review time):**

| package | snapshot commit | contents |
|---|---|---|
| `experiments/EXP-SSIQ-4de240/runs/RUN-SSIQ-4de240-a/` | `41a4aebd` | `manifest.yaml`, `raw-result.json`, `execution_report.yaml`, `source_access_log.yaml`, `stdout.txt`, `stderr.txt` (+ `implementation/fit_delta_counting.py`) |
| `coordination/.../BATCH-002/tasks/TASK-20260805-c89efb/` | `948c9aee` | `cascade_cost_note.md`, `extractor_unblock_log.md`, `source_access_log.yaml`, `task_report.yaml` |

**Division of labour respected.** The re-fit, the receipt/hash verification, and the
estimator-bias experiment belong to the Validator (`TASK-20260805-79e700`) and are not
duplicated here. I attack **interpretation and scope**: what the reported numbers license,
what the controls could have shown, what the cascade reading does and does not change, and
what a checkpoint will take away from this batch if nobody stops it.

---

## 0. Inference and the independence cap — stated before any finding

```yaml
inference:
  requested_policy: review-adversarial
  policy_binding_per_adapter: "anthropic:claude-opus-5 (effort=xhigh)"
  resolved_model_id: claude-opus-5
  resolved_model_provenance: >-
    Self-reported by this Claude Code subagent session. NOT probe-verified;
    `orchestration.adapter doctor --probe` was not run.
  model_verified: false
  fallback_used: true
  fallback_reason: >-
    Subagent frontmatter under this runtime cannot express a policy (CLAUDE.md,
    "Model policy note"); this session runs `model: inherit`. The resolved model
    coincides with the adapter's binding for review-adversarial, but the xhigh
    reasoning-effort component is neither settable nor verifiable from inside a
    subagent. Recorded as satisfied-by-coincidence, not as resolved.
  degraded_allowed: false
  degraded_requirements: ["reasoning_effort=xhigh not assertable or verifiable under this runtime"]
  independent_session: true
  independence_kind: session
  runs_authorized_note: >-
    The dispatch queue card sets runs_authorized: 0; the embedded handoff sets
    budget.maximum_runs: 1. I took the binding reading (0) and performed no compute.
    The inconsistency is recorded for the Coordinator, not treated as authorisation.
```

**Did REC-1's external data lift the cap? Partially, asymmetrically, and not on the
question the cap was about.**

- **It did lift it for the setup.** Two facts computed by other people could have
  contradicted this program's reading of the object and did not: `N(1,p) = h(−4p)/2` at
  **5377/5377** primes, and `max δ_E ≤ ⌊(p/2)^{1/3}⌋` at **5379/5379** primes with 119
  attaining the bound. Those are genuine external confirmations that `δ_E` *is* the
  quantity D1 counts and that the normalisation is right. That is real and it is more
  than any amount of same-model re-derivation could have produced.
- **It did not lift it for D1.** The primary metric returned nothing usable, so on
  ingredient (c) — the one confound BATCH-001 could not touch — the external data
  delivered exactly zero. D1 remains a single derivation-tier pillar checked only by one
  model, which is where BATCH-001 left it.
- **It did deliver one thing nobody planned:** a decisive negative about the *instrument*,
  with a quantitative reason (§1). That is an honest closure of a lane, not a fatigue
  report, and it is worth recording as such.

---

## 1. FRONT 1 — Was REC-1 right, and what did it buy?

**Answer in one line: the recommendation was right in strategy and wrong in instrument;
the contract hardened my error into a pre-registered tolerance; the execution was
exemplary. I had every input needed to foresee the instrument failure, and the check I
failed to run is the one I myself prescribed in `RT-BATCH-001` §5 control 2.**

### 1.1 Not the execution

The executor obtained external data, verified both anchors exactly, reproduced the
coefficient digest bit-identically, disclosed three aborted launches, disclosed a
data-look before fixing a check (D6), disclosed a publisher-side selection that moves
`alpha` by 0.102 (D3), refused to invent a threshold for an exploratory arm (D4), and
**self-reported the estimator bias that voids its own headline**. Nothing here is an
execution failure. I attacked D2's counting-unit conversion and it holds: the
`⌊p/12⌋ + e` reconstruction matches at 5379/5379 primes, which a wrong Galois-orbit
conversion cannot do.

### 1.2 What a value below both models means — and which explanation is right

The candidate explanations named in the task, adjudicated:

**E1 — finite-`T` truncation / pre-asymptotic saturation. THIS IS THE ANSWER, and it is
quantitative, not a hedge.**

Two facts fix the counting function's endpoints, and both are verified in this run:

- `fraction(1, p) = N(1,p)/(p/12) = 12·h(−4p)/(2p)`. By Dirichlet's class-number formula
  `h(−4p) = 2√p·L(1,χ_{−4p})/π`, so **`fraction(1,p) = (12/π)·L/√p ≈ 3.82·L/√p`**.
- `fraction(T, p) = 1` at `T = (p/2)^{1/3}`, verified with 0 violations in 5379 primes.

Therefore the **mean log-log slope of `fraction` over the whole admissible `T` range is
pinned**, with no fit and no estimator (`derivation`, `L = 1`):

```
s(p) = ln(1/fraction(1,p)) / ln((p/2)^{1/3}) = (1.5·ln p − 4.02) / (ln p − 0.693)
s(1009) = 1.02      s(22000) = 1.18      s(265207) = 1.25
s(p) − 3/2 = −2.98 / (ln p − 0.693)          ← the deficit is Θ(1/log p)
```

The deficit is not noise and not a model error: it is the constant `12L/π` in the small-`T`
anchor, which is negligible only when `ln p ≫ 6`. At `log₂ p = 18` it eats a quarter of the
exponent. And it decays as slowly as anything can — **`|s − 3/2| ≤ 0.20` first requires
`log₂ p ≳ 22.5`; `≤ 0.05` requires `log₂ p ≈ 87`; at `log₂ p = 256` the residual is 0.017.**

Now compare the pinned values with what was actually fitted, per block, from
`raw-result.json robustness_observations`:

| block | primes | fitted `alpha` | pinned `s(p)` over that block |
|---|---|---|---|
| complete coverage, `1009 ≤ p ≤ 21997` | 2296 | **1.0817** | 1.02 → 1.18 |
| sieve-selected, `p ≥ 22273` | 2915 | **1.1835** | 1.18 → 1.25 |
| pooled W-MAIN | 5211 | **1.1661** | 1.02 → 1.25 |

Every fitted value lands inside the range the two anchors pin for its own primes. The
same mechanism predicts the `beta` excess (`+0.089` in **both** data and null, U4): with
`alpha` forced constant while the true finite-size slope rises with `p`, the residual
`p`-dependence has nowhere to go but `beta`. One mechanism, four symptoms, all
quantitative. This is not "most likely"; it is the explanation that also predicts the
null's measured `−0.3638` bias and the block-to-block ordering.

**E2 — the counting unit.** Measured and excluded as the cause: the order-type unit gives
1.0664, the curve unit 1.1661 — a 0.10 shift, real but a fifth of the deficit — and the
curve unit is the one D1's ingredient (e) requires and the one verified exactly.

**E3 — the surrogate's own asymptotics not reached.** Not a competing explanation: it is
E1 observed on a known-truth object, and that is precisely what makes E1 *measured* rather
than argued.

**E4 — the model is wrong in a way neither candidate captures (true asymptotic `alpha ≈ 1.17`).**
Excluded by the run's own anchors: `s(p) → 3/2` is forced as `p → ∞` by the two verified
endpoints, so no asymptotic exponent below 3/2 is available. A genuinely smaller asymptotic
exponent would in any case make D1's upper bound *conservative* and L1's closure
*stronger*, not weaker.

**What would separate them, if anyone still doubts:** re-fit in the scaling variable
`x = T/(p/2)^{1/3}`, restricted to `x ≤ x_cut`, sweeping `x_cut ∈ {0.5, 0.3, 0.2, 0.15, 0.1}`,
and require the bias measured **on the α = 3/2 null** to decay monotonically toward 0 as
`x_cut` falls. It must, because the first-moment regime is exact as `x → 0`. If it does
not decay, the surrogate or the code is wrong and nothing measured is believable. That is
the `docs/inventor-protocol.md` §3 decay test applied to the instrument instead of to the
object, and it is the only form in which any further fitting should be attempted.

### 1.3 Was the recommendation wrong, the contract wrong, or the execution wrong?

- **Recommendation: right in strategy, wrong in one asserted claim.** The rationale —
  external data fails differently from same-model re-derivation — stands and was partly
  vindicated (§0). But `RT-BATCH-001` §7 asserted "`α = 3/2` versus `α = 2` is a large,
  easily separated difference over `T ∈ [1,30]`" **with no calculation behind the word
  "easily"**. Both of my predicted numbers come from an asymptotic formula whose range of
  validity I never checked. That is a method-ceiling audit (`docs/inventor-protocol.md` §8
  audit 4) applied to a measurement, and I skipped it in my own recommendation while
  demanding it of producers.
- **Could I have foreseen it? Yes, with the five lines in §1.2, from two facts already in
  this repository** — Dirichlet's formula and Theorem 1.5's bound. Worse: `RT-BATCH-001`
  §5 required control 2 is exactly the small-`T` endpoint check, and §2.3 already observed
  that D1 is "pinned at both `log_p T = 0` and `log_p T = 1/3`". I had the pinning
  argument, wrote it down, and did not turn it on the instrument I was proposing.
- **Contract: wrong on four separable points**, of which three are mine by inheritance —
  a pre-registered ±0.20 tolerance on an uncalibrated estimator (O22); a null control whose
  failure condition was the outcome D1 predicts (O23); no numeric tolerance for
  "reproduces c" (O25); and a sensitivity window (`p ≥ 10000`) that tests the axis that
  did not matter while pooling across the axis that did (O28).
- **Execution: not wrong.** See §1.1.

### 1.4 The one thing this refuses to be filed as

**"The data was uninformative" is false, and the campaign may not record it.** Three things
are now known that were not known before the batch:

1. The instrument was out of range **by a computable amount** (§1.2), so no measurement of
   this exponent on `log₂ p ≤ 18` data could have discriminated, whatever the estimator's
   variance said.
2. **The frozen competing model was refutable at zero compute** from two facts already in
   the repository (O27). A global `T²p^{−1/2}` law anchored at `T = 1` saturates at
   `T = p^{1/4}/1.95 ≈ 11.6` at `p = 265207`; the data carries curves at
   `⌊(p/2)^{1/3}⌋ ≈ 50` at 119 primes, with a largest shortfall of 5 anywhere. That is a
   factor-4 contradiction in `T`, from the run's own C-ANCHOR-HIGH tail check.
3. **The dataset never samples the regime the lever lives in** (O21). At the lever's
   operating point `T = p^{1/4}`, the scaling variable is
   `x = p^{1/4}/(p/2)^{1/3} = 2^{1/3}p^{−1/12}`: **0.708 at `p = 1009`, 0.548 at 22000,
   0.445 at 265207 — and 2^{−21} at `log₂ p = 256`.** Every prime in this dataset puts the
   decision point in saturation; at cryptographic scale it sits deep in the first-moment
   regime. The two are different regimes of the same function, and the toy data samples the
   wrong one. This is a far sharper statement of the scale gap than "sub-toy" and it should
   replace it in every downstream citation.

The honest headline for this batch is: **the instrument was mis-specified, the mis-specification
is now quantified in closed form, and the batch's controls carry more information than its
primary metric.**

---

## 2. FRONT 2 — The C-NULL failure

### 2.1 (a) No arithmetic, or a blind estimator? **A blind estimator — and this is proved inside the run.**

`N(1,p) = h(−4p)/2` holds **exactly** at 5377/5377 primes. That is arithmetic information
carried by the counting function, at a precision (exact integer identity, thousands of
independent instances) that no generic lattice ensemble reproduces. The arithmetic is
present and externally verified. What is void is a **three-parameter power-law summary's**
ability to see it. The executor states this ("the fit is blind to the structure, not the
data") and I confirm it without reservation.

**A better null, named as required.** Compare the *fluctuation*, not the coefficients:
plot `N(1,p)·p^{−1/2}` across `p` for data and surrogate. The data's spread is the
`L(1,χ_{−4p})` class-number fluctuation — a wide, arithmetically structured band; the
surrogate's is binomial sampling noise around a fixed mean, which is narrow. A variance
ratio, or a two-sample KS test on the whole `δ_E` distribution at fixed `p`, would have
discriminated where three fitted coefficients could not. **Caveat, and it matters:** such a
control would establish that the measurement sees *some* arithmetic; it would **not** make
the fit a test of D1, because the arithmetic it would see is the `T = 1` class-number
identity, not ingredient (c). C-NULL's purpose and the experiment's purpose are different
questions, and passing the former never validates the latter.

### 2.2 (b) Is D1 merely re-deriving lattice geometry? **Yes — and the answer to "strengthen or weaken" is: both, in separable directions.**

First, the mechanical reason C-NULL could not have passed. The surrogate shares **both**
endpoints with the real object:

- **Top end:** Hermite for rank 3 gives `min ≤ γ₃·det^{1/3} = 2^{1/3}(p/4)^{1/3} = (p/2)^{1/3}` —
  *the same bound with the same constant as Theorem 1.5*, which is exactly what BATCH-001's
  Validator found when it reproduced Theorem 1.5's constant from the trace-zero lattice.
- **Bottom end:** the determinant is matched to `p/4` (mean ratio 0.999987 over the 5211
  W-MAIN primes), which fixes the `p^{−1/2}` scale of `fraction(1)`.

With both endpoints shared and the interior pinned between them, agreement in `alpha`,
`beta` **and** `c` was structurally forced. C-NULL as written demanded that the data
*differ* from the surrogate in `beta` and `c` — i.e. it required the data to violate D1's
own prediction in order for D1's metric to survive. **The control's failure condition was
the outcome D1 predicts.** I predicted the match in `RT-BATCH-001` §5 control 1 and wrote
that a match is "a controlled null, not a finding"; the contract converted that predicted
outcome into a voiding condition. That conversion is the defect (O23, O24), and it is the
one place where my own recommendation and the contract diverged and the contract was worse.

Now the deep question:

- **It strengthens the closure's *robustness*, weakly and uncalibratedly.** If Gross
  lattices were anomalously short-vector-rich, D1 would fail in the dangerous direction and
  L1's disjunct 2 would reopen. The data tracking a structure-free ensemble of the same rank
  and determinant across all three fitted coefficients is (weak) evidence against such an
  anomaly at these `p`. **Magnitude: negligible.** The estimator carries a −0.36 bias against
  a 0.5 model gap, and no calibration exists that would tell us what an anomalous ensemble
  would have returned in this same window. It may not be cited as support, and the contract
  forbids citing it — rightly, though for the wrong reason.
- **It weakens the closure's claim to arithmetic depth, and that is the useful half.** If L1
  is closed because the governing object is *generic*, then the closure's content is: **no
  arithmetic conspiracy makes the Gross lattice's minimum smaller than `1/rank` of its
  discriminant.** That is a real, named obstruction with an argument and forward guidance, so
  it meets the `docs/inventor-protocol.md` §4 closure standard — I checked the closure as
  hard as I check claims, and it holds. But its scope is now visible with unusual clarity:
  **the closure covers exactly those objects whose governing lattice is generic of
  determinant ≍ p.** It says nothing about an object with a different rank, a different
  homogeneity degree of the degree form, or a normalised determinant below `p^{3/4}`. That is
  precisely N5, and it is precisely why `CLOSED-IN-SCOPE` was the right token in BATCH-001.
  This batch sharpens the scope string; it does not move the verdict.

**Net:** L1's state is unchanged. Its evidential tier is unchanged (single derivation-tier
pillar, one model). What changed is that the campaign now knows *why* the lever is closed —
genericity — and therefore where a lever could still live.

### 2.3 (c) The unstated tolerance — **yes, it is load-bearing, and I say so despite endorsing the choice**

The contract fixed no numeric tolerance for "reproduces … c". The producer chose
`|Δ| ≤ 0.20` on exponents (the contract's own model tolerance) and a factor of 2 on `c`,
disclosed the choice, and recorded the raw numbers so it can be re-read. Under that
criterion the null reproduces by wide margins: `Δalpha = 0.0299`, `Δbeta = 0.0060`,
`c`-ratio 1.017.

**Now the attack.** The natural alternative scale is the surrogate's own variability: the
three-seed range on `alpha` is **0.000554**. Against that scale, `Δalpha = 0.0299` is
**54 σ** and the null plainly does **not** reproduce the data — C-NULL would **PASS**, and
the primary metric would **not** be void. Two defensible tolerances, opposite verdicts, on a
contract that fixed neither. The producer's own boundary note ("it would take a tolerance
below 0.030 on alpha … to flip it") understates this: a *statistically* motivated tolerance
is two orders of magnitude below 0.030, so the flip is not a knife-edge, it is a different
question being asked.

**Which is right?** The producer's, on the merits: the control asks whether the fit can
*discriminate*, so the relevant yardstick is the 0.5 model gap the fit exists to resolve,
and 0.030 is 6% of it. A 3% `alpha` difference is also well inside the surrogate's own
mis-specification budget — the Goldstein–Mayer ensemble has no congruence structure, its
determinant ratio scatters ±6% over W-MAIN primes, and it is not the ensemble of Gross
lattices. I endorse the verdict and reject the alternative reading of the *criterion*.

**But two things must be recorded rather than absorbed.** First, the contract's silence is a
genuine defect and the successor must fix the tolerance as a stated multiple of the model
gap. Second, the alternative reading leaves a **highly significant, unexplained residual**:
the data sits 0.0299 above the surrogate in `alpha` and 0.0171 above in `log c`, with
seed-noise 54× smaller. That is a lead, not a finding, and it has a cheap decay test: if it
is arithmetic, it should *grow* relative to the noise as `x_cut` falls into the first-moment
regime where congruence conditions bite; if it is surrogate mis-specification, it should
wander. Nobody should build on it before that test.

---

## 3. FRONT 3 — The cascade and GD-1

### 3.1 (a) Does any 1/4 condition change when carried from OneEnd to Isogeny? **No numeric condition changes. Three non-numeric things do, and one of them is new.**

Both reductions are assigned costs polynomial in the **instance length**, i.e.
`(log p)^{O(1)} = p^{o(1)}`. A `p^{o(1)}` multiplier cannot move an exponent, and the `o(1)`
in a `p^{1/4+o(1)}` target absorbs it by definition. **Every exponent-level condition
BATCH-001 derived — F1 must reach exponent 1/4, `T = c·q·d/k + r`, `r ≥ 0`, the balance
chain — transfers unchanged from OneEnd to EndRing and Isogeny.** I looked for an
exponent-carrying step in the cascade and found none; recorded as "I attacked here and it
held".

What does change:

1. **GRH enters at the Isogeny arrow (O30).** `[35, Proposition 8.5]` begins "Assuming the
   generalised Riemann hypothesis"; the frozen source's Corollary 1.2 says only "Assuming
   Heuristic 1". `docs/claims-and-verification.md` is explicit: "If a reduction is itself
   heuristic or GRH-conditional, that dependency is *added to the list*, never hidden" — and
   that same document uses this very cascade as its worked example of "no more, no fewer",
   so **the program's own doc is now wrong at the Isogeny arrow**. Note the escape hatch,
   which is checkable and cheap: `[33]` (obtained by this task) states Isogeny ≡ OneEnd
   unconditionally under probabilistic polynomial-time reductions, with GRH needed only when
   `P = ℓ-IsogenyPath` or `Q ∈ {MaxOrder, MaxOrder_Q}` and `p ≡ 1 mod 8`. So the GRH rider
   may well be removable by a citation swap — **but the frozen source cites `[35]`, not
   `[33]`, and nobody in this program has checked the swap.** State the rider; offer the
   route; do not assume it.
2. **A new side condition on every candidate mechanism (O32).** Theorem 7.2 reduces EndRing
   to **`OneEnd_λ`** — OneEnd with `log(deg α) ≤ λ(log p)` — and *neither* source states the
   `λ` at which Corollary 1.2 applies it. This is the one genuinely new, exponent-relevant
   finding of REC-2: **any mechanism this campaign proposes must return an endomorphism with
   `log deg α = (log p)^{O(1)}`, or the cascade does not apply at the stated cost.** A
   hypothetical `p^{1/4}` mechanism returning an endomorphism of degree `exp(p^{c})` would
   pay a `poly(λ) = poly(p^c)` factor and lose its exponent at the first arrow. This belongs
   in `target_conditions` as a standing requirement, and it was not there before.
3. **Concrete cost does not transfer (O31).** The only explicit exponent anywhere in the
   cascade is **12**, in the second loop's per-iteration success probability
   `Ω((log N)^{−12})` with `log N = O(log p · λ(log p))`. Propagated naively at
   `log₂ p = 256`: with `λ = O(log p)`, `(log N)^{12} ≈ (256²)^{12} = 2^{192}`; even with
   `log N = O(log p)` it is `256^{12} = 2^{96}` — against a headline `p^{1/3} = 2^{85.3}`.
   **Caveats, stated so this is not read as a refutation:** that is an upper bound derived
   from a *lower* bound on a success probability, the outer iteration count carries no
   assigned degree at all, and the source claims no concrete efficiency for the cascade. The
   conclusion is not "the cascade is broken"; it is **"the `p^{1/3+o(1)}` figure for
   EndRing and Isogeny is asymptotic-only, and no concrete or NIST-level number may be
   inherited across it."** Given `GOAL-P13-001`'s measured per-entry overheads
   (`EV-PEC-2e67ff`, `EV-PEC-857664`, cited as inputs), this is the second independent place
   where the concrete picture is worse than the asymptotic one.

### 3.2 (b) Must the goal be rescoped to OneEnd? **No for the exponent target; yes for three riders.**

`(log p)^{O(1)}` of unassigned degree **is** good enough to carry an exponent claim — that is
what `p^{o(1)}` means, and refusing it would also invalidate the incumbent's own Corollary 1.2.
Rewriting the goal's title and objective onto OneEnd would understate what the campaign is
entitled to claim and would break its comparability with the source. **Do not rescope.**

Instead, GD-1 is **partly discharged and must be superseded, not marked repaired (O34)**:

- GD-1's central question — "is any reduction `p^ε`?" — is now **answered: NO**, on obtained
  primary text, at three independent extractors' agreement.
- GD-1's other prediction — "no exponent is assigned to those reductions anywhere" — is
  **confirmed exactly**, and the frozen source states no multiplier at all when it applies
  them (row S4).
- Residual defect, narrower than GD-1: **(i)** unassigned polynomial degrees make concrete
  cost non-inheritable; **(ii)** GRH is missing from every Isogeny-level restatement;
  **(iii)** `λ` is unstated in both sources and now constrains every candidate.

### 3.3 (c) Is "conditional on Heuristic 1 alone" now wrong? **Wrong for Isogeny; correct for OneEnd and EndRing.**

| statement | conditionality, as now established |
|---|---|
| OneEnd at `p^{1/3+o(1)}` (frozen Theorem 1.1) | **Heuristic 1** — unchanged, correct |
| EndRing at `p^{1/3+o(1)}` (via `[35]` Thm 1.1/7.2) | **Heuristic 1** — the reduction is probabilistic polynomial time, no GRH, no heuristic stated |
| **Isogeny** at `p^{1/3+o(1)}` (via `[35]` Prop. 8.5) | **Heuristic 1 + GRH**, plus the unstated `λ` |

**Records that need correcting** (Coordinator action; I hold no write access to any of them):
`ledger/goals/GOAL-SSIQ-001/goal.yaml` → `scheme_context.incumbent_baselines.heuristic_conditional`,
which states the tier conditional on Heuristic 1 inside a `problem:` field naming the isogeny
problem; `RQ-SSIQ-9702af` wherever it repeats the tier; the worked example in
`docs/claims-and-verification.md` §"Claim records for conditional results"; and — recorded
against myself — the "heuristic-conditional" row of `RT-BATCH-001` §6's frontier table, which
I marked "correctly carried" and which needs the same rider when read at the Isogeny level.
BATCH-001's producer packages need **no** correction: they restricted every derived condition
to OneEnd and marked the cascade CITED-NOT-VERIFIED, which is exactly why this correction is
small.

One inherited citation defect, recorded because it is otherwise invisible: **"[35, Theorem 1]"
has no literal referent** in any obtained rendering (O33). Both candidate readings give the
same cost class, so nothing exponent-level turns on it, but no record of this program may cite
"[35, Theorem 1]" as verified. Write `[35, Theorem 1.1], stated precisely as [35, Theorem 7.2]`.

---

## 4. The pre-committed reversion — was it honoured?

**Yes, strictly, and it did not fire. Nothing has been renegotiated, and nothing may be read
as confirmation.**

- Trigger (`spec.falsification_criterion`): `alpha` within `2.0 ± 0.20`, excluding 1.5 at
  2 s.e., **with C-NULL, C-ANCHOR-LOW, C-ANCHOR-HIGH and C-REPRO all passing.**
- Observed: `alpha = 1.1661` (`|alpha − 2.0| = 0.834 > 0.20`) and **C-NULL FAILED**. Two of
  the trigger's conditions are unmet, so the reversion does not fire.
- The rule was applied mechanically by the executor, the arithmetic is shown, and the
  `INCONCLUSIVE` branch is the branch the frozen text selects. **No clause was reinterpreted
  after seeing the data.** The one place the contract was silent (the `c` tolerance) was
  disclosed rather than filled silently, and it does not touch the reversion.

**The symmetric statement, which is the one at risk of being lost:** `SUPPORTS-D1` did not
fire either. A reversion that does not fire is **not** confirmation of the thing it would
have reverted. L1 is exactly as closed, and exactly as weakly supported, as it was before
BATCH-002 — one derivation-tier pillar, three unfetched ingredients, one model.

**Verified as of this review:** no BATCH-002 ledger record exists yet. `ledger/evidence/`
contains only `EV-SSIQ-e43afd` under this goal; `ledger/decisions/` contains only
`DEC-20260805-2be965` for 2026-08-05; `ledger/goals/GOAL-SSIQ-001/checkpoints/` contains only
`BATCH-001.yaml`. So no record is currently mis-stating this. **Sentences that would be
violations if they appear in `EV-SSIQ-29fcbb`, `DEC-20260805-be2f87`, or
`checkpoints/BATCH-002.yaml`:**

- "the reversion did not fire, so D1 stands" — false; the trigger was never approached;
- "the fit is consistent with `alpha = 3/2`" — the fit is 0.334 from 3/2 and its instrument
  has a measured −0.364 bias; consistency is a calibration statement and no calibration exists;
- "C-NULL failed, so the counting function carries no arithmetic structure" — contradicted
  inside the same run by 5377/5377 exact class-number matches;
- "`alpha = 1.166` is evidence about D1" — barred by the contract's own failure consequence.

---

## 5. Numbered objections

Continuing the campaign's numbering from `RT-BATCH-001` (O1–O20). Severity: HIGH = would
mislead a downstream record about what is established; MEDIUM = real defect, bounded fix;
LOW = hygiene.

| # | objection | sev. | resolution route |
|---|---|---|---|
| **O21** | **Regime mismatch.** At every prime in the dataset the lever's operating point `T = p^{1/4}` sits at `x = T/(p/2)^{1/3} ∈ [0.44, 0.71]` — in saturation; at `log₂ p = 256` it sits at `x = 2^{−21}` — in the first-moment regime. The experiment measured a different regime of the function from the one that decides L1. §1.4 | HIGH | Every citation of this run states the `x`-value of the decision point at the `p` tested. Any successor fit is parameterised in `x`, not `T`. Not repairable by adding primes below `2^{18}`. |
| **O22** | **A tolerance pre-registered on an uncalibrated instrument.** `±0.20` was frozen against a finite-size deficit of 0.25–0.48 computable in closed form before freeze (§1.2). `M-RANGE` defined separating power as `2·se` — a *precision* measure — when the binding limit is *bias*. | HIGH | No exponent tolerance may be pre-registered without a bias calibration on an ensemble of known exponent, at the same `p` and the same window. Generalise this into the experiment template. |
| **O23** | **C-NULL could not have passed.** The surrogate shares both endpoints with the data (Hermite gives `γ₃(p/4)^{1/3} = (p/2)^{1/3}`, the same constant as Theorem 1.5; the determinant fixes the `p^{−1/2}` scale). Requiring the surrogate *not* to reproduce `beta` and `c` required the data to violate D1. The failure consequence was attached to the outcome D1 predicts. §2.2 | HIGH | Relabel the outcome: **surrogate faithful, estimator blind**. It is a controlled null of the *instrument*, not evidence about the object. "C-NULL failed" may never be cited as a statement about supersingular arithmetic. |
| **O24** | **The frozen contract got no adversarial pass before freeze**, although the batch had an adversarial slot. `RT-BATCH-001` §5 control 1 predicted the C-NULL match in writing; the contract turned the predicted outcome into a voiding condition. | MED-HIGH | Any BATCH-003 contract goes through one red-team pass **before** freeze. This is the single cheapest change available and it is the only one that would have saved this batch. |
| **O25** | **The unstated `c` tolerance is load-bearing.** Producer's criterion → null reproduces; a tolerance scaled to the surrogate's own seed spread (0.000554) → the 0.0299 gap is 54σ, C-NULL **passes**, and the metric is not void. Two defensible readings, opposite verdicts. §2.3 | MEDIUM | Fix the tolerance in the successor as a stated multiple of the model gap. I endorse the producer's verdict on the merits, and require the unexplained 0.0299/0.0171 residual to be recorded as a lead with the `x_cut` decay test attached. |
| **O26** | **Tightness vs correctness.** D1 is an *upper bound*; the failure mode is a *weaker* upper bound. Measuring the true counting function tests which bound is tight, never which is correct. Measuring the truth is nonetheless the right target (L1's disjunct 2 depends on the truth, not on the bound) — but no record may say this run "tested D1's derivation" or "tested ingredient (c)". | MEDIUM | Restate the measured object as "the true counting function's exponent, which is what L1 depends on". Ingredient (c) remains checked only by same-model re-derivation. |
| **O27** | **The frozen competing model was refutable at zero compute**, from the `T = 1` class-number anchor plus Theorem 1.5's attained bound: a global `T²p^{−1/2}` law saturates at `≈ 11.6` at `p = 265207`, while 119 primes carry curves at `⌊(p/2)^{1/3}⌋ ≈ 50` and no prime has a shortfall above 5. `RT-BATCH-001` O3 named that endpoint and stopped one step short. §1.4 | MED-HIGH | Record the endpoint argument as the actual disposition of the `alpha = 2` failure mode, at derivation tier, with O26's caveat. It constrains the truth over the tested range; it is not a proof about the asymptotic. |
| **O28** | **D3 selection dominates the sensitivity check.** The publisher's wisde sieve above `p = 22000` selects on the upper tail of the fitted distribution and moves `alpha` by **0.102**; the contract's chosen sensitivity axis moved it by **0.0066**. W-SENS (`p ≥ 10000`) is almost entirely the selected block, so the pre-registered robustness check tested the axis that did not matter. | MEDIUM | Successors take `p ≤ 22000` (exhaustive) as primary and report the selected block separately. Never pool. Executor's handling was correct and is not at fault. |
| **O29** | **M-GRAD's non-measurement is justified on a reason stronger than the facts support.** Rebuilding 2-isogeny adjacency from the released `Z`-bases is *not* a re-import of the model-dependence confound: it is mechanical linear algebra with an exact external oracle — the recomputed right orders must reproduce the released type list with 3-regular multiplicity, and each computed minimum must equal the released `δ`. The budget reason stands alone; the independence reason does not. This matters because M-GRAD is L4's question and L4 is the only lever whose ceiling meets the target. | MEDIUM | See §7 REC-3. Restrict to the exhaustive block, validate against the released minima, and report the validation as a first-class control. |
| **O30** | **GRH is missing from every Isogeny-level restatement of the tier**, including `goal.yaml`'s baseline field, and the program's own `docs/claims-and-verification.md` worked example is wrong at that arrow. §3.1 | MEDIUM | Add "+ GRH" to Isogeny-level statements, or check the `[33]` route (Isogeny ≡ OneEnd stated unconditionally there) and record the citation swap. Do not assume the swap. |
| **O31** | **Concrete cost is not inheritable across the cascade.** The only explicit exponent anywhere in it is 12, in `Ω((log N)^{−12})` with `log N = O(log p·λ(log p))`; naive propagation at `log₂ p = 256` gives `2^{96}`–`2^{192}` against a `2^{85.3}` headline. Loose upper bound, unassigned degrees, no concrete claim by the source — but decisive for what may be *inherited*. §3.1 | MED-HIGH | Record the rider: `p^{1/3+o(1)}` for EndRing/Isogeny is **asymptotic-only**. Any concrete or NIST-level statement this campaign makes stops at OneEnd. |
| **O32** | **New side condition, previously unrecorded:** Theorem 7.2 reduces EndRing to `OneEnd_λ`, and no source states `λ` for Corollary 1.2. Any candidate mechanism must return `α` with `log deg α = (log p)^{O(1)}` or lose its exponent at the first arrow. | MED-HIGH | Add the `λ` condition to `target_conditions` as a standing requirement on every candidate. Independently check the executor's own derivation (`deg α ≤ 2^{2n}·p·p^{1/3+o(1)}`) — it is labelled as a derivation of that task and carries no source authority. |
| **O33** | **"[35, Theorem 1]" has no literal referent** in any obtained rendering. Both readings give the same cost class, so nothing exponent-level turns on it. Inherited from the source, not created here. | LOW-MED | Cite as "[35, Theorem 1.1], stated precisely as [35, Theorem 7.2]", with the ambiguity and the `[33]` alternative noted. |
| **O34** | **GD-1 is partly discharged, not closed.** Its exponent question is answered NO; three narrower residuals remain (unassigned degrees, GRH, `λ`). Marking it "repaired" would erase them. | MEDIUM | Supersede GD-1 with a narrowed defect naming exactly those three. Do not rescope the goal's target statement to OneEnd (§3.2). |
| **O35** | **Presentation risk on the reversion.** The executor's framing is correct, but "the reversion did not fire" reads to a checkpoint as an event about D1. It is an event about the fit failing to reach either branch. §4 | LOW-MED | Checkpoint wording: "INCONCLUSIVE, primary metric VOID; no evidence in either direction; the pre-committed reversion neither fired nor was renegotiated; L1 unchanged at CLOSED-IN-SCOPE on the same single derivation-tier pillar." |

**Unresolvable within this batch:** the model-independence cap (§0), which no action inside
this repository can lift; and O21, which cannot be repaired at `log₂ p ≤ 18` by any estimator,
because it is a property of the data's range and not of the analysis.

**Attacked and held — recorded so this report is not a list of only what broke:** the D2
counting-unit conversion (verified exactly at 5379/5379); C-REPRO's bit-identical digest;
C-SEED's spread (54× smaller than the effect it qualifies); the cascade note's refusal to
assess consequences it was not tasked with; the executor's decision-rule arithmetic; the
absence of any scheme-scope widening — I grepped both packages for every name in the source's
affected and out-of-range lists and found **none**; and the exponent-level invariance of every
BATCH-001 condition under the cascade (§3.1), which I attacked specifically and could not break.

---

## 6. Required controls

1. **Bias calibration before any exponent tolerance.** No `alpha` may be compared to a
   pre-registered model value until the same estimator, same window, same `p` has been run on
   an ensemble whose exponent is known by construction — and the comparison reported as
   `alpha_data − alpha_null + alpha_null_true`, with the calibration's own uncertainty.
2. **Decay discipline on the instrument (`docs/inventor-protocol.md` §3).** Sweep
   `x_cut ∈ {0.5, 0.3, 0.2, 0.15, 0.1}` in `x = T/(p/2)^{1/3}`; the bias on the `α = 3/2` null
   **must** decay monotonically toward 0. A flat bias is a code or surrogate bug and voids
   everything measured with it. Pre-register this before the sweep.
3. **A distribution-level null.** Variance of `N(1,p)·p^{−1/2}` across `p`, data vs surrogate;
   or a KS test on the `δ_E` distribution at fixed `p`. Expect the data's class-number
   fluctuation band to separate from the surrogate's binomial noise. Record explicitly that
   passing this shows the measurement sees arithmetic, **not** that it tests D1.
4. **Exhaustive-block-only primary analysis.** `p ≤ 22000`; the sieve-selected block reported
   separately and never pooled (O28).
5. **Correctness oracle for any in-session recomputation** (L4/M-GRAD): recomputed right
   orders must reproduce the released type list with 3-regular multiplicity and each computed
   minimum must equal the released `δ`. Report the match count as a control, not a footnote.
6. **Null of the same shape for any descent experiment:** the undirected random walk on the
   *same* graphs, measured with the *same* instrument, so that finite-size constants cancel in
   the difference of exponents.
7. **Cost-charging, unchanged** (`KN-LIT-7593`): any invariant, precomputation, or shared
   structure carries its own construction cost inside the total before any exponent is claimed.

---

## 7. Baseline comparison and Pareto honesty

This batch claims no algorithm, so there is no Pareto position to defend. I re-checked the
frontier row by row and it is carried correctly in both packages, with one row now amended:

| row | figure | axes | status after BATCH-002 |
|---|---|---|---|
| unconditional | `p^{1/2}(log p)^{O(1)}` time, polynomial memory | time + memory | unchanged, correctly carried |
| heuristic-conditional (**OneEnd**) | `p^{1/3+o(1)}` time **and** memory, above a superpolynomial `o(1)` | time + memory + disclosed overhead | unchanged, Heuristic 1 only |
| heuristic-conditional (**EndRing**) | same | same | Heuristic 1 only; polylog of unassigned degree (O31) |
| heuristic-conditional (**Isogeny**) | same | same | **now: Heuristic 1 + GRH**, unassigned `λ`, concrete cost not inheritable (O30–O32) |
| interpolation | vOW `p^{1/2+o(1)}/w^{1/2}` at memory `w`; `/(w^{1/2}n)` parallel | time–memory–parallelism | unchanged, correctly carried |
| `F_p`-restricted | `Õ(p^{1/4})`, heuristic, high-storage, memory unstated | time only | unchanged; still barred as `F_{p^2}` evidence |

The gap flagged in `RT-BATCH-001` §6 is still open and still unfilled: no record states that a
hypothetical `p^{1/4}`-time, `p^{1/4}`-memory algorithm would dominate vOW at matched memory
(vOW at `w = p^{1/4}` gives `p^{3/8}`). One sentence in the checkpoint closes it.

**`dominated_by`:** `n/a (no algorithm claimed by this batch)` — checked against every row
above, on all three axes.
**`sota_delta`:** `no attack; one voided measurement, one instrument closure, one costed
reduction cascade`.

---

## 8. Cheapest next falsification for BATCH-003

**First, what not to do.** Do **not** spend BATCH-003 repairing the estimator. Even a perfectly
calibrated fit at `log₂ p ≤ 18` cannot validate an asymptotic (AGENTS rule 7), and the only
outcome that could have reopened L1 — a genuine `alpha ≈ 2` — is refuted for free by the two
anchors (O27). Repairing the instrument would buy a better-measured sub-toy number about a
lever that is already `CLOSED-IN-SCOPE`. The correct disposition of that lane is a **§4
closure, not more measurement**:

> **Closure (instrument lane).** *Obstruction:* the finite-size deficit of the counting
> exponent is `Θ(1/log p)` with the constant fixed by the `T = 1` class-number anchor —
> `s(p) − 3/2 = −2.98/(ln p − 0.693)` — so a `±0.20` discrimination first becomes possible at
> `log₂ p ≳ 22.5`, and `±0.05` at `log₂ p ≈ 87`. *Argument:* §1.2, from two facts already in
> the repository. *Forward guidance:* the repair, if anyone ever needs it, is the scaling
> variable `x = T/(p/2)^{1/3}` with the first-moment (`−log(1 − fraction)`) transform and a
> null calibration; and the only way to reach the required range is data at larger `p`, which
> the AOV authors' own released code could in principle produce.

**REC-3 (primary, recommended) — greedy descent on the 2-isogeny graph: the direct test of L4,
on the dataset already fetched.**

L4 is the only lever whose ideal ceiling equals the goal's target (`RT-BATCH-001` §3.4,
carried into `goal.yaml lever_corrections` as `priority: highest`), and its live question is
whether a computable `δ_E`-gradient exists. That is not a fitting question and it does not
inherit O21's regime problem, because it measures a **hitting time**, not an exponent of a
truncated counting function.

- **Object:** the 2-isogeny graph on the supersingular set at each prime `p ≤ 22000`
  (≤ 1833 vertices — trivially small), built from the released `Z`-bases by enumerating the
  norm-2 left ideals of each maximal order and taking right orders. Vertex label: the
  released `δ_E`.
- **Measurement:** expected number of steps for **greedy/annealed descent on `δ`** to reach
  the `F_p` locus `{δ = 1}`, versus the **undirected random walk on the same graph** as the
  null object of the same shape, both as a function of `p` over the exhaustive block.
- **Pre-registered prediction and the artifact tell:** the null must exhibit the hitting-time
  exponent `≈ 1/2` (density `p^{−1/2}` in an expander); a genuine gradient shows as a
  *smaller exponent* in the greedy arm. Report **the difference of exponents on the same
  graphs**, so finite-size constants cancel. A greedy arm that matches the walk is a
  **controlled null** and a real strengthening of L4's obstruction — recordable, scoped to
  the tested primes. A greedy arm at exponent `≈ 1/4` is the most valuable thing this
  campaign could find.
- **Correctness control (O29):** the recomputed right orders must reproduce the released type
  list with 3-regular multiplicity, and each recomputed minimum must equal the released `δ`.
  This removes the silent-bug risk the executor cited, using the external data as its own
  oracle — which is why the independence objection to M-GRAD does not survive.
- **Cost:** no new acquisition (same bytes, already hashed and logged), pure integer linear
  algebra, graphs of ≤ 1833 vertices, restricted to a few hundred primes if budget bites.
- **Scope, pre-committed:** sub-toy, existence-screen only; a positive result is a lead
  requiring a scaling study, never a claim about cryptographic sizes.

**REC-4 (second, zero compute) — the N5 scoping pass.** Still unscoped, still cheap, and now
sharper than in BATCH-001: §2.2 establishes that L1 is closed *by genericity*, so N5's audit
question is exactly "does the candidate object's governing lattice fail to be generic of
determinant `≍ p`?" — answered by the corrected triple (rank, homogeneity degree of the degree
form, determinant) and the Minkowski exponent computed from all three (`goal.yaml`
`admissibility_criterion` correction). A lookup, no compute, and it is the only enumerated
route the L1 closure provably does not reach.

**REC-5 (hygiene, one session) — pre-freeze red-team pass on the BATCH-003 contract** (O24).

---

## 9. Narrowest supported statement

> **Scoped to the two committed packages at `41a4aebd` and `948c9aee`, under session-only
> (not model) independence:**
>
> 1. `RUN-SSIQ-4de240-a` obtained external, exhaustive `δ_E` data, verified two independent
>    normalisation anchors exactly (`h(−4p)/2` at 5377/5377 primes; the Theorem 1.5 bound at
>    5379/5379 with 119 attaining it), reproduced its coefficients bit-identically, and
>    applied its frozen decision rule mechanically to return **INCONCLUSIVE with the primary
>    metric VOID**. That verdict is correct as recorded.
> 2. **The instrument, not the data, is what failed.** The finite-size deficit of the fitted
>    exponent is `Θ(1/log p)` with a computable constant; at the tested range it is 0.25–0.48,
>    larger than the frozen `±0.20` tolerance and consistent with the −0.364 bias measured on
>    a known-`3/2` ensemble. No fit over `log₂ p ≤ 18` could have discriminated `3/2` from `2`.
> 3. **C-NULL could not have passed.** The surrogate shares both endpoints with the real
>    object (Hermite's constant reproduces Theorem 1.5 exactly; the determinant fixes the
>    `p^{−1/2}` scale), so agreement in `alpha`, `beta` and `c` was structurally forced. The
>    correct label is *surrogate faithful, estimator blind* — a controlled null of the
>    instrument, not a statement about supersingular arithmetic, which the same run proves is
>    present at 5377/5377 exact class-number matches.
> 4. **The frozen `alpha = 2` failure mode is refuted over the tested range by the run's own
>    anchors** (factor 4 in `T` at the largest prime), at derivation tier, and was refutable
>    before the batch was dispatched. This constrains the true counting function; it does not
>    certify D1's derivation, which remains checked by one model only.
> 5. **L1's state is unchanged: `CLOSED-IN-SCOPE`, single pillar, derivation tier.** The
>    reversion did not fire and was not renegotiated; confirmation did not fire either. What
>    is newly visible is *why* the lever is closed — the governing lattice is generic of
>    determinant `≍ p` — which meets the §4 closure standard and locates the remaining opening
>    precisely at N5.
> 6. **The `[35]` cascade carries no exponent**, so every BATCH-001 exponent condition
>    transfers from OneEnd to EndRing and Isogeny unchanged. It carries three non-exponent
>    riders: GRH at the Isogeny arrow, an unstated `λ` that constrains every future candidate,
>    and unassigned polynomial degrees that make concrete cost non-inheritable.
> 7. Nothing in either package states, implies, or is arranged to suggest that a `p^{1/4}`
>    algorithm exists, is likely, or is near, and the source's affected-vs-safe scheme scope is
>    inherited unwidened — I checked every name in both lists across both packages.

---

## 10. Verdict

> **CONFIRM-SCOPED.**

Both packages survive adversarial reading. Nothing asserted in either is false; the executor
disclosed the finding that undermines its own headline; the cascade note quotes primary text
under three independent extractors and correctly refuses to draw the consequences that belong
to me; the decision rule was applied mechanically and the pre-commitment was honoured on both
sides.

It is **not a bare CONFIRM** because the batch's own summary understates what is known. Filed
as "the data was uninformative", this batch teaches nothing; filed correctly — *the instrument
was mis-specified by a computable amount, the null could not have passed, the competing model
was refutable for free, and the dataset never samples the regime the lever lives in* — it
closes a lane with a named obstruction and redirects the campaign to L4 and N5. The relabelling
is mandatory, not cosmetic: O21, O23 and O27 change what a checkpoint should record.

It is **not a CHALLENGE.** Nothing requires reversal. It would become a CHALLENGE the moment
any record cites `alpha = 1.166` as evidence about D1, reads the non-firing reversion as
confirmation, reads "C-NULL failed" as a statement about supersingular arithmetic, or inherits
a concrete cost across the `[35]` cascade.

**On the specific interpretive question the task poses:** REC-1 was the right *strategy* and
the wrong *instrument*, and the error was mine to catch — the pinning argument that predicts
the failure is in my own BATCH-001 report, one step short of being applied to the measurement
I was proposing.

---

## 11. Required output block

```yaml
red_team_report:
  id: RT-BATCH-002
  task_id: TASK-20260805-538c72
  goal_id: GOAL-SSIQ-001
  batch_id: BATCH-002
  reviewed_commits: ["41a4aebd", "948c9aee"]
  head_at_review: 6a629be758cdb3391e2df654e4004f78e952e880
  working_tree_clean_at_review: true
  claim_under_review: >-
    (a) the interpretation and scope of RUN-SSIQ-4de240-a (alpha = 1.1661 +- 0.0005,
    C-NULL FAIL, primary metric VOID, decision branch INCONCLUSIVE); (b) the reading of
    the [35] reduction cascade in TASK-20260805-c89efb and its consequences for GD-1 and
    for every 1/4 condition BATCH-001 derived.
  objections: [O21, O22, O23, O24, O25, O26, O27, O28, O29, O30, O31, O32, O33, O34, O35]
  objection_severity:
    high: [O21, O22, O23]
    medium_high: [O24, O27, O31, O32]
    medium: [O25, O26, O28, O29, O30, O34]
    low_medium: [O33, O35]
  unresolvable_objections:
    - "The model-independence cap: no action inside this repository lifts it."
    - "O21: the regime mismatch cannot be repaired at log2 p <= 18 by any estimator; it is a property of the data's range."
  attacked_and_held:
    - "D2 Galois-orbit counting-unit conversion (exact at 5379/5379 primes)."
    - "C-REPRO bit-identical coefficient digest; C-SEED spread 54x smaller than the effect."
    - "Exponent-level invariance of every BATCH-001 condition under the [35] cascade: no exponent-carrying step exists."
    - "Affected-vs-safe scheme scope: no widening; no scheme name appears in either package."
    - "The executor's mechanical application of the frozen decision rule, including the reversion arithmetic."
    - "L1's closure meets the inventor-protocol section 4 standard (named obstruction = genericity, argument, forward guidance to N5)."
  required_controls:
    - "Bias calibration on a known-exponent ensemble at the same p and window BEFORE any exponent tolerance is pre-registered."
    - "Decay discipline: sweep x_cut in x = T/(p/2)^{1/3}; the bias on the alpha = 3/2 null must decay monotonically to 0, pre-registered; a flat bias is a code or surrogate bug."
    - "Distribution-level null: variance of N(1,p) p^{-1/2} across p, data vs surrogate (class-number fluctuation vs binomial noise). Establishes that the measurement sees arithmetic; does NOT make it a test of D1."
    - "Exhaustive-block-only primary analysis (p <= 22000); never pool with the wisde-selected block."
    - "Correctness oracle for any in-session recomputation: recomputed right orders must reproduce the released type list with 3-regular multiplicity and each minimum must equal the released delta."
    - "Null of the same shape for any descent experiment: undirected random walk on the SAME graphs, difference of exponents reported."
    - "Charge the construction cost of any invariant or precomputation into the total (KN-LIT-7593)."
  counterexample_or_mutation: >-
    Two, both zero-compute and both derived in this report. (1) The two verified anchors pin
    the mean log-log slope of fraction(T) with no fit: s(p) = (1.5 ln p - 4.02)/(ln p - 0.693),
    giving 1.02 at p = 1009 and 1.25 at p = 265207, with deficit -2.98/(ln p - 0.693) = Theta(1/log p);
    every block-restricted fitted alpha lands inside the range pinned for its own primes, so the
    fit measures the finite-size slope and not the asymptotic exponent. (2) A global T^2 p^{-1/2}
    law anchored at T = 1 saturates at T = p^{1/4}/1.95 ~ 11.6 at p = 265207, contradicted by
    curves attaining floor((p/2)^{1/3}) ~ 50 at 119 primes with a largest shortfall of 5 anywhere:
    the frozen competing model is refuted over the tested range by the run's own tail check.
  baseline_comparison: >-
    Frontier re-checked row by row on all three axes. Unchanged: p^{1/2}(log p)^{O(1)} at
    polynomial memory; p^{1/3+o(1)} time AND memory for OneEnd and EndRing conditional on
    Heuristic 1 above a superpolynomial o(1); vOW p^{1/2+o(1)}/w^{1/2} at memory w; the
    F_p-restricted Otilde(p^{1/4}) heuristic high-storage figure, still barred as F_{p^2}
    evidence. AMENDED: the Isogeny-level row now carries Heuristic 1 + GRH, an unstated lambda,
    and unassigned polynomial degrees, so no concrete cost may be inherited across the cascade.
    Still-open gap from RT-BATCH-001: no record states that a hypothetical p^{1/4}-time
    p^{1/4}-memory algorithm would dominate vOW at matched memory (vOW at w = p^{1/4} gives p^{3/8}).
  dominated_by: "n/a (no algorithm claimed by this batch)"
  sota_delta: "no attack; one voided measurement, one instrument closure, one costed reduction cascade"
  heuristic_challenges:
    - "D1's content is a null-model statement (Gross lattices are not anomalously short-vector-rich for their determinant). The C-NULL match is weak, uncalibrated corroboration of exactly that content, which is why the control could not discriminate: the surrogate shares BOTH endpoints, Hermite's gamma_3 (p/4)^{1/3} = (p/2)^{1/3} reproducing Theorem 1.5's constant."
    - "The experiment tests the TIGHTNESS of D1's upper bound, never its correctness. Ingredient (c) remains checked only by same-model re-derivation; the external data did not touch it."
    - "Heuristic 1's uniformity range and the F4/F5 exponent-free narrowing from RT-BATCH-001 O13 are unaffected by this batch and still stand."
  cost_model_challenges:
    - "The [35] cascade assigns no exponent, so exponent-level conditions transfer unchanged; but the only explicit exponent in it is 12 in Omega((log N)^{-12}) with log N = O(log p . lambda(log p)), which propagated naively at log2 p = 256 gives 2^{96} to 2^{192} against a 2^{85.3} headline. Upper bound of an upper bound, degrees unassigned - decisive for inheritance, not a refutation."
    - "lambda is unstated in both sources: Theorem 7.2 reduces EndRing to OneEnd_lambda, so any candidate mechanism must return an endomorphism with log deg alpha = (log p)^{O(1)} or lose its exponent at the first arrow. New standing condition on every candidate."
    - "M-RANGE reported separating power as 2*se (precision) when the binding limit is bias; the frozen +-0.20 tolerance is smaller than the instrument's own finite-size deficit at every prime tested."
  reduction_and_scope_challenges:
    - "GRH appears in [35, Proposition 8.5] and not in Corollary 1.2, so Isogeny-level statements are conditional on Heuristic 1 AND GRH. OneEnd and EndRing remain Heuristic 1 only. docs/claims-and-verification.md uses this exact cascade as its 'no more, no fewer' example and is wrong at the Isogeny arrow. [33] may remove the rider by citation swap; unchecked."
    - "[35, Theorem 1] has no literal referent in any obtained rendering; both readings give the same cost class, so nothing exponent-level turns on it, but no record may cite it as verified."
    - "GD-1 is partly discharged (its exponent question is answered NO) and must be superseded with a narrowed defect naming the three residuals, not marked repaired. The goal's target statement should NOT be rescoped to OneEnd: (log p)^{O(1)} of unassigned degree is exactly what an exponent claim tolerates."
    - "Affected-vs-safe scheme scope: checked both packages against every name in the source's two lists. NO WIDENING. No scheme is named anywhere in either package."
  proof_architecture_challenges:
    - "Method-ceiling attack on the INSTRUMENT (the audit nobody ran, including me): the ceiling of a truncated-window power-law fit at log2 p <= 18 is an exponent deficit of Theta(1/log p) with a computable constant; the headline discrimination it was asked to perform was outside that ceiling before the contract was frozen."
    - "Nearby-object attack: the surrogate is not merely a nearby object, it is an object sharing both endpoints with the target, so the fit cannot distinguish the pair. The load-bearing structure the fit sees is Hermite plus determinant, i.e. lattice geometry."
    - "Observation-collision: the three-parameter power-law summary is a genuine observation collision - a generic ternary ensemble and the supersingular counting function have the same observable to 0.03 in alpha and a c-ratio of 1.017, while differing exactly at 5377/5377 primes in a statistic the summary discards."
    - "Quantifier order: unchanged from BATCH-001 and still sound; the cascade adds a per-instance lambda bound that is a NEW quantifier the campaign had not recorded."
  reversion_statement: >-
    HONOURED AND DID NOT FIRE. Trigger requires alpha within 2.0 +- 0.20 with C-NULL,
    C-ANCHOR-LOW, C-ANCHOR-HIGH and C-REPRO all passing. alpha = 1.1661 (|alpha - 2.0| = 0.834)
    and C-NULL FAILED, so two trigger conditions are unmet. The rule was applied mechanically
    and no clause was reinterpreted after seeing the data. SYMMETRICALLY: SUPPORTS-D1 did not
    fire either, and a reversion that does not fire is not confirmation. L1 is exactly as
    closed, and exactly as weakly supported, as before BATCH-002. Verified at review time that
    no BATCH-002 evidence, decision or checkpoint record yet exists, so no record currently
    misstates this.
  narrowest_supported_statement: "See section 9, items 1-7."
  next_concrete_action: >-
    REC-3: build the 2-isogeny graph per prime over the exhaustive block (p <= 22000, <= 1833
    vertices) from the released Z-bases by enumerating norm-2 left ideals and taking right
    orders, label vertices by the released delta_E, and measure the expected steps for greedy
    descent on delta to reach the F_p locus AGAINST the undirected random walk on the same
    graphs, reporting the DIFFERENCE of hitting-time exponents as a function of p. Validate the
    reconstruction against the released minima (3-regular multiplicity; each recomputed minimum
    equals the released delta) and report the match count as a control. This is the direct test
    of L4, the only lever whose ideal ceiling equals the goal's target, it does not inherit the
    regime mismatch of O21, and it needs no new acquisition. Second: REC-4, the zero-compute N5
    scoping pass under the corrected (rank, homogeneity degree, determinant) criterion. Third:
    REC-5, a red-team pass on the BATCH-003 contract BEFORE freeze. Explicitly NOT recommended:
    repairing the estimator, because a perfect fit at log2 p <= 18 still cannot validate an
    asymptotic and the only outcome that could reopen L1 is refuted for free by the anchors.
  independence_cap: >-
    SESSION independence only, never model independence. REC-1's external data lifted it for
    the SETUP (two externally computed anchors that could have contradicted this program's
    reading of the object and did not) and NOT for D1 (the primary metric returned nothing, so
    ingredient (c) is still checked by one model only). It did deliver one unplanned result: a
    quantified negative about the instrument.
  artifact_paths:
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-002/reviews/RT-BATCH-002.md
  files_written_outside_scope: []
  raw_artifacts_modified: 0
  ledger_touched: false
  record_statuses_changed: 0
  compute_performed: none
  commits_made: 0
  commit_note: >-
    No commit made. Per AGENTS.md "Durable research commits", the Coordinator's ledger archive
    task commits this report. It is not durable until that archive exists.
  verdict: CONFIRM-SCOPED
```
