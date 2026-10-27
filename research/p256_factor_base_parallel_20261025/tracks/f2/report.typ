#set page(paper: "a4", margin: (x: 1.6cm, y: 1.5cm), footer: context align(right, text(size: 8pt, counter(page).display("1"))))
#set text(font: "DejaVu Sans", size: 9pt, lang: "en")
#set par(justify: false, leading: 0.55em)
#set heading(numbering: none)
#show heading: set block(above: 0.8em, below: 0.4em)
#heading(level: 1)[#text("F2 — actual-field auxiliary isogeny chain and complete coordinate fibres")]
#figure(image("diagram.svg", width: 100%, height: 5.4cm, fit: "contain"), caption: [Editable study diagram; exact scope and evidence paths appear in the report.])


#text("Date: 2026-10-25. Handoff: TASK-20261025-929e0f, committed input 2c8c71cfff6f7f63297fbe4de4608cd94d857184.")
#parbreak()

#text("This report records exact implementation checks and derived mathematics. It contains no admitted scientific performance trial, official research-state transition, speedup claim, or unknown-scalar recovery claim. Every coordinate lift uses the fixed published P-256 curve. The auxiliary curve supplies domains.")
#parbreak()

#heading(level: 2)[#text("Observed exact checks")]

#text("The implementation produced a rational 16-edge degree-65,536 isogeny chain from A: y²=x³+x over the actual P-256 prime, with an explicit rational point of exact order 2^96. All 16 endpoint curves, kernel points, image generators and rational maps are serialized in chain.json (receipts/validation-001/chain.json). There are 128 pointwise checks of the two dual compositions, in addition to curve and homomorphism controls. The universal map identity and completeness proofs are given in derivation.md (derivation.md); finite point checks do not substitute for them.")
#parbreak()

#text("The complete enumerated domains have the following exact target incidence. One retained coordinate represents the pair ±P; counts use the canonical sign 0<y<=floor(p/2). Each accepted P is on P-256 and satisfies [r]P=O.")
#parbreak()

#table(columns: 5, inset: 4pt, stroke: 0.3pt + rgb("#b0bdc9"), [#text(size: 8pt, "Raw x-domain size")],
[#text(size: 8pt, "Elliptic generic fibre accepted")],
[#text(size: 8pt, "Elliptic kernel accepted")],
[#text(size: 8pt, "Dickson generic accepted")],
[#text(size: 8pt, "Matched final M, all families")],
[#text(size: 8pt, "64")],
[#text(size: 8pt, "34")],
[#text(size: 8pt, "29")],
[#text(size: 8pt, "26")],
[#text(size: 8pt, "26")],
[#text(size: 8pt, "256")],
[#text(size: 8pt, "133")],
[#text(size: 8pt, "121")],
[#text(size: 8pt, "122")],
[#text(size: 8pt, "121")],
[#text(size: 8pt, "1,024")],
[#text(size: 8pt, "519")],
[#text(size: 8pt, "526")],
[#text(size: 8pt, "515")],
[#text(size: 8pt, "515")],
[#text(size: 8pt, "4,096")],
[#text(size: 8pt, "2,080")],
[#text(size: 8pt, "2,066")],
[#text(size: 8pt, "2,108")],
[#text(size: 8pt, "2,066")])

#text("These are complete-set counts for the specified deterministic domains, with no sampling uncertainty for those sets. They do not estimate a universal acceptance rate or relation yield. In total there are 12 complete domains, 16,320 raw coordinate rows and 8,279 accepted target lifts. Their rejected rows carry certified nonresidue outcomes. All rows, including rejections, remain in split cases/*/rows-*.json certificates below the validation receipt.")
#parbreak()

#text("For the generic elliptic domains, composite degrees are 64,256,1024,4096. For kernel domains of the same raw x size the degrees are 128,512,2048,8192, because a cyclic order-N kernel has N/2 finite nonzero x coordinates modulo sign. Dickson generic fibre degrees equal the raw domain sizes.")
#parbreak()

#text("The full degree-65,536 chain has a compact complete generic-fibre certificate: x(P+jK), 0<=j<65536, with K of exact order 65,536 and non-2-torsion terminal Phi(P). Its 65,536 distinct rational x values are certified by the coset proof and exact endpoint checks. Target lifts at that full degree have not been enumerated. This distinction is recorded in compact-full-chain.json (receipts/validation-001/compact-full-chain.json).")
#parbreak()

#text("The producer passed 55,293 checked assertions. A second implementation of target scalar multiplication in Jacobian coordinates replayed all rows and passed 65,877 checks; the producer uses affine arithmetic with inversions. This is arithmetic diversity inside the producing session, not independent-session scientific review. Twelve constructed d=3 positives passed 48 checks of exact point sums, the committed symmetric S4, and an independently evaluated quadratic-resultant expression for S4. They show P1+P2+P3-Q=O with three distinct x coordinates in each matched base. Q was constructed as the sum; this is a correctness control, with no search claim. Additional compact, standard-generator and input-binding checks bring the recorded total to 121,228.")
#parbreak()

#heading(level: 2)[#text("Exact mathematical construction")]

#text("The field is")
#parbreak()

#text("p = 2^256 - 2^224 + 2^192 + 2^96 - 1 = 115792089210356248762697446949407573530086143415290314195533631308867097853951.")
#parbreak()

#text("The fixed target is")
#parbreak()

#text("E: y² = x³ - 3x + b, b = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b, r = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551, h = 1.")
#parbreak()

#text("input-bindings.json (input-bindings.json) checks these constants against the committed baseline, and checks exact bytes for all four declared input files. identities.json (identities.json) contains complete EC1 identities using the repository identity implementation, explicit endpoint coefficients and their certified subgroup generators. Those identities bind representation metadata; they do not themselves prove isogenies or group cardinalities.")
#parbreak()

#text("Derived: p=3 mod 4. Pairing x and -x cancels the character sum of x³+x, so #A(F_p)=p+1 exactly. Its 2-adic valuation is 96, and its sole rational nonzero 2-torsion point is (0,0). Hence its 2-primary subgroup is cyclic. The explicit generator is")
#parbreak()

#text("Hx = 10599893377482732565328788441705923540237515648764703688194156613780883961171, Hy = 40168709640596064189193023138493943397341466558489288332789300810036555680426.")
#parbreak()

#text("Both [2^96]H=O and [2^95]H!=O are checked, including by the replayer's projective arithmetic. No factorization or smoothness assumption is made about the odd cofactor of p+1.")
#parbreak()

#text("For an order-two point (r0,0) on the current curve, write u=x-r0 and y²=u(u²+a*u+b0). The exact quotient and destination are")
#parbreak()

#text("X=u+a+b0/u, Y=y(1-b0/u²), Y²=X³-2aX²+(a²-4b0)X.")
#parbreak()

#text("The map extends over u=0 and infinity by sending both to infinity. It is a separable degree-two elliptic isogeny over F_p; its normalized dual and both composition checks are included. The chain follows the rational cyclic subgroup rather than introducing extension-field kernels. Its elliptic maps are unramified. No conductor-based horizontal/ascending/descending assertion is made for these supersingular endpoints.")
#parbreak()

#text("For induced x maps, poles and ramification are distinct issues. At composite degree N=2^k the reduced numerator and denominator have degrees N and N-1. The finite poles are x=0 with multiplicity one and N/2-1 other kernel coordinates with multiplicity two; infinity is a simple pole. Exact factor products establish these identities through degree 4,096. The derivative numerator has degree 2N-2 and is squarefree. All finite non-pole critical values lie on the exact destination 2-torsion cubic; the source 2-torsion coordinates are not critical. See the four algebra receipts (receipts/validation-001/algebra/) for degrees, polynomial digests and branch checks. These statements concern the P¹ rational map, while the elliptic isogeny itself is unramified.")
#parbreak()

#heading(level: 2)[#text("Matched comparison and cost boundary")]

#text("Comparison fixes d=3. At each raw size, sort the accepted x values in each family and retain the first minimum accepted count among the three families. Thus final canonical M is exactly matched: 26,121,515,2066. The signed target point counts are twice those M values. Sorting, filtering and the resulting selection predicate must be included in any later solver comparison; final M is not silently identified with raw fibre degree.")
#parbreak()

#table(columns: 3, inset: 4pt, stroke: 0.3pt + rgb("#b0bdc9"), [#text(size: 8pt, "Item")],
[#text(size: 8pt, "Elliptic generic/kernel construction")],
[#text(size: 8pt, "Dickson generic control")],
[#text(size: 8pt, "Working field")],
[#text(size: 8pt, "Published P-256 F_p")],
[#text(size: 8pt, "Same F_p; norm-one torus represented in F_p[i]")],
[#text(size: 8pt, "Compact representation")],
[#text(size: 8pt, "Rational quadratic tower")],
[#text(size: 8pt, "Polynomial quadratic tower")],
[#text(size: 8pt, "Generic expanded degree")],
[#text(size: 8pt, "2^k")],
[#text(size: 8pt, "2^k")],
[#text(size: 8pt, "Step equation")],
[#text(size: 8pt, "(x-r0)²+(a-X)(x-r0)+b0=0, with denominator nonzero")],
[#text(size: 8pt, "X=x²-2")],
[#text(size: 8pt, "Sequential affine x evaluation")],
[#text(size: 8pt, "One inversion and one multiplication by b0 per step, plus translations")],
[#text(size: 8pt, "One squaring and subtraction per step")],
[#text(size: 8pt, "Alternative representation")],
[#text(size: 8pt, "Projective/batched evaluation can change inversion charges; not measured")],
[#text(size: 8pt, "No finite denominator to saturate")],
[#text(size: 8pt, "Kernel-domain degree for raw M")],
[#text(size: 8pt, "Isogeny degree 2M; reduced denominator degree 2M-1 and radical degree M")],
[#text(size: 8pt, "Generic control uses degree M")],
[#text(size: 8pt, "Domain setup")],
[#text(size: 8pt, "Generator projection, curve/map construction, kernel/coset enumeration")],
[#text(size: 8pt, "Norm-one generator projection and coset enumeration")],
[#text(size: 8pt, "Fixed-target recovery")],
[#text(size: 8pt, "Target square roots, rejected coordinates, point/subgroup checks")],
[#text(size: 8pt, "Same obligations")],
[#text(size: 8pt, "Relation solving, rank, target attachment")],
[#text(size: 8pt, "Unimplemented beyond constructed correctness positives")],
[#text(size: 8pt, "Same limitation in this comparison")],
[#text(size: 8pt, "Cold start / reuse")],
[#text(size: 8pt, "Setup charged once / may be reused over targets")],
[#text(size: 8pt, "Same accounting rule")])

#text("These are exact degree descriptions and stated arithmetic formulas, not a performance ranking. The polynomial tower has a simpler finite-pole profile; that alone does not price elimination or recover a relation. An expanded dense membership polynomial still has degree equal to the raw domain size. No end-to-end speedup is inferred from short circuits, setup times, finite incidence counts or constructed positives.")
#parbreak()

#text("Derived: the auxiliary and target orders are coprime, and their traces differ:")
#parbreak()

#text("gcd(p+1,r)=1, t_A=0, t_E=p+1-r=89188191154553853111372247798585809583.")
#parbreak()

#text("Thus a rational-point group homomorphism from the target into the auxiliary group must be zero, and there is no F_p-isogeny between these elliptic curves. The coordinate selection rule supplies no transfer of P-256 scalar labels or its DLP into an auxiliary smooth subgroup.")
#parbreak()

#heading(level: 2)[#text("Checks, failures and reproducibility")]

#text("Software: CPython 3.12.14; python-flint 0.8.0, with the underlying FLINT version in result.json (result.json). Primality uses FLINT's is_prime backend. A portable primality proof object is not serialized. The published target total order r is an input, and every accepted target lift additionally satisfies the exact [r]P test. The auxiliary point count has the direct character-sum proof.")
#parbreak()

#text("The validation used one process, about 54 MiB maximum resident memory (54,628 KiB), and about 81.49 seconds of wall time. Replay took about 18.64 seconds. These are software-validation resource observations, not matched algorithm performance measurements. The declared 2 GiB envelope was respected. Exact commands, revisions, dirty-tree state, source hashes, seeds, parameters, stdout and stderr are retained in the receipts.")
#parbreak()

#text("Four negative controls completed with their expected nonzero exits:")
#parbreak()

#block(inset: (left: 8pt))[#text("• Unexpected exception injection: launcher refuses to create a success result.")]

#block(inset: (left: 8pt))[#text("• Early return: missing completion sentinel is rejected.")]

#block(inset: (left: 8pt))[#text("• Mutated accepted target y: replay rejects the curve equation.")]

#block(inset: (left: 8pt))[#text("• Direct implementation-body execution: refused; use the guarded launcher.")]

#text("The initial SVG-builder command completed with a harmless Python literal backslash warning. Its output is retained as receipts/build-001.json; the literal spelling was corrected, and builds 002/003 completed without the warning. Inkscape rendered both previews successfully while reporting that its profile/font cache directories are read-only; default settings were used. No arithmetic run failed unexpectedly and no coordinate was dropped.")
#parbreak()

#text("From this track directory, the original primary commands were:")
#parbreak()

#text(size: 7.2pt)[#raw("/workspace/dickson-solver/.venv/bin/python run_validation.py --label control-exception --inject \nexception\n/workspace/dickson-solver/.venv/bin/python run_validation.py --label control-early-return --inject \nearly_return\n/workspace/dickson-solver/.venv/bin/python run_validation.py --label validation-001\n/workspace/dickson-solver/.venv/bin/python verify_certificates.py --source receipts/validation-001 \n--receipt receipts/replay-corrupt-target.json --corrupt-target\n/workspace/dickson-solver/.venv/bin/python verify_certificates.py --source receipts/validation-001 \n--receipt receipts/replay-pass.json\n/workspace/dickson-solver/.venv/bin/python relation_certificates.py\n/workspace/dickson-solver/.venv/bin/python input_bindings.py\n/workspace/dickson-solver/.venv/bin/python finalize.py", block: true)]

#text("Receipts contain their actual absolute command paths and launch directory. Sealed receipt paths refuse overwrite. To reproduce the full main arithmetic pass alongside existing evidence, choose a fresh label such as --label validation-replay-002, then point verify_certificates.py --source at that new directory and choose a fresh --receipt path. The sealed first relation/input certificates can be replayed from a fresh study checkout or checked directly from their explicit point and polynomial data.")
#parbreak()

#text("All JSON certificate chunks and code files are below 64 KiB. PNG inspection previews are larger derived visualizations, below 1 MiB; editable SVG is the primary rendering. Root is responsible for the requested aggregate PDF. diagram.svg (diagram.svg) and incidence.svg (incidence.svg) were rendered and visually inspected; their source is finalize.py (finalize.py). No shared canonical graph was edited because the assigned write scope is only this track and no official conclusion changes.")
#parbreak()

#heading(level: 2)[#text("Existing evidence, limitations and next check")]

#text("Internal provenance: the existing PKM decomposition obstruction (../../../../problems/pkm-isogeny-chain-factor-base-no-fast-decomposition.md) was read. It already describes this auxiliary family, a proposed 44-edge P-256 route, the absence of a fast decomposition solver and historical chain-versus-dense studies. This pass does not claim novelty, independently revalidate those historical results, or rerun their grid. It adds actual-field map, complete-fibre, pole/branch and fixed-target incidence certificates. input-bindings.json pins the exact version read. No external literature claim is used as proof of these new checks.")
#parbreak()

#text("The next decisive implementation is a complete relation solver over the frozen matched bases at d=3: couple the committed symmetric S4 to each membership representation, saturate all denominators, certify complete root sets and point signs, and charge rejected coordinates, setup, root recovery and verification. A separately admitted paired study would then measure total cost, against dense same-set and Dickson controls, with successful and empty cases retained. The present bundle does not meet or change the existing scientific solver-performance exit criterion.")
#parbreak()
