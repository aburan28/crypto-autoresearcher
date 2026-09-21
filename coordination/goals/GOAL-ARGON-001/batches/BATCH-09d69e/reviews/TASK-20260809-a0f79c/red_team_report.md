# Red-team report: TASK-20260809-4e04eb proposal (BATCH-09d69e)

```yaml
red_team_report:
  id: RT-20260809-a0f79c
  task_id: TASK-20260809-a0f79c
  claim_under_review: >-
    proposal.md §4 (TASK-20260809-4e04eb, snapshot commit da073ca9d, parent
    dce4cf061 verified against Git, sha256 of both artifacts verified against
    the snapshot receipt): "recency-biased reference selection collapses
    per-lane depth-robustness relative to a window-matched uniform-reference
    null" — a graph-structure-only hypothesis, no attack, no security verdict.
  objections:
    - "§6 title-vs-body inconsistency: §4's own section title asserts the
       mechanism as fact ('...collapses per-lane depth-robustness...') while
       the same section immediately states 'this is a genuine two-outcome
       discriminator, not a foregone conclusion.' The title should be phrased
       as a hypothesis ('would collapse' / 'predicted to collapse'), not a
       finding, or a downstream reader who reads titles only will treat this
       as an established result before the KS precondition or the rho
       measurement has run."
    - "The rho <= 0.5 (confirm) / rho >= 0.8 (falsify) thresholds are
       pre-registered (good) but are round numbers with no derivation from
       any depth-robust-graph theorem's own notion of 'material' weakening —
       they are declared, not derived, and the proposal itself says the
       relevant theory (Alwen-Blocki-Pietrzak et al.) was never read. Once
       primary literature is available, these thresholds should be
       re-anchored to whatever constant the tradeoff-attack argument treats
       as material, not kept as this session's arbitrary picks."
    - "The KS precondition test (§4, testing C6: is z/W(j) recency-biased)
       is framed as a 'genuine' falsifier of the whole mechanism, but Argon2's
       reference-index transform biasing z toward recent blocks is
       well-established public/textbook knowledge about the algorithm,
       independent of whether RFC 9106 was fetched in this session. This
       reviewer's own (equally unverified-in-session, but concurring)
       recollection is that this is documented, intentional design, not an
       open question. Presenting the KS check as a coin-flip discriminator
       therefore somewhat overstates its informativeness — it is a legitimate
       cheap sanity gate, but it is very unlikely to actually falsify
       anything, and the proposal should say so rather than imply real
       uncertainty about C6's direction."
    - "SCOPE-CREEP CHECK: no violation found. Every place the document could
       have drifted into a verdict, cost claim, or recommendation instead
       states the disclaimer explicitly (header, §5, §9, §11). The strongest
       language risk is the §4 section title above, which is a framing/editing
       defect, not a substantive scope violation."
  required_controls:
    - "NULL-VS-THEORY GAP (the sharpest control gap in §7): G_unif matches
       G_real's window size W(j) and randomizes only the within-window
       choice, which correctly isolates 'does the selection RULE matter
       beyond window truncation.' It does NOT establish that comparing
       against a window-matched uniform null is the comparison 'the
       asymptotic tradeoff-attack argument assumes' — the RQ's own stated
       target. Depth-robust-graph constructions studied in this literature
       are not uniformly restricted to a recent, truncated window; some
       explicit constructions deliberately place edges at many DISTINCT
       SCALES across the full prior history precisely to defeat local
       node-removal attacks. If the asymptotic bound this goal wants to test
       against assumes access to the FULL prior history rather than a
       truncated recent window, then BOTH G_real and G_unif in this design
       are already far from that idealized construction, and a low rho
       relative to G_unif would say only 'worse than a window-truncated
       uniform baseline,' not 'diverges from what the theory assumes.' This
       is not flagged anywhere in §7's confounder list and should be, even
       though it cannot be resolved until the cited literature is actually
       read (which the proposal itself names as the hard precondition)."
    - "CALIBRATION AGAINST KNOWN GROUND TRUTH (missed sibling control): §6
       step 6 / §7 'greedy heuristic asymmetry' proposes only a small-scale
       exact/ILP cross-check on the SAME two graphs already under test
       (G_real vs G_unif). A materially stronger, already-designed control
       exists in this program's own ledger and was not found by this task's
       dedup pass: IDEA-20260809-bcf891 ('Calibrate the graph measurement
       against constructions whose depth robustness is known, in both
       directions') proposes running the identical measurement pipeline
       against an INDEPENDENTLY known-depth-robust family and an
       independently known-shallow family, bounding the greedy heuristic's
       error in both directions before trusting any Argon2-graph number.
       bcf891 explicitly states it is 'a precondition for IDEA-20260809-a915ea's
       numbers being usable' — a915ea being the direct ancestor of this
       task's own hypothesis. A future /design-experiment step on this
       proposal should adopt bcf891's calibration design rather than the
       weaker self-referential cross-check sketched here."
    - "Null-model sampling variance and window-boundary controls (§7) are
       adequately designed as stated; no further objection."
  counterexample_or_mutation: >-
    Cheapest discriminating control beyond what's already in the proposal:
    run the sketched pipeline (§6 steps 1-5) against IDEA-20260809-bcf891's
    two reference families (a known-(e,d)-depth-robust construction and a
    deliberately shallow one) at the SAME small q used for this proposal's
    own exact/ILP cross-check, BEFORE running it on the real Argon2 topology.
    If the greedy heuristic's rho on the known-depth-robust family is not
    close to 1 (i.e., it wrongly reports the known-robust graph as
    shatterable), or its rho on the known-shallow family is not close to a
    correctly small value, the pipeline's own measurement error dominates
    whatever rho is later reported for G_real vs G_unif, and no Argon2 rho
    value is interpretable until that is fixed. This is strictly cheaper
    than building the real Argon2 topology (it needs no G-evaluations, no
    RFC 9106 read) and should run first.
  baseline_comparison: >-
    Not directly applicable in the ECDLP-baseline sense (Pollard-rho/BSGS
    have no analogue here); this is a measurement/control proposal, not an
    algorithmic claim. The relevant "baseline" is the uniform-reference null
    G_unif itself, which is present and adequately isolates the
    within-window selection rule (see required_controls for the deeper gap:
    it is not shown to be the comparison the cited asymptotic literature
    itself uses).
  heuristic_challenges:
    - "H1 (reference-index output modeled as Uniform[0, 2^32)) is honestly
       labeled as unproven and given a stated validation route (chi-sq/KS
       against G's real output). Adequate as stated; no objection beyond
       requiring the transfer-scale statement to actually appear when run."
    - "H2 (configuration-model / marginal-independence approximation) is the
       correct classical analogy (Molloy-Reed style) and comes with its own
       validation route (independent resampling from the empirical marginal
       as a third control object) — well-designed. No objection."
    - "C6 (the load-bearing recency-bias premise) is correctly flagged by the
       proposal itself as its 'single most load-bearing and least certain
       recalled detail' with medium-low self-assessed confidence — but see
       objections above: this reviewer's independent (also unverified)
       recollection suggests the actual uncertainty is lower than
       medium-low, which cuts toward the precondition check being closer to
       a formality than a coin flip. Flagged as a caveat on the 'genuine
       two-outcome discriminator' framing, not a defect in the check itself."
  cost_model_challenges:
    - "§9 correctly disclaims any algorithmic-complexity-improvement claim
       and states O(q) construction cost and O(q^2) naive greedy cost, with
       the RFC-scale-q risk named as unresolved. No attempt to hide cost in
       o(1)/polylog cofactors, because no asymptotic claim is made. No
       objection beyond what the proposal itself already flags (naive O(q^2)
       greedy heuristic may not reach literal RFC-recommended q without
       engineering not committed to here)."
  reduction_and_scope_challenges:
    - "No reduction chain (OneEnd/EndRing/Isogeny-style) is claimed here;
       not applicable."
    - "Affected-vs-safe scheme scope: not applicable — no scheme is claimed
       affected or safe by this proposal at any point."
  proof_architecture_challenges:
    - "Not applicable — proposal.md correctly self-classifies as a
       'measurement'-class idea (agents/idea-generator.md taxonomy), not a
       proof-oriented/asymptotic-complexity claim, so docs/inventor-protocol.md
       §8's proof_search_map is correctly not required here (per this task's
       own dispatch-queue constraint)."
  narrowest_supported_statement: >-
    proposal.md's mechanism, quantitative prediction (rho), two-tier
    falsification design, and null-object control are genuinely falsifiable
    and non-vacuous, and its RFC-9106-access-failure and honest-accounting
    sections hold up under independent challenge (see verdict below for the
    corroborating check performed by this review). However, the document's
    own "DEDUP FIRST" duty is satisfied only partially: it undercounts
    existing sibling proposals under RQ-ARGON-141710 by nearly half (5
    claimed vs. 9 actually on record, all pre-dating this batch) and misses
    the two most relevant ones (IDEA-20260809-ac5947, the direct downstream
    tradeoff-attack proposal this graph work is meant to feed, and
    IDEA-20260809-bcf891, a stronger, already-designed calibration control
    for exactly this proposal's weakest methodological point). This
    proposal's CONTENT should not be rejected on that basis — it adds real,
    verifiable rigor over its nearest sibling (a915ea) — but it is not yet
    reconcilable with the existing sibling set as filed, and should not be
    treated as the sole or primary next input to a /design-experiment step
    without that reconciliation.
  next_concrete_action: >-
    Before any /design-experiment step: (1) Coordinator reconciles this
    task's proposal against all nine existing RQ-ARGON-141710 proposals
    (join key question_id, not literal-string "Argon2" grep — see
    dedup-methodology finding below), explicitly deciding whether this
    task's content supersedes, merges with, or stands alongside a915ea and
    ac5947; (2) if/when a frozen experiment is designed for this hypothesis,
    adopt IDEA-20260809-bcf891's independent-known-family calibration in
    place of (or in addition to) the self-referential small-q cross-check
    sketched in proposal.md §6 step 6; (3) re-run the RFC 9106 fetch routes
    in a future session — this review's own WebFetch/WebSearch attempts
    failed with the identical backend-model error, corroborating that the
    blocker is session/infra-wide and not specific to the producing agent.
  artifact_paths:
    - coordination/goals/GOAL-ARGON-001/batches/BATCH-09d69e/tasks/TASK-20260809-4e04eb/proposal.md
    - coordination/goals/GOAL-ARGON-001/batches/BATCH-09d69e/tasks/TASK-20260809-4e04eb/receipt.yaml
    - coordination/goals/GOAL-ARGON-001/batches/BATCH-09d69e/archives/TASK-20260809-862322/snapshot-receipt.json
    - ledger/proposals/IDEA-20260809-a915ea.yaml
    - ledger/proposals/IDEA-20260809-ac5947.yaml
    - ledger/proposals/IDEA-20260809-bcf891.yaml
```

## Verdict

**CONDITIONAL PASS on content; FAIL on the dedup/novelty duty as performed.**
The hypothesis is genuinely falsifiable and the two-tier design is not an
escape hatch (see §1 below). The scope discipline holds (see §3). The RFC
9106 access failure is independently corroborated by this review as a real,
reproducible infrastructure failure, not a cover story (see §5). But the
"DEDUP FIRST" named duty, marked `satisfied: true` in receipt.yaml, is
factually wrong on its own terms: the proposal states "five same-day
proposals" exist under `RQ-ARGON-141710`; **nine** do, and all nine were
committed to `main` (commit `0f4698ebd`, "open twelve draft goals and 108
proposals") before `GOAL-ARGON-001` was even activated (commit `dce4cf061`,
verified ancestor). This is not a hard-to-find gap — `grep -l
"RQ-ARGON-141710" ledger/proposals/*.yaml` finds all nine in one command.
The four missed proposals are not peripheral: one
(`IDEA-20260809-ac5947`) is the actual tradeoff-attack implementation this
graph work exists to feed, explicitly built on `a915ea`'s graph object; one
(`IDEA-20260809-bcf891`) is a stronger, already-designed calibration control
for precisely this proposal's weakest link (validating the greedy
depth-reducing-set heuristic). See objections and required_controls above
for the substantive detail.

---

## 1. Falsifiability of §4 — no escape hatch found, with two caveats

The two-tier design is genuinely non-vacuous:

- **Precondition tier** (KS test on `z_j / W(j)` vs. `Uniform[0,1)`): a clean
  binary gate. Failing to reject uniformity kills the entire mechanism's
  premise outright, stated explicitly as such, and is checked *before* any
  expensive depth-reducing-set compute — correctly ordered per
  `docs/inventor-protocol.md` §3's "cheapest structural tell first" spirit.
- **Material-effect tier** (`rho`): asymmetric quantifiers by design — `rho
  <= 0.5` must hold *at every tested pair* to confirm, `rho >= 0.8` at *any*
  tested pair falsifies. This is the conservative direction (harder to
  confirm, easier to falsify) and is not gameable after the fact because the
  thresholds are declared before any measurement runs.
- The **middle zone** `[0.5, 0.8)` is explicitly reported as "partial
  effect... not rounded into either bucket," which is the honest behavior —
  it does not let the proposal claim success regardless of outcome. I looked
  specifically for language that would let a `rho` anywhere in `[0, 1)` be
  spun as "confirmed" and did not find it.

Two caveats, not disqualifying: the `0.5`/`0.8` cutoffs are declared round
numbers, not derived from the (unread) depth-robust-graph literature's own
notion of "material," and should be revisited once that literature is read.
Separately, the precondition check is less of a coin-flip than presented —
see `heuristic_challenges` above.

## 2. Controls before belief — real gap in §7, reinforced by a missed sibling

`G_unif` is a fair null for the question "does the *within-window* selection
rule matter" (matched chain edges, matched `W(j)`, only the offset draw
differs) — this correctly neutralizes the window-boundary confound §7
already names. The gap is one level up: §7 never asks whether comparing
against a *window-truncated* uniform null is the comparison the cited
asymptotic tradeoff-attack argument itself makes, as opposed to a
theoretical construction with edges spanning the *full* prior history at
multiple scales. Because the underlying literature was never read (both by
the producer and, independently, by this review — see §5), neither of us can
resolve this, but it should be named as an open gap rather than left
implicit. This dovetails with the missed-sibling finding in §6/§7 above:
`IDEA-20260809-bcf891` already proposes calibrating the exact same pipeline
against independently-known depth-robust and known-shallow graph families,
which is a strictly stronger check than the self-referential small-`q`
exact/ILP cross-check sketched in this proposal's §6 step 6, and was not
found or engaged with.

## 3. Scope creep — none found, one framing defect

Every section that could have drifted toward a verdict, an attack-cost
number, or a recommendation instead states the disclaimer explicitly and
repeatedly (header, §5, §9, §11), and §9 even retitles the standard
"target-complexity" field to make clear no algorithmic claim is made. The one
defect worth naming precisely: §4's own section title states the mechanism
as an accomplished fact ("...collapses per-lane depth-robustness...")
immediately before the body calls it "a genuine two-outcome discriminator,
not a foregone conclusion." A reader who skims section titles only would
walk away with an unearned conclusion. This is an editorial tell, not a
substantive violation — but it is exactly the kind of drift the next
`/design-experiment` write-up should not repeat in its own title.

## 4. Premature closure / overclaiming — §10/§11 hold up under challenge

`novelty_status: unverified` is correctly forced by the disclosed unchecked
web-literature pass, per program rule. `dominated_by` is handled correctly —
the producer refuses `null` (which would assert a full frontier check that
did not happen) and instead writes an honest, hedged, non-null string
naming the likely-but-unconfirmed dominating family. `sota_delta` is stated
as a test-design contribution, not a numeric result, which matches what was
actually produced. "Enumerated closures: none" is correct — nothing is
closed here. The one terminology nit: the proposal's own text uses the word
"supersedes" informally to describe its relationship to `a915ea`
("supersedes a915ea in content depth"), which is a loaded, reserved term in
this program's immutable-record system; the producer does immediately
qualify it ("makes no ledger edit"), which defuses the risk, but a future
reader citing this proposal out of context could still misread it as a
formal supersession. Minor; worth a note, not an objection.

## 5. RFC 9106 access failure — independently corroborated, not an excuse

This review made its own `WebFetch` attempt against
`https://www.rfc-editor.org/rfc/rfc9106.txt` and its own `WebSearch` for
`"RFC 9106 Argon2 recommended parameters memory iterations"`, from an
independent session. **Both failed with the identical error** the producer
reported: `There's an issue with the selected model
(us.anthropic.claude-haiku-4-5-20251001-v1:0). It may not exist or you may
not have access to it.` This is a strong independent data point: the
blocker is a genuine, reproducible, session/infra-wide failure of the
`WebFetch`/`WebSearch` backend, not something specific to the producer's
tool use or an excuse to skip a route that was actually available. On the
"tried hard enough" question: this review also checked for a local corpus
route the producer might have missed — a `downloads/` directory referenced
by two adjacent `KN-LIT` records' `Local copies` fields
(`KN-LIT-3385.md`, `KN-LIT-7247.md`) — and confirmed **no such directory
exists anywhere in this worktree** (`find . -iname downloads` returns
nothing), so there was no locally-available RFC 9106 or Argon2-spec PDF for
the producer's `Grep`/`Glob` pass to have missed. The producer's declared
route list (6 fetch/search attempts across 3 URL variants and 2 queries,
plus a local corpus search) is reasonable given a single-point-of-failure
backend where every retry predictably fails identically; the honest
labeling of every recalled algorithmic detail (`§3`'s RECALLED-vs-VERIFIED
table) as unconfirmed, rather than reconstructing RFC 9106 from memory and
presenting it as read, is exactly the required behavior under this
program's rules and was followed.

## 6. Sibling-proposal collision — the strongest finding of this review

The task handoff names five siblings (`a915ea, ac98b5, b17238, b9e9cc,
c059a7`). `grep -l "RQ-ARGON-141710" ledger/proposals/*.yaml` returns
**nine**: those five plus `ac5947`, `bcf891`, `bf5139`, and `c13b8b`. All
nine were committed in a single prior commit
(`0f4698ebd`, "ideas: open twelve draft goals and 108 proposals across
uncovered deployed-crypto lanes") which is a verified ancestor of the
commit that activated `GOAL-ARGON-001` and opened `BATCH-09d69e`
(`dce4cf061`) — i.e., all nine existed and were available well before this
batch, let alone this task, was dispatched. The producer's dedup method
(`grep`-ing `ledger/proposals/` for the literal string `Argon2`) is why four
were missed: only one of the four (`bcf891`) happens to contain the literal
substring "Argon2" in its body text; the other three refer only to "the
goal," "the memory-access graph," etc., and are joined to this question
solely via their `question_id: RQ-ARGON-141710` field, which the producer's
search pattern never checked. `batch.yaml`'s own `dedup_census: []` is also
empty, so this gap was not caught at batch-opening time either — worth
naming for the Coordinator, though reconciling it is explicitly not this
task's job.

Substantively, does this task's proposal add something the nine don't
already have? **Partially, and only relative to the five the producer did
find.** Against `a915ea` (the closest match), yes: `a915ea` is an unsourced
sketch with no explicit quantitative metric, no null-object control, and no
tiered falsification design; this task's proposal supplies all three. But
against the four missed siblings, the answer is less clean: `ac5947` is the
literal downstream attack this graph-structure work exists to feed, and
already names the graph object (`from IDEA-20260809-a915ea`) this task
re-derives with more rigor — meaning the Coordinator now has two
independent, non-identical formalizations of "measure the DAG structure
first" in play (`a915ea`'s original sketch and this task's more rigorous
version) with no reconciliation. `bcf891` had already anticipated and
designed a stronger version of exactly the calibration control this
proposal's own §7 admits is only partially addressed (see §2 above). Given
that six of the nine siblings (`a915ea, ac5947, ac98b5, b17238, b9e9cc,
bcf891`) already sketch essentially the entire roadmap this goal's
`next_action` describes — graph-first measurement, the actual attack,
frontier mapping, variant comparison, parallelism effects, and
calibration — dispatching a wholly new idea-generator task to re-derive one
node of that roadmap (rather than a cheaper "elaborate/refine `a915ea`"
step, or a `/design-experiment` step directly on the existing sketch) is a
legitimate resource-allocation question for the Coordinator to weigh,
independent of this task's content quality. Flagged per the task's own
framing: this is a legitimate concern to raise even though reconciling it
is not this task's job.
