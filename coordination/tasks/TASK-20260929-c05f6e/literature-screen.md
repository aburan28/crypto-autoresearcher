# TASK-20260929-c05f6e: literature screen (D1) and source record for the Frobenius relation (D2)

Author: idea-generator (independent session, research-deep), 2026-09-30.
Zero scientific runs. No code written, no curve instantiated, no relation computed.
Every arithmetic statement below marked "derived" was done by hand in this session
and has NOT been machine-checked; recompute before any record leans on it.

## 0. Instrument disclosure

- `search_knowledge` (the kb MCP server) was **not available** in this session's
  tool surface. AGENTS.md "Knowledge retrieval policy" asks for it before
  asserting an avenue is tested or untested. The substitute used was ripgrep over
  `knowledge/` (including `knowledge/frontiers/ecdlp/`) and `ledger/`, plus
  WebSearch/WebFetch. So there are no kb source IDs to report. Corpus hits are
  reported by record ID instead. Absence of a hit is reported as absence of a
  search result and is not evidence that the avenue was untried.
- PDF extraction failed in this environment. The WebFetch of two PDFs returned
  compressed streams, and `pdftoppm` is not installed. HTML sources were used
  instead.
- No shell was available. So `allocate_id.py`, `validate_ledger.py`,
  `goal_lanes.py` and `git` were not run (see DESIGN.md section 9).

## 1. D2 first: the Frobenius characteristic relation, from opened sources

### Sources opened in this session

| # | Source | Provenance | What was read | verified_by |
|---|---|---|---|---|
| S1 | Wikipedia, "Schoof's algorithm" (https://en.wikipedia.org/wiki/Schoof%27s_algorithm), fetched 2026-09-30 | retrieved | Frobenius definition, characteristic equation, definition of t, Hasse bound | TASK-20260929-c05f6e (this session) |
| S2 | Wikipedia, "Counting points on elliptic curves", section "Schoof–Elkies–Atkin algorithm" (https://en.wikipedia.org/wiki/Counting_points_on_elliptic_curves), fetched 2026-09-30 | retrieved | characteristic equation; Hasse's theorem | TASK-20260929-c05f6e |
| S3 | Adikari, Dimitrov, Cintra, "A New Algorithm for Double Scalar Multiplication over Koblitz Curves", arXiv:1801.08589 (2018), rendered at https://ar5iv.arxiv.org/html/1801.08589, fetched 2026-09-30 | retrieved | Koblitz curve definition, tau as a complex number, mu | TASK-20260929-c05f6e |

Quoted as returned by the fetch tool:

- S1: "φ:(x,y)↦(x^q,y^q)"; "φ²−tφ+q=0"; "t=q+1−#E(F_q)"; "|q+1−#E(F_q)|≤2√q".
- S2: "the characteristic equation of the Frobenius endomorphism" is "ϕ² − tϕ + q = 0";
  Hasse: "||E(F_q)| − (q+1)| ≤ 2√q".
- S3: "[τ]P = (x², y²)", with τ "a complex number with value (μ + √−7)/2, where
  μ = (−1)^{1−a}"; Koblitz curves "E_a: y² + xy = x³ + ax + 1", a ∈ {0,1}, over
  F_{2^m}. **Discrepancy recorded, not resolved.** The extracted text shows `ax`
  where the standard Koblitz form (and this task's scope) has `ax²`. The two forms
  agree pointwise over F_2, since x² = x there, and give the same #E(F_2). They
  are different curves over F_{2^m}. This may be an artifact of the fetch tool's
  extraction. Nothing below depends on which form S3 intended, because only
  #E_a(F_2) is used, and that is recomputed by hand.

The Solinas papers ("Efficient arithmetic on Koblitz curves") and the
Avanzi–Heuberger–Prodinger tau-expansion papers are the usual primary sources.
They were located but **not read**: the PDF fetches returned undecodable streams.
They remain `recalled` pointers.

### The relation, as the sources state it, and what follows by derivation

1. **General form (S1, S2).** For E/F_q with q-power Frobenius φ(x, y) = (x^q, y^q):
   φ² − tφ + q = 0 in End(E), where t = q + 1 − #E(F_q) and |t| ≤ 2√q.
2. **Binary curve defined over F_2 (q = 2), derived from 1.** π² − tπ + 2 = 0,
   t = 3 − #E(F_2). Hasse gives |t| ≤ 2√2 ≈ 2.83, so **t ∈ {−2, −1, 0, 1, 2}**.
   The claim that odd t is ordinary and t ∈ {0, ±2} is supersingular in
   characteristic 2 is `recalled` (p | t iff supersingular). It is not used below.
3. **Koblitz curves (S3 plus a hand count).** τ = (μ + √−7)/2 with μ = (−1)^{1−a}.
   Squaring gives τ² = (−6 + 2μ√−7)/4 and μτ = (2 + 2μ√−7)/4, so
   **τ² − μτ + 2 = 0**. That is item 2 with t = μ. Hand count (derived): on
   y² + xy = x³ + ax² + 1 over F_2, a = 0 has 4 points {O, (0,1), (1,0), (1,1)}, so
   t = −1 = μ. a = 1 has 2 points {O, (0,1)}, so t = +1 = μ. Consistent with S3.
4. **Action on E(F_{2^n}) (derived from the definition in S1).** π^n fixes every
   point of E(F_{2^n}), because x^{2^n} = x on F_{2^n}. The fixed points of π itself
   are exactly E(F_2). E(F_2) is a subgroup of E(F_{2^n}), so #E_a(F_2) ∈ {4, 2}
   divides #E_a(F_{2^n}). If the ℓ-primary part is cyclic of prime order ℓ, then π
   acts on it as multiplication by some λ with λ² − μλ + 2 ≡ 0 (mod ℓ). λ has
   multiplicative order exactly n when n is prime and ℓ ∤ #E(F_2), since π^n = 1
   and π ≠ 1 on that subgroup.

### Verdict on FG-1 (DEC-20260929-3e8a1c `forward_guidance`)

- **Form: CORRECT.** "π² − tπ + 2 = 0 on the point group, with t the trace" is right
  for a curve defined over F_2 viewed over F_{2^d}, with the permitted values of t
  given in item 2. For Koblitz curves t = μ = (−1)^{1−a}.
- **Hypotheses: CORRECT, but one load-bearing condition is left implicit.** The
  Frobenius is an endomorphism only because the curve is defined over F_2. A
  random binary curve over F_{2^d} has no such endomorphism: its 2-power Frobenius
  maps E to E^(2). For prime d there is no intermediate field of definition
  (KN-OPEN-095df5 says the same for d = 131).
- **Consequence: IMPRECISE, and the imprecision matters for this task.** FG-1 says
  that ΣP_i = R implies Σπ(P_i) = π(R), and that this is "a free orbit action on
  the m-SUM solution set". The implication is right. The action, however, is on
  the **union over targets** ∪_R S_R, not on any single instance S_R. π maps S_R
  bijectively to S_{π(R)}, and π(R) = R iff R ∈ E(F_2) (item 4). So for every
  target of order ℓ the Frobenius **transports** the instance and fixes none of it.
  A single-target m-SUM oracle, which is what HEUR-GENERIC-MSUM prices, inherits
  no symmetry of its target-dependent side from π. Whatever π buys has to come in
  through the target-independent side: the stored table and the factor-base
  unknowns. This is the pivot of D3.

A draft KN-LIT entry for the relation is at `proposed-records/KN-LIT-e3a95c.md`.
The corpus had no citable statement of it: a Grep of `knowledge/` for the
characteristic-equation forms found only unrelated uses.

## 2. D1: does the k-SUM / generalised-birthday literature already answer the question?

**The question as posed:** does a free group automorphism acting on the factor
base improve the k-SUM time-store frontier?

### 2a. What the corpus already holds (read in this session)

| Record | Provenance of the underlying source | Relevance |
|---|---|---|
| KR-IC-b0fcda / KN-LIT-0d9d28 (Galbraith–Granger–Merz–Petit 2020/21) | row internal; paper abstract-read | Frobenius-invariant factor bases on subfield curves: "up to 1/n fewer systems" and linear algebra "faster by a factor n²". A factor-n family, i.e. logarithmic. The row's `forecloses` list contains "Frobenius-stable factor base" and "Koblitz index calculus speedup". |
| KN-FIND-b9a41d (`established`) | internal | σ-stable F_q-subspaces are the submodules cut by divisors of T^n − 1. The π-quotient alone gains mean orbit size g ≤ n, `claim_kind: constant_factor`. At (2,131) and (2,163) the only faithful stable dimension is n − 1 and the quotient is a net loss for m = 2..5. **This is the corpus's existing ceiling for the orbit quotient, on the relation-count axis.** |
| KN-FIND-47da4e (`unverified` deposit) | internal | The orbit-union (representative, shift) parameterisation is cost-neutral for m = 2 decomposition at toy n (ratio 1.00–1.47). |
| KN-OPEN-095df5 | internal | Non-linear Galois-invariant bases (Couveignes–Lercier via GGMP §4.2) are excluded at n = 131 for abelian varieties of dimension ≤ 4. Flags GGMP Lemma 3.3's hypothesis as possibly narrower than its statement. |
| KR-RHO-037e22 / KN-LIT-c5d918 (Gallant–Lambert–Vanstone 2000) | row internal; paper abstract-read | The same Frobenius gives parallel rho √(2n) on ⟨σ, −1⟩ classes. **The baseline gets the Frobenius too.** |
| KR-RHO-7d93f6 (Dinur 2020; Trimoska–Ionica–Dequen 2021) | row internal; papers abstract-read | "Finding C collisions with time T and space S requires T²·S = Θ̃(C²·N), so parallel collision search is optimal." This is the bound the 2c sketch needs. |
| KR-RHO-46c2c6 (Kuhn–Struik; Fouque–Joux–Mavromati; Yun 2015) | row internal; papers abstract-read | L discrete logs cost about √(2Lℓ) in total, tight by Yun's generic lower bound. Bears on whether any generic relation harvester can beat rho. |
| KR-RHO-5b1c0a (Delaplace–May) | row internal; paper abstract-read | Representation/subset-sum ECDLP over F_{p²} costs p^{1.314}, worse than rho. The nearest known negative for the representation route (D3 candidate X1), on a different field. |
| KR-RHO-6239aa / KN-LIT-73f7e1 (van Oorschot–Wiener) | retrieved (vendored primary source) | See 2c. **This is the contradictory source.** |
| KR-IC-1fcdbc | row internal; papers abstract-read | Galbraith–Gebregiyorgis 2-torsion and halving symmetries in characteristic 2: decomposition remains far slower than rho. |
| KN-LIT-2063 (Wagner 2002), KN-LIT-1188 (Joux–Kippen–Loss 2024, k-list over Z_p), KN-LIT-6192 (Nikolić–Sasaki), KN-LIT-3555 (Dinur–Dunkelman–Keller–Shamir, dissection) | internal stubs, abstract-level | k-tree and dissection filter partial sums on bits or integer intervals, i.e. on a structured quotient of the ambient group. The Z_p variant works on integer representatives of scalars, which a point representation does not expose. |

### 2b. Web screen (this session)

- ePrint 2016/312 (Nikolić–Sasaki, "Refinements of the k-tree Algorithm for the
  Generalized Birthday Problem", ASIACRYPT 2015), abstract page **retrieved**:
  "T² · M^{lg k − 1} = k · N", and "T² M = 4 · N" at k = 4. The abstract does not
  state the ambient group. The algorithm is Wagner-style list filtering.
- Wagner, "A Generalized Birthday Problem" (CRYPTO 2002), landing page
  **retrieved**, citation only. The corpus stub KN-LIT-2063 carries the abstract
  ("k lists of n-bit values ... xor to zero").
- Queries run: k-SUM / generalized birthday combined with automorphism,
  symmetry, time-memory, generic group. **No search result addressed k-SUM under
  a group automorphism acting on the input lists.** This is absence of a search
  result, not evidence that the question is untried. Its likely home is not the
  k-SUM literature but the symmetry-in-index-calculus literature, where the answer
  on record is the factor-n one (GGMP).
- `recalled`, backs nothing: Faugère–Gaudry–Huot–Renault, "Using symmetries in the
  index calculus for elliptic curves discrete logarithm" (J. Cryptology 2014).
  From memory, they use symmetries that **fix the target** (summand permutations
  and small-torsion translations with ΣT_i = 0) to lower Gröbner degree, and
  Frobenius is not among them. That matches item 1's verdict. Not opened in this
  session.

### 2c. Contradictory source: van Oorschot–Wiener golden-collision meet-in-the-middle

Read at source in `inputs/VOW-1996-PCS/paper_fulltext.md` (the preprint behind
KN-LIT-73f7e1), §4.2 lines 318–415 and §5.3 lines 682–774. Display equations are
fragmentary in the vendored text. Formulas below are restatements (R) from prose
plus fragments, and they are consistent with the prose ratio the paper states.

- §5.3 lines 707–713, quoted: the memory-limited MITM "expected run-time ... is
  (1/2)(n1/w)(w + n2) ≈ n1n2/(2w) function evaluations".
- §5.3 eq. (8) (R): parallel-collision-search MITM run time
  T_m ≈ 7 · n2 · √(n1/w) / m_proc · t. Lines 738–739 say it is "0.07 [√(n1/w)]
  times faster" than n1n2/(2w). The check (derived):
  (n1n2/2w) / (7 n2 √(n1/w)) = √(n1/w)/14 ≈ 0.071 √(n1/w). Consistent.
- §4.2 eq. (4) (R): golden-collision run time ≈ 2.5 √(|S|³/w)/m_proc · t, valid per
  lines 408–413 for w ≥ 2^10 at θ ≈ 2.25√(w/|S|). Line 766 gives the precondition
  |R| ≥ 2|D1|.

**Application to m-SUM on E(F_{2^n}) (derived, unreviewed).** Take
f1(a) = Σ_{i≤m/2} a_i and f2(b) = R − Σ_{i>m/2} b_i over F^{m/2}. Then
n1 = n2 = |F|^{m/2}, and the precondition is ℓ ≥ 2|F|^{m/2}. At store w = |F|^s
(with w ≥ 2^10):

- vOW MITM: T ≈ 7 |F|^{3m/4 − s/2}.
- HEUR-GENERIC-MSUM / memory-limited MITM: T ≈ |F|^{m − s}.

vOW is **strictly lower for every s < m/2** (m = 4, s = 1: |F|^{2.5} against
|F|^3). The two coincide at s = m/2. At m = 3 the unbalanced split gives
7|F|^{2.5 − s/2} against |F|^{3−s}, which is lower only for s < 1. So the
program's single supporting datum (m = 3, s = 1) cannot see this, which fits the
handoff's warning that m = 3 does not discriminate.

**Reading.** HEUR-GENERIC-MSUM says m-SUM on this group "admits no better generic
time-store tradeoff than partial meet-in-the-middle". **As worded, that is
contradicted per target by a generic algorithm in a retrieved primary source.**
The contradiction is conditional on vOW's random-function behaviour, which their
Table 1 simulations support. It contradicts an unvalidated heuristic, not
established evidence. It is flagged for Coordinator routing (AGENTS.md rule 12
if carried forward as a contradiction), not claimed.

**What it does NOT do (derived sketch, unreviewed).** It does not by itself open
a sub-rho cell in H-SEMBIN-8e7ae3's family:

1. A per-target golden-collision search over f on |S| = 2n1 points must find
   about C = |S|/(2k) collisions before a golden one, with k ≈ n1n2/ℓ golden
   collisions expected. vOW lines 342–346 give this for k = 1, and it generalises.
   The step also needs heuristic G1 of the successor proposal: the golden
   collision is not preferentially reachable.
2. KR-RHO-7d93f6 gives T² · S ≥ C² · |S| up to logs, and S ≤ C is the useful
   regime. So T ≳ √(C · |S|) = √(2ℓ · n1/n2), which is ≈ √(2ℓ) for balanced halves.
3. An index calculus needing ≥ |F|/(2n) relations from per-target oracles
   therefore pays ≳ (|F|/2n) · √ℓ, above rho.

The same sketch also shows why the shared-table PMITM line is the family's real
frontier: filling a table of M entries costs ≥ M, and the relation side costs
|F|ℓ/M, so T ≥ 2√(|F|ℓ). That is consistent with KR-RHO-46c2c6's √(2Lℓ) for
L = |F| logs, but the factor base is defined by x-coordinates, which is
non-generic, so that row applies only by analogy. **Hybrids** (a shared table
plus per-target golden-collision search) are not examined here. They are the
open part, carried as `proposed-records/IDEA-20260930-4b7d1e.yaml`.

### 2d. D1 verdict

- **On the question as posed** (does a free automorphism on the factor base improve
  the k-SUM frontier): **no direct result was found in the k-SUM literature.**
  That is a search result, not a proof. The adjacent symmetry-in-index-calculus
  literature already in the corpus (GGMP via KR-IC-b0fcda; KN-FIND-b9a41d)
  answers it on the relation-count and linear-algebra axes with a factor-n,
  logarithmic, gain. D3 derives the matching statement on the time-store axis.
- **On HEUR-GENERIC-MSUM itself:** existing work (vOW §5.3, retrieved)
  **contradicts its per-target wording** for m ≥ 4 and s < m/2, and for m = 3 at
  s < 1. It neither discharges the heuristic nor, by the 2c sketch, refutes
  H-SEMBIN-8e7ae3's family conclusion. The heuristic needs **restating**, as a
  statement about relation harvesting with the table fill charged rather than
  about single-target m-SUM, before it can be validated at all.
  DEC-20260928-7c3d91's knowledge_promotion deferral turns on that restatement,
  not on a Frobenius experiment. Choosing the record type is the Coordinator's
  decision; this screen writes no ledger record.
