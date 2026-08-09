# Red-team report — `TASK-20260809-2ded5b`

```yaml
red_team_report:
  id: RT-20260809-2ded5b
  task_id: TASK-20260809-2ded5b
  claim_under_review: >-
    Completeness of the design-only exact-cost and control contract in
    EXP-SSI-fe3f76. This is a contract review; no scientific claim is reviewed
    or made.
  verdict: DISSENT
  verdict_scope: >-
    Dissent from treating the successor as execution-ready or as having closed
    the requested exact-cost/control gaps. Concur that it is an additive,
    execution-unauthorized design refinement with an explicit no-claim ceiling
    and intact snapshot provenance.
  objections:
    - RT-B6-1: exact prime expressions are present, but the F_p^2 basis and
      canonical j-coordinate serialization are not fully pinned; two source
      line references do not identify the cited prime text.
    - RT-B6-2: the T_q definition is materially repaired and has correct
      fixed-advice, worst-case, q=0, and fixed-seed wording, but the builder,
      cost units, and branch-level index construction needed to instantiate it
      are not defined.
    - RT-B6-3: A/B widths and the B theta-to-sigma map are explicit at the
      field-list level, but order canonicalization, C indexing, and the
      branch-polymorphic control record types remain incomplete.
    - RT-B6-4: R_t(A;I_A) is a better shared-index union definition, but its
      byte pair contains undefined b_shared, its index formula is not reconciled
      with retained versus attempted records, and C has no corresponding
      multi-entry fiber access contract.
    - RT-B6-5: the repaired random-advice path avoids the old invalid-tag
      shortcut for tagged records, but its stated layout cannot be the same
      typed payload for membership-only B or pair-entry C; the small-cardinality
      edge and S=0 applicability are also not fully specified.
    - RT-B6-6: the C finite gate fixes n, bins, and tolerance numerically but
      leaves the binning observable, C_iid, collision event, and pair generator
      semantics open; H-ADV-1-R still lacks a fully reproducible toy walk/CDF
      protocol, while correctly remaining weaker than H-ADV-1-W.
    - RT-B6-7: build/deduplication/physical-byte/Q obligations are named, but
      b_shared, padding, failed-receipt widths, pair-index bytes, exact build
      equations, compatible incumbent units, and an integer break-even rule are
      not frozen. S=p and S_eff therefore remain mixed symbolic and physical
      corners.
  required_controls:
    - Pin an F_p^2 defining polynomial or basis, component order, canonical
      version-byte value, and canonical order/basis serialization; correct the
      frozen-source line pointers.
    - Define attempted, failed, duplicate, retained, saturated, and padded
      counts and use the appropriate retained count in every index/byte formula.
    - Define per-branch index layouts and widths, including b_shared, C pair
      index metadata, padding, failed-build receipts, and physical peak memory.
    - Give T_build and T_q a common declared work unit and a branch-level build
      algorithm; define the integer Q break-even comparator against an explicit
      incumbent cost in those units.
    - Provide separate same-typed matched nulls for A-tagged, B-tagged,
      B-membership-only, and C-pair records, with a specified path and output
      gate for each; retain shuffled-fiber only as an identity-integrity test.
    - Freeze the C pair generator, endpoint orientation, bin observable,
      collision definition, iid reference, seed pairing, and acceptance gate.
    - Freeze the H-ADV-1-R toy walk kernel, target-set generator, time horizon,
      censoring, aggregation, and CDF comparison procedure without presenting
      it as H-ADV-1-W evidence.
  counterexample_or_mutation: >-
    Proposed but not executed: apply CTRL-RANDOM-ADVICE to the
    B-membership-only and C-pair branches without adding fields; the declared
    order_tag/owner_curve_id layout is unavailable there. Separately, take
    |V_p|=1 in the stated random-advice modulo rule; its forced-zero result no
    longer follows. These are contract mutations only, not experiment results.
  baseline_comparison: >-
    S=0, the p^(1/2) balance control, and the S=p full-advice corner were read
    as declared known-answer inputs only. No baseline, arithmetic row, or
    physical-cost comparison was executed or independently validated.
  heuristic_challenges:
    - H-ADV-1-W is explicitly fixed-advice and worst-case-over-E; the separate
      random-set H-ADV-1-R diagnostic is correctly prohibited from validating it,
      but its own finite protocol is still underdefined.
    - H-ADV-2 and H-ADV-3 remain unverified conditional assumptions; the
      deferred output-producing pullback and shared-data access rules prevent a
      future fiber row from being treated as a fully operational witness count.
    - H-ADV-4 is correctly C-only and has a matched-null concept, but its
      statistic is not yet reproducible from the frozen fields.
  cost_model_challenges:
    - T_q(A_p,E)=E[W]/q with q=0 mapped to infinity and a max over E is a
      coherent repaired semantic definition.
    - The contract does not define the builder/index construction, common work
      units, failed-build receipt size, or exact branch-level T_build function.
    - M_adv_bytes and Q_break_even are named but not fully evaluable; b_shared,
      padding, C index metadata, and the incumbent comparator are missing.
    - b_index uses S while the contract also introduces S_eff after duplicate
      rejection, without saying whether slots are allocated for requested,
      attempted, retained, saturated, or padded records.
  reduction_and_scope_challenges:
    - The pullback, saturation, path direction, field encoding, and conversion
      to an explicit non-scalar OneEnd output are still deferred to a future
      implementation, so abstract membership cannot yet be substituted for an
      output-producing fiber.
    - R_t is restricted to named typed branches and is not a universal
      all-advice lower bound; this ceiling is appropriate and must remain.
    - The nearby oriented/CSIDH object is explicitly non-gating and separately
      typed; that demotion survives review.
  proof_architecture_challenges:
    - The exact sigma grid, S=0 sentinel, S=p corner, and B map are recorded,
      but saturation/padding and physical comparability at the corners remain
      unresolved.
    - The observation-collision audit correctly separates B-tagged from
      B-membership-only, but the two branches still need complete byte and
      query accounting before any collision interpretation.
    - The named finite controls are not observations and must not be treated as
      proof-map passes until their missing generators and statistics are frozen.
  narrowest_supported_statement: >-
    The immutable snapshot and successor are an additive, no-execution design
    refinement with a substantially clearer fixed-advice T_q semantic, typed
    branch split, conditional heuristic inventory, non-gating nearby diagnostic,
    and explicit no-attack/no-security/no-exponent/no-novelty/no-completion
    boundary. They do not yet constitute a complete, branch-polymorphic,
    physically charged, reproducible execution contract. No scientific result
    follows from this review.
  next_concrete_action: >-
    Create an additive clarification record before freeze or authorization that
    pins the F_p^2 and order encodings, branch-specific indexes and matched
    nulls, R_t access model, C and H-ADV-1-R statistics, retained/padded byte
    accounting, and compatible build/Q units. Re-review the clarification
    independently; do not execute a stage or diagnostic as part of this repair.
  artifact_paths:
    - coordination/goals/GOAL-SSI-001/batches/BATCH-6554d6/reviews/TASK-20260809-2ded5b/red_team_report.md
    - coordination/goals/GOAL-SSI-001/batches/BATCH-6554d6/reviews/TASK-20260809-2ded5b/runtime-session-receipt.json
```

## Verdict

**`DISSENT` on execution readiness; `CONCUR` on additive provenance, scope, and claim ceiling.**

The successor is materially better than `EXP-SSI-1d0f36`. In particular, it now
states a fixed p-dependent advice object, keeps the instance worst case over
`V_p`, averages only query randomness, defines `q=0` as infinite cost, conditions
builder randomness on a committed seed, separates build cost from query cost,
and explicitly prevents H-ADV-1-R from validating H-ADV-1-W
(`experiments/EXP-SSI-fe3f76/specification.yaml:75-97`, `:221-239`). The B
mapping is also algebraically explicit for its applicable rows, and the nearby
oriented/CSIDH object is correctly demoted to a non-gating diagnostic
(`:176-189`, `:365-369`).

Those repairs do not close the contract. The remaining failures are not
observations against a mathematical hypothesis. They are specification and
control failures that should block freeze, arithmetic-row production, and any
execution authorization until corrected. No experiment, Stage 0, Stage 1,
optional diagnostic, attack, security analysis, exponent conclusion, novelty
statement, hypothesis transition, or goal-completion conclusion was made here.

## Review boundary and inputs

I reviewed the immutable snapshot commit `b12abf38922e62329d7bd51cf690c88bf759b50d`
and its successor `EXP-SSI-fe3f76`, without treating the later checkout `HEAD`
as the review boundary. I read:

- `AGENTS.md` and `agents/red-team.md`;
- the BATCH-6554d6 manifest, queue, dispatch plan/report, and snapshot receipt;
- `experiments/EXP-SSI-fe3f76/specification.yaml` and its predecessor
  `experiments/EXP-SSI-1d0f36/specification.yaml`;
- `ledger/proposals/IDEA-20260806-9c2f80.yaml`;
- `inputs/P13-WESOLOWSKI-2026/paper_fulltext.md`;
- the producer refinement/audit artifacts and the prior BATCH-4f52ab and
  BATCH-6c960d review materials named by the successor; and
- the three current corrected catalogue paths named by the successor:
  `ideas/catalogue-20260806-mlkem-aes-ssi-ssqi/S1.md`, `S2.md`, and `Q3.md`.

The catalogue files are present under the `ssi-ssqi` directory and state that
they are proposal material with novelty unadjudicated. They are context only;
they do not validate this successor or supply any missing execution semantics.

## Snapshot and provenance integrity

The pinned snapshot has parent
`8264428dae7fa8d2cc085099748f85108c7e8da6` and changes exactly these four paths:

1. the snapshot receipt;
2. the producer refinement report;
3. the producer duplication/knowledge audit; and
4. `experiments/EXP-SSI-fe3f76/specification.yaml`.

The snapshot receipt records the same parent (abbreviated there as
`8264428da`) and the three producer/successor path hashes below. The receipt
itself retains `commit_sha: null` and `verification.status: pending_post_commit`;
this review did not invoke or rely on a later queue-binding/verification
command, so those later operational receipts are not treated as part of the
reviewed snapshot evidence. The recorded path hashes are:

- refinement report: `25ecf6728f04f9fde3989d6a2b02485739704960f2296333113fbc1233523a60`;
- duplication audit: `7b07b6a3af7b1861cef9f1026837404ec0c5d8c74bf86ca8963a8c3397435493`;
- successor specification: `234a9ccc58ae511fa62fa3d5c5ecc82d24069ad2ebf1ac1cb63f670e110d0f34`.

The receipt stored in the snapshot itself has `commit_sha: null` and
`verification.status: pending_post_commit`; that is consistent with the
post-commit queue binding, but the receipt alone is not self-contained proof of
the post-commit verification. I do not treat that bookkeeping limitation as a
scientific or cryptanalytic result.

The frozen-source prime provenance is less precise than the successor claims:
the paper states both exact expressions at line 248 and identifies the second
case again at line 256. The successor cites `:248,256` for SQIsign-I and
`:248,257` for SQIsign-V (`:102-103`); line 257 is blank, and line 256 is the
Figure 2 caption. The expressions themselves are present, but the source
selectors should be corrected to the exact text line(s).

## Falsification findings

### RT-B6-1 — Exact primes are present, but the vertex byte encoding is not fully canonical

The exact expressions `5*2^248-1` and `27*2^500-1` are a real repair over the
predecessor’s bit-length-only parameter block. The declared formulas imply
`bit_length(p)=251, b_p=32, b_curve=65` for the first expression and
`bit_length(p)=505, b_p=64, b_curve=129` for the second. This arithmetic is only
a static reading of the declared expressions, not an executed experiment.

The byte string is nevertheless not fully pinned. `j_0` and `j_1` require a
specific representation of `F_{p^2}`: a defining polynomial or non-residue,
the basis, coefficient order, reduction convention, and the concrete value of
the one-byte encoding version. The text says “canonical unsigned little-endian”
for field elements but does not say what makes the two coordinates canonical or
which `F_{p^2}` basis is used (`:104-110`). The order tag is likewise a width
description rather than a canonical order/basis encoding: it gives four signed
scalars and an owner curve but no basis ordering, order normalization, version
value, or duplicate-key rule for equivalent order descriptions
(`:143-152`).

Thus the successor has exact width expressions but not an exact reproducible
vertex/order serialization. A later freeze receipt cannot repair a missing
serialization convention merely by reporting measured widths; it must identify
the bytes that were measured. The contract also gives no canonical enumeration
or membership/sampling procedure for `V_p`; consequently `|V_p|`, the
`target_index` used by the null, duplicate rejection, and the full-advice
control are named quantities rather than reproducible finite objects.

### RT-B6-2 — T_q is semantically repaired, but not yet instantiable as a charged functional

The fixed-advice/worst-case-E semantics survive the direct definitional attack:
`omega` is query-side randomness only, `W` includes lookup, parsing, validation,
walks, pullback, saturation, output conversion, and failed-candidate work,
`q` is the probability of an admissible output before the hard budget,
`q=0` yields infinity, and the worst-case query cost is a maximum over `V_p`
(`:79-92`). The stated amortization identity is also clear at the symbolic
level (`:93-97`). This is a repair, not a measured result.

The remaining problem is instantiation. No builder algorithm defines how a
fixed `A_p`, its shared index, and its retained records are produced from the
committed builder seed. `T_build` is said to include failures, duplicates,
serialization, and index construction, but there is no branch-level equation
or common declared work unit for those charges (`:88-92`, `:162-175`). The
incumbent is only `p^(1/3+o(1))` in the contract (`:129-132`), so the
break-even expression cannot be evaluated or compared to `T_build` until the
incumbent and builder costs are expressed in compatible units. The repaired
semantic definition is therefore coherent but not a complete cost contract.
In addition, `L_steps` is never assigned a value in the successor, although
the producer repair summary described a prospective `2^20` bound. The finite
success event and per-attempt work are therefore not concretely bounded by the
successor itself. Restart independence also lacks a prescribed
domain-separated seed derivation, and the amortization line states an equality
for `Q` instances even though `T_q` is a worst-case expected bound rather than
a specified instance-sequence expectation.

### RT-B6-3 — A/B/C widths and the B mapping are improved but still underdefined

The successor does make the useful distinctions the predecessor lacked:

- A and tagged B have separate named record schemas;
- membership-only B has no hidden order bytes;
- C has two endpoint IDs and a middle descriptor; and
- `sigma_B(theta)=1/2+3theta/2` with
  `theta=(2sigma-1)/3` is mapped for `sigma` `1/2`, `2/3`, `4/5`, and `1`,
  while lower sigma labels are explicitly not applicable (`:153-189`).

The widths are not sufficient to define the data structures. C’s
`middle_descriptor` contains only two slot indices; no middle-factor identity,
orientation, path direction, or reconstruction rule is specified. “Pair index”
and its offsets/collision metadata are charged by name but have no width
formula (`:151-157`, `:173-175`). B’s optional “delta-screen certificate bytes”
are also not a declared field with a width (`:166-172`). The order-tag fields
have the canonicalization gaps described in RT-B6-1.

Most importantly, the control record in `CTRL-RANDOM-ADVICE` says the selected
treatment branch has a valid `lookup_curve_id` and a valid `order_tag`
(`:326-341`). That is not the exact record layout of
`construction_b_membership_only`, which has only a curve ID, nor of C, which
has two endpoints and a middle descriptor. The control therefore cannot be
the same-typed matched null for every branch listed in the prediction formula
(`:397-404`). Construction C also has no declared `S_C`/sigma mapping or
endpoint-list size law, so the `T_C_pair` term in `T_min(S)` is not evaluable
from the frozen contract even if its byte layout were completed.

### RT-B6-4 — R_t(A;I_A) is a better union, but shared-byte and C-fiber accounting remain open

The replacement of the old `R_t(A)` with `R_t(A;I_A)` is directionally correct.
It counts distinct vertices, requires an explicit output-producing witness,
unions before counting, and says that shared index bytes are not free
(`:196-215`). This prevents the prior simple overlap/double-counting objection
for the explicitly named A model.

The operational invariant is still incomplete:

- the reported pair contains `b_index+b_shared`, but `b_shared` is never
  defined;
- `b_index=1+S*(b_curve+b_slot)` uses requested `S`, while the same contract
  introduces `S_eff=min(S,|V_p|)` after duplicate rejection and later requires
  attempted/retained/padded counts to be reported (`:119-125`, `:149-152`,
  `:186-194`);
- the access rule says a query may read the declared shared index and its
  selected record, but does not define the per-record selection/key/scan model
  for each branch; and
- only `I_A` is named in the fiber definition. C’s pair entry can require two
  endpoint resolutions and a middle reconstruction, but no multi-entry C fiber
  union or adaptive-access rule is supplied.

The claim ceiling correctly restricts this to named typed branches and rejects
an all-advice theorem (`:216-219`). The issue is that even the named C branch
has not yet been made into the same output-producing, byte-charged object as A.

### RT-B6-5 — The null path is repaired for tagged records, not for the declared branch family

The new random-advice null fixes the old construction flaw for an A/tagged-B
record: it uses a valid order tag, assigns a different owner curve, forbids a
malformed validity tag, and requires parse, validation, path reconstruction,
pullback, saturation, and only then final identity rejection (`:326-342`).
The shuffled-fiber control similarly preserves valid fields and requires the
same semantic work before the final gate (`:343-352`). These are useful repairs.

They do not establish semantic null equivalence for the full declared branch
family. The random null’s required `order_tag` is absent from membership-only
B, and its single lookup/owner shape is absent from C. The C pair null is a
distribution null, not a replacement for a same-path semantic null, and the
specification does not say what the B-membership-only null must parse, validate,
and charge. A future implementation could therefore use the stronger null for
A while leaving the membership terminal procedure or C reconstruction
uncontrolled.

There are two additional edge ambiguities. The random owner rule uses
`(target_index+1) mod |V_p|` without the explicit `|V_p|=1` fallback given to
the shuffled control; at cardinality one it does not force a no-witness result.
Also, `CTRL-RANDOM-ADVICE` is described as a control at every declared `S`, but
the S=0 control explicitly has no advice lookup (`:317-325`), so its paired
record/path is undefined at that corner. The exact cryptographic primes are
not being tested here; these are unclosed finite-contract cases.

There is a deeper validity ambiguity in the owner permutation. If the four
scalar payloads remain attached to the original owner while only
`owner_curve_id` is changed, the order tag is not necessarily valid for its
declared owner and can fail validation for precisely the reason the null is
supposed to avoid. If the payload is rebuilt or moved with a valid order for
the new owner, the null carries endomorphism data and is no longer the stated
"no endomorphism data" object. The contract must choose and define one of
these constructions. Finally, the text does not define whether the treatment
acceptance condition is owner equality or production of an explicit witness
at the target after pullback; without that definition, the forced zero result
is asserted rather than entailed by semantic-path equivalence.

The shuffled control should consequently remain a narrow identity-integrity
control. Its forced rejection is expected from the owner-curve check and is
not evidence for the frontier or for the absence of a content-independent
shortcut.

### RT-B6-6 — Finite gates are numerically named but not fully reproducible

The successor improves the C gate to `n=8192`, `B=256`,
`z_max<=6`, and `|collision_excess|<=4/sqrt(8192)` and explicitly scopes it to
C (`:353-381`). However, no definition says what observable is assigned to a
bin, how endpoints are oriented before binning, what counts as a collision, or
how `C_iid` is computed. The formula
`collision_excess=(C_obs-C_iid)/n` is not executable without those definitions
(`:360-363`). A fixed sample count and tolerance do not prevent post-hoc choice
of the statistic.

The H-ADV-1-R gate has the right logical separation and adds 1024 target sets,
4096 starts, 8 replicates, a committed seed, and a KS tolerance
(`:377-381`). It still does not freeze the toy prime set, non-backtracking walk
kernel and initial-step convention, walk horizon, censored-hit treatment, null
CDF construction, or aggregation across sets/replicates. It remains a sampled
random-set diagnostic and cannot validate H-ADV-1-W; that limitation is one of
the successor’s surviving strengths, not a failure to be “fixed” by more toy
samples.

The `paired_query_seeds` field and seed list likewise do not state the pairing
map or the RNG/serialization procedure that makes the null and treatment path
work comparable (`:300-315`). No gate was run here.

### RT-B6-7 — Physical bytes, deduplication, build cost, and Q remain obligations rather than closed charges

The successor names all relevant axes and gives a conditional break-even
expression (`:190-194`, `:384-395`), but several quantities are still
placeholders or inconsistent:

- `b_shared` appears in the fiber pair and physical-memory prose but has no
  definition; `b_entry`, `b_padding`, failed-build receipt width, deduplication
  metadata width, and C pair-index width are not frozen;
- `b_index` is defined for an A-like shared index in terms of `S`, while
  duplicate rejection and finite-vertex saturation produce `S_eff`; the
  contract does not state whether requested, attempted, retained, rejected,
  saturated, and padded slots are all materialized or which ones consume
  index bytes;
- C says to charge a pair index but supplies no physical index layout, and B
  allows certificate bytes “if any” without a byte count;
- `T_build` has no explicit failure/retry/dedup/index work equation or peak
  memory equation; and
- `Q_break_even=T_build/(T_inc-T_q)` has no integer ceiling/minimum convention,
  no branch/min-row selection rule, and no explicit incumbent cost in the same
  work unit. When `T_q>=T_inc` it is undefined, but the contract does not say
  how the row is reported in a Q table.

The sigma grid itself is now coherent at the label level: `0` is a sentinel,
the exact rational rows are listed, B is absent below `1/2`, and `1` is marked
as a symbolic full-advice control rather than sampler evidence
(`:111-125`, `:176-189`). The physical corner is not coherent yet: `S=p`
requests p logical entries while the full table contains only distinct `V_p`
vertices and the contract simultaneously introduces saturation and padding.
The full-advice control can remain a symbolic known-answer corner, but it must
be explicitly excluded from or fully specified on the comparable physical
memory axis before any arithmetic table is called exact.

### RT-B6-8 — The claim ceiling and nearby-object demotion survive

This is the strongest part of the repair. The successor states that it cannot
validate H-ADV-1 through H-ADV-4 by symbolic arithmetic, cannot certify an
all-advice lower bound, and cannot transfer to EndRing, Isogeny, SQIsign, CSIDH,
or deployed parameters (`:38-43`). Its heuristic inventory marks H-ADV-1-R as
diagnostic-only and explicitly says it cannot establish H-ADV-1-W
(`:221-239`). The nearby oriented/CSIDH object is explicitly non-gating
(`:365-369`), and the invalidation rules prohibit attack, security, exponent,
and method-ceiling overclaims (`:454-460`).

The batch manifest independently sets `execution_authorized: false` and the
same design-only claim ceiling. I preserve that boundary. Nothing in this
report promotes, rejects, or changes any hypothesis or official research
status.

## Required next action

Before freeze or any authorization, create an additive clarification that:

1. fixes the `F_{p^2}` basis/encoding and canonical order representation;
2. corrects the frozen-source line pointers;
3. gives branch-specific A, B-tagged, B-membership-only, and C index/record
   schemas and matched null paths;
4. assigns `L_steps`, defines work units/restart seed derivation, and gives the
   `T_build`/`T_q`/integer-`Q` conventions in one compatible unit;
5. defines `R_t` access and output conversion for every branch;
6. defines C’s size law, pair generator/statistic, and H-ADV-1-R’s complete toy protocol;
7. separates requested, attempted, failed, duplicate, retained, saturated, and
   padded records;
8. supplies physical-byte and peak-memory formulas including all shared/index
   metadata; and
9. defines valid, branch-specific semantic null construction, including the
   actual final acceptance gate and domain-separated paired seeds.

The clarification should receive a fresh independent review. No experiment,
Stage 0/1 arithmetic, or optional diagnostic is needed or authorized as part
of this review repair.

## Artifact paths

- `coordination/goals/GOAL-SSI-001/batches/BATCH-6554d6/reviews/TASK-20260809-2ded5b/red_team_report.md`
- `coordination/goals/GOAL-SSI-001/batches/BATCH-6554d6/reviews/TASK-20260809-2ded5b/runtime-session-receipt.json`
