# Red Team Report — TASK-20260803-005 (RT-20260803-005)

Independent adversarial review of frozen amendment
`PA-IT-001-v3-rc44-repair-4` (EXP-IT-001), snapshot commit
`3b93abccee76`, BATCH-044, GOAL-ECDLP-001.

Claim under review: whether `PA-IT-001-v3-rc44-repair-4` closes all
`RT-20260802-314` blockers (B1–B3) under `DEC-20260802-233`, preserves
RC-43 non-conflicting closures, and is machine-loadable so a later toy
Executor batch could be admitted against this contract.

Claim ceiling: **design review only.** No experiment, run, timing, or
statistic is asserted. Arithmetic below uses frozen constants from the
committed snapshot text.

## Verdict: REVISE

RT-314 **B1, B2, and B3 are substantively closed** in the frozen text:
`c_smart=8` makes `C_special_smart/matched_rho ≈ 0.176 < 0.7` at the
pinned plant (`bits=20`); `matched_rho` is restated; an explicit supersession
clause governs over spec v3's quadratic `20*(log2 N)^2`; density abscissa is
restored to `{20,24,28}` with HEUR freeze; RC-43 command binding, M1/M3
certificates, null gate, and Pareto axes are preserved.

**Two mandatory admission blockers remain**, both repairable:

1. **YAML parse failure** — `yaml.safe_load` on the frozen amendment fails
   at line 205 (unquoted acceptance criterion with an embedded colon). The
   binding Executor entrypoint loads amendments by YAML; an unparseable overlay
   is not a durable contract.
2. **Missing null-recompute script** — `recompute_null_plant_from_ledger.py`
   is listed in `implementation_archive_manifest` and the contract declares
   absence ⇒ `contract_invalid`, but the file is absent from the repository
   at snapshot `3b93abccee76`.

Hence REVISE, not PASS. Content is coherent enough that FAIL is unwarranted.

---

## Attack checklist

| # | Check | Result |
|---|-------|--------|
| 1 | YAML parseability | **FAIL** — `ScannerError` line 205 col 59 |
| 2 | RT-314-B1 structural headroom | **PASS** — ratio ≈0.176 at bits=20 |
| 3 | RT-314-B2 pin/supersede/discretion | **PASS** |
| 4 | RT-314-B3 density {20,24,28} + HEUR freeze | **PASS** |
| 5 | RC-43 command/cert/null/comparator/Pareto | **PASS** (wording) |
| 6 | `recompute_null_plant_from_ledger.py` present | **FAIL** — path declared, file missing |
| 7 | Cheapest admission-breaking mutation | Unquote line 205 (already broken) or restore `c_smart=64` |

---

## Blocking findings

### RT-044-Y1 — frozen amendment fails `yaml.safe_load` (harness blocker)

- **Frozen clause:** `experiments/EXP-IT-001/amendments/PA-IT-001-v3-rc44-repair-4.yaml#repairs[R4-FIX-PRESERVE-M1].acceptance_criteria[3]` — line 205: `- pullback_evaluated: true and relation_reverified: true` (unquoted).
- **Finding.** PyYAML raises `mapping values are not allowed here` because the embedded `relation_reverified: true` is parsed as a nested mapping key inside an unquoted scalar. The superseded overlay `PA-IT-001-v3-rc43-repair-3` quoted the same criterion (`'pullback_evaluated: true and relation_reverified: true'`) and parses cleanly — this is a regression introduced in RC-44.
- **Impact.** `run_bounded_toy.py --amendment …/PA-IT-001-v3-rc44-repair-4.yaml` cannot load the contract. R4-FIX-PRESERVE-CMD binds that entrypoint; a non-loadable amendment voids the command-binding closure at runtime even though the prose strings are frozen.
- **Cheapest falsification (no run).** `python3 -c "import yaml; yaml.safe_load(open('…/PA-IT-001-v3-rc44-repair-4.yaml'))"` at commit `3b93abccee76` → `ScannerError`.

### RT-044-M2 — null-recompute script path declared but file absent (RT-244-M2 not implementation-closed)

- **Frozen clauses:**
  - `#implementation_archive_manifest` lists `experiments/EXP-IT-001/implementation/recompute_null_plant_from_ledger.py`
  - `#repairs[R4-FIX-PRESERVE-M2]` — "Missing script => contract_invalid / not completed_valid"
  - `control-matrix.yaml#CTRL-NULL-IT-PLANT.recompute_script` (same path)
- **Finding.** `git ls-tree -r 3b93abccee76` shows no
  `recompute_null_plant_from_ledger.py` under `experiments/EXP-IT-001/implementation/`.
  RT-314 closed M2 only as **path-declared** on rc43; rc44 repeats the same
  manifest entry and invalidation rule but still does not ship the script.
  A future Executor pre-run archive check would fail immediately.
- **Cheapest falsification (no run).** `test ! -f experiments/EXP-IT-001/implementation/recompute_null_plant_from_ledger.py` at snapshot → true.

---

## RT-314 closure ledger (substantive content)

### RT-314-B1 — CLOSED (structural calibration)

At pinned `anomalous_plant_bits=20` with detector `#E(F_p)=p` ⇒ `N=p`,
`log2(p)=bits`:

| Quantity | Value |
|----------|------:|
| `matched_rho` = `0.886 · 2^(bits/2)` | 907.264 |
| `0.7 · matched_rho` | 635.085 |
| `C_special_smart` = `c_smart · bits`, `c_smart=8` | 160 |
| `C_special_smart / matched_rho` | **0.176** |
| Headroom `floor(0.45 · matched_rho)` | 408 |
| Max `R_xfer` if `C_path+C_pullback` saturates headroom | **0.626** |

The constant alone is below 0.7; with mandatory headroom the anomalous
positive control is structurally satisfiable at the pinned cell. This fixes
the rc43 inversion (`c_smart=64` gave ratio 1.41 at bits=20).

### RT-314-B2 — CLOSED (pin, restate, supersede)

- `anomalous_plant_bits: 20` frozen; density cells 24/28 explicitly excluded
  from the anomalous positive control.
- `matched_rho` restated as `ceil(0.886 * sqrt(N_star))` with
  `matched_rho_formula_id: ceil_0_886_sqrt_Nstar`.
- `C_special_smart_supersession` explicitly supersedes spec v3
  `experiment.inputs.cost_ledger.C_special.anomalous_trace_eq_1`
  (`20*(log2 N)^2`); quadratic form listed in `forbidden_as_anomalous_pass_threshold`.
- Single-branch `limb_binding` removes Executor formula choice on the anomalous arm.

### RT-314-B3 — CLOSED (density abscissa restored)

- `density_protocol.bits: [20, 24, 28]` with explicit supersession over
  rc36/rc43 `{16,18,20,22,24}` overlays.
- `multiplicity_method: bonferroni_3`; Wilson 95% CI preserved.
- `rho_special_freeze` binds HEUR-ISO-1 freeze to `{20,24,28}` before path search,
  matching spec v3 `density_universe.bits` and `density_freeze`.

### RC-43 preserved closures — CLOSED at wording

| Id | Status |
|----|--------|
| R4-FIX-PRESERVE-CMD | Closed — one entrypoint, frozen smoke/measure strings, no CLI discretion note |
| R4-FIX-PRESERVE-M1 | Wording closed; YAML encoding broken (RT-044-Y1) |
| R4-FIX-PRESERVE-M3 | Closed — MOV formula comparator-only ban restated |
| R4-FIX-PRESERVE-NULL | Closed — packaging gate + ledger artifacts named |
| R4-FIX-PRESERVE-PARETO | Closed — three-axis `sota_delta` + `dominated_by` + `non_solver_scope` |

---

## Major (non-blocking) findings

### RT-044-D1 — density scan still lacks null-object decay control (RT-314-D1 carryover)

Per inventor-protocol §3, the density estimand should name the parameter that
destroys the signal and include an identical measurement on the null object.
RC-44 restores the preregistered abscissa but does not add a null-graph density
control or a stated decay expectation across `{20,24,28}`. Non-blocking for
RT-314 closure but required before treating density outputs as evidence.

### RT-044-D2 — `c_smart=8` unit conversion still thin (RT-314-D3 carryover)

RC-44 discloses `c_smart=8` as an "explicit upper-bound conversion" from
O(log p) Smart field ops to group-op equivalents, which is better than
rc43's unjustified `64`. It still lacks an enumerated Smart-algorithm operation
count or a cited bound tying 8 to a concrete step tally. Non-blocking for
design admission once YAML and script blockers are fixed, but a future
`review-breakthrough`-tier promotion would need this spelled out.

### RT-044-D3 — two frozen command strings (RT-314-D2 carryover)

Smoke and measure are two strings under one entrypoint. Acceptable; flag
discretion is removed.

---

## Baseline comparison

- **`dominated_by`:** Pollard rho at exponent ½ (matched negation) — correct
  generic baseline for ordinary prime-order subgroups; rho dominates matched
  BSGS on memory at the same √N time (spec records `matched_BSGS =
  2·ceil(sqrt(N))`).
- **Closest specialized baseline:** Smart linear-time anomalous solve — now
  charged at plausible toy scale via `c_smart=8`, not the rc43-inverted `64`.
- **Pareto fields:** Honest for this design-only overlay (`sota_delta` all
  `not_applicable` with explicit `non_solver_scope`); no fabricated frontier
  claim.

## Scope limits

- Design review of frozen text at snapshot `3b93abccee76` only.
- Does **not** conclude the isogeny-transfer lane is dead, HEUR-ISO-1 false,
  or that toy-scale transfer cannot work — only that two harness-integrity
  defects block Executor admission today.
- H-IT-001 stays `specified`; GOAL-ECDLP-001 stays `active`.

## Required next action

Author `PA-IT-001-v3-rc44-repair-5` (or amend rc44 in a new snapshot task) that:

1. Quotes or restructures line 205 acceptance criteria so `yaml.safe_load`
   succeeds (restore rc43 quoting pattern).
2. Adds `experiments/EXP-IT-001/implementation/recompute_null_plant_from_ledger.py`
   to the repository **or** amends the manifest/invalidation rule if the script
   is intentionally deferred to a separate implementation task (current text
   forbids deferral).

Re-run independent `review-adversarial` after both fixes before any Executor run.

## Non-claims

No experiment performed. No implementation performed. No run, timing, or
statistic invented. No official research state changed.
