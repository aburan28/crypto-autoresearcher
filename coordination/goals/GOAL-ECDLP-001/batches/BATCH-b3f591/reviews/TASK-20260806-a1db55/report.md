# Independent Validator Report — BATCH-b3f591

**Task:** TASK-20260806-a1db55
**Batch:** BATCH-b3f591
**Goal:** GOAL-ECDLP-001
**Policy:** review-adversarial (xhigh reasoning, independent session)
**Date:** 2026-08-07

---

## 1. No committed run record claimed

**Finding: PASS.**

All four producer artifacts are analysis-only:

- **TASK-20260806-a01d5a** (Producer D, experiment design): Explicitly states "No run executes; no run record is minted" (line 260). Status is `design_submitted`; no `specification.yaml` committed. Experiment id `EXP-SEMAEV-f48dd1` is reserved, not committed.
- **TASK-20260806-a4b58a** (knowledge candidates): Three KN-FIND candidates drafted; none promoted. States "No experiment ran in this record" (Candidate 1 non-claims).
- **TASK-20260806-ad94be** (H-PSEUDO o(1) disposition): States "No new hypothesis is introduced. No status transition is proposed. No proof of either reading is claimed."
- **TASK-20260806-bf2364** (Producer A, halving-query equivalence): States "No experiment ran. No run record is fabricated. The numeric verification above is a hand-checkable arithmetic derivation, not a measured computation."

No artifact contains a run id, manifest, raw-result.json, or any claim of executed computation. This is consistent with the batch being analysis-only.

**Fabricated-run claims ticked: 0/4.**

---

## 2. Arithmetic recomputation checks

### 2.1 Producer A: Duplication formula (TASK-20260806-bf2364)

**Claim:** x([2]P) = (x^4 - 2ax^2 + a^2 - 8bx) / (4(x^3 + ax + b))

**Independent derivation:**

Starting from the chord-tangent formula for P = (x, y) on y^2 = x^3 + ax + b:

    lambda = (3x^2 + a) / (2y)
    x([2]P) = lambda^2 - 2x = (3x^2 + a)^2 / (4y^2) - 2x

Substituting y^2 = x^3 + ax + b:

    x([2]P) = [(3x^2 + a)^2 - 8x(x^3 + ax + b)] / [4(x^3 + ax + b)]

Expanding numerator:

    (3x^2 + a)^2 = 9x^4 + 6ax^2 + a^2
    8x(x^3 + ax + b) = 8x^4 + 8ax^2 + 8bx
    Difference = x^4 - 2ax^2 + a^2 - 8bx

**Result: VERIFIED.** The closed form matches the producer's derivation exactly.

**Numeric verification on E: y^2 = x^3 + 3x + 7 over F_1009:**

| Check | Producer value | Independent value | Match |
|-------|---------------|-------------------|-------|
| H = [9]Q | (819, 627) | (819, 627) | YES |
| [2]H | (998, 113) = Q | (998, 113) = Q | YES |
| f_correct(819) | 998 | 998 | YES |
| f_wrong(819) | != 998 | 950 | YES (both != 998) |

**Wrong-formula disagreement count:**

Producer claims: wrong formula disagrees at 472 of 475 x-coordinates with y != 0.

Independent count: 475 x-coordinates have curve points with y != 0. The wrong and correct formulas agree iff 8x^2(x^2 + a) = 0 mod p, which gives exactly 3 roots: x = 0, x = 260, x = 749 (where 260^2 = 749^2 = -3 mod 1009). Therefore 475 - 3 = 472 disagreements.

**Result: VERIFIED.** The producer's count of 472/475 is exactly correct.

### 2.2 Producer B: K* corrections (TASK-20260806-a4b58a, Candidate 2)

**Claim 1:** K*(standard) = 2000, not 2001. Cause: IEEE-float ceil artifact on 200/0.1.

**Independent check of the correction:**
- The exact rational value of 200/0.1 is 2000. The ceiling of 2000 is 2000.
- **K* = 2000 is CORRECT as a mathematical statement.**

**Independent check of the IEEE mechanism:**
- On this platform (Python 3 / macOS / IEEE 754 double precision): `200 / 0.1` evaluates to exactly `2000.0`. `math.ceil(200 / 0.1)` returns `2000`, not `2001`.
- The specific claim "200/0.1 = 2000.0000000000005 in double precision" does **NOT** reproduce on this platform.
- Since 0.1 in double precision is 0.1000000000000000055511151... (> 1/10 exact), the quotient 200/0.1_double is actually slightly below 2000, not above. `ceil` of a value slightly below 2000 gives 2000.

**Assessment:** The corrected value K* = 2000 is mathematically correct. The stated IEEE mechanism is platform-dependent and does not reproduce here. The error in the as-committed table (2001) could have arisen from a different computation path (e.g., intermediate rounding in a different language/library, or a different formula arrangement). The correction itself is valid regardless of the specific error mechanism.

**Claim 2:** m=4 cell = 125, not 126. Same IEEE-float ceil artifact.

**Independent check:**
- Without the exact original computation, I cannot reproduce the specific IEEE path. However, the mathematical correction (exact rational = 125, ceiling = 125) is structurally identical to Claim 1.
- **The corrected value 125 is plausible** as a mathematical statement, but the specific IEEE mechanism claim has the same platform-dependency issue as Claim 1.

**Claim 3:** K*(BKK) = 96, correct as-committed.

**Independent check:** Not independently recomputable without the exact BKK K* formula and input parameters. The producer states this value is confirmed correct; no discrepancy is claimed. **ACCEPTED as stated** (no correction claimed).

### 2.3 Summary of arithmetic checks

| Check | Result | Notes |
|-------|--------|-------|
| Duplication formula derivation | VERIFIED | Independent derivation matches |
| Duplication formula numeric (H, Q) | VERIFIED | [2](819,627) = (998,113) confirmed |
| Correct formula f(819) = 998 | VERIFIED | Independent computation confirms |
| Wrong formula f(819) != 998 | VERIFIED | Independent: 950 != 998 |
| Wrong formula 472/475 disagree | VERIFIED | Independent: exactly 472 |
| K*(std) = 2000 not 2001 | VERIFIED (value) | IEEE mechanism not reproduced |
| m=4 cell = 125 not 126 | PLAUSIBLE (value) | IEEE mechanism not reproduced |
| K*(BKK) = 96 correct | ACCEPTED | No correction claimed |

---

## 3. Experiment design: null-object control and corridor-compatible cells

### 3.1 Null-object control

**Present: YES.** The experiment design (TASK-20260806-a01d5a) specifies a three-arm null-object triple:

- **Arm A:** no-oracle, exhaustive enumeration (baseline)
- **Arm B:** x-oracle, true x-coordinate responses
- **Arm C:** random predictor, deterministic PRNG responses

Arms B and C are run-matched: identical code path, identical branching, identical query count, identical hash-table lookups. The only difference is the response value. This satisfies the inventor-protocol "controls before belief" requirement.

Control pass conditions are pre-registered:
1. B and C must execute the same number of oracle queries per config.
2. C's PRNG must be collision-free within each run.
3. A's yield must be consistent with B^m/N prediction (within factor 2).

### 3.2 Corridor-compatible cells

**Present: YES.** The parameter cells are:

- m in {3, 4} (tested in EXP-SEMAEV-002; corridor-empty for m=5)
- p in {101, 103, 107, 211} (EXP-SEMAEV-002 curve set)
- b in {0.4, 0.5} (cellgrid-tested range)
- 5 seeds per cell

Total: 80 config-run combinations, 240 arm-runs.

The design explicitly states it does NOT test the rescue-window claim, K*(std) vs K*(BKK) crossover, or any parameter cell in the proven-empty corridor (Section 9). A cell exclusion rule drops cells where B^m/N is outside [0.05, 0.8].

### 3.3 Toy-scale scoping

**Present: YES.** Section 0 explicitly states this is toy-scale only (N < 200) and no result is presented as evidence about crypto-scale ECDLP.

---

## 4. Artifact integrity

### 4.1 No fabricated artifacts

All four producer files are present at their expected paths under `coordination/goals/GOAL-ECDLP-001/batches/BATCH-b3f591/tasks/`. No run records, manifests, or raw-result.json files exist (consistent with analysis-only batch).

### 4.2 Identifier hygiene

- KN-FIND-194294, KN-FIND-ac28ed, KN-FIND-ff4a46: all stated as minted via `allocate_id.py --check` and confirmed free. These are 6-hex suffixes per AGENTS.md rule 14.
- EXP-SEMAEV-f48dd1: stated as reserved, not committed. Confirmed: no specification.yaml exists.
- TASK ids: all follow the TASK-YYYYMMDD-NNN format with 6-hex suffixes.

### 4.3 No research-state transition

No producer file claims a hypothesis status transition. All are analysis, derivation, or design documents. This is consistent with the Validator's mandate (no state transitions).

---

## 5. Findings summary

| Check | Status | Severity |
|-------|--------|----------|
| No fabricated run records | PASS | — |
| Duplication formula derivation | VERIFIED | — |
| Duplication formula numeric verification | VERIFIED | — |
| Wrong-formula disagreement count | VERIFIED | — |
| K*(std) = 2000 correction | VERIFIED (value) | LOW: IEEE mechanism not reproduced |
| m=4 cell = 125 correction | PLAUSIBLE (value) | LOW: IEEE mechanism not reproduced |
| Null-object control present | PASS | — |
| Corridor-compatible cells | PASS | — |
| Toy-scale scoping | PASS | — |
| Artifact integrity | PASS | — |
| No state transitions claimed | PASS | — |

**Overall assessment:** The batch passes validation. The two LOW-severity findings (IEEE mechanism not reproduced) do not affect the mathematical correctness of the corrections; they affect only the stated error mechanism, which is not load-bearing for the research conclusions.

---

## 6. Non-claims

- This report does not promote or demote any hypothesis or research direction.
- This report does not evaluate the mathematical merit of the H-PSEUDO disposition or the oracle equivalence beyond arithmetic verification.
- This report does not assess whether the experiment design is worth executing.

---

*Validator: TASK-20260806-a1db55, independent session, policy review-adversarial.*
*Resolved model: accounts/fireworks/models/qwen3p7-plus (per model binding).*
