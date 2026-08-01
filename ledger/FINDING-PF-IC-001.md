# FINDING-PF-IC-001 — Candidate quantitative negative result for prime-field index calculus

**Type:** negative result of record / candidate conditional lower bound. **NOT a break.**
**Status:** preliminary–replicated (toy scale, CI-backed on the key leg). Owner: coordinator.
**Consolidates:** EXP-REP-001, EXP-REP-002, EXP-ISO-001, EXP-FB-001 (this harness) +
the ecdlp-autolab R6 firmed result (`tier1_T1_R6_firm`, bootstrap-CI).

## Statement (candidate)

On a generic prime-field curve `E/F_p`, `ℓ ≈ p`, the membership-constrained Semaev
point-decomposition route to index calculus does **not** produce relations below the
Pollard-rho birthday bound. Concretely, over every tested variation the per-PDP cost model is

```
per-PDP solving degree   d_reg = 2            (floor for a nonlinear 0-dim system)
per-PDP solve cost       ~ d^gamma,  gamma in [4.57, 5.86] (90% CI, R6-firmed)
                         with d = |F| = ell^{1/m}  =>  ~ ell^{gamma/m}
relations needed         ~ |F| = ell^{1/m}
total IC cost            ~ ell^{(1+gamma)/m}  ; total exponent 2.05, 90% CI [1.86, 2.29]
                                                                (m=3, R6-firmed)
rho baseline             ell^{1/2}
```

The total-cost exponent's **entire** confidence interval `[1.86, 2.29]` lies far above rho's
`0.5`. The `d_reg = 2` floor is a genuine, non-degenerate solve (verified `dim=0`, correct
decomposition as a root) — it does not lower the cost, because the cost is dominated by the
`|F|`-size linear algebra over the membership-quotient ring, not by the solving degree.

## Invariances measured (each a matched-control scoped negative)

| Lever | Effect on (d_reg, cost) | Evidence |
|---|---|---|
| Curve **model** (Weierstrass Semaev vs twisted-Edwards native), m=2, m=3 | none — both `d_reg=2`; Edwards native is constant-factor *slower* | EXP-REP-001/002 |
| **Isogeny** class (2,3,5-isogeny neighbors, same order) | none — `d_reg` and decomposition yield track coefficient variance | EXP-ISO-001 |
| **Factor-base structure** (interval / arithmetic-progression vs random) | none — yield `~|F|^3/N`, solve `~d^6`, `d_reg=2`, all structure-invariant | EXP-FB-001 |
| **Arbitrary explicit membership** (the narrowed R6) | no-win signature: `d_reg=2`, solve `~d^gamma` (CI above rho) | R6-firmed |

## Why this is the expected structural outcome (informal)

A nonlinear 0-dimensional system has `d_reg ≥ 2`; the membership-constrained Semaev system
sits exactly at `d_reg = 2` (all solutions are the ≤`m!` decompositions, so the reduced GB is
low-degree). But the Macaulay matrix at degree 2 over the degree-`d` membership quotient has
size polynomial in `d = |F|`, so the per-PDP solve is `poly(|F|) ≥ |F|`, and with `|F|`
relations the total is `≥ |F|^2 = ℓ^{2/m}` — minimized at large `m`, but the Semaev
polynomial degree grows (doubly-exponentially in `m`), and prime fields admit **no natural
small factor base** to make `|F| ≪ √ℓ` cheaply. This is the standard reason IC fails over
prime fields (Gaudry/Diem require an extension-field subfield base), here re-derived with
matched-control measurements and a CI-backed cost exponent.

## Scope and honest limits (AGENTS rules 6–7)

- Toy scale (`p ≤ 2^16`, `m ≤ 3`, `d ≤ 24`). This is a *candidate* statement supported by
  toy-scale measurements + one CI-backed exponent; it is **not** a proof and **not** a
  crypto-scale certificate.
- It is a **negative** result (a lower-bound-shaped claim), the opposite of a breakthrough.
- It closes the tested experimental levers; it does not exclude an undiscovered mechanism,
  a different (non-IC) algorithm, or the two genuinely-open theoretical residuals
  (unconditional reverse black-box separation; d_reg growth of the *binary* Weil-descent
  core past the memory wall — a different field, not generic prime).

## Disposition

The generic prime-field ECDLP breakthrough sought this session was **not found**. The
accessible in-bar experimental levers are exhausted and uniformly negative. The genuine
research value delivered is (i) this candidate quantitative negative result and (ii) the
reproducible, matched-control experiment suite. Escalating any of these below-rho claims to
a positive break would require fabrication and is excluded (AGENTS rule 9).

## Versioned focused-harness extensions — 2026-07-17

These rows append later representation experiments without changing the historical
statement above. A scoped theorem or verifier pass is not a generic lower bound and is not
evidence of a better-than-rho ECDLP algorithm.

### ECFG-P1513-R1 — Shared common-norm standard-route screen

- Status: `REVISE_STANDARD_ROUTES_SCOPED_NEGATIVE_KU_REDUCTION_OPEN`.
- Exact positive control: one `B^2`-leaf symbolic bivariate circuit represents two
  degree-`B^3` norm families with exactly `B` planted common roots and complete source rows.
- Scoped negatives: specialization, explicit norms, dense fiber-product gcd, fixed-point
  truncated resultants, and the 2026 algebraic two-relation-matrix modular-composition route.
- Producer source/result/note SHA-256:
  `aaa1a730c58079f995d4b70532e827265a4bc7cf14559b145346f1a1b8891c17`,
  `972c13439fac0dd8e6f42bac6f008af981f6678da3bf32d77b10e896bab23cc9`,
  `83e5c70eeb80e180e27e190bf33a4ce080b7956408e79789d188d76f2748bef7`.
- Independent-audit source/result/note SHA-256:
  `d1d0e5bf73538ca2ecb3069413f7b1b0a6b051355b3003a719fe36900511d3b6`,
  `0fd8b697d565f6151cadd6987c358d7fb0f75858891ba4f5b2a44720ec62065f`,
  `f5de58633241f2e92bfff6d0595e135db2770b83a5487e9d9c90da2f4d267b8d`.
- Boundary: no direct KU-compatible reduction, relation collection, factor logs, blind
  descent, or Shoup-bound break.

### ECFG-P1513-V2 — IDEA-121 assignment and theorem-only successor

- Official mechanism ID: `ECDLP-IDEA-121`, state
  `deferred_ku_circuit_common_norm_reduction_required`.
- Hypothesis/dedup/assignment SHA-256:
  `d2dbef82ef8c9936f389df793b7476178012da07223eb97ac240d3e25bf7a085`,
  `f84b11ed371e02d46f1d4da82a2bd16c206887c9052aa213ca17737af839e46f`,
  `65b5a2db9c3271c30cba508bac3536cc4315dc1237e841ebddc7655ec71186fa`.
- Versioned contract SHA-256:
  `6587801eb08b190e49f398443398a6ea4a02f1dcb6058835ca27e0f30d2199b3`.
- Authority: `review_required`, `approved_by: null`, `maximum_runs: 0`; theorem evidence
  only, with no elliptic scaling dispatch.

### ECFG-P1513-R2 — Intrinsic-degree and generic-SLP screen

- Status:
  `REVISE_INTRINSIC_GEOMETRIC_AND_GENERIC_SLP_ROUTES_CLOSED_KU_REDUCTION_OPEN`.
- Exact degree boundary: every literal square three-equation subsystem of
  `T(U)=F(V)=H(U,W)=H(V,W)=0` has generic degree `B^4` or `B^5`, although the
  favorable final overdetermined cut has only `B` accepted points. Even substituting the
  final degree optimistically into the classical geometric-resolution matrix formula gives
  dimension `2B^3`, above rho `B^(5/2)`.
- Generic straight-line GCD/factor algorithms remain parameterized by the norm total degree
  `D=B^3` supplied in unary and do not construct source jets. This is a scoped solver-route
  negative, not an unconditional arithmetic-circuit lower bound.
- Derivation SHA-256:
  `bc7f9e44852ff6a7a7e59d52676154e82f3b43988b7824ce8a2fbb8c0cd260c6`.
- Producer source/result/note SHA-256:
  `e7ddb49e3cfd3d573a1c42340ad66f4d89b9f781a3c9399ce80dfd855360780f`,
  `62665fe08874d7596683dcdd55b1acc281ccb6a7a2d5eb8263d8b60d745fa74f`,
  `caeef44960be649d93b4632850fd5353d73edac4e582193ff7d591b9a03f4111`.
- Independent-audit source/result/note SHA-256:
  `f862b0e591d7f1c1eadaffcdae4890cc9bcd654973e5c7607412bb0885c8d8ec`,
  `fecfb205a852dc9d357ed92dc7fcc645b47fb95ba10ce94e33bd72af53d54ac7`,
  `df385cb479059909decccbc0e2cbf6a66f6ab49c37f4e6b160e6305a99f6ea38`.
- Sole surviving action: derive a direct circuit-preserving reduction to a bounded number of
  degree-`B^2` Kedlaya-Umans-compatible operations with multiplicities and complete source
  jets, or preserve another versioned scoped negative.

### ECFG-P1513-V4 — Stable-corpus replay repair

- Reason: the coordinator advanced IDEA-121's exactly-one-next-action after P1513 v2 froze
  the recovered hypothesis; v3 then captured a transient red-team-report hash while that
  report was still being written. Historical contracts and R2 receipts remain unchanged.
- Final IDEA-121 hypothesis SHA-256:
  `ede253da2f7e0effea67c0a535294dcd42e203d2cb6041b40f0f0c4cb238e2c6`.
- Final cohort dedup/red-team SHA-256:
  `95c9ef8bf2f520f726299ea4adf0e112bf94fa259098d24114725f709937f334`,
  `62a97a28f041a50063ebc38a45e9d4e231898d6fb77fb184efa1ccf0292ba992`.
- Historical v2, transient v3, and stable v4 contract SHA-256:
  `6587801eb08b190e49f398443398a6ea4a02f1dcb6058835ca27e0f30d2199b3`,
  `780f1c58fed230c1e7e6781a0081d7bfd8c9aca8063e20a83458a884e1a831ab`,
  `4fac5ac1f00bc6161858d31b62752206ec83919f6d6448e63052cabcf4555033`.
- Validator boundary: the final corpus passes structural validation across unique IDs
  `001`–`133`; IDEA-121 remains theorem-deferred and unapproved.

### ECFG-P1513-R2-V2 — Final-corpus deterministic replay

- Producer source/result/note SHA-256:
  `91a0829c82967f36361b325629802fa5afdccc283ca5eb93430e1b171cd0e8a4`,
  `818983c7d63d85b5d16df98e122a18ec7ff5194e6a641a88e3051e56c189b723`,
  `be50ef17d540fc5f816684ead538af707d645c710b3b44e8e1de1e61be247bc0`.
- Independent-audit source/result/note SHA-256:
  `cd0ab6bcc59f1ded817439ecb1f1defa5658f36b07a9aa635c6a435d760b37c2`,
  `d4a9386ace9542ff7d877d2a034db940ec75e02a20aaca3e48e1cb62dad45c5d`,
  `72de5382094735e417e44153558f7921998837982b4f3f0fc7c8ecff19f63346`.
- Replay result: producer `13/13`; independent audit `12/12`; mutations `8/8` rejected.
- Stable active queue/plan/report SHA-256:
  `2dcc2e1ba0fcfd2c2c4cc955bb8da1b57ff57f3ce108046e669d5d9d6e00c546`,
  `f230852d7f830d351c15d805c15e32e65c967e4db3f161395d6bf0b7061880c9`,
  `cd059f479a4e03702e3aec220c4a5b42031d54a0dda185dbffe4e0433c1d21e9`.
- Next artifact: `ideas/artifacts/ECDLP-IDEA-121/ku_circuit_reduction_v2.md`.

### ECFG-P1513-R3 — Direct-KU representation-dimension gate

- Status:
  `SCOPED_NEGATIVE_STANDARD_KU_EMBEDDINGS_NEW_CIRCUIT_OPERATION_OPEN`.
- Exact interface: `H(U,W)` has `B^2` constant-degree product leaves, each selector has
  degree `B`, each norm has degree `B^3`, the favorable common factor has degree `B`, and
  rho is `B^(5/2)`.
- Standard KU coefficient-ring route: a degree-`B^2` operation over
  `K[U]/(T)` has `B^2 * B = B^3` base-field coordinates. The finite-ring bit bound retains
  `log|K[U]/(T)|=Theta(B log p)`, so its fixed-epsilon exponent is
  `B^(3+2*epsilon+o(1))`.
- Equivalent scoped negatives: the query-triangular algebra `(T(U),C(W))` has dimension
  `B^3` at `deg(C)=B^2`; primitive/Kronecker flattening has product dimension `B^3`;
  dense multivariate KU omits the product-circuit conversion; and transposed power
  projection preserves cubic coordinate width and does not compute a nonlinear gcd.
- Conditional positive control: once the exact degree-`B` common factor `G` is already
  supplied, target/start marker decoding can live in dimension `B*deg(G)=B^2`. This is a
  decoder, not a locator.
- Derivation and v5 contract SHA-256:
  `6fcca1d12e911f6eb2142ac96b6d0a83b6ac20db11efd06bc24c0abb7c99dc48`,
  `1fa2f94af806bb2e0d1747c400819d67bcee28649ec352743bf8fc5e8f30424f`.
- Producer source/result/note SHA-256:
  `204a5bb07d87bab8df5c5c98ba7a054508f5c4c8d209f106ff48b801b6569912`,
  `71acdd7dcf58d86aa1237c2141727d697eb8cb435b1e4b60e192cc690a5e1d7b`,
  `38cf9d109ba7c934c5b2a4ac0f7b4dfa9d293eb41a130f2c226e2566aa4eee47`.
- Independent-audit source/result/note SHA-256:
  `794cf81401d091f309ef454bdd909a15c6a9d811bdd0c9b2f2bf64d63c60418b`,
  `dc27abf53decfcbee43dafdcac4283e1b557b7f5779817625c9ace3313fcec87`,
  `9c399e69ba6bc8a120f4d7e0819bc9bc1339d065c18dd5cbf4a659fa54bfbb79`.
- Replay result: producer `16/16` and audit `12/12`; both reject `8/8` accounting,
  circular-query, transposition, dense-input, and conditional-decoder mutations.
- Boundary: this is a format-and-dimension obstruction for standard KU representations,
  not an arithmetic-circuit lower bound. No relation collection, factor logs, blind
  descent, or generic below-rho ECDLP algorithm exists.

### ECFG-P1514-V1 — Target-local nonlinear apolar theorem pivot

- P1513 disposition: `inconclusive`, independently verified at its scoped route boundary.
  A future product-circuit common-factor locator requires a versioned mechanism-new
  hypothesis rather than another backend substitution.
- Selected successor: `P1514`, bound to theorem-deferred `ECDLP-IDEA-133`. Its claimed
  operation is a compact target-local nonlinear apolar functional built directly from
  recursive `S3` equations, with a flat Hankel extension and exact signed five-source
  multiplication-algebra inverse.
- Exactly one action: write
  `ideas/artifacts/ECDLP-IDEA-133/nonlinear_apolar_operation_theorem.md`, proving or
  refuting the constructor, source biconditional, independence from P1512/P1513, and
  complete `lambda,mu<=0.45` before code or toy runs.
- Stable P1514 queue/plan/report SHA-256:
  `6268cb9c66277cf6579f49ba67a40761e71a405600587c6eec25dd5fca1d07ce`,
  `c58e80ea22065910a10f6a2c28bdfee55f86e50d2d1bf66bc00207362c795da3`,
  `be3b9f88971266127c2741a62e0027e2f1f415329a912053c7b61b601e9742d9`.
- Boundary: supplied moments, flatness alone, multiplication spectra, valid toy tuples,
  scalar-linear atoms, and explicit or implicit P1513 norms are controls, not a
  breakthrough.

### ECFG-P1514-V2 — Append-only apolar receipt scope correction

- Disposition: both P1514 producer receipts are `REVISE`; `ECDLP-IDEA-133` remains
  theorem-deferred, unapproved, and outside the active registry. No ECDLP experiment or
  algorithm promotion occurred.
- Immutable v1 and intermediate-v2 receipt SHA-256:
  `4093e48132d96706db1155c44a8ab0f82de5ae997885df56b6ba1074022f297e`,
  `b97666d65119c90eb7c63ac9df3be650af1b1e42854f613d1b39dc1eb68c50b2`.
- Append-only independent scope correction and self-contained verifier-source SHA-256:
  `7cf48786840dc94f19a394c09f3e3c31ca2bfb9d6fa905e9c81d8fc6e0a0c8ab`,
  `935c83ec427d082e216a24c893c2c5341ac399490d41b6adb771793b0a6e99f3`.
- Corrected direct-route boundary: a reusable right deck charges `B^3` total
  precomputation/campaign time and `B^3` state; streaming charges `B^4=N^0.8` campaign
  time and can use `B^2` working memory. Direct five-tuple enumeration charges either
  `B^5` precomputation/state or `B^6` rescanned campaign time. Constant density,
  `Theta(B)` relation queries, constant fiber rank, and full rank growth are favorable
  heuristic/model-bound controls.
- Corrected Macaulay boundary: `k=5B-3` is a theorem-guaranteed sufficient cutoff, not a
  compulsory minimum. Only the frozen instantiation with `binomial(5B+2,5)=Theta(B^5)`
  coordinates is closed. Adaptive early stabilization, smaller fiber-specific cutoffs,
  sparse/multihomogeneous routes, and a structured nonlinear moment oracle remain open.
- Corrected nonreduced boundary: eigenvalues recover reduced support; exact multiplicity
  and scheme structure require a charged joint primary decomposition and nilpotent local
  algebra, or a proved equivalent recovering local lengths.
- Workspace incident: an earlier concurrent verifier revision contained hard-coded
  `/Volumes/Volume/autolab` inputs and outputs and was executed during independent audit,
  creating two external audit outputs. Those files were not read, edited, or removed by
  this closeout. The preserved in-repository verifier now rejects every path outside
  `/Volumes/Volume/crypto-autoresearcher` and writes nothing without `--write`.
- Exactly one action: after independent static review and a versioned coordinator
  approval, run `PYTHONDONTWRITEBYTECODE=1 python3 ideas/artifacts/ECDLP-IDEA-133/verify_nonlinear_apolar_theorem.py`
  without `--write`; require the scope-correction verdict before advancing P1514.
- Boundary: this is a scoped input, representation, and direct-enumeration cost screen,
  not a general lower bound, sub-rho ECDLP algorithm, or breakthrough.

### ECFG-P1514-R1-V4 — Corrected apolar moment-constructor scope screen

- Disposition: `inconclusive`; full IDEA-133 constructor `not_reproduced`.
- Durable status:
  `STANDARD_ENUMERATIVE_ROUTES_SCOPED_NEGATIVE__ADAPTIVE_AND_STRUCTURED_CONSTRUCTORS_OPEN`.
- Supplied flat moments and multi-index sequences are decoder inputs, not public-input
  constructors. A faithful single functional also requires `ann(Lambda_R)=I_R`; exact
  nonreduced recovery additionally needs joint primary decomposition and nilpotent local
  algebra or a charged equivalent.
- Corrected reusable two-plus-three route: `B^3` precomputation/state, `B^2` lookup per
  target, and `B^3=N^0.6` total campaign time/state across `B` targets. Corrected streamed
  route: `B^2=N^0.4` working memory, `B^3` work per target, and
  `B^4=N^0.8` campaign time. Direct source enumeration is either `B^5` precompute/state
  or `B^6` rescanned campaign work.
- The dense Macaulay count `binomial(5B+2,5)=Theta(B^5)` applies to the frozen
  theorem-guaranteed sufficient cutoff `5B-3`. That cutoff is not a compulsory minimum;
  adaptive early stabilization, smaller fiber-specific cutoffs, sparse or
  multihomogeneous Macaulay, structured five-sum algorithms, and new nonlinear moment
  constructors remain open.
- Original theorem, intermediate correction, and authoritative scope-note SHA-256:
  `4093e48132d96706db1155c44a8ab0f82de5ae997885df56b6ba1074022f297e`,
  `b97666d65119c90eb7c63ac9df3be650af1b1e42854f613d1b39dc1eb68c50b2`,
  and
  `7cf48786840dc94f19a394c09f3e3c31ca2bfb9d6fa905e9c81d8fc6e0a0c8ab`.
- Corrective producer source/result/note SHA-256:
  `b5aa6cfaa75e1e06fee972c95b0d3661a10c707712c3c194b5e13e7bfb05ff66`,
  `1aea3f2aa6972fb2302a177331ad0cdb89bad699bc756b2106c46ead5e1a5dce`,
  and
  `264c7ddc02628fed2dfd28c5534c1ec8939fc93234ed80585d789fcd2f920ba7`;
  checks/mutations `14/14` and `14/14`.
- Final independent verifier/result/note SHA-256:
  `8d17e1339c98d586a3d1bb67032ba30fe364b9b76d9171f6cb88bebcc0c9293b`,
  `821493806a4e65bc6ac2c21036eff3d38ba49d26f9526d0556d46635c931e82d`,
  and
  `933961a462efb1f90a7451128360e50066c56d729367bf96b550cae095bfe7bc`;
  checks/mutations `13/13` and `7/7`.
- Invalid static-check audit receipts are preserved at
  `9d5b535b88f743a9a48d7e49ed568d7886d880d45d592d1cda2dd7f0e944224f`
  and
  `9a81cab4a367998f30e029052867873f49d8d571ee6b2fb9a3060b45cad2cf03`;
  their arithmetic and mutation checks passed, but exact prose-token checks failed.
- Handoff SHA-256:
  `16edd92f80a515f645d29577cea951859c4a56b45c65cd4931cf3874f83e48c7`.
- Boundary: no elliptic experiment, relation collection, factor-log solve, blind descent,
  arithmetic-circuit lower bound, generic Shoup improvement, or breakthrough occurred.

### ECFG-P1514-V5 — Workspace-confined lifecycle repair

- Disposition: the R1-V4 formulas survive only as a static scoped correction. Every
  associated external execution is `invalid` current evidence; the live P1514 claim is
  `open`, not independently verified, and `ECDLP-IDEA-133` remains deferred behind its
  retired, `review_required`, zero-run contract.
- Current authoritative scope-note and canonical unrun verifier SHA-256:
  `d718a341153f1ea805c59fe1f45511712fda1805fbcc61103bbe9f1f4159866f`,
  `cafef7ab468f11d3c68d58ab3105c3c76ebc33a7ffcdd3ec519c6a6cdbc43ec4`.
- Rejected verifier-source SHA-256:
  `de07cdefea70091f193a0bb6b28e5dc38d0fc29fcf809295a0a30f29561b9ef9`
  (impossible immutable-receipt token) and
  `8d17e1339c98d586a3d1bb67032ba30fe364b9b76d9171f6cb88bebcc0c9293b`
  (loosened tokens and unauthorized external execution). The first overwritten
  external-path verifier revision is tombstoned at SHA-256
  `ae8c549ab5781acc98d99c73325ffa99da16cf8f65aab87fe6d5753bdfd0e25e`;
  its raw bytes were not retained before repair.
- The live focus queue records append-only corrections from `completed`/verified to
  `invalid`/unverified for the P1514 external runs, excludes their external outputs from
  current evidence, sets candidate `maximum_runs` to zero, and plans exactly one
  repository-confined verifier action. Pre-repair queue/plan/report snapshots remain
  preserved under `focus/archive/`.
- Exactly one action: after independent static review and a versioned coordinator
  approval, run `PYTHONDONTWRITEBYTECODE=1 python3 ideas/artifacts/ECDLP-IDEA-133/verify_nonlinear_apolar_theorem.py`
  without `--write`; a pass verifies only the scope correction and cannot promote the
  missing structured moment constructor.
- Boundary: no valid P1514 execution, relation campaign, factor-log solve, blind descent,
  general lower bound, sub-rho ECDLP result, or breakthrough is claimed.

### ECFG-P1515-V1 — Squarefree source-shelling theorem pivot

- Selected successor: `P1515`, bound to theorem-deferred `ECDLP-IDEA-098`.
- Mechanism-new operation: a target-independent flat degeneration of the labelled
  recursive-`S3` relation ideal to a squarefree Stanley-Reisner complex, followed by
  accepted-facet navigation and exact deformation lifting to signed sources.
- Semantic boundary: this is not P1514 moment/trace decoding. It survives only if a
  compressed facet grammar or target-uniform shelling skips the degree-preserving source
  deck without tuple-indexed annotations, dense Grobner/Macaulay construction, ambiguous
  lifts, or post-hoc source labels.
- Exactly one action: write
  `ideas/artifacts/ECDLP-IDEA-098/squarefree_source_gate.md`, proving either sub-rho
  accepted-facet navigation with an exact source lift or the scoped degree-preserving
  obstruction for every admitted source-biconditional shelling representation.
- Final P1515 queue/plan/report SHA-256:
  `0599f81ecc88196d7d4ea195962d95c35134b180e366e3ccf8816bd77b295626`,
  `7a09b4a8ca4402a55bc12998b54ddc5ed7301f8f9fb03d5c9b36b3d4350f4d82`,
  and
  `9b2e9e94f0beeff0a4829b4f4e2ccb148693191a643b0ee791940f7ff48a353c`.
- Boundary: squarefreeness, shellability, a short monomial-generator list, a valid lifted
  relation, or a toy scalar is not source compression or a breakthrough.

### ECFG-IDEA146-R1 — Faithful-addition WNU preservation gate

- Cohort context: the validated `146`–`157` semantic pass preserved IDEA-146 as a
  theorem-deferred conservative candidate. This receipt consumes its declared theorem
  action without dispatching the retired `review_required`, zero-run contract.
- Producer status:
  `SCOPED_NEGATIVE_FAITHFUL_GROUP_ADDITION_SIGNATURE_HAS_NO_PROPER_FACTOR_BASE_PRESERVING_WNU`;
  independent verification remains `false`, so the coordinator-controlled hypothesis
  state is unchanged.
- Algebraic result: preservation of the ternary group-addition graph forces every
  `k`-ary polymorphism on the prime-order subgroup to be linear. Idempotence and the WNU
  identities then force the unique modular average
  `w(x_1,...,x_k)=k^(-1) sum_i x_i` when `k` is invertible modulo the subgroup order.
- Factor-base obstruction: for every proper nontrivial factor base `F` of size `B`,
  Cauchy-Davenport gives `|kF| >= min(N,kB-k+1) > B`; modular averaging therefore cannot
  preserve the unary relation `F`.
- Producer theorem SHA-256:
  `f3cfa4518092c677c412198017fd7a3647243cf4d77adcd068a868a343c7cb14`.
- Surviving exception: a nonfaithful x-only summation-polynomial signature that does not
  primitive-positive define signed addition remains outside scope. Any successor must
  separately prove a non-affine preserving WNU, an exact all-strata signed source lift,
  no hidden completion table, and complete time/memory exponents at most `0.45`.
- Next admissible action: independent static review of the six-item checklist in the
  theorem receipt before any corpus-state or focus-queue transition.
- Boundary: this is a scoped nonexistence theorem for one CSP operation, not a general CSP
  lower bound, relation campaign, factor-log solve, blind descent, Shoup-bound
  improvement, or breakthrough.

### ECFG-P1515-R1 — Explicit universal facet-deck theorem gate

- Context: this receipt consumes IDEA-098's theorem-only next action without executing
  its retired `review_required`, zero-run contract. P1515 remains open and independently
  unverified pending static review.
- Producer status:
  `SCOPED_NEGATIVE_EXPLICIT_UNIVERSAL_FACET_DECK__COMPRESSED_TARGET_NAVIGATOR_OPEN`.
- Universal-deck result: for fixed arity `m`, the exact signed source deck has
  `M_m=Theta(B^m)` labelled tuples. A source-biconditional squarefree universal complex
  therefore has `Theta(B^m)` explicit facets; source-output collisions do not identify
  graph points because exact source inversion is required.
- Known-target yield: for `T` frozen random known-scalar targets, expected source rows are
  `T*M_m/N`. Constant-success rank `B` therefore requires
  `T=Omega(N/B^(m-1))`, even when every returned source is counted as independent.
- Explicit-facet cost: one batched traversal has
  `Omega(B^m + N/B^(m-1))` work. Minimizing
  `max(m*beta,1-(m-1)*beta)` gives `m/(2m-1)>1/2`; the frozen arities
  `3,4,5` give `3/5,4/7,5/9`. Thus explicit universal facets, facet dictionaries,
  complete shellings, and equivalent lift/source annotation lists miss rho.
- Scope correction: flatness does not force every fixed target fiber to contain the full
  universal deck. Its degree is `d_R=|sigma^(-1)(R)|`, with average `B^m/N`.
  A target-local output-small squarefree fiber is not closed; its public constructor and
  navigator are the missing operation.
- Surviving quantitative gate: at `m=5,beta=1/5`, a compressed grammar must have setup
  exponent at most `B^2.25` and per-target query exponent at most `B^1.25` before linear
  algebra, descent, output, and memory are charged, while retaining exact all-strata
  signed source lifting and no hidden `Theta(B^5)` dictionary.
- Producer theorem SHA-256:
  `51ad15480c7740cc9f340684bbb98d3701dc033593569949a9536b2e5e6caead`.
- Next admissible action: independent static review of the eight-item checklist, then a
  versioned compressed-navigator gate for the recursive `S3` source map. No P1515 code or
  toy run is authorized by this receipt.
- Boundary: this is a scoped explicit-representation and target-yield lower bound, not an
  arithmetic-circuit lower bound, relation campaign, factor-log solve, blind descent,
  Shoup-bound improvement, or breakthrough.

### ECFG-P1515-R2 — Compressed-navigator representation-separation gate

- Context: this theorem-only receipt instantiates the compressed exception left open by
  `ECFG-P1515-R1`. No contract, prototype, relation campaign, or finite experiment ran;
  independent verification remains `false`.
- Producer status:
  `OPEN_REPRESENTATION_SEPARATION__KNOWN_KSUM_CONTROLS_FAIL`.
- Frozen budget: at five sources and `B=N^(1/5)`, rank needs `Omega(B)` random
  known-scalar targets. A setup/query grammar with costs `B^s,B^q` therefore has the
  favorable floor `max(s/5,(1+q)/5,2/5,1/5)`, so P1515's `lambda<=0.45` gate requires
  `s<=2.25` and `q<=1.25` before failures, ambiguity, descent, and memory are charged.
- Explicit controls: storing `A_2` and scanning `A_3` costs `B^4` over the campaign;
  storing `A_3` and scanning `A_2` costs `B^3`; the offline six-list meet-in-the-middle
  control also materializes `B^3=N^0.6` source states.
- Current-literature control: Dinur-Golovnev 2026 `kSUM`-Indexing, instantiated as their
  `k=6` five-source query, gives
  `S=soft-O(B^(5.5-delta)), T=soft-O(B^delta)` for `0<=delta<=1` and
  `soft-O(B^5)` preprocessing. Even the most favorable point has setup exponent `4.5`.
  Their asymmetric `B^2`/`B^3` bound has `s=6-2*delta,q=2*delta`; imposing
  `q<=1.25` leaves `s>=4.75`. These are upper-bound controls, not lower bounds, and an
  elliptic transfer is not assumed.
- Representation-separation requirement: a successor must freeze one projective
  recursive-`S3` family, target-independent squarefree order, grammar, target router, and
  all-strata exact source lift; it must also identify a finite-field coordinate identity
  unavailable to black-box group addition/equality/hash at the same cost. Otherwise it
  merges into generic sum indexing rather than supplying a new operation.
- Producer receipt SHA-256:
  `dadcadf45bdea910f0a12e904bdfe32c4a517b0756ef08148de75fb39929e3e5`.
- Exactly one next action: write
  `ideas/artifacts/ECDLP-IDEA-098/recursive_s3_grammar_spec_v1.yaml`, freezing one concrete
  projective recursive-`S3` ideal, target-independent weight order, symbolic grammar
  nonterminals, setup/query recurrences, and exact source-lift interface. Reject the
  version on any `B^3` state stage or post-hoc source dictionary; do not implement or time
  a solver.
- Boundary: this is a mechanism-separation and known-algorithm comparison, not a proof
  against all compressed algebraic circuits, relation collection, factor-log recovery,
  blind descent, Shoup-bound improvement, or breakthrough.

### ECFG-P1515-R3 — Natural serial recursive-S3 grammar screen

- Context: the parsed YAML specification consumes P1515-R2's symbolic grammar action
  without running a contract, Grobner basis, toy curve, or prototype. Independent
  verification remains `false`.
- Producer status:
  `SCOPED_NEGATIVE_NATURAL_SERIAL_GRAMMAR_B3_PROVENANCE__NONLOCAL_ORDER_OPEN`.
- Frozen representation: five signed source slots are joined by four coherent projective
  addition stages `U2=P1+P2`, `U3=U2+P3`, `U4=U3+P4`, and `R=U4+P5`; standard `S3`
  equations are retained only as the x-coordinate core, with chord, tangent, vertical,
  infinity, repetition, and nonreduced strata explicitly required.
- First failing separator: the natural target-independent serial order creates
  `PREFIX2` with `Theta(B^2)` exact parent alternatives and `PREFIX3` with
  `Theta(B^3)=N^0.6`. Endpoint hashing does not delete exact source parents. Aggregating
  them into one endpoint polynomial removes biconditional source recovery unless a new
  output-sensitive unranking operation is proved.
- Semantic routing: explicit serial or balanced state materialization merges into
  P1511/IDEA-134; product/norm aggregation merges into P1510/P1513; dense elimination or
  moment construction merges into P1514; explicit universal facets remain closed by R1.
- Producer specification SHA-256:
  `884854c2928ce5baecf56f415653cb6bf436d5062309cbbcff3e60bcd0d49bc7`.
- Exactly one next action: write
  `ideas/artifacts/ECDLP-IDEA-098/recursive_s3_local_separator_trichotomy_v1.md`, proving
  or refuting that every source-biconditional recursive-`S3` grammar with a local serial
  or balanced separator falls into `B^3` provenance, a P1513-style product/norm object,
  or a P1514-style dense elimination object. Do not implement or time a solver.
- Boundary: no squarefree initial ideal was constructed, and the result does not close a
  nonlocal target-independent order with factored exact unranking. It is not relation
  collection, factor-log recovery, blind descent, a universal circuit lower bound,
  Shoup-bound improvement, or breakthrough.

### ECFG-P1515-R4 — Local-separator operator trichotomy

- Context: this theorem-only receipt screens the source-complete local operators left open
  after R3. No contract, Grobner basis, prototype, toy curve, or timing run was executed;
  independent verification remains `false`.
- Producer status:
  `SCOPED_NEGATIVE_KNOWN_LOCAL_SEPARATOR_OPERATORS__NOVEL_FIELD_ROUTER_OPEN`.
- Scoped cases: explicit provenance reaches `B^3`; endpoint-only equality/hash scanning
  costs `B^2` per target and still lacks source parents; replacing the scan is exactly the
  source-reporting five-term sum-index problem whose checked controls miss the P1515
  rectangle; known product/norm and dense quotient/moment aggregates route to frozen
  P1513 and P1514 evidence.
- Scope limit: the operator list is frozen, not universal. A new indexed or factored
  source-unranking primitive remains outside the trichotomy and must be exhibited rather
  than assumed. The sum-indexing comparisons are upper-bound controls, not lower bounds.
- Surviving mechanism: one target-independent finite-field coordinate router with at most
  `B^2.25` setup and `B^1.25` query, exact all-strata source output, and no `B^3` table,
  P1513 norm/common factor, or P1514 dense quotient.
- Producer theorem SHA-256:
  `dec667b097bcaefdf4c54091b2a9fa7757db5a65efe5b36e6ac15a6ff11a435a`.
- Exactly one next action: write
  `ideas/artifacts/ECDLP-IDEA-098/recursive_s3_field_router_candidate_v1.md`, deriving one
  concrete finite-field identity for the recursive-`S3` coefficient family and applying
  the P1511/P1513/P1514 removal tests before any implementation. Record
  `NO_CANDIDATE_OPERATION` if no identity survives.
- Boundary: this is a scoped representation screen, not an unconditional branching-
  program, data-structure, arithmetic-circuit, or Grobner-fan lower bound. It is not
  relation collection, factor-log recovery, blind descent, Shoup-bound improvement, or a
  breakthrough.

### ECFG-P1515-R5 — Sparse factor-map field-router removal

- Context: the final producer action derives one concrete finite-field identity and
  subjects it to the frozen removal tests. No contract, polynomial system, Grobner basis,
  prototype, toy curve, relation campaign, or timing run was executed; independent
  verification remains `false`.
- Producer status:
  `NO_PASSING_CANDIDATE_OPERATION__SPARSE_FACTOR_MAP_DUPLICATES_PKM16_AND_RESTORES_P1513`.
- Positive representation control: for a multiplicative x-coordinate factor map
  `L(X)=X^d-c`, `d=Theta(B)|p-1`, the one-step source incidence is
  `Res_X(L(X),S3(U,V,X))`. Since `S3` is quadratic in `X`, numeric membership reduces to
  the norm of `X^d-c` in a rank-two quadratic algebra and can use binary powering; a
  local candidate x-source follows from a degree-at-most-two gcd.
- Removal: the smooth-subgroup factor map is the PKM16 prime-field factor-base
  construction, is unavailable for a generic prime without their auxiliary-map machinery,
  does not itself enforce rational signed point membership, and supplies no five-step
  target router. Composing the transition correspondences restores P1511 explicit states,
  P1513 product/norm/common-factor elimination, or P1514 dense solving.
- Producer receipt SHA-256:
  `ee7c0ef479f33d3a82ab6827c286460604c6d26c9a76aa551305eccc2a337e24`.
- Exactly one next action: independent static review of the P1515 R1-R5 receipt chain,
  producing `ideas/artifacts/ECDLP-IDEA-098/p1515_r1_r5_independent_audit.md` and either a
  mechanism-new successor with an explicit router recurrence or a
  `deferred_no_candidate_operation` recommendation. Do not authorize the planned P1515
  contract or a solver search from this identity.
- Boundary: compact one-step factor-base membership is not compact composed path finding.
  No relation campaign, factor-log recovery, blind descent, generic-prime below-rho
  algorithm, Shoup-bound improvement, or breakthrough is claimed.

### ECFG-P1516-R1 — Fixed pair-sum quotient theorem gate

- Context: this theorem-only producer screen consumes the fixed rational pair-sum
  quotient proposed by ECDLP-IDEA-165. No contract, pair table, solver, toy curve,
  relation campaign, or timing run was executed; independent verification remains
  `false`.
- Producer status:
  `SCOPED_NEGATIVE_BOUNDED_DEGREE_PAIR_QUOTIENT_COMPRESSION__TARGET_LOCAL_ROUTER_OPEN`.
- Exact-composition gate: a predicate that decides `u+v+w=R` biconditionally from
  only `pi(u),pi(v),pi(w),pi(R)` forces `pi` to be injective. A noninjective state map
  therefore needs false positives, source lists, or another discriminator.
- Source-list gate: for the favorable unordered pair domain
  `D={{S,T}:S,T in F}`, any target-independent exact inverse with `M` states and
  maximum list `L` satisfies `M*L>=|D|=B(B+1)/2`. Constant-list unranking therefore
  requires `Omega(B^2)` states, while `B^(2-epsilon)` states force a
  `B^epsilon` source list somewhere.
- Algebraic gate: a nonconstant bounded-degree rational map has bounded geometric
  fibers. On a generic/Sidon factor base at `B=N^(1/5)`, `|F+F|=Theta(B^2)`, so its
  image remains `Theta(B^2)`. Small-doubling factor bases move the same payload into
  average pair-source multiplicity rather than supplying a constant-list inverse.
- Cost boundary: `B^2=N^0.4` setup is not itself above rho. The failure is that the
  quotient has not supplied P1515's required target router; direct scanning over
  `Omega(B)` relation targets is `B^3=N^0.6`. An arbitrary indexed router remains
  open because the checked `kSUM` tradeoffs are upper-bound controls, not lower bounds.
- Producer theorem SHA-256:
  `18cebc9c209c6ba0d705e43da7f921885e60d3436b201375e306e14f4ae0bdb2`.
- Exactly one next action: independently review
  `ideas/artifacts/ECDLP-IDEA-165/pair_sum_quotient_theorem.md` and either recommend
  rejection of the fixed-map operation or freeze one explicit noncongruence
  target-local collision-router recurrence with setup at most `B^2.25`, query at most
  `B^1.25`, and exact all-strata source output. Do not build a pair table or run a
  solver.
- Boundary: this closes the bounded-degree fixed quotient as the missing compression,
  not arbitrary preprocessing, arithmetic circuits, or target-local data structures.
  No relation campaign, factor-log solve, blind descent, Shoup-bound improvement, or
  breakthrough is claimed.

### ECFG-P1517-R1 — Prime-to-p ramification-data invariance gate

- Context: this theorem-only producer screen consumes ECDLP-IDEA-160's proposed
  nonlogarithmic ramification-break digit operation. No contract, local-field tower,
  precision computation, scalar sample, or timing run was executed; independent
  verification remains `false`.
- Producer status:
  `SCOPED_NEGATIVE_FUNCTORIAL_FULL_TOWER_RAMIFICATION_IS_GENERATOR_INVARIANT__ORIENTED_BRANCH_OPEN`.
- Generator-field gate: for nonzero `Q=[x]P` in the prime-order subgroup,
  `<Q>=<P>` and `K(Q)=K(P)=K(<P>)` because `x` is invertible modulo `N`.
- Good-reduction gate: with `N!=p`, Neron-Ogg-Shafarevich makes the `N`-adic
  Tate module and every finite `E[N^m]` layer unramified. Their positive
  upper/lower ramification groups therefore carry no generator label.
- Full-fiber gate: if `gcd(a,N)=1`, then `[a]^(-1)(Q)=h_Q+E[a]` with
  `h_Q in <P>`, and its full field is `K(<P>,E[a])`, independently of `x`.
  This includes `p`-power division fibers: their ramification comes from the common
  `E[p^m]` field. Multiplication by `x` likewise identifies full `N`-primary fibers.
- Consequence: every functorial ramification filtration, break, discriminant,
  conductor, Herbrand function, or field-of-norms object of those towers is constant
  on the nonzero scalar orbit. It distinguishes `Q=O` at most; it returns no generic
  scalar digit.
- Open exception: a selected nonfunctorial branch may vary with `Q`, but its public
  canonical selector and typed return are the new operation and must be charged as
  orientation, not assumed from pure ramification data.
- Producer theorem SHA-256:
  `33079fb5e6fef57fe6d4b21b65b82cba0eea9bcf6dcbbea1e2331df4978b24a7`.
- Exactly one next action: independently review
  `ideas/artifacts/ECDLP-IDEA-160/ramification_data_gate.md` and either recommend
  scoped rejection or freeze one publicly canonical nonfunctorial oriented branch
  with a typed scalar law and complete sub-rho cost. Do not construct or time a tower.
- Boundary: this closes functorial full-tower ramification data, not every conceivable
  marked local-field branch. No scalar recovery, below-rho generic-prime algorithm,
  Shoup-bound improvement, or breakthrough is claimed.

### ECFG-P1518-R1 — Non-diagonal polar generic-stalk gate

- Context: this theorem-only producer screen consumes ECDLP-IDEA-159's proposed
  non-diagonal conormal/polar Rees atomizer. No contract, Rees algebra,
  normalization, chart, source tuple, toy curve, or timing run was executed;
  independent verification remains `false`.
- Producer status:
  `SCOPED_NEGATIVE_GENERIC_STALK_REES_TRICHOTOMY__SOURCE_INDEXED_CENTER_OPEN`.
- Generic-stalk gate: componentwise on the reduced all-distinct incidence,
  `O_(X,eta)` is a function field. The stalk of an ordinary coherent ideal is
  therefore zero or the unit ideal, never a proper nonzero generic ideal.
- Blowup gate: a nonzero ideal is unit on a dense open and its blowup is an
  isomorphism there. A zero generic ideal has no positive-degree Rees object on
  that component. A proper critical center changes only its closed support.
- Cartier gate: making the polar center divisorial does not help because blowing
  up an invertible ideal is an isomorphism. Noninvertible centers live on proper
  branch/collision/critical loci and cannot label every generic source tuple.
- Reducible boundary: choosing zero/unit behavior separately on source components
  already encodes a component partition. Refining such centers into exact valuation
  words needs a compact source-component rule; otherwise it is a source dictionary.
- Producer theorem SHA-256:
  `755fdab79fd2ed0c60054a9b7dfbd32ff7dc6e5e36d93ed9f1dddaa9ac05d7b3`.
- Exactly one next action: independently review
  `ideas/artifacts/ECDLP-IDEA-159/non_diagonal_polar_theorem.md` and either recommend
  scoped rejection or freeze one nonordinary target-independent representation with
  a compact exact source-component rule and complete sub-rho cost. Do not construct
  a Rees algebra.
- Boundary: this closes ordinary polar/Rees atomization on the generic stratum, not
  every derived, stacky, noncommutative, or target-local nonlinear representation.
  No relation campaign, factor-log solve, blind descent, Shoup-bound improvement, or
  breakthrough is claimed.

### ECFG-P1519-R1 — Four-window Kummer interpretation gate

- Context: this theorem-only producer screen consumes ECDLP-IDEA-158's natural
  full-`S3` x-only WNU operation. No contract, CSP solver, finite instance, toy
  curve, relation campaign, or timing run was executed; independent verification
  remains `false`.
- Producer status:
  `SCOPED_NEGATIVE_FULL_S3_KUMMER_SIGNATURE_PP_INTERPRETS_ADDITION__HIGH_ARITY_SIGNATURE_OPEN`.
- Oriented-domain gate: for any nonzero public `g` in the prime-order group, the
  four-state tuple `([t],[t+g],[t+2g],[t+3g])` is primitive-positive defined by
  its six pairwise Kummer-distance atoms. The exceptional sign branches have empty
  intersection for prime order `N>=5`, so the encoding is bijective without a
  y-sign oracle or source table.
- Addition gate: on three encoded tuples, seven distinct ternary Kummer atoms force
  `gamma=alpha+beta`. Three horizontal and three vertical atoms reduce the possible
  branches to the true sum or `alpha=beta,gamma=0`; two mixed atoms eliminate the
  sole distinct exceptional case `alpha=beta=-2`.
- Polymorphism gate: any idempotent WNU preserving full `S3`, the adjacent public
  constants, and the x-factor base transports through the encoding to a WNU on the
  faithful prime-cyclic addition graph. It is therefore modular averaging. Iterated
  Cauchy-Davenport shows that averaging cannot preserve the proper nontrivial
  oriented factor-base lift, for every arity at least three.
- Scope limit: the theorem is parameterized and closes signatures exposing full
  ternary `S3`, including recursive high-arity implementations. It does not close a
  deliberately high-arity-only language proved unable to primitive-positive define
  the four-window gadget. Such a language must still exhibit a sparse-base WNU and
  an exact all-sign source lift without restoring adjacent Kummer transitions.
- Producer theorem SHA-256:
  `e904d2d29504f67cb45728fb621c221287baf7ca7527d810fa4cd3b691d82a7b`.
- Exactly one next action: independently review
  `ideas/artifacts/ECDLP-IDEA-158/nonfaithful_signature_theorem.md` and either
  recommend scoped rejection of the full-`S3` operation or freeze one explicit
  high-arity-only signature with proofs of gadget noninterpretability, sparse-base
  WNU preservation, and exact all-sign source lifting. Do not implement a CSP solver.
- Boundary: this is a representation no-go for the natural full-`S3` signature, not
  a no-go for every summation-polynomial language. No relation campaign, factor-log
  solve, blind descent, generic-prime below-rho algorithm, Shoup-bound improvement,
  or breakthrough is claimed.

### ECFG-P1520-R1 — Full high-arity affine Kummer pinning gate

- Context: this theorem-only producer screen attacks the explicit high-arity-only
  exception left by ECFG-P1519-R1. No contract, CSP solver, finite-field search,
  toy curve, relation campaign, or timing run was executed; independent
  verification remains `false`.
- Producer status:
  `SCOPED_NEGATIVE_FULL_AFFINE_SM_FOR_M_GE_5_PP_DEFINES_S3__AFFINE_S4_OR_RESTRICTED_LANGUAGE_OPEN`.
- Pinning gate: for fixed `m>=5`, put `k=m-3`. If `m` is odd, `k` repeated
  nonzero pins have a zero signed padding sum. If `m` is even, `k-1` repeated
  pins plus `[(k-1)z]` have one. A false ternary signed sum can satisfy the
  resulting `R_m` atom at at most `16k` sign orbits `[z]`, so conjunction at
  `16k+1` distinct public nonzero pins primitive-positive defines affine `R3`.
- Affine-chart gate: on
  `U=G minus {0,-g,-2g,-3g}`, the four-window domain and seven-atom addition
  gadget remain valid. Any induced partial additive WNU on `U^r` extends to
  `G^r`: decompositions and comparison bridges exist coordinatewise after
  avoiding at most sixteen values.
- Polymorphism consequence: the extension is a homomorphism; WNU and idempotence
  force modular averaging. The interpreted factor-base subset loses at most four
  oriented values, so iterated Cauchy-Davenport still forbids preservation at
  every arity at least three.
- Scope limit: this closes direct full affine `S5` and every fixed full affine
  `S_m` for `m>=6`, even without an infinity constant. It does not close strict
  affine full `S4`, a proper promise/subrelation/projection that invalidates the
  pinning formula, or a non-WNU operation. Exact all-source lifting and complete
  below-rho costs remain mandatory for every survivor.
- Producer theorem SHA-256:
  `9da224432a97db91e002cd220503df8857235792faecfdbc2eb58f2660b604be`.
- Exactly one next action: independently review both IDEA-158 theorem gates and
  either recommend scoped rejection of full `S3` and full affine `S_m` for
  `m>=5`, or freeze strict affine full `S4` and prove gadget noninterpretability,
  sparse-base WNU preservation, and exact all-sign source lifting. Do not run a
  CSP solver.
- Boundary: this is a scoped representation theorem, not a lower bound against
  every x-only language or non-WNU operation. No relation campaign, factor-log
  solve, blind descent, generic-prime below-rho algorithm, Shoup-bound improvement,
  or breakthrough is claimed.

### ECFG-P1521-R1 — Strict affine S4 two-atom chain gate

- Context: this theorem-only producer screen consumes the sole full-relation
  exception left by ECFG-P1520-R1. No contract, CSP solver, finite-field search,
  toy curve, relation campaign, or timing run was executed; independent
  verification remains `false`.
- Producer status:
  `SCOPED_NEGATIVE_FULL_AFFINE_S4_PP_DEFINES_S3__RESTRICTED_LANGUAGE_OR_NON_WNU_OPEN`.
- Chain gate: for a nonzero public `z`, two affine `R4` atoms sharing one
  existential nonzero Kummer state realize a six-term signed relation on
  `(a,b,c,z,z,2z)`, provided the first three-term partial sum is nonzero.
- Completeness gate: if a ternary signed sum is zero, padding signs
  `z+z-2z=0` work. When the first partial sum vanishes, flipping only the
  three source signs makes it nonzero in odd characteristic, so the affine
  intermediate never requires the point at infinity.
- False-shift gate: if no ternary signed sum is zero, every accepted pin obeys
  `l+c*z=0` with one of eight ternary signed sums `l` and
  `c in {-4,-2,2,4}`. At most 32 sign orbits can pass, so conjunction at 33
  distinct nonzero public pins primitive-positive defines affine `R3`.
- Consequence: the ECFG-P1519 four-window addition interpretation and ECFG-P1520
  local homomorphism extension apply unchanged. WNU again forces modular
  averaging, which cannot preserve the proper asymptotic factor-base subset.
- Scope limit: the combined IDEA-158 receipts close WNU on every full fixed-arity
  rational-point Kummer summation relation `S_m`, `m>=3`. They do not close a
  proper target-uniform promise subrelation/projection with a proved complete
  source lift, or a non-WNU operation.
- Producer theorem SHA-256:
  `84fefb4193dfa0e47acad8751a2a79e3b6b0c3818d7926e14db9fad0c24ffb4e`.
- Exactly one next action: independently review all three IDEA-158 theorem gates
  and either recommend scoped rejection of WNU on every full affine summation
  relation, or freeze one explicit branch-deleting promise subrelation and prove
  gadget avoidance, sparse-base WNU preservation, exact all-sign source lifting,
  and complete sub-rho cost. Do not run a CSP solver.
- Boundary: this is a scoped representation theorem, not a lower bound against
  every restricted x-only language or non-WNU algorithm. No relation campaign,
  factor-log solve, blind descent, generic-prime below-rho algorithm,
  Shoup-bound improvement, or breakthrough is claimed.

### ECFG-P1522-R1 — Restricted-language and induced-template access gate

- Context: this theorem-only producer screen separates fixed signed branch deletion
  from restriction to the induced factor-base template. No contract, CSP solver,
  finite-field search, toy curve, relation campaign, or timing run was executed;
  independent verification remains `false`.
- Producer status:
  `SCOPED_NEGATIVE_LIFT_INVARIANT_FIXED_BRANCH_DELETION__INDUCED_TEMPLATE_SUPPORT_ROUTER_OPEN`.
- Branch-invariance gate: modulo global negation, the full affine `m`-source
  Kummer relation is the union of `2^(m-1)` signed hyperplanes. For
  `N>2^(m-1)+m-1`, every branch has a nonzero-coordinate point outside all
  other branches. Independent lift flips act transitively on those branches,
  so the only lift-invariant fixed branch families are empty and full.
- Scope correction: the ambient IDEA-158 no-go does not automatically close an
  operation defined only on `F_x` and preserving an induced target fiber. A
  singleton fiber is preserved by every idempotent operation, demonstrating that
  an induced WNU can be algebraically vacuous and still reveal no source.
- Access gate: the complete endpoint-labelled induced relation graph has at least
  `B^m` entries; at `m=5,B=N^(1/5)` this is `N`. Keeping it implicit changes every
  local-consistency support test into an exact residual restricted-summation query,
  and returning support is exact source unranking.
- Router boundary: a surviving induced-template operation must supply the missing
  target-independent support/witness router with setup at most `B^2.25`, query at
  most `B^1.25`, exact all-strata output, and complete rank/descent costs. This is
  operationally the P1515/IDEA-165 frontier, not a free consequence of WNU.
- Producer theorem SHA-256:
  `d54344c1c063dd7a7df1fadcc7826a8cb6bb5627414458b9877b47569803f302`.
- Exactly one next action: independently review all four IDEA-158 gates and either
  recommend `deferred_induced_template_router_not_supplied`, or freeze one explicit
  induced five-source support/witness recurrence meeting the P1515 setup/query
  rectangle, sparse-base non-affine WNU, exact source lift, and complete sub-rho
  factor-log and blind-descent gates. Do not run a CSP solver.
- Boundary: this is a fixed-branch no-go and an access/accounting reduction, not an
  unconditional lower bound against lift-invariant tuple predicates, induced-template
  data structures, or non-WNU algorithms. No relation campaign, factor-log solve,
  blind descent, generic-prime below-rho algorithm, Shoup-bound improvement, or
  breakthrough is claimed.

### ECFG-P1523-R1 — Prime-order exact composable bucket gate

- Context: this theorem-only producer screen consumes the exact nested-filter arm of
  ECDLP-IDEA-057's generalized-birthday operation. No contract, bucket campaign,
  finite instance, relation search, toy curve, or timing run was executed;
  independent verification remains `false`.
- Producer status:
  `SCOPED_NEGATIVE_EXACT_COMPOSABLE_BUCKET_LABELS_ARE_CONSTANT_OR_INJECTIVE__NONHOMOMORPHIC_CORRECTION_OPEN`.
- Congruence gate: if bucket equality is preserved under addition of arbitrary
  equal-labelled pairs, its zero fiber is a subgroup and every fiber is a coset.
  Equivalently, every exact label-composition law factors through a quotient group.
- Prime-order consequence: the subgroup is zero or the whole group. The label is
  therefore injective or constant. A succinct injective label retains the full point
  and supplies no quotient collisions; a constant label supplies no filter.
- Wagner boundary: exact progressive cancellation through a proper quotient chain is
  unavailable on the prime-order subgroup. The theorem does not close list-specific
  filters, approximate sieves, or field-derived nonhomomorphic corrections.
- Kummer boundary: x-coordinate orbits are not exact single-valued composable labels;
  restoring faithful adjacent context gives the order-`N` IDEA-158 state rather than
  a proper quotient.
- Producer theorem SHA-256:
  `524a59c1728bcbea804ac4be42ace5a965b68a6332e85d941829b89e04fc4225`.
- Exactly one next action: independently review the theorem and either preserve
  scoped rejection of exact bucket composition or derive one explicit
  nonhomomorphic field-specific correction identity with a proved support-law change,
  exact signed source replay, and complete sub-rho relation/rank/descent costs. Do not
  implement a bucket campaign.
- Boundary: this is a congruence theorem, not an unconditional list-algorithm or
  arithmetic-circuit lower bound. No relation campaign, factor-log solve, blind
  descent, generic-prime below-rho algorithm, Shoup-bound improvement, or
  breakthrough is claimed.

### ECFG-P1524-R1 — Kummer trace/norm correction removal gate

- Context: this theorem/identity-only producer screen tests the first concrete
  nonhomomorphic exception left by ECFG-P1523-R1. No contract, bucket campaign,
  finite-field search, toy curve, relation collection, or timing run was executed;
  independent verification remains `false`.
- Producer status:
  `SCOPED_NEGATIVE_PAIRWISE_KUMMER_TRACE_NORM_IS_AN_S3_NORM_BACKEND__LIST_SPECIFIC_SUPPORT_ROUTER_OPEN`.
- Pair gate: on a short Weierstrass curve and the affine nonvertical chart, the
  unordered roots `{x(P+Q),x(P-Q)}` have trace and norm equal to the normalized
  linear and constant coefficients of `S3(x(P),x(Q),Z)`. The rank-two state is
  exact but is not a new correction identity.
- Deck gate: for `F(U)=product_i(U-u_i)`, aggregating the pair states is exactly
  `Res_U(F(U),S3(U,v,Z))=product_i S3(u_i,v,Z)`. Two-deck aggregation has one
  quadratic leaf per source pair; source-complete composition is an iterated
  norm/resultant with the P1478/P1513/P1515 provenance obligations.
- Wagner boundary: trace/norm is nonhomomorphic, so it avoids the prime-order
  congruence theorem, but it does not transport an earlier cancellation, map a
  failed merge to a new valid relation, or prove support enrichment. Bucketing a
  trace or norm coefficient only adds a filter whose failed branches and source
  preimages still require a charged router.
- Scope limit: this removes raw pairwise Kummer trace/norm as a mechanism-new
  correction. It does not close a list-specific support-changing field identity,
  an output-sensitive circuit common-root operation, or an implicit exact source
  router meeting the P1515 setup/query rectangle.
- Producer receipt SHA-256:
  `81a025925063937f4a496e0f6b0618b32525b1c176627449bdbd8eb96dd2f947`.
- Exactly one next action: independently review both IDEA-057 receipts and either
  preserve their scoped rejections or freeze one explicit list-specific
  support-changing identity/router with exact exceptional-strata source replay and
  complete sub-rho relation, rank, factor-log, and blind-descent costs. Do not run a
  bucket campaign.
- Boundary: this is a representation/backend removal receipt, not an unconditional
  arithmetic-circuit or list-algorithm lower bound. No relation campaign, factor-log
  solve, blind descent, generic-prime below-rho algorithm, Shoup-bound improvement,
  or breakthrough is claimed.

### ECFG-P1525-R1 — Exact spectral rank/density gate

- Context: this theorem-only producer screen evaluates IDEA-001's exact
  target-uniform linear character-factorization mechanism. No contract, character
  table, tensor, curve fixture, relation search, or timing run was created;
  independent verification remains `false`.
- Producer status:
  `SCOPED_NEGATIVE_EXACT_LINEAR_TARGET_UNIFORM_SPECTRAL_FACTOR_WITH_ONE_WITNESS__NONLINEAR_MULTIROW_ROUTER_OPEN`.
- Rank gate: flattening the exact `m`-source addition incidence tensor with target
  rows and source-tuple columns gives one standard basis column per tuple sum, so
  its rank over any coefficient field is exactly `|mF|`. Every exact separated
  linear/character representation has at least that many components.
- Density gate: with `S=|mF|`, a uniform known-log target is supported with
  probability `S/N`. Under the favorable one-witness/one-independent-row API,
  collecting `B` rows requires at least `B*N/S` attempts. Explicit components plus
  attempts therefore cost at least `max(S,B*N/S)>=sqrt(B*N)`.
- Campaign consequence: for `B=N^beta,beta=1/5`, the favorable optimized exponent
  is `(1+beta)/2=3/5`, already above rho before witness recovery, exceptions,
  linear algebra, descent, or memory traffic.
- Scope limit: this closes the exact linear low-rank one-witness mechanism, not a
  nonlinear operation that consumes a succinct target batch, emits many
  independently ranked exact rows, and avoids materializing modes or failed targets.
  That exception is the unresolved P1515 support/witness router.
- Producer theorem SHA-256:
  `e572713a3910ef6a3e31ac360123aa8b5135c75d4210cbfb579e6831e9746fca`.
- Exactly one next action: independently review the IDEA-001 receipt and either
  recommend scoped rejection of its exact linear branch or freeze one explicit
  nonlinear implicit-batch/multirow recurrence with exact all-strata sources and
  complete sub-rho relation, rank, factor-log, and blind-descent costs. Do not run
  the old character preflight.
- Boundary: this is a linear representation and favorable density theorem, not an
  unconditional arithmetic-circuit, nonlinear data-structure, or ECDLP lower bound.
  No relation campaign, factor-log solve, blind descent, generic-prime below-rho
  algorithm, Shoup-bound improvement, or breakthrough is claimed.

### ECFG-P1526-R1 — ECFFT auxiliary-isogeny router gate

- Context: this theorem-only producer screen tests ECFFT as a generic-prime
  realization of the field-specific/list-restricted exception left by P1523-P1525.
  No contract, ECFFT construction, finite-field search, curve fixture, bucket
  campaign, relation collection, or timing run was executed; independent
  verification remains `false`.
- Producer status:
  `SCOPED_NEGATIVE_ECFFT_AUXILIARY_TREE_IS_NOT_A_TARGET_GROUP_ROUTER__LIST_SPECIFIC_INTERTWINER_OPEN`.
- Target-isogeny gate: for an `F_p`-rational isogeny `phi` with
  `deg(phi)<N`, the kernel of `phi` on the prime-order target subgroup `G` is a
  proper subgroup and hence trivial. Therefore the ECFFT chain is injective on
  `G`; after x-projection its only ambiguity is `P` versus `-P`, not a growing
  quotient hierarchy.
- Auxiliary-tree gate: ECFFT's certified two-to-one maps act on evaluation sets
  built from a smooth subgroup on an auxiliary curve. On an unrelated target
  curve they supply no identity transporting target addition, failed merges, or
  exact signed source witnesses. Applying the maps to target x-coordinates is a
  rational filter unless a new `S3` intertwining factorization is proved.
- Canonical-map gate: for `psi(x)=x+c+1/x`, a global factorization through
  `psi` would make the transformed Kummer trace invariant under `x -> 1/x`.
  On `y^2=x^3+1` with the other input `Y=2`, the exact trace difference is
  `9*(X-1)*(X+1)*(2*X^2+X+2)/((X-2)^2*(2*X-1)^2)`, so the universal
  degree-two auxiliary-map factorization is false. Exceptional curves, other
  maps, and list-restricted supports remain open.
- Occupancy control: at `B=N^(1/5)`, requiring one pair sum to land in a
  certified set of size `O(sqrt(N))` has expected occupancy
  `O(B^2*sqrt(N)/N)=O(N^(-1/10))` on the low-additive-energy/random-support
  control. Constant expected occupancy needs explicit support
  `Omega(N/B^2)=Omega(N^(3/5))=Omega(B^3)`, beyond the P1515 setup cap. This
  statement is model-bound and preserves proved support enrichment as open.
- Backend gate: ECFFT accelerates dense univariate polynomial operations through
  invertible local transforms; it does not reduce exact degree/source traffic.
  Pairwise Kummer evaluation routes to P1524, transition composition to P1513,
  and expanded fiber/quotient objects to P1514 unless a new output-sensitive
  source splitter is supplied.
- Producer theorem SHA-256:
  `f8abb802b5052f614a6500c722083d3ebbd45d6e54353686ff3283ffa27a88b7`.
- Exactly one next action: independently review this receipt with P1523-P1525 and
  either preserve the scoped ECFFT removal or freeze one explicit resultant
  factorization through an auxiliary rational map on the admitted recursive-`S3`
  supports, including exact all-strata source inversion and complete
  `B^2.25/B^1.25` plus relation-rank, factor-log, and blind-descent accounting.
  Do not build an FFT tree or run a bucket campaign without that identity.
- Boundary: this is an isogeny-kernel, representation-separation, and model-bound
  occupancy gate, not an unconditional lower bound against list-specific
  intertwiners, nonlinear circuits, or support-enriched factor bases. No relation
  campaign, factor-log solve, blind descent, generic-prime below-rho algorithm,
  Shoup-bound improvement, or breakthrough is claimed.

### ECFG-P1527-R1 — Canonical ECFFT list-support branch-locus gate

- Context: this theorem-only producer screen consumes the first list-specific
  exception left by P1526. It asks whether the canonical degree-two auxiliary map
  can transport the complete Kummer branch polynomial after restricting source
  pairs. No contract, finite-field sample, factor-base construction, ECFFT tree,
  relation search, toy scalar recovery, or timing run was executed; independent
  verification remains `false`.
- Producer status:
  `SCOPED_NEGATIVE_CANONICAL_TWO_ISOGENY_LIST_SUPPORT_HAS_ONLY_DECK_FIXED_COMPONENT__OTHER_MAPS_AND_TARGETS_OPEN`.
- Frozen family: on `E:y^2=x^3+1`, use
  `psi_c(x)=x+c+1/x` over `Q(c)`, with deck involution `x -> 1/x`.
  The two transformed Kummer roots are branch-complete only when both their trace
  and norm are invariant under that involution.
- Common-component gate: if `D_T,D_N` are the reduced numerators of those trace
  and norm differences, exact gcd gives
  `gcd(D_T,D_N)=X^2-1`. The only common curve component is `X=+-1`, where the
  deck involution is fixed and supplies no two-to-one source compression.
- Constant-residue gate: after dividing by `X^2-1` at `c=0`, both residual
  equations have bidegree `(6,7)`, coprime contents, and a nonzero degree-84
  resultant. Their nonfixed intersection therefore has at most 84 algebraic
  ordered pairs counted with multiplicity, independent of factor-base size.
- List consequence: a support that keeps one representative from each deck pair
  makes `psi_c` injective; a support that keeps both representatives has only the
  deck-fixed positive-dimensional component and a bounded nonfixed residue on
  this target/map. Thus it cannot supply asymptotically many compressed first-
  level merges in the frozen scope.
- Producer theorem SHA-256:
  `e4972a1c6f4fb796a9efa556c745c4d4d5e4b00e5637e9fca9f3828abb4db120`.
- Exactly one next action: independently review P1526-P1527 and either preserve
  the canonical-map scoped removal or freeze one different rational map/target
  family with a positive-dimensional nonfixed simultaneous trace/norm invariance
  component, exact all-strata source inverse, and complete P1515 plus relation-
  rank, factor-log, and blind-descent costs. Do not build an ECFFT tree from a
  trace-only or deck-fixed component.
- Boundary: this closes one target, one canonical map family, and pairwise exact
  branch transport. It is not an unconditional lower bound against other curves,
  maps, exceptional parameters, non-Cartesian recursive supports, approximate
  support-changing corrections, or nonlinear multirow routers. No relation
  campaign, factor-log solve, blind descent, generic-prime below-rho algorithm,
  Shoup-bound improvement, or breakthrough is claimed.

### ECFG-P1528-R1 — ECFFT/Lattes rational-kernel cofactor gate

- Context: this theorem-only producer screen tests the strongest global
  intertwiner exception left by P1526-P1527: an actual same-field target isogeny
  or Lattes map whose smooth kernel supplies many source representations. No
  contract, isogeny chain, curve fixture, finite-field sample, preimage tree,
  relation search, factor-log solve, toy scalar recovery, or timing run was
  executed; independent verification remains `false`.
- Producer status:
  `SCOPED_NEGATIVE_TARGET_ISOGENY_INTERTWINER_HAS_SUBPOLYNOMIAL_RATIONAL_KERNEL_AND_DUPLICATE_LOG_COLUMNS__EXTENSION_AND_NONGROUP_SUPPORT_OPEN`.
- Cofactor gate: write `#E(F_p)=h*N` for the target prime subgroup
  `N=p^(1+o(1))`. If an `F_p`-rational isogeny preserves that subgroup, its
  rational kernel has trivial intersection with it. The rational-kernel order
  therefore divides `h`, so it is at most `p^o(1)=N^o(1)`; it is trivial on a
  cofactor-one curve and constant on a constant-cofactor family.
- Hasse gate: a same-field curve carrying both the order-`N` target subgroup and
  a rational ECFFT kernel of order `K` would have `K*N|#E(F_p)`, while Hasse gives
  `#E(F_p)<=p+1+2*sqrt(p)`. Hence no `K>=N^kappa`, `kappa>0`, is available on the
  frozen family. A polynomial ECFFT tree must live on an auxiliary curve without
  the target subgroup.
- Rational-preimage gate: if a rational preimage exists, all rational preimages
  form a torsor under the rational kernel and number at most `N^o(1)`. Geometric
  nonrational preimages are extension-field data, not same-field factor points.
- Rank gate: kernel-coset preimages have the same isogeny image and therefore the
  same factor-log column. For fixed arity `m`, their `K^m=N^o(1)` lifted
  representations change no exponent and provide no independent row rank after
  image-column aggregation.
- Semantic boundary: this is earlier than IDEA-113's arboreal branch-state
  obstruction. P1528 bounds rational branching itself and then removes duplicate
  log columns; IDEA-113 charges orientation of a deep geometric inverse tree.
- Producer theorem SHA-256:
  `342e872f1e86297d88bb8684155ed84cf7c3b37351402fba4c296ff986ab141e`.
- Exactly one next action: independently review P1526-P1528 and either preserve
  the same-field ECFFT/Lattes removal or freeze one explicit extension-field or
  unrelated-auxiliary intertwiner whose rational target-source yield, column
  rank, setup/query, factor-log, and blind-descent costs meet the P1515 gates.
  Do not credit geometric or kernel-coset multiplicity before image-column
  aggregation.
- Boundary: this is a same-field rational-kernel and rank theorem, not an
  unconditional lower bound against extension-field descent, unrelated auxiliary
  maps, non-Cartesian support laws, or nonlinear batch/multirow routers. No
  relation campaign, factor-log solve, blind descent, generic-prime below-rho
  algorithm, Shoup-bound improvement, or breakthrough is claimed.

### ECFG-P1529-R1 — P1515 R1-R11 independent disposition

- Context: an independent static reviewer reconstructed the complete P1515 R1-R11
  receipt chain, the frozen source/yield/rank/cost interface, and the surviving
  extension/intertwiner and nonlinear batch/multirow classes. No contract, solver,
  parameter sweep, elliptic fixture, relation campaign, or experiment ran.
- Independent status:
  `INDEPENDENT_SCOPED_AUDIT_PASS__DEFERRED_NO_CANDIDATE_OPERATION`.
- Receipt result: every R1-R11 artifact hash matches the ledger and artifact index;
  every scoped negative or semantic removal is accepted only within its recorded
  operator class. The R10 gcd `X^2-1` and degree-84 resultant were reconstructed
  exactly rather than inferred from finite samples.
- P1528 correction: `K_rat|h` follows directly because
  `|H_rat+G|=K_rat*N` divides `#E(F_p)=h*N`. For an image point of `G`, exactly one
  rational kernel-fiber preimage lies in `G`; the other rational or geometric lifts
  have no target-subgroup logarithm. They collapse to one image column and add no
  independent rank. This correction is append-only and does not rewrite P1528.
- Extension routing: ordinary algebraic or Frobenius-equivariant trace-zero maps
  route to independently verified negative P1501. A genuinely nonequivariant
  public evaluator plus a decomposition-changing locus remains owned by IDEA-009;
  nontrivial cover geometry beyond raw deck multiplicity remains owned by IDEA-010;
  neither record currently supplies an explicit source-invertible fully costed
  operation.
- Nonlinear routing: R8's implicit-batch and multirow exceptions remain logical
  open classes, but no receipt supplies a target-independent recurrence, exact
  all-strata sources, post-aggregation rank `B`, masked descent, and complete
  `lambda,mu<=0.45` accounting. Naming an accepted-facet navigator, common-root
  circuit, or spectral consumer does not instantiate the missing operation.
- Scoped decision: recommend `deferred_no_candidate_operation` for P1515, cancel
  its never-authorized planned run, preserve its underlying claim as unattempted,
  and rerank outside the squarefree-shelling/ECFFT-kernel grammar. This is not a
  lower bound against all circuits, data structures, covers, or extension maps.
- Independent audit SHA-256:
  `7e7609716f87b1b4df5ffc77406a912ad0303cc309ec1b84be42ebcc0d09539e`.
- Exactly one next action: write a theorem-only, branch-complete specification for
  IDEA-003's partial scalar-power correspondence at
  `ideas/artifacts/ECDLP-IDEA-003/correspondence_spec.md`, and reject the version
  unless one explicit public branch rule outputs `[x^D]P` with charged
  acquisition-plus-Cheon cost below rho on the claimed generic subgroup family.
- Boundary: independent reconstruction and a no-candidate disposition are not a
  relation campaign, factor-log solve, blind descent, Shoup-bound improvement, or
  breakthrough. The full ECDLP objective remains open.

### ECFG-P1530-R1 — Partial scalar-power correspondence producer gate

- Context: the theorem-only P1530 producer pass froze IDEA-003's public branch,
  verification, divisor-applicability, Cheon-recovery, and memory interface. No
  contract, solver, point fixture, parameter sweep, or experiment ran.
- Producer status: `SCOPED_NO_PASS__OPEN_COMPACT_EXPONENT_COSET_TESTER`; independent
  review is pending, so P1530 remains queued and the underlying claim remains open.
- Rational-map result: every single-valued rational map `E->E` is a homomorphism
  followed by translation and is scalar-affine on the rational prime-order subgroup.
  Complete group-sum traces of finite correspondence branches are affine through the
  induced `Pic^0` push-pull action. This does not close irreducible higher-genus
  correspondences with a compact nonalgebraic public selector.
- Retry-cost correction: algebraic correspondence membership is not a certificate that
  `Z=[x^D]P`. Without a cheaper sound verifier, every false branch pays Cheon plus final
  scalar verification. For `B=ell^beta` materialized affine sections, inverse density
  `ell^delta`, and `D=ell^alpha`, the receipt gives
  `lambda>=beta+delta+chi(alpha)>=1-alpha+chi(alpha)>1/2`, where
  `chi(alpha)=max(alpha/2,(1-alpha)/2)`.
- Surviving normal form: choose public `theta`, return the constant point
  `T=[theta]P`, and accept a randomized `Q_s=[s*x]P` exactly when
  `log_P(Q_s)^D=theta`. On acceptance, `[s^(-D)]T=[x^D]P`; the success density is
  `D/(ell-1)`. A compact coordinate-level exponent-coset tester would therefore be a
  genuine mechanism, not merely a solver swap.
- Exact failed controls: the sign-complete vanishing ideal and point table require
  `D` setup/state; generic orbit BSGS plus retries exceeds rho; division-polynomial and
  isogeny-kernel zero sets have additive subgroup structure and cannot select the
  intermediate multiplicative scalar coset in prime-order `G`.
- Scope boundary: no compact summation-polynomial, finite-field-extension, ECFFT,
  pairing, isogeny, or arithmetic-circuit membership recurrence is supplied. Degree
  alone is not used as a circuit lower bound, and H047's exponent-DH wording is not
  promoted to an unconditional impossibility theorem.
- Producer receipt SHA-256:
  `7ad6ee0d5a038dbb086eb32d65e40cda79cba20bf2288c0bee473e9e96c2fc0f`.
- Exactly one next action: independently audit
  `ideas/artifacts/ECDLP-IDEA-003/correspondence_spec.md`; only a passing audit may
  freeze a successor whose sole positive is a sign-complete exponent-coset membership
  circuit below the stated setup, query, Cheon, and memory gates.
- Boundary: a sharper missing primitive and corrected cost model are not an auxiliary
  point, ECDLP recovery, generic-prime Shoup-bound improvement, or breakthrough.

### ECFG-P1530-R2 - Orbit-distinguisher literature correction

- Context: a primary-source audit compared P1530's constant-output survivor against
  Robert Gallant's 2010 type-1 set-orbit distinguisher. The R1 producer receipt remains
  immutable; this record corrects its novelty boundary without claiming independent
  verification or dispatching an experiment.
- Prior-art identification: on `ell-1=A*B`, Gallant's orbit
  `O_a={[alpha0^a*beta0^j]P}` with `ord(beta0)=B` equals
  `S_(D,theta)={[u]P:u^D=theta}` after `D=B` and
  `theta=(alpha0^a)^B`. Thus P1530's predicate
  `1[log_P(R)^D=theta]` is exactly the type-1 orbit indicator on Gallant's factor
  families. Arbitrary divisors remain scalar-subgroup orbits, although Gallant's stated
  recovery algorithm may require factor splitting when its coprimality hypothesis fails.
- Cost identity: Gallant's type-1 algorithm has
  `lambda_G=max(1-alpha,alpha/2,1-alpha+q)` for orbit size
  `B=ell^alpha` and indicator query exponent `q`. P1530's random-hit plus Cheon route
  has `lambda_P=max(1-alpha+q,chi(alpha))`. With `q=0`, both reach `1/3` at
  `alpha=2/3`; this oracle consequence is prior art. With generic orbit BSGS,
  `q=alpha/2` and `1-alpha/2>1/2` for every fixed `alpha<1`.
- Structured-generic check: treating free structure as confined to the orbit fraction
  `delta=B/ell`, the Corrigan-Gibbs-Henzinger-Wu model gives the sanity bound
  `Omega(min(sqrt(ell),1/delta))`; at `alpha=2/3` this is `ell^(1/3)`. The comparison
  is model-bound and is not an exact reduction from an arbitrary coordinate predicate
  to their partial-operation model.
- Operation screen: dense ideals/tables, generic orbit BSGS, x-only products,
  additive torsion tests, pairing transport, and summation-polynomial, FFE, or ECFFT
  backends without an explicit point-to-orbit intertwiner do not pass. A successor must
  publish a target-independent, sign-complete EC-coordinate type-1 distinguisher with
  setup exponent below `1/2`, query exponent below `alpha-1/2`, complete state and
  divisor-family costs, and final DLP recovery.
- Scoped status:
  `LITERATURE_CORRECTION_PASS__REDISCOVERY__NO_EXPLICIT_EC_TESTER`. No compact
  tester, auxiliary point, solver, fixture, generic-prime ECDLP algorithm, Shoup-bound
  improvement, or breakthrough was produced.
- Literature-correction receipt SHA-256:
  `4a2108cdad0445286fe4970e17ec16f34e70f0bbea314cad53d6d81861bd71b6`.
- Exactly one next action: independently audit the R1 producer and R2 literature
  correction as one package; only a passing audit may freeze a successor whose sole
  positive is an explicit sign-complete EC-coordinate Gallant type-1 distinguisher,
  potentially using summation-polynomial, FFE, or ECFFT machinery, with complete costs.
- Boundary: identifying a prior-art reduction and a narrower open primitive is not an
  ECDLP solution or breakthrough. P1530 remains queued, open, and unverified.

### ECFG-P1530-R3 - Independent R1-R2 audit and type-2 rerank

- Context: an independent theorem-only reconstruction checked the immutable P1530
  producer and literature correction from group definitions and primary-source cost
  formulas. No contract, point fixture, known logarithm, or experiment was used.
- Audit result: the rational-map, complete branch-trace, materialized-section retry,
  constant-output orbit, sign, and Gallant type-1 cost arguments pass in their stated
  scopes. The structured generic-group comparison is advisory only: a unary orbit label
  is not automatically an instance of that model's partial binary label operation.
- Type-1 disposition: the polynomial-time `ell^(1/3)` orbit consequence is Gallant
  prior art. Direct tables, dense ideals, and generic same-orbit work do not pass. No
  compact coordinate predicate or auxiliary point was produced, so P1530 is terminal
  `inconclusive`, independently audited, with the broader mathematical exception open.
- Type-2 successor: for an even order-`D` scalar subgroup `H`, the elliptic period
  `eta_H(R)=sum_(h in H/{+1,-1})x([h]R)` is invariant on `H` orbits. If it labels
  every orbit and has query exponent `q`, Gallant's type-2 cost is
  `max((1-alpha)/2,alpha/2,(1-alpha)/2+q)`; strict sub-rho time requires
  `q<alpha/2`.
- FFE gate: if a homomorphism defined over `F_(p^k)` intertwines `[beta]` on the
  rational prime-order subgroup with `p`-Frobenius, then iteration gives
  `beta^k=1 mod ell`; hence `D=ord(beta)` divides `k`. Homomorphic Frobenius-cycle
  encoding therefore restores a degree-`D` payload.
- Endomorphism gate: a nonconstant global rational invariant `f o psi=f` cannot exist
  for an isogeny of degree greater than one because degrees multiply. Pointwise
  invariants modulo the finite subgroup ideal remain outside scope.
- Independent audit SHA-256:
  `e7dfae990f357da7d1f3f8503c06d6334323d925244d3803f2a002888081c402`.
- Exactly one next action: freeze a theorem-only P1531 partial elliptic-period type-2
  specification with an exact separation rule and one explicit sub-square-root transfer
  recurrence or a scoped no-candidate result; do not authorize a contract or fixture.
- Boundary: an independently audited no-candidate disposition and a sharper successor
  are not an ECDLP algorithm, generic-order result, Shoup-bound improvement, or
  breakthrough.

### ECFG-P1531-R1 - Cauchy elliptic-period type-2 producer gate

- Context: P1531 replaces the heuristic assumption that one unweighted elliptic period
  separates rational scalar cosets with a proved public randomized label. It remains a
  theorem-only producer record and has not been independently audited.
- Exact label: for each orbit polynomial
  `F_u(Z)=product_(h in H/{+1,-1})(Z-x([u*h]P))`, use three public Cauchy traces
  `F_u'(c_i)/F_u(c_i)`, with tagged poles. Distinct even-`H` orbits have disjoint
  squarefree root sets. For each pair the logarithmic-derivative collision polynomial is
  nonzero of degree at most `D-2`.
- Separation bound: a union bound over `A=(ell-1)/D` orbits and three independent
  public constants gives probability at most
  `A^2((D-2)/p)^3/2=ell^(-(1-alpha)+o(1))` that any two orbit labels collide, assuming
  a cryptographic-size prime subgroup with subpolynomial cofactor. Final DLP
  verification detects a bad public setup.
- Cost rectangle: Gallant type-2 recovery requires
  `lambda=max(c,(1-alpha)/2,alpha/2,(1-alpha)/2+q)` and
  `mu=max(m,(1-alpha)/2,alpha/2)`. At `alpha=1/2`, the promotion cap requires
  `c<=0.45,q<=0.20,m<=0.30`; strict sub-rho time requires `q<1/4`.
- Failed producer controls: direct period summation has `q=alpha`; natural subgroup and
  orbit-polynomial recurrences retain `D` distinct leaves; Semaev equations do not
  aggregate the Cauchy weights; homomorphic FFE needs degree divisible by `D`; a
  low-degree endomorphism has no nonconstant global invariant; ECFFT lacks a
  multiplicative-scalar-to-additive-fiber intertwiner.
- Scoped status: `SCOPED_NO_PASS__OPEN_CAUCHY_PERIOD_TRANSFER_OPERATOR`. The open
  operation is a target-independent arithmetic circuit evaluating all three tagged
  traces with `q<alpha/2`, not the already proved separator or Gallant reduction.
- Producer specification SHA-256:
  `b59775a7fa5329df780c3a4aa8d453c585ae5782139a3f01d46ba571fc9d682a`.
- Exactly one next action: independently audit the separation polynomial, union bound,
  sign condition, type-2 cost rectangle, subgroup-tree leaf count, and degree-`D`
  FFE proof; only then may one explicit summation-polynomial or ECFFT transfer recurrence
  be frozen, and no contract or toy fixture is authorized.
- Boundary: a rigorous orbit-label separator without a sub-square-root evaluator is not
  a sub-rho ECDLP algorithm or breakthrough.

### ECFG-P1531-R2 - Independent audit and batched-label rerank

- Context: an independent theorem-only reconstruction checked the P1531 separator,
  probability bound, sign quotient, Gallant type-2 interface, and every producer control.
  No known logarithm, orbit table, contract, or experiment was used.
- Audit result: distinct orbit polynomials give a nonzero logarithmic-derivative
  collision polynomial of degree at most `D-2`; three public traces fail to separate
  with probability at most `ell^(-(1-alpha)+o(1))`. The type-2 cost rectangle and
  `q<alpha/2` independent-query gate pass.
- Square-root Velu control: granting the most favorable additive index system, automatic
  differentiation of the elliptic polynomial evaluator computes one Cauchy trace in
  `D^(1/2+o(1))`. Gallant then costs
  `ell^((1-alpha)/2)D^(1/2)=ell^(1/2+o(1))`, exactly rho. The two-set resultant model
  cannot be rebalanced below square root because it covers at most
  `2|I||J|+|K0|` roots.
- Fourier control: multiplicative character orthogonality expresses the orbit trace as
  `A` elliptic Fourier modes. A nonzero normalized mode transforms by `chi(u)^(-1)` on
  input `[u]P`, so it is a Gallant type-1 distinguisher. Classical universal Gauss-sum
  powers erase that orientation, while direct mode materialization retains linear
  torsion payload.
- Isogeny control: an isogeny nonzero on the prime subgroup is injective there. It cannot
  map `[h]R` and `R` to the same point for nontrivial `h`, so additive-kernel Velu or
  ECFFT isogenies cannot collapse a multiplicative scalar orbit.
- Rerank: Gallant actually requests two structured batches of `K=sqrt(A)` labels. If the
  complete base and target batches have exponents `c_B,b_B`, the repeated-query term is
  replaced by `max(c_B,b_B)`. A hypothetical row-preserving
  `sqrt(KD)` evaluator has exponent `(1+alpha)/4`, equal to `3/8` at
  `alpha=1/2`; no such evaluator is supplied.
- Independent audit SHA-256:
  `67561fc763a2909c71ba6ca5017deb59d3be302e385a391dca18b07ef0bddc61`.
- Exactly one next action: freeze P1532's theorem-only row-preserving batch interface and
  independently audit one transposed resultant or quotient recurrence with
  `c_B,b_B<1/2`, or record a scoped no-candidate disposition. No contract or fixture is
  authorized.
- Boundary: P1531 is terminal `inconclusive` at the independently audited scoped level.
  The batch cost opportunity is `novelty-unverified`, not an algorithm, Shoup-bound
  improvement, or breakthrough.

### ECFG-P1532-R1 - Row-preserving batched type-2 producer gate

- Context: P1532 changes the cost unit from one orbit label to the exact two
  `K=ceil(sqrt(A))` label vectors required by Gallant's outer collision stage. Every row
  and source index must survive; a union product or checksum is not sufficient.
- Batch rectangle: if the public base batch, target batch, and state have exponents
  `c_B,b_B,m_B`, then
  `lambda=max(c_B,b_B,(1-alpha)/2,alpha/2)` and
  `mu=max(m_B,(1-alpha)/2,alpha/2)` before a justified low-memory collision variant.
- Controls: direct rows cost exponent `(1+alpha)/2`; `K` independent square-root Velu
  calls cost exactly `1/2`; a union product loses row identity; product-ring packing pays
  one base-field operation per row; and Fourier tags restore the type-1 hidden-character
  gate.
- Positive target: emit the six row generating polynomials for the three public traces on
  the base and challenge batches using a transposed elliptic resultant, quotient
  q-holonomic recurrence, batched Semaev eliminant, or nonhomomorphic cyclic-algebra
  trace with `c_B,b_B<1/2` and all row, pole, applicability, collision, recovery, and
  memory costs charged.
- Scoped status: `SCOPED_NO_PASS__OPEN_ROW_PRESERVING_BATCH_TRANSFER`. No admitted
  construction currently supplies the row-preserving operation.
- Producer specification SHA-256:
  `2ddd84829b8f110675545764aea4e30a699af9552b94c58fa4d474b89f40af43`.
- Exactly one next action: independently audit the P1532 cost model and either derive one
  explicit row-preserving recurrence or transposed resultant below the batch gate, or
  sign a scoped no-candidate disposition. Do not authorize a contract, solver, or toy
  fixture.
- Boundary: amortizing a hypothetical label interface is not a sub-rho ECDLP algorithm,
  generic-order result, Shoup-bound improvement, or breakthrough.

### ECFG-P1532-R2 - Independent audit and output-gate correction

- Context: an independent theorem-only reconstruction checked the exact Gallant batch,
  batch rectangle, direct and square-root controls, recurrence route, row-tag transfer,
  and complete collision recovery. No experiment or solver was used.
- Audit result: the cost rectangle passes, but ordered row output is sufficient rather
  than necessary. Public random affine compression of the three P1531 traces has false
  cross-collision probability at most `K^2/p=ell^(-alpha+o(1))`; characteristic
  polynomials or direct intersection resultants can replace ordered rows if deterministic
  subdivisions recover both source indices and final scalar verification is retained.
- Recurrence control: the complete quotient row functions have disjoint pole sets in the
  Cauchy variable. They are constant-linearly independent, every cyclic Fourier mode is
  nonzero, and any symbolic constant-coefficient recurrence has order at least `A`.
  Generic q-holonomic N-th-term algorithms do not supply a variable-coefficient elliptic
  recurrence or its coefficients.
- Transfer control: the row multiplier lives in `F_ell`, not `F_p`; a formal row tag does
  not parameterize scalar multiplication over the base field. Tagged Semaev elimination
  retains `K` chains and `K*D` leaves unless a genuinely new transfer identity is given.
- Balanced CRT control: when `A=A_1*A_2` is a balanced coprime split, both Gallant
  batches can be complete multiplicative-subgroup orbits. Simple nested orbit labels
  followed by independent quotient search still cost
  `sqrt(K)*sqrt(DK)=sqrt(ell)` exactly.
- Independent audit SHA-256:
  `fec71dc29a264a08e19208e41195f2fb25922b0ccfa2e51038f384e521b6d2e5`.
- Exactly one next action: freeze P1533's theorem-only collision-recovering multiset
  resultant and independently derive one balanced-subgroup relative resultant or direct
  cross-resultant below rho, or record a scoped no-candidate disposition. No contract,
  solver, or toy fixture is authorized.
- Boundary: P1532 is terminal `inconclusive` after a required scope correction. The
  corrected interface is `novelty-unverified`; it is not an algorithm or breakthrough.

### ECFG-P1533-R1 - Collision-recovering multiset resultant producer gate

- Context: P1533 replaces six ordered row-generating polynomials with the weakest exact
  Gallant interface found in the audit: a characteristic-polynomial family, direct
  cross-resultant, or equivalent relative norm that decides label-set intersection and
  deterministically recovers one base and one target source index.
- Compression and poles: on a pole-free setup a public affine hash of the three traces
  has total false-cross-collision probability at most `K^2/p`. An admitted operation must
  instead carry projective numerator/denominator tags or return an aggregate bad-setup
  bit and charge resampling. Every candidate is finally checked by `[x]P=Q`.
- Cost gate: with complete base, target/recovery, and state exponents `c_C,b_C,m_C`,
  `lambda=max(c_C,b_C,(1-alpha)/2,alpha/2)`. A subset primitive costing
  `sqrt(nD)^(1+o(1))` supports geometric bisection in `O(sqrt(KD))`; at
  `alpha=1/2` the target is exponent `3/8`, with promotion caps
  `c_C,b_C<=0.45` and `m_C<=0.30`.
- Frozen controls: a full-batch collision bit without source recovery, `K` independent
  label calls, degree-`K*D` materialization, unit-cost product-ring arithmetic,
  low-order constant recurrences, cross-characteristic row substitution, hidden Fourier
  orientation, and uncharged balanced-factor generation all fail.
- Scoped status: `SCOPED_NO_PASS__OPEN_COLLISION_RESULTANT`. No explicit relative norm,
  characteristic-polynomial constructor, or direct cross-resultant meets the gate.
- Producer specification SHA-256:
  `f9eb2ae215d75cce9684e8d2fde7d4a94e6ce36a9a8787eec8a5614ea1a8f337`.
- Exactly one next action: independently audit the P1533 direct-resultant interface and
  write one balanced-subgroup resultant through to base-field degrees and source
  recovery, or sign a scoped no-candidate disposition. Do not authorize a contract,
  solver, or toy fixture.
- Boundary: a collision-certificate target is not an ECDLP algorithm, generic-order
  result, Shoup-bound improvement, or breakthrough.

### ECFG-P1533-R2 - Independent derivative-resultant and norm audit

- Context: an independent theorem-only audit reconstructed the balanced CRT batches,
  affine-compression and pole model, direct resultant, split coordinate algebra,
  source-localization recursion, union-gcd control, and complete time and memory path.
  No experiment, solver, contract, or elliptic fixture was used.
- Balanced collision: writing `xH=x_1*x_2` in `J_1 x J_2` gives exactly one true
  cross equality, at base source `x_1` and target source `x_2^(-1)`, conditioned on
  the charged pole-free and no-false-hash branch.
- Tautological predicate: the full scalar resultant is zero for every valid challenge,
  because every balanced batch pair has one intersection. A full-set zero bit therefore
  contains no scalar information and cannot localize either source.
- Exact witness identity: for
  `R(t,s)=product_(i,j)((1+s)u_i-v_j+t)` with one simple common root `z`,
  `z=(dR/ds)(0,0)/(dR/dt)(0,0)`. This recovers the compressed common label without
  ordered rows if the derivatives can be evaluated.
- Cost boundary: explicit derivatives, orbit-coordinate relative norms, Fourier
  representations, structured subdivision membership, and high-multiplicity union
  collision all require rho-scale work or a denser payload in the audited
  representations. At `alpha=1/2`, the best complete tested time exponent is `1/2`;
  the hypothetical `sqrt(KD)` operation remains unconstructed.
- Independent audit SHA-256:
  `0de12da09c1bc49aa577431cff5ac09a264a367bce57aa1699c495015c28803f`.
- Exactly one next action: preserve P1533 terminal inconclusive and independently audit
  IDEA-158's four theorem gates, focusing on whether the induced sparse x-only
  five-source template has one target-independent support/witness recurrence within
  the declared setup, query, exact-source, rank, and blind-descent budgets. Do not
  implement a CSP solver or authorize the review-required contract.
- Boundary: the derivative identity and scoped no-candidate receipt are not an ECDLP
  algorithm, generic-order result, Shoup-bound improvement, or breakthrough.

### ECFG-P1534-R1 - Independent induced-template WNU router audit

- Context: an independent theorem-only audit reconstructed IDEA-158's full-`S3`,
  high-arity affine, strict affine-`S4`, and fixed-branch lift-invariance gates. It
  then wrote one exact FFE support operation and one favorable `2+3` support split
  through source recovery and complete costs. No contract, solver, finite-field
  fixture, relation campaign, or toy run was used.
- Theorem disposition: all four producer gates pass in their stated scopes. Every
  full fixed-arity rational-point Kummer summation relation pp-interprets faithful
  addition, while an invariant fixed signed-branch family is empty or full. An
  induced factor-base WNU remains logically possible and is not closed by the
  ambient theorem.
- Access dichotomy: ambient `S6` plus factor-base unary relations has cheap tuple
  membership but no admitted sparse-base WNU. Supplying the induced target relation
  extensionally already supplies the desired decompositions; keeping it implicit
  turns each local-consistency projection into the missing residual restricted-sum
  support and witness query.
- Explicit FFE attempt: with `F(T)` the factor-base root polynomial, multiplication
  by `S6(T_1,...,T_5,x(R))` in the fivefold tensor quotient is singular exactly on
  supported target fibers. The algebra has `B^5=N` coordinates. A `2+3` flattening
  permits `B^2` pair setup but retains a target-dependent `B^3` triple side, giving
  one-target exponent `3/5` and `B`-target campaign exponent `4/5`.
- Source correction: after a valid x-tuple is found, exact signed lifting at arity
  five costs at most `2^5` checked branches plus fixed exceptional-chart handling.
  The asymptotic missing operation is x-support, not the final sign enumeration.
- Independent audit SHA-256:
  `6a2c96f41552f91ab6d6ddc4801d6e4f958cf5845f6f81676de7f4db89653c53`.
- Recommended disposition:
  `INDEPENDENT_SCOPED_AUDIT_PASS__DEFERRED_INDUCED_TEMPLATE_ROUTER_NOT_SUPPLIED`.
  The residual operation is P1515's nonlinear implicit-batch/source-router class;
  IDEA-158 supplies no semantically distinct recurrence, rank path, or blind descent.
- Exactly one next action: preserve P1534 as deferred and independently audit
  `ideas/artifacts/ECDLP-IDEA-159/non_diagonal_polar_theorem.md`; either give one
  nonordinary target-independent representation with a compact exact
  source-component rule and complete sub-rho cost, or sign a scoped no-candidate
  receipt. Do not construct a Rees algebra or authorize its review-required contract.
- Boundary: WNU identities, exact FFE predicates, source lifting, and scoped deferral
  are not an ECDLP algorithm, generic-order result, Shoup-bound improvement, or
  breakthrough.

### ECFG-P1535-R1 - Independent nonordinary source-component audit

- Context: an independent theorem-only audit reconstructed IDEA-159's ordinary
  generic-stalk Rees trichotomy and screened explicit derived, stacky,
  noncommutative, Azumaya, Hopf-Galois, free-field, and conductor escapes. No
  Rees algebra, solver, contract, relation campaign, or toy run was used.
- Ordinary theorem: at each reduced irreducible generic component the local ring
  is a field, so a coherent ideal is zero or unit there. Proper centers alter only
  their support, Cartier centers blow up trivially, and componentwise zero/unit
  choices are source advice unless a compact public rule constructs them.
- Explicit nonordinary attempt: for the split five-source factor algebra
  `A_5=(F_p[T]/F)^(tensor 5)` of dimension `D=B^5`, the noncommutative algebra
  `End(A_5)=M_D(F_p)` has many noncanonical rank-one projectors. The exact source
  projectors are precisely the primitive idempotents of the embedded commutative
  algebra `A_5`; retaining them restores the original source split, while dense
  matrix representation has `B^10` entries.
- Exact finite-field residue: for
  `g_R=S6(T_1,...,T_5,x(R))`, the element `chi_R=1-g_R^(p-1)` is the exact
  Cartesian x-source indicator. `Tr(chi_R)` counts supported tuples and, for a
  singleton fiber, the five traces `Tr(T_i*chi_R)` return its coordinates.
  Constant `2^5` sign checking then gives exact signed lifts.
- Cost boundary: explicit projector or trace construction costs `B^5`; reusable
  `2+3` costs `B^3` setup/state; streaming costs `B^3` per target and `B^4` per
  relation campaign. A succinct exact trace circuit is not ruled out. To pass at
  `B=N^(1/5)`, it must have setup and memory at most `B^2.25` and per-target query
  at most `B^1.25`, before rank and descent costs.
- Independent audit SHA-256:
  `5d054c32e9cc60de1b5ab0742182e4932fee4c25a4338d07acc893b6c4307712`.
- Recommended disposition:
  `INDEPENDENT_SCOPED_AUDIT_PASS__NONORDINARY_NO_CANDIDATE__FROBENIUS_MOMENT_SUCCESSOR`.
  The broad nonordinary existence claim remains open; no explicit P1535 object
  passes.
- Exactly one next action: audit P1536's exact Frobenius-projector moments as a
  concrete P1514 structured-constructor successor. Derive a tensor-contraction,
  transposed power-projection, modular-composition, or FFE recurrence inside the
  `B^2.25/B^1.25` rectangle, or freeze a scoped no-candidate receipt. Do not run
  the retired P1514 verifier or authorize a solver.
- Boundary: the projector identity, six supplied traces, exact tuple recovery, and
  scoped deferral are not an ECDLP algorithm, generic-order result, Shoup-bound
  improvement, or breakthrough.

### ECFG-P1536-R1 - Independent Frobenius-projector and norm-jet audit

- Context: an independent theorem-only audit reconstructed the exact projector,
  trace moments, quotient dimension, split routes, generic triangular-set
  algorithms, current kSUM-indexing control, special decks, and extension-field
  return obligations. No contract, retired verifier, solver, point fixture,
  relation campaign, or toy run was used.
- Append-only symmetry correction: on five copies of one factor deck, `S6` is
  symmetric. A generic all-distinct x-source therefore contributes all `5!=120`
  ordered permutations. The P1535 six-trace singleton formula is exact only on a
  true singleton and is generically inapplicable to this same-deck support. For one
  complete orbit, `M_(j*e_1)=(r/5)*sum_i a_i^j`, `j=1,...,5`, recovers the
  unordered multiset after the moments are constructed.
- Coloured repair: five public disjoint colour decks retain a rainbow all-distinct
  source with constant probability `5!/5^5` under the favorable random-support
  model and remove permutation copies. Rank, signed-row distribution, failures,
  and every colouring remain charged.
- Exact norm-jet residue: for the coloured split algebra, let
  `R(t,s)=Norm(g_R+t+sum_i s_i*T_i)`. A simple coloured support satisfies
  `R(0)=0`, `dR/dt!=0`, and
  `a_i=(dR/ds_i)/(dR/dt)`. Empty support has nonzero constant term; support size
  at least two makes the complete first jet vanish. Constant `2^5` sign checks
  then recover every signed lift on the accepted simple branch.
- Cost screen: the quotient has dimension `B^5`; direct determinant, adjugate,
  norm, resultant, Poteaux-Schost triangular power projection, and dense trace
  routes retain that scale. Reusable or streamed `2+3` retains `B^3` state or
  query work. The 2026 kSUM-indexing theorem has `B^5` preprocessing for a
  five-source query and excessive advice. Multiplicative-subgroup decks are
  prime-family restricted and lose their monomial form after rational-point
  filtering; no FFE route supplies a generic rational-source return.
- Independent audit SHA-256:
  `81ec3515b584c36a809c155b5f26127bce91c09d7bfe6bccc425cdef07d51393`.
- Recommended disposition:
  `INDEPENDENT_SCOPED_AUDIT_PASS__NO_TRACE_RECURRENCE__COLOURED_NORM_JET_SUCCESSOR`.
  P1536 is terminal inconclusive so its narrower successor is dependency-valid;
  the broader arbitrary structured-constructor claim remains deferred and open.
  The exact coloured jet is a sharper output interface, not a qualifying
  constructor or complete ECDLP path.
- Exactly one next action: audit P1537's jet-preserving compositional-deck
  intertwiner bound to IDEA-195. Require an explicit target-independent map whose
  first coloured norm jet contracts before the `B^5` Cartesian product, a bounded
  exact source inverse, generic-prime applicability, setup and memory at most
  `B^2.25`, query at most `B^1.25`, full rank, factor logs, and masked descent.
  Do not run the retired IDEA-195 contract or authorize a solver.
- Boundary: projector correctness, a norm derivative identity, a coloured simple
  source, and scoped deferral are not a relation campaign, factor-log solve, blind
  descent, generic-order result, Shoup-bound improvement, or breakthrough.

### ECFG-P1537-R1 - Independent compositional norm-jet transport audit

- Context: an independent theorem-only audit reconstructed the P1536 coloured
  first jet, IDEA-195 non-Cartesian map requirement, P1478 sparse-transition
  boundary, and P1526-P1528 ECFFT/Lattes controls. No contract, retired verifier,
  solver, finite-field fixture, relation campaign, or toy run was used.
- Exact transport theorem: over
  `D=F_p[e_0,...,e_5]/(e)^2`, determinant-norm transitivity through any finite
  rational deck tower preserves the norm constant and all six derivatives. For
  each parent block, the seven channels are one product plus six
  product-excluding-one sums. If the global coloured support is a singleton, the
  unique zero block and ratios `j_i/j_0=a_i` persist through every level.
- Constructor boundary: blockwise evaluation starts with `B^5` leaves. Sequential
  elimination returns a dense resultant and a balanced cut returns `B^3` state.
  Norm transitivity is therefore the exact transport interface, not its compact
  evaluator; no degree or dimension statement is promoted as a universal circuit
  lower bound.
- Descent/multiplicity correction: if the Semaev relation itself factors through
  a nontrivial deck map, one parent zero pulls back to its whole accepted fiber.
  The local norm then has first nonzero homogeneous degree equal to the fiber size,
  so its constant and complete first jet vanish. Keeping one leaf per fiber is
  injective and gives no compression; selecting a favorable leaf after the target
  is source advice.
- Structured-map screen: a Lattes map induced by `[m]` is a permutation on the
  rational prime subgroup when `gcd(m,N)=1`, while a full geometric five-source
  parent relation has `|E[m]|^4=m^8` signed lifts. ECFFT leaves live on an
  auxiliary curve; a target-compatible morphism returns to an isogeny, and
  filtering or hashing leaves destroys the intertwiner. Power/Dickson decks need
  smooth-order families, and homomorphic extension-field return is trivial or
  duplicates projected columns.
- Independent audit SHA-256:
  `5b0112a1efc6043150d998fb1c38217c602a00186f7982443aaab7a443acf249`.
- Recommended disposition:
  `INDEPENDENT_SCOPED_AUDIT_PASS__EXACT_LOCAL_JET_TRANSPORT__NO_COMPACT_GENERIC_DECK__FINITE_STATE_CLOSURE_SUCCESSOR`.
  P1537 is terminal inconclusive; exact source transport survives, but no admitted
  realization meets setup/state `B^2.25` and query `B^1.25`.
- Exactly one next action: audit P1538's bounded-state local-norm renormalization
  gate bound jointly to IDEA-195 and IDEA-102. Require an explicit finite-field
  star-triangle, Yang-Baxter, transfer, or other identity closed under all seven
  channels for a public rational deck, exact conditioned leaf-source recovery,
  and complete sub-rho costs. Do not run either retired contract, construct a
  solver, or generate a toy fixture.
- Boundary: exact norm transitivity, derivative-ratio source preservation, a
  compact formula for one block, or a structured-map no-candidate receipt is not
  a relation campaign, factor-log solve, blind descent, generic-order result,
  Shoup-bound improvement, or breakthrough.

### ECFG-P1538-R1 - Independent bounded-state local-norm closure audit

- Context: an independent theorem-only audit reconstructed P1537's exact
  seven-channel update, IDEA-102's finite-field integrability gate, the exact
  IDEA-001 rank/density theorem, IDEA-050's source-complete matchgate control, and
  the concurrent IDEA-242/IDEA-253 norm-tower and MPS records. No contract,
  retired verifier, solver, finite-field fixture, relation campaign, or toy run
  was used.
- Exact positive control: the seven-channel message is multiplication in
  `D=F_p[e_0,...,e_5]/(e)^2`, so associativity and commutativity give exact
  finite-field regrouping and preserve singleton source ratios. The seed still
  has `Theta(B^5)` leaf messages; fixed value-space dimension is not compressed
  domain construction.
- Projector correction: a proper nonempty diagonal factor-base projector does
  not commute with every regular translation and therefore breaks local closures
  that require that centrality. A projector placed only on boundary source legs
  may leave the bulk Yang-Baxter/star-triangle identity intact. The prior blanket
  indicator-breaks-integrability wording is too broad; the boundary branch is
  screened by state, conditioning, and density instead.
- Linear transfer theorem: the exact endpoint-versus-source incidence flattening
  has rank `S=|F_1+...+F_5|`. Every explicit target-uniform linear transfer,
  tensor cut state, retained character list, or vectorized matrix pairing has at
  least `S` represented components. Reducing a seven-channel dual-number transfer
  to its constant channel preserves this lower bound.
- Cost gate: if `U` is the simple accepted endpoint set, then `|U|<=S`; even with
  one independent row per accepted endpoint, collecting `B` rows needs at least
  `B*N/S` attempts. Explicit state plus attempts costs at least
  `max(S,B*N/S)>=sqrt(B*N)=N^0.6` for `B=N^0.2`, before source conditioning,
  rank defects, factor logs, descent, verification, output, or memory traffic.
- Scope limit: the theorem closes explicit linear transfer/cut-state components,
  translation-regular interior projectors, reassociation of the local norm, and
  supplied matchgate/Pfaffian/MPS tensors. It does not lower-bound nonlinear
  arithmetic recurrences, implicit target batches, multirow source generators,
  or a new finite-field factor-base defect equation. None is explicitly supplied.
- Concurrent semantic deduplication: IDEA-242 repeats P1537's norm-transitivity,
  first-jet, composition-tower, and bounded-inverse operation and is consumed as
  a duplicate/control. The concurrent file is preserved unchanged.
- Independent audit SHA-256:
  `2a25ed9ed8eef5518229752a5c439c515255eb810bc01f99e7f0987531b52174`.
- Recommended disposition:
  `INDEPENDENT_SCOPED_AUDIT_PASS__VALUE_SPACE_CLOSURE_EXACT__INTERIOR_PROJECTOR_BREAKS_TRANSLATION_CLOSURE__BOUNDARY_LINEAR_TRANSFER_FAILS_RANK_DENSITY__NONLINEAR_IMPLICIT_RECURRENCE_UNSUPPLIED`.
  P1538 is terminal inconclusive and IDEA-102/IDEA-195 return to
  theorem-deferred status; no further integrability successor is admitted without
  explicit mechanism-new equations.
- Exactly one next action: rerank the focus queue outside the exhausted
  integrability/transfer naming family. Reopen only on an explicit nonlinear
  seven-channel recurrence or finite-field factor-base defect equation with an
  endpoint compiler, exact source inverse, and complete sub-rho costs. Do not run
  either retired contract or any concurrent retired preflight.
- Boundary: value-space closure, an exact projector commutator, a rank/density
  receipt, or a scoped no-candidate disposition is not a relation campaign,
  factor-log solve, blind descent, generic-order result, Shoup-bound improvement,
  or breakthrough.

### ECFG-P1539-P0 - Abel-Jacobi evaluation-minor producer gate

- Context: the post-P1538 semantic rerank returns to active IDEA-012, but replaces
  its aspirational aggregate-section oracle with one exact genus-one predicate
  compiler. The producer read the complete active/deferred/rejected corpus controls
  and bound the result to IDEA-014, IDEA-052, P1515, and P1538. No contract,
  verifier, solver, finite-field fixture, relation campaign, or toy run was used.
- Exact target interface: for
  `L_R=O_E((m-1)O+R)`, Riemann-Roch gives `h^0(L_R)=m`. Distinct points
  `A_1,...,A_m` sum to `R` if and only if their `m` evaluation rows on a public
  basis of `H^0(L_R)` form a singular square minor. Repeated points require
  confluent evaluation jets; ordinary duplicate rows are false positives.
- Five-colour specialization: five disjoint signed factor decks give five public
  target-dependent `B x 5` row blocks. An exact rainbow decomposition is a
  singular transversal `5 x 5` minor containing one row from every block. The
  matrix compiler has `Theta(B)` represented field elements for fixed arity, but
  its `B^5` possible minors remain implicit.
- Complement correction: factoring the canonical union-factor-base section as
  `sigma_F=sigma_D*sigma_C` with `sigma_D in H^0(L_R)` is biconditional to the
  same supported divisor/minor. Complement duality changes degree and target class
  but does not select the source divisor.
- Semantic controls: standard AG-code decoding consumes a received word or
  syndrome; P1539 instead seeks an unknown weight-five dual word in a
  target-dependent evaluation code. Source-labelled wedge/Pfaffian forms restore
  `B^2/B^3` split catalogues, direct `2+3` search has `B^3` target work, generic
  kSUM indexing has excessive setup, and an explicit all-target linearization
  returns to P1538.
- Favorable gate: at `B=N^0.2`, constant five-source density and `B` required rows,
  target-matrix construction and a nonlinear zero-minor locator must each cost at
  most `B^1.25`; setup and resident state must be at most `B^2.25`, with complete
  `lambda,mu<=0.45`. A `B^2` per-target locator gives `B^3=N^0.6` and fails.
- Producer receipt SHA-256:
  `99227d06594cc50395b368dbef1da602085fc07a9e9a9f39e117682b991c4263`.
- Producer disposition:
  `UNREVIEWED_EXACT_INTERFACE__COLOURED_DECOMPOSITION_IFF_SINGULAR_EVALUATION_MINOR__COMPLEMENT_FACTORIZATION_EQUIVALENT__SUB_B1_25_ZERO_MINOR_LOCATOR_UNSUPPLIED`.
  This exact thin-matrix interface is the sole queued candidate and awaits
  independent theorem review.
- Exactly one next action: independently reconstruct the line-bundle,
  determinant, confluent-jet, and complement equivalences, then derive one explicit
  elliptic-normal-curve singular-transversal-minor locator inside the focus
  rectangle or sign a scoped no-candidate receipt. Do not approve or execute the
  IDEA-012 contract, construct a solver, or generate a toy fixture.
- Boundary: a thin predicate matrix, singular supplied minor, section
  factorization identity, or source row is not relation rank, factor-log recovery,
  blind descent, a generic-order improvement, Shoup-bound improvement, or
  breakthrough.

### ECFG-P1539-R1 - Abel-Jacobi minor-locator independent disposition

- Context: an independent theorem-only audit reconstructed the P1539 producer,
  the exact direct and batched source costs, the current 2026 kSUM-indexing
  positive control, and the prior generalized-birthday correction gates. No
  contract, verifier, solver, finite-field fixture, relation campaign, or toy run
  was executed.
- Evaluation theorem: the genus-one determinant biconditional is exact on the
  distinct-point stratum, and restriction to a length-five divisor gives the
  correct confluent-jet interface for multiplicities. Five ordinary `B x 5`
  blocks are an all-strata compiler only under a disjoint simple-colour policy;
  copied colours need tuple-dependent jet orders.
- Translation theorem: for prime subgroup order `N!=5`, put
  `T=[5^(-1) mod N]R`. Then
  `O_E(4O+R) ~= tau_(-T)^* O_E(5O)`, and each target row is projectively
  equivalent to the fixed degree-five embedding row at `A-T`. In short
  Weierstrass coordinates the fixed basis `{1,x,y,x^2,xy}` is point-injective.
- Semantic consequence: a singular five-colour transversal minor is exactly the
  ordinary coloured elliptic query `A_1+...+A_5=R`. The target line bundle,
  elliptic code, normal-curve hyperplane, and complement section do not provide a
  second target geometry or a witness oracle.
- Explicit cost controls: `2+3`, `3+2`, and `4+1` use respectively
  `(state,query)=(B^2,B^3),(B^3,B^2),(B^4,B)`. Treating the `B` known targets as
  a sixth colour gives a balanced `3+3` campaign of `B^3=N^0.6` work, above the
  `B^2.25=N^0.45` cap.
- Current indexing control: Dinur-Golovnev arXiv:2512.04258v2 treats this as
  `k=6` indexing and gives `S=soft-O(B^(5.5-delta))`,
  `T=soft-O(B^delta)`, with `soft-O(B^5)` preprocessing. Its query-cap regime
  and the simpler four-sum table both require state at least `B^4`; grouping
  pairs into 3SUM indexing requires `B^4.75` advice at the P1539 query cap.
  These are positive-algorithm comparisons, not unconditional lower bounds.
- Representation screen: known-scalar neutral masks create valid extra source
  representations, but an exact Wagner filter needs a proper composable quotient.
  IDEA-057 proves no such quotient on the prime-order subgroup; coordinate
  prefixes lose cancellation, and the Kummer trace/norm repair is the recursive
  `S3` resultant with source leaves restored.
- Scope limit: arbitrary list-specific nonlinear finite-field locators remain
  outside the proved negatives. No explicit one meets setup/state `B^2.25`, query
  `B^1.25`, exact row output, relation rank, factor logs, and masked descent.
- Independent audit SHA-256:
  `634e5a7d2847e849a2e46178f31500f19109e9a9d88a2bf8c70d1f0afe4d467a`.
- Recommended disposition:
  `INDEPENDENTLY_VERIFIED_EXACT_EVALUATION_INTERFACE__TARGET_BUNDLE_TRANSLATES_TO_FIXED_COLOURED_5SUM__PUBLISHED_INDEXING_AND_WAGNER_CONTROLS_MISS_B2_25_B1_25_RECTANGLE__NONHOMOMORPHIC_LOCATOR_UNSUPPLIED__INCONCLUSIVE`.
  P1539 is terminal inconclusive; the exact predicate compiler is preserved and
  the broader existence claim remains open.
- Exactly one next action: rerank outside evaluation-minor, explicit kSUM, and
  exact generalized-birthday families. Audit active IDEA-011 against P1530-P1533
  and admit a P1540 scalar-orbit-period successor only if it names one distinct
  exact construction-or-degree operation. Do not draft or execute a contract,
  period table, or toy fixture.
- Boundary: a target translation theorem, fixed alternant, current-algorithm cost
  miss, or scoped no-candidate disposition is not relation rank, factor-log
  recovery, blind descent, a generic-prime below-rho algorithm, Shoup-bound
  improvement, or breakthrough.

### ECFG-P1540-R0 - Elliptic-net translated-pole annihilator producer gate

- Context: the focused rerank first compared active IDEA-011 with the complete
  P1530-P1533 scalar-orbit audit family. IDEA-011's coordinate sum is the first
  elementary symmetric coefficient of the same scalar-orbit polynomial, and its
  subgroup-chain recursion is the same relative-trace tower. It is semantically
  consumed and receives no successor slot.
- Routed root: P1540 instead audits IDEA-006's rank-two elliptic-net short
  annihilator. The existing execution contract remains `review_required`; no
  contract, implementation, verifier, point fixture, rank sweep, or experiment
  was run.
- Exact net interface: Stange's identity
  `W(v)^2 W(w)^2 (x(v.P)-x(w.P))=-W(v+w)W(v-w)` gives a
  gauge-invariant bridge from rank-two net ratios to the translated coordinate
  orbit. For `Q=[x]P`, `W(a,1)=0` exactly at `a=-x mod N`; fast value
  evaluation is not a locator for that index.
- Metric correction: for every scalar sequence, the standard Hankel displacement
  `Z_m H-H Z_n^T` is supported only on the first row and column and has rank at
  most two. This metric is a boundary identity, not sequence compression, and
  the random negative control passes it identically.
- Translated-pole theorem: the functions `f_n(R)=x(R+[n]P)` have distinct
  double poles at `-[n]P` and are linearly independent. More strongly, a
  constant-coefficient recurrence on any length-`M` consecutive finite block
  has order at least `ceil((M-2)/3)`; the complete finite subgroup orbit has
  order at least `ceil((N-3)/3)`. The proof counts `M-r` zeros against at most
  `2(r+1)` poles.
- Scope: the theorem closes constant-coefficient translated-x annihilators and
  ordinary low-Hankel-rank interpretations. It does not close a compact
  variable-coefficient recurrence, nonlinear target state machine, short local
  signature with a global locator, or another gauge-invariant net observable.
- Eigenvalue boundary: a Fourier shift ratio is `zeta^(j*x)`; labeling it is an
  order-`N` finite-field DLP unless a separately charged transfer algorithm is
  supplied. Returning an eigenvalue is not direct index recovery.
- Producer SHA-256:
  `d9a4040230022c24f7011932ef7cd9b5bcea51236a80c042bb498d2012428437`.
- Producer disposition:
  `UNREVIEWED_SCOPED_SYMBOLIC_NO_GO__STANDARD_HANKEL_DISPLACEMENT_RANK_IS_TAUTOLOGICAL__CONSECUTIVE_TRANSLATED_X_BLOCKS_HAVE_LINEAR_COMPLEXITY_AT_LEAST_(M-2)/3__FULL_ORBIT_ORDER_AT_LEAST_(N-3)/3__TARGET_SPECIFIC_NONLINEAR_LOCATOR_UNSUPPLIED__OPEN`.
- Exactly one next action: independently reconstruct the net identity, Hankel
  displacement calculation, and both pole theorems; then name one
  gauge-invariant nonlinear or variable-coefficient locator with direct scalar
  recovery and complete `lambda,mu<=0.45`, or return P1540 terminal
  inconclusive. Do not execute or revise the IDEA-006 contract during review.
- Boundary: a metric correction, linear-complexity lower bound, recurrence
  identity, or scoped no-go is not target recovery, a generic-prime sub-rho
  algorithm, a Shoup-bound improvement, or breakthrough.

### ECFG-P1540-R1 - Elliptic-net locator independent disposition

- Context: an independent theorem-only audit reconstructed the P1540 net,
  displacement, pole, nonlinear-state, rational-linearization, Fourier, EDS, and
  Lax/QRT controls. The `review_required` IDEA-006 contract was not revised or
  executed; no implementation, fixture, rank sweep, or experiment was created.
- Producer reconstruction: Stange's net quotient is gauge invariant and
  `W(a,1)=0` is the target relation location. Standard Hankel displacement rank
  is at most two for every sequence. The translated functions have distinct
  double poles, and a length-`M` consecutive finite block has constant linear
  complexity at least `ceil((M-2)/3)`.
- Novelty correction: translated-rational-function zero/pole arguments for
  elliptic sequence linear complexity are established prior art. The P1540
  finite-block constant is retained as an exact specialization, not a novel
  mechanism or breakthrough result.
- Nonlinear-state theorem: for `P=(u,v)` on `y^2=x^3+A*x+B`, the adjacent state
  `(X,Y)=(x(R),x(R+P))` lies on the fixed Semaev biquadratic and rationally
  recovers `R`. It obeys
  `F_P(X,Y)=(Y,2*(f(Y)+f(u))/(Y-u)^2-2*Y-2*u-X)`, with
  `F_P o phi_P=phi_P o tau_P`. After projective completion this QRT map is
  birationally conjugate to translation by `P` on the original curve.
- Index consequence: the nonlinear state is constant-dimensional but is an
  exact encoding of the original ECDLP orbit. State conversion and inversion
  cost `O(1)` field operations; an iterate-index decoder transfers one-for-one
  to ECDLP. Fast recurrence evaluation is not index location.
- Rational screen: a nonconstant multiplicative translation eigenfunction has
  translation-invariant divisor and therefore at least one full `N`-point pole
  orbit. A prime-to-characteristic additive coordinate has zero increment and
  factors through the degree-`N` quotient. This closes low-degree rational
  additive/multiplicative linearization, not arbitrary succinct nonlinear
  circuits.
- Route screen: Fourier output retains an order-`N` field DLP; EDS discrete log
  isolates the same index-location problem; a QRT Lax pair packages the same
  genus-one translation. Periodic public coefficients and arbitrary
  list-specific nonlinear locators remain logically open but are unsupplied.
- Independent audit SHA-256:
  `8032be2d3a645ac64c046783191cc9c634715518eb18e4702acf66e077223d45`.
- Recommended disposition:
  `INDEPENDENTLY_VERIFIED_SCOPED_NO_GO__NET_RATIO_AND_TRANSLATED_POLE_BOUNDS_RECONSTRUCT__LINEAR_COMPLEXITY_METHOD_IS_PRIOR_ART__CONSTANT_DIMENSION_NONLINEAR_STATE_IS_QRT_TRANSLATION_CONJUGATE_TO_E__LOW_DEGREE_RATIONAL_ADDITIVE_OR_MULTIPLICATIVE_LINEARIZATION_REQUIRES_A_FULL_N_ORBIT_DIVISOR__NO_DIRECT_INDEX_DECODER__INCONCLUSIVE`.
  P1540 is terminal inconclusive and IDEA-006 remains open only for a
  mechanism-new direct locator outside the audited classes.
- Exactly one next action: rerank outside elliptic-net recurrence,
  translated-coordinate linear complexity, scalar-orbit period, QRT/Lax state,
  and Fourier eigenvalue families. Admit one exact mechanism-distinct
  construction or degree operation; do not execute the IDEA-006 contract.
- Boundary: a prior-art correction, QRT conjugacy, divisor-support gate, or
  scoped no-candidate disposition is not scalar recovery, relation rank,
  factor-log recovery, blind descent, a Shoup-bound improvement, or
  breakthrough.

### ECFG-P1541-R0 - Miller S-unit support-coset producer gate

- Context: the post-P1540 semantic rerank compared the remaining proposal
  fingerprints and admitted IDEA-007 only at its mechanism-distinct operation:
  finding a supported principal divisor rather than constructing or verifying
  one whose support coefficients are already known. No contract, executable,
  S-unit basis, lattice reducer, point fixture, or experiment was created.
- Kernel theorem: for public factor points `F_i` in the prime-order subgroup,
  the supported divisor `sum_i e_i*((F_i)-(O))` is principal exactly when
  `sum_i [e_i]F_i=O`. The exponent lattice `L` is the kernel of the
  Abel-Jacobi map `Z^B -> <P>`, has index and determinant `N`, and is the
  fixed-support function-field S-unit group modulo constants.
- Moving-target theorem: a function with divisor
  `(R)-(O)+sum_i e_i*((F_i)-(O))` exists exactly when
  `sum_i [e_i]F_i=-R`. Its coefficient vectors form one affine coset
  `e_0+L`. Multiplying by fixed-support S-units moves inside that coset and
  does not supply its first representative.
- Miller boundary: short line-function programs construct and verify the
  rational function after a terminal zero-sum relation is known. They reduce
  representation size but do not alter the kernel, target syndrome, support
  search, relation yield, or descent density.
- Full-kernel cost identity: a basis of the complete kernel determines the
  relative factor-base logs by Smith normal form. Including the public
  known-log anchor `P` fixes the quotient scale and recovers every factor-base
  log, so complete S-unit-basis construction already contains the factor-log
  solve and cannot be free preprocessing.
- Candidate-mass theorem: for any finite target-independent coefficient family
  `C` and uniform relation or blinded target input, average witness count is
  `|C|/N` and success probability is at most `min(1,|C|/N)`. Large candidate
  mass may create witnesses but still requires a nonenumerative decoder.
- Live exception: a compact arithmetic operation may conceivably decode the
  inhomogeneous syndrome into one admissible coefficient vector without
  materializing `C`, constructing the full kernel, or solving an order-`N`
  DLP. IDEA-007 supplies no equations or costed decoder for that operation.
- Producer SHA-256:
  `1d6ded9cdeedc411eda8d22c4c1b05c8fe1ed9409191e4f6ed0788d75471c7c5`.
- Producer disposition:
  `UNREVIEWED_EXACT_INTERFACE__SUPPORTED_PRINCIPAL_DIVISORS_ARE_THE_ABEL_JACOBI_KERNEL__TARGET_FUNCTIONS_FORM_AN_AFFINE_KERNEL_COSET__MILLER_PROGRAMS_CONSTRUCT_OR_VERIFY_AFTER_A_COSET_REPRESENTATIVE_IS_KNOWN__BOUNDED_COEFFICIENT_SUCCESS_IS_AT_MOST_CANDIDATE_MASS_OVER_N__STRUCTURED_COSET_DECODER_UNSUPPLIED__OPEN`.
- Exactly one next action: independently reconstruct the kernel, affine-coset,
  full-kernel factor-log, and candidate-mass theorems; then specify one exact
  implicit support-coset decoder with complete relation-to-descent output and
  `lambda,mu<=0.45`, or return P1541 terminal inconclusive. Do not draft or
  execute an IDEA-007 contract during review.
- Boundary: an S-unit basis, short Miller program, principal-divisor
  certificate, homogeneous relation, counting bound, or toy scalar is not a
  generic-prime sub-rho algorithm, a Shoup-bound improvement, or breakthrough.

### ECFG-P1541-R1 - Miller S-unit decoder independent disposition

- Context: an independent theorem-only audit reconstructed the P1541
  divisor-class, lattice, counting, differential, evaluation, and full-cost
  controls. No contract, implementation, curve fixture, S-unit basis, lattice
  run, relation campaign, factor-log solve, or target descent was created.
- Exact reconstruction: fixed-support principal divisors are the kernel
  `L=ker(Z^B -> <P>)`, with `Z^B/L ~= Z/NZ`. For a moving input `R`, all
  target functions form one affine coset `e_0+L`; multiplying by S-units moves
  inside that coset and does not find its first representative.
- Full-kernel theorem: including the known-log anchor `P`, a complete kernel
  basis determines the quotient map by Smith normal form and recovers every
  factor-base logarithm. Complete S-unit-basis construction is factor-log
  preprocessing, while partial relations retain their collection and rank
  costs.
- Miller boundary: line-function programs compactly construct and verify a
  rational function after the support coefficients and terminal zero sum are
  known. They do not select the support or change relation and descent density.
- Candidate-mass theorem: for a frozen finite coefficient family `C`, uniform
  relation and blinded-target witness count averages `|C|/N`, and success is at
  most `min(1,|C|/N)`. This is a witness-availability bound, not an enumeration
  or query lower bound.
- Cartier/dlog screen: residues of `df/f` recover divisor multiplicities only
  modulo `p`. Even granting global integration,
  `div(f)=D_res+p*D_hidden`; on the prime-to-`p` order-`N` lane,
  `[D_hidden]=-[p^(-1)]*[D_res]` can carry the entire target class. Excluding or
  recovering the invisible divisor restores the original support-coset problem.
- Other routes: multiplicative evaluations need finite-field logarithm labels;
  Riemann-Roch consumes chosen multiplicities; generic lattice, subset-sum,
  generalized-birthday, and summation-polynomial routes retain existing
  decomposition costs. No implicit structured decoder remains instantiated.
- Independent audit SHA-256:
  `0cd9b2a3e42056d61c4b365af626bbf0a21e2f8bb666ffb1da098c31755e26a5`.
- Recommended disposition:
  `INDEPENDENTLY_VERIFIED_SCOPED_NO_GO__SUPPORTED_PRINCIPAL_DIVISORS_ARE_THE_ABEL_JACOBI_KERNEL__MOVING_TARGETS_ARE_AFFINE_KERNEL_COSETS__ANCHORED_FULL_KERNEL_REVEALS_FACTOR_LOGS__MILLER_PROGRAMS_CONSUME_A_KNOWN_COSET_REPRESENTATIVE__CANDIDATE_MASS_BOUND_RECONSTRUCTS__CARTIER_DLOG_LOSES_AN_INVISIBLE_P_MULTIPLE_DIVISOR_CLASS__EVALUATION_LINEARIZATION_REQUIRES_FIELD_LOGS__NO_STRUCTURED_DECODER__INCONCLUSIVE`.
  P1541 is terminal inconclusive; IDEA-007 remains open only for a
  mechanism-new inhomogeneous decoder outside the audited classes.
- Exactly one next action: rerank outside fixed-support S-units, prescribed-
  divisor Miller programs, Cartier residues, generic decomposition, pairing
  evaluation, and prior elliptic-net/orbit lanes. Admit one exact
  mechanism-distinct construction or degree operation with a complete
  factor-base-to-target path.
- Boundary: an exact kernel, affine torsor, Smith-form reduction, residue
  obstruction, or scoped no-candidate receipt is not scalar recovery, relation
  rank, blind descent, a Shoup-bound improvement, or breakthrough.

### ECFG-P1542-R0 - Partial pairing lift-return geometry producer gate

- Context: the post-P1541 semantic rerank admits IDEA-008 only at its concrete
  outward-and-back operation. P1530 already controls the abstract scalar-power
  correspondence and Cheon recovery; P1542 requires construction of both a
  nondegenerate scalar-compatible second pairing lift and a certified return
  from selected pairing-target values. No contract, implementation,
  extension-field fixture, pairing run, return table, or Cheon campaign exists.
- Ordinary lift gate: when the rational and second `N`-torsion Frobenius
  eigenvalues are distinct, every geometric endomorphism of an ordinary
  elliptic curve commutes with Frobenius and preserves the rational eigenline.
  It cannot provide the distortion lift to the independent pairing direction.
  Auxiliary correspondences and low-embedding-degree special families remain
  outside this exact class.
- Rational return gate: every rational map from a connected algebraic torus to
  an elliptic curve is a homomorphism followed by translation, and every torus-
  to-abelian homomorphism is zero. A globally rational pairing-target return is
  therefore constant.
- Finite-domain degree theorem: if rational coordinates of degree at most `d`
  return points of a short Weierstrass curve on `M` distinct target values,
  clearing denominators gives a polynomial of degree at most `5d`. For
  `M>5d` it vanishes identically and defines a constant torus-to-`E` map.
  Hence every nonconstant explicit univariate return has `d>=ceil(M/5)`.
- Correspondence screen: complete branch traces from a finite cover define the
  same constant rational map. A survivor must select one nonsymmetric branch,
  with public equations, membership, certificate, branch density, failed
  attempts, and exact product-scalar output.
- Whole-cycle gate: the charged return density is the probability that every
  lift and return in the fixed `O(log N)` scalar-power circuit succeeds. Per-
  gate acceptance cannot replace the cycle exponent. Cheon's quarter-exponent
  term matters only after a valid auxiliary point is acquired.
- Scope limit: degree is not arithmetic-circuit size. Compact high-degree
  formulas using `z^N=1`, nonrational cover branches, auxiliary abelian
  correspondences, and correlated circuit-closed return domains remain open.
  No such operation is supplied.
- Producer SHA-256:
  `0fc5bc2796aab3f2a1daab8d3ec40b769b472f8c023cda2716677532bb2b7897`.
- Producer disposition:
  `UNREVIEWED_SCOPED_GEOMETRIC_NO_GO__ORDINARY_GEOMETRIC_ENDOMORPHISMS_PRESERVE_FROBENIUS_EIGENLINES_AND_DO_NOT_SUPPLY_A_DISTORTION_LIFT__RATIONAL_MAPS_FROM_A_PAIRING_TORUS_TO_E_ARE_CONSTANT__A_UNIVARIATE_RATIONAL_RETURN_VALID_ON_M_TARGET_VALUES_HAS_DEGREE_AT_LEAST_M_OVER_5__SYMMETRIC_CORRESPONDENCE_TRACE_IS_CONSTANT__COMPACT_HIGH_DEGREE_OR_NONSYMMETRIC_COVER_BRANCH_RETURN_UNSUPPLIED__OPEN`.
- Exactly one next action: independently reconstruct the eigenline, rational-
  map, finite-domain degree, correspondence-trace, and whole-cycle gates; then
  specify one compact high-degree or nonsymmetric-cover lift-and-return with
  complete `lambda,mu<=0.45`, or return P1542 terminal inconclusive. Do not
  draft or execute an IDEA-008 contract during review.
- Boundary: a distortion obstruction, constant rational map, degree floor,
  pairing value, returned toy product, or injected Cheon input is not a generic-
  prime sub-rho algorithm, a Shoup-bound improvement, or breakthrough.

### ECFG-P1542-R1 - Pairing lift-return independent disposition

- Context: an independent theorem-only audit reconstructed the P1542
  Frobenius, rational-map, finite-domain, correspondence, pairing-inversion,
  Fourier-support, extension, and whole-cycle controls. No contract,
  implementation, extension-field fixture, pairing run, return table, or Cheon
  campaign was created.
- Exact FAPI interface: for a nondegenerate pairing
  `e:G_1 x G_2 -> mu_N`, fixed generators `P,T` give isomorphisms
  `Phi_1(R)=e(R,T)` and `Phi_2(S)=e(P,S)`. The required cross-line lift is
  `Phi_2^(-1) o Phi_1`, or FAPI-1, and the source return is `Phi_1^(-1)`, or
  FAPI-2. Together they map `([a]P,[b]P)` to `[a*b]P`.
- Compact-graph boundary: equations `e(P,S)=z` and `e(R,T)=z` uniquely define
  and cheaply verify the two inverse fibers. Graph membership does not find the
  points; a correspondence certificate is not a return algorithm.
- Geometric reconstruction: ordinary same-curve endomorphisms preserve the
  rational Frobenius eigenline; rational maps from a torus to `E` and complete
  correspondence traces are constant; a nonconstant explicit degree-`d`
  rational-coordinate return on `M` targets has `M<=5d`.
- Fourier screen: after a public constant-extension shift avoiding the affine
  pole, the unique polynomial on `mu_N` representing the returned `x` sequence
  has at least `ceil((N-2)/3)` nonzero Fourier coefficients. This closes
  expanded sparse character sums, not straight-line, rational, or nonlinear
  circuits.
- Literature correction: Satoh's majorly revised 2025 preprint gives
  polynomial-time Miller inversion for reduced Tate pairings at every embedding
  degree greater than one. The older degree-about-`N` Miller-root obstruction is
  not retained. FAPI still requires a final-exponent preimage in the Miller image
  of the prescribed source domain, both inversion directions, and all extension
  costs.
- Cost boundary: materialized target state, embedding degree, EI, MI, lift,
  return, branch search, every failed full circuit, and Cheon recovery are
  charged. No compact prescribed-image EI or auxiliary branch supplies complete
  `lambda,mu<=0.45`.
- Independent audit SHA-256:
  `7ace892e881a36878d02e94381205ed2c85629ac35e3db9ab7dec8a16f9d83ea`.
- Recommended disposition:
  `INDEPENDENTLY_VERIFIED_SCOPED_NO_GO__ORDINARY_ENDOMORPHISM_EIGENLINE_GATE_RECONSTRUCTED__TORUS_RETURN_M_OVER_5D_AND_SYMMETRIC_TRACE_GATES_RECONSTRUCTED__LIFT_AND_RETURN_ARE_FAPI_1_AND_FAPI_2__REVISED_SATOH_MAKES_MILLER_INVERSION_POLYNOMIAL_BUT_DOES_NOT_SUPPLY_PRESCRIBED_IMAGE_EI__SHIFTED_RETURN_HAS_OMEGA_N_FOURIER_SUPPORT__PAIRING_EXTENSION_AND_WHOLE_CYCLE_COSTS_UNSUPPLIED__COMPACT_EI_OR_AUXILIARY_BRANCH_UNCLASSIFIED__INCONCLUSIVE`.
  P1542 is terminal inconclusive; IDEA-008 remains open only for a compact
  prescribed-image EI or auxiliary correspondence outside the audited classes.
- Exactly one next action: rerank outside ordinary distortion maps, global
  rational return, explicit interpolation, expanded Fourier return, symmetric
  covers, direct pairing inversion, and prior scalar-orbit families. Admit one
  exact mechanism-distinct source construction with a complete direct scalar-
  recovery path.
- Boundary: an efficiently verifiable FAPI graph, polynomial-time Miller
  inversion, Fourier-support floor, pairing value, or scoped terminal receipt is
  not scalar recovery, a Shoup-bound improvement, or breakthrough.

### ECFG-P1543-R0 - Global-lift torsion-or-defect producer gate

- Context: the post-P1542 semantic rerank admits IDEA-005 only at the missing
  height-compression operation. Xedni-style coordinate lifts, canonical curve
  lifts, EDS encodings, lattice-basis changes, and planted global relations are
  controls. No contract, Sage implementation, number-field catalog, lattice
  sweep, relation campaign, factor-log solve, or blind descent exists.
- Torsion-lift theorem: for good characteristic-zero reduction and `N!=p`,
  finite-etale Hensel lifting gives a unique local lift
  `t:G -> E(K_v)[N]`. It is a group homomorphism and preserves the scalar, but
  it is torsion, has zero canonical height, is killed by characteristic-zero
  logarithms, and retains the original order-`N` relation problem.
- Defect theorem: any non-torsion set section `s` reducing to the finite group
  has `u(R)=s(R)-t(R)` in the formal reduction kernel. A global lifted relation
  holds exactly when both `sum [e_i]F_i=R` and
  `sum [e_i]u(F_i)=u(R)` hold. The second equality is the local defect syndrome.
- Homomorphism gate: the formal kernel is pro-`p` and has no nontrivial
  `N`-torsion. A homomorphism from the prime order-`N` group into it is zero.
  Thus a scalar-compatible section is the torsion lift; every non-torsion
  section has a nonlinear defect that must be constructed and decoded.
- Density and Xedni controls: any frozen coefficient family has uniform lifted-
  witness probability at most `min(1,|C|/N)` before the defect can only reduce
  it. Under its stated Lang and discriminant-height assumptions, the fixed-
  arity Xedni analysis bounds dependent-lift coefficients by a constant and
  gives `O(1/N)` success. Growing structured bases remain outside that scoped
  theorem.
- Live exception: a target-independent non-torsion section could conceivably
  place all defect values in a compact family with a joint finite-and-local
  decoder. IDEA-005 supplies no such equations, rank path, blind descent, or
  complete bit cost.
- Producer SHA-256:
  `37288382aeabdf4ce43ae95a32f0c86e59dd9200dfbeb80654a89f765f4c1631`.
- Producer disposition:
  `UNREVIEWED_SCOPED_LIFT_DICHOTOMY__PRIME_TO_P_GROUP_COMPATIBLE_LIFT_IS_TORSION_AND_HEIGHT_ZERO__NONTORSION_SET_SECTION_CARRIES_A_FORMAL_GROUP_DEFECT_SYNDROME__GLOBAL_RELATIONS_MUST_CANCEL_BOTH_FINITE_AND_LOCAL_OFFSETS__XEDNI_FIXED_ARITY_DENSITY_CONTROL_PRESERVED__STRUCTURED_DEFECT_COMPRESSION_UNSUPPLIED__OPEN`.
- Exactly one next action: independently reconstruct the finite-etale torsion
  lift, torsion-or-defect biconditional, pro-`p` homomorphism gate, coefficient-
  family density, Xedni scope, and complete bit-cost model; then specify one
  non-torsion section with a direct joint defect decoder and
  `lambda,mu<=0.45`, or return P1543 terminal inconclusive. Do not draft or
  execute an IDEA-005 contract during review.
- Boundary: a canonical curve lift, torsion section, zero height, short toy
  vector, reduced global relation, or defect identity is not relation rank,
  factor-log recovery, blind descent, a Shoup-bound improvement, or
  breakthrough.

### ECFG-P1543-R1 - Global-lift independent disposition

- Context: an independent theorem-only audit reconstructed the good-reduction
  lift, exact defect, fixed-family density, Xedni, Mordell-Weil-coordinate, and
  complete-cost boundaries. No contract, point catalog, global field, lift
  implementation, lattice run, relation campaign, factor-log solve, or blind
  descent was created.
- Torsion and height correction: finite-etale lifting gives the unique local
  scalar-compatible order-`N` section. On the canonical ordinary curve, the
  elliptic Teichmuller lift is this same group section. Global Neron-Tate height
  is defined only after a global realization; every such realization remains
  torsion and has height zero.
- Exact defect interface: for `u(R)=s(R)-t(R)`, a lifted relation holds iff the
  finite syndrome and `sum [e_i]u(F_i)=u(R)` both hold. A homomorphic defect is
  zero because the formal kernel is pro-`p` and `N!=p`.
- First-jet gate: `E_1/E_2` is additive residue-field state and `[a]` acts as
  multiplication by `a mod p`. Thus `[N]` is invertible on the first defect jet
  for `N!=p`; it does not suppress arbitrary-lift noise as `[p]` does in the
  anomalous control. Formal logarithms expose the second syndrome but do not
  make it scalar compatible.
- Density scope: a frozen coefficient family still succeeds with probability at
  most `min(1,|C|/N)` before the defect can only remove witnesses. The Xedni
  `C_0/p` theorem reconstructs only under Lang, its discriminant-height
  comparison, and fixed arity `2<=r<=9`; growing correlated bases remain open.
- Mordell-Weil coordinate gate: expressing `s(R)` in a known free basis returns
  a coefficient vector whose reduction is already a multigenerator preimage of
  `R`. Heights, denominator ideals, EDS values, saturation, LLL/BKZ, and
  Mordell-Weil sieves can rank or test supplied candidates but do not construct
  the fresh target coordinates.
- Scope limit: a mechanism-new target-independent non-torsion section could
  conceivably give compact defect equations and a direct joint decoder. No
  unconditional lower bound against that class is claimed.
- Independent audit SHA-256:
  `d7654a1286a42e67cd0aa9b73020c04389a7072c08762ebd09ef66c0eeeefeba`.
- Recommended disposition:
  `INDEPENDENTLY_VERIFIED_SCOPED_NO_GO__FINITE_ETALE_SECTION_IS_TORSION_AND_GLOBAL_HEIGHT_ZERO__CANONICAL_TEICHMULLER_LIFT_IS_THE_SAME_GROUP_SECTION__NONTORSION_SECTION_HAS_EXACT_FORMAL_DEFECT_SYNDROME__PRIME_TO_P_MULTIPLICATION_DOES_NOT_SUPPRESS_FIRST_JET_DEFECT__FIXED_COEFFICIENT_AND_XEDNI_DENSITY_GATES_RECONSTRUCTED__MORDELL_WEIL_COORDINATES_REQUIRE_THE_ORIGINAL_PREIMAGE__STRUCTURED_DEFECT_DECODER_UNCLASSIFIED__INCONCLUSIVE`.
  P1543 is terminal inconclusive; IDEA-005 remains open only for a structured
  nonlinear defect section outside the audited named routes.
- Exactly one next action: rerank to the nonadditive IDEA-160 ramification lane
  and independently audit the existing generator-invariance theorem plus the
  oriented-branch exception. Do not execute either review-required contract.
- Boundary: a canonical point lift, formal defect, first-jet identity, short
  global vector, denominator factorization, height score, or sieve exclusion is
  not a complete relation system, scalar recovery, Shoup-bound improvement, or
  breakthrough.

### ECFG-P1544-R0 - Ramification oriented-branch audit assignment

- Context: P1543 closes additive and height-based lift routes within scope. The
  next mechanism-distinct lane is IDEA-160's nonlogarithmic local-field tower,
  already represented by the immutable P1517 producer theorem. This assignment
  creates no new tower, branch, contract, fixture, or run.
- Frozen producer: for nonzero `Q=[x]P` in a prime-order subgroup,
  `<Q>=<P>` and `K(Q)=K(P)`. Good-reduction prime-to-`p` torsion is unramified,
  and full torsion or division-fiber towers are layerwise generator invariant.
  Their ramification breaks, conductors, Herbrand functions, and field-of-norms
  data return no scalar digit.
- Exact open exception: selecting one nonfunctorial branch can vary with `Q`,
  but the public canonical selector, orientation cost, ambiguity, and typed
  return to `Z/NZ` are then the missing operation. Pure ramification data may
  not be credited for that selector.
- Producer theorem SHA-256:
  `33079fb5e6fef57fe6d4b21b65b82cba0eea9bcf6dcbbea1e2331df4978b24a7`.
- Assignment disposition:
  `QUEUED_THEOREM_ONLY__FUNCTORIAL_TOWER_GENERATOR_INVARIANCE_TO_RECONSTRUCT__GOOD_REDUCTION_UNRAMIFIED_BOUNDARY_TO_CHECK__FULL_DIVISION_FIBER_FIELD_EQUALITY_TO_CHECK__PUBLIC_ORIENTED_BRANCH_WITH_TYPED_SCALAR_RETURN_UNSUPPLIED__NO_RUN`.
- Exactly one next action: independently reconstruct every field-equality,
  unramified, full-fiber, field-of-norms, and cost statement; then specify one
  publicly canonical nonfunctorial branch with complete `lambda,mu<=0.45`, or
  return P1544 terminal inconclusive. Do not construct or time a tower.
- Boundary: a common tower, ramification break, selected toy branch, recovered
  toy digit, or theorem receipt is not generic-prime scalar recovery, a
  Shoup-bound improvement, or breakthrough.

### ECFG-P1544-R1 - Ramification oriented-branch independent disposition

- Context: an independent theorem-only audit reconstructed the generator-field,
  good-reduction inertia, full division-fiber, selected branch, field-of-norms,
  orientation, and complete-cost boundaries. The review_required IDEA-160
  contract remained unexecuted; no tower, branch fixture, scalar sample, or
  timing result was created.
- Common-field gate: for every nonzero `Q=[x]P`,
  `K(P)=K(Q)=K(<P>)=:F`. Good-reduction order-`N` torsion is unramified because
  `N!=p`, and full coprime fibers generate `F(E[a])`. Full order-`N` division
  fibers are also generator invariant.
- Selected-branch normal form: for `gcd(a,N)=1`, the public point
  `h_a(Q)=[a^(-1) mod N]Q` is a zero branch and every selected point is uniquely
  `R_a(Q)=h_a(Q)+T_a(Q)` with `T_a(Q) in E[a]`. Exact field equality
  `F(R_a(Q))=F(T_a(Q))` makes every selected-branch ramification invariant an
  invariant of a target-independent torsion offset.
- Affine orientation gate: `theta_Q(R)=[N]R` is an affine bijection from
  `[a]^(-1)(Q)` to `E[a]`. If aligned branches obeyed
  `R_a(Q)=[x]R_a(P)`, their labels would obey `theta_Q=[x]theta_P` and expose
  `x mod ord(theta_P)`. But `x` and `x+N` name the same input; well-definedness
  forces `[N]theta_P=O`, hence `theta_P=O` because `[N]` is invertible on
  `E[a]`. Choosing a nonzero representative-aligned label is exactly the digit
  oracle, not an output of ramification.
- Ramification-selector gate: a unique valuation, break, conductor, Frobenius
  stratum, canonical subgroup, or eligible field-of-norms extremum selects the
  same offset for every target. A tied target-dependent choice is an external
  nonramification selector. Classical field-of-norms language additionally
  requires an APF tower; the unramified order-`N` tower is not credited as one.
- Order-`N` gate: a branch above `Q` requires choosing a lift of `x mod N` to
  `x mod N^(m+1)`. The full level has `N^(2m)` branches and no positive
  ramification at the residue prime. A compact oriented lift remains an
  unsupplied scalar-coordinate operation.
- Scope limit: model-dependent coordinate root ordering can define an arbitrary
  small-range set map `Q -> E[a]`. No checked map has a typed scalar law,
  model-invariance rule, ambiguity bound, or complete sub-rho recovery path,
  but this audit does not prove all such nonhomomorphic maps hard.
- Independent audit SHA-256:
  `db68ae68e99952656db3c4b179b94770f73972f2429f240c579879ea0502782f`.
- Recommended disposition:
  `INDEPENDENTLY_VERIFIED_SCOPED_NO_GO__GENERATOR_AND_FULL_TOWER_FIELDS_ARE_COMMON__GOOD_REDUCTION_ORDER_N_TORSION_IS_UNRAMIFIED__COPRIME_DIVISION_BRANCH_IS_ZERO_BRANCH_PLUS_A_TORSION_OFFSET__SELECTED_BRANCH_FIELD_EQUALS_THE_TORSION_OFFSET_FIELD__THE_N_MULTIPLE_MAP_BIJECTS_BRANCHES_WITH_TORSION_LABELS__NONZERO_SCALAR_EQUIVARIANT_LABEL_IS_NOT_WELL_DEFINED_MOD_N__RAMIFICATION_ONLY_SELECTION_IS_TARGET_INDEPENDENT__ORDER_N_DIVISION_REQUIRES_A_SCALAR_LIFT_ORIENTATION__FIELD_OF_NORMS_APF_DOMAIN_CORRECTED__ARBITRARY_NONRAMIFICATION_SMALL_RANGE_SELECTOR_UNCLASSIFIED__INCONCLUSIVE`.
  P1544 is terminal inconclusive within the audited tower and selector classes;
  IDEA-160 remains open only for an explicit compact nonramification selector.
- Exactly one next action: rerank the active corpus outside additive lifts,
  global heights, full local-field towers, and torsion-orientation selectors,
  then bind one mechanism-distinct theorem question as P1545. Do not execute
  the IDEA-160 contract.
- Boundary: a common field, affine branch-label theorem, ramification stratum,
  fixed torsion offset, selected toy branch, or tiny torsion DLP after oracle
  alignment is not generic-prime scalar recovery, a Shoup-bound improvement, or
  breakthrough.

### ECFG-P1545-R0 - Trace-zero cross-encoding transfer audit assignment

- Context: P1544 closes local full-tower, ramification-only selected-branch, and
  exact torsion-equivariance routes within scope. The next mechanism-distinct
  active lane is IDEA-009's global transfer into a trace-zero variety followed
  by summation-polynomial decomposition. This assignment creates no transfer,
  trace-zero fixture, factor base, relation, contract, or run.
- Frozen algebraic predecessor: independently replayed P1501 records that a
  rational map from an elliptic curve to an abelian variety is a translate of a
  homomorphism, ordinary geometric endomorphisms commute with Frobenius, and the
  tested bounded algebraic/divisor correspondences preserve or kill the rational
  order-`N` Frobenius line rather than move it into trace zero. The four arithmetic
  cells are toy; the exact morphism and module statements must be separated from
  the finite catalog.
- Exact open operation: publish a pointwise evaluator
  `tau(Q)=[x]tau(P)` for `Q=[x]P` in a second order-`N` trace-zero encoding,
  without a source or target DLP, oracle eigendirection, scalar table, pairing
  inversion, or target-derived advice. Merely defining the unique cyclic-group
  isomorphism does not evaluate it.
- Index-calculus gate: even a valid evaluator must place its image on a
  target-independent recognizable locus whose trace-zero Semaev/FFE relation
  collection, independent rank, factor-log solve, and separate blind masked
  descent have complete `lambda,mu<=0.45`. A representation change or generic
  trace-zero relation is not enough.
- Hash-bound inputs:
  - IDEA-009 root:
    `7fabf5c4fa94353908eb4e1dbf61dfab9b768ce28f8f391b25e69ff994f8e240`;
  - P1501 producer:
    `97949bb077a932d777dd10e25f11050a2e326060e5112f45868f6080473978c3`;
  - P1501 independent audit:
    `b0b912521ff0b4568c3214fdd482ef22a1a19015f38f10302d1b66daca5cb61c`;
  - P1515 overlap audit:
    `7e7609716f87b1b4df5ffc77406a912ad0303cc309ec1b84be42ebcc0d09539e`;
  - P1544 independent audit:
    `db68ae68e99952656db3c4b179b94770f73972f2429f240c579879ea0502782f`.
- Assignment disposition:
  `QUEUED_THEOREM_ONLY__P1501_ALGEBRAIC_AND_FROBENIUS_BOUNDARY_TO_RECONSTRUCT__TWO_GROUP_GENERIC_EVALUATOR_GATE_TO_PROVE__EXPLICIT_COORDINATE_TRANSFER_UNSUPPLIED__TRACE_ZERO_SUMMATION_POLYNOMIAL_IMAGE_LOCUS_UNSUPPLIED__COMPLETE_RELATION_TO_TARGET_COST_UNSUPPLIED__NO_RUN`.
- Exactly one next action: write
  `ideas/artifacts/ECDLP-IDEA-009/p1545_trace_zero_cross_encoding_gate.md`.
  Reconstruct P1501 and the independent-encoding generic boundary, then name one
  explicit presentation-stable nonalgebraic evaluator plus a source-invertible
  trace-zero locus and complete cost, or return P1545 terminal inconclusive. Do
  not draft, approve, or execute an IDEA-009 experiment.
- Boundary: a valid algebraic theorem, abstract cyclic isomorphism, oracle
  off-diagonal map, trace-zero point, Semaev relation, FFE solve, factor row, or
  recovered toy scalar is not a generic-prime below-rho algorithm, a Shoup-bound
  improvement, or breakthrough.

### ECFG-P1545-R1 - Trace-zero cross-encoding independent disposition

- Independent audit: the algebraic P1501 boundary reconstructs. A rational map
  from the source elliptic curve to an abelian target is a fixed translation plus
  a homomorphism. On an ordinary curve every geometric endomorphism commutes with
  Frobenius, so the rational order-`N` line remains fixed and trace is `[k]`; when
  `gcd(k,N)=1`, algebraic trace-zero transfer kills that line.
- Piecewise gate: if one rational branch has form `t_i+phi_i` and is correct for
  two distinct source scalars, subtraction forces `phi_i(P)=tau(P)` and then
  `t_i=0`. It is already the forbidden global transfer. Every other fixed branch
  covers at most one scalar, so an explicit complete catalog has state exponent
  one. Compact adaptive branch predicates remain outside this theorem.
- Cross-encoding gate: with independent generic source and target encodings,
  source labels have form `a+bX` while target labels remain known constants.
  Only a source collision can reveal `X`; the standard collision count gives
  constant-success work `Omega(sqrt(N))`. This is not a lower bound against an
  explicit finite-field coordinate operation.
- Cost gate: published fixed-degree trace-zero index calculus has base-field cost
  `p^(2-2/(k-1)+o(1))` for `k>=3`, hence at least `N^(1+o(1))` relative to the
  prime-field source subgroup. An oracle transfer into the full trace-zero
  variety is therefore source-rho worse. A useful successor needs both a compact
  nonalgebraic evaluator and a source-invertible special image locus.
- Backend screen: Frobenius polynomials, Lang/Frobenius preimages, root ordering,
  endomorphisms, pairings, interpolation, summation polynomials, FFE, Groebner
  bases, resultants, and learning do not supply both missing operations under the
  frozen interface. Backend substitution alone is not a new transfer.
- Independent audit SHA-256:
  `7bdfcbd66e2e559f38d91fece064b19c262d94ac26278a1ee290bb9c41841184`.
- Recommended disposition:
  `INDEPENDENTLY_VERIFIED_SCOPED_NO_GO__RATIONAL_TRANSFER_IS_TRANSLATE_OF_A_HOMOMORPHISM__ORDINARY_GEOMETRIC_ENDOMORPHISMS_COMMUTE_WITH_FROBENIUS__ALGEBRAIC_TRACE_ZERO_TRANSFER_KILLS_THE_RATIONAL_ORDER_N_LINE__EACH_NONPASSING_PIECEWISE_ALGEBRAIC_BRANCH_COVERS_AT_MOST_ONE_SCALAR__INDEPENDENT_GENERIC_CROSS_ENCODING_NEEDS_SQUARE_ROOT_WORK__LANG_AND_FROBENIUS_PREIMAGE_ROUTES_REQUIRE_A_BRANCH_OR_EXCEPTIONAL_MODULE__FULL_TRACE_ZERO_INDEX_CALCULUS_IS_SOURCE_RHO_WORSE__SUMMATION_POLYNOMIAL_AND_FFE_BACKENDS_DO_NOT_CONSTRUCT_THE_TRANSFER__ARBITRARY_ADAPTIVE_COORDINATE_EVALUATOR_AND_SPECIAL_IMAGE_LOCUS_UNCLASSIFIED__INCONCLUSIVE`.
  P1545 is terminal inconclusive within the audited algebraic, fixed-branch,
  independent-generic, Frobenius/Lang, full-trace-zero, and backend classes.
- Exactly one next action: rerank to IDEA-002 and bind a P1546 theorem-only audit
  of split-Jacobian conorm projected smoothness before its `review_required`
  300 CPU-hour contract can be considered. Do not implement or execute it.
- Boundary: a transfer definition, trace-zero point, valid Semaev relation,
  full-variety complexity improvement, toy factor row, or toy scalar is not a
  generic-prime sub-rho algorithm, Shoup-bound improvement, or breakthrough.

### ECFG-P1546-R0 - Split-Jacobian projected-smoothness theorem assignment

- Context: P1545 closes ordinary algebraic trace-zero transfer, fixed rational
  branch catalogs, independent generic cross-encoding, and full trace-zero
  decomposition within scope. IDEA-002 instead embeds the source through conorm
  into a split Jacobian and claims a special projected divisor distribution.
- Exact theorem question: for a bounded-degree cover `pi:C->E`, explicit
  `i=pi^*`, `n=pi_*`, and `n*i=[d]`, determine whether decomposing `i(Q)` over a
  target-independent divisor-atom base can asymptotically increase the count of
  source-complete projected relations after atoms, fibers, kernel terms, norm
  images, and duplicate E columns are charged. A valid norm identity is only the
  starting representation.
- Required receipt: separate multiplicity upstairs from distinct projected
  E-factor support; derive the best information-theoretic relation count by
  divisor arity, factor-base size, cover degree, genus, and admissible-cover
  density; then charge independent rows, factor logs, sparse linear algebra, and
  blind target descent. State exactly which distributional step remains heuristic.
- Hash-bound inputs:
  - IDEA-002 root:
    `76b0857c718388cc1e054b09362952b9e2dab5874af6eca8b8a316e1bbbf4ffc`;
  - review-required contract:
    `9c45c941f88c5f4c4743e64904644eafabe39c15d8e1ae047b7fef72211ca342`;
  - P1545 independent audit:
    `7bdfcbd66e2e559f38d91fece064b19c262d94ac26278a1ee290bb9c41841184`.
- Assignment disposition:
  `QUEUED_THEOREM_ONLY__CONORM_NORM_AND_SPLIT_FACTOR_IDENTITIES_TO_RECONSTRUCT__UPSTAIRS_ATOM_MULTIPLICITY_VERSUS_DISTINCT_PROJECTED_SUPPORT_TO_SEPARATE__PROJECTED_RELATION_COUNT_AND_SOURCE_CERTIFICATE_BOUND_TO_DERIVE__FIXED_DEGREE_AND_GROWING_GENUS_COSTS_TO_CHARGE__BLIND_DESCENT_PATH_UNSUPPLIED__REVIEW_REQUIRED_CONTRACT_NOT_AUTHORIZED__NO_RUN`.
- Exactly one next action: write
  `ideas/artifacts/ECDLP-IDEA-002/p1546_projected_smoothness_counting_gate.md`.
  Produce one theorem-only receipt with a complete relation-to-target cost or a
  sharply scoped gap. Do not create Sage code, cover fixtures, relation rows, or
  run artifacts, and do not execute the IDEA-002 contract.
- Boundary: existence of a cover, split Jacobian, correct conorm/norm map,
  reduced divisor, projected relation, toy smoothness advantage, or backend speed
  is not generic-prime recovery, a Shoup-bound improvement, or breakthrough.

### ECFG-P1546-R1 - Split-Jacobian projected-smoothness independent disposition

- Exact geometry: `pi_*pi^*=[d]` on the source Jacobian, and the degree-`g`
  Abel map `C^(g)->J(C)` is birational on a dense open. Fixing a cover,
  kernel dither, and reduction chart therefore gives a rational divisor branch
  from the embedded E line into a symmetric power of `C`.
- Sparse capture theorem: the universal support incidence of any nonconstant
  branch has a component of finite degree `Delta` over `C`. For an atom set of
  size `B_up`, at most `Delta*B_up+O(1)` source points have branch output wholly
  supported on that set. For bounded geometry, `Delta=N^o(1)`.
- Projected support: a degree-`d` cover has at most `d` upstairs rational atoms
  above one E-factor image. After zero and duplicate columns are removed,
  `B_up<=d*B+O(d)`. Fiber multiplicity is not logarithmic rank.
- Work conservation: one fixed branch succeeds on only
  `O(Delta*d*B)` of `N` source scalars. Even granting valid independent rows,
  `B` factor-log relations require `Omega(N/(Delta*d))` branch evaluations and
  blind target descent requires `Omega(N/(Delta*d*B))`. An explicit dither
  catalog raises coverage and evaluation work together; a full incidence table
  reaches linear state.
- Quotient and known-log gates: an arbitrary residual `K in ker(pi_*)` is
  equivalent to the projected E relation and verifies rather than locates it.
  Tuple-first atom sums have public E endpoints but unknown source logarithms;
  reversing the query is the direct target-local E sum problem.
- Standard full-Jacobian index calculus costs at least `N^(1+o(1))` relative
  to the frozen prime-field source. Classical cover attacks in the reviewed
  source apply to DLPs over non-prime extension fields, not this family.
- Independent audit SHA-256:
  `f64cc45b05cc74364d87eec69f54ecda79100274c0b498103a6492fa61c62702`.
- Recommended disposition:
  `INDEPENDENTLY_VERIFIED_SCOPED_NO_GO__CONORM_NORM_RELATIONS_PROJECT_TO_DIRECT_E_RELATIONS__DEGREE_G_ABEL_MAP_IS_BIRATIONAL_ON_A_DENSE_OPEN__FIXED_REDUCTION_BRANCH_IS_A_BOUNDED_DEGREE_CORRESPONDENCE__ONE_BRANCH_CAPTURES_ONLY_O_B_SPARSE_ATOM_TARGETS__FINITE_COVER_FIBERS_GIVE_ONLY_BOUNDED_PROJECTED_MULTIPLICITY__EXPLICIT_DITHER_BRANCHES_CONSERVE_COVERAGE_AND_WORK__FIXED_BRANCH_RELATION_COLLECTION_IS_LINEAR_AND_BLIND_DESCENT_IS_N_OVER_B__ARBITRARY_KERNEL_RESIDUAL_IS_A_TAUTOLOGICAL_PROJECTED_CERTIFICATE__TUPLE_FIRST_RELATIONS_LACK_KNOWN_SOURCE_LOGS__STANDARD_JACOBIAN_INDEX_CALCULUS_IS_SOURCE_RHO_WORSE__GROWING_DEGREE_OR_IMPLICIT_TARGET_ROUTER_UNCLASSIFIED__INCONCLUSIVE`.
  P1546 is terminal inconclusive within bounded covers, fixed algebraic
  reduction branches, explicit dithers, quotient certificates, tuple-first
  catalogs, and the frozen contract. Compact growing-degree or adaptive routers
  remain outside scope.
- Exactly one next action: rerank to IDEA-004 and bind P1547 as a theorem-only
  prime-to-`p` jet-coordinate audit. Do not execute the IDEA-002 or any jet
  experiment.
- Boundary: a correct cover, smooth reduced divisor, projected relation,
  kernel certificate, fixed-branch count, or toy target is not generic-prime
  recovery, a Shoup-bound improvement, or breakthrough.

### ECFG-P1547-R0 - Prime-to-p jet-coordinate theorem assignment

- Context: P1546 closes bounded cover reduction and explicit quotient dithers
  within scope. IDEA-004 instead seeks an additive scalar coordinate in a
  finite-order deformation or Witt jet. Its claimed target is `ell`-primary,
  while the native infinitesimal lift kernels are `p`-primary for `ell!=p`.
- Exact theorem question: classify every admitted finite-order jet module and
  lift-change direction; prove whether multiplication by `ell` is invertible;
  then determine whether any functorial additive functional on `<P>` can be
  nonzero. If an `ell`-primary target is adjoined, identify its public basis,
  construction, point evaluator, and scalar-coordinate inverse without
  importing the original torsion orientation or DLP.
- Controls: rejected IDEA-140 gives the exact p-typical de Rham-Witt vanishing
  argument; P1543 gives finite-etale prime-to-`p` torsion lifting and the first
  formal-defect normal form; JET/JETB provide toy evidence that free first-order
  tangent screens are zeroth-order-equivalent. None alone classifies every
  constrained higher-order or nonadditive jet operation.
- Hash-bound inputs:
  - IDEA-004 root:
    `e18a697e37a98855e475f9415ea076eac164eccfe060ec87b0c4f6acac6e76dc`;
  - IDEA-140 exact scoped rejection:
    `9616d6f2deee662ca6376a7e26b966be526acb4bf2929daa37182f26c4d4e13b`;
  - P1543 independent audit:
    `d7654a1286a42e67cd0aa9b73020c04389a7072c08762ebd09ef66c0eeeefeba`;
  - JETB evidence:
    `a8887d69dea9a664d7399f5e62448267d8cebc2720a5783dfc60924994fbde2a`;
  - P1546 independent audit:
    `f64cc45b05cc74364d87eec69f54ecda79100274c0b498103a6492fa61c62702`.
- Assignment disposition:
  `QUEUED_THEOREM_ONLY__FINITE_ORDER_DEFORMATION_TARGETS_TO_CLASSIFY__PRIME_TO_P_MULTIPLICATION_INVERTIBILITY_TO_PROVE__ADDITIVE_JET_COORDINATE_EXPECTED_ZERO__FINITE_ETALE_TORSION_LIFT_CONTROL_TO_RECONSTRUCT__FREE_FIRST_JET_SIMULATION_TO_SEPARATE_FROM_CONSTRAINED_HIGHER_JETS__EXPLICIT_ELL_PRIMARY_MODULE_AND_BASIS_UNSUPPLIED__NO_RUN`.
- Exactly one next action: write
  `ideas/artifacts/ECDLP-IDEA-004/p1547_prime_to_p_jet_coordinate_gate.md`.
  Produce one theorem-only receipt with a typed target and complete direct
  scalar-recovery cost or a sharply scoped no-go. Do not implement or execute a
  jet preflight.
- Boundary: an anomalous-curve reproduction, canonical torsion lift, tangent
  identity, nonzero toy residue, or correct toy scalar is not generic-prime
  recovery, a Shoup-bound improvement, or breakthrough.

### ECFG-P1547-R1 - Prime-to-p jet-coordinate independent disposition

- Native target theorem: for a finite nilpotent thickening, the reduction
  kernel has a finite filtration whose quotients are characteristic-`p`
  tangent modules. Multiplication by `ell!=p` is invertible on every quotient
  and therefore on the kernel. The same unit argument applies to formal,
  truncated Witt, p-complete p-typical, crystalline, and additive
  arithmetic-differential targets.
- Additive vanishing: any requested scalar law `J([n]R)=[n]J(R)` makes `J`
  additive on the order-`ell` source line. Since `[ell]` is invertible on the
  admitted native targets, `J(P)=0`. A nonlinear formula does not escape this
  conclusion if it retains the requested scalar law.
- Torsion-lift normal form: prime-to-`p` torsion lifts uniquely finite-etale.
  Given any lift `R_tilde`, invert `[ell]` on its formal defect and subtract
  that defect to recover the unique torsion lift. Its formal coordinate is
  zero; non-torsion sections store only p-primary lift error.
- First and higher jets: free first-jet consistency is the tangent space of the
  zeroth-order relation. Higher finite additive jets retain the same filtered
  prime-to-`p` vanishing. JET/JETB remain toy controls and are not needed for
  the theorem.
- Escape audit: adjoining `E[ell]`, etale cohomology, an abstract cyclic
  module, or a pairing target preserves or moves the DLP unless a public basis
  and orientation are supplied; generic pairing routes must also charge the
  embedding extension and finite-field DLP. A typed nonadditive point invariant
  remains outside scope, but IDEA-004 supplies none.
- Independent audit SHA-256:
  `bfdeb57b686ade5c4a3db1c99d0f4fde3f1d193bb7becb7f4703bc7381a5b2b9`.
- Recommended disposition:
  `INDEPENDENTLY_VERIFIED_SCOPED_NO_GO__FINITE_NILPOTENT_JET_KERNEL_HAS_P_PRIMARY_FILTRATION__MULTIPLICATION_BY_ELL_IS_INVERTIBLE_ON_NATIVE_JET_FORMAL_AND_P_TYPICAL_TARGETS__EVERY_ADDITIVE_ORDER_ELL_IMAGE_IN_THOSE_TARGETS_IS_ZERO__PRIME_TO_P_TORSION_LIFTS_UNIQUELY_FINITE_ETALE__CANONICAL_TORSION_LIFT_HAS_ZERO_FORMAL_DEFECT__NON_TORSION_SECTIONS_STORE_ONLY_P_PRIMARY_LIFT_ERROR__FREE_FIRST_JET_CONSISTENCY_IS_ZEROTH_ORDER_TANGENT_DATA__HIGHER_FINITE_ADDITIVE_JETS_DO_NOT_ESCAPE__ADJOINED_ELL_TORSION_REIMPORTS_BASIS_OR_ORIENTATION__ETALE_COHOMOLOGY_AND_PAIRING_ROUTES_MOVE_THE_DLP_OR_REQUIRE_NON_GENERIC_EMBEDDING_COST__NONADDITIVE_TYPED_SCALAR_INVARIANT_UNCLASSIFIED__INCONCLUSIVE`.
  P1547 is terminal inconclusive within finite additive jets, formal and
  p-typical targets, finite-etale re-encodings, arithmetic delta-characters,
  free tangent consistency, and the named cohomological and pairing routes.
- Exactly one next action: rerank outside additive local lifts, p-typical
  targets, finite-etale re-encodings, torsion orientation, and free tangent
  consistency; bind one mechanism-distinct P1548 theorem question. Do not run
  a jet preflight.
- Boundary: a canonical lift, exact tangent identity, nonzero anomalous
  residue, cohomology class, pairing value, or toy scalar is not generic-prime
  recovery, a Shoup-bound improvement, or breakthrough.

### ECFG-P1548-R0 - Torsor deck-orbit router theorem assignment

- Context: P1544 proves that branch labels in a coprime division fiber are
  torsion offsets and that choosing a scalar-compatible representative is the
  missing orientation oracle. P1546 proves that every fixed bounded-degree
  algebraic cover/reduction branch captures only `O(B)` sparse-base targets and
  that explicit branch catalogs conserve coverage and work. IDEA-010 names the
  remaining possibility as non-homomorphic deck-orbit canonicalization.
- Exact theorem question: for a finite cover or torsor `pi:X->E` with deck
  group `Gamma`, determine whether a target-independent orbit invariant can
  retain information not already on `E`, and whether a non-invariant branch
  selector can be defined without a torsor trivialization, deck orientation,
  target advice, or an explicit branch table. Classify fixed and growing degree
  separately and charge pushforward rank plus blind target descent.
- Required receipt: distinguish an invariant orbit canonicalization from a
  section of the cover; prove the strongest quotient-factorization and
  selector-ambiguity statements available; combine them with the bounded
  branch sparse-capture theorem; then either exhibit one compact
  growing-degree target-local router with complete `lambda,mu<=0.45` or record
  the exact unclassified circuit family.
- Hash-bound inputs:
  - IDEA-010 root:
    `315f2b6e62df24fa300cec72190fc2bc1c3e42f4aea074ef78eac7c461745c56`;
  - P1515 independent router audit:
    `7e7609716f87b1b4df5ffc77406a912ad0303cc309ec1b84be42ebcc0d09539e`;
  - P1544 independent audit:
    `db68ae68e99952656db3c4b179b94770f73972f2429f240c579879ea0502782f`;
  - P1546 independent audit:
    `f64cc45b05cc74364d87eec69f54ecda79100274c0b498103a6492fa61c62702`;
  - P1547 independent audit:
    `bfdeb57b686ade5c4a3db1c99d0f4fde3f1d193bb7becb7f4703bc7381a5b2b9`.
- Assignment disposition:
  `QUEUED_THEOREM_ONLY__DECK_INVARIANT_QUOTIENT_FACTORIZATION_TO_PROVE__ORBIT_CANONICALIZATION_VERSUS_BRANCH_SECTION_TO_SEPARATE__TORSOR_TRIVIALIZATION_AND_ORIENTATION_COST_TO_CLASSIFY__FIXED_BRANCH_SPARSE_CAPTURE_ALREADY_BOUNDED__PUSHFORWARD_RANK_AND_BLIND_DESCENT_TO_CHARGE__COMPACT_GROWING_DEGREE_ROUTER_UNSUPPLIED__NO_RUN`.
- Exactly one next action: write
  `ideas/artifacts/ECDLP-IDEA-010/p1548_torsor_deck_orbit_router_gate.md`.
  Produce one theorem-only receipt with a target-compatible branch operation
  and complete cost or a sharply scoped no-go. Do not draft or execute the
  proposed fiber-enumeration contract.
- Boundary: a solvable fiber, canonical orbit, deck action, valid upstairs
  relation, nontrivial pushforward, or toy target descent is not generic-prime
  recovery, a Shoup-bound improvement, or breakthrough.

### ECFG-P1548-R1 - Torsor deck-orbit router independent disposition

- Invariant quotient theorem: for a faithful finite deck action on
  `L=F_p(X)`, the extension `L/L^Gamma` is Galois of degree `|Gamma|`.
  Rational invariant labels factor through `Z=X/Gamma`. If `Z=E`, a full
  orbit label is only base data; if `Z->E` retains degree, selecting an orbit
  is the same residual branch problem on the intermediate quotient.
- Section theorem: a rational representative `s:E->X` with `pi*s=id` would
  give a `K=F_p(E)`-linear injection `L->K`, forcing `[L:K]=1`. Thus a
  connected nontrivial finite cover has no rational section, and a section of
  the generic torsor is a trivialization.
- Pushforward theorem: a deck-orbit atom maps to its single base image with
  orbit/stabilizer multiplicity. Repeated branches and orbit variants are
  duplicate E columns; zero multiplicity modulo `N` is unusable and invertible
  multiplicity is only a known coefficient.
- Fixed-branch theorem: every fixed rational divisor branch is a map into a
  bounded symmetric power of `X`; its universal support incidence captures at
  most `Delta*B_up+O(1)` targets on an atom base of size `B_up`. Explicit
  branch catalogs increase coverage and branch evaluations together, giving
  linear relation work and `N/B` blind descent for bounded geometry.
- Scope limit: coordinate ordering and other finite-field programs may choose
  roots without defining rational sections. A compact nonalgebraic selector or
  compact growing-degree circuit is not lower-bounded here, but IDEA-010
  supplies no such circuit, source inverse, projected rank, or complete cost.
- Independent audit SHA-256:
  `ea22392aeebf6f436a3ed19f9126f4c618c3327437c06f25a263439208e38742`.
- Recommended disposition:
  `INDEPENDENTLY_VERIFIED_SCOPED_NO_GO__GENERIC_DECK_INVARIANTS_FACTOR_THROUGH_QUOTIENT__TRANSITIVE_FIBER_ORBIT_LABEL_IS_BASE_DATA__NONTRANSITIVE_ORBIT_LABEL_MOVES_BRANCH_TO_INTERMEDIATE_QUOTIENT__CONNECTED_NONTRIVIAL_COVER_HAS_NO_RATIONAL_SECTION__RATIONAL_TARGET_COMPATIBLE_SELECTOR_IS_MISSING_SECTION_OR_TRIVIALIZATION__FIXED_RATIONAL_BRANCH_HAS_O_B_SPARSE_CAPTURE__EXPLICIT_BRANCH_CATALOG_CONSERVES_COVERAGE_AND_WORK__ORBIT_ATOM_PUSHFORWARD_COLLAPSES_TO_BASE_IMAGE_AND_MULTIPLICITY__PUSHFORWARD_CERTIFICATE_DOES_NOT_LOCATE_KNOWN_LOG_RELATION__LANG_TRIVIALITY_OVER_FINITE_FIELD_DOES_NOT_TRIVIALIZE_FUNCTION_FIELD_FAMILY__NONALGEBRAIC_ROOT_ORDERING_AND_COMPACT_GROWING_DEGREE_ROUTER_UNCLASSIFIED__INCONCLUSIVE`.
  P1548 is terminal inconclusive within invariant quotients, rational sections,
  orbit atoms, fixed rational branches, explicit catalogs, tuple-first
  pushforwards, and Lang-triviality claims.
- Exactly one next action: rerank to the independently preserved theorem-deferred
  IDEA-195 frontier and bind P1549 as a theorem-only seven-channel finite-state
  closure audit. Do not run the retired IDEA-195 contract or construct a solver.
- Boundary: a quotient identity, orbit label, section on a split control,
  nonzero pushforward, fixed-branch count, or toy target is not generic-prime
  recovery, a Shoup-bound improvement, or breakthrough.

### ECFG-P1549-R0 - Seven-channel non-Cartesian closure theorem assignment

- Context: P1548 closes rational deck invariants, rational representative
  sections, fixed algebraic branches, and explicit branch catalogs within
  scope. Independent corpus review preserves IDEA-195 as the sole
  theorem-deferred candidate. P1537 already proves that finite-tower norm
  transitivity transports the constant coefficient and six first derivatives
  and returns all five leaf x-sources on a simple coloured fiber.
- Exact theorem question: determine whether the restricted seven-channel
  Semaev local norm operator belongs to an explicit target-independent
  non-Cartesian representation family closed under every public factor-deck
  level, without enumerating `B^5` leaves, storing a `B^3` transition deck,
  materializing a pair table or dense resultant, or losing the conditioned
  five-source inverse.
- Required receipt: freeze the representation family and local update formulas;
  prove simultaneous trace/norm compatibility on a positive-dimensional
  nonfixed support; preserve poles, multiplicities, repeated roots, infinity,
  and every source stratum; then charge setup and state at most `B^2.25`, one
  target query at most `B^1.25`, independent rows, factor logs, blind descent,
  output, verification, and complete `lambda,mu<=0.45`.
- Hash-bound inputs:
  - IDEA-195 deferred root:
    `b52403859590a549f621fce1d2d71ab2e4da2d90faacbf9c0d3d48fcdb2bc513`;
  - P1537 exact transport audit:
    `5b0112a1efc6043150d998fb1c38217c602a00186f7982443aaab7a443acf249`;
  - P1538 bounded-state audit:
    `2a25ed9ed8eef5518229752a5c439c515255eb810bc01f99e7f0987531b52174`;
  - IDEA-195 independent red-team review:
    `8c92774c682e69c969a31970a1bcbb6a1e6d971cacbad4bb98d1cad91ec373d4`;
  - P1548 independent audit:
    `ea22392aeebf6f436a3ed19f9126f4c618c3327437c06f25a263439208e38742`.
- Assignment disposition:
  `QUEUED_THEOREM_ONLY__SEVEN_CHANNEL_TRANSPORT_ALREADY_EXACT__NONCARTESIAN_REPRESENTATION_FAMILY_TO_CONSTRUCT_OR_ELIMINATE__SIMULTANEOUS_TRACE_NORM_NONFIXED_SUPPORT_TO_PROVE__LOCAL_DECK_CLOSURE_WITHOUT_B5_LEAVES_OR_B3_STATE_TO_DERIVE__EXACT_ALL_STRATA_FIVE_SOURCE_INVERSE_REQUIRED__SETUP_B225_AND_QUERY_B125_RECTANGLE_UNMET__RETIRED_CONTRACT_NOT_AUTHORIZED__NO_RUN`.
- Exactly one next action: write
  `ideas/artifacts/ECDLP-IDEA-195/p1549_noncartesian_finite_state_closure_gate.md`.
  Produce one theorem-only construction or scoped no-candidate receipt. Do not
  execute the retired IDEA-195 contract, construct a solver, or generate a toy
  fixture.
- Boundary: exact norm transport, a finite-state value recurrence, trace-only
  descent, valid branch identity, singleton source ratios, or a toy row is not
  generic-prime recovery, a Shoup-bound improvement, or breakthrough.

### ECFG-P1549-R1 - Seven-channel non-Cartesian closure independent disposition

- Exact interface: the square-zero marked norm has one constant and six
  derivative channels. Norm transitivity and local multiplication preserve all
  seven exactly, and a unique simple zero returns the five x-sources by the
  ratios `j_i/j_0`. This is value-space closure, not domain compression.
- Frozen grammar: five shared state layers of size `O(B)`, four exact
  source-labelled projective `S3` correspondences of outdegree
  `D=B^gamma`, and optimistic `O(BD)` edge state support at most `O(BD^4)`
  complete five-source paths.
- Density theorem: a uniform known-scalar campaign needs at least
  `B^5/D^4` attempted targets for `B` rows, and blind masked descent needs at
  least `B^4/D^4`, before rank loss, source failures, or output costs.
- Explicit-navigation closure: even granting the initial state for free,
  expanding `D^4` continuations gives `B^5=N` relation work. Scanning every
  stored edge per target gives relation work `B^(6-3*gamma)>=B^3`.
- Conditional survivor: if a genuinely new target-conditioned path locator
  costs `O(D)`, setup/state is `B^(1+gamma)`, relation work is
  `B^(5-3*gamma)`, and blind descent is `B^(4-3*gamma)`. The complete
  relation gate is possible only for `11/12<=gamma<=1`.
- Degree correction: degree or adjacency size `B` is not alone fatal. At
  `gamma=1`, an exact `O(B)` locator would fit the exponent rectangle. What
  fails in the audited families is path expansion, global edge scans, `B^3`
  provenance, dense elimination, source advice, or missing exact costs.
- Missing operation: no artifact supplies simultaneous nonfixed `S3`
  trace/norm closure, a generic-prime shared-layer construction, an `O(D)`
  target-to-path inverse, complete signed all-strata replay, independent rank,
  verified factor logs, or identical blind descent.
- Independent audit SHA-256:
  `cd42b2b8ae71af0fb2c3d09ff264307b8705488daac2e6ec69e92a41d7c08fe1`.
- Recommended disposition:
  `INDEPENDENTLY_VERIFIED_SCOPED_NO_CANDIDATE__SEVEN_CHANNEL_VALUE_ALGEBRA_EXACT__SHARED_LAYER_PATH_MASS_AT_MOST_BD4__EXPLICIT_D4_PATH_EXPANSION_CONSERVES_B5_WORK__GLOBAL_EDGE_SCAN_MISSES_THE_RECTANGLE__AN_O_D_TARGET_LOCATOR_REQUIRES_GAMMA_AT_LEAST_11_OVER_12__DEGREE_B_IS_NOT_ALONE_FATAL__SIMULTANEOUS_TRACE_NORM_CLOSURE_AND_EXACT_PATH_INVERSE_UNSUPPLIED__INCONCLUSIVE`.
  P1549 is terminal inconclusive within the frozen shared-layer grammar,
  explicit path expansion, whole-edge scans, serial provenance, dense
  composed elimination, named deck controls, and explicit linear transfers.
- Exactly one next action: admit P1550 as a theorem-only audit of one
  high-branching shared-layer `S3` path locator in the surviving
  `11/12<=gamma<=1` window. Do not execute the retired IDEA-195 contract,
  construct a solver, or generate a toy fixture.
- Boundary: the `gamma` window is a necessary conditional cost window, not a
  construction, sub-rho algorithm, Shoup-bound improvement, or breakthrough.

### ECFG-P1550-R0 - High-branching S3 path-locator theorem assignment

- Context: P1549 closes explicit four-level branch expansion and global edge
  scans, while correcting the broader claim that degree `B` alone is fatal.
  The sole quantitative survivor is an exact `O(D)` target locator on a
  shared-layer support with `D=B^gamma` and `11/12<=gamma<=1`.
- Exact theorem question: construct one generic-prime shared-layer recursive
  `S3` correspondence and derive a target-conditioned recurrence that locates
  and replays an exact signed five-source path in `O(D)` work while carrying
  simultaneous trace, norm, and all seven marked channels.
- Required receipt: freeze state and edge equations, prove generic-prime
  applicability and path mass, derive every locator step without `D^4`
  expansion or a `BD` scan, handle every source stratum, and charge setup,
  query, output, independent rank, factor logs, blind descent, verification,
  bit time, and memory.
- Hash-bound input:
  - P1549 independent audit:
    `cd42b2b8ae71af0fb2c3d09ff264307b8705488daac2e6ec69e92a41d7c08fe1`.
- Assignment disposition:
  `QUEUED_THEOREM_ONLY__HIGH_BRANCHING_WINDOW_11_OVER_12_TO_1__SHARED_LAYER_S3_CORRESPONDENCE_TO_FREEZE__O_D_TARGET_PATH_LOCATOR_TO_DERIVE__SIMULTANEOUS_SEVEN_CHANNEL_TRACE_NORM_CLOSURE_REQUIRED__EXACT_SIGNED_ALL_STRATA_REPLAY_REQUIRED__NO_RUN`.
- Exactly one next action: write
  `ideas/artifacts/ECDLP-IDEA-195/p1550_high_branching_s3_path_locator_gate.md`.
  Produce one exact recurrence or a sharply scoped no-candidate receipt. Do not
  implement, execute a contract, invoke a solver, or generate a toy fixture.
- Boundary: high branching, compact one-step membership, a short powering
  circuit, or one valid path is not a complete path locator, ECDLP recovery,
  Shoup-bound improvement, or breakthrough.

### ECFG-P1550-R1 - High-branching S3 path-locator independent disposition

- Generic-prime one-step control: for each exact signed factor base, its dense
  squarefree x-support polynomial `L_i` can be reduced modulo the quadratic
  `S_3(x(U),x(V),X)` in `O(B)` field operations. The rank-two norm tests edge
  membership, and a degree-at-most-two gcd plus exact point checks returns the
  constant candidate source list. This is one-step membership, not composed
  path location.
- Frozen locator family: set `D=B` and enumerate `K=O(B)` public global
  rational branches. Branch `b` publishes five maps `s_(b,i):E->E` whose sum
  is identically the target and is accepted only when every output lies in its
  coloured exact factor base.
- Affine-branch theorem: every rational map `E->E` is a translation of an
  endomorphism. On the rational prime-order subgroup it is scalar-affine. The
  five-source sum identity forces at least one nonzero scalar coefficient, so
  one source coordinate is a subgroup permutation.
- Capture and work theorem: factor-base membership restricts that permutation
  coordinate to at most `B` target scalars. An explicit `K`-branch campaign
  therefore costs at least `N` branch evaluations for `B` rows and `N/B` for
  one blind masked descent, even granting exact rank, factor logs, all seven
  channels, output, and verification.
- Finite-domain degree gate: if explicitly enumerated rational coordinate
  formulas need satisfy the point and sum laws only on accepted rational
  targets, a degree-`d` branch captures at most `O(dB)` targets. The complete
  `B^(9/4)` relation-work gate requires `d>=B^(11/4)`; a dense representation
  already misses setup/state.
- Scope limit: reduced degree is not arithmetic-circuit size. Repeated public
  powering, Frobenius, finite-field reduction, equality masks, gcd logic, or
  modular composition can represent some high-degree functions succinctly.
  A compact circuit that selects and outputs a path without enumerating its
  branches remains unclassified and unsupplied.
- Independent audit SHA-256:
  `b41bb7919b3b32fe062369139d450649912f94edb63b72d72f5bc397665700c3`.
- Recommended disposition:
  `INDEPENDENTLY_VERIFIED_SCOPED_NO_GO__DENSE_FACTOR_POLYNOMIAL_GIVES_GENERIC_PRIME_O_B_ONE_STEP_MEMBERSHIP_AND_EXACT_GCD_SOURCE_LIFT__EVERY_GLOBAL_RATIONAL_SOURCE_BRANCH_IS_SCALAR_AFFINE_ON_THE_PRIME_SUBGROUP__SUM_IDENTITY_FORCES_ONE_PERMUTATION_COORDINATE__EACH_BRANCH_CAPTURES_AT_MOST_B_TARGETS__EXPLICIT_K_BRANCH_RELATION_WORK_IS_AT_LEAST_N_AND_BLIND_DESCENT_AT_LEAST_N_OVER_B__FINITE_DOMAIN_NONMORPHIC_SELECTOR_REQUIRES_DEGREE_AT_LEAST_B_11_OVER_4_IN_THE_ENUMERATED_BRANCH_MODEL__SUCCINCT_HIGH_DEGREE_FINITE_FIELD_CIRCUIT_UNCLASSIFIED__INCONCLUSIVE`.
  P1550 is terminal inconclusive within dense-polynomial one-step membership,
  global rational branches, rational sections, explicit branch catalogs, and
  explicitly enumerated finite-domain rational selectors.
- Exactly one next action: admit P1551 as a theorem-only audit of the residual
  compact high-degree finite-field `S3` selector-circuit grammar. Do not
  implement, execute the retired contract, invoke a solver, or generate a toy
  fixture.
- Boundary: an exact one-step test, degree floor, rational-branch no-go, valid
  source tuple, or compact high-degree formula is not a composed selector,
  sub-rho algorithm, Shoup-bound improvement, or breakthrough.

### ECFG-P1551-R0 - Finite-domain high-degree S3 selector-circuit assignment

- Context: P1550 gives a generic-prime dense-factor-polynomial one-step
  primitive and eliminates every explicitly enumerated global rational path
  branch independently of degree. Its finite-domain divisor count forces
  degree at least `B^(11/4)` but deliberately does not convert degree into a
  circuit-size lower bound.
- Exact theorem question: determine whether one target-independent finite-field
  circuit can use the five dense factor polynomials, projective `S3`
  coefficients, rank-two remainder/norm and gcd operations, public powering or
  Frobenius, equality masks, and a constant number of modular-composition
  stages to select and output an exact signed five-source path without
  enumerating rational branches, roots, `B^3` provenance, or a dense composed
  eliminant.
- Required receipt: freeze the circuit grammar and every coefficient source;
  prove reduced source-coordinate degree at least `B^(11/4)` is attained
  inside setup/state `B^(9/4)` and target query `B^(5/4)`; reconstruct every
  signed and nonreduced source stratum; then charge independent rank, factor
  logs, blind descent, output, verification, bit time, and memory. Otherwise
  identify the first exact branch-list, root-list, dense-elimination,
  provenance, or P1513/P1515 traffic restoration.
- Hash-bound input:
  - P1550 independent audit:
    `b41bb7919b3b32fe062369139d450649912f94edb63b72d72f5bc397665700c3`.
- Assignment disposition:
  `QUEUED_THEOREM_ONLY__FINITE_DOMAIN_SELECTOR_CIRCUIT_GRAMMAR_FROZEN__REDUCED_DEGREE_B_11_OVER_4_REQUIRED__DENSE_FACTOR_AND_RANK_TWO_S3_PRIMITIVES_ADMITTED__BRANCH_AND_ROOT_ENUMERATION_FORBIDDEN__EXACT_ALL_STRATA_FIVE_SOURCE_OUTPUT_REQUIRED__COMPLETE_LAMBDA_MU_045_PATH_REQUIRED__NO_RUN`.
- Exactly one next action: write
  `ideas/artifacts/ECDLP-IDEA-195/p1551_finite_domain_selector_circuit_gate.md`.
  Produce one exact selector circuit or a sharply scoped grammar no-go. Do not
  implement, execute a contract, invoke a solver, or generate a toy fixture.
- Boundary: high reduced degree, a short powering chain, a membership bit,
  selected toy root, or one valid path is not source-complete relation
  collection, ECDLP recovery, a Shoup-bound improvement, or breakthrough.

### ECFG-P1551-R1 - Finite-domain S3 selector-circuit independent disposition

- Frozen grammar: five dense squarefree factor polynomials, projective `S3`
  coefficients, supplied-edge rank-two remainder/norm/gcd, public powering and
  Frobenius, exact equality masks, and a constant number of explicitly costed
  modular-composition, power-projection, trace, norm, or elimination stages
  over named quotient algebras. Root lists, branch catalogs, source advice,
  target-fitted coefficients, unrestricted Boolean programs, and unnamed
  coefficient or trace oracles remain excluded.
- Exact projector result: in the split five-deck algebra the Fermat mask
  `1-S_6^(p-1)` is the P1536 equality projector. Frobenius is identity on this
  product of copies of `F_p`; powering changes tuple values pointwise and does
  not aggregate hidden source indices.
- Rank-two boundary: dense factor-polynomial reduction modulo the quadratic
  `S_3(x(U),x(V),T)` gives an exact `O(B)` test and constant signed lift only
  after adjacent path states `U,V` are supplied. The gate does not quantify
  over unknown path prefixes.
- Explicit representation gate: every admitted nonpointwise operation is
  charged in its represented quotient or endpoint-support dimension. Exact
  source-faithful staged aggregation reaches at least `B^3` traffic, while the
  direct five-deck quotient has dimension `B^5`. These exceed setup/state
  `B^(9/4)` and query `B^(5/4)` before rank, factor logs, or blind descent.
- Exact positive diagnostic: in `F_p[G]`, the coefficient of `[R]` in the
  product of five signed factor-set sums counts exact endpoint tuples modulo
  `p`. Square-zero x/y markers give the ten coloured source moments. They
  recover all five signed sources conditionally on a unique coloured fibre;
  multiple fibres aggregate, so this is not an all-strata selector.
- Standard endpoint controls: point-basis convolution restores the `B^3`
  separator. Character-basis diagonalization needs hidden scalar or pairing
  orientation, or all `N=B^5` modes. This is not a theorem against every
  noncharacter representation.
- Scope limit: no representation-independent arithmetic- or Boolean-circuit
  lower bound is claimed. A genuinely new noncharacter, nonenumerative
  endpoint coefficient and source-unranking operation remains outside the
  grammar, but IDEA-012, IDEA-156, IDEA-199, and IDEA-266 already record that
  missing interface. Naming it is not a mechanism-new successor.
- Independent audit:
  `ideas/artifacts/ECDLP-IDEA-195/p1551_finite_domain_selector_circuit_gate.md`.
- Independent audit SHA-256:
  `5f1bd9c12ca700074c9cd327f6539bc880ec60b27431dc5f34e23b0a12f6c68f`.
- Recommended disposition:
  `INDEPENDENTLY_VERIFIED_SCOPED_NO_CANDIDATE__FERMAT_EQUALITY_MASK_IS_THE_P1536_FROBENIUS_PROJECTOR__FROBENIUS_IS_IDENTITY_ON_THE_SPLIT_SOURCE_ALGEBRA__HIGH_REDUCED_DEGREE_IS_POINTWISE_SUCCINCT_BUT_DOES_NOT_COMPUTE_GLOBAL_SOURCE_MOMENTS__RANK_TWO_REMAINDER_NORM_GCD_DECIDES_ONLY_A_SUPPLIED_EDGE__STANDARD_MODULAR_COMPOSITION_NORM_TRACE_AND_POWER_PROJECTION_ARE_CHARGED_IN_EXPLICIT_QUOTIENT_DIMENSION__EVERY_SOURCE_FAITHFUL_EXPLICIT_FIVE_DECK_MERGE_REACHES_AT_LEAST_B3_STATE_OR_B5_FULL_STATE__ENDPOINT_GROUP_ALGEBRA_COEFFICIENT_AND_SOURCE_MOMENT_NORMAL_FORM_EXACT__POINT_BASIS_RESTORES_B3_SEPARATOR__CHARACTER_BASIS_REQUIRES_HIDDEN_SCALAR_ORIENTATION_OR_N_MODES__NO_UNREPRESENTED_NONCHARACTER_COEFFICIENT_EXTRACTOR_SUPPLIED__ARBITRARY_CIRCUIT_LOWER_BOUND_NOT_CLAIMED__INCONCLUSIVE`.
- P1551 is terminal inconclusive within the frozen finite-field grammar. No
  experiment, relation campaign, factor-log solve, masked descent, scalar
  recovery, Shoup-bound improvement, or breakthrough exists.
- Exactly one next action: admit P1552 as a theorem-only corpus-wide
  operation-level rerank. Do not admit another endpoint coefficient oracle,
  source annotation, solver swap, parameter change, dense resultant, or
  supplied source algebra as a new mechanism.

### ECFG-P1552-R0 - Mechanism-distinct post-selector frontier rerank assignment

- Context: P1551 leaves unrestricted compact circuits logically open but
  identifies their exact required interface as the already-recorded endpoint
  coefficient/source-unranking oracle. IDEA-195 has no supplied successor
  identity inside the audited grammar.
- Exact review question: after reading every active, deferred, rejected,
  anomalous, and `REVISE` record and the raw ledgers, does one operation-level
  mechanism survive semantic deduplication and explicitly remove the
  source-aggregation obstruction with exact all-strata output and complete
  `lambda,mu<=0.45` costs?
- Positive gate: publish one explicit identity or representation, its
  coefficient provenance, source inverse, generic-prime applicability,
  setup, query, state, relation density, rank, factor logs, blind descent,
  output, verification, bit time, and memory before any contract or run.
- Negative gate: if every route is an existing coefficient oracle, source
  annotation, solver/backend swap, parameter change, explicit tuple deck,
  dense eliminant, post-hoc selector, or relation-only certificate, preserve
  the theorem-deferred frontier and queue no cryptanalytic experiment.
- Assignment disposition:
  `QUEUED_THEOREM_ONLY__CORPUS_WIDE_OPERATION_LEVEL_RERANK__ALL_STATUSES_AND_RAW_LEDGERS_REQUIRED__COEFFICIENT_ORACLE_AND_SOURCE_ANNOTATION_CONTROLS__ONE_EXPLICIT_MECHANISM_OR_THEOREM_DEFERRED_FRONTIER__NO_RUN`.
- Exactly one next action: write
  `ideas/reviews/P1552_MECHANISM_FRONTIER_20260718.md` with a complete semantic
  inventory, closest-operation table, quantitative gates, independent
  red-team track, and exactly one executable successor action. Do not execute
  any review-required contract or create a solver or toy fixture.
- Boundary: a newly named oracle, equality mask, source moment, valid relation,
  or theorem receipt is not an ECDLP improvement or breakthrough.
