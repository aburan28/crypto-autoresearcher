# Transcription report — Esser–Bellini SEC Table 1

Transcription convention: coordination/goals/GOAL-MCE-001/batches/BATCH-a68f79/tasks/TASK-20260808-a9f648/transcription_convention.md
Binding authority: DEC-20260803-a5b9b1 D-10

**Task:** TASK-20260808-1985f1 · **Goal:** GOAL-MCE-001 · **Batch:** BATCH-a68f79
**Role:** executor · **Date:** 2026-08-09 (UTC; local session date 2026-08-08)
**Deliverables reported on:** `sec_table1.md`, `sec_table1.json`, this file, and
`source_access_log.yaml` (required by convention Rule 3.1.7; see DEV-3).

**Inference record (verbatim, as required by the task card):** requested_policy
`executor-implementation`, degraded_allowed false, fallback_allowed false; per
CLAUDE.md per-role selection is process-level under Claude Code and subagents keep
model: inherit, so the resolved model is the session model; fallback_used: false.

**Budget:** authorized 1 run, 2 GB, 3600 s. One run was executed. Measured span
from the first retrieval (2026-08-09T01:30:26Z) to the post-write verification
(2026-08-09T01:48:55Z) is **1109 s** of the 3600 s authorized — and that span is
reported as a span, not as compute time: it includes agent deliberation between
commands, and no per-command timing was instrumented. No timeout, memory cap or
run cap was reached, no run was abandoned, and no run was repeated to obtain a
different answer.

**Claim tier: toy, unchanged. `GOAL-MCE-001.active_hypothesis_ids`: empty,
unchanged.** Transcribing a table establishes nothing about Classic McEliece, in
either direction. Nothing in this report or in `sec_table1.md` asserts that any
parameter set is secure, insecure, above or below any category threshold; the
source's own statements on that are quoted, as the source's, and are not adopted.

---

## Was the source obtainable in this environment, and by what route

**Yes.** `https://classic.mceliece.org/mceliece-security-20221023.pdf`, direct
GET, HTTP 200, 332574 bytes, sha256
`db17ef0879cb8822120c312b7290f7db82fe9fc356bd16058ad334a512b523fa`, 36 pages.
No proxy, no redirect chain beyond `-L`'s default, no authentication, no 403.

The declared route order put the local repository first, and it was checked
first: `find / -iname 'mceliece-security*'` returns nothing, no `inputs/`
subdirectory holds an Esser–Bellini or Classic McEliece source, and no PDF in the
worktree is this document. **The source is not committed to this repository** —
third-party PDFs deliberately are not — so the network route was necessary and
was used. Full attempt log with timestamps and commands:
`source_access_log.yaml`.

The `[NOT-OBTAINED]` outcome this task was told to record if the source could not
be read **does not apply**: the source was read. `[RECALLED-NOT-READ]` is 0 and
nothing in any deliverable is transcribed from BATCH-001's quotation of SEC, from
a summary, or from memory. The one thing taken from a prior record is the URL,
which is a retrieval instruction and not a transcribed value.

Independent corroboration, reported as an observation and not as a source of
values: the byte count and sha256 above are identical to those recorded by
`TASK-20260803-f3aece/source_access_log.yaml` seq 7 on 2026-08-03, which this task
read directly; and the row order this task read — `348864, 460896, 6688128,
6960119, 8192128`, each × three `mem` models — is the row order the binding
convention's § 8.6 attributes to validator `TASK-20260803-409c5e`. That second
item is quoted at one remove: this task read the convention, not the validator's
report, and says so rather than implying a first-hand read. Both checks were made
*after* the transcription was built from the extractor output, and neither was
used to build it.

---

## Second pass

**No disagreement.**

The second pass was made deliberately independent of the first at three points:
a second retrieval, a different set of extractor configurations, and a separately
written parser.

| | Pass 1 | Pass 2 |
|---|---|---|
| Retrieval | seq 1, 2026-08-09T01:30:26Z | seq 2, 2026-08-09T01:36:07Z, a second GET; `cmp` reports the two files byte-identical |
| Extractor 1 | E-A poppler pdftotext 26.04.0, `-layout` (positional) | P2-A poppler pdftotext 26.04.0, `-raw`, read as a flat token stream |
| Extractor 2 | E-B pypdf 6.15.0, `extract_text()` default mode | P2-B pypdf 6.15.0, `extract_text(extraction_mode="layout")` |
| Extractor 3 | E-C pdfminer.six 20260107, LTChar positional reconstruction, default `LAParams` | P2-C pdfminer.six 20260107, LTChar reconstruction, `LAParams(char_margin=1.5, line_margin=0.3, word_margin=0.2)` |
| Parser | `extract_compare.py` | `pass2.py`, written separately |

Result, compared in code by string equality rather than by eye:

- Pass-1 internal agreement: E-A = E-B = E-C on all 150 cells and on all 10
  column headers. **0 disagreements out of 150.**
- Pass 2 against pass 1: P2-A, P2-B and P2-C each equal pass 1's 15×10 array.
  **0 disagreements out of 450 comparisons.**
- Header row: identical ten tokens in identical order in all six extractions.

**One disagreement exists and it is not in the table.** E-B (pypdf default mode)
renders the caption `T able 1`, `1 /3`, `1 /2` where E-A, E-C and P2-C render
`Table 1`, `1/3`, `1/2`, and P2-B renders `Table 1:` followed by two spaces.
Nothing was reconciled: all five renderings are preserved verbatim in
`sec_table1.md`, and the JSON caption field carries `[CONVENTION-GAP:1]` rather
than a choice among them. Pass 2 did not resolve this disagreement and was not
expected to; it established that the disagreement is a property of the extractor
and not of the retrieval, since it reproduces on independently fetched bytes.

---

## Unreadable rows

**None. All 15 rows and all 10 columns were read, and every one of the 150 cells
is transcribed.** No row, no column and no cell is marked `[EXTRACTION-DAMAGED]`,
`[NOT-STATED-BY-SOURCE]` as to its value, or `[NOT-OBTAINED]`.

This is a stronger statement than BATCH-001's `markers set: 0` and the difference
matters, so the basis is given rather than asserted. The failure mode that
produces silently wrong table transcriptions is column-to-row misassociation, and
one of the three extractors used here does exactly that. Its raw output is
preserved below.

### Raw output — E-C, pdfminer.six 20260107, flow mode `extract_text()`

Locus: SEC, Table 1, 10/10

```
param mem Prange Stern Dumer
151.4
173.4
348864
159.7
176.7
348864
163.2
178.3
348864
193.2
216.8
460896
202.2
220.4
460896
205.8
222.1
460896
267.9
295.7
6688128
279.5
299.4
6688128
283.3
301.2
6688128
268.3
296.8
6960119
280.5
300.4
6960119
284.3
302.2
6960119
307.4
334.1
8192128
317.1
337.7
8192128
321.0
339.5
8192128

151.4
159.3
162.8
193.3
201.7
205.3
268.0
279.2
283.0
268.4
280.1
283.9
303.2
316.8
320.7

0
1/3
1/2
0
1/3
1/2
0
1/3
1/2
0
1/3
1/2
0
1/3
1/2

BC BJMM pdw MO
140.8
156.4
158.6
179.8
198.6
201.0
246.2
274.9
278.2
245.7
275.8
279.2
275.6
311.9
315.6

141.9
159.1
162.2
180.8
201.6
204.8
247.3
278.9
282.3
246.6
279.4
283.3
277.7
316.3
320.0

143.4
157.8
160.3
182.6
200.6
203.4
248.8
277.6
280.4
248.4
278.6
281.4
279.1
315.5
318.6

151.5
159.7
163.2
193.3
202.2
205.8
268.0
279.5
283.3
268.4
280.5
284.3
303.4
317.1
321.0

BM
142.7
157.5
159.8
182.1
199.8
202.2
249.6
276.4
279.4
249.2
277.3
280.3
281.1
313.3
317.0
```

Extraction note: this is the column-major hazard, unedited. The reading order is
not the printed reading order: the stream interleaves `Dumer`, `Prange` and
`param` for fifteen rows, then emits `Stern` as a block of fifteen, then `mem`,
then `MO`, `BC`, `pdw`, `BJMM`, `BM` as blocks. **Taken alone this output cannot
establish which value belongs to which column**, and identifying its blocks by
matching them against another extractor's output would be circular. It is
therefore used for nothing in this transcription except as the raw record here.

### Raw output — E-B, pypdf 6.15.0, `extract_text()` default mode

Locus: SEC, Table 1, 10/10

```
param mem Prange Stern Dumer BC BJMM pdw MO BM
348864 0 173.4 151.4 151.4 151.5 141.9 143.4 140.8 142.7
348864 1/3 176.7 159.3 159.7 159.7 159.1 157.8 156.4 157.5
348864 1/2 178.3 162.8 163.2 163.2 162.2 160.3 158.6 159.8
460896 0 216.8 193.3 193.2 193.3 180.8 182.6 179.8 182.1
460896 1/3 220.4 201.7 202.2 202.2 201.6 200.6 198.6 199.8
460896 1/2 222.1 205.3 205.8 205.8 204.8 203.4 201.0 202.2
6688128 0 295.7 268.0 267.9 268.0 247.3 248.8 246.2 249.6
6688128 1/3 299.4 279.2 279.5 279.5 278.9 277.6 274.9 276.4
6688128 1/2 301.2 283.0 283.3 283.3 282.3 280.4 278.2 279.4
6960119 0 296.8 268.4 268.3 268.4 246.6 248.4 245.7 249.2
6960119 1/3 300.4 280.1 280.5 280.5 279.4 278.6 275.8 277.3
6960119 1/2 302.2 283.9 284.3 284.3 283.3 281.4 279.2 280.3
8192128 0 334.1 303.2 307.4 303.4 277.7 279.1 275.6 281.1
8192128 1/3 337.7 316.8 317.1 317.1 316.3 315.5 311.9 313.3
8192128 1/2 339.5 320.7 321.0 321.0 320.0 318.6 315.6 317.0
```

Extraction note: content-stream order; here it happens to be row-major and each
line carries a full row. No `(cid:NN)` token and no flattened superscript appears
in the table region. The `T able`/`1 /3` artefacts appear in this extractor's
caption text, quoted in `sec_table1.md`, not in the table.

### Raw output — P2-A, poppler pdftotext 26.04.0, `-raw`

Locus: SEC, Table 1, 10/10

```
param mem Prange Stern Dumer BC BJMM pdw MO BM
348864 0 173.4 151.4 151.4 151.5 141.9 143.4 140.8 142.7
348864 1/3 176.7 159.3 159.7 159.7 159.1 157.8 156.4 157.5
348864 1/2 178.3 162.8 163.2 163.2 162.2 160.3 158.6 159.8
460896 0 216.8 193.3 193.2 193.3 180.8 182.6 179.8 182.1
460896 1/3 220.4 201.7 202.2 202.2 201.6 200.6 198.6 199.8
460896 1/2 222.1 205.3 205.8 205.8 204.8 203.4 201.0 202.2
6688128 0 295.7 268.0 267.9 268.0 247.3 248.8 246.2 249.6
6688128 1/3 299.4 279.2 279.5 279.5 278.9 277.6 274.9 276.4
6688128 1/2 301.2 283.0 283.3 283.3 282.3 280.4 278.2 279.4
6960119 0 296.8 268.4 268.3 268.4 246.6 248.4 245.7 249.2
6960119 1/3 300.4 280.1 280.5 280.5 279.4 278.6 275.8 277.3
6960119 1/2 302.2 283.9 284.3 284.3 283.3 281.4 279.2 280.3
8192128 0 334.1 303.2 307.4 303.4 277.7 279.1 275.6 281.1
8192128 1/3 337.7 316.8 317.1 317.1 316.3 315.5 311.9 313.3
8192128 1/2 339.5 320.7 321.0 321.0 320.0 318.6 315.6 317.0
```

Extraction note: `-raw` emits content-stream order without poppler's column
alignment; on this page that order happens to be row-major, and single spaces
replace `-layout`'s padding. The pass-2 parser deliberately ignored the line
structure and consumed the page as a flat stream of the 150 tokens following the
header token `BM`, so that a line-boundary artefact could not hide a
misassociation; it reassembled them 10 to a row and compared against pass 1.

### Raw output — E-C, pdfminer.six, LTChar baseline clustering with `|` at every inter-glyph gap > 1.0 pt

Locus: SEC, Table 1, 10/10

```
  707.6  param|mem|Prange|Stern|Dumer|BC|BJMM|pdw|MO|BM
  692.7  0|173.4|151.4|151.4|151.5|141.9|143.4|140.8|142.7
  692.4  348864
  678.3  1/3|176.7|159.3|159.7|159.7|159.1|157.8|156.4|157.5
  677.9  348864
  663.8  1/2|178.3|162.8|163.2|163.2|162.2|160.3|158.6|159.8
  663.5  348864
  649.0  0|216.8|193.3|193.2|193.3|180.8|182.6|179.8|182.1
  648.7  460896
  634.5  1/3|220.4|201.7|202.2|202.2|201.6|200.6|198.6|199.8
  634.2  460896
  620.1  1/2|222.1|205.3|205.8|205.8|204.8|203.4|201.0|202.2
  619.8  460896
  605.3  0|295.7|268.0|267.9|268.0|247.3|248.8|246.2|249.6
  604.9  6688128
  590.8  1/3|299.4|279.2|279.5|279.5|278.9|277.6|274.9|276.4
  590.5  6688128
  576.4  1/2|301.2|283.0|283.3|283.3|282.3|280.4|278.2|279.4
  576.0  6688128
  561.5  0|296.8|268.4|268.3|268.4|246.6|248.4|245.7|249.2
  561.2  6960119
  547.1  1/3|300.4|280.1|280.5|280.5|279.4|278.6|275.8|277.3
```

Extraction note: first 22 baseline clusters only; `|` is inserted by the
reconstruction script at each gap and is not source content. This is the
positional evidence that column-to-row association was **read from the rendered
layout** and not inferred from extraction order, as Rule 5.2.1 requires. The
`param` label of each row sits on a baseline 0.3–0.4 pt below the rest of its
row, which is why it forms its own cluster at this tolerance; the 1.0 pt
tolerance used for the transcription merges them.

Two further checks on readability, reported as checks and not as repairs:

- No `(cid:NN)` token occurs anywhere in the extracted page 10.
- No flattened superscript occurs in the 150 cells or the header row. Flattened
  superscripts DO occur in the prose on pages 10 and 11 (`2143`, `286.6`,
  `2207` as extracted). Those are left unrepaired inside their verbatim blocks in
  `sec_table1.md`, each annotated on an `Extraction note:` line outside the block
  with a conjectured reading prefixed `NOT TRANSCRIBED — conjectured reading:`.
  No cell depends on any of them.

---

## Obstructions

Three convention gaps were encountered and are returned rather than resolved.
Per Rule 7.2 a gap is closed by a superseding convention document under a new
task id, never by editing `TASK-20260808-a9f648`'s file, which this task did not
open for write.

### CONVENTION-GAP:1

- `id:` `CONVENTION-GAP:1`
- `cell_or_locus:` table.caption_verbatim (SEC, Table 1, 10/10) — not a cell; no cell id can be formed
- `what_is_undetermined:` When two extractors disagree on the bytes of a non-cell verbatim field, the convention does not determine what a single-valued JSON string field is populated with, and the fixed §8.3 schema offers no status / raw_extractor_output / damage_note structure for non-cell verbatim text of the kind Rule 5.3 provides for cells.
- `candidate_renderings:`
  - (a) the bytes returned by the majority of extractors, i.e. E-A/E-C's 'Table 1: ... 1/3 ... 1/2', with the minority rendering recorded only in the Markdown
  - (b) the bytes returned by a single declared primary extractor, i.e. E-B's 'T able 1: ... 1 /3 ... 1 /2'
  - (c) the literal marker string '[EXTRACTION-DAMAGED]', treating Rule 5.2.5 as reaching non-cell verbatim text, with the raw renderings in the Markdown
  - (d) the literal marker string '[CONVENTION-GAP:1]', which is what this deliverable carries
  - (e) an extension of the §8.3 schema giving the caption the cell-shaped damage structure of Rule 5.3 — not available to this task, which may not edit the convention
- `what_was_done:` NOTHING WAS TRANSCRIBED into table.caption_verbatim: it carries the literal marker '[CONVENTION-GAP:1]'. All five extractor renderings of the caption are preserved verbatim, each in its own fenced block with its own Locus line and Extraction note, in sec_table1.md § 'Caption and headers, verbatim'. No caption byte was restored, normalised or reconciled anywhere.
- `decision_needed_from:` coordinator

### CONVENTION-GAP:2

- `id:` `CONVENTION-GAP:2`
- `cell_or_locus:` unit_locus on all 150 cells, and table.table_unit_locus (SEC, Table 1, 10/10)
- `what_is_undetermined:` When the source states no unit at any level, the convention does not determine (a) the level at which the absence is recorded — Rule 1.1.4 records a unit at the level at which it is stated, and an absence is stated at no level; (b) the value of unit_locus / table_unit_locus — Rule 1.2 requires a string, the §8.3 skeleton types the field as null, and Rule 3.1.4's remedy of a '_reason' sibling is forbidden by §8.3's fixed key set and key order; (c) the counting basis for the resulting NOT-STATED-BY-SOURCE markers — per cell (150), per column (10), or per table (1).
- `candidate_renderings:`
  - (a) unit_locus: null on every cell, table_unit_locus: null, NOT-STATED-BY-SOURCE counted once for the table
  - (b) unit_locus: 'NOT-STATED-BY-SOURCE' as a string on every cell, counted 150 times
  - (c) unit_locus: a prose string naming the five loci of Rule 1.1.2 that were read and found to state no unit, counted once per cell
  - (d) unit_locus: null with a 'unit_locus_reason' sibling per Rule 3.1.4, which §8.3's fixed key order forbids
  - (e) the literal marker string '[CONVENTION-GAP:2]', which is what this deliverable carries
- `what_was_done:` NOTHING WAS TRANSCRIBED into unit_locus or table_unit_locus: all 151 of those fields carry the literal marker '[CONVENTION-GAP:2]'. The absence of a unit itself IS recorded, per Rule 1.1.3, as unit: null + unit_status: 'NOT-STATED-BY-SOURCE' on all 150 cells and as '[unit: NOT-STATED-BY-SOURCE]' in all 10 Markdown column headers per Rule 1.2, whose form for this case IS determined. No unit was inferred from magnitude, convention, a sibling table, another document, or the transcriber's knowledge. The counting basis actually used is stated at the head of the marker summary.
- `decision_needed_from:` coordinator

### CONVENTION-GAP:3

- `id:` `CONVENTION-GAP:3`
- `cell_or_locus:` the <ROW_SLUG> component of all 150 cell ids (SEC, Table 1, 10/10)
- `what_is_undetermined:` Rule 3.1.5 builds a cell id as <SOURCE_KEY>.<TABLE_LABEL_SLUG>.<ROW_SLUG>.<COL_SLUG> and its worked example is a table with one dedicated row-label column. SEC Table 1 has no dedicated row-label column: its rows are keyed jointly by two printed data columns, 'param' and 'mem', and 'param' alone repeats across three rows. The convention does not determine which printed text is the row label of such a row, nor how two key columns are joined before the slug rule is applied.
- `candidate_renderings:`
  - (a) row_label '348864 1/3' (the two key cells as printed, left to right, single-space joined) → slug '348864_1_3', which is what this deliverable carries
  - (b) row_label '348864' → slug '348864', which is not an identifier here: it collides across the three mem rows of each parameter set
  - (c) row_label 'param 348864 mem 1/3' (key columns named) → slug 'param_348864_mem_1_3'
  - (d) row_label 'mceliece348864 1/3', using the prose form the surrounding text uses — rejected without a ruling because 'mceliece348864' is not what the row prints
  - (e) a positional row index, e.g. 'r02' — rejected without a ruling because it is not printed anywhere in the source
- `what_was_done:` THIS ENTRY DOES NOT READ 'nothing was transcribed', and that departure is deliberate and is also recorded as DEV-2 under '## Deviations'. Rule 7.1.2 would place the marker in the affected field, but the affected field is the cell id itself: marking 150 ids would leave every transcribed value with no identifier and would destroy every provenance link in the deliverable, which Rule 7.1.4 ('a gap blocks one value, not the task') cannot have intended. Rendering (a) was applied to all 150 ids and is stated explicitly in sec_table1.md § TRANSCRIBED with a worked example. It uses only printed source text and the unmodified §3.1.5 slug rule, and it is the only listed candidate that both uses only printed text and yields distinct ids. If the coordinator rules otherwise, every id in this deliverable must be re-keyed by a superseding record; no value, locus, or marker in it depends on the choice.
- `decision_needed_from:` coordinator

None of the three gaps touches a transcribed value. Every one of the 150 values,
its row label, its column header, its page and its section are unaffected by how
the coordinator rules on any of them.

---

## Deviations

Recorded under AGENTS.md rule 8. None was discarded and none is presented as a
result.

**DEV-1 — `pdftotext -bbox` crashed (infrastructure_error).** A fourth pass-2
extractor configuration was planned: poppler's `-bbox` mode, which emits per-word
bounding boxes. Both to stdout and to a file it terminated with
`libc++abi: terminating due to uncaught exception of type std::out_of_range:
basic_string`, exit 134 (SIGABRT), leaving a 179-byte truncated XML file. poppler
26.04.0 on macOS 26.6 arm64. It was replaced with `-raw`. **This is a tool defect
and is not evidence about the source**, and it cost no coverage: pass 2 still ran
three distinct extractor configurations and pass 1 already had a positional
reconstruction from pdfminer's own glyph coordinates.

**DEV-2 — `[CONVENTION-GAP:3]` carries no in-artifact marker, contrary to Rule
7.1.2.** Rule 7.1.2 places the marker in the affected field. Gap 3's affected
field is the cell id, and marking 150 cell ids `[CONVENTION-GAP:3]` would leave
every transcribed value without an identifier and destroy every provenance link
in the deliverable — which Rule 7.1.4 ("a gap blocks one value, not the task")
cannot have intended. The obstruction entry is filed in full, its
`what_was_done` field says outright that it does not read "nothing was
transcribed", and the rendering used is stated in `sec_table1.md` § TRANSCRIBED
with a worked example. **This is a deviation, it is not a discretionary
improvement to the convention, and a coordinator ruling supersedes it.**

**DEV-3 — a fourth file, `source_access_log.yaml`, beyond the three declared
deliverables.** Convention Rule 3.1.7 requires retrieval-side facts to live in
`source_access_log.yaml` in the same task directory; the task card's deliverable
list names three files. The file is inside the task's declared `write_scope`, so
it was written rather than dropping a binding requirement, and it is reported as
a fourth artifact path rather than added silently.

**DEV-4 — one key added to the `§8.3` fixed JSON schema.** `§8.1` requires the
binding header to appear in `sec_table1.json` "as a JSON field", and `§8.3`'s
fixed schema has no field carrying those two lines — its `convention` field holds
a task id, not the path. A single key `binding_header`, first in key order,
carries the header's exact two lines. No other key was added, removed or
reordered. Consequence, stated rather than worked around: `sec_table1.json`
carries no claim-tier field, because `§8.3` provides none; the claim tier is
stated in `sec_table1.md` and in this report.

**DEV-5 — a `title_as_printed` line join, disclosed.** SEC's title page prints
the title on three centred lines. `sources[0].title_as_printed` renders them on
one line, each line break replaced by a single space and nothing added; the two
colons are the source's. The unedited three lines are quoted verbatim in
`sec_table1.md` § Sources with their own `Locus:` line. This is recorded because
an undisclosed join inside something labelled "as printed" is validator
`TASK-20260803-409c5e`'s **Q3** defect (convention § 12, V-2), and disclosure is
the whole point of the rule it breaches.

**DEV-6 — a TLS verification failure, fixed by adding a CA bundle and not by
weakening TLS.** The post-write verification (below) fetched SEC a third time with
a different HTTP client, `python urllib.request`. The first attempt raised
`ssl.SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify
failed: unable to get local issuer certificate`, because that interpreter ships no
CA bundle. **TLS verification was not disabled and no unverified context was
created;** `certifi 2026.07.22` was installed into the scratchpad venv and passed
explicitly as `cafile`. Recorded because the tempting fix here is the forbidden
one. Second attempt: HTTP 200, 332574 bytes, same sha256.

**Not a deviation, recorded so it is not mistaken for one:** the three extractors
of pass 1 exceed Rule 5.2.5's requirement of two, and pass 2 adds three more
configurations. Rule 5.2.5 sets a floor.

---

## What was not obtained

1. **Reference [33] of SEC, the Esser–Bellini estimator itself.** Not attempted;
   outside this task's scope. Consequence, stated plainly: **nothing read in this
   task establishes what the numbers in Table 1 count, nor what the column headers
   `BC`, `BJMM`, `pdw`, `MO`, `BM` name.** SEC defines only the `mem` column, in
   its caption. A reader wanting either must read [33].
2. **`iacr:2026/1232`'s PDF, by any route.** Not attempted. The 403 is
   path-scoped and reproducible, circumvention is forbidden, and AGENTS.md rule 5
   makes a blocked route a recorded outcome. This is a different source from SEC;
   it is named only so that the prohibition is visibly observed. No 403 was met
   in this task by any route.
3. **The rendered PDF was not read visually.** All readings are from the three
   extractors' output. Where they disagree — the caption — nothing was
   reconciled, and a reviewer wanting to settle it must render the PDF at sha256
   `db17ef08…` and look.

Nothing else was sought and not obtained. No locus of Table 1 is
`[NOT-OBTAINED]`.

---

## Conformance checklist (§9), item by item

| # | Requirement | Conforms | Basis |
|---|---|---|---|
| 1 | Binding header present in all three artifacts, byte-exact (§8.1). | **yes** | `sec_table1.md` lines 3–4 and this file's lines 3–4 carry the two lines as written. `sec_table1.json` carries them in the `binding_header` field, exactly, `\n`-separated; the added key is DEV-4. |
| 2 | Every source has a full 64-hex sha256, or `not_obtained` + reason (Rule 3.1, 3.3). | **yes** | SEC: full 64-hex in `sec_table1.md` § Sources and in `sec_table1.json`. `source_access_log.yaml` seq 0 (the local-repository search, which retrieved nothing) carries `sha256: not_obtained` with a `sha256_reason`. |
| 3 | Every abbreviated hash is first-8 + `…` (Rule 3.2). | **yes** | One abbreviation form occurs across the deliverables: `db17ef08…`. Checked by regular expression over `sec_table1.md`: the set of matches has one element. Convention § 12 V-7 is the defect this avoids. |
| 4 | Every cell has an id built by the §3.1.5 slug rule. | **yes** | 150 ids, all of the form `SEC.table_1.<row_slug>.<col_slug>` with the slug rule applied unmodified in code, and all 150 distinct (checked). The `<ROW_SLUG>` question is `[CONVENTION-GAP:3]`. |
| 5 | Every cell has `unit`, `unit_status`, `unit_locus` (Rule 1). | **yes** | All 150 cells carry all three keys, in the §8.3 order (checked: the cells share one key tuple). `unit: null`, `unit_status: "NOT-STATED-BY-SOURCE"`, `unit_locus: "[CONVENTION-GAP:2]"`. |
| 6 | No transcribed value was re-rounded or re-notated; every JSON `value_printed` is a string (Rule 2). | **yes** | Checked in code: all 150 `value_printed` are `str`. No value was typed by hand at any point — every one comes from the extractor output through the generator script, so re-rounding was not merely avoided but structurally impossible. `1/3` and `1/2` are not converted to decimals; `0` is not written `0.0`; `283.0`, `268.0`, `321.0`, `201.0` keep their trailing zeros; no `≈` occurs in this table. |
| 7 | Exactly one `rounding_rule` line, in one of the two permitted forms, iff any derived value exists (Rule 2.1.6). | **yes** | No derived value exists, and no `rounding_rule` line appears in any deliverable (checked: zero lines beginning `rounding_rule`). Convention § 12 V-3 is the defect this avoids. |
| 8 | No derived value appears under `cells` or under `## TRANSCRIBED` (Rule 4.1). | **yes** | `derived` is `[]` and every entry of `cells` is a value printed in the table. The `## DERIVED — NOT TRANSCRIBED` section reads `None. No derived value appears in this deliverable.` Nothing was recomputed, cross-checked arithmetically, or converted — this table offers the temptation (e.g. differencing the `mem` rows) and it was refused. |
| 9 | Every derived value carries formula, formula_source, input cell ids, computation, rounding rule (Rule 4.3). | **yes** | Vacuously: there are no derived values. |
| 10 | No derived value consumes a non-`OK` cell (Rule 4.4). | **yes** | Vacuously: there are no derived values. |
| 11 | No damaged value is reconstructed anywhere; every conjectured reading appears only in a damage note with the required prefix (Rule 5.2, 5.4). | **yes** | No cell is damaged. Four conjectured readings appear in the deliverables — the caption's inserted spaces, and the three flattened superscripts in quoted prose — and every one is on an `Extraction note:` line outside its verbatim block, prefixed exactly `NOT TRANSCRIBED — conjectured reading:`. None is carried in any value field, any table cell, any JSON `cells` entry, or any summary. This is the V-1 discipline. |
| 12 | Two extractors were run on every table and their agreement is recorded (Rule 5.2.5). | **yes** | Three in pass 1 and three further configurations in pass 2, on independently retrieved bytes. Agreement is recorded per cell in `extractor_agreement` and in aggregate under `## Second pass`. The one disagreement, on the caption, is recorded rather than resolved. |
| 13 | Marker summary present, all six counts stated including zeros (Rule 5.2.6). | **yes** | `sec_table1.md` § Marker summary and `sec_table1.json.marker_counts` carry the same six counts, with the counting basis stated and the discrepancy against a naive text search explained. |
| 14 | `RECALLED-NOT-READ` count is 0 (Rule 5.1). | **yes** | 0. Every value, header, caption and quotation was read from the retrieved bytes at sha256 `db17ef08…` in this session. Nothing came from BATCH-001's quotation of SEC, from a summary, or from memory. |
| 15 | Every verbatim block has a `Locus:` line before it and, where artifacts are present, an `Extraction note:` line after it; no edit inside any block (Rule 6.2). | **yes** | Checked in code over `sec_table1.md`: 12 fenced blocks, all balanced, none with a language tag, and every one immediately preceded (across blank lines only) by a line beginning `Locus: `. The same holds for this file's four blocks. Every block's contents were written straight from an extractor output file by the generator script, never retyped, so no edit inside a block was possible. |
| 16 | Every `[CONVENTION-GAP:<n>]` has a matching `## Obstructions` entry with all six fields (Rule 7.1). | **yes** | Gaps 1, 2 and 3 each have an entry with exactly the six fields in the required order (checked in code against `sec_table1.json.obstructions`). Gap 3 additionally carries no in-artifact marker; that is DEV-2, stated in its own `what_was_done` field and under `## Deviations`. |
| 17 | Second pass performed and its disagreements reported (§8.4). | **yes** | Second retrieval, three different extractor configurations, separately written parser. Zero disagreements on 150 cells and on the header row; the caption disagreement is reported and is a pass-1 finding that pass 2 reproduced. |
| 18 | Claim tier stated as toy; no security statement about Classic McEliece in either direction. | **yes** | Stated in `sec_table1.md` and in this file. No deliverable asserts that any parameter set is secure or insecure, meets or misses any category, or that any attack cost is achievable. SEC's own statements on those points are quoted, attributed to SEC, and not adopted; and because reference [33] was not obtained, this task could not evaluate them even if it were permitted to. |

**18 of 18 `yes`.** Two qualifications, so the row of `yes` values is not read
as more than it is: items 9 and 10 are vacuous, and item 16's `yes` is about the
obstruction entries, while the placement of gap 3's marker is a recorded
deviation (DEV-2) and not a conformance.

Three deliverable-level items the checklist does not cover, checked anyway:
§8.2's section order is exactly the nine sections in the order listed; §8.4's five
required section headings are present in this file; §8.5's encoding requirements
hold for all four artifacts (UTF-8, no BOM, LF only, no trailing whitespace on any
line, final newline present — checked in code).

---

## Post-write verification

Run after the three artifacts were written, against a **third** retrieval by a
different HTTP client (`python urllib.request`, seq 3 of the access log, TLS
verification on — see DEV-6), and by a verifier written without reference to the
pass-1 or pass-2 comparison data:

| Check | Result |
|---|---|
| Third retrieval byte count and sha256 vs the values declared in `sec_table1.json` | match (332574; `db17ef08…`) |
| 150 `sec_table1.json` cells vs a fresh extraction of the third retrieval | 150/150 equal, 0 mismatches |
| `sec_table1.md` § TRANSCRIBED table vs `sec_table1.json` `cells` | 15 rows × 10 columns, 150/150 equal, 0 mismatches |
| All 150 cell ids re-derived from the stated §3.1.5 slug rule | 150/150 equal, 0 mismatches |

This is the executor completion gate's "raw data and summary tables agree" and
"reproduces from the recorded command and revision" check. It verifies the
deliverables against the source; it verifies nothing about the source.

---

## What this task did NOT establish

Stated plainly, because a clean 150-cell transcription invites more weight than
it can carry.

- It did not establish what the numbers mean. SEC states no unit for them and
  reference [33] was not obtained.
- It did not check the numbers against the estimator, against any other source,
  or against each other. It did not recompute anything.
- It did not evaluate SEC's own reasoning about categories, memory models, or
  bit-operation counts. Those passages are quoted so the numbers are not read
  without them, not endorsed.
- It did not correct, edit or supersede any BATCH-001 artifact. The convention's
  § 12 names V-1…V-7 in those files; this task read them as worked examples and
  opened none of them for write.
- It made no git commit, staged nothing, and changed no ledger, hypothesis, goal
  or knowledge record.
