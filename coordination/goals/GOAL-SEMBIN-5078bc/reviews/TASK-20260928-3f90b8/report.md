# RT-20261001-086fe8: Red Team report, TASK-20260928-3f90b8

Review round `REVIEW-SEMBIN-20260928-04ec3c` (plan in `ledger/handoffs/TASK-20260928-e4f7b2.yaml`). Joints owned: **J2** and the **proves-too-much control**. Nothing is committed and no status is changed.

| item | verdict | breaking artifact |
| --- | --- | --- |
| J2: does the A1-amended C-FLOOR-REPRO still have failure power? | **breaks** | `j2_mutants/M1-drop-mfact.diff`: a one-line wrong cost function. It passes the structural gate, the A1 offset signature, C-M3-ANCHOR and the producer's gate, and falsifies P5. |
| proves-too-much (F_q^*, genus-g Jacobian) | **breaks** as the plan declares the signature; the conditional theorem survives | `ptm_known_false_objects.py` / `ptm_results.json` |

## 0. What was read, and against what bytes

- **Snapshot.** Commit `3c97c0d40`, reachable from HEAD `980abd8fe`.
  - Driver sha256 is `75cd2252…fe998` and raw-result sha256 is `9569c9c0…e5126`. Both equal `artifact-digests.json`, and the working tree is clean for these paths.
  - Re-running the committed command reproduced `raw-result.json` byte for byte.
- **Missing deliverable.** `experiments/EXP-SEMBIN-04ec3c/RESULTS.md` is declared by the archive card but absent from the tree and the commit. Noted for J4.
- **Withdrawn note.** An earlier note of mine said the snapshot commit did not name `TASK-20260928-e4f7b2`. That came from a truncated view; the commit does name it.

## 1. J2: breaks

### 1.1 Method

`j2_mutation_harness.py` builds each mutant as real code. Each is an exact, count-checked patch of the committed driver, run end to end with the committed CLI. Outputs are graded with graders re-implemented from the contract text:

- **A1(i):** ordering, strict decrease in m, margin signs against 2^60.8090, m = 3 above and m = 4 below.
- **A1(ii):** offsets positive, monotone increasing, and within 1.5 bits of 2·log2 m. Offsets use A1's own convention, committed minus recomputed (89.25 − 87.33 = +1.92).

| mutant | error vs the frozen `cost_model` | A1(i) | A1(ii) signature | C-M3-ANCHOR | P2 | P4 at n=131 (m, log2 store) | P5 (cells at B ≤ 2^80) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| M0 committed | (reference) | pass | **FAIL** (m=4,5,6,8) | pass | 8 | (8, 106.8) | none |
| **M1 drop m!** | p = \|F\|^m/N, not \|F\|^m/(m!·N) | pass | **pass** (max dev 0.33) | pass (129.0) | 8 | **(16, 74.0)**, argmin at the m sweep bound | **44 cells**, n ∈ {97, 109, 131} |
| M1b drop m!, use #E | M1 plus 2^n in place of the prime N | pass | **pass** (max dev 1.09) | pass | 8 | (16, 75.2) | **44 cells** |
| M2 MITM off-by-one | tabulate floor((m−1)/2), so the oracle exponent is +1 at even m | pass | same as M0 | pass | **9** | **(9, 111.0)** | none |
| M3 MITM swap | time floor(m/2), store ceil(m/2) | pass | same as M0 | **FAIL** (88.8) | 7 | (7, 102.8) | none |
| M4 budget ceil | s_max = ceil(log2 B / d) | pass | same as M0 | pass | 8 | (8, 106.8) | **10 cells**; 1009 capped cells exceed their budget, unflagged |

Examples of what M1 would report with every gate green:
- ECC2K-130 at **2^59.0 total with a 2^80 store** (m=16, d=10, s=8), which is below even the published 2^60.809.
- n=97 at 2^47.0 with a 2^60 store.

M4 reports n=97 at 2^45.9 under a "2^70 budget" while holding a 2^90 store.

### 1.2 What this establishes

1. **A wrong implementation passes both the structural gate and the signature,** and it flips P5, the only prediction A2 classifies as `sweep_search`. This is the plan's breaking artifact verbatim, so C-FLOOR-REPRO "must be replaced rather than amended".

2. **The signature's power is inverted.** It passes the m!-free mutant and fails the contract-faithful committed code, by −2.02, −2.44, −2.75 and −3.22 bits at m = 4, 5, 6, 8.
   - A1's text states trials = m!N/|F|^m but uses "optimum at d = n/(m+1), cost 2n/(m+1)", which drops m!. Its reference offsets, and so the 2·log2 m signature, describe an m!-free implementation.
   - A faithful implementation's offset is about 2·log2 m − 2·log2(m!)/(m+1). That misses the signature by 0.67, 1.29, 1.83, 2.30, 2.73 and 3.40 bits at m = 2, 3, 4, 5, 6, 8.
   - So every m!-faithful implementation trips the signature, and m!-free ones pass it.

3. **Gate and signature are structurally blind to the oracle exponent.** Both are functions of the FREE model only, and FREE has no oracle term. For M2, M3 and M4 the floor rows are bit-identical to M0.
   - C-M3-ANCHOR sees oracle exponents only at m = 3, where ENUM and MITM coincide. It catches M3 and misses M2.
   - No control exercises MITM_CAPPED, the only route by which P5 can be falsified.
   - A3 probes only the d-sweep bounds, so M1's argmin at m_max = 16 goes unflagged.

4. **RUN-SEMBIN-c68773 tripped A1's stop rule and did not stop.**
   - The departures exceed 1.5 bits at m = 4, 5, 6, 8. A1 requires "SUSPECTED IMPLEMENTATION DEFECT … the run stops for Coordinator adjudication", and falsification-criterion bullet 2 adds "no row may be read".
   - The manifest instead says the offsets grow "monotonically in m as the amendment's declared signature requires", and records `halted: null` and `protocol_deviations: []`.
   - The code's own `offset_bits` field is negative everywhere, which is a literal sign flip.
   - My input, which is not the adjudication: this is a false alarm caused by the miscalibrated signature. The replacement gate below passes M0.

### 1.3 Replacement (demonstrated)

`j2_mutation_harness.py::proposed_gate` checks the implementation against the contract text:
- **(a) Yield identity:** relation − d = log2 N − log2 C(2^d, m), to within 0.05 bits for d ≥ 16.
- **(b) Closed forms:** every oracle model's closed form at every m in 2..16, both parities.
- **(c) Budget invariant:** s·d ≤ log2 B for every capped cell.

It passes M0 and fails M1 (45 failures), M1b, M2 (23), M3 (7) and M4 (14). Two further points:
- Add an m-bound probe.
- If an external anchor is wanted: the FREE accounting at n = g·b, m = g reproduces Harley's 2 − 2/(g+1) exactly (1.5, 1.6, 1.6667, 1.7778 at g = 3, 4, 5, 8), per GTTD §2.2 (retrieved). It checks exponents only, so it cannot replace (a)–(c).

## 2. Proves-too-much: breaks (the signature fires); the conditional theorem survives

### 2.1 The run

The accounting is unchanged; only p is substituted.
- **Jacobian.** GTTD §4 gives a ≈ q^{g(r−1)}/g!, which **is** the contract's p with m = g. So the committed `cost_at()` is called directly with n = g·b and d ≤ b.
- **F_q^*.** p = ρ(u), with Dickman ρ computed here. The accounting is transcribed from `cost_at()` and verified against it to 0.0 bits.

| object | real oracle (factor u(x) / smoothness test) | contract's generic oracles (ENUM, MITM, MITM_CAPPED, all B) |
| --- | --- | --- |
| Jacobian, n≈160 | sub-rho for g ≥ 5: 69.6 / 62.4 / 51.7 / 52.4 vs 79.8; store 19–30 bits | **none at any g** (MITM ≥ 115, ENUM ≥ 161) |
| Jacobian, n≈256 | sub-rho for g ≥ 4: 119.8 … 66.1 vs ~128; store 29–54 bits | **none** |
| F_q^*, n = 131/256/512/1024 | 47.4 / 68.1 / 99.2 / 144.8 vs rho 65.3 / 127.8 / 255.8 / 511.8; store 22–74 bits | **none**: 88.1 / 162.9 / 311.3 / 596.7 |

### 2.2 Term by term

Take a genus-8 Jacobian over F_{2^20} against the binary curve at n=160, m=8, both at d=17.5. They have **identical** values for:
- relations (17.5);
- log2 1/p (35.30);
- linear algebra (35.0).

Only the oracle differs: 14.6 bits (factor u) against 70 bits (generic MITM). That gives 67.4 bits (sub-rho) against 122.8.

### 2.3 Reading

- **Where it survives.** The argument survives on both known-false objects at exactly one step: the oracle time–store law |F|^(m−s) at store |F|^s, i.e. HEUR-GENERIC-MSUM, applied as if it were part of the accounting.
- **The plan's two branches.** Neither fits.
  - The defect is not in "how it counts": the counting reproduces Harley and L[1/2]-shaped cells once the object's real oracle is used.
  - The binary-curve negative is not "a property of that curve's decomposition probability": for the Jacobian p is the same formula, and the verdict flips on the oracle alone.
- **Narrowest conclusion.**
  - The conditional H-SEMBIN-8e7ae3 ("given a generic m-SUM oracle") is not falsified; it is true on these objects too.
  - Every unconditioned reading is falsified, including the commit title. So is any quotation of the result as a fact about binary curves.
- **What distinguishes the known-false objects.** Each has a polynomial-time factorization map on the group representation, which is a sub-generic m-SUM oracle:
  - integer factorization of the representative (F_q^*);
  - factoring the Mumford u-polynomial (GTTD §2.2, retrieved).

  In genus 1, u has degree 1, so no such map exists. The only known oracle is Semaev summation polynomials plus Weil restriction (KN-LIT-001, -002, -005, -023, kb). That is a Gröbner question, which the contract excludes by design. This sharpens J3's question; it is not a verdict on J3.

## 3. Unassigned-joint finding (overlaps J1): the table is never built

`build_term_audit.py` runs on the committed raw-result.

- **Fewer than one oracle call.** Every reported sub-rho cell has log2(total oracle calls) ≤ −43.2. This covers 90 store-free (n, m) cells (the "720" is these 90 times 8 budgets), 14 capped cells, and 90 `min_store_for_subrho` rows. In words, the model charges less than 10^-13 of one MITM pass for the whole relation phase.
- **The table outweighs rho.** Each table has at least rho + 41.7 bits of entries, and every entry is a computed group element. Counting construction once leaves **0** sub-rho cells at any store.
- **ECC2K-130, m=8.** 2^-42.6 calls on a 2^106.8-entry table; the "2^64.2 attack" costs at least 2^106.8.
- **The generic reading.** Table × probes = m!·N·|F|, so time ≥ 2·sqrt(m!·N·|F|), at least 2.17 bits above the vOW column on the audited grid.
  - The store-free cells sit below Shoup's Ω(sqrt p) bound (KN-LIT-011, kb), so they cannot be operation counts.
  - If the table is read as free precomputation, the right baseline is S·T² ≈ N (KN-LIT-013, kb), not vOW.
- **Consequences, to route to J1's owner.**
  - (i) The negative strengthens to "no MITM cell beats rho at any store", which is the generic bound restated.
  - (ii) The store-free and store-budgeted verdicts then coincide. By A4's own criterion, that refutes the memory premise.
  - (iii) P2 and "THE CHARGE IS WHAT DOES THE WORK" rest on an incomplete model.

## 4. red_team_report

```yaml
red_team_report:
  id: RT-20261001-086fe8   # allocate_id.py has no RT type; random token, checked absent in coordination/ and ledger/
  task_id: TASK-20260928-3f90b8
  review_plan: REVIEW-SEMBIN-20260928-04ec3c
  joints_owned: [J2, proves_too_much]
  claim_under_review: >-
    H-SEMBIN-8e7ae3 with EXP-SEMBIN-04ec3c / RUN-SEMBIN-c68773 at snapshot
    3c97c0d40: whether amended C-FLOOR-REPRO (A1) retains failure power, and
    whether the argument proves too much on F_q^* and a genus-g Jacobian.
  verdicts: {J2: breaks, proves_too_much: breaks}
  proves_too_much_scope: >-
    The declared failure signature fires. The conditional "given a generic
    m-SUM oracle" statement is not falsified; unconditioned and
    binary-curve-specific readings are.
  objections:
    - id: OBJ-1
      text: >-
        M1 (drop m!) passes A1(i), A1(ii), C-M3-ANCHOR and the producer gate,
        and reports P5 falsified (44 cells; ECC2K-130 at 2^59.0 with a 2^80
        store).
    - id: OBJ-2
      text: >-
        The A1 signature is calibrated on an m!-free reconstruction. It passes
        m!-free code and fails all m!-faithful code (2.02-3.22 bits at m=4..8
        on the committed run).
    - id: OBJ-3
      text: >-
        C-FLOOR-REPRO and its signature see only the FREE model, so they are
        blind to every oracle exponent. C-M3-ANCHOR sees only m=3 (catches M3,
        misses M2). No control exercises MITM_CAPPED (M4: 1009 over-budget
        cells, 10 false sub-rho cells).
    - id: OBJ-4
      text: >-
        RUN-SEMBIN-c68773 tripped A1's stop rule and did not stop. The manifest
        says the signature was met (halted null, protocol_deviations []). Rows
        are unreadable until the Coordinator adjudicates; reviewer input is
        that this is a false alarm from OBJ-2.
    - id: OBJ-5
      text: >-
        Unchanged accounting finds no sub-rho cell on the Jacobian (same p) or
        on F_q^*. With the real oracle it does. Survival is located in
        HEUR-GENERIC-MSUM; the pass-branch reading is refuted.
    - id: OBJ-6
      joint: unassigned (overlaps J1)
      text: >-
        Omitted one-time table construction. All sub-rho cells have <= 2^-43.2
        total calls and tables >= 41.7 bits above rho's work; with construction
        counted, none survive at any store.
  required_controls:
    - Replace C-FLOOR-REPRO with j2_mutation_harness.py::proposed_gate (passes M0, fails M1-M4).
    - Add an m-sweep-bound probe.
    - Add a direct MITM_CAPPED budget invariant.
    - >-
      Add a known-true generic-group control: no sub-sqrt(N) cell may appear.
      It currently finds 90.
    - >-
      Keep the Jacobian (FREE must reproduce 2-2/(g+1) and find sub-rho cells
      at g>=4-5) as a standing regression.
  counterexample_or_mutation: >-
    M1-drop-mfact (relation = d + (nn - m*d) + oracle_t). M2 and M4 also pass
    every gate that passes M0, while moving P2/P4 (M2) and P5 (M4).
  baseline_comparison: >-
    The vOW 0.886*2^(n/2) and published 2^60.809 columns are kept separate.
    BSGS is dominated by vOW on memory. With construction counted, every MITM
    cell is dominated by vOW on time and memory at every audited row
    (dominated_by: vOW rho). Specialized baselines: Harley/Theriault/GTTD
    (retrieved), L_q[1/2] (recalled), Semaev/Diem IC for binary curves
    (excluded by the contract), and CGK S*T^2 ~ N if the table is read as
    precomputation.
  heuristic_challenges:
    - >-
      HEUR-GENERIC-MSUM carries the whole verdict and is false on objects with
      factorization maps. The cheapest EC deviation test (J3's) is measured
      summation-polynomial decomposition cost vs |F|^(m-s).
  cost_model_challenges:
    - Omitted table construction (OBJ-6).
    - The A5 "store not charged" ceiling does not cover construction, which is operations.
  reduction_and_scope_challenges:
    - >-
      "The decomposition-oracle family cannot buy its way below rho" is false
      unconditioned. Proposed: "Given a decomposition oracle no better than
      generic m-SUM meet-in-the-middle, no m-summand index-calculus cell falls
      below the vOW rho column at any listed degree" (at any store once OBJ-6
      is applied).
    - >-
      J4 minor: raw enum_d_independent_everywhere is false, but the manifest's
      enum_d_independent is true.
  proof_architecture_challenges:
    - >-
      Nearby-object: the genus-g Jacobian shares p and is not separated. The
      missing separator is a genus-1 lower bound on decomposition-oracle cost.
    - Method ceiling with construction counted: 2*sqrt(m! N |F|) > sqrt(N).
  narrowest_supported_statement: >-
    At 3c97c0d40:
    (1) amended C-FLOOR-REPRO cannot detect yield-term, even-m oracle-exponent
        or budget errors, and its signature rejects faithful code while
        accepting an m!-free mutant;
    (2) the run tripped A1's stop rule without stopping;
    (3) under its own oracle law the accounting gives the same no-sub-rho
        verdict where index calculus is known to win, so the negative follows
        from HEUR-GENERIC-MSUM, not from binary curves;
    (4) every reported sub-rho cell depends on an unbuilt table.
    Nothing here bears on whether a sub-generic oracle exists on binary curves.
  next_concrete_action: >-
    In one decision, before any row of the run enters an EV record, the
    Coordinator: records and adjudicates the untriggered A1 stop on
    RUN-SEMBIN-c68773 as a procedure deviation; replaces C-FLOOR-REPRO with
    proposed_gate through an additive amendment; and routes OBJ-6 to the J1
    owner.
  artifact_paths:
    - coordination/goals/GOAL-SEMBIN-5078bc/reviews/TASK-20260928-3f90b8/{j2_mutation_harness.py, j2_results.json, j2_mutants/, ptm_known_false_objects.py, ptm_results.json, build_term_audit.py, build_term_audit.json}
    - report.md (refused by harness; this text is its content)
  citations:
    - {id: KN-LIT-011, what: Shoup 1997, provenance: kb}
    - {id: KN-LIT-013, what: Corrigan-Gibbs-Kogan 2018, provenance: kb}
    - id: KN-LIT-92caf4
      what: >-
        GTTD ePrint 2004/153. Sec 2.2: factor-u decomposition; Harley
        O~(q^(2-2/(g+1))). Sec 4: a ~ q^(g(r-1))/g!. Thm 1: O~(q^(2-2/g)).
      provenance: retrieved
      verified_by: TASK-20260928-3f90b8
    - {id: KN-LIT-001/002/005/023, provenance: kb, note: titles only}
    - {what: "L_q[1/2, sqrt 2]; Dickman rho reference values", provenance: recalled, note: comparison only}
```

## 5. review_attestation

```yaml
review_attestation:
  task_id: TASK-20260928-3f90b8
  role: red-team
  joints_owned: [J2, proves_too_much]
  independent_session: true
  originated_claim: false
  requested_policy: review-adversarial
  resolved_model_id: claude-opus-5-5   # session-reported, not probe-verified
  model_verified: false
  snapshot_commit: 3c97c0d40
  paths_read:
    - AGENTS.md
    - agents/red-team.md
    - ledger/handoffs/TASK-20260928-e4f7b2.yaml (whole file; see D1)
    - experiments/EXP-SEMBIN-04ec3c/specification.yaml
    - experiments/EXP-SEMBIN-04ec3c/code/memory_charged_family.py
    - experiments/EXP-SEMBIN-04ec3c/runs/RUN-SEMBIN-c68773/{manifest.yaml, raw-result.json, command.txt, environment.json, timing.json, artifact-digests.json}
    - git log of 3c97c0d40
    - knowledge/literature/{KN-LIT-011, -013, -164, -92caf4}.md
    - eprint.iacr.org/2004/153.pdf
  not_read:
    - DEC-20260928-7c3d91
    - RESULTS.md (absent)
    - sibling dirs TASK-20260928-{4e5c26, a1c7e5, d8b371} (present, not opened)
  read_sibling_reports: false
  verdict: {J2: breaks, proves_too_much: breaks}
  procedure_deviations:
    - id: D1
      text: >-
        My first read of the handoff returned coordinator_prior (lines 102-133)
        before any verdict. Neither verdict depends on it; both rest on
        executed runs and contradict the prior on mechanism.
    - id: D2
      text: >-
        No committed handoff card for TASK-20260928-3f90b8 exists, so
        `archived_by` could not be verified. This is for the dispatcher to
        record.
    - id: D3
      text: The kb MCP server was not exposed; I used grep over knowledge/ instead.
    - id: D4
      text: >-
        Two Dickman-rho schemes were rejected (absolute-error trapezoid;
        forward-unstable Heun on ln rho). The final averaging scheme matches
        1 - ln u exactly at u = 1.5 and 2, and changes by < 3e-4 bits at u = 90
        when h is halved. No reported number comes from a rejected scheme.
    - id: D5
      text: >-
        Coordinator relayed a resume after an API spend-limit interruption. It
        changed no scope or verdict.
    - id: D6
      text: >-
        The harness refused the write of report.md; its content is returned
        inline for the archive task.
  committed: false
```

**Reproduce:** from the task directory, run `python3 j2_mutation_harness.py` (about 2 min), `python3 build_term_audit.py`, and `python3 ptm_known_false_objects.py`. All three refuse to run if the committed driver or raw-result hashes don't match the digests the run recorded.