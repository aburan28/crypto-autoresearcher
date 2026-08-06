# Literature-acquisition procedure: open-access aggregator resolution step

Status: a reusable process step for GOAL-MLKEM-005's own literature
acquisition (this goal's task write_scope only; it does not amend any
program-wide document). Written by TASK-20260806-9918cd (B2-D), following
the correction recorded at `EV-MLKEM-d146a5.yaml` `corrections_to_this_batch`
CX-3 (raised by `RT-20260806-d008e0` OBJ-5), which found that
`BATCH-a51f91/TASK-20260805-cdee80` (T4) recorded ePrint 2021/1351 as
"unobtainable" without trying an open-access aggregator.

## Rule

Before any acquisition record in this goal uses the word "unobtainable" for
a DOI-bearing work, the aggregator step below MUST have been run and its
result recorded. A "the direct/publisher/preprint-server routes all failed"
finding is not sufficient on its own; "unobtainable" is a claim about the
document, and only the aggregator step (plus the direct routes) supports it.

This binds forward within GOAL-MLKEM-005. It does not retroactively edit
`BATCH-a51f91/TASK-20260805-cdee80/reads.md`, which is immutable; this
procedure and `corrected_acquisition_table.md` supersede that record by
citation only (see CX-3, `verified_by_coordinator` in EV-MLKEM-d146a5.yaml).

## Preconditions

- A DOI for the target work. If only an ePrint/arXiv/other-repository ID is
  known, first resolve the DOI via the publisher page, a citation database,
  or the paper's own front matter (do not skip the aggregator step merely
  because a DOI was not handed to you already-resolved).
- The direct routes (repository landing page, repository PDF, publisher PDF,
  cached/mirror fetches) have been attempted and their HTTP statuses
  recorded, exactly as `BATCH-a51f91/TASK-20260805-cdee80/reads.md` Sec. 3.2
  already does. The aggregator step runs BEFORE those routes are summarized
  as a failure, not instead of them.

## Step 1 — OpenAlex

```
curl -sS "https://api.openalex.org/works/doi:<DOI>"
```

No API key required. Budget: one HTTP round trip, well under two minutes in
every case observed so far (TASK-20260806-9918cd measured 0.655s; the T4
red-team review, RT-20260806-d008e0, reported "about ninety seconds" total
for the whole two-step procedure including the PDF fetch).

Read these fields from the JSON response, in this order of preference:

1. `open_access.is_oa` (boolean) and `open_access.oa_status`
   (`gold` / `green` / `hybrid` / `bronze` / `closed`). If `is_oa` is
   `false`, stop here and record that OpenAlex found no OA copy; proceed to
   Step 3 (Unpaywall) as a second aggregator before recording
   "unobtainable".
2. `best_oa_location.pdf_url`. **Do not treat this as sufficient by
   itself.** `best_oa_location` is OpenAlex's own best guess and can point
   at a publisher URL that is in fact paywalled (observed directly in this
   task: `best_oa_location.pdf_url` for the DOI below resolved to
   `dl.acm.org`, which returned HTTP 403 with a Cloudflare challenge, the
   same failure mode `reads.md` Sec. 3.2 already recorded for that same
   ACM route).
3. **Iterate the full `locations[]` array**, not just `best_oa_location`.
   Each entry carries its own `is_oa`, `pdf_url`, `landing_page_url`, and
   `source.display_name`. In the DOI below, `locations[]` held 5 entries;
   the one that actually served the PDF (`source.display_name`: "TU/e
   Research Portal") was `locations[1]`, not `best_oa_location`
   (`locations[0]`, the ACM entry, which 403'd). Try every `pdf_url` in
   `locations[]` where `is_oa` is `true`, in order, until one returns
   HTTP 200 with a `content-type` starting `application/pdf` and a
   non-trivial byte count (a few hundred bytes of HTML is a
   soft-block/challenge page, not a paper).

## Step 2 — fetch the returned pdf_url

```
curl -sS -D headers.txt -w "HTTP_STATUS:%{http_code}\nCONTENT_TYPE:%{content_type}\nSIZE:%{size_download}\nTIME_TOTAL:%{time_total}\n" \
  "<pdf_url>" -o retrieved.pdf
```

Accept the result only if HTTP status is 200 and `content-type` is
`application/pdf` (or the tool's Content-Type reports a PDF; some
repositories omit a charset but still declare `application/pdf`). A 403,
429, or an HTML challenge page disguised behind a 200 (check byte count and
`file`/magic-number type, not status code alone) is a failure of that
location; move to the next `locations[]` entry.

## Step 3 — Unpaywall (second aggregator, if Step 1/2 do not resolve)

```
curl -sS "https://api.unpaywall.org/v2/<DOI>?email=<contact>"
```

Requires a contact email in the query string per Unpaywall's terms; use a
real, already-authorized contact address for this program (do not invent
one). Read `is_oa`, `best_oa_location.url_for_pdf`, and
`oa_locations[].url_for_pdf` the same way as Step 1, and fetch as in Step 2.

## Step 4 — record, regardless of outcome

For whatever was retrieved (or attempted and failed), record in the
acquisition table:

- the exact URL fetched,
- HTTP status,
- `content-type`,
- byte count (`size_download` / `wc -c`),
- page count (see "Page count" below),
- sha256 of the retrieved bytes,
- **whether a second, independent fetch of the same URL reproduces the same
  sha256** (see "Hash stability" below — this task found it does not, for
  the one document tested, and that finding is now part of this
  procedure).
- timestamp (UTC) and elapsed time.

Only after Steps 1-3 are exhausted and still fail may a record use the word
"unobtainable", and even then the correct framing is that the *search*
failed, not that the document does not exist or cannot exist online — per
`docs/inventor-protocol.md` Sec. 4, a count of failed routes has honest
status `unverified` about the document, not `unobtainable` about it (this
is exactly OBJ-5's finding against the original T4 record).

## Page count

`file <path>.pdf` reports a page count from PDF structure heuristics that
this task found to be UNRELIABLE (it reported 10 pages for a document whose
own internal structure carries 17 `/Type/Page` objects). Prefer, in order:
`pdfinfo` (poppler-utils) if available; a PDF-parsing library (`pypdf`,
`pdfminer.six`, PyMuPDF/`fitz`) if the environment's Python can load one
without dependency conflicts (this task's `pypdf` import failed on a broken
`cryptography`/`_cffi_backend` binding in this specific environment — an
infrastructure defect, recorded, not worked around by disabling
verification); as a fallback that needs no library, count top-level page
objects directly from the raw PDF bytes:

```
grep -a -o '/Type/Page[/>]' retrieved.pdf | wc -c   # (or | wc -l)
```

This undercounts if a producer compresses object streams (common in some
modern PDF generators using cross-reference streams / `ObjStm`); check for
a plausible non-zero result and cross-check against `/Count <N>` on the
document's own `/Type/Pages` root dictionary object where present. Record
which method was used.

## Hash stability — a finding from this task, now a required check

This task fetched the same `pdf_url` five times (across two runs) and
obtained the same byte count (1,832,736) and the same page-object count (17)
every time, but a **different sha256 every time** — none matching the value
reported by the retrieval this task was reproducing
(`RT-20260806-d008e0`'s `2198eaf192cd58aa48fc272ebe18c66145476bfbe6a951fadb15dc6eb59bcb4c`).
Byte-level diffing of two of this task's own fetches localized every
differing byte to PDF font-subset-tag strings inside `/FontDescriptor`
objects (e.g. `/FontName/JWSTBL+ArialUnicodeMS` in one fetch vs.
`/FontName/FUXSPD+ArialUnicodeMS` in another — the 6-letter prefix is the
standard PDF subset-tag convention), not to the document's visible text,
section structure, or bookmarks, which were identical and matched the
paper's actual title and section titles in every fetch.

**Consequence for this procedure:** treat sha256 as a per-fetch fingerprint,
not a guaranteed persistent document identity, for any repository whose
serving pipeline regenerates the PDF per request (a real, previously
undocumented property of at least the TU/e repository server tested here).
Record byte count, page count, and a content spot-check (title/section
match) as the primary reproducibility evidence; record sha256 for the record
but do not treat a mismatched sha256 alone, with matching byte count, page
count and content, as evidence that a different document was retrieved.
Where feasible, fetch twice and report whether the hash was stable — this
procedure now requires that second fetch as a check, not an optional
extra.

## Budget

Steps 1-3 together are a small, fixed number of HTTP round trips
(observed: 4 requests total in this task's run — 1 OpenAlex query, 1 failed
publisher fetch, 2 repository fetches — completing in under 5 seconds of
`curl` wall time). This is negligible next to any task's stated wall-clock
budget and should be run unconditionally before any "unobtainable" finding,
never skipped for budget reasons.
