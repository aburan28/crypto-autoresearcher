# Experiment Contract: P1043 p231 y-residue relation rank audit

## Hypothesis
HYPOTHESIS / TOY-EVIDENCE: The y-residue-filtered true witnesses from P1038, P1041, and P1042 form more than isolated scalar predictions; they contribute a shared factor-base relation rowspace suitable for later linear algebra.

## Null hypothesis
The witnesses derive local scalars but do not share a globally consistent factor-value assignment, or they add only a low-dimensional repeated factor direction. This would narrow the y-residue route to a scalar-stability signal, not a full index-calculus relation stream.

## Parameters
- field/curve family: toy p231 ECDLP harness, target `22050.cf1@11731`
- input artifacts:
  - `low_term_total2_p1038_p231_guarded_structural_family_supply_search_probe.json`
  - `low_term_total2_p1041_p231_yresidue_strict_route_validation_probe.json`
  - `low_term_total2_p1042_p231_yresidue_second_holdout_validation_probe.json`
- included witnesses: primary `p1029_leaf8_scout_forward_compressed`, strict family `[8,8,11,11]` / tail `[9,12]`, toy-secret-verified true predictions only
- coefficient model: local target variable per public/window witness group, shared factor columns by factor index
- modulus/order: `11779`

## Metrics
- unique witness groups;
- unique forms;
- unique public fingerprints;
- factor-column support;
- factor-signature diversity;
- coefficient rank;
- augmented rank;
- shared-factor residual diversity;
- whether a global shared-factor assignment is consistent.

## Positive control
Each included witness must individually derive its local scalar by exact factor-vector elimination.

## Negative control
The audit must not merge source-secret labels into rule predicates or count repeated object models as independent witness groups.

## Success criterion
Success requires global shared-factor consistency and nontrivial factor-column/rank diversity beyond a single repeated factor direction.

## Falsification criterion
If residual factor equations disagree across witness groups, or if all witnesses use the same factor signature with factor rank `1`, the y-residue stream is not yet a usable shared factor-base relation stream.

## Reproduction command
```bash
PYTHONPATH=tasks/ecdlp_index_calculus \
  python3 tasks/ecdlp_index_calculus/low_term_total2_p1043_p231_yresidue_relation_rank_audit.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1043_p231_yresidue_relation_rank_audit.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1043_p231_yresidue_relation_rank_audit_probe.json
```

## Results
Run timestamp: `2026-06-30T04:15:49Z`.

Artifact: `ecdlp_index_calculus_state/low_term_total2_p1043_p231_yresidue_relation_rank_audit_probe.json`.

Claim status: `NEGATIVE_RESULT_P1043_SINGLE_FACTOR_DIRECTION_ONLY`.

Rank and consistency summary:

| Metric | Value |
|---|---:|
| unique witness groups | 5 |
| unique forms | 10 |
| unique public fingerprints | 5 |
| local target variables | 5 |
| factor columns | 2 (`8`, `11`) |
| coefficient rank | 6 |
| augmented rank | 6 |
| factor rank | 1 |
| unique factor signatures | 1 |
| unique shared residuals | 1 (`5459`) |
| globally consistent | true |

Included witness groups:

| Source | Window | Public fingerprint | Derived scalar | Residuals |
|---|---|---|---:|---|
| P1038 | `12520_12527` | `[5063,6547]` | 11550 | `5459,5459` |
| P1038 | `12552_12559` | `[4643,5694]` | 440 | `5459,5459` |
| P1041 | `12776_12783` | `[1837,238]` | 8189 | `5459,5459` |
| P1042 | `12968_12975` | `[9166,10292]` | 1936 | `5459,5459` |
| P1042 | `13008_13015` | `[10378,8246]` | 11669 | `5459,5459` |

All groups use the same factor signature `[(8,11777),(11,11777)]`, i.e. one repeated factor direction over columns `8` and `11`.

## Interpretation
MIXED RESULT / TOY-EVIDENCE: the y-residue stream is better than isolated scalar predictions because the five true witness groups are globally consistent under a shared factor residual `5459`. However, it is not yet a useful shared factor-base relation stream because the factor rank is only `1` and every witness uses the same factor signature.

Next concrete action: create P1044 as a y-residue adjacent-family rank-diversity scout. Keep the public y-residue filter and scalar-stability checks, but search nearby repeated two-tail families for additional globally consistent residual classes with factor signatures independent of `[(8,-2),(11,-2)]`.

## Interpretation boundary
This is a rank/consistency audit over toy p231 relation-generation artifacts. It does not prove or disprove index calculus over prime fields; it only tests whether this y-residue filtered stream has the linear-algebra structure needed for the next stage.
