# Independent validation — GOAL-MCE-001 BATCH-002

**Task:** `TASK-20260803-8cf2b6` · **Role:** validator · **Date:** 2026-08-03
**Goal:** `GOAL-MCE-001` · **Batch:** BATCH-002 · **Question:** `RQ-MCE-e65b3c`
**Objects reviewed:** the snapshot-committed packages of `TASK-20260803-a53f73`
and `TASK-20260803-cb44ab` at commit `b30400a9699e04a0aaca49d5278ab7c50027da13`.

## VERDICT: **ADMIT_WITH_QUALIFICATIONS**

Both packages are admissible. Every proposed correction was checked against the
source sentence it rests on, and every one is **right, not merely different**.
The specific trap this task was directed at — a replacement that leads with the
Goppa exclusion while deleting the rate scoping — was **not** fallen into, and I
verified that against the paper's own three-conjunct sentence in a copy I
re-fetched myself. The 150-cell cost table reproduces exactly from a
re-acquisition, including its column assignment under a geometry-only
reconstruction that shares no reading order with either producer path.

Six qualifications are recorded below. **None** of them touches a table value, a
quoted source sentence, an identifier, or the substance of any correction. Two
(V-1/V-2 and V-3) are defects in the `cb44ab` package's own self-certifications
and observations; one (V-5) is a filing-quality defect that becomes permanent if
filed, and should be fixed before `TASK-20260803-3aa684` writes into
`knowledge/`.

**Inference.** `requested_policy: review-adversarial`; `resolved_model_id:
claude-opus-5`; `fallback_used: true` — the alias does not resolve under this
Claude Code harness and `review-adversarial`'s `xhigh` requirement cannot be
served here. `model_verified: false` (no `orchestration.adapter doctor --probe`
was run). **This review is NOT admissible toward an AGENTS.md rule 13 closure
quorum**: it is the same resolved model as both producers, the Coordinator, the
concurrent red team, and both BATCH-001 reviews. **No attestation may be
synthesized from it, now or later.**

---

## 1. Snapshot integrity — PASS (12/12)

| Check | Result |
|---|---|
| `b30400a9` reachable from `HEAD` (`89a60924`) | **YES** |
| Parent is the declared `33750003863d269e…` | **YES** |
| Commit changes exactly the 12 declared paths, no more, no fewer | **YES** |
| 11 recorded per-path sha256 recompute from the committed blobs | **11/11 MATCH** |
| Receipt's own committed hash vs. `dispatch_queue.json` archive block | `c29470e2cb07c620…` — **MATCH** |
| Working tree identical to committed blobs for all 11 paths | **YES** |

The receipt's `commit_sha: null` and the absence of its own hash from
`path_sha256` are correct by construction and are declared as such. The reviewed
object is fixed and hash-bound; I did not review a working tree.

---

## 2. Re-acquisition — 5 sources, 5 byte-identical, 0 non-reproducible

Re-fetched independently; not trusted from the producers' logs.

| Source | Recorded | My re-acquisition | Result |
|---|---|---|---|
| `classic.mceliece.org/mceliece-security-20221023.pdf` (SEC) | 200, 332,574 B, `db17ef08…b523fa` | 200, 332,574 B, `db17ef0879cb8822120c312b7290f7db82fe9fc356bd16058ad334a512b523fa` | **MATCH** |
| `eprint.iacr.org/2021/1243` (abstract) | 200, 16,056 B, `59810b6c…195734` | 200, 16,056 B, `59810b6c57cc199404bc447779082324d27bbe750db73d0aaea7f47535195734` | **MATCH** |
| `arxiv.org/pdf/2304.14757` | 200, 526,690 B, `ebbd94ac…c564b8` | 200, 526,690 B, `ebbd94ac3cd00b0f0e723aeab56fd3b0820c89d47072fc8241f12c5f93c564b8` | **MATCH** |
| `perso.telecom-paris.fr/randriam/maths/distingueur.pdf` | 200, 726,538 B, `b69f8256…d68c0` | 200, 726,538 B, `b69f8256133dcfd8c9d5dae196b8f653f5b956532a7ba949f400af3b902d68c0` | **MATCH** |
| `eprint.iacr.org/2025/531` (abstract) | 200, `88035f1a…bfb299` | 200, 16,793 B, `88035f1a7a0f59750cbaf89a770295643f0e9a111d72b43bbb6d9ad497bfb299` | **MATCH** |

**Zero non-reproducible hashes and zero unexplained mismatches.** None of the
four BATCH-001 traps applies to this batch's recorded sources: no HAL endpoint,
no eprint OAI-PMH response, no `csrc.nist.gov` page and no `iso.org` request
appears in either package. The two eprint **abstract** pages hashed stably, which
is consistent with `EV-MCE-332f99` O-9's path-scoped finding and does not
re-test the PDF endpoint. `TASK-20260803-cb44ab` D3 correctly declares that it
contributed no new evidence about the 403; I contributed none either, having not
requested that path.

`TASK-20260803-a53f73` performed **no** network retrieval and says so. Its
sources are BATCH-001 artifacts and committed ledger records; I nonetheless
re-fetched the two primary PDFs it quotes and verified its quotations against
them directly (§3).

---

## 3. Per-correction source checks

Every quotation below was verified **in a copy I re-fetched and hashed myself**,
not in the producer's transcription. Ligature and kerning artifacts (`ﬁ`, `ﬀ`,
`“` for `=`) were normalised only in my search patterns, never in what I record.

### C-1 · `KN-LIT-4c8135` → `KN-LIT-c4c2ac` — **RIGHT. The named trap was avoided.**

The task card's duty 2 states the paper carries **three conjuncts** and that an
entry keeping the exclusion while dropping the rate scoping has traded one wrong
entry for another. Verified directly in `arXiv:2304.14757`
(`ebbd94ac…c564b8`), one sentence carrying all three:

> "…show that we can actually attack McEliece-alternant for any extension degree
> m provided that **the rate of the alternant code is sufficiently large (6)**
> and **the field size sufficiently low q “ 2 or q “ 3**."

and the exclusion, verbatim and intact:

> "Interestingly our attack does not work at all when the alternant code has the
> additional structure of being a Goppa code."

Also verified in the re-acquired text: Table 1's *"q “ 2 or q “ 3, m arbitrary +
high rate condition (6) (does not apply in the particular case of Goppa
codes)"*; §3.2's heading *"What is wrong with Goppa codes?"*; *"Goppa codes
behave differently from random alternant codes and provide counterexamples to
Heuristic 18"*; the abstract's *"when the code is a generic alternant code and
when the code field size q is small : q ∈ {2,3}"*; the CFS sentence; and the
MAGMA repository URL. **Every quotation in the proposed entry reproduces.**

| Conjunct | Kept in `KN-LIT-c4c2ac`? |
|---|---|
| 1. Code family — generic alternant, explicitly NOT Goppa | **YES**, led with, at the paper's own hedging level |
| 2. Field size `q ∈ {2,3}` | **YES**, quoted verbatim |
| 3. Rate — the paper's numbered condition (6) | **YES**, quoted verbatim, **and still marked `[EXTRACTION-DAMAGED]` and untranscribed** |

**The rate scoping is not deleted.** What is retracted is precisely and only the
claim that it is *"the whole content of its practical reading"*. The entry keeps
the correct statement that the numeric threshold **remains unheld by this
program**, and now records it as an extraction failure rather than an unattempted
read. Hedging is preserved exactly: *"does not work at all"* is neither hardened
to "cannot work" nor softened to "is not known to work".

### C-2 · `KN-LIT-71d1a0` → `KN-LIT-819780` — **RIGHT, and the producer's correction to the Coordinator's framing is CONFIRMED.**

`BATCH-002-OPENING` §2 and this task's own handoff both call the entry
**wrong-typed**, with the handoff adding *"Any entry stating otherwise is
wrong."* I read `knowledge/literature/KN-LIT-71d1a0.md` in full: **it contains no
rate figure at all.** Its "Not verified here" section reads, verbatim:

> "The construction, its complexity, the code families and rates for which it
> succeeds, and whether it reaches Classic McEliece parameters are NOT recorded
> here."

The producer's finding F-2 is therefore correct and I uphold it: the mis-typing
lives in `BATCH-001-OPENING` §4's framing (`DEC-20260803-a5b9b1` D-2
`also_wrong_typed`), not in the entry. **No corpus entry states otherwise.** The
correction is consequently the right shape — fill the blank from primary text,
remove the `key-recovery` tag — rather than retract a claim never made.

Every quotation in the replacement verified against the re-acquired author's copy
(`b69f8256…d68c0`): Theorem 3's *"Asymptotically, q-ary alternant (including
Goppa) codes of **dual rate R** can be distinguished from random codes"*;
*"However here we allow any R."*; Remark 2's *"1. is satisfied for R < 0.277 and
2. is satisfied for R < 0.141"*; the shortened-code *"= o(1), so by Remark 2 …
both conditions in Heuristic 1 are satisfied"*; *"Distinguishers address the
decisional version of the problem"*; the regime-reach claim; the
finite-parameter caveat; *"remain practically unreacheable"* (source's spelling,
preserved); the 3-of-5 precondition sentence naming `(4608, 13, 96)` and
`(6688, 13, 128)`; and the title-page self-description *"(Eurocrypt 2025 version,
expanded, with supplementary material and errata)"* underwriting the version
caveat. The `[EXTRACTION-DAMAGED]` marking of formula (92) is justified — my own
extraction of that passage emits `(cid:16)` tokens.

`key-recovery` appears nowhere in the replacement's `tags`. Confirmed.

### C-3 · `KN-LIT-13a01d` → `KN-LIT-6b5b72` — **RIGHT.**

The self-contradiction is real and I read it in the file: `tags:` line 18 carries
`key-recovery`, while line 28 reads *"It does not recover keys; it
distinguishes"* and line 43 instructs *"Report a distinguisher as a
distinguisher"*. `RQ-MCE-e65b3c.constraints` names this entry as the anchor of
*"Distinguisher is not break"* — verified in the RQ, line 139. The replacement
removes the tag, carries the body text unchanged, and withdraws only the
cross-reference sentence at line 48–49 whose claim C-1 retracts. The withdrawal
is correctly scoped: it explicitly leaves *this* paper's own high-rate scoping
intact.

### C-4 · `KN-LIT-7ee1a9` → `KN-LIT-45b1b2` — **RIGHT.**

All quoted abstract sentences verified against the re-acquired
`eprint.iacr.org/2025/531` page (`88035f1a…bfb299`): *"Computing HF(2) still
gives a polynomial time distinguisher for alternant or Goppa codes and is
**apparently** able to distinguish…"*, *"rate very close to 1"*, *"a precise
description of the new regime of rates"*, and *"a first step before being able to
attack McEliece"*. The **"apparently" hedge is preserved**, as the entry
insists. `citation_verified` correctly stays `web`; the entry adds the true
statement that the precise regime lives in an unobtained body. It also softens
the superseded entry's *"bears directly on McEliece's structural assumption"* to
*"bears on … ; what it bears is not established by this program"* — an
improvement to the scope firewall, not a loss.

### C-5 · `KN-LIT-e37d4c` → `KN-LIT-15c85b` — **RIGHT, and correctly narrowed.**

Nobody in this program has read `iacr:2025/1661`, and the correction does **not**
assert that the paper is a distinguisher result rather than a key recovery. The
claim made is only that *nothing this program holds supports the `key-recovery`
tag*, which is checkable and which I confirm from the superseded entry's own
body and recorded ePrint title. This is the discipline `KN-OPEN-3f7a21` demands,
applied correctly; the `unread` tag makes the state greppable.

### C-6 · `RQ-MCE-e65b3c` constraint replacement — **RIGHT, and it does not delete the rate axis.**

The defective constraint is quoted exactly as it stands (RQ lines 142–146,
verified), as is `scope.targets` bullet 2 (lines 35–40, verified). The
replacement splits one item into a general discipline plus a paper-specific fact,
keeps all three conjuncts, and keeps the statement that condition (6) is not
held. The proposed `corrections:` block preserves the superseded text in place,
which is the right call under AGENTS.md rule 15: `RQ-MCE-e65b3c` is named in the
binding fields of completed archives and must not be re-keyed. I confirm it is
named in `EV-MCE-332f99`, `DEC-20260803-a5b9b1`, `goal.yaml` and both BATCH-002
dispatch entries.

### C-7 · `BATCH-001-OPENING` §4 superseding note — **RIGHT, filed as a sibling.**

The note quotes §4 verbatim, retracts exactly two claims, and explicitly
reaffirms both the rate condition and §4's own final sentence. `D-6`'s keyword
line is verified in the record chain. The producer's flag stands: the filer's
declared `write_scope` originally could not place the note beside the text it
corrects — the dispatch queue now carries an amendment adding
`batches/BATCH-001` to `TASK-20260803-3aa684`, which resolves it.

### C-8 · Five specification entries — dedup determination **INDEPENDENTLY RE-RUN AND CONFIRMED.**

I re-ran the probes myself rather than reading the producer's table:

| Probe | Producer | Mine |
|---|---:|---:|
| files matching `mceliece` in `knowledge/literature/` | 169 | **169** |
| `knowledge/literature/*.md` | 7807 | **7807** |
| `mceliece-spec` | 0 | **0** |
| `conservative code-based cryptography` | 0 | **0** |
| `guide for implementors` / `guide for security reviewers` | 0 / 0 | **0 / 0** |
| `plaintext confirmation` | 0 | **0** |
| `NIST.IR.8545` / `10.6028/NIST.IR.8545` | 0 / 0 | **0 / 0** |
| `nvlpubs.nist.gov` | 1 (`KN-LIT-7620`) | **1 (`KN-LIT-7620`)** |
| `10.6028` | 4 (`7620`, `055`, `056`, `4573`) | **4, same four** |
| `mceliece(348864\|…\|8192128)` | 1 (`KN-LIT-6614`) | **1 (`KN-LIT-6614`)** |
| sha256 of the spec PDF anywhere in `knowledge/` | 0 | **0** |

**Determination confirmed: the specification family and NIST IR 8545 are not
held.** The `citation_verified: read` discipline is sound — the flag is earned by
`TASK-20260803-f3aece`, each entry names the reading task and receipt, states
`committed_locally: false`, and states that the drafting agent did not read the
documents. This does **not** add to the `KN-OPEN-3f7a21` class.

### C-9 · Transcription convention — **RIGHT, and the two BATCH-002 packages are consistent.**

T1–T3 are `TASK-20260803-292b99`'s standard, which is the stricter one;
`TASK-20260803-cb44ab` independently declared it applied that standard, so the
two producers converged without reading each other. T4 (record extractor,
version and non-default settings) is the addition neither BATCH-001 producer met.
`cb44ab` records extractor names and versions but not its `laparams`; the
convention itself declares that gap non-blocking, and in practice I reproduced
`cb44ab`'s extraction with defaults, so nothing rests on it.

---

## 4. Tag prevalence — re-measured corpus-wide with my own parser

I did **not** run the producer's regex script. I parsed each file's YAML
frontmatter with `yaml.safe_load` and counted tag-set membership over every
subdirectory of `knowledge/`, including `gathers/` which the producer's
enumeration omits.

| Population | files | `key-recovery` | `distinguisher` | **both** | `distinguisher`-only |
|---|---:|---:|---:|---:|---:|
| `knowledge/literature/` | 7807 | 50 | 7 | **4** | 3 |
| `knowledge/techniques/` | 83 | 2 | 2 | 0 | 2 |
| `knowledge/findings/` | 31 | 0 | 0 | 0 | 0 |
| `knowledge/open-problems/` | 26 | 0 | 0 | 0 | 0 |
| `knowledge/gathers/` | 7 | — | — | — | — (no frontmatter tags) |
| **tagged total** | **7947** | **52** | **9** | **4** | **5** |

**Exact agreement with the producer on every cell.** The both-tagged set is
exactly `KN-LIT-13a01d`, `KN-LIT-71d1a0`, `KN-LIT-7ee1a9`, `KN-LIT-e37d4c` — the
four `DEC-20260803-a5b9b1` D-5 names, and no others corpus-wide. The
distinguisher-only set is `KN-LIT-109`, `KN-LIT-110`, `KN-LIT-7587`,
`KN-TECH-039`, `KN-TECH-077`.

Sub-population `added: "2026-08-03"` in `knowledge/literature/`: **137** entries,
**36** `key-recovery`, **4** `distinguisher`, **4** both, **0**
distinguisher-only. The red team's BATCH-001 measurement reproduces exactly, and
so does the producer's reproduction of it.

**Producer's conclusion CONFIRMED:** the defect does not extend beyond the four,
no pre-existing or non-McEliece entry carries the pair, and the corpus's own
prior practice shows correct single-tagging was already available — so the defect
is **local to the 2026-08-03 McEliece sweep**.

Two qualifications on the producer's *prose* (neither affects a count or the
conclusion):

- **"The corpus-wide prevalence is 4 of 7."** 4 of 7 is the **literature-only**
  figure. Corpus-wide, by the producer's own table, there are 9
  distinguisher-tagged records, so the corpus-wide figure is **4 of 9**. The
  sentence and the table two lines above it disagree.
- **"`KN-LIT-109`, `KN-LIT-110` and `KN-LIT-7587` (lattice/LWE, added
  2026-07-24)."** `KN-LIT-7587` was added **2026-07-27**, and it is not
  lattice/LWE — its tags are `complexity, lower-bound, low-degree-method,
  average-case-hardness, hardness-evidence, counterexample, barrier,
  methodology, reed-muller, distinguisher`. Two stated attributes of one of three
  entries do not reproduce.

**Boundary I endorse:** this is tag-set membership only. It cannot find a
distinguisher paper carrying neither tag, and it establishes nothing about
whether anything consumes these tags. The producer states this explicitly and
rests no correction on `BATCH-002-OPENING` §3's harm claim. That claim remains
untested here; testing it is the red team's duty 3, not mine.

---

## 5. Identifier allocation — all ten well-formed and free

`python3 tools/allocate_id.py --check <ID>`, run by me at this HEAD, 9967 files
scanned per call:

| ID | Purpose | 6-hex? | Occurrences across the union |
|---|---|---|---:|
| `KN-LIT-c4c2ac` | supersedes `KN-LIT-4c8135` | yes | 0 |
| `KN-LIT-819780` | supersedes `KN-LIT-71d1a0` | yes | 0 |
| `KN-LIT-6b5b72` | supersedes `KN-LIT-13a01d` | yes | 0 |
| `KN-LIT-45b1b2` | supersedes `KN-LIT-7ee1a9` | yes | 0 |
| `KN-LIT-15c85b` | supersedes `KN-LIT-e37d4c` | yes | 0 |
| `KN-LIT-48b4eb` · `7b78de` · `b7f8f8` · `209151` · `9a7860` | retained spec entries A–E | yes (all five) | 0 (each) |

**All ten are lowercase 6-hex and free.** Two caveats a filer must know, both
established by reading the tool:

1. `--check` prints *"well-formed: YES — no pattern is enforced for `KN-*` in
   `validate_ledger.ID_PATTERNS`; well-formedness NOT checked."* The tool
   **does not** verify the 6-hex form for `KN-*` identifiers. I verified the form
   myself, character by character; the tool's "OK" alone would not have.
2. `occurrences()` matches on **file name**, and `SEARCH_GLOBS` includes
   `knowledge/*/*.md`. The union therefore does cover the directory these will be
   filed into, which is what matters here.

**No `max+1` shape.** None of the ten sits adjacent to any existing maximum;
legacy `KN-LIT` identifiers in this corpus are ≤4 digits, and `819780` / `209151`
are 6-hex tokens that happen to be all-decimal, not increments of anything. The
producer's method (`allocate_id.random_token(SystemRandom())`, reject unless
`occurrences()` is empty, then `--check`) scans no state and cannot converge.

**DV-1 verified clean.** The unminted token `KN-LIT-9b1c9e` survives in **exactly
one place** in the whole repository — `correction_log.yaml` line 138, inside the
DV-1 deviation record that discloses it. It is not used as an entry ID, a
`supersedes` target, or a cross-reference anywhere in the package. **No unminted
identifier survives in live use.** Recording a discarded token inside its own
disclosure is correct, not a residue.

---

## 6. Cost table — 150/150 cells reproduce from my own re-acquisition

I re-fetched the SEC PDF, extracted it row-major with pypdf 6.14.2, and
independently rebuilt the table from `LTChar` character coordinates (rows
clustered by baseline `y`, cells by `x`-gap), sharing no reading order with the
producer's paths. I then diffed all 150 cells three ways: **my extraction × the
rendered markdown table in §3 × the raw block embedded in §3.1.**

```
cells compared: 150   mismatches: 0
header:  param mem Prange Stern Dumer BC BJMM pdw MO BM   (all three agree)
```

Column-assignment check, reproduced independently:

- Header token centres: `123.0 / 164.0 / 206.7 / 250.6 / 294.1 / 342.2 / 380.9 /
  426.9 / 466.9 / 506.3` pt — **identical to the recorded values**.
- First data row cell centres: `120.8 / 173.4 / 211.3 / 251.0 / 298.3 / 337.3 /
  385.4 / 424.4 / 463.4 / 502.5` pt — **identical**. Every cell's nearest header
  is the header it is transcribed under, for all ten columns and all fifteen rows.
- Table region (`y0 > 480`): **771 glyphs, one single font size 11.96 pt** —
  reproduced exactly. The claim that no table cell needs an
  `[EXTRACTION-DAMAGED]` marker is therefore mechanically justified, not asserted.

Supporting measurements, all reproduced:

- Flattened superscripts: exponent digits at **7.97 pt raised 5.1 pt** above an
  **11.96 pt** base `2`, verified for `143`, `86.6`, `256`, `246.6` (p.10) and
  `279.2`, `207` (p.11). Every `[EXTRACTION-DAMAGED]` marker in the package is
  backed by this measurement.
- Caption verbatim with its artifacts (`T able 1`, `1 /3`, `1 /2`, `cube- root`)
  — reproduced character for character, including that the same bullet prints
  `1/3` unsplit while `1 /2` is split.
- Grep counts: `Table 1` → **7**, `T able 1` → **1** (8 references total),
  `memor` → **18**. All reproduce, and the caption really is missed by a naive
  `Table 1` grep — a useful caution, correctly stated.
- Value statistics: 120 cost values, **102 distinct**, **16** appearing more than
  once. `140.8` once at `348864/0/MO`; `246.6` once at `6960119/0/BJMM`; `279.2`
  **twice**, at `6688128/1/3/Stern` and `6960119/1/2/MO`. All confirmed; the
  refusal to adjudicate which one SEC's sentence means is correct.
- All twelve hedges H1–H12 verified in the re-acquired text, including the
  `ﬀ`/`ﬁ`/`ﬂ` ligatures and kerning splits recorded around them
  (`diﬀerent`, `ﬁndingC`, `2L +C`, `quantiﬁcation`, `201 .0`, `0 .8`).
- SEC's printed date *"23 October 2022"* and title confirmed on the title page.
- Bibliography `[33]` reproduces verbatim, hyphenation included.
- The `GOAL-MCE-001` completion criterion quoted in `baseline_gap_statement.md`
  §1 matches `goal.yaml` exactly.

### Convention adopted: NO. Cost computed: NO. — with one qualified exception

I checked this against the whole package, not the summary. **No costing
convention is adopted, proposed, or derived; `ISD-FC-2026` appears only in
statements that this task does not bind to it; no cost figure of this program's
own exists anywhere; and no table value is converted, aggregated, ratioed, or
compared against any external number.** The substantive prohibition holds.

The **absolute** self-certification does not. See V-1/V-2 below.

### Anomaly `8192128 / mem 0 / Dumer` = 307.4 — CONFIRMED IN THE SOURCE

The cell reads `307.4` in my row-major extraction **and** in my geometry-only
reconstruction, seated at `x = 298.3` pt directly under the `Dumer` header at
`294.1` pt. It is **not** a transcription artifact and not a column-assignment
error. `Stern` reads `303.2` and `BC` `303.4` in the same row. Recording it and
proposing no cause is the correct disposition for a transcription task, and I
propose none either.

### Undefined column abbreviations — disposition correct, **measurement partly false**

The refusal to expand `BC`, `BJMM`, `pdw`, `MO`, `BM` is right: supplying them
from memory would be a rule-9 fabrication and inferring them from §3.3 would be a
forbidden derivation. But the *measurement* that supports the observation does
not fully reproduce. See V-3.

---

## 7. The BATCH-001 red team's published control — **DOES NOT REPRODUCE. The producer is right.**

`coordination/goals/GOAL-MCE-001/batches/BATCH-001/reviews/TASK-20260803-08e883/red_team_report.md`,
lines 607–608, publishes:

> **Cheapest control:** `grep -c -i goppa knowledge/literature/KN-LIT-4c8135.md`
> → 1, and read the one hit. Cost: one command.

I ran it:

```
$ grep -c -i goppa knowledge/literature/KN-LIT-4c8135.md
2
$ grep -o -i goppa knowledge/literature/KN-LIT-4c8135.md | wc -l
2
```

Line 25 and line 31. I also ran it against the committed blob at the BATCH-002
snapshot (`2`) and against **every revision of that file in git history** — the
file has exactly one content revision, `10dc665c`, which also gives `2`. **The
published control never reproduced at any point.** This is a defect in a
**committed review report** and must be recorded as such in
`DEC-20260803-18d8f3`, alongside the corresponding "mentions Goppa once" wording
in `DEC-20260803-a5b9b1` D-4 and `BATCH-002-OPENING` §2.

**Direction: the defect is LARGER than the record states, not smaller.** The
second occurrence, line 31 — *"The attack is **rate-scoped** — it does not claim
to break alternant or Goppa codes at arbitrary rate"* — has as its natural
contrapositive that the attack *does* claim to break Goppa codes at high rate,
which is exactly what the paper's own sentence denies. The proposed replacement
neutralises both occurrences and says so.

---

## 8. Confirmed findings against the Coordinator's own framing

I independently verified the producer's two material findings against
`BATCH-002-OPENING`, at this HEAD:

- **F-3 UPHELD.** `BATCH-002-OPENING` §1's defect table marks D-3 *"already
  corrected"*. That is true of `ledger/goals/GOAL-MCE-001/goal.yaml` (the
  correction is at lines 42–44, quoted verbatim and present) and **false of
  `RQ-MCE-e65b3c`**, which still carries **both** `constraints` item 3 — *"Bind
  to the costing convention produced under GOAL-HQC-001 TASK-20260802-0100a5; do
  NOT derive a competing one"* (lines 133–137) — **and** `scope.targets` bullet 3
  — *"under the same costing convention GOAL-HQC-001 and GOAL-SDITH-001 bind
  to"* (lines 41–44). The RQ still instructs an act `DEC-20260803-a5b9b1` D-3
  says cannot be performed, and it did so **while `TASK-20260803-cb44ab` ran**.
  `TASK-20260803-3aa684`'s handoff already carries the duty to correct both;
  this validation confirms the premise of that duty.
- **F-4 UPHELD.** `RQ-MCE-e65b3c.scope.standardization_status` (lines 19–27)
  still reads *"UNVERIFIED here — neither page was fetched"*, when
  `EV-MCE-332f99` O-6 records NIST IR 8545 read directly. The ISO half correctly
  remains open per O-7.

Both were flagged and **not drafted** by the producer, on the stated ground that
inventing an unasked fourth correction is how a correction batch grows a new
defect. I endorse that restraint.

---

## 9. Scope firewall — HOLDS in both packages

I read both packages for security predicates about Classic McEliece. **Every
occurrence is either a quoted, attributed source statement or the package's own
prohibition on itself.** No statement about whether any parameter set is secure
or threatened appears in either package, including by juxtaposition. Notably:
`cost_table_transcription.md` §3 places the five `param` labels beside
`EV-MCE-332f99` O-1's parameter sets and explicitly declines to use anything from
O-1; `convention_as_stated.md` §5 transcribes the submission's own category
claims and states three times that it endorses, contests and concludes nothing
from them; `KN-LIT-c4c2ac` states the Goppa/Classic-McEliece adjacency and draws
no consequence in either direction. No hypothesis was created, no experiment
designed, no solver run, and `runs_executed: 0` in both packages against
`runs_authorized: 0`.

---

## 10. Qualifications

**V-1 — the "zero arithmetic" self-certification is contradicted by the package's
own observation. (Material to a stated claim; not to any value.)**
`source_access_log.yaml` `costs_computed_note` and `cost_table_transcription.md`
§0/§8 certify *"No arithmetic of any kind was performed on a table value: no
differencing, no ratio, no comparison to any other number."* But
`cost_table_transcription.md` §6 O-2 states that in the other four `mem 0` rows
the `Stern` and `Dumer` entries *"are within 0.1–0.2 of each other"* — that is a
**differencing of table values and a comparison between them**. It is used only
to characterise an anomaly; no cost is derived from it and no convention follows.
The substantive prohibitions (compute no cost, adopt no convention) **hold**; the
absolute wording does not. The fix is to narrow the certification, not to delete
the observation.

**V-2 — the stated range does not recompute.** I computed the four `mem 0`
`Dumer − Stern` differences: **0.0, −0.1, −0.1, −0.1**. The range is **0.0 to
0.1**, not *"0.1–0.2"*: the `348864` pair is `151.4 / 151.4`, a difference of
exactly zero, which the stated range excludes, and no pair differs by 0.2. The
four listed pairs themselves are correct, and the anomaly (`+4.2`) is unaffected.

**V-3 — observation O-1's grep measurement is false for one of its five tokens,
and propagates to two other files.** O-1 states that a grep of the whole 36-page
extraction finds `BJMM`, `pdw`, `MO` and `BM` *"nowhere outside that single
header line"*. My grep over all 36 pages:

| token | occurrences | pages |
|---|---:|---|
| `BJMM` | **2** | **10 and 31** |
| `pdw` | 1 | 10 |
| `MO` | 1 | 10 |
| `BM` | 1 | 10 |
| `BC` (standalone) | 1 | 10 |

The second `BJMM` is SEC's bibliography entry **[15]**, PDF page 31: *"Leif Both
and Alexander May. Optimizing BJMM with nearest neighbors: Full decoding…"* Four
of five tokens reproduce; `BJMM` does not. **The disposition is unaffected and
remains correct** — a bibliography title is not a column-label expansion, and
supplying one would still be a derivation the task is forbidden to make. But the
measurement as stated is wrong, and it propagates verbatim into
`baseline_gap_statement.md` G9 and `source_access_log.yaml` O1.

**V-4 — a stale cross-reference in text proposed for filing into immutable
entries. Fix before filing; uncorrectable after.** The package's own §5
correctly moves the retrieval `sha256` out of `identifiers:` into a new top-level
`source_artifact:` block, having measured that `build_source_index.py` would
otherwise emit a content hash into `SOURCES.md` as a bibliographic identifier.
But three replacement entries still direct the reader to *"the sha256 in
`identifiers`"*, where it no longer is:

- `superseding_entries.md` §1.4 (`KN-LIT-c4c2ac`): *"A reviewer wanting condition
  (6) must read the rendered PDF at the sha256 in `identifiers`."*
- `superseding_entries.md` §2.3 (`KN-LIT-819780`): *"every claim recorded here is
  scoped to the sha256 in `identifiers`."*
- `tag_defect_corrections.md` §4.2 (`KN-LIT-45b1b2`): *"Only the ePrint abstract
  was obtained, at the sha256 in `identifiers`."*

These are one-word edits now and permanent afterwards, since a filed entry is
corrected only by supersession.

**V-5 — three new frontmatter keys, one flagged and two not.** At this HEAD,
`supersedes` appears in 5 corpus entries; **`supersedes_reason` (0),
`citation_verified_note` (0) and `source_artifact` (0) appear nowhere.** The
producer flags `source_artifact` and asks the Coordinator to decide; it does not
flag the other two. I confirm all three are inert in the derived index
(`build_source_index.py` walks a fixed key list and ignores unknown top-level
keys), so this is a schema-consistency decision, **not a defect** — but the filer
should make it once, for all three keys, rather than for one.

**V-6 — tag hygiene in `KN-LIT-c4c2ac` (minor, a filing decision).** The entry
introduces two synonymous tags, `not-goppa` and `goppa-excluded`, **neither of
which occurs anywhere in the corpus**, and it does **not** carry the existing
`goppa` tag. A future tag-grep for `goppa` will therefore miss the entry that
carries this campaign's single most load-bearing Goppa sentence. `dual-rate` and
`betti-numbers` in `KN-LIT-819780` are likewise new (0 occurrences); `unread` (3)
and `subexponential` (4) already exist. Given that the whole D-5 defect is a
tag-line defect, a consistent tag vocabulary is worth one decision at filing.

**V-7 — trivial.** `baseline_gap_statement.md` §1 says *"Five requirements are
load-bearing in that sentence"* and then lists six.

---

## 11. What this validation does and does not support

- It establishes that the reviewed object is hash-bound and reproduces; that all
  five recorded sources re-acquire byte-identically; that every proposed
  correction is right against the source sentence it rests on; that all 150 table
  cells and their column assignment reproduce from an independent extraction;
  that the tag census reproduces under a different parser; and that all ten
  identifiers are well-formed and free.
- **It supports no claim about Classic McEliece's security in either direction**,
  and none may be inferred from it. It is not evidence for or against any attack,
  cost, or parameter set. A corrected literature entry is not a result.
- **It addresses none of promotion gates G1–G4.** BATCH-002 advances no
  asymptotic-complexity claim of this program's own, so there is nothing for
  `docs/inventor-protocol.md` §6's ladder or §3's null-object requirement to bind
  to: no speedup is claimed, no statistical signal is reported, and no baseline
  measurement of this program's own exists. Stated explicitly so it cannot be
  read as gate progress.
- `claim_tier` stays **toy**; `RQ-MCE-e65b3c`'s ceiling is unchanged; AGENTS.md
  rule 7 applies unchanged.
- **Not admissible toward an AGENTS.md rule 13 quorum.** One resolved model
  (`claude-opus-5`) across the Coordinator, both producers, both BATCH-001
  reviews, this validation and the concurrent red team. No `completion_quorum`
  block may cite this report and **no attestation may be synthesized from it**.

## 12. Recommendation to `TASK-20260803-3aa684`

File C-1 through C-5 and C-8 (both writes each: the new entry **and**
`superseded_by` on the old). Apply V-4 before filing — it is the only
qualification that becomes permanent. Decide V-5 and V-6 once. Record V-1, V-2
and V-3 as findings against `TASK-20260803-cb44ab`'s package that do **not**
block admission of the table, and record §7's non-reproducing BATCH-001 control
and §8's F-3/F-4 as findings against committed Coordinator and review records,
carried rather than dropped — the practice `DEC-20260803-a5b9b1` established.

**Report path:**
`coordination/goals/GOAL-MCE-001/batches/BATCH-002/reviews/TASK-20260803-8cf2b6/validation_report.md`
