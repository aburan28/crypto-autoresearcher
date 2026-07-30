# Coordinate Energy Certificate V2.1 Calibration Analysis

## Status

`OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`, `PROTOCOL DEBUGGING`.

Neither `CALIBRATION-001` nor `CALIBRATION-002` is a registered calibration
packet or candidate evidence. Both used the now-consumed development seeds
`[1201,1301,1409]`. The registered development lockbox
`[2203,2309,2411]` remains unexecuted, and no post-freeze confirmatory seed
lock exists.

## Calibration 001

The first packet used 31 predictor permutations and eight binary planted-label
negative replicates. Its arithmetic and then-current independent replay were
valid, but its predictor controls failed:

- the positive control recovered `chi_x_minus_1=+` with perfect held-out
  enrichment and recall;
- its minimum possible rank was `1/32=0.03125`, which cannot cross the frozen
  three-family Bonferroni threshold `1/60`;
- every binary negative replicate failed the then-registered recall cap
  because ordinary broad buckets had recall between about 10% and 21%;
- maximum negative retained enrichment was only `0.100514`.

This is a `NEGATIVE RESULT` for the first control specification, not for the
candidate families.

The packet is not fully source-reproducible: it launched from a dirty
development tree and the exact dirty source bytes were not retained before
revision. Its source identities remain recorded:

- producer SHA-256
  `08ee248756baaadf8ce235f16055a3cd8f4b86547e398172b7e497b8a9638884`;
- verifier SHA-256
  `eac09cd9b5fff268e93953a455f9eaa1c9db3c87c98e06fb9c1d365cf9b6e979`;
- contract SHA-256
  `b7f129818239a56fac3fdb7f428dc0c00e254664f0b26bff2adbba83b37673e5`.

## Calibration 002

The second packet removed the invalid recall cap and used 63 permutations.
On the same consumed development curves:

- the positive control selected `chi_x_minus_1=+`, retained 100% enrichment,
  and reached rank `1/64=0.015625`;
- all eight binary negative replicates passed their sentinel checks;
- maximum negative retained enrichment was `0.100514`;
- no negative replicate or held-out curve passed the complete predictor gate;
- the then-current verifier reconstructed all nine curves, 27 null sets, 27
  candidate cells, and 15,825 target rows;
- all 19 then-registered mutations changed the verifier projection.

The packet is nevertheless `CONTROL-INVALID` for registered calibration after
red-team review because:

1. binary planted-label negatives do not match candidate-family heavy-tailed
   D4 multiplicities;
2. the verifier accepted arbitrary development profiles;
3. mutation checks detected projection changes rather than executing semantic
   mutants through the full verifier;
4. 63 permutations differed from the confirmatory pipeline;
5. the 1% eligibility boundary lacked exact below/at/above, balanced-null, and
   near-boundary positive controls.

Its exact dirty source identities are:

- producer SHA-256
  `f7d4597b8ad77659b45dda3e105a7fe4ea72583985ed561842d62d46b8d63f37`;
- verifier SHA-256
  `9f10a8d47fa75668f2887afebe9fc7d870b7af37d6760913cb923c3067df2926`;
- contract SHA-256
  `e9fa9e44ae9aa9b1cacd1f222d96529b6a07be113cd0a860b48f9c786bc24bbe`.

These exact dirty source bytes were also not retained before the subsequent
red-team revision, so the packet is preserved for diagnostic evidence rather
than source-level reproduction.

## Red-Team Repairs

The successor now preregisters:

- one exact registered development profile;
- 127 permutations in both registered development and confirmation;
- eight candidate-matched negative sentinels per family;
- exact eligibility fixtures below, at, and above 1%;
- a balanced 50/50 null and a just-above-1% planted positive;
- post-freeze confirmatory seed derivation;
- full-verifier execution for the five semantic eligibility/control mutants.

Eight sentinels per family do not establish a 1% false-positive rate. The
result is restricted to detecting the observed rare-bucket pathology and
gross candidate-matched instability.

## Next Concrete Action

Freeze the revised contract, producer, verifier, and tests in a clean commit.
Then execute the exact registered development lockbox once. Do not create the
post-freeze confirmatory seed lock unless that packet and its semantic
mutation runs verify.
