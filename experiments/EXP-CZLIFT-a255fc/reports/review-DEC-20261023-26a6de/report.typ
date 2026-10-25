#set document(title: "Decision report DEC-20261023-26a6de", author: "Coordinator, crypto-autoresearcher")
#set page(paper: "a4", margin: (x: 1.8cm, y: 1.8cm), numbering: "1 / 1")
#set text(size: 9pt)
#set par(justify: false, leading: 0.58em)
#show heading.where(level: 2): set text(size: 10.5pt)
#let vb(body) = block(fill: luma(244), inset: 6pt, radius: 3pt, width: 100%, body)

= Decision report: DEC-20261023-26a6de
#"EXP-CZLIFT-a255fc · H-CZLIFT-9a32e9 · RQ-CZLIFT-b9f765 · GOAL-CZLIFT-1516d5 · 2026-10-23"

== Status
#"Written by the coordinator subagent, which has no shell. graph.svg is produced by plot.py from plot_data.json, and report.pdf is compiled and inspected by the session. The decision is not official until the ledger archive commit carrying EV-CZLIFT-376eee, DEC-20261023-26a6de, analysis.md, the H-CZLIFT-9a32e9 update and this folder passes post-commit verification and is pushed to the PR branch."

== Decision
- *Decision:* #"weaken (one transition: H-CZLIFT-9a32e9 approved -> weakened)."
- *Evidence strength:* #"replicated (EV-CZLIFT-376eee). C1 alone would be strong; C2 is capped by post-hoc selection and by runs that share all points up to H = 1e5."
- *Claim tier:* #"toy (p = 103..20011, at most 15 bits; naive height <= 3e5)."
- *Refutation basis:* #"proof_status derivation (analysis.md D1-D7) plus replicated post-hoc empirical calibration; counterexample instances recorded in rt_c, not yet packaged as certificates."
- *Records:* #"EV-CZLIFT-376eee, DEC-20261023-26a6de, H-CZLIFT-9a32e9, EXP-CZLIFT-a255fc, RUN-CZLIFT-74f172, RUN-CZLIFT-490b33, CORR-20261023-0657da, VAL-20261022-9ab683 (TASK-20261022-3aca4b), RT-20261023-481827 (TASK-20261023-326d39), TASK-20261009-6552c9 (execution), TASK-20261023-4d7449 (ledger archive), DEC-20261009-9f9254 (observation readings superseded at clause level)."

=== Exact scoped claim, by clause

#"Scope for every clause: the minimal-conductor ladder 11a1, 37a1, 389a1, 5077a1, 234446a1, 19047851a1, 5187563742a1, 382623908456a1 (recalled ranks 0..7; r independent points verified, rank upper bounds not), naive height H(x) = max(|a|, d^2) <= 3e5, reductions at the 16 good primes 103..20011 (H_half resolved at 103..2417), quadratic twists by D in {-1, 2, -3, 5, -7, 13} of the first four curves at height <= 3e4, exhaustive deterministic enumeration (implementation/run.py d8de24d0), toy tier."
#table(columns: (0.55fr, 0.9fr, 3fr), stroke: 0.4pt + luma(200), inset: 3.5pt,
  [*clause*], [*reading*], [*scoped claim*],
  "C1 growth law", "supported",
  "N_E(H) agrees with the volume law V_r (log H)^(r/2)/sqrt(Reg) within [0.963, 1.309] for 1e3 <= H <= 3e5 on ranks 1..7; the growth slopes are within 0.32 of r/2 on both runs; 11a1 stays at its 5 torsion points for H >= 30. The frozen slope tolerance (+-1) does not confirm rank labels.",
  "C2 uniform reduction (HEUR-CZLIFT-UNIFORM)", "contradicted as stated",
  "The frozen criterion is met (median 1.0330 / 1.0333, none above 1.5), but it cannot fail on the upper side. The median lies outside every seeded uniform null (upper edge <= 1.0041; 0/200 reps reach it), and 97 / 123 cells have upper tails and 2 / 6 lower tails below 1e-6. A structured model (reduction homomorphism with the same image index and kernel floor h^ >= 2 log p) fits: 1.0350 [1.0294, 1.0398] against 1.0338. Not reject_scoped: the analyses are post hoc.",
  "C3 H_half scaling", "consistent, derived from C1, not uniform in p",
  "Off-grid slopes of log log H_half on log p equal 2/r within 0 to +10 percent (r = 3..7, 1-sigma <= 0.022, p = 103..2417). H_half is infinite where [E(F_p) : red_p E(Q)] >= 3 (37a1: p = 211 index 5, p = 293 index 4), so the uniform-in-p O(1) fails, in the direction that makes lifting harder.",
  "C4 exponential height, 'useless'", "not measured; conditional",
  "Half coverage is reached at H_half <= p^1.71 at every resolved toy prime. Beyond toy scale only log H_half >= (sqrt(Reg) N_p / (2 V_r))^(2/r) (1 + o(1)) holds, for fixed rank, bounded c_E and index <= 2, under T1-T4. Height is not attack cost.",
  "C5 twists / E(K)", "untested",
  "The instrument counts E(Q) union E^D(Q), not E(K). The 8 twist-bearing frozen cells all come from 389a1 D = -1, and O is counted twice. Nothing is measured about E(K) or Q(c^(1/d)).",
)

== Observation
#"Validity, checked first. 2 of 2 planned trials ran; both receipts are output_validated with returncode 0 and check_returncode 0; 20/20 artifact hashes match the receipts; every frozen metric recomputes bit-identically; two implementations that share no producer code (validator replay, red-team sieve) reproduce all counts and every coverage cell with H <= 3e4. The enumeration is deterministic, with no seeds. The 11a1 control fires as written at H = 10, where the count is 3 and arithmetically correct; CORR-20261023-0657da scopes it to H >= 16, and N_E(H) = 5 for every grid H >= 30 on both runs. Recorded, non-blocking defects: check.py imports the driver; the manifest revision of RUN-CZLIFT-490b33 was read after the run; library versions and memory are not recorded."
#figure(image("graph.svg", width: 100%), caption: [#"Panels A-B: coverage-ratio median per run (RUN-CZLIFT-74f172, 693 cells; RUN-CZLIFT-490b33, 785 cells) against the frozen band [0.8, 1.2], the seeded uniform null bands (validator seed 20261022 and red-team seed 20261023, 200 reps each, 95 percent bands), the random-lattice, Mordell-Weil-coordinate and index-matched homomorphism nulls, the kernel-floor structured null (470 cyclic cells, H <= 3e4, 100 reps), and the planted max-spread ceiling. Panel C: growth slope minus r/2, frozen tolerance +-1. Panel D: H_half slope / (2/r), frozen grid (recorded) and off grid (red team), +-1 SE, frozen tolerance [0.5, 2]. Panel E: obstruction quantity q1, N_E(H) over the volume law (RUN-CZLIFT-490b33). Panel F: log H_half / log p at the resolved toy primes. Data: plot_data.json; draw with plot.py."])

#"Recorded (manifests): coverage median 1.033040 (693 cells) and 1.033250 (785 cells); frac_above_1.5 = frac_below_0.5 = 0; growth slopes within 0.319 / 0.280 of r/2; grid H_half slopes 0.590, 0.415, 0.406, 0.375 / 0.364, 0.320 / 0.312 against 2/r 0.667, 0.5, 0.4, 0.333, 0.286; twist median 1.0036 over 129 cells."

#"Reviewer values (read by key): uniform nulls 1.0017 [1.0010, 1.0023] / 1.0016 [1.0007, 1.0022]; nested and paired 1.0025 [1.0010, 1.0041]; random lattice 1.0125 [1.0074, 1.0179]; actual point set under a random homomorphism 1.0116 [1.0080, 1.0164] (observed 1.0322 on 598 cells); index-matched 1.0139 [1.0089, 1.0192]; kernel-floor-conditioned 1.0350 [1.0294, 1.0398] (observed 1.0338, 69/100 reps reach it); kernel floor min lambda1^2(ker red_p) - 2 log p = +0.91 nats over 86 cyclic pairs; red_p(E(Q)) proper on 14 of 112 pairs; every 37a1 row maximally spread; planted max-spread median 1.0514 / 1.0548 passes the frozen criterion."

== Comparison
- #"Frozen success criterion: met on both runs; the frozen falsification criterion does not fire; no amendment is made."
- #"Instrument power: for any point set the ratio is at most min(x,1)/(1 - e^-x) with x = N/N_p, and the median x is 0.10. The upper side of the coverage criterion cannot fail, so meeting it is no evidence for C2."
- #"Observed median against calibrated nulls: above every uniform band and above the generic-geometry nulls (upper edges 1.0164 to 1.0192); inside the kernel-floor structured null. Generic geometry explains about 0.012 of the 0.032 excess, and the kernel floor the rest."
- #"Growth and H_half: within the frozen tolerances, which cannot separate r from r +- 1. Off the grid the H_half slope equals 2/r within 0 to +10 percent."
- #"Toy half-coverage height against 'exponential in p^(2/r)': H_half <= p^1.71 at every resolved prime. The target log p = 177.4 is 23 to 31 times the largest fitted log p."
- #"Twist clause against the instrument: E(K) grows like (log H)^((r + r_D)/2); the instrument counts the union, which grows like (log H)^(max(r, r_D)/2)."

== Inference
#"Derivation (analysis.md D1-D7). Reduction mod p is a homomorphism (D1). Every non-zero kernel vector has p^2 | den x(K), hence h^ >= 2 log p - c_E (D2; measured >= 2 log p + 0.91). Collisions among small points are therefore suppressed at short distance and clumped on a few kernel vectors, which is not the independent-uniform law (D3). Rank-1 sets are exactly injective below ord(red_p P)/2 (D4). The image index caps coverage at 1/k_p (D5). By pigeonhole, any spread saves at most a factor 2 ln 2 in N, i.e. Delta log log H_half <= 0.327 at r = 2 and 0.093 at r = 7 (D6). The H_half exponent is the inverse growth exponent read through pigeonhole (D7)."

#"Reading: the small points are as few as the Neron-Lang count says, and their reductions are not uniform but slightly over-spread by an arithmetic kernel floor. The over-spread is worth at most an O(1) shift in log log H_half, and the floor works against relation-finding. The counting obstruction to global lifts at fixed rank survives; its uniform-reduction justification does not. H-CZLIFT-9a32e9 is weakened because its stated mechanism is false as stated, its exponential-height consequence is unmeasured at toy scale, and its twist clause is untested."
#vb[#"Obstruction (EV-CZLIFT-376eee): counting floor at fixed rank. q1 count / volume law in [0.963, 1.309]; q2 off-grid H_half slopes equal 2/r within 0 to +10 percent (1-sigma <= 0.022); q3 kernel floor gap >= +0.91 nats; q4 median 1.0330 / 1.0333 against uniform 1.0025 [1.0010, 1.0041] and structured 1.0350 [1.0294, 1.0398]. Measured by RUN-CZLIFT-74f172 and RUN-CZLIFT-490b33. Scope: the ladder, H <= 3e5, p = 103..20011, toy; beyond that only the conditional fixed-rank bound under T1-T4. Resource check (examined): the obstruction is a rank obstruction. It collapses for lifts of rank >~ r*(p) = 2 log p / log(2 log p) (60.4 at 2^256), and the CVP route through ker red_p needs discrete logs (KN-LIT-7593 pattern). Both are routed to the idea-generator as candidates."]
#"Transfer assumptions for any statement beyond toy scale: T1, fixed rank independent of p; T2, bounded c_E and height difference along the lifts; T3, index [E(F_p) : red_p E(Q)] <= 2; T4, a fixed E/Q stands in for the attacker's p-dependent lift."

== Limitation
- #"Toy tier only; H_half resolved at p = 103..2417 with 4-10 primes per curve; no statement about cryptographic p beyond the conditional bound."
- #"The C2 adverse analyses are post hoc; the two runs share all points up to 1e5; structured and Mordell-Weil-coordinate nulls cover H <= 3e4 only; the kernel-floor analysis skips 26 non-cyclic pairs."
- #"Rank upper bounds are unverified; D4 and D5 rely on the recalled Mordell-Weil group of 37a1; the volume-law constant and the height-difference bound are recalled."
- #"The derivation is a written argument, not a machine-checked proof; the counterexample instances are not yet packaged as certificates."
- #"Spec discrepancies (primes 103..20011 vs 101..20000; cell domain; twist O double count; '10^6' in interpretation_limits) change no frozen outcome."

== Review inputs
- #link("../validation-20261022/validation_report.yaml")[#"reports/validation-20261022/validation_report.yaml"] #"(VAL-20261022-9ab683: J1 holds, J2 breaks on the 11a1 wording, J3 holds, PTM-1 breaks on instrument power)"
- #link("../redteam-20261023/redteam_report.yaml")[#"reports/redteam-20261023/redteam_report.yaml"] #"(RT-20261023-481827: R1 breaks, R2 breaks, PTM-1 holds; rt_a to rt_h artifacts)"
- #"ledger/corrections/CORR-20261023-0657da.yaml (11a1 control scoped to H >= 16)"
- #"No earlier reports/run-* directory exists for this experiment; the run records are the manifests under runs/."

== Canonical graphs checked
#"knowledge/frontiers/ecdlp/index-calculus/KR-IC-cd159a.yaml (xedni and lifting to characteristic zero) was checked. It is a frontier record, not a graph, and is unchanged: this decision is a toy-tier weaken with no cost claim and no closure. No canonical graph under knowledge/frontiers/ecdlp/ plots this quantity."

== Next actions
+ #"Session: write analysis.md from the coordinator's returned text, run plot.py, compile and inspect report.pdf, run tools/validate_ledger.py and tools/check_review_independence.py, then the ledger archive TASK-20261023-4d7449 by exact path; verify, merge origin/main, push, and open or refresh the ready PR 'evidence: EV-CZLIFT-376eee/DEC-20261023-26a6de'."
+ #"Goal checkpoint GOAL-CZLIFT-1516d5 (active), with one next action for this lane: the idea-generator writes the refined successor of H-CZLIFT-9a32e9 (a structured-reduction heuristic, H_half scoped to k_p <= 2, T1-T4 numbered, C4 as the conditional counting bound, height and cost separated)."
+ #"Pre-registered replication before any reject_scoped: structured null against the paired uniform null, with exact per-cell tails, on curves and primes disjoint from this census; k_p before H_half; off-grid H_half with tolerance |slope x r/2 - 1| <= 0.1."
+ #"Package the 37a1 p = 211 / 293 index instances and the 389a1 p = 149 kernel point as certificates with an independent re-checker."
+ #"If C5 is kept: an E(K) census over sums of the E(Q) and E^D(Q) bases, with positive-rank twists (11a1 D = -7) and O counted once."
+ #"Synthesis task on RQ-CZLIFT-b9f765: correct decision_target (a) (uniform-reduction wording is false), the H^(r/2) motivation (log height), and the JKSST / Neron attributions; close the global-lift sub-question, if at all, on the counting obstruction with its forward guidance."
+ #"Infrastructure ticket: an independent checker that evaluates every frozen control; read the revision at launch; record library versions and memory."
