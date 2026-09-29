# Curve-blindness of summation-polynomial index calculus

*What an elliptic curve can, and cannot, contribute to a factor base.*

Draft, 2026-09-29. Isogeny Labs.

> **Status.** A synthesis draft written on user instruction. It assembles
> results already recorded in this repository, adds one short proof
> (Proposition 5) and one encoding remark (Section 8), and states one
> conjecture. It is **not** a ledger record and claims nothing above the tiers
> of the records it cites. Every internal result is toy tier or derivation
> tier. Independent review is owed on Sections 5 and 8, and a novelty search
> is owed on every item in Section 9 before submission.

## Abstract

Index calculus for the elliptic-curve discrete logarithm problem (ECDLP)
through Semaev's summation polynomials has one input that finite-field index
calculus lacks: the curve. We ask how much of it the method can use. Across
three independent lines we find the same answer, a constant factor. First,
the summation cover is curve-blind: its Galois group is $(\mathbb Z/2)^{m-2}$
for every curve in every characteristic, its fibres split by an exact law that
depends on no curve invariant beyond the quadratic character of $f(x)$, and on
the factor-base locus they always split completely. Second, the mean relation
yield of any factor base of size $B$ is $\binom{B+m-1}{m}/N$, whatever the base
and whatever the curve. Third, every endomorphism acts on a prime-order group as
a scalar; we prove that a non-unit endomorphism of norm $n$ whose scalar has
order $h$ satisfies $n^h \ge (\sqrt N - 1)^2$. So cheap short orbits come only
from automorphisms and from inseparable maps. The Frobenius of a subfield model
attains the bound up to the cofactor. The symmetry a curve can lend a factor
base therefore has order at most $|\mathrm{Aut}(E)| \cdot n$ for a curve over
$\mathbb F_{q^n}$ with a model over $\mathbb F_q$. Toy measurements across
isogeny classes, special $j$-invariants, isogenous transports and structured
factor bases agree. We conclude that any subexponential behaviour of this
family must come from the solving degree of the descended polynomial system,
the field side of the problem, and we state that as a conjecture with its
evidence. A final section shows why "system size" barriers, unlike the three
above, are not encoding-invariant.

## 1. Introduction

For finite fields, index calculus is subexponential because smoothness is a
property the field supplies. For elliptic curves there is no smoothness, and
since Semaev (2004) the substitute has been decomposition: write a target point
as a sum of $m$ points from a factor base $\mathcal F$, detected by the
$(m+1)$-st summation polynomial. The literature then splits by field.

- **Extension fields $\mathbb F_{q^n}$** with a subfield factor base
  (Gaudry 2009, Diem 2011) are subexponential for suitable $(q, n)$.
- **Prime-degree binary fields** rest on first-fall-degree assumptions that
  are disputed (Petit–Quisquater 2012, Semaev 2015, Huang–Kosters–Yeo 2015,
  Galbraith–Gaudry 2016).
- **Prime fields** have no known method below Pollard rho.

Across all three, a recurring hope is that *special curves* help: small CM
discriminant, $j = 0$ or $1728$, GLV or GLS endomorphisms, Koblitz Frobenius,
rational torsion, a well-chosen curve in the isogeny class. The known gains
(Duursma–Gaudry–Morain 1999 and Wiener–Zuccherato 1998 for rho;
Faugère–Gaudry–Huot–Renault 2014 and Faugère–Huot–Joux–Renault–Vitse 2014 for
symmetrized summation polynomials; Galbraith–Granger–Merz–Petit 2020 for
Frobenius factor bases) are all constant factors. This paper asks whether that
is an accident of the constructions tried or a property of the method. It
argues for the second.

**The claim, informally.** In summation-polynomial index calculus with a
factor base defined on the $x$-line, the curve enters only through (i) the
group order, (ii) the field, and (iii) a symmetry group of order at most
$|\mathrm{Aut}(E)| \cdot n$. Everything else the method does is determined by
the field and the factor-base set. Sections 3 to 5 prove the parts that can be
proved. Section 6 collects the measurements. Section 7 states the conjecture
that closes the gap.

## 2. Where curve information could enter

Fix $E/K$, $K = \mathbb F_{q^n}$, a subgroup $G = \langle P \rangle$ of prime
order $N$ with $N \,\|\, \#E(K)$, and a target $Q = [k]P$. The pipeline is:

1. **Factor base.** $\mathcal F = \{R \in E(K) : x(R) \in \mathcal B\}$ for a
   set $\mathcal B \subset K$, usually an $\mathbb F_2$-subspace $V$ or a
   subfield.
2. **Relation search.** For random combinations $R = [a]P + [b]Q$, decide
   whether $S_{m+1}(x_1, \dots, x_m, x(R)) = 0$ has a solution with every
   $x_i \in \mathcal B$, typically by Weil descent and a Gröbner or SAT solver.
3. **Symmetry quotient.** Optionally identify factor-base elements related by
   a map $\sigma$ with $\sigma(\mathcal F) = \mathcal F$, which shrinks the
   unknown vector.
4. **Linear algebra** on the relation matrix modulo $N$.

A curve-specific advantage has to show up in one of four places: the fibre
arithmetic of step 2, the number of relations step 2 yields, the symmetry
group of step 3, or the algebra of the descended system in step 2. Sections
3, 4 and 5 treat the first three. The fourth is Section 7.

## 3. The summation cover is curve-blind

Let $\pi : E \to \mathbb P^1$ be the $x$-map, put $L = K(t_1, \dots, t_{m-1})$
and consider $S_m(t_1, \dots, t_{m-1}, T) \in L[T]$, of degree $2^{m-2}$ in $T$.

**Theorem 1** (`KN-FIND-a8990a`, independently corroborated by
`KN-FIND-6edecd`). *For every elliptic curve over every field, in every
characteristic including 2 and 3, the splitting field of $S_m$ over $L$ is the
function field of $E^{m-1}/\Delta$, where $\Delta$ is the diagonal inversion.
Hence*
$$\mathrm{Gal}(S_m / L) = (\mathbb Z/2)^{m-2},$$
*acting simply transitively on the roots, and arithmetic and geometric
monodromy coincide.*

The only inputs are that $\pi$ is a separable degree-2 Galois cover and that
inversion is not the identity. The whole content is that no signed sum
$\sum_{i \in S} \epsilon_i P_i$ lies in $E[2]$ generically, which holds because
the summation map $E^{m-1} \to E$ is a surjective homomorphism.

**Theorem 2** (exact factorization law, same source). *Over $\mathbb F_q$,
$q$ odd, for a good specialization $a \in \mathbb F_q^{m-1}$: if the fibres
$\pi^{-1}(a_i)$ are simultaneously rational or simultaneously irrational,
$S_m(a, T)$ splits into $2^{m-2}$ distinct linear factors; otherwise it is a
product of $2^{m-3}$ distinct irreducible quadratics. No other factorization
occurs.* The class counts are $S^k N^{n-k} + N^k S^{n-k}$ with $S, N$ the
numbers of split and inert fibres, and the trace of Frobenius cancels to first
order in the split density at every $m$.

**Corollary 3** (factor-base locus; `KN-FIND-c41ea9`, `EV-MONO-a0a89c` OBS-4
and OBS-5). *If every $a_i$ is the $x$-coordinate of a rational point, $S_m(a,
T)$ splits completely, with roots $x(\pm P_1 \pm \dots \pm P_{m-1})$.* The
reason is the group law, not monodromy: sums of rational points are rational.

**Consequence.** Any statistic of the form "factorization type" or "Frobenius
class of the summation fibre" is identically constant where relation search
operates. No curve has smaller monodromy (Theorem 1), so no exceptional family
of curves can carry a deviant relation rate through fibre arithmetic. This
closes the question of `KN-OPEN-009` by derivation.
`KN-FIND-6edecd` adds that a cross-curve null control for this cover cannot be
built at all, because $\mathbb F_p$ has a unique quadratic extension.

Verification: 16,737 good samples at $m = 3, 4, 5$ and 257,061 exhaustive
specializations, with 0 mismatches, over $p \le 1009$ on generic, $j = 0$,
$j = 1728$ and full-2-torsion curves; two null controls rejected at 86 and 51
percent (`EXP-SMON-e5cbe6`).

## 4. The mean yield is curve-blind and base-blind

**Theorem 4** (`KN-FIND-007`). *Let $G$ be any finite abelian group of order
$N$ and $\mathcal D \subset G \setminus \{0\}$ any set of $B$ elements. The
number of size-$m$ multisets from $\mathcal D$ summing to a uniformly random
target has mean exactly $\binom{B+m-1}{m}/N$.*

The proof is a double count: every multiset sums to exactly one target. Nothing
about $E$ enters except $N$, and nothing about $\mathcal D$ enters except $B$.
A structured factor base can therefore *redistribute* yield across targets:
coverage, multiplicity, rank. It cannot raise the mean. Measured over 144
cells at $N \approx 2^{14}$ to $2^{18}$, the deviation of the exact cell mean
from the formula was exactly 0 (`EXP-FB3-001`). Six pre-registered geometries
showed no advantage over random that grows with $N$ (`EV-FBG-001`).

## 5. The symmetry a curve can lend is bounded

### 5.1 Scalars

Every endomorphism of an ordinary $E$ commutes with Frobenius, so it is
defined over $K$ and preserves $G$ when $N \,\|\, \#E(K)$. Since $G$ is cyclic
of prime order, $\alpha|_G = [\lambda_\alpha]$ for a scalar
$\lambda_\alpha \in \mathbb Z/N$. Two consequences are already recorded.

- **Witness lattices gain nothing** (`KN-FIND-009`, `EV-ENDO-001`). Adding $r$
  endomorphisms to the lattice of $(a_0, \dots, a_r)$ with
  $\sum a_i \lambda_i \equiv k$ adds coordinates and no congruence. On $j = 0$
  the Vieta identity $1 + \lambda + \lambda^2 \equiv 0$ makes the minimum
  exactly 1, certified on $y^2 = x^3 + 7$ over a 32-bit prime (42 of 42 checks).
- **Endomorphism oracles are generic** (`KN-FIND-b7e091`, `KN-FIND-002`). An
  oracle returning $\alpha(X)$ is simulable in the generic group model with
  $O(1)$ overhead, so Shoup's $\Omega(\sqrt N)$ stands.

### 5.2 A cheap map cannot have a short orbit

An orbit quotient by a map $\sigma$ saves a factor of about the orbit length
in the factor base, and about its square root in rho. It needs $\sigma$ to be
cheap and its orbits on $G$ to be short. For endomorphisms these pull against
each other.

**Proposition 5** (norm–orbit inequality). *Let $E$ be ordinary, $G \subset
E(K)$ of prime order $N$ with $N \,\|\, \#E(K)$, and let $\alpha \in
\mathrm{End}(E)$ be a non-unit of norm $n = \deg \alpha$. If $\lambda_\alpha$
has multiplicative order $h$ in $(\mathbb Z/N)^\times$, then*
$$n^h \ge (\sqrt N - 1)^2, \qquad\text{so}\qquad n \ge N^{1/h}\,(1 - o(1)).$$

*Proof.* On $G$, $\alpha^h$ acts as $\lambda_\alpha^h = 1$, so
$G \subseteq \ker(\alpha^h - 1)$. Since $\alpha$ is not a unit, $\alpha^h$ has
norm $n^h > 1$ and $\alpha^h - 1 \ne 0$, so it is an isogeny whose degree is
at least its kernel size, hence at least $N$. In the imaginary quadratic order
$\mathrm{End}(E)$ the degree is the norm $|\cdot|^2$, and
$|\alpha^h - 1| \le |\alpha|^h + 1 = n^{h/2} + 1$. So
$(n^{h/2} + 1)^2 \ge N$. $\square$

The idea and a verification plan are in `IDEA-20260901-6b63a4` (proposed,
unrun). The proof above is four lines and elementary; it is stated here so a
reviewer can check it without the proposal.

**Reading.** Short orbits at small norm are forbidden. Three cases escape, and
they are exactly the known ones.

- **Units** ($n = 1$). $|\mathrm{Aut}(E)| \in \{2, 4, 6\}$ for ordinary curves,
  giving the classical $\sqrt{|\mathrm{Aut}|}$ rho speedup and at most
  $|\mathrm{Aut}|$ in a factor base.
- **Frobenius of a subfield model.** If $E$ has a model over $\mathbb F_q$ and
  $G \subset E(\mathbb F_{q^n})$, then $\pi_q$ has norm $q$ and orbit $h = n$,
  and $q^n \approx \#E(\mathbb F_{q^n}) = N \cdot \text{cofactor}$.
  **Frobenius attains the inequality up to the cofactor.** It is cheap despite
  its norm because it is purely inseparable: evaluating it is a $q$-th power.
- **Twisted Frobenius (GLS).** On a GLS curve over $\mathbb F_{p^2}$ the map
  $\psi = \phi \pi_p \phi^{-1}$ has norm $p$, is inseparable, and satisfies
  $\psi^2 = -1$ on the group, so $h = 4$ and the gain over negation is 2.

For a *separable* non-unit, a short orbit forces a norm near $N^{1/h}$. For a
256-bit $N$ and $h \le 6$ that is a norm of at least about $2^{42}$. We do not
prove a cost lower bound for evaluating such maps: a norm with smooth
factorisation can be evaluated as a chain of small isogenies. But the number of
elements of norm at most $X$ in $\mathrm{End}(E)$ is about $X/\sqrt{|D|}$, and
a scalar of order at most $h$ is hit with probability about $h/N$. So one
should not expect such an element below norm about $N\sqrt{|D|}/h$, where
evaluation is no cheaper than the discrete logarithm. This is a heuristic, and
`IDEA-20260904-742c48` proposes the measurement that would test it.

### 5.3 Frobenius on linear factor bases

**Theorem 6** (`KN-FIND-b9a41d`, strength strong, blind re-derivation). *For
$K = \mathbb F_{q^n}$ with $\gcd(q, n) = 1$ and the $q$-power Frobenius
$\sigma$, the $\sigma$-stable $\mathbb F_q$-subspaces $V \subseteq K$ are
exactly the submodules cut by divisors of $T^n - 1$. The orbit quotient on
$\mathcal F_V$ gains the mean orbit size $g \le n$, a constant factor.*

Its dimensions are sums of the degrees of irreducible factors of $T^n - 1$,
with spacing $\mathrm{ord}_n(q)$. At $q = 2$ this makes the prime degrees very
unequal:

| $n$ | curve | $\mathrm{ord}_n(2)$ | stable dimensions below $n$ |
|---|---|---|---|
| 131 | ECC2K-130 | 130 | 0, 1, 130 |
| 163 | K-163 | 162 | 0, 1, 162 |
| 233 | K-233 | 29 | 0, 1, 29, 30, 58, 59, ... in steps of 29 |
| 283 | K-283 | 94 | 0, 1, 94, 95, 188, 189 |
| 409 | K-409 | 204 | 0, 1, 204, 205 |

At $n = 131$ and $163$ the only faithful stable base has dimension $n - 1$ and
the quotient on it is a net loss of 57 to 122 bits for $m = 2, \dots, 5$ in
every cost model examined. At $n = 233$ it is available at dimension 59, the
natural size for $m = 4$, which is why K-233 is the one standard Koblitz curve
where the Frobenius quotient is free.

### 5.4 The bound

Putting 5.1 to 5.3 together: the maps a curve supplies that are cheap and have
short orbits on $G$ generate a group of order at most
$|\mathrm{Aut}(E)| \cdot n$, where $n$ is the degree of $K$ over the smallest
field carrying a model of $E$. With negation included, that is 2 for a generic
prime-field curve, 6 for $j = 0$, 4 for $j = 1728$, $2n$ for a Koblitz curve
over $\mathbb F_{2^n}$, and 4 for GLS. Every one is a constant, or at most
logarithmic in $N$ for Koblitz curves.

## 6. What the measurements say

The following are toy-tier measurements recorded in this repository. None is
an attack. Each tests a place where curve structure could have shown up, and
none found it.

| channel tested | object | result | record |
|---|---|---|---|
| isogeny class | 138 curves, $p = 4001$, $t = 30$, $D_0 = -59$ | Betti table, regularity, singular locus and elimination degree of the Semaev systems constant on the class **and** equally constant on a matched control outside it; the one varying feature equals the 2-torsion count on 276 of 276 curves | `EV-ICINV-343679` |
| isogenous neighbours | 2-, 3-, 5-isogenous curves | relation yields 0.0138, 0.0145, 0.0134 inside the control band 0.0145 ± 0.0004 | `EV-ISO-001` |
| model | Weierstrass against Edwards; interval, progression and random bases | no change in solving degree or cost exponent; total index-calculus exponent 2.05 against rho's 0.5 | `FINDING-PF-IC-001` |
| isogeny transport | preprocessing moved along degree-$\ell$ isogenies, $\ell = 3$ to 31 | transport loses at every degree, 1.5 to 21 times | `EV-ENDO-10109d`, `EXP-MTGT-952db3` |
| automorphism walk | $j = 0$ and $j = 1728$, $p = 100057$, 20 seeds | ratio to the $\sqrt{|\mathrm{Aut}|}$ ceiling 1.004 and 1.044 | `EV-ENDO-10109d` |
| endomorphism-invariant base | $\phi$-orbit-closed base on $j = 0$ | the claimed linear-algebra gain came from appended rows; removing them returns random-base behaviour | `EV-STR-003` |
| factor-base structure | small-$x$, random and subgroup bases, 12 to 32 bits | within 7 percent at equal size; exponents 0.99 to 1.01 exhaustive, $\max(h, m-h+1)/m$ with meet-in-the-middle | `src/crypto_autoresearcher/index_calculus/README.md` §1, §3, §5 |
| Frobenius orbits | 14 toy cells, $|\mathcal F_V|$ up to 4005 | orbit count exact on 14 of 14; gain $g \le n$ | `EV-FROB-d336b0` |
| orbit-union encoding | $n = 13$ to 23, CaDiCaL and WDSat | conflict ratio 1.02 to 1.47, never below 1 | `EV-FROB-b6e1e9` |

Two anomalies are open and are not evidence for curve dependence. A
within-class over-dispersion of relation counts sits under an untested sampler
confound (`CORR-20260807-d78e2f`). A deficit in the multiplicative order of the
GLV scalar is probably the elementary bound $|\lambda| \le \sqrt p + 1$
(`KN-OPEN-2c095b`).

## 7. The conjecture

Sections 3 to 5 leave one channel: the algebra of the descended system itself,
whose coefficients depend on the curve equation.

**Conjecture 7** (curve-blindness of the solving degree). *For fixed field,
factor-base set and arity, the solving degree of the Weil-descended
decomposition system is independent of the curve, up to the symmetry group of
Section 5.4 and the rational 2-torsion.*

Evidence for it is Section 6's first three rows, and one more: at $j = 0$ and
$j = 1728$ the Semaev $S_3$ support is smaller (9 and 10 monomials against 13)
without moving Gröbner time (ratios 0.988 to 1.011, `GOAL-ENDO-001`). Evidence
it still needs:

- a second isogeny class and a second prime, which `EV-ICINV-343679` names as
  its own cheapest next step;
- one binary-field instance, where the curve enters only through $a_6$.

**If Conjecture 7 holds**, the complexity of summation-polynomial index
calculus depends on $E$ only through $N$, $K$ and a group of order at most
$|\mathrm{Aut}(E)| \cdot n$. Any subexponential behaviour then has to come from
the first-fall-degree behaviour of the descended system, which is a property
of the field and the factor base. That is where the open binary-field question
already lives, and it is the right place to look.

**What would refute it:** two curves over the same field, with the same
factor-base set and arity, whose descended systems have different solving
degrees, with the difference not explained by torsion or automorphisms.

## 8. Remark: size barriers are not encoding-invariant

Theorems 1, 4 and 6 and Proposition 5 are statements about groups, covers and
counts. They do not depend on how the system is written. A different kind of
negative result says the descended system is too large to write down within
the rho budget. This repository recorded one (`EV-ICPERF-784b25`): on
standardised binary curves the expanded system $S_{m+1}(x_1, \dots, x_m, x_R)$
in the $m\ell$ bits of the $x_i$ has Boolean degree $m \min(m-1, \ell)$, 12 at
$m = 4$, and exceeds the per-decomposition budget by 6 to 41 bits up to
$n = 283$.

That barrier does not survive a change of encoding. With the symmetrized
system in auxiliary unknowns $e_k$ (Faugère–Perret–Petit–Renault 2012), the
measured Boolean degree is 2 at $m = 3$ and 4 at $m = 4$ on eleven of eleven
toy descents. With Semaev's (2015) chain of $S_3$ it is 3. Priced on the same
cells and budget, the barrier survives only at $n = 131$ and $163$, by 0.6 to
14 bits, and flips sign at $n = 233$, 239 and 283 by 8 to 37 bits
(`CORR-20260929-12a50e`, `analysis/symmetrized-anf-20260929/`).

The lesson is general. Auxiliary variables shrink any polynomial system
towards the size of the circuit that computes it, so a size barrier is a
statement about an encoding, not about the problem. A structural barrier, like
the ones above, is a statement about the problem.

## 9. What is new and what is known

| item | status | what to check before submission |
|---|---|---|
| Theorem 1, monodromy $(\mathbb Z/2)^{m-2}$ | possibly new as stated; irreducibility is Semaev 2004 | Diem 2011; function-field experts; FGHR 2014 studies a different group (on variables) |
| Theorem 2, exact factorization law | not found in the literature searched | same |
| Corollary 3 | the group-law observation is folklore | none; cite as folklore |
| Theorem 4, yield conservation | elementary double count; likely known informally | Galbraith–Gaudry 2016 survey |
| Proposition 5, norm–orbit inequality | elementary; not found stated | GLV 2001, Galbraith–Lin–Scott 2009, and Duursma–Gaudry–Morain 1999 |
| Theorem 6, stable-subspace lattice | the Frobenius factor bases are GGMP 2020; the lattice classification and the $n = 131, 163$ loss are this repository's | GGMP 2020 Lemma 3.3 states the gain as $n'$, not $g$; reconcile |
| Section 5.4 bound | synthesis | — |
| Conjecture 7 | new as a stated conjecture | — |
| Section 8 | the degree drop is FPPR 2012's; the per-curve table is new | — |

The paper's contribution, if it has one, is the synthesis: three independent
closures that meet at one statement, plus a clean line between structural and
encoding-dependent negative results.

## 10. Open problems

- **Non-linear Galois-invariant factor bases.** Is there a commutative group
  over $\mathbb F_2$ with a rational point of order 131 giving an invariant
  base at index-calculus size (`KN-OPEN-095df5`)? Theorem 6 covers only linear
  bases.
- **The cost half of Proposition 5.** Measure the cheapest non-unit
  endomorphism's evaluation cost, including smooth-norm chains
  (`IDEA-20260904-742c48`).
- **Torsion quotients over $\mathbb F_{p^5}$.** Does the rescaled 2-torsion
  quotient on ecGFp5 have ideal degree $2^{16}$ (`KN-OPEN-9b4a2b`)? It is the
  one torsion symmetry the Section 5.4 count does not already include.
- **Conjecture 7** at a second class, a second prime and a binary field.

## References

Internal records are cited by identifier and live in `ledger/` and
`knowledge/` of this repository.

- I. Duursma, P. Gaudry, F. Morain. Speeding up the discrete log computation
  on curves with automorphisms. ASIACRYPT 1999.
- M. Wiener, R. Zuccherato. Faster attacks on elliptic curve cryptosystems.
  SAC 1998.
- R. Gallant, R. Lambert, S. Vanstone. Faster point multiplication on elliptic
  curves with efficient endomorphisms. CRYPTO 2001.
- S. Galbraith, X. Lin, M. Scott. Endomorphisms for faster elliptic curve
  cryptography on a large class of curves. EUROCRYPT 2009.
- I. Semaev. Summation polynomials and the discrete logarithm problem on
  elliptic curves. IACR ePrint 2004/031.
- P. Gaudry. Index calculus for abelian varieties of small dimension and the
  elliptic curve discrete logarithm problem. J. Symbolic Comput. 2009.
- C. Diem. On the discrete logarithm problem in elliptic curves. Compositio
  Math. 2011.
- J.-C. Faugère, L. Perret, C. Petit, G. Renault. Improving the complexity of
  index calculus algorithms in elliptic curves over binary fields. EUROCRYPT
  2012.
- C. Petit, J.-J. Quisquater. On polynomial systems arising from a Weil
  descent. ASIACRYPT 2012.
- J.-C. Faugère, P. Gaudry, L. Huot, G. Renault. Using symmetries in the index
  calculus for elliptic curves discrete logarithm. J. Cryptology 2014.
- J.-C. Faugère, L. Huot, A. Joux, G. Renault, V. Vitse. Symmetrized summation
  polynomials: using small order torsion points to speed up elliptic curve
  index calculus. EUROCRYPT 2014.
- I. Semaev. New algorithm for the discrete logarithm problem on elliptic
  curves. IACR ePrint 2015/310.
- M.-D. Huang, M. Kosters, S. Yeo. Last fall degree, HFE, and Weil descent
  attacks on ECDLP. CRYPTO 2015.
- S. Galbraith, P. Gaudry. Recent progress on the elliptic curve discrete
  logarithm problem. Des. Codes Cryptogr. 2016.
- S. Galbraith, R. Granger, S.-P. Merz, C. Petit. On index calculus algorithms
  for subfield curves. SAC 2020 (IACR ePrint 2020/1315).
- V. Shoup. Lower bounds for discrete logarithms and related problems.
  EUROCRYPT 1997.

## Review checklist

- [ ] Independent check of Proposition 5 and of the three escape cases in 5.2.
- [ ] Reconcile Theorem 6's gain $g$ with GGMP 2020 Lemma 3.3's $n'$.
- [ ] Independent review of `analysis/symmetrized-anf-20260929/` before
      Section 8 is quoted.
- [ ] Novelty search on every row of Section 9, including the non-open-access
      Diem 2011.
- [ ] One human reader from arithmetic geometry for Section 3 and one from the
      Gröbner-basis community for Sections 7 and 8.
