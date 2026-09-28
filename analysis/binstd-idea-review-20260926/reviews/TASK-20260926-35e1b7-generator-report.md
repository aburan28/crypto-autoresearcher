# TASK-20260926-35e1b7 (S2) generator report: the linear-algebra and relation side

Lane: idea-generator, policy research-deep, round 2, seam S2 of
`analysis/binstd-idea-review-20260926/BRIEF-ROUND2.md`. Four records filed
under pre-minted ids; one id returned unused with the reason below; no
existing record edited; no run, no status change. Every number is this
session's hand arithmetic on `IDEA-20260926-4b65e3`'s model
(rho = 2^60.81, N = 2^131, N' = r/262 = 2^120.97) and is labelled for
recomputation. This lane has no shell: nothing was executed, and the YAML
files were checked by inspection (every prose scalar is a `>-` block; the
one list item containing `: ` was quoted), not by `yaml.safe_load`. The
lane was interrupted once by an API rate limit after the first file was
written; that file was re-read in full, found complete, and rewritten with
the one quoting fix.

## 1. The four proposals

| id | class | question | claim (25 words) | target m, budget | novelty | cost |
| --- | --- | --- | --- | --- | --- | --- |
| IDEA-20260926-201e86 | mechanism | RQ-BINSTD-b6f698 | e = ord_131(r) = 1 is forced; the block-circulant relation matrix has exactly one live Fourier block, so LA is m (B/131)^2 and no lower; matters at m = 4 only. | m = 4: budget 2^11.0 plain, f^3 per LA-dimension lever up to f = 29, 2^33.9 with the orbit quotient if the 131^{m-1} shift enumeration is amortised, 2^12.8 if not; m >= 5 unmoved | unverified | impl low, compute low |
| IDEA-20260926-20ba8f | mechanism | RQ-BINSTD-b6f698 | Index calculus amortises as L^-1 against rho's L^-1/2; on the generic S T^2 = N' frontier the per-attempt budget is 2^43.5, 2^46.7, 2^48.8, 2^51.3 at m = 4, 5, 6, 8. | every m >= 4; preprocessing budget column 5 to 32 bits above the single-target one; an m = 5 oracle g < 13.2 bits over budget beats Kuhn-Struik rho for L in [2^(2g), 2^(56.8-2g)] | unverified | impl low, compute low |
| IDEA-20260926-3c6a19 | mechanism | RQ-CERTBIN-836ce2 | Above the cap each target yields mu = B^m/(m! N) relations; the calls column is B/mu, per-call budgets 2^37 (m = 5), 2^50 (m = 6); pays iff the oracle's solution-count elasticity is below (m-1)/m. | m >= 5 (no window at m = 4); per-call budgets 2^37.1 at (5, B = 2^29), 2^50.3 at (6, 2^26), about 2^60 at one call | unverified | impl low, compute medium |
| IDEA-20260926-3cc0b8 | control | RQ-ICPERF-94c86e | At the ECC2K-130 cap locus block Wiedemann needs 435 GB (m = 5) to 1.2 TB (m = 4) against rho's 1.7 TB Theta(P) floor at P = 2^30; 2e2a58's E2 fails by 20+ bits; width does not bind. | instrument; no m moved; bytes column per m | unverified | impl medium, compute low |

Every record carries the full `idea` schema, the lane's extra fields,
`added: '2026-09-26'`, `status: proposed`, `approved_by: null`, the
prescribed `id_allocation_provenance`, a `prior_art` block with rows read
from the rendered frontier map (provenance `retrieved`), a runnable-shaped
`minimal_test.cell`, instrument paths with `missing:` where an engine is
absent, metrics with units, controls (null object, ordinary-curve or
Koblitz control, relabelled Z/NZ control), a three-row outcome table, a
pre-registered falsification threshold, and an order-of-magnitude cost
labelled as an estimate. Budgets are stated per attempt (or per call),
never as the floor-to-rho gap.

## 2. Which to test first, and why

**IDEA-20260926-20ba8f, Stage 0**, then **IDEA-20260926-201e86, Stage 0-1**.
20ba8f's Stage 0 is a zero-run Python recomputation (seconds) that either
reproduces the preprocessing budget column and the identity P_IC = P_gen at
C = sqrt(N'/B_cap), or fails and voids the record; if it reproduces, every
oracle record on the seam gains a second, much more forgiving line (32 bits
higher at m = 4), which changes what the CERTBIN cap-locus ladder is worth.
201e86's Stage 0 is one modular reduction (131 | r - 1) and its Stage 1 is
two exact checks on the n = 19 Koblitz cell (right-hand sides vanish off the
live character; the live block equals 261004's quotient system), minutes on
installed instruments; it removes an open number from a record already in
BATCH-b67954 and corrects a factor-131 discrepancy between two records that
batch absorbed. Both are the cheapest valid discriminators because their
predicted outcomes are forced by derivation and a failure localises an
arithmetic or instrument error rather than a hypothesis.

## 3. Arithmetic performed this session (all to be recomputed)

- e = 1: n | r - 1 at n = 19 (130872 = 19 x 6888) and at both prime factors
  of the composite n = 17 cell (136 = 17 x 8, 238 = 17 x 14). ECC2K-130's r
  was NOT reduced mod 131 by hand; the claim rests on 261004 (A).
- Row-DFT of a conjugate family at character t: right-hand side is
  sum_j lambda^j zeta^{-tj}, which is 131 log R at zeta^t = lambda and 0
  otherwise; the live block is 261004's quotient row verbatim.
- m = 4 exchange rate: minimising A B^{-3} + D B^2 gives C_max proportional
  to D^{-3/2} = f^3; cap reached at D = 2^-7.73, f = 2^4.87 = 29; budgets
  2^11.0 (plain), 2^26.9 (cap-bound, plain relations), 2^33.9 (orbit
  quotient, relations 2^26.87, LA 2^55.7, shifts amortised), 2^12.8 (shifts
  at 131^3 = 2^21.1); m = 5 orbit quotient 2^40.2 amortised, 2^12.1 at
  131^4 = 2^28.1.
- Generic frontier at the cap: T_gen = sqrt(N'/B_cap), P_gen = sqrt(N' B_cap):
  (m, log2 B_cap, log2 T_gen) = (4, 33.90, 43.54), (5, 27.58, 46.70),
  (6, 23.42, 48.78), (8, 18.29, 51.34), (16, 10.95, 55.01); the line
  log2 T_gen = (1/2)(1 - 1/m) n - (3 + log2 n + (log2 m!)/m)/2.
- m = 5 crossing window against 2^60.81 sqrt(L): 2^{g-28.4} s^2 - s + 2^g < 0
  in s = sqrt(L); real roots iff g < 13.2; L in [2^{2g}, 2^{56.8-2g}].
- Above-cap window: B_LA = sqrt(rho/m) = 2^29.40, 2^29.24, 2^29.11, 2^28.9
  at m = 4, 5, 6, 8; empty at m = 4; m = 5 at B = 2^29.0: LA 2^60.32,
  remaining 2^59.0, mu 2^7.1, calls 2^21.9, budget 2^37.1 per call; m = 6 at
  B = 2^26: LA 2^54.6, mu 2^15.5, calls 2^10.5, budget 2^50.3; at B = 2^28,
  mu 2^27.5, one call. Neutral elasticity (m-1)/m; enumeration sits on it
  exactly (the m N identity); MITM at ceil(m/2)/m.
- Bytes (17 B per word, 32 B per DP): m = 5 cap vector 2^31.7 B, relations
  2^32.7 B, block Wiedemann n0 = 64 2^38.7 B; m = 4 sub-cap n0 = 64 2^40.1 B;
  rho at P = 2^30, epsilon = 0.01: 2^35.64 records = 2^40.64 B; E2 ratios in
  2e2a58's units 2^-6.6 (m = 4), 2^-8.1 (m = 5); p_flip about 2^28; width
  floor 2^22.6 L_mv at m = 5 (1.7 h at 1 ms); rho meets it at P = 2^42.5.

## 4. Discrimination from the nearest filed material (summary)

- 261004 / b19793 (absorbed into BATCH-b67954): 201e86 resolves b19793's open
  e to 1, shows only one of its blocks is live, and reconciles its factor n
  with 261004's and KR-IC-b0fcda's n^2; 61049d is the prime-field j = 0
  cousin of the isotypic argument.
- 2e2a58 and its review: 201e86 measures the spectral quantity the review
  named as the successor seam, on the live block; 3cc0b8 evaluates the
  region model at the ECC2K-130 arity rows and finds E2 fails there.
- 9191ed, a67a1d, d20846 (filtering, peeling, fold-before-peel): own the
  dimension-reduction measurement; 201e86 only prices their gain f through
  the m = 4 exchange rate. This is why the seam's filtering candidate got
  no separate record (section 6).
- KR-IC-081a58 (Joux-Vitse static DH), KR-RHO-46c2c6, KR-RHO-ea34b8,
  H-ICEX-9e54c2, 2e37b3: 20ba8f is the amortisation mechanism priced on
  ECC2K-130 against the S T^2 frontier and Kuhn-Struik, which none of them
  does.
- KN-FIND-007, H-ICEX-9e54c2, H-PFDR-26bcee, 4b65e3, 96c4f3, 845a77: 3c6a19
  names the elasticity that separates the harvest-all and cap conventions,
  prices the above-cap window with the LA ceiling, and measures it.
- 136bd3 (C4) and 1db0e8: close the seam's other two "not one-to-one"
  candidates (sumset collisions, partial decompositions) and are cited.

## 5. Honest accounting (docs/inventor-protocol.md section 5)

**Objects considered on seam S2.**

1. The Z/131 Fourier blocks of the raw relation matrix, with the log vector
   as a lambda-eigenvector (filed: 201e86).
2. The live block's minimal polynomial and displacement rank against a
   configuration-model null (filed inside 201e86).
3. The LA-dimension lever f in general (filtering, peeling, merge, SGE,
   orbit quotient) and its exchange rate on the oracle budget (priced inside
   201e86; not filed separately, section 6).
4. The shared/per-target split and the advice size S at the cap locus,
   against Kuhn-Struik and the S T^2 frontier (filed: 20ba8f).
5. All-solutions oracle calls above the cap and the solution-count
   elasticity (filed: 3c6a19).
6. Relations among factor-base elements by collision inside the sumset
   (closed, C1 below; not filed).
7. Partial decompositions and large primes (closed by 1db0e8; not filed).
8. The bytes and width of the LA phase at the cap-locus rows, against
   rho's Theta(P) floor (filed: 3cc0b8).
9. The toy elimination's fill-in law (filed inside 3cc0b8).

**Depth of verified structure.** Derivation tier or arithmetic throughout;
nothing measured. 201e86 (A)-(B) rest on 261004's theorem plus the DFT; the
identities in 20ba8f (C) and 3c6a19 (B)-(C) are algebra on 4b65e3's model;
3cc0b8 (A)-(D) are arithmetic under 2e2a58's reviewed model.

**dominated_by (Pareto, per proposal).** 201e86: n/a (no attack); matched
rho (2^60.81, O(1) per walk) dominates every IC cell with or without the
orbit-quotient LA, since the lifted m = 4 budget is conditional and
unmet; BSGS dominated by rho; multi-target rows untouched. 20ba8f: n/a; at
L = 1 rho dominates; at L targets Kuhn-Struik dominates unless an oracle is
within 13.2 bits of the single-target budget; on the preprocessing frontier
Bernstein-Lange dominates unless C < sqrt(N'/B_cap); no oracle known to meet
either. 3c6a19: n/a; rho dominates every above-cap cell because the two
oracles with known elasticity (enumeration, MITM) sit at m N and above rho.
3cc0b8: n/a; rho dominates on time at every P; on memory the sides are
within a few bits at realistic P and rho wins below p_flip. Frontier rows
checked in each record: matched rho, BSGS, multi-target (KR-RHO-46c2c6),
preprocessing (KR-RHO-ea34b8), time-space (KR-RHO-7d93f6), the finding's
floors, the exact loop, the MITM engine.

**sota_delta (quantitative).** Attack capability: zero on time, memory and
data/queries in all four. New numbers for the corpus: e = 1 forced and the
n^2 LA gain shown exhaustive (a factor-131 correction to b19793's block
accounting); the m = 4 exchange rate f^3 with ceiling f = 29 and the
conditional 23-bit lift; the preprocessing budget column (2^43.5 to 2^55.0
at m = 4 to 16, relaxations of 32.5 to 5.3 bits); P_IC = P_gen at
C = T_gen; the m = 5 crossing window in g; the above-cap per-call column
(2^37.1, 2^50.3, about 2^60) and the neutral line (m-1)/m; the bytes column
(2^29.4 to 2^40.1 B for block Wiedemann at n0 = 64) with E2 ratios of
2^-6.6 to 2^-17.3 and p_flip about 2^28.

**Enumerated closures, each with mechanism (section 4 standard).**

- C1. Relation collection by collision inside the m-fold sumset of the
  factor base (no target) is a generic procedure and costs at least
  2^62.5 per relation on ECC2K-130. Mechanism: it uses only group
  operations and equality, so Shoup's bound (KR-RHO-13bf67, via
  IDEA-20260901-863e36 C4) applies to the whole pipeline, and
  IDEA-20260926-136bd3 (C4) prices the join's birthday floor with sign and
  Frobenius matched free. Scope: joins by exact equality; the non-generic
  variant (V'-membership on the sums) is the large-prime graph, closed by
  1db0e8.
- C2. The Z/131-equivariant reduction of the LA phase is exactly 131^2 and
  cannot be improved by symmetry. Mechanism: e = 1 forces a complete
  splitting of F_r[Z/131]; the log vector is a lambda-eigenvector, so one
  Fourier block is live and the other 130 are homogeneous with zero
  solution; beyond Z/131 the module block systems on the order-r subgroup
  are the <lambda, -1>-orbits (G1's C4), already absorbed. Scope: symmetric
  reductions; the non-symmetric residue is measured, not closed.
- C3. LA-dimension levers (filtering, peeling, merge, SGE, orbit quotient)
  move the ECC2K-130 oracle budget only at m = 4, as f^3 up to f = 29, and
  by at most 0.15 bit at m = 5 and nothing at m >= 6. Mechanism: at m >= 5
  the LA at the cap is already 3.3 bits or more below rho, so dividing it
  cannot raise the budget; at m = 4 the sub-cap optimum's T_min is (5/3) D
  B^2 with D proportional to 1/f^2. Scope: 4b65e3's sparse model.
- C4. The orbit-quotient lift of the m = 4 budget to 2^33.9 is worth 1.8
  bits unless the 131^{m-1} shift enumeration is amortised, and the same
  lever is a 20-bit loss at m = 5 without amortisation. Mechanism:
  KN-FIND-47da4e's cost-neutral (representative, shift) encoding; the
  relation saving is 2^7 and the shift cost is 2^21 (m = 4) or 2^28 (m = 5).
  Scope: orbit-union bases; a77711's equivariance question is the one
  reopening condition.
- C5. The above-cap window is empty at m = 4. Mechanism: B_LA = sqrt(rho/4)
  = 2^29.4 is below B_cap = 2^33.9, so LA binds before the cap is reached.
- C6. The enumeration oracle gains nothing from the above-cap window.
  Mechanism: its elasticity is exactly (m-1)/m, the neutral line, which is
  the m N identity of 96c4f3 in another coordinate.
- C7. 2e2a58's preregistered E2 (memory ratio above 2^20 on every
  competitive row) fails on every ECC2K-130 arity row for P >= 2^28.
  Mechanism: the IC dimension at m >= 4 is 2^18 to 2^29 words while rho's
  Theta(P)/(2 epsilon) floor at P = 2^30 is 2^35.6 records; the
  preregistration was written for B' = N^{1/(m+1)} at small m. Scope: this
  population under 2e2a58's own model and units; its limb (B) and E1 are
  not contested.
- Not closed, stated so it is not mistaken for closed: the spectral
  genericity of the live block (measured by 201e86); the solution-count
  elasticity of algebraic oracles (measured by 3c6a19); whether any oracle
  meets the preprocessing budget column (20ba8f); the shift amortisation
  (FROB); the coverage concentration on subspace bases in the multi-target
  reading (measured by 20ba8f).

**Open directions for the next session.**

1. Carry both budget rows (single-target and preprocessing) on every oracle
   record of the seam; the CERTBIN cap-locus ladder should fit theta(m)
   against both lines.
2. Build the scalar/block Wiedemann engine once (3cc0b8 Stage 1); 201e86 (D)
   and 2e2a58 Stage 2 share it.
3. The m = 6 single-call regime (one target, 2^27.5 decompositions, 168
   unknowns, 131 equations, budget about 2^60) is an underdetermined
   descended system and belongs to SDEG/SEMBIN if 3c6a19's LEAD reading
   fires.
4. Compose 3c6a19 with 20ba8f: above the cap each target's own descent
   yields mu relations, so the per-target cost in the preprocessing row is
   C_all/mu.
5. The SGE bytes law and the 2-core fraction of ECDLP relation hypergraphs
   at the dependency threshold (a known random-hypergraph quantity, recalled
   from the XORSAT and peeling literature) would sharpen 9191ed's P1 and
   061f97's x_m; left with the peeling records.

## 6. Unused id

`IDEA-20260926-4e139a` is returned unused. It was reserved for the seam's
"NFS-style filtering priced honestly" candidate. On reading the corpus that
candidate is already three records (IDEA-20260915-9191ed's filtering stack
against a degree-matched null, IDEA-20260814-a67a1d's online peeling core
stopping, IDEA-20260807-d20846's fold-before-peel) plus 061f97's rank
threshold; the only number a fourth record would add is the exchange rate
of a dimension lever on the ECC2K-130 budget, which is C3 above and is
priced inside 201e86 (C). A fifth file would have been a repackaging.

## 7. Files written (absolute paths)

- /home/user/crypto-autoresearcher/ledger/proposals/IDEA-20260926-201e86.yaml
- /home/user/crypto-autoresearcher/ledger/proposals/IDEA-20260926-20ba8f.yaml
- /home/user/crypto-autoresearcher/ledger/proposals/IDEA-20260926-3c6a19.yaml
- /home/user/crypto-autoresearcher/ledger/proposals/IDEA-20260926-3cc0b8.yaml
- /home/user/crypto-autoresearcher/analysis/binstd-idea-review-20260926/reviews/TASK-20260926-35e1b7-generator-report.md

YAML parse disclosure: no interpreter was available to this lane. Every
multi-line value is a `>-` block scalar; quoted strings containing
apostrophes use doubled single quotes; list items containing `: ` are
single-quoted. The dispatcher's `python3 -c "import yaml;
yaml.safe_load(open(path))"` is the check.
