# Experiment suite for Jao–Miller–Venkatesan 2005 (arXiv:math/0411378v3)

**"Do All Elliptic Curves of the Same Order Have the Same Difficulty of Discrete Log?"**

Status: **DRAFT DESIGN — not approved, not executed.** No evidence record exists
for any experiment below. Coordinator approval is required before any run.
Author: top-level session, 2026-07-26. Target goal: `GOAL-ECDLP-001`
(currently `paused`; this suite is queued, not dispatched).

---

## 1. What the paper actually proves, and where it leaves room

JMV prove (under GRH) two things and explicitly disclaim a third:

| # | Claim | Location | Testable content |
|---|---|---|---|
| T1 | The horizontal-isogeny graph on **one level** of an isogeny class is an expander; nontrivial eigenvalues satisfy `λ_χ = O(m^{1/2} log|mD|)` for `m = (log q)^{2+δ}` | Thm 1.1, Lem 4.1 | The **implied constant is unspecified**. Whether the bound is non-vacuous at `q ≈ 2^256` is not established by the paper. |
| T2 | dlog is random self-reducible **within a level** in `polylog(q)` oracle queries | Cor 1.2 | `polylog(q)` counts **isogeny steps**, not field operations. Each step costs `O(ℓ³)` for `Φ_ℓ` with `ℓ ≤ m`. The **concrete** cost of the reduction is never computed. |
| T3 | *Not proved:* equivalence **across levels**; holds only if `c_π` is polynomially smooth | §1.1, §6 | The `c_π` distribution claim (`Pr[P(c_π) > β] = O(1/β)`) is a **heuristic**, stated loosely, never measured. |

Three gaps are therefore measurable, and none of them requires breaking anything:

- **G1 (constants).** T1/T2 are asymptotic. Nobody has published the concrete
  spectral gap or the concrete reduction cost at cryptographic sizes.
- **G2 (equidistribution ≠ equal cost).** T2 gives cost equality *up to the
  polylog reduction overhead*. It does **not** prove that dlog cost is constant
  across a level. A level-internal cost spread smaller than the overhead is
  fully compatible with the theorem and has never been measured.
- **G3 (the admitted hole).** Cross-level behaviour, i.e. exactly the case where
  "same order ⇒ same difficulty" could fail. JMV say a general equivalence
  "might be false" under unbalanced attacks.

## 2. Scouting result (exact, NOT reviewed): a Figure 1 inconsistency

> **Amended 2026-07-26 after Coordinator review (DEC-20260726-001/003).** Two
> corrections to what this section originally claimed:
>
> 1. **The claim is narrower than "the paper has an error."** The Figure 1 values
>    used here come from a plain-text paste, not from arXiv:math/0411378v3, and
>    that paste contains **no P-224 row at all**. A dropped or shifted row *in the
>    paste* produces exactly the discrepancy below. Until the table is checked
>    verbatim against the source by someone who did not produce the transcription,
>    the only supported statement is *"the transcription we hold is inconsistent
>    with these curves' parameters"* — not that the paper is wrong. This is
>    condition C1 and it gates every conclusion in this suite, since Prop 3.1's
>    inequality and Lemma 4.1's normalization are also held only in paste form.
> 2. **`c_π` was defined incorrectly.** It is the conductor of `Z[π]`
>    (`d_π = c_π² d_K`, `d_K` fundamental), not "the largest integer whose square
>    divides `d_π`". For `d_π = s²u` with `u` squarefree: `c_π = s` if
>    `u ≡ 1 (mod 4)`, else `c_π = s/2`. The mod-9 argument below **survives
>    unchanged** — 3 is odd, so `3 | c_π` forces `9 | d_π` on either branch — but
>    any `c_π` *values* or level counts computed under the old definition do not.
>    The correction bites only when `4 | d_π`; every prime-field curve of odd
>    prime order has `t` odd and so is unaffected, while the Koblitz curves over
>    `F_2^m` **are** affected — and those are the intended positive control.

Run before designing, to check whether the paper's own table is reproducible.
Script: `experiments/EXP-JMV-001/cpi_audit.py`.

For NIST P-256, using the standard field prime, generator `G`, and group order
`n` — independently confirmed by checking `G` lies on the curve and `[n]G = O`:

```
t = p + 1 - n = 89188191154553853111372247798585809583
-d_π = 4p - t²  ≡  3 (mod 9)
```

`3 ‖ (-d_π)`, so `9 ∤ d_π`, so **`3 ∤ c_π`** — `c_π` is the conductor of `Z[π]`,
the unique positive `f` with `d_π = f²d_K` and `d_K` fundamental (see the
amendment above; 3 is odd, so `3 | c_π` forces `9 | d_π` on either branch of that
definition). Figure 1 lists **`c_π = 3`, `P(c_π) = 3` for P-256**. That entry is
inconsistent with the curve's own parameters. Trial division to `10⁶`
finds no square factor at all, so `c_π(P-256) = 1` or all its prime factors
exceed `10⁶` (settling this needs a 255-bit factorization — the paper itself
credits Peter Montgomery for factoring assistance, so this is a real cost).

Meanwhile **P-224**, which is *absent* from Figure 1, does satisfy `9 | (-d_π)`,
hence `3 | c_π`. The most economical reading is a row misattribution between
P-224 and P-256.

This is a mod-9 computation on published constants — exact, cheap, and requiring
no factoring. It is recorded here as **scouting, not evidence**; EXP-JMV-001
promotes it to a reviewed record.

### 2b. The Koblitz rows: pipeline validated, and a second inconsistency

The `d_π = −7c_π²` positive control turns out to need **no binary-field
arithmetic at all** — an earlier version of this doc wrongly said it did. For
`E_a: y²+xy = x³+ax²+1` over `F_2`, Frobenius satisfies `τ² − μτ + 2 = 0` with
`μ = (−1)^{1−a}`, so `disc = −7`, and the trace over `F_2^m` follows an **integer**
Lucas recurrence `t_k = μt_{k−1} − 2t_{k−2}`, `t_0 = 2`, `t_1 = μ`. This *derives*
the group order rather than trusting a published `n` — strictly stronger than the
`[n]G = O` check, which only confirms a published `n` against a published `G`.

Results, all five K-curves: derived order `= cofactor × n_NIST` ✓, and
`d_π = −7c_π²` exactly ✓.

An earlier version of this section said "`c_π` here is only 81–285 bits, so it
factors completely." **That is false** and the reason it doesn't matter is more
interesting than the claim: K-409 leaves a ~95-bit residual after its listed
factors and K-571 a ~263-bit one, and 263 bits is not routinely factorable. What
actually makes the K-rows checkable is that **verifying a *complete claimed*
factorization requires no factoring at all** — only multiplication and primality
tests. K-163/233/283 carry a complete claimed factorization in the paste and are
therefore fully checkable; K-409/K-571 do not (their `P(c_π)` values are
line-wrapped into unusability) and stay **censored, level counts included**.

| row | Figure 1 as pasted | computed | verdict |
|---|---|---|---|
| K-233 | `5610641·85310626991·P`, `P = 150532234816721999` | identical | **exact match** |
| K-283 | `1697·162254089·P`, `P = 1779143207551652584836995286271` | identical | **exact match** |
| K-163 | `45641·82153·56498081·P`, `P = 86110311` | `45641·82153·8610311·56498081` | **mismatch** |

Two consequences — and they do **not** point the same way:

- **The pipeline is validated.** K-233 and K-283 reproduce exactly, including
  primality of every listed factor and maximality of `P(c_π)` (established by a
  full Sage factorization, not by the product identity alone). That is a strong
  positive control on the *computation* — the Lucas recurrence, the conductor
  definition, and the `−7c_π²` identity are jointly correct.
- **K-163 is inconsistent however it is read.** The printed `P(c_π) = 86110311`
  is **composite** (`3·7·367·11173`), so it cannot be any prime factor. The true
  fourth factor is `8610311` (prime), and the *largest* prime factor is
  `56498081` — which Figure 1 already lists among the other factors. So the
  `P(c_π)` column is wrong on that row on either reading of the digits.

> **Overruled by Coordinator ruling (DEC-20260726-004), and the correction
> matters.** An earlier version of this section concluded that the K-233/K-283
> agreement "raises confidence in the P-256 result correspondingly." **It does
> not.** Three reasons:
>
> 1. The agreement is a strong control on the **computation** and a much weaker
>    one on the **transcription**. It shows the paste is faithful on rows it
>    contains and checks; the competing explanation for P-256 is a *dropped row*,
>    which a paste can satisfy while reproducing every row it does contain.
> 2. **There is no transfer across blocks.** The K-rows are checkable precisely
>    because Koblitz CM makes `c_π` exactly computable; the P-rows have no such
>    redundancy. K-block fidelity is not evidence of P-block fidelity.
> 3. **Decisive, and it cuts the opposite way:** K-163 shows the artifact we hold
>    is corrupt *at digit level*. The transcription defect rate in this paste is
>    no longer hypothetical — it is **measured, and nonzero, on the only rows we
>    can fully check** (1 of 3). Under a demonstrated nonzero defect rate,
>    attributing the P-256 discrepancy to the paper rather than to the paste is
>    unjustified.
>
> Note where the uncertainty actually sits: the arithmetic half of the P-256
> claim (`−d_π ≡ 3 mod 9 ⇒ 3 ∤ c_π`) is **certain** and re-checkable in one line.
> *All* residual uncertainty is transcription uncertainty. C1 is not merely still
> gating — it is the only open question in the claim.

**K-163 is not a second finding of the same class** (DEC-20260726-004, Ruling 2).
A one-digit edit repairs it to exact consistency, so the more probable cause is
internal to our own artifact. Its status is a **C1 control result** — the
measured reason the paste cannot be trusted — not a Figure 1 claim. It enters the
erratum gate only if C1 shows the source prints `86110311`, and then as *one
joint claim* with P-256, never as two replications.

One asymmetry to carry forward: if C1 passes, **K-163 becomes the headline row,
not P-256** — its compositeness certificate is refutable from the printed table
alone and is immune to any error in our curve constants, whereas the P-256
certificate depends on the published `p` and `n`.

Practical consequence for the program: the claim "10 of 11 standards curves have
a single level" rests on this table, and `cπ = 1` is what makes a curve's isogeny
class single-level. If the table is wrong for one row, the single-level census
should be re-derived rather than cited.

## 3. Why this suite is worth running — as a standalone track

> **Amended per DEC-20260726-001.** This section originally pitched the suite
> under `GOAL-ECDLP-001`. RQ-JMV-001 is **not** attached to that goal, or to
> `GOAL-CRYPTO-001`. The reason is structural before it is budgetary: the RQ's own
> constraints state that no experiment under it can produce an attack or an
> attack-cost improvement, and both goals' completion criteria require exactly
> that. Hanging it off a goal it cannot satisfy is goal drift, and it would make a
> paused campaign appear to have live qualifying work. It runs as a standalone
> track capped at 2 CPU-hours / 10 runs, consuming no goal campaign budget.
> References below to the program's cost discipline are about *method*, not about
> goal attachment.

The goal demands *complete end-to-end cost accounting* for any claimed advantage.
JMV is a **reduction**, and reductions have been audited far less carefully than
attacks. Track B applies the program's own cost discipline to a reduction: it
asks what the JMV self-reduction actually costs in field operations at 256 bits,
and at which bit size that overhead falls below the `√n` cost of just solving the
instance directly. That number does not appear in the literature and is
computable without any new mathematics.

Track C tests G2, which is where a "weak curve" could still hide *without*
contradicting the theorem. `EV-ISO-001` already probed 3 isogeny neighbours and
found nothing; Track C is the full-level census version with a permutation test,
which is a strengthening, not a repeat.

**None of this is an attack, and no experiment below can produce one.** The
honest upside is a verified structural result plus concrete constants.

---

## 4. Track A — reproduce and audit the paper's arithmetic (cheap, high confidence)

### EXP-JMV-001 — Conductor audit of the Figure 1 curve set

- **Question.** Is Figure 1 reproducible from published curve parameters?
- **Method.** For every curve in Figure 1 plus P-224: recompute `t`, `d_π = t²−4q`,
  the exact `ν_ℓ(d_π)` for all `ℓ ≤ 10⁶` by trial division, and the full `c_π`
  where the cofactor factors within budget. Report `c_π` **and** a rigorous
  lower/upper bound when it does not.
- **Positive control.** Koblitz K-curves have CM by `Q(√−7)`, so `d_π = −7c_π²`
  exactly. Verify that identity holds — it validates the whole pipeline on rows
  where the paper's values are large and specific.
- **Independent order check.** For each curve, verify `[n]G = O` before using `n`.
  Without this, a transcription error in `n` masquerades as a paper error.
- **Metrics.** `t`, `ν_ℓ(d_π)`, `c_π` (exact or bounded), `P(c_π)`, level count.
- **Falsification of the scouting claim.** Any curve where the recomputed `c_π`
  matches Figure 1 and the mod-9 result does not reproduce.
- **Budget.** < 1 CPU-hour excluding optional large factorizations; those get a
  hard cap and are reported as `unresolved`, never as `c_π = 1`.
- **Claim tier.** `crypto` — scoped to these exact named curves, arithmetic only.
- **Deliverable.** A verified table; if the discrepancy stands, a `CORR-` record
  and a `KN-LIT` entry noting the erratum.

### EXP-JMV-002 — Does `c_π` behave like the square part of a random integer?

- **Question.** §6 models `−d_π = 4q − t²` as "a random integer of size `q`" and
  derives `Pr[P(c_π) > β] = O(1/β)` and a `6/π² ≈ 0.61` squarefree density. Is
  that model correct?
- **Method.** Sample many random curves over random primes at sizes where `d_π`
  factors completely (`q` from 40 to 80 bits, ≥ 10⁴ curves per size). Compute the
  empirical distribution of `c_π`, `P(c_π)`, and the level count.
- **Control (this is the point of the experiment).** Compare against random
  integers of matched size — the paper's own null. Stratify by prime `ℓ`:
  the density of `ℓ² | d_π` should be `1/ℓ²`-ish for a random integer.
- **Predicted deviation, worth stating in advance.** `d_π ≡ 0` or `1 (mod 4)` is
  **forced**, so the prime 2 cannot behave randomly; the model is wrong at `ℓ=2`
  by construction. The real question is whether **odd** primes follow the random
  model, and whether the Hasse-interval distribution of `t` induces further bias.
- **Falsification.** Odd-prime square-density deviates from `1/ℓ²` beyond
  binomial error at fixed `ℓ`, or the `P(c_π)` tail is not `Θ(1/β)`.
- **Budget.** ≤ 8 CPU-hours; hard cap per factorization, timeouts reported as
  censored data, never dropped (censoring biases the tail, which *is* the metric).
- **Claim tier.** `medium`. Extrapolation to 256 bits is a stated conjecture, not
  a result.

## 5. Track B — concrete-parameter audit of the machinery (the substance)

### EXP-JMV-003 — Measured spectral gap vs. the GRH bound

- **Question.** Lemma 4.1's implied constant is absolute but unspecified. What is
  it, empirically?
- **Key method note (makes this cheap).** The graph is an **abelian** Cayley
  graph on `Cl(O)`, so eigenvalues are character sums and **no `h×h` matrix is
  ever needed**:
  `λ_χ = (1/e) Σ_{p ≤ m} a_p(χ)`, where a split prime `p` contributes
  `2·Re χ([𝔭])`, an inert prime contributes `0`, and a ramified prime
  contributes `χ([𝔭])`. Requires the class-group structure and the discrete log
  of each prime form in it. Feasible for `h` up to ~10⁵.
- **Scope.** Maximal orders first (`c_E = 1`), where Pari's `bnfinit` /
  `bnfisprincipal` give exact class-group discrete logs. Non-maximal orders are a
  documented extension, not part of the first pass.
- **Cross-check.** For small `h` (≤ 2000), also build the adjacency matrix and
  diagonalize numerically. Agreement of the two methods is the correctness gate;
  disagreement means the discrete-log step is wrong.
- **Metrics.** `λ_triv`, `λ_2`, the ratio `λ_2/λ_triv`, and the fitted exponent
  `β` in `λ_2 = λ_triv^β`, as functions of `(m, |D|)`.
- **Falsification.** `λ_2` exceeds `C·m^{1/2} log|mD|` for any modest `C` (would
  indicate a GRH-conditional bound failing empirically — the single most
  interesting possible outcome, and most likely a bug, so it gets replicated
  before it gets believed).
- **Budget.** ≤ 12 CPU-hours; ≥ 200 discriminants across 4 size decades.
- **Claim tier.** `medium`, with an explicit scaling analysis feeding EXP-JMV-004.

### EXP-JMV-004 — At what field size is the JMV reduction concretely cheaper than solving the dlog directly?

This is the experiment with the most novelty per unit of compute, and it is
**deterministic arithmetic** — no sampling, no seeds.

- **Question.** Cor 1.2 gives `polylog(q)` *oracle queries*. Converted to field
  operations, what does one random self-reduction actually cost at
  `q ∈ {2⁶⁴, …, 2⁵¹²}`, and how does that compare to Pollard rho's `√n`?
- **Method.** For a grid of `(q, δ)`:
  1. `m = (log q)^{2+δ}`; degree `k = λ_triv ≈ π(m)/2`.
  2. Bound `λ_2` two ways — (a) the **proven** GRH bound with explicit constants
     (Bach–Sorenson, the paper's ref [2]), and (b) the **measured** constant from
     EXP-JMV-003.
  3. Walk length `r` from Prop 3.1: `r ≥ log(2h/|S|^{1/2}) / log(k/c)`, `h ≈ √q`.
  4. Per-step cost: root-finding on `Φ_ℓ(j(E), X)` at `O(ℓ³)` field ops for a
     **typical** step — note that a uniformly random prime `ℓ ≤ m` is typically
     of size `≈ m`, not small, so cheap `ℓ=2` steps are *not* what the theorem's
     generator set gives.
  5. Total reduction cost `= r × per-step`, versus rho at `√n ≈ q^{1/2}`.
- **Primary output.** The **crossover curve**: bit sizes where reduction overhead
  is negligible / comparable / dominant relative to the dlog itself.
- **Secondary output, and the sharper question.** Whether `log(k/c) > 0` at all
  under the *proven* bound at `q = 2²⁵⁶`. If the proven separation is vacuous at
  cryptographic sizes while the *measured* gap is healthy, then Cor 1.2 is
  asymptotically sound but **concretely unproven** at the sizes anyone deploys.
  That is a precise, publishable, non-obvious statement about a widely cited
  justification for curve selection.
- **Falsification / null.** Reduction overhead is negligible (`< 2^{-20} × √n`)
  at every size ≥ 128 bits under both bounds, and `log(k/c) > 0` throughout — in
  which case the paper's practical reading is fully vindicated and this closes.
- **Budget.** < 1 CPU-hour. Depends on EXP-JMV-003 for branch (b) only; branch
  (a) is runnable immediately.
- **Claim tier.** Analytic/`crypto`, scoped to *the stated cost model*. It claims
  nothing about actual attack cost — only about the cost of the reduction.

### EXP-JMV-005 — Is Proposition 3.1 tight?

- **Question.** How much slack is there between the proven mixing bound and real
  mixing?
- **Method.** Simulate random walks on `Cl(O)` with the JMV generator set;
  measure total-variation distance to uniform vs. step count, and the hitting
  probability of a subset `S` of size `h/polylog`.
- **Controls.** Positive: exact uniform sampling. Negative: walk restricted to
  `ℓ = 2` only (degree ≈ 2, slow mixing — the bound must clearly separate this
  from the full generator set, else the metric is insensitive). Reference: the
  proven `r` from Prop 3.1.
- **Falsification.** Measured mixing *slower* than the proven bound — a
  contradiction under GRH, so treated as a bug signal and replicated before any
  interpretation.
- **Budget.** ≤ 6 CPU-hours.
- **Claim tier.** `medium`.

## 6. Track C — the gap the paper admits (highest research value)

### EXP-JMV-006 — Equidistribution vs. equal cost: full-level census

- **Question (G2).** Within a *single level*, is dlog cost genuinely constant, or
  merely equal up to the reduction's polylog overhead?
- **Method.** Choose `p` small enough that an entire level is enumerable
  (`h ≈ √p`; `p ≈ 2²⁰` gives ~10³ curves). Enumerate **every** curve in one level.
  For each, measure cost proxies:
  - (a) exact Pollard-rho iteration count under a **fixed, curve-independent**
    partition rule, averaged over many seeds;
  - (b) Semaev `m=3` decomposition yield over a canonically defined factor base.
- **Controls.** (i) Same-curve seed-to-seed variance — the noise floor, and the
  quantity the level-internal spread must beat. (ii) Random curves of *different*
  order — the "unrelated curve" variance band. (iii) A **label-permutation test**
  for significance, so a spread is not read off eyeballed extremes.
- **Falsification.** Level-internal spread lies within the same-curve seed noise
  ⇒ "same difficulty" holds at the constant-factor level too, and G2 closes at
  toy scale.
- **Relation to `EV-ISO-001`.** That record sampled 3 neighbours of one base
  curve and found yields inside the control band. This is the whole-level version
  with a proper null distribution; it can detect a spread that a 3-point sample
  cannot. Explicitly a strengthening, and it must cite `EV-ISO-001` and report
  agreement or conflict.
- **Budget.** ≤ 16 CPU-hours, hard-capped; `maximum_runs` enforced.
- **Claim tier.** `toy`. A negative here says nothing about P-256, and the record
  must say so.

### EXP-JMV-007 (deferred, design only) — cross-level cost stratification

Tests G3: build an isogeny class with non-smooth `c_π` via CM, enumerate its
levels, measure the same cost proxies **per level**, and measure Kohel's `O(ℓ⁴)`
descent cost. If proxies differ systematically *between* levels, then "same order
⇒ same difficulty" is empirically false exactly where JMV is silent. Deferred
because it depends on EXP-JMV-006's proxy being calibrated first; a null result
there makes this uninformative.

---

## 7. Non-duplication audit

| Existing record | Overlap | Why this suite is not a repeat |
|---|---|---|
| `RQ-ISO-001` / `H-ISO-001` (`rejected_scoped`), `EV-ISO-001` | Isogeny neighbours vs PDP `d_reg` and yield | Sampled 3 neighbours of 1 base. EXP-JMV-006 is a full-level census with a permutation null. Different statistical object. |
| `ISOWALK-C1` (proposed, unscheduled) | Isogeny-graph expander walks | C1 asks whether the spectral gap beats the **birthday exponent** for collisions. Track B asks what the gap **is**, and what the **reduction** costs. Disjoint questions; EXP-JMV-003 would supply C1 its gap constant. |
| `EXP-ISADV-001` | Advice transfer across isogenous curves | Transfer of a planted advice table. Track C measures **intrinsic per-curve cost**, no advice. |
| `KN-TECH-024`, `KN-TECH-029`, `KN-OPEN-013` | Isogeny graphs, path-finding | All **supersingular** / `F_{p²}`. JMV is **ordinary** prime-field, horizontal isogenies, class-group Cayley graphs. |
| `BAR-AMORT-D2`, D1 data-movement barrier | Exponent-neutrality barriers | Track B is a **reduction cost audit**, not an attack-exponent claim, so the barriers do not pre-empt it — and it must not be written up as if it evades them. |

**Corpus gap.** JMV 2005 is **not in `knowledge/`** — no `KN-LIT` entry cites it,
despite the corpus holding 5 other Jao papers. It should be ingested via
`/curate-knowledge` regardless of whether any experiment here is approved.

## 8. Standing limits on what this suite may claim

- No experiment here can produce an ECDLP attack or an attack-cost improvement.
- Track A/B results are about **arithmetic and reduction cost**, never about the
  hardness of any dlog instance.
- Track C is `toy` tier. A null result closes the toy scope only, in the
  mandatory negative-result phrasing of `docs/evidence-and-reproducibility.md`.
- The Figure 1 discrepancy is currently **scouting**, not evidence. It becomes a
  record only through EXP-JMV-001 plus independent validation.
- GRH is assumed throughout by the paper; nothing measured here confirms or
  disconfirms GRH, and no record may imply otherwise.

## 9. Suggested order

1. **EXP-JMV-001** — hours, settles the erratum, unblocks a `KN-LIT` entry.
2. **EXP-JMV-004 branch (a)** — < 1 hour, pure arithmetic, highest insight/cost.
3. **EXP-JMV-003** — supplies the measured constant for branch (b).
4. **EXP-JMV-002**, **EXP-JMV-005** — parallel, independent.
5. **EXP-JMV-006** — largest budget, run once the proxies are calibrated.
6. **EXP-JMV-007** — only if 006 shows a measurable spread.
