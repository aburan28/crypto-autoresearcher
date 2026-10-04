# TASK-20260906-2f2a56 implementation package

This is a **non-measuring, dry-run-only** implementation/reuse package for the
approved composite protocol `EXP-ECDLP-1b1b99` +
`DEC-20260906-f73475`.  It starts no curve search, fixture preparation,
pairing/map evaluation, timing block, candidate sweep, or run record.

## Exact bindings

* Frozen specification: `experiments/EXP-ECDLP-1b1b99/specification.yaml`, SHA-256
  `b331940a2f5215058d84845f953365c39dac78b4a0d4894604e90b06bc2f3fff`.
* Additive approval and decision: `DEC-20260906-f73475`.
* This handoff: `TASK-20260906-2f2a56`; snapshot owner: `TASK-20260906-ebfb30`.

## What is implemented

`driver.py` provides deterministic, standard-library helpers for the frozen
SHA-256 rejection streams and Fisher-Yates shuffle; explicit unique-sign
selection for `lambda`; an abstract map composition in the exact order
`phi(i(psi(R)))`; cost-ledger formulas retaining every prescribed charge; and
the scalar-arm selection restriction to seed `606101`, `q=256`.

The map composition is intentionally named **charged transport**: using dual
composition, it produces `[3 lambda]R`, with `m = 3*lambda mod r`.  It contains
no division by three and does not label the output `[lambda]R`.

The coverage declaration names all five controls: composition, coordinate,
level (all four paired conductor-3 floors), identity-transport/sign, and label
permutation.  A future runner must bind their actual certificates and results.

## Reuse assessment

The nearest local code is `experiments/EXP-ECTD-001/driver/`:

| File | SHA-256 | Reuse result |
| --- | --- | --- |
| `isogeny.py` | `ecefcb79835ca0447d717a5a4940544086c09c48746e440789d1ee086c24bf69` | Partial: contains rational-kernel/Velu codomain helpers, but explicitly restricts rational kernels and does not construct normalized maps, exact duals, or the conductor-3 four-floor certificate. |
| `curve.py` | `ec5e9565288667958ee2fb414f430facb1bad6b9449cfea4cc0f8977acdeb4ca` | Partial: affine group operations can support a future toy backend, but no `j=1728` automorphism, map normalization, or required accounting. |
| `fp.py` | `c5caa486d133d3a1a786734d78b00ee4f8e2fd095c663e64bc2f213eef99fe39` | Partial finite-field helper only. |
| `run_common.py` | `1680bf344f1c4a8777265073ee10d7c239672fa039224ea8a2213ed1aec9aa98` | Not reused: it has another experiment's run-manifest/budget assumptions. |

No exact reusable implementation was found for every frozen obligation.  In
particular, a certified conductor-3 level rule, all four normalized Vélu maps
with exact duals, and their coordinate-conjugation controls are absent.  This
package therefore preserves a bounded adapter and reports that missing backend
as an implementation/reuse gap; it does not substitute an incomplete map. No
environment, dependency, host, scheduler, storage, or other infrastructure failure
was observed.

## Bounded checks

Run the 16 synthetic contract checks (no scientific fixture is loaded):

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tests.py
```

Inspect the default dry-run coverage:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 driver.py --dry-run
```

`driver.py --launch-lock PATH` only parses a future control-plane lock with
bindings for this frozen source, code/plan hashes, runtime, resource limits,
and signature.  It still raises `LaunchRefused`, because this task does not
bundle the certified backend and may not launch an experiment.

For a future locked runner, `canonical_artifact_layout` returns (but never
creates) the required run paths and `check_cancellation` exposes the stage
boundary at which a runner must persist completed artifacts and stop.

## Remaining launch prerequisites

1. Complete and certify the missing mathematical backend: the conductor-3 level
   rule, all four normalized Vélu maps with exact duals, the `j=1728`
   automorphism, and coordinate-conjugation controls. An implementation review
   or a launch lock cannot make the current adapter runnable without this work.
2. Coordinator snapshot of these five paths and receipt verification.
3. Independent implementation review against frozen controls, RNG, cost terms,
   map/dual normalization, all floor certificates, and scalar branches.
4. A genuine future runtime/code/execution-plan lock that binds actual hashes
   and the frozen 7200 s / 2 CPU-hour / 8 GiB / one-run / one-worker limits.
5. A separately allocated, collision-checked run handoff and artifact path.
