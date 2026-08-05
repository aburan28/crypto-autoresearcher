# Classic McEliece standardization status — what primary text establishes

**Task:** TASK-20260803-f3aece · **Goal:** GOAL-MCE-001 · **Batch:** BATCH-001
**Question:** RQ-MCE-e65b3c · **Date:** 2026-08-03
**Role:** executor · `requested_policy: executor-implementation` ·
`resolved_model_id: claude-opus-5` · `fallback_used: true`

> Named duty 2 of this task: GOAL-MCE-001 marks `standardization_status` as
> **UNVERIFIED** and infers an ISO track plus NIST non-selection from *the mere
> existence* of "NIST" and "ISO" pages at classic.mceliece.org — pages that were
> never fetched. This document does not restate that inference. It reports what
> two fetched primary documents say, and marks the rest open.

**Bottom line: the question is SETTLED on the NIST side against NIST's own
text, and settled on the ISO side against the designers' text with one named
residual gap (no ISO designation number, ISO's own catalogue unreachable).**

---

## 1. Routes tried

Full log with statuses, byte counts and sha256: `source_access_log.yaml`.

| Route | URL | Status | Outcome |
|---|---|---|---|
| R1 | `https://classic.mceliece.org/` | 200 | Yielded real paths (nist.html, iso.html, spec.html) |
| R2 | `https://classic.mceliece.org/nist.html` | 200 | Designers' NIST page, v2026.06.23 |
| R3 | `https://classic.mceliece.org/iso.html` | 200 | Designers' ISO page, v2026.06.15 |
| R7 | `https://csrc.nist.gov/projects/post-quantum-cryptography` | **200** | Reachable — contrary to expectation |
| R7 | `https://www.nist.gov/` | **200** | Reachable |
| R7 | `https://csrc.nist.gov/pubs/ir/8545/final` | 200 | Landing page for NIST IR 8545 |
| R7 | `https://nvlpubs.nist.gov/nistpubs/ir/2025/NIST.IR.8545.pdf` | 200 | **NIST IR 8545, 34 pp — the authoritative document** |
| R8 | `https://www.iso.org/standard/detail` | **403** | Blocked |
| R8 | `https://www.iso.org/search.html?q=McEliece` | **403** | Blocked |

**A note on R7 that matters beyond this task.** The task card and
`RQ-HQC-001.provenance` record csrc.nist.gov and nist.gov as UNREACHABLE from
this harness (proxy CONNECT 403). Today they returned 200, and nvlpubs.nist.gov
served a 589 KB PDF. That is recorded as observation O1 in the access log.

It is a reachability measurement at one moment from one harness. It is **not**
a finding that the earlier record was wrong when written — proxy and host
behaviour both change, and the two observations may simply be at different
times. GOAL-HQC-001 BATCH-001's red team had to correct a Coordinator claim of
exactly the shape *"the blocker did not reproduce"*; this document declines to
make the mirror-image error. It also says nothing whatever about
eprint.iacr.org's PDF endpoint, which **this task never tested** (deviation D2).

**iso.org was not circumvented.** Two endpoints, two 403s, consistent with bot
protection. Per the task constraint and AGENTS.md rule 5, that is a recorded
outcome and never evidence about ISO's actual actions.

---

## 2. NIST: settled, from NIST's own publication

**Source:** NIST IR 8545, *"Status Report on the Fourth Round of the NIST
Post-Quantum Cryptography Standardization Process"*, March 2025, 34 pp.,
DOI `10.6028/NIST.IR.8545`, sha256 `d802f484…`. Authors as printed on the title
page include Alagic, Bros, Ciadoux, Cooper, Dang, Dang, Kelsey, Lichtinger,
Liu, Miller, Moody, Peralta, Perlner, Robinson, Silberg, Smith-Tone, Waller.

Verbatim, from the report's discussion of Classic McEliece:

> *"In IR 8413 [2], NIST requested feedback on specific use cases for which
> Classic McEliece would be a good solution. Responses noted that Classic
> McEliece may provide better performance than BIKE or HQC for applications in
> which a public key can be transferred once and then used for several
> encapsulations (e.g., file encryption and virtual private networks [VPNs]) due
> to its small ciphertext size and fast encapsulation and decapsulation. There
> was also some interest in Classic McEliece based on the perception that it is
> a conservative choice. However, the interest expressed in Classic McEliece was
> limited, and having more standards to implement adds complexity to protocols
> and PQC migration.*
>
> *Classic McEliece is currently under consideration for standardization by the
> International Organization for Standardization (ISO). Concurrent
> standardization of Classic McEliece by NIST and ISO risks the creation of
> incompatible standards. After the ISO standardization process has been
> completed, NIST may consider developing a standard for Classic McEliece based
> on the ISO standard. However, Classic McEliece is no longer under
> consideration for standardization as part of the current NIST PQC
> Standardization Process."*

**Established:**

1. Classic McEliece **is not** a NIST-standardized algorithm and, as of March
   2025, **is no longer under consideration** in the current NIST PQC process.
2. NIST's stated reasons are (a) limited expressed interest plus added
   migration complexity, and (b) incompatibility risk from concurrent
   NIST/ISO standardization — **not** a security finding. The report gives no
   security-based reason for the non-selection.
3. NIST leaves an explicit future door open: it *"may consider developing a
   standard … based on the ISO standard"* after ISO completes.

**Not established, and deliberately not inferred:** nothing here says Classic
McEliece was "rejected", "broken", "found weak", or "failed". Reading NIST's
non-selection as a security judgement would be an overread of this text, which
supplies the opposite explanation.

The designers' own page (R2, v2026.06.23) quotes the same two sentences and
characterises the event as *"In 2025, NIST delayed McEliece standardization"*.
The designers' framing ("delayed") is their word; NIST's text is the primary
statement and is quoted above in full for that reason.

> The goal record's field `nist_track: not_selected` is **consistent** with NIST
> IR 8545. It is now corroborated by primary text rather than inferred from the
> existence of a web page. The word "delayed" vs "not selected" should be
> attributed carefully: NIST says "no longer under consideration … as part of
> the current … Process" while allowing a future ISO-based standard.

---

## 3. ISO: settled as to the fact, open as to the designation

**Source:** `https://classic.mceliece.org/iso.html`, page version **2026.06.15**,
sha256 `cc73020d…`. This is the **designers'** page, not ISO's.

Verbatim opening:

> *"ISO standardized Classic McEliece in June 2026. The ISO standard is
> compatible with the official specification from the Classic McEliece team."*

The page then lists the parameter sets in the ISO standard, verbatim:

> mceliece460896, mceliece460896f, mceliece460896pc, mceliece460896pcf,
> mceliece6688128, mceliece6688128f, mceliece6688128pc, mceliece6688128pcf,
> mceliece6960119, mceliece6960119f, mceliece6960119pc, mceliece6960119pcf,
> mceliece8192128, mceliece8192128f, mceliece8192128pc, mceliece8192128pcf

and adds: *"The Classic McEliece team recommends the mceliece6* sizes for
long-term security."*

Its "History" section states that the team published a draft
`iso-mceliece-20230419.pdf`; that ISO asked for at least 128 bits of security in
a quantum model assuming a Grover square-root speedup; that the draft
*"specified only the mceliece6* and mceliece8* parameter sets"*; and that
*"ISO decided to also standardize mceliece4*."*

### 3.1 Three things this establishes

1. **Sixteen parameter sets are in the ISO standard**, per the designers.
2. **No mceliece348864 variant is in the ISO standard.** The 3488 family is
   absent from the list entirely. This is significant for GOAL-MCE-001: the
   phrase *"the standardized parameter sets"* excludes 348864, which is exactly
   the set carrying the lowest claimed category and the subject of both
   attack-claim notes on the designers' NIST page. Any deliverable using that
   phrase must say which set it means. Recorded as observation O3.
3. **The ISO standard is claimed compatible with the fetched specification**,
   which is what licenses using SPEC's (m, n, t) — and therefore the rates in
   `parameter_sets.md` — for the ISO sets.

### 3.2 What remains OPEN, explicitly

| Open item | Why |
|---|---|
| **The ISO standard's designation number** (e.g. an ISO/IEC number and part) | The designers' page never states it. iso.org 403'd on both attempts. **Not obtained.** |
| **ISO's own text**, for any purpose | Never read. Everything in §3 is the *designers'* assertion about ISO. |
| **Publication date / edition / status** beyond "June 2026" | Not stated on the page beyond the month. |
| Whether NIST has acted on its "may consider" since March 2025 | Not established. IR 8545 is March 2025; the ISO event is claimed June 2026, i.e. **after** the NIST report. No NIST document later than IR 8545 was fetched. |

The last row is a real limitation and is stated rather than smoothed over: NIST
IR 8545 describes ISO standardization as *"currently under consideration"* and
conditions a possible NIST standard on ISO *completing*. The designers say ISO
completed in June 2026. This task did **not** establish what, if anything, NIST
has done in the fourteen months since.

### 3.3 Confidence, stated honestly

The ISO fact rests on a **single source that is a party to it**. The designers
are the most-informed party and their site is versioned, specific (a 16-item
list, a month, a compatibility claim, a documented drafting history including
ISO overruling their draft on mceliece4*), and internally consistent with NIST
IR 8545's independent March-2025 statement that ISO standardization was then
under way. Those are reasons to take it seriously. They are **not** a second
independent source, and it is not upgraded to one here.

Recommended designation under `knowledge/SEEDING.md`'s axes for any record
built on this: `confidence: reported`, `citation_verified: read` for the
designers' page as a page; the ISO standardization *event* should be recorded
as **reported by the design team, unconfirmed against ISO**.

---

## 4. Answer to the goal record's UNVERIFIED field

`GOAL-MCE-001.scheme_context.standardization_status` currently reads, in part:
*"The Classic McEliece project site lists both a 'NIST' and an 'ISO' page, from
which this record infers an ISO track and non-selection by NIST. Neither page
was fetched."*

Both pages have now been fetched, and NIST's own report as well. Proposed
replacement text — **proposed only**; this task does not edit the goal record,
which is outside its write scope and is the Coordinator's alone:

> Classic McEliece is **not** a NIST-standardized algorithm. NIST IR 8545
> (March 2025, DOI 10.6028/NIST.IR.8545) states that it *"is no longer under
> consideration for standardization as part of the current NIST PQC
> Standardization Process"*, citing limited expressed interest, added migration
> complexity, and incompatibility risk from concurrent NIST/ISO
> standardization — **no security reason is given** — while stating NIST *"may
> consider developing a standard … based on the ISO standard"* after ISO
> completes. The Classic McEliece team's ISO page (v2026.06.15) states that
> *"ISO standardized Classic McEliece in June 2026"* and lists **16** parameter
> sets, **excluding every mceliece348864 variant**. The ISO claim is **reported
> by the design team and unconfirmed against ISO's own text**: iso.org returned
> HTTP 403 on two attempts and the standard's designation number was not
> obtained. Verified 2026-08-03 by TASK-20260803-f3aece.

Two cautions for whoever adopts it:

- The inference *"Classic McEliece is the conservative code-based KEM the NIST
  process did not select, which makes its parameters durable rather than
  provisional"* (RQ-MCE-e65b3c.scope.standardization_status) is **not**
  established by anything fetched here. NIST IR 8545 supports "did not select"
  and supports that the reason was not security; it says nothing about
  durability. "Durable rather than provisional" remains an unverified editorial
  judgement.
- ISO's inclusion of `pc` and `pcf` sets means the standardized algorithm set is
  **not** identical to SPEC §7's ten selected sets. See `parameter_sets.md` §6.

---

## 5. Marker summary

- `[RECALLED-NOT-READ]`: **0**. Every quotation above is from a document
  fetched today with a recorded sha256.
- `[EXTRACTION-DAMAGED]`: **0**. The NIST IR 8545 passage is running prose and
  extracted cleanly; the ISO list is an HTML list.
- Blocked routes recorded as outcomes, not evidence: iso.org ×2 (403).
