# Transcription convention — settled for GOAL-MCE-001

**Task:** TASK-20260808-a9f648 · **Goal:** GOAL-MCE-001 · **Batch:** BATCH-a68f79
**Role:** coordinator · **Date:** 2026-08-08
**Authority:** `DEC-20260803-a5b9b1` **D-10**, which records the defect this
document closes and requires that *"the convention must be fixed before the next
transcription batch, not after."*

> **BINDING ON `TASK-20260808-1985f1`** (*Transcribe Esser–Bellini SEC Table 1
> under the settled convention*), which declares `TASK-20260808-a9f648` as its
> only dependency and whose completion gate reads: *"Every transcribed value
> carries its provenance per the settled convention from TASK-20260808-a9f648."*
> It is binding on every later transcription task of `GOAL-MCE-001` until a
> superseding convention document is archived under a new task id.

**Inference record (verbatim, as required by the task card):** requested_policy
coordinator-orchestration-code; per CLAUDE.md per-role model selection is
process-level under Claude Code and subagents keep model: inherit, so the
resolved model is the session model; fallback_used: false; model_verified: false
(no adapter probe receipt for this session).

**Budget:** authorized 1 run, 2 GB, 2700 s. **Runs executed: 0.** This role has
no execute capability (`orchestration/roles.yaml`, `may_execute_experiments:
false`). Nothing in this document was executed, and §10 lists every rule below
whose *verification* requires execution by whoever drives the harness.

**Claim tier: toy, unchanged. `GOAL-MCE-001.active_hypothesis_ids`: empty,
unchanged.** This document settles the *form* of a transcription. It establishes
nothing whatever about Classic McEliece, in either direction, and no rule below
may be cited as evidence about any cryptosystem.

**Not attempted, deliberately:** `iacr:2026/1232`'s PDF, by any route. The 403 is
path-scoped and reproducible, circumvention is forbidden, and AGENTS.md rule 5
makes a blocked route a recorded outcome. No route to it was tried in this task.

---

## 0. What D-10 actually found, and what "settled" has to mean

D-10 is not an aesthetic complaint. Two producers in one batch applied different
disclosure standards to the same class of extraction artifact:

- `TASK-20260803-292b99` left raw `(cid:NN)` tokens and the ligature artifact `“`
  visible inside its verbatim blocks, annotated them outside the block, and
  marked the affected values `[EXTRACTION-DAMAGED]`.
- `TASK-20260803-f3aece` silently restored `C0 ∈ Fmt 2` to `C0 ∈ F2^mt` and
  `(cid:100)…(cid:101)` to `⌈…⌉` **inside a block presented as verbatim**, and
  then declared *"`[EXTRACTION-DAMAGED]` markers set: **0**"*.

The validator (`TASK-20260803-409c5e`, qualification **Q2**) confirmed the
restoration was *"unambiguous and correct"* and that **no number was affected**,
and still recorded it as a defect, because the reader cannot tell an undisclosed
correct edit from an undisclosed incorrect one without re-fetching the source.
That is the whole problem. The fix is not "be careful"; it is to remove the
discretion.

**The standard this document holds itself to.** Two competent transcribers,
given the same source and this file, must produce **byte-identical form**:
identical field names, identical field order, identical markers, identical
delimiters, identical cell identifiers, identical table structure, identical
value strings. Their explanatory *prose* will differ, and this convention does
not claim otherwise — but no prose may appear inside a value, a marker, or a
verbatim block, so prose variation cannot reach the transcribed data.

**Where this convention took its side.** Where the two BATCH-001 producers
diverged, this convention adopts `TASK-20260803-292b99`'s standard, which is what
the validator recommended (*"Recommend the batch adopt 292b99's standard."*).

---

## 1. RULE 1 — UNITS

### 1.1 The rule

1. Every transcribed numeric value carries a `unit` and a `unit_locus`.
2. The `unit` is **copied from the source**, verbatim, from wherever the source
   states it: the table caption, the column header, the row label, a unit row, or
   the sentence introducing the table. `unit_locus` names which of those, exactly.
3. **If the source states no unit anywhere, the unit is
   `[NOT-STATED-BY-SOURCE]`.** It is never inferred from magnitude, from
   convention, from a sibling table, from another document, or from the
   transcriber's knowledge of the field.
4. A unit stated for a whole table is recorded **once, on the table**, and every
   cell inherits it. A unit stated per column is recorded on the column and
   overrides the table. A unit stated per cell overrides both. Nothing else
   overrides anything.
5. **Never convert.** Bytes stay bytes; `2^143` is not converted to a decimal;
   a base-2 logarithm is not converted to a count and a count is not converted to
   a logarithm. If a conversion is wanted it is a derived value (Rule 4).
6. A column whose header *is* the unit statement (e.g. a header reading `bytes`)
   still gets an explicit `unit` field; the header is not left to speak for itself.

### 1.2 Required form

**Markdown.** The unit appears in the column header in exactly this form:

```
| <header as printed> [unit: <unit as printed>] |
```

and where the source states none:

```
| <header as printed> [unit: NOT-STATED-BY-SOURCE] |
```

A table-wide unit is declared on the line immediately below the table's
provenance block, in exactly this form:

```
Table unit (all cells unless overridden): <unit as printed> — stated at: <locus>
```

**JSON.** `"unit": "<string>"` or `"unit": null` with
`"unit_status": "NOT-STATED-BY-SOURCE"`, plus `"unit_locus": "<string>"`.

### 1.3 Worked example — CORRECT

From `TASK-20260803-f3aece/parameter_sets.md` §4, the substance is exactly right:
it quotes the caption verbatim — *"Sizes of inputs and outputs to the complete
cryptographic functions. All sizes are expressed in bytes."* — and then states
*"All values in **bytes**, per the table's own caption."* The unit comes from the
source and the source is named. Under this convention it must additionally be
carried in the header or in the table-unit line, so a reader who copies one row
out of the table cannot lose it.

### 1.4 Worked example — INCORRECT

The same table, rendered as its headers actually stand:

```
| Parameter set | Public key | Private key | Ciphertext | Session key |
|---|---:|---:|---:|---:|
| mceliece348864 | 261120 | 6492 | 96 | 32 |
```

The numbers are correct (the validator re-checked **40/40 cells exact**), but the
row is unit-free the moment it is quoted away from the prose two paragraphs
below. Under this convention the header must read
`| Public key [unit: bytes] | …`, or the table-unit line must precede the table.

**Existing artifact that does not conform to this rule (named, NOT edited):**
`coordination/goals/GOAL-MCE-001/batches/BATCH-001/tasks/TASK-20260803-f3aece/parameter_sets.md`
§4. This is a **form** non-conformance only. Its values were independently
verified 40/40 and its unit statement is present in prose and sourced. It is
named because Rule 7 forbids silence, not because the numbers are in doubt.

---

## 2. RULE 2 — ROUNDING AND SIGNIFICANT FIGURES

### 2.1 The rule

1. **A transcribed value is copied glyph-for-glyph as printed.** It is never
   re-rounded, never re-formatted, never re-notated.
2. Specifically forbidden on a transcribed value: stripping or adding trailing
   zeros (`143.00` ≠ `143`); changing the decimal mark or thousands separator;
   converting `2^143` to any other form; converting `≈` to `~` or dropping it;
   converting a printed `1.2 × 10^5` to `120000`; normalising `0,5` to `0.5`.
3. **A value the source itself gives rounded is transcribed as the source gives
   it, together with the source's own rounding language, verbatim.** If the
   source prints `≈ 2^143.4`, the transcribed value is the string `≈ 2^143.4`,
   not `2^143.4` and not `143.4`. If the source says "rounded to two decimals"
   or "to the nearest bit", that sentence is quoted under Rule 6 and the field
   `source_rounding_statement` carries it.
4. **The transcriber never increases precision.** A source's rounded value is not
   refined by recomputation, by another source, or by a formula.
5. **Two loci, two records.** If the same quantity is printed with different
   precision in two places, both are recorded with both loci and
   `intra_source_discrepancy: true`. The transcriber does not choose.
6. **Derived values (Rule 4) may be rounded, under one declared rule, stated once
   per document,** in exactly one of these two forms and no other:
   - `rounding_rule: round-half-even to <N> decimal places`
   - `rounding_rule: truncate toward zero at <N> decimal places`
   The words "truncated/rounded", "approximately", "to about N places", or any
   disjunction are **not** a rule and are non-conforming.
7. Exact rationals, where available, are recorded exactly and are authoritative
   over any decimal rendering of them.
8. **In JSON, every transcribed numeric value is a JSON string.** This is not
   stylistic: a JSON number round-trips through a float and can silently
   re-round or re-notate the very thing this rule protects. Numeric typing is
   permitted only inside the `derived` block.

### 2.2 Worked example — CORRECT

`TASK-20260803-292b99/rate_regime_extraction.md` §2.3 transcribes
`R < 0.277` and `R < 0.141` exactly as printed, explicitly records that they are
*"clean — they appear as plain inline digits, not as flattened superscripts"*,
and does not recompute them from the entropy-function conditions printed beside
them (which were marked damaged). Same file, §1.4: `74.9` bits is kept with its
source's attribution *"according to [LS12]"* rather than being re-derived.

### 2.3 Worked example — INCORRECT

`TASK-20260803-f3aece/parameter_sets.md` §2 states:

> Decimals are truncated/rounded to 6 places; the exact rational is authoritative.

`85/109` is `0.7798165137…`. Truncation at 6 places gives `0.779816`; rounding
gives `0.779817`. The document prints `0.779817`. The *value* is therefore fine
and the exact rationals beside it are authoritative and were independently
recomputed 5/5 by the validator — but the *stated rule* does not determine the
digit, so a second transcriber applying the stated rule would print a different
one. Under this convention the line must read
`rounding_rule: round-half-even to 6 decimal places`.

**Existing artifact that does not conform to this rule (named, NOT edited):**
`coordination/goals/GOAL-MCE-001/batches/BATCH-001/tasks/TASK-20260803-f3aece/parameter_sets.md`
§2, the phrase "truncated/rounded to 6 places". Form only; all five decimals and
all five exact rationals were independently confirmed by
`TASK-20260803-409c5e`.

---

## 3. RULE 3 — PROVENANCE PER VALUE

### 3.1 The rule

Every transcribed value is reachable, by a mechanical read, to the exact bytes it
came from. Concretely:

1. **Source keys.** Each document gets a short uppercase key defined once, in a
   source table at the top of the deliverable, carrying: key, title **as printed
   on the document**, retrieval URL, HTTP status, byte count, **full 64-hex
   sha256**, page count, extractor and version, and the `source_access_log.yaml`
   attempt id.
2. **Hash abbreviation is fixed.** The full 64-hex form appears in the source
   table. Elsewhere the *only* permitted abbreviation is **the first 8 hex digits
   followed by U+2026 `…`** — e.g. `db17ef08…`. Mixed abbreviation lengths are
   non-conforming.
3. **No hash, no silence.** Where bytes were not retained, the field is
   `sha256: not_obtained` plus a `sha256_reason:` naming why. A hash is never
   back-filled by a later fetch, because a later fetch hashes a different
   retrieval than the one being logged.
4. **Locus, with these fields and no others:**
   `source_key`, `page_printed` (the number printed on the page),
   `page_pdf` (1-based index in the PDF), `section` (as printed),
   `table_label` (as printed, e.g. `Table 1`), `row_label` (**verbatim**),
   `column_header` (**verbatim**), `caption` (verbatim, under Rule 6).
   Any field the source does not supply is `null` with a `_reason` sibling.
   **A page number that is not printed and not counted is `null`. It is never
   invented.**
5. **Cell identifiers.** Every cell in a transcribed table gets an id of exactly
   the form `<SOURCE_KEY>.<TABLE_LABEL_SLUG>.<ROW_SLUG>.<COL_SLUG>`, where the
   slug rule is, mechanically: lowercase; replace every character outside
   `[a-z0-9]` with `_`; collapse runs of `_` to one; strip leading and trailing
   `_`. Example, from a table this program has fully transcribed and verified:
   IMPL Table 1's public-key cell for `mceliece6960119` is
   `IMPL.table_1.mceliece6960119.public_key`.
6. **Each value has exactly one locus-bearing home.** A value may be repeated in
   a summary or index table only with a `see: §<n>` pointer to that home. A
   repetition without a pointer is non-conforming, because it is the form in
   which a value drifts loose from its provenance.
7. Retrieval-side facts (URL, status, bytes, sha256, timestamps, route order,
   deviations, blocked routes) live in `source_access_log.yaml` in the same task
   directory, in the schema already used by both BATCH-001 producers. Blocked
   routes are recorded as outcomes, never as evidence (AGENTS.md rule 5).

### 3.2 Worked example — CORRECT

`TASK-20260803-f3aece/source_access_log.yaml` seq 7 records SEC with URL, HTTP
200, 332574 bytes, `sha256 db17ef0879cb8822120c312b7290f7db82fe9fc356bd16058ad334a512b523fa`,
36 pages, and `used_for: Security category claims (Section 3.5 area) and Table
1` — and `parameter_sets.md` §0 then binds the key `SEC` to it. Every value in
that document is reachable from a key to a hash to a URL. Seq 11 of the same log
is the correct handling of a missing hash: `sha256: not_obtained` with the reason
*"This request was a reachability probe written with `-o /dev/null`; the body was
never retained… Recorded as not obtained rather than back-filled by a second
fetch."*

`TASK-20260808-843c87/correction_report.md` §2 is the correct handling of a
missing page number: *"**No page number is cited, because none exists in the
record.** … Inventing one would be exactly the fabrication the card forbids."*

### 3.3 Worked example — INCORRECT

A row of the shape

| Source | Rate condition |
|---|---|
| `arXiv:2304.14757` | high rate condition (6), m arbitrary |

carries a source key and no locus, no hash, and no pointer. As a *summary* it is
legitimate; as the only home of the value it is not. Under this convention it
must carry `see: §3.4`, which is where the locus and the damage marker live.

**Existing artifacts that do not conform to this rule (named, NOT edited):**

- `…/BATCH-001/tasks/TASK-20260803-292b99/rate_regime_extraction.md` §5, the
  summary table, whose rows repeat values from §§1–4 without the `see:` pointer
  this convention now requires. Form only; the locus-bearing sections are
  present and correct upstream.
- Hash-abbreviation drift **inside one batch**: `rate_regime_extraction.md` §3
  writes `ebbd94ac…c564b8` (first 8 + last 6) while
  `parameter_sets.md` §0 writes `dcc68788…` (first 8). Both are honest; only one
  form is permitted from now on, and it is `dcc68788…`.

---

## 4. RULE 4 — A SOURCE'S OWN FIGURE vs A DERIVED ONE

### 4.1 The rule

**A derived value is not a transcription.** It may appear, and often should —
this program's strongest BATCH-001 integrity control was a derivation — but it
never appears where a transcribed value appears, and it is never presented in a
form a reader could mistake for one.

1. **Segregation is structural, not typographic.**
   - In JSON: transcribed values live under `"cells"`. Derived values live under
     `"derived"`. Nothing derived ever appears under `"cells"`, under any key,
     under any circumstance.
   - In Markdown: transcribed values live in tables under `## TRANSCRIBED`.
     Derived values live under a section headed exactly
     `## DERIVED — NOT TRANSCRIBED`.
2. **Marking.** Every derived column header carries the suffix ` [DERIVED]`. A
   derived value appearing anywhere in prose carries a trailing `[DERIVED]`.
3. **Every derived value states, in this order:** the `formula`; the
   `formula_source` — either a verbatim quotation of the source's own formula
   with its locus (Rule 6), or the literal token `transcriber`; the input cell
   ids it consumed; the computation shown; and the document's `rounding_rule`.
4. **A derived value may never consume a cell marked `[EXTRACTION-DAMAGED]`,
   `[NOT-STATED-BY-SOURCE]`, or `[NOT-OBTAINED]`.** If it needs one, the derived
   value is `[NOT-OBTAINED]` too, with the blocking cell id named.
5. **A derived value is never promoted.** It does not become a transcription
   because it was checked, because it matched, or because it is obviously right.
6. A derived value that *disagrees* with a transcribed value is an unexpected
   observation and is recorded under AGENTS.md rule 8, in the report, with both
   values and both provenances. The transcriber does not choose between them and
   does not adjust either.

### 4.2 Worked example — CORRECT

`TASK-20260803-f3aece/parameter_sets.md` §6 labels each `pc` ciphertext size
*"**computed** from PC + SPEC §6.1"* in a provenance column, and then states
outright: *"These five ciphertext sizes are **computed from the sources'
formulas, not transcribed from any table**, and are marked as such. … A reviewer
wanting a transcribed pc size table should treat it as **not obtained**."* That
is exactly the posture this rule requires. Its §5 cross-check is likewise framed
as a *check* on two independent transcriptions, not as a source of values, and
its §8 marker summary enumerates every computed quantity in the document.

### 4.3 Worked example — INCORRECT

The same document's §2 table places one transcribed column and four derived ones
side by side with no per-column marker:

| Parameter set | n | m·t | k = n − mt | k/n exact | k/n decimal |
|---|---:|---:|---:|---:|---:|

`n` is SPEC §7's own figure; `m·t`, `k`, and both rate columns are computed. The
disclosure exists — honestly and in full — but it is in §8, at the end of the
document, and a reader who copies this table copies four derived numbers wearing
the same clothes as a transcribed one. Under this convention the derived columns
must read `m·t [DERIVED]`, `k = n − mt [DERIVED]`, `k/n exact [DERIVED]`,
`k/n decimal [DERIVED]`, and the table must sit under
`## DERIVED — NOT TRANSCRIBED` with `n` carrying a `see:` pointer to its
transcribed home.

**Existing artifact that does not conform to this rule (named, NOT edited):**
`coordination/goals/GOAL-MCE-001/batches/BATCH-001/tasks/TASK-20260803-f3aece/parameter_sets.md`
§2. Form only. Every value in it was independently recomputed 5/5 by
`TASK-20260803-409c5e` and the document discloses the derivation in §8.

---

## 5. RULE 5 — AMBIGUOUS OR UNREADABLE VALUES

### 5.1 The closed marker set

Exactly six markers exist. **No transcriber may introduce a seventh** — that is
Rule 7's case.

| Marker | Means | Never means |
|---|---|---|
| `[EXTRACTION-DAMAGED]` | the glyphs exist in the source but the extraction cannot be trusted to reproduce them | that the source lacks the value |
| `[NOT-STATED-BY-SOURCE]` | the locus was read and the source states no such value | that it was hard to read |
| `[NOT-OBTAINED]` | the locus was not read in this session (blocked, unfetched, out of scope) | that the value does not exist |
| `[DERIVED]` | computed, not transcribed (Rule 4) | — |
| `[RECALLED-NOT-READ]` | a value that came from memory rather than a source | — |
| `[CONVENTION-GAP:<n>]` | this convention does not determine the form (Rule 7) | — |

**These three are never interchanged: `[EXTRACTION-DAMAGED]`,
`[NOT-STATED-BY-SOURCE]`, `[NOT-OBTAINED]`.** They answer three different
questions and collapsing them destroys the only information a reviewer needs to
decide what to re-fetch.

**`[RECALLED-NOT-READ]` may not appear in a delivered artifact.** Its only use is
to make an accidental recall visible while drafting. Any cell still carrying it
at delivery makes the deliverable **invalid**, and the transcriber reports that
rather than deleting the marker. `TASK-20260803-f3aece` set this marker count to
**0** and stated why; that is the target.

### 5.2 The rule

1. A value is `[EXTRACTION-DAMAGED]` whenever **any** of these holds: the
   extractor emits unmapped glyph tokens (`(cid:NN)`) in or adjacent to it;
   superscript, subscript, or exponent grouping is flattened; column-to-row
   association in a multi-column table is inferred from extraction order rather
   than read from the rendered layout; two extractors disagree; or the
   transcriber cannot state the value's glyphs with certainty for any other
   reason.
2. **A damaged value is NEVER reconstructed, interpolated, inferred, averaged,
   completed from a neighbouring cell, completed from another document, or
   completed from the transcriber's knowledge.** There is no exception for an
   obvious reading.
3. The **raw extractor output is preserved verbatim**, in a fenced block, beside
   the marker. It is the only thing that carries information here.
4. A reading that seems obvious is recorded **only** inside the damage note,
   prefixed exactly `NOT TRANSCRIBED — conjectured reading:`. It may never be
   copied into a value field, a table cell, a summary, a JSON `cells` entry,
   another document, or a decision. Consistency checks on it may be **reported as
   checks**; a check never repairs damage.
5. **Two extractors are required for every table**, and their disagreement is by
   itself sufficient to mark damage. Agreement is recorded; it does not remove a
   marker set for another reason.
6. Every deliverable ends with a **marker summary** giving the count of each of
   the six markers. A count of 0 is stated, not omitted.

### 5.3 Required form

Markdown, in a table cell:

```
| <row label> | [EXTRACTION-DAMAGED] |
```

with, below the table (the outer fence here is four backticks only so this
template can show the inner three-backtick fence it requires):

````
### [EXTRACTION-DAMAGED] — <cell id>

Raw extractor output, unedited (<extractor> <version>):

```
<exact bytes, unedited>
```

Damage: <what specifically is not recoverable>
NOT TRANSCRIBED — conjectured reading: <reading, or "none">
````

JSON:

```json
{
  "id": "<cell id>",
  "value_printed": null,
  "status": "EXTRACTION-DAMAGED",
  "raw_extractor_output": "<exact bytes>",
  "damage_note": "<what is not recoverable>",
  "conjectured_reading": "NOT TRANSCRIBED — conjectured reading: <...>"
}
```

### 5.4 Worked example — CORRECT

Two, both from `TASK-20260803-292b99`, and both are the reason this program
caught its own errors instead of publishing them.

`rate_regime_extraction.md` §3.4 reproduces the raw pdfminer output at the
location of condition (6) unedited, marks it `[EXTRACTION-DAMAGED]`, states
precisely what interleaved, and concludes: *"**This inequality is NOT
reconstructed and carries no claim in any deliverable of this task.** A reviewer
wanting condition (6) must read the rendered PDF at sha256 `ebbd94ac…`."*

`attack_transcription.md` §2.4 does the harder version. The κ row extracts as
`2528`, `(21080)`, `(21224)`, `21030`, `2997`; the producer records that these
are *"almost certainly powers of two whose superscript markup was flattened"*,
immediately adds *"**That reading is a reconstruction and is NOT transcribed as a
fact.** No deliverable of this task carries a κ value"*, and names the precedent:
*"This is precisely the class of error that cost GOAL-HQC-001 BATCH-001 50.7
bits at NIST-5, and it is being refused rather than committed."* §2.2 does the
same for equation (92), running an internal consistency check and then stating
*"The internal consistency check is reported as a check, not as a repair."*

### 5.5 Worked example — INCORRECT

The canonical one, and the reason D-10 exists.
`TASK-20260803-f3aece/parameter_sets.md` §6 presents, inside a verbatim block:

> *"A ciphertext C has two components: C0 ∈ F2^mt and C1 ∈ F2^ℓ. …"*

The re-fetched PDF extracts as `"A ciphertext C has two components: C0 ∈ Fmt 2.
…"`, with the superscripts and the `and C1 ∈ F₂^ℓ` clause dislocated by the
layout (validator `TASK-20260803-409c5e` **Q2**, which re-fetched and confirmed
this). The restoration is unambiguous and correct and **no number is affected** —
and it is still the incorrect rendering, because it is an undisclosed editorial
step inside a block labelled verbatim, sitting beside a declaration of *zero*
damage markers. Under this convention the correct rendering keeps the extracted
bytes in the block, sets `[EXTRACTION-DAMAGED]` on the affected symbols, and puts
the restored reading in the damage note prefixed `NOT TRANSCRIBED — conjectured
reading:`.

**Existing artifact that does not conform to this rule (named, NOT edited):**
`coordination/goals/GOAL-MCE-001/batches/BATCH-001/tasks/TASK-20260803-f3aece/parameter_sets.md`
§6 (the PC ciphertext-representation quotation) and §8 (the `markers set: 0`
declaration that accompanies it). This is the defect D-10 records. It is named
here, as D-10 requires; it is **not** edited, because BATCH-001's artifacts are
immutable and snapshot-archived (`DEC-20260803-a5b9b1` D-1, all 9 recorded hashes
recomputing from the committed blobs). A correction, if one is wanted, is a
superseding record under a new id — not a change to that file.

---

## 6. RULE 6 — VERBATIM QUOTATION

### 6.1 When to quote rather than tabulate

Quote — do not tabulate — in exactly these cases:

1. The table's **caption**, and any **column header** whose wording carries a
   condition, a unit, or a hedge.
2. Any sentence stating a **unit**, a **cost model**, a **rounding**, an
   **assumption**, an **attribution** ("according to [X]"), or a **hedge** ("we
   conjecture", "under Heuristic 1", "apparently", "aimed at having").
3. Any **definition** of a symbol appearing in a transcribed table.
4. Any **scope statement** about what the numbers do and do not cover.
5. Any passage whose **absence** is being reported — the passage that does *not*
   state the thing is quoted, so the absence is checkable rather than asserted.

Rule of thumb, mechanical: **if removing the words would change what a number
means, the words are quoted, not summarised.**

### 6.2 Delimitation, and what may happen inside a block

- **Prose** → Markdown blockquote, `> ` prefix on every line.
- **Anything whose whitespace or layout is load-bearing, and anything containing
  extractor artifacts** → fenced code block with **no language tag**.
- Every verbatim block is **immediately preceded** by a locus line of exactly the
  form `Locus: <source_key>, <section/table>, <page_printed>/<page_pdf>` (with
  `null` where a component does not exist), and, where any artifact is present,
  **immediately followed** by a line beginning `Extraction note: `.

**Inside a verbatim block, the permitted edits are: none.** Not glyph
substitution, not ligature repair, not `(cid:NN)` removal, not spelling
correction, not punctuation, not joining a heading to body text, not adding
emphasis, not normalising quotation marks, not normalising whitespace, not
silently eliding. The one permitted mark is an omission, written exactly `[…]`.
Anything the transcriber wants to say goes **outside** the block, on the
`Extraction note:` line.

### 6.3 Worked example — CORRECT

`TASK-20260803-292b99/attack_transcription.md` §1.3 reproduces the authors'
revision note with its unbalanced quotation marks, its French guillemets and its
non-breaking spaces intact, and notes outside the block: *"(The unbalanced
quotation marks, the French guillemets, and the non-breaking spaces are the
source's, not a transcription artefact. The raw characters were checked against
the un-rendered HTML.)"*

Same producer, §3: the pdfminer ligature artifact is left in place and annotated
outside the block — *"(`“` is the extraction's rendering of `=`; this is a known
pdfminer ligature artefact in this document and is left as extracted.)"* — and
the source's own misspelling is preserved with *"(\"unreacheable\" is the
source's spelling.)"*.

### 6.4 Worked example — INCORRECT

Two, both recorded by the validator:

- **Q2**, §5.5 above: silent glyph restoration inside a verbatim block.
- **Q3**: `TASK-20260803-f3aece/parameter_sets.md` §1 presents
  *"7.7 Parameter set mceliece6960119 — KEM with m = 13, n = 6960, t = 119."*
  inside a verbatim block. The source has a section heading followed by body
  text; **the em-dash is the transcriber's join**. The validator's own
  characterisation is *"Cosmetic; substance exact"* — and it is still
  non-conforming, because a reader cannot distinguish a cosmetic join from a
  substantive one without re-fetching. Under this convention the two are quoted
  as two blocks, each with its own locus line.

**Existing artifact that does not conform to this rule (named, NOT edited):**
`coordination/goals/GOAL-MCE-001/batches/BATCH-001/tasks/TASK-20260803-f3aece/parameter_sets.md`
§1 and §6.

---

## 7. RULE 7 — WHEN THIS CONVENTION DOES NOT COVER THE CASE

### 7.1 The rule

**Return the obstruction. Do not invent a rule.** An invented rule is worse than
a gap, because a gap is visible and an invention is not.

Mechanically, on encountering a case this document does not determine:

1. **Stop transcribing that value.** Do not transcribe it under a guessed form,
   and do not skip it silently.
2. Put `[CONVENTION-GAP:<n>]` in the cell, numbering gaps from 1 in encounter
   order within the task.
3. Record the gap in `transcription_report.md` under a section headed exactly
   `## Obstructions`, one numbered entry with exactly these fields, in this
   order:
   - `id:` `CONVENTION-GAP:<n>`
   - `cell_or_locus:` the cell id, or the locus if no cell id can be formed
   - `what_is_undetermined:` one sentence naming the *form* question, not the
     value question
   - `candidate_renderings:` two or more, written out in full
   - `what_was_done:` **nothing was transcribed** — this field exists so that any
     other answer is conspicuous
   - `decision_needed_from:` `coordinator`
4. **Continue the rest of the transcription.** A gap blocks one value, not the
   task.
5. The task **completes** with obstructions reported. Reporting a gap is a
   successful outcome, not a failure; transcribing through a gap on a guessed
   form is the failure.

### 7.2 How a gap is closed

Not by editing this file. This document is immutable once archived. A gap is
closed by a **superseding convention document** under a new task id, which cites
this one and states exactly which rule it extends. Corrections supersede, never
overwrite — the same rule as every other record in this program.

### 7.3 Worked example — CORRECT

`TASK-20260803-292b99/attack_transcription.md` §5 (*"Deviations, and things that
surprised the executor"*) is the right shape: numbered, each with what happened
and why it is recorded, filed under AGENTS.md rule 8 rather than dropped —
including DEV-1, routes attempted beyond the declared order, and the observation
that an eprint **HTML** endpoint was blocked, which falsified the coarser
statement both the goal record and the batch opening had been using.

`TASK-20260808-843c87/correction_report.md` §2 shows the discipline this rule
protects, on a live instance of exactly this question: faced with an
undetermined rendering, it wrote *"This report does **not** pre-empt
`TASK-20260808-a9f648`, which settles the transcription convention
`DEC-20260803-a5b9b1` D-10 left open; it simply refuses to silently normalise a
glyph inside something labelled verbatim."* Deferring the form question to the
task that owns it is what Rule 7 asks for.

### 7.4 Worked example — INCORRECT

Encountering a table cell that is blank in the source and writing `0`; or
`[NOT-OBTAINED]`; or a value carried over from the row above; or inventing a
seventh marker such as `[BLANK]` because none of the six seemed to fit. The
conforming response to "the source's cell is empty and I cannot tell whether
that means zero, not-applicable, or not-stated" is `[CONVENTION-GAP:1]` plus an
obstruction entry listing those three candidate renderings.

---

## 8. Required deliverable form for `TASK-20260808-1985f1`

This section is what makes "byte-identical form" checkable. It binds the three
artifacts that task declares.

### 8.1 Binding header

Each of `sec_table1.md`, `sec_table1.json`, `transcription_report.md` carries, at
the top (as a JSON field for the JSON file), exactly:

```
Transcription convention: coordination/goals/GOAL-MCE-001/batches/BATCH-a68f79/tasks/TASK-20260808-a9f648/transcription_convention.md
Binding authority: DEC-20260803-a5b9b1 D-10
```

### 8.2 `sec_table1.md` — section order, fixed

1. `# Esser–Bellini SEC Table 1 — transcription`
2. binding header (§8.1), task/goal/batch/role/date, inference record, budget,
   claim-tier line
3. `## Sources` — the source-key table of Rule 3.1
4. `## Caption and headers, verbatim` — Rule 6
5. `## TRANSCRIBED` — the table(s), Rules 1–3
6. `## [EXTRACTION-DAMAGED] details` — Rule 5.3, one subsection per damaged cell
7. `## DERIVED — NOT TRANSCRIBED` — Rule 4, or the single line
   `None. No derived value appears in this deliverable.`
8. `## Marker summary` — counts for all six markers, zeros stated
9. `## Not obtained` — every locus recorded `[NOT-OBTAINED]`, with the reason

### 8.3 `sec_table1.json` — schema, fixed

```json
{
  "schema": "crypto.autoresearch.transcription.v1",
  "convention": "TASK-20260808-a9f648",
  "binding_authority": "DEC-20260803-a5b9b1 D-10",
  "task_id": "TASK-20260808-1985f1",
  "sources": [
    {
      "key": "SEC",
      "title_as_printed": "",
      "url": "",
      "http_status": null,
      "bytes": null,
      "sha256": "",
      "pages": null,
      "extractors": [{"name": "", "version": ""}],
      "access_log_ref": ""
    }
  ],
  "table": {
    "table_label": "",
    "caption_verbatim": "",
    "locus": {"source_key": "SEC", "page_printed": null, "page_pdf": null,
              "section": null},
    "table_unit": null,
    "table_unit_locus": null,
    "column_headers_verbatim": []
  },
  "cells": [
    {
      "id": "",
      "row_label_verbatim": "",
      "column_header_verbatim": "",
      "value_printed": "",
      "status": "OK",
      "unit": null,
      "unit_status": null,
      "unit_locus": null,
      "source_rounding_statement": null,
      "locus": {"source_key": "SEC", "page_printed": null, "page_pdf": null,
                "section": null, "table_label": ""},
      "extractor_agreement": {"extractors": [], "agree": null}
    }
  ],
  "derived": [],
  "marker_counts": {
    "EXTRACTION-DAMAGED": 0,
    "NOT-STATED-BY-SOURCE": 0,
    "NOT-OBTAINED": 0,
    "DERIVED": 0,
    "RECALLED-NOT-READ": 0,
    "CONVENTION-GAP": 0
  },
  "obstructions": []
}
```

`status` takes exactly one of: `OK`, `EXTRACTION-DAMAGED`,
`NOT-STATED-BY-SOURCE`, `NOT-OBTAINED`, `CONVENTION-GAP`. Every
`"value_printed"` is a **string** (Rule 2.1.8), and is `null` exactly when
`status` is not `OK`. Key order is as written above; arrays are in source order
(rows top-to-bottom, columns left-to-right as printed).

### 8.4 `transcription_report.md` — required sections

`## Second pass` (the completion gate requires a re-read; report every
disagreement between pass 1 and pass 2, or state `No disagreement.`),
`## Unreadable rows`, `## Obstructions` (Rule 7.1), `## Deviations` (AGENTS.md
rule 8), `## What was not obtained`.

### 8.5 Encoding

UTF-8, no BOM, LF line endings, no trailing whitespace on any line, final
newline present. Source glyphs are never replaced with ASCII lookalikes.

### 8.6 One thing this convention deliberately does not decide

**It does not decide what SEC Table 1 contains.** I have not read it. This
document names no row, no column, no value, and no page content of that table.
The only fact about it carried here is second-hand and attributed: validator
`TASK-20260803-409c5e` states, having re-fetched SEC at
`sha256 db17ef08…`, that Table 1's row order is
*"`348864, 460896, 6688128, 6960119, 8192128` (each × three `mem` models)"*, and
`TASK-20260803-f3aece/parameter_sets.md` §3 records its location as
`mceliece-security-20221023.pdf` p.10. Both are recorded as pointers for the
transcriber, **not** as transcribed content, and the transcriber must read the
source rather than rely on either.

---

## 9. Conformance checklist (mechanical)

A deliverable conforms iff every line below is true. The transcriber states each
as `yes` / `no` in `transcription_report.md`.

1. Binding header present in all three artifacts, byte-exact (§8.1).
2. Every source has a full 64-hex sha256, or `not_obtained` + reason (Rule 3.1,
   3.3).
3. Every abbreviated hash is first-8 + `…` (Rule 3.2).
4. Every cell has an id built by the §3.1.5 slug rule.
5. Every cell has `unit`, `unit_status`, `unit_locus` (Rule 1).
6. No transcribed value was re-rounded or re-notated; every JSON
   `value_printed` is a string (Rule 2).
7. Exactly one `rounding_rule` line, in one of the two permitted forms, iff any
   derived value exists (Rule 2.1.6).
8. No derived value appears under `cells` or under `## TRANSCRIBED` (Rule 4.1).
9. Every derived value carries formula, formula_source, input cell ids,
   computation, rounding rule (Rule 4.3).
10. No derived value consumes a non-`OK` cell (Rule 4.4).
11. No damaged value is reconstructed anywhere; every conjectured reading appears
    only in a damage note with the required prefix (Rule 5.2, 5.4).
12. Two extractors were run on every table and their agreement is recorded
    (Rule 5.2.5).
13. Marker summary present, all six counts stated including zeros (Rule 5.2.6).
14. `RECALLED-NOT-READ` count is 0 (Rule 5.1).
15. Every verbatim block has a `Locus:` line before it and, where artifacts are
    present, an `Extraction note:` line after it; no edit inside any block
    (Rule 6.2).
16. Every `[CONVENTION-GAP:<n>]` has a matching `## Obstructions` entry with all
    six fields (Rule 7.1).
17. Second pass performed and its disagreements reported (§8.4).
18. Claim tier stated as toy; no security statement about Classic McEliece in
    either direction.

---

## 10. What could not be verified here, and by whom it must be

Stated plainly, per the task card's note on this role's tool surface. **This role
has read/search/write/edit and no execute capability. Nothing below was run, and
nothing below is claimed to have been run.**

1. **Hashing.** Rules 3.1–3.3 require a sha256 of retrieved bytes. Computing one
   requires execution. The transcriber (`TASK-20260808-1985f1`, role `executor`)
   computes them; I did not, and this document contains no hash I computed.
2. **Dual-extractor agreement.** Rule 5.2.5 requires two extractors per table.
   That requires running them. The transcriber runs them.
3. **The second pass.** §8.4 requires a re-read and a disagreement report. That
   requires re-fetching. The transcriber does it.
4. **Encoding conformance.** §8.5's no-trailing-whitespace / LF / final-newline
   requirements are checkable by a one-line command; I could not run it, and I
   make no claim that this file itself was machine-checked against them.
5. **`tools/validate_ledger.py` and `tools/build_knowledge_index.py` were NOT
   run** by this task. This task writes no ledger record and no knowledge entry,
   so neither is required by it — stated so the omission is not mistaken for a
   skipped obligation.
6. **No git operation was performed.** No staging, no commit. Archival is
   `TASK-20260808-2de410`'s task.
7. **I did not read SEC Table 1**, `arXiv:2304.14757`, or any other primary
   source in this task. Every quotation in this document is quoted from this
   program's own committed artifacts, each named at the point of use, and none is
   presented as a first-hand read of a primary source.

---

## 11. Completion gate, item by item

| Requirement from the task card | Status |
|---|---|
| Units, including the no-unit case | **Met** — Rule 1, with `[NOT-STATED-BY-SOURCE]` as the mandatory no-unit form and inference from magnitude or convention forbidden. |
| Rounding and significant figures | **Met** — Rule 2: glyph-for-glyph transcription, no re-rounding ever, source-rounded values kept with the source's own rounding language, one declared `rounding_rule` for derived values only. |
| Provenance per value, with locus and content hash | **Met** — Rule 3: source keys, full-then-abbreviated sha256, eight named locus fields, mechanical cell ids, one locus-bearing home per value. |
| Source's own figure vs derived | **Met** — Rule 4: structural segregation (`cells` vs `derived`, `## TRANSCRIBED` vs `## DERIVED — NOT TRANSCRIBED`), mandatory `[DERIVED]` marker, derived values may appear but never where a transcription appears and never consume a damaged cell. |
| Ambiguous/unreadable, never reconstructed | **Met** — Rule 5: closed six-marker set, `[EXTRACTION-DAMAGED]` retained as this program's marker, raw extractor output preserved, conjectured readings confined to the damage note with a fixed prefix. |
| Verbatim quotation: when, and how delimited | **Met** — Rule 6: five triggers, blockquote vs fenced block, `Locus:` before and `Extraction note:` after, zero permitted edits inside. |
| Return the obstruction, do not invent a rule | **Met** — Rule 7: `[CONVENTION-GAP:<n>]`, six-field obstruction entry, gaps closed by supersession not by editing this file. |
| Mechanically applicable; byte-identical form from two transcribers | **Met as scoped** — §8 fixes section order, JSON schema, key order, string typing, encoding; §9 is an 18-item mechanical checklist. Scope stated honestly in §0: byte-identical *form*, not byte-identical explanatory prose. |
| Worked correct and incorrect examples per rule, drawn from BATCH-001 | **Met** — every rule carries both, from `TASK-20260803-292b99` and `TASK-20260803-f3aece` and from validator `TASK-20260803-409c5e`'s Q2 and Q3. |
| Binding on `TASK-20260808-1985f1`, cites D-10 | **Met** — header block and §8. |
| Existing violations named, not edited | **Met** — §12. No BATCH-001 file was opened for write by this task. |
| Claim tier toy, `active_hypothesis_ids` empty | **Met** — header block; §8.6 additionally refuses to state SEC Table 1's contents. |
| No fabricated citation, quotation, page reference, timing or run | **Met** — §10.7 states the provenance of every quotation; §10 states that nothing was executed. |

---

## 12. Existing transcriptions that do not conform — named, NOT edited

Required by the task card, and by AGENTS.md rule 4: BATCH-001's artifacts are
immutable and snapshot-archived, with all 9 recorded hashes recomputing from the
committed blobs (`DEC-20260803-a5b9b1` D-1). **No file listed here was opened for
write by this task.** Corrections, if wanted, supersede under new ids.

| # | File | Rule | What does not conform | Substance affected? |
|---|---|---|---|---|
| V-1 | `…/TASK-20260803-f3aece/parameter_sets.md` §6, §8 | 5, 6 | Silent glyph restoration inside a verbatim block, beside a `markers set: 0` declaration. **This is the defect D-10 records.** | **No** — validator Q2 re-fetched and confirmed the restoration is unambiguous and correct; no number is affected. |
| V-2 | `…/TASK-20260803-f3aece/parameter_sets.md` §1 | 6 | An em-dash joining a section heading to body text inside a verbatim block (validator Q3). | **No** — "Cosmetic; substance exact" (validator). |
| V-3 | `…/TASK-20260803-f3aece/parameter_sets.md` §2 | 2 | `rounding_rule` stated as "truncated/rounded to 6 places", which does not determine the digit. | **No** — all five decimals and five exact rationals independently recomputed 5/5. |
| V-4 | `…/TASK-20260803-f3aece/parameter_sets.md` §2 | 4 | One transcribed column and four derived columns in one table with no per-column `[DERIVED]` marker; disclosure present but deferred to §8. | **No** — derivations disclosed and independently recomputed. |
| V-5 | `…/TASK-20260803-f3aece/parameter_sets.md` §4 | 1 | Unit stated in prose after the table rather than on the table or its headers. | **No** — 40/40 cells verified exact; unit is sourced from the caption. |
| V-6 | `…/TASK-20260803-292b99/rate_regime_extraction.md` §5 | 3 | Summary table repeats values without the `see: §<n>` pointer to their locus-bearing home. | **No** — loci present and correct in §§1–4. |
| V-7 | Both producers, batch-wide | 3 | Two hash-abbreviation forms in one batch: `ebbd94ac…c564b8` and `dcc68788…`. | **No** — both honest; only the second form is permitted henceforth. |

**Every one of these is a form non-conformance, and not one of them is a value
error.** That is worth stating precisely, because the point of this convention is
that a reader should not have to re-fetch a source to establish it. In BATCH-001
someone did have to — the validator re-acquired 26 sources to get 25 hash
matches and confirm 0 fabrications — and that is the cost this document exists to
remove.

**One thing this convention does not claim to fix.** It governs form. It does not
prevent the error family `DEC-20260803-a5b9b1` D-2, D-3 and D-4 record — asserting
something about a source's content that the source does not say. `TASK-20260803-f3aece`
was fully conforming in intent and still declined to transcribe SEC Table 1 for a
reason that did not exist (D-3). No convention catches that. Reading the source
catches that.
