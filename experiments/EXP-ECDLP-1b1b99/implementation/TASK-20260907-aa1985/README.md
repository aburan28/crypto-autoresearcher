# `EXP-ECDLP-1b1b99` prospective backend

This six-file package completes the previously missing executable backend for
the approved, frozen toy calibration. It remains **non-measuring**: the default
command only prints coverage and creates no fixture, candidate search, timing
block, run directory, or scientific artifact.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 driver.py --dry-run
```

The package is bound to frozen specification SHA-256
`b331940a2f5215058d84845f953365c39dac78b4a0d4894604e90b06bc2f3fff`, additive
approval `DEC-20260906-f73475`, and this implementation authorization
`DEC-20260907-b21c85`. It supersedes no historical artifact: the partial
`TASK-20260906-2f2a56` package is retained as an immutable reuse input.

## What code now exists

`driver.py` provides the complete prospective path below. Each routine is
implemented but not invoked by this task.

| Frozen obligation | Executable implementation |
| --- | --- |
| Full rational `E0[3]` | Field-point enumeration requires eight nonzero 3-torsion points and canonically returns four +-paired kernels. |
| Four normalized degree-three maps | `normalized_velu_map` constructs each codomain and image formula; `construct_class_fixture` builds all four. |
| Exact duals and model normalization | `exact_dual` enumerates rational dual kernels, constructs a normalized candidate, finds its explicit short-Weierstrass isomorphism, and requires `ψφ=[3]` on a non-kernel selector. |
| `j=1728` automorphism and sign | `j1728_automorphism`, `sqrt_minus_one_mod_prime`, and `choose_eigenvalue_sign`; `m=3λ mod r` is retained explicitly. |
| Conductor-three data | `conductor3_certificate` records `Dπ=-4fπ²`, `v3(fπ)=1`, inertness, four models, and rational-kernel crosschecks. The order-theoretic implication still needs independent review. |
| Scalar comparator | Binary, wNAF widths 2–5, and a labelled pinned affine-library arm; selection is restricted to seed `606101`, `q=256`. |
| All frozen controls | `verify_controls` implements composition, coordinate conjugation, level, wrong-sign identity, and the floor-label permutation rule. |
| Timing and accounting | Seven-block `timed_blocks`, all frozen cost terms, query stream, candidate-rejection retention, and full-cost helpers. |
| Future run artifacts | Lock-gated `execute_frozen_run` writes all nine required files and retains cancellation, memory, invalid-measurement, implementation/infrastructure classifications. |

The math definitions, assumptions, exceptional cases, and review joints are in
[`mathematical-implementation.md`](mathematical-implementation.md).

## Future launch gate

No `--launch` switch is exposed. A future control-plane runner must call
`execute_frozen_run` only after supplying all of these inputs:

1. An allocated, collision-checked run identifier and new artifact directory.
2. A lock whose source, driver, plan, runtime, and resource fields equal actual
   SHA-256/runtime values computed by `verify_launch_lock`.
3. A separately supplied Coordinator authorization whose bytes are hash-bound
   into the lock and which hash-binds that exact lock.
4. An external, trusted Coordinator authenticator executable. Its zero exit
   status is the only authorization acceptance path; JSON `approved` booleans,
   nonempty signature text, and trust roots supplied by this implementation are
   intentionally insufficient.
5. Coordinator snapshot and an independent implementation/mathematical review
   with owned joints before any fixture or timing operation.

The runner enforces the frozen 7200-second / 2 CPU-hour / 8 GiB / one-run /
one-worker binding as data in the authenticated lock. Its internal RSS guard
classifies excess memory as `resource_exhaustion`; it is never a scientific
result. Cancellation preserves all files already written and classifies the
run `incomplete_cancelled`.

## Software checks in this task

The only intended bounded test invocation is:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tests.py
```

It contains ten fixed synthetic/mock cases: stream and artifact-interface
checks, a fixed `F_7` map/dual algebra object, a fixed `F_5` automorphism
object, scalar agreement, and absent-lock refusal. It performs no frozen-prime
candidate discovery, production fixture construction, control panel, timing,
or measurement. Check results and durations are recorded accurately in the
implementation report after this package is finalized.
