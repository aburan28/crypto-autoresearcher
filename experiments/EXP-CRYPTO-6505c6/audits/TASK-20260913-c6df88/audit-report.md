# Audit report — EXP-CRYPTO-6505c6, TASK-20260913-c6df88

## What this document is, and is not

This report formalizes `specification.yaml`'s frozen 160-cell obligation
matrix and 400-cell chart-coverage matrix using
`coordination/design/BATCH-aa0d38/audits/TASK-20260913-0d9fe6/source-digest.md`,
a literature digest of the cited primary source
(arXiv:2511.09459v1, Fouvry–Kowalski–Michel–Sawin, "Bilinear forms with
trace functions"). This task performed **no new reading** of the primary
source, no numerical computation, and no code execution beyond reading and
authoring these 20 files.

**These verdicts are this task's own best-effort formalization. They are
NOT yet an independently reviewed result.**
Per `specification.independent_checker_plan.semantic_output`, an independent
qualified review task is required before any of these statuses can be
treated as a checked mathematical fact; this task's own structural
self-check (`checker-results.yaml`) explicitly disclaims performing that
review. Readers should treat every `CERTIFIED` and `REFUTED` verdict below
as "certified/refuted by this task's own elementary reasoning or by direct
formalization of the digest," not as a claim independently checked by a
second party.

## The two headline findings, carried forward

1. **Theorem 2.4 is stated ineffectively.** No explicit formula for its
   implicit constant (dependent on `d, c(M)`) exists anywhere retrievable in
   the paper; Remark 1.2 explicitly disclaims polynomial/effective
   dependency for this paper's own method. This is independently
   corroborated across two prior passes (`TASK-20260913-4e7c6d`,
   `TASK-20260913-0d9fe6`). Per `specification.main_transfer_target.effective_B`,
   this means obligation **O06 is OPEN for every family-K/L case**, and
   every O07/O08 cell that would depend on a certified effective bound is
   OPEN too. See `moment-certificates.yaml`, `open-obligations.yaml` HEADLINE-GAP-01.
2. **Family L ("Legendre R¹") does not appear anywhere in the cited primary
   source**, confirmed by a dedicated negative search. Every case row using
   family L (case-02, case-04, case-06, case-08, case-10, case-12, case-14)
   carries an **OPEN**, not `REFUTED` or `CERTIFIED`, status for its
   family-specific obligations (O01 and everything downstream of it) — the
   obligation still applies to a required main-target family; it is simply
   unmet from this source. See `open-obligations.yaml` HEADLINE-GAP-02.

Both findings are stated plainly rather than softened, per this task's
handoff.

## What was actually resolved by this task, without the paper

A meaningful fraction of the panel does **not** depend on the primary
source at all, and this task resolved those cells directly:

- **Addition-chart geometry (O02's compatibility sub-claim, and all 400
  chart-coverage cells' compatibility/emptiness status)**: elementary
  Weierstrass-addition-law case analysis from `specification.addition_charts`'s
  own precedence order. CERTIFIED for the P-identity coupling fact (every
  case) and for all 16 non-identity chart combinations in every "Full X"
  case; CERTIFIED/empty for the diagonal case-03/case-04; left OPEN only
  for the 16 non-identity combinations in the two off-diagonal
  shared-locus cases (case-05, case-06), where the locus itself is
  unresolved (O05).
- **The diagonal cases' shared-constituent locus (O05, case-03/case-04)**:
  trivially the entire object, since `Q=R` forces the two pullbacks to
  coincide. CERTIFIED without needing the unretrieved Goursat's-Lemma
  material.
- **The constant-sheaf controls (case-15, case-16)**: every obligation
  except O06/O07/O08 is elementary (trivial rank/conductor, trivial
  dagger/dual, trivial full-support shared locus) and CERTIFIED directly.
  O06/O07/O08 are REFUTED by an exact, elementary counterexample: the
  required all-extension 4th moment fails at scale `q_n^6` against the
  required `O(q_n^5)`, uniformly across all of X — exactly the rejection
  `specification.controls.constants` requires of a known-false control
  (see `counterexamples.yaml` CTREX-01/CTREX-02).
- **O10** (certificate/dependency bookkeeping) is CERTIFIED uniformly as a
  process attestation; it does not upgrade any mathematical verdict.

## What remains genuinely open, and why

The bulk of the panel — **112 of 160 obligation cells and 32 of 400 chart
cells (144 total)** — is OPEN, not because this task declined to work them,
but because the exact prerequisite each depends on is missing from the
cited source (or, for family L, from the source entirely). Every OPEN cell
is listed with its precise missing prerequisite in `open-obligations.yaml`;
none is a vague "needs more work." The largest single blocking gap is the
unretrieved Sections 5–6 of the primary source (the actual moment-bound
proof for gallant sheaves and its application to conclude the main
theorems) and the unretrieved Sections 3.1–3.2 (Goursat's Lemma / the
coinvariant-vanishing criterion), both disclosed as gaps by the digest
itself, not manufactured by this task.

## Matched-null and control admission gate

Per `case_order`, the known-false cancellation controls (case-15, case-16)
were worked first and correctly REJECTED (see `control-results.yaml`). The
matched-null cases (case-07, case-08) were worked next; per
`specification.controls.matched_nulls`'s own rule ("Missing required
matching certificate means OPEN and overall inconclusive, not N/A"), both
are recorded OPEN, not forced to a favorable match and not treated as N/A.

## Per-family outcome

Per `specification.outcomes.per_family` (`CERTIFIED_MAIN_SCOPE`,
`EXACT_MAIN_COUNTEREXAMPLE`, `INCONCLUSIVE`, `INVALID_ARGUMENT`):

- **Family K: INCONCLUSIVE.** The main-target case (case-01) and every
  supporting case using K (case-03, case-05, case-07, case-09, case-11,
  case-13) has O06 (moment/effective-B) OPEN due to Theorem 2.4's
  ineffectiveness, and O01 (family-specific rank/purity/ramification) OPEN
  because the source supplies only bare notation for `L_chi`, not the
  quadratic specialization's properties. No exact counterexample to the K
  main-target claim was found (none is fabricated here either).
  `specification.success_criterion` requires "complete source-matched,
  independently checkable certificates for the all-extension effective
  moment and its valid stratification consequences" — not met.
  `specification.falsification_criterion`'s "absence of proof cannot refute
  the main target" applies equally: this is not `EXACT_MAIN_COUNTEREXAMPLE`
  either. INCONCLUSIVE is the only outcome the evidence supports.
- **Family L: INCONCLUSIVE**, for a strictly stronger reason than K: family
  L does not appear in the cited source at all (Finding 2 above), so every
  L-specific obligation (O01 and everything chained from it: O02, O03, O04,
  O07, O09) is OPEN in addition to O06's shared ineffectiveness gap. As with
  K, no exact counterexample to the L main-target claim was found or
  fabricated.

## Overall classification

Per `specification.outcomes.partial` ("One family can be certified while
the other remains open; do not convert that into overall success") — this
does not even reach the partial case, since **neither** family reaches
`CERTIFIED_MAIN_SCOPE`. The overall outcome for this audit pass is
**INCONCLUSIVE for both families**, not `CERTIFIED_MAIN_SCOPE` and not
`overall_positive`. This is the honest reading of what the digest and
specification actually support; it is not stretched toward a more
complete-sounding classification. The degeneration/excluded-base diagnostic
cases (case-09 through case-14) are correctly scoped and classified (mostly
OPEN, for the same family-specific reasons as the main cases) and, per
`specification.obligation_matrix.diagnostic_rule`, their open status
"cannot refute the main target alone" — it is recorded, not treated as a
refutation.

## Launch gate and next steps

Per `specification.launch_gate`, this audit does not authorize, approve, or
claim any scientific breakthrough. The concrete next actions, in order of
what would most reduce the largest disclosed gaps, are: (1) an independent,
direct-access (non-LLM-mediated) reading of the primary source's Sections
5–6 and 3.1–3.2, and a resolution of the "n vs d" transcription ambiguity in
Theorem 2.4 conclusion (3); (2) an independent derivation or a different,
more foundational source for family K's classical Kummer-sheaf properties
and, separately and more substantially, for family L's entire definition,
since it is absent from this source; (3) only after (1)–(2), a genuine
independent qualified semantic review of whatever this bundle's OPEN cells
resolve to.
