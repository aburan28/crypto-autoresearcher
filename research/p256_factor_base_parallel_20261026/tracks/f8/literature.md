# F8 source review before implementation

26 October 2026. Reader: `/root/pass2_lattice_orbits`. No second-pass data has
been collected. The committed task is `TASK-20261026-7324bb`.

- **Retrieved and read:** [SEC 2 version 2.0](https://www.secg.org/sec2-v2.pdf),
  section 2.4.1: secp256k1's field, `a=0`, `b=7`, standard generator,
  subgroup order and cofactor. These are inherited published group facts;
  checking subgroup witnesses is not a regenerated point count.
- **Internal, read:** the immutable first-pass F8 report, source
  `orbit_matrix.py`, result and independent relations-and-bounds review.
  Its representatives `[i]G` and 96 additive rows are constructed positives.
  The projective automorphism argument and exact compression identity are
  elementary derivations, separate from a measured relation-generation law.
- **Retrieved source gap:** searched for Faugere--Gaudry--Huot--Renault,
  *Using Symmetries in the Index Calculus for Elliptic Curves Discrete
  Logarithm*, DOI [10.1007/s00145-013-9158-5](https://doi.org/10.1007/s00145-013-9158-5).
  Search located `hal-00700555v3` and ePrint `2012/199`; full-text fetches
  from ePrint and CiteSeer failed with 403, and the guessed author PDF was
  inaccessible. No theorem or improvement from that unread paper is used.
  The search abstract concerns extension-field decomposition and does not
  establish a prime-field improvement for this implementation.
- **Internal, read:** `AGENTS.md`, literature-first and observation rules,
  `audit-curve`, `experiment-protocol`, and second-pass execution gates.

The fixed public fixture sampler hashes `(seed, domain, counter)` to an
abscissa and retains every rejected lift/collision. No scalar labels are
computed or supplied. This is a declared deterministic fixture generator;
it is not an RFC hash-to-curve implementation and no uniform-point sampling
or unknown-log hardness theorem is claimed.

Every nonzero representative receives all six signed order-three images.
Both complete three-summand solvers use the same resulting point set; the
baseline gets the identical symmetry/compression map. Pure orbit identities
compress to zero and add no independent relation on representative logs.
All target-query outputs, including empty sets, are finite-domain exact
observations only. A separately constructed target and the historical
constructed matrices are detector/regression controls, not natural yield.
