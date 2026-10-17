#set page(paper:"a4",margin:16mm)
#set text(size:10pt)
#set par(leading:0.5em)
= Historical evidence inventory

#text("This inventory reproduces the existing local pilot scopes and limitations from the imported follow-up record. It is not an independent scientific review, harness execution-proof evidence, a status transition, or completion of the original full protocols.")

#text("E3 with E1/E2/E4 support is the recorded conditional research priority. No demonstrated attack advantage follows. The diagram shows obligations that must be charged and verified before a completed-operation comparison against the frozen index-calculus baseline. The rho gap is reported as the distance remaining.")

#image("dependencies.svg",width:100%)

#text("All 23 original leads retain their canonical IDEA identities in canonical-coverage.json and tracking.json. The original ledger, audit corrections, code, raw observations, local reports and requirements are preserved in sibling directories. The current canonical execution attempts, their failures and outstanding contracts are tracked separately in STATUS.md.")

#text("Toy controls have limited scope. A working prototype is finite control, never a subexponential ECDLP result. Original theorem-closed items remain receipt-only. No deployed-key recovery or NFS sieving is in scope.")

#text("Source of the following table: snfs-ecdlp-followup/all-lead-dispositions.json. Each row reproduces pilot_scope and full_protocol_limitations literally; historical conclusions and draft spending gates are not new approvals. Current execution and budget conventions remain those in STATUS.md.")

#text("Tracking PR: https://github.com/aburan28/crypto-autoresearcher/pull/2382")
#pagebreak()
#set text(size:8.2pt)
= Pilot scope and outstanding work
#text("Historical inventory: entries 1–8 of 23. Full original protocols remain outstanding.")

#table(columns:(0.7fr,2.0fr,3.3fr),inset:6pt,stroke:0.4pt + luma(190),align:top,table.header([*Lead*],[*Historical pilot scope*],[*Explicit limitations*]),
[#text("SNFS-A1")],[#text("Integer S3/S4 support reduction for three fixed curves and matched prime bit sizes")],[#text("No universal Z[a,b] support claim: coefficient specialization/reduction exceptions remain possible. | No full decomposition-throughput ratio or modular-reduction time share measured.")],
[#text("SNFS-A2")],[#text("Small S3 bivariate modular-lattice prototype with exact short-vector checks and root extraction")],[#text("Only two planted cases per cell; no 50%-recovery threshold or asymptotic exponent can be estimated. | Univariate monic Coppersmith controls passed; the required independent bivariate linear-control protocol is not implemented, so these multivariate numbers remain diagnostic. | No BKZ-20, dimension-200 sweep or S4 lattice experiment. | Timeouts are censored, not failures.")],
[#text("SNFS-A3")],[#text("Completed two-point decomposition: enumeration versus bit-vector SAT, interval and compositional subgroup bases")],[#text("SAT uses Z3 bit-vector arithmetic, not CryptoMiniSat/WDSat. | Small m=2 pilot only; no m=3, F4/F5 or completed relation/matrix index-calculus campaign. | No solver exponent fit: range is small and timeout censoring is material. | Factor-base setup and target solving are recorded separately; total cost must include both.")],
[#text("SNFS-A4")],[#text("Valid integral digit-ring maps and closure measurements with matched random-subset controls")],[#text("The original n,d grid has no valid pairs; this is an explicitly corrected small grid. | Digit-ring lifting/factorization of S3 and a matched random-prime closure experiment remain unrun. | Finite closure deviations are not evidence of an algebraically closed factor base.")],
[#text("SNFS-B1")],[#text("Torsion section and lift-independence modulo p^2; original statistic is identically zero")],[#text("No ramified extensions or higher precision tested. | Rescaled uniformity is an exhaustive fixed-point/fixed-curve-lift calculation, not a general mutual-information estimate.")],
[#text("SNFS-B2")],[#text("Known-answer Smart controls on four anomalous class-number-one CM curves modulo p^2")],[#text("No Hilbert class polynomial computation beyond four explicit degree-one polynomials. | Canonical-lift degeneracy was checked modulo p^2 only; no higher-precision implementation.")],
[#text("SNFS-B3")],[#text("Reduced Tate-pairing positive controls at embedding degree one")],[#text("Generalized-Jacobian divisor/function arithmetic was not implemented, so no independent connecting-map/Miller agreement claim. | Extension-field k=2,3 tests remain unrun.")],
[#text("SNFS-B4")],[#text("Small-field embedding-order distribution pilot with exact orders")],[#text("Small samples do not establish equality of distributions at cryptographic sizes. | CADO-NFS polynomial selection and Murphy-E comparisons were not run; no sieving was performed. | Curve25519 public-parameter order computation was not attempted.")],
)

#pagebreak()
#set text(size:8.2pt)
= Pilot scope and outstanding work
#text("Historical inventory: entries 9–16 of 23. Full original protocols remain outstanding.")

#table(columns:(0.7fr,2.0fr,3.3fr),inset:6pt,stroke:0.4pt + luma(190),align:top,table.header([*Lead*],[*Historical pilot scope*],[*Explicit limitations*]),
[#text("SNFS-B5")],[#text("Finite cyclic-kernel Ext quotient sanity table")],[#text("Not an enumeration of generalized-Jacobian moduli or a computational classification of all transfers. | Receipt covers only the finite kernel divisibility calculation.")],
[#text("SNFS-B6")],[#text("Explicit zero-dimensional factor bases described by repeated squaring")],[#text("Demonstrates compact equations for small algebraic bases; it does not demonstrate cheap point decomposition. | Does not contradict a correctly scoped bounded-degree positive-dimensional Hasse-Weil statement.")],
[#text("SNFS-B7")],[#text("Genus-two split-cover point-count and isogeny-order control")],[#text("No Jacobian index calculus or rho comparison executed; no complexity exponent inferred. | Genus-three covers and descent-direction implementation remain unrun.")],
[#text("SNFS-C1")],[#text("Frobenius-order class-number sampling and a rational-CM exception")],[#text("These are class numbers of Z[pi], not certified End(E) orders. | No general canonical-lift Newton algorithm or endomorphism-ring algorithm executed. | Small-CM rational j is an exception to a universal statement, not evidence about typical random j.")],
[#text("SNFS-C3")],[#text("Exhaustive Teichmuller representatives at one small prime, with matched uniform-unit samples")],[#text("No proof of pseudorandomness or asymptotic Dickman behavior. | One-prime finite distribution; sparse counts require uncertainty and more primes before interpreting ratios.")],
[#text("SNFS-D1")],[#text("Exact rank-one sublattice count/sumset control and reduction coverage")],[#text("No certified rank-5 to rank-31 lattices or saturation certificates were available. | This tests a non-torsion cyclic sublattice, not the full high-rank hypothesis or its cryptographic thresholds.")],
[#text("SNFS-D2")],[#text("Fixed-small-curve lift control against a blanket log(p) height inference")],[#text("No rank distribution, conductor matching, 2-descent or full small-point coverage experiment executed. | This selected family is not a random-lift ensemble; it does not refute an empirical average-rank hypothesis.")],
[#text("SNFS-D3")],[#text("Two-point fitted rational lifts; exhaustive small-coefficient dependence search")],[#text("Absence of a relation with |c_i|<=2 does not certify independence or rank. | The k=3,4 parametrized fitting families and exact full rank certificates remain unimplemented.")],
)

#pagebreak()
#set text(size:8.2pt)
= Pilot scope and outstanding work
#text("Historical inventory: entries 17–23 of 23. Full original protocols remain outstanding.")

#table(columns:(0.7fr,2.0fr,3.3fr),inset:6pt,stroke:0.4pt + luma(190),align:top,table.header([*Lead*],[*Historical pilot scope*],[*Explicit limitations*]),
[#text("SNFS-D4")],[#text("Rank-one support falsification of the proposed smoothness/kernel independence test")],[#text("Rank-r net recurrence and HNF reconstruction were not implemented. | For every nonzero integral W and B<p, B-smooth(W) implies p does not divide W. This logical exclusion invalidates the original independence trigger; a nonzero MI here is not an exploitable attack signal. | The p-cofactor variant W/p requires prior kernel membership and does not itself find relations.")],
[#text("SNFS-D5")],[#text("Small-field EDS linear-complexity profiles and held-out quadratic recurrence controls")],[#text("No universal L/2 profile asserted; value period and zero-apparition rank are distinct. | Search covers quadratic degree and span four, not all degree-three/span-eight systems. | No period-finding acceleration or 40-bit-order sequence experiment demonstrated.")],
[#text("SNFS-E1")],[#text("Eight prescribed-fibre split rational surfaces, plus explicit nonconstant j-image controls")],[#text("Rank eight follows from checked split cubic-pencil geometry; no random-surface zeta-function rank experiment. | No higher-chi rank-growth construction tested; j-image samples are not conditioned on high rank.")],
[#text("SNFS-E2")],[#text("Exact height lattice of the constructed split rational surfaces")],[#text("This is a selected E8 family with chi=1, not a universal height theorem for arbitrary surfaces. | No empirical D2 random-lift height comparison or chi=2,3 surface experiment.")],
[#text("SNFS-E3")],[#text("Fresh-target low-section interpolation search, bounded-MW oracle MITM, and known-answer rho")],[#text("Geometry search covers 92 known height-two section classes only; it is not a general bounded-height section solver. | MITM is oracle-assisted group search; no blind F4/F5/SAT rational-section coefficient-system solver was executed. | Success on planted low sections does not establish fresh-target coverage. | Precomputation, pencil construction and query costs are reported separately; shared precomputation cannot be silently omitted. | MW-coordinate recovery for these explicit classes is exact from the determinant-one Gram matrix; no kernel-relation collection is required because basis specialization logs are known by construction.")],
[#text("SNFS-E4")],[#text("Complete E8 short-vector counts and actual specialization coverage")],[#text("Exact enumeration verified against the first four E8 theta-series counts. | Coverage is measured on eight selected rank-eight surfaces, not extrapolated to rank 100 or 300. | Independent occupancy and volume expressions are reference heuristics, not proofs of uniformity.")],
[#text("SNFS-F1")],[#text("Actual pseudo-Mersenne degree-one reductions of a fixed new non-torsion quadratic-field point")],[#text("No number-field descent, cubic/quintic fields, rank-gain distribution or full bounded-height coverage measurement executed. | The selected fixed curve/field supplies a height control, not a claim about a random ensemble.")],
)
