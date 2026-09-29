# Context for TASK-20260906-284fe9 (RQ-RELN-001, GOAL-RELN-001; proposals only, no lane opened)

Assigned IDEA ids (pre-allocated, --check verified free 2026-09-06; use in order; leave unused ones unused, never pad):

- IDEA-20260906-86cd30 -> ledger/proposals/IDEA-20260906-86cd30.yaml
- IDEA-20260906-cd7b7e -> ledger/proposals/IDEA-20260906-cd7b7e.yaml
- IDEA-20260906-fc429b -> ledger/proposals/IDEA-20260906-fc429b.yaml
- IDEA-20260906-5b4930 -> ledger/proposals/IDEA-20260906-5b4930.yaml
- IDEA-20260906-c03bf1 -> ledger/proposals/IDEA-20260906-c03bf1.yaml

Knowledge retrieval: crypto-kb index is EMPTY this session (':memory:'); do not call it; screen by reading.

## Lane state

- Goal next_action: 'Protocol design PASS. Defer measurement until activation residuals clear and PATH prioritizes an admitted RELN executor batch; no runs now.' Proposals are welcome; nothing here authorizes a run.
- Frozen protocol: coordination/goals/GOAL-RELN-001/batches/BATCH-001/tasks/TASK-20260725-661/decomp_probability_protocol.yaml
- Hypotheses:
- H-RELN-66c079 (proposed) SCOPE: prime-field Semaev decomposition over a +/- symmetric factor base W = V union -V of size 2B on deterministically generated ordinary curves at field_bits in {8, 10, 12, 16}, m in {2, 3}, with a Z/N control group. CLAIM TIER toy. NO ATTACK, NO EXPONENT MO
- H-RELN-96e3ba (proposed) SCOPE: the reference curve RULE-HEUR-TRACK pins in the frozen GOAL-RELN-001 protocol (coordination/goals/GOAL-RELN-001/batches/BATCH-001/tasks/ TASK-20260725-661/decomp_probability_protocol.yaml), evaluated on that protocol's own default B-ladder at field_bits
- H-RELN-a44c18 (proposed) SCOPE. The frozen interface of the bounded-degree algebraic factor-base theorem (ideas/artifacts/IDEA-20260801-021/bounded_degree_factor_base_theorem.md, Theorems 1, 1G, 2, 3) and the open universal question KN-OPEN-020, examined against two external index-cal
- H-RELN-f697be (proposed) SCOPE: the p_exist / p_solve separation and the B-ladder of the frozen GOAL-RELN-001 protocol, at field_bits in {8, 10, 12, 16}, m in {2, 3}, under a complete fix-(m-1)-and-root-find decider implemented in the standard library. CLAIM TIER toy. NO ATTACK, NO EX
- Experiments: EXP-RELN-0a979f, EXP-RELN-475c87, EXP-RELN-66c1ab, EXP-RELN-e48d01
- Evidence: EV-RELN-001; decisions DEC-20260725-017, DEC-20260810-2f92d8; knowledge KN-FIND-007, KN-LIT-009, KN-LIT-025

## Existing proposals bound to RQ-RELN-001 (17) -- read each whose title is adjacent to a candidate before filing; name the nearest one in discriminated_from with the exact delta

- IDEA-20260805-061f97 [mechanism; novelty=unverified; prio=medium] Relations needed is not B -- the left-kernel threshold is the fixed point of x = 1 - e^{-mx}, and the deviation of the touched-column curve from that forced value is the first measurement of relation independence this program would ever make
- IDEA-20260805-44bc0b [theory; novelty=unverified; prio=high] The bounded-degree factor-base no-go does not turn on "algebraic description" at all - it turns on a single scalar, the coverage exponent chi = m*log(Delta)/log(N) - and the two index-calculus families that demonstrably work, NFS and Gaudry-Diem, both sit at c
- IDEA-20260805-4ddd8c [control; novelty=unverified; prio=high] The RELN protocol's primary metric is a control that cannot fail -- p_exist(B) is pinned by counting, and the one free parameter is the normalized collision ratio Xi, whose value for a random base is exactly 1 - 1/M
- IDEA-20260805-5ac0a2 [control; novelty=unverified; prio=high] The reference curve this goal froze is off by a derivable factor 2^m: an exact-counting audit of HEUR-SEMAEV-2015-4.3 as transcribed into the GOAL-RELN-001 protocol, which decides the protocol's own headline verdict at every cell of the ladder before any measu
- IDEA-20260805-96cb3d [control; novelty=known; prio=high] The solve gap is zero by construction at every primary cell of this goal's ladder, and the relation-collection cost is invariant in B: charging the complete fix-(m-1)-and-root-find baseline turns the protocol's p_solve pin into a measurement of the solver rath
- IDEA-20260805-a25f11 [mechanism; novelty=unverified; prio=high] Only the collision deficit is free: an exact ceiling on P(decomp) at fixed factor-base size, a derived threshold B > (N/2)^{1/3} below which the best possible factor base is WORSE than a random one, and the graded additive-energy census that measures the one q
- IDEA-20260808-5e257f [measurement; novelty=screened; prio=medium] The frozen p_exist/p_solve instrument measures a CENSORED BINARY and throws away the only informative quantity it computes - replace the success bit by the ordinal "degree reached before the budget expired", which is uncensored, monotone, and turns every timed
- IDEA-20260808-9ef88c [representation; novelty=screened; prio=medium] A multiplicative-coset factor base makes the decomposition Macaulay operator an exact multilevel twisted circulant, giving the lane its first NON-semi-regular calibration point with a derivable solving degree of exactly B-1 and cost O~(B^m) - which still loses
- IDEA-20260815-c13ef4 [measurement; novelty=unverified; prio=medium] FACTOR BASES ARE ALWAYS BUILT BY SAMPLING; MEASURE WHETHER A DESIGNED BASE WITH ARITHMETIC-PROGRESSION STRUCTURE DECOMPOSES BETTER THAN A RANDOM ONE OF THE SAME SIZE
- IDEA-20260815-c3f707 [cost-model; novelty=unverified; prio=high] CHARGE THE FAILURES: every published P(decomp) in this lane is a per- attempt success rate, but an index calculus pays for FAILED attempts too, and the quantity the exponent actually consumes is the expected cost per ACCEPTED relation -- which no record in the
- IDEA-20260815-f9e978 [measurement; novelty=unverified; prio=high] P(decomp) IS REPORTED AS A SCALAR AND IS ALMOST CERTAINLY A DISTRIBUTION: measure decomposition probability CONDITIONED ON THE TARGET POINT, because an index calculus whose relation supply is heavy- tailed in the target has a different exponent from one whose 
- IDEA-20260815-fa56e7 [control; novelty=adaptation; prio=high] RELATION COLLECTION PRODUCES DUPLICATES AND THE LANE COUNTS RELATIONS RATHER THAN INDEPENDENT ONES: measure the rank deficit, because a relation that adds no rank costs the same and buys nothing
- IDEA-20260830-1f2b8b [mechanism; novelty=unverified; prio=high] THE DENSITY-INDEPENDENT OVER-DISPERSION HAS A DENSITY-INDEPENDENT SUSPECT WITH A CLOSED FORM: EV-ENDO-10109d's unexplained 1.3-3.6x residual is predicted to be 1 + (T/N)*mean(n1 - 1) exactly, because the target sampler draws from the cyclic subgroup generated 
- IDEA-20260830-21e7c4 [measurement; novelty=unverified; prio=medium] P(decomp) IS NOT A PROBABILITY TO BE ESTIMATED, IT IS AN INTEGER RATIO THE HARNESS ALREADY COMPUTES AND THEN THROWS AWAY: the sampled-target estimator is dominated in BOTH cost and precision below the crossover B^floor(m/2) < T, it wastes variance by a factor 
- IDEA-20260830-d2ebb5 [control; novelty=unverified; prio=high] EVERY NEGATIVE IN A P(decomp) MEASUREMENT IS CURRENTLY UNCERTIFIED, AND AT LOW DENSITY THE NEGATIVES ARE THE MEASUREMENT: define a kind exhaustive_nondecomposition certificate from four independently recomputable invariants, prove by an explicit observation co
- IDEA-20260905-029c9c [measurement; novelty=unverified; prio=medium] THE DEPENDENCY LATTICE OF AUGMENTED SEMAEV RELATION ROWS IS A GL(m+2, F_n)-INVARIANT OF THE ROW CONFIGURATION: measure lambda_1 of the integer left-kernel lattice L_K of the rows (c_i, -a_i, -b_i) against the exact-determinant Gaussian heuristic, with a synthe
- IDEA-20260905-1a8cb3 [control; novelty=unverified; prio=low] SHORT DEPENDENCIES ARE REDUNDANCY CERTIFICATES, NOT INFORMATION: define relation-generation entropy as H_k = log2 of the number of logarithm vectors consistent with the first k relations, measure bits per decomposition attempt on the same streams as IDEA-20260
