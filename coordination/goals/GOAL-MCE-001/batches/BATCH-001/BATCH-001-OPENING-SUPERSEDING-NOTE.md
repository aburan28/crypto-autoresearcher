# PROPOSED superseding note for `BATCH-001-OPENING` §4 — TASK-20260803-a53f73

**Task:** TASK-20260803-a53f73 · **Goal:** GOAL-MCE-001 · **Batch:** BATCH-002
**Role:** executor · **Date:** 2026-08-03
**Requested policy:** `executor-implementation` · **Resolved model:** `claude-opus-5` ·
**fallback_used:** `true`

> **PROPOSED ONLY. `BATCH-001-OPENING.md` WAS NOT MODIFIED AND MUST NOT BE.**
> It is a committed BATCH-001 artifact and this task is forbidden to edit it.

---

## 1. Where this note goes, and why not into the file it corrects

`BATCH-001-OPENING.md` is committed batch-opening state referenced by
`DEC-20260803-a5b9b1`, `EV-MCE-332f99`, both BATCH-001 review reports, and both
BATCH-001 archive receipts. Editing it would silently change the object those
records reviewed.

**Proposed filing location:**
`coordination/goals/GOAL-MCE-001/batches/BATCH-001/BATCH-001-OPENING-SUPERSEDED-4.md`
— a sibling file, filed by `TASK-20260803-3aa684`, never a modification of the
original. A reader arriving at §4 from a citation reaches the retraction by
directory listing, which is the same discovery path the corpus's
`superseded_by` chain provides.

**Note for the filer:** `TASK-20260803-3aa684`'s `write_scope` as declared in
`dispatch_queue.json` does **not** include
`coordination/goals/GOAL-MCE-001/batches/BATCH-001/`. Filing this note there
requires a scope amendment from the Coordinator. The alternative — filing it
under `batches/BATCH-002/` — leaves nothing beside the defective text for a
reader who arrives at BATCH-001 directly, which is the failure mode this note
exists to prevent. **Flagged, not resolved: it is a dispatch decision, not an
executor's.**

---

## 2. The note, ready to file

```markdown
# SUPERSEDING NOTE — `BATCH-001-OPENING.md` §4

**Applies to:** `coordination/goals/GOAL-MCE-001/batches/BATCH-001/BATCH-001-OPENING.md`
section 4, "The primary target, stated at the level the evidence supports".
**Authority:** `DEC-20260803-a5b9b1` rationale **D-2** (RETRACTED) and **D-6**
(UPHELD).
**Drafted by:** `TASK-20260803-a53f73` (GOAL-MCE-001 BATCH-002).
**Filed by:** `TASK-20260803-3aa684`.
**Status of the original:** UNCHANGED AND NOT EDITED. `BATCH-001-OPENING.md` is
committed batch state that two independent reviews read; it keeps its text. This
note supersedes two claims inside it and nothing else.

---

## Claim 1 — RETRACTED

`BATCH-001-OPENING.md` §4 asserts, verbatim:

> "**The rate threshold is the whole question.** `KN-LIT-4c8135` is genuinely
> polynomial-time and genuinely confined to high rate. Classic McEliece's rate is
> a number this program has not transcribed. The distance between those two is
> what BATCH-001 exists to measure, and until it is measured neither 'the
> structural line threatens Classic McEliece' nor 'it does not' is a statement
> this program is entitled to make."

**"The rate threshold is the whole question" is RETRACTED.** It was falsified by
the very batch it opened, from primary text that batch itself retrieved.

`arXiv:2304.14757`, VERBATIM, from full text at sha256
`ebbd94ac3cd00b0f0e723aeab56fd3b0820c89d47072fc8241f12c5f93c564b8`
(`EV-MCE-332f99` O-5; transcription at
`.../tasks/TASK-20260803-292b99/rate_regime_extraction.md` §3.3; re-acquired
byte-identically by validator `TASK-20260803-409c5e`):

> "Interestingly our attack does not work at all when the alternant code has the
> additional structure of being a Goppa code."

Table 1 of the same paper carries the restriction parenthetically:
*"(does not apply in the particular case of Goppa codes)"*. Section 3.2 is headed
*"What is wrong with Goppa codes?"* and states *"Goppa codes behave differently
from random alternant codes and provide counterexamples to Heuristic 18."*

Classic McEliece uses binary Goppa codes. **The restriction that separates that
paper's attack from Classic McEliece's code family is a family exclusion, and the
opening asserted the opposite axis was "the whole question" about a paper nobody
had read.**

### What is NOT retracted, stated so the retraction is not over-read

- **The high-rate condition is real and stands.** `arXiv:2304.14757` states it
  itself: *"provided that the rate of the alternant code is sufficiently large
  (6)"*, and Table 1 lists *"q “ 2 or q “ 3, m arbitrary + high rate condition
  (6)"*. The paper's restriction has **three conjuncts** — code family, field
  size `q ∈ {2,3}`, and rate — and the retraction is of "whole question", not of
  the rate axis. A reading of this note that drops the rate scoping repeats the
  original error with the axes exchanged.
- **Condition (6) is still not transcribed.** It is `[EXTRACTION-DAMAGED]`
  (`rate_regime_extraction.md` §3.4) and carries no claim in any record. The
  numeric rate threshold §4 correctly called the single most important number in
  that paper **remains unheld by this program**, now as a recorded extraction
  failure rather than an unattempted read.
- **§4's final sentence stands and is reaffirmed:** *"neither 'the structural
  line threatens Classic McEliece' nor 'it does not' is a statement this program
  is entitled to make."* This note asserts nothing about Classic McEliece's
  security in either direction. The exclusion above is `arXiv:2304.14757`'s
  statement about `arXiv:2304.14757`'s attack, quoted at its own hedging level.
- **The mis-typing that travelled with the claim.** The same framing typed
  `iacr:2024/1193` (`KN-LIT-71d1a0`, now superseded by `KN-LIT-819780`) as a
  rate-threshold result. Its Theorem 3 is stated in the **DUAL** rate and the
  paper says VERBATIM *"However here we allow any R"*; its 0.277 / 0.141 figures
  are Heuristic-1 **null-model conditions on a shortened code**, not applicability
  bounds on the distinguisher (`rate_regime_extraction.md` §2.2–2.3;
  `DEC-20260803-a5b9b1` D-2 `also_wrong_typed`). No record of this program ever
  stated those figures as applicability bounds; the mis-typing is in this
  opening's framing, and it is retracted here.

---

## Claim 2 — CORRECTED as unused held evidence

`BATCH-001-OPENING.md` §4 lists among the things "not established, by anything
this program holds":

> "whether it touches binary Goppa codes at all"

**`DEC-20260803-a5b9b1` D-6, UPHELD:** the program already held the answer. The
ePrint page for `iacr:2026/1232`, fetched during `GATHER-20260803` on 2026-08-03
for citation verification, carries the keyword line, VERBATIM:

> `McEliece scheme, Algebraic cryptanalysis, Binary Goppa codes`

and the abstract retrieved by `TASK-20260803-292b99` states, VERBATIM: *"We
provide a new way of performing an algebraic attack on the McEliece cryptosystem
based on binary Goppa codes."*

D-6: *"Unused held evidence, not caution."* The cheapest control was to record
the Keywords line at verification time, at zero marginal network cost.

**Scope of this correction, which is narrow.** It establishes only that the paper
**addresses** binary Goppa codes. It establishes nothing about the paper's
complexity claim, its heuristics, its rate regime, or its bearing on Classic
McEliece's parameters. Every other item in §4's not-established list stands:
**the body of `iacr:2026/1232` was never obtained** (`EV-MCE-332f99` O-2, O-3,
O-9), `KN-LIT-7c4620` remains `citation_verified: web`, and no record of this
program may imply the paper was read.

---

## What this note does not touch

`BATCH-001-OPENING.md` §§1–3 and 5–9 are outside this note's authority. Their
separate dispositions are in `DEC-20260803-a5b9b1`: §5's costing-convention claim
is retracted by **D-3**, §2's danger framing is inverted per **D-7**, §5's "two
live code-based goals" overstates per **D-8**, and §3's use of `KN-OPEN-3f7a21`
was challenged and **withdrawn by the red team itself** per **D-9**. Read that
decision, not this note, for those.

**No conclusion about Classic McEliece's security appears anywhere in this note,
and none may be inferred from it.**
```

---

## 3. Two things this note deliberately does not do

- **It does not retract the rate axis.** Duty 2's warning is the sharpest risk in
  this whole package: a correction that leads with the Goppa exclusion while
  deleting the rate scoping has traded one wrong record for another. §4's rate
  condition is the paper's own and it is reaffirmed inside the retraction.
- **It does not upgrade `iacr:2026/1232`.** Claim 2 corrects exactly one bullet —
  "whether it touches binary Goppa codes at all" — from a keyword line and an
  abstract sentence. The paper's body is unobtained and every other item in §4's
  list of unknowns stands verbatim.
