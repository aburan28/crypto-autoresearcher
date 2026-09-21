# Red-team objections — EXP-MLKEM-015 / EV-MLKEM-015 / DEC-20260731-007

- **Report id:** RT-20260731-001
- **Task:** TASK-20260731-003 (GOAL-MLKEM-003, BATCH-001)
- **Role:** red-team, independent session
- **Validator ref:** VAL-20260731-001 (`accept_with_qualifications`, `blocks_ledger_record: false`)
- **Verdict:** `pass_with_constraints`
- **blocks_ledger_record:** false
- **Disposition on DEC-20260731-007 refine:** accept with constraints (refine stands; KN-FIND-015 promotion stands under scoped reading)

Independence: this session did not author EXP-MLKEM-015, EV-MLKEM-015, DEC-20260731-007, KN-FIND-015, or VAL-20260731-001. Inference: `requested_policy=review-xhigh`, `resolved_model_id=cursor-grok-4.5`, `fallback_used=true`, `independent_session=true`.

Attack lines challenged: cost-model sleight of hand; equating LE MATZOV dual with Carrier polar repair; NIST pressure as break; MLWE vs LWE; whether KN-OPEN-016 is advanced.

---

## Verdict summary

The four H-MLKEM-014 conjuncts and matched-cost discipline survive. DEC `refine` is the correct branch. Constraints bind **adoption language** and **KN-OPEN-016 scope**, not the refine token itself.

---

## 1. OBJ-RT009-001 — medium — Carrier absolutes vs LE MATZOV not proven commensurate

Carrier targets 139.5 / 195.1 / 259.7 are NIST cutoffs minus abstract shortfalls 3.5 / 11.9 / 12.3. Subtracting those from LE `dual_hybrid+fft` under `RC.MATZOV` assumes shared cost arithmetic. Primary Table 5.1 / App. C was not re-derived. C2 is instrument non-reproduction, not same-model proof of algorithmic overclaim.

**Constraint:** cite C2 only as headline-vs-LE-instrument gap until BATCH-002 re-derives Carrier costing.

## 2. OBJ-RT009-002 — high — LE MATZOV dual ≠ Carrier polar repair

Polar heuristics were not reimplemented (validator + package non_claims). C2 must not be paraphrased as settling KN-LIT-7617. Residual of KN-OPEN-016 remains disjunctive: polar ingredients ∪ different cost arithmetic ∪ overclaim (as KN-FIND-015 already states).

**Constraint:** keep that disjunction; never claim polar repair was measured here.

## 3. OBJ-RT009-003 — medium — NIST undercut is cost-model pressure, not a break

C3 shows MATZOV gate-count revision moves `primal_bdd` below 143/207/272. Package non_claims defeat break language. Kyber1024 margin is ~1.28 bits.

**Constraint:** name `RC.MATZOV`; refuse FIPS-203 / operational-break paraphrase.

## 4. OBJ-RT009-004 — medium — Module-LWE estimated as LWE

`schemes.Kyber*` Module-LWE→LWE modeling is disclosed and load-bearing. Conjuncts hold inside that LWE model; transfer to structured MLWE remains open.

**Constraint:** retain modeling boundary in every EV/DEC/KN-FIND-015 citation.

## 5. OBJ-RT009-005 — high — KN-OPEN-016 narrowed on public instrument only

Public LE result: dual does not beat primal under MATZOV; published dual headlines not reproduced. Polar-repair half untouched. "Lose security" via primal is KN-TECH-040 cost-model pressure, not the dual-heuristic question KN-OPEN-016 foregrounds.

**Constraint:** allow "public-instrument narrowing"; forbid closed / settled / advanced past that measurement. Status stays `open`.

## 6. OBJ-RT009-006 — medium — validator receipt qualifications live

Adopt VAL qualifications: missing `raw_by_scheme`, uncommitted working-tree package, no Sage re-execution. Non-fatal to conjuncts; fatal to immutable citation and to citing GJ21 / `fft=False` from `results.json`.

**Constraint:** archive/commit EXP-MLKEM-015 before durable ledger cite.

---

## Disposition on DEC refine

**Accept `refine` with constraints.** Promote KN-FIND-015 as a public-instrument finding. Keep GOAL-MLKEM-003 active; open BATCH-002 toward Carrier primary recompute or polar-decode falsification. Do not reopen GOAL-MLKEM-001/002. Do not mark KN-OPEN-016 closed.
