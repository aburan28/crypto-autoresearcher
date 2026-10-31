# Scout dossier: coding theory (ISD, structured/QC decoding, list decoding GS/Wu, AG codes and Riemann-Roch spaces)

Scout field: coding theory. Written 2026-10-24 for the final lead-discovery round. Everything here
is a proposal or a derivation. Nothing changes a lead's status, and no record in the repositories
was edited or created. The only things written are this file and the scratch scripts under
`/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/scout/coding-isd/`.

Inputs read in full: ATLAS.md (all families), KRMAP.md, object-frame-ideation.md sections 1-3,
idea-generator.md ("Search heuristics", "Obstructions as generative material"), and the head of
target-result-profile.md. I also read the lead YAMLs of every SO code quoted below,
H-ECDLP-f6a43a, EXP-RELN-dc761f (head), EXP-PFDR-ca5e01 (kappa definition),
IDEA-20261018-a0830c, analysis/smallroot-reach/CLOSURE.md and its CORRECTION.md / CORR-20261024-b2a799.
Ledger dedup used grep on `ledger/.index/{proposals,hypotheses}.jsonl` only. It has 0 hits for
Guruswami, list decoding, AG code, elliptic code, deep hole, Plucker, Parvaresh and Sudan. The
nearest internal prior art is H-ECDLP-bac70e (the L(4O) hyperplane-section correspondence) and
IDEA-20260906-aa6da3 (the Riemann-Roch level-N linearisation).

Hygiene: the repo tools ran with `PYTHONDONTWRITEBYTECODE=1 python3 -B`. A `find` for
`__pycache__` newer than the atlas files found nothing new in the repository. The first
`lead_atlas.py --match` call ran before that flag was set and created nothing either.

Provenance policy: *retrieved* means I opened the source in this session (WebFetch/WebSearch or a
PDF text dump). *recalled* means from memory, not verified here. Labels used below:
**MEASURED (this session, toy)** for numbers I produced, **PREDICTION** for expected values, and
**H-x.y** for heuristics.

---

## 0. The dictionary, which is prior art and the frame for everything below

Let F be a factor base of n points, R the target, m the arity, and G_R = R + (m-1)O. The
elliptic code C_R = C_L(F, G_R) is [n, m] over F_p with designed distance n - m.

- **Cheng, "Hard problems of algebraic geometry codes", arXiv cs/0507026 (2005), IEEE Trans.
  IT 2008. Provenance: retrieved; I read the PDF text, Theorem 1 and its proof.** A codeword
  of weight exactly n - m exists iff some m points of F sum to R. The function with divisor
  ΣS - R - (m-1)O is unique up to a scalar. Theorem 2 of the same paper goes the other way: a
  2^{cn}·polylog minimum-distance algorithm gives ECDLP in time q^c.
- Equivalent forms: a weight-m codeword of C_R^⊥ = C_Ω(F, G_R); a singular m×m minor of the
  m×n generator matrix; m points of the degree-m elliptic normal curve E ⊂ P^{m-1} lying on one
  hyperplane (the internal H-ECDLP-bac70e is the m = 4 case).
- Li, Wan, Zhang, "On the minimum distance of elliptic curve codes", arXiv 1501.01138 (2015).
  Provenance: retrieved, abstract only. It gives an explicit minimum distance only when |F| ≥
  (2/3)·#E. That is the dense regime, where the program has already found the Weil bound
  vacuous for index-calculus sizes.

**MEASURED (this session, toy; `coding-isd/check_c1_dictionary.py`, output
`c1_dictionary_out.txt`).** Curve p = 2927, N = 2957. For m = 2, 3, 4, with 20 planted targets per
m and a 14-point base, the test "singular (m+1)×(m+1) evaluation matrix of L((m+1)O) on S ∪
{-R}" agreed with "ΣS = R" on 29,120 of 29,120 subsets. That included all 77 true
decompositions, with 0 mismatches. For supports of size w ∈ {m+1, m+2} the evaluation rank was
full in 1,800 of 1,800 random draws (Lemma L1 below).

The dictionary itself is not a candidate. What follows asks whether any decoder or ISD algorithm
can use it.

---

## 1. Killed candidates (killed first, with reasons)

**K1. GS / Sudan / Wu / power-decoding / BMS / Feng-Rao list decoding of C_R as a decomposition
oracle (B1). Killed by Lemma L2 (§2, C1).**

- A decomposition is a codeword whose agreement with the zero word is exactly k = m. There is no
  Riemann-Roch excess on genus 1: zeros ≤ deg G = m and dim L(G) = m.
- Guruswami–Sudan (IEEE Trans. IT 45(6), 1999; retrieved abstract) lists codewords only for
  agreement t > sqrt(n(n - d')), i.e. t > sqrt(n·k) on a genus-1 curve. m > sqrt(n·m) iff n < m.
- So no factor base larger than m is ever inside the radius. Capacity-achieving codes need
  t ≥ k + εn, which also fails.
- The dual has rate 1 - m/n, and its radius ≈ m/2 is half its distance m.

**K2. ISD (Prange, Stern, Dumer, MMT, BJMM, May–Ozerov) on C_R^⊥ (B1). Killed by L1 + L3 and
Canto Torres–Sendrier (PQCrypto 2016, LNCS 9606:144-161; retrieved abstract): at sublinear
weight every ISD variant has Prange's exponent.**

- Prange on C_R^⊥ tests (n - m)·m candidate m-subsets per information set, at Θ(1) amortised
  work per subset. The subtraction oracle tests n subsets per group operation, so Prange is
  dominated by a factor of about n.
- Stern-type splits either enumerate p^{Θ(m)} value vectors, or collide on column spans. The
  span-intersection test is a Plücker-orthogonality (incidence) join, not an equality join. Its
  only cheap evaluation is "the hyperplane through m-1 points meets E in one more point", i.e.
  the group law, so it is the pair-table MITM inside SO-TABLE.

**K3. Folded RS / Parvaresh–Vardy / Guruswami–Xing folded AG codes (capacity) (B1).**

- Folding needs a function-field automorphism σ and a place Q of small degree r with
  σ(Q) = Frob(Q). On E/F_p, σ = translation by a rational T, and a Q with πQ = Q + T has degree
  ord(T).
- On a prime-order group ord(T) = N, so the folding parameter is N. The cofactor part is
  Sylow-coprime (LEAD-ICB-cofactor-torsion-quotients).
- Capacity would still need agreement ≥ (1+ε)k (K1). Killed.

**K4. Interleaved / collaborative decoding (B1).**

- It needs error positions shared across codewords. Decompositions of distinct targets have
  distinct supports, so there is no shared support to use. Killed.

**K5. Quasi-cyclic structure / DOOM (decoding one out of many; Sendrier 2011, recalled) (B1, B5).**

- A code automorphism must fix the class of G_R. On F_p only Aut(E) (order ≤ 6) does that,
  which is a constant (KR-RHO-0528e7, SO-ENDO). Translation moves the class.
- On Koblitz curves the quasi-cyclic structure is the Frobenius orbit. That is SO-FROB, and the
  orbit-LA lead is exhausted_at_scale.
- DOOM is multi-target, which is SO-MULTI: "The multi-instance generic bound (L logarithms cost
  >~ sqrt(L r/|Aut|)) covers generic-oracle IC including its set-up, and batch rho (Kuhn-Struik)
  attains it ...". Killed.

**K6. Riemann-Roch spaces as implicit factor bases (B1/B2; named in the field brief).** Three
cases, all closed:

- (a) A finite family of functions {f_1..f_r} ⊂ L(G) with F = ∪ zeros. Then |F| ≤ r·deg G and
  the membership polynomial ∏ Norm(f_i) has degree ≥ |F|. That is SO-ALGFB: "a size-B
  algebraic base has description degree >= B/3 ... Scope: prime-order E/F_p, any base of size B".
- (b) A positive-dimensional linear subsystem V ⊂ L(G), dim V ≥ 2. Through every point passes
  a member, so F = E(F_p).
- (c) A target-dependent F_R. Its logs are new unknowns unless F_R ⊂ a fixed base. If it is
  inside one, it is a subset choice and conservation applies (KN-FIND-007). Otherwise it is the
  decomposition itself ("Target-dependent and walk-carried bases are known-log pools",
  LEAD-ICB-generic-table-oracle).
- Iterated-map tower bases (Petit–Kosters–Messeng 2016; Amadori–Pintore–Sala; recalled) are
  already foreclosed by KR-IC-5931ee ("Petit-Kosters-Messeng tower").

**K7. Rank-metric MaxMinors / Support-Minors modelling of the descended binary system (B4).**

- For deg G = m + k with k ≥ 1, ℓ(G - ΣP_i) = k for any points, whatever their sum. A rank
  defect exists only in the square degree-m case, which is one determinant. There are no
  rectangular minors to linearise.
- Rank decoding is hard because the support is unknown, but the subspace V is known here.
- The y coordinate adds n bits per point. Killed.

**K8. A Parvaresh–Vardy / folding "correlated equation" booster for
LEAD-ICP-coppersmith-smallroot-semaev (B1/B2).**

- Lemma: an auxiliary polynomial sharing the decomposition root comes from one of three sources.
  (i) A homomorphism ψ: endomorphism, isogeny, automorphism or [j]. Its pulled-back locus
  {Σ±P_i ∓ R ∈ ker ψ} contains the original locus as a component. S_{m+1} is irreducible, so
  the new polynomial is a multiple of S_{m+1}(·, x_R) and adds nothing to the ideal. Sparser
  multiples are the optimal-shift question already in the lead's next step. This is SO-ENDO
  again: "For G of prime order N, End(G) = Z/N ...".
  (ii) A further restriction on the base points: windowed internal nodes are already priced in
  ε_required. Small-y bases have |F| = X^2/p and demand m(1+β)/(m+1) ≥ 0.93 at m = 4, worse.
  (iii) Nothing else: the instance carries no other algebraic data.
- So there is no PV analogue without a density cost. Killed.
- **Flag for the coordinator:** this lead's YAML quotes numbers superseded by
  CORR-20261024-b2a799, which is still pending rule-12 review. Its best_measured reads "epsilon
  margin -0.0481 at (m,w) = (4,2) (JM extended 0.8408 vs demand 8/9)". The correction
  (analysis/smallroot-reach/CORRECTION.md) gives ε(S_3) = 0.2803 and a best margin of −0.6086 at
  (4,2) (−0.5161 at (32,0)). If the correction stands, the reach gain needed is about 3x, not 6%.
  The demand of 8/9 in the next_action does not change; the supply it is compared against
  becomes 0.28 rather than 0.84.

**K9. Stichtenoth-type AG-code automorphism / invariant-degree bound for
LEAD-RHO-non-automorphism-equivalence (B6).**

- Derived: a non-constant H-invariant F ∈ L(dO) needs d ≥ (N-1)/(n*+1). Here n* is the least
  degree of an endomorphism realising some λ ∈ H \ Aut. The reason: F∘α - F has at most
  d(n*+1) poles yet vanishes on N-1 points, so F∘α = F, and comparing degrees forces n* = 1.
- For a generic CM discriminant D, n* ≈ N·sqrt|D|/h, so the bound is vacuous.
- Algebraic degree is also not SLP cost: x^{(p-1)/2} has degree p/2 and costs log p.
- It does not decide the lead. Killed.

**K10. Coding-theory linear algebra (structured Gaussian elimination, block Wiedemann/Lanczos)
for B3.**

- LA is not the gap driver.
- The B3 decision rests on SO-TABLE's theorem, not on any fitted number: "Any decomposition
  oracle that enumerates or table-looks-up factor-base elements is a generic time/memory
  trade-off and obeys S*T^2 >~ N ... Scope: any generic (enumeration/table) decomposition over
  F_p." No constant-factor programme on an enumerative oracle crosses rho asymptotically.
- Illustration only: a two-point slope between the unvalidated (pre-gate) Table B endpoints is
  log2(13.5/5.47)/(23.4 − 11.9) = 0.113 per bit, i.e. about 0.61 against rho's 0.50. The board's
  own fit is 0.841 [0.500, 1.024]. Killed (outside my field in any case).

**K11. Determinantal / Frobenius–Stickelberger y-linear (Riemann–Roch) presentation of the
decomposition system for B2.**

- Riemann–Roch formulations are known: Nagao 2010, Diem 2011, and the McGuire–Mueller
  Gröbner-free variant cited in KR-IC-5931ee (all recalled).
- Over F_p the bottleneck is factor-base membership, which a change of presentation does not
  touch.
- The y variables are not small, which also rules out Coppersmith. Killed.

**K12. Sub-linear membership by sparse gcd (cyclic-code / BCH structure of a subgroup base) for
B1 ("a decomposition test sub-linear in |F|", SO-TABLE revisit_when).**

- gcd(f, X^B - 1) costs O(M(deg f)·log B). That is sub-linear, but only in one variable.
- For m = 2 the joint condition is C_R ∩ (μ_B × μ_B), where C_R : S_3(x_1, x_2, x_R) = 0 is a
  genus-1 curve in G_m^2. Every reduction I found works in F_p[x_1]/(x_1^B - 1), which costs
  Θ(B) per target, the same as subtraction.
- A sub-linear monomial structure for translation would be a homomorphism E(F_p) → G_m, i.e.
  embedding degree 1. That is SO-PAIR: "... an F_p-rational graph-type (N,N) kernel exists only
  when k_emb = 1; both reduce to MOV. Scope: ordinary and supersingular curves over F_p, prime N."
  Killed.

---

## 2. Live candidates

### C1. Riemann–Roch excess lemma: no AG-code decoder or ISD is a decomposition oracle (a cheap PROOF that closes the coding-theory family)

**Bottleneck.** B1. The family "use a decoder for the elliptic code as the non-enumerative
oracle" is uncatalogued. The matcher returns LEAD-ICE-generic-oracle-arity-cost-floor (binary),
LEAD-ICE-rootfind-pairtable-oracle and LEAD-EXO-augmented-oracle-ggm, none of which covers it.

**External ingredient.**
- Cheng 2005/2008, Theorem 1 (dictionary; retrieved).
- Guruswami–Sudan 1999, the AG-code list-decoding radius n - sqrt(n(n - d')) (retrieved abstract).
- Canto Torres–Sendrier 2016, sublinear-weight ISD equivalence (retrieved abstract).
- Riemann–Roch on genus 1 (textbook).

**Mechanism (three lemmas).**
- **L1 (no information above weight m).** For S ⊂ F with |S| = w > m, the dual words supported
  in S form Ω(G_R - S) ≅ L(S - G_R), using K ≅ 0 on genus 1. This has dimension exactly w - m
  for every S, independent of ΣS.
  - So the only dual words carrying group information are the weight-m words, which are the
    decompositions themselves.
  - Representations, partial syndromes and k-tree linear combinations all manipulate words with
    zero group content until the last step.
  - (MEASURED toy: 1,800/1,800 full rank at w = m+1, m+2.)
- **L2 (decoder ceiling).** Every interpolation decoder certifies a codeword only through a
  zero-count beating a pole order. That gives t > sqrt(n(k+g-1)) for GS-type decoders and
  t ≥ k + εn for capacity codes.
  - The excess of zeros over dimension for f ∈ L(G) on genus g is at most g - 1. On E it is 0,
    so a decomposition codeword has agreement exactly k with the zero word.
  - Hence decompositions lie outside every polynomial-time list-decoding radius for every base
    with |F| > m.
  - A genus-g cover raises the excess to g - 1, but GS's radius degrades by the same g, and the
    cover pays SO-COVER.
- **L3 (ISD collapse).** As in K2: Prange is dominated by subtraction, and Stern-type collisions
  reduce to the group-law MITM.

**(Representation, operation set).**
- Representation: the point as a column of the Riemann–Roch evaluation matrix, i.e. a point of
  the degree-m elliptic normal curve in P^{m-1} (class R2, curve embedding).
- Operation set: hyperplane sections in the class of G_R, i.e. relations. This is translation by
  factor-base elements only.
- Trichotomy: **partial-action** (Class I, the same as IC), because the relation vector
  propagates only under translation by base elements.

**SO codes touched, with the premise escaped.**
- **SO-TABLE**, LEAD-ICP-generic-table-decomposition: "Any decomposition oracle that enumerates
  or table-looks-up factor-base elements is a generic time/memory trade-off and obeys S*T^2 >~ N
  (Corrigan-Gibbs--Kogan) and T >~ sqrt(N) (Shoup); ... Scope: any generic (enumeration/table)
  decomposition over F_p."
  - Decoders escape the premise "enumerates or table-looks-up": they do linear algebra on
    coordinate evaluations. So SO-TABLE alone does not close them, and C1 is needed.
- **SO-GEN**, LEAD-RHO-generic-sqrt-lower-bound: "Shoup/Nechaev generic-group lower bound: any
  generic algorithm needs Omega(sqrt r) group operations ... Scope: all generic algorithms, any
  field, any r."
  - Escaped premise: "generic". The decoder reads the representation.
- **SO-ALGFB**, LEAD-ICP-algebraic-membership-factor-base: "A target-independent algebraic locus
  of degree d yields O(d) usable points, ... mean per-target yield is binomial(B+m-1, m)/N for
  every base of size B ... Scope: prime-order E/F_p, any base of size B."
  - Escaped premise: "algebraic locus of degree d". A decoder needs no membership polynomial
    and works for any F, which is why C1 is stated for arbitrary F.
- **SO-COVER**, LEAD-TRF-same-field-genus-g-embedding: "... genus-g index calculus costs
  O~(q^{2-2/g}) >= q for g >= 2 ... Scope: prime-field source curves, any same-field cover
  (DEC-20260902-4c82fd)."
  - Not escaped. The only way to gain Riemann–Roch excess (genus g > 1) lands in it.
- Binary-scope neighbour, LEAD-ICE-generic-oracle-arity-cost-floor: "... Scope: oracles that do
  not read curve coordinates algebraically ...". Decoders do read coordinates algebraically, so
  they are outside its scope, and C1 covers that gap.

**Proposed obstruction statement (with its scope).** "Point decomposition over any factor base
F with |F| > m is a minimum-weight codeword of the genus-1 evaluation code C_L(F, R + (m-1)O)
(Cheng 2005, Thm 1). Its agreement with the zero word equals the code dimension, so it lies
outside every interpolation decoder's radius sqrt(n(k+g-1)) and every capacity radius k + εn.
Dual words of weight above m have dimension w − m for every support and carry no group
information. ISD variants collapse to Prange (dominated by subtraction) or to the group-law MITM.
Scope: interpolation-based list decoders (GS/Sudan/Wu/power/BMS/Feng-Rao/folded/PV) and ISD
variants on genus-1 evaluation codes, any factor base with |F| > m. Not covered: a general
minimum-distance algorithm for elliptic codes, which by Cheng's Theorem 2 would itself solve
ECDLP."

**First discriminating step.** An independent review of the one-page derivation of L1–L3 (this
section), plus the toy check already run.
- L1–L3 survive review → file a new lead LEAD-ICP-ag-code-decoding-oracle as
  closed_obstructed(proof), with the scope clause above. Suggested forecloses:
  - "list decoding of elliptic codes for point decomposition"
  - "information set decoding for elliptic subset sum"
  - "minimum-weight codeword of the elliptic AG code as relation oracle"
  - "folded or Parvaresh-Vardy elliptic codes"
  - "Riemann-Roch implicit factor base"
- A decoder is found whose correctness does not rest on a zero count against a pole order → the
  lead goes open_next_step, with that decoder named and a planted toy recovery (the
  check_c1_dictionary harness) as the next step.

**Tier.** X: it closes an exponent route.

**Predicted gain.** 0 (closure).
- H-C1.1: the ISD behaviour of C_R^⊥ is no better than a random [n, n-m] code with the same
  parameters. Rigorous half: L1, intermediate words are information-free. Classical half:
  Canto Torres–Sendrier's random-code analysis.
- L1 and L2 are unconditional.

**Cost.** Implementation about half a day to write up. Toy check done (seconds).

**Self-kill risk.** Medium-high that a reviewer calls it folklore (Cheng's dictionary, and the
general sense that deep-hole decoding is as hard as subset sum). Its value is a filed closure with
forecloses phrases, so the family stops coming back as "new arithmetic".

**--match phrasings** (results in `coding-isd/match-coding.txt`):
1. own: "elliptic AG code minimum-weight dual codeword as point-decomposition oracle via
   Guruswami-Sudan list decoding or information set decoding" → top hit
   LEAD-ICE-generic-oracle-arity-cost-floor (8). No lead covers it.
2. plain: "use error-correcting-code decoders to find factor-base points that add up to the
   target point" → LEAD-ICE-gpu-rootfind-oracle (8), KR-IC-5a43e5.
3. obstruction vocabulary: "non-generic decomposition test sub-linear in the factor base from
   algebraic decoding of the Riemann-Roch evaluation code instead of enumeration or table lookup"
   → LEAD-ICB-kic-golden-base-exact-decomp (22), LEAD-ICB-generic-table-oracle (18),
   LEAD-ICP-coppersmith-smallroot-semaev (16).

---

### C2. Guruswami–Sudan list-recovery certifier for the log graph: complete per-curve proof that no degree-d polynomial omega beats rho (decides LEAD-EXO-invertible-hint-subset; secondary arm for B7)

**Bottleneck.** The open lead LEAD-EXO-invertible-hint-subset, which is not one of B1–B7, plus
a secondary arm for B7.
- LEAD-EXO-invertible-hint-subset, next step: "Measure A(1) and A(d) ... the cell was never
  measured (claim expired, EV-ECDLP-924941)."
- In H-ECDLP-f6a43a, Theorem W leaves the window (1/2, 3/4] in α open "by the sqrt(p) error term
  alone".
- Secondary: B7, LEAD-TRF-miller-cocycle-nonhom-transfer, as a polynomial-structure arm next to
  its equidistribution test.

**External ingredient.**
- Guruswami–Sudan 1999 (retrieved abstract): it lists every degree ≤ k polynomial agreeing with
  n given points on more than sqrt(kn) of them. The abstract states the problem for "n points",
  and list recovery (two values per abscissa) is the weighted/list-recovering extension; that
  section of Guruswami's FnT-TCS monograph is retrieved as a title only.
- Fast interpolation: Jeannerod–Neiger–Schost–Villard (arXiv 1512.03503; retrieved), Õ(m^{ω-1}(σ
  + |s|)) for shifted minimal bases, i.e. Õ(L^{ω-1}·n·s^2) for GS.
- Roth–Ruckenstein root finding (recalled).

**Mechanism.**
- Points: Γ_E = {(x(Q), log Q mod p) : Q ≠ O}, which is n = N - 1 pairs, two per abscissa (±).
- **Completeness lemma (derived here).** Under model M_deg, a degree-d polynomial omega F whose
  agreement set D_F has size a gives random self-reduction at cost (N/a)·(d + O(log N)): try
  Q* + rG until [F(x)]G checks.
  - This beats rho only if a > d·sqrt(N)·(1 + o(1)).
  - For d ≥ 2 that already exceeds Sudan's threshold sqrt(2dN), and GS's sqrt(dN) for d ≥ 1.
  - So an empty GS list at t = d·sqrt(N) proves on that curve that no degree-d M_deg omega beats
    rho. That is complete for the whole rho-beating region of the model, not a sample of it.
  - d = 1 is handled by the existing O(n^2) anchor-slope census (EXP-ECDLP-02bd1c).
- Against Theorem W, N(F) ≤ 2 + K_d·sqrt(p)·(1 + ln(pn)), the GS threshold sits a factor of
  about 5.7·(1 + 2 ln p) lower at d = 1 (≈ 162x at p = 2^20). So the census closes per curve the
  band that the Weil error term leaves open.
- At t = d·sqrt(N), Sudan's Y-degree is L ≈ sqrt(N). In the JNSV bound
  Õ(m^{ω-1}(σ + |s|)) with m = L + 1, σ = n and shift sum |s| ≈ d·L²/2 ≈ dN/2, the cost is
  Õ(d·N^{(ω+1)/2}) ≈ d·N^{1.7–1.9}. The factor d comes from the shifts.
- **This replaces the lead's own discriminator, and the replacement needs review.** The lead's
  next_action reads A(d) "against the random-labelling null". C2 instead gives a complete
  certificate over the rho-beating band a > d·sqrt(N). It does not measure A(d) at the H1 scale.
  The load-bearing new step for review is the completeness lemma.
- **Blind spot, which goes into revisit_when.** The lemma holds only under M_deg (dense cost =
  degree). An omega with SLP cost c(F) beats rho when a > c(F)·sqrt(N), but GS sees it only when
  a > sqrt(deg F · N). So sparse or SLP-cheap omegas in the band c(F)·sqrt(N) < a <
  sqrt(deg F·N), which is nonempty iff deg F > c(F)², e.g. polylog-cost and high-degree ones,
  stay invisible.

**MEASURED (this session, toy; `coding-isd/check_c2_gs_pilot.py`; outputs `c2_pilot_b10.txt`,
`c2_pilot_b11.txt`; dense numpy Sudan s = 1, so O(n^3)).**

| bits | curves | d | t (Sudan) | real-curve lists | planted (NULL-1 + degree-d plant at 1.3t) |
|---|---|---|---|---|---|
| 9 | 1 (p=491, N=461) | 1, 2, 3 | 30, 42, 52 | empty, empty, empty | recovered 3/3 |
| 10 | 3 (p ∈ {1013, 881, 907}) | 1, 2, 3 | 41–77 | empty 9/9 | recovered 9/9 |
| 11 | 2 (p ∈ {1481, 1033}) | 1, 2, 3 | 55–78 | empty 6/6 | recovered 6/6 |

Wall time was 3–31 s per cell. This shows the instrument is correct and has power at toy size. It
is not evidence at the H1 scale: GS certifies A(d) < t, while H1 predicts A(d) ≈ 3–6 here.

**(Representation, operation set).**
- Representation: R1, the affine x coordinate with integer lifts of the log, as in H-ECDLP-f6a43a.
- Operation set: degree-bounded polynomial evaluation on x (not translation).
- Trichotomy: **coordinate-dependent** (Class III). The tracked object is a function of the
  encoding.

**SO codes touched, with the premise escaped.**
- **SO-GEN**, LEAD-RHO-generic-sqrt-lower-bound: "... any generic algorithm needs Omega(sqrt r)
  group operations ... Scope: all generic algorithms, any field, any r."
  - Escaped premise: "generic". F reads the coordinate. Its revisit_when says "only a method that
    reads the representation ... can change the exponent", and an omega is such a method.
- **SO-TORS**, LEAD-STR-torsion-module-leak: "... A non-homomorphic point statistic is a function
  of the encoding of Q. Using it is index calculus or a generic query, and partial information
  about k on the point costs more than it saves, by sqrt(M) (IDEA-20260811-8cf53a). ... Scope:
  prime-order G, any l != N."
  - Escaped premise: "partial information". A hint family returns the full log on D_F, verified
    with one scalar multiplication. The certifier tests that escape exhaustively.
- **SO-ENDO / SO-PADIC** are not touched: no endomorphism image or lift is used.
- Object frame: coordinate-dependent, and the projection is not required to propagate under
  translation.

**First discriminating step.** A native (C/NTL or Rust) GS/Sudan with fast interpolation and
Roth–Ruckenstein, run as a census:
- bits 12–20; 10 curves per size plus NULL-1 relabellings;
- d ∈ {2, 3, 4, 6, 8, 16, 32, ..., ⌊sqrt N⌋}, at two thresholds: t_J = Johnson + 1 (the
  strongest certificate) and t_ρ = d·sqrt(N) (the completeness boundary);
- planted positives at 1.2·t on NULL-1, with the existing d = 1 anchor-slope arm alongside.

| outcome | disposition |
|---|---|
| Real-curve lists empty at every (size, d), planted recovered everywhere | LEAD-EXO-invertible-hint-subset → closed_obstructed(measured), model M_deg, toy tier ≤ 20 bits: "no polynomial omega of degree ≤ D_max beats rho on any tested curve". revisit_when: an omega whose degree exceeds the square of its SLP cost (band c(F)·sqrt(N) < a < sqrt(deg F·N)). |
| A non-planted list on a real curve absent from its NULL-1 matches | open_next_step, best_measured = (curve, d, agreement, F); price the random self-reduction end to end against matched rho |
| Planted miss | O-ARTIFACT; the instrument is void |
| Secondary arm (B7): the same census on {(log_g U(kP), k)} empty | evidence for H1 of IDEA-20261017-e3a6f1 on its polynomial-structure arm. It does not close that lead alone; equidistribution and character correlation remain its step. |

**Tier.** X: a positive would be a sub-sqrt random self-reduction.

**Predicted gain.** 0.
- PREDICTION: empty lists on every real curve.
- H-C2.1 (= H1 of H-ECDLP-f6a43a): A(d) ≤ (1+ε)(d+1)·ln p / ln((d+1)·ln p) + O(1). That is about
  11 at p = 2^20, d = 2, against t ≥ 2048.
- H-C2.2 (first moment): E[#F of degree ≤ d with agreement ≥ t] ≤ p^{d+1}·C(n_x, t)·(2/p)^t ≤
  p^{d+1}·(e/t)^t, which is below 2^{-10^4} at t ≥ 2048.
- The census is complete per curve, so a null result is a certificate, not a sample. It is still
  a toy-tier certificate: crypto-size extrapolation rests on H-C2.1.

**Cost.** Implementation 2–4 days for a native fast-interpolation GS. Compute
Õ(d·N^{1.7–1.9}) field operations per (curve, d): about d·2^{34–38} at N = 2^20, minutes to hours
per cell for d ≤ 32. The whole census is a few hundred to a few thousand core-hours. The dense
numpy pilot is O(n³) and stops near 11–12 bits.

**Self-kill risk.** Medium-high that the outcome is "null as the GGM intuition says". The value is
that it turns an expired, never-measured cell into a complete per-curve certificate over the
region where an omega would matter. Also a scope risk: the census is toy only, since logs are
needed for every point.

**--match phrasings:**
1. own: "Guruswami-Sudan list-recovery certifier for the maximal agreement A(d) of the elliptic
   log graph with degree-d polynomials" → LEAD-EXO-dl-character-sum-pseudorandom (5),
   LEAD-EXO-invertible-hint-subset (4).
2. plain: "check whether any low-degree polynomial of the x-coordinate equals the discrete log on
   a large set of curve points" → LEAD-EXO-invertible-hint-subset (19).
3. obstruction vocabulary (SO-TORS): "non-homomorphic point statistic that is a function of the
   encoding and recovers the logarithm on a dense recognizable and invertible subset" →
   LEAD-EXO-invertible-hint-subset (22), LEAD-TRF-miller-cocycle-nonhom-transfer (7).

---

### C3. Exact all-target decomposition census from the log-domain spectrum (Li–Wan sieve = elliptic-code weight distribution): one instrument for P(decomp) variance, coincidence excess kappa and target preselection

**Bottleneck.** The prime-field relation stage (B1/B3).
- LEAD-ICE-decomposition-probability-audit: "reporting the exact count vector c_D and its
  variance against a size-matched random base".
- LEAD-ICP-coincidence-harvest-structured-base: the kappa growth ladder, and target
  preselection as a way out of conservation.
- SO-ALGFB revisit_when: "... or a base raises coverage or variance with an excess that grows
  with N".
- LEAD-ICE-semaev-yield-model-coset-typing: the m! factor.

**External ingredient.**
- Li–Wan, "A new sieve for distinct coordinate counting", Sci. China Math. 53(9):2351–2362
  (2010) (retrieved via search: bibliographic data and abstract). It counts distinct-coordinate
  solutions with p(m) terms (the symmetric case) instead of 2^{C(m,2)}.
- Used for elliptic-code minimum distance by Li–Wan–Zhang 2015 (retrieved abstract).
- Through Cheng's Theorem 1, c_D(R) is exactly the number of minimum-weight codewords of
  C_L(D, R + (m-1)O) up to scalars, i.e. the weight distribution of the elliptic-code family.

**Mechanism.**
- Let û(t) = Σ_{P∈D} ω^{t·log P} over Z/N. Then
  c_D^{dist}(R) = (1/N)·Σ_t ω^{-t·log R}·Σ_{λ⊢m} ε_λ z_λ^{-1} ∏_i û(λ_i t).
  - The multiset version drops ε_λ. The ordered version is û^m.
- One length-N FFT gives c_D(R) for every target R and every arity m.
- Σ_R c(R)^2 is the m-fold additive energy E_m(D) (an exact identity), so
  Var_R c = E_m/N - mean^2.
- kappa of EXP-PFDR-ca5e01 is the non-trivial part of E_2 divided by its null mean.
- The preselection gain for any feature φ(x(R)) is max over φ-classes of the class mean of c
  divided by the global mean. It is exact, with no sampling.
- This identity ties together three leads that are currently measured separately. It also links
  them to LEAD-EXO-dl-character-sum-pseudorandom (the same û coefficients).
- **Identity checked (this session, toy; `coding-isd/check_c3_kappa_identity.py`, output
  `c3_kappa_identity_out.txt`).** The ca5e01 count C(F) = Σ_{s≠O} binom(m_s, 2) equals
  Σ_{s≠O} binom(c_2^{dist}(s), 2) from the FFT. Brute force agreed with the FFT on 3/3 windows
  (540/540, 490/490, 586/586). So kappa is computed exactly from the count vector, not merely "a
  related second moment".
- **Dual arm for EXP-PFDR-bb0d26.** bb0d26 counts F_p-additive pair sums of x-labels
  (u + v = s mod p). The same sieve over Z/p computes it exactly, without curve logs. Brute force
  agreed with the FFT on 1/1 log-GAP label set (1099/1099).

**Geometry classification and exclusion rule. Needed before the census can decide anything.**
- Each base must be classified first. A **coordinate-defined** base has membership decided by
  x(P): the ca5e01 window (x-interval) and the rank-d "label GAP" (x0 + a + c·w1 + e·w2 mod p, an
  x-coordinate GAP), plus subgroup and coset bases.
- A **group-defined (log-defined)** base has membership defined by group combinations of known
  points: the ca5e01 planted base {±kG}, and the bb0d26 "log-GAP" Q = Σ c_i P_i over small
  coefficient boxes.
- **Exclusion rule:** a curve-group energy excess on a group-defined base is a known-log pool and
  does not count as a relation source, by LEAD-ICB-generic-table-oracle: "Target-dependent and
  walk-carried bases are known-log pools (H-BINSTD-1447cf)". The pilot's planted log-AP
  (δ̂ = 0.50–0.78) is exactly this case.
- For log-GAP bases the relevant coincidence is the F_p-additive x-label count of bb0d26, the
  dual sum-product probe. C3 measures it with its dual arm, not with the log-domain arm.

**The current next step points at an experiment that does not measure c_D.**
LEAD-ICE-decomposition-probability-audit's next_action says "Run BATCH-79a580 ... for
EXP-RELN-dc761f, reporting the exact count vector c_D and its variance". But EXP-RELN-dc761f's
specification (version 1, objective) measures short-cycle (length 3 and 4) enrichment of the
honest 2-LP summation multigraph against degree-preserving rewires. It does not measure the c_D
variance. C3 is the step that measures what the lead row asks for.

**MEASURED (this session, toy; `coding-isd/check_c3_spectrum_pilot.py`; `c3_pilot_ladder.txt`,
v1, and `c3_pilot_ladder_v2.txt`, size-matched subgroup bases).**
- Setup: symmetric bases sized so that the mean distinct-subset count is about 1; m ∈ {2, 3, 4};
  8 size-matched random symmetric nulls per cell; FFT rounding error ≤ 2e-11.
- Mean c is identical to the null to 4 decimals in every size-matched cell, as conservation
  requires.
- Variance ratios are in the table below.

Pilot ladder v2: bits 16 (4 curves), 18 (3) and 20 (2). Distinct-subset counts at every target
R ≠ O. Var ratio = Var_R c / mean over the null of Var_R c. δ̂ is the OLS slope of log(var ratio)
on log N (summary in `c3_pilot_v2_summary.txt`).

| base | m | cells | var/null range | δ̂ (se) | Σc²/null range |
|---|---|---|---|---|---|
| small_x window | 2 | 9 | [0.984, 1.021] | −0.0039 (0.0030) | [0.992, 1.010] |
| small_x window | 3 | 9 | [0.966, 1.038] | +0.0036 (0.0068) | [0.975, 1.027] |
| small_x window | 4 | 9 | [0.887, 1.074] | +0.0092 (0.0186) | [0.908, 1.060] |
| x ∈ μ_d subgroup | 2 | 5 | [0.996, 1.013] | −0.0024 (0.0029) | [0.998, 1.006] |
| x ∈ μ_d subgroup | 3 | 5 | [0.987, 1.008] | −0.0028 (0.0035) | [0.990, 1.006] |
| x ∈ μ_d subgroup | 4 | 5 | [0.929, 1.010] | +0.0184 (0.0111) | [0.942, 1.008] |
| planted log-AP (positive control) | 2 / 3 / 4 | 9 each | [92, 1524] | +0.500 / +0.683 / +0.780 | [46, 1227] |

- Across 42 structured cells, 3 have |z| > 2.5 against an 8-sample null SD. A t_7 tail predicts
  about 1.7, so this is consistent.
- Every structured δ̂ has its 2-se upper bound ≤ 0.046. That is below δ*(h = 4) = 0.143 and
  δ*(h = 2) = 0.333.
- The planted control is flagged in 27/27 cells, and its growth is detected.
- This is a toy pilot (2–4 curves per rung, ≤ 20 bits). It is preliminary support for the null
  prediction, not the census the first step asks for.
- The v1 file `c3_pilot_ladder.txt` has subgroup cells that are not size-matched (|D| < B). They
  are void and superseded by v2.

**(Representation, operation set).**
- As an instrument it uses the log-domain indicator, which is known on toy curves.
- The bases tested are R1 (x-coordinate-defined sets).
- Operation set: translation by base elements. Trichotomy: **partial-action** (Class I).

**SO codes touched, with the premise escaped.**
- **SO-ALGFB**, quoted under C1. **Not escaped**: the mean-yield conservation is reproduced
  exactly. The instrument evaluates the revisit_when clause ("variance with an excess that grows
  with N") exactly, at every target.
- **SO-TABLE**, quoted under C1. Not escaped: harvested coincidences are still table relations.
  C3 decides whether there is any excess worth harvesting.
- Nearest exhausted lead, LEAD-EXO-dl-character-sum-pseudorandom: "R = C_EC/C_null is flat at
  about 1.28-1.34, i.e. the curve behaves like a random set up to a constant ..." The E_m are
  moments of the same coefficients.

**First discriminating step.**
- Geometries: the log-domain arm on the coordinate-defined EXP-PFDR-ca5e01 geometries (window,
  rank-d x-GAP, subgroup, coset), with the planted {±kG} / log-AP as the positive control. The
  dual Z/p arm runs on the EXP-PFDR-bb0d26 log-GAP label sets. Each geometry is classified before
  any reading.
- This is what LEAD-ICE-decomposition-probability-audit's next_action asks for (the c_D count
  vector and variance), which EXP-RELN-dc761f does not measure.
- Ladder: bits 16–28 (FFT length N ≤ 2^28 via Bluestein or NTT, about 4 GB at the top). At least
  8 curves per rung; m ∈ {2, 3, 4, 5}; ordered, multiset and distinct conventions.
- Fit δ̂: the slope of log(E_m ratio) and of log(variance ratio) against log N, compared with
  δ*(h) = 1/(2h-1) from IDEA-20261018-a0830c.

| outcome | disposition |
|---|---|
| |δ̂| 95% CI inside [-0.02, 0.02] and ratios in [0.95, 1.05] | LEAD-ICP-coincidence-harvest-structured-base → exhausted_at_scale (sub-break-even by law, δ < δ*/10); LEAD-ICE-decomposition-probability-audit → closed_obstructed(measured), "KN-FIND-007 holds to second order at every target", reached size recorded; the SO-ALGFB revisit_when is answered negatively at toy scale |
| δ̂ CI lower bound ≥ δ* for a coordinate-defined base | open_next_step, best_measured = (base, m, δ̂); price end to end against matched rho |
| δ̂ ≥ δ* only on group-defined bases (log-GAP, planted) | excluded as a known-log pool; no change to the disposition |
| Planted log-AP not flagged | O-ARTIFACT |

**Tier.** X: it decides an exponent-relevant growth law, with a null outcome predicted.

**Predicted gain.** 0.
- PREDICTION: variance and E_m ratios in [0.95, 1.05], δ̂ ∈ [-0.02, 0.02], and preselection gain
  ≤ 1 + O(N^{-1/2}) for any φ of bounded description.
- H-C3.1: for x-coordinate-defined D, the multiset {log P : P ∈ D} matches a uniform random
  B-subset of Z/N in Fourier moments up to order 2m ≤ 10. Rigorous half: Parseval plus exact mean
  conservation (KN-FIND-007). Classical half: the random-subset moment formula E_m ≈
  B^{2m}/N + m!·B^m. Support: EV-ECDLP-f83a17 (R flat), EXP-PFDR-ca5e01 (kappa ∈ [0.889, 1.103]),
  and the toy pilot here.
- H-C3.2: the slope law of IDEA-20261018-a0830c (an excess matters only if it grows as N^δ with
  δ ≥ δ*).

**Cost.** Implementation about 1 day (native log table, FFT, sieve). Compute O(N log N) per base:
about 1 minute at N = 2^28 plus a 2^28-step log walk, so the whole ladder is under 1 core-day.
The pilot ran in minutes in Python.

**Self-kill risk.** High that the result is null (it is predicted to be). There is also a medium
risk that a reviewer considers kappa already settled by EXP-PFDR-ca5e01. That experiment did not
measure growth with N (EV-PFDR-ad6274 says so), nor higher m, nor all targets. C3 is exact and
cheaper.

**--match phrasings:**
1. own: "exact decomposition count vector over all targets from the log-domain Fourier spectrum
   of the factor base via the Li-Wan distinct-coordinate sieve and additive energy" →
   LEAD-ICB-kic-golden-base-exact-decomp (19), LEAD-EXO-dl-character-sum-pseudorandom (17),
   LEAD-ICP-coincidence-harvest-structured-base (17).
2. plain: "count for every target how many ways it splits over the factor base and test whether
   structured bases cluster more than random ones" →
   LEAD-ICP-coincidence-harvest-structured-base (19).
3. obstruction vocabulary (SO-ALGFB / KN-FIND-007): "mean per-target yield conservation
   binomial(B+m-1,m)/N with a variance excess or coverage gain that grows with N" →
   LEAD-ICE-decomposition-probability-audit (7), LEAD-ICP-coincidence-harvest-structured-base (7).

---

## 3. What the field does not give

- **Prime-field B1/B2.** Every coding-theory decoder or ISD algorithm either sits inside SO-TABLE
  (ISD) or never reaches the decomposition regime (algebraic decoders, L2). The field contributes
  a closure (C1) and two exact instruments (C2, C3), not a sub-rho oracle. I found no coding-theory
  ingredient that escapes SO-ALGFB's membership premise. Every route I checked (K6, K11, K12) runs
  into it.
- **B3.** Decided by SO-TABLE's slope (K10): fitted exponent ≈ 0.61 against rho's 0.50.
- **Binary/Koblitz B4–B5.** Rank-metric (K7) and quasi-cyclic (K5) structure reduce to known
  closures. I did not manufacture a binary candidate.
- **B6.** The AG automorphism / invariant-degree bound (K9) is vacuous for generic discriminants.
- **B7.** Only the C2 secondary arm.

## 4. Citations

| citation | provenance | used for |
|---|---|---|
| Q. Cheng, Hard problems of algebraic geometry codes, arXiv cs/0507026 (2005); IEEE Trans. IT 54 (2008) | retrieved (PDF text, Thms 1–2; journal venue recalled) | dictionary §0, C1 |
| V. Guruswami, M. Sudan, Improved decoding of Reed–Solomon and algebraic-geometry codes, IEEE Trans. IT 45(6):1757–1767 (1999); ECCC TR98-043 | retrieved (abstract) | C1 L2, C2 |
| R. Canto Torres, N. Sendrier, Analysis of information set decoding for a sub-linear error weight, PQCrypto 2016, LNCS 9606:144–161 | retrieved (abstract via search) | C1 L3, K2 |
| J. Li, D. Wan, A new sieve for distinct coordinate counting, Sci. China Math. 53(9):2351–2362 (2010) | retrieved (bibliographic data and abstract via search) | C3 |
| J. Li, D. Wan, J. Zhang, On the minimum distance of elliptic curve codes, arXiv 1501.01138 (2015) | retrieved (abstract) | §0, C3 |
| C.-P. Jeannerod, V. Neiger, É. Schost, G. Villard, Computing minimal interpolation bases, arXiv 1512.03503 | retrieved (abstract) | C2 cost |
| H. Cohn, N. Heninger, Ideal forms of Coppersmith's theorem and Guruswami–Sudan list decoding, arXiv 1008.1284 / ICS 2011 | retrieved (abstract via search) | K8 frame |
| M. Alekhnovich, Linear Diophantine equations over polynomials and soft decoding of RS codes, IEEE Trans. IT 51(7) (2005) | retrieved (bibliographic data only) | C2 cost (alternative) |
| Parvaresh–Vardy 2005; Guruswami–Rudra 2008; Guruswami–Xing 2012/2013 (folded/capacity codes) | recalled | K3 |
| Sendrier, Decoding one out of many, PQCrypto 2011 | recalled | K5 |
| Bardet et al. 2020, MaxMinors / Support-Minors | recalled | K7 |
| Petit–Kosters–Messeng PKC 2016; Amadori–Pintore–Sala | recalled (and internal KR-IC-5931ee) | K6 |
| Nagao 2010; Diem 2011; McGuire–Mueller | recalled (and internal KR-IC-5931ee) | K11 |
| Stichtenoth 1990 (automorphisms of geometric Goppa codes) | recalled | K9 |
| Roth–Ruckenstein root finding | recalled | C2 |
| Ahmadi–Shparlinski arXiv:1302.4210 (Theorem W, d = 1) | retrieved by the program (H-ECDLP-f6a43a), not by me | C2 |

## 5. Files

All under `/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/scout/coding-isd/`:
`ec_toy.py`, `check_c1_dictionary.py` and `c1_dictionary_out.txt`, `check_c2_gs_pilot.py` and
`c2_pilot_b10.txt` / `c2_pilot_b11.txt`, `check_c3_spectrum_pilot.py` and `c3_pilot_ladder.txt`
(v1, which has a subgroup size-matching defect) / `c3_pilot_ladder_v2.txt` (v2) /
`c3_pilot_v2_summary.txt`, `check_c3_kappa_identity.py` and `c3_kappa_identity_out.txt`,
`match-coding.txt` (the matcher outputs), and `dl/cheng2005.{pdf,txt}`.
