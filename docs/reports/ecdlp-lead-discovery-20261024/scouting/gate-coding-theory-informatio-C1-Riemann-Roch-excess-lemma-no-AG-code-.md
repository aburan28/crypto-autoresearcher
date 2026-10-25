# Novelty gate N1-N4: C1 Riemann-Roch excess lemma (no AG-code decoder or ISD algorithm is a point-decomposition oracle)

Field: coding theory: information-set decoding, structured/quasi-cyclic decoding, list decoding and Guruswami-Sudan/Wu root finding, AG codes and Riemann-Roch spaces as implicit factor bases.
Gate date: 2026-10-24. Writer: gate subagent. Nothing inside the repositories was edited, created, added or committed; all files are under `/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/scout/`.

## 0. VERDICT

**duplicate_of_lead** at corpus level, with an atlas-level gap. The lead anchor is INFERRED, not recorded: the nearest registering lead is `LEAD-EXO-ideas-corpus-algebraic-transforms` (open_blocked), reached through IDEA-012 / P1539 (the lead's evidence cites P1553 artifacts of IDEA-012, not P1539, and its next_action covers only the 15 active registry rows). The decoder rejections (IDEA-013/014/130/336, PREID T05/T06/T10) are NOT cited by any lead row (grep of `knowledge/leads/ecdlp`: 0 hits), so the coding-theory decoder family is an unmapped atlas gap and the candidate's sentence "No lead covers this family" is literally true at atlas level and false at corpus level. The coordinator decides which lead receives the records.

One-paragraph reason. The four mandated `--match` runs (and three more of mine) return no lead whose text mentions codes, decoding or Riemann-Roch evaluation, so the candidate's statement "no lead covers this family" is true of the matcher output and false of the program. The same object and the same conclusion are already recorded in four places the matcher does not index: (a) `ledger/FINDING-PF-IC-001.md` entries ECFG-P1539-P0 (line 1628) and ECFG-P1539-R1 (line 1675), the Abel-Jacobi evaluation-minor gate, which states the identical dictionary (m points sum to R iff the m evaluation rows on a basis of H^0(O((m-1)O+R)) form a singular minor, i.e. a weight-m dual word of the target evaluation code), prices the locator gate (a sub-B^1.25 nonlinear zero-minor locator), and screens "standard AG-code / MinRank solver"; (b) `ideas/rejected/` records ECDLP-IDEA-013, -014 (elliptic-code error-locator descent), -130 (folded AG list recovery), -132, -136, -210, -226, -268, -336 (Guruswami-Sudan source list decoder) and the PREID duplicates T05 (Berlekamp-Welch), T06 (Prange information-set), T10 (ordered statistics), all merged/rejected on the diagnosis "a decoder consumes a supplied received word, syndrome or support; constructing it is the decomposition oracle"; (c) `ideas/proposed/ECDLP-CROSSOVER-EC-CODE-SYNDROME.md`, which carries the same dictionary at m = 3, 4 over L(4O) and the same exhaustive zero-disagreement toy check (35,960 four-point subsets, 36 singular, 0 disagreements); (d) the zero-minor thread H-HZM-001 / KN-FIND-3d6f78 / `LEAD-EXO-cryptoscale-candidate-screen`. The dictionary itself is Cheng's (retrieved, section 2.2). What the candidate adds, and the only thing I could not find in those records, is a quantitative agreement-versus-radius statement for interpolation list decoders run on the zero word (L2), a pricing of ISD as a direct low-weight dual-word locator (L3), and the information-free-support remark (L1). That is a proof upgrade of a closure the program already holds at the "missing source oracle" level, not a new mechanism and not a next step for an open lead. Recommended handling: do not file the candidate's new lead `LEAD-ICP-ag-code-decoding-oracle` with its novelty framing. Attach the rejected-decoder records (list in section 1.3) plus L2 as evidence and forecloses phrases to a lead chosen by the coordinator (nearest by inference: LEAD-EXO-ideas-corpus-algebraic-transforms), after the corrections in section 6. Precise delta: one formulation the records do not treat (L2, Guruswami-Sudan run on the zero word of the target evaluation code, no planted error), with a negative result conditional on the recalled GS bound, gain 0; L3 re-derives controls P1539-R1 already charged.

Provenance of tools used: WebFetch and WebSearch were available. Cheng (arXiv cs/0507026) Theorems 1-2 were read in the retrieved PDF text (provenance: retrieved). Canto Torres-Sendrier and Cheng-Wan were confirmed from search-result abstracts only (retrieved, abstract level). Guruswami-Sudan 1999 and the Trans. IT 2008 venue of Cheng are recalled.


## 1. N1 Atlas collision

Environment: `LEAD_ATLAS_CRYPTO`, `LEAD_ATLAS_CRYPTANALYSIS`, `LEAD_ATLAS_ECC_CHALLENGES` exported as specified; run from `/Volumes/SSD990-2/crypto-autoresearcher`. Raw outputs below are verbatim (files `c1_gate_raw/final_atlas_{1..4}.txt`; a second identical run confirmed the matcher is deterministic).

### 1.1.1 `python3 tools/lead_atlas.py --match "elliptic AG code minimum-weight dual codeword as point-decomposition oracle via Guruswami-Sudan list decoding or information set decoding"`

```
    8  LEAD-ICE-generic-oracle-arity-cost-floor     closed_obstructed  Generic (enumerative / MITM / free) decomposition oracles cannot reach rho at any arity
    6  LEAD-ICE-gpu-rootfind-oracle                 open_blocked       CUDA root-finding 2-decomposition oracle (embarrassingly parallel target x factor-base cells)
    6  LEAD-ICE-rootfind-pairtable-oracle           open_blocked       Root-finding / pair-table decomposition oracle in place of a Groebner solve
    5  LEAD-EXO-augmented-oracle-ggm                closed_obstructed  Augmented oracles (x-, y-, full-point, halving, endomorphism-image, incidence) and GGM simulability
    4  KR-RHO-38be82                                known_result       Tag tracing and table-driven step shortcuts
    4  LEAD-EXO-invertible-hint-subset              open_next_step     The invertible half: dense, cheaply recognizable AND cheaply invertible subsets of E(F_p)
    4  LEAD-ICB-prime-degree-algebraic-decomposition open_blocked       Bounded-degree algebraic decomposition (Weil-descended S_{m+1} on subspace bases) at prime extension degree: ECC2K-130, NIST K/B, sect571
    4  LEAD-ICE-sat-xor-pdp-oracle                  open_next_step     SAT / native-XOR (CryptoMiniSat, WDSat) point-decomposition oracle with honest pricing
```

### 1.1.2 `python3 tools/lead_atlas.py --match "use error-correcting-code decoders to find factor-base points that add up to the target point"`

```
    8  LEAD-ICE-gpu-rootfind-oracle                 open_blocked       CUDA root-finding 2-decomposition oracle (embarrassingly parallel target x factor-base cells)
    7  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
    7  KR-IC-955fd6                                 known_result       Symmetries and torsion speed up point decomposition
    7  LEAD-ICB-frobenius-search-symmetry           closed_obstructed  Frobenius as a symmetry of the decomposition search: orbit CNF encodings, conjugate attempts, equivariant elimination
    6  KR-IC-5765d2                                 known_result       SAT and XOR reasoning for point decomposition
    6  KR-RHO-6239aa                                known_result       Parallel collision search with distinguished points
    6  KR-RHO-6654ba                                known_result       Point halving as a rho step on binary curves
    6  LEAD-ICB-generic-table-oracle                closed_obstructed  Generic decomposition oracles for Koblitz IC: pair tables, compact-orbit 4-sum, MITM and enumeration, cap-locus arity, known-log pools
```

### 1.1.3 `python3 tools/lead_atlas.py --match "non-generic decomposition test sub-linear in the factor base from algebraic decoding of the Riemann-Roch evaluation code instead of enumeration or table lookup"`

```
   22  LEAD-ICB-kic-golden-base-exact-decomp        open_next_step     Co-designed binary factor bases with exact decomposition: affine 2-flats, orbit-canonical abscissa lookup, SAT vs exact MITM (KIC lane)
   18  LEAD-ICB-generic-table-oracle                closed_obstructed  Generic decomposition oracles for Koblitz IC: pair tables, compact-orbit 4-sum, MITM and enumeration, cap-locus arity, known-log pools
   16  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients of the factor base
   16  LEAD-ICP-coppersmith-smallroot-semaev        open_next_step     Small-root (Coppersmith / Jochemsz-May) decomposition with lattice-describable (window, AP, GAP) factor bases
   14  LEAD-ICP-algebraic-membership-factor-base    closed_obstructed  Factor bases with low-degree algebraic membership over F_p (subgroup, coset, Dickson, j=0 orbit, images of low-degree maps, character-constant sets)
   14  LEAD-ICP-retained-setup-online               closed_dominated   Retained-setup online IC (compact orbit n61, dense K1798 root table n83, orbit-folded m = 2) as a per-target win
   12  KR-IC-b0fcda                                 known_result       Frobenius-invariant factor bases for subfield (Koblitz) curves
   12  LEAD-ICB-composite-degree-c2pnb              open_next_step     Composite-degree ANSI X9.62 binary curves (c2pnb176/208/272/304/368): Gaudry-Diem n = 4 with a pi_16 orbit base
```

### 1.1.4 `python3 tools/lead_atlas.py --match "Riemann-Roch space implicit factor base Hamming weight list decoding information set decoding subset sum elliptic curve"`

```
   15  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
   13  KR-IC-73db3f                                 known_result       Choosing the factor-base vector space V (small product spaces)
   12  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
   12  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients of the factor base
   12  LEAD-ICB-nonlinear-frob-stable-bases         open_next_step     Non-subspace Frobenius-stable factor bases at prime n: trace-spectrum, Hamming ball, multiplicative subgroup, tau-adic, algebraic-group (Couveignes-Lercier) points
   11  LEAD-ICP-coppersmith-smallroot-semaev        open_next_step     Small-root (Coppersmith / Jochemsz-May) decomposition with lattice-describable (window, AP, GAP) factor bases
   10  LEAD-ICB-frobenius-orbit-factor-base         closed_obstructed  Frobenius/endomorphism-invariant factor bases and orbit columns on Koblitz and subfield curves, beyond the trivial orbit saving
   10  LEAD-ICB-kic-golden-base-exact-decomp        open_next_step     Co-designed binary factor bases with exact decomposition: affine 2-flats, orbit-canonical abscissa lookup, SAT vs exact MITM (KIC lane)
```

Extra semantic runs added by me after finding the P1539 and zero-minor records (files `atlas_extra_p1539.txt`, `atlas_extra_hzm.txt`):

`--match "Abel-Jacobi evaluation minor: m points sum to R iff singular minor of Riemann-Roch evaluation matrix; standard AG-code decoder as zero-minor locator"`
```
    8  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
    6  KR-RHO-6239aa                                known_result       Parallel collision search with distinguished points
    6  LEAD-ICB-orbit-linear-algebra                exhausted_at_scale Linear algebra of the orbit-folded relation matrix (equivariant blocks, sparse filters, Wiedemann, CADO-style merge)
    5  KR-RHO-825bca                                known_result       Practical rho cost on standard curves
    4  KR-RHO-46c2c6                                known_result       Multi-target and batch discrete logarithms
    4  LEAD-EXO-cryptoscale-candidate-screen        exhausted_at_scale GOAL-CRYPTO-001 discovery screen for a reproducible non-generic crypto-size algorithm
    4  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
    4  LEAD-ICP-char0-lifting-xedni-smoothness      closed_known       Lifting to characteristic zero - classical xedni, prescribed rational lifts (Cheon 2-isogeny form) and smoothness of integer lifts of x
```

`--match "hyperplane signature zero minor Riemann-Roch evaluation matrix relation locator"`
```
   12  LEAD-ICB-orbit-linear-algebra                exhausted_at_scale Linear algebra of the orbit-folded relation matrix (equivariant blocks, sparse filters, Wiedemann, CADO-style merge)
    7  LEAD-TRF-global-lift-small-height            closed_known       Global lifts to E(Q) or E(K) with small canonical height (xedni, SNFS / cyclotomic / Solinas number fields, rational 2-torsion lifts)
    6  LEAD-EXO-cryptoscale-candidate-screen        exhausted_at_scale GOAL-CRYPTO-001 discovery screen for a reproducible non-generic crypto-size algorithm
    6  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
    6  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engineering of the prime-field IC pipeline (native arithmetic, batching, pair-table build, generator, LA filter, planner)
    6  LEAD-ICP-xedni-function-field-sections       closed_obstructed  Function-field xedni - Mordell-Weil sections of elliptic surfaces over F_p(t) as a relation source
    5  KR-IC-cd159a                                 known_result       Xedni calculus and lifting to characteristic zero fail
    5  LEAD-ICE-syzygy-cascade-signatures           open_next_step     Exploiting the degree-born non-rewritable syzygy (F5 signature) cascade of Semaev systems
```

Note: even the tailored phrasing never ranks `LEAD-EXO-ideas-corpus-algebraic-transforms`, which is where the P1539 thread lives; it only surfaces `LEAD-EXO-cryptoscale-candidate-screen` (the H-HZM-001 thread). A lexical miss proves nothing.

### 1.2 Reading of the top hits (lead YAMLs opened; mechanism, obstruction, forecloses)

Top-5 per run: run1 = generic-oracle-arity-cost-floor, gpu-rootfind-oracle, rootfind-pairtable-oracle, EXO-augmented-oracle-ggm, KR-RHO-38be82 (a KR row, section 2). run2 = gpu-rootfind-oracle, KR-IC-5a43e5, KR-IC-955fd6, ICB-frobenius-search-symmetry, KR-IC-5765d2. run3 = ICB-kic-golden-base-exact-decomp, ICB-generic-table-oracle, ICB-cofactor-torsion-quotients, ICP-coppersmith-smallroot-semaev, ICP-algebraic-membership-factor-base. run4 = EXO-dl-character-sum-pseudorandom, KR-IC-73db3f, KR-IC-5a43e5, ICB-cofactor-torsion-quotients, ICB-nonlinear-frob-stable-bases.

#### LEAD-ICE-generic-oracle-arity-cost-floor  (closed_obstructed)  `knowledge/leads/ecdlp/ic-engine/LEAD-ICE-generic-oracle-arity-cost-floor.yaml`
- mechanism: Treat the oracle as an abstract m-SUM search or charge it nothing, and ask whether any arity m or base size puts point-decomposition IC below rho. The product law relations x targets x oracle = m 2^n is independent of dim V, and the store any sub-rho cell needs costs as much as rho's whole walk.
- obstruction.statement: "For oracles of class ENUM, MITM and MITM_CAPPED on binary curves of prime degree n, the replicated v2 cost model has zero in-domain sub-rho cells (EV-SEMBIN-b6d042); on ECC2K-130 a free oracle at m = 3 still costs 2^68.58 against rho's 2^60.81 (KN-FIND-aa2efc); in-model, structured generic-group bounds (CHW 2026/384) and non-adaptive time-space bounds (DKM 2025/783) give the same wall. Scope: oracles that do not read curve coordinates algebraically; the FREE control does have sub-VOW cells, so the obstruction is the oracle class, not IC."
- obstruction.revisit_when: "An oracle that reads coordinates with per-query cost polynomial in n at fixed degree (see LEAD-ICE-descent-closure-degree-at-scale) is measured, or a non-generic yield exceeds C(B+m-1,m)/N on average."
- forecloses: ['free decomposition oracle lifts IC below rho', 'arity threshold for point-decomposition index calculus', 'generic m-SUM decomposition oracle', 'larger arity m makes enumeration IC beat rho', 'multi-target amortisation rescues exhaustive-solver IC']

#### LEAD-ICE-rootfind-pairtable-oracle  (open_blocked)  `knowledge/leads/ecdlp/ic-engine/LEAD-ICE-rootfind-pairtable-oracle.yaml`
- mechanism: The S_3 root in the last variable is x(R -/+ F_i), so an m = 2 decomposition is one batched inversion plus table probes (prime) or one pair-sum lookup (binary); m = 3 is |F| lookups. It is exact and complete like enumeration and replaces Macaulay row reduction. It is now the default oracle in every Table A/B row, and it moves the constant, never the p/|F| exponent.
- next_action.step: Price every native primitive of the rootfind-negfold m = 2 arm and of matched strong rho (table canonicalisation, inversions) at 0, 0.1 and 1 GAE/op, replay on a second host (L2+), and re-run the 17-bit Koblitz and 20-bit prime cold sessions.
- next_action.discriminates: If the cold complete IC / strong-rho ratio stays above 1 across the band, the pair-table engine is exhausted at toy scale and only a degree-bounded algebraic oracle (LEAD-ICE-descent-closure- degree-at-scale) can change the slope; if it falls below 1 across the band at two sizes, it is the first validated sub-rho cold row and goes to the IC leaderboard gate.
- forecloses: ['replace Groebner with root finding in point decomposition', 'pair-sum table meet-in-the-middle decomposition oracle', 'x(R minus F_i) direct subtraction relation sweep', 'batched inversion root-finding oracle beats rho', 'all-roots univariate solver for Semaev S_3']

#### LEAD-ICE-gpu-rootfind-oracle  (open_blocked)  `knowledge/leads/ecdlp/ic-engine/LEAD-ICE-gpu-rootfind-oracle.yaml`
- mechanism: Each (target, F_i) cell is two slopes, one squaring and two probes, with one Montgomery-batched inversion per target, so the oracle maps onto a GPU at an estimated 5e10-1e11 cells/s. It can only lower the relation-phase constant (68-95% of Table B S); a matched comparison needs rho on the same GPU, which already has a measured Blackwell kernel.
- next_action.step: Execute `./bench throughput` and the fail-closed validation harness of gpu/rootfind on a real sm_120 (or sm_89) device, then run one ecbench cold session with IC relation phase on GPU against same-GPU rho at matched targets.
- next_action.discriminates: Measured cells/s confirm or falsify the 300-1000x host-emulation estimate; the matched GPU-IC / GPU-rho S ratio says whether the constant gain survives once rho gets the same device.
- forecloses: ['GPU root finding for point decomposition', 'CUDA kernel for Semaev decomposition oracle', 'Blackwell sm_120 relation collection', 'GPU index calculus relation sieve']

#### LEAD-EXO-augmented-oracle-ggm  (closed_obstructed)  `knowledge/leads/ecdlp/exotic/LEAD-EXO-augmented-oracle-ggm.yaml`
- mechanism: Give the solver an extra public oracle (x-coordinate, y-coordinate, full point, halving query, endomorphism image, factor-base incidence, jet) and hope it supplies sub-birthday information or guided decomposition.
- obstruction.statement: "Each named oracle is GGM-simulable (jet, endomorphism O(1); incidence O(m); halving equivalent to x; net O(log N)), so the Shoup lower bound closes its candidate family at exponent 1/2 (KN-FIND-002, KN-FIND-b7e091, KN-FIND-194294; EV-GGM-001 strong). Measured: the x-oracle gives Y_A = Y_B exactly (no yield advantage, EV-ECDLP-fd61e4 strong) and the m=3 MITM split saving is attributable to the split, not the oracle (EV-ECDLP-7367e2). Scope: oracles, not resources (see IDEA-20260808-ea3b4f)."
- obstruction.revisit_when: "A publicly computable oracle that is NOT GGM-simulable is exhibited (the threshold oracle is the minimal non-simulable identifier, KN-FIND-982fdf, but needs private data)."
- forecloses: ['x-coordinate oracle meet in the middle', 'y-coordinate oracle guided decomposition', 'full-point oracle', 'endomorphism image oracle', 'halving query oracle', 'generic group model simulable oracle']

#### LEAD-ICB-frobenius-search-symmetry  (closed_obstructed)  `knowledge/leads/ecdlp/ic-binary/LEAD-ICB-frobenius-search-symmetry.yaml`
- mechanism: Use x -> x^2 (or tau) as a symmetry inside one decomposition search: symmetry-breaking clauses, orbit-quotient encodings, treating the n conjugates of a target as one attempt, or Faugere-Svartz character blocks in F4, to divide per-attempt cost by up to n.
- obstruction.statement: "The absolute Frobenius is an equivariance between conjugate target instances, not a per-instance search symmetry (H-BINSTD-74b002 supported, replicated); fixed-target tau-orbit CNF clauses are unsound (H-BINSTD-c3d68f, replicated); sound orbit encodings cost >= 0.95x the plain single-instance search at n = 17, 23, 31; on a non-stable V the n conjugates of a target are n attempts over n conjugate bases (Proposition T); the k conjugates of a relation are one row in the orbit basis. Equivariant elimination is a constant only: 44-73x against a naive kernel is 2-3x against gf2_elim; whole-oracle 5.1x/15.5x at n = 11/13, of which fall-row augmentation alone gives 11.6x, and it does not apply to the production pipeline systems (regresses 0.29-0.59x there)."
- obstruction.revisit_when: "A genuine stabilizer of a single target R in the descended system (not a conjugation), or an equivariant elimination that applies to the production compact-orbit pipeline."
- forecloses: ['Frobenius symmetry breaking in the SAT encoding', 'treat the n Frobenius conjugates of a target as one attempt', 'equivariant F4 makes Koblitz decomposition sub-rho', 'orbit-quotient CNF for Koblitz point decomposition']

#### LEAD-ICB-kic-golden-base-exact-decomp  (open_next_step)  `knowledge/leads/ecdlp/ic-binary/LEAD-ICB-kic-golden-base-exact-decomp.yaml`
- mechanism: Design the factor base and the decomposition constraint together (affine-plane pools, one-hot shift encodings, orbit-canonical pair lookup with exact witness transport) so that charged decomposition cost drops without losing coverage.
- next_action.step: Coordinator evidence review of the five completed KIC runs (EXP-KIC-3df18c, -424885, -7bcef8, -c3c732, -d9c828), none of which has an EV record; then, for any arm whose advantage survives its null and A/A, a paired test inside the compact-orbit pipeline.
- next_action.discriminates: A reviewed wall or coverage advantage that survives the null is a candidate constant improvement for the IC baseline; none closes the lane as dominated by exact MITM.
- forecloses: ['golden factor base with easy SAT decomposition', 'affine 2-flat factor base', 'orbit-canonical abscissa pair lookup']

#### LEAD-ICB-generic-table-oracle  (closed_obstructed)  `knowledge/leads/ecdlp/ic-binary/LEAD-ICB-generic-table-oracle.yaml`
- mechanism: Decide whether a target is an m-sum of factor-base points by table lookup, pair tables or meet-in-the-middle, collect relations, solve the orbit-folded matrix and descend. This is the production pipeline behind every Table A and Table C row; engineering it (K, arity, table layout) is how the baseline has improved.
- obstruction.statement: "Every oracle built from group operations and membership tests makes IC a generic-group algorithm with advice: Shoup T >= sqrt(r/|Aut|) and Corrigan-Gibbs-Kogan S*T^2 >~ r/|Aut| apply, so with |Aut| = 2n no 4-, 5- or 6-sum table can beat sqrt(r/2n) in total work; the balanced generic-IC cost is ~ r^{2/3}/n^{4/3} against rho r^{1/2}. Measured: rungs sit 2^25-2^27 above the generic line; ln(IC/rho) grows 0.165 [0.117, 0.213] per ln r. Target-dependent and walk-carried bases are known-log pools (H-BINSTD-1447cf). At ECC2K-130 this route needs K* ~ 4e11 columns and ~8e9 core-years. Scope: all binary and Koblitz curves, one target, setup charged."
- obstruction.revisit_when: "An oracle that is not generic (algebraic restriction on the unknowns with membership degree far below |F|), which is LEAD-ICB-prime-degree-algebraic-decomposition; constant-factor engineering of this pipeline remains valid baseline work (LEAD-ICB-koblitz-setup-phase-cost)."
- forecloses: ['bigger pair table or k-sum table for ECC2K-130', '5-sum or 6-sum compact-orbit extraction beats rho', 'meet-in-the-middle point decomposition as a sub-rho oracle', 'walk-carried or target-dependent factor base', 'arity lever at the cap locus for ECC2K-130']

#### LEAD-ICB-cofactor-torsion-quotients  (closed_obstructed)  `knowledge/leads/ecdlp/ic-binary/LEAD-ICB-cofactor-torsion-quotients.yaml`
- mechanism: Use E -> E/2E -> E/4E coset labels on legs, homomorphic cofactor quotients or sum-compatible filters (Wagner k-tree) to prune decomposition candidates, or fold the factor base by 2-torsion translation.
- obstruction.statement: "On ECC2K-130 gcd(4, l) = 1, so every full-translation homomorphic cofactor quotient reduces to the order-l projection rho already uses (Sylow coprimality); exactly sum-compatible filters on E(F_{2^131}) carry 2 bits (the cofactor), so Wagner k-tree has no quotient to work in; the corrected iota-stable classification (V_d = b^{1/4} F_{2^d}) empties the (subspace base, 2-torsion quotient) cell on every prime-degree standardized curve; the production 2-torsion census adds 0 relations. FGHR 2-torsion symmetrisation of the solve is a separate constant (engine family)."
- obstruction.revisit_when: "A curve with a large smooth cofactor, or a non-homomorphic sum-compatible filter with more than log2(cofactor) bits."
- forecloses: ['Wagner k-tree on ECC2K-130', 'cofactor 4 coset label prunes decomposition', '2-torsion translation quotient of a subspace factor base', 'spend the cofactor on decomposition']

#### LEAD-ICP-coppersmith-smallroot-semaev  (open_next_step)  `knowledge/leads/ecdlp/ic-prime/LEAD-ICP-coppersmith-smallroot-semaev.yaml`
- mechanism: A small-x or windowed factor base turns decomposition into a multivariate small-root problem for S_{m+1}, whose cost is set by lattice reach rather than solving degree. With binary addition trees and kept windowed internal nodes, all-S_3 degree-2 blocks have the largest reach; if reach exceeded the index-calculus demand the decomposition would cost polynomial time per attempt at a factor base large enough to beat rho.
- next_action.step: Compute the provably optimal shift set (Ryan, EUROCRYPT 2025; Feng-Luo-Chen-Nitaj-Pan sumset bounds) for the 13-monomial S_3 polytope and the full-tree (m, w) = (4, 2) system, and the rank-r >= 2 GAP substitution of H-PFDR-3c7d1e, with tools/smallroot_reach.py as the calibrated calculator; then a planted direct-box S_4/S_5 recovery (H-PFDR-621852) at 40-56 bits only if the computed reach clears 8/9.
- next_action.discriminates: Optimal reach >= 0.8889 at (4,2) (or any rank-r GAP cell with positive margin) reopens a concrete lattice decomposition oracle to be measured; optimal reach < 0.8889 everywhere turns the current heuristic -0.0481 closure into a strategy-independent one and closes the family.
- forecloses: ['Coppersmith small roots of summation polynomials', 'small-x factor base solved by LLL', 'windowed addition tree with lattice reduction', 'symmetric e1 e2 lattice for S_3', 'rank-r generalized arithmetic progression factor base', 'lattice-assisted meet-in-the-middle decomposition']

#### LEAD-ICP-algebraic-membership-factor-base  (closed_obstructed)  `knowledge/leads/ecdlp/ic-prime/LEAD-ICP-algebraic-membership-factor-base.yaml`
- mechanism: Over F_{q^n} the subfield makes membership x^q = x low degree after Weil restriction. Over F_p one would need a size-B subset cut out by equations of degree << B that survive substitution into S_{m+1} (multiplicative subgroups x^B = 1, cosets, Dickson images, x = g(t)), or a structured base whose multiplicative characters bias x(P +/- Q) and so raise yield.
- obstruction.statement: "A target-independent algebraic locus of degree d yields O(d) usable points, so a size-B algebraic base has description degree >= B/3 and membership polynomial prod(x - v) of degree B (bounded-degree factor-base theorem, IDEA-20260801-021); mean per-target yield is binomial(B+m-1, m)/N for every base of size B (KN-FIND-007 conservation; coverage gain <= 1.582, constant in N). Measured: subgroup, small_x and random bases within 7 % at 32 bits; exact mean-yield ratio 1.000000 for six geometries at N ~ 2^14..2^18 (EV-FBG-001); msolve on subgroup bases grows deg^{4.4} at m = 3. Scope: prime-order E/F_p, any base of size B."
- obstruction.revisit_when: "KN-OPEN-020 is answered positively (a size-B set with sub-B-degree membership surviving substitution), or a base raises coverage or variance with an excess that grows with N."
- forecloses: ['multiplicative subgroup factor base x^B = 1', 'Dickson or coset factor base for prime-field index calculus', 'algebraic factor base with low-degree membership polynomial', 'character sums bias decompositions over a coset base', 'image of a low-degree map as factor base']

#### LEAD-EXO-dl-character-sum-pseudorandom  (exhausted_at_scale)  `knowledge/leads/ecdlp/exotic/LEAD-EXO-dl-character-sum-pseudorandom.yaml`
- mechanism: If max_k |sum_{P in F} e(2 pi i k DL(P)/N)| over the small-x set F were well above sqrt(B), the factor base would have super-random additive yield; by the Betti-yield duality (KN-FIND-9d2f56) exactly this is what a sub-rho combinatorial IC needs.
- obstruction.statement: "Measured the character-sum constant against a matched random null at 2^20-2^26 (EV-ECDLP-f83a17): R = C_EC/C_null is flat at about 1.28-1.34, i.e. the curve behaves like a random set up to a constant; all six standard analytic proof routes are closed (KN-FIND-e7a3b1), so neither a proof nor a measured bias exists. EXP7 Fourier flatness (8-14 bit) found no candidate predicate."
- obstruction.revisit_when: "R trends upward with p beyond 2^30 on the same matched null, or a structured set other than small-x shows R growing with N."
- forecloses: ['discrete log character sum on small-x factor base', 'H-PSEUDO bias', 'Fourier bias of x-coordinate sets in log order', 'super-random additive yield factor base', 'exponential sum cancellation for the elliptic log']

#### LEAD-ICB-nonlinear-frob-stable-bases  (open_next_step)  `knowledge/leads/ecdlp/ic-binary/LEAD-ICB-nonlinear-frob-stable-bases.yaml`
- mechanism: Prime n with 2 primitive leaves no Frobenius-stable F_2-subspace of useful dimension, but non-linear stable sets exist: V_E = {x : Tr(x^e) = 0, e in E}, Hamming balls in a normal basis, multiplicative subgroups x^d = 1, tau-adic patterns over an orbit-union base, and F_2-rational points of low-dimensional algebraic groups or Jacobians. If one keeps the n-fold orbit gain with a membership system no costlier than a subspace, it restores the Koblitz lever at n = 131.
- next_action.step: Run the approved matched-|F| per-attempt cost comparison: trace-spectrum V_E (H-CERTBIN-5a81ca) and normal-basis Hamming ball B_w (H-CERTBIN-ec0945) against a random subspace on RC-1 (n = 17) and a Koblitz n = 19 cell, in D <= 5 closure work and WDSat conflicts with a size-matched null; in parallel finish the dimension-5/6 Weil-polynomial census over F_2 for 131 | #A (H-FROB-ff99bf hit an impediment at dims 5-6; H-BINSTD-944a66 has preliminary support) and read the Couveignes-Lercier primary source.
- next_action.discriminates: Per-attempt cost within [0.5, 2] of the subspace arm keeps the n-fold gain at prime n and justifies an n = 131 price; cost above 2x means the stable structure is paid back in membership cost and the non-linear stable lane closes. A census with no dimension-5/6 abelian variety having 131 | #A closes the Couveignes-Lercier route at g <= 6.
- forecloses: ['Hamming-ball factor base in a normal basis for ECC2K-130', 'trace-spectrum or trace-conditioned Frobenius-stable base at prime degree', 'Couveignes-Lercier elliptic periods or algebraic-group factor base at n = 131', 'multiplicative-subgroup x^d = 1 factor base on Koblitz curves', 'tau-adic factor base over an orbit union']

Reading, per hit (is it the same mechanism?):
- generic-oracle-arity-cost-floor, ICB-generic-table-oracle, rootfind-pairtable, gpu-rootfind, kic-golden-base: enumeration, MITM, pair-table, SAT or free oracles. Not the same mechanism. Their scopes ("oracles that do not read curve coordinates algebraically"; "Every oracle built from group operations and membership tests") do not reach a decoder, which is the gap the candidate names, and I agree the gap exists at lead level.
- EXO-augmented-oracle-ggm: extra public oracles are GGM-simulable. A decoder is not an added oracle. Not the same.
- coppersmith-smallroot-semaev: lattice small-root search is the number-field analogue of list decoding (agreement threshold ~ sqrt), with a lattice-describable (window, AP, GAP) base. Different object (roots of S_{m+1} over Z, base must be lattice-describable), same family resemblance: reach threshold versus demand. Not the same mechanism; useful as the calibration for how the program closed a "decoding-radius" style route (reach 0.8408 vs demand 8/9, margin -0.0481).
- algebraic-membership-factor-base (SO-ALGFB), nonlinear-frob-stable-bases, dl-character-sum, cofactor-torsion-quotients, frobenius-search-symmetry: factor-base shape or filter leads. Not the same mechanism.
- None of the twelve mentions codes, decoding, Riemann-Roch evaluation, dual words or minors.

### 1.3 Semantic collision outside the matcher (the decisive finding)

The lead row that registers these records is `LEAD-EXO-ideas-corpus-algebraic-transforms` (open_blocked; its evidence lists `ideas/artifacts/ECDLP-IDEA-012/...`, and P1539 is the IDEA-012 gate):

#### LEAD-EXO-ideas-corpus-algebraic-transforms  (open_blocked)  `knowledge/leads/ecdlp/exotic/LEAD-EXO-ideas-corpus-algebraic-transforms.yaml`
- mechanism: The ideas/ECDLP-IDEA-* corpus (about 436 generated ideas: spinor-matchgate addition transform, block-Krylov transition intersection, Cremona-shrunk toric decomposition, aggregate complement-divisor compression, x-only nonfaithful signed lifts, conormal-polar blowups, ramification-break digits, and many more) proposes representation changes whose payoff depends on an explicit constructor or theorem not yet supplied.
- next_action.step: For each of the 15 active registry rows, supply the named constructor or theorem the deferred/independent audits ask for, then run its zero-compute contract preflight; start with IDEA-012 (finite-deck weighted endpoint, REVISE_SCOPED_REDUCTION) whose missing pieces are listed.
- next_action.discriminates: A constructor that passes its preflight becomes its own lead with an experiment; a theorem-level no-go moves the idea to rejected with a cited obstruction.
- forecloses: ['spinor matchgate addition transform', 'Cremona toric decomposition', 'block Krylov transition intersection', 'aggregate complement divisor compression', 'ramification break scalar digits', 'x-only nonfaithful signed lift']

#### LEAD-EXO-cryptoscale-candidate-screen  (exhausted_at_scale)  `knowledge/leads/ecdlp/exotic/LEAD-EXO-cryptoscale-candidate-screen.yaml`
- mechanism: Screen literature and representation families (compact target-label common factors, defect-scaled hyperplane-signature zero-minor routes, corner-coefficient induction, KN-OPEN gates) through Gate A/B admission for any candidate that could beat rho on cryptographic prime-field ECDLP.
- obstruction.statement: "Thirteen screening batches returned FINAL_NO_CANDIDATE / NO_ADMISSIBLE_NEXT_MECHANISM over the checked source set (EV-CRYPTO-010..013); the hyperplane-signature zero-minor route is not sub-rho under its own pinned model at d=1 (KN-FIND-3d6f78, EV-CRYPTO-ad7fa2 replicated). Scale reached: the recorded source set, zero-compute admission sheets; no crypto-size run."
- obstruction.revisit_when: "An externally sourced candidate with an explicit constructor arrives, or the screen's own sensitivity audit (IDEA-20260805-9430e9) shows it could not have admitted a known positive."
- forecloses: ['crypto-size non-generic ECDLP candidate screen', 'hyperplane signature zero-minor route', 'compact target-label common factor', 'corner-coefficient induction']

Atlas-gap check: `grep -rn -E "IDEA-336|IDEA-130|IDEA-014|IDEA-013|IDEA-210|source.decoder|ideas/rejected|ideas/proposed|CROSSOVER-EC-CODE" knowledge/leads/ecdlp` returned nothing; the lead above cites `ideas/artifacts/ECDLP-IDEA-012/p1553_*`, not p1539. The anchor to this lead is therefore by inference through IDEA-012.

Same-mechanism records (read by me; paths exact):

| record | what it already says | relation to C1 |
|---|---|---|
| `ledger/FINDING-PF-IC-001.md` ECFG-P1539-P0 (line 1628), ECFG-P1539-R1 (line 1675) | For L_R = O_E((m-1)O+R), h^0 = m; distinct points sum to R iff their m evaluation rows on a public basis form a singular square minor; confluent jets for repeats; semantic control "standard AG-code decoding consumes a received word or syndrome; P1539 instead seeks an unknown weight-five dual word in a target-dependent evaluation code"; gate: a nonlinear sub-B^1.25 zero-minor locator; independent audit adds the translation theorem (target bundle = translate of the fixed degree-m bundle by T = [m^{-1}]R, so no second target geometry or witness oracle); disposition INDEPENDENTLY_VERIFIED_EXACT_EVALUATION_INTERFACE ... NONHOMOMORPHIC_LOCATOR_UNSUPPLIED ... INCONCLUSIVE; scope limit "arbitrary list-specific nonlinear finite-field locators remain outside the proved negatives" | Same dictionary (C1's mechanism paragraph), same locator formulation, same open slot. C1's L2/L3 target exactly that open slot for two named locator families. |
| `ideas/artifacts/ECDLP-IDEA-012/p1539_abel_jacobi_evaluation_minor_gate.md` section 8 "Evaluation-code interpretation and its limit"; section 13 route table; `p1539_r1_independent_audit.md` section 10 "Code, MinRank, and algebraic solver screen" | Evaluation code of length Theta(B), dimension m; weight-m dual word; "Supplying the syndrome, locator, or support is the decomposition oracle"; "A qualifying code algorithm must therefore be a direct low-weight dual-word locator ... not a decoder replay on planted errors"; table row "Standard AG-code error locator: consumes a syndrome/error word" | Same conclusion for standard decoders, argued by input type instead of by radius. |
| `ideas/rejected/ECDLP-IDEA-014_elliptic_code_error_locator_descent_hypothesis.md` | Elliptic-code error-locator descent (Pellikaan locator, Guruswami-Sudan named as the list-decoding boundary); README: "merged/rejected: same support-matrix family plus uncharged residual-list cost" | Decoder-as-oracle, rejected. |
| `ideas/rejected/ECDLP-IDEA-336_guruswami_sudan_source_list_decoder_hypothesis.md` | GS interpolation and factorisation as source decoder; "a list decoder assumes evaluations correlated with an existing codeword. Constructing source-indexed evaluations from the endpoint is the missing source oracle" | The candidate's phrase 'list decoding of elliptic codes for point decomposition', rejected. |
| `ideas/rejected/ECDLP-IDEA-130_folded_ag_list_recovery_source_decoder_hypothesis.md`, `-132`, `-136`, `-210`, `-226`, `-268`, `-013`; `ideas/rejected/preallocation/20260724-a_T05_berlekamp_welch..., T06_prange_information_set_source_decoder_preid_duplicate.md, T10_fossorier_lin...` | Folded AG list recovery, HDX/sheaf, Schur filtration of AG codes, polar SC, multiplicity codes, secant syzygy, Berlekamp-Welch, Prange information sets, ordered statistics: all merged/rejected as "supplied word / syndrome / local view is the missing oracle" | Covers the candidate's forecloses phrases 'information set decoding for elliptic subset sum', 'folded or Parvaresh-Vardy elliptic codes', 'Riemann-Roch implicit factor base'. |
| `ideas/proposed/ECDLP-CROSSOVER-EC-CODE-SYNDROME.md` | Dictionary over L(4O): four points sum to O iff the four evaluation columns are dependent; sparse-syndrome form V_B z = -v(-R), wt(z) = 3 for a 3-point decomposition; toy E/F_1009: 35,960 four-point subsets, 36 singular, zero disagreements with EC addition | Same dictionary and the same kind of zero-mismatch toy check as the candidate's 29,120-subset check. |
| `ledger/hypotheses/H-HZM-001.yaml`, KN-FIND-3d6f78, IDEA-20260723-002 | Zero-minor of the Riemann-Roch evaluation matrix as relation locator (Mahalanobis-Mallick-Abdullah, Abdullah-Mahalanobis, as cited in the program record); explicit signature enumeration closed at d = 1: charged work >= N/(L+1); interpretation_limits: closes only that interface, "not all nonlinear zero-minor locators" | Same object, explicit-enumeration locator closed; the decoder locator class is what H-HZM-001 left open. |

Closest-record checks of the other kind (the program's atlas rows that C1 relies on): SO-TABLE, SO-GEN, SO-ALGFB, SO-COVER, quoted in section 5.

## 2. N2 Known results

### 2.1 `python3 tools/build_frontier_map.py --match` (verbatim)

`--match "elliptic AG code minimum-weight dual codeword as point-decomposition oracle via Guruswami-Sudan list decoding or information set decoding"`
```
KR-RHO-38be82  score=4  [known_mechanism/reported]  Tag tracing and table-driven step shortcuts
    sources: KN-LIT-93696f, KN-LIT-20ef89
```

`--match "use error-correcting-code decoders to find factor-base points that add up to the target point"`
```
KR-IC-5a43e5  score=7  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-955fd6  score=7  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
KR-IC-5765d2  score=6  [known_mechanism/measured]  SAT and XOR reasoning for point decomposition
    sources: KN-LIT-92b022, KN-LIT-102cdb, KN-LIT-6e036d
KR-RHO-6239aa  score=6  [known_mechanism/proven]  Parallel collision search with distinguished points
    sources: KN-LIT-73f7e1, KN-LIT-012, KN-TECH-006
KR-RHO-6654ba  score=6  [known_mechanism/reported]  Point halving as a rho step on binary curves
    sources: KN-LIT-359dcc
KR-IC-73db3f  score=4  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
KR-RHO-46c2c6  score=4  [known_bound/proven]  Multi-target and batch discrete logarithms
    sources: KN-LIT-f47b10, KN-LIT-7e25f1
KR-RHO-ea34b8  score=4  [known_bound/proven]  Precomputation: l^{1/3} online after l^{2/3} tables, and the lower bound
    sources: KN-LIT-7cc07f, KN-LIT-013, KN-LIT-7e2964
```

`--match "non-generic decomposition test sub-linear in the factor base from algebraic decoding of the Riemann-Roch evaluation code instead of enumeration or table lookup"`
```
KR-IC-b0fcda  score=12  [known_mechanism/heuristic]  Frobenius-invariant factor bases for subfield (Koblitz) curves
    sources: KN-LIT-0d9d28
KR-IC-5931ee  score=11  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-5a43e5  score=11  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-73db3f  score=9  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
KR-IC-8b9daa  score=7  [known_mechanism/reported]  Point decomposition via symmetric formulations (Karabina)
    sources: KN-LIT-327949
KR-IC-46d822  score=6  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-IC-49c882  score=6  [known_bound/conjectured]  Quasi-subfield polynomials
    sources: KN-LIT-0a321c, KN-LIT-4fe9d2
KR-RHO-cd0049  score=6  [known_bound/measured]  Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
    sources: KN-FIND-4e12fa
```

`--match "Riemann-Roch space implicit factor base Hamming weight list decoding information set decoding subset sum elliptic curve"`
```
KR-IC-73db3f  score=13  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
KR-IC-5a43e5  score=12  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-b0fcda  score=9  [known_mechanism/heuristic]  Frobenius-invariant factor bases for subfield (Koblitz) curves
    sources: KN-LIT-0d9d28
KR-IC-5931ee  score=7  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-49c882  score=6  [known_bound/conjectured]  Quasi-subfield polynomials
    sources: KN-LIT-0a321c, KN-LIT-4fe9d2
KR-RHO-0528e7  score=5  [known_mechanism/proven]  Automorphisms give a sqrt(m) constant factor
    sources: KN-LIT-db2a90, KN-LIT-042, KN-LIT-a5c59c, KN-TECH-018
KR-IC-5ea2f8  score=4  [known_mechanism/proven]  GHS Weil descent and cover attacks
    sources: KN-LIT-007, KN-LIT-fa389d, KN-LIT-bf1772, KN-LIT-b4a89c, KN-LIT-54c462
KR-IC-791cb7  score=4  [known_mechanism/heuristic]  Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    sources: KN-LIT-d7995a, KN-LIT-f64d86, KN-LIT-fc822d, KN-LIT-0e854b, KN-LIT-007
```

Extra: `--match "Riemann-Roch evaluation matrix zero minor elliptic normal curve hyperplane section decomposition"`
```
KR-IC-955fd6  score=8  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
KR-IC-cd159a  score=8  [known_negative/proven]  Xedni calculus and lifting to characteristic zero fail
    sources: KN-LIT-020, KN-LIT-021
KR-IC-46d822  score=6  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-IC-8b9daa  score=6  [known_mechanism/reported]  Point decomposition via symmetric formulations (Karabina)
    sources: KN-LIT-327949
KR-IC-081a58  score=5  [known_bound/heuristic]  Joux–Vitse n−1 decomposition and oracle-assisted static DH
    sources: KN-LIT-673219, KN-LIT-022, KN-LIT-41fe5c
KR-IC-5765d2  score=5  [known_mechanism/measured]  SAT and XOR reasoning for point decomposition
    sources: KN-LIT-92b022, KN-LIT-102cdb, KN-LIT-6e036d
KR-IC-1fcdbc  score=4  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-5ea2f8  score=4  [known_mechanism/proven]  GHS Weil descent and cover attacks
    sources: KN-LIT-007, KN-LIT-fa389d, KN-LIT-bf1772, KN-LIT-b4a89c, KN-LIT-54c462
```

Reading: no KR row concerns codes, decoding, Riemann-Roch evaluation or minors. The hits are Semaev summation polynomials (KR-IC-5a43e5: "novelty must lie in representation, factor base, elimination or solver"), symmetries and torsion (KR-IC-955fd6), SAT/XOR (KR-IC-5765d2), factor-base space choice (KR-IC-73db3f), naive prime-field Semaev (KR-IC-5931ee, closed_known), tag tracing (KR-RHO-38be82), distinguished points (KR-RHO-6239aa). So the matcher gives no known_result hit. KR-IC-5931ee is the nearest closed known row (B2) and is not about decoders.

### 2.2 External literature (this is where the candidate's ingredients are already known)
- Cheng, Hard problems of algebraic geometry codes, arXiv cs/0507026. Provenance: **retrieved** (PDF text extracted locally, `c1_gate_raw/cheng_pdf_untrusted/cheng.txt`; read Theorem 1 with proof, Theorem 2 with proof, introduction and conclusion). Content verified: Theorem 1 builds the code from L(Q+(k-1)O) evaluated at the points a_i G and proves, inside its proof, that a weight n-k codeword exists iff k of the points sum to Q, giving minimum distance n-k (yes) or n-k+1 (no). This is the candidate's dictionary, with the same genus-1 equality "k zeros = k poles". Theorem 2 states that a 2^{cn}(log q)^{O(1)} minimum-distance algorithm for linear codes [n,k]_q would solve ECDLP in time q^c; its proof uses the code L(R+(n/2-1)O) at the known-log points 2^i P with n about log p, and recovers the support D by deleting one position at a time. So the identity "min-distance algorithm = decomposition oracle" is in Cheng, but only for length-log q codes over a known-log base, not for a factor base of size B = p^{1/m}. The paper also records that its reductions use the subset-sum problem directly so preprocessing-subset-sum results carry over (relevant to SO-TABLE), and that known AG decoders are insensitive to alphabet size. Journal venue (IEEE Trans. IT 54(1), 2008): recalled.
- Cheng-Wan, On the list and bounded distance decodability of Reed-Solomon codes (arXiv math/0405082). Provenance: **retrieved** (search-result abstract). Decoding at radius n - g^(n,k,q) or beyond would make DLP in a finite field easy; for distances between n - sqrt(nk) and that radius, list or bounded-distance decodability is unknown and generally believed not to hold. This concerns Reed-Solomon codes (genus 0) and finite-field DLP, so for elliptic codes I use it only as an ANALOGY: it suggests the regime of C1's L2 (agreement between k and sqrt(nk)) is open and believed hard rather than closed, and that an unconditional "no AG-code decoder" title cannot be proved cheaply. Cheng's own Theorem 1/2 are the elliptic-code statements. The candidate's scope (interpolation-based decoders) is the part that can be proved.
- Canto Torres-Sendrier, PQCrypto 2016, LNCS 9606:144-161. Provenance: **retrieved** (HAL/DBLP abstract via search): for sub-linear weight w every analysed ISD variant has cost 2^{c w (1+o(1))} with c depending only on the rate, equal to Prange's. This is a statement about generic (random) codes, which is what H-C1.1 needs and what makes the ISD half conditional.
- Guruswami-Sudan, IEEE Trans. IT 45(6):1757-1767 (1999). Provenance: **recalled** (the program's own IDEA-014/336 records cite the same paper; I did not open it). Agreement threshold sqrt(n(k+g-1)) is textbook and I take it as recalled.
- Mahalanobis-Mallick-Abdullah (INDOCRYPT 2018, ePrint 2018/134; arXiv 1703.07544), Abdullah-Mahalanobis (arXiv 2310.04132), Mahalanobis (arXiv 2607.09814). Provenance: **retrieved** for existence and the zero-minor framing (search results); the Riemann-Roch evaluation-matrix content is taken from the program's H-HZM-001 record, not from the papers.
- Searches for index calculus point decomposition via AG-code list decoding returned only index-calculus papers and nothing on the coding side (no published use of GS or ISD as a decomposition oracle found). Absence of a hit is not a novelty proof.

N2 outcome: no KR hit; the dictionary (Cheng, retrieved) and the min-distance/decomposition equivalence (Cheng Thm 2) are known literature; the radius-versus-agreement observation is an immediate application of a recalled textbook bound in a regime the literature itself labels open.

## 3. N3 Ledger

Tool: grep over `/Volumes/SSD990-2/crypto-autoresearcher/ledger/.index/{proposals,hypotheses}.jsonl` through `c1_gate_raw/ledger_c1.py` (substring match on the whole index line). Terms and counts (proposals / hypotheses):

| term | hits | term | hits |
|---|---|---|---|
| algebraic geometry code, ag code, evaluation code, elliptic code, normal curve, elliptic normal, guruswami, sudan, shokrollahi, deep hole, minimum distance, error-correcting | 0 / 0 | reed-solomon | 2 / 0 (both non-ECDLP: low-degree test; HQC decoder) |
| list decod | 1 / 0 (IDEA-20260820-b87428, 'conversion-fibre syndrome list recovery', not opened, title is not an ECDLP decomposition) | information set / information-set | 5+2 / 1+3 (all HQC/McEliece/SDitH ISD pricing, non-ECDLP) |
| riemann-roch | 1 / 2 | hyperplane | 3 / 4 |
| zero-minor / zero minor / hzm | 1 / 1 | evaluation matrix | 0 / 1 |
| codeword, linear code, decoder, decoding, goppa, mceliece, lee-brickell (0 / 1) | many; the ones I inspected by title are PQC code-based or SHA-1 linear-code records, none ECDLP decomposition (not every hit opened) | subset-sum | 8 / 2 |
| k-sum, m-sum, generalized birthday | 3,3,1 / 0,2,1 | prange | 11 / 4 (PQC) |

Hits that may be the same object (id, status, first 100 chars of claim; from the index):

| id | status | claim (100 chars) |
|---|---|---|
| IDEA-20260723-002 | known | A published defect-scaled hyperplane-signature zero-minor search is a mechanism-distinct academic EC |
| IDEA-20260723-003 | unverified | After excluding the failed compact z_R constructor and the inconclusive hyperplane-signature cost cl |
| IDEA-20260808-24c61b | proposed | Write k in base B with m = log_B N digits, so Q = sum_j [d_j B^{j-1}] P with d_j in [0,B). ECDLP is  |
| IDEA-20260817-1e0111 | proposed | (A) THE COUNTEREXAMPLE TO UNIVERSALITY, WHICH IS THE RECORD'S MAIN CONTRIBUTION AND IS UNAFFECTED BY |
| IDEA-20260906-aa6da3 | proposed | REPRESENTATION CLASS R2 (curve models and embeddings: level-n theta and Riemann-Roch models). ATTACK |
| IDEA-20260920-a5757d | proposed | (A) THE REBUTTAL. docs/n13-ecdlp-hint-family.md section 8 Route 3 argues: "Wagner's k-tree attains 2 |
| IDEA-20260922-845a77 | proposed | Search heuristic 3 (agents/idea-generator.md) asks, for any bottleneck search, whether the target sp |
| IDEA-20260930-4b7d1e | proposed | (A) Under vOW's random-function behaviour, generic m-SUM on E(F_(2^n)) per target admits time about  |
| IDEA-20260930-750de2 | proposed | SETTING. Generic group G of prime order n with generator P; target Q = [x]P with x in W(m, w) = {0 < |
| IDEA-20261018-49fdf7 | proposed | Every recorded pair-table, k-sum and 6-sum design at ECC2K-130 and every n=85,89 rung is a non-adapt |
| H-ECDLP-bac70e | specified | On E_p:y^2=x^3+x+1 for p in {5,7,11,17}, split rational effective degree-four sum-zero divisors shou |
| H-HZM-001 | rejected | The published defect-scaled hyperplane-signature zero-minor ECDLP route survives the GOAL-CRYPTO-001 |
| H-PFDR-673eed | proposed | THE REPRESENTATION TECHNIQUE FAILS FOR ECDLP AT THE FILTER AND NOT AT THE COUNTING, AND THAT LOCALIS |
| H-SCR-001 | approved | Applying the frozen post-z_R / post-hyperplane admission sheet mechanically to the frozen corpus sna |

Full ledger records opened (three, as allowed): `ledger/proposals/IDEA-20260723-002.yaml`, `ledger/hypotheses/H-HZM-001.yaml`, `ledger/proposals/IDEA-20260906-aa6da3.yaml`. Disclosure: I also read a FOURTH ledger file, `ledger/FINDING-PF-IC-001.md`, by targeted line ranges only (grep hits, lines 1620-1728 and 1873-1912; not the whole 2,776-line file), because a third record cited it; the decision rests on those ranges. Decisions: IDEA-20260723-002 and H-HZM-001 are the zero-minor / Riemann-Roch evaluation-matrix route (published prior art, closed at d = 1 under its own formulas; limits explicitly leave "all nonlinear zero-minor locators" open). IDEA-20260906-aa6da3 closes the R2 level-N Riemann-Roch linearisation as the pairing transfer F4 and records that "The Riemann-Roch presentation of point decomposition (L_R = O_E((m-1)O+R), h^0 = m) is already in the corpus (ledger/FINDING-PF-IC-001.md line 1636)". No index record proposes an AG-code decoder or ISD as an ECDLP decomposition oracle; those proposals live in `ideas/` (section 1.3), which the ledger index does not cover.

Additional files read to settle the decision (non-ledger, disclosed for transparency): `ideas/artifacts/ECDLP-IDEA-012/p1539_*` (grep-targeted passages), `ideas/rejected/ECDLP-IDEA-014`, `-336`, `-013` (head), `.../preallocation/..._T06_...`, `ideas/proposed/ECDLP-CROSSOVER-EC-CODE-SYNDROME.md`, `knowledge/findings/KN-FIND-3d6f78.md`, `knowledge/open-problems/KN-OPEN-020.md`.

Is any of it the same object? Yes: ECFG-P1539, IDEA-014/336/130/T06 and CROSSOVER-EC-CODE-SYNDROME are the same object (decoding the target evaluation code of the Riemann-Roch bundle as the decomposition locator). I grepped those files for radius, sqrt(n, Johnson, agreement-versus-threshold and Prange exponents: none carries an agreement-versus-radius calculation or an ISD exponent for the thin code; IDEA-014 has only "the correctable radius can be constant while relation collection needs a growing base". That is the residual delta, section 6.

## 4. N4 Notation change (representation / operation-set pair)

Pair as stated by the candidate: representation = the point as a column of the Riemann-Roch evaluation matrix, i.e. a point of the degree-m elliptic normal curve in P^{m-1} (class R2, curve embedding; attack stage relation decomposition / factor-base membership); operation set = hyperplane sections in the class G_R = R+(m-1)O, i.e. relations; translation by factor-base elements only. Trichotomy class: partial-action, Class I (same as index calculus).

Is this a recorded rigidity result in new notation? Yes, in three ways.
1. Lossy-projection test (object-frame section 3): the column map P -> (f_1(P),...,f_m(P)) on a basis of L(G_R) is injective on E(F_p) (P1539-R1: "in short Weierstrass coordinates the fixed basis {1,x,y,x^2,xy} is point-injective"; the candidate's harness, re-run by me, uses L((m+1)O) and agrees on all tested subsets). The projection discards nothing, so it is a change of coordinates, "not returned" under IDEA-20260806-c5d183 (a deterministic full-translation-compatible map is constant or injective; injective is the rigid end) and KN-FIND-ffe1df Theorem C (injective case).
2. The target-dependence is a translation: P1539-R1's translation theorem (T = [m^{-1}]R, O_E((m-1)O+R) ~ translate of O_E(mO) by T, so each target row is projectively the fixed degree-m row at A - T). I did not re-derive the sign convention; with it, C_R is the fixed code L(mO) on the shifted base F - T and "target-dependent evaluation code" adds no second geometry. In the IDEA-20260906-aa6da3 notation this is the R2 class already closed ("every theta-type or level-N model ... is F4 in new notation"; small levels give only the injective object [n]P) and the degree-d-function-on-E paradigm closed at model lever 1 (KN-OPEN-003 as cited in object-frame section 1).
3. Class I with Sigma = relations by factor-base translation is exactly the recorded index-calculus placement (IDEA-20260806-c5d183, IDEA-20260901-863e36). C1 asks for nothing outside it.

Where the candidate sits relative to KN-OPEN-020: its membership description is implicit and target-dependent, i.e. inside the open class the object-frame document names (high-degree, implicit-membership, target-dependent). KN-OPEN-020's "Required next result" asks for a lower bound for the implicit membership/source solver; C1's L2/L3, if correct, would be a partial instance of that for the decoder sub-class. This is the one place where the candidate has a stake in a recorded open problem, and it is why I recommend keeping the proof as evidence rather than discarding it.

## 5. Standing obstructions: quoted rows and whether C1 escapes them

**SO-TABLE: LEAD-ICP-generic-table-decomposition** (closed_obstructed)
> obstruction.statement: Any decomposition oracle that enumerates or table-looks-up factor-base elements is a generic time/memory trade-off and obeys S*T^2 >~ N (Corrigan-Gibbs--Kogan) and T >~ sqrt(N) (Shoup); with linear algebra included the two-term model gives m = 2 >= 3 (pT_dec)^{2/3} and m = 3 only ties rho even with T_dec = O(1). Measured on generated prime-order E/F_p, 12-32 bits: exhaustive IC exponent 0.99 (m = 2) and 1.01 (m = 3), mitm 0.67 / 0.75 / 0.60 at m = 3/4/5 (4/7 at m = 7) against rho 0.50 [0.48, 0.52]; Table B gap to matched rho widens from 5.47x at log2 r = 11.9 to 13.5x at 23.4. Scope: any generic (enumeration/table) decomposition over F_p.

**SO-GEN: LEAD-RHO-generic-sqrt-lower-bound** (closed_obstructed)
> obstruction.statement: Shoup/Nechaev generic-group lower bound: any generic algorithm needs Omega(sqrt r) group operations for a prime-order-r group (KR-RHO-13bf67). Every lead in this family moves only the constant (automorphism classes divide it by sqrt|Aut|, KR-RHO-0528e7). Scope: all generic algorithms, any field, any r.

**SO-ALGFB: LEAD-ICP-algebraic-membership-factor-base** (closed_obstructed)
> obstruction.statement: A target-independent algebraic locus of degree d yields O(d) usable points, so a size-B algebraic base has description degree >= B/3 and membership polynomial prod(x - v) of degree B (bounded-degree factor-base theorem, IDEA-20260801-021); mean per-target yield is binomial(B+m-1, m)/N for every base of size B (KN-FIND-007 conservation; coverage gain <= 1.582, constant in N). Measured: subgroup, small_x and random bases within 7 % at 32 bits; exact mean-yield ratio 1.000000 for six geometries at N ~ 2^14..2^18 (EV-FBG-001); msolve on subgroup bases grows deg^{4.4} at m = 3. Scope: prime-order E/F_p, any base of size B.

**SO-COVER: LEAD-TRF-same-field-genus-g-embedding** (closed_obstructed)
> obstruction.statement: Tate multiplicativity gives #Jac(C)(F_p) = N * #A(F_p) with #A = Theta(N^{g-1}); genus-g index calculus costs O~(q^{2-2/g}) >= q for g >= 2, at least a full exponent above rho's N^{1/2}; quadric-pencil and quartic models of E itself are isomorphic models with the same group. Scope: prime-field source curves, any same-field cover (DEC-20260902-4c82fd).

**binary neighbour: LEAD-ICE-generic-oracle-arity-cost-floor** (closed_obstructed)
> obstruction.statement: For oracles of class ENUM, MITM and MITM_CAPPED on binary curves of prime degree n, the replicated v2 cost model has zero in-domain sub-rho cells (EV-SEMBIN-b6d042); on ECC2K-130 a free oracle at m = 3 still costs 2^68.58 against rho's 2^60.81 (KN-FIND-aa2efc); in-model, structured generic-group bounds (CHW 2026/384) and non-adaptive time-space bounds (DKM 2025/783) give the same wall. Scope: oracles that do not read curve coordinates algebraically; the FREE control does have sub-VOW cells, so the obstruction is the oracle class, not IC.

**subset-sum / ISD collision neighbour: LEAD-ICP-representation-subset-sum** (closed_obstructed)
> obstruction.statement: The method uses only group operations and equality of encodings, so it is a generic algorithm and is bounded below by T >~ sqrt(N) (Shoup) and S*T^2 >~ N with advice; the filter step has no non-generic handle on E(F_p) (KR-RHO-5b1c0a records the same failure over F_{p^2}). Scope: any representation/filter variant on a prime-order group.

**Wagner / Stern collision neighbour: LEAD-EXO-four-list-ktree-join** (open_next_step)
> (open lead, no obstruction row) mechanism: Run a Wagner-style k-list tree (or representation-technique subset-sum) on E(F_p) using a cheap filter h with h(P+Q)=f(h(P),h(Q)) often enough, or an output-sensitive partial verifier, aiming at N^(1/3+o(1)) end-to-end. Signed-y and Boolean-success cascades are the program's concrete instances.  next_action: Measure the relative bucket variance W of the O2 agreement kernel (H-ECDLP-2ade73; IDEA-20260904-f7d47d second moment) on the covered families across N and fit its decay against 1/sqrt(N); EXP-ECDLP-5cad48 ran many stages without ever assigning a W class.

Assessment against the candidate's escape premises (mine, not the candidate's):
- SO-TABLE ("enumerates or table-looks-up"): GS-type interpolation does not enumerate, so the premise is escaped there; the candidate's own L3 puts the ISD collision half back inside SO-TABLE (its only cheap evaluation is the group law = pair-table MITM). The recorded program rejections (IDEA-336, T06) reach the same place by a different route (supplied syndrome = the oracle). So "SO-TABLE alone does not close them, and C1 is the proof that does" is overstated: the closure is already on file at the input-type level.
- SO-GEN (all generic algorithms): decoders read coordinates, so not generic; escape is real but vacuous for a closure.
- SO-ALGFB ("target-independent algebraic locus of degree d", Scope "prime-order E/F_p, any base of size B"): the decoder description is implicit and needs no membership polynomial, so it sits in the open class of KN-OPEN-020; the candidate is right that SO-ALGFB does not cover it.
- SO-COVER: the candidate concedes it is not escaped (genus > 1 lands in O~(q^{2-2/g})). Agreed.
- The binary neighbour's scope ("oracles that do not read curve coordinates algebraically") does leave decoders out; that part of the candidate's lead-level gap claim is correct. The gap is closed at corpus level, not atlas level.

## 6. Review of the candidate's own claims (what I checked, what I did not)

Reproduced by me (provenance: produced this session): `python3 -I coding-isd/check_c1_dictionary.py` on E/F_2927 (a=153, b=352, N=2957), 0.91 s user. Output (verbatim in `c1_gate_raw/check_c1_rerun.txt`):
```
curve p=2927 a=153 b=352 N=2957
m=2: subsets=1820 decompositions=22 singular<=>decomposition agree=1820 mismatch=0; support>m rank-full 600/600
m=3: subsets=7280 decompositions=23 singular<=>decomposition agree=7280 mismatch=0; support>m rank-full 600/600
m=4: subsets=20020 decompositions=32 singular<=>decomposition agree=20020 mismatch=0; support>m rank-full 600/600
python3 -I coding-isd/check_c1_dictionary.py  0.91s user 0.05s system 52% cpu 1.829 total
```
Totals 1820+7280+20020 = 29,120 subsets, 22+23+32 = 77 true decompositions, 0 mismatches, 1800/1800 rank-full: the candidate's numbers reproduce exactly. What this harness tests: that m points plus -R are dependent in the evaluation space of L((m+1)O) iff they sum to the claimed value. That is the classical elliptic-normal-curve / hyperplane-section fact, a restatement of the group law; it is not evidence about any decoder. It checks the dictionary leg and the rank-full leg of L1; it does not test L2 or L3 at all (no decoder is run).

Not verified by me, stated as the candidate's conditional claims:
- A1 (L2): Guruswami-Sudan on genus-1 evaluation codes needs agreement t > sqrt(n(k+g-1)) = sqrt(nk); a nonzero function in L(G_R) has at most m zeros, so for n > m the guarantee is vacuous at agreement exactly m. This is an arithmetic consequence of a recalled bound. It shows the guarantee is vacuous, not that the algorithm cannot succeed on the planted codeword; the candidate says so ("if a decoder is found whose correctness does not rest on a zero count"). Cheng-Wan (retrieved) place this exact regime in the open-and-believed-hard gap, so the title "no AG-code decoder" must be read as "no interpolation-based decoder with a zero-count guarantee".
- A2 (L3, Prange dominated by the subtraction oracle by a factor about n): not re-derived by me. Plausible from n^m/m! subsets versus n^{m-1} subtraction.
- A3 (H-C1.1, no ISD variant beats a random code of the same size on C_R^perp): conditional on the Canto Torres-Sendrier random-code analysis plus L1; I did not test it.
- A4 (scope line "a general minimum-distance algorithm is excluded because by Cheng's Theorem 2 it would itself solve ECDLP"): Theorem 2 as retrieved requires a 2^{cn}(log q)^{O(1)} algorithm for codes of length n about log q over the known-log base 2^i P; it does not transfer verbatim to a factor base of size p^{1/m}. The exclusion is fine as a scope choice, the justification should be reworded.

Corrections the candidate needs before any filing: (i) delete "No lead covers this family"; cite FINDING-PF-IC-001 ECFG-P1539, ideas/artifacts/ECDLP-IDEA-012/p1539_*, ideas/rejected IDEA-013/014/130/336, PREID T05/T06/T10, proposed CROSSOVER-EC-CODE-SYNDROME, H-HZM-001 / KN-FIND-3d6f78; (ii) credit Cheng for Theorem 1 as the dictionary (the candidate does) and note that the program's P1539 gate already carries it; (iii) restate the title as a scoped statement; (iv) the toy check duplicates in kind the CROSSOVER-EC-CODE-SYNDROME zero-disagreement check; (v) "self_kill_risk" should be raised: the folklore is inside this repository.

What survives (the delta): L2 as an explicit agreement-versus-radius closure for interpolation list decoders on the zero word of the target evaluation code; L3 as the ISD pricing for the thin code, to be set beside P1539's 2+3 MITM and kSUM-indexing controls; L1 (dual words of support above m carry no group information; a dimension count). None of this reopens anything or moves an exponent (predicted gain 0, tier X).

Mapping of C1's lemmas onto the P1539 records (this decides the verdict): P1539 section 8 defines the qualifying object as "a direct low-weight dual-word locator for the structured target code, not a decoder replay on planted errors". ISD on C_R^perp IS such a locator, so the open slot of P1539 includes decoders of that kind and C1 is aimed at the right slot. (i) L3 (ISD): by C1's own text, Stern-type collisions reduce to the Plucker incidence join evaluated by the group law (= the pair-table MITM) and Prange is dominated by subtraction; that lands inside P1539-R1's already-charged rows (direct 2+3 MITM at B^2 state / B^3 query, kSUM-indexing at advice >= B^4, Wagner / neutral-mask quotient absent). So L3 is a re-derivation of controls the program already charged, conditional on C1's reduction, which I did not re-derive. (ii) L2 (GS on the zero word): neither P1539's "consumes a syndrome" row nor IDEA-336's "endpoint-derived received word" treats the formulation in which the received word is 0, the target enters through the code, and no planted error exists; this is the one untreated formulation, and its result is negative. (iii) L1 is a dimension count. If L3 had not landed in those charged rows the verdict would tilt to advances_lead; on C1's own L3 text it does land there. The P1539 gate itself (a sub-B^1.25 nonlinear locator beyond the charged controls) is untouched by C1.

Numbered heuristics used in this gate: H-G1 the matcher misses semantic neighbours that use different vocabulary (checked: confirmed twice); H-G2 a program-corpus rejection at "missing source oracle" level is a valid precedent for a duplicate verdict only if the candidate's formulation does not remove that obstacle; here the candidate's zero-word formulation does remove the syndrome obstacle but is the formulation P1539 already adopted; H-G3 the delta (A1-A3) is conditional on recalled GS and on the Canto Torres-Sendrier random-code model.
