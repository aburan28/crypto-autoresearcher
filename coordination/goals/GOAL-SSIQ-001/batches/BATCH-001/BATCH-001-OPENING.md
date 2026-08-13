# GOAL-SSIQ-001 BATCH-001 — opening

**Goal:** GOAL-SSIQ-001 · **Question:** RQ-SSIQ-9702af · **Opened:** 2026-08-05
**Coordinator authority:** user direction this session — *"create a new goal to
breakthrough and find a 0.25 algorithm for this problem
https://eprint.iacr.org/2026/1486"*.

BATCH-001 is **zero compute and primary-text only**. It designs no experiment,
mints no hypothesis, runs no solver, and asserts nothing about whether a
`p^{1/4}` algorithm exists, is likely, or is near.

---

## 1. What the user asked for, and what this batch does instead

The paper at `eprint.iacr.org/2026/1486` is Wesolowski, *The supersingular
isogeny problem in time and memory p^{1/3+o(1)}*. This repository already
holds its full text, frozen, at `inputs/P13-WESOLOWSKI-2026/paper_fulltext.md`
(`SRC-P13-WESOLOWSKI-2026`, corpus entry `KN-LIT-7563`), and it is the
canonical exemplar of `docs/target-result-profile.md`. The user's target is the
next exponent below it: `p^{1/4+o(1)}` for the general `F_{p^2}` problem.

This batch does not search for that algorithm. Section 8 of
`docs/inventor-protocol.md` (`KN-TECH-080`) requires the **exact bottleneck and
baseline reproduction** before the Coordinator approves implementation or
expensive experiments, and here that ordering is doing real work rather than
paperwork: *"reach 1/4"* is not yet a falsifiable target, because nobody in
this program has written down **which quantity in the proof would have to
move, and to what value**. Until that exists, every proposal is unrankable and
every negative result is unattributable.

## 2. The bottleneck, as the Coordinator currently reads it

From the proof of Theorem 1.1 (`paper_fulltext.md` lines 177–218), `1/3` is not
one number but a product:

| | factor | exponent | source |
|---|---|---|---|
| **F1** | minimal degree of `E -> E^{(p)}` is `<= (p/2)^{1/3}` | 1/3 | Theorem 1.5, attributed to [4] |
| **F2** | balanced smooth split: each side `<= X = B^{1/2}(p/2)^{1/6}` | 1/2 of F1 | Lemma 3.4 |
| **F3** | `|L(E,X,B)| = Psi(X,B) * X^{1+o(1)} = X^{2+o(1)}` | joint → 1/3 | Lemma 3.3 |
| **F4** | `P0^{-1} = u^{u(1+o(1))}` at `B = e^{(1/3)sqrt(log(p/2))}` | **0** | Lemma 3.5 |

Two consequences follow immediately, and they are the batch's reason to exist:

1. **F4 carries no exponent.** Any proposal whose saving comes from "a better
   success probability" is confusing an `o(1)` with an exponent. That class of
   idea is refuted at the whiteboard, for free, before it is ever dispatched.
2. **F3 is quadratic in `X`** — `~X` admissible smooth degrees times `~d`
   cyclic isogenies of degree `d` — which is simultaneously why the time
   exponent is `1/3` and why the memory equals the time. Whoever moves F3 moves
   both.

This table is a **Coordinator reading and is not yet independently verified.**
`TASK-20260805-85af9d` exists to re-derive it from the frozen text with line
locators and to correct it. A lever built on an uncorrected factor inherits the
defect, so the correction comes first.

## 3. Levers, and the ceilings that are audited before any of them are built

`L1`–`L5` are enumerated in `ledger/goals/GOAL-SSIQ-001/goal.yaml` under
`exponent_budget.levers`, each with the statement that would have to be true
and the obstruction to audit *first*. BATCH-001 audits the two that are
cheapest to kill and most load-bearing:

- **L1 (move F1 to exponent 1/4).** The named obstruction is a Minkowski-type
  lower bound on the minimum of the rank-4 quaternion lattice underlying
  `Hom(E, E^{(p)})` with the form `Nrd/p`. If the determinant forces a minimum
  at exponent `1/3`, **L1 is closed and the ceiling argument is the useful
  result.** A failed audit is a real deliverable here, not a wasted batch.
- **L4 (subfield descent).** `E` lies on the `F_p` locus exactly when
  `E ≅ E^{(p)}` — i.e. when the F1 degree is `1` — so the archived theorem
  already says every curve is within degree `p^{1/3}` of the degenerate stratum
  of that same invariant. The lever is natural. Its problem is its baseline:
  the `Otilde(p^{1/4})` figure attached to the `F_p`-restricted problem is
  carried in this corpus at `relayed_from_abstract` **and contested across
  retrievals** (`KN-TECH-058`, *"What is NOT corrected here"*, RC4 — two
  retrievals returned two different abstracts, one containing no `p^{1/4}`
  figure at all). Building on a contested figure is building on nothing, so
  the batch establishes it or records that it could not be established.

## 4. What this batch may not do

- It may not state, imply, or arrange its findings to suggest that a `p^{1/4}`
  algorithm exists or is near. **0.25 is the search target, not a claim.**
- It may not cite the `F_p` `Otilde(p^{1/4})` figure as evidence that exponent
  `1/4` is reachable over `F_{p^2}`. Different problem, contested source.
- It may not treat *"1/3 was just proved, so 1/4 is hopeless"* as evidence.
  Premature closure is a failure mode symmetric with overclaiming
  (`docs/inventor-protocol.md`), and AGENTS.md rule 9 governs any
  deprioritisation.
- It may not re-derive or restate GOAL-P13-001's concrete-cost findings
  (`EV-PEC-2e67ff`, `EV-PEC-857664`) as its own. Those are **inputs**, cited.
- It may not treat `L1`–`L5` as exhaustive. Producers are explicitly asked to
  add levers; no later record may read *"not in L1–L5"* as *"not a route"*.

## 5. Evidence-strength cap, stated before any evidence exists

Per-role model policies do not resolve under this Claude Code binding: every
alias falls back to the session model. Producer/reviewer independence in this
campaign is therefore **session** independence, not **model** independence —
the same cap that held `EV-SSI-005` at `preliminary`. Every task records
`requested_policy` beside the resolved model with `fallback_used: true`.
This is recorded now, at batch open, so that no later record can present the
cap as a surprise or quietly omit it.

---

**Batch closes** on: two producer snapshot archives, an independent Validator
pass, an independent Red Team pass, and one Coordinator ledger archive writing
`ledger/goals/GOAL-SSIQ-001/checkpoints/BATCH-001.yaml` and advancing
`latest_verified_commit`.
