# Experiment Contract: EXP-ECDLP-RECURSIVE-002 v3 execution / v2 arithmetic

## Hypothesis

`HYPOTHESIS`: A frozen coordinate family is extreme against independently
seeded point-set null samples in exact eight-term coverage, coverage efficiency,
and exact uniform-order fixed-curve lookup efficiency on clean curves.

## Null hypothesis

The EXP-ECDLP-RECURSIVE-001 signal lies inside random-set variation or
disappears when anomalous curves, repeated fields, incomplete coordinate costs,
and support-map ordering are controlled.

## Parameters

- field/curve family: seeded `p mod 4 = 3` prime fields; prime-order
  short-Weierstrass curves with trace not in `{0,1}` and
  `j not in {0,1728}`
- sizes: 12, 14, and 16 field bits, with three distinct field primes at every
  size and monotone `q` for each seed
- seeds: 2473001, 2473004, and 2473012
- relation shape: sign-complete `m=8`, split `4+4`
- factor-base size: smallest even `B` with `binomial(B+7,8)/q >= 0.5`
- null samples: 31 random-scalar and 31 random-x bases per curve; these sample
  the same sign-complete point-set distribution, while random-x also matches
  coordinate-construction cost
- candidates: x interval, square map, rational union
- targets: 128 shared seeded targets
- order seeds: 811, 821, 823, and 827
- rho trials: two per curve, used as arithmetic scale only

## Metrics

- exact support: `|4A|`, `|8A|`, signed-generic maximum, finite-null raw
  ranks/ties, and empirical percentiles
- expansion efficiency: `|8A|/|4A|^2`
- online work: exact per-target successful-partial count and uniform-permutation
  first-hit expectation `(S+1)/(k+1)`, plus four retained shuffled scans
- order control: sampled aggregate error against the exact expectation at most
  25 percent and aggregate shuffle variation at most 25 percent
- memory: reconstructible functional-artifact deep bytes, entries, measured
  lookup counts, a labeled 64-byte traffic assumption, and child peak RSS
- construction: group operations plus charged binary-pow, coordinate-RHS, and
  map multiplication/inversion proxies; each charged cost is separate
- runner boundary: single child-process wall/CPU/peak RSS; post-child parsing
  and core-artifact hashing are reported separately
- excluded runner overhead: process-monitor helper cost, receipt/manifest
  serialization, and final publication are not charged as attack work
- rho: arithmetic scale only
- rank, solver degree, linear algebra, and descent: not measured and not
  claimable

## Positive control

Scalar progression must compress `|4A|` and lose `|8A|` against the random
median. Failure makes the document invalid and blocks every family promotion.

## Negative controls

Independent random-scalar and construction-matched random-x samples at
identical `B`, curve, sign mode, targets, and order seeds.

## Success criterion

Require both-sample `>=0.95` support and coverage-efficiency percentiles,
both-sample `>=0.90` exact uniform-order frontier percentiles, both order
controls, and at most `4x` the random-x median in each of group operations,
charged field multiplications, and charged field inversions. All mandatory
curve, field-distinctness, seed-uniqueness, positive-control, order, rho,
resource, command, lock, receipt, and verifier-linkage controls must pass. A
family must pass six of nine curves while spanning every size and seed.

This is an exploratory finite-null screen across three selected families. It
does not claim a family-wise error rate or stable performance on all curves.

## Falsification criterion

Narrow the frozen family hypothesis if no candidate meets the full gate. A
failure means only that no tested family met this finite schedule; it does not
identify random variation as the cause or close other coordinate families or
recursive circuits.

## Execution boundary

The v1 and v2 independent pre-run audits both returned `REVISE`. Version 3 is
`review_required` with `approved_by: null`. Canonical execution is prohibited
until all of the following occur:

1. a third independent audit returns `GO` on the review commit;
2. an approval-only commit changes only status and approver fields;
3. an external `execution-approval.json` binds that approved commit, exact
   specification and plan digests, protocol hashes, Python runtime, non-root
   effective UID, and no-descendant policy;
4. a final independent check publishes the external lock path and SHA-256; and
5. run `003` is launched with those exact published values.

Locked child argv uses the absolute approved interpreter with `-I -S -B`.
`RLIMIT_NPROC=0` forbids child creation under the lock-bound non-root UID. The
process sampler remains defense in depth, not a kernel sandbox claim. Wrapper
postprocessing is reported only through core-artifact hashing. Process-monitor
helpers and receipt/manifest publication remain outside the measured attack
payload and must not be described as included resource cost.

The final lock audit must instantiate `APPROVAL_LOCK` and `APPROVAL_SHA256` in
the command templates below. Until then these are not executable canonical
commands.

```bash
PYTHONPATH=src /Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13 -P -S -B -m crypto_autoresearcher.cli run \
  --experiment-dir experiments/EXP-ECDLP-RECURSIVE-002 \
  --run-id RUN-ECDLP-RECURSIVE-003 \
  --seed 2473001 \
  --parameter phase=generator \
  --parameter protocol=EXP-ECDLP-RECURSIVE-002-v2 \
  --timeout 900 \
  --approval-lock "$APPROVAL_LOCK" \
  --approval-lock-sha256 "$APPROVAL_SHA256" \
  -- /Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13 -I -S -B \
  experiments/EXP-ECDLP-RECURSIVE-002/src/null_calibrated_coverage.py \
  --bit-sizes 12 14 16 \
  --seeds 2473001 2473004 2473012 \
  --null-replicates 31 \
  --targets 128 \
  --order-seeds 811 821 823 827 \
  --occupancy-lambda 0.5 \
  --rho-trials 2
```

Commit the immutable generator directory without any other path change. The
verifier launch commit may differ from the approved base commit by exactly
those committed generator files. Then use:

```bash
PYTHONPATH=src /Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13 -P -S -B -m crypto_autoresearcher.cli run \
  --experiment-dir experiments/EXP-ECDLP-RECURSIVE-002 \
  --run-id RUN-ECDLP-RECURSIVE-004 \
  --seed 2473001 \
  --parameter phase=verifier \
  --parameter protocol=EXP-ECDLP-RECURSIVE-002-v2 \
  --timeout 900 \
  --approval-lock "$APPROVAL_LOCK" \
  --approval-lock-sha256 "$APPROVAL_SHA256" \
  -- /Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13 -I -S -B \
  experiments/EXP-ECDLP-RECURSIVE-002/src/verify_null_calibrated_coverage.py \
  --input experiments/EXP-ECDLP-RECURSIVE-002/runs/RUN-ECDLP-RECURSIVE-003/raw-result.json
```

Reduced non-evidence checks remain:

```bash
/Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13 -I -S -B experiments/EXP-ECDLP-RECURSIVE-002/src/verify_null_calibrated_coverage.py --self-test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## Claim boundary

`HYPOTHESIS`, `TOY-EVIDENCE`, `HEURISTIC`, and `MODEL-BOUND`. A pass authorizes
a larger clean-curve additive-geometry experiment only, not index calculus,
rank, descent, an exponent improvement, a faster-than-rho algorithm, or a
deployment claim.
