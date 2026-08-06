# Corrected acquisition table for ePrint 2021/1351 (Duman, Hövelmanns, Kiltz, Lyubashevsky, Seiler)

Supersedes, **by citation only, not by edit**, the acquisition-failure record
at `coordination/goals/GOAL-MLKEM-005/batches/BATCH-a51f91/tasks/TASK-20260805-cdee80/reads.md`
Sec. 3.2 (immutable, not modified by this task). That record listed direct
routes for ePrint 2021/1351 and recorded the body as unobtainable from them.
This table adds the open-access-aggregator step that record did not attempt,
per the correction at `EV-MLKEM-d146a5.yaml` `corrections_to_this_batch` CX-3
(raised by `RT-20260806-d008e0` OBJ-5, task `TASK-20260805-49acd8`).

**Scope caveat, restated (carried forward from the red team's own words in
`TASK-20260805-49acd8/notes.md` Sec. 4.1 and `report.yaml` OBJ-5):** what
follows is the retrieval of the **CCS'21 published version**
(DOI `10.1145/3460120.3484819`), **not the ePrint 2021/1351 PDF itself**. The
two may differ in content; this task asserts only what it directly read from
the CCS'21 published-version copy retrieved below.

## Part A — what this task independently measured

All commands below were actually executed by this task (`TASK-20260806-9918cd`)
against the live network through this environment's egress proxy. Exact
commands, timestamps and raw curl metadata are in `receipt.json`. Two
independent runs were made (an exploratory run and a clean scripted run); the
table reports the clean scripted run's figures as canonical and separately
notes the reproducibility check across all five total fetches.

| Step | URL fetched | HTTP status | Content-Type | Bytes | Elapsed |
|---|---|---|---|---|---|
| 1. OpenAlex query | `https://api.openalex.org/works/doi:10.1145/3460120.3484819` | 200 | application/json | 16,078 | 0.655 s |
| 2. `best_oa_location.pdf_url` (ACM) | `https://dl.acm.org/doi/pdf/10.1145/3460120.3484819` | **403** (Cloudflare challenge) | text/html | 5,494 | 0.740 s |
| 3. `locations[1].pdf_url` (TU/e, attempt A) | `https://pure.tue.nl/ws/files/362308384/3460120.3484819.pdf` | **200** | application/pdf | **1,832,736** | 1.324 s |
| 4. same URL, refetched (attempt B, repeatability check) | `https://pure.tue.nl/ws/files/362308384/3460120.3484819.pdf` | **200** | application/pdf | **1,832,736** | 1.470 s |

OpenAlex's `open_access` block for this DOI: `is_oa: true`, `oa_status: gold`.
`best_oa_location.pdf_url` pointed at the publisher (ACM), which was
paywalled (403) — the same failure the original T4 record already found for
that route. The working copy came from `locations[1]`
(`source.display_name: "TU/e Research Portal"`), not from
`best_oa_location`. This is recorded in `acquisition_procedure.md` as a
required refinement: iterate all of `locations[]`, not just
`best_oa_location`.

### Page count and content verification

`file` reported an unreliable page count (10) for attempt A's PDF. Independent
verification by counting `/Type/Page` objects directly in the raw PDF bytes,
cross-checked against a `/Type/Pages/Count 17` entry present in the file,
gives **17 pages** for every one of this task's fetches (attempts A and B,
and three earlier exploratory fetches of the same URL — 5/5 agree at 17).
Bookmark/outline titles extracted directly from the PDF's (uncompressed)
object dictionaries include "Abstract", "1 Introduction",
"3 Fujisaki-Okamoto Transformation with Prefix Hashing", "4 Proof of THEOREM
3.1", "5 Proof of THEOREM 3.2", "6 Quantum Preliminaries", "References" —
consistent with the DHKLS paper's actual content, not a placeholder or wrong
document.

### sha256

| Fetch | sha256 |
|---|---|
| This task, attempt A | `fec826dc053b36ec5c9537280fef88e8323423377d63e3ccc89dde8752e32cfd` |
| This task, attempt B (same URL, refetched) | `770e31a569f1579f07262ff54b416c0d66cbd57a539dfc80b02f3ef034236961` |
| This task, 3 earlier exploratory fetches of the same URL | `7ead7c34b7dc6eb1f61cbd9f72ba1112ee241c5a1d529f142302f035a07108a2`, `7a9df6fd95399a643e318a9606263078ed79416810d7d18cda108a638db419a3`, `7d640d5e595e282a70f94986ebe6eb876b2c6d4c4658b5c06284bcc3f770475e` |
| `RT-20260806-d008e0`'s reported value (not reproduced by this task) | `2198eaf192cd58aa48fc272ebe18c66145476bfbe6a951fadb15dc6eb59bcb4c` |

**All five of this task's own independent fetches of the identical URL
produced five different sha256 hashes.** Verified with three independent
hashing implementations (`sha256sum`, `openssl dgst -sha256`, Python
`hashlib`) on the same bytes, so this is not a hashing-tool artifact. None of
the five match `RT-20260806-d008e0`'s reported hash.

Byte-diffing two of this task's own fetches (attempt A vs. attempt B) found
exactly 81 differing bytes, localized to a ~73 KB region near the end of the
file, entirely inside PDF `/FontDescriptor` objects' `/FontName` fields
(e.g. `JWSTBL+ArialUnicodeMS` vs. `FUXSPD+ArialUnicodeMS` — a standard PDF
font-subset-tag prefix). Byte count, page-object count, and every other
inspected structural and textual element were identical between attempts.

## Part B — comparison against the red team's reported values

| Field | `RT-20260806-d008e0` (reported) | This task (measured) | Match? |
|---|---|---|---|
| Route | OpenAlex -> TU/e repository PDF | OpenAlex -> TU/e repository PDF (`locations[1]`) | Same route |
| HTTP status | 200 | 200 (attempts A and B, and 3 earlier fetches) | Match |
| Content-Type | application/pdf | application/pdf | Match |
| Byte count | 1,832,736 | 1,832,736 (all 5 fetches) | **Match, exactly** |
| Page count | 17 | 17 (all 5 fetches, via `/Type/Page` object count) | **Match** |
| sha256 | `2198eaf192cd58aa48fc272ebe18c66145476bfbe6a951fadb15dc6eb59bcb4c` | 5 different values across 5 fetches, none equal to the red team's | **Does not reproduce** |
| Elapsed | "about ninety seconds" (whole two-command procedure) | 0.655 s (OpenAlex) + 1.324 s (PDF fetch) = 1.98 s for the successful path; 4 total requests including the failed ACM attempt completed in 4.19 s | Both fast; this task's environment measurably faster, not a contradiction |

**Honest reading of the discrepancy, reported rather than smoothed over per
this task's constraints:** this task's retrieval independently reproduces
the red team's route, HTTP status, content type, byte count, and page count
exactly, and independently confirms (via bookmark titles and section
headings extracted from the PDF) that the retrieved document is the correct
paper. It does **not** reproduce the red team's reported sha256 — and,
critically, this task's own repeated fetches of the identical URL do not
even reproduce each other's sha256, with the difference confined to
per-request font-subsetting metadata rather than document content. This
means sha256 is not a stable identity check for this specific server/URL in
this environment; whether the red team's single fetch happened to land on a
sha256 that would also fail to reproduce on a repeat fetch is unknown; this
task did not have access to the red team's raw bytes to check the diff
region directly. This task does not claim its retrieval is byte-identical to
the red team's; it claims independent reproduction of route, status, content
type, byte count, page count, and document identity, with an honestly
reported hash non-match and hash instability.

## What this does not establish

No claim is made about the ePrint 2021/1351 PDF itself, which was not
retrieved by this task or (per the record it is reproducing) by
`RT-20260806-d008e0`. No claim is made about DHKLS's mathematical content
beyond what `TASK-20260805-49acd8/notes.md` Sec. 4.2 already quotes; this
task did not re-read the paper's technical content, only verified its
identity (title, DOI, section structure) and acquisition metadata. This task
makes no finding about ML-KEM, and AGENTS.md rule 12 remains unmet and
unwaived; no `EV-MLKEM-*` or `KN-*` record's status changes here.
