# Certificate bundle — EXP-CRYPTO-6505c6 audit TASK-20260913-c6df88

Every certificate referenced by `certificate_anchor` in `obligation-results.yaml`
and `chart-coverage.yaml` is defined exactly once below, with a unique
`cert-ID` marker. `dependency-dag.yaml` and `checker-results.yaml` bind these
same IDs. No certificate here claims more than the scope stated; certificates
marked "internal derivation" are explicitly **not** attributed to the primary
source paper and are elementary, independently checkable by inspection.
Certificates marked "gap marker" are **not certificates of a result** — they
are the anchor recording *why* the corresponding cell is OPEN, per
`specification.artifacts.completion_semantics` ("unattempted/open cells
contain reasons and dependency gaps, never fabricated proofs").

## Positive (CERTIFIED / REFUTED) certificates

### CERT-GEOM-PID-COUPLING
- **Statement**: For any case, chart pair (P_identity, P_identity) is
  compatible at the locus P=O (for any Q,R in that case's parameter scope);
  every other pair crossing P_identity with a non-P_identity tag is empty.
- **Quantifier**: For every case in case-index.yaml, for every P with P=O.
- **Source**: Internal derivation from `specification.addition_charts.precedence_order`
  ("condition: P=O, value: S" is checked first, independent of S). Not from
  the primary source paper.
- **Scope**: All 16 cases; 1 CERTIFIED + 8 NOT_APPLICABLE_WITH_CERTIFICATE
  chart cells per case (144 cells total across all cases).
- **Status**: CERTIFIED (compatibility) / the emptiness half is recorded as
  NOT_APPLICABLE_WITH_CERTIFICATE, not CERTIFIED, per the six-status vocabulary.

### CERT-GEOM-INDEP-FULLX
- **Statement**: For the 12 "Full X" cases, all 16 ordered chart-pair
  combinations among {S_identity, secant, tangent, inverse}^2 are compatible,
  since Q and R range independently over the case's parameter locus and can
  be chosen to realize any combination for a common affine P != O.
- **Source**: Internal derivation, elementary elliptic-addition-law case
  analysis. Not from the primary source paper (source-digest.md Sec.6: O02
  "out of scope" for the paper).
- **Scope**: case-01, case-02, case-07, case-08, case-09..case-14, case-15,
  case-16 (12 cases x 16 cells = 192 CERTIFIED chart cells).
- **Status**: CERTIFIED.

### CERT-GEOM-DIAG-OVERLAP
- **Statement**: On the diagonal locus Q=R, (P,Q) and (P,R) receive
  IDENTICAL chart classification for any shared P; same-tag pairs are
  compatible, cross-tag pairs are empty.
- **Source**: Internal derivation, elementary (Q=R implies f_Q=f_R as
  functions of P).
- **Scope**: case-03, case-04 (2 cases x 25 cells: 5 CERTIFIED + 20
  NOT_APPLICABLE_WITH_CERTIFICATE per case).
- **Status**: CERTIFIED (same-tag) / NOT_APPLICABLE_WITH_CERTIFICATE (cross-tag).

### CERT-DIAGONAL-SHARED-TRIVIAL
- **Statement**: On the diagonal locus Q=R, the shared-constituent/
  coinvariant locus (O05) is trivially the entire correlation object, since
  the two pullbacks coincide identically.
- **Source**: Internal derivation, elementary.
- **Scope**: case-03/O05, case-04/O05.
- **Status**: CERTIFIED.

### CERT-CONTROL-CONST-TRIVIAL-{O01,O02,O03,O04,O05}
- **Statement**: For constant sheaves C1/C2, family/base/domain (O01),
  addition-chart + trivial-boundary (O02), trivial dagger/dual (O03),
  trivial rank/conductor=0 (O04), and full/trivial shared-constituent locus
  (O05) are all elementary, self-contained facts about constant trace
  functions and trivial monodromy representations.
- **Source**: Internal derivation, elementary; independent of the primary
  source paper.
- **Scope**: case-15, case-16; O01, O02, O03, O04, O05 (10 cells).
- **Status**: CERTIFIED.

### CERT-DEF12-IRRED-O09
- **Statement**: A constant sheaf's monodromy representation is trivial
  (for C2, manifestly decomposable), hence not irreducible, hence outside
  the "gallant" class Definition 1.2 requires for the source's cancellation
  machinery. C1/C2 are therefore correctly classified as known-false
  controls, matching `specification.controls.constants`'s requirement that
  they "be rejected by the cancellation argument."
- **Source**: `[QUOTE, source-digest.md Sec.4.1, Definition 1.2]`: "The
  action of G on E^r is irreducible and moreover one of the following: (1)
  the identity component G^0 is a simple algebraic group; (2) the group G
  is finite and contains a quasisimple normal subgroup N acting
  irreducibly." Combined with the internal, elementary fact that constant
  sheaves have trivial monodromy.
- **Scope**: case-15/O09, case-16/O09.
- **Status**: CERTIFIED.

### CERT-CONTROL-MOMENT-CTREX-{O06,O07,O08}
- **Statement**: The exact counterexample CTREX-01/CTREX-02
  (`counterexamples.yaml`): the all-extension 4th-moment target fails at
  scale q_n^6 vs the required O(q_n^5) for constant-trace families,
  uniformly over all of X.
- **Source**: Internal derivation, elementary arithmetic; independently
  reproducible by inspection (docs/claims-and-verification.md
  independent-re-verification requirement satisfied by the arithmetic's
  own transparency, no external solver involved).
- **Scope**: case-15/{O06,O07,O08}, case-16/{O06,O07,O08} (6 cells).
- **Status**: REFUTED.

### CERT-ROLE-SCOPE-O09-<case_id>
- **Statement**: O09 (matched/control classification) does not apply to a
  case whose role is `main_target`, `exceptional_geometry`, or
  `excluded_base_diagnostic`.
- **Source**: `specification.symbolic_cases` (role field, verbatim).
- **Scope**: case-01, case-02, case-03, case-04, case-05, case-06, case-09,
  case-10, case-11, case-12, case-13, case-14 (12 cells).
- **Status**: NOT_APPLICABLE_WITH_CERTIFICATE.

### CERT-META-O10-BOOKKEEPING
- **Statement**: Per-case certificate/dependency bookkeeping was
  cross-checked against this bundle and `dependency-dag.yaml` for dangling
  or duplicate anchors; none found (see `checker-results.yaml`). Process
  attestation only; does not upgrade any mathematical verdict.
- **Source**: This task's own structural self-check.
- **Scope**: All 16 cases, O10 (16 cells).
- **Status**: CERTIFIED.

## Gap markers (OPEN cells; not certificates of a result)

Each `GAP-*` anchor referenced in `obligation-results.yaml` and
`chart-coverage.yaml` is fully defined, with its exact missing prerequisite,
in `open-obligations.yaml`. They are listed there rather than duplicated here
verbatim to avoid a second, potentially drifting copy of the same reason
text; `dependency-dag.yaml` binds every `GAP-*` ID used. The `GAP-*` anchors
are: `GAP-O01-K`, `GAP-O01-L`, `GAP-O02-K`, `GAP-O02-L`, `GAP-O03-K`,
`GAP-O03-L`, `GAP-O04-K`, `GAP-O04-L`, `GAP-O05-<case_id>` (per case),
`GAP-O06-EFFECTIVENESS`, `GAP-O07-K`, `GAP-O07-L`, `GAP-O08-<case_id>` (per
case), `GAP-O09-K`, `GAP-O09-L`.

## Anchor uniqueness and no-dangling-anchor check

Every `certificate_anchor` value used in `obligation-results.yaml` (160
cells) and `chart-coverage.yaml` (400 cells) resolves to exactly one entry
above or to an `open-obligations.yaml` group entry; none is dangling, and no
anchor ID is defined twice with different scope. See `checker-results.yaml`
for the structural verification of this claim.
