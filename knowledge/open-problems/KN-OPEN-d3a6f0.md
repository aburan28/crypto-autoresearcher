---
id: KN-OPEN-d3a6f0
type: open_problem
title: "How fast does the maximal Fourier mass of p-adic digit characters of the torsion section s_tor decay with n, and does any digit beat the n^(-1/4) Fourier-learning breakeven?"
tags: [lifting, local-torsion, torsion-section, p-adic, digit-encoding, character-sum, fourier-learning, hidden-number, ecdlp, prime-field, open-problem, exponent]
confidence: reported
status: open
source_refs: [KN-OPEN-3417fc, KN-TECH-73630e, KN-TECH-06bb4e]
internal_refs: [EV-CZLIFT-764f54, DEC-20261023-2e7447, EXP-CZLIFT-1a3453, RUN-CZLIFT-037e5f, RUN-CZLIFT-d37ca4, VAL-20261022-55676f, RT-20261023-dcb217, H-CZLIFT-fba874, RQ-CZLIFT-b9f765]
added: 2026-10-23
superseded_by: null
---

## The question

Let `E/F_p` have a point `P` of prime order `n != p`. Let `s_tor : <P> -> E(Z_p)[n]`
be the prime-to-`p` torsion section on a fixed integral model, either the CM
canonical model or an arbitrary integer lift. Let `a_i(z)` be the `i`-th
`p`-adic digit of `z in Z_p`. For a digit index `i >= 1`, a coordinate
`c in {x, y}` and a nontrivial additive character `t in F_p^*`, put

```
g(k) = e( t * a_i(c(s_tor([k]P))) / p ),   k in Z/n,
Phi_i(n) = max_{t != 0} max_{j in Z/n} | (1/n) sum_{k in Z/n} g(k) e(-j k / n) |.
```

The sum runs over the full range. Even x-digit functions need it, because only
full-range sums are covariant under a change of generator.

- **Q1 (measurement).** What is the growth exponent of `Phi_i(n)` in `n`,
  for `i = 1..4`, over CM-canonical and arbitrary lifts? A uniform random
  model predicts about `sqrt(ln(p n) / n)`, which is exponent `-1/2`.
- **Q2 (proof).** Is there a Weil-type bound for the digit sums,
  `|sum_k g(k) chi(k)| = O(p^c n^(1/2) polylog)` for `i >= 1`?
  - For digit 0, subgroup-sum bounds give `O(sqrt p)` cancellation (with a
    log factor once twisted by `chi`): Lange-Shparlinski, as stated in
    Farashahi-Shparlinski arXiv:1005.4771 Lemma 5, and Kohel-Shparlinski
    ANTS-IV 2000. Status: reported.
  - For `i >= 1`, the digit function passes through `[p^i]`-type
    multiplication of a lift (a Greenberg transform), and its degree grows
    with `p`. No bound is known.
- **Q3 (consequence).** `s_tor` is a computable homomorphism, so `g` has exact
  shift-query access: `g(d + r)` is read from `s_tor(Q + [r]P)`. A heavy
  coefficient `tau = Phi_i(n)` then gives `chi_j(d)` from about `tau^-2`
  queries, and `d` by scaling `Q -> [u]Q`. This is the Fourier-learning
  mechanism of the hidden-number / hard-core lineage (Boneh-Venkatesan CRYPTO
  1996; Akavia-Goldwasser-Safra FOCS 2003).
  - Total cost: about `tau^-2 polylog(n)` evaluations of `s_tor`, at
    `O(log n)` group operations over `Z/p^(i+1)` each, plus the cost of
    locating the heavy coefficient.
  - Against rho (`sqrt(pi n / 4)` group operations), the breakeven is about
    `tau* = n^(-1/4)` up to polylog factors (order-of-magnitude estimate in
    RT-20261023-dcb217).
  - A family with `Phi_i(n) >= n^(-1/4 + delta)` and a locatable heavy
    coefficient would therefore be an exponent-level sub-rho attack. Before
    any exponent is claimed, the polynomial degree of the coefficient-location
    step in `1/tau` must be checked.

## Why it is not already answered

- `KN-TECH-73630e` covers only group-theoretic invariants. `s_tor` is a group
  isomorphism onto its image, and the formal logarithm vanishes on torsion, so
  any gain must come from the encoding.
- `KN-OPEN-3417fc` asks for an efficiently *invertible* coordinate functional.
  This entry asks a weaker, Fourier-level property, which suffices through
  learning, and names a concrete threshold. It sharpens `KN-OPEN-3417fc` and
  does not supersede it.
- EXP-CZLIFT-1a3453 (EV-CZLIFT-764f54, DEC-20261023-2e7447) measured only
  half-range single-pair correlation. It excludes `tau >= rho_min`, with
  `rho_min` in `[0.28, 0.98]`, on 42 toy records (`47 <= n <= 613`,
  `p <= 571`, digits 0..4, one generator per record), and the spectra are
  white at that floor. This is a toy-scale floor, by the red team's estimate
  about 50 bits of correlation from the attack regime. It is not evidence
  about the exponent.
- Whiteness is not independence. Digit 0 determines `k` up to sign and is
  still white. The question is computational, not information-theoretic.

## Falsification / resolution criteria

- **Resolved negatively (scoped)** by either of:
  - a measured exponent consistent with `-1/2` for each `i = 1..4` on stated
    families, up to a stated `n` (about 10^4 to 10^5 at toy tier). The
    measurement must use a symmetry-matched null (negation classes, and
    `mu_6` orbits on D = -3), drop `j = 0` from the spike count, report
    planted-leak power curves, and use several lifts per curve;
  - a proof of a Weil-type bound for digit `i`.
- **Resolved positively** by a digit and a family with a replicated
  `Phi_i(n) >= n^(-1/4 + delta)`, a locatable heavy coefficient, and a charged
  end-to-end cost below rho and BSGS. Independent replication and a red team
  are required before any claim.

Neither outcome is a statement about deployed curves.

## Status

`OPEN`. A toy floor only (EXP-CZLIFT-1a3453). The successor work is named in
DEC-20261023-2e7447 NA-4 (measurement) and NA-6 (Weil-type bound, a
candidate). Citations are as checked by RT-20261023-dcb217; the coordinator
did not re-read them.
