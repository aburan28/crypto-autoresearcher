# Red Team report — TASK-20260904-22e444

Goal `GOAL-SSI-001` · batch `BATCH-256a94` · round plan on `TASK-20260904-1f4e2f`
Package under review: the RG-0 source-state census, snapshot commit
`5872cf99a2e71c0455502244047ad3c2f019ccbc`.
Joints owned: **J4 anchor reconciliation and citation eligibility**, **J6 scope and
provenance of the fix-status verdict**. Also owned: the `proves_too_much` control and
the `blind_rederivation`.

This report is a review, not a decision. It changes no status and commits nothing.

---

## 1. Blind re-derivation of the charging law (written before any producer artifact was opened)

**Ordering attestation.** Everything in this section was computed and written before I
opened any file under `coordination/goals/GOAL-SSI-001/batches/BATCH-256a94/tasks/TASK-20260904-1f4e2f/`,
any run record under `experiments/EXP-WESOVOW-001/runs/`, `experiments/EXP-WESOVOW-001/cost_model.py`,
any ledger evidence or decision record, `batch.yaml` of either batch, or the review plan.
Sources for this section, and only these:

- `experiments/EXP-WESOVOW-001/specification.yaml` — `model_definition`,
  `scenario_definitions`, controls `C2`, `C3`, `C4`, and the `metrics` list.
- my own arithmetic, in a Dickman-ρ implementation written for this task.

I did not read `cost_model.py`. I did not read any of the five `blind_from` paths at any
point in this task.

### 1.1 What C3 and C4 force

C3: *"T(w) must be non-increasing in memory budget w for every (p, overhead) scenario;
T(w) must equal T_full for w >= M."*
C4: *"At w = M, vOW time must equal T_full exactly (cap check)."*

The van Oorschot–Wiener middle-memory interpolation is a square-root penalty in the memory
deficit. Writing the deficit relative to the full-memory point M, the unique one-parameter
form with a `1/2` exponent that is (i) non-increasing in w, (ii) equal to `T_full` at
`w = M`, and (iii) constant for `w >= M`, and that carries the specification's explicit
multiplier `2^{c·sqrt(log2 p)}` on `T(w)`, is

```
LAW B:   log2 T_c(w) = log2 T_full + c·sqrt(log2 p) + max(0, (log2 M − log2 w)/2)
```

equivalently `T_c(w) = T_full · 2^{c·sqrt(log2 p)} · sqrt(M/w)` for `w ≤ M`, capped at
`T_full · 2^{c·sqrt(log2 p)}` above. Its crossover against the Delfs–Galbraith baseline
`log2 T_DG = log2(p)/2` (control C2) is obtained by solving `T_c(w*) = T_DG`:

```
log2 w*_B = log2 M + 2·( log2 T_full + c·sqrt(log2 p) − log2 T_DG )
```

with "capped by M" read as: `w*_B > log2 M` means the crossover is unreachable — even at
full memory the modelled cost does not descend to the baseline — and `w*_B ≤ log2 M` means
it is reachable at that budget.

### 1.2 A defect in the frozen specification itself, found blind

The specification's own `metrics` list states a *different* analytic crossover:

> `crossover memory log2(w*) per (p, overhead c), analytic: w* = (T_full * 2^{c*sqrt(log2 p)} / T_DG)^2, capped by M`

That formula is the crossover of

```
LAW A:   log2 T_c(w) = log2 T_full + c·sqrt(log2 p) − (log2 w)/2
```

**LAW A violates C4.** At `w = M` it gives `T_c(M) = T_full·2^{c·√log2 p} / sqrt(M)`, which
is below `T_full` by `log2(M)/2` bits — 46.6 bits at the smallest field size in the grid and
134.3 bits at the largest (table in §1.4). It also has no `w ≥ M` plateau, so it violates the
second sentence of C3.

So two clauses of the frozen contract are mutually unsatisfiable: **no single law satisfies
both the `metrics`-line analytic `w*` and control C4.** This is a defect in the contract, not
in any implementation, and I found it without reading any implementation. An implementation
that satisfies C4 *cannot* reproduce the `metrics`-line `w*`; an implementation that
reproduces the `metrics`-line `w*` *cannot* pass C4 except by a cap check that does not
actually test the law. Any review that reports "C4 passes" and "the analytic `w*` is as
specified" has necessarily done at least one of those two things vacuously.

### 1.3 The two laws differ by a constant, and that is what a margin test can see

For every `w ≤ M`:

```
log2 T_B(w) − log2 T_A(w) = max(0, (log2 M − log2 w)/2) + (log2 w)/2 = (log2 M)/2
```

— **independent of w, of c, and of the overhead scenario.** The two candidate laws are
related by a pure multiplicative constant `2^{(log2 M)/2}` over the whole in-grid range.

This has a sharp consequence for any control that discriminates laws by the size of a gap.
A gap of `(log2 M)/2` bits between two laws is *not* evidence that the test is sensitive; it
is evidence that the two objects compared differ by a constant of that size and nothing else.
Such a test is blind, by construction, to: the exponent on the memory deficit (½ vs any other
value); the presence, sign, or magnitude of the `2^{c·sqrt(log2 p)}` overhead term; the
placement of the cap; the values of `log2 M`, `log2 P0`, and `log2 T_full` themselves; and
any error whose effect is smaller than the constant. I return to this under J4.

### 1.4 Blind numbers

Optimizer as specified (`log2 B ∈ [1,60]`, step 0.1, minimize `log2 T_full`, constraints
`w ≥ 1`, `u ≥ 1`), Dickman ρ from my own delayed-ODE march — deliberately **not** the
Laplace-inversion method the specification describes, so that any agreement is cross-method
rather than re-implementation. My ρ anchors: `ρ(2)` matches `1 − ln 2` to 1.8e-13 relative,
`ρ(3)` to 1.8e-9, `ρ(4)` to 4.0e-8, `ρ(5)` to 5.9e-7, `ρ(6)` to 8.7e-6. It degrades past
u ≈ 8 (relative error 1e-1 at u = 9), exactly as the specification's `why_not_dde_marching`
note predicts; every optimum below sits at `w_opt ∈ [3.49, 5.40]`, and re-running the
optimizer with ρ replaced by its asymptotic form for all `u > 8` reproduces every optimum to
0.00e+00 bits, so no reported quantity depends on the degraded region.

| log2 p | log2 B_opt | log2 X | w_opt | u_opt | log2 ρ(w) | log2 M | log2 P0 | log2 T_full | log2 T_DG | (log2 M)/2 |
|---|---|---|---|---|---|---|---|---|---|---|
| 256 | 14.2 | 49.600 | 3.493 | 5.986 | −5.922 | 93.278 | −15.453 | 108.731 | 128.0 | 46.639 |
| 384 | 17.8 | 72.733 | 4.086 | 7.172 | −7.979 | 137.488 | −20.387 | 157.874 | 192.0 | 68.744 |
| 512 | 20.9 | 95.617 | 4.575 | 8.150 | −9.797 | 181.436 | −24.668 | 206.104 | 256.0 | 90.718 |
| 576 | 22.3 | 106.983 | 4.797 | 8.595 | −10.660 | 203.307 | −26.674 | 229.981 | 288.0 | 101.654 |
| 768 | 26.1 | 140.883 | 5.398 | 9.796 | −13.080 | 268.687 | −32.249 | 300.935 | 384.0 | 134.343 |

(On a 0.01 grid the p = 512 and p = 576 optima move to log2 B = 20.86 and 22.27, changing
`log2 T_full` by 0.000 and 0.000 bits respectively; the 0.1 grid the contract specifies is
what the table reports.)

`log2 T_c(w)` and `log2 w*` follow from LAW B and this table by §1.1 in closed form; I
computed both grids blind, and I withhold the two numeric entries the task card places under
a citation prohibition (§4), which I had not yet read when this section was written. The
derivation above is sufficient for any reader to regenerate them.

### 1.5 The C4 arm is algebraically entailed — found blind, and it is worse than "entailed"

Under LAW B the cap check C4 evaluates `max(0, (log2 M − log2 M)/2) = max(0,0) = 0`. A test
of `T(M) = T_full` therefore compares a quantity to itself through an identity, for every p
and every c. My blind C4 pass returned `+0.000e+00` at all five field sizes — a result that
carries **zero bits of information about the implementation**, because no implementation of
the `max(0, ·)` form can return anything else.

The point I want on the record is stronger than "this control is entailed". C4 is the *only*
control in the frozen contract that pins the charging law's normalisation, i.e. the only one
that could have caught the LAW A / LAW B substitution of §1.2. C3's first sentence
(monotonicity) is satisfied by **both** laws — I checked: 0 of 20 `(p, c)` pairs are
non-monotone under LAW B, and LAW A is strictly decreasing in `w` everywhere, so it passes
too. C1 and C2 constrain `T_full`, `M`, and `T_DG`, none of which the substitution touches.
So the contract as frozen has **no control that distinguishes LAW A from LAW B**, and the
one control written to do it is an identity. That is a contract-design finding, and it is
independent of anything the producer did.

---

## 2. What the blind derivation reproduced once the package was opened

Written after §1, on the committed artifacts named in §8.

My blind LAW B is, character for character in the frozen log2 units, the law the package
carries. Independent agreement, on paths that never touched the same implementation:

| Blind quantity (§1) | Committed statement | Agreement |
|---|---|---|
| `log2 T_c(w) = log2 T_full + c·√(log2 p) + max(0, (log2 M − log2 w)/2)` | `cost_model.py:272-275`; `protocol_amendment.yaml` `log2_law` | identical expression |
| `log2 w* = log2 M + 2·(log2 T_full + c·√log2 p − log2 T_DG)` | `protocol_amendment.yaml` `crossover.equation` | identical expression |
| all 240 rows of `anchor_reconciliation.json`, recomputed from each row's own declared `log2T_full_anchor`, `log2M_anchor`, `log2w`, `overhead_c` | `log2T_w_current_law` | **max abs difference 0.000e+00 bits, 240/240** |
| all 240 `log2w_star_current_law` | same | **max abs difference 0.000e+00 bits, 240/240** |
| `fitted_opt` anchor, re-optimised from the frozen `model_definition` with my own Dickman ρ | `RUN-WESOVOW-001/raw-result.json:per_field[*].optimal` | `log2B_opt` identical at all five sizes; `log2T`/`log2M` agree to **≤ 2.5e-4 bits** |
| the predecessor law's cap deficit `0.5·log2 M` = 46.639 / 68.744 / 90.718 / 101.654 / 134.343 | `anchor_reconciliation.json` `controls.proves_too_much.object_1` deficits | identical to 3 d.p. at all five sizes |

Two consequences the round should record.

**(a) The blind re-derivation, not RG-1/RG-2/RG-3, is what protects this package.** RG-1 and
RG-2 recompute committed run cells and match them to `0.0` bits over 120 cells each. Bit-exact
agreement over 120 cells is what a faithful re-implementation of the same expression tree
produces, and it is *equally* what a faithful re-implementation of a wrong expression tree
would produce. Those gates establish arithmetic identity with the run, not correctness of the
law. The law's correctness against the frozen contract is established by §1 and by the
amendment, and I confirm it. Whoever composes this round should not let `0.0` bits over 120
cells be quoted as independent validation of the cost model; it is a self-consistency check
plus, now, one independent derivation.

**(b) I closed the one hole the declared controls cannot reach.** The task card names a
mixed-anchor row — a time from one anchor with a memory from the other — as "a defect, not a
result", and the producer answers that its two anchors are built by code paths that never mix.
That answer is an assertion about `reconcile.py`, which is in my `blind_from` set, and **no
declared control tests it**: RG-1/RG-2 compare against committed run cells, which exist only
for `fitted_opt`, so a mixed-anchor defect confined to the 120 `PAPER_PAIRS` rows is invisible
to them; the largest such defect is `|Δ log2M|/2 ≤ 1.76` bits, two orders of magnitude under
RG-3's separation; and RG-4's cap identity is anchor-agnostic. I therefore ran the check that
does reach it, from the JSON alone: for every row, is `(log2T_full_anchor, log2M_anchor)`
exactly one of the two declared literal pairs for that field size, unmixed?
**Result: 0 mixed-anchor rows out of 240**, and `overhead_bits = c·√(log2 p)` in 240/240,
`log2T_DG = log2 p / 2` in 240/240 (C2). The hole is closed; it was closed by a control that
did not exist in the plan, and it should exist in the next one.

---

## 3. J4 anchor reconciliation and citation eligibility

**Verdict: BREAKS**, narrowly and precisely — the reconciliation half holds and I strengthen
it; the citation-eligibility half breaks.

### 3.1 The arithmetic and the localization hold, and I go further than the producer did

The producer states that the `optimal` anchors are "read as inputs, not reproduced;
reproducing them would require re-running the `B` optimizer." I reproduced them without
running anything of theirs: from `specification.yaml`'s `model_definition` and optimizer
declaration, with a Dickman ρ marched from the delayed ODE rather than the specification's
Laplace inversion. Same `log2B_opt` at all five field sizes; `log2T_full` and `log2M` agreeing
to between 9.1e-6 and 2.5e-4 bits, the whole residue being my ρ against theirs (the time and
memory deviations are equal to the last digit at each field size, which is what must happen
when `log2P0 = −u log2 u` is exact and the only inexact term is `log2 ρ(w)`).

That upgrades the record: **`fitted_opt` is independently reproducible from the frozen
contract by a second implementation.** The two anchors are therefore not symmetric in
verifiability, and no artifact in this round said so.

### 3.2 The break in comparability: `PAPER_PAIRS` is not a point of this model at three of five field sizes

The joint asks what each anchor measures and whether they are the same quantity. They are not,
and the failure is sharper than "an external report versus an internal computation".

`specification.yaml:74-78` declares the optimizer: *variable* `log2(B)`, *grid* `[1.0, 60.0]`
step 0.1, *objective* **minimize `log2(T_full)`**. So `per_field[*].optimal.log2T` is, by the
contract's own definition, the smallest `log2 T_full` this model attains. Comparing it with the
transcribed pair, from committed literals only:

| log2 p | model's attained minimum `log2 T_full` | `PAPER_PAIRS` `log2 time` | paper − minimum |
|---|---|---|---|
| 256 | 108.73088958800618 | 106.5 | **−2.231** |
| 384 | 157.87439031817553 | 157.5 | **−0.374** |
| 512 | 206.1038967394178 | 204.2 | **−1.904** |
| 576 | 229.98121023958595 | 230.9 | +0.919 |
| 768 | 300.93543569782855 | 302.4 | +1.465 |

At `log2 p` = 256, 384 and 512 the transcribed time lies **below the minimum the model can
attain at any `B` on its declared grid**. A value below a minimum is not a value of the
function. Whatever `PAPER_PAIRS` is at those three sizes, it is not an `(T_full, M)` pair this
cost model produces.

The Pareto reading makes the same point without appealing to minimality: at `log2 p` = 256 and
512 the transcribed pair has **both** smaller time and smaller memory than the model's
optimum, so it dominates the model's own optimum in both coordinates; at 576 and 768 the
model's optimum dominates *it* in both coordinates. Either way it is not the model's optimum
anywhere, and at three sizes it is not on the model's curve at all.

Scope, stated plainly: this shows the two anchors are different *kinds* of quantity under this
cost model. It says nothing about which of the paper, the transcription, or the model's Dickman
ρ / grid / conventions is responsible, and I make no claim in any of those directions. The
cheapest experiment that would separate them is RC-1 below.

This is the plan's first breaking artifact for J4 — "a demonstration that one anchor is not
comparable to the other at all (which would strengthen the prohibition)" — and it strengthens
it.

### 3.3 The break in citation eligibility: the flag's scope is narrower than its own rationale

`anchor_reconciliation.json` carries a per-row `citation_prohibited` boolean, and the batch
states its purpose: "so a downstream consumer that reads only the JSON still meets the flag."
That field is the machine interface to the prohibition. Its scope is exactly
`field_size_log2p == 512`: 48 rows flagged, all at 512, 192 rows carrying
`citation_prohibited: false` and `citation_prohibition_note: null`.

The rationale the batch records for the prohibition is anchor-dependence of the baseline
comparison's **sign**. I searched the 96 non-512 cell pairs for that same phenomenon,
recomputing both sides from my own blind law rather than trusting the JSON's own columns:

> At **`log2 p` = 256, `log2 w` = 50, `c` = 0.0** and at **`log2 p` = 256, `log2 w` = 70,
> `c` = 0.5**, the two anchors give **opposite signs** for the baseline comparison. Both rows
> carry `citation_prohibited: false` and `citation_prohibition_note: null`.
> (Values withheld; the sign disagreement is the finding. Neither cell is `P=512` and neither
> is `w = 2^80`, so neither is covered by the standing prohibition.)

At one of those two cells the smaller of the two margins is a **quarter of a bit** — under the
anchor that §3.2 shows is not a point of this model at `log2 p` = 256.

So the phenomenon that justifies the prohibition occurs at a field size the prohibition does
not cover, and the package's own machine-readable flag reports those rows as unprohibited. A
downstream consumer honouring the flag is led straight to an anchor-dependent sign. **This is
the break on J4**, and it argues for widening the boundary, never for lifting it.

### 3.4 Why this is generic, and the null-object reading

Under the corrected law, for `log2 w` below `log2 M` at both anchors,

```
Δ log2 T(w)  =  Δ log2 T_full + (Δ log2 M)/2
```

— **independent of `w`, of `c`, and of the overhead scenario.** I verified this reproduces the
producer's per-field figures to the last digit at all five field sizes (+2.6197987313,
−0.1817828877, +1.9718130766, −2.2652788711, −3.2211963513). Two consequences.

First, the producer reports this as "max |Δ log2T(w)| over the 24 (budget, c) cells". The
quantity does not vary over those 24 cells; the maximum is the only value. The phrasing invites
a reader to think 24 numbers were surveyed and the worst reported. One was.

Second — the null-object reading the inventor protocol asks for. Because the anchor offset is a
rigid constant per field size, the **count** of sign disagreements is not a fact about isogenies
or about this cost model; it is a count of how many grid cells happen to fall within that
constant of the baseline. Any two anchors separated by the same constant produce the same count
on the same grid. So "2 of 96" is a controlled null, not a finding, and its correct reading is
the general one: *anchor-dependent signs are generic wherever the grid samples within the anchor
gap of the baseline.* That is why a prohibition indexed by field size cannot be the right shape.

**Ask what should have destroyed the signal.** The parameter that ought to kill an
anchor-dependent sign is model accuracy: as the model tracks its external reference, the two
anchors converge and the flips must vanish. The measured C1 deviations are 2.62, 0.18, 1.97,
2.27, 3.22 bits at `log2 p` = 256 → 768. They do not decay with the field size; the largest is
at the largest field size, and `within_tolerance_0.75bit: False` at **all five** field sizes
(8 of the 10 individual coordinates out of tolerance). A quantity that fails to shrink when the
parameter meant to shrink it grows is the canonical artifact tell. Here it means the anchor
ambiguity is not a small-parameter nuisance that would wash out at larger sizes.

### 3.5 The strongest honest argument for LIFTING, and where it fails

I built it deliberately, as the plan asks.

> *For lifting.* Three of the four things one could have doubted are now settled: the current
> implementation, the successor run, the frozen amendment and the `BATCH-eb0a7e` derivation are
> one law (I confirm, blind); that law reproduces the committed successor cells to `0.0` bits
> over 120 cells; the divergence is fully localized to the anchor inputs, with no formula
> residue beyond `5.7e-14`. `DEC-20260824-384e78` already records the anchor ambiguity as a
> committed Coordinator decision, so the ambiguity is public. A value cited *with its anchor
> named and the ambiguity attached* would therefore carry its own caveat, and suppressing a
> number whose provenance is fully documented costs the program more than it protects.

It fails at four independent points, any one of which is sufficient:

1. **The anchor is not merely undetermined; one candidate is infeasible.** §3.2. Citing "under
   both anchors" would publish, at three of five field sizes, a figure derived from a pair the
   model cannot produce. Naming the anchor does not repair that, because the reader has no way
   to know one of the two named anchors is off-curve — nothing in the committed record says so
   before this report.
2. **The resolving power is not established at the scale that decides the sign.** The anchor
   gap is 0.18–3.22 bits; the contract's own sanity tolerance is 0.75 bits and the run is
   outside it at every field size. The quantity being cited is a *comparison to a baseline*,
   and its sign turns on differences smaller than the model's demonstrated agreement with its
   own reference.
3. **The overhead is a free parameter, not a measurement.** `c` is a declared scenario knob
   over `{0.0, 0.5, 1.0, 2.0}` modelling "the superpolynomial factor hidden in the paper's
   o(1)". At `log2 p` = 256 the term spans 0 to 32 bits across that range. Any sign statement
   is a statement conditional on an unmeasured parameter, and the package measures nothing.
4. **Neither run's provenance is attested.** `RUN-WESOVOW-001/manifest.yaml:19` and
   `RUN-WESOVOW-201692-001/manifest.yaml:24` both record `dirty_tree: true`, and the producer
   correctly declines to attest their historical execution. Lifting a citation prohibition
   promotes a number to quotable status; that is precisely the point at which unattested
   provenance stops being tolerable.

### 3.6 Recommendation on the P=512 prohibition — A RECOMMENDATION, NOT A DECISION

The prohibition, restated verbatim and **not lifted by this report**:

> The `P=512` crossover value and its `w=2^80` sign are **NOT citation-eligible**. This task
> does not lift that prohibition. Only a committed Coordinator decision on independently
> reviewed evidence can lift it.

**I recommend RETAINING it, and I recommend EXTENDING it.** This is a reviewer's
recommendation. It changes nothing. Only a committed Coordinator decision — the batch reserves
`DEC-20260904-166ab5` — can act on it, and reserving an identifier is not a commitment either
way.

The extension I recommend is by **predicate, not by field size**: a row is citation-ineligible
when the two anchors disagree in the sign of the baseline comparison, or when the smaller
|margin| across the two anchors is below the field size's anchor gap `|Δ log2T_full + Δ log2M/2|`.
On the committed grid that predicate captures the currently prohibited family **and** the two
`log2 p` = 256 rows of §3.3, and it stays correct if the grid is ever extended, which a
field-size index does not. If the Coordinator prefers the minimum change, flagging those two
rows is a one-line edit to a successor artifact and costs nothing.

I recommend **against** lifting on the strength of this package for the reasons in §3.5. I note
for completeness that lifting would also be premature on a procedural ground independent of the
science: the sibling reviewer on J1/J2/J3/J5 has not reported, and I cannot see its joints.

---

## 4. J6 scope and provenance of the fix-status verdict

**Verdict: BREAKS** on scope. **Holds** on provenance — and the provenance is better than the
task brief's suspicion allowed for; I record that plainly, because the suspicion was correct to
raise and the evidence answers it.

### 4.1 Provenance: the producer did not reproduce the prior it was handed

The concern was that `fix_already_applied` is both the Coordinator's recorded expectation and
the producer's finding, and that agreement of that kind is a reason for more suspicion. I tested
it three ways.

- **Did the producer lean on the inadmissible block?** `batch.yaml`'s `opening_observation` is
  declared "HYPOTHESIS, NOT A FINDING … no artifact of this batch may cite this block as
  support." The census carries a section headed *"Explicitly not cited as support"* and rests
  every claim on a shown `git` command or a quoted `file:line`. I found no step in
  `source_state_census.md`, `outstanding_fix.md` or `anchor_reconciliation.md` that requires the
  block. **Not sustained.**
- **Did it verify independently, or restate?** It overturned a load-bearing detail of the prior.
  The prior and the opening block both say the repair was "admitted upstream on 2026-08-09";
  the census's AN-1 shows the source reached `origin/main` only later. A producer reproducing a
  handed prior does not contradict it.
- **Is the verification itself sound?** I re-ran it rather than reading it. Independently:
  `7d188a7c3` exists, dated 2026-08-08 23:45:42 −0700;
  `git merge-base --is-ancestor 7d188a7c3 bd47a3f5c` → exit 1;
  `… 7d188a7c3 e45861af5` → exit 1;
  `… 7d188a7c3 2675886ea` → exit 0; `… 2675886ea origin/main` → exit 0.
  `bd47a3f5c` is 2026-08-24 11:32:12 −0700 = **18:32:12 UTC**; `2675886ea` is **20:50:28 UTC**
  — the fix reached `origin/main`'s first-parent line about 2 h 18 min *after* that batch's
  snapshot base. I also checked the step the census asserts but does not show: the first parent
  of `2675886ea` is `6fda12409`, and `git merge-base --is-ancestor 7d188a7c3 6fda12409` → exit
  1, so `2675886ea` genuinely is the first-parent entry point and the census's binary search
  landed correctly. **AN-1 verified.**

**And the census's own worktree/committed discipline holds at the snapshot, not merely at census
time.** The census reports blob `a7ec7fd1ac4a48e7025fe8e7cfee0e46f6344b47` at worktree, `HEAD`
(`27efe0cdc`) and `origin/main`. I checked the commit that actually binds this review:
`5872cf99a2e71c0455502244047ad3c2f019ccbc:experiments/EXP-WESOVOW-001/cost_model.py` is the
same blob, as is `origin/main`'s. The J1 attack line — "the census is a claim about what is
COMMITTED and the producer reads a WORKING TREE" — does not land here on the evidence I can
see; the distinction was checked and I re-checked it one commit further forward than the
producer could.

**Package integrity, for my own standing to review.** All seven declared
`source_path_sha256` values reproduce exactly from the snapshot commit's tree. One discrepancy,
recorded rather than passed over: the receipt declares `parent_sha:
a769ca3e72217708b93f40192afd321bdcd9cc1b`, while the snapshot commit's actual first parent is
`26a8d6061` (`revert: un-publish RG-0 artifacts + receipt so the snapshot archive can bind
them`); `a769ca3e7` is an ancestor but not the parent. The receipt records `commit_sha: null`
and `status: pending_post_commit` with a content-first note, and under the repository's
content-first rule the binding is the hashes, which verify. I flag the parent mismatch as an
observation for the archive task, not as a defect in the science.

### 4.2 The break: a governing committed artifact still states the pre-fix law, and the census quoted around it

RG-0's mandate is a census of the charging law across five governing artifacts, one of which is
`specification.yaml`. The census quotes C3 and C4 from it and then characterises the file:

> "The specification states a **normalisation requirement**, not a closed-form law."

**That is false of the file.** `experiments/EXP-WESOVOW-001/specification.yaml:39-40`, in the
`metrics` list, states a closed-form law:

```
  - crossover memory log2(w*) per (p, overhead c), analytic: w* = (T_full * 2^{c*sqrt(log2
      p)} / T_DG)^2, capped by M
```

I identified that line as inconsistent with C4 in §1.2 **before opening any producer artifact**,
purely because no single law can satisfy both. Reading the package afterwards resolves what it
is: it is the **pre-fix crossover**. The census's own account of the repair says the fix moved
the crossover "from `2.0 * (log2Tfull + overhead_bits - log2TDG)` to `log2M + 2.0 * (…)`" —
and `2.0*(log2Tfull + overhead − log2TDG)` is exactly the `metrics` line in log2 form. The
frozen amendment `TASK-20260809-ef3e58` lists "analytic log2w_star crossover computation" among
its `defect.affected_source_locations`, freezes
`log2(w_star) = log2(M) + 2*(log2(T_full) + overhead_bits − log2(T_DG))`, and lists
`specification.yaml` under `immutable_exclusions` — so the contract was deliberately left
unchanged and now disagrees with the amendment that governs the implementation.

I confirmed the disagreement is live and material against both committed runs, using my blind
formulas. At `log2 p` = 256, the predecessor run's committed `log2w_star_entries` are
−38.53822082398764 (c = 0.0) and −22.538220823987643 (c = 0.5) — reproduced exactly by my blind
LAW A crossover, i.e. by the `specification.yaml:39-40` formula. The successor run's are
54.739597462664136 and 70.73959746266414 — reproduced exactly by my blind LAW B crossover, i.e.
by the amendment's. **The frozen contract's only closed-form crossover statement is the one the
predecessor run used and the amendment repaired**, it is still on `origin/main` at blob
`989d1eaffd7406c6166739ec22f80a2a526a87c7`, and:

- it is **not among the census's five verbatim quotations**, which take C3 and C4 from that file
  and not line 39;
- it is **not among `outstanding_fix.md`'s R1–R8** residual inconsistencies, although R1 records
  a strictly less consequential omission (a `required_artifacts` file list) in the same file for
  the same reason;
- the sentence quoted above **affirmatively tells a later reader there is no closed-form law
  there to check**.

The verdict word is `fix_already_applied`, and its stated body is scoped to the implementation
and the run records, where it is correct and I confirm it. The task it answers is titled
*"Establish the committed charging-law state of `EXP-WESOVOW-001`"*, and at that scope a
governing committed artifact still carries the pre-fix law. **The verdict word is broader than
the evidence supports, by exactly one artifact — the one the census read selectively.**

This is not an accusation of concealment; the omission is consistent with the census having
searched `specification.yaml` for controls rather than for law statements. It is a real
incompleteness in a census, which is the one artifact type whose value is entirely in its
completeness. `outstanding_fix.md`'s closing test — "If a future census finds the serialized law
at `cost_model.py:239` … differing" — is likewise indexed only on the implementation, so a
future census run to that test would miss it again.

### 4.3 What this package licenses, and the shortest over-reading paths

Enumerated as the joint requires. For each: the sentence, the shortest path a later reader could
take, and what actually blocks it.

**S1 — `source_state_census.md`, "VERDICT: `fix_already_applied`."**
*Path:* fix applied → the cost model is correct → the `p^{1/3}` cost model is validated → a
security conclusion. *Blocked by:* the verdict is a string comparison between an implementation,
two run records and a frozen amendment. It asserts nothing about whether the law models
van Oorschot–Wiener correctly; the census says so itself ("It does not establish that the
corrected law is the *right* model"). *Residual risk:* the verdict word travels well and the
disclaimer does not; and per §4.2 the word already overreaches its own artifact set by one file.

**S2 — `anchor_reconciliation.md`, "Under the `fitted_opt` anchor, that recomputation and the
committed `RUN-WESOVOW-201692-001` cells agree exactly (`0.0` bits) at all 120 overlapping
cells."**
*Path:* exact agreement over 120 cells → independently validated → citable. *Blocked by:*
§2(a) — it is arithmetic identity with the same implementation's output under the same law from
the same anchors. *Residual risk:* highest of any sentence in the package. "`0.0` bits over 120
cells" is the most quotable number here and the least informative.

**S3 — `anchor_reconciliation.md`, "The `fitted_opt` / `PAPER_PAIRS` divergence is **not an
arithmetic error** and **not a formula difference**. It is a genuine difference between two
committed inputs."**
*Path:* not an error → both are legitimate → pick either → cite. *Blocked by:* the same artifact
declines to choose an anchor. *Residual risk:* real, and §3.2 shows the sentence is too kind to
`PAPER_PAIRS` — "genuine difference between two committed inputs" reads as two measurements of
one thing, and at three of five field sizes one of them is not a value of the model at all.

**S4 — `anchor_reconciliation.json`, `citation_prohibited: false` on 192 rows.**
*Path:* machine consumer honours the flag, quotes an unflagged sign. *Blocked by:* nothing.
This is the §3.3 break.

**S5 — `anchor_reconciliation.json` row field `log2speedup_vs_DG_current_law`, present on every
row.** *Path:* quote a "speedup versus Delfs–Galbraith" at any unflagged field size. *Blocked
by:* the batch's `claim_ceiling` and each artifact's claim boundary — which are prose in the
`.md` files and in one `claim_boundary` string at the top of the JSON, while the number sits in
240 rows. *Residual risk:* a field named `log2speedup_vs_DG` is a comparison to a cryptanalytic
baseline; it is the shape of the claim the ceiling forbids.

**S6 — `outstanding_fix.md` R2**, that a future `cost_model.py` invocation without
`WESOVOW_RAW_PATH` "would write into the `RUN-WESOVOW-201692-001` directory, overwriting a
committed run artifact", recorded "without asserting it is an error."
*This is an under-read rather than an over-read, and I am recording it as a finding.* A standing
path by which an immutable run receipt can be silently overwritten is an evidence-integrity
hazard, not a bookkeeping note. It is correctly out of this task's authority to fix, and it
should not leave this batch classified as a non-defect.

**S7 — `GOAL-SSI-001` status.** Nothing in the package bears on it. The batch's `claim_ceiling`
is explicit that no completion criterion is met or approached, `DEC-20260809-c1066f` records
`official_research_state_changed: false`, and `EV-SSI-12c22e` is `direction: neutral`,
`strength: inconclusive`. I found no sentence that could be read as goal progress.

### 4.4 A procedure observation the round should record

`review_plan.procedure_deviations` is `[]`. Meanwhile
`BATCH-256a94/CORRECTION-20260904-rg0-timing.md` — committed at `19f3a222b`, 17:12:08 UTC,
before the snapshot at 17:16:42 and before either reviewer ran — states, of the very verdict
under review, that it "is unaffected and **stands**", under the heading *"Scope: a timing claim
only."* Correcting the record promptly was right, and the note is scrupulous about what it
corrects. But affirming a reviewed verdict in a committed batch artifact before the review round
reports is the kind of act AGENTS.md asks to be written into `procedure_deviations` rather than
quietly absorbed, precisely because it is not self-documenting. I raise it as an observation for
the composing Coordinator; it changes none of my verdicts and I did not treat the note as
evidence for anything.

---

## 5. The proves-too-much control

Run on all three declared known-false objects. I state, for each, the outcome required by the
declared `failure_signature`, what the package's own procedure did, and my independent check.
Then the fourth object, which the plan did not declare and on which the procedure **passes where
the conclusion is false**.

### Object 1 — the predecessor law as serialized in `RUN-WESOVOW-001/raw-result.json:13`, for which "this law satisfies the C4 cap requirement at `w = M`" is KNOWN FALSE

*Required:* report a cap violation. *Procedure did:*
`controls.proves_too_much.object_1_…: procedure_reported_cap_violation: true`, five rows, each
`satisfies_C4: false`, deficits −46.63890914332589 / −68.74382679408042 / … . *My check:* the
deficit must be exactly `0.5·log2 M`; my blind §1.4 column gives 46.639, 68.744, 90.718,
101.654, 134.343 — agreeing at all five. RG-4 separately records
`predecessor_law_violates_cap_everywhere: true`. **Correct negative. Does not prove too much.**

*Objection to the object, not to the result.* Its known-falseness is not arithmetic. Under the
predecessor's own semantics `T_full` named the `w = 1` endpoint, and
`T(w) = T_full/√min(w,M)` is then unremarkable; it violates C4 only because C4 defines `T_full`
as the `w = M` endpoint. `CORR-20260806-3ac71e` identifies exactly this as "a naming collision
on `T_full`" and settles it by reading the frozen paper. So object 1 is known-false relative to a
recorded interpretive ruling. That is a legitimate frame — C4 is a specification control — but
the object tests the procedure's fidelity to that ruling, not to a fact, and the round should not
describe it as more than that.

### Object 2 — a synthetic anchor with `log2 M = 0`, for which "the corrected law and the predecessor law are distinguishable at the probe" is KNOWN FALSE

*Required:* report no discrimination. *Procedure did:*
`object_2_…: procedure_reported_no_discrimination: true`; every synthetic row `100.0` under both
laws, `distinguishable: false`; RG-3 records `synthetic_log2M_0_reports_no_difference: true`.
*My check:* with `log2 M = 0` and `log2 w ≥ 0`, the corrected law's penalty is
`0.5·max(0, −log2 w) = 0` and the predecessor's is `−0.5·min(log2 w, 0) = 0`; both collapse to
`log2 T_full`. **Correct negative. Does not prove too much.**

*Objection: this is the weakest possible null object.* It is known-false because the two laws are
**pointwise identical** there — both clamps saturate — so "no discrimination" is entailed by the
same `max(0, ·)` identity that makes RG-4's cap arm entailed. It shows only that the procedure
does not manufacture a difference between two expressions that are equal. It cannot show the
procedure avoids manufacturing differences where the laws genuinely differ but the probe should
not resolve them. A null object whose falseness is an identity is a tautology control; the plan
counted it as one of three.

### Object 3 — the predecessor run's committed vOW rows fed to the successor law's checker, for which "these values agree with the corrected law" is KNOWN FALSE

*Required:* report disagreement. *Procedure did:*
`object_3_…: procedure_reported_disagreement: true`, `mismatch_count: 120`,
`max_abs_diff_bits: 134.34336795088666`. *My check:* the disagreement must be exactly
`0.5·log2 M` per field size, maximised at `log2 p` = 768; my blind value there is 134.343.
**Correct negative. Does not prove too much.**

*Objection: objects 1 and 3 are one object.* Both measure `0.5·log2 M`, the single constant
separating the two laws. RG-3's `min_abs_separation_bits: 46.25` is the same constant again —
it is `0.5 × 92.5`, i.e. half the `PAPER_PAIRS` `log2 M` at `log2 p` = 256, the smallest
`log2 M` in the grid. So of three declared known-false objects, two probe one number and the
third is an identity. **The declared proves-too-much control has the coverage of one quantity
and one tautology.**

*What RG-3's 46.25-bit margin therefore cannot see.* Its failure condition fires only if a real
cell shows `|current − predecessor| ≤ 1e-12`. It has only ever been exercised against a
difference of 46.25 bits or larger, so it pins the procedure's discrimination threshold to
somewhere in `(0, 46.25]` bits and nowhere tighter: **any defect perturbing `log2 T(w)` by less
than 46.25 bits is invisible to it.** Concretely it cannot see (i) the entire overhead term —
`c·√(log2 p)` reaches 32 bits at `log2 p` = 256, `c` = 2, below the margin, and in any case the
term is added identically to both laws so the comparison is insensitive to it *by construction*;
(ii) a change in the exponent of the memory-deficit term — `0.45` in place of `0.5` moves values
by at most ≈ 3.2 bits at `log2 p` = 256; (iii) a mixed-anchor defect, ≤ 1.76 bits; (iv) the
anchor divergence itself, 0.18–3.22 bits — the quantity this batch exists to study.

### Object 4 — UNDECLARED, and the procedure PASSES where the conclusion is false

*Object:* the `PAPER_PAIRS` anchor at `log2 p` ∈ {256, 384, 512}, for which the conclusion
**"this pair is an admissible `(T_full, M)` input to this cost model"** is KNOWN FALSE, by §3.2:
its time lies below the minimum the model attains on its own declared optimizer grid.

*Required by the declared `failure_signature` had it been listed:* report the negative outcome —
refuse the anchor, or flag those rows as off-curve.

*What the procedure does:* it accepts the pair, applies `L_curr` to it, and emits 120 fully
formed rows carrying `log2T_w_current_law`, `log2w_star_current_law` and
`log2speedup_vs_DG_current_law`, of which 72 sit at the three infeasible field sizes. No field
in the schema records that the anchor is off-curve, and 48 of those 72 rows carry
`citation_prohibited: false`.

**This is a pass where the conclusion is false, and it is the control's one genuine break.**
Where in the argument the survival happens is worth naming, because that is the finding: the law
`log2 T_c(w) = log2 T_full + c√(log2 p) + max(0, (log2 M − log2 w)/2)` is *total* — it accepts
any real pair `(log2 T_full, log2 M)` and returns a well-formed number. Nothing in the law, and
nothing in any declared control, ever asks whether the pair it was handed is reachable by the
model that the law is supposed to describe. The procedure's agreements elsewhere are not thereby
void — they are agreements about arithmetic, and I independently confirmed all 240 of them — but
its *outputs at the `PAPER_PAIRS` anchor* carry no warrant that they describe this cost model.

The producer is not silent on the underlying point: it states the two anchors "are not obviously
the same quantity" and that one is an external report. It did not have the feasibility fact, and
no control looked for it.

---

## 6. Objections, controls, and the narrowest statement

### Objections

- **O1 (J6, break).** `specification.yaml:39-40` still states the pre-fix analytic crossover; it
  is not among RG-0's five quotations, not among `outstanding_fix.md`'s R1–R8, and the census
  affirmatively describes the file as stating no closed-form law. §4.2.
- **O2 (J4, break).** `citation_prohibited` is scoped by field size while the phenomenon it
  encodes occurs at `log2 p` = 256, `log2 w` ∈ {50, 70}, on rows flagged `false`. §3.3.
- **O3 (J4, comparability).** `PAPER_PAIRS` is not a point of this cost model at `log2 p` ∈
  {256, 384, 512}; its time is below the model's attained minimum. The anchors are different
  kinds of quantity, not two estimates of one. §3.2.
- **O4 (proves-too-much, break).** The procedure accepts and fully processes that infeasible
  anchor, on 72 rows. §5, object 4.
- **O5 (control coverage).** Objects 1 and 3 and RG-3 all measure `0.5·log2 M`; object 2 is an
  identity; RG-4's cap arm is entailed (disclosed by the producer, and confirmed blind in §1.5).
  The frozen contract contains **no** control that distinguishes the pre-fix law from the
  corrected one other than C4 — which is the entailed one. §1.5, §5.
- **O6 (presentation).** "max |Δ log2T(w)| over the 24 (budget, c) cells" is one number, not a
  maximum over 24; the quantity is `w`- and `c`-independent. §3.4.
- **O7 (integrity, out of scope but recorded).** R2's default output path is a live route to
  overwriting an immutable run receipt, classified as a non-defect. §4.3 S6.
- **O8 (receipt).** The snapshot receipt's declared `parent_sha` is not the snapshot commit's
  parent; content hashes verify, so the package is admissible under the content-first rule. §4.1.
- **O9 (procedure).** `procedure_deviations: []` alongside a committed pre-review artifact
  affirming that the verdict "stands". §4.4.

### Required controls

- **RC-1 (cheapest discriminating control in the whole round).** Verify the five `PAPER_PAIRS`
  literals against Section 4.1 of `inputs/P13-WESOLOWSKI-2026/paper_fulltext.md`, with page or
  line locators. This is a text lookup. **Not performed here: that path is outside my declared
  `read_scope`, and I did not exceed it.** Its status is therefore **undetermined**, and I found
  no committed record in this batch or in `BATCH-eb0a7e`'s readable artifacts in which any agent
  checked it. The anchor the round treats as its external reference has, so far as I can
  determine from committed state, never been compared with the external source.
- **RC-2 (anchor feasibility).** Before any anchor is used, compare its `log2 T_full` with the
  model's attained minimum on the contract's optimizer grid, and record any anchor lying below it
  as off-curve. Five comparisons against committed literals; catches O3 and O4.
- **RC-3 (null object for the sign disagreements).** Recount sign flips using two synthetic
  anchors separated by the same per-field constant. A matching count establishes the flips as a
  property of grid placement — a controlled null — rather than of the cost model. §3.4.
- **RC-4 (a discriminating control with the right resolution).** Replace or supplement RG-3 with
  one whose known difference is set at the scale the round cares about (≈ 0.2–3.2 bits), so that
  a passing result bounds the procedure's resolution somewhere useful. §5.
- **RC-5 (predicate-scoped citation flag).** §3.6.
- **RC-6 (contract reconciliation).** A recorded amendment or superseding note reconciling
  `specification.yaml:39-40` with the frozen crossover, or at minimum an entry in the residual
  list. O1.
- **RC-7 (provenance).** Attest, or record as unattestable, the two runs whose manifests carry
  `dirty_tree: true`.

### Counterexample / mutation

The cheapest mutation that every declared control would have missed: **swap `log2 M` between the
two anchors inside the 120 `PAPER_PAIRS` rows.** RG-1 and RG-2 compare only against committed run
cells, which exist for `fitted_opt` alone; the perturbation is `|Δ log2M|/2 ≤ 1.76` bits, two
orders below RG-3's 46.25-bit margin; RG-4's cap identity is anchor-agnostic and would still hold;
and the task card's own prohibition on mixed-anchor rows is discharged only by an assertion about
`reconcile.py`, which reviewers on this joint are blind from. **I ran the control that catches it**
(§2b): 0 mixed-anchor rows in 240, and all 240 `log2T_w` and `log2w_star` values reproduce from
row-local anchors under my blind law to `0.000e+00` bits. The mutation is refuted for this
package; the gap in the control set is not.

### Baseline comparison

The only baseline in play is the Delfs–Galbraith figure the contract fixes by C2,
`log2 T_DG = log2(p)/2`, which I verified is what all 240 rows carry (128/192/256/288/384). I make
**no** comparison against Pollard-rho, BSGS, or any specialized isogeny baseline, and no
security, standardized-parameter, exponent or asymptotic claim in either direction: this package
computes a declared cost model on committed literals and constructs no attack, and neither does
this review. The one baseline-facing observation I do make is negative and internal — the sign
of the model-versus-`T_DG` comparison is anchor-dependent at more cells than the citation flag
covers (§3.3), and `dominated_by` is therefore **not assessable** from this package: no row
carries a memory-and-time Pareto comparison against any external method, and none should be
inferred from `log2speedup_vs_DG_current_law`.

### Narrowest supported statement

> On the artifacts named in §8, at snapshot commit `5872cf99a2e71c0455502244047ad3c2f019ccbc`:
> the charging law carried by `cost_model.py`, by `RUN-WESOVOW-201692-001`, by the frozen
> amendment `TASK-20260809-ef3e58`, and by the `BATCH-eb0a7e` recomputation is one law, and it
> is the law forced by the frozen specification's C3 and C4 — established here by a derivation
> that read neither implementation, and reproducing all 240 committed rows and both runs'
> crossover values to `0.000e+00` bits. The repair is committed and reachable from
> `origin/main`, and reached it after `BATCH-eb0a7e`'s snapshot base. The `fitted_opt` anchor is
> independently reproducible from the frozen contract to ≤ 2.5e-4 bits. Two things do **not**
> follow and are not supported: that no pre-fix law statement remains in a governing committed
> artifact — one does, at `specification.yaml:39-40` — and that the unflagged rows of
> `anchor_reconciliation.json` are citation-eligible — at least two are not, on the
> prohibition's own rationale. Everything above is scoped to the five field sizes, six memory
> budgets and four overhead scenarios of this frozen grid, to this cost model, and to these two
> anchors. Nothing here is a measurement, an attack, or a statement about any scheme, parameter
> set, exponent, or security margin.

### Next concrete action

**RC-1: verify the five `PAPER_PAIRS` literals against Section 4.1 of the frozen paper, with
locators, in a task whose `read_scope` includes `inputs/P13-WESOLOWSKI-2026/paper_fulltext.md`.**
It is the cheapest step in the round, it is the only one that can distinguish a transcription
defect from a model defect from a genuine external disagreement, and §3.2 shows the question is
live: at three of five field sizes the transcribed time is not attainable by the model. Until it
is answered, the anchor choice cannot be settled and the prohibition should not be lifted.

---

## 7. Compliance and limits

- No status changed, no ledger record written, nothing committed, nothing staged. No file under
  `experiments/` was modified, moved, regenerated, or executed; my checks read the run records
  and the specification and ran only my own throwaway arithmetic.
- The P=512 citation prohibition is restated verbatim in §3.6 and is **not lifted**. I state no
  P=512 crossover value and no `w = 2^80` sign, in any anchor, run package, paraphrase, rounding,
  or sign-only summary, and I use neither as an intermediate step. §1.4 deliberately withholds the
  crossover grid I computed blind. I note, as a reviewer's observation, that the prohibited
  quantity is recomputable in one line from the frozen contract and the committed literals, which
  is why it is a *citation* boundary and not a secrecy one — and why RC-5's predicate scoping
  matters more than the boundary's tightness.
- No security, standardized-parameter, exponent, or asymptotic claim in either direction. No
  attack is constructed or described.
- I report only on J4 and J6 and return no whole-claim verdict. J1, J2, J3 and J5 are invisible to
  me by construction; where my work touches them (my §4.1 re-check of the census's git evidence,
  my §1.5 and §5 observations on control capability) it is incidental to my own joints and the
  Coordinator should compose it against the owning reviewer's report, not in place of it.
- **Budget disclosure.** `maximum_runs: 2`. I executed **zero** runs of any experiment,
  producer implementation, or artifact under `experiments/`. I invoked my own throwaway analysis
  script nine times (two of which aborted — a `ValueError` on an out-of-range Dickman argument,
  and a numerically diverging ρ variant that I discarded and replaced). I read that budget as
  bounding executions of experiment or producer code, consistent with this batch's own
  characterisation of the work as "arithmetic on already-committed literals"; I flag the
  ambiguity rather than resolve it silently, and the Coordinator may rule otherwise.
- **An honest negative about my own instrument.** My first Dickman ρ (marched DDE, and later a
  log-domain variant) diverges past `u ≈ 8`, reproducing precisely the instability
  `specification.yaml`'s `why_not_dde_marching` note records — including, in one intermediate
  computation, a spurious low optimum of the same kind the specification says its own first run
  hit. I discarded that computation rather than report it, and my §3.2 argument was rebuilt to
  need no global search at all: it rests on the contract's declared optimizer objective plus the
  committed `optimal.log2T` literals. Every ρ value I do rely on lies at `u ∈ [3.49, 5.40]`,
  where my implementation is accurate to ≤ 8.7e-6 relative against published ρ values.
- **Undetermined, and reported as such:** RC-1 (transcription fidelity of `PAPER_PAIRS`); the
  historical execution provenance of both runs (`dirty_tree: true`); whether `reconcile.py`'s
  anchor paths mix (assertion untested by any control — but its observable consequence is
  refuted by §2b); and the resolved-model verification of this session (§8).

---

## 8. `review_attestation`

```yaml
review_attestation:
  task_id: TASK-20260904-22e444
  role: red-team
  round_plan: TASK-20260904-1f4e2f
  package_reviewed:
    snapshot_commit: 5872cf99a2e71c0455502244047ad3c2f019ccbc
    receipt: coordination/goals/GOAL-SSI-001/batches/BATCH-256a94/archives/TASK-20260904-47c3ea/snapshot_commit_receipt.json
    content_verification: >-
      All seven declared source_path_sha256 values independently recomputed from the
      snapshot commit's tree and matching. Declared parent_sha a769ca3e7 is an ancestor
      but is not the snapshot commit's parent (26a8d6061); commit_sha is null and the
      receipt records pending_post_commit. Admissible under the content-first rule;
      the parent mismatch is recorded, not waived.
  joints_owned:
    - J4 anchor reconciliation and citation eligibility
    - J6 scope and provenance of the fix-status verdict
  also_owned:
    - proves_too_much control
    - blind_rederivation
  verdicts:
    J4 anchor reconciliation and citation eligibility: breaks
    J6 scope and provenance of the fix-status verdict: breaks
    proves_too_much control: breaks
    blind_rederivation: holds
  verdict: breaks
  verdict_scope: >-
    Both breaks are narrow and neither overturns the package's arithmetic, which I
    reproduced independently to 0.000e+00 bits on all 240 rows. J4 breaks on citation
    eligibility, not on the reconciliation. J6 breaks on the scope of the verdict word,
    not on its provenance, which I re-verified and which holds. The proves-too-much
    control passes on all three declared objects and breaks on a fourth I add.
  read_sibling_reports: false
  sibling_directory_encountered: >-
    coordination/goals/GOAL-SSI-001/batches/BATCH-256a94/reviews/ appeared as a directory
    entry in one listing of the batch root. I did not list its contents and did not open
    any path under reviews/TASK-20260904-e13cf2. I hold no knowledge of the sibling's work.
  blind_from_respected: true
  blind_from_paths_not_opened:
    - coordination/goals/GOAL-SSI-001/batches/BATCH-256a94/tasks/TASK-20260904-1f4e2f/reconcile.py
    - coordination/goals/GOAL-SSI-001/batches/BATCH-256a94/tasks/TASK-20260904-1f4e2f/law_equivalence.md
    - coordination/goals/GOAL-SSI-001/batches/BATCH-256a94/tasks/TASK-20260904-1f4e2f/controls_report.md
    - coordination/goals/GOAL-SSI-001/batches/BATCH-eb0a7e/tasks/TASK-20260824-dd5b5c/corrected_charging.py
    - coordination/goals/GOAL-SSI-001/batches/BATCH-eb0a7e/reviews/TASK-20260824-5b150a/validation_report.md
  blind_rederivation:
    written_before_any_producer_artifact_was_opened: true
    section: 1
    sources_at_time_of_writing:
      - experiments/EXP-WESOVOW-001/specification.yaml
      - own arithmetic (independent Dickman rho, not the specification's Laplace method)
    note: >-
      experiments/EXP-WESOVOW-001/cost_model.py was NOT read before or during the blind
      derivation. It is not in blind_from, but reading it would have contaminated the
      derivation, so it was deferred and is listed in sources_read below.
  sources_read:
    - AGENTS.md
    - agents/red-team.md
    - .claude/agents/red-team.md
    - experiments/EXP-WESOVOW-001/specification.yaml
    - experiments/EXP-WESOVOW-001/cost_model.py
    - experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-001/raw-result.json
    - experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-201692-001/raw-result.json
    - coordination/goals/GOAL-SSI-001/batches/BATCH-256a94/tasks/TASK-20260904-22e444/task_card.yaml
    - ledger/handoffs/TASK-20260904-22e444.yaml
    - coordination/goals/GOAL-SSI-001/batches/BATCH-256a94/tasks/TASK-20260904-1f4e2f/task_card.yaml
    - coordination/goals/GOAL-SSI-001/batches/BATCH-256a94/tasks/TASK-20260904-1f4e2f/source_state_census.md
    - coordination/goals/GOAL-SSI-001/batches/BATCH-256a94/tasks/TASK-20260904-1f4e2f/outstanding_fix.md
    - coordination/goals/GOAL-SSI-001/batches/BATCH-256a94/tasks/TASK-20260904-1f4e2f/anchor_reconciliation.md
    - coordination/goals/GOAL-SSI-001/batches/BATCH-256a94/tasks/TASK-20260904-1f4e2f/anchor_reconciliation.json
    - coordination/goals/GOAL-SSI-001/batches/BATCH-256a94/batch.yaml
    - coordination/goals/GOAL-SSI-001/batches/BATCH-256a94/CORRECTION-20260904-rg0-timing.md
    - coordination/goals/GOAL-SSI-001/batches/BATCH-256a94/archives/TASK-20260904-47c3ea/snapshot_commit_receipt.json
    - coordination/goals/GOAL-SSI-001/batches/BATCH-256a94/dispatch_queue.json
    - coordination/goals/GOAL-SSI-001/batches/BATCH-2e6130/tasks/TASK-20260809-ef3e58/protocol_amendment.yaml
    - git history and object contents (read-only) for 7d188a7c3, bd47a3f5c, e45861af5,
      2675886ea, 6fda12409, 27efe0cdc, 5872cf99a, 26a8d6061, a769ca3e7, c1a39ee5a, 19f3a222b
  not_read_though_in_read_scope:
    - docs/claims-and-verification.md
    - docs/inventor-protocol.md
    - templates/research-records.md
    - ledger/evidence/EV-WESO-001.yaml
    - ledger/evidence/EV-SSI-4b17e7.yaml
    - ledger/evidence/EV-SSI-e8cc71.yaml
    - ledger/evidence/EV-SSI-12c22e.yaml
    - ledger/decisions/DEC-20260809-c1066f.yaml
    - ledger/decisions/DEC-20260809-39eb45.yaml
    - ledger/decisions/DEC-20260824-384e78.yaml
    - coordination/goals/GOAL-SSI-001/batches/BATCH-eb0a7e/batch.yaml
    - coordination/goals/GOAL-SSI-001/batches/BATCH-eb0a7e/tasks/TASK-20260824-dd5b5c/anchor_sensitivity.md
    - coordination/goals/GOAL-SSI-001/batches/BATCH-eb0a7e/tasks/TASK-20260824-dd5b5c/recomputed_table.json
    - note: >-
        Statements about these records in this report are attributed to the census's
        reading of them and are marked as such; I did not independently confirm their
        contents. Where the census's characterisation of a record is load-bearing for my
        verdicts it is not, in fact, load-bearing: O1 rests on specification.yaml and the
        protocol amendment, both of which I read directly, and O2-O4 rest on
        anchor_reconciliation.json and committed literals.
  read_scope_exceeded: false
  inference:
    requested_policy: review-adversarial
    requested_reasoning_effort: xhigh
    fallback_allowed: false
    degraded_allowed: false
    independent_session_required: true
    served_by: >-
      Independent Claude Code red-team subagent session. .claude/agents/red-team.md
      carries `effort: xhigh`, derived from roles.yaml -> review-adversarial. Resolved
      model identifier as reported to this session: claude-opus-5.
    fallback_used: false
    degraded_requirements: []
    model_verified: undetermined
    model_verified_note: >-
      I did not run `python3 -m orchestration.adapter doctor --probe`; the resolved
      identifier is therefore unverified configuration by AGENTS.md's own definition and
      is recorded as such rather than asserted. No downgrade was requested or accepted; had
      the session been unable to honour xhigh on an independent session I would have
      refused rather than proceed.
  independence:
    originated_no_reviewed_claim: true
    producer_messages_relied_on: none
    coordinator_prior_treated_as: an unverified expectation, tested in section 4.1
    batch_opening_observation_treated_as: inadmissible; not cited as support anywhere
  runs_executed_against_experiments: 0
  status_changed: none
  records_written: none
  committed: false
```
