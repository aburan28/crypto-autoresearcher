# Reconciliation: TASK-20260809-4e04eb's DAG-structure proposal against RQ-ARGON-141710's ten proposals

- task: TASK-20260810-7e0990
- role: coordinator
- goal: GOAL-ARGON-001
- batch: BATCH-0c7f2f
- question: RQ-ARGON-141710
- date: 2026-08-10
- governs: DEC-20260809-8732e6's next_action (reconcile before designing any experiment)
- claim tier: **reconciliation of existing PROPOSAL records only.** No hypothesis
  or experiment record is created here. No claim about Argon2's security, any
  parameter set's safety, or any attack's cost is made anywhere below. This
  document does not itself constitute the official Coordinator decision — that
  is DEC-20260810-627dd4, written by the downstream ledger-archive task
  (TASK-20260810-70a1bf) from this document's findings.

---

## 0. Method

Read in full: `ledger/goals/GOAL-ARGON-001.yaml` (next_action and its
supersession history), `ledger/questions/RQ-ARGON-141710.yaml`,
`ledger/evidence/EV-ARGON-209ece.yaml`, `ledger/decisions/DEC-20260809-8732e6.yaml`,
`coordination/goals/GOAL-ARGON-001/batches/BATCH-09d69e/tasks/TASK-20260809-4e04eb/proposal.md`
(all 11 sections), both independent review reports
(`.../reviews/TASK-20260809-28c68e/validation_report.yaml`,
`.../reviews/TASK-20260809-a0f79c/red_team_report.md`), and all nine
`ledger/proposals/IDEA-20260809-{a915ea,ac5947,ac98b5,b17238,b9e9cc,bcf891,bf5139,c059a7,c13b8b}.yaml`
records in full (not titles/frontmatter only). Verdicts below are grounded in
that content, joined on `question_id: RQ-ARGON-141710`, not on body-text
search — the exact methodology gap both independent reviews found in the
producer's own dedup pass.

---

## 1. Verdict: TASK-20260809-4e04eb's proposal vs. IDEA-20260809-a915ea

**Verdict: SUPERSEDE (content-wise).** TASK-20260809-4e04eb's proposal is the
surviving formalization of "measure the Argon2 memory-access DAG's
depth-robustness directly" that a future `/design-experiment` step should
build on, in place of a915ea.

**Reasoning, grounded in content comparison, not titles:**

- **Same tracked object.** a915ea's claim is: "the Argon2 memory-access DAG
  ... is completely determined and can be built explicitly... attacker-
  relevant structural quantities — above all the size of a set whose removal
  reduces the graph's depth below a target — can be computed exactly or
  tightly bounded." TASK-20260809-4e04eb's proposal §2 tracks the identical
  object (DAG topology, depth-reducing-set size) and explicitly credits it as
  "the object the goal's own `next_action` already names," not a novel
  invention — i.e., the new proposal itself does not claim to introduce a new
  object, only a new operationalization of a915ea's object.
- **Same directional claim, strictly more specific.** a915ea predicts the
  measured curve will be "systematically different from the asymptotic
  family's guarantee at recommended parameters" — a qualitative, untargeted
  prediction with no named mechanism for *why*. TASK-20260809-4e04eb's
  proposal §4 supplies a specific causal mechanism (recency-biased
  within-window reference selection, C6) and a scale-free quantitative
  metric (`rho = |S*_real|/|S*_unif|`) with two-tier, pre-registered
  falsification thresholds (`rho <= 0.5` confirms, `rho >= 0.8` falsifies,
  `[0.5,0.8)` reported as partial) plus a cheaper precondition falsifier (KS
  test on the offset distribution) that runs first. This is a's915ea's
  general claim made specific and falsifiable, not a different claim.
- **a915ea's own fields disclose it is an unworked sketch.** `source_refs:
  RFC 9106 -- REQUIRED READ, NOT YET READ`; `novelty_screen: WEB NOT
  CHECKED`; no null-object control is named; no quantitative metric is named
  (only "curve, marked exact or bounded per point," with no comparison
  baseline); no falsification threshold is stated beyond "the symbolic DAG
  disagrees with the instrumented access pattern" (a construction-validity
  check, not a hypothesis falsifier). TASK-20260809-4e04eb's proposal
  supplies all of these: an explicit window-matched uniform null (`G_unif`),
  a scale-free ratio metric, two-tier falsification, a structural-tell
  scaling control, and two named, validation-routed heuristics (H1, H2) —
  independently confirmed present and non-vacuous by both reviewers
  (validator `hypothesis_consistency_checks`, all PASS; red-team §1, "no
  escape hatch found").
- **a915ea's second prediction is subsumed, not dropped.** a915ea's second
  observable ("how far up in (t,m) exact computation reaches") is carried
  forward inside TASK-20260809-4e04eb's proposal as methodology rather than
  a separate prediction: §6 step 6 (small-scale exact/ILP cross-check) and
  step 7 (scale sweep) do exactly this, now embedded as a *control* on the
  greedy heuristic's error rather than a free-standing observable. Nothing
  a915ea asked for is lost; it is absorbed into a more disciplined design.
- **Independent corroboration.** RFC 9106's seven RECALLED premises (C1-C7)
  that TASK-20260809-4e04eb's proposal is built on were independently
  spot-checked by the Validator against the actual primary text via raw HTTP
  fetch and found accurate at the claimed confidence for every one,
  including the load-bearing, self-flagged-uncertain C6 (directionally
  confirmed). a915ea carries no equivalent corroboration — it never got past
  "REQUIRED READ, NOT YET READ."

**What "supersede" does and does not mean here.** This is a content-level
finding, not a ledger status transition: this task's write scope permits
editing only IDEA-20260809-a915ea's `dominated_by` field (and one directly-
adjacent field for internal consistency, see §4 below), not its `status`
field, and no other task in this batch has write access to
`ledger/proposals/*.yaml` `status` fields either. A formal `status:
superseded` transition on a915ea, if this program's proposal-record schema
supports one, is **not performed by this task** and is named as an open
item for whoever next has write scope over that file (see §5). What *is*
decided here, as the Coordinator content ruling that DEC-20260810-627dd4
should record: a future `/design-experiment` step on this research
direction should read TASK-20260809-4e04eb's proposal, not a915ea, as its
starting formalization.

---

## 2. Verdict: TASK-20260809-4e04eb's proposal vs. IDEA-20260809-ac5947

**Verdict: STAND-ALONE, with an upstream-dependency note.** ac5947 is not
superseded or merged — it answers a genuinely different question (measured
*attack cost* at recommended parameters, `class: algorithm`) from
TASK-20260809-4e04eb's proposal (measured *graph structure*,
`class: measurement`). Both are legitimate, distinct, non-duplicate
contributions to RQ-ARGON-141710's roadmap.

**Does the new proposal's more rigorous formalization change what ac5947
should build on?** Yes, in one specific and narrow respect. ac5947's
`mechanism` field reads: "store a subset of blocks, recompute the rest on
demand using the graph structure **from IDEA-20260809-a915ea**." That is a
named upstream dependency on a915ea's (unworked, unsourced) graph object.
Given §1's finding that TASK-20260809-4e04eb's proposal is the more rigorous
successor formalization of exactly that graph object — same topology, same
depth-reducing-set target quantity, now with an explicit, RFC-corroborated
construction procedure (proposal.md §6 step 2, "the topology-only builder")
— ac5947's downstream graph-construction dependency should, going forward,
be read as pointing at whichever record becomes the surviving DAG-structure
formalization from this reconciliation (i.e., TASK-20260809-4e04eb's
proposal once it is carried into a filed/frozen form), not literally at
a915ea's sketch. This is a **reference-currency note, not a content change**
to ac5947: ac5947's own hypothesis (attack cost as a computation-memory
pair, not a factor) is unaffected either way, since it needs *a* graph
construction to recompute against, not a specific one of the two competing
sketches. No edit to ac5947's file is made by this task (outside write
scope); the note is recorded here for whoever next designs an experiment
that depends on ac5947.

**bcf891's role is unchanged by this verdict.** bcf891 explicitly names
itself "a precondition for IDEA-20260809-a915ea's numbers being usable."
Since TASK-20260809-4e04eb's proposal's own §6 step 6 sketches only a
*weaker*, self-referential small-`q` exact/ILP cross-check (compare greedy
`|S*|` to exact on the same two graphs, `G_real` and `G_unif`, already under
test) rather than bcf891's *independently*-known-family calibration (known
depth-robust and known-shallow reference families, bounding the greedy
heuristic's error in both directions before trusting any Argon2-graph
number at all), bcf891's precondition status transfers unchanged onto
TASK-20260809-4e04eb's proposal: bcf891 is a required calibration control
for *this* proposal's numbers being usable too, exactly as
DEC-20260809-8732e6's next_actions already ruled. This is confirmed here,
not newly decided.

---

## 3. The other seven proposals

Read in full; none requires the depth of treatment given a915ea/ac5947
above because none overlaps TASK-20260809-4e04eb's proposal's specific
graph-structure-and-null-comparison content. Brief relationship notes:

- **IDEA-20260809-ac98b5** (frontier mapping in (t,m,p)) — `dominated_by:
  Downstream of IDEA-20260809-ac5947`. Depends on attack-cost measurements
  ac5947 would produce, not on graph topology directly. No overlap with
  TASK-20260809-4e04eb's proposal; unaffected by this reconciliation.
- **IDEA-20260809-b17238** (three-variant tradeoff-vs-leakage harness) —
  `dominated_by: Downstream of IDEA-20260809-ac5947`. Same relationship as
  ac98b5: consumes attack-cost results, not graph topology. Unaffected.
- **IDEA-20260809-b9e9cc** (parallelism/lane effect on depth-robustness) —
  `dominated_by: Downstream of IDEA-20260809-a915ea`. This one **does**
  share a load-bearing dependency with the a915ea finding above: its own
  `controls` field states a "SINGLE-LANE ANCHOR" requirement — "at p equal
  to one the measurements must match those of IDEA-20260809-a915ea
  exactly." Per §1's verdict, that anchor should, going forward, be read
  against TASK-20260809-4e04eb's proposal's single-lane construction (its
  own explicit scope restriction, proposal.md §5) rather than a915ea's,
  since it is the more rigorous, RFC-corroborated formalization of the same
  single-lane object. This is the same reference-currency note as ac5947's
  (§2 above), not a content conflict — b9e9cc's own hypothesis (depth-
  reducing-set size decreasing in `p`) is independent of which sketch
  supplies the `p=1` baseline. No edit made; recorded for the next
  `/design-experiment` step that touches b9e9cc.
- **IDEA-20260809-bcf891** (calibration against known-depth-robust/known-
  shallow families) — already treated in §2 as a load-bearing, unresolved
  precondition, not superseded or merged by anything in this batch.
- **IDEA-20260809-bf5139** (hardware-aware AT cost model) —
  `dominated_by: Downstream of IDEA-20260809-ac5947`. Consumes an attack
  cost curve; no graph-topology overlap. Unaffected.
- **IDEA-20260809-c059a7** (defender/attacker cost ratio surface) —
  `dominated_by: Downstream of the whole goal`. Consumes both graph and
  attack results at a late stage; no direct overlap with this
  reconciliation's subject matter. Unaffected.
- **IDEA-20260809-c13b8b** (queryable, no-recommendation measurement
  artifact) — `dominated_by: Downstream of the whole goal`. Tooling over
  the eventual measured grid; no overlap. Unaffected.

None of these seven is superseded, merged, or otherwise touched by this
reconciliation. The goal's roadmap (graph structure -> attack cost ->
frontier -> variant comparison -> hardware-aware pricing -> ratio surface ->
queryable artifact) remains intact; only the graph-structure node (a915ea
vs. TASK-20260809-4e04eb's proposal) needed resolving, plus the one
reference-currency note each on ac5947 and b9e9cc.

---

## 4. IDEA-20260809-a915ea `dominated_by` correction

**Defect:** a915ea's `dominated_by` field asserted "Not dominated by any
corpus record; no memory-hard-function records exist in the corpus." This
is factually false. `knowledge/INDEX.md` contains eight matching records
(`KN-LIT-3385`, `KN-LIT-4894`, `KN-LIT-494`, `KN-LIT-5442`, `KN-LIT-6385`,
`KN-LIT-6793`, `KN-LIT-7033`, `KN-LIT-7247`), independently confirmed twice:
once by TASK-20260809-4e04eb's own dedup pass (proposal.md §1) and once,
independently, by the Validator (`validation_report.yaml`
`dedup_verification`, "THE FLAGGED ERROR IS REAL... the corpus does contain
eight memory-hard-function-adjacent literature records," each spot-checked
as a real git-tracked file). Recorded formally in EV-ARGON-209ece and named
as this batch's required correction in DEC-20260809-8732e6.

**Correction applied** (`ledger/proposals/IDEA-20260809-a915ea.yaml`,
this task's sole permitted ledger edit):

- `dominated_by` rewritten to state the corpus fact accurately, name the
  eight records, cite the correcting evidence, and honestly state what
  remains unconfirmed (whether any of the eight specifically dominates
  a915ea's claim — not verified either way; `KN-LIT-3385`'s title is the
  closest match but carries no verified author/year/abstract in this
  corpus per the producer's own read, so it is not citable as a confirmed
  dominating record).
- `novelty_screen` also corrected: this field is directly adjacent to
  `dominated_by` and asserted the same false premise from the same root
  cause (a grep pattern too narrow to find the eight records, i.e. "no
  records") — left uncorrected, it would now directly contradict the fixed
  `dominated_by` field in the same record. Corrected minimally, preserving
  the field's original honest hedge ("WEB NOT CHECKED") rather than
  rewriting the record.

No other field in a915ea.yaml is touched. The record's `claim`, `mechanism`,
`predictions`, `controls`, `falsification_conditions`, `status`, and every
other field are left exactly as filed, per this task's write-scope
restriction and per this program's rule that ledger records are corrected
by superseding or by the Coordinator editing a specifically-defective field
with a stated reason, never silently rewritten wholesale.

---

## 5. Recommended next concrete action for GOAL-ARGON-001

1. **RFC 9106 primary-source acquisition remains the correct immediate next
   move, unchanged from DEC-20260809-8732e6.** The Validator demonstrated a
   working route in this environment (raw HTTP fetch via `curl` against
   `https://www.rfc-editor.org/rfc/rfc9106.txt`, HTTP 200, full text
   retrieved) where `WebFetch`/`WebSearch` fail identically for every agent
   that has tried them in this branch (producer, validator, red-team all
   independently hit the same backend-model infra error on the tool route).
   This reconciliation does not change that finding or that recommendation;
   it is restated here because RQ-ARGON-141710's own constraints require
   RFC 9106 filed as a primary KN-LIT source before any measurement is
   recorded, and TASK-20260809-4e04eb's proposal's own C7 (the exact
   recommended `(t,m,p)` table) is still unread. This task does not perform
   the fetch (no Bash/git access in this task's tool set; the Validator's
   route requires shell access this coordinator session does not have) —
   it is named as the next dispatched task's job, exactly as
   DEC-20260809-8732e6 already directed.
2. **Surviving formalization for the next `/design-experiment` step:**
   TASK-20260809-4e04eb's proposal (this batch's `proposal.md`), not
   a915ea's original sketch, per §1's verdict. When that step runs, it
   should:
   - freeze proposal.md §6's construction procedure and two-tier
     falsification design (KS precondition, then `rho` against `G_unif`);
   - **substitute bcf891's independent-known-family calibration
     (known-depth-robust + known-shallow reference families) for, or in
     addition to, the self-referential small-`q` exact/ILP cross-check
     currently sketched in §6 step 6**, per §2 above and per
     DEC-20260809-8732e6's unchanged next_action;
   - carry forward proposal.md §3's RECALLED/UNVERIFIED table and replace
     each entry with the confirmed RFC 9106 text once item 1 above lands
     (the Validator's spot-check already gives high confidence all seven
     will resolve as stated, but the frozen experiment contract must cite
     the primary text directly, not the spot-check);
   - name, as an explicit open item inherited from the Red Team's review
     (`red_team_report.md` §2, "NULL-VS-THEORY GAP"), that the window-
     matched uniform null `G_unif` is not yet shown to be the comparison
     the (still-unread) depth-robust-graph asymptotic literature itself
     makes — this cannot be resolved until that literature is located and
     read, and should not be silently assumed away when the experiment is
     frozen.
3. **Reference-currency notes for ac5947 and b9e9cc** (§2, §3 above) should
   be applied by whoever next has write scope over those files, or at
   minimum re-affirmed in the experiment contract that eventually builds on
   them — not a blocking precondition, since both proposals' own
   hypotheses are independent of which graph-construction sketch supplies
   the underlying object.
4. **A915ea's proposal `status` field** (currently `proposed`) is not
   changed by this task (outside write scope); if this program's schema
   supports a `superseded`/`refined` proposal status distinct from a
   hypothesis-record status, that transition is named here as unperformed
   and left to a future task with the appropriate write scope.

No hypothesis or experiment record is created by this task. No claim about
Argon2's security, any parameter set's safety, or any attack's cost is made
anywhere in this document.
