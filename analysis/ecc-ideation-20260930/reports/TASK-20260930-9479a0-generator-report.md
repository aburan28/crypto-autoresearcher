# TASK-20260930-9479a0 — generator report, lane L5 (REPR)

Idea Generator, 2026-10-01. Branch `claude/elliptic-curve-goals-3bfz9x`, base
`5cd61253a`. Proposals only; nothing approved, no status changed, no run.

## Identifiers

| id | disposition | question |
| --- | --- | --- |
| IDEA-20260930-8e3b75 | FILED | RQ-ECDLP-c1b7b1 |
| IDEA-20260930-a6491b | FILED | RQ-ECDLP-4fcbd3 |
| IDEA-20260930-9620c8 | RETURNED UNUSED | — |

Why the third was not filed. Two candidates were drafted for it and both
failed the overlap review honestly:

1. *The small-lift information budget* (RQ-ECDLP-623a32, R1): every
   factor-base presentation of x by small integers (box, rational a/b,
   quadratic-order u + v omega, degree-k order boxes, bounded digits) spends
   at least log|F| unknown bits per point against one equation mod p per
   relation, so the lattice-oracle reach and the end-to-end p^{1/2} ceiling
   are representation-invariant. Found to be the union of statements already
   on the ledger: the eps > m/(2(m-1)) criterion of IDEA-20260808-486ae2, the
   volume-preservation / demand-neutrality lemma of IDEA-20260904-8dccc9, and
   the ratio tie (Q2) of IDEA-20260905-ab4a6e. Delta would have been
   "adaptation" with no new number; dropped.
2. *The equicharacteristic anomalous attack as a standalone mechanism*
   (dual-number [p]-map is a nonzero homomorphism iff a_p = 1): a web search
   surfaced Belding, arXiv math/0703906 (2007) and her 2008 UMD thesis, whose
   abstracts state exactly "an attack on the discrete logarithm problem on
   anomalous curves, analogous to that of Smart, using a lift of E over the
   dual numbers". Known; folded into IDEA-20260930-8e3b75 as its retrieved
   positive control (C3) instead of filed.

A 623a32-native third candidate with real content was not found this
session: every R2 model with a torsion-based symmetry is unavailable on a
cofactor-1 curve, R3 (nets, cubical, torsor, E x E gluing, Weil restriction,
local rings, level-N) is filed, and the remaining R1 ideas collapsed to the
budget argument above.

## Returned once (2026-10-01)

Dispatcher acceptance check: `prior_art.nearest[].ref` must resolve to a
KR-* row or a KN-* entry under knowledge/; IDEA-*, H-*, repository paths and
arXiv strings are rejected there. What moved, per record (no claim,
mechanism, prediction, threshold, cost or novelty_status changed):

- IDEA-20260930-8e3b75: removed from `nearest` the refs IDEA-20260905-3e9133,
  H-ECDLP-a3598b, ideas/rejected/ECDLP-IDEA-109_..., IDEA-20260905-3a30d5 and
  the Belding arXiv string; all five were already in `citations` (internal /
  retrieved, with verification notes) and in `discriminated_from`, where the
  deltas now sit. New `nearest`: KR-RHO-53c89f (special_case),
  KN-OPEN-3417fc (adjacent), KN-TECH-06bb4e (adjacent), KN-TECH-73630e
  (adjacent), KR-IC-cd159a (adjacent); KN-TECH-73630e also added to
  `citations`. `novelty_status: adaptation` stands on the internal records
  in `citations`.
- IDEA-20260930-a6491b: removed from `nearest` IDEA-20260905-b6154d and
  IDEA-20260905-9c4f0c (both remain in `citations` and
  `discriminated_from`). New `nearest`: KR-RHO-13bf67, KR-RHO-898783,
  KN-FIND-ffe1df, KN-TECH-005, KR-RHO-53c89f (all adjacent); KN-TECH-005 also
  added to `citations`.
- Every KN-* id used was verified to exist by Glob (knowledge/findings,
  literature, open-problems, techniques) before writing; `rows_checked`
  unchanged, KR-* only.

## One-line summaries

- **IDEA-20260930-8e3b75** — class `representation`, filed under
  RQ-ECDLP-c1b7b1. Claim: the unique n-torsion lift of a point into a
  NON-constant first-order deformation E_eps/F_p[eps] (Kodaira–Spencer
  direction) has a canonical O(log n) defect digit delta_KS relative to the
  coordinate-defined reference section; delta_KS is provably not a rational
  function of degree below p/C, equals lambda x/y on the trivial direction
  (exact), is predicted equal to the lift-derivative of the p-adic torsion
  digit of IDEA-20260905-3a30d5, and reduces to Belding's dual-number
  anomalous attack at n = p; its DL-spectrum on generic prime-order curves is
  predicted white and is measured on the existing census instrument.
  Trichotomy: Class III (coordinate-dependent). `novelty_status: adaptation`
  (object exists as IDEA-20260905-3e9133 / H-ECDLP-a3598b; anomalous arm is
  Belding 2007, abstract retrieved). Cost: implementation low, compute low
  (CPU-hours).
- **IDEA-20260930-a6491b** — class `mechanism`, filed under RQ-ECDLP-4fcbd3.
  Claim: for any subset S cut out by a bounded-degree coordinate condition
  and any bounded-degree predictor, the restricted advantage is at most
  c D L^2 sqrt(p)/|S| (b6154d's Weil-level bound on 1_S·g) while each sample
  costs N/|S| re-randomisations and eps^{-2} samples are needed by
  information, so the product is at least sqrt(N)/polylog uniformly in |S|,
  the two regimes meeting at |S| = sqrt(N); the RQ's "structured subset of
  points" escape is therefore open only to high-degree subsets (itineraries,
  bit families, and the digit family of 8e3b75, put on the ladder first).
  Trichotomy: Class III. `novelty_status: unverified`. Cost: implementation
  low, compute low.

## Recommended first test

IDEA-20260930-8e3b75, Stage 0 + Stage 1: the derivation note and the four
zero-tolerance gates — (C1) delta_triv(P) = lambda x_P/y_P on every point of
three toy curves; the homomorphism s(P+Q) = s(P)+s(Q) on all pairs at 12 bits;
(C3) scalar recovery with certificate on 50 anomalous toy curves; (C2) the
lift-derivative identity against a Z/p^2 torsion section if the lane's p-adic
instrument exists. These are exact identities with no noise, they cost
minutes, and they decide whether the instrument may read a spectrum at all.
Only after they pass does Stage 2 (the census at 2^16–2^24) run; either
outcome there is a deliverable (a measured obstruction closing an unnamed
lifting cell at toy tier, or the first computational handle in a
local-torsion cell).

## Records read for overlap

Handoff card; BRIEF.md §§0, 3, 4, 5; docs/object-frame-ideation.md in full;
IDEA-20260806-c5d183, IDEA-20260901-863e36, IDEA-20260802-002 in full;
KN-FIND-ffe1df, KN-OPEN-003, -019, -020, -3417fc, KN-TECH-06bb4e in full;
context/L5-REPR.md (five questions verbatim, two goal heads, 77 hypothesis and
54 proposal lines); both frontier maps (48 rows); agents/idea-generator.md;
docs/inventor-protocol.md; docs/target-result-profile.md;
templates/research-records.md ("Prior art on ideas", "Citation provenance");
docs/ecdlp-literature-review-20260926.md and
docs/recent-cryptanalysis-literature-20260926.md; exemplar
IDEA-20260926-89886c in full.

Lane proposals read in claim/mechanism (or further): IDEA-20260905-b6154d
(through its limits), -f31bc4, -848b77, -3a30d5, -9c4f0c, -5a1ea2, -24b41a,
-579fcc, -ab4a6e, -3e9133 (full), IDEA-20260906-aa6da3, -476f20, -e07475 (full),
IDEA-20260904-8dccc9, IDEA-20260808-486ae2, -e2315e. Hypotheses:
H-ECDLP-a3598b (full); statements of H-ECDLP-09125b, -6a9479, -c48f2a,
-f1e714, -0bc396, -3ca750, -5b245d, H-PFDR-621852 by grep; H-ECDLP-4afa77 and
-2ac931 (unrelated, confirmed by title). Evidence: verdict/strength fields of
EV-ECDLP-8ef054, -b909d7, -b91d4a, -6a0e86 (all neutral/inconclusive/toy on
EXP-ECDLP-a5f766). Rejected: ideas/rejected/ECDLP-IDEA-109 (first 120 lines).
Artifacts: grep context in ideas/artifacts/ECDLP-IDEA-436/ggm_simulability_gate.md
and analysis/xedni-prescribed-points/20260905-7d477a/README.md.

## Searches run

Corpus (Grep; kb index empty this session):
- `Kodaira|Kodaira-Spencer|deformation direction|vectorial extension|equicharacteristic|F_p[[t]]|F_p[t]/t|first-order deformation|universal deformation` (repo-wide)
- `dual number|dual-number|F_p[eps|K[eps|deformation|Kodaira|Belding|hitting cost|restricted advantage|rejection sampling|subset S of|thin subset` (ledger/hypotheses)
- `3e9133|a3598b|deformation jet` (ledger; knowledge) — repo-wide form timed out, narrowed
- `Coppersmith|rational reconstruction|half-gcd` (ledger/proposals, 47 files; none on the budget invariance)
- `Tate normal form|X_1(|modular curve|diamond operator|Hecke` (ledger)
- `projective coordinates|Z-coordinate|Jacobian coordinates|inversion-free|redundant representation` (ledger/proposals; six files, titles checked, none a Z-history object)
- `hitting cost|thin set|thin subset|restricted advantage|subset of points|rerandomi[sz]e until` (ledger/proposals: no match)
- Glob `knowledge/**/KN-{...}.md` for every KN-* id used in `prior_art.nearest` and `citations` (all resolve)

Web (WebSearch / WebFetch):
- `anomalous elliptic curve discrete logarithm attack "dual numbers" OR "universal vectorial extension" OR "Hasse invariant" OR "Cartier operator" trace one`
- `elliptic curve discrete logarithm "deformation" "F_p[t]" OR "F_p[epsilon]" OR "first-order deformation" torsion section Kodaira-Spencer attack`
- Fetched: arXiv abstract page math/0703906 (read); UMD thesis landing page (read). Blocked: the arXiv PDF (not renderable here, pdftoppm missing); bohrium mirror (HTTP 404). No source body was read; provenance is `retrieved` at abstract level only.

## Honest accounting (docs/inventor-protocol.md §5)

- **Objects considered.** (i) The deformation defect digit delta_KS of the
  equicharacteristic torsion lift (filed). (ii) The subset-restricted
  DL-correlation pair (membership, restricted spectrum) with the hitting
  cost (filed). (iii) The small-lift information budget across R1
  presentations (covered; dropped). (iv) The dual-number anomalous
  homomorphism Sigma (known, Belding; used as control). (v) Rejected on the
  lossy-projection test or by existing records during search: Tate-normal-form
  coordinates (bounded-degree change of coordinates, Kummer-equivalent);
  ell-division-fibre Frobenius type (constant on G); isogeny-descent classes
  (trivial for n coprime to ell); projective Z-history (24b41a's Miller
  torsor); multiplicative characters of any order (b6154d class (ii));
  coordinate-independent iterates x∘[k], x∘tau_T, x∘phi (spectrum
  permutations, folded into a6491b); extension-field and global-lift
  representations (KR-RHO-5b1c0a, 848b77).
- **dominated_by.** Both filed records: `n/a (no result claimed)`, set after
  checking every row of both rendered maps (listed in each record). The
  dropped budget candidate would have been dominated by IDEA-20260808-486ae2
  and IDEA-20260904-8dccc9 as structural statements.
- **sota_delta.** Zero on time, memory and data/queries for both records.
  Methodological deltas: a canonical cheap digit in a lifting cell the
  taxonomy does not name, with three exact calibrations and a degree bound
  (8e3b75); a uniform floor sqrt(N)/polylog for the subset-restricted
  coordinate-bias route with the meeting point at |S| = sqrt(N) (a6491b).
- **Enumerated closures with mechanisms.** (1) Bounded-degree subsets cannot
  concentrate DL-bias usefully: mechanism = Weil-level restricted bound
  times rejection-hitting cost, minimised at sigma = polylog/sqrt(N)
  (conditional on b6154d's recalled bound; a6491b). (2) Coordinate-independent
  iterates of bounded-degree functions are at the ceiling: mechanism =
  spectrum equivariance (a6491b, zero compute). (3) No scalar-covariant
  deformation jet exists for n ≠ p: mechanism = Hom(Z/n, F_p) = 0 (restated
  from 24b41a / IDEA-109; 8e3b75 accepts it and measures the non-covariant
  defect). (4) The R1 small-lift budget is representation-invariant: already
  closed by 486ae2 / 8dccc9 / ab4a6e; not re-filed.
- **Open directions for the next session.** (a) Read Belding's body: if it
  states the Hasse-invariant criterion, (C3)'s obligation becomes a citation;
  if her lift is the constant family, the non-constant construction of 8e3b75
  needs its own derivation of non-degeneracy. (b) Higher-precision digits
  delta_k over F_p[t]/t^(k+1) and mixed rings W_2(F_p)[eps] as further census
  members, only after 8e3b75's Stage 1 passes. (c) The high-degree subset
  families a6491b leaves open: itinerary classes (9c4f0c), bit families
  (KN-FIND-ffe1df I, J), digit-defined sets; a hitting-cost analysis for
  high-degree subsets would complete the subset door. (d) For RQ-ECDLP-623a32
  proper, the unfilled slot: an R2/R3 representation on a cofactor-1 curve
  that changes a degree of a named stage; this session found none outside
  the filed families, which is a statement about the search
  (`novelty_status: unverified` for that closure), not about the problem.

## Files written

- ledger/proposals/IDEA-20260930-8e3b75.yaml
- ledger/proposals/IDEA-20260930-a6491b.yaml
- analysis/ecc-ideation-20260930/reports/TASK-20260930-9479a0-generator-report.md

No existing file was edited; IDEA-20260930-9620c8 was not written.
