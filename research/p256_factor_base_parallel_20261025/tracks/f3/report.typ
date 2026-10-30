#set page(paper: "a4", margin: (x: 1.6cm, y: 1.5cm), footer: context align(right, text(size: 8pt, counter(page).display("1"))))
#set text(font: "DejaVu Sans", size: 9pt, lang: "en")
#set par(justify: false, leading: 0.55em)
#set heading(numbering: none)
#show heading: set block(above: 0.8em, below: 0.4em)
#heading(level: 1)[#text("F3: coefficient-labelled P-256 bases, exact dependency controls")]
#figure(image("diagram.svg", width: 100%, height: 5.4cm, fit: "contain"), caption: [Editable study diagram; exact scope and evidence paths appear in the report.])


#text("2026-10-25. Task TASK-20261025-1f3375. Implementation validation and derived mathematics only; no admitted scientific performance trial, official research transition, or speed claim. The supplied card owns this folder. The root task renders the aggregate PDF with diagram.svg (diagram.svg).")
#parbreak()

#heading(level: 2)[#text("Checked observations")]

#text("Python receipt (receipts/validation-02/checks.json) records 97/97 passing checks. Independent Sage receipt (sage-independent.json) records 100/100 passing assertions, using Sage 10.6 group/polynomial arithmetic without importing producer code. Each of three deterministic cases uses actual P-256, 24 labelled points, and three disjoint coordinate domains of eight points each.")
#parbreak()

#table(columns: 5, inset: 4pt, stroke: 0.3pt + rgb("#b0bdc9"), [#text(size: 8pt, "Case")],
[#text(size: 8pt, "Hybrid specializations / membership probes")],
[#text(size: 8pt, "Complete signed tuples")],
[#text(size: 8pt, "Dependencies")],
[#text(size: 8pt, "Nonzero-Q dependencies")],
[#text(size: 8pt, "Natural random labels, hash-to-point target")],
[#text(size: 8pt, "64 / 128")],
[#text(size: 8pt, "2,048")],
[#text(size: 8pt, "0")],
[#text(size: 8pt, "0")],
[#text(size: 8pt, "Deliberately added label-vector dependency")],
[#text(size: 8pt, "64 / 128")],
[#text(size: 8pt, "2,048")],
[#text(size: 8pt, "1")],
[#text(size: 8pt, "0")],
[#text(size: 8pt, "Deliberately arranged known-witness fixture")],
[#text(size: 8pt, "64 / 128")],
[#text(size: 8pt, "2,048")],
[#text(size: 8pt, "1")],
[#text(size: 8pt, "1")])

#text("Counts are implementation counters, not performance measurements or statistical estimates. The exhaustive control covers 512 partition-coordinate triples and four sign choices per triple; simultaneous negation is identified. Sage separately rechecks all 6,144 signed group sums, all 72 point labels, nine exact membership polynomials, and the producer's complete candidate lists. These are independent arithmetic checks by a separate implementation, not independent scientific review. The recorded counts are plotted in counts.svg (counts.svg); each is a complete deterministic domain count, so no sampling uncertainty is inferred.")
#parbreak()

#text("All three bases require 24 forward labelled-point constructions, each using two scalar multiplications and one addition call: 48 multiplications and 24 addition calls per initial base. Neither case had a rejected point. Each arranged case replaces one point using two more scalar multiplications and one addition call; the original construction remains charged. Target generation, validation, sign checks, final recovery and independent checking are separate from those base counters. No total-runtime comparison was made.")
#parbreak()

#text("The natural target is a deterministic SHA-256-to-x then increment-and-lift point. No target scalar is generated or supplied for that case. The useful fixture has a public generation witness; it is intentionally arranged and demonstrates correctness only. The search interface is exactly aps3_search(points, parts); neither labels nor the target scalar enter it. Label reduction follows the search. The exhaustive search also receives only points and partitions. Public fixtures do not establish resistance to an adversarially modified search implementation.")
#parbreak()

#heading(level: 2)[#text("Exact formulation and source scope")]

#text("Retrieved: APS, section 3, initializes a factor base with random points R_i=a_i G+b_i Q, retaining their coefficients. It seeks a signed zero sum of m base points using S_m(X_1,...,X_m)=0 together with membership polynomials. Equation (9) uses one coordinate set; equation (11) instead partitions the base and imposes f_j(X_j)=0, where f_j(T)=product_(v in V_j)(T-v). This lowers membership degrees and breaks variable permutation symmetry. One usable dependency replaces the large linear-algebra stage. Its partial analysis writes the solving contribution as p m^m/s^m * T(E,m,V) for total base size s. The unknown system-solving cost is explicit; the paper does not claim a rho improvement. Its proposed comparison of two system-solving costs is an assumption, not a theorem about P-256. APS full text (https://pure.tue.nl/ws/files/91158650/609.pdf), accepted manuscript, retrieved and read by /root/labelled_relations.")
#parbreak()

#text("Retrieved, limited: The publisher's Kudo et al. abstract (https://link.springer.com/chapter/10.1007/978-3-030-00434-7_19) describes combining enumeration with Gröbner bases and exploiting summation polynomial symmetry, with a limitation analysis. The chapter text was not available through this access; the author publication list supplied no chapter PDF. No detailed theorem, numerical benchmark, or claimed asymptotic result is attributed to that unread text. The following hybrid and symmetry arguments are our derivations and executable controls, not a reproduction of its full solver.")
#parbreak()

#text("No knowledge-retrieval tool was exposed in this session; direct primary-source retrieval was used. Source provenance and failed retrieval commands are retained in sources/README.md (sources/README.md) and commands.md (commands.md).")
#parbreak()

#heading(level: 2)[#text("Derived relation semantics")]

#text("Let r be the published P-256 prime subgroup order, G its standard generator, and Q=dG. For integer signs or multiplicities c_i, a checked point sum gives")
#parbreak()

#text("sum c_i R_i = A G + B Q = O, A=sum c_i a_i mod r, B=sum c_i b_i mod r.")
#parbreak()

#text("If B != 0, recover d=-A/B mod r and verify dG=Q. If B=0, prime order and nonzero G force A=0; there is no target information. A nonzero A with B=0 and alleged zero point sum therefore signals invalid data/arithmetic. The useful fixture finds indices [0,8,23] with signs [1,1,1] and")
#parbreak()

#text(size: 7.2pt)[#raw("A = 29573671103124895115787968340613126283327914975757212433605680540275524054175\nB = 4950236570683604987279798809952199384361660423120179508534101522829488279666\nd = 17771659022183858000793161591735937992842282683861079915509427757067157576346", block: true)]

#text("Sage verifies its three labels, zero sum, and final dG=Q. This scalar was already known to fixture generation. It is not a recovered ordinary unknown-log instance.")
#parbreak()

#text("Derived construction limitation: adding label vectors to arrange R_3=-(R_1+R_2) by setting (a_3,b_3)=-(a_1,b_1)-(a_2,b_2) arranges A=B=0. This is exactly the second checked case, with distinct coordinates and no inverse pair: removing inverse pairs alone is insufficient. In the useful fixture we deliberately use the known d to change a_3 so that A=-dB with B!=0. For an arbitrary target, supplying such a kernel vector is equivalent to supplying its logarithm. This identifies the hidden-oracle boundary without excluding genuine point-relation search.")
#parbreak()

#text("Derived conditional usefulness lemma: if (a_i,b_i) are independent uniform pairs in F_r^2, write t_i=a_i+d b_i. The change of variables (a_i,b_i) -> (t_i,b_i) is bijective. Thus labels b_i remain independent uniform conditional on all points R_i=t_iG. Any nonzero relation vector chosen from points alone has B=sum c_i b_i uniform; conditional probability of B=0 is exactly 1/r. Point-only rejection of identity or repeated x values preserves that property. Adaptive/dependent label construction or label-dependent relation selection invalidates that proof. Our SHA-derived finite fixtures do not test this probability distribution.")
#parbreak()

#heading(level: 2)[#text("Executable hybrid and degeneracy handling")]

#text("For m=3, the code specializes the exact symmetric summation polynomial")
#parbreak()

#text("S_3(x,y,z)=(x-y)^2 z^2-2[(x+y)(xy+a)+2b]z+(xy-a)^2-4b(x+y).")
#parbreak()

#text("It enumerates (x,y) in the first two domains, solves the residual quadratic over the actual P-256 field, and tests roots in a hash table for the third domain. P-256 has p=3 mod 4, permitting exact square-root tests. Linear, constant nonzero, repeated-root and nonsquare branches are checked; an identically zero residual raises an error rather than falsely declaring empty. Root sets, recovered rational point signs and exact point sums are all checked. All domain points already lie on P-256, so no extension-field lift is inferred from the summation polynomial alone.")
#parbreak()

#text("Search input rejects identity, off-curve points, repeated x values (including inverse pairs), and overlapping/incomplete partitions. The separate relation assessor records inverse-pair and repeated-index cancellations as zero-Q dependencies; it rejects forged labels, off-curve points and off-curve targets. A wrong-sign near-relation is correctly nonzero. The inverse pair, repeated-index case, and distinct-coordinate dependent-label case are separate controls.")
#parbreak()

#text("This is a complete solver for the declared three domains, not a general Gröbner solver. Its agreement with a separate exhaustive group-sum search demonstrates finite completeness for the tested domains. No performance gain is inferred from comparing an operation count with a different primitive count.")
#parbreak()

#heading(level: 2)[#text("Full construction/search accounting (derived models)")]

#text("Write s for total stored points and n=s/m for equal partition sizes. Let C_mul(r) denote a scalar multiplication, C_solve an exact system solve, and P_u the probability one generated base contains an accepted useful dependency found by that solver. A cold attempt must charge")
#parbreak()

#text("C_base + C_membership + C_solve + C_sign + C_label + C_verify,")
#parbreak()

#text("where C_base includes rejected attempts and label construction. Expected restart cost, if attempts are independent with fixed success probability, is that entire cost divided by P_u, with success-only costs charged once where appropriate. No empirical P_u has been measured here. Stopping after this fixed correctness workload is not campaign exhaustion or proof of infeasibility.")
#parbreak()

#table(columns: 2, inset: 4pt, stroke: 0.3pt + rgb("#b0bdc9"), [#text(size: 8pt, "Stage")],
[#text(size: 8pt, "Honest cost/obligation")],
[#text(size: 8pt, "Independent labelled construction")],
[#text(size: 8pt, "Two scalar multiplications plus an addition per raw point in this implementation; store point and two labels. Joint multiplication can change constants but must be counted.")],
[#text(size: 8pt, "Deduplication/subgroup")],
[#text(size: 8pt, "Reject O and repeated x, retain all rejection costs; subgroup order checked for Q, published cofactor one; forward labels remain in the subgroup.")],
[#text(size: 8pt, "Random membership polynomial")],
[#text(size: 8pt, "Naive product is quadratic field work per partition, output has n+1 coefficients; product trees can change construction cost. Root-list input alone is not a short solving algorithm.")],
[#text(size: 8pt, "Dense representation")],
[#text(size: 8pt, "m membership polynomials have degree n; S_m has exponential individual degree as m grows. Representing a circuit avoids expansion only if the solver accepts and exploits it.")],
[#text(size: 8pt, "Generic hybrid")],
[#text(size: 8pt, "For h enumerated variables, sum residual-solving and root/sign costs over all n^h specializations; an unmeasured residual cost is not zero.")],
[#text(size: 8pt, "This m=3 implementation")],
[#text(size: 8pt, "Exactly n^2 quadratic specializations and at most 2n^2 membership probes; each square root and inverse has field-bit cost. Memory is linear in s apart from output; retained output can be large.")],
[#text(size: 8pt, "Recovery")],
[#text(size: 8pt, "Sum selected labels modulo r; invert B only when nonzero; verify the candidate by scalar multiplication.")])

#text("In an ideal independent uniform-point model, there are N=2^(m-1) n^m sign choices modulo simultaneous negation across the disjoint partitions. Each fixed sign vector has zero-sum probability 1/r before nonidentity/repeated-x rejection, so expected raw dependencies are N/r. Linearity of expectation needs no independence between relation events. The probability of at least one is at most N/r; using 1-exp(-N/r) is a heuristic, not an identity. For uniform points sampled with distinct x values, a safe union bound is N/(r-2m+1) by exposing the last of the m distinct-point representatives; its required point is either forbidden or is one of the remaining equally likely points. For the fixed 8/8/8 domains this bound is 2048/(r-5). The zero observed natural dependencies do not estimate a tiny probability or establish a negative mathematical conclusion.")
#parbreak()

#text("For the implemented m=3 method, constant expected raw relation count requires n^3 on the order of r in that ideal model, while its enumeration term is quadratic in n. This explicitly retains the construction and solver obligations; it is not a measured attack cost or a claim of general optimality. For other m, neither a low-degree circuit nor a factorial symmetry reduction supplies the missing residual solver or a useful-relation probability theorem.")
#parbreak()

#text("Choosing points from a structured x-domain first does not supply their labels: given an arbitrary selected R and chosen b, finding a with R-bQ=aG is another discrete-log instance unless additional structure supplies a costed method. Conversely, testing forward random labelled points against a domain accepted with probability delta costs on average 1/delta raw constructions per accepted point under independent sampling. Both routes must charge their full setup.")
#parbreak()

#heading(level: 2)[#text("Symmetry, comparators and reuse boundaries")]

#text("S_m is invariant under variable permutations. The full system inherits that action only if the domains and additional constraints also permit it. Equal domains can identify m! orderings for tuples with distinct coordinates, but repeated-coordinate stabilizers alter the orbit size. Disjoint fixed domains break that variable-permutation symmetry; permuting domain names too does not create new reductions inside one fixed system. Global point negation is already quotiented by fixing the first sign positive. Inverse-pair padding creates roots without new information and is explicitly excluded or counted separately.")
#parbreak()

#text("A hybrid replaces variables by enumeration and reduces the remaining system; it trades specialization count against residual algebra. That trade can be valuable locally while leaving base construction, relation availability, degenerate outputs and total memory unresolved. This is our inspection of the limitation, not an assertion that Kudo proved a theorem absent from accessible text. No impossibility result for new structured/adaptive constructions follows.")
#parbreak()

#text("The generic reference formulations are rho with expected square-root group work and modest storage, and BSGS with a precomputed table of B generator multiples, table construction B and per-target search about r/B group steps. These are theoretical references, unrun here; identical sign/symmetry advantages must be given to both sides. Many-relation index calculus additionally needs sufficient independent factor-base rows, linear algebra and target attachment. The labelled construction removes that rank quota only after paying for one dependency with nonzero B; merely recording many known labels does not solve that search.")
#parbreak()

#text("For multiple targets Q_j, this random labelled base has coordinates a_iG+b_iQ_j, so its domains and membership polynomials change with the target. Generator tables or stored a_iG can be shared, but b_iQ_j and the solving instance remain target dependent. Taking all b_i=0 creates reusable labels with B identically zero; it needs a separate target-attachment algorithm. Any proposed many-target benefit must also compare with the shared BSGS table and fixed-base scalar precomputation, with cold setup and number of targets stated.")
#parbreak()

#heading(level: 2)[#text("Limitations and next decisive step")]

#text("The concrete unresolved requirement is a costed solver/construction producing natural useful dependencies over large labelled P-256 bases without knowing d. The current implementation certifies arithmetic and finite-domain search only. There is one natural deterministic case, not a random statistical panel. Its complete empty result pertains only to its declared three domains. Fixture success, zero-Q examples, field polynomial roots, or label count cannot fill that requirement. Kudo's detailed hybrid/symmetry limitation remains a literature access gap; no external model/backend was probed.")
#parbreak()

#text("Next derive an exact partition-compatible solver for m=4 or higher with charged label construction, polynomial representation, specialization, rational sign recovery and memory. Compare its symbolic total against generic references before any performance trial. The decisive acceptance condition is a reproducible natural-instance solver and a justified success/cost model under independent labels, with blind points-only search, retained inverse/zero-Q controls and independent point verification. A proposed structured base must supply its label algorithm and label-distribution analysis first. Any scientific execution needs its own admitted protocol; none was launched here. See the scoped problem-record draft (problem-record.md) supplied to the Coordinator, whose write scope alone can update problems/ and its index.")
#parbreak()

#text("The checked existing graph is the study's original week-plan (no canonical mathematical edge is changed). This folder adds a derived implementation-flow diagram; no shared graph was edited because it was outside the assigned scope.")
#parbreak()
