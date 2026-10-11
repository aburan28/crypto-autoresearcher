# Analysis — EXP-CRYPTO-6505c6, review of audit TASK-20260913-c6df88

This is the Coordinator's `/review-evidence` analysis for the symbolic
proof-audit bundle at `experiments/EXP-CRYPTO-6505c6/audits/TASK-20260913-c6df88/`,
executed under the review plan pre-registered in
`ledger/handoffs/TASK-20260928-14fdee.yaml` (`review_plan`). That plan owns
two joints and a proves-too-much control, both discharged by the blind
re-derivation task `TASK-20260928-b9a4de` (`ledger/handoffs/TASK-20260928-b9a4de.yaml`),
whose full report is reproduced there and cited below.

Per AGENTS.md, this analysis is strictly separated into Observation /
Comparison / Inference / Limitation. Nothing here changes any status; the
Coordinator decision (`ledger/decisions/DEC-20260928-2f8c6b.yaml`) records
the official outcome.

## Observation

**What the bundle is.** `audit-manifest.yaml` records this as Stage 3 of a
3-stage pipeline: a literature digest (`coordination/design/BATCH-aa0d38/audits/TASK-20260913-0d9fe6/source-digest.md`)
formalized against `specification.yaml`'s frozen 160-cell obligation matrix
(16 symbolic cases x 10 obligation columns O01-O10) and 400-cell chart-pair
coverage matrix (16 cases x 25 ordered addition-chart pairs), with no new
primary-source reading performed by this task itself. All 20 declared root
files are present (confirmed against `audit-manifest.yaml.root_files`).

**Internal consistency, checked directly (not trusted from prose):**

- `obligation-results.yaml` contains exactly 160 rows. Status counts:
  `CERTIFIED` 30, `REFUTED` 6, `OPEN` 112, `NOT_APPLICABLE_WITH_CERTIFICATE`
  12. Sum = 30+6+112+12 = 160. This matches the file's own `status_tally`
  block and matches `checker-results.yaml`'s `obligation_status_tally`.
- `chart-coverage.yaml` contains exactly 400 rows. Status counts:
  `CERTIFIED` 216, `OPEN` 32, `NOT_APPLICABLE_WITH_CERTIFICATE` 152. Sum =
  216+32+152 = 400, matching its own `status_tally` and
  `checker-results.yaml`'s `chart_status_tally`.
- `open-obligations.yaml`'s own group-by-group cell-count cross-check (112
  obligation cells across 14 named groups, 32 chart cells across 2 named
  groups) sums correctly by direct arithmetic. This is the same 112/32
  figure `audit-report.md` states in prose ("112 of 160 obligation cells
  and 32 of 400 chart cells"). **No discrepancy found between the prose
  summary, the two per-file status tallies, and open-obligations.yaml's
  independent grouping.**
- `checker-results.yaml` is itself a structural self-check (explicitly not
  the required independent semantic review) and reproduces the same
  tallies, plus anchor/DAG/case-order checks, all `pass: true`. It
  correctly and repeatedly disclaims that structural pass upgrades any
  OPEN cell.
- `counterexamples.yaml` (CTREX-01, CTREX-02) and `control-results.yaml`
  agree on the case-15/case-16 (constant-sheaf) rejection: both cite the
  same derivation (`S_{F,n}(Q,R) = c^2 |E(F_{p^n})|` for constant trace
  `c`, giving `sum |S|^4 ~ c^8 q_n^6`, violating the required `<= B q_n^5`
  for any n-independent `B`), and `obligation-results.yaml`'s O06/O07/O08
  rows for case-15/case-16 cite the identical corrected figures (`c^8`, not
  `c` or `c^2` alone — a documented in-bundle correction from
  `TASK-20260913-627c97` is consistently propagated across all three
  files, not left stale in one). This is the required known-false control
  (`specification.controls.constants`) and it is REFUTED as expected — an
  instrument-validation result, not evidence about family K or L (see
  Inference).
- `case-index.yaml` lists exactly the 16 cases specification.yaml defines,
  with the same `case_order` as `obligation-results.yaml`,
  `chart-coverage.yaml`, and `checker-results.yaml`.
- `artifact-sha256.json` lists SHA-256 hashes for all 19 other root files
  (well-formed 64-hex-character digests for each). **Not independently
  recomputed in this review round** — flagged in Limitations, not silently
  assumed.

**No defect found.** The two headline findings (`audit-report.md` "The two
headline findings, carried forward") are stated consistently across
`audit-manifest.yaml`, `open-obligations.yaml` (HEADLINE-GAP-01,
HEADLINE-GAP-02), `moment-certificates.yaml`, and every individual OPEN row
in `obligation-results.yaml` that cites `GAP-O06-EFFECTIVENESS`,
`GAP-O01-K`, or `GAP-O01-L`. Per-family outcome: **both K and L are
INCONCLUSIVE**, not `CERTIFIED_MAIN_SCOPE` and not
`EXACT_MAIN_COUNTEREXAMPLE`; the overall classification is INCONCLUSIVE for
both families, correctly not escalated to `specification.outcomes.partial`
since neither family is certified. `independent_review_status: NOT YET
PERFORMED` is stated plainly in `audit-manifest.yaml`, matching
`specification.independent_checker_plan`'s requirement that the semantic
review is a separate task from this formalization pass.

## Comparison

The review plan (`TASK-20260928-14fdee`) owned two joints and one
proves-too-much control, all assigned to a single blind re-derivation task
(`TASK-20260928-b9a4de`) that fetched `arXiv:2511.09459v1` directly (abs
page, HTML rendering, and the raw PDF converted to text in an isolated
venv) and read it itself — explicitly not opening this audit bundle, the
source digest, or `TASK-20260913-4e7c6d` (blindness: mutual, per the plan).

**Joint 1 (Theorem 2.4 ineffectiveness).** Audit's own finding
(`open-obligations.yaml` HEADLINE-GAP-01, `moment-certificates.yaml`): no
explicit formula for Theorem 2.4's implicit constant in terms of
`(d, c(M))` anywhere retrievable; Remark 1.2 disclaims polynomial/effective
dependence. Blind task's independent finding: **CONFIRMED**, at high
confidence, quoting Theorem 2.4's conclusion (4) verbatim ("the implicit
constant depends only on d and c(M)" — existential, no formula) and
Remark 1.2 verbatim ("whereas the latter provides estimates where the
dependency on the complexity ... is polynomial, this is not the case in
this paper"). The blind task additionally checked the proof of Theorem 2.4
itself (citing "[27, Lemma 6.26]" and Xu's Theorem 3.5) and grepped the
whole paper for "effective"/"explicit", finding no effective version
anywhere, including no undisclosed appendix. This is a **strictly
stronger** confirmation than the audit bundle itself had (which never
re-read the primary source at this stage; it formalized a prior digest).

**Joint 2 (Family L absence).** Audit's own finding (HEADLINE-GAP-02): the
paper never mentions "Legendre" or the Legendre elliptic-curve family under
any name, confirmed by "a dedicated negative search" in the digest chain.
Blind task's independent finding: **CONFIRMED**, via an exhaustive
full-text search of all 57 pages (~126,000 characters) for "Legendre",
"Legendre family", "Legendre normal form", and the equation patterns
`z(z-1)(z-u)`/`x(x-1)(x-u)` — zero matches anywhere, including in Section 9
("examples of trace functions"), the paper's own dedicated worked-examples
section, which discusses hypergeometric, Kloosterman-type, orthogonal-
monodromy and finite-monodromy sheaves but never a Legendre-family
construction under any name.

**Proves-too-much control (Family K / quadratic Kummer sheaf).** The
review plan required checking that the same blind search methodology could
find a known-present object, since there is no independently-known-false
mathematical object to substitute in a literature-presence check. Result:
**PASSED**. The blind task found the same "bare notation" `L_chi` the
audit itself reported (quoting the identical passage from Section 2, just
before Proposition 2.3: "we use the usual notation L_psi or L_chi for the
associated Artin-Schreier or Kummer sheaf") and confirmed no dedicated
quadratic-specialization treatment exists beyond that generic notation —
this **matches the audit's own prior characterization exactly**, and the
fact that the method surfaced a real (if minimal) match validates that the
methodology is not simply blind to everything; the Family L negative is
not attributable to search-shallowness.

**Net comparison result.** All three items the review plan pre-registered
BEFORE the blind task ran are corroborated by a genuinely independent,
methodologically-blind read of the primary source, at a stated
`coordinator_prior` of ~75% (joint 1) and ~50-60% (joint 2, the weaker one
specifically flagged as vulnerable to a same-object-different-name failure
mode). The weaker joint (2) is the one that came back most strongly
confirmed (exhaustive search of the paper's own dedicated examples
section, not merely a keyword grep).

## Inference

The audit bundle's own **INCONCLUSIVE for both families** classification
is internally consistent (Observation) and its two load-bearing findings
are now independently corroborated (Comparison), rather than resting only
on an unverified digest chain as `audit-manifest.yaml` itself flagged
("scope_and_capability_boundary": this task had no web_search/WebFetch
capability and formalized the digest as given). This strengthens the basis
for the two headline findings specifically — Theorem 2.4's implicit
constant is stated ineffectively, and Family L does not appear in this
cited source — without changing the audit's own verdict: **no exact
counterexample to either main-target claim was found or manufactured, and
no certificate for either family was produced.** `INCONCLUSIVE` (not
`EXACT_MAIN_COUNTEREXAMPLE`, not `CERTIFIED_MAIN_SCOPE`) remains the only
outcome the evidence supports for both K and L, per
`specification.falsification_criterion` ("absence of proof cannot refute
the main target").

This review therefore does **not** change any per-family classification,
any per-cell obligation status, or the overall audit verdict. What it adds
is independent verification of the two facts the audit's 112 OPEN cells
are overwhelmingly downstream of (`open-obligations.yaml`'s cross-check:
O06 alone accounts for 14 of 112 OPEN obligation cells directly, and gates
a further 28 O07/O08 cells; the family-L-absence finding accounts for 7
O01 cells directly and gates every downstream O02-O04/O07/O09 cell for
family L). Per `docs/claims-and-verification.md`'s refutation-artifact
ladder, these two findings — quoted verbatim from a genuinely
independently fetched primary source, reasoned through step by step, and
archived in this document — now meet the `derivation` bar (a written,
self-contained, independently checkable argument) for **those two specific
findings**, which is a stronger basis than the `empirical_only`/digest-
chain basis they had before this review. This is recorded in
`ledger/evidence/EV-CRYPTO-4a91d7.yaml`'s `proof_status`; it is not a proof
of anything about ECDLP, and it does not discharge or certify any
obligation cell — Theorem 2.4's implicit constant remains genuinely
ineffective in this source, and family L's classical properties remain to
be supplied from elsewhere.

## Limitation

- **Scope of this review round.** This review verified: (a) the internal
  consistency of the audit bundle's own tallies, cross-checks, and
  headline-finding propagation across files (Observation), and (b) an
  independent, blind re-derivation of exactly the two headline findings
  plus one proves-too-much control (Comparison). It did **not**
  independently re-verify the other 110+ OPEN cells (Sections 5-6's
  moment-bound proof for gallant sheaves; Sections 3.1-3.2's Goursat's
  Lemma / coinvariant-vanishing criterion, named but unretrieved by the
  original digest chain and not re-checked here; the "n vs d"
  transcription ambiguity in Theorem 2.4 conclusion (3); family K's
  classical rank/purity/ramification facts beyond bare notation; the
  off-diagonal shared-locus dimension for case-05/case-06; the
  matched-null certificates for case-07/case-08). Those remain exactly as
  OPEN as the audit bundle itself records, with their own disclosed
  missing prerequisites in `open-obligations.yaml` — this review neither
  closes nor reopens them, and no broader coverage should be inferred from
  this round.
- **Hash verification not performed.** `artifact-sha256.json`'s 19 listed
  digests were checked for presence and well-formedness (64 hex characters
  each, one entry per other root file) but not recomputed against the
  actual file bytes in this review round. This is a structural gap in this
  review, not a finding about the bundle.
- **The blind task's own access caveat stands.** `TASK-20260928-b9a4de`
  fetched the v1-tagged PDF specifically (noting the unversioned URL
  currently resolves to v3) and converted it with `pypdf` in an isolated
  venv; this is a direct, independent read of the primary source text, but
  it is still a single read by a single (LLM-mediated) session, not a
  second independently-typeset cross-check or a human mathematician's
  verification of the surrounding proof.
- **This review draws no adverse conclusion about H-CRYPTO-fde1f1 itself.**
  The obstruction identified is scoped to **this one cited source**
  (arXiv:2511.09459v1) supplying an effective Theorem-2.4-type bound and
  Family L's definition — not to the hypothesis's transfer-target claim in
  general. `audit-report.md`'s own "Launch gate and next steps" names an
  independent derivation or a different, more foundational source for both
  gaps as the concrete next step, ahead of a full independent semantic
  review of whatever remains open; this review does not foreclose that
  path.
- **certificate.kind.** This experiment is a zero-run symbolic proof audit
  (`specification.budget.maximum_numerical_runs: 0`); it claims no
  discrete-log solve, decomposition, or key recovery anywhere in the
  bundle (checked: no `certificate:` block asserting `kind` other than
  `none` appears in any of the 20 files, and `audit-report.md` explicitly
  disclaims being an independently reviewed result). `certificate_refs: []`
  / certificate-tier `none` in the evidence record is therefore the
  correct, honest classification, not an understatement of a stronger
  claim made elsewhere in the bundle.
