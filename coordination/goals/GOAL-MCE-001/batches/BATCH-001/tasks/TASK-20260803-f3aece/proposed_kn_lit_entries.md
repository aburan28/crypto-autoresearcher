# PROPOSED KN-LIT entries — TASK-20260803-f3aece

**Task:** TASK-20260803-f3aece · **Goal:** GOAL-MCE-001 · **Batch:** BATCH-001
**Date:** 2026-08-03
**Role:** executor · `requested_policy: executor-implementation` ·
`resolved_model_id: claude-opus-5` · `fallback_used: true`

> **PROPOSED ONLY. NOTHING WAS WRITTEN INTO `knowledge/`.** Named duty 5. These
> are drafts for the Coordinator (or a `/curate-knowledge` task) to accept,
> amend, or reject. The IDs below are *candidates* verified free at the time of
> writing; whoever files must re-check for collisions, since another worktree
> may have consumed them.

---

## 1. Dedup determination — done FIRST, per named duty 4

The task card warns: 169 KN-LIT entries mention McEliece, BATCH-001-OPENING
reports zero KN-TECH entries on ISD but **does not** claim the specification is
absent, and *"a broad unread corpus is precisely the condition under which a
novelty or dedup check returns a confident wrong answer."* So the check below
is by grep against the corpus, not by recollection.

**Corpus census reproduced.** `grep -rli "mceliece" knowledge/literature/ | wc -l`
→ **169**. This confirms BATCH-001-OPENING section 2's count exactly.

**Queries run against `knowledge/`:**

| Probe | Hits | Determination |
|---|---:|---|
| `mceliece-spec` | 0 | Specification not held |
| `cryptosystem specification` | 0 | " |
| `conservative code-based cryptography` (the document family's actual title stem) | 0 in `knowledge/`; 1 in `ledger/questions/RQ-MCE-e65b3c.yaml` (prose, not a citation) | Not held |
| `guide for implementors` | 0 | Not held |
| `guide for security reviewers` | 0 | Not held |
| `plaintext confirmation` | 0 | Not held |
| `mceliece348864\|460896\|6688128\|6960119\|8192128` (parameter-set names) | 1 file: `KN-LIT-6614` | See below — **not** a duplicate |
| `8545` | 2 files, **both false positives** | IR 8545 not held |
| `NIST IR` / `Status Report on the … Round` | 1 file: `KN-LIT-7620` | Near-neighbour, **not** a duplicate |
| `classic.mceliece.org` | 20+ files, all the same GATHER-20260803 provenance footer citing `papers.html` | No entry cites the spec/nist/iso pages |

**The two near-misses, examined rather than waved through:**

- **`KN-LIT-6614`** — Lahr, Niederhagen, Petri, Samardjiska, *"Side Channel
  Information Set Decoding using Iterative Chunking …"*. It is the only corpus
  entry containing a Classic McEliece parameter-set name, and it contains it
  only incidentally: *"for the 256-bit security parameter set kem/mceliece6960119"*
  inside a relayed abstract. It is a third-party side-channel paper, not the
  specification, and it transcribes no parameter table. **Not a duplicate.**
  (Note for the record: this entry carries `citation_verified: read` against a
  `downloads/` path — exactly the provenance class KN-OPEN-3f7a21 flags as
  unconfirmed. Not relied on here for anything.)
- **`KN-LIT-7620`** — *"NIST IR 8610: Status Report on the Second Round of the
  Additional Digital Signature Schemes …"*. Same NIST author group, same
  document series, **different report**: IR 8610 covers additional signatures,
  IR 8545 covers the fourth-round KEMs and is the one that states Classic
  McEliece's status. **Not a duplicate**, but it is a useful precedent for
  entry formatting and shows the corpus already holds one document of this
  series.
- The `8545` hits were `KN-LIT-4537` (matched the phrase "fourth round" inside a
  Keccak abstract; `grep -c "8545"` → 0) and `KN-LIT-1908` (matched the arXiv
  identifier `2603.08545`). Both checked individually. Neither is IR 8545.

**Determination: the Classic McEliece primary specification is NOT held by this
corpus, nor is any document of its round-4 family, nor NIST IR 8545.** All five
entries below are new. This is a positive check, not an assumption.

**Scope limit on that determination, stated plainly:** the probes above are
string matches over `knowledge/`. They would miss an entry that holds one of
these documents under a wholly different title with no matching identifier,
URL, or phrase. I judge that unlikely given the number and variety of probes,
but the check is a grep, not a proof.

---

## 2. Provenance axes applied

Per `knowledge/SEEDING.md`. All five documents below were **actually fetched and
read** in this task, with byte counts and sha256 in `source_access_log.yaml`.
So each is proposed as:

- `citation_verified: read` — genuinely earned here, not inherited. The claims
  in these entries reflect text I read, not search snippets. This deliberately
  contrasts with the 137 GATHER-20260803 entries, which correctly use `web`
  or `false`.
- `confidence: reported` for security claims (the categories are the
  submission's own assertions, relayed); `established` is **not** used anywhere.
  Parameter values are definitional rather than claims — they are what the
  specification *defines* — but the entries still say where each came from.

**Local copies:** none of these PDFs is committed, per the task constraint on
third-party copyrighted material. The entries therefore record URL + sha256 and
**no** `## Local copies` section. Filing them with a `downloads/` path would
re-create precisely the defect KN-OPEN-3f7a21 documents.

---

## 3. Proposed entry A — the primary specification

```markdown
---
id: KN-LIT-48b4eb
type: literature
title: "Classic McEliece: conservative code-based cryptography: cryptosystem specification"
authors: []
authors_note: >-
  The document's title page carries no author list; it is issued by the Classic
  McEliece team. Authors NOT filled in from recall. The team roster is at
  https://classic.mceliece.org/people.html, which this task did not fetch.
year: 2022
venue: "Classic McEliece round-4 NIST PQC submission, document dated 23 October 2022"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: "https://classic.mceliece.org/mceliece-spec-20221023.pdf"
  sha256: "dcc6878852ef8a00a7bedd859da661770cf85d2c3d9239e06d25e4a0d365fd12"
tags: [code-based, mceliece, goppa, niederreiter, specification, parameters, kem, primary-source]
confidence: reported
citation_verified: read
added: "2026-08-03"
superseded_by: null
---

## Contribution
The official definition of Classic McEliece, so designated by the project's own
Specification page ("The official definition of Classic McEliece is the
cryptosystem specification"). 16 pages. Defines the KEM over binary Goppa codes
in Niederreiter form: parameters, matrix reduction and generation, encoding and
decoding subroutines, key generation, fixed-weight-vector generation,
encapsulation, decapsulation, byte-string representations, and ten selected
parameter sets.

## Key claims (as reported)
- Parameters are (m, n, t) with q = 2^m, n <= q, t >= 2 and mt < n; the
  specification defines k = n - mt (Section 3). Definitional, not a claim.
- Ten selected parameter sets (Section 7), five (m, n, t) triples each in a
  plain and an "f" (semi-systematic, (mu, nu) = (32, 64)) variant:
  (12, 3488, 64), (13, 4608, 96), (13, 6688, 128), (13, 6960, 119),
  (13, 8192, 128).
- Resulting code rates k/n, computed from the specification's own definition:
  85/109 ~ 0.7798, 35/48 ~ 0.7292, 157/209 ~ 0.7512, 5413/6960 ~ 0.7777,
  51/64 ~ 0.7969. All five standardized-family rates lie in [0.729, 0.797].
- Symmetric parameters (Section 6.1): l = 256, H = first 256 bits of SHAKE256,
  sigma_1 = 16, sigma_2 = 32.
- Size formulas (Section 6.2): public key is mt*ceil(k/8) bytes; ciphertext is
  ceil(mt/8) bytes.
- The document makes NO security-category claim and states NO numeric byte
  sizes; it delegates both (see KN-LIT-7b78de and KN-LIT-b7f8f8).

## Relevance to this program
Primary source for RQ-MCE-e65b3c and GOAL-MCE-001. Supplies the rate k/n that
every rate-threshold claim in the alternant/Goppa distinguisher line
(KN-LIT-4c8135, KN-LIT-13a01d, KN-LIT-71d1a0, KN-LIT-7ee1a9) must be compared
against, and the exact (n, k, t) at which any memory-charged ISD baseline for
this goal must be computed. Forecloses nothing on the attack side.

## Not verified here
Only Sections 3, 6 and 7 were read closely; the algorithm definitions in
Sections 4 and 5 were not audited. No claim in this entry has been
independently reproduced beyond the arithmetic cross-check recorded in
TASK-20260803-f3aece/parameter_sets.md section 5. No implementation was run
and no KAT was checked.
```

---

## 4. Proposed entry B — guide for security reviewers

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
  sha256: "db17ef0879cb8822120c312b7290f7db82fe9fc356bd16058ad334a512b523fa"
tags: [code-based, mceliece, isd, security-categories, memory-cost, structural-attacks, primary-source]
confidence: reported
citation_verified: read
added: "2026-08-03"
superseded_by: null
---

## Contribution
36-page security discussion accompanying the round-4 submission. The round-4
submission overview delegates "Expected strength (2.B.4) for each parameter
set" and "Analysis of known attacks (2.B.5)" to this document, making it the
submission's designated source for security-category claims.

## Key claims (as reported)
- The submission assigns its selected parameter sets to categories
  "1, 3, 5, 5, 5 respectively" (i.e. 348864 -> 1, 460896 -> 3, 6688128 -> 5,
  6960119 -> 5, 8192128 -> 5), stating these are "based on counting realistic
  costs for memory".
- The same document states that under free-memory bit-operation accounting
  "the correct assignments will instead be 1, 2, 4, 4, 5", and frames the two
  as two cost models rather than a revision.
- Table 1 reports Esser-Bellini estimator output for all five sets under three
  memory models (mem = 0, 1/3, 1/2). Lowest tabulated entry is 140.8 for
  mceliece348864 at mem = 0.
- The document argues the estimator's numbers are underestimates of bit
  operations because it "counts each vector operation as just 1 operation",
  and that the 140.8 figure corresponds to an attack using memory 2^86.6.
- These are the SUBMITTERS' assessments of their own scheme. This entry relays
  them and does not endorse them.

## Relevance to this program
Directly bears on GOAL-MCE-001's second completion criterion: it is a
primary-source statement of how the designers charge memory, and its Table 1 is
a published estimator output at exactly the parameters the goal must cost. Any
memory-charged ISD baseline this program builds should be compared against it
rather than derived in ignorance of it. Does NOT settle the charging
convention, which GOAL-HQC-001 TASK-20260802-0100a5 owns.

## Not verified here
Table 1's numbers were read but NOT reproduced, and no estimator was run. The
document's arguments about memory-access cost were not evaluated. The
categories are relayed as the submission's assertions; this program takes no
position on whether any parameter set meets any category.
```

---

## 5. Proposed entry C — guide for implementors

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
  sha256: "86225992a73a2dc986b2ef5edfcfa3e28d49684fffd8be281237e1e5af2757a3"
tags: [code-based, mceliece, key-sizes, implementation, constant-time, primary-source]
confidence: reported
citation_verified: read
added: "2026-08-03"
superseded_by: null
---

## Contribution
19-page implementors' guide; the submission overview delegates "Detailed
performance analysis (2.B.2)" to it. Its Table 1 is the primary source for the
numeric key, ciphertext and session-key sizes of all ten selected parameter
sets.

## Key claims (as reported)
- Table 1 (sizes in bytes; public key / private key / ciphertext / session key):
  mceliece348864 and 348864f: 261120 / 6492 / 96 / 32;
  460896 and 460896f: 524160 / 13608 / 156 / 32;
  6688128 and 6688128f: 1044992 / 13932 / 208 / 32;
  6960119 and 6960119f: 1047319 / 13948 / 194 / 32;
  8192128 and 8192128f: 1357824 / 14120 / 208 / 32.
- The private key "can be compressed down to 40 bytes (or 32 bytes for non-f
  parameter sets) with uncompression less expensive than key generation", so
  the tabulated private-key column is the uncompressed form.
- The guide characterises the trade-off as large public keys with small
  ciphertexts, and notes use in PQ-WireGuard.

## Relevance to this program
Supplies the concrete sizes for any cost or deployment statement about Classic
McEliece at standardized parameters. Every public-key and ciphertext figure in
Table 1 was independently re-derived in TASK-20260803-f3aece from the
specification's formulas and the (m, n, t) triples, matching 10/10 - which
cross-validates this table and the specification's Section 7 simultaneously.

## Not verified here
No implementation was built, run, or benchmarked. Timing and performance claims
in the guide were not examined. Table 1 covers only the ten non-pc sets; no
numeric sizes for pc variants appear in any document read.
```

---

## 6. Proposed entry D — the plaintext-confirmation variant

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
  sha256: "9894108c16c2d38de2bac9a9d9f228fe25602acfe9214aba279669f353d2ed99"
tags: [code-based, mceliece, plaintext-confirmation, kem, fujisaki-okamoto, primary-source]
confidence: reported
citation_verified: read
added: "2026-08-03"
superseded_by: null
---

## Contribution
One-page document defining the "pc" (plaintext confirmation) variants as a
list of changes to the cryptosystem specification. States that it "defines
exactly the same KEM as the round-3 Classic McEliece submission".

## Key claims (as reported)
- Encap gains a step C1 = H(2,e) and sets C = (C0,C1); Decap gains a
  re-computation and comparison of C1, falling back to the private random
  string s and b <- 0 on mismatch.
- Ciphertexts become the concatenation of a ceil(mt/8)-byte C0 and a
  ceil(l/8)-byte C1; with l = 256 from the specification, pc ciphertexts are
  32 bytes longer than non-pc ciphertexts.
- The document introduces NO new (m, n, t) values. The pc parameter sets share
  the parameters, and therefore the code rate k/n, of their base sets.

## Relevance to this program
Load-bearing for GOAL-MCE-001's scoping: the ISO standard's parameter list
includes pc and pcf sets that do not appear in the specification's Section 7,
so without this document the standardized set list cannot be mapped onto
transcribed parameters. Because pc changes no code parameter, the rate table
for Classic McEliece applies unchanged to the pc variants.

## Not verified here
The security argument for plaintext confirmation was not evaluated; the
separate "advantages and disadvantages" statement
(nist/mceliece-mods3-20221023.pdf) was NOT fetched. No pc numeric size table
exists in anything read; pc ciphertext sizes stated in this program's task
artifacts are computed from formulas, not transcribed.
```

---

## 7. Proposed entry E — NIST IR 8545

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
  sha256: "d802f4849a52d18001533cef86e0950f31350643cc06881ee62b2382e1ea0e9d"
tags: [pqc, standardization, nist, mceliece, bike, hqc, sike, code-based, primary-source]
confidence: reported
citation_verified: read
added: "2026-08-03"
superseded_by: null
---

## Contribution
NIST's own status report closing the fourth round of the PQC standardization
process. It is the authoritative primary statement of Classic McEliece's
standing in the NIST process. Author list transcribed from the title page.

## Key claims (as reported)
- "Classic McEliece is no longer under consideration for standardization as
  part of the current NIST PQC Standardization Process."
- The stated reasons are NOT security-based: "the interest expressed in Classic
  McEliece was limited, and having more standards to implement adds complexity
  to protocols and PQC migration", plus "Concurrent standardization of Classic
  McEliece by NIST and ISO risks the creation of incompatible standards."
- "After the ISO standardization process has been completed, NIST may consider
  developing a standard for Classic McEliece based on the ISO standard."
- As of March 2025 the report describes Classic McEliece as "currently under
  consideration for standardization by the International Organization for
  Standardization (ISO)".
- The report also records that SIKE was broken early in the fourth round and
  removed from consideration.

## Relevance to this program
Settles the standardization_status field that GOAL-MCE-001 and RQ-MCE-e65b3c
both marked UNVERIFIED, and does so from the deciding body's own text rather
than from an inference about a project website's menu structure. Important
scoping consequence: NIST's non-selection carries NO security implication in
this document, so it must not be cited as evidence for or against the scheme's
strength.

## Not verified here
Only the Classic McEliece passage and the title page were read closely; the
report's BIKE, HQC and SIKE analyses were not. Whether NIST has acted further
since March 2025 was NOT established - no later NIST document was fetched, and
the ISO completion claimed for June 2026 postdates this report.
```

---

## 8. Not proposed, with reasons

Honesty about what was deliberately left out.

| Document | Fetched? | Why no entry proposed |
|---|---|---|
| `nist/mceliece-submission-20221023.pdf` (round-4 submission overview) | Yes, 200, 115,971 B, sha `cbcbcd49…` | Read in full; it is a 5-page cover document whose substantive sections are all pointers to the four documents above. An entry would carry no claim the others do not. Recorded in the access log so a curator can reverse this call cheaply. |
| `classic.mceliece.org/iso.html`, `nist.html`, `spec.html`, `comparison.html` | Yes, all 200 | Web pages, not literature. Their content is transcribed and quoted in `standardization_status.md` with page-version strings and sha256. If the ISO standardization event should be a durable corpus fact, the right home is a `KN-FIND` or a goal/ledger record, not a `KN-LIT` — and per `knowledge/SEEDING.md` a literature entry never becomes a finding. Flagged for the Coordinator; not decided here. |
| `mceliece-rationale-20221023.pdf` (design rationale) | **No** | Not fetched. It is the submission's designated source for "Design rationale" and "Advantages and limitations", and is plainly relevant to this goal — but it was outside this task's transcription objective and proposing an entry for an unfetched document would violate the constraint this task exists to honour. **Recommended as a cheap, high-value acquisition for a follow-up task.** |
| `mceliece-610-20260623.pdf`, `mceliece-529-20250417.pdf` (team notes responding to 2^610 key-recovery and 2^529 distinguisher claims) | **No** | Not fetched; discovered on nist.html. These are the designers' direct responses to recent attack claims against mceliece348864 and are **highly** relevant to GOAL-MCE-001's primary target and to TASK-20260803-292b99's subject matter. Flagged prominently rather than quietly skipped: a future task should fetch them. This task asserts nothing about their content. |
| KN-TECH entry on ISD | **No** | BATCH-001-OPENING section 2 explicitly declines to patch this gap in this batch, on the grounds that a technique entry must state applicability conditions and known limits and nothing has been read yet. That reasoning is unchanged by this task, which read no ISD paper. |

---

## 9. Filing checklist for whoever accepts these

1. Re-verify all five candidate IDs are still free (`ls knowledge/literature/`);
   they were free at 2026-08-03 against 7807 existing entries but another
   worktree may have consumed them.
2. Do **not** add `## Local copies` sections. No PDF is committed; the sha256 in
   `identifiers` is the integrity anchor.
3. Regenerate `knowledge/INDEX.md` per `knowledge/SEEDING.md` step 6.
4. Cross-reference: entries A–D are one document family and should reference
   each other; A is the anchor.
5. Consider whether `KN-LIT-141bac` (McEliece 1978, currently
   `citation_verified: false`) should gain a cross-reference to A.
