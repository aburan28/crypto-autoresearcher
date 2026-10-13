# Exploratory Koblitz rho calibration ladder

Frozen: 2026-10-13, before the 512-target run.

Status: **exploratory pilot only**. This is not ledger evidence, a sealed
measured bound, an isogeny-transfer experiment, a cryptographic-size ECDLP
solve, or evidence that a named curve is weak.

## Question

On word-sized Koblitz proxy groups, does the collision-walk transition ratio
between otherwise matched negation and signed-Frobenius rho arms track the
random-map prediction `sqrt(m)` after fixed setup work is separated?

The pilot also measures an unquotiented plain-rho control. It does not price
Frobenius/orbit canonicalisation, construct an isogeny, test a conductor
endpoint, or execute sect113r1 or a NIST K/B/P curve.

## Frozen grid and eligibility

The cells are `(a,m) = (0,23), (1,23), (0,31), (0,37), (0,41),
(1,43), (1,47)`. They were selected before outcomes were observed from this
run. Every `m` is prime, every curve is registered in the producer, and the
largest selected prime subgroup has at least 20 bits. The `(0,31)` cell is
retained as a high-cofactor stress point, and the two `m=23` cells separate
the Koblitz signs at one degree.

Each cell has 512 independently derived planted targets and one measured
round. Each target is run once under each arm with the same algorithm seed:

- `rho-frob`: `rho.signed_frobenius`, the reference arm;
- `rho-neg`: `rho.negation`, the baseline arm;
- `rho-plain`: `rho.plain`, an unquotiented control.

The exact machine-readable design is [`spec.json`](spec.json). Its fixed
target seed is `2026101301`, algorithm seed is `2026101302`, arm order is a
seeded shuffle, per-execution timeout is 900 seconds, and there are no
unmeasured warm-up rounds. The producer source is
`aburan28/crypto@0dc6b7f4a03253e7c7641f99700f7f423f8d07e0`; its worktree was clean.
The locally built release binary SHA-256 is
`f2164ce16c6ae17c408777dc2448e8f226a42ca8c4d3da1d00aeff7419ec1f88`.

## Estimands and inference

For each cell, pair records by workload ID and round and require identical
algorithm seeds and verified planted-key recovery across all three arms.
Cells are never pooled as independent replicates.

The primary observable is `counters.walk_operations`, which equals steps plus
look-ahead additions plus cycle-escape doublings and excludes setup, walk
starts, and verification. Define the primary rho-bit saving as

`beta_walk = log2(mean(W_neg) / mean(W_frob))`.

Compare it descriptively with `0.5 log2(m)` and report their difference.
The secondary observables are:

- setup-inclusive counted GAE ratio and its log2 value;
- `rho-plain` versus `rho-neg` walk ratio as a quotient control;
- setup, starts, verification, unpriced canonicalisations, failures, caps,
  and cycle counters;
- solve wall time, labelled descriptive because the environment is virtual
  and no isolation claim is made.

Canonicalisations are counted but unpriced, so counted-GAE figures are lower
bounds rather than fully charged costs. No end-to-end speedup is inferred.

Use a paired target-level BCa bootstrap with 50,000 resamples and fixed seed
`2026101303` for 95% intervals on ratios and bit savings. Report raw cell
intervals; with only seven deliberately selected proxy cells, do not fit or
promote an asymptotic exponent. A residual within +/-0.15 bit is a descriptive
agreement marker only, not an acceptance test or promoted claim.

## Validity and stopping

The launch count is fixed. Do not add targets after inspecting results. Keep
every record, failure, cap, and timeout. A cell is `INDETERMINATE` if any arm
does not have all 512 planned records, any planted key fails verification,
the target/seed pairing is broken, or any solve is capped/times out. No failed
record may be deleted or replaced. The run may be interrupted only for a
process or environment failure, which must remain in the attempt log.

The archived `m=37` and `m=41` studies use different implementations and
sampling designs. They may be shown as contextual replications but are not
pooled with this run.

## Reporting boundary

This pilot can support observations about this producer, these word-sized
groups, and these counters. It cannot support a NIST-size runtime claim, an
attack-cost projection, an isogenous-endpoint advantage, or a weak-curve
verdict. Any stronger quantitative claim requires the repository's ledger
experiment route, fully priced canonicalisation and setup, independent
review, and—where transfer is claimed—certified maps and recovery.
