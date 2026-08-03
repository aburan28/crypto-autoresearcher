# PROPOSED correction to `RQ-MCE-e65b3c` — TASK-20260803-a53f73

**Task:** TASK-20260803-a53f73 · **Goal:** GOAL-MCE-001 · **Batch:** BATCH-002
**Role:** executor · **Date:** 2026-08-03
**Requested policy:** `executor-implementation` · **Resolved model:** `claude-opus-5` ·
**fallback_used:** `true`

> **PROPOSED ONLY. `ledger/questions/RQ-MCE-e65b3c.yaml` WAS NOT MODIFIED BY
> THIS TASK.** Writing it is `TASK-20260803-3aa684`'s act, and only after both
> BATCH-002 reviews accept.

---

## 1. The defective constraint, quoted exactly as it stands

`ledger/questions/RQ-MCE-e65b3c.yaml`, `research_question.constraints`, fifth
item (lines 142–146 at HEAD `2ea6216d`):

```yaml
    - >-
      Rate-scoping is load-bearing, not decoration. KN-LIT-4c8135 is
      polynomial-time key recovery for HIGH-RATE random alternant codes; the
      threshold is the practically decisive number and no deliverable may
      state the headline without it.
```

## 2. What is wrong with it, and what is right with it

**Right, and kept:** *"Rate-scoping is load-bearing, not decoration"*, and
*"KN-LIT-4c8135 is polynomial-time key recovery for HIGH-RATE random alternant
codes"*. `arXiv:2304.14757` does carry a high-rate condition — its numbered
condition (6) — and the constraint's instinct that a headline must not be stated
without its scope is the correct instinct, correctly applied to the wrong scope.

**Wrong:** *"the threshold is the practically decisive number"*. The paper
carries a **code-family exclusion** alongside the rate condition, and Classic
McEliece uses binary Goppa codes. The paper's own sentence, transcribed from full
text at sha256 `ebbd94ac…c564b8` by `TASK-20260803-292b99`
(`rate_regime_extraction.md` §3.3) and recorded as `EV-MCE-332f99` O-5:

> "Interestingly our attack does not work at all when the alternant code has the
> additional structure of being a Goppa code."

Its Table 1 carries the same restriction parenthetically: *"(does not apply in
the particular case of Goppa codes)"*, and §3.2 is headed *"What is wrong with
Goppa codes?"*.

`DEC-20260803-a5b9b1` D-2 retracts the parent framing: *"RETRACTED — 'the rate
threshold is the whole question' … Falsified by this batch's own primary text …
The decisive restriction is the CODE FAMILY."* D-4 upholds the same defect in
`KN-LIT-4c8135` itself. The red team's finding (`red_team_report.md` §6a) quotes
this constraint by name as one of the three places the defect propagated to.

**The correction is NOT "the rate does not matter."** It is: the restriction has
three conjuncts and naming only one of them as decisive is the error. A
replacement that leads with the exclusion while deleting the rate scoping trades
one wrong constraint for another.

## 3. PROPOSED REPLACEMENT TEXT

Replace the single constraint item quoted in §1 with the two items below. Two
items rather than one, because the constraint was doing two jobs — stating a
general discipline and stating a fact about one paper — and the fact was wrong
while the discipline was right.

```yaml
    - >-
      SCOPE IS MULTI-AXIS. A restricted result is restricted on every axis its
      source states, and no deliverable may name one axis as the decisive one
      unless the source does. When recording a restricted result, enumerate
      every conjunct of the restriction and say explicitly which conjuncts this
      program has NOT obtained. A single-axis summary of a multi-axis
      restriction is the failure recorded as DEC-20260803-a5b9b1 D-2 and D-4.
    - >-
      KN-LIT-c4c2ac (superseding KN-LIT-4c8135; arXiv:2304.14757) is
      polynomial-time key recovery under THREE stated conjuncts, not one, and
      no deliverable may quote any of them alone: (1) CODE FAMILY -- generic
      alternant codes, and the paper states VERBATIM that its attack "does not
      work at all when the alternant code has the additional structure of being
      a Goppa code", with Table 1 carrying "(does not apply in the particular
      case of Goppa codes)"; (2) FIELD SIZE -- q in {2,3}; (3) RATE -- a high
      rate condition, the paper's numbered condition (6). Classic McEliece uses
      binary Goppa codes; this record states that adjacency and draws no
      consequence from it in either direction. Condition (6) is
      [EXTRACTION-DAMAGED] and NOT transcribed, so the numeric rate threshold is
      still not held by this program -- now as a recorded extraction failure
      rather than an unattempted read. Source: EV-MCE-332f99 O-5, from full text
      at sha256 ebbd94ac3cd00b0f0e723aeab56fd3b0820c89d47072fc8241f12c5f93c564b8,
      re-acquired byte-identically by TASK-20260803-409c5e.
```

**Hedging check.** Every quoted phrase above is the paper's own sentence at the
paper's own level. Nothing strengthens the exclusion into a statement about
Classic McEliece's security, and nothing softens it into a preference. The
paper's *"does not work at all"* is reproduced exactly, neither hardened into
"cannot work" nor weakened into "is not known to work".

## 4. HOW THE CORRECTION IS RECORDED — a form question the Coordinator must settle

`AGENTS.md` rule 4 says results are immutable and corrections create new records;
`knowledge/README.md` says the same for the corpus. But
`DEC-20260803-a5b9b1.next_actions` directs the correction into
`RQ-MCE-e65b3c.constraints` in place, and `TASK-20260803-3aa684`'s `write_scope`
grants write access to `ledger/questions/RQ-MCE-e65b3c.yaml`. **A research
question is not an evidence or run record, and the dispatch queue treats it as
amendable.** This task follows the dispatch queue.

**To keep the amendment non-destructive, the old text must survive inside the
record.** Proposed: add a `corrections` block to `research_question`, so a reader
of the RQ sees what it used to say and why it changed without leaving the file.

```yaml
  corrections:
    - id: RQ-CORR-001
      applied_at: '2026-08-03'
      applied_by: TASK-20260803-3aa684
      authority: DEC-20260803-a5b9b1 D-2, D-4
      field: constraints
      superseded_text: >-
        Rate-scoping is load-bearing, not decoration. KN-LIT-4c8135 is
        polynomial-time key recovery for HIGH-RATE random alternant codes; the
        threshold is the practically decisive number and no deliverable may
        state the headline without it.
      why: >-
        "the threshold is the practically decisive number" is falsified by
        EV-MCE-332f99 O-5. arXiv:2304.14757 carries a CODE-FAMILY EXCLUSION
        alongside its rate condition, and Classic McEliece uses binary Goppa
        codes. The rate condition is real and is retained in the replacement;
        what is retracted is the claim that it is the decisive one.
      replaced_by: the two constraint items added in this correction
```

If the Coordinator prefers a superseding `RQ-*` record over an in-place
amendment, that is a defensible reading of rule 4 and this task does not object
— but it is a heavier act than the decision directed, and `AGENTS.md` rule 15
warns that re-keying a record named in a completed archive's binding fields
breaks that archive. `RQ-MCE-e65b3c` is named in `EV-MCE-332f99`,
`DEC-20260803-a5b9b1`, `ledger/goals/GOAL-MCE-001/goal.yaml`, both BATCH-001
archives and both BATCH-002 dispatch entries. **Amend in place with the
`corrections` block; do not re-key.**

---

## 5. CONSEQUENTIAL ID UPDATES — required, or the RQ points at superseded entries

Every `KN-LIT` ID this RQ names in a load-bearing position is superseded by this
package. A record that cites the old ID is not wrong, but it sends a reader to an
entry marked `superseded_by`. Update these **only if the corresponding new entry
is actually filed** — if a review rejects one, that RQ reference stays as it is.

| RQ location | Old ID | New ID | Filed by |
|---|---|---|---|
| `constraints` — "Distinguisher is not break" | `KN-LIT-13a01d` | `KN-LIT-6b5b72` | `tag_defect_corrections.md` §4.1 |
| `constraints` — replacement text in §3 above | `KN-LIT-4c8135` | `KN-LIT-c4c2ac` | `superseding_entries.md` §1.4 |
| `scope.targets` bullet 2 | `13a01d`, `4c8135`, `71d1a0`, `7ee1a9` | `6b5b72`, `c4c2ac`, `819780`, `45b1b2` | both files |

### 5.1 `scope.targets` bullet 2 is on the same wrong axis and needs the same fix

Current text (lines 35–40):

```yaml
      - >-
        The rate-threshold structure of the alternant/Goppa distinguisher
        line — KN-LIT-13a01d (high-rate distinguisher), KN-LIT-4c8135
        (polynomial-time key recovery, high-rate alternant), KN-LIT-71d1a0
        (syzygy distinguisher), KN-LIT-7ee1a9 (degree-2 alternant) — stated
        as a quantitative distance from Classic McEliece's actual rates.
```

**Two defects, both established by this batch's own transcription.**

1. *"The rate-threshold structure"* and *"stated as a quantitative distance from
   Classic McEliece's actual rates"* pre-commit the goal to the rate axis. That
   is the retracted framing (`DEC-20260803-a5b9b1` D-2) in the RQ's own target
   list, and it is what would drive a later batch straight back into a rate
   comparison.
2. It types all four papers as one "rate-threshold structure". They are not one
   structure: `iacr:2024/1193`'s Theorem 3 is stated in the **dual** rate and
   says VERBATIM *"However here we allow any R"*
   (`rate_regime_extraction.md` §2.2); `arXiv:2304.14757` carries a family
   exclusion plus a field condition plus a rate condition; `iacr:2025/531`'s
   regime is **not obtained** at all.

Proposed replacement:

```yaml
      - >-
        The SCOPE STRUCTURE of the alternant/Goppa distinguisher line -- not
        assumed to be a rate structure. Each source states its own restriction
        on its own axes and they do not agree: KN-LIT-6b5b72 (2010 high-rate
        distinguisher, threshold NOT transcribed); KN-LIT-c4c2ac
        (polynomial-time key recovery on generic alternant codes -- code-family
        exclusion of Goppa codes, PLUS q in {2,3}, PLUS a high-rate condition
        that is [EXTRACTION-DAMAGED] and not transcribed); KN-LIT-819780
        (syzygy distinguisher, Theorem 3 stated in the DUAL rate, paper says
        "here we allow any R"; its 0.277 / 0.141 figures are Heuristic-1
        null-model conditions on a SHORTENED code, not applicability bounds);
        KN-LIT-45b1b2 (degree-2 alternant distinguisher -- the paper announces a
        precise rate regime in its abstract and the body was NOT obtained, so
        this program does not hold it). A quantitative distance from Classic
        McEliece's rates is computed only where BOTH sides are transcribed, and
        the axis of comparison is named before the arithmetic.
```

---

## 6. TWO STALE RQ FIELDS THIS TASK IS NOT AUTHORIZED TO FIX — flagged, not fixed

Both are outside this task's named duties. Recorded rather than silently passed
over, per `AGENTS.md` rule 8.

### 6.1 The ISD-binding instruction is still live in the RQ

`DEC-20260803-a5b9b1` D-3 retracts the claim that a binding exists: *"RETRACTED
— goal.yaml's claim that GOAL-HQC-001 and GOAL-SDITH-001 'already bind to' a
memory-charged ISD costing convention … **RQ-MCE-e65b3c.constraints and goal.yaml
therefore both instructed an act that cannot currently be performed.**"*

`BATCH-002-OPENING` §1's defect table marks D-3 *"**already corrected** in the
BATCH-001 ledger archive"*. **That is true for `goal.yaml` and NOT for the RQ.**
Verified at HEAD `2ea6216d`:

- `ledger/goals/GOAL-MCE-001/goal.yaml` carries the correction, lines 42–44:
  *"(The original note said this record 'binds to their ISD costing convention';
  corrected 2026-08-03 by DEC-20260803-a5b9b1 D-3 — no such binding exists.)"*
- `ledger/questions/RQ-MCE-e65b3c.yaml` still says, unamended:
  - `scope.targets` bullet 3: *"under the same costing convention GOAL-HQC-001
    and GOAL-SDITH-001 bind to. Not a separate convention."*
  - `constraints` item 3: *"Bind to the costing convention produced under
    GOAL-HQC-001 TASK-20260802-0100a5; do NOT derive a competing one."*

**The RQ still instructs an act D-3 says cannot be performed.** This matters this
batch, because `TASK-20260803-cb44ab` is transcribing a cost table under a
convention that is explicitly not adopted, and the RQ as written tells it to bind
to one. Routed to the Coordinator for `TASK-20260803-3aa684`; **not drafted here,
because it is not among this task's named duties and inventing a fourth
correction unasked is how a correction batch grows a new defect.**

### 6.2 `scope.standardization_status` is stale in this record's own favour

It reads: *"This status claim is transcribed from the Classic McEliece project's
own site structure … and is UNVERIFIED here — neither page was fetched."*
`TASK-20260803-f3aece` fetched both pages and read NIST IR 8545 directly
(`EV-MCE-332f99` O-6, O-7). The NIST half is now settled from the deciding body's
own text; the ISO half is **not** — O-7 records it as resting on an interested
single source with `iso.org` 403 twice and the designation number not obtained.
Flagged for the Coordinator. **Not drafted here**, same reason as §6.1.

---

## 7. What this correction does NOT do

- It states **nothing** about Classic McEliece's security in either direction.
  The Goppa exclusion is quoted as `arXiv:2304.14757`'s sentence about
  `arXiv:2304.14757`'s attack.
- It does **not** compute or imply any distance between any attack regime and
  Classic McEliece's rates. `EV-MCE-332f99` boundaries: *"there is no transcribed
  left-hand side."*
- It does **not** touch `claim_tier_ceiling`, which stays TOY, or
  `active_hypothesis_ids`, which stays empty.
- It does **not** assert anything about `iacr:2026/1232`. Nobody here has read
  it; `KN-LIT-7c4620` stays `citation_verified: web`.
