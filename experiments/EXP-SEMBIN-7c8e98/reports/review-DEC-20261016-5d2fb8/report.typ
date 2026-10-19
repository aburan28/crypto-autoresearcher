#set page(paper: "a4", margin: 2cm)
#set text(size: 10pt)

= Evidence review: EXP-SEMBIN-7c8e98 / RUN-SEMBIN-9ecb77

Decision `DEC-20261016-5d2fb8` (refine) · Evidence `EV-SEMBIN-3e91a7` · Hypothesis `H-SEMBIN-371c51` · Idea `IDEA-20261010-066c44` · Question `RQ-SEMBIN-fa2e3f` · Goal `GOAL-SEMBIN-5078bc` · Approval `DEC-20261012-b4ec9c` · Producer task `TASK-20261012-d17d69` · Snapshot task `TASK-20261012-c5a016` · 2026-10-16

#table(
  columns: 2,
  [*Decision*], [refine. The run set is invalid as evidence, and H-SEMBIN-371c51 is untested (status unchanged).],
  [*Evidence strength*], [inconclusive (direction neutral)],
  [*Claim tier*], [toy],
  [*Scoped claim*], [None. On the one chained S_3 system over F_2[z]/(z^5+z^2+1) (k = 2, target z = 6, cap 4), the frozen driver did not measure the refutation degree. Its recorded value of 1 is an artifact of generator truncation.],
  [*Proof status*], [derivation (code reading). The counterexample has not been executed yet.],
  [*Success criterion*], [No cost was measured, so there is no improvement over the IC baseline. The gap to matched rho is not measured by this experiment, and no GAE band applies.],
)

Earlier run reports: none. No `reports/run-*/` directory exists for this experiment; the run was reviewed before publication.

== Validity (checked before interpretation)

- Run count: 1 of 1. Seeds: none (deterministic). The `manifest.yaml` metrics match `raw-result.json`.
- *Defect V1, packaging.* The manifest lacks `run.id`, `status`, `code.commit`, `code.command`, `environment`, `inputs`, `timing` and `result`. The files `command.txt`, `environment.json`, `stdout.log`, `stderr.log` and `execution-receipt.json` are missing. Nothing is committed or published.
- *Defect V2, checker blind.* `check.py` recomputes `run.census()` from the same `run.py`. Its exit 0 shows determinism, not correctness.
- *Defect V3, unsound and target-blind instrument* (see below).

== Observation (measured)

`raw-result.json` records:

- `selected_target` 6, `solution_count` 0, `refutation_degree` 1;
- `planted_ok` true, `matrix_holds` false, `beyond_matrix` true;
- `column_count` 562, `modulus` 37, `n_variables` 11, `bound` 4.

== Comparison

The prediction was degree 4 and the recorded value is 1. The difference is not read as a measurement (see Inference).

#figure(
  image("graph.svg", width: 100%),
  caption: [Closure degree: preregistered prediction and cap (4, declared) against the recorded value for RUN-SEMBIN-9ecb77 (1, measured but invalid) and the frozen instrument's derived output for any target and for a satisfiable control (both 1, derived, not executed). n = 1, no uncertainty recorded. Data: `graph-data.json`.],
)

== Inference: derivation of the instrument defect

`contains_one()` (lines 202–212 of `run.py`) replaces each generator and each product by its truncation:

```python
truncated = {mask for mask in masks if popcount(mask) <= degree}
```

Truncation is not an ideal consequence. A sound degree-D closure admits a product m·f only when deg(m·f) ≤ D, and never drops monomials.

(a) *Unsound.* The equation x0·x1 + 1 = 0 is encoded `[{3, 0}]` and is satisfied at x0 = x1 = 1. Its degree-1 truncation is {0}, so `contains_one([{3, 0}], 1)` returns True.

(b) *Target-blind.* S_3(u, x1, x2) has:

- a constant 1, whose coefficient has only bit 0 set;
- bit-monomials of popcount 2 (the squared part, whose cross terms cancel in pairs) and 3 (the cubic);
- no popcount-1 terms.

So its coordinate-0 equation truncates to {0} at D = 1, and the instrument returns 1 for every target in 1..31.

The planted controls (unit, linear, empty, and `sound_ok` on an unsatisfiable system) cannot detect truncation.

Reproduction, to be executed by the dispatching session; it should print `True True`:

```sh
python3 -c "import importlib.util as u;s=u.spec_from_file_location('r','experiments/EXP-SEMBIN-7c8e98/implementation/run.py');m=u.module_from_spec(s);s.loader.exec_module(m);print(m.contains_one([{3,0}],1), m.satisfies([{3,0}],3))"
```

The run is therefore invalid as evidence. This is implementation signal, not a negative mathematical result. The contract's literal falsification clause presupposes a valid measurement and is not applied. The frozen contract is not edited.

== Limitation

- One toy system: 11 bits, m = 3. Nothing here bears on larger m, batch rates, exponents or deployed curves.
- The counterexample is derived, not executed.
- `build_system` and `solution_count` were not re-derived, and the source hashes were not re-hashed.
- The analysis lives in EV-SEMBIN-3e91a7 and in this report. `analysis.md` could not be written, because the subagent harness refuses `.md` writes.
- *Rendering gap:* the reviewing subagent has no shell. This PDF and the SVG render must be produced and inspected by the dispatching session before the ledger archive.

== Next actions

+ Dispatching session: run `allocate_id.py --check` on both ids, execute the reproduction line, render and inspect `report.pdf`, and run `tools/validate_ledger.py`.
+ Executor: republish RUN-SEMBIN-9ecb77 with a schema-complete manifest and its companion artifacts, marked invalid_instrument, without rerunning the trial. Then the snapshot archive, then the ledger archive.
+ `/design-experiment IDEA-20261010-066c44`: write a new versioned contract with a sound closure (m·f only if deg ≤ D, no truncation), satisfiable controls above the cap, an independent checker, and a blind re-derivation. The prediction of 4 is frozen before execution.
+ GOAL-SEMBIN-5078bc stays active, with one next action: the corrected closure-degree contract.

Canonical graphs checked and left unchanged: no canonical graph cites EXP-SEMBIN-7c8e98, and this decision changes no supported content.
