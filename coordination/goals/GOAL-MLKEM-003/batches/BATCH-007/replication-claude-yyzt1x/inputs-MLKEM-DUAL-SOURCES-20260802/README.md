# MLKEM-DUAL-SOURCES-20260802

Primary-source retrieval package for **TASK-20260802-101** (GOAL-MLKEM-003,
BATCH-007). Produced by
`coordination/goals/GOAL-MLKEM-003/batches/BATCH-007/tasks/TASK-20260802-101/fetch_sources.py`
on 2026-08-02 UTC, repository commit `25e90257`.

## Why this package exists

For the whole prior history of GOAL-MLKEM-003 every primary source was
unreachable, so all four standing Carrier findings (KN-FIND-012/013/014/016)
were derived from a single vendored HAL snapshot and a pinned code commit with
no way to check them against an authoritative current revision. Network access
was partially restored for this session. This package is the retrieval half of
the resulting cheap falsification gate; the adjudication half lives in
`coordination/goals/GOAL-MLKEM-003/batches/BATCH-007/tasks/TASK-20260802-101/source_adjudication.md`.

## What is here

| Path | What it is |
|---|---|
| `provenance.json` | One record per attempted source: `url`, `http_status`, `retrieved_at` (UTC), `sha256`, `bytes`, `revision_id`, `status` ∈ {`retrieved`, `unretrieved`, `not_attempted`}, the exact curl command, and for failures the exact server error. 35 attempts: 20 retrieved, 14 unretrieved, 1 deliberately not attempted. |
| `extracts/` | The small text regions the adjudication actually quotes. |

### `extracts/` contents

| File | Derived from | Used for |
|---|---|---|
| `eprint-2022-1750-abstract-page.txt` | ePrint 2022/1750 landing page (HTML) | Q1: revision history (`2025-06-11: last of 3 revisions`, `2022-12-20: received`), the `Note:` field, publication info |
| `eprint-search-coded-dual-attack-hits.txt` | ePrint search index | Q1 corroboration (`2022/1750 last_updated=2025-06-11`); Q3 literature sweep |
| `hal-05406481-api.json` | HAL search API | Q1: deposit version (`version_i: 1`), `submittedDate_s`, `producedDate_s`, file URL |
| `carrier-hal-05406481-pdf-metadata.json` | HAL PDF document info dictionary | Q1: `/ModDate D:20250611152836+02'00'`, page count, title, author list |
| `carrier-hal-05406481-p02-titlepage.txt` | HAL PDF page 2 (page 1 is the HAL cover sheet) | Q1: the paper's own title and author list |
| `carrier-hal-05406481-p37-tableC1-C2.txt` | HAL PDF page 37 (printed page 36) | **Q1 locus**: Tables C.1 and C.2 verbatim, including the CN/Kyber-512 row |
| `carrier-hal-05406481-fig4.1-validation-section.txt` | HAL PDF, Section 4 | **Q2 locus** (the footnote naming the code repository, branch and directory) and **Q3 locus** (the Fig 4.1 T-axis range and parameters) |
| `ducas-pulles-2023-sec5.2-5.3-excerpt.txt` | CWI repository copy of Ducas–Pulles, CRYPTO 2023 | Q3: what that paper actually measured, and in which variable |
| `eprint-2026-599-abstract.txt`, `eprint-2026-1400-abstract.txt`, `eprint-2026-1326-abstract.txt` | ePrint landing pages | Q3: recent work building on the Carrier variant |
| `semanticscholar-citations-carrier.json` | Semantic Scholar citation edges for DOI 10.1007/978-3-032-01855-7_15 | Q3: citation sweep |

## What was deliberately **not** vendored

Five full PDFs were retrieved, hashed, and read, but not committed, because the
handoff forbids committing multi-megabyte binaries when the adjudication needs a
table. Their complete-object `sha256` values are in `provenance.json` and are
the authoritative identifiers:

| Object | bytes | sha256 |
|---|---|---|
| `https://hal.science/hal-05406481/document` | 1252838 | `083b142256eecaebfa72dfccf847151b2175666a3979cef4e7383376757b8005` |
| `https://ir.cwi.nl/pub/33407/33407.pdf` (Ducas–Pulles, CRYPTO 2023) | 1021750 | `947f2826ce64d7a8c09493f9901ef418095b89a8660be075880f8874863eb62e` |
| `https://inria.hal.science/hal-04827068/document` (Pouly–Shen, EUROCRYPT 2024) | 925479 | `d120d4a43607053a2c66cbee72e45a236327e93dd1563f14183add35d4a2386f` |
| `https://zenodo.org/api/records/6493704/.../content` (MATZOV 2022) | 610325 | `2a6cb56e5ca2d80e7b6c12d32779ab330c1b5938ba91e22822b634647056c3a9` |
| `https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.203.pdf` | 1252341 | `fe1f12f32a7e44ec9fdebbf400cda843a40b506dee676725234dc6f7923b6cac` |

The HAL Carrier PDF is **byte-identical** to the existing immutable run artifact
`experiments/EXP-MLKEM-010/vendor-lock/Carrier-2022-1750-hal-05406481.pdf`
(same sha256; `provenance.json` records this comparison under
`byte_identical_to_vendored_artifact`). Re-vendoring it here would have created
a second copy of an immutable artifact, so it was not copied. That directory was
not modified by this task.

## Reuse boundary

Read this before citing anything in this directory.

1. **`extracts/` is derived text, not source bytes.** Every `.txt` under
   `extracts/` was produced by `pypdf` 6.14.2 text extraction or by HTML tag
   stripping. Extraction reorders and mangles mathematical typesetting (see the
   run-together tokens in the Table C.2 extract). It is adequate for reading a
   numeric cell and quoting a sentence; it is **not** adequate for
   character-level claims about the source. Any downstream claim must be
   re-derived from the full object identified by its `sha256` in
   `provenance.json`.
2. **Only `retrieved` records are usable.** A record with
   `status: unretrieved` is an infrastructure fact and is never evidence for or
   against a finding (AGENTS.md rule 5). Fourteen such records are present,
   including every ePrint-hosted PDF and every GitHub endpoint.
3. **Nothing here was written from recollection.** Every byte in `extracts/`
   came off the wire in this session through the commands recorded in
   `provenance.json`.
4. **Revision identity is claimed only where recorded.** `revision_id` states
   what a record is; where the identity of a retrieved object with a nominal
   revision is an *inference* rather than a byte equality, that inference and
   its evidence are set out explicitly in `source_adjudication.md` (Q1) and are
   not asserted here.
5. **Scope.** These are estimate/table-tier reference materials for auditing
   published cost tables. Nothing in this directory supports any ML-KEM break
   claim or any crypto-scale claim.
6. **Third-party content.** ePrint 2022/1750 is distributed CC BY (recorded on
   its landing page). The other excerpts are short verbatim quotations retained
   for verification of published numbers; their licences were not established
   and no redistribution beyond that purpose is intended. The MATZOV report is
   from Zenodo record 6493704 and FIPS 203 is a US Government publication.

## Reproducing

```
python3 coordination/goals/GOAL-MLKEM-003/batches/BATCH-007/tasks/TASK-20260802-101/fetch_sources.py
```

The script is idempotent, re-writes `provenance.json` and `extracts/`, and
requires network egress plus `pypdf`. Retrieval outcomes are environment
dependent: the ePrint PDF failures are Cloudflare bot mitigation
(`cf-mitigated: challenge`) and the GitHub failures are a session-scoped egress
policy, so a different session may see different `status` values. That is why
each record stores the exact status and error rather than only the successes.
