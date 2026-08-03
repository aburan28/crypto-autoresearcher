# PROPOSED specification KN-LIT entries A–E, at filing quality — TASK-20260803-a53f73

**Task:** TASK-20260803-a53f73 · **Goal:** GOAL-MCE-001 · **Batch:** BATCH-002
**Role:** executor · **Date:** 2026-08-03
**Requested policy:** `executor-implementation` · **Resolved model:** `claude-opus-5` ·
**fallback_used:** `true`
**Measured on:** HEAD `2ea6216dda15f77044f5785144d8c0296dad9cc7`

> **PROPOSED ONLY. NOTHING UNDER `knowledge/` WAS WRITTEN OR MODIFIED.**
> Origin: `TASK-20260803-f3aece/proposed_kn_lit_entries.md` §§3–7, deferred by
> `DEC-20260803-a5b9b1` `knowledge_promotion.not_warranted` (2) so that the
> correction task could land first. This is that task.

---

## 1. INDEPENDENT DEDUP DETERMINATION — re-run, not inherited

Named duty 5: *"Re-run that dedup determination independently."* The BATCH-001
determination was read **after** this one was run, and the probes below are this
task's own, executed at HEAD `2ea6216d`.

**Census reproduced.**

```
$ grep -rli "mceliece" knowledge/literature/ | wc -l
169
$ ls knowledge/literature/*.md | wc -l
7807
```

**Probes, over the whole of `knowledge/` (not only `literature/`):**

| Probe | Hits in `knowledge/` | Determination |
|---|---|---|
| `mceliece-spec` | 0 | Specification not held |
| `cryptosystem specification` | 0 | " |
| `conservative code-based cryptography` | 0 | Document family not held |
| `guide for implementors` | 0 | Not held |
| `guide for security reviewers` | 0 | Not held |
| `plaintext confirmation` | 0 | Not held |
| `classic.mceliece.org/mceliece` (the PDF path stem) | 0 | No entry cites any of the four PDFs |
| `NIST.IR.8545` | 0 | IR 8545 not held |
| `10.6028/NIST.IR.8545` | 0 | " |
| `nvlpubs.nist.gov` | 1 — `KN-LIT-7620` | Near-neighbour, examined below |
| `NIST IR` | 1 entry — `KN-LIT-7620` (plus the derived `INDEX.md`, `SOURCES.md`, `sources.json`) | " |
| `Status Report on the` | same 1 entry | " |
| `10.6028` | 4 entries — `KN-LIT-7620`, `055`, `056`, `4573` | none is IR 8545 |
| `Fourth Round` | 1 — `KN-LIT-4537` | false positive, examined below |
| `mceliece(348864\|460896\|6688128\|6960119\|8192128)` | 1 — `KN-LIT-6614` | Near-neighbour, examined below |

**Hash probe, which BATCH-001 did not run.** Each of the five documents' recorded
`sha256` was grepped across `knowledge/`: **0 hits for all five.** No entry cites
any of these bytes under any title.

**The near-misses, examined individually rather than waved through:**

- **`KN-LIT-6614`** — Lahr–Niederhagen–Petri–Samardjiska, *"Side Channel
  Information Set Decoding using Iterative Chunking … "Classic McEliece"
  Hardware Reference Implementation"*. The only corpus entry containing a Classic
  McEliece parameter-set name, and it contains it incidentally, inside a relayed
  abstract. A third-party side-channel paper, not the specification; it
  transcribes no parameter table. **Not a duplicate.** (Its `identifiers` are all
  `null` and it carries `citation_verified: read` — the provenance class
  `KN-OPEN-3f7a21` flags as unconfirmed. Nothing here relies on it.)
- **`KN-LIT-7620`** — *"NIST IR 8610: Status Report on the Second Round of the
  Additional Digital Signature Schemes …"*. Same author group, same series,
  **different report**: IR 8610 covers additional signatures; IR 8545 covers the
  fourth-round KEMs and is the one that states Classic McEliece's status. **Not a
  duplicate**, and a useful formatting precedent.
- **`KN-LIT-4537`** — matched *"fourth round"* inside a Keccak abstract;
  `grep -c "8545"` → **0**. Not IR 8545.
- **`KN-LIT-1908`** — matched the arXiv identifier `2603.08545`. Not IR 8545.
- **`KN-LIT-055`, `056`, `4573`** — carry `10.6028` DOIs for other NIST
  publications. Checked individually; none is `10.6028/NIST.IR.8545`.

**DETERMINATION: the Classic McEliece primary specification is NOT held by this
corpus, nor is any document of its round-4 family, nor NIST IR 8545. All five
entries below are new.** This is a positive check run by this task, not an
inherited assumption, and it **agrees with** `TASK-20260803-f3aece`'s
determination on every point.

**Scope limit, stated plainly.** These are string matches over `knowledge/` at one
commit on one branch. They would miss an entry holding one of these documents
under a wholly different title with no matching identifier, URL, phrase, or hash.
Fourteen probes plus a hash probe make that unlikely; the check is still a grep,
not a proof.

---

## 2. `citation_verified: read` — who earned it, and how it is kept auditable

Named duty 5: `read` **only** if the producer actually read the document.
`KN-OPEN-3f7a21` records **7457** entries carrying a `read` flag against a
`downloads/` tree that is absent and was never git-tracked. This package must not
add to that count.

**`read` is proposed for all five, and it is earned — by
`TASK-20260803-f3aece`, not by this task.** That task fetched each document
(HTTP 200, byte count and sha256 recorded in its `source_access_log.yaml`,
extracted with two independent extractors and agreement required) and its
transcriptions were re-acquired and re-checked by validator
`TASK-20260803-409c5e`, which independently re-verified all 40 IMPL Table 1 cells
and re-ran the 10/10 size-formula control.

**Three disciplines make the flag auditable rather than assertive**, and every
entry below carries all three:

1. A `citation_verified_note` naming **which task read it, when, at what URL,
   status, byte count and sha256**, so the flag points at a receipt.
2. `committed_locally: false` and **no `## Local copies` section**. No
   third-party PDF is committed; the sha256 is the integrity anchor. Filing a
   `downloads/` path here would re-create the exact defect `KN-OPEN-3f7a21`
   documents.
3. An explicit statement of **what was read and what was not** — for the
   specification, only §§3, 6, 7 were read closely.

**The drafting agent (this task) did not read any of the five documents.** Every
entry says so. Working from another task's committed, independently re-acquired
transcription is the honest basis, and stating it is what separates this flag
from the 7457.

---

## 3. Two filing-quality changes applied to all five BATCH-001 drafts

### 3.1 `sha256` moved OUT of `identifiers` — a measured defect, not a preference

All five BATCH-001 drafts place `sha256:` inside `identifiers:`. That key is
emitted into the derived source index as a bibliographic identifier.
`tools/build_source_index.py::collect_literature()` walks
`IDENTIFIER_ORDER = ("eprint","arxiv","doi","isbn","url")` and then walks every
**remaining** key of `identifiers` through `canonical_identifier()`, whose
fallback is `f"{kind}:{low}"`. Reproduced at HEAD `2ea6216d` on proposed entry
A's own frontmatter:

```
identifiers -> ['url:classic.mceliece.org/mceliece-spec-20221023.pdf',
                'sha256:dcc6878852ef8a00a7bedd859da661770cf85d2c3d9239e06d25e4a0d365fd12']
```

`SOURCES.md` and `sources.json` are **derived and regenerated** (`make sources`),
never hand-edited, so this cannot be repaired downstream. Every entry below
therefore carries a top-level `source_artifact:` block instead. That key is new
to the corpus (checked: zero occurrences at HEAD `2ea6216d`) and is inert in the
derived index because unknown top-level keys are ignored. **If the Coordinator
declines the schema extension, the hash goes in the body prose — but it must not
go under `identifiers`.**

### 3.2 Cross-references retargeted to the superseding entries

BATCH-001's entry A pointed at `KN-LIT-4c8135`, `13a01d`, `71d1a0`, `7ee1a9`.
All four are superseded by this package. The references below point at the new
IDs. **If a review rejects any supersession, that reference reverts to the old
ID** — the filer must reconcile this at filing time, not assume it.

---

## 4. Entry A — the primary specification (`KN-LIT-48b4eb`)

```markdown
---
id: KN-LIT-48b4eb
type: literature
title: "Classic McEliece: conservative code-based cryptography: cryptosystem specification"
authors: []
authors_note: >-
  The document's title page carries no author list; it is issued by the Classic
  McEliece team. Authors NOT filled in from recall. The team roster is at
  https://classic.mceliece.org/people.html, which was not fetched.
year: 2022
venue: "Classic McEliece round-4 NIST PQC submission, document dated 23 October 2022"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: "https://classic.mceliece.org/mceliece-spec-20221023.pdf"
source_artifact:
  url: "https://classic.mceliece.org/mceliece-spec-20221023.pdf"
  sha256: "dcc6878852ef8a00a7bedd859da661770cf85d2c3d9239e06d25e4a0d365fd12"
  retrieved_by: TASK-20260803-f3aece
  committed_locally: false
tags: [code-based, mceliece, goppa, niederreiter, specification, parameters, kem, primary-source]
confidence: reported
citation_verified: read
citation_verified_note: >-
  `read` is earned by TASK-20260803-f3aece (GOAL-MCE-001 BATCH-001), which
  fetched this PDF from the designers' own site on 2026-08-03 (HTTP 200; URL,
  byte count and sha256 in that task's source_access_log.yaml) and extracted it
  with two independent extractors (pypdf and pdfminer.six) requiring agreement.
  Validator TASK-20260803-409c5e independently re-fetched it and recomputed
  every arithmetic claim below. ONLY SECTIONS 3, 6 AND 7 WERE READ CLOSELY. The
  agent that drafted this entry (TASK-20260803-a53f73) did NOT read the
  document; it worked from that task's committed transcription. No local copy
  is committed; the sha256 above is the integrity anchor.
added: "2026-08-03"
superseded_by: null
---

## Contribution
The official definition of Classic McEliece, so designated by the project's own
Specification page (*"The official definition of Classic McEliece is the
cryptosystem specification"*). 16 pages. Defines the KEM over binary Goppa codes
in Niederreiter form: parameters, matrix reduction and generation, encoding and
decoding subroutines, key generation, fixed-weight-vector generation,
encapsulation, decapsulation, byte-string representations, and ten selected
parameter sets.

## Key claims (as reported)
- Parameters are `(m, n, t)` with `q = 2^m`, `n ≤ q`, `t ≥ 2` and `mt < n`; the
  specification defines `k = n − mt` (Section 3). **Definitional, not a claim.**
- **Ten selected parameter sets (Section 7)** — five `(m, n, t)` triples, each in
  a plain and an "f" (semi-systematic, `(μ, ν) = (32, 64)`) variant:
  `(12, 3488, 64)`, `(13, 4608, 96)`, `(13, 6688, 128)`, `(13, 6960, 119)`,
  `(13, 8192, 128)`.
- **Resulting code rates `k/n`**, computed from the specification's own
  definition: `85/109 ≈ 0.779817`, `35/48 ≈ 0.729167`, `157/209 ≈ 0.751196`,
  `5413/6960 ≈ 0.777730`, `51/64 ≈ 0.796875`. The five rates of the
  **specification's own Section 7 sets** lie in `[0.729167, 0.796875]`.
  *(Phrased as the specification's sets rather than "the standardized sets": the
  ISO list is not identical — see the scoping note below and KN-LIT-209151.)*
- Symmetric parameters (Section 6.1): `l = 256`, `H` = first 256 bits of
  SHAKE256, `σ₁ = 16`, `σ₂ = 32`.
- Size formulas (Section 6.2): public key is `mt·⌈k/8⌉` bytes; ciphertext is
  `⌈mt/8⌉` bytes.
- **The document makes NO security-category claim and states NO numeric byte
  sizes**; it delegates both. See [[KN-LIT-7b78de]] and [[KN-LIT-b7f8f8]].
  Independently confirmed by the validator: the specification contains no
  occurrence of `categor*` and no byte sizes.

## Arithmetic verified by this program
`k = n − mt` and `k/n` in exact rationals for all five sets were **independently
recomputed 5/5** by `TASK-20260803-409c5e` from a re-fetched specification — on
`k`, on lowest-terms fractions, on gcds, and on 6-decimal-place values, with
`mt < n` everywhere and `5413` confirmed prime (`EV-MCE-332f99` O-1). This is
arithmetic on transcribed definitional values, **not** a reproduction of any
security claim.

## Relevance to this program
Primary source for `RQ-MCE-e65b3c` and `GOAL-MCE-001`. Supplies the rate `k/n`
that any rate-axis claim in the alternant/Goppa line ([[KN-LIT-c4c2ac]],
[[KN-LIT-6b5b72]], [[KN-LIT-819780]], [[KN-LIT-45b1b2]]) must be compared
against, and the exact `(n, k, t)` at which any memory-charged ISD baseline for
this goal must be computed.

**Scope discipline this entry must carry with it.** A rate comparison is only
meaningful once the axis is named: `KN-LIT-c4c2ac`'s restriction includes a
**code-family exclusion of Goppa codes** alongside its rate condition, and
`KN-LIT-819780`'s theorem is stated in the **dual** rate. This entry supplies a
**primal** rate `k/n`. Converting, and naming which axis is being compared, is
required before any arithmetic (`DEC-20260803-a5b9b1` D-2, D-4).

**Forecloses nothing on the attack side**, and asserts nothing about Classic
McEliece's security in either direction.

## Not verified here
Only Sections 3, 6 and 7 were read closely; the algorithm definitions in Sections
4 and 5 were **not audited**. No claim in this entry has been independently
reproduced beyond the arithmetic cross-check recorded above and the 10/10
size-formula control at
`coordination/goals/GOAL-MCE-001/batches/BATCH-001/tasks/TASK-20260803-f3aece/parameter_sets.md`
§5. **No implementation was run and no KAT was checked.** No local copy of the
PDF is committed.
```

> **ATTRIBUTION NOTE.** All five documents in this section were retrieved by
> `TASK-20260803-f3aece`, not by `TASK-20260803-292b99`, which retrieved the
> *attack* papers (`arXiv:2304.14757`, `iacr:2024/1193`, the `iacr:2025/531`
> abstract, the `iacr:2026/1232` abstract). The two retrieval sets are disjoint
> and must not be conflated in any `retrieved_by` field.

---

## 5. Entry B — guide for security reviewers (`KN-LIT-7b78de`)

```markdown
---
id: KN-LIT-7b78de
type: literature
title: "Classic McEliece: conservative code-based cryptography: guide for security reviewers"
authors: []
authors_note: No author list on the title page; issued by the Classic McEliece team.
year: 2022
venue: "Classic McEliece round-4 NIST PQC submission, document dated 23 October 2022"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: "https://classic.mceliece.org/mceliece-security-20221023.pdf"
source_artifact:
  url: "https://classic.mceliece.org/mceliece-security-20221023.pdf"
  sha256: "db17ef0879cb8822120c312b7290f7db82fe9fc356bd16058ad334a512b523fa"
  retrieved_by: TASK-20260803-f3aece
  committed_locally: false
tags: [code-based, mceliece, isd, security-categories, memory-cost, structural-attacks, esser-bellini, primary-source]
confidence: reported
citation_verified: read
citation_verified_note: >-
  `read` is earned by TASK-20260803-f3aece, which fetched this PDF on
  2026-08-03 (HTTP 200; URL, byte count and sha256 in that task's
  source_access_log.yaml) and extracted it with two independent extractors.
  Validator TASK-20260803-409c5e re-fetched it and read the re-fetched Table 1
  directly. The agent that drafted this entry (TASK-20260803-a53f73) did NOT
  read the document. No local copy is committed.
added: "2026-08-03"
superseded_by: null
---

## Contribution
36-page security discussion accompanying the round-4 submission. The round-4
submission overview delegates *"Expected strength (2.B.4) for each parameter
set"* and *"Analysis of known attacks (2.B.5)"* to this document — the delegating
sentence *"See the separate "guide for security reviewers" document"* was
confirmed in the overview by the validator — making it the submission's own
designated source for security-category claims.

## Key claims (as reported — THE SUBMITTERS' ASSESSMENTS OF THEIR OWN SCHEME)
Every bullet here is the submitters' assertion. This entry relays them and
**endorses none of them.**

- The submission assigns its selected parameter sets to categories
  *"1, 3, 5, 5, 5 respectively"* — i.e. 348864 → 1, 460896 → 3, 6688128 → 5,
  6960119 → 5, 8192128 → 5 — stating these are *"based on counting realistic
  costs for memory"*. (The `respectively` mapping is an inference, not a
  transcription; it was independently traced and confirmed by
  `TASK-20260803-409c5e` from the document's own row order and two explicit
  antecedents.)
- The same document states that under free-memory bit-operation accounting
  *"the correct assignments will instead be 1, 2, 4, 4, 5"*, and frames the two
  as **two cost models rather than a revision**.
- **Table 1 (p. 10) reports Esser–Bellini estimator output for all five sets
  under three memory models (`mem = 0, 1/3, 1/2`).** The lowest tabulated entry
  read by `TASK-20260803-f3aece` is **140.8** for `mceliece348864` at `mem = 0`.
- The document argues the estimator's numbers **underestimate** bit operations
  because it *"counts each vector operation as just 1 operation"*, and that the
  140.8 figure corresponds to an attack using memory `2^86.6`.

**The full cell-by-cell transcription of Table 1 is NOT in this entry.** It is
dispatched as `TASK-20260803-cb44ab` (GOAL-MCE-001 BATCH-002). This entry states
only what `TASK-20260803-f3aece` read; a reader needing the table must go to that
task's deliverable or to the PDF at the sha256 above.

## Relevance to this program
Directly bears on `GOAL-MCE-001`'s second completion criterion: a primary-source
statement of **how the designers charge memory**, with a published estimator
output at exactly the parameters this goal must cost. Any memory-charged ISD
baseline this program builds should be compared against it rather than derived in
ignorance of it.

**This document does NOT settle a costing convention for this program, and this
program is bound to none.** `DEC-20260802-344883` D-6 records
*"ISD-FC-2026 IS NOT ADOPTED … a usable draft, not a binding convention"*, and
`GOAL-HQC-001.next_action` says *"DO NOT bind GOAL-SDITH-001 to ISD-FC-2026."*
`DEC-20260803-a5b9b1` D-3 retracts the contrary claim that any binding existed.
**Reading this document is not adopting its convention, and citing its numbers
requires citing its model alongside them** — a cost figure without its memory
model is not a baseline.

## Not verified here
**Table 1's numbers were read but NOT reproduced, and no estimator was run by
this program.** The document's arguments about memory-access cost were not
evaluated. The security categories are relayed as the submission's assertions;
**this program takes no position on whether any parameter set meets any
category**, and no statement here bears on Classic McEliece's security in either
direction. Only the passages named above were read closely. No local copy is
committed.
```

---

## 6. Entry C — guide for implementors (`KN-LIT-b7f8f8`)

```markdown
---
id: KN-LIT-b7f8f8
type: literature
title: "Classic McEliece: conservative code-based cryptography: guide for implementors"
authors: []
authors_note: No author list on the title page; issued by the Classic McEliece team.
year: 2022
venue: "Classic McEliece round-4 NIST PQC submission, document dated 23 October 2022"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: "https://classic.mceliece.org/mceliece-impl-20221023.pdf"
source_artifact:
  url: "https://classic.mceliece.org/mceliece-impl-20221023.pdf"
  sha256: "86225992a73a2dc986b2ef5edfcfa3e28d49684fffd8be281237e1e5af2757a3"
  retrieved_by: TASK-20260803-f3aece
  committed_locally: false
tags: [code-based, mceliece, key-sizes, implementation, constant-time, primary-source]
confidence: reported
citation_verified: read
citation_verified_note: >-
  `read` is earned by TASK-20260803-f3aece, which fetched this PDF on
  2026-08-03 (HTTP 200; URL, byte count and sha256 in that task's
  source_access_log.yaml). Validator TASK-20260803-409c5e re-fetched it and
  independently verified ALL 40 cells of Table 1, because the private-key
  column has no arithmetic bridge to the specification. The agent that drafted
  this entry (TASK-20260803-a53f73) did NOT read the document. No local copy is
  committed.
added: "2026-08-03"
superseded_by: null
---

## Contribution
19-page implementors' guide; the submission overview delegates *"Detailed
performance analysis (2.B.2)"* to it. Its Table 1 is the primary source for the
numeric key, ciphertext and session-key sizes of all ten selected parameter sets.

## Key claims (as reported)
- **Table 1** (sizes in bytes; public key / private key / ciphertext / session
  key):
  - `mceliece348864` and `348864f`: 261120 / 6492 / 96 / 32
  - `460896` and `460896f`: 524160 / 13608 / 156 / 32
  - `6688128` and `6688128f`: 1044992 / 13932 / 208 / 32
  - `6960119` and `6960119f`: 1047319 / 13948 / 194 / 32
  - `8192128` and `8192128f`: 1357824 / 14120 / 208 / 32
- The private key *"can be compressed down to 40 bytes (or 32 bytes for non-f
  parameter sets) with uncompression less expensive than key generation"*, so the
  tabulated private-key column is the **uncompressed** form.
- The guide characterises the trade-off as large public keys with small
  ciphertexts, and notes use in PQ-WireGuard.

## Control run by this program
Every public-key and ciphertext figure in Table 1 was independently re-derived
from the specification's own size formulas and its `(m, n, t)` triples, matching
**10/10**, and that control was **independently re-run at 10/10** by
`TASK-20260803-409c5e` (`EV-MCE-332f99` O-1 `controls`). This cross-validates
this table and [[KN-LIT-48b4eb]] Section 7 simultaneously. **The private-key
column has no arithmetic bridge** and was verified by direct re-reading, not by
derivation.

## Relevance to this program
Supplies the concrete sizes for any cost or deployment statement about Classic
McEliece at the specification's parameter sets. Companion to [[KN-LIT-48b4eb]]
(parameters) and [[KN-LIT-7b78de]] (categories and memory-charged estimates).

## Not verified here
**No implementation was built, run, or benchmarked.** Timing and performance
claims in the guide were not examined. Table 1 covers only the ten non-pc sets;
**no numeric sizes for pc variants appear in any document read** — see
[[KN-LIT-209151]], where pc ciphertext sizes are computed from formulas rather
than transcribed. No local copy is committed.
```

---

## 7. Entry D — the plaintext-confirmation variant (`KN-LIT-209151`)

```markdown
---
id: KN-LIT-209151
type: literature
title: "Classic McEliece: conservative code-based cryptography: what plaintext confirmation means"
authors: []
authors_note: No author list on the title page; issued by the Classic McEliece team.
year: 2022
venue: "Classic McEliece round-4 NIST PQC submission, document dated 23 October 2022"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: "https://classic.mceliece.org/mceliece-pc-20221023.pdf"
source_artifact:
  url: "https://classic.mceliece.org/mceliece-pc-20221023.pdf"
  sha256: "9894108c16c2d38de2bac9a9d9f228fe25602acfe9214aba279669f353d2ed99"
  retrieved_by: TASK-20260803-f3aece
  committed_locally: false
tags: [code-based, mceliece, plaintext-confirmation, kem, fujisaki-okamoto, iso, primary-source]
confidence: reported
citation_verified: read
citation_verified_note: >-
  `read` is earned by TASK-20260803-f3aece, which fetched this one-page PDF on
  2026-08-03 (HTTP 200; URL, byte count and sha256 in that task's
  source_access_log.yaml). Validator TASK-20260803-409c5e re-fetched it and
  confirmed the substance of every quoted passage, noting under its finding Q2
  that the producer had silently glyph-normalised the ciphertext sentence
  inside a block labelled verbatim (no number affected). The agent that drafted
  this entry (TASK-20260803-a53f73) did NOT read the document. No local copy is
  committed.
added: "2026-08-03"
superseded_by: null
---

## Contribution
One-page document defining the "pc" (plaintext confirmation) variants as a list
of changes to the cryptosystem specification. States that it *"defines exactly
the same KEM as the round-3 Classic McEliece submission"*.

## Key claims (as reported)
- Encap gains a step `C1 = H(2,e)` and sets `C = (C0,C1)`; Decap gains a
  re-computation and comparison of `C1`, falling back to the private random
  string `s` and `b ← 0` on mismatch.
- Ciphertexts become the concatenation of a `⌈mt/8⌉`-byte `C0` and a
  `⌈l/8⌉`-byte `C1`; with `l = 256` from the specification, **pc ciphertexts are
  32 bytes longer** than non-pc ciphertexts.
  *(Transcription note: the two-component ciphertext sentence extracts from the
  PDF with dislocated superscripts and `(cid:96)` glyphs. The reading above is a
  normalisation, confirmed by the validator against the document's own Decap
  step. The normalisation is disclosed here rather than presented as verbatim.)*
- **The document introduces NO new `(m, n, t)` values.** The pc parameter sets
  share the parameters, and therefore the code rate `k/n`, of their base sets.

## Relevance to this program
Load-bearing for `GOAL-MCE-001`'s scoping. The ISO standard's parameter list
includes pc and pcf sets that do not appear in [[KN-LIT-48b4eb]] Section 7, so
without this document the standardized set list cannot be mapped onto transcribed
parameters. **Because pc changes no code parameter, the rate table for Classic
McEliece applies unchanged to the pc variants** (`EV-MCE-332f99` O-8).

The same observation carries a scoping consequence that any later deliverable
must respect: the ISO list contains **16** sets and **no `mceliece348864`
variant** — the set carrying the lowest claimed category. *"The standardized
parameter sets"* is therefore not interchangeable with *"the specification's five
sets"*, and a deliverable using either phrase must say which it means.

## Not verified here
**The security argument for plaintext confirmation was not evaluated.** The
separate "advantages and disadvantages" statement
(`nist/mceliece-mods3-20221023.pdf`) was **NOT fetched**. **No pc numeric size
table exists in anything read**; pc ciphertext sizes stated in this program's
task artifacts are computed from formulas, not transcribed. The ISO parameter
list itself is known only from the designers' own `iso.html` page — `iso.org`
returned 403 twice and the ISO designation number was never obtained
(`EV-MCE-332f99` O-7). No local copy is committed.
```

---

## 8. Entry E — NIST IR 8545 (`KN-LIT-9a7860`)

```markdown
---
id: KN-LIT-9a7860
type: literature
title: "NIST IR 8545: Status Report on the Fourth Round of the NIST Post-Quantum Cryptography Standardization Process"
authors:
  - "Gorjan Alagic"
  - "Maxime Bros"
  - "Pierre Ciadoux"
  - "David Cooper"
  - "Quynh Dang"
  - "Thinh Dang"
  - "John Kelsey"
  - "Jacob Lichtinger"
  - "Yi-Kai Liu"
  - "Carl Miller"
  - "Dustin Moody"
  - "Rene Peralta"
  - "Ray Perlner"
  - "Angela Robinson"
  - "Hamilton Silberg"
  - "Daniel Smith-Tone"
  - "Noah Waller"
year: 2025
venue: "NIST Internal Report, March 2025"
identifiers:
  eprint: null
  doi: "10.6028/NIST.IR.8545"
  arxiv: null
  url: "https://nvlpubs.nist.gov/nistpubs/ir/2025/NIST.IR.8545.pdf"
source_artifact:
  url: "https://nvlpubs.nist.gov/nistpubs/ir/2025/NIST.IR.8545.pdf"
  sha256: "d802f4849a52d18001533cef86e0950f31350643cc06881ee62b2382e1ea0e9d"
  retrieved_by: TASK-20260803-f3aece
  committed_locally: false
tags: [pqc, standardization, nist, mceliece, bike, hqc, sike, code-based, primary-source]
confidence: reported
citation_verified: read
citation_verified_note: >-
  `read` is earned by TASK-20260803-f3aece, which fetched this PDF on
  2026-08-03 (HTTP 200; URL, byte count and sha256 in that task's
  source_access_log.yaml) after csrc.nist.gov and nvlpubs.nist.gov proved
  REACHABLE, contrary to the expectation recorded in RQ-HQC-001.provenance.
  Validator TASK-20260803-409c5e re-acquired it and reproduced the quoted
  passage exactly, in full. The agent that drafted this entry
  (TASK-20260803-a53f73) did NOT read the document. Author list transcribed
  from the title page, not from recall. No local copy is committed.
added: "2026-08-03"
superseded_by: null
---

## Contribution
NIST's own status report closing the fourth round of the PQC standardization
process. The authoritative primary statement of Classic McEliece's standing in
the NIST process.

## Key claims (as reported)
- *"Classic McEliece is no longer under consideration for standardization as part
  of the current NIST PQC Standardization Process."*
- **The stated reasons are explicitly NOT security-based:** *"the interest
  expressed in Classic McEliece was limited, and having more standards to
  implement adds complexity to protocols and PQC migration"*, plus *"Concurrent
  standardization of Classic McEliece by NIST and ISO risks the creation of
  incompatible standards."*
- *"After the ISO standardization process has been completed, NIST may consider
  developing a standard for Classic McEliece based on the ISO standard."*
- As of March 2025 the report describes Classic McEliece as *"currently under
  consideration for standardization by the International Organization for
  Standardization (ISO)"*.
- The report also records that SIKE was broken early in the fourth round and
  removed from consideration.

## Relevance to this program
Settles the `standardization_status` that `GOAL-MCE-001` and `RQ-MCE-e65b3c` both
marked UNVERIFIED, and does so from the deciding body's own text rather than from
an inference about a project website's menu structure.

**Scoping consequence, and it cuts both ways.** NIST's non-selection carries **no
security implication in this document**, so it must not be cited as evidence for
or against the scheme's strength. Equally, this document does not confirm the ISO
completion the designers' site claims for June 2026 — it **predates** it and
describes ISO consideration as ongoing.

## Not verified here
Only the Classic McEliece passage and the title page were read closely; the
report's BIKE, HQC and SIKE analyses were **not**. **Whether NIST has acted
further since March 2025 was NOT established** — no later NIST document was
fetched. The ISO standardization claimed for June 2026 **postdates this report**
and rests on the designers' own site alone, with `iso.org` returning 403 twice
and the designation number not obtained (`EV-MCE-332f99` O-7). No local copy is
committed.
```

---

## 9. Filing checklist for `TASK-20260803-3aa684`

1. **Re-verify all five IDs are still free** with `python3 tools/allocate_id.py
   --check <ID>`. All five were confirmed free at HEAD `2ea6216d`; another
   worktree may have consumed one since.
2. **Check every `retrieved_by` reads `TASK-20260803-f3aece`** — the two BATCH-001
   producers' retrieval sets are disjoint (§4 attribution note).
3. **Do NOT add `## Local copies` sections.** No PDF is committed; the sha256 in
   `source_artifact` is the integrity anchor.
4. **Decide the `source_artifact:` schema question** (§3.1) before filing all
   eight new entries in this package consistently. The one thing that must not
   happen is `sha256` under `identifiers`.
5. **Reconcile cross-references** (§3.2) against which supersessions the reviews
   actually accepted. A reference to a rejected supersession's new ID would point
   at a file that does not exist.
6. **Regenerate `knowledge/INDEX.md`, `knowledge/SOURCES.md` and
   `knowledge/sources.json`** (`make sources`) after filing. They are derived;
   never hand-edit them.
7. Entries A–D are one document family; A is the anchor and they cross-reference
   each other.
8. Consider whether `KN-LIT-141bac` (McEliece 1978, `citation_verified: false`)
   should gain a cross-reference to A. **Not decided here.**

## 10. Not proposed, and why — carried forward from BATCH-001 unchanged

These calls were made by `TASK-20260803-f3aece` and are **not** re-litigated by
this task; they are reproduced so they stay visible rather than dropping out of
the record when the entries are filed without them.

| Document | Fetched? | Why no entry |
|---|---|---|
| `nist/mceliece-submission-20221023.pdf` (round-4 overview) | Yes, 200, 115,971 B | 5-page cover document; substantive sections are all pointers to the four above. Recorded in the access log so a curator can reverse this cheaply. |
| `classic.mceliece.org/iso.html`, `nist.html`, `spec.html`, `comparison.html` | Yes, all 200 | Web pages, not literature. Quoted with page-version strings and sha256 in `standardization_status.md`. If the ISO event should be durable corpus state, the home is a `KN-FIND` or ledger record — and `knowledge/SEEDING.md` forbids a literature entry becoming a finding. **Still flagged for the Coordinator; still not decided.** |
| `mceliece-rationale-20221023.pdf` (design rationale) | **No** | Not fetched. The submission's designated source for "Design rationale" and "Advantages and limitations", plainly relevant. **Recommended as a cheap, high-value acquisition.** |
| `mceliece-610-20260623.pdf`, `mceliece-529-20250417.pdf` (designers' notes on 2^610 key-recovery and 2^529 distinguisher claims) | **No** | Not fetched; discovered on `nist.html`. **The designers' direct responses to recent attack claims against `mceliece348864` — highly relevant to `RQ-MCE-e65b3c`'s primary target.** Flagged prominently rather than quietly skipped. This package asserts nothing about their content. |
| `KN-TECH` entry on ISD | **No** | A technique entry must state applicability conditions and known limits. `DEC-20260803-a5b9b1` D-2 is a live demonstration that this program does not yet know them here. Unchanged. |

---

## 11. Scope firewall

**No entry in this package asserts anything about Classic McEliece's security in
either direction.** Every security-adjacent sentence above is either a quoted,
attributed statement by the submitters or by NIST, or a self-imposed prohibition.
No cost is computed, no convention is adopted, no distance to any attack regime
is derived, and `iacr:2026/1232` is neither cited as read nor characterised
beyond what `EV-MCE-332f99` already records.
