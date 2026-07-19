# Literature anchors and claim boundary

This is an orientation set, not a novelty claim. It supports only
`RQ-RHO-001` and `H-RHO-001`.

1. Victor Shoup, *Lower Bounds for Discrete Logarithms and Related Problems*,
   EUROCRYPT 1997, DOI
   [10.1007/3-540-69053-0_18](https://doi.org/10.1007/3-540-69053-0_18).
   It gives an Omega(sqrt(p)) lower bound in the generic group model. This lane
   therefore makes no exponent claim; the result is not a lower bound for all
   structure-exploiting ECDLP methods.

2. Edlyn Teske, *On Random Walks for Pollard's Rho Method*, Mathematics of
   Computation 70 (2001), DOI
   [10.1090/S0025-5718-00-01213-8](https://doi.org/10.1090/S0025-5718-00-01213-8).
   It is the direct r-adding-walk anchor. Here r choice and partition behavior
   are a matched quality control, not a new algebraic mechanism.

3. Jeong Han Kim, Ravi Montenegro, Yuval Peres, and Prasad Tetali,
   [*A Birthday Paradox for Markov chains with an optimal bound for collision in
   the Pollard Rho algorithm for discrete logarithm*](https://arxiv.org/abs/0712.0220).
   This motivates measuring collision quality under stated partition/oracle
   assumptions rather than treating walk samples as automatically independent.

4. Iwan Duursma, Pierrick Gaudry, and François Morain, *Speeding up the
   discrete log computation on curves with automorphisms*, ASIACRYPT 1999, DOI
   [10.1007/978-3-540-48000-6_10](https://doi.org/10.1007/978-3-540-48000-6_10).
   Fixed-order automorphism folding is a known special-structure constant factor
   and is excluded from the candidate arm.

## Local design constraints

- `inputs/h100_session/h040_rho_const.json` is the existing toy numerical
  collision-constant baseline, not a cryptographic-scale performance result.
- `inputs/h100_session/h039_walk_corr.json` reports significant long-lag cells
  in one serial r=20 probe, so the new protocol requires an independent quality
  check.
- `inputs/h100_session/h041_xonly_walk.json` records short cycles and poor
  useful-collision fraction for a tested x-only construction; it is a negative
  control rather than evidence against every x-coordinate representation.

No cited source establishes the proposed 5% effect. It is a preregistered
decision gate; the hypothesis remains `CONJECTURE` / `HYPOTHESIS`,
`TOY-EVIDENCE`, `HEURISTIC`, `MODEL-BOUND`, and `novelty-unverified` until
controlled execution and independent review.
