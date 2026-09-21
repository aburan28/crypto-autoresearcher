# Analysis — Autolab prime-field: round015_exp031_torus_semaev

## Observation
inconclusive

Source excerpt / raw summary:

```
# EXP-031 — Torus-based Semaev Index Calculus (H-TS-001)

Round 15. Last genuinely-novel algebra lever in the named queue.
Toy-scale, model-bound. NO break claim, NO cryptographic-size claim.

## 1. Idea and expected null

Granger–Vercauteren algebraic-tori IC obtains LOW-degree summation relations
by decomposing inside an algebraic torus's MULTIPLICATIVE group law (which is
low-degree in a rational parametrization) instead of the EC chord–tangent law
(whose Semaev/Gröbner solving degree blows up as ~`4^(m-1)`).

EXPECTED NULL (stated up front): the torus does give a genuine LOW-degree
summation relation (the GV win), BUT it solves a finite-field DLP in
`F_{p^2}^*` that does NOT descend to the prime-field EC DLP, because the
torus connects to the EC group only via a pairing of embedding degree 2
(MOV/Frey–Rück), which a P-256-like curve is chosen to avoid. Predicted
verdict: FAILED for the EC target (low torus degree, wrong problem).

## 2. Torus construction and rational parametrization

- `T_2(F_p) = ker(Norm: F_{p^2}^* -> F_p^*)`, the norm-1 subgroup, order `p+1`.
- `F_{p^2} = F_p(s)` with `s^2 = d`, `d` a fixed non-square in `F_p`.
- Parametrization `psi: A^1 \ {±s} -> T_2`, `psi(t) = (t + s)/(t - s)`.
  Norm check: `N(psi(t)) = psi(t) * psi(t)^p = ((t+s)/(t-s))((t-s)/(t+s)) = 1`,
  so `psi(t) ∈ T_2` for every `t` with `t^2 ≠ d`. This is the standard
  degree-1 (birational) parametrization of the Pell conic / norm-1 torus.
- Group law in parameter coordinates (Pell/Chebyshev composition):
  `psi(t1)·psi(t2) = psi(t3)` with `t3 = (t1·t2 + d)/(t1 + t2)`.
  Equivalently a Möbius action with matrix `M(u) = [[u, d],[1, u]]`; the
  m-fold product is `∏ M(u_i)`, whose entries are per-variable degree 1.

## 3. Summation system and degree comparison

The m-fold torus summation (product) relation "decompose target `psi(T)` as
a product of factor-base elements `psi(u_1)…psi(u_m)`" is read off from
`∏_{i=1}^m M(u_i)` versus the target:
`rel1 = M[0,0] - T·M[1,0] = 0`, `rel2 = M[0,1] - T·M[1,1] = 0`.

| quantity | torus T_2 (this exp) | EC Semaev (baseline) |
```

## Comparison
Compared against Autolab's stated baseline (typically Pollard rho / VW / Wesolowski-class
isogeny cost, depending on topic). This import does not recompute those baselines inside
crypto-autoresearcher.

## Inference
`OBSERVATION` / `TOY-EVIDENCE` (or Autolab's original label if stronger, still not upgraded):
the Autolab package is now citeable as `EXP`+`RUN` evidence under the harness. Scientific
content remains bounded by Autolab's original scope and caveats.

## Limitation
- Not independently re-executed in this repository.
- Certificates were not re-verified; do not promote discrete-log / decomposition claims.
- Claim tier remains `toy` unless a later harness experiment re-runs with certificates.
