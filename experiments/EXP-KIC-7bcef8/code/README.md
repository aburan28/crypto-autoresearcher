# EXP-KIC-7bcef8 native N19 pair transport

This is the frozen public-synthetic exact-three point-decomposition experiment.
The same C++ field, group, batch-addition, base-validation and query loop serve
three arms:

- **expanded** stores an inline pair of indices for each full point-sum key.
  The sorted i<=j traversal selects the first lexicographic pair.
- **canonical_poly** stores one normalized pair for each full signed-Frobenius
  orbit key and applies the query frame's inverse sign/Frobenius transform.
- **canonical_normal_x** builds the least normal basis and both five-nibble
  conversion maps afresh, stores one normalized pair per x-orbit key, and
  aligns y/sign only after a key hit.

Every arm constructs its table from the same four-seed, 152-point admitted
base and searches the same sorted Q-minus-P sequence. All hits return three
actual B points and undergo complete group replay. Infinity, cancellation
and repeated summands are supported. No worker receives a scalar, prior
coverage cache, full-group map or retained table.

Stage A permits **only** implementation, static source checks and compilation:

```sh
python3 experiments/EXP-KIC-7bcef8/code/runner.py --phase build
```

Root alone supplies literal full-40-hex committed admissions and launches the
following commands serially, after separate source/control/checker gates:

```sh
python3 experiments/EXP-KIC-7bcef8/code/runner.py --phase control --admission <committed-control-admission> --admission-commit <full40hex>
python3 experiments/EXP-KIC-7bcef8/code/runner.py --phase checker --admission <committed-checker-admission> --admission-commit <full40hex>
python3 experiments/EXP-KIC-7bcef8/code/runner.py --phase benchmark --admission <committed-benchmark-admission> --admission-commit <full40hex>
```

Control mode exports all table rows, exact membership bitvectors for the
262,543-point public subgroup universe, 6,909 target verdicts, 153 exception
verdicts, arithmetic and conversion controls, and real rejected forgeries.
The independent Python checker uses its own long-division field multiplication,
Euclidean inverse and point law. Its table reuse is validation only, never
benchmark timing.

Benchmark mode runs the frozen 144-cell schedule as **direct native child
processes** without a Python worker inside the primary boundary. Each cell
has a fresh cwd/HOME/TMPDIR. Popen-to-sole-wait4-reap wall includes startup,
base and table construction, normal preparation where applicable, all query
probes, transport, replay and output. Parent admission/hash/validation/archive
costs are separate. Phase raw archives are immutable; the aggregate archive
is written only after a complete benchmark. A failed or censored slot stops
later launches and keeps actual partial receipts, with no retry.

Six repeats are technical measurements on each of eight fixed public targets,
not 48 independent target samples. This finite PDP result makes no IC, rho,
asymptotic or security claim. No network publication is part of this task.
