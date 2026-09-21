# RT-PREFREEZE-EXP-SSIQ-58b642 — Pre-freeze Red Team review of the DRAFT contract EXP-SSIQ-58b642

**Goal:** `GOAL-SSIQ-001` · **Batch:** `BATCH-003` (new — this file creates its `reviews/` dir)
**Reviewed artifact:** `experiments/EXP-SSIQ-58b642/specification.yaml` (`status: draft`, `approved_by: null`, **NOT** frozen — read as a working-tree draft per GD-4's standing practice, which explicitly asks for this review BEFORE the file is committed as frozen. This is a deliberate, narrow exception to "review only a Coordinator-committed snapshot": the artifact under review IS the pre-freeze contract, and its entire purpose is to not yet be durable.)
**Also read:** `ledger/goals/GOAL-SSIQ-001/goal.yaml` (`exponent_budget.levers.L4`, `known_defects_of_this_record` GD-4/GD-5, `instrument_calibration`), `ledger/hypotheses/H-SSIQ-18dc91.yaml`, `coordination/goals/GOAL-SSIQ-001/batches/BATCH-002/reviews/RT-BATCH-002.md`, `ledger/evidence/EV-SSIQ-29fcbb.yaml`, `tools/validate_ledger.py` (`RUN_REQUIRED_TOP`, companion-artifact check), `templates/research-records.md`.
**Compute performed:** arithmetic only — OLS on hand-constructed synthetic series (shown in full, reproducible in a few lines), and integer arithmetic on stated bounds. No code was run, no dataset was fetched, no fit was recomputed on real data.

```yaml
inference:
  requested_policy: review-adversarial
  resolved_model_id: claude-sonnet-5
  resolved_model_provenance: self-reported by this Claude Code subagent session; not probe-verified (orchestration.adapter doctor --probe not run)
  model_verified: false
  fallback_used: true
  fallback_reason: >-
    Subagent frontmatter under this runtime cannot express a policy (CLAUDE.md,
    "Model policy note"); this session runs model: inherit. The xhigh
    reasoning-effort component of review-adversarial is neither settable nor
    verifiable from inside a subagent.
  independent_session: true
  independence_kind: session
  task_id_note: >-
    No TASK-YYYYMMDD-NNN identifier was supplied in this handoff. Not
    fabricated here; the Coordinator should assign one when this report is
    archived.
```

---

## 0. What this review is and is not

This is a pre-freeze check on a *contract*, not a post-hoc check on results — there are no results yet. The standard is the one GD-4 set: could this instrument, as specified, do the work the campaign is asking of it, or does it repeat the shape of "an obstruction/estimator that could not do the work asked of it, asserted without the cheap calculation that would have refuted it"? I tried to break points 1–3 with real numbers, not assertion, per the task's instruction, and found a genuine counterexample on point 1 and concrete, checkable contradictions on points 2, 3, and 7 (an item not on the original numbered list but squarely in scope: `required_artifacts` against the schema GD-5 was about).

**Bottom line up front:** the contract is well-constructed in several places that visibly learned from BATCH-002 (the sign/CI decision rule instead of a point target, the exhaustive-block instinct, the "unresolved by this test" discipline, the correctness oracle against WISDE, the tie between M-GAP and RT-BATCH-002's own required control #6). It is not ready to freeze. Seven findings below are BLOCKING, all with a concrete, bounded fix — none requires redesigning the experiment.

---

## 1. The cancellation claim (highest risk, and the contract said so itself)

### 1.1 The claim as written

`scale_relevance.justification`: "A shared instrument bias in gamma_greedy and gamma_random cancels in M-GAP to first order." No calculation is offered. This is exactly the shape of BATCH-002's O22 ("a pre-registered ±0.20 tolerance on an uncalibrated estimator") and RT-BATCH-001 §7's own confessed error ("`α = 3/2` versus `α = 2` is a large, easily separated difference... with no calculation behind the word 'easily'"). An assertion that a bias "should cancel" is not evidence that it does — that is the literal text of `docs/inventor-protocol.md` §3 and of `RT-BATCH-002` O22/O23.

### 1.2 A toy counterexample where it does NOT cancel

Model the mechanism named in the task: a **shared, additive, N-independent-in-form finite-size offset** applied to two power laws with **different true exponents**, fit by OLS on `ln(h)` vs `ln(N)` over the same finite window the contract will actually use (a few hundred to ~2000 vertices — see Finding 3 for why this window matters). This offset stands in for exactly the kind of thing named in the task prompt: a fixed local-minimum "floor" cost for greedy, or a fixed warm-up/mixing-time offset for the walk, or discreteness at small N.

True processes (illustrative, not fitted to anything): `h_random(N) = N^{1/2} + c`, `h_greedy(N) = N^{1/4} + c` — same additive constant `c`, same estimator, same window `N ∈ {50, 100, 500, 1000, 2000}`, both fit with the described OLS-on-logs.

| `c` | fitted `γ_random` (true 0.500) | fitted `γ_greedy` (true 0.250) | fitted M-GAP | true M-GAP | **M-GAP bias** |
|---|---|---|---|---|---|
| 5  | 0.3831 (Δ = −0.117) | 0.1139 (Δ = −0.136) | 0.2692 | 0.250 | **+0.0192** |
| 15 | 0.2675 (Δ = −0.233) | 0.0552 (Δ = −0.195) | 0.2123 | 0.250 | **−0.0377** |

(Both rows: OLS slope by hand, `cov(ln N, ln h)/var(ln N)` over the 5-point window; arithmetic reproducible in three lines.)

The **same** bias-generating mechanism, applied identically to both arms through the **same** estimator on the **same** graphs, produces an M-GAP error that is (a) non-zero, (b) **not the same magnitude** as either individual bias, and (c) **changes sign** as the offset-to-signal ratio changes across the window — from +8% of the true gap to −15% of it, using only two illustrative values of `c`. The reason is structural, not a property of this particular toy: an identical **linear-scale** shift does not translate into an identical **log-scale** (i.e., exponent) shift when the two curves have different exponents or coefficients, because the log transform is non-linear. Two processes whose exponents differ by hypothesis (that is the entire content of a DETECTED result) are, by that same hypothesis, at different points on that non-linear map, so "same bias source" does not imply "cancels in the difference" — it must be measured, not assumed.

This is close kin to the actual mechanism EV-SSIQ-29fcbb O-4/O-5 found (saturation inside a retained window plus finite-`T` discreteness), which is exactly why it is the right toy model here and not an arbitrary one.

### 1.3 What is missing from the contract, concretely

`goal.yaml.instrument_calibration.standing_practice_adopted` already states the fix in general terms: *"RUN THE FROZEN ESTIMATOR ON AN OBJECT WITH THE TARGET EXPONENT BEFORE FREEZING THE CONTRACT."* The draft contract's `controls` list (C-NULL-LABEL, C-CONNECTIVITY, C-DEGSEQ, C-SEED, C-REPRO) has **no entry that does this for M-GAP.** None of the five controls checks whether the M-GAMMA-GREEDY/M-GAMMA-RANDOM/M-GAP pipeline, run on a **synthetic pair of hitting-time processes with known, different exponents and a plausible shared finite-size bias**, recovers the true gap to within a declared tolerance, over the **same** N-window the real run will use.

### 1.4 BLOCKING — required fix

Add a pre-registered calibration control, e.g. **C-CAL-GAP**: before touching real graphs, run the exact M-GAP pipeline (same OLS estimator, same window shape, same N range as Finding 3's corrected bound) on at least two synthetic hitting-time pairs with known different exponents and a stated shared bias mechanism (constant offset; and, since greedy specifically risks *saturation* not just an offset — see Finding 2 — a saturating/capped variant too). Declare a tolerance for how close the recovered M-GAP must be to the true gap. If it is not close, either the estimator is fixed before real data is touched or the "cancels to first order" sentence is deleted and replaced with a measured correction/uncertainty band. This is the single most important fix in this review.

---

## 2. A second, independent failure mode for the SAME real-vs-null gap: local-minimum censoring

Not asked for by name in the task's point 1, but it attacks the identical headline quantity (M-GAP) by a different mechanism, so it belongs here rather than as an afterthought.

The mechanism (`H-SSIQ-18dc91.mechanism`) states greedy descent "halts at a local minimum" when no neighbour is strictly smaller, and the contract treats this as a **separate, exploratory** outcome (`M-LOCALMIN`), explicitly **not part of the confirmatory decision rule**. But `M-GAMMA-GREEDY` is defined as "fitted exponent `γ_greedy` in `median_hitting_time_greedy(N) ~ N^{γ_greedy}`" with **no stated handling for starts that never reach `δ_E = 1`.**

If the local-minimum-halt rate **grows with N** (plausible: a bigger graph offers more chances for a strictly-decreasing chain to run into a vertex with no smaller neighbour before reaching the target locus), then "median hitting time" computed **only over the starts that reach the target** is a median over a shrinking, N-correlated, non-random survivor set. A greedy arm's *apparent* speed-up over the random walk could then be entirely a **selection effect** — the survivors that happen to reach `δ_E = 1` quickly look fast, while the population that includes trapped starts would show something else entirely — with nothing to do with an actual `δ_E`-gradient. This is exactly the shape of finding that would make a DETECTED result an artifact rather than a signal, which is what this pre-freeze review exists to catch before, not after, the run.

**BLOCKING — required fix:** pre-register how non-reaching greedy starts are counted in `median_hitting_time_greedy(N)` — e.g., right-censor at a stated cap tied to graph diameter and report the censoring fraction as a function of N alongside M-GAP; or define `γ_greedy` only when the trapped-fraction is below a stated ceiling and report VOID above it. Whatever the choice, it must be fixed **before** data, not selected after seeing which choice produces a cleaner fit — and the censoring fraction vs. N must be one of the reported numbers, because a censoring fraction that **grows** with N next to a "detected" small `γ_greedy` is the artifact tell of `docs/inventor-protocol.md` §3 applied to this exact metric.

---

## 3. The prime-set selection rule: the stated bound is self-contradictory, and the arithmetic says why the correct bound is the one already used elsewhere in this document

### 3.1 The contradiction, stated exactly

`inputs.primes.selection_rule`: *"The 12 smallest primes p with `5000 <= p/12 <= 2000*12`."* `2000*12 = 24000`, so as literally written this requires graph size (`≈ p/12`) **between 5000 and 24000 vertices**. That directly contradicts, in the **same document**:

- `size_bound_note` two lines later: *"graphs up to ~2000 vertices"*;
- `H-SSIQ-18dc91.scope_ceiling.detail`: *"graph sizes up to ~2000 vertices"*;
- `goal.yaml.next_action` (the REC-3 instruction this contract implements): *"the exhaustive block (`<= 1833` vertices)"*.

The lower end of the stated bound (5000 vertices, i.e. `p ≳ 60000`) is already **3× past** the ~2000-vertex ceiling the rest of the document commits to. This is flagged by the contract itself as a placeholder (`size_bound_note`), which is why I do not treat it as a fabrication risk — but it must not survive freeze as written, because a placeholder inconsistency in a *frozen* contract is precisely GD-4/GD-5's shape (an unchecked assertion nobody ran the numbers on).

### 3.2 A second, independent contradiction the arithmetic surfaces

The upper end of the stated bound (24000 vertices, `p` up to `288000`) also **exceeds the WISDE dataset's own coverage**: `EV-SSIQ-29fcbb` O-1 records the released data spans `p ∈ [2, 265207]`. `265207/12 ≈ 22100` vertices — so even the *largest* prime WISDE covers sits below the placeholder's stated 24000-vertex ceiling, and any prime the placeholder's literal bound would admit above `p ≈ 265207` has **no WISDE record to cross-reference at all**, directly breaking `H-SSIQ-18dc91`'s own assumption 2 ("delta_E … cross-referenced against the WISDE released data … NEVER used to construct or bias an edge") and the contract's `delta_E_cross_reference` requirement, which has nothing to check against for such a prime.

### 3.3 What the correct bound is, with the arithmetic

Compute against the stated budget (`wall_clock_seconds_per_run: 7200`, `total_cpu_hours: 4` = 14400 CPU-s, `maximum_runs: 1`). Take a deliberately conservative per-vertex cost for pure-Python `F_{p^2}` cubic root-finding via `Φ_2(X, j)` — modular exponentiation `x^{p^2} mod f(x)` by repeated squaring needs on the order of `4·log2(p)` squarings of a low-degree polynomial mod the cubic, each a handful of `F_{p^2}` multiplications; at `p ≈ 22000` (`log2 p ≈ 15`) that is on the order of 60 squaring steps, each a few hundred Python-level bigint operations — call it 0.5–5 ms/vertex allowing generous Python overhead. At **≤ 2000 vertices × 12 primes = 24000 vertex root-finds**, total construction cost is on the order of **12–120 seconds** — comfortably inside the 7200 s wall clock even at the pessimistic end, and the hitting-time simulations (Section 5 below) are the more likely bottleneck, not construction. This is the arithmetic the placeholder needed and did not have: **the correct ceiling is the ~2000-vertex figure already used elsewhere in this document, not the 5000–24000 range in the selection rule**, and it is not merely "more realistic" but the *only* one consistent with (a) the rest of the same contract, (b) the goal's own REC-3 instruction, and (c) the WISDE coverage the correctness check depends on.

**BLOCKING — required fix:** replace the selection rule with something of the form "12 primes with `p ≤ 22000` (staying inside WISDE's *exhaustive* block — `RT-BATCH-002` O-28/control #4: never pool with the sieve-selected block above `p = 22000`), `p/12` spread across roughly a few hundred to ~1800 vertices (not clustered near the ceiling, so the power-law fit has an actual N-range to work with), balanced across `{1,5,7,11} mod 12`." Pin the exact 12 primes before freeze, as the contract already intends.

---

## 4. C-NULL-LABEL: correctly designed as a control, but its "should be indistinguishable" claim is asserted, not calculated — and the calculation matters here because of a fact specific to this object

### 4.1 What is right about it

Unlike BATCH-002's C-NULL (which used a *different lattice family* as the null object and thereby shared structural endpoints with the real object without anyone checking), C-NULL-LABEL shuffles `δ_E` **on the same graph**, preserving graph structure exactly and only breaking the label-adjacency correlation. This is a materially better-designed null than BATCH-002's — it is a real null object of the same shape, not a different family — and its `failure_consequence` (void the real-label metric if the shuffle also shows a gap) is the right response if it does fail.

### 4.2 What is not calculated: tie-breaking under a small, discrete label alphabet

`δ_E ≤ (p/2)^{1/3}` (Theorem 1.5 / the corrected L1 lattice bound). At `p = 22000`, `(p/2)^{1/3} = 11000^{1/3} ≈ 22.2`. So **`δ_E` takes roughly 22 distinct integer values** across a graph of up to **~1833 vertices** — an average multiplicity of **≈ 83 vertices per `δ_E` value** (unevenly distributed, weighted toward larger `δ_E`, per the counting-function shape `EV-SSIQ-29fcbb` already established). Each vertex has only **3 neighbours**. With that few possible values and that few neighbours, **exact ties among a vertex's 3 neighbours' `δ_E` values are the generic case for greedy descent's local comparison, not a corner case** — under the real labels (where nearby vertices may correlate in `δ_E` if the hypothesis is true, which only increases tie frequency locally) *and* under the shuffled labels (where the marginal distribution, and hence the tie rate, is preserved exactly by construction).

The mechanism section states ties are "broken by a fixed deterministic rule" and never names it. If that rule has **any** correlation with graph structure — e.g. "prefer the neighbour discovered earlier in the BFS," "prefer the lower internal vertex ID," or anything else derived from how the graph was built rather than from `δ_E` content alone — then greedy descent's trajectory under **both** the real and the shuffled labels is doing substantial work through the tie-break rule rather than through `δ_E`. In the worst case this could produce a spurious gap that C-NULL-LABEL is well-positioned to *catch* (its failure_consequence already voids the metric if the shuffle shows a gap too) — but it could just as easily produce a spurious gap **correlated in the same direction in both arms**, in which case the control's stated expectation ("statistically indistinguishable... because greedy on an uncorrelated label is just another random walk") is simply wrong for a structural reason nobody calculated, and the control would silently PASS while the real-label result is still contaminated by the same structural artifact.

This is the same category of error as BATCH-002's O22/O23: an uncalculated "should be indistinguishable" is not evidence that it is.

**BLOCKING — required fix:** (a) name the exact tie-break rule in the contract now, and argue or verify explicitly that it is independent of BFS discovery order, vertex numbering, and any other construction-derived structure — e.g. break ties via a fresh RNG draw keyed only by a hash of the tied vertices' own labels/adjacency content, never by discovery order; (b) report the **tie frequency** (fraction of greedy steps landing on an exact tie among the 3 neighbours) as a diagnostic alongside M-GAP, both under real and shuffled labels, so a reviewer can see how much of the trajectory the tie-break rule — rather than any `δ_E` gradient — actually determined.

---

## 5. Degenerate vertices (j = 0, j = 1728): flagged as risky, not resolved, and the prime-balance requirement *guarantees* the hardest case is tested

The contract's own `degenerate_j_handling` text says to "handle exactly per the standard convention" without stating what that convention is, and flags the risk correctly: getting it wrong "silently biases the degree sequence at exactly the two most structurally important vertices."

I can state the *shape* of the correct convention with reasonable confidence — the standard treatment in the Pizer-graph literature is to build the modular-polynomial graph as a **multigraph**, where a **root multiplicity of `Φ_2(X, j)` at a vertex is an edge multiplicity**, not something to be deduplicated to distinct neighbours; this is what keeps the graph `(l+1)`-regular (here 3-regular) even at vertices with automorphism groups larger than `{±1}`, where a single geometric neighbour can be reached by more than one degree-2 isogeny up to automorphism. But I cannot state the **exact** multiplicity pattern at `j = 0` and `j = 1728` for `Φ_2` specifically, nor its dependence on `p mod 12`, without risking exactly the kind of unverified-citation error `AGENTS.md` rule 9 and `docs/claims-and-verification.md` forbid. **This needs primary-source or literature verification before freeze**, not a red-team guess. Name the sources to check: Sutherland, *"Isogeny volcanoes,"* ANTS X (2012), §2 (modular-polynomial graph construction and degenerate-vertex conventions); Pizer's original construction papers on supersingular Ramanujan graphs; or a modern survey such as Costello's *"Supersingular Isogeny Graphs in Cryptography."*

This matters more here than in a generic instance because the contract's own `selection_rule` requires the 12 primes to be **balanced across all four residues `{1, 5, 7, 11} mod 12`** — and `p ≡ 11 mod 12` (`≡ 3 mod 4` and `≡ 2 mod 3`) is exactly the case where **both** `j = 0` and `j = 1728` are simultaneously supersingular with enlarged automorphism groups. The balance requirement does not merely risk this case, it **forces** it into the pre-registered prime set, at exactly the point where a silent multiplicity bug is most likely and where the aggregate `C-CONNECTIVITY` vertex-count check is weakest (a compensating pair of local errors — one vertex over-counted, one under-counted — can still match the total count and pass).

**BLOCKING — required fix:** pin the exact convention from a verified primary or secondary source before freeze, state the exact expected degree/multiplicity at `j = 0` and `j = 1728` for each of the four `p mod 12` residue classes numerically (not "the standard convention"), and make `M-DEGSEQ`'s "expected shape" check that exact numeric pattern rather than a generic 3-regularity statement.

---

## 6. `required_artifacts` vs. the actual run-manifest schema: this is GD-5's shape again, reached by a different route

`tools/validate_ledger.py` (`RUN_REQUIRED_TOP`, lines 155–156 and 382–395) checks two distinct things: (a) `manifest.yaml`'s **body** contains the keys `id, experiment_id, status, code, environment, inputs, timing, result`, with `code.commit` and `code.command` as sub-keys of the `code` **dict entry**; and (b) the run **directory** contains five literal **companion files**: `command.txt`, `environment.json`, `stdout.log`, `stderr.log`, `raw-result.json`.

The draft's `required_artifacts` lists `runs/RUN-SSIQ-58b642-a/code.txt` and `runs/RUN-SSIQ-58b642-a/inputs.json` — **neither of which the validator checks for** — and **omits `command.txt`**, which the validator explicitly does check for and which is the actual file the GD-5 repair (`manifest_v2.yaml` + `command.txt`) added. I confirmed this against the real repaired precedent: `experiments/EXP-SSIQ-4de240/runs/RUN-SSIQ-4de240-a/` contains `command.txt` on disk and contains **no** `code.txt` anywhere.

The `required_artifacts_note` states: *"THIS LIST NAMES THE RUN-MANIFEST SCHEMA KEYS EXPLICITLY (code.txt, inputs.json, environment.json, stdout.log, stderr.log)"* — this conflates the manifest **body key names** (`code`, `inputs`, `environment`) with the validator's separate **companion-filename** check, and mechanically appended `.txt`/`.json` to the key names rather than reading the validator's actual per-file list. `environment.json` happens to be correct in both readings, which likely masked the other two being wrong. This is the exact GD-5 shape (a required-artifacts list that does not match the schema it claims to match), produced this time by an attempt to *fix* GD-5 that generalized the wrong lesson from it.

**BLOCKING — required fix:** replace `code.txt` with `command.txt` in `required_artifacts`; drop or relabel `inputs.json` as a genuinely optional supplementary artifact (it is not required by the validator, though it is not harmful to keep); and add an explicit line stating that `manifest.yaml`'s **body** must independently satisfy `RUN_REQUIRED_TOP` with `code.commit`/`code.command` populated — as a distinct obligation from the five companion filenames, not implied by them.

---

## 7. Decision-rule wording: mostly good, one real gap found on the exact question this review was asked to check

The contract's `decision_rule_frozen_before_data` is careful and explicit: branch 2 says NO-detection "must say 'unresolved by this test', never 'refuted'," and `success_criterion` correctly treats a clean NOT-DETECTED-AT-THIS-SCALE outcome as a fully successful run. This is a genuine, visible improvement over BATCH-002 and I record it as attacked-and-held: I looked for the asymmetry BATCH-002 needed after the fact and mostly did not find it here.

I did find one place it slips. `falsification_criterion` reads: *"H-SSIQ-18dc91 is **falsified** at the tested scale if M-GAP's CI includes or is below 0..."* — "falsified" is functionally a synonym of the "refuted" the contract elsewhere goes out of its way to forbid. A checkpoint author citing `falsification_criterion` verbatim could correctly say "H-SSIQ-18dc91 was falsified," which a downstream reader can easily conflate with "L4's obstruction is refuted" or "no `δ_E`-gradient exists" — precisely the misreading `decision_rule_frozen_before_data` branch 2 and `H-SSIQ-18dc91.scope_ceiling` ("no result transfers to cryptographic scale") were written to prevent. This is a real instance of the wording gap this review was asked to check for (point 6 of the task), not a hypothetical one.

**BLOCKING — required fix (one line):** reword `falsification_criterion` to match branch 2's own discipline, e.g.: *"H-SSIQ-18dc91's toy-scale prediction is NOT SUPPORTED AT THIS SCALE if M-GAP's CI includes or is below 0 with C-NULL-LABEL and C-CONNECTIVITY passing on ≥ 4 primes; record as 'unresolved by this test,' never as 'falsified' or 'refuted,' consistent with `decision_rule_frozen_before_data` and `scope_ceiling`."*

---

## 8. Feasibility (task point 5): not infeasible, contingent on Finding 3's fix, with two remaining advisory gaps

Once the vertex-count ceiling is corrected to ~2000 (Finding 3), the construction-time arithmetic in §3.3 above (≈12–120 s for 24000 vertex root-finds, even pessimistically) suggests the stated budget (7200 s wall clock, 4 CPU-hours) is **adequate, not overreaching**, for graph construction specifically. The more uncertain cost centre is the hitting-time simulation itself. Using the null's own predicted exponent (`γ_random ≈ 1/2`, i.e. mean hitting time to a density-`p^{-1/2}` target in an expander scales like `p^{1/2}`), a rough trial-count estimate (starts × seeds × label-regimes × methods × primes, each trial costing `O(N^{1/2})` cheap adjacency-list steps) also lands comfortably inside budget — so I do **not** find outright infeasibility here, in contrast to what a literal reading of the placeholder bound in Finding 3 would have implied.

Two gaps remain, ADVISORY (not blocking, because a competent Executor can plausibly infer a reasonable protocol, but they should be pinned before the run rather than left implicit):

- **A1.** The relationship between `wall_clock_seconds_per_run: 7200` and `total_cpu_hours: 4` (=14400 CPU-s) is not explained — is the CPU-hour figure inclusive of ~2× parallelism, or a separate looser accounting? State which.
- **A2.** The exact population the "median hitting time" is a median *over* is not stated (plausibly: one trial per starting vertex, all N vertices, replicated at the three declared seeds per `C-SEED` — a reasonable reconstruction, but state it explicitly, and note it interacts directly with Finding 2's censoring question).

Also ADVISORY: add a small pre-run correctness gate for the from-scratch `F_{p^2}` cubic root-finder beyond the post-hoc aggregate `C-CONNECTIVITY` vertex-count check — e.g. verify the full **edge list** (not just the vertex count) for one small pre-registered prime against an independent computation, since a compensating pair of local errors can pass an aggregate count check while still corrupting the adjacency the entire experiment depends on.

---

## 9. Attacked and held

- The sign/CI decision rule replacing a numeric point-prediction target — genuinely the right response to BATCH-002's O22, and I could not find a way it repeats that specific defect.
- The correctness oracle against WISDE released `δ_E` (assumption 2 / `C-CONNECTIVITY`) — a real, checkable invalidation trigger, not an assertion.
- `objective_boundary` and `asymptotic_claim: null` — correctly scoped; a DETECTED result is explicitly barred from being read as a complexity claim.
- The stopping rule's 900 s smallest-prime check and the ≥4-primes-or-INCONCLUSIVE fallback — a real, mechanical guard against silent scope-shrinking.
- `required_artifacts_note`'s stated *intent* (name the schema explicitly, per GD-5) — the intent is right; the execution has the specific defect in Finding 6.

---

## 10. Verdict

**FREEZE-WITH-FIXES.**

None of the seven BLOCKING findings requires redesigning the experiment: the object (build the graph directly, measure greedy-vs-random hitting-time exponents, sign-test the difference) is sound and is the correct direct test of L4 per RT-BATCH-002 REC-3. Every fix below is a bounded amendment to the same contract.

**Required before freeze, in order of importance:**

1. **Add a pre-registered calibration control (C-CAL-GAP)** that runs the exact M-GAP pipeline on synthetic hitting-time pairs of known, different exponents with a stated shared finite-size bias mechanism, over the corrected N-window, and declares a recovery tolerance — replacing the uncalculated "cancels to first order" sentence. (§1)
2. **Specify how non-reaching greedy starts are counted** in `median_hitting_time_greedy(N)`, and report the trapped-fraction vs. N as a diagnostic beside M-GAP. (§2)
3. **Fix the prime-selection size bound** to match the ~2000-vertex ceiling already used elsewhere in the document (`p ≤ 22000`, inside WISDE's exhaustive block), spread across the range rather than clustered near the top. (§3)
4. **Name the tie-break rule explicitly**, verify it is independent of graph-construction order, and report tie frequency alongside M-GAP. (§4)
5. **Pin the exact degenerate-vertex (j=0, j=1728) convention from a cited, verified source**, numerically, per `p mod 12` class — required because the prime-balance rule guarantees the hardest case (`p ≡ 11 mod 12`) is tested. (§5)
6. **Fix `required_artifacts`**: `code.txt` → `command.txt`; state that `manifest.yaml`'s body must independently satisfy `RUN_REQUIRED_TOP`. (§6)
7. **Reword `falsification_criterion`** to match the "unresolved by this test, never refuted" discipline already used elsewhere in the same contract. (§7)

Advisory, travel with the frozen contract as documented limitations if not resolved: A1 (CPU-hour/wall-clock relationship), A2 (median-population protocol), and the pre-run edge-list correctness gate (§8).

---

## 11. Required output block

```yaml
red_team_report:
  id: RT-PREFREEZE-EXP-SSIQ-58b642
  task_id: null
  task_id_note: >-
    No TASK-YYYYMMDD-NNN identifier was supplied in this handoff; not
    fabricated. The Coordinator should assign one at archive time.
  claim_under_review: >-
    The DRAFT contract experiments/EXP-SSIQ-58b642/specification.yaml
    (status: draft, not frozen), a pre-freeze review per GD-4 standing
    practice: whether it repeats the shape of GD-4/GD-5 (an instrument or
    claim that cannot do the work asked of it), before status moves to
    approved.
  objections:
    - "PF-1: scale_relevance's 'shared bias cancels in M-GAP to first order' is asserted, not calibrated; a hand-constructed toy counterexample (shared additive finite-size offset on two power laws of different true exponent, same OLS estimator, same window) shows M-GAP bias of +0.0192 to -0.0377 against a true gap of 0.25 -- non-zero, sign-changing, and not equal to either individual bias."
    - "PF-2: M-GAMMA-GREEDY's 'median hitting time' has no stated handling for greedy starts that halt at a local minimum before reaching delta_E=1; if the halt rate grows with N, the reported gamma_greedy is computed over a shrinking, N-correlated survivor set, which can manufacture a spurious gap independent of any real delta_E gradient."
    - "PF-3: the prime selection_rule's literal bound (5000 <= p/12 <= 24000) contradicts the ~2000-vertex ceiling used elsewhere in the SAME document and the goal's inherited <=1833-vertex bound, and its upper end (p up to 288000) exceeds WISDE's own covered range (p <= 265207 per EV-SSIQ-29fcbb O-1), breaking the delta_E cross-reference correctness check for any prime near that end."
    - "PF-4: the greedy descent tie-break rule is never named. delta_E takes ~22 distinct integer values (Theorem 1.5 bound at p=22000) across graphs of up to ~1833 vertices with degree 3, so exact ties among a vertex's 3 neighbours are the generic case, not a corner case, for both the real-label and C-NULL-LABEL shuffled arms; an unnamed, possibly structure-correlated tie-break rule could drive the measured gap in either arm."
    - "PF-5: degenerate-vertex (j=0, j=1728) handling is flagged as risky by the contract itself and left as 'the standard convention' with no citation; the pre-registered prime-balance requirement across {1,5,7,11} mod 12 GUARANTEES p = 11 mod 12 is tested, which is exactly where both j=0 and j=1728 are simultaneously supersingular with enlarged automorphism groups, and where a compensating local multiplicity error is least likely to be caught by the aggregate C-CONNECTIVITY vertex-count check."
    - "PF-6: required_artifacts lists code.txt and inputs.json, neither checked by tools/validate_ledger.py's companion-artifact loop, and omits command.txt, which IS checked and which is the actual file the GD-5 repair added (confirmed against experiments/EXP-SSIQ-4de240/runs/RUN-SSIQ-4de240-a/ on disk). required_artifacts_note's claim that the list names the schema explicitly is false in exactly the way that produced GD-5, reached this time by conflating manifest-body key names with companion filenames."
    - "PF-7: falsification_criterion uses 'falsified at the tested scale,' in tension with decision_rule_frozen_before_data branch 2's explicit 'must say unresolved by this test, never refuted' -- a checkpoint reader citing falsification_criterion verbatim could misreport a NOT-DETECTED outcome as L4 being refuted or delta_E having no gradient."
  required_controls:
    - "C-CAL-GAP: run the exact M-GAP estimator pipeline on >=2 synthetic hitting-time pairs of known different exponents with a stated shared finite-size bias mechanism (constant offset AND a saturating/capped variant, given PF-2), over the corrected N-window, with a pre-declared recovery tolerance -- BEFORE real graphs are built."
    - "Pre-registered, explicit handling of non-reaching greedy starts in median_hitting_time_greedy(N) (censoring rule or validity ceiling), with trapped-fraction vs. N reported alongside M-GAP."
    - "Tie-frequency diagnostic: fraction of greedy steps landing on an exact delta_E tie among the 3 neighbours, reported for both real and shuffled labels alongside M-GAP."
    - "Numeric, per-(p mod 12 class) expected degree/multiplicity at j=0 and j=1728, cited from a verified primary or secondary source, checked by M-DEGSEQ exactly rather than against 'the standard convention.'"
    - "A pre-run edge-list correctness gate for at least one small pre-registered prime, independent of the aggregate C-CONNECTIVITY vertex-count check."
  counterexample_or_mutation: >-
    Toy hitting-time pair with a shared additive finite-size offset c on two
    power laws of different true exponent (h_random = sqrt(N) + c, h_greedy =
    N^0.25 + c), OLS-fit in log-log space over N in {50,100,500,1000,2000}
    (the contract's own working range). At c=5: fitted gamma_random=0.3831
    (true 0.5), fitted gamma_greedy=0.1139 (true 0.25), fitted M-GAP=0.2692
    vs true 0.25 (bias +0.0192). At c=15: fitted gamma_random=0.2675,
    fitted gamma_greedy=0.0552, fitted M-GAP=0.2123 vs true 0.25 (bias
    -0.0377). Same bias source, same estimator, same graphs -- M-GAP bias is
    non-zero, unequal to either individual exponent's bias, and changes sign
    across the two cases. This directly falsifies the unqualified
    "cancels to first order" claim as a general property of the design; it
    may still hold approximately for the ACTUAL bias mechanism this
    experiment will encounter, but that must be measured (C-CAL-GAP), not
    assumed.
  baseline_comparison: >-
    Not applicable in the algorithm-comparison sense -- this experiment
    claims no algorithm and asymptotic_claim is correctly null. The relevant
    baseline for THIS review is the campaign's own prior instrument
    (EXP-SSIQ-4de240's counting-function fit, EV-SSIQ-29fcbb), whose failure
    mode (an uncalibrated estimator applied to a shared-endpoint null with an
    unchecked 'should cancel'/'should be indistinguishable' assumption) this
    draft's PF-1 and PF-4 findings show has not yet been fully avoided, only
    partially avoided (the sign/CI decision rule and the same-graph null
    object are real improvements; the missing calibration control and the
    unnamed tie-break rule are not).
  heuristic_challenges:
    - "The mechanism section's implicit heuristic -- 'if delta_E behaves as a graph distance to the F_p locus plus bounded noise, greedy descent reaches it in O(diam) steps with a smaller exponent' -- is not numbered and carries no stated random-model justification; this is consistent with the hypothesis's own heuristic_assumptions_note (none numbered, by design, since this is a gradient-existence screen, not a proof-oriented claim per proof_search_map's not_applicable_reason), so I do not treat the absence as a defect on its own -- but the ABSENCE of a numbered heuristic makes the missing calibration control (PF-1) more load-bearing, not less, since there is no other place a systematic bias would be caught."
  cost_model_challenges:
    - "Construction-cost arithmetic (Section 3.3, Section 8): at the corrected ~2000-vertex ceiling, ~24000 total vertex root-finds cost on the order of 12-120s even at a pessimistic 0.5-5ms/vertex pure-Python estimate, well inside the 7200s wall-clock cap -- feasibility is NOT the binding objection once PF-3 is fixed, contrary to what a literal reading of the placeholder bound would suggest."
    - "The relationship between wall_clock_seconds_per_run (7200) and total_cpu_hours (4 = 14400 CPU-s) is unexplained (A1, advisory) -- state whether the CPU-hour figure implies parallelism."
    - "No stated sub-budget split between graph construction and hitting-time measurement, and no stated trial-count/sampling protocol for 'median hitting time' (A2, advisory) -- a reasonable reconstruction exists (one trial per starting vertex, replicated at 3 declared seeds) but is not stated."
  reduction_and_scope_challenges:
    - "H-SSIQ-18dc91.asymptotic_claim is correctly null and objective_boundary correctly bars reading a DETECTED result as a complexity claim -- checked and held."
    - "No scheme name from the source's affected-vs-safe lists appears anywhere in this contract; no scope widening found."
  proof_architecture_challenges:
    - "proof_search_map's not_applicable_reason (this is a gradient-existence screen, not a proof-oriented proposal) is correctly reasoned and I did not find a place where section 8's audits would silently have caught something this reasoning misses -- attacked and held."
    - "Method-ceiling framing is present at the goal level (L4's own obstruction is a hitting-time bound for a density-p^{-1/2} set in an expander) and is correctly NOT claimed as tested by this experiment (H-SSIQ-18dc91 explicitly: 'a gradient existing is necessary but nowhere near sufficient for a p^{1/4}-time descent') -- held."
  narrowest_supported_statement: >-
    Scoped to experiments/EXP-SSIQ-58b642/specification.yaml as read at
    review time (draft, unfrozen): the contract's core design -- build
    2-isogeny graphs independently via Phi_2 root-finding, measure greedy
    vs. random-walk hitting-time exponents on the same graphs, sign/CI-test
    the difference -- is a sound, direct test of lever L4 and correctly
    avoids BATCH-002's point-prediction failure mode. It is not yet freezable:
    seven concrete, bounded defects (PF-1 through PF-7) would, if frozen as
    written, either produce an uncalibrated headline number (PF-1, PF-2,
    PF-4), test the wrong prime range or break its own correctness check
    (PF-3), leave a flagged risk unresolved at exactly the point the prime
    set is forced to test it (PF-5), fail the run-manifest schema check GD-5
    was created to prevent (PF-6), or invite a downstream misreading of a
    null result as a refutation (PF-7). None requires redesigning the
    experiment.
  next_concrete_action: >-
    Coordinator revises experiments/EXP-SSIQ-58b642/specification.yaml per
    the seven required fixes in Section 10 above, in the order listed
    (C-CAL-GAP first), and returns the revised draft for a second, shorter
    pre-freeze pass focused only on verifying the seven fixes before setting
    status: approved / frozen_at. Do not skip straight to execution on the
    theory that the fixes are minor -- PF-1 and PF-4 both change what the
    headline M-GAP number means.
  artifact_paths:
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-003/reviews/RT-PREFREEZE-EXP-SSIQ-58b642.md
  files_written_outside_scope: []
  raw_artifacts_modified: 0
  ledger_touched: false
  record_statuses_changed: 0
  compute_performed: "arithmetic only (hand OLS on synthetic series; integer arithmetic on stated bounds); no code run, no data fetched"
  commits_made: 0
  commit_note: >-
    No commit made. Per AGENTS.md "Durable research commits," the
    Coordinator's ledger/snapshot archive task commits this report; it is
    not durable until that archive exists. Per write_scope, this task did
    not modify experiments/EXP-SSIQ-58b642/specification.yaml or any ledger
    record.
  verdict: FREEZE-WITH-FIXES
```
