# Experiment Contract: Coordinate Energy Certificate V2.1

## Candidate

Repair the V2 target-wide predictor protocol by excluding categorical buckets
whose training support is too small for stable held-out enrichment, while
leaving the frozen coordinate families, exact additive metrics, public
witnesses, null law, and multiple-testing gates unchanged.

## Status

`HYPOTHESIS`, `TOY-EVIDENCE`, `MODEL-BOUND`, `PREREGISTERED`,
`RED-TEAM REVISED`.

This is a protocol-repair successor to the control-invalid V2 run. It is not
an ECDLP improvement and cannot retroactively validate or invalidate V2
candidate outcomes.

## Incorporated V2 Contract

This contract incorporates the complete
`development/COORD-ENERGY-CERT-V2/contract.md` contract with SHA-256
`6e2bc68174d067b323914205d75e3f7c0ab5630a20cb915667fbb870a131a2f6`.
Every V2 clause remains binding except where this document explicitly
replaces it.

The following V2 evidence is context, not input data:

- raw-result SHA-256
  `dede6ffad9091fa21838d986463e83f62908283b730dd26ff98d290f93ff4456`;
- verification SHA-256
  `285926b435c8fe32e734f80b265ecc1232ea8a8273af950cc92fd4db6bb89286`;
- status `CONTROL-INVALID`;
- invalid reason `mandatory predictor-negative control failed`.

No V2 candidate statistic may be used to tune V2.1 or interpreted as V2.1
evidence.

## Hypothesis

After enforcing a 1% pooled and per-training-curve bucket-coverage floor, the
registered public-coordinate positive control is learnable and each
candidate-matched deterministic permutation sentinel stays below 20% held-out
retained enrichment while failing the complete predictor gate.

The 1% rule is hypothesized only to exclude the observed V2 rare-bucket
pathology. It is not assumed to establish a general concentration or
stability theorem for heavy-tailed D4 multiplicities.

Conditional on those controls passing, the unchanged candidate pipeline can
validly test whether one of the three registered coordinate families has
joint additive-energy, public-certificate, and target-wide predictor
structure on fresh generated curves.

## Null Hypothesis

At least one of these holds:

1. the repaired learner cannot recover the public-coordinate positive
   control;
2. at least one permuted-label negative control exceeds 20% held-out retained
   enrichment or passes the complete predictor gate;
3. no candidate family passes every unchanged V2 gate;
4. independent reconstruction or mutation testing fails.

Items 1, 2, or 4 make the run invalid. Item 3 is a scoped negative only if
every mandatory control and verification gate passes.

## Frozen Predictor Eligibility

The learner still fits exactly one categorical feature and exactly one
bucket. Before labels or multiplicities are used to rank a bucket, the bucket
must satisfy all of:

1. pooled training coverage at least `0.01`;
2. coverage at least `0.01` on every individual training curve;
3. at least one row on every training curve.

Coverage is `bucket_rows / all_rows` in the corresponding training scope.
The threshold comparison is exact integer arithmetic:

`100 * bucket_rows >= all_rows`.

For each feature, rank only eligible buckets by:

1. decreasing training mean multiplicity;
2. increasing bucket string.

Across features, retain the V2 deterministic ordering:

1. maximum training retained oracle enrichment;
2. maximum training F1;
3. lexicographically maximum feature name;
4. lexicographically maximum singleton bucket list.

If no eligible bucket exists, fitting fails closed and all predictor and
control gates are false. The producer and verifier must store:

- minimum pooled training coverage;
- minimum per-training-curve coverage;
- eligible bucket count per feature;
- selected-bucket pooled count and coverage;
- selected-bucket count and coverage for every training curve;
- a deterministic eligibility digest.

The 1% floor applies identically to observed candidate labels, permutation
fits, the public-coordinate positive control, and every permuted negative
control. Held-out labels never affect eligibility.

## Predictor Gates

The V2 held-out gate remains unchanged. Every held-out curve must have:

- at least 1% predicted coverage;
- at least 10% recall;
- nonzero precision;
- at least 80% retained oracle enrichment.

The pooled candidate predictor must retain at least 80% oracle enrichment and
survive the same 127-permutation Bonferroni screen over three families.

The permutation statistic remains
`max(0, retained_oracle_enrichment) * recall`.

## Predictor Controls

### Positive control

Retain the V2 public feature `chi(x-1)=+1`. The repaired learner must:

- select `chi_x_minus_1=+`;
- satisfy every training eligibility receipt;
- retain at least 95% held-out enrichment;
- pass every pooled and per-curve predictor gate;
- survive the same permutation and Bonferroni procedure.

### Negative controls

For each of the three candidate families, use eight deterministic,
domain-separated within-curve permutations of that family's complete
`(multiplicity, positive)` label pair. Feature rows and target coordinates
remain fixed. Each of the 24 replicates uses the same frozen learner and its
own permutation reference distribution. Every replicate must:

- satisfy selected-bucket training eligibility;
- fail the complete predictor gate;
- have pooled held-out retained enrichment at most `0.20`;
- have no held-out curve that passes all per-curve gates.

The negative-control suite passes only if all eight replicates for all three
families pass. Report per-family and global maximum retained enrichment,
maximum recall, minimum reference-tail rank, and all replicate receipts. No
median or majority rule is allowed.

These 24 replicates are sentinels against the observed failure mode. They do
not estimate or claim a 1% false-positive rate; zero failures in eight
replicates per family is too small for that claim.

## Eligibility Boundary Controls

Before any registered development packet can calibrate, exact synthetic
fixtures must establish:

- a bucket immediately below 1% on every training curve is ineligible;
- a bucket exactly at 1% on every training curve is eligible;
- buckets at 2% and 5% on every training curve are eligible;
- a pooled 1% bucket absent from one training curve is ineligible;
- a balanced 50/50 feature with independently permuted labels is accepted as
  null-like even when recall is near 50%;
- a planted informative bucket just above 1% is selected and recovered.

These controls test implementation boundaries, not statistical generality.

## Development Calibration

The first two development packets using seeds `[1201,1301,1409]` are consumed
protocol-debugging runs. They must be preserved as `CALIBRATION-001` and
`CALIBRATION-002`, but neither may satisfy the registered calibration gate.

Before freezing a confirmatory launch, run the registered development lockbox
with:

- bits `[8, 9, 10]`;
- development curve seeds `[2203, 2309, 2411]`;
- 127 predictor permutations, identical to confirmation;
- eight candidate-matched negative-control replicates per family.

Development calibration may execute the candidate machinery for code-path
coverage, but candidate values are non-evidence and cannot alter the
contract, feature dictionary, thresholds, or confirmatory seeds.

The development calibration succeeds only if the eligibility boundary
controls, positive control, and all 24 candidate-matched negative sentinels
pass and independent verification reconstructs every eligibility receipt.

The verifier must classify packets as exactly one of:

- `registered_development`: the exact lockbox profile above;
- `exploratory_development`: any other development profile;
- `confirmatory`: the exact seed-lock profile below.

Only `registered_development` may satisfy the calibration gate.

## Fresh Confirmatory Configuration

Confirmatory curve seeds must not exist before the producer, verifier,
contract, and tests are frozen in a clean Git commit. After that freeze,
create `confirmatory-seed-lock.json` in a second commit. For replicate index
`i in {0,1,2}`, derive:

`seed_i = 1 + int(SHA256(domain || freeze_commit || i)[0:8],16) mod (2^31-2)`

where `domain` is the ASCII string
`EXP-ECDLP-COORD-EXPANSION-001-COORD-ENERGY-CERT-V2.1-SEED`.

The lock records the freeze commit, derivation domain, three derived seeds,
and its construction command. Producer and verifier both hash and enforce
the lock.

The only V2.1 confirmatory configuration is:

- bits `[10, 12, 14]`;
- the three post-freeze seeds in `confirmatory-seed-lock.json`;
- 2,047 canonical-random-fiber null draws per curve;
- 127 predictor permutations;
- eight negative-control replicates;
- development mode false.

Any other parameter set is exploratory development and cannot produce a
screening or positive signal.

## Unchanged Candidate Surface

The candidate families remain exactly:

1. `coset_prefix_chain`;
2. `quartic_composition_chain`;
3. `reciprocal_denominator_chain`.

Factor-base construction, `B=max(5,round(q^(1/5)))`, canonical-random-fiber
null generation, exact D2/D4 metrics, numerical Fourier diagnostic,
popular-difference and Freiman witnesses, 27-test energy Holm family,
81-test certificate Holm family, scalar-free construction gate, public EC
replay, and V2 family success criteria remain unchanged.

No candidate parameter, feature, or threshold may be changed after
development calibration. A control repair may not weaken any candidate gate.

## Independent Verification

The V2.1 verifier must not import the producer. It must independently:

- reconstruct every curve, factor base, null set, and target row;
- recompute D4 using direct ordered four loops;
- reconstruct bucket eligibility using exact integer comparisons;
- replay selected-bucket pooled and per-training-curve receipts;
- reproduce all candidate, permutation, and control predictor fits;
- replay exact ranks, Holm correction, public EC witnesses, and family gates;
- reject mutations to an eligibility threshold, eligible-bucket count,
  selected-bucket count, per-curve coverage receipt, and negative replicate.

Every registered semantic mutant must be submitted to the complete verifier
and produce `valid=false`. Mutation code must recompute any attacker-controlled
payload digest affected by the mutation, so a changed projection hash cannot
be the sole rejection reason. Telemetry digest mutations remain packet
integrity tests only unless an external wrapper receipt is present.

A valid verifier receipt is necessary but does not override a failed control.

## Success Criterion

A verified V2.1 positive signal requires:

1. the exact fresh confirmatory configuration;
2. all unchanged V2 candidate gates;
3. the repaired public-coordinate positive control;
4. all eight repaired negative-control replicates;
5. scalar-free candidate construction;
6. a clean frozen launch tree;
7. independent verification and all registered mutation rejections.

A positive signal authorizes only a separately contracted, fully charged
relation-compiler experiment. It is not an algorithmic promotion or an ECDLP
improvement.

## Falsification And Interpretation

- failed development controls: revise only the control/eligibility model and
  do not consume confirmatory seeds;
- failed confirmatory controls: mark the run invalid and preserve no candidate
  conclusion;
- valid controls with no candidate family pass: preserve a scoped V2.1
  negative for these three families, nine fresh toy curves, and this exact
  metric/certificate/predictor dictionary;
- valid candidate signal: independently reproduce on another fresh schedule
  before relation-compiler work.

No outcome is a generic structured-group barrier, an index-calculus
algorithm, or an exponent improvement.

## Reproduction Commands

Development calibration:

```bash
python3 experiments/EXP-ECDLP-COORD-EXPANSION-001/src/coord_energy_certificate_v21.py \
  --bits 8 9 10 \
  --curve-seeds 2203 2309 2411 \
  --null-draws 3 \
  --predictor-permutations 127 \
  --negative-control-replicates 8 \
  --development
```

Frozen confirmatory launch:

```bash
python3 experiments/EXP-ECDLP-COORD-EXPANSION-001/src/coord_energy_certificate_v21.py \
  --bits 10 12 14 \
  --null-draws 2047 \
  --predictor-permutations 127 \
  --negative-control-replicates 8
```
