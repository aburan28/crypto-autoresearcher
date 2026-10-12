# Cheon 2-torsion lifting audit — 2026-10-07

Update: `CERTIFICATION.md` completes the next check for both published candidates. All six factor magnitudes are now certified prime, both rational ranks are exactly 2, and the supplied point pairs are proved independent. The original scan and its earlier unresolved status below are retained as historical evidence.

Primary sources: [Cheon, Lee, Hahn, Chee, *Elliptic Curve Discrete Logarithms and Wieferich Primes*](https://www.math.snu.ac.kr/~jhcheon/publications/2000/JWISC00_CLH.pdf), §§2–4; [IEICE event record](https://www.ieice.org/publications/ken/summary.php?contribution_id=KJ00002127102&expandable=0&ken_id=ISEC&lang=en&presen_date=2000%2F1%2F25&schedule_id=AN10060811_99%28584%29&society_cd=ESSNLS&year=2000), presentation 2000-01-25. A separate PDF posting date is not established.

## Exact scope

The section 4 family assumes a nonsingular curve over F_p with nontrivial rational 2-torsion, written y²=x(x²+ax+b). The supplied points have distinct nonzero x coordinates. The authors choose integral lifts x1=t1² and x2=−t2², ordinate lifts with prescribed residues, and a parameter n; coefficient changes are multiples of p. Their explicit formulas make B(n) linear and A(n) quadratic, and factor A(n)²−4B(n) into two quadratic polynomials. For their rank bound, |B(n)| and both quadratic factors must be prime up to sign, giving w(B)+w(A²−4B)−1≤2. The authors' stated residue applicability additionally distinguishes p mod 4 and, for p≡1 mod 4, requires both finite x coordinates to be quadratic residues. Integral representative, parity, coprimality, and inverse conditions remain in the formula. This is a restricted construction, not a proof of acceptance for every externally supplied pair.

For this exact model at odd good p, (0,0) is a nonidentity point of order 2 after reduction, so #E(F_p) is even. Thus an odd-order target curve cannot be reached by this model with compatible good reduction. This is a mathematical obstruction to this family on those targets, not to other lifting families.

Theorem 2 is a separate fast **coefficient recovery** algorithm. It assumes two already dependent rational lifts on E/Q (free rank 1 for the relevant points), a good auxiliary prime q dividing the finite order of P, a non-Wieferich condition for the free generator, q>16 in the proof's torsion argument, and q² not dividing #E(F_p). It computes the relation coefficient mod q from a q-adic formal-logarithm ratio after multiplying both points by N_q=#E(F_q). The paper gives O(log N_q) group operations modulo q^5 **per eligible q**, plus point counting/factorization, a residual small-subgroup computation and CRT. The method does not construct a dependent pair; the authors say that obtaining the rational lift is difficult. Rank≤2 from §4 does not imply dependence of two lifted points.

The recovery certificate would be: exact curve and point equations over Q, good reduction to the supplied finite curve and points, a rank≤1 or explicit nonzero rational relation certificate, verified q hypotheses, and final multiplication check Qtilde=[m]Ptilde. Our run checks the first two and the section 4 polynomial identities; it does not establish the rank, rational dependence, auxiliary-prime hypotheses, or recovered logarithm.

## Bounded reproduction

Command from `/workspace/scratch/3da470499f60`:

```bash
python research-watch/cheon_example_audit.py > research-watch/cheon_example_audit.json
```

No seed. Python 3.12.14, standard library only. Exact inputs and all raw output are in the JSON. Source example: p=353, a=−1, b=16, P=(9,63), Q=(17,183), t1=703, t2=439; scan every integer n from −2000 through 2000 inclusive. Check absolute values of the three factor polynomials using Miller–Rabin bases 2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53. **This is probable primality, not a primality certificate.** Independently reconstruct A(n), B(n), lifted ordinates; check equations, reduction, and discriminant factorization with exact integers.

Result: 4,001 n tested; 3,819 rejected first at B, 175 first at quadratic factor 1, 5 first at quadratic factor 2. The only surviving values were n=−1793 and 181, matching the paper. Both passed all exact algebraic checks; 0 assertion failures. The run's measured execution time was 0.109 seconds on this runtime; it excludes source retrieval, script preparation, rank computation, point counting, and dependency recovery. Each example had 63-bit |A| and 81-bit |B|. No general performance inference follows.

## Comparison and next falsifiable test

Xedni V2's dependent doubling section verified a built-in relation in 68 synthetic cases but covered one residue per p. Its four-prime curve-fitting trial had 1,944 fits from 24 pairs; 20 pairs had a finite-field small relation, and none of those produced a rational relation within coefficient bound 8. The Cheon family fits an eligible supplied pair and constrains rank, but no dependency certificate emerged here. Thus it addresses the curve-rank side more directly than unrestricted fitting without closing the same missing-dependence obligation.

Next test, using Sage/Magma or a verified 2-descent implementation: enumerate finite point pairs on the published F_353 curve with distinct nonzero x, classify the formula's x-square/sign eligibility, choose bounded representatives |t_i|≤1000 satisfying the congruences and inverse/coprimality conditions, and scan |n|≤2000. Record every failed branch and prime test. For every candidate with certified prime factors, compute a rigorous rank upper bound and independent lower bound and run a saturation/relation calculation for the lifted P,Q. Success requires a verified rational relation whose reduction has a nonzero invertible P coefficient, plus recovery checked by [m]Ptilde=Qtilde. Falsification within this budget is zero such certificates; that would limit only this bounded family, not all 2-torsion lifts.
