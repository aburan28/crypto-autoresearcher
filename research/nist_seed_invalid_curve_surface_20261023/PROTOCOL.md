# Does the selected coefficient change the invalid-curve surface?

Frozen 2026-10-23 UTC before this exact archive check. This is a conditional
implementation analysis, not an ordinary-group ECDLP claim or evidence about
the historical selection program.

## Inputs and theorem to check

Use the eleven omitted seed-level classes in
`research/nist_seed_skipped_curves_20261016/assessed.json`, SHA-256
`370e79ce0bff8f26bb437fe37d1756f3f8261a5c00e9062ba41cf70f272e8841`,
and eight published controls over the same four fields in `traits.json`,
SHA-256 `a1102bd487379d223581863fab731d6eb6957bf0e264b450f1c7b298279b0b67`.
Exclude P-384 and P-521 singletons from label comparison. Bind every row to
its EC1 UID, field prime `p`, and exact short-Weierstrass coefficients `a,b`.

For affine short-Weierstrass arithmetic on `E_b: y²=x³+ax+b`, addition of
distinct points uses `λ=(y₂−y₁)/(x₂−x₁)` and doubling uses
`λ=(3x₁²+a)/(2y₁)`, followed by `x₃=λ²−x₁−x₂`,
`y₃=λ(x₁−x₃)−y₁`. The formulas use `p,a` but not `b` provided points are
handled under the usual exceptional-case rules. Thus, if an implementation
skips the curve-equation validation and uses this formula family, any valid
input on another nonsingular `E_b'` with the same `p,a` is processed as a
point on `E_b'`, independent of configured `b`.

Check that all 19 rows have `a = p−3 (mod p)`, `b != 0`, and one exact `p` per
field. Then construct the universal candidate `b'=0`, `Q=(0,0)` for each
row. Confirm `E_0` is nonsingular, `Q` lies on `E_0`, has order two, and is
off the configured `E_b`. Record the exact per-row results. Use an independent
small-field control at `p=101,a=-3,b=1,2,b'=0`: show both configurations
reject `Q` by curve-equation validation while b-independent scalar arithmetic
maps `[1]Q=Q`, `[2]Q=O`, `[3]Q=Q`. An off-curve point on a nonsingular
third `b'` with nonzero y checks ordinary addition as a second control.

## Outcomes and boundaries

If any archived row differs in `p,a` within its claimed field or has `b=0`,
stop the universal conclusion and report the exact exception. If every row
passes, conclude only that this *unvalidated affine-formula model* has a
shared invalid-curve family and a shared order-two witness, so selecting
one of these `b` values cannot eliminate that model's exposure. This does
not cover implementations using b-dependent complete formulas, explicit
validation, cofactor handling, x-only ladders, fault models, fixed-base-only
operations, or protocols with no observable secret-dependent result. An
order-two witness alone is not a full key-recovery demonstration. The
historical program's behavior remains unknown.

Preserve the exact check code, source hashes, output, theorem derivation,
primary literature references, editable diagram, vector chart and inspected
PDF. Do not change prior sealed curve or factorization records.
