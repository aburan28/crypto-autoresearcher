# Scout dossier: additive combinatorics and character sums (final lead-discovery round, run 2)

Field: additive combinatorics. This covers sum-product, Elekes-Szabo and expanding polynomials, Szemeredi-Trotter
over F_p, energies and Fourier spectra of coordinate-defined subsets of E(F_p), Kloosterman / Weil control of
decomposition counts, and the k-SUM side of algorithmic additive combinatorics.

Author: scout subagent, 2026-10-24. I wrote only under `scratchpad/scout/`. Nothing in any repository was edited,
created, staged or committed.

The run-1 dossier of 18:52 is preserved unchanged at `scratchpad/scout/ac-r2/scout-additive-comb.prior-1852.md`.
This file replaces it. Every measurement quoted below was produced in this run, by scripts in
`scratchpad/scout/ac-r2/`. The one exception is marked INHERITED.

Provenance legend:
- **retrieved** means the source text was read in this session; the URL is given.
- **recalled** means it was not read in this session.
- **derived here** means a derivation made in this session that nobody has reviewed.
- PREDICTION marks numbers that were not measured.

## 0. Summary

Two facts shape everything below.

1. Most of this field proves pseudorandomness, that is, upper bounds on structure. An index-calculus (IC) gain needs
   structure above random. Weil, Deligne, Kohel-Shparlinski and Burgess-type estimates all lose about sqrt(p), or
   need intervals longer than p^{1/4+eps}. The IC operating point B = p^{1/(m+1)} is at or below p^{1/4} for every
   m >= 3, so no constructive ingredient for B1-B3 comes out of the field (section 1).
2. Three of the four run-1 candidates are now duplicated by other scouts this round:
   - the Miller-primitive Weil bound by scout-arithmetic-statistics C1;
   - the Bezout log-interpolation ceiling by scout-polynomial-method C3 and scout-coding-isd C2;
   - the G1 floor by scout-polynomial-method C1, which in turn sits inside EXP-ICEX-153c34's own method_ceiling.

   I therefore kept only what is additive-combinatorial and not covered elsewhere, and added one new result.

| id | bottleneck | what it decides | evidence (this run) | tier |
|:--|:--|:--|:--|:--|
| **AC-Q** (new) | Not one of B1-B7. It is a lead-deciding proof for LEAD-EXO-four-list-ktree-join (the four-list k-tree on prime-field E(F_p)) and for the KN-FIND-ffe1df "bucket hole" | A Latin-square Cauchy-Schwarz bound. For EVERY quasigroup combining rule and EVERY target bucket, the per-bucket Wagner speedup is at most 1 + Gamma/(sqrt(alpha_c) Pr_c), which is about 1 + M^{3/2} Gamma. The red-team bound it replaces is 1 + M^2 Lambda. With the Kummer-Lang Weil bound for character filters, Gamma <= (s sqrt(p) + s + 1)/N, so at level 1 the speedup is p^{o(1)} for every M <= p^{1/3+o(1)}. That covers j = 2, which KN-FIND-ffe1df lists as UNPROVED. | Derivation, plus an exact whole-group check on 96 cells at p = 1009..65537 with M = 8..64. The worst case over all Latin squares is computed as the ratio-optimal permutation by Dinkelbach-iterated assignment. Algebraic filters never exceed 0.14 of the bound; the positive control reaches 0.49. At p = 65537, M = 64, a character filter reaches 1.088 against the bound 3.67; the red-team bound there is 47.3. | X |
| **AC-3** (refined) | B1 (prime). LEAD-ICP-generic-table-decomposition (revisit_when) and LEAD-ICE-charged-toy-ic-exponent-vs-rho | Planted m-SUM search embeds into any decomposition oracle that works on random bases. Under the Average-Case k-SUM Conjecture (DKK21; ASSVV23 Conj. 3.5) and ASSVV23 Cor. 4.9 (both retrieved), every such oracle has per-target exponent tau >= m(1 - 1/(2 Delta)). In the sparse branch (Delta <= 1) that puts it outside the (tau, mu) escape region R_m for every m. So SO-TABLE's revisit point (an S_5 oracle with T_dec << p^{1/4} at B = p^{1/5}) is unreachable: tau >= 1.5 means T_dec >= p^{0.3}. The amortised-preprocessing branch is conditional on H3b. | Reduction (derived here) composed with retrieved theorems. No run. | X |
| **AC-1** (kept; overlaps scout-arithmetic-statistics C1) | B7 (prime). LEAD-TRF-miller-cocycle-nonhom-transfer, LEAD-EXO-miller-pairing-cocycle | A conductor-controlled (Kummer x Lang) Weil bound: \|sum chi(U(kP)) e(ak/N)\| <= 2 sqrt(p). It closes the character-level cell of H1. | Re-run in this session: max\|S\|/(2 sqrt p) = 0.9974-1.0000 on 15/15 curves (p = 101..2003). K2 is exact on 9/9 curves. | X |

Predicted gain is 0 for all three: they are closures or routings. Killed candidates (section 6) are listed with the
number that killed each. Side flags for the coordinator are in section 7.

## 1. Why B1-B3 stay empty in this field (kill test applied to the field)

IC sizes: sub-rho linear algebra needs |F| = B <= N^{1/4}. A relation needs B^m/m! of order N/(targets).

1. **Completion (Weil, Deligne, Kohel-Shparlinski).** For an interval, GAP or coset base, the decomposition count is
   N(c) = |A|^m |V_c|/p^m + O(p^{(m-1)/2} (log p)^m). This is non-trivial only when |A| >> p^{(m+1)/(2m)} > p^{1/2},
   so it is vacuous at every IC size.
2. **Burgess barrier.** The only tool that beats completion on short intervals (Burgess, length p^{1/4+eps}) needs
   B > p^{1/4}. The IC point B = p^{1/(m+1)} is at or below p^{1/4} for every m >= 3, so a closure or an opening of
   LEAD-ICP-coincidence-harvest-structured-base by analytic number theory is out of reach. Its growth ladder is the
   only instrument that can decide it. This is a recalled statement of where Burgess applies; I did not re-read
   Burgess.
3. **Elliptic sum-product and incidence bounds** (Ahmadi-Shparlinski; Stevens-de Zeeuw; Rudnev) give
   E_+(x(A)) <= |A|^{3-delta}. At |A| = N^theta that is kappa <= N^{1-theta(1+delta)}, at least N^{0.6} for theta <=
   0.35, against the break-even delta* = 1/3 of IDEA-20261018-a0830c. The bound cannot close the lead, and as an
   upper bound it cannot power an attack.
4. **Elekes-Szabo / Bays-Breuillard.** S_3 is the special (group) case. A low-degree reparametrisation that made S_3
   additive or multiplicative would be a non-constant algebraic map E -> G_a or G_m compatible with the group law,
   which is impossible.
5. **The constructive side** (dense subset sums, Sarkozy-Szemeredi-Vu; algebraic 3SUM; Kane-Lovett-Moran decision
   trees) needs explicit logs, real cuttings or an order compatible with addition. E(F_p) offers none of these.
6. **Fourier preselection of targets.** A coordinate predicate pi with Pr[pi] = rho raises the decomposition rate by
   at most a factor of 1 + (sqrt(N) Lambda_pi / (2 B rho)) eta_F^{m-2}, where eta_F = max_{xi != 0}|F~(xi)|/(2B) is the
   base's log-space Fourier bias (derived here). At m = 4 and B = N^{1/5} a random-level base has
   eta_F^2 ~ N^{-0.2} while sqrt(N)/B = N^{0.3}. The bound is then at least N^{0.1}/rho, which is vacuous. Killed.

## 2. AC-Q: Latin-square Cauchy-Schwarz bound for bucket-resolved sum-compatible filters (new)

### 2.1 What is open, quoted

- **LEAD-EXO-four-list-ktree-join** (open_next_step). Next step: "Measure the relative bucket variance W of the O2
  agreement kernel (H-ECDLP-2ade73; IDEA-20260904-f7d47d second moment) on the covered families across N and fit its
  decay against 1/sqrt(N) ... LARGE-W ... reopens a bucket-concentrated filter for a four-tree; SMALL-W extends the
  bucket-averaged O2 barrier (KN-FIND-ffe1df) to a bucket-resolved one and closes the filter class." Best measured:
  "j=2 four-tree at exponent 0.4167 closed for character filters under group-law or quasigroup combining, toy N <=
  65539".
- **KN-FIND-ffe1df** (Red Team, RT-20260803-be45a8): "A Wagner level fixes **one** bucket c ... chosen after seeing
  h, and is paid at max_{c,d} pi_c(d) ... Repairing it costs back exactly the factor the composition removed ...
  eps_c <= 1/M^2 + Lambda_W and speedup = M pi_c <= 1 + M^2 Lambda_W -> p^{o(1)} only for M <= p^{1/4}. j = 2 needs
  M ~ p^{1/3}." Its status table says j = 2 is "UNPROVED -- outside M <= p^{1/4}; the bucket hole is fatal here".
  Its section "What is NOT established" lists as item 1 "Approximate quasigroup combining ... no robust Theorem C is
  proved", and as item 6 "Levels >= 2 of the tree".

### 2.2 Lemma Q (derived here)

**Setting.** G is cyclic of prime order N, written additively through the discrete log k <-> kP. The filter is any
map h: G -> [M] with buckets A_a = h^{-1}(a) of density alpha_a. Use the normalised DFT
A^_a(xi) = N^{-1} sum_x 1_{A_a}(x) e(-xi x/N). Define

  S(xi) = sum_a |A^_a(xi)|^2,      Gamma(h)^2 = max_{xi != 0} S(xi).

If the buckets are labelled by any abelian group Z of order M, Parseval over Z gives
S(xi) = M^{-1} sum_{psi in Z^} |E_x psi(h(x)) e(-xi x/N)|^2. The trivial psi contributes 0 at xi != 0. Hence
Gamma <= Lambda := max_{psi != 1, xi != 0} |E_x psi(h(x)) e(-xi x/N)|, the dlog-Fourier coefficient of the filter
characters, which is O2's Lambda. Gamma is labelling-free.

Let f be any Latin square on [M]. Fix a target bucket c, and let sigma_c be the permutation with f(a, sigma_c(a)) = c.
Put Pr_c = sum_a alpha_a alpha_{sigma_c(a)} and pi_c = Pr[h(P+Q) = c | f(h(P), h(Q)) = c].

**Claim.**

  pi_c <= alpha_c + sqrt(alpha_c) * Gamma / Pr_c,

so the per-bucket speedup over random satisfies

  pi_c / alpha_c <= 1 + Gamma / (sqrt(alpha_c) Pr_c).

For kappa-balanced filters (every alpha_a in [1/(kappa M), kappa/M]) this gives speedup <= 1 + kappa^{3/2} M^{3/2}
Gamma. Averaging over c with weights Pr_c gives eps <= max_c alpha_c + sqrt(M) Gamma for the bucket-averaged rate.

**Proof.**
1. The count. #{(x,y): f(h(x),h(y)) = c, h(x+y) = c}/N^2 equals
   sum_a sum_xi A^_a(xi) A^_{sigma_c(a)}(xi) conj(A^_c(xi)).
2. The main term. The xi = 0 term is alpha_c Pr_c.
3. The inner sum. For xi != 0, Cauchy-Schwarz and the bijectivity of sigma_c give
   |sum_a A^_a A^_{sigma_c(a)}| <= S(xi). This is the only point where the Latin property is used.
4. The outer sum. The error is at most
   sum_{xi != 0} |A^_c(xi)| S(xi) <= (sum_xi |A^_c|^2)^{1/2} (sum_{xi != 0} S^2)^{1/2}.
   The first factor is at most sqrt(alpha_c) by Parseval. The second factor is at most
   (Gamma^2 sum_a alpha_a)^{1/2} = Gamma.
5. Divide by Pr_c.

QED.

**What this changes.**
- The red-team per-bucket bound bounded each of the M^2 coefficients by Lambda: eps_c <= 1/M^2 + Lambda_W.
- Lemma Q instead takes the l2 norm over buckets (step 3) and over frequencies (step 4). This saves M^{1/2}, and it
  holds for every quasigroup, the group law included.
- The bound needs no balance or non-redundancy hypothesis, because the xi = 0 marginal is exactly alpha_c Pr_c. That
  marginal is the term that broke KN-FIND's family J.
- The 99% regime falls out as a corollary. Per-bucket agreement pi_c >= 1/2 forces Gamma >= Pr_c/(2 sqrt(alpha_c)),
  which is about 1/(2 sqrt(M)). Any such filter therefore carries a log-character correlation of size at least
  1/(2 sqrt M). This is a robust Theorem C: it is quantitative and holds for every quasigroup.

### 2.3 Composition with Weil for character filters (derived here; the ingredient is partly retrieved)

**Scope of the character class.**
- **Single character (r = 1).** h(P) = ind_psi(F(P)) mod M, with psi of order M. This needs M | p-1. At M ~ p^{1/3}
  that restricts p; otherwise use product filters.
- **Product filters (r > 1).** h = (ind_psi(F_1), ..., ind_psi(F_r)), with M = k^r.
- **Non-degeneracy.** For every non-zero t, the product prod F_i^{t_i} must not be a constant times a k-th power.
  This is [D]'s (H6) non-redundancy, and it makes every psi_t(h) geometrically non-trivial.
- **s.** The total number of distinct points in the union of the supports of div F_i, with O included.

**Balance is automatic.** The xi = 0 terms give |alpha_a - 1/M| <= (1/M) sum_{t != 0}|E psi_t(h)| <= s/sqrt(p)
(1 + o(1)). Hence kappa <= 1/(1 - M s/sqrt(p)), which tends to 1 for M <= p^{1/3}. No separate balance hypothesis is
needed in this class.

Let F be one such rational function, with divisor support of s points. Then psi_t(h(P)) chi_xi(P) is the trace
function of L_{psi_t}(F) (x) L_{chi_xi}:
- L_{chi_xi} is the Lang torsor of the group character chi_xi of E(F_p). It is lisse and geometrically non-trivial
  for xi != 0.
- L_{psi_t}(F) is the Kummer sheaf. It is tame, and ramified at the zeros and poles of F where psi_t is non-trivial on
  the local order.
- The tensor product is rank 1 and lisse on E minus s points, with H^1_c of dimension at most s.

Hence |E_P psi_t(F(P)) chi_xi(P)| <= (s sqrt(p) + s + 1)/N, and so Gamma <= Lambda <= (s sqrt(p) + s + 1)/N.

Provenance of this step:
- The x-only case with an additive character is Kohel-Shparlinski Cor. 1, quoted as O(q^{1/2}) in
  Ahmadi-Shparlinski, Lemma 1 (retrieved, arXiv 1302.4210).
- The load-bearing multiplicative, conductor-controlled form is MY derivation, by the same argument as AC-1. It is
  **recalled/derived**, not retrieved.
- Measured support: Lambda sqrt(N) = 2.42-2.92 for the x+3 filter (s = 3) over all 24 xchar cells, p = 1009..65537.
  That is under the bound of 3 + o(1) everywhere, and within 3% of it at p >= 16001.

Substituting into Lemma Q gives the level-1 speedup:

  speedup_c <= 1 + kappa^{3/2} s M^{3/2} p^{1/2} / N  (1 + o(1)).

At M = p^{1/3}, which is j = 2's requirement, this is at most 1 + kappa^{3/2} s, a constant, hence p^{o(1)}. For
M <= p^{1/3-eps} it is 1 + o(1). The level-1 bucket hole therefore closes for every j >= 2 and for every quasigroup
combining rule, within the character-filter class of bounded divisor support s.

### 2.4 Measured in this run (toy tier; `ac-r2/latin_bucket.py`)

**Method.**
- Whole-group exact counts through the dlog DFT. The identity was checked against brute force over all N^2 pairs at
  p = 211, with maximum deviation 3e-17 (`check_wc.py`).
- For every bucket c, the worst case over ALL Latin squares is the permutation sigma that maximises the RATIO
  count(sigma)/Pr_c(sigma). It is found by Dinkelbach iteration: assignment on W - lambda alpha_a alpha_b, then update
  lambda, until no improvement. This is valid because every permutation sigma extends to a Latin square
  f(a, b) = c + (b - sigma(a)).
- The run-1 version of this column used the max-COUNT permutation. Its outputs are kept in `ac-r2/v1/`. The ratio
  optimum exceeds it by at most 0.013.
- The worst case over group-law rules a + b + d is reported alongside.
- Filters:
  - `xchar`: dlog(x+3) mod M, with M | p-1;
  - `xmod`: x mod M;
  - `sha`: SHA-256 null;
  - `dlog_interval`: floor(Mk/N). This is the positive control: it computes the log.
- Output: `run_latin_v2_all.jsonl`. It has 96 cells: p in {1009, 4001, 16001, 65537}, 2 seeds each, M in
  {8, 16, 32[, 64]}, 4 filters.

| p | N | M | filter | Gamma sqrt(N) | worst speedup over all Latin squares (ratio-optimal sigma) | worst, group law | this bound 1+M^{3/2}Gamma | red-team 1+M^2 Lambda |
|--:|--:|--:|:--|--:|--:|--:|--:|--:|
| 1009 | 967 | 16 | xchar | 1.65 | 1.278 | 1.202 | 4.39 | 23.8 |
| 4001 | 3967 | 32 | xchar | 1.50 | 1.214 | 1.189 | 5.32 | 45.8 |
| 16001 | 16063 | 32 | xchar | 1.43 | 1.086 | 1.085 | 3.05 | 24.6 |
| 65537 | 65951 | 32 | xchar | 1.59 | 1.046 | 1.045 | 2.12 | 12.5 |
| 65537 | 65951 | 64 | xchar | 1.34 | 1.088 | 1.086 | 3.67 | 47.3 |
| 65537 | 65651 | 64 | xchar (seed 2) | 1.38 | 1.079 | 1.077 | 3.75 | 47.5 |
| 65537 | 65951 | 64 | xmod | 1.35 | 1.064 | 1.056 | 3.68 | 66.1 |
| 65537 | 65951 | 64 | sha (null) | 1.28 | 1.018 | 1.006 | 3.55 | 60.0 |
| 65537 | 65951 | 64 | dlog_interval (control) | 32.1 | 32.02 | 32.02 | 64.97 | 4095 |

- The bound held in 96/96 cells.
  - The largest (speedup - 1)/(bound - 1) was 0.485, on the positive control, which sits at about half the bound in
    every cell (0.385-0.485). The bound is tight within a factor of about 2 where structure exists.
  - Over the algebraic and null filters the largest ratio was 0.138.
- M = 64 at p = 65537 is already above j = 2's M ~ p^{1/3} = 40.3. The ratio-optimal Latin square gives
  1.079-1.088 for the character filter.
- For algebraic filters the worst-case excess shrinks with p at fixed M.
  - xchar, M = 32: 0.214-0.240 (p = 4001) -> 0.086-0.099 (16001) -> 0.041-0.046 (65537).
  - The run-1 single-seed stall at xchar, M = 16 (0.044 at p = 65537) is seed-specific: seed 2 gives 0.017.
- Algebraic filters sit above the SHA null at toy size: 1.088 against 1.018 at M = 64. This is consistent with
  KN-FIND-ffe1df's report that T_x sits at the Weil scale and T_sha at 1/p. It stays inside the bound.

### 2.5 Object frame

- **Pair.** Representation R1: x(P) in F_p through a multiplicative-character label. Operation set Sigma: the group
  law on input pairs, plus the quasigroup f on labels.
- **Trichotomy.** Branching. The label of P+Q is only probabilistically determined by the labels of P and Q.
  Theorem C excludes deterministic propagation. Lemma Q prices the branching: L = log M bits are discarded, and the
  per-bucket survival rate is at most alpha_c + sqrt(alpha_c) Gamma/Pr_c.
- **Factor base.** None (not an IC object). KN-OPEN-020 does not apply.

### 2.6 Obstructions touched (obstruction.statement quoted from the lead YAMLs, Scope included)

- **SO-GEN** (LEAD-RHO-generic-sqrt-lower-bound): "Shoup/Nechaev generic-group lower bound: any generic algorithm
  needs Omega(sqrt r) group operations for a prime-order-r group (KR-RHO-13bf67). Every lead in this family moves
  only the constant ... Scope: all generic algorithms, any field, any r."
  - Premise escaped: "generic algorithm". A coordinate-reading filter is not generic, which is why the k-tree lead
    exists at all.
  - Lemma Q supplies the quantitative barrier for the non-generic filter class that SO-GEN cannot reach.
- **SO-TORS** (LEAD-STR-torsion-module-leak): "... A non-homomorphic point statistic is a function of the encoding of
  Q. Using it is index calculus or a generic query, and partial information about k on the point costs more than it
  saves, by sqrt(M) (IDEA-20260811-8cf53a) ... Scope: prime-order G, any l != N."
  - Premise not escaped. Lemma Q gives that sentence a bucket-resolved number for filters: speedup - 1 <=
    M^{3/2} Gamma.
- **Object-frame result (KN-FIND-ffe1df Theorem C)**: "an exactly sum-compatible bucket index is a surjective
  homomorphism onto a group of order dividing N, impossible for prime N and 1 < M < N." Lemma Q is its robust,
  quantitative form for quasigroups.
- **Binary sibling** (LEAD-ICB-cofactor-torsion-quotients, not an SO code): "exactly sum-compatible filters on
  E(F_{2^131}) carry 2 bits (the cofactor), so Wagner k-tree has no quotient to work in ..." Lemma Q never uses p
  odd. The approximate case on binary curves needs the additive-character (Artin-Schreier) analogue of 2.3, which is
  not done here.

### 2.7 First discriminating step and outcome -> disposition

**Step** (about 1 day, CPU minutes):
1. Independent review of Lemma Q (one page) and of the Kummer-Lang constant in 2.3.
2. Run the `latin_bucket.py` meter on every O2 filter family:
   - A/B: x-based intervals and windows;
   - I: popcount and digit sums;
   - J: y-sign;
   - the y-based and nonlinear members x±y, xy, x^{-1};
   - p ladder 2^12 .. 2^20, three or more seeds, the SHA null, and the dlog_interval control.
3. Report Gamma sqrt(N) per family and its fitted growth exponent gamma in p, together with the exact
   worst-over-Latin-squares speedup at M = p^{1/3}.

**Outcomes.**
- Review passes. Then LEAD-EXO-four-list-ktree-join's level-1, bucket-resolved cell becomes **closed_obstructed
  (proof)** for multiplicative-character filters of bounded divisor support s, for every quasigroup rule and every
  j >= 2. The scope clause should read "level 1 of the tree; character filters with bounded s". The W-measurement
  next step is retired for that class, because W is bounded by theorem.
- A family has Gamma sqrt(N) = O(1) (gamma CI contains 0 and excludes values above 0.05) across at least 3 primes. Its
  level-1 cell becomes **exhausted_at_scale**, with the reached size recorded.
- A family has gamma > 0 with its CI excluding 0. Then **open_next_step**, best_measured = (family, gamma). That family
  is the first bucket-concentrated candidate and must then be priced against matched rho.
- Lemma Q is violated in any cell. The derivation is wrong; the lead stays as it is, best_measured = the violating
  cell.
- In every case the lead stays **open_next_step** for two cells, with these next steps:
  - (i) levels >= 2: write the bootstrap lemma KN-FIND-ffe1df sketches ("a tree whose first merge yields no filtering
    gain cannot bootstrap the later ones");
  - (ii) arbitrary cheap h, which KN-FIND's Proposition 2 shows no group-theoretic argument can close.

**Cost.** Implementation about half a day (the meter exists). Compute is minutes up to p = 2^20 at M <= 64, which is
O(M^3 N) by BLAS.

**Numbered heuristics.**
- **H-Q1.** For the non-character families (I, J, y-based), Gamma sqrt(N) stays O(log p). PREDICTION, based on the
  measured 1.28-2.2 for xmod and sha.
- **H-Q2.** A level-1 speedup of p^{o(1)} implies a tree speedup of p^{o(1)}. This is the bootstrap lemma, unproved.

## 3. AC-3 (refined): planted k-SUM routing of base-uniform decomposition oracles (B1, prime)

### 3.1 The external ingredient (retrieved)

Source: Agrawal, Saha, Schwartzbach, Vanukuri, Vasudevan, "k-SUM in the Sparse Regime", arXiv 2304.01787 / IACR ePrint
2023/488. The PDF text of the arXiv version was read in this session.
- **Conjecture 3.5** (Average-Case k-SUM Conjecture, formalised by Dinur-Keller-Klein [DKK21] as folklore): "For any
  k in N, any algorithm that solves (non-planted) search k-SUM over G_k-SUM^(1) with constant success probability has
  expected running time at least Omega(r^{ceil(k/2) - o(1)})." This is density 1.
- **Corollary 4.9**: under Conjecture 3.5, "for k in N and Delta in (1/2, 1], any algorithm that solves planted search
  k-SUM in G_k-SUM^(Delta) ... with constant success probability has to take expected time
  Omega(r^{[k(1 - 1/(2 Delta))] - o(1)})".
- Theorem 4.8 proves the density reduction "for an Abelian group G", so it applies to Z/N with N prime.
- DKK21 Theorem 4.6 (quoted there, dense regime Delta in (1, 2]): Omega(r^{k(1/Delta - 1/2) - o(1)}).
- The same bibliography lists Kopelowitz-Porat, "The strong 3SUM-indexing conjecture is false". I read the title only
  (retrieved), not the paper.

### 3.2 Reduction (derived here)

Let O be a decomposition oracle that, for a uniformly random base F of B points and a target T equal to the sum of m
random elements of F, returns an m-decomposition with probability >= eps in time T_O. T_O includes any preprocessing
O does on F.

Given a planted m-SUM instance (x_1..x_B) in Z/N with planted zero-sum K, draw a uniform u. Set F_i = (x_i + u)P and
T = m u P, at a cost of O(B log N) group operations. Then F is i.i.d. uniform and T = sum_{i in K} F_i, which is
exactly O's input distribution. So O solves planted m-SUM at density Delta = m log B / log N. By Cor. 4.9,

  T_O >= B^{m(1 - 1/(2 Delta)) - o(1)},   i.e.   tau >= m - 1/(2 beta)   (beta = log B / log N, Delta in (1/2, 1]).

Signs: IC returns signed decompositions. The signed variant changes the density by 2^m, a constant. I take this as
**H3a** (folklore, recalled; not in ASSVV23).

### 3.3 Composition with the escape region (scout-query-communication C1)

The region lemma R_m is another scout's derivation from this round and is unreviewed. Everything below inherits that
status. That scout's region lemma reads: "C <= N^{1/2-eps} for some beta iff (tau, mu) lies in R_m = {tau < m/2 - 1 and
tau + mu < m - 1} (m >= 4); R_2 = R_3 = empty."

- **Sparse branch (Delta <= 1).** tau >= m - 1/(2 beta) gives m - 1 - tau <= 1/(2 beta) - 1. The relation-term
  requirement beta > 1/(2(m-1-tau)) then reads beta > beta/(1 - 2 beta), which is impossible. For Delta <= 1/2 the
  relation exponent alone forces tau < -1. So **no base-uniform, unamortised oracle lies in R_m, for any m**. The
  only premise is Conjecture 3.5.
- **SO-TABLE's revisit point.** "per-attempt cost T_dec << p^{1/4} at arity m = 4 (an S_5 oracle at B ~ p^{1/5})".
  Here Delta = 4/5 gives tau >= 4(1 - 5/8) = 1.5, so T_dec >= B^{1.5} = p^{0.3} > p^{1/4}. The point is unreachable
  by such oracles.
- **Dense branch (Delta in (1, 2]; per-target saturation).** DKK Thm 4.6 gives tau >= 1/beta - m/2. Then R_m is
  feasible only if beta > 1/(m - 2) with beta <= 1/4, that is, only at m >= 7. This is exactly the explicit-Z/N Wagner
  regime.
  - Remark: inside E(F_p) a base-uniform oracle that wanted the k-tree speedup would need sum-compatible filters. AC-Q
    closes those at level 1 for character filters. This is a link I state, not a theorem: an IC oracle need not run a
    k-tree.
- **Amortised preprocessing (mu > tau).** Not covered by Cor. 4.9. **H3b** (my conjecture): planted m-SUM indexing
  with space B^mu needs per-query time B^{tau} with tau >= min(ceil(m/2), m - mu) - o(1). The known upper bounds meet
  it: table splits give tau = m - mu, and Schroeppel-Shamir gives (tau, mu) = (m/2, m/4). Fiat-Naor inversion is
  worse (scout-query-communication K1). H3b places every amortised base-uniform oracle outside R_m. Kopelowitz-Porat's
  title is a warning that strong indexing conjectures can fail, so H3b is the weakest link.

### 3.4 Object frame

- **Pair.** R1: the x-coordinates of base points. Sigma: translation by factor-base elements.
- **Trichotomy.** Partial-action (IC, Class I).
- **KN-OPEN-020 class.** AC-3 shows that the open class must be **base-specific**: high-degree, implicit or
  target-dependent descriptions whose advantage disappears on random-coordinate bases. Base-uniform designs are
  pruned.

### 3.5 Obstructions touched (quoted, Scope included)

- **SO-TABLE** (LEAD-ICP-generic-table-decomposition): "Any decomposition oracle that enumerates or table-looks-up
  factor-base elements is a generic time/memory trade-off and obeys S*T^2 >~ N (Corrigan-Gibbs--Kogan) and
  T >~ sqrt(N) (Shoup); ... Scope: any generic (enumeration/table) decomposition over F_p."
  - Premise escaped: "enumerates or table-looks-up". AC-3 covers any algorithm, including coordinate-reading
    Groebner, SAT and lattice oracles.
  - The price is conditionality on Conjecture 3.5 and a restriction to base-uniform guarantees.
- **SO-TABLE (binary)** (LEAD-ICB-generic-table-oracle): "Every oracle built from group operations and membership
  tests makes IC a generic-group algorithm with advice ... Scope: all binary and Koblitz curves, one target, setup
  charged."
  - Same premise escaped. The reduction is field-agnostic (Theorem 4.8 holds for any abelian group).
- **SO-MULTI** (LEAD-ICB-multi-target-and-portfolio): "The multi-instance generic bound (L logarithms cost
  >~ sqrt(L r/|Aut|)) covers generic-oracle IC including its set-up ... the L^-1 amortisation applies only to the
  online part after a set-up that obeys the same bound."
  - Premise "generic-oracle". AC-3's amortised branch is the non-generic analogue of this statement, and it is the
    branch that needs H3b.
- **SO-GEN** (LEAD-RHO-generic-sqrt-lower-bound): quoted in 2.6. AC-3 does not rely on GGM.

### 3.6 First discriminating step and outcome -> disposition

**Step.** The base-specificity gap test. It is already designed as **EXP-ICEX-153c34 arm N** ("Arm N random-x factor
base of equal L on identical attempts (tests whether G1 uses small x; HEUR-ICEX-6ca21f-2)"). Add the same paired arm
to the prime Groebner, SAT and lattice oracle runs, at L over 3 or more sizes. AC-3 supplies the decision rule that
arm N currently lacks.

**Amortisation condition.** Cor. 4.9 covers only oracles whose preprocessing is counted in their own per-target
time. Each arm must therefore also report its measured setup exponent mu (setup units against L) beside its per-query
exponent tau.
- G1 qualifies. Its setup is the per-fixture pair-product tensors, dense R4 elements of dimension about L^4. Its
  per-query cost is at least about L^5 (scout-polynomial-method C1; the contract's grid floor). So mu <= tau.

**Outcomes.**
- The designed/random cost ratio is flat in L (|log-log slope| <= 0.05, CI inside +-0.1) AND the measured mu <= tau.
  The oracle family is base-uniform in practice and unamortised, so the AC-3 floor applies. That arm becomes
  **closed_obstructed (cost_model, conditional on ASSVV23 Conj. 3.5 / DKK21, and on the unreviewed R_m lemma)**.
  SO-TABLE's revisit_when gains the clause "base-specific oracles only; base-uniform ones need
  tau >= m - 1/(2 beta)".
- The ratio is flat but mu > tau. The same disposition is conditional on H3b, the weakest link
  (Kopelowitz-Porat). Record it as **open_next_step**, best_measured = (tau, mu), and do not close.
- The ratio falls as L^{-gamma}, gamma > 0, with CI excluding 0. Then **open_next_step**, best_measured = gamma. This
  is the first base-specific signal and the only admissible escape.

**Cost.** Half a page of derivation. One paired arm per oracle, reusing existing contracts.

## 4. AC-1 (kept): conductor-controlled Weil bound for the Miller primitive (B7, prime)

**Overlap.** scout-arithmetic-statistics C1 states the same theorem, the "Kummer-conductor bound". Treat this as an
independent re-derivation and merge.

What this section adds over that scout:
- the EDS-ratio extension C1c;
- the K2 verification;
- my own reproduction of the measurements.

**Setting.** E/F_p, P of prime order N, gcd(N, p-1) = 1, so the Tate pairing is trivial. f = f_{N,P} has
div f = N(P) - N(O). U(R) = f(R)^e with e = N^{-1} mod (p-1) (IDEA-20261017-e3a6f1).

**Theorem (derived here).** For every non-trivial chi of F_p^* and every a in Z/N:

  |sum_{k=2}^{N-1} chi(U(kP)) e(ak/N)| <= 2 sqrt(p).

**Proof.** chi(U) = chi^e(f), and chi^e is non-trivial of order d | p-1. The Kummer sheaf L_{chi^e}(f) is tame and
ramified exactly at P and O, with local monodromy chi^{eN}, which is non-trivial because gcd(N, d) = 1. Tensor with the
Lang-torsor sheaf of e(a. /N), which is lisse on E. The result is rank 1 on E - {P, O}, with chi_c = -2 and
H^0_c = H^2_c = 0, so dim H^1_c = 2. Apply Weil.

The bound counts distinct zeros and poles, not deg f = N. On a degree route the bound would be about N sqrt(p), which
is vacuous. The same argument gives s sqrt(p) for any product of Miller and line functions whose divisor has s
distinct points.

**Corollaries (derived here).**
- **C1a (joint equidistribution).** (k mod N, log U(kP) mod p-1) has discrepancy O(p^{-1/2} log^2 p).
- **C1b (ratio recovery).** The fraction of k with log U(kP) = ck is at most 1/(p-1) + O(log p/sqrt(p)). This is a
  rate of p^{-1/2}, not the 1/p rate the lead's discriminator names. So random self-reduction through U costs at least
  sqrt(p)/(C log p) Miller loops, which is rho-level.
- **C1c (EDS ratio).** Given K2, r_k = psi_{k-1}/psi_k satisfies |sum chi(r_k) e(ak/N)| = O(sqrt(p) log N) for every
  chi. This extends Shparlinski-Stange (quadratic chi; retrieved abstract in run 1) to all characters.
- **C1d (circularity).** Recovery through K2 needs r_k, which is EDS-residue-equivalent to computing k.
  Lauter-Stange is recalled.

**Measured in this session** (`ac-r2/run_miller_r2.txt`, `run_miller_r2_p2003.txt`, `run_k2_r2.txt`):

| p | curves | max\|S\|/(2 sqrt p) | shuffled-ell control max\|S\| |
|--:|--:|:--|:--|
| 101 | 3 | 0.9974-0.9999 | 29.6-30.4 |
| 211 | 3 | 0.9976-0.9995 | 44.4-50.8 |
| 401 | 3 | 0.9994-0.9998 | 70.2-73.9 |
| 1009 | 3 | 0.9999-1.0000 | 113-124 |
| 2003 | 3 | 0.9999 (89.50 vs 89.51) | 166-169 |

- The bound is sharp and never exceeded. The shuffled control, which has the same marginal, reaches about 1.9 times
  the bound.
- K2: the first difference of dlog(U(kP) W_k/W_{k-1}) is constant mod p-1 on 9/9 curves (p = 101, 401, 1009).
- max|sum chi(r_k) e(ak/N)| = 27.7-31.0 (p = 101), 67.6-73.2 (401), 109.8-122.4 (1009). That is inside
  2 sqrt(p) log N.

**Pair and trichotomy.**
- Pair: R2, the F_p^*-valued canonical section U of the G_m-extension of class [P]. Sigma: translation by S, acting
  through the explicit defect g_{R,S}(P).
- Trichotomy: coordinate-dependent.
- Not a factor base.

**Obstructions touched (quoted).**
- **SO-PADIC** (LEAD-TRF-padic-canonical-section): "For p not dividing #E(F_p) the only homomorphic section is the
  prime-to-p torsion section, which the formal logarithm kills ...; any non-homomorphic section recovers d only at
  the random 1/p rate ... Scope: non-anomalous prime-field curves, all lifts of E."
  - Not escaped. AC-1 extends the "non-homomorphic section ... random rate" premise to sections of G_m-extensions,
    with a rigorous rate of p^{-1/2+o(1)}.
- **SO-PAIR** (LEAD-TRF-second-torsion-direction): "Balasubramanian-Koblitz: for N || #E(F_p), N != p,
  E(F_{p^k})[N] is larger than the rational line iff N | p^k - 1 ... Scope: ordinary and supersingular curves over
  F_p, prime N."
  - U is the non-homomorphic remainder that SO-PAIR does not cover. AC-1 closes that remainder at the character
    level.
- **SO-NET** (LEAD-EXO-elliptic-net-eds): "Somos identities hold for every k, so net relations encode the group law
  on one k-fibre and not k (KN-FIND-002 ...)". The YAML has no Scope clause.
  - C1c adds the all-character flatness of the EDS ratio.
- **SO-TORS** (quoted in 2.6). AC-1 gives correlation <= 2/sqrt(N) per character pair.

**First step and dispositions.**
- **Step.** Review the derivation. Extend the check to p of about 2^14-2^16 with all small-order chi and 10^3 random
  (chi, a) pairs.
- **No cell above 2 sqrt(p), review passes.** The **character-level cell of LEAD-TRF-miller-cocycle-nonhom-transfer
  becomes closed_obstructed (theorem)**.
  - The lead's own discriminator asks for "Equidistribution at the 1/p rate". AC-1 proves a p^{-1/2} rate. So the
    ratio clause (C1b) and nonlinear inversion stay out of scope.
  - The zeta-defect and generalized-Jacobian cells stay open_unexamined.
- **Sister lead.** LEAD-EXO-miller-pairing-cocycle's K1/K2 verification is done at toy size (K2 9/9). Its recovery
  route reduces to r_k (C1d, recalled Lauter-Stange), so that cell moves to closed_obstructed (proof) only after
  review of C1d.
- **A violating cell.** The derivation is wrong; best_measured = that cell.

## 5. Match phrasings and tool hits (env exports set; full output in `ac-r2/match_r2.txt`)

- **AC-Q**
  - own: "Latin square Cauchy-Schwarz per-bucket bound for quasigroup combining of sum-compatible filters" ->
    LEAD-EXO-four-list-ktree-join (7); frontier KR-RHO-13bf67 (5).
  - plain: "can any bucket of a cheap filter be predictable from the buckets of two summands" ->
    LEAD-EXO-four-list-ktree-join (10).
  - obstruction vocabulary: "approximately sum-compatible bucket index with quasigroup combining rule bucket-resolved
    agreement" -> LEAD-RHO-correlated-walks-shared-sums (9), LEAD-EXO-four-list-ktree-join (5).
  - No KR row forecloses it. Ledger index grep for "quasigroup" / "Latin square" found no record. The knowledge grep
    found KN-FIND-ffe1df, which lists the approximate case as not established.
- **AC-3**
  - own: "planted k-SUM conjecture lower bound for base-uniform decomposition oracles" ->
    LEAD-ICB-generic-table-oracle (10), LEAD-ICE-generic-oracle-arity-cost-floor (7).
  - plain: "a decomposition algorithm that works on random factor bases is as hard as planted 4-SUM" ->
    LEAD-ICB-kic-golden-base-exact-decomp (14), LEAD-ICP-coppersmith-smallroot-semaev (14).
  - obstruction vocabulary: "decomposition oracle that enumerates or table-looks-up factor-base elements is a generic
    time/memory trade-off" -> LEAD-ICE-generic-oracle-arity-cost-floor (14),
    LEAD-ICP-generic-table-decomposition (14).
  - No KR row. Ledger index grep for "k-SUM conjecture", "planted k-SUM", "3SUM-indexing" and "DKK" found none.
- **AC-1**
  - own: "conductor-controlled Weil bound for the Miller primitive U and the Kummer sheaf of f_{N,P}" ->
    LEAD-EXO-miller-pairing-cocycle (7), LEAD-TRF-miller-cocycle-nonhom-transfer (6).
  - plain: "character sums of Miller function values are square-root small regardless of degree" ->
    LEAD-EXO-miller-pairing-cocycle (20), LEAD-TRF-miller-cocycle-nonhom-transfer (9); frontier KR-RHO-53c89f.
  - obstruction vocabulary: "non-homomorphic section recovers k only at the random rate" ->
    LEAD-TRF-padic-canonical-section (4).
  - No KR row forecloses it.

## 6. Killed candidates (my own, with the number that killed each)

| # | candidate | target | why killed |
|:--|:--|:--|:--|
| K-1 | G1 per-query floor (>= L^5 per query, >= 3.75 q per success) as a closure of the G1 backend | B1 | Duplicate. scout-polynomial-method C1 proves it via Alon's Combinatorial Nullstellensatz, with a pilot. EXP-ICEX-153c34 already records "method_ceiling: Grid floor A*L^5 is 1,041-8,438 times T" and "status: predicted_dominated". |
| K-2 | Bezout difference-count ceiling on log interpolation (run-1 AC-2) | exotic (LEAD-EXO-invertible-hint-subset) | Duplicate: scout-polynomial-method C3 (\|D_F\| <= 1 + sqrt(8d(M-1))) and scout-coding-isd C2. My A(1) re-run is handed to them as data: A(1) is at or below the random-labelling null on 12/12 curves (p = 211..2003), with A(1) in {6..10} against bounds 43-132 (`ac-r2/run_a1_r2.txt`). |
| K-3 | GGM multiplicative-collision bound for H-class canonicalisation (LEAD-RHO-non-automorphism-equivalence) | B6 | Duplicate of scout-query-communication C4, and dominated by SO-GEN. Every generic H-walk is a generic algorithm, so Shoup already caps it within an O(1) constant of rho. My per-step bound, q >= sqrt(s h)/\|Aut\| generic operations for consistency s, only tightens that constant to at most sqrt(2) over Aut-quotient rho, under the heuristic that consistency s inflates steps by s^{-1/2}. No disposition changes. |
| K-4 | Energy identity: the audit's target-variance equals the count of base-internal 2m-term relations (LEAD-ICE-decomposition-probability-audit) | B1-adjacent | Known: IDEA-20260811-7734c5, identity (iii) "Var_R ... = (1/M) sum_{chi != 1} \|S-hat(chi)\|^{2m}". Kept as side flag F-1. |
| K-5 | U^2 / triple-correlation bound eps <= 1/M + Lambda for group-law filters | exotic | Known: O2 Theorem A' (KN-FIND-ffe1df). AC-Q is the per-bucket and quasigroup extension. |
| K-6 | Akavia-Goldwasser-Safra shift conversion (a filter with log-Fourier coefficient eta gives DL in eta^{-2} polylog evaluations) | exotic (LEAD-EXO-hnp-advice-leakage) | Known in the program: that lead's conversion "exponent 2*beta vs 1/2". It adds nothing until a statistic exists. |
| K-7 | Fourier preselection of targets by coordinate predicates | B1 | Vacuous: gain - 1 <= (sqrt(N) Lambda_pi/(2B rho)) eta_F^{m-2}, which is at least N^{0.1}/rho at m = 4, B = N^{1/5} (section 1 item 6). |
| K-8 | Elekes-Szabo / Bays-Breuillard reparametrisation making S_3 separable | B1 | The ES group is isogeny-invariant. A separable form would be an algebraic group-law map E -> G_a or G_m. |
| K-9 | Energy ceilings (Stevens-de Zeeuw, Rudnev, Ahmadi-Shparlinski) closing LEAD-ICP-coincidence-harvest-structured-base | B1 | Ceiling kappa <= N^{1-theta(1+delta)} >= N^{0.6} against delta* = 1/3. Completion is rigorous only for n >= p^{2/3+eps}. |
| K-10 | BSG / approximate-group inverse theorem for coincidence excess | B1 | K = \|A\|^3/E(A) = N^{1-theta-delta}. BSG gives structure only for delta near 1 - theta. At the break-even delta = 1/3, K = N^{2/3-theta} is unbounded. |
| K-11 | 99%-stability (Ben-Or-Coppersmith-Luby-Rubinfeld homomorphism testing; Gowers-Long partial associativity) for quasigroup filters | exotic | Superseded by AC-Q's quantitative bound, which covers the 1% regime as well. The stability route needs agreement >= 1 - 2/9. |
| K-12 | Linear Kneser/Vosper (Hou-Leung-Xiang; Bachoc-Serra-Zemor) for the ECC2K-130 writability wall | B4 | Already in cryptanalysis pdp-degree-heuristics. The wall is priced on the dense direct ANF, independent of V's product profile. |
| K-13 | Katz-Sarnak second moment of decomposition counts for coset bases | B1 | Parseval forces Poisson variance. At IC sizes the index is >= p^{3/4} and completion is vacuous. |
| K-14 | Kummer-cover point counting as an exact decomposition counter | B1 | Genus O(k) per character pair, with k >= p^{3/4}. Counting does not find decompositions. |
| K-15 | NTT / gcd decomposability test on subgroup bases (sub-linear test) | B1/B3 | gcd(x^B - 1, Res_v(S_3, v^B - 1)) costs O~(B) = enumeration. No sub-linear test. |
| K-16 | Bourgain-Glibichuk-Konyagin sums for H-invariants | B6 | Parseval gives \|g^(a)\| <= 1/sqrt(h) for any H-invariant g, but nothing about coordinate computability. Bezout is vacuous: min\|lambda\| ~ N^{2/3}. |
| K-17 | Algebraic 3SUM / polynomial partitioning; Kane-Lovett-Moran k-SUM decision trees | B1 | Needs real cuttings or an order compatible with addition. Z/N has neither. |
| K-18 | Points on curves in small boxes (Cilleruelo-Garaev-Ostafe-Shparlinski; Chang et al.) | B1 | Upper bounds only. Lattice reach is dominated by LEAD-ICP-coppersmith-smallroot-semaev. |
| K-19 | Sidon / B_h factor bases to remove duplicate relations (B3 constant) | B3 | Gain 1 + O(B^2/N), which is about 1 at B = N^{1/3}. Conservation (KN-FIND-007) fixes the mean. |

**Why the B1-B3 list has one entry.** This is an explanation, not a shortfall: the prime-field requirement is met by
AC-3 (B1) and AC-1 (B7, prime-field), with AC-Q also on prime-field E(F_p). Every further B1-B3 ingredient I found is
either duplicated (K-1, K-2, K-4) or numerically vacuous at B <= p^{1/4} (K-7, K-9, K-10, K-13..K-15, K-18, K-19).
B2, the solving degree, has no additive-combinatorial handle beyond what LEAD-ICP-digit-presentation-solving-degree
already measures. B3 is constant engineering, and this field supplies no constant beyond K-19.

**Cross-scout dedup for AC-Q.** I grepped every `scout-*.md` for "four-list", "ktree", "k-tree", "ffe1df",
"quasigroup", "bucket hole" and "Latin square". No other scout addresses LEAD-EXO-four-list-ktree-join or the bucket
hole. scout-query-communication C5 is a single-statistic heavy-Fourier-coefficient FFT (the AGS conversion, my K-6).
AC-Q's distinct content is the per-bucket l2 saving: M^{3/2} Gamma instead of M^2 Lambda, valid for every Latin
square.

## 7. Side flags for the coordinator (no action taken)

- **F-1.** LEAD-ICE-decomposition-probability-audit plans a sampled variance against size-matched random bases. Its
  positive branch is "names a clustering effect worth a targeted collector". IDEA-20260811-7734c5's identity says the
  target-variance excess at arity m IS the excess count of base-internal 2m-term zero-sum relations. Those are
  target-free IC rows, so the positive branch is a free-relation source and belongs to
  LEAD-ICP-coincidence-harvest-structured-base's pricing, not to a targeted collector. Both leads measure the same
  Parseval quantity at matched order, so one exact energy count (O(B^2) x-key enumeration at m = 2) decides both.
- **F-2.** KN-FIND-ffe1df's j = 2 row ("UNPROVED ... the bucket hole is fatal here") should be re-read against
  Lemma Q once it is reviewed.

## 8. Citations

- Agrawal, Saha, Schwartzbach, Vanukuri, Vasudevan, "k-SUM in the Sparse Regime", arXiv 2304.01787 / ePrint
  2023/488. **retrieved** (PDF text read): Conjecture 1.1/3.5, Theorem 4.8, Corollary 4.9, and DKK21 Theorem 4.6 as
  quoted there. https://arxiv.org/pdf/2304.01787
- Dinur, Keller, Klein, "Fine-grained cryptanalysis: tight conditional bounds for dense k-SUM and k-XOR" (FOCS 2021).
  **recalled**; read only as quoted in ASSVV23.
- Kopelowitz, Porat, "The strong 3SUM-indexing conjecture is false" (CoRR 2019). **retrieved** (title only, from the
  ASSVV23 bibliography).
- Ahmadi, Shparlinski, "Exponential sums over points of elliptic curves", arXiv 1302.4210. **retrieved** (PDF text
  read): Lemma 1 restates Kohel-Shparlinski [17, Cor. 1] as sum_{n in Z_T} psi(x(nG)) chi(nG) << q^{1/2}.
  https://arxiv.org/pdf/1302.4210
- Kohel, Shparlinski, "Exponential sums and group generators for elliptic curves over finite fields", ANTS IV,
  LNCS 1838 (2000) 395-404. **recalled** for the exact constant; the author PDF refused connection in this session.
- Kiltz, Winterhof, "On the interpolation of bivariate polynomials related to the Diffie-Hellman mapping",
  Bull. Austral. Math. Soc. **retrieved** (PDF text read: Lemma 1, Theorems 5-6, and the statement "The results of
  this section extend and improve [8, Theorem 3]", where [8] is Lange-Winterhof). This is the nearest retrieved prior
  art for K-2.
- Lange, Winterhof, "Polynomial interpolation of the elliptic curve and XTR discrete logarithm", COCOON 2002, LNCS 2387,
  137-143. **recalled** for the statement; the bibliographic entry was seen on Tanja Lange's publication page, which
  has no PDF.
- Shparlinski, Stange, "Character sums with division polynomials", Canad. Math. Bull. 55 (2012). **recalled** in this
  run (abstract retrieved in run 1).
- Lauter, Stange, SAC 2008. **recalled**.
- Weil / Deligne (Lang torsor, Kummer sheaves); Burgess; Ben-Or-Coppersmith-Luby-Rubinfeld (2008); Gowers-Long
  (GAFA 2020); Elekes-Szabo (2012); Bays-Breuillard (2021); Stevens-de Zeeuw (2017); Rudnev (2018); Hou-Leung-Xiang
  (2002); Bachoc-Serra-Zemor (2017/18); Bourgain-Glibichuk-Konyagin (2006); Cilleruelo-Garaev-Ostafe-Shparlinski
  (2012); Kane-Lovett-Moran (2019); Akavia-Goldwasser-Safra (2003); Schroeppel-Shamir; Wagner (2002). All
  **recalled**.
- Internal, read this session: KN-FIND-ffe1df; `analysis/o2-sum-compatible-filters/README.md` and
  `O2_composition_closure.md`; EXP-ICEX-153c34 `specification.yaml`; IDEA-20260811-7734c5; H-EWALK-29cb90; and the
  lead YAMLs quoted above.

## 9. Fields searched, nothing surviving

- Sum-product / Elekes-Szabo / expanding polynomials as a constructive prime-field decomposition oracle (B1).
- Szemeredi-Trotter and energy bounds over F_p as closures of the coincidence lead (B1).
- Kloosterman / Weil / Burgess control of decomposition counts at IC sizes (B1-B3).
- Fourier preselection of decomposable targets (B1).
- Linear Kneser/Vosper/3k-4 for binary and Koblitz bases (B4/B5; already in cryptanalysis).
- BGK subgroup sums and GGM canonicalisation for equivalence classes beyond Aut (B6; dominated by SO-GEN, and
  duplicated).
- Teske trapdoor over F_{p^6} and Jacobian carriers (B5/B7): no additive-combinatorial content.
- Algebraic 3SUM / polynomial partitioning / linear decision trees: no F_p analogue.
