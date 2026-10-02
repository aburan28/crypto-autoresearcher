# Stage 0 methodological note — EXP-BINSTD-f124db

## Role (HOLD-H)

This packet is a **structural companion** to IDEA-20260922-d11575: it certifies
why the k-prime divisor lattice is minimal (`tau(N)=2*tau(16)=10`) and why the
conjugate-period formula generalises beyond the two special-case families.
It is **not** a competing attack lane and does **not** claim a break.

## What Stage 0 does

- Recomputes `n(c)=d/gcd(c,d)` for each of five curves × ten divisors and
  compares to d11575's inherited stated periods (`16/c` for `c|16`,
  `16/(c/k)` for `c=jk`) in a **separate inherited column**.
- Recomputes the frozen tau table: `tau(16)=5`, `tau(16k)=10` for prime `k`,
  and counterfactuals `tau(144)=15`, `tau(240)=20`, `tau(336)=20`.

## ECC2K-130 / d=1 null

At `d=1` the period formula and extra-divisor argument are **vacuous**
(ECC2K-130-shaped control). Stage 1 records that null; Stage 0 does not
run GHS on deployed curves.

## certificate.kind vocabulary

Run manifests for this experiment use `certificate.kind: none` only.
Period/tau/genus/orbit observations are **not** discrete-log solves.
Do not invent non-vocabulary kinds (e.g. `frobenius_order`) on manifests.
Stage YAML may carry `observation_kind` labels outside that field.

## Amazon Bedrock

Prohibited. Not used.
