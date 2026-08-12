# Experiment Contract: Nonlinear S4 Quotient Preflight V1

## Handoff

```yaml
handoff:
  id: TASK-20260801-NS4-001
  from: coordinator
  to: executor
  objective: test whether exact source-tagged D2/D3 elliptic states have family-specific low-degree coordinate quotient spaces
  inputs:
    - development/TYPED-FIVE-EC-V1/raw-result.json
  constraints:
    - generated ordinary prime-field curves only
    - preserve exact nondecreasing source witnesses
    - compare every family with same-curve random_x control
    - no scalar labels in candidate state construction
    - no promotion from a rank signal alone
  deliverables:
    - raw machine-readable result
    - independent replay verifier
    - resource receipts and hashes
    - scoped analysis and ledger update
  budget:
    wall_clock_seconds: 120
    memory_gb: 2
    maximum_runs: 1
  completion_gate:
    - exact state and witness replay
    - degree-rank curves for D2 and D3
    - matched random-x comparisons
    - mutation rejection
    - explicit no-breakthrough boundary
```

## Hypothesis

The exact source-tagged `D2` and `D3` states generated from a coordinate
factor base may lie in a family-specific low-degree coordinate quotient. If a
candidate retains at least 80% of same-curve random support while its `D3`
feature rank is at most 80% of the random control at a tested degree, this is
a signal for a nonlinear recursive `S4` compiler.

The feature census is only a preflight. It does not construct a target
selector, solve a join, or imply an ECDLP improvement.

## Null Hypotheses

1. Candidate D2/D3 states have the same degree-rank curve as same-curve
   random-x states after support is accounted for.
2. Any rank reduction is caused by fewer distinct states or the algebraic
   coordinate ring itself, not by a family-specific recursive quotient.
3. A low-degree feature space does not preserve exact source witnesses or
   provide a target-conditioned complement lookup.

## Parameters

- immutable input: `TYPED-FIVE-EC-V1/raw-result.json`;
- three generated ordinary prime-order curves with `q=953,3919,15583`;
- candidate families: random-x, source-PRF-x, x-interval, rational-union;
- same-curve control: random-x factor base;
- exact nondecreasing source tuples at levels `D2` and `D3`;
- first witness: lexicographically first source tuple for each exact state;
- feature basis: affine monomials `x^i y^j` with `i+j<=d`, plus an infinity
  indicator, for `d=0..8`;
- rank: exact row rank over `F_p`;
- no scalar labels or subgroup discrete-log advice are used.

## Metrics

- attempted tuples and unique state support at D2/D3;
- identity presence;
- source-state and witness digests;
- feature basis width and exact rank at every degree;
- candidate/control support and rank ratios;
- point additions, inversions, multiplications, wall time, and peak RSS.

## Controls

- same-curve random-x control for every candidate family;
- exact witness replay from source indices;
- constant feature rank and infinity separation;
- independent affine addition, state construction, rank, and comparison code;
- five deterministic mutations rejected by the verifier.

## Signal Gate

This preflight reports a diagnostic signal only when a D3 candidate row has
support ratio at least `0.8` and rank ratio at most `0.8` against random-x at
the same degree. A signal must be replicated across at least two curves and
must survive a future target-conditioned selector test.

No algorithm promotion gate exists in this experiment. A successor would
need an exact target-conditioned join, complete witness lift, charged advice
and online costs, quotient relation rank, target descent, and a strict
sub-rho comparison.

## Falsification

- state or witness mismatch;
- replay or mutation failure;
- no cross-curve D3 rank signal;
- candidate rank reduction explained by support loss;
- feature rank saturating with degree before a useful exact selector exists.

Failure is scoped to this low-degree coordinate-state quotient. It does not
rule out other nonlinear composition towers, divisor/resultant circuits, or
target-batched operators.

## Reproduction

```bash
python3 src/nonlinear_s4_quotient_preflight.py \
  development/TYPED-FIVE-EC-V1/raw-result.json \
  --families random_x source_prf_x x_interval rational_union \
  --max-degree 8

python3 src/verify_nonlinear_s4_quotient_preflight.py \
  /path/to/raw-result.json
```
