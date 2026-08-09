# Evidence review, part 2 — the five slices that failed

**What this is.** `REVIEW-UNADDRESSED-20260807.md` §6 recorded that five of ten survey
slices had failed on a session usage limit and named what they left unexamined. This
document completes them. Together the two documents are one review.

**Slices completed here:** `never-launched`, `closed-and-paused`, `methodology`,
`literature-debt`, `cross-cutting`. Five readers opened **365 records** between them and
returned 30 gaps; consolidation verified, deduped against all 459 existing proposals, and
returned **21 clusters** and 4 drops.

**Deliverables.** 21 new `IDEA-20260809-*` records in `ledger/proposals/`, one per cluster.

**Authority.** Nothing here changes a hypothesis status, approves an experiment, adopts a
convention, suspends a rule, or transitions a goal. Several findings *are* Coordinator
actions and are reported, not taken (AGENTS.md rule 1). The branch adds files only.

**Base.** `HEAD == origin/main` at review time. Part 1's work was merged to `main`; this
branch was restarted from it, as the merged-PR rule requires.

---

## 1. Corrections to findings this session reported earlier

Four deterministic findings were reported to the user before the slices returned. **Two
were wrong and one was a rediscovery.** They are corrected here rather than quietly
dropped, because the errors are instructive about solo pattern-matching over a corpus
this size.

### 1.1 The calibration sample — WRONG, by a factor of about 20

**Reported:** 343 proposals carry a numeric `honest_prior_of_survival` and 153 have both a
numeric prior and a downstream hypothesis, so `KN-OPEN-875d43`'s retrospective is
answerable today on committed data.

**Actual (cluster PRCAL, re-measured):** of the 343, **only 7 are a bare number**; 341 of
343 strings are distinct prose scoped to a narrow sub-claim (*"0.97 that (A) is correct as
stated, since it is five lines of…"*). A prior on "the theorem is two lines and correct" is
not a prior on survival under parameter change. Further, only **12 of 271 hypotheses have
reached a resolved status** (203 sit at `proposed` or `analyzed`), and only 40 carry a
source-proposal back-link. **The usable (prior, outcome) sample is at most 7, not 153.**

My error had two parts: I matched `0\.\d+` anywhere in the string, which counts prose
priors about sub-claims; and I treated "referenced by a hypothesis" as "has an outcome",
when three quarters of hypotheses have no outcome yet. The binding constraint is the
**hypothesis-resolution rate**, which is itself a measurable property of this program worth
stating — and is now `IDEA-20260809-81f74b`.

### 1.2 The claim-tier ceiling — a REDISCOVERY, and the existing record is stronger

**Reported:** `TIER_ORDER.get()` returns `None` outside `{toy, medium, crypto}` and the
check is guarded on `is not None`, so unrecognised tiers skip the ceiling silently.

That is true, and `IDEA-20260805-de2945` with `H-FIND-52472d` already claims it — **and
names a second cause I missed**: every one of 60 cited manifests records parameters at
`run.parameters` while `tier_of_run()` reads `(run.inputs or {}).get('parameters')`, so
`tier_of_run` returns `None` and the ceiling is skipped for a second, independent reason
(corpus split: 103 manifests top-level-only, 1317 inputs-only, 0 both). Its deliverable is
a derived tier-certificate register that reconstructs the ceiling without editing immutable
records.

The gap was therefore **dropped, not filed**. What survives is the part `de2945` does not
cover — the decision layer performs no tier check at all — folded into `IDEA-20260809-253a58`
alongside two further defects in the same validator path.

### 1.3 The exponent count — off by one, and incomplete

**Reported:** zero of 459 proposals claim an exponent improvement.

**Actual (cluster SELFM):** **exactly one** does — `IDEA-20260805-bd8339`, which states
*"This IS an exponent statement, not a cofactor statement, and it is the exponent the
proposal exists to move."* My classifier read its `target_complexity` text as a disclaimer.
SELFM also found what I did not: 214 proposals contain an explicit self-declaration of
non-compliance, and `DEC-20260730-014` issued a corrective `next_action` on 2026-07-30
(*"Prefer exponent-targeting ideation"*) after which, in the 417 proposals added on or
after 2026-07-31, **not one ECDLP-lane record targets an exponent.** The finding stands and
is sharper than I had it; it is `IDEA-20260809-7c2aed`.

### 1.4 What held

The corpus-state counts (§2) were correct. The `conversion rate` figure I corrected mid-turn
(6% → 47%) was itself the fix to an error of the same family: counting only named link
fields and missing `source_proposal` plus free references.

---

## 2. What the slices found

All counts re-measured at HEAD by the consolidating session. Spot-checks by the top-level
session are marked ✅ (verified exactly) or ⚠️ (overstated).

### 2.1 The framing of "never launched" was wrong

The `never-launched` slice reports, against the premise it was given:

> these goals are **NOT un-ideated**. Every one carries designed, deeply specified
> hypotheses (many with pre-registered forced values, nulls and positive controls) and
> frozen contracts. What is missing is narrower and sharper: the design layer took the
> **cheap disjunct** of the goal's own completion criterion, and the expensive disjunct —
> the one the goal was opened for — has no design at all.

And it re-partitions the debt: all **25** contracts under the 14 draft goals sit at
`review_required` with zero runs. That is **approval debt upstream of dispatch debt** —
`/run-experiment` was never eligible, so the bottleneck is the Coordinator approval step,
not the executor. Part 1 called this "execution debt"; that was too coarse.

### 2.2 Part of the execution debt is unreadable-contract debt ✅

**18 frozen experiment specifications do not parse at HEAD** — verified exactly, list
reproduced. One was frozen on 2026-08-07, which proves no parse check exists at the freeze
step. `DEC-20260724-020` **ordered that check 15 days ago**, on the finding that
`EXP-FB3-001` "sat unexecuted — no tool could read its contract"; the goal that owned the
obligation was marked `completed` in the same breath. `EXP-IC-002`, the yield-charged
descent control part 1 named as having "NO MEASURED REPLACEMENT", is one of the 18.
→ `IDEA-20260809-3971c1`

### 2.3 Goal records cannot describe their own state ⚠️/✅

`active_hypothesis_ids` is empty in **36 of 46 goals** (the cluster said 46 of 46 —
overstated, corrected here), and **202 of 271 hypotheses carry no `goal_id`** ✅. Worse, on
the closure side, verified exactly: **`GOAL-XEDN-001` cites `DEC-20260725-001` as its
closing decision, and that decision is a `revise` targeting `GOAL-ECDLP-001` / `BATCH-003`**
— another campaign entirely. `GOAL-XEDN-002` and `GOAL-ICLIFT-001` have the same defect,
traced to an ID collision that `CORR-20260729-001` recorded and nothing since revisited.
An external reader auditing the program's three oldest completion claims today lands on
unrelated records. → `IDEA-20260809-369dbe`

### 2.4 Rule 12 is unreachable and was never suspended, unlike rule 13

`AGENTS.md` rule 12 requires independent `review-breakthrough` at max effort and says it
"may not be degraded or run on a backend that cannot reach it". `GOAL-MLKEM-003`'s
BATCH-008 checkpoint records that no backend in this environment can serve it. The
consequence is precise: rule 12 "blocks the KN-FIND-012 restatement, the KN-FIND-014
withdrawal successor and the KN-OPEN-016 amendment, which remain owed", plus a fourth — a
supersession of `EV-MLKEM-015` that the validator and the red team **independently
recommended on the merits and each explicitly declined to perform, naming rule 12**.

CLAUDE.md rule 8 suspended the three-model closure quorum for exactly this reason. Rule 12
fails identically and was left standing. **The asymmetry runs in the dangerous direction:
closure got easier while correction stayed impossible.** → `IDEA-20260809-6b423b`

This is the natural companion to part 1's finding that `GOAL-FIND-001` is paused on the
suspended rule 13.

### 2.5 The apparatus built to measure this harness has never been run ✅

`docs/measuring-the-harness.md` specifies a two-axis eval programme and the code exists
across nine `orchestration/eval` modules. Verified at HEAD: `evals/results/` is
`.gitignore`d at line 42 and has never existed; **`evals/baselines/` contains only its
README, so no baseline has ever been pinned and the tuning loop has never completed one
cycle.** The apparatus is not rotted — `python3 -m orchestration.eval validate --suite
evals/suites/discipline.yaml` returns `OK: 8 task(s) valid, fixtures build, policies
resolve` ✅. The only thing between this program and its first self-measurement is deciding
to keep the output. → `IDEA-20260809-7c2aed`

### 2.6 The rest

| Cluster | Finding | Proposal |
|---|---|---|
| CHRG | The memory-charge exponent is mandatory, live at **1/2 and 1/3** in two lanes, never measured; and the `COST-*` disclosure record the template calls mandatory has zero instances, no schema, no validator entry | `IDEA-20260809-19e739` |
| QCOST | The classical cost model was deliberately unified (`KN-TECH-044` exists to prevent two accountings) and the quantum one never was; MAXDEPTH appears in **zero** `knowledge/` and **zero** `docs/` files while 13 goals name a NIST category; eleven papers on quantum ECDLP circuits are cited by nothing | `IDEA-20260809-243ab4` |
| EVDIS | `strength` is required with **no vocabulary and no semantics** (13 values, unchecked, while `proof_status` *is* checked); `run_ids: []` satisfies the required-field check on 203 of 326 records; 11 of 29 `replicated` records cite zero runs; the decision layer has no tier check at all | `IDEA-20260809-253a58` |
| KSUPR | Zero of 89 `KN-TECH` and zero of 58 `KN-FIND` entries have ever been superseded; 3 of 4 declared supersession edges have a null back-edge; `KN-TECH-029` reads `superseded_by: null` while 20 records cite it and its superseder's title names it | `IDEA-20260809-4896ba` |
| FRTAB | FrodoKEM's sampling table is treated as given by every design; its space is finite and exactly enumerable at standardized parameters, and `H-FRODO-e0c651` has already derived the machinery to place the published table on its own (divergence, DFR) frontier — pointed the other way | `IDEA-20260809-5a78e7` |
| FPREC | FN-DSA's finite-precision channel is named in the question's title, named by both hypotheses as where the 9.5-bit margin is consumed, and never measured — while `H-FNDSA-58b464` already derived the discriminator and left it unused | `IDEA-20260809-6c4035` |
| MPCFC | Three goals share the MPC-in-the-Head soundness object and derive it three times incompatibly; six triples where both derivations should agree are already listed, so the falsification is free | `IDEA-20260809-6f4575` |
| XAMOR | Symmetry-amortized preprocessing found independently in the ECDLP and lattice lanes, disclaimed as "an acknowledged structural analogy" in both; the ECDLP ratio is pinned at 1 and the lattice side has three figures in disagreement | `IDEA-20260809-8f32fd` |
| ISALT | Two 2026 reformulations of the supersingular isogeny problem sit uncited — one a polynomial system the program's own solving-degree instrument was built for | `IDEA-20260809-972c9e` |
| XENV | No committed number has ever been checked across two environments, although a matched cross-platform run set is already paid for and committed | `IDEA-20260809-7811bc` |
| CYCST | The class-group / S-unit route was audited for ML-KEM only; the audit's own finding enumerates what it did not close; the program holds the perfect null (FrodoKEM uses no ring) | `IDEA-20260809-9b01f9` |
| IMPOP | `GOAL-MLKEM-002` completed with its criterion resolved into a third outcome class — the instrument proven adequate at the moment its population became the open question | `IDEA-20260809-a985a1` |
| XJNT | The XEDN lane was completed three times on one statistic at the same four primes; the cheapest control is a fifth and sixth prime, not another degree raise | `IDEA-20260809-aaf81c` |
| BIKE | The one code-based KEM never framed — including in two papers the corpus cites whose titles name all three schemes | `IDEA-20260809-b53890` |
| PRCAL | The corpus's one open problem about its own reasoning prescribes a retrospective the committed data cannot support (§1.1) | `IDEA-20260809-81f74b` |
| LADDR | The inventor protocol calls its rung 2 "the one this program most often skips" and nobody has counted; 10 of 326 evidence records carry a `reproduced_baseline` | `IDEA-20260809-88708d` |
| PSEL | ROADMAP Phase 4.3 was retired by one line of prose in a markdown synthesis that is not a ledger record, cites no evidence and names no successor — and the deterministic baseline it assumed exists does not | `IDEA-20260809-898b29` |

---

## 3. Dropped as duplicates

Four gaps were dropped after checking against the 459 existing proposals:

1. **GOAL-ECDSA-001's crypto-tier certificate** — `IDEA-20260805-787c8b` already frames it
   more sharply, deriving the HNP success region as a bounded window with both edges
   computable in closed form, and naming the missing key recovery as its first deliverable.
2. **The claim-tier ceiling** — `IDEA-20260805-de2945` / `H-FIND-52472d`, which found a
   second cause (§1.2).
3. **GOAL-MONO-001's re-scoping** — `IDEA-20260805-cf2d5a` and `IDEA-20260805-a9a95d`
   already carry the science; the residue is a Coordinator act.
4. **Rank-metric decoding** — under-supported on the surveyor's own assessment; its live
   half belongs as a row in `IDEA-20260807-b63f08`'s accounting basis.

---

## 4. Verification

- `tools/validate_ledger.py`: **zero new errors.** The error-line diff against the
  pre-change run is empty; pre-existing failures are unchanged.
- `tools/allocate_id.py --check`: all 21 identifiers verified free before use, minted with
  `--next idea --date 20260809`.
- Schema: all 21 parse; all carry the six validator-required `idea` fields; every filename
  matches its `id`.
- Spot-checks by the top-level session: the 18 unparseable specifications ✅ (exact list),
  `evals/baselines/` contents ✅, the eval apparatus validating ✅, 202 of 271 hypotheses
  without `goal_id` ✅, the `GOAL-XEDN-001` → `DEC-20260725-001` mis-resolution ✅. One
  overstatement corrected: `active_hypothesis_ids` is empty in 36 of 46 goals, not 46 ⚠️.

**Standing limits.** Every proposal carries `novelty_status: unverified`. None claims an
exponent improvement. Most predict a negative and several say so in their titles. Priors of
survival are stated per record and are mostly low.
