# Family B — module and representation structure: candidate leads

Idea Synthesist report, 2026-10-31. Family: E(F_p) as a Z[pi] / End-module, the
mod-N Galois representation and E[N] as a group scheme, twist families,
modular-curve / level-structure reformulations, isogeny-class and Brauer-Manin
invariants, endomorphism algebra beyond units, quaternion/Deuring structure on
supersingular curves. Claim boundary: mathematical ideation on toy and public
parameters only; no secret scalar, no deployed key, no exploit. Nothing here is
a finding; every connection is a hypothesis for the Coordinator and an
independent Validator.

Authority note: no IDs are allocated here (ids are `IDEA-20261031-<alloc>`,
to be minted with `tools/allocate_id.py`), no record is edited, no status
changes. The top-level session runs `tools/lead_atlas.py --match` on each
candidate; the collision phrases each candidate will hit are listed explicitly.

## 0. What was read

- `knowledge/leads/ecdlp/README.md`; every lead in `structure/` (17),
  `transfer/` (22), `exotic/` (23); the generic/ic leads that touch this
  family: `LEAD-ICP-self-pairing-prime-order`, `LEAD-ICB-cofactor-torsion-quotients`,
  `LEAD-RHO-non-automorphism-equivalence`, `LEAD-RHO-pool-class-quotient`,
  `LEAD-RHO-cheon-deployed-applicability`, `LEAD-ICP-extension-field-embedding`,
  `LEAD-ICP-isogeny-transported-relation-yield`.
- Known-results map titles/claims for all 57 `KR-*` rows (`knowledge/frontiers/ecdlp/`).
- `analysis/endomorphism-isogeny-decomposition/DECOMPOSITION.md` sections 1–4
  (Layer 0 admissibility filter, R1–R8, T1–T5, lanes L7–L13).
- Proposals located by grep on this family's vocabulary and read at header/claim
  level: IDEA-20260806-0c9de1 (X_1(N) diamond torsor, read in full to its
  mechanism), IDEA-20260812-a3720a (ray-class fibre), IDEA-20260807-dc14b4
  (Tate-module invariance test), IDEA-20260906-476f20 (F_{p^2}-twist coset),
  IDEA-20261006-32b931, IDEA-20261005-c94831, IDEA-20260922-b19793,
  IDEA-20260930-f1d8ff, IDEA-20260807-1c14d7, IDEA-20260807-6eab6a
  (ell-primary coprimality), IDEA-20260807-464ff8 (distortion maps, supersingular slice).
- `ideas/rejected/` ECDLP-IDEA-112 (modular-unit diamond eigenspace), -026
  (N-division Kummer cocycle), -023 (level-structure monodromy word), -036 (joint
  torsion covariant label), -207 (Brauer-Severi reduced norm): obstruction sections.
- `KN-OPEN-ed922d` (hidden advantage behind a subgroup-preserving correspondence),
  `KN-OPEN-2c095b` (multiplicative-order deficit of a curve-derived lambda).
- Web (standard mode, three queries, results recorded in section 6).

## 1. The recurring obstruction in this family, named once

Every lead in this family that is closed is closed by one of three facts, and
every open lead in it is open only where one of the three has not yet been
written down for the particular object:

- **O1 (scalar action).** G = <P> has prime order N, so End(G) = Z/N and every
  F_p-rational endomorphism, isogeny-loop, CM relation, automorphism, Frobenius
  power and Hecke-type correspondence acts on G as a scalar (DECOMPOSITION.md
  Layer 0, H-ENDO-001, KN-FIND-b7e091). Closes: endo-scalar-action, small-cm-disc,
  glv-gls-isogeny-loop, p192-class-cm-relations, secp256k1-audit, automorphism-quotient
  (beyond sqrt|Aut|).
- **O2 (the other half of E[N] lives over F_{p^{k_emb}}).** Over F_p,
  E[N] = G (+) G' with Frobenius eigenvalues 1 and p, so G' is isomorphic to mu_N
  as a Galois module and has no rational points below F_{p^{k_emb}}
  (Balasubramanian-Koblitz). Everything that needs a second N-torsion direction,
  a distortion map, a self-pairing, a Kani/Richelot kernel, a trace-zero transfer
  or a Weil-pairing identification G' ~ mu_N is MOV. Closes: second-torsion-direction,
  one-point-self-pairing, self-pairing-prime-order, mov-small-embedding-degree.
- **O3 (k is point data, not curve data).** Every invariant of E, of its isogeny
  class, of its twists, of its volcano position, of E[ell] (ell != N), of its CM
  order or of its moduli point in X_0(N) is independent of k (L7; torsion-module-leak;
  isogeny-class-generic-invariance; IDEA-0c9de1 F2/F3). Point-dependent data that
  is not a group operation is coordinate data (R1/R2, index calculus) or a
  level-N function (Miller / elliptic net).

The three open leads in this family — `LEAD-STR-class-group-ecdlp-bridge`
(simulation lemma not written), `LEAD-TRF-miller-cocycle-nonhom-transfer` /
`LEAD-EXO-miller-pairing-cocycle` (same mechanism filed twice) and the
`revisit_when` of `LEAD-STR-small-cm-disc-nonunit-endo` (prime-field Koblitz
analogue never constructed) — are each one derivation or one construction away
from O1–O3. Candidates 1, 2, 4 below are those derivations; candidate 3 is that
construction; candidate 5 names the one operation set (scalar action) the
program's rigidity theorem has not been applied to, and prices it.

**Honest headline.** I found no candidate in this family with a plausible
exponent change. The best algorithmic upside is a constant <= sqrt(log N)
(candidate 3), predicted to be a loss once canonicalisation is charged. The
program value of this batch is closure: one theorem (candidate 1) would retire
the simulation-lemma `next_action`, bound ring/class-group-knowledge trapdoors
(KN-OPEN-ed922d row 3) and decide both Miller-cocycle leads.

## 2. Ranked candidates

Ranking rationale: candidate 1 would change the most records (two open leads,
one open problem, one goal's hidden-structure clause) if proved, and names the
one place a proof could fail, which would be the real lead. Candidate 2 is its
algebraic companion and retires two `revisit_when` clauses. Candidate 3 is the
only one with any algorithmic upside and realises a `revisit_when` the program
wrote but never built. Candidate 4 adds a zero-compute forced value to an open
lead. Candidate 5 is a frame-completing lemma with a small measurement.

---

### Candidate 1 — Structured generic-group closure for the module/representation family

**1. Title.** A curve-aware generic group model in which the adversary also
gets End(E), the Cl(O)-action on (E, P) with level-N structure, E[ell] for
ell != N, and Miller/Kummer values at N not dividing p-1, still needs
Omega(sqrt N) group operations — or the one oracle that cannot be simulated.

**2. Object.** The tuple of F_p-rational algebraic structures attached to
(E, G): End_{F_p}(E) as a ring with its action on points; the simply transitive
Cl(O)-action on the isogeny class carrying G by transport (T1) and its
level-structure refinement Cl_n(O), n = (pi - 1) (IDEA-20260812-a3720a); the
Galois modules E[ell], ell != N; the Miller function values f_{N,T}(R) for
T, R in G and their unique N-th roots (candidate 4 says what these are).

**3. Mechanism and gain level.** No gain: this is a closure. The claim is that
each structure is simulable by a lazy simulator in the generic group model with
only the algebraic identities the structures actually satisfy: endomorphisms
act as public scalars (O1), the class-group action moves curves and transports
G without changing k (T1), ell-torsion data is k-independent (O3, IDEA-6eab6a),
and Miller values at N not dividing p-1 satisfy only Weil-reciprocity symmetry
f_{N,T}(R) = f_{N,R}(T) up to normalisation constants (no bilinearity, since
every element of F_p^* is an N-th power). If every structure is simulable,
Shoup's bound (KR-RHO-13bf67) gives Omega(sqrt N) and the whole family is closed
at exponent 1/2 by one theorem. If one simulation fails, the failure names the
single non-generic identity in this family, which is the only lead worth a
compute budget. Gain level: primitive-level closure, no algorithmic content.

**4. Closest leads and why this is not already foreclosed.**
`LEAD-STR-class-group-ecdlp-bridge` (open_next_step; its `next_action` IS the
class-group half of this simulation lemma: the candidate advances it and widens
it to the other structures); `LEAD-STR-endo-scalar-action-generic` and
`LEAD-EXO-augmented-oracle-ggm` (closed for endomorphism-image and incidence
oracles, KN-FIND-b7e091, EV-GGM-79e710; this candidate extends the same
instrument to oracles those records did not cover); `LEAD-TRF-miller-cocycle-nonhom-transfer`
and `LEAD-EXO-miller-pairing-cocycle` (open; a Miller-value simulator decides
them without the toy run, or the toy run finds the non-simulable identity);
`KN-OPEN-ed922d` row 3 (ring knowledge as trapdoor; a simulable End/Cl(O)
oracle bounds the trapdoor holder at the public cost). Bridge sentence: the
simulability already proved for endomorphism-image oracles transfers to the
class-group action because transport preserves k and to Miller values because,
with N not dividing p-1, the only identities among them are symmetric
normalisation constants; the obstruction recorded for CLGP ("no explicit bridge
map") becomes a theorem rather than absence of evidence.

**5. Smallest discriminating experiment.** Toy, p in {1009, 4099, 10007},
prime-order curves with k_emb > 2 (so N does not divide p-1, p^2-1).
Implement the lazy simulator and the real oracles; run a distinguisher battery
(all algebraic identities expressible in the oracle language up to depth 3:
reciprocity, scalar/transport commutation, additivity tests) on
2^16 random queries per oracle; counted quantity: number of identity classes
on which real and simulated transcripts differ. Control arm (positive): a toy
curve with N dividing p-1 (k_emb = 1), where the reduced Tate self-pairing
is a genuine bilinear identity — the Miller-value simulator MUST be
distinguished there; if it is not, the battery is blind and the run is invalid.
Falsifying outcome: a reproducible identity among real Miller values (or real
class-group transport data) that the simulator cannot satisfy, on the k_emb > 2
arm. Then the theorem is false and that identity is the lead.

**6. Prior-art risk.** Generic group action models exist (Montgomery-Zhandry
ASIACRYPT 2022; Duman-Hartmann-Kiltz-Kunzweiler-Lehmann-Riepel PKC 2023,
retrieved abstract-level via web search) but model the action alone, not an
action on curves carrying a generic group whose DLP is the target. The
combination is not in the literature I could find; the result would be a
hardness statement, not an attack. `novelty_status: unverified`.

**7. Rating.** Promising as a closure instrument (it would retire two open
leads, one open-problem row and one trapdoor clause); zero attack content. One
sentence of why: every closed lead in this family already cites one of O1–O3,
so a single simulator theorem is the natural consolidation, and its one
possible failure point is precisely where a real lead would have to sit.

**Collision phrases for `--match`:** "generic group model simulable oracle",
"class group action solves ECDLP", "vectorization oracle gives discrete logs",
"endomorphism image oracle", "ray class group torsor bridge", "Miller function
transfer". Expected hits: LEAD-EXO-augmented-oracle-ggm,
LEAD-STR-class-group-ecdlp-bridge, LEAD-STR-endo-scalar-action-generic,
LEAD-TRF-miller-cocycle-nonhom-transfer. All are advanced/consolidated, none
re-proposed.

```yaml
idea:
  id: IDEA-20261031-<alloc>
  title: Curve-aware generic group model (End, Cl(O)-action with level structure, E[ell], Miller values) is simulable, or the one oracle that is not
  class: mechanism
  claim: >-
    For ordinary E/F_p with prime-order G and N not dividing p^j - 1 for j below the
    embedding degree, every oracle in the set {endomorphism images, Cl(O)/Cl_n(O)
    action on (E', P') with transport, E[ell] Galois data for ell != N, Miller values
    f_{N,T}(R) and their unique N-th roots for T, R in G} is simulable in the generic
    group model with a lazy simulator respecting only scalar action, transport and
    Weil-reciprocity symmetry; hence any algorithm using them needs Omega(sqrt N)
    group operations. Falsified by exhibiting one algebraic identity among real
    oracle outputs that a transcript-consistent simulator cannot satisfy.
  mechanism: >-
    O1 (End(G) = Z/N), T1 (isogeny transport preserves k), O3 (curve-level and
    ell-torsion data are k-independent) and the triviality of H^1(F_p, mu_N) when
    N does not divide p-1 (so every Miller value is an N-th power and the only
    relations among values are reciprocity constants). Operation set: all of the
    above; trichotomy class: partial action (the structures act on G through
    scalars and transport); the discarded information is exactly k.
  novelty_status: unverified
  citations:
    - {ref: KN-FIND-b7e091, provenance: internal, claim: incidence and endomorphism-image oracles are GGM-simulable, verified_by: lead file LEAD-STR-endo-scalar-action-generic read 2026-10-31}
    - {ref: IDEA-20260812-a3720a, provenance: internal, claim: ECDLP on a conductor-1 curve is vectorization inside the level fibre of Cl_n(O) -> Cl(O), verified_by: header read 2026-10-31}
    - {ref: IDEA-20260807-6eab6a, provenance: internal, claim: every homomorphic ell-primary invariant vanishes on G for ell != N, verified_by: header read 2026-10-31}
    - {ref: "Duman, Hartmann, Kiltz, Kunzweiler, Lehmann, Riepel, Generic models for group actions, PKC 2023 (eprint 2023/186)", provenance: retrieved, claim: information-theoretic DL lower bound in a generic group action model, verified_by: web search abstract 2026-10-31}
    - {ref: "Montgomery, Zhandry, Full quantum equivalence of group action DLog and CDH, ASIACRYPT 2022", provenance: recalled, claim: earlier generic group action model, verified_by: null}
  assumptions:
    - N does not divide p^j - 1 for all j < k_emb (the generic prime-order case).
    - The oracle language is fixed in advance (depth-3 identities); deeper identities are out of the test's scope and said so.
  proof_search_map:
    bottleneck: the Miller-value oracle; whether real values satisfy any identity beyond reciprocity symmetry
    baseline_embedding:
      parameter_slice: endomorphism-image and incidence oracles (KN-FIND-b7e091) as the already-proved sub-case
      reproduction_check: the new simulator restricted to those oracles reproduces EV-GGM-79e710's classification 4/4
    observation_collision:
      observable: the transcript of oracle answers
      distinct_preimage_search: two instances (k, k') with identical simulated transcripts for every query sequence of length q < sqrt N / 10
    constructive_transforms:
      - {transform: representation_reduction, proposed_object: lazy simulator with a symmetric random table for Miller values, predicted_gain: closure at exponent 1/2 for the family}
    quantifier_order: "FOR ALL generic algorithms A with q queries to group + structure oracles, FOR ALL instances, Pr[A outputs k] <= O(q^2 / N) + 1/N"
    method_ceiling:
      strongest_certifiable_claim: no algorithm that uses the listed structures only through their oracle behaviour beats sqrt N
      nearby_object_control: the k_emb = 1 fixture, where the Tate self-pairing is bilinear and the simulator provably fails
    proof_obligations:
      - {claim: End and Cl(O)-transport oracles are simulable, responsibility: correctness}
      - {claim: Miller values with N not dividing p-1 have no identities beyond reciprocity symmetry, responsibility: strictness}
      - {claim: the simulator is transcript-consistent, responsibility: interface}
      - {claim: Shoup bound applies to the composed model, responsibility: baseline}
    not_applicable_reason: null
  predictions:
    - {metric: distinguisher_identity_classes_failed_on_k_emb_gt_2_arm, direction: lower, minimum_effect: "0 of all tested classes; any nonzero count is the result"}
    - {metric: distinguisher_identity_classes_failed_on_k_emb_1_control, direction: higher, minimum_effect: ">= 1 (bilinearity) or the battery is invalid"}
  minimal_test:
    design: lazy simulator vs real oracles, depth-3 identity battery, 2^16 queries per oracle, p in {1009, 4099, 10007}, prime-order curves with k_emb > 2
    controls: [k_emb = 1 fixture with nontrivial Tate self-pairing (must be distinguished), random-relabelling null of the group encoding]
    required_metrics: [identity classes failed per arm, query counts, exact curve identities]
  falsification_conditions:
    - a reproducible identity among real Miller or transport values on the k_emb > 2 arm that the simulator cannot satisfy
    - the control arm not distinguished (invalidates the instrument, not the claim)
  confounders: [normalisation conventions for Miller functions at O (leading-coefficient constants masquerading as identities), toy k_emb accidentally small]
  interpretation_limits: [a simulability theorem bounds generic use only; a representation-specific algorithm (index calculus class) is outside its scope and is priced elsewhere]
  heuristic_assumptions: []
  target_complexity:
    time_exponent: no change (closure at N^{1/2})
    memory_exponent: n/a
    best_known: sqrt(pi N / 2) group operations (KR-RHO-13bf67)
    hidden_overhead: none claimed
    tradeoff_note: n/a
  estimated_cost: {implementation: medium, compute: low}
  recommended_priority: medium
  prior_art:
    frontier_map: knowledge/frontiers/ecdlp
    rows_checked: [KR-RHO-13bf67, KR-RHO-817bf8, KR-RHO-53c89f, KR-RHO-0528e7]
    nearest:
      - {ref: KR-RHO-13bf67, provenance: internal, relation: generalizes, delta: "extends the generic bound's scope to named structure oracles; adds no attack"}
      - {ref: LEAD-STR-class-group-ecdlp-bridge, provenance: internal, relation: special_case, delta: "the bridge's simulation lemma is one of four oracles here"}
    searched: {corpus_grep: ["generic group model", "simulable", "vectorization", "ray class"], web: ["generic group action model lower bound discrete logarithm"], blocked: []}
    lead: LEAD-STR-class-group-ecdlp-bridge
    new_lead_reason: null
```

---

### Candidate 2 — Correspondence dichotomy lemma (the algebraic half of candidate 1)

**1. Title.** Every F_p-rational algebraic correspondence out of E acts on G
either through Hom(E, -) (isogeny transport, closed by T1/O2/order inflation)
or through the coordinates of its fibre points (Class II branching, priced by
index-calculus meters); there is no third kind.

**2. Object.** Correspondences Z subset E x Y (Y a curve or abelian variety
over F_{p^n}), including Hecke correspondences T_ell on the level-N moduli
point, Kani/Richelot graph kernels, trace-zero projections and
"non-group-theoretic correspondences" as the revisit clauses call them.

**3. Mechanism and gain level.** None; closure. Weil's theorem: a correspondence
Z of bidegree (a, b) induces a homomorphism Pic^0(E) -> Pic^0(Y), i.e. an
element of Hom(E, Jac Y). On G this is either zero or an injective transport
into an isogeny factor of Jac(Y) of order N; for Y = E it is a scalar (O1); for
Y of genus g >= 2 over the same field the ambient order is N * Theta(N^{g-1})
(same-field genus-g obstruction); over F_{p^n} the only new N-torsion is G'
(O2). What a correspondence offers beyond its homomorphic content is the
unordered fibre Z(R) as a set of points with coordinates — Class II in the
IDEA-20260806-c5d183 trichotomy, whose only price is the measured branching
(L, b) of a decomposition oracle. Gain level: none; the lemma converts two
`revisit_when` clauses into "never for correspondences".

**4. Closest leads and why not foreclosed.** `LEAD-TRF-second-torsion-direction`
(closed; `revisit_when` asks for "a non-group-theoretic correspondence (not a
homomorphism on N-torsion) with verified scalar compatibility" — the lemma says
no such correspondence exists: the homomorphic part is forced, the rest is
coordinate data); `LEAD-TRF-one-point-self-pairing` (`revisit_when`: a
non-bilinear map with partial return — same answer); `LEAD-TRF-same-field-genus-g-embedding`
(order inflation is the Y-of-genus->=2 case); IDEA-20260806-0c9de1 (D)/(F3):
its queued "does T_ell separate fibre points" measurement is forced zero because
T_ell is diamond-equivariant, i.e. transport. Bridge sentence: the Weil
correspondence->homomorphism theorem that the HYPER lane used implicitly for
Kani kernels applies to every correspondence at once, so the three revisit
clauses are one clause and it is closed.

**5. Smallest discriminating experiment.** Toy p in {101, 211}, E ordinary
prime-order. Enumerate F_p-rational effective divisors on E x E of bidegree
<= (3,3) (via NS(E x E) = Z^2 (+) End(E) and explicit curves); for each, compute
the induced map on G as a function table and check it is a scalar; counted
quantity: number of correspondences whose induced map on G is not multiplication
by a scalar (prediction: 0). Second cell: X_1(N)(F_p) for N in {5, 7, 11, 13}
enumerated explicitly (Tate normal form); compute T_ell on fibres for ell in
{2, 3}; counted quantity: fibre-point separation statistic against a random
degree-(ell+1) correspondence null (prediction: forced zero; a nonzero value
means an implementation error, per IDEA-0c9de1 step 5). Control arm: a
non-equivariant random permutation of the fibre (must separate). Falsifying
outcome: any rational correspondence on E x E with non-scalar action on G.

**6. Prior-art risk.** The lemma is textbook (Weil; correspondences and
Jacobians). Its value is in the atlas, not in the literature.
`novelty_status: known` (relation `same` to textbook; provenance recalled, so
formally `unverified` until a KN-LIT entry is opened).

**7. Rating.** Likely-closed-on-inspection as an attack (it is a closure by
design); promising as hygiene because it collapses three revisit clauses into
one and removes the "correspondence" escape hatch from the family's vocabulary.

**Collision phrases:** "Kani embedding of the ECDLP", "trace zero variety
transfer", "distortion map on an ordinary curve", "genus g cover of a prime
field curve", "higher dimensional isogeny embedding". Expected hits:
LEAD-TRF-second-torsion-direction, LEAD-TRF-one-point-self-pairing,
LEAD-TRF-same-field-genus-g-embedding. All consolidated, none re-proposed.

```yaml
idea:
  id: IDEA-20261031-<alloc>
  title: Correspondence dichotomy: homomorphic content of any rational correspondence out of E is an isogeny on G; the rest is fibre coordinate data
  class: control
  claim: >-
    For every F_p-rational correspondence Z subset E x Y, the induced map on G is in
    Hom(E, Jac Y) restricted to G (zero or an order-preserving transport), so no
    correspondence supplies a non-scalar, non-coordinate operation on G. Falsified by
    one rational correspondence E x E of bounded bidegree whose induced map on G is not a scalar.
  mechanism: >-
    Weil: correspondences act on divisor classes as homomorphisms of Jacobians; End(G) = Z/N;
    same-field Jacobians inflate the ambient order; extension-field N-torsion is G' (BK).
    Operation set: correspondences; class: partial action on the class level, branching
    (Class II) on the point-set level.
  novelty_status: unverified
  citations:
    - {ref: "Weil, correspondences on curves induce homomorphisms of Jacobians (textbook)", provenance: recalled, claim: Z of bidegree (a,b) induces Pic^0(E) -> Pic^0(Y), verified_by: null}
    - {ref: IDEA-20260808-40aab9, provenance: internal, claim: graph kernel rational iff k_emb = 1, verified_by: lead file read 2026-10-31}
    - {ref: DEC-20260902-4c82fd, provenance: internal, claim: same-field genus-g embedding closed by order inflation, verified_by: lead file read 2026-10-31}
  assumptions: [prime-order G; ordinary E; correspondences defined over F_p or F_{p^n} with the BK scope]
  proof_search_map:
    bottleneck: none; the lemma is a restatement of a theorem applied to the family
    baseline_embedding: {parameter_slice: Kani/Richelot graph kernels (IDEA-20260808-40aab9) as the special case already closed, reproduction_check: lemma specialised to (N,N)-kernels reproduces "rational iff k_emb = 1"}
    observation_collision: {observable: induced map on G, distinct_preimage_search: distinct correspondences with the same induced scalar (expected: many; the scalar is the only invariant)}
    constructive_transforms:
      - {transform: stronger_invariant, proposed_object: the pair (homomorphic part, fibre-set part) of a correspondence, predicted_gain: none; closure}
    quantifier_order: "FOR ALL rational correspondences Z, EXISTS lambda in Z/N with Z_*|_G = [lambda] composed with a transport"
    method_ceiling: {strongest_certifiable_claim: no correspondence-based transfer escapes T1/O2/order-inflation, nearby_object_control: a correspondence to Y = E' with k_emb = 1 (MOV), where transport into mu_N is rational}
    proof_obligations:
      - {claim: induced map is a homomorphism, responsibility: correctness}
      - {claim: fibre-set data is Class II with measurable branching, responsibility: scope}
    not_applicable_reason: null
  predictions:
    - {metric: non_scalar_correspondences_found, direction: lower, minimum_effect: "0"}
    - {metric: hecke_fibre_separation_vs_null, direction: lower, minimum_effect: "identically 0 (forced)"}
  minimal_test:
    design: enumerate bidegree <= (3,3) correspondences on E x E at p in {101, 211}; T_ell on X_1(N)(F_p) fibres for N in {5,7,11,13}
    controls: [random fibre permutation (must separate), random correspondence of matched degree]
    required_metrics: [count of non-scalar inductions, separation statistic, exact models]
  falsification_conditions: [a rational correspondence with non-scalar induced map on G]
  confounders: [incomplete enumeration of NS(E x E) classes; sign conventions]
  interpretation_limits: [says nothing about coordinate-based (R1/R2) methods; those are the IC families]
  heuristic_assumptions: []
  target_complexity: {time_exponent: no change, memory_exponent: n/a, best_known: sqrt N, hidden_overhead: none, tradeoff_note: n/a}
  estimated_cost: {implementation: low, compute: low}
  recommended_priority: low
  prior_art:
    frontier_map: knowledge/frontiers/ecdlp
    rows_checked: [KR-RHO-53c89f, KR-RHO-817bf8, KR-IC-a4dd54]
    nearest:
      - {ref: LEAD-TRF-second-torsion-direction, provenance: internal, relation: generalizes, delta: "turns its revisit_when into a theorem"}
    searched: {corpus_grep: ["correspondence", "Kani", "trace zero", "distortion"], web: [], blocked: []}
    lead: LEAD-TRF-second-torsion-direction
    new_lead_reason: null
```

---

### Candidate 3 — Prime-field Koblitz analogue: CM curves with a norm-2 endomorphism of prescribed small orbit on G

**1. Title.** Build E/F_p with CM by Z[(1+sqrt(-7))/2] (or Z[sqrt(-2)]) so the
degree-2 endomorphism alpha has multiplicative order h ~ log_2 N on G, and
measure rho on <+-alpha>-classes with canonicalisation fully charged.

**2. Object.** The endomorphism algebra beyond units: alpha = (1+sqrt(-7))/2,
N(alpha) = 2, acting on G as lambda = alpha mod n where n = (pi - 1) is the
norm-N prime of O. By construction N | N(alpha^h - 1) = 2^h + 1 - L_h (L_h the
Lucas sequence with L_{n+1} = L_n - 2 L_{n-1}), so lambda^h = 1 and the
alpha-orbit of a point of G has size h, not N.

**3. Mechanism and gain level.** Rho on classes {+-alpha^i P : 0 <= i < h} of
size 2h gives sqrt(2h)/sqrt(2) = sqrt(h) fewer iterations than negation rho
(the ECC2K Frobenius mechanism, KR-RHO-482ed3, with Frobenius replaced by a
degree-2 CM endomorphism). The recorded obstruction for non-unit endomorphisms
(LEAD-STR-small-cm-disc-nonunit-endo, IDEA-20260901-6b63a4) is n^h >= (sqrt N - 1)^2,
i.e. h >= log_n N; with n = 2 this is h >= log_2 N, and the construction sits
exactly at equality. The obstruction's second half — canonicalisation costs
about h evaluations of alpha, so the net factor is kappa / sqrt(h) with kappa ~
h c(alpha)/c(add) — is the open price. Gain level: constant, at most sqrt(h) ~
sqrt(log N) (~16 at 256 bits) and only if a canonicaliser costing o(h) exists;
with orbit enumeration the predicted net is a LOSS by about sqrt(h) c(alpha)/c(add)
(c(alpha) ~ 6–8 M with batched inversion against c(add) ~ 6 M, so ~ sqrt(h)).
Said plainly: best case a small constant; expected case a measured loss that
closes the lead's `revisit_when`.

**4. Closest leads and why not foreclosed.** `LEAD-STR-small-cm-disc-nonunit-endo`
(closed_obstructed; its `revisit_when` names exactly this object and the program
has never constructed one); `LEAD-STR-glv-gls-isogeny-loop-scalar-mult`
(closed; its premise "a non-unit loop endomorphism acts as lambda of
multiplicative order about r, so its orbits are the whole group" is false by
construction here — the candidate escapes the stated premise, leaving only the
canonicalisation cost); `LEAD-RHO-non-automorphism-equivalence` (open_unexamined;
H-EWALK-29cb90 conjectures Omega(log h) canonicalisation per step for h > 6 —
this construction is the natural test bed); `KN-OPEN-2c095b` (order of
curve-derived lambda; here the order is designed, not sampled);
KR-RHO-482ed3/037e22 (Koblitz sqrt(2m): the binary case where enumeration of
the orbit is free because Frobenius is a rotation in a normal basis — the
reason the prime-field analogue is expected to fail is that alpha costs field
operations). Bridge sentence: ECC2K's sqrt(2m) comes from a degree-2
endomorphism with orbit size m = log_2 of the field size; the CM method lets us
manufacture prime-field curves with the same orbit arithmetic, so the only
remaining difference between the two cases is the per-element orbit cost, which
is the quantity H-EWALK-29cb90 is about.

**5. Smallest discriminating experiment.** Construction: for h in [16, 32],
factor 2^h + 1 - L_h; for each prime factor N >= 2^{h-4} take the generator
gamma_0 of the norm-N prime of O (class number 1); test p = N(1 +- gamma_0)
prime; keep instances with #E = N (prime order) or #E = cN with small c; realise
E by j = -3375 (y^2 = x^3 - 35x - 98 and its twist), choose the twist with
trace Tr(pi), build alpha by Velu through the rational 2-torsion point plus
the isomorphism back to E, verify alpha^2 - alpha + 2 = 0 on random points and
lambda's order exactly h on G. Arms: (a) negation-class rho (control, the
matched baseline of LEAD-RHO-matched-rho-calibration), (b) <+-alpha>-class rho
with canonical representative = minimal x over the orbit, every alpha
evaluation and comparison counted in the ecbench counted unit, (c) same as
(b) but the orbit enumerated x-only with one batched inversion per orbit
(cheapest honest canonicaliser I can name). Counted quantity: total counted
cost to solve, median over >= 200 planted instances per (h, arm), reported as
ratio to arm (a) with 95% intervals; also iterations alone, to confirm the
sqrt(h) iteration saving is real (positive control for the class mechanism).
Toy sizes: N ~ 2^20–2^32. Falsifying outcome for the obstruction: a total-cost
ratio below 1 at h >= 16 that persists across h. Falsifying outcome for the
candidate: ratio >= 1 at every h with iteration saving confirmed (then the lead
closes as measured, with kappa recorded).

**6. Prior-art risk.** Duursma-Gaudry-Morain 1999 (automorphisms of large
order; retrieved abstract-level), Wiener-Zuccherato and Gallant-Lambert-Vanstone
(Frobenius classes; recalled), Bos-Costello-Miele (order-6 automorphism
measured; KR-RHO-825bca). I found no paper that constructs prime-field curves
with a small-order non-automorphism endomorphism for rho; the reason is
presumably the canonicalisation cost, which is also this candidate's predicted
outcome. `novelty_status: unverified`.

**7. Rating.** Speculative. One sentence: the iteration saving is real and the
object has never been built, but the total-cost prediction is a loss of about
sqrt(h), so the likely result is a measured closure rather than an improvement.

**Collision phrases:** "cheap endomorphism of degree 2 gives rho equivalence
classes", "endomorphism claw from small D_0", "small CM discriminant makes
ECDLP easier", "isogeny-loop endomorphism speeds up ECDLP", "quotient rho by
multiplier subgroup", "equivalence classes beyond automorphisms". Expected hits:
LEAD-STR-small-cm-disc-nonunit-endo (advanced: realises its revisit_when),
LEAD-STR-glv-gls-isogeny-loop-scalar-mult (premise escaped, stated),
LEAD-RHO-non-automorphism-equivalence (advanced: supplies the test bed).

```yaml
idea:
  id: IDEA-20261031-<alloc>
  title: Prime-field Koblitz analogue: CM-by-Z[(1+sqrt(-7))/2] curves with the norm-2 endomorphism of designed orbit size h ~ log_2 N on G, rho on <+-alpha>-classes with canonicalisation charged
  class: algorithm
  claim: >-
    On curves constructed with N | N(alpha^h - 1), rho on <+-alpha>-classes needs
    sqrt(h) fewer iterations than negation rho (positive control), and its total
    counted cost relative to negation rho is kappa/sqrt(h) with kappa the charged
    per-step canonicalisation cost; the recorded obstruction predicts kappa >= (h-1)
    c(alpha)/c(add), hence a net loss of about sqrt(h). The claim is falsified (and
    the lead reopened) if total cost falls below negation rho at h >= 16.
  mechanism: >-
    Representation: Weierstrass points; operation set: translation plus the endomorphism
    alpha (degree 2) and negation; the tracked object is the orbit class (block system of
    <+-alpha> acting on G, Class I partial action per IDEA-20260901-863e36); the priced
    open number is the canonicalisation cost kappa. Escapes the glv-gls premise (orbit =
    whole group) by designing ord_N(lambda) = h.
  novelty_status: unverified
  citations:
    - {ref: KR-RHO-482ed3, provenance: internal, claim: Koblitz signed-Frobenius classes give sqrt(pi r/(4m)), verified_by: frontier map read 2026-10-31}
    - {ref: IDEA-20260901-6b63a4, provenance: internal, claim: n^h >= (sqrt N - 1)^2 for a norm-n endomorphism with eigenvalue order h, verified_by: lead file read 2026-10-31}
    - {ref: H-EWALK-29cb90, provenance: internal, claim: canonicalisation cost conjecture for multiplier subgroups of order > 6, verified_by: lead file read 2026-10-31}
    - {ref: "Duursma, Gaudry, Morain, Speeding up the discrete log computation on curves with automorphisms, ASIACRYPT 1999", provenance: retrieved, claim: sqrt(m) speedup for automorphisms of order m, verified_by: web search result 2026-10-31}
  assumptions:
    - Class number 1 for D = -7 (so the norm-N prime is principal); CM construction of E/F_p with prescribed Frobenius.
    - Counted-unit cost model of ecbench for alpha evaluations and comparisons.
  proof_search_map:
    bottleneck: the per-step canonicalisation cost kappa for an orbit of size h under a degree-2 endomorphism
    baseline_embedding: {parameter_slice: h = 1 (negation only) reproduces KR-RHO-fb88e6; h = 3 with an automorphism reproduces the j = 0 sqrt 6, reproduction_check: ratio-to-ceiling within the EV-ENDO-10109d band}
    observation_collision: {observable: canonical orbit representative, distinct_preimage_search: none (the class is the object)}
    constructive_transforms:
      - {transform: specialization_pack, proposed_object: the CM family with N | N(alpha^h - 1), predicted_gain: constant sqrt(h) in iterations, net predicted <= 1/sqrt(h) in total cost}
    quantifier_order: "EXISTS a curve family (constructed) such that FOR ALL instances the iteration saving is sqrt(h); the total-cost sign is the measured unknown"
    method_ceiling: {strongest_certifiable_claim: a constant <= sqrt(log N), never an exponent, nearby_object_control: a j = 0 curve of the same N (automorphism classes, known sqrt 6 net gain) and a generic-D curve of the same N (no classes)}
    proof_obligations:
      - {claim: the construction yields ord_N(lambda) = h exactly, responsibility: correctness}
      - {claim: iteration count scales as sqrt(h) saving, responsibility: success_probability}
      - {claim: kappa >= (h-1) c(alpha)/c(add) for orbit-enumeration canonicalisers, responsibility: runtime}
    not_applicable_reason: null
  predictions:
    - {metric: iterations_ratio_alpha_classes_over_negation, direction: lower, minimum_effect: "about 1/sqrt(h), e.g. 0.25 at h = 16"}
    - {metric: total_counted_cost_ratio_over_negation, direction: higher, minimum_effect: "predicted >= 1 (loss); the candidate is alive only if < 0.9 at h >= 16"}
  minimal_test:
    design: three arms (negation rho; alpha-class rho full canonicalisation; alpha-class rho x-only batched canonicalisation), h in [16, 32], N ~ 2^20..2^32, >= 200 planted instances per cell
    controls: [j = 0 automorphism-class rho on a matched-N curve (positive), generic-D curve of matched N (null), matched-rho calibration per LEAD-RHO-matched-rho-calibration]
    required_metrics: [iterations, counted cost, kappa per step, exact curve identities and seeds]
  falsification_conditions:
    - total-cost ratio >= 1 at every h with the iteration saving confirmed closes the candidate (lead stays closed, revisit_when discharged)
    - iteration saving absent means the class walk is mis-implemented (invalid run, not evidence)
  confounders: [fruitless cycles in class walks (handle per KR-RHO-fb88e6), batching across walks hiding alpha cost, choice of representative rule]
  interpretation_limits: [constant-factor only; nothing about generic-D deployed curves (|D_K| large, no norm-2 endomorphism)]
  heuristic_assumptions:
    - {id: H1, statement: "rho on the N/(2h) classes behaves as a random mapping on N/(2h) points", rigorous_support: "KR-RHO-93979e (random-oracle partition bound) for the class walk as in Duursma-Gaudry-Morain", validation_plan: "iteration histogram vs sqrt(pi N/(4h)) at each h, KS test, >= 200 instances"}
  target_complexity:
    time_exponent: N^{1/2} (unchanged)
    memory_exponent: polylog (distinguished points)
    best_known: sqrt(pi N / 4) iterations with negation
    hidden_overhead: kappa ~ h alpha-evaluations per step; the whole question
    tradeoff_note: parallelises as rho; no memory change
  estimated_cost: {implementation: medium, compute: low}
  recommended_priority: low
  prior_art:
    frontier_map: knowledge/frontiers/ecdlp
    rows_checked: [KR-RHO-0528e7, KR-RHO-482ed3, KR-RHO-037e22, KR-RHO-fb88e6, KR-RHO-825bca, KR-RHO-13bf67]
    nearest:
      - {ref: KR-RHO-482ed3, provenance: internal, relation: adjacent, delta: "same class mechanism with a degree-2 CM endomorphism instead of Frobenius; the orbit cost is the difference"}
      - {ref: LEAD-STR-small-cm-disc-nonunit-endo, provenance: internal, relation: special_case, delta: "constructs the equality case its revisit_when names"}
    searched: {corpus_grep: ["norm-2 endomorphism", "equality case", "Koblitz analogue", "canonicalisation"], web: ["Pollard rho equivalence classes endomorphism small order prime field"], blocked: []}
    lead: LEAD-STR-small-cm-disc-nonunit-endo
    new_lead_reason: null
```

---

### Candidate 4 — Kummer identification of the Miller primitive: U = f_{N,P}^{1/N} is a degree-N rational function on E/G

**1. Title.** The "canonical Miller-cocycle primitive" U(R) = f_{N,P}(R)^{1/N}
(N not dividing p-1) is the Kummer generator of the function-field extension
F_p(E/G) / F_p(E); forced values K1, K2 and a Fourier prediction that decide
the two open Miller-cocycle leads.

**2. Object.** The group scheme E[N] = G (+) G' with G' ~ mu_N; the etale
mu_N-torsors over E, which by the Kummer sequence are classified by
H^1_et(E, mu_N) ~ Pic^0(E)(F_p)[N] = G when F_p^*/(F_p^*)^N is trivial; the
torsor attached to P is y^N = f_{N,P}, and it is the isogeny cover
phi-hat: E/G -> E whose kernel phi(E[N]) ~ E[N]/G ~ mu_N. Hence U = f_{N,P}^{1/N}
is a rational function on E/G of degree N (zeros at the N translates of a
preimage of P by ker phi-hat, poles at ker phi-hat), and for R in E(F_p) the
unique N-th root of f_{N,P}(R) in F_p^* is U evaluated at the unique rational
preimage of R (phi-hat is a bijection on rational points since
(mu_N)(F_p) = 1).

**3. Mechanism and gain level.** No gain claimed; this is a zero-compute
sharpening of an open lead. Forced values: K1 (U is the unique primitive) is
Hilbert 90 for mu_N over F_p. K2 (the lead's U(kP) = c r_k C^{k/N}) follows
from the Miller identity f_{N,kP} = f_{N,P}^k / f_{k,P}^N and reciprocity:
U_P(kP) equals, up to a fixed constant and a factor gamma^k with gamma the
N-th root of the normalised self-value C, the reciprocal of the Miller
self-value f_{k,P}(P), a k-fold product of line values at P — an elliptic-net
quantity whose recovery of k is the closed EDS problem (LEAD-EXO-elliptic-net-eds).
Consequences: (i) U_P(kP) is a cheap function of kP that equals an EDS-type
quantity of index k, so the Miller-cocycle lead and the elliptic-net lead are
one object seen from two sides; (ii) log U_P(kP) contains a known linear
component k log gamma (mod p-1), which a Fourier test must regress out or it
will see resonance peaks that carry no information; (iii) because U has degree
N on a genus-1 curve, Weil/Perel'muter bounds (~ deg U sqrt p) are vacuous, so
equidistribution cannot be proved and the toy test is the only arbiter; the
natural prediction is hash-like behaviour because the divisor of U is supported
on non-rational points. Gain level: reformulation with no algorithmic content;
the deliverable is a decision for an open lead.

**4. Closest leads and why not foreclosed.**
`LEAD-TRF-miller-cocycle-nonhom-transfer` (open_unexamined) and
`LEAD-EXO-miller-pairing-cocycle` (open_next_step): both cite
IDEA-20261017-e3a6f1 and list K1/K2 as things to verify; this candidate derives
them and identifies the curve U lives on. `LEAD-EXO-elliptic-net-eds` (closed):
the collapse the EXO lead's `discriminates` clause anticipates is made explicit.
IDEA-20260807-6eab6a: the ell-primary coprimality argument is void exactly at
ell = N, and this is the ell = N object. Bridge sentence: Kummer theory for the
mu_N half of E[N] (O2) identifies the Miller primitive with a rational function
on the isogenous curve E/G, which puts the open Miller lead on the same footing
as the closed net lead and turns its toy test into a decision with a stated
forced value.

**5. Smallest discriminating experiment.** p in {1009, 10007, 100003},
prime-order curves with N not dividing p-1, p^2-1. (a) Exact check of the
identification: compute U_P(R) by Miller + unique root for all R in G, compute
the rational preimage R_1 on an explicit model of E/G (Velu with kernel G,
toy size), evaluate the Kummer generator on E/G, compare: 100% agreement or
the derivation is wrong. (b) Exact check of K2: U_P(kP) f_{k,P}(P) gamma^{-k}
constant over k (k known in the toy). (c) Full Fourier spectrum over Z/N of
ell(k) = log_g U_P(kP) and of E(k) = log_g f_{k,P}(P), against the null of a
random function G -> F_p^* with the same marginal, with the linear term
regressed out; counted quantity: maximal normalised Fourier coefficient and the
count of coefficients above the null's 99.9% quantile. Control arm (positive):
a toy curve with N | p-1 where (f_{N,P}(kP))^{(p-1)/N} = t(P,P)^k is a genuine
character of k — the spectrum MUST show a peak; if not, the instrument is
blind. Falsifying outcome (for the prediction, i.e. the interesting result):
reproducible coefficients above the null on the N not dividing p-1 arm across
all three primes after the linear term is removed.

**6. Prior-art risk.** Kummer theory of isogenies with mu_N kernel and the
Miller identity f_{ab} = f_a^b f_{b,aP} are textbook (Silverman; Miller 2004,
recalled). The identification is standard mathematics applied to this program's
object; the novelty is only in the decision it forces. `novelty_status: known`
(textbook, recalled; hence formally unverified).

**7. Rating.** Likely-closed-on-inspection. One sentence: U is a degree-N
function whose rational values are predicted to be Fourier-flat, and K2 shows
the only structure in them is the closed elliptic-net recursion; the toy test
is cheap and ends the lead either way.

**Collision phrases:** "Miller function transfer", "unreduced Tate pairing
value", "zeta defect quasi-homomorphism", "pairing-free Miller cocycle",
"division-polynomial value collisions below birthday", "elliptic net relations
for discrete log". Expected hits: LEAD-TRF-miller-cocycle-nonhom-transfer,
LEAD-EXO-miller-pairing-cocycle, LEAD-EXO-elliptic-net-eds. Advances the first
two, confirms the third.

```yaml
idea:
  id: IDEA-20261031-<alloc>
  title: The Miller primitive U = f_{N,P}^{1/N} is the Kummer generator of F_p(E/G)/F_p(E), a degree-N function on E/G; K1 is Hilbert 90, K2 is the Miller self-value identity, and the Fourier spectrum of U on G decides the open Miller leads
  class: control
  claim: >-
    For N not dividing p-1, the etale mu_N-torsor y^N = f_{N,P} over E is the isogeny
    cover E/G -> E, so U is a rational function of degree N on E/G, its values on
    E(F_p) are its values at the rational preimages, and U_P(kP) equals up to a fixed
    constant and gamma^k the reciprocal Miller self-value f_{k,P}(P). Prediction:
    after removing the linear term k log gamma, log U_P(kP) is Fourier-flat over Z/N
    at the random-function level. Falsified by exact disagreement in test (a) or (b),
    or by reproducible above-null Fourier mass in (c).
  mechanism: >-
    Kummer sequence on E_et with trivial unit contribution (F_p^*/N = 1); H^1(E, mu_N) = G;
    kernel of the dual isogeny E/G -> E is E[N]/G ~ mu_N; Miller identity
    f_{N,kP} = f_{N,P}^k / f_{k,P}^N with reciprocity. Operation set: argument translation
    by G (no cheap transformation law for U) and the scalar action (K2); U is Class II
    (branching) under neither, it is simply a hash of the point unless the spectrum says otherwise.
  novelty_status: unverified
  citations:
    - {ref: IDEA-20261017-e3a6f1, provenance: internal, claim: U is a canonical primitive when N does not divide p-1; K1, K2 as stated, verified_by: lead files read 2026-10-31}
    - {ref: "Miller, The Weil pairing and its efficient calculation, J. Cryptology 2004", provenance: recalled, claim: f_{ab,P} = f_{a,P}^b f_{b,aP} for normalised Miller functions, verified_by: null}
    - {ref: "Silverman, AEC, Kummer theory / isogenies with mu_N kernel (textbook)", provenance: recalled, claim: mu_N-torsors over a variety with trivial global units are classified by Pic[N], verified_by: null}
    - {ref: KN-FIND-002, provenance: internal, claim: elliptic-net oracle GGM-simulable with O(log N) overhead, verified_by: lead file read 2026-10-31}
  assumptions: [N prime, N not dividing p^j - 1 for j below k_emb; Miller functions normalised at O]
  proof_search_map:
    bottleneck: whether the rational values of a degree-N function on E/G carry any Fourier structure over Z/N
    baseline_embedding: {parameter_slice: N | p-1 (reduced Tate self-pairing is a character of k), reproduction_check: a Fourier peak at the character frequency on the control fixture}
    observation_collision: {observable: log U_P(kP) as a function of k, distinct_preimage_search: two values of k with equal U (expected at the birthday rate; U is injective-ish)}
    constructive_transforms:
      - {transform: representation_reduction, proposed_object: U as an element of F_p(E/G) of degree N, predicted_gain: none; decision only}
    quantifier_order: "FOR ALL k, U_P(kP) f_{k,P}(P) gamma^{-k} = c (exact); FOR ALL nontrivial characters chi of Z/N, |sum_k chi(k) psi(ell(k) - k log gamma)| = O(sqrt N) (prediction)"
    method_ceiling: {strongest_certifiable_claim: the Miller primitive carries no k-structure beyond the EDS recursion, nearby_object_control: the N | p-1 fixture where it carries a full character}
    proof_obligations:
      - {claim: torsor identification with E/G, responsibility: correctness}
      - {claim: K2 identity, responsibility: correctness}
      - {claim: Fourier flatness, responsibility: success_probability (measured, not proved)}
    not_applicable_reason: null
  predictions:
    - {metric: exact_identification_agreement, direction: higher, minimum_effect: "100% of points"}
    - {metric: max_normalised_fourier_coefficient_vs_null_99.9pct, direction: lower, minimum_effect: "at or below the null on all three primes after regressing the linear term"}
  minimal_test:
    design: tests (a) identification, (b) K2, (c) spectrum, at p in {1009, 10007, 100003}
    controls: [N | p-1 fixture (must peak), random function null with matched marginal, k-resampled null at fixed curve]
    required_metrics: [agreement counts, spectrum statistics, exact models and seeds]
  falsification_conditions: [exact disagreement in (a) or (b); reproducible above-null spectrum in (c)]
  confounders: [the linear term k log gamma producing resonance peaks (regress it out); normalisation at O]
  interpretation_limits: [toy primes only; a flat spectrum at toy size is the predicted behaviour of a degree-N function and does not prove flatness at crypto size, but the lead's own next_action accepts it as closure]
  heuristic_assumptions: []
  target_complexity: {time_exponent: no change, memory_exponent: n/a, best_known: sqrt N, hidden_overhead: none, tradeoff_note: n/a}
  estimated_cost: {implementation: low, compute: low}
  recommended_priority: medium
  prior_art:
    frontier_map: knowledge/frontiers/ecdlp
    rows_checked: [KR-RHO-53c89f, KR-RHO-13bf67]
    nearest:
      - {ref: LEAD-EXO-miller-pairing-cocycle, provenance: internal, relation: same, delta: "derives K1/K2 and names the curve U lives on; adds the control fixture and the linear-term caveat"}
      - {ref: LEAD-EXO-elliptic-net-eds, provenance: internal, relation: adjacent, delta: "shows the two leads are one object"}
    searched: {corpus_grep: ["Miller cocycle", "canonical primitive", "f^{1/N}", "Kummer"], web: [], blocked: []}
    lead: LEAD-TRF-miller-cocycle-nonhom-transfer
    new_lead_reason: null
```

---

### Candidate 5 — Scalar-action block systems: the one operation set the rigidity theorem has not been applied to, and its price

**1. Title.** The (Z/N)^* scalar action on G \ {0} is a regular action whose
block systems are multiplicative cosets k Delta; a cheap chi-eigenfunction of
order m would be worth sqrt(m) through a multiplicative BSGS/rho, and no
rational function on E can be one (degree lemma), so every candidate is a
level-N function and reduces to candidate 4.

**2. Object.** Functions u on G with u(dP) = chi(d) u(P) for a character chi
of (Z/N)^* of order m; equivalently the intermediate covers
X_1(N) -> X_Delta(N) -> X_0(N) for Delta = ker chi (the "F2 live corner" of
IDEA-0c9de1 exists for prime N because (Z/N)^*/{+-1} is cyclic of composite
order).

**3. Mechanism and gain level.** Given chi(k) (k's coset mod Delta, index m),
write k = k_0 h^b with h generating Delta; then Q = [h^b] P' with
P' = [k_0] P, a DLP in the cyclic group Delta acting freely on the orbit,
solvable by BSGS or rho in about 2 sqrt((N-1)/m) scalar multiplications, i.e.
~2.4 log N sqrt(N/m) group operations; this beats negation rho only when
m > (2.4 log N)^2 (~2^18.5 at 256 bits) and the eigenfunction costs less than
the saving. GGM: computing k mod Delta from kP generically costs Omega(sqrt N)
regardless of m (success probability <= 1/m + O(q^2/N)), so any cheap
eigenfunction is representation-specific. Degree lemma: a rational function u
on E with u o [d] = chi(d) u has deg(u o [d]) = d^2 deg u != deg u, so no
rational function of the coordinates is a chi-eigenfunction on all of E; an
eigenfunction can exist only as a function of the level-N structure (division
polynomials, Miller functions, Siegel-unit products), which are the objects of
candidate 4 and the closed EDS lead. Gain level: primitive-level pricing; the
only algorithmic content is the conversion cost formula, which says even an
index-2 eigenfunction (the "Legendre symbol of the discrete log") would be
worth nothing on E, in contrast to F_p^*, where it is free. Said plainly: a
frame-completing lemma, no attack.

**4. Closest leads and why not foreclosed.** `LEAD-EXO-lossy-object-propagation`
(open_next_step; the translation-rigidity theorem IDEA-20260806-c5d183 and the
block-system theorem IDEA-20260901-863e36 are stated for operation sets
containing translation — this applies 863e36 to the scalar action, which is
regular on G \ {0} and therefore has exactly the multiplicative cosets as block
systems); `LEAD-EXO-coordinate-statistic-leakage` (its census found every
stable multiplicative coset statistic at the random level — the degree lemma
explains why that was forced for rational functions and confines any survivor
to level-N functions); `LEAD-RHO-lhw-modular-filter-price` (the additive
residue-guess price; this is the multiplicative analogue);
`LEAD-EXO-hnp-advice-leakage` (conversion of partial information; the
multiplicative conversion formula is the missing row). Bridge sentence: the
program's rigidity results were proved for translation; the scalar action is
the only other regular action on G, and applying the same theorem there yields
cosets, a conversion price, and (with the degree lemma) a reduction of every
eigenfunction candidate to candidate 4.

**5. Smallest discriminating experiment.** p in {1009, 4099}, prime-order
curves. (a) Enumerate all rational functions of degree <= 4 in x, y over F_p
(up to scaling) and compute their correlation with chi(k) for chi of order 2
and 3 across all k; counted quantity: maximal normalised correlation against
the random-relabelling null (prediction: null level — the census already saw
this for its statistics; here the class is exhaustive at bounded degree).
(b) Multiplicative BSGS/rho cost with an oracle for chi(k) planted (oracle
cost set to 0), m in {2, 16, 256}: counted cost vs negation rho; prediction
matches 2.4 log N sqrt(N/m) within the birthday spread; this is the pricing
row, with a planted oracle so there is a possible negative (if the measured
conversion is far worse, the price formula is wrong). Control arm: the F_p^*
analogue where the Legendre symbol of the log is free and the index-2 saving
is realised. Falsifying outcomes: a bounded-degree rational function correlated
with chi(k) above the null (would contradict the degree lemma as applied on G
and be the result), or a conversion cost off the formula.

**6. Prior-art risk.** Hard-core bits of the DL (Blum-Micali; Håstad-Näslund;
Kaliski for elliptic curves; Schnorr's generic one-wayness; retrieved
abstract-level) and Legendre-PRF key recovery (Beullens-Beyne-Udovenko-Vitto;
Kaluderović-Kleinjung-Kostić; recalled) are adjacent; I found no statement of
the degree lemma or of the multiplicative conversion price for elliptic groups.
`novelty_status: unverified`.

**7. Rating.** Likely-closed-on-inspection. One sentence: the lemma makes the
census's negative a theorem for rational functions and shows that the "Legendre
symbol of the log" shortcut of F_p^* has no cheap analogue on E, but it opens
nothing.

**Collision phrases:** "stable and structured statistic on the curve group",
"split-quotient certificate", "residue-guess price", "convert a statistical
distinguisher into key recovery", "modular unit diamond eigenspace" (rejected
ECDLP-IDEA-112). Expected hits: LEAD-EXO-coordinate-statistic-leakage,
LEAD-EXO-lossy-object-propagation, LEAD-RHO-lhw-modular-filter-price,
LEAD-EXO-hnp-advice-leakage. Advances the first two, adds a row to the third.

```yaml
idea:
  id: IDEA-20261031-<alloc>
  title: Scalar-action block systems on G are multiplicative cosets; a chi-eigenfunction of order m is worth 2.4 log N sqrt(N/m) and cannot be a rational function on E (degree lemma)
  class: control
  claim: >-
    (i) Lossy objects propagating deterministically under the (Z/N)^* scalar action on
    G \ {0} are exactly the cosets of subgroups Delta; (ii) knowing k mod Delta of index
    m converts to a full solve in about 2 sqrt((N-1)/m) scalar multiplications; (iii) no
    rational function on E satisfies u o [d] = chi(d) u for d >= 2 (degree). Falsified by
    a bounded-degree rational function correlated with chi(k) above the null, or by a
    measured conversion cost off the formula with a planted oracle.
  mechanism: >-
    Block-system theorem (IDEA-20260901-863e36) applied to a regular action; multiplicative
    BSGS/rho in the cyclic group Delta acting on the orbit; deg(u o [d]) = d^2 deg u.
    Operation set: scalar action; class: partial action (Class I); the discarded
    information is k mod Delta's complement; the priced number is the eigenfunction cost.
  novelty_status: unverified
  citations:
    - {ref: IDEA-20260901-863e36, provenance: internal, claim: lossy objects propagating under Sigma are block systems of <Sigma>, verified_by: agents/idea-generator.md search heuristic 6 read 2026-10-31}
    - {ref: EV-ECDLP-81f4d4, provenance: internal, claim: stable multiplicative coset statistics sit at the random level, verified_by: lead file read 2026-10-31}
    - {ref: "Schnorr, Security of almost all discrete log bits / generic one-wayness (recalled; Kaliski's EC bit-hardness cited therein)", provenance: retrieved, claim: individual bits of EC discrete logs are hard in the Blum-Micali sense via an oracle technique for abelian groups, verified_by: web search snippet 2026-10-31}
  assumptions: [prime N; chi trivial on {+-1} when the walk uses negation classes]
  proof_search_map:
    bottleneck: existence of a sub-sqrt(N/m) chi-eigenfunction of order m >= (2.4 log N)^2
    baseline_embedding: {parameter_slice: F_p^* with chi = Legendre symbol (free, index 2), reproduction_check: the multiplicative conversion realises the index-2 saving there}
    observation_collision: {observable: chi(k), distinct_preimage_search: all k in the same coset (by construction N/m of them)}
    constructive_transforms:
      - {transform: observable_fiber, proposed_object: the coset k Delta as tracked object, predicted_gain: sqrt(m) at eigenfunction cost c_chi; none known below N}
    quantifier_order: "FOR ALL rational u on E, FOR ALL d >= 2, u o [d] != chi(d) u (degree); EXISTS? level-N u with cost o(sqrt(N/m)) — open, reduces to candidate 4"
    method_ceiling: {strongest_certifiable_claim: no coordinate-rational eigenfunction; conversion price formula, nearby_object_control: F_p^* where the index-2 eigenfunction is the Legendre symbol}
    proof_obligations:
      - {claim: block systems of a regular action are cosets, responsibility: correctness}
      - {claim: conversion cost formula, responsibility: runtime}
      - {claim: degree lemma, responsibility: strictness}
    not_applicable_reason: null
  predictions:
    - {metric: max_correlation_bounded_degree_rational_functions_with_chi, direction: lower, minimum_effect: "null level at degree <= 4"}
    - {metric: planted_oracle_conversion_cost_ratio_vs_formula, direction: different, minimum_effect: "within the birthday spread of 2.4 log N sqrt(N/m)"}
  minimal_test:
    design: exhaustive bounded-degree correlation scan and planted-oracle conversion timing at p in {1009, 4099}
    controls: [random relabelling null, F_p^* Legendre analogue (positive)]
    required_metrics: [correlation maxima, counted costs, models and seeds]
  falsification_conditions: [above-null correlation for a rational function; conversion cost off the formula]
  confounders: [chi of order 2 coinciding with negation classes; small-p saturation of the function space]
  interpretation_limits: [bounded degree only; level-N functions are deferred to candidate 4]
  heuristic_assumptions: []
  target_complexity: {time_exponent: no change, memory_exponent: n/a, best_known: sqrt N, hidden_overhead: none, tradeoff_note: n/a}
  estimated_cost: {implementation: low, compute: low}
  recommended_priority: low
  prior_art:
    frontier_map: knowledge/frontiers/ecdlp
    rows_checked: [KR-RHO-13bf67, KR-RHO-cd86f5, KR-RHO-ea34b8]
    nearest:
      - {ref: LEAD-EXO-coordinate-statistic-leakage, provenance: internal, relation: generalizes, delta: "explains the census's multiplicative-coset null by a degree lemma and prices a survivor"}
      - {ref: LEAD-RHO-lhw-modular-filter-price, provenance: internal, relation: adjacent, delta: "multiplicative analogue of the residue-guess price"}
    searched: {corpus_grep: ["multiplicative coset", "scalar action", "eigenfunction", "Legendre symbol"], web: ["Legendre symbol of the discrete logarithm hard-core predicate"], blocked: []}
    lead: LEAD-EXO-lossy-object-propagation
    new_lead_reason: null
```

## 3. Examined and dropped (would have been candidates 6–9)

Each is a rephrase of an existing lead or record; filed here so the matcher's
hits are expected rather than surprising.

- **Quaternion/Deuring structure on supersingular E/F_p for ECDLP.** Dropped as
  dominated: a supersingular curve over F_p has #E = p+1 and embedding degree
  2, so every non-rational endomorphism is a distortion map and the ECDLP is
  MOV-reducible to F_{p^2}^* (KR-RHO-53c89f, LEAD-TRF-mov-small-embedding-degree,
  IDEA-20260807-464ff8's supersingular slice). The Deuring correspondence is a
  sampling shortcut for isogeny problems (used in IDEA-20260829-056e9d and
  -ec17aa), not an ECDLP resource. No candidate.
- **(E, P) as a point of X_1(N); diamond torsor.** Already proposed and decided
  at zero compute by IDEA-20260806-0c9de1 (F1 rational torsors trivial, F2 free
  action, F3 Eichler-Shimura pins <p>), with rejected corpus ideas 112
  (modular-unit diamond eigenspace: gonality/degree), 023 (monodromy word) and
  026 (N-division Kummer cocycle). The j = 0 "non-free" corner is the known
  sqrt 6; the composite-N corner is Pohlig-Hellman; the Hecke T_ell corner is
  forced zero (candidate 2). Not re-proposed; see atlas finding (a).
- **F_{p^2}-twist coset representation E(F_{p^2}) = G (+) G'.** IDEA-20260906-476f20
  (proposed control with a forced yield-and-rank value) under
  LEAD-ICP-full-width-arity-grid; sextic/quartic twist versions foreclosed by
  LEAD-STR-secp256k1-cm-class-audit. Trace-zero reading foreclosed by
  LEAD-TRF-second-torsion-direction. Not re-proposed.
- **Ray-class fibre / Cl_n(O)-torsor with level structure.** IDEA-20260812-a3720a
  under LEAD-STR-class-group-ecdlp-bridge; candidate 1 advances it instead.
- **Lenstra's isomorphism E(F_p) ~ O/(pi-1) as an explicit module structure;
  GLV decomposition k = a + b lambda as a 2-D search.** Scalar action (O1) and
  LEAD-STR-glv-gls-isogeny-loop-scalar-mult; no content.
- **Kernel polynomial / sqrt-Velu evaluation of the rational mu_N-isogeny
  E -> E/G'.** Costs Omega(N) to write down (Elkies at degree N) or transports
  k (T1) when it exists; nothing beyond LEAD-STR-isogeny-class-generic-invariance.
- **Brauer-Manin-style invariants of (E, P) over F_p.** Br(F_p) = 0 and every
  torsor over F_p with a rational point is trivial (Lang; IDEA-0c9de1 F1;
  rejected ECDLP-IDEA-207): vacuous.
- **Quadratic-twist pair as a joint multi-target or Richelot-glued surface.**
  Coprime orders N, N' give no shared structure; gluing is same-field genus 2
  (LEAD-TRF-same-field-genus-g-embedding, order inflation).

## 4. Atlas findings (coverage and disposition)

- **(a) No lead for level-structure / modular-curve reformulations.**
  `coverage.tsv` maps IDEA-20260806-0c9de1 (X_1(N) diamond torsor) to
  `LEAD-TRF-teske-secret-isogeny-trapdoor`, which is unrelated, so a future
  rephrasing ("diamond operator", "X_1(N)", "modular unit", "level structure")
  would not collide with a lead that names its obstruction. Recommend a new row
  `LEAD-STR-level-structure-torsor`, disposition `closed_obstructed`
  (obstruction: F1–F3 of IDEA-0c9de1 plus the gonality/degree obstruction of
  rejected ECDLP-IDEA-112/023/026; `best_measured: none`; the forced-zero T_ell
  check is a derivation, not a run), `forecloses`: "X_1(N) diamond torsor",
  "modular unit eigenfunction of the level structure", "diamond operator
  coordinate", "Hecke operator separates fibre points", "level structure
  monodromy word". This is a coverage gap, not a mis-disposition.
- **(b) Duplicate Miller-cocycle leads.** `LEAD-TRF-miller-cocycle-nonhom-transfer`
  (open_unexamined) and `LEAD-EXO-miller-pairing-cocycle` (open_next_step) are
  the same mechanism (both rest on IDEA-20261017-e3a6f1 and its K1/K2). One
  should become `closed_dominated` by the other, or they should be merged;
  candidate 4 supplies the derivation either would record.
- **(c) `LEAD-STR-small-cm-disc-nonunit-endo`'s `revisit_when` is constructible
  now** (candidate 3): the disposition is sound, but the clause reads as if the
  object were hypothetical; the CM method produces it at toy size in minutes.
  Suggest the next review either runs candidate 3 or rewords the clause to
  "canonicaliser costing o(h)", which is the real unknown.
- **(d) Wording in `LEAD-TRF-second-torsion-direction`.** "Hence for N not
  dividing k, T_k(E)[N] = 0" should read "for k_emb not dividing k" (the
  embedding degree divides k is the BK condition, not N | k). Typo-level; the
  gist is correct.
- **(e) No mis-dispositions found** among the structure/transfer/exotic leads
  touching this family: every `closed_*` row names an obstruction that I could
  re-derive (O1–O3 of section 1), and the `exhausted_at_scale` rows state their
  scale.

## 5. Honest accounting (docs/inventor-protocol.md section 5)

- **Objects studied.** E(F_p) as an O-module (O1); the Galois module
  E[N] = G (+) G' and its mu_N half (O2); the isogeny class as a Cl(O)-torsor
  and its level-N refinement; algebraic correspondences out of E; the Miller
  primitive U as a Kummer generator on E/G; the (Z/N)^* scalar action and its
  block systems; CM curves with a designed small-orbit endomorphism; twist
  families; supersingular quaternion structure (dropped, MOV).
- **Depth of verified structure.** Derivation tier, unreviewed, no measurement.
  Candidates 2, 4, 5 re-derive established mathematics (Weil correspondences,
  Kummer theory of mu_N-isogenies, degree of composition, block systems of a
  regular action) through this program's lens and are recorded as exactly that.
  Candidate 1 is a conjectured theorem with a named failure point. Candidate 3
  is a construction whose cost prediction is derived from the recorded
  obstruction, not measured.
- **dominated_by.** `n/a (no result claimed)` for all five. Frontier rows
  checked: KR-RHO-13bf67, -817bf8, -53c89f, -0528e7, -482ed3, -037e22, -fb88e6,
  -825bca, -cd86f5, -ea34b8, -93979e; KR-IC-a4dd54, -955fd6, -cd159a.
- **sota_delta.** No attack. Candidate 3's best case is a constant
  <= sqrt(log N) in iterations with a predicted total-cost ratio >= 1; the
  others are closures or pricing rows with time exponent unchanged at 1/2.
- **Closures proposed, with mechanism (section 4 standard).** (i) Correspondence
  dichotomy (candidate 2): obstruction = Weil's homomorphism theorem + O1/O2/order
  inflation; closes the "non-group-theoretic correspondence" revisit clauses.
  (ii) Miller primitive (candidate 4): obstruction = Kummer identification +
  Miller self-value identity reducing to the closed EDS lead; closure is
  conditional on the toy spectrum, stated as a prediction. (iii) Scalar-action
  degree lemma (candidate 5): obstruction = degree growth under [d]; closes
  coordinate-rational eigenfunctions only. (iv) Candidate 1 would close the
  family at exponent 1/2 if proved; recorded as a proof obligation, not a closure.
- **Open directions for the next session.** Prove or break the Miller-value
  simulator (candidate 1's bottleneck); run candidate 4's spectrum with its
  control; build candidate 3's curves and measure kappa; add the atlas row of
  finding (a) and resolve the duplicate of finding (b).

## 6. Web searches run (standard mode, 2026-10-31)

- "Pollard rho equivalence classes efficiently computable endomorphism small
  order prime field elliptic curve not automorphism speedup": Duursma-Gaudry-Morain
  (automorphisms of large order), negation-map literature (Bos-Kleinjung-Lenstra;
  Bernstein-Lange-Schwabe); nothing on non-automorphism small-order endomorphisms
  over prime fields.
- "generic group action model lower bound discrete logarithm ...": Duman et al.
  PKC 2023 (eprint 2023/186), Montgomery-Zhandry; group action alone, no combined
  model with a generic group carried by the curves.
- "Legendre symbol of the discrete logarithm hard-core predicate generic group
  model elliptic curve": Schnorr (generic one-wayness; Kaliski's EC bit results),
  Perera CRYPTO 2013 (DH bits); no result on the Legendre symbol of the log in
  the GGM.

Sources: https://rd.springer.com/content/pdf/10.1007/978-3-540-48000-6_10.pdf ,
https://eprint.iacr.org/2011/461 , https://eprint.iacr.org/2023/186 ,
https://www.cs.utexas.edu/~dwu4/papers/SGGM.pdf ,
https://publikationen.ub.uni-frankfurt.de/opus4/files/4278/schnorr.pdf ,
https://www.iacr.org/archive/crypto2013/80420315/80420315.pdf
