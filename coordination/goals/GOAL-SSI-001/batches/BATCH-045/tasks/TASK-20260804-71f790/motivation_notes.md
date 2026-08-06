# Motivation Notes: Transcript-Leakage Lane After EXP-SSI-S1

**Task:** TASK-20260804-71f790 (GOAL-SSI-001 / BATCH-045 / Lane C)
**Motivated by:** EXP-SSI-S1 clean negative (EV-SSI-17c854)

---

## Summary

**Recommendation: PAUSE the transcript-leakage lane.** One low-cost CRT
independence test is proposed as a final check before pausing. The fundamental
obstruction is the model, not the statistic.

---

## Analysis of the EXP-SSI-S1 negative

### What the experiment proved

EXP-SSI-S1 established that the chi-squared goodness-of-fit statistic on
kernel-scalar residues mod 7 does NOT distinguish KLPT-generated transcripts from
uniform at p=6143. Specifically:

- The **pool** of all 688 norm-D quaternion elements has near-uniform s mod 7
  distribution: counts {0:88, 1:80, 2:88, 3:88, 4:88, 5:88, 6:80}, chi2=1.07,
  p=0.983.
- Key-dependent **Gaussian weighting** of this near-uniform pool produces
  near-uniform marginals (all p-values > 0.014 across 15 per-key tests; none
  reject at corrected alpha=0.0002).
- Mutual information I(residue; key) is near zero (0.007 bits across all runs).

### Why the negative is structural, not a power issue

The negative is not merely a failure to reach significance. It has a structural
explanation:

1. The pool itself is near-uniform (chi2=1.07 on 7 bins across 600 finite values).
2. Gaussian weighting with sigma = diameter/3 spreads mass across ~400 of the 688
   elements. Any weighted average of a near-uniform pool remains near-uniform.
3. The ONLY way to produce detectable bias from a near-uniform pool is to
   **concentrate** on a very small subset that happens to have non-uniform residues.
   The Gaussian model doesn't do this (it concentrates gradually, not sharply).

### Why scaling up chi2_7 or changing modulus (mod-11, mod-13) won't help

The same argument applies to ANY single-residue projection:

- For any small prime q coprime to D and p, the norm-D elements equidistribute
  well modulo q. This follows from the representation theory of quadratic forms
  modulo primes (Siegel mass formula, local densities).
- The counts will be approximately 688/q per residue for any q, with O(sqrt(688/q))
  fluctuations.
- Gaussian weighting from this equidistributed pool cannot create detectable
  marginal bias at any q.

Scaling up sample size (n > 400 per key) improves power against CONCENTRATED bias,
but the effect to be detected (Gaussian-weighted sampling from a near-uniform pool)
has essentially zero effect size, not merely small effect size.

---

## Candidate statistics evaluated

### Candidate 1: CRT independence (s mod 7, s mod 11) -- PROPOSED as final check

**Mechanism:** The norm constraint Nrd(gamma) = D creates an algebraic variety in
Z^4. The projections s mod 7 and s mod 11 are rational functions on this variety.
Independence of these projections requires that the variety's image in
P^1(F_7) x P^1(F_11) factorizes as a product. This is a non-trivial claim about
the specific quadratic form.

**Why chi2_7 would miss it:** Chi2_7 tests only the marginal P(s mod 7). The joint
distribution P(s mod 7, s mod 11) could be non-product even when both marginals are
uniform.

**Expected outcome:** NEGATIVE. The Hasse-Minkowski local-global principle and
Siegel's mass formula predict that integral quadratic forms equidistribute well over
Z/NZ for squarefree N. The pool's joint distribution is predicted to be
near-product.

**Value if negative:** Confirms that the pool structure is well-equidistributed at
all tested levels, and the lane should be paused.

**Value if positive:** Would indicate the norm variety has non-trivial P^1 x P^1
structure at (7,11), suggesting a previously-unnoticed algebraic constraint. Would
require replication and careful analysis of whether the non-independence is a pool
property or a key-dependent amplification.

**Cost:** Low (~30 min implementation, ~2 min compute). The rho_11 representation is
derived from the same quaternion algebra machinery already implemented.

### Candidate 2: Sequential correlations -- NOT PROPOSED (model limitation)

**Mechanism:** If the same key generates multiple transcripts, successive KLPT
outputs s_1, s_2, ... might be correlated because lattice reduction from nearby
starting points produces nearby outputs.

**Why not proposed:** The current model treats each sample as INDEPENDENT (drawn
from the weighted distribution with replacement). Sequential correlations would
require modeling KLPT's lattice-reduction trajectory, which the Gaussian model
explicitly does NOT capture. This test would give automatic negatives against the
current model without providing any information.

**What would make this testable:** A model where successive transcripts use
SEQUENTIAL commitment ideals (e.g., derived from a random walk on the isogeny
graph) and the KLPT lattice-reduction state carries forward between calls.

### Candidate 3: Lattice autocorrelation -- NOT PROPOSED (reduces to Candidate 2)

**Mechanism:** The 688-element set has specific pairwise-distance structure. KLPT
concentration might sample pairs that are closer than random.

**Why not proposed:** Under independent sampling (current model), pairwise distances
between samples are determined by the weight distribution, not by KLPT-specific
structure. This reduces to asking whether Gaussian weights concentrate on close
elements, which is a property of the Gaussian (smooth, well-understood) not a
testable KLPT property.

### Candidate 4: Conditional P(s | j(E_1)) -- NOT PROPOSED (requires model upgrade)

**Mechanism:** The commitment curve E_1 determines a connecting ideal. KLPT operates
within this ideal, accessing only a SUBSET of the 688 norm-D elements. The per-ideal
subset might have non-uniform residue distribution.

**Why this is the MOST theoretically motivated but NOT implementable:**
- Real KLPT doesn't sample from all 688 elements; it finds elements in a SPECIFIC
  left ideal I determined by End(E_A) and the commitment walk.
- The intersection of I (or its norm-D sublattice) with the maximal order could be
  a SMALL subset with non-uniform residues.
- The current model conflates "all 688 with Gaussian weights" with "ideal-specific
  subset." This is exactly the model limitation (DEV-1) the executor documented.

**What would make this testable:**
1. Compute the left ideal class set of the maximal order O at p=6143.
2. For each ideal class, enumerate the norm-D elements IN THAT CLASS.
3. Test whether per-class distributions are uniform.
4. This is a medium-difficulty research task (requires quaternion ideal arithmetic).

### Candidate 5: Lane should be paused -- RECOMMENDED

The clean negative is informative and well-controlled. It closes the specific
combination tested. But the MODEL cannot produce informative results beyond what
was already obtained, because:

- Near-uniform pool + smooth weighting = near-uniform marginals (proved by EXP-SSI-S1)
- This holds for ANY single modulus q and is predicted to hold for ANY joint distribution
- The ONLY escape is to model the ideal-class specificity of KLPT, which requires a
  model upgrade

---

## Obstruction diagnosis (inventor-protocol section 4 closure standard)

**Named obstruction:** The Gaussian-weighted all-pool model (DEV-1 + DEV-2) cannot
produce detectable transcript leakage because the pool equidistributes well in all
tested projections, and smooth weighting preserves equidistribution.

**Argument:** Let X be drawn from {gamma_1, ..., gamma_688} with smooth weights
w_i (sum = 1, max w_i / min w_i < 3 for sigma=diameter/3). For any function
f: S -> Z/qZ where the pre-images |f^{-1}(r)| are approximately equal for all r,
the distribution of f(X) is approximately uniform regardless of the weights. The
approximation improves with |S|/q and degrades with weight concentration. At |S|=688
and q=7 (ratio ~98), even extreme concentration on 10% of elements (69 elements,
~10 per residue) produces at most ~30% relative deviation per bin -- detectable only
with much larger n or much stronger concentration than the model provides.

**Forward guidance -- what remains open:**
1. Per-ideal-class distributions (Candidate 4) -- requires quaternion ideal arithmetic
2. Strong-approximation lattice-reduction bias (actual KLPT trajectory modeling)
3. Larger p where type-number > 1 creates genuinely distinct ideal-class families
4. Conditional tests P(s | public_data) where public_data constrains the ideal class

---

## Decision matrix

| Candidate | Theoretically motivated? | Testable with current model? | Expected outcome | Cost | Proposed? |
|-----------|:---:|:---:|:---:|:---:|:---:|
| CRT independence | Moderate | Yes | Negative (mass formula) | Low | YES (final check) |
| Sequential correlation | Moderate | No (ind. samples) | N/A | N/A | No |
| Lattice autocorrelation | Weak | Reduces to #2 | N/A | N/A | No |
| Conditional P(s\|E1) | Strong | No (model upgrade) | Unknown | Medium-High | No (future) |
| Pause lane | N/A | N/A | N/A | Zero | YES (recommended) |

---

## Implementation note for the CRT test (if approved)

The mod-11 representation rho_11: O -> M_2(Z/11Z) is derived from the same
quaternion algebra B(-1, -6143). The construction mirrors rho_7:

1. Compute sqrt(-p) mod 11: p = 6143, -p mod 11 = -6143 mod 11 = -(6143 mod 11) =
   -(558*11 + 5) = -5 mod 11 = 6 mod 11. Need sqrt(6) mod 11: 6 is not a QR mod 11
   (Legendre symbol (6/11) = -1). This means rho_11 does NOT split as two
   1-dimensional representations -- it is irreducible over F_11. The "kernel scalar"
   interpretation changes: we would need the full 2x2 matrix action on F_11^2 and
   extract the projective fixed point.

   **Correction:** If sqrt(-p) mod 11 doesn't exist, the representation rho_11 is
   IRREDUCIBLE over F_11. The matrix has no eigenvalues in F_11. There is no
   "kernel scalar mod 11" in the same sense as mod 7. The CRT test as formulated
   requires a modulus q where -p is a quadratic residue (so rho_q splits). For p=6143:
   -p mod q is a QR iff -6143 is a QR mod q.

   Checking: -6143 mod 7 = -6143 + 878*7 = -6143 + 6146 = 3. Is 3 a QR mod 7?
   3^3 = 27 = 6 mod 7 = -1 mod 7. So (3/7) = -1. But wait, the kernel scalar WAS
   computed mod 7... Let me re-examine.

   Actually, the representation rho_7 exists as a 2x2 matrix representation regardless
   of whether -p is a QR mod 7. The kernel scalar s is defined as the eigenvector
   direction of the matrix, which exists over F_7 iff the characteristic polynomial
   splits (iff the discriminant Tr^2 - 4*Nrd is a QR in F_7). Since Nrd=D=4 mod 7,
   the char poly is x^2 - Tr*x + 4. Discriminant = Tr^2 - 16 mod 7 = Tr^2 - 2 mod 7.
   This is element-dependent (depends on Tr of the specific gamma).

   **This means:** The kernel scalar mod q exists for a given gamma iff the char poly
   of rho_q(gamma) splits over F_q. For some elements it exists, for others it doesn't.
   The EXP-SSI-S1 implementation handles this via the "infinity" case (88 of 688
   elements have s = infinity mod 7, i.e., the fixed point is [1:0] in P^1(F_7), or
   equivalently M01 = 0).

   For the CRT test, we need a modulus q where MOST elements have a well-defined
   kernel scalar. The choice depends on local splitting behavior of the char poly.

   **Revised proposal:** Instead of s mod 11, use a DIFFERENT algebraic invariant
   mod 11 -- specifically Tr(rho_11(gamma)) mod 11, which always exists (it's the
   trace of the matrix, a LINEAR function of coordinates). The joint test becomes
   (s mod 7, Tr mod 11).

   Actually, let me simplify. The cleanest test is: (s mod 7, norm_part mod 11) where
   norm_part = g(a,c) mod 11 (one half of the norm decomposition). This is always
   well-defined and algebraically constrained (g(a,c) + g(b,d) = D, so g(a,c) mod 11
   determines g(b,d) mod 11). The question is whether P(s mod 7 | g(a,c) mod 11)
   varies across values of g(a,c) mod 11.

This subtlety is noted in the proposal as a refinement needed at implementation time.
The fundamental conclusion (pause recommended, one cheap test as final check) is
unchanged.
