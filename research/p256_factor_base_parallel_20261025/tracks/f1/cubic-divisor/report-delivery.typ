#set page(paper: "a4", margin: (x: 1.6cm, y: 1.5cm), footer: context align(right, text(size: 8pt, counter(page).display("1"))))
#set text(font: "Liberation Sans", size: 9pt, lang: "en", ligatures: false)
#show raw: set text(font: "Liberation Mono")
#set par(justify: false, leading: 0.55em)
#set heading(numbering: none)
#show heading: set block(above: 0.8em, below: 0.4em)
#heading(level: 1)[#text("F1 continuation: reduced cubic-divisor membership on P-256")]
#figure(image("diagram.svg", width: 100%, height: 5.4cm, fit: "contain"), caption: [Editable study diagram; exact scope and evidence paths appear in the report.])


#text("2026-10-25 · TASK-20261025-13c38e · exact implementation and solver-formulation validation. This continuation completes the fixed k=3 membership+S4 target that the original forward formulation left unknown. It also proves and checks reduced membership ideals for all coordinate-multiplicity strata. Distinct-coordinate solving at k=4 remains unknown after three fresh bounded attempts. No performance trial, speed advantage, asymptotic benefit or official research transition is claimed.")
#parbreak()

#heading(level: 2)[#text("Inputs, scope and representation")]

#text("The original F1 package and this card were supplied as pushed commit c35b9da6a65e019eaa517fc1a5f7774428ff35db. All output is under this new tracks/f1/cubic-divisor/ directory; original evidence is unchanged. The exact published P-256 p,a,b,r and 35-term symmetric S4 are inherited from the committed baseline and original F1 source. execution.json (execution.json) binds their hashes and the source/commands used here. No Git, PR, shared-file or external service action was performed.")
#parbreak()

#text("Use F(t)=D_(2^k)(t)−c with c≠±2 and the monic cubic h=t³−s1 t²+s2 t−s3. Repeated squaring computes the three coefficients of F mod h without constructing D_(2^k) densely. Setting them to zero means h divides F. For separable F this automatically selects three distinct coordinate roots. It avoids the earlier triple-equal terminal's scheme multiplicities, while repeated coordinates are preserved through separate systems.")
#parbreak()

#text("The exact three-stratum construction and its proof are in derivation.md (derivation.md):")
#parbreak()

#table(columns: 3, inset: 4pt, stroke: 0.3pt + rgb("#b0bdc9"), [#text(size: 8pt, "Coordinate stratum")],
[#text(size: 8pt, "Equations before S4")],
[#text(size: 8pt, "Geometric membership points")],
[#text(size: 8pt, "Three distinct")],
[#text(size: 8pt, "Three coefficients of F mod h vanish")],
[#text(size: 8pt, "C(S,3)")],
[#text(size: 8pt, "Exactly two equal (x,x,y)")],
[#text(size: 8pt, "F(x)=0 and Δ_F(x,y)=0")],
[#text(size: 8pt, "S(S−1)")],
[#text(size: 8pt, "All equal (x,x,x)")],
[#text(size: 8pt, "F(x)=0")],
[#text(size: 8pt, "S")])

#text("Here Δ_F=(F(x)−F(y))/(x−y) is a polynomial computed by a short circuit. On the diagonal it equals F'(x), so separability excludes x=y without a saturation variable. Each ideal is reduced. Joining S4 keeps a subset of a finite reduced algebra and therefore remains reduced. All tested F split completely over Fp, so all geometric points are rational. This rationality is checked rather than assumed from the field size.")
#parbreak()

#heading(level: 2)[#text("Completed solver and completeness checks")]

#text("The algebraic adapter expands the remainder coefficients, joins S4, constructs a grevlex Groebner basis, then performs exact lex/root extraction. Each successful basis checks original generator reductions, every critical pair, basis vanishing on every complete reference zero, and equality of finite quotient dimension with that zero count. A separate implementation of sparse modular polynomial division replays these certificates without calling SymPy. Complete geometric references are enumerated for certification; they do not feed coefficients or roots into the Groebner search. The delivered validation harness includes that exhaustive reference work and does not claim to avoid its cost.")
#parbreak()

#text("All accepted coordinate states are factored and fully lifted with signs on P-256. The three strata's signed solutions are united and compared with a separate exhaustive signed-point triple implementation. Equal x-coordinates can lift to opposite points; this includes inverse-pair cancellations.")
#parbreak()

#table(columns: 4, inset: 4pt, stroke: 0.3pt + rgb("#b0bdc9"), [#text(size: 8pt, "Fixed public query")],
[#text(size: 8pt, "Distinct / two-equal / all-equal S4 states")],
[#text(size: 8pt, "Signed point solutions")],
[#text(size: 8pt, "Algebraic completeness")],
[#text(size: 8pt, "k=2 constructed positive")],
[#text(size: 8pt, "1 / 0 / 0")],
[#text(size: 8pt, "1")],
[#text(size: 8pt, "Complete")],
[#text(size: 8pt, "k=3 original constructed positive")],
[#text(size: 8pt, "1 / 0 / 0")],
[#text(size: 8pt, "1")],
[#text(size: 8pt, "Complete")],
[#text(size: 8pt, "k=3 constructed two-equal coordinates")],
[#text(size: 8pt, "0 / 1 / 0")],
[#text(size: 8pt, "1")],
[#text(size: 8pt, "Complete")],
[#text(size: 8pt, "k=3 constructed all-equal coordinates")],
[#text(size: 8pt, "0 / 0 / 1")],
[#text(size: 8pt, "1")],
[#text(size: 8pt, "Complete")],
[#text(size: 8pt, "k=3 base-member cancellation control")],
[#text(size: 8pt, "0 / 7 / 1")],
[#text(size: 8pt, "7")],
[#text(size: 8pt, "Complete")],
[#text(size: 8pt, "k=3 published generator G")],
[#text(size: 8pt, "0 / 0 / 0")],
[#text(size: 8pt, "0")],
[#text(size: 8pt, "Complete empty set")],
[#text(size: 8pt, "k=4 original constructed positive")],
[#text(size: 8pt, "unknown / 0 / 0")],
[#text(size: 8pt, "unknown; reference has 1")],
[#text(size: 8pt, "Partial: distinct solver stopped")])

#text("The k=3 fixed terminal and public target are the original fixture. k=2 uses its same subfibre as the earlier forward adapter. k=4 uses the committed generic k=4 fixture. These solver fixtures have actual canonical base sizes M=4,7,10, respectively; the k=2 subfibre differs from the first package's matched-M=3 coset. Exact c, targets, roots, signed bases, all accepted states and all point witness indices are retained in the result and recombination files. Constructed positives establish correctness only. The fixed G empty check is a finite-domain fact, not a uniform-target sampling result. Base cancellations are controls and are not counted as independent useful relations.")
#parbreak()

#text("Additional exact outcomes:")
#parbreak()

#block(inset: (left: 8pt))[#text("• Membership-only k=3 gives a reduced quotient of dimension 56=C(8,3), 28 basis")]

#text("polynomials and 378 checked critical pairs. These are exact algebraic counts.")
#parbreak()

#block(inset: (left: 8pt))[#text("• Across 21 successful algebraic attempts, the separate sparse verifier checks")]

#text("386 critical pairs. All 21 certificates pass.")
#parbreak()

#block(inset: (left: 8pt))[#text("• Complete linear factorization, divisor identities, nonzero Jacobians and the")]

#text("equality det Jacobian=Res(h,F/h) are checked at all 4+56+560 distinct divisors for S=4,8,16 over the actual field.")
#parbreak()

#block(inset: (left: 8pt))[#text("• Forty deterministic actual-field coefficient cases compare symbolic remainder")]

#text("circuits with independent polynomial long division and automatic derivatives.")
#parbreak()

#block(inset: (left: 8pt))[#text("• Seven three-distinct divisor/remainder/nonzero-Jacobian witnesses reach depths")]

#text("k=6,7,8,16,32,64,96. They certify representations, not complete high-depth solves.")
#parbreak()

#block(inset: (left: 8pt))[#text("• The out-of-scope actual-field control F=D8−2, h=t³−4t divides F but has zero")]

#text("remainder Jacobian determinant. This checks that separability is a substantive hypothesis for the proof; it does not classify every nonseparable fibre.")
#parbreak()

#heading(level: 2)[#text("Preserved unknown attempts and costs")]

#text("attempts-01/receipt.json (attempts-01/receipt.json) retains 22 sequential attempts: 21 complete, one stopped. The default SymPy Buchberger k=4 distinct-positive attempt stops during basis construction. attempts-02/receipt.json (attempts-02/receipt.json) retains two fresh F5B attempts, for that k=4 positive and the fixed generator; both stop during basis construction. Each has a declared 30-second watchdog and 2 GiB process address-space cap. Native stdout/stderr remain per attempt. No stopped case has an empty-set or completeness label. The original F1 watchdog is left unchanged in its original directory.")
#parbreak()

#text("No timing or peak-memory benchmark was collected, and no adapter comparison is inferred. Environment: the pinned /workspace/dickson-solver/.venv/bin/python, CPython 3.12.14, SymPy 1.14.0, python-flint 0.8.0. The inherited native Codex runtime/model binding remains unprobed; same-session replay is not independent scientific review.")
#parbreak()

#text("With fixed h-coefficient products shared, a uniform remainder step has 3 field squarings, 9 general multiplications, 3 small-constant scalings and 8 additions. This is an arithmetic-circuit count. Polynomial expansion still grows:")
#parbreak()

#table(columns: 4, inset: 4pt, stroke: 0.3pt + rgb("#b0bdc9"), [#text(size: 8pt, "k")],
[#text(size: 8pt, "S")],
[#text(size: 8pt, "Expanded coefficient degree")],
[#text(size: 8pt, "Nonzero terms (R0,R1,R2)")],
[#text(size: 8pt, "2")],
[#text(size: 8pt, "4")],
[#text(size: 8pt, "2")],
[#text(size: 8pt, "2,2,3")],
[#text(size: 8pt, "3")],
[#text(size: 8pt, "8")],
[#text(size: 8pt, "6")],
[#text(size: 8pt, "10,13,14")],
[#text(size: 8pt, "4")],
[#text(size: 8pt, "16")],
[#text(size: 8pt, "14")],
[#text(size: 8pt, "67,85,81")],
[#text(size: 8pt, "5")],
[#text(size: 8pt, "32")],
[#text(size: 8pt, "30")],
[#text(size: 8pt, "496,575,546")])

#text("The generic cubic-divisor quotient has length C(S,3), versus S³ for the earlier symmetric-terminal representation; the full reduced union has C(S+2,3) states. These representation facts do not bound solver runtime, certificate-generation cost, target success, or total ECDLP complexity. The current algebraic adapter expands the input; the circuit code and deep witnesses keep the short formulation available for further work.")
#parbreak()

#heading(level: 2)[#text("Artifacts and reproduction")]

#block(inset: (left: 8pt))[#text("• checks-01/receipt.json (checks-01/receipt.json): six complete query unions and")]

#text("one partial unknown; individual files contain full witnesses.")
#parbreak()

#block(inset: (left: 8pt))[#text("• checks-01/identities.json (checks-01/identities.json): exact factor, Jacobian,")]

#text("circuit, gradient, hypothesis-control and deep-witness results.")
#parbreak()

#block(inset: (left: 8pt))[#text("• basis-replay-01.json (basis-replay-01.json): independent-code replay of 21 bases.")]

#block(inset: (left: 8pt))[#text("• execution.json (execution.json): source/input identities, exact commands and")]

#text("environment; native logs remain alongside their receipts.")
#parbreak()

#block(inset: (left: 8pt))[#text("• packed-artifacts.json (packed-artifacts.json): the 71,029-byte native membership")]

#text("certificate is retained losslessly as gzip with its original byte hash. Its receipt still binds the decompressed bytes. No data was omitted.")
#parbreak()

#block(inset: (left: 8pt))[#text("• diagram.svg (diagram.svg): editable vector explanation; aggregate PDF rendering")]

#text("belongs to the Coordinator.")
#parbreak()

#text("For a fresh single-case replay from the repository root, choose a previously unused output path:")
#parbreak()

#text(size: 7.2pt)[#raw("TRACK=research/p256_factor_base_parallel_20261025/tracks/f1/cubic-divisor\nPYTHONDONTWRITEBYTECODE=1 /workspace/dickson-solver/.venv/bin/python \"$TRACK/solve.py\" \\\n  --case \"$TRACK/../checks-02/generic-k3.json\" --depth 3 \\\n  --stratum distinct --target positive --out \"$TRACK/replay-distinct-k3-new.json\"", block: true)]

#text("The two supervisor scripts and check script deliberately refuse existing result directories; preserve the delivered records. verify_basis.py reads either native JSON or its exact gzip representation. Source inputs and frozen receipt hashes are retained, including the stopped attempts' reconstructible equations.")
#parbreak()

#heading(level: 2)[#text("Remaining obligation")]

#text("The nonreduced generic membership obstacle now has an exact replacement on all three strata. The separate obstacle is a certified global elimination method and cost bound for the unexpanded circuit. problem.md (problem.md) records that change and the next discriminating step: implement incremental elimination on the multiplication-gate circuit and replay unchanged k=3 and k=4 positive/empty controls, retaining complete or unknown outcomes. Relation rank, labels, setup, linear algebra and final target attachment remain separate ECDLP obligations.")
#parbreak()

#text("No shared graph or problem index was edited. The Coordinator should link this progress into the original F1 problem and include the new report/diagram in the aggregate PDF. Neither filing nor archiving this package changes a hypothesis.")
#parbreak()
