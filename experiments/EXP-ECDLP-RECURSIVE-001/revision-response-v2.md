# Pre-Run Revision Response V2

## Status

`OBSERVATION`: independently audited `GO` at commit `90ff031`. No canonical run has occurred.

The `v1` static audit returned `REVISE`. Its preserved SHA-256 is `8b6b3723f3198dcc607eb17b5937adab16f0305142a8ad67dd1fc484e3a933b7`.

## Finding closure

### Functional preprocessing metric

`CLOSED IN V2`: promotion now requires:

```text
final_support_ratio_to_random >= 0.8
success_adjusted_st2_ratio_to_random <= 0.8
offline_group_operations_ratio_to_random_x <= 4.0
replication count >= 3
```

The normalized metric uses functional witness-map deep bytes for `S`, average online group operations for `T`, exact `|mA|/q` for `epsilon`, and subgroup order `q`. Advice-entry and online-operation ratios remain diagnostics and cannot bypass the joint gate. A self-test sets both legacy ratios to `0.01` while the functional metric exceeds `0.8` and requires rejection.

### Source hash chain

`CLOSED IN V2`: generator output contains the runtime SHA-256 of both executable source inputs. The verifier recomputes both local files, compares them to frozen constants, reconstructs the exact source object in the submitted result, and rejects any mismatch before arithmetic replay.

- generator: `c8e6986dd48e341b3e585a170990a018210602f99fc6cd748b81902f1b4e446d`
- independent verifier: `d677d1bc9c7efa9c3a94704eddd2f80ea651074f55c4a8452e5295f5d9797552`
- imported coordinate arithmetic: `7e9b16c18c5855ef7786f78d42300e63fb2a3dcf768413355a31d14160c6ea71`

The raw result is itself hashed by the immutable run manifest, and verifier output records the input raw-result hash.

### Controls and field-family disclosure

`CLOSED IN V2`: the unimplemented shuffled-source-tag promise was removed. It was replaced by the enforced source-hash control. The specification, contract, hypothesis, candidate checklist, generator curve record, and verifier reconstruction disclose the seeded `p mod 4 = 3` field-prime restriction and its deterministic-square-root purpose.

### Exact reproduction

`CLOSED IN V2`: the contract lists every required generator argument and gives the exact second immutable verifier command. It requires committing the generator run before the verifier run so both manifests record clean Git states.

### Parser hardening

`CLOSED IN V2`: the verifier self-test now explicitly executes duplicate-key and non-finite JSON rejection, in addition to strict Boolean/float rejection for exact integer fields.

## Verification

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m unittest discover -s tests -v
8 tests passed

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m crypto_autoresearcher.cli validate experiments/EXP-ECDLP-ENERGY-001 experiments/EXP-ECDLP-RECURSIVE-001
13 records validated

python3 -B experiments/EXP-ECDLP-RECURSIVE-001/src/verify_recursive_expansion.py --self-test
18 checks passed; experiment_harness_executed=false
```

## Remaining boundary

The functional-byte `S*T^2/(epsilon*q)` ratio is an implementation-specific matched-control diagnostic, not a calibrated theorem instantiation. The experiment still stops before relation independence, rank, sparse linear algebra, individual logarithm descent, asymptotic fitting, and any deployed-curve mapping. A `GO` authorizes toy evidence collection only.

## Next concrete action

Record coordinator approval in a separate Git commit, then launch the exact first immutable command from `contract.md`.
