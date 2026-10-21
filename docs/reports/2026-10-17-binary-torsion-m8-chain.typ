#set page(paper: "us-letter", margin: 0.62in)
#set text(font: "New Computer Modern", size: 9.5pt)
#set heading(numbering: "1.")

= Eight-summand chained torsion-coordinate witness

_2026-10-17 · One planted correctness witness on the certified ordinary-binary GF(2^61) fixture._

== Exact chain

Take eight raw points from the target-blind torsion-coordinate base. Let $U_i=sum_(j=1)^(i+1) P_j$ for $i=1,dots,6$ and $S=U_6+P_8$. The chain has seven $P_(phi,3)$ equations: $P_(phi,3)(t(P_1),t(P_2),t(U_1))=0$, five links through $U_2,dots,U_6$, and $P_(phi,3)(t(U_6),t(P_8),t(S))=0$. The independent Sage replay checked all seven equations and the full point sum. This is an eight-summand chained system; a direct eighth summation polynomial represents seven summands plus target.

The projected subgroup target is $R=[4]S$. Its four raw preimages are $R_0+j T$ for $j in {0,1,2,3}$, where $R_0=[4^(-1) mod r]R$ and $T$ has order four. The planted sum occupies channel 0. The other three final equation values for this particular chain are nonzero; their other possible decompositions remain untested. One channel has 8 × 10 + 6 × 61 = 446 Boolean variables and 7 × 61 = 427 coefficient equations before lift, pole, sign, and verification branches. These are structural counts, not solver measurements.

#figure(image("2026-10-17-binary-torsion-m8-chain.svg", width: 93%), caption: [Seven verified equations and 128 checked torsion presentations of one projected row. The larger permutation count is a group-level combinatorial identity, not a solver-root count.])

== Duplicate accounting and next gate

Every even subset of the eight points can be shifted by the rational two-torsion point without changing their raw sum or projected coefficient row. The producer and Sage replay checked all 128 even masks: 128 distinct ordered coordinate tuples, one row, rank contribution at most one. Permuting summands gives $8! times 128 = 5160960$ ordered group-level tuples. Some finite-coordinate chains may encounter poles; no unknown-target relation search or degree-of-regularity measurement was run.

The next frozen comparison must price equation construction, actual solver degree and memory, curve lifts, signs, four target channels, verified useful rank, linear algebra, reconstruction, and matched rho on identical unseen targets. The full-width arity-grid obstruction remains open. Source, exact inputs, replay, and scope details are in the companion Markdown report and `research/icperf_binary_torsion_m8_chain_20261017/`.

Canonical frontier graphs were checked and remain unchanged because this record has no reviewed complete-cost result.
