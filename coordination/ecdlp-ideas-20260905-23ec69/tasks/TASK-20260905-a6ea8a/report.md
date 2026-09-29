# TASK-20260905-a6ea8a -- producer report (novel point representations, RQ-ECDLP-623a32)

> Provenance note (Coordinator, 2026-09-05): the idea-generator subagent's `Write` of this file was
> refused by the runtime (the producer reports two refusals) ("subagents should return findings as text"), so the producer returned
> the report in its final message and the Coordinator transcribed it here verbatim (HTML entities in
> the relayed text, such as `&gt;`, restored to the characters the producer wrote). Nothing was
> altered, added or removed by the Coordinator; `ideas.yaml` and `sources.json` were written by the
> producer directly. The producer's own words follow, beginning with the deliverable note it returned
> ahead of the report body.

## Deliverables (producer's note)

- Written: `coordination/ecdlp-ideas-20260905-23ec69/tasks/TASK-20260905-a6ea8a/ideas.yaml` (5 records, rewritten to carry the object-frame amendments (a)-(g) and the YAML quoting fix at the old line 677) and `.../sources.json` (now including docs/object-frame-ideation.md, KN-TECH-ee6696, KN-FIND-ffe1df, IDEA-20260806-c5d183, IDEA-20260807-df906f, IDEA-20260815-f558e4, IDEA-20260901-863e36, H-TLD-f4c8ba).
- Not written: `report.md` -- refused by the runtime as a "report file". Content is in the last section below.

## Object-frame compliance (per record)

| id | representation | Sigma | class | priced number |
|---|---|---|---|---|
| d0fee4 | R2: value of a degree-n coordinate f(P), relation vector over the window base | translation by factor-base elements (m-fold relation) | I partial-action; branching bound n^{m-2} | (L,b) for x, y, r∘x with identity / random-label / relabelled Z/nZ / PGL_2 controls |
| 24b41a | R3: torsor point (net / cubical / Miller / dual-number lift) | group law lifted to the torsor (full translation, declared: not branching -- forced constant) | III coordinate-dependent | (L,b) = (log2 N, 1) for the torsor coordinate, (1,2) for the residue, with all controls |
| 579fcc | R1: unlabelled multiset of x over a shift set / scalar orbit | affine involution P ↦ -P-cR (block system); multiplication by H | I partial-action (or injective, no class) | (L,b) ∈ {(0,1),(1,2)}; c_can = |H| per orbit |
| ab4a6e | R1: x(P) reduced in O_K/(π), box predicate | translation by F_box; on CM curves also the unit group Γ ≤ Aut(E) | I partial-action | c_can = O(1) on CM (morphism-induced); predicate (L,b) with b = 2 (no propagation) |
| 0e0982 | R3: Mumford divisor Φ(P,Q) on a (2,2)-self-glued Jacobian | translation by degree-1 base divisors on J | I partial-action; Φ's kernel coset is a block system on E×E (geometric), bijective on rational pairs | (L,b) = (0,1) rational / (2,1) geometric; line-vs-uniform yield |

Each record's `assumptions` names the F1-F7 component used (F2; F4/F5 boundaries; F1/F6; F2/F6; F2/F3), `interpretation_limits` gives the KN-OPEN-020 class with charged costs or "no factor base proposed", and `claim` opens with the R-class and attack-stage clause.

## Idea ids and titles

1. `IDEA-20260905-d0fee4` -- Kummer line Bezout-optimal among all coordinates E → P^1 (average rational fibre size 1; deg ≥ n^{m-2}); refutes 2e14f7 HA-1; y-coordinate witness. Priority high.
2. `IDEA-20260905-24b41a` -- Nets / cubical / Miller / dual-number lifts are one torsor; Hom(Z/N, A) = A[N] = 0 forces 0 bits; residue is a coordinate. Control, medium.
3. `IDEA-20260905-579fcc` -- Shift multisets are injective or the shifted Kummer coordinate; scalar-orbit multisets cost |H|. Control, medium.
4. `IDEA-20260905-ab4a6e` -- Quadratic-order box factor base; predicted interval-base reparametrisation; CM curve positive control. Representation, low.
5. `IDEA-20260905-0e0982` -- Pair as one Mumford divisor on one of exactly two rational (2,2)-self-gluings; tests KN-FIND-61347e's open corner. Representation, low.

Unused: `IDEA-20260905-1af7ac`, `-2d77c3`.

## Recommended first test

`d0fee4` Stage 1 (window counts for x, y, r∘x at p ∈ {2^12, 2^16, 2^20} with the adaptive-window known-false object, PGL_2 battery, translation null, matched random curve, and the identity / random-label / relabelled-Z/nZ meter controls) -- a counting loop with two pre-registered opposite predictions from two corpus records and a control that proves the counter is not blind.

## Constraints not satisfied

- `report.md` not writable by this runtime (content below).
- Five ideas, not six (sixth withdrawn as a repackaging of cb8e46 / cf63ad / H-PFDR-9aadc0 / KN-FIND-b0c3c9 / EV-REP-001).
- Robert eprint 2024/517 (and HAL), GTTD eprint 2004/153 blocked → `recalled`; Stange/Kohel abstracts only → the quasi-periodicity form in 24b41a (T3) is `recalled`, gated at Stage 0.
- The YAML was scanned by regex, not parsed by an interpreter (no Bash); the three hazard classes the Coordinator named return no hits outside block scalars.

## report.md (verbatim)

# TASK-20260905-a6ea8a -- idea-generator deliverable (BATCH-23ec69, GOAL-ECDLP-001, RQ-ECDLP-623a32)

Declared artifact of the handoff (archived by TASK-20260905-8443e4). Proposal-only;
`maximum_runs: 0`; no experiment run, no ledger path written. `search_knowledge` was
NOT available; every screen is Grep/Read over `ledger/proposals`, `ledger/hypotheses`,
`knowledge/` plus the retrievals in `sources.json`. Five idea records filed in
`ideas.yaml` (`IDEA-20260905-d0fee4`, `-24b41a`, `-579fcc`, `-ab4a6e`, `-0e0982`);
`-1af7ac` and `-2d77c3` left unused. All `status: proposed`, `novelty_status: unverified`.
Every record carries the object-frame declarations of docs/object-frame-ideation.md
(representation, operation set Sigma, trichotomy class, discard and its
Sigma-compatibility, priced open number, off-limits component, KN-OPEN-020 class,
R1/R2/R3 class and attack stage) in the fixed schema fields.

## 0. Established families declared off-limits as the primary lens

Degree-2 coordinates on the same curve (closed at lever 1 by IDEA-20260807-8027a2,
-e6d79e, -dadcd2); degree-d functions E -> P^1 in general (IDEA-20260808-2e14f7) unless
a specific d, class and consequence is named; X_1(N) torsor (IDEA-20260806-0c9de1);
split-quotient Igusa certificate (IDEA-20260808-fa1d80); CANL/XEDN lifts; pairing
transfer; ISO/ICINV transfer; CM-trace base (IDEA-20260902-701458); families F1-F7 of
IDEA-20260802-002 as enumerated in KN-TECH-ee6696. Also treated as closed neighbours
after reading: the chained Kummer presentation on the Groebner axis (IDEA-20260830-cb8e46,
IDEA-20260903-cf63ad, H-PFDR-9aadc0, KN-FIND-b0c3c9) and the divisor/symmetric-coordinate
presentation on the small-root axis (IDEA-20260904-e9675e; IDEA-20260903-e0a3e8 by
citation). Closure engine used, not lens: IDEA-20260806-c5d183, IDEA-20260807-df906f,
KN-FIND-ffe1df Theorem C, IDEA-20260901-863e36.

## 1. Candidate objects enumerated, three-axis scores

N = genuinely new vs repackaging; T = testable one-step propagation; S = survival.

| # | Object (brief class) | Lossy-projection test | N | T | S | Disposition |
|---|---|---|---|---|---|---|
| 1 | Level-n embedding E in P^{n-1}, un-eliminated system keeping full points (1) | Injective; keeping y un-quotients the sign (EV-REP-001 d_reg 4->12; 8027a2 D1) | low | high | low | Repackaging of EV-REP-001 and sibling IDEA-20260905-bf8898; NOT filed |
| 1b | Chained Kummer presentation S_3(x1,x2,u), S_3(u,x3,xR), Groebner axis (1) | Lossy 1 bit, branching 2 | low | high | med | Already in corpus (cb8e46, cf63ad, H-PFDR-9aadc0, KN-FIND-b0c3c9); NOT filed |
| 1c | Factor base cut by a pencil of hyperplane sections in n(O) = degree-n coordinate (1) | Branching >= n^{m-2} | med | high | med | Folded into d0fee4 |
| 1d | Factor base cut by a net of hyperplanes (1) | Essentially all of E | low | - | - | Degenerate; closed |
| 2 | Elliptic net W_{P,Q}(a,b) with zero lattice L (2) | Coordinate function plus torsor coordinate; torsor forced trivial | med | high | low | Filed as 24b41a (control); EV-NET-001 prior |
| 3a | Dual-number lift E(F_p[eps]) (3) | Canonical splitting (Schur-Zassenhaus): tangent component 0 | low | high | none | Closed in 24b41a (T2); consistent with EV-JETB-001 |
| 3b | Cubical/biextension torsor (3) | Tate self-pairing class, trivial when N does not divide p-1 | med | high | none | Closed in 24b41a |
| 4 | x(P) as residue of small u+v*omega in O_K mod split prime (4) | Predicate, Class I through the relation vector; height-ratio tie with interval base | low-med | high | low / known (CM) | Filed as ab4a6e with CM positive control |
| 5a | Lagrangians at level N (5) | done by fa1d80 | - | - | - | Off-limits |
| 5b | Pair on split Kummer surface via (P,Q)->(P+Q,P-Q) (5) | Symmetric functions of {x(P+Q), x(P-Q)} = S_3 coefficients: the (Delta,Pi) case | low | high | none | Closed (coordinate change) |
| 5c | Pair as one Mumford divisor on a (2,2)-self-glued Jacobian (5) | Degree-4 isogeny, lossy+compatible geometrically, bijective on rational pairs: (L,b)=(0,1) | med | high | low | Filed as 0e0982; dominated by KN-FIND-61347e |
| 5d | Graph Gamma_k in NS(E x E): (1-k)f1+(k^2-k)f2+k*Delta, degree k^2+1 | Tautological; no propagation | low | none | none | Closed (own derivation, unverified) |
| 6 | Weil restriction Res E = E x E' (6) | Zero twist component; size-N^2 group | low | med | none | Closed by the same obstruction as 5c |
| 7a | Translation frames (x(P-R_i))_i (7) | Injective for r >= 2 | low | high | none | Closed (579fcc M1) |
| 7b | Torsion-translate sets over F_{p^k} (7) | dadcd2 (L3) | - | - | - | Already closed |
| 8a | Miller functions, ratio f_{N,Q}/f_{N,P}^k (8) | Torsor coordinate, trivial | low | high | none | Closed in 24b41a |
| 8b | Redundant divisor (A)+(B)-2(O) (8) | Fibre N; arity-2 decomposition | low | high | - | Closed (KN-FIND-007 yield exact) |
| 9a | Multiset {x(P+sR): s in S} (9) | Injective unless S centrally symmetric; then x_T, (1,2) | med | high | none | Filed as 579fcc (control) |
| 9b | Multiset over scalar orbit H (9) | Lossy log|H|, dilation-deterministic, c_can = |H| | low | high | low | Closed in 579fcc (M3) = KN-TECH-018 / 863e36 (C4) |
| 9c | Field-structured statistics of x(aP) over intervals (9) | Forced equidistribution up to Weil error | med | med | ? | OPEN corner; not filed |
| 10a | Universal fibre-size law + n^{m-2} bound (own) | Quantified clause-two failure (branching bound) | med-high | high | high | Filed as d0fee4 |
| 10b | y-coordinate as prime-order-available degree-3 witness (own) | Collinear triples; (0.585, 2.25) | med | high | med | Folded into d0fee4 |
| 10c | 2-descent map over F_p(E[2]) = F_{p^3} (own) | Odd-order group -> 2-group: trivial | low | high | none | Closed by Hom(Z/N,A)=A[N] |
| 10d | Hom-trichotomy for homomorphic representations (own) | - | - | - | - | Closure engine for 2, 3a, 3b, 8a, 10c; KN-FIND-ffe1df Theorem C is its validator-confirmed form |

## 2. Honest-accounting block (inventor-protocol section 5)

- Objects studied: the 25 rows above; five at idea level.
- Depth of verified structure: d0fee4 (C1) exact double count, (C2) three-line count
  on KN-FIND-a8990a's generic distinctness, meter values heuristic; 24b41a (T2)
  elementary group theory (the coprime-order case of KN-FIND-ffe1df Theorem C), (T3)
  depends on the quasi-periodicity form read only at snippet depth (Stage-0 gate,
  recalled); 579fcc (M1) short argument for generic P, (M3) is 863e36 (C4)-(C5)
  applied; ab4a6e (Q2) height bookkeeping against an unopened record (81a943,
  recalled); 0e0982 (G1) S_3-centraliser count, (G2) Tate + N odd, (G3) is
  KN-FIND-61347e's. All derivation-tier at best, toy-tier for every proposed
  measurement, none reviewed.
- dominated_by: per record; session-wide `n/a (no result claimed)`. Rows checked for
  every record: parallel rho with DPs and negation (0.886 sqrt N, O(1) memory, 0
  queries), automorphism-discounted rho, BSGS, kangaroo, Pohlig-Hellman, generic
  preprocessing S T^2 = N, PKM/Semaev prime-field decomposition (KN-LIT-025,
  KN-FIND-f8c290, BKK constants). None approached; 0e0982 dominated by rho by N^{1/2}.
- sota_delta: 0.000 bits on every attack exponent. Non-cost deltas: 2e14f7 HA-1
  predicted false (|V| ~ B for every d, not d*B); lever-1 closure extended from five
  degree-2 models to all coordinate functions; brief classes (2),(3),(6),(7),(8) and
  parts of (1),(5),(9) closed by mechanism; two new meter calibrators (0,1),(1,2)
  and two predicted meter points (y, r o x); every record placed in the trichotomy
  with its Sigma and priced open number.

## 3. Enumerated closures with mechanism (section 4 standard)

1. Degree-d coordinates: average rational fibre size (p+1-a_p)/(p+1) ~ 1 for every f;
   deg_t S_m^f >= n^{m-2}; Bezout >= n^{m-2} B^{m-1}, minimum at n = 2 (d0fee4).
   Open: adaptive full-fibre windows at a membership-predicate cost; non-window bases.
2. Torsor-type representations (nets, cubical, Miller, dual numbers, 2-descent):
   homomorphism G -> A with Hom(Z/N, A) = A[N] = 0 for N not dividing |A| (24b41a).
   Open: non-homomorphic torsor statistics (24b41a Stage 4), higher jets.
3. Shift multisets / frames: labelling rigidity; only the Kummer bit is discardable;
   (L,b) in {(0,1),(1,2)} (579fcc). Open: field-structured multiset statistics (9c).
4. Scalar-orbit multisets: c_can = |H| per step vs sqrt|H| space (579fcc M3 =
   KN-TECH-018, 863e36 (C4)).
5. Pair objects (E x E, Weil restriction, glued Jacobians): embedded in a size-N^2
   group where index calculus costs N^{2-2/g} = N at g = 2 (KN-FIND-61347e); Kummer-
   surface reading is lossless; Gamma_k has NS-degree k^2+1. Open: factor-restricted
   index calculus, probed by 0e0982.
6. Quadratic-order box (generic curves): predicted tie (Q2), a prediction not a closure.

## 4. Open directions for the next session

Adaptive full-fibre windows costed on KN-OPEN-020's membership axis; 24b41a Stage 4
to locate EV-NET-001's 0.52-0.70x asymmetry; a test for class 9c whose signal would
be the Weil error term; factor-restricted index calculus on glued Jacobians; F6
arithmetic selectors (863e36 (C6)) as the one Sigma = multiplication cell this
session did not populate; writing the Hom-trichotomy (10d) into KN-OPEN-019's
enumeration beside KN-FIND-ffe1df Theorem C.

## 5. Ranking (expected information gain vs cost)

1. d0fee4 (high): zero-compute derivation + minutes of counting; decides a live
   corpus heuristic; closes a class by argument.
2. 24b41a (medium): symbolic gates; closes three classes; one measurement resolves an
   open EV-NET-001 confound.
3. 579fcc (medium): theorem + two meter calibrators + one c_can measurement; minutes.
4. ab4a6e (low): predicted null with known positive control; hours of Sage.
5. 0e0982 (low): high implementation cost, predicted null, already dominated by
   N^{1/2}; cheapest test of KN-FIND-61347e's open direction.

## 6. Recommended first test

d0fee4 Stage 1: for p in {2^12, 2^16, 2^20}, three prime-order curves each, count
|F_W^f| for 10^3 random windows of sizes 32/128/512 in x, y and r o x (deg r = 2),
with the PGL_2 battery, the translation-conjugate null x_R, a matched random curve,
the identity / random-label / relabelled-Z/nZ meter controls, and the adaptive-window
known-false object (ratio must be about 3). Cheapest valid discriminator: a counting
loop with no elimination, solver or tuning; two outcomes pre-registered with opposite
predictions from two corpus records (2e14f7: ~d; this record: ~1); the known-false
control proves the counter can see a fibre gain.

## 7. Constraints not fully satisfied

- Five ideas, not six: the sixth candidate (un-eliminated / chained presentation) was
  a repackaging of corpus records and was withdrawn.
- Robert (eprint 2024/517, HAL) and GTTD (eprint 2004/153) blocked: `recalled`.
  Stange and Kohel arXiv abstracts fetched, bodies not read; the quasi-periodicity
  form in 24b41a (T3) is `recalled` and gated at Stage 0.
- Sibling records IDEA-20260905-40aa90/-4dff7b/-bf8898 read from Coordinator-supplied
  scratchpad copies (open branches, not on main); named in the relevant novelty
  screens with `provenance: internal`.
- ideas.yaml was checked for the three YAML hazard classes by regex scan, not by an
  interpreter (no Bash in this session).
