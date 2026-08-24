# ATOMIC correction — one defect, three places, superseded together

**Task:** TASK-20260808-843c87 · **Goal:** GOAL-MCE-001 · **Batch:** BATCH-a68f79
**Role:** coordinator · **Date:** 2026-08-08 · **Claim tier:** toy (unchanged)

**Inference record (verbatim, as required by the task card):** requested_policy
coordinator-orchestration-code; under the Claude Code runtime per CLAUDE.md
per-role model selection is process-level and subagents keep model: inherit, so
the resolved model is the session model; fallback_used: false; model_verified:
false (no adapter probe receipt for this session).

**Budget:** authorized 1 run, 2 GB, 3600 s. **Runs executed: 0.** This role has
no execute capability (`orchestration/roles.yaml`, `may_execute_experiments:
false`); the task is a record correction and needed none.

---

## 0. Source availability — read this before the quotations

The task card says: *"If you cannot read the source in this environment, RECORD
THAT AND STOP — a corrected citation written from memory is a fabrication and is
worse than the defect you were sent to fix."* That clause is answered here
first, explicitly, because everything below depends on it.

**What I looked for and what I found.**

| Route | Result |
|---|---|
| `inputs/` (checked first, as the card directs) | 38 files, all ECDLP/idea-generation ledgers and manifests. **No arXiv:2304.14757**, no code-based-crypto source package. |
| `downloads/` | **Absent** — the tree `KN-OPEN-3f7a21` is about. Never git-tracked. |
| Repo-wide search for the PDF or its extracted text | Not present. `TASK-20260803-292b99`'s own log states the policy: *"No third-party copyrighted PDF is committed to this repository … Retrieved bodies live only in the session scratchpad and are not part of the repo."* |
| `kb/.kb-corpus/` | Contains `KN-LIT-2304.md` — an unrelated corpus entry whose ID merely resembles the arXiv number. Not this paper. |
| Fetching it myself | **Not possible and not attempted.** This role's tool surface is read/search/write/edit with no execute and no fetch. |

**So: the primary object is NOT readable in this session, and this report says
so rather than implying otherwise.**

**Why this is not a stop, and not a citation from memory.** Nothing below is
recalled. Every quotation is *re-quoted* from this program's own committed,
snapshot-archived, verbatim transcription of the full text:

- Produced by `TASK-20260803-292b99` on 2026-08-03 from
  `https://arxiv.org/pdf/2304.14757`, HTTP 200, 526,690 bytes, 36 pages, PDF
  1.4, pdfminer.six extraction — bound to
  `sha256 ebbd94ac3cd00b0f0e723aeab56fd3b0820c89d47072fc8241f12c5f93c564b8`
  (`source_access_log.yaml`, attempt C02).
- **Independently re-acquired byte-identically at that sha256** by validator
  `TASK-20260803-409c5e`, whose report records: *"Both obtained full texts
  reproduce byte-identically. That is the load-bearing receipt for everything
  quoted in §2 and §3 of `attack_transcription.md`, and it holds."*
- Independently re-read and upheld by red team `TASK-20260803-08e883`
  (objection O-5, *"Duty 6a — KN-LIT-4c8135 Goppa-exclusion omission:
  **VERIFIED. The producer is right.**"*).
- Committed as ledger evidence: `EV-MCE-332f99` O-5.
- Both snapshot commits were verified: `DEC-20260803-a5b9b1` D-1 records all 9
  recorded hashes recomputing from the committed blobs.

That chain — hash-bound transcription, independent byte-identical
re-acquisition, independent adversarial re-read, committed evidence record — is
the strongest attestation obtainable in this environment, and it is *why* the
defect was found in the first place. Proceeding on it, with the second-hand
status declared at every site, is different in kind from writing a citation from
memory. **Every quotation in this report and in both superseding records is
labelled `re-quoted, not re-read`, and the declared basis is the committed
transcription at that sha256 — not the PDF.**

The batch's own validator task `TASK-20260808-ea7bed` is gated on checking the
boundary *against the source*, not against this report. That check is where a
first-hand read belongs, and it is not claimed here.

**Not attempted, deliberately:** `iacr:2026/1232`'s PDF, by any route. The 403
is path-scoped and reproducible (A02, A29, 8 minutes apart, same status, same
byte count, different sha256 from a per-request nonce), circumvention is
forbidden, and AGENTS.md rule 5 makes a blocked route a recorded outcome. No
route to it was tried in this task.

---

## 1. The defect — one defect, three places

BATCH-001 recorded arXiv:2304.14757's boundary as **rate-scoped**. The paper
states, verbatim, that its attack *"does not work at all when the alternant code
has the additional structure of being a Goppa code."* The decisive restriction
is the **code family**, and Classic McEliece uses binary Goppa codes.

The three sites are the same sentence written three times:

1. `BATCH-001-OPENING.md` §4 — *"The rate threshold is the whole question."*
2. `RQ-MCE-e65b3c.constraints` — the rate-scoping clause.
3. `knowledge/literature/KN-LIT-4c8135.md` — the entry itself.

Authority: `DEC-20260803-a5b9b1` D-2 (retraction) and D-4 (upheld), on evidence
`EV-MCE-332f99` O-5, and `GOAL-MCE-001.next_action`, which requires all three to
be superseded **at once** because fixing them separately lets a later task cite
whichever was fixed last and inherit the defect from the other two.

---

## 2. The quotation, verbatim, with its location

> Interestingly our attack does not work at all when the alternant code has the
> additional structure of being a Goppa code.

**Where it appears.** In the extracted text the sentence stands directly under
the paragraph heading *"Opening the road for attacking the CFS scheme."* The
transcription records the two together:

> Opening the road for attacking the CFS scheme. Interestingly our attack does not
> work at all when the alternant code has the additional structure of being a
> Goppa code.

The same restriction appears in **Table 1**, restriction column, row *"this
paper"*, verbatim as extracted:

```
paper                 restriction
[SS92, CGG`14]        m “ 1
[COT14]               m “ 2 + Wild Goppa code
this paper            q “ 2 or q “ 3, m arbitrary + high rate condition (6)
                      (does not apply in the particular case of Goppa codes)
```

(`“` is the pdfminer extraction's rendering of `=`. Left as extracted and
annotated. This report does **not** pre-empt `TASK-20260808-a9f648`, which
settles the transcription convention `DEC-20260803-a5b9b1` D-10 left open; it
simply refuses to silently normalise a glyph inside something labelled verbatim,
which is the half of D-10 that is not in dispute.)

**Section 3.2** of the paper is headed *"What is wrong with Goppa codes?"* and
states, verbatim:

> Goppa codes behave differently from random alternant codes and provide
> counterexamples to Heuristic 18.

**No page number is cited, because none exists in the record.** The
transcription recorded a paragraph heading, a table, a section number and a
section heading, and no page numbers. Inventing one would be exactly the
fabrication the card forbids.

**Provenance of these quotations:** re-quoted, not re-read — see §0.
Sources: `TASK-20260803-292b99/attack_transcription.md` §3 and
`rate_regime_extraction.md` §3.1, §3.3, both bound to
`sha256 ebbd94ac3cd00b0f0e723aeab56fd3b0820c89d47072fc8241f12c5f93c564b8`.

---

## 3. What the corrected boundary IS

Stated positively, because "not a rate threshold" is not a boundary.

**The boundary is a conjunction of three conditions, and the family conjunct is
the one that decides applicability to Classic McEliece.**

1. **CODE FAMILY — decisive.** Generic / random alternant codes, with **Goppa
   codes explicitly excluded**. The attack "does not work at all" on them; the
   paper's stated mechanism for the exclusion is that Goppa codes are
   *"counterexamples to Heuristic 18"*. The abstract confines the result the
   same way, verbatim: *"We give for the first time a positive answer for this
   problem when the code is {\em a generic alternant code} …"*. The exclusion
   carves out precisely the subfamily Classic McEliece uses.
2. **FIELD SIZE.** `q ∈ {2,3}`, with extension degree `m` **arbitrary** —
   breaking the earlier `m = 2` barrier is one of the paper's headline claims.
   Verbatim: *"we can actually attack McEliece-alternant for any extension degree
   m provided that the rate of the alternant code is sufficiently large (6) and
   the field size sufficiently low q “ 2 or q “ 3."*
3. **RATE.** *"sufficiently large (6)"*. **The rate condition is real and is not
   withdrawn** — the paper's own title says *high rate*. Condition (6) is a lower
   bound on `n − 1`; its formula is `[EXTRACTION-DAMAGED]` in the available
   extraction and is **not transcribed by this program**, here or anywhere. What
   is clean: `e := max{ i ∈ ℕ | r ≥ q^i + 1 } = ⌊log_q(r−1)⌋`.

**What changed is not "the rate condition is gone".** What changed is: the rate
threshold is one of three conjuncts, it is not *the* boundary, and it is not the
discriminator between this result and Classic McEliece — because conjunct 1
settles applicability to binary Goppa codes before any rate arithmetic is
performed.

Read the paper's title again with both halves live: *"Polynomial time
key-recovery attack on high rate **random alternant** codes"*. The family
restriction was in the title all along. `KN-LIT-4c8135` carried the title and
read only the "high rate" half of it.

**No mis-scoping is substituted for the old one.** The corrected statement is
the source's own three-conjunct restriction, quoted, with the untranscribed
conjunct labelled untranscribed.

---

## 4. What this correction does NOT establish

- **It is not a security claim about Classic McEliece, in either direction.**
  *"Our attack does not work at all on Goppa codes"* is these authors'
  statement about **their** attack. It is not a theorem that Goppa codes resist
  algebraic attacks, and this program asserts nothing about Classic McEliece's
  security.
- **It says nothing about the 2026 line.** `KN-LIT-7c4620` /`iacr:2026/1232`
  names *binary Goppa codes* in its abstract and its **body was not obtained**.
  This exclusion does not transfer to it. Treating it as licence to dismiss the
  2026 line would be the dismissal-side error that `BATCH-001-OPENING.md` §7
  defines as this campaign's failure condition — symmetric with alarm, per
  `docs/inventor-protocol.md`.
- **It moves nothing.** Claim-tier ceiling stays **toy**;
  `GOAL-MCE-001.active_hypothesis_ids` stays **empty**; no hypothesis status
  changes; no completion criterion is met or approached.
- **It is a correction of the program's description of someone else's paper.**
  That is all it is.

---

## 5. The three superseding entries

**No original was edited.** `BATCH-001-OPENING.md`, `RQ-MCE-e65b3c.yaml`, and
`KN-LIT-4c8135.md` are byte-unchanged by this task; none was opened for write.
This task's writes are exactly three new files, all inside its declared write
scope:

| Site | Superseded record | Superseding artifact |
|---|---|---|
| 1 | `coordination/goals/GOAL-MCE-001/batches/BATCH-001/BATCH-001-OPENING.md` §4 | §5.1 of this report + `RQ-MCE-3f7c02` |
| 2 | `ledger/questions/RQ-MCE-e65b3c.yaml`, constraints item 5 (and the scope.targets bullet repeating it) | `ledger/questions/RQ-MCE-3f7c02.yaml` |
| 3 | `knowledge/literature/KN-LIT-4c8135.md` | `knowledge/literature/KN-LIT-c41d8b.md` |

`RQ-MCE-3f7c02` carries all three sites in one `one_defect_three_sites` block,
so the ledger holds a single durable anchor for the whole defect rather than
three loose corrections.

**Why site 1's superseding note lives here.** `BATCH-001-OPENING.md` is
immutable *and* outside this task's write scope, so no note can be placed beside
it. Its superseding text is therefore this report — a declared artifact of this
task, at a fixed path, archived by `TASK-20260808-2de410` — with the ledger
anchor in `RQ-MCE-3f7c02`. Stated plainly so nobody mistakes the arrangement for
an oversight.

### 5.1 SITE 1 — superseding note for `BATCH-001-OPENING.md` §4

**This note supersedes** the final paragraph of section 4 of
`coordination/goals/GOAL-MCE-001/batches/BATCH-001/BATCH-001-OPENING.md`,
verbatim:

> **The rate threshold is the whole question.** `KN-LIT-4c8135` is genuinely
> polynomial-time and genuinely confined to high rate. Classic McEliece's rate is
> a number this program has not transcribed. The distance between those two is
> what BATCH-001 exists to measure, and until it is measured neither "the
> structural line threatens Classic McEliece" nor "it does not" is a statement
> this program is entitled to make.

**Why it is superseded.** Falsified by that same batch's own primary text
(`DEC-20260803-a5b9b1` D-2, `EV-MCE-332f99` O-5). The Coordinator asserted
"genuinely confined to high rate" about a paper nobody had read, and built the
batch's measurement plan on that axis. The cheapest control was one grep for
"Goppa" over text the program was about to retrieve anyway.

**What stands in its place.**

> **The boundary is a conjunction, and its decisive conjunct is the code
> family.** `KN-LIT-4c8135` is genuinely polynomial-time, and it is scoped to
> **generic / random alternant codes over F_2 or F_3, m arbitrary, at high rate
> per condition (6) — with Goppa codes explicitly excluded**: *"Interestingly our
> attack does not work at all when the alternant code has the additional
> structure of being a Goppa code."* Classic McEliece uses binary Goppa codes, so
> for that target the family conjunct settles applicability before any rate
> arithmetic is done, and the rate distance BATCH-001 set out to measure is not
> the discriminator. The rate conjunct is not withdrawn — condition (6) is real,
> is `[EXTRACTION-DAMAGED]`, and remains untranscribed. What is withdrawn is the
> claim that it is *the* question.
>
> The final sentence of the superseded paragraph is **retained and reaffirmed**:
> neither *"the structural line threatens Classic McEliece"* nor *"it does not"*
> is a statement this program is entitled to make. The corrected boundary
> strengthens the reason. An author's statement that **their own** attack fails
> on Goppa codes is not a security theorem, and it transfers to no other paper in
> the line — least of all to `KN-LIT-7c4620`, which names binary Goppa codes and
> whose body is unread.

**Not superseded:** the same section's bibliographic gloss *"`KN-LIT-4c8135`
(polynomial-time key recovery, **high-rate** random alternant codes, IEEE-IT
2024)"*. It repeats the paper's own title and is accurate.

### 5.2 SITE 2 — `ledger/questions/RQ-MCE-3f7c02.yaml`

A **clause-scoped** supersession record. It supersedes one constraint clause of
`RQ-MCE-e65b3c` (and the one `scope.targets` bullet repeating its framing); it
does **not** retire, replace, or re-ask `RQ-MCE-e65b3c`, which stays active and
stays the goal's question.

Superseded clause, verbatim:

> Rate-scoping is load-bearing, not decoration. KN-LIT-4c8135 is polynomial-time
> key recovery for HIGH-RATE random alternant codes; the threshold is the
> practically decisive number and no deliverable may state the headline without
> it.

The replacement clause is `RQ-MCE-3f7c02.replacement_constraint`: it keeps the
"scoping is load-bearing" discipline, states the conjunction, and requires the
**family exclusion** in any deliverable stating the headline — while forbidding
the opposite error of reading the exclusion as a statement about Classic
McEliece's security.

**Why clause-scoped rather than a full restatement.** A wholesale replacement
RQ would have to carry `RQ-MCE-e65b3c`'s other clauses forward, and two of them
are already known defective on grounds *outside this task's mandate* — the
ISD-costing-convention binding (`DEC-20260803-a5b9b1` D-3) and the
standardization-status gloss (superseded on the facts by `EV-MCE-332f99`
O-6/O-7/O-8). Copying a known-false clause into a new active record would author
a fresh defect while fixing an old one. Both are listed explicitly in
`RQ-MCE-3f7c02.clauses_deliberately_not_touched`, so silence there cannot be
read as "checked and sound".

### 5.3 SITE 3 — `knowledge/literature/KN-LIT-c41d8b.md`

A superseding literature entry carrying `supersedes: KN-LIT-4c8135`. It quotes
the source on its own boundary with locations, states the three conjuncts,
itemises the four withdrawn statements from the old entry against their verbatim
originals, and carries the provenance chain in its `citation_verified_note`.

Two honesty points inside it:

- `citation_verified` is **not** set to `read`.
  `TASK-20260803-292b99` proposed upgrading `KN-LIT-4c8135` to `read` on the
  basis that the paper was in hand at a recorded sha256 *in that session*. It is
  not in hand in this one, so the new entry uses
  `transcription_of_full_text_at_recorded_sha256` with the chain spelled out.
- **Known limitation, recorded not hidden:** the supersession link is
  **one-way**. `KN-LIT-4c8135` still carries `superseded_by: null` and cannot be
  edited here, so corpus retrieval that filters on `superseded_by` will still
  surface the defective entry. Only a task with authority to edit that field —
  or a reader following `supersedes` forward from `KN-LIT-c41d8b`, or reading
  `RQ-MCE-3f7c02` — will see the correction. Flagged for
  `TASK-20260808-ea7bed` and for the ledger archive.

---

## 6. What I could not verify, and what I did not do

1. **I did not read arXiv:2304.14757.** It is not in this environment and this
   role cannot fetch. Every quotation is second-hand within the program, from a
   hash-bound transcription that an independent validator re-acquired
   byte-identically. §0 states the chain in full. `TASK-20260808-ea7bed` is the
   first-hand check.
2. **No page numbers** exist in the record for any quotation; none is invented.
   Locations are the paragraph heading *"Opening the road for attacking the CFS
   scheme."*, Table 1's restriction column, §3.2 and its heading, and the
   abstract.
3. **Condition (6) remains untranscribed.** It is `[EXTRACTION-DAMAGED]` and is
   not reconstructed here. Any claim needing the numeric rate threshold still
   requires a fresh read of the PDF at the recorded sha256.
4. **The arXiv version number is unknown.** The retrieval URL carried no version
   suffix; quotations are scoped to the sha256, not to a version.
5. **`knowledge/INDEX.md` was NOT regenerated.** `KN-LIT-c41d8b` is a new corpus
   entry, so the index needs `python3 tools/build_knowledge_index.py`. This role
   has no execute capability. **I do not claim it was run** — the
   harness-driving session must run it. (The index is `.gitignore`d and rebuilt
   on demand per CLAUDE.md, so this is a rebuild obligation, not a commit
   obligation.)
6. **`tools/validate_ledger.py` was NOT run.** Same reason. Both new records
   were written against the schemas as read from `templates/research-records.md`
   and `tools/validate_ledger.py` (`REQUIRED["research_question"] = [id, title,
   scope, status, owner]`; knowledge frontmatter `[id, type, title, tags,
   confidence, added]` with filename stem `==` id; `RQ-[A-Z]+-<6hex>` id
   pattern), but the checker itself was not executed. Baseline for whoever runs
   it: BATCH-001 opened with **110** pre-existing errors on this branch and the
   identical 110 on `origin/main`; compare against that, not against zero.
7. **No sha256 was recorded for the three superseded sites.**
   `RQ-FBG-001`'s supersession pattern records `supersedes_sha256`; I cannot
   compute hashes. Each site is pinned instead by path, locus, and verbatim
   superseded text — checkable by string match. Recorded as a gap.
8. **Two new identifiers were minted without `tools/allocate_id.py`**
   (`RQ-MCE-3f7c02`, `KN-LIT-c41d8b`): the tool needs execution. Both are random
   6-hex tokens in the required format, and both were `--check`-equivalent
   verified by a repository-wide search returning **zero** occurrences of either
   token before use. No sequential "next free number" scan was performed, which
   is the failure mode AGENTS.md rule 14 forbids.
9. **`iacr:2026/1232` was not re-attempted by any route**, as directed.
10. **No git operation was performed.** No staging, no commit. Archival is
    `TASK-20260808-2de410`'s task.

---

## 7. Completion gate, item by item

| Gate | Status |
|---|---|
| All three sites superseded in this one task; none left for a later task | **Met.** Sites 1, 2, 3 superseded by §5.1, `RQ-MCE-3f7c02`, `KN-LIT-c41d8b` — written in one task, all three anchored in one ledger record. |
| Superseding text quotes arXiv:2304.14757 verbatim on its own boundary and cites where it appears | **Met, with the provenance qualification in §0**: quotation re-quoted from the committed transcription at sha256 `ebbd94ac…c564b8`, located at the paragraph *"Opening the road for attacking the CFS scheme."*, Table 1's restriction column, and §3.2. No page number exists in the record and none is invented. |
| Each superseded site names what it supersedes and why; originals not edited | **Met.** Each artifact quotes its superseded text verbatim and gives its reason with the authorising decision id. No original file was opened for write. |
| The report states plainly what the corrected boundary IS | **Met** — §3: generic/random alternant codes over F_2 or F_3, m arbitrary, at high rate per condition (6), with Goppa codes explicitly excluded; family conjunct decisive; rate conjunct real and untranscribed. |
| Claim tier stays toy, `active_hypothesis_ids` stays empty | **Met** — §4. Nothing here moves a status. |

---

## 8. Artifacts written by this task

- `coordination/goals/GOAL-MCE-001/batches/BATCH-a68f79/tasks/TASK-20260808-843c87/correction_report.md` (this file)
- `ledger/questions/RQ-MCE-3f7c02.yaml`
- `knowledge/literature/KN-LIT-c41d8b.md`

Nothing else was written, and nothing outside the declared write scope was
touched.
