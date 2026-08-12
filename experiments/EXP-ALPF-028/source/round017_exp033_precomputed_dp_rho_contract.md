# Experiment Contract: round017_exp033_precomputed_dp_rho

## Hypothesis

HEURISTIC / TOY-EVIDENCE: On generated prime-order toy elliptic curves, a target-independent database of Pollard-rho distinguished endpoints can recover random target logs with online cost near `n^(1/3)` group additions, while the charged setup cost is near `n^(2/3)` additions and storage is near `n^(1/3)` points.

## Null hypothesis

The implementation fails to recover the planted scalar without reading it, or the online cost does not separate from generic `sqrt(n)` search once precomputation and memory are charged.

## Parameters

- field/curve family: generated prime-field short-Weierstrass curves `y^2 = x^3 - 3x + b` with prime group order
- sizes: subgroup orders near the requested bit sizes, default `15,18,21`
- seeds: default `20260601`
- factor base: none; this is a generic rho table, not index calculus
- relation shape: precomputed endpoint `A0 P` collides with target walk endpoint `A P + b Q`
- baseline: BSGS implementation, Pollard-rho estimates `sqrt(pi*n/2)` and `0.886*sqrt(n)` with negation

## Metrics

- group operations: precompute additions, online additions, BSGS addition estimate
- field operations: not instrumented in this generic group prototype
- memory: distinguished endpoint table size
- relation probability: target solves per online trial and table-hit counts
- rank: not applicable
- solver degree: not applicable
- wall-clock: precompute and online seconds

## Positive control

The same-curve precomputed endpoint table must recover random target logs and verify `k*P == Q`.

## Negative control

For a successful table hit, corrupt the stored endpoint scalar by `+1 mod n`; the same relation must fail verification. This checks that scalar bookkeeping and public verification reject bogus precomputed data.

## Success criterion

For all three sizes, recover all planted target logs, report average online additions, report the separate setup cost, and keep the interpretation explicitly scoped as generic non-uniform precomputation rather than an ECDLP structure break.

## Falsification criterion

Any size with repeated verification failures, no target recovery under the online-trial cap, or a bookkeeping relation that verifies after scalar corruption narrows or kills this implementation claim.

## Reproduction command

```bash
sage experiments/ecdlp_prime_field/round017_exp033_precomputed_dp_rho.sage --seed 20260601 --bits 15,18,21 --targets 12 --lanes 4 --rho-baseline-targets 6
```
