# Design: Miller primitive U = f_{N,P}^{1/N}, exact K1/K2 and spectrum test

## Lead and question
LEAD-EXO-miller-pairing-cocycle (open_next_step) and LEAD-TRF-miller-cocycle-nonhom-transfer (open_unexamined) are one mechanism on IDEA-20261017-e3a6f1 (K1, K2, H1). Question: for prime-order E/F_p, N not dividing p-1, is chi_a(U(kP)) character-flat in k and equidistributed, as a random function would be, by the same detector that finds the planted Tate character at N | p-1?

## What the lead already says
The idea's own prediction is a white spectrum, ratio success 1/p, positive control peaked (H1; notes section 4). The EXO lead says K2 plus "r_k needs k" collapses U into the closed elliptic-net lead (LEAD-EXO-elliptic-net-eds); TRF says equidistribution closes it. Neighbours: LEAD-TRF-one-point-self-pairing (closed: a self-pairing needs E[N] rational, so the N | p-1 control needs k_emb=1), LEAD-TRF-mov-small-embedding-degree (closed_known; k_emb ~ N here), LEAD-STR-class-group-ecdlp-bridge (open, unrelated: no bridge map is used). KR-RHO-53c89f, KR-RHO-13bf67: no rho comparison is made.
**The lead predicts a NULL.** Candidate-4's Kummer identification (U is a degree-N function on E/G) is textbook, recalled; I checked it is self-consistent (fibre of the dual isogeny is a mu_N-torsor with one rational point; div U has degree N, Abel-Jacobi sum O). **Its proposed test (a) is dropped**: evaluating the "Kummer generator" on a Velu model of E/G is circular (the generator is defined as the root), and the dual isogeny has kernel mu_N, defined over a field of degree ord_N(p) ~ N. Also dropped: "regress out the k log gamma term" (it breaks Z/N-periodicity; a random factor times a linear phase stays flat, so a peak is only shifted, never hidden).

## Hypotheses
H0: K1, K2 exact on every cell; spectrum flat (add-one p >= 0.05/208 on every cell and channel); positive control 15/15. Expected outcome. H1: an AC peak (j != 0) with p < 0.05/208 that replicates on fresh-seed cells, at the base-point-transformed frequency, and not in the shuffled arm.

## Instances (seeds: sha256(protocol_hash, arm, instance, replicate))
- T1: size class s in {10,12,14,16,18}, N prime in [2^s+8, 1.1*2^s], p-form crossed {p-1 64-smooth, generic}, 8 curves each = 80 cells, E(F_p)=G prime order. Table logs. Window k=2..2^s+1.
- T2 (smooth-(p-1) instrument): p of 48/56/64 bits with p-1 2^12-smooth (random smooth m, p=m+1 prime), prime-order curve via PARI `ellcard` (SEA, ms at 64 bit), full F_p^* log by Pohlig-Hellman. 4 curves per size, 2^16-point contiguous and strided window = 24 cells. 104 candidate cells total, plus 4 exact-only cells at N~2^20 (K1/K2 only).
- Multipliers A (24): {1, 2, N mod p-1}, (p-1)/q^v and (p-1)/q for q | p-1 ascending, seeded random fill.

## Arms and controls
Candidate `cand-miller-U`. Reference `ref-recursion` (K2 recursion from two Miller seeds, an independent algorithm). Baseline `base-point-hash` (PRF of x(kP)). A/A `aa-second-base` (base point sP, next primitive root; 24 cells). **Positive** `pos-k1-tate`: 15 cells, k=1 Cocks-Pinch j=0 curves (N in 1009..2^18, N | p-1, E[N] rational, p-1 = N * smooth), U := f(kP), same `miller_value`/`dlog`/`spectrum` functions; the order-N character is an exact linear phase, must be flagged at the predicted bin. Plus `pos-planted`: eps in {0.008,0.016,0.032,0.064} planted on candidate sequences, giving the minimum detectable amplitude. **Negative** `neg-random-fn` (10000 iid draws per class, same L, |A|, code path) and `neg-shuffle` (candidate values permuted: separates marginal bias from k-dependence).

## Counted metrics
Exact: K1 rate (2000 pairs/cell, one sign eps per curve), K2 rate (every admissible k). Derived: max normalised AC power over (a, bin), DC power, add-one empirical p. Counted: charged field M/S/I (inversion = 1 whatever the algorithm; FFT, PRF uncharged and listed), collision count vs Poisson (stands in for the lead's undefined "Smart-ratio success"). No clock.

## Decision rule and consequences
Gate: pos_detect 15/15, no neg-shuffle flag, else `invalid_measurement`. K1 fails: withdraw the idea's record; K2 only fails: cocycle statement stands, EDS form withdrawn; both leads stay open. **No flag: confirm closure** (recommend EXO closed_obstructed by collapse into the elliptic-net lead, TRF closed on measurement; disposition is the Coordinator's). DC-only flag: marginal non-uniformity, no reopen. **AC flag: run 8 pre-listed fresh-seed cells; reopen if >= 2 flag at p<0.01, A/A shows the peak at frequency j/s, and shuffle does not.** That is "a non-flat spectrum that depends on k"; it advances next_action to a charged rho comparison with r_k charged, after independent review. Outcome falsifying the current disposition (closure): exactly that.
p-value resolution: n=10000, 2/(n+1)=1.9998e-4 < alpha/m = 0.05/208 = 2.404e-4 (208 = 104 cells x AC/DC, Bonferroni). Power argued separately: eps_min ~ 1.1*sqrt(ln(24M)+9.2)/sqrt(M), about 0.15, 0.04, 0.02, 0.011 at M=2^10..2^18; a null excludes only linear-phase amplitudes above that.

## Inadmissible moves
Regressing out gamma^k; changing multipliers, windows, alpha or draws after a p-value; reading a DC-only or unreplicated flag as a signal; reading toy flatness (or a 2^16 window of a 2^64 group) as a full-size or full-group claim; any rho, cost or clock claim; dropping control misses.

## Cost
Implementation ~1200 lines Rust (Montgomery u64/u128 field, projective Miller with second chain, Pohlig-Hellman/BSGS, radix-2 FFT, PRF, JSONL rows) plus ~300 lines Python orchestration; 3-5 days. Compute: cells ~15 min; nulls 10000 draws x 5 classes ~4.6 core-hours; total ~1.5 h on 4 cores (estimate, not measured).

## Implementation plan
Rust for everything numeric; PARI/gp (installed, v2.15.4) and Python only for curve search and analysis. Repo search: no Rust Miller/Pohlig-Hellman exists; `tools/lattice_ic_pairing.py` has a Python Miller with poles exposed (read before reuse, checker only); `experiments/EXP-ECDLP-84af7b` has a Rust field crate (read before reuse). Export via `experiment_protocol.py from-rows`. Counted unit defined above; ecbench is not required.

## Independent checker
Python + gp, no code shared with the runner: re-derives #E (`ellcard`), order of P, p-1 factorisation; for nonce-sampled k recomputes the Miller value on a different chain (affine, NAF), the root and the log (`znlog`); recomputes K1/K2 on sampled pairs; recomputes 20 recorded spectrum bins by direct DFT sum; for positive cells compares f^((p-1)/N) with gp `elltatepairing`; recomputes p-values from the recorded null draws. Tamper test: change one recorded ell, one K1 sign, one null draw, one peak bin; the checker must reject each.

## Open risks
(1) Normalisation and sign conventions: K1 holds up to eps = -1 in the probe; collisions with the Miller chain hit 28 of 1011 k there (about 2%), refilled on a second chain. (2) With 10000 draws the empirical tail is resolved only to 2e-4; the analytic Exp(1) tail is a cross-check, not a decision. (3) iid-with-replacement null is slightly conservative when M/(p-1) ~ 1; neg-shuffle is the exactly matched null. (4) T2 windows test local structure only. (5) Only E(F_p) = G (prime order); cofactor cases untested. (6) "Smart-ratio success" is undefined in the lead text.

**Feasibility probes (not results).** `python3 probe_k1k2.py` (p=1009, a=1, b=14, N=1013): 982 of 1011 k computed, K1 ratio single value 1008 = -1 on 2742 pairs, K2 telescoped constant 113 for all k. `gp -q probe_k1curve.gp`: k=1 control exists, e.g. p=13240099, group [13117, 1009], p-1 = 1009 * 2 * 3 * ... smooth.
