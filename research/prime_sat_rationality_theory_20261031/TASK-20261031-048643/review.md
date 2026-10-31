# Independent mathematical source audit — TASK-20261031-048643

The seven submitted joints **hold on their exact stated hypotheses**. The review also finds one false ancillary description: the two guard square-root choices do not always correspond to a *balanced* signed divisor. A concrete valid chart below has multiplicities 4 and 1. This correction does not change the existential predicate or the fiber count; recovery must retain the residual-ratio rule already required by the signed-recovery source.

This is an adversarial audit of deliberately supplied producer proofs, with independent mathematical checks and counterexamples. It is not blind proof reconstruction, a software review, an executed experiment, or an official scientific decision. No tests, solver calls, software suites, benchmarks, cloud jobs, or Git commands were run.

| Assigned joint | Verdict | Exact scope |
|---|---|---|
| common_root_localization | holds | Rational-point support for a supplied nonzero chart with verified split norm |
| slack_projection | holds | Existential projection over F_p and exact auxiliary fibers |
| guard_projection | holds | All five equations, implied Boolean guard, exact fibers; ancillary balanced-divisor wording corrected below |
| nilpotent_square | holds | Split monic U, all multiplicities, k>=p, separate U=1 case |
| fiber_count | holds | Fixed U, all roots valid, 2^q p^(k-r), with uniquely determined lift intermediates |
| quadratic_circuit | holds | The displayed, unsimplified field-level layouts for k=0,...,5 |
| complete_integration_boundary | holds | Necessary complete-stratum, normalized-coefficient projection, and signed-recovery contract for supplied charts |

## Custody, sources, and review boundary

The dispatcher supplied snapshot commit `8c928d45760f7fac9cc0a94cea53157befc32788`, binding `800ed809f6`, release `765880412c`, and reviewer claim `56e3f89a0c`. Those commit/claim identities are dispatcher provenance, not independently authenticated Git facts in this no-Git session. The actual owner/session declared in dispatch are `reviewer-prime-rationality-theory` / `prime-rationality-theory-independent-review-20261031`, epoch 1.

Before reading the mathematical proofs, byte hashes of the 24 files listed by the snapshot receipt were compared with the receipt and all matched. The receipt itself has SHA-256 `69ecb293179bff5ef6a2f7f83d256b6505a84a46369dba66b18e7eccc6535c7f`. Immediately before sealing, all 25 hashes were rechecked and all fifteen canonical source sizes/hashes also matched `source-inputs.json`. The attestation records the exact map. The two principal source-package hashes are:

- `source-package.json`: `5d6b9a1d05ec1daf5f33067f35ad1797fe4100601cc59a73edf10071fb5400c5`.
- `claim-map.md`: `7b35ae612a8424e36d39a4e4fbd83117613b2da6e424425c3562b065ce635f88`.

All fifteen frozen source files were inspected. PDF contents were read by text extraction and SVG contents as source; this reviewer makes no visual-rendering attestation. Scratch-relative references were resolved through the manifest to canonical copies. No mutable scratch draft, later research note, sibling review, prior reviewer attestation, or engine implementation was read. The failed guessed path `agents/reviewer.md` was absent; the available `agents/validator.md` supplies the review-plan and attestation contract. The source-audit handoff governs the narrow write scope and forbids the broader execution/publication actions described by generic review-evidence guidance.

Primary mathematical sources personally retrieved by this reviewer on 2026-10-31 were [Stacks Project Lemma 10.15.4](https://stacks.math.columbia.edu/tag/00DT), for the Chinese remainder theorem, and [Sutherland, MIT 18.782 Lecture 23](https://math.mit.edu/classes/18.782/2023sp/LectureNotes23.pdf), especially Theorem 23.3 and its proof for pole orders/bases, and Theorem 23.16 for the point/divisor-class correspondence. These sources support standard background. The proofs below are this reviewer's checks of the submitted constructions, not results attributed to those sources. No novelty search or novelty verdict is claimed. Citation provenance is `retrieved`, verified by `TASK-20261031-048643`; the frozen repository sources are `internal`.

Throughout, p>3 is prime, E is nonsingular with y^2=f(x)=x^3+a x+b, and every coefficient and witness is in F_p. A supplied chart h=A+B y is nonzero and normalized as specified; its nonzero norm N=A^2-fB^2 and its exact degree, full coefficient identity, splitting, interval constraints, and target conditions are retained. These are hypotheses, not outputs of a rationality block.

## 1. common_root_localization — holds

Source: `sources/signed-recovery/proof.md`, input contract, local-parameter, nonbranch, branch, and gcd-support sections; `sources/conditional-square/proof.md`, lines 7–9. Source paths in this report are relative to `coordination/prime_sat_rationality_theory_20261031/`.

Let alpha be a root of the verified split norm, hence alpha is in F_p. At a nonbranch point, x-alpha is a local parameter: 2 beta is nonzero and y+beta is a unit. At a branch point, nonsingularity gives f'(alpha) nonzero, and x-alpha=y^2/F(x), with F(alpha) nonzero, so y is a parameter and x-alpha has order 2.

If A and B do not both vanish at a nonbranch norm root, B(alpha) cannot vanish: the norm equation would force A(alpha)=0 too. Thus beta=-A(alpha)/B(alpha) is in F_p and beta^2=f(alpha); it is the vanishing sign. If both vanish, factor out (X-alpha)^g, g=min(v_alpha(A),v_alpha(B))>0. This factor contributes g at each nonbranch sign. Consequently both signs occur, and are rational precisely when f(alpha) is a square. If the reduced norm also vanishes, B_0(alpha) is nonzero and its ratio supplies a rational root; the residual multiplicity q=m-2g goes entirely to that sign, since the conjugate residual factor is a unit. If q=0, the multiplicities are exactly g,g. This proves both necessity and sufficiency of the gcd-support test, including unbalanced common roots.

At a branch root the sole geometric point is (alpha,0), already rational. Orders of A and By are 2v_alpha(A) and 2v_alpha(B)+1. Finite orders have different parity, so there is no cancellation. Their minimum is both the local order of h and the X-root multiplicity of N. Repeated roots therefore change multiplicities without changing the support criterion.

With B=0, the convention v(0)=infinity gives g=v(A), m=2g and the nonbranch balanced case. With A=0, away from branch roots the same reasoning gives g=v(B), m=2g; at branch roots the order is 2v(B)+1. A=B=0 is excluded by h nonzero. A constant nonzero gcd has empty support. No argument divides by a multiplicity or uses factorial derivatives, so characteristic-divisible multiplicities cause no failure.

For finite R=(r,s_R), retain cN=(X-r)U and h(-R)=0. Remove exactly one copy of (r,-s_R) after recovering local orders; its presence follows from target vanishing but still needs certificate checking. Since f(r)=s_R^2, a nonsquare common-root pair cannot lie over r. Subtracting this rational point cannot erase any nonrational support. This remains true for a branch target and for r outside the interval; the latter factor must remain in the norm support even if it is absent from U. For R=O there is no finite subtraction.

**Split-norm control.** Over F_5 take f=X^3+X+1 and h=y. The values of f at 0,1,2,3,4 are respectively 1,3,1,1,4, so the cubic has no F_5 root. Its discriminant condition is 4+27=1 mod 5, hence E is nonsingular. Here gcd(0,1)=1, so a gcd-only rationality test is vacuous, yet the zeros of y are nonrational branch points. The missing premise is precisely splitting of N=-f. This is a hand-worked counterexample, not an executed field census.

## 2. slack_projection — holds

Source: `sources/conditional-square/proof.md`, lines 13–23, 41–51.

For b1 nonzero, b1 z=1 and b1 alpha+b0=0 uniquely give z=b1^-1 and alpha=-b0/b1. Put c=A(alpha), F=f(alpha). If c is nonzero, each beta in F_p determines the unique u=(beta^2-F)/c, yielding exactly p witnesses, regardless of whether F is zero, square, or nonsquare. If c=0, the equation is beta^2=F and u is arbitrary. F=0 has one root and p witnesses; a nonzero square has two distinct roots and 2p witnesses; a nonsquare has none. These cases prove the claimed existential predicate and exact fibers.

The seven alpha/inverse/evaluation variables are uniquely determined by chart coefficients. Adding beta,u gives nine variables; the two fixing equations, five evaluation equations, and one slack equation give eight equations. This count excludes chart coefficients and surrounding obligations. Odd characteristic supplies the two-root count. A zero evaluation c, including A identically zero, requires no exceptional division.

## 3. guard_projection — holds, with a preserved wording correction

Source: `sources/conditional-square/proof.md`, lines 27–37 and 41–51; the same wording occurs in its Typst/PDF report.

From c e=0, if c is nonzero then e=0. The first equation sets u=c^-1 and (1-e)beta=0 sets beta=0; the remaining equations hold for every F. If c=0, the first equation gives e=1, u e=0 gives u=0, and the final equation is beta^2=F. Hence the valid fibers are respectively one, one, or two, and the nonsquare common-root case has none. Multiplying c u=1-e by e and using c e=0 gives e=e^2; no independent Boolean equation is missing. The equations u e=0 and (1-e)beta=0 remove the otherwise free u and beta choices. Ten auxiliary variables and twelve equations follow from seven evaluation/fixing variables plus e,u,beta and seven prior equations plus five guards.

Prime-field semantics are essential. For p=5,c=0,F=3, there is no F_5 root (the square set is {0,1,4}), but in F_25 a square root exists. The guard then accepts e=1,u=0 and that extension-field beta. The corresponding slack block also accepts. Canonical F_p domains, or separately enforced field equations, cannot be omitted.

**Finding F1 — the universal balanced-divisor description breaks.** The source's line 37 describes both guard roots as giving the same balanced signed multiset. Let E/F_5 be y^2=x^3+1 and h=X(y-1), so A=-X, B=X, alpha=0, c=0, F=1. This is a normalized pole-order-five chart with N=-X^5 and U=X^5 for target O. At P=(0,1), x is a parameter and y-1=x^3/(y+1) has order 3. Thus h has order 4 at P and order 1 at -P. Both guard witnesses beta=1 and beta=-1 are valid, but the chart's divisor is 4P+(-P), which is unbalanced. The correct statement is that both auxiliary signs project to the same chart and its uniquely recovered signed divisor; only the q=0 case is balanced. For q>0 the residual ratio must determine the selected sign. The signed-recovery proof and SOURCE-API already retain that rule, so F1 does not invalidate the assigned guard equivalence or fiber count. Promoting beta to the selected sign in every common-root case would be a real implementation error.

## 4. nilpotent_square — holds

Source: `sources/nilpotent-square/proof.md`, equivalence and repeated-branch sections.

Write U=product_i (X-alpha_i)^{m_i}, with distinct alpha_i in F_p, positive m_i, and k=sum m_i>=1. Let H=C^2-f. If U divides H^k, evaluation at each alpha_i gives H(alpha_i)^k=0 in a field, hence C(alpha_i)^2=f(alpha_i). Conversely, choose a square root beta_i of every f(alpha_i) and interpolate a polynomial of degree below r, the number of distinct roots. It has degree below k and each X-alpha_i divides H. Therefore H^k has root multiplicity at least k at each alpha_i, and m_i<=k proves U divides H^k.

This reasoning uses distinct-root interpolation and ordinary divisibility, not derivatives or division by k. It works when k>=p. For example, with f=X^3+1 and U=X^k, k>=p, C=1 gives H=-X^3 and U divides H^k. U=1 is a distinct empty quotient case with no C variables and no constraints; it must not be implemented by a literal exponent-zero equation in a positive-dimensional presentation. This vacuous rationality block does not create a nonexistent pole-order-one chart or make an impossible finite-target k=0 chart valid.

**Repeated branch control.** For f=X^3+X and U=X^2 over any p>3, the curve is nonsingular and its support is the rational branch point (0,0). Exact equality C^2=f mod X^2 for C=c0+c1X forces c0=0 and then a linear coefficient 0=1. Nilpotence accepts C=0 because U divides f^2. Thus exact square congruence is strictly too strong for the submitted predicate.

**Splitting and domain controls.** For the irreducible cubic f=X^3+X+1 over F_5 used above, take U=f and C=0. The nilpotent equation holds although the support has nonrational x-coordinates. It cannot certify splitting. Separately, for split U=X-1 and the same f, f(1)=3 is a nonsquare in F_5; a constant C with C^2=3 over F_25 satisfies the equation. This isolates why both splitting and F_p witness domains are required.

## 5. fiber_count — holds

Source: `sources/nilpotent-square/proof.md`, exact-fibers section; `sources/implementation-draft/CIRCUIT-LAYOUT.draft.md`, lines 7 and 38.

For fixed U, evaluate the k coefficients of C at r distinct roots. Lagrange interpolation makes this linear map F_p^k -> F_p^r surjective; equivalently its Vandermonde minor has nonzero determinant. Its kernel has dimension k-r, even when k>=p (the number r of distinct F_p roots is at most p). Every admissible root-value tuple consequently has exactly p^(k-r) preimages. Each zero f-value offers one ordinate and each nonzero square offers two; if q values are nonzero squares there are 2^q choices. The exact number is therefore 2^q p^(k-r). Any nonsquare yields zero. For empty U, the separately defined empty coefficient tuple is the unique witness, agreeing formally with r=q=k=0.

Higher coefficients in repeated-root directions impose no extra conditions: the nilpotent equation is exactly root-value vanishing, as proved above. For example the repeated branch case U=X^2 allows every C=c1X and has p witnesses, rather than just C=0.

Monic polynomial division uniquely determines each bounded quotient and remainder from fixed inputs. In the specified acyclic addition chains, this determines every W,S,T,Q and low-degree f-reduction auxiliary from U,C. A final zero remainder only rejects C or determines its unique quotient. Thus the lifted block neither multiplies nor divides the C fiber. This is a set-theoretic fiber count at fixed U, not an observed model count or an assertion that an arbitrary SAT encoding projects these fibers correctly.

## 6. quadratic_circuit — holds

Source: `sources/implementation-draft/CIRCUIT-LAYOUT.draft.md`, all displayed layouts; `sources/implementation-draft/SOURCE-API.draft.md`, modular-product contract.

If deg L,deg R<k, then deg(LR)<=2k-2. Division by monic U of degree k gives deg P<k and deg Q<=k-2. Coefficients in positions 0 through 2k-2 give 2k-1 equations. New P and Q require k+(k-1)=2k-1 variables, or only k-1 if P is fixed to zero. For k=1, Q is absent. Products of coefficients of L,R or U,Q have total degree at most two when their inputs are affine expressions in the declared variables. All substitutions D=W-F used here are affine. Variable U therefore does not conceal a higher-degree remainder computation: the quotient variables expose it. Monicity and exact degree are indispensable for the stated uniqueness and bounds.

| k | Explicit added variables | Equations | Check |
|---|---|---:|---|
| 0 | none | 0 | separate U=1 case |
| 1 | v,F,C: 3 | 3 | v=u0^2, F=-u0 v-a u0+b, C^2=F |
| 2 | f reduction 3; C 2; W,Q0 3; final Q1 1: total 9 | 3+3+3=9 | quotient of cubic f is X+q |
| 3 | C 3; W,Q0 5; S,Q1 5; final Q2 2: total 15 | 5+5+5=15 | F=f-U is affine and has degree<3 |
| 4 | C 4; W,Q0 7; S,Q1 7; final Q2 3: total 21 | 7+7+7=21 | f already has degree<4 |
| 5 | C 5; W,Q0 9; S,Q1 9; T,Q2 9; final Q3 4: total 36 | 9+9+9+9=36 | chain D,D^2,D^4,D^5 |

For k=2, expanding U(X+q)+F1 X+F0 gives coefficients 1, q+u1, u0+u1 q+F1, and u0 q+F0, exactly the three equations in the source. For k=1 the modulus root is -u0 and f(-u0)=-u0^3-a u0+b, verifying the signs. k=3 relies on both cubics being monic. The counts retain unsimplified zero/fixed coefficients and are not minimality claims. U coefficients already belong to the surrounding chart; norm, interval, field-range, and signed-checker equations are outside this count.

**Degree control.** Maximum generator degree does not equal degree of regularity. For a concrete homogeneous algebraic comparison, the quadratic ideal (z1^2,...,zn^2) has quotient basis the square-free monomials and Hilbert series (1+t)^n; its highest nonzero graded component is degree n. Thus even a basic regularity-related invariant grows with n although all generators have degree two. No invariant of this reviewed circuit follows without its exact definition, term order where applicable, and further argument. No solving-degree or runtime result is inferred.

## 7. complete_integration_boundary — holds as a mathematical contract

Source: `sources/conditional-square/proof.md`, lines 55–59; `sources/signed-recovery/proof.md`, full extraction and gcd support; `sources/implementation-draft/SOURCE-API.draft.md`, lines 11–21; `sources/implementation-draft/sat-integration-audit.json`.

For deg B<=1, the cases b1 nonzero, b1=0 with b0 nonzero, and b1=b0=0 are disjoint and exhaustive. The first uses the reviewed guard or slack block. In the second, B has no root; at any split nonbranch norm root the ordinate is obtained by division, and branch roots are rational, so no additional rationality block is needed. The inverse equation for b0 certifies the stratum. In the third, keep full support rationality, for example the reviewed nilpotent block on U. Existing normalized chart equations can rule out a stratum, but empirical absence cannot.

**Zero-B control.** On E/F_5: y^2=x^3+1, h=X has pole order 2, B=0, split norm U=X^2 for target O, and zeros (0,1)+(0,-1). With an interval containing 0 this is a valid rational relation. Deleting zero-B even-pole charts loses it. A different nonzero-B function cannot recover the same zero divisor and pole divisor: their ratio would have no zeros or poles and be constant; normalization then fixes h. Lower-pole and empty-output cases must remain governed by their original chart conditions.

**U-only projection control.** On the same curve, h1=y-1 and h2=y+1 are both normalized pole-order-three charts with target O and the same U=X^3. Their zero divisors are respectively 3(0,1) and 3(0,-1). They are distinct signed outputs with the same norm and x-multiset. Both triples sum to O: the tangent at (0,1) is horizontal and 2(0,1)=(0,-1). Therefore blocking a U assignment alone can discard a valid distinct signed divisor. Projecting the free normalized A/B coefficients, with chart/target/k/stratum tags outside the solve and canonical field encodings, distinguishes these charts. All ordinate/idempotent/reduction witnesses must lie outside that projected prefix.

For fixed normalized h, exact local orders determine one signed zero divisor, independent of auxiliary witness choices. Balanced roots may use either checked square root; unbalanced roots must use the residual ratio; branch roots use their full local order. Remove exactly one -R, preserve a finite target factor outside the interval, and independently check curve membership, multiplicities, residual interval/base restrictions, any subgroup restriction, and group sum. Ordered permutations and O-padding are separate declared output semantics. Preserving existential coefficient models does not on its own prove a bijection between every desired relation and a chart.

The attached SAT integration audit is a producer's read-only description of three engine files. Those engine files are outside this review's frozen mathematical input set and were not inspected or executed here. Its assertions about current bridge/transcript implementations are **unverified in this review**. Accordingly this joint accepts the mathematical boundary and specified projection obligations, not a working wrapper, complete SAT coverage, native UNSAT certificate, universal chart descent theorem, or complete solver. Such implementation claims remain inconclusive on the supplied source package.

## Preserved finding, next dependency, and seal

F1 requires an additive correction of the conditional-square proof/report language: replace the universal balanced-divisor statement with independence of the recovered signed divisor from auxiliary root choice, and explicitly retain residual-ratio recovery when q>0. The admissible chart h=X(y-1) over F_5 is the concrete regression object for that distinction. No frozen source was edited.

The next implementation dependency is concrete: emit the reviewed coefficient identities, preserve all B strata and canonical normalized-coefficient projection, and independently check signed reconstruction against these counterexamples. This audit supplies neither execution evidence nor a bound for that implementation.

Requested policy/effort were `review-adversarial` / `xhigh`. Actual serving model, provider, effective effort, tier, and context/output capacity were not authenticated; the supplied prospective inference amendment records that limitation. Independent source-audit separation is declared, but no blind phase or model-authentication claim is made. The only incoming task message was the initial dispatcher prompt, recorded verbatim in the native sidecar; no later substantive producer guidance or sibling-review message arrived before sealing.

The native `review_attestation` is in the adjacent `attestation.yaml`, including all seven verdicts, F1, actual read scope, hashes, runtime limits, and message provenance. Both final artifacts were written once and sealed. Root retains responsibility for the native gate, decision, visual report, publication, and archive.
