# Implementation

The experiment uses dependency-free affine short-Weierstrass arithmetic. It deterministically selects a prime `p = 3 mod 4`, generates nonsingular ordinary curves, counts `#E(F_p)`, and accepts only instances with a prime subgroup `q >= p/16`. The generator is projected into that subgroup and verified by direct multiplication.

Every factor base is sign-complete and has the same even cardinality. The implementation compiles ordered two-sum and three-sum counters, measures additive energy and occupancy, then queries 128 shared held-out targets for five-term decompositions. Offline construction and online lookup counters are kept separate. Pollard rho runs on the same curves and affine implementation.

`verify_coordinate_energy.py` does not trust summary fields. It independently checks primality, curve order, subgroup membership, factor-base construction witnesses, pair/triple counters, five-term target counts, recovered witnesses, and rho outputs.

No Gröbner solver or hidden native dependency is used. Python object storage is reported as an implementation measurement, not a language-independent lower bound.
