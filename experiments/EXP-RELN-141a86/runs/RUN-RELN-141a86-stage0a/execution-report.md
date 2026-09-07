# Execution Report -- RUN-RELN-141a86-stage0a

## Scope

STAGE 0a ONLY of EXP-RELN-141a86 (version 1, approved, `approved_by:
coordinator`, `execution_authorized: true`, per DEC-20260907-93a502), per
handoff `TASK-20260907-4a304a`. Zero measured data was read. No Stage 0b
work was performed. This run STOPS here per the contract's own
`stopping_rules` and `ordering_control`, pending a Coordinator snapshot
archive of the frozen files and hash.

## Deliverables produced

- `candidate-list.yaml` -- 19 entries, transcribed from
  `ledger/hypotheses/H-RELN-427bfd.yaml` `candidate_invariants`, each with
  its statement, status, a grammar-notation expression (where one exists)
  and a canonical node count computed by
  `experiments/EXP-RELN-141a86/source/grammar_engine.py`'s own
  `node_count()` function -- never hand-counted.
- `grammar.yaml` -- faithful transcription of the frozen
  `frozen_pipeline.primary_engine.grammar` block (operators, leaf sets by
  pack, node-counting rule, `C_max = 12`, tie-break seed `20260906`,
  enumeration order).
- `environment.lock.json` -- honest PySR/Julia availability check (see
  below); no version asserted from memory.
- `control-tables/recovery-controls-closed-form.yaml` -- the five
  recovery-control closed forms (symbolic only, no measured cell read).
- `candidate-list-hash.txt` -- sha256 over the exact concatenation
  `candidate-list.yaml` + `grammar.yaml` + `environment.lock.json`, in that
  order, with individual file hashes recorded separately.
- `experiments/EXP-RELN-141a86/source/grammar_engine.py`,
  `constant_fit.py`, `pysr_harness.py` -- real, working, deterministic
  implementations (self-tested; see `stdout.log`).

## 1. Candidate-list entry count and computed node counts

19 entries, exactly matching H-RELN-427bfd's `candidate_invariants` list.

| id | computed node count | note |
|---|---|---|
| INV-1 (mean) | 9 | contract pre-stated; match |
| INV-2 (Delta from E_m) | 5 | structural identity, not an SR target (E_m not a grammar leaf) |
| INV-2prime (with-replacement E[Delta]) | 5 | |
| INV-2doubleprime (forced term \|W\|^3/4) | 5 | forced-mass lower-bound term only, not a full Delta expression |
| INV-3 (rho(S)=1) | 1 | trivial constant; discriminating content not expressible in this grammar |
| INV-4 (E^ord_m bound) | 17 | a bound, not an exact closed form; K treated as a free leaf |
| INV-4c | null | open conjecture; no independent closed form (null form uses INV-A1's expression, 9) |
| INV-5a | null | not applicable; exact curve reformulation, not Z/N-testable |
| INV-5b | null | open; no closed form conjectured yet |
| INV-6 | null | definitional set-recursion, not a scalar expression |
| INV-7 p_fail | 9 | contract pre-stated; match |
| INV-7 p_exist | 11 | contract pre-stated; match |
| INV-8 (d_reg) | 10 | contract pre-stated; match |
| INV-9 (floor 1-mu) | 3 | same tree shape as INV-A4 Delta |
| INV-A1 (Delta_random) | 9 | |
| INV-A2 (E[R_k]) | 5 | P_runs treated as a reference-function leaf |
| INV-A3 (Delta floor(W)) | 17 | |
| INV-A4 coverage | 7 | contract pre-stated; match |
| INV-A4 Delta | 3 | contract pre-stated; match |
| INV-A5 (T leading term) | 5 | leading-order term only |
| INV-A6 (Delta identity) | 7 | contract pre-stated; match |

Four entries (INV-4c, INV-5a, INV-5b, INV-6) have no closed-form grammar
expression and are recorded as `expression: null` with an explicit note in
`candidate-list.yaml`, rather than a fabricated formula.

## 2. Contract-pre-stated node-count verification

The contract's `node_counting_rule` text pre-states node counts for **five
recovery-control invariants** (INV-1, INV-7, INV-8, INV-A4, INV-A6), two of
which (INV-7, INV-A4) each carry two named sub-values, for **seven
individual stated values** in total. This run's own
`source/grammar_engine.py` `node_count()` function, applied to hand-built
expression trees for each, reproduced **all seven exactly**:

| target | contract value | engine-computed value | match |
|---|---|---|---|
| INV-1 mean | 9 | 9 | yes |
| INV-7 p_fail | 9 | 9 | yes |
| INV-7 p_exist | 11 | 11 | yes |
| INV-8 d_reg | 10 | 10 | yes |
| INV-A4 coverage | 7 | 7 | yes |
| INV-A4 Delta | 3 | 3 | yes |
| INV-A6 Delta | 7 | 7 | yes |

**No disagreement was found.** All seven values match the contract's
pre-stated values exactly; nothing needed escalation to the Coordinator on
this account.

## 3. PySR/Julia availability

Probed directly, no installation attempted:

```
python3 -c "import pysr; print(pysr.__version__)"
  -> ModuleNotFoundError: No module named 'pysr'
julia --version
  -> FileNotFoundError: [Errno 2] No such file or directory: 'julia'
```

Both PySR and Julia are **unavailable** in this run environment. Recorded
honestly as `pysr_available: false` in `environment.lock.json`, with the
exact commands and raw output. Per the contract's own
`secondary_engine.pinning` clause ("If the pinned release cannot be
installed in the run environment, the same applies [failed_infrastructure
for the PySR arm, never a result]"), the secondary engine arm is
unavailable in this environment; the primary exhaustive-grammar engine
stands alone. This is an anticipated, legitimate Stage-0a outcome per the
handoff's own constraints, not a blocker.

## 4. Hash

`candidate-list-hash.txt` sha256 (over `candidate-list.yaml` +
`grammar.yaml` + `environment.lock.json`, concatenated in that exact
order, raw bytes, no separators):

```
f1aec620f8cb19318e6d6459174bd79b80daf6dd46fdacf6afdf2468c7cac7f2
```

Individual file hashes (sha256):

- `candidate-list.yaml`: `7a3ab7865d94de46683c5a33c3873883ff95541a439e095e8d64d3dbadd331eb`
- `grammar.yaml`: `5ca6e2bc8f746effbf3e6542685b2393b1da633b53ea245486a992725824ed3d`
- `environment.lock.json`: `857b652082f3798ad26307b4171675c4b3a98e08bf5d5078b12cb29e4228737d`

Recomputation command recorded in `candidate-list-hash.txt` and
`command.txt`.

## 5. Deviations / anomalies

- None from the frozen protocol's Stage-0a scope. The dirty working tree
  at run time also contains an unrelated untracked directory
  (`experiments/EXP-RELN-82f487/source/`) from a concurrent or prior
  executor dispatch on a different experiment; it was not created, read,
  or modified by this run and is recorded in `manifest.yaml` for
  auditability.
- Four candidate-list entries (INV-4c, INV-5a, INV-5b, INV-6) have no
  closed-form grammar expression; recorded as `null` rather than
  fabricated, per AGENTS.md rule 5 and the executor's prohibition on
  fabricating outputs.

## 6. Stop

Per `frozen_pipeline.ordering_control` and `stopping_rules`, this run STOPS
here. Stage 0b (which reads measured FB3/DREG/sibling-enumeration tables)
may not begin until a Coordinator snapshot commit archives
`candidate-list.yaml`, `grammar.yaml`, `environment.lock.json`, the control
tables, and `candidate-list-hash.txt`, and the Stage-1 manifest records
this same hash and the archive commit. No ledger record was written or
edited by this run; no interpretation or hypothesis-status conclusion is
offered.
