# ECC2K-130 methodological note (Stage 0)

This note is **methodological**, not a solve or attack claim.

## Same derivation at q=2, k=131

On ECC2K-130 the curve is defined over `F_2` (Koblitz), so the base-2
Frobenius is an endomorphism. The class group available to Pollard rho on the
prime-order subgroup is `<tau, [-1]>` of order `2*131 = 262`, with
`j = 1/b = 1 != 0` so `Aut(E) = Z/2` after the char-2 classification (Stage 1).

Matched rho under the corrected convention is
`sqrt(pi * l / (4 * 131))` with the 129-bit prime subgroup order `l`
(Bailey et al. / Certicom parameters). The Weil recursion from `t = -1`
reproduces `#E = 4l`.

## Why the 16-fold conflation cannot arise

The tempting `32k` figure on the ANSI `c2pnb*` rows comes from confusing the
`16k`-element Galois orbit of **curves** under `pi_2` with automorphisms of
**one** curve. On ECC2K-130 the curve is already over `F_2`, so that Galois
orbit of curves is trivial — the conflation has no place to start.

## Ceiling (C)

Any single-target decomposition line may charge at most the order-`131`
group on the Frobenius-aware side. Rho extracts `sqrt(131)` from that group;
index calculus may extract up to `131` (relations) / `131^2` (LA). This is
a ceiling statement, not a measured cost.

## Scope

No group walk, no break claim, no new attack cost is asserted here.
Deployed `c2pnb*` rows in this experiment remain arithmetic-only.
