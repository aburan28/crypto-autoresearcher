# Proposal: Argon2 memory-access DAG structure at RFC 9106 recommended parameters

- task: TASK-20260809-4e04eb
- role: idea-generator
- goal: GOAL-ARGON-001
- question: RQ-ARGON-141710
- date: 2026-08-09
- claim tier: **structural / graph-theoretic prediction only.** No claim in this
  document is a security verdict, a cost measurement of any attack, or a
  parameter recommendation/deprecation. All inputs referenced or implied are
  synthetic (arbitrary, non-secret password/salt/associated-data bytes chosen
  in-run); no real password, credential, leaked corpus, or third-party dataset
  is named or assumed anywhere below.

---

## 0. RFC 9106 source-access outcome (read first — this bounds everything below)

**Outcome: RFC 9106 could NOT be obtained in this session.** Every fetch/search
route available to this task failed with the identical infrastructure error
(`There's an issue with the selected model (us.anthropic.claude-haiku-4-5-20251001-v1:0).
It may not exist or you may not have access to it.`), which is the backend
model the `WebFetch`/`WebSearch` tools route through for page summarization —
not a research finding, and not evidence about Argon2 or RFC 9106 in any
direction (AGENTS.md rule 3: infra failures are never mathematical evidence).

Routes tried, in order, all in this session (2026-08-09):

1. `WebFetch https://www.rfc-editor.org/rfc/rfc9106.txt` — failed, same model error.
2. `WebFetch https://www.rfc-editor.org/rfc/rfc9106.html` — failed, same model error.
3. `WebSearch "RFC 9106 Argon2 indexing function data-independent data-dependent recommended parameters"` — failed, same model error.
4. `WebFetch https://datatracker.ietf.org/doc/html/rfc9106` — failed, same model error.
5. `WebSearch "RFC 9106 Argon2 recommended parameters memory iterations"` — failed, same model error.
6. `WebFetch https://www.rfc-editor.org/rfc/rfc9106` — failed, same model error.
7. Local-copy search: `Grep` for `RFC 9106|rfc9106` across the repository found only
   this program's own ledger/coordination records *referencing* RFC 9106 (as a
   citation target), never the RFC's own text. `Glob` for `*rgon2*` found only
   `kb/.venv/.../cryptography/hazmat/primitives/kdf/argon2.py` (a Python KDF
   wrapper binding, not the RFC and not a reference implementation of the
   indexing functions). No local/offline copy of RFC 9106 exists in this
   worktree.

No computer-use/browser tool was available in this task's actual tool set (the
system-level MCP instructions describing `computer-use`/`claude-in-chrome`
tools are not bound to any callable function in this session's tool list).

**Consequence, applied strictly per this task's named duty:** nothing below is
presented as read from RFC 9106. Every algorithm-level detail this proposal
relies on is explicitly labeled `RECALLED, UNVERIFIED` and is treated as a
premise to be confirmed — not a fact already confirmed — before any future
`/design-experiment` step executes the sketched measurement. Where the exact
numeric recommended `(t, m, p)` table entries would be needed, this proposal
uses symbolic `(t, m, p)` / per-lane `(t, q)` instead of asserting specific
recalled numbers, and states explicitly which parts of the hypothesis do and
do not depend on the exact recommended values once read.

This is exactly the situation GOAL-ARGON-001's own `pause_conditions` names
("RFC 9106 ... cannot be obtained in primary text after the declared
source-preference order is exhausted") — logged here for the Coordinator's
downstream batch triage, not acted on by this task (idea-generator has no
authority to pause a goal).

---

## 1. Dedup check (before proposing anything as new)

**Checked:**

- `knowledge/INDEX.md` — grepped (case-insensitive) for
  `Argon2|memory-hard|depth-robust|pebbling|Alwen|Blocki|scrypt|Percival`.
  Eight matching rows exist, all `literature`/`reported`/`read` status:
  `KN-LIT-3385` ("Depth-Robust Graphs and Their Cumulative Memory
  Complexity"), `KN-LIT-4894` ("Memory-Hard Functions from Cryptographic
  Primitives"), `KN-LIT-494` ("Balloon Hashing"), `KN-LIT-5442` ("On the
  Complexity of Scrypt and Proofs of Space..."), `KN-LIT-6385` ("Scrypt is
  Maximally Memory-Hard"), `KN-LIT-6793` ("Static-Memory-Hard Functions..."),
  `KN-LIT-7033` ("The Parallel Reversible Pebbling Game..."), `KN-LIT-7247`
  ("Tradeoff Cryptanalysis of Memory-Hard Functions").
- `knowledge/literature/` — grepped the same pattern directly against the 27
  files matched by filename/content; read `KN-LIT-7247.md` and `KN-LIT-3385.md`
  in full (both bulk-seeded 2026-07-24, `citation_verified: read` but flagged
  internally as heuristically parsed / not independently verified past the
  abstract or, for `KN-LIT-3385`, past the title — no abstract was extracted
  for that record at all). `KN-LIT-7247` (Biryukov–Khovratovich, "Tradeoff
  Cryptanalysis of Memory-Hard Functions") analyzes Catena, yescrypt, and
  Lyra2 by its own recorded abstract — **not Argon2** — and is the closest
  corpus record to this goal's attack-side question (RQ's "tradeoff attack"),
  not to this task's graph-structure-only question. `KN-LIT-3385`'s title
  ("Depth-Robust Graphs and Their Cumulative Memory Complexity") is exactly
  the shape of reference this task's mechanism would want, but the record
  carries **no verified authors, year, or abstract** — I cannot confirm it is
  the Alwen–Blocki–Pietrzak line of work my mechanism below recalls, and I do
  not cite its content as read. No corpus record specifically targets Argon2's
  own indexing-function-induced DAG.
  - **Grep found no `Argon2`-naming file content** anywhere under
    `knowledge/literature/` except one incidental mention inside
    `KN-LIT-6385.md` ("an inspiration for Argon2d, one of the winners of the
    recent password-hashing competition") — a passing remark in a scrypt
    record, not an Argon2-focused entry.
- `ledger/proposals/` — grepped for `Argon2`; found five same-day proposals
  already filed under this same `RQ-ARGON-141710` from an earlier session/batch:
  `IDEA-20260809-a915ea`, `-ac98b5`, `-b17238`, `-b9e9cc`, `-c059a7`. Read all
  five in full. **`IDEA-20260809-a915ea` states almost exactly this task's
  target hypothesis in sketch form** ("the memory-access DAG ... measure its
  depth-robustness directly instead of bounding it asymptotically"), but its
  own `source_refs` field says `RFC 9106 -- REQUIRED READ, NOT YET READ` and
  its `novelty_screen` says `WEB NOT CHECKED` — i.e., it is an unsourced draft,
  not a completed, RFC-grounded proposal. This task's deliverable therefore
  supersedes `a915ea` **in content depth** (explicit mechanism, quantitative
  prediction, null-object control, falsification thresholds) but is written
  entirely inside this task's write scope, per this task's constraints, and
  makes no ledger edit — reconciling the two records is left to the
  Coordinator's downstream archive/ledger tasks.
  - Note for the record: `a915ea`'s `dominated_by` field asserts "no
    memory-hard-function records exist in the corpus" — **that claim is false**
    per the `knowledge/INDEX.md` grep above (eight matching rows exist). Flagged
    here rather than silently repeated.
- **Not checked (declared, not silently skipped):** live web literature search
  for Alwen–Blocki / Alwen–Blocki–Pietrzak primary sources — attempted via
  `WebSearch` above and failed with the same infra error. `novelty_status`
  below is therefore `unverified`, per this program's rule that an unchecked
  web literature pass forces that label regardless of corpus-check depth.

---

## 2. Object-first framing (`docs/inventor-protocol.md` §§1–2)

**Established family, named and set aside as the primary lens for this
session:** the published Argon2/scrypt/Balloon-family tradeoff and
ranking-tradeoff attacks (Biryukov–Khovratovich-style, `KN-LIT-7247`) and the
depth-robust-graph asymptotic theory these attacks argue against. This task
does not propose a new attack variant in that family — it proposes measuring
the object those attacks and that theory both make claims about, directly.

**Tracked object (primary, coarse projection):** the memory-access **DAG
topology** — which block indices have a directed dependency edge to which
other block indices — projected out of the full computational state (the
1&nbsp;KiB block *contents* produced by Argon2's compression function `G`,
and by extension any password/salt/secret material feeding those contents).

**Lossy-projection test, applied before proposing the experiment
(`docs/inventor-protocol.md` §2):**

- *Is it lossy?* Yes, substantially: it discards all 1 KiB of hash content per
  block, retaining only a pair of integers per block (its trivial
  same-lane-predecessor index, and its resolved reference-block index).
- *Is what is discarded, discarded compatibly with the operations the target
  quantity depends on?* Yes for the quantity this proposal predicts. Depth,
  longest-path length, reachability under node removal, and any
  eps-depth-reducing-set size are **purely topological** — none of the
  standard depth-robustness definitions this literature uses reference block
  *content*, only the edge relation. So the retained part (the edge set)
  propagates deterministically through exactly the operations
  (`depth-reducing-set`, `longest path after removal`) this proposal's
  prediction is stated over. This is why building this graph is not "sketching
  an attack": an attack needs the content (to actually recompute/forge a hash);
  this measurement explicitly never needs it.
- *Is this a genuine new object or a change of coordinates?* It is the object
  the goal's own `next_action` already names ("the memory-access DAG ... is
  fully determined and finite ... the quantity every tradeoff bound is a
  statement about"), not a novel invention of this task — the contribution
  here is not the object choice but the **specific null-controlled,
  falsifiable comparison** built on it (§4).

**Secondary tracked object (for the specific mechanism below):** the marginal
**reference back-distance** ℓ(j) = (candidate-window size at position j) −
(resolved offset within that window), i.e., "how many blocks back, relative to
the largest possible back-reference at that point, does this block's
long-range dependency edge reach." This is a further lossy projection of the
edge set itself (it discards *which* earlier block is targeted, keeping only
*how far back*). It is compatible with the comparison this proposal runs
because the null model (§4) is built to match window sizes exactly, so any
difference in the *back-distance distribution* between the real graph and the
null is attributable to the *within-window selection rule*, not to a trivial
window-size artifact (see Confounders, §7).

---

## 3. What is RECALLED vs. what would need RFC 9106 to confirm

Stated as a ledger so a reader can see exactly which parts of the mechanism
below are load-bearing recollection and which are symbolic/parameter-agnostic.

| # | Claim relied on | Status | Confidence (self-assessed) | What RFC 9106 read would settle |
|---|---|---|---|---|
| C1 | Each Argon2 block `B[i][j]` (lane `i`, column `j>0`) has a dependency edge from `B[i][j-1]` (the immediately preceding block in the same lane), forming one linear "trivial chain" per lane, spanning all `t` passes over that lane (`t·q − 1` edges total, `q` = blocks per lane). | RECALLED, UNVERIFIED | high — this is the definitional "fill memory in order" structure of an iterated memory-hard function | Confirms pass-wrap behavior (whether the first block of a lane in pass ≥ 1 chains from that lane's last block of the previous pass) exactly. |
| C2 | Each block `B[i][j]` additionally has exactly one "reference" dependency edge to an earlier-computed block `B[l][z]`, chosen by an indexing function specific to the variant. | RECALLED, UNVERIFIED | high | Exact candidate-window definition (segment/lane restrictions, which blocks are eligible at each point). |
| C3 | Argon2i's indexing is **data-independent**: `(l, z)` are derived from a pseudorandom stream generated by `G` applied to counter/position inputs that do not depend on password or salt content in a way that changes the *access pattern* (only the resulting *values* depend on secret content). | RECALLED, UNVERIFIED | high (this is the entire documented rationale for Argon2i's side-channel resistance, referenced even in this goal's own `scheme_context`) | Exact generation mechanism (block-of-128 pregeneration, refresh cadence). |
| C4 | Argon2d's indexing is **data-dependent**: `(l, z)` are derived from bytes of the *content* of `B[i][j-1]` itself. | RECALLED, UNVERIFIED | high | Exact byte offsets / word extraction. |
| C5 | Argon2id splits passes: some early portion (recalled as roughly "the first half of the first pass") uses Argon2i-style indexing, the remainder uses Argon2d-style. | RECALLED, UNVERIFIED | medium | Exact split point — this task does not depend on the exact split point (see §5 scope). |
| C6 | The within-window offset `z` is **not drawn uniformly** from the candidate window; it is produced by a monotone transform of a uniform 32-bit value that concentrates probability toward small offsets (i.e., toward *recent* candidate blocks). | RECALLED, UNVERIFIED | **medium-low — this is the single most load-bearing and least certain recalled detail; the mechanism below is written so its falsification, not just its confirmation, is a full, informative test outcome** | The exact transform (I recall something of the shape `z = (W−1) − W·J1²/2³²` but do **not** assert this formula here as fact — it is exactly the kind of detail this task's own instructions forbid reconstructing from memory and presenting as read). |
| C7 | The recommended parameter table (RFC 9106 §4) lists specific `(t, m, p)` tuples for Argon2id (and alternates for Argon2i/Argon2d) that a deployment is meant to choose from. | RECALLED, UNVERIFIED — **no numeric values are asserted anywhere in this document** | n/a | Exact table entries — required before any measurement claims a specific point is "the recommended parameter set." |

Only C1–C2 are load-bearing for the *coarse* tracked object (§2); C3–C6 are
load-bearing for the specific mechanism in §4; C6 is explicitly the premise
under test, not an assumed fact (see the two-tier falsification design below).

---

## 4. The hypothesis

**Title:** Recency-biased reference selection collapses per-lane
depth-robustness relative to a window-matched uniform-reference null, at a
scale visible already at RFC-recommended lane lengths.

**Mechanism (causal chain):**

1. (C1) Every lane is, independent of any reference edges, a single linear
   chain of length `t·q − 1`. This chain alone lower-bounds the graph's depth
   at `t·q − 1` and is *unaffected* by removing any node that is not itself a
   chain node — so no removal set can shorten this chain except by removing
   chain nodes (i.e., ordinary blocks) themselves, or by removing nodes such
   that no reference edge can "bridge" across the resulting gap and restore an
   equivalently long alternate path.
2. Whether a removal set of nodes shatters the chain into short pieces (small
   post-removal depth) or leaves it substantially bridged (large post-removal
   depth) is governed by how *far back* the surviving reference edges reach
   relative to the size of the gaps created — this is precisely the classical
   depth-robust-graph mechanism (a chain plus edges spanning many distinct
   scales resists node deletion; a chain plus edges that only span short,
   locally-concentrated distances does not).
3. (C6, under test) If Argon2's within-window offset selection is recency
   biased as recalled, the *typical* bridging distance available at any point
   in the lane is short relative to the window size `W(j)`, so a removal set
   that deletes nodes at intervals slightly larger than that typical bridging
   distance should sever most bridging routes with a removal set far sparser
   than what a graph with reference edges spread more evenly across the full
   window (up to `W(j)`) would require.

**Quantitative prediction.** Fix a single lane (`p`-generalization deferred,
see §5) at an RFC-9106-recommended `(t, q)` pair (`q` read from the table once
obtained; symbolic here). Build:

- **Real graph** `G_real`: the actual Argon2 per-lane topology — chain edges
  (C1) plus reference edges resolved by running the actual specified indexing
  function (C2–C6) against synthetic, arbitrary (non-secret) seed material.
- **Null graph** `G_unif`: identical chain edges and identical per-position
  candidate-window size `W(j)`, but each reference edge's target `z` drawn
  i.i.d. **uniformly** from `[0, W(j))` instead of via Argon2's specified
  transform.

For each, compute `S*`, the node-removal set returned by a declared greedy
heuristic (§6) that hits every root-to-current longest path until the
remaining graph's longest path is ≤ 50% of the native `t·q − 1` depth. Report
`ρ = |S*_real| / |S*_unif|` (both as a fraction of `q`, so `ρ` is
scale-free).

- **Prediction, if the mechanism holds:** `ρ ≤ 0.5` at every tested
  RFC-recommended `(t, q)` pair — the real, specification-driven graph needs
  at most half as many node removals (as a fraction of lane length) to halve
  its depth as the uniform-reference null does.
- **This is a genuine two-outcome discriminator, not a foregone conclusion:**
  it is equally possible that `ρ ≈ 1` (recency bias, even if C6 is confirmed
  to exist, is too weak at RFC-scale `q` to matter for this coarse a depth
  target — a real, informative, and different finding), or that `ρ` lands
  between the two (a real but smaller-than-predicted effect).

**Falsification criterion:** the hypothesis, as a *material-effect* claim, is
**falsified** if `ρ ≥ 0.8` at any tested recommended `(t, q)` pair (indicating
the bias, whatever its magnitude, does not materially change per-lane depth
robustness against this specific coarse 50%-depth target at deployed scale).
A measured `ρ` in `[0.5, 0.8)` is a *partial* effect — reported as such, not
rounded into either bucket.

**Precondition falsification (checked first, and separately reportable):**
before the `ρ` comparison is meaningful at all, C6 itself must be checked —
compute the empirical distribution of `z` values (window-relative offset)
actually produced by the real indexing function over many synthetic
draws, and run a goodness-of-fit test (e.g. Kolmogorov–Smirnov) against
`Uniform[0, W(j))`. **If this test does not reject uniformity** (e.g.
`p > 0.05` at a sample size large enough to detect a practically meaningful
departure), C6 as recalled is itself falsified — the reference-selection
transform is not recency-biased in the recalled sense, the entire mechanism
in this proposal has no supporting premise, and the `ρ` prediction above
should not be interpreted as informative even if numerically it happens to
satisfy the `ρ ≤ 0.5` bucket (a coincidental agreement, not a validated
mechanism). This precondition check is cheap (pure counting, no e-DRS
computation needed) and should run before any greedy-heuristic compute is
spent, in the same spirit as `docs/inventor-protocol.md` §3's "structural
tell" check.

**Secondary control (structural-tell, `docs/inventor-protocol.md` §3.1):**
sweep `q` (lane length) at fixed `t` across at least three RFC-adjacent
scales feasible for exact/near-exact computation, and check that `ρ` does not
*increase* with `q`. Depth-robust-graph theory's standard guarantees are
stated as constant *fractions* (Θ(L) removal size for a target depth
fraction), so `ρ` trending toward 1 or staying flat as `q` grows is expected
behavior either way; `ρ` trending sharply *toward 0* as `q` grows (the
biased graph becoming *relatively* easier to shatter at larger scale) would
be the kind of "excess that doesn't decay" signature this program treats as
grounds to suspect the measurement (greedy heuristic degrading differentially,
implementation divergence from spec) before it is reported as a scaling
finding.

---

## 5. Scope limits

- **Single-lane slice only.** This proposal's minimal test (§6) is scoped to
  `p = 1` (or, for `p > 1`, the induced subgraph restricted to intra-lane
  reference edges only, discarding cross-lane reference edges). Real Argon2
  with `p > 1` has cross-lane reference edges that can only *add* bridging
  routes, never remove them, so this is a conservative (worst-case-for-the-
  defender-graph, best-case-for-finding-an-effect) simplification, not a
  claim about the full multi-lane graph. Extending to true multi-lane
  topology is explicitly named as follow-on work, not claimed here.
- **Greedy heuristic gives an upper bound on the true minimum eps-depth-
  reducing-set size, never an exact minimum**, except at scales small enough
  for exhaustive/ILP cross-check (§6, §7). Any reported `ρ` at RFC-recommended
  scale is a ratio of two upper bounds, not of two exact values, and is
  reported as such.
- **No claim about attack cost, wall-clock time, or memory in any adversary
  model.** `ρ` is a dimensionless topological ratio between two graphs; it
  feeds a later tradeoff-attack-cost measurement (a separate, later record per
  this goal's own lifecycle) but is not that measurement.
- **No claim that any recommended parameter set is unsafe**, and no
  recommendation or deprecation of any parameter set, per this goal's
  explicit prohibition.
- **Every numeric detail attributed to RFC 9106 in §3–4 is a placeholder
  pending primary-source confirmation**; this proposal is not admissible as a
  "read RFC 9106" step for any future record in this goal.

---

## 6. Sketched minimal graph measurement (NOT frozen — a sketch only)

This is explicitly *not* an `EXP-*` contract. It sketches what a future
`/design-experiment` step would need to freeze, once RFC 9106 is obtained.

1. **Obtain RFC 9106 primary text** (retry the routes in §0, or use a
   locally-provisioned copy) and extract, verbatim: the exact indexing
   function pseudocode for Argon2i/Argon2d/Argon2id (settles C2–C6) and the
   recommended parameter table (settles C7). This step is a hard precondition,
   not optional — it is exactly this task's forbidden shortcut to skip it.
2. **Implement the topology-only builder**: given `(t, q)` and a variant, walk
   the specified processing order and record, for each `j`, the pair
   `(j−1, z_j)` — the two dependency-edge targets. For Argon2d/id this
   requires actually evaluating the real compression function `G` on
   synthetic, arbitrary, non-secret seed bytes generated fresh in-run (per
   this goal's synthetic-input constraint); for Argon2i it requires only the
   counter-driven pseudorandom stream, no password/salt-derived content at
   all. **No attack is implemented** — this is literally running the
   specification's addressing computation, nothing more, matching the goal's
   own next_action framing.
3. **Precondition check**: collect the empirical distribution of `z_j /
   W(j)` over a declared sample size (start at the largest `q` for which this
   is cheap, e.g. `q` in the low thousands, before attempting RFC-scale `q`);
   KS-test against `Uniform[0,1)`. Report the test statistic and p-value.
4. **Build the matched null** `G_unif` for the same `(t, q)`: identical chain
   edges, identical `W(j)`, uniform `z_j`.
5. **Greedy eps-depth-reducing-set heuristic** (named, standard, no tuning):
   topologically compute each node's longest-path-ending-here value via
   dynamic programming; while current longest path exceeds the 50% target,
   remove one node lying on (some) current longest path — e.g., the node
   closest to the path's midpoint, a standard choice that avoids
   systematically favoring either graph — and recompute. Record `|S*|` and the
   exact/approximate flag.
6. **Cross-check at small scale**: at the smallest `q` where an
   exhaustive or ILP-based exact minimum eps-depth-reducing-set computation is
   tractable, compare the greedy `|S*|` to the exact minimum for both `G_real`
   and `G_unif`, to bound how much of any measured `ρ` deviation from 1 could
   be a greedy-approximation artifact rather than a true topological
   difference (`docs/inventor-protocol.md` §6, validation-ladder step 1).
7. **Scale sweep**: repeat at 3+ values of `q` (validation-ladder step 2,
   §4's structural-tell control) before attempting the literal RFC-recommended
   `q`, which may be large enough to need a more efficient depth-tracking data
   structure than the naive `O(q)`-per-removal DP restated in step 5 — this
   task does not commit to that engineering; it is named as a cost risk for
   whoever designs the frozen experiment.
8. Report `ρ` per tested `(t, q)`, the KS precondition-check result, the
   small-scale exact-vs-greedy cross-check, and the scale-sweep trend —
   exactly, not exact-and-approximate values blurred together.

**Budget shape for a future frozen version** (rough order of magnitude, not a
commitment): step 2–5 at `q ~ 10^3`–`10^4` is minutes of single-machine
compute; step 7's sweep is a small constant multiple of that; the literal
RFC-recommended `q` (unknown numeric value pending §0) could be orders of
magnitude larger and may require the frozen experiment to either subsample
or engineer a faster incremental depth-DP — flagged, not solved, here.

---

## 7. Controls and confounders

**Controls (already built into §4's design):**

- Null-object control: `G_unif`, matched skeleton, uniform selection
  (`docs/inventor-protocol.md` §3.2).
- Structural-tell control: `ρ` vs. `q` scaling behavior (§4, secondary
  control).
- Precondition control: KS test on `z_j/W(j)` before trusting any `ρ` reading
  (§4).
- Cross-check control: greedy vs. exact/ILP at small scale (§6 step 6).

**Confounders:**

- **Window-size boundary effect.** Early-lane blocks have small `W(j)`
  regardless of any selection bias — this is a trivial consequence of "there
  isn't much to reference yet," not evidence of recency bias. Neutralized by
  construction: `G_unif` uses the *same* `W(j)` at every position, so any
  measured `ρ` deviation from 1 is attributable to the *within-window*
  selection rule, not to window-size shrinkage near the start of a lane.
- **Greedy heuristic asymmetry.** The greedy midpoint-removal heuristic could
  behave differently well on locally-clustered (biased) vs. spread-out
  (uniform) graphs for reasons that are an artifact of the heuristic, not of
  true minimum eps-depth-reducing-set size. Addressed only partially by the
  small-scale exact cross-check (§6 step 6) — a persistent, unexplained gap
  between greedy and exact behavior at small scale would require a second,
  structurally different heuristic before any `ρ` claim at RFC scale is
  trusted.
- **Null-model sampling variance.** `G_unif` is itself a single random draw;
  report `ρ` averaged over multiple independent draws of `G_unif` with
  variance stated, not a single-seed point estimate.
- **Wrong-direction recall risk (C6).** If the recalled bias direction is
  simply wrong (Argon2 is uniform, or biased toward *long*-range instead of
  short), the precondition check (§4) catches this directly and is designed
  to be the *first* thing checked, before any e-DRS compute is spent.
- **Per-lane-only scope hides cross-lane bridging** (§5) — a real
  multi-lane graph could show a smaller effect than this single-lane slice
  predicts, precisely because cross-lane references add bridging routes this
  test cannot see. This is a scope limit, not a hidden confounder, and is
  already stated in §5.

---

## 8. Heuristic assumptions (named, numbered)

**H1 — reference-index distribution modeling.** *Formal statement:* the
32-bit pseudorandom value `J1` feeding the reference-index transform (from
`G`'s output, for Argon2i; from the previous block's leading bytes, for
Argon2d) is modeled as drawn from `Uniform[0, 2^32)`. *Rigorous support:* none
proven for a general compression function; this is the standard
random-oracle-style modeling heuristic used throughout this literature
("a cryptographic compression function's output on fresh input is
indistinguishable from uniform to a computationally bounded distinguisher"),
imitating the classical assumption that a PRF/PRG output is
computationally uniform. *Validation route:* evaluate the real `G` function
on `≥ 10^5`–`10^6` synthetic (arbitrary, non-secret) input blocks at small
scale, extract the leading 32 bits, and run a chi-squared/KS goodness-of-fit
test against `Uniform[0, 2^32)` (binned appropriately); report the test
statistic, p-value, and tail behavior (e.g., agreement of the extreme
order statistics with the uniform prediction), directly analogous in
methodology to this program's existing smoothness-heuristic validation
routes (`docs/claims-and-verification.md` heuristic-record template).
Sampled parameters and any transfer assumption from small-scale `G`-calls to
full RFC-scale volumes of calls must be stated explicitly when this is run.

**H2 — marginal-distribution sufficiency (configuration-model
approximation).** *Formal statement:* the eps-depth-reducing-set size of the
graph built from "fixed chain + per-node independently-drawn reference
target" is well-approximated by treating each node's reference target as an
**independent** draw from its own position-dependent back-distance
distribution — i.e., higher-order correlations among different nodes' targets
(e.g., shared pseudorandom-stream structure within an Argon2i slice) do not
materially change eps-depth-reducing-set size relative to what the marginal
distribution alone would predict. *Rigorous support:* none proven for this
specific construction; this imitates the classical **configuration-model**
approximation in random graph theory (Molloy–Reed-style results showing
macroscopic graph properties are well predicted by a graph's degree/edge-length
sequence alone, independent of higher-order correlation structure, away from
small-size effects). *Validation route:* at small `q` (exact/near-exact
e-DRS tractable), compare `e-DRS(G_real)` against `e-DRS` of a graph built by
**independently resampling** each node's reference target from `G_real`'s own
empirical per-position back-distance distribution (not from the assumed
uniform null — a *third*, intermediate control object). Close agreement
validates H2 at that scale and licenses using the marginal-distribution-based
reasoning in §4's mechanism when extrapolating past exactly-computable `q`;
divergence would mean cross-node correlation in the real indexing function
(e.g., shared Argon2i pregeneration blocks) matters and the mechanism in §4
needs a correlation-aware restatement. Record the sampled `q` and flag this
extrapolation explicitly if H2 is relied on beyond exactly-validated scale.

---

## 9. Target-complexity-equivalent (measurement cost, not an algorithmic claim)

This proposal makes no algorithmic-complexity-improvement claim against any
central hard problem (it is a `measurement`-class idea per
`agents/idea-generator.md`'s taxonomy, not an `algorithm`-class one), so
`target_complexity` in the exponent-vs-best-known sense used for ECDLP
proposals does not apply. The honest analogue — cost of the sketched
measurement procedure itself:

- **Real/null graph construction:** `O(q)` time and `O(q)` memory per lane
  per variant (one `G`-evaluation per block for Argon2d/id-style content-
  dependent indexing; pure counter-driven `G`-evaluations for Argon2i-style
  pregeneration; pure RNG draws, no hashing, for the null).
- **Greedy eps-depth-reducing-set heuristic (naive):** `O(q)` per removal
  round for the longest-path DP recomputation, times up to `O(q)` removal
  rounds in the worst case, i.e. `O(q^2)` naive — this is the risk flagged
  in §6 step 7 for literal RFC-scale `q`, not resolved by this proposal.
- **Small-scale exact/ILP cross-check (§6 step 6):** exponential in the
  worst case for exact minimum eps-depth-reducing-set (a known NP-hard-flavored
  combinatorial optimization in general graphs); bounded only by choosing `q`
  small enough for this to be tractable, named explicitly as a scale ceiling
  on the "exact" tier of this measurement, exactly as GOAL-ARGON-001's own
  completion criterion requires ("exactly computed quantities reported as
  exact and bounded quantities reported with the bounding method named").
- **Memory:** all of the above is single-machine, well under the task's
  declared 2 GB budget at the small-to-moderate `q` scales this proposal
  itself is scoped to (§5–§6); literal RFC-recommended `q`, once its numeric
  value is known, may exceed this and would need to be re-budgeted by
  whoever designs the frozen experiment.

---

## 10. Novelty classification

`novelty_status: unverified`

Rationale: the corpus check (§1) is thorough (INDEX + literature grep, five
sibling ledger proposals read in full) and finds no existing record that
performs this specific null-controlled comparison for Argon2. But the live
web-literature check required to distinguish "known result restated" from
"genuinely new operationalization" (specifically: confirming whether
Alwen–Blocki / Alwen–Blocki–Pietrzak already published a numerically
comparable per-lane, null-controlled measurement, which the qualitative
mechanism in §4 is very likely *adjacent to* even if not identical) could not
be completed — every `WebSearch`/`WebFetch` attempt failed (§0). Per this
program's rule, an unchecked web pass forces `unverified` regardless of
corpus-check depth. If forced to classify the qualitative *direction* alone
(data-independent/recency-influenced addressing being weaker than idealized
depth-robust-graph theory assumes) it would likely be `adaptation` — recalled,
unverified, and not asserted as this proposal's own discovery — but the
specific null-controlled, two-tier-falsifiable operationalization in §4 is
what this task contributes, and its novelty against the specific (not yet
locatable) primary sources remains unverified.

---

## 11. Honest accounting (`docs/inventor-protocol.md` §5)

- **Object(s) considered:** (1) primary — the Argon2 memory-access DAG
  topology, projected from full block content (§2); (2) secondary — the
  marginal reference back-distance distribution `z_j/W(j)` (§2); (3) the
  window-matched uniform-reference null graph (§4); (4) named but not built —
  a marginal-distribution-resampled (configuration-model) intermediate control
  object for validating H2 (§8).
- **`dominated_by`:** qualitatively, this proposal's direction (Argon2's
  data-dependence/data-independence choice trading off against depth-robustness
  guarantees) is very likely already dominated by published
  Alwen–Blocki-family results — recalled, unverified, not locatable in this
  session (§0, §10) and therefore not citable as a checked row on the
  frontier. `KN-LIT-3385`'s title suggests it may be exactly this line of
  work but its content is unverified in this corpus (§1). I cannot set
  `dominated_by: null` (that would assert I checked every row on the frontier,
  which the RFC/web access failure directly prevents) and I cannot honestly
  assert a name either. **`dominated_by: "unknown — primary literature check
  blocked by infra failure (§0); likely dominated qualitatively by
  Alwen–Blocki-family depth-robustness results, unconfirmed in this
  session."`**
- **`sota_delta`:** no attack, no algorithm proposed. Quantitatively: this
  proposal contributes a specific, falsifiable, null-controlled *test design*
  (the `ρ` ratio, its two-tier falsification thresholds, the KS precondition
  check) that does not yet exist as a filed, sourced record in this program's
  ledger or knowledge corpus (checked, §1) — the delta is "a concrete,
  executable test design where the corpus previously had an unsourced sketch
  (`IDEA-20260809-a915ea`) and adjacent-but-not-Argon2-specific literature
  entries," not a numeric result of any kind.
- **Enumerated closures:** none. Nothing in this task is closed; §0's RFC
  access failure is recorded as a blocker with a named mechanism (backend
  model unavailability) and forward guidance (retry the same routes in a
  later session; obtain a local copy if the tool infra issue persists),
  exactly matching the closure standard's requirement that a blocker name its
  obstruction and what remains open, rather than silently narrowing scope.
- **Open directions for the next session:**
  1. Obtain RFC 9106 primary text (§0) — the hard precondition for everything
     else in this goal, including this proposal's own C2–C7.
  2. If a future session pursues this specific hypothesis: implement §6 steps
     1–4 first (graph construction + KS precondition check) *before* spending
     compute on the greedy heuristic — the precondition check is the cheapest
     possible falsifier and should run first.
  3. Attempt the web-literature check this session could not complete, to
     resolve §10's `novelty_status` and §11's `dominated_by` properly before
     any experiment is frozen.
  4. Reconcile this task's output with the five pre-existing sibling proposals
     under `RQ-ARGON-141710` (§1) — that reconciliation is a Coordinator
     decision, not this task's to make.
