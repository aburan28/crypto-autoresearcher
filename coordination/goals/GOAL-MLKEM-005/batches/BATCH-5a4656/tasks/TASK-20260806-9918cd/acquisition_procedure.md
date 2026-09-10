# Open-access-aggregator resolution step for literature acquisition

Status: draft process document produced by TASK-20260806-9918cd
(GOAL-MLKEM-005 / BATCH-5a4656). This is NOT a KN-TECH or KN-FIND entry.
AGENTS.md rule 12 is UNMET and UNWAIVED for this goal; only the Coordinator
may promote a knowledge-corpus entry, and only when rule 12 is satisfied.
This document is scoped to GOAL-MLKEM-005's own literature-acquisition
practice; it does not amend any program-wide document.

## Why this exists

BATCH-a51f91's TASK-20260805-cdee80 recorded ePrint 2021/1351
(Duman-Hövelmanns-Kiltz-Lyubashevsky-Seiler, CCS'21) as "unobtainable (full
text)" after eight direct-route attempts, all logged in that task's
`reads.md` Sec. 3.2 and `receipt.json`, none of which queried an
open-access aggregator. RT-20260806-d008e0 (BATCH-a51f91
TASK-20260805-49acd8, `report.yaml` OBJ-5 / Q17) obtained the CCS'21
published version in two commands via OpenAlex. This procedure generalizes
that correction into a mandatory step, run BEFORE any acquisition record in
this goal uses the word "unobtainable".

## The procedure (two commands, sub-two-minute budget)

Given a DOI (or a paper for which a DOI can be resolved from ePrint's
metadata, a publisher landing page, or a citation index):

1. **OpenAlex.**
   ```
   curl -sS https://api.openalex.org/works/doi:<DOI>
   ```
   Read, in order:
   - `open_access.is_oa` and `open_access.oa_status`
   - `best_oa_location.pdf_url` (the aggregator's top-ranked OA copy)
   - every entry in `locations[]` with `is_oa: true`, in particular any
     `host_type: "repository"` entry (institutional or subject repositories
     are frequently reachable when the publisher's own PDF route is not)

2. **Fetch the candidate PDF(s).**
   ```
   curl -sS -D headers.txt -o candidate.pdf -w \
     "HTTP_STATUS:%{http_code} SIZE:%{size_download} CONTENT_TYPE:%{content_type}\n" \
     <pdf_url>
   ```
   Try `best_oa_location.pdf_url` first. If that returns anything other
   than HTTP 200 with `content-type: application/pdf`, walk the remaining
   OA entries in `locations[]` in the order they appear — a
   publisher/DOI-resolver route (e.g. `dl.acm.org`) can be blocked by
   bot-protection while an institutional-repository mirror of the exact
   same accepted manuscript or published version is not.

3. **Unpaywall as a second aggregator, if OpenAlex found nothing OA.**
   ```
   curl -sS "https://api.unpaywall.org/v2/<DOI>?email=<contact-email>"
   ```
   Read `is_oa`, `best_oa_location.url_for_pdf`, and every entry in
   `oa_locations[]`. Unpaywall's location ranking can differ from
   OpenAlex's (observed directly in this task: for the DOI below, both
   aggregators ranked the publisher's own blocked PDF route as
   `best_oa_location`, and the reachable institutional-repository copy
   appeared only lower in each aggregator's location list) — this is why
   the procedure says to read the full location list, not only the
   top-ranked entry, from EITHER aggregator.

4. **Record, for whichever fetch succeeds:** the exact URL used, HTTP
   status, `content-type`, byte count, page count (verified with a PDF
   parser that reads actual page objects — see the "page-count pitfall"
   note below, not a byte-heuristic tool), and sha256 of the retrieved
   bytes. Record ALL attempted URLs and their results, not only the one
   that worked, per rule 5 (never discard a failed route) and rule 9
   (never omit an inconvenient observation).

5. **Only if step 1-3 all fail** (no `is_oa: true` anywhere, or every OA
   location 4xx/5xx/timeout) may an acquisition record use the word
   "unobtainable" for the FULL TEXT, and even then the record must name
   which routes were the aggregator-suggested ones (not just the direct
   publisher/ePrint/Wayback routes already conventional in this goal's
   prior practice) and confirm they were tried.

## Page-count pitfall observed in this task

The Unix `file` command's page count for at least one PDF fetched under
this procedure (see `corrected_acquisition_table.md`) undercounted pages
relative to the PDF's actual `/Type /Page` object count, apparently because
`file`'s PDF page-count heuristic does not reliably parse this file's
object structure. Verify page count with a tool that walks the document's
page tree (e.g. `pymupdf`/`fitz`'s `doc.page_count`, or counting
`/Type/Page` objects directly), not with `file -b`.

## Scope and limits of this procedure

- This step is an ADDITION before "unobtainable" is recorded, not a
  replacement for the direct-route attempts already conventional in this
  goal (publisher, ePrint mirror, arXiv, Wayback, institutional author
  pages). Both should be tried; the aggregator step is cheap enough
  (two commands, well under the two-minute budget observed here — see
  `receipt.json` for this task's own timings) that omitting it before
  declaring a document unobtainable is the actual defect being corrected.
- An aggregator returning `is_oa: true` with a working `pdf_url` retrieves
  A version of the paper. It does not guarantee that version is
  IDENTICAL to a different pointer to "the same" paper (e.g. an ePrint
  preprint vs. a publisher's typeset proceedings version can differ in
  content, pagination, and even claimed results). Record which version
  was retrieved (by DOI/identifier and by reading the retrieved PDF's own
  title page) and state the scope explicitly rather than treating any
  aggregator hit as interchangeable with a different specific artifact
  that was originally sought. See `corrected_acquisition_table.md` for a
  concrete instance of this caveat.
- A byte-for-byte hash of a "successful" retrieval is a comparison ONLY
  against another retrieval of the exact same bytes; a network
  intermediary that re-serializes or re-signs a PDF in transit (observed
  directly in this task; see `corrected_acquisition_table.md`) can change
  the sha256 and byte count of a document whose page count and text
  content are unchanged. A hash mismatch between two independent
  retrievals of the same URL is therefore not, by itself, evidence that
  the documents differ in content — check page count and extracted text
  before concluding otherwise.
