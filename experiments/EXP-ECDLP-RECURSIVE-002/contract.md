# Experiment Contract: EXP-ECDLP-RECURSIVE-002

## Hypothesis

`HYPOTHESIS`: A frozen coordinate family is extreme against both replicated null distributions in exact eight-term coverage, coverage efficiency, and order-robust fixed-curve lookup efficiency on clean curves.

## Null hypothesis

The EXP-ECDLP-RECURSIVE-001 signal lies inside random-set variation or disappears when anomalous curves and support-map ordering are removed.

## Parameters

- field/curve family: seeded `p mod 4 = 3` prime fields; prime-order short-Weierstrass curves with trace not in `{0,1}` and `j not in {0,1728}`
- sizes: 12, 14, and 16 field bits, with monotone `q` for each of three seeds
- relation shape: sign-complete `m=8`, split `4+4`
- factor-base size: smallest even `B` with `binomial(B+7,8)/q >= 0.5`
- nulls: 31 random-scalar and 31 random-x bases per curve
- candidates: x interval, square map, rational union
- targets: 128 shared seeded targets
- order seeds: 811, 821, 823, and 827
- rho trials: two per curve, used as arithmetic scale only

## Metrics

- exact support: `|4A|`, `|8A|`, signed-generic maximum, and both-null empirical percentiles
- expansion efficiency: `|8A|/|4A|^2`
- online work: group operations and lookups over every target under each support-order seed
- memory: functional witness-map deep bytes, entries, estimated lookup traffic, and wrapper peak RSS
- construction: factor-base and split-compiler group/field operations kept separate
- rho: arithmetic scale only
- rank, solver degree, linear algebra, and descent: not measured and not claimable

## Positive control

Scalar progression should compress `|4A|` while losing `|8A|` and coverage efficiency.

## Negative controls

Independent random-scalar and construction-matched random-x distributions at identical `B`, curve, sign mode, targets, and order seeds.

## Success criterion

Require both-null `>=0.95` support and coverage-efficiency percentiles, both-null `>=0.90` order-robust frontier percentiles, at most 25 percent order variation, at most `4x` median random-x offline work, and six of nine clean instances spanning all sizes and seeds.

## Falsification criterion

Narrow the family hypothesis if no candidate meets the full gate. A null result distinguishes random variation from the frozen coverage signal; it does not close other coordinate families or recursive circuits.

## Reproduction command

Pre-run verifier and integration checks:

```bash
python3 -B experiments/EXP-ECDLP-RECURSIVE-002/src/verify_null_calibrated_coverage.py --self-test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_null_calibrated_coverage.py' -v
```

The specification remains `review_required` with `approved_by: null`; no
canonical run is authorized. The exact harness command and immutable run ID
will be recorded only after an independent pre-run `GO` and approval commit.

## Claim boundary

`HYPOTHESIS`, `TOY-EVIDENCE`, `HEURISTIC`, and `MODEL-BOUND`. A pass authorizes a larger clean-curve additive-geometry experiment only, not an index-calculus attack or faster-than-rho claim.
