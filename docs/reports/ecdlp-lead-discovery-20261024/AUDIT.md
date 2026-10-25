# Audit passes AUD-1..6 over all 147 leads (per family; proposed changes only)

Generated 2026-10-24 by the audit agents (opus, effort high) of the lead-discovery workflow; every finding quotes the lead's obstruction.statement or next_action and names an evidence path. Disposition changes were sent to three skeptics each (see report section b for the verification outcome). Nothing here was applied to a row.

---

## Family: generic

# Audit of the generic (RHO) family, passes AUD-1..AUD-6

Reviewer: workflow subagent, 2026-10-24. Read-only over the repositories. 26 lead rows read in full from `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/generic/`. Quotes of `obstruction.statement`, `revisit_when` and `next_action` are pasted verbatim from the YAML by `audit/generic-work/build_audit.py`; analysis text is in `audit/generic-work/analysis.py`. Observations name a path; everything labelled "reviewer derivation" or "conditional" is interpretation, not an observed result.

Current state used for AUD-1: `atlas/KRMAP.md`; crypto `docs/ic/LEADERBOARD.md` and `docs/bounds/FRONTIER.md` (frontier `ECFR1hbd02e945e867`, domains Koblitz toy, Koblitz medium, prime toy; no prime medium tier); `atlas/delta.txt` (201 paths); the delta folds already in `audit/fold-*.md` (their bound-id drift edits, fold-crypto.md 2.2b, are referenced, not repeated); cryptanalysis `docs/sixclass-20261024/`; ecc-challenges main at df8cd52.

## Summary

- **AUD-1:** no revisit trigger of the 10 closed rows has fired on the current state. Two triggers are defective: LEAD-RHO-automorphism-class-walks (ambiguous, already true on the point estimate at closure) and LEAD-RHO-bsgs-family-memory (cites KR-RHO-7d93f6, a many-collision bound, for a one-collision problem). Two triggers name domains, not events: LEAD-RHO-cheon-aux-acquisition clause 2 and LEAD-RHO-kangaroo-interval.
- **AUD-2:** forecloses wider than the proof in bsgs-family-memory, cheon-aux-acquisition, generic-sqrt-lower-bound (including its family-scope sentence), negation-map-fruitless-cycles and r-adding-walk-mixing (which carries the open transfer-operator hypothesis H-TRA-4344b7). The correlated-walks proof statement says "can never meet"; the precise statement is "never merge".
- **AUD-3** covers 2 rows by kind (bsgs-family-memory cost_model, kangaroo-interval measured). It gives a Lean target for the BSGS covering bound and a kind change for kangaroo.
- **AUD-4** covers 13 rows. The two with a decisive desk route are cheon-deployed-applicability (a factorisation-free bound E >= (log n - log q)/(2 log r) needs supply >= r^{0.2} for E <= 0.40; this is a conditional close) and cheon-toy-reproduction (its queued hypothesis is arithmetic only and cannot discriminate). pool-class-quotient is stale: walk 4 is already the default on two campaigns.
- **AUD-5** covers 3 rows. non-automorphism-equivalence: its queued Omega(log h) target is too weak; SO-GEN closes the generic half via H-EWALK-29cb90's own N^{1/3} derivation.
- **AUD-6:** SO-GEN, SO-CHEON and SO-WALK are owned here; see the lead subsections.

## LEAD-RHO-advice-table-variants

- Title: Variants of the advice table: batch-reselected, batch-grown, basin-instrumented and transported tables
- Disposition: `open_next_step`; file `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/generic/LEAD-RHO-advice-table-variants.yaml`
- next_action.step (verbatim): "Replicate EV-ECDLP-f6b3f5's re-scoped support (T_sel in {0.65T, 0.75T}) on an elliptic-curve walk at N = 2^30 with an independent implementation, and repair fixture_gate_v2 for the basin instrument (EV-ECDLP-31e91c failed the comparability gate)."
- next_action.discriminates (verbatim): "Replicated S1_v2 at both T_sel on a curve makes the reselected table a measured precomputation saving (constant level); failure confirms EV-ECDLP-60e266's contradiction and closes the variant."
- forecloses: "batch-reselected Bernstein-Lange table"; "grow the table from solved walks"; "basin-partition coverage instrument"; "transport a precomputation table by isogeny"; "retention rate of preprocessing across curves"

**AUD-1 revisit triggers.**

n/a for this disposition.

**AUD-2 scope.**

n/a for this disposition.

**AUD-3 measured/cost_model to proof.**

n/a for this disposition.

**AUD-4 open_next_step/open_blocked: theorem vs experiment.**

Observation: the queued step replicates EV-ECDLP-f6b3f5's re-scoped support at N = 2^30 and repairs fixture_gate_v2 (EV-ECDLP-31e91c failed the comparability gate).

Theorem route: KR-RHO-ea34b8 / KN-LIT-013 (Corrigan-Gibbs-Kogan, S*T^2 = Omega~(eps*N), generic, tight) already decide the asymptotic question for every table variant that is still S bits of generic advice: a reselected, grown or transported table cannot change the online exponent. The lead's own `discriminates` is constant-level ("a measured precomputation saving (constant level)"), which no theorem decides. Interpretation (conditional): no proof shortcut for the constant; the experiment stays. One wording change: state in `discriminates` that both outcomes are constant-level under CGK, so a positive result cannot be read as an exponent change.

**AUD-5 open_unexamined: first step.**

n/a for this disposition.

**AUD-6 obstruction as hypothesis.**

n/a for this disposition.

*Proposed change:* none

## LEAD-RHO-automorphism-class-walks

- Title: Rho on automorphism/Frobenius orbits: sqrt(2m) on Koblitz, order-4/6 maps on j=1728/j=0
- Disposition: `closed_known`; file `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/generic/LEAD-RHO-automorphism-class-walks.yaml`
- obstruction.kind: `literature`
- obstruction.statement (verbatim): "Known (KR-RHO-037e22, KR-RHO-482ed3, KR-RHO-0528e7) and reproduced: rho.signed_frobenius_strong 1.089 [0.927, 1.261] x sqrt(pi/4n) on Koblitz curves log2 r 32.1-47.2 (medium tier, 144 runs); strong-rho steps/ideal 0.99, 0.92, 0.94 at n = 41, 53, 61; j=0 crater rho.cubic/rho.negation 0.573 [0.562, 0.585] against theory 0.577 (volcano census). The ceiling is sqrt|Aut| and the program sits on it."
- obstruction.revisit_when (verbatim): "A curve family with a larger efficiently computable automorphism group is found, or a medium-tier run shows a shortfall >5% from the sqrt(A) ceiling."
- forecloses: "Frobenius equivalence classes for Koblitz rho"; "sqrt(2m) speedup on anomalous binary curves"; "GLV automorphism quotient on j=0 curves"; "walk on orbits of the automorphism group"; "automorphism speedup beyond sqrt(|Aut|)"

**AUD-1 revisit triggers.**

Not fired on the current state. FRONTIER `ECFR1hbd02e945e867` (crypto docs/bounds/FRONTIER.md, Koblitz medium domain) still reads `rho.signed_frobenius_strong` 1.089 [0.927, 1.261] (v2 bound `ECBND1hcf69c27b4978`, same values as the cited v1 `ECBND1h05a2ea918f3c`). The 2026-10-24 six-class j = 0 walk (cryptanalysis docs/sixclass-20261024/assessment.md: 1.257x and 1.826x the default wall time on `glv-j0-26`, 20 targets, no CI) is order 6 (not a larger group) and is toy wall time, not a medium-tier counted shortfall; it bears on LEAD-RHO-native-step-cost and LEAD-STR-automorphism-quotient-rho, not on this trigger.

Trigger defect: "a medium-tier run shows a shortfall >5% from the sqrt(A) ceiling" is ambiguous. Read on the point estimate it was already true at closure (1.089 > 1.05); read on the interval it is not (lower bound 0.927). Proposed operational trigger: "the lower 95% bound of a medium-tier bound exceeds 1.05 x floor".

**AUD-2 scope.**

Statement scope: counted steps (GAE) on Koblitz log2 r 32.1-47.2 and j=0 crater counts. `forecloses` "automorphism speedup beyond sqrt(|Aut|)" is supported by KR-RHO-0528e7 for automorphisms. No overreach found in the counted-step scope. Native-time claims (the six-class wall-time loss) are outside this closure and belong to LEAD-RHO-native-step-cost; no phrase here forecloses them.

**AUD-3 measured/cost_model to proof.**

n/a for this disposition. (kind literature)

**AUD-4 open_next_step/open_blocked: theorem vs experiment.**

n/a for this disposition.

**AUD-5 open_unexamined: first step.**

n/a for this disposition.

**AUD-6 obstruction as hypothesis.**

Not a standing obstruction of this family's SO list; see AUD-6 under LEAD-RHO-generic-sqrt-lower-bound and LEAD-RHO-non-automorphism-equivalence for the cheap-endomorphism-orbit idea.

*Proposed change:* revisit_when operationalisation

## LEAD-RHO-batched-inversion-shared-pm

- Title: Batched affine steps: Montgomery simultaneous inversion and the free x(P-Q) beside x(P+Q)
- Disposition: `closed_known`; file `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/generic/LEAD-RHO-batched-inversion-shared-pm.yaml`
- obstruction.kind: `literature`
- obstruction.statement (verbatim): "Known (KR-RHO-cb1c58, KR-RHO-fbd582) and reproduced: batch inversion proved correct in Lean (rho_assurance); GPU NIST W-sweep 1.52x/2.61x cumulative with by-reference inversion; plain-step cost falls with batch size (179 ns at 1024 walks on P-256). The remaining use of the free P-Q is the best-of lead."
- obstruction.revisit_when (verbatim): "An inversion-free step cheaper than 1I/n + 3M per walk."
- forecloses: "Montgomery trick for rho"; "simultaneous inversion across walks"; "shared inversion for P+Q and P-Q"; "batched affine addition"

**AUD-1 revisit triggers.**

Not fired. Delta items touching this lead: crypto problems/rho-worker-tier1-host-access.md (serial vs batch worker; per fold-crypto.md row 14 every aggregate `unknown_gate_failed`, diagnostic 5.110 not admitted) and crypto benchmarks/20261022-strong-rho-batchinv (binary batch inversion, Callgrind 707.2 -> 679.7 instructions/step, native ns not established, per fold-crypto.md 2.1b). Neither is an inversion-free step below 1I/n + 3M.

**AUD-2 scope.**

No overreach: the forecloses phrases are the KR-RHO-cb1c58 / KR-RHO-fbd582 mechanisms themselves.

**AUD-3 measured/cost_model to proof.**

n/a for this disposition. (kind literature)

**AUD-4 open_next_step/open_blocked: theorem vs experiment.**

n/a for this disposition.

**AUD-5 open_unexamined: first step.**

n/a for this disposition.

**AUD-6 obstruction as hypothesis.**

None found (not an SO-coded obstruction).

*Proposed change:* none

## LEAD-RHO-best-of-candidates-indegree

- Title: Step to the better of k candidate images (best of P+R, P-R) to concentrate in-degree
- Disposition: `open_next_step`; file `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/generic/LEAD-RHO-best-of-candidates-indegree.yaml`
- next_action.step (verbatim): "Build best-of-P+-R into the gpu/nist kernel at W = 16-32 walks per thread with the kernel's own inversion and fruitless-cycle escape; paired rate and steps-to-collision against the shipping kernel on P-256, with DP-corpus replay. On ECC2K-130, price the best-of-two sigma step (emulated 0.836x iterations) against its +38% carry-less work."
- next_action.discriminates (verbatim): "Net cost per solve < 0.97 at W = 16-32 makes it the GPU default (a constant improvement on live walks); >= 1.0 closes it as closed_obstructed (cost_model) for batched GPU walks."
- forecloses: "best of P+R and P-R step"; "choose the better candidate image"; "in-degree concentration walk"; "score-selected rho step"; "best of four candidates"

**AUD-1 revisit triggers.**

n/a for this disposition.

**AUD-2 scope.**

n/a for this disposition.

**AUD-3 measured/cost_model to proof.**

n/a for this disposition.

**AUD-4 open_next_step/open_blocked: theorem vs experiment.**

Observation (crypto research/rho_walk_leads_20261014/README.md, "Lead 1 in detail"): steps speedup s = 1.129 [1.081, 1.184] under DPs; cost vs plain step 1.215 at 1024 walks/inversion (net 0.95), 1.029-1.119 at 8-64 (net 1.03-1.12); the README adds "The inversion here is plain Fermat, which overstates the inversion share that small batches pay."

A cost-model inequality decides the GPU question before building the kernel arm. With per-step plain cost C(W) = I/W + c0 (I: one inversion, c0: the rest of the batched affine step, both in M) and extra cost e = 1M + 1S for the second candidate, net = s / (1 + e/C(W)) > 1 iff C(W) > e/(s - 1), i.e. I/W + c0 > 7.75 e at s = 1.129 (6.46 e at the predicted 1.155). Two microbenchmarks of the gpu/nist kernel (its own I/M and c0/M at W = 16 and 32) plus the measured fruitless-cycle escape rate (651 per 10^6 steps for best of P+-R) decide the sign. Outcome map: inequality fails at W = 16-32 by more than the band -> closed_obstructed (cost_model) without building the arm; inequality holds -> build the arm (the lead's current step).

**AUD-5 open_unexamined: first step.**

n/a for this disposition.

**AUD-6 obstruction as hypothesis.**

n/a for this disposition.

*Proposed change:* next_action prepend cost-model gate

## LEAD-RHO-bsgs-family-memory

- Title: Baby-step giant-step family (textbook, interleaved, negation, paired, signed-Frobenius claw)
- Disposition: `closed_known`; file `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/generic/LEAD-RHO-bsgs-family-memory.yaml`
- obstruction.kind: `cost_model`
- obstruction.statement (verbatim): "Known (KN-LIT-732e36, KN-LIT-2135) and reproduced: bsgs.negation is the prime-toy ops leader at 1.100 [0.978, 1.225] x sqrt(pi/4) but needs 0.50 sqrt(r) table entries (rho 0.034); at log2 r = 256 that is 2^127 entries, so rho with DPs dominates at every cryptographic size (KR-RHO-7d93f6). claw.pair_table costs (c + 1/c)/sqrt(n) >= 2/sqrt(n), i.e. >= 2.26x sqrt(pi/4n) rho: measured 2.20x [1.90, 2.55] strong rho at its best shape."
- obstruction.revisit_when (verbatim): "A BSGS-type schedule with o(sqrt r) memory and BSGS-level operations (would contradict KR-RHO-7d93f6)."
- forecloses: "baby-step giant-step with negation"; "interleaved BSGS"; "pair claw on Frobenius classes"; "BSGS beats rho"; "memory-bounded BSGS"

**AUD-1 revisit triggers.**

Not fired. Nothing in delta.txt is a BSGS-type schedule with o(sqrt r) memory.

Trigger defect: the parenthetical "(would contradict KR-RHO-7d93f6)" misapplies that row. KR-RHO-7d93f6 is "Finding C collisions with time T and space S requires T^2*S = Theta~(C^2*N)"; one discrete log needs C = 1, where T = sqrt(N) with S = O(1) is allowed and is achieved by rho. The correct obstruction for BSGS-type (store-and-match) schedules is the covering count in AUD-3.

**AUD-2 scope.**

Overreach: `forecloses` "BSGS beats rho" is broader than the statement. FRONTIER prime toy (crypto docs/bounds/FRONTIER.md, domain `ECDOM1ha1f283af3a5d`) has bsgs.negation 1.100 [0.978, 1.225] (`ECBND1h9d01a5c2ae56`) against rho.negation 1.453 [1.184, 1.772] (`ECBND1h67e22de83dca`): at toy scale BSGS does beat rho on ops. The statement's own scope is memory-charged at cryptographic size. Proposed phrase: "BSGS beats rho at cryptographic size with memory charged".

**AUD-3 measured/cost_model to proof.**

Kind cost_model. A short proof replaces it.

Lean target (informal): Let r be prime, G = Z/r. A store-and-match schedule is a pair of finite sets B, J of Z/r (baby multipliers stored, giant offsets visited) and it solves target x iff x is in B + J (with negation, iff x is in +-B + J). Then (i) |{x : solved}| <= 2|B||J| (with negation; |B||J| without); hence (ii) success probability >= 1/2 forces |B||J| >= r/4; (iii) with memory |B| <= M the online operation count is >= |J| >= r/(4M), so M = o(sqrt r) implies operations = omega(sqrt r); (iv) average-case ops of the textbook negation schedule with |B| = M, stride 2M+1 is M + r/(2(2M+1)) + O(1), minimised at M ~ sqrt(r)/2 giving sqrt(r)(1+o(1)) = 1.128 x sqrt(pi r/4) asymptotically, while rho.negation tends to the floor under the random-mapping heuristic (KR-RHO-fb88e6). Also: claw.pair_table cost (c + 1/c)/sqrt(n) >= 2/sqrt(n) by AM-GM, i.e. >= 2/sqrt(pi/4) = 2.257 x the sqrt(pi/4n) rho floor, which the statement already quotes.

Interpretation (conditional): (iv) says BSGS's toy ops lead is a finite-size effect of rho's set-up cost, not an asymptotic ordering.

**AUD-4 open_next_step/open_blocked: theorem vs experiment.**

n/a for this disposition.

**AUD-5 open_unexamined: first step.**

n/a for this disposition.

**AUD-6 obstruction as hypothesis.**

None found (not an SO-coded obstruction). The quantity 'memory Theta(sqrt r)' is taken as a hypothesis by the precomputation theory (KR-RHO-ea34b8): stored tables amortised over many targets.

*Proposed change:* revisit_when and forecloses rewording + Lean target

## LEAD-RHO-cheaper-step-primitives

- Title: Cheaper step primitives never measured here: tag tracing on EC, point-halving steps on binary curves
- Disposition: `open_unexamined`; file `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/generic/LEAD-RHO-cheaper-step-primitives.yaml`
- next_action.step (verbatim): "Port a tag-tracing r-adding walk to a 64-bit prime toy curve in research/rho_walk_leads' harness (ns/step paired against the plain step at 8-1024 walks/inversion, steps/collision with DP replay) and a halving-step walk on sect113r1-size binary curves."
- next_action.discriminates (verbatim): "A net ns per useful step < 0.95 opens an engineering lead for the pool and GPU kernels; >= 1.0 with matching steps closes each as closed_obstructed (cost_model) for affine batched EC walks."
- forecloses: "tag tracing for elliptic-curve rho"; "point halving rho step"; "partial-information table step"; "skip full multiplications in rho"

**AUD-1 revisit triggers.**

n/a for this disposition.

**AUD-2 scope.**

n/a for this disposition.

**AUD-3 measured/cost_model to proof.**

n/a for this disposition.

**AUD-4 open_next_step/open_blocked: theorem vs experiment.**

n/a for this disposition.

**AUD-5 open_unexamined: first step.**

First discriminating step, desk-only, before porting code: an operation-dependency count for one batched affine r-adding step. For tag tracing to save work, the next partition index must be computable from a strict subset of the step's field operations. In affine addition the slope lambda = (y_R - y_P)/(x_R - x_P) needs the batched inverse (about 3M amortised plus I/n) and 1M; x3 = lambda^2 - x_P - x_R needs 1S; y3 needs 1M and is required by the next slope. The tag is a function of x3 only, so at most the y3 multiplication can be deferred, and only by one step. Outcome map: if the deferrable share is < 5% of the step's M-equivalents, tag tracing is closed_obstructed (cost_model) for affine batched prime-field walks without an experiment; if a partial-x3 tag (top bits of lambda^2 from a truncated product) can be shown to determine the index with high probability, port it (the lead's current step). For point halving on binary curves: an r-adding walk has no doubling to replace, so halving applies only to mixed walks with doublings; first step is to check that the walk family it would enter (Teske mixed walks) is used anywhere in this program; if not, close as closed_dominated by LEAD-RHO-r-adding-walk-mixing.

Observation: the lead lists only literature evidence (KR-RHO-38be82, KR-RHO-6654ba, KN-LIT-6767); KN-LIT-6767's title is "Speeding Up the Pollard Rho Method on Prime Fields" (finite-field DLP).

**AUD-6 obstruction as hypothesis.**

n/a for this disposition.

*Proposed change:* first step: desk dependency count

## LEAD-RHO-cheon-aux-acquisition

- Title: Run Cheon's auxiliary-input algorithm on ordinary ECDLP by generating [x^d]P yourself
- Disposition: `closed_obstructed`; file `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/generic/LEAD-RHO-cheon-aux-acquisition.yaml`
- obstruction.kind: `theorem`
- obstruction.statement (verbatim): "Generic scope: from (P, [x]P) a generic algorithm can only form linear combinations [a + bx]P; [x^2]P is outside that span, and computing it is the square-DH problem, which has the same Omega(sqrt r) generic lower bound as DH (Shoup). Producing [x^d]P therefore costs rho-scale work, which DEC-20260802-204 records as the acquisition gate (APR-206 classified as Cheon prior art). Scope: generic algorithms on any curve; non-generic acquisition is not excluded."
- obstruction.revisit_when (verbatim): "A non-generic (representation-using) way to compute [x^2]P from [x]P below sqrt(r), or a protocol that releases powers (LEAD-RHO-cheon-deployed-applicability)."
- forecloses: "generate auxiliary input from the public key"; "Cheon attack on ordinary ECDLP"; "r^{1/4} ECDLP via x^d P"; "self-supplied auxiliary powers"

**AUD-1 revisit triggers.**

Not fired. Clause 1 (non-generic [x^2]P below sqrt(r)): nothing in delta.txt. Clause 2 ("a protocol that releases powers (LEAD-RHO-cheon-deployed-applicability)") is not an event: power-releasing protocols are already in the program's roster (ledger/proposals/IDEA-20260930-68326c.yaml: powers-of-tau SRS on BLS12-381 and BN254, q-SDH and VRF query channels). The clause is a scope split pointing at another lead and is satisfied permanently. Proposed: remove clause 2 from revisit_when and keep the pointer in `related`.

**AUD-2 scope.**

Overreach: the statement ends "Scope: generic algorithms on any curve; non-generic acquisition is not excluded", while `forecloses` includes "Cheon attack on ordinary ECDLP", "self-supplied auxiliary powers" and "r^{1/4} ECDLP via x^d P", which as phrased would also block a non-generic acquisition idea.

Reviewer-supplied argument that could close the gap (conditional; the sources are not in the KN-LIT store, grep for Maurer/den Boer/Boneh-Lipton found only unrelated notes): squaring-DH and DH are equivalent (xy = ((x+y)^2 - x^2 - y^2)/2), and the den Boer / Maurer / Maurer-Wolf reductions turn a DH oracle into a discrete-log algorithm with polylog(r) oracle calls, given an auxiliary curve over F_r with smooth order (existence heuristic in general). If that holds, any method computing [x^2]P from [x]P at cost C solves ECDLP at about polylog(r) * C without Cheon, so the Cheon route is dominated in every scope, not just the generic one. Proposed change: add a KN-LIT entry for the DH-DL equivalence, then restate the obstruction as "generic: Shoup; non-generic: dominated by the DH-to-DL reduction" and keep the forecloses phrases.

**AUD-3 measured/cost_model to proof.**

n/a for this disposition. (kind theorem)

**AUD-4 open_next_step/open_blocked: theorem vs experiment.**

n/a for this disposition.

**AUD-5 open_unexamined: first step.**

n/a for this disposition.

**AUD-6 obstruction as hypothesis.**

SO-CHEON (this lead). The obstructing quantity is the cost of producing [x^d]P. Theories that take it as a hypothesis: (a) protocol-supplied auxiliary input, i.e. Cheon's own setting (powers-of-tau SRS, q-SDH, static-DH oracles; Brown-Gallant), owned by LEAD-RHO-cheon-deployed-applicability; (b) the DH-oracle reduction theory (den Boer, Maurer, Maurer-Wolf), which takes a DH or square-DH oracle as hypothesis and derives the discrete log; (c) none found for ordinary ECDLP without an oracle.

*Proposed change:* obstruction scope + revisit_when cleanup

## LEAD-RHO-cheon-deployed-applicability

- Title: Where Cheon stops on deployed parameters: exact r+-1 divisor census times priced auxiliary supply
- Disposition: `open_blocked`; file `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/generic/LEAD-RHO-cheon-deployed-applicability.yaml`
- next_action.step (verbatim): "Approve a revised protocol for the typed quantity of H-AUXIN-6db354 (per-branch, supply-capped E(r)), then join the completed census (RUN-AUXIN-fd1edc) with the supply roster of IDEA-20260930-68326c under a cap on released powers."
- next_action.discriminates (verbatim): "A row with E(r) <= 0.40 at a degree some protocol releases is a named protocol-conditional weakness; no such row confirms Cheon is inert at deployed supply. Neither moves ordinary ECDLP."
- next_action.blocked_by (verbatim): "DEC-20260923-a4c3d5 refused AMD-EXP-AUXIN-7e2e3d-20260923-d1d10; H-AUXIN-6db354 is approved only with a future revised protocol"
- forecloses: "factor r-1 and r+1 of standardized curves"; "Cheon exponent on deployed parameters"; "powers-of-tau auxiliary inputs"; "SafeCurves auxiliary-input row"; "Phi_k smooth part census"

**AUD-1 revisit triggers.**

n/a for this disposition.

**AUD-2 scope.**

n/a for this disposition.

**AUD-3 measured/cost_model to proof.**

n/a for this disposition.

**AUD-4 open_next_step/open_blocked: theorem vs experiment.**

Blocked by DEC-20260923-a4c3d5 (procedural). A bound computable from the frozen definition decides the lead's discriminator without the blocked protocol.

Bound (derivation by this audit): with n = r +- 1, a supply cap q on the released degree, and E(d) = log(sqrt(n/d) + sqrt(d))/log r, dropping the sqrt(d) term gives E(d) >= (log n - log d)/(2 log r) >= (log n - log q)/(2 log r) for every d <= q. Hence E <= 0.40 requires q >= about r^{0.2}: 2^44.8 at 224 bits, 2^51.2 at 256, 2^76.8 at 384, 2^104.2 at 521. The bound needs no factorisation, so it also covers the census rows with unfactored cofactors (P-384, P-521, brainpoolP384r1, Ed25519 r-1), where divisor enumeration gives only an upper bound on the minimum.

Supply observed (ledger/proposals/IDEA-20260930-68326c.yaml, lines 39-51 and its source list): S1 public SRS rows reach at most "the perpetual powers of tau on BN254 (2^29 - 1 powers, d_max >= 2^28)"; Zcash Sapling depth 2^21; ceremony setups 2^12-1 ... 2^15-1; Filecoin and Aztec "RECALLED, NOT RETRIEVED" at about 2^27 and 2^20-2^26; S2 query-derived channels (Boneh-Boyen, Dodis-Yampolskiy, BBS, VRFs) "q = UNDETERMINED (issuance-bounded)". On BN254 (log2 r = 253.6) q = 2^29 gives E >= (253.6 - 29)/(2 * 253.6) = 0.443. Cross-check by enumeration over factored divisors (audit/generic-work/cheon_cap.py on experiments/EXP-AUXIN-7e2e3d/runs/RUN-AUXIN-fd1edc/factorizations.json; the r+1 branch needs 2d powers, not modelled): minimum over all 11 curves and both branches is 0.438 (P-224, r-1) at q <= 2^28 and 0.412 (P-224, r+1, log2 d = 39.2) at q <= 2^40.

Interpretation (conditional on S2 issuance staying below r^{0.2}, about 2^51 queries per key at 256 bits): no deployed row reaches E <= 0.40, so the lead's negative outcome ("no such row confirms Cheon is inert at deployed supply") is decided by the bound. Two caveats: (1) E between 0.44 and 0.5 is still below rho (BN254 perpetual powers of tau at about 2^113 vs rho about 2^127), which IDEA-20260930-68326c already frames as BELOW_RHO; the lead's 0.40 threshold is its own choice. (2) The S2 q values are undetermined, so the closure is conditional.

Outcome map: S2 issuance bound < r^{0.2} established for each S2 row -> closed_obstructed (kind proof, the bound above); any S2 row with q >= r^{0.2} -> stays open with that row as the step.

**AUD-5 open_unexamined: first step.**

n/a for this disposition.

**AUD-6 obstruction as hypothesis.**

n/a for this disposition.

*Proposed change:* disposition conditional close

## LEAD-RHO-cheon-toy-reproduction

- Title: Toy reproduction of Cheon's algorithm with memory charged and supplied-input CRT composition
- Disposition: `open_next_step`; file `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/generic/LEAD-RHO-cheon-toy-reproduction.yaml`
- next_action.step (verbatim): "Run EXP-AUXIN-25a29a (H-AUXIN-a86953: 56-bit r, divisor 65536, stage counts and gain fractions) end to end with recovered scalars certified and memory/DP costs reported beside rho on the same group."
- next_action.discriminates (verbatim): "Measured sqrt(r/d) + sqrt(d) within a small constant of the closed form closes the reproduction as closed_known; a large memory-charged excess re-prices Cheon's deployed frontier."
- forecloses: "reproduce Cheon at toy scale"; "planted-divisor curve"; "Cheon with memory charged"; "CRT of supplied Cheon residues"

**AUD-1 revisit triggers.**

n/a for this disposition.

**AUD-2 scope.**

n/a for this disposition.

**AUD-3 measured/cost_model to proof.**

n/a for this disposition.

**AUD-4 open_next_step/open_blocked: theorem vs experiment.**

Defect in the queued step. `next_action.step` says "Run EXP-AUXIN-25a29a (H-AUXIN-a86953: 56-bit r, divisor 65536, stage counts and gain fractions) end to end with recovered scalars certified and memory/DP costs reported beside rho". The hypothesis file (ledger/hypotheses/H-AUXIN-a86953.yaml) says "No curve is built", its mechanism says "It does not build a curve and it does not run a walk", and its method_ceiling is "The stage counts and the signed gaps. Not a measured walk constant and not an attack cost." The statement is integer arithmetic ("The square root of 65536 is 256. Twice 256 is 512 ..."). EXP-AUXIN-25a29a therefore cannot produce either outcome in `discriminates`.

Theorem route for the re-pricing question: a memory-charged constant c multiplies Cheon's cost and moves the deployed exponent by only log c / log r (about 0.04 for c = 1000 at 256 bits), so no toy constant can re-price the deployed frontier by more than that; the deployed verdict is decided by the supply bound under LEAD-RHO-cheon-deployed-applicability. Cheon's algorithm itself is literature (KN-LIT-6736, solved at 160 bits).

Proposed change: replace the step with a hypothesis that actually runs Cheon on a planted-divisor curve, or close the lead closed_known (KN-LIT-6736) with revisit_when "a deployed row whose verdict depends on a constant factor > r^{0.04}". Outcome map stays as written for a real run.

**AUD-5 open_unexamined: first step.**

n/a for this disposition.

**AUD-6 obstruction as hypothesis.**

n/a for this disposition.

*Proposed change:* next_action points at arithmetic-only hypothesis

## LEAD-RHO-correlated-walks-shared-sums

- Title: Correlated walks: one shared index sequence or shared precomputed sums across walks
- Disposition: `closed_obstructed`; file `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/generic/LEAD-RHO-correlated-walks-shared-sums.yaml`
- obstruction.kind: `proof`
- obstruction.statement (verbatim): "With a shared index sequence every walk adds the same R_i at every step, so pairwise differences P_i - P_j are invariant and two walks can never meet unless they started equal; measured 0.073x [0.070, 0.076] (176/1000 censored, a lower bound on the loss). A pair table still costs one addition per step: 1.027 [0.982, 1.073]. Changing the representative rule per epoch breaks walk determinism: 0.83x [0.79, 0.87], worse than no negation map. Scope: any parallel rho."
- obstruction.revisit_when (verbatim): "A sharing scheme that keeps walks a deterministic function of the point while saving additions (not just table lookups)."
- forecloses: "walks share one index sequence"; "shared precomputed sums across walks"; "pair table R_i + R_j steps"; "per-epoch class rule rotation"

**AUD-1 revisit triggers.**

Not fired. Nothing in delta.txt proposes a point-deterministic sharing scheme that saves additions (fold-car-decisions.md lists this lead only in --match tables, with no folded record).

**AUD-2 scope.**

Precision defect in the proof statement. "With a shared index sequence every walk adds the same R_i at every step, so pairwise differences P_i - P_j are invariant and two walks can never meet unless they started equal" holds only at equal step index. Two walks can coincide at different indices (P_i(t) = P_j(t') with t != t'); because the index is a function of time, not of the point, they then diverge, so the meeting never merges trails and is detected only if the meeting point itself is stored. The measured 0.073x with "176/1000 trials censored" (crypto research/rho_walk_leads_20261014/README.md, row 3) shows that solves still occur, which is consistent with such meetings (the harness detection path was not read), which the phrase "can never meet" does not allow. Proposed rewording: "never merge; a meeting at different step indices is detected only if the meeting point is a stored point".

Kind mismatch: the kind is `proof`, but the pair-table figure (1.027 [0.982, 1.073]) and the per-epoch rule (0.83x) are measurements; `forecloses` "pair table R_i + R_j steps" and "per-epoch class rule rotation" rest on those measurements (the pair-table one also on the one-addition-per-step argument). The proof covers the shared-index mechanism; it extends to any shared affine schedule P -> a_t P + c_t with a_t a unit mod r (differences are multiplied by a_t and never vanish).

**AUD-3 measured/cost_model to proof.**

n/a for this disposition. (kind proof)

**AUD-4 open_next_step/open_blocked: theorem vs experiment.**

n/a for this disposition.

**AUD-5 open_unexamined: first step.**

n/a for this disposition.

**AUD-6 obstruction as hypothesis.**

SO-WALK (this lead). The obstructing quantity is merging: trails meet only if the iteration is a deterministic function of the point. Taking non-merging as a hypothesis gives the store-all regime: a time-indexed shared schedule is a store-and-match search whose detection needs every meeting point stored, i.e. the BSGS / grumpy-giants regime (LEAD-RHO-bsgs-family-memory, LEAD-RHO-grumpy-store-all-schedules), with memory Theta(points visited). None found beyond that.

*Proposed change:* proof statement precision

## LEAD-RHO-dp-multitarget-precomputation

- Title: Distinguished points, multi-target batching and Bernstein-Lange precomputation (incumbent controls)
- Disposition: `closed_known`; file `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/generic/LEAD-RHO-dp-multitarget-precomputation.yaml`
- obstruction.kind: `literature`
- obstruction.statement (verbatim): "Known (KR-RHO-6239aa, KR-RHO-7d93f6, KR-RHO-46c2c6, KR-RHO-ea34b8) and reproduced as controls: at equal or smaller advice Bernstein-Lange rho solves a fresh Koblitz target 50-500x faster online than compact-orbit IC at n = 41, 53, 61 (09-equal-advice); precomputed rho is faster in every matched N83 pair (3.74x-395x); lazy DP test 0.998 [0.995, 1.001]; Kuhn-Struik is the repository's multi-target margin rule. T^2 S = Theta(C^2 N) bounds many-collision tradeoffs."
- obstruction.revisit_when (verbatim): "A table or batch scheme that beats the Bernstein-Lange l^{1/3}/l^{2/3} tradeoff or the sqrt(2Ln) batch law (variants are LEAD-RHO-advice-table-variants)."
- forecloses: "distinguished point memory tradeoff"; "multi-target rho amortisation"; "Kuhn-Struik batch rho"; "Bernstein-Lange precomputed table"; "online cost with advice"; "lazy reduction before DP check"

**AUD-1 revisit triggers.**

Not fired. Delta items mapped here by fold-car-decisions.md (C-12: DEC-20261018-8e211e, -16581f, -3fd5b1, -b3861f, -d763f3; EXP-ECDLP-c9c5a4, -30277c, -3365b4) are custody records for a finite cover worksheet ("knowledge_promotion.not_warranted; no hypothesis or goal status moved"). None beats the Bernstein-Lange tradeoff or the sqrt(2Ln) batch law.

**AUD-2 scope.**

No overreach: the phrases name the KR-RHO-6239aa / -46c2c6 / -ea34b8 / -7d93f6 mechanisms. The KR-RHO-7d93f6 bound is cited here for many collisions, which is its correct scope.

**AUD-3 measured/cost_model to proof.**

n/a for this disposition. (kind literature)

**AUD-4 open_next_step/open_blocked: theorem vs experiment.**

n/a for this disposition.

**AUD-5 open_unexamined: first step.**

n/a for this disposition.

**AUD-6 obstruction as hypothesis.**

None found (not an SO-coded obstruction).

*Proposed change:* none

## LEAD-RHO-ecc2k130-gpu-fpga-throughput

- Title: ECC2K-130 kernel throughput on GPU and FPGA (iterations per second per device and per watt)
- Disposition: `open_next_step`; file `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/generic/LEAD-RHO-ecc2k130-gpu-fpga-throughput.yaml`
- next_action.step (verbatim): "Build and pair TABLE_PHASE_POPC (phase via popc planes, CHEAPER-SELECTION.md) against the 15.88 B/s sigma-table control on one RTX PRO 6000, with identical sorted DP corpora and the 300-report re-walk gate."
- next_action.discriminates (verbatim): "A promoted gain moves the ALU-bound kernel (91% ALU busy, speed of light 27.4 B/s for its CLMADs) toward the 26 B/s goal; a null with the ALU pipe saturated leaves only logic-instruction cuts and FPGA as levers."
- forecloses: "faster ECC2K-130 GPU kernel"; "FPGA ECC2K-130 walk"; "26 B/s goal"; "bitsliced normal-basis rho throughput"

**AUD-1 revisit triggers.**

n/a for this disposition.

**AUD-2 scope.**

n/a for this disposition.

**AUD-3 measured/cost_model to proof.**

n/a for this disposition.

**AUD-4 open_next_step/open_blocked: theorem vs experiment.**

No theorem decides a kernel rate. The roofline (crypto ecc2k130/ROOFLINE.md: ALU 91% busy, speed of light 27.4 B/s for its CLMADs) already bounds what TABLE_PHASE_POPC can give: at most 27.4/15.884 = 1.73x on the CLMAD-bound path. No change. Delta: the fold (fold-cryptanalysis-ecc.md R12) found only a pointer migration of the paper PDF.

**AUD-5 open_unexamined: first step.**

n/a for this disposition.

**AUD-6 obstruction as hypothesis.**

n/a for this disposition.

*Proposed change:* none

## LEAD-RHO-ecc2k130-iteration-function

- Title: ECC2K-130 iteration function: sigma walk vs v3 table walk vs class-signed sigma steps
- Disposition: `open_next_step`; file `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/generic/LEAD-RHO-ecc2k130-iteration-function.yaml`
- next_action.step (verbatim): "Measure the v3 table-walk kernel's paired rate on the RTX PRO 6000 against the fused sigma-table control (five alternating pairs, A/A drift), plus a planted-log and re-walk gate, then price iterations x rate per solve for sigma, SIGMA_SIGN=2 and table-v3."
- next_action.discriminates (verbatim): "If table-v3 loses < 14-19% rate the switch pays (projected 0.81-0.86x cost per solve) and the campaign owner decides; a larger loss leaves sigma (+ optionally SIGMA_SIGN=2, ~0.96-0.97x) as the walk."
- forecloses: "switch ECC2K-130 to the table walk"; "signed sigma step R - sigma^j R"; "ECC2K-130 walk constant"; "Frobenius table walk fruitless cycles"

**AUD-1 revisit triggers.**

n/a for this disposition.

**AUD-2 scope.**

n/a for this disposition.

**AUD-3 measured/cost_model to proof.**

n/a for this disposition.

**AUD-4 open_next_step/open_blocked: theorem vs experiment.**

No theorem decides a device rate; the walk constants are already measured (crypto ecc2k130/WALK-CONSTANT.md). The step is a single paired rate measurement and is the fastest decider. No change.

**AUD-5 open_unexamined: first step.**

n/a for this disposition.

**AUD-6 obstruction as hypothesis.**

n/a for this disposition.

*Proposed change:* none

## LEAD-RHO-generic-sqrt-lower-bound

- Title: Beat the square-root exponent with any generic collision algorithm
- Disposition: `closed_obstructed`; file `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/generic/LEAD-RHO-generic-sqrt-lower-bound.yaml`
- obstruction.kind: `theorem`
- obstruction.statement (verbatim): "Shoup/Nechaev generic-group lower bound: any generic algorithm needs Omega(sqrt r) group operations for a prime-order-r group (KR-RHO-13bf67). Every lead in this family moves only the constant (automorphism classes divide it by sqrt|Aut|, KR-RHO-0528e7). Scope: all generic algorithms, any field, any r."
- obstruction.revisit_when (verbatim): "Never for generic algorithms; only a method that reads the representation (index calculus, transfer) can change the exponent."
- forecloses: "sub-square-root generic algorithm"; "beat sqrt(r) with a smarter walk"; "generic collision search below the birthday bound"; "new exponent from rho engineering"

**AUD-1 revisit triggers.**

Not fired. revisit_when says never for generic algorithms. Delta adds KN-OPEN-005 and KN-OPEN-010 reconciliation notes (2026-10-18), which stay `open` and concern non-generic representations.

**AUD-2 scope.**

Two overreaches.

(1) `forecloses` "beat sqrt(r) with a smarter walk" and "new exponent from rho engineering" are wider than the theorem's scope "all generic algorithms". A walk whose iteration reads algebraic structure of the coordinates is not generic and is exempted by the lead's own revisit_when ("only a method that reads the representation ... can change the exponent"). Proposed phrases: "beat sqrt(r) with a smarter generic walk (iteration treats the encoding as random)".

(2) The statement says "Every lead in this family moves only the constant". LEAD-RHO-non-automorphism-equivalence (open_unexamined) has a non-generic half: H-EWALK-29cb90 says an encoding-level H-invariant at h ~ N^{1/3} would give N^{1/3} and "the generic-group bound does not forbid it because such an invariant is non-generic by construction". Proposed: "Every generic lead in this family ...".

Observation: best_measured "bsgs.negation 0.529 [0.485, 0.596]" is the v1 interval; the v2 bound `ECBND1h9d01a5c2ae56` reads 0.529 [0.486, 0.595] (FRONTIER prime toy). The id-drift edits are already in fold-crypto.md 2.2b and are not repeated here.

**AUD-3 measured/cost_model to proof.**

n/a for this disposition. (kind theorem)

**AUD-4 open_next_step/open_blocked: theorem vs experiment.**

n/a for this disposition.

**AUD-5 open_unexamined: first step.**

n/a for this disposition.

**AUD-6 obstruction as hypothesis.**

SO-GEN (this lead). Theories that take the sqrt(r) generic floor as a hypothesis and price an extra resource: (a) preprocessing/advice, S*T^2 = Omega~(eps*N) (KN-LIT-013; KR-RHO-ea34b8); (b) auxiliary input (Cheon; SO-CHEON); (c) multi-instance amortisation sqrt(2Ln) (KR-RHO-46c2c6); (d) low-entropy or interval secrets (KR-RHO-898783; the LHW leads); (e) the contrapositive screen: a sub-sqrt algorithm must use a non-random property of the encoding, which is the GGM-simulability screen of KN-OPEN-005 (H-GGM-001 `analyzed`). (e) is the only one that targets the exponent of single-target ECDLP.

*Proposed change:* forecloses + family-scope sentence

## LEAD-RHO-grumpy-store-all-schedules

- Title: Exact average-case constant of store-all generic schedules (grumpy giants, compiled tiered walks)
- Disposition: `open_next_step`; file `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/generic/LEAD-RHO-grumpy-store-all-schedules.yaml`
- next_action.step (verbatim): "Run EXP-GRUMPY-eb8675 (certified exhaustive ladder, Z/l from 2^10 to 2^20, covered-set counter against per-target simulation, negation map as a separate arm) and file the evidence record for EXP-GRUMPY-cd7b82's Stage 1."
- next_action.discriminates (verbatim): "A certified constant below bsgs.negation's 1.10x floor (per-op) would be a new ops leader for store-all schedules at toy scale; it cannot beat rho at cryptographic size because memory stays Theta(sqrt l) (LEAD-RHO-bsgs-family-memory)."
- forecloses: "grumpy giants constant"; "two grumpy giants and a baby"; "three-class coverage floor"; "Bellman certificate for giant schedules"; "compiled reservoir-guided rho schedule"

**AUD-1 revisit triggers.**

n/a for this disposition.

**AUD-2 scope.**

n/a for this disposition.

**AUD-3 measured/cost_model to proof.**

n/a for this disposition.

**AUD-4 open_next_step/open_blocked: theorem vs experiment.**

The queued ladder certifies finite-l constants; it cannot change any disposition beyond toy scale (the lead's own discriminates: memory stays Theta(sqrt l)). The asymptotic average-case constant of a store-all schedule is the limit of |C_n|/l as a function of n/sqrt(l). Under H-GRUMPY-1ead49's statement ("C_n ... is a union of three explicit interval systems"), that limit is an integral computable in closed form, so a derivation decides the asymptotic constant faster than extending the ladder to 2^20. Comparison caveat: the discriminator compares against bsgs.negation's 1.10x (A = 2 floor); the grumpy arm must be compared at the same A (the lead lists the negation map as a separate arm, which is the right control).

Lean target candidate: H-GRUMPY-1ead49's target-independence (the solved set after n additions is a fixed subset of Z/l, so the mean success is |C_n|/l exactly).

**AUD-5 open_unexamined: first step.**

n/a for this disposition.

**AUD-6 obstruction as hypothesis.**

n/a for this disposition.

*Proposed change:* derive asymptotic constant

## LEAD-RHO-kangaroo-interval

- Title: Kangaroo / lambda (van Oorschot-Wiener, Gaudry-Schost) as a full-group ECDLP solver
- Disposition: `closed_dominated`; file `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/generic/LEAD-RHO-kangaroo-interval.yaml`
- obstruction.kind: `measured`
- obstruction.statement (verbatim): "On every sealed domain kangaroo.vow is dominated on ops and memory: prime toy 2.203 [1.803, 2.527] x floor vs rho.negation 1.453; Koblitz medium 15.558 [13.742, 17.597] vs signed-Frobenius rho 1.188; constants match the literature (KR-RHO-898783). Scope: full-group single target; interval DLP is the kangaroo's own domain and is not an ECDLP improvement."
- obstruction.revisit_when (verbatim): "A target with a known short interval or low-entropy secret (LHW leads)."
- forecloses: "kangaroo for full ECDLP"; "Pollard lambda constant"; "four-kangaroo method"; "Gaudry-Schost on the whole group"

**AUD-1 revisit triggers.**

Not fired for full-group ECDLP. The trigger "A target with a known short interval or low-entropy secret (LHW leads)" names a domain, not an event; the LHW leads already use kangaroo as their incumbent (H-LHW-371a91 title: "the guess-and-kangaroo family ... is dominated by min(kangaroo, brute force)"). Proposed: replace with "a full-group method with an interval-style constant below rho.negation's".

**AUD-2 scope.**

Measured scope vs forecloses: the measured arm is kangaroo.vow only; `forecloses` also covers "four-kangaroo method" and "Gaudry-Schost on the whole group", which were not measured. KR-RHO-898783 covers them by literature: four-kangaroo about 1.71 sqrt(N), Gaudry-Schost about 1.66 sqrt(N), with negation about 1.36 sqrt(N), all above rho.negation's sqrt(pi r/4) = 0.886 sqrt(r) (heuristic). Also: FRONTIER prime toy lists the 6-size kangaroo bound `ECBND1h2e9e2024d8f3` as dominated by the rho.plain bounds `ECBND1h760ed0d9277e`, `ECBND1h7842836dcaad`, not by a rho.negation bound; `dominated_by: LEAD-RHO-negation-map-fruitless-cycles` stays true by literature but is not what FRONTIER prints.

**AUD-3 measured/cost_model to proof.**

Kind measured. A short argument replaces it: change obstruction.kind to literature, citing KR-RHO-898783 (best interval constant with negation 1.36 sqrt(N) at N = r) against KR-RHO-fb88e6 / KR-RHO-6239aa (rho.negation about 0.886 sqrt(r)). The rho constant is heuristic (random mapping), so the comparison is not a theorem; KR-RHO-93979e gives rigorous rho bounds only up to a sqrt(log|G|) factor for additive walks. Lean target: none worth formalising (the comparison is arithmetic on literature constants).

**AUD-4 open_next_step/open_blocked: theorem vs experiment.**

n/a for this disposition.

**AUD-5 open_unexamined: first step.**

n/a for this disposition.

**AUD-6 obstruction as hypothesis.**

None found (not an SO-coded obstruction). Its obstructing quantity (2 sqrt(N) on width N) is the hypothesis of the interval/low-entropy theory owned by the LHW leads.

*Proposed change:* obstruction kind measured -> literature

## LEAD-RHO-lhw-modular-filter-price

- Title: Residue-guess price of modular (mod-M) representation filters in prime-order groups
- Disposition: `open_next_step`; file `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/generic/LEAD-RHO-lhw-modular-filter-price.yaml`
- next_action.step (verbatim): "Run EXP-LHW-9adf78 (residue-guess price on W(m, w) with Mersenne/Fermat M) or write the proof obligation of H-LHW-371a91 as a checked derivation."
- next_action.discriminates (verbatim): "A proved G_M multiplier closes representation filters for the group LHW-DLP as closed_obstructed (proof); a counterexample filter is a new LHW lead."
- forecloses: "modular filter for low-weight DLP"; "representation technique in a prime-order group"; "Schroeppel-Shamir for low Hamming weight"; "residue guess multiplier"

**AUD-1 revisit triggers.**

n/a for this disposition.

**AUD-2 scope.**

n/a for this disposition.

**AUD-3 measured/cost_model to proof.**

n/a for this disposition.

**AUD-4 open_next_step/open_blocked: theorem vs experiment.**

Theorem route. H-LHW-371a91 (approved) defines the class: "F_M is the class of algorithms that compute only [a]P and Q - [b]P with a, b known and keep a b-side candidate only if b = tau (mod M) for a supplied residue tau". Under that definition Lemma 1's multiplier is close to definitional; the content is Theorem 3 (Mersenne and Fermat moduli) and Conjecture 4 (all other odd M).

Theorem 3's counting step is short and decides the Mersenne/Fermat half without EXP-LHW-9adf78: for M = 2^k - 1 or 2^k + 1, distinct k-bit integers of weight w are distinct residues mod M (all are < M, except 2^k - 1 itself when w = k), so G_M >= C(k, w); concavity of L(kappa) = kappa H(alpha/kappa) + (1 - kappa)/2 on [1.124 alpha, 1] gives log2 C_M >= min(m/2, log2|W|) - O(log m).

Lean target: "For k >= w >= 1 and M in {2^k - 1, 2^k + 1} with w < k, the map {x < 2^k : popcount x = w} -> Z/M, x -> x mod M is injective; hence |rho_M(W(m,w))| >= C(k, w) for m >= k."

Outcome map: Theorem 3 checked -> closed_obstructed (proof) for Mersenne/Fermat folds; Conjecture 4 still needs the exhaustive D_M measurement (or an equidistribution bound for weight-w integers mod M with ord_M(2) >= m), so the lead stays open_next_step for other M.

**AUD-5 open_unexamined: first step.**

n/a for this disposition.

**AUD-6 obstruction as hypothesis.**

n/a for this disposition.

*Proposed change:* Lean target + split

## LEAD-RHO-lhw-polymem-collision-walks

- Title: Low-Hamming-weight DLP with polynomial memory: collision walks on the weight-w class
- Disposition: `open_next_step`; file `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/generic/LEAD-RHO-lhw-polymem-collision-walks.yaml`
- next_action.step (verbatim): "Re-run EXP-LHW-b49bc6 Stage 1 (hash-realisable jump sums on the frozen (m, w) ladder, m in {20, 24}) with checkpointed sumset counts and a run length inside the claim TTL; score E1 vs E2."
- next_action.discriminates (verbatim): "E1 (Def ratio <= 2000 millirho at all T >= 64) supports a polymem walk near the MITM bound at toy m; E2 (>= 8000 and rising) shows the fibre deficit grows and the walk family cannot reach sqrt(binom(m, w))."
- forecloses: "low Hamming weight discrete log with polynomial memory"; "fibre-surplus law"; "carry-run mixture representations"; "jump-sum walk on weight-w exponents"

**AUD-1 revisit triggers.**

n/a for this disposition.

**AUD-2 scope.**

n/a for this disposition.

**AUD-3 measured/cost_model to proof.**

n/a for this disposition.

**AUD-4 open_next_step/open_blocked: theorem vs experiment.**

Conditional prediction from the parallel-collision-search analysis (van Oorschot-Wiener golden collision, as summarised in KR-RHO-6239aa / KR-RHO-7d93f6): a hashed split walk f: W' -> W' collides mostly through hash collisions of distinct points; only point equalities across branches (the representations x = z1 + z2, R of them) are useful. With memory w the expected cost scales as about sqrt(|W'|^3 / w) / sqrt(R) rather than sqrt(|W|). This predicts the "fibre deficit grows" outcome E2 unless R is large. The experiment stays (it measures the constant at toy m), but the prediction curve should be pre-registered beside E1/E2. Observation: EV-LHW-9ca475 Stage 1 is `claim_expired, not negative`, so no outcome exists yet.

**AUD-5 open_unexamined: first step.**

n/a for this disposition.

**AUD-6 obstruction as hypothesis.**

n/a for this disposition.

*Proposed change:* none

## LEAD-RHO-lhw-preprocessing-frontier

- Title: Low-weight DLP with preprocessing: the (P, S, T, epsilon, U) frontier
- Disposition: `open_unexamined`; file `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/generic/LEAD-RHO-lhw-preprocessing-frontier.yaml`
- next_action.step (verbatim): "Price the two incumbent rows of IDEA-20260930-79abd9 (Coppersmith-split advice tables and a weight-restricted BL table) in group operations at m in {32, 40} and measure one with planted low-weight logs."
- next_action.discriminates (verbatim): "A frontier point below both incumbents is a new LHW preprocessing lead; matching them closes it as closed_known."
- forecloses: "low-weight DLP with preprocessing"; "Coppersmith split advice table"; "weight-restricted precomputation"

**AUD-1 revisit triggers.**

n/a for this disposition.

**AUD-2 scope.**

n/a for this disposition.

**AUD-3 measured/cost_model to proof.**

n/a for this disposition.

**AUD-4 open_next_step/open_blocked: theorem vs experiment.**

n/a for this disposition.

**AUD-5 open_unexamined: first step.**

Observation: the only follow-up is H-LHW-c72fa4, whose title is "One half exceeds 4999/10000 by 1/10000" (an arithmetic contract, not evidence).

First discriminating step (desk): derive whether the Corrigan-Gibbs-Kogan compression argument (KN-LIT-013, S*T^2 = Omega~(eps*N) for prime-order N) extends to targets uniform on a subset W of Z/N, giving S*T^2 = Omega~(eps*|W|) for T >= 1. The Bernstein-Lange table restricted to W (l^{1/3} online after l^{2/3} precomputation, KR-RHO-ea34b8, with l = |W|) meets that curve. Outcome map: bound proved -> closed_obstructed (proof) for generic algorithms, with the BL-restricted row as the tight incumbent; bound fails (a generic algorithm below it on W) -> new lead; derivation unfinished -> keep the lead's pricing step.

**AUD-6 obstruction as hypothesis.**

n/a for this disposition.

*Proposed change:* first step: CGK-on-subsets derivation

## LEAD-RHO-matched-rho-calibration

- Title: The matched rho reference itself: finite-size bias and the missing prime medium tier
- Disposition: `open_next_step`; file `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/generic/LEAD-RHO-matched-rho-calibration.yaml`
- next_action.step (verbatim): "Seal ecbench bounds for rho.negation, rho.plain and bsgs.negation on prime curves at log2 r 32-48 (the Koblitz medium-tier ladder's sizes), >= 24 runs per size, with replay certificates and the section 5a band, and fit R(N) = 1 + c/N^beta to the toy-to-medium ratio (H-ECDLP-ff38dc)."
- next_action.discriminates (verbatim): "If medium-tier rho.negation lands within 1.10x of sqrt(pi/4) the toy excess is set-up and every prime gap shrinks by the toy factor; a persistent 1.3-1.5x would point to a real walk shortfall (reopen LEAD-RHO-negation-map-fruitless-cycles)."
- forecloses: "calibrate the charged rho baseline"; "rho finite-size bias law"; "medium-tier prime rho bound"; "coefficient of variation of matched rho"

**AUD-1 revisit triggers.**

n/a for this disposition.

**AUD-2 scope.**

n/a for this disposition.

**AUD-3 measured/cost_model to proof.**

n/a for this disposition.

**AUD-4 open_next_step/open_blocked: theorem vs experiment.**

Two derivation-level points decide parts of the queued step.

(a) The threshold. The step's discriminator is "within 1.10x of sqrt(pi/4)". KR-RHO-fb88e6 records "measured 0.947*sqrt(2) on P-256 (Bos-Costello-Miele 2014)", which corresponds to about 1/0.947 = 1.056 x the A = 2 floor at cryptographic size, before any r-adding penalty (KR-RHO-cd86f5) and before the 1 + Theta(1/sqrt(r)) negation overhead of KN-LIT-c8e485 (Bernstein-Lange-Schwabe). The expected asymptote is therefore near 1.06-1.10, and an outcome of 1.10-1.15 would be consistent with literature rather than a walk shortfall. Proposed: pre-register the asymptote predicted for the implementation's r-adding size and escape rule, and read the outcome against that prediction instead of 1.10.

(b) Existing data. crypto docs/ic/LEADERBOARD.md Table B already lists matched rho.negation references (S, reference, about 24 runs per row per research/ic_validation_gate_20261024/README.md's 312 recorded seeds over 13 rows) at 8 prime sizes: S/0.886 = 4.06, 3.22, 2.29, 1.96, 1.64, 1.46, 1.38, 1.17 at log2 r = 9.7, 11.9, 14.0, 16.0, 18.0, 20.0, 21.7, 23.4. A fit of R(N) = 1 + c/N^beta to these rows is a zero-compute first step (descriptive; the rows are not a sealed ecbench bound).

Fold note: fold-crypto.md 2.2a proposes the v2 alpha interval [0.315, 0.475] for best_measured; not repeated.

**AUD-5 open_unexamined: first step.**

n/a for this disposition.

**AUD-6 obstruction as hypothesis.**

n/a for this disposition.

*Proposed change:* next_action threshold + zero-compute fit

## LEAD-RHO-native-step-cost

- Title: Native cost of one rho step: canonicalisation, field arithmetic and admitted CPU timing
- Disposition: `open_next_step`; file `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/generic/LEAD-RHO-native-step-cost.yaml`
- next_action.step (verbatim): "Price the Koblitz canonicaliser in field-multiplication equivalents: run EXP-CERTBIN-b4d29c (design C canonicalising every step vs Bailey sigma walk normalising only at DPs) at n = 131 and the rotation-invariant polynomial key of IDEA-20261015-2d8e5a, with callgrind Ir (no PMU needed)."
- next_action.discriminates (verbatim): "If canonicalisation stays > 2x the ~6-7 multiplication floor, Koblitz rho constants in GAE understate native cost and the section 5a band must price it; if it falls near the floor the GAE constant is native."
- forecloses: "cheaper canonicalisation for Koblitz rho"; "instructions per rho step"; "branch-free field arithmetic for rho"; "Bailey walk normalises only at distinguished points"

**AUD-1 revisit triggers.**

n/a for this disposition.

**AUD-2 scope.**

n/a for this disposition.

**AUD-3 measured/cost_model to proof.**

n/a for this disposition.

**AUD-4 open_next_step/open_blocked: theorem vs experiment.**

Theorem route for the intrinsic part. Canonicalising a normal-basis Koblitz x-coordinate under the m rotations is the least-rotation problem, solvable in O(m) bit comparisons (Booth's algorithm), which is below one field multiplication for m = 131. The negation choice is one more comparison. So the intrinsic canonicalisation cost is far below the ~6-7 multiplication floor; a measured cost above 2x the floor is implementation overhead, not a property of the class walk. The lead's own step names the alternative design ("Bailey sigma walk normalising only at DPs"), which avoids per-step canonicalisation. The Booth least-rotation claim is reviewer-supplied and not in the KN-LIT store. Outcome map: unchanged, but the "> 2x floor" outcome should be read as an engineering gap, not as "GAE understates native cost" in principle.

Delta: benchmarks/20261022-strong-rho-batchinv (707.2 -> 679.7 instructions/step at n = 53, native not established; fold-crypto.md 2.1b) and cryptanalysis docs/sixclass-20261024 (six-class j = 0 wall time 1.257x and 1.826x the default, toy, no CI) are native-cost evidence for this lead. The sixclass record's own "Suspected explanation" is "Extra canonicalization, DP management and short-cycle work may outweigh a quotient gain on this curve".

**AUD-5 open_unexamined: first step.**

n/a for this disposition.

**AUD-6 obstruction as hypothesis.**

n/a for this disposition.

*Proposed change:* none

## LEAD-RHO-negation-map-fruitless-cycles

- Title: Negation-map rho on {+-P} classes with fruitless-cycle escape (prime curves)
- Disposition: `closed_known`; file `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/generic/LEAD-RHO-negation-map-fruitless-cycles.yaml`
- obstruction.kind: `literature`
- obstruction.statement (verbatim): "Known: the sqrt(2) gain and fruitless-cycle handling are established (KR-RHO-fb88e6). The program reproduced the gain: on prime toy curves (log2 r 15.7-25.3) rho.negation measures 1.453 [1.184, 1.772] x sqrt(pi/4) against rho.plain 1.920 [1.633, 2.221] (ratio 0.757 vs ideal 0.707); fruitless 2-cycle rate 487 per 1e6 steps against 1/(2r) = 488 (rho_walk_leads lead 4); collab dead trails fixed 50->1 (generic_dlp_correctness). Nothing new remains in the mechanism; the remaining ~7% toy shortfall is a calibration question (LEAD-RHO-matched-rho-calibration)."
- obstruction.revisit_when (verbatim): "A medium-tier (log2 r >= 32) prime rho.negation bound shows a gain over rho.plain below 1.30 with disjoint CIs, or a new escape rule beats the literature constant."
- forecloses: "negation map sqrt(2) speedup"; "fruitless cycle escape rule"; "walk on x-coordinate classes"; "change the class representative rule each round"; "negation map becomes a net loss"

**AUD-1 revisit triggers.**

Not fired. FRONTIER (crypto docs/bounds/FRONTIER.md) has three domains: Koblitz toy, Koblitz medium, prime toy. There is still no prime medium-tier bound, and no new escape rule is recorded in delta.txt.

**AUD-2 scope.**

Overreach: `forecloses` "negation map becomes a net loss". The closure's evidence is counted steps on prime toy curves. Literature makes the net gain depend on the jump-table size and the cycle handling: KN-LIT-c8e485 says "negation costs a factor 1 + Theta(1/sqrt(r))", and KR-RHO-fb88e6 gives "Best practical gain was 1.29 (Bos-Kleinjung-Lenstra 2010)". KR-RHO-fb88e6's internal note on EXP-RHO-60da4f reads "every configuration lost to plain rho (affine steps, memoryless escapes); unreviewed". The ecc-challenges walk 4 uses 32 jumps plus an escape jump (docs/multicurve-storage.md). Proposed phrase: "negation map becomes a net loss in counted steps with large r and cycle reduction"; native-time net loss belongs to LEAD-RHO-native-step-cost and LEAD-RHO-pool-class-quotient.

**AUD-3 measured/cost_model to proof.**

n/a for this disposition. (kind literature)

**AUD-4 open_next_step/open_blocked: theorem vs experiment.**

n/a for this disposition.

**AUD-5 open_unexamined: first step.**

n/a for this disposition.

**AUD-6 obstruction as hypothesis.**

None found (not an SO-coded obstruction).

*Proposed change:* forecloses narrowing

## LEAD-RHO-non-automorphism-equivalence

- Title: Equivalence classes larger than Aut(E): quotients by subgroups H of (Z/N)^*
- Disposition: `open_unexamined`; file `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/generic/LEAD-RHO-non-automorphism-equivalence.yaml`
- next_action.step (verbatim): "Prove or refute H-EWALK-29cb90's per-step canonicalisation bound: show that for h = |H| > 6 on ordinary prime-field curves any canonicaliser costs Omega(log h) group operations per step (charged gain <= 1), and search the encoding for a non-constant H-invariant at h ~ N^{1/3} on toy curves (exhaustive at N < 2^20)."
- next_action.discriminates (verbatim): "A cost bound closes the lead as closed_obstructed (cost_model); a cheap invariant at any h > 6 would be a new constant-or-better lead and a non-generic structure worth a full experiment."
- forecloses: "quotient rho by multiplier subgroup"; "equivalence classes beyond automorphisms"; "H-invariant of the point encoding"; "N^{1/3} rho with free canonicalisation"

**AUD-1 revisit triggers.**

n/a for this disposition.

**AUD-2 scope.**

n/a for this disposition.

**AUD-3 measured/cost_model to proof.**

n/a for this disposition.

**AUD-4 open_next_step/open_blocked: theorem vs experiment.**

n/a for this disposition.

**AUD-5 open_unexamined: first step.**

Proposed split, with a closure for the generic half.

Defect in the queued proof target: the step asks to "show that ... any canonicaliser costs Omega(log h) group operations per step (charged gain <= 1)". Omega(log h) per step against a sqrt(h) step saving gives a charged gain of about sqrt(h)/log h > 1, so that bound would not close the lead.

Generic half (closure by SO-GEN): H-EWALK-29cb90 derives that free canonicalisation (or a free H-invariant with multiplicative steps) at h = N^{1/3} gives total N^{1/3}. For a generic canonicaliser that would contradict Shoup's Omega(sqrt N) bound (KR-RHO-13bf67), so any generic per-step canonicaliser must cost enough that the charged total is >= Omega(sqrt N): with walk cost sqrt(N/h)*c(h) and disambiguation about h*log2 N, Shoup forces c(h) >= about sqrt(h) whenever h*log2 N < sqrt(N). This reduction inherits the random-mapping heuristic for the class walk, so it is a heuristic-conditional closure, not a theorem about all generic algorithms. A direct form: a generic H-invariant F with small collision probability must, on inputs P and [h]P, query a common group element for every h in H, which forces its multiplier set A to satisfy A*A^{-1} covering H, so |A| >= sqrt(|H|) and the per-step cost is >= sqrt(h), which cancels the sqrt(h) saving.

Lean target candidate (combinatorial core): "For a finite group K and subsets A of K, H of K with H contained in {a b^{-1} : a, b in A}, |A|^2 - |A| + 1 >= |H|."

Non-generic half (stays open): an encoding-level invariant is outside SO-GEN. Reviewer remark (conditional): a non-constant rational function f with f([h]P) = f(P) on G must contain each H-orbit in a fibre, so deg f >= |H|; this does not bound evaluation cost (x([m]P) has degree m^2 and costs O(log m)), so it is not a closure. The lead's exhaustive toy search for an H-invariant of the encoding remains the discriminating step; link it to KN-OPEN-005.

Outcome map: generic half -> closed_obstructed (theorem, SO-GEN); toy search finds no invariant of degree <= D at N < 2^20 -> exhausted_at_scale for the encoding half with that D; an invariant found -> open_next_step with a full experiment.

**AUD-6 obstruction as hypothesis.**

Not an SO-coded obstruction, but generative: taking "canonicalisation must be non-generic and cheap" as a hypothesis points at endomorphisms of small degree whose eigenvalue has small order on G, the prime-field analogue of Koblitz Frobenius. Reviewer derivation (conditional, unverified): in K = Q(sqrt(-7)) with alpha = (1 + sqrt(-7))/2 of norm 2, a CM curve over F_p with Frobenius pi = 2 - alpha^k (p = Norm(2 - alpha^k) prime) has #E(F_p) = Norm(alpha^k - 1), and alpha acts on E(F_p) with order dividing k (about log2 p). Orbits would have size k, giving at most sqrt(2k) if canonicalisation were cheap; but each alpha-application is a 2-isogeny evaluation (no normal-basis rotation shortcut over F_p), so orbit canonicalisation costs about k*c_alpha per step, an expected net loss for k ~ 256. Collision check: `lead_atlas.py --match "small-degree endomorphism eigenvalue small order orbit quotient rho prime field CM"` ranks LEAD-STR-small-cm-disc-nonunit-endo first (score 18, closed_obstructed). Its revisit_when reads "Someone constructs a prime-field curve where a norm-2 or norm-3 endomorphism has eigenvalue order near log_n N (the equality case, a prime-field Koblitz analogue) and a canonical orbit representative costs o(h) maps." So this is that row's idea, not a new lead.

Observed (scratch computation, audit/generic-work/cm7_search.py and cm7_hit.txt; integer arithmetic in Z[alpha], no curve built or point counted): over k in [100, 600], both signs of alpha, pi = 1 - (alpha^k - 1) beta with Norm(beta) <= 8, and Norm(alpha^k - 1)/c prime with c <= 4, there is exactly one hit with p prime: alpha = (-1 + sqrt(-7))/2, k = 239, beta = 2 + 2 alpha, p a 243-bit prime, #E(F_p) = 8 * Norm(alpha^239 - 1) = 32 N' with N' a 238-bit prime. On the order-N' subgroup alpha has order 239 (k prime, alpha - 1 of norm 2), i.e. h = 239 against the STR row's bound h >= log2 N' (about 238): the equality case. The search's Koblitz-prime list (k = 163, 233, 283, 409, 571 among others) matches the known Koblitz orders, a positive control on the arithmetic. Interpretation (conditional): the construction half of the STR row's revisit_when is met by this instance; the second half (a canonical orbit representative in o(h) maps) is not, and the STR row's cost model sqrt(h)/(h c(alpha)) predicts a net loss. Proposed: hand this instance to the structure-family review as the test case for that second half.

*Proposed change:* disposition open_unexamined -> split (generic half closed)

## LEAD-RHO-pool-class-quotient

- Title: Distributed pool v2 walk has no class quotient: add negation (sqrt 2) and Frobenius (sqrt 2m)
- Disposition: `open_next_step`; file `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/generic/LEAD-RHO-pool-class-quotient.yaml`
- next_action.step (verbatim): "Before enabling the negation-class walk (ecc-challenges PR #56, default off): run a few hundred thousand trail starts on a real campaign curve at production DP density to measure the trap rate, test the CUDA path on a GPU, then canary it; design the Koblitz Frobenius class walk (a further sqrt(m)) per docs/negation-walk.md."
- next_action.discriminates (verbatim): "A trap rate near zero at production density lets the walk replace v2 while v2 progress is below about 0.40 E; traps would need a stronger escape before enabling."
- forecloses: "negation map in the ecc-challenges worker"; "Frobenius quotient for ECC2K-163"; "v2 walk automorphism quotient"; "speed up Certicom prime campaigns"

**AUD-1 revisit triggers.**

n/a for this disposition.

**AUD-2 scope.**

n/a for this disposition.

**AUD-3 measured/cost_model to proof.**

n/a for this disposition.

**AUD-4 open_next_step/open_blocked: theorem vs experiment.**

The step is stale. It says "Before enabling the negation-class walk (ecc-challenges PR #56, default off)". On ecc-challenges main (HEAD df8cd52): docs/multicurve-storage.md lines 45-49 "ECC2-131 and ECCp-131 register new runs under walk 4 by default (`DEFAULT_WALKS` in `multicurve/codec.py`)" and src/ecc_challenges/multicurve/codec.py:41 `DEFAULT_WALKS = {campaign: WALK_V4 for campaign in FAST_WALK_CAMPAIGNS}`. Walk 4 (`...-negmap-v4`) uses the walk-3 partition (32 jumps) plus a 33rd escape jump, and the doc says "cycle handling adds work whose cost must be measured". Evidence[4] (verification/negation-walk-20261024/README.md) and evidence[5] (docs/negation-walk.md) do not resolve on main; the only commit touching docs/negation-walk.md is 1f49962 ("Negation-class generic walk (default off)"), so both entries need a `ref:` pin. Separately, verification/rho131-nine-curve-20261023/README.md records an off-curve ECCp-131 walk-4 state on the hosted macOS x86_64 Apple Paravirtual Metal device (jobs 120789662742 and the retry 120796467229); PR #57 tests a 32-bit carry/borrow repair, so the README attributes it to the device arithmetic path, not to the class logic.

Theory decides the expected overhead: with r = 32 jumps, KN-LIT-c8e485 gives a negation overhead factor 1 + Theta(1/sqrt(32)) with 2-cycles at about 1/(2r) = 1/64 per step (KR-RHO-fb88e6); long fruitless cycles of length 2t occur at roughly r^{-t} per step (reviewer-supplied rate, to be checked against KN-LIT-c8e485), so a 2^34-step DP trail meets cycles up to length about 14, and the anchor detector must cover them. Proposed step: measure trap and escape overhead on live walk-4 trails of ECC2-131/ECCp-131 at production DP density (the walk is already deployed), against the 1 + Theta(1/sqrt r) prediction; keep the Koblitz Frobenius design as the second step.

**AUD-5 open_unexamined: first step.**

n/a for this disposition.

**AUD-6 obstruction as hypothesis.**

n/a for this disposition.

*Proposed change:* next_action stale; evidence ref pins

## LEAD-RHO-prime-gpu-rho

- Title: GPU rho on prime and generic binary curves with an admitted CPU/GPU comparison
- Disposition: `open_blocked`; file `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/generic/LEAD-RHO-prime-gpu-rho.yaml`
- next_action.step (verbatim): "Run the gpu-match workload on a CUDA host with qualified traffic telemetry: interleaved CPU/GPU repeats with A/A controls, then a matched P-256 toy-to-medium ladder in ecbench.gae."
- next_action.discriminates (verbatim): "An admitted interval lets GPU rho rows enter FRONTIER and the pool's capacity estimates; without it every GPU figure stays descriptive."
- next_action.blocked_by (verbatim): "crypto problems/ecbench-gpu-matched-workload-contract.md (PCIe telemetry and admission rule missing); problems/certicom-binary-gpu-rho-integration.md"
- forecloses: "GPU Pollard rho for P-256"; "CPU vs GPU rho comparison"; "generic GPU rho worker"; "Certicom prime-field GPU campaign"

**AUD-1 revisit triggers.**

n/a for this disposition.

**AUD-2 scope.**

n/a for this disposition.

**AUD-3 measured/cost_model to proof.**

n/a for this disposition.

**AUD-4 open_next_step/open_blocked: theorem vs experiment.**

No theorem decides an admission or telemetry blocker. The blockers (crypto problems/ecbench-gpu-matched-workload-contract.md, problems/certicom-binary-gpu-rho-integration.md) are still open per fold-crypto.md section 1. No change beyond the fold's evidence additions.

**AUD-5 open_unexamined: first step.**

n/a for this disposition.

**AUD-6 obstruction as hypothesis.**

n/a for this disposition.

*Proposed change:* none

## LEAD-RHO-r-adding-walk-mixing

- Title: Iteration-function choice: Teske r-adding walks, mixing, hashed partitions
- Disposition: `closed_known`; file `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/generic/LEAD-RHO-r-adding-walk-mixing.yaml`
- obstruction.kind: `literature`
- obstruction.statement (verbatim): "Known (KR-RHO-cd86f5, KR-RHO-93979e) and reproduced: plain rho on 3,200 solves over whole 26-bit volcanoes averages 659,263 +- 12,422 iterations against sqrt(pi n/2) = 654,547 (1.007x); a precomputed pair table R_i+R_j gives 1.027 [0.982, 1.073] (no gain, one addition still advances one step). Scope: prime-field toy and 26-bit curves."
- obstruction.revisit_when (verbatim): "A walk family with provable mixing strictly better than a random mapping (in-degree concentration is LEAD-RHO-best-of-candidates-indegree)."
- forecloses: "choose r for the r-adding walk"; "Teske walk constant"; "partition index from one coordinate"; "random-mapping walk constant"; "mixed walk with squarings"

**AUD-1 revisit triggers.**

Not fired. No walk family with provable mixing better than a random mapping appears in delta.txt.

**AUD-2 scope.**

Scope mismatch with a ledger ref. The lead lists H-TRA-4344b7 in ledger_refs and TRA in areas. H-TRA-4344b7 (status proposed; EXP-TRA-b39f46 review_required, refs KN-OPEN-010) is the coarse-grained transfer-operator question: whether the spectrum of the translation-by-P operator localises k. KN-OPEN-010 is `open`. The closure here is literature on walk constants ("Scope: prime-field toy and 26-bit curves") and says nothing about spectral localisation. Neither H-TRA-4344b7 nor IDEA-20260807-018769 has a row in coverage.tsv (grep found none), no other lead cites them, and `lead_atlas.py --match "coarse-grained transfer operator translation walk spectrum localize k Koopman"` returns no owning row (top hits LEAD-TRF-mov-small-embedding-degree 8, LEAD-TRF-prime-field-isogeny-to-weak 8, KR-RHO-755e35 6, KR-RHO-cd86f5 6, LEAD-ICB-cofactor-torsion-quotients 6), so README rule 4 permits a new lead. Proposed: move H-TRA-4344b7 and IDEA-20260807-018769 to a lead whose disposition reflects KN-OPEN-010 (an exotic-family row), and drop TRA from this lead's areas.

Candidate theorem route for that new row (conditional; KN-LIT-f6de4b is only an "attempted verification" of a Bombieri-Weil hypothesis): Bombieri-Weil bounds for character sums over points of E would make the coarse operator on x-interval cells equal to a rank-one matrix plus an O(p^{-1/2} log^2 p) perturbation for cells much larger than sqrt(p), which would give the barrier L = O(1).

Second scope point: `forecloses` "partition index from one coordinate" would block IDEA-20260920-5b1f84 (F_{p^5}, partition from ONE base-field coefficient), but coverage.tsv maps that idea to LEAD-ICP-gfp5-rho-reference-audit; the prime-field evidence here does not cover an extension-field partition. Proposed phrase: "partition index from one coordinate (prime field)".

**AUD-3 measured/cost_model to proof.**

n/a for this disposition. (kind literature)

**AUD-4 open_next_step/open_blocked: theorem vs experiment.**

n/a for this disposition.

**AUD-5 open_unexamined: first step.**

n/a for this disposition.

**AUD-6 obstruction as hypothesis.**

None found (not an SO-coded obstruction).

*Proposed change:* ledger_ref reassignment + forecloses narrowing

---

## Family: ic-binary

# Audit AUD-1..AUD-6: ic-binary family (21 leads)

Reviewer pass, 2026-10-24. Read-only; every claim cites a path or record id. Observation and interpretation are separated; interpretations are conditional. No research status is changed here (README rule 2); proposed changes are for the Coordinator / atlas curator.

## Current state used for AUD-1

- Known-results map: `/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/atlas/KRMAP.md` (index-calculus rows read in full).
- IC leaderboard: `/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/crypto-main/docs/ic/LEADERBOARD.md` (Tables A-C values identical to the leads' best_measured; phase table: Table A set-up 98.5-99.7%, Table C relations 56.3% at n53 and 78.8% at n61, LA <= 2.7%).
- Bounds frontier: `/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/crypto-main/docs/bounds/FRONTIER.md` (Koblitz medium tier ops leader `rho.signed_frobenius_strong` ECBND1hcf69c27b4978, 1.089x floor; `claw.pair_table` dominated).
- Delta: `/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/atlas/delta.txt` (201 paths). Binary-relevant items found by keyword scan and by matching every ic-binary ledger_ref/known_result against the delta files: DEC-20261018-273b2d (GF(2^61) m = 8 fixture design, no run), DEC-20261024-e29f4c (opens GOAL-PEXT-4a1d6b, prime-degree extension descent theory), IDEA-20261018-{1bc873, 88041d, e7a860, 1aff90, 6c1c6e, b4bc61, e3bcff, c4adb6, 4c28fc, 49fdf7, 670088, 2c37f5, f2cd4d, 329d0a} (all unrun proposals), problems/full-width-ic-arity-grid-unmeasured.md (no measurement). The CZLIFT decisions DEC-20261023-*, KN-FIND-3c7e19/7e2b94/c71e5d and KN-OPEN-d3a6f0 are prime-field p-adic and touch no ic-binary lead. No new decision changes the status of any ic-binary ledger_ref.
- Sibling evidence outside the delta that bears on triggers: `/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/cryptanalysis-main/experiments/pdp-degree-heuristics/README.md`; `/Volumes/SSD990-2/crypto-autoresearcher/problems/binary-subfield-base-has-no-large-prime-component.md`; `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/findings/KN-FIND-007.md`; LMFDB query saved at `/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/audit/lmfdb-av-f2-131.json`.

AUD-5: this family has **no open_unexamined lead** (dispositions: closed_obstructed 7, exhausted_at_scale 3, closed_dominated 1, open_next_step 9, open_blocked 1).


## Family-level AUD-6: standing obstructions owned by ic-binary

| code | lead (statement quoted in its subsection) | theory taking the obstructing quantity as a HYPOTHESIS |
|:--|:--|:--|
| SO-TABLE | LEAD-ICB-generic-table-oracle | (1) Non-genericity witness: a measured log2(S*T^2) - log2(r/|Aut|) < 0 certifies representation use (IDEA-20261018-4c28fc proposes recording it). (2) Per-group scope: curve-family advice (F4 trace replay KR-IC-f3da82, Semaev precomputation) lies outside a per-group bound. (3) Algebraic group model uses generic hardness as an assumption (not generative). |
| SO-MULTI | LEAD-ICB-multi-target-and-portfolio | Finite-field NFS precomputation (1/L amortisation after non-generic setup): 1/L observed on an EC oracle would witness non-genericity. Not generative on EC. |
| SO-QSP | LEAD-ICB-quasi-subfield-polynomials | HKPYY cost model takes beta as a parameter; beta < 3/4 requires non-linearized splitters (open). None found that constructs one. |
| SO-TORS | LEAD-ICB-cofactor-torsion-quotients | Wagner k-tree takes the size of an exactly sum-compatible quotient as input; KN-FIND-007 / cryptanalysis finding 3 take the class distribution in E/<G> as input. Both bound the cofactor's value by log2(h) bits. With h ~ 2^16 (c2pnb) this is non-trivial; with h = 4 (ECC2K-130) it is 2 bits. |
| SO-FROB | LEAD-ICB-frobenius-search-symmetry, LEAD-ICB-frobenius-orbit-factor-base | GGMP accounting takes the n-fold as input; random self-reducibility across conjugate targets takes the equivariance as input (bounded by SO-MULTI). None found that yields more than n. |


## LEAD-ICB-cofactor-torsion-quotients

- file: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/ic-binary/LEAD-ICB-cofactor-torsion-quotients.yaml`
- disposition: `closed_obstructed`
- title: Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients of the factor base

- obstruction.kind: `proof`

obstruction.statement (verbatim):

> On ECC2K-130 gcd(4, l) = 1, so every full-translation homomorphic cofactor quotient reduces to the order-l projection rho already uses (Sylow coprimality); exactly sum-compatible filters on E(F_{2^131}) carry 2 bits (the cofactor), so Wagner k-tree has no quotient to work in; the corrected iota-stable classification (V_d = b^{1/4} F_{2^d}) empties the (subspace base, 2-torsion quotient) cell on every prime-degree standardized curve; the production 2-torsion census adds 0 relations. FGHR 2-torsion symmetrisation of the solve is a separate constant (engine family).

obstruction.revisit_when (verbatim):

> A curve with a large smooth cofactor, or a non-homomorphic sum-compatible filter with more than log2(cofactor) bits.


forecloses: Wagner k-tree on ECC2K-130; cofactor 4 coset label prunes decomposition; 2-torsion translation quotient of a subspace factor base; spend the cofactor on decomposition


**AUD-1.** **Trigger fired in its first clause, at the level of existence.** Observation: the five composite-degree ANSI curves in this family's own lead `LEAD-ICB-composite-degree-c2pnb` have cofactors 65390, 65096, 65286, 65070, 65392 (`/Volumes/SSD990-2/crypto-autoresearcher/analysis/binstd-curve-audit/README.md`, table "curve | m | k = m/16 | A, B in F_{2^16} | cofactor"). Factorisations computed here (sympy): 65390 = 2*5*13*503, 65096 = 2^3*79*103, 65286 = 2*3^4*13*31, 65070 = 2*3^3*5*241, 65392 = 2^4*61*67. These are ~2^16 cofactors (largest prime factor 31 for 65286), against 4 on ECC2K-130. Interpretation (conditional): the revisit condition 'a curve with a large smooth cofactor' is met by curves already in the atlas. The proof's ECC2K-130 clause (2 bits) does not transfer; the Sylow-coprimality clause does (gcd(h, r) = 1 still forces every homomorphic quotient to factor through the order-r projection). What reopens is only the 'exactly sum-compatible filter carries log2(h) bits' clause: on c2pnb it is ~16 bits. Whether 16 bits of filter matter depends on the oracle (the c2pnb lane uses an algebraic Gaudry n = 4 oracle, where candidate filtering is not the cost driver). No new measurement exists.


**AUD-2.** **Over-broad foreclose.** The statement proves its claims on ECC2K-130 and on 'every prime-degree standardized curve' (the iota-stable cell), and explicitly exempts 'FGHR 2-torsion symmetrisation of the solve'. The phrase 'spend the cofactor on decomposition' blocks every use of the cofactor, including two that the statement does not cover: (a) FGHR 2-torsion symmetrisation (named as a separate constant in the statement itself; IDEA-20261018-6c1c6e prices it at 30-416x on the m = 4 system, `/Volumes/SSD990-2/crypto-autoresearcher/ledger/proposals/IDEA-20261018-6c1c6e.yaml`); (b) placing the factor base in the class of the target in E/<G> (ker(Tr) placement), which cryptanalysis measured as doubling yield at equal degree ('A progression placed inside ker(Tr) (family geomtrace) keeps the minimal profile and gets the kernel-of-trace doubling of the yield', `/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/cryptanalysis-main/experiments/pdp-degree-heuristics/README.md` finding 3). Both are bounded by log2(h) bits (a constant), so they do not contradict the closure's conclusion; they contradict the phrase. Also the phrase 'Wagner k-tree on ECC2K-130' is correctly scoped.


**AUD-3.** Kind is proof; pass not required. The Sylow clause is already a short proof; a Lean target is cheap (see finding list): for a finite abelian group G = H x C_r with gcd(|H|, r) = 1, every homomorphism phi: G -> Q with phi restricted to C_r injective factors as (projection to C_r) followed by an injection, up to the H-part.


**AUD-4.** n/a (pass applies to other dispositions)


**AUD-5.** n/a (pass applies to other dispositions)


**AUD-6.** SO-TORS. A theory that takes gcd(h, r) = 1 and |H| = h as a hypothesis: Wagner's generalized-birthday k-tree takes the size of an exactly sum-compatible quotient as its input parameter; with h ~ 2^16 (c2pnb) it has one ~16-bit level, with h = 4 (ECC2K-130) none. KN-FIND-007-style yield conservation over E/<G> classes (cryptanalysis finding 3) also takes h as a parameter: base placement in the target's class raises mean yield by at most h. Both turn the cofactor into a bounded constant, never an exponent.



## LEAD-ICB-composite-degree-c2pnb

- file: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/ic-binary/LEAD-ICB-composite-degree-c2pnb.yaml`
- disposition: `open_next_step`
- title: Composite-degree ANSI X9.62 binary curves (c2pnb176/208/272/304/368): Gaudry-Diem n = 4 with a pi_16 orbit base


next_action.step (verbatim):

> Run the C1 toy ladder (NEXT-STEPS item 6): E over F_{2^4} lifted to F_{2^{4k}}, k in {5, 7, 9, 11, 13}, about 2e4 decompositions, to pin c_trial, the solving degree and per-worker memory; pair it with the primitive-prime c2tnb null ladder (H-BINSTD-e241a8).

next_action.discriminates (verbatim):

> c_trial <= 2^27 at extrapolation keeps the mesh area-time win at c2pnb304w1 and c2pnb368w1, the first standardized binary row below rho under a memory-charged metric; c_trial > 2^27 makes the lane dominated on every metric and closes it.


forecloses: Gaudry n = 4 on c2pnb curves beats rho; trace-zero variety decomposition breaks the ANSI c2pnb curves; subfield-rational factor base on composite-degree ANSI curves; GHS base field c | 16 for c2pnb


**AUD-1.** n/a (pass applies to other dispositions)


**AUD-2.** n/a (pass applies to other dispositions)


**AUD-3.** n/a (pass applies to other dispositions)


**AUD-4.** **Evidence addition (no disposition change).** The best_measured clause 'The F_{2^16}-rational base is structurally empty in G' now has a proved conditional statement behind it: `/Volumes/SSD990-2/crypto-autoresearcher/problems/binary-subfield-base-has-no-large-prime-component.md` ('A direct base restricted to x-coordinates in F_(2^d) cannot contribute to a large prime subgroup of E(F_(2^n)) when d|n, d<n, the curve descends to F_(2^d), and the target prime order exceeds 2^d+1+floor(2 sqrt(2^d))'). The c2pnb curves descend to F_{2^16} (`analysis/binstd-curve-audit/README.md`: 'A, B in F_{2^16}: yes'), so d = 16 satisfies the hypotheses. It does NOT apply to the Gaudry n = 4 base F_{2^{4k}} with k prime, because F_{2^16} is not contained in F_{2^{4k}} for odd k (intersection F_{2^4}), so the curve does not descend to the base field. Theorem shortcut for the queued ladder: the lead's own mechanism treats c_trial as the per-trial Groebner cost of a fixed-n system; if the system shape is q-independent for generic coefficients, one k suffices to pin c_trial in F_q operations and the remaining rungs only test constancy (and memory). This does not decide the lane: the decision needs c_trial against the 2^27 threshold, which is a measurement.


**AUD-5.** n/a (pass applies to other dispositions)


**AUD-6.** n/a (pass applies to other dispositions)



## LEAD-ICB-decomposition-encoding-and-sat

- file: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/ic-binary/LEAD-ICB-decomposition-encoding-and-sat.yaml`
- disposition: `closed_obstructed`
- title: Decomposition-oracle encodings and SAT/enumeration solving of binary PDP: SAT/XOR, Karabina, S_m symmetrisation, chained vs direct S_4, Nagao, basis and reduction-polynomial choice, trace replay

- obstruction.kind: `measured`

obstruction.statement (verbatim):

> Every SAT or enumeration method measured has per-attempt UNSAT cost 2^{alpha l} with alpha ~ m (WDSat 2.9985 bits per unit l at m = 3, reproducing 2^{3l}/3!; alpha 4.09-4.33 at m = 4, l = 3..5), while beating rho needs alpha < m/2 - 1; at m = 3, 4 the measured families extrapolate 50-150 bits above budget at n = 131. Ladders n = 11..31: no arm grows slower than the enumeration floor (m = 3 slopes 0.53-0.58 vs floor 0.21; m = 4 wide chain 0.805 vs 0.333). Encoding levers are constants: S_m symmetrisation saturates product spaces at m >= 5 at balanced l (H-BINSTD-770ec3 supported), closure outcomes are basis-invariant (Proposition B), reduction-polynomial weight is a constant confound, Nagao coset yield weakened vs chained S_3, trace replay is a constant at most.

obstruction.revisit_when (verbatim):

> A solver or presentation whose UNSAT cost grows by fewer than m/2 - 1 bits per unit l at m >= 3 (then it becomes LEAD-ICB-prime-degree-algebraic-decomposition).


forecloses: SAT or XOR solver for point decomposition beats rho; Karabina symmetric formulation or crossbred for binary PDP; direct S_4 instead of chained S_3; normal basis versus polynomial basis changes decomposition cost; pentanomial vs trinomial reduction polynomial lever


**AUD-1.** Not fired. No delta item reports a solver whose UNSAT cost grows by fewer than m/2 - 1 bits per unit l. Delta proposals touching the trigger are unrun: IDEA-20261018-b4bc61 (Crossbred with ePrint 2026/360 preprocessing, claim only), IDEA-20261018-e3bcff (port f4_gf2/f4_gpu, tooling), IDEA-20261018-88041d (degree measurement, unrun).


**AUD-2.** **Measured null at small l used as an unqualified closure.** The statement measures m = 3 and m = 4 only (alpha 4.09-4.33 at m = 4, l = 3..5; ladders n = 11..31). The foreclose phrase 'SAT or XOR solver for point decomposition beats rho' carries no m, l or n qualifier. Its scope therefore includes m >= 5, where the statement reports only an encoding observation (S_m symmetrisation saturation), not a solver cost. The ic-engine lead `LEAD-ICE-sat-xor-pdp-oracle` is still open_next_step with 'fit alpha(m) of the conflict count at m in {3,4,5}' (`/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/atlas/ATLAS.md`), so the two rows disagree on whether m = 5 SAT cost is decided. Second: 'normal basis versus polynomial basis changes decomposition cost' is backed by Proposition B ('closure outcomes are basis-invariant'). That proposition covers algebraic closure/XL degree, not CDCL conflict counts, which depend on the encoding. So the phrase is proved for closure-type solvers only.


**AUD-3.** **Short proofs replace two sub-claims.** (i) The beat-rho threshold 'alpha < m/2 - 1' is a two-line cost-model inequality. Lean target below. (ii) Proposition B (basis invariance) and the 'reduction-polynomial weight is a constant confound' clause reduce to one lemma. An invertible F_2-affine change of the Boolean variables maps the degree-<=d span of the Macaulay matrix onto itself. The XL/closure refutation degree is therefore invariant under the choice of F_2-basis of F_{2^n} and of the defining polynomial (both induce such a change on the descended variables). This does not cover CDCL/WDSat conflict counts. The measured clause alpha ~ m stays measured; no short proof is known for a lower bound on resolution/CDCL refutation of these systems.


**AUD-4.** n/a (pass applies to other dispositions)


**AUD-5.** n/a (pass applies to other dispositions)


**AUD-6.** Not a standing obstruction (measured). The quantity alpha(m) is taken as a parameter (hypothesis) by the HKPYY/Petit-Quisquater-style cost models (exponent as a function of the refutation cost) and by the program's own threshold lemma; none found that takes alpha ~ m as a hypothesis and outputs a new algorithm.



## LEAD-ICB-ecc2k130-jacobian-carrier

- file: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/ic-binary/LEAD-ICB-ecc2k130-jacobian-carrier.yaml`
- disposition: `open_next_step`
- title: ECC2K-130 via a Jacobian carrying the trace-zero abelian variety A (Torelli rarity heuristic)


next_action.step (verbatim):

> Run the toy ladder at the first faithful rungs n = 11 and n = 13 (2 primitive mod n, A simple, no small magic number), sampling curves of genus dim A to dim A + 2 over F_2 and testing whether the target polynomial divides P_C.

next_action.discriminates (verbatim):

> Carriers at genus <= dim A + 2 on a faithful rung reopen a constructive search toward n = 131; none confirms rarity where Weil-restriction structure is absent, closing the route with data rather than a dimension count.


forecloses: ECC2K-130 trace-zero variety is a Jacobian; genus 130 to 300 curve carrying A; Torelli locus search for ECC2K-130


**AUD-1.** n/a (pass applies to other dispositions)


**AUD-2.** n/a (pass applies to other dispositions)


**AUD-3.** n/a (pass applies to other dispositions)


**AUD-4.** No theorem found that decides the carrier question faster. A point-count positivity check (#C(F_{2^k}) >= 0 with A's trace contribution, which is -(tau^k + taubar^k) for 131 not dividing k and 130(tau^k+taubar^k) for 131 | k) gives no contradiction at genus >= dim A (the A-contribution is at most ~2^{73.5} at k = 131 against 2^131 + 1). The toy ladder remains the discriminating step; no change proposed.


**AUD-5.** n/a (pass applies to other dispositions)


**AUD-6.** n/a (pass applies to other dispositions)



## LEAD-ICB-factor-base-subspace-choice

- file: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/ic-binary/LEAD-ICB-factor-base-subspace-choice.yaml`
- disposition: `exhausted_at_scale`
- title: Choice of the factor-base subspace V at fixed dimension (geometric progression, dim(V.V), trace rank, cosets, greedy coverage, HW pools, trace-parity window)

- obstruction.kind: `measured`

obstruction.statement (verbatim):

> Measured with nulls up to n = 41 and r = 2^39: greedy coverage 1.18x at r = 2^13 shrinking to 1.0000 at r = 2^39; coset/random 1.020 [0.959, 1.083]; geometric-progression vs random at matched dim(V.V) weakened and replicated (EV-BINSTD-78ca0d, EV-BINSTD-b176df); repeated Spearman catalog tests of dim(V.V) or trace rank against N_var inconclusive (distinct-value floors not met); normal-basis vs polynomial-basis HW pools give no yield change at n = 17 (scoped support of H1). The Weil bound is vacuous for abscissa density at every IC dimension l <= 66 at n = 131. All effects are constants that vanish with size.

obstruction.revisit_when (verbatim):

> A property of V that predicts N_var or yield with a null-controlled effect that grows with n at n >= 31.


forecloses: geometric progression subspace beats random subspace; small dim(V.V) factor base reduces XOR-SAT variables; Bailey Hamming-weight distinguished points as a factor base; greedy or coset factor base raises relation yield; trace-parity half window of Semaev polynomial basis


**AUD-1.** **Trigger fired for the product-profile arm, conditionally.** revisit_when asks for 'a property of V that predicts N_var or yield with a null-controlled effect that grows with n at n >= 31'. Observation, sibling repo: `/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/cryptanalysis-main/experiments/pdp-degree-heuristics/README.md`. (1) The linearization excess e = n - dim V - dim V^(2) predicts the closure solving degree as D = 2 + [e < -3.5] + [e < -8.5] over 656 bases, 7 families, 9 fields (MAE 0.06; 0.08 with each field size held out). (2) 'For prime n, dim V^(2) >= 2l - 1, and below n - 1 only the progressions c*span{1, g, ..., g^(l-1)} attain it' (Hou-Leung-Xiang Kneser analogue; Bachoc-Serra-Zemor; README section 3). (3) In the symmetric formulation the number of unknowns 'is Sum_k dim V^(k): 15 against 19 at l = 3, and 21 against 34 at l = 4', and progressions are '15-40x cheaper per query at equal degree, and 500-1,500x cheaper where the random base needs one more degree' (m = 3, n = 31 run listed in its Quick start). (4) Section 8, structure-only at n = 131: progressions keep the minimal profile through V^(4) for l <= 28 while random and normal-basis bases saturate V^(2) from l = 16 (Sum_{k<=3} dim V^(k) = 165 vs 290 at l = 28). That is a property of V that predicts N_var exactly and whose effect grows with l at n = 131. 'Null-controlled at n >= 31' holds for the m = 3 symmetric n = 31 cell (random family as control); growth with n is shown structurally (exact profile arithmetic), not measured. The same README says 'None of this is an IC result', and its n = 131 table gives log2 E[decompositions] of -23.6 (m = 4) and 2.1 (m = 5) at l = 28. So the lever does not by itself reach rho at n = 131.


**AUD-2.** **Closure forecloses more than it proved.** (a) The GP-vs-random null is 'at matched dim(V.V)' (EV-BINSTD-b176df: n = 17, l = 3, '12 matched GP/random pairs with |Delta dim(V.V)|=1'). The record itself lists the confound '(1) product-dimension-only driver - matching dim(V.V) erases GP' (`/Volumes/SSD990-2/crypto-autoresearcher/ledger/evidence/EV-BINSTD-b176df.yaml` lines ~176-202). By the cryptanalysis characterisation, GP's only structural property is the minimal profile, so a profile-matched comparison controls away the lever. The phrase 'geometric progression subspace beats random subspace' is therefore not closed by it. (b) 'small dim(V.V) factor base reduces XOR-SAT variables' is false as a closure in the symmetric formulation, where N_var = Sum_k dim V^(k) by construction (cryptanalysis finding 5). (c) 'repeated Spearman catalog tests ... inconclusive (distinct-value floors not met)' is an uncontrolled null (the statement's own words) used as part of an exhausted_at_scale closure. (d) 'All effects are constants that vanish with size' is contradicted for the profile by the exact n = 131 profile table (the gap grows with l). The coverage arms (greedy 1.18x -> 1.0000, coset 1.020) are correctly closed, and more strongly than measured (AUD-3).


**AUD-3.** **Coverage arms: replace measured with proof.** KN-FIND-007 (`/Volumes/SSD990-2/crypto-autoresearcher/knowledge/findings/KN-FIND-007.md`, derivation) states Sum_r c_D(r) = binomial(B+m-1, m) for every base D of size B, so mean yield is base-independent. With Markov (P(c_D(R) >= 1) <= E[c_D(R)] = lambda), the uniform-target success probability of ANY base is at most lambda. A random base attains about 1 - e^(-lambda) (Poisson, which cryptanalysis finding 3 reports matching to 2-3%). So the maximal coverage gain of any engineered base over random is about lambda/(1 - e^(-lambda)) -> 1 as lambda -> 0. This is exactly the measured greedy 1.18x at r = 2^13 shrinking to 1.0000 at r = 2^39. The bound part is a theorem; the 'random attains Poisson' part is a heuristic. Lean target below. The product-profile arm has no short proof of closure; the Hou-Leung-Xiang lower bound dim V^(2) >= 2l - 1 at prime n is a theorem in the other direction (it shows GP is optimal).


**AUD-4.** n/a (pass applies to other dispositions)


**AUD-5.** n/a (pass applies to other dispositions)


**AUD-6.** Not a standing obstruction. Yield conservation (KN-FIND-007) is taken as a hypothesis by the linearization-excess programme (LEAD-ICE-linearization-excess-fb-prior): since yield is fixed by |F|, every remaining degree of freedom of V can be spent on degree/variable count at no yield cost.



## LEAD-ICB-free-relations-self-collision

- file: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/ic-binary/LEAD-ICB-free-relations-self-collision.yaml`
- disposition: `exhausted_at_scale`
- title: Free relations from self-collisions in the pair-root table (no-probe relations)

- obstruction.kind: `measured`

obstruction.statement (verbatim):

> The relations exist but are highly correlated: homogeneous rank 49 from 588 verified rows at n61/K600, 746 at K1200, 1,197 at K1500, and 6 at n83/K600; rank grows about K^4, so a free rank stage needs K ~ 1,500-2,050 at n61 and ~2,600 at n83 (36 GB), where scan plus K^2 linear algebra exceed the guided rank stage. In production (n <= 63, default on) it is a constant 0.957-0.960x of the complete solve; the 2-torsion census adds 0 relations. Scale reached: n = 41-83, K <= 1,500.

obstruction.revisit_when (verbatim):

> A wide-path (n > 63) harvest is implemented, or a table structure yields independent rows faster than K^4.


forecloses: free relations by sorting the pair-root table; self-collision relations make the rank stage free; harvest relations without probes on Koblitz IC


**AUD-1.** Not fired. No delta item implements a wide-path (n > 63) harvest or reports independent free relations faster than K^4. crypto problem `problems/n83-prebuilt-base-quality-m2-m4.md` (delta) concerns base quality, not a harvest.


**AUD-2.** Scope consistent: the statement gives its scale ('Scale reached: n = 41-83, K <= 1,500') and the foreclose phrases are about this mechanism. No flag.


**AUD-3.** No short proof found. The rank-growth law (about K^4) is an empirical fit, and the crossover K* follows from it by algebra, which adds no proof content. The measured closure stands at its stated scale.


**AUD-4.** n/a (pass applies to other dispositions)


**AUD-5.** n/a (pass applies to other dispositions)


**AUD-6.** Not a standing obstruction. None found.



## LEAD-ICB-frobenius-orbit-factor-base

- file: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/ic-binary/LEAD-ICB-frobenius-orbit-factor-base.yaml`
- disposition: `closed_obstructed`
- title: Frobenius/endomorphism-invariant factor bases and orbit columns on Koblitz and subfield curves, beyond the trivial orbit saving

- obstruction.kind: `proof`

obstruction.statement (verbatim):

> For E/F_q attacked over F_{q^n}, the base {x(P) in V} is pi-stable exactly when V is sigma-stable, the stable subspaces form an arithmetic lattice fixed by the factorisation of X^n-1 over F_q, and the gain is exactly n on relations (n^2 on LA) and never more (H-FROB-6774fb supported, DEC-20260923-e6cd5d; the tau-factor-base pilot finds the per-attempt decomposition probability at matched |FB| equal to the birthday value for orbit-union, normal-basis and polynomial bases, n = 11..23). At prime n with ord_n(2) = n-1 (131, 163) the usable stable dimensions are empty (H-BINSTD-b1f016 replicated). Rho gets the matching sqrt(2n) from the same automorphisms, so the matched gap is unchanged. Prime-field phi-stable bases (EQIC) are bounded by the eigenvalue-subgroup order (at most 6) and measured +4% Ir at order 6 on j = 0. Scope: Koblitz/subfield curves over F_{2^n}, n prime, toy to n = 61 measured; ECC2K-130 by structure.

obstruction.revisit_when (verbatim):

> A Frobenius-stable base whose per-attempt decomposition probability exceeds the birthday value at matched |FB| (a second gain in the decomposition step), or a stable non-subspace base with membership degree far below its size (see LEAD-ICB-nonlinear-frob-stable-bases).


forecloses: Frobenius-invariant factor base gives more than an n-fold saving; Frobenius-stable subspace factor base for ECC2K-130 or K-163; orbit columns cut relation collection below rho on Koblitz curves; phi-stable or mu_3-invariant factor base on j = 0 curves beats the |Aut| fold; Koblitz structure of the K-curves buys IC more than it buys rho


**AUD-1.** Not fired. Delta IDEA-20261018-329d0a proposes multiplicative-subgroup bases S_d = {x : x^d = 1} (stable under squaring and x -> 1/x). Its membership degree equals its size d, so it does not meet 'membership degree far below its size'. IDEA-20261018-c4adb6 is not Frobenius-stable.


**AUD-2.** **Prime-field scope leak.** The statement is scoped 'Koblitz/subfield curves over F_{2^n}, n prime, toy to n = 61 measured; ECC2K-130 by structure', but it also carries a prime-field clause: 'Prime-field phi-stable bases (EQIC) are bounded by the eigenvalue-subgroup order (at most 6) and measured +4% Ir at order 6 on j = 0'. The foreclose phrase 'phi-stable or mu_3-invariant factor base on j = 0 curves beats the |Aut| fold' then closes a prime-field question (j = 0, e.g. secp256k1-type curves) from a binary-family row on one measurement. The bound 'at most 6' is a theorem about |Aut| (and the |Aut| fold is matched by rho), so the conclusion is plausible. The phrase belongs to the ic-prime/structure family with its own evidence (`crypto/research/notes/index-calculus/RESEARCH_GLV_INVARIANT_FACTOR_BASES.md`), not here. Second, kind is 'proof', but the 'never more' clause for the decomposition step rests on a pilot measured at n = 11..23 ('tau-factor-base pilot finds the per-attempt decomposition probability at matched |FB| equal to the birthday value').


**AUD-3.** Kind is proof, but the 'no second gain in the decomposition step' clause is measured. It can be made a proof. Per-attempt decomposition probability at matched |FB| for a uniformly random target is bounded by the mean yield binomial(B+m-1, m)/N (Markov), and that mean is base-independent (KN-FIND-007). So no base, stable or not, can raise the uniform-target per-attempt probability above the birthday value; it can only redistribute it across targets. Consequence for revisit_when: its first clause ('per-attempt decomposition probability exceeds the birthday value at matched |FB|') cannot fire for uniformly random targets. It can fire only under target selection correlated with the base (the 'escaping conservation by target preselection' route of LEAD-ICP-coincidence-harvest-structured-base), which must then be charged.


**AUD-4.** n/a (pass applies to other dispositions)


**AUD-5.** n/a (pass applies to other dispositions)


**AUD-6.** SO-FROB (orbit fold = exactly n). Takes the fold as hypothesis: Galbraith-Granger-Merz-Petit (KR-IC-b0fcda) cost accounting, in which the n-fold on relations and n^2 on LA is an input. Since rho receives sqrt(2n) from the same group, a theory that takes 'IC gets n, rho gets sqrt(n)' as hypothesis predicts the matched gap shrinks by sqrt(n) per unit of fold. That is a constant for fixed n; no exponent consequence found.



## LEAD-ICB-frobenius-search-symmetry

- file: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/ic-binary/LEAD-ICB-frobenius-search-symmetry.yaml`
- disposition: `closed_obstructed`
- title: Frobenius as a symmetry of the decomposition search: orbit CNF encodings, conjugate attempts, equivariant elimination

- obstruction.kind: `proof`

obstruction.statement (verbatim):

> The absolute Frobenius is an equivariance between conjugate target instances, not a per-instance search symmetry (H-BINSTD-74b002 supported, replicated); fixed-target tau-orbit CNF clauses are unsound (H-BINSTD-c3d68f, replicated); sound orbit encodings cost >= 0.95x the plain single-instance search at n = 17, 23, 31; on a non-stable V the n conjugates of a target are n attempts over n conjugate bases (Proposition T); the k conjugates of a relation are one row in the orbit basis. Equivariant elimination is a constant only: 44-73x against a naive kernel is 2-3x against gf2_elim; whole-oracle 5.1x/15.5x at n = 11/13, of which fall-row augmentation alone gives 11.6x, and it does not apply to the production pipeline systems (regresses 0.29-0.59x there).

obstruction.revisit_when (verbatim):

> A genuine stabilizer of a single target R in the descended system (not a conjugation), or an equivariant elimination that applies to the production compact-orbit pipeline.


forecloses: Frobenius symmetry breaking in the SAT encoding; treat the n Frobenius conjugates of a target as one attempt; equivariant F4 makes Koblitz decomposition sub-rho; orbit-quotient CNF for Koblitz point decomposition


**AUD-1.** Not fired. Delta DEC-20261018-273b2d (sorted presentation for the 8! summand symmetry of the GF(2^61) m = 8 fixture) is S_m symmetry breaking, not a stabilizer of one target; IDEA-20261018-e3bcff is a solver port. No equivariant elimination for the production compact-orbit pipeline appears.


**AUD-2.** Scope consistent with statement; the measured sub-clauses (>= 0.95x at n = 17, 23, 31; 5.1x/15.5x at n = 11/13) are cited as measured. No flag.


**AUD-3.** Kind is proof. Sharpening of revisit_when by proof: the first clause asks for 'a genuine stabilizer of a single target R in the descended system (not a conjugation)'. For R != O in a subgroup of prime order r, every element of <pi, -1> acts on <R> as multiplication by some lambda in (Z/r)^*, and it fixes R iff lambda = 1. So no non-trivial curve automorphism stabilizes R. Any stabilizer must be a symmetry of the polynomial system not induced by Aut(E) (the S_m slot symmetry is the known one, already used). Lean target below.


**AUD-4.** n/a (pass applies to other dispositions)


**AUD-5.** n/a (pass applies to other dispositions)


**AUD-6.** SO-FROB (equivariance, not symmetry). Taking the equivariance as hypothesis gives random self-reducibility across the n conjugate targets pi^i(R) (log pi^i(R) = lambda^i log R), which is a batch-DL statement, bounded by SO-MULTI. None found beyond that.



## LEAD-ICB-generic-table-oracle

- file: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/ic-binary/LEAD-ICB-generic-table-oracle.yaml`
- disposition: `closed_obstructed`
- title: Generic decomposition oracles for Koblitz IC: pair tables, compact-orbit 4-sum, MITM and enumeration, cap-locus arity, known-log pools

- obstruction.kind: `theorem`

obstruction.statement (verbatim):

> Every oracle built from group operations and membership tests makes IC a generic-group algorithm with advice: Shoup T >= sqrt(r/|Aut|) and Corrigan-Gibbs-Kogan S*T^2 >~ r/|Aut| apply, so with |Aut| = 2n no 4-, 5- or 6-sum table can beat sqrt(r/2n) in total work; the balanced generic-IC cost is ~ r^{2/3}/n^{4/3} against rho r^{1/2}. Measured: rungs sit 2^25-2^27 above the generic line; ln(IC/rho) grows 0.165 [0.117, 0.213] per ln r. Target-dependent and walk-carried bases are known-log pools (H-BINSTD-1447cf). At ECC2K-130 this route needs K* ~ 4e11 columns and ~8e9 core-years. Scope: all binary and Koblitz curves, one target, setup charged.

obstruction.revisit_when (verbatim):

> An oracle that is not generic (algebraic restriction on the unknowns with membership degree far below |F|), which is LEAD-ICB-prime-degree-algebraic-decomposition; constant-factor engineering of this pipeline remains valid baseline work (LEAD-ICB-koblitz-setup-phase-cost).


forecloses: bigger pair table or k-sum table for ECC2K-130; 5-sum or 6-sum compact-orbit extraction beats rho; meet-in-the-middle point decomposition as a sub-rho oracle; walk-carried or target-dependent factor base; arity lever at the cap locus for ECC2K-130


**AUD-1.** Not fired. Delta IDEA-20261018-49fdf7 ('Every recorded pair-table, k-sum and 6-sum design at ECC2K-130 ... is a non-adaptive table-lookup algorithm with advice below sqrt(N), so by Dinur-Keller-Marmor (ePrint 2025/783) ...', `/Volumes/SSD990-2/crypto-autoresearcher/ledger/.index/proposals.jsonl`) is an unrun proposal that would strengthen, not reopen, the closure. FRONTIER.md Koblitz medium tier lists `claw.pair_table` at 2.390x floor (ECBND1h308cafe94026) dominated by `rho.signed_frobenius_strong` (ECBND1hcf69c27b4978): consistent with the closure.


**AUD-2.** Scope check of 'a generic-group bound applied to an oracle that reads coordinates'. The oracle class is 'group operations and membership tests'. A membership test x(P) in V reads coordinates. In Shoup's model an algorithm may compute any function of labels (distinguished points rely on this), so a label predicate used only as a filter keeps the algorithm generic, and the bound applies. The bound does not apply once the predicate's algebraic structure is exploited (Semaev/Weil descent), and the statement says so in revisit_when. Recommend rewording 'membership tests' to 'label predicates used only as filters (no algebraic use of coordinates)' so the scope line is explicit. The foreclose phrase 'walk-carried or target-dependent factor base' is backed by H-BINSTD-1447cf (known-log pools are generic). No over-reach found.


**AUD-3.** Kind is theorem; pass not required.


**AUD-4.** n/a (pass applies to other dispositions)


**AUD-5.** n/a (pass applies to other dispositions)


**AUD-6.** SO-TABLE (S*T^2 >~ r/|Aut|). Theories that take it as a hypothesis: (1) a non-genericity witness. Any measured algorithm with log2(S*T^2) - log2(r/|Aut|) < 0 must exploit the representation; IDEA-20261018-4c28fc proposes recording exactly this number. (2) Family-level advice. The bound is per group, so advice that is curve-independent (an F4 trace replayed across systems, KR-IC-f3da82; Semaev polynomial precomputation) is outside it. That is the 'advice shared across many curves' clause of LEAD-ICB-retained-setup-online. (3) The algebraic group model takes generic hardness as a hypothesis for reductions, which is not generative for attacks.



## LEAD-ICB-kic-golden-base-exact-decomp

- file: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/ic-binary/LEAD-ICB-kic-golden-base-exact-decomp.yaml`
- disposition: `open_next_step`
- title: Co-designed binary factor bases with exact decomposition: affine 2-flats, orbit-canonical abscissa lookup, SAT vs exact MITM (KIC lane)


next_action.step (verbatim):

> Coordinator evidence review of the five completed KIC runs (EXP-KIC-3df18c, -424885, -7bcef8, -c3c732, -d9c828), none of which has an EV record; then, for any arm whose advantage survives its null and A/A, a paired test inside the compact-orbit pipeline.

next_action.discriminates (verbatim):

> A reviewed wall or coverage advantage that survives the null is a candidate constant improvement for the IC baseline; none closes the lane as dominated by exact MITM.


forecloses: golden factor base with easy SAT decomposition; affine 2-flat factor base; orbit-canonical abscissa pair lookup


**AUD-1.** n/a (pass applies to other dispositions)


**AUD-2.** n/a (pass applies to other dispositions)


**AUD-3.** n/a (pass applies to other dispositions)


**AUD-4.** **Two arms decidable without the queued review.** (a) Coverage arm: 'candidate coverage 70 = null coverage 70' is the expected outcome by KN-FIND-007 plus Markov (no base can raise uniform-target coverage above the mean yield; AUD-3 of LEAD-ICB-factor-base-subspace-choice). Any coverage advantage the review finds is bounded by about lambda/(1 - e^-lambda). Outcome map: coverage advantage <= that bound -> no change; above it -> instrument error. (b) Pair-table reuse arm: EXP-KIC-d9c828 tests H-KIC-5c9611 (pair-table reuse; run `/Volumes/SSD990-2/crypto-autoresearcher/experiments/EXP-KIC-d9c828/runs/RUN-KIC-ba86d9`). H-KIC-5c9611 is the single ledger ref of the closed_dominated `LEAD-ICB-retained-setup-online` (dominated by Bernstein-Lange preprocessing rho), so that arm's cross-target value is already decided there. Only the wall-time arms (SAT vs exact MITM, orbit-canonical lookup) remain for review. Completeness: experiments index lists EXP-KIC-6ee7d9 (H-KIC-278c66) and EXP-KIC-976649 (H-KIC-baee02) with empty runs/ (`ls experiments/EXP-KIC-*/runs`), and H-KIC-9416d9 (EXP-KIC-424885's hypothesis) is not in ledger_refs. All KIC hypotheses are status proposed/specified (`ledger/.index/hypotheses.jsonl`); no EV-KIC-* record exists (`ls ledger/evidence | grep KIC` returns 0).


**AUD-5.** n/a (pass applies to other dispositions)


**AUD-6.** n/a (pass applies to other dispositions)



## LEAD-ICB-koblitz-rho-reference

- file: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/ic-binary/LEAD-ICB-koblitz-rho-reference.yaml`
- disposition: `open_next_step`
- title: The matched Koblitz rho reference for binary IC rows: step pricing, signed-Frobenius canonicalisation, a 131-bit walk


next_action.step (verbatim):

> Run the strong rho fixture and ParallelRho on the same Table A targets in the same process and price the stronger one at the canonical step (the rule-v4 validator found the strong fixture needs 0.845 +- 0.08 of ParallelRho's steps, and admissibility failed at 4 of 6 sizes); then build the 131-bit signed-Frobenius walk.

next_action.discriminates (verbatim):

> Settles strongest_available for Table A's rho_reference (the only missing piece of a VALIDATION.json for rule v4); a stronger reference widens the gap.


forecloses: Table A rho reference is fair; point halving rho step on Koblitz curves; no matched rho for ECC2K-130 IC lanes; Frobenius-class walk constant sqrt(2n)


**AUD-1.** n/a (pass applies to other dispositions)


**AUD-2.** n/a (pass applies to other dispositions)


**AUD-3.** n/a (pass applies to other dispositions)


**AUD-4.** No theorem decides an implementation constant. Evidence addition: `/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/crypto-main/docs/bounds/FRONTIER.md`, domain 'ecdlp.single_target . koblitz . planted targets . ecbench.gae . tier medium', names `rho.signed_frobenius_strong` (ECBND1hcf69c27b4978, 1.089x floor [0.927, 1.261], sizes 32.1-47.2) as ops leader. Those sizes include the Table A sizes 36.6-47.2. This is in GAE, a counted unit; Table A is in batched-addition clock units, and the leaderboard forbids converting between them ('No conversion to table A's or C's unit is applied or claimed'). So it informs which method is strongest in counted operations, not Table A's priced reference. Cite it as context; it does not settle strongest_available.


**AUD-5.** n/a (pass applies to other dispositions)


**AUD-6.** n/a (pass applies to other dispositions)



## LEAD-ICB-koblitz-setup-phase-cost

- file: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/ic-binary/LEAD-ICB-koblitz-setup-phase-cost.yaml`
- disposition: `open_next_step`
- title: Cutting the reusable set-up of the one-target Koblitz pipeline (Table A), where 98.5-99.7% of S sits


next_action.step (verbatim):

> Port the S3 root-index build and the rank finder from the cryptanalysis n = 83 producers (experiments/koblitz-n83-indexbuild2-20261020, koblitz-n83-rankfinder-20261021) into the Rust `ic price` pipeline (estimated 3-5 days; rule v4 README, follow-ups), then re-run the rule-v4 paired panel on a host where the heavy-compute lock is honoured.

next_action.discriminates (verbatim):

> A paired cold ratio below 1 at >= 4 of 6 sizes is a Table A baseline improvement; no movement means the n = 83 levers are specific to the S3 pipeline's cost profile.


forecloses: speed up the Koblitz pair-table build; retune K for the one-target Koblitz rows; batched or cache-blocked table construction for compact orbit IC


**AUD-1.** n/a (pass applies to other dispositions)


**AUD-2.** n/a (pass applies to other dispositions)


**AUD-3.** n/a (pass applies to other dispositions)


**AUD-4.** No theorem decides it. The ceiling on what set-up engineering can buy is SO-TABLE: rows sit 2^25-2^27 above the generic line (LEAD-ICB-generic-table-oracle), so constant cuts have room but cannot cross sqrt(r/2n). The queued port-and-panel is the right step. No change.


**AUD-5.** n/a (pass applies to other dispositions)


**AUD-6.** n/a (pass applies to other dispositions)



## LEAD-ICB-large-prime-variants

- file: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/ic-binary/LEAD-ICB-large-prime-variants.yaml`
- disposition: `open_next_step`
- title: Single and double large-prime relation collection for binary and Koblitz IC (free-leg, GTTD on subspace bases)


next_action.step (verbatim):

> Implement and run the approved Stage 0 of EXP-BINSTD-e066d8 (large-prime rows of the KN-FIND-aa2efc free-oracle floor), and add a 1LP/2LP arm to the compact-orbit relation stage at n = 53 and 61 (Table C sizes where relation collection is 56-79% of S), paired against the incumbent in the counted unit; the orphan module large_prime_filter.rs is the starting point.

next_action.discriminates (verbatim):

> A counted-S ratio below 1 is a constant advance on the relation phase; Stage 0 confirming the free-leg birthday dominance by matched rho closes the subspace-base large-prime line in the enumeration oracle class.


forecloses: double large prime variation on ECC2K-130 subspace bases; free last leg decomposition as a large prime; large-prime graph for Koblitz index calculus


**AUD-1.** n/a (pass applies to other dispositions)


**AUD-2.** n/a (pass applies to other dispositions)


**AUD-3.** n/a (pass applies to other dispositions)


**AUD-4.** **Half of the queued step is already decided by a theorem.** The second outcome of discriminates is 'Stage 0 confirming the free-leg birthday dominance by matched rho closes the subspace-base large-prime line in the enumeration oracle class'. A large-prime variant built on a generic (table/enumeration) oracle is still a generic algorithm. Shoup's bound and the CGK bound of LEAD-ICB-generic-table-oracle apply to the complete algorithm, large primes included. So 'subspace-base large primes in the enumeration oracle class cannot beat sqrt(r/|Aut|)' is decided by SO-TABLE without Stage 0. Outcome map after the split: (a) asymptotic large-prime route with a generic oracle -> closed_obstructed (theorem, SO-TABLE); (b) counted-S constant of a 1LP/2LP arm vs the compact-orbit incumbent at n = 53, 61 -> stays open_next_step (baseline engineering; Table C relation share 56.3% and 78.8% at n53, n61 in `docs/ic/LEADERBOARD.md` phase table); (c) large primes with an algebraic oracle (Gaudry/GTTD, KR-IC-46d822) -> belongs to LEAD-ICB-composite-degree-c2pnb and LEAD-ICB-oakley-quintic-tower. Note: `problems/binary-subfield-base-has-no-large-prime-component.md` is about a large prime subgroup, not the large-prime variation, and is not evidence here.


**AUD-5.** n/a (pass applies to other dispositions)


**AUD-6.** n/a (pass applies to other dispositions)



## LEAD-ICB-multi-target-and-portfolio

- file: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/ic-binary/LEAD-ICB-multi-target-and-portfolio.yaml`
- disposition: `closed_obstructed`
- title: Batch IC and IC/rho portfolios: amortising the set-up over many targets, restart portfolios

- obstruction.kind: `theorem`

obstruction.statement (verbatim):

> The multi-instance generic bound (L logarithms cost >~ sqrt(L r/|Aut|)) covers generic-oracle IC including its set-up, and batch rho (Kuhn-Struik) attains it; the L^-1 amortisation applies only to the online part after a set-up that obeys the same bound. A restart portfolio IC + rho cannot beat pure rho when IC cost is concentrated at a floor ratio >= 1 (H-BINSTD-32867d supported). The four-target union column is a rare-event linearisation, not a batch speed-up. Measured: Table C (32 targets) stays 3.62-14.9x above batch rho.

obstruction.revisit_when (verbatim):

> A non-generic oracle (then amortisation matters), or IC attempt costs that are heavy-tailed with median within about two orders of magnitude of rho.


forecloses: index calculus amortises as 1/L so batch IC beats batch rho; IC and rho restart portfolio; four-target union column as a batch speedup; shared set-up across many Koblitz targets


**AUD-1.** Not fired, but half the second clause holds. Its median condition ('median within about two orders of magnitude of rho') is met by the current board (Table A 5.23-21.0x, Table C 3.62-14.9x, `docs/ic/LEADERBOARD.md`). The heavy-tail condition is unmeasured. Interpretation: with 98.5-99.7% of S in target-independent set-up (phase table), the IC cost distribution is expected to be concentrated, not heavy-tailed. This is checkable from the existing 64-targets-per-size rule-v3 data (`crypto/research/ic_tool_program/rule/v3/analysis.json`) without new runs.


**AUD-2.** Scope consistent (generic-oracle IC; batch rho attains the bound). No flag.


**AUD-3.** Kind is theorem; the portfolio clause (H-BINSTD-32867d supported) is a short argument already. Pass not required.


**AUD-4.** n/a (pass applies to other dispositions)


**AUD-5.** n/a (pass applies to other dispositions)


**AUD-6.** SO-MULTI (L logs cost >~ sqrt(L r/|Aut|)). Takes it as hypothesis: the NFS/finite-field precomputation theory, where 1/L amortisation after a non-generic precomputation is the norm. So 1/L amortisation observed on an EC oracle would itself witness non-genericity. None found that is generative on EC.



## LEAD-ICB-nonlinear-frob-stable-bases

- file: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/ic-binary/LEAD-ICB-nonlinear-frob-stable-bases.yaml`
- disposition: `open_next_step`
- title: Non-subspace Frobenius-stable factor bases at prime n: trace-spectrum, Hamming ball, multiplicative subgroup, tau-adic, algebraic-group (Couveignes-Lercier) points


next_action.step (verbatim):

> Run the approved matched-|F| per-attempt cost comparison: trace-spectrum V_E (H-CERTBIN-5a81ca) and normal-basis Hamming ball B_w (H-CERTBIN-ec0945) against a random subspace on RC-1 (n = 17) and a Koblitz n = 19 cell, in D <= 5 closure work and WDSat conflicts with a size-matched null; in parallel finish the dimension-5/6 Weil-polynomial census over F_2 for 131 | #A (H-FROB-ff99bf hit an impediment at dims 5-6; H-BINSTD-944a66 has preliminary support) and read the Couveignes-Lercier primary source.

next_action.discriminates (verbatim):

> Per-attempt cost within [0.5, 2] of the subspace arm keeps the n-fold gain at prime n and justifies an n = 131 price; cost above 2x means the stable structure is paid back in membership cost and the non-linear stable lane closes. A census with no dimension-5/6 abelian variety having 131 | #A closes the Couveignes-Lercier route at g <= 6.


forecloses: Hamming-ball factor base in a normal basis for ECC2K-130; trace-spectrum or trace-conditioned Frobenius-stable base at prime degree; Couveignes-Lercier elliptic periods or algebraic-group factor base at n = 131; multiplicative-subgroup x^d = 1 factor base on Koblitz curves; tau-adic factor base over an orbit union


**AUD-1.** n/a (pass applies to other dispositions)


**AUD-2.** n/a (pass applies to other dispositions)


**AUD-3.** n/a (pass applies to other dispositions)


**AUD-4.** **The census branch is already decided, and its closing outcome is excluded.** discriminates says 'A census with no dimension-5/6 abelian variety having 131 | #A closes the Couveignes-Lercier route at g <= 6'. Observations: (1) `/Volumes/SSD990-2/crypto-autoresearcher/ledger/evidence/EV-BINSTD-2d41c3.yaml` (2026-10-01, cited in this lead's own evidence list) records 'g=5 outcome B (24 sympy-agreed hits, LMFDB 14325, amb=0)'. (2) Independent LMFDB query run in this audit (`/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/audit/lmfdb-av-f2-131.json`): av_fq_isog over F_2 has 0 classes with 131 | #A(F_2) for g <= 4; 24 of 14,325 for g = 5 (all simple, 11 with has_jacobian = 1, e.g. 5.2.b_d_e_h_n); 617 of 164,937 for g = 6 (497 simple, 173 with has_jacobian = 1). The class totals equal the completeness denominators in EV-BINSTD-2d41c3, and the g = 5 count equals its 24 hits. Interpretation: an abelian variety over F_2 of dimension 5 with a rational point of order 131 exists (Cauchy), including Jacobians of genus-5 curves. This is an existence precondition for the Couveignes-Lercier construction only; it says nothing about membership degree or factor-base cost. **Ledger inconsistency for the Coordinator** (no status moved here): H-FROB-ff99bf claims 'For every abelian variety A of dimension g in {5, 6} over F_2, the point count #A(F_2) is NOT divisible by 131' (`ledger/.index/hypotheses.jsonl`, status analyzed), and EV-FROB-a85eaf (2026-10-07) records 'dimension >= 5 open'. Both are contradicted at g = 5 by EV-BINSTD-2d41c3 and by the LMFDB rows above. The lead's next_action still says to 'finish the dimension-5/6 Weil-polynomial census'. That clause can be dropped: what remains is the matched-|F| per-attempt cost arm, plus reading the Couveignes-Lercier primary source to learn what the 24 (g = 5) classes would have to supply.


**AUD-5.** n/a (pass applies to other dispositions)


**AUD-6.** n/a (pass applies to other dispositions)



## LEAD-ICB-oakley-quintic-tower

- file: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/ic-binary/LEAD-ICB-oakley-quintic-tower.yaml`
- disposition: `open_next_step`
- title: Gaudry-Diem n = 5 point decomposition on the Oakley EC2N curves over F_{2^155} and F_{2^185}


next_action.step (verbatim):

> Execute the approved Oakley ladder contracts (EXP-OAKLEY-2c0552, -4276c4, -7f73ef have trial plans and no runs): chained S_3 vs S_6 on identical instance bytes at n = 5, the SAT arm on E/F_{2^{5p}} with V = F_{2^p}, and the measured K_5; price both against the GHS genus-16 route at the same cells.

next_action.discriminates (verbatim):

> Direct n = 5 decomposition below the GHS price makes it the better route to the two Oakley groups; above it, the lane is dominated by the GHS transfer (transfer family) and closes.


forecloses: Oakley group 3 or 4 by point decomposition; n = 5 Gaudry-Diem on F_{2^155}; S_6 versus chained S_3 at n = 5


**AUD-1.** n/a (pass applies to other dispositions)


**AUD-2.** n/a (pass applies to other dispositions)


**AUD-3.** n/a (pass applies to other dispositions)


**AUD-4.** **A cost-model inequality decides most of the outcome space before the ladder.** Inputs: rho sqrt(pi r/4) = 2^75.8 (group 3) and 2^91.3 (group 4) group ops. GHS advantage after correction is +1.1 and +10.9 bits, so GHS is about 2^74.7 and 2^80.4 (`/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/crypto-main/research/cover_route_prime_binary_20261008/README.md` lines 92-133). Gaudry's n-fixed constant grows like n!*2^{n(n-1)} (KR-IC-46d822), i.e. a symmetrised system of degree D ~ 2^20 at n = 5. Model: relations ~ q/2 at n! = 120 trials each is 2^{36.9} trials at q = 2^31. With per-trial cost >= D^beta F_q-operations, Gaudry n = 5 beats GHS on group 3 iff 36.9 + 20*beta - c < 74.7, with c = log2(cost of one F_{2^155} group op / one F_{2^31} op). That gives beta < (37.8 + c)/20. On group 4 (q = 2^37, 2^{42.9} trials) the condition is beta < (37.5 + c)/20. Since the lead's mechanism says K_5 is 'one q-independent Groebner constant', a single K_5 measurement at one toy q decides the S_6 arm against this threshold. Outcome map: K_5 < 2^{37.8+c} F_q-ops -> run the full contract; above it -> closed_dominated by the GHS transfer. Conditional on the KR-IC-46d822 constant; the chained S_3 arm has a different D and needs its own measurement.


**AUD-5.** n/a (pass applies to other dispositions)


**AUD-6.** n/a (pass applies to other dispositions)



## LEAD-ICB-orbit-linear-algebra

- file: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/ic-binary/LEAD-ICB-orbit-linear-algebra.yaml`
- disposition: `exhausted_at_scale`
- title: Linear algebra of the orbit-folded relation matrix (equivariant blocks, sparse filters, Wiedemann, CADO-style merge)

- obstruction.kind: `measured`

obstruction.statement (verbatim):

> Linear algebra is 0.0-2.7% of S in every Table A-C row, so no LA speed-up moves the board: the CADO-style filter is 2.48-10.4x faster on the phase alone and 1.93x faster than CADO-NFS at 262,144 columns, sparse-cado in ic.pipeline spends 0.25-0.72x the LA wall at identical S. The ECC2K-130 F_r[Z/131] structure is exhausted by the orbit quotient (ord_131(r) = 1 leaves only the lambda-eigenblock live). Scale reached: 262,144 columns.

obstruction.revisit_when (verbatim):

> Factor bases of 10^6+ columns or a large-prime arm that makes linear algebra a material share of S.


forecloses: block Wiedemann for the Koblitz relation matrix; equivariant linear algebra over F_r[Z/n]; sparse filtering makes IC beat rho


**AUD-1.** Not fired for this lead's scope. Delta IDEA-20261018-670088 reports, as a proposal context, that in the genus-3 double-large-prime pipeline 'linear algebra (local q^1.52) is the next lever'. That is a large-prime arm making LA material, but in a different family and pipeline, not the Koblitz orbit-folded matrix. IDEA-20261018-1bc873 (wire block Wiedemann into ic.pipeline) is unrun tooling. The open LEAD-ICB-large-prime-variants 1LP/2LP arm is the in-family event that would fire it.


**AUD-2.** **Over-broad foreclose.** The statement is scoped to Tables A-C and 262,144 columns. The phrase 'sparse filtering makes IC beat rho' is unscoped and would block the genus-3 2LP pipeline idea IDEA-20261018-670088, where LA is reported as the bottleneck. Recommend 'sparse filtering moves a Koblitz Table A-C row'. The phrase 'block Wiedemann for the Koblitz relation matrix' is correctly scoped.


**AUD-3.** **Short proof replaces the measured closure (conditional on the measured shares).** Amdahl: if LA is a fraction s of S, any LA speed-up gives S'/S >= 1 - s. With s <= 0.027 (phase table), no LA change moves any Table A-C row by more than 1/(1 - 0.027) = 1.028x. The measured part is only the share. Lean target below. Caveat for asymptotics: at the ECC2K-130 scale the generic-table lead quotes K* ~ 4e11 columns, where K^2-type LA (~2^77) exceeds rho. LA share is small only at board scale, which the revisit clause already captures.


**AUD-4.** n/a (pass applies to other dispositions)


**AUD-5.** n/a (pass applies to other dispositions)


**AUD-6.** Not a standing obstruction. None found.



## LEAD-ICB-prime-degree-algebraic-decomposition

- file: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/ic-binary/LEAD-ICB-prime-degree-algebraic-decomposition.yaml`
- disposition: `open_blocked`
- title: Bounded-degree algebraic decomposition (Weil-descended S_{m+1} on subspace bases) at prime extension degree: ECC2K-130, NIST K/B, sect571


next_action.step (verbatim):

> Measure the F4 / degree-4 closure refutation degree at (m, l) = (4, 5) and (4, 6), and m = 5 with |V| = 8, plus the conversion K (rho steps per column touch) on the same host; price n = 131 in one unit.

next_action.discriminates (verbatim):

> Degree staying at 4 makes the modelled m = 4 price about +9.8 bits over rho at n = 131 (median K), the closest any ECC2K-130 or sect571 route has come, and justifies an n = 131 cost table; degree >= 5-6 puts it at +21 to +112 bits and closes the lane by measured scaling.


next_action.blocked_by (verbatim):

> Memory: (4,5), (4,6), (13,4) and (13,5) exceeded the 3 GB cap (msolve segfaults at 1.6-1.8 GB RSS); the m = 5, |V| = 8, D = 4 cell (~112k columns) and the (15,5) degree-7 XL cell (110-120 GB) need a 32-128 GB host; no 131-bit rho walk exists to measure K at n = 131 (IDEA-20261015-c6f017).


forecloses: solving degree stays bounded for Weil descent at m = 4 on ECC2K-130; first fall degree assumption makes binary ECDLP subexponential; Semaev 2015 regime for B-571 or K-571; mutant or degree-4 closure as a sub-rho decomposition oracle; index calculus on K-163 or B-163 at prime degree


**AUD-1.** n/a (pass applies to other dispositions)


**AUD-2.** n/a (pass applies to other dispositions)


**AUD-3.** n/a (pass applies to other dispositions)


**AUD-4.** **(1) Split blocked_by; one blocker has a new route.** The K clause ('no 131-bit rho walk exists to measure K at n = 131') is addressed by IDEA-20261018-e7a860 (delta): 'K, the number of ecbench group operations (GAE) per Macaulay column touch in the current m=4 oracle, is measurable' by field-operation counters, estimated cost 'low (one perf-ipc session)'. That needs no 131-bit walk. K is also already modelled at median 4.48 [3.96, 16.77] (`crypto/research/k_conversion_20261018/README.md`). The memory clause stands, but IDEA-20261018-1aff90 proposes a GF(2) block Wiedemann consistency test 'using memory at least 10x below the dense approach' that yields an upper bound on the (4,6) degree. So the lead stays open_blocked on memory for the exact degree, with an unblocked bound-only route. **(2) The outcome map caps the result.** By the lead's own discriminates, the best outcome (degree stays at 4) is '+9.8 bits over rho at n = 131 (median K)'. So no outcome of the blocked run produces a sub-rho row; it decides distance only. A paper stack decides whether any combination could close +9.8 bits: FGHR 2-torsion symmetrisation, priced at 30-416x (4.9-8.7 bits) in IDEA-20261018-6c1c6e, plus the geometric-progression profile lever (cryptanalysis pdp-degree-heuristics finding 5). If the stacked constants sum to < 9.8 bits, the memory-heavy run measures only distance remaining. Context: delta DEC-20261024-e29f4c opened GOAL-PEXT-4a1d6b (prime-degree extension descent, 'understanding how it works rather than as an attack'), which owns the theory side.


**AUD-5.** n/a (pass applies to other dispositions)


**AUD-6.** n/a (pass applies to other dispositions)



## LEAD-ICB-quasi-subfield-polynomials

- file: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/ic-binary/LEAD-ICB-quasi-subfield-polynomials.yaml`
- disposition: `closed_obstructed`
- title: Quasi-subfield-polynomial factor bases (Huang-Kosters-Petit-Yeo-Yun; Euler-Petit) at prime extension degree, ECC2K-130

- obstruction.kind: `theorem`

obstruction.statement (verbatim):

> Euler-Petit Theorem 1: every linearized QSP has beta >= 3/4, so under the HKPYY cost model the exponent is >= 0.93, i.e. >= 2^122 at n = 131 against rho 2^60.9; for F_2-coefficient lambda only X^2 + X (n0 = 1) and L_Phi131 (n0 = 130) exist at n = 131 (Prop. 2), and multiplicative QSPs give |V| = 264 or p + 1, beta >= 1.02. The crypto census also shows Lemma 4.1 tight (the n mod n0 term cannot be removed; witnesses at n = 7). Measured at toy n = 31, k = 15: QSP bases yield 0.214 against 0.204-0.230 for random subspaces (no gain).

obstruction.revisit_when (verbatim):

> A non-linearized or correspondence-defined QSP family (IDEA-20260916-a17f43) whose root count escapes the Frobenius-injection bound, or an exhaustive search past n = 47 finding log2(deg lambda) < n0^2/n at prime n.


forecloses: quasi-subfield polynomial factor base for ECC2K-130; search for split X^{2^k} - lambda(X) at prime n as a factor base; QSP no-Weil-descent chain beats rho on binary curves; remove the n mod n0 term in HKPYY Lemma 4.1


**AUD-1.** Not fired. No delta item reports a non-linearized or correspondence-defined QSP family, or a search past n = 47.


**AUD-2.** **Theorem scope narrower than the foreclose.** The statement proves beta >= 3/4 for linearized QSPs (Euler-Petit Theorem 1), covers F_2-coefficient lambda at n = 131 (Prop. 2) and multiplicative QSPs, and names non-linearized families as the revisit condition. KR-IC-49c882 says the same ('Euler-Petit prove beta >= 3/4 for linearised complete splitters, and existence of useful families remains open'). The phrase 'search for split X^{2^k} - lambda(X) at prime n as a factor base' is unqualified and so covers general (non-linearized, F_{2^n}-coefficient) lambda, which no cited theorem covers. Recommend 'search for split linearized X^{2^k} - lambda(X) ...'. The n = 131 cost '>= 2^122' is conditional on the HKPYY cost model.


**AUD-3.** Kind is theorem. The measured toy clause ('QSP bases yield 0.214 against 0.204-0.230 for random subspaces') is implied by KN-FIND-007 (mean yield is base-independent), so it carries no evidence about the QSP mechanism, which is a degree lever, not a yield lever. Recommend labelling it as a control, not as part of the obstruction.


**AUD-4.** n/a (pass applies to other dispositions)


**AUD-5.** n/a (pass applies to other dispositions)


**AUD-6.** SO-QSP (beta >= 3/4). The HKPYY cost model itself takes beta as a parameter (the exponent is a function of beta); a theory that would take beta < 3/4 as hypothesis needs non-linearized splitters, which is the open part. None found that turns the bound into a construction.



## LEAD-ICB-retained-setup-online

- file: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/ic-binary/LEAD-ICB-retained-setup-online.yaml`
- disposition: `closed_dominated`
- title: Retained-setup online IC on Koblitz curves (n = 61, 71, 73, 83): online ratio after an uncharged precomputation

- obstruction.kind: `measured`

obstruction.statement (verbatim):

> Dominated by Bernstein-Lange preprocessing rho (generic family): at equal or smaller advice it is 53-317x faster online than IC at n61, and precomputed-table rho wins every matched N83 pair (K3300: 3.74x time-matched, 40.6x memory-matched; K600: 81.5-215x time-matched, 396x memory-matched). The published online wins used rho with an empty distinguished-point table; the validation sweep (2026-10-20, sweep-B rows 104.1, 108.1, 110.1) marked them contradicted. Theorem side: the IC table sits 2^25-2^27 above the CGK S*T^2 line that preprocessing rho attains.

obstruction.revisit_when (verbatim):

> An online IC whose S*T^2 lies at or below r/|Aut| (a non-generic oracle), or advice shared across many curves that preprocessing rho cannot share.


forecloses: IC online after precomputation beats rho on Koblitz curves; N83 or n61 online speedup over rho; reuse the pair table across many targets to beat rho; retained-setup class win


**AUD-1.** Not fired. Delta IDEA-20261018-4c28fc proposes extending the Bernstein-Lange instrument to n = 73, 83 with log2(S*T^2) - log2(r/|Aut|) recorded; unrun. No shared multi-curve advice appears.


**AUD-2.** Scope consistent: the dominance is measured at n61 and N83, and the theorem side (CGK line) is generic-oracle. No flag.


**AUD-3.** Kind measured, backed by the CGK theorem. A short lemma would make dominance formal given a measured (S, T): if BL preprocessing rho attains T_BL <= c*sqrt(r/(|Aut| S)) for advice S, and IC has S_IC*T_IC^2 > c^2 r/|Aut|, then BL with S = S_IC has T_BL < T_IC. This is algebra given BL's (heuristic) guarantee; low value. No finding returned.


**AUD-4.** n/a (pass applies to other dispositions)


**AUD-5.** n/a (pass applies to other dispositions)


**AUD-6.** Not a standing obstruction (dominance). See SO-TABLE under LEAD-ICB-generic-table-oracle.



## LEAD-ICB-tau-horner-chain

- file: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/ic-binary/LEAD-ICB-tau-horner-chain.yaml`
- disposition: `open_next_step`
- title: tau-Horner decomposition chain on Koblitz curves (R = tau^{m-1}P_1 + ... + P_m over one base)


next_action.step (verbatim):

> Run IDEA-20261018-f2cd4d: cost per distinct relation of the plain, symmetry-broken and tau-Horner chains at matched core size on toy Koblitz n in {17, 19, 23}, m in {2, 3}, with a size-matched ordinary-curve null.

next_action.discriminates (verbatim):

> Horner cheaper per distinct relation than the symmetry-broken chain is a constant m! advance for the collection stage; equal cost means the Horner m! is the symmetry-breaking m! relabelled (accounting, not an improvement), and the lead closes.


forecloses: tau-Horner chain kills the m! factor; tau-adic ordered decomposition on Koblitz curves; Horner-form relations multiply yield by m!


**AUD-1.** n/a (pass applies to other dispositions)


**AUD-2.** n/a (pass applies to other dispositions)


**AUD-3.** n/a (pass applies to other dispositions)


**AUD-4.** **A counting identity decides the m! accounting before the run.** IDEA-20261018-f2cd4d (`/Volumes/SSD990-2/crypto-autoresearcher/ledger/proposals/IDEA-20261018-f2cd4d.yaml`) states it: 'Plain+SB searches 2^(ml)/m! and has B^m/(m! r) unordered solutions; Horner searches 2^(ml) and has B^m/r ordered ones; both cost c 2^(ml) r/B^m per relation'. In the exhaustive-core regime (cost proportional to search space) this is a two-line double count. Second identity: when the base is tau-stable (orbit base), (P_1, ..., P_m) -> (tau^{m-1}P_1, ..., P_m) is a bijection of F^m. Horner relations are then plain ordered relations relabelled, and in the orbit-folded matrix they are the same rows. Outcome map: identity holds (provable) -> the m! Horner yield is the WDSat symmetry-breaking m! (KR-IC-5765d2), and the lead becomes closed_dominated by plain chain + symmetry breaking in the exhaustive regime. The queued run then only checks the solver constant against the frozen band [0.8, 1.25]: in band -> confirms; outside -> the regime assumption (cost proportional to search space) failed, and the lead stays open for the non-exhaustive (algebraic) regime. There, plain chains can also use S_m symmetrisation and Horner cannot, so Horner is not expected to gain.


**AUD-5.** n/a (pass applies to other dispositions)


**AUD-6.** n/a (pass applies to other dispositions)



## Lean target candidates (informal statements)

Each is short. Hypotheses, quantifiers and conclusion are stated; none is claimed proved here.

**LT-1 (yield conservation + Markov; used by LEAD-ICB-factor-base-subspace-choice, LEAD-ICB-frobenius-orbit-factor-base, LEAD-ICB-kic-golden-base-exact-decomp, LEAD-ICB-quasi-subfield-polynomials).** Let G be a finite abelian group of order N, D a subset of G with |D| = B, and m >= 1. For r in G let c_D(r) be the number of size-m multisets from D summing to r. Then (a) sum_{r in G} c_D(r) = binomial(B+m-1, m); (b) #{r in G : c_D(r) >= 1} <= binomial(B+m-1, m). Hence for r uniform on G, P(c_D(r) >= 1) <= binomial(B+m-1, m)/N, for every D of size B. Part (a) is KN-FIND-007 (derivation); part (b) is the new content and is what bounds every coverage-engineering gain.

**LT-2 (beat-rho threshold; LEAD-ICB-decomposition-encoding-and-sat).** For real n > 0, integer m >= 2 and real alpha: there exists real l with 0 < l <= n/m and n + l(1 + alpha - m) < n/2 if and only if alpha < m/2 - 1. (Model: log2 total relation cost = n + l(1 + alpha - m) up to the m! constant, with decomposition probability 2^{ml - n} needing l <= n/m.)

**LT-3 (basis invariance of the refutation degree; Proposition B of LEAD-ICB-decomposition-encoding-and-sat).** Let F be a finite set of polynomials in the Boolean ring B_N = F_2[x_1..x_N]/(x_i^2 + x_i), and A an invertible F_2-affine map of F_2^N. For every d >= 1: 1 lies in the degree-<= d linear span {sum g_i f_i : deg(g_i f_i) <= d} of F iff 1 lies in the corresponding span of F o A. Consequently the XL/closure refutation degree is the same under any change of F_2-basis of F_{2^n} or of defining polynomial. (No claim about CDCL conflict counts.)

**LT-4 (no automorphism stabilizes a target; LEAD-ICB-frobenius-search-symmetry revisit_when).** Let r be prime, R a nonzero element of Z/r, and lambda in (Z/r)^*. If lambda*R = R then lambda = 1. Hence no non-identity element of <pi, -1> acting on a prime-order subgroup fixes a target R != O.

**LT-5 (Amdahl bound; LEAD-ICB-orbit-linear-algebra).** Let S = S_LA + S_rest with S_LA, S_rest >= 0 and S_LA <= s*S for some 0 <= s < 1. For every S'_LA >= 0, S' = S'_LA + S_rest satisfies S' >= (1 - s) S. With s = 0.027 the maximal speed-up of S from any LA change is 1/(1 - s) < 1.028.

**LT-6 (coprime filters carry no r-information; LEAD-ICB-cofactor-torsion-quotients).** Let G = H x C_r be a finite abelian group with r prime and r not dividing |H|, and f : G -> Q a group homomorphism to a finite abelian group Q with r not dividing |Q|. Then f(x) = f(pi_H(x)) for all x in G; in particular f is constant on every coset of C_r, so an exactly sum-compatible homomorphic filter carries at most log2 |H| bits and none about the C_r component.

**LT-7 (tau-Horner is a relabelling on a stable base; LEAD-ICB-tau-horner-chain).** Let G be an abelian group, tau an automorphism of G, F a finite subset of G with tau(F) = F, m >= 1. The map Phi(P_1, ..., P_m) = (tau^{m-1}P_1, tau^{m-2}P_2, ..., P_m) is a bijection F^m -> F^m with sum_i Phi(P)_i = sum_i tau^{m-i} P_i. Hence for every R, #{Horner tuples over F with Horner sum R} = #{ordered tuples over F with sum R}; the Horner relation for Phi(P) and the plain ordered relation for P are the same vector in the tau-orbit-folded column basis. Companion arithmetic identity (exhaustive regime): (c 2^{ml}/m!) / (B^m/(m! r)) = c 2^{ml} / (B^m / r).

---

## Family: ic-engine

# Audit: ic-engine family (AUD-1..AUD-6)

Reviewer pass, 2026-10-24. Read-only over the repositories; every quote of `obstruction.statement`, `revisit_when` and `next_action` below is pasted verbatim from the YAML by `audit/gen_ice.py`. Arithmetic is reproducible with `python3 -I audit/calc_ice.py <crypto-main>` (output `audit/calc_ice.out`); lexical collisions with `audit/ice-match.txt` (lead_atlas.py --match). Observation and interpretation are separated: lines marked *interpretation* or *derivation* are this reviewer's reasoning, not recorded outcomes.

## Current state consulted (AUD-1 inputs)

- KRMAP.md (25 IC rows; KR-IC-5931ee, -fbdb61, -889857, -f5c584, -73db3f, -e847d1, -1fcdbc, -9e610d read in full).
- crypto docs/ic/LEADERBOARD.md (Tables A-D, Phases table, frontier audit rows) and docs/bounds/FRONTIER.md (prime toy tier: ic.pipeline mitm m = 2 at fixed base size 32, alpha 0.841 [0.646, 0.953]; subtract alpha 1.005).
- delta.txt: new findings KN-FIND-3c7e19 / 7e2b94 / c71e5d are CZLIFT p-adic section calibrations (transfer family), no ic-engine trigger; new problems read: dreg-c1-memory-cap-exhausted, semaev-degree-two-fall-nonzero-bridge, full-width-ic-arity-grid-unmeasured, icperf-prime63-* (crypto-autoresearcher), rootfinding-complete-cost-calibration (crypto, last updated 2026-10-14, still open); new decisions touching this family: DEC-20261018-9262ac (approves EXP-SEMBIN-24ec56; runs/ empty), DEC-20261022-a0f165 (GOAL-MONO-001 completed), DEC-20261023-19c53b (portfolio rank, zero runs), DEC-20261024-e29f4c (opens GOAL-PEXT-4a1d6b, prime-degree extension descent, no trials); new ideas relevant here: IDEA-20261018-1aff90, -1bc873, -2d21b9, -49fdf7, -5fa71b, -6c1c6e, -71a901, -88041d, -9fc21f, -a0830c, -ac3694, -b4bc61, -b90b0c, -c0b13a, -c49f37, -c4adb6, -e3bcff, -e7a860, IDEA-20261022-727676, IDEA-20261023-f15270 (all status proposed or null in ledger/.index/proposals.jsonl).
- KN-OPEN-5b3a08 audit update (2026-10-18): s4_expr fixed on main; exposure includes RUN-ICINV-e0cd8f-m3class (m4 columns).

## AUD-1 consolidated: leads whose revisit trigger fired

- LEAD-ICE-prime-field-semaev-solving-degree: fired in letter only (vacuous). EV-PFDR-acc71a: p-independence at fixed digit shape is forced, so it is no evidence. Rewrite the trigger on the s axis.
- LEAD-ICE-generic-oracle-arity-cost-floor: clause (a) partly fired, with handoff. A fixed-degree coordinate-reading oracle was measured at toy cells (research/dreg_closure_m4l6_20261018/RESULTS.md, research/dreg_hybrid_guess_20261024/RESULTS.md). It is outside this obstruction's scope, so the lead hands off to LEAD-ICE-descent-closure-degree-at-scale. Clause (b) can never fire (KN-FIND-007).
- LEAD-ICE-boolean-f4-f5-f6-engines, LEAD-ICE-semaev-chain-cost-model, LEAD-ICE-semaev-cover-monodromy: not fired (evidence in each subsection).

## Per-lead audit (19 leads)

### LEAD-ICE-generic-oracle-arity-cost-floor

- File: `knowledge/leads/ecdlp/ic-engine/LEAD-ICE-generic-oracle-arity-cost-floor.yaml`; disposition `closed_obstructed`, obstruction kind `cost_model`.
- obstruction.statement (verbatim): "For oracles of class ENUM, MITM and MITM_CAPPED on binary curves of prime degree n, the replicated v2 cost model has zero in-domain sub-rho cells (EV-SEMBIN-b6d042); on ECC2K-130 a free oracle at m = 3 still costs 2^68.58 against rho's 2^60.81 (KN-FIND-aa2efc); in-model, structured generic-group bounds (CHW 2026/384) and non-adaptive time-space bounds (DKM 2025/783) give the same wall. Scope: oracles that do not read curve coordinates algebraically; the FREE control does have sub-VOW cells, so the obstruction is the oracle class, not IC."
- revisit_when (verbatim): "An oracle that reads coordinates with per-query cost polynomial in n at fixed degree (see LEAD-ICE-descent-closure-degree-at-scale) is measured, or a non-generic yield exceeds C(B+m-1,m)/N on average."
- forecloses: "free decomposition oracle lifts IC below rho"; "arity threshold for point-decomposition index calculus"; "generic m-SUM decomposition oracle"; "larger arity m makes enumeration IC beat rho"; "multi-target amortisation rescues exhaustive-solver IC"
- **AUD-1.** Clause (b) cannot fire. It reads "a non-generic yield exceeds C(B+m-1,m)/N on average". KN-FIND-007 proves "E_r[c_D(r)] = binomial(B + m - 1, m) / N for every base of size B", so the uniform-target average equals that value for every base. Proposed rewrite: "a target-sampling rule whose per-sampled-target cost is O(1) GAE and whose conditional yield exceeds C(B+m-1,m)/N" (the conservation escape that LEAD-ICP-coincidence-harvest-structured-base names). Clause (a) is partly met: an oracle reading coordinates at fixed degree 4 has been measured at toy cells, (4,6) at N = 54 and (3,7) with k* <= 2 (LEAD-ICE-descent-closure-degree-at-scale; research/dreg_hybrid_guess_20261024/RESULTS.md). "Polynomial in n" is not established (the degree rises at l = 7 on random V). That oracle is outside this obstruction's stated scope anyway, so firing hands off to LEAD-ICE-descent-closure-degree-at-scale rather than reopening this lead. No disposition change.
- **AUD-2.** Over-reach flagged, in three places. (1) The forecloses phrase "free decomposition oracle lifts IC below rho" contradicts the lead's own evidence. KN-FIND-aa2efc: "The first row that is even in principle below rho is m = 4, at 2^56.40, and that is 2^-4.41 of headroom", and "the m >= 4 rows stay live work". EV-SEMBIN-b6d042: "The FREE control ... has 7,850 in-domain cells below the VOW column". The statement itself scopes the free-oracle cost to m = 3. Proposed: scope the phrase to "at m <= 3 on ECC2K-130", and add the m = 4 headroom 2^-4.35 (integer l = 27, RESEARCH_ECC2K130_DESCENT_DEGREE.md) to the statement. (2) "multi-target amortisation rescues exhaustive-solver IC" is not argued anywhere in this lead's statement. It belongs to SO-MULTI (LEAD-ICB-multi-target-and-portfolio). Proposed: drop the phrase or cite that lead. (3) Scope of the generic-group citations: CHW 2026/384 and DKM 2025/783 are invoked for ENUM/MITM. An oracle that tests x(R - F_i) in V by linear algebra on the bits reads coordinates; that test is not an equality query in the generic group model. The valid support for m <= 3 is the product law (counting, oracle-independent). The support for the ENUM/MITM zero-cell result is the v2 cost model. Proposed: attribute the m <= 3 wall to the product law and the m >= 4 ENUM/MITM wall to the cost model, not to the generic-group bounds.
- **AUD-3.** kind cost_model. A short proof replaces the core. Lean target candidate (product law, ENUM class): G is a finite abelian group of order N, D a subset of G of size B, m >= 1, and c_D(r) the number of size-m multisets of D summing to r. Then sum over r of c_D(r) = C(B+m-1,m). Hence an algorithm that queries uniformly random targets and receives every decomposition needs expected R*N/C(B+m-1,m) queries to collect R relations. If each query enumerates C(B+m-2,m-1) multisets (ENUM) and R >= B, then total oracle work >= B*N*C(B+m-2,m-1)/C(B+m-1,m) = m*N*(B/(B+m-1)) >= N for m >= 2 and B >= m-1. Second, model-level lemma (free oracle): for a, B > 0 and m >= 2, a/B^{m-1} + B^2 >= ((m+1)/(m-1)) * ((m-1)a/2)^{2/(m+1)} (AM-GM), with a = m!*N*T.
- **AUD-4.** n/a.
- **AUD-5.** n/a.
- **AUD-6.** Obstructing quantity: the product relations x targets x oracle = m*2^n. KN-FIND-aa2efc already reads it as a specification ("It says exactly what an m >= 4 oracle must cost to clear rho"). The oracle-budget calculus (per-query budget 2^{60.81-56.46} at ECC2K-130 m = 4) takes the product law as a hypothesis. The theory is time-space trade-off accounting, as for SO-TABLE.

### LEAD-ICE-semaev-chain-cost-model

- File: `knowledge/leads/ecdlp/ic-engine/LEAD-ICE-semaev-chain-cost-model.yaml`; disposition `closed_obstructed`, obstruction kind `cost_model`.
- obstruction.statement (verbatim): "Under Semaev 2015's cost model at n in [250, 600], t* = m* at every n under all three solving-cost readings, replicated by an independent optimiser (EV-SEMBIN-1d36a3); N = (t-2)n + tk is invariant over merge topologies, so charged cost is topology-blind (factor <= ~4 from sigma_top); the n = 409 storage indeterminacy is an artefact of the vOW operating point (EV-SEMBIN-4125ec)."
- revisit_when (verbatim): "A solver whose degree (not variable count) depends on topology, e.g. the transfer-matrix dynamic-programming Groebner variant (IDEA-20261016-7a138a), shows a topology-dependent closure degree on measured cells."
- forecloses: "chain length t less than m in Semaev chaining"; "merge-tree topology of S_3 chaining"; "memory-charged Semaev crossover against van Oorschot-Wiener"; "recharge Semaev Table 3 at integer k"
- **AUD-1.** Not fired. The trigger needs a topology-dependent closure degree measured with the transfer-matrix DP variant (IDEA-20261016-7a138a). That idea is status proposed (ledger/.index/proposals.jsonl) with no measurement. EXP-SEMBIN-24ec56 (approved DEC-20261018-9262ac, GOAL-SEMBIN-5078bc) has an empty runs/ directory (0 entries).
- **AUD-2.** Over-reach flagged. The scope is Semaev 2015's binary cost model at n in [250, 600] (F_{2^n}, Weil-descended). The forecloses phrases "chain length t less than m in Semaev chaining" and "merge-tree topology of S_3 chaining" carry no field qualifier. They would mark prime-field chained-tree work as known: IDEA-20260903-cf63ad ("chained t = 3 tree as in GOAL-DREG-001 but over F_p and with no Weil descent"). lead_atlas --match puts this lead first for "chain length topology prime field chained S_3 tree" (audit/ice-match.txt, score 18). Proposed: qualify both phrases with "binary, Semaev 2015 cost model".
- **AUD-3.** kind cost_model. A short proof replaces the topology-invariance half. Lean target candidate: every full binary tree with t >= 2 leaves has exactly t - 1 internal nodes. Hence a chained S_3 decomposition of R into t summands uses t - 1 S_3 equations and t - 2 intermediate points. With n-bit intermediates and k-bit summands the descended variable count is N = (t-2)n + tk for every merge topology. Corollary: any cost model that depends only on (N, number of equations, equation degree) is topology-invariant. The t* = m* half depends on the paper's explicit cost formula and stays a cost_model result.
- **AUD-4.** n/a.
- **AUD-5.** n/a.
- **AUD-6.** Obstructing quantity: the topology-invariant variable count N. The tree-decomposition / bucket-elimination complexity theory (Dechter-style variable elimination) takes the tree topology as its hypothesis, with cost |domain|^{treewidth+1}. With 2^n-valued intermediates that is >= 2^{2n} (interpretation), above rho. The transfer-matrix DP variant IDEA-20261016-7a138a is the in-program instance.

### LEAD-ICE-semaev-cover-monodromy

- File: `knowledge/leads/ecdlp/ic-engine/LEAD-ICE-semaev-cover-monodromy.yaml`; disposition `closed_obstructed`, obstruction kind `proof`.
- obstruction.statement (verbatim): "For every p > 3 and nonsingular E/F_p, the generic monodromy is (Z/2)^{m-2} (ordered base) and (Z/2)^{m-2} x| S_{m-1} (symmetric base, m >= 4) with an exact Frobenius rule on unramified fibres (KN-FIND-bdcd60, two blind re-derivations); on the factor-base locus S_m splits completely with an exact root multiset, so the generic-fibre cycle-type census is a no-go as a relation-rate probe at every m >= 3 (KN-FIND-4f0d84). GOAL-MONO-001 completed under DEC-20261022-a0f165."
- revisit_when (verbatim): "A rule-12 review breaks KN-FIND-4f0d84 or KN-FIND-bdcd60, or a factor-base statistic answering KN-OPEN-62c870 Q1/Q3 carries curve-specific relation-rate information."
- forecloses: "exceptional monodromy locus of Semaev summation cover"; "Frobenius cycle-type census as relation-rate probe"; "Chebotarev density of Semaev fibres"; "wreath-group monodromy over symmetric base"; "curve family with higher relation rate from Galois group"
- **AUD-1.** Not fired. KN-FIND-4f0d84 and KN-FIND-bdcd60 are not among the delta's changed paths. KN-OPEN-62c870 is unchanged in the delta. The new related records are proposals and rankings, not answers: IDEA-20261023-f15270 (status proposed, a re-scope onto KN-OPEN-62c870 Q3) and DEC-20261023-19c53b (portfolio rank: "approves no experiment ... launches zero runs").
- **AUD-2.** Over-reach flagged. The proof's scope is "every p > 3 and nonsingular E/F_p". The forecloses phrases are field-agnostic: "Chebotarev density of Semaev fibres", "Frobenius cycle-type census as relation-rate probe", "curve family with higher relation rate from Galois group". They would mark char-2 and extension-field variants as known. Those variants have different cover geometry and are explicitly open: DEC-20261023-19c53b records "Q3, extension fields (IDEA-20260803-ff7415)" as open content of KN-OPEN-62c870, and IDEA-20261023-f15270 quotes the F_p-to-F_{q^n} transfer as "an untested extrapolation". lead_atlas --match ranks this lead first (score 20) for "Frobenius cycle type census Semaev cover binary field F_2^n" (audit/ice-match.txt). Proposed: prefix every phrase with "over F_p, p > 3", and add to revisit_when "a monodromy computation over F_{2^n} or F_{q^n} (KN-OPEN-62c870 Q3)".
- **AUD-3.** n/a (closure kind `proof`).
- **AUD-4.** n/a.
- **AUD-5.** n/a.
- **AUD-6.** SO-MONO (this family's standing obstruction). Obstructing quantity: the uniform generic monodromy (Z/2)^{m-2} (ordered base) and (Z/2)^{m-2} x| S_{m-1} (symmetric base), with an exact Frobenius rule. Theory that takes it as a hypothesis: Chebotarev density in families (Deligne/Katz equidistribution). With the group known, it yields an exact null distribution of fibre cycle types for every curve. That null is a calibration resource for KN-OPEN-62c870 Q1 statistics: a factor-base statistic can be tested against the Chebotarev-predicted law rather than a simulated null. It is a hypothesis-use, not a mechanism. No theory found that turns the uniform group into a relation-rate gain.

### LEAD-ICE-prime-field-semaev-solving-degree

- File: `knowledge/leads/ecdlp/ic-engine/LEAD-ICE-prime-field-semaev-solving-degree.yaml`; disposition `closed_known`, obstruction kind `literature`.
- obstruction.statement (verbatim): "Naive Semaev IC over prime fields cannot beat generic methods (KR-IC-5931ee). The program reproduced it: at balanced L = q^(1/5) on ordinary toy curves, beta_work(B1) = 0.797 on interval and random bases and 0.647 on subgroup bases against the 0.30 sub-rho threshold, 36/36 cells, 105/105 FGLM checks (EV-SDEG-4a1c3d, strong); in ecbench the root-finding/pair-table oracle dominates any prime-field Groebner arm."
- revisit_when (verbatim): "A prime-field factor base whose membership equation has bounded degree independent of p (the base-d digit-map / PFDR descent, IDEA-20260830-84cdb7) produces a measured solving degree that stays flat across >= 3 field sizes."
- forecloses: "prime-field Semaev Groebner solving degree law"; "serial S_3 eliminant for sub-rho prime-field IC"; "subresultant pivot tree for prime-field decomposition"; "grevlex versus lex solving degree on F_p summation systems"; "semi-regular null for prime-field decomposition"
- **AUD-1.** Fired in letter, vacuously, so the trigger needs rewriting. The trigger asks for a PFDR digit-descent factor base whose "measured solving degree ... stays flat across >= 3 field sizes". EV-PFDR-acc71a (H-PFDR-09e1b0, recorded 2026-09-04) supports "at fixed digit shape the graded Macaulay invariants ... are p-independent above a small threshold prime", and states that "the three primes are three evaluations of a value that is forced for every odd prime, so nothing on the p-axis is an independent test". So at fixed (m, d, s) the solving degree is flat across p by construction. The trigger is met without any evidence of an early fall. EV-PFDR-1394a4 gives d_ff = m 2^{m-1} + floor((s - 2^{m-1})/2) + 1, which grows with s and is reproduced by a curve-free null. Proposed rewrite: "a digit or structured prime-field base whose last-fall or solving degree stays bounded as the digit count s (equivalently log B / log p at fixed relative base size) grows over >= 3 values, strictly below the support-matched / block-factored null (LEAD-ICP-digit-presentation-solving-degree next_action)". No disposition change.
- **AUD-2.** Mostly in scope. KR-IC-5931ee is a prime-field literature result, and every phrase is prime-field qualified. One phrase is a methodology phrase, not a mechanism: "semi-regular null for prime-field decomposition". It would mark the open lead LEAD-ICP-digit-presentation-solving-degree as known, because that lead's next step compares d_lf against "the semi-regular rate" with support-matched nulls. lead_atlas --match ranks this lead 6th for that wording (audit/ice-match.txt). Proposed: drop the phrase, or narrow it to "semi-regular null for direct-presentation interval/random bases".
- **AUD-3.** n/a (closure kind `literature`).
- **AUD-4.** n/a.
- **AUD-5.** n/a.
- **AUD-6.** Obstructing quantity (YYTK, KR-IC-5931ee): the membership polynomial of an interval/random base has degree |V|. The algebraic-factor-base programme (Petit-Kosters-Messeng tower; digit presentation IDEA-20260830-84cdb7) takes low membership degree as its hypothesis. It is in turn met by SO-ALGFB: "A target-independent algebraic locus of degree d yields O(d) usable points" (LEAD-ICP-algebraic-membership-factor-base). No other theory found.

### LEAD-ICE-boolean-f4-f5-f6-engines

- File: `knowledge/leads/ecdlp/ic-engine/LEAD-ICE-boolean-f4-f5-f6-engines.yaml`; disposition `closed_dominated`, obstruction kind `measured`.
- obstruction.statement (verbatim): "Dominated by LEAD-ICE-rootfind-pairtable-oracle on Koblitz and random-binary curves n <= 31, m in {2,3,4}: once its word XORs are priced (#1774), inherited F4 is about 22x-33x strong rho at K13 (n13) and the complete-S pair table is about 17x-22x cheaper than F4; F6-IC is 55x-6,483x rho (lower bound); in ic_m3_algebraic_vs_mitm F4 on the S_3 chain and F6-IC grow faster in n than the MITM floor (slope-difference CI above 0) at m = 3 and m = 4."
- revisit_when (verbatim): "A descended cell where the pair table is infeasible (m >= 4 at large n) and the algebraic degree stays bounded (LEAD-ICE-descent-closure-degree-at-scale), or a priced engine beats the MITM floor slope on >= 3 cells."
- forecloses: "faster F4 for Weil descent summation polynomial systems"; "F5 signature basis for point decomposition"; "M4RI GF(2) elimination speedup for PDP"; "GPU RREF Groebner decomposition"; "F4 trace reuse across decomposition targets"; "F6-IC geometric closure decomposition"
- **AUD-1.** Not fired. Clause 1 needs a descended cell where the pair table is infeasible (m >= 4 at large n) and the degree stays bounded. Observed: the bounded-degree cells are toy cells only. Closure degree 4 is recorded through (m,l) = (4,6) at N = 54 (crypto research/dreg_closure_m4l6_20261018/RESULTS.md, as summarised in LEAD-ICE-descent-closure-degree-at-scale). At those n the pair table is feasible. Clause 2: no priced engine beats the MITM floor slope. crypto research/ic_m3_algebraic_vs_mitm_20261014/README.md says "every finished algebraic arm grows faster than the MITM floor". The new ideas IDEA-20261018-e3bcff (GPU f4_gf2 port), IDEA-20261018-b4bc61 (crossbred) and IDEA-20261022-727676 (F4 replay lever) are all status proposed in ledger/.index/proposals.jsonl, with no measurement.
- **AUD-2.** Over-reach flagged. Observed scope of the statement: "Koblitz and random-binary curves n <= 31, m in {2,3,4}" (a measured constant ranking). Several forecloses phrases carry no field, size or arity qualifier: "faster F4 for Weil descent summation polynomial systems", "F5 signature basis for point decomposition", "GPU RREF Groebner decomposition", "F4 trace reuse across decomposition targets". Two collisions follow. (a) "F4 trace reuse across decomposition targets" would mark the prime-field idea IDEA-20261022-727676 as known. That idea is about the f4_fp_tower, the Petit-Kosters-Messeng tower over F_p, "systems of two targets differ only through x_R". The ranking that closed this lead was measured over F_2 only. lead_atlas --match puts this lead in the top 5 for that idea's wording (audit/ice-match.txt, score 8). (b) The unscoped "faster F4 ..." phrase also covers the open closure-degree engines (LEAD-ICE-descent-closure-degree-at-scale, LEAD-ICE-hybrid-guess-determine-l7). Interpretation: a small-n constant ranking is being used as a blanket closure. Proposed: qualify every phrase with "Boolean/Weil-descended, n <= 31, as a constant-level ranking against the pair table".
- **AUD-3.** kind measured. No short proof replaces it. The statement is a constant-level ranking of two implementations at n <= 31, and the m = 3/4 slope part is an empirical growth comparison. Proposed instead: scope the closure (AUD-2). No Lean target.
- **AUD-4.** n/a.
- **AUD-5.** n/a.
- **AUD-6.** Obstructing quantity: the per-query cost ratio of an algebraic engine to the table/MITM oracle. The crossbred / hybrid guess-and-determine framework (KR-IC-e847d1) takes this ratio as an input that sets the optimal split between enumeration and Macaulay preprocessing. It does not treat the ratio as a refutation. This framework is the one IDEA-20261018-b4bc61 proposes.

### LEAD-ICE-charged-toy-ic-exponent-vs-rho

- File: `knowledge/leads/ecdlp/ic-engine/LEAD-ICE-charged-toy-ic-exponent-vs-rho.yaml`; disposition `open_blocked`.
- next_action.step (verbatim): "Build the EXP-ICEX-153c34 backend (G1 membership, O5 oracle, S/G/X/V counters, admission-refusing driver) and pass S0 gates G0-1..G0-6 on smoke curves, then fit the crossover order log l* (IDEA-20260805-4d31bc) rather than a ratio exponent."
- next_action.discriminates (verbatim): "A measured crossover with both arms on the same instances fixes the distance to rho in one unit-invariant number; an empty crossover across the reachable range turns the lane into an exhausted_at_scale record with the reached size."
- blocked_by (verbatim): "EXP-ICEX-153c34 backend unbuilt; dispatch gated on the C-7 host-load gate (GOAL-ICEX-001 next_action)"
- forecloses: "charged toy index calculus exponent versus rho"; "fit IC exponent over four toy sizes"; "censoring-charged cost exponent"; "go/no-go on optimistic handed-over inputs"
- **AUD-1.** n/a (not a closed_* or exhausted_at_scale lead).
- **AUD-2.** n/a (no obstruction; forecloses checked, no scope note).
- **AUD-3.** n/a (open lead).
- **AUD-4.** A cost-model identity decides where a crossover can exist before the backend is built. Derivation (interpretation, conditional on the two-term model): take a uniform-target collection with mean yield C(B+m-1,m)/N (exact by KN-FIND-007), an oracle cost T per target, and linear-algebra or table cost proportional to B^2. Then min over B of (c N T / B^{m-1} + B^2) = Theta((N T)^{2/(m+1)}). This is below sqrt(N) only if T << N^{(m-3)/4}: never at m = 2; only T = O(1) ties at m = 3; T << N^{1/4} at m = 4. LEAD-ICP-generic-table-decomposition states the same m = 2 and m = 3 consequences ("m = 2 >= 3 (pT_dec)^{2/3} and m = 3 only ties rho even with T_dec = O(1)"). Constant at m = 3 under the same hypotheses (table/LA coefficient 1, yield B^3/(6N)): the minimum is 2*sqrt(6NT), i.e. at least 2*sqrt(6)/0.886 = 5.53*sqrt(T) times rho's 0.886 sqrt(N). Consequence for the queued crossover fit: at m = 2 the empty crossover is predetermined on exponents. At m = 3 it is predetermined under the model's constants for every T >= 1 GAE. A measured l* can exist only for the non-enumerative O5 oracle at m >= 4, and only if its fitted T(N) slope is below (m-3)/4. Mapping: measure the O5 per-query cost slope first. Slope >= (m-3)/4 at every m maps to exhausted_at_scale without running the full pipeline. Slope below it maps to the full crossover fit. IDEA-20261018-ac3694 records that the O5 backend (EXP-ICEX-153c34) is still unbuilt.
- **AUD-5.** n/a.
- **AUD-6.** n/a (no obstruction).

### LEAD-ICE-descent-closure-degree-at-scale

- File: `knowledge/leads/ecdlp/ic-engine/LEAD-ICE-descent-closure-degree-at-scale.yaml`; disposition `open_blocked`.
- next_action.step (verbatim): "Run the frozen dreg_closure C1 cell (m = 3, n = 19, l = 7, degree 5) and A2/B1/B2 cells on a host with >= 250 GB RAM (or a sparse closure), then (m, l) = (4, 7); report closure degree on >= 4 unsatisfiable draws plus satisfiable controls."
- next_action.discriminates (verbatim): "Degree 4 at l = 7 for m = 4 restores the "4, constant" row (2^68.43, still +7.6 bits over rho); degree 5 confirms the +10.32-bit optimistic bracket; degree >= 6 shows the degree grows with l and the binary-descent route has no constant-degree regime, closing this lead as obstructed."
- blocked_by (verbatim): "memory (C1 capped at 169 GB of 184 GB; projection 217 GB) - research/dreg_closure_m4l6_20261018/RESULTS.md"
- forecloses: "solving degree of Weil descent stays 4"; "first fall degree assumption makes binary ECDLP subexponential"; "MutantXL closure degree on summation polynomial systems"; "degree-capped certified decomposition"; "arity axis of bounded-degree refutation"
- **AUD-1.** n/a (not a closed_* or exhausted_at_scale lead).
- **AUD-2.** (Open lead; forecloses scope.) The phrase "solving degree of Weil descent stays 4" is broader than what was measured. Every closure cell used random subspaces: crypto research/dreg_hybrid_guess_20261024/PREREGISTRATION.md line 225 ("random l-dimensional subspaces of GF(2^n)"), research/dreg_closure_mutantxl_20261016/PREREGISTRATION.md ("random subspaces, n <= 13") and research/dreg_closure_scale_20261016/PREREGISTRATION.md line 122. The polynomial-basis / geometric-progression V of FPPR and Petit-Quisquater (KR-IC-73db3f) was never run at l = 7. Proposed: qualify the phrase with "random subspaces".
- **AUD-3.** n/a (open lead).
- **AUD-4.** A cheaper measurement gates whether the 250 GB run can change the cost verdict. Observed: crypto research/notes/ecc2k130/RESEARCH_ECC2K130_DESCENT_DEGREE.md section 2 prices the oracle in monomial-column touches at w = 1 ("one touch per column, which no elimination beats") against rho in group operations. It says "Converting would lower every row with an oracle by log2 K ... K is not measured" and "a reader should subtract log2 K from those gaps". The three outcomes of the blocked C1 step are +7.6 bits (degree 4), +10.32 (degree 5) and closed (>= 6), all in unconverted units. Mapping (derivation): if a measured log2 K < 7.62, all three outcomes stay above rho and the C1 run informs degree science only. It cannot change the ECC2K-130 verdict, so the lead can record its cost question as closed_obstructed (cost_model) and keep the degree measurement as instrument work. If log2 K >= 7.62, nothing is decided, because w = 1 is a lower bracket. The measured closure cost per column is far above one touch: about 2.9e6 word ops per column on (3,19,7) draw 3, branch 1 (audit/calc_ice.out, from the dreg_hybrid_guess RESULTS table). K is measured by IDEA-20261018-e7a860 and is already named in LEAD-ICB-prime-degree-algebraic-decomposition's next_action. Family-wide threshold from the same section 2 table: the m = 4, D = 2 "any Macaulay matrix" row sits at +2.07 bits (w = 1). So log2 K < 2.07 means no Macaulay-based m = 4 oracle beats rho at any degree. That threshold also settles the m = 4 rows of LEAD-ICB-prime-degree-algebraic-decomposition. The per-outcome thresholds are 7.62 for C1 and 8.43 for hybrid E8. Second cheap discriminator, which also serves LEAD-ICE-linearization-excess-fb-prior: fresh enumeration-certified UNSAT draws at (3,19,7) and (3,21,7) on V = c*span{1,g,...,g^6}, against random-V draws at the same (n, l) as the null, with satisfiable planted controls as before. The frozen draws cannot simply be reused, because an UNSAT label belongs to a (V, target) pair. If degree 4 refutes on the geometric-progression V while random V needs 5, the "degree rises at l = 7" rule is a random-base effect, and the m = 4 pricing must use the structured base.
- **AUD-5.** n/a.
- **AUD-6.** n/a (no obstruction).

### LEAD-ICE-first-fall-degree-assumptions

- File: `knowledge/leads/ecdlp/ic-engine/LEAD-ICE-first-fall-degree-assumptions.yaml`; disposition `open_blocked`.
- next_action.step (verbatim): "Discharge or refute the nonzero-residual bridge for the S_3 degree-two cancellation in Lean (formal/targets/semaev-s3-degree2-fall-witness.yaml), and fix fall_profile's representation defect before re-running the FFD_SEMAEV_MEASUREMENT1 table."
- next_action.discriminates (verbatim): "A proved bridge reinstates the uniform first-fall-2 statement for S_3 (scoped); a counterexample restricts it to the trace identity, removing the last uniform premise of the FFD route; the at-scale degree question itself lives in LEAD-ICE-descent-closure-degree-at-scale."
- blocked_by (verbatim): "problems/semaev-degree-two-fall-nonzero-bridge.md (crypto-autoresearcher)"
- forecloses: "Nagao coset-shift invariance of first fall degree"; "fake first fall degree bounds the true one"; "Semaev Assumption 1 d_F4 at most 4"; "trace morphism forces first fall at degree 2"; "polynomial-time ECDLP over F_2^n under FFD assumption"
- **AUD-1.** n/a (not a closed_* or exhausted_at_scale lead).
- **AUD-2.** n/a (no obstruction; forecloses checked, no scope note).
- **AUD-3.** n/a (open lead).
- **AUD-4.** The counterexample branch of this lead's own mapping has been realised on a finite model. problems/semaev-degree-two-fall-nonzero-bridge.md (updated 2026-10-24) records Lean certificates for the sample n = 4, n' = 4, s = 1, x_R = 1: "newFalls(1)=0, newFalls(2)=0, newFalls(3)=1" (BooleanParityFiniteCertificate.lean), and an explicit degree-3 witness outside V_2 (ConcreteFirstFallWitness.lean). The corrected replay gives 68/80 draws at degree two and 12 at degree three. The lead's discriminates line maps a counterexample to "restricts it to the trace identity, removing the last uniform premise of the FFD route". Caveats from the same record: the counterexample is degenerate ("the trace residual ... is already the fourth linear generator"). The record still lists "Generic correctness of rankOn, a generic descent from abstract S_3, and a general statement about first fall remain unproved" and requires independent semantic review. Proposed (conditional on that review completing): change the disposition to closed_obstructed (kind proof, scope: uniform first-fall-2 claim for descended S_3, toy Boolean model). Replace the blocked step with the scoped Lean target in lean_target. Until then, blocked_by should name the review item, not "discharge or refute". Lean target (scoped bridge): let F be the Weil-descended S_3 system over F_2 with nonzero target abscissa x_R, V_1 the span of its degree-1 generators, and r the linear trace residual whose quadratic coefficients DegreeTwoFall.lean proves cancel. Hypothesis r not in V_1. Conclusion newFalls(2) >= 1, i.e. some degree-2 combination of generators reduces to a linear polynomial outside V_1. Companion statement, already kernel-checked on one sample: r in V_1 is consistent with newFalls(2) = 0.
- **AUD-5.** n/a.
- **AUD-6.** n/a (no obstruction).

### LEAD-ICE-gpu-rootfind-oracle

- File: `knowledge/leads/ecdlp/ic-engine/LEAD-ICE-gpu-rootfind-oracle.yaml`; disposition `open_blocked`.
- next_action.step (verbatim): "Execute `./bench throughput` and the fail-closed validation harness of gpu/rootfind on a real sm_120 (or sm_89) device, then run one ecbench cold session with IC relation phase on GPU against same-GPU rho at matched targets."
- next_action.discriminates (verbatim): "Measured cells/s confirm or falsify the 300-1000x host-emulation estimate; the matched GPU-IC / GPU-rho S ratio says whether the constant gain survives once rho gets the same device."
- blocked_by (verbatim): "no NVIDIA device has executed the kernel (RESEARCH_GPU_ROOTFIND_DECOMPOSITION.md status line); cryptanalysis RunPod attempts failed at CUDA device init"
- forecloses: "GPU root finding for point decomposition"; "CUDA kernel for Semaev decomposition oracle"; "Blackwell sm_120 relation collection"; "GPU index calculus relation sieve"
- **AUD-1.** n/a (not a closed_* or exhausted_at_scale lead).
- **AUD-2.** n/a (no obstruction; forecloses checked, no scope note).
- **AUD-3.** n/a (open lead).
- **AUD-4.** An Amdahl bound decides most rows before any device runs. It is conditional on the lead's own scope ("It can only lower the relation-phase constant (68-95% of Table B S)"). Suppose only the relation phase moves to the device, and the other phases get no more device speedup than rho's own kernel. Then the matched ratio is at least ratio_CPU * (1 - relation share), whatever the cells/s. Computed from the LEADERBOARD Table B ratios and the Phases table (audit/calc_ice.out): floor >= 1, so sub-rho is impossible, at fp12 (1.745), fp16 (1.308), fp18 (1.548), fp20 (2.100), fp22 (2.594), fp24 (3.834), f2m15, f2m24 and f2m27. Elsewhere the relation kernel would need h_min = 10.6 (fp10), 42.2 (fp14), 35.4 (f2m18) or 65.9 (f2m21) times rho's device efficiency. Mapping: measured h below h_min on those four rows -> closed_obstructed (cost_model, Amdahl on the validated Table B shares), with the kernel kept as engineering. h above h_min -> run the matched ecbench session on those rows only. The bound fails if the factor-base phase is also offloaded. The remaining LA and verification shares are <= 1.7%, so the bound would then be weak. State that scope in the lead.
- **AUD-5.** n/a.
- **AUD-6.** n/a (no obstruction).

### LEAD-ICE-rootfind-pairtable-oracle

- File: `knowledge/leads/ecdlp/ic-engine/LEAD-ICE-rootfind-pairtable-oracle.yaml`; disposition `open_blocked`.
- next_action.step (verbatim): "Price every native primitive of the rootfind-negfold m = 2 arm and of matched strong rho (table canonicalisation, inversions) at 0, 0.1 and 1 GAE/op, replay on a second host (L2+), and re-run the 17-bit Koblitz and 20-bit prime cold sessions."
- next_action.discriminates (verbatim): "If the cold complete IC / strong-rho ratio stays above 1 across the band, the pair-table engine is exhausted at toy scale and only a degree-bounded algebraic oracle (LEAD-ICE-descent-closure- degree-at-scale) can change the slope; if it falls below 1 across the band at two sizes, it is the first validated sub-rho cold row and goes to the IC leaderboard gate."
- blocked_by (verbatim): "problems/rootfinding-complete-cost-calibration.md (crypto); native work unpriced, L0 only, same-host replay"
- forecloses: "replace Groebner with root finding in point decomposition"; "pair-sum table meet-in-the-middle decomposition oracle"; "x(R minus F_i) direct subtraction relation sweep"; "batched inversion root-finding oracle beats rho"; "all-roots univariate solver for Semaev S_3"
- **AUD-1.** n/a (not a closed_* or exhausted_at_scale lead).
- **AUD-2.** n/a (no obstruction; forecloses checked, no scope note).
- **AUD-3.** n/a (open lead).
- **AUD-4.** A theorem decides the exponent, and validated rows already decide the prime arm. (1) SO-TABLE covers this oracle class. LEAD-ICP-generic-table-decomposition: "Any decomposition oracle that enumerates or table-looks-up factor-base elements is a generic time/memory trade-off and obeys S*T^2 >~ N". LEAD-ICB-generic-table-oracle, scope "all binary and Koblitz curves, one target, setup charged": "no 4-, 5- or 6-sum table can beat sqrt(r/2n) in total work". Interpretation: the slope cannot move, as the lead's own discriminates line already says. Any sub-rho cold row would be constant-level at small r. (2) The prime 20-bit cold session in the blocked step is redundant for the sign question. Table B prices native counts at pinned ratios ("exact native operation counts converted to additions at the dimensionless ratios pinned per instance") and now marks all 13 rows "validated" (crypto docs/ic/LEADERBOARD.md; commit a8d8e3cd38, 2026-10-24, "Validate the 13 Table B rows through the gate"). fp20 is 8.3x. The ratio grows 0.113 bits per bit of log2 r from fp12 to fp24 (audit/calc_ice.out), the same sign as SO-TABLE's m = 2 prediction of 1/6. Proposed: drop the prime session from next_action, keep only the 17-bit Koblitz cold row, and state that a sub-rho Koblitz toy row would be a constant-level row whose ratio SO-TABLE says must grow with r. Update best_measured to say Table B is validated. Evidence hygiene: the evidence note attributes "the leaderboard's 96 replay mismatches are inherited-F4 ..." to D-known-issues/REPORT.md. That file discusses the 48 mismatches. The 96 split ("48 real mismatches plus 48 refusals") is in D-known-issues/item1_cross_isa_20261020/RESULT.md, line 36. The current LEADERBOARD audit row still says "96 mismatches across all four IC arms ... root-finder rows are not claimed to pass". Re-point the evidence to item1 RESULT.md and flag the stale LEADERBOARD wording to its owner.
- **AUD-5.** n/a.
- **AUD-6.** n/a (no obstruction).

### LEAD-ICE-chained-semaev-dreg-vs-semiregular

- File: `knowledge/leads/ecdlp/ic-engine/LEAD-ICE-chained-semaev-dreg-vs-semiregular.yaml`; disposition `open_next_step`.
- next_action.step (verbatim): "Re-run item C1 (n = 15, D = 6, seeds as frozen) with a streaming native Macaulay builder (IDEA-20260828-770aa4) under the lane's memory floor, with the block-matched / topology-matched null (IDEA-20260805-f49efb, IDEA-20260808-11b8c7) as a co-arm."
- next_action.discriminates (verbatim): "A deficit that survives the shape-matched null and grows with n is a real d_reg departure worth pricing; a deficit absorbed by the matched null reclassifies the n = 12 numbers as support artefacts and closes the departure question at toy scale."
- forecloses: "degree of regularity of chained Semaev system tracks semi-regular"; "Macaulay rank deficit of Boolean Semaev system"; "Hilbert series of chained summation ideal"; "block-matched null for Semaev Macaulay rank"
- **AUD-1.** n/a (not a closed_* or exhausted_at_scale lead).
- **AUD-2.** n/a (no obstruction; forecloses checked, no scope note).
- **AUD-3.** n/a (open lead).
- **AUD-4.** A known result decides one arm faster. KR-IC-fbdb61 (proven) says "Semi-regular (Bardet-Faugere-Salvy) predictions do not describe descended summation systems". The semi-regular arm therefore cannot carry a curve-specific conclusion, and only the block/topology-matched null is informative. That null can be run at n = 12, where the Semaev ranks already exist (EV-DREG-008), before any n = 15 attempt. Outcome mapping: if the matched null absorbs the n = 12 genuine deficit of 17,947, the lead closes as a support artefact at toy scale (closed_obstructed, measured) without n = 15. If the deficit survives the matched null at n = 12, the n = 15 rung becomes worth its memory. Scope note: KN-FIND-9cba50 says the DREG ladder "measures Frobenius-invariant subspaces of dimension ord_n(2)", not Semaev's Assumption-1 object, so either outcome is scoped to that subspace family. Recommendation, not a measurement: the queued n = 15 step depends on IDEA-20260828-770aa4 (a streaming builder that does not exist yet). problems/dreg-c1-memory-cap-exhausted.md is open with "0 of 6 runs completed_valid". Disposition open_blocked with that problem as blocked_by would describe the state more exactly than open_next_step.
- **AUD-5.** n/a.
- **AUD-6.** n/a (no obstruction).

### LEAD-ICE-curve-presentation-invariance

- File: `knowledge/leads/ecdlp/ic-engine/LEAD-ICE-curve-presentation-invariance.yaml`; disposition `open_next_step`.
- next_action.step (verbatim): "Execute EXP-DREG-dd668d (spec frozen, runs/ empty): last-fall and grevlex solving degree of the native, Velu-graph-eliminated and random-enrichment ideals on certified toy edges (H-DREG-c44a0d, H-DREG-1d0e5d), plus one special-model curve vs a generic classmate (IDEA-20260922-fac3e7)."
- next_action.discriminates (verbatim): "A drop beyond random enrichment and beyond a GL(N,F_2) coordinate change is a transport effect to price (including the transport cost); no drop closes isogeny/model transport of Groebner difficulty at toy scale, consistent with the mean-invariance identity."
- forecloses: "isogeny transport to an easier Semaev presentation"; "curve model invariance of solving degree"; "special j-invariant Semaev degeneration"; "within-isogeny-class variance of decomposition rate"; "Velu edge lowers Groebner degree"
- **AUD-1.** n/a (not a closed_* or exhausted_at_scale lead).
- **AUD-2.** n/a (no obstruction; forecloses checked, no scope note).
- **AUD-3.** n/a (open lead).
- **AUD-4.** A short identity decides the native arm of the queued experiment. It does not cover the Velu-eliminated arm. Observed: EXP-DREG-dd668d is binary. Its specification gives fields "F_2[z]/(z^2 + z + 1)" and "F_2[w]/(w^4 + w + 1)", "at most 12 candidate models (4 values of a2, 3 of a6)", and factor base "V = {0, 1} inside the rung field". The binary S_3 used in crypto is "S3 = (X1+X2)^2 x3^2 + X1 X2 x3 + (X1 X2)^2 + b" (crypto src/cryptanalysis/ffd_harness.rs line 373; isogeny_class_search.rs line 561 maps a6 into weil_descend_s3_subspace). The curve therefore enters the native chained system only through the additive constant b = a6, and a2 does not appear. IDEA-20261018-c49f37 T1 (hand-derived, proposed) states the m = 2 form: "the curve enters only as additive constants". Derivation: the 12 native ideals of the experiment collapse to at most 3 distinct systems, one per a6. Native r(d), first_fall and last_fall must be identical across a2 at fixed a6. That gives a free positive control, and the native-arm comparison is a right-hand-side-constant (pencil) comparison, as posed by IDEA-20261018-70caad. Not covered: the "Velu-graph-eliminated" ideal adds cleared isogeny coordinate maps (spec, field delta), i.e. it pulls the base back through a degree-2 map, so the additive-constant argument says nothing about it. Mapping: native profiles identical across a2 -> instrument check passes, and only the Velu and random-enrichment arms carry information. Native profiles differ across a2 at equal a6 -> instrument or S_3-certificate defect, so stop before reading ranks. The prime-field arm (EV-ICINV-6b6264: support 13 generic, 9 at a = 0, 10 at b = 0) is not touched by this identity. Related lead to add: LEAD-ICP-xline-symmetry-special-j (open_unexamined), whose special-j Macaulay-rank step overlaps IDEA-20260922-fac3e7. Exposure check: KN-OPEN-5b3a08 (audit update 2026-10-18) names RUN-ICINV-e0cd8f-m3class as affected by the s4_expr bug in its m4 columns ("s4_support 227/225 archived against 439 recomputed"). This lead's S_3 claims (KN-FIND-ddd982) do not use s4_expr. EV-ICINV-6b6264 reports S_4 support 439, matching the recomputed value. Note the exposure in the evidence list.
- **AUD-5.** n/a.
- **AUD-6.** n/a (no obstruction).

### LEAD-ICE-decomposition-probability-audit

- File: `knowledge/leads/ecdlp/ic-engine/LEAD-ICE-decomposition-probability-audit.yaml`; disposition `open_next_step`.
- next_action.step (verbatim): "Run BATCH-79a580 (three F-2 28-bit fixtures with P-5 yields, nine F-1 fixtures as control) for EXP-RELN-dc761f, reporting the exact count vector c_D and its variance against a size-matched random base."
- next_action.discriminates (verbatim): "A target-conditional variance beyond the random-base null names a clustering effect worth a targeted collector; no excess confirms KN-FIND-007 to second order and retires the P(decomp) lane. Learned predictors are exhausted at N <= 2^20 (inconclusive x3) and reopen only with held-out bases beating a size-matched null at N >= 2^24."
- forecloses: "decomposition probability conditioned on the target"; "P(decomp) versus factor base size curve"; "charge the failed decomposition attempts"; "graph neural decomposability predictor"; "symbolic regression of relation yield"
- **AUD-1.** n/a (not a closed_* or exhausted_at_scale lead).
- **AUD-2.** n/a (no obstruction; forecloses checked, no scope note).
- **AUD-3.** n/a (open lead).
- **AUD-4.** No theorem decides the variance question faster. Weil/Lang-Weil error terms for points on the Semaev variety are far above the mean yield C(B+m-1,m)/N = O(1) in the IC regime (interpretation). But KN-FIND-007 consequence 3 changes what the positive branch can buy: "coverage <= min(1, mean)", and repeated sums lower coverage at matched size. So a target-conditional variance excess lowers coverage. It helps only if a cheap recogniser selects high-c_D targets before the oracle runs. The lead records the learned predictors as "exhausted at N <= 2^20 (inconclusive x3)". Proposed rewrite of the discriminates line: "variance beyond the random-base null AND a recogniser that predicts c_D(R) > mean at cost below one oracle call -> targeted collector; variance without a recogniser -> no cost effect (KN-FIND-007 consequence 3) and retire the P(decomp) lane". IDEA-20261018-5fa71b (one count vector, three moments) and IDEA-20261018-71a901 (periodogram of c_D) are new and fit this step.
- **AUD-5.** n/a.
- **AUD-6.** n/a (no obstruction).

### LEAD-ICE-hybrid-guess-determine-l7

- File: `knowledge/leads/ecdlp/ic-engine/LEAD-ICE-hybrid-guess-determine-l7.yaml`; disposition `open_next_step`.
- next_action.step (verbatim): "Run the registered stretch cell E8, (m, n, l) = (3, 22, 8): find k* (fixed variables under rule R1 until every branch refutes at degree 4), about 10-12 GB and 25 locked minutes per branch."
- next_action.discriminates (verbatim): "k* equal to its l = 7 value (<= 2) keeps the constant-k reading alive (ECC2K-130 m = 4 row +8.43 bits over rho against +10.32 at degree 5); one more guess per l moves it to S_lin (+30.7 to +58.3 bits) and closes this lead."
- forecloses: "hybrid guess and determine descent"; "fix one variable then Groebner"; "crossbred on descent cells"; "specialisation lowers closure degree"
- **AUD-1.** n/a (not a closed_* or exhausted_at_scale lead).
- **AUD-2.** n/a (no obstruction; forecloses checked, no scope note).
- **AUD-3.** n/a (open lead).
- **AUD-4.** The queued E8 cell does not discriminate the cost-versus-rho question unless K is known. Observed in research/dreg_hybrid_guess_20261024/RESULTS.md: "The lead does not close below rho by this route in any scenario". Both E8 outcomes are above rho in touch units: k* constant gives +8.43 bits, k* growing gives +30.7 to +58.3. Those rows are unconverted touches at w = 1 (RESEARCH_ECC2K130_DESCENT_DEGREE.md section 2: "subtract log2 K"). Mapping: if measured log2 K < 8.43 (IDEA-20261018-e7a860), both E8 outcomes map to above-rho and the lead goes to closed_obstructed (cost_model: priced hybrid m = 4 row above rho in every scenario). E8 then has degree-science value only. If log2 K >= 8.43, E8 decides between a possibly sub-rho lower bracket (constant k) and closure (k growing with l). Caveat: the degree-4 floor of +7.62 bounds only the R1 rule (guess until degree 4 refutes). A degree-3 hybrid (more guesses) is not costed in RESULTS.md. Add it to the scenario list or to revisit_when.
- **AUD-5.** n/a.
- **AUD-6.** n/a (no obstruction).

### LEAD-ICE-relation-graph-rank-large-prime

- File: `knowledge/leads/ecdlp/ic-engine/LEAD-ICE-relation-graph-rank-large-prime.yaml`; disposition `open_next_step`.
- next_action.step (verbatim): "Extend the honest 2LP summation-multigraph run (EXP-RELN-c5a377 v4 generator, L = q^(1/5)) to larger q with rank-qualified rows and a rewire / Erdos-Renyi null, reporting edge density delta against the 1/4 supercritical threshold and whole-solve S against matched rho."
- next_action.discriminates (verbatim): "delta > 1/4 with a whole-solve S drop beyond the null is a priced relation-phase gain (as in the genus-3 2LP study); delta stuck below 1/4 closes 2LP for point-decomposition IC at L = q^(1/5)."
- forecloses: "two large prime cycle basis enrichment for point decomposition"; "rank-feedback relation generator selection"; "relations needed fixed point of left kernel"; "adaptive stopping on the relation 2-core"
- **AUD-1.** n/a (not a closed_* or exhausted_at_scale lead).
- **AUD-2.** n/a (no obstruction; forecloses checked, no scope note).
- **AUD-3.** n/a (open lead).
- **AUD-4.** Partly decidable by counting before the run. By KN-FIND-007, a single/double-large-prime scheme is a base D union L with a different linear algebra. Its mean yield is C(|D|+|L|+m-1,m)/N, so any gain must come from (i) the oracle being cheaper with L on one side than with D union L, or (ii) cycle elimination being cheaper than carrying L as columns. The leaderboard records linear algebra as "< 0.5% of Table B S" (LEADERBOARD Phases table: LA 0.0-0.4% on the B rows). Interpretation: branch (ii) can save at most about 0.5% of S at these sizes. Proposed: state in discriminates that a whole-solve S drop must come from oracle-side asymmetry (i), and measure that per-target oracle cost ratio directly (one table probe into L against |D union L| probes) as the first step. The edge-density run is needed only if (i) exceeds 1.
- **AUD-5.** n/a.
- **AUD-6.** n/a (no obstruction).

### LEAD-ICE-sat-xor-pdp-oracle

- File: `knowledge/leads/ecdlp/ic-engine/LEAD-ICE-sat-xor-pdp-oracle.yaml`; disposition `open_next_step`.
- next_action.step (verbatim): "Calibrate ns per conflict and per propagation against ns per group addition on the count-qualified-main hardware, reprice the native-XOR SAT arm of ecbench_sat_pdp at 0, 0.1 and 1 GAE per solver op, and fit alpha(m) of the conflict count at m in {3,4,5} (H-SATIC-5c526c)."
- next_action.discriminates (verbatim): "Priced S/rho below 1 across the band would be a sub-rho toy row to send through the validation gate; above 1 with conflicts tracking 2^(ml)/m! confirms SAT is enumeration at a constant and closes the lead as dominated by the pair table."
- forecloses: "SAT solver for point decomposition"; "CryptoMiniSat Gaussian elimination on Weil descent"; "WDSat XOR reasoning for summation polynomials"; "CNF-XOR encoding of the PDP"; "DPLL conflict law 2^(ml)/m!"
- **AUD-1.** n/a (not a closed_* or exhausted_at_scale lead).
- **AUD-2.** n/a (no obstruction; forecloses checked, no scope note).
- **AUD-3.** n/a (open lead).
- **AUD-4.** Already decided by recorded counts and by a closed lead. The calibration step is not needed for the across-band verdict. (1) Band arithmetic on the frozen count-qualified-main resource vector (crypto research/ecbench_sat_pdp_20261009/count-qualified-main.resources.json; script audit/calc_ice.py). Over the same 40 measured runs: rho-strong total 40,950.357 GAE with 13,788 uncharged native ops; ic-sat-xor 34,963.343 GAE with relations.solver_ops = 2,755,966 unpriced conflicts. Pricing both arms' unpriced units at w gives S/rho = 0.854 (w = 0), 7.337 (w = 0.1) and 50.987 (w = 1). Break-even is w < 0.00218 GAE per conflict, i.e. one conflict must cost less than about 1/458 of a group addition. The branch "Priced S/rho below 1 across the band" is therefore excluded by the recorded counts at w = 0.1 and w = 1. (2) The other half of the closing branch ("conflicts tracking 2^(ml)/m!") is the obstruction of the closed lead LEAD-ICB-decomposition-encoding-and-sat: "WDSat 2.9985 bits per unit l at m = 3, reproducing 2^{3l}/3!; alpha 4.09-4.33 at m = 4, l = 3..5, while beating rho needs alpha < m/2 - 1". Proposed: change the disposition to closed_obstructed (measured; scope m in {3,4}, n = 17 Koblitz band arithmetic plus the ICB alpha ladders), with revisit_when "alpha(5) < 1.5 on a complete pruned configuration (H-SATIC-5c526c), or a solver whose per-conflict cost is < 0.0022 GAE". Add LEAD-ICB-decomposition-encoding-and-sat as related, because the two leads currently duplicate each other. Why closed_obstructed and not closed_dominated, as the lead's own mapping suggests: at w = 0 SAT (0.854) is below Frobenius MITM (4.271, same README table), so dominance by the table oracle fails across the band. The obstruction is the alpha ~ m law plus the band arithmetic.
- **AUD-5.** n/a.
- **AUD-6.** n/a (no obstruction).

### LEAD-ICE-semaev-yield-model-coset-typing

- File: `knowledge/leads/ecdlp/ic-engine/LEAD-ICE-semaev-yield-model-coset-typing.yaml`; disposition `open_next_step`.
- next_action.step (verbatim): "Run the in-regime coset-typed solver-degree conservation test (IDEA-20260918-c05e71): matched (n, m, k) typed and untyped chains, exact yield plus degree-4 closure refutation rate, against random affine-shift nulls (IDEA-20261006-839ced)."
- next_action.discriminates (verbatim): "Typed yield near the finite-k cap at unchanged closure degree is a constant-factor (m!) gain to price; a degree rise that cancels the yield gain conserves cost and closes the coset-typing route."
- forecloses: "coset-typed factor base erases m factorial"; "Semaev eq. 11 decomposition probability"; "trace-parity confinement of binary factor base"; "disjoint coset shifts raise relation yield"
- **AUD-1.** n/a (not a closed_* or exhausted_at_scale lead).
- **AUD-2.** n/a (no obstruction; forecloses checked, no scope note).
- **AUD-3.** n/a (open lead).
- **AUD-4.** The two sources compare at different matchings, so this is a matching mismatch, not a contradiction. It still corrects the size of the gain and gives a cheaper decision inequality. KN-FIND-007 consequence 4: "For typed decompositions with sub-base sizes B1 + B2 + B3 = B, the total is B1*B2*B3 <= (B/3)^3 = B^3/27, strictly below the untyped binomial(B+2,3) ~ B^3/6. Measured penalty at a balanced split: 4.817x." Interpretation, two matchings. (i) Matched per-variable dimension (the lead's comparison): typed yield per query is m! higher, but the typed base is m times larger, so m times more relations are needed. The net gain is (m-1)! before any change in query cost, so "m!" overstates the gain by a factor m. (ii) Matched total base size (KN-FIND-007's comparison): typing loses a factor m^m/m! in yield (4.5 at m = 3, 10.67 at m = 4). It gains only through a cheaper query, because each unknown ranges over |V| instead of m|V|, about log2 m fewer bits per summand. Mapping under (ii): the typed route wins iff C_query(l + log2 m)/C_query(l) > m^m/m!. That ratio can be read from existing degree-4 closure costs at adjacent l (research/dreg_hybrid_guess_20261024 summary.json, dreg_closure cells) before running the conservation test. Ratio below m^m/m! -> closed_obstructed (conservation, KN-FIND-007 consequence 4). Ratio above -> run IDEA-20260918-c05e71 as queued. IDEA-20261018-9fc21f ("trace-parity confinement is kappa = d(V) at most the cofactor ... and is empty on prime order") bounds the trace-parity half to the cofactor. Add it to ledger_refs.
- **AUD-5.** n/a.
- **AUD-6.** n/a (no obstruction).

### LEAD-ICE-syzygy-cascade-signatures

- File: `knowledge/leads/ecdlp/ic-engine/LEAD-ICE-syzygy-cascade-signatures.yaml`; disposition `open_next_step`.
- next_action.step (verbatim): "Run the repaired SIG-D6-NULL-RECAL-v2 calibration, adding the planted-syzygy unit-slope control (H-SIG-22ec42) and the Boolean-ring trivial-syzygy repair (IDEA-20260805-bbfca9)."
- next_action.discriminates (verbatim): "Unit slope on the planted family plus an extra_D excess over the matched D >= 6 null means the cascade is a curve fact to price as a degree drop; no excess (or a failed planted control) closes exploitability at toy scale or retires the instrument."
- forecloses: "non-rewritable syzygy cascade in Semaev systems"; "F5 signature criterion on summation polynomials"; "syzygy fall image of decomposition ideal"; "relative syzygy gluing across Semaev chain"
- **AUD-1.** n/a (not a closed_* or exhausted_at_scale lead).
- **AUD-2.** n/a (no obstruction; forecloses checked, no scope note).
- **AUD-3.** n/a (open lead).
- **AUD-4.** No theorem found that decides the cascade question faster. The Boolean semi-regular Hilbert series (Bardet-Faugere-Salvy over F_2, the semi-regular reference named in KR-IC-fbdb61) gives a closed-form trivial-syzygy count. That can serve as an analytic co-null for the D >= 6 recalibration, but KR-IC-fbdb61 says semi-regular predictions do not describe descended systems. The planted-syzygy control stays necessary. No change proposed.
- **AUD-5.** n/a.
- **AUD-6.** n/a (no obstruction).

### LEAD-ICE-linearization-excess-fb-prior

- File: `knowledge/leads/ecdlp/ic-engine/LEAD-ICE-linearization-excess-fb-prior.yaml`; disposition `open_unexamined`.
- next_action.step (verbatim): "On the m = 3 and m = 4 descent cells, rank candidate factor-base subspaces of equal size by e. Measure the closure degree and charged cost per query for the top-e and the median-e bases, with a random-subspace control."
- next_action.discriminates (verbatim): "If the degree is lower at the same yield, a constant- or exponent-level improvement in the IC baseline is possible and the fitted rule transfers. If the degree is unchanged, the rule is specific to PDP systems and the lead closes as exhausted at that scale."
- forecloses: "linearization excess factor base"; "choose factor base to lower solving degree"; "degree-aware factor base selection"; "excess-maximising subspace"
- **AUD-1.** n/a (not a closed_* or exhausted_at_scale lead).
- **AUD-2.** n/a (no obstruction; forecloses checked, no scope note).
- **AUD-3.** n/a (open lead).
- **AUD-4.** n/a.
- **AUD-5.** First discriminating step, cheaper than the stated step: draw fresh enumeration-certified UNSAT instances at (m, n, l) = (3,19,7) and (3,21,7) on V = c*span{1,g,...,g^6}, using the research/dreg_hybrid_guess_20261024 instrument (dreg_hybrid, degree-4 closure, unspecialised k = 0). The null is random-V draws at the same (n, l), and the planted satisfiable controls are kept. The frozen draws cannot be reused with V swapped, because an UNSAT label belongs to a (V, target) pair. Why it is discriminating: every closure cell so far used random subspaces (PREREGISTRATION line 225). cryptanalysis experiments/pdp-degree-heuristics/README.md, finding 5: "the family moves it by at most one degree" for three summands in the direct formulation. That one degree is exactly the 4-versus-5 gap that sets the ECC2K-130 m = 4 row. For prime n the excess e = n - dim V - dim V^(2) is maximised only by geometric progressions (finding 2: "below n - 1 only the progressions ... attain it"), so the top-e base needs no search. Mapping: geometric-progression V refutes at degree 4 where random V needs 5 -> the "degree rises at l = 7" rule is a random-base effect; reprice the m = 4 row with that base and promote the lead to open_next_step at m = 4. No change at l = 7 -> exhausted_at_scale (scope: chained m = 3, l = 7, n <= 21), consistent with finding 5. Do not close it through LEAD-ICB-factor-base-subspace-choice: that lead measured yield and N_var, not closure degree. IDEA-20261018-c4adb6 (adaptation, proposed) is the matching ledger idea. Cite it in ledger_refs.
- **AUD-6.** n/a (no obstruction).

## AUD-6, family level

- **SO-MONO** (LEAD-ICE-semaev-cover-monodromy) is the only standing obstruction owned by this family; see that subsection: Chebotarev-in-families equidistribution takes the uniform monodromy as hypothesis and returns exact nulls, not a rate gain.
- The family *uses* SO-TABLE (LEAD-ICP-generic-table-decomposition, LEAD-ICB-generic-table-oracle) and SO-GEN implicitly through LEAD-ICE-generic-oracle-arity-cost-floor and LEAD-ICE-rootfind-pairtable-oracle; the theory that takes S*T^2 >~ N as a hypothesis is the oracle-budget calculus of KN-FIND-aa2efc (m >= 4 per-query budget), which is already in use.

## Cross-lead observations (interpretation)

1. The single unmeasured quantity that gates three open leads (descent-closure, hybrid-guess, and the m = 4 rows of LEAD-ICB-prime-degree-algebraic-decomposition) is K, column touches per group operation, together with the measured touches-per-column factor (about 2^21.5 word ops per column at N = 40, audit/calc_ice.out). Measuring both (IDEA-20261018-e7a860) is cheaper than the 250 GB C1 run and decides whether that run can change the ECC2K-130 verdict.
2. Every Weil-descent closure cell was run on random subspaces. Fresh enumeration-certified UNSAT draws at l = 7 on a geometric-progression V, with a random-V null (LEAD-ICE-linearization-excess-fb-prior AUD-5), are the cheapest experiment in the family that could move the m = 4 row by a full degree. The family-wide K threshold is log2 K = 2.07: below it, no Macaulay-based m = 4 oracle beats rho at any degree (RESEARCH_ECC2K130_DESCENT_DEGREE.md section 2, D = 2 row).
3. Prime field: within ic-engine every prime-field arm is either decided (SO-TABLE; Table B validated 5.47x-13.5x, ratio growing 0.113 bit per bit) or awaits a non-enumerative oracle at m >= 4 (LEAD-ICE-charged-toy-ic-exponent-vs-rho, T << N^{1/4} requirement). The prime-field trigger of LEAD-ICE-prime-field-semaev-solving-degree must be stated on the s axis, not the p axis, to mean anything.

---

## Family: ic-prime


# Audit of the ic-prime lead family (AUD-1 .. AUD-6)

Reviewer audit, 2026-10-24. Read-only over the repositories. Every lead YAML in
`/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/ic-prime/` (24 rows) was read in full.
The quotes of `obstruction.statement`, `revisit_when` and `next_action` below are inserted
verbatim from those YAML files by `render_ic_prime.py` (same directory).

Path prefixes used below:

- `car:` = `/Volumes/SSD990-2/crypto-autoresearcher/`
- `crypto:` = `/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/crypto-main/` (origin/main checkout)
- `cax:` = `/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/cryptanalysis-main/`

Labels: **observed** = read from a record or file; **derived (reviewer)** = computed or argued by this
reviewer from observed values, not checked by an independent party; **model** = a cost model or
extrapolation. A timeout or censored call is never read as a negative here.

State used for AUD-1: `scratchpad/atlas/KRMAP.md` (51 KR rows), `crypto:docs/ic/LEADERBOARD.md`
(note commit `a8d8e3cd38` "Validate the 13 Table B rows through the gate; Table C fails"),
`crypto:docs/bounds/FRONTIER.md` (fit v2), the 201 paths of `scratchpad/atlas/delta.txt`
(decisions DEC-20261018..24, ideas IDEA-20261018..24, KN-FIND-3c7e19/7e2b94/c71e5d, problems),
and the dispositions of all other families in `scratchpad/atlas/ATLAS.md`.


## Summary of proposed changes (details in each lead's subsection)

**AUD-1 result.** None of the ten closed leads' `revisit_when` conditions has fired against the
current state. Each condition is checked in its lead's subsection, with paths. One closed lead
carries stale evidence text: generic-table-decomposition still says Table B is "unvalidated
(pre-gate)", and the LEADERBOARD now marks those rows `validated`. The open lead
prime-ic-constant-engineering carries the same stale text.

Changes that alter a disposition:

1. **LEAD-ICP-gfp5-odd-char-cover**: `open_blocked` -> `closed_obstructed`, scoped to x-line
   GHS covers. The blocker (a source freeze) is bypassed by paper theorems already in
   `crypto:research/ghs_cover_census_n5_20261013/README.md`: Cor. T5 and Prop. O5 give genus >= 33
   for #E(K) = 2 mod 4 and for odd order, for every odd q. EcGFp5 has #E = 2n and EcMasFp5 has
   prime order, and the floor holds across each isogeny class. Priced with the 1/g! relation
   probability, genus 33 over F_p with p ~ 2^64 costs >= 2^184.8 (model), against rho at 2^159.3.
2. **LEAD-ICP-lattice-ic-relation-construction**: `open_blocked` -> `closed_obstructed` for the
   pairing route (SO-PAIR) and the endomorphism-chain route (SO-ENDO). The lead's own report
   derives both reductions. The small-roots route moves into LEAD-ICP-coppersmith-smallroot-semaev.
3. **LEAD-ICP-xline-symmetry-special-j**: `open_unexamined` -> `closed_dominated`, absorbed into
   LEAD-STR-special-j-ic-semaev. The folding sub-claim is closed_known (KR-RHO-0528e7, KR-IC-955fd6).
4. **LEAD-ICP-construction-normal-form**: `open_unexamined` -> `closed_dominated` by
   LEAD-EXO-methodology-instruments. It is methodology, not a cost mechanism.

Changes that keep the disposition but change the content:

5. **LEAD-ICP-gfp5-oa-sdhp-jv**: the lead expects closure arithmetic for JV (n-1) on full ECDLP
   "unless it unexpectedly falls below 2^160". The program's own model points the other way.
   It puts the crossover at q* ~ 2^55.3 (`crypto:research/joux_vitse_n1_20261015/MODEL.md`), and
   Vitse's published crossover is 2^60. With the measured trial constant (5-9e9, up to
   1.104e10 F_p mults), the model at p = 2^64 gives JV (n-1) / rho ~ 2^-3.9 .. 2^-2.0. That is
   heuristic, about 2^63 relations of memory, and the sign flips with a ~2^4 change in the
   constant. The decisive measurement is C_pdp4 on the real descended system.
6. **LEAD-ICP-full-width-arity-grid**: a counting lemma fixes part of the panel before it runs.
   It uses conservation and the support bound in `crypto:problems/eccp131-full-parameter-index-calculus.md`.
   At B = 475 and r ~ 2^63, every m <= 4 cell (any oracle, uniform targets, >= 1 GAE per attempt)
   is above matched rho, and m = 5 needs T_dec <= 4 GAE. The panel therefore measures T_dec(m)
   against a break-even column, not "distance to rho". The m = 2 600 s censors of RUN-ICPERF-eb0d88
   are a formulation fact: a subtraction oracle decides m = 2 in 2B point subtractions.
7. **LEAD-ICP-isogeny-transported-relation-yield**: a group-isomorphism bijection lemma makes the
   transported arms exact replicates of the source-curve native arms, in mean, variance and
   coverage. Only the native crater/floor arms carry information.
8. **LEAD-ICP-extension-field-embedding**: the cost-model closure upgrades to a proof. For odd n,
   {P in E(F_{p^n}) : x(P) in F_p} = E(F_p), so the "subfield base" is the prime-field instance
   itself. For even n it adds only twist points (Lean target).
9. **LEAD-ICP-generic-table-decomposition**: Lean target for the m = 2/3 part, using conservation.
   It gives m = 3 IC >= sqrt(3 c T) sqrt(N), a tie in exponent with an explicit constant condition.
   AUD-2 flags `free decomposition oracle at m = 2 or m = 3` and the B-optimisation phrase as
   wider than what was proved.
10. **LEAD-ICP-coincidence-harvest-structured-base**: the scheduled log-GAP validation EXP-PFDR-bb0d26
    ran with O-NULL on 44 powered cells (DEC-20261022-9aec2b, review pending). Update next_action.
    Lean target: the coincidence relations of a rank-r GAP base have rank <= r + 1.
11. **LEAD-ICP-prime-ic-constant-engineering**: the gate half of next_action is done
    (LEADERBOARD rows validated). The fixed-window gain was confirmed on held-out curves
    (DEC-20261023-122e32). The batching gain in the counted unit is an operation-count identity,
    and the rho reference must be batched too.
12. AUD-2 scope fixes:
    - algebraic-membership: `x^B = 1` blocks the binary IDEA-20261018-329d0a.
    - representation-subset-sum: the generic bound is applied to coordinate-reading filters.
    - xedni-function-field: "an elliptic surface" blocks the K3 case its own revisit names.
    - self-pairing: arbitrary bilinear maps versus Tate/Weil pairings.
    - gfp5-rho-reference-audit: "SafeCurves audit" versus six criteria not examined (EV-GFPN-ba8e4d).
    - icperf-writability: forecloses the chained representation its revisit names.
    - retained-setup-online: a binary duplicate of LEAD-ICB-retained-setup-online.
    - Family misfiling: icperf-binary-pdp-solver and icperf-writability-boundary are binary leads
      filed under ic-prime.


## LEAD-ICP-algebraic-membership-factor-base

- file: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/ic-prime/LEAD-ICP-algebraic-membership-factor-base.yaml`
- disposition (as filed): `closed_obstructed`; last_reviewed 2026-10-24
- obstruction.kind: `theorem`

obstruction.statement (verbatim):

> A target-independent algebraic locus of degree d yields O(d) usable points, so a size-B algebraic base has description degree >= B/3 and membership polynomial prod(x - v) of degree B (bounded-degree factor-base theorem, IDEA-20260801-021); mean per-target yield is binomial(B+m-1, m)/N for every base of size B (KN-FIND-007 conservation; coverage gain <= 1.582, constant in N). Measured: subgroup, small_x and random bases within 7 % at 32 bits; exact mean-yield ratio 1.000000 for six geometries at N ~ 2^14..2^18 (EV-FBG-001); msolve on subgroup bases grows deg^{4.4} at m = 3. Scope: prime-order E/F_p, any base of size B.

obstruction.revisit_when (verbatim):

> KN-OPEN-020 is answered positively (a size-B set with sub-B-degree membership surviving substitution), or a base raises coverage or variance with an excess that grows with N.

best_measured (verbatim):

> mean-yield ratio vs matched random 1.000000 at N ~ 2^14..2^18 (EV-FBG-001); subgroup vs random within 7 % at 32 bits

forecloses (verbatim): `multiplicative subgroup factor base x^B = 1`; `Dickson or coset factor base for prime-field index calculus`; `algebraic factor base with low-degree membership polynomial`; `character sums bias decompositions over a coset base`; `image of a low-degree map as factor base`

**AUD-1.** Trigger (a), KN-OPEN-020 answered positively: **not fired**. `car:knowledge/open-problems/KN-OPEN-020.md`
is `status: open` (file dated 2026-10-09), and it is not in the delta.
Trigger (b), "a base raises coverage or variance with an excess that grows with N": **not fired**.
- The nearest new data is EXP-PFDR-bb0d26 (log-GAP coincidence census; `car:ledger/decisions/DEC-20261022-9aec2b.yaml`):
  O-NULL, with slopes of log kappa per log2 n in [-0.0088, +0.0042]. It measures pair-sum
  coincidence excess, not coverage, and nothing grows with N.
- IDEA-20261018-5f37a1 (log-blind golden bases) is `proposed`, with no result.

**AUD-2.** Proved scope: "prime-order E/F_p, any base of size B" (statement). Over-foreclosure:
- `multiplicative subgroup factor base x^B = 1` has no field qualifier. It collides with
  IDEA-20261018-329d0a (`car:ledger/proposals/IDEA-20261018-329d0a.yaml`). That idea uses
  Frobenius-stable mu_d bases over F_{2^n}, where membership is measured after Weil descent
  ("Boolean degree = binary weight of d"). Neither the prime-field Bezout bound nor the F_p
  measurement covers that setting.
- The same holds for `Dickson or coset factor base ...` (already qualified), `algebraic factor
  base with low-degree membership polynomial` and `image of a low-degree map as factor base`.
- `character sums bias decompositions over a coset base`: conservation (KN-FIND-007) fixes the
  mean yield over all targets. It does not bound a target-preselection rule that attempts only
  targets whose character value predicts decomposability. That rule is explicitly open in
  LEAD-ICP-coincidence-harvest-structured-base ("conservation binds only over the whole group").

Proposed change: qualify phrases 1, 3 and 5 with "over a prime field F_p". Rewrite phrase 4 as
"character sums bias the mean per-target yield over a coset base".

**AUD-3.** Closure kind is `theorem`; not applicable.

**AUD-4.** Not applicable to this disposition.

**AUD-5.** Not applicable to this disposition.

**AUD-6.** SO-ALGFB (membership degree >= B/3 for a size-B base). Theories that take this quantity as a
hypothesis rather than a refutation:
- (i) Coppersmith / Howgrave-Graham small roots. Membership is a norm bound |x| < X, not an
  equation, so the degree of membership never enters. See LEAD-ICP-coppersmith-smallroot-semaev.
- (ii) Weil descent, where degree is measured after restriction of scalars, so x^q = x is linear.
  Over F_p there is no subfield; LEAD-ICP-extension-field-embedding, AUD-3 here, shows the embedded
  subfield base is the prime-field problem itself.
- (iii) The base-B digit presentation (LEAD-ICP-digit-presentation-solving-degree). It is the F_p
  attempt at "degree after a change of coordinates".

## LEAD-ICP-char0-lifting-xedni-smoothness

- file: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/ic-prime/LEAD-ICP-char0-lifting-xedni-smoothness.yaml`
- disposition (as filed): `closed_known`; last_reviewed 2026-10-24
- obstruction.kind: `literature`

obstruction.statement (verbatim):

> Jacobson-Koblitz-Silverman-Stein-Teske (2000) show xedni does not beat rho: the logs span rank(E(Q)) unknowns and the target must still be a bounded combination of generators. The program reproduced the published p = 353 Cheon example and certified both historical prescribed pairs independent modulo torsion (rank exactly two), with a derived signed-square independence lemma; the integer-lift route has no compositional identity because the x-line addition law is 2-valued (H-PFDR-e0988d).

obstruction.revisit_when (verbatim):

> A certified exact dependent lift found by the frozen bounded search (H-XEDN-4a5b50) with lift and certificate costs charged, or a lifting family whose relation coefficients stay bounded at crypto-relevant rank.

best_measured (verbatim):

> p = 353 example reproduced; 2/2 historical pairs certified independent; Xedni V2 curve-fitting 0 certified dependencies among 20 bounded pairs

forecloses (verbatim): `xedni calculus`; `lift points to a rational elliptic curve and reduce relations`; `prescribed rational lifts with a dependency`; `smoothness of integer lifts of x-coordinates`; `Cheon two-isogeny lift`

**AUD-1.** Trigger (a), "a certified exact dependent lift found by the frozen bounded search (H-XEDN-4a5b50)":
**not fired**. H-XEDN-4a5b50 is `proposed` in `car:ledger/.index/hypotheses.jsonl`.
- New and adjacent: H-CZLIFT-cb95b8 was moved to `weakened` (`car:ledger/decisions/DEC-20261023-488023.yaml`).
  Its statement reads "Xedni lifts of two or three random points are never dependent within a
  relation bound of 6, while a planted dependence is always detected". The supported residue is
  EV-CZLIFT-ee9b23 (eight primes, r in {2, 3}). No dependent lift was found.

Trigger (b), "a lifting family whose relation coefficients stay bounded at crypto-relevant rank":
**not fired**.
- H-CZLIFT-9a32e9 is `weakened` (DEC-20261023-26a6de: "C1 growth law supported", the
  (log H)^{r/2} small-point growth).
- H-CZLIFT-27a184 is `weakened` (DEC-20261023-6931ab).
- KN-FIND-7e2b94 and KN-FIND-3c7e19 concern p-adic sections (the TRF padic family), not rational
  lifts.

Proposed change (no disposition change): add `related: [LEAD-TRF-global-lift-small-height]`.
That row already carries H-CZLIFT-9a32e9/27a184/89e169/cb95b8. Also add EV-CZLIFT-ee9b23 as
evidence for the "prescribed rational lifts" phrase.

**AUD-2.** The statement leans on a Cheon certificate whose evidence note reads "lemma pending independent
review" (`car:analysis/xedni-cheon/20261007-certificates/REPORT.md`, per the lead's evidence entry).
- The phrase `Cheon two-isogeny lift` is therefore closed on 2/2 certified toy pairs plus an
  unreviewed lemma. That is a toy-scale measurement used as closure.
- The JKSST literature (KR-IC-cd159a) covers the general phrase `prescribed rational lifts with a
  dependency`, but not the Cheon 2-isogeny construction specifically.

Proposed change: add to revisit_when "the signed-square independence lemma fails independent review".

**AUD-3.** Closure kind is `literature`; not applicable.

**AUD-4.** Not applicable to this disposition.

**AUD-5.** Not applicable to this disposition.

**AUD-6.** Obstruction: JKSST height growth (points of height <= B number about (log B)^{r/2}). Theories that
take bounded height as a hypothesis:
- Function-field analogues, where height is bounded by degree. Shioda-Tate Mordell-Weil lattices,
  and Ulmer's unbounded-rank curves over F_p(t), lead to LEAD-ICP-xedni-function-field-sections
  (alpha = 3, SO-XEDNI).
- Small-regulator high-rank constructions. These are revisit (b), and remain unrealized.

## LEAD-ICP-coincidence-harvest-structured-base

- file: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/ic-prime/LEAD-ICP-coincidence-harvest-structured-base.yaml`
- disposition (as filed): `open_next_step`; last_reviewed 2026-10-24

next_action.step (verbatim):

> Run the break-even growth ladder (IDEA-20261018-a0830c): measure kappa_rel for the best FAM-1 geometry at 3+ rungs from 16 to 32 bits with planted positive controls, and require growth of 2^(8 delta*) per rung; run the scheduled log-GAP validation EXP-PFDR-bb0d26 in the same instrument.

next_action.discriminates (verbatim):

> kappa constant in N (as observed so far) closes the family as sub-break-even by law (exhausted_at_scale); kappa growing at or above the break-even rate is the first structural relation source on F_p and must then be priced end to end against matched rho.

best_measured (verbatim):

> EXP-PFDR-ca5e01 O-MIXED: 63 null / 16 intermediate / 11 underpowered cells, kappa in [0.889, 1.103], planted kappa ~2.6 recovered; kappa_rel 0.998 (small_x TT m = 4, 30-32 bits)

forecloses (verbatim): `harvest x-key collisions the mitm engine discards`; `pair-sum coincidence excess of structured factor bases`; `additive energy of label-GAP bases gives free relations`; `rho-trail harvest of coincidences`; `only attempt targets whose x(R) predicts a decomposition`

**AUD-1.** Open lead; not applicable.

**AUD-2.** Open lead; the forecloses phrases mark coverage, and none is a closure. No change.

**AUD-3.** Not applicable to this disposition.

**AUD-4.** **Observed new state.** The second half of next_action ("run the scheduled log-GAP validation
EXP-PFDR-bb0d26") has executed. From `car:ledger/decisions/DEC-20261022-9aec2b.yaml`:
- The tool wrote outcome `O-NULL`, headline `SUPPORT_SCOPED`, 44 of 45 cells powered and null.
- Largest |kappa - 1| = 0.0414 at b28-r1-n256 (ci95 [1.0100, 1.0743], z = 2.52). Smallest
  kappa = 0.9649 at b28-r2-n512.
- Planted kappa >= 1.2885 and plant z >= 21.9 in every powered cell.
- Secondary slopes of log kappa per log2 n lie in [-0.0088, +0.0042].
- One cell is invalid (b20-r3-n4096).
- H-PFDR-727bfc stays `approved`. The independent review (NA-1) is pending, and nothing is
  promoted.

The lead's best_measured still cites only EXP-PFDR-ca5e01.

**Observed, re-tabulated by the reviewer** from `car:experiments/EXP-PFDR-bb0d26/runs/RUN-PFDR-089edc/analysis.json`:
- Kappa at fixed (r, n) across 20/24/28 bits: 14 of 15 (r, n) groups show no monotone change.
- r1-n256 reads 0.9999 -> 1.0246 -> 1.0414, below the frozen |z| > 4 flag.

Interpretation, conditional on review: the experiment is already a 3-rung growth ladder at fixed
(r, n). Its single monotone group is below the detection rule. It is a candidate for the first
fresh-curve rung of the IDEA-20261018-a0830c ladder (32/36 bits), not evidence.

**Would a theorem decide faster? Partly.**
- (a) x-structured bases: derived (reviewer), a sketch not checked independently. A Bombieri/Weil
  count of additive quadruples in an x-window base gives E(F) = |F|^4/N (1 + O(N p^{1/2} log^2 p / |F|^2)).
  That is nontrivial only for |F| >> N^{3/4}, so no short proof exists in the IC regime
  |F| <= N^{1/2}, and the ladder stays.
- (b) log-structured (GAP) bases: a short lemma shows that coincidences add no information for
  bases constructed from points of known form. It does not bound x-structured bases.

Lean target candidate: "Let N be prime, a, d_1..d_r in Z/N, and F a subset of a PROPER GAP
{a + sum_j i_j d_j : 0 <= i_j < L_j}, where proper means the map from (i_j) is injective. Then every
additive coincidence f1 + f2 = f3 + f4 among elements of F holds identically in the coordinates
(i_j). Every integer relation it implies therefore lies in the Z-span of the parametrization
relations log f = log a + sum_j i_j(f) log d_j."

Consequences:
- The coincidence module can have rank up to B - r - 1, so it leaves only the r + 1 generator logs
  unknown. These are genuine free relations.
- When F is built by group operations from points of known form (the log-GAP arm and its planted
  control), those relations restate the construction and carry no information about the target.
- In an improper GAP, an extra coincidence is a low-height relation sum_j k_j d_j = 0 among the
  generators. That is new information, and it is the open content of the lead. The lemma does not
  exclude it.
- The lemma says nothing about x-structured bases.

Proposed next_action:
- (i) the independent review of EXP-PFDR-bb0d26;
- (ii) a0830c rungs at 32/36 bits with fresh-curve replication of r1-n256;
- (iii) the GAP relation-rank lemma.

**AUD-5.** Not applicable to this disposition.

**AUD-6.** See the family section (conservation law, SO-TABLE).

## LEAD-ICP-construction-normal-form

- file: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/ic-prime/LEAD-ICP-construction-normal-form.yaml`
- disposition (as filed): `open_unexamined`; last_reviewed 2026-10-24

next_action.step (verbatim):

> Compute the H-PFDR-6189d0 normal form over every PFDR/PATH proposal and hypothesis, and run the H-PATH-7fdef7 estimator-bias check on the sealed 8-32-bit prime fixtures.

next_action.discriminates (verbatim):

> A quotient much smaller than the record count lets the atlas mark duplicates mechanically; a biased single-cell estimator invalidates any exponent claim that used it.

forecloses (verbatim): `deduplicate proposed polynomial systems by normal form`; `result classes between nothing and a break`; `instrument must show dynamic range before a null counts`

**AUD-1.** Open lead; not applicable.

**AUD-2.** Not applicable to this disposition.

**AUD-3.** Not applicable to this disposition.

**AUD-4.** Not applicable to this disposition.

**AUD-5.** First discriminating step, as filed: compute the H-PFDR-6189d0 normal form over every PFDR/PATH
proposal and hypothesis, and run the H-PATH-7fdef7 estimator-bias check on the sealed 8-32-bit
fixtures. Outcome map:
- Normal-form quotient <= ~10% of the record count: mechanical duplicate marking in coverage.tsv.
  No ECDLP disposition changes.
- Quotient ~ record count: the dedup instrument does not compress. Close it as `exhausted_at_scale`.
- Estimator bias interval excludes 0: re-read every lead whose best_measured exponent used the
  single-cell estimator. Leads whose closure rests on such an exponent go back to open.
- Unbiased: no change.

Proposed closure: this is methodology, not a cost mechanism. LEAD-EXO-methodology-instruments
(`car:knowledge/leads/ecdlp/exotic/LEAD-EXO-methodology-instruments.yaml`, open_next_step) states
"Records that test the program's own instruments ... they cannot by themselves make ECDLP cheaper".
Mark this row `closed_dominated`, `dominated_by: LEAD-EXO-methodology-instruments`, and append both
steps to that row's next_action.

**AUD-6.** No standing obstruction.

## LEAD-ICP-coppersmith-smallroot-semaev

- file: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/ic-prime/LEAD-ICP-coppersmith-smallroot-semaev.yaml`
- disposition (as filed): `open_next_step`; last_reviewed 2026-10-24

next_action.step (verbatim):

> Compute the provably optimal shift set (Ryan, EUROCRYPT 2025; Feng-Luo-Chen-Nitaj-Pan sumset bounds) for the 13-monomial S_3 polytope and the full-tree (m, w) = (4, 2) system, and the rank-r >= 2 GAP substitution of H-PFDR-3c7d1e, with tools/smallroot_reach.py as the calibrated calculator; then a planted direct-box S_4/S_5 recovery (H-PFDR-621852) at 40-56 bits only if the computed reach clears 8/9.

next_action.discriminates (verbatim):

> Optimal reach >= 0.8889 at (4,2) (or any rank-r GAP cell with positive margin) reopens a concrete lattice decomposition oracle to be measured; optimal reach < 0.8889 everywhere turns the current heuristic -0.0481 closure into a strategy-independent one and closes the family.

best_measured (verbatim):

> S_3 reach rigorous delta <= 0.10, heuristic 0.12-0.16 (needs 1/2), Probes B/C at 40/56 bits; epsilon margin -0.0481 at (m,w) = (4,2) (JM extended 0.8408 vs demand 8/9)

forecloses (verbatim): `Coppersmith small roots of summation polynomials`; `small-x factor base solved by LLL`; `windowed addition tree with lattice reduction`; `symmetric e1 e2 lattice for S_3`; `rank-r generalized arithmetic progression factor base`; `lattice-assisted meet-in-the-middle decomposition`

**AUD-1.** Open lead; not applicable.

**AUD-2.** Open lead; no closure to audit. One note for a future closure: `rank-r generalized arithmetic
progression factor base` is listed while `car:analysis/smallroot-reach/CLOSURE.md` is scoped
"rank-1 GAP and tree scope only" (the lead's own evidence note). Any closure must keep that scope.

**AUD-3.** Not applicable to this disposition.

**AUD-4.** **Would a theorem decide faster? No short theorem found.**
- No strategy-independent upper bound on Coppersmith-type reach is known. Reach depends on the
  shift polytope.
- The first-moment density bound (`car:research/lattice_index_calculus_20261015/report.md`:
  "E_R N(R) = M^m/r, Pr[N(R)>0] <= min(1, M^m/r)") is necessary but does not bind at the demand 8/9.

The queued step is itself a proof-type computation: the asymptotic reach of a given shift polytope
is an exact integral over its Newton polytope. Outcome map, unchanged:
- >= 0.8889 at (4, 2), or any positive-margin rank-r GAP cell -> the planted 40-56-bit run.
- < 0.8889 for every polytope in the family -> `closed_obstructed`, kind proof, scope:
  "Coppersmith-type lattices with these polytopes".

Proposed addition: absorb the Newton-target shift route of IDEA-20261015-9defe9 from
LEAD-ICP-lattice-ic-relation-construction. It is the same small-root mechanism.

**AUD-5.** Not applicable to this disposition.

**AUD-6.** See the family section (SO-ALGFB).

## LEAD-ICP-digit-presentation-solving-degree

- file: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/ic-prime/LEAD-ICP-digit-presentation-solving-degree.yaml`
- disposition (as filed): `open_next_step`; last_reviewed 2026-10-24

next_action.step (verbatim):

> Run the certified finite degree-growth ladder with blocking controls (H-PFDR-d5f90f) on the digit system at m = 2, 3 over s = 2..8 with independent primes per s (fixing the pseudoreplication of EV-PFDR-99c699) and the support-matched and block-factored nulls; then the adaptive staircase arm (H-PFDR-f3fe89) on the 12/16/20-bit panel.

next_action.discriminates (verbatim):

> d_lf growing with s at the semi-regular rate (as every measured cell so far suggests) closes the lane as exhausted at the measured scale; a d_lf bounded in s strictly below the null is the first elliptic early fall over F_p and reopens the conditional cost table (still needing sigma < 1).

best_measured (verbatim):

> d_ff = m 2^{m-1} + floor((s - 2^{m-1})/2) + 1, curve-independent and reproduced by a curve-free block-factored null (EV-PFDR-1394a4); sigma > 1 at every tested s (EV-PFDR-99c699); no syzygy beyond Koszul (EV-PFDR-e67f06)

forecloses (verbatim): `base-B digit presentation as Weil descent over a prime field`; `bounded last fall degree for prime-field Semaev systems`; `first fall degree of the digit-presented decomposition system`; `Groebner staircase or semigroup presentation of the decomposition ring`; `carry-circuit encoding of prime-field decomposition`; `Yokoyama semi-normality object`

**AUD-1.** Open lead; not applicable.

**AUD-2.** Not applicable to this disposition.

**AUD-3.** Not applicable to this disposition.

**AUD-4.** **Would a theorem decide faster? No short theorem found.**
- The observed closed form d_ff = m 2^{m-1} + floor((s - 2^{m-1})/2) + 1 equals a curve-free
  block-factored null (`car:ledger/evidence/EV-PFDR-1394a4.yaml`).
- Proving that the digit system's low-degree syzygies coincide with the null's for every curve
  would close the first-fall part. That is a research problem, not a short proof.
- No bound on the last fall degree is known (KR-IC-fbdb61 covers Weil descent over extension
  fields, not digit presentations).

The queued ladder is the right decider. Its stated repair (independent primes per s) answers the
evidence defect recorded in EV-PFDR-99c699 ("four integers repeated 120 times; receipt pinned to
an unreachable blob").

**Contamination check (observed).** No evidence file of this lead mentions `s4_expr` or
`harness/semaev` (grep over EV-PFDR-1394a4/99c699/f71d7f/e67f06/acc71a). KN-OPEN-5b3a08's s4_expr
defect therefore has no observed path into this lead.

**AUD-5.** Not applicable to this disposition.

**AUD-6.** See the family section.

## LEAD-ICP-extension-field-embedding

- file: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/ic-prime/LEAD-ICP-extension-field-embedding.yaml`
- disposition (as filed): `closed_obstructed`; last_reviewed 2026-10-24
- obstruction.kind: `cost_model`

obstruction.statement (verbatim):

> Gaudry's cost on E(F_{p^n}) is O~(p^{2-2/n}) against the original sqrt(p): p at n = 2 and p^{4/3} at n = 3; the embedding enlarges the problem faster than the subfield helps. Scope: any fixed n.

obstruction.revisit_when (verbatim):

> A decomposition over F_{p^n} with exponent below 1/(2n) in |E(F_{p^n})|, i.e. far beyond Gaudry/Diem.

forecloses (verbatim): `lift the prime-field curve to an extension field to get a subfield`; `base change to F_{p^2} then Gaudry index calculus`; `Weil descent for a prime-field curve`

**AUD-1.** Trigger "a decomposition over F_{p^n} with exponent below 1/(2n) in |E(F_{p^n})|": **not fired**.
The only new extension-field cost in the delta is JV (n-1) on F_{q^5}: q^2 work on a group of size
q^5, exponent 0.4 > 0.1 (`crypto:research/joux_vitse_n1_20261015/MODEL.md`).

**AUD-2.** Scope "any fixed n" matches the forecloses phrases, so there is no over-foreclosure. The phrase
`base change to F_{p^2} then Gaudry index calculus` is covered by the even-n case of the AUD-3
lemma.

**AUD-3.** **A short proof replaces the cost model.**

Lean target candidate: "Let p be an odd prime, E/F_p an elliptic curve y^2 = f(x), n >= 1, and
S_n = {P in E(F_{p^n}) : P = O or x(P) in F_p}. If n is odd, S_n = E(F_p). If n is even,
S_n = E(F_p) union iota(E^d(F_p)), where E^d is the quadratic twist by a non-square d in F_p and
iota(x, y) = (x, y sqrt d)."

Proof: x in F_p gives y^2 = f(x) in F_p, so y lies in F_{p^2} intersect F_{p^n}. That is
F_{p^{gcd(2,n)}}, which is F_p for odd n.

Corollaries:
- For odd n, every decomposition R = sum +-P_i of R in E(F_p) over the subfield base is a
  decomposition inside E(F_p) over a subset of E(F_p). The embedded instance is the prime-field
  instance verbatim.
- For even n, iota(E^d(F_p)) intersect E(F_p) is contained in E[2]. The twist summands of a
  decomposition of a target in the odd prime-order subgroup therefore contribute only to the
  2-primary part, and nothing to the prime-order component (derived, reviewer).

So the closure does not depend on Gaudry's exponent: the subfield condition buys no structure.

Proposed change: `obstruction.kind: cost_model` -> `proof`. Replace the statement with the lemma
above, and keep the Gaudry comparison as context. Disposition unchanged. The Mathlib finite-field
subfield lattice should make the field step short.

**AUD-4.** Not applicable to this disposition.

**AUD-5.** Not applicable to this disposition.

**AUD-6.** Obstruction (Gaudry exponent): with the AUD-3 lemma the obstructing quantity disappears. None found.

## LEAD-ICP-full-width-arity-grid

- file: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/ic-prime/LEAD-ICP-full-width-arity-grid.yaml`
- disposition (as filed): `open_blocked`; last_reviewed 2026-10-24

next_action.step (verbatim):

> Run the approved 63-bit three-base m = 2..8 solver-to-certificate feasibility panel (H-ICPERF-05021b) once the prime63 launcher admission repair and RSS monitor/positive controls are fixed; same for the k11 ordinary-binary matched bases.

next_action.discriminates (verbatim):

> Completed cells give the first measured distance to rho at 63 bits per arity (the generic model predicts it widens); persistent censoring at m >= 4 confirms the writability boundary for this route.

next_action.blocked_by: `problems/full-width-ic-arity-grid-unmeasured.md`

best_measured (verbatim):

> prime complete-solve arity ladder stops at 32 bits and m = 7; 63-bit second run: six time-censored planted controls, one monitor-error cell

forecloses (verbatim): `complete index calculus at 63-bit prime subgroup`; `coset factor base with quadratic lift at m = 8`; `Frobenius-invariant base on Koblitz cells against sqrt(2n) rho`; `full arity grid 2 to 8`

**AUD-1.** Open lead; not applicable.

**AUD-2.** Not applicable to this disposition.

**AUD-3.** Not applicable to this disposition.

**AUD-4.** **A counting lemma decides part of the grid before any run.**

Inputs:
- The conservation law (KN-FIND-007, quoted in LEAD-ICP-algebraic-membership-factor-base:
  "mean per-target yield is binomial(B+m-1, m)/N for every base of size B").
- The support bound in `crypto:problems/eccp131-full-parameter-index-calculus.md`: "The ordered
  signed triple list has at most (2B)^3 = 8B^3 point entries ... probability at most 8B^3/(n-1)".

Derived (reviewer): with B = 475 and r ~ 2^63, matched rho = 0.886 * 2^31.5 = 2^31.33 GAE. If
attempts are on uniformly drawn targets and each attempt costs >= 1 GAE (a fresh target point),
the relation phase alone needs >= B * r / (2^s C(B+m-1, m)) GAE, with s = 0 (unsigned) or s = m
(signed). The break-even per-attempt cost is T* = 2^31.33 / that quantity:

| m | log2 C(B+m-1,m) | log2(B r / C) | log2 T* (s = 0 / s = m) |
|--:|--:|--:|--:|
| 2 | 16.79 | 55.11 | -23.8 / -21.8 |
| 3 | 24.10 | 47.79 | -16.5 / -13.5 |
| 4 | 31.00 | 40.89 | -9.6 / -5.6 |
| 5 | 37.58 | 34.31 | -3.0 / +2.0 |
| 6 | 43.90 | 27.99 | +3.3 / +9.3 |
| 7 | 50.01 | 21.89 | +9.4 / +16.4 |
| 8 | 55.92 | 15.97 | +15.4 / +23.4 |

Consequences, conditional on uniform targets with no preselection:
- For m <= 4, no oracle, generic or not, brings this B = 475 relation phase under matched rho at
  63 bits.
- m = 5 needs T_dec <= 4 GAE even under the favourable convention.
- The lemma holds at B = 475 only. Derived (reviewer, with LA costed at c = 1 GAE per B^2 cell):
  with B free, the optimum is B ~ 2^15.3, where the break-even T* is 2^8.3 (unsigned) to 2^12.3
  (signed) GAE at m = 4 and 2^21.3 to 2^26.3 at m = 5. The lemma therefore does not foreclose
  m >= 4 in general, consistent with the revisit_when of LEAD-ICP-generic-table-decomposition
  ("T_dec << p^{1/4}"). It does say that the fixed B = 475 panel is the wrong place to look for m = 4.
- The quantity named in `discriminates` ("first measured distance to rho at 63 bits per arity")
  is therefore pre-decided (> 1) for m <= 4. Those cells can only measure solver feasibility and
  constants. The informative measurement is T_dec(m) at m = 6..8 against the T* column.

**Observed (m = 2 censors).** From `car:problems/icperf-prime63-monitor-and-positive-controls.md`,
RUN-ICPERF-eb0d88 had three planted m = 2 cells "timeout_censored" at 600.1 s. The coset arm
stopped in Groebner work; the random and small-x arms stopped in root enumeration. The supervisor
returned `invalid_output` because of `car:problems/icperf-prime63-m2-output-contract-mismatch.md`.
Derived (reviewer): at m = 2 a planted decomposition is decided by at most 2B = 950 point
subtractions plus a hash lookup (the subtraction oracle of LEAD-ICP-generic-table-decomposition).
A 600 s censor is therefore a fact about the formulation, not a feasibility bound.

Proposed change (disposition unchanged):
- Add `problems/icperf-prime63-m2-output-contract-mismatch.md` to blocked_by.
- Add a subtraction-oracle positive control to the successor.
- Replace the distance-to-rho discriminator with the T*(m) comparison, and demote the m = 2..4
  natural cells to instrument controls.

Lean target candidate: "For a finite group G of prime order N, F a subset of G with |F| = B, and
targets drawn uniformly: if the mean number of signed m-decompositions per target is
<= 2^m C(B+m-1, m)/N, then any procedure that obtains B - 1 decompositions using one target per
attempt makes, in expectation, >= (B-1) N / (2^m C(B+m-1, m)) attempts."

**AUD-5.** Not applicable to this disposition.

**AUD-6.** See the family section (conservation law).

## LEAD-ICP-generic-table-decomposition

- file: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/ic-prime/LEAD-ICP-generic-table-decomposition.yaml`
- disposition (as filed): `closed_obstructed`; last_reviewed 2026-10-24
- obstruction.kind: `theorem`

obstruction.statement (verbatim):

> Any decomposition oracle that enumerates or table-looks-up factor-base elements is a generic time/memory trade-off and obeys S*T^2 >~ N (Corrigan-Gibbs--Kogan) and T >~ sqrt(N) (Shoup); with linear algebra included the two-term model gives m = 2 >= 3 (pT_dec)^{2/3} and m = 3 only ties rho even with T_dec = O(1). Measured on generated prime-order E/F_p, 12-32 bits: exhaustive IC exponent 0.99 (m = 2) and 1.01 (m = 3), mitm 0.67 / 0.75 / 0.60 at m = 3/4/5 (4/7 at m = 7) against rho 0.50 [0.48, 0.52]; Table B gap to matched rho widens from 5.47x at log2 r = 11.9 to 13.5x at 23.4. Scope: any generic (enumeration/table) decomposition over F_p.

obstruction.revisit_when (verbatim):

> A non-generic decomposition oracle exists with per-attempt cost T_dec << p^{1/4} at arity m = 4 (an S_5 oracle at B ~ p^{1/5}), or a decomposition test sub-linear in |F|.

best_measured (verbatim):

> S_IC/S_rho = 5.47x (log2 r = 11.9) to 13.5x (log2 r = 23.4), Table B prime ladder, unvalidated (pre-gate); FRONTIER fitted exponent 0.841 [0.500, 1.024] for folded mitm m = 2

forecloses (verbatim): `pair-table meet-in-the-middle decomposition beats rho at higher arity`; `faster S_3 root finding or batched subtraction makes prime IC sub-rho`; `choose the factor-base size B optimally to cross rho`; `free decomposition oracle at m = 2 or m = 3`; `generic collision floor for x-key relations`

**AUD-1.** Trigger (a), "a non-generic decomposition oracle ... T_dec << p^{1/4} at arity m = 4": **not fired**.
- IDEA-20261018-ac3694 (`car:ledger/proposals/IDEA-20261018-ac3694.yaml`) records "the
  non-enumerative membership oracle EXP-ICEX-153c34 is approved and unbuilt".
- IDEA-20261018-e7a860 (K conversion for the m = 4 oracle, binary) is `proposed`.

Trigger (b), "a decomposition test sub-linear in |F|": **not fired** (same records).

Stale evidence, observed:
- The evidence note for `crypto:docs/ic/LEADERBOARD.md` says "Table B prime rows fp10..fp24, all
  unvalidated (pre-gate)", and best_measured says "unvalidated (pre-gate)". LEADERBOARD lines 49-56
  now mark all eight prime rows `validated` (commit a8d8e3cd38).
- `crypto:docs/bounds/FRONTIER.md` line 123 (fit v2) reports the folded mitm m = 2 exponent as
  0.841 [0.646, 0.953], not [0.500, 1.024].

Proposed change: update best_measured and both evidence notes. No disposition change.

**AUD-2.** Three over-foreclosures:
- (i) The kind is `theorem`, but the m = 2/m = 3 part of the statement is a two-term cost model.
  Shoup and CGK cover only enumeration and table oracles.
  - `faster S_3 root finding or batched subtraction makes prime IC sub-rho` and `free decomposition
    oracle at m = 2 or m = 3` cover algebraic root finding, which reads coordinates and is not
    generic. Only the cost model forecloses it.
  - The statement itself says m = 3 "only ties rho". An exponent tie leaves the constant open,
    and the phrase claims more. AUD-3 gives the constant condition.
- (ii) `choose the factor-base size B optimally to cross rho` has no arity or oracle qualifier. At
  m >= 4 only the generic-oracle part applies, and the lead's own revisit_when names a non-generic
  m = 4 oracle.
- (iii) Scope alignment. LEAD-ICE-generic-oracle-arity-cost-floor states "Scope: oracles that do not
  read curve coordinates algebraically" and cites CHW 2026/384 and DKM 2025/783
  (IDEA-20261018-49fdf7). Use the same scope sentence here.

**AUD-3.** The m = 2/3 cost-model part can be replaced by a short proof that rests on conservation.

Lean target candidate:
- Setting: G cyclic of prime order N, F a subset of G with |F| = B, m in {2, 3}.
- Hypotheses:
  - (H1) attempts use targets drawn uniformly and independently of F, each costing >= T GAE;
  - (H2) the mean number of signed decompositions of a uniform target over F is
    <= 2^m C(B+m-1, m)/N (KN-FIND-007);
  - (H3) >= B - 1 relations are needed, and linear algebra on B unknowns costs >= c B^2 GAE.
- Conclusion: expected total cost >= min_B [(B-1) N T / (2^m C(B+m-1, m)) + c B^2]. For m = 2 this
  is Omega((c T^2 N^2)^{1/3}), exponent 2/3. For m = 3 it is >= sqrt(3 c T) sqrt(N) (1 - o(1)).

Derived (reviewer): m = 3 IC beats the rho floor sqrt(pi/4) sqrt(N) only if 3 c T < pi/4.
- With T >= 1 (target generation) and Wiedemann-type c ~ 2(m+1) mu, where mu is a mod-N multiply
  in GAE (~0.1-0.2), 3cT is 2.4-4.8 against pi/4 = 0.785. That puts m = 3 IC at >= 1.7-2.5x the
  rho floor even with a free oracle.
- This is a constant-level statement that depends on mu. It is recorded as a target, not a closure.

**AUD-4.** Not applicable to this disposition.

**AUD-5.** Not applicable to this disposition.

**AUD-6.** SO-TABLE. The structured generic-group model (CHW, ePrint 2026/384, KN-LIT-7606) takes the
structured fraction delta as a hypothesis: DL costs Omega(min(sqrt(q), 1/delta)). That turns the
obstruction into a per-oracle measurable delta (IDEA-20261018-49fdf7).

## LEAD-ICP-gfp5-oa-sdhp-jv

- file: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/ic-prime/LEAD-ICP-gfp5-oa-sdhp-jv.yaml`
- disposition (as filed): `open_next_step`; last_reviewed 2026-10-24

next_action.step (verbatim):

> Freeze the JV/Granger sources, measure C_pdp4 at toy p' and project to p = 2^64 (H-GFPN-3366ea), and file the JV (n-1) full-ECDLP closure arithmetic (goal criterion C5).

next_action.discriminates (verbatim):

> A measured C_pdp4 gives the concrete OA-SDH cost for both deployed curves (a protocol-level, not ECDLP, weakness); the closure arithmetic removes JV (n-1) from the ECDLP budget unless it unexpectedly falls below 2^160.

forecloses (verbatim): `oracle-assisted static Diffie-Hellman on EcGFp5`; `Joux-Vitse n-1 decomposition for full ECDLP`; `learning phase with a static DH oracle`

**AUD-1.** Open lead; not applicable.

**AUD-2.** Not applicable to this disposition.

**AUD-3.** Not applicable to this disposition.

**AUD-4.** **The JV (n-1) half of the discriminator is already answered by existing documents, with the
opposite sign to the lead's expectation.**

Observed:
- `crypto:research/joux_vitse_n1_20261015/MODEL.md` lines 50-67: "trials per relation (n - 1)! q = 24 q";
  "relations needed |F| + 1 ~ q/2"; "relation search ... ~ 12 q^2 c~"; "c~, one trial ~ 3*10^9
  F_p mults"; "c_add ~ 190 (this repository's affine F_{p^5} addition)"; "q* ~ ... ~ 2^{55.3}".
  The paper's crossover is quoted as "plus rapide des que la cardinalite du corps de base est plus
  grande que 2^{60}" (odd p).
- `crypto:problems/k5-joux-vitse-trial-cost-and-fpk-ecbench.md`: one trial costs "~ 5-9*10^9 F_p
  multiplications (measured, flat in q)", and on today's engine "C'' = 1.104*10^10".
- `car:research/gfp5_deployed_curves_20260920.md`: "the Joux-Vitse (n-1)-point variant for full DLP
  needs >= p^2*4! ~ 2^132.6 attempts at p = 2^64".
- `car:ledger/hypotheses/H-GFPN-3366ea.yaml`: the rho ruler is ~2^159.3 group operations (EcGFp5).

Derived (reviewer, model): IC/rho = 12 q^2 c~ / (sqrt(pi/4) sqrt(n) c_add), with q = 2^64 and
n ~ 2^319.
- For c~ in [3e9, 1.104e10], IC/rho = 2^-3.9 .. 2^-2.0.
- The MODEL.md ruler (q^{5/2}) gives 2^-4.3 .. 2^-2.45.
- So under the published heuristic and the repository's measured constants, JV (n-1) full ECDLP on
  EcGFp5 sits 2^2-2^4 below matched rho, with ~2^63 stored relations and linear algebra of ~2^128
  multiplications mod l.

This is the outcome `discriminates` calls "unexpected". It does not threaten the 128-bit design
target (about 2^155-2^157 GAE). The sign flips with a ~2^4 change in c~ or c_add.

The comparison is time-only. Charging memory (~2^63 relations, ~2^69 bytes, against rho's
negligible store) reverses it in an area-time accounting.

Do not import the Edwards-route constant (`REPORT_EDWARDS`): a twisted Edwards model needs a rational
4-torsion point, and EcGFp5 has #E = 2n, i.e. 2 mod 4.

Proposed change (disposition unchanged):
- mechanism: delete "expected to cost more than rho and is to be closed by arithmetic".
- discriminates: "JV (n-1)/rho priced with measured C_pdp4 and c_add. A ratio < 1 is a model-level
  sub-rho full-ECDLP route on a deployed curve, with memory ~2^63 relations. A ratio > 1 closes it."
- step: measure C_pdp4 on the actual descended EcGFp5/EcMasFp5 systems at toy p', and c_add of the
  best published F_{p^5} implementation.
- Add the three crypto paths as evidence.

**AUD-5.** Not applicable to this disposition.

**AUD-6.** Obstruction quoted is not standing (open lead). See the family section on SO-GEN for the rho ruler.

## LEAD-ICP-gfp5-odd-char-cover

- file: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/ic-prime/LEAD-ICP-gfp5-odd-char-cover.yaml`
- disposition (as filed): `open_blocked`; last_reviewed 2026-10-24

next_action.step (verbatim):

> Compute the odd-characteristic cover genus (or Diem bound) for both curves plus an isogeny-class control.

next_action.discriminates (verbatim):

> A genus within the hyperelliptic IC threshold for any curve in the class is a transfer lead; a genus bound above it closes the cover route for these curves.

next_action.blocked_by: `GOAL-GFPN-380702 pause condition: Diem / Gorla-Massierer source freeze not obtained (criterion C3)`

forecloses (verbatim): `GHS cover attack on EcGFp5`; `Diem cover for degree-5 extension curves`; `isogeny walk to a coverable curve over F_{p^5}`

**AUD-1.** Open lead; not applicable.

**AUD-2.** Not applicable to this disposition.

**AUD-3.** Not applicable to this disposition.

**AUD-4.** **A theorem decides this faster than the blocked source freeze.**

Observed, `crypto:research/ghs_cover_census_n5_20261013/README.md`:
- Question (line ~22): "the x-line with branch set B = x(E[2]), the smallest genus of the (Z/2)^m
  compositum of the n conjugate double covers over every F_q-structure tau (g = 2^{m-2}(r-4)+1)".
- Line ~44: "derived floors 33 (odd) / 33 (2 mod 4) / 25 (E(K)[2] = Z/2, 4 | #E) / 5 (E(K)[2] = (Z/2)^2)".
- Derivations table: "Cor. T5 | n = 5: E(K)[2] = Z/2 => g >= 25; #E(K) = 2 mod 4 => g >= 33 |
  proved (paper)"; "Prop. O5 | odd #E(K), n = 5: genera in {33, 97, 129} ... for j not in {0,1728}:
  minimum 33 iff j(E) not in F_q, else >= 97 | proved (paper)"; "Lemma H | ... m >= 4 never hyperelliptic".
- "These hold for every odd q (char != 2) and do not depend on the census."
- `car:research/gfp5_deployed_curves_20260920.md` line 17: EcGFp5 "2n, n 319-bit prime";
  EcMasFp5 "320-bit prime, cofactor 1".

Derived (reviewer):
- EcGFp5 has #E = 2 mod 4, so g >= 33 on every structure (Cor. T5).
- EcMasFp5 has odd order, so g >= 33 (Prop. O5). With a = 3 and b = 8z^4 (z^5 = 3), b^2 = 192 z^3,
  so j in F_p would need z^3 in F_p. Hence j is not in F_p and not in {0, 1728}, and 33 is attained
  by exactly one structure.
- Isogenous curves over K have equal #E(K) (Tate). The types "2 mod 4" (which forces E(K)[2] = Z/2)
  and "odd" (which forces E(K)[2] = 0) are therefore invariant on each isogeny class, so the floors
  hold for the whole class. This is the "isogeny-class control" the step asks for.

Pricing (model, reviewer):
- For genus g over F_p with p ~ 2^64 and relation probability ~1/g! (log2 33! = 122.7):
  conservative g! * q^{1-1/g} ~ 2^184.8; g! * q^{2-2/g} ~ 2^246.8; L_{q^g}[1/2, sqrt 2] at
  q^g = 2^2112 ~ 2^210.8. All exceed rho 2^159.3.
- The crossovers with 2^159.3 are near g ~ 28 (g! q^{1-1/g}) and g ~ 15 (g! q^{2-2/g}).
- The README itself notes "even genus 33 is 'sub-rho' in the exponent, but the constants grow very
  quickly with g".

Scope limits. The README says the floors "rest on the merged census's construction (branch-set
genus formula), which this study does not re-derive". From its "Not established" list:
- descent and injectivity of the transfer;
- degree-2 maps other than x. IDEA-20261024-d84f20 indexes these by E(K)/2E(K). Derived (reviewer):
  that group has order 2 for EcGFp5 (one further class) and is trivial for odd-order EcMasFp5.

Proposed change: `open_blocked` -> `closed_obstructed`.
- obstruction.kind: proof (genus floor) plus cost_model (pricing).
- scope: "x-line (Z/2)^m Weil-restriction covers over F_p of E/F_{p^5}, both curves and their
  isogeny classes".
- revisit_when: "a degree-2 map other than x (the non-trivial class of E(K)/2E(K) on EcGFp5)
  realizes genus <= 28, or a genus-g Jacobian IC whose relation probability does not decay like 1/g!".
- Add `related: LEAD-TRF-odd-char-descent-smith-quartic`.

Lean target candidate (Cor. T5; the 2-descent step is listed "not formalized"): "Let q be odd,
K = F_{q^5}, E/K with #E(K) = 2 mod 4. For every F_q-structure tau on P^1_K, the (Z/2)^m compositum
of the five double covers branched at tau^i(x(E[2]) union {infinity}) has genus >= 33."

**AUD-5.** Not applicable to this disposition.

**AUD-6.** New standing-type obstruction (genus floor 33). A theory that takes genus as a hypothesis, i.e. a
Jacobian IC whose cost does not carry g!, would reopen this. None found. Diem's plane-curve
algorithm needs small plane degree, and Lemma H rules out hyperelliptic models for m >= 4.

## LEAD-ICP-gfp5-rho-reference-audit

- file: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/ic-prime/LEAD-ICP-gfp5-rho-reference-audit.yaml`
- disposition (as filed): `closed_known`; last_reviewed 2026-10-24
- obstruction.kind: `literature`

obstruction.statement (verbatim):

> The generic costs are the published ones (rho ~ 2^160 per key; Kuhn-Struik / BL for many keys; kangaroo for narrow intervals). The program's certificate-bearing audit reproduced both orders and twist securities (EcGFp5 twist 120.66 bits; EcMasFp5 101.9321 vs self-reported 101.93, |delta| 0.0021). Nothing here can make ECDLP cheaper than rho; remaining items are instrument constants.

obstruction.revisit_when (verbatim):

> A deployment with narrow nonce intervals or many keys on one curve, or a walk-mixing defect measured in the F_{p^5} backend.

best_measured (verbatim):

> EcMasFp5 twist rho security 101.9321 bits reproduced (EV-GFPN-ba8e4d)

forecloses (verbatim): `Pollard rho cost on EcGFp5`; `multi-key rho on a STARK curve`; `kangaroo on narrow nonces for EcGFp5`; `SafeCurves audit of EcMasFp5 twist`

**AUD-1.** Triggers: "a deployment with narrow nonce intervals or many keys on one curve", and "a walk-mixing
defect measured in the F_{p^5} backend". Nothing in the delta bears on either. **Not fired.**

**AUD-2.** Over-foreclosure. The phrases `SafeCurves audit of EcMasFp5 twist` and `Pollard rho cost on EcGFp5`
read as complete audits, but `car:ledger/evidence/EV-GFPN-ba8e4d.yaml` line 237 says: "Six
SafeCurves criteria (field, equation, base, ladder, complete, ind) and extension-field transfer at
n = 5 are NOT examined; rho, MOV/anomalous transfer and twist are partial".

The statement "Nothing here can make ECDLP cheaper than rho" is true. For this family, though, rho
is not the binding ruler: the designer's Gaudry estimate (>= 2^142, KR-IC-e2d81b) and the JV (n-1)
model (~2^155-2^157 GAE, see gfp5-oa-sdhp-jv) are both below rho at 2^159.3.

Proposed change:
- Rename the phrase to "twist order and twist-rho audit of EcMasFp5".
- Add the "not examined" list to the statement's scope.
- Add a note that the 128-bit design target, not rho, is the comparison bar for decomposition
  routes on these curves.

**AUD-3.** Closure kind is `literature`; not applicable.

**AUD-4.** Not applicable to this disposition.

**AUD-5.** Not applicable to this disposition.

**AUD-6.** SO-GEN: see the family section.

## LEAD-ICP-gfp5-symmetrized-gaudry

- file: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/ic-prime/LEAD-ICP-gfp5-symmetrized-gaudry.yaml`
- disposition (as filed): `open_next_step`; last_reviewed 2026-10-24

next_action.step (verbatim):

> Run H-GFPN-6cc6aa (degree-4 Macaulay rank of the double-odd 2-torsion quotient against a cofactor-1 null) at toy p', then re-run the C1 ladder with an honest memory envelope (the m = 5 cells died at the degree-33 F4 round under 11 GiB) on >= 3 primes spanning >= 12 bits.

next_action.discriminates (verbatim):

> Rank ratio <= 1/2 with the null above 1/2 supports the symmetrized degree drop and gives a measured band to compare with 2^142 (still far above rho's ~2^160 only if the band collapses); no drop leaves the published estimate standing and closes the symmetrization arm.

best_measured (verbatim):

> H-GFPN-9a29be inconclusive: m = 5 cells memory_exhausted at p' = 4111, arm (i) at m = 5 never attempted (EV-GFPN-fc5950)

forecloses (verbatim): `symmetrized Gaudry attack on EcGFp5`; `two-torsion symmetry lowers the ideal degree at n = 5`; `side dichotomy of extension-field descent roots`

**AUD-1.** Open lead; not applicable.

**AUD-2.** Not applicable to this disposition.

**AUD-3.** Not applicable to this disposition.

**AUD-4.** **(a) The comparison ruler is internally inconsistent.** The discriminates text says "(still far
above rho's ~2^160 only if the band collapses)". But the raw published floor 2^142
(`car:research/gfp5_deployed_curves_20260920.md`, table "raw ... 2^40 -> 2^142") is already below
rho at 2^159.3. The binding comparison is the 128-bit design claim, against the bands 2^142 (raw),
2^129 (S_5) and 2^121 ((Z/2)^4 x| S_5).

Proposed rewrite: "Rank ratio <= 1/2 with the null above 1/2 supports the symmetrized band (2^121
for EcGFp5, below the 128-bit design target). No drop leaves the 2^142 raw estimate standing."

**(b) Counterexample check: no counterexample.**
- Translation by T = (0, 0) on y^2 = x(x^2 + 2x + 263z) is x -> 263z/x. The plain base
  {x in F_p} is therefore not T-invariant, since 263z is not in F_p.
- H-GFPN-6cc6aa uses "the published degree-1 rescaled predicate" and the formal substitution
  "t = u + c/u" (`car:ledger/hypotheses/H-GFPN-6cc6aa.yaml` lines 29-57).
- Derived (reviewer): a T-stable rescaled base always exists in odd-degree extensions. Choose
  c in F_p^* with 263z*c a square in K; this is possible because a non-square of F_p stays a
  non-square in F_{p^5}. Set s^2 = 263z*c and u = x/s. Then u(P+T) = c^{-1}/u, so {u in F_p} is
  T-stable.
- So the Macaulay-rank test is not pre-decided.

**(c) The ideal-degree part is known by orbit counting.** D_sym >= D/|G|, with equality iff G acts
freely on the generic fibre, as the design doc says. What needs measuring is the F4 degree of the
invariant presentation. Keep the experiment, with the honest memory envelope it names.

**AUD-5.** Not applicable to this disposition.

**AUD-6.** See the family section.

## LEAD-ICP-icperf-binary-pdp-solver

- file: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/ic-prime/LEAD-ICP-icperf-binary-pdp-solver.yaml`
- disposition (as filed): `open_next_step`; last_reviewed 2026-10-24

next_action.step (verbatim):

> Run H-ICPERF-c9380d: a Boolean-native Groebner column (BRiAl) with parseable d_solv and an RSS watchdog on l in {5, 6}, with WDSat installed on the runner and the side-classified exhaustive table as ground truth.

next_action.discriminates (verbatim):

> A >= 10x SAT-over-Groebner gap on every cell makes the gap structural and fixes the solver for the boundary table; any l = 6 cell below that threshold marks the reported gap as an engine-availability artifact. Either way no arm has yet grown slower than the pair-table MITM floor.

best_measured (verbatim):

> EV-ICPERF-390707: five unverified SAT answers are quadratic-twist decompositions, instrument not invalidated, gap direction reproduced (moderate); m = 3 F4/F6/SAT slopes 0.53-0.58 vs MITM floor 0.207

forecloses (verbatim): `SAT solver beats Groebner for point decomposition`; `WDSat conflict law for descended Semaev systems`; `add curve-membership constraints to the SAT core`; `branching order versus structure effect in DPLL`

**AUD-1.** Open lead; not applicable.

**AUD-2.** **Family misfiling.** The mechanism is "the Weil-descended binary PDP ... on the ICPERF boundary",
a binary problem. It overlaps LEAD-ICE-sat-xor-pdp-oracle (open_next_step).

Proposed change: move the row to ic-binary, or ic-engine, with `related: LEAD-ICE-sat-xor-pdp-oracle`.

**AUD-3.** Not applicable to this disposition.

**AUD-4.** No theorem decides whether a >= 10x SAT/Groebner gap is structural. A blocking control is missing,
though:
- `crypto:docs/ic/LEADERBOARD.md`, frontier-audit row: "Current-binary root-finder replay-all:
  current main (2026-10-19): 72/168 identical; 96 mismatches across all four IC arms ... Open regression".
- IDEA-20261018-b90b0c (`car:ledger/proposals/IDEA-20261018-b90b0c.yaml`): "inherited F4 ... is not
  reproducible across hosts for 48 replays".

Proposed change: add a replay-identity gate on every Groebner column of H-ICPERF-c9380d before the
>= 10x rule is read. Disposition unchanged.

**AUD-5.** Not applicable to this disposition.

**AUD-6.** See the family section.

## LEAD-ICP-icperf-writability-boundary

- file: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/ic-prime/LEAD-ICP-icperf-writability-boundary.yaml`
- disposition (as filed): `closed_obstructed`; last_reviewed 2026-10-24
- obstruction.kind: `cost_model`

obstruction.statement (verbatim):

> At the best viable arity the descended ANF exceeds the whole per-decomposition rho budget by +6.3 bits (n = 233), +18.8 (283), +24.2 (113), +25.6 (127), +40.8 (ECC2K-130) and +37.4 (K-163); the cost is paid before any solver runs. Scope: standardised binary curves with n <= 283, unchained descended ANF; the crossover is inside (283, 409].

obstruction.revisit_when (verbatim):

> n >= 409, or a representation (e.g. chained S_3 at m = 5, 6, ~2^31-2^33 monomials) whose written size plus solve fits under the rho budget with memory charged.

best_measured (verbatim):

> ANF size minus rho budget: +40.8 bits at ECC2K-130, -4.9 bits at n = 409 (m = 4)

forecloses (verbatim): `index calculus on ECC2K-130 with a better solver`; `chained Semaev system at m = 5 or 6 on ECC2K-130`; `memory column for block Wiedemann at the cap locus`

**AUD-1.** Triggers: "n >= 409", or "a representation (e.g. chained S_3 at m = 5, 6 ...) whose written size
plus solve fits under the rho budget". Nothing in the delta bears on the first. For the second,
H-ICPERF-3982eb ("Canonical summand order and gamma-bound binary m8 solver feasibility") is
`specified`, and its EXP-ICPERF-554db4 has approved_by null (`car:ledger/.index/experiments.jsonl`).
**Not fired.**

**AUD-2.** - **Family misfiling:** the scope is "standardised binary curves with n <= 283". Move the row to
  ic-binary.
- **Self-contradiction:** the forecloses phrase `chained Semaev system at m = 5 or 6 on ECC2K-130`
  blocks exactly the representation that revisit_when names as the reopening condition ("chained
  S_3 at m = 5, 6, ~2^31-2^33 monomials"). The proved scope is "unchained descended ANF".

Proposed change: delete that phrase, or requalify it as "unchained".

**AUD-3.** No short proof. A lower bound on the written ANF size needs the descended monomials not to cancel.
Certifying that for each standardized curve is not a short argument. Keep `cost_model`.

**AUD-4.** Not applicable to this disposition.

**AUD-5.** Not applicable to this disposition.

**AUD-6.** Obstruction (ANF size > rho budget). Theories that take "too large to write" as a hypothesis:
implicit or black-box representations, such as straight-line programs, chained S_3 circuits, and
evaluation-oracle solvers. The chained-S_3 route is already in revisit_when.

## LEAD-ICP-isogeny-transported-relation-yield

- file: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/ic-prime/LEAD-ICP-isogeny-transported-relation-yield.yaml`
- disposition (as filed): `open_blocked`; last_reviewed 2026-10-24

next_action.step (verbatim):

> Finish the 17 missing arms of EXP-ECTD-0cf008 (32,768 targets each) after the recovery amendment, reporting coverage and variance, not only mean yield.

next_action.discriminates (verbatim):

> Transported/native yield ratios within the A/A band confirm the conservation prediction and close the lead; a coverage or variance excess that grows with field size is the only outcome that would matter.

next_action.blocked_by: `problems/prime-field-arity3-relation-oracle.md`

best_measured (verbatim):

> conductor-gap counted diagnostics IC floor/crater 0.975 [0.603, 1.451] (ell = 8209), 1.127 [0.922, 1.342] (ell = 131101): no separation

forecloses (verbatim): `walk the isogeny volcano to a curve with better relation yield`; `transport the factor base along an isogeny`; `crater versus floor index calculus`

**AUD-1.** Open lead; not applicable.

**AUD-2.** Not applicable to this disposition.

**AUD-3.** Not applicable to this disposition.

**AUD-4.** **A short theorem decides the transported arms.**

Derived (reviewer): let phi: E -> E' be an F_p-isogeny with gcd(deg phi, r) = 1, and G = <P> of
prime order r. Then phi restricted to G is a group isomorphism onto phi(G), and phi(-X) = -phi(X).
For F a subset of G and R in G, (P_1..P_m) -> (phi P_1..phi P_m) is a bijection between the signed
m-decompositions of R over F and those of phi(R) over phi(F). For uniform targets, the whole
distribution of decomposition counts of the transported base (mean, variance and coverage) is
therefore identical to the source base's on E.

Consequences:
- "transported vs source-native" arms are exact A/A replicates.
- "transported vs native-on-E'" is really "native F on E vs native F' on E'", a comparison of two
  native bases on two curves.
- Observed: the 4 `u2-transport` arms are "stuck waiting_on_dependencies"
  (`car:problems/ectd-arity3-panel-infrastructure-loss.md`). They can be dropped, or kept as
  known-answer A/A controls.
- What remains open is native-base coverage and variance across volcano levels. This is
  consistent with SO-ISO and KR-RHO-755e35.
- Scope of the lemma: occupancy, yield, coverage, variance and relation rank, the quantities
  EXP-ECTD-0cf008 measures. It does not cover per-attempt oracle cost: an oracle that exploits the
  x-structure of the source base, such as small-x windows, loses that structure after transport.

Proposed next_action: "finish the native arms only (the 13 of the 17 missing arms that are not
transport arms). The transported arms are determined by their source arms through the bijection
lemma." Add `problems/ectd-arity3-panel-infrastructure-loss.md` to blocked_by.

Lean target candidate: "If f: G -> G' is an isomorphism of additive groups and F is a subset of G,
then for every R in G and m, #{(x_1..x_m) in (+-F)^m : sum x_i = R} = #{(y_1..y_m) in (+-f(F))^m :
sum y_i = f(R)}."

**AUD-5.** Not applicable to this disposition.

**AUD-6.** SO-ISO: see the family section.

## LEAD-ICP-lattice-ic-relation-construction

- file: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/ic-prime/LEAD-ICP-lattice-ic-relation-construction.yaml`
- disposition (as filed): `open_blocked`; last_reviewed 2026-10-24

next_action.step (verbatim):

> Deliver the admitted polynomial successor: one pipeline on an explicit prime cyclic subgroup (F43/F97/F101 fixtures plus the rank-two F25 negative control) that certifies density, valid roots/points, independent rank and complete cost for a relation, then the four-track review.

next_action.discriminates (verbatim):

> A certified pipeline with relation density above the matched decomposition rate opens a measurable lead; failure to certify density or rank on the toy fixtures closes these proposals.

next_action.blocked_by: `problems/lattice-index-calculus-relation-construction-not-demonstrated.md`

forecloses (verbatim): `lattice index calculus for elliptic curves`; `quaternion order volume as relation source`; `isogeny-adjoint pairing witness relations`; `Newton shift certificates for small-window decompositions`

**AUD-1.** Open lead; not applicable.

**AUD-2.** Not applicable to this disposition.

**AUD-3.** Not applicable to this disposition.

**AUD-4.** **The lead's own report reduces two of its three routes to standing obstructions.** Observed in
`car:research/lattice_index_calculus_20261015/report.md`:
- Lines ~28-31: "A same-field isogeny of degree d coprime to r preserves that subgroup order and q,
  hence k. ... it cannot lower k at those fixed inputs." Lines ~52-54: "Powering by invertible d
  permutes mu_r ... Selected-target variation alone is not an average descent improvement."
  -> Route 1 (IDEA-20261015-3afbc7, isogeny-adjoint pairing witnesses) is MOV with an unchanged
  embedding degree. It falls under SO-PAIR (LEAD-TRF-second-torsion-direction) and
  LEAD-TRF-mov-small-embedding-degree (closed_known) for prime-order curves with large k.
- Lines ~104-110: "substituting log(alpha^j F_i) = lambda^j log(F_i) makes every transformed copy of
  one augmented relation row a scalar multiple of the original."
  -> Route 2 (IDEA-20261015-1e8145, auxiliary coset chain) falls under SO-ENDO (End(G) = Z/N).
  Transformed rows add no rank. New rank comes only from new decompositions, which conservation
  governs.
- Lines ~73-78: "the formal relation lattice ... uses the unknown logarithms ... This is the missing
  interface in a direct NFS-lattice analogy."
- Route 3 (IDEA-20261015-9defe9, Newton-target shifts) is a small-root decomposition, the same
  mechanism as LEAD-ICP-coppersmith-smallroot-semaev.

Proposed change: `open_blocked` -> `closed_obstructed`.
- obstruction.kind: proof, citing SO-PAIR and SO-ENDO.
- scope: "prime-order subgroups of E(F_p) with embedding degree k > small; endomorphisms preserving
  G act as scalars".
- revisit_when: "a public lattice whose short vectors involve the target's coordinates, with relation
  density above the matched decomposition rate".
- Move route 3 into the coppersmith lead's next_action, and add it as `related`.
- The F43 (k = 2) fixtures remain instrument tests only.

**AUD-5.** Not applicable to this disposition.

**AUD-6.** SO-PAIR and SO-ENDO: see the family section.

## LEAD-ICP-prime-ic-constant-engineering

- file: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/ic-prime/LEAD-ICP-prime-ic-constant-engineering.yaml`
- disposition (as filed): `open_next_step`; last_reviewed 2026-10-24

next_action.step (verbatim):

> Put the eight Table B prime rows through the validation gate (replay certificate, validator report, matched rho with the section 5a band, VALIDATION.json), then run the unimplemented two-level target batching (step 1024 targets in lock-step so the R <- R + G inverse is amortised) as a paired ecbench arm against the current folded/walked m = 2 recipe at fp20-fp28.

next_action.discriminates (verbatim):

> Gate pass keeps the 5.5-13.5x distances as the validated baseline (fail demotes them); a paired ratio with the interval below 1 at every size is a measured constant improvement of the relation phase (~2x predicted); an interval spanning 1 closes the batching item.

best_measured (verbatim):

> fixed-window aP+bQ generator: full-solve reference/candidate 1.161 [1.127, 1.198], A/A 1.044, 54 toy prime solves (EV-ICPERF-92c130); planner: alternatives 1.36-1.60x worse than plan at w = 0

forecloses (verbatim): `batched inversion speeds up prime index calculus`; `Montgomery native arithmetic for the relation search`; `NFS-style relation filtering for the ECDLP matrix`; `blocked cache-aware pair table construction`; `automatic recipe planner for ic.pipeline`

**AUD-1.** Open lead; not applicable.

**AUD-2.** Not applicable to this disposition.

**AUD-3.** Not applicable to this disposition.

**AUD-4.** **Observed: the gate half of the step is done.**
- `crypto:docs/ic/LEADERBOARD.md` lines 49-56 show every prime Table B row `validated` (commit
  a8d8e3cd38). By the lead's own discriminates ("Gate pass keeps the 5.5-13.5x distances as the
  validated baseline"), the baseline is now validated: 6.34x (fp10, 9.7 bits) to 13.5x (fp24,
  23.4 bits).
- `car:ledger/decisions/DEC-20261023-122e32.yaml` accepted EXP-ICPERF-6c546e, run on held-out curve
  seeds 3/4/5. The claim `car:claims/ic-target-balanced-6c546e.json` gives a geometric-mean complete
  solve of 0.016255 s -> 0.014006 s, interval [1.1268, 1.1977], A/A 1.044, `rho_gap: unmeasured`.
- EXP-ICPERF-3065f9 stays preliminary / not_isolated (DEC-20261023-d70a08).
- The lead cites none of these three records.

**Would a theorem decide faster? Yes, for the counted unit.**
- In GAE, the batching gain is fixed by the operation-count identity. Montgomery's trick turns k
  inversions into 1 inversion plus 3(k-1) multiplications (KR-RHO-cb1c58).
- `crypto:docs/ic/calibration.json` pins a per-instance `ns_per_inversion` ratio (observed key; the
  values were not read here). The counted gain is therefore computable from the native counts
  without a run.
- Only the wall-time tier needs the paired arm.
- Matched rho can batch the same way (KR-RHO-cb1c58). A distance-to-rho statement therefore needs a
  batched reference.

Proposed next_action:
- (i) drop the gate step;
- (ii) compute the counted batching gain from calibration.json;
- (iii) run the paired arm against both the incumbent IC recipe and a batched-rho reference;
- add DEC-20261023-122e32, EXP-ICPERF-6c546e and DEC-20261023-d70a08 to ledger_refs.

**AUD-5.** Not applicable to this disposition.

**AUD-6.** See the family section.

## LEAD-ICP-representation-subset-sum

- file: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/ic-prime/LEAD-ICP-representation-subset-sum.yaml`
- disposition (as filed): `closed_obstructed`; last_reviewed 2026-10-24
- obstruction.kind: `theorem`

obstruction.statement (verbatim):

> The method uses only group operations and equality of encodings, so it is a generic algorithm and is bounded below by T >~ sqrt(N) (Shoup) and S*T^2 >~ N with advice; the filter step has no non-generic handle on E(F_p) (KR-RHO-5b1c0a records the same failure over F_{p^2}). Scope: any representation/filter variant on a prime-order group.

obstruction.revisit_when (verbatim):

> A filter predicate that reads non-generic coordinate structure with a measured bias.

forecloses (verbatim): `representation technique for ECDLP`; `subset-sum of scalar digits with many representations`; `knapsack-style filtering of partial group sums`

**AUD-1.** Trigger: "a filter predicate that reads non-generic coordinate structure with a measured bias".
H-PFDR-673eed is `proposed` and unrun (`car:ledger/.index/hypotheses.jsonl`), and nothing in the
delta bears on it. **Not fired.**

**AUD-2.** Over-foreclosure: a generic-group bound is applied beyond the generic class. The statement's scope
reads "any representation/filter variant on a prime-order group", yet its own revisit_when reopens
on "a filter predicate that reads non-generic coordinate structure". Shoup and CGK cover only
filters that use group operations and equality of encodings. `representation technique for ECDLP`
and `knapsack-style filtering of partial group sums` are unscoped. KR-RHO-5b1c0a is a cost result
for Delaplace-May over F_{p^2}, not a generic proof over F_p.

Proposed change: scope "... whose filter uses only group operations and equality of encodings",
and requalify both phrases the same way.

**AUD-3.** Closure kind is `theorem`; not applicable.

**AUD-4.** Not applicable to this disposition.

**AUD-5.** Not applicable to this disposition.

**AUD-6.** SO-GEN: see the family section.

## LEAD-ICP-residual-partial-relations

- file: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/ic-prime/LEAD-ICP-residual-partial-relations.yaml`
- disposition (as filed): `open_next_step`; last_reviewed 2026-10-24

next_action.step (verbatim):

> Add a single-large-prime residual table to the prime mitm m = 2 engine and run a paired complete-solve ladder 16-32 bits against the current folded/walked recipe with matched rho, counting table memory; fit the relation-phase exponent.

next_action.discriminates (verbatim):

> A fitted exponent near (1+beta)/2 with total S below the incumbent is a measured IC-baseline improvement (distance to rho shrinks but stays > 1 by S*T^2); an exponent unchanged, or a gain erased by linear algebra as in the F_{p^4} double-large-prime arm, closes the variant.

best_measured (verbatim):

> F_{p^4} analogue: double large primes cut LA exponent 0.495 -> 0.420 [0.405, 0.440] but whole solve 2.31x [2.10, 2.62] costlier at measured sizes; no prime-field measurement

forecloses (verbatim): `large prime variation for prime-field ECDLP index calculus`; `partial relations from residual x-coordinates`; `double large prime graph for Semaev relations`

**AUD-1.** Open lead; not applicable.

**AUD-2.** Not applicable to this disposition.

**AUD-3.** Not applicable to this disposition.

**AUD-4.** **The exponent is already fixed by derivation, so the experiment measures only constants.**

Derived (reviewer), checking H-PFDR-cb9606:
- Each target yields 2B residuals, so T targets yield 2BT residuals, with about (2BT)^2/(2N)
  collisions.
- B relations need T ~ sqrt(N/(2B)), so the work is 2BT ~ sqrt(2NB) = Theta(N^{(1+beta)/2}).
- With linear algebra ~B^2, the balance point is beta = 1/3, giving exponent 2/3.
- This compares with the current fitted 0.841 [0.646, 0.953] (FRONTIER fit v2, line 123).

The residual-collision step is a birthday search over uniformly distributed points, with B-fold
work per stored point. It is therefore dominated by rho for every beta > 0, so the variant can lower
the IC baseline but never reach rho.

Proposed change: add to discriminates "fit against the derived 2/3", and add `related:
[LEAD-ICB-large-prime-variants, LEAD-ICE-relation-graph-rank-large-prime]`. Disposition unchanged.

**AUD-5.** Not applicable to this disposition.

**AUD-6.** See the family section (SO-GEN).

## LEAD-ICP-retained-setup-online

- file: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/ic-prime/LEAD-ICP-retained-setup-online.yaml`
- disposition (as filed): `closed_dominated`; last_reviewed 2026-10-24
- obstruction.kind: `measured`

obstruction.statement (verbatim):

> The online ratios compared against rho with an empty distinguished-point table. Bernstein-Lange preprocessing rho with equal or smaller advice is 53-317x faster online than IC at n = 41/53/61, and precomputed-table rho wins every N83 matched pair; orbit-folded m = 2 Koblitz IC is BSGS on the quotient and sits on the BL r/P law. Scope: retained-advice, many-target accounting on these curves.

obstruction.revisit_when (verbatim):

> An IC online row that beats BL preprocessing rho at equal advice bytes and equal setup.

best_measured (verbatim):

> superseded: rho/IC 13.9x (n61) and 18.528x (n83) were against empty-table rho; BL at equal advice 53-317x faster online than IC

forecloses (verbatim): `retained factor base makes later targets cheaper than rho`; `dense root table online index calculus`; `multi-target index calculus beats rho per target`; `orbit-folded m = 2 index calculus online`

**AUD-1.** Trigger: "an IC online row that beats BL preprocessing rho at equal advice bytes and equal setup".
IDEA-20261018-4c28fc (co-measured BL vs IC at n = 73/83) is `proposed`, with no result.
**Not fired.**

**AUD-2.** - **Family and duplication:** the rows are Koblitz n61/n83 (binary). The row duplicates
  LEAD-ICB-retained-setup-online (ic-binary, closed_dominated, same BL 53-317x evidence).
- `multi-target index calculus beats rho per target` is unscoped, and no prime-field row was ever
  measured here.

Proposed change: set `dominated_by: LEAD-ICB-retained-setup-online` (or `related`), or rescope to
prime fields with "no prime-field measurement".

**AUD-3.** The exponent part can be proved; the constants stay measured.

Lean target candidate (a modeling lemma, with CGK as a hypothesis): "Let A be an online algorithm
that receives advice of S pairs (F_i, log F_i) and a target Q, and decides decompositions using
only group operations and equality of encodings. Then A is a preprocessing generic algorithm with
advice S * ceil(log2 N) bits. If A succeeds with probability eps within T queries, CGK gives
S T^2 >= c eps N."

Bernstein-Lange preprocessing rho attains this up to constants (KR-RHO-ea34b8). The 53-317x
constant-level domination remains `measured`.

**AUD-4.** Not applicable to this disposition.

**AUD-5.** Not applicable to this disposition.

**AUD-6.** SO-TABLE (preprocessing). See the family section.

## LEAD-ICP-self-pairing-prime-order

- file: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/ic-prime/LEAD-ICP-self-pairing-prime-order.yaml`
- disposition (as filed): `closed_obstructed`; last_reviewed 2026-10-24
- obstruction.kind: `theorem`

obstruction.statement (verbatim):

> On a cyclic group of prime order N every bilinear map is determined by h = b(P, P), so the space of self-pairings is one-dimensional, and Galois equivariance puts t_N(P, P) in mu_N intersected with the base field, trivial above embedding degree 1. Scope: prime-order subgroups of E(F_p) with embedding degree > 1.

obstruction.revisit_when (verbatim):

> Embedding degree 1 or non-cyclic N-torsion over the base field (a transfer-family case).

forecloses (verbatim): `self-pairing on a prime-order elliptic curve`; `distortion-free bilinear map recovers the discrete log`; `Tate pairing of P with itself`

**AUD-1.** Trigger: "embedding degree 1 or non-cyclic N-torsion over the base field". This is a curve-check
condition that does not apply to generic prime-order curves, and nothing in the delta bears on it.
**Not fired.**

**AUD-2.** Over-foreclosure: `distortion-free bilinear map recovers the discrete log`.
- The Galois-equivariance argument covers mu_N-valued Weil and Tate pairings.
- For an arbitrary bilinear map b: G x G -> H, the one-dimensionality lemma shows only that b is
  determined by h = b(P, P). It says nothing about whether such a b is computable or nontrivial.
  That is the general self-bilinear-map question.

Proposed change: requalify the phrase as "Weil/Tate (mu_N-valued) self-pairing ...".

**AUD-3.** Closure kind is `theorem`; not applicable.

**AUD-4.** Not applicable to this disposition.

**AUD-5.** Not applicable to this disposition.

**AUD-6.** SO-PAIR. MOV and Frey-Ruck take a small embedding degree as the hypothesis; that is the transfer
family (LEAD-TRF-mov-small-embedding-degree, closed_known).

## LEAD-ICP-xedni-function-field-sections

- file: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/ic-prime/LEAD-ICP-xedni-function-field-sections.yaml`
- disposition (as filed): `closed_obstructed`; last_reviewed 2026-10-24
- obstruction.kind: `proof`

obstruction.statement (verbatim):

> Exact closed form for the frozen family (deg b = 6, monic quadratic x): P_lift(p) = (1 - 2/p + p^-3)/(2p^3), limiting exponent alpha = 3 exactly (constant 1/2), checked against 596,268,874 enumerated slots with zero disagreements; a parameter count forces exactly four free prescribed sections and re-derives alpha = 3 from dimension (IDEA-20260805-d426f9). alpha = 3 is far above the 1/2 a viable relation source needs. The four coefficient-bound goals (max|coeff| = 1) measured an observable forced by norm-2 / E_8 lattice structure, so they neither support nor threaten the lead. Scope: rational elliptic surfaces with the frozen section shapes.

obstruction.revisit_when (verbatim):

> A surface family with a dimension surplus (more free section parameters than prescribed conditions, e.g. explicit high-rank K3 fibrations) whose measured lift exponent is below 1/2.

best_measured (verbatim):

> P_lift ~ p^-3 / 2 exactly (alpha = 3); max|coeff| = 1 at p in {7, 13, 19, 31} across four families (forced value)

forecloses (verbatim): `Mordell-Weil sections of an elliptic surface as factor base`; `function-field xedni lift probability`; `bounded relation coefficients among integral sections`; `specialise sections of a rational elliptic surface to get relations`

**AUD-1.** Trigger: "a surface family with a dimension surplus ... whose measured lift exponent is below 1/2".
No K3 or higher-rank surface measurement appears in the delta. **Not fired.**

**AUD-2.** Over-foreclosure. The proved scope is "rational elliptic surfaces with the frozen section shapes",
but `Mordell-Weil sections of an elliptic surface as factor base` is unscoped. It blocks the
"explicit high-rank K3 fibrations" that the lead's own revisit_when names.

Proposed change: requalify the phrase as "... of a rational elliptic surface (frozen section
shapes)". Also add `related: LEAD-TRF-function-field-xedni-lift` (the same SO-XEDNI pair).

**AUD-3.** Closure kind is `proof`; not applicable.

**AUD-4.** Not applicable to this disposition.

**AUD-5.** Not applicable to this disposition.

**AUD-6.** SO-XEDNI (alpha = 3, from the parameter count). Theories that take a dimension surplus as a
hypothesis: higher-rank elliptic surfaces (K3, and Shioda's Mordell-Weil lattices on surfaces of
higher arithmetic genus) and Ulmer's unbounded-rank families over F_p(t). There, free section
parameters exceed the prescribed conditions. LEAD-EXO-global-lift-height (open_next_step) is the
live measurement.

## LEAD-ICP-xline-symmetry-special-j

- file: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/ic-prime/LEAD-ICP-xline-symmetry-special-j.yaml`
- disposition (as filed): `open_unexamined`; last_reviewed 2026-10-24

next_action.step (verbatim):

> Compute degree-d Macaulay ranks of the digit or chained S_4 system at j = 0, j = 1728 and on the predicted degeneration points of the j-line against generic curves and against a coefficient-block vanishing null of the same support, at three toy primes (H-PFDR-df0127, H-PFDR-6b9f1a).

next_action.discriminates (verbatim):

> A rank drop beyond the block-vanishing null is an elliptic special locus worth a cost study (still only for special curves); no excess confirms that symmetry gives only the known constant factor (negation 2, j = 0 orbit 3) and closes the lead.

forecloses (verbatim): `automorphism folding of the factor base at j = 0`; `special j-invariant makes summation polynomials degenerate`; `Mobius symmetry of the x-line in decomposition`

**AUD-1.** Open lead; not applicable.

**AUD-2.** Not applicable to this disposition.

**AUD-3.** Not applicable to this disposition.

**AUD-4.** Not applicable to this disposition.

**AUD-5.** **Proposed closure for the folding sub-claim (closed_known).**
- Of the x-line Mobius symmetries, half are translations by 2-torsion points. These are absent on
  an odd-order E(F_p): H-PFDR-ebec07 says "half survives on a prime-order subgroup".
- The surviving half are automorphisms, which act as scalars on G (SO-ENDO).
- Their folding saving applies to rho as well (KR-RHO-0528e7, sqrt|Aut|) and to factor-base orbits
  (KR-IC-955fd6). There is no relative gain.

**First discriminating step for the rank-drop sub-claim.** This is the filed step: Macaulay ranks
at j = 0, j = 1728 and the H-PFDR-6b9f1a degeneration points, against a coefficient-block-vanishing
null, at three toy primes. Outcome map:
- A rank drop beyond the null becomes an arm of LEAD-STR-special-j-ic-semaev (open_next_step).
- No excess means closed_known (constant folding only).
- Any S_4 built with `harness/semaev.py` must use the repaired s4_expr (KN-OPEN-5b3a08;
  EXP-SEMAEV-6e9dcf `approved`).

**Overlap.** LEAD-STR-special-j-ic-semaev already covers "a Semaev degeneration divisor on the
j-line" and uses an "automorphism-orbit factor base and a sham-curve null of the same support
shape".

Proposed change: `closed_dominated` with `dominated_by: LEAD-STR-special-j-ic-semaev`, carrying the
Macaulay-rank step into that row. The cryptanalysis six-class GLV rho note
(`cax:docs/sixclass-20261024/assessment.md`) is rho-only, with a negative toy wall-time result,
and is not a trigger.

**AUD-6.** SO-ENDO: see the family section.

## AUD-6 (family level): obstructions in ic-prime as generative material

| obstruction (where it closes an ic-prime lead) | obstructing quantity | theory that takes it as a hypothesis |
|:--|:--|:--|
| SO-TABLE (generic-table-decomposition; retained-setup-online) | S*T^2 >~ r/\|Aut\| for generic advice | Structured GGM (CHW 2026/384): cost Omega(min(sqrt q, 1/delta)), with delta, the fraction of points on which structure is exploited, as the hypothesis. Converts the bound into a per-oracle measurable (IDEA-20261018-49fdf7). Cheon auxiliary input takes extra group structure as the hypothesis (SO-CHEON). |
| Conservation law KN-FIND-007 (algebraic-membership; full-width grid; coincidence-harvest) | mean yield C(B+m-1,m)/N per uniform target | Target preselection / importance sampling: attempt only targets predicted to decompose. The law bounds the mean over all targets, not over a cheaply selected subset; that is the open companion idea in coincidence-harvest. Second-moment (coverage/variance) theory: the break-even ladder IDEA-20261018-a0830c. |
| SO-ALGFB (algebraic-membership) | membership degree >= B/3 | Small roots (membership as a norm bound) and Weil descent (degree after restriction). See that lead's AUD-6. |
| SO-XEDNI (xedni-function-field) | alpha = 3 from the parameter count | K3 and higher-rank surfaces with a dimension surplus; LEAD-EXO-global-lift-height. |
| JKSST heights (char0-lifting) | point count (log B)^{r/2} | Function-field heights bounded by degree (leads back to SO-XEDNI); small-regulator high rank (unrealized). |
| SO-PAIR / Galois equivariance (self-pairing; lattice route 1) | embedding degree k | MOV / Frey-Ruck (transfer family, closed_known for generic curves). |
| SO-ENDO (lattice route 2; xline folding) | End(G) = Z/N | None found within the prime-order setting. |
| SO-ISO (isogeny-transported) | relation counts invariant under isomorphism | None found. The AUD-4 bijection lemma makes the invariance exact. |
| Gaudry exponent (extension-field-embedding) | p^{2-2/n} | None found. The AUD-3 lemma removes the subfield structure itself. |
| Genus floor 33 at n = 5 (gfp5-odd-char-cover, proposed) | genus of the x-line GHS cover | A Jacobian IC whose relation probability does not decay like 1/g!: none found. Non-x degree-2 maps (IDEA-20261024-d84f20) are a different cover, not a hypothesis on this one. |
| ANF size > rho budget (icperf-writability) | written monomial count | Implicit representations (chained S_3 circuits, straight-line programs); already in revisit_when. |
| SO-GEN (representation-subset-sum) | sqrt(r) generic lower bound | Any coordinate-reading filter is outside the model; the revisit condition. |


---

## Family: transfer

# Audit of the transfer family (LEAD-TRF-*), passes AUD-1..AUD-6

Reviewer: subagent audit, 2026-10-24. Read-only. 21 lead rows read in full from
`/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/transfer/`.

Current state consulted:
- the delta list `scratchpad/atlas/delta.txt`, in particular EV-CZLIFT-{376eee,712fe4,764f54,ad28f5,b6fe48,e9a7cf,ee9b23,f2a401};
  DEC-20261023-{039ddf,147f9f,26a6de,2e7447,36b4f0,488023,66af3b,6931ab,9de83a,fdc4af}; DEC-20261024-{23d64d,992998,e29f4c};
  KN-FIND-{3c7e19,7e2b94,c71e5d}; KN-OPEN-d3a6f0; IDEA-20261022-{e5b3a4,727d2e}; IDEA-20261024-{3c71a9,5f08bd,7be1c6,a29e53,b58e07,d84f20};
  problems/{ectd-arity3-panel-infrastructure-loss,nist-seed-selection-rule-unexplained}.md (crypto-autoresearcher);
  problems/k5-joux-vitse-trial-cost-and-fpk-ecbench.md and docs/ic/LEADERBOARD.md Table D (crypto)
- the correction CORR-20261024-63d682 of KR-IC-cd159a (`ledger/corrections/`)
- KRMAP.md and ATLAS.md (the overlapping rows LEAD-EXO-miller-pairing-cocycle, LEAD-EXO-global-lift-height,
  LEAD-EXO-padic-jet-canonical-lift, LEAD-EXO-elliptic-net-eds, LEAD-ICP-xedni-function-field-sections, LEAD-ICP-char0-lifting-xedni-smoothness)

Conventions: **Observation** = read from the cited file. **Interpretation** = my argument, conditional where marked.
"Recalled" = literature from memory, not re-read in this audit; such items are proposals to check, not evidence.
No experiment was run.

## Summary of proposed changes

| lead | pass | change | alters disposition |
|:--|:--|:--|:--|
| LEAD-TRF-global-lift-small-height | AUD-1/2/3 | closed_known -> closed_obstructed (counting bound, kind proof); best_measured false (1/3200 relation); KR basis now heuristic; rank threshold r~34 | yes |
| LEAD-TRF-padic-canonical-section | AUD-1/2 | 1/p clause false as worded; split off an open row for KN-OPEN-d3a6f0 digit-character Fourier mass | yes |
| LEAD-TRF-cover-catalog-jacobian-transfer | AUD-4 | every catalogue map is same-field -> closed by SO-COVER; blockers become tooling | yes |
| LEAD-TRF-miller-cocycle-nonhom-transfer | AUD-5 | duplicate of LEAD-EXO-miller-pairing-cocycle -> closed_dominated; equidistribution cannot close it if K2 holds | yes |
| LEAD-TRF-teske-secret-isogeny-trapdoor | AUD-4 | pigeonhole cap e/(e-1) on the occupancy meter -> IC-meter half closes at zero exponent | yes (split) |
| LEAD-TRF-small-genus-cover-general | AUD-1/2/5 | forecloses exceed x-line proof; split an open row for non-x-line degree-2 functions (IDEA-20261024-d84f20, a29e53) | yes (split) |
| LEAD-TRF-teske-trapdoor-fp6-weak-class | AUD-5 | first step from existing W/h(O_sel) census data; outcome -> disposition | no (step) |
| LEAD-TRF-odd-char-descent-smith-quartic | AUD-4 | Tian 2023 / IDEA-20261024-a29e53 second route; cheap Prop. 2/4 applicability test; Diem quartic cost marked VERIFY (recall only) | no |
| LEAD-TRF-jv-sieve-fp6-weak-class | AUD-2/4 | literature fixes sub-rho direction (KR-IC-ae532f); >1 at toy p is exhausted_at_scale, not closure | no |
| LEAD-TRF-same-field-genus-g-embedding | AUD-2 | kind theorem -> cost_model; revisit 'never' replaced | no |
| LEAD-TRF-jv-nagao-genus2-cover-decomp | AUD-1 | missing dominated_by field; validator does not enforce it | no |
| LEAD-TRF-cm-canonical-lift-heights | AUD-1/2/3 | basis changed; forecloses 'canonical lift for ECDLP' too broad; CM/Siegel theorem replaces cost model | no |
| LEAD-TRF-function-field-xedni-lift | AUD-2 | forecloses exceed random-sampling scope; twin scope conflict | no |
| LEAD-TRF-mov-small-embedding-degree | AUD-1 | revisit clause fired by known pairing-friendly literature; reword; map IDEA-20261022-e5b3a4 | no |
| LEAD-TRF-one-point-self-pairing, LEAD-TRF-second-torsion-direction | AUD-2 | BK hypothesis N not dividing p-1 omitted; k = 1 wording | no |
| LEAD-TRF-ghs-binary-composite | AUD-2 | forecloses need 'over F_{2^N}' qualifier | no |
| LEAD-TRF-curve-parameter-transfer-audits | AUD-1/2 | trigger met by known composite-N standards; 'NIST seed backdoor' too broad | no |
| LEAD-TRF-anomalous-padic-lift | AUD-1 | 'review pending' stale; cite EV-CZLIFT-712fe4, KN-FIND-3c7e19 | no |
| LEAD-TRF-pairing-target-field-recost | AUD-4 | no theorem shortcut; map IDEA-20261022-e5b3a4 | no |
| LEAD-TRF-prime-field-isogeny-to-weak | AUD-1 | not fired | no change |


## Per-lead audit

### LEAD-TRF-anomalous-padic-lift

*Smart / Satoh-Araki / Semaev p-adic lift for anomalous (trace one) curves*  
Disposition: `closed_known`; file `knowledge/leads/ecdlp/transfer/LEAD-TRF-anomalous-padic-lift.yaml`

obstruction.kind: `literature`  
obstruction.statement (verbatim):

> Works exactly on trace-one curves, which are an isogeny-class invariant (#E = p) and absent from generic or standard curves. The program reproduced it (Smart certificate p = 771853 in EXP-IT-001) and re-derived the canonical-lift degeneracy (CZLIFT runs, review pending).

obstruction.revisit_when (verbatim):

> never for generic curves; only as a positive control or for a curve with #E = p

forecloses: `anomalous curve attack`; `Smart attack`; `p-adic elliptic logarithm`; `Satoh-Araki-Semaev lift`; `trace one curves`

**AUD-1.** **Not fired.** The trigger asks for a curve with #E = p or use as a positive control; nothing in the delta supplies a new trace-one curve.
Observation (stale text, no disposition effect): the statement still says the canonical-lift degeneracy was re-derived "(CZLIFT runs, review pending)". The review has completed:
EV-CZLIFT-712fe4 (direction supports, strength replicated, toy; `ledger/evidence/EV-CZLIFT-712fe4.yaml`), DEC-20261023-147f9f (H-CZLIFT-889c9d approved -> supported, scoped),
KN-FIND-3c7e19 ("known theory ... prior art is Belding 2007, arXiv:math/0703906, section 7"; `knowledge/findings/KN-FIND-3c7e19.md`), and the 10^4..10^5 replication EV-CZLIFT-e9a7cf.
The run set of EXP-CZLIFT-7c8d73 (H-CZLIFT-d3dc4b, in this lead's ledger_refs) was ruled inadmissible (DEC-20261023-66af3b).
**Proposed change:** replace "(CZLIFT runs, review pending)" with "degeneracy rule v_p(j(E^) - j_can) >= 2e calibrated at toy tier (EV-CZLIFT-712fe4, KN-FIND-3c7e19; prior art Belding 2007 s.7); EXP-CZLIFT-7c8d73 inadmissible (DEC-20261023-66af3b)" and add those records to evidence. Also checked against crypto `docs/bounds/FRONTIER.md` (no transfer-mechanism rows: grep for MOV/pairing/embedding/anomal/lift/xedni/cover/descent/GHS/Joux/Smith/quartic returns nothing), `docs/ic/LEADERBOARD.md` (only Table D, JV, comparison withheld), and the orchestrator lists `atlas/obstr_debt.txt` and `atlas/obstr_unexamined.txt` (no TRF entries).

**AUD-2.** Scope (trace-one curves) matches what is proved. One phrase is wider than the scope: forecloses `p-adic elliptic logarithm` without the trace-one qualifier would also match non-anomalous formal-logarithm ideas, which are owned by LEAD-TRF-padic-canonical-section (and LEAD-EXO-padic-jet-canonical-lift). Proposed: `p-adic elliptic logarithm on trace-one curves`. No disposition effect.

**AUD-3.** Not applicable (disposition is not in this pass's scope). (kind literature). Side note, not returned: KN-FIND-3c7e19 labels the degeneracy rule 'derivation, not proved'; a formal statement would be: for ordinary E/F_p with #E(F_p)=p and an unramified lift E^/Z_p, v_p(z([p]P^)) >= 2 for all point lifts iff E^(Z/p^2) = (Z/p)^2 iff v_p(j(E^) - j_can) >= 2e. Not short in Lean (formal groups, Serre-Tate).

**AUD-4.** Not applicable (disposition is not in this pass's scope).

**AUD-5.** Not applicable (disposition is not in this pass's scope).

**AUD-6.** See the family table below.

### LEAD-TRF-cm-canonical-lift-heights

*Serre-Tate canonical lift with CM: does the CM order shrink the heights of lifted points enough for xedni to bite?*  
Disposition: `closed_obstructed`; file `knowledge/leads/ecdlp/transfer/LEAD-TRF-cm-canonical-lift-heights.yaml`

obstruction.kind: `cost_model`  
obstruction.statement (verbatim):

> Writing the canonical lift down needs the Hilbert/ring class polynomial of D = t^2 - 4p, of degree h(D) = |D|^{1/2+o(1)} ~ p^{1/2}, already the rho budget; for small |D| (cheap lifts) the height-coverage obstruction of LEAD-TRF-global-lift-small-height applies unchanged. Lane L9 was closed reject_scoped (DEC-20260810-2c7e3c); the red team confirmed the closure but replaced its load-bearing norm-form argument (DEC-20260810-3110d5). Scope: ordinary prime-field curves, canonical and CM lifts.

obstruction.revisit_when (verbatim):

> a CM lift whose field of definition has degree O(p^{epsilon}) and whose lifted points have height o(log N), or the cheap stage-0/1 checks of IDEA-20260815-93f483 return something unexpected

forecloses: `canonical lift for ECDLP`; `CM lifting`; `Serre-Tate lift heights`; `norm-form gap of the CM order`; `Hilbert class polynomial lift`

**AUD-1.** **Not fired by its own clauses; one cited basis changed.**
(i) Clause 2 ("the cheap stage-0/1 checks of IDEA-20260815-93f483 return something unexpected"): the experiments index lists EXP-CANL-c10053 (approved, "Closed-form n=2 P-S0-CANOLANE calibrator") and H-CANL-52c4b1 (specified); no evidence record for them appears in `ledger/.index/` -> no observed outcome, not fired.
(ii) The statement's second sentence leans on "the height-coverage obstruction of LEAD-TRF-global-lift-small-height ... unchanged". That obstruction was restated by DEC-20261024-23d64d (`h2_established_at_toy_tier.global_lift_counting`): "'Reductions cover E(F_p) like uniform points' is contradicted as stated ... The obstruction is a fixed-rank COUNTING bound, not uniformity". The known_result KR-IC-cd159a was corrected by CORR-20261024-63d682 (K2: status proven -> heuristic; K4: "'Lift to characteristic zero' and 'canonical lift for ECDLP' are not foreclosed by JKSST").
**Proposed change:** cite the counting bound (EV-CZLIFT-376eee D6/D7; DEC-20261024-23d64d) instead of "height-coverage obstruction ... unchanged", and drop KR-IC-cd159a as the support for the canonical-lift part (its own cost model does not need it). Also checked against crypto `docs/bounds/FRONTIER.md` (no transfer-mechanism rows: grep for MOV/pairing/embedding/anomal/lift/xedni/cover/descent/GHS/Joux/Smith/quartic returns nothing), `docs/ic/LEADERBOARD.md` (only Table D, JV, comparison withheld), and the orchestrator lists `atlas/obstr_debt.txt` and `atlas/obstr_unexamined.txt` (no TRF entries).

**AUD-2.** **Over-scoped forecloses.** Scope is "ordinary prime-field curves, canonical and CM lifts" for the xedni-height purpose. The phrase `canonical lift for ECDLP` blocks more than that: KN-OPEN-d3a6f0 (opened 2026-10-23, status open) asks whether p-adic digit characters of the torsion section s_tor on "the CM canonical model or an arbitrary integer lift" carry d, with an exponent-level criterion; CORR-20261024-63d682 K4 says the canonical-lift foreclosure must rest on the program's own derivations "each with its scope, and coordinate or digit encodings of the canonical section remain open (KN-OPEN-d3a6f0)". The cost-model argument (degree h(D) of the field of definition of a GLOBAL CM model) does not touch a p-adic computation on an integer lift, which needs no class polynomial.
**Proposed:** replace `canonical lift for ECDLP` with `canonical (CM) lift as a global height source for xedni`; add KN-OPEN-d3a6f0 to related.

**AUD-3.** **Yes, a short paper proof replaces the cost model (not short in Lean).** Informal theorem (lean_target candidate):
*Hypotheses:* E/F_p ordinary, O = End(E) an order of discriminant D in K = Q(sqrt(t^2-4p)); E~ any elliptic curve over a number field L with good reduction E at a prime above p and End(E~) = O (Deuring lift).
*Conclusion:* [Q(j(E~)) : Q] = h(O), and for every eps > 0 there is c(eps) > 0 with h(O) >= c(eps)|D|^{1/2-eps} (Siegel; ineffective). Hence any global CM lift has a field of definition of degree >= c(eps)|D|^{1/2-eps}; for |D| >> p^{1-delta} this is >= p^{1/2-delta-eps}.
*Quantifiers:* for all E, for all CM lifts E~. The small-|D| case (|t| near 2 sqrt p) is excluded and stays under the counting bound. Mathlib lacks CM theory and Siegel's theorem, so as a Lean target this is long; it is short on paper given CM theory.

**AUD-4.** Not applicable (disposition is not in this pass's scope).

**AUD-5.** Not applicable (disposition is not in this pass's scope).

**AUD-6.** See the family table below.

### LEAD-TRF-cover-catalog-jacobian-transfer

*Catalogued cover maps (1,940 prime quadratic pullbacks, 160 binary cubic pullbacks): executable pushforward and subgroup recovery*  
Disposition: `open_blocked`; file `knowledge/leads/ecdlp/transfer/LEAD-TRF-cover-catalog-jacobian-transfer.yaml`

next_action.step (verbatim):

> Build even-degree (two points at infinity) odd-characteristic Mumford arithmetic and the general binary norm phi_*: Jac(H) -> E, then certify subgroup order, kernel and image for each binding.

next_action.discriminates (verbatim):

> Executable maps let the catalog be screened end to end (most rows should land in the same-field obstruction); without them the 2,572 assessments stay classification-only.

blocked_by: crypto problems/prime-cover-balanced-jacobian-and-induced-maps-missing.md; problems/binary-cover-arbitrary-jacobian-norm-missing.md; problems/catalog-cover-subgroup-certificates-incomplete.md

forecloses: `cover catalog transfer`; `prime quadratic pullback cover`; `binary cubic pullback cover`; `Jacobian norm map pushforward`

**AUD-1.** Not applicable (disposition is not in this pass's scope). (open_blocked).

**AUD-2.** Not applicable (disposition is not in this pass's scope).

**AUD-3.** Not applicable (disposition is not in this pass's scope).

**AUD-4.** **A theorem decides the ECDLP value of the whole catalogue faster than the blocked engineering.**
Observation: the catalogue assessment says every map is same-field. `research/cover_transfer_assessment_20261013/README.md` (crypto) lines 112-115: "Binary cubic, same field | 165 | genus 3"; "Direct odd prime field | 14,272 | genus 2"; "Odd extension field | 1,324 | genus 2, degree 2 over the declared GF(p^k)"; lines 195-198: the odd-characteristic cover is over "the declared prime field or polynomial-basis extension field; it is not a descent to a proper subfield"; line 92: the primary theorem (Xarles v1, Cor. 3) has hypothesis "same base field".
Interpretation (conditional on the known-algorithm cost of genus-g index calculus): for every binding H -> E over the same field F_q, Jac(H) ~ E x A with #Jac(H)(F_q) = N * #A(F_q), #A = Theta(q^{g-1}), and the best known genus-2/3 index calculus costs O~(q^{2-2/g}) >= q > q^{1/2} (rho on E). That is exactly LEAD-TRF-same-field-genus-g-embedding's obstruction (SO-COVER). Executable pushforward and subgroup certificates would make the transfer runnable but cannot change its cost class.
**Proposed change:** open_blocked -> closed_obstructed (kind cost_model, statement: same-field covers, SO-COVER; revisit_when: a catalogue row whose cover lives over a proper subfield of E's field, or a genus-g DLP algorithm with exponent below 1/2 in q), or closed_dominated with dominated_by LEAD-TRF-same-field-genus-g-embedding. Keep the three problem files as tooling problems, not lead blockers.
Outcome map: a row with descent to a proper subfield found -> reopen that row as open_next_step; none -> closure stands.

**AUD-5.** Not applicable (disposition is not in this pass's scope).

**AUD-6.** See the family table below.

### LEAD-TRF-curve-parameter-transfer-audits

*Transfer-safety audits of deployed curves: embedding degree, anomaly, twist, subfield/descent, seed provenance*  
Disposition: `closed_known`; file `knowledge/leads/ecdlp/transfer/LEAD-TRF-curve-parameter-transfer-audits.yaml`

obstruction.kind: `literature`  
obstruction.statement (verbatim):

> SafeCurves-type checks are standard and the deployed prime curves pass MOV/anomalous/descent checks; the NIST seed reproduction (2026-10-16) is provenance and changes no ECDLP. Remaining work is certification tooling (large-field certificates), not an attack.

obstruction.revisit_when (verbatim):

> an audit finds a deployed curve with small k, trace one, or a composite-degree binary field in use

forecloses: `embedding degree audit of standard curves`; `NIST seed backdoor`; `SafeCurves transfer checks`; `anomalous standard curve`

**AUD-1.** **Not fired.** New evidence in `problems/nist-seed-selection-rule-unexplained.md` (crypto-autoresearcher, in delta) lists an "Exact embedding-degree comparison: certified ord_n(p) for all 19 comparable candidates" and "Quadratic-twist pairing screen: all 25 large twist factors have embedding degree above 1,000 within the bounded test" -> no small-k hit. IDEA-20261022-727d2e (integer-specialness census) states it audits "companion F_p^* and F_{p^2}^* DLP risk and hidden-structure detection, NOT ECDLP" -> not a trigger.
Observation (trigger mis-specified): the clause "a composite-degree binary field in use" is already met by literature-known standards listed in LEAD-TRF-ghs-binary-composite ("Composite-N standards (Oakley Groups 3/4, ANSI c2pnb*)"). **Proposed:** add "outside the composite-N standards owned by LEAD-TRF-ghs-binary-composite" to revisit_when; map IDEA-20261022-727d2e to this lead in coverage.tsv (it is not in coverage.tsv). Also checked against crypto `docs/bounds/FRONTIER.md` (no transfer-mechanism rows: grep for MOV/pairing/embedding/anomal/lift/xedni/cover/descent/GHS/Joux/Smith/quartic returns nothing), `docs/ic/LEADERBOARD.md` (only Table D, JV, comparison withheld), and the orchestrator lists `atlas/obstr_debt.txt` and `atlas/obstr_unexamined.txt` (no TRF entries).

**AUD-2.** **Over-scoped forecloses.** `NIST seed backdoor` is foreclosed while the statement closes only MOV/anomalous/descent checks and says the seed reproduction "changes no ECDLP". The program's own problem record `problems/nist-seed-selection-rule-unexplained.md` is Status `open`, and LEAD-TRF-teske-secret-isogeny-trapdoor (open_next_step) owns "secret isogeny to a weak curve as a backdoor". Proposed: `NIST seed backdoor detectable by MOV, anomaly or descent checks`.

**AUD-3.** Not applicable (disposition is not in this pass's scope). (kind literature).

**AUD-4.** Not applicable (disposition is not in this pass's scope).

**AUD-5.** Not applicable (disposition is not in this pass's scope).

**AUD-6.** See the family table below.

### LEAD-TRF-function-field-xedni-lift

*Function-field xedni: lift relations to sections of elliptic surfaces y^2 = x^3 + a(t)x + b(t) over F_p(t)*  
Disposition: `closed_obstructed`; file `knowledge/leads/ecdlp/transfer/LEAD-TRF-function-field-xedni-lift.yaml`

obstruction.kind: `proof`  
obstruction.statement (verbatim):

> Exact closed form for the frozen family: P_lift(p) = (1 - 2/p + p^{-3})/(2 p^3), so alpha = 3 (finite-size exponents 2.986-2.997); relation coefficients stay at max|coeff| = 1 but later audits show that value is forced by the lattice (norm-2 vectors at support 3), so the coefficient census carried no discriminating power. Scope: deg b <= 10, deg a <= 4, sections deg x <= 3, p <= 31.

obstruction.revisit_when (verbatim):

> a section shape with prescribed-fibre lift probability exponent below 1/2, derived before measurement

forecloses: `function field xedni`; `elliptic surface section lifting`; `Mordell-Weil sections over F_p(t)`; `rational elliptic surface relation source`; `section height relation coefficients`

**AUD-1.** **Not fired.** No section shape with derived exponent below 1/2 appears in the delta. Related: LEAD-EXO-global-lift-height (open_next_step) runs IDEA-20261009-581f5d (also in this lead's ledger_refs); its stage-0 instrument EXP-ECDLP-f34097 and the metadata reproduction EXP-ECDLP-ee406e were approved (DEC-20261018-ca4056) and no evidence record is indexed -> no observed outcome. Also checked against crypto `docs/bounds/FRONTIER.md` (no transfer-mechanism rows: grep for MOV/pairing/embedding/anomal/lift/xedni/cover/descent/GHS/Joux/Smith/quartic returns nothing), `docs/ic/LEADERBOARD.md` (only Table D, JV, comparison withheld), and the orchestrator lists `atlas/obstr_debt.txt` and `atlas/obstr_unexamined.txt` (no TRF entries).

**AUD-2.** **Over-scoped forecloses; scope text conflicts with its twin.**
(i) What is proved: an exact closed form of P_lift, the probability that a target fibre point lies on a low-degree section of a random surface of the frozen family (random sampling). The forecloses `elliptic surface section lifting`, `Mordell-Weil sections over F_p(t)` and `rational elliptic surface relation source` also block the solve variant (find a surface and section through a prescribed point by solving), which LEAD-EXO-global-lift-height keeps open ("closes the function-field variant" only if T_section > p^{1/2} poly(log p)).
(ii) The twin LEAD-ICP-xedni-function-field-sections closes the same H-XEDN-001 result with scope "deg b = 6, monic quadratic x" and a dimension-count reason ("a parameter count forces exactly four free prescribed sections and re-derives alpha = 3 from dimension (IDEA-20260805-d426f9)"), with revisit "a surface family with a dimension surplus". This lead states scope "deg b <= 10, deg a <= 4, sections deg x <= 3, p <= 31".
Interpretation: the dimension count (at most four prescribable sections against Mordell-Weil rank <= 8, so no forced dependency) is what blocks the solve variant; alpha = 3 alone does not.
**Proposed:** narrow the three phrases to `random low-degree sections of the frozen rational-surface family`; cite the dimension count as the obstruction to the solve variant; make the scope text agree with LEAD-ICP-xedni-function-field-sections and list each as related; align LEAD-EXO-global-lift-height's discriminates with the dimension count.

**AUD-3.** Not applicable (disposition is not in this pass's scope). (kind proof).

**AUD-4.** Not applicable (disposition is not in this pass's scope).

**AUD-5.** Not applicable (disposition is not in this pass's scope).

**AUD-6.** See the family table below.

### LEAD-TRF-ghs-binary-composite

*GHS / generalized GHS Weil descent (with Galbraith-Hess-Smart isogeny walks) for curves over F_{2^N}, N composite*  
Disposition: `closed_known`; file `knowledge/leads/ecdlp/transfer/LEAD-TRF-ghs-binary-composite.yaml`

obstruction.kind: `literature`  
obstruction.statement (verbatim):

> Menezes-Teske-Weng / Menezes-Teske: N prime is not weak; all NIST/SEC binary curves use prime N, and subfield curves are not weakened. Composite-N standards (Oakley Groups 3/4, ANSI c2pnb*) are known literature cases; the program re-derived magic numbers and genera exactly (jacobian_transfer_scan) and densities on toy fields, but never ran a higher-genus GHS solve.

obstruction.revisit_when (verbatim):

> an end-to-end measured row is wanted for Oakley Group 3/4 or c2pnb176w1 (needs a genus-15 / genus-127 Jacobian IC solver)

forecloses: `GHS attack`; `Weil descent to a hyperelliptic Jacobian`; `isogeny to a GHS-weak curve`; `magic number of a binary curve`; `Oakley group curves`; `c2pnb curves`

**AUD-1.** **Not fired.** The trigger is a work request (a genus-15/127 Jacobian IC solver for a measured row). `research/ghs_curve_comparison_20261009/RESULT.md` (crypto) still records the higher-genus GHS solver as not implemented. Delta items about prime n (GOAL-PEXT-4a1d6b, EXP-PEXT-212d5c approved with a char-2 arm; IDEA-20261024-5f08bd's Hess/Mersenne comparison "formula-level") are genus censuses without cost, and do not touch composite N. Also checked against crypto `docs/bounds/FRONTIER.md` (no transfer-mechanism rows: grep for MOV/pairing/embedding/anomal/lift/xedni/cover/descent/GHS/Joux/Smith/quartic returns nothing), `docs/ic/LEADERBOARD.md` (only Table D, JV, comparison withheld), and the orchestrator lists `atlas/obstr_debt.txt` and `atlas/obstr_unexamined.txt` (no TRF entries).

**AUD-2.** **Over-scoped forecloses.** The statement's scope is F_{2^N}. The phrases `GHS attack`, `Weil descent to a hyperelliptic Jacobian` and `isogeny to a GHS-weak curve` carry no field qualifier, so they would block odd-characteristic and F_{p^k} descent work that is open elsewhere: LEAD-TRF-jv-sieve-fp6-weak-class (open_next_step), LEAD-TRF-odd-char-descent-smith-quartic (open_blocked), and the active GOAL-PEXT-4a1d6b (DEC-20261024-e29f4c). Proposed: suffix each with `over F_{2^N}, N composite`.

**AUD-3.** Not applicable (disposition is not in this pass's scope). (kind literature).

**AUD-4.** Not applicable (disposition is not in this pass's scope).

**AUD-5.** Not applicable (disposition is not in this pass's scope).

**AUD-6.** See the family table below.

### LEAD-TRF-global-lift-small-height

*Global lifts to E(Q) or E(K) with small canonical height (xedni, SNFS / cyclotomic / Solinas number fields, rational 2-torsion lifts)*  
Disposition: `closed_known`; file `knowledge/leads/ecdlp/transfer/LEAD-TRF-global-lift-small-height.yaml`

obstruction.kind: `literature`  
obstruction.statement (verbatim):

> Jacobson-Koblitz-Silverman-Stein-Teske: lifted points have canonical height of order log of the group size per relation and the number of points of height <= B grows like (log B)^{r/2}, so covering a target residue mod p needs exponentially large height; the program re-measured uniform reduction of small points on rank 0-11 curves and over Q(2^{1/3}) (CZLIFT, review pending). Scope: lifts to E(Q) and E(K) for bounded-degree K, any rank reachable by known constructions.

obstruction.revisit_when (verbatim):

> a lift family with rank growing like log p and provably small regulator, or an exact dependent-lift finder (RQ-XEDN-3bfe2e) that hits a prescribed residue faster than p^{1/2}

forecloses: `xedni calculus`; `lift to characteristic zero`; `Mordell-Weil relation of lifted points`; `small height global lift`; `SNFS number field lift of an elliptic curve`; `high rank lift`

**AUD-1.** **Fired: the obstruction's two load-bearing claims were revised by records in the delta.** The revisit_when clauses themselves (rank ~ log p lift family; an exact dependent-lift finder) did not fire.
(a) "the program re-measured uniform reduction of small points" -> contradicted: EV-CZLIFT-376eee (`direction: weakens`; "C2 (reductions behave like independent uniform points, HEUR-CZLIFT-UNIFORM) contradicts as stated"); DEC-20261023-26a6de; DEC-20261024-23d64d global_lift_counting: "The obstruction is a fixed-rank COUNTING bound, not uniformity: reduction is a homomorphism, so half coverage of E(F_p) needs at least N_p/2 distinct global points (Omega(p) against O(sqrt p) for rho), and any spread saves at most a factor 2 ln 2."
(b) The literature row is weaker than quoted: CORR-20261024-63d682 K1/K2: JKSST Theorem 4.1 holds "under ... Lang's lower-bound conjecture for the canonical height and Lemma 4.1's assumption", "vacuous at small p", status proven -> heuristic.
(c) best_measured "xedni dependence never seen within relation bound 6" is false: EV-CZLIFT-ee9b23: "found 1 relation in 3200 valid trials ... The one relation is the tangent relation 2 P~1 + P~2 = O at p = 101, r = 2" (DEC-20261023-488023, H-CZLIFT-cb95b8 weakened).
(d) Rank threshold now quantified: DEC-20261024-23d64d not_established: "Lifts whose rank grows like log p / log log p (the bound weakens once r >~ 34 at 2^128 and 60 at 2^256)".
**Proposed change:** disposition closed_known -> closed_obstructed; obstruction.kind literature -> proof (coverage part: pigeonhole counting bound, exact; asymptotic height form conditional on T1-T4 of EV-CZLIFT-376eee); keep JKSST for xedni proper, stated as conditional on Lang's conjecture; best_measured -> "1/3200 relations at bound 6 (tangent coincidence, p = 101); uniform reduction contradicted (coverage medians 1.0330/1.0333 vs uniform bands <= 1.0041)"; revisit_when -> "a lift family of rank >= ~34 at 2^128 (>= ~60 at 2^256) with bounded c_E and regulator (DEC-20261024-23d64d), or an exact dependent-lift finder (RQ-XEDN-3bfe2e) hitting a prescribed residue faster than p^{1/2}".
**Caveats on the relabel.** "Proof" covers only the exact pigeonhole coverage bound. The beyond-toy height form stays conditional on T1-T4 (EV-CZLIFT-376eee). Xedni proper stays literature-conditional (CORR-20261024-63d682 K2). DEC-20261024-23d64d records `rq_closure.can_close: false`, and README rule 2 says the atlas changes no research state. So the relabel restates the obstruction's basis; it does not close RQ-CZLIFT-b9f765. Also checked against crypto `docs/bounds/FRONTIER.md` (no transfer-mechanism rows: grep for MOV/pairing/embedding/anomal/lift/xedni/cover/descent/GHS/Joux/Smith/quartic returns nothing), `docs/ic/LEADERBOARD.md` (only Table D, JV, comparison withheld), and the orchestrator lists `atlas/obstr_debt.txt` and `atlas/obstr_unexamined.txt` (no TRF entries).

**AUD-2.** **Over-scoped.** Statement scope "lifts to E(Q) and E(K) for bounded-degree K, any rank reachable by known constructions". Evidence: E(K) clause C5 untested and the degree-3 run set EXP-CZLIFT-8c50ea inadmissible (DEC-20261023-fdc4af; DEC-20261024-23d64d: "E(K) for any K: C5 untested"). The counting bound holds at fixed rank and weakens at high rank, yet forecloses `high rank lift` is listed. Proposed: drop `high rank lift` (or qualify `fixed-rank`), and restrict `SNFS number field lift of an elliptic curve` to "coverage by reductions of a fixed E(K)" until a valid E(K) run set exists.

**AUD-3.** (Kind is literature, but the coverage part is now carried by the program's own counting argument; a Lean target replaces it.)
**lean_target (short):** Let G be a finite set of size N (the group E(F_p)), S a finite set, red : S -> G any function (reduction of enumerated global points). Then #(image red) <= #S; hence for a uniformly random target t in G, Pr[exists s, red s = t] <= #S / N, and half coverage forces #S >= N/2. In Lean: `(Finset.univ.image red).card <= Finset.univ.card` (`Finset.card_image_le`), with the probability statement as a ratio of cards. The companion ceiling of KN-TECH-5c41e7 (distinct-residue coverage ratio <= min(x,1)/(1 - e^{-x})) is the same pigeonhole fact against a Poisson baseline.

**AUD-4.** Not applicable (disposition is not in this pass's scope).

**AUD-5.** Not applicable (disposition is not in this pass's scope).

**AUD-6.** See the family table below.

### LEAD-TRF-jv-nagao-genus2-cover-decomp

*Nagao decomposition on a genus-2 cover of E(F_{p^6}) (examples/jv_cover.rs), with F4 and sparse-FGLM engineering*  
Disposition: `closed_dominated`; file `knowledge/leads/ecdlp/transfer/LEAD-TRF-jv-nagao-genus2-cover-decomp.yaml`

obstruction.kind: `measured`  
obstruction.statement (verbatim):

> On the same weak-class instances the Nagao route sits at S/rho 151-293 after sparse FGLM (p <= 251) while the JV sieve (LEAD-TRF-jv-sieve-fp6-weak-class) was historically below rho; per-test engineering (1.28x) cannot close a two-order gap, and only a large-prime variation (lead L6 of ic_cover_leads) could change the exponent.

obstruction.revisit_when (verbatim):

> the sieve row fails validation, or a large-prime variation for the Nagao route is built

forecloses: `Nagao decomposition on a genus 2 cover`; `sparse FGLM for jv_cover`; `F5 signatures for cover decomposition`

**AUD-1.** **Not fired.** The sieve row has not "failed validation": LEADERBOARD Table D (`docs/ic/LEADERBOARD.md` line 84ff, crypto) says "Comparison withheld", with positive-control and A/A acceptance unresolved. No large-prime variation for the Nagao route is reported.
Observation: the row is closed_dominated but carries no `dominated_by` field (grep of the YAML finds none). `tools/lead_atlas.py` lines 222-226 only check dominated_by when present, so --check passes. The dominating row is itself withheld.
**Proposed change:** add `dominated_by: LEAD-TRF-jv-sieve-fp6-weak-class`; state in the obstruction that independently of the sieve the measured S/rho 151-293 (> 1) at p <= 251 already places the route above rho at reachable sizes; and make the validator require dominated_by for closed_dominated (a tooling change outside the atlas). Also checked against crypto `docs/bounds/FRONTIER.md` (no transfer-mechanism rows: grep for MOV/pairing/embedding/anomal/lift/xedni/cover/descent/GHS/Joux/Smith/quartic returns nothing), `docs/ic/LEADERBOARD.md` (only Table D, JV, comparison withheld), and the orchestrator lists `atlas/obstr_debt.txt` and `atlas/obstr_unexamined.txt` (no TRF entries).

**AUD-2.** The measured gap is used as dominance only (not asymptotic closure); the revisit names the one mechanism (large-prime variation) that could change the exponent. Scope matches. No change beyond AUD-1.

**AUD-3.** Kind measured. No short proof replaces it: the dominance compares two measured constants and two different decomposition exponents on a non-prime-order weak class; no lower bound on F4 trial cost exists (the k = 5 problem `problems/k5-joux-vitse-trial-cost-and-fpk-ecbench.md` says "No lower bound on C_trial is proved"). No lean_target.

**AUD-4.** Not applicable (disposition is not in this pass's scope).

**AUD-5.** Not applicable (disposition is not in this pass's scope).

**AUD-6.** See the family table below.

### LEAD-TRF-jv-sieve-fp6-weak-class

*Joux-Vitse cover-and-decomposition sieve on the weak class of E(F_{p^6}) (genus-3 cover), with the isogeny walk into the class*  
Disposition: `open_next_step`; file `knowledge/leads/ecdlp/transfer/LEAD-TRF-jv-sieve-fp6-weak-class.yaml`

next_action.step (verbatim):

> Freeze numeric acceptance tolerances for the positive control (R0 S) and the rho A/A rule, then re-run the paired sieve vs strong-rho panel at p in {1009, 1511, 1823} with the corrected hash accounting, the F4/linear-algebra additions emitted, and the isogeny walk into the weak class charged, producing VALIDATION.json.

next_action.discriminates (verbatim):

> Ratios below one across the 0/0.1/1 GAE band with controls accepted would make this the program's first validated sub-rho transfer row (weak class only, not prime order); ratios that move above one once the walk and hashes are charged would close it as an accounting artefact.

forecloses: `Joux-Vitse cover and decomposition`; `weak class over F_{p^6}`; `genus 3 cover sieve`; `isogeny walk into the JV weak class`

**AUD-1.** Not applicable (disposition is not in this pass's scope). (open_next_step).

**AUD-2.** The discriminates clause says ratios above one "once the walk and hashes are charged would close it as an accounting artefact". That would use a measured null at toy p (log2 l <= 63) as a closure of an asymptotic question. Proposed: map that outcome to exhausted_at_scale with the measured crossover, not to a closure.

**AUD-3.** Not applicable (disposition is not in this pass's scope).

**AUD-4.** **Partly: literature already fixes the asymptotic direction; the queued experiment only decides constants and accounting.**
Interpretation (exponent from KR-IC-a4dd54, `knowledge/frontiers/ecdlp/index-calculus/KR-IC-a4dd54.yaml`: "index calculus with double large primes costs O~(q^{2-2/g})"): the weak class maps the DLP into a genus-3 hyperelliptic Jacobian over F_{p^2}; double-large-prime index calculus there costs O~(q^{4/3}) with q = p^2, i.e. p^{8/3}, while rho on the prime l | #E(F_{p^6}) costs about p^3 / sqrt(cofactor). The asymptotic ratio is about p^{-1/3} * sqrt(cofactor), so sub-rho on this class is the literature expectation (KR-IC-ae532f: Joux-Vitse solved a 149-bit subgroup of E(F_{p^6})). Hence "the program's first validated sub-rho transfer row" would be a reproduction of known literature on a non-prime-order class.
**Proposed change:** add KR-IC-ae532f to known_results; outcome map: validated ratio < 1 and trending like p^{-1/3} -> closed_known (reproduced, weak class only); ratio > 1 at toy p -> exhausted_at_scale with crossover p*, not closed. Also note the plane-quartic route (LEAD-TRF-odd-char-descent-smith-quartic AUD-4) would cut the destination cost to O~(q) on the subset where Smith's isogeny applies.

**AUD-5.** Not applicable (disposition is not in this pass's scope).

**AUD-6.** See the family table below.

### LEAD-TRF-miller-cocycle-nonhom-transfer

*Non-homomorphic transfers into F_p^* when the pairing is trivial: Miller-cocycle primitive U, zeta-defect, generalized Jacobians*  
Disposition: `open_unexamined`; file `knowledge/leads/ecdlp/transfer/LEAD-TRF-miller-cocycle-nonhom-transfer.yaml`

next_action.step (verbatim):

> Test H1 of IDEA-20261017-e3a6f1 at toy size: equidistribution of ell(k) = log_g U(kP) in Z/(p-1), Smart-ratio success and correlation with characters of Z/N, on special and matched random p, with planted-structure positive control.

next_action.discriminates (verbatim):

> Equidistribution at the 1/p rate closes the lead (a non-homomorphic map of this kind is a hash); any character correlation would be the first one-point transfer signal and needs the full cost accounting.

forecloses: `Miller function transfer`; `generalized Jacobian transfer`; `unreduced Tate pairing value`; `Miller S-unit descent`; `zeta defect quasi-homomorphism`

**AUD-1.** Not applicable (disposition is not in this pass's scope). (open_unexamined).

**AUD-2.** Not applicable (disposition is not in this pass's scope).

**AUD-3.** Not applicable (disposition is not in this pass's scope).

**AUD-4.** Not applicable (disposition is not in this pass's scope).

**AUD-5.** **Proposed closure: closed_dominated, dominated_by LEAD-EXO-miller-pairing-cocycle (README rule 3, absorbed lead).**
Observation: LEAD-EXO-miller-pairing-cocycle (`knowledge/leads/ecdlp/exotic/`, open_next_step) rests on the same IDEA-20261017-e3a6f1 and IDEA-20261009-c8433d and has a sharper step: "Verify IDEA-20261017-e3a6f1 claims K1 ... and K2 (U(kP)=c*r_k*C^(k/N), r_k=psi_{k-1}/psi_k) exactly ... If K2 holds and r_k needs k (division-polynomial values), the primitive collapses into the closed elliptic-net lead".
Interpretation (conditional on K2, which IDEA-20261017-e3a6f1 marks "unreviewed"): taking discrete logs, ell(k) = log_g U(kP) = log_g c + log_g r_k + k * (log_g C / N) mod (p-1), N invertible mod p-1. So ell is a LINEAR function of k masked by log_g r_k. An equidistribution or no-character-correlation result for ell is then exactly what a masked linear function produces, so this lead's discriminates clause ("Equidistribution at the 1/p rate closes the lead") would turn an uncontrolled null into a closure. The decisive object is r_k: recovering k from U(kP) is equivalent to evaluating the EDS ratio psi_{k-1}(P)/psi_k(P) from (P, kP), which is the elliptic-net residue question of LEAD-EXO-elliptic-net-eds (SO-NET).
First discriminating step (shared with the EXO lead): exact K1/K2 identity check on >= 20 toy curves with gcd(N, p-1) = 1, plus an N | p-1 control. Outcomes: K2 holds on every k -> closed_obstructed, obstruction = reduction to the EDS residue (quote LEAD-EXO-elliptic-net-eds statement); K2 fails while K1 holds -> run the H1 spectral test with the planted N | p-1 control as the second arm of the EXO lead; K1 fails -> withdraw the record (IDEA's own falsification condition).

**AUD-6.** See the family table below.

### LEAD-TRF-mov-small-embedding-degree

*MOV / Frey-Rueck pairing transfer of the ECDLP to F_{p^k}^* for small embedding degree k*  
Disposition: `closed_known`; file `knowledge/leads/ecdlp/transfer/LEAD-TRF-mov-small-embedding-degree.yaml`

obstruction.kind: `literature`  
obstruction.statement (verbatim):

> k = ord_N(p) is a function of (N, p) alone, hence an isogeny-class invariant (no walk lowers it), and for random prime-field curves it is of size ~N (Balasubramanian-Koblitz); the transfer is a curve check, not an ECDLP algorithm. Scope: ordinary and supersingular curves over any finite field; the target-field cost is a separate lead (LEAD-TRF-pairing-target-field-recost).

obstruction.revisit_when (verbatim):

> a deployed curve is found with small k (an audit hit), or a construction yields a subgroup of prime order N with k << log-size where finite-field DLP beats rho

forecloses: `MOV reduction`; `Frey-Rueck Tate pairing transfer`; `small embedding degree attack`; `pairing transfer to finite field`; `CM curves with low embedding degree`; `walk the isogeny class to lower the embedding degree`

**AUD-1.** **Second clause fired by known literature; the trigger is mis-specified.** revisit_when clause "a construction yields a subgroup of prime order N with k << log-size where finite-field DLP beats rho" is met by pairing-friendly families: IDEA-20261022-e5b3a4 (proposed 2026-10-22, in delta) states "[derived, unverified] BN-254: transfer < rho across the band" and uses "the BN row reproduces 99.69 bits" as its positive control. The lead's own scope already sends target-field cost to LEAD-TRF-pairing-target-field-recost. First clause ("a deployed curve ... with small k") not fired (NIST seed twist and exact embedding-degree screens in `problems/nist-seed-selection-rule-unexplained.md` found none).
**Proposed change:** revisit_when -> "a deployed curve with small k outside the pairing-friendly families (LEAD-TRF-pairing-target-field-recost owns those), or a non-CM construction with k << log N"; map IDEA-20261022-e5b3a4 to LEAD-TRF-pairing-target-field-recost (it is absent from coverage.tsv). Also checked against crypto `docs/bounds/FRONTIER.md` (no transfer-mechanism rows: grep for MOV/pairing/embedding/anomal/lift/xedni/cover/descent/GHS/Joux/Smith/quartic returns nothing), `docs/ic/LEADERBOARD.md` (only Table D, JV, comparison withheld), and the orchestrator lists `atlas/obstr_debt.txt` and `atlas/obstr_unexamined.txt` (no TRF entries).

**AUD-2.** Scope matches. Wording shared with LEAD-TRF-one-point-self-pairing: Balasubramanian-Koblitz needs the hypothesis N not dividing p-1 (see that lead's AUD-2). No disposition effect.

**AUD-3.** Not applicable (disposition is not in this pass's scope). (kind literature).

**AUD-4.** Not applicable (disposition is not in this pass's scope).

**AUD-5.** Not applicable (disposition is not in this pass's scope).

**AUD-6.** See the family table below.

### LEAD-TRF-odd-char-descent-smith-quartic

*Odd-characteristic Weil descent onto genus 3, then Smith's isogeny to a plane quartic and Diem's q^{4/3} attack*  
Disposition: `open_blocked`; file `knowledge/leads/ecdlp/transfer/LEAD-TRF-odd-char-descent-smith-quartic.yaml`

next_action.step (verbatim):

> Implement Smith's Props. 2 and 4 / the trigonal construction and test F_q-rationality and non-degeneracy on the odd-characteristic genus-3 descents already enumerated.

next_action.discriminates (verbatim):

> Rational, non-degenerate Smith images give an executable q^{4/3} route on that class (then measure against matched rho with the isogeny walk charged); failure closes the pipeline. The characteristic-2 version is already closed (Smith excludes char 2, 3).

blocked_by: crypto problems/ghs-to-smith-pipeline-characteristic-mismatch.md (Smith construction not implemented)

forecloses: `Smith isogeny to a plane quartic`; `Diem plane quartic index calculus`; `genus 3 Weil descent in odd characteristic`; `GHS to Smith pipeline`

**AUD-1.** Not applicable (disposition is not in this pass's scope). (open_blocked).

**AUD-2.** Not applicable (disposition is not in this pass's scope).

**AUD-3.** Not applicable (disposition is not in this pass's scope).

**AUD-4.** **Yes: a cheap applicability test decides the pipeline before the trigonal construction is implemented; one statement needs correction.**
(a) VERIFY (recalled; no repository source states the quartic cost): Smith (J. Cryptology 22 (2009), arXiv:0806.2995) pairs his isogeny with Diem's plane-quartic index calculus at O~(q). O~(q^{4/3}) is the double-large-prime cost on genus 3 (KR-IC-a4dd54: "index calculus with double large primes costs O~(q^{2-2/g})", i.e. q^{4/3} at g = 3, the hyperelliptic route). If the recall holds, the lead's mechanism ("Diem's ... O~(q^{4/3}) instead of rho's q^{3/2}") quotes the hyperelliptic cost for the quartic step, and the pipeline's gain is q^{1/3} over the hyperelliptic route and q^{1/2} over rho. I searched for a repository source stating the quartic cost (`problems/ghs-to-smith-pipeline-characteristic-mismatch.md` and `research/ghs_cubic_quartic_ic_20261012/README.md` in crypto, KR-IC-a4dd54, KR-IC-5ea2f8) and found none. This item is not returned as a finding.
(b) Smith's construction needs a specific F_q-rational maximal isotropic (Z/2)^3 subgroup of Jac(C)[2], i.e. a condition on the Galois action on the Weierstrass points; he reports it holds for a positive proportion of genus-3 hyperelliptic curves (about 18.57%, recalled, VERIFY). The repository already names the conditions to test: `problems/ghs-to-smith-pipeline-characteristic-mismatch.md` (crypto) line 84, "Prop. 4 (leading coefficient of s(t) a square)". So the first step can be: factor the Weierstrass polynomial of each odd-characteristic genus-3 descent already enumerated (`research/odd_char_descent_genus3_20261014/REPORT.md`, (m,r) in {(2,6),(3,5)}) and test the isotropic-subgroup condition. Outcomes: no descended curve meets it -> closed_obstructed for this pipeline (scope: those descents); a positive fraction meets it -> implement Smith Props. 2/4 on those only.
(c) Alternative route named in the delta: IDEA-20261024-a29e53 claims genus-3 F_q-curves (hyperelliptic or plane quartic) exist in every irreducible class over F_{q^3} and cites Tian 2023 (KN-LIT-b4a89c, abstract only) for an explicit (l,l,l)-isogeny family at n = 3. Proposed: add it to next_action as a second route; it needs the explicit isogeny degree before it is a transfer.

**AUD-5.** Not applicable (disposition is not in this pass's scope).

**AUD-6.** See the family table below.

### LEAD-TRF-one-point-self-pairing

*A non-degenerate self-pairing or distortion map computable from one point of the prime-order subgroup*  
Disposition: `closed_obstructed`; file `knowledge/leads/ecdlp/transfer/LEAD-TRF-one-point-self-pairing.yaml`

obstruction.kind: `theorem`  
obstruction.statement (verbatim):

> On a cyclic group G of prime order N every bilinear map G x G -> H is a scalar multiple of one fixed map; a non-trivial self-pairing on the rational N-torsion line needs the full E[N] rational (Balasubramanian-Koblitz: E[N] subset E(F_{p^k}) iff N | p^k - 1), i.e. embedding degree 1, and every geometric endomorphism of an ordinary curve commutes with Frobenius and preserves the rational eigenline, so it is not a distortion map. Scope: ordinary curves over prime fields, N || #E, N != p.

obstruction.revisit_when (verbatim):

> a non-bilinear, efficiently computable map out of G with a verified partial return property is exhibited (ECDLP-IDEA-008 style), or an ordinary family with k=1 and prime N of crypto size is needed

forecloses: `CM self-pairing`; `distortion map on an ordinary curve`; `pairing of a point with itself`; `one-point pairing escape`; `partial pairing return cycle`

**AUD-1.** **Not fired.** No non-bilinear map with partial return and no k = 1 crypto-size need in the delta. Also checked against crypto `docs/bounds/FRONTIER.md` (no transfer-mechanism rows: grep for MOV/pairing/embedding/anomal/lift/xedni/cover/descent/GHS/Joux/Smith/quartic returns nothing), `docs/ic/LEADERBOARD.md` (only Table D, JV, comparison withheld), and the orchestrator lists `atlas/obstr_debt.txt` and `atlas/obstr_unexamined.txt` (no TRF entries).

**AUD-2.** **Statement misquotes Balasubramanian-Koblitz at k = 1 (wording; conclusion stands).** BK assumes N does not divide p-1. When N | p-1 and N || #E(F_p), E(F_p)[N] is cyclic, yet the reduced Tate pairing on E(F_p)[N] x E(F_p)/N E(F_p) is non-degenerate, so t(P,P) != 1 without the full E[N] being rational. The clause "a non-trivial self-pairing on the rational N-torsion line needs the full E[N] rational ... i.e. embedding degree 1" is therefore false in its middle part; the corrected statement: "the Weil pairing is alternating, so e_N(P,P) = 1; a non-trivial self-pairing into mu_N exists only through the Tate pairing with N | p-1 (k = 1)". Same omission in LEAD-TRF-second-torsion-direction. No disposition change.

**AUD-3.** Not applicable (disposition is not in this pass's scope). (kind theorem).

**AUD-4.** Not applicable (disposition is not in this pass's scope).

**AUD-5.** Not applicable (disposition is not in this pass's scope).

**AUD-6.** See the family table below.

### LEAD-TRF-padic-canonical-section

*Canonical point sections E(F_p) -> E(Q_p) and their p-adic digits on non-anomalous curves*  
Disposition: `closed_obstructed`; file `knowledge/leads/ecdlp/transfer/LEAD-TRF-padic-canonical-section.yaml`

obstruction.kind: `theorem`  
obstruction.statement (verbatim):

> For p not dividing #E(F_p) the only homomorphic section is the prime-to-p torsion section, which the formal logarithm kills (log vanishes on torsion), exactly as log_p kills the Teichmuller section of F_p^*; any non-homomorphic section recovers d only at the random 1/p rate. Toy runs (p < 2000 and 10^4..10^5) met the frozen criteria; the only failure (naive F_p^* section) is a size effect for g^d < p, not a p-adic one. Scope: non-anomalous prime-field curves, all lifts of E.

obstruction.revisit_when (verbatim):

> a section is found whose carry is small for a positive fraction of targets (that would be a height lead, see LEAD-TRF-global-lift-small-height)

forecloses: `canonical point lift to E(Q_p)`; `p-adic digits of the torsion section`; `Teichmuller section for elliptic curves`; `formal logarithm on non-anomalous curves`; `Hensel lift section`

**AUD-1.** **Fired.** The statement's clause "any non-homomorphic section recovers d only at the random 1/p rate" is now recorded false as worded: DEC-20261024-23d64d (`smart_and_the_canonical_lift.not_established`): "The clause 'every non-canonical section recovers d at the random rate 1/p' is false as worded." EV-CZLIFT-f2a401 (direction contradicts, strength strong): the naive section's Smart-style ratio equals d "far above the mean 1/p on both seeds", explained by the no-carry region (KN-FIND-c71e5d). And the digit sub-question is open: DEC-20261024-23d64d `canonical_section.not_established`: "Whether any coordinate or digit encoding of s_tor carries d. ... The exponent-relevant unknown is KN-OPEN-d3a6f0"; EV-CZLIFT-764f54 excludes only single (character, character) correlations above rho_min = 0.28-0.98 on 42 toy records.
KN-OPEN-d3a6f0 states an exponent-level criterion: "A family with Phi_i(n) >= n^(-1/4 + delta) and a locatable heavy coefficient would therefore be an exponent-level sub-rho attack."
The revisit_when ("a section ... whose carry is small for a positive fraction of targets") does not name that criterion, so the trigger as written misses it.
**Proposed change:** split. Keep this row closed_obstructed (kind theorem) for the homomorphic-section clause, restated from KN-FIND-7e2b94 (s_tor is the unique homomorphic section; the Smart functional vanishes on it; for every section the Smart ratio equals the tau-ratio). Remove the 1/p clause, or mark it heuristic (toy, H-1 of EV-CZLIFT-ad28f5). Remove `p-adic digits of the torsion section` from forecloses. Open a new row (open_next_step) for KN-OPEN-d3a6f0 with step = DEC-20261024-23d64d N-3(1): growth exponent of Phi_i(n), i = 1..4, to n ~ 1e4..1e5, symmetry-matched null. Discriminates: exponent -1/2 within error, or a Weil-type bound proved (Q2) -> closed_obstructed; exponent above -1/4 with a locatable heavy coefficient -> priced comparison against rho.
Caveat: the retained clause rests on KN-FIND-7e2b94, whose proof_status is `derivation` (a checkable written argument, not machine-checked). The split changes no hypothesis status (README rule 2). Also checked against crypto `docs/bounds/FRONTIER.md` (no transfer-mechanism rows: grep for MOV/pairing/embedding/anomal/lift/xedni/cover/descent/GHS/Joux/Smith/quartic returns nothing), `docs/ic/LEADERBOARD.md` (only Table D, JV, comparison withheld), and the orchestrator lists `atlas/obstr_debt.txt` and `atlas/obstr_unexamined.txt` (no TRF entries).

**AUD-2.** **Theorem scope vs forecloses.** The theorem covers homomorphic sections and the formal logarithm. Forecloses `p-adic digits of the torsion section` and `Hensel lift section` block non-homomorphic encodings, which the theorem does not reach (KN-OPEN-d3a6f0; EV-CZLIFT-764f54 "NOT EXCLUDED: nonlinear or pseudorandom encodings of k ..., multi-digit functions, digits beyond index 4 ... any n > 613"). This closure forecloses more than it proved. Same pattern in LEAD-EXO-padic-jet-canonical-lift (`Teichmuller lift digit`); that row is outside this family and is only flagged here.

**AUD-3.** (Kind theorem; the homomorphic clause has a short Lean form.)
**lean_target:** for n >= 1 and any torsion-free additive group B (e.g. Z_p, the target of the formal logarithm on E^(pZ_p) for p >= 3), every additive homomorphism f : ZMod n ->+ B is zero. Consequence: the formal-log functional composed with any homomorphic section <P> -> E^(Q_p) is identically zero. The formal-group input (E^1(Z_p) torsion-free for p >= 3, log an isomorphism onto pZ_p) is a stated hypothesis, not proved in Lean.

**AUD-4.** Not applicable (disposition is not in this pass's scope).

**AUD-5.** Not applicable (disposition is not in this pass's scope).

**AUD-6.** See the family table below.

### LEAD-TRF-pairing-target-field-recost

*Recompute the post-MOV target-field DLP cost (exTNFS in GF(p^12)) for BLS12-381 and BN254 with memory charged*  
Disposition: `open_next_step`; file `knowledge/leads/ecdlp/transfer/LEAD-TRF-pairing-target-field-recost.yaml`

next_action.step (verbatim):

> Run the certified toy tower-field DLP that RQ-PAIR-f2e31f already specifies (H-PAIR-62e9cc: coprime tower splits n in {4,5,6,8,12} and one certified discrete log in F_121), then a small same-shape GF(p^12) calibration against a published record before any deployed estimate.

next_action.discriminates (verbatim):

> If the cost model retrodicts the published record within its stated band, the BLS12-381/BN254 re-estimate is admissible; if it cannot, every downstream bit label in this lane stays unpriced. Either way it says nothing about ECDLP on non-pairing curves.

forecloses: `exTNFS recost for BLS12-381`; `BN254 security level`; `pairing target group DLP`; `tower number field sieve memory`; `polynomial selection tail for pairing curves`

**AUD-1.** Not applicable (disposition is not in this pass's scope). (open_next_step).

**AUD-2.** Not applicable (disposition is not in this pass's scope).

**AUD-3.** Not applicable (disposition is not in this pass's scope).

**AUD-4.** No theorem or counterexample decides it faster: the question is whether a cost model retrodicts a published record, which is empirical calibration. The toy step (ordered coprime splits of n in {4,5,6,8,12}; one certified log in F_121; EXP-PAIR-513c28 approved) is a closed-form enumeration plus a certificate. It calibrates tooling and decides nothing about BLS12-381/BN254.
**Proposed change (bookkeeping):** map IDEA-20261022-e5b3a4 (model-priced MOV + (S)exTNFS reference rows beside matched rho; not in coverage.tsv) to this lead. It is the same question with a 5a-band presentation.

**AUD-5.** Not applicable (disposition is not in this pass's scope).

**AUD-6.** See the family table below.

### LEAD-TRF-prime-field-isogeny-to-weak

*Isogeny transfer of a prime-field ECDLP to a weaker curve (anomalous, low embedding degree, descent-friendly) in the same class*  
Disposition: `closed_obstructed`; file `knowledge/leads/ecdlp/transfer/LEAD-TRF-prime-field-isogeny-to-weak.yaml`

obstruction.kind: `theorem`  
obstruction.statement (verbatim):

> Tate: ordinary curves over F_p are F_p-isogenous iff they have the same #E(F_p); trace one and k = ord_N(p) are functions of #E and p, and prime fields admit no GHS descent, so the special set inside a generic class is empty at every size (EV-IT-511f3d). Scope: prime fields, ordinary or supersingular classes. Over composite-degree binary fields descent weakness is NOT class-invariant (see LEAD-TRF-ghs-binary-composite).

obstruction.revisit_when (verbatim):

> a prime-field weakness is found that is not a function of (#E, p) (that is the ECTD lead)

forecloses: `walk the isogeny class to a weak curve`; `isogeny transfer to an anomalous curve`; `isogeny path to low embedding degree`; `isogeny transfer cost gate`; `same order same difficulty`

**AUD-1.** **Not fired.** The trigger points at the ECTD lead. Its 20-arm panel is still lost to infrastructure (`problems/ectd-arity3-panel-infrastructure-loss.md`: "only 3 arms have output_validated receipts"). No non-(#E, p) weakness is observed. See LEAD-TRF-teske-secret-isogeny-trapdoor AUD-4: a pigeonhole bound caps the native factor-base occupancy meter at a constant factor, so even a fired ECTD meter of that type cannot reopen this row at the exponent level. Also checked against crypto `docs/bounds/FRONTIER.md` (no transfer-mechanism rows: grep for MOV/pairing/embedding/anomal/lift/xedni/cover/descent/GHS/Joux/Smith/quartic returns nothing), `docs/ic/LEADERBOARD.md` (only Table D, JV, comparison withheld), and the orchestrator lists `atlas/obstr_debt.txt` and `atlas/obstr_unexamined.txt` (no TRF entries).

**AUD-2.** Scope (prime fields, Tate) matches the forecloses; the binary exception is stated. No change.

**AUD-3.** Not applicable (disposition is not in this pass's scope). (kind theorem).

**AUD-4.** Not applicable (disposition is not in this pass's scope).

**AUD-5.** Not applicable (disposition is not in this pass's scope).

**AUD-6.** See the family table below.

### LEAD-TRF-same-field-genus-g-embedding

*Embed E/F_p as an isogeny factor of a genus-g Jacobian over the same field (covers, quadric pencils, quartic/bielliptic models)*  
Disposition: `closed_obstructed`; file `knowledge/leads/ecdlp/transfer/LEAD-TRF-same-field-genus-g-embedding.yaml`

obstruction.kind: `theorem`  
obstruction.statement (verbatim):

> Tate multiplicativity gives #Jac(C)(F_p) = N * #A(F_p) with #A = Theta(N^{g-1}); genus-g index calculus costs O~(q^{2-2/g}) >= q for g >= 2, at least a full exponent above rho's N^{1/2}; quadric-pencil and quartic models of E itself are isomorphic models with the same group. Scope: prime-field source curves, any same-field cover (DEC-20260902-4c82fd).

obstruction.revisit_when (verbatim):

> never for same-field covers; extension-field sources are separate leads

forecloses: `genus g cover of a prime field curve`; `Poincare factor embedding`; `split Jacobian projection`; `quadric pencil model transfer`; `bielliptic quartic relation`; `higher genus Jacobian over the same field`

**AUD-1.** **Not fired.** revisit_when is 'never' (see AUD-2). Also checked against crypto `docs/bounds/FRONTIER.md` (no transfer-mechanism rows: grep for MOV/pairing/embedding/anomal/lift/xedni/cover/descent/GHS/Joux/Smith/quartic returns nothing), `docs/ic/LEADERBOARD.md` (only Table D, JV, comparison withheld), and the orchestrator lists `atlas/obstr_debt.txt` and `atlas/obstr_unexamined.txt` (no TRF entries).

**AUD-2.** **Kind mislabelled; 'never' unsupported.** The theorem part is Tate multiplicativity (#Jac(C) = N * #A, #A = Theta(N^{g-1})). The load-bearing cost "genus-g index calculus costs O~(q^{2-2/g})" is a known-algorithm upper bound, not a lower bound (standing note SO-COVER). So the closure forecloses every future genus-g Jacobian algorithm on the strength of today's algorithms.
**Proposed change:** obstruction.kind theorem -> cost_model (Tate part stays as a stated theorem); revisit_when "never ..." -> "a DLP algorithm on genus-g Jacobians (g >= 2) over F_q with cost below q^{1/2}, or a same-field embedding whose complementary factor A has O(1) order (cf. LEAD-EXO-split-jacobian-projection revisit)". The disposition stays closed_obstructed.

**AUD-3.** (After relabelling to cost_model.) No short proof replaces it: no lower bound for DLP on genus-g Jacobians above the generic sqrt bound is known, so the cost model cannot become a theorem. No lean_target.

**AUD-4.** Not applicable (disposition is not in this pass's scope).

**AUD-5.** Not applicable (disposition is not in this pass's scope).

**AUD-6.** See the family table below.

### LEAD-TRF-second-torsion-direction

*Reach a second N-torsion direction: nonequivariant trace-zero transfer, Kani/Robert graph kernels, Richelot gluing of E with E'*  
Disposition: `closed_obstructed`; file `knowledge/leads/ecdlp/transfer/LEAD-TRF-second-torsion-direction.yaml`

obstruction.kind: `theorem`  
obstruction.statement (verbatim):

> Balasubramanian-Koblitz: for N || #E(F_p), N != p, E(F_{p^k})[N] is larger than the rational line iff N | p^k - 1, i.e. the embedding degree divides k. Hence for N not dividing k, T_k(E)[N] = 0 (trace acts as [k] on the rational line), and an F_p-rational graph-type (N,N) kernel exists only when k_emb = 1; both reduce to MOV. Scope: ordinary and supersingular curves over F_p, prime N.

obstruction.revisit_when (verbatim):

> a non-group-theoretic correspondence (not a homomorphism on N-torsion) with verified scalar compatibility is exhibited

forecloses: `trace zero variety transfer`; `nonequivariant transfer to an extension field`; `Kani embedding of the ECDLP`; `Richelot gluing with an isogenous curve`; `Castryck-Decru machinery for ECDLP`; `higher dimensional isogeny embedding`

**AUD-1.** **Not fired.** No non-group-theoretic correspondence with scalar compatibility appears in the delta. Also checked against crypto `docs/bounds/FRONTIER.md` (no transfer-mechanism rows: grep for MOV/pairing/embedding/anomal/lift/xedni/cover/descent/GHS/Joux/Smith/quartic returns nothing), `docs/ic/LEADERBOARD.md` (only Table D, JV, comparison withheld), and the orchestrator lists `atlas/obstr_debt.txt` and `atlas/obstr_unexamined.txt` (no TRF entries).

**AUD-2.** **Same BK wording issue as LEAD-TRF-one-point-self-pairing.** "for N || #E(F_p), N != p, E(F_{p^k})[N] is larger than the rational line iff N | p^k - 1" is false at k = 1 when N | p-1 (then N | p - 1 but E(F_p)[N] is the rational line because N || #E). BK assumes N not dividing p-1. The conclusion ("both reduce to MOV") is unaffected, since k = 1 is itself the MOV/Tate case. Proposed: add "and N not dividing p-1 (the k = 1 case is the Tate pairing itself)". The forecloses `higher dimensional isogeny embedding` and `Castryck-Decru machinery for ECDLP` rest only on the F_p-rational (N,N) graph-kernel argument. Interpretation: embeddings built on auxiliary torsion of other degrees are not covered by the stated proof; I found no record proposing one for the ECDLP, so this is flagged and no change is proposed.

**AUD-3.** Not applicable (disposition is not in this pass's scope). (kind theorem).

**AUD-4.** Not applicable (disposition is not in this pass's scope).

**AUD-5.** Not applicable (disposition is not in this pass's scope).

**AUD-6.** See the family table below.

### LEAD-TRF-small-genus-cover-general

*Find small-genus GHS/Kummer covers beyond the Joux-Vitse weak class (other configurations over F_{q^3}, F_{p^k} with k = 6, 10, 14)*  
Disposition: `closed_obstructed`; file `knowledge/leads/ecdlp/transfer/LEAD-TRF-small-genus-cover-general.yaml`

obstruction.kind: `proof`  
obstruction.statement (verbatim):

> Riemann-Hurwitz census g = 1 - 2^m + 2^{m-2} R: among 2-torsion Kummer covers of E/F_{q^3} only the JV configuration gives g <= 3 (others g in {1, 7, 9, 13}); for E/GF(p^k) with F_p(j) = GF(p^k) every GHS cover has genus >= 9, 49, 41 at k = 6, 10, 14, which repriced 247 of 846 cover_descent rows down to marginal/boundary. Scope: Kummer/GHS covers of the x-line in odd characteristic.

obstruction.revisit_when (verbatim):

> a non-Kummer cover family (Hess Artin-Schreier analogue, non-x-line function) is constructed in odd characteristic

forecloses: `generalize the Joux-Vitse weak class`; `genus 3 cover outside the weak class`; `Kummer cover genus over F_{q^3}`; `cover descent at genus k`

**AUD-1.** **Trigger pending (proposed, not observed).** revisit_when requires "a non-Kummer cover family (Hess Artin-Schreier analogue, non-x-line function) is constructed in odd characteristic". New records (2026-10-24): IDEA-20261024-d84f20 introduces exactly the non-x-line degree-2 functions f_T, T in E(K)/2E(K), and predicts at n = 3 a T != 0 configuration "(m,r) = (2,6), a single 6-orbit absent from the x-line, ... expected to be the Momose-Chao Type 2 family (to be checked)", with a minimal test (extend cover_census_n.rs, enumerate (2,2)/(4) 4-sets at q = 5, 7, 11). IDEA-20261024-a29e53 claims "classes with #E(K) odd or 2 mod 4, where the GHS cover floor is 13 / 5 (proved), still hold genus-3 Jacobians, and the cover floor is not the genus floor" (Torelli plus Serre's twist theorem), and points to Tian 2023 (KN-LIT-b4a89c) for explicit isogenies. Both have status proposed. The approved EXP-PEXT-212d5c (DEC-20261024-992998) covers the x-line at n = 7 only and has no report. Nothing is constructed yet, so the trigger has not fired by observation. Also checked against crypto `docs/bounds/FRONTIER.md` (no transfer-mechanism rows: grep for MOV/pairing/embedding/anomal/lift/xedni/cover/descent/GHS/Joux/Smith/quartic returns nothing), `docs/ic/LEADERBOARD.md` (only Table D, JV, comparison withheld), and the orchestrator lists `atlas/obstr_debt.txt` and `atlas/obstr_unexamined.txt` (no TRF entries).

**AUD-2.** **Over-scoped forecloses.** Proof scope: "Kummer/GHS covers of the x-line in odd characteristic". Forecloses `generalize the Joux-Vitse weak class` and `genus 3 cover outside the weak class` block the d84f20 (non-x-line) and a29e53 (Jacobian existence without a cover) directions, which the proof does not reach. Proposed: `x-line Kummer cover of genus <= 3 outside the JV configuration`.

**AUD-3.** Not applicable (disposition is not in this pass's scope). (kind proof).

**AUD-4.** Not applicable (disposition is not in this pass's scope).

**AUD-5.** (Not open_unexamined. The split proposed here creates an open sub-row, given in this pass.) **Proposed:** split. The x-line closure stays closed_obstructed. A new open_next_step row 'non-x-line degree-2 functions and Jacobian-existence routes over F_{q^3}' gets step = IDEA-20261024-d84f20 minimal test (1)-(3) at n = 3, q = 5, 7, 11, with the T = 0 reproduction as positive control. Discriminates: at least one T != 0 genus-3 curve outside the JV configuration -> a new candidate weak class over F_{q^3}, followed by descent/injectivity and cost questions; zero such curves (G = 0) -> extend the closure to all degree-2 functions (strengthened proof scope). Map the six IDEA-20261024-* PEXT ideas to it in coverage.tsv (none is mapped).

**AUD-6.** See the family table below.

### LEAD-TRF-teske-secret-isogeny-trapdoor

*Teske-style trapdoor on ordinary prime-field curves: a secret isogeny to an endpoint with a non-invariant ECDLP weakness*  
Disposition: `open_next_step`; file `knowledge/leads/ecdlp/transfer/LEAD-TRF-teske-secret-isogeny-trapdoor.yaml`

next_action.step (verbatim):

> Re-run the approved 20-arm panel EXP-ECTD-0cf008 (H-ECTD-e88346: crater/floor pairs with conductor steps 8209 and 131101, native vs random factor bases, verified arity-3 relation occupancy); every trial of run-20261016T0409Z died with psutil_import_missing. ALSO (merged from LEAD-STR-secret-isogeny-trapdoor): Discharge the proof obligation in IDEA-20260805-4243e6 / IDEA-20260808-5ee6b4. It claims the class has about h(O) = p^{1/2+o(1)} members, so a secret path holds at most (1/2) log2 p bits. Enumerating or walking the class costs about sqrt(N), so the trapdoor holder's advantage over public rho is capped at zero exponent. Write it as a reviewed derivation that names its cost model for testing endpoint weakness (c_test).

next_action.discriminates (verbatim):

> Both floor/crater ratios beyond 20% with 99% intervals excluding one would be the first non-invariant meter and reopen trapdoor costing; ratios consistent with one, as the isogeny-fibre pullback theorem predicts, close the IC-meter half at toy scale.

forecloses: `elliptic curve trapdoor`; `secret isogeny to a weak endpoint`; `heavy tail of Semaev meters in an isogeny class`; `conductor step relation yield`; `hidden weak curve in an ordinary class`; `secret isogeny to a weak curve as a backdoor`; `Teske trapdoor for prime-field curves`; `vertical conductor barrier hides a weakness`; `trapdoor DDH from a secret isogeny`; `descend to the N-floor to make the target subgroup rational`

**AUD-1.** Not applicable (disposition is not in this pass's scope). (open_next_step). Observation: the 20-arm panel is still blocked (`problems/ectd-arity3-panel-infrastructure-loss.md`, Status open, 'Last updated 2026-10-18'; IDEA-20261018-b32287 proposes the re-run).

**AUD-2.** Not applicable (disposition is not in this pass's scope).

**AUD-3.** Not applicable (disposition is not in this pass's scope).

**AUD-4.** **Yes: an elementary pigeonhole theorem settles the exponent question for the IC-meter half before the panel re-runs.**
Observation: H-ECTD-e88346's own mechanism concedes "Equal base cardinality and shared group order fix the all-target ordered multiplicity mean but permit a different distribution of triple sums" (`ledger/hypotheses/H-ECTD-e88346.yaml`).
Theorem (informal): G a finite abelian group of order N, F a subset of G, m >= 1, c(R) the number of m-multisets of F summing to R. Then sum_R c(R) = M := C(|F|+m-1, m), so the nonempty-target fraction (occupancy) of any curve's native base satisfies occ <= min(1, x), x = M/N. A target-uniform (Poisson-like) curve has occ = 1 - e^{-x} + o(1). Hence the occupancy advantage of the best class member over a Poisson-like member is at most min(x,1)/(1 - e^{-x}) <= e/(e-1) ~= 1.582 at matched |F| and N. This is the same ceiling KN-TECH-5c41e7 records (DEC-20261024-23d64d knowledge_promotion: "capped by min(x,1)/(1 - e^-x)").
Interpretation (conditional on a positive fraction of class members being Poisson-like, which is heuristic): a native-coordinate factor-base occupancy meter can give a trapdoor holder at most a constant factor of about 1.58 per relation over the best public alternative, so zero exponent. The 20% lead threshold sits below this cap, so the panel can still fire, but only for a constant.
Outcome map: panel ratio <= 1.58 (either sign) -> the IC-meter half closes as closed_obstructed (kind proof, constant factor); any curve exceeding a Poisson baseline by more than min(x,1)/(1 - e^{-x}) -> instrument error (invalid), not a lead. Other non-invariant meters (Macaulay degrees, conductor-level arithmetic) are not covered and stay open.
Also the merged proof obligation (IDEA-20260805-4243e6 / 20260808-5ee6b4): the class is a Cl(O)-torsor of size h(O) <= (1/pi) sqrt|D| log|D| + O(sqrt|D|) (elementary class-number bound), so a secret position holds at most (1/2) log2 p + O(log log p) bits. That is a short paper proof; c_test must still be named for the hiding-cost half.
**Proposed change:** split the IC-meter half into a closed_obstructed row (proof above, lean_target below); keep this row open_next_step for non-occupancy meters and for the c_test-priced hiding derivation.
lean_target: for a finite AddCommGroup G, F : Finset G and m : N, `((Finset.univ : Finset G).filter (fun R => exists s : Multiset G, s.card = m and (forall x in s, x in F) and s.sum = R)).card <= Nat.choose (F.card + m - 1) m`. It follows from the image of the multiset map having at most that many elements.

**AUD-5.** Not applicable (disposition is not in this pass's scope).

**AUD-6.** See the family table below.

### LEAD-TRF-teske-trapdoor-fp6-weak-class

*Teske-style trapdoor over F_{p^6} built on the Joux-Vitse weak class*  
Disposition: `open_unexamined`; file `knowledge/leads/ecdlp/transfer/LEAD-TRF-teske-trapdoor-fp6-weak-class.yaml`

next_action.step (verbatim):

> For random ordinary classes over F_{p^6}, measure the cost of the public ISO-1 walk to the nearest weak curve. Then ask whether any class places its weak curve beyond a public walk, at a cost far above 1e5-1e8 F_p multiplications against about 1e10 for the attack.

next_action.discriminates (verbatim):

> If the walk is always cheap, the trapdoor hides nothing and the lead closes with a cost-model obstruction. If some classes have far or unreachable weak curves, a hidden-weakness construction exists and needs a security definition.

forecloses: `trapdoor in the weak class over F_p^6`; `hidden Joux-Vitse weak curve`; `secret isogeny to a JV-weak curve`; `Teske trapdoor odd characteristic`

**AUD-1.** Not applicable (disposition is not in this pass's scope).

**AUD-2.** Not applicable (disposition is not in this pass's scope).

**AUD-3.** Not applicable (disposition is not in this pass's scope).

**AUD-4.** Not applicable (disposition is not in this pass's scope).

**AUD-5.** **First discriminating step from data the program already holds (no new run).** `research/weak_curve_database_20261012/THEOREMS_AND_HEURISTICS.md` (crypto) records per-class weak representative counts and class numbers: "traces 137406 and 137410 have equal Frobenius conductor 2-depth 3 ... saved maximal-order class number 414. Their cubic representative counts are 0 and 12", and a "Selected CM-order intersection: Exact class decision for the two named hyperelliptic genus-three branches".
Quantity: per class, W = number of JV-weak curves, h(O_sel) = size of the level (CM order) that holds them, and whether O_sel is reached by vertical isogenies.
Interpretation: public search from E_pub costs about (vertical walk to O_sel) + h(O_sel)/W horizontal steps (random walk) or direct construction. If W/h(O_sel) >= 1/poly(log p), or the weak curves are pinned by a structural invariant reachable vertically, the public walk is cheap -> closed_obstructed (kind cost_model: no hiding). If some classes have W = O(1) with h(O_sel)/W above the attack cost (the lead quotes about 1e10), hiding exists -> open_next_step with a security definition.
Outcomes map exactly to these two dispositions. Proposed next_action: tabulate W and h(O_sel) from the existing census before any new measurement.

**AUD-6.** See the family table below.

## AUD-6: standing obstructions of the transfer family, read as hypotheses

| obstruction (lead) | obstructing quantity | theory that takes it as a HYPOTHESIS |
|:--|:--|:--|
| SO-ISO (LEAD-TRF-prime-field-isogeny-to-weak) | weakness is a function of (#E, p) | Teske-type trapdoors where weakness is NOT class-invariant: composite binary fields (LEAD-TRF-ghs-binary-composite) and the F_{p^6} JV weak class (LEAD-TRF-teske-trapdoor-fp6-weak-class). Over F_p itself: none found. The only non-invariant meter in the program (native factor-base occupancy, ECTD) is capped at a constant by the pigeonhole bound in LEAD-TRF-teske-secret-isogeny-trapdoor AUD-4. |
| SO-PAIR (LEAD-TRF-second-torsion-direction, LEAD-TRF-one-point-self-pairing, LEAD-TRF-mov-small-embedding-degree) | k = ord_N(p) | Pairing-friendly constructions (BN/BLS/KSS) take small k as the design hypothesis; the cost then moves to (ex)TNFS in F_{p^k} (LEAD-TRF-pairing-target-field-recost). For random prime-field curves: none found. |
| SO-PADIC (LEAD-TRF-padic-canonical-section) | Hom(Z/n, torsion-free) = 0: the formal log kills s_tor | The hidden-number / Fourier-learning lineage (Boneh-Venkatesan 1996; Akavia-Goldwasser-Safra 2003, as cited in KN-OPEN-d3a6f0) takes a heavy Fourier coefficient of an efficiently computable encoding as hypothesis and turns it into recovery with about tau^-2 queries; s_tor gives exact shift-query access. Open quantity: Phi_i(n) vs n^{-1/4} (KN-OPEN-d3a6f0). Recalled, not verified here: on the canonical lift s_tor is the elliptic Teichmuller lift (DEC-20261024-23d64d: "on the canonical lift, is the unique Frobenius-fixed section"), and Finotti (J. Number Theory 2002) gives its first Witt coordinate as a polynomial in x_0 of degree about 3p/2, too high for Weil's bound. That explains why Q2 of KN-OPEN-d3a6f0 has no known bound. A G_m control is available: digit 1 of the multiplicative Teichmuller lift is x * q(x) mod p (q the Fermat quotient), for which nontrivial character-sum bounds exist (recalled). |
| SO-XEDNI (LEAD-TRF-function-field-xedni-lift) | alpha = 3; at most four prescribable sections vs MW rank <= 8 | Elliptic surfaces with a dimension surplus (K3 or higher, more free section parameters than prescribed conditions; LEAD-ICP-xedni-function-field-sections revisit_when) would take the parameter count as hypothesis. No construction found. |
| fixed-rank counting bound (LEAD-TRF-global-lift-small-height, after AUD-1) | #{points of height <= B} ~ (log B)^{r/2} at fixed r | High-rank families: DEC-20261024-23d64d puts the break-even near r ~ 34 at 2^128 (60 at 2^256). Known constructions over Q stop below that (record rank 28-29, recalled). Conditional, none usable. |
| h(D) cost model (LEAD-TRF-cm-canonical-lift-heights) | degree h(D) of the CM field of definition | CM-method curves with small |D| (e.g. j = 0, D = -3, h = 1, the secp256k1 family) take small h(D) as hypothesis. For them the lift is free and the obstruction falls back to the counting bound plus the known sqrt(6) automorphism speedup. |
| SO-COVER (LEAD-TRF-same-field-genus-g-embedding, LEAD-TRF-small-genus-cover-general) | O~(q^{2-2/g}) genus-g IC cost; Riemann-Hurwitz genus of x-line covers | Weil descent takes the genus-g cost as given and wins by shrinking the field (GHS, JV). IDEA-20261024-a29e53 (Torelli + Serre) decouples 'a genus-3 Jacobian exists in the class' from 'a low-genus cover exists', taking the Riemann-Hurwitz floor as a hypothesis about covers only. |
| Tate multiplicativity (same-field) | #Jac = N * #A | None found. |
| BK / bilinearity (one-point self-pairing) | bilinear maps on a cyclic group are scalar multiples | None found: any non-bilinear replacement falls under SO-NET/SO-DECK (LEAD-TRF-miller-cocycle-nonhom-transfer AUD-5). |

---

## Family: structure

# Audit: structure family (LEAD-STR-*), passes AUD-1..AUD-6

Reviewer audit, 2026-10-24. Read-only on all repositories; every file written by this audit is under `/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/audit/`.
Scope: all 17 rows in `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/structure/`, each read in full. Current state for AUD-1: `atlas/KRMAP.md`, crypto `docs/ic/LEADERBOARD.md` and `docs/bounds/FRONTIER.md` (scratchpad crypto-main), the 201 paths in `atlas/delta.txt`, and ATLAS.md dispositions.

Conventions: **Observed** means seen in a cited file or computed by an audit script whose path is given. **Interpretation** is conditional and marked. Quotes of `obstruction.statement` and `revisit_when` are verbatim (whitespace normalised) from the YAML.

## Summary

| lead | disposition (kind) | AUD-1 trigger | change proposed |
|:--|:--|:--|:--|
| `LEAD-STR-automorphism-quotient-rho` | closed_known (literature) | not fired vs current state; clause 2 would be met once audit CM construction is registered | scope statement to F_p; drop/rephrase fruitless-cycle phrase; tighten revisit_when |
| `LEAD-STR-class-group-ecdlp-bridge` | open_next_step (-) | n/a | replace next_action with stated simulation lemma; on check -> closed_obstructed |
| `LEAD-STR-class-representative-ic-selection` | open_next_step (-) | n/a | keep open_next_step; rewrite next_action (h>1 max-N0 vs subgroup-only; h=1 mean proved, coverage only); graph-study mean arm decided |
| `LEAD-STR-curve-generation-provenance-seeds` | exhausted_at_scale (measured) | near, not fired | drop Brainpool/BN phrase; scope 21 vs 69 cohort; union-bound Lean target |
| `LEAD-STR-endo-scalar-action-generic` | closed_obstructed (theorem) | not fired (CZLIFT section is homomorphic) | restate as Omega(sqrt(N/ord lambda)); Lean target |
| `LEAD-STR-glv-gls-isogeny-loop-scalar-mult` | closed_obstructed (proof) | not fired (targets walked) | scope the orbit claim; rephrase GLV-rho phrase |
| `LEAD-STR-isogeny-class-generic-invariance` | closed_obstructed (theorem) | not fired | qualify depth phrase "generic, over F_p"; add Koblitz crater exception |
| `LEAD-STR-isogeny-transport-preprocessing` | closed_obstructed (proof) | not fired | none |
| `LEAD-STR-isogeny-walk-weak-neighbour` | closed_known (literature) | not fired | add "over F_p" to statement |
| `LEAD-STR-jmv-random-self-reduction` | closed_known (literature) | not fired | rewrite unsatisfiable revisit_when; Lean target |
| `LEAD-STR-koblitz-volcano-descendants` | closed_obstructed (measured) | not fired | kind measured -> theorem (Aut) + cost model (non-unit) |
| `LEAD-STR-p192-class-cm-relations` | closed_obstructed (theorem) | not fired | none (add N0 note to evidence) |
| `LEAD-STR-safecurves-parameter-audit` | closed_known (literature) | not fired | none |
| `LEAD-STR-secp256k1-cm-class-audit` | closed_obstructed (theorem) | not fired | rephrase sextic-twist phrase |
| `LEAD-STR-small-cm-disc-nonunit-endo` | closed_obstructed (theorem) | not fired vs current state; construction clause would be met once audit computation is registered; canonicalisation open | kind -> cost_model for net clause; narrow revisit_when; NEW LEAD (IC orbit columns) |
| `LEAD-STR-special-j-ic-semaev` | open_next_step (-) | n/a | support lemma; N0/cofactor control; cost ceiling; add H-STR-002 |
| `LEAD-STR-torsion-module-leak` | closed_obstructed (proof) | not fired | character-sum theorem for non-homomorphic clause |

No lead in this family is open_unexamined or open_blocked, so AUD-5 has no rows. AUD-4 has three rows: class-group-ecdlp-bridge, class-representative-ic-selection and special-j-ic-semaev.

## Principal observation (class-representative IC effects are exact cofactor-class counting)

Audit computation over crypto `research/isogeny-volcano-cost-v2_20261017/`. Scripts and outputs are in `/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/audit/n0check/` (`n0.py`, `n0_out.txt`, `n0_rows.py`, `n0_rows.jsonl`, `residual.py`, `residual_out.txt`).

- For each of the 7,760 archived curve-models, the script rebuilt the `prime-abscissa:size=32` base and the negation-folded pair table, including doubles, following `prime_factor_base` and `PairTable::build_negation_folded` in crypto `src/cryptanalysis/ic_boundary.rs`. It counted N0, the number of folded pair sums lying in the order-r subgroup.
- Normalising every archived ic-mitm run's yield (relations_found/targets_tried) by 2·N0/r changes the results as follows:

| quantity | raw (archive) | N0-normalised |
|:--|--:|--:|
| ℓ=2 floor/crater, geometric mean of 14 classes | 0.9417 | 0.9983 |
| ℓ=3 floor/crater, geometric mean of 14 classes | 1.0062 | 1.0046 |
| crater model heterogeneity Q/df, all 28 classes | 1.539 (7963.7/5175) | 0.995 (5147.8/5175) |
| same, 25 classes with h > 1 | 1.612 | 0.994 |
| same, 3 classes with h = 1 | 0.999 | 0.999 |

- The closed form (F+1)/(F+3) = 0.943 at F = 32 (floor |E(F_p)[2]| = 2, crater 4) is the identity's prediction for H1's 0.942 [0.928, 0.956].
- Interpretation (conditional on uniform targets and on the code reading): in this archive, the ℓ=2 level effect, the isomorphic-model effect and the horizontal effect are all the cofactor-class count of the base. The lever is exactly zero at cofactor h = 1 and O(1/F) otherwise.


---

## LEAD-STR-automorphism-quotient-rho

*Rho on E/Aut (negation, j=0 order-6, j=1728 order-4) and anything beyond sqrt(|Aut|)*  
Path: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/structure/LEAD-STR-automorphism-quotient-rho.yaml`  
Disposition: **closed_known** (kind: literature)

> **obstruction.statement:** The automorphism quotient gives exactly a sqrt(|Aut|) constant (KR-RHO-0528e7, KR-RHO-fb88e6, KN-TECH-018), reproduced here: the 26-bit volcano census j=0 crater rho.cubic/rho.negation is 0.573 [0.562, 0.585] against 0.577 theory, and EV-ENDO-10109d puts the j=0 and j=1728 ratio-to-ceiling at 1.0043 and 1.0442 over 20 seeds at p=100057. Quotienting by the full End(E) action leaves two classes and is useless, because a non-unit endomorphism has orbits of size ord_N(lambda), so the ceiling is sqrt(|Aut|) for any equivalence-class walk on a prime-order group.

> **revisit_when:** A canonicalisation with per-step cost kappa below 1 group operation is found for a group larger than Aut, or a curve class with a cheap small-orbit non-unit endomorphism is constructed (see LEAD-STR-small-cm-disc-nonunit-endo).

forecloses: "automorphism quotient beats sqrt(|Aut|)"; "GLV-split rho walk on j=0 curves"; "quotient the walk by the full endomorphism ring"; "orbit-choice mixing on E/Aut gives extra speedup"; "fruitless cycles at |Aut| greater than 2"

### AUD-1

**Not fired against the defined current state (KRMAP, leaderboard, delta, ATLAS).** The second clause would be met literally once this audit's CM construction (`cm_verify_out.txt`) is registered as evidence.
- Clause 1 ("canonicalisation with per-step cost kappa below 1 group operation ... for a group larger than Aut"): the only new rho-orbit work in the delta is the six-class walk, cryptanalysis `docs/sixclass-20261024/assessment.md`. Its group is |Aut| = 6 (equal to Aut, not larger). Observed there: "Six-class took 1.257x the wall time" (original run) and "six-class totals ... 1.826x the mean default time" (A/B/A receipt `docs/sixclass-20261024/paired-glv-j0-26-aba.json`). Not fired.
- Clause 2 ("a curve class with a cheap small-orbit non-unit endomorphism is constructed"): this audit verified CM parameters (see LEAD-STR-small-cm-disc-nonunit-endo, AUD-1) for prime-field curves with a degree-2 endomorphism whose eigenvalue on the prime-order subgroup has order exactly h = 17, 19, 23, 107, 283 with log2 N = h (`/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/audit/n0check/cm_verify.py`, output `/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/audit/n0check/cm_verify_out.txt`). The orbit is small (h ~ log2 N) and alpha is cheap to evaluate (a degree-2 map), so the literal clause would be met once that computation is registered. It is not in the current state. Interpretation: the substance of the trigger (a net rho gain above sqrt(|Aut|)) still needs an o(h) canonicalisation, which is the open clause of LEAD-STR-small-cm-disc-nonunit-endo. Proposed: record the construction in `evidence`, and tighten revisit_when to "net factor sqrt(orbit)/kappa exceeds sqrt(|Aut|)".

### AUD-2

**Over-reach found (two items).**
1. The statement's last sentence, "the ceiling is sqrt(|Aut|) for any equivalence-class walk on a prime-order group", is contradicted in binary scope by KR-RHO-482ed3 (signed Frobenius on Koblitz curves gives sqrt(2m)) and by this family's own LEAD-STR-koblitz-volcano-descendants best_measured ("crater+tau 6.36x fewer steps"). The orbit argument ("orbits of size ord_N(lambda)") is right, but ord_N(tau) = m is small. The ceiling holds when ord_N(lambda) is about N, or when canonicalisation costs about ord_N(lambda) maps. Proposed scope: "prime-field curves whose non-unit endomorphisms have ord_N(lambda) >= log N / log deg, canonicalised by enumeration (IDEA-20260901-6b63a4)". This audit's CM construction shows the second condition, not the first, carries the obstruction over F_p.
2. forecloses "fruitless cycles at |Aut| greater than 2" is not covered. The obstruction proves a ceiling. It does not prove that the ceiling is attained or that fruitless-cycle handling is solved. The realised constant is below the ceiling in KR-RHO-825bca ("automorphism factor 0.790·sqrt6 on BN254") and in the six-class toy above. `ecc-challenges/pool/docs/DESIGN.md` (lead evidence) still lacks the negation map. Proposed: rephrase to "fruitless-cycle handling gives more than sqrt(|Aut|)", and route the realised-constant gap to an engineering lead.

### AUD-3

Not applicable (kind literature). No Lean target is needed for the ceiling itself. See LEAD-STR-endo-scalar-action-generic AUD-2 for the GGM-with-free-scalar-oracle bound that formalises it.

### AUD-4

Not applicable (closed).

### AUD-5

Not applicable.

### AUD-6

SO-GEN and SO-ENDO enter through the sqrt(|Aut|) ceiling. A theory that takes |orbit| as a hypothesis is Duursma-Gaudry-Morain orbit rho (KR-RHO-0528e7). It is already used. New generative material: the CM construction of prime-field curves with a small-order degree-2 endomorphism (LEAD-STR-small-cm-disc-nonunit-endo AUD-1). It makes |orbit| = 2h about 2 log2 N available to an algorithm that needs no per-step canonicalisation: index calculus with orbit columns (proposed NEW LEAD, see the cross-cutting section).


---

## LEAD-STR-class-group-ecdlp-bridge

*Reduction between Cl(O)-vectorization (or CM self-pairings) and ECDLP in the same class*  
Path: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/structure/LEAD-STR-class-group-ecdlp-bridge.yaml`  
Disposition: **open_next_step**

> **next_action.step:** Write and review the simulation lemma of H-CLGP-63f471 / IDEA-20260807-1b7241. In a curve-aware generic group model where the adversary also gets free class-group action on curves, show ECDLP still needs Omega(sqrt N) group operations. State quantifier order and the size-gap argument (h ~ p^{1/2} vs N ~ p, IDEA-20260807-bbdcf3).

> **next_action.discriminates:** A checked simulator closes the lane at exponent 1/2 with a theorem. A place where the simulation fails names the one bridge (for example the ray-class level fiber of IDEA-20260812-a3720a) that a concrete reduction must use.

forecloses: "class group action solves ECDLP"; "vectorization oracle gives discrete logs"; "CM self-pairing breaks the discrete log"; "ray class group torsor bridge"; "n-torsion edge character as a bridge map"

### AUD-1

Not applicable (open_next_step).

### AUD-2

Not applicable (no obstruction). The forecloses phrases serve as de-duplication for an open lead.

### AUD-3

Not applicable.

### AUD-4

**Yes. The queued step is itself a proof, and a short version can be stated now.** The current next_action rests partly on "the size-gap argument (h ~ p^{1/2} vs N ~ p, IDEA-20260807-bbdcf3)". That argument alone does not decide the question. Two vectorization answers carry about log p bits, which is enough to encode k, so a counting argument cannot rule out an O(1)-query reduction. The content that does decide it is the k-independence of curve-only answers.

*Informal theorem (Lean target candidate).*
- **Setting.** E/F_p is ordinary with End(E) = O, G ≤ E(F_p) is cyclic of prime order N ~ p, and P, Q = [k]P are given by random encodings (generic group model).
- **Oracles.** The adversary may additionally query (i) an action oracle CG(a, E') = [a]E' for a ∈ Cl(O) and E' ∈ Ell_p(O), with curves encoded by j-invariant, and (ii) a vectorization oracle V(E1, E2) = a with [a]E1 = E2.
- **Claim.** Every curve the adversary can submit is either (a) a curve built without reference to the group encodings: its own walks, where [a] is known, or any CM-method or public-data construction, where V may return an a unknown to the adversary but independent of k; or (b) a j-invariant computed from group encodings. Under random encodings, a type (b) j-invariant is uniform in F_p and lies in Ell_p(O) with probability ≤ |Ell_p(O)|/p = O(h_O/p) = O(p^{-1/2} log p).
- **Consequence.** After q queries, success ≤ O(q^2/N + q p^{-1/2} log p + 1/N). Hence q = Ω(N^{1/2}/log N) for N ~ p.
- **Where it fails.** The simulation fails exactly when the oracle acts on curves with level-𝔫 structure, 𝔫 | N (pairs (E', <P'>) or (E', P'), the ray-class fiber of IDEA-20260812-a3720a). Vectorizing (E, P) against (E, Q) in Cl_𝔫(O) returns the class of k in (O/𝔫)^*/O^*. That is ECDLP by definition, not a bridge.

*Outcome → disposition.*
- Checked simulator for level-1 (curve-only) oracles → closed_obstructed (theorem). The level-𝔫 case is recorded as "equivalent to ECDLP, not a reduction" (closed_known).
- A gap in step (b), meaning a curve-construction map from group encodings that lands in Ell_p(O) with probability far above h/p → names the bridge, and the lead stays open with that map as next_action.

### AUD-5

Not applicable.

### AUD-6

SO-ISO (class invariance) enters as the hypothesis of CSIDH/CRS-type vectorization-hardness assumptions. The class-group action itself is the hypothesis there, which is the reverse direction (a hardness assumption, not an attack). None found for ECDLP.


---

## LEAD-STR-class-representative-ic-selection

*Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost*  
Path: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/structure/LEAD-STR-class-representative-ic-selection.yaml`  
Disposition: **open_next_step**

> **next_action.step:** Run a preregistered ecbench IC study with three arms. (a) Floor instance solved on the floor. (b) Floor instance carried by verified 2-isogeny to the crater and solved there, transport charged. (c) Crater instance on the best of K isomorphic models, selected on calibration targets and measured on held-out targets. Use l=2 depth-3 volcanoes at 24-32 bits. Report charged S with the §5a 0/0.1/1 GAE band and the gap to matched rho as the distance remaining.

> **next_action.discriminates:** If (b) beats (a) by about 4% S net of transport, and (c) beats the default model on held-out targets, then representative selection is a measured IC improvement, a success under the iterative criterion. It is constant-factor only: IC/rho is 17-170x here. If held-out gains vanish, the 7.2% model effect and the 5.8% l=2 yield effect are factor-base sampling noise or a selection artifact, and the lead closes as measured.

forecloses: "heavy-tailed Semaev meters across an isogeny class"; "floor versus crater index calculus yield"; "walk to the crater before running index calculus"; "pick the isomorphic model with the best small-x factor base"; "large conductor gap changes index calculus cost"

### AUD-1

Not applicable (open_next_step).

### AUD-2

Not applicable (no obstruction).

### AUD-3

Not applicable.

### AUD-4

**Yes. A short identity, combined with an audit recomputation on the archived v2.1 data, decides the measured effects and the mean-yield arms of the queued three-arm study.**

*Theorem used.* KN-FIND-007 (`knowledge/findings/KN-FIND-007.md`, "Decomposition-yield conservation") covers bases D ⊆ G. Extend it to D ⊆ A = E(F_p) with G of prime order r and gcd(h, r) = 1 (h = #E/r). For R uniform in G, the mean number of representations equals N0(D)/r, where N0(D) is the number of m-tuples (or m-multisets) of D whose sum lies in G. Equivalently, it counts tuples whose cofactor classes [r]P_i sum to 0 in C = A/G. crypto `src/cryptanalysis/ic_boundary.rs` already implements this ceiling as `exact_decomposition_ceiling` ("the summands' cofactor classes cancel") but does not use it to explain yield. The binary-scope LEAD-ICB-cofactor-torsion-quotients already applies Sylow coprimality to cofactor quotients ("every full-translation homomorphic cofactor quotient reduces to the order-l projection rho already uses"; "the production 2-torsion census adds 0 relations"). That is consistent with this audit: cofactor classes decide admissibility, not extra relations. The new part here is narrower: the prime-field volcano level, model and horizontal effects are this accounting.

*Corollary for the measured pipeline.* The pipeline is `prime-abscissa:size=32` with `mitm:negation_folded=1`. Its table is `PairTable::build_negation_folded`, which includes "plus its own double", i.e. 2P_i. With F = 32 abscissae and classes uniform on C, the expected N0 up to sign is (F(F−1) + F·|C[2]|)/h. The doubles 2P_i land in G exactly when 2c = 0. On an l = 2 volcano, crater and levels 1–2 have full rational 2-torsion (`classes/*/curves.jsonl`: n2 = 2) and the floor is cyclic (n2 = 1), so |C[2]| = 4 versus 2. Predicted floor/crater ratio (F+1)/(F+3) = 33/35 = 0.943. For l = 3 classes |C[2]| does not change, so the predicted ratio is 1.

*Audit observations* (scripts and outputs under `/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/audit/n0check/`; they mirror `prime_factor_base` and `build_negation_folded` as read in crypto `src/cryptanalysis/ic_boundary.rs`):
1. `n0.py` → `n0_out.txt`: the exact N0 for all 7,760 archived curve-models. l = 2 classes have crater mean about 280 and floor mean about 264 at h = 4, matching (992+128)/4 and (992+64)/4. Per-class predicted floor/crater lies inside the archived 95% CI for 28/28 classes (archived values from `analysis/class-*.json`, metric `relation_yield`).
2. `residual.py` → `residual_out.txt`: per-run yield (`relations_found/targets_tried` from `sessions/<class>/spec/records.jsonl.gz`; `spec-r2` for l2-s1002 per README "Interrupted session") divided by the curve-model's predicted rate 2·N0/r:
   - l = 2 geometric-mean floor/crater: raw 0.9417 → normalised 0.9983;
   - l = 3: raw 1.0062 → 1.0046;
   - crater isomorphic-model heterogeneity (Cochran Q on log rates, Poisson variance), all classes: raw Q/df 1.539 → normalised 0.995; h > 1 classes: raw 1.612 → 0.994; h = 1 classes: 0.999 raw, 0.999 normalised.
   - The three h = 1 classes (l3-s1009/1013/1014) have N0 constant across models (CV 0). Their archived model-effect permutation p-values are 0.4733, 0.1514 and 0.7346 (`analysis/class-l3-s1009.json`, `-s1013`, `-s1014`). Every h > 1 class has p ≤ 0.0205 except l3-s1007 (h = 2, p = 0.0865, exact N0 CV 0.030).
   - Absolute check: observed/predicted crater rate is 0.967–1.001 by class (common scale, not level-dependent).
3. Interpretation (conditional on the uniform-target model and on the code reading above): N0 predicts the H1 ℓ = 2 level effect (0.942), the H4 isomorphic-model effect (τ 7.2%) and the horizontal effect to within the Poisson noise of the archive. No residual level or model effect survives normalisation in this data. The README's mechanism prediction ("the ℓ-power torsion changes between levels") tested the wrong group. The relevant quantity is |E(F_p)[2]|, which explains why `l3-s1011` showed no deficit.

*What it decides.*
- **h = 1 (every deployed prime-order curve: P-192, P-224, P-256, P-384, secp256k1).** C is trivial, so N0 = |D|^2 minus sum collisions for every model and every isogenous curve. Mean yield is the same by proof (KN-FIND-007), so arms (a)–(c) have zero mean-yield effect. Coverage and rank, and hence charged S, which stops at full rank, depend on repeated sums (the additive energy of the base). That part is not proved. It is bounded by the repeated-sum count, and the measured model effect at h = 1 is null (p = 0.4733 / 0.1514 / 0.7346). So: mean, proof; coverage/rank, measured null at h = 1.
- **h > 1.** The lever is real but has the form ΔN0/N0 = O(|C[2]|/F) for level choice, and O(1/F) for model choice (multinomial class-count fluctuation). It vanishes at the family optimum F ≈ #E^{1/3}: transport gain 2/(F+3) falls below the 1.3% transport charge for F ≳ 150. Its a-priori selector is max N0, computable in O(F^2) additions with no calibration targets, so arm (c)'s held-out question ("selection artifact") does not arise. A base confined to G (`PrimeProjectedAbscissaBase`; "LEAD-19: cofactor-projected and subgroup-only bases" in ic_boundary.rs) raises N0 by up to the index h and should dominate any representative choice. → Proposed (single disposition): **keep open_next_step**. Rewrite next_action as (i) "max-N0 model versus subgroup-only base at matched F on h > 1 curves, yield normalised by N0", and (ii) for h = 1, a target-free repeated-sum (coverage) count per representative. Add the h = 1 mean-yield proof to the lead text, and narrow forecloses to "mean IC yield differs across an isogeny class or model at cofactor 1". No ATLAS lead owns subgroup-only bases (grep of ATLAS.md for cofactor-projected|subgroup-only|LEAD-19 returned nothing), so closed_dominated is not available yet.
- **Graph-wide study (`problems/isogeny-graph-wide-relation-solver.md`, lead evidence).** Its protocol scopes "fixed prime-order isogeny classes" (crypto-autoresearcher `research/isogeny_relation_yield_scan_20261016/PROTOCOL-original-draft.md` line 10). So h = 1 and KN-FIND-007 applies directly: the mean (all-target) ordered/multiset yield is identical at every one of the 2,306 vertices for equal base size. Only coverage (useful-target fraction, governed by repeated 3-sums) and useful rank remain open. Coverage has an exact target-free form, #distinct 3-sums/N, computable per vertex without discovery or confirmation target streams. Rank is not covered by this identity. Cross-family note: LEAD-TRF-teske-secret-isogeny-trapdoor's next step (EXP-ECTD-0cf008 on the same P29 pairs) is decided in mean by the same identity.

*Outcome → disposition (if the Coordinator wants a confirmatory run instead of accepting the proof).* Run arm (c) on h = 1 curves only. Model τ at null → closed_obstructed. A surviving model τ at h = 1 would contradict the identity and point to a code-path difference (for example, table key collisions), not to a curve effect.

### AUD-5

Not applicable.

### AUD-6

SO-TORS generative use, recorded here because this is where it acts. gcd(h, r) = 1 coprimality is exactly the hypothesis of `exact_decomposition_ceiling`. The l-primary quotient A/G is then a design input: choose base points whose classes cancel, or confine the base to G. This is the generative reading of the torsion-coprimality obstruction for IC.


---

## LEAD-STR-curve-generation-provenance-seeds

*Manipulated generation of standard curves (NIST P-curve seeds, Brainpool, BN, rigidity)*  
Path: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/structure/LEAD-STR-curve-generation-provenance-seeds.yaml`  
Disposition: **exhausted_at_scale** (kind: measured)

> **obstruction.statement:** All ten NIST prime-field seeds are explained (about 30 bits of freedom per curve). Every public weak-class screen run on all 21 published and omitted classes found no anomaly and no rule separating them: exact CM field, class number <= 2000 (Kimura list), conductor, embedding degree, twist factors, invalid-curve surface, rational isogenies of odd degree <= 10,000, the ANSI A.3.2 gates, and 21 preregistered features. So a hidden weak class would need density at least about 2^-30 among prime-order curves and be invisible to all of these. The skip rule itself is historical and has no bearing on ECDLP.

> **revisit_when:** The historical generator code or logs are recovered, or a new publicly testable weak class of density at least 2^-30 is named.

forecloses: "NIST P-256 backdoor via the seed"; "skipped seed candidates reveal a hidden weak class"; "Brainpool or BN parameters were manipulated"; "count rejections in verifiably random generation"

### AUD-1

**Not fired (near).** crypto-autoresearcher `problems/nist-seed-selection-rule-unexplained.md` (in delta, "Last updated: 2026-10-24") records two acquisitions:
- the 17 November 1997 X9.62 draft, which "contains seven published prime-field examples and no candidate decision log";
- ECPP V3.4.1 period certificate-search source, where "no failed prime input or linkage to the original generator has been established".

Neither is "the historical generator code or logs". No new weak class of density ≥ 2^-30 is named in KRMAP.md or the delta. Watch item: if the ECPP replay labels an omitted order composite, that would explain the skip rule. It still bears on provenance only, not on ECDLP.

### AUD-2

**Over-reach found.**
1. forecloses "Brainpool or BN parameters were manipulated" is not covered. The statement's scope is "All ten NIST prime-field seeds ... all 21 published and omitted classes". No Brainpool or BN evidence path is cited, though the mechanism mentions "verifiability and rigidity of other families". Proposed: drop the phrase or add the Brainpool/BN audit evidence.
2. Cohort scope: the same problem file now states "69 seed positions with at least one qualifying root branch ... 10 published and 59 unpublished". The screens ran on 21 classes. Proposed: amend the statement to "the 21 classes (10 published + 11 named omitted); the 69-position cohort is unscreened". Disposition unchanged.

### AUD-3

**A short proof can replace the inferential half** (the "density at least about 2^-30" sentence). The measured half (null screens) stays measured.

*Lean target candidate:* Let H: S → X be uniformly random with |S| ≤ 2^b, and C ⊆ X with |C| = δ|X|. Then Pr[∃ s ∈ S, H(s) ∈ C] ≤ 2^b·δ. Corollary: a designer limited to the ≈2^30 seed choices recorded in the statement ("about 30 bits of freedom per curve") reaches a class C with probability ≥ 1/2 only if δ ≥ 2^{-31}.

This changes no disposition. It turns the density bound from prose into a checkable lemma (union bound, SHA-1 modelled as a random function).

### AUD-4

Not applicable.

### AUD-5

Not applicable.

### AUD-6

Not a standing obstruction of this family. A theory taking 'designer freedom 2^b' as a hypothesis is the BADA55 / 'manipulable curve generation' model (Bernstein et al.). It is literature already reflected in the mechanism. None found beyond it.


---

## LEAD-STR-endo-scalar-action-generic

*Endomorphism-augmented generic and witness-lattice attacks on a prime-order subgroup*  
Path: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/structure/LEAD-STR-endo-scalar-action-generic.yaml`  
Disposition: **closed_obstructed** (kind: theorem)

> **obstruction.statement:** For G of prime order N, End(G) = Z/N, so every endomorphism-image oracle is simulable by group operations and Shoup's bound applies (KN-FIND-b7e091, EV-GGM-79e710, DEC-20260804-3b4258). Augmenting the witness lattice with r eigenvalues leaves the index at N and the meet-in-the-middle exponent at 1/2 (H-ENDO-001). The one EV-ENDO-001 contradiction (first minimum exactly 1 on the J0 cells, by Vieta 1 + lambda_2 + lambda_3 = 0) is a certificate-void k-independent vector. It does not touch the exponent. Scope: any prime-field or binary curve, any size, prime-order subgroup.

> **revisit_when:** A proposed oracle is shown not to be GGM-simulable (it returns field data or curve data, resource R1/R2 in DECOMPOSITION.md, not a group element).

forecloses: "add endomorphism images to the oracle to beat sqrt(N)"; "endomorphism-augmented witness lattice for ECDLP"; "use phi(P) and phi(Q) as extra relations in a generic attack"; "eigenvalue lattice reduction recovers k"

### AUD-1

**Not fired in substance.** The trigger asks for an oracle shown not to be GGM-simulable, i.e. one that returns field or curve data. The delta's KN-FIND-7e2b94 (`knowledge/findings/KN-FIND-7e2b94.md`) studies the p-adic point section s_tor, which returns Q_p coordinates (field data). On <P> it is "the unique homomorphic ... section", and "s_tor carries the discrete-log relation s_tor(Q) = [d]s_tor(P) isomorphically into E^(Q_p)[n], no easier". A homomorphism between cyclic groups of prime order is fixed by the image of one generator, so it is GGM-simulable. KN-FIND-3c7e19 covers anomalous curves only, and KN-FIND-c71e5d covers F_p^* only. These belong to LEAD-TRF-padic-canonical-section (SO-PADIC), not here.

### AUD-2

**Over-reach in the constant, not in the exponent.** The statement reads "every endomorphism-image oracle is simulable by group operations and Shoup's bound applies ... Scope: any prime-field or binary curve".
- Simulating φ(X) = [λ]X costs Θ(log N) group operations. If φ-queries are free, the correct generic bound is Ω(sqrt(N/k)) with k = ord_N(λ) (Duursma-Gaudry-Morain; it matches KR-RHO-482ed3's sqrt(m) on Koblitz curves). The exponent 1/2 survives, as the statement says, but "Shoup's bound applies" over-claims in binary scope.
- Over F_p, this audit's CM construction gives a free degree-2 φ with k = h ≈ log2 N, so the free-query lower bound weakens there too, to Ω(sqrt(N/log N)).

Proposed: amend to "Ω(sqrt(N/ord_N(λ))) with free φ-queries; exponent 1/2 in all cases".

### AUD-3

Kind is theorem. A Lean target is still proposed for the precise form:

*In the generic group model on a cyclic group of prime order N, let the adversary hold a group-operation oracle and a free oracle φ(X) = [λ]X, with λ of multiplicative order k. Then any algorithm making q queries outputs log_P Q with probability ≤ c·k·q^2/N + 1/N.*

Proof idea: each encoding is a linear polynomial a + bK. φ multiplies by λ, so collisions among the ≤ q·k implicit polynomials are bounded by Schwartz–Zippel.

### AUD-4

Not applicable.

### AUD-5

Not applicable.

### AUD-6

SO-ENDO (End(G) = Z/N). Theories that take the scalar action as a hypothesis:
- GLV/GLS (known-scalar multiplication);
- DGM orbit rho when ord_N(λ) is small;
- Frobenius/automorphism-invariant factor bases in IC (KR-IC-b0fcda, KR-IC-955fd6).

New: on the CM-constructed prime-field family (h = ord_N(λ) ≈ log2 N), IC can use λ as known column coefficients with no per-step canonicalisation, while rho cannot use it cheaply. This is the proposed NEW LEAD.


---

## LEAD-STR-glv-gls-isogeny-loop-scalar-mult

*GLV/GLS and isogeny-loop endomorphisms, neighbour-model routing (known-scalar multiplication)*  
Path: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/structure/LEAD-STR-glv-gls-isogeny-loop-scalar-mult.yaml`  
Disposition: **closed_obstructed** (kind: proof)

> **obstruction.statement:** These speed up known-scalar multiplication only. A rho step is one group addition, and a non-unit loop endomorphism acts as lambda of multiplicative order about r, so its orbits are the whole group and it cannot form rho classes (RESEARCH_ISOGENY_LOOP_GLV.md §4.2). On random challenge curves the cheapest loop costs 20-93x the doublings it would save (h about sqrt q). On Koblitz curves the only loop is tau. Measured scalar-multiplication gains (chain GLV-2 1.52x, neighbour a=-3 route 3.07% one-shot on BADA55-VPR-224) are real and outside ECDLP cost.

> **revisit_when:** An ECDLP algorithm whose dominant cost is variable-base scalar multiplication, not additions, is in use. IC relation sampling with fresh aP+bQ per candidate would qualify if not done incrementally.

forecloses: "isogeny-loop endomorphism speeds up ECDLP"; "GLV decomposition helps Pollard rho"; "route kP through an isogenous neighbour with a=-3"; "4-dimensional GLV-GLS for discrete logs"

### AUD-1

**Not fired.** The trigger needs an ECDLP algorithm dominated by variable-base scalar multiplication, for example IC relation sampling with fresh aP+bQ not done incrementally. crypto `src/cryptanalysis/ic_boundary.rs` module doc, `_walk` row: "targets come from a 16-jump r-adding walk with tracked coefficients, one addition each, instead of two scalar multiplications each". Every prime-field Table B recipe in `docs/ic/LEADERBOARD.md` is "folded, walked". Unverified: the graph-wide study's target preparer, which draws (alpha, beta) coefficient streams. It is not an ECDLP cost claim.

### AUD-2

**Over-reach found.**
1. "a non-unit loop endomorphism acts as lambda of multiplicative order about r, so its orbits are the whole group" is false for Koblitz τ (order m; KR-RHO-482ed3). The statement's own "On Koblitz curves the only loop is tau" does not say that τ does form rho classes. It is also false over F_p in general: this audit's CM curves have a degree-2 endomorphism of order h ≈ log2 N (`/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/audit/n0check/cm_verify_out.txt`). The claim holds for the random challenge curves measured (h ~ sqrt q). Proposed scope: "deployed and random challenge curves".
2. forecloses "GLV decomposition helps Pollard rho" is ambiguous. On j=0 curves (secp256k1) the GLV endomorphism is a unit (ζ_3) and does help rho by sqrt 3 (KR-RHO-0528e7; cryptanalysis `docs/sixclass-20261024/assessment.md`). Proposed rephrase: "GLV scalar decomposition or a non-unit loop endomorphism helps rho beyond sqrt(|Aut|)".

### AUD-3

Not applicable (kind proof).

### AUD-4

Not applicable.

### AUD-5

Not applicable.

### AUD-6

SO-ENDO, as in LEAD-STR-endo-scalar-action-generic. Theory that takes 'a cheap λ' as hypothesis: GLV itself. None new for ECDLP beyond the IC orbit-column lead.


---

## LEAD-STR-isogeny-class-generic-invariance

*Generic (rho, BSGS) ECDLP cost across an isogeny class and across volcano levels*  
Path: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/structure/LEAD-STR-isogeny-class-generic-invariance.yaml`  
Disposition: **closed_obstructed** (kind: theorem)

> **obstruction.statement:** Isogenous curves have F_p-isomorphic prime-order subgroups (T1), and rho and BSGS depend only on the group order and the automorphism group. The automorphism group is a class invariant except at the j=0/1728 crater. Measured with controls: the crypto 26-bit census of three whole volcanoes (403,168 runs, every instance carried by verified Velu maps) found 33/35 level ratios equivalent under TOST (±5% rho/BSGS), 0 different, and no curve effect beyond the isomorphic-control spread. v2.1 rho floor/crater is 1.004 [0.990, 1.016]. 40- and 48-bit volcano-rho studies found no level effect. Transport is exact and costs at most 1.3% of a solve.

> **revisit_when:** A generic-model algorithm whose cost depends on more than the group and Aut, or a level-dependent change in step cost (field-arithmetic model cost). The latter is a constant and belongs to LEAD-STR-class-representative-ic-selection.

forecloses: "volcano level changes Pollard rho cost"; "endomorphism-ring depth makes ECDLP easier"; "walk the volcano to a cheaper curve for rho"; "read the volcano level off the group structure to find a weak curve"; "conductor of End(E) affects generic ECDLP"

### AUD-1

Not fired. No generic-model algorithm depending on more than the group and Aut, and no level-dependent step-cost measurement, appears in the delta (`atlas/delta.txt`), KRMAP.md, LEADERBOARD.md or FRONTIER.md. The only level-dependent cost measured anywhere in the family is the IC yield, which this audit attributes to |E(F_p)[2]| (LEAD-STR-class-representative-ic-selection AUD-4). It is outside this lead's generic scope.

### AUD-2

**Mild over-reach.**
1. forecloses "endomorphism-ring depth makes ECDLP easier" has no "generic" qualifier, unlike "conductor of End(E) affects generic ECDLP". Two cases contradict the unqualified phrase:
   - Over F_p, IC mean yield does depend on level through |E(F_p)[2]| at relative size 2/(F+3) (audit observation; it vanishes as F grows and is 0 at h = 1).
   - Over F_{2^m}, the Koblitz crater carries τ (6.36x; LEAD-STR-koblitz-volcano-descendants).
2. The statement's exception list ("except at the j=0/1728 crater") omits the Koblitz crater.

Proposed: add "for generic methods over F_p" to the phrase, and add the Koblitz crater to the exception list. No disposition change.

### AUD-3

Not applicable (kind theorem; T1 is elementary).

### AUD-4

Not applicable.

### AUD-5

Not applicable.

### AUD-6

SO-ISO. Theories that take isogeny-class invariance as a hypothesis:
- JMV random self-reducibility (worst case to average case within a level);
- isogeny-based hardness assumptions.

The theory that exploits its failure is GHS/generalised GHS with isogeny walks over composite-degree binary fields (KR-IC-791cb7, LEAD-TRF-ghs-binary-composite). It is out of prime-field scope. Over F_p: rational small torsion (|E(F_p)[2]|, |E(F_p)[3]|) is not a class invariant, and it enters IC yield through diagonal sums. That effect is O(1/F) (this audit).


---

## LEAD-STR-isogeny-transport-preprocessing

*Multi-target and preprocessing tables shared across an isogeny class*  
Path: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/structure/LEAD-STR-isogeny-transport-preprocessing.yaml`  
Disposition: **closed_obstructed** (kind: proof)

> **obstruction.statement:** Transporting each target to the table's curve costs O(1) isogeny evaluations and reduces "M targets on M isogenous curves" exactly to M targets on one curve. That is the known single-curve multi-target and Bernstein-Lange frontier, which it ties and cannot beat (IDEA-20260807-406fef, IDEA-20260807-a2fb45). Transporting the table instead is dominated by transporting the targets, and was measured to lose against rebuild for baby-step tables at every odd l from 3 to 31, 1.5x to 21x with no crossover (EV-ENDO-10109d N4). It also needs a known path, and finding one to a specified curve is vectorization.

> **revisit_when:** A preprocessing object whose value is not a function of the (point, scalar) pairing, so not carried by target transport, is shown to beat the single-curve Bernstein-Lange frontier.

forecloses: "transport a precomputation table across the isogeny class"; "multi-target attack over isogenous curves"; "Bernstein-Lange table reused on isogenous curves"; "amortise preprocessing over an isogeny class"

### AUD-1

Not fired. No preprocessing object whose value is not carried by target transport appears in the delta. The KR-RHO-ea34b8 / Bernstein-Lange frontier is unchanged in KRMAP.md.

### AUD-2

No over-reach found. The proof part (target transport reduces M curves to one curve) carries the closure. The table-transport measurement at p = 50021/60013 is supporting only. 'Multi-target attack over isogenous curves' is within the proved reduction.

### AUD-3

Not applicable (kind proof).

### AUD-4

Not applicable.

### AUD-5

Not applicable.

### AUD-6

SO-MULTI enters through the Kuhn-Struik / Bernstein-Lange frontier. The theory that takes amortisation as its hypothesis is the precomputation model of KR-RHO-ea34b8, already used. None new.


---

## LEAD-STR-isogeny-walk-weak-neighbour

*Walk or construct isogenies from a deployed curve to find a weak neighbour*  
Path: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/structure/LEAD-STR-isogeny-walk-weak-neighbour.yaml`  
Disposition: **closed_known** (kind: literature)

> **obstruction.statement:** Transfer weaknesses (MOV embedding degree, anomalous trace, CM field, group order) are isogeny-class invariants, so no neighbour can be weaker by them (KR-RHO-53c89f, KR-RHO-755e35, DECOMPOSITION.md T4). Isogenous curves are equally hard for generic methods. Reproduced: the P-256 million-model walk found no structural-screen hit, and P-192 / P-224 large-degree isogenies found no weakness. A huge-degree self-isogeny of secp256k1 is an endomorphism, so it acts as a scalar on G.

> **revisit_when:** A weakness that is not an isogeny-class invariant is exhibited (see LEAD-STR-class-representative-ic-selection, where only constant-factor IC variation is measured).

forecloses: "isogeny walk from P-256 finds a weak curve"; "largest prime degree isogeny weakens secp256k1"; "isogenous neighbour with small embedding degree"; "search the isogeny class for an anomalous curve"

### AUD-1

Not fired. No non-invariant weakness is exhibited. The trigger points to LEAD-STR-class-representative-ic-selection. This audit shows its measured variation equals the cofactor-class count N0, which is exactly constant at h = 1. P-192, P-224, P-256 and secp256k1 all have h = 1, so the referenced variation is identically zero on every curve this lead walked from.

### AUD-2

**Scope gap (wording).** "Transfer weaknesses (MOV embedding degree, anomalous trace, CM field, group order) are isogeny-class invariants, so no neighbour can be weaker by them" is correct over F_p for the listed invariants. It does not extend to cover/Weil-descent susceptibility over F_{2^N} with N composite, which is not a class invariant (KR-IC-791cb7; IDEA-20261024-7be1c6 in the delta studies isogeny-walk reachability of a floor cover). The forecloses phrases name prime-field curves, so nothing is blocked in practice. Proposed: add "over F_p" to the statement.

### AUD-3

Not applicable (kind literature).

### AUD-4

Not applicable.

### AUD-5

Not applicable.

### AUD-6

SO-ISO, as in LEAD-STR-isogeny-class-generic-invariance. The generative theory is GHS isogeny walking (binary composite only).


---

## LEAD-STR-jmv-random-self-reduction

*Jao-Miller-Venkatesan isogeny-expander random self-reduction within a level*  
Path: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/structure/LEAD-STR-jmv-random-self-reduction.yaml`  
Disposition: **closed_known** (kind: literature)

> **obstruction.statement:** JMV is a hardness-equivalence (average equals worst case within a level), not a speedup. The program re-derived its cost as a stated deterministic model (KN-FIND-f293c6, EV-JMV-05a150). The required eigenvalue separation is vacuous at q=2^256 for delta <= 0.5 and non-vacuous only at delta=2.0. The modelled reduction falls below rho only above 192 bits there. It moves no ECDLP cost. Point-level Elkies-walk self-reduction (IDEA-20260807-631e80) is the same mechanism.

> **revisit_when:** A use of the self-reduction as a subroutine of an attack (not a hardness proof) is proposed with a cost below rho.

forecloses: "JMV random self-reduction gives an attack"; "expander isogeny walk re-randomises ECDLP to an easier curve"; "dlog cost is constant within a level so pick the best level"

### AUD-1

Not fired. No attack using the self-reduction as a subroutine appears in the delta.

### AUD-2

**The trigger is not satisfiable as written.** revisit_when says "A use of the self-reduction as a subroutine of an attack (not a hardness proof) is proposed with a cost below rho". The reduction maps any instance in a level to random instances in the same level. An attack below rho that uses it would therefore already contain an average-case solver below rho for that level. So the trigger reduces to "an average-case ECDLP algorithm below rho on some level exists", which is a stronger and simpler statement. Proposed: rewrite revisit_when to that.

### AUD-3

Kind literature, but the closure's quantitative content is a cost model (KN-FIND-f293c6). *Lean target candidate (short):* if A solves ECDLP on a δ-fraction of curves of one level in time T, then the JMV walk solves every curve of that level in expected time O((T + W)/δ), W being the walk cost. Conversely, any algorithm built from the reduction plus oracle calls to A costs at least T per call. Hence no attack below the average-case cost can come from the reduction. This replaces the 'vacuous at q=2^256' cost model as the reason for closure.

### AUD-4

Not applicable.

### AUD-5

Not applicable.

### AUD-6

SO-ISO. JMV is itself the theory that takes class invariance as hypothesis. None new.


---

## LEAD-STR-koblitz-volcano-descendants

*Curves below a binary Koblitz curve in its volcano (ECC2K-130, K-163, K-283, m=37..83)*  
Path: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/structure/LEAD-STR-koblitz-volcano-descendants.yaml`  
Disposition: **closed_obstructed** (kind: measured)

> **obstruction.statement:** At m=37 and m=41, with negation, every level costs the same (KW p=0.76, each level within ±3% of the crater by TOST). Only the crater has a cheap non-trivial endomorphism (tau, degree 2), worth 6.36x steps [6.20, 6.53], and no curve beats crater plus Frobenius (Holm p=1.0 on 127 and 91 curves). Below the crater the least non-integer endomorphism degree is 121,046 (ECC2K-130 floor) or 73,324,526 (m=83 floor), so using it makes rho 45x to 3,000x slower. At m=83 IC floor yield differs by at most 0.014%, and Frobenius atlases cost 137-513x the best chart.

> **revisit_when:** An explicit K-163 / K-283 floor map is persisted (problems/koblitz-vertical-isogeny-maps-not-persisted.md) and a floor factor base beats the crater tau-orbit base in charged S. Or the m=51 replication passes its A/A gate and shows a level effect.

forecloses: "descend from ECC2K-130 to a weaker floor curve"; "K-163 conductor floor is easier than the Koblitz curve"; "isogenous curve to a Koblitz curve better for rho"

### AUD-1

Not fired. crypto-autoresearcher `problems/koblitz-vertical-isogeny-maps-not-persisted.md` ("Status: open", "Last updated: 2026-10-14") and `problems/m51-deep-volcano-levels-not-constructed.md` ("Status: open", "Last updated: 2026-10-13") are not in `atlas/delta.txt`. No K-163/K-283 floor map and no m = 51 A/A pass exist.

### AUD-2

**Over-reach found.** "every level costs the same" is measured at m = 37 and m = 41 (log2 r about 35–39). Yet forecloses "K-163 conductor floor is easier than the Koblitz curve" applies it to the deployed 163-bit curve. That is a small-scale measured null used as a closure at deployed scale. The conclusion is still right, because a theorem covers it (AUD-3). Proposed: switch the closure to the theorem and keep the measurements as controls.

### AUD-3

**Yes. A short proof replaces the measured closure for rho, and explains the IC null.**

*Lemma 1 (norm bound; Lean target).* Let K = Q(sqrt(−7)), O_K = Z[ω] with ω = (1+sqrt(−7))/2, and O_f = Z + f·O_K with f odd. Then min{N(α) : α ∈ O_f \ Z} = (7f^2 + 1)/4. Proof: α = a + f·b·ω with b ≠ 0, so N(α) = (a + fb/2)^2 + 7f^2b^2/4 ≥ 1/4 + 7f^2/4. This reproduces the statement's measured values exactly: f = 263 → 121,046 ("ECC2K-130 floor") and f = 6473 → 73,324,526 ("m=83 floor"). The conductor values come from cryptanalysis `ecc2k130/research/volcano-m83/README.md` lines 21–26 ("nearest conductor prime | 263, split ... | 6473, inert"; "min noninteger endomorphism degree on the floor | 121,046 | 73,324,526").

*Lemma 2 (Lean target).* Let m be prime and E' be F_{2^m}-isogenous to a Koblitz curve but not on the crater. Then E' is not defined over F_2: otherwise its 2-power Frobenius would put Z[τ] = O_K inside End(E'). F_{2^m} has no intermediate subfield, so E' has no subfield Frobenius. With T1 and the orbit lemma of LEAD-STR-small-cm-disc-nonunit-endo, generic rho on E' is no cheaper than negation rho, and the crater with τ is strictly cheaper by sqrt(m). For composite m (the m = 51 study), a floor curve may be defined over F_{2^d}, d | m, d < m, and then carries an orbit of size 2m/d < 2m. The crater stays strictly best.

*IC null (interpretation).* Ordinary binary curves have |E(F_{2^m})[2]| = 2 at every level, and odd-degree vertical isogenies preserve the 2-primary part. So the diagonal term found in LEAD-STR-class-representative-ic-selection is level-constant, consistent with "IC floor yield differs by at most 0.014%".

Proposed: obstruction kind measured → "theorem (Aut part, Lemma 2) + cost model (non-unit part)". The claim that a floor endomorphism of degree ≥ 121,046 is too expensive to use still rests on LEAD-STR-small-cm-disc-nonunit-endo's cost model. Lemma 1 only fixes the degree. Measured TOST results stay as controls. Disposition unchanged.

### AUD-4

Not applicable.

### AUD-5

Not applicable.

### AUD-6

SO-FROB / SO-ENDO. The theory that takes 'only the crater has τ' as a hypothesis is the Frobenius-invariant factor base (KR-IC-b0fcda) on the crater. It is already the best chart. None new.


---

## LEAD-STR-p192-class-cm-relations

*P-192 isogeny class, smooth principal CM relations and loops*  
Path: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/structure/LEAD-STR-p192-class-cm-relations.yaml`  
Disposition: **closed_obstructed** (kind: theorem)

> **obstruction.statement:** Any CM relation is an endomorphism and acts as a scalar on the prime-order subgroup (H-ENDO-001). A cheap one gives only GLV-type scalar multiplication (LEAD-STR-glv-gls-isogeny-loop-scalar-mult), and its orbits are too large for rho classes. Navigation of the class is generic-cost neutral (T1). Measured: all 103 emitted relations in the L <= 2^48 box are scalar (census not provably complete), and the crypto P-192 weak-curve review found no structural weakness or speedup.

> **revisit_when:** A non-isogeny-invariant weakness is found in any class (would make navigation matter).

forecloses: "P-192 isogeny class has a weak curve"; "smooth principal CM loop on P-192"; "non-scalar CM relation in the P-192 class"

### AUD-1

Not fired. No non-isogeny-invariant weakness is found in any class. The only measured candidate (IC representative effects) equals the cofactor-class count N0, which is constant at h = 1. P-192 has h = 1 (this audit; LEAD-STR-class-representative-ic-selection AUD-4).

### AUD-2

No over-reach. The theorem (CM relations are endomorphisms, hence scalars) makes census completeness irrelevant. 'Census not provably complete' does not weaken the closure.

### AUD-3

Not applicable (kind theorem).

### AUD-4

Not applicable.

### AUD-5

Not applicable.

### AUD-6

SO-ENDO / SO-ISO. None found.


---

## LEAD-STR-safecurves-parameter-audit

*SafeCurves-style parameter audits (twist security, completeness, ladder, cofactor, transfer rows)*  
Path: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/structure/LEAD-STR-safecurves-parameter-audit.yaml`  
Disposition: **closed_known** (kind: literature)

> **obstruction.statement:** The criteria and verdicts are published (SafeCurves). The program's replications reproduce them, for example Ed448 base-point certificates and P-192 x-only singular-companion recovery on an unchecked low-level multiplier (EV-SCURVE-44f051, an implementation weakness, not ECDLP). The deliberately weak rows fall to known transfers (KR-RHO-53c89f). Most SCURVE hypotheses are Stage-0 arithmetic identities with no ECDLP content.

> **revisit_when:** A deployed row is found to violate a criterion that bears on ECDLP cost (rho size, transfer, CM), not only on implementation safety.

forecloses: "SafeCurves audit finds an ECDLP weakness in Curve25519"; "twist security breaks the discrete log"; "anomalous or MOV-weak standard curve"; "invalid-curve attack as an ECDLP speedup"

### AUD-1

Not fired. The delta's crypto `problems/nist-extension-twist-composite-cofactors.md` ("One NIST extension-twist composite cofactor remains unsplit") concerns factorisation of a degree-2 extension-twist order of P-256. That is a twist/implementation criterion, not a criterion bearing on ECDLP cost (rho size, transfer, CM).

### AUD-2

No over-reach found. The forecloses phrases match the literature scope.

### AUD-3

Not applicable (kind literature).

### AUD-4

Not applicable.

### AUD-5

Not applicable.

### AUD-6

Not a standing obstruction. None found.


---

## LEAD-STR-secp256k1-cm-class-audit

*secp256k1 CM structure (D=-3, j=0, h=1) and its isogeny class*  
Path: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/structure/LEAD-STR-secp256k1-cm-class-audit.yaml`  
Disposition: **closed_obstructed** (kind: theorem)

> **obstruction.statement:** The crater for D=-3 has one vertex (h=1), and secp256k1 is it. It already carries the maximal unit group (order 6). Every other curve in the class is lower in some volcano with fewer units, so by T1 and the automorphism-only rho ceiling no class member is cheaper for generic attack. The sextic twists have different orders and are not isogenous. The only ECDLP lever is the sqrt 6 constant (KR-RHO-0528e7). Genus-2 gluing and cover threads in the audit belong to the transfer/covers family.

> **revisit_when:** An IC method on j=0 curves beats rho with the sqrt 6 discount (see LEAD-STR-special-j-ic-semaev).

forecloses: "secp256k1 endomorphism breaks ECDLP"; "sextic twist of secp256k1 is weaker"; "Bitcoin curve CM weakness"

### AUD-1

Not fired. The trigger is "An IC method on j=0 curves beats rho with the sqrt 6 discount". crypto `docs/ic/LEADERBOARD.md` says "No row is below its reference". The new j=0 work in the delta (cryptanalysis `docs/sixclass-20261024/`) is a rho walk, measured slower than the default at toy scale.

### AUD-2

**Over-reach found.** forecloses "sextic twist of secp256k1 is weaker" is not covered. The statement shows only that "The sextic twists have different orders and are not isogenous". That proves their weakness cannot transfer to ECDLP on secp256k1. It does not prove the twists are not weaker; twist security is an implementation criterion (LEAD-STR-safecurves-parameter-audit). Proposed rephrase: "a sextic twist's weakness transfers to secp256k1 ECDLP".

### AUD-3

Not applicable (kind theorem).

### AUD-4

Not applicable.

### AUD-5

Not applicable.

### AUD-6

SO-ISO / SO-ENDO. None found.


---

## LEAD-STR-small-cm-disc-nonunit-endo

*Small |D_0| or a cheap non-unit endomorphism beyond the automorphism constant*  
Path: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/structure/LEAD-STR-small-cm-disc-nonunit-endo.yaml`  
Disposition: **closed_obstructed** (kind: theorem)

> **obstruction.statement:** A non-unit alpha of norm n acting as lambda on G has orbit size h = ord_N(lambda) with n^h >= (sqrt N - 1)^2, so h >= log N / log n (IDEA-20260901-6b63a4, an elementary proof). A rho class of size h costs about h evaluations of alpha to canonicalise, so the net factor is at most sqrt(h)/kappa with kappa about h times c(alpha) (IDEA-20260826-506ba2). On deployed curves |D_K| is large (endosweep). Only the units of D_0 in {-3, -4} give finite orbits at O(1) cost, and those are an isogeny-class invariant (DECOMPOSITION.md T4). Scope: ordinary prime-field curves, prime-order G.

> **revisit_when:** Someone constructs a prime-field curve where a norm-2 or norm-3 endomorphism has eigenvalue order near log_n N (the equality case, a prime-field Koblitz analogue) and a canonical orbit representative costs o(h) maps. Findings file NEW LEAD 1.

forecloses: "small CM discriminant makes ECDLP easier"; "class number one curves are weak beyond automorphisms"; "cheap endomorphism of degree 2 gives rho equivalence classes"; "endomorphism claw from small D_0"; "closed isogeny-graph walk gives an orbit invariant"

### AUD-1

**Not fired against the defined current state.** The construction clause would be met once this audit's computation (`cm_verify_out.txt`) is registered. The canonicalisation clause is not met.

The trigger reads "constructs a prime-field curve where a norm-2 or norm-3 endomorphism has eigenvalue order near log_n N ... and a canonical orbit representative costs o(h) maps".

*Construction.* Standard CM with D_K = −7 and α = ω = (1+sqrt(−7))/2 (norm 2):
- set ν = (α^h − 1)/(α − 1);
- require N = Norm(ν) prime;
- take Frobenius π = 1 + γν with small γ, requiring p = Norm(π) prime.

Then #E(F_p) = Norm(γ)·N, and α acts on the order-N subgroup as λ with λ^h = 1. The search is `/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/audit/n0check/cm_norm2c.py`, `cm_norm2d.py`; its loop label is h+1, so the true orders are the primes h listed below.

*Verification* (`/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/audit/n0check/cm_verify.py` → `cm_verify_out.txt`). For h = 17, 19, 23, 107, 283:
- N is a prime of h bits and p is prime (p of 19, 21, 25, 112 and 288 bits);
- the quadratic twist of y^2 = x^3 − 35x − 98 (j = −3375) over F_p has order p+1−t = Norm(γ)·N, checked on 8 random points per curve;
- one root of x^2 − x + 2 mod N has multiplicative order exactly h;
- cofactors are 8, 4, 4, 32 and 32.

Both roots correspond to degree-2 endomorphisms (α and ᾱ = 1 − α), so a degree-2 endomorphism with eigenvalue order h = log2 N exists. This is the equality case of the lemma n^h ≥ (sqrt N − 1)^2. Literature status: not checked in this audit; GLV 2001 already uses D = −7 degree-2 endomorphisms, but not with ord_N(λ) ≈ log N.

*Canonicalisation clause.* Still open. Each α application is a degree-2 rational map, costing roughly one affine addition, so naive canonicalisation costs about h maps.

### AUD-2

**Over-reach found (two items).**
1. The obstruction kind is "theorem", but only the orbit-size bound (h ≥ log N / log n) is a theorem. "A rho class of size h costs about h evaluations of alpha to canonicalise" is a cost model: no lower bound on canonicalisation is proved. The equality-case curves now exist (AUD-1), so the closure rests entirely on that cost model.
2. forecloses "cheap endomorphism of degree 2 gives rho equivalence classes" contradicts binary Koblitz τ (degree 2, KR-RHO-482ed3, 6.36x measured in LEAD-STR-koblitz-volcano-descendants). The statement scopes "ordinary prime-field curves", but the phrase does not. Proposed: add "over F_p, with enumeration canonicalisation".

### AUD-3

**Theorem part (Lean target candidate).** Let E/F_p be ordinary, α ∈ End(E) with deg α = n ≥ 2, and G ≤ E(F_p) cyclic of prime order N with α(G) ⊆ G and α|_G = [λ], λ ≠ 1, of order h. Then N divides Norm(α^h − 1) ≤ (n^{h/2} + 1)^2, so h ≥ 2·log(sqrt(N) − 1)/log n. The equality case is attained for n = 2 (AUD-1).

**Cost-model part (no short proof available).** Whether a canonical representative of an α-orbit can be computed with o(h) evaluations is open; this audit found no theorem. Proposed: change kind to cost_model for the net-speedup clause, and narrow revisit_when to the o(h) canonicalisation clause, since the construction exists. Disposition for deployed curves (large |D_K|, endosweep) unchanged.

### AUD-4

Not applicable (closed). See the NEW LEAD below for the IC consequence.

### AUD-5

Not applicable.

### AUD-6

SO-ENDO (orbit-size form). **A theory that takes the obstructing quantity as a hypothesis exists: IC with endomorphism-orbit columns.**
- A relation Σ c_j log P_j with P_j = α^e(S_s) has column coefficient λ^e. That is known once, so IC folds columns by the orbit size 2h with no per-step canonicalisation.
- Rho needs canonicalisation at every step, at cost about h maps, so it cannot use α cheaply.
- The obstruction quantity, "orbit size h ≈ log N with canonicalisation cost h", is therefore exactly the hypothesis under which IC gains and rho does not.

Cross-family flag: LEAD-ICB-frobenius-orbit-factor-base's statement "Prime-field phi-stable bases (EQIC) are bounded by the eigenvalue-subgroup order (at most 6)" assumes units only. On the constructed family the eigenvalue subgroup <λ, −1> has order 2h (566 at h = 283). Its "Rho gets the matching sqrt(2n) from the same automorphisms" does not hold over F_p.


---

## LEAD-STR-special-j-ic-semaev

*Special j (0, 1728, small height, Semaev degeneration locus) in Semaev and index-calculus systems*  
Path: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/structure/LEAD-STR-special-j-ic-semaev.yaml`  
Disposition: **open_next_step**

> **next_action.step:** On matched-order families (fixed N, as in MATCHED-ORDER-DESIGN.md), measure the first-fall degree, F4 solve time and complete charged IC cost S for S_3/S_4 decompositions on j=0 and j=1728 curves against generic-j curves. Use the automorphism-orbit factor base and a sham-curve null of the same support shape. Report the gap to matched rho with the automorphism discount applied to rho too.

> **next_action.discriminates:** An equal or higher charged S at matched N closes the lead: support reduction is cost-invisible, consistent with the callgrind j=0 order-6 base costing 4% more Ir. A lower S that survives the sham null and exceeds the sqrt(|Aut|) rho discount is a measured IC improvement on special-j classes, which include secp256k1.

forecloses: "j=0 Semaev polynomial is sparser so index calculus is faster"; "Semaev degeneration divisor on the j-line"; "small-height j makes decomposition easier"; "automorphism-quotient coordinate factor base on special-j curves"

### AUD-1

Not applicable (open_next_step).

### AUD-2

Not applicable (no obstruction).

### AUD-3

Not applicable.

### AUD-4

**Three short results narrow the queued experiment.**

(a) *Support lemma (Lean target; replaces EV-ENDO-e8d3e5's "structural fact").* With S_3 = (x1−x2)^2 x3^2 − 2((x1+x2)(x1x2+a) + 2b)x3 + (x1x2 − a)^2 − 4b(x1+x2):
- for a = 0, every monomial has total degree ≡ 1 mod 3;
- for b = 0, every monomial has even total degree;
- the supports are 13 (generic), 9 (a=0) and 10 (b=0).

Checked in this audit with sympy (inline run; output "generic 13 ... j0 a=0 9 deg mod3 [1] ... j1728 b=0 10 ... deg mod2 [0]"). The support reduction is the automorphism action x ↦ ζx (resp. x ↦ −x) on the x-line, not an independent sparsity. So "support reduction" and "automorphism-orbit factor base" are one lever, and the sham-curve null of "the same support shape" cannot separate them.

(b) *Cofactor confound (from LEAD-STR-class-representative-ic-selection AUD-4).*
- Mean IC yield depends on h and |E(F_p)[2]|.
- y^2 = x^3 + ax (j=1728) always has the rational 2-torsion point (0,0), so |E(F_p)[2]| ≥ 2.
- y^2 = x^3 + b (j=0) has one iff b is a cube.

A matched-order design that fixes N but not h and |E(F_p)[2]| will show a spurious yield difference of the diagonal size computed there. Proposed change to next_action: fix h = 1, or normalise yield by the exact N0 of each base.

(c) *Cost-model ceiling (conditional).* For the prime-field MITM pipeline with an Aut-closed base, S_IC ∝ (r/A)^{2/3} with an unfolded table, or ∝ r^{2/3}/A with an Aut-folded table, against rho ∝ (r/A)^{1/2}. Hence j=0 can improve IC/rho over generic j by at most 3^{1/6} to 3^{1/2} (1.20–1.73), and j=1728 by at most 2^{1/6} to 2^{1/2}. Table B shows 13.5x at log2 r = 23.4 (`icv1-fp24-t1577-77336155`), growing with r.

*Outcome → disposition.*
- Measured special-j IC/rho improvement within that ceiling, after N0 normalisation → closed_known (KR-IC-955fd6: symmetries are a constant).
- Improvement above the ceiling → a support or degree effect beyond Aut accounting; stays open.

Coverage gap: H-STR-002 (status weakened; φ-invariant factor base on j=0 curves; EXP-STR-002/003/004; `problems/str002-support-verdict-missing-artifacts.md`, in delta) has no row in `knowledge/leads/ecdlp/coverage.tsv` (grep returned nothing). Proposed: add it to this lead's ledger_refs.

### AUD-5

Not applicable.

### AUD-6

Not closed. SO-QSP / SO-ALGFB are adjacent but not this family's.


---

## LEAD-STR-torsion-module-leak

*l-torsion (l != N) as a Galois/End module leaking k or attack cost*  
Path: `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/structure/LEAD-STR-torsion-module-leak.yaml`  
Disposition: **closed_obstructed** (kind: proof)

> **obstruction.statement:** Any statistic of the curve alone is k-independent by construction. Any homomorphic invariant from the prime-order group G to an l-primary group (l != N) is trivial (coprimality, IDEA-20260807-6eab6a). A non-homomorphic point statistic is a function of the encoding of Q. Using it is index calculus or a generic query, and partial information about k on the point costs more than it saves, by sqrt(M) (IDEA-20260811-8cf53a). Toy checks agree: the psi_5 factor-degree multiset does not change with k (H-TORS-3bed8a). Scope: prime-order G, any l != N.

> **revisit_when:** A point-dependent l-torsion statistic computable in o(sqrt N) correlates with k beyond a k-resampled null at matched curve.

forecloses: "division polynomial factorisation leaks the discrete log"; "Elkies Atkin split pattern as an ECDLP fingerprint"; "l-torsion Galois module carries information about k"; "Legendre symbol of psi_l at x(kP)"; "division polynomial statistics leak k"; "ell-torsion Galois module"; "Elkies Atkin split pattern"; "torsion translate norms"; "Legendre symbol of psi_ell at x(kP)"

### AUD-1

Not fired. No point-dependent l-torsion statistic with a k-resampled-null correlation appears in the delta. The CZLIFT findings (KN-FIND-3c7e19, KN-FIND-7e2b94, KN-FIND-c71e5d) concern p-adic sections and F_p^*, not l-torsion with l ≠ N, p.

### AUD-2

**Partial over-reach.** The proof covers (i) curve-only statistics (k-independent) and (ii) homomorphisms G → l-primary groups (trivial by coprimality). The third sentence ("A non-homomorphic point statistic ... Using it is index calculus or a generic query, and partial information about k on the point costs more than it saves, by sqrt(M)") is a classification plus a cost argument (IDEA-20260811-8cf53a), not a proof. Yet forecloses "Legendre symbol of psi_l at x(kP)" and "division polynomial statistics leak k" are non-homomorphic point statistics, so they rest on that argument. A theorem can cover them (AUD-3).

### AUD-3

**Kind is proof, but the non-homomorphic clause can be upgraded with a known character-sum theorem.**

*Lean target candidate:* for a nonconstant rational function f on E of degree d, a nontrivial multiplicative character χ of F_p^*, a cyclic subgroup G = <P> of prime order N and any additive character ψ of Z/N, |Σ_{k ∈ Z/N} χ(f([k]P)) ψ(k)| ≤ 2d·sqrt(p) + O(d). To be proved from the Weil bound for character sums on curves. Literature pointer, unverified (no path in the repositories was checked): Kohel–Shparlinski, ANTS 2000.

With f = ψ_l ∘ x (d = O(l^2)), every Fourier coefficient of k ↦ χ(ψ_l(x(kP))) is O(l^2/sqrt(N)). So the Legendre-of-psi_l bit is uncorrelated with every character of k up to that bound. This turns the forecloses phrase into a theorem consequence for d = o(sqrt p).

### AUD-4

Not applicable.

### AUD-5

Not applicable.

### AUD-6

SO-TORS. Theories that take the coprimality (trivial homomorphisms G → l-primary groups) as a hypothesis:
- Pohlig–Hellman (the converse case);
- in IC, `exact_decomposition_ceiling` in crypto `src/cryptanalysis/ic_boundary.rs`, which uses gcd(h, r) = 1 to make the cofactor-class map E(F_p) → E(F_p)/G a homomorphism and to count admissible sums.

This audit used that hypothesis generatively: it explains the class-representative effects and gives the subgroup-only base design rule (LEAD-STR-class-representative-ic-selection AUD-4).


---

## Cross-cutting: NEW LEAD proposal (prime-field Koblitz analogues and IC with endomorphism-orbit columns)

`tools/lead_atlas.py --match` was run with the phrase "prime field curve with norm 2 endomorphism of small eigenvalue order, endomorphism orbit factor base for index calculus, Koblitz analogue over prime field". Top hits: KR-IC-5931ee (31), LEAD-ICP-full-width-arity-grid (24), LEAD-ICB-nonlinear-frob-stable-bases (23), LEAD-ICB-frobenius-orbit-factor-base (22), KR-IC-b0fcda (20). None covers prime-field curves with a non-unit endomorphism of order about log N. The closest, LEAD-ICB-frobenius-orbit-factor-base, explicitly bounds the prime-field case by "at most 6".

**Mechanism.**
- Over the CM family verified in this audit (D = −7, degree-2 α, ord_N(λ) = h = log2 N; `/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/audit/n0check/cm_verify_out.txt`), an index-calculus base made of α-orbits {±α^e S_s} has one column per seed.
- Its coefficients λ^e are known once, so building the base costs F evaluations of α and nothing per trial.
- Rho cannot use α without canonicalising each step (about h maps). It keeps only the negation sqrt 2.
- This asymmetry is absent on binary Koblitz curves, where rho gets sqrt(2n) from cheap squaring.

**Cost-model prediction (conditional; not measured).**
- MITM IC with a column fold A_c = 2h has S_IC ∝ (r/h)^{2/3} against the program's generic prime-field IC, which is ∝ r^{2/3}. The predicted IC/rho on the family is therefore Table B's generic IC/rho at matched log2 r divided by h^{2/3}.
- Table B values (crypto `docs/ic/LEADERBOARD.md`): 5.82x at 18.0 bits, 8.3x at 20.0, 13.5x at 23.4. Divided by 17^{2/3}, 19^{2/3} and 23^{2/3}, they give about 0.88, 1.17 and 1.67.
- Second estimate from the measured Koblitz ladder (LEAD-ICB-frobenius-orbit-factor-base best_measured: compact-orbit IC/signed-Frobenius rho 2.96x at n = 13, 18.2x at n = 41). Removing rho's sqrt(n) Frobenius gain gives about 0.82 and 2.8.
- The exponent stays 2/3 > 1/2, so IC/rho grows like r^{1/6}/h^{2/3}. This family cannot reach deployed curves, which have large |D_K| (endosweep).

**Experiments (outline; outcome → disposition).**
- **E1 (construction, hours):** For h ∈ {17, 19, 23, 107}, build the explicit curve (twist of y^2 = x^3 − 35x − 98 over the listed p) and the explicit degree-2 endomorphism (kernel = the 2-torsion point attached to (α)).
  - Verify α(P) = [λ]P on G and ord λ = h.
  - Fail → the construction premise is wrong; drop the lead.
- **E2 (IC, ecbench, days):** Add an `endo-orbit` factor-base builder to `ic bench` beside `glv-orbit`. Run it on the h = 17, 19, 23 curves, using seeds projected into G (h_cofactor = 8, 4, 4), against `prime-abscissa` at matched F and matched negation rho (GAE, §5a 0/0.1/1 band).
  - Report IC/rho and its ratio to the generic Table B row.
  - Ratio ≈ h^{-2/3} → cost model confirmed (a constant/polylog lever; record as a measured IC improvement on a special family).
  - IC/rho < 1 on any curve → first prime-field IC row below matched rho, scoped to this family.
  - Ratio ≈ 1 → orbit columns give no gain in this pipeline; close as measured.
- **E3 (rho control):** Rho with α-orbit canonicalisation by enumeration (batched inversion) on the same curves. Measure κ.
  - κ ≈ h·c(α)/c(add) → rho cannot use α, so the asymmetry is real.
  - κ ≪ h → reopens LEAD-STR-automorphism-quotient-rho and LEAD-STR-small-cm-disc-nonunit-endo.
- **T1 (theory, open):** Does a canonical representative of the cycles of a degree-2 rational map on F_p (restricted to x(G)) exist with o(h) evaluations?
  - A lower bound closes E3's question by proof.
  - An algorithm gives rho sqrt(2h) on the family.
- **Binary/Koblitz analogue check:** None needed; KR-IC-b0fcda and KR-RHO-482ed3 already give matched gains there.

## AUD-6 family summary (standing obstructions in this family)

Verbatim statements: SO-ENDO is quoted in the LEAD-STR-endo-scalar-action-generic section, SO-ISO in LEAD-STR-isogeny-class-generic-invariance, and SO-TORS in LEAD-STR-torsion-module-leak. The two non-STR leads named by the standing codes are quoted here:

> **LEAD-TRF-prime-field-isogeny-to-weak (SO-ISO) obstruction.statement:** Tate: ordinary curves over F_p are F_p-isogenous iff they have the same #E(F_p); trace one and k = ord_N(p) are functions of #E and p, and prime fields admit no GHS descent, so the special set inside a generic class is empty at every size (EV-IT-511f3d). Scope: prime fields, ordinary or supersingular classes. Over composite-degree binary fields descent weakness is NOT class-invariant (see LEAD-TRF-ghs-binary-composite).

> **LEAD-ICB-cofactor-torsion-quotients (SO-TORS) obstruction.statement:** On ECC2K-130 gcd(4, l) = 1, so every full-translation homomorphic cofactor quotient reduces to the order-l projection rho already uses (Sylow coprimality); exactly sum-compatible filters on E(F_{2^131}) carry 2 bits (the cofactor), so Wagner k-tree has no quotient to work in; the corrected iota-stable classification (V_d = b^{1/4} F_{2^d}) empties the (subspace base, 2-torsion quotient) cell on every prime-degree standardized curve; the production 2-torsion census adds 0 relations. FGHR 2-torsion symmetrisation of the solve is a separate constant (engine family).

| obstruction | theory that takes the obstructing quantity as a hypothesis |
|:--|:--|
| SO-ENDO (End(G) = Z/N) | GLV/GLS (known), DGM orbit rho (known), orbit-column IC on Koblitz (known). New: orbit-column IC on CM-constructed prime-field curves with ord_N(λ) = log2 N (NEW LEAD above) |
| SO-ISO (class invariance over F_p) | JMV (known); isogeny hardness assumptions (reverse direction); GHS isogeny walking exploits its failure over composite binary fields (known, out of F_p scope). Over F_p, rational small torsion is not invariant and enters IC yield at O(1/F) (this audit) |
| SO-TORS (G → l-primary trivial) | Pohlig–Hellman (converse); `exact_decomposition_ceiling` / subgroup-only IC bases use gcd(h, r) = 1 as a design hypothesis (this audit applies it) |
| SO-GEN / SO-MULTI (referenced) | None new; DGM and Bernstein-Lange already used |

## Files written by this audit

- `/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/audit/audit-structure.md` (this file)
- `/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/audit/n0check/` : `n0.py`, `n0_out.txt`, `n0_rows.py`, `n0_rows.jsonl`, `residual.py`, `residual_out.txt`, `cm_norm2.py`, `cm_norm2b.py`, `cm_norm2c.py`, `cm_norm2d.py`, `cm_verify.py`, `cm_verify_out.txt`
- `/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/audit/gen/` : generator scripts for this file (`quotes.py`, `quotes.json`, `analysis_part*.py`, `render.py`)

---

## Family: exotic

# Audit of the exotic lead family (LEAD-EXO-*), passes AUD-1..AUD-6

Scope: all 19 rows in `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/exotic/`, each read in full.
Written 2026-10-24 by an audit subagent. Read-only: no repository file was edited.
Quotes of `obstruction.statement`, `revisit_when`, `next_action` are copied verbatim from the YAML
(whitespace normalised) by `audit/tools/exo_quotes.py`.

## Current state examined (AUD-1 trigger inputs)

- Known-results map `scratchpad/atlas/KRMAP.md` (51 rows read in full).
- `crypto-main/docs/ic/LEADERBOARD.md` and `crypto-main/docs/bounds/FRONTIER.md`: rho/BSGS and IC tables only;
  no row concerns an exotic mechanism (coordinate statistics, lifts, Miller, nets, oracles). They fire no exotic trigger.
- `scratchpad/atlas/delta.txt` (201 paths). Exotic-relevant items, all read at least at the summary level:
  - CZLIFT round: KN-FIND-3c7e19, KN-FIND-7e2b94, KN-FIND-c71e5d, KN-OPEN-d3a6f0, decisions DEC-20261023-147f9f,
    -36b4f0, -26a6de, -2e7447, -488023, -039ddf, -9de83a, -6931ab, -66af3b, -fdc4af and the synthesis DEC-20261024-23d64d.
  - IDEA-20261018-49fdf7 (structured-GGM / non-adaptive time-space bounds), IDEA-20261018-a0830c (break-even growth law),
    IDEA-20261018-2d21b9 (learned Groebner orderings), IDEA-20261018-6c1c6e (FGHR symmetrisation, binary m=4),
    IDEA-20261022-727d2e (special-number census), IDEA-20261022-e5b3a4 (pairing-transfer rows). The PEXT ideas
    (IDEA-20261024-*) concern GHS covers over F_{q^n} and touch no exotic row.
- Other leads' dispositions in `scratchpad/atlas/ATLAS.md`, plus the transfer rows that overlap this family
  (LEAD-TRF-miller-cocycle-nonhom-transfer, LEAD-TRF-padic-canonical-section, LEAD-TRF-global-lift-small-height) and the
  sibling audit `scratchpad/audit/audit-transfer.md`.

## Cross-cutting results (referenced from the per-lead sections)

### X1. The "GGM-simulable" closures for coordinate-reading oracles rest on a model in which Shoup's bound does not hold

Observation (`knowledge/findings/KN-FIND-002.md`, "Scope and limitations"): "The classification uses the **structured GGM**
(curve equation is public), not the strictest Shoup GGM (opaque labels). Under the strictest GGM, jet and endomorphism
would be NON-SIMULABLE because they require coordinate access." The same file closes the jet family with: "The generic
simulator computes P+Q (1 group operation) and then evaluates the rational function. **This closes all jet-based ECDLP
candidates** ... at exponent 1/2."
Observation (`knowledge/techniques/KN-TECH-005.md`): applicability "any lower-bound argument that treats group elements
as opaque labels accessed only via the group-operation oracle"; "it says nothing about attacks exploiting concrete
structure (... summation-polynomial index calculus over extension fields)".

Interpretation: a simulator that evaluates rational functions of coordinates is not a generic algorithm, so "simulable
with O(1) overhead in the structured GGM" does not import Shoup's Omega(sqrt r). The criterion proves too much:
Gaudry's decomposition on E(F_{q^n}) (KR-IC-46d822, O~(q^{2-2/n}) below rho for n >= 3) and Smart's anomalous attack
(KR-RHO-53c89f) are also "deterministic functions of coordinates plus O(1) group operations", yet beat sqrt.
What survives: oracles whose answers are group elements obtainable by group operations from public data
(endomorphism image [lambda]P with lambda known, halving [2^{-1}]P, incidence by subset sums) are genuinely generic and
are closed by Shoup. Oracles that return field data (x, y, jet/derivative data, Stange net values W(a,b) in F_p,
torsion-section digits) are closed only by whatever measurement or separate argument backs them.
Note also KN-FIND-002 item 3 describes the elliptic-net oracle as "the net value W(a,b) = a*P + b*Q", whereas the
Shipsey/Stange net (the object of LEAD-EXO-elliptic-net-eds) is field-valued (division-polynomial values).

### X2. A Weil-bound theorem for canonical primitives of computable cocycles (Miller U; zeta-defect Z)

Derivation (this audit, unreviewed; Lean target candidate T-KUMMER):
Hypotheses: E/F_p elliptic, P in E(F_p) of prime order N, gcd(N, p-1) = 1, f = f_{N,P} with div f = N(P) - N(O),
U(R) = f(R)^{N'} with N' = N^{-1} mod (p-1) (the unique N-th root, as in IDEA-20261017-e3a6f1), chi a nontrivial
character of F_p^*, psi any character of E(F_p).
Claim: |sum_{R in E(F_p) \ {P,O}} chi(U(R)) psi(R)| <= 2 sqrt(p).
Argument: chi(U(R)) = chi1(f(R)) with chi1 = chi^{N'} nontrivial. The Kummer sheaf L_{chi1}(f) on E \ {P,O} has local
monodromy chi1^{+-N} at P and O, nontrivial because ord(chi1) divides p-1 and gcd(N, p-1) = 1; it is tame and
unramified elsewhere. psi is the trace function of a lisse rank-1 Lang-torsor sheaf L_psi on E. The tensor product is
geometrically nontrivial (ramified), so H^0_c = H^2_c = 0 and dim H^1_c = -chi_c = -(2 - 2g - 2) = 2; Deligne's
weight bound gives 2 sqrt(p).
Consequence: for a prime-order curve (E(F_p) = <P>), every joint Fourier coefficient of (k, ell(k) = log_g U(kP)),
i.e. (1/N)|sum_k e(a ell(k)/(p-1) - jk/N)|, a != 0, is <= (2 sqrt p + 2)/N = O(N^{-1/2}). The Fourier-learning
breakeven against rho is about N^{-1/4} (KN-OPEN-d3a6f0 Q3, order-of-magnitude estimate in RT-20261023-dcb217).
So no multiplicative-character statistic of U is a heavy coefficient. The control predicted by the same argument:
when N | p-1 and ord(chi) = N, chi1^N = 1, the sheaf is unramified and the bound fails exactly where the reduced Tate
pairing is a homomorphism (the IDEA's own planted N | p-1 control).
Scope: character/correlation statistics of U only. It says nothing about non-character statistics (the IDEA's
"Smart-ratio" clause) or about an algebraic closed form for k; for the latter, K2 makes k a function of the EDS ratio
r_k = psi_{k-1}(P)/psi_k(P) taken at the integer k, which is not a function of kP (it is not N-periodic: r_{k+N} = r_k C^{-1}
if K2 holds). Evaluating it from (P, kP) is an EDS-association/residue-type problem; KN-LIT-247 (Lauter-Stange 2008,
`knowledge/literature/KN-LIT-247.md`, citation_verified: read, claims "as reported" from the abstract) reports the three EDS
problems equivalent to ECDLP at sub-exponential granularity.

Generalisation (sketch, lower confidence): the same proof applies to any commutative connected extension
0 -> L -> G -> E -> 0 (L = G_m or G_a) with gcd(N, #L(F_p)) = 1, the unique homomorphic section s over <P>, and an
algebraic section sigma on E \ S: theta(s(R) - sigma(R)) = Theta(sigma(R))^{-1} for the character Theta of G(F_p) that
extends theta and kills s(<P>), so the sum is a Lang-torsor sum on E \ S bounded by (#S + Swan) sqrt(p). For the
zeta-defect Z of IDEA-20261016-09fd08 (G = universal vector extension E^natural, cocycle = chord slope, S = {O},
Swan conductor 1 if the Cech class is represented by a simple pole) this would give |sum_R e(tZ(R)/p) psi(R)| <= 2 sqrt(p).
Unverified points: the Swan value and the identification of the chart; to be checked before any record cites it.

Numerical check (observed in this audit; script `scratchpad/audit/tkummer/check.py`, run with python3 -I):
on a NONTRIVIAL coset R0 + <P> (h > 1, so no Miller line has a zero or pole there; the coset sum obeys the same 2 sqrt(p)
bound by character orthogonality), the maximum over all p-2 nontrivial characters chi of F_p^* and all j of
|sum_k chi(f_{N,P}(R0 + kP)) e(-jk/N)| was:

| p | N | h | gcd(N,p-1) | max | 2 sqrt(p) | max / 2 sqrt(p) | same-shape random-function max |
|--:|--:|--:|--:|--:|--:|--:|--:|
| 1009 | 97 | 10 | 1 | 28.09 | 63.53 | 0.442 | 35.04 |
| 2003 | 257 | 8 | 1 | 68.06 | 89.51 | 0.760 | 55.74 |
| 3001 | 743 | 4 | 1 | 72.07 | 109.56 | 0.658 | 102.38 |
| 4001 | 661 | 6 | 1 | 74.81 | 126.51 | 0.591 | 93.78 |
| 1019 | 509 | 2 | 509 (control) | 509.0 | 63.84 | 7.973 | 81.87 |
| 1019 | 509 | 2 | 509 (control) | 509.0 | 63.84 | 7.973 | 77.66 |
| 2039 | 1019 | 2 | 1019 (control) | 1019.0 | 90.31 | 11.283 | 117.91 |

Reading: in the four gcd = 1 cells the maximum stays below 2 sqrt(p) and at the level of a random function; in the three
N | p-1 control cells the maximum is exactly N (a character of order N makes chi(f) a homomorphism, the reduced pairing),
as the derivation predicts. Limits: four curves, p <= 4001, coset sums only (the subgroup itself was not evaluated because
Miller lines vanish at multiples of P); this checks the inequality numerically, it is not a proof.

### X3. Where the torsion-section digit question (KN-OPEN-d3a6f0) sits relative to X2

Interpretation (conditional): the length-2 Greenberg transform of a lift E^ is an extension of E by a vector group; s_tor
mod p^2 is its unique homomorphic section over <P> (KN-FIND-7e2b94). X2 bounds fixed characters of the G_a-coordinate of
s_tor relative to an algebraic section of bounded complexity, but KN-OPEN-d3a6f0 asks about p-adic DIGITS of x and y,
which are not a fixed character of that coordinate (adding an E1-point changes x by a multiple depending on y(R)), and the
Greenberg group's defining equations have degree p (Witt-vector polynomials). That is the precise reason the Weil route
of X2 does not cover KN-OPEN-d3a6f0 ("For i >= 1 ... its degree grows with p. No bound is known", KN-OPEN-d3a6f0 Q2).
So the digit question is the one CZLIFT object that remains open at the exponent level; the Miller and zeta primitives
are (conditionally on X2's review) closed for character statistics.

### X4. Counting identity for decomposition yield (used in LEAD-EXO-dl-character-sum-pseudorandom)

Derivation (elementary): for any S subset of a group of order N with |S| = B and any m, sum_R r_m^S(R) = B^m, and the
number of targets R that admit an m-term S-decomposition is at most |mS| <= C(B+m-1, m) (unordered). So the probability
that a uniformly random target decomposes is at most C(B+m-1, m)/N for EVERY S: the random heuristic is an upper bound on
decomposition probability, and additive structure (large Fourier coefficients) can only lower |mS|. A Fourier bias can
raise the count of zero-sum relations inside S (r_m(0) = (1/N) sum_psi S^(psi)^m), not the yield of randomised targets.

## Summary table

| lead | disposition | AUD-1 | headline finding | change proposed |
|:--|:--|:--|:--|:--|
| `LEAD-EXO-augmented-oracle-ggm` | closed_obstructed | depends on reading: not fired (structured GGM, the row's sense); met under strict GGM | Shoup applied to coordinate-reading oracles (X1) | split: theorem part for group-element oracles; x/y/full-point/jet to measured scope |
| `LEAD-EXO-coordinate-statistic-leakage` | open_next_step | n/a | bounded-degree statistics are decided by Weil; threshold should be the N^{-1/4} breakeven | restate discriminates; add theorem for degree <= ~N^{1/4}/2 |
| `LEAD-EXO-cryptoscale-candidate-screen` | exhausted_at_scale | not fired | no experiment record references the screen's sensitivity audit | make the audit the queued revisit step |
| `LEAD-EXO-curve-model-representation` | closed_obstructed (measured) | clause 2 met (routing only) | the degree argument is a short proof | upgrade kind to proof via Lean target |
| `LEAD-EXO-dl-character-sum-pseudorandom` | exhausted_at_scale | not fired | target-yield reading of the mechanism is impossible by counting (X4) | restate mechanism as zero-sum relation count; cite X4 |
| `LEAD-EXO-elliptic-net-eds` | closed_obstructed (proof) | not fired | GGM support invalid for field-valued nets; literature anchor KN-LIT-247 missing; toy null used as closure | re-anchor on KN-LIT-247; scope collision phrase to toy; Lean target for period phrase |
| `LEAD-EXO-four-list-ktree-join` | open_next_step | n/a | Weil does not decide bucket-resolved W at the needed M | no change |
| `LEAD-EXO-global-lift-height` | open_next_step | n/a | next_action cites KR-IC-cd159a, now under correction; counting bound decides the fixed-surface case | reword next_action and evidence |
| `LEAD-EXO-hnp-advice-leakage` | open_blocked | n/a | conversion is priced by theorem for bounded-degree and Miller statistics; live candidate is KN-OPEN-d3a6f0 | update blocked_by |
| `LEAD-EXO-ideas-corpus-algebraic-transforms` | open_blocked | n/a | no single theorem; no change | none |
| `LEAD-EXO-invertible-hint-subset` | open_next_step | n/a | no theorem decides A(d) | none |
| `LEAD-EXO-lossy-object-propagation` | open_next_step | n/a | equidistribution on the Semaev surface decides the algebraic panel members | narrow the panel to the hash member |
| `LEAD-EXO-methodology-instruments` | open_next_step | n/a | add a documented null miscalibration and a proves-too-much control for simulability closures | add evidence and a control |
| `LEAD-EXO-miller-pairing-cocycle` | open_next_step | n/a | Weil-Kummer theorem (X2) bounds every character statistic of U; closed-form route reduces to EDS (KN-LIT-247) | close character route by theorem; re-anchor K2 route; settle duplicate with TRF |
| `LEAD-EXO-ml-learned-models` | open_next_step | n/a | hard-core reduction prices any positive; new idea not mapped | add pricing and ledger ref |
| `LEAD-EXO-padic-jet-canonical-lift` | closed_obstructed (proof) | not fired (near miss explained by exact null) | `Teichmuller lift digit` forecloses the open KN-OPEN-d3a6f0 question; jet GGM support invalid | narrow forecloses; tighten revisit_when; add new evidence |
| `LEAD-EXO-quantum-ecdlp-resources` | open_next_step | n/a | no theorem; no change | none |
| `LEAD-EXO-split-jacobian-projection` | closed_obstructed (proof) | not fired | kind proof rests on a known-algorithm cost (SO-COVER) | relabel kind cost_model |
| `LEAD-EXO-torsor-deck-period` | closed_obstructed (proof) | not fired | scope matches; Lang's theorem as AUD-6 | none |

## Per-lead audit

### LEAD-EXO-augmented-oracle-ggm

*Augmented oracles (x-, y-, full-point, halving, endomorphism-image, incidence) and GGM simulability*  
Disposition `closed_obstructed`; file `knowledge/leads/ecdlp/exotic/LEAD-EXO-augmented-oracle-ggm.yaml`; obstruction.kind `theorem`

> obstruction.statement: "Each named oracle is GGM-simulable (jet, endomorphism O(1); incidence O(m); halving equivalent to x; net O(log N)), so the Shoup lower bound closes its candidate family at exponent 1/2 (KN-FIND-002, KN-FIND-b7e091, KN-FIND-194294; EV-GGM-001 strong). Measured: the x-oracle gives Y_A = Y_B exactly (no yield advantage, EV-ECDLP-fd61e4 strong) and the m=3 MITM split saving is attributable to the split, not the oracle (EV-ECDLP-7367e2). Scope: oracles, not resources (see IDEA-20260808-ea3b4f)."

> revisit_when: "A publicly computable oracle that is NOT GGM-simulable is exhibited (the threshold oracle is the minimal non-simulable identifier, KN-FIND-982fdf, but needs private data)."

forecloses: `x-coordinate oracle meet in the middle`; `y-coordinate oracle guided decomposition`; `full-point oracle`; `endomorphism image oracle`; `halving query oracle`; `generic group model simulable oracle`

**AUD-1 (revisit triggers).** **Depends on the reading of "GGM-simulable"; not fired in the sense the row uses.** The trigger asks for "A publicly
computable oracle that is NOT GGM-simulable", and its parenthetical ("the threshold oracle is the minimal non-simulable identifier,
KN-FIND-982fdf") uses simulability in KN-FIND-002's structured-GGM sense, where a simulator may evaluate rational functions of
coordinates. Under that reading no delta item fires it: the new torsion section s_tor (KN-FIND-7e2b94, "computable as
s_tor(R) = R^ - [n^{-1} mod p^k]([n]R^)") is again a deterministic function of coordinates. Under the strict reading that
KN-TECH-005 requires for Shoup's bound ("treats group elements as opaque labels"), the condition is already met by the row's own
evidence: KN-FIND-002 states "Under the strictest GGM, jet and endomorphism would be NON-SIMULABLE because they require coordinate
access" (the endomorphism part is too strong, [lambda]P being generic when lambda is public). Evidence paths:
`knowledge/findings/KN-FIND-002.md`, `knowledge/techniques/KN-TECH-005.md`, `knowledge/findings/KN-FIND-7e2b94.md`.
Interpretation: the mismatch between the two readings is the AUD-2 problem below; the disposition change is carried there.

**AUD-2 (scope).** **Forecloses more than proved.** The theorem (Shoup via simulability) is sound only for oracles returning group
elements computable by group operations. The phrases `x-coordinate oracle meet in the middle`, `y-coordinate oracle guided
decomposition` and `full-point oracle` name coordinate-reading oracles (X1); for them the only support is the measured
"x-oracle gives Y_A = Y_B exactly (no yield advantage, EV-ECDLP-fd61e4 strong)" and the m=3 MITM attribution (EV-ECDLP-7367e2),
both toy-scale. This is the pattern "a generic-group bound applied to an oracle that reads coordinates". The phrase
`generic group model simulable oracle` is fine as worded.

**AUD-3 (measured/cost_model -> proof).** The measured clause "Y_A = Y_B exactly" is a tautology and can be stated as a proof: if Arm B is the exhaustive
enumeration of Arm A filtered by an exact membership predicate, the two arms output the same relation set, so yields are
equal by construction and only the work differs.
lean_target: for finite types and a predicate `mem` that is exact on the factor base, `(Finset.filter rel (enum A)) =
(Finset.filter rel (Finset.filter memAll (enum A)))` whenever `rel t -> memAll t`; hence yield(A) = yield(B).

**AUD-4 (theorem vs queued experiment).** (closed; not applicable)

**AUD-5 (open_unexamined).** (not open_unexamined)

**AUD-6 (obstruction as hypothesis).** SO-GEN taken as a hypothesis: the Maurer-Wolf / Boneh-Lipton black-box-field theory. It assumes exactly the generic
model and shows that an oracle multiplying in the exponent (a DH oracle) reduces DL to DL in an auxiliary elliptic curve over
F_N with smooth order. Generative reading: the screening question for a new public oracle is not "is it simulable" but
"does it realise a non-linear polynomial map in the exponent" (the same question LEAD-RHO-cheon-aux-acquisition answers
negatively for [x^2]P). None of the oracles in this row does; none found that does.

**Proposed change.** Split the obstruction: keep `kind: theorem` and closed_obstructed for endomorphism-image (lambda public), halving and
incidence oracles; move x-, y-, full-point and jet oracles to a measured scope (toy, EV-ECDLP-fd61e4, EV-ECDLP-7367e2), i.e.
exhausted_at_scale with the scale reached, or a separate row. Replace the jet citation of KN-FIND-002 by the measured
evidence it actually has.


### LEAD-EXO-coordinate-statistic-leakage

*Coordinate-statistic hunts: bias of x/y, slopes, bits, cross-ratios and trace functions under the group law*  
Disposition `open_next_step`; file `knowledge/leads/ecdlp/exotic/LEAD-EXO-coordinate-statistic-leakage.yaml`

> obstruction: none (open row).

> next_action.step: "Measure the digit-character family (IDEA-20260921-1ec106), the one natural candidate the census never measured, for (lambda, PGL_2-stability) against a PGL_2-orbit-matched null at the census sizes."

> next_action.discriminates: "A stable statistic with lambda above the random level would be the first census survivor and feeds LEAD-EXO-hnp-advice-leakage; random-level lambda for it closes the natural-statistic registry, leaving only unnatural (unbounded-degree) statistics."

forecloses: `x-coordinate statistic census`; `Legendre symbol bias under doubling`; `cross-ratio statistic`; `least significant bit of x correlates with 2P`; `trace-function sheaf pulled back through addition`; `stable and structured statistic on the curve group`; `chord slope bias`

**AUD-1 (revisit triggers).** (open; no obstruction to test)

**AUD-2 (scope).** (open; forecloses are ownership phrases, no closure to audit)

**AUD-3 (measured/cost_model -> proof).** (no measured closure)

**AUD-4 (theorem vs queued experiment).** **A theorem decides the bounded-degree part faster than measurement.** For a rational function h on E of degree d
and characters (chi of F_p^* or additive e(t./p)) and psi of <P>, the Weil/Bombieri bound gives
|sum_{R in <P>} chi(h(R)) psi(R)| <= 2 d sqrt(p) (subgroup-sum form cited in KN-OPEN-d3a6f0 for digit 0: "subgroup-sum
bounds give O(sqrt p) cancellation ... Lange-Shparlinski ... Kohel-Shparlinski ANTS-IV 2000. Status: reported").
So the normalised Fourier mass of any degree-d statistic is <= 2 d sqrt(p)/N, below the Fourier-learning breakeven N^{-1/4}
(KN-OPEN-d3a6f0 Q3) whenever d < N^{3/4}/(2 sqrt p), about N^{1/4}/2 on prime-order curves. This proves, for that class,
what the census measured ("every stable multiplicative coset statistic sits at the random level", EV-ECDLP-81f4d4).
Outcome map: the theorem (once checked) closes bounded-degree statistics; the queued digit-character measurement
(IDEA-20260921-1ec106) is still needed because base-2 digit signs of the integer lift are not of bounded algebraic degree.
The discriminating threshold for that measurement should be "lambda / Fourier mass decaying slower than N^{-1/4}", not
"above the random level": an excess that is above random but below N^{-1/4} cannot be converted below rho
(and IDEA-20261018-a0830c argues the same in its break-even law: an N-constant excess is sub-break-even).

**AUD-5 (open_unexamined).** (not open_unexamined)

**AUD-6 (obstruction as hypothesis).** (no obstruction in this row)

**Proposed change.** Add to the row: closure-by-theorem for statistics of bounded algebraic degree d <= c N^{1/4} (Lean target below);
change `discriminates` to use the N^{-1/4} breakeven and cite KN-OPEN-d3a6f0 Q3.
lean_target: for E/F_p, P of prime order N, h in F_p(E) nonconstant of degree d not of the form g^m (multiplicative case) or
g^p - g + c (additive case), and nontrivial characters, |sum_{k<N} chi(h(kP)) e(jk/N)| <= 2 d sqrt(p) + O(d).


### LEAD-EXO-cryptoscale-candidate-screen

*GOAL-CRYPTO-001 discovery screen for a reproducible non-generic crypto-size algorithm*  
Disposition `exhausted_at_scale`; file `knowledge/leads/ecdlp/exotic/LEAD-EXO-cryptoscale-candidate-screen.yaml`; obstruction.kind `measured`

> obstruction.statement: "Thirteen screening batches returned FINAL_NO_CANDIDATE / NO_ADMISSIBLE_NEXT_MECHANISM over the checked source set (EV-CRYPTO-010..013); the hyperplane-signature zero-minor route is not sub-rho under its own pinned model at d=1 (KN-FIND-3d6f78, EV-CRYPTO-ad7fa2 replicated). Scale reached: the recorded source set, zero-compute admission sheets; no crypto-size run."

> revisit_when: "An externally sourced candidate with an explicit constructor arrives, or the screen's own sensitivity audit (IDEA-20260805-9430e9) shows it could not have admitted a known positive."

forecloses: `crypto-size non-generic ECDLP candidate screen`; `hyperplane signature zero-minor route`; `compact target-label common factor`; `corner-coefficient induction`

**AUD-1 (revisit triggers).** **Not fired.** Trigger: "An externally sourced candidate with an explicit constructor arrives, or the screen's own
sensitivity audit (IDEA-20260805-9430e9) shows it could not have admitted a known positive." No delta item is an externally
sourced non-generic prime-field candidate (IDEA-20261022-e5b3a4 prices known pairing transfer; IDEA-20261022-727d2e is a
special-form census). Observation: no EXP record in `ledger/.index/experiments.jsonl` references IDEA-20260805-9430e9
(`grep -c 9430e9` returned 0), and its row in `ledger/.index/proposals.jsonl` has status null. Interpretation: no evidence that
the test the second clause names has run, so the clause has nothing to fire on.

**AUD-2 (scope).** The scope statement is honest ("Scale reached: the recorded source set, zero-compute admission sheets; no crypto-size
run"). The forecloses `crypto-size non-generic ECDLP candidate screen` is broad, but as an exhausted_at_scale ownership phrase it
matches the stated scope. No flag.

**AUD-3 (measured/cost_model -> proof).** Measured closure of a finite screen; no short proof replaces it (there is no theorem that a screening fingerprint
admits all positives). Not upgradable.

**AUD-4 (theorem vs queued experiment).** (not open)

**AUD-5 (open_unexamined).** (not open_unexamined)

**AUD-6 (obstruction as hypothesis).** Screen closure, not an obstruction quantity. None found.

**Proposed change.** Record in the row that no experiment record references the revisit test (IDEA-20260805-9430e9), and make it the row's cheapest
decisive step: replay the Gate A/B sheets on the known positives in the map (Smart anomalous, MOV small-k, Gaudry n >= 3,
JV n = 6) and record admit/reject. A screen that rejects a known positive voids the 13-batch FINAL_NO_CANDIDATE reading.


### LEAD-EXO-curve-model-representation

*Alternative curve models and point representations (Edwards, Hessian, Montgomery, Kummer, x-only)*  
Disposition `closed_obstructed`; file `knowledge/leads/ecdlp/exotic/LEAD-EXO-curve-model-representation.yaml`; obstruction.kind `measured`

> obstruction.statement: "Model-native PDP solving degree is invariant (d_reg = 2) between Weierstrass Semaev and twisted Edwards at m=2 and m=3, with Edwards a constant factor larger (EV-REP-001, EV-REP-002 replicated); the Kummer line is Bezout-optimal among coordinates E -> P^1 and the model lever is capped by a one-line degree argument (IDEA-20260905-d0fee4, IDEA-20260913-11d3cb, proposals). Exponent lever closed; at most constant factors (Hessian coordinate factor <= 2) remain."

> revisit_when: "A coordinate E -> P^1 with summation-polynomial degree below the Kummer degree is exhibited (would refute the Bezout claim), or a constant-factor model gain is wanted inside an IC engine (then it belongs to ic-prime)."

forecloses: `Edwards model summation polynomial`; `Hessian curve index calculus`; `Montgomery x-only factor base`; `Kummer line coordinate change`; `curve model changes solving degree`

**AUD-1 (revisit triggers).** **Clause 2 condition met, routing only; clause 1 not fired.** Clause 2: "a constant-factor model gain is wanted inside
an IC engine (then it belongs to ic-prime)". IDEA-20261018-6c1c6e (`ledger/proposals/IDEA-20261018-6c1c6e.yaml`, "FGHR 2-torsion
symmetrisation ... on the m=4 Weil-descent system", RQ-DREG-bd6c86) is such a gain, on the binary ECC2K-130 system, so it belongs
to ic-engine/ic-binary rather than ic-prime; nothing reopens here. Clause 1 (a coordinate with summation degree below Kummer):
no delta item.

**AUD-2 (scope).** The forecloses `Hessian curve index calculus` and `Edwards model summation polynomial` are backed at the exponent
level by the degree argument and by toy measurements (d_reg = 2 at m = 2, 3). They are stated as prime- and binary-agnostic; the
degree argument is characteristic-free, so no prime-to-binary overreach. No flag beyond the kind (see AUD-3).

**AUD-3 (measured/cost_model -> proof).** **A short proof would replace the measured closure.** Derivation (this audit, unreviewed): let phi: E -> P^1 be
nonconstant and fix generic values u_1..u_{m-1}; the degree of S_m^phi in u_m is the number of distinct values phi(P_m),
P_m = -(P_1+...+P_{m-1}), over the d^{m-1} tuples with phi(P_i) = u_i. Galois case: if phi is Galois with deck group D, then D is a
subgroup of Aut(E as a curve) = T x| A with T translations by a finite subgroup and A <= Aut(E,O), and A != 1 because E/T is an
elliptic curve, not P^1. Translations are absorbed by T and the only generic coincidence is the simultaneous action of A, so the
number of distinct values is |A|^{m-1}/|A| = |A|^{m-2} >= 2^{m-2}, with equality iff |A| = 2 (the Kummer x, and x composed with
an isogeny E -> E/T). Non-Galois case (lower confidence, unreviewed): fibres are not group orbits, so there are fewer forced
coincidences and the degree is expected to be at least the Galois value. This is the "one-line degree argument" the statement cites.
lean_target: for an elliptic curve E over an algebraically closed field and a nonconstant Galois cover phi: E -> P^1 with deck group
T x| A (A <= Aut(E,O), A != 1), the number of distinct values phi(-(P_1+...+P_{m-1})) over the fibres phi^{-1}(u_i) at generic
u_1..u_{m-1} equals |A|^{m-2}, hence deg_{u_m} S_m^phi >= 2^{m-2}; separately (open), the same bound for non-Galois phi.

**AUD-4 (theorem vs queued experiment).** (closed; not applicable)

**AUD-5 (open_unexamined).** (not open_unexamined)

**AUD-6 (obstruction as hypothesis).** Obstruction quantity: the per-variable summation degree 2^{m-2}. Theory that takes it as a hypothesis: invariant-theoretic
symmetrisation (FHJRV / FGHR, KR-IC-955fd6) uses the degree floor and divides it by the symmetry group order; it moves constants,
not exponents. None found that moves the exponent.

**Proposed change.** Once the Galois-case count is checked (and the non-Galois case is either proved or scoped out), change obstruction.kind measured -> proof for the exponent claim, keeping the
toy d_reg measurements as evidence for the constant-factor part; note in revisit_when that clause 2 routes to ic-engine/ic-binary
when the engine is binary (IDEA-20261018-6c1c6e).


### LEAD-EXO-dl-character-sum-pseudorandom

*Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)*  
Disposition `exhausted_at_scale`; file `knowledge/leads/ecdlp/exotic/LEAD-EXO-dl-character-sum-pseudorandom.yaml`; obstruction.kind `measured`

> obstruction.statement: "Measured the character-sum constant against a matched random null at 2^20-2^26 (EV-ECDLP-f83a17): R = C_EC/C_null is flat at about 1.28-1.34, i.e. the curve behaves like a random set up to a constant; all six standard analytic proof routes are closed (KN-FIND-e7a3b1), so neither a proof nor a measured bias exists. EXP7 Fourier flatness (8-14 bit) found no candidate predicate."

> revisit_when: "R trends upward with p beyond 2^30 on the same matched null, or a structured set other than small-x shows R growing with N."

forecloses: `discrete log character sum on small-x factor base`; `H-PSEUDO bias`; `Fourier bias of x-coordinate sets in log order`; `super-random additive yield factor base`; `exponential sum cancellation for the elliptic log`

**AUD-1 (revisit triggers).** **Not fired.** Trigger: "R trends upward with p beyond 2^30 on the same matched null, or a structured set other than
small-x shows R growing with N." No delta record measures R beyond 2^26 or on another set.

**AUD-2 (scope).** **Measured null used as closure of a phrase that a counting identity already decides.** The forecloses
`super-random additive yield factor base` is, in the randomised-target sense, impossible for every set (X4: decomposition
probability <= C(B+m-1, m)/N), so no measurement was needed for it; in the zero-sum-relation sense (r_m(0) inside the base) it is
the open question and the evidence is toy (2^20..2^26). The row should say which yield it means. The mechanism text cites the
Betti-yield duality (KN-FIND-9d2f56), whose condition "r_2(R) >= B^2/N for MOST R" is, by sum_R r_2(R) = B^2, satisfiable only
when B is of order N; interpretation: that theorem constrains average target yield, which no S can raise.

**AUD-3 (measured/cost_model -> proof).** Can a short proof replace the measured closure? **Not in the measured regime.** The Weil/Kohel-Shparlinski bound with
completion gives max_{psi != 1} |sum_{x(R) < B} psi(R)| = O(sqrt(p) log p), which is weaker than the measured C ~ 1.3 sqrt(B) when
B << p. The counting identity (X4) is a proof for the target-yield reading only.
lean_target (for X4): for a finite abelian group G of order N, S subset G, m >= 1: sum_{R in G} #{(s_1..s_m) in S^m : sum s_i = R}
= |S|^m, and #{R : exists decomposition} <= #(multisets of size m from S).

**AUD-4 (theorem vs queued experiment).** (not open)

**AUD-5 (open_unexamined).** (not open_unexamined)

**AUD-6 (obstruction as hypothesis).** Obstruction quantity: flat character-sum constant R. Taken as a hypothesis by the hidden-number / Fourier-learning
theory (KN-OPEN-d3a6f0 Q3): flatness at level N^{-1/2} is exactly "no heavy coefficient", i.e. the hypothesis under which
Akavia-Goldwasser-Safra-style learning fails. None found that turns flatness into an algorithm.

**Proposed change.** Restate the mechanism as the zero-sum relation count r_m(0) inside the small-x base (the only reading in which a
Fourier bias could help), cite X4 for the target-yield reading, and add IDEA-20261018-a0830c (N-constant excess is
sub-break-even) to the closure's rationale once that idea is reviewed.


### LEAD-EXO-elliptic-net-eds

*Elliptic nets / elliptic divisibility sequences as a relation or annihilator source*  
Disposition `closed_obstructed`; file `knowledge/leads/ecdlp/exotic/LEAD-EXO-elliptic-net-eds.yaml`; obstruction.kind `proof`

> obstruction.statement: "Somos identities hold for every k, so net relations encode the group law on one k-fibre and not k (KN-FIND-002: net oracle GGM-simulable with O(log N) overhead); standard Hankel displacement rank of translated x-blocks is tautological and consecutive blocks have linear complexity >= (M-2)/3 (IDEA-006 gate). Measured at toy prime fields p in {101,431,1601}, n <= 1607: collision statistics are random-oracle-equivalent and the charged k-recovery exponent is 1.97-2.80 against BSGS 1.17-1.32 at identical accounting, with the sieve/BSGS gap growing (24x -> 135x)."

> revisit_when: "Someone supplies a target-specific NONLINEAR locator outside the closed Hankel/translated-block classes, or a rank>=2 net whose relations are k-specific (the NC2 permuted-net asymmetry in EV-NET-001 is unexplained)."

forecloses: `elliptic net relations for discrete log`; `Somos sequence sieve on net exponents`; `short annihilator of an elliptic divisibility sequence`; `EDS period finding mod p`; `division-polynomial value collisions below birthday`

**AUD-1 (revisit triggers).** **Not fired.** Trigger: "Someone supplies a target-specific NONLINEAR locator outside the closed Hankel/translated-block
classes, or a rank>=2 net whose relations are k-specific (the NC2 permuted-net asymmetry in EV-NET-001 is unexplained)." No delta
record. Related: the Miller lead (K2 of IDEA-20261017-e3a6f1) routes into EDS ratios, but supplies no locator.

**AUD-2 (scope).** **Three scope problems.** (i) The statement's first support, "KN-FIND-002: net oracle GGM-simulable with O(log N) overhead",
rests on KN-FIND-002 item 3, which describes "the net value W(a,b) = a*P + b*Q" (group elements); the net in this lead's mechanism
is the field-valued Shipsey/Stange net (division-polynomial values), for which the structured-GGM argument does not import Shoup (X1).
(ii) The kind is `proof`, but the phrases `division-polynomial value collisions below birthday` and `Somos sequence sieve on net
exponents` rest on the measurement "at toy prime fields p in {101,431,1601}, n <= 1607": a measured null at small size used as
closure. (iii) `EDS period finding mod p` is foreclosed on an unrun proposal ("predicted random linear-complexity profile
(proposal, unrun)", IDEA-20261009-9f89ae). Literature not cited: KN-LIT-247 (Lauter-Stange 2008, "three hard problems in the
theory of elliptic divisibility sequences (EDS Association, EDS Residue and EDS Discrete Log), each of which is solvable in
sub-exponential time if and only if the elliptic curve discrete logarithm problem is"), present in `knowledge/literature/`
but in no KR row and not in this lead.

**AUD-3 (measured/cost_model -> proof).** Measured parts: the toy collision statistics cannot be replaced by a proof in general, but two phrases can.
Derivation (this audit, elementary): a rank-1 EDS W_n(P) depends on P alone, so its period mod p is a function of P (and of
ord(P), already known) and carries no information about k; for the rank-2 net W(a,b) of (P, Q), W(a,b) = 0 iff aP + bQ = O, so
the net's zero/period lattice is {(a,b) : a + bk = 0 mod N} and finding any nontrivial element of it is solving the DLP.
lean_target: (a) for a sequence defined from P only, any function of it is constant in Q; (b) for the Stange net of (P,Q),
W(a,b) = 0 <-> a*P + b*Q = 0, hence {v : W(v) = 0} = ker(Z^2 -> E, (a,b) |-> aP + bQ), whose generators determine k.

**AUD-4 (theorem vs queued experiment).** (closed; not applicable)

**AUD-5 (open_unexamined).** (not open_unexamined)

**AUD-6 (obstruction as hypothesis).** SO-NET as a hypothesis: Ward's quasi-periodicity W(k+N) = W(k) A^k B is the hypothesis of the Tate-pairing theory
(Shipsey; KN-LIT-018 "The Tate pairing via elliptic nets"): when N | p-1 the multiplier is the pairing and gives MOV-type transfer;
when gcd(N, p-1) = 1 the multiplier can be removed by an N-th root, which is exactly the Miller primitive U of
LEAD-EXO-miller-pairing-cocycle. So SO-NET generates the Miller lead; X2 then bounds its character statistics.

**Proposed change.** Re-anchor the closure on KN-LIT-247 (add a KR row from it: EDS Association/Residue/DL equivalent to ECDLP) instead of
KN-FIND-002; set kind to literature+measured; scope `division-polynomial value collisions below birthday` and `Somos sequence
sieve on net exponents` to "toy p <= 1601"; replace the unrun-proposal support of `EDS period finding mod p` with the elementary
argument above.


### LEAD-EXO-four-list-ktree-join

*Wagner k-tree / four-list joins with cheap sum-compatible filters*  
Disposition `open_next_step`; file `knowledge/leads/ecdlp/exotic/LEAD-EXO-four-list-ktree-join.yaml`

> obstruction: none (open row).

> next_action.step: "Measure the relative bucket variance W of the O2 agreement kernel (H-ECDLP-2ade73; IDEA-20260904-f7d47d second moment) on the covered families across N and fit its decay against 1/sqrt(N); EXP-ECDLP-5cad48 ran many stages without ever assigning a W class."

> next_action.discriminates: "LARGE-W (decay slower than 1/sqrt(N)) reopens a bucket-concentrated filter for a four-tree; SMALL-W extends the bucket-averaged O2 barrier (KN-FIND-ffe1df) to a bucket-resolved one and closes the filter class."

forecloses: `Wagner k-tree on elliptic curve points`; `four-list join with a cheap filter`; `sum-compatible hash on E(F_p)`; `representation technique subset-sum for ECDLP`; `signed-y four-list cascade`; `output-sensitive partial verifier`

**AUD-1 (revisit triggers).** (open)

**AUD-2 (scope).** (open)

**AUD-3 (measured/cost_model -> proof).** (no measured closure)

**AUD-4 (theorem vs queued experiment).** **No theorem decides it faster.** The bucket-averaged barrier uses a Weil/Bombieri bound composed with Theorem A
(`analysis/o2-sum-compatible-filters/README.md`: "[D]'s Weil bound into [F]'s Theorem A => j = 2 closes"). Interpretation: a
per-bucket version loses the bucket mass: conditioning on h(P+Q) = c multiplies the nontrivial-character term by M, giving
pi_c <= 1/M + O(M Lambda) with Lambda ~ p^{-1/2}; at the exponent-relevant M = p^{1/3} (the README's table for j = 2) the error
p^{-1/6} exceeds 1/M = p^{-1/3}. So Weil alone cannot decide LARGE-W versus SMALL-W at the needed M, and the queued measurement of
W stands. Also relevant from the delta: IDEA-20261018-49fdf7 claims every recorded pair-table/k-sum design is a non-adaptive
table-lookup algorithm covered by Dinur-Keller-Marmor; that covers generic filters only, not coordinate filters h (X1).

**AUD-5 (open_unexamined).** (not open_unexamined)

**AUD-6 (obstruction as hypothesis).** (no obstruction in this row)

**Proposed change.** None (no change).


### LEAD-EXO-global-lift-height

*Height-compressing global lifts (Q, number fields, function fields / elliptic surfaces)*  
Disposition `open_next_step`; file `knowledge/leads/ecdlp/exotic/LEAD-EXO-global-lift-height.yaml`

> obstruction: none (open row).

> next_action.step: "Run IDEA-20261009-581f5d: time T_section(d,chi,p) to find a bounded-height section through a prescribed fibre point on E1 surfaces at the Gaussian-heuristic degree d, across >= 3 primes, with a random-system Groebner control."

> next_action.discriminates: "T > p^(1/2) poly(log p) for every solver with d_reg equal to the random-system value closes the function-field variant (the Q-lift variant is already closed_known by KR-IC-cd159a); T <= p^0.45 at matched d on >= 3 primes, or d_reg systematically below random, keeps it alive."

forecloses: `xedni calculus`; `lift the curve to Q and find short relations`; `height-compressing global lift`; `SNFS number field lift of an elliptic curve`; `elliptic surface function-field index calculus`; `high-rank lift through a prescribed fibre`

**AUD-1 (revisit triggers).** (open)

**AUD-2 (scope).** (open)

**AUD-3 (measured/cost_model -> proof).** (no measured closure)

**AUD-4 (theorem vs queued experiment).** **Partly decided by an argument; the queued experiment stays for the varying-surface case.**
Observation: the next_action says "the Q-lift variant is already closed_known by KR-IC-cd159a". DEC-20261024-23d64d (xedni block)
says "JKSST 2000 (retrieved) bounds xedni success by C0/p only conditionally (Lang's height conjecture, Lemma 4.1's assumption),
vacuously at toy p, and reports frequent dependence at small discriminants; KR-IC-cd159a overstated it", and writes
CORR-20261024-63d682 against KR-IC-cd159a. The same synthesis gives the operative obstruction for fixed-rank lifts: "reduction is a
homomorphism, so half coverage of E(F_p) needs at least N_p/2 distinct global points (Omega(p) against O(sqrt p) for rho)",
conditional on transfer assumptions T1 to T4, and lists rank-growing lifts as not established.
Interpretation: the same counting applies to a FIXED elliptic surface over F_p(t): specialisation at t_0 is a homomorphism from a
Mordell-Weil lattice of rank r <= rho(S) - 2, so sections of height <= h hit at most O(h^{r/2}) points of E_{t_0}(F_p) and a
bounded-height section through a prescribed point exists with probability O(h^{r/2}/p). That decides the fixed-surface reading
by theorem. IDEA-20261009-581f5d instead varies the surface (degree d at the Gaussian heuristic), where no counting bound applies;
its timing experiment remains the discriminating step.

**AUD-5 (open_unexamined).** (not open_unexamined)

**AUD-6 (obstruction as hypothesis).** (no obstruction in this row)

**Proposed change.** Reword the next_action parenthetical: the Q-lift variant is closed for fixed rank by the counting bound of
DEC-20261024-23d64d (conditional on T1-T4), not by KR-IC-cd159a alone, whose claim is under CORR-20261024-63d682; add the
rank-growing case (r >~ log p / log log p) as explicitly open; restrict the IDEA-20261009-581f5d step to varying surfaces, the
fixed-surface case being decided by the specialisation count.


### LEAD-EXO-hnp-advice-leakage

*Bit-security / hidden-number conversion of DL leakage, auxiliary inputs and advice*  
Disposition `open_blocked`; file `knowledge/leads/ecdlp/exotic/LEAD-EXO-hnp-advice-leakage.yaml`

> obstruction: none (open row).

> next_action.step: "Price the Thue-Morse/Rudin-Shapiro conversion of H-ECDLP-a4be60 (IDEA-20260904-f68c7f: exponent 2*beta vs 1/2, memory and cost table) once a statistic with a measured nonzero log-bit advantage exists."

> next_action.discriminates: "With a measured advantage, 2*beta < 1/2 gives a sub-rho conversion to test against matched rho; without one the conversion has nothing to convert and stays a cost model."

> next_action.blocked_by: "No coordinate-to-log-bit statistic with measured nonzero advantage exists (LEAD-EXO-coordinate-statistic-leakage, LEAD-EXO-dl-character-sum-pseudorandom); auxiliary inputs require protocol leakage, not the plain ECDLP (GOAL-AUXIN-a93442)."

forecloses: `hidden number problem from coordinate bias`; `bit security of the elliptic discrete log`; `Cheon auxiliary input attack`; `convert a statistical distinguisher into key recovery`; `advice-length discrete log table`

**AUD-1 (revisit triggers).** (open)

**AUD-2 (scope).** (open)

**AUD-3 (measured/cost_model -> proof).** (no measured closure)

**AUD-4 (theorem vs queued experiment).** **A theorem prices most of the blocked conversion now.** The blocked step is the 2*beta-vs-1/2 conversion
(IDEA-20260904-f68c7f) "once a statistic with a measured nonzero log-bit advantage exists". For every statistic of bounded
algebraic degree d the Fourier mass is <= 2 d sqrt(p)/N (see LEAD-EXO-coordinate-statistic-leakage AUD-4), and for multiplicative
characters of the Miller primitive U it is <= (2 sqrt p + 2)/N (X2). With Fourier learning needing about tau^{-2} queries, these
classes cost >= N/(4 d^2) evaluations, so they cannot unblock the lead below rho for d < ~N^{1/4}/2. The remaining live supplier is
the torsion-section digit family: KN-OPEN-d3a6f0 Q3 states the conversion explicitly ("A family with Phi_i(n) >= n^(-1/4 + delta)
and a locatable heavy coefficient would therefore be an exponent-level sub-rho attack").
Outcome map: KN-OPEN-d3a6f0 Q1 exponent -1/2 -> the lead stays blocked with no natural supplier left; exponent above -1/4 with a
locatable coefficient -> unblocked, run the priced conversion.

**AUD-5 (open_unexamined).** (not open_unexamined)

**AUD-6 (obstruction as hypothesis).** (no obstruction in this row)

**Proposed change.** Rewrite blocked_by to name KN-OPEN-d3a6f0 (s_tor digit characters) as the only open supplier, state that
bounded-degree coordinate statistics and Miller-U characters are excluded by Weil-type bounds (X2), and use the n^{-1/4}
breakeven of KN-OPEN-d3a6f0 Q3 as the unblocking threshold.


### LEAD-EXO-ideas-corpus-algebraic-transforms

*ECDLP-IDEA breakthrough corpus: algebraic-geometric transforms awaiting constructors*  
Disposition `open_blocked`; file `knowledge/leads/ecdlp/exotic/LEAD-EXO-ideas-corpus-algebraic-transforms.yaml`

> obstruction: none (open row).

> next_action.step: "For each of the 15 active registry rows, supply the named constructor or theorem the deferred/independent audits ask for, then run its zero-compute contract preflight; start with IDEA-012 (finite-deck weighted endpoint, REVISE_SCOPED_REDUCTION) whose missing pieces are listed."

> next_action.discriminates: "A constructor that passes its preflight becomes its own lead with an experiment; a theorem-level no-go moves the idea to rejected with a cited obstruction."

> next_action.blocked_by: "Theorem-deferred constructors unsupplied (ideas/deferred/README.md); no experiment from the corpus has ever run (ideas/README.md)."

forecloses: `spinor matchgate addition transform`; `Cremona toric decomposition`; `block Krylov transition intersection`; `aggregate complement divisor compression`; `ramification break scalar digits`; `x-only nonfaithful signed lift`

**AUD-1 (revisit triggers).** (open)

**AUD-2 (scope).** (open)

**AUD-3 (measured/cost_model -> proof).** (no measured closure)

**AUD-4 (theorem vs queued experiment).** No single theorem or counterexample decides a 15-row registry. Interpretation: X1 applies to any corpus row whose
gate cites GGM simulability of a coordinate oracle; those rows' rejections would need re-checking, but I did not open the
15 registry rows individually, so no row-level claim is made here.

**AUD-5 (open_unexamined).** (not open_unexamined)

**AUD-6 (obstruction as hypothesis).** (no obstruction in this row)

**Proposed change.** None (no change).


### LEAD-EXO-invertible-hint-subset

*The invertible half: dense, cheaply recognizable AND cheaply invertible subsets of E(F_p)*  
Disposition `open_next_step`; file `knowledge/leads/ecdlp/exotic/LEAD-EXO-invertible-hint-subset.yaml`

> obstruction: none (open row).

> next_action.step: "Measure A(1) and A(d) (maximal agreement of degree-d polynomials with the log graph Gamma_E) on the toy ladder of H-ECDLP-f6a43a against the random-labelling null; the cell was never measured (claim expired, EV-ECDLP-924941)."

> next_action.discriminates: "A(d) at the random-labelling level for all d closes the algebraic-omega model of the invertible half; an excess growing with n is the first measured hint family and goes to a charged comparison."

forecloses: `dense invertible subset of the curve group`; `hint family with cheap logarithms`; `low-degree polynomial agreeing with the discrete log`; `small-x set logarithm interpolation`; `recognizable versus invertible duality`

**AUD-1 (revisit triggers).** (open)

**AUD-2 (scope).** (open)

**AUD-3 (measured/cost_model -> proof).** (no measured closure)

**AUD-4 (theorem vs queued experiment).** No short theorem found. Interpretation: A(d) compares a polynomial over F_p with logarithms in Z/N; with N != p the
ring mismatch blocks algebraic (Bezout/Weil) arguments. A partial constraint (derivation sketch, unreviewed): on an agreement set
A_g = {R : log R = g(x(R))}, every additive triple R1 + R2 = R3 inside A_g satisfies g(x(R1)) + g(x(R2)) = g(x(R3)) after lifting
to integers, which is not an algebraic equation on E x E because of the mod-N/mod-p mismatch, so even the triple count is not
bounded this way. The queued A(1)/A(d) measurement against the random-labelling null stays the discriminating step.

**AUD-5 (open_unexamined).** (not open_unexamined)

**AUD-6 (obstruction as hypothesis).** (no obstruction in this row)

**Proposed change.** None (no change).


### LEAD-EXO-lossy-object-propagation

*Lossy tracked objects propagated through scalar multiplication (doubling coordinates, rigidity, belief propagation)*  
Disposition `open_next_step`; file `knowledge/leads/ecdlp/exotic/LEAD-EXO-lossy-object-propagation.yaml`

> obstruction: none (open row).

> next_action.step: "Run the disjoint projection panel of IDEA-20260817-84755b in the probabilistic regime that the rigidity theorem (IDEA-20260807-df906f, IDEA-20260806-c5d183) leaves open, with exact-arithmetic fibre tests (KN-FIND-7d098b caveat) and a random-relabelling null."

> next_action.discriminates: "Propagation advantage at the null level for every projection closes the probabilistic regime too (the deterministic regime is already constant-or-injective); a projection with above-null propagation that is not injective is a genuine new lever."

forecloses: `propagate a lossy coordinate through double-and-add`; `belief propagation on the scalar multiplication graph`; `x+y or xy under doubling`; `tracked object enumeration`; `split-quotient certificate`; `latent linearisation of the group law`

**AUD-1 (revisit triggers).** (open)

**AUD-2 (scope).** (open)

**AUD-3 (measured/cost_model -> proof).** (no measured closure)

**AUD-4 (theorem vs queued experiment).** **A short theorem decides most of the panel asymptotically.** The panel (IDEA-20260817-84755b) measures
D(pi) = H(pi(X+Y) | pi(X), pi(Y)) for P2 chi(x), P3 d-th power residues, P4/P5 bit windows, P6 x mod m, P9 a window indicator,
P8 the r-adding partition index. Derivation (this audit, unreviewed): fix X; Y -> t2 x(Y) + t3 x(X+Y) is a rational function of
degree 4 on E (double poles at O and -X), not of Artin-Schreier form for p > 4, so |sum_Y e((t2 x(Y) + t3 x(X+Y))/p)| <= 6 sqrt(p);
similarly chi2(x(Y)) chi3(x(X+Y)) is a Kummer sheaf ramified at <= 6 points for all but O(1) values of X. Summing over X, the
triple (x(X), x(Y), x(X+Y)) is equidistributed for characters with discrepancy O(p^{-1/2}), and with completion for windows and
residue classes O(p^{-1/2} log^3 p). For any fixed-range projection built from these, D(pi) = D_null(pi) + O_range(p^{-1/2} polylog p).
Outcome map: theorem holds -> P2-P6 and P9 are closed asymptotically (their toy values only calibrate the instrument; at toy p
the error term can exceed the triple probabilities for 8-bit windows, so toy deviations are not evidence either way);
the measurement stays informative only for P8 (implementation hash) and for the P1 Kummer control.

**AUD-5 (open_unexamined).** (not open_unexamined)

**AUD-6 (obstruction as hypothesis).** (no obstruction in this row)

**Proposed change.** Narrow the next_action to the non-algebraic members (P8) plus the P0/P1/P7 controls, and record the algebraic members
as decided by the equidistribution argument.
lean_target: for E/F_p and nontrivial additive characters (t2, t3) != (0, 0), |sum_{X,Y in E(F_p)} e((t1 x(X) + t2 x(Y) +
t3 x(X+Y))/p)| <= 6 sqrt(p) #E(F_p) + O(#E(F_p)).


### LEAD-EXO-methodology-instruments

*Program methodology: instrument calibration, nulls, findings promotion (not a cost mechanism)*  
Disposition `open_next_step`; file `knowledge/leads/ecdlp/exotic/LEAD-EXO-methodology-instruments.yaml`

> obstruction: none (open row).

> next_action.step: "Inject the three planted-signal families of IDEA-20260807-efc8de into the real pipeline and replay every ECDLP mechanism screen against synthetic positives (IDEA-20260815-bc26a3) to measure the program's false-negative rate."

> next_action.discriminates: "A screen that misses planted positives invalidates the closures that rest on it and reopens those leads; a high detection rate licenses the closed_* dispositions in this atlas."

forecloses: `planted-signal positive control`; `instrument detection floor`; `label-permutation null`; `findings promotion gate`; `false-positive rate of mechanism screens`

**AUD-1 (revisit triggers).** (open)

**AUD-2 (scope).** (open)

**AUD-3 (measured/cost_model -> proof).** (no measured closure)

**AUD-4 (theorem vs queued experiment).** No theorem decides an instrument's false-negative rate; the planted-signal replay stays. Two delta items belong here:
KN-FIND-c71e5d shows a uniform null was wrong for a structured section ("naive 33 against 5.39 at mean 1/p (ratio 6.13 ...), but
33 against 29.19 under the exact null (1.13 ...)"), a concrete false-positive mechanism the replay should include; and X1 is a
proves-too-much failure of a closure instrument (the simulability test would also "close" Gaudry's E(F_{q^n}) decomposition).

**AUD-5 (open_unexamined).** (not open_unexamined)

**AUD-6 (obstruction as hypothesis).** (no obstruction in this row)

**Proposed change.** Add KN-FIND-c71e5d as evidence (exact structure-conditioned nulls; the integral-multiple split of DEC-20261023-039ddf
control C1) and add a proves-too-much control to the replay: run the GGM simulability test (EXP-GGM-001) on a known non-generic
positive (Gaudry n = 3 decomposition, or Smart on an anomalous curve); classifying it "simulable, closed at 1/2" invalidates the
instrument for coordinate oracles.


### LEAD-EXO-miller-pairing-cocycle

*Miller functions, S-unit descent and pairing-free Miller cocycles on prime-order curves*  
Disposition `open_next_step`; file `knowledge/leads/ecdlp/exotic/LEAD-EXO-miller-pairing-cocycle.yaml`

> obstruction: none (open row).

> next_action.step: "Verify IDEA-20261017-e3a6f1 claims K1 (Weil-reciprocity cocycle, U unique primitive) and K2 (U(kP)=c*r_k*C^(k/N), r_k=psi_{k-1}/psi_k) exactly on toy prime-order curves with gcd(N,p-1)=1, then measure whether k can be recovered from U(kP) in fewer than sqrt(N) group operations once r_k is charged."

> next_action.discriminates: "If K2 holds and r_k needs k (division-polynomial values), the primitive collapses into the closed elliptic-net lead and this lead closes as obstructed; if r_k can be removed or batched without k, it is the first pairing-free homomorphic exit and goes to a charged rho comparison."

forecloses: `Miller function S-unit descent`; `pairing-free Miller cocycle`; `generalized Jacobian transfer of the prime-order part`; `partial pairing return cycle`; `reduced Tate character without small embedding degree`

**AUD-1 (revisit triggers).** (open)

**AUD-2 (scope).** (open)

**AUD-3 (measured/cost_model -> proof).** (no measured closure)

**AUD-4 (theorem vs queued experiment).** **A theorem decides the correlation part faster than the experiment.** X2 (T-KUMMER): for gcd(N, p-1) = 1,
|sum_R chi(U(R)) psi(R)| <= 2 sqrt(p) for every nontrivial chi and every psi, so on prime-order curves every joint Fourier coefficient
of (k, log U(kP)) is O(N^{-1/2}), below the N^{-1/4} breakeven. This proves the spectral prediction of IDEA-20261017-e3a6f1
("max spectral statistic ... lower") rather than measuring it, and predicts the N | p-1 control peak.
The other route in the mechanism ("if U(kP) exposed k through a cheap closed form"): under K2, U(kP) = c r_k C^{k/N} with
r_k = psi_{k-1}(P)/psi_k(P) at the integer k; since U(kP) is N-periodic in k and C^{k/N} is not, r_k is not a function of kP, and
computing it from (P, kP) is an EDS-association/residue problem that KN-LIT-247 reports equivalent to ECDLP.
Outcome map: X2 checked -> close the character/Fourier route as closed_obstructed (theorem); K2 verified -> the closed-form route
reduces to KN-LIT-247 (closed_known); K2 false with K1 true -> only non-character statistics (the Smart-ratio clause) remain, an
open_unexamined residue. The sibling audit reaches the same K2 reduction (`scratchpad/audit/audit-transfer.md`, AUD-5 of
LEAD-TRF-miller-cocycle-nonhom-transfer) and warns that an equidistribution null would otherwise be read as a closure; X2 makes
that equidistribution a theorem, which closes only the correlation route, not the closed-form route.

**AUD-5 (open_unexamined).** (not open_unexamined)

**AUD-6 (obstruction as hypothesis).** (no obstruction in this row)

**Proposed change.** Replace the next_action by: (1) check the T-KUMMER derivation (Lean target in X2); (2) verify K1/K2 on toy curves as
the reduction check. Upon (1), move the character/correlation route to closed_obstructed (theorem, scope gcd(N,p-1) = 1,
prime-order curves); upon K2, close the closed-form route as closed_known via KN-LIT-247 (not via the elliptic-net row, whose
GGM support is unsound for field-valued nets, see that row). Keep LEAD-EXO-miller-pairing-cocycle as the owner and mark
LEAD-TRF-miller-cocycle-nonhom-transfer closed_dominated by it (coverage.tsv currently maps IDEA-20261017-e3a6f1 and
IDEA-20261016-09fd08 to the TRF row).


### LEAD-EXO-ml-learned-models

*Machine learning / neural and RL approaches to ECDLP and its subroutines*  
Disposition `open_next_step`; file `knowledge/leads/ecdlp/exotic/LEAD-EXO-ml-learned-models.yaml`

> obstruction: none (open row).

> next_action.step: "Run a learnability control on toy prime-order groups: train a model to predict a log bit from coordinates, with a planted-structure positive control (a known homomorphic leak) and a random-relabelling null, at N up to 2^24; in parallel execute the frozen ec_hardness_predictor phases 0-3."

> next_action.discriminates: "Detecting the planted leak but staying at chance on the curve closes direct learned DL prediction at that scale (consistent with IDEA-20260806-94676a: an exact latent linearisation IS the log); above-null accuracy on the curve that survives the null is a new statistic for LEAD-EXO-coordinate-statistic-leakage."

forecloses: `neural network predicts discrete log bits`; `representation learning of the group law`; `reinforcement learning over isogeny class`; `learned SAT branching for point decomposition`; `machine learning curve hardness predictor`

**AUD-1 (revisit triggers).** (open)

**AUD-2 (scope).** (open)

**AUD-3 (measured/cost_model -> proof).** (no measured closure)

**AUD-4 (theorem vs queued experiment).** No theorem decides learnability, but one prices a positive outcome: by the Fourier-learning/hard-core lineage cited in
KN-OPEN-d3a6f0 Q3 (Boneh-Venkatesan 1996; Akavia-Goldwasser-Safra 2003), a predictor with advantage epsilon on a concentrated
predicate of k yields k from about epsilon^{-2} polylog(N) predictor calls, so an above-null learned predictor matters only if
T_model * epsilon^{-2} < sqrt(N). At N <= 2^24 a model can also memorise; the train/test split must be over disjoint k (or disjoint
curves) for the null to be meaningful. IDEA-20261018-2d21b9 (learned Groebner orderings, HATSolver) is a learned solver policy,
i.e. this row's mechanism, and is not in its ledger_refs.

**AUD-5 (open_unexamined).** (not open_unexamined)

**AUD-6 (obstruction as hypothesis).** (no obstruction in this row)

**Proposed change.** Add the hard-core pricing criterion to `discriminates` (advantage epsilon counts only if T_model epsilon^{-2} <
sqrt(N)), require disjoint-k held-out splits, and add IDEA-20261018-2d21b9 to ledger_refs.


### LEAD-EXO-padic-jet-canonical-lift

*Prime-to-p jets, canonical/Teichmuller lifts and p-adic formal-group digits*  
Disposition `closed_obstructed`; file `knowledge/leads/ecdlp/exotic/LEAD-EXO-padic-jet-canonical-lift.yaml`; obstruction.kind `proof`

> obstruction.statement: "For gcd(n,p)=1 the prime-to-p torsion lifts uniquely (finite etale) with zero formal defect and multiplication by l is invertible on every native jet, formal and p-typical target, so every additive order-l image is zero (IDEA-004 gate, independently verified); jet oracles are GGM-simulable with O(1) overhead (KN-FIND-002). The digit identity d(mS^)=m*d(S^) holds only on the HARD global lift (1360/1360 exact, KN-FIND-85845f), whose cost is the lift itself; the computable Teichmuller-style contrast reads as chance under a resolution-matched repaired test (KN-FIND-e8cfdc); IDEA-436 D1 valuation profile collapses to the +/- fibre indicator (KN-FIND-1ba0fe). Scope: ordinary prime-field curves, toy primes 10-14 bits for the measured parts."

> revisit_when: "A computable non-homomorphic local section shows above-chance scalar information against a matched null at a resolution that could detect a 3x effect, or a succinct manipulation of the hard lift T^=mS^ without its coordinates (RQ-ECDLP-c1b7b1 first clause) is exhibited."

forecloses: `prime-to-p jet logarithm`; `dual-number lift of the addition law`; `canonical lift formal logarithm`; `Teichmuller lift digit`; `Serre-Tate canonical lift attack`; `extend Smart anomalous attack to ordinary curves`; `valuation profile of torsion lift`

**AUD-1 (revisit triggers).** **Not fired.** Clause 1 asks for "A computable non-homomorphic local section [that] shows above-chance scalar
information against a matched null at a resolution that could detect a 3x effect". Nearest delta item: KN-FIND-c71e5d, where the
naive integer section of F_p^* exceeds the uniform 1/p null (z = 7.65, 9.14) but matches the exact null (33 vs 29.19, ratio 1.13,
CI 0.78-1.59), and is F_p^*, not elliptic; DEC-20261024-23d64d calls it "an archimedean no-carry effect with no discrete-log content
beyond an O(log p) integer-logarithm check". KN-FIND-7e2b94: the three structured elliptic sections hit "at the random rate (toy)",
with a 4.2x-5.2x detection floor, i.e. coarser than the 3x resolution the trigger names, so it neither fires nor strengthens the
trigger's negative. Clause 2 (succinct manipulation of the hard lift): no delta item. Evidence paths:
`knowledge/findings/KN-FIND-c71e5d.md`, `knowledge/findings/KN-FIND-7e2b94.md`, `ledger/decisions/DEC-20261024-23d64d.yaml`.

**AUD-2 (scope).** **Forecloses more than proved.** The proof covers additive (formal-log) images and homomorphic sections ("every additive
order-l image is zero"). The phrase `Teichmuller lift digit` (and, read broadly, `valuation profile of torsion lift`) also blocks
non-linear digit statistics of the torsion/Teichmuller section, which DEC-20261024-23d64d lists as not established: "Whether any
coordinate or digit encoding of s_tor carries d ... The exponent-relevant unknown is KN-OPEN-d3a6f0". The measured support for
digits is toy (10-14 bits) and tests linearity, not Fourier mass. The same overreach is flagged for the transfer twin
(`scratchpad/audit/audit-transfer.md`, LEAD-TRF-padic-canonical-section AUD-2). The supporting clause "jet oracles are
GGM-simulable with O(1) overhead (KN-FIND-002)" does not import Shoup (X1); the closure does not need it, since the additive-image
argument stands on its own.

**AUD-3 (measured/cost_model -> proof).** (kind proof; not a measured closure. The additive clause has the Lean form given in the transfer audit: every additive homomorphism ZMod n ->+ B into a torsion-free B is zero.)

**AUD-4 (theorem vs queued experiment).** (closed; not applicable)

**AUD-5 (open_unexamined).** (not open_unexamined)

**AUD-6 (obstruction as hypothesis).** SO-PADIC as a hypothesis: Hom(Z/N, A) = 0 with gcd(N, |A|) = 1 is the hypothesis under which every computable cocycle on
<P> with values in A has a UNIQUE primitive (H^1 = H^2 = 0 for coprime orders). That is a generator, not a refutation: it produces
canonical non-homomorphic functions (Miller U into F_p^*, zeta-defect Z into F_p, the Greenberg torsion section s_tor into W_2).
The theory that then decides them is the Lang-torsor/Deligne character-sum theory of X2: bounded-conductor primitives (U, and
conditionally Z) are provably flat; s_tor digits are the case where the Greenberg group's equations have degree p (X3), i.e. the
one place the generator is not yet decided. Buium's delta-geometry (torsion as the zero locus of a delta-character) is a second
theory that takes the torsion locus as its hypothesis; its use here is untested.

**Proposed change.** Narrow `Teichmuller lift digit` to "formal-logarithm (additive) readout of a Teichmuller or torsion lift"; add
related: KN-OPEN-d3a6f0 (the new open row proposed in the transfer audit); amend revisit_when clause 1 to require the exact
structure-conditioned null and the integral-multiple split (KN-FIND-c71e5d; DEC-20261023-039ddf control C1) and add "or
KN-OPEN-d3a6f0 Q1 measures Phi_i(n) decaying slower than n^{-1/4}"; add KN-FIND-7e2b94 and KN-FIND-3c7e19 to evidence; drop the
KN-FIND-002 jet clause from the statement.


### LEAD-EXO-quantum-ecdlp-resources

*Quantum ECDLP: reversible secp256k1 point-addition circuits for Shor (resource reduction)*  
Disposition `open_next_step`; file `knowledge/leads/ecdlp/exotic/LEAD-EXO-quantum-ecdlp-resources.yaml`

> obstruction: none (open row).

> next_action.step: "Replace the per-step cswaps of the binary-GCD inverse by a safegcd/jump-GCD structure to narrow the apply and ipmul/quotient phases together (the 1,434-qubit peak is a 6-phase co-bind), validated on the full input space rather than only on a Fiat-Shamir reroll island."

> next_action.discriminates: "A peak below 1,434 qubits with exact correctness on all inputs is a real resource gain; gains that exist only on a reroll island are test-set fitting and should not count."

forecloses: `quantum circuit for secp256k1 point addition`; `Shor ECDLP resource estimate`; `Toffoli count of elliptic curve addition`; `reversible modular inversion for Shor`

**AUD-1 (revisit triggers).** (open)

**AUD-2 (scope).** (open)

**AUD-3 (measured/cost_model -> proof).** (no measured closure)

**AUD-4 (theorem vs queued experiment).** No short theorem gives a qubit lower bound for reversible modular inversion that would decide the jump-GCD step; the
engineering step stays. Its own discriminates already guards against reroll-island fitting. No change.

**AUD-5 (open_unexamined).** (not open_unexamined)

**AUD-6 (obstruction as hypothesis).** (no obstruction in this row)

**Proposed change.** None (no change).


### LEAD-EXO-split-jacobian-projection

*Split-Jacobian projected smoothness and the pair (P,Q) as a genus-2 divisor*  
Disposition `closed_obstructed`; file `knowledge/leads/ecdlp/exotic/LEAD-EXO-split-jacobian-projection.yaml`; obstruction.kind `proof`

> obstruction.statement: "Cross-genus Poincare-factor embedding cannot beat Pollard rho on the embedded elliptic factor because the Hasse-Weil order inflation of the ambient Jacobian outweighs genus-2 IC savings (KN-FIND-61347e); the IDEA-002 projected-smoothness counting gate finds no route with lambda,mu <= 0.45 and its projected endpoint fails the known-log interface."

> revisit_when: "A same-field embedding whose ambient group order is O(N) rather than inflated, or a projection with a known-log interface, is constructed."

forecloses: `split Jacobian projected smoothness`; `glue E to a genus-2 curve and do index calculus`; `encode P and Q as one Mumford divisor`; `Poincare factor embedding of an elliptic curve`

**AUD-1 (revisit triggers).** **Not fired.** Trigger: "A same-field embedding whose ambient group order is O(N) rather than inflated, or a projection
with a known-log interface, is constructed." The PEXT ideas (IDEA-20261024-*) are GHS covers over F_{q^n}, not same-field
embeddings; no delta item constructs either object.

**AUD-2 (scope).** **Kind overstates the scope.** KN-FIND-61347e item 1 is a theorem (Tate: #Jac(C)(F_p) = N #A(F_p)); item 2 compares with
"The best published genus-g hyperelliptic/plane-curve index-calculus family ... Otilde(p^{2-2/g})", a known-algorithm cost, not a
lower bound (SO-COVER). The row's `kind: proof` and the phrase `glue E to a genus-2 curve and do index calculus` therefore rest
on a cost model. The same relabel is proposed for the transfer twin in `scratchpad/audit/audit-transfer.md`.

**AUD-3 (measured/cost_model -> proof).** As a cost_model closure: no short proof would replace it, because no lower bound for DLP on genus-2 Jacobians below q is
known (that would be a new theorem). Not upgradable.

**AUD-4 (theorem vs queued experiment).** (closed; not applicable)

**AUD-5 (open_unexamined).** (not open_unexamined)

**AUD-6 (obstruction as hypothesis).** SO-COVER as a hypothesis: Weil descent / GHS takes "the ambient Jacobian is larger than E" as its premise and pays for it
by moving to a smaller base field (KR-IC-5ea2f8, KR-IC-791cb7). Over F_p there is no smaller field: none found for prime fields;
for composite-degree binary fields the theory is the existing GHS lane.

**Proposed change.** obstruction.kind proof -> cost_model (Tate part kept as a stated theorem); revisit_when add "or a DLP algorithm on genus-2
Jacobians over F_p whose cost on an order-N subgroup is below N^{1/2}".


### LEAD-EXO-torsor-deck-period

*Torsor, deck-orbit, cubical/biextension and scalar-orbit elliptic-period descent*  
Disposition `closed_obstructed`; file `knowledge/leads/ecdlp/exotic/LEAD-EXO-torsor-deck-period.yaml`; obstruction.kind `proof`

> obstruction.statement: "For a generically Galois cover every rational deck-invariant factors through the quotient; a transitive fibre-orbit label is base data; a connected nontrivial cover has no rational section, so a rational target-compatible selector is a missing section or trivialization (IDEA-010 gate, independently verified). The cubical/biextension lift lands on the invertible side of the recognizable/invertible duality, i.e. computing its label costs the log (IDEA-20260920-376b00)."

> revisit_when: "A rational, target-compatible selector or section of a nontrivial cover (or a non-Galois cover escaping the quotient argument) is exhibited."

forecloses: `torsor deck-orbit descent`; `cubical lift of the prime-order subgroup`; `biextension label of the target`; `scalar-orbit elliptic period`; `theta-structure linearisation of translation`

**AUD-1 (revisit triggers).** **Not fired.** Trigger: "A rational, target-compatible selector or section of a nontrivial cover (or a non-Galois cover
escaping the quotient argument) is exhibited." Nearest delta item: the torsion section s_tor (KN-FIND-7e2b94) is a pointwise
section of the Greenberg extension, computable and homomorphic, but it is not a rational section of a nontrivial cover over E and
it routes nothing (it "carries the discrete-log relation isomorphically into E^(Q_p)[n], no easier").

**AUD-2 (scope).** Scope matches the forecloses: the quotient argument is characteristic-free and covers Galois covers; the cubical/biextension
clause rests on IDEA-20260920-376b00 (a proposal) rather than a checked result, a weaker support than `kind: proof` suggests but
the phrase `cubical lift of the prime-order subgroup` is the only one resting on it. Minor; no change proposed.

**AUD-3 (measured/cost_model -> proof).** (kind proof; not a measured closure)

**AUD-4 (theorem vs queued experiment).** (closed; not applicable)

**AUD-5 (open_unexamined).** (not open_unexamined)

**AUD-6 (obstruction as hypothesis).** SO-DECK as a hypothesis: Lang's theorem (H^1(F_q, G) = 0 for connected G) makes every torsor pointwise trivial, so
pointwise selectors always exist; evaluating the label of a point is evaluating a Lang-torsor character psi(R) of E(F_p), which is
the discrete log itself. The theory that takes the obstruction as its hypothesis returns the DLP; none found beyond it.

**Proposed change.** None (no change).

## AUD-5 for the family

No exotic row is `open_unexamined`. Cross-family note: LEAD-TRF-miller-cocycle-nonhom-transfer (open_unexamined) duplicates
LEAD-EXO-miller-pairing-cocycle; the sibling audit proposes closed_dominated for it, consistent with the Miller proposal above.

## AUD-6 summary (standing obstructions touching this family)

| obstruction | rows here | theory taking it as a hypothesis | generative outcome |
|:--|:--|:--|:--|
| SO-GEN | augmented-oracle-ggm | Maurer-Wolf / Boneh-Lipton black-box field (DH oracle => DL via auxiliary curve) | screen oracles for non-linear maps in the exponent; none found |
| SO-PADIC | padic-jet-canonical-lift | coprime cohomology (unique primitives) + Lang-torsor/Deligne sums (X2); Buium delta-geometry | generates U, Z, s_tor; U provably flat (X2), Z conditionally, s_tor digits open (KN-OPEN-d3a6f0) |
| SO-DECK | torsor-deck-period | Lang's theorem H^1(F_q, G) = 0 | pointwise selectors = Lang-torsor characters = DL; none found |
| SO-NET | elliptic-net-eds | Tate pairing via nets (KN-LIT-018), Lauter-Stange equivalences (KN-LIT-247) | gcd(N,p-1)=1 multiplier removal = Miller primitive U; closed for characters by X2 |
| SO-COVER | split-jacobian-projection | Weil descent / GHS (smaller base field) | none for prime fields; binary composite degree is the GHS lane |
| (row-local) Bezout degree floor | curve-model-representation | invariant-theoretic symmetrisation (KR-IC-955fd6) | constants only; none for exponents |
| (row-local) flat character constant | dl-character-sum-pseudorandom | Fourier-learning theory (KN-OPEN-d3a6f0 Q3) | flatness = no heavy coefficient; none found |

## Cross-family observation (not returned as a finding)

LEAD-TRF-padic-canonical-section's statement says "any non-homomorphic section recovers d only at the random 1/p rate";
DEC-20261024-23d64d records "The clause \"every non-canonical section recovers d at the random rate 1/p\" is false as worded."
The transfer audit already proposes removing that clause.
