# BINSTD yield ceiling formal review plan (prepared, not dispatched)

Immutable input tree: `8d7fc59238ce0230c4ec3b32ef43519356ffb2dd`. This plan records the prior before independent review. No verdict is assigned.

## Claim and prior

Producer claim: in the four archived BINSTD Stage-1 toy cells at n=17 and ell 8/9, open hits all 40 targets; conditional on that observation, no tau hit count in 0..40 can reach the 1.25 tau/open band. The named Lean declaration is `CryptoResearch.Binstd.YieldCeiling.saturated_open_below_band`; the second declaration instantiates four numeric pairs.

Prior: the arithmetic statement appears plausible and the four committed aggregate rows agree with its literals. The run output, EC arithmetic, and Lean machine verification at this exact head have not yet been independently established.

Observed after recording this prior: a negative control against the archived post-run checker accepted a stage-1 `completed_valid` raw result with no hit counts, no yield matrix, no artifact digest, and a placeholder manifest (exit 0); an invalid status was rejected (exit 1). The retained control is `binstd-postrun-checker-control-20261030.json`, SHA-256 `c6c25ce7874cc6cbbf5c3b2fac58c1c7215aca2251c7b91902315f5432c0e566`. Reviewers must treat the archived checker exit code as status/outcome syntax evidence only.

## Bound inputs

- `experiments/EXP-BINSTD-8bdf86/stage1-ell89/yield-matrix.json` SHA-256 `9356f502e98263b672bbde019e87a5f5b0a6a2a7b5f4425cf596ace8baf3fbf5`
- `experiments/EXP-BINSTD-8bdf86/stage1-ell89r1/yield-matrix.json` SHA-256 `fc5a2beb0bc2117eb5f9b05f844826c4c712417088f45da93351e942f3e8d8bc`
- `formal/CryptoResearch/Binstd/YieldCeiling.lean` SHA-256 `c76fc9b90a315285ac0d4e9913938f46131605575e5868ed90600773479463de`
- `formal/targets/binstd-yield-ceiling.yaml` SHA-256 `27137822c177c837e8dca5325faa4ef1730df5bf4a9d9a1d417f4003afc997b8`
- `knowledge/findings/KN-FIND-48f0ae.md` SHA-256 `92cfa7ce3588e426df96aca1eaf0f55c710c653752472fed5cca0ec3d5912f02`
- Lean toolchain `leanprover/lean4:v4.35.0-rc1`; Mathlib revision `7fa22735254ddf7e11f119250a9f2d0352bc7c3a`.
- Static input precheck SHA-256 `79a513f59835e5afde3942bef35df0bf410c324056b57bb97d364473ab24cf4e`; static run-link precheck SHA-256 `f9e51dd0c1b77f8c5c9c5609599d358fc2e555afbed510f58ae08c5cefcb78c0`.

## Independent joints and attacks

1. Mathematical boundary (semantic reviewer): derive the 1.25 band from matched target counts without the producer proof. Attack zero targets, unsaturated open hits, tau hits above targets, and the equality case. Check that the Lean quantifiers and hypotheses cover exactly the conditional claim.
2. Source binding (evidence reviewer): recompute the four hit pairs and ratios from committed yield matrices, check each raw-result digest link, then trace the execution receipts and archived check logs. Attack a changed yield matrix, a swapped ell or seed, and a source summary inconsistent with the raw run. A digest match alone does not authenticate execution.
3. Machine gate (verifier owner): in an isolated immutable snapshot, build the named module explicitly on pinned Lean and Mathlib, print both declaration types and transitive axioms, and run the complete-source formal gate plus an independent checker where available. Attack an omitted module, wrong theorem name, and a custom axiom. Existing receipt JSON is not fresh verification.
4. Claim scope (coordinator): compare the two reviewers and machine log with `KN-FIND-48f0ae`, preserving its empirical-only proof status unless execution and semantic obligations genuinely pass. Do not promote a four-row arithmetic fact into a runner or curve result.

## Blind re-derivation packet

Give the blind reviewer only: nonnegative integers `targets`, `tauHits`, `openHits`; assumptions `targets>0`, `openHits=targets`, `tauHits<=targets`; requested band `tauHits/openHits < 5/4`; and the four hit pairs. Forbid access to the Lean source, target YAML, producer finding, saved prechecks, receipts and sibling report until their derivation is sealed.

## Dispatch and completion gates

Before dispatch, archive this plan and exact input hashes under a Conductor review task, then give each reviewer isolated inputs and require read attestations. Completion needs fresh machine evidence, independent semantic reports, a checked independence contract, controls, an inspected report PDF, and a published technical packet. None of those later gates is claimed here.
