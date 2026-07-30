# Red Team Result: Public Basis-Transition Secondary Audit

## Decision

P0 decision: no P0 blocker found in the recorded secondary audit. The result may be promoted only as `OBSERVATION / TOY-EVIDENCE / MODEL-BOUND` for the fixed public fixture.

P1 decision: keep the claim narrow. This is public basis-relative label transport, not isogeny recovery, not an `N=8` generality result, not an asymptotic claim, not an ECDLP speedup, and not a Pollard-rho comparison. The phrase "150 unit certificates" means 150 lane-side certificate records; it must not be read as 150 distinct algebraic unit values.

## Frozen Inputs

- Contract: `experiments/ecdlp_isogeny/iso_public_basis_transition_contract.md`
  - SHA-256: `2bafd1e6f0cd807338ab096f858374fe8e273255e863ac4818d01c1997c93f83`
- Harness: `experiments/ecdlp_isogeny/iso_public_basis_transition_certificate.sage.py`
  - SHA-256: `d3bf3e1f0d083d0701b40a890df33bf23a8253479aea75b1e32198758fb1e415`
- Result: `experiments/ecdlp_isogeny/iso_public_basis_transition_result.json`
  - SHA-256: `7a884d3b779c5bbf7e5a2b0823bd488e611a5ab9b6e09ba40fb6327db379ec99`
- Prelaunch red-team note: `research/red_team_public_basis_transition_prelaunch.md`
  - SHA-256: `75e43c63dd0d8239d181cbcc0f97ada814f1ad71b89feea85c7e50ecaf034490`

## Top-Level Result Assertions

Recorded result status:

- `success=true`
- `status=OBSERVATION`
- `evidence_type=TOY-EVIDENCE / MODEL-BOUND`

Recorded assertion booleans all pass:

- `contract_exists=true`
- `artifact_hashes_match=true`
- `lexical_source_audit_passed=true`
- `embedding_count_is_12=true`
- `all_embedding_certificates_pass=true`
- `preserved_strict_failure_is_raw_coordinate_only=true`
- `all_seed_certificates_pass=true`
- `all_controls_pass=true`
- `source_and_artifact_hashes_stable=true`

## Count Audit

- Seeds: `3`, exactly `20260720`, `20260721`, `20260722`.
- Public embeddings: `12`, indices `0..11`.
- Per-seed embedding lanes: `12` for each seed.
- Total lanes: `75`.
  - `round13_M48_to_theta_N16`: `3`.
  - `round13_M48_to_N8`: `36`.
  - `theta_N16_to_N8`: `36`.
- Unit certificate records: `150`, all success.
  - Source accepted unit count values: `[1]`.
  - Target accepted unit count values: `[1]`.
- Branch transports: `150`, all success.
- Reconstructed module certificates: `30`, all success.
  - Orbit sizes checked: `64/64` and `256/256`.
  - Annihilator check: only `[0,0]`.
  - Frobenius characteristic relation: true.
- Canonical map-body hashes transported:
  - `a2fb756a1e1b5f5cdfdfe8210b5e0656879898e4a6ba7326e03580b9efd4c560`
  - `bc561dbb89b58d60325df9ef280a2860763e6125ef97d068265bade281548636`

## Preserved Raw-Mismatch Check

The preserved strict raw-mismatch artifact is correctly consumed as a negative raw-coordinate equality result, not as a failed map-body result:

- Preserved result status is `OPEN`.
- Preserved result success is false.
- All three expected seeds are present.
- For every seed, selected raw branch equality fails while selected canonical map-body equality passes.
- Preserved Round13 and N16 branch tables match the hash-bound primary artifacts.
- Empty `j=274` comparisons pass.

## Controls

Controls pass as scoped negative and positive checks:

- Nonunit inverse is rejected.
- Inconsistent shear has `0` accepted units and is rejected.
- Generic swap matrix is invertible but rejected as an `R_n` unit because its Frobenius commutator is nonzero.
- Synthetic unit transport passes identity, round-trip, and point-action checks.
- Branch mutation is rejected against the fixed map-body key.
- Direct cross-degree coordinate-string comparison is rejected before equality is evaluated without an embedding.

## Source Stability

Start/end source stability passes:

- Contract start/end SHA-256 remains `2bafd1e6f0cd807338ab096f858374fe8e273255e863ac4818d01c1997c93f83`.
- Harness start/end SHA-256 remains `d3bf3e1f0d083d0701b40a890df33bf23a8253479aea75b1e32198758fb1e415`.
- Hash-bound primary artifacts remain stable:
  - Round13 crater queue: `8b11e7cacc8e1c6899fba04cd62af16f22224eb242baf5a90f4f442e6d4ff035`.
  - Theta-only N16: `3f761d3d11c515e4d4e4d7b14990d0707aa8e609ac55a72c1c126116ecc41773`.
  - Minimal N8: `b7e007ed9414aea05f0e0a24b10c59c8ce95a9755fd7d5c99e707851b519e51a`.
  - Preserved raw mismatch: `7e914f5e1440fae045a63d274576f775ead87c7f883faebbb771a09481253c28`.

## Limitations And Overclaim Corrections

- Say `fixed F_431 degree-7 class-number-two toy fixture`, not curve-family behavior.
- Say `public R/nR basis-relative branch-label transport`, not new isogeny recovery.
- Say `hash-bound local Sage field-model reconstruction`, not portable artifact independence.
- Say `OBSERVATION / TOY-EVIDENCE / MODEL-BOUND`, not theorem.
- Do not infer any asymptotic, deployment, ECDLP, or Pollard-rho implication.

## Required Next Falsification Action

Run a non-authoritative throwaway copy on a second nontrivial crater family with machine-parsable field and point metadata exported at source. The test must require the same result shape: exact hashes, all embeddings, unique source/target unit witnesses per lane, full orbit/annihilator/characteristic checks, preserved raw-mismatch table agreement, and branch transport by canonical map-body key.

## Handoff: public basis-transition post-run red team

### Claim or task

Post-run Red Team audit of the public basis-transition certificate result.

### Status

OBSERVATION / TOY-EVIDENCE / MODEL-BOUND

### Assumptions

- Fixed public `F_431`, trace `3`, degree `7`, selected target `j=57`, seeds `20260720..20260722`.
- The hash-bound local Sage field models are the intended artifact reconstruction models.
- Canonical numerator, denominator, and y-multiplier keys identify the same public map body across artifacts.

### Evidence so far

- Result SHA-256 is `7a884d3b779c5bbf7e5a2b0823bd488e611a5ab9b6e09ba40fb6327db379ec99`.
- All top-level result assertions pass.
- The audit records `3` seeds, `12` embeddings, `75` lanes, `150` unit certificate records, `150` branch transports, and `30` reconstructed module certificates.
- Controls and source stability pass.

### Failure modes

- The result would not survive a different curve family, field model, or artifact serialization without rerunning the same checks.
- A future artifact with multiple valid units per lane would need disambiguation by branch transport, not automatic promotion.
- If canonical map-body keys cease to identify the same public map body, branch-label transport is not meaningful.

### Next concrete action

Run the same certificate shape on a second nontrivial crater family with exported machine-parsable field and point metadata, then compare whether the unique-unit and transport-success counts survive unchanged.

### Artifact paths

- `research/red_team_public_basis_transition_result.md`
- `experiments/ecdlp_isogeny/iso_public_basis_transition_result.json`
- `experiments/ecdlp_isogeny/iso_public_basis_transition_contract.md`
- `experiments/ecdlp_isogeny/iso_public_basis_transition_certificate.sage.py`
