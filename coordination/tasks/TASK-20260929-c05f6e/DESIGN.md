# TASK-20260929-c05f6e: design pass on a sub-generic m-SUM oracle via Frobenius orbits

Author: idea-generator, independent session, policy research-deep, 2026-09-30
(resumed 2026-10-01 after an interruption, see §9 PD-3).
**Zero scientific runs. No implementation. No record in `ledger/` or `experiments/`
was written or edited.** Companion: `literature-screen.md` (D1, and D2's sources).
Proposed records: `proposed-records/`.

---

## 0. One-page summary (return_format)

- **Does the literature already answer the question?** Not as posed. No k-SUM or
  generalised-birthday result on automorphism-equipped lists was found; that is
  a search result, not a proof. The corpus already holds the factor-n answer on
  the relation-count axis: KN-FIND-b9a41d (`established`) and GGMP via
  KR-IC-b0fcda. **HEUR-GENERIC-MSUM itself is contradicted as worded** by a
  retrieved primary source. van Oorschot–Wiener §5.3 golden-collision MITM gives
  per-target time ≈ 7|F|^{3m/4 − s/2} at store |F|^s, below |F|^{m−s} for every
  s < m/2. By the sketch in literature-screen §2c, this does not open a sub-rho
  cell in H-SEMBIN-8e7ae3's family.
- **Exponential structure or method ceiling?** **Method ceiling. Nothing can be
  named.** The Frobenius transports an m-SUM instance to a different instance
  (S_R → S_{π(R)}) and fixes no target of order ℓ. So it can shrink only the
  target-independent side (stored table, factor-base unknowns), and only by the
  orbit size 2n. Charged, both exponents are unchanged. The concrete gain is at
  most 2·log2(2n) bits in relation-collection time at fixed physical store
  (16.1 bits at n = 131, 20.3 at n = 571), and ½·log2(2n) at the balanced
  optimum, which is exactly rho's own √(2n) from the same Frobenius. Every route
  to an exponential gain that could be named reduces to an impossible filter,
  a DL-hard canonicaliser, or a bounded target-fixing group (§3.4).
- **Owning goal:** GOAL-SEMBIN-5078bc, verified from the committed goal record
  and from H-SEMBIN-8e7ae3's attribution ruling. **This work discharges no
  completion criterion** (§5).
- **Recommendation on a Frobenius-orbit contract: DO-NOT-BUILD.** No D4 contract
  was produced, per the handoff's branch rule. The recommended successor is
  **not** a Frobenius experiment. It is a restatement of HEUR-GENERIC-MSUM with
  the vOW row added and the family bound re-derived for hybrid oracles:
  `proposed-records/IDEA-20260930-4b7d1e.yaml`, zero compute plus an optional
  toy fixture. That is the single test I would run first.

---

## 1. Scope of every claim below

Unless a line says otherwise, every claim here is about:

- **Curve family.** Koblitz curves E_a: y² + xy = x³ + ax² + 1, a ∈ {0,1},
  defined over F_2 and considered over F_{2^n}, **n an odd prime**.
  h = #E_a(F_2) ∈ {4, 2} divides #E_a(F_{2^n}) (derived). ℓ is the large prime
  factor.
- **Factor base.** F = F_V = {P affine : x(P) ∈ V}, with V a σ-stable
  F_2-subspace of F_{2^n}, σ = squaring, 1 < dim V < n (KN-FIND-b9a41d (1)–(2)).
- **Oracle.** m-SUM for fixed m ≥ 2 at store |F|^s, s ≤ ⌊m/2⌋, priced as in
  H-SEMBIN-8e7ae3's mechanism: partial MITM with a table shared across targets.
  The store is charged on the same footing as the baseline's (RUN-SEMBIN-c68773
  symmetry). **I did not read RUN-SEMBIN-c68773 or EXP-SEMBIN-04ec3c's cost
  model.** The model is reconstructed from H-SEMBIN-8e7ae3's text.
- **Mechanism class.** A_G: algorithms whose only use of G = ⟨−1, π⟩ is orbit
  bookkeeping, meaning orbit-canonical storage, orbit-class unknowns, and
  orbit-conjugate relations.

**Transfer statement.** Nothing here transfers to a random binary curve over
F_{2^n}. π is not an endomorphism there, and G shrinks to {±1}. Nothing
transfers to composite n or to curves with a model over a proper subfield of
F_q (KN-FIND-b9a41d "What this finding is NOT"). Nothing here is a statement
about any deployed curve.

---

## 2. D2: the mechanism, established, and the actual question answered

**Established (literature-screen §1, `retrieved` S1–S3 plus hand check):**
π² − tπ + 2 = 0 with t = 3 − #E(F_2) ∈ {−2, …, 2}. For Koblitz curves,
t = μ = (−1)^{1−a}, so τ² − μτ + 2 = 0. π^n = 1 on E(F_{2^n}). Fix(π) = E(F_2).
FG-1's form is correct. FG-1's "action on the solution set" is corrected to
"transport between solution sets".

### 2.1 Three lemmas (derivations, this session, unreviewed)

- **L1 (transport, not action).** π(S_R) = S_{π(R)} and −S_R = S_{−R}. For R of
  order ℓ, Stab_G(R) = {1}, since π^k R = ±R forces R ∈ E(F_{2^{gcd(k,n)}}) up
  to sign, which for prime n is E(F_2), with no points of order ℓ. **So G acts
  on the family of instances and trivially on each instance.**
- **L2 (target-fixing symmetries are bounded).** The symmetries of a single
  instance that fix R are summand permutations (S_m) and tuple translations
  (T_1..T_m) with ΣT_i = 0 and F + T_i = F. {T : F + T = F} is a subgroup. If it
  contained a point of order ℓ, F would be a union of cosets of an order-ℓ group,
  impossible for |F| < ℓ. So its order divides h ≤ 4, and
  |target-fixing group| ≤ m!·4^{m−1}. That is independent of |F| and n, and S_m
  is already inside PMITM's unordered accounting.
- **L3 (what G does buy, and only this).** All three items are target-independent.
  - (a) **Unknowns:** |F|/g + O(f) orbit classes, with g = 2n. This is
    KN-FIND-b9a41d (3) with negation added, and GGMP's "1/n fewer systems".
  - (b) **Store coverage:** a table holding G-canonical representatives of s-sums
    covers g·M group elements per M physical entries. A lookup of
    Y = R − Σ_right succeeds iff Y ∈ G·X for a stored X, and then
    R = Σ_right + gX is a valid decomposition because gF = F. Each lookup costs
    one canonicalisation: κ ≤ n field squarings, which are cyclic shifts in a
    normal basis.
  - (c) **Linear algebra:** divided by about g² (GGMP's n²).

  **The target-dependent enumeration itself gains nothing (L1).** Enumerating
  right tuples up to G is useless, because g·b gives R − gΣb, which is not
  G-related to R − Σb.

### 2.2 The handoff's question

"Does quotienting by orbits reduce the STORE exponent, the TIME exponent, both,
or neither, once the orbit bookkeeping is charged?"

Charged model, with g = |G| (derived):

    T_G(M) ≈ g·M                      (fill: enumerate all s-tuples, keep canonical reps)
           + (1+κ)·|F|·ℓ / (g²·M)     (|F|/g relations × ℓ/(gM) samples each)

At g = 1, κ = 0 this is T = M + |F|ℓ/M, the generic shared-table PMITM line.
That is the baseline slice (proof_search_map below).

- **At fixed physical store M:** the gain is ≤ g²/(1+κ) ≤ (2n)².
- **At the optimum over M:**
  T*_G = 2√((1+κ)|F|ℓ/g) against T*_1 = 2√(|F|ℓ). The gain is ≤ √(2n).
- **Exponents:** log(gain)/log|F| ≤ 2·log(2n)/log|F| → 0 at fixed m as |F| grows,
  because n ≤ m·log2|F| + m.

**Answer: NEITHER exponent moves.**

- Store **size** at fixed coverage falls by g.
- Store **exponent** is unchanged.
- Time at fixed physical store falls by at most g² (a polylog factor).
- The time **exponent** is unchanged.

**Relative to the baseline.** Parallel rho on the same curve gains √(2n) from the
same G (KR-RHO-037e22). So at the balanced optimum the family's position
relative to rho is unchanged up to constants. In the store-limited regime, the
Frobenius favours the family over rho by at most g²/√g = (2n)^{3/2}
(12.05 bits at n = 131). That can lower the minimum store admitting a sub-rho
cell by at most ≈ 1.5·log2(2n) + O(1) bits. That shift is below dim V whenever
|F| ≳ (2n)^{1.5}, so H-SEMBIN-8e7ae3 P3's n/2 floor survives in this model. The
check against RUN-SEMBIN-c68773's actual model is owed (§7).

**Structural caveat that sharpens the ceiling.** At n = 131 and 163 **no**
σ-stable V of index-calculus dimension exists (KN-FIND-b9a41d (5)). At the goal's
degrees the pinned-dimension cells exist only sporadically (§7 table). So the
linear A_G mechanism is not even available at most cells H-SEMBIN-8e7ae3 prices.

---

## 3. D3: the honest ceiling, and what would have to be true for more

### 3.1 The logarithmic ceiling, stated plainly

Orbits of G on F have size dividing 2n, and 2n = O(log |F|) at fixed m. **The
naive orbit quotient is a factor of at most 2n per use, used at most twice
(unknowns and coverage). That is a polylogarithmic cofactor and moves no
exponent.** L1 is why it cannot be applied a third time, to the
target-dependent side.

### 3.2 Lossy-projection test on the candidate object

- **Representation:** R1, affine x-coordinate in F_{2^n}.
- **Operation set Σ:** {π, −1} together with the m-ary sum.
- **Tracked object:** the G-orbit of the m-tuple.
- **Lossy?** Yes. It discards log2(2n) bits, the position in the orbit.
- **Discarded compatibly?** Yes. π and −1 are group automorphisms, so the orbit
  of the sum is determined by the orbit of the tuple (diagonal action).
- **Propagates under translation?** Only by the ≤ 4 points of E(F_2).
  Translation by a target R of order ℓ does not commute with the orbit map
  (orbit(P + R) is not a function of orbit(P)). This is the rigidity of
  IDEA-20260806-c5d183 / KN-FIND-ffe1df Theorem C, applied to translation by the
  target.
- **Trichotomy placement:** partial-action. The object propagates under the
  diagonal sum and under a 4-element partial translation set, and dies at
  translation by the target. Priced by orbit-canonicalisation cost κ ≤ n
  squarings per canonical representative.
- **Verdict:** a genuine lossy object, not a change of coordinates, but it
  retains exactly log2(2n) bits of leverage.

### 3.3 Object-first framing and off-limits families

Declared off-limits as the primary lens (already established or priced in the
corpus):

- Frobenius-invariant factor bases for relation count (KR-IC-b0fcda / GGMP;
  KN-FIND-b9a41d).
- Frobenius classes in rho (KR-RHO-037e22).
- Orbit-union parameterisation for decomposition (KN-FIND-47da4e).
- Target-fixing 2-torsion and halving symmetries (KR-IC-1fcdbc).

| Candidate object | New or repackaging | One-step propagation testable | Survives until |
|---|---|---|---|
| G-orbit of the tuple | repackaging of GGMP's orbit count onto the store axis | yes (L3b coverage identity) | translation by the target (L1) |
| G-canonical table of s-sums | adaptation (new axis, same factor) | yes | same |
| λ-eigenvalue class of the dlog, i.e. H-orbits for a larger H ≤ (Z/ℓ)^* | new as an object | **no**: no poly-time canonicaliser (X2) | immediately |
| Target-fixing tuple translations | known (FGHR-style, `recalled`) | yes | order ≤ 4^{m−1} (L2) |

### 3.4 What would have to be true for an exponential gain

Each candidate route gets a verdict.

- **X1: a lossy additive projection** (representation / modular filtering:
  Schroeppel–Shamir, HGJ/BCJ, Wagner k-tree). This needs a nontrivial
  homomorphism from ⟨P⟩ ≅ Z/ℓ onto a group of size about |F|^c. **Impossible:**
  Z/ℓ has no proper nontrivial quotient, and it remains a simple module over
  Z[π], so the Frobenius adds no quotient. The full group's quotients have order
  ≤ h ≤ 4. KN-FIND-ffe1df Theorem C is the prime-field analogue for exact
  sum-compatible bucket filters, and its four-line argument uses only prime
  order. **Not covered:** approximate filters (same gap as KN-FIND-ffe1df item 1).
  Nearest known negative: KR-RHO-5b1c0a (representation ECDLP over F_{p²} at
  p^{1.314}).
- **X2: an exponentially large, efficiently canonicalisable symmetry group**
  H ≤ Aut(⟨P⟩) = (Z/ℓ)^*, with |H| ≥ |F|^c and HF = F, plus a poly(n)
  canonical-orbit-representative map on **arbitrary** points (needed on the
  target side).
  - From End(E_a) ⊇ Z[τ], τ = (μ + √−7)/2, an order of discriminant −7: its
    units are ±1 (`recalled`). Only ⟨±π⟩ of order 2n is available.
  - Any larger H acts by multipliers λ ∉ ⟨±λ_π⟩. A canonical representative for
    an index-k subgroup is a relabelling of the coset of dlog(Q) in
    (Z/ℓ)^*/H, i.e. a k-valued multiplicative character of the discrete log. No
    poly-time method is known, and for small k this is a DL-information problem.
  - Separately, HF = F is expected to fail for x-coordinate-defined F (heuristic
    H-STAB, §3.6).
  - **Verdict: no candidate can be named.**
- **X3: representation multiplicity** (each solution having exponentially many
  orbit-distinct preimages that a filter thins). Without X1 there is no filter to
  thin with. G gives each relation exactly 2n images, polynomial multiplicity.
  **No.**
- **X4: a target-fixing symmetry of size |F|^c.** Bounded by m!·4^{m−1} (L2).
  **No.**
- **X5: outside the orbit class.** An algebraic (non-generic) oracle where a
  σ-stable V lowers the Weil-descent solving degree. Not an orbit quotient.
  By L1 the per-target system has no σ-symmetry, so invariant-ring degree
  reduction is available only for S_m and small torsion. This class is priced
  elsewhere (GOAL-SEMBIN-5078bc criteria 1–3, IMP-SEMBIN-ENGINE; KN-OPEN-095df5
  for non-linear invariant bases). **Named as the open class, not assessed.**

**D3 VERDICT: NOTHING CAN BE NAMED within the Frobenius-orbit mechanism class.**
This is a method ceiling under inventor-protocol §8 audit 4. It is the cheapest
refutation of rank 1 **as a route to an exponent**. It is **not** a refutation of
HEUR-GENERIC-MSUM, which the literature screen shows fails as worded for a
different, Frobenius-free reason.

### 3.5 proof_search_map (inventor-protocol §8, all four audits)

```yaml
proof_search_map:
  bottleneck: >-
    The target-dependent enumeration side of the m-SUM oracle (the |F|^(m-s)
    factor in HEUR-GENERIC-MSUM). A sub-generic oracle must shrink it
    exponentially; L1 shows G does not act on it.
  baseline_embedding:
    parameter_slice: >-
      g = |G| = 1 and kappa = 0 in T_G(M) = g*M + (1+kappa)|F| l/(g^2 M). This
      reproduces the generic shared-table PMITM line T = M + |F| l / M, i.e.
      per target |F|^(m-s) at store |F|^s and |F| relations: H-SEMBIN-8e7ae3's
      mechanism text.
    reproduction_check: >-
      Symbolic, and done here: substituting g = 1, kappa = 0 gives exactly
      M + |F| l / M. A frozen numeric fixture against RUN-SEMBIN-c68773 is
      OWED; that run was not read.
  observation_collision:
    observable: >-
      The G-orbit of the m-tuple, equivalently the G-orbit of its sum.
    distinct_preimage_search: >-
      FOUND, and it is the obstruction. Targets R and pi(R) are distinct
      instances whose solution sets carry identical orbit observables
      (pi(S_R) = S_pi(R)). The observable answers "is the sum in G.R", which is
      2n targets at once: a factor g, never an exponent.
  constructive_transforms:
    - transform: observable_fiber
      proposed_object: >-
        Hold the tuple-orbit observable fixed and vary the target within G.R.
      predicted_gain: >-
        Exactly g = 2n per stored entry (coverage, L3b) and nothing on the
        target side (L1).
  quantifier_order: >-
    FOR ALL odd primes n, Koblitz E_a/F_2, sigma-stable V with 1 < dim V < n,
    fixed m >= 2 and s <= floor(m/2), and FOR ALL algorithms in A_G: at physical
    store M, time >= T_PMITM(M) / g^2 up to the canonicalisation factor.
    WEAK JOINT: membership in A_G is a definition ("uses G only through
    orbits"), not a theorem about all algorithms. An algorithm that uses pi
    through its eigenvalue lambda in any other way is outside A_G and outside
    this ceiling.
  method_ceiling:
    strongest_certifiable_claim: >-
      Within A_G and the reconstructed PMITM model: Delta_e(time) =
      Delta_e(store) = 0; log2 gain <= 2 log2(2n) at fixed physical store and
      <= 0.5 log2(2n) at the balanced optimum, matched there by rho's own
      sqrt(2n) (KR-RHO-037e22).
    nearby_object_control: >-
      (a) The same Koblitz curve with a matched non-sigma-stable V of the same
      dimension: pi(F) != F, coverage gain 1, predicted total gain <= 4
      (negation only). (b) A random binary curve over F_(2^n) not defined over
      F_2: pi is not an endomorphism, g = 2, same prediction. The method
      separates (Koblitz, stable V) from both by at most (2n)^2, polynomial,
      which is what the ceiling says and no more.
  proof_obligations:
    - claim: L1 transport and trivial target stabiliser for R of order l
      responsibility: correctness
    - claim: L2 target-fixing group order <= m! * 4^(m-1)
      responsibility: size
    - claim: L3b coverage identity (lookup of canonical(Y) yields a valid decomposition iff Y in G.X)
      responsibility: correctness
    - claim: L3a class count |F|/g + O(f), from KN-FIND-b9a41d (3) plus negation
      responsibility: size
    - claim: canonicalisation cost kappa <= n squarings (normal-basis rotations)
      responsibility: runtime
    - claim: X1, Z/l simple as a Z[pi]-module, so no lossy exact additive filter exists
      responsibility: scope
    - claim: X2, units of End(E_a) are +-1 (RECALLED; needs a retrieved source before any record leans on it)
      responsibility: scope
    - claim: baseline gain sqrt(2n) for rho on the same curve (KR-RHO-037e22)
      responsibility: baseline
  not_applicable_reason: null
```

### 3.6 Named heuristic (supports X2's second half only; the ceiling does not rest on it)

- **H-STAB.** For F = F_V with V σ-stable and 1 < dim V < n on a Koblitz curve,
  the multiplicative stabiliser {λ ∈ (Z/ℓ)^* : λF = F} equals ⟨±λ_π⟩ (order 2n).
  It imitates the fact that a uniformly random subset of Z/ℓ of size |F| has
  trivial multiplicative stabiliser except with probability about |F|²/ℓ.
- **Validation route.** At toy scale (ℓ ≤ 2^32; |F| ≤ 2^10), compute the dlogs
  of all of F by BSGS. The candidate multipliers are λ_Q = dlog(Q)/dlog(P0) for
  Q ∈ F, so there are only |F| candidates. Check λF = F for each (|F|² lookups).
  - Null: a random subset of the same size.
  - Positive control: ⟨±λ_π⟩ must be found.
  - Transfer to cryptographic size is by assumption only, stated as such.

The ceiling does not need H-STAB. The canonicalisation obstruction suffices.

---

## 4. D4: not attempted

The completion gate says: "A D3 that names none is a COMPLETE and ACCEPTED
deliverable and terminates the task at D5-D6; D4 is not attempted in that
branch." **No H-SEMBIN-* or EXP-SEMBIN-* identifier was minted**, and no
contract exists to approve.

---

## 5. D5: goal binding, read from committed records

**Owner: GOAL-SEMBIN-5078bc.** Verified, with one discrepancy.

- Goal objective item (4), quoted from `ledger/goals/GOAL-SEMBIN-5078bc.yaml`:
  "(4) COST. Produce the time-AND-memory comparison the paper does not make.
  Table 3 and eqs. (15)-(17) are time only, while stage 2 stores Theta(2^k)
  relations ... against a Pollard rho comparator with negligible memory
  (KN-OPEN-86e7e1)."
- Criterion 4, quoted: "A committed Coordinator decision carries a COST record
  giving time AND memory for the chained-S_3 index calculus against van
  Oorschot-Wiener PARALLEL rho with distinguished points at n = 233, 283, 409,
  571, with every optimistic assumption flagged on both sides and a tradeoff
  curve in m."
- H-SEMBIN-8e7ae3 `question_id_attribution_ruling` (DEC-20260928-7c3d91):
  "The owning goal is GOAL-SEMBIN-5078bc", citing objective item (4) and
  criterion 4.
- **Discrepancy, recorded and not repaired.** The goal head's
  `active_hypothesis_ids` (H-SEMBIN-112e2e, -2d7708, -c5b2e0, -83999d) does not
  list H-SEMBIN-8e7ae3. The head was last updated 2026-09-15, before that
  hypothesis existed. The binding rests on the ruling, not on the head.

**Criteria this work would and would NOT discharge, ruled in advance:**

| Criterion | Discharged? | Why |
|---|---|---|
| 1 (d_F4 ↔ d_reg map) | no | unrelated |
| 2 (Tables 1–2 reproduction) | no | unrelated |
| 3 (d_F4 = 4 boundary) | no | unrelated. X5 points there but assesses nothing |
| **4 (COST record)** | **NO** | That criterion names the chained-S_3 index calculus with its Gröbner cofactor at n = 233–571. This deliverable prices an orbit mechanism class inside a reconstructed PMITM family and admits no Gröbner cost. **No number here (the log2-gain bounds, the §7 spectra, the vOW exponents) may be quoted against criterion 4.** At most, a later COST record may flag "Frobenius on the family side" as an optimistic-assumption row, sized by §2.2's bound, which is the ruling's analogue of DEC-20260928-7c3d91's on EXP-SEMBIN-04ec3c. |
| 5 (eq. (11) yield) | no | unrelated |
| 6 (no design intake satisfies any criterion) | n/a | This deliverable **is** design intake and satisfies nothing, by that criterion's own words. |

---

## 6. D6: what a negative would and would not establish, and the obstruction quantity

**What a negative would NOT establish.**

- It would not validate HEUR-GENERIC-MSUM. That heuristic already fails as
  worded, for a Frobenius-free reason (literature-screen §2c).
- It would not show that no sub-generic m-SUM oracle exists on E_a(F_{2^n}).
- It would not bear on X5 (algebraic oracles), on approximate filters, on
  non-linear invariant bases (KN-OPEN-095df5), or on hybrid table-plus-golden-
  collision oracles.

**What it WOULD establish, within §1's scope.** No algorithm in A_G moves the
time or store exponent. Frobenius leverage on this family is bounded by (2n)².

**The prospective obstruction, stated before any run exists:**

```yaml
obstruction:
  statement: >-
    On Koblitz E_a(F_(2^n)), n an odd prime, the Frobenius-negation group
    G = <-1, pi> transports m-SUM instances (S_R -> S_(+-pi^k R)) and fixes no
    target of order l. Its leverage on an m-SUM relation harvester is therefore
    confined to target-independent bookkeeping (factor-base classes, store
    coverage, linear algebra), each bounded by |G| = 2n.
  quantity: >-
    (i) Stab_G(R) for R of order l, in group elements. (ii) The exponent change
    Delta_e = lim log(T_generic / T_G) / log|F| at fixed m, s, dimensionless.
    (iii) log2 of the relation-collection time ratio at fixed physical store,
    in bits.
  value: >-
    (i) 1, exact. (ii) 0, exact. (iii) <= 2 log2(2n): 16.07 (n=131), 16.70
    (163), 17.73 (233), 18.29 (283), 19.35 (409), 20.31 (571) bits; and
    <= 0.5 log2(2n) = 4.02 to 5.08 bits at the balanced optimum. No error bars:
    these are derivations, not measurements.
  measured_by: []
  measured_by_note: >-
    EMPTY BY CONTRACT. This is a zero-run task and the values are derived
    (proof_status would be `derivation`), not measured. Under inventor-protocol
    §4 this is a METHOD-CEILING statement over the class A_G. It is not a
    measured closure of the sub-generic m-SUM question and must not be recorded
    as one. If it is ever proposed as a closure it needs rule-12 review.
  scope: >-
    Section 1 of this document: Koblitz E_a/F_2 over F_(2^n), n an odd prime;
    F = F_V with V sigma-stable, 1 < dim V < n; fixed m >= 2, s <= floor(m/2);
    shared-table PMITM family model with store charged; algorithm class A_G only.
  resource_check:
    examined: true
    reading: >-
      The same fact is an ASSET for target-free collision search. Pollard rho
      needs no fixed target, so a free transport of instances becomes a free
      quotient of the walk's state space. That is exactly why rho gains
      sqrt(2n) on Koblitz curves (KR-RHO-037e22) while a fixed-target m-SUM
      oracle gains nothing on its target side. A second reading: a
      multi-target relation harvester whose targets are themselves G-orbits
      (harvest relations Sum P_i = g Sum P'_j, homogeneous) turns the target
      side target-free. By KR-RHO-46c2c6's sqrt(2 L l) with L = |F|/2n classes,
      it is still dominated by rho by about sqrt(|F|/n). Recorded as examined,
      no resource found that moves an exponent.
    spawned_ids: []
```

**If a later session wants this measured rather than derived** (prospective,
not a contract):

- **Quantity:** the ratio ρ_G = T_{A_G}/T_generic of relation-collection
  operation counts at matched physical store.
- **Setting:** toy Koblitz curves where σ-stable V exist at several dimensions.
  Hand-checked (derived) candidates: n = 17 (ord 8), 23 (ord 11), 31 (ord 5),
  41 (ord 20), 73 (ord 9). Whether E_a(F_{2^n}) has a large prime factor at
  these n is **unchecked**.
- **Prediction:** log2 ρ_G ∈ [−2·log2(2n), 0] with **zero slope in dim V** at
  fixed n. A slope in log|F| that does not vanish is the §3 structural tell: an
  artifact first, a finding only after controls.
- **Null object (blocking):** a matched non-σ-stable V of the same dimension on
  the same curve. Predicted ρ ≥ 1/4 (negation only). **Any gain beyond the
  negation factor on the null base voids the Frobenius attribution.**
- **Known-positive control:** the same table stored uncanonicalised with all 2n
  images explicit (physical store 2nM) must reproduce the canonical table's hit
  rate exactly. An implementation that fails this has broken the coverage
  identity L3b.

---

## 7. Stable-subspace spectra at the owning goal's degrees (derived by hand; NOT machine-checked)

Orders were checked by explicit modular exponentiation in this session:

- ord_233(2) = 29, since 2^29 − 1 = 233 · 2 304 167.
- ord_283(2) = 94, since 2^94 ≡ 1 (mod 283), and 2 is a quadratic non-residue
  so 2^47 ≢ 1.
- ord_409(2) = 204, since 2^102 ≡ −1 and 2^4, 2^12, 2^68 ≢ 1.
- ord_571(2) = 114, since 2^114 ≡ 1 and 2^38 ≡ 109.
- ord_131(2) = 130 and ord_163(2) = 162 (primitive, agreeing with
  KN-FIND-b9a41d (5)).

Attainable σ-stable dimensions are a + b·ord_n(2) (KN-FIND-b9a41d (1)).

Cells where the pinned dimension l* = ⌈n/m⌉ is itself attainable and faithful
(Δ = l' − l* = 0), for m ≤ 12:

| n | ord_n(2) | m with Δ = 0 | nearest-miss cells (Δ in bits) | criterion-4 cells m = 11, 12 |
|---|---|---|---|---|
| 233 | 29 | 2, 4, 8 | m=9: +3, m=10: +5, m=11: +7, m=3: +9, m=12: +9 | Δ = +7, +9 |
| 283 | 94 | 3 | m=4: +23 | Δ = +70 (m=12) |
| 409 | 204 | 2 | m=3: +67 | Δ = +166, +169 |
| 571 | 114 | 5 | m=6: +18 | Δ = +62, +66 |

Under KN-FIND-b9a41d (4)'s MA-1–MA-4 (net win iff 2^Δ < g ≈ n):

- The Δ = 0 cells are wins of log2 n ≈ 7.9–9.2 bits.
- (233, m = 9, 10, 11) are wins of 4.9, 2.9 and 0.9 bits.
- Every other cell is a loss.

**All of these are constant factors, consistent with §3.** No Frobenius-stable
linear base of pinned dimension exists at the FIPS-scale m = 11, 12 cells
objective (2) names, except (233, m = 11) at a 0.9-bit margin.

**Asymmetry to check (flag, not a claim).** If RUN-SEMBIN-c68773 charged the rho
baseline **with** Frobenius classes at Koblitz cells (KR-RHO-037e22 says the
ECC2K-130 figure of about 2^60.9 iterations includes them) and the family
**without**, the family is priced pessimistically by up to (2n)^{3/2} in the
store-limited regime. §2.2 argues this cannot breach P3's n/2 floor when
|F| ≳ (2n)^{1.5}. The per-cell margin is RUN-SEMBIN-c68773's, which I did not
read. At n = 131 only orbit unions (KN-FIND-47da4e) could carry the effect,
since no linear σ-stable V exists there.

---

## 8. Honest-accounting block (inventor-protocol §5)

```yaml
honest_accounting:
  objects_considered:
    - G-orbit of the m-tuple under <-1, pi> on Koblitz E_a(F_(2^n)), F = F_V with V sigma-stable
    - G-canonical shared table of s-sums (store-coverage object)
    - H-orbits for a larger multiplicative subgroup H of (Z/l)^* (no canonicaliser; not testable)
    - target-fixing tuple translations (bounded by L2)
  depth_of_verified_structure: >-
    Frobenius relation: retrieved (Wikipedia Schoof / SEA sections; arXiv
    1801.08589) plus a hand count of E_a(F_2). L1-L3, X1, X4: derivations in this
    session, unreviewed. X2: a search result plus one recalled fact (units of
    End(E_a)). vOW contradiction: retrieved primary source plus derivation. §7
    orders: hand modular arithmetic, not machine-checked. The ceiling
    re-derives, on the time-store axis, the factor-n structure already
    established on the relation-count axis by KN-FIND-b9a41d, and is recorded as
    exactly that.
  dominated_by: "n/a (no result claimed)"
  dominated_by_check: >-
    Checked, not defaulted. As a hypothetical result, the Frobenius-orbit oracle
    would be dominated in time at every memory by vOW parallel rho with
    Frobenius-negation classes (KR-RHO-6239aa with KR-RHO-037e22): charged
    family T >= 2 sqrt((1+kappa)|F| l / 2n) against rho about sqrt(pi l / 4n);
    memory about (2n)^(-1) |F|^s against rho's negligible store (KR-RHO-7d93f6);
    queries: single-target both. Rows opened in full: KR-RHO-6239aa,
    KR-RHO-037e22, KR-RHO-7d93f6, KR-RHO-46c2c6, KR-RHO-5b1c0a, KR-IC-b0fcda,
    KR-IC-1fcdbc. Not opened: the other 19 KR-RHO rows (titles read) and the
    other 22 KR-IC rows (not read). That is why this is "n/a (no result
    claimed)" and not null.
  sota_delta: >-
    No attack; conceptual contribution only. Quantitatively: the Frobenius
    orbit quotient moves the family's time and store exponents by 0. Its
    concrete effect is <= 2 log2(2n) bits of relation-collection time at fixed
    physical store (16.07 at n = 131 to 20.31 at n = 571) and <= 0.5 log2(2n)
    bits at the balanced optimum (4.02 to 5.08), equal to rho's own gain from
    the same Frobenius. Separately: HEUR-GENERIC-MSUM's per-target tradeoff is
    beaten as worded by vOW golden-collision MITM by |F|^(m/4 - s/2) for
    s < m/2 (m = 4, s = 1: |F|^0.5), with no sub-rho consequence found for the
    family.
  closures:
    - closure: Frobenius-orbit quotient as a route to an exponent-moving m-SUM oracle
      mechanism: >-
        L1 (transport, trivial target stabiliser) + L2 (bounded target-fixing
        group) + X1 (Z/l simple, no exact additive filter) + X2 (no
        poly-time canonicaliser for larger H): leverage confined to
        target-independent bookkeeping, bounded by 2n per use, used at most
        twice.
      standard: >-
        Method ceiling over a DEFINED class A_G, derivation-grade. Meets §4's
        "named obstruction + argument + redirection" in form, but its
        obstruction is derived, not measured, so it is not a lane closure.
        novelty_status of the closure: unverified (FGHR and the k-SUM
        literature were not opened).
  open_directions:
    - HEUR-GENERIC-MSUM restatement with the vOW golden-collision row, and re-derivation of H-SEMBIN-8e7ae3's family bound for hybrid oracles (proposed-records/IDEA-20260930-4b7d1e.yaml). Ranked first.
    - X5, algebraic decomposition oracles on sigma-stable V at the section 7 Delta = 0 cells (233 with m = 2, 4, 8; 283/3; 409/2; 571/5), priced by solving degree. Needs the IMP-SEMBIN-ENGINE clearance.
    - Approximate sum-compatible filters on binary curves (the KN-FIND-ffe1df item-1 gap, binary-field instance).
    - Non-linear Galois-invariant bases (KN-OPEN-095df5).
    - The Koblitz-cell pricing-asymmetry check against RUN-SEMBIN-c68773 (section 7).
    - Retrieve FGHR 2014 and a source for the units of End(E_a) to lift the two recalled pointers above.
```

---

## 9. Procedure deviations and dispatch preconditions (disclosed, not waived)

- **PD-1, no shell.** `allocate_id.py --next/--check`, `validate_ledger.py`,
  `goal_lanes.py` and `git` could not be run. Two identifiers were chosen by this
  agent without scanning state: `IDEA-20260930-4b7d1e` and `KN-LIT-e3a95c`.
  Because a language model chose them, they are not guaranteed random. Glob and
  Grep over `ledger/` and `knowledge/` found no occurrence of either token.
  **The committed-state check (`git grep <token> HEAD` after merging
  origin/main) and `validate_ledger.py` are OWED by the archiving session.**
  Nothing was written under `ledger/`, so ledger validation should be
  unaffected. Whether the validator scans `coordination/tasks/**` is unknown.
- **PD-2, `search_knowledge` unavailable.** Substituted by corpus grep
  (literature-screen §0).
- **PD-3, interruption.** The session was cut off by an API spend-limit error
  after this file and `literature-screen.md` were written, and resumed on
  2026-10-01 on the Coordinator's instruction. On resume:
  - The proposed records were written.
  - One YAML defect in the IDEA draft was fixed: an unquoted scalar beginning
    with `|`.
  - This file was rewritten to correct a garbled τ expression in §3.4 X2 and
    three provenance slips. KR-RHO-18cc42 had been listed as read but only its
    title was read. The 2^60.9 attribution now cites KR-RHO-037e22. The DP-3
    claim about TASK-20260929-7b42d9's scope is softened.
  - No content was half-written. No other claim changed.
- **DP-1 (inputs committed).** Not verifiable without git. The launching session
  stated the branch is at origin/main.
- **DP-2 (lane claim).** `coordination/goals/GOAL-SEMBIN-5078bc/lanes/` holds
  only `BATCH-457504.lane.json` and `BATCH-457504.closed.json`. No claim file for
  TASK-20260929-c05f6e was found under the goal's `batches/*/claims/`. This binds
  the dispatcher and is recorded, not repaired.
- **DP-3 (snapshot archival card for these deliverables).** A grep of
  `ledger/handoffs/` for this task ID finds only this card and
  TASK-20260929-7b42d9. DEC-20260929-3e8a1c describes 7b42d9 as the ledger
  archive of that decision and its cards. I did not open 7b42d9 to confirm that
  it excludes these deliverables. This card's own `archived_by_note` says the
  deliverables "need their own snapshot archival task". **No such card was
  found.** Under AGENTS.md "Dispatch preconditions", binding afterwards is a
  remedy to be disclosed as a correction (CORR-20260915-6708e4 pattern).
- **DP-4 (focus reading).** The goal head lists one open batch, BATCH-9d649f (head
  last updated 2026-09-15). The lane files show BATCH-457504 opened and closed.
  This task opens no batch and no lane and adds zero live critical lanes. The
  renderer was unavailable (no shell); the property is reported instead.
- **Partial reads, declared.** EXP-SEMBIN-04ec3c/specification.yaml and
  RUN-SEMBIN-c68773 were **not read**, so no statement here is about their cost
  model except §7's flag. AGENTS.md was read at the core rules, dispatch
  preconditions and knowledge-retrieval sections only.
