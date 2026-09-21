# Red-team report — `TASK-20260809-83623a`

Task: `TASK-20260809-83623a`  
Goal: `GOAL-SSI-001`  
Batch: `BATCH-4f52ab`  
Role: independent Red Team  
Requested policy: `review-adversarial` with `xhigh` reasoning  

## Verdict

**`CONCUR_WITH_CAVEAT` for the design-only review boundary; not execution-ready.**

The schema repair, snapshot binding, additive predecessor-to-successor registry
entry, and explicit no-execution boundary survive the provenance attack. The
candidate also states an appropriately narrow ceiling: it is a derivation about
a named closed list and its accounting conventions, not a result about all
advice strings.

The scientific/accounting design does not survive as a fully specified
execution contract without further clarification. The main unresolved points
are the quantifier used for the per-prime advice frontier, the random-walk
hitting assumption for arbitrary advice sets, the exact matched-null data
construction, the pair-distribution assumption behind Construction C, the
observation-collision claim for Construction B, and the undefined nearby
oriented/CSIDH control. These are review blockers for any later Stage 0/1
authorization, not mathematical negative evidence. No experiment, Stage 0,
Stage 1, attack, security analysis, exponent conclusion, hypothesis
transition, or goal-completion conclusion was made here.

## Claim under review and boundary

The reviewed object is the snapshot-bound corrected contract
`EXP-SSI-2d8583`, sourced from `IDEA-20260806-9c2f80`, for a classical,
per-prime OneEnd advice-frontier accounting exercise. The successor explicitly
remains `review_required`, unfrozen, execution-unauthorized, and
evidence-ineligible, and it says that the output is not an attack, an
all-advice lower bound, or a security result (`experiments/EXP-SSI-2d8583/specification.yaml:1-36`).

This review therefore assesses only:

- whether the changed advice quantifier is stated coherently;
- whether the named Construction A/B/C rows and their cost axes are actually
  pinned well enough to review;
- whether the proof-map audits and controls distinguish the stated closed list
  from a global method ceiling;
- whether the random-advice and nearby-object controls are executable as
  controls rather than assertions;
- whether the schema-supersession and snapshot provenance are intact; and
- whether the claim boundary prevents accidental promotion.

No numeric row was executed or independently validated. In particular, the
pre-registered `T_min` expression is treated as an input to attack, not as a
finding.

## Independence and reviewed inputs

This was a separate native Codex review session in
`/Volumes/SSD990/crypto-autoresearcher/.worktrees/ssi-cost-source-20260809`.
I read `AGENTS.md`, `agents/red-team.md`, the task-lifecycle and dispatch
contracts, the BATCH-4f52ab manifest and queue, the retry capsule, the
snapshot receipt, `EXP-SSI-2d8583`, its immutable predecessor, the selected
proposal, the schema registry, the prior Validator report named by the
capsule, and the current S1/S2/Q3 catalogue files. The queue spells the
catalogue directory `catalogue-20260806-mlkem-aes-ssi-ssiq`, but that directory
does not exist. The committed files are under
`catalogue-20260806-mlkem-aes-ssi-ssqi`; I read those actual files and record
the path discrepancy below rather than claiming that the literal queue paths
were readable.

The read-only harness preflight reported current generated bindings and role
bindings, but the harness doctor found no configured usable API backend. No
Bedrock provider, endpoint, or model was selected. This is recorded in the
runtime receipt as unverified native-session provenance; it is not treated as
evidence about the candidate.

## Snapshot and provenance checks

The immutable boundary itself is sound:

- `329eef133c5a84605469af92c692fa8c010df7df` is reachable from the review
  `HEAD` `73097851a116144a46a6d56b1e0c636257320329` and has the declared parent
  `7c65f5f6959cfa7b133fa58344de4d4c87ffded8`.
- The snapshot commit changes exactly the declared snapshot receipt, retry
  capsule, and registry paths. The queue-bind commit changes only the
  dispatch plan, dispatch report, and dispatch queue.
- The queue-bound SHA-256 values match the current committed bytes:
  `snapshot-receipt.json` begins with
  `8b5623c2faf8397e092827999cf7b987ddcace7c49d5e6f76fc6854fa2dad5e8`, the
  capsule with
  `c0cff2d41bfbd2216767cfa5f12f1de8c7358ee5a692384dd371d46d9b9c8271`, and
  the registry with
  `f6d91ab9badb6041fa9180d714aab4b9b5833261566da44a0e036e028f8a87cf`.
- The capsule's predecessor and successor hashes match the live files:
  `EXP-SSI-a6132d` has SHA-256
  `531b0a647a3354c7a303d47c5c97923fafeff8a819df6257e4c1e7f5f1405d4e`, and
  `EXP-SSI-2d8583` has SHA-256
  `d36a9cd14e4dc450f282118d6243d925fe8dd589fbdd16949183252aa2df27b7`.
- The predecessor blob is identical at the snapshot commit and its parent
  (`7e25d0e0a320f1a705a58d932bb7d66fd7278748`), so the repair is additive.
- The registry entry is present in the snapshot and routes the predecessor to
  `EXP-SSI-2d8583` with the same two pinned hashes
  (`tools/schema_supersession_registry.yaml:507-514`).

The snapshot receipt retains `commit_sha: null` and
`verification.status: pending_post_commit`, while the queue carries the
post-commit SHA and path hashes. That is a coherent queue/Git binding, but the
receipt is not self-contained proof of post-commit verification. Any later
archive should preserve the queue/Git verification rather than describing the
receipt's null fields as an independently complete receipt.

The successor specification retains `batch_id: BATCH-75287c`, while the
review retry is `BATCH-4f52ab` (`experiments/EXP-SSI-2d8583/specification.yaml:13-22`).
This is acceptable as experiment lineage only if the Coordinator records that
the current batch is retrying a review gate for an experiment authored in the
predecessor batch. A later synthesis must not silently relabel the experiment
as authored by BATCH-4f52ab.

## Findings

### RT-1 — The stated `forall E` frontier is stronger than the hitting-time validation

The proof map states the intended quantifier as a fixed, prime-dependent advice
string followed by a query that works for every supersingular `E`
(`experiments/EXP-SSI-2d8583/specification.yaml:63-66`). Construction A then
prices a random walk by the density of a stored set
(`ledger/proposals/IDEA-20260806-9c2f80.yaml:164-179`). This leaves three
unfixed choices:

1. Is `T(S)` a worst-case expected query cost over every starting `E`, an
   average over `E`, or a high-probability bound over both `E` and the advice
   generation?
2. Is the advice set fixed before the instance and then held fixed, or is the
   expectation also over regenerating the advice set?
3. What success probability, restart policy, mixing burn-in, and pullback cost
   are included in one query?

The proposal's H-ADV-1 validation plan samples random target sets and compares
their hitting-time distribution with a geometric law at toy primes. That does
not test the universal advice-set quantifier. A set of the same density can be
clustered or otherwise arranged differently from a random set, and a spectral
gap statement alone does not identify a geometric hitting law with absolute
constants for every fixed set and every starting vertex. The control is
therefore currently a random-set sanity check, not a validation of the
quantifier written in the proof map.

This is not a rejection of either model. It is a required choice of model:
either define a worst-case-over-`E`, fixed-advice expected cost and supply the
corresponding mixing/hitting assumption, or weaken the quantifier to the
distribution actually tested. The report must not silently move between them.

### RT-2 — H-ADV-1 is load-bearing but the successor contract does not carry its exact status

The successor correctly says that the future derivation cannot validate H-ADV-1
(`experiments/EXP-SSI-2d8583/specification.yaml:33-36`), but Construction A's
query row still relies on a random-walk hit model. The proposal names H-ADV-1
and gives it toy validation, but its statement covers all sufficiently large
primes and all sufficiently dense subsets, whereas its proposed test covers
only a small-prime graph and random subsets. The future artifact therefore
needs to label the A row explicitly as conditional on H-ADV-1 and report the
tested random-set scope separately. A symbolic row can be emitted under that
assumption; it cannot be called a validation of the assumption.

The same separation is needed for H-ADV-2, which the proposal itself calls an
unverified order-to-curve direction, and H-ADV-3, which it calls its
load-bearing, unproved fiber conjecture (`ledger/proposals/IDEA-20260806-9c2f80.yaml:644-690`).
The current claim ceiling is honest about this; the danger is only that a later
table or synthesis drops the qualifiers.

### RT-3 — The A/B observation collision is contingent on an unpinned data layout

The proof map records Construction A at the same observable `(S,T)` as
Construction B and declares that B's curves already carry orders
(`experiments/EXP-SSI-2d8583.specification.yaml:53-62`). The proposal's B
description, however, begins with a stored set `G_theta` of curves satisfying
a small-`delta` predicate and then charges a terminal procedure at the landed
curve (`ledger/proposals/IDEA-20260806-9c2f80.yaml:181-197`). Two materially
different implementations fit that prose:

- advice contains each curve plus its endomorphism order; the terminal step is
  effectively the database lookup of A; or
- advice contains only the curve identifier/membership information, and the
  terminal small-`delta` procedure is performed after a hit.

The two branches have the same displayed observable at the named collision but
different forgotten structure and different build/query charges. The current
collision note assumes the first branch without pinning the advice bytes,
order representation, or lookup contract. This is exactly the observation-
fiber attack: hold `(S,T)` fixed and vary the omitted content. The collision
does not by itself prove mechanism equivalence.

Required repair: split B into an order-tagged branch and a membership-only
branch, or state and hash-commit one precise representation. If the latter
branch is retained, its terminal procedure and its construction cost must be
charged separately. The conclusion may still be that the named branch is
redundant, but that conclusion must follow from the pinned branch rather than
from the same `(S,T)` pair.

### RT-4 — Construction C assumes a pair-uniformity statement that is not in the heuristic inventory

Construction C's table-size argument treats the pair consisting of the first
list's codomain and the last list's domain as essentially uniform in a
two-dimensional curve-pair universe (`ledger/proposals/IDEA-20260806-9c2f80.yaml:199-224`).
That is stronger and different from H-ADV-1's single-set hitting statement.
It requires a declared distribution/independence claim for the pair generated
by the two instance-dependent balls, including the effect of the middle
factor, path orientation, and correlations between the two endpoints.

The proof-map obligation names the table-size formula, but the successor
contract does not number or state the pair-distribution assumption. Static
arithmetic can verify the formula after that assumption is supplied; it cannot
establish the assumption. The C-dominance row must remain conditional until
the pair law is either proved for the stated model or explicitly registered as
a heuristic with a matching null and falsification boundary.

### RT-5 — The fiber metric does not yet define the set whose size is charged

The proposal defines `R(a)` as the set of curves resolved by one advice element
and then includes curves reachable by a walked path
(`ledger/proposals/IDEA-20260806-9c2f80.yaml:90-109`). The metric is described
as an average fiber ratio, while the method ceiling uses a product of total
advice size and per-query time. To make those quantities comparable, the
contract needs a budgeted definition such as `R_T(a)`, an explicit union over
advice elements, and a rule for overlapping balls and shared table bits.

Without that definition, an averaged per-element fiber can double-count the
same resolved curves, while a compressed p-only data structure can share bits
among many logical elements. The proposed product argument is appropriate for
the named entry-based constructions if those accounting conventions are
fixed; it is not a method ceiling for arbitrary encodings. The proposal
acknowledges this boundary, and the successor correctly limits certification
to a closed list (`experiments/EXP-SSI-2d8583/specification.yaml:67-70`).
The future artifact must retain that limitation and must not present
`fiber_ratio` as a universal lower-bound certificate.

### RT-6 — The matched random-advice null is not fully reproducible in the successor specification

The successor declares `CTRL-RANDOM-ADVICE` before treatment and matches only
the declared size, access model, and query budget
(`experiments/EXP-SSI-2d8583/specification.yaml:77-87`). The proposal gives a
more useful verbal description—random supersingular identifiers with no
endomorphism data—but that exact byte-level construction is not copied into
the successor contract. The following must be frozen before any execution:

- the null object's record encoding and bits/entry;
- whether it is a random set of distinct vertices, a random byte string, or a
  random permutation of a typed advice table;
- the generator and its seed/independence model;
- the identical lookup, walk, restart, and query code path used by treatment;
- the precise meaning of “no endomorphism data attached”; and
- the finite-size tolerance and statistic that distinguish the forced null
  behavior from sampling noise.

Otherwise the null can pass or fail because the code sees a different object
shape, not because content was removed. The shuffled-fiber control has the same
issue: if a permuted order may be reinterpreted as an order for another curve,
the expected negative outcome is not forced by the current description. The
access model must forbid or charge such reinterpretation explicitly.

### RT-7 — The nearby oriented/CSIDH control is a sanity condition, not a reproducible method-ceiling test

The successor requires that an “oriented/CSIDH-shaped” nearby object must not
return the same flat frontier (`experiments/EXP-SSI-2d8583/specification.yaml:67-70,94-96`),
but it does not define the nearby input, output, advice encoding, query
algorithm, quantifier, baseline, or expected alternative frontier. The S2
catalogue explicitly distinguishes the classical per-prime advice model from
quantum coset-state pooling, and Q3 treats CSIDH-style group actions as a
different scope. A nearby object with a different problem type cannot, by
itself, validate a claim about the SSI resolution fiber.

The control can remain as a qualitative sensitivity check, but it cannot be an
exact proof-map gate in its current form. Before execution, either define a
typed nearby problem with a known-answer cost table and the same accounting
axes, or demote this item to a non-gating sanity check. A same-frontier outcome
would then be an instrument/model diagnostic; it would not automatically be a
mathematical refutation of the SSI closed-list accounting.

### RT-8 — Build cost, entry units, deduplication, and physical memory are still undercharged

The proposal calls Construction A's build cost load-bearing and says it costs
roughly one polynomial-time construction per stored curve
(`ledger/proposals/IDEA-20260806-9c2f80.yaml:164-176`). The successor metrics
still primarily expose advice entries and per-instance query time
(`experiments/EXP-SSI-2d8583/specification.yaml:97-108`). A complete accounting
needs, at minimum:

- a separate build/preprocessing function, including failed samples and
  duplicate rejection;
- a definition of whether `S` counts curves, order records, bytes, or logical
  entries with shared storage;
- the representation size of a j-invariant, an order, a path, and an index;
- the working memory and time of the query separately from advice lookup;
- the amortized instance count at which build cost is recovered; and
- a declared byte-to-entry conversion for the physical-memory comparison.

The random maximal-order sampler does not automatically produce `S` distinct
uniform vertices, especially near the finite graph's saturation regime. That
does not invalidate a symbolic density row, but it makes the build and finite-
size interpretation incomplete. The `S=p` known-answer corner is a separately
declared control and must not be used as evidence that the random construction
can enumerate the full vertex set at the same charge.

There is also no explicit mapping from Construction B's theta parameter to all
seven sigma grid points. Its declared size law is a threshold-parameterized
curve and must state how it is evaluated below the minimum threshold, how
duplicate/saturation effects are handled, and whether unused advice slots are
padded. Without that mapping, “every closed-list row at every sigma” is not a
fully determined output requirement.

Finally, the successor says to use exact rational arithmetic, while the sigma
values are written as finite decimal approximations
(`experiments/EXP-SSI-2d8583/specification.yaml:45-52`). The implementation
must bind each displayed value to an exact rational label (for example,
declared `1/6`, `1/3`, and `2/3`) rather than silently treating the decimals as
the mathematical parameters.

### RT-9 — The resolution-fiber closure needs an explicit output-type check

The candidate says that a walked isogeny and a known order at the landed curve
can be pushed/saturated to obtain an order at the original curve. The tracked
fiber, however, is defined as resolving a non-scalar endomorphism, not merely
an abstract order (`ledger/proposals/IDEA-20260806-9c2f80.yaml:90-109`). The
contract must state how the pushed order yields an explicit admissible
endomorphism representation for the OneEnd output, what saturation costs, and
whether the path direction and field representation are part of the advice or
the query. Otherwise the closure argument proves a statement about an abstract
ring object while the metric charges a OneEnd witness.

This is a reduction/output-type caveat only. The current scope does not permit
transferring a design row to EndRing, Isogeny, a scheme, or a security
interpretation, and the successor says so (`experiments/EXP-SSI-2d8583/specification.yaml:27-36,149-154`).

### RT-10 — The proposal/specification boundary contains a stale execution instruction

The successor requires standard-library-only Stage 1 arithmetic and explicitly
invalidates numpy, Sage, network access, and isogeny implementation
(`experiments/EXP-SSI-2d8583/specification.yaml:119-148`). The selected proposal's
`compute_budget_note` still says that Stage 1 is “numpy-only”
(`ledger/proposals/IDEA-20260806-9c2f80.yaml:760-768`). The successor is the
corrected experiment contract, so this is not a run violation—no run occurred.
It is nevertheless a future-dispatch hazard. Any executor handoff must state
that the successor specification governs and that the proposal's stale
implementation note is not an authorization or a dependency.

### RT-11 — The dispatch read scope has a literal catalogue-path defect

The queue declares the Red Team read paths with the suffix `ssi-ssiq`
(`coordination/goals/GOAL-SSI-001/batches/BATCH-4f52ab/dispatch_queue.json:94-116`),
but all three committed files are under `ssi-ssqi`. The literal paths are
missing; the corrected paths were found by repository listing and read for
this review. This is a provenance/dispatch defect, not scientific evidence.
The Coordinator should repair the task binding with a new additive queue or
correction record before treating this review as a strict fulfillment of the
declared catalogue input set. I did not edit the queue.

## Required controls and repairs before any execution authorization

1. Freeze the advice quantifier and cost convention: fixed `A_p`, worst-case
   or average-case over `E`, expectation over query randomness versus advice
   generation, success probability, restart/mixing cost, path pullback, and
   failure handling.
2. Register H-ADV-1 exactly as used. If the intended scope is arbitrary fixed
   advice sets, add a suitable clustered/adversarial-set control; if the
   intended scope is random advice sets, narrow the quantifier and claim
   ceiling accordingly. Keep the toy validation explicitly toy/design
   support.
3. Split Construction B by data representation or hash-commit one precise
   order-tagged/membership-only format. Re-run the observation-collision audit
   on the chosen representation and charge its build and query path.
4. Add the Construction C pair-distribution assumption, its random-model
   justification, and a nearby null that can falsify pair correlations. Do not
   treat the table-size expression as self-validating arithmetic.
5. Define `R_T(a)`, the union/overlap convention, shared-bit accounting, and
   the exact domain of `fiber_ratio`. Keep H-ADV-3 as a bounded conjecture or
   accounting assumption, never as an all-advice lower bound.
6. Pin the random-advice null byte schema, generator, seed policy, identical
   access/query path, no-content guarantee, and finite-size acceptance rule
   before any treatment row. Apply the same discipline to shuffled orders.
7. Replace the nearby-object sentence with a reproducible typed control, or
   demote it from a gating control. It cannot be used as a proxy proof for the
   SSI object.
8. Add build-cost, byte-level advice, duplicate/saturation, working-memory,
   and physical-memory columns. Give Construction B an explicit mapping to
   the sigma grid and bind the decimal display values to exact rationals.
9. State the explicit OneEnd witness/output conversion in the resolution-fiber
   proof obligation and preserve the no-transfer boundary.
10. Repair the three queue catalogue paths through the Coordinator's additive
    coordination process; do not edit this review's inputs in place.

## Counterexample or mutation proposed (not executed)

The cheapest discriminating mutation is to keep Construction B's `G_theta`
curve identifiers and declared density fixed while stripping all endomorphism
order tags from the advice. Run the same terminal query under the same access
budget in the authorized future protocol. If the accounting changes, the
current A/B collision is a data-layout collision, not a mechanism identity; if
it does not, the query path is likely using an uncharged information channel.
This mutation was not executed, and no result is inferred from it.

A second required static/test-design mutation is to keep `|G|` fixed while
switching from a random target set to a deliberately clustered set and to
report worst-case starting vertices separately from random starts. This is a
control for RT-1/RT-2, not a claim about the graph or a security statement.

## Baseline comparison

The contract declares the no-advice known-answer corner, the full-advice
known-answer corner, and the named S=p^(1/2) balance embedding
(`experiments/EXP-SSI-2d8583/specification.yaml:53-58,77-96`). Those are useful
boundary controls. They were not executed here. The prior proposal also lists
working memory and advice as separate axes and names the incumbent, Delfs–
Galbraith, meet-in-the-middle, and van Oorschot–Wiener rows as comparison
records (`ledger/proposals/IDEA-20260806-9c2f80.yaml:728-758`).

This review does not choose a “closest baseline” for a broader cryptanalytic
claim, because the task is explicitly limited to the closed-list accounting
contract. The current specification still needs to make units commensurable:
field-operation count, query time, advice entries/bits, working memory, and
preprocessing are not interchangeable. The single incumbent memory number
does not by itself define a physical byte model.

## Heuristic, cost, reduction, and scope conclusions

- **Heuristics:** H-ADV-1, H-ADV-2, H-ADV-3, and the Construction C pair law
  remain explicit unresolved assumptions or bounded conjectures. None is
  promoted by this review.
- **Cost model:** the per-query rows can be reviewed symbolically only after
  advice representation, build cost, query units, working memory, and
  amortization are fixed. A build-versus-query caveat present in the proposal
  is not yet a machine-readable cost axis in the successor.
- **Reduction/output:** the walked-order argument needs an explicit conversion
  from a pushed/saturated order to the declared OneEnd witness. No transfer to
  EndRing, Isogeny, a scheme, security, or any broader cryptographic scope is
  admitted.
- **Method ceiling:** the current proof map can at most organize the named
  Construction A/B/C list under declared conventions. It cannot certify all
  p-only advice, compressed/shared advice, or unlisted p-dependent structures.
- **Controls:** S=0, S=p, shuffled-fiber, random-advice, and nearby-object
  outcomes are declarations until their exact data and execution semantics are
  frozen. A forced result in YAML is not a measurement.
- **Provenance:** the schema-supersession repair and snapshot binding pass;
  the queue catalogue path and pending receipt fields remain operational
  caveats to preserve in the archive.

## Narrowest supported statement

At the reviewed `HEAD`, BATCH-4f52ab provides a hash-bound, additive
schema-successor boundary for a design-only Red Team review of
`EXP-SSI-2d8583`. The predecessor remains byte-immutable, the successor is not
authorized to execute, and the contract explicitly limits any future output
to a declared closed-list accounting derivation. The current review finds no
reason to treat the package as an attack, security, exponent, or completion
result. It also finds that the listed quantifier, null, nearby control,
Construction B collision, Construction C distribution, and cost-unit details
must be repaired or explicitly downgraded before any later Coordinator task
authorizes Stage 0/1.

## Next concrete action for the Coordinator

Archive this report with the fresh Validator artifact, preserve the
`CONCUR_WITH_CAVEAT` scope, and keep execution unauthorized. Create an additive
protocol clarification/successor task covering RT-1 through RT-11, including
the corrected catalogue paths, before dispatching any executor. If the
Coordinator elects not to repair those points, the ledger decision should
record that only a conditional, bounded symbolic design review was admitted;
it must not describe the forced controls or pre-registered rows as observed
results.

Artifact paths written by this task:

- `coordination/goals/GOAL-SSI-001/batches/BATCH-4f52ab/reviews/TASK-20260809-83623a/red_team_report.md`
- `coordination/goals/GOAL-SSI-001/batches/BATCH-4f52ab/reviews/TASK-20260809-83623a/runtime-session-receipt.json`
