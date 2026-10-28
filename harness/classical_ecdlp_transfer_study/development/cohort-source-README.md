# Public-coordinate transfer cohort generator

`cohort.py` is a new source module for the fixed-circuit transfer study. It does not import the constructor, evaluate any candidate, make a log table, generate scalar truth, use a network or access credentials. Actual study cohort generation has **not** been invoked during this implementation task.

## Interface

- `describe_plan(plan)` validates the fixed public schedule and returns `fixture_count_planned`, `target_cases_planned`, per-stratum counts and proposal caps. It neither draws entropy nor enumerates future curve points.
- `generate(plan, outdir, *, exclusions_data)` requires `plan.status == "frozen"` and a fresh nonexistent output subdirectory. The engine should use its raw directory's `cohort/` child. The caller checks the raw exclusion-file hash before supplying the decoded object.
- The returned public record has `schema: classical.ecdlp.transfer-study.public-cohort/v1`, `generation_status: complete|incomplete`, `public_nonce_hex`, `fixtures` and explicit shortfalls. Incomplete generation requires zero subsequent candidate attempts; it must not be filtered into a smaller successful panel.

The frozen `cohort` object requires a fixed 64-hex `seed_hex` and `strata`. Each stratum has `id`, `curve_count`, `p_min`, `p_max`, `target_mode`, `max_proposals`, and either fixed `target_order` for `all_nonidentity`, or `target_count` plus an optional `r_bits` for `sampled_unique`. The point-sampling cap is separately fixed with `max_point_sampling_attempts` (default 10,000).

The agreed study schedule is eight exact curves (two each with order 17,31,61,127; 464 targets) and 32 sampled curves (16 with field/order bitlength 10 and 16 with bitlength 13, 64 unique nonidentity targets each). The module remains schedule-driven; it does not hardcode or generate those future fixtures during import or plan description.

## Selection and retention

A fresh 256-bit public nonce is written with exclusive creation, flush and `fsync` before any future curve proposal. SHAKE256 domains include the fixed seed, nonce and canonical JSON plan hash. `plan_canonical_sha256` is explicitly a semantic canonical-plan digest; the engine/provider separately binds the original raw plan-file SHA. All random integers use rejection sampling rather than biased modulus reduction.

Each proposal samples a uniformly chosen integer congruent to 3 modulo 4 in the declared interval, then public coefficients. It records a durable proposal intent before primality, discriminant, complete quadratic-residue point census, exact/bitlength order, ordinary/anomalous and deduplication checks. Every result includes its public rejection reason and cost delta. Selection never consults constructor output. The proposal cap is per stratum and is never extended after seeing results.

The frozen exclusion document is exactly `classical.ecdlp.transfer-study.exclusions/v1`. `curve_keys` excludes equal `(p,j)` keys, which is stronger than excluding only one Fp-isomorphism class because twist classes are also excluded. `excluded_fields` is honored defensively. The final Coordinator-owned metadata has raw SHA `d9601d4ae9b963e4885382d637a6103a50d6d42aa17f2e8a28f7aec418c321a6`; it contains only prior published/development metadata, including fields 11 and 383.

Accepted curves are nonsingular with an exactly counted odd prime total group order different from the field prime, nonzero trace, and a public nonidentity base satisfying `[r]P=O`. A coordinate sampler chooses random x, rejects nonresidues/zero roots and chooses the root sign uniformly. On an odd prime-order curve there are no affine order-two points, so this yields uniform nonidentity points without scalar labels. Exact targets are all finite public points in lexicographic coordinate order; sampled targets are unique public coordinates and duplicate rejections remain counted. Transformed bases are the engine's known public multiples, never favorable unrelated points selected by this generator.

Outputs are `cohort-nonce.json`, `cohort-public.json`, `cohort-history.jsonl`, `cohort-costs.json` and `cohort-completion.json`. Live atomic snapshots retain accepted prefixes. A selection cap or caught generation failure returns an incomplete public cohort and retains the prefix, history, counts and actual exception; no candidate work is authorized on it. Uncaught interruption still leaves its durable nonce and intent prefix for the outer failure sealer.

## Cost scope and evidence

The module records actual residue-table construction, x-census, RNG, sampling, primality and public base-order checks separately from candidate operation counters. SHAKE/builtin modular inverse/power invocations, Python control/containers, I/O and integer bit costs are not assigned arbitrary prices. It is not an efficient point-counting proposal; it is finite public input construction and validation work. No timing or complexity advantage is claimed.

Sources checked (internal provenance): `AGENTS.md`; literature-first and observation-first sections of `docs/agent-contract-extended.md`; prior `harness/classical_ecdlp_nongeneric_screen/curve.py` for the unchanged affine ledger and public order check; `harness/classical_ecdlp_endpoint_reuse/cohort/curve_identity.py` for the distinction between representation identity and isomorphism identity; prior public `cohort/public/fixtures.tsv`; current goal's fixed-circuit and known-multiplier transfer requirement. This task implements established exact finite-field point census and sampling; it proposes no mathematical novelty. No external primary source was fetched under this task's no-remote restriction. The exact arithmetic and scope assumptions are checked by the mechanical tests and the separate independent verifier; a source hash alone is not mathematical verification.

## Software checks

Fifteen tests passed in 0.008s. They use the already published F11/order13 fixture and mocked invalid/duplicate proposal paths only. They test draw-free description, configuration refusal, exact known census, j scaling/twist keys, coordinate target order, uniform-root mechanics, deterministic domain separation, frozen/fresh-directory guards, durable incomplete prefixes, excluded-field refusal and residue-cache bounds. No future study curves or fresh entropy were drawn.

The initial test run exposed a test mock that incorrectly marked the fixed order 13 nonprime; that original failure log is preserved, and the mock was narrowed to reject only candidate fields. Interface iterations before source freeze are preserved outside canonical, including the brief exclusion-schema alignment race. Only the final source hash in `delivery.json` should be copied and frozen.
