# TASK-20260905-a6ea8a -- producer report (novel point representations, RQ-ECDLP-623a32)

> Provenance note (Coordinator, 2026-09-05): the idea-generator subagent's `Write` of this file was
> refused twice by the runtime ("subagents should return findings as text"), so the producer returned
> the report in its final message and the Coordinator transcribed it here verbatim (HTML entities in
> the relayed text, such as `&gt;`, restored to the characters the producer wrote). Nothing was
> altered, added or removed by the Coordinator; `ideas.yaml` and `sources.json` were written by the
> producer directly. The producer's own words follow, beginning with the deliverable note it returned
> ahead of the report body.

## Deliverables (producer's note)

- Written: `coordination/ecdlp-ideas-20260905-23ec69/tasks/TASK-20260905-a6ea8a/ideas.yaml` (5 records) and `.../sources.json`.
- Not written (runtime refusal): `report.md` -- content below.

## Idea ids and one-line titles

1. `IDEA-20260905-d0fee4` (mechanism, priority high) — The Kummer line is Bezout-optimal among ALL coordinates E → P^1: average rational fibre size is (p+1−a_p)/(p+1) ≈ 1 for every degree n, and deg_t S_m^f ≥ n^{m−2}; predicts IDEA-20260808-2e14f7's HA-1 (|V| ≈ d·B) false; the y-coordinate is the universally available degree-3 non-Galois witness with predicted meter values (L,b) = (0.585, 2.25).
2. `IDEA-20260905-24b41a` (control, medium) — Elliptic nets, cubical/biextension lifts, Miller functions and dual-number lifts are one torsor object; Hom(Z/N, A) = A[N] = 0 for A = F_p^* (embedding degree > 1) and A = F_p (Schur–Zassenhaus) forces 0 bits; the twist-invariant net cross-ratio is a coordinate function; symbolic gates plus one measurement locating EV-NET-001's open asymmetry.
3. `IDEA-20260905-579fcc` (control, medium) — Multisets {x(P+sR): s ∈ S} are injective unless S is centrally symmetric, in which case they equal the translation-conjugate Kummer coordinate x_T (2T = −cR) with (L,b) = (1,2); scalar-orbit multisets cost |H| per step (KN-TECH-018 accounting); generic ceiling stated.
4. `IDEA-20260905-ab4a6e` (representation, low) — Quadratic-order box factor base (x(P) as a small u+vω residue mod a split prime): predicted reparametrisation of the interval base by norm-height bookkeeping, with the CM curve (unit action on box and curve) as the labelled positive control reproducing the known |Aut| gain.
5. `IDEA-20260905-0e0982` (representation, low) — The pair (P,Q) as one Mumford divisor on one of exactly two F_p-rational (2,2)-self-gluings of a prime-order curve (Frobenius acts on E[2] as a 3-cycle); dominated by KN-FIND-61347e (exponent 1); tests only that finding's open "factor-restricted" corner (line elements vs uniform elements in the degree-1 factor base), predicted null.

Identifiers `IDEA-20260905-1af7ac` and `-2d77c3` left unused. A sixth candidate (the un-eliminated |4(O)| / chained-Kummer presentation) was withdrawn after the corpus screen found it already measured (IDEA-20260830-cb8e46, IDEA-20260903-cf63ad, H-PFDR-9aadc0, KN-FIND-b0c3c9, EV-REP-001).

## Recommended first test

`IDEA-20260905-d0fee4` Stage 1: for p ∈ {2^12, 2^16, 2^20}, three prime-order curves each, count |F_W^f| for 10^3 random windows of sizes 32/128/512 in the coordinates x, y and r∘x (deg r = 2), with the PGL_2 battery, the translation-conjugate null x_R, a matched random curve, and the adaptive full-fibre window as the known-false object (ratio must be ≈ 3). It is the cheapest valid discriminator: a counting loop with no elimination or solver, two pre-registered opposite predictions from two corpus records (2e14f7: ≈ d; d0fee4: ≈ 1), and a known-false control proving the counter is not blind.

## Constraints not satisfied

- `report.md` could not be written (runtime refuses report-named files for subagents, twice). Content follows for Coordinator transcription.
- Five ideas rather than six (sixth withdrawn as a repackaging).
- Primary sources for Robert (eprint 2024/517 and its HAL mirror) and Gaudry–Thomé–Thériault–Diem (eprint 2004/153) were blocked from this container: cited as `recalled`. Stange arXiv 0710.1316 and Kohel arXiv 1005.3623 abstracts were fetched; bodies not read; the quasi-periodicity form used in 24b41a (T3) is `recalled` and gated at Stage 0.
- The Coordinator's mid-run request was addressed: the three sibling records were read from the scratchpad copies, listed in `sources.json`, and named with `provenance: internal` ("on open branch, not on main") in the novelty screens of d0fee4 (4dff7b), 24b41a (bf8898), ab4a6e (40aa90) and 0e0982 (40aa90).

## report.md (verbatim)

# TASK-20260905-a6ea8a — idea-generator deliverable (BATCH-23ec69, GOAL-ECDLP-001, RQ-ECDLP-623a32)

Declared artifact of the handoff (archived by TASK-20260905-8443e4). Proposal-only;
`maximum_runs: 0`; no experiment run, no ledger path written. `search_knowledge` was
NOT available; every screen is Grep/Read over `ledger/proposals`, `ledger/hypotheses`,
`knowledge/` plus the retrievals in `sources.json`. Five idea records filed in
`ideas.yaml` (`IDEA-20260905-d0fee4`, `-24b41a`, `-579fcc`, `-ab4a6e`, `-0e0982`);
`-1af7ac` and `-2d77c3` left unused. All `status: proposed`, `novelty_status: unverified`.

## 0. Established families declared off-limits as the primary lens

Degree-2 coordinates on the same curve (closed at lever 1 by IDEA-20260807-8027a2,
-e6d79e, -dadcd2); degree-d functions E -> P^1 in general (IDEA-20260808-2e14f7) unless
a specific d, class and consequence is named; X_1(N) torsor (IDEA-20260806-0c9de1);
split-quotient Igusa certificate (IDEA-20260808-fa1d80); CANL/XEDN lifts; pairing
transfer; ISO/ICINV transfer; CM-trace base (IDEA-20260902-701458). Also treated as
closed neighbours after reading: the chained Kummer presentation on the Groebner axis
(IDEA-20260830-cb8e46, IDEA-20260903-cf63ad, H-PFDR-9aadc0, KN-FIND-b0c3c9) and the
divisor/symmetric-coordinate presentation on the small-root axis (IDEA-20260904-e9675e;
IDEA-20260903-e0a3e8 by citation). Closure engine used, not lens: the rigidity theorems
IDEA-20260806-c5d183 / IDEA-20260807-df906f.

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
| 4 | x(P) as residue of small u+v*omega in O_K mod split prime (4) | Predicate, Type III; height-ratio tie with interval base | low-med | high | low / known (CM) | Filed as ab4a6e with CM positive control |
| 5a | Lagrangians at level N (5) | done by fa1d80 | - | - | - | Off-limits |
| 5b | Pair on split Kummer surface via (P,Q)->(P+Q,P-Q) (5) | Symmetric functions of {x(P+Q), x(P-Q)} = S_3 coefficients: the (Delta,Pi) case | low | high | none | Closed (coordinate change) |
| 5c | Pair as one Mumford divisor on a (2,2)-self-glued Jacobian (5) | Degree-4 isogeny, lossy+compatible, bijective on rational pairs: (L,b)=(0,1) | med | high | low | Filed as 0e0982; dominated by KN-FIND-61347e |
| 5d | Graph Gamma_k in NS(E x E): (1-k)f1+(k^2-k)f2+k*Delta, degree k^2+1 | Tautological; no propagation | low | none | none | Closed (own derivation, unverified) |
| 6 | Weil restriction Res E = E x E' (6) | Zero twist component; size-N^2 group | low | med | none | Closed by the same obstruction as 5c |
| 7a | Translation frames (x(P-R_i))_i (7) | Injective for r >= 2 | low | high | none | Closed (579fcc M1) |
| 7b | Torsion-translate sets over F_{p^k} (7) | dadcd2 (L3) | - | - | - | Already closed |
| 8a | Miller functions, ratio f_{N,Q}/f_{N,P}^k (8) | Torsor coordinate, trivial | low | high | none | Closed in 24b41a |
| 8b | Redundant divisor (A)+(B)-2(O) (8) | Fibre N; arity-2 decomposition | low | high | - | Closed (KN-FIND-007 yield exact) |
| 9a | Multiset {x(P+sR): s in S} (9) | Injective unless S centrally symmetric; then x_T, (1,2) | med | high | none | Filed as 579fcc (control) |
| 9b | Multiset over scalar orbit H (9) | Lossy log|H|, dilation-deterministic, cost |H| | low | high | low | Closed in 579fcc (M3) = KN-TECH-018 |
| 9c | Field-structured statistics of x(aP) over intervals (9) | Forced equidistribution up to Weil error | med | med | ? | OPEN corner; not filed |
| 10a | Universal fibre-size law + n^{m-2} bound (own) | Quantified clause-two failure | med-high | high | high | Filed as d0fee4 |
| 10b | y-coordinate as prime-order-available degree-3 witness (own) | Collinear triples; (0.585, 2.25) | med | high | med | Folded into d0fee4 |
| 10c | 2-descent map over F_p(E[2]) = F_{p^3} (own) | Odd-order group -> 2-group: trivial | low | high | none | Closed by Hom(Z/N,A)=A[N] |
| 10d | Hom-trichotomy for homomorphic representations (own) | - | - | - | - | Closure engine for 2, 3a, 3b, 8a, 10c |

## 2. Honest-accounting block (inventor-protocol section 5)

- Objects studied: the 25 rows above; five at idea level.
- Depth of verified structure: d0fee4 (C1) exact double count, (C2) three-line count
  on KN-FIND-a8990a's generic distinctness, meter values heuristic; 24b41a (T2)
  elementary group theory, (T3) depends on the quasi-periodicity form read only at
  snippet depth (Stage-0 gate, recalled); 579fcc (M1) short argument for generic P;
  ab4a6e (Q2) height bookkeeping against an unopened record (81a943, recalled);
  0e0982 (G1) S_3-centraliser count, (G2) Tate + N odd, (G3) is KN-FIND-61347e's.
  All derivation-tier at best, toy-tier for every proposed measurement, none reviewed.
- dominated_by: per record; session-wide `n/a (no result claimed)`. Rows checked for
  every record: parallel rho with DPs and negation (0.886 sqrt N, O(1) memory, 0
  queries), automorphism-discounted rho, BSGS, kangaroo, Pohlig-Hellman, generic
  preprocessing S T^2 = N, PKM/Semaev prime-field decomposition (KN-LIT-025,
  KN-FIND-f8c290, BKK constants). None approached; 0e0982 dominated by rho by N^{1/2}.
- sota_delta: 0.000 bits on every attack exponent. Non-cost deltas: 2e14f7 HA-1
  predicted false (|V| ~ B for every d, not d*B); lever-1 closure extended from five
  degree-2 models to all coordinate functions; brief classes (2),(3),(6),(7),(8) and
  parts of (1),(5),(9) closed by mechanism; two new meter calibrators (0,1),(1,2)
  and two predicted meter points (y, r o x).

## 3. Enumerated closures with mechanism (section 4 standard)

1. Degree-d coordinates: average rational fibre size (p+1-a_p)/(p+1) ~ 1 for every f;
   deg_t S_m^f >= n^{m-2}; Bezout >= n^{m-2} B^{m-1}, minimum at n = 2 (d0fee4).
   Open: adaptive full-fibre windows at a membership-predicate cost; non-window bases.
2. Torsor-type representations (nets, cubical, Miller, dual numbers, 2-descent):
   homomorphism G -> A with Hom(Z/N, A) = A[N] = 0 for N not dividing |A| (24b41a).
   Open: non-homomorphic torsor statistics (24b41a Stage 4), higher jets.
3. Shift multisets / frames: labelling rigidity; only the Kummer bit is discardable;
   (L,b) in {(0,1),(1,2)} (579fcc). Open: field-structured multiset statistics (9c).
4. Scalar-orbit multisets: |H| per step vs sqrt|H| space (579fcc M3 = KN-TECH-018).
5. Pair objects (E x E, Weil restriction, glued Jacobians): embedded in a size-N^2
   group where index calculus costs N^{2-2/g} = N at g = 2 (KN-FIND-61347e); Kummer-
   surface reading is lossless; Gamma_k has NS-degree k^2+1. Open: factor-restricted
   index calculus, probed by 0e0982.
6. Quadratic-order box (generic curves): predicted tie (Q2), a prediction not a closure.

## 4. Open directions for the next session

Adaptive full-fibre windows costed on KN-OPEN-020's membership axis; 24b41a Stage 4
to locate EV-NET-001's 0.52-0.70x asymmetry; a test for class 9c whose signal would
be the Weil error term; factor-restricted index calculus on glued Jacobians; writing
the Hom-trichotomy (10d) into KN-OPEN-019's enumeration.

## 5. Ranking (expected information gain vs cost)

1. d0fee4 (high): zero-compute derivation + minutes of counting; decides a live
   corpus heuristic; closes a class by argument.
2. 24b41a (medium): symbolic gates; closes three classes; one measurement resolves an
   open EV-NET-001 confound.
3. 579fcc (medium): theorem + two meter calibrators; minutes.
4. ab4a6e (low): predicted null with known positive control; hours of Sage.
5. 0e0982 (low): high implementation cost, predicted null, already dominated by
   N^{1/2}; cheapest test of KN-FIND-61347e's open direction.

## 6. Recommended first test

d0fee4 Stage 1: for p in {2^12, 2^16, 2^20}, three prime-order curves each, count
|F_W^f| for 10^3 random windows of sizes 32/128/512 in x, y and r o x (deg r = 2),
with the PGL_2 battery, the translation-conjugate null x_R, a matched random curve,
and the adaptive-window known-false object (ratio must be about 3). Cheapest valid
discriminator: a counting loop with no elimination, solver or tuning; two outcomes
pre-registered with opposite predictions from two corpus records (2e14f7: ~d; this
record: ~1); the known-false control proves the counter can see a fibre gain.

## 7. Constraints not fully satisfied

- Five ideas, not six: the sixth candidate (un-eliminated / chained presentation) was
  a repackaging of corpus records and was withdrawn.
- Robert (eprint 2024/517, HAL) and GTTD (eprint 2004/153) blocked: `recalled`.
  Stange and Kohel arXiv abstracts fetched, bodies not read; the quasi-periodicity
  form in 24b41a (T3) is `recalled` and gated at Stage 0.
- Sibling records IDEA-20260905-40aa90/-4dff7b/-bf8898 read from Coordinator-supplied
  scratchpad copies (open branches, not on main); named in the relevant novelty
  screens with `provenance: internal`.

Sources used for the external checks: Kohel, arXiv:1005.3623 (abstract); Stange, arXiv:0710.1316 (abstract); Robert, eprint 2024/517 (blocked; snippet only); GTTD, eprint 2004/153 (blocked; snippet only).
