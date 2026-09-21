# Red-Team Review: TASK-20260809-f2ea94

## Review boundary

This is an independent Red Team review of the proposed qualitative successor
to `EV-SSI-59f7a2`. The reviewed proposal is the correction in
`coordination/goals/GOAL-SSI-001/batches/BATCH-d03e96/tasks/TASK-20260809-238546/correction_derivation.yaml`,
as snapshot-bound by `TASK-20260809-6e8601` and the dispatch queue. The review
does not edit the predecessor, the derivation, the frozen source, or a ledger
record. No experiment, new numerical calculation, or cost-model execution was
performed.

The claim boundary is documentary only: whether the old OneEnd/SQIsign label
and its missing transfer conditions require a qualitative correction, and
whether the predecessor's `2^{120-123}` value may be carried forward as a
properly qualified historical/model quantity. This report makes no security,
exponent, attack, hypothesis-status, or goal-completion claim.

## Verdict

**CONCUR_WITH_CAVEAT — the narrow qualitative correction survives adversarial
review, provided the successor uses the qualifiers below literally.**

The frozen paper supports attributing the Section 4.1 algorithmic estimate to
the paper's OneEnd solution path. The paper's SQIsign references support
relevance to SQIsign parameter selection, but do not by themselves turn the
OneEnd-side cost model into a direct SQIsign key-recovery or security result.
`SC-1` and `SC-3` are necessary transfer-boundary conditions, but `SC-3`
should be understood as “not automatically inheritable” rather than as a
claim that a concrete cost can never be transferred after a separate,
reduction-aware accounting. The `2^{120-123}` bracket is honest to preserve
only as the predecessor's un-recalculated, model-dependent OneEnd-side
bracket. It would be dishonest to preserve it as a newly verified or direct
SQIsign quantity.

## Source interpretation: does Section 4.1 support OneEnd attribution?

### Strongest objection

Section 4.1 says “the algorithm” and labels its parameter row “SQIsign
NIST-I”; it does not repeat the word `OneEnd` in the section heading. A
reader could therefore argue that the section is a generic supersingular
isogeny/SQIsign cost estimate rather than an estimate attached to OneEnd.

### Falsification result

That objection does not survive the local source context:

1. The frozen source identifies the object of Theorem 1.1 as finding a
   non-scalar endomorphism, and Problem 2.2 names exactly that computational
   problem `OneEnd` (`inputs/P13-WESOLOWSKI-2026/paper_fulltext.md:17-23` and
   `:117-120`).
2. Algorithm 3 is explicitly titled “Finding a non-scalar endomorphism” and
   returns the non-scalar endomorphism constructed from the random walk,
   Algorithm 2, and Frobenius (`paper_fulltext.md:193-220`).
3. Section 4.1 immediately follows that proof and says it is estimating the
   concrete cost “of the algorithm”; its `M`, `P0`, table-generation, and
   per-attempt quantities are the quantities used by Algorithm 2 inside
   Algorithm 3 (`paper_fulltext.md:222-240`).

Thus “OneEnd-side” is a faithful attribution when it means the concrete cost
model of this paper's Algorithm 3 route to a OneEnd output. The attribution
must not be widened into any of the following stronger statements:

- a lower or upper bound for every possible OneEnd algorithm;
- a direct cost for the EndRing or Isogeny problems; or
- a measured cost for an implementation at the stated parameter.

### Surviving caveat

The source itself calls the Section 4.1 quantity a rough lower-bound estimate,
charges one field operation per table entry as an optimistic assumption, and
assumes the Lemma 3.5 success-probability bound is tight. It also warns that
the table-generation cost is underestimated and that the bound on `P0` may not
be tight (`paper_fulltext.md:224-240`). Therefore the safe attribution is
“Section 4.1's rough OneEnd-algorithm cost model,” not “the OneEnd concrete
cost.” The correction derivation largely captures this distinction; the
successor should retain it in its prose.

## Source interpretation: can the SQIsign discussion rescue the old label?

### Strongest objection

The paper explicitly lists the SQIsign signature family among systems affected
by the new algorithm, says that the cost of resolving the relevant problem is
a major factor in parameter selection, and says that the concrete parameters
warrant reevaluation (`paper_fulltext.md:27-43`). Section 4.1 then labels the
`log2(p) approximately 256` row “SQIsign NIST-I” and compares it with previous
methods (`paper_fulltext.md:232-240`). This is genuine source-level evidence
that the author intended the table to inform SQIsign discussion. The old
record's SQIsign-oriented reading is therefore not baseless or fabricated.

### Falsification result

It nevertheless does not rescue the old *unqualified* label. The same source
draws a boundary between the problems: Theorem 1.1 is OneEnd, while Corollary
1.2 obtains EndRing and Isogeny through cited reductions
(`paper_fulltext.md:17-25`, `:117-127`). The source says the new algorithm is
not a complete break of the listed cryptosystems and describes the practical
impact as unclear, with high memory and optimistic concrete-cost assumptions
(`paper_fulltext.md:29-43`). Nothing in the frozen Section 4.1 passage is a
key-recovery, forgery, or scheme-specific security theorem for SQIsign.

The correct surviving interpretation is therefore two-layered:

- **Supported by the source:** the OneEnd algorithm's parameterized cost is
  relevant input to a reevaluation of systems whose security depends on the
  corresponding supersingular problems, and the paper chose SQIsign parameter
  rows to illustrate that relevance.
- **Not supported by that passage alone:** relabeling the OneEnd-side numeric
  model as a direct SQIsign security estimate, without instantiating the
  reduction chain, its conditions, its output requirements, and its concrete
  overheads.

The proposed correction is therefore narrow enough. It should not overcorrect
by saying that the SQIsign discussion is irrelevant; it should say that
relevance is not automatic concrete-security transfer.

## SC-1: GRH at the transfer boundary

### Objection and assessment

`SC-1` says that GRH enters at the Isogeny arrow through [35, Proposition
8.5], while the frozen source's Corollary 1.2 lists only Heuristic 1. The
standing condition is directionally correct and is needed to prevent the
phrase “conditional on Heuristic 1 alone” from being applied indiscriminately
to the entire cascade. This is also the exact distinction recorded in
`ledger/goals/GOAL-SSIQ-001/checkpoints/BATCH-002.yaml:132-148`.

There is, however, a proof-boundary caveat: the frozen paper states the
corollary and names the reductions, but Section 4.1 does not reproduce the
hypotheses or finite-cost behavior of [35, Proposition 8.5]. The source's
introduction separately describes rigorous reductions under GRH and the later
OneEnd equivalence history (`paper_fulltext.md:121-127`). Accordingly, SC-1
is a required transfer warning, not a complete derivation of the transfer
condition. A future successor should retain the exact proposition citation
and should not imply that this red-team review independently re-proved its
hypotheses.

### Required wording

The successor should state that the OneEnd-side source estimate retains the
source's own condition, while any Isogeny/SQIsign interpretation must carry
the GRH condition attached to the cited reduction. It should avoid collapsing
the two into one blanket “Heuristic 1” condition. This is a documentary
conditionality correction, not a new mathematical claim.

## SC-3: concrete cost across the reduction cascade

### Objection

“Concrete cost is not inheritable across the [35] EndRing/OneEnd/Isogeny
cascade” is safe as a warning against automatic relabeling, but too absolute
if read literally. A reduction can, in principle, be instantiated with an
explicit number of calls, representation conversions, success probabilities,
restarts, and arithmetic costs. In that event a cost bound could be
transferred after a new reduction-aware analysis. What is not valid is to
transfer it merely because the reductions are polynomial-time or because the
source names SQIsign parameters.

This objection does not defeat the proposed correction; it identifies a
wording constraint. The successor should say **“not automatically inheritable
without a separate reduction-aware cost analysis.”** That wording preserves
the intended `SC-3` boundary while avoiding an unnecessarily universal
impossibility statement. The checkpoint correctly records the missing
concrete transfer issue (`BATCH-002.yaml:144-148`), and the correction
derivation's “pending a separate reduction-aware analysis” qualifier points
in the right direction.

## Is preserving `2^{120-123}` without recalculation honest?

### Strongest objection

The frozen Section 4.1 source does **not** produce `2^{120-123}`. It reports a
rough lower-bound table estimate of at least `2^106.5` `F_{p^2}` operations at
the NIST-I-sized parameter and memory at least `2^92.5`, under its stated
one-operation-per-entry and `P0` assumptions (`paper_fulltext.md:226-240`).
The `2^{120-123}` bracket is from the prior BATCH-046 toy-scale cost-model
refinement and its model-dependent conversion, not from the frozen source
itself (`concrete_cost_analysis.md:7-17`, `:33-56`; `red_team_concrete_cost.yaml:337-357`).

The prior model also carries unresolved objections rather than a single
settled arithmetic path: the earlier review records a toy-to-cryptographic
`B` regime mismatch, a `B=85` versus paper-optimized-`B` inconsistency, the
distinction between modular-polynomial neighbor enumeration and Velu
evaluation, and a model-dependent field-operation-to-AES conversion
(`red_team_concrete_cost.yaml:23-84`, `:89-121`, `:193-229`). This review does
not recompute or silently repair any of those issues.

### Falsification result

Preservation is honest only as provenance-preserving quotation:

> `2^{120-123}` is the prior record's un-recalculated, model-dependent
> OneEnd-side bracket, carried forward pending separate reduction-aware and
> numerical analysis.

That sentence records what the prior artifact said without converting it into
fresh evidence. It also keeps the prior toy-extrapolation, memory, and
conversion caveats visible. Preservation would fail if the successor:

- presented the bracket as obtained from Section 4.1;
- called it a direct SQIsign security value;
- implied that this review revalidated the bracket; or
- silently changed its endpoints or arithmetic interpretation.

The correction derivation explicitly chooses no numeric recalculation and
preserves the bracket only as a model-dependent OneEnd-side quantity. On that
precise reading, the no-recalculation rule is honest. The unresolved numeric
questions remain caveats, not reasons to invent a replacement value in this
qualitative review.

## Provenance and snapshot caveat

The snapshot receipt at
`coordination/goals/GOAL-SSI-001/batches/BATCH-d03e96/archives/TASK-20260809-6e8601/snapshot-receipt.json`
still records `pending_post_commit` with null `commit_sha` and empty
`path_sha256`. The dispatch queue supplies the post-commit binding, and the
declared snapshot commit `0fef3f904bd9abe5592e52028e4bc4fff5e42690` is
reachable with exactly the derivation and receipt paths; its derivation hash
matches the queue-bound hash. This is sufficient for this review's read-only
input binding, but the pending/null receipt fields should remain a visible
provenance caveat until the Coordinator's archive process supersedes them.

## Narrow conclusion

The qualitative correction should proceed only in this form:

1. Attribute the Section 4.1 estimate to the paper's Algorithm 3/OneEnd-side
   cost model, with its rough-underestimate and success-probability caveats.
2. Preserve the paper's SQIsign discussion as motivation and parameter
   relevance, but remove the inference that it is itself a direct SQIsign
   security or key-recovery result.
3. Carry `SC-1` as the separate GRH condition at the cited Isogeny reduction
   boundary, without claiming that Section 4.1 independently proves the
   reduction hypotheses.
4. Carry `SC-3` as a prohibition on automatic concrete-cost inheritance;
   phrase it so a future explicit reduction-aware analysis remains possible.
5. Quote `2^{120-123}` only as the predecessor's un-recalculated,
   model-dependent OneEnd-side bracket. Do not recalculate, endorse, or
   relabel it in this batch.

This verdict is limited to the qualitative correction and its provenance. It
does not decide the numerical bracket, any concrete security level, any
asymptotic exponent, any hypothesis status, or goal completion.

