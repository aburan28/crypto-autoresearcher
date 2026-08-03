# PROPOSED transcription convention — TASK-20260803-a53f73

**Task:** TASK-20260803-a53f73 · **Goal:** GOAL-MCE-001 · **Batch:** BATCH-002
**Role:** executor · **Date:** 2026-08-03
**Requested policy:** `executor-implementation` · **Resolved model:** `claude-opus-5` ·
**fallback_used:** `true`
**Authority:** `DEC-20260803-a5b9b1` D-10 (OPEN), from validator finding
`TASK-20260803-409c5e` Q2 and Q4.

> **PROPOSED ONLY.** Settling this as durable program state is
> `TASK-20260803-3aa684`'s act. It applies to `TASK-20260803-cb44ab`, running
> concurrently in this batch.

---

## 1. The divergence, quoted from the record that found it

`DEC-20260803-a5b9b1` D-10:

> "OPEN — divergent transcription standards inside one batch (validator Q2).
> `TASK-20260803-f3aece` silently glyph-normalised quoted material presented as
> verbatim while declaring zero `[EXTRACTION-DAMAGED]` markers;
> `TASK-20260803-292b99` left raw `(cid:NN)` tokens visible and marked them. No
> number is affected. The convention must be fixed before the next transcription
> batch, not after."

The validator's own finding, `TASK-20260803-409c5e` Q2:

> "The normalisation is **unambiguous and correct** — I confirmed the restored
> reading against PC's Decap step … and **no number is affected**. But it is an
> undisclosed editorial step inside a block labelled verbatim, and it sits beside
> a zero-damage declaration. … **The two producers in one batch applied different
> disclosure standards to the same class of extraction artifact.** Recommend the
> batch adopt 292b99's standard."

And Q4, which the settled convention must also answer:

> "the `292b99` 'raw extraction, unedited' blocks are extractor-settings-dependent.
> … The *tokens* are identical and no claim depends on the layout, but 'raw and
> unedited' is only reproducible if the extraction settings are recorded, and
> they are not."

---

## 2. THE CONVENTION

**`TASK-20260803-292b99`'s standard is the program standard, plus one addition
from Q4 that neither producer met.** Four rules.

**T1 — `VERBATIM` means byte-faithful to the extractor's output.** A block
labelled `VERBATIM` reproduces what the extractor emitted, including `(cid:NN)`
tokens, dislocated superscripts, ligature artifacts, and the source's own
misspellings. Nothing inside a `VERBATIM` block is silently repaired. If nothing
in the transcription is labelled `VERBATIM`, nothing carries this guarantee.

**T2 — A normalisation is permitted, and is disclosed beside the raw form.**
Extraction artifacts often have one obvious correct reading, and refusing to
state it is not extra rigor — `TASK-20260803-f3aece`'s normalisation was
*correct* and the validator confirmed it independently. What is forbidden is
performing it **inside** a block labelled `VERBATIM`. The permitted form is:
give the raw extraction, then give the normalised reading labelled
`[NORMALISED]`, then say what confirmed it. `TASK-20260803-f3aece`'s own
confirmation route — checking the ciphertext sentence against the document's
Decap step — is the model; only the labelling was missing.

**T3 — `[EXTRACTION-DAMAGED]` marks anything not reliably reconstructible, and a
zero-marker declaration is a claim that must be true.** Damage is marked at the
narrowest scope that is honest: `rate_regime_extraction.md` §2.3's
`[EXTRACTION-DAMAGED — symbolic form only; the numeric thresholds are clean]` is
the exemplar, because it tells a reader precisely which characters to distrust.
A damaged expression is **not reconstructed and carries no claim** anywhere in
the deliverable (`rate_regime_extraction.md` §3.4 is the exemplar refusal). A
transcription that declares **zero** markers is asserting that every glyph in it
survived extraction intact; make that declaration only after checking, and never
beside an undisclosed normalisation.

**T4 — Record the extraction settings, or do not call a block "raw".** Name the
extractor and its version, and any non-default layout parameters (for
`pdfminer.six`, the `laparams`). This is validator finding Q4 and **neither
BATCH-001 producer met it**: the validator could not reproduce `292b99`'s
column alignment with default settings. "Raw and unedited" is a reproducibility
claim, and it is only checkable if the command that produced it is recorded.
Where two extractors were run and required to agree — `TASK-20260803-f3aece`'s
practice — say so and name both; that is a control and it should be visible.

### 2.1 What a transcriber must do, operationally

1. Record extractor name, version, and non-default settings in the deliverable
   or its access log **before** quoting anything (T4).
2. Quote `VERBATIM` blocks byte-faithfully from the extractor's output (T1).
3. Where a glyph artifact has one obvious reading, add a `[NORMALISED]` line
   beside the raw form, with what confirmed it (T2). Never edit inside
   `VERBATIM`.
4. Mark `[EXTRACTION-DAMAGED]` at the narrowest honest scope; do not reconstruct
   the damaged expression; do not let it carry a claim anywhere (T3).
5. State the marker count only if it was checked, and never beside an
   undisclosed normalisation (T3).
6. Numbers are held to the strictest reading of all four rules. A number that
   passed through a normalisation without disclosure is not a transcribed number.

### 2.2 Why 292b99's standard rather than f3aece's

Not because `f3aece` was wrong about the text — it was right, and the validator
verified it. Because the two standards are **asymmetric in their failure modes**.
An over-marked transcription costs a reader some noise. An under-marked one
costs a reader the ability to tell repaired text from source text, and that
distinction cannot be recovered later without re-acquiring the PDF. A convention
is chosen for its worst case.

`docs/inventor-protocol.md`'s "controls before belief" is the same instinct
applied to statistics: a quantity is an artifact until the measurement has been
run against a null object. Here the null object is the raw extraction, and T2
keeps it in the record beside the reading.

### 2.3 Scope of this convention

- Binds **transcription tasks in this program's goals**, starting with
  `TASK-20260803-cb44ab` in this batch.
- It is a **disclosure** convention. It does not require any particular
  extractor, forbid normalisation, or make a transcription more authoritative
  than its source.
- It asserts nothing about any paper's content and nothing about Classic
  McEliece's security.
- **Neither BATCH-001 producer is retroactively invalidated by it.** D-10 records
  that no number was affected, and `DEC-20260803-a5b9b1` D-1 admits both
  packages. A convention settled after the fact governs what comes next; it is
  not a finding against work done before it existed. Applying it backwards would
  be re-scoring completed work against a rule adopted later, which this program
  does not do.

### 2.4 One thing this convention does not settle

`TASK-20260803-cb44ab`'s handoff instructs it to *"apply the STRICTER of the two
BATCH-001 standards"* because it cannot read this file (disjoint write scopes, no
dependency). **T1–T3 are that stricter standard, so a task following its handoff
will comply with them.** T4 is an addition neither BATCH-001 producer met, so
`cb44ab` may not satisfy it. **If `cb44ab`'s deliverable omits extraction
settings, that is a gap against a convention it could not see, not a producer
defect** — the fix is a note at filing, not a finding against the task.
