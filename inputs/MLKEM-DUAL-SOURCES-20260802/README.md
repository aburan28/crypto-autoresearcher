# TASK-20260802-101 source package

This package records the primary-source retrieval and bounded adjudication for
GOAL-MLKEM-003 / BATCH-007. It is literature and source-code provenance only;
it is not a run, a security estimate, or an ML-KEM break claim.

## Retrieved material

- Carrier–Meyer-Hilfiger–Shen–Tillich, ePrint 2022/1750: the current landing
  page and revision metadata, plus the accessible HAL `hal-05406481v1`
  document. The ePrint page says `2025-06-11: last of 3 revisions`. The HAL
  PDF is 1,252,838 bytes with SHA-256
  `083b142256eecaebfa72dfccf847151b2175666a3979cef4e7383376757b8005`, which
  is byte-identical to the pinned `origin/main` comparison artifact. Only the
  front matter, Table C.2 region, and the Pgood-threshold paragraph are kept;
  the full PDF is not duplicated here. The direct ePrint PDF and revision
  archive both returned HTTP 403 and remain explicitly unretrieved.
- NIST FIPS 203 final, published 2024-08-13: landing page and PDF were
  retrieved. The selected text records the standard identity, date, and its
  ML-KEM scope; the full PDF is not duplicated here.
- Ducas–Pulles ePrint 2023/302: landing page was retrieved. The direct ePrint
  PDF returned HTTP 403 and is recorded as unretrieved. The authors' accessible
  CWI version-of-record full text
  (2025-11-20) was retrieved as a supplemental primary source for the score
  distribution and measurement-scope check; only selected loci are retained.
- MATZOV, `Zenodo-6412487-v1` and `Zenodo-6493704-v2`: metadata and report
  PDFs were retrieved; selected abstract/Table-1/distinguisher loci are
  retained rather than duplicating the PDFs.
- Guo–Johansson, ASIACRYPT 2021 LNCS 13093, pp. 33–62: the IACR proceedings
  PDF and selected text were retrieved.
- `kevin-carrier/CodedDualAttack`: GitHub API resolved `main` to
  `9c1367f85d26038244bc83c025d84c0b7006f2ee`; the relevant current-head
  `FFT_sample.py` and `Algorithm.py` were retrieved. The FFT file is
  byte-identical to the pinned `origin/main` vendor-lock file.

Every attempted source has one record in `provenance.json` with URL, HTTP
status where applicable, UTC retrieval time, byte count, SHA-256 for retrieved
content, revision identifier, and either `retrieved` or `unretrieved` status.

## Reuse boundary

The exact HAL PDF and optimizer artifacts in
`experiments/EXP-MLKEM-010/vendor-lock/` were read from `origin/main` only and
were not modified. No ledger, prior batch, experiment, finding, or open-problem
record was edited. The extracted loci are sufficient to reproduce the three
adjudication questions; they must not be reused as fresh empirical runs.

The initial script invocation failed before writing any source file because
the Python TLS stack could not verify the local CA certificate. That
infrastructure failure was preserved in the execution narrative; the script
was corrected to use the repository host's working `curl` transport, and the
successful bounded invocation is the one recorded in `provenance.json`.
