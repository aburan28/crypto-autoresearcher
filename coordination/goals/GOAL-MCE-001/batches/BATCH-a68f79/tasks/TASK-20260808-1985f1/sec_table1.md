# Esser–Bellini SEC Table 1 — transcription

Transcription convention: coordination/goals/GOAL-MCE-001/batches/BATCH-a68f79/tasks/TASK-20260808-a9f648/transcription_convention.md
Binding authority: DEC-20260803-a5b9b1 D-10

**Task:** TASK-20260808-1985f1 · **Goal:** GOAL-MCE-001 · **Batch:** BATCH-a68f79
**Role:** executor · **Date:** 2026-08-09 (UTC; local session date 2026-08-08)

**Inference record (verbatim, as required by the task card):** requested_policy
`executor-implementation`, degraded_allowed false, fallback_allowed false; per
CLAUDE.md per-role selection is process-level under Claude Code and subagents keep
model: inherit, so the resolved model is the session model; fallback_used: false.
model_verified: false (no `orchestration.adapter doctor --probe` receipt for this
session).

**Budget:** authorized 1 run, 2 GB, 3600 s. One retrieval-and-extraction run was
executed, in two passes over the same declared budget. No budget limit was reached.

**Claim tier: toy, unchanged. `GOAL-MCE-001.active_hypothesis_ids`: empty,
unchanged.** This document transcribes a published table. It establishes nothing
whatever about Classic McEliece, in either direction, and no line of it may be
cited as evidence about any cryptosystem. The numbers below are the source's
report of a third-party estimator's output, transcribed; they are not this
program's measurement, estimate, or endorsement.

---

## Sources

| Field | Value |
|---|---|
| `key` | `SEC` |
| `title_as_printed` | "Classic McEliece: conservative code-based cryptography: guide for security reviewers" |
| `url` | `https://classic.mceliece.org/mceliece-security-20221023.pdf` |
| `http_status` | 200 |
| `bytes` | 332574 |
| `sha256` | `db17ef0879cb8822120c312b7290f7db82fe9fc356bd16058ad334a512b523fa` |
| `pages` | 36 |
| `extractors` | poppler pdftotext 26.04.0; pypdf 6.15.0; pdfminer.six 20260107 |
| `access_log_ref` | `source_access_log.yaml` seq 1 (pass 1) and seq 2 (pass 2), this task directory |

The title as the title page actually prints it, unedited:

Locus: SEC, title page, null/1

```
                        Classic McEliece:
             conservative code-based cryptography:
                  guide for security reviewers
```

Extraction note: the leading indentation is the extractor's rendering of the
source's centring and is left as extracted. The title page prints no page number,
so `page_printed` is `null`; it is not invented.

`title_as_printed` in the table above renders those three printed lines on one
line, replacing each line break with a single space and adding nothing. The two
colons are the source's. **This is a stated transformation, not a silent one**,
and it is disclosed here because the field is named `as printed`; the unedited
bytes are immediately above.

Abbreviated form of this hash, used nowhere else in this document but fixed by
Rule 3.2 for any use: `db17ef08…`.

The sha256 recorded here was computed from the bytes retrieved in this session.
It equals the sha256 recorded by `TASK-20260803-f3aece/source_access_log.yaml`
seq 7 for the same URL; that equality is reported as an observation, and the hash
in this table is this session's own computation, not a copy of that record.

---

## Caption and headers, verbatim

### Section heading containing the table

Locus: SEC, section 3.5, 9/9

```
3.5    Concrete costs of information-set decoding
```

### Sentence introducing the table, and the model assumptions it states

Quoted under Rule 6.1.2 (assumptions, cost model) and Rule 6.1.5 (the passage in
which a unit would be stated, quoted so its absence is checkable).

Locus: SEC, section 3.5, 9/9

```
As numerical examples of the importance of memory access, Table 1 reports output of the
Esser–Bellini security estimator [33] for each of the selected Classic McEliece parameter sets,
under three different models supported by the estimator:
   • The rows where “mem” is 0 use a model making a physically implausible assumption
     of free access to arbitrarily large amounts of memory. In this model, the 2011/2012
     algorithms using “representations” provide noticeable speedups compared to Stern’s
     1989 algorithm.
   • The rows where “mem” is 1/2 use a model assigning plausible square-root costs to
     memory access. The rows where “mem” is 1/3 use a model assigning cube-root costs to
     memory access. In these models, the algorithms using “representations” provide much
     smaller speedups compared to Stern’s algorithm. In other words, most of the claimed
     speedup from these algorithms at cryptographic sizes relies on assigning unrealistically
     low costs to memory access.
```

Extraction note: the leading three-space indent and the five-space bullet
continuation indent are the extractor's rendering of the source's list layout and
are left as extracted. `“` / `”` are U+201C / U+201D in the source.

### Column header row, as printed

Locus: SEC, Table 1, 10/10

```
       param    mem     Prange    Stern   Dumer       BC    BJMM       pdw     MO      BM
```

Extraction note: horizontal spacing is the extractor's column alignment. All
three pass-1 extractors and all three pass-2 extractor configurations return the
same ten header tokens in the same order; see `transcription_report.md`.

**No unit appears in any column header.** The only column SEC defines is `mem`,
and it defines it in the caption. **SEC states no definition of the columns
`BC`, `BJMM`, `pdw`, `MO`, `BM`**: a full-text search of the extracted document
(poppler `-layout`, all 36 pages) finds `BJMM` on exactly two lines — this header
row and bibliography entry [15] — and finds `BC`, `pdw`, `MO` and `BM` on exactly
one line each, this header row. `Prange`, `Stern` and `Dumer` do occur elsewhere
in SEC as authors of information-set-decoding algorithms, and `param` is used in
the caption's phrase `parameter sets`, but SEC states no sentence binding any of
those names to a column of this table. These absences are recorded, not filled:
the estimator of reference [33] was not obtained (see `## Not obtained`).

### Caption

Rule 5.2.5 makes extractor disagreement by itself sufficient to mark damage, and
the extractors disagree here. **Nothing below is restored, normalised or
reconciled.** Each extractor's raw bytes are given in their own block. The
difference is confined to inserted spaces; see `[CONVENTION-GAP:1]` in
`transcription_report.md` for the form question this raises for the single-valued
JSON field `table.caption_verbatim`, which is why that field carries the gap
marker rather than one extractor's bytes.

#### E-A — poppler pdftotext 26.04.0 (-layout, page 10 (positional)), pass 1

Locus: SEC, Table 1, 10/10

```
Table 1: Output of the Esser–Bellini estimator for the selected Classic McEliece parameter sets.
The “mem” column is 0 for estimates assuming free memory access, 1/3 for estimates using a cube-
root assumption, and 1/2 for estimates using a square-root assumption. Some cost components are
ignored in all estimates.
```

Extraction note: E-A and E-C return byte-identical caption text (checked by
string equality, not by eye).

#### E-B — pypdf 6.15.0 (extract_text() default mode (content-stream order)), pass 1

Locus: SEC, Table 1, 10/10

```
T able 1: Output of the Esser–Bellini estimator for the selected Classic McEliece parameter sets.
The “mem” column is 0 for estimates assuming free memory access, 1 /3 for estimates using a cube-
root assumption, and 1 /2 for estimates using a square-root assumption. Some cost components are
ignored in all estimates.
```

Extraction note: this extractor emits `T able 1`, `1 /3` and `1 /2` where E-A
and E-C emit `Table 1`, `1/3` and `1/2`. The inserted spaces are left exactly as
extracted and are NOT removed. NOT TRANSCRIBED — conjectured reading: the
inserted spaces are kerning artefacts of this extractor's default mode rather than
source content; that reading is a conjecture, it repairs nothing, and it is
carried in no value field of any deliverable of this task.

#### E-C — pdfminer.six 20260107 (extract_text() + LTChar positional reconstruction), pass 1

Locus: SEC, Table 1, 10/10

```
Table 1: Output of the Esser–Bellini estimator for the selected Classic McEliece parameter sets.
The “mem” column is 0 for estimates assuming free memory access, 1/3 for estimates using a cube-
root assumption, and 1/2 for estimates using a square-root assumption. Some cost components are
ignored in all estimates.
```

Extraction note: E-A and E-C return byte-identical caption text (checked by
string equality, not by eye).

#### P2-B — pypdf 6.15.0 (layout mode), pass 2

Locus: SEC, Table 1, 10/10

```
Table 1:  Output of the Esser–Bellini estimator for the selected Classic McEliece parameter sets.
The “mem” column is 0 for estimates assuming free memory access, 1/3 for estimates using a cube-
root assumption, and 1/2 for estimates using a square-root assumption. Some cost components are
ignored in all estimates.
```

Extraction note: recorded because it is the same library as E-B in a different
mode and it reproduces neither E-B's `T able` nor E-B's `1 /3` and `1 /2`; it does
insert a second space after `Table 1:`, where the other four extractions have one.
Left exactly as extracted. NOT TRANSCRIBED — conjectured reading: the doubled
space is this mode's column padding rather than source content; a conjecture,
carried in no value field.

#### P2-C — pdfminer.six 20260107 (non-default LAParams), pass 2

Locus: SEC, Table 1, 10/10

```
Table 1: Output of the Esser–Bellini estimator for the selected Classic McEliece parameter sets.
The “mem” column is 0 for estimates assuming free memory access, 1/3 for estimates using a cube-
root assumption, and 1/2 for estimates using a square-root assumption. Some cost components are
ignored in all estimates.
```

Extraction note: byte-identical to E-A and E-C.

### Cost-model, rounding and scope sentences bearing on the numbers

Quoted under Rule 6.1.2 and Rule 6.1.4. They are quoted, not summarised, because
removing them changes what the numbers mean.

Locus: SEC, section 3.5, 10/10

```
If these requirements include “mem” being 0, counting only bit operations with free memory
access, then Table 1 raises the following concern: the smallest number in the table, 140.8 for
mceliece348864, is slightly below 143. However, the underlying estimator from [33] counts
each vector operation as just 1 operation: in particular, finding C collisions between two lists,
each list containing L vectors, is assigned cost 2L + C, no matter what the vector length is.
Consequently, the 140.8 actually counts more than 2143 bit operations. The exact numbers
in Table 1 should be expected to be superseded by larger numbers from future estimators
that count bit operations.
```

Extraction note: **this block contains flattened superscripts and is not
repaired.** `2143` in the penultimate line is the extractor's rendering of a
printed power of two whose exponent markup is flattened. NOT TRANSCRIBED —
conjectured reading: `2^143`. That reading is a conjecture, it is carried in no
value field, and no cell of this transcription depends on it.

Locus: SEC, section 3.5, 10/10

```
More importantly, the 140.8 is for an attack using memory 286.6 , according to the same
estimator. Accounting for costs of memory access shows that all known attacks against
```

Extraction note: same flattening. `286.6` is the extractor's rendering of a
printed power of two. NOT TRANSCRIBED — conjectured reading: `2^86.6`. A
conjecture; carried in no value field. The `86.6` memory figure is **not** in
Table 1 and is not transcribed by this task.

Locus: SEC, section 3.5, 11/11

```
the assignment of 460896 to “Category 3” (AES-192) since NIST estimates 2207 operations
for brute-force AES-192 key search while Table 1 says 201.0, which is below 207; but, as
noted above, the estimates in the table are underestimates of bit operations, for example
counting each vector operation as just 1 operation.
```

Extraction note: same flattening; `2207` renders a printed power of two. NOT
TRANSCRIBED — conjectured reading: `2^207`. A conjecture; carried in no value
field. This passage is quoted because it states the source's own scope caveat on
the transcribed numbers.

---

## TRANSCRIBED

Locus for every cell below: `source_key` SEC, `page_printed` 10, `page_pdf` 10,
`section` `3.5    Concrete costs of information-set decoding`, `table_label`
`Table 1`, `caption` as quoted above, `row_label` and `column_header` as given by
the row and column of each cell. Per-cell loci are carried in full in
`sec_table1.json`.

Cell ids follow Rule 3.1.5 mechanically:
`SEC.table_1.<row_slug>.<col_slug>`, where `<row_slug>` slugs the row's printed
label `"<param> <mem>"` and `<col_slug>` slugs the printed column header. Worked
example: row `348864 1/3`, column `MO` → `SEC.table_1.348864_1_3.mo`.
See `[CONVENTION-GAP:3]` in `transcription_report.md`: this table has no dedicated
row-label column and the convention does not fix `<ROW_SLUG>` for that case.

Every column carries `[unit: NOT-STATED-BY-SOURCE]`. Rule 1.1.2 admits five loci
for a unit statement and SEC states one at none of them: the caption is quoted
above and states none; the column header row is quoted above and states none; the
row labels are the `param` and `mem` cells of the table below and state none;
**the table has no unit row** — the header row is followed directly by the first
data row, as the quoted header row and the extractor dumps in
`transcription_report.md` show; and the sentence introducing the table is quoted
above and states none. Rule 1.1.3 forbids inferring a unit from magnitude, from
convention, from a sibling table, from another document, or from the
transcriber's knowledge, and none is inferred here. The surrounding prose does
exponentiate individual table entries (`2143`, `2246.6`, `2279.2` as extracted);
reading that as establishing a unit for the table would be exactly the inference
Rule 1.1.3 forbids, so it is not made, and the passages are quoted above so a
reviewer can check the absence rather than take it on trust.

| param [unit: NOT-STATED-BY-SOURCE] | mem [unit: NOT-STATED-BY-SOURCE] | Prange [unit: NOT-STATED-BY-SOURCE] | Stern [unit: NOT-STATED-BY-SOURCE] | Dumer [unit: NOT-STATED-BY-SOURCE] | BC [unit: NOT-STATED-BY-SOURCE] | BJMM [unit: NOT-STATED-BY-SOURCE] | pdw [unit: NOT-STATED-BY-SOURCE] | MO [unit: NOT-STATED-BY-SOURCE] | BM [unit: NOT-STATED-BY-SOURCE] |
|---|---|---|---|---|---|---|---|---|---|
| `348864` | `0` | `173.4` | `151.4` | `151.4` | `151.5` | `141.9` | `143.4` | `140.8` | `142.7` |
| `348864` | `1/3` | `176.7` | `159.3` | `159.7` | `159.7` | `159.1` | `157.8` | `156.4` | `157.5` |
| `348864` | `1/2` | `178.3` | `162.8` | `163.2` | `163.2` | `162.2` | `160.3` | `158.6` | `159.8` |
| `460896` | `0` | `216.8` | `193.3` | `193.2` | `193.3` | `180.8` | `182.6` | `179.8` | `182.1` |
| `460896` | `1/3` | `220.4` | `201.7` | `202.2` | `202.2` | `201.6` | `200.6` | `198.6` | `199.8` |
| `460896` | `1/2` | `222.1` | `205.3` | `205.8` | `205.8` | `204.8` | `203.4` | `201.0` | `202.2` |
| `6688128` | `0` | `295.7` | `268.0` | `267.9` | `268.0` | `247.3` | `248.8` | `246.2` | `249.6` |
| `6688128` | `1/3` | `299.4` | `279.2` | `279.5` | `279.5` | `278.9` | `277.6` | `274.9` | `276.4` |
| `6688128` | `1/2` | `301.2` | `283.0` | `283.3` | `283.3` | `282.3` | `280.4` | `278.2` | `279.4` |
| `6960119` | `0` | `296.8` | `268.4` | `268.3` | `268.4` | `246.6` | `248.4` | `245.7` | `249.2` |
| `6960119` | `1/3` | `300.4` | `280.1` | `280.5` | `280.5` | `279.4` | `278.6` | `275.8` | `277.3` |
| `6960119` | `1/2` | `302.2` | `283.9` | `284.3` | `284.3` | `283.3` | `281.4` | `279.2` | `280.3` |
| `8192128` | `0` | `334.1` | `303.2` | `307.4` | `303.4` | `277.7` | `279.1` | `275.6` | `281.1` |
| `8192128` | `1/3` | `337.7` | `316.8` | `317.1` | `317.1` | `316.3` | `315.5` | `311.9` | `313.3` |
| `8192128` | `1/2` | `339.5` | `320.7` | `321.0` | `321.0` | `320.0` | `318.6` | `315.6` | `317.0` |

150 cells, 15 rows × 10 columns, in source order (rows top to bottom, columns
left to right as printed). Values are copied glyph-for-glyph: no trailing zero is
stripped or added, no decimal is re-rounded, `1/3` and `1/2` are not converted to
decimals, and `0` is not written `0.0`.

SEC states no rounding language for these numbers, so no
`source_rounding_statement` is recorded for any cell; the field is `null` in
`sec_table1.json` with `unit_status` carrying the absence of a unit separately.

---

## [EXTRACTION-DAMAGED] details

**None. No cell of this transcription carries `[EXTRACTION-DAMAGED]`.**

This is a claim about the 150 cells only, and it is the claim BATCH-001's
`markers set: 0` declaration could not support. The evidence for it:

- Three independent extractors in pass 1 (E-A poppler `-layout`, positional; E-B
  pypdf default mode, content-stream order; E-C pdfminer.six with LTChar
  positional reconstruction) return the same 15×10 array. Compared
  cell-by-cell by string equality in code: 0 disagreements out of 150.
- Column-to-row association is read from the rendered layout, not inferred from
  extraction order: E-A and E-C both reconstruct rows from glyph coordinates.
  (E-C's flow-mode `extract_text()` output does emit the table column-major and
  would have been unusable alone; that raw output is preserved in
  `transcription_report.md`.)
- No `(cid:NN)` token, no ligature artefact, and no flattened superscript occurs
  anywhere in the 150 cells or the header row. Flattened superscripts DO occur in
  the surrounding prose and are left unrepaired and annotated above.
- Three further extractor configurations in pass 2, on an independently
  re-retrieved copy of the file, return the same 15×10 array: 0 disagreements.

The caption is a separate matter: the extractors disagree on it, it is not a
cell, and it is handled above and under `[CONVENTION-GAP:1]`.

---

## DERIVED — NOT TRANSCRIBED

None. No derived value appears in this deliverable.

---

## Marker summary

Counting basis, stated because Rule 5.2.6 does not fix one: a marker is counted
once per **field of `sec_table1.json` it is assigned to**. The same counts appear
in that file's `marker_counts` block. A raw text search over that file returns
MORE occurrences than these counts — 156 for `[CONVENTION-GAP:` against 152
assignments, 156 for `NOT-STATED-BY-SOURCE` against 150, and 1 for
`RECALLED-NOT-READ` against 0 — because the `obstructions` entries and the
`marker_counts` keys name the markers in prose. That difference is stated so the
counts below cannot be mistaken for a grep total.

| Marker | Count | Where |
|---|---:|---|
| `[EXTRACTION-DAMAGED]` | 0 | — |
| `[NOT-STATED-BY-SOURCE]` | 150 | `unit_status` of each of the 150 cells |
| `[NOT-OBTAINED]` | 0 | — |
| `[DERIVED]` | 0 | — |
| `[RECALLED-NOT-READ]` | 0 | — |
| `[CONVENTION-GAP:<n>]` | 152 | 1 × `table.caption_verbatim` (gap 1); 150 × cell `unit_locus` + 1 × `table.table_unit_locus` (gap 2) |

Three distinct gap ids are open (1, 2, 3). Gap 3 carries **no** in-artifact
marker, deliberately and as a recorded deviation: the only field it could occupy
is the cell id itself, and marking 150 cell ids would destroy every provenance
link in this deliverable. It is reported in full under `## Obstructions` in
`transcription_report.md`.

`[RECALLED-NOT-READ]` is 0. Every value, header, caption and quotation in this
document was read from the retrieved bytes at sha256 `db17ef08…` in this session.
Nothing here is transcribed from a summary, from another record's quotation of
SEC, or from memory.

---

## Not obtained

**No locus of Table 1 is recorded `[NOT-OBTAINED]`.** The table was retrieved and
read in this session; all 15 rows and all 10 columns are transcribed.

Recorded here so the boundary of what was read is explicit, and counted in no
marker total because neither is a cell or a locus of Table 1:

1. **Reference [33], the Esser–Bellini estimator itself, was not obtained.** No
   route to it was attempted in this task; it is outside the task's scope, which
   is to transcribe SEC's Table 1. Consequence: the meaning of the column headers
   `BC`, `BJMM`, `pdw`, `MO`, `BM`, and the meaning and unit of the numbers, are
   not established by anything read here.
2. **`iacr:2026/1232`'s PDF was not attempted, by any route.** The 403 is
   path-scoped and reproducible, circumvention is forbidden, and AGENTS.md rule 5
   makes a blocked route a recorded outcome. It is a different source from this
   one and is named only to record that the prohibition was observed.
