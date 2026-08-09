# Red-team report — `TASK-20260809-950724`

Task: `TASK-20260809-950724`  
Goal: `GOAL-SSI-001`  
Batch: `BATCH-6c960d`  
Role: independent Red Team  
Requested policy: `review-adversarial` with `xhigh` reasoning  
Reviewed snapshot: `e17eeccdf5870580c9b87fc2a29d66d5ef4dfb72`  
Reviewed queue binding: `840212b06599eed472a8b937aab027b0255d91d9`

```yaml
red_team_report:
  id: RT-20260809-950724
  task_id: TASK-20260809-950724
  claim_under_review: design-only fixed-advice SSI refinement successor
  verdict: CONCUR_WITH_CAVEAT
  objections:
    - RT-6C-1 worst-case expected T_q and builder-seed semantics are not formally defined
    - RT-6C-2 H-ADV-1-R is labelled weaker but H-ADV-1-W lacks a durable formal non-promotion gate
    - RT-6C-3 typed A/B/C records and branch-specific costs remain underdefined
    - RT-6C-4 R_t(A) does not reconcile shared bytes and multi-entry queries
    - RT-6C-5 random-advice null can reject by validity_tag=0 before the treatment path
    - RT-6C-6 shuffled-fiber rejection is forced and needs narrower interpretation
    - RT-6C-7 C-pair null statistic and tolerance are not frozen
    - RT-6C-8 build, deduplication, physical-byte, and Q charges remain templates
    - RT-6C-9 exact prime values and S=0/S=p physical corner semantics are absent
  required_controls:
    - define fixed-advice worst-case expectation, success, restart, and Q break-even
    - freeze exact prime convention and complete per-branch byte schemas
    - replace the type-invalid primary random null with a same-typed null path
    - freeze C-pair generation/statistic/tolerance before treatment
    - define shared-data fiber access and explicit OneEnd output conversion
  counterexample_or_mutation: clustered fixed-density targets; same-typed random payload; order-tag stripping; and uncoupled C endpoint pairs, all not executed
  baseline_comparison: declared S=0 and S=p^(1/2) controls only; no baseline measurement or broader comparison
  heuristic_challenges:
    - H-ADV-1-W and H-ADV-1-R remain distinct and unvalidated
    - H-ADV-2 and H-ADV-3 remain conditional
    - H-ADV-4 remains C-only and conditional
  cost_model_challenges:
    - exact byte widths, build failures, retained entries, physical memory, and Q are not yet quantities
  reduction_and_scope_challenges:
    - output-producing pullback/saturation/witness conversion is deferred
    - closed-list scope cannot become an all-advice or security statement
  proof_architecture_challenges:
    - quantifier-order, observation-fiber, matched-null, and nearby-object audits remain bounded
  narrowest_supported_statement: additive design successor with intact no-execution boundary; not execution-ready
  next_concrete_action: preserve execution unauthorized and additively clarify RT-6C-1 through RT-6C-9 before any Stage 0/1 authorization
  artifact_paths:
    - coordination/goals/GOAL-SSI-001/batches/BATCH-6c960d/reviews/TASK-20260809-950724/red_team_report.md
    - coordination/goals/GOAL-SSI-001/batches/BATCH-6c960d/reviews/TASK-20260809-950724/runtime-session-receipt.json
```

## Verdict

**`CONCUR_WITH_CAVEAT` for a design-only review boundary; not execution-ready.**

The successor is a real additive repair and materially closes several findings
from BATCH-4f52ab. In particular, it now states a fixed per-prime advice
witness, distinguishes the random-set diagnostic from the universal fixed-advice
model, splits Construction B into order-tagged and membership-only forms,
defines an output-producing resolution-fiber union, registers a Construction-C
pair heuristic and matched pair null, and demotes the oriented/CSIDH comparison
to a non-gating diagnostic. Its top-level boundary also remains explicit:
`review_required`, `frozen: false`, `execution_authorized: false`,
`evidence_eligible: false`, and no hypothesis is attached
(`experiments/EXP-SSI-1d0f36/specification.yaml:1-43`).

The repair does not yet make the proposed rows or controls a reproducible
execution contract. The largest surviving problems are semantic rather than
cosmetic: the worst-case expected query cost is described but not defined by an
actual supremum equation; the typed records name fields without fixing their
byte encodings or branch-specific costs; `R_t(A)` conflicts with the shared
index/table bytes that the query is allowed to use; the primary random null can
reject by a validity tag before exercising the treatment path; and the exact
prime values needed for floors, saturation, and physical widths are absent.
These are blockers for any later Stage 0/1 authorization, not negative
evidence about the mathematical proposal. No experiment, Stage 0, Stage 1,
optional diagnostic, attack, security analysis, exponent result, novelty
finding, hypothesis transition, or goal-completion conclusion was made.

## Reviewed boundary and provenance

I read the governing contracts, the current batch manifest/queue/dispatch plan,
the snapshot receipt, `EXP-SSI-1d0f36`, its pinned predecessor
`EXP-SSI-2d8583`, the proposal, the BATCH-4f52ab Validator and Red Team
reports, the refinement report and duplication audit, and the corrected
catalogue files:

- `ideas/catalogue-20260806-mlkem-aes-ssi-ssqi/S1.md`
- `ideas/catalogue-20260806-mlkem-aes-ssi-ssqi/S2.md`
- `ideas/catalogue-20260806-mlkem-aes-ssi-ssqi/Q3.md`

The literal corrected paths exist in the reviewed tree and are also the paths
declared by the BATCH-6c960d Red Team read scope. This fixes the prior
BATCH-4f52ab `ssi-ssiq` spelling defect; I did not edit the queue or any input.
The three catalogue files, the proposal, the predecessor, and the successor
have no diff between the pinned snapshot and the queue-binding head.

The Git/provenance checks passed within the declared boundary:

- `840212b...` is a direct child of `e17eecc...`; the snapshot parent is
  `66ee7bce4292dbc068875b172de3da8d7b5fb1b8`.
- The snapshot commit changes exactly its receipt, the producer refinement
  report, the producer duplication audit, and `EXP-SSI-1d0f36`.
- The queue archive object binds snapshot commit `e17eecc...`, its parent, and
  the four exact declared SHA-256 path values. The live successor hash is
  `98212d5c195479c9978433371ad3414d9d9e4dc81c1696ee68d6f628b1350e27` and the
  predecessor hash is `d36a9cd14e4dc450f282118d6243d925fe8dd589fbdd16949183252aa2df27b`.
- The predecessor is unchanged from the snapshot parent through the queue
  head. The successor lineage is carried by its `supersedes` field, as the
  queue completion gate specifies; the existing schema registry remains
  unchanged and hash-pinned.

One provenance caveat survives: the committed snapshot receipt itself retains
`commit_sha: null` and `verification.status: pending_post_commit`. The queue
binding supplies the post-commit SHA, parent, and path hashes and those values
match the live Git state, so this is not a content mismatch. It does mean the
receipt is not self-contained proof of post-commit verification; a later archive
must preserve the queue/Git verification rather than describing the receipt's
null fields as independently complete.

## Findings

### RT-6C-1 — Fixed-advice wording is improved, but `T_q` is not formally the worst-case expected cost

The successor says that `A_p` is fixed before `E`, that query randomness is the
only expectation, and that `E` is worst case
(`experiments/EXP-SSI-1d0f36/specification.yaml:74-97`). This repairs the
prior quantifier ambiguity at the prose level. It does not yet define the
quantity charged by the frontier. The text names `T_q(A_p,E)` while saying that
`E` is “held at the worst case,” then the amortization formula uses
`T_q(A_p)` without defining how the `E` argument was eliminated
(`:79-97`). The contract must distinguish, for example, a supremum of the
query-side expectation from an expectation of a supremum; those are different
quantifier orders.

There is a second gap around advice-generation randomness. The contract says
that generation randomness belongs in `T_build` and must not be averaged away,
but it does not say whether the builder's seed is fixed as part of `A_p`,
worst-case over seeds, or averaged in a separately declared build measure. A
random builder can otherwise satisfy a finite-sample average while failing the
stated existential fixed-witness interpretation.

Finally, the restart paragraph gives an epsilon target and lists costs but does
not define a branch-specific success probability, nor what `T_q` means when an
instance has zero success probability. A truthful worst-case convention should
make that cost infinite (or declare the branch invalid), rather than allowing a
conditional-on-success table to look finite.

**Required control/repair:** bind `T_q^wc(A_p)` to an explicit
query-randomness expectation and a worst-case `E` operation; state the treatment
of fixed builder seeds; define the restart success probability and zero-success
case; and use that same quantity in the `Q` amortization equation and
break-even calculation. A clustered target set with an explicitly worst-case
start vertex is the cheapest static mutation; it was not run.

### RT-6C-2 — H-ADV-1-R is labelled as weaker, but H-ADV-1-W remains too vague to make the exclusion durable

The successor explicitly records that H-ADV-1-R covers random distinct target
sets and sampled starts only, and that it cannot establish H-ADV-1-W
(`experiments/EXP-SSI-1d0f36/specification.yaml:201-219`, `:340-350`). The
proof-map quantifier audit repeats the prohibition
(`:263-266`). This is a genuine improvement and is sufficient to reject any
claim that a random-set toy result is itself a universal fixed-advice result.

The remaining problem is that H-ADV-1-W is only described as a “conditional
worst-case-over-E hitting model” including the stated charges
(`:201-212`). It does not carry a formal hitting bound, its start-state
quantifier, a clustered/adversarial-set boundary, or a machine-readable result
field that a future report cannot accidentally mark as validated by the R
diagnostic. The contract therefore labels the two hypotheses correctly but does
not fully specify the semantic gate that prevents evidence migration.

**Required control/repair:** keep H-ADV-1-R descriptive-only, add an explicit
`cannot_validate: H-ADV-1-W`/non-promotion field to any future result schema,
and either formalize H-ADV-1-W with a worst-case set/start statement or narrow
the claim to the distribution actually tested. The random-set result must never
be the sole positive control for the universal row.

### RT-6C-3 — A/B/C are named as typed branches, but their records are not yet fully typed or costable

Splitting B was the correct repair. However, the successor still gives only
field names:

- A and order-tagged B use `[curve_id, order_tag, path_descriptor]`.
- Membership-only B uses `[curve_id, path_descriptor]`, while its terminal
  small-delta/order procedure is merely named.
- C uses `[left_endpoint, right_endpoint, middle_descriptor]`.

These declarations do not fix serialization widths, endianness/canonical
forms, validity semantics, orientation, path direction, middle-table key
meaning, or whether the descriptor contains information shared across entries
(`experiments/EXP-SSI-1d0f36/specification.yaml:128-179`). The byte symbols
`b_j`, `b_ord`, `b_path`, `b_idx`, `b_shared`, `b_padding`, and `b_entry` are
promised to be measured later but are not defined now. Construction B has no
branch-specific mapping from its threshold/density parameter to every exact
sigma row. Construction C's pair count and endpoint marginals are named, but
the actual pair generator and middle-factor correlation are not.

Thus the old `(S,T)` collision is no longer silently treated as an identity,
but the new branches remain underdefined enough that two implementations can
both satisfy the text while charging different advice, build, lookup, and
output costs. The C null has the same issue: “remove the declared middle-factor
correlation” is not an executable operation until the treatment distribution,
orientation, middle factor, and matching statistic are frozen.

**Required control/repair:** freeze a branch-by-branch typed byte table,
including all shared/index bytes and failed-build representations; specify B's
threshold-to-sigma mapping; specify C's ordered/unordered endpoint convention,
middle descriptor, table key, and pair-generation law; and state the exact
terminal output type and cost for membership-only B.

### RT-6C-4 — `R_t(A)` is a set union, but not yet an honest operational fiber for shared advice

The successor correctly requires distinct vertices, an explicit non-scalar
OneEnd witness, and union-before-counting
(`experiments/EXP-SSI-1d0f36/specification.yaml:181-199`). This removes the
prior double-counting ambiguity for a simple entry-based construction.

The definition still says that a query uses “only `a`,” while the same contract
allows a shared index, shared table bits, and shared metadata to be charged
once in the representation (`:175-179`, `:187-190`). A lookup that uses the
shared index is not using only `a`; a lookup that is allowed to use arbitrary
shared bits can make the per-element fiber depend on information not charged
to that element. Construction C is more direct: its pair entry is inherently a
multi-endpoint object, but the specification never states how a fiber of one
pair entry is represented in the union or whether a query may combine multiple
entries adaptively.

The output gate is directionally correct, but the actual path direction, field
encoding, order validation, saturation, and conversion to the explicit OneEnd
witness are deferred to a future implementation
(`:191-195`). Consequently, the current text defines the intended set, not a
constructive fiber/cost invariant that can yet be falsified.

**Required control/repair:** define `R_t` over `(A, shared_metadata)` with a
fixed access model, or explicitly exclude shared structures from the fiber
claim; give C a multi-entry query rule; and pin the canonical output witness,
path direction, field representation, validation, and saturation work before
using fiber mass in a cost row.

### RT-6C-5 — The random-advice null can pass by construction through `validity_tag=0`

The new null is more concrete than its predecessor: it specifies distinct
curve IDs, fixed-width payloads, SHAKE256-derived bytes, an independent seed,
the same declared lookup/budget path, and a no-witness result
(`experiments/EXP-SSI-1d0f36/specification.yaml:292-309`). The decisive flaw is
that `validity_tag=0` explicitly marks that no order data are attached, and the
query is instructed to return `NO_WITNESS` without interpreting the payload as
an order. A query can therefore reject before performing the treatment's
order parsing, identity validation, pullback, saturation, or output work. Its
forced incumbent outcome does not distinguish a content-sensitive instrument
from a branch that simply obeyed the null's invalidity bit.

This is not evidence that the treatment is wrong; it is a control-construction
failure. A negative control whose semantic type announces “invalid” is expected
to pass even when the treatment has an uncharged or malformed information path.

**Required control/repair:** use a same-width, well-typed payload with the same
validity class as treatment but no admissible witness, and require the same
parse/validation/pullback/output path to reach a charged rejection. If a
type-invalid null is retained, make it a separate parser regression control,
not the primary matched-content null. Do not infer anything from the declared
forced result until that mutation is frozen.

### RT-6C-6 — The shuffled-fiber control is a useful negative test but also has a forced rejection path

The shuffled control preserves the treatment bytes but assigns order payloads
to different curve IDs, with identity validation required before acceptance
(`experiments/EXP-SSI-1d0f36/specification.yaml:310-320`). This catches a query
that ignores the curve/order binding, but a correct identity check rejects the
control by construction. It therefore cannot by itself show that the treatment
advantage is not caused by table size, metadata, or an early branch shortcut.
It also does not say how the permutation handles duplicate IDs, the small-S
fixed-point exception, or the C pair representation.

**Required control/repair:** retain it as a narrowly scoped identity-integrity
control, with a deterministic permutation and explicit fixed-point/duplicate
rules, but pair it with the well-typed random-payload null above and a resource
null that traverses the same validation stages. Its pass must not be described
as evidence for the frontier.

### RT-6C-7 — The C pair null is named and scoped, but its pass criterion can still be selected after seeing the data

H-ADV-4 is now explicitly C-only and has a matched pair-null description
(`experiments/EXP-SSI-1d0f36/specification.yaml:236-248`, `:340-346`). The
contract does not pre-register the bins/statistic, finite-sample tolerance,
sample count, seed separation, or the exact independent-pair generator. It
only says that a future report must state them. A later implementation could
choose bins or a tolerance after inspecting the treatment and null, or choose
a statistic insensitive to the middle-factor correlation. That lets the null
pass without testing the stated pair law.

**Required control/repair:** freeze the pair statistic, bins, sample count,
seeds, tolerance, and acceptance rule before any C treatment row; make the null
preserve the exact orientation and endpoint marginals under the declared access
path; and report the result as descriptive unless the pre-registered gate is
actually met.

### RT-6C-8 — Build, deduplication, physical bytes, and Q amortization are obligations, not charged quantities yet

The successor names all the right axes: failed attempts, duplicate rejection,
serialization, index construction, physical advice bytes, working memory,
`T_build`, `T_q`, `T_amort`, and break-even `Q`
(`experiments/EXP-SSI-1d0f36/specification.yaml:93-97`, `:128-179`,
`:352-362`). The names do not yet supply numerical or symbolic functions:

- `b_entry` is undefined per branch, and the component widths are placeholders
  awaiting a freeze receipt.
- `T_build` has no formula for failed samples, retries, order-to-curve work,
  deduplication, index construction, or build peak memory.
- `S_eff = min(S, |V_p|)` assumes that the requested number of distinct records
  can be filled even though failed builds and rejected duplicates are separately
  charged; retained-record count and attempted-record count are not separated.
- The amortization formula uses `T_q(A_p)` without the missing worst-case
  operation from RT-6C-1 and does not define the incumbent comparison that
  determines `Q_break_even`.
- No unit conversion is pinned between the incumbent's entry model and the
  successor's physical bytes; the proposed byte formula is only a template.

**Required control/repair:** freeze the exact byte layouts and measured widths,
define attempted versus retained entries and all failure charges, report build
and query peak memory independently, define `Q_break_even` against an explicit
comparison quantity, and preserve all bytes/index/padding in the physical
model. A row lacking any one of these fields must stop before treatment
arithmetic.

### RT-6C-9 — The sigma labels are exact, but the parameter corners are not fully coherent without concrete primes

The rational labels themselves are repaired: `0`, `1/6`, `1/3`, `1/2`, `2/3`,
`4/5`, and `1` are represented by numerator/denominator pairs, and `S=0` is
explicitly a sentinel rather than `floor(p^0)`
(`experiments/EXP-SSI-1d0f36/specification.yaml:99-126`). The exact parameter
block gives only `log2_p: [256, 512]`, not actual prime values. Exact floors,
finite vertex counts, saturation, canonical field-coordinate widths, and even
the physical table size cannot be computed from a bit-length label alone.

The `S_eff = min(S, |V_p|)` shorthand also hides whether the builder is required
to continue until `S_eff` distinct entries are retained or may terminate with
fewer after failed/rejected attempts. At `sigma=1`, the full-table known-answer
control says that all distinct `V_p` vertices are available, while the logical
size is labelled `S=p`; the contract simultaneously says unused slots are not
free and that a random maximal-order sampler is not being credited with this
enumeration. The query corner can be retained as a symbolic known answer, but
its logical-slot padding, physical bytes, and build cost must be explicit.

**Required control/repair:** provide exact primes or an explicit symbolic
interval/arithmetic convention; define attempted, retained, and padded counts;
and state whether the `S=p` corner is a full `|V_p|` table padded to `p` slots or
a separate known-answer object not comparable on the treatment memory axis.
Keep `S=0` as the sentinel and keep the `p^{1/2}` balance point visibly
separate from the treatment row if that is the intended design.

### RT-6C-10 — The nearby-object demotion is now appropriate and durable within this boundary

This is a repair that survives. `CTRL-NEARBY-ORIENTED` is explicitly a
non-gating sanity diagnostic with no forced result, and the proof-map method
ceiling limits certification to the named typed branches
(`experiments/EXP-SSI-1d0f36/specification.yaml:267-270`, `:331-338`). The
diagnostic may still be underdefined if someone later runs it, but its result
cannot serve as a proof-map gate or validate the SSI frontier under the current
contract. No further repair is required before retaining it in this demoted
role; it must simply remain non-gating and separately scoped.

## Heuristic and proof-architecture challenges

The catalogue context supports the scope discipline but does not validate the
successor's hypotheses. S1-2 treats terminal membership cost as the load-bearing
quantity and warns that an uncharged test changes the accounting; Q3-2/Q3-7
separate family size from batched lookup and explicitly scope their necessary
conditions to a list-and-close architecture; Q3-8 distinguishes cheap
curve-side predicates from the hard visibility question. Those are useful
nearby controls, not evidence for this successor.

The remaining heuristic obligations are therefore:

- H-ADV-1-W: fixed-advice, worst-case-start hitting semantics and mixing;
- H-ADV-2: availability and cost of the order-to-curve direction;
- H-ADV-3: the bounded resolution-fiber growth rule for the named typed
  branches; and
- H-ADV-4: the C-specific endpoint-pair law.

None is promoted here. In particular, a toy random-target CDF, a symbolic
known-answer corner, a forced null outcome, or a catalogue derivation is not a
measurement of any of these hypotheses.

The output/reduction boundary also remains important. The successor requires a
future implementation to turn a walked path plus stored order information into
an explicit admissible non-scalar OneEnd witness, but it does not yet pin that
conversion. Until it does, a fiber count of abstract ring membership would not
be the same object as a fiber of output-producing queries. No transfer to
EndRing, Isogeny, any scheme, or any security interpretation is admitted.

## Baseline comparison

The successor carries S=0, the S=p^(1/2) balance embedding, and the full-advice
known-answer corner as declared controls
(`experiments/EXP-SSI-1d0f36/specification.yaml:250-291`). I treat these as
model inputs and boundary tests only; none was executed or independently
recomputed. The incumbent, working-memory, advice, and query axes are not
physically comparable until exact primes, byte widths, and build/query units
are fixed. Accordingly, this review makes no broader baseline or algorithm
comparison and draws no result from the pre-registered frontier formula.

## Required controls before any execution authorization

1. Define the fixed-advice worst-case expected query cost, builder-seed
   convention, success probability, restart cost, and zero-success behavior.
2. Freeze exact primes or a valid symbolic convention, then freeze branch-level
   byte schemas, width measurements, path/orientation rules, and B/C parameter
   mappings for every sigma label.
3. Replace `validity_tag=0` as the primary random-advice null with a same-typed
   random payload that traverses the treatment validation/output path; retain a
   type-invalid null only as a parser control.
4. Keep shuffled-fiber as an identity-integrity control, but add explicit
   permutation/fixed-point rules and do not treat its forced rejection as
   evidence of the frontier.
5. Pre-register the C pair-null generator, orientation, statistic, bins, sample
   count, seeds, tolerance, and descriptive-versus-gating status.
6. Define the shared-data access model for `R_t`, construction-C multi-entry
   queries, and the exact canonical OneEnd witness/output conversion.
7. Define attempted versus retained entries, duplicate/failure charges, build
   and query peak memory, physical padding, and the exact break-even-Q
   comparator.
8. Preserve the current non-gating nearby diagnostic and the explicit
   no-execution/no-attack/no-security/no-exponent/no-novelty boundary.

## Counterexamples and mutations proposed (not executed)

- Hold a target-set cardinality fixed and replace a random set with a clustered
  set while taking the worst starting vertex. This separates H-ADV-1-R from the
  fixed-advice worst-case claim.
- Keep the random-advice record widths and curve IDs fixed, set the payload to
  a well-typed random order encoding with the treatment validity class, and
  force the same parse, identity, pullback, saturation, and output checks before
  rejection. If the null cannot be made to traverse that path, it is not a
  matched-content control.
- Strip order tags from B while preserving its curve IDs and access budget. A
  changed terminal cost would expose the representation collision that the
  successor correctly refuses to collapse by `(S,T)` alone.
- Hold the C endpoint marginals fixed while removing only the middle-factor
  coupling using a pre-registered independent-pair construction. Reject any
  later choice of bins or tolerance made after seeing the treatment.

These are review mutations only. They were not executed because the task
prohibits EXP-SSI-1d0f36, Stage 0/1, and optional diagnostics.

## Narrowest supported statement

At the pinned queue head, BATCH-6c960d provides a hash-bound additive successor
whose design contract is materially more explicit than `EXP-SSI-2d8583` and
whose corrected `ssi-ssqi` catalogue paths are present and readable. The
successor's provenance and no-execution boundary are intact, subject to the
snapshot receipt's pending/null self-binding caveat. The contract is not yet a
fully specified or control-safe execution protocol: the RT-6C-1 through
RT-6C-9 caveats remain open. The nearby-object diagnostic is appropriately
non-gating (RT-6C-10).

The only safe Coordinator action from this review is to archive this report
with the other independent review, preserve execution as unauthorized, and
either create an additive clarification covering the listed fields or record
that the batch remains design-only. This report does not change any official
status.

## Artifact paths

- `coordination/goals/GOAL-SSI-001/batches/BATCH-6c960d/reviews/TASK-20260809-950724/red_team_report.md`
- `coordination/goals/GOAL-SSI-001/batches/BATCH-6c960d/reviews/TASK-20260809-950724/runtime-session-receipt.json`
