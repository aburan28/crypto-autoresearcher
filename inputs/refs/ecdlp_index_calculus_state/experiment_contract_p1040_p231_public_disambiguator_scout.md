# Experiment Contract: P1040 p231 public disambiguator scout

## Hypothesis
HYPOTHESIS / TOY-EVIDENCE: The P1038 true strict-route witnesses and the P1039 false strict-route witness differ by public/local metadata that can be used to propose a narrower scalar-stable selector before the next holdout.

## Null hypothesis
No tested public/local feature separates the P1038 true primary forward compressed witnesses from the P1039 false primary forward compressed witness without also selecting diagnostic false witnesses. This would mean the next route needs a different representation or a new public invariant, not only a local guard refinement.

## Parameters
- field/curve family: toy p231 ECDLP harness, target `22050.cf1@11731`
- positive primary source: P1038 `p1029_leaf8_scout_forward_compressed`
- negative primary source: P1039 `p1029_leaf8_scout_forward_compressed`
- diagnostic false sources: widened forward compressed pools from P1038 and P1039
- strict family: terms `[8,8,11,11]`, tail support `[9,12]`
- public features: row-key/salt provenance, salt gap, q/rhs deltas, public-coordinate residues, tail coefficient signs, raw-support agreement, and object-model multiplicity
- forbidden selector input: toy secret, verification label, or source secret

## Metrics
- distinct primary true witness count;
- distinct primary false witness count;
- diagnostic false witness count;
- candidate rule true coverage;
- primary false rejection;
- diagnostic false rejection;
- scout-control coverage;
- feature values for true versus false witnesses.

## Positive control
The extractor must recover the two P1038 primary true witnesses:
- `[5063,6547]@12520_12527`, q `[7344,9170]`, predicted/source secret `11550`;
- `[4643,5694]@12552_12559`, q `[646,4641]`, predicted/source secret `440`.

## Negative control
The extractor must recover the P1039 primary false witness:
- `[9665,1060]@12704_12711`, q `[8099,10611]`, predicted `3712`, source secret `7344`.

## Success criterion
Scout success requires at least one public rule that selects all P1038 primary true witnesses and rejects the P1039 primary false witness. A stronger candidate also rejects all diagnostic false witnesses. Any such rule remains post-hoc until frozen and validated on a fresh holdout.

## Falsification criterion
If every public rule either misses a P1038 true witness or selects the P1039 false witness, P1040 is negative for this local disambiguator catalog.

## Reproduction command
```bash
PYTHONPATH=tasks/ecdlp_index_calculus \
  python3 tasks/ecdlp_index_calculus/low_term_total2_p1040_p231_public_disambiguator_scout.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1040_p231_public_disambiguator_scout.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1040_p231_public_disambiguator_scout_probe.json
```

## Results
Run timestamp: `2026-06-30T04:02:32Z`.

Artifact: `ecdlp_index_calculus_state/low_term_total2_p1040_p231_public_disambiguator_scout_probe.json`.

Claim status: `P1040_PUBLIC_DISAMBIGUATOR_CANDIDATE_WITH_DIAGNOSTIC_REJECTION`.

Witness classes:

| Class | Count |
|---|---:|
| `primary_forward_true` | 2 |
| `primary_forward_false` | 1 |
| `diagnostic_forward_false` | 11 |
| `primary_scout_true` | 12 |
| `other_true` | 36 |

Top candidate rule:

| Rule | Primary true | Primary false selected | Diagnostic false selected | Scout true | Description |
|---|---:|---:|---:|---:|---|
| `y_mod_11_in_primary_true_values` | `2/2` | `0/1` | `0/11` | `12/12` | public y-coordinate residue mod `11` is in `{2,7}` |

Other diagnostic-clean candidates were `x_mod_5_in_primary_true_values` and `x_mod_7_in_primary_true_values`, but both select `0/12` primary scout true witnesses. The `y mod 11` rule is therefore the better frozen-validation candidate because it keeps the scout control as well as the P1038 primary positives while rejecting the P1039 primary false and widened diagnostic false witnesses.

Primary witness feature table:

| Class | Window | Public | Salt pair | Salt gap | q-delta-min | rhs-delta-min | y mod 11 |
|---|---|---|---|---:|---:|---:|---:|
| true | `12520_12527` | `[5063,6547]` | `[174]` | 0 | 1826 | 5889 | 2 |
| true | `12552_12559` | `[4643,5694]` | `[166,175]` | 9 | 3995 | 2729 | 7 |
| false | `12704_12711` | `[9665,1060]` | `[172,175]` | 3 | 2512 | 4424 | 4 |

## Interpretation
OBSERVATION / POST-HOC / TOY-EVIDENCE: P1040 found public-local discriminators for the observed P1038/P1039 contrast. The best candidate is `public_y mod 11 in {2,7}` because it preserves both primary true witnesses and all primary scout true controls while rejecting the primary false and all diagnostic false witnesses in this artifact set.

Next concrete action: create P1041 as a frozen validation over fresh windows starting at `12760_12767`, using the strict P1029 leaf-8 route plus the public `y mod 11 in {2,7}` filter. Any forward compressed false prediction in the primary pool falsifies this frozen selector for that holdout.

## Interpretation boundary
This is a post-hoc public-feature scout over toy p231 artifacts. It does not prove a complete faster-than-rho ECDLP algorithm, sparse linear algebra closure, target descent, or a deployable selector. Pollard rho remains the one-target scalar-search baseline.
