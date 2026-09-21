# Analysis — Autolab prime-field: round017_exp033_precomputed_dp_rho

## Observation
Status: OBSERVATION / TOY-EVIDENCE / HEURISTIC.

Source excerpt / raw summary:

```
# Round 017 EXP-033: Precomputed Distinguished-Point Pollard Rho

Status: OBSERVATION / TOY-EVIDENCE / HEURISTIC.

Candidate: use a target-independent distinguished-point rho table to reduce online target ECDLP cost below a fresh generic search, while charging setup and memory separately.

Scope: generated prime-order toy curves only. This is a generic non-uniform precomputation demonstration, not index calculus and not a deployment-relevant break.

## Reproduction

```bash
sage experiments/ecdlp_prime_field/round017_exp033_precomputed_dp_rho.sage --seed 20260601 --bits 21 --targets 48 --lanes 4 --rho-baseline-targets 48
```

## Results

| n_bits | n | dp_bits | table | precomp_ops | avg_online_ops | fresh_rho_avg | online_speedup | amortized_speedup | BSGS_ops | solved |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 21 | 1948729 | 7 | 128 | 48787 | 565.0 | 1883.9 | 3.33x | 1.19x | 2573 | 48/48 |

## Interpretation

- OBSERVATION: the prototype recovers target logs from public `P,Q` and verifies `k*P == Q`; the solver does not use the planted scalar except for test bookkeeping.
- HEURISTIC: the online operation scale follows the expected `n^(1/3)` shape only at toy scale and with constants from the chosen distinguished-point rate.
- MODEL-BOUND: the speedup is non-uniform. The precomputed table is specific to the group, base point, walk function, and distinguished-point predicate.
- NEGATIVE CONTROL: corrupting the stored precomputed scalar for a successful endpoint hit must fail public verification; this catches bogus relation bookkeeping.
- LIMITATION: charging setup removes the attack value for a single target. The measured setup constants are visible here; at these toy sizes they can dominate the ideal `n^(2/3)` heuristic, while storage is around `n^(1/3)` points.
- SPEEDUP ACCOUNTING: `online_speedup` excludes setup and shows why the non-uniform model looks attractive; `amortized_speedup` charges setup over the measured fresh-rho baseline targets and is the practical cost comparison.

## Handoff: precomputed DP rho prototype

### Claim or task
Implement and measure the Bernstein-Lange precomputed distinguished-point rho mechanism on controlled toy ECDLP instances.

### Status
OBSERVATION

### Assumptions
- Prime-order toy short-Weierstrass curves over prime fields.
- Fixed target-independent walk adding only precomputed multiples of `P`.
```

## Comparison
Compared against Autolab's stated baseline (typically Pollard rho / VW / Wesolowski-class
isogeny cost, depending on topic). This import does not recompute those baselines inside
crypto-autoresearcher.

## Inference
`OBSERVATION` / `TOY-EVIDENCE` (or Autolab's original label if stronger, still not upgraded):
the Autolab package is now citeable as `EXP`+`RUN` evidence under the harness. Scientific
content remains bounded by Autolab's original scope and caveats.

## Limitation
- Not independently re-executed in this repository.
- Certificates were not re-verified; do not promote discrete-log / decomposition claims.
- Claim tier remains `toy` unless a later harness experiment re-runs with certificates.
