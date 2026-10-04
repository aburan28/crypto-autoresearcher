# EXP-ECDLP-651b94 prospective spectral collision pipeline

This directory is the exact executor output for `TASK-20260906-9393c3`.  It
implements the frozen deterministic components of the effective contract:
`specification.yaml` SHA-256
`97b44f40c8f9d52a587cf4fd9788dd391e42ce5c6dab8ec212a8af34cdfa4eee`, plus
the additive approval `DEC-20260906-f73475`.  It has not run a fixture sweep,
collision census, null shuffle, control, candidate search, timing matrix, or
scientific measurement.

`driver.py` maps the protocol to code as follows: `fixture_candidates` and
`select_fixtures` enforce the exact `b in {9,11}`, first-32-primes,
`B=0..31`, nonsingular/nonsupersingular, and `[127,509]` subgroup rules;
`stream_digest`, `rejection_draw`, and `fisher_yates` implement the frozen
SHA-256 stream; `rho_step` implements the public `x mod 3` map and scalar
recurrence; `collision_census` performs the all-start first-repeat accounting;
`binary_verifier` isolates the recovered-label check from the producer;
`occupancy_assignment` makes seven matched shuffles possible; and
`pooled_null_cost`, `cell_difference`, and `heldout_branch` preserve the
charged-cost and finite held-out decision rule.  `cayley_*` is a separate
reversible calibration and is never used to infer a rho spectral gap.

The future runner must also persist all `canonical_artifact_layout` paths and
execute the full named controls: exact Cayley row/column/Fourier/TV checks,
relabel identity, constant-map and altered-scalar known-false checks,
occupancy counts, and all three coordinate models. Cayley numerical work uses
`mpmath` with `workprec=128`, including the numerical/Fourier eigenvalue
multiset comparison and explicit point-basis total-variation curve; its
interpretation remains separate from rho.

Safe commands used here are:

```sh
python3 driver.py                 # prints dry-run coverage only
python3 tests.py                  # 16 synthetic contract tests only
```

Those 16 synthetic cases preceded the final Cayley/control/runner integration.
They are retained as historical bounded checks, not presented as final-code test
coverage. The final source digest is
`3f8a862c0bec7d5ddab3b6de9b104e0a61a6f0530dc7dfdae912d652985d4b75`;
subsequent validation was static compilation and whitespace checking only.

`verify_launch_lock` performs detached Ed25519 verification and compares actual
driver/plan hashes, frozen resources, and an exact runtime binding when a
future admitted runner supplies the separately committed Coordinator trust
key. `--launch-lock <path>` remains fail-closed because this task was not given
those trust inputs.
A real future launch requires an allocated run ID and archived dispatch
handoff, snapshot receipt for these five files, independent implementation
review, and a separate trusted verifier that cryptographically verifies an
explicit committed Coordinator trust key/signature and compares the actual
specification, driver, execution-plan, runtime/dependency, resource, and
review bindings.  Boolean approval fields or a nonempty signature are not
accepted as verification.  No standard verifier was found in the inspected
local control-plane sources.
