# BRIEF, round 2 (2026-09-26): a large ideation round on index calculus for the ECDLP on ECC2K-130

Addendum to `BRIEF.md` in this directory, which still binds in full (sections
0 to 4: authority and prohibitions, lane state, the ECC2K-130 frontier, the
record conventions, the object-frame constraint block). This addendum adds
what changed since round 1, the round-2 rules, and the six seams.

## 1. What changed since round 1

- **The 13 round-1 proposals are filed and merged** (PR #1455): `IDEA-20260926-`
  `136bd3, 178821, 1db0e8, 4b65e3` (arity lever), `89886c, 917981, a79052,
  ae8f0a` (solver asymmetry, RQ-CERTBIN-836ce2), `b48c9d, b6cc43, cafcf1`
  (representation objects). Read their titles and claims before writing;
  do not duplicate them, and fill `discriminated_from` against the nearest.
- **The product-law finding is under a validator pass**
  (`coordination/review/icperf-aa2efc-20260926/`, REVIEW-ICPERF-20260926-bcf1b2).
  The blind re-derivation (TASK-20260926-9fef40) has returned: the six
  free-oracle floors reproduce from the statement alone (log2 F = 89.2516,
  68.5850, 56.4049, 48.4352, 42.8501, 35.6086 at m = 2, 3, 4, 5, 6, 8 under
  the producer's model N = 4r), the rho reference is 60.8090 bits, #E = 4r
  and r is prime. Under a subgroup-restricted base (N = r, |F| = 2^(l-2)) the
  floors sit 1.33, 1.00, 0.80, 0.67, 0.57, 0.44 bits lower; m <= 3 stays above
  rho under both. TWO DEFINITIONS TO KEEP APART: the **floor-to-rho gap**
  (2^-4.41 at m = 4) and the **oracle budget per attempt** = rho / targets at
  the floor-optimal l, which the re-derivation puts at 2^5.73 (m = 4), 2^13.96
  (5), 2^19.77 (6), 2^27.37 (8) under N = 4r and about 0.5 to 0.8 bit higher
  under N = r. An m >= 4 oracle must meet the BUDGET per attempt (the
  first-summand row), not the gap. Round-1 records that quoted the gap as the
  budget are being listed by the validator; do not repeat that.
- **The known-results map exists** (`knowledge/frontiers/ecdlp/`, 48 rows,
  rendered for you at `frontier-map-rendered-20260926.md` in this directory)
  and **every new record carries a `prior_art` block** (schema below). The
  block is required by the validator from IDEA-20261001 on and by this brief
  now.
- **A prime-field meet-in-the-middle decomposition engine** landed on `main`
  (`src/crypto_autoresearcher/index_calculus/`, `--engine mitm`, table of
  tails). Binary ports and cost columns can cite it as an existing instrument.
- **numpy is now declared** in `requirements-dev.txt`; the CERTBIN
  instruments (`experiments/EXP-CERTBIN-e94b27/impl/`) import in this
  container. No SAT or Groebner binary is installed (say `missing: <engine>`).

## 2. Round-2 rules (in addition to BRIEF.md)

- Five pre-minted ids per lane, in the order given on the card; a lane that
  produces fewer returns the rest unused and says so.
- Every record: the full `idea` schema (`agents/idea-generator.md`), the
  lane's extra fields (BRIEF.md section 3, exemplar
  `ledger/proposals/IDEA-20260922-845a77.yaml`), `added: '2026-09-26'`,
  `status: proposed`, `approved_by: null`, `id_allocation_provenance`
  naming the lane's TASK id, AND:

```yaml
  prior_art:
    frontier_map: knowledge/frontiers/ecdlp
    rows_checked: [KR-...]            # every row you positioned the idea against
    nearest:                          # at least one, or none_found_after: [queries]
      - ref: KR-...                   # a KR-* row or a KN-* entry
        provenance: retrieved         # you READ the row in the rendered map
        relation: adjacent            # same | special_case | generalizes | adjacent | orthogonal
        delta: "what this idea adds, quantitatively, or 'none'"
    searched:
      corpus_grep: [terms you grepped]
      web: []                         # only if you actually searched
      blocked: []
```

  `novelty_status: known` requires a `nearest` entry with relation `same` or
  `special_case` whose provenance is not `recalled`. Otherwise `unverified`
  (no web check) or `speculative`. Read the rendered map before writing.
- `question_id` by the R2 ownership rule (BRIEF.md section 2): structural
  certificates and table columns to RQ-BINSTD-b6f698; measured decomposition
  mechanisms on the Certicom family and its prime-degree siblings to
  RQ-CERTBIN-836ce2; a Frobenius mechanism to RQ-FROB-7d8dd4; a phase-cost
  instrument to RQ-ICPERF-94c86e; quasi-subfield objects to RQ-QSP-f9bbdb.
  Say why in `origin.scope`.
- Every idea states its **target arity m** and the **per-attempt oracle
  budget** it must meet (from the table above), or says it is a constant,
  a certificate, or an instrument and cannot move a row.
- The concrete-experiment requirement of BRIEF.md section 3 is unchanged:
  a runnable-shaped cell, instrument path, metrics with units, controls
  (null object, ordinary-curve control, relabelled Z/NZ control where a
  group-structure claim is made), a three-row outcome table, a
  falsification threshold, an order-of-magnitude cost labelled as an
  estimate.
- YAML must parse. Prose scalars containing ": " or ending in ":" go in
  ">-" block scalars. A file that does not parse is not filed.
- Write only your five proposal files and your generator report
  `reviews/<TASK id>-generator-report.md` (with the inventor-protocol
  section 5 honest-accounting block). Never edit an existing record.

## 3. The six seams

| lane | seam | ids |
| --- | --- | --- |
| TASK-20260926-12a355 (S1) | ALGEBRAIC ORACLES WITH KOBLITZ STRUCTURE AT m >= 5. The only exponent-relevant lever is arity m >= 5 with a per-attempt cost under the budget. Candidates: Frobenius-twisted summation polynomials S_{w+1}(x^{2^{j_1}}, ..., x^{2^{j_w}}, x_R) as ONE-variable objects over an orbit-union base (G3's open direction); symmetrisation of S_{m+1} by the full automorphism group of order 262 (Joux-Vitse-style symmetrisation extended to Frobenius); Nagao's disjoint-coset decomposition and Riemann-Roch encodings at m = 5, 6 with the last summand root-found by gcd against a subspace polynomial; the "coupled solve" escape that b48c9d priced but did not design. Owner usually RQ-CERTBIN-836ce2 or RQ-FROB-7d8dd4. | 009cb9, 0d1d74, 120d6a, 197ecf, 1ddce2 |
| TASK-20260926-35e1b7 (S2) | THE LINEAR-ALGEBRA AND RELATION SIDE. The product law charges m 2^(2l) for linear algebra and one relation per decomposable target. Candidates: the F_r[Z/131]-module structure of the relation matrix (one relation per orbit; block-circulant elimination; whether the LA term can be driven below m 2^(2l)/131^2 and whether that ever matters at the cap locus); NFS-style filtering (singleton, clique) on ECDLP relation hypergraphs (discriminate from IDEA-20260915-9191ed); multi-target and batch discrete logs (L targets: rho costs sqrt(2 L r), KR-RHO-46c2c6; does index calculus amortise BETTER than sqrt(L)? price it); relations that are not "one target = one relation" (partial decompositions, relations among factor-base elements found by collision inside the sumset, priced against KR-RHO-13bf67 and the product law). Owner RQ-ICPERF-94c86e or RQ-BINSTD-b6f698. | 201e86, 20ba8f, 3c6a19, 3cc0b8, 4e139a |
| TASK-20260926-646e2a (S3) | GALOIS-INVARIANT AND ALGEBRAIC-GROUP FACTOR BASES AT n = 131 (the Couveignes-Lercier successor, KN-OPEN-095df5). Both written constructions are excluded at n = 131 over F_2 and no abelian variety of dimension <= 4 has 131 dividing its point count. Candidates: a Weil-polynomial census at dimension 5 and 6 (Jacobians of genus-5/6 curves over F_2 with 131 | #J(F_2); the LMFDB isogeny-class tables are the retrieval target, mark recalled if not opened); norm-one and other algebraic tori over F_2 with a rational point of order 131 (which k has 131 | Phi_k(2)? the answer is a one-line computation from ord_131(2) = 130); unipotent or non-commutative groups; the explicit translation formulae needed to write the membership condition; the descended degree such a base would give. Owner RQ-BINSTD-b6f698 (certificate) or RQ-FROB-7d8dd4 (mechanism). | 56d3c9, 5c26f9, 6f2601, 80209d, 84e2c0 |
| TASK-20260926-736257 (S4) | SOLVER STRUCTURE SPECIFIC TO A CURVE DEFINED OVER F_2. The descended systems have F_2 coefficients and are cyclic-shift equivariant in a normal basis (a77711: system(R) maps to system(sigma R)). Candidates: solving the ORBIT system once for all 131 conjugate targets (what is shared, what is not; the 917981 propositions are the coordinate-independence baseline); Frobenius-aware linearisation (squaring is F_2-linear, so x^2-monomials are linear in a normal basis: which degree-fall this buys on S_3 and S_4 descents); first-fall-degree and semi-regularity of Koblitz descents versus ordinary-curve descents at matched n (a controlled measurement on the CERTBIN cells and their Koblitz siblings); XOR-rich CNF structure and Gaussian-elimination-in-SAT (WDSat-style) as a cost law rather than a benchmark; symmetry breaking that respects equivariance rather than asserting a per-instance symmetry (HOLD-R's lesson). Owner RQ-CERTBIN-836ce2 or RQ-SATIC-1ae57a. | 9c5694, 9cc043, b11cb1, b88409, bb6dd5 |
| TASK-20260926-e13b6b (S5) | TARGET-DEPENDENT AND IMPLICIT FACTOR BASES (KN-OPEN-020's open classes) ON ECC2K-130. Candidates: bases defined relative to the target R (points at short tau-adic distance from R or from a walk through R; bases that move with the walk, so relation collection and rho become one process); implicit-membership bases with an O(n) test and no low-degree polynomial (the Hamming ball b6cc43 is one; find others: run-length, cyclotomic-coset weight, trace-vector patterns); the QSP successor object a17f43 with a twisted lambda (KN-TECH-54c38e "Limits"); for each, the lossy-projection test against its named Sigma, the description/membership/relation/descent/time/memory charge, and where it sits against the budget. Owner RQ-BINSTD-b6f698 or RQ-QSP-f9bbdb or RQ-CERTBIN-836ce2. | bbf2ed, bc1cab, beb5b6, c5125a, c5cdb5 |
| TASK-20260926-e93f77 (S6) | INSTRUMENTS, COST LAWS AND CONTROLS THE LANE IS MISSING. Candidates: the same-unit exchange rate (field multiplications per group operation versus per W_4 refutation on the RC-1 archived instances; the 818b73 successor); the (L, b) meter fixture on EC addition versus a relabelled Z/NZ and a random bijection (faa8d2's seam); theta(m) at the cap locus for m in {3, 4} on the CERTBIN cells (4b65e3's Stage 1); per-attempt cost DISTRIBUTION columns (CV, tail index) for ICPERF's boundary table; a binary port of the prime-field MITM engine as a solver-free certificate-producing ground-truth oracle for m = 3, 4 cells; a memory-charged reachability column with the Frobenius collapse (the producer's section 6.2). Owner RQ-ICPERF-94c86e or RQ-CERTBIN-836ce2. | c98e92, d06324, d1adfc, d3c5a5, dacb83 |

Spare ids (held by the dispatching session, unassigned): `IDEA-20260926-ddbea8`,
`-dec1a0`, `-e86967`, `-f5c26d`. Spare handoff id: `TASK-20260926-f1a0e5`.

## 4. What to read before writing (per lane, in order)

Your card in `handoffs/`; `BRIEF.md` sections 0 to 4; this file;
`frontier-map-rendered-20260926.md` (all 48 rows); `agents/idea-generator.md`;
the exemplar `ledger/proposals/IDEA-20260922-845a77.yaml`; the round-1
proposal(s) nearest your seam (titles and claims of all 13 at minimum); the
seam's named records; and `rg -li ecc2k ledger/proposals` for the rest of the
ECC2K-130 corpus (titles). `README.md` in this directory has the verdicts on
the 26 round-1 reviews and eight concrete experiment examples; the review
YAMLs' `successor_seam` fields are legitimate seeds and should be credited
in `origin.scope` when used.
