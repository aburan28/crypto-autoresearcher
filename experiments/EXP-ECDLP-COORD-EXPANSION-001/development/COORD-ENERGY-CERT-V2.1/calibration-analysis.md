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

## Calibration 003

The exact registered development lockbox launched once from clean commit
`fe7c1c7cc7f5f4eb27caf56e6d3288cd2733e1ed` and tree
`0d215408bc6aa6423ac15b27f4eb1a933a9cd0df`.

- execution profile: `registered_development`;
- curves: nine generated 8-10-bit prime-order curves;
- candidate cells: 27, retained only for code-path coverage;
- exact eligibility boundary controls: all pass;
- public-coordinate positive control: pass;
- candidate-matched negative sentinels: 24/24 pass;
- worst negative retained enrichment: `0.038099`;
- minimum negative reference-tail rank: `0.023438`;
- predictor calibration gate: pass;
- producer screening signals: zero;
- independent verifier: valid;
- target rows independently reconstructed: 15,543;
- semantic and integrity mutations: 19/19 rejected;
- producer wall time/RSS: 133.12 seconds / 66,240,512 bytes;
- verifier wall time/RSS: 803.51 seconds / 73,318,400 bytes.

The full AP control bundle is false because three development null draws
cannot resolve the inherited `<=0.01` AP rank thresholds. That is expected
and outside the registered predictor-calibration gate. The packet authorizes
post-freeze seed-lock creation only.

## Next Concrete Action

Preserve the registered packet, derive the confirmatory seeds from frozen
commit `fe7c1c7c` using the contract's domain-separated procedure, commit the
seed lock without changing source or contract bytes, and launch the exact
confirmatory command once from a clean tree.
