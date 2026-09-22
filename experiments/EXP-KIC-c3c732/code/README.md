# EXP-KIC-c3c732 N19 affine-plane SAT pilot

This package implements the frozen public-synthetic exact-three N19
point-decomposition diagnostic. Every cold worker reconstructs the same
152-point admitted affine-plane base from four seed points. The 12 external
solver controls instead reconstruct the exact two-point base `{G,-G}` and
disable the Q-in-base shortcut. Neither worker input carries a scalar, a
coverage cache, a base logarithm map, or a retained pair table.

All SAT arms use the same S3 equations, polynomial integer ordering
`x1 <= x2 <= x3`, native XOR rows, constant folding, linear square and
public-constant multiplication. Their only intended difference is x-domain
encoding: strong explicit one-hot76 with forward and reverse bit clauses,
factorized one-hot19 Frobenius shift, or binary5 cyclic shift. The fourth arm
is a separately compiled, fresh coordinate-only pair-sum MITM.

Stage A permits this command only:

```sh
python3 experiments/EXP-KIC-c3c732/code/runner.py --phase build
```

It compiles `native.cpp`, captures the compiler and binary, reads CMS
`--version`/`--help`, resolves executable and non-system-library symlinks
to regular bytes, archives and rehashes those bytes, then freezes the source,
base and exact 12+32 case manifests. It does not invoke a control or solver
instance.

The following commands are templates for **root alone**, each requiring its
own exact committed admission and explicit launch assignment:

```sh
python3 experiments/EXP-KIC-c3c732/code/runner.py --phase native --admission <committed-native-admission-path> --admission-commit <full-commit>
python3 experiments/EXP-KIC-c3c732/code/runner.py --phase controls --admission <committed-external-control-admission-path> --admission-commit <full-commit>
python3 experiments/EXP-KIC-c3c732/code/runner.py --phase science --admission <committed-science-admission-path> --admission-commit <full-commit>
```

Native phase is one Python driver with exactly one C++ control child.
External phase has 12 fresh one-worker CMS pipelines. Science has 32 fresh
workers in frozen case-major order: 24 CMS and eight native MITM children.
Each process uses sole-parent `wait4`, a fresh cwd/HOME/TMPDIR and its own
raw streams. CMS exit 15 plus `INDETERMINATE` is a declared censored
observation, distinct from process watchdog, memory cap and faults. A
declared science CMS censor stays in the fixed panel; identity, model, domain
and infrastructure faults stop later launches. No slot is retried.

Primary timing is each cold worker's launch-to-reap wall, including its child,
construction and replay. Parent preflight, file promotion and archive work
remain separately labeled in receipts and root supervisor measurements.
Static analysis uses only preserved receipts and never launches a new solver.
This finite diagnostic cannot imply a full index-calculus or security gain.
