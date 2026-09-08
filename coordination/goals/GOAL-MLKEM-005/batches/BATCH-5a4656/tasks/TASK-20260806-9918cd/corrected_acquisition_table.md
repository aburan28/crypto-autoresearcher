# Corrected acquisition record for ePrint 2021/1351 / CCS'21 DOI 10.1145/3460120.3484819

Status: draft correction produced by TASK-20260806-9918cd
(GOAL-MLKEM-005 / BATCH-5a4656). This SUPERSEDES BATCH-a51f91
TASK-20260805-cdee80's `reads.md` Sec. 3.2 by citation only. That file is
immutable and is NOT edited or referenced as edited.
AGENTS.md rule 12 is UNMET and UNWAIVED; no EV-MLKEM-* or KN-* record status
changes as a result of this document.

## Scope caveat (restated, carried forward from RT-20260806-d008e0)

This table concerns the **CCS'21 published version** of Duman, Hövelmanns,
Kiltz, Lyubashevsky, Seiler, "Faster Lattice-Based KEMs via a Generic
Fujisaki-Okamoto Transform Using Prefix Hashing" (DOI
`10.1145/3460120.3484819`), NOT the ePrint 2021/1351 PDF specifically.
BATCH-a51f91's original acquisition-failure record concerned the ePrint
identifier; the aggregator route resolves an OA copy of the DOI, which is
the CCS'21 published version, not necessarily byte-identical or
content-identical to the ePrint preprint filed under 2021/1351. The two may
differ; this task does not assert they do not.

**Additional, unexpected finding recorded honestly (not part of this
task's assigned deliverable, but observed during a scope-verification
check and preserved per rule 5/9 rather than discarded):** a direct fetch
of `https://eprint.iacr.org/2021/1351.pdf` in this session returned
**HTTP 200**, `application/pdf`, whereas BATCH-a51f91's `reads.md` Sec. 3.2
recorded HTTP 403 (Cloudflare) for the same URL, on both a plain and a
browser-User-Agent request. This task did NOT attempt to reproduce that
failure's cause or confirm whether the block is now permanently lifted,
intermittent, or geographically/proxy-dependent; it only records that on
2026-09-08T01:32Z the direct route to the ePrint PDF itself was reachable
where it previously was not. See "Unexpected observation" table below.
This is reported as a follow-up candidate for the Coordinator, not acted
on further by this task (constraint: "no new census rows... report it as a
follow-up rather than expanding scope").

## Independent retrieval (own commands, own hashes — not copied from RT-20260806-d008e0)

Commands run, in order (full transcript and timings in `receipt.json`):

```
curl -sS https://api.openalex.org/works/doi:10.1145/3460120.3484819
```
returned HTTP 200 with `open_access.is_oa: true`, `open_access.oa_status:
"gold"`. `best_oa_location.pdf_url` was `https://dl.acm.org/doi/pdf/10.1145/3460120.3484819`
(the ACM DL route BATCH-a51f91 already recorded as 403). The `locations[]`
array separately listed a `TU/e Research Portal` entry with
`pdf_url: https://pure.tue.nl/ws/files/362308384/3460120.3484819.pdf` and
`is_oa: true` — the same institutional-repository URL RT-20260806-d008e0
used. This is a genuine, minor divergence from the red team's description:
their report characterizes the TU/e URL as what "OpenAlex... returns"
without noting it is not the top-ranked `best_oa_location`; walking the
full `locations[]` list (as `acquisition_procedure.md` step 2 now
requires) was necessary to find it in this run.

```
curl -sS -o /dev/null -w "HTTP_STATUS:%{http_code} CONTENT_TYPE:%{content_type}\n" \
  -A "Mozilla/5.0" https://dl.acm.org/doi/pdf/10.1145/3460120.3484819
```
confirmed HTTP 403, consistent with BATCH-a51f91's own finding for this
route.

```
curl -sS -D headers.txt -o tue_paper.pdf -w \
  "HTTP_STATUS:%{http_code} SIZE:%{size_download} CONTENT_TYPE:%{content_type}\n" \
  https://pure.tue.nl/ws/files/362308384/3460120.3484819.pdf
```
returned **HTTP 200**, `application/pdf`.

### Measured results of this retrieval, vs. RT-20260806-d008e0's reported values

| field | RT-20260806-d008e0 reported (report.yaml Q17 / OBJ-5) | this task's own independent retrieval | match? |
|---|---|---|---|
| URL | `https://pure.tue.nl/ws/files/362308384/3460120.3484819.pdf` | same URL | yes |
| HTTP status | 200 | 200 | yes |
| Content-Type | `application/pdf` | `application/pdf` | yes |
| Byte count | 1,832,736 | **1,832,738** | **no — differs by 2 bytes** |
| Page count | 17 | **17** (verified with `pymupdf`; see note below) | yes |
| sha256 | `2198eaf192cd58aa48fc272ebe18c66145476bfbe6a951fadb15dc6eb59bcb4c` | **`fbbcc63f837d702996b327a3dad30408009b1033775bc06635178468579b8ed8`** | **no — different hash** |

**This is a genuine discrepancy, reported honestly per this task's own
constraint ("If your own retrieval attempt fails where the red team's
succeeded, report that discrepancy honestly rather than copying their
figures") even though the retrieval did not fail — it succeeded but did
not byte-for-byte match.**

Diagnostic evidence gathered (not a conclusion, an observation): the
retrieved PDF's own metadata carries `producer: "OpenPDF 1.4.2"` and
`creationDate: D:20260908013135Z` — a timestamp matching this task's own
fetch time to the second, not a 2021 publication date. This is consistent
with (but does not prove) the retrieved bytes having been re-serialized by
a network intermediary between the TU/e origin server and this session
(this environment's outbound HTTPS is documented to route through a
policy-enforcing proxy that re-terminates TLS; see
`/root/.ccr/README.md`). No claim is made about WHERE the re-serialization
happens or whether RT-20260806-d008e0's session was subject to the same
intermediary; both the 2-byte size difference and the differing sha256 are
consistent with a lossless-content, different-bytes re-encoding (e.g. a
PDF sanitization/rewrite step), and the page count (17, independently
confirmed by walking `/Type /Page` objects and by `pymupdf.Document.page_count`)
and the extracted first-page text (title, author list, DOI link) match the
correct paper in both cases. **The content identity is verified; the
byte-level identity is not, and the two artifacts (this task's PDF and
the red team's) cannot be assumed to be bit-for-bit the same file even
though both retrieved the same URL and both are the correct 17-page
document.**

### Page-count verification detail

An initial check with the Unix `file` command on this task's retrieved PDF
reported "10 page(s)" — WRONG. Counting `/Type /Page` object markers
directly in the raw PDF bytes gave 17, and `pymupdf.open(...).page_count`
independently confirmed 17. The corrected `acquisition_procedure.md`
records this pitfall so a future task does not trust `file`'s page count.

### Unexpected observation: direct ePrint PDF route, now reachable

| field | value |
|---|---|
| URL | `https://eprint.iacr.org/2021/1351.pdf` |
| BATCH-a51f91 result (reads.md Sec. 3.2) | HTTP 403 (Cloudflare), twice, including with browser UA+Referer |
| this task's result, 2026-09-08T01:32:34Z | HTTP 200, `application/pdf`, 954,342 bytes, 16 pages (pymupdf), sha256 `b2ac83649f5c45c88d4331b2a6b25180a9325ca200f87bbe23126aff6cdd0a59` |

This is the ePrint preprint itself (16 pages, distinct byte count and page
count from the 17-page CCS'21 published version above — consistent with
the scope caveat that the two are not asserted identical). This task does
not read or characterize the paper's content beyond its title page; that
remains out of this task's scope (a literature-reading task, not this
process/acquisition task). Recorded here only as an acquisition-status
correction candidate: a future task in this goal that needs 2021/1351's
own text (as opposed to the CCS'21 published version) should re-attempt
the direct route before treating it as unobtainable, since the block
recorded in BATCH-a51f91 was not present in this session.

## What this table does NOT claim

- No claim is made about the CONTENT of either PDF beyond what is visible
  on the extracted title page (paper title, author list, DOI link) used to
  confirm identity; this is a process-and-acquisition correction task, not
  a literature-reading task.
- No claim is made about why the sha256/byte-count mismatch against
  RT-20260806-d008e0's reported values occurred; the proxy-reprocessing
  explanation above is offered as a plausible, evidence-consistent
  hypothesis, not a verified cause.
- No claim is made about whether the ePrint direct-route 403 seen in
  BATCH-a51f91 is now permanently resolved; only that it was not observed
  in this one retrieval at this one time.
- This document does not modify, and does not claim to modify,
  BATCH-a51f91 TASK-20260805-cdee80's `reads.md`, which remains immutable
  and unedited.
