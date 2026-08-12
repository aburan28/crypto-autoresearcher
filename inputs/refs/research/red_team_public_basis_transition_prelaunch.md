# Red Team Handoff: Public Basis-Transition Prelaunch Final Hash Review

Reviewed current inputs:

- `experiments/ecdlp_isogeny/iso_public_basis_transition_contract.md`
  - SHA-256: `2bafd1e6f0cd807338ab096f858374fe8e273255e863ac4818d01c1997c93f83`
- `experiments/ecdlp_isogeny/iso_public_basis_transition_certificate.sage.py`
  - SHA-256: `d3bf3e1f0d083d0701b40a890df33bf23a8253479aea75b1e32198758fb1e415`
- `research/ascending_isogeny_basis_transition_design.md`
  - SHA-256: `7e1227293f3418b6aee247548744522ddd76a6582bc0e77be0521e211962f5c4`

This note supersedes the stale prelaunch Red Team note. The authoritative
certificate was not run in this review.

## Final Hash Go/No-Go

Final-hash decision: GO for one authoritative certificate run as a scoped
`TOY-EVIDENCE / MODEL-BOUND`
artifact, provided the output claim remains limited to this fixed public
`F_431`, trace-`3`, degree-`7`, seeds-`20260720..20260722` fixture.

No P0 blocker remains in the latest harness. A successful run would support only:

> Public `R_n` unit basis transitions explain the raw branch labels attached to
> identical canonical map bodies across the hash-bound Round13 `M=48`,
> theta-only `N=16`, and minimal `N=8` toy artifacts, under the recorded local
> Sage field-model assumptions.

It would not support a new-isogeny recovery claim, an `N=8` generality claim, an
asymptotic claim, a Pollard-rho comparison, or a deployment/ECDLP claim.

## P0 Findings

None in the latest reviewed versions.

Resolved during hardening:

- Transport direction now remains consistent with the design: the scanner
  recovers `P_new = u * P_old`, and branch transport uses
  `gamma_new = u0 * gamma_old * u1^-1`.
- Reconstructed generators now get full `n^2` orbit, zero-annihilator, and
  Frobenius characteristic-relation certificates, closing the earlier risk that
  exact scalar order alone was too weak for an `R_n`-module basis claim.
- Synthetic controls now include identity transport and a point-action check,
  so the target inverse direction is tested outside the real artifacts.
- Failed-lane handling no longer crashes the branch-mutation control; a missing
  reference transport makes the control fail closed.
- The preserved strict N16 failure is now semantically consumed: every seed must
  show selected raw branch inequality, canonical map-body equality, and
  successful empty-target comparison before the top-level certificate can pass.
- The preserved strict N16 failure also matches its recorded branch tables to
  branches independently extracted from the hash-bound primary Round13 and N16
  artifacts on every seed.
- Direct cross-degree string comparison is now an executable negative control:
  the guard receives actual degree-12 and degree-24 artifact points, derives
  degrees from each point's `base_ring().degree()`, and must reject before text
  equality is evaluated when no embedding is supplied.

## P1 Findings

1. Artifact independence remains conditional on local Sage field models.

   Evidence: the harness reconstructs serialized point strings in deterministic
   local `GF(431^12,"z")` and `GF(431^24,"z")` models, and the output explicitly
   records the assumption that those models match the serialized artifact models.

   Required correction: keep this as `MODEL-BOUND` evidence. Do not call it a
   portable standalone public certificate until future artifacts export
   machine-parsable field defining polynomials, coefficient arrays, and explicit
   source-model metadata.

2. Operation proxies are useful but not complete enough for cost claims.

   Evidence: unit scans, orbit scans, scalar-order checks, timings, and RSS are
   recorded, but ring multiplication, inversion, Frobenius-image, and point
   addition counts are not fully normalized or aggregated.

   Required correction: use these numbers only as audit instrumentation, not as
   runtime evidence. Add explicit operation-counter aggregation before making
   even toy cost comparisons.

3. The prohibited-oracle audit is source-review plus lexical sentinel, not a
   proof of absence under arbitrary refactoring.

   Evidence: the current harness imports only Sage primitives and reads
   hash-bound JSON, and no forbidden oracle call was seen in review. The lexical
   audit remains marker-based.

   Required correction: adequate for this prelaunch run, but future reusable
   certificates should add a runtime call sentinel or narrower import boundary.

4. Preserved branch-table independence is adequate but not maximally
   self-contained.

   Evidence: the preserved strict-failure check re-extracts the selected primary
   Round13 and N16 branch sets seed-by-seed from the hash-bound primary artifacts
   and compares the preserved tables to those extracted sets. The final success
   path also requires within-artifact equality controls for Round13 direct/CRT
   and N16 direct/theta.

   Required correction: acceptable for this one run. A future reusable
   certificate should directly extract and compare each primary branch family
   table-to-table inside the preserved-mismatch certificate, instead of relying
   on the separate within-artifact control to collapse equivalent branch sets.

## Required Controls For Authoritative Interpretation

The authoritative run should be interpreted as successful only if the JSON output
shows all of the following:

- Contract and harness hashes match the reviewed values above.
- All four artifact hashes match the harness constants at start and end.
- All three seeds are present.
- `preserved_raw_mismatch_certificate.success` is true: the strict N16 artifact
  is `OPEN`, fails selected raw branch equality on every seed, preserves
  canonical map-body equality, passes the empty-target comparison, and its
  recorded branch tables match branches independently extracted from the
  hash-bound primary Round13 and N16 artifacts.
- Round13-to-N16 succeeds at modulus `16`.
- Round13-to-N8 and N16-to-N8 succeed at modulus `8` for every recorded
  `GF(431^12) -> GF(431^24)` embedding.
- Every reconstructed generator and Frobenius image has exact required order,
  full `n^2` orbit, zero annihilator, and the characteristic relation
  `pi^2 - 3*pi + 431 = 0`.
- Every source and target lane has exactly one accepted `R_n` unit witness.
- Unit certificates show odd norm, verified inverse, determinant equal to norm,
  and zero Frobenius commutator.
- Branch equality is keyed by exact canonical numerator, denominator, and
  y-multiplier map body, not by unordered branch labels alone.
- Empty `j=274` payload controls remain empty.
- Controls pass, including `direct_cross_degree_string_comparison` showing
  `rejected=true`, `comparison_performed=false`, and unequal degrees derived
  from the actual artifact point base rings.

## Overclaim Corrections

- Say `OBSERVATION / TOY-EVIDENCE / MODEL-BOUND`, not theorem.
- Say `public basis-relative label transport`, not isogeny recovery.
- Say `fixed F_431 toy fixture`, not curve-family behavior.
- Say `hash-bound local Sage field-model reconstruction`, not fully portable
  artifact independence.
- Say `no Pollard-rho or ECDLP implication`, not cryptanalytic speedup.

## Next Falsification Tests

1. Direction mutation: run a non-authoritative copy with `u1` instead of
   `u1^-1` in `transport_branch`; the synthetic point-action control and real
   branch transports should fail.
2. Embedding twist stress: force one `GF(431^12) -> GF(431^24)` embedding index
   to be omitted or mislabeled; aggregation should fail rather than silently
   accepting a subset.
3. Cross-degree guard tamper test: in a throwaway copy, supply same-degree
   points or an explicit embedding and verify the guard no longer reports the
   no-embedding rejection path.
4. Preserved-failure tamper test: in a throwaway copy, flip one selected
   map-body equality or empty-target success bit in the strict-failure artifact;
   the top-level `preserved_strict_failure_is_raw_coordinate_only` assertion
   should fail.
5. Primary-branch tamper test: in a throwaway copy, alter one preserved
   Round13/N16 branch table entry; the primary-artifact branch-table match must
   fail seed-by-seed.
6. Field-model portability test: regenerate one future artifact with explicit
   coefficient arrays and defining polynomial metadata, then verify the
   certificate without `sage_eval` on display strings.
7. Nonunit module test: replace one generator in a throwaway copy with a
   same-order point whose `R_n` orbit is not free; the new annihilator/orbit
   certificate should fail before unit transport is trusted.

## Handoff: public R-module basis-transition prelaunch red team

### Claim or task

Pre-run review of the public certificate harness for explaining raw accepted
branch-label mismatches as public `R_n` basis transitions.

### Status

OPEN

### Assumptions

- Fixed public toy fixture only: `p=431`, trace `3`, source `[359,383]`,
  selected target `[70,86]`, degree `7`, seeds `20260720..20260722`.
- The serialized artifact point strings are interpreted in the deterministic
  local Sage field models recorded by the harness.
- Canonical map bodies identify the same public map body across artifacts.
- No authoritative certificate run was performed by this red-team review.

### Evidence so far

- Reviewed contract hash
  `2bafd1e6f0cd807338ab096f858374fe8e273255e863ac4818d01c1997c93f83`.
- Reviewed harness hash
  `d3bf3e1f0d083d0701b40a890df33bf23a8253479aea75b1e32198758fb1e415`.
- Transport direction, unit matrix arithmetic, exact-order checks, full
  `R_n`-orbit checks, embedding aggregation, and scoped output limitations are
  structurally aligned with the contract.

### Failure modes

- A missing/nonunique unit or branch mismatch should produce `success=false`;
  it narrows the basis-transition hypothesis for this fixture.
- A field-model mismatch can create a local Sage reconstruction artifact rather
  than a portable public certificate.
- The preserved strict-failure artifact is now semantically certified, but only
  as evidence that raw branch equality failed while map-body equality and
  empty-target controls passed and branch tables matched the primary artifacts;
  it is not evidence for a new isogeny.

### Next concrete action

Run the authoritative certificate once against the reviewed hashes, then inspect
`assertions`, all seed certificates, all embedding lanes, all unit certificates,
and controls before accepting only the scoped `TOY-EVIDENCE / MODEL-BOUND`
claim.

### Artifact paths

- `experiments/ecdlp_isogeny/iso_public_basis_transition_contract.md`
- `experiments/ecdlp_isogeny/iso_public_basis_transition_certificate.sage.py`
- `research/ascending_isogeny_basis_transition_design.md`
- `research/red_team_public_basis_transition_prelaunch.md`
