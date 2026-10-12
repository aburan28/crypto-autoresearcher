# Generator report, lane L6 CONSTRAINT (TASK-20260930-a1877b)

Date: 2026-10-01. Idea generator, policy `research-deep` (served by the
session model; `fallback_reason_if_used` per the handoff). Repository at
`5cd61253a` on `claude/elliptic-curve-goals-3bfz9x`; frontier map rendered at
`980abd8feec6429d1e7abb17618fe37bd10bd8a0`. No runs; no file outside the
declared write scope was written; no existing record was edited.

## Returned once (2026-10-01)

The dispatcher returned all three records for one schema fix:
`prior_art.nearest[].ref` must resolve to a KR-* row or a KN-* entry
(`templates/research-records.md` "Prior art on ideas";
`tools/validate_ledger.py check_prior_art`). IDEA-* refs were moved out of
`nearest` (they were already in `citations` and `discriminated_from`; the
`discriminated_from` text was expanded to carry the former `nearest` deltas)
and replaced by KN-* entries carrying the same prior work, each verified by
Glob before writing. No claim, mechanism, prediction, threshold, cost or
novelty_status changed. What moved:

- IDEA-20260930-b26bbc: removed `IDEA-20260926-0d1d74`, `IDEA-20260926-89886c`
  from `nearest`; added `KN-FIND-c3a917` (special_case), `KN-TECH-b18366`
  (adjacent), `KN-OPEN-3c8f51` (adjacent). `nearest` now: KR-IC-889857,
  KR-IC-fbdb61, KR-IC-e847d1, KR-IC-5765d2, KN-FIND-c3a917, KN-TECH-b18366,
  KN-OPEN-3c8f51.
- IDEA-20260930-ba8184: removed `IDEA-20260905-24d827`, `IDEA-20260808-da1428`,
  `IDEA-20260906-c8f2f6` from `nearest`; added `KN-FIND-c3a917` (orthogonal),
  `KN-OPEN-020` (adjacent), `KR-IC-0d2021` (adjacent). `nearest` now:
  KR-IC-5931ee, KR-IC-f5c584, KN-FIND-c3a917, KN-OPEN-020, KR-IC-0d2021.
- IDEA-20260930-c5466b: removed `IDEA-20260926-9cc043`, `IDEA-20260930-b26bbc`
  from `nearest`; added `KN-FIND-c3a917`, `KN-TECH-b18366`, `KN-OPEN-3c8f51`
  (all adjacent); added a `citations` entry for `IDEA-20260930-b26bbc`
  (provenance internal). `nearest` now: KR-IC-8b9daa, KR-IC-f5c584,
  KR-IC-889857, KN-FIND-c3a917, KN-TECH-b18366, KN-OPEN-3c8f51.

## Ids used and unused

| id | used | question | class |
| --- | --- | --- | --- |
| IDEA-20260930-b26bbc | yes | RQ-ECDLP-f0a7b0 | algorithm |
| IDEA-20260930-ba8184 | yes | RQ-ECDLP-f0a7b0 | control |
| IDEA-20260930-c5466b | yes | RQ-SATIC-1ae57a | control |

Unused: none. No spare id was requested.

## One-line summaries

- **IDEA-20260930-b26bbc** -- class (a), search exponent. Claim: enumerating
  m-2 legs by group arithmetic and deciding the two-leg residual
  `S_3(x_1, x_2, x(R - P_3)) = 0` by the degree-bounded mutant closure W_D
  (the exact object certified at m = 2 by KN-FIND-5a8d3e / KN-FIND-c3a917)
  gives per-attempt exponent `(m-2) l + O(log l)` instead of `(m-1) l`,
  conditional on the refuting degree staying bounded along `n = 3 l` (H2);
  relation collection `2^{2n/3} poly` at polynomial memory, a factor
  `2^{n/6}` above rho, product law on ECC2K-130 unchanged; escapes the SATIC
  ceiling because the inner theory is degree-4 polynomial calculus, not unit
  propagation or degree-1 closure; null ladder = same-support random inner
  systems, planted satisfiable residuals, deliberately easy control.
  `novelty_status: unverified`. Cost: implementation medium, compute medium
  (10^1-10^2 CPU-hours estimate). Priority high within the lane.
- **IDEA-20260930-ba8184** -- class (a), honestly expected negative. Claim:
  for the prime-field digit-presented two-leg residual (one equation in 2s
  Boolean-valued variables over F_p) the plain Macaulay refutation degree is
  exactly `4 + deg(f^{-1})` (pointwise inverse on the cube; zero linear
  algebra), generically `2s + 4`; its slope in s and the mutant rung W_D
  decide whether a Groebner-theory CDCL(T) can prune two free digit blocks,
  testing IDEA-20260905-24d827 (B) and IDEA-20260808-da1428 at d = 2 with an
  exact instrument and naming the binary/prime contrast (n descended
  generators versus one principal residual). `novelty_status: unverified`.
  Cost: implementation medium (an F_p closure engine), compute low. Priority
  medium.
- **IDEA-20260930-c5466b** -- mechanism control (aimed at (a) only through
  b26bbc; no exponent of its own). Claim: the one-leg restriction of the
  direct S_4 descent equals `(a + x_R)^4 S_3(x_2, x_3, u_+) S_3(x_2, x_3, u_-)`
  with `u_+- = x(R +- P_3)`, so it is the descent of a PRODUCT of the two
  certified inner objects; the product penalty `rung(product) - max rung
  (factors)` on identical (a, R), against same-support, random-pair and
  one-random-factor nulls, decides whether the bounded-degree refutation is
  S_3-specific (M1) or restriction-general (M2). `novelty_status:
  unverified`. Cost: implementation low, compute low. Priority medium.

## Recommended first test

IDEA-20260930-b26bbc Stage 1 at (n, l) = (23, 8) and (35, 12): the
off-diagonal m = 2 ladder with W_3 and W_4 on 60 unsatisfiable inner
instances per cell plus the same-support null, with no wrapper and no SAT
solver. It is the cheapest discriminator of the one assumption (H2) that
carries the lane's only exponent claim: at (35, 12) the null needs degree 5
by the semi-regular reference (rows 10535 against 12951 columns at degree 4,
so degree 4 is not generic there), and a W_4 rate near 1 or near the null's
decides E-BOUNDED against E-DRIFT. Its instruments exist
(`experiments/EXP-CERTBIN-e94b27/impl/closure.py`, `src/semaev_tree.py`).

## Ranking rationale (expected information gain against cost)

b26bbc first: positive outcome moves a per-attempt exponent within the
binary family (asymptotically, with a degree-11 polynomial constant that
pushes the crossover to about l = 50); negative outcome closes the
bounded-degree inner-theory route with a measured rung-versus-cell table.
c5466b second: cheapest, shares b26bbc's build, and decides the presentation
question 9cc043 and b26bbc leave open. ba8184 third: cheap and exact, but
its expected outcome is negative and its exponent reading has prior at most
0.1; its value is the exact prime-field obstruction.

## Honest accounting (docs/inventor-protocol.md section 5)

- Objects considered: the depth-l node label of a leg-enumerating search
  with a bounded-degree closure as inner theory (b26bbc); the pair
  (inverse degree, mutant rung) of the prime-field digit residual (ba8184);
  the rung triple (product, factor, factor) of the restricted direct S_4
  (c5466b). Each passes the lossy-projection test against its named
  operation set (restriction then D-bounded ring action); each is placed as
  coordinate-dependent in the weak sense of IDEA-20260926-917981
  Proposition B.
- `dominated_by`: b26bbc -- rho on the ECDLP; the pair-table row ties the
  conditional time exponent at exponential memory; the loop dominates at toy
  scale; checked against every KR-IC row named in its `prior_art`. ba8184 --
  n/a (no result claimed) under its expected outcome; rho and the MITM
  engine otherwise. c5466b -- n/a (no result claimed).
- `sota_delta`: b26bbc -- zero on the ECDLP; conditional on H2, the
  poly-memory relation-collection row of the binary subspace family moves
  from `2^n` to `2^{2n/3} poly`. ba8184 -- zero; an exact instrument.
  c5466b -- zero; a presentation-level measurement.
- Enumerated closures (mechanism and forward guidance): none closed by this
  session. Declined, with reasons recorded here: (i) MaxSAT / ILP factor-base
  selection -- the only free quantity under KN-FIND-007 is coverage, whose
  headroom `min(1, mu)/(1 - e^{-mu})` tends to 1 in the relation-collection
  regime `mu << 1`, so no ILP objective on coverage can move a constant
  there; the remaining objectives (|G| via torsion-invariant bases, the
  per-node refutation rate, linear-algebra weight) are known (KR-IC-955fd6,
  KR-IC-b0fcda, IDEA-20260920-18dc28), have no closed-form proxy, or are a
  log cofactor; the measured V-dependence of the refutation rate is a
  secondary arm of b26bbc (KN-FIND-7c1e94 section 3 already shows W_4 is not
  polynomial-basis-specific on one random V). (ii) Cube-and-conquer /
  lookahead with learned orders -- under the ceiling mechanism failed-literal
  probing on core variables fires only within O(1) of the leaves and a learned
  order can at most reach B(order) = 0 (IDEA-20260904-7fd218 H2); low
  information gain, not filed. (iii) A separate (c)-class certificate-format
  record -- folded into b26bbc (per-attempt certificate tree, check cost as a
  required metric) to avoid restating IDEA-20260905-a6f98e.
- Open directions for the next session: the (47, 16) and (53, 18) ladder
  cells if E-BOUNDED holds; a second curve per n; the coordinate presentation
  (y_1, y_2 free) of the prime-field residual; the (m-2)-leg restriction of
  S_5 if M2 holds; a compiled GF(2) echelon for columns above 25000.

## Records read for overlap

Lane list (`context/L6-CONSTRAINT.md`): all 14 hypotheses by title; all 17
proposals -- the five SATIC records of 2026-09-04 in full, the six
RQ-ECDLP-f0a7b0 records of 2026-09-05 (claim, mechanism, novelty screens),
the four 2026-09-06 SATIC records (claim and mechanism), IDEA-20260920-18dc28
and IDEA-20260926-b11cb1 (claim). Outside the lane: IDEA-20260926-89886c
(exemplar, in full), 917981, 9cc043, 0d1d74, d3c5a5, 4b65e3 (claims),
IDEA-20260808-da1428 (to line 60), IDEA-20260903-e1e38b (to line 45),
IDEA-20260830-84cdb7 (title), all 2026-09-26 to 2026-09-30 proposal titles.
Knowledge: KN-FIND-5a8d3e, KN-FIND-c3a917, KN-FIND-aa2efc (in full);
KN-FIND-007 (to line 60); KN-FIND-7c1e94 (section 3); KN-FIND-a8990a
(Theorem C); KN-TECH-b18366 (to line 80); KN-OPEN-002, KN-OPEN-020 (in
full); KN-OPEN-3c8f51 (statement, criteria); the index-calculus frontier map
(24 rows); DEC-20260926-901ea1 (ruling lines); notes/satic_solver_environment
_20260904.md; docs/claims-and-verification.md; docs/inventor-protocol.md
sections 4, 5, 8; docs/object-frame-ideation.md sections 1-3;
templates/research-records.md (prior art, citation provenance);
agents/idea-generator.md; docs/target-result-profile.md (part A).

## Searches run

Grep (corpus): `cvc5|finite.field (theory|solver)|QF_FF|MaxSAT|cube.and.conquer|ILP|pseudo.Boolean|VeriPB|#SAT|model count` over `knowledge/` (32 files, none on the pdp); `cvc5|QF_FF|MaxSAT|cube-and-conquer|lookahead|CDCL(T)` over `ledger/` (10 files); `hybrid|guess|fix.*block|one block|residual|W_4|W_D|mutant` over `ledger/proposals` (250+ files; all 2026-09-26 to 2026-09-30 titles read); `R - P_3|inner oracle|m = 2 oracle|delegat` (no hits); `x(R - P|last leg|end leg|peel` over 2026-09 proposals (25 files, titles inspected); `random subspace|dim V^(2)|product space` (24 files, titles inspected); `Bettale|hybrid approach|BooleanSolve` over `knowledge/` (6 files); engine names under `src/` and `experiments/`; Glob of the five KN-* ids used as replacement `nearest` refs (all resolve).
Web: WebFetch `https://eprint.iacr.org/2023/091` (abstract); WebFetch `https://cs.stanford.edu/~aozdemir/research` (publication list: Split Groebner Bases CAV 2024, SMT-LIB theory of finite fields SMT 2024); WebSearch "proof-producing finite field SMT solver Nullstellensatz certificate cvc5 Groebner unsat proof"; WebSearch "cube-and-conquer lookahead failed literal probing Weil descent summation polynomial point decomposition SAT 2024 2025"; WebSearch "MaxSAT OR ILP factor base selection index calculus elliptic curve point decomposition". None returned a source on a bounded-degree closure as an inner theory of a leg-enumerating decomposition search, on the refutation degree of a digit-presented residual, or on MaxSAT/ILP factor-base selection; absence is a floor. The crypto-kb index was empty (`CRYPTO_KB_QDRANT_URL=:memory:`), so no `kb` provenance was available.

## Numbers derived in this session (all labelled "my arithmetic", to be re-derived at Stage 0)

Semi-regular references `(1+z)^{2l}/(1+z^2)^n` for the m = 2 inner object:
(12,17): 4; (14,19): 4; (16,23): 4; (20,29): 4; (24,35): 5; (28,41): 5;
(32,47): 6; (18,17): 5 (reproduces KN-FIND-5a8d3e). Rows `n C(2l, <= 2)`
against columns `C(2l, <= 4)`: 1343/794, 2014/1471, 3151/2517, 6119/6196,
10535/12951, 16687/24158, 24863/41449. For n quartics in 2l variables
(c5466b): (12,17) D_reg 6, (16,23) D_reg 7. Size law for the inner W_4:
about 0.04 l^11 word operations; crossover against the loop about l = 50.
Prime-field exact identity: plain Macaulay refutation degree
`4 + deg(f^{-1})`; generic value `2s + 4`.

## Files written

- `/home/user/crypto-autoresearcher/ledger/proposals/IDEA-20260930-b26bbc.yaml`
- `/home/user/crypto-autoresearcher/ledger/proposals/IDEA-20260930-ba8184.yaml`
- `/home/user/crypto-autoresearcher/ledger/proposals/IDEA-20260930-c5466b.yaml`
- `/home/user/crypto-autoresearcher/analysis/ecc-ideation-20260930/reports/TASK-20260930-a1877b-generator-report.md`
