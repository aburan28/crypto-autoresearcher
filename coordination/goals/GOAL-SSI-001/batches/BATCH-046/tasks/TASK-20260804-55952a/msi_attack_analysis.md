# MSI Hecke-Eigendecomposition Attack: Rigorous Analysis

**Task**: TASK-20260804-55952a (GOAL-SSI-001/BATCH-046)  
**Date**: 2026-08-04  
**Verdict**: **ATTACK_FAILS**  
**Named obstruction**: Exponential lattice dimension barrier (dim ker(Pi_m) ~ p/6 >> poly(log p))

---

## Executive summary

The Hecke-eigendecomposition attack on MSI contains a correct algebraic skeleton
(Steps 1-5) but a fatal computational error in Step 6. The eigendecomposition IS
valid, the periods ARE computable, and the target IS uniquely short in its coset.
However, the lattice in which CVP must be solved has dimension Theta(p), which is
**exponential in the security parameter** log(p). The gap between ||gamma*|| and
lambda_1(ker Pi_m) is polynomial (~ p^{1/2}), but LLL/BKZ requires the gap to be
exponential in the lattice dimension (~ 2^{p/12}). The attack reduces MSI to CVP
in a high-dimensional structured lattice of equal or greater hardness.

---

## Detailed analysis of each step

### Question 1: Is Omega_i computable?

**Answer: YES.** No circularity here.

The periods Omega_i = <f_i, gamma_i> mod l^m are computable from the modular form
f_i alone:

1. **Classical periods**: For a normalized Hecke eigenform f_i in S_2(Gamma_0(pN)),
   the classical periods are:
   - Omega^+_{f_i} = Re(integral_0^{i*infty} f_i(z) dz) proportional to L(f_i, 1)
   - Omega^-_{f_i} = Im(integral_0^{i*infty} f_i(z) dz)
   
   These are computable from the Fourier expansion {a_n(f_i)} via the functional
   equation of L(f_i, s).

2. **l-adic periods (Coleman integration)**: The l-adic analogs are computable via
   overconvergent modular symbol methods (Pollack-Stevens algorithm). Given the
   Hecke eigenvalues {a_n(f_i)}, these compute Omega_{f_i,l} mod l^m in time
   polynomial in m and the level pN.

3. **The computation depends only on the level pN**: The eigenforms f_1, ..., f_d
   are deterministic functions of the level. They require no information about
   End(E), the orientation, or the target curve. Standard algorithms (Cremona,
   Stein, Sage/Magma modular symbols) compute them.

**Critical caveat**: The computation is polynomial in the LEVEL pN (i.e., linear in
p), not polynomial in log(p). This already signals the dimensional issue below.

### Question 2: Is the gap real?

**Answer: YES, but the gap is polynomial, not exponential.**

#### Dimension count

- dim S_2(Gamma_0(pN)) = g approximately pN/12 (for N = 1: approximately p/12)
- H_1(X_0(pN), cusps, Z) has rank approximately 2g + c - 1, where c = number of cusps
- Cuspidal homology H_1^cusp has rank 2g (by Eichler-Shimura)
- The period map Pi: Z^{2g} -> Z_l^g (restriction to holomorphic differentials) has
  kernel of rank g (the "anti-holomorphic" sublattice)
- The truncated map Pi_m: Z^{2g} -> (Z/l^m Z)^g has ker(Pi_m) of full rank 2g in
  Z^{2g}, with [Z^{2g} : ker(Pi_m)] = l^{mg} (assuming surjectivity)

#### Lattice parameters

Setting l^m approximately p^{1/3} (the minimum precision to determine gamma* of
norm p^{1/3}) and g = p/12:

**Gaussian heuristic for lambda_1(ker Pi_m)**:

    lambda_1 approximately sqrt(n / (2*pi*e)) * det^{1/n}

where n = 2g = p/6 and det = l^{mg}:

    det^{1/n} = (l^{mg})^{1/(2g)} = l^{m/2} = (p^{1/3})^{1/2} = p^{1/6}
    sqrt(n/(2*pi*e)) = sqrt(p/(12*pi*e)) approximately p^{1/2} / 6.1

    lambda_1(ker Pi_m) approximately (p^{1/2} / 6) * p^{1/6} = p^{2/3} / 6

**Target norm** (gamma* as isogeny path of length p^{1/3}):

In the Manin-symbol basis, gamma* = sum of approximately p^{1/3} terms with
coefficients in {-1, 0, +1}:

    ||gamma*||_2 approximately sqrt(p^{1/3}) = p^{1/6}

**Gap ratio**:

    lambda_1 / ||gamma*|| approximately (p^{2/3}/6) / p^{1/6} = p^{1/2} / 6

The gap IS real: gamma* is a factor of ~p^{1/2} shorter than the generic shortest
vector in its coset. This confirms uniqueness: gamma* is (with overwhelming
probability) the UNIQUE shortest vector in the fiber Pi_m^{-1}(y).

#### But the gap is the wrong kind

The gap p^{1/2} is **polynomial** in p. In terms of the lattice dimension
n = p/6, this gap is:

    p^{1/2} = (6n)^{1/2} approximately sqrt(n)

A gap of sqrt(n) in dimension n is NEGLIGIBLE for lattice algorithms. The relevant
threshold is 2^{n/2} for LLL and beta^{n/(2*beta)} for BKZ-beta.

### Question 3: Does LLL/Babai exploit the gap?

**Answer: NO. The gap is exponentially too small.**

#### LLL threshold

LLL finds a vector within factor 2^{n/2} of the shortest, where n is the lattice
dimension. For our CVP instance:

- Dimension: n = 2g = p/6
- LLL approximation factor: 2^{p/12}
- Required: gap >= 2^{p/12}
- Achieved: gap = p^{1/2} = 2^{(log_2 p)/2}
- Deficit: 2^{(log p)/2} vs 2^{p/12}

For p >= 100 (let alone cryptographic p approximately 2^256): (log p)/2 << p/12.

**LLL cannot exploit this gap.** It fails by an exponential factor.

#### BKZ-beta threshold

BKZ with block size beta gives approximation factor beta^{n/(2*beta)}. Setting:

    beta^{p/(12*beta)} = p^{1/2}
    
    (p/(12*beta)) * log beta = (1/2) * log p
    
    beta / log(beta) approximately p / (6 * log p)
    
    => beta approximately p / (6 * log p)

Cost of BKZ-beta: 2^{Omega(beta)} = 2^{Omega(p / log p)}

This is **exponential in p/log(p)** -- comparable to (or worse than) the original
isogeny problem's complexity of p^{1/3} = 2^{(log p)/3}.

#### Babai's nearest-plane algorithm

Babai with an LLL-reduced basis: approximation factor 2^{n/2}. Same failure as
LLL. With BKZ-beta reduced basis: factor beta^{n/(2*beta)}, same cost analysis.

#### Exact SVP/CVP algorithms

The exact algorithms (sieving, enumeration) in dimension n:
- Sieving: 2^{0.292n} = 2^{0.292 * p/6} = 2^{0.049p}
- Enumeration: 2^{O(n log n)} = 2^{O((p/6) log(p/6))}

Both are **exponential in p** -- worse than the original p^{1/3+o(1)} algorithm.

### Question 4: The circularity check

**Answer: The periods and matrix are computable without End(E), but the computation
itself takes exponential time (poly(p), which is exp(log p)).**

| Object | Computable without End(E)? | Cost |
|--------|---------------------------|------|
| Eigenforms f_1, ..., f_g | YES (from level pN alone) | poly(p) |
| Eigenvalues a_l(f_i) | YES | poly(p) |
| l-adic periods Omega_i mod l^m | YES (Pollack-Stevens) | poly(p, m) |
| Period matrix A_{ij} = <f_i, e_j> | YES (modular symbol computation) | O(g^2) = O(p^2) |
| Coefficients c_i = y_i / Omega_i | YES (given y) | O(g) = O(p) |

**No circularity in the algebraic setup.** The obstruction is purely computational:
all these objects live in a space of dimension p, and manipulating them takes
time polynomial in p (= exponential in the security parameter log p).

The only way to make the computation poly(log p) would be to avoid the full
eigendecomposition. But:
- Using k << g eigenforms gives dimension 2g - k approximately 2g for the kernel,
  making lambda_1 SMALLER and the problem HARDER
- The Hecke operators act on p-dimensional spaces; there is no known O(log p)
  representation of their action on individual modular symbols

---

## The precise obstruction (structural theorem)

**Theorem (informal)**: The Hecke-eigendecomposition attack on MSI reduces the
problem to CVP in a lattice of dimension Theta(p) with a polynomial gap. This is
at least as hard as the original isogeny problem.

**Proof sketch**:

1. The modular-symbol lattice has rank 2g = Theta(p) (from the Riemann-Hurwitz
   formula for genus(X_0(p)) = floor((p-13)/12) + corrections).

2. The CVP instance has:
   - Dimension n = 2g approximately p/6
   - Gap ratio approximately p^{1/2} = n^{1/2}
   - This is a "polynomial gap" CVP instance in high dimension

3. No algorithm solves polynomial-gap CVP in dimension n faster than 2^{Omega(n^c)}
   for some c > 0 (under standard lattice assumptions). With n = p/6, this gives
   cost 2^{Omega(p^c)}.

4. The original isogeny problem is solvable in p^{1/3+o(1)} = 2^{(1/3+o(1)) log p}.
   Since (1/3) log p << p^c for any c > 0, the lattice approach is STRICTLY HARDER.

---

## Why Step 6 of the original argument is wrong

The original argument claims:
> "If the gap ratio lambda_1(ker A) / ||gamma*|| >= 2^{(p/12)/2}..."

This is FALSE. The gap ratio is:
- lambda_1 / ||gamma*|| approximately p^{2/3} / p^{1/6} = p^{1/2}
- NOT 2^{p/24}

The error conflates:
- The NORM ratio (p^{2/3} / p^{1/6} = p^{1/2} approximately sqrt(n)) with
- The REQUIRED gap for LLL (2^{n/2} = 2^{p/12})

The norm ratio is polynomial; the required gap is exponential in the dimension.
These differ by a factor of 2^{p/12} / p^{1/2} -- an exponential discrepancy.

The original argument also states "sqrt(p/12) / log(p) is superpolynomial" as if
this were relevant to the LLL threshold. Even if the ratio were superpolynomial,
LLL requires it to be 2^{Omega(n)} where n = p/6. A superpolynomial gap in p
(like p^{100}) would still be sub-exponential in n = p/6.

---

## Could Hecke structure make CVP easier?

The lattice ker(Pi_m) is not random -- it is Hecke-equivariant: for every prime q
coprime to pN, the Hecke operator T_q preserves ker(Pi_m) (acting with eigenvalue
a_q(f_i) on the f_i-eigenspace). This is analogous to the "ring structure" in
ideal lattices.

Known results on structured CVP:
- Ideal lattices in cyclotomic fields: current best attacks essentially match
  generic lattice algorithms (no known polynomial-time CVP exploiting ring
  structure at cryptographic dimension)
- Module lattices: same situation (KN-TECH-046, KN-LIT-116)
- The Hecke algebra is more complex than a number ring (it's a product of number
  fields K_{f_i}, one per Galois orbit of eigenforms), but its CVP status is
  likely no better

**Assessment**: There is no known evidence that Hecke-equivariance makes CVP
tractable. The analogy to ring/module lattice attacks, where decades of work have
not found fundamental advantages over generic attacks, suggests this is unlikely.

---

## The representation barrier (meta-observation)

The fundamental issue is a **dimension blow-up**:

| Representation | Dimension | Problem |
|---------------|-----------|---------|
| Isogeny path (original) | O(log p) bits input | Path-finding in exp(log p)-vertex graph |
| Quaternion lattice | rank 4 over Z | Short vector of norm p^{1/3} |
| Modular-symbol lattice | rank p/6 over Z | CVP in dim p/6 |

The MSI embedding takes a compact problem (finding a short element in a rank-4
lattice) and inflates it to a high-dimensional lattice problem (CVP in rank p/6).
This inflation CANNOT help: the information about gamma* is spread across p/6
coordinates, making it harder (not easier) to locate.

Compare with the successful direction in lattice cryptanalysis: the LWE-to-uSVP
reduction WORKS because it embeds a SECRET of dimension n into a lattice of
dimension O(n) with an exponential gap (the error is exp(n) shorter than lambda_1).
In MSI, the "secret" gamma* has dimension p/6 and the gap is only POLYNOMIAL in
that dimension. The embedding is in the wrong regime.

---

## Partial results and residual value

Despite the attack's failure, the analysis establishes:

1. **The period map is information-theoretically sufficient**: Pi_m(gamma) with
   m = O(log_l(p)) uniquely determines gamma* among short classes. The data
   CONTAINS the answer; extracting it is the hard part.

2. **Eigendecomposition reduces d independent 1D problems**: Each coordinate
   c_i = y_i / Omega_i is independently recoverable. The difficulty is ENTIRELY
   in the reconstruction step (assembling gamma from its eigenspace projections).

3. **The reconstruction is exactly CVP**: This gives a clean complexity-theoretic
   characterization of MSI: it is at least as hard as CVP in Hecke-equivariant
   lattices of dimension p/6.

4. **Lower bound on MSI**: The reduction shows MSI is at least as hard as CVP in
   dimension p/6 with polynomial gap. Under standard lattice hardness assumptions,
   this gives MSI is at least 2^{Omega(p^c)}-hard -- which is MUCH harder than the
   p^{1/3+o(1)} isogeny algorithm. This means MSI is NOT a useful attack channel:
   solving MSI is harder than solving the isogeny problem directly.

---

## Verdict: ATTACK_FAILS

**Primary obstruction**: Exponential lattice dimension. The reconstruction step
requires solving CVP in a lattice of dimension Theta(p), which is exponential in
the security parameter. No lattice algorithm (LLL, BKZ, sieving, enumeration)
solves this faster than 2^{Omega(p^c)}, which exceeds the p^{1/3+o(1)} direct
method.

**Secondary obstruction**: Insufficient gap for polynomial-time lattice reduction.
The gap ratio (polynomial: ~p^{1/2}) falls exponentially short of the 2^{Omega(n)}
gap required for LLL/Babai to succeed in dimension n = p/6.

**Implication for GOAL-SSI-001**: The MSI direction does NOT offer a sub-p^{1/3}
path. In fact, MSI appears HARDER than direct isogeny computation. The
eigendecomposition provides a clean algebraic decomposition but inherits an
exponentially worse computational problem. This closes the MSI attack channel.

**What would change this**: A method to solve CVP in Hecke-equivariant lattices
in time subexponential in their dimension (exploiting the algebraic structure).
No such method is known or conjectured. The analogy to ideal/module lattices
(where structure has not yielded fundamental speedups despite decades of effort)
suggests this is unlikely.

---

## Falsification conditions for this analysis

1. If Hecke-equivariant CVP in dimension n is solvable in time 2^{o(n)}: reopen
2. If a COMPACT representation of the modular-symbol lattice exists (dimension
   O(log p) rather than O(p)): reopen
3. If the MSI problem has exploitable structure NOT captured by the CVP reduction
   (e.g., the Coleman integration has p-adic analytic structure that bypasses
   lattice methods): reopen
4. If the dimension count is wrong (e.g., MSI can be stated on a curve of genus
   O(polylog(p)) rather than O(p)): reopen

None of these appear plausible given current number theory.
