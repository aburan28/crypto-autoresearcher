# Classical ECDLP finite diagnostic harness

The first admitted all-track pilot is complete: [report](../../experiments/EXP-ECDLP-fe3337/reports/run-20261025T0526Z/HEADER.md), [observations](../../experiments/EXP-ECDLP-fe3337/reports/run-20261025T0526Z/observations.md), [PDF](../../experiments/EXP-ECDLP-fe3337/reports/run-20261025T0526Z/report.pdf) and [sealed data](../../experiments/EXP-ECDLP-fe3337/runs/RUN-ECDLP-d7f049/parts-manifest.json). The repository supervisor records one output-validated batch, zero remaining trials and 241 rows from all ten tracks on eight public synthetic toy curves. Measurement used three concurrent module workers.

This implements finite exploratory diagnostics, not a new ECDLP solver. The larger discovery and blinded solver cohorts in the original plan are not completed by this pilot. Known methods and explicitly charged truth tables remain controls. No quantum computation or index calculus is included.

| Program | Tracks | Implemented object |
| --- | --- | --- |
| `src/circuit.cpp` | D, L4 | Total Boolean modular/EC scalar circuits; exact tagged boundaries; finite exact rational matchgate grammar |
| `src/padic_endo.cpp` | L1, L3 | Public p² section/defects; sign-matched predictor controls; certified known endomorphism actions |
| `src/sequences.cpp` | L2, L6 | EDS/coordinate identities, quadratic predictors/BM, exact finite residual automata and ambiguity |
| `src/algebraic.cpp` | L5, L7, L8 | Explicit branch/CRT controls, conditional coefficients, integer count/degree/divisibility audits |
| `src/lossy.cpp` | L9 | Exact full-pair entropy for 22 projections; 99 unrestricted and applicable 99 sign-matched null draws |

All programs accept `--self-test` or `--run FIXTURES_TSV FRESH_OUTPUT_JSONL`. They reject unsupported inputs and output overwrites. `protocol/fixtures.tsv`, `fixture-history.jsonl`, `fixture-certificate.json` and `pilot.json` define the cohort and scope. `src/fixtures.cpp` recreates the fixed manifest and all 85 candidates/rejections. `tests/` records development commands and limitations, including explicit disabling of unavailable leak detection during ASan/UBSan checks.

For a development self-test, from the repository root:

```sh
g++ -std=c++20 -O2 -Wall -Wextra -Wconversion -Werror \
  harness/classical_ecdlp_pilot/src/circuit.cpp -o /tmp/classical-circuit
/tmp/classical-circuit --self-test
```

The admitted end-to-end route uses the repository supervisor:

```sh
python3 tools/experiment_execution.py status \
  --plan experiments/EXP-ECDLP-fe3337/trial-plan.json
```

Its `run` operation uses a published live task claim and the actual owner/epoch. The completed frozen plan is idempotent and preserves its existing run; it is not a command to overwrite or repeat evidence. For a fresh scientific cohort, allocate fresh official IDs, generate a new packet with `protocol/admission/prepare_packet.py`, publish its exact source/input snapshot, require genuine preapproval and selector readiness, and claim its executor task. Do not reuse `ids.json` for a new campaign. Standing user authorization covers complete runnable experiments without another user confirmation.

The adapter compiles and self-tests sequentially, then launches five module processes in a pool of three. It checks the real supervisor parent/argv and hash bindings. All output is preserved in 64 predefined row-part slots below 60 KiB; the parts manifest verifies exact reconstruction. Both ordinary and null outcomes are retained. `output_validated` means output integrity, not independent scientific review, novelty or advantage.

The missing research operations remain explicit in each module: an EC-specific compositional cancellation rule, cheap target locator/coefficient/residue evaluator, public automaton orientation, or global planar/tag construction. A finite grammar's failure is scoped to that grammar.
