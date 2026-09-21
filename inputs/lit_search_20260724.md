# Literature Search: State of the Art and Prior Art for ECDLP on Ordinary Prime-Field Curves

- **Date:** 2026-07-24
- **Scope:** Elliptic Curve Discrete Logarithm Problem (ECDLP) on *ordinary* (i.e., general, non-special) curves over prime fields F_p of large characteristic. Baseline: Pollard rho, O(√n) group operations for group order n; no known subexponential index-calculus attack. Purpose: novelty classification support (LEDGER-NEW / LITERATURE-ADJACENT / NOVELTY-UNVERIFIED / POSSIBLY NOVEL).
- **Method:** ~34 targeted web searches (kimi_search_v2 / WebSearch) across 13 assigned areas, followed by reading of returned primary sources (arXiv, IACR ePrint, journal pages, conference programs, reference lists). Identifiers (DOI/arXiv/ePrint/LNCS) are given where observed. Items whose details come only from secondary reference lists are flagged.
- **Caveat:** This is a coverage-oriented search, not a full-text audit of every cited paper. Where a claim matters for a novelty decision, the primary source should be re-read before the claim is relied upon in a ledger record.

---

## 1. Generic algorithms and lower bounds (rho, BSGS, generic-group model)

Framing: the security baseline for prime-field ECDLP. The generic-group model gives an Ω(√q) lower bound; all practical improvements are constant-factor (parallelization, negation/automorphism orbits).

- **Pollard, J. M. (1978). "Monte Carlo methods for index computations (mod p)."** *Mathematics of Computation* 32(143): 918–924.
  The original rho/kangaroo methods for DLP; directly adapted to elliptic-curve groups. This is the baseline O(√n) algorithm all prime-field ECDLP attacks are measured against.
- **Shanks, D. (1971). "Class number, a theory of factorization, and genera."** *Proc. Symp. Pure Math.* 20: 415–440.
  Baby-step giant-step; deterministic O(√n) time/space generic algorithm.
- **Nechaev, V. I. (1994). "Complexity of a determinate algorithm for the discrete logarithm."** *Mathematical Notes* 55(2): 91–101.
  First Ω(√q) lower bound for deterministic generic DL algorithms (some reference lists give pages 165–172).
- **Shoup, V. (1997). "Lower bounds for discrete logarithms and related problems."** EUROCRYPT 1997, LNCS 1233: 256–266.
  The standard generic-group model: any generic DL algorithm in a group of prime order q needs Ω(√q) group operations. Formal foundation for "rho is optimal generically".
- **Maurer, U.; Wolf, S. (1998). "Lower bounds on generic algorithms in groups."** EUROCRYPT 1998, LNCS 1403: 72–84.
  Alternative generic-model formalization (black-box group with random encoding), confirming √q-type bounds.
- **van Oorschot, P. C.; Wiener, M. J. (1999). "Parallel collision search with cryptanalytic applications."** *Journal of Cryptology* 12: 1–28.
  Distinguished-point parallelization: m processors give essentially m× speedup; the basis of all record ECDLP computations.
- **Wiener, M.; Zuccherato, R. (1998); Escott, A. (1998); Duursma, I.; Gaudry, P.; Morain, F. (1999). "Speeding up the discrete log computation on curves with automorphisms."** ASIACRYPT 1999, LNCS 1716: 103–121.
  Rho on automorphism orbits: an efficiently computable automorphism of order m yields a √m speedup. Includes the √(2n)-style Koblitz-curve result (Frobenius orbit, extension fields only). Consequence for prime fields: generic curves have only ±1 → max √2 gain.
- **Gallant, R.; Lambert, R.; Vanstone, S. (2000). "Improving the parallelized Pollard lambda search on anomalous binary curves."** *Mathematics of Computation* 69: 1699–1705.
  Optimal orbit use for Koblitz (anomalous binary) curves; not applicable to prime fields.
- **Bos, J. W.; Kleinjung, T.; Lenstra, A. K. (2010). "On the use of the negation map for computing Pollard rho."** ANTS-IX 2010, LNCS 6197: 108–118.
  Showed the negation map can introduce fruitless cycles; best non-SIMD speedup observed 1.29 rather than √2.
- **Bernstein, D. J.; Lange, T.; Schwabe, P. (2011). "On the correct use of the negation map in the Pollard rho method."** PKC 2011; IACR ePrint 2011/003; cr.yp.to/elliptic/negation-20110102.pdf.
  Fixed the cycle issue; the full √2 negation-map speedup is regained, including SIMD. Establishes the accepted constant: rho+negation ≈ √(πn/4) iterations (SafeCurves rho page: √(π/2)√ℓ → √(π/4)√ℓ).
- **Bos, J. W.; Kaihara, M. E.; Kleinjung, T.; Lenstra, A. K.; Montgomery, P. L. (2012). "Solving a 112-bit prime elliptic curve discrete logarithm problem on game consoles."** *International Journal of Applied Cryptography* 2(3): 212–228.
  The standing prime-field ECDLP record: secp112r1, ~60 PS3 years. Nothing larger has been publicly solved over a prime field.
- **Cheon, J. H.; Hong, J.; Kim, M. (2012). "Accelerating Pollard's rho algorithm on finite fields."** *Journal of Cryptology* 25: 195–242.
  Polynomial-evaluation speedups for DL in extension fields with smooth-order structure; does not beat √n for prime-order prime-field EC groups.
- **Bernstein, D. J. et al. (2016).** IACR ePrint 2016/382 (FPGA rho implementations). Engineering-only constant-factor line of work.
- **Corrigan-Gibbs, H.; Henzinger, A.; Wu, D. J. (2026). "The Structured Generic-Group Model."** EUROCRYPT 2026; IACR ePrint 2026/384.
  The strongest recent theory result: any DL algorithm that exploits structure of at most a δ-fraction of group elements must run in Ω(min(√q, 1/δ)) operations, with *explicit* lower bounds for the structure of small integers, smooth polynomials, and **elliptic-curve points** — i.e., exactly the kind of structure an index-calculus factor base over F_p would need. Effectively raises the bar for any claimed sub-√n prime-field ECDLP algorithm. (Related model: Hhan 2025 smooth-GGM.)

**Verdict (prime-field F_p):** Well-covered and closed in practice: Ω(√q) generic lower bound; best real constant is rho+negation √(πn/4); parallelization linear in hardware; largest public solve 112 bits (2012). SGGM 2026 extends lower bounds to structure-exploiting algorithms.

---

## 2. Semaev summation polynomials and the decomposition problem

Framing: Semaev's summation polynomials enable index-calculus *decomposition* over extension fields; whether they can work over prime fields is a central question for any algebraic ECDLP claim.

- **Semaev, I. (2004). "Summation polynomials and the discrete logarithm problem on elliptic curves."** IACR ePrint 2004/031.
  Defines summation polynomials S_r; S_r has degree 2^{r−2} in each variable. Foundation of all algebraic ECDLP attacks.
- **Gaudry, P. (2009). "Index calculus for abelian varieties of small dimension and the elliptic curve discrete logarithm problem."** *Journal of Symbolic Computation* 44(12): 1690–1702.
  Summation-polynomial decomposition gives Õ(q^{2−2/n}) over F_{q^n} for fixed n ≥ 2; beats rho for n ≥ 3 asymptotically (with large constants).
- **Diem, C. (2011). "On the discrete logarithm problem in elliptic curves."** *Compositio Mathematica* 147(1): 75–104; and **Diem, C. (2013).** *Algebra & Number Theory* 7(6): 1281–1323.
  Rigorous Õ(q^{2−2/n}) for fixed n ≥ 2 and a subexponential (q^n)^{o(1)} result for n → ∞ with n/log q → 0. **Crucially, all of this is for extension fields** (q^n with n ≥ 2); the techniques presuppose a base field F_q and Weil restriction.
- **Faugère, J.-C.; Perret, L.; Petit, C.; Renault, G. (FPPR) (2012). "Improving the complexity of index calculus algorithms in elliptic curves over binary fields."** EUROCRYPT 2012, LNCS 7237: 27–44.
  First-fall-degree (FFD) based complexity analysis of binary-field ECDLP decomposition.
- **Petit, C.; Quisquater, J.-J. (2012). "On polynomial systems arising from a Weil descent."** ASIACRYPT 2012, LNCS 7658: 451–466.
  Heuristic subexponential binary ECDLP under an FFD assumption; beats generic algorithms only for n ≳ 2000.
- **Faugère, J.-C.; Huot, L.; Joux, A.; Renault, G.; Vitse, V. (2014). "Symmetrized summation polynomials: using small order torsion points to speed up elliptic curve index calculus."** EUROCRYPT 2014, LNCS 8441: 40–57.
  Symmetrization (invariant coordinates) plus small-torsion tricks; reduces degree growth of decomposition systems (binary fields).
- **Faugère, J.-C.; Huot, L.; Renault, G. (FGHR) (2014).** *Journal of Cryptology* — complexity O(log q · (d^{ωn} + n·2^{3n(n−1)})) for the point-decomposition problem; illustrates the double-exponential-in-n cost driver.
- **Kosters, M.; Yeo, S. L. (2015). "Notes on summation polynomials."** arXiv:1503.08001.
  Two disruptive observations: (i) deciding S_r = 0 is NP-complete for large r (under an assumption; unconditional for singular curves); (ii) the Weil descent of S_2 over F_{2^n} has first fall degree 2, which the authors say should "raise doubt on certain Gröbner basis heuristics" underlying subexponential claims.
- **Huang, M.-D. A.; Kosters, M.; Yeo, S. L. (2015). "Last fall degree, HFE, and Weil descent attacks on ECDLP."** CRYPTO 2015, LNCS 9215: 581–600; ePrint 2015/573.
  Introduces last-fall-degree as the right invariant; provides evidence *against* the first-fall-degree assumption used for subexponentiality claims.
- **Huang, M.-D. A.; Kosters, M.; Yang, Y.; Yeo, S. L. (2018). "On the last fall degree of zero-dimensional Weil descent systems."** *Journal of Symbolic Computation* 87: 207–226; arXiv:1505.02532.
  Summation-polynomial Weil-descent systems without field equations are **not zero-dimensional**, so degree of regularity may depend on n; further undermines heuristic subexponentiality.
- **Huang, M.-D. A.; Kosters, M.; Petit, C.; Yeo, S. L.; Yun, A. (2020). "Quasi-subfield polynomials and the elliptic curve discrete logarithm problem."** *Journal of Mathematical Cryptology* 14(1): 25–38.
  Quasi-subfield polynomials tighten what is achievable from summation-polynomial structure (abstract-level coverage here).
- **Kousidis, S.; Wiemers, A. (2019). "New lower and upper bounds for the degree of regularity of Weil descent systems."** *Journal of Mathematical Cryptology*; arXiv:1906.05594; doi:10.1515/jmc-2017-0022.
  The first fall degree of the Weil descent of S_{m+1} is ≤ m²−m+1, strictly beating the Petit–Quisquater bound m²+1, and sharp for m ≥ 3 (m = 2 pathological). If Dreg = m²−m+1+o(1), the PQ complexity sharpens toward O(2^{c·log n·(n^{2/3}+1)}) — still exponential and still binary-field only.
- **Petit, C.; Kosters, M.; Messeng, A. (2016). "Algebraic approaches for the elliptic curve discrete logarithm problem over prime fields."** PKC 2016, LNCS 9614: 3–18.
  **The key prime-field prior art.** Defines factor bases {L(x) = 0} via rational maps, using either cosets of smooth subgroups or isogenies from auxiliary smooth-order curves; shows NIST P-224 falls in the framework. Their own conclusion: *"At the moment all attacks are outperformed by generic discrete logarithm algorithms for practically relevant parameters."* Any new "prime-field summation-polynomial/index-calculus" claim must differentiate itself from this paper.
- **Amadori, A.; Pintore, F.; Sala, M. (2018). "On the discrete logarithm problem for prime-field elliptic curves."** *Finite Fields and Their Applications* 51: 168–182; plus companion chapter "Acceleration of Index Calculus … and Its Limitation" (Springer, 2018; uses Caminata–Gorla solving-degree bounds, arXiv:1706.06319).
  Prime-field variant with a single Gröbner-basis call; claims to outperform Semaev/Petit et al. in experiments — but remains far slower than rho at cryptographic sizes.
- **McGuire, G.; Mueller, D. (2017).** IACR ePrint 2017/1262.
  Fast summation-polynomial evaluation with a random factor base, avoiding Gröbner bases; practical only at toy sizes.
- **Shantz, M.; Teske, E. (2013).** LNCS 8260: 94–107. Solving multivariate systems from ECDLP decomposition; implementation-level results.
- **Galbraith, S. D.; Gebregiyorgis, S. W. (2014).** INDOCRYPT 2014, LNCS 8885: 409–427. Disjoint factor bases removing k! symmetry overheads (char 2 focus).
- **Huang, Y.-J.; Petit, C.; Shinohara, N.; Takagi, T. (2013).** IWSEC 2013, LNCS 8231: 115–132. Improvements for decomposition over extension fields.
- **Semaev, I. (2015).** arXiv:1504.01175 = ePrint 2015/310. Heuristic 2^{1.69√(n ln n)} binary-field claim; widely regarded as unproven/disputed given the FFD literature above.
- **Galbraith, S. D.; Gaudry, P. (2016). "Recent progress on the ECDLP."** *Designs, Codes and Cryptography* 78: 51–72; hal-01215623.
  Authoritative survey. On prime fields: Semaev's factor base of small-integer abscissae exists, but *"the elliptic group law is deeply incompatible with the multiplication of the integers… there is no known efficient decomposition algorithm for that choice of F, and elliptic curves over prime fields remain unaffected by index calculus algorithms."*
- **Weak/flagged:** a 2024 EasyChair preprint claims the Petit et al. S_3 expression is incorrect; venue and quality are low — treat as unverified noise unless independently confirmed.

**Verdict (prime-field F_p):** Well-covered. Prime-field algebraic attacks have been *explicitly attempted* (Petit–Kosters–Messeng 2016; Amadori–Pintore–Sala 2018; McGuire–Mueller 2017) and all lose to rho; the FFD/last-fall-degree literature explains why even the stronger binary-field subexponentiality claims are doubtful. "Semaev-style index calculus for prime fields" is **not** novel per se — only a *specific new mechanism* that demonstrably beats rho could be.

---

## 3. Index calculus via Jacobians and class groups (Gaudry, Diem, Enge)

Framing: subexponential index calculus exists for higher-genus curves and for elliptic curves over extension fields via Jacobian arithmetic; understanding *why* it fails over F_p is essential.

- **Gaudry, P.; Thomé, E.; Thériault, N.; Diem, C. (2007). "A double large prime variation for small genus hyperelliptic index calculus."** *Mathematics of Computation* 76(257): 475–492.
  Õ(q^{2−2/g}) for genus-g hyperelliptic Jacobians; genus 3 gives q^{4/3}, beating rho's q^{3/2}.
- **Thériault, N. (2003).** ASIACRYPT 2003, LNCS 2894: 75–92. Earlier q^{2−2/(g+1)} index calculus.
- **Diem, C.; Thomé, E. (2008). "Index calculus in class groups of non-hyperelliptic curves of genus three."** *Journal of Cryptology* 21: 593–611.
- **Diem, C. (2006).** ANTS 2006, LNCS 4076: 543–557. q^{2−2/(g−1)} for sufficiently general plane curves.
- **Enge, A.; Gaudry, P. (2002).** *Acta Arithmetica* 102(1): 83–103. General L(1/2) framework for medium/high genus.
- **Enge, A.; Gaudry, P.; Thomé, E. (2011).** *Journal of Cryptology* 24: 24–41. L(1/3) for low-degree plane curves.
- **Adleman, L.; DeMarrais, J.; Huang, M.-D. (1999).** *Theoretical Computer Science* 226: 7–18. First L(1/2) high-genus algorithm.
- **Enge, A. (2002).** *Mathematics of Computation* 71: 729–742. L(1/2) refinements.
- **Why prime fields fail (survey-level explanation):** index calculus needs a smoothness notion obtained either by lifting F_q elements to rings of integers of number fields (Frey/Lange, Handbook of Elliptic Curve Cryptography: *"the reason for these fast algorithms is that it is easy to lift elements in F_q to elements in rings of integers of number fields"*) or from subfield structure. A prime field F_p offers neither: elliptic-curve points over F_p have no natural global-field lift with multiplicative structure (cf. the Galbraith–Gaudry quote in §2).

**Verdict (prime-field F_p):** Well-covered. All class-group index calculus is genus ≥ 2 or extension-field; the obstruction over F_p is structural and documented. Any claim of Jacobian/class-group methods helping ordinary prime-field ECDLP must explain how it supplies the missing smoothness structure.

---

## 4. Weil descent, GHS, and trace-zero attacks

Framing: the most powerful classical ECDLP attacks beyond rho — but they are intrinsically extension-field attacks.

- **Frey, G. (1998).** Conference talk "Applications of arithmetical geometry to cryptographic constructions" — origin of the Weil-descent attack idea.
- **Galbraith, S. D.; Smart, N. P. (1999).** LNCS 1746: 191–200. First technical realization of Weil descent for ECDLP.
- **Gaudry, P.; Hess, F.; Smart, N. P. (2002). "Constructive and destructive facets of Weil descent on elliptic curves."** *Journal of Cryptology* 15(1): 19–46.
  The GHS attack: Weil-restrict E/F_{q^n} to an abelian variety over F_q, intersect with hyperplanes to land in a genus-2^{m−1} (or 2^{m−1}−1) Jacobian, then apply §3 index calculus.
- **Menezes, A.; Qu, M. (2001).** CT-RSA 2001, LNCS 2020: 308–318. GHS fails for all curves over F_{2^m} for prime m ∈ [160, 600].
- **Jacobson, M.; Menezes, A.; Stein, A. (2001).** *J. Ramanujan Mathematical Society* 16: 231–260. Practical GHS for composite-degree fields.
- **Maurer, M.; Menezes, A.; Teske, E. (2002).** *LMS Journal of Computation and Mathematics* 5: 127–174. Complete classification of GLS-vulnerable binary curves.
- **Hess, F. (2004). "Generalising the GHS attack on the elliptic curve discrete logarithm problem."** *LMS J. Comput. Math.* 7: 167–192. GHS in any characteristic.
- **Galbraith, S. D.; Hess, F.; Smart, N. P. (2002). "Extending the GHS Weil descent attack."** EUROCRYPT 2002, LNCS 2332: 29–44. Isogeny-walk extension of GHS (weakens more curves over F_{q^7}, F_{2^155}, …).
- **Menezes, A.; Teske, E. (2006).** *AAECC* 16: 439–460. Cryptographic implications survey of Weil descent.
- **Karabina, K.; Menezes, A.; Pomerance, C.; Shparlinski, I. (2013). "On the asymptotic effectiveness of Weil descent attacks."** *Journal of Mathematical Cryptology* (preprint: math.dartmouth.edu/~carlp/WeilDescent-Product.pdf).
  For almost all elliptic curves over F_{q^n}, the GHS genus satisfies 2^{(1/2+o(1))n} ≤ g ≤ 2^{(2/3+o(1))n} — **exponential in n**, so Weil descent is asymptotically almost never efficient.
- **Diem, C. (2002). "The GHS attack in odd characteristic."** Preprint. Odd-characteristic GHS.
- **Lange, T. (2004).** *Ramanujan Mathematical Society* 19: 15–33. Trace-zero variety attacks (genus 2).
- **Diem, C.; Scholten, J. (DS03).** Trace-zero cover attack: n = 5 → genus 4 with Õ(q^{4/3}) (one curve found); n = 7 → genus 8, none found.
- **Nagao, K. (2010).** ANTS-IX 2010, LNCS 6197: 285–300. Decomposition attacks on trace-zero / higher-dimensional targets.
- **Gorla, E.; Massierer, M. (2015). "Index calculus in the trace zero variety."** *Advances in Mathematics of Communications* 9(3): 515; hal-01097427.
  State of the art on trace-zero index calculus — and an explicit scope statement: *"Notice that this approach only threatens elliptic curves defined over extension fields and does not affect groups E(F_p) where p is a prime. The best attack on such groups is the Pollard-Rho attack, and the current record … is held by Bos, Kaihara, Kleinjung, Lenstra, and Montgomery."*

**Verdict (prime-field F_p):** Well-covered. Weil descent requires an extension F_{q^n}; over F_p there is no proper subfield, so nothing to descend to. Explicit statements in the literature (Gorla–Massierer; Karabina–Menezes–Pomerance–Shparlinski) close the door at the asymptotic level too.

---

## 5. Gröbner bases, SAT solvers, and crossbred methods for ECDLP systems

Framing: even where decomposition systems exist (extension fields), solving them is the bottleneck; solver technology has advanced but not changed the asymptotic picture.

- **Joux, A.; Vitse, V. (2017). "A crossbred algorithm for solving Boolean polynomial systems."** NuTMiC 2017; ePrint 2017/372; hal-01981516.
  Crossbred: Gröbner-free hybrid (sparse/dense linear algebra on degree-monomial partial evaluations). Records: 148 equations/74 variables < 1 day; n = 83/m = 186; n = 114/m = 76 (Boolean MQ).
- **Duarte, J. D. (hpXbred thesis/analysis); Bouillaguet, C.; Sauvage, V. (hpXbred implementation).**
  Careful complexity analysis: for q > 2, crossbred gives **no asymptotic improvement** over FES/Hybrid-F5; its wins are practical/engineering-level.
- **Niederhagen, R.; Ning, K.-C.; Yang, B.-Y. (2018).** GPU implementation of crossbred (NNY18).
- **Bardet, M.; Faugère, J.-C.; Salvy, B.; Spaenlehauer, P.-J. (2013). "On the complexity of solving quadratic Boolean systems."** *Journal of Complexity* 29(1): 53–75.
  BooleanSolve Õ(2^{0.792n}) for overdetermined Boolean quadratic systems; crossover vs exhaustive search around n ≈ 200.
- **Bettale, L.; Faugère, J.-C.; Perret, L. (2009). "Hybrid approach for solving multivariate systems over finite fields."** *J. Math. Cryptol.* 3: 177–197.
- **Bouillaguet, C. et al. (2010). "Fast exhaustive search for polynomial systems in F_2."** CHES 2010. FES.
- **Joux, A.; Vitse, V. (2011). "A variant of the F4 algorithm."** CT-RSA 2011, LNCS 6558: 356–375.
- **Joux, A.; Vitse, V. (2012). "Cover and decomposition index calculus on elliptic curves."** EUROCRYPT 2012, LNCS 7237: 9–26.
  Practical cover/decomposition attacks; 149-bit ECDLP over F_{p^6} (oracle-assisted static-DH setting) — the largest "algebraic" ECDLP computation, on an extension field.
- **Trimoska, M.; Ionica, S.; Dequen, G. (2020). "Time-memory trade-offs for the ECDLP via SAT solvers (WDSat)."** AFRICACRYPT 2020; PMC7334981.
  SAT-based point decomposition: up to 300×/1700× faster than Gröbner on PDP instances — **but the paper's own conclusion is that index calculus remains impractical versus parallel collision search even for prime-degree extension fields**, let alone prime fields.
- **Sparse linear algebra cost model:** Wiedemann/Lanczos Õ(n·weight) vs dense ω ≈ 2.37 — matters for crossbred-style linearization cost accounting (see Gorla–Massierer timings discussion).

**Verdict (prime-field F_p):** Well-covered as solver technology. No solver advance changes the fact that prime-field decomposition systems are dense/high-degree and not known to be constructible efficiently at all; solver improvements are LITERATURE-ADJACENT inputs, not novelty, for any ECDLP mechanism claim.

---

## 6. Isogeny-based transfers, Kani correspondence, and the SIDH attacks — do they transfer to prime-field ECDLP?

Framing: the 2022 SIDH attacks broke isogeny-based crypto using higher-dimensional isogenies (Kani's reducibility theorem). Whether this machinery yields any handle on ordinary ECDLP is an explicit question in this search.

- **Kani, E. (1997). "The number of curves of genus two with elliptic differentials."** *J. Reine Angew. Math.* 485: 93–121.
  Reducibility criterion for products of elliptic curves inside genus-2 Jacobians; the mathematical engine later used by Smith and by the SIDH attacks.
- **Smith, B. (2008/2009). "Isogenies and the discrete logarithm problem in Jacobians of genus 3 hyperelliptic curves."** EUROCRYPT 2008, LNCS 4965: 163–180; journal version *J. Cryptology* 22(4): 505–529 (2009); arXiv:0806.2995; thesis "Explicit endomorphisms and correspondences" (Sydney, 2005).
  **The one true "isogenies for DLP" result:** (2,2,2)-isogenies move the DLP from ~18.57% of hyperelliptic genus-3 Jacobians into non-hyperelliptic genus-3 Jacobians, where Diem–Thomé index calculus gives Õ(q^{4/3}). Genus ≥ 2 only — no elliptic-curve application.
- **Castryck, W.; Decru, T. (2022). "An efficient key recovery attack on SIDH."** IACR ePrint 2022/975; EUROCRYPT 2023.
  Breaks SIKE: SIKEp434 in ~1 hour on one core. Requires: known isogeny degree (smooth A + B), small non-scalar endomorphisms on the starting curve, and **images of a large torsion subgroup under the secret isogeny**.
- **Maino, L.; Martindale, C. (2022).** ePrint 2022/1026. Removes the special-starting-curve requirement (arbitrary start; subexponential, polynomial when End(E_0) is known, under GRH).
- **Robert, D. (2022/2023). "Breaking SIDH in polynomial time."** ePrint 2022/1038; EUROCRYPT 2023, LNCS 14008: 472–503.
  Dimension-8 isogenies (Kani in higher dimension) give a *proven* polynomial-time attack on all of SIDH, no heuristics.
- **Maino, L.; Martindale, C.; Panny, L.; Pope, G.; Wesolowski, B. (2023). "A Direct Key Recovery Attack on SIDH."** EUROCRYPT 2023.
  Practical key recovery for SIKE parameters. Explicit scope statement: the attack *"has no effect on isogeny-based cryptosystems that do not publish images of points under a secret isogeny, such as CSIDH, CSIFiSh, and SQISign."*
- **Galbraith, S. D. (2022). ellipticnews blog, August 2022.**
  **The critical explicit statement on ECDLP transfer:** *"Does it break ECC? No. The attack assumes the degree of the isogeny is known, and that is exactly the secret key in ECC. There is no particular reason to think attacks on SIDH lead to attacks on ECC."* Also: SIDH is broken "by using knowledge of exact images of torsion points under a secret isogeny" — data that an ECDLP instance does not provide.
- **Galbraith, S. D.; Petit, C.; Shani, B.; Ti, Y. B. (GPST) (2016).** ASIACRYPT 2016. Adaptive attack on SIDH using torsion-point images — context for why published torsion images are dangerous *in isogeny protocols*.
- **Robert, D. (2022).** ePrint 2022/1704 (applications of higher-dimensional isogenies to elliptic curves — endomorphism ring computation etc.); ePrint 2022/1068 (polylog isogeny evaluation). Algorithmic fall-out, none aimed at ECDLP.
- **Page, A.; Robert, D. (2023). "Clapoti(s)."** ePrint 2023/1766. Polynomial-time evaluation of class-group actions; CSIDH-side, not ECDLP.
- **Childs, A.; Jao, D.; Soukharev, V. (2014).** *J. Math. Cryptol.* Quantum subexponential (Kuperberg) attack on CRS/CSIDH-style group actions — isogeny-group-action specific, not ECDLP.

**Verdict (prime-field F_p):** Well-covered, and the answer is explicitly **no transfer**. The SIDH-attack ingredients (known smooth isogeny degree, auxiliary torsion images, special endomorphisms, Kani gluing into higher-dimensional abelian varieties) are exactly the data ECDLP withholds. Expert statements on the record (Galbraith; Maino–Martindale–Panny–Pope–Wesolowski) say the attacks do not affect ECC. A claim that Kani/higher-dimensional-isogeny techniques speed up ordinary prime-field ECDLP therefore **contradicts published expert assessment** unless it supplies a genuinely new ingredient (e.g., a way to obtain torsion-image-like data from a DLP instance) — that ingredient itself would be the novelty claim to scrutinize.

---

## 7. Endomorphisms, GLV/GLS, and automorphism-accelerated rho

Framing: efficiently computable endomorphisms speed up *scalar multiplication* (GLV/GLS) and give rho a constant-factor orbit speedup; the question is whether anything beyond √m constants exists.

- **Gallant, R.; Lambert, R.; Vanstone, S. (2001). "Faster point multiplication on elliptic curves with efficient endomorphisms."** CRYPTO 2001, LNCS 2139: 190–206.
  GLV: decompose scalars via an efficient endomorphism (e.g., secp256k1's λ); 2-dimensional decomposition with max|k_i| ≤ C√n. Speeds up the *forward* map only.
- **Galbraith, S. D.; Lin, X.; Scott, M. (2009/2011). "Endomorphisms for faster elliptic curve cryptography on a large class of curves."** EUROCRYPT 2009; *J. Cryptology* 24(3): 446–469 (2011).
  GLS: GLV-style decomposition using the twist over F_{p²}. Again a scalar-multiplication technique.
- **Longa, P.; Sica, F. (2012). "Four-dimensional Gallant–Lambert–Vanstone scalar multiplication."** ASIACRYPT 2012; arXiv:1106.5149. 4-GLV; forward map only.
- **Duursma–Gaudry–Morain 1999** (see §1): the *only* ECDLP consequence of endomorphisms — an automorphism of order m gives rho a √m speedup.
- **Consequences for prime-field curves (standard fact, assembled from the above):** over F_p of large characteristic, j ≠ 0, 1728 → Aut(E) = {±1} → max speedup √2; j = 1728 → |Aut| = 4 → speedup 2; j = 0 → |Aut| = 6 → speedup √6 (e.g., secp256k1). Frobenius-based √(2n) requires extension fields (Koblitz curves). GLV endomorphisms are not automorphisms (degree > 1) and do not enlarge the usable orbit beyond this.
- **Bernstein, D. J.; Lange, T. (2012). "Two grumpy giants and a baby."** BSGS-in-interval variants (verified only at citation level; include with care).

**Verdict (prime-field F_p):** Well-covered and closed: endomorphisms buy at most small constants (√2 general; 2 and √6 for special j-invariants). No subexponential mechanism. A claim exploiting "efficiently computable endomorphisms" beyond the automorphism orbit should be classified LITERATURE-ADJACENT unless it shows a new orbit structure.

---

## 8. Arithmetic dynamics, elliptic divisibility sequences, and elliptic nets

Framing: ECDLP has equivalent reformulations in the language of EDS/elliptic nets; the literature shows equivalence, not speedup.

- **Shipsey, R. (2000). "Elliptic divisibility sequences."** PhD thesis, Goldsmiths College, University of London.
  Double-and-add arithmetic for EDS; an ECDLP-to-EDS reduction when #E(F_q) = q − 1 (MOV-like special case).
- **Lauter, K. E.; Stange, K. E. (2008). "The elliptic curve discrete logarithm problem and equivalent hard problems for elliptic divisibility sequences."** SAC 2008, LNCS 5381: 309–327; ePrint 2008/099; arXiv:0803.0728.
  Defines EDS Association / EDS Residue / EDS Discrete Log; each is solvable in subexponential time **if and only if** ECDLP is; relates EDS Association to the Tate pairing and hence to MOV/Frey–Rück/Shipsey. This is an *equivalence of difficulty* result — no new algorithmic lever.
- **Stange, K. E. (2007). "The Tate pairing via elliptic nets."** Pairing 2007, LNCS 4575: 329–348.
- **Stange, K. E. (2011). "Elliptic nets and elliptic curves."** *Algebra & Number Theory* 5(2): 197–229; arXiv:0710.1316.
  General theory of elliptic nets (rank-1 nets = EDS). Computational tool, not a DLP speedup.
- **Everest, G.; Miller, V.; Stephens, N. (~2003).** Division-polynomial alternative to MOV when #E(F_q) = q − 1. (Citation seen only in reference lists; details unverified.)

**Verdict (prime-field F_p):** Covered. EDS/net reformulations are provably as hard as ECDLP; they recast rather than accelerate. No spectral/transfer-operator/dynamical-systems cryptanalysis of ECDLP was found anywhere in this search — see Gaps.

---

## 9. Tensor rank, tensor networks, and treewidth-based methods

Framing: could multilinear-algebra structure (tensor rank of the group law, tensor-network contraction, treewidth/separator-rank of constraint graphs) accelerate solving summation-polynomial or Weil-descent systems?

- **Håstad, J. (1990). "Tensor rank is NP-complete."** *Journal of Algorithms* 11: 644–654.
  Tensor rank is NP-complete over finite fields — the in-principle obstacle to rank-based shortcuts.
- **Chudnovsky-line bilinear complexity of multiplication in F_{q^n}:** Ballet, S.; Pieltant, J.; Randriambololona, H. — "On the tensor rank of multiplication in finite extensions of finite fields and related issues in algebraic geometry" (and predecessors): symmetric elliptic Chudnovsky-type algorithms achieve O(n·(2q)^{log*_q(n)}).
  **Adjacent but different problem:** this is the tensor rank of the *multiplication map* of an extension field (algorithm design), not a cryptanalytic tool for DLP systems.
- **arXiv:2603.07280 (2026).** Automated/computer-assisted lower bounds for bilinear complexity over F_2/F_3 (e.g., 3×3 matrix multiplication tensor rank ≥ 20, improving Bläser 2003's ≥ 19).
- **Alexeev, B.; Forbes, M. A.; Tsimerman, J. (2011).** 3n − O(log n) explicit tensor lower bounds.
- **Landsberg, J. M.; Ottaviani, G.** Border-rank ≥ 2n² − n for matrix multiplication.
- **Search result for cryptanalytic use:** **Nothing found** applying tensor rank, tensor-network contraction, treewidth, or separator-rank analysis to Semaev summation systems, Weil-descent systems, or ECDLP generally. Generic treewidth-in-SAT/CSP literature exists but was not covered by this search.

**Verdict (prime-field F_p):** **Gap.** No prior art located connecting tensor-rank/tensor-network/treewidth methods to ECDLP or to summation-polynomial solving. A proposal here is a NOVELTY-UNVERIFIED / POSSIBLY NOVEL candidate — with the caveat that absence-of-evidence is from a targeted (not exhaustive) search, and generic CSP-treewidth literature should be skimmed before any POSSIBLY NOVEL classification is finalized.

---

## 10. Tropical methods, Newton polytopes / BKK bounds, jets, and p-adic lifts

Framing: several geometric/analytic toolkits (mixed volumes, tropical algebra, jet schemes, canonical lifts) could conceivably bear on polynomial systems from ECDLP; what exists is largely on special curves or point counting.

- **Smart, N. P. (1999). "The discrete logarithm problem on elliptic curves of trace one."** *Journal of Cryptology* 12(3): 193–196.
  p-adic logarithm attack on anomalous curves (#E(F_p) = p): polynomial time. **Special curve class only.**
- **Satoh, T.; Araki, K. (1998).** *Commentarii Mathematici Universitatis Sancti Pauli* 47(1): 81–92; and **Semaev, I. (1998).** *Mathematics of Computation* — the other two anomalous-curve attack papers.
- **Satoh, T. (2000). "The canonical lift of an ordinary elliptic curve over a finite field and its point counting."** *J. Ramanujan Math. Soc.* 15(4): 247–270.
  Canonical lifts for **point counting** — not a DLP algorithm.
- **Satoh, T.; Skjernaa, B.; Taguchi, Y. (2003).** *Finite Fields and Their Applications* 9: 89–101. AGM point counting; **Mestre, J.-F. (2001)** AGM; **Kohel, D. (2003)** ASIACRYPT 2003, LNCS 2894 (AGM via X_0(N)); medium-characteristic canonical lift Õ(p^{0.5}nm) (hal-03702658).
  **Explicitly checked:** no DLP application of AGM/canonical-lift machinery was found; all uses are point counting.
- **Grigoriev, D.; Shpilrain, V. (2014). "Tropical cryptography."** *Groups, Complexity, Cryptology* 6(1).
  Tropical (min-plus) algebra as a **platform for constructing protocols**, not as cryptanalysis.
- **Kotov, M.; Ushakov, A.** Cryptanalysis of the tropical protocol schemes — again protocols built *on* tropical algebra.
- **Chen, Y.; Grigoriev, D.; Shpilrain, V. (2023). "Tropical cryptography III: digital signatures."** arXiv:2309.11256.
  NP-hardness of tropical polynomial factorization as a hardness assumption. Still construction-side; **no use of tropical methods to attack finite-field systems or ECDLP was found.**
- **BKK theory:** Bernstein, D. N. (1975); Kushnirenko, A. G. (1976); Khovanskii, A. G. (1977): mixed-volume (BKK) bounds on the number of torus roots of sparse polynomial systems.
- **Canny, J.; Emiris, I. (2000).** *JACM* — sparse resultant algorithms.
- **Bender, M. R.; Faugère, J.-C.; Tsigaridas, E. (2019). "Gröbner bases over semigroup algebras."** arXiv:1902.00208.
  Gröbner complexity driven by Newton polytopes; cryptography listed among motivating application classes — but no application to Semaev/Weil-descent systems was found.
- **Rojas, J. M.** — degenerate sparse systems / k-rational points; Diem has suggested Rojas-type algorithms for related point-finding (citation-level only).
- **Jets/arcs:** **No Hasse-derivative, jet-scheme, or arc-space cryptanalysis** of ECDLP or summation systems was found.

**Verdict (prime-field F_p):** Partial coverage with real gaps. p-adic methods solve only anomalous curves (poly-time, but #E = p is excluded by "ordinary"); lift/AGM machinery is point-counting-only. **No BKK/mixed-volume/Newton-polytope analysis of Semaev systems was found** — noteworthy because symmetrized summation polynomials are extremely sparse, making BKK-type bounds a plausible unexplored angle. Tropical methods exist only as protocol platforms. These are NOVELTY-UNVERIFIED candidate directions.

---

## 11. Incidence geometry over finite fields

Framing: incidence bounds over F_p (Szemerédi–Trotter-type, point–plane, restriction theory) could conceivably constrain or accelerate search/decomposition structures; what exists is pure math with no cryptanalytic application found.

- **Pach, J.; Sharir, M. (1998). "On the number of incidences between points and curves."** *Combinatorics, Probability and Computing* 7: 121–127.
- **Helfgott, H. A.; Rudnev, M. (2011). "An explicit incidence theorem in F_p."** *Mathematika* 57(1): 135–145.
  Explicit Szemerédi–Trotter-type bound over prime fields.
- **Rudnev, M. (2018). "On the number of incidences between points and planes in three dimensions."** *Combinatorica* 38: 219–238.
  Point–plane incidences I ≲ |P|^{1/2}|Π| + k|Π| for |P| = O(p²), k = max collinear points; de Zeeuw, F. (arXiv:1612.02719) gives a short proof via the Klein quadric.
- **Jones, T. G. F. (2012/2016).** *European Journal of Combinatorics* 52: 136–145; CoRR 1206.4517. Beck-type results over F_q.
- **Iosevich, A.; Pham, T.; et al. (2023).** arXiv:2303.00330. Improved point–line incidence bounds over arbitrary F_q (their own note: Rudnev's prime-field bound remains better in its regime).
- **Koh, D.; Lee, S.; Pham, T. (2022).** *IMRN* 2022(21): 17079–17111. Cone restriction estimates → point–sphere incidences.
- **Shkredov, I. D. (2020). "On asymptotic formulae in some sum-product questions."** *Journal of Number Theory* 220: 182–211. Modular hyperbolas / Kloosterman-sum incidence-flavored number theory over F_p — the closest "F_p structure" work with arithmetic content.
- **Output-sensitive incidence reporting:** Agarwal, P. K.; Sharir, M. — point–circle reporting O*(m^{2/3}n^{2/3} + m^{6/11}n^{9/11} + m + n); Aiger, D.; Kedem, K. (arXiv:2005.08193; LIPIcs ESA 2017: 5) — approximate output-sensitive incidence reporting.
- **Search result for cryptanalytic use:** **None found.** No application of finite-field incidence theorems or incidence-reporting algorithms to ECDLP, summation systems, rho analysis, or factor-base construction was located.

**Verdict (prime-field F_p):** **Gap.** Rich, mature finite-field incidence theory with zero located cryptanalytic usage. Any mechanism claiming to exploit incidence bounds for ECDLP is NOVELTY-UNVERIFIED pending a deeper combinatorics-literature pass.

---

## 12. Noncommutative hidden subgroup problems, group algebra, and representation theory

Framing: DLP in F_p* reduces to the dihedral HSP; representation-theoretic methods give *quantum* subexponential algorithms. Whether classical group-algebra/representation methods yield anything for ECDLP is the question.

- **Shor, P. W. (1994/1997). "Algorithms for quantum computation: discrete logarithms and factoring."** FOCS 1994; *SIAM Journal on Computing* 26: 1484–1509 (1997).
  Polynomial-time quantum DLP in any group with efficient group arithmetic — including E(F_p) (abelian HSP).
- **Ettinger, M.; Høyer, P. (2000). "On quantum algorithms for noncommutative hidden subgroups."** *Advances in Applied Mathematics* 25(3): 239–251; quant-ph/9807029.
  **The precise requested statement:** the discrete logarithm problem (in F_p*) reduces to the dihedral hidden subgroup problem in D_N; their framework gives polynomial *query* complexity but exponential post-processing.
- **Ettinger, M.; Høyer, P.; Knill, E. (2004).** *Information Processing Letters* 91(1); quant-ph/0401083.
  Polynomial quantum query complexity for the general (arbitrary nonabelian) HSP; processing may remain exponential.
- **Kuperberg, G. (2005). "A subexponential-time quantum algorithm for the dihedral hidden subgroup problem."** *SIAM Journal on Computing* 35(1): 170–188; quant-ph/0302112.
  DHSP in 2^{O(√(log N))} time and space.
- **Regev, O. (2004).** quant-ph/0406151. Poly-space variant of Kuperberg. **Regev, O. (2004).** *SIAM J. Comput.* 33(3): 738–760 — unique-SVP reduces to DHSP.
- **Bacon, D.; Childs, A. M.; van Dam, W. (2005/2006).** FOCS 2005; *Chicago Journal of Theoretical Computer Science* 2006. Optimal HSP measurements; DHSP ↔ average-case subset sum via semidirect-product HSP.
- **Kuperberg, G. (2011/2013).** arXiv:1112.3333; TQC 2013. Another 2^{O(√(log N))} DHSP algorithm with O(log N) quantum space.
- **Kobayashi, H.; Le Gall, F. (2005).** *IPSJ Journal* 46(10). DHSP survey. **Childs, A. M. — HSP lecture notes** (survey; arXiv identifier cited as 1008.0010 in secondary lists — unverified).
- **Moore, C.; Young, S. (2022).** Polynomial-time algorithm for D_{2^n} only (special case).

**Verdict (prime-field F_p):** Covered. The DLP→DHSP route yields only a *quantum* subexponential 2^{O(√log N)} algorithm — already dominated by Shor's polynomial algorithm, which applies directly to E(F_p) since the group is abelian. **No classical representation-theoretic or group-algebra algorithm for DLP/ECDLP was found**, and nothing HSP-flavored adds leverage for ECDLP beyond Shor. Path-algebra/correspondence-algebra cryptanalysis: not found (gap, but adjacent to a closed verdict).

---

## 13. Recent (2023–2026) claimed breakthroughs and their status

Framing: any recent claim of beating rho on ECDLP must be located and assessed.

- **Quantum-annealing ECDLP line (all toy-scale):**
  - Wroński, M. (2021). ICCS 2021, LNCS 12742: 114–124 — index calculus via quantum annealing.
  - Wroński, M. (2022). ICCS 2022, LNCS 13350: 92–106 — DLP over prime fields via QA.
  - Żołnierczyk, P.; Wroński, M. (2023). ICCS 2023, LNCS 14073: 296–311 — B-smooth QA decomposition.
  - Wroński, M.; Burek, E.; Dzierzkowski, G.; Żołnierczyk, P. (2024). *Journal of Telecommunications and Information Technology* 2024(1): 75–82 — direct ECDLP→QUBO transformation.
  - Wroński, M.; Dzierzkowski, G. (2024). *Quantum Information & Computation* 24(7&8): 0541–0564.
  - **Dzierzkowski, G. (2024). arXiv:2410.08725** — generalized ECDLP→QUBO for arbitrary curve models; and **Dzierzkowski, G. (2024). *Tatra Mountains Mathematical Publications*** — QA + index calculus on a twisted Edwards curve over F_1021, group order 4·241; the authors themselves call this the largest ECDLP solved by hybrid quantum-classical means — a **10-bit field**, which Pollard rho solves instantly. The QA papers themselves admit "determining the full formal complexity requires further research."
- **Machine learning:** Jebrane, A.; et al. (2024). "Elliptic Curve Cryptography with Machine Learning." *MDPI Cryptography* 9(1): 3.
  Survey; ML for key generation/analysis (e.g., GAN-based) — **no cryptanalytic improvement over rho** claimed or shown.
- **Quantum circuit optimization (Shor-side, not new mathematics):**
  - Häner, T.; Roetteler, M.; Svore, K. (2020) — baseline ECDLP Shor resource estimates.
  - **Hu, J.; Zhang, Y.; Zhou, X.; Qu, D. (2025). *Quantum Information Processing* 24: 311** — Ed25519 Shor circuit with −75% T-count / −87% T-depth vs Häner et al. Engineering improvement of a known polynomial quantum algorithm.
  - Regev, O. (2023) factoring circuits; Ragavan, S.; Vaikuntanathan, V.; Ekerå, M.; Gärtner, J. — quantum DLP/factoring optimizations. None affects classical ECDLP.
- **Theory:** Corrigan-Gibbs, Henzinger, Wu (2026), ePrint 2026/384 — see §1; the strongest recent *defensive* result (lower bounds against structure exploitation).
- **Side-channel (non-mathematical, noted for completeness):** De Micheli, G.; Heninger, N.; Shapira, N. (2026). arXiv:2605.16362 — characterizing physical side-channel attacks on ECC. Out of mathematical scope.
- **Surveys corroborating "no breakthrough":**
  - Galbraith, S. D.; Gaudry, P. (2016). DCC 78: 51–72 (hal-01215623) — prime fields unaffected by index calculus.
  - "State-of-the-Art Attacks on ECDLP." *Annals of Emerging Technologies in Computing* 8(4) (2024) — ECDLP instances "continue to withstand all known attacks."
  - "A Brief Survey of ECDLP Solvers" (2024, hiepbla96/github) — rho remains best for prime fields.
- **Flagged weak item:** a 2022 IOP conference paper on "Projective ECDLP" claims to beat rho via Semaev polynomials only for key sizes n ≤ ~64 bits (toy regime); its own tables show it loses above that. Also an anecdotal 114-bit solve claim (2017) circulates without a primary publication — treat as unverified.

**Verdict (prime-field F_p):** Covered. No 2023–2026 classical sub-√n ECDLP claim was located that survives even the papers' own stated limitations; the recent classical literature is surveys, toy quantum-annealing experiments, ML-adjacent work, and quantum-circuit engineering. The SGGM 2026 result *raises* the bar for new classical claims.

---

## Cross-area synthesis

1. **The O(√n) baseline stands everywhere in scope.** For ordinary prime-field curves: generic lower bound Ω(√q) (Shoup; Nechaev); best constants rho+negation √(πn/4) with automorphism constants ≤ √2/2/√6 (§1, §7); largest public computation 112 bits (2012).
2. **Every subexponential ECDLP mechanism in the literature requires structure prime fields lack:** a subfield (Weil descent, GHS, trace-zero — §4), higher genus (Jacobian index calculus — §3), a global-field lift with smoothness (classical index calculus — §3), anomalous order #E = p (p-adic — §10), or protocol-provided data like torsion images and known isogeny degree (SIDH attacks — §6).
3. **Prime-field algebraic attacks have been explicitly tried and published** (Petit–Kosters–Messeng PKC 2016; Amadori–Pintore–Sala 2018; McGuire–Mueller 2017) and all are outperformed by generic algorithms at practical sizes — the authors say so themselves. "Apply Semaev polynomials to prime fields" is therefore LITERATURE-ADJACENT, not novel.
4. **The FFD/last-fall-degree line (Kosters–Yeo; Huang–Kosters–Yeo; Huang–Kosters–Yang–Yeo; Kousidis–Wiemers) casts doubt even on the binary-field subexponentiality heuristics** — the theoretical wind is blowing toward *stronger* confidence in rho's dominance, not weaker.
5. **The 2026 SGGM lower bound (ePrint 2026/384) explicitly covers elliptic-curve-point structure**, directly constraining any factor-base-style mechanism over F_p: exploiting structure of a δ-fraction of points costs Ω(min(√q, 1/δ)).
6. **SIDH/Kani techniques do not transfer** — explicitly stated by Galbraith and by Maino–Martindale–Panny–Pope–Wesolowski; the attack inputs (torsion images, known degree, special endomorphisms) are absent from ECDLP instances.

## Gaps with novelty relevance (NOVELTY-UNVERIFIED candidates)

- **§9 Tensor rank / tensor networks / treewidth:** no prior art found connecting these to summation systems or ECDLP. Closest existing body: bilinear complexity of extension-field multiplication (Chudnovsky-type) — a different problem. Residual check needed: generic treewidth-SAT/CSP literature.
- **§10 BKK/mixed-volume/Newton-polytope analysis of Semaev systems:** not found; plausible given the sparsity of symmetrized summation polynomials. Tropical methods exist only as protocol-construction platforms; no tropical *cryptanalysis* of finite-field systems found. No jet/arc-space cryptanalysis found.
- **§11 Incidence geometry over F_p:** mature theory, zero located cryptanalytic applications.
- **§8 Dynamical/spectral methods:** only equivalence results (EDS/nets); no transfer-operator or spectral cryptanalysis found.
- Note: absence-of-evidence here comes from ~34 targeted searches, not an exhaustive database crawl; ePrint 2025/2026 listing was probed via targeted queries, not a full skim.

## Residual verification notes

- Identifier-level unverified (from reference lists only): Nechaev page numbers; Everest–Miller–Stephens (~2003) details; Childs HSP-survey arXiv ID; Kohel ASIACRYPT 2003 pages; Bernstein–Lange "Two grumpy giants"; Thériault/Diem ANTS page ranges as cited in secondary lists; anecdotal 114-bit record; 2024 EasyChair anti-Petit preprint (low credibility).
- The 2022 "Projective ECDLP" IOP paper and the MDPI ML survey were assessed from abstracts/tables, not full text.
