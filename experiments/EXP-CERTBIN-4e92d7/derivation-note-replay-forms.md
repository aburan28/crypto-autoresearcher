# Derivation note -- exact replay-form algebra for EXP-CERTBIN-4e92d7 (regime A, n = 17)

- **Status:** `derivation`. This is a checkable written argument, not a machine-verified proof.
- **Cited by:** EV-CERTBIN-6c3e0a `proof_refs` and DEC-20260923-f25b97.
- **Source:** RT-20260923-29e7af J4-F2 and J4-F3, restated here by the Coordinator so that it can be read on its own.
- **Scope:** the fixed-schedule replay of RUN-CERTBIN-3b7e05's archived reference op logs, at n = 17 and D in {3, 4}. The lemmas are general. The numbers are this cell's.

## Setup

Let r in F_2^n (n = 17) be the target bits, and let M(r) = M_D(E(r)).

M(r) is exactly affine over F_2: M(r) = M_0 + sum_j r_j M_j. The reason is that x_R enters S_3 only through x_R and x_R^2, both F_2-linear in r, and the Macaulay construction is F_2-linear in E. This was verified per instance by C-AFF, J1 and J6.

A reference op log is a sequence (p_k, c_k, X_k), k = 0..L-1. Let L_{<k} be the product of the elementary row additions of steps j < k (add row p_j into every row of X_j). L_{<k} does not depend on r. Replay is fixed: the matrix before step k is L_{<k} M(r).

## Lemma 1 (affine pivot forms)

e_k(r) := (L_{<k} M(r))[p_k, c_k] = a_{k,0} + <a_k, r>, where:
- a_{k,0} = (L_{<k} M_0)[p_k, c_k];
- (a_k)_j = (L_{<k} M_j)[p_k, c_k].

*Proof.* L_{<k} is a fixed F_2-linear map, extracting an entry is linear, and M(r) is affine in r. ∎

## Lemma 2 (the survival set is a coset of dimension n - K_rank)

Let Sigma = {r : e_k(r) = 1 for all k}, let A be the matrix whose rows are the a_k, and let K_rank = rank_F2(A). Then r_ref is in Sigma, and Sigma = r_ref + ker A, so dim Sigma = n - K_rank. In particular, if K_rank = n then Sigma = {r_ref}.

*Proof.* The reference's own elimination chose each (p_k, c_k) with a 1 in its current matrix, and replay at r_ref reproduces those matrices (REF_SELF_REPLAY; J5 O1(a)). Hence r_ref is in Sigma. Sigma is the solution set of the linear system <a_k, r> = 1 + a_{k,0}. It is non-empty, so it is a coset of ker A. ∎

**Corollary 2a (T_ops).** Suppose a target t has T_ops(t) = T_ops(ref). Then its own elimination performed exactly the replay's operations, with pivot entry 1 at every step, so r_t is in Sigma. T_ops retention on a target set T is therefore at most |Sigma ∩ T| / |T|.

At this cell:
- K_rank = 17 for all 6 references at D = 3 and D = 4 (references.json, reproduced by J1, J3, J4 and J6/J7);
- solving explicitly for the 6 D = 4 references returns r_ref each time (j4-exact/predictions-D4.json);
- F-S3 test targets exclude the references' x_R by construction.

So T_ops, i.e. fixed-schedule, retention on F-S3 is 0 exactly, as an identity.

**Corollary 2b (why retention is not 2^{-K}).** For uniform r, Pr[r in Sigma] = 2^{-K_rank} >= 2^{-n}, whatever K (the number of nonzero a_k) is. With K about 2670 and K_rank <= 17, at most n of the K divergence events are independent. "Retention about 2^{-K} with near-independent divergences" therefore cannot hold.

T_strict equality does not imply T_ops equality, because the X-sets may differ. Corollary 2a therefore does not bind T_strict, and the 0/386 T_strict retention is an empirical result, not a derived one.

## Lemma 3 (exact hazard law)

Definitions:
- T is the target set, and H = h_0 + W is its affine hull.
- S_k = {r in T : e_j(r) = 1 for all j < k} is the set of survivors at step k.
- Sigma_k = {r in H : e_j(r) = 1 for all j < k} is the survivor subspace.

Suppose <a_k, .> restricted to W lies in the span of the restrictions of {<a_j, .> : j < k}. Equivalently, a_k lies in span{a_j : j < k} + W^perp. Then:
- e_k is constant on Sigma_k;
- if r_ref is in H, the constant is e_k(r_ref) = 1;
- so h_k = #{r in S_k : e_k(r) = 0} / |S_k| = 0 EXACTLY.

A hazard of 1 cannot occur.

*Proof.* Take r and r' in Sigma_k. Then r - r' is in W, and <a_j, r - r'> = 0 for every j < k. By the hypothesis, <a_k, r - r'> = 0. So e_k is constant on Sigma_k. The reference r_ref is in Sigma_k (by self-replay, and because r_ref is in H), so the constant is 1. ∎

If instead a_k is independent modulo span{a_j : j < k} + W^perp, then e_k is a nonconstant affine function on Sigma_k. It vanishes on exactly half of Sigma_k, and on a sample from Sigma_k, h_k is about 1/2 with sd about 1/(2 sqrt(S_k)).

**Curve targets.** In F_2[t]/(t^17 + t^3 + 1), Tr(t^j) = 0 for j = 1..16 (computed; j4-exact/curve-constraint.json), so Tr(x) = r_0. All 1000 F-S3 targets and all 5 references have r_0 = 0 (measured). Hence e_0 is in W^perp, and the hull has dimension 16 (measured).

A pivot with a_k = e_0 is therefore constant on F-S3 and nonconstant on F-RANDX. This accounts exactly for K_exact - K_sampled. The fact that the x(2E) trace is fixed is recalled and not relied on: only the measured r_0 = 0 is used.

## Application to HEUR-CERTBIN-TS1

TS1 asserts h_k in [0.4, 0.6] for every pivot whose e_k is nonconstant over the sampled targets.

Take a pivot with a_k = a_j for some j < k, where e_j is itself nonconstant over T. Then e_k = e_j + const, so e_k is nonconstant over T and lies inside TS1's quantifier domain. Yet by Lemma 3 its hazard is h_k = 0.

Explicit instances at D = 4 (j4-exact/forms-D4.json and p2-table.tsv; the h values are in the archived pivot-hazards.json and are reproduced by J3's own forms):

| reference | pivots k | a_k (repeats) | S_k | h_k |
|---|---|---|---|---|
| U2 | 1 | e_15 = a_0 | 507 | 0 |
| U2 | 3 | e_14 = a_2 | 250 | 0 |
| U2 | 4 | e_15 | 250 | 0 |
| U3 | 1, 2, 3 | e_16 = a_0 | 492 | 0 |
| U3 | 5-9 | e_13 = a_4 | 249 | 0 |

TS1's formal statement is therefore false at this cell. ∎

Beyond the P2 set, 76-78 of the 86-90 live pivots per reference are of this type (j4-exact/allpivots-D4.json).

**DR-4 as a threshold (consequence).** Take N = 993 and balanced rank-increasing pivots. S_k roughly halves at each rank-increasing pivot: 993, then about 497, 248 and 124. So the cut S_k >= 200 admits about 3 rank-increasing pivots per reference, i.e. n_IND is about 15 over 5 references (observed: 15). The in-band fraction is then 15 / (15 + n_rep), where n_rep is the number of repeated-form pivots. It follows that:
- the fraction is >= 0.9 iff n_rep <= 1;
- the median is < 0.2 iff n_rep >= 16;
- the observed n_rep = 11 gives "not supported, not falsified".

## Independent checks

1. **RT-20260923-29e7af J4.** Its own replay (no import of the impl's replay code) on the archived constructor, which J1 found bit-identical to a spec-literal construction. 0 of 26 mismatches in P2, and 0 over all pivots of all 6 references.
2. **VAL-20260923-a679de J3.** Its own M_4 and its own affine forms. 5,900 first-zero comparisons with 0 mismatches, and the 11 h = 0 pairs reproduced.
3. **J6 blind re-derivation, compared in J7.** The rank-increment flags of the first 64 nonzero a_k agree with the run's on 192 of 192 entries, and a_k agrees at 8,015 steps.

## What this note does not show

- Anything about T_strict retention, which is empirical.
- Whether K_rank = n holds at other n, curves, V or orders. K_rank <= n always holds, but its value elsewhere is unmeasured.
- Anything about regime B, where pivot entries are not F_2-affine in the target.
- Any universal statement about trace replay.
