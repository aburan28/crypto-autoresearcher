# Mathematical implementation note — `TASK-20260907-aa1985`

This note describes the definitions implemented in `driver.py`. It is an
implementation aid for the required independent mathematical review; it is not
a certificate that a selected scientific fixture has passed the definitions.
No fixture, search, map evaluation, control, or timing measurement was run by
this task.

## Source boundary and provenance

The binding source is the frozen `experiments/EXP-ECDLP-1b1b99/specification.yaml`, SHA-256 `b331940a2f5215058d84845f953365c39dac78b4a0d4894604e90b06bc2f3fff`, with additive approval `DEC-20260906-f73475` and implementation authorization `DEC-20260907-b21c85`. The precise inputs used below are the frozen source's `inputs`, `algorithms`, and `controls` fields (**internal provenance**). The odd-degree Vélu formulas were audited against the compatible local helper `harness/isogeny_class.py:velu_odd/velu_image` (**internal provenance**), but this package independently implements them and does not take that helper's existence as validation.

The CM assertion that a degree-three vertical quotient from the maximal `Z[i]` order is a conductor-three floor when `3` is inert is an **unverified mathematical assumption of this implementation**, copied from the frozen specification. The driver records the discriminant arithmetic and rejects an absent certificate; independent mathematical review must establish the order theory and exceptional-j treatment before any measurement.

## Curves, kernels, and normalized Vélu maps

All curves use `E: y²=x³+Ax+B` over `F_p`, with `p>3`. `full_rational_three_torsion` enumerates every affine field point and requires exactly eight nonzero points killed by `[3]`. It pairs `K` with `-K`, creates four distinct cyclic kernels `{O,K,-K}`, and sorts them by the degree-two kernel polynomial `(x-x_K)²=x²-2x_K x+x_K²`. A curve with only one rational three-kernel is rejected as not satisfying the frozen *full* `E0[3]` condition; `rational_three_kernels` is intentionally separate and is used only while finding a dual on a quotient.

For a representative `Q=(x_Q,y_Q)` of an order-three kernel, the code sets `g_Q=3x_Q²+A`, `h_Q=-2y_Q`, `v_Q=2g_Q`, and `u_Q=h_Q²`. The normalized codomain is

`A'=A-5v_Q`, `B'=B-7(u_Q+x_Qv_Q)`,

and the map is

`x'=x+v_Q/(x-x_Q)+u_Q/(x-x_Q)²`,

`y'=y-2u_Qy/(x-x_Q)³-v_Qy/(x-x_Q)²`.

The point at infinity maps to infinity and nonzero kernel points map to infinity. The code immediately checks that every non-kernel image satisfies the codomain equation. This is a runtime integrity check, not a theorem proof.

## Exact dual and model normalization

For each of the four `φ_j:E0→E_j`, `exact_dual` enumerates rational order-three kernels on `E_j`, builds a normalized Vélu candidate `E_j→E''`, and searches explicitly for a short-Weierstrass isomorphism `ι_u:E''→E0`, `(x,y)↦(u²x,u³y)`, where `A0=A''u⁴` and `B0=B''u⁶`. It accepts exactly one candidate for which `ψ_j∘φ_j(P)=[3]P` holds on a supplied non-kernel certificate point. The future composition control must repeat this on `G0`, `G_j`, and the 128 frozen public scalars; a single witness only selects the candidate and never replaces those controls. The reverse identity `φ_j∘ψ_j=[3]` on `E_j` is a required reviewer/control joint and is not implied merely by the selected implementation path.

## Automorphism, eigenvalue, and the factor of three

For `E0:y²=x³-x`, choose the smaller field root `ι` of `ι²=-1`; the implemented automorphism is `i(x,y)=(-x,ιy)`, with `i²=[-1]`. The two roots of `λ²=-1 (mod r)` are enumerated. Both scalar products on `G0` are evaluated and the code requires exactly one satisfying `[λ]G0=i(G0)`. With `G_j=φ_j(G0)`, the implemented auxiliary operation is `β_j=φ_j∘i∘ψ_j=[3λ]` on `G_j`; it is compared to `m=3λ mod r`. The code has no division by three, and never labels this output `[λ]`. The deliberately wrong root is required to fail on a nonzero point in the future identity-transport control.

## Coordinate and level certificates

For `u∈{1,2,3}`, the coordinate model is `E^(u): y²=x³+(u⁴A)x+u⁶B`, with `C_u(x,y)=(u²x,u³y)`. Maps are conjugated as `C_target ∘ f ∘ C_source⁻¹`; no input is independently re-sampled for a coordinate arm.

`conductor3_certificate` records `Dπ=t²-4p=-4fπ²`, `v3(fπ)=1`, the inertness predicate `3 mod 4=3`, the four quotient models, and a rational-three-kernel count for each quotient. It refuses the frozen level label if the arithmetic or cardinality fails. The counts are a crosscheck with retained multiplicity, not a substitute for the independent order-theoretic proof.

## Review joints before launch

1. Re-derive the normalized Vélu formulas and both dual identities on the actual selected models.
2. Prove the conductor-three floor implication and resolve all special `j=1728`/rational-isogeny multiplicities for the selected fixtures.
3. Check `i`, eigenvalue-root sign selection, and `[3λ]` transport in the actual subgroup.
4. Check coordinate conjugation, scalar-label isolation, every frozen cost term, and that the future timing/control runner keeps all failed candidates and terminal classifications.
