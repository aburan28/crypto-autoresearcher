# Sources note — TASK-20260731-012 (GOAL-FAEST-001, BATCH-001)

Task: obtain the FAEST Round-3 specification and reference implementation
from primary sources, verify each citation, and file four KN-LIT entries
(KN-LIT-7637, KN-LIT-7638, KN-LIT-7619..7620) plus this note. Executed 2026-07-31.

## Headline finding

**There is no published FAEST Round-3 specification as of 2026-07-31.**
The latest published FAEST specification is **v2.0** (the Round-2 NIST
submission document, https://faest.info/faest-spec-v2.0.pdf). NIST's
Additional Digital Signatures process gives Round-3 teams until
**2026-08-14** to submit updated specifications/implementations ("tweaks"),
and those are not public yet. KN-LIT-7637 therefore files the verified v2.0
specification and records the Round-3 gap explicitly; it is NOT filed as a
Round-3 document. All other requested sources were obtained and verified.
The Coordinator should NOT pause the goal: the verified v2.0 spec + faest-ref
implementation + IR 8610 roster are sufficient primary-source grounding for
BATCH-001's ideation, with the Round-3 tweak pending tracked as a caveat.

## URLs fetched and results

| # | URL | Result | Notes |
|---|-----|--------|-------|
| 1 | https://faest.info | 200 (rendered markdown) | Landing page: design, variants, performance table, team contact |
| 2 | https://faest.info/resources.html | 200 (rendered markdown) | Spec versions v1.0/v1.1/v2.0; Round-2 submission bundle (Google Drive, 49 MB); Round-1 bundle (GitHub release zip); Crypto 2023 paper link |
| 3 | https://faest.info/faest-spec-v2.0.pdf | 200 (raw PDF bytes) | `%PDF-1.5` header observed; body text NOT extractable by this runtime's fetch pipeline (binary dump saved by runtime); identity/version confirmed by resources page |
| 4 | https://faest.info/authors.html | 200 (rendered markdown) | 12-member team roster, matches NIST Round-3 submitter list |
| 5 | https://eprint.iacr.org/2023/996 | 200 (rendered) | Full metadata + abstract for the VOLEitH/FAEST paper; "major revision of an IACR publication in CRYPTO 2023"; approved 2023-06-27 |
| 6 | https://github.com/faest-sign/faest-ref | 200 (rendered HTML) | Repo page: README, MIT license, 1,523 commits, 12 parameter-variant dirs, meson build |
| 7 | https://github.com/faest-sign/faest-ref/commits/main.atom | 200 (raw XML) | HEAD `2a2c36d96f8e6d2b7acda341741892099e8c5cc1` (2026-07-24); version 2.0.5 bump `55b52681b4d962df9f55f4e403a68bca98b10d37` (2026-07-02) |
| 8 | https://csrc.nist.gov/projects/pqc-dig-sig/round-3-additional-signatures | 200 (rendered) | Round-3 program page: nine candidates, FAEST submitter list, HAWK withdrawal note, page updated 2026-07-29. **This URL previously returned proxy CONNECT 403 per RQ-FAEST-001 provenance; reachable in this session** |
| 9 | https://csrc.nist.gov/pubs/ir/8610/final | 200 (rendered) | IR 8610 final page: title, 16 authors, abstract, DOI 10.6028/NIST.IR.8610, PDF at nvlpubs.nist.gov/nistpubs/ir/2026/NIST.IR.8610.pdf, history 05/14/26 final |
| 10 | websearch (corroboration only) | n/a | Confirms no Round-3 FAEST spec published; Round-3 tweaks due 2026-08-14 (secondary: boilerroom.dev 2026-05-15, projecteleven.com, postquantum.com, thequantuminsider.com; primary NIST news page nist.gov/news-events/news/2026/05/... found but not fetched) |

Fetch order followed the handoff's source-preference order (faest.info spec
-> NIST round-3 page -> faest-sign GitHub). The eprint URL (primary source
for the paper) was fetched in parallel. No URL in the declared set was
unreachable.

## Versions / identities recorded

- FAEST specification: **v2.0** (Round-2 submission; latest published).
  v1.1 (2023-07-04 per search metadata), v1.0 (Round 1) exist but are
  superseded for experimental purposes.
- faest-ref: version **2.0.5**, HEAD `2a2c36d96f8e6d2b7acda341741892099e8c5cc1`
  on `main` at fetch time; MIT license. Moving target — runs must pin a commit.
- FAEST paper: eprint **2023/996**, CRYPTO 2023, 7 authors.
- NIST IR 8610: final 2026-05-14, DOI 10.6028/NIST.IR.8610.

## Checksums

**None computed.** This runtime exposes no command execution (no shell
tool), so no SHA-256 (or other) checksums of the fetched PDFs or pages could
be computed, and none are fabricated here. Per-path SHA-256 of the five
filed artifacts will be recorded by the snapshot archive task
(TASK-20260731-013) in its snapshot-receipt.json. HTTP-level identity
evidence recorded instead: `%PDF-1.5` magic header for the spec PDF, atom
feed commit IDs for the repo, and page metadata for CSRC/eprint.

## Rendered vs raw sources

- **Rendered pages**: faest.info landing/resources/authors pages, GitHub
  repo HTML page, csrc round-3 program page, csrc IR 8610 publication page,
  eprint landing page (all fetched through the web-fetch pipeline as
  markdown/text).
- **Raw bytes**: the spec PDF (`faest-spec-v2.0.pdf`, raw PDF served over
  HTTPS; binary, not text-extracted) and the GitHub atom commit feed (raw
  XML).
- **No git objects were fetched or cloned locally.** No local clone, build,
  or run of faest-ref was performed. "Raw git objects" copies were not
  possible in this session; this is recorded so later tasks do not assume a
  local tree exists.

## Citation_verified disposition

| Entry | Source | citation_verified | Basis |
|-------|--------|-------------------|-------|
| KN-LIT-7637 | faest.info spec v2.0 | **true** (for the v2.0 document) | PDF fetched 200 + `%PDF-1.5` header; identity/version from resources page. **Caveat in body: no Round-3 spec exists; this is v2.0** |
| KN-LIT-7638 | eprint 2023/996 | **true** | Landing page fetched 200; full metadata + abstract read |
| KN-LIT-7619 | faest-ref | **true** | Repo page + atom feed fetched 200; HEAD and version recorded |
| KN-LIT-7620 | NIST IR 8610 | **true** | CSRC publication page fetched 200; metadata + abstract read; round-3 program page (fallback) also fetched 200 |

No entry carries `citation_verified: false` because every declared primary
source that exists was actually fetched and checked. The only obstruction is
the nonexistence of a Round-3 FAEST spec, recorded as the headline finding
above and inside KN-LIT-7637.

## Inference metadata

- requested_policy: `research-deep`
- resolved model identifier (per runtime): `opencode/deepseek-v4-flash-free`
- reasoning_effort: null (policy default)
- fallback_allowed: false; fallback_used: none reported to this session
- degraded_allowed: false; no inference amendment requested
- independent_session_required: false (per handoff); session independence:
  this session executed only TASK-20260731-012; no lineage shared with any
  other task's session.

## Official state

No experiment, hypothesis, evidence, or decision record was created.
No official research state was changed. This task produced exactly its five
declared artifacts:
`knowledge/literature/KN-LIT-7637.md`, `knowledge/literature/KN-LIT-7638.md`,
`knowledge/literature/KN-LIT-7619.md`, `knowledge/literature/KN-LIT-7620.md`,
and this note.
