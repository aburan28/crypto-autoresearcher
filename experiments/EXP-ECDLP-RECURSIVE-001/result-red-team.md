# EXP-ECDLP-RECURSIVE-001 red-team result

**Verdict: REVISE_INTERPRETATION**

The frozen runs are valid arithmetic/verifier artifacts, but their promotion must be interpreted as a toy preflight signal only. Do not promote the frozen result as evidence of a generic ECDLP advantage. Preserve the positive arithmetic signal and keep the wider family OPEN.

## Scope and immutable evidence

Audited worktree: `/Volumes/Volume/crypto-autoresearcher-worktrees/coordinate-energy`

- HEAD: `fd7243701dd86bc194a379f0eb7a1016c7d4daef`
- Run 001 raw result SHA-256: `cf9e8fc8fa26bb5ea40e289bae435f0147ecc6e87da17482772528c8496d2890`
- Run 002 raw result SHA-256: `a99acde52f07d52600fa89a93250b4e253eca70bcdbe5c25c165c4153b3f81b0`
- Run 001 manifest SHA-256: `81ef7a0c5f119aca24bd563d1563b7e6cba2946216cff7bf993e50044a2a5179`
- Run 002 manifest SHA-256: `125c9e51b3eae486cda0e7b4c89ad349fd619db89950f20f247c0ba794361870`

Commands used:

```bash
git -C /Volumes/Volume/crypto-autoresearcher-worktrees/coordinate-energy rev-parse HEAD
sha256sum experiments/EXP-ECDLP-RECURSIVE-001/runs/RUN-ECDLP-RECURSIVE-00{1,2}/{manifest.json,raw-result.json}
jq '.[...]' .../raw-result.json
```

The independent verifier reports `valid=true`, `configurations_verified=216`, six instances, recomputed curve orders, replayed generators/targets, factor-base sources, supports, split advice, first witnesses, operation counters, and rho trials. This verifies the frozen arithmetic and wrapper/verifier agreement; it does not verify an attack or deployment result.

## Severity-ordered findings

### S0 — promotion boundary is not clean

The candidate checklist explicitly says anomalous curves invalidate a run, but the generator/verifier reject only `trace == 0`. Seed `1473002`, bits 12 has `p=q=3931` and `trace=1`, hence is anomalous. Any cross-instance promotion that includes this instance has an invalidated control under the repository’s own checklist. Repair: reject `trace in {0,1}` and special `j` values before generation and independently in verification.

### S1 — the apparent compression is not `|4A|` compression

For every frozen promoted candidate, `|4A|` is the generic signed maximum: `B=8 -> 225`, `B=10 -> 501`, `B=12 -> 985`. Advice-byte ratios are approximately `0.995..1.014`. Thus the signal is not a factor-base or four-fold-support compression. It arises through `|8A|`/coverage and the sampled first-witness `T`; the interpretation must say “recursive coverage/first-witness arithmetic signal,” not “split compression.”

### S1 — null comparison is underpowered and heterogeneous

The six random_x/random-scalar frontier ratios are `[0.5705, 0.6583, 0.8856, 0.9652, 1.3564, 1.4155]`. This is a large single-null spread. No family hits three instances while staying `<= 0.8` against both random controls. Therefore the frozen gate does not establish a stable family effect; it establishes at most a noisy, instance-dependent signal.

### S2 — first-witness and scan order can bias the observed pass

The successful pass uses sampled first-witness `T`, and support scans are order-sensitive unless shuffled/order-independent controls are used. A first witness is a valid arithmetic witness, but its sampled cost is not a robust estimator of target descent or amortized online cost. Re-measure with randomized support order and exact full-distribution statistics.

### S2 — resource accounting is incomplete

The frozen run reports rho only as a scale reference. It does not measure rank, sparse linear algebra, individual-log/target descent, exponent trend, or a deployed-size result. Advice bytes must be joined by actual bytes/bandwidth and construction cost. No claim beyond preflight arithmetic is licensed.

## Exact narrow claim

**OBSERVATION / TOY-EVIDENCE / MODEL-BOUND:** On the six frozen small ordinary-looking test instances as recorded (including one anomalous instance that violates the checklist), the verifier reproduces a valid recursive-support arithmetic signal for three `sign_complete, m=8` families. The signal is compatible with larger `|8A|`/coverage and sampled first-witness behavior, while `|4A|` remains at the generic signed maximum and advice bytes remain near matched random. This is not evidence of split compression, a rank advantage, a target-descent method, an exponent improvement, or a deployed prime-field ECDLP result.

## Required repaired successor

Create a versioned successor; do not mutate `harness/` or either frozen `runs/` directory.

1. Reject `trace == 0` **or** `trace == 1`, and reject special `j` values, in both generator and independent verifier. Require all curves to be non-special and prime-order under the explicit contract.
2. Use many independent random-scalar and random-x null replicates per curve and across more curves; report paired distributions, confidence intervals, and the number of families meeting the gate on every instance.
3. Shuffle support order and provide an order-independent scan/control; report first-witness `T` percentiles, not only sampled first witnesses.
4. Report exact `|4A|` and `|8A|` percentiles, coverage percentiles, and per-target success distributions, retaining the full unsuccessful-target sample.
5. Charge actual advice bytes, construction bytes, lookup bytes, and memory bandwidth; retain group/field operation counters.
6. Repeat on the same non-special curve family with wider bit sizes and seeds. Keep `m`, `B`, sign mode, target count, and baseline selection preregistered.
7. Leave rank, linear algebra, individual logarithm/target descent, and asymptotic exponent analysis as later mandatory gates. A successor pass cannot promote without those gates.

## Required controls and falsification tests

- Clean counterexample: remove seed1473002 and rerun paired nulls; if the family effect disappears or fails the per-instance gate, the frozen signal is narrowed to instance noise.
- Order counterexample: permute supports and compare first-witness `T`; a large change falsifies order-robust online-cost interpretation.
- Representation counterexample: compare exact `|4A|`/`|8A|` quantiles at matched `B` against random controls; unchanged `|4A|` confirms no split compression.
- Resource counterexample: include actual bytes/bandwidth and all offline construction work; if the advantage vanishes, it was an advice-accounting artifact.
- Family control: require a predeclared minimum number of clean curves and independent replicates, not “three instances” selected from the six frozen cases.

## AGENTS handoff

## Handoff: repaired recursive coverage successor

### Claim or task
Test whether the observed clean-instance recursive `|8A|`/coverage and first-witness signal survives non-special curves, replicated nulls, randomized scans, and complete resource accounting.

### Status
HYPOTHESIS

### Assumptions
- Prime-order, non-anomalous, non-special curves only.
- Matched random-scalar and random-x controls are valid nulls.
- Exact support and resource accounting are the promotion metrics; rho is scale only.
- Rank, linear algebra, and target descent remain unresolved later gates.

### Evidence so far
- Independent verifier valid for 216 configurations across six instances.
- Promoted labels: rational_union (4), square_map (3), x_interval (3), all `sign_complete, m=8`.
- `|4A|` is generic maximum and advice-byte ratios are near one.
- Frontier ratios show a large six-instance spread and no family passes the stated three-instance/two-null gate.
- One frozen instance is anomalous (`p=q=3931`, trace 1) under the checklist.

### Failure modes
- Exceptional-curve contamination; single-null sampling; support-order bias; first-witness selection bias; hidden byte/bandwidth cost; later rank/LA/descent failure.

### Next concrete action
Implement and run a successor contract with `trace not in {0,1}`, special-`j` rejection, many paired null replicates, shuffled scans, exact `|4A|`/`|8A|` percentiles, and byte/bandwidth instrumentation.

### Artifact paths
- `/Volumes/Volume/autolab/research/crypto_autoresearcher_exp_ecdlp_recursive_001_result_redteam_20260717.md`
- `experiments/EXP-ECDLP-RECURSIVE-001/candidate-checklist.md`
- `experiments/EXP-ECDLP-RECURSIVE-001/runs/RUN-ECDLP-RECURSIVE-001/raw-result.json`
- `experiments/EXP-ECDLP-RECURSIVE-001/runs/RUN-ECDLP-RECURSIVE-002/raw-result.json`
