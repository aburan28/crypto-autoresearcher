#set page(paper: "a4", margin: (x: 1.6cm, y: 1.5cm), footer: context align(right, text(size: 8pt, counter(page).display("1"))))
#set text(font: "Liberation Sans", size: 9pt, lang: "en", ligatures: false)
#show raw: set text(font: "Liberation Mono")
#set par(justify: false, leading: 0.55em)
#set heading(numbering: none)
#show heading: set block(above: 0.8em, below: 0.4em)
#heading(level: 1)[#text("F6: explicit interval and digit-box lattice screen")]
#figure(image("diagram.svg", width: 100%, height: 5.4cm, fit: "contain"), caption: [Editable study diagram; exact scope and evidence paths appear in the report.])


#text("25 October 2026. TASK-20261025-f439ca. This is exact implementation validation and a sufficient-bound theory screen, with constructed public points on published P-256. No performance trial, attack-cost claim, official state transition, or general multivariate solver theorem is asserted.")
#parbreak()

#heading(level: 2)[#text("Observations and reproducibility")]

#text("From the repository root:")
#parbreak()

#text(size: 7.2pt)[#raw("python3 research/p256_factor_base_parallel_20261025/tracks/f6/check_bounds.py\npython3 research/p256_factor_base_parallel_20261025/tracks/f6/verify_artifacts.py", block: true)]

#text("The first command checks actual-field f3 and f4 relation witnesses, 28 rectangular parameter cases, nine four-digit parameter cases, and one nine-row lattice. Python and SymPy versions, exact points and integer parameters are in receipt.json (receipt.json). The independent implementation recheck of emitted artifacts is in verification.json (verification.json); this is a same-session software cross-check, not an independent research review.")
#parbreak()

#text("The exact rectangular sufficient bound admits B=2^32 for the best tested two-unknown cases (D=12 through 16). No B>=1 passes the tested three-unknown cases D=4 through 16. The nine digit-box cases D=4 through 12 also give no B>=1 under the stated sufficient bound. These are certificate-window observations, not failed searches for roots.")
#parbreak()

#text("Even a half-target coverage counting prerequisite needs width B at least 170141183440662191106579983831721312255 for two summands, or 35148224029723583543551324 for three. These are necessary bounds, not success estimates. They count every possible signed point, allow repeated summands, and ignore collisions, so are generous to the construction.")
#parbreak()

#heading(level: 2)[#text("Explicit polynomials and triangular shifts")]

#text("Use E: y^2=x^3+a x+b over p=2^256-2^224+2^192+2^96-1, a=-3, and the published b,r from parameters.py (../../baseline/parameters.py). The group order and primality are inherited published inputs, not freshly certified here. The checked subgroup witness satisfies [r]P=O.")
#parbreak()

#text("For a fixed target abscissa t, the two-unknown polynomial is")
#parbreak()

#text("f3(x,y,t)=(x-y)^2 t^2-2((x+y)(xy+a)+2b)t+(xy-a)^2-4b(x+y).")
#parbreak()

#text("It has individual degrees (2,2) and leading product x^2 y^2 with coefficient 1. The three-unknown polynomial is resultant_z(f3(x,y,z),f3(z,w,t)); the executable actual-P-256 expansion has 125 terms, individual degrees (4,4,4), and monic leading product x^4 y^4 w^4. Its full coefficients are retained. An interval offset replaces each coordinate by c_i+u_i; this preserves the individual degree bounds and monic leading product. Nonleading coefficients may be reduced modulo p before taking integer lifts, since the modular roots are unchanged. Summation-polynomial vanishing alone does not establish a rational signed-point decomposition; witnesses here are separately checked point sums.")
#parbreak()

#text("Let s=2,e=2 for f3, or s=3,e=4 for f4. For every alpha in {0,...,D}^s choose")
#parbreak()

#text("k(alpha)=min(m, floor(alpha_1/e),...,floor(alpha_s/e)), g_alpha=p^(m-k) x^(alpha-k(e,...,e)) f^k.")
#parbreak()

#text("All coefficients are integers. At any modular root, every g_alpha is divisible by p^m. Because every exponent of f is coordinatewise <=(e,...,e), the shifted polynomials stay in the same box. In graded lexicographic order their leading monomials are distinct x^alpha. Scaling columns by B^|alpha| yields a square triangular integer lattice with")
#parbreak()

#text("n=(D+1)^s, K=sum_{k=1}^{min(m,floor(D/e))}(D-ek+1)^s, det(L)=p^(mn-K) B^(s D n/2).")
#parbreak()

#text("This determinant is exact, not a heuristic volume estimate. Increasing m beyond floor(D/e) cannot improve the cancelled sufficient inequality for this family.")
#parbreak()

#heading(level: 2)[#text("Integer zero lifting and what it does not prove")]

#text("For a reduced polynomial h and |u_i|<=B, Cauchy-Schwarz gives")
#parbreak()

#text("|h(u)| <= sqrt(n) ||h(Bx)||_2.")
#parbreak()

#text("If the right side is strictly below p^m, divisibility proves h(u)=0 over the integers. For delta=3/4, the usual first-vector LLL norm bound is 2^((n-1)/4) det(L)^(1/n). Combining and raising to the power 4n gives the exact sufficient check")
#parbreak()

#text("n^(2n) * 2^(n(n-1)) * B^(2 s D n) < p^(4K).")
#parbreak()

#text("The code checks this inequality using integer arithmetic, including strictness. It does not apply a univariate small-root theorem. The inequality guarantees at least one short lifted polynomial; enough algebraically independent polynomials, a zero-dimensional ideal, extraction cost, exceptional components, and completeness must be established separately. Failure of this sufficient inequality does not show that LLL fails, that roots do not exist, or that another shift family is impossible.")
#parbreak()

#text("For the present family, monotonicity bounds")
#parbreak()

#text("K <= integral_0^(D/e) (D+1-et)^s dt < (D+1)^(s+1)/(e(s+1)).")
#parbreak()

#text("Thus any positive sufficient window has log_p(B)<2(D+1)/(e s D(s+1)). For D>=e this is <=1/4 for f3 or <=5/96 for f4. D<e has K=0 and cannot meet the strict inequality. The counting-required widths exceed p^(1/4) and p^(5/96), respectively, verified with exact powers. Consequently this particular guaranteed interval window never intersects the half-target counting range, for any D,m. This concerns a sufficient-bound construction; it is no general impossibility statement. Its large-D determinant exponents before the LLL factor are 1/6 and 1/24.")
#parbreak()

#text("The coverage bound uses an interval {c,...,c+B} with at most B+1 distinct x-coordinates. Write M<=B+1 for the canonical x-base count, and n_signed<=2M<=2(B+1) for signed points. At most binomial(n_signed+s-1,s) unordered multisets can sum to targets. A uniform nonzero target on a group of order r therefore has coverage <= that count/(r-1), capped at 1. Half coverage requires 2*binomial(2(B+1)+s-1,s)>=r-1. No equidistribution or independence assumption is needed for this upper bound. In the coordinator's convention M=B+1 is the most generous x-base capacity of this interval; actual lift density may reduce M. The reported log2(B)~127 for two summands and ~84.86 for three summands are necessary capacity thresholds, never sufficient success conditions.")
#parbreak()

#heading(level: 2)[#text("Two-digit boxes and bounded lattice correctness")]

#text("For a concrete alternative write x=u0+2^128 u1 and y=v0+2^128 v1, with 0<=each digit<=B<2^128. There are at most (B+1)^2 abscissas per coordinate. Substitution in f3 gives a four-variable degree-4 polynomial with graded-lex leading monomial u0^2 v0^2 and coefficient 1. Use the full total-degree simplex |alpha|<=D, evec=(2,0,2,0), and the same k/divisibility construction. Here")
#parbreak()

#text("n=binomial(D+4,4), A=binomial(D+4,5), K=sum_{k=1}^{floor(D/4)} binomial(D-4k+4,4), det(L)=p^(mn-K) B^(4A), n^(2n) 2^(n(n-1)) B^(16A) < p^(4K).")
#parbreak()

#text("Terms remain in the simplex and are triangular in graded lex order even though evec has zero entries. Nine exact checks are retained. Asymptotically K/(4A) tends to 1/16; half-target counting needs digit width approximately p^(1/4). The radix factors affect actual vector quality and coefficient heights; determinant triangularity does not erase them from actual reduction or root extraction. General digit decompositions remain unassessed.")
#parbreak()

#text("The bounded lattice example uses actual P-256 P and 17P, constructs T=P+17P, and deliberately picks offsets P.x-1 and (17P).x-1, giving the known root (1,1). The D=2,m=1,B=2 lattice has nine rows, determinant p^8*2^18, and eight LLL vectors satisfying the exact zero-lifting norm bound. Their rational integer-polynomial Groebner basis is [x-1,y-1]. A separate verifier checks that the emitted LLL transform is integral unimodular, the determinant is preserved, each lifted polynomial vanishes at (1,1), and the resulting ideal is zero-dimensional. The offsets were derived from the known solution. This validates lattice construction and zero lifting, and supplies no evidence for solving ordinary targets or scaling.")
#parbreak()

#heading(level: 2)[#text("Scope, failures, and decisive next step")]

#text("Initial reads of two sparse profile references failed; git confirmed tracked blobs, and a subsequent read with enabled network succeeded. The initial promisor fetch failed because the default sandbox could not connect to proxy port 8080. No scientific command failed. During final validation a yielded F6 process was still running when F8 artifact verification started, briefly exceeding the handoff's one-process concurrency limit. The checks were subsequently rerun sequentially; this does not erase the procedural deviation. No timing or performance result was collected. Exact commands and terminal states are retained in commands.log (commands.log).")
#parbreak()

#text("The specific unresolved problem is a sufficient multivariate construction whose guaranteed root window covers a useful ordinary-target base, with certified zero-dimensional extraction and total cost. The rectangular and fixed two-digit constructions here do not provide it. To change that conclusion for this mechanism, supply alternative explicit shifts, an exact rank/determinant or norm certificate at the counting-required widths, and an independent-component or certified-extraction argument without solution-derived offsets. A bounded proof-of-concept passing those checks would justify designing an admitted trial; a short vector by itself would leave extraction and success coverage unresolved.")
#parbreak()

#text("Sources: internally derived algebra in the linked code and certificates; published constants inherited through the committed baseline. Repository endo/audit profiles were consulted for scope. No external small-root citation is being used as proof. The local diagram.svg (diagram.svg) is the new editable visual; shared canonical graphs are outside this handoff and were not changed. Root renders the aggregate PDF.")
#parbreak()
