# Prime-field candidate memo (proposals only)

Recommended order: shared divisor Graeffe encoding; certified finite-domain FF-CDCL; partial multigraded Macaulay layers. Strong backdoors and complete saturation are secondary, stop-gated investigations. All drafts reuse RQ-PFDR-ae2fba. Graeffe now has a separate open_unexamined lead draft because the existing membership lead's low-degree/yield revisit criterion does not cover shared solving work; the other drafts reuse existing leads. None asserts a new factor base or proven degree/exponent improvement.

## Distinctive representation and exact mathematics

Work initially with an ordinary curve E: y^2=f(x)=x^3+ax+b over F_p, p>5, with E(F_p) of prime order. Let R=(r,s), s nonzero, and d=2^k divide p-1. Choose t nonzero and c=t^d. Then X^d-c has exactly d distinct F_p roots: the coset t*mu_d.

The space L(6O) has basis 1,x,y,x^2,xy,x^3. Normalize the x^3 coefficient to 1 and write h=A(x)+B(x)y with A monic cubic and B of degree at most 1. Require

    A(r)-s B(r)=0,
    A(X)^2-B(X)^2 f(X)=(X-r)U(X),

where U is monic degree 5. If U(r)!=0 and gcd(U,B)=1, every root xi of U yields P_i=(xi,-A(xi)/B(xi)); its multiplicity in U is retained. The function h has pole order exactly 6 at O. Its zeros are -R and these five points, counted with multiplicity. Therefore div(h)=sum(P_i)+(-R)-6O is principal, and sum P_i=R. This is a standard divisor argument, not a new theorem. Conversely a decomposition in this chart gives such a normalized h. Points at infinity, coincident target x, B=0 cases and other excluded divisors need separate complete branches or an explicitly measured coverage loss. For curves with cofactor, subgroup handling needs a separate exact projection/coverage argument.

Two exact simultaneous-membership circuits are worth comparing:

1. Shared quotient circuit: enforce X^d=c in F_p[X]/U. For squaring use R_j^2=Q_j U+R_(j+1), deg R<5, deg Q<=3. This requires O(log d) layers with O(1) coefficient variables/equations per layer. Because U divides squarefree split X^d-c, U itself is split and squarefree. It selects distinct x coordinates.
2. Shared Graeffe circuit: if U_j(X)=E_j(X^2)+X O_j(X^2), set U_(j+1)(T)=T O_j(T)^2-E_j(T)^2. For monic degree 5 this is the monic polynomial whose roots are squares of the roots of U_j. Thus U_k(T)=(T-c)^5 is equivalent to every root of U_0 satisfying xi^d=c. Each layer has five quadratic coefficient equations. Repeated roots are allowed; impose squarefreeness only when matching the quotient circuit's selected predicate.

The second circuit has no per-root labels, no quotient-polynomial variables and no division in the membership layers. It is not a claim of low solving degree: elimination through k quadratic layers can recover degree comparable to 2^k. The m=1 slice is the familiar x^d=c equation, which exposes that distinction immediately. The suitable divisor d is a real field restriction. An arbitrary interval-support product has no free logarithmic-length circuit.

The most speculative solver extension is to branch backwards on polynomial preimages. The terminal polynomial (T-c)^5 has only six unordered coefficient preimages under squaring, corresponding to how many roots choose each square root of c. Further layers branch on multiplicity signatures. This replaces arbitrary field-value branching with exact finite choices. Nevertheless the complete tree contains binomial(d+4,5) multisets; absent norm-driven early pruning this is only known permutation symmetry. A useful claim would require short, independently checked norm-incompatibility certificates that eliminate entire early branches, with certificate construction charged. Do not turn this into a sixth independent lead without evidence.

## Prior work and honest novelty boundary

- Petit-Kosters-Messeng 2016 already uses multiplicative subgroup/coset factor bases and separate low-degree rational-map towers. The exact source is https://people.maths.ox.ac.uk/petit/files/16PKC_primeECDLP.pdf, sections 3.1-3.4. Function-first coefficient/support solving H|L_V is already explicit in IDEA-20260918-5a9a51. The remaining proposed delta is shared membership on symmetric divisor coefficients throughout the tower.
- Graeffe root squaring itself is classical. A primary formally verified implementation is discussed in https://link.springer.com/article/10.1007/s10817-019-09526-y. The proposal-index search for Graeffe, root-squaring, symmetric-power, Adams, plethysm and companion-matrix terms found no direct match, which is not a novelty proof.
- The latest algebraic-membership atlas lead is closed against lower-degree membership and improved mean yield. This proposal accepts both obstructions; it tests algorithmic solving work on the same high-degree base. No reopening claim follows from a shorter input circuit.
- Prime-field CDCL(T), guarded PRS, separator syzygies and tensor/chordal views already have proposals. Basic SAT, quadratization, graph densification and symmetry are not new leads.
- Root audit reports DEC-20261003-277d8b as preliminary inverse-degree FULL support at s=4,5,6, produced with dirty state and without independent review. It concerns plain Macaulay residual refutation, not exact d_reg or the bounded-PC mutant stage. Direct-SAT and PRS records have run references, but only specification.yaml was found in their tracked experiment trees; execution evidence must be reconciled before citing results.

## Cost gate and minimal first test

For factor-base size B=N^beta and fixed arity m, the mean number of unordered decompositions is approximately B^m/(m!N), with exact sign/multiplicity conventions required. The probability rho of at least one decomposition is a separate measured quantity. Ordinary IC costs preprocessing +(B/rho)*C_attempt + sparse relation linear algebra, approximately soft-O(B^2), plus descent. For m=5, beta=1/5 and constant rho, a sub-rho attempt budget needs C_attempt=N^gamma with gamma<3/10. No proposal presently meets it. S_(m+1) represents m factor-base points plus the target; S5 must not be described as a five-factor-base-point system.

The best first action is a symbolic correspondence note and tiny exact census for the Graeffe encoding at k=3,4, after separately checking at least five usable distinct x coordinates, comparing its full recovered relation set against the per-root and quotient encodings on the identical declared chart. Since d=4 cannot contain five distinct roots, retain k=2 only as a deliberate empty squarefree-chart negative control. Include repeated roots separately, target-coordinate collisions, 2-torsion x roots when applicable, gcd(B,U)=0, and infinity. Uniform targets and planted targets must remain separate. A single correspondence failure stops timing work. This first test establishes encoding correctness only. After it passes, freeze a matched solver protocol that records solving/refutation degree, rank profiles, matrix work, all branch/certificate costs, coverage and complete relation costs.

No experiment was run while preparing this memo. Only the five YAML drafts and this memo were written.
