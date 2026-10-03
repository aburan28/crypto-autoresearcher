# TASK-20261001-9b3e70: generic-class corollary interface (D1), hybrid-oracle question (D2), open non-generic routes (D5)

- **Author:** idea-generator, independent session, policy research-deep. Written 2026-10-01 and 2026-10-02 (the session was interrupted by an API session limit and resumed on the Coordinator's message; no instruction changed).
- **Zero scientific runs. No implementation.** Every number below is either quoted from a named record or is hand arithmetic, labelled **scratch**. None is a measurement.
- **Not committed. No status changed.** The draft records are in `proposed-records/`.
- **Scope of every statement, unless a line says otherwise:**
  - **Curves:** binary curves E/F_{2^n}, with n in {97, 109, 131, 163, 191, 233, 239, 283, 409, 571}. Each n is a parameter label.
  - **Group:** the prime-order subgroup ⟨P⟩, of order ℓ.
  - **Factor base:** F = F_V = {Q ∈ ⟨P⟩ : x(Q) ∈ V}, where V is an F_2-subspace. |F| = 2^d in the v2 convention.
  - **Algorithm:** m-summand index calculus, with m ≥ 2 and s ≤ ⌊m/2⌋ unless stated.
  - **Oracle class:** as stated per line.
  - **Security:** no statement about the security of any deployed curve, in either direction.

---

## 0. One-page summary

**D1: the corollary's interface.**
- **What the corollary covers.** Wagner 2002 Cor. 1 rests on Dai's reduction and Shoup's bound. It covers an index-calculus relation phase only when the harvester meets all of these conditions:
  - It touches group elements only through the generic oracle of Shoup's model. That means group operation, inverse and equality, with encodings visible, so hashing and tables are allowed.
  - It receives F as a list of handles and tests membership in F only by lookup in that list.
  - Its cost and success guarantee still holds when F is replaced by a uniformly random list closed under the automorphisms the algorithm can detect generically: negation always, and ⟨±λ_π⟩ on Koblitz curves when applied as [λ].
- **What the corollary then gives.** Under those conditions, the cost to output the first non-trivial relation is at least c·√ℓ group operations. This holds at any memory and needs no heuristic. Building the target list and reading F are included, as the index calculus pays both anyway.
- **Where the corollary stops.** Its boundary is exactly Dai's requirement of random known-representation lists. Anything that reads coordinates is outside it:
  - the membership test x(Q) ∈ V;
  - summation polynomials and Weil descent;
  - approximate F_2-linear x-filters;
  - halving and trace tests;
  - Frobenius applied by squaring;
  - the Riemann–Roch oracle behind the program's own m = 3 anchor.
- **Three further limits:**
  - The corollary bounds Ω(√ℓ) with an **unspecified constant**. It does not bound "0.886·√N". That constant-level clause holds only inside the v2 model, as an algebraic identity.
  - It bounds the **first** relation, not the amortized rate.
  - It says nothing about a **preprocessing** reading, where the table is built once for many instances. That reading belongs to Corrigan-Gibbs–Kogan and Bernstein–Lange (KR-RHO-ea34b8).

**D2, question (C): answered, and it is a flag.**
- **Model pinned first.** In the v2 header, PROBE·FILL = m!·N·|F|. This is the "shared-table line" T·M ≈ |F|ℓ.
- **Literal result: (C-yes).** The card's numeric (C-yes) trigger is T·M < |F|ℓ/4 at per-relation cost below √ℓ. That trigger is **met by known generic algorithms**:
  - **PCS batched multi-collision harvesting.** Source: J3 O2 and AMD-20261001-e61f2b X-6. Scratch numbers at n = 131, d = w = 10:
    - T = 2^71.5 and M = 2^10, so T·M = 2^81.5, against |F|ℓ/4 = 2^137.
    - Per relation: 2^61.5, against √ℓ = 2^64.5.
  - **Dense-regime golden-collision decomposition search.** By derivation sketch, this enters the same multi-collision regime once the per-target half-domain exceeds about √ℓ.
- **Why it fires, and why it matters little.** The trigger fires because its two thresholds are not generic invariants. The generic invariants are:
  - total T ≥ c·√ℓ for the first relation (Cor. 1);
  - total T ≳ c·√(Kℓ) for K relations (multiple-DL type, conditional on one named missing step);
  - T²·M ≈ K²ℓ for collision-type harvesters (Dinur, random-function model).

  Amortisation alone drives the per-relation cost below √ℓ. **No sub-rho cell results.** The best constructed generic cell at n = 131 is 2^71.5, which is 7.17 bits above the vOW column.
- **Status of the flag.** Per the card I **stopped deriving** at that point. This is written up as an **escalated candidate, not a claim** (§2.5), and flagged for rule-12 routing. The candidate is a 1999 algorithm that DEC-20261001-5c9e7a R3 has already read (J3 O2) and ruled non-escalating. My reading is that this is a trigger-wording collision of the PD-7 kind. That is the Coordinator's call.
- **Effect on P3.** (C-yes) in this literal sense does **not** void P3 of H-SEMBIN-8e7ae3 beyond what R6 already withdrew. Voiding P3 needs a sub-rho cell, and Cor. 1 excludes one for every generic hybrid.
- **Single named missing step.** This is the step for the sharpened harvesting bound that D3 needs: a generic lower bound for solving any K of L ≥ K DL instances of the solver's choice, of order Ω(√(Kℓ)). It is an extension of Yun 2015 and Hhan 2024 Thm 3.4.

**D3: the restated heuristic.** **HEUR-HARVEST-FV**, with two numbered clauses (`proposed-records/heuristic-restatement.md`).
- **Clause 1, distributional.** F_V's additive statistics match those of a uniformly random negation-closed list. These are the non-trivial 2-sum coincidences and the per-target decomposition counts.
- **Clause 2, algorithmic.** No harvester in the semi-generic class (generic operations plus unit-cost membership test x(Q) ∈ V plus Frobenius) outputs K = |F|+2 full-rank relations in fewer than (1/8)·K·√(ℓ/min(M, K)) operations, fill charged.
- **Falsified by** either of:
  - (1) a non-trivial-coincidence count, or a decomposition-count distribution, departing from the null at p < 10^-3 (Bonferroni) while the null and the positive control pass;
  - (2) an exhibited harvester below that line at any tested (n, dim V, M) over ≥ 30 instances.

**D4: the draft hypothesis.** `proposed-records/H-SEMBIN-c7e1d4.yaml`. Status `proposed`; it supersedes H-SEMBIN-8e7ae3 on commit. It carries R6's wording with four stated, reasoned differences (D4 §statement_differences).

**D5: open routes.** Four candidate KN-OPEN texts (§5):
- approximate characteristic-2 x-filters;
- FFDA-type solving degree;
- the semi-generic membership-class lower bound;
- Frobenius beyond orbit bookkeeping.

**Recommended next act:**
1. The Coordinator rules on the §2.5 flag first. Rule-12 convening or a recorded trigger-wording deviation is its call.
2. Then TASK-20261001-d815a6 archives this directory.
3. The cheapest next discriminator is HEUR-HARVEST-FV clause 1's toy statistic (heuristic-restatement §5, sample V1). It needs about 2^24 group operations per cell, which is seconds. Designing it is a later task.

---

## 1. The model, pinned before anything was derived

Read in full in this session:
- `specification.yaml` cost_model, controls, A1–A8;
- the v1 driver `code/memory_charged_family.py`;
- `AMD-20261001-e61f2b`, including its v2 header block.

**Not opened:** `code/v2/`, any v2 run directory, and `RESULTS-amd-e61f2b.md`. A directory listing on resumption (2026-10-02) showed that `code/v2/` now exists. Its files were not opened, per the card.

**The v2 model, quoted (amendment header).** All terms are log2.

```
K = d; TPR = N + L - m d; CALLS = K + TPR; PROBE = K + TPR + o
o: ENUM (m-1)d; MITM (m-S)d; MITM_CAPPED (m-s)d, s = min(S, floor(log2 B / d))
FILL = s d (table models, s >= 1); LA = 2d; TOTAL = log2(2^PROBE + 2^FILL + 2^LA)
VOW = log2(0.886) + N/2; N = log2 r ~ 129.000 at n = 131, n elsewhere
```

**Consequences used below.** These are scratch algebra and agree with J1 S6 and the blind identity I1.

- **(M1) The shared-table identity.** For every table model and every m, s, d:

      PROBE + FILL = (d + N + L - md + (m-s)d) + sd = N + L + d.

  That is, 2^PROBE · 2^FILL = m!·N·|F|. Writing T = 2^PROBE and M = 2^FILL, this is the line T·M = m!·N·|F|. IDEA-20260930-4b7d1e writes it as "T·M ~ |F|ℓ", dropping m!.
- **(M2) The floor.** By AM-GM, TOTAL ≥ 1 + (N + L + d)/2. This exceeds N/2 + log2(0.886) by at least 1.17 + (L + d)/2 > 0 for every m ≥ 2 and d ≥ 0.
  - Scratch check at n = 131, m = 8, d = 20.55: L = log2 40320 = 15.30, so 1 + (129.00 + 15.30 + 20.55)/2 = 83.43. That agrees with E-2's 83.44 to 0.01.
  - E-2 is a reviewer-derived expectation, not a measurement.
- **(M3) ENUM** has FILL = 0 and PROBE = N + L + d > N/2. Its membership test is unspecified in the contract: "test whether the remainder lies in F". This matters in §3.3.

**Note on the dense regime, and not a defect claim.** At the E-2 optimum (n = 131, m = 8, d ≈ 20.55), TPR = 129.00 + 15.30 − 164.4 ≈ −20.1 (scratch). Each target has about 2^20 decompositions, and the relation phase needs CALLS ≈ 0.45, i.e. about 1.4 full MITM passes. The model is consistent there: one full pass over one target yields all of that target's decompositions as relations. C-2's guard (CALLS ≥ 0) is satisfied. I record it because the minimum of the model lies in the regime where §2.4's dichotomy matters.

---

## 2. D2: the hybrid-oracle question (C)

### 2.1 The question as posed

IDEA-20260930-4b7d1e (C) asks whether a hybrid beats the shared-table line T·M ≈ |F|ℓ without paying about √ℓ per relation. A hybrid here means a target-independent shared table plus per-target golden-collision search. The card's trigger for (C-yes) is T·M < |F|ℓ/4 at per-relation cost < √ℓ.

### 2.2 The comparator line is not a generic frontier

Write K = |F| (relations needed, v2 convention) and w for stored distinguished points.

**PCS batched harvesting.**
- **Source:** J3 report §2 (`retrieved`, vOW §4.2 read at source by J3, and by me in this session at lines 318–417); AMD X-6.
- **Construction (J3):** a walk X → f(H(X)) on ⟨P⟩, with f(u) = a sum of m−1 factor-base points plus aP + bQ. With H injective, every collision is a relation.
- **Cost:** 2 + d + (N − w)/2 at memory 2^w, for w ≤ d (X-6, log2).

**Scratch arithmetic (log2):**
- T·M = 2 + d + (N + w)/2. Against |F|ℓ/4 = d + N − 2, T·M is below exactly when **w < N − 8**.
- Per relation, T − d = 2 + (N − w)/2. This is below N/2 exactly when **w > 4**.
- So the card's trigger holds for every 4 < w ≤ d, at every listed degree.

**The n = 131 instance** (N = 129.00, d = w = 10):

| quantity | value (log2) | comparator (log2) |
|---|---|---|
| T | 71.5 | VOW 64.33; PUB 60.81 |
| M | 10 | — |
| T·M | 81.5 | \|F\|ℓ/4 = 137.0 |
| per relation | 61.5 | √ℓ = 64.5 |
| T − VOW | +7.17 | J3 reports +7.17 |

**Why no sub-rho cell follows.** T − N/2 = 2 + d − w/2 ≥ 2 + d/2 > 0 for every w ≤ d. The excess over VOW is 2.17 + d − w/2 (scratch).

**What the frontier actually is.** The literature frontier for collision-type harvesting is T²·M = Θ̃(K²·ℓ) for M ≤ K. Source: Dinur 2020 via KR-RHO-7d93f6, abstract-read, random-function model. PCS meets it.

The shared-table line T·M = m!·N·|F| (M1) lies above PCS at every memory M = 2^w < ℓ/256. Scratch: this is w < N − 8 above, against the card's |F|ℓ/4 comparator. **The shared-table line is the frontier of nothing.** It is the cost of one algorithm.

### 2.3 Why per-relation √ℓ is not a generic invariant

Cor. 1 (§3) bounds the **first** non-trivial relation at c·√ℓ. Amortisation over K relations is bounded only by the multiple-instance bound:
- **Bound:** Ω(√(Kℓ)) in total, i.e. a per-relation cost of order √(ℓ/K).
- **Sources:**
  - KR-RHO-46c2c6 (`internal`; sources abstract-read).
  - Yun 2015, ePrint 2014/637. Abstract `retrieved` this session: "tight generic lower bound … O(√(np))".
  - Hhan 2024, arXiv 2402.11269, Thm 3.4, `retrieved` (HTML) this session: Pr ≤ O((e(T+2m+1)²/(2m|G|))^m).

The card's per-relation threshold √ℓ is therefore crossed by amortisation alone, by any batched generic harvester. That is why the trigger fires on a 1999 algorithm.

### 2.4 Strict hybrids (shared table plus per-target golden collision): the dichotomy, a sketch

This is a derivation, unreviewed. It relies on vOW §4.2 eq. (4) and §5.3 eq. (8), read at source this session (lines 318–417 and 682–749).
- **Model:** take a per-target split into half-domains of size n_h ≤ n_h' with per-target memory w ≤ n_h.
- **Golden collisions per target:** k ≈ n_h·n_h'/ℓ', where ℓ' absorbs split multiplicity.
- **Sparse regime, k ≤ 1:**
  - per relation ≈ 7·n_h'·√(n_h/w)/k = 7ℓ'/√(n_h·w);
  - with w ≤ n_h ≤ √ℓ', this is ≥ 7√ℓ'.

  This is IDEA claim (B), and it holds **only in the sparse regime**. The table only raises coverage n_h', which is already inside k.
- **Dense regime, k ≫ 1:**
  - the same expression 7ℓ'/√(n_h·w) can fall below √ℓ when n_h·w ≳ 49ℓ';
  - as n_h → ℓ, the compression g: R → I×{1,2} becomes injective, every collision is a real group equality, and the search becomes PCS batching.

  IDEA claim (B) is therefore **false as worded outside the sparse regime**. Literature-screen §2c step 2 sets C = |S|/2k with memory w = C. That is the sparse optimum, not a bound over w.
- **Where I stopped.** Exact dense-regime numbers need a coupon correction: one decomposition is 70 golden collisions at m = 8, S = 4. **I did not compute them. Per the card I stopped deriving here.**

### 2.5 Escalated candidate: flagged for rule-12 routing, not claimed

```yaml
candidate:
  label: C-YES-LITERAL
  what: >-
    The card's (C-yes) numeric trigger (T*M < |F| l / 4 at per-relation cost
    < sqrt(l)) is met by (i) PCS batched multi-collision relation harvesting
    (J3 O2; AMD-20261001-e61f2b X-6), at n = 131, d = w = 10: T*M = 2^81.5
    against 2^137, and 2^61.5 per relation against 2^64.5 (scratch); and (ii) by
    derivation sketch, by per-target golden-collision decomposition search in
    the dense regime (section 2.4).
  is_it_a_hybrid: >-
    (i) No. It is not a decomposition oracle, and its DP store depends on Q.
    (ii) Yes, a strict hybrid, but only in the dense regime. Numbers are not
    derived, because the stop rule fired.
  sub_rho: >-
    No. Every generic route has T >= c*sqrt(l) by Cor. 1. The best constructed
    cell is +7.17 bits over VOW at n = 131.
  exponent_moving: no
  novelty_status: known
  prior_art:
    - "vOW 1999 sections 4.2 and 5.3 (KN-LIT-73f7e1, retrieved)"
    - "Dinur 2020 via KR-RHO-7d93f6 (internal; abstract-read)"
    - "J3 report O2 (TASK-20260928-62ad14), already read by DEC-20261001-5c9e7a (composition J3; R3)"
  why_flagged_anyway: >-
    The card makes the trigger's appearance a stop-and-escalate event. Whether a
    numeric trigger met by a non-sub-rho, already-adjudicated algorithm convenes
    the review-breakthrough tier at max is the Coordinator's decision under
    DEC-20261001-5c9e7a R3 mandatory_revisit (i). That condition is worded as "a
    sub-rho or exponent-moving decomposition oracle ... including (C-yes)".
  recommendation_not_a_ruling: >-
    Record it as a trigger-wording collision, of the PD-7 kind. Re-word any
    future trigger on the generic invariants of section 2.3 (T vs c*sqrt(K l);
    T^2 M vs K^2 l) rather than on per-relation sqrt(l) or T*M ~ |F| l.
  effect_on_P3: >-
    None beyond R6. Voiding P3 would need a sub-rho cell. IDEA-20260930-4b7d1e's
    inference "(C-yes) => P3 void" is invalid as stated.
```

### 2.6 proof_search_map for D2 (inventor-protocol §8, all four audits)

```yaml
proof_search_map:
  bottleneck: >-
    The step "a hybrid harvester pays at least min(sqrt(l), l/coverage) per
    relation" (IDEA-20260930-4b7d1e). It holds only in the sparse regime
    (section 2.4) and is not a generic invariant (section 2.3).
  baseline_embedding:
    parameter_slice: >-
      K = 1 relation against a list with known logs, m = 2 split as table plus
      probe, FILL = log2 M, PROBE = N - log2 M. TOTAL >= N/2 + 1 at M = 2^(N/2):
      BSGS, 2*sqrt(l) operations at sqrt(l) store. The PCS slice K -> 1
      reproduces vOW rho, sqrt(pi l / 2) per KN-LIT-73f7e1 eq. (5).
    reproduction_check: >-
      Symbolic, scratch, done here. It is identity (M1) with L = 0, K = 0 (log2
      of 1), o = 0. A frozen numeric fixture is owed to the v2 receipt, which
      this task must not read.
  observation_collision:
    observable: "(T, M, per-relation cost) of a harvester"
    distinct_preimage_search: >-
      FOUND. PCS batching (not a decomposition oracle) and a dense-regime
      golden-collision decomposition search have the same observable regime
      (T^2 M ~ K^2 l), but sit on opposite sides of the "hybrid" definition. The
      card's trigger cannot separate them, so the trigger is not identifying the
      class it names. Separator: the generic invariant total T versus
      c*sqrt(K l), which neither crosses.
  constructive_transforms:
    - transform: stronger_invariant
      proposed_object: >-
        Replace (T*M, per-relation sqrt l) by (total T versus c*sqrt(K l);
        T^2 M versus K^2 l) as the harvesting invariant.
      predicted_gain: >-
        A trigger that a 1999 algorithm cannot fire. Adopted in D3 clause 2.
  quantifier_order: >-
    FOR ALL generic harvesters H (Shoup model, list interface, random-closed-
    list guarantee), FOR ALL m >= 2, s, d, M: T_first(H) >= c*sqrt(l). EXISTS c
    > 0 uniform in everything, but not stated numerically by any source opened.
    The K-relation form, T(H) >= c*sqrt(K l), is conditional on the missing
    K-of-L step. The per-relation sqrt(l) form is FALSE as a for-all statement:
    PCS is a witness.
  method_ceiling:
    strongest_certifiable_claim: >-
      Generic class: no sub-rho cell at any memory (Cor. 1, sota_delta 0 against
      KN-LIT-011). Nothing about non-generic oracles.
    nearby_object_control: >-
      m = 3, s = 1. PASSES on the oracle axis: the vOW per-target golden
      collision with n1 = |F|, n2 = |F|^2 and w = |F| costs 7|F|^2 against
      PMITM's |F|^2, so it predicts NO gain (log2 7 = 2.81 bits worse, scratch).
      It is also outside vOW's validity range, since w <= |S|/2^10 fails at
      w = |F|. NOT DISCRIMINATING on the harvesting axis: PCS batching beats the
      shared-table line at m = 3 too, because its cost is m-independent. That is
      the comparator's failure, not a predicted per-target gain, and it does not
      touch the measured m = 3 per-target anchor (unconferred grade, A8).
  proof_obligations:
    - claim: "(M1) PROBE + FILL = N + L + d for every table model"
      responsibility: baseline
    - claim: PCS-batch numbers per X-6 formula, and trigger region 4 < w <= d
      responsibility: runtime
    - claim: "sparse-regime per-relation cost >= 7 sqrt(l') (vOW random-function model; G1/G2 of IDEA-20260930-4b7d1e)"
      responsibility: runtime
    - claim: dense-regime limit equals PCS batching (sketch only; stopped)
      responsibility: strictness
    - claim: no generic route below c*sqrt(l) (section 3)
      responsibility: interface
  not_applicable_reason: null
```

### 2.7 D2 dominated_by and sota_delta

- **dominated_by:**
  - The candidate harvesting algorithm is dominated by vOW parallel rho in time at every memory (KR-RHO-6239aa). At n = 131 that is +7.17 bits against the VOW column and +10.69 against the published 2^60.809 (scratch).
  - Rho also uses less memory.
  - On Koblitz curves rho additionally gains √(2n) (KR-RHO-037e22).
  - Under a free-table (preprocessing) reading, KR-RHO-ea34b8 / KN-LIT-7cc07f dominate.
- **sota_delta:** time +7.17 bits (worse) against VOW at the best constructed generic cell. Memory: none better than rho. Data and queries: none. As a contribution: the conceptual correction of a trigger. No attack.
- **Rows checked:**
  - all 24 KR-RHO rows by claim line;
  - KR-RHO-13bf67, -ea34b8, -46c2c6, -7d93f6, -6239aa, -037e22, -0528e7 and -fbd7b1 in full;
  - KN-LIT-011, -012, -013, -73f7e1 and -7cc07f in full.

---

## 3. D1: the generic-class corollary and its interface

### 3.1 The corollary, as cited, not re-proved

| ref | provenance | claim relied on | verified_by |
|---|---|---|---|
| Wagner 2002, CRYPTO, §3 Thm 2 (Dai) and Cor. 1 | retrieved (by J3) | "Every generic algorithm for the k-sum problem in a group G has running time Ω(√p)", proved from Dai's reduction plus Shoup. Dai's reduction uses lists of random known-exponent elements. | TASK-20260928-62ad14 (iacr archive PDF, text extracted). **This session:** fetched the same PDF and the author's genbday-long.ps; neither was text-extractable here (no pdftoppm; bitmap-font PS). Not re-read by me. |
| Shoup 1997 (KN-LIT-011) | kb/internal; primary **unreadable** | Ω(√p) generic group operations for DL | **This session:** fetched shoup.net/papers/dlbounds1.pdf; content not extractable. KN-LIT-011 itself says "not re-read". Retrieved secondaries that state the bound: (a) Hhan, arXiv 2402.11269 (HTML read this session), Thm 3.3: Pr[A(g, g^x) → x] = O(T²/\|G\|), **Maurer's model**; (b) Galbraith–Gaudry 2016 §4, retrieved by J3 (not by me); (c) Wagner §3 via J3. |
| Hhan 2024, arXiv 2402.11269, Thm 3.4 | retrieved (this session, HTML) | m-instance DL: Pr = O((e(T+2m+1)²/(2m\|G\|))^m), giving Ω(√(mp)) | this session |
| Yun 2015, ePrint 2014/637 | retrieved (abstract only, this session) | tight Ω(√(np)) generic bound for n DL instances | this session (abstract) |
| KN-FIND-b7e091 | internal | incidence and [m]-endomorphism oracles are GGM-simulable, hence closed at exponent 1/2 (prime field) | read this session |
| IDEA-20260807-070d03 | internal | a free arity-1 membership oracle gives rho: N/(2√L) draws, optimal at L = N | read this session (relevant lines) |

### 3.2 Statement

**COR-GEN.** Let H be a relation harvester for ⟨P⟩ of prime order ℓ that satisfies all four conditions:
- **(G1)** It accesses group elements only through Shoup's generic oracle: group operation, inverse and equality on random encodings. The algorithm may compute any function of the encoding strings (hash tables, distinguished points). Cost is the number of oracle calls.
- **(G2)** It receives the factor base as an input list of handles, and decides membership in F only by lookup in that list.
- **(G3)** Its success guarantee holds when the list is a uniformly random list of |F| elements closed under negation. On a Koblitz curve with σ-stable V, the list is also closed under [λ_π], where H applies π only as [λ].
- **(G4)** Targets are group elements built by H from P and Q.

Then the number of oracle calls H makes before outputting its first relation that is non-trivial in the reduction's representation is at least c·√ℓ − O(|F| + #targets). This holds at any memory. The table fill is automatically charged, because every table entry is a computed handle.

The list term is paid by any index calculus, so the whole pipeline costs at least c·√ℓ.

**Route.** This is Dai's reduction (as J3 retrieved it) with the list sampled as ±(r_j·P + s_j·Q) and known (r_j, s_j). The adaptation to a negation-closed or λ-closed list, and the "non-trivial relation" form, are **mine, derivation, unreviewed**:
- A relation Σc_j·F_j = aP + bQ that is not a formal identity gives x unless the Q-coefficient vanishes. That happens with probability about 1/ℓ.
- Including ±r_j makes the trivial pairs F_j + (−F_j) = 0 formal identities, so they are excluded.
- **sota_delta: 0** against KN-LIT-011 and KR-RHO-13bf67. This is the known theorem's interface, not a result.

### 3.3 Where it stops: oracle-by-oracle

| harvester / oracle | inside COR-GEN? | why |
|---|---|---|
| FREE (control) | n/a | charges zero; not an algorithm (exempt in C-3) |
| ENUM with membership by **list lookup** | yes | G1–G3 hold |
| ENUM with membership by **x(R′) ∈ V** (F_2-linear algebra on the coordinate) | **no** | reads coordinates; breaks G2. Covered only by HEUR-HARVEST-FV clause 2 (D3) |
| MITM, MITM_CAPPED (tables of s-sums, hashing) | yes in Shoup's model | hashing encodings is permitted in Shoup's model. **Not** covered by a Maurer-model statement alone (Hhan's Thm 3.3 is Maurer-model) |
| vOW golden-collision MITM (X-5) | yes | the compression g acts on encodings |
| PCS batching (X-6) | yes | but it is not a decomposition oracle |
| Frobenius orbit quotient with π by **squaring** (X-7, R8's A_G) | **no** | non-generic, about n field squarings. Bounded separately by R8's ceiling: ≤ 2·log2(2n) bits |
| Frobenius applied as [λ] | yes | O(log ℓ) group operations per application, so the R8 gain is consumed |
| Halving / trace test Tr(x) = Tr(a) (J3 §5) | no | coordinate. Exact gain ≤ h ≤ 4 (Theorem C) |
| Summation polynomials + Weil descent + Gröbner/SAT | no | coordinate algebra |
| Approximate F_2-linear x-filters (RC5) | no | coordinate. KN-FIND-ffe1df's additive completion assumes p > 2 |
| Riemann–Roch oracle (the measured m = 3 anchor) | **no** | function-field based. The program's single anchor measured a **non-generic** oracle that happens to reach generic cost |
| Preprocessing reading (s-sum table depends only on (E, V), built once for many targets) | **no, different theorem** | COR-GEN counts all calls for one instance. With the build amortised, the bound is Corrigan-Gibbs–Kogan S·T² = Ω̃(εN) (KN-LIT-013, abstract-read), and the comparator is KR-RHO-ea34b8 |
| Many instances (many Q) | different theorem | Yun / Hhan Thm 3.4: Ω(√(Lℓ)) |

### 3.4 Five interface facts that change wording

1. **The constant.** COR-GEN is Ω(√ℓ) with an unspecified constant. No source opened in this session states it numerically (Hhan Thm 3.3 is O(T²/\|G\|)). KR-RHO-fbd7b1 shows that generic constants vary by algorithm. So "no generic algorithm below 0.886·√N" is **not** a corollary of Shoup. Only "below c·√ℓ" is.
   - R6's wording ("no cell … below the vOW column 0.886 √N … for generic algorithms at large it is a corollary of Shoup") conflates two layers.
   - **Inside the model**, the constant-level statement is the identity (M2), with margin ≥ +16.5 bits at every listed degree per E-2. E-2 is reviewer-derived, not measured, and not read from v2.
   - **Outside the model**, only the Ω-statement holds.
2. **Dai's list.** The reduction needs random **known-representation** lists. F_V is a fixed set whose discrete logs are unknown and possibly structured. Two consequences:
   - COR-GEN binds F_V only through (G3), the algorithm's indifference to the list.
   - It says nothing about whether F_V itself has exploitable additive structure. That is HEUR-HARVEST-FV clause 1, and it is a heuristic.
3. **Detectable symmetry must be in the null list.** A generic algorithm can detect negation-closure, and on Koblitz curves [λ]-closure. The random list in (G3) must carry the same closure, or the reduction's list is distinguishable from F.
4. **First relation, not rate.** COR-GEN bounds the first non-trivial relation. The rate over K relations needs Yun-type bounds plus the K-of-L missing step (§2.3).
5. **Linear algebra is free in Shoup's metric.** COR-GEN bounds group operations only. The model's LA = 2d term is additional and unaffected.

### 3.5 D1 dominated_by and sota_delta

- **dominated_by:** "n/a (no result claimed)". The statement itself is KN-LIT-011 / KR-RHO-13bf67.
- **sota_delta:** 0 on time, memory and data/queries. The contribution is interface bookkeeping only.

---

## 4. Reserved

D3 lives in `proposed-records/heuristic-restatement.md`. D4 lives in `proposed-records/H-SEMBIN-c7e1d4.yaml`.

---

## 5. D5: non-generic open routes, as candidate KN-OPEN text

Each entry follows the same structure, and none is a closure. No closure standard is claimed. These are open questions with their measurable quantities.

### OPEN-A: Approximate sum-compatible F_2-linear x-filters on binary curves

**Statement.** Let E/F_{2^n} be ordinary, n prime, with ⟨P⟩ of prime order ℓ. Consider maps h: E(F_{2^n}) → [M], M = 2^j, j ≥ 2, computable in poly(n) from x(Q), in particular h(Q) = (Tr(α_1·x(Q)), …, Tr(α_j·x(Q))). Does any such map, together with a combining rule f, have bucket agreement

    ε = Pr_{Q,R}[ h(Q+R) = f(h(Q), h(R)) ]

with a bucket gain M·ε that grows without bound in M?

**Known.**
- The exact case (ε = 1) is impossible for M > h, by Theorem C of KN-FIND-ffe1df (internal; it transfers verbatim to the prime-order part).
- j = 1 gives exact gain 2 through the halving trace. J3 §5 recalls the criterion and checked it on exhaustive toy scratch only.
- KN-FIND-ffe1df's additive-completion degeneracy lemma assumes p > 2, so characteristic 2 is uncovered.

**What settles it.** Either of:
- a Weil/Bombieri-type bound ε ≤ 1/M + O(poly(n)·2^(−n/2)) for every non-degenerate (α, f), plus a classification of the degenerate Artin–Schreier cases in characteristic 2;
- or an exhibited filter with growing gain.

**Measurable quantity.** The J3 RC5 ladder: bucket gain against j on toy binary curves, with a SHA null and Tr(x) as the positive control.

**Exponent stake.** It could move the exponent, through Wagner/HGJ-type trees on an approximate quotient.

### OPEN-B: FFDA-type solving degree of Weil-descended summation polynomials, binary curves, prime n

**Statement.** For V ⊂ F_{2^n} an F_2-subspace of dimension d′ ≈ n/m, take the F_2-polynomial system obtained by Weil descent of S_{m+1}(x_1, …, x_m, x(R)) = 0 with x_i ∈ V. Is its solving degree (or first-fall degree) bounded by f(m), independent of n?

**Known.**
- A yes gives a heuristic subexponential index calculus.
- Galbraith–Gaudry 2016 §10.2 (retrieved by J3, not by me) records "no consensus" and that FFDA "seems to be too optimistic".
- The program's own Assumption-1 check reaches n ≤ 21 (EV-ICPERF-a8080e, as the contract cites it; not re-read here).

**What settles it.** A proof of either bound, or measured solving degrees at n from 17 to about 41 across m and d′ that show growth in n at fixed m.

**Measurable quantity.** Solving degree against (n, m, d′), with a random-system null of matched shape. The engine is IMP-SEMBIN-ENGINE.

**Exponent stake.** It could move the exponent.

### OPEN-C: Generic lower bound with a factor-base membership oracle (the semi-generic class)

**Statement.** In the generic group model augmented with a unit-cost membership oracle for a uniformly random negation-closed subset F of size |F| (with dlogs uniform), does every algorithm that outputs K full-rank relations make Ω(√(Kℓ)) calls? Separately, is the K-of-L variant of Yun's multiple-DL bound true?

**Known.**
- COR-GEN does not cover a membership oracle. "Accidental" memberships (the decomposition events) cannot be simulated without x.
- The arity-1 case gives rho exactly (IDEA-20260807-070d03, internal).
- A heuristic count is my sketch, unreviewed: relations ≲ T·|F|/ℓ + T²/ℓ, which gives T ≳ √(Kℓ).

**What settles it.** A proof, which would turn HEUR-HARVEST-FV clause 2's generic half into a theorem, or a counterexample algorithm.

**Measurable quantity.** None needed; this is a mathematics task.

**Exponent stake.** None. It can only confirm a 1/2 floor. It is a building block, ranked low unless a review needs it.

### OPEN-D: Frobenius beyond orbit bookkeeping (Koblitz curves)

**Statement.** Is there a poly(n)-computable canonicaliser for orbits of a multiplicative subgroup H ≤ (Z/ℓ)^* strictly larger than ⟨±λ_π⟩, with HF = F for an x-coordinate-defined F?

**Known.** This is R8 revisit condition X2. A candidate H acts by multipliers whose canonicaliser is a multiplicative character of the discrete log (TASK-20260929-c05f6e DESIGN.md §3.4). The units of End(E_a) being ±1 is `recalled` there.

**What settles it.** An exhibited canonicaliser. Alternatively, a proof that any such canonicaliser computes DL-information.

**Measurable quantity.** The H-STAB validation of DESIGN.md §3.6: the multiplicative stabiliser of F at ℓ ≤ 2^32.

**Exponent stake.** Possible in principle. No candidate has been named.

---

## 6. Honest-accounting block (inventor-protocol §5)

```yaml
honest_accounting:
  objects_considered:
    - shared-table PMITM line (M1) as a tracked cost object, pinned to the v2 header
    - generic relation harvester (list interface, Shoup model): COR-GEN
    - per-target golden-collision search, sparse and dense regimes (section 2.4)
    - PCS batched harvesting (X-6)
    - semi-generic class, generic plus membership test x(Q) in V (OPEN-C, D3 clause 2)
  lossy_projection_test: >-
    Not applicable as an object proposal. No new projection of the point is
    proposed. The tracked object is a cost pair, and the operation set is "the
    generic oracle", for which KN-FIND-ffe1df Theorem C already says that no
    lossy exact sum-compatible projection exists on Z/l.
  depth_of_verified_structure: >-
    Derivation-grade, single session, unreviewed. Retrieved this session: vOW
    sections 4.2 and 5.3 (vendored), Hhan Thm 3.3 and 3.4 (HTML), Yun (abstract).
    Wagner Cor. 1 is relied on as retrieved by TASK-20260928-62ad14 and was not
    re-read by me. Shoup's primary text was unreadable.
  dominated_by:
    D1: n/a (no result claimed); the statement is KN-LIT-011 / KR-RHO-13bf67
    D2: >-
      vOW parallel rho (KR-RHO-6239aa) in time and memory: candidate +7.17 bits
      vs VOW at n = 131; Koblitz rho KR-RHO-037e22; preprocessing reading
      KR-RHO-ea34b8
    D3: >-
      n/a (heuristic, no result); its generic half is KR-RHO-46c2c6 and
      KN-LIT-011
    D4: KN-LIT-011 / KR-RHO-13bf67 for the generic clause (sota_delta 0)
  rows_checked: >-
    All 24 KR-RHO rows by claim line. KR-RHO-13bf67, ea34b8, 46c2c6, 7d93f6,
    6239aa, 037e22, 0528e7 and fbd7b1 in full. KN-LIT-011, 012, 013, 73f7e1 and
    7cc07f in full.
  sota_delta: >-
    0 on time, memory and data/queries for every deliverable. The best
    constructed generic harvesting cell is +7.17 bits above VOW at n = 131
    (scratch, from the X-6 formula). No attack; conceptual and measurement-design
    contribution only.
  enumerated_closures:
    - closure: none
      note: >-
        Nothing here meets the section 4 closure standard. COR-GEN is a known
        theorem scoped by its interface. The section 2.5 candidate is escalated,
        not closed.
  method_ceilings_restated:
    - >-
      Generic class: no sub-rho at any memory. Mechanism: Dai's reduction plus
      Shoup (via Cor. 1).
    - >-
      Per-target golden collision, sparse regime: >= 7 sqrt(l') per relation.
      Mechanism: golden collisions are a vanishing fraction of all collisions
      (vOW section 4.2).
  open_directions:
    - OPEN-A (approximate char-2 x-filters; RC5 ladder)
    - OPEN-B (FFDA-type solving degree; IMP-SEMBIN-ENGINE)
    - OPEN-C (semi-generic lower bound; K-of-L multiple-DL step)
    - OPEN-D (Frobenius canonicaliser; H-STAB)
    - >-
      Re-word the (C) trigger on generic invariants (section 2.5). Coordinator
      act.
```

---

## 7. Procedure deviations and dispatch preconditions (disclosed, not waived)

- **PD-1: run before preconditions were verified.** Dispatched on the user's instruction to run now.
  - DP-1: TASK-20261001-7d04c9 has **no receipt yet**, though its records are committed on main, per the dispatch note.
  - DP-3: no lane claim via `tools/goal_lanes.py` was made by me.
  - I could not verify either, because I have no shell.
- **PD-2: no shell.**
  - `allocate_id.py` was not run. The draft identifiers H-SEMBIN-c7e1d4 and HEUR-HARVEST-FV are a hand-chosen random token and a name.
  - A Glob over `ledger/` for `*c7e1d4*`, plus a Grep of `ledger/hypotheses/` for `c7e1d4` and `HEUR-HARVEST`, found nothing. Broader Greps over `ledger/`, `knowledge/` and `coordination/` timed out.
  - Owed: the committed-state check `git grep c7e1d4 HEAD` and `validate_ledger.py`.
- **PD-3: kb MCP not used.** `search_knowledge` was not in this session's tool surface. Grep and Glob over the corpus were used instead.
- **PD-4: v2 directory seen, not opened.** A Glob listing showed `experiments/EXP-SEMBIN-04ec3c/code/v2/` file names. No file in it was opened, and no v2 run directory or RESULTS file was read.
- **PD-5: the stop rule fired.** Per the card I stopped deriving on (C) at §2.4. The D3 and D4 drafts are therefore **conditional on the Coordinator's ruling** on §2.5. They use the generic invariants of §2.3, which stand under either ruling.
- **PD-6: session interruption.** An API session limit cut the session off after the reading phase. It resumed on the Coordinator's message (2026-10-02). No file had been written before the interruption.
- **PD-7: in-place correction before handoff.** DERIVATION.md was rewritten once by its author, before any handoff, to fix a garbled clause in §2.2 (the shared-table line's formula and memory range) and a wrong cross-reference in §1 (M3). No other content changed. It is a draft under the task directory, not an immutable record.

**Sources opened this session** (beyond the repository):
- https://www.iacr.org/archive/crypto2002/24420288/24420288.pdf (fetched, not extractable)
- https://people.eecs.berkeley.edu/~daw/papers/genbday.html
- https://people.eecs.berkeley.edu/~daw/papers/genbday-long.ps (fetched, not extractable)
- https://www.shoup.net/papers/dlbounds1.pdf (fetched, not extractable)
- https://eprint.iacr.org/2014/637
- https://arxiv.org/abs/2402.11269
- https://arxiv.org/html/2402.11269
