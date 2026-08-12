# Implementation v1

## Status

`OBSERVATION` - implementation complete and independently reviewed `GO` for
the frozen development execution. This is a `SANITY_ONLY` implementation, not
an ECDLP improvement.

## Programs

- `src/generate_tt_norm_rank.py` is a standard-library-only producer. It
  transcribes the frozen 40-gate RCB addition law literally, evaluates all
  registered five-source tuples, computes `g_Q`, `h_Q`, and the scheduled pure
  powers, measures exact unfolding ranks, emits D2/D3 comparators, and records
  operations, logical traffic, canonical storage, RSS, and provenance.
- `src/verify_tt_norm_rank.py` does not import the producer or existing EC
  arithmetic. It independently reconstructs the manifest, RCB circuit,
  source tables, target residuals, norm identity, source-span identity,
  zero sets, projective rescaling, ranks, controls, schedule, and accounting.
  It also hashes the local producer source and requires that hash to match the
  producer artifact.
- `tests/test_tt_norm_rank.py` covers RCB identity/inverse/doubling behavior,
  frozen control profiles, C08 semantics and rescaling, base/extension rank
  equality, all 15 mutation detectors, and producer-import independence.

## Frozen hashes

| Boundary | SHA-256 |
|---|---|
| producer | `98b5739a544dbfba74d1b62bc235fcb9d9389780c09a21fd0ed4670756540e0a` |
| independent verifier | `f8a1d6deb19115df70405a1e437ddb1b7d8823ca0a3fe9cc691f5f989e675056` |
| focused tests | `f805d053d829454ec6fd6905ad817f66c17f7ccc98d05b0f26f22d0552b28ee7` |
| instance manifest v1 | `a6c8e8297e74328d577d299245b0087ee96f61ec3d3acc580b4acf3e559161cc` |
| execution matrix v3 | `77bd8ed64956d3795aec65a23f3f3dd381b54a368c83c4b8eea0dc6263618a43` |
| mutation manifest v2 | `45d052855e89b5aad7834d9f9fdfecaf5e75cbab31dfcf58b5ebb63b6a6aed01` |

The artifact protocol is
`EXP-ECDLP-TT-NORM-RANK-001-development-v3`, matching the V3 contract and
traffic model. The hard-coded protocol commit is the reviewed protocol-only
commit `ec0b9e075b1dfa77bca453fd452e56cfb514b7e4`.

## Pre-run replay

The unregistered local round trip completed with:

- 24 source tables and 615,868 source tuples;
- 2,463,472 RCB calls;
- 60 semantic cells and 1,539,670 residual/norm evaluations;
- 264 EC rank jobs plus 24 controls, for 288 total rank jobs;
- 12 tested-cohort span jobs and 18 comparator jobs;
- zero semantic, projective, source-span, zero-set, rank-cap, schedule, or
  traffic mismatches;
- 336,364,325 observed base-field-word-equivalent rank traffic, below the
  frozen 587,622,372 ceiling;
- producer/verifier peak RSS of 189,513,728/186,859,520 bytes;
- all 15 frozen mutations detected, with zero survivors.

These `/tmp` artifacts are implementation checks only. They are not registered
evidence and are superseded by harness-created run directories.

## Trust and claim boundary

Primary curves, generators, registries, targets, mode order, tuple order,
addition tree, and rank fields are frozen before tensor evaluation. Full
enumeration is charged and labeled diagnostic; it is not retained as advice.
The output requires `SANITY_ONLY`, `breakthrough_claim=false`,
`compiler_constructed=false`, and `success_probability=not_applicable`.

The implementation validates the first-norm tensor and its exact toy ranks.
It does not construct coefficient-space advice, compress `h^(p-1)`, locate
zeros without enumeration, generate relations, solve ECDLP, or beat rho.

## Next concrete action

Execute the four frozen development run partitions through the repository
harness and preserve the immutable generator/verifier artifacts.
