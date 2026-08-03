# SEC Table 1 — transcription

**Task:** `TASK-20260803-cb44ab` · **Goal:** `GOAL-MCE-001` · **Batch:** BATCH-002
**Question:** `RQ-MCE-e65b3c` · **Date:** 2026-08-03
**Access log:** `source_access_log.yaml` in this directory (route order declared
before the first attempt; every attempt logged).

---

## 0. What this document is, and what it is not

**It is** a transcription of one published table and of the sentences the
publishing document uses to describe that table, from a copy this task fetched
itself and hashed.

**It is not** any of the following, and nothing in it may be read as any of
them:

- It is **not an adoption of a costing convention.** `ISD-FC-2026` is not
  adopted here and is not adoptable by this task: `DEC-20260802-344883` D-6
  records *"ISD-FC-2026 IS NOT ADOPTED… a usable draft, not a binding
  convention"*, and `DEC-20260803-a5b9b1` D-3 records that this goal's own
  claim to bind to it was retracted. This document proposes no replacement
  convention either.
- It is **not a computation.** No arithmetic of any kind was performed on any
  value in the table: no difference, no ratio, no comparison against any
  external figure, no unit conversion, no aggregation.
- It is **not an assessment.** No statement appears here about whether any
  Classic McEliece parameter set is secure, threatened, adequate or
  inadequate — including by implication or by juxtaposition. Where the source
  makes such statements, they are transcribed as **the source's statements**,
  attributed, and not endorsed.
- It is **not a baseline.** What a memory-charged baseline at these parameters
  would still require is named — and deliberately left unfilled — in
  `baseline_gap_statement.md`.

Why this exists: `TASK-20260803-f3aece` **read this table and deliberately did
not transcribe it**, deferring to a costing-convention binding that
`DEC-20260802-344883` D-6 shows does not exist. `DEC-20260803-a5b9b1` D-3
records that under `concrete_cost`. Transcribing a published table is not
adopting a convention.

---

## 1. Source

| Field | Value |
|---|---|
| Short name used here | **SEC** |
| Title as printed | *"Classic McEliece: conservative code-based cryptography: guide for security reviewers"* |
| URL fetched | `https://classic.mceliece.org/mceliece-security-20221023.pdf` |
| HTTP status | 200 |
| Bytes | 332,574 |
| sha256 | `db17ef0879cb8822120c312b7290f7db82fe9fc356bd16058ad334a512b523fa` |
| Fetched at | 2026-08-03T19:52:54Z |
| Pages | 36 |
| Table location | **PDF page 10**, which carries the printed folio **10** — the two agree, so "p.10" is unambiguous for this document |
| Section | 3.5, *"Concrete costs of information-set decoding"* (begins PDF page 9) |

The PDF is **not** committed to this repository (third-party copyright). The
row above is sufficient for a reviewer to re-acquire and hash-compare.

The fetched bytes are **identical** to the copy `TASK-20260803-f3aece` fetched
earlier on 2026-08-03 (its access log seq 7): same status, same byte count,
same sha256. Recorded as an observation about these two retrievals, not as a
claim that the document is stable in general.

SEC attributes the table's contents to an external tool, citing `[33]`. SEC's
own bibliography entry for `[33]`, PDF page 33, verbatim:

> *"[33] Andre Esser and Emanuele Bellini. Syndrome decoding estimator. In
> Goichiro Hanaoka, Junji Shikata, and Yohei Watanabe, editors, Public-Key
> Cryptography—PKC 2022— 25th IACR International Conference on Practice and
> Theory of Public-Key Cryptogra- phy, Virtual Event, March 8–11, 2022,
> Proceedings, Part I , volume 13177 of Lecture Notes in Computer Science ,
> pages 112–141. Springer, 2022. https://eprint.iacr. org/2021/1243."*

(Line-break hyphenation and stray spaces above are the extractor's, left
visible per §2.)

The eprint **abstract** page for 2021/1243 was fetched once (HTTP 200, 16,056
bytes, sha256 `59810b6c…`) solely to record that document's identity:
*"Syndrome Decoding Estimator"*, Andre Esser and Emanuele Bellini (Technology
Innovation Institute), *"A minor revision of an IACR publication in PKC 2022"*.
**The estimator paper itself was not read and its PDF was not requested.** No
cost-model statement anywhere in this package comes from it.

---

## 2. Transcription standard applied

This task applied **the stricter of the two BATCH-001 standards**, per its task
card's named duty 4 — i.e. the `TASK-20260803-292b99` standard, **not** the
`TASK-20260803-f3aece` standard that `DEC-20260803-a5b9b1` D-10 left open.
Concretely:

1. `[EXTRACTION-DAMAGED]` is set **wherever extraction is unreliable**, with
   the mechanical evidence for the finding stated, not asserted.
2. Raw glyph and kerning artifacts (`T able 1`, `1 /2`, `140 .8`, the `ﬁ`/`ﬀ`
   ligatures) are left **visible inside quoted material** rather than silently
   normalised. Where a reading is supplied it appears **outside** the
   quotation and is labelled as this transcriber's reading.
3. No `(cid:NN)` token occurred anywhere in this document's extraction; had one
   occurred it would have been shown raw.

`TASK-20260803-a53f73` is settling the convention (D-10) concurrently. Its
output is **outside this task's read scope and was not read** — disjoint write
scopes, no dependency. If the settled convention differs from the standard
applied here, this package was produced under a standard chosen without
knowledge of it. Recorded so a reviewer can check the two against each other.

### Extraction method and the agreement check

Table 1 is a genuine PDF table, which is the extraction-damage case. It was
recovered by **three independent paths**:

| Path | Tool | Reading order it produces |
|---|---|---|
| A | pypdf 6.14.2 | **Row-major**: 15 data lines + one header line |
| B | pdfminer.six 20260107 (`extract_text`) | **Column-major in blocks**: Dumer/Prange/param interleaved, then Stern, then mem, then MO, pdw, BJMM, BC, then BM |
| C | pdfminer.six character coordinates (`LTChar` x0/x1/y0) | **Geometry only** — rows clustered by baseline y (2.0 pt tolerance), cells by x-gap; ignores both extractors' reading orders |

Result: **150 of 150 cells agree** (15 rows × 10 columns), **0 mismatches**.

Path C additionally checks the part a row-major dump cannot: that each value
sits under the header it is transcribed under. Header token centres vs. the
first data row's cell centres, in points:

| Column | Header centre | Row-1 cell centre |
|---|---:|---:|
| param | 123.0 | 120.8 |
| mem | 164.0 | 173.4 |
| Prange | 206.7 | 211.3 |
| Stern | 250.6 | 251.0 |
| Dumer | 294.1 | 298.3 |
| BC | 342.2 | 337.3 |
| BJMM | 380.9 | 385.4 |
| pdw | 426.9 | 424.4 |
| MO | 466.9 | 463.4 |
| BM | 506.3 | 502.5 |

Each data cell's nearest header is the header it is transcribed under, for all
ten columns.

**Why no table cell carries an `[EXTRACTION-DAMAGED]` marker:** every glyph in
the table region of PDF page 10 (baseline y > 480 pt — body, header and rules;
771 glyphs) is set at **one single font size, 11.96 pt**. There is no
superscript, subscript or size change anywhere inside the table. That is a
measurement, not an impression.

---

## 3. The table, cell by cell

**Provenance of every cell below:** SEC, PDF page 10 (printed folio 10), from
the retrieval whose sha256 is recorded in §1, recovered by all three extraction
paths of §2 in agreement. **Cells marked not obtained: 0. Cells carrying
`[RECALLED-NOT-READ]`: 0.**

Column headers are reproduced **exactly as printed**; §5 records that SEC never
expands the abbreviations, and this document does not expand them either.

| param | mem | Prange | Stern | Dumer | BC | BJMM | pdw | MO | BM |
|---|---|---|---|---|---|---|---|---|---|
| 348864 | 0 | 173.4 | 151.4 | 151.4 | 151.5 | 141.9 | 143.4 | 140.8 | 142.7 |
| 348864 | 1/3 | 176.7 | 159.3 | 159.7 | 159.7 | 159.1 | 157.8 | 156.4 | 157.5 |
| 348864 | 1/2 | 178.3 | 162.8 | 163.2 | 163.2 | 162.2 | 160.3 | 158.6 | 159.8 |
| 460896 | 0 | 216.8 | 193.3 | 193.2 | 193.3 | 180.8 | 182.6 | 179.8 | 182.1 |
| 460896 | 1/3 | 220.4 | 201.7 | 202.2 | 202.2 | 201.6 | 200.6 | 198.6 | 199.8 |
| 460896 | 1/2 | 222.1 | 205.3 | 205.8 | 205.8 | 204.8 | 203.4 | 201.0 | 202.2 |
| 6688128 | 0 | 295.7 | 268.0 | 267.9 | 268.0 | 247.3 | 248.8 | 246.2 | 249.6 |
| 6688128 | 1/3 | 299.4 | 279.2 | 279.5 | 279.5 | 278.9 | 277.6 | 274.9 | 276.4 |
| 6688128 | 1/2 | 301.2 | 283.0 | 283.3 | 283.3 | 282.3 | 280.4 | 278.2 | 279.4 |
| 6960119 | 0 | 296.8 | 268.4 | 268.3 | 268.4 | 246.6 | 248.4 | 245.7 | 249.2 |
| 6960119 | 1/3 | 300.4 | 280.1 | 280.5 | 280.5 | 279.4 | 278.6 | 275.8 | 277.3 |
| 6960119 | 1/2 | 302.2 | 283.9 | 284.3 | 284.3 | 283.3 | 281.4 | 279.2 | 280.3 |
| 8192128 | 0 | 334.1 | 303.2 | 307.4 | 303.4 | 277.7 | 279.1 | 275.6 | 281.1 |
| 8192128 | 1/3 | 337.7 | 316.8 | 317.1 | 317.1 | 316.3 | 315.5 | 311.9 | 313.3 |
| 8192128 | 1/2 | 339.5 | 320.7 | 321.0 | 321.0 | 320.0 | 318.6 | 315.6 | 317.0 |

Shape: **5 parameter sets × 3 "mem" values × 8 algorithm columns = 120 cost
values**, plus the 15 `param` and 15 `mem` label cells = 150 cells.

The five `param` values are the same five sets whose (m, n, t) and rates
`EV-MCE-332f99` O-1 records — 348864, 460896, 6688128, 6960119, 8192128 — in
the same order. That correspondence is by the printed labels alone; no
parameter, rate or size from O-1 is used anywhere in this document.

### 3.1 Raw extractor output for the table block (path A, unedited)

Reproduced so a reviewer can diff the rendered table above against the bytes it
came from. This is the pypdf text stream verbatim, artifacts included:

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

---

## 4. The caption, verbatim

Raw, path A (pypdf), with kerning artifacts left visible:

> *"T able 1: Output of the Esser–Bellini estimator for the selected Classic
> McEliece parameter sets. The “mem” column is 0 for estimates assuming free
> memory access, 1 /3 for estimates using a cube- root assumption, and 1 /2 for
> estimates using a square-root assumption. Some cost components are ignored in
> all estimates."*

Path B (pdfminer.six) renders the same caption with different artifacts:

> *"Table 1: Output of the Esser–Bellini estimator for the selected Classic
> McEliece parameter sets. The “mem” column is 0 for estimates assuming free
> memory access, 1/3 for estimates using a cube- root assumption, and 1/2 for
> estimates using a square-root assumption. Some cost components are ignored in
> all estimates."*

**Transcriber's reading of the differences** (outside the quotations, per §2):
`T able` is a kerning split of `Table`; `1 /2` and `1 /3` are kerning splits of
`1/2` and `1/3`; `cube- root` is the printed line-break hyphenation of
`cube-root`. The two paths agree on every word and every character otherwise.
No `[EXTRACTION-DAMAGED]` marker is set on the caption: nothing in it is
unreliable, only cosmetically split.

The caption's last sentence — *"Some cost components are ignored in all
estimates."* — is transcribed in full in `convention_as_stated.md` together
with everything else SEC says about what its numbers do and do not charge for.

---

## 5. What the numbers are, in the source's own words

SEC does **not** print a unit inside the table or its caption. The caption says
only *"Output of the Esser–Bellini estimator"*. The document's surrounding
prose uses table values as **exponents of 2**, in these sentences (PDF page 10,
path A raw; superscripts flattened by both extractors — see the markers):

> *"Consequently, the 140.8 actually counts more than 2 143 bit operations."*
> — `[EXTRACTION-DAMAGED: flattened superscript]` the printed text sets `143`
> at 7.97 pt raised 5.1 pt above the 11.96 pt `2`; the printed form is 2^143.
> Path B renders the same string as `2143`. **Both extractors lose the
> superscript**; neither rendering is the printed text.

> *"This is consistent with the 2 246.6 number in Table 1."*
> — `[EXTRACTION-DAMAGED: flattened superscript]`, same measurement (`246.6`
> at 7.97 pt, raised 5.1 pt). Printed form 2^246.6. Path B: `2246.6`.

and (PDF page 11):

> *"This is consistent with the 2 279.2 number in Table 1."*
> — `[EXTRACTION-DAMAGED: flattened superscript]`, same measurement (`279.2`
> at 7.97 pt, raised 5.1 pt). Printed form 2^279.2. Path B: `2279.2`.

Where those three values sit in the transcribed table, by exact string match on
the printed labels:

- `140.8` occurs **once**, at `348864 / 0 / MO`.
- `246.6` occurs **once**, at `6960119 / 0 / BJMM`.
- `279.2` occurs **twice**, at `6688128 / 1/3 / Stern` **and** at
  `6960119 / 1/2 / MO`. **Which of the two SEC's sentence refers to is not
  adjudicated here.** The sentence sits in a passage about the 6960119
  parameter set, but resolving the reference on that basis is an inference and
  this task does not make it. (16 of the table's 102 distinct cost values occur
  in more than one cell, so this ambiguity is a property of the table, not of
  the transcription.)

**That the source uses these values as exponents of 2 is transcribed; nothing
is inferred from it about the remaining cost cells, and no unit is assigned to
the table by this document.**

SEC also gives a **memory** figure for one specific attack, PDF page 10:

> *"More importantly, the 140 .8 is for an attack using memory 2 86.6,
> according to the same estimator."*
> — `[EXTRACTION-DAMAGED: flattened superscript]` (`86.6` at 7.97 pt, raised
> 5.1 pt; printed form 2^86.6). `140 .8` is a kerning split of `140.8`. Path B
> renders `140.8` and `286.6`.

That memory figure is **not in Table 1**; SEC states it in prose and attributes
it to *"the same estimator"*. It is transcribed here because it is the only
memory quantity SEC attaches to any table entry, and a later reader looking for
"the memory the table's numbers assume" will find exactly this one sentence.

---

## 6. Observations recorded and NOT resolved

Per this task's named duty 3: where something looks discrepant, it is recorded
as an observation and left unresolved.

### O-1. SEC never expands its own column abbreviations

The header reads `param mem Prange Stern Dumer BC BJMM pdw MO BM`. A grep of
the full 36-page extraction finds `BJMM`, `pdw`, `MO` and `BM` **nowhere else
in the document**, and `BC` nowhere else as a standalone token. Section 3.3
names algorithms in prose — *"1988 Lee–Brickell [50]"*, *"1989 Stern [61]"*,
*"2011 May–Meurer–Thomae [52]"*, *"2012 Becker–Joux–May–Meurer [3]"* — but
**never ties those names to the table's column labels**.

**Not resolved.** No expansion is supplied for `BC`, `BJMM`, `pdw`, `MO` or
`BM`. Supplying one from memory would be a fabrication under AGENTS.md rule 9
and would have to carry `[RECALLED-NOT-READ]`; inferring one from Section 3.3
would be a derivation this task is forbidden to make. A later task that needs
the mapping must obtain it from a source and record where.

### O-2. One within-table ordering differs from the pattern of the other rows

In the `8192128 / mem 0` row, `Dumer` reads **307.4** while `Stern` reads
**303.2** and `BC` reads **303.4**. In the other four `mem 0` rows the `Stern`
and `Dumer` entries are within 0.1–0.2 of each other (151.4/151.4,
193.3/193.2, 268.0/267.9, 268.4/268.3).

This is stated because the relevant question for a **transcription** is whether
it is an extraction artifact. It is not: the cell reads 307.4 identically in
all three extraction paths, including the geometry-only reconstruction, and its
column assignment is confirmed by the header-centre check in §2.

**Not resolved.** No cause is proposed, no correction is implied, and nothing
is concluded from it. It is recorded so that a reviewer re-acquiring the source
sees the same thing and does not read it as a transcription error.

### O-3. A second, different set of designer-published cost figures exists and is not reconciled here

`TASK-20260803-f3aece`'s access log (its `unexpected_observations` O2) records
that `classic.mceliece.org/comparison.html` carries **CryptAttackTester
bit-operation estimates** for overlapping problem sizes. This task did not
fetch that page and transcribes none of those figures.

**Not resolved.** Whether those figures and SEC Table 1 are consistent,
comparable, or produced under the same convention is **unknown to this task**.
Named again in `baseline_gap_statement.md` as an open item.

### O-4. SEC's own statement that its table will be superseded

SEC states, of its own table (PDF page 10):

> *"The exact numbers in Table 1 should be expected to be superseded by larger
> numbers from future estimators that count bit operations."*

Transcribed here as an observation about the source's status claim for its own
numbers. Its full context and the reason SEC gives are in
`convention_as_stated.md` §3.

### O-5. SEC ties a `param` label to a concrete pair exactly once, in a different context

The table's `param` column carries only the five compound labels. The only
place in SEC where such a label is connected to a concrete pair of numbers is
PDF page 13, inside a discussion of a shortening reduction's tightness:

> *"For example, in the setting of Table 1 with 1 /2 for “mem”, the tightness
> loss is just 0 .8 bits for 460896. To check this calculation, run the
> estimator for (4608 , 96) and (8192, 96), and compare the security-level
> diﬀerence to…"*

**Not resolved.** This is transcribed as it stands. This document does **not**
infer from it a general rule for reading the other four labels, and does not
connect any label to the (m, n, t) triples of `EV-MCE-332f99` O-1. A later task
needing the estimator's per-row inputs must obtain them from a source and
record where.

---

## 7. What was NOT obtained

| Item | Status |
|---|---|
| Expansion of the column abbreviations `BC`, `BJMM`, `pdw`, `MO`, `BM` | **not obtained** — absent from SEC; see O-1. Not supplied from any other source. |
| A unit or formal definition printed with the table | **not obtained** — the caption says only *"Output of the Esser–Bellini estimator"*; §5 records the source's exponent usage for three specific cells and stops there. |
| The estimator's own cost model, as defined by Esser–Bellini | **not obtained** — the paper `[33]` (eprint 2021/1243) was **not read**; only its abstract page was fetched, and only for bibliographic identity. |
| Memory figures for any table entry other than `348864 / 0 / MO` | **not obtained** — SEC gives 2^86.6 for that one attack only. |
| Time–memory tradeoff curves, or any tradeoff data | **not obtained** — SEC gives three fixed `mem` values, not a curve. |
| Quantum estimates for these parameter sets | **not obtained** — Table 1 has no quantum column; SEC discusses quantum attacks in prose only. |
| Any figure from `comparison.html` (CryptAttackTester) | **not obtained** — not fetched by this task; see O-3. |

---

## 8. Marker inventory

- `[RECALLED-NOT-READ]` markers set: **0**. No number in this document came
  from recall. Every figure traces to the retrieval whose sha256 is in §1.
- `[EXTRACTION-DAMAGED]` markers set in this file: **4** — all in quoted prose
  (the flattened superscripts 2^143, 2^246.6, 2^279.2, 2^86.6), each supported
  by a character-size and baseline measurement rather than an impression.
  **Zero table cells are marked**, for the measured reason in §2.
- Values computed rather than transcribed: **none**. This document contains no
  arithmetic.
- Conventions adopted: **none**.
