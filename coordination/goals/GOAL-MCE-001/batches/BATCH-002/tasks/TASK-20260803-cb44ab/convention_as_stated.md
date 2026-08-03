# The costing convention SEC Table 1 uses — in the authors' own words

**Task:** `TASK-20260803-cb44ab` · **Goal:** `GOAL-MCE-001` · **Batch:** BATCH-002
**Companion:** `cost_table_transcription.md` (the table itself) ·
`source_access_log.yaml` (retrieval)

**Source for every quotation in this file:** SEC =
`https://classic.mceliece.org/mceliece-security-20221023.pdf`, HTTP 200,
332,574 bytes, sha256
`db17ef0879cb8822120c312b7290f7db82fe9fc356bd16058ad334a512b523fa`, fetched
2026-08-03T19:52:54Z. Page numbers are PDF pages; on this document the PDF page
and the printed folio agree.

---

## 0. Standing conditions on this document

- **Nothing here is adopted.** Recording what a third party charges for memory
  is not adopting their convention. `ISD-FC-2026` is **not** adopted, is not
  adoptable by this task (`DEC-20260802-344883` D-6: *"ISD-FC-2026 IS NOT
  ADOPTED… a usable draft, not a binding convention"*), and is not compared
  against anything here.
- **No competing convention is proposed.** This document contains no
  definition, formula or cost model of this program's own.
- **Nothing here is endorsed.** Several quoted passages are the Classic
  McEliece submission's own security claims about its own parameter sets. They
  are transcribed because they state *which accounting the submission
  operates under* — which is exactly the convention question — and for no
  other reason. **This task asserts nothing about whether any parameter set is
  secure or threatened, and none of these quotations may be read as this
  program adopting, echoing or contesting them.**
- **Extraction standard:** the stricter BATCH-001 standard. Quotations are
  reproduced with their raw kerning and ligature artifacts visible (`T able`,
  `1 /2`, `140 .8`, `ﬁ`, `ﬀ`); readings appear outside quotations and are
  labelled. Flattened superscripts are marked `[EXTRACTION-DAMAGED]` with the
  measurement supporting the finding. Quotations are path A (pypdf 6.14.2)
  unless stated; path B (pdfminer.six 20260107) is given where it differs.

---

## 1. What the authors charge for memory

### 1.1 The three models, verbatim (PDF page 9)

> *"As numerical examples of the importance of memory access, Table 1 reports
> output of the Esser–Bellini security estimator [33] for each of the selected
> Classic McEliece parameter sets, under three diﬀerent models supported by the
> estimator:"*

> *"• The rows where “mem” is 0 use a model making a physically implausible
> assumption of free access to arbitrarily large amounts of memory. In this
> model, the 2011/2012 algorithms using “representations” provide noticeable
> speedups compared to Stern’s 1989 algorithm."*

> *"• The rows where “mem” is 1 /2 use a model assigning plausible square-root
> costs to memory access. The rows where “mem” is 1/3 use a model assigning
> cube-root costs to memory access. In these models, the algorithms using
> “representations” provide much smaller speedups compared to Stern’s
> algorithm. In other words, most of the claimed speedup from these algorithms
> at cryptographic sizes relies on assigning unrealistically low costs to
> memory access."*

*(Transcriber's reading, outside the quotation: `diﬀerent` is the `ﬀ` ligature
for `different`; `1 /2` in the first sentence of the second bullet is a kerning
split of `1/2` — note the same bullet prints `1/3` unsplit, which is why the
artifact is left visible rather than normalised.)*

### 1.2 The caption's own statement of the three models (PDF page 10)

> *"T able 1: Output of the Esser–Bellini estimator for the selected Classic
> McEliece parameter sets. The “mem” column is 0 for estimates assuming free
> memory access, 1 /3 for estimates using a cube- root assumption, and 1 /2 for
> estimates using a square-root assumption. Some cost components are ignored in
> all estimates."*

### 1.3 What that amounts to, stated only in these words

SEC's entire specification of the memory charge, as printed, is:

| `mem` | SEC's words for the model |
|---|---|
| `0` | *"a model making a physically implausible assumption of free access to arbitrarily large amounts of memory"*; caption: *"assuming free memory access"* |
| `1/3` | *"a model assigning cube-root costs to memory access"*; caption: *"using a cube- root assumption"* |
| `1/2` | *"a model assigning plausible square-root costs to memory access"*; caption: *"using a square-root assumption"* |

**No formula, exponent convention, unit, or definition of "cost of memory
access" appears anywhere in SEC.** The three phrases above are the whole of it.
SEC attributes the models to the estimator — *"three diﬀerent models supported
by the estimator"* — and cites `[33]`. §5 records what that means for anyone who
needs the actual cost function.

---

## 2. What memory-access model they assume, and why — in their words (PDF page 9)

The paragraph immediately preceding the table's introduction, which is SEC's
statement of *why* it charges for memory at all:

> *"Many of the papers cited above include precise operation counts and precise
> probability formulas for each attack iteration. A closer look shows that
> these operation counts tend to omit important components of attack costs. For
> example, the lowest operation counts in the literature ignore the costs of
> random access to a huge array, much larger than the public key being
> attacked. In reality, time and energy are required to move data across long
> distances, and to control which array elements are being accessed; meanwhile
> the same amount of attack hardware allows much more parallelism for
> low-memory attacks."*

And the section's opening position on asymptotics, which sets up why concrete
tables are used at all (PDF page 9, section 3.5's first lines):

> *"It is important to realize that o(1) does not mean 0: it means something
> that converges to 0 as n→∞ . More detailed attack-cost evaluation is
> therefore required for any particular parameters."*

---

## 3. What they exclude — in their words

### 3.1 The blanket exclusion, in the caption itself (PDF page 10)

> *"Some cost components are ignored in all estimates."*

**SEC does not enumerate which components.** That sentence is the whole of the
blanket statement; the only concrete instance SEC gives is §3.2 below.

### 3.2 The one exclusion SEC does name: vector length (PDF page 10)

> *"However, the underlying estimator from [33] counts each vector operation as
> just 1 operation: in particular, ﬁndingC collisions between two lists, each
> list containing L vectors, is assigned cost 2L +C, no matter what the vector
> length is."*

*(Transcriber's reading: `ﬁndingC` is the `ﬁ` ligature plus a lost space, for
`finding C`; `2L +C` is `2L + C`. Path B renders this as `finding C` and
`2L + C` with the `ﬁ` ligature retained.)*

### 3.3 What SEC says follows from that exclusion (PDF page 10)

> *"Consequently, the 140.8 actually counts more than 2 143 bit operations. The
> exact numbers in Table 1 should be expected to be superseded by larger
> numbers from future estimators that count bit operations."*

`[EXTRACTION-DAMAGED: flattened superscript]` — in the printed PDF, `143` is
set at 7.97 pt raised 5.1 pt above the 11.96 pt `2`; the printed form is
2^143. Path B renders the same string as `2143`. **Neither extractor's
rendering is the printed text.**

### 3.4 The memory an estimate assumes is stated for exactly one entry (PDF page 10)

> *"More importantly, the 140 .8 is for an attack using memory 2 86.6,
> according to the same estimator. Accounting for costs of memory access shows
> that all known attacks against mceliece348864 are much more expensive than
> brute-force AES-128 key search."*

`[EXTRACTION-DAMAGED: flattened superscript]` — `86.6` at 7.97 pt, raised
5.1 pt; printed form 2^86.6. `140 .8` is a kerning split of `140.8`. Path B:
`140.8` and `286.6`.

**This is the only memory quantity SEC attaches to any table entry.** Table 1
itself has no memory column. The second sentence is the submission's own
security claim; it is transcribed for completeness of the passage and is not
this task's statement.

---

## 4. Every place they hedge

Collected exhaustively from the passages that bear on the table's cost
accounting (PDF pages 9–11 and the single later use on page 13). Each is
quoted; the middle column is the hedge itself, in the source's words.

| # | Where | The hedge, in SEC's words |
|---|---|---|
| H1 | p.9, bullet 1 | *"a model making a physically implausible assumption of free access to arbitrarily large amounts of memory"* — the `mem 0` column is labelled by its own authors as resting on a physically implausible assumption |
| H2 | p.9, bullet 2 | *"a model assigning **plausible** square-root costs"* — plausibility is claimed for `1/2` and, notably, **not** claimed in the same sentence for `1/3`, which is described only as *"a model assigning cube-root costs to memory access"* |
| H3 | p.9, bullet 2 | *"most of the claimed speedup from these algorithms at cryptographic sizes relies on assigning unrealistically low costs to memory access"* |
| H4 | p.10, caption | *"Some cost components are ignored in all estimates."* — applies to **all three** models, not only to `mem 0` |
| H5 | p.10 | *"the underlying estimator from [33] counts each vector operation as just 1 operation… no matter what the vector length is"* |
| H6 | p.10 | *"Consequently, the 140.8 actually counts more than 2 143 bit operations."* `[EXTRACTION-DAMAGED: flattened superscript, see §3.3]` |
| H7 | p.10 | *"The exact numbers in Table 1 should be expected to be superseded by larger numbers from future estimators that count bit operations."* — the source's own statement that its table's exact values are provisional |
| H8 | p.10 | *"Larger parameter sets can be above or below (e.g.) AES-256 depending on whether costs of memory are included."* |
| H9 | p.11 | *"the estimates in the table are underestimates of bit operations, for example counting each vector operation as just 1 operation"* |
| H10 | p.11 | *"One can object to the assignment of 460896 to “Category 3” (AES-192) since NIST estimates 2 207 operations for brute-force AES-192 key search while Table 1 says 201 .0, which is below 207; but, as noted above…"* — the source raises the objection against itself `[EXTRACTION-DAMAGED: flattened superscript — `207` at 7.97 pt raised 5.1 pt; printed 2^207; `201 .0` is a kerning split of `201.0`]` |
| H11 | p.9 | *"It is important to realize that o(1) does not mean 0… More detailed attack-cost evaluation is therefore required for any particular parameters."* |
| H12 | p.13 | *"Full quantiﬁcation depends on the exact cost of state-of-the-art attacks, as in Section 3.5."* |

H1–H12 is the complete set found by reading §3.5 in full and then grepping the
whole 36-page extraction for every occurrence of *"Table 1"* (**7** hits) and
of *"memor"* (**18** hits, case-insensitive), and reading the surrounding
sentence of each.

**A caution that belongs with that count, and is the reason the strict
standard matters:** the caption's own reference to the table is rendered
`T able 1` by path A and is therefore **missed** by a naive grep for
`Table 1` — 7 hits plus 1 kerning-split hit, 8 references in total. A
subsequent agent who greps this document rather than reading it will silently
skip the caption, which is where the blanket exclusion H4 lives.

---

## 5. Which accounting the source itself operates under

Transcribed because it identifies **which column of the table the publishing
party treats as operative** — a convention fact. **These are the submission's
own claims about its own parameter sets. This task endorses none of them,
contests none of them, and concludes nothing from them.**

PDF page 10, on the 6960119 parameter set:

> *"• Imagining free memory access: The submission has always stated that this
> parameter set is breakable using fewer bit operations than brute-force
> AES-256 key search when the costs of memory access are ignored: “Subsequent
> ISD variants have reduced the number of bit operations considerably below
> 2 256.” This is consistent with the 2 246.6 number in Table 1."*

PDF page 11:

> *"• Counting realistic costs for memory: “We expect that switching from a
> bit-operation analysis to a cost analysis will show that this parameter set
> is more expensive to break than AES-256 pre-quantum and much more expensive
> to break than AES-256 post-quantum.” This is consistent with the 2 279.2
> number in Table 1."*

> *"Given the fact that memory is not free in the real world, the submission
> has always assigned this parameter set to NIST’s “Category 5” (AES-256)."*

> *"Since the underlying facts have not changed, the submission continues to
> assign its selected parameter sets to “categories” 1, 3, 5, 5, 5
> respectively. As before, these assignments are based on counting realistic
> costs for memory."*

> *"If NIST instead decides to make “category” assignments on the basis of bit
> operations with free memory access, then the correct assignments will instead
> be 1, 2, 4, 4, 5. This does not reﬂect any instability in the Classic
> McEliece security estimates: the submission has always been careful to
> distinguish between these two diﬀerent types of accounting for the costs of
> attacks."*

`[EXTRACTION-DAMAGED: flattened superscripts]` in the two quotations above:
`256` (printed 2^256), `246.6` (printed 2^246.6) and `279.2` (printed 2^279.2)
are each set at 7.97 pt raised 5.1 pt above an 11.96 pt `2`; path B renders
them `2256`, `2246.6`, `2279.2`. `reﬂect` and `diﬀerent` are the `ﬂ` and `ﬀ`
ligatures.

**Observation, recorded and not resolved:** `279.2` occurs at two cells of
Table 1 (`6688128 / 1/3 / Stern` and `6960119 / 1/2 / MO`). Which one this
sentence refers to is **not adjudicated here**; see
`cost_table_transcription.md` §5.

The single later use of the table elsewhere in SEC (PDF page 13), which shows
the source treating table values as bit-denominated security levels:

> *"For example, in the setting of Table 1 with 1 /2 for “mem”, the tightness
> loss is just 0 .8 bits for 460896. To check this calculation, run the
> estimator for (4608 , 96) and (8192, 96), and compare the security-level
> diﬀerence to…"*

*(Transcriber's reading: `1 /2` = `1/2`; `0 .8` = `0.8`; `(4608 , 96)` =
`(4608, 96)`.)*

---

## 6. What the convention does NOT state, in SEC

Named because a cost figure without its model is not a baseline, and this is
the part of the model SEC does not carry. **None of these gaps is filled here.**

| Missing from SEC | Status |
|---|---|
| A formula for the memory charge — what "cube-root costs" and "square-root costs to memory access" cost, of what quantity, in what unit | **not stated in SEC.** Only the three phrases in §1.3 appear. |
| The unit of the table's entries | **not stated in the table or caption.** The caption says only *"Output of the Esser–Bellini estimator"*. SEC's prose uses three specific values as exponents of 2 (§5, and `cost_table_transcription.md` §5) and speaks of *"bits"* on p.13; no unit is printed with the table. |
| Which cost components are ignored | **not enumerated.** The caption's *"Some cost components are ignored in all estimates"* is unqualified; the only named instance is the vector-length exclusion (§3.2). |
| A hardware, architecture, parallelism, energy or area model | **not stated.** p.9 refers in prose to *"time and energy… to move data across long distances"* and to *"the same amount of attack hardware"*, but no model is given. |
| Time–memory tradeoff data | **not present.** SEC prints three fixed `mem` values, not a tradeoff curve, and Table 1 has no memory column. |
| Memory usage per entry | **not present**, except the single prose figure 2^86.6 for the `348864 / 0 / MO` attack (§3.4). |
| Quantum costs at these parameters | **not in Table 1.** SEC discusses quantum attacks in prose on p.9 only. |
| The estimator's own cost model | **deferred to `[33]`**, Esser–Bellini, *"Syndrome decoding estimator"*, PKC 2022, `https://eprint.iacr.org/2021/1243`. **That paper was NOT read by this task.** Only its eprint abstract page was fetched (HTTP 200, 16,056 bytes, sha256 `59810b6c…`), and only to record its identity. No statement in this document comes from it. |

---

## 7. Marker inventory for this file

- `[RECALLED-NOT-READ]` markers: **0**. Every quotation and every number here
  comes from the retrieval whose sha256 is recorded at the head of this file.
- `[EXTRACTION-DAMAGED]` markers: **5** (§3.3, §3.4, H10, and the two grouped
  in §5 covering `2^256` / `2^246.6` / `2^279.2`). All are flattened
  superscripts in quoted prose, each supported by a character-size and
  baseline-offset measurement. **No table cell is marked**: every glyph in the
  table region is a single 11.96 pt size, measured across 771 glyphs.
- Conventions adopted: **0**. Conventions proposed: **0**. Costs computed:
  **0**.
