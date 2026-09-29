# TASK-20260926-995431 (G1) generator report: the arity lever against the product law

Lane: idea-generator, policy research-deep. Seam G1 of
`analysis/binstd-idea-review-20260926/BRIEF.md`. Four records filed under
pre-minted ids; no existing record edited; no run, no status change. Every
number below is hand arithmetic from this session and is labelled for
recomputation; nothing was executed (this lane has no shell).

## 1. The four proposals

| id | class | question | claim (25 words) | target m, oracle budget | novelty | cost |
| --- | --- | --- | --- | --- | --- | --- |
| IDEA-20260926-136bd3 | control | RQ-BINSTD-b6f698 | Exact sum-compatible filters on ECC2K-130 carry 2 bits (cofactor); an ideal 16-list tree with orbit unknowns would beat rho by 13 bits; approximate capacity measured on Koblitz toys. | k = m = 16 (stake); aa2efc has no row; corrected budget 2^49.7; ideal tree 2^29.8 per attempt needs a 2^25.8-alphabet filter, exact capacity 4 | unverified | impl medium, compute low |
| IDEA-20260926-178821 | mechanism | RQ-BINSTD-b6f698 | Over the 524 known-log Frobenius conjugates of P and Q, one decomposition at arity about 23 solves ECC2K-130; rho is its generic oracle; sumset redundancy fixes the true arity. | m about 23 nominal (higher after the coverage deficit); budget = the whole rho, 2^60.81, zero relations, zero linear algebra | unverified | impl medium, compute low |
| IDEA-20260926-1db0e8 | control | RQ-BINSTD-b6f698 | Large primes on subspace bases move arity into the large-base oracle: j = 1 is a birthday search, j = 2 costs 2^124 C_2(B')/B'; one reopening condition measurable. | rows priced at m = 13 (j = 1, B = 2^8) and m = 8 (j = 2); aa2efc budget at m = 8 is 2^25.2, corrected 2^42.2; the rows cost >= 2^63 and 2^124 O(n) | unverified | impl low, compute low |
| IDEA-20260926-4b65e3 | mechanism | RQ-CERTBIN-836ce2 | With the per-target cap and B re-optimised, the ECC2K-130 oracle budgets are about 2^11, 2^33, 2^37, 2^42, 2^50 at m = 4, 5, 6, 8, 16; the lever is the (1/2 - 1/m) line. | m in {4, 5, 6, 8, 16}; budgets as stated versus the finding's 2^4.4, 2^12.4, 2^18.0, 2^25.2 | unverified | impl medium, compute medium |

Every record: full `idea` schema plus the lane's fields, `added: '2026-09-26'`,
`status: proposed`, `approved_by: null`, the prescribed
`id_allocation_provenance`, a runnable-shaped `minimal_test.cell` naming the
curve, m, l, targets, seeds, instrument paths (with `missing:` where an engine
is absent), metrics with units, controls (null object of the same shape,
ordinary-curve control, relabelled Z/lZ control), a three-row outcome table, a
pre-registered falsification threshold, and an order-of-magnitude cost labelled
as an estimate.

## 2. Which to test first, and why

**IDEA-20260926-4b65e3, Stage 0.** It is the cheapest valid discriminator in the
lane: a zero-run Python recomputation (seconds) that either reproduces
KN-FIND-aa2efc's four free-oracle floors to two decimals (I reproduced
2^89.25, 2^68.58, 2^56.40, 2^48.44 by hand, which identifies the model as
relations = B, attempts = m! 2^131 / B^m, LA = m B^2) and emits the corrected
oracle-budget column, or fails to reproduce them and voids the correction. Every
other record in this lane, and every m >= 4 record in the cluster, prices itself
against that column; if the column is off by 17-20 bits at m >= 5, as I compute,
the seam's question changes from "an oracle at 2^12 per attempt at m = 5" to
"an oracle at 2^33". The second test is 136bd3's Stage 1 (exact controls read
2 and 4 on the n = 19 Koblitz cell), because it gates a measurement whose LEAD
branch is the only exponent-relevant outcome in the lane.

## 3. Arithmetic performed this session (all to be recomputed)

- Product-law model identification: floors at m = 2, 3, 4, 5 reproduced exactly.
- Corrected budgets with the per-target cap mu <= 1 and B re-optimised:
  m = 4: 2^11.0 at B = 2^29.04 (sub-cap regime, LA binds); m = 5: 2^32.4 to
  2^32.6 at B = 2^27.6 to 2^28.0; m = 6: 2^36.7 to 2^37.0; m = 8: 2^42.2;
  m = 10: 2^45.5; m = 12: 2^47.5; m = 16: 2^49.7; m = 3: closed for every C >= 1.
- The cap line for cofactor-4 Koblitz curves: log2 C_budget(n, m) =
  (n - 2)/2 - 0.176 - (log2 n)/2 - (n + log2 m!)/m, slope 1/2 - 1/m.
- Ideal k-tree stakes on ECC2K-130 with orbit unknowns: k = 8 ties rho
  (2^59.95 + 2^52.4 vs 2^60.81); k = 16 at 2^47.6; without orbit unknowns
  k = 16 at 2^55.6, k = 8 at 2^68.5.
- Plain two-list join floor with sign and 131 conjugates: 2^62.5 per relation.
- Exact filter capacity of E(F_{2^131}): alphabets {1, 2, 4} below l.
- Single-large-prime free-leg form: attempts 2^59.0 sqrt(B), memory 2^58.0
  sqrt(B), tuple supply forces m >= 13 at B = 2^8, hence >= 2^63 time.
- Double-large-prime form: 2^124.0 C_2(B')/B'; the m = 2 subspace oracle is an
  enumeration of u in V' with Tr(u) = Tr(1/c) by an Artin-Schreier reduction of
  S_3 on y^2 + xy = x^3 + 1 (re-derive; the constant term is where an error
  would hide).
- Conjugate-base row: 524 signed points, mu = 1 at m = 22.6 under H1, nominal
  m = 23; the Z[tau] identity tau^2 + tau + 2 = 0 gives the weight-2 collision
  sigma^3 P + sigma P = -(sigma^2 P + sigma P).
- Toy Koblitz orders by the Lucas sequence t_{k+1} = -t_k - 2 t_{k-1}
  (t_0 = 2, t_1 = -1): n = 17 gives 130972 = 4 * 137 * 239 (composite, used as
  the capacity positive control); n = 19 gives 523492 = 4 * 130873 with 130873
  passing trial division to 359 by hand (prime if my division is right; the
  instrument must prove it). n = 19 shares the field t^19 + t^5 + t^2 + t + 1
  with the CERTBIN ordinary cell, giving a matched Koblitz/ordinary pair.

## 4. Discrimination from the nearest filed material (summary)

- 845a77 / faa8d2 (HOLD-P): the plain and solver-query MITM. 136bd3 (C4) is the
  per-relation birthday floor that closes every plain join at every cell, and
  (D) measures the one thing faa8d2's bucketed residual predicted but did not
  control for. Neither hold record states the capacity or the stake.
- c2bbe6 (HOLD-Q): 1db0e8 prices the j = 1 form with memory and tuple supply,
  and prices the j = 2 form HOLD-Q asked c2bbe6 to adopt, with the sub-oracle
  charged; c2bbe6's revision can cite its dominated_by from there.
- 793fd8 (HOLD-U): 178821 does not race rho against index calculus; it shows the
  two are one family and that rho is the m -> large endpoint.
- 2ef5c8 / fa9839 / EV-ICEX-2be32e: 4b65e3 uses the per-target cap
  (m! N)^{1/m} with linear algebra kept, applied to the binary Koblitz table.
- KN-FIND-ffe1df / 390ccc / ce1915: 136bd3 is the binary-Koblitz transplant of
  the filter-gain measurement with an exact capacity certificate and exact
  positive controls.
- KN-FIND-47da4e: the orbit-union base is used as a component in 136bd3's stake
  and named as an open direction (amortising the 131^{m-1} shift enumeration is
  FROB's equivariance question, IDEA-20260906-a77711), not re-proposed.

## 5. Honest accounting (docs/inventor-protocol.md section 5)

**Objects considered on seam G1.**

1. Sum-compatible filter h: E -> [M] for k-tree joins, exact and approximate
   (filed: 136bd3).
2. Frobenius-canonical half-sum tables and plain group-arithmetic k-lists
   (closed inside 136bd3, C1/C4).
3. Subspace-constrained intermediate sums, the chained tree (closed inside
   136bd3, C3).
4. Z[tau]-module block systems on the order-l subgroup (closed, section 5
   below; not filed).
5. Orbit-union (representative, shift) bases with the algebraic oracle (open
   direction, FROB-owned; not filed).
6. The target-dependent known-log conjugate base as the arity lever's endpoint
   (filed: 178821).
7. Large primes j = 1, j = 2, j >= 3 on subspace bases (filed: 1db0e8).
8. The cost model itself (filed: 4b65e3).

**Depth of verified structure.** Everything is derivation tier or arithmetic;
nothing is measured. The exact-capacity certificate rests on a
validator-confirmed theorem (KN-FIND-ffe1df Theorem C) re-run on a
composite-order group, a proof obligation stated in 136bd3. The Artin-Schreier
form of S_3 and the Z[tau] identity are derivations with a named place an
error would hide.

**dominated_by (Pareto, per proposal).** 136bd3: n/a (no attack); every k-list
construction priced is dominated by matched rho (2^60.81, O(1) per walk) on
time at every memory budget; the conditional stake would dominate rho only
given a 26-bit filter that (B) excludes exactly. 178821: matched rho ties the
row (it is the row's generic oracle) and dominates every memory-heavy generic
variant; no point below rho claimed. 1db0e8: matched rho dominates the j = 1
form on time and memory at every feasible cell and the j = 2 form on time by
about 63 bits under the natural sub-oracle; the cap-locus row of 4b65e3
dominates every large-prime row under unknown-count-monotone solvers. 4b65e3:
n/a (no result on any cost axis; a cost-model correction); rho unchanged;
the exact loop is dominated by 2^{n/2} at every m. Frontier rows checked in
each record: matched rho, BSGS, multi-target, preprocessing S T^2, the
finding's floors, the exact loop, Esser-May-type low-weight solvers (reported).

**sota_delta (quantitative).** Attack capability: zero on time, memory and
data/queries in all four. New numbers for the corpus: exact filter capacity 2
bits and ideal-tree stakes (2^47.6 at k = 16 with orbit unknowns, 13 bits below
rho; k = 8 ties); plain-join floor 2^62.5 per relation; the zero-relation
known-log row at budget 2^60.81; the j = 1 memory charge 2^58 sqrt(B) and the
j = 2 identity 2^124 C_2(B')/B'; the corrected oracle-budget column (about
+6.6, +20, +19, +17 bits at m = 4, 5, 6, 8) and the (1/2 - 1/m) line.

**Enumerated closures, each with mechanism (section 4 standard).**

- C1. Exact sum-compatible filters on ECC2K-130 have alphabet at most 4.
  Mechanism: Theorem C's quasigroup argument on a group of order 4l; the
  subgroup lattice has no quotient of order between 4 and l. Scope: exact
  filters; approximate filters are measured, not closed.
- C2. Group-arithmetic k-lists without a filter cost >= 2^62.5 per relation at
  every arity and base size. Mechanism: expected matches L_1 L_2 * 262 / 2^131
  (mean exact by double counting); above rho before one relation. Scope: joins
  by exact equality with sign and Frobenius matched free.
- C3. Trees with x-subspace-constrained intermediate sums cost >= l C_3 / (2B).
  Mechanism: a non-subgroup constraint costs its density in probability at
  every level and does not compose (Theorem C); enumeration in disguise.
- C4. Z[tau]-module block systems on the order-l subgroup are the
  <lambda, -1>-orbit partitions, i.e. rho's classes. Mechanism: the subgroup is
  Z[tau]/(Phi) with Phi of prime norm l, so tau acts as the scalar lambda and
  IDEA-20260901-863e36 (C1)/(C3) applies with Gamma = <lambda, -1> of order 262;
  no new lossy object and only the sqrt(262) class gain rho already takes.
- C5. Single-large-prime free-leg relation collection is a birthday search:
  2^59.0 sqrt(B) time, 2^58.0 sqrt(B) memory, feasible only at B >= 2^8 where
  time >= 2^63. Mechanism: the optimal large base is the whole group, at which
  the construction is collision search with Shoup's bound.
- C6. Double-large-prime relation collection costs 2^124 C_2(B')/B'.
  Mechanism: locating two large legs is an m = 2 decomposition over F' per
  target, which for a subspace base is an enumeration of u in V' (Artin-Schreier
  reduction); there is no smoothness test on E, which is what GTTD's
  hyperelliptic gain relies on.
- C7. The finding's oracle-budget column is the linear reading at the
  free-oracle-optimal B and understates the budget at m >= 5 by about 17-20
  bits. Mechanism: enforcing mu <= 1 per target and re-optimising B moves the
  optimum to B_cap where attempts are 1 and LA is below rho. This is a
  correction of a record, not a closure of the lane.
- Not closed, stated so it is not mistaken for closed: approximate filters on
  Koblitz curves (measured by 136bd3), the coverage deficit of the conjugate
  base (measured by 178821), the small-block-only descent oracle (measured by
  1db0e8), and theta(m) at the cap locus (measured by 4b65e3). "Every
  group-arithmetic oracle is generic" is a heuristic about oracles that use
  only group operations and membership; a subspace membership is non-generic
  and its exploitation is the algebraic route, owned by SEMBIN/SDEG/G2.

**Open directions for the next session.**

1. The filter-gain ladder on Koblitz cells (136bd3): the only exponent-relevant
   LEAD branch in the lane; run its Stage 0-1 first because the controls are
   exact.
2. The conjugate-base coverage deficit (178821) and its second reading: a small
   structured sumset at fixed weight is a smaller search space for a structured
   knapsack solver in normal basis; hand to FROB/SEMBIN if the deficit is real.
3. theta(m) at the cap locus for m in {3, 4} (4b65e3), then m in {5, 6} once
   S_6/S_7 builders exist at n >= 37; price G2's refutation-asymmetry lever AT
   the cap, where it is worth at most about 2.7.
4. Amortising the 131^{m-1} shift enumeration of an orbit-union base to O(1)
   systems per target (IDEA-20260906-a77711's equivariance question): worth at
   most 2^7 on the relation column, which matters at m = 4 (budget 2^11) and
   not at m >= 5 (budgets 2^33 and up).
5. A Koblitz repeat of 1db0e8's asymmetric-block ladder, and the hyperelliptic
   toy where large primes MUST pay, as the proves-too-much control.
6. The "polynomial in m" oracle the seam asked for now has a numeric target:
   2^37 per attempt at m = 6 on a system with about 138 Boolean unknowns after
   descent, i.e. a structural speed-up of about 2^{0.3 n} over exhaustive
   evaluation at the cap locus. No record in this lane proposes one; the honest
   statement is that the target is now priced, not reached.

## 6. Files written (absolute paths)

- /home/user/crypto-autoresearcher/ledger/proposals/IDEA-20260926-136bd3.yaml
- /home/user/crypto-autoresearcher/ledger/proposals/IDEA-20260926-178821.yaml
- /home/user/crypto-autoresearcher/ledger/proposals/IDEA-20260926-1db0e8.yaml
- /home/user/crypto-autoresearcher/ledger/proposals/IDEA-20260926-4b65e3.yaml
- /home/user/crypto-autoresearcher/analysis/binstd-idea-review-20260926/reviews/TASK-20260926-995431-generator-report.md

YAML parse disclosure: no interpreter was available to this lane; every
multi-line value is a folded block scalar, quoted strings containing
apostrophes use doubled single quotes, and one plain scalar that contained a
hash character was rewritten to avoid a comment truncation. The dispatcher's
`python3 -c "import yaml; yaml.safe_load(open(path))"` is the check.
