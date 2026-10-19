#set page(paper: "a4", margin: 1.7cm, numbering: "1")
#set text(font: "New Computer Modern", size: 10pt)
#set heading(numbering: "1.")
#show table: set text(size: 8.5pt)

= Evidence review: does the 2-isogeny-chain factor base help decomposition?

*Decision* DEC-20261015-a08389: *reject_scoped* H-ECDLP-60de36 · *evidence* EV-ECDLP-6bdff6 (contradicts, preliminary, toy tier) · *validation* VAL-20261015-1c3bff · *runs* RUN-ECDLP-f49f75-01, -02, -03 · *experiment* EXP-ECDLP-f49f75 · *goal* GOAL-ECDLP-001.

*Scoped claim.* For prime $p equiv 3 med 4$ with $2^L | p+1$, $p <= 23$ bits, and Semaev $m in {2,3}$, encoding the factor-base set $V = x(R + ⟨K⟩)$ (the fibre of a chain of $L$ Vélu 2-isogenies from $y^2 = x^3 + x$) by its chain equations makes Gröbner decomposition (Singular `std`/`slimgb` + `fglm`) *slower* than the dense encoding of the same set, and no faster than a random set of the same size; enumeration beats every Gröbner arm.

== Question

The proposal (user, 2026-10-15) builds a P-256 factor base $cal(B) = {(u,v) : Phi_x (u) = x(Phi(R))}$ from a 44-step 2-isogeny chain on $E_0: y^2 = x^3 + x$ (P-256 has $2^96 | p+1$), and needs a decomposition $T = P_1 + dots + P_6$ in $tilde(O)(|cal(B)|)$ for an $N^(1/3)$ attack. This is the Petit–Kosters–Messeng construction (PKC 2016, recalled). The experiment asks the cheapest question first: does the short chain description give a solver *any* advantage at toy scale?

== Observation

#figure(image("cost-vs-L.svg", width: 100%), caption: [Median decomposition time vs $L$ ($|V| = 2^L$), arms A (chain), B (dense, same set), C (dense, random set), E (enumeration); n = 6 per cell; × = all instances timed out at 600 s. Measured.])

#figure(image("criteria-ratio.svg", width: 85%), caption: [Frozen criterion 1: median time of A over B per jointly completed cell, both solvers (derived from measured medians; `criteria.json`). A threshold of 1 would be parity.])

#table(columns: 3, stroke: 0.4pt,
[*frozen criterion*], [*threshold*], [*observed*],
[A faster than B, jointly completed cells], [≥ 80% to support; A ≥ B in ≥ 80% falsifies], [std: 0/8 faster; slimgb: 0/8 faster (7 slower, 1 tie at 1 ms)],
[m = 3 retirement], [A completes larger L than B and C to support; A retired at L ≤ theirs falsifies], [A retired at L = 5; B and C completed L = 5],
[positive control], [100% planted in variety], [248/248 (non-excluded cells)],
)

== Comparison

- The A/B gap grows with $L$: 2× → 654× (std) at m = 2, L = 3 → 8; 5.6× → 35× at m = 3, L = 3 → 4. The chain replaces one degree-$2^L$ equation per point by $L$ quadratics, multiplying the variable count by $L$; eliminating the auxiliary variables gives exactly arm B's polynomial (validator check), so A and B define the same variety.
- B and C are indistinguishable: the solver cannot see that $V$ came from an isogeny.
- Enumeration (E) needs ~$2|"FB"|^(m-1)$ group operations (629 at m = 3, L = 5) and is orders of magnitude cheaper than any Gröbner arm at every cell.

== Inference

The chain encoding supplies no solver advantage at toy scale under this instrument; it is a growing slowdown. The isogeny structure lives in $E_0$'s group law, which shares no homomorphism with the target curve's addition, and the experiment found no indirect effect either. The decomposition step the proposal needs remains unsolved (problem record `problems/pkm-isogeny-chain-factor-base-no-fast-decomposition.md`).

== Limitations

- Toy scale ($p <= 23$ bits), $m <= 3$; P-256 needs $m = 6$, $L = 44$. One solver family (Singular); msolve/Magma F4 were not available.
- Process: RUN-01 Gröbner cells m = 2, L ≥ 8 invalidated by a launcher int overflow (AMD-02), re-run as RUN-03; m = 2, L = 12 and m = 3, L = 6 not executed (host 2 h limit; neither can affect the criteria). Manifests were written post-run; hand-typed amendment timestamps corrected in NOTE-01. Validator verdict `incomplete` on records only; its idle-host re-run of 48 instances matched every deterministic field and timings within ~15%.
- 1 ms timer resolution at small L; four workers on four vCPUs.

== Next actions

+ Keep the problem record open; next discriminating step: the m = 3 grid under an F4 solver with first-fall/regularity degrees when msolve is available.
+ No further P-256 work on this route until a solver beats the dense and random controls on this frozen grid.
