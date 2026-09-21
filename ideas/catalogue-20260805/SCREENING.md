# Screening report — idea catalogue 2026-08-05 (102 ideas)

**Status: pre-ledger. This document mints nothing.** It records a screen and an
adversarial review of the 102 entries in `ideas/catalogue-20260805/`, and it
recommends what a Coordinator should do next. No `IDEA-*` identifier is minted
here, no hypothesis status changes, no experiment is approved.

---

## 1. What was screened, and by what method

All 102 entries across the nine slice files (`A1`–`A4`, `B1`–`B3`, `C1`, `C2`)
were screened entry-by-entry against the five criteria stated in `INDEX.md` §2 —
(c1) a reachable negative, (c2) no tautological gate, (c3) every load-bearing
premise re-read at the committed artifact rather than at another record's
citation of it, (c4) a positive control that can fail, evaluated *before* the
primary run, and (c5) environment honesty with a stated fallback — producing one
of three verdicts per entry: `PASS`, `REPAIRABLE` (the claim survives, the task
card does not), or `FAIL` (repairing it changes the claim). Screeners re-derived
arithmetic by hand, recomputed committed artifacts where feasible
(`n1_ms.json`, `raw-result.json`, `reversibility_check.json`), and checked
declared environment capabilities by execution rather than by assumption. Every
entry that screened `PASS` was then put through three **independent adversarial
lenses** — *tautological-gate* (is the gate evaluated anywhere the candidate
readings actually disagree?), *premise-verification* (does each load-bearing
number survive re-reading at the primary artifact, not at a record quoting it?),
and *already-closed* (does committed evidence already settle, refute, or render
vacuous the question?) — each run without sight of the others' conclusions. **A
survivor had to survive all three.** Anything refuted by even one lens is
reported as contested or refuted, never as mint-ready.

---

## 2. Headline counts

### Screening

| verdict | count | share |
|---|---:|---:|
| screened | 102 | 100% |
| `PASS` | **9** | **8.8%** |
| `REPAIRABLE` | 84 | 82.4% |
| `FAIL` | 9 | 8.8% |

Pass rate by slice: A1 0/13 · A2 0/12 · A3 2/11 · A4 1/11 · B1 2/12 · B2 1/10 ·
B3 1/8 · C1 **0/13** · C2 2/12.

### Adversarial review of the 9 that passed

| outcome | count | ids |
|---|---:|---|
| **unanimous survivors** (refuted by no lens) | **0** | — |
| contested (refuted by 1–2 of 3 lenses) | 2 | `B3-6`, `C2-1` |
| refuted (refuted by all 3 lenses) | 7 | `A3-4`, `A3-5`, `A4-10`, `B1-1`, `B1-6`, `B2-7`, `C2-7` |

**Stated plainly: the screening pass rate is 8.8%, and the survival rate after
adversarial review is 0/102 = 0%.** The pass rate is *not* high, so the
"screener was too lenient" warning does not apply in the direction `INDEX.md` §2
anticipated. The opposite warning does apply and must be recorded here:

- **A 0% survival rate is itself a signal requiring interpretation, not a
  conclusion.** Two readings are live. (i) The catalogue is genuinely not
  mint-ready — consistent with the 4-of-6 defect rate `INDEX.md` §2 measured on
  the 2026-08-03 proposals, which is what motivated screening in the first
  place. (ii) The lenses are calibrated to refute anything put in front of them.
- **No lens-calibration control was run.** No entry known to be sound was passed
  through the three lenses to confirm they can return "not refuted". That is
  criterion 4 — instrument fidelity before measurement — applied to the screen
  itself, and the screen fails it. The only evidence against reading (ii) is
  weak but real: two lenses did return `refuted: false` (premise-verification on
  `B3-6` and `C2-1`; already-closed on `C2-1`), so the lenses are not
  unconditional refuters.
- A Coordinator acting on this document should treat "0 survivors" as **"nothing
  is ready to mint today"**, not as "the catalogue is worthless". 84 entries are
  `REPAIRABLE` — that is the actionable population, and §6 is the actionable
  section.

---

## 3. Mint-ready shortlist

**EMPTY. No entry in this catalogue is recommended for `IDEA-*` identifier
minting on this screening.**

Nine entries passed the five-criterion screen. Seven were refuted by all three
adversarial lenses. Two were refuted by one or two lenses each. Zero survived
unanimously, and unanimous survival was the stated bar.

This section is deliberately not padded. The temptation — to promote the two
contested entries, or the best-scoring `REPAIRABLE` items, into a shortlist so
the document has a shortlist — is exactly the failure the screen exists to
prevent: identifiers are immutable, and a shortlist assembled to avoid an empty
table would carry its defects into the ledger permanently.

**What to do instead of minting.** The correct next action is the repair tier in
§6, and specifically its 16-entry priority sub-tier (high decision value, zero or
low cost). Repairs are cheap, reversible, and pre-ledger; minting is neither.
The single highest-value item in the catalogue by the screeners' own reckoning,
`C2-1`, is contested rather than refuted and is described in §4 — repair it and
re-screen it first.

---

## 4. Contested — passed screening, refuted by some but not all lenses

### `C2-1` — Endpoint audit of the vOW interpolation: is committed `T(w)` anchored at `w=M` or `w=1`
*Refuted by 1 of 3 lenses (tautological-gate). Survived premise-verification and
already-closed.*

- **What survived, and it matters.** Both surviving lenses independently
  confirmed the premise: three committed artifacts state three different
  functions for the same quantity, and the inconsistency is uncorrected.
  `cost_model.py:270` computes `log2Tw = log2Tfull − 0.5·min(lw, log2M) +
  overhead_bits`; `specification.yaml:146-149` requires `T(w) = T_full` for
  `w ≥ M` and exactly `T_full` at `w = M`; `execution_report.yaml:53` reports
  `T(w) = T_full·min(1, sqrt(M/w))` while conceding the cap branch is never
  exercised by the tested grid. The already-closed lens searched
  `ledger/corrections` through `CORR-20260804-1e9769` and found no correction
  touching the anchor, and independently pinned the correct form from the frozen
  source (`KN-TECH-058:112-125` quoting `paper_fulltext.md:39`). The endpoint
  evaluation separates the candidate forms by `0.5·log2 M = 46.64` bits — larger
  than every other term in the campaign combined.
- **What refuted it.** The *designated gate is placed where two of the four
  candidate forms are indistinguishable* — the same disease the entry claims to
  cure. At `w = M`, form (b) returns `T_full·min(1,1) = T_full` and the
  vOW-consistent form returns `T_full·sqrt(M/M) = T_full`: they coincide
  exactly, and `w = M` is the unique `w ∈ (0, M]` where they do (at `w = 2^30`
  they differ by 31.64 bits). Meanwhile forms (a) and vOW differ by a *constant*
  46.64 bits at every `w ≤ M`, so `w = M` is not privileged for that pair
  either. Two of three controls cannot fire: ordering control (2) reduces to the
  identity `sqrt(M/w) ≥ 1`, and absurdity control (3)'s stated criterion
  (`T(w) < T(M)` for `w < M`) is arithmetically unreachable for the monotone form
  it targets. Separately, the NIST-III correction reads `138.6` from the
  *paper* column of `RUN-WESOVOW-001/stdout.txt` into a *model*-side formula
  (the model's own `log2 M` at 384 bits is `137.4877`) — the exact class of error
  the entry is auditing.
- **Disposition: REPAIR-THEN-RECONSIDER.** The refutation is card-level, not
  claim-level. Repair: (i) evaluate all four candidate forms across the whole
  `w` range and report the pairwise separation function, rather than gating at a
  single `w`; (ii) replace the two inert controls; (iii) use the model column
  `137.49`, not the paper column `138.6`. Re-screen and re-run all three lenses
  before minting. Do not mint on this screening.

### `B3-6` — Charged-provenance audit of this program's own transfer, cover, and advice directions
*Refuted by 2 of 3 lenses (tautological-gate, already-closed). Survived
premise-verification.*

- **What survived.** Every premise opened at the artifact rather than at a
  citation: `advice_transfer.py`'s docstring ("Plant advice on E0 as the
  x-coordinates of k*G0"), `EXP-WESOVOW-001/specification.yaml` (`status:
  approved`, frozen paper section + published parameters),
  `REDUCTION_REQUIRES_UNCHARGED_ORACLE_OR_FULL_END` present independently at
  `EV-SSI-004:26`, `DEC-20260725-004:45` and `TASK-20260725-513:28`, and
  `RQ-JMV-001` present in `ledger/questions/`.
- **What refuted it.** *The instrument reads self-declarations; the hypothesis is
  about the gap between self-declaration and reality.* The procedure is "read
  each target's own record and classify its givens"; the claim is that a live
  direction sits in class (c) **without saying so**. A procedure whose only input
  is what a record says cannot detect what a record does not say, so both
  candidate readings produce acquittal regardless of ground truth. Both controls
  resolve by reading one line (`EXP-ISADV-001`'s docstring declares (c);
  `EXP-WESOVOW-001`'s spec declares (a)) — they certify a reader, not an
  auditor. The already-closed lens added that the (c) screen is *already* a
  standing completion criterion (`GOAL-SSI-001/goal.yaml:36`) already executed
  per-task in committed review artifacts ("No uncharged oracle and no
  nonstandard graph access", "No uncharged oracles detected", and three more),
  and that the flagship live target answers itself: `RQ-JMV-001`'s committed
  `related_records` reads "EXP-ISADV-001 — planted-advice transfer across
  isogenous curves; **no advice here**".
- **Disposition: DROP as a standalone idea.** The two refuting lenses converge on
  a claim-level defect, and the deliverable already exists as a standing
  criterion. Salvage, at near-zero cost and without an identifier: fold the
  three-way (a)/(b)/(c) rubric text into the existing `GOAL-SSI-001` completion
  check so future reviews apply it uniformly, and record the one real caveat —
  `EXP-ISADV-001` has no `specification.yaml` and no ledger experiment record, so
  "read the target's own record" has no record to read for that target.

---

## 5. Refuted and failed — recurring failure modes

This is the section worth carrying into future authorship. Sixteen entries died:
seven refuted `PASS` entries and nine `FAIL`s. They did not die in sixteen
different ways. They died in eight, and every one of the eight also appears
*inside* the `REPAIRABLE` population, where it is survivable only because it sits
in the task card rather than in the claim. Ids in **bold** are `FAIL` or refuted;
ids in plain text exhibit the same mode at repairable severity.

### Mode 1 — The gate is an identity, a theorem, or a definition, so it cannot return another value
The single most common killer. A check whose outcome is forced by algebra tests
the implementation, not the claim.

- **`A3-1`** — `δ = B/N` with `B = N^{1/2}` gives `1/δ = N^{1/2}` by
  substitution; `S = G` gives `min(√N,1) = 1` by substitution. Both controls and
  the "sharp prediction stated in advance" are arithmetic identities.
- **`A1-11`** — "verify that the factor-base condition contributes zero equations
  of degree > 1" is true by the definition of Weil restriction once the unknowns
  are declared to live in `F_q`; the falsifier names an impossible event.
- **`A3-4`** — the committed detailed-balance residual is not a near-zero
  measurement but an exact integer identity: `cell(R)` is negation-invariant
  because `x(−R) = x(R)`, and the involution `r ↦ n−1−r` forces
  `cnt[c,c'] = cnt[c',c]` exactly (the per-row value is literally `0.0` in most
  of the 54 rows). Splitting on `sign(y)` removes that identity *by definition*,
  so both spectral predictions are consequences of the partition's definition and
  `F3` has no mechanism.
- **`A3-5`** — the evaluation to `G` is the coordinate *sum*, which is invariant
  under the `S_m` permutations and insensitive to which coordinate a translation
  hits, so `v(w) = ε + Σ aᵢsᵢ` and Corollary 1 reappears verbatim at two
  vertices: `S_nc(d) ⊆ S_comm(d)` is again algebraically guaranteed, and the
  "single violation" signal is unreachable. The entry's own kill-early concedes
  it. The object is also ill-posed: on *unordered* tuples the `S_m` action is
  trivial and per-coordinate translations are not well-defined maps.
- **`B1-6`** — "Kills it early: Nothing kills it" is the diagnosis, not a wording
  slip. A derivation with no pre-registered condition under which it returns a
  different answer is not a gate.
- **`C2-7`** — `delta_batched` equals `exponent(M) − 1`, i.e. it partitions the
  space of *multiplication routines*, not the space of candidate worlds:
  guaranteed `≥ 0.4` under schoolbook or Karatsuba, unreachable below `0.05`
  without an FFT-class kernel the entry neither requires nor budgets. The
  campaign's own committed numbers demonstrate it —
  `γ_A = 0.9328644281` (schoolbook) vs `γ_B = 0.8100336227` (Karatsuba) from
  implementations "sharing every line but `poly_mul`", a gap 2.5× the width of
  the entry's entire confirm band.
- **`B3-6`** — controls that resolve by reading a declaration (see §4).
- **`C2-1`** — the gate-placement variant: the gate sits at the one point where
  two candidate forms coincide (see §4).

Same mode, repairable severity: `A1-5` (Cayley–Bacharach dimension identity —
all three falsifiers are theorem-forbidden events), `A1-6` (the double count
`Σ(c_D(r)−1)⁺ = C(B+m−1,m) − |mD|` cannot fail), `C2-4`
(`|G/σ| = (|G|+#fix)/2` is a theorem, and `σ`-equivariance follows from
`Φ_ℓ ∈ Z[X,Y]`), `B3-3` (`d + (N−d) = N` as an "integer existence predicate"),
`C1-5` (the two anchors force `α = 3/2` uniquely, so the `α = 2` branch carrying
the whole OPEN outcome is not evaluable), `B2-3` (permuting *reasons* leaves a
verdict that is a conjunction over *statuses* identically unchanged).

### Mode 2 — Both candidate readings agree everywhere the grid is actually evaluated (the `48e258` pattern)
Distinct from Mode 1: the check *could* discriminate somewhere, but not where it
is run.

- **`A2-4`** — there is no trichotomy. Applying the single committed up-closure
  convention to `n1_ms.json` reproduces `46,694/8,761` exactly as the N1 **null**
  arm at seed 2; `46,709/8,746` is the SEM arm at seed 2 and `46,717/8,738` is
  the SEM arm at seed 2026 in the DREG lineage. Three objects, two arms, two
  seeds, all already attributed at source — so a 128-convention enumeration would
  fail to reproduce two of them for a reason that is not a defect, making the
  "named defect" branch a guaranteed false positive.
- **`B1-1`** — the entry correctly diagnoses that CDF-agreement with `ρ(u)` is not
  a discriminator, then relocates discrimination onto two statistics the null
  matches by construction. Null (i) draws integers uniformly from
  `[1,(p/2)^{1/3}]`, so its `λ₁` scale *is* `p^{1/3}` by definition — and
  `p^{1/3}` is a theorem for the real arm (Theorem 1.5, unconditional). The tail
  is likewise the content of Heuristic 1 itself. The surviving statistic is
  unreachable at the declared budget: at `10^4` samples the expected count of
  12589-smooth draws is `10^4/69232 = 0.144`, so observing zero (probability
  ~87%) is consistent with a correct instrument and a broken one alike.
- **`B1-12`** — both arms are random ideal walks from the same special extremal
  order, differing only in a walk length and norm profile the author picks. Run
  past mixing both are uniform up to conjugation and the test cannot reject at
  any sample size; run under-mixed it must reject. The outcome is a modelling
  choice, not a measurement.
- **`B2-5`** (also Mode 6) — the simulator's generative model *is* the hypothesis
  (i.i.d. uniform residues), so "measured mean deviates from H1's prediction"
  cannot fire except as sampling noise, and the same-mean null matches by
  construction.
- **`B3-6`** — the already-closed variant (see §4).

Same mode, repairable severity: `A2-9` (readings diverge only at `m ≥ 5`, which
the design declares out of reach), `A4-5` (the toy `k=12` control is evaluated in
the one regime where the readings are *inverted* — a correct MOV oracle is
declared void), `A4-6` (both live `ISO-COST` readings "win" at
`p = 2^20, L = 64`), `A4-11`, `B2-6`, `B2-9` (the `(2/(1−δ))^d` tree factor is
common to both accounts), `B2-10`, `B1-7` (the gate fires on a graph whose
diameter *is* its mixing time), `C1-4`, `C1-6`, `C2-10`.

### Mode 3 — The decision-relevant branch is unreachable at freeze (the `cc2b32` pattern)
`INDEX.md` §2 criterion 1 exists for this and it still recurs.

- **`A3-10`** — `F3` (supply `= o(B)`, the counting closure that is the whole
  point) is unreachable: a factor base of size `B` spans `Θ(B²)` chords by
  construction, and the committed Stevens–de Zeeuw form is `Θ(B^{4/3})` at
  `m = n = B`. No incidence bound `m^a n^b` with `a+b > 1` can ever return
  `o(B)`, so the outcome is fixed at `F2` before anything runs.
- **`A1-13`** — the headline claim is false under its own model: rho
  Pareto-dominates iff the IC time exponent is `≥ 1/2`, i.e. iff
  `d ≥ (m−3)/4` — precisely the complement of the committed
  "beats rho iff `d < (m−3)/4`". The entry's own falsifier fires by arithmetic
  before any table is built, and it is internally self-contradictory
  ("memory below `N^{1/(m+1)}`" one sentence after "memory is at least
  `B ≥ N^{1/(m+1)}`").
- **`A4-7`** — the only threshold to compare against (`PP-REC`) is untranscribed
  and unreachable, and the named fallback ("downgrade to measure `T_iso(S)`,
  which is a component of A4-6") dissolves the idea rather than rescuing it.
- **`B1-6`** — branch 1 is unreachable under the entry's own deliverable (iii):
  under either of `KN-TECH-057`'s `τ` conventions the VW interpolation lands
  *below* `p^{4/9}`, so the baseline never becomes `p^{4/9}` and the headline
  dichotomy is empty.

Same mode, repairable severity: `A1-4` (the headline forcing limb concedes in its
own Ceiling that the generic bound does not bind a non-generic algorithm),
`C2-8` (both negative branches dead on arrival — the buffer is `≥ 2^25.1` for
every `N/ℓ ≥ 1`, while the falsifier and the kill-early both require it below
`2^20`), `B1-3` (the advertised `2^{88}` upside requires `κ = 0`, contradicted by
the entry's own argument), `B1-11` and `A1-3` (both answer their own primary
question in the Mechanism paragraph), `A4-9` (the control's failure reason is
supplied in advance), `C1-12`.

### Mode 4 — A load-bearing premise taken at second hand (criterion 3)
Three distinguishable sub-modes, one of which is an artifact of *this worktree*
and must not be charged to the ideas.

**4a — The record exists, but not on the branch the screen ran on.** Four
screeners reported that a cited decision or correction record "does not exist
anywhere in this repository" (`A2-4`, `A2-5`, `A2-6`, `B2-1`). **That finding is
a branch-visibility artifact, and it is the most consequential correction in this
document.** Verified here: `DEC-20260805-cc2b32`, `DEC-20260805-0e1c91`,
`CORR-20260805-9d2e17` and `CORR-20260805-7f3a08` are all present on
`origin/claude/ssi-ecdlp-experiments-4cwbrq`, 11 commits ahead of its merge base
with the catalogue branch, and none is reachable from this worktree's `HEAD`.
The load-bearing figures are in them: `DEC-20260805-cc2b32` carries
"`h_6(12) = 7494` and `h_6(13) = 106743`, a 14.2× jump" verbatim, and
`DEC-20260805-0e1c91` carries revisit condition `R-B`. Consequences:
`A2-5`'s and `A2-6`'s c3 failures and `B2-1`'s primary c3 failure are **void as
stated** and must be re-screened against the sibling branch; `A2-4`'s `FAIL`
stands, because its primary ground (three distinct arm/seed objects, recomputed
from `n1_ms.json`) is independent of the missing citation. The same defect
touches the screen's own foundations: `INDEX.md` §2 cites
`DEC-20260805-0e1c91`, `CORR-20260805-9d2e17` and `DEC-20260805-cc2b32` — the
latter as the authority for criterion 1 — and none is readable from the branch
the catalogue was written on. **Procedural fix, straight from `CLAUDE.md`: fetch
`origin` and merge open research branches (or run `tools/sync_open_branches.py`)
*before* a premise-verification pass, and record the base commit checked.**

**4b — The cited record exists but does not contain the number.** `A4-4`
(`KN-LIT-742` states only `Õ(q)` for prime-order `E/F_{q^3}`; genus `g = 3` is
not in it, and its declared local PDF does not exist), `A4-6` (`p^{1/4}` does not
appear in `KN-LIT-317`), `A4-7`/`A4-11` (`PP-REC` untranscribed; `L_p(1/2)` not
in `KN-LIT-309`), **`B1-6`** (`paper_fulltext.md:23` states a complexity and two
problems and says nothing about output degree, so the "smooth composite degree"
conversion charge is scoped against a form the locator does not license),
**`B1-1`** (`paper_fulltext.md:196` is an *empty line*; the mixing bound is at
193 and governs a curve-side 2-isogeny walk, not the order-side walk the
mechanism applies it to), **`C2-7`** (the "48–59% of 21.233–25.223 bits" band
welds `S-B`'s lower endpoint to `S-A`'s upper endpoint — two scenarios with two
denominators reported as one band that exists in no committed scenario), `C1-8`
(the sampler premise is at `EV-PEC-857664:657`, not `EV-WESO-001`), `B3-3`
(the "known necessary condition `N > d`" is not in `KN-TECH-026`), `B3-5` and
`B3-7` (the matched `F_p` baseline is VW `p^{1/4}` conditional on mixing, not DG
`p^{1/3}` — a substitution that biases every verdict).

**4c — The corpus already answers, in the opposite direction.** `A3-11`
(`IDEA-20260727-004` already defines `G = C_sim/C_real`, already computes
`C_sim = Θ(B^m/m!)`, and already returns the four verdicts the entry proposes to
discover), **`A3-10`** (`KN-LIT-019`'s own relevance section already states the
direction the entry says the literature has never supplied), `A2-2`
(`EV-SIG-008` GATE 1 commits `n_vanish = 0` four words from the numbers the entry
quotes, pre-settling half its falsifier), `A3-2` (`EV-GGM-002` boundary item 5
records the endomorphism oracle as genuinely simulable, contradicting the
entry's prediction), **`B2-7`** (the screener read half of `implication_check`:
`source_literal_substitution_8L_into_equation_4_1: false` is immediately followed
by `conservative_fc0_cap` with `status:
verified_derivation_for_pinned_figure_1_row` and a four-step chain licensing
`D = 8L`, and `EQ_4_1_D_BOUND_DERIVATION`'s "nine lookups" × "`4D` T-gates"
already *is* Eq. (4.1)'s `36·L̃`), `B2-9` (`KN-LIT-4095` records GGAM/group-action
lower bounds, falsifying the "no committed query lower-bound source" premise).

### Mode 5 — The idea's own kill switch fires against committed state, in minutes
- **`A2-3`** — the stated falsifier is "`|V_i| = 24` for all `i` (mechanism
  void)". Measured directly from `n1_ms.json`: `|V_i| = 24` for eleven of twelve
  cubics and 23 for the twelfth; 210 of 276 pairs have `|V_i ∪ V_j| = 24`, not
  the `≤ 15` the design assumes. The system is not variable-local, there are no
  blocks, and the cost model collapses with it (`N(24,6) = 190,051` per pair, not
  `N(15,6) = 9,949`). The supporting argument is also a logic error: "105
  monomials of degree ≤3 require only about 9 variables" is a *lower* bound on
  variables needed, not evidence of locality.
- **`A4-7`** — its own kills-it-early says fold `T_iso(S)` into `A4-6`.
- `A1-3`, `B1-11` — same shape, repairable because the surviving scope is real.

**Authorship rule this yields: run the kill-early first, and against committed
artifacts, before writing the rest of the entry.** In every case above it costs
minutes and it is dispositive.

### Mode 6 — Arithmetic or structural error in the load-bearing derivation
- **`B2-5`** — `L1·L2/2^s` is the expected *length* of the single output phase
  vector, not an offspring count. The pinned source's committed derivation says
  so ("per_internal_node: one collimation"; "input and output phase-vector
  lengths bounded by `D`"), node growth is the separate `(2/(1−δ))^d` factor
  governed by the discard probability, and the convergence direction inverts:
  a "subcritical" length recursion means vectors die and the attempt restarts —
  unbounded retries, not finite total charge.
- **`A4-7`** — the stated law returns `Õ(1)` online time at `S = p^{1/4}`, which
  is impossible; the correct distinguished-point accounting on a class of size
  `M ≈ p^{1/2}` gives `Õ(p^{1/2}/S)`.
- **`A4-10`** — two of three lattice families (`L1`, `L2` are the lifts of
  `x(iP)`; `L3` the division-polynomial coefficients) contain no `Q` and so are
  functions of `(E,P,m)` alone. Sixteen of 24 cells are therefore
  guaranteed-null arms sharing one `3σ` falsifier — a false-positive generator.
  Independently, `λ₁ ≈ √(m/2πe)·p^{1/m}` is an `O(1)` constant at `m ∈ {32,64}`,
  so the real arm and the null are indistinguishable by construction.
- `C1-7` and its propagation — the claimed smooth fraction `≈2·10^{−4}` at
  `u ≈ 6` is ~10× too large (`ρ(6) = 1.96·10^{−5}`; committed
  `log2 P0 = −15.45`). This single number sizes `C1-7`'s power arithmetic and is
  inherited by `C1-4` and `C1-9`, where it silently converts "≈200 smooth
  events" into "≈22" and makes both designs unpowered.
- Sign and direction errors: `A3-3` (twist law `u` inverted, flipping every
  weight), `A3-9` (null control stated backwards — rank–nullity forces
  `D(A) > 0`, so a correct instrument is indicted), `A3-6` (`π(k) = k mod r` is
  not well defined on `Z/n` for `n` prime; `T3` mis-enumerates the `AGL(1,F_n)`
  subgroup lattice), `C1-1`/`C1-13` (`M ≥ X²` is backwards), `C1-3`/`C1-13`
  (the boundary optimum is at the *largest* admissible `T`, not the smallest),
  `C2-6` (`M = 2^93.28 ≠ p^{1/3} = 2^85.3`, so the asymptotic AT "tie" is
  concretely a 12-bit loss), `B1-8` (`p^{θ/γ}` is the *typical*, not the minimum,
  displacement), `B1-10` (`θ₂` and `θ₂′` used interchangeably in one formula).
- Symbol collisions: `C2-2` and `C2-11` both write `ρ(u)` where the committed
  model computes `ρ(w)` with `w = 3.49` against `u = 5.99`.

### Mode 7 — Every control is a null; no positive control that can fail, or it runs alongside rather than before
Criterion 4 is the second-most-common failure across the whole catalogue and the
easiest to repair, because it is almost always an *ordering* defect.

- **`A3-1`** — both controls are arithmetic identities (Mode 1 overlap).
- **`A4-10`** — the planted-HNP control with 8 leaked bits at `p ≈ 2^20`
  over-determines the system ~30×, so it is solved by size reduction alone and
  passes with a badly broken or precision-starved reduction. The declared risk
  ("LLL at dimension ≤ 64") is never exercised, so the control's negative branch
  is effectively unreachable and the `AGENTS.md` rule-5 routing it is praised for
  never gets used.
- **`B3-6`** — both controls resolve from a declaration (see §4).

Same mode at repairable severity, all fixable with one line in the task card
("run X first, abort if it does not fire"): `A1-9`, `A1-10`, `A1-12`, `A2-1`,
`A2-2`, `A2-7`, `A2-8`, `A2-9`, `A2-10`, `A4-1`, `A4-2`, `A4-8`, `B1-9`,
`B2-6`, `B3-2`, `B3-5`, `B3-7`, `C2-3`, `C2-5`.

### Mode 8 — Environment blocked with no fallback, or a claimed capability that does not exist here
`INDEX.md` §2 criterion 5 is stated and still violated, including by the
`INDEX` itself.

- **`A3-1`** — step (i) is declared *blocking*, `KN-LIT-7606`'s body is recorded
  unread ("the fetched PDF did not yield extractable text"), eprint is
  unreachable, and no fallback is named; `F1` and `F2` are undecidable.
- **`A3-10`** — "transcribe from source" with arXiv unreachable, no fallback, and
  no citation of the corpus entry that already carries the exponents.
- **`B1-12`** — no Round-3 SQIsign spec is obtainable and `KN-TECH-028` contains
  no keygen content, so the walk parameters that decide the whole test have no
  source; the honest fallback ("label every output as a statement about the
  declared model") voids the headline claim.
- Verified-by-execution environment errors elsewhere: SciPy **and** NumPy are
  both absent (`A2-1`, `A2-3`, `A2-6`, `A2-8` all re-cost); `sympy` is not
  installed and `requirements-agent.txt` does not list it (`B3-1`); `pdftotext`
  is absent and `pypdf`/`fitz`/`pdfminer` all fail to import, so **both** of
  `B2-2`'s named extraction routes are unavailable — and `INDEX.md` §3's
  top-ranked claim that the PDF is "fully extractable here (25 pages, 78,826
  chars, verified)" is **not reproducible** (a pure-Python zlib route does work
  and yields ~98.5k chars, but `B2-2` never names it); `A4-3`'s mandatory `N=p`
  band needs ~`4·10^6` pure-Python BSGS point counts against a stated
  `<2 CPU-hours`, and the Sage-free trace-1 curve construction it depends on is
  unnamed; `A3-4`'s "reproduce `EV-TRA-001` cell-for-cell" requires a CPython
  port of a Sage instrument (`sage_version 10.9` in the run manifest) that the
  entry never names, while its own slice-mate `A3-5` names the identical issue.

---

## 6. Repairable — 84 entries whose claim is sound and whose task card is not

These are the actionable population. None is recommended for minting *as
written*; each is recommended for repair, re-screening, and only then
reconsideration.

### 6.1 Priority tier — high decision value at zero or low cost (16)

Repair these first. Each is `value: high` with `cost: zero` or `cost: low` in the
slice screening, and each repair is a task-card edit rather than a redesign.

| id | repair |
|---|---|
| `A1-2` | Run the nearby-object control on the **algebraic** accounting with `D_trial = N^{o(1)}`, not on algebra-free MITM (which is genuinely worse than rho at every `n`, so the control false-alarms on a correct accounting); re-derive `d = 5/9` and `N^{0.7}` at one `B`. |
| `A1-12` | Compute the `F_{q^n}` subfield row first and abort the menu if it comes out inadmissible. |
| `A1-1` | Require `B^{m−1} ≫ N` in the grid (`B ≥ N^{1/(m−1)}`); restate the falsifier as a ratio against the matched-random-base control at identical `(B,m,N)`. |
| `A1-4` | Keep `c` symbolic; mark the multi-target baseline environment-blocked per `EV-IC-002` OBS-9; retitle the composed limb as the entry's own honest inversion. |
| `A3-6` | Replace the ill-defined control with the `r`-th power residue character `χ_r`; restate T3 up to conjugacy; demote T1 to a definitional remark. |
| `A4-1` | Run the bucketing audit against `EXP-IT-001`'s own edge generator and its root field; re-quote `special_families` from `H-IT-001.yaml:121`; order control (b) first. |
| `A4-3` | Name the Sage-free anomalous (trace-1) curve construction and re-cost, or shrink the `N=p` band and state the reduced power. |
| `B2-1` | Re-fetch `DEC-20260805-0e1c91` from the sibling branch (§5 Mode 4a) or drop the citation; rest on `goal.yaml` `next_action` + `EV-SSI-041`; run decoys as a separate pre-pass; relocate discrimination to the anchor-distinctness test. |
| `B2-2` | Name the pure-Python zlib extraction route (both named routes are unavailable here) and specify page-boundary recovery; drop the unreproducible 78,826-char figure. |
| `B2-8` | Fix the variable inside the `O` at source (`KN-OPEN-014` says `log p`, `KN-LIT-071` says `log N` — a `√2` in the sole deliverable); replace the `36 = 9×4` control with one that exercises the `(δ,d)` optimisation. |
| `B2-10` | Relabel arm (b) as instrument validation; run planted-shift recovery as a pre-flight; state that the exponent claim rests wholly on the symbolic arm (a); carry `KN-TECH-057`'s mixing condition. |
| `B3-5` | Substitute VW `p^{1/4}` (conditional on mixing) as the matched `F_p` baseline with DG `p^{1/3}` as the stated fallback; add F4 as a pre-run positive control. |
| `B3-7` | Correct the threshold to `δ < 1/2`; state thresholds per regime instead of `min()` across `F_p` and `F_{p²}`; move the `σ(d)` tracking check first; check `σ(d)` vs `ψ(d)`. |
| `C1-8` | Re-cite the sampler premise to `EV-PEC-857664:657`; pre-register the TV threshold and the induced-bias band numerically. |
| `C1-10` | Use `2.2309` for the NIST-I time row and `3.5133` for the others — a one-number fix to a gate a correct instrument currently fails. |
| `C1-13` | Prove closure (i) for the smooth-sum functional rather than for `X²`; replace (iii)'s derivative mechanism with the `P0 ≤ 1` saturation argument; fix the degenerate-`R` control. |

### 6.2 Remaining repairs, by slice

**A1** — `A1-3` scope the claim to single-target and deny positive readings in the
amortized setting · `A1-5` pre-register `r_free` *strictly below* the component
count and relabel the census an implementation check · `A1-6` demote the
double-count to a counter self-test, make the dichotomy the claim · `A1-7` drop
the "measured without naming" framing and the `2^{m−1}` transplant, keep the rank
limb · `A1-8` pre-register `R*·m/(B ln B)` with a tolerance band plus a
synthetic known-rank matrix, fix the rank `B−1` off-by-one · `A1-9` label both
external results as unverified recollections and gate the primary runs on the
planar control · `A1-10` run the planted-defect detection first, and the paper
argument before any compute.

**A2** — `A2-1` run the D5 control first, make matching-certificate verification
mandatory pre-report, re-cost on pure-Python greedy · `A2-2` restate as
duplicate-rows-only citing committed `n_vanish = 0`, lift the loader-validator in
as a pre-run gate · `A2-5` compute the freeze degree per rung and admit only
cells with D6 below freeze, cite `EV-DREG-008`'s committed zero deficit ·
`A2-6` re-derive `h_6(13)` from the Bardet series independently, declare the
support-size carry-over a named heuristic, re-cost · `A2-7` run the `f=0` and
permutation controls first, cite `EV-DREG-008` alongside `EV-SIG-008`, compute
the freeze degree at `nb = 16,17` · `A2-8` freeze a dynamic-range admission
condition or plant a cell with known separation, borrow `A2-9`'s control ·
`A2-9` make `g_true − g_random` at `m ∈ {3,4}` the primary gate and record the
`m`-trend as unadjudicable · `A2-10` promote control (ii) to primary, add a
planted known-`d_solve` pre-run gate · `A2-11` split off a separately budgeted
stage 0 ("does any nonzero prime-field D-deficit exist at reachable `m`?") and
fund nothing downstream until it fires · `A2-12` name the committed anchor per
arm or move the `w0` control to the prime-field arm.

**A3** — `A3-2` drop the endomorphism limb, pre-register `REV-20260727-002`'s
derivation as the expected value · `A3-3` fix the twist convention and re-derive
control (a) · `A3-7` name the `S₃` fixture file and line (the repo carries two
conflicting statements) · `A3-8` verify each cell's `B mod 3` at source and build
the base by orbit closure rather than rounding · `A3-9` invert null (b) to
"`D(A)` must equal `|A| − fiber count` exactly" and declare a fiber count
exceeding `|A|` · `A3-11` restate the premise against `IDEA-20260727-004`, scope
to the four new subjects, add one control whose column is not fixed by its
definition.

**A4** — `A4-2` quote and reconcile the committed `C_special_anomalous`, make the
dense-mark arm plus planted pullback a pre-run gate · `A4-4` restate as
`e(n,c) = c/n` with `c` pre-registered per corpus point from its own record ·
`A4-5` evaluate control (a) symbolically at BN254/BLS12-381 and use the toy
`k=12` curve only to check `ord_N(p)` · `A4-6` make path-finding cost its own
measured quantity over ≥6 primes with a pre-registered exponent band, and
transcribe `ISO-COST` from the locally held
`inputs/ECTD-TESKE-20260731/sources/galbraith-iso.pdf` · `A4-8` freeze the
field-op↔group-op charging convention before measuring and add a known-DL
pre-gate · `A4-9` swap the nearby object to Cheon's auxiliary-input algorithm,
which is generic and *does* beat `√N` — that control can fail · `A4-11` seed the
control set with contested predicates and pre-register their assignments.

**B1** — `B1-2` pre-register ≥5 primes spanning a decade of `log p` with a
declared exponent-resolution threshold, and drop the claim that covolume + AOV
force the stated profile (`INDEX` already rules it the loser of `B1-2 ∥ C1-3`) ·
`B1-3` delete the `2^{88}` target, make the `κ ≥ 1` closure primary, keep Ford's
density symbolic, fix the `p^{1/3−o(1)}` sign and the dropped `B^{1/2}` ·
`B1-4` pick one arm — structural argument (zero compute) or `(B,L)` optimisation
with a pre-declared threshold — and state the pure-Python Bach–Peralta recursion
or mark it blocked · `B1-5` make the O5 oracle-indexability audit the sole gate
and report the four-model ladder as arithmetic · `B1-7` plant a synthetic
gradient field with engineered long-range correlation and require greedy descent
to beat the random walk on it first · `B1-8` replace the candidate list with maps
that are not bounded perturbations of Frobenius, pre-register every `(γ,θ)` as
unknown, fix "minimum" → typical displacement · `B1-9` use "`j ∈ F_p`" as the
positive control and require recovery before scoring, and charge the
`α`-recovery and reconnection costs · `B1-10` obtain the `D`-exponent of the
`(d,d)`-isogeny count in `g=2` (asserted `D^4`, no source) — that, not the mass
constant, decides the exponent · `B1-11` delete the pre-answered row, scope to
the prescribed-kernel door, ship the reading list.

**B2** — `B2-3` permute obligation *statuses* not reasons (or drop control D) and
settle scope-vs-power failure by reading §1.1 first · `B2-4` pre-register the
candidate→F-family reduction criterion and add a known-admissible positive
control · `B2-6` relocate the gate to a `(d,δ)` region with `D` well below any
plausible cap, and sequence the VW null first · `B2-9` restate as a prefactor
comparison on a shared `(2/(1−δ))^d` factor and re-run the corpus search with
group-action-model terms.

**B3** — `B3-1` pre-register the secret space as the exponent vector/walk, adopt
`B3-8`'s R0/R6 pole test as a pre-run gate, demote the CSIDH rung to cited
algebra, fix the `sympy` attribution · `B3-2` exhibit a rung pair where inclusion
order and `r−m` order disagree and gate there, merge or re-derive C1/C2, correct
the `KN-LIT-3867` premise · `B3-3` replace the arithmetic identity with a
non-trivial diamond-degree condition or drop the predicate arm, source or derive
`N > d`, and state that identifiability — not Kani constructibility — is what is
measured · `B3-4` narrow to the `g=2` Kani kernel generators derivable here,
record the dim-4/8 arm as blocked, declare the `GOAL-SQISIGN-002` overlap ·
`B3-8` make the ladder's intended verdicts single-valued and pre-registered
independently of the screen's designer, score only rungs not derivable from the
screen's own definition, promote the observation-collision hunt to primary.

**C1** — `C1-1` restate the gain against `2^{92.5}` (L234) or `93.28`
(`RUN-WESOVOW-001`) and replace `M ≥ X²` with the two-lists-must-cover-`D`
argument · `C1-2` state `ℓ ≤ M^{1/4}` as a cap and show where it binds; use the
`3.5133`-bit band for non-NIST-I rows · `C1-3` state `κ` with its derivation and
replace the derivative closure with the saturation argument · `C1-4`
pre-register the minimum detectable `|log C|` from corrected event counts and
ship the Euler-product arm as a standalone zero-compute deliverable · `C1-5`
drop the `θ = 1/3` anchor (or localise the power law) so the `α = 2` branch is
evaluable, and replace the degenerate-`θ` gates · `C1-6` re-specify the
discriminator at bit scale rather than exponent scale · `C1-7` recompute `n`,
event counts, resolution and budget from `ρ(6) ≈ 2·10^{−5}` · `C1-9` recompute
the bin arithmetic from the corrected `P0`; either raise the sample ~10× (past
the batch budget) or restrict to one powered bin and drop the trend · `C1-11`
make the realisability/storage ceiling the primary gate · `C1-12` fold the L4
term into the kill-early and replace gate (4) with a quantity this machinery
emits.

**C2** — `C2-2` make the one-step-update admissibility argument primary and gate
the `Ω(d)` census on it; rename `u → w` · `C2-3` gate on the scaling null (the
`3/2` exponent in `N`), which needs no unreachable external constant · `C2-4`
reclassify as a zero-compute derivation plus a key-convention declaration, or
re-point the measurement at whether the canonicalising Frobenius costs more than
the 1.0 bit it saves · `C2-5` add a planted-claw fidelity check before the
filters are applied · `C2-6` state the DG baseline constant `k` as missing and
blocking, and lead with the concrete metric-indexed table rather than the
asymptotic tie · `C2-8` recompute the buffer under both schedules so the
flat-surface branch is reachable, and fix the `√w` factor of two · `C2-9` mark
the `Ω(N^{2/3})` query lower bound UNVERIFIED-RELAYED and scope it to the
black-box model · `C2-10` narrow the claim to the four statistics at the tested
scale and add a power calculation · `C2-11` correct `ρ(u) → ρ(w)` throughout ·
`C2-12` declare the predictor value→candidate-set map for every family member
and drop the constant-valued members.

---

## 7. What this screening does not do

- **It mints nothing.** No `IDEA-*`, `H-*`, `EXP-*`, `EV-*` or `DEC-*` identifier
  is created, reserved, or implied by this document. Section 3 is empty and that
  is its content.
- **It changes no status.** No hypothesis moves, no experiment is approved, no
  goal checkpoint is written. Only the Coordinator does those things, and this
  document is input to that decision, not a substitute for it.
- **It resolves no open problem.** `KN-OPEN-001`, `-002`, `-004`, `-005`, `-010`,
  `-011`, `-013`, `-014`, `-015`, `-018`, `-019`, `-020` and `-024` are exactly
  where they were.
- **It adjudicates no novelty, in either direction.** eprint and arXiv are
  unreachable from this environment. No entry is claimed novel and none is
  dismissed as known. Several entries rest on unverified recollections
  (`INDEX.md` §5) that still require primary-source transcription before use.
- **It advances no exponent, cost, or claim tier.** `sota_delta` remains 0 on
  every axis for every entry, `dominated_by` remains explicit, and Pollard rho at
  `c·√N` remains the ECDLP baseline. Nothing here claims to beat it.
- **A `PASS` — and a fortiori a "contested" — is a statement about an idea's
  FORM, not evidence that its claim is true.** It means: this entry has a
  reachable negative, its gate is evaluated where the readings disagree, its
  premises were re-read at source, it has a positive control that can fail and
  runs first, and it is honest about the environment. It does not mean the
  mathematics is right. Truth is decided by running the experiment and reviewing
  the evidence, not by passing a screen.
- **This screen has its own instrument-fidelity gap, stated in §2** — no
  calibration entry was passed through the three lenses to confirm they can
  return "not refuted" — and its own criterion-3 defect, stated in §5 Mode 4a:
  four "record does not exist" findings were artifacts of screening from a branch
  that had not merged `origin/claude/ssi-ecdlp-experiments-4cwbrq`. Both should be
  fixed before the next pass: fetch and merge open branches first, and calibrate
  the lenses on a known-good entry.
