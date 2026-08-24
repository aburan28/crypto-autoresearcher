# Red Team Report — TASK-20260803-013 (RT-20260803-013)

Independent adversarial review of frozen amendment
`PA-IT-001-v3-rc45-repair-5` (EXP-IT-001), snapshot commit
`16f7b7bf8b9d8a483b6ef939e9ebcc2a0fcb4620`, BATCH-045, GOAL-ECDLP-001.

Claim under review: whether `PA-IT-001-v3-rc45-repair-5` closes
`RT-20260803-005` blockers **RT-044-Y1** and **RT-044-M2** under
`DEC-20260803-001` / `EV-IT-006`, without silently reopening RT-314-B1/B2/B3
or introducing a new harness-integrity blocker.

Claim ceiling: **design review only.** No experiment, run, timing, or
statistic is asserted. Arithmetic below uses frozen constants from the
committed snapshot text.

## Verdict: PASS

Named admission blockers from RT-20260803-005 are closed at this snapshot:

1. **RT-044-Y1** — `yaml.safe_load` succeeds on the frozen amendment
   (sha256 `06f76632…1384`). The double-colon M1 acceptance scalar that caused
   `ScannerError` in rc44 is quoted.
2. **RT-044-M2** — `experiments/EXP-IT-001/implementation/recompute_null_plant_from_ledger.py`
   exists as a blob (sha256 `0e13cf24…c2f088`), is listed in
   `implementation_archive_manifest`, and `py_compile`s. Plant predicate and
   `c_iso` match the driver/`it001_pure` conventions.

RT-314 **B1, B2, and B3 remain closed** (not silently reopened): `c_smart=8`,
pinned `anomalous_plant_bits=20`, density abscissa `{20,24,28}`, matched_rho
restatement, and quadratic Smart supersession are intact. RC-43
command/certificate/null/comparator/Pareto wording is preserved at the design
layer. No fraud or scope laundering. FAIL is unwarranted.

Non-blocking residuals (quote hygiene, CLI wiring, density null-decay,
`c_smart` enumeration) are recorded below and do not reopen the named
DEC-20260803-001 blockers.

---

## Attack checklist

| # | Check | Result |
|---|-------|--------|
| 1 | `yaml.safe_load` at `16f7b7bf8` | **PASS** — loads `protocol_amendment` dict |
| 2 | Null script blob + manifest at snapshot | **PASS** — present; listed; hashes match receipt |
| 3 | RT-314-B1 structural headroom | **PASS** — ratio ≈0.176 at bits=20 |
| 4 | RT-314-B2 pin/supersede/discretion | **PASS** — preserved |
| 5 | RT-314-B3 density `{20,24,28}` + HEUR freeze | **PASS** — preserved |
| 6 | Command / cert / Pareto honesty (wording) | **PASS** — preserved; CLI wiring gap = D2 |
| 7 | New harness blocker (false presence, parse bomb, path mismatch) | **PASS** — none blocking |
| 8 | Cheapest admission-breaking mutation | Unquote M1 line 204 (would revive Y1) |

---

## Closure of RT-20260803-005 blockers

### RT-044-Y1 — CLOSED

- **Prior defect:** rc44 line 205 unquoted
  `pullback_evaluated: true and relation_reverified: true` → PyYAML
  `ScannerError`.
- **Frozen repair:** R5-FIX-Y1 + quoted R5-FIX-PRESERVE-M1 acceptance criteria
  (including `'pullback_evaluated: true and relation_reverified: true'`).
- **Falsification (no run):**
  `python3 -c "import yaml; yaml.safe_load(open('…/PA-IT-001-v3-rc45-repair-5.yaml'))"`
  at commit `16f7b7bf8` → success.

### RT-044-M2 — CLOSED

- **Prior defect:** path listed in `implementation_archive_manifest` with
  absence ⇒ `contract_invalid`, but no blob at rc44 snapshot.
- **Frozen repair:** R5-FIX-M2 ships the script in the TASK-20260803-012
  proposal snapshot and keeps the manifest entry + invalidation rule.
- **Falsification (no run):**
  `git ls-tree 16f7b7bf8 -- experiments/EXP-IT-001/implementation/recompute_null_plant_from_ledger.py`
  → blob `dba5cb479d29…`; sha256 matches authoring provenance and snapshot
  receipt. Script is a presence/integrity helper, not a cryptanalytic claim.

---

## RT-314 reopen check (must stay closed)

### RT-314-B1 — CLOSED (preserved)

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

No silent restore of rc43's inverted `c_smart=64`.

### RT-314-B2 — CLOSED (preserved)

- `anomalous_plant_bits: 20` frozen; density cells 24/28 excluded from anomalous
  positive control.
- `matched_rho` restated; `matched_rho_formula_id: ceil_0_886_sqrt_Nstar`.
- `C_special_smart_supersession` still forbids quadratic `20*(log2 N)^2` as
  anomalous pass threshold.
- Single-branch `limb_binding` removes Executor formula choice on the anomalous arm.

### RT-314-B3 — CLOSED (preserved)

- `density_protocol.bits: [20, 24, 28]` with supersession over `{16,18,20,22,24}`.
- `multiplicity_method: bonferroni_3`; Wilson 95% CI; HEUR-ISO-1 freeze bound to
  the same abscissa.

---

## Command-binding / certificate / Pareto

| Limb | Status |
|------|--------|
| R5-FIX-PRESERVE-CMD | One binding entrypoint; frozen smoke/measure strings; no CLI-discretion note |
| R5-FIX-PRESERVE-M1 | Quoted; start/end nonspecial + reverse + pullback/relation |
| R5-FIX-PRESERVE-M3 | MOV formula comparator-only ban restated |
| R5-FIX-PRESERVE-NULL | Packaging gate + ledger artifacts named |
| R5-FIX-PRESERVE-PARETO | Three-axis `sota_delta` + `dominated_by` + `non_solver_scope` |

Runtime note (non-blocking D2): the frozen CLI flags are not implemented by
today's `run_bounded_toy.py` (no argparse; hardcoded older amendment id). That
is an implementation-wiring gap for a future Executor batch, not a false
presence claim about this design overlay.

Manifest audit: every path in `implementation_archive_manifest` resolves to a
blob at `16f7b7bf8` (no false-presence entries).

---

## Non-blocking findings

### RT-045-D1 — residual colon prose still coerces some list items to dicts

Several non-M1 acceptance criteria and two metrics still contain unquoted
`key: value` tokens and load as mappings (`B1[2]`, `B2[0]`, `B2[1]`, `B3[1]`,
`metrics[0..1]`). Parse still succeeds. Capsule asked for quoted strings on
colon-bearing acceptance criteria; R5-FIX-Y1's acceptance gate only requires
M1 quoting + safe_load. Quote the residuals (rc43 pattern) before any Executor
string equality checks on acceptance criteria.

### RT-045-D2 — frozen CLI ≠ entrypoint surface (carryover)

See command-binding table note.

### RT-045-D3 / D4 — density null-decay and `c_smart` enumeration (carryovers)

Unchanged from RT-044-D1 / D2. Required before treating density or Smart-cost
outputs as evidence; not required to close DEC-20260803-001.

### RT-045-D5 — two command strings (RT-044-C1 carryover)

DEC-20260803-001 / BATCH-045 capsule did not require collapsing smoke+measure
into one string. Not re-raised as a blocker.

---

## Baseline comparison

- **`dominated_by`:** Pollard rho at exponent ½ (matched negation) — correct
  generic baseline; overlay does not claim a sub-rho exponent.
- **Closest specialized baseline:** Smart linear-time anomalous solve — still
  charged at plausible toy scale via `c_smart=8`.
- **Pareto fields:** Honest for this design-only overlay (`sota_delta` all
  `not_applicable` with explicit `non_solver_scope`); no fabricated frontier
  claim. `dominated_by` is set, not an unchecked `null`.

## Scope limits

- Design review of frozen text + M2 blob presence at snapshot `16f7b7bf8` only.
- Does **not** authorize Executor admission by itself beyond closing the named
  repair blockers; Coordinator decides next transition.
- Does **not** conclude the isogeny-transfer lane is dead or supported.
- H-IT-001 stays `specified`; GOAL-ECDLP-001 stays `active`.

## Required next action

Coordinator may adopt PASS on the RC-45 repair closures. Preferred pre-run
hygiene (non-blocking): quote residual colon-bearing acceptance/metrics
scalars and wire the binding entrypoint to the frozen `--amendment` CLI under
a separate implementation task. Then consider Executor admission only under a
new decision, not under this design-review PASS alone.

## Non-claims

No experiment performed. No implementation performed beyond reading the
archived M2 helper. No run, timing, or statistic invented. No official
research state changed.
