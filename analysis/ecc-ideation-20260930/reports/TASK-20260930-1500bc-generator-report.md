# Generator report, lane L1 (SSIQ), TASK-20260930-1500bc

Date: 2026-10-02. Branch claude/elliptic-curve-goals-3bfz9x. Question: RQ-SSIQ-9702af.
Proposals only: no hypothesis, experiment, approval or status change; no runs; no
existing record edited. The deferral of the earlier SSIQ delta_E run at its first
gate (named by the handoff card) is an environment impediment and is treated as
such, never as evidence about any lever (AGENTS.md rule 3).

## Inference

The card requests policy research-deep with fallback_allowed: true. Five earlier
launches of this lane were terminated by the API (a spend limit; a content-safeguards
classifier false positive on isogeny-attack text on the session model; then three
session limits on the larger models) before the deliverables were written; this
launch runs on a smaller model as the card's permitted fallback. Each record
therefore carries `inference: {requested_policy: research-deep, fallback_used: true,
fallback_reason: ...}`. Because the model is smaller than requested, these proposals
warrant closer reviewer scrutiny than the siblings. Specific places to scrutinise are
listed at the end of this report.

## Ids used and unused

| id | status |
| --- | --- |
| IDEA-20260930-024033 | used (memory axis, ordered-key obstruction) |
| IDEA-20260930-0d7c7d | used (F3, degree-level thinning by representation multiplicity) |
| IDEA-20260930-27b6c1 | UNUSED, returned to the dispatcher (no third honest candidate; see "Why two") |

## Records read for overlap

Handoff card; BRIEF.md (sections 0, 3, 4, 5, 7); context/L1-SSIQ.md in full (every
hypothesis and proposal title); agents/idea-generator.md; docs/inventor-protocol.md
(sections 4 and 5); templates/research-records.md (Prior art on ideas, Citation
provenance); exemplar IDEA-20260926-89886c; filed sibling IDEA-20260930-a6491b (form);
RQ-SSIQ-9702af and RQ-SSI-001 (via the context file); inputs/P13-WESOLOWSKI-2026/
paper_fulltext.md lines 1-330 (Sections 1-4.2); DEC-20260805-596d71 (first 80 lines).
Proposals read in claim and mechanism blocks: IDEA-20260806-d5a34e, IDEA-20260807-edb3f3,
IDEA-20260807-7424a9, IDEA-20260901-1f5a62, IDEA-20260805-b4bc59, IDEA-20260805-e7ee4a,
IDEA-20260901-deaf80, IDEA-20260807-6c89a8, IDEA-20260901-871141, IDEA-20260906-d95de0.
Read by title or context summary only: the other SSIQ and SSI proposals in the context
file, including IDEA-20260821-167fd9, IDEA-20260815-e94ea3, IDEA-20260805-250e50,
IDEA-20260805-c60813, IDEA-20260901-863e36, IDEA-20260806-c5d183. Knowledge entries
read: KN-TECH-055 (lines 1-40), KN-TECH-050 (lines 1-80), KN-LIT-6fb205 (full),
KN-LIT-6085 (full); titles only for KN-OPEN-013/015, KN-FIND-ffe1df, KN-LIT-7563,
KN-LIT-1499, KN-LIT-5d518f, KN-LIT-3f24a6, KN-LIT-678a43. docs/recent-cryptanalysis-
literature-20260926.md (first 120 lines). The sibling lanes' records were checked by
grep for holonomy, Schroeppel, thinning and strong approximation: only IDEA-20260930-750de2
(lane L4, generic groups) mentions Schroeppel-Shamir, in a different problem; no overlap.

## Searches run, and what was and was not retrieved

The crypto-kb index is empty this session; no `kb` provenance exists. Grep over
knowledge/ and ledger/ (corpus): Eisenstein or Mazur or Brandt module (ledger/proposals:
unrelated except IDEA-20260805-c60813); representation technique or Howgrave or
Schroeppel or k-list (only IDEA-20260901-871141 in the SSI lanes); midpoint, tau(d),
divisor-window (IDEA-20260805-b4bc59 and others, no degree-level thinning); Tani or
quantum claw or 2026/1821 (IDEA-20260904-ec17aa explicitly screened a quantum claw record
out because eprint 2026/1821 covers it; I therefore did not file one); 2609.03839,
2607.25552, Mamah (the corpus has Mamah at abstract level, not the other two). Glob
verified every KN-*, IDEA-*, H-*, DEC-*, EV-*, RQ-* id cited in the two records.

Web (WebSearch and WebFetch, 2026-10-02):
- Retrieved at abstract level (read): eprint 2026/1821 (Mamah, "Complexity Analysis and
  Security Implications of the New Isogeny-Path Algorithm": improves on prior work only
  at NIST level I; vOW variant recovers the advantage with high parallelisation; Grover
  removes the memory but gives little time gain; Tani gives a stronger gate-memory
  tradeoff at the cost of substantial coherent quantum memory). arXiv 2609.03839
  (Swanson, "Supersingular Elliptic Curves Without Inseparable Small Degree Endomorphisms",
  3 Sep 2026: delta(p) attains its upper bound iff p is represented by one of nine
  explicit cubic polynomials; for almost all primes delta(p) lies at least p^{1/6-o(1)}
  below its upper bound). arXiv 2607.25552 (Kirimli and Korpal, "Refined Humbert
  Invariants in Supersingular Isogeny Degree Analysis", 28 Jul 2026: an upper bound on the
  largest minimal isogeny degree among pairs of supersingular curves, independent of
  endomorphism rings, checked up to p = 659). A search result confirmed the abstract-level
  description of Aubry-Oyono-Vincent (delta_E definition) without the paper.
  Consequence recorded in the report only (no write scope to knowledge/literature):
  neither 2609.03839 nor 2607.25552 moves the exponent of F1; Swanson's gap p^{1/6-o(1)}
  is lower-order against p^{1/3}. A curator may wish to log both, hedged, as ingredient
  scouting.
- NOT retrieved: Tani's claw-finding theorem (arXiv 0708.2584). The abstract states an
  optimal quantum-walk algorithm for domains of sizes N and M and the extension to k
  functions; the exponent could not be read (PDF unrenderable, no pdftoppm). One fetch
  summary returned O~(N^{1/2} M^{1/4}) and "N^{3/4} for M = N"; I believe that is the
  earlier bound of Buhrman et al. that Tani improves to O((NM)^{1/3}), but this is
  recalled and UNVERIFIED. Biasse-Jao-Sankar's quantum exponent for the supersingular
  problem was not retrieved (the search snippet concerned a different statement).
  Schroeppel-Shamir, strong approximation (Kneser, Eichler), Howgrave-Graham-Joux, the
  divisor bound and Ford, and the smooth-integer samplers are recalled only.

## One-line summaries

| id | class | claim | novelty_status | cost |
| --- | --- | --- | --- | --- |
| IDEA-20260930-024033 | mechanism | Memory axis: Schroeppel-Shamir streaming of the Frobenius claw would give (time, memory) = (p^{1/3}, p^{1/6}), p^{1/12} below the vOW curve, but needs an abelian-valued ordered key independent of the path; conditional on strong approximation the only such key on the level-N-marked groupoid is the degree (alphabet about p^{1/6} < M = p^{1/3}), and the N dividing 6 abelianisations are path-dependent holonomy. Time exponent does not move. | unverified | low (Stage 0 derivation; holonomy census of groups of order at most 2016, minutes; crypto-size row env-gated) |
| IDEA-20260930-0d7c7d | algorithm (building block) | F3: a shortest isogeny of degree d has k(d) balanced splits, so thinning the list by a random fraction of DEGREES keeps a split with probability 1 - (1 - rho^2)^{k/2}; gain about 0.45 sqrt(k) in time AND memory (unlike vertex subsampling), Pareto family time x memory about 1.75 M^2 / k; ceiling k <= tau(d) = p^{o(1)}, so (p^{1/4}, p^{1/4}) would need k >= p^{1/6}. No exponent moves. | unverified | low (Arm I integer-only now; Arm II Deuring and Arm III end-to-end env-gated) |

Which factor each moves, from what to what: 024033 acts on the storage of the F3 list
(memory p^{1/3} to p^{1/6} IF an ordered key existed; predicted not; time stays p^{1/3}).
0d7c7d acts on F3 by a constant p^{o(1)} factor G = 0.45 sqrt(k) (time p^{1/3} to p^{1/3},
memory p^{1/3} to p^{1/3}, overhead divided by G); the numeric condition on F3 for 1/4
is k >= 2 p^{1/6}. Both state the corollaries (EndRing, Isogeny via the cited reductions,
unchecked by this program) as inheriting at most a constant or memory change.

## The one recommended first test

IDEA-20260930-0d7c7d, Arm I plus the cover-probability simulation. It is integer-only
(no curve or quaternion machinery, so the environment impediment that deferred the
earlier run does not apply), costs minutes to hours, and its outcome is genuinely open
(prior about 0.5 on median k at least 80 versus below 8) with thresholds fixed in the
record. Its negative result is informative (the lever is worth under half a bit at
NIST-I). IDEA-20260930-024033's Stage 0 and census are cheaper still but their predicted
outcome is closure (prior about 0.9), so they carry less information per run.

## Honest accounting (docs/inventor-protocol.md section 5)

Objects considered. Scored (new or repackaging / concretely testable / how far it
survives):
1. Marked-vertex key g with cocycle labels on the level-N groupoid (024033): new as a
   statement for OneEnd, a transplant of 871141's digest requirement; testable (holonomy
   census, minutes); dissolves at the perfectness of SL_2(Z/N) (predicted).
2. Degree-support set S of listed degrees (0d7c7d): the same kind of object as Delgado's
   deterministic family; testable at integer level; survives until the closure term and
   the k distribution are measured.
3. sigma-invariant vertex filter: standard (vOW with multiplicity, b4bc59); folded into
   0d7c7d as the second knob, not filed alone.
4. Polynomial-method object F(y) = prod Phi_a(j_E, y), claw as gcd(F, F-bar): lossless,
   a change of coordinates (fails the lossy-projection test); same Otilde(M) time and
   memory; not filed.
5. Mod-p Eisenstein-congruence harmonic labelling of the supersingular set: a branching
   (not partial-action) object whose neighbour sums are determined but individual
   neighbours are not; no mechanism that propagates; not filed (could be a measurement
   of branching b at toy primes if a reviewer wants it).
6. Quantum claw object: already screened out by IDEA-20260904-ec17aa against eprint
   2026/1821; not filed (see open directions for the exponent arithmetic).

dominated_by. 024033: n/a (no result claimed); frontier rows checked: Delfs-Galbraith,
the source's list algorithm, van Oorschot-Wiener; the conditional lever would dominate
the vOW row at w = p^{1/6}. 0d7c7d: n/a (no exponent result claimed); the incumbent
list algorithm is the baseline modified; the Pareto family lies below vOW with
multiplicity k for memory between about 3 M / k and M sqrt(1.25 / k), conditional on a
measured k and on the closure term (hand estimate). The ECDLP map has no isogeny rows,
so no `null` is claimed on either record.

sota_delta. Zero on every exponent axis for both records. 024033: first statement of the
ordered-key requirement for the OneEnd claw with a conditional closure. 0d7c7d: a factor
0.45 sqrt(k) on the incumbent's superpolynomial overhead (illustration 14, about 3.8 bits,
at k of order 10^3, an UNCHECKED input from IDEA-20260805-b4bc59 at the asymptotic B; the
number at the optimised B is smaller and is what Arm I measures).

Enumerated closures (named obstruction, argument, forward guidance; all are derivations of
this session, UNVERIFIED, none committed):
- Ordered-merge memory lever (Schroeppel-Shamir class): obstruction = path-dependent
  holonomy; argument = key must be trivial on H_N which contains SL_2(Z/N) by strong
  approximation (recalled), SL_2(Z/N) perfect for N prime to 6, det = degree; remaining
  classes: vOW interpolation, non-abelian or extra-data keys, quantum memory models.
- Representation technique and any filter-based sublist compression at the exponent:
  obstruction = number of representations per solution is at most tau(d) = p^{o(1)}
  (plus p^{o(1)} distinct short solutions); argument = divisor bound; forward guidance:
  only a constant p^{o(1)} gain, which 0d7c7d prices.
- F1 (smallest-degree bound): closed in scope already by EV-SSIQ-e43afd and the rank-3
  count of IDEA-20260805-e7ee4a; the 2026 literature scouted this session
  (Swanson 2609.03839) gives a lower-order gap only. Forward guidance unchanged: the
  open classes are the covering and detection routes of IDEA-20260807-edb3f3.
- Extra free canonical correspondences: the only End-invariant kernels on a maximal order
  of B_{p,infinity} are those of two-sided ideals, which are P^a (n); so Frobenius is the
  only free long jump (consistent with IDEA-20260901-deaf80, IDEA-20260805-e7ee4a).
  Remaining: instance-supplied auxiliary data (KN-OPEN-015).
- k-way splits with equality-only matching: no partial constraints, so intermediate lists
  cannot be filtered; time at least p^{1/3} (folded into 024033's obstruction).
- Re-randomised endpoints used simultaneously: a solution for a pair (E_i, sigma E_j)
  corresponds to a non-minimal one for E_i (degree scaled by deg of the walk squared);
  no gain (hand argument, not filed).

Open directions for the next session.
1. Read eprint 2026/1821 in full (this program has the abstract only) and Tani's theorem
   (arXiv 0708.2584). Hand arithmetic, UNVERIFIED: with ball volume V = p^v, single-solution
   probability pi = V^{3/2} / p^{1/2} (v at most 1/3), amplitude amplification over attempts
   and a claw cost V^{e}, the quantum exponent is 1/4 + v (e - 3/4): flat at 1/4 for
   e = 3/4 (the older Buhrman et al. exponent, matching quantum Delfs-Galbraith) and
   1/4 - v/12 = 2/9 at v = 1/3 for e = 2/3 (Tani, recalled). Which of the two Tani's
   theorem states decides whether the quantum tier sits at 2/9 or 1/4, at memory
   about p^{2/9} under quantum RAM. A zero-run check, tier labelled quantum.
2. Execute 0d7c7d Arm I; if the median k is at least 80, Arms II and III and a hand-off
   to the NIST-I concrete rows.
3. Execute 024033 Stage 0 and the holonomy census; read the strong-approximation input.
4. IDEA-20260807-7424a9's design should replace its single-entry null by the per-solution
   null of 0d7c7d if it is designed.
5. The environment gate that deferred the earlier SSIQ run blocks Arm II and Arm III and
   the cryptographic-size rows; it is an impediment, not evidence.

## Why two and not three

I found two honest, distinct, falsifiable candidates after enumerating objects against
the corpus. The third slot was left unused rather than filled with a record that
restates a filed one: the quantum claw (screened out by ec17aa), the memory tradeoff
(IDEA-20260821-167fd9), the auxiliary-target census (IDEA-20260805-e7ee4a,
IDEA-20260901-deaf80), the F1 closure (EV-SSIQ-e43afd) and the detection levers
(IDEA-20260821-e99afd, IDEA-20260901-65c009, IDEA-20260901-22428d) are all covered.

## Where to scrutinise these records (smaller-model fallback)

1. 024033: the requirement that an SS key have labels independent of the middle curve
   (K2) and the equivalence "K1-K3 imply path independence" are my derivation; the
   proof obligations are listed, not discharged. The strong-approximation and perfectness
   steps are recalled. The SQIsign-prime caveat (cheap 2^e marking) is stated.
2. 0d7c7d: the independence of unordered-pair events, the hand constants (t about 1.25,
   0.45 sqrt(k), 1.75, the 3 M / k crossover), and the vertex-filter independence of the
   two ordered splits are by hand and unchecked by code. The vertex-level knob is
   standard (vOW with multiplicity); the claimed novelty is the degree knob and the
   per-solution null. The generation-time claim rests on H4 (parent closure) and
   Algorithm 1's batch structure.
3. No shell was available: the YAML was checked by hand and by grep for ": " hazards
   in plain scalars and tabs, not parsed. The dispatcher should run the validator.
   (A first draft of 024033 had one such hazard in a list item; it was rewritten before
   delivery. The Edit tool was unavailable, so each record was written whole.)
4. Every cited id was verified to exist by Glob; every `recalled` citation is marked and
   both records are therefore `unverified`; every internal citation has `verified_by`.

## Files written

- /home/user/crypto-autoresearcher/ledger/proposals/IDEA-20260930-024033.yaml
- /home/user/crypto-autoresearcher/ledger/proposals/IDEA-20260930-0d7c7d.yaml
- /home/user/crypto-autoresearcher/analysis/ecc-ideation-20260930/reports/TASK-20260930-1500bc-generator-report.md

IDEA-20260930-27b6c1 was not written (returned unused).
