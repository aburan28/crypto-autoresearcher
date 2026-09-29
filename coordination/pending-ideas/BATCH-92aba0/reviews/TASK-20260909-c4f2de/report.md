**TASK-20260909-c4f2de — REVISE: independent pre-implementation protocol review**

The frozen design preserves the intended finite ladder and has substantial explicit algebraic, chart, control and cost coverage. It is not ready for an unconditional protocol pass: the specialized-resultant invalidation rule conflates affine and exceptional charts; zero-polynomial root multiplicity is undefined; a retained K-growth prediction lacks an explicit disposition rule; and baseline identity scheduling/ties and canonical tree/hash keys need deterministic completion. These are protocol findings only, not executed counterexamples, scientific evidence or hypothesis transitions.

This concerns unchanged EXP-SDEG-8dfcf9 and H-SDEG-96e0d7 at snapshot 35ca1613fe9b33c62ab9c5f58eba1de50bd1a48c. All eight source snapshot bindings and the proposal hash matched. All 45 accessed repository files remained byte-identical at the final source recheck. Parent-owned Git/dispatcher/recovery checks are attributed to the admission capsule; this worker did not execute them.

**Evidence boundary.** Scientific runs, numerical regressions, curve/point enumerations, symbolic-kernel executions, formal builds, test suites and shell commands: all **0**. Findings are static protocol analysis and manual reasoning. No hypothesis or goal is validated or changed.

**F1 — Actual-degree affine filters can be nonzero on valid exceptional-chart tuples (high; revise).**

The specialized arm substitutes outer coordinates and takes actual-degree determinants, includes separate first-O charts, but then calls any nonzero filter with a genuine chart witness an instrument failure. A specialized actual-degree affine resultant is not a global filter for those extra charts.

Let P=(a,y), Q=(b,z) be affine permitted points with yz != 0, and write u=x(2P), v=x(2Q). For the valid ordered decomposition (P,-P,Q) of target Q, f(U)=S3(a,a,U)=-4*y^2*(U-u), and g(U)=S3(U,b,b)=-4*z^2*(U-v). The actual-degree linear/linear Sylvester resultant is 16*y^2*z^2*(u-v), which is nonzero when u != v. Nevertheless the first_O_at_2 chart is valid. The fixed generic-degree materialized S4 specialization vanishes: both quadratic leading coefficients drop and the padded determinant retains the infinity contribution. Thus equality of those two filter values, or global invalidation from the actual-degree nonzero value, is unjustified.

Required revision: State that each actual-degree filter rejects only its declared affine-prefix chart, then union the separately verified exceptional charts regardless of that filter. If the materialized global polynomial is retained as a sanity check, label it separately from specialized affine determinants. Restrict instrument-failure tests to a witness in the same chart/domain as its filter and require an appropriate future positive regression after additive protocol approval.

Limit: This identifies an inconsistent universally stated rule. It does not assert that a particular hash-selected source cell has been numerically exhibited with u != v, and it does not refute the guarded solver or the cost hypothesis.

Locations: [experiments/EXP-SDEG-8dfcf9/specification.yaml:212](/Volumes/SSD990/1083/ultra-recovery-20260909/experiments/EXP-SDEG-8dfcf9/specification.yaml:212) — experiment.inputs.baselines.complete_resultant; [experiments/EXP-SDEG-8dfcf9/specification.yaml:143](/Volumes/SSD990/1083/ultra-recovery-20260909/experiments/EXP-SDEG-8dfcf9/specification.yaml:143) — experiment.inputs.algebra.projective_completeness.

**F2 — The mandatory all-zero control has no finite algebraic multiplicity convention (medium; revise).**

The design correctly returns every field coordinate for (f,g)=(0,0), but separately requires root multiplicities of gcd(f,g) by repeated exact division and includes gcd multiplicities in C5. Under gcd(0,0)=0, every power of U-r divides the zero polynomial; repeated division supplies no finite stopping multiplicity.

Required revision: Freeze a nonnumeric sentinel such as undefined_zero_polynomial for original-gcd multiplicity, prohibit the repeated-division loop on zero, and separately retain the finite rational-coordinate set. If reduced field-restricted multiplicity is reported, label its value separately from original algebraic multiplicity. Define the same sentinel in certificates, metrics and the independent checker.

Locations: [experiments/EXP-SDEG-8dfcf9/specification.yaml:166](/Volumes/SSD990/1083/ultra-recovery-20260909/experiments/EXP-SDEG-8dfcf9/specification.yaml:166) — experiment.inputs.algebra.multiplicity/root_solver; [experiments/EXP-SDEG-8dfcf9/specification.yaml:175](/Volumes/SSD990/1083/ultra-recovery-20260909/experiments/EXP-SDEG-8dfcf9/specification.yaml:175) — experiment.inputs.subresultants.zero_cases; [experiments/EXP-SDEG-8dfcf9/specification.yaml:253](/Volumes/SSD990/1083/ultra-recovery-20260909/experiments/EXP-SDEG-8dfcf9/specification.yaml:253) — C5-all-zero-degrees.

**F3 — K-growth remains a hypothesis prediction but is only diagnostic in the experiment outcome (medium; revise).**

The source and derived hypothesis retain both adjacent finite beta<1. The specification defines that quantity, but success requires only correctness/cost/H1 and asks merely to report K; falsification omits a beta violation. A cost/H1 pass with beta>=1 could therefore be called overall success while one declared prediction fails.

Required revision: Preregister separate correctness, cost, H1 and finite-growth dispositions and a deterministic combined outcome, or explicitly narrow the target claim in an additive amendment. Retain every m2/m3/m4 row. For the declared D values the finite-growth comparisons can be specified exactly as K3<4*K2 and K4<8*K3, with equality failing the strict threshold, without claiming asymptotic growth.

Locations: [ledger/proposals/IDEA-20260906-69b3fc.yaml](/Volumes/SSD990/1083/ultra-recovery-20260909/ledger/proposals/IDEA-20260906-69b3fc.yaml) — idea.predictions; heuristic_assumptions; proof_search_map; [ledger/hypotheses/H-SDEG-96e0d7.yaml:25](/Volumes/SSD990/1083/ultra-recovery-20260909/ledger/hypotheses/H-SDEG-96e0d7.yaml:25) — hypothesis.predictions[2] and falsification_conditions; [experiments/EXP-SDEG-8dfcf9/specification.yaml:285](/Volumes/SSD990/1083/ultra-recovery-20260909/experiments/EXP-SDEG-8dfcf9/specification.yaml:285) — finite_degree_comparison; success; falsification.

**F4 — Identity-arm selection and metric-defining keys require a complete deterministic convention (medium; revise).**

The unrestricted identity arm calls the selected direct baseline, selected by completed cell work, while the rotating arm schedule can place it before the two direct arms. No equal-total-W tie rule chooses Rstar, although different per-atom costs can change H1. Hash recipes use cell_key and point_encoding without a complete concrete value grammar. The required K_declared syntactic tree and pi canonicalization also lack an explicit test-order/fast-quadratic-versus-general-PRS precedence and serialization rule.

Required revision: Freeze an identity-control phase after both direct arms, or compare identity wrappers against each direct arm independently; distinguish these cell-coupled controls from the controls-first algebra gate and charge all work. Freeze an outcome-independent Rstar tie order, the concrete cell/point encodings, branch-test precedence and canonical structural key/tree recipe before implementation and all observations. State whether per-synopsis preimage counts are retained, as requested in the source, alongside cell-level L and maximum b.

Limit: These are missing deterministic conventions, not evidence that any particular rotation, tie, null coefficient or K value occurred. No alternative implementation was run.

Locations: [experiments/EXP-SDEG-8dfcf9/specification.yaml:94](/Volumes/SSD990/1083/ultra-recovery-20260909/experiments/EXP-SDEG-8dfcf9/specification.yaml:94) — schedule.order; [experiments/EXP-SDEG-8dfcf9/specification.yaml:213](/Volumes/SSD990/1083/ultra-recovery-20260909/experiments/EXP-SDEG-8dfcf9/specification.yaml:213) — baselines.primary_reference/unrestricted_identity; [experiments/EXP-SDEG-8dfcf9/specification.yaml:283](/Volumes/SSD990/1083/ultra-recovery-20260909/experiments/EXP-SDEG-8dfcf9/specification.yaml:283) — measurement.H1/K; [experiments/EXP-SDEG-8dfcf9/specification.yaml:238](/Volumes/SSD990/1083/ultra-recovery-20260909/experiments/EXP-SDEG-8dfcf9/specification.yaml:238) — C2-coefficient-null.

**Disposition of the complete original scope.**

- **J0-custody-and-independence — pass.** All eight required file hashes matched before substantive inspection. This session did not produce the design and read no sibling/predecessor reports. The parent supplied current claim and native metadata; no local Git, claim or serving probe is represented as executed.

- **J1-source-ladder-and-m2-boundary — pass.** The full 101/211/431, m2/m3/m4, generic/j0/j1728 ladder remains. Both group scopes and all three base seeds are explicit. Treating m2 as a full identity/control census preserves the source's explicit effect scope; no twofold m2 improvement is invented. K outcome fidelity is separately revised under F3.

- **J2-S3-determinant-and-PRS — pass.** The retrieved Semaev short-Weierstrass formula and resultant recursion match. The retrieved AFP definitions match the stated initial and recursive PRS scalings and swap sign. Expanding the quadratic 2x2 minors gives S1=(a*e-d*b)U+(a*v-d*c); the stated resultant formula follows from eliminating U under a!=0. This is manual formula review, not a machine-checked identity or executed PRS test. Limits: The pseudoremainder implementation must save the pre-scaling coefficient before its loop update; the displayed identity is authoritative. Basic, not Lazard-optimized, PRS is the pinned algorithm. Semaev's S3 display is in section 2 after equation (2); calling it equation (1) is a locator imprecision, since (1) is the Weierstrass equation.

- **J3-first-O-target-O-rational-charts — pass.** The first internal O at 2/3/none partitions actual ordered signed tuples. Each stated exceptional suffix rule follows directly from the group sum, including empty m3 first-O identity and m4 first-O-at3 identity strata. Nonidentity rational prefixes have rational x, and recovering signs plus actual prefixes rejects incoherent/extension-only witnesses. No use is made of Semaev Lemma 2 outside its no-shorter-decomposition assumptions. F1 concerns baseline invalidation across these charts, not the partition itself. Limits: Identity-mask controls reduce to arity 0/1 as well as 2/3/4; explicitly state empty-sum=O and one-point equality base cases in the completed implementation contract.

- **J4-zero-and-multiplicity-semantics — revise.** Zero/constant solution-set branches are explicit and finite, and distinct multiplicity notions are separated. The mandatory gcd(0,0) multiplicity still requires F2.

- **J5-complete-resultant-comparator — revise.** Taking the minimum of two valid complete cell costs is a defensible strict reference. F1 prevents accepting the current cross-chart nonzero-filter failure rule; F4 completes identity-control selection.

- **J6-basic-F4-source-and-certificates — inconclusive.** Retrieved section 2.3 identifies batch critical-pair reduction, both pair multiples, symbolic preprocessing, complete matrix columns and a termination/correctness theorem. The proposed monic/RREF/grevlex implementation has explicit final S-pair and mutual ideal-containment obligations. Its structure is suitable for a basic F4 comparator. Exact typeset formula fidelity is incompletely inspectable because the primary PDF text has damaged mathematical glyphs and screenshot requests produced reference stubs without images. Follow-up: Inspect a legible primary copy or visual PDF for the displayed Reduction/Symbolic Preprocessing definitions before calling the exact source transcription fully verified. No optimized-F4 or best-implementation performance equivalence is established.

- **J7-same-task-generic-and-group-baselines — pass.** The generic arms acquire logs from points, retain failed rho restarts and charged BSGS fallback, enumerate decompositions and verify group outputs. They solve the same final task. Full_curve is not silently treated as cyclic. Scalar labels remain constructor/oracle-private by contract; enforcing isolation requires later QA. Freeze explicit traversal/caching for exhaustive_group with the rest of the implementation before measuring its row.

- **J8-all-nine-controls — revise.** All nine families were reviewed individually below. Their scientific executions remain future obligations. C1 requires F4; C5 requires F2; C6/comparator interpretation requires F1. No control is certified as having passed by this review.

- **J9-signed-weights-and-complete-cost — pass.** For s_a equal to the product of permitted rational-lift counts, summing over all x and all targets gives M=|T||B|^m. Summing C_A(a)=W_local(a)+s_a*W_shared/M reconciles exactly to complete W_total. This handles two-torsion without double-counting signs. Preparation, discovery, exceptions, rejected witnesses, recovery, checking, cache/I/O and unsuccessful attempts are required costs; wall/CPU/bytes are not inferred from field counts. No measured Pareto gain follows.

- **J10-finite-growth-prediction — revise.** F3 must reconcile hypothesis and experiment outcomes. The degree products are explicitly diagnostic, not actual costs or an asymptotic theorem. F4 must freeze a reproducible K/pi tree convention.

- **J11-deterministic-order-and-identifiers — revise.** Curve/subgroup/base selection and literal-expansion ownership are substantially deterministic and preserve all source cells. F4 identifies remaining key/order/selection conventions. Actual N,q,G,V,B,T values and all source counts remain uncomputed here.

- **J12-proof-architecture-and-formal-scope — pass.** L1-L4 are separated from cost/success and strict improvement L5-L6. The nonzero-multiplier law and first-zero partition are appropriate small formal targets with explicit semantic review, pinned Lean and axiom audit. They do not prove full Semaev correspondence or a speedup. C3/C4/C6/C8 challenge false implications. No formal artifact is claimed.

- **J13-lifecycle-and-execution-readiness — inconclusive.** The proposed chain preserves distinct protocol, implementation, formal, QA, activation, science and archive boundaries. The current review is an authorized isolated successor, but it cannot activate any old chain. Current interfaces still have concrete legacy-ID and finite-time constraints; no compatible SDEG adapter, executed QA, formal result or activation is validated by this task. Existing explicit gates correctly keep launch unadmitted.

- **J14-neighbor-scope-and-frontier — pass.** 18f6c5 retains open-locus residual mass missing from the earlier overbroad localization claim. SATIC is a binary regular-chain neighbor; SUBRES/RT1476 is an m5 backward-support/successful-membership scope; ALR/CREP address different represented objects. These bounded reads do not establish novelty or a complete frontier. The historical S4 record is context; current harness/semaev.py was not read because it is outside this frozen scope.

- **J15-proposed-S4-regression — pass.** The proposed fresh-variable construction is aligned with the retrieved recursion. The stated group relation gives the intended vanishing condition, and the linear-factor resultant rule explains the mutant's form. The literal 101-field point/addition/evaluation values remain proposed control expectations; no current implementation or numerical witness was evaluated.

- **J16-question-and-claim-limits — pass.** This is a small finite decomposition-component protocol. It does not fulfill the larger PFDR curve/size/yield/null matrix or the SDEG scaling-law goal by itself. Deterministic shared curves/seeds are not independent random trials for confidence intervals. Goals and hypotheses remain unchanged and no lane is closed.

**All nine control families.**

| Control | Protocol disposition | Reason |
|---|---|---|
| C1-unrestricted | revise | Exact algorithm identity is the correct control concept; complete selection order, tie handling and its placement relative to rotated baseline arms under F4. |
| C2-coefficient-null | revise | Matched nonzero coefficient support, multidegrees and adjacency plus all witness recovery is appropriate. Freeze the cell/edge/monomial key grammar under F4. Eight null chains per source cell and an algebraic witness-set comparison are distinct from source signed-point weighting. No predetermined criterion licenses an ECC-specific attribution from a raw difference alone. |
| C3-leading-zero | pass | At lambda=0 the degree drops but U=0 survives. The unguarded division must reject and the guarded solver must use actual degree. This is a control design, not an executed rejection. |
| C4-observation-collision | pass | The zero resultant and generic singleton can agree while the lambda=0 gcd/root set differs; the protocol labels the zero-polynomial sentinel and retains original equations/PSC/gcd information. |
| C5-all-zero-degrees | revise | Pairs and swaps cover important actual-degree cases and certificate corruption. The (0,0) multiplicity convention must be supplied under F2. |
| C6-infinity-signs | revise | The chart partition and inverse-pair mutant are appropriate, including target O and all identity-input masks outside main weights. F1 must ensure specialized baseline filters do not wrongly invalidate these valid exceptional witnesses; state arity0/1 mask base cases. |
| C7-S4-collision-regression | pass | Retained as a proposed fresh-variable versus sequential-substitution regression. No numeric evaluation, current shared-code verification or tested witness is claimed. |
| C8-rationality | pass | A nonsquare quadratic separates algebraic-closure roots from rational candidates; U^2 separates root coordinate count from finite multiplicity. No source computation was performed. |
| C9-generic | pass | Matched complete subgroup decomposition and label-permuted cyclic oracle are explicit. Hidden-label isolation, exact key format and full acquisition/fallback charges remain future implementation/QA obligations. |

**Current execution-interface limits.**

- [src/crypto_autoresearcher/runner.py:42](/Volumes/SSD990/1083/ultra-recovery-20260909/src/crypto_autoresearcher/runner.py:42): RUN_ID_PATTERN remains legacy decimal-only and planned timeout is validated as a positive finite number. The reserved six-hex RUN IDs and absent scientific deadline require explicit compatible mapping/engineering and QA. No runtime refusal was executed.

- [schemas/experiment.schema.json:11](/Volumes/SSD990/1083/ultra-recovery-20260909/schemas/experiment.schema.json:11): Experiment/run patterns remain decimal-shaped and execution-plan timeout excludes null. The generic record schema is not demonstrated compatible with this profile by a design snapshot.

- [schemas/execution-approval.schema.json:12](/Volumes/SSD990/1083/ultra-recovery-20260909/schemas/execution-approval.schema.json:12): Approval ID fields still use the legacy decimal-shaped patterns. External additive approval must be represented and validated explicitly.

- [schemas/runner-receipt.schema.json:12](/Volumes/SSD990/1083/ultra-recovery-20260909/schemas/runner-receipt.schema.json:12): Receipt ID fields remain legacy-shaped and timeout is numeric. Canonical receipt generation needs compatibility work before launch.

- [harness/finite_yaml_locked_v1.py:108](/Volumes/SSD990/1083/ultra-recovery-20260909/harness/finite_yaml_locked_v1.py:108): The local wrapper admits six-hex IDs but casts timeout to float and couples CPU seconds to that value; it does not establish this SDEG adapter's readiness. Do not substitute a finite research deadline or reuse the wrapper as unconditional authority.

- [schemas/run-manifest.schema.json:26](/Volumes/SSD990/1083/ultra-recovery-20260909/schemas/run-manifest.schema.json:26): Manifest ID fields have broader support, but timeout remains numeric. Some surfaces already differ; an undifferentiated assertion that every current file is a historical draft or that every ID field fails would be false.

The design keeps this mapping unadmitted. Protocol completion must be followed by separately authorized implementation, formal/semantic QA, activation and actual claim/runtime launch gates. Static reads are not a schema test or runtime pass. The two formal targets cover nonzero-multiplier preservation and first-zero partition only; they do not substitute for full group correspondence or cost obligations.

**Primary-source provenance.**

- [Primary source](https://arxiv.org/html/1504.01175): Section 2 definition/S3 display and resultant recursion, section 3 chain (4), section 4.1 Lemmas 1/2 and proof (web lines 51-156). Formula and scope of the affine-chain converse; not the article's speculative complexity claims. Provenance: retrieved; verified_by: TASK-20260909-c4f2de.

- [Primary source](https://isa-afp.org/browser_info/current/AFP/Subresultants/Subresultant.html): Algorithm definitions lines 22-67; determinant matrix and coefficient identity around 217-251 and 337; injective-homomorphism lemma 598-599; selected PRS proof excerpt around 2455. Basic PRS recurrence, scaling, determinant coefficient convention and injective-hom limitation. No formal build was performed. Provenance: retrieved; verified_by: TASK-20260909-c4f2de.

- [Primary source](https://wstein.org/129-05/refs/faugere_f4.pdf): Section 2.3, printed pages 5-8, Reduction, Symbolic Preprocessing, Lemmas 2.1/2.2 and Theorem 2.2. Four screenshot requests for zero-based pages 4,5,6 and repeated page5 returned reference stubs only; no image was viewed. Basic batch F4 structure at legible extracted-text scope only; exact displayed-formula fidelity is inconclusive. Provenance: retrieved; verified_by: TASK-20260909-c4f2de.

- [Primary source](https://math.mit.edu/classes/18.783/2025/LectureNotes13.pdf): Section 13.1 Theorem 13.3/Corollary 13.4 with proof, section 13.2 Definition 13.11/special j forms. For prime p>3 supersingularity iff trace zero, and special j models; no point count computed. Provenance: retrieved; verified_by: TASK-20260909-c4f2de.

The proposal, design, hypotheses, scoped neighbors and governance are internal sources. Exact accessed paths and hashes are in [read-inventory.json](read-inventory.json). No callable knowledge-search tool was available. The exact-task MEMORY.md lookup had no matches and supplied no evidence. The canonical skill, dynamic-dispatch and inventor-protocol documents were mandatory administrative reads beyond the enumerated list and were disclosed before START. The snapshot receipt was read only for its expressly supplied hash binding.

**Runtime, custody and independence.**

The actual producing Validator session is 01a084c7-e356-79d2-a1c0-1ff773438105, using openai / gpt-6-astra / literal ultra under review-adversarial. The parent observed native metadata at 2026-09-09T06:11:26.210927Z. model_verified=false; no serving probe occurred. The design producer, recovery preparer and parent controller are separate identified sessions. This worker read no predecessor/sibling report, other session history, canonical queue or future implementation/run result, and did not delegate.

Claim epoch 1 belongs to coordinator-pending-ideas-swarm-20260907, controller 01a07e0d-9f07-7382-a7d3-e2f0b4cf08de, acquired 2026-09-09T06:05:21Z and expiring 2026-09-09T09:05:21Z. The task filesystem root is /Volumes/SSD990/1083/ultra-recovery-20260909. Native/Node metadata cwd remains the original checkout; all repository operations used absolute recovery-root paths. The supplied publication is 21d87cf7e08a723b9717b21a34dd8607bb8b25db and contract SHA256 is 185d80809e41a16bed56950b9a3b8c62dc030de69f1c4a0ec88fa415fc35ff73. These parent-observed admission facts are not model-serving or scientific evidence.

One administrative JavaScript parse error occurred while preparing this bundle in memory. That cell executed no code and wrote no file; preparation then succeeded in smaller cells. This is recorded in runtime-provenance.json and carries no scientific implication.

**Coordinator handoff.**

Archive this exact successor report set under TASK-20260909-fdf917 with a scoped REVISE disposition. Prepare an additive protocol completion addressing F1-F4 and the legible F4 primary-source check, then commission fresh relevant independent review under new declared authority. Keep old blocked chains and scientific execution unactivated until explicit separate adoption and all remaining gates pass.

Standing user authorization already covers the next justified design work; no repeated per-experiment user approval is needed.

**Review attestation and stop-writes declaration.**

I own the seventeen local protocol questions above. Verdict on those completeness joints: breaks / revise. No whole-hypothesis verdict is issued. sources_read covers the complete filesystem/remote/in-context inventory and final readback of these four own outputs. read_sibling_reports=false; read_predecessor_reports=false; blind_from_respected=null because this is not a blind re-derivation. After exclusive creation/readback of report.json, report.md, read-inventory.json and runtime-provenance.json, all task writes stop. The actual post-write timestamp and exact four hashes/byte lengths are returned to the parent; TASK-20260909-fdf917 owns the durable archive.
