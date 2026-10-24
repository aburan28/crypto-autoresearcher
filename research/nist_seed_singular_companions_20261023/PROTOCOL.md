# Frozen singular-companion audit

**Frozen before execution:** 2026-10-23 UTC. This is an exact algebraic audit, not a historical reconstruction or a deployed-protocol exploit.

## Question and fixed inputs

If scalar multiplication uses the usual short-Weierstrass formulas with `a=-3` and omits point-on-curve validation, can singular formula-compatible companions distinguish the eleven omitted candidate curves from the eight published same-field controls? Use the 19 seed-level classes and full EC1 UIDs in `research/nist_seed_skipped_curves_20261016/assessed.json` (SHA-256 `370e79ce0bff8f26bb437fe37d1756f3f8261a5c00e9062ba41cf70f272e8841`) and `traits.json` (SHA-256 `a1102bd487379d223581863fab731d6eb6957bf0e264b450f1c7b298279b0b67`). Include only published names `prime192v1`, `prime192v2`, `prime192v3`, `prime239v1`, `prime239v2`, `prime239v3`, `secp224r1`, and `prime256v1`.

## Checks fixed in advance

1. Verify exactly 11 omitted and 8 published UIDs, 4 fields, prime `p>3`, every `a=-3`, and every configured `b` nonsingular and different from `+2,-2`.
2. Derive the singular values by the discriminant equation `4a^3+27b'^2=0`: for `a=-3`, `b'^2=4`, so `b'=+2` or `-2`. Check the exact identities `x^3-3x+2=(x-1)^2(x+2)` and `x^3-3x-2=(x+1)^2(x-2)`.
3. For `b'=+2`, write `u=x-1`, obtaining `y^2=u^2(u+3)`; for `b'=-2`, write `u=x+1`, obtaining `y^2=u^2(u-3)`. Count smooth rational points by slope `s=y/u`: finite smooth points are in one-to-one correspondence with `s in F_p` such that `s^2 != c` for `c=3` or `-3`, plus the point at infinity. Hence order is `p-1` when `c` is a square and `p+1` otherwise. Check quadratic characters using Euler's criterion.
4. Independently verify each field prime and Legendre symbol in Sage. For small prime controls `p=101,103`, enumerate all smooth points and compare counts for both singular cubics. Require a negative control for a configured `b` that equals a singular value; the launcher must reject it as a nonsingular source.
5. Compare omitted and published rows **within each field**. A shared singular-companion family and its smooth-locus orders refute only a coefficient-specific split under this exact unvalidated-formula model. Do not infer an implementation attack without a real decoder, scalar path, key reuse, and observable output.

## Execution and records

`check.py` writes a new, write-once `runs/<UTC>/results.json`, one result per UID and field, command/environment/input/code hashes, and `complete.ok` only after every check passes. `verify.sage` writes separate write-once verification records bound to the first result hash. Any exception, missing case, failed control, or mismatch makes the result indeterminate. No randomized trials or time-cost claim. The run command is recorded verbatim in the output. The report, editable diagram, SVG graph, and PDF are produced after the run records and cite exact paths. This result changes no official hypothesis or goal status.
