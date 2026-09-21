# Validation report — GOAL-MCE-001 BATCH-001 transcriptions, receipts, and the ISD-convention status

**Task:** TASK-20260803-409c5e · **Role:** validator · **Goal:** GOAL-MCE-001 ·
**Batch:** BATCH-001 · **Question:** RQ-MCE-e65b3c · **Date:** 2026-08-03
**Validates:** TASK-20260803-292b99 (via snapshot TASK-20260803-9fddc2) and
TASK-20260803-f3aece (via snapshot TASK-20260803-f3beb0)

## VERDICT: `ADMIT_WITH_QUALIFICATIONS`

Both transcriptions say what their sources say. Every number I could check
recomputed or re-verified against a re-fetched primary document. The
qualifications are four, none of which touches a transcribed number, and one of
which is a **finding against the batch opening, not against either producer**.

---

## 0. Inference and admissibility — read this before using this report

```yaml
inference:
  requested_policy: review-adversarial
  resolved_model_id: claude-opus-5
  fallback_used: true
  fallback_reason: >-
    orchestration/model-policies.yaml aliases (GPT-5.6 family) do not resolve
    under this Claude Code harness; .claude/agents/ frontmatter supports only
    Claude models and all subagents run model: inherit. Recorded per CLAUDE.md
    "Model policy note", never silently substituted.
  reasoning_effort_requested: xhigh
  reasoning_effort_verified: false
  model_verified: false
  model_verified_note: >-
    No `python3 -m orchestration.adapter doctor --probe` was run by this task.
  independent_session: true
```

**This review is NOT admissible toward an AGENTS.md rule 13 closure quorum.**
It is an independent session, but it resolves to the **same single model**
(`claude-opus-5`) as both producers and as the Coordinator. Rule 13 requires
three **pairwise-distinct resolved models**; correlated judgements from one
backend counted three times are the exact failure mode that rule exists to
prevent. **No attestation may be synthesized from this report.** Nothing in
BATCH-001 is admissible toward closure of GOAL-MCE-001.

This report establishes only that the receipts hold and the transcription is
faithful. Per `agents/validator.md`, a passed validation **does not** support
any claim about Classic McEliece's security, does not demonstrate a speedup,
and does not authorize promotion. I express **no view** on the attack's
mathematical significance — that is outside this role and was excluded by the
task card.

---

## 1. Snapshot integrity — `PASS`, no qualification

I validated Coordinator-committed snapshots, not working-tree artifacts.

| Check | TASK-20260803-9fddc2 | TASK-20260803-f3beb0 |
|---|---|---|
| Commit | `6787c6e4` | `4d801d94` |
| Reachable from `HEAD` (`398677d7`) | yes | yes |
| Recorded `parent_sha` matches Git | `6b4c09dc` ✓ | `6787c6e4` ✓ |
| Commit changes **exactly** the declared paths | 6/6 ✓ | 5/5 ✓ |
| No scope expansion (`dispatch_queue.json` excluded as stated) | ✓ | ✓ |
| `path_sha256` reproduce against committed blobs | 5/5 ✓ | 4/4 ✓ |
| Working tree clean | ✓ | ✓ |

All nine recorded artifact hashes recomputed identically from the committed
blobs **and** from the working tree. The `commit_sha: null` construction is
sound and self-documenting: a receipt committed inside the commit it describes
cannot carry that commit's hash. The declared-vs-actual path check is what
makes that safe, and it passes.

---

## 2. Named duty 1 — RE-ACQUIRE, DO NOT TRUST

I re-fetched every source the producers recorded a hash for, from this session,
and recomputed sha256 myself. **26 re-acquisitions.**

### 2.1 Result summary

| Outcome | Count |
|---|---|
| Byte-identical sha256 **match** | **25** |
| Not reproducible **by construction**, cause established mechanically | **5** |
| Unexplained mismatch | **0** |
| Evidence of fabrication | **0** |

### 2.2 TASK-20260803-f3aece — the load-bearing documents all reproduce

All ten `classic.mceliece.org` retrievals reproduced **byte-identically**:

| seq | URL | bytes | sha256 (recomputed) | result |
|---|---|---:|---|---|
| 1 | `classic.mceliece.org/` | 6291 | `919bd41c…` | MATCH |
| 2 | `/spec.html` | 5669 | `43152e52…` | MATCH |
| 3 | `/nist.html` | 9378 | `4b6276f3…` | MATCH |
| 4 | `/iso.html` | 6155 | `cc73020d…` | MATCH |
| 5 | `/mceliece-spec-20221023.pdf` | 249199 | `dcc68788…` | **MATCH** |
| 6 | `/nist/mceliece-submission-20221023.pdf` | 115971 | `cbcbcd49…` | MATCH |
| 7 | `/mceliece-security-20221023.pdf` | 332574 | `db17ef08…` | **MATCH** |
| 8 | `/comparison.html` | 22587 | `a5350b5f…` | MATCH |
| 9 | `/mceliece-impl-20221023.pdf` | 279687 | `86225992…` | **MATCH** |
| 15 | `/mceliece-pc-20221023.pdf` | 96835 | `9894108c…` | MATCH |
| 14 | `nvlpubs.nist.gov/…/NIST.IR.8545.pdf` | 588999 | `d802f484…` | **MATCH** |

Every document that any number or quotation actually rests on (SPEC, SEC, IMPL,
PC, NIST IR 8545, iso.html) reproduced byte-for-byte. The producer's own
`reproducibility_check` (re-fetch of SPEC, `byte_identical_to_first_fetch:
true`) is confirmed independently.

Two entries recorded `sha256: not_obtained` with a stated reason (`-o /dev/null`
reachability probes). I confirmed both are consistent: `www.nist.gov` → 200 /
95182 bytes (matching the recorded byte count exactly), `iso.org/standard/detail`
→ 403 / 5404 bytes (matching exactly). Declining to back-fill a hash from a
*later* retrieval than the one logged is the correct call and I endorse it.

### 2.3 TASK-20260803-292b99 — 14 of 16 attempted match

MATCH: `A01` (eprint abstract, 17323 B, `6e27530d…`), `A05`, `A12`, `A13`,
`A14`, `A16`, `A21`, `A24`, `A25`, **`B01`** (syzygy full text, 726538 B,
`b69f8256…`), `B02`, `C01`, **`C02`** (high-rate alternant full text, 526690 B,
`ebbd94ac…`), `D03`.

**Both obtained full texts reproduce byte-identically.** That is the
load-bearing receipt for everything quoted in §2 and §3 of
`attack_transcription.md`, and it holds.

### 2.4 The five non-reproducible hashes — cause established, producer not at fault

The task card warned about the HAL trap. I found the same class of artifact at
**four additional endpoints**, and established the mechanism in each case rather
than asserting it.

| Source | Recorded | Mine | Bytes | Mechanism (verified by diffing two of my own fetches) |
|---|---|---|---:|---|
| `292b99` A11 — eprint OAI-PMH | `0de9ebdd…` | `e3ddc89c…` | 3273 = 3273 | XML `<responseDate>` timestamp. Fixed-width ⇒ byte count stable. **Content byte-identical after stripping that one element.** |
| `292b99` D01 — `inria.hal.science/…/document` | `1d67cddb…` | `7ac84b8c…` | 12595 / 12596 | Anubis proof-of-work interstitial, `<title>Making sure you're not a bot!</title>`, served under **HTTP 200**. Per-request challenge. |
| `f3aece` seq 10 — `csrc.nist.gov/projects/post-quantum-cryptography` | `e635a9f4…` | `4ecfefd2…`, then `ef722652…` | 60700 = 60700 = 60700 | Cloudflare `/cdn-cgi/l/email-protection` obfuscation uses a **per-response random XOR key**. Three fetches, three hashes, one byte count. |
| `f3aece` seq 13 — `csrc.nist.gov/pubs/ir/8545/final` | `9851072f…` | `16568504…`, then `e43358c7…` | 49219 (all) | Same mechanism. |
| `f3aece` seq 16 — `iso.org/search.html?q=McEliece` | `8df45368…` | `e5df1f0d…`, then `e245fc8b…` | 5440 (all) | Cloudflare managed challenge; body carries `nonce-…`, `cRay`, and per-request `cf_chl` tokens. HTTP 403 reproduces. |

**None of these is a producer error and none is evidence against either
producer** (AGENTS.md rule 5). In every case the *outcome* the producer recorded
— status code, byte count, and blocked/success classification — reproduced
exactly. Only the hash is non-reproducible, and it is non-reproducible **by
construction**.

I did not re-attempt `A02`/`A03`/`A04`/`A29` for hash comparison because the
producer had already documented those bodies as nonce-bearing; I verified their
*statuses* instead (§5).

**Qualification Q1 (methodological, addressed to the log format, not to a
number).** The 292b99 producer explicitly flagged nonce non-reproducibility for
its challenge pages (`A02` note, `A29`, `D02`, and deviation item 4: *"A
validator re-acquiring a blocked URL should expect the hash to differ and should
not read that as a discrepancy"*). That warning is accurate, useful, and it is
what let me classify these quickly. But **neither producer flagged the other
three cases** — OAI-PMH `responseDate`, and the two Cloudflare
email-obfuscation pages, which are *successful* HTTP 200 content fetches, not
challenges. A future reviewer re-acquiring `csrc.nist.gov` will get a hash
mismatch on a page that served fine. Recommendation for the batch's log schema,
not a defect in this batch's conclusions: a recorded sha256 should carry a
`hash_stable: true|false|unknown` axis, since "same bytes, different hash" is
evidently common across three unrelated hosts.

---

## 3. Named duty 2 — the rate arithmetic, recomputed in exact rationals

Recomputed independently with `fractions.Fraction` and `math.gcd` from the
`(m, n, t)` triples **as re-read by me from the re-fetched specification**, not
from the producer's table.

| Set | m | n | t | m·t | k = n − mt | k/n exact | gcd(k,n) | k/n (6 dp) | mt < n |
|---|---:|---:|---:|---:|---:|---:|---:|---:|:--:|
| mceliece348864(f) | 12 | 3488 | 64 | 768 | **2720** | **85/109** | 32 | 0.779817 | ✓ |
| mceliece460896(f) | 13 | 4608 | 96 | 1248 | **3360** | **35/48** | 96 | 0.729167 | ✓ |
| mceliece6688128(f) | 13 | 6688 | 128 | 1664 | **5024** | **157/209** | 32 | 0.751196 | ✓ |
| mceliece6960119(f) | 13 | 6960 | 119 | 1547 | **5413** | **5413/6960** | 1 | 0.777730 | ✓ |
| mceliece8192128(f) | 13 | 8192 | 128 | 1664 | **6528** | **51/64** | 128 | 0.796875 | ✓ |

**All five `k` values, all five reduced fractions, all five gcds, and all five
six-decimal roundings agree with `parameter_sets.md` §2 exactly.** `m, n, t, k`
are mutually consistent in every row, and the specification's own precondition
`mt < n` (SPEC §3) holds in every row.

- **5413 is prime** — confirmed by trial division. `6960 = 2⁴·3·5·29 = 6960` ✓.
  The fraction is irreducible.
- The producer's **self-disclosed** prose error (first draft justified
  irreducibility with "5413 = 7·773") is confirmed to have been an error
  (7·773 = 5411) **and** confirmed to have been correctly identified,
  corrected, and disclosed under AGENTS.md rule 8. No transcribed value was
  affected. Disclosing a caught error rather than silently repairing it is the
  behaviour the contract asks for, and it is what let me verify the correction
  independently.
- Rate range **0.729167 … 0.796875** confirmed; non-monotonicity in claimed
  category confirmed (348864 at cat 1 has a *higher* rate than 6688128 at
  cat 5). Restricting to the ISO sets leaves the endpoints unchanged, since
  460896 and 8192128 are both ISO sets — confirmed against the ISO list I
  re-fetched (§6.3).

### 3.1 The producer's own control, independently re-run — 10/10 confirmed

I re-derived the size table from the transcribed triples using the formulas as
**I** read them verbatim from the re-fetched SPEC §6.2 (`mt⌈k/8⌉` for the public
key, `⌈mt/8⌉` for the ciphertext):

| Set | ⌈k/8⌉ | mt·⌈k/8⌉ | IMPL pk | ⌈mt/8⌉ | IMPL ct | |
|---|---:|---:|---:|---:|---:|:--:|
| 348864 | 340 | 261120 | 261120 | 96 | 96 | MATCH |
| 460896 | 420 | 524160 | 524160 | 156 | 156 | MATCH |
| 6688128 | 628 | 1044992 | 1044992 | 208 | 208 | MATCH |
| 6960119 | **677** | 1047319 | 1047319 | **194** | 194 | MATCH |
| 8192128 | 816 | 1357824 | 1357824 | 208 | 208 | MATCH |

**10/10 confirmed.** The producer's claim is correct. The discriminating case is
real: 6960119 is the only set where both ceilings bite (5413/8 = 676.625 → 677;
1547/8 = 193.375 → 194) and it matches exactly. A transcription error in
`m`, `n`, `t`, or in the pk/ct columns would need two compensating errors to
survive this bridge.

**Scope of that control, stated precisely because the producer stated it
precisely.** The bridge covers **pk and ct only** — 10 of the 40 cells of IMPL
Table 1. The **private-key column** (6492, 13608, 13932, 13948, 14120) has no
arithmetic bridge and is transcription-only. `parameter_sets.md` §5 correctly
scopes its claim ("5 sizes × pk and ct") and does not overstate. I therefore
verified the private-key and session-key columns **directly** against the
re-fetched IMPL Table 1 instead: **all 40 cells match** (§6.2).

### 3.2 The `pc` ciphertext arithmetic

`⌈ℓ/8⌉ = ⌈256/8⌉ = 32` confirmed; the five `pc` ciphertext sizes
(128, 188, 240, 226, 240) recompute correctly. These are labelled **computed,
not transcribed**, and §6 states plainly that a transcribed `pc` size table was
**not obtained**. That labelling is correct and I endorse it.

---

## 4. Named duty 3 — the ISD-convention status, settled as a FACT

This is the material finding of this review. I read the artifact. I did not
restate the opening document.

### 4.1 What exists

`coordination/goals/GOAL-HQC-001/batches/BATCH-001/tasks/TASK-20260802-0100a5/`
— `isd_costing_convention.md` (759 lines) and `convention_provenance.yaml`
(1017 lines). Snapshot-committed at `e6f20223` by `TASK-20260802-a3dc0a`. The
task is `state: completed`. It has been independently reviewed: validation
`TASK-20260802-b8d69f`, red team `TASK-20260802-73a352`. The convention is named
**`ISD-FC-2026` v1**.

So: **the artifact exists, it is real, it is complete, and it is reviewed.**
That much of BATCH-001-OPENING §5 is a checked fact.

### 4.2 Is it final? — **NO. It is explicitly NOT ADOPTED.**

Three independent records say so, two of them official ledger records:

1. **The convention's own header:**
   `| Status | **proposed** — binding only if a Coordinator ledger archive adopts it |`
   and `| Binds (if adopted) | every ISD cost figure reported by GOAL-HQC-001 or GOAL-SDITH-001 |`.

2. **`ledger/decisions/DEC-20260802-344883.yaml`, decision D-6, verbatim:**
   > "ISD-FC-2026 IS NOT ADOPTED. The proposed convention is admitted as a
   > reviewed working document only. Adoption is conditional on resolving the
   > red team's O6 and O7: the mandatory F4 self-audit is under-determined by
   > the convention's own rules (U2 and section 3(g) never pin N, and Wiener's
   > form is F = Theta(T r m^{1/3}) at p = Theta(m^{2/3}/r)), the second stated
   > justification for the cube-root memory-access model is circular…"

   with the note: *"It is a usable draft, not a binding convention, and
   GOAL-SDITH-001 must not bind to it in its current state."*

   The same decision's options-not-taken explicitly **rejects** the option
   *"Adopt ISD-FC-2026 so GOAL-SDITH-001 can bind to it"*, because *"Adopting it
   to unblock another goal would propagate the defect to both."*

3. **`ledger/goals/GOAL-HQC-001.yaml` `next_action`, verbatim:**
   > "DO NOT bind GOAL-SDITH-001 to ISD-FC-2026: it is reviewed but NOT ADOPTED,
   > pending DEC-20260802-344883 D-6."

### 4.3 Is it genuinely scheme-independent? — **YES, and independently checked**

This is the one substantive property that survives. It is not merely
self-asserted by the producer: `DEC-20260802-344883` D-6's note records that
*"The convention's scheme-independence gate DID hold under exhaustive integer
enumeration, and its five charged/uncharged verdicts and falsification hooks are
complete."* The document contains no parameter set, no code length, no security
level, and no bit-count; symbolic quantities are placeholders. Confirmed by
reading it.

### 4.4 Is binding to it available to GOAL-MCE-001? — **NO**

Two independent grounds:

- **It is not adopted.** The program's own decision forbids GOAL-SDITH-001 — a
  sibling code-based goal in exactly GOAL-MCE-001's position — from binding to
  it in its current state, on the reasoning that doing so *propagates the
  defect*. That reasoning applies to GOAL-MCE-001 a fortiori.
- **GOAL-MCE-001 is not in its declared binding scope.** The convention's own
  header enumerates `GOAL-HQC-001` and `GOAL-SDITH-001`. Extending a convention
  to a third goal is a Coordinator act, and it has not occurred.

### 4.5 Finding against BATCH-001-OPENING §5

BATCH-001-OPENING §5 states flatly:

> "This goal **binds to that convention and does not derive a competing one.**"

**That sentence is not currently supported.** The convention is not adopted,
and the program's standing decision forbids a peer goal from binding to it. The
supportable form is *"this goal intends to bind to ISD-FC-2026 once
DEC-20260802-344883 D-6's conditions are discharged and a Coordinator ledger
archive adopts it, and derives no competing convention in the meantime."*

The opening's own hedge in the next paragraph — *"Whether TASK-20260802-0100a5's
output is final is **not asserted here** … this Coordinator has not read that
convention artifact"* — was well placed, and directing this task to settle it
was the right call. It is now settled: **not final, not adopted, not available.**

**Consequential, and reported because it is a ledger defect rather than a
producer defect:** `RQ-MCE-e65b3c.constraints` instructs *"Bind to the costing
convention produced under GOAL-HQC-001 TASK-20260802-0100a5; do NOT derive a
competing one"*, and `ledger/goals/GOAL-MCE-001/goal.yaml` says *"this record
binds to their ISD costing convention"*. **Both instructions are currently
unexecutable.** GOAL-MCE-001's second completion criterion (a memory-charged
concrete ISD cost "under the convention shared with GOAL-HQC-001 and
GOAL-SDITH-001") is therefore **blocked on an upstream goal's unresolved
red-team objections**, not on anything BATCH-001 did or failed to do.

**This does not affect BATCH-001's admissibility.** Neither producer applied the
convention. `f3aece` stopped at parameters precisely so it would not, which
§5 correctly anticipated and which I confirm it did: no ISD cost, no memory
charge, and no cost figure of any kind appears in either producer's
deliverables. The batch's own design absorbed this risk correctly.

---

## 5. Named duty 4 — the PDF-vs-abstract endpoint distinction

The 292b99 producer reported a **sharper** result than the goal record
anticipated: that `eprint.iacr.org/archive/versions/2026/1232` is an **HTML**
endpoint that **also** 403s, making the block **path-scoped, not
format-scoped**.

**I re-tested all three endpoints. The claim reproduces.**

| Endpoint | Kind | Status (mine) | Producer |
|---|---|---:|---|
| `https://eprint.iacr.org/2026/1232` | HTML abstract | **200** (17323 B, hash MATCH) | A01: 200 |
| `https://eprint.iacr.org/2026/1232.pdf` | PDF | **403** | A02/A29: 403, challenge |
| `https://eprint.iacr.org/archive/versions/2026/1232` | **HTML** | **403** | A03: 403, challenge |

**Confirmed: an HTML endpoint on the same host is blocked while another HTML
endpoint is served.** "eprint HTML works" is not a correct generalisation, and
the producer is right that the correct statement is path-scoped. This is a
genuine improvement on both the goal record's and the batch opening's framing,
and it corrects the opening's §3 characterisation in the *stricter* direction.

**No deliverable generalises from one endpoint to another.** I checked
specifically:

- `attack_transcription.md` §0: *"These are reported separately and neither
  licenses a statement about the other."*
- `source_access_log.yaml` (292b99) `summary.endpoint_finding_reported_separately.explicit_non_generalisation`
  states the non-generalisation in both directions and adds the `/archive/`
  counterexample.
- `f3aece` deviation **D2** is the strongest form of this discipline: it
  declines to fire an unnecessary fallback and then states *"THIS TASK
  CONTRIBUTES NO NEW EVIDENCE about the eprint PDF endpoint; the separate
  question of that endpoint's 403 status is untouched by this task and must not
  be treated as tested here."* Correctly refusing to manufacture a data point.

Nothing in either producer's set generalises across endpoints. Duty 4 is
satisfied.

---

## 6. Named duty 5 — the damage and recall markers

### 6.1 `f3aece`: zero `[RECALLED-NOT-READ]` is **CORRECT**

I traced **every number** in `parameter_sets.md` to a re-fetched primary source
and found **no unsourced or silently recalled value**. The two textual
occurrences of each marker name in that file are negative declarations in §0/§4/§8
("markers set: 0"), not markers set.

| Numbers | Verified against | Result |
|---|---|---|
| All 10 `(m, n, t)` triples, §1 | SPEC §7.1–§7.10, re-fetched, `dcc68788…` | **10/10 exact** |
| `(µ,ν) = (32, 64)` at §7.2/7.4/7.6/7.8/7.10 only | SPEC §7 | exact |
| `k = n − mt` definition, §1 | SPEC §3 verbatim: *"A positive integer t ≥ 2 with mt < n. This also defines a parameter k = n − mt."* | exact |
| All of §2 (k, rates, gcds, decimals) | recomputed by me | **exact** (§3 above) |
| Categories `1,3,5,5,5` and `1,2,4,4,5`, §3 | SEC, re-fetched, `db17ef08…` | exact, both quotes verbatim |
| Size table, 40 cells, §4 | IMPL Table 1, re-fetched, `86225992…` | **40/40 exact** |
| Size formulas, §5 | SPEC §6.2 verbatim | exact |
| `ℓ = 256`, §6 | SPEC §6.1 verbatim: *"The integer ℓ is 256."* | exact |
| PC delta quotes, §6 | PC, re-fetched, `9894108c…` | substance exact (see Q2) |
| NIST IR 8545 passage | `d802f484…`, re-fetched | **exact**, full paragraph |
| iso.html quotes + 16-set list | `cc73020d…`, re-fetched | **exact** |

**The `"respectively"` resolution in §3 is the one real inference in the
document, and it holds.** I verified all three of its supports independently:

1. SEC Table 1's row order is `348864, 460896, 6688128, 6960119, 8192128`
   (each × three `mem` models) — confirmed by reading the re-fetched table.
2. *"One can object to the assignment of 460896 to "Category 3" (AES-192)"* —
   explicit, pins position 2. Confirmed verbatim.
3. *"the submission has always assigned this parameter set to NIST's "Category
   5" (AES-256)"* — I traced the antecedent of *"this parameter set"* back
   1900 characters to *"The Classic McEliece submission has always included the
   **6960119** parameter set"*. **The antecedent is 6960119**, so this pins
   position 4. Confirmed.

**A control the producer did not run, which I ran, and which holds.** SEC Table 1's
`mem = 0` rows independently corroborate the free-memory column `1,2,4,4,5`:
348864 ≈ 2¹⁴⁰⁻¹⁴³, 460896 ≈ 2¹⁸⁰ (< 2²⁰⁷ = AES-192 ⇒ cat 2), 6688128 and
6960119 ≈ 2²⁴⁵⁻²⁴⁹ (< 2²⁷² = AES-256 ⇒ cat 4), 8192128 ≈ 2²⁷⁵⁻²⁸¹ (⇒ cat 5).
The transcribed column is consistent with the table it sits beside.

I also confirm the producer's negative claims about source *scope*, which are
checkable and were checked: SPEC contains **no** occurrence of `categor*` and
**no** byte sizes; SEC contains no byte sizes; the submission overview contains
the delegating sentences *"See the separate "guide for security reviewers"
document"* and *"See the separate "guide for implementors" document"*. The
producer's claim that SEC and IMPL are *the specification's own designated
sources* rather than substitutions of its choosing is therefore **correct**.

Observation **O3** is confirmed and is materially important: the re-fetched ISO
list contains **16** sets and **no `mceliece348864` variant** — the set carrying
the lowest claimed category. Any later use of the phrase "the standardized
parameter sets" must say which set it means.

### 6.2 `292b99`: the markers sit where extraction genuinely fails

I re-extracted `distingueur.pdf` (`b69f8256…`, byte-identical) with
`pdfminer.six` myself and compared against each marked site.

| Marked site | My independent extraction | Marker correct? |
|---|---|---|
| Eq. (92), Theorem 3 | Reproduces the producer's raw block: `(cid:16) ω R2 / 1−R +o(1) (cid:17) …` with `κ = q` emitted **after** its own exponent. Superscript grouping genuinely unrecoverable. | **YES** |
| Example 2, κ row | Extraction yields exactly `2528`, `(21080)`, `(21224)`, `21030`, `2997`. These are flattened `2^528`, `(2^1080)`, `(2^1224)`, `2^1030`, `2^997`. | **YES — and the refusal to transcribe them is the right call** |
| Heuristic 1, parts 1–2 formulas | `(cid:0)k+1 (cid:1)`, `(cid:16) k(k+1) r − n (cid:17) (cid:0)k−1 r−2 (cid:1)` — binomial delimiters unmapped, operand placement unrecoverable. Surrounding **prose is clean**, exactly as the producer says. | **YES** |
| Condition (6), `arXiv:2304.14757` | Not reconstructed by the producer. | **YES** (correctly refused) |

The Example 2 κ row is the single most important marker in the batch: those are
exactly the flattened-exponent values whose mis-transcription cost GOAL-HQC-001
BATCH-001 50.7 bits at NIST-5. **The producer identified the correct reading,
labelled it a reconstruction, refused to transcribe it, and carried no κ value
into any deliverable.** That is the behaviour the contract requires.

**Positive cross-producer control neither producer claimed.** The `(n, m, t)`
row the 292b99 producer transcribed *from a third party* (KN-LIT-71d1a0's
Example 2) — `(3488,12,64)`, `(4608,13,96)`, `(6688,13,128)`, `(6960,13,119)`,
`(8192,13,128)` — **agrees exactly** with the triples `f3aece` transcribed from
the specification itself. Two independent producers, two independent documents,
two independent extractions, same ten numbers. 292b99 was right to warn *"Do not
use this row as a parameter source"*, and it is nonetheless a genuine
corroboration of the parameter transcription.

**Verbatim spot-checks against re-fetched sources, all exact:** the full
`iacr:2026/1232` abstract; the authors' revision `Note:` **character-for-character
including the unbalanced quote, the French guillemets, and the `\xa0`
non-breaking spaces** (the producer's parenthetical that these are the source's
and not a transcription artefact is **correct** — I checked the un-rendered
HTML); the bibliographic header, Category, Keywords, History `2026-06-12:
revised / 2026-06-10: received`, Short URL, License; *"Now, under Heuristic 1,
we have:"*; Theorem 3's statement; *"where ω ≈ 2.372 is the exponent of linear
algebra"*; Example 2's caption and all six non-κ rows; the paper's commentary
including its own spelling `"unreacheable"`.

**Machine-checked negative control.** `rate_regime_extraction.md` §1.3 asserts
that no occurrence of "rate", "high rate", "R =", "k/n", or any inequality
appears in the primary abstract. I ran that check on the re-fetched abstract:
`rate` → none; `high rate` → none; `k/n` → none; `genus` → none; `[<>≤≥]` →
none. The single `R\s*=` hit is `r=9`, the CFS Goppa-polynomial degree — which
the producer's own scope table already classifies as *"a demonstrated CFS
instance, not as a restriction"*. **The negative claim is accurate**, and §1.1's
refusal to treat the absence of a rate condition in a 235-word abstract as
evidence about the body is the correct epistemic posture.

---

## 7. Qualifications

**Q1 — undisclosed hash instability at three endpoints.** §2.4. Affects log
schema, no number. Not a defect in any conclusion.

**Q2 — `f3aece` silently glyph-normalised material presented as `verbatim`,
while declaring zero extraction-damage markers.** The re-fetched PDFs render
`ℓ` as `(cid:96)` and `⌈ ⌉` as `(cid:100)/(cid:101)`, and PC's ciphertext
sentence extracts as `"A ciphertext C has two components: C0 ∈ Fmt 2. …"` with
the superscripts and the `and C1 ∈ F₂^ℓ` clause dislocated by the layout. The
producer's quotation restores all of this to `C0 ∈ F2^mt and C1 ∈ F2^ℓ` and
`⌈mt/8⌉`, presents it inside a verbatim block, and then states
*"`[EXTRACTION-DAMAGED]` markers set: **0**"*.

The normalisation is **unambiguous and correct** — I confirmed the restored
reading against PC's Decap step, which extracts as *"Split the ciphertext C as
(C0, C1) with C0 ∈ Fmt 2 and C1 ∈ F(cid:96) 2"* — and **no number is affected**.
But it is an undisclosed editorial step inside a block labelled verbatim, and it
sits beside a zero-damage declaration. The contrast with 292b99 is instructive:
that producer left raw `(cid:NN)` tokens visible and marked them. **The two
producers in one batch applied different disclosure standards to the same class
of extraction artifact.** Recommend the batch adopt 292b99's standard.

**Q3 — one `verbatim` quote carries a transcriber's punctuation.**
`parameter_sets.md` §1 presents *"7.7 Parameter set mceliece6960119 — KEM with
m = 13, …"*. The source has a section heading followed by body text; the em-dash
is the transcriber's join. Cosmetic; substance exact.

**Q4 — the `292b99` "raw extraction, unedited" blocks are
extractor-settings-dependent.** The producer's raw blocks are more
column-aligned than my default-`pdfminer.six` output, implying different
`laparams`. The *tokens* are identical and no claim depends on the layout, but
"raw and unedited" is only reproducible if the extraction settings are recorded,
and they are not.

**Q5 — observation O1 is real but is already officially recorded upstream.**
The producer flagged NIST reachability (`csrc.nist.gov` 200, `www.nist.gov` 200,
`nvlpubs` 200) as `severity: material_to_other_records` and recommended a
Coordinator/Validator re-probe. **I re-probed: all three reproduce.** However,
`DEC-20260802-344883` decision **D-5** already records exactly this for
GOAL-HQC-001 — *"THE CSRC.NIST.GOV HALF STANDS AND HAS CROSS-GOAL CONSEQUENCES …
RQ-HQC-001 is immutable and is superseded on this point … a recorded
source-access blocker in this program is STALE"*. O1 therefore **corroborates an
existing official decision** rather than raising a new one, and the producer's
recommended follow-up is largely already discharged. The producer's careful
refusal to claim the earlier record was *wrong when written* is correct and
matches D-5's own handling.

---

## 8. What I did not check

- The mathematical significance of the attack, of the syzygy distinguisher, or
  of any rate threshold. Excluded by the task card and outside this role.
- BATCH-001-OPENING §9's claim of 110 `validate_ledger.py` errors on both this
  branch and `origin/main`, and §2's corpus census (169 / 137 / 0-read). Those
  are framing claims assigned to the red team, `TASK-20260803-08e883`.
- The producers' un-hashed or infrastructure-failed attempts (`A06`–`A10`,
  `A15`, `A17`–`A20`, `A22`, `A23`, `A26`–`A28`, `D02`), beyond confirming the
  classification pattern on representatives of each class.
- Whether ISO's own text says what `iso.html` says. `iso.org` returned 403 for
  me as it did for the producer; **the ISO designation number remains not
  obtained**, and the producer's `confidence: reported` framing is correct and
  should be preserved downstream.
- Whether NIST has acted since IR 8545 (March 2025). Not established by anyone.

---

## 9. Required output record

```yaml
validation_report:
  id: VAL-20260803-409c5e
  task_id: TASK-20260803-409c5e
  run_ids: [TASK-20260803-292b99, TASK-20260803-f3aece]
  snapshots_validated:
    - {task: TASK-20260803-9fddc2, commit: 6787c6e4, parent: 6b4c09dc, paths: 6, hashes_reproduced: 5/5}
    - {task: TASK-20260803-f3beb0, commit: 4d801d94, parent: 6787c6e4, paths: 5, hashes_reproduced: 4/4}
  artifact_checks:
    - {check: snapshot_reachable_from_head, result: pass}
    - {check: declared_paths_equal_actual_commit_paths, result: pass}
    - {check: recorded_path_sha256_vs_committed_blobs, result: pass, n: 9}
    - {check: working_tree_clean, result: pass}
  source_reacquisition:
    attempted: 26
    sha256_match: 25
    not_reproducible_by_construction: 5
    unexplained_mismatch: 0
    fabrication_detected: 0
    load_bearing_documents_byte_identical:
      [mceliece-spec-20221023.pdf, mceliece-security-20221023.pdf,
       mceliece-impl-20221023.pdf, mceliece-pc-20221023.pdf,
       NIST.IR.8545.pdf, iso.html, nist.html, spec.html,
       eprint 2026/1232 abstract, distingueur.pdf, arXiv 2304.14757 pdf]
    nonreproducible_causes:
      - {src: 292b99/A11, cause: oai_pmh_responseDate_timestamp, bytes_stable: true, content_identical_after_normalisation: true}
      - {src: 292b99/D01, cause: anubis_proof_of_work_interstitial_under_http_200, flagged_by_producer: true}
      - {src: f3aece/seq10, cause: cloudflare_email_obfuscation_per_response_key, bytes_stable: true, flagged_by_producer: false}
      - {src: f3aece/seq13, cause: cloudflare_email_obfuscation_per_response_key, bytes_stable: true, flagged_by_producer: false}
      - {src: f3aece/seq16, cause: cloudflare_managed_challenge_nonce, bytes_stable: true, status_403_reproduced: true, flagged_by_producer: false}
  metric_recomputations:
    - {metric: k_eq_n_minus_mt, sets: 5, method: exact_integer, result: 5/5 match}
    - {metric: rate_k_over_n_lowest_terms, sets: 5, method: fractions.Fraction+math.gcd, result: 5/5 match}
    - {metric: rate_decimal_6dp, sets: 5, result: 5/5 match}
    - {metric: mutual_consistency_m_n_t_k_and_mt_lt_n, sets: 5, result: 5/5 hold}
    - {metric: public_key_size_mt_ceil_k_over_8, sets: 5, result: 5/5 match IMPL Table 1}
    - {metric: ciphertext_size_ceil_mt_over_8, sets: 5, result: 5/5 match IMPL Table 1}
    - {metric: producer_size_control, claimed: 10/10, independently_confirmed: 10/10}
    - {metric: impl_table_1_all_cells, cells: 40, result: 40/40 match}
    - {metric: pc_ciphertext_delta_ceil_l_over_8, value: 32, result: match, provenance: computed_not_transcribed}
    - {metric: primality_of_5413, result: prime, producer_prose_error_confirmed_and_confirmed_corrected: true}
  control_checks:
    - {control: spec_triples_reread_from_refetched_pdf, result: 10/10 exact}
    - {control: respectively_ordering_pinned_by_sec_table1_rowsheet, result: confirmed}
    - {control: antecedent_trace_of_this_parameter_set_to_6960119, result: confirmed}
    - {control: free_memory_column_1_2_4_4_5_vs_sec_table1_mem0_rows, result: consistent, note: validator-run, not producer-run}
    - {control: cross_producer_triple_agreement_kn_lit_71d1a0_vs_spec, result: exact agreement, note: independent corroboration}
    - {control: negative_control_no_rate_condition_in_abstract, result: confirmed by regex on refetched abstract}
    - {control: extraction_damage_markers_reproduced_independently, sites: 4, result: 4/4 correctly placed}
    - {control: recalled_not_read_markers_zero_for_f3aece, result: correct, every number traced to a refetched source}
    - {control: endpoint_non_generalisation, result: honoured by both producers}
  endpoint_findings:
    - {url: 'eprint.iacr.org/2026/1232', kind: html_abstract, status: 200, hash_match: true}
    - {url: 'eprint.iacr.org/2026/1232.pdf', kind: pdf, status: 403}
    - {url: 'eprint.iacr.org/archive/versions/2026/1232', kind: html, status: 403}
    conclusion: >-
      Producer claim CONFIRMED. The block is path-scoped, not format-scoped: an
      HTML endpoint on the same host is blocked while another HTML endpoint is
      served. Sharper and stricter than BATCH-001-OPENING section 3.
  isd_convention_status:
    artifact_exists: true
    path: coordination/goals/GOAL-HQC-001/batches/BATCH-001/tasks/TASK-20260802-0100a5/
    name: ISD-FC-2026
    version: 1
    snapshot_commit: e6f20223
    independently_reviewed: true
    reviews: [TASK-20260802-b8d69f, TASK-20260802-73a352]
    is_final: false
    is_adopted: false
    adoption_blocker: DEC-20260802-344883 D-6 (red-team objections O6 and O7 unresolved)
    scheme_independent: true
    scheme_independence_independently_verified: true
    scheme_independence_basis: DEC-20260802-344883 D-6 note — gate held under exhaustive integer enumeration
    declared_binding_scope: [GOAL-HQC-001, GOAL-SDITH-001]
    goal_mce_001_in_binding_scope: false
    binding_available_to_goal_mce_001: false
    finding_against_opening: >-
      BATCH-001-OPENING section 5's sentence "This goal binds to that convention
      and does not derive a competing one" is NOT currently supported. The
      convention is not adopted and GOAL-HQC-001's own next_action forbids the
      peer goal GOAL-SDITH-001 from binding to it in its current state.
    consequential_ledger_defect: >-
      RQ-MCE-e65b3c.constraints and ledger/goals/GOAL-MCE-001/goal.yaml both
      instruct binding to an unadopted convention. Both instructions are
      currently unexecutable. GOAL-MCE-001's second completion criterion is
      blocked upstream. This is a ledger defect, not a producer defect, and it
      does not affect BATCH-001's admissibility because neither producer applied
      the convention or reported any cost figure.
  heuristic_validation_checks:
    - {check: not_applicable, reason: "BATCH-001 validates no heuristic, runs no sampler, and pre-registers no distribution. It is a transcription batch."}
    - {check: primary_target_heuristics_obtained, result: 0, classification: infrastructure_error_not_negative_observation, correct: true}
  cost_model_checks:
    - {check: not_applicable, reason: "No cost table, no cost unit, no per-attempt-cost x inverse-success-probability claim appears in any BATCH-001 deliverable. Confirmed by inspection of all nine artifacts."}
    - {check: comparison_html_isd_estimates_recorded_as_pointer_only, result: correct, note: "O2 logs primary CryptAttackTester figures as a location pointer and explicitly asserts nothing about their cost model."}
  proof_architecture_checks:
    - {check: not_applicable, reason: "No proof, boundary parameter, strictness witness, or reduction arrow is claimed in this batch."}
  verdict: passed
  verdict_label: ADMIT_WITH_QUALIFICATIONS
  qualifications: [Q1, Q2, Q3, Q4, Q5]
  limitations:
    - >-
      Single-model review. requested_policy review-adversarial did not resolve;
      fallback_used true; resolved_model_id claude-opus-5, identical to both
      producers and the Coordinator. NOT admissible toward an AGENTS.md rule 13
      quorum; no attestation may be synthesized from this report.
    - >-
      xhigh reasoning effort could not be verified; model_verified false (no
      adapter doctor --probe run).
    - >-
      Five recorded hashes are non-reproducible by construction. Their causes
      were established mechanically, but their exact recorded bytes cannot be
      re-verified by anyone, ever. Status codes and byte counts did reproduce.
    - >-
      ISO's own text was not read by the producer or by me; iso.org returned 403
      to both. The ISO standardization event rests on a single interested party
      and must stay at confidence "reported".
    - >-
      The primary target's body (iacr:2026/1232) was not obtained by the
      producer and I did not attempt to obtain it. Everything about that paper
      in this batch is abstract-level. Its numbered heuristics remain unread.
    - >-
      B01 (distingueur.pdf) is the author's 2025-05-02 copy, not necessarily the
      latest of the 4 ePrint revisions. C02 carried no version suffix. Both
      version caveats are the producer's and both are correct.
    - >-
      No bot-protection challenge was circumvented or attempted, by the
      producers or by me.
  artifact_paths:
    - coordination/goals/GOAL-MCE-001/batches/BATCH-001/reviews/TASK-20260803-409c5e/validation_report.md
```

---

## 10. Bottom line for the Coordinator

**Admit both producer packages as evidence of transcription.** The snapshots are
sound, 25 of 30 recorded hashes reproduce exactly and the other 5 fail for
established structural reasons that are nobody's fault, the rate arithmetic is
independently correct in exact rationals, the size-formula control genuinely
holds at 10/10, and every verbatim block I sampled matched its re-fetched source
character-for-character. The `[EXTRACTION-DAMAGED]` markers sit exactly where
extraction fails, and the refusal to transcribe the flattened κ row is the
single best decision in the batch.

**Correct BATCH-001-OPENING §5 before the ledger archive.** `ISD-FC-2026`
exists, is complete, is reviewed, and is genuinely scheme-independent — but it
is **`proposed`, explicitly NOT ADOPTED** per `DEC-20260802-344883` D-6, its
binding scope does not name GOAL-MCE-001, and GOAL-HQC-001's own `next_action`
forbids the peer goal GOAL-SDITH-001 from binding to it in its current state.
`RQ-MCE-e65b3c.constraints` and `GOAL-MCE-001/goal.yaml` both instruct an act
that cannot currently be performed. Nothing in BATCH-001 depends on it — that is
the batch's own design working — but the goal's second completion criterion is
blocked upstream and the ledger records should say so rather than assert a
binding that does not exist.

**Adopt 292b99's extraction-disclosure standard batch-wide** (Q2), and record a
`hash_stable` axis in the source-access log schema (Q1).
