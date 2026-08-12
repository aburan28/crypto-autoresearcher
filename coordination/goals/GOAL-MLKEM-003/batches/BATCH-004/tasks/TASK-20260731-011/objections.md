# Red-team objections — EV-MLKEM-011/012 / DEC-20260731-003/004

- **Report id:** RT-20260731-002
- **Task:** TASK-20260731-011 (GOAL-MLKEM-003, BATCH-004)
- **Role:** red-team, independent session
- **Validator ref:** VAL-20260731-002 (`accept_with_qualifications`, `blocks_ledger_record: false`)
- **Verdict:** `pass_with_constraints`
- **blocks_ledger_record:** false
- **Disposition on DEC-20260731-003 refine:** accept with constraints (refine stands; KN-FIND-012 promotion stands)
- **Disposition on DEC-20260731-004 refine:** accept with constraints (refine stands; KN-FIND-013 promotion stands as conditional Case A sensitivity only)

Independence: this session did not author EXP-MLKEM-011/012, EV-MLKEM-011/012, DEC-20260731-003/004, KN-FIND-012/013, or VAL-20260731-002. Inference: `requested_policy=review-xhigh`, `resolved_model_id=cursor-grok-4.5`, `fallback_used=true`, `independent_session=true`.

Attack lines challenged: Pwrong/Pgood score-scale commensurability; equating ~84-bit floor gap with measured underestimation; HEUR-S1 +Δ realism; “erased shortfalls” as security restored; DEC refine + KN-FIND promotion warrant.

---

## Verdict summary

Coverage-gap numbers and Case A what-if arithmetic survive. Both DEC `refine` decisions stand. Constraints bind **84≠measured Δ**, **HEUR-S1 as accounting convention not ε-physics**, **“erased”≠security restored**, and **prose Δ alignment** — not the refine tokens themselves.

---

## 1. OBJ-RT011-001 — high — Pwrong/Pgood units match under archived claims

Fatal only if units differ. Headers: Pwrong line i = P(F≥i); Pgood = F(solution); matched left-panel stem. Recomputed fraction inside = 0; ~84-bit Kyber-512 floor gap confirmed. Incommensurate-normalization falsification does not fire.

**Constraint:** cite as same-F archived-header reading; reopen if verifyModel shows distinct normalizations.

## 2. OBJ-RT011-002 — high — ~84-bit floor gap ≠ measured Pwrong underestimation

Gap is toy-floor log2(Pwrong)≈−35.70 vs Table C.2 −119.57 — coverage/extrapolation distance, not operating-threshold model error. RUN-012 / H-MLKEM-012 / EV-012 rhetoric couples it to HEUR-S1 Δ; KN-FIND-013 “upper reference” label must bind.

**Constraint:** never substitute 84 for measured Δ; forbid “15 ≪ 84 therefore shortfalls fail.”

## 3. OBJ-RT011-003 — high — HEUR-S1 +Δ is not ε-restoration physics

ε ∝ R·Pwrong: holding ε by cutting R when Pwrong is 2^Δ larger moves the second term by **−Δ**, not +Δ. Case A is a stated accounting convention / what-if; crossovers 9.46/14.36/14.76 remain valid under that convention only.

**Constraint:** say “if second term is charged +Δ,” not “restoring ε costs +Δ”; no experimental validation claim for the payment map.

## 4. OBJ-RT011-004 — high — erased shortfalls ≠ ML-KEM security restored

Package non_claims defeat break language. Residual: “shortfalls erased” + 84-bit coupling reads as security restored / Carrier defeated.

**Constraint:** allow “CC margins evaporate under Case A +Δ accounting”; forbid security-restored / KN-OPEN-016 closed.

## 5. OBJ-RT011-005 — medium — DEC refine + KN-FIND promotions warranted under constraints

DEC-003 + KN-FIND-012: durable coverage gap — promote. DEC-004 + KN-FIND-013: conditional Case A sensitivity only — promote under AL-2/AL-3/AL-4 locks. GOAL active; KN-OPEN-016 open.

**Constraint:** do not advance official goal closure on this package.

## 6. OBJ-RT011-006 — medium — prose Δ drift (adopts validator)

Machine-readable Case A Δ = 9.46/14.36/14.76. EV-012 / RUN-012 headline / DEC-004 drifted (~9.6/14.9/14.6). KN-FIND-013 matches JSON. Non-fatal to `<15`; fix before immutable cite.

**Constraint:** align prose to JSON (or KN-FIND-013 rounding).

---

## Disposition on DEC refine

**Accept DEC-20260731-003 `refine` with constraints.** Promote KN-FIND-012 as archived coverage/extrapolation finding.

**Accept DEC-20260731-004 `refine` with constraints.** Promote KN-FIND-013 only as numbered-heuristic Case A sensitivity. Correct prose Δ. Do not mark KN-OPEN-016 closed. Do not claim ML-KEM security restored.
