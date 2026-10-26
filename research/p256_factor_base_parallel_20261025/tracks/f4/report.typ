#set page(paper: "a4", margin: (x: 1.6cm, y: 1.5cm), footer: context align(right, text(size: 8pt, counter(page).display("1"))))
#set text(font: "DejaVu Sans", size: 9pt, lang: "en")
#set par(justify: false, leading: 0.55em)
#set heading(numbering: none)
#show heading: set block(above: 0.8em, below: 0.4em)
#heading(level: 1)[#text("F4: exact P-256 principal divisors and signed partial relations")]
#figure(image("diagram.svg", width: 100%, height: 5.4cm, fit: "contain"), caption: [Editable study diagram; exact scope and evidence paths appear in the report.])


#text("2026-10-25 · TASK-20261025-ce1163 · implementation validation and derivation.")
#parbreak()

#text("The working prototype extracts exact rational principal divisors and cancels one/two outside-base-point columns over the published P-256 subgroup order. All 29 fixed divisor certificates pass a separate checker. These are implementation observations; no scientific yield/cost trial, performance comparison, attack claim, or official state transition was performed. The split positives deliberately use known small scalar multiples and engineered coincidences. Their ranks establish software behavior only.")
#parbreak()

#heading(level: 2)[#text("Observed outputs")]

#text("Final producer record: check-04/receipt.json (receipts/check-04/receipt.json). Separate arithmetic checker: independent-04.json (receipts/independent-04.json). Corruption controls: adversarial-03.json (receipts/adversarial-03.json). Earlier attempts are retained in receipts/; see commands.md (commands.md).")
#parbreak()

#table(columns: 7, inset: 4pt, stroke: 0.3pt + rgb("#b0bdc9"), [#text(size: 8pt, "Fixed correctness family")],
[#text(size: 8pt, "Raw rows")],
[#text(size: 8pt, "Rank over all columns")],
[#text(size: 8pt, "Rank of outside incidence")],
[#text(size: 8pt, "Kernel dimension")],
[#text(size: 8pt, "Rank after cancellation")],
[#text(size: 8pt, "Zero output rows")],
[#text(size: 8pt, "One outside point")],
[#text(size: 8pt, "7")],
[#text(size: 8pt, "5")],
[#text(size: 8pt, "1")],
[#text(size: 8pt, "6")],
[#text(size: 8pt, "4")],
[#text(size: 8pt, "2")],
[#text(size: 8pt, "Two outside points")],
[#text(size: 8pt, "5")],
[#text(size: 8pt, "4")],
[#text(size: 8pt, "3")],
[#text(size: 8pt, "2")],
[#text(size: 8pt, "1")],
[#text(size: 8pt, "1")],
[#text(size: 8pt, "Combined, with pole-order fixtures")],
[#text(size: 8pt, "20")],
[#text(size: 8pt, "13")],
[#text(size: 8pt, "4")],
[#text(size: 8pt, "16")],
[#text(size: 8pt, "9")],
[#text(size: 8pt, "6")],
[#text(size: 8pt, "Same-sign triangle negative control")],
[#text(size: 8pt, "3")],
[#text(size: 8pt, "3")],
[#text(size: 8pt, "3")],
[#text(size: 8pt, "0")],
[#text(size: 8pt, "0")],
[#text(size: 8pt, "0")])

#text("Every rank is independently recalculated modulo r, not modulo p. The projected base-column ranks before cancellation are respectively 5, 4, 11, 3. These projections alone are not complete relations because their omitted outside columns remain nonzero. The first table's after-cancellation ranks are actual full-base row ranks. For every family the checker verifies rank(full rows) - rank(outside incidence) = rank(cancelled rows) and the full rank of the supplied kernel witnesses.")
#parbreak()

#text("The 29 cases comprise eight pole/multiplicity fixtures, six coefficient-sampler checks, seven one-outside rows, five two-outside rows, and three same-sign triangle rows. Twenty-four divisors are completely rational. Five coefficient checks retain unresolved norm factors; they are not accepted as full or partial rational relations. Those six checks are validation inputs with seeds 4100–4105, not a probability estimate. Pole orders 2 through 8 occur; all orders 3–8 have a hand-arranged fully split positive. The checker verifies 100 irreducible norm factors, 188 local-branch multiplicity checks, and 24 stitched group sums. Five independent certificate corruptions (norm, zero multiplicity, signed row, stitching coefficient, rank) are detected. Five expected API refusals check the zero function, exhausted interpolation space, anchors forcing a lower pole, unresolved divisors entering the graph, and more than two outside orbit columns.")
#parbreak()

#heading(level: 2)[#text("Exact instance and source provenance")]

#text("baseline/parameters.py supplies p, a=-3, b, r, h=1. Its SHA-256 is bound by the producer receipt; exact integers and generator coordinates appear there. The target is E/F_p: y²=x³-3x+b, p=2^256-2^224+2^192+2^96-1, with the published prime subgroup order r and h=1. The standard generator G is embedded in source; both implementations check the curve equation and [r]G=O. The cubic is independently irreducible over F_p, so no rational branch point y=0 occurs. The published h=1 and r are input facts; this pass does not independently point-count the curve or prove their primality.")
#parbreak()

#text("Provenance: the committed task, plan and fixed constants are internal, retrieved, verified by this executor reading the assigned inputs. The formulas below are derived in this work and the finite checks are internal, retrieved receipts produced here. Prior /workspace/dickson-inspection/proofs.txt, section 3, was read, read-only: it explicitly restricts its earlier bounds to uniform-target, explicit-fibre, three-point collection and excludes nonuniform and partial-relation methods. That earlier result is context, not evidence for this implementation. No external paper was used to support an unverified claim; the plan's literature pointers remain pointers.")
#parbreak()

#heading(level: 2)[#text("Function space, exact divisor extraction, and failure boundary")]

#text("For m>=2 use the basis")
#parbreak()

#text("L(mO) = span{ x^i : 2i<=m } + span{ x^j y : 2j+3<=m },")
#parbreak()

#text("which has dimension m. A function is f=A(x)+yB(x). Since ord_O(x)=-2 and ord_O(y)=-3, its exact pole order is")
#parbreak()

#text("m(f)=max(2 deg A, 3+2 deg B).")
#parbreak()

#text("The two weights have opposite parity, so their leading poles cannot cancel. Set g=x³+ax+b. The norm under y -> -y is N=A²-gB², of degree m(f). The producer factors N over the actual 256-bit field with python-flint's fmpz_mod_poly_ctx. Every norm factor, exponent, coefficient, and unit is retained.")
#parbreak()

#text("For every linear factor root X with square g(X), both points (X,+Y) and (X,-Y) are tested. Because Y!=0, t=x-X is a local parameter. The producer recursively lifts y(t) from y(t)²=g(X+t) and finds the first nonzero coefficient of A(X+t)+y(t)B(X+t). The two local orders sum to the norm-root multiplicity, including common A/B roots and inverse pairs. The separate consumer constructs the same local branch using Newton/Hensel polynomial inversion and independently verifies these valuations. Pole degree, factor product, irreducibility, point recovery, and every declared anchor multiplicity are checked.")
#parbreak()

#text("When every zero is rational and the total degree is m, the complete divisor is div(f)=sum_P v_P(f)[P]-m[O]. A separate Jacobian group implementation checks sum_P v_P(f)P=O; the producer uses affine formulas. When norm factors have degree >1, or a linear X has nonsquare g(X), the receipt retains an explicit unresolved block and refuses to claim a rational relation. This is not a full extension-prime-divisor decomposition engine. The API deliberately refuses rational 2-torsion local jets; irreducibility of the P-256 cubic proves that branch is unreachable here. These limitations remain visible in obstruction.md (obstruction.md).")
#parbreak()

#heading(level: 2)[#text("Sampling distributions and exact conditional controls")]

#text("The uniform-coefficient control samples uniformly in the evaluation kernel for explicitly supplied anchors, then rejects functions whose top pole coefficient vanishes. It records the basis, all anchor coordinates, evaluation rank, kernel dimension, RNG seed, and rejected draws. A finite seeded PRNG is used for reproducible software checks; distribution statements describe ideal uniform draws of the free coefficients.")
#parbreak()

#text("For distinct anchors H with k constraints and evaluation-kernel dimension d, if the top coefficient is a nonzero linear functional on the kernel, there are (p-1)p^(d-1) acceptable coefficient vectors and p^(d-1) projective functions. Every projective function has exactly one zero divisor. Consequently this sampler is exactly uniform over effective divisors D in |mO| containing H and excluding O. The leading-coefficient rejection probability per draw is exactly 1/p. If the top functional vanishes on the whole kernel, the sampler refuses instead of looping. Repeated anchor entries do not impose derivative constraints in the sampler; the validation fixtures separately declare repeated zeros and check their actual multiplicities. Distinct point evaluations have d=m-k when the remaining positive degree applies; the implementation always calculates rank rather than assuming it.")
#parbreak()

#text("The six checked choices (m, anchor scalars, seed, d) are (3,[],4100,3), (4,[3],4101,3), (5,[2,-2],4102,3), (6,[3,4],4103,4), (7,[3,4,5],4104,4), (8,[3,4],4105,6). All anchor points are public scalar multiples of G. Their constraints and residual degrees are charged explicitly. In particular opposite anchors +2G and -2G force the factor x-x(2G) and add one inverse pair, hence zero signed information. The pole-3 opposite-anchor refusal is mathematically required: the residual degree-one zero is O, contradicting exact pole 3.")
#parbreak()

#text("There is also an exact all-rational control requiring no sampling. Since E(F_p) has prime order r, for 2<=m<r the number of effective degree-m divisors supported on affine rational points whose group sum is O is")
#parbreak()

#text("C(r+m-2,m)/r.")
#parbreak()

#text("Proof: Burnside's lemma acts on ordered tuples by S_m. For a permutation with c cycles, the fixed tuples satisfy a weighted sum of c nonzero group elements equal to O. Every cycle length is in 1..m and is invertible modulo r. Multiplying its group variable by that length preserves the nonzero domain, so the fixed count is T_c=((r-1)^c+(r-1)(-1)^c)/r. The cycle enumerator is sum_sigma z^cycles = z(z+1)...(z+m-1). For m>=2 its value at z=-1 vanishes. Dividing its value at z=r-1 by r*m! yields the claimed count. The usual degree-zero divisor criterion on an elliptic curve gives principality over F_p; equivalently a one-dimensional rational section is fixed up to scalar, and Hilbert 90 supplies a rational function. Exact pole m projective sections number p^(m-1). Therefore")
#parbreak()

#text("Pr(all zeros affine rational) = C(r+m-2,m)/(r*p^(m-1)).")
#parbreak()

#text("This is approximately 1/m! when m is fixed and p grows; it is not a factor-base smoothness or useful-rank probability. At m=2 all rational zero divisors are inverse pairs, so their signed rows are zero. exact-counts.json (receipts/exact-counts.json) contains exact integer fractions for m=2..8 and 18 independently enumerated abstract cyclic-group checks of the Burnside formula. These checks validate the formula, not P-256 yield.")
#parbreak()

#text("For a fixed inverse-closed affine base B, the exact full-base probability is")
#parbreak()

#text("#{D>=0 : deg D=m, supp(D) subset B, sum D=O} / p^(m-1).")
#parbreak()

#text("For fixed anchors replace the numerator by the same count with D>=H and replace the denominator by p^(d-1). This formula counts multiplicity, forced anchors and inverse pairs. A fair structured/unstructured-base comparison must evaluate this base-specific count or sample the identical kernel law; it cannot transplant the all-rational probability. For partial relations the event must be defined after signed orbit aggregation: the number of nonzero outside orbit columns must be one or two. A pair of opposite outside points disappears and must be counted as a cancellation, not as a reusable large point.")
#parbreak()

#text("A prospective matched conditional control should hold m, k, evaluation rank, exact-pole filtering, base cardinality, inverse closure, subgroup handling and anchors fixed. It should compare uniform kernel coefficients with the proposed nonuniform law, record all draws and rejections, and report rank increments after anchor-only, inverse-pair, duplicate and dependent rows are counted. Products of preselected lines/parabolas have a very different factorization-biased distribution; the examples here must never enter that yield comparison.")
#parbreak()

#heading(level: 2)[#text("Partial graph and exact cancellation")]

#text("The canonical column representative for (X,Y) is (X,min(Y,p-Y)); its coefficient is +v or -v according to the sign of Y. Infinity contributes no column. Full rational rows are checked before being split into base and outside columns.")
#parbreak()

#text("One outside point is an edge to a distinguished hub; two outside points form an edge between their inverse orbits. Endpoint signs and multiplicities are retained. Write D for the complete row matrix and A for the matrix whose columns are rows' outside coefficients. The algorithm computes the full right kernel of A over F_r. Every kernel vector c has the exact witness A*c=0, and c^T*D is a full-base relation. Independent elimination verifies the rank identity in the observations table. This dense kernel implementation is a correctness oracle, not a scalable graph engine: it stores complete coefficient witnesses and performs dense modular elimination. A sparse spanning-forest signed-cycle engine remains unimplemented. Kernel rows that map to zero, duplicate raw rows, and their zero independent-rank contribution are retained.")
#parbreak()

#text("The base in the one-/two-outside families consists of the 12 inverse orbits of G through 12G. The one-outside family fixes the excluded point 15G and uses base sums 3+12=4+11=5+10=6+9=7+8=15. Duplicate and inverse-augmented copies add no independent signed row. The two-outside family takes oriented edges (100,101),(101,103),(103,106),(106,100) with functions through iG and -jG. Their outside coefficients telescope; base differences give the nonzero relation G+2G+3G-6G=O. A duplicate edge produces a zero combination.")
#parbreak()

#text("The negative control uses pairs (100,101),(101,103),(103,100) and a base with inverse orbits 201G,203G,204G. It has a three-cycle as an unsigned graph, but its incidence matrix is invertible: after column/row sign changes its determinant has magnitude 2, nonzero modulo odd r. It yields no full-base relation. Thus ordinary cycle count cannot stand in for signed cancellation rank. Mixed families remain separate in the records; the combined matrix is a software fixture, not a common-law sample.")
#parbreak()

#heading(level: 2)[#text("Accounting and work explicitly unrun")]

#text("The producer receipt reports wall/CPU time and peak RSS for this exact validation workload, with versions, platform, HEAD and dirty-tree state. These are implementation resource observations only. No matched baseline exists. No comparative cost, asymptotic attack bound, target logarithm, or speed statement follows.")
#parbreak()

#text("The implemented algebra uses norm degree m, retains all irreducible factors and local multiplicities, and records graph edges, kernel witnesses and cancelled rows. Coefficient generation requires constructing and eliminating a k-by-m evaluation matrix; every rejected exact-pole draw is retained. Norm formation, factorization, root recovery, local jets, base membership, outside-point hashing, graph storage, row reduction and subgroup scalar multiplication must each be charged in a prospective trial. Dense cancellation can require O(L*t + L^2) field-element storage for L raw rows, t outside columns and explicit nullspace witnesses; this is a representation bound for this implementation, not a lower bound for sparse alternatives. The current signed row compression removes inverse pairs but preserves their counts.")
#parbreak()

#text("Still unrun: natural relation production on any structured P-256 base of scientific interest; matched random-base and conditional-uniform controls; a frozen uniform or nonuniform coefficient workload of meaningful sample size; independence/rank growth versus every generated function and elapsed/resource cost; outside-vertex collision frequency and graph growth; sparse signed-cycle implementation and retained coefficient cost; dependence on pole order, anchor rule, base size and structure; complete target attachment and final linear solve; amortized single-/many-target setup comparison. No unknown target Q was supplied or recovered. The coefficient sampler checks do not measure any of these quantities, and engineered common outside points provide no collision-rate evidence.")
#parbreak()

#text("The next decisive work is a Coordinator-frozen paired trial using the exact conditional laws above, a declared target-independent base and all-failure cost/rank accounting. It needs a real graph workload and enough natural retained edges to measure cancellation. A scarcity of retained rows would be a bounded observation, not an impossibility proof. obstruction.md (obstruction.md) names this measurement/implementation gap with acceptance conditions. No shared problem index, goal record, hypothesis record, git state, or PR was changed by this executor. Root renders the aggregate PDF under the explicit handoff; the editable diagram.svg (diagram.svg) is supplied here.")
#parbreak()
