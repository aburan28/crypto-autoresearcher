# Exact metadata scorer and unavailable launcher

This additive correction implements TASK-20260908-6fa062 under the frozen
BATCH-eaf08d protocol for EXP-CRYPTO-5e8beb. It contains no scientific launch
path. Its tests use artificial precomputed scores only. Original implementation,
independent checker, scientific fixtures and specification remain untouched.

`panel_scoring.score_panel_advantage(metadata)` is a pure function. Its input is
a plain dictionary with `panels`, `validity`, and `controls`:

* `panels` is a list of exactly 32 dictionaries, each with exactly `N`, `q`,
  `kernel`, `coordinate_delta`, and `nulls`. The complete identity domain is
  N=11,17; q=2,3,4,5; kernel=R1,R2,R3,R4. N and q are integers (booleans and
  floats rejected), and kernel is a string.
* Each delta is exactly `{"numerator": integer, "denominator": integer}` with
  positive denominator, gcd=1, and value in [0,1]. Zero is 0/1. Booleans,
  floats, string numbers, missing or extra fields, and nonreduced values are
  rejected. Output gaps may be negative and remain reduced exact fractions.
* `nulls` is a list of exactly 32 dictionaries with exactly `seed` and `delta`.
  Seeds are integer labels 0..31, each present once. Equal numeric values with
  different labels remain distinct observations; they are not IID claims.
* `validity` must be literally `True` to permit a positive or negative outcome.
  It represents the caller's aggregate assertion of complete provenance-valid,
  calibration-valid, transcript-valid scientific evidence. This scorer cannot
  verify that assertion.
* `controls` maps exactly the seven names `exact_identity_constant`,
  `C15_cosets`, `hidden_uniform`, `public_prime_rigidity`, `matched_sizes`,
  `full_joint_and_freshness`, `independent_exact_tables` to literal `True`.
  Missing, false, nonboolean or unknown gates yield
  `incomplete_or_invalid_evidence`, even when a pair qualifies. Additional
  control names also make evidence invalid. Missing `validity`/`controls` is
  an invalid-gate result; missing or malformed panel data raises `SchemaError`.

Structural schema failures raise `SchemaError` before a score result exists;
they must never be translated to a negative outcome. Successful parsing always
returns all 32 full panel rows, all 1024 labeled null scores, and all 16 pairs,
even for invalid gates. Rows are ordered by N, q, kernel; nulls by seed; pairs
by q, kernel. Inputs may be reordered; output and input preservation are tested.
Each panel includes the exact mean, signed gap, strict-win count, threshold
flags and nonqualification reasons. Controls include explicit passed flags
and gating reasons. A panel qualifies iff gap >= 1/8 AND strict wins >= 24.
A pair qualifies iff the same q and kernel qualify at both N. With every gate
passed, at least one pair produces `finite_panel_advantage_with_valid_controls`;
zero pairs produces `complete_valid_panel_no_paired_advantage`. These are
metadata classifications, not findings from the synthetic tests.

`driver.check_launch_admission` and `driver.launch_scientific` always raise
`ScientificLaunchUnavailable` without inspecting their arguments. `driver.main`
and every CLI invocation print an unavailable message and return exit 3.
There is no successful admission state, binding parser, source authentication,
review authentication, genuine claim/lock verification, run allocation,
transport or backend implementation in this version. Even fully populated
synthetic binding files cannot enable it. File presence or matching hashes
alone would not authenticate authorization, review acceptance, or lock ownership.

Later integration needs separately approved work to convert independently
checked full scientific certificates into this exact schema, attest every
validity/control gate, and preserve all source/output provenance. The original
independent checker must remain independent; synthetic score arithmetic cannot
establish its agreement on real tables. The frozen scientific launch gate,
real lock/claim, authorized run identity, runtime/transport and end-to-end
certificate integration remain outstanding. No launch-readiness claim follows
from this correction or from its tests.

Run the tests from the repository root, choosing unused paths under the task's
scratch scope (the runner exclusively creates the chosen scratch directory and
evidence file):

```sh
python3 -B experiments/EXP-CRYPTO-5e8beb/implementation-v2/test_correction.py \
  --scratch coordination/goals/GOAL-CRYPTO-001/batches/BATCH-eaf08d/tasks/TASK-20260908-6fa062/scratch/reproduce-001 \
  --evidence coordination/goals/GOAL-CRYPTO-001/batches/BATCH-eaf08d/tasks/TASK-20260908-6fa062/scratch/reproduce-001.json
```

The evidence records exact artificial inputs and full outputs or schema-error
messages for all scorer cases, plus driver refusal and guarded side-effect
observations. Tests are deterministic, use no original scientific imports,
and require no external dependencies. Python `-B` prevents bytecode writes.
The test audit hook guards driver calls against process/network/write attempts;
scratch inventories and loaded-module inspection supplement that bounded check.
It is not an operating-system sandbox or a scientific execution receipt.
