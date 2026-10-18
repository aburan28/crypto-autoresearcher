# GOAL-ECDLP2M-001 iteration, 2026-10-09: derived audits

This directory holds pre-compute audits and derivations made during a read-only
`/deep-research` pass and a follow-up iteration on GOAL-ECDLP2M-001 (binary-field
ECDLP). Each one can be regenerated from the scripts here.

Nothing here is an experiment, a run record, evidence, or a decision. No ledger
record was written and no status changed. A conclusion becomes official only
through the normal lifecycle: a contract, `/run`, and a Coordinator archive or
correction. Every figure here is labelled measured, derived, or published, with
its provenance given in the sub-directory README.

| sub-directory | what it is | headline |
| --- | --- | --- |
| `certbin-k2-collision-audit/` | Replay audit of EXP-CERTBIN-66e167 Stage 1 (EV-CERTBIN-691499, DEC-20261004-d70aac) that classifies every colliding pair | The archived k=2 "excess" (17 and 38 pairs against a birthday expectation of 5.00) is an instrument artifact. Structural identities that hold for every generator account for 16/17 and 33/38 pairs. The kernel span held only 2G+tG+t^2G per generator, so it missed P+(-P) and the tau-shifted relations. The genuine collision ratios are 0.20, 0.40, 1.00 and 0.80. |
| `c1-gaudry-n4-c2pnb/` | Three-metric cost model: Gaudry-Diem fixed-n=4 double-large-prime index calculus with a pi_16 orbit factor base on the ANSI X9.62 example curves c2pnb176v1/208w1/272w1/304w1/368w1 | Time only, it beats matched rho on all five rows across c_trial in [2^15.5, 2^32.5]. Under the program's time x memory convention against vOW, it loses on every row inside that band. Under mesh area-time, it wins only on 304w1 and 368w1 at c_trial <= 2^27. The per-trial cost at toy size has never been measured. |
| `m3-closure-pilot/` | Exploratory pilot, not evidence: degree-4 mutant closure (W_4) on chained S_3 at m=t=3, n = 9..19, with exhaustive ground truth, a support-matched null, a dense null and an independent eliminator | W_4 refutes every UNSAT instance run: 60/60 at n=9, 40/40 at n=11, 8/8 at n=15. No SAT instance is refuted. Plain M_4 and M_5 refute none. The support-matched null is refuted (11/11) and the dense null is not (0/12), so the mechanism is the sparse support shape. n=19 is censored by memory. This is consistent with Assumption 1 at m=3. It is not a speedup: the cost is polynomial in N at fixed D, and m=3 is bound by its linear algebra. |
| `m45-closure-pilot/` | Exploratory pilot, not evidence: the same closure instrument at m = t = 4 (n = 7, 9, 11) and m = 5 (n = 7, 9), with both enumerators, both nulls and the independent eliminator | On every cell with a non-trivial factor base (k = 3, |V| = 8) the refuting degree is again exactly 4 and plain M_4 refutes nothing: m=4 n=9 10/10, n=11 2/2, zero false refutations. m=5 at D=4 was reachable only with |V| = 4 (10/10 at n=7, 1/1 at n=9 at 980 s and 7 GB); that |V| = 4 cell is degenerate (W_3 alone refutes 30/30 at n=9, while |V| = 8 gives 0/30), so the degree at m=5 with a real factor base is still unmeasured. The deciding cell (m=5, |V| = 8, D=4, about 112k columns) is beyond this host. |
| `block-local-closure-pilot/` | Exploratory pilot, not evidence: the degree-4 mutant closure restricted to monomials whose variables lie within L consecutive chain blocks (independent eliminator) | At m=3 and m=4 the W_4 refutation is essentially locality-1 (124/125 UNSAT refuted at L=1, the one miss refuted at L=2; 0/31 false refutations), with 39-69% fewer columns. At m=5 with |V|=8, the cell pilot #2 could not run, L=1 refutes 0/10 but L=2 refutes 5/5 at 170 s and 483 MB (65,649 columns instead of 124,314), and L2 is contained in W_4, so the minimal refuting degree is 4 at m=3, 4 and 5 with a non-trivial factor base (5/5 is a lower bound, CP95 [0.48, 1]). Restricting the multipliers destroys the refutation; the block-crossing products through the shared u variables are what carries it. |
| `m4-sat-cost-pilot/` | Exploratory pilot, not evidence: the first m=4 SAT cells (WDSat, vendored and sha-bound) on chained S_3, with the paper's own m=3 instances as the instrument gate | The gate reproduces 2^(3l)/3! (alpha 2.981 [2.973, 2.997]). At m=4 the per-attempt UNSAT conflict count grows with alpha 4.33 [4.32, 4.34] under Gaussian elimination alone and 4.09 [4.06, 4.12] with complete symmetry pruning (l = 3..5, seven cells), i.e. the 2^(ml)/m! exhaustive law transfers to m=4; the budget needs alpha < 1. Stock WDSat -b is incomplete on chained m >= 4; the complete symmetry variant is this pilot's patch. Chained S_3 only; no S_5 builder exists. |
| `tau-factor-base-pilot/` | Exploratory pilot, not evidence: exhaustive relation-yield accounting under the Frobenius tau and negation on toy Koblitz curves (n = 11..23, m = 2, 3) for three factor-base choices | tau buys exactly log2(n) bits for an orbit-union base (7.03 bits at n=131; the base is not a subspace), about 1 bit gross and 0.6-0.8 bit net for a normal-basis window, about 0 for the polynomial basis; the per-attempt decomposition probability at matched |FB| is the birthday heuristic for all three, so there is no second gain in the decomposition step. Reproduces the program's earlier 'exactly n and no more' reading. |
| `leads-pilot4/` | Exploratory pilot, not evidence: four candidate cuts to the degree-4 closure's per-attempt cost (u-bit caps, windowed closure, target-independent precomputation, the n=131 value of locality) and one pre-registered test at m=6 | Windowed closure refutes every UNSAT instance L2 refutes (m=4: 35/35, m=5: 5/5), always in the last window on the first forward pass, so the per-target work is one 2n+2k-variable window with a precomputed message. Precomputing the z-free closure cuts UNSAT per-target time 3-50x, SAT none. u-bit caps give nothing from m=5 on. Pre-registered: L2 refutes 1/5 at m=6 (predicted <= 1/5). Every toy cell sits where the closure can nearly interpolate the z-free solution set (log2 cols/solutions -2 to +5); n=131 sits below -100. F_(2^131) has no Frobenius-stable subspace of dimension 2..129. |
| `closure-rescope-audit/` | Derived audit of four records cited by 240, 148, 132 and 112 files, against the primary sources in `inputs/` | KR-IC-1fcdbc rests on Galbraith-Gebregiyorgis experiments at n <= 53, m <= 4, l <= 8 and a heuristic for n > 100; the same paper reports the degree of regularity staying at 4 (often 3 with symmetry breaking). KN-FIND-aa2efc's free-oracle floor is below rho for m >= 4. KR-IC-5ea2f8 is `proven` on abstract-level sources. KR-IC-46d822 labels the single-large-prime exponents 10/7 and 14/9 as double (4/3 and 3/2). Rho polishing has about 0.1 bit of headroom. Route: `/curate-knowledge`. |
| `ctrial-harvest/` | Every recorded per-attempt point-decomposition cost (411 rows, 1554 per-target values) from main and the unmerged branches, fitted against l and extrapolated to ECC2K-130 | At m=3 and m=4, measured per-attempt costs extrapolate 50 to 150 bits above every budget line at n=131. WDSat UNSAT conflict counts match exhaustive search, 2^(3l)/3!, with a slope of 2.9985 bits per unit l. m=5 and m=6 have no usable data. |

## The criterion these results share (derived)

Relation collection beats rho only if a failed decomposition attempt costs
2^(alpha*l) with alpha < m/2 - 1, where l is about n/m. Every measured SAT or
enumeration method has alpha of about m, so it never qualifies.

The only mechanism that could give alpha near 0 is refutation by closure at a
bounded degree D, where D does not grow with n. This has been measured only at
m=2 (KN-FIND-5a8d3e, -c3a917), where it cannot help because m/2 - 1 = 0. At m >= 3
it has not been measured (KN-OPEN-3c8f51 item B, KN-OPEN-d218ec). That question is
the dispute recorded in KR-IC-889857.

## Instruments and environment

- Python 3 with the standard library, plus sympy where noted. M4RI and Sage are not
  needed for these three audits.
- The CERTBIN audit imports the archived implementation unchanged from
  `experiments/EXP-CERTBIN-66e167/implementation/`. It reproduces the archived raw
  pair counts exactly: 17, 5, 38, 7.
- `SHA256SUMS` binds every file in this directory.
