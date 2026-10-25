# Coordinator notes: verified derivations (2026-10-24)

These are my own derivations/computations, independent of the literature lanes.

## 1. Newton polytope of S_{m+1} with one variable fixed is the full box (computed)

Sage (inner binary, p = next_prime(2^28), random a, b):

| polynomial | terms | deg/var | total deg | support with last var fixed | box | hull centroid sum c_N | JM reach 1/((m+1)c_N) |
|---|---:|---:|---:|---:|---:|---:|---:|
| S_3 | 17 | 2 | 4 | 9 | 9 | 2 | 1/6 |
| S_4 | 439 | 4 | 12 | 125 | 125 | 6 | 1/24 |
| S_5 | 54777 | 8 | 32 | 6561 | 6561 | 16 | 1/80 |

Total degree of S_n is (n-1)·2^{n-2}; with one variable fixed the remaining m = n-1 variables of degree 2^{m-1} each have max total degree m·2^{m-1} = total degree of S_n, so the box is not cut. Verified: every monomial of the box appears.

Consequence: the Jochemsz–May basic-strategy asymptotic reach for equal bounds X_i = p^δ is
  δ_max = 1/((m+1)·c_N)   with c_N = Σ_j (centroid_j of Newton polytope),
derived from |M_k| = #((t−k)N + k·l) = #lattice pts of (t−k)N ≈ Vol(N)(t−k)^m (shape independent, l any point of N), s_N = t|M_0| − Σ_{k≥1}|M_k| ≈ Vol·t^{m+1}·m/(m+1), Σ_j s_j ≈ Vol·t^{m+1}·c_N; condition Σ_j δ s_j < t|M_0| − s_N. For the box c_N = m·d/2 ⇒ δ_max = 2/(m(m+1)d), the formula in RESEARCH_PRIME_FIELD_BREAKTHROUGH_PROGRAM.md §2.2. Since the support is the full box, the polytope cannot be exploited. (Unequal bounds: Σ_j δ_j·centroid_j < 1/(m+1).)

## 2. Lang–Weil / Bézout lemma: no algebraic factor base over F_p

Claim. Let V ⊂ F_p, |V| = B, and suppose V = π(W(F_p)) where W ⊂ A^{1+r} is defined by polynomials of degrees ≤ D (π = projection to the x-coordinate). Then either (i) some F_p-irreducible, absolutely irreducible, positive-dimensional component of W that is not contained in a fibre {x = c} contributes ≥ (p − O(D^2 √p))/D ≳ p/D distinct x-values (Lang–Weil + the fibre of π over a value has ≤ D points on a curve component, more generally the degree of π restricted to the component), or (ii) all x-values come from vertical components (one x each) and 0-dimensional components (≤ Bézout number ∏ d_i points). So B ≤ #(vertical comps) + Bézout(W) unless B ≳ p/D.

Reading: a factor base of size B = p^{1/m} ≪ p/D that is cut out algebraically has Bézout cost ≥ B, i.e. its "membership degree" is ≥ its size. The quotient algebra F_p[x_1..x_m]/(g_V(x_i)) ≅ F_p^{B^m} (CRT, g_V split with distinct roots), so any Gröbner/XL computation in it is a change of basis from evaluation on the grid V^m: the HEUR-ICEX-6ca21f-1 statement, now with the "images of low-degree maps" loophole closed by Lang–Weil. Over F_{q^n} the escape is Weil restriction: "x ∈ F_q" is q-degree as a polynomial but LINEAR in F_q-coordinates because Frobenius is F_q-linear; F_p has trivial Galois group, so no such coordinate system exists. Also: any polynomial map F_p → S has degree ≥ p/|S| (each value has ≤ deg preimages), so "bit extraction" or any projection to a small set is degree ~p — the "bit-descent" idea (write x_i = Σ x_{ij}2^j, x_{ij}^2 = x_{ij}) lands in the split algebra F_p[x_ij]/(x_ij^2 − x_ij) ≅ F_p^{2^N}, same CRT barrier.

## 3. APS known-log factor base = k-sum problem in a generic group

If F = {R_i = a_iP + b_iQ} with known (a_i, b_i), a relation Σ e_i R_i = O (e_i ∈ {−1,0,1}) gives k = −Σ e_i a_i / Σ e_i b_i. Finding such a relation among B random group elements is the k-sum (generalised birthday) problem in the group E(F_p). Wagner's k-list algorithm needs a "partial order compatible with the group operation" (XOR-low-bits, or sums landing in a small interval of Z/n) to merge lists without computing all pairwise sums; on E(F_p) no coordinate function is compatible with the group law (x(P+Q) is not predictable from x(P), x(Q) without the full addition), so each merge is a full MITM. The summation-polynomial formulation S_m(x_1..x_m)=0, g_F(x_i)=0 lives in F_p^{B^m} (CRT) and is evaluation. So the one-relation trick cannot beat the generic k-sum cost and in particular not √p; this is the CRT argument in AR:H-ICEX-6ca21f. What the trick does buy: removes the linear algebra and the factor-of-B relation count, so it is strictly a constant-factor reorganisation inside the generic class.

Note the dual: with a STRUCTURED base (interval/subgroup), logs are unknown and B relations are needed, so the one-relation trick does not apply; with KNOWN logs there is no structure. The two ingredients (structure, known logs) are mutually exclusive except through Aut(E)/endomorphisms, which give orbits of size |Aut| ∈ {2,4,6} (constant).

## 4. Product/evaluation paradigm and why it is blocked too

The PDP for base V ⊂ F_p and target z: decide whether N_V(z) := Π_{u ∈ V^m} S_{m+1}(u, z) = 0 (norm of S_{m+1} from the split algebra A_V = F_p[x]/(g_V(x_i))). One-dimensional norms are cheap:
 - V = μ_B (subgroup): Π_{u∈μ_B} g(u) = Res(g, X^B − 1) via X^B mod g, cost Õ(deg g · log B).
 - V = [0,B): Π_{u<B} g(u) via Bostan–Gaudry–Schost baby-step/giant-step, cost Õ(√B · deg g).
So the LAST variable of a decomposition costs polylog or √B instead of B. But the (m−1)-fold outer product is over a polynomial of degree 2B (resultant in the last variable has X-degree deg_X(S)·B), so the second level costs Õ(B) (subgroup) or Õ(B^{3/2}) (interval, BGS on a degree-2B polynomial); a direct 2-D baby/giant split with s^2 baby steps produces a bivariate polynomial with ~4s^4 coefficients, giving B^{4/3}. Both are ≥ the enumeration B and ≥ the MITM B^{m/2} for m ≤ 2. Precise open problem that a breakthrough in this paradigm needs: compute Π_{u ∈ [0,B)^4} S_5(u_1..u_4, z) mod p (or the μ_B^4 analogue) in time B^{1−ε}; nothing known is below B^2 (MITM) and the natural reductions give ≥ B^{3/2}.

For f = X_2 − X_1 − a and V = μ_B the double product collapses: Res(X^B−1, (X+a)^B−1) = a^B Π_{u∈μ_e} (a^B − u)^{r_u}, e = (p−1)/B, r_u = cyclotomic numbers of order e. Evaluating needs the e ≈ p/B cyclotomic numbers (Jacobi sums of order e, Õ(√p) each via Gross–Koblitz/fast factorials) — total ≥ p/B, i.e. √p at B = √p. No collapse for S_3 (not homogeneous: for a = 0 only the diagonal μ_3 action is a symmetry).

## 5. Accounting (from the repo, re-derived)

cost(B) ≈ (m!/2^m)·p·T_dec/B^{m−1} + m·B^2, optimum B = (p·T_dec)^{1/(m+1)}, total ≈ (p·T_dec)^{2/(m+1)}·const. m=2: never < √p; m=3: ties only with T_dec = O(1); m=4: beats √p iff T_dec ≪ p^{1/4}; m=5: iff T_dec ≪ p^{1/2}. With enumeration/MITM T_dec = B^{⌈m/2⌉}: m=4 gives p^{2/3}, m→∞ gives p^{1/2+1/m}. The Kuhn–Struik / Bernstein–Lange / Corrigan-Gibbs–Kogan S·T^2 ≥ n line is respected by every enumeration variant, including "multiplied" bases ∪_{k≤N}[k](F) and Aut-orbits (these only shift constants).
