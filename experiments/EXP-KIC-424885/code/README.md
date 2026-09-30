# EXP-KIC-424885 exact N7 pipeline

This package implements the frozen public-synthetic GF(2^7) factor-base SAT
discriminator in `research/golden_factor_base_sat_20260921/design_completion.json`.
The timed worker receives a point `Q`, arm name, base recipe and pinned solver
path. It receives no scalar, no precomputed factor base, no relation table and
no full subgroup lookup. Candidate and null bases are reconstructed inside
each relevant worker. The direct arm uses batch-affine point-pair MITM.

Stage A executes only native controls and source, case, dependency and solver
custody. Run from the checkout root:

`python3 experiments/EXP-KIC-424885/code/tests.py --native`

`python3 experiments/EXP-KIC-424885/code/runner.py --phase stage-a`

Later phases require a Coordinator-committed admission file, its exact commit
and an explicit sole-launch assignment. The command shapes are:

`python3 experiments/EXP-KIC-424885/code/runner.py --phase controls --admission <committed-path> --admission-commit <commit>`

`python3 experiments/EXP-KIC-424885/code/runner.py --phase science --admission <committed-path> --admission-commit <commit>`

The 70 control and 64 scientific worker slots are immutable and never retried.
Every worker uses a fresh process and directory. CMS descendants use the
frozen single-thread argv, with exact source/model/group checks. Outer wall
time ends at `wait4` reap; per-PID CPU/RSS and sampled footprint are recorded
with their scopes. Build cost and post-run static propagation are separate.
Each admitted phase has a nonblocking parent lock and a permanent launch
marker; a partial batch requires Coordinator review and cannot automatically
resume. Declared solver/resource limits remain censored rows in the fixed
panel, while model, source, and infrastructure faults stop later children.
The supervisor's actual terminal streams are captured in phase-specific logs.

`checker.py` uses independent bitwise field and point arithmetic for finite
oracle/replay calculations; it shares only the declared curve parameters and
point encoding with `field.py`. `circuits.py` retains internal XOR RHS values
and exports CMS native-XOR rows by the frozen convention. The native control
suite tests its gate truth tables and arithmetic before any CMS instance.

Every reported outcome is limited to this finite N7 public-synthetic setup.
