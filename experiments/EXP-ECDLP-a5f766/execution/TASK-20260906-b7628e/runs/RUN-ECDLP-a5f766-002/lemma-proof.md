# Scoped etale-section lemma — proof record (RUN-ECDLP-a5f766-002)

Status: **UNRESOLVED** as a whole (see components). Nothing here is
self-certified; the independent review round audits this document.

## Setting

`R = k[eps]/eps^2`, `char(k) = p > 3`, smooth elliptic family
`E: y^2 = x^3 + (A0 + eps A1) x + (B0 + eps B1)` over `R` with `A0` and the
special-fiber discriminant invertible, and a section `P` with `[n]P = O` for
`n > 1` invertible in `k`.

## Part 1 — constant family: unique lift, zero coordinate response

Assume the family is constant (`A1 = B1 = 0`) and coordinates are fixed.

1. Reduction mod `eps` gives the exact sequence of groups
   `0 -> K -> E(R) -> E_0(k) -> 0` where the reduction kernel `K` consists of
   points congruent to `O`. In the formal group of `E_0` over the Artin ring
   `R`, `K` is identified, via the invariant differential, with
   `eps * Lie(E_0) ~ k` as a group (the formal group law truncated at order
   `eps^2` is additive: `(eps a) +_F (eps b) = eps (a + b)` because all
   higher terms carry `eps^2 = 0`).
2. `[n]` is a fixed group endomorphism of the constant family. Its
   differential at `O` is multiplication by `n` on `Lie(E_0)`, hence on `K`
   the map is `eps a -> eps (n a)`.
3. `n` is invertible in `k`, so `[n]|_K` is bijective; in particular
   injective. The only element of `K` killed by `[n]` is `0`.
4. Let `P0 in E_0(k)` with `[n]P0 = O`, and let `P~ in E(R)` be any lift with
   `[n]P~ = O`. Any two lifts differ by an element of `K`; write
   `P~ = P0 + eps D` in fixed coordinates. Then
   `[n]P~ = [n]P0 + eps (n D) = eps (n D)` (constancy of the family makes
   the first-order term of `[n]` at a torsion point pure translation by the
   differential; there is no family-variation term because `A1 = B1 = 0`).
   `[n]P~ = O` forces `n D = 0`, hence `D = 0`.
5. Conclusion: the lift is unique and its first-order coordinate response in
   the fixed constant coordinates is zero. This is where the constant-family
   premise enters: step 4 uses `A1 = B1 = 0`.

Status: complete elementary proof, written from the design.md-sanctioned
route (invertibility of the differential of `[n]` on the reduction kernel),
with the ambient-family and fixed-coordinate hypotheses explicit. Subject to
independent audit; not self-certified by the Executor.

## Part 2 — varying family: uniqueness does not force constant coordinates

Witness (machine-checked in symbolic group 5 and all 32 finite V rows):
`s = 5 + eps`, `A = 6 s - 27 = 3 + 6 eps`, `B = s^2 - 18 s + 54 = -11 - 8 eps`,
`P = (3, s)`. Certificates: `P` lies on `E` over `R`; the tangent `y = 3x + s - 9`
meets `E` with residual cubic `(x - 3)^3` mod `eps^2`, so `2P = -P` and
`[3]P = O` as a section; the special fiber is smooth (`3375` a unit on the
panel) and `3` is invertible, so `P` is a smooth nonidentity order-3 section.
Yet `J = 2 x0 x1 / A0 - x0^2 A1 / A0^2 = -6 != 0` on the panel, and the raw
`y` derivative is `1`.

Therefore any argument claiming that etale-section uniqueness forces zero
coordinate derivatives in a varying Weierstrass model is refuted by explicit
controlled witness: the blanket zero-derivative rule is the known-false
object, and it fails here as designed. The gauge-invariant jet law is
preserved throughout (`J' = J` under the active gauge; `J -> c J` under
pullback), so the nonzero jet is coordinate response of a varying family,
not gauge motion.

## IDEA-109 reconciliation — DEFERRED (by design)

design.md: "A nonzero varying-family coordinate jet does not, by itself,
contradict that expectation or provide a displacement observable. The later
proof audit must make that precise without turning the expectation into a
proven universal closure." That reconciliation is a later proof-audit
deliverable and is NOT discharged in this run. Hence group 6 is recorded
UNRESOLVED overall; this is unresolved work, not a refutation and not a
FAIL of the recorded identities.
