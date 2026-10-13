# EigenX/CEST EndRing reduction is not established

- **Status:** `investigating`
- **Kind:** proof gap and construction gap
- **Affected work:** [GOAL-SSI-2fa82a](../ledger/goals/GOAL-SSI-2fa82a.yaml), [CEST-PKE candidate](../coordination/design/TASK-20261007-9c36ba/tasks/TASK-20261007-913665/candidate.md), [scheme contract](../coordination/design/TASK-20261007-9c36ba/tasks/TASK-20261007-913665/scheme-contract.yaml), [proof-search map](../coordination/design/TASK-20261007-9c36ba/tasks/TASK-20261007-913665/proof-search-map.yaml), [BATCH-44a1ce decision](../ledger/decisions/DEC-20261013-122bb5.yaml), [BATCH-be2a37 composition](../coordination/design/TASK-20261013-0348f3/composition/TASK-20261013-a7be35/final-composition.yaml), [EigenX-v2 report](../research/ssi-endring-pke/2026-10-13-eigenx-v2-prescribed-path/report.md), [closing evidence](../ledger/evidence/EV-SSI-279763.yaml), and [closing decision](../ledger/decisions/DEC-20261013-9c2f80.yaml)
- **Next action owner:** future Coordinator only after a new explicit Coordinator decision and user-authorized scope; no automatic successor
- **Last updated:** 2026-10-13

## Problem

We cannot establish EndRing-based confidentiality or call EigenX complete because the CEST-PKE transcript currently supports only a proposed reduction to the separately named `CEST-XFER-KI` game, while no correctly directed solver turns a successful scheme attacker into a complete `End(E)` basis on the exact real-key distribution.

Here, **EigenX** is the user-facing alias for the CEST-PKE candidate recorded by `IDEA-20261007-560bcb`, `H-SSI-fbe68d`, and `TASK-20261007-913665`; the alias does not create a new candidate or strengthen its claims. The frozen candidate uses `A=psi_E(P)`, `R=[r]P`, sender value `[r]A`, and recipient value `psi_E(R)`. Correctness is conditional on accepted keys and an evaluable `psi_E`. Its advertised EndRing dependency would require a reduction with input sampled from the stated EndRing challenge distribution, access to a successful IND attacker on the complete scheme view, and output of a rank-four efficiently evaluable basis of `End(E)` with explicit probability, loss, and runtime.

An attempted path through Page--Wesolowski additionally needs a solver for bounded OneEnd on every adaptively generated internal query curve. `BATCH-12e6aa` established only that the four submitted public samplers do not supply that interface; it did not prove that no such bridge exists.

## Evidence and uncertainty

- **Observed:** `TASK-20261007-913665/scheme-contract.yaml` leaves O5 open for `IND-CPA -> AuxEndRing_CEST` and names only a proposed classical-ROM reduction to `CEST-XFER-KI`. `EV-SSI-65dc17` and `DEC-20261009-e8b142` record zero surviving public samplers and a broken J4 bridge from high-mass success on the campaign endpoint law to every adaptive Page--Wesolowski internal query. Both batches used zero scientific runs.
- **Derived or proved:** A complete evaluable EndRing witness is sufficient to derive `psi_E` and compute `psi_E(R)`, so an EndRing solver gives an attack route against the candidate. This is the reverse of the security-reduction direction. The current decryption behavior factors through one evaluator on the reachable ciphertext subgroup line; no cited theorem upgrades that observable to a complete rank-four ring basis. The conditional identity `psi_E([r]P)=[r]psi_E(P)` establishes only the declared accepted-key correctness step.
- **Suspected explanation:** The reachable-line action may be a strict witness quotient of a complete EndRing witness, and the adaptive OneEnd oracle required by the known reconstruction may be strictly stronger than a sampler on one endpoint distribution. These are hypotheses to test, not impossibility results.
- **Missing capability:** A distribution-matched, polynomial-time challenge embedding and extractor in the correct direction; if the extractor calls OneEnd, a complete adaptive-query coverage theorem with exact representation, degree, success, abort, and total-cost accounting. An independently reviewed six-obligation scheme discharge is also absent.
- **What this evidence does not establish:** It does not prove EigenX insecure in every model, prove `CEST-XFER-KI` easy, prove that no EndRing-based PKE exists, or prove universal nonexistence of a public adaptive OneEnd bridge. Failed or absent constructions and zero-run theory reviews do not establish those conclusions.

## BATCH-44a1ce reviewed update

The bounded adaptive-coverage and EigenX audit has now completed. Independent ownership produced the vector `J1=holds`, `J2=breaks`, `J3=breaks`, `J4=breaks`, and `J5=breaks`; the later documentation joint `J6` passed after corrections. The raw independence checker did **not** pass: it returned eight frozen plan-schema alias diagnostics (`prior` versus `coordinator_prior`, `owner_task_id` versus `assigned_to` for J1--J6, and per-object versus top-level proves-too-much failure signatures). A direct one-owner/one-verdict record crosscheck passed, but that comparison is not presented as a replacement checker pass.

- **Adaptive interfaces:** I1 (pointwise-total direct) and I2 (transcript-conditional compiler) remain inconclusive because their uniform public construction, every-prefix law, stopping-tail, and resource certificates are absent. I3 (outer-path pushforward) has a scoped break: it is path-correlated, its pullback is `[deg(phi)^2]alpha`, and an allowed singleton-support base can keep the phase-1 ring at rank at most two forever. No interface survives; this does not prove that every possible adaptive bridge fails.
- **Six obligations:** O3 alone has a reviewed discharge for accepted valid keys and the declared interfaces: `psi([r]P)=[r]psi(P)` makes the canonical sender and recipient pad inputs equal, so actual-message decryption has conditional failure probability zero. O1, O2, O4, O5, and O6 remain open. In particular, setup/canonical selection is not executable, the reachable transcript factors through a line evaluator, the EndRing reduction is absent, and the adversarial/encoding scope is incomplete.
- **Pairing and classical-ROM boundary:** one pairing equation admits the full affine line `T=[r]A+[x]P`; the additional equation `e(A,T)=1`, together with q-torsion membership, uniquely recognizes the supplied point `T=[r]A`. This supports a separate classical-ROM CEST-XFER-KI query-recognition step only. It does not compute `T`, construct an evaluator, or extract a complete rank-four endomorphism ring.
- **Reduction direction:** there is still no attacker-to-complete-EndRing extractor. The fact that a complete EndRing solver can derive the evaluator and decrypt is the reverse attack direction and has no security-reduction value.
- **Active attack:** the frozen unauthenticated syntax has an exact standard IND-CCA2 break. Reusing `R*` while replacing `v*` by `v* XOR Delta` for nonzero `Delta` gives a distinct accepted ciphertext; one decryption query reveals `m_beta XOR Delta`, hence `m_beta`. This is scoped to the frozen syntax and does not refute a different authenticated construction or the narrower conditional IND-CPA proposal.
- **Documentation correction history:** J6 detected missing PDF direction arrows and temporary localhost links, corrected by `TASK-20261013-1c2b7a`, then detected conflated link-count metadata, corrected by `TASK-20261013-b61e2d`. J6 inspected the actual SVG and all eleven final PDF pages and returned `pass_after_corrections`. These were documentary corrections; no J1--J5 verdict or scientific content changed.
- **Run boundary:** zero scientific, implementation, formalizer, experiment, benchmark, and parameter-selection runs occurred. No measured result, concrete parameter, performance claim, or implementation result exists.

The problem remains `investigating`; none of its exit criteria is met. The reviewed result blocks describing EigenX as a complete or secure EndRing PKE, but it is neither an EndRing hardness result nor a universal obstruction to EndRing-based encryption.

## BATCH-be2a37 reviewed update

The one-candidate EigenX-v2 prescribed-path/torsion round has completed. The valid independent vector is `J1=breaks`, `J2=breaks`, `J3=breaks`, `J4=breaks`, and `J5=breaks`; the postcomposition documentation joint `J6` passed without requesting corrections. The independence checker passed on the five valid scientific reports.

- **J5 procedure:** Attempt 1, owned by `eigenx-v2-j5`, was abandoned before artifact creation after a filename-format scan mechanically touched current J1/J3 filenames and violated strict mutual blindness. Attempt 2, owned by `reviewer-eigenx-j5-clean`, independently produced the only valid J5 report and was accepted by the checker.
- **Finite-action factorization:** For the exact prescribed-degree M=1 endpoint-plus-full-N-torsion interface, accepted mathematical decapsulation factors through `q_N=(d,e,theta(P_N),theta(Q_N))` and the independent rejection seed `z`. The complete saturated evaluable rank-four `End(E)` witness is not necessary for the declared recipient operation. This does not prove that `q_N` cannot be lifted to a complete ring; it refutes only the claimed necessity of the full witness for this interface.
- **Reduction direction:** The packet supplies no exact real-key challenge embedding, no decapsulation-oracle simulation without the withheld ring witness, and no extractor from attacker behavior to a complete efficiently evaluable rank-four basis. One recovered prescribed path also does not instantiate the arbitrary-input OneEnd/Isogeny oracle required by the cited completion theorems. O5 is therefore contradicted for this tested reduction, not universally.
- **Syntax, correctness, view, and cost:** The HHK outer theorem remains conditional because `TrapCurveGen_ER`, `SelectTrap`, canonical endpoint/point transport, validation, total `Dec0`, the actual correctness bound, the real adversarial distribution, and total operation/bit/memory/retry costs are unavailable. Accepted-key/per-path algebra is not an O3 discharge.
- **Source overlap:** The valid J5 review finds that Seta already supplies the endpoint-plus-full-torsion M=1 algebraic core and finite-action recovery. The added outer shell and unused complete-ring witness do not establish a materially different EndRing mechanism. The source metadata for Page--Wesolowski, Eaton--Jao--Komlo--Mokrani, Jana--Dutta, and Moriya--Stopar was corrected; the LIT-SiGamal and UPKE25 full-text retrieval limits remain explicit.
- **Six obligations:** O1, O2, O3, and O6 remain open. O4 and O5 are contradicted for the exact frozen interface. The reviewed-discharge count is zero, so the candidate is a scoped obstruction and is not admitted as an EndRing PKE/KEM.
- **Authenticated CEST boundary:** Authenticated CEST remains only a separate conditional accepted-key, single-user, classical-ROM `CEST-XFER-COMP`/`EvalLine_(P,A)` control with canonical parsing and public recognition. It is not EigenX-v2, is not EndRing-bound, and receives no construction, active-security, or deployment label.
- **Run boundary:** Zero scientific, implementation, formalizer, experiment, benchmark, and parameter-selection runs occurred. No measured result or parameter claim exists.

The problem remains `investigating`, and every exit criterion remains unmet. The exact EigenX-v2 interface is closed as a scoped obstruction; broader EndRing-PKE existence remains open.

## What would unblock it

Provide one of the following, then pass independent review:

- [ ] A polynomial-time reduction that receives an EndRing challenge sampled from the exact distribution used by EigenX KeyGen, simulates the complete declared IND game for an attacker, and outputs a valid complete evaluable `End(E)` basis with a quantified non-negligible success bound and total runtime.
- [ ] If the reduction uses Page--Wesolowski, a public-only algorithm or compiler that answers every adaptive bounded-OneEnd query generated by the reduction, with pointwise or transcript-conditional success, polynomial representation and degree bounds, bounded abort probability over the whole transcript, and no hidden path, orientation, ideal, torsion label, tag, or complete-ring data.
- [ ] A completed EigenX scheme contract in which O1--O6 each has an independently reviewed discharge under every named assumption and model, including complete honest algorithms, actual-message recovery, rejection behavior, the exact adversarial view, and concrete limitations.

The first two conditions are alternatives only if the direct reduction avoids the adaptive OneEnd path; the six-obligation discharge remains necessary for a construction. Meeting an adaptive bridge alone would not prove confidentiality, and meeting a `CEST-XFER-KI` theorem alone would not make the assumption EndRing.

## Prior discriminating step completed by BATCH-44a1ce

- **Action or proof obligation:** Execute the zero-run `BATCH-44a1ce` proof/construction search. Freeze the exact adaptive OneEnd transcript, test at most three materially distinct public bridge interfaces, and independently audit the full EigenX reduction chain and six obligations.
- **Inputs and controls:** The frozen Page--Wesolowski source packet from `TASK-20261009-daf6ab`; the CEST/EigenX candidate, scheme contract, and proof-search map; the `D_ER` sampler records; controls consisting of a single-distribution sampler, a non-uniform per-query adviser, the scalar-only hashed-DH slice, the reverse `EndRing solver -> decryptor` implication, a one-endomorphism-only witness, and pairing-visible transcript checks.
- **Execution limits and stop condition:** Zero scientific, implementation, benchmark, formalizer, and parameter-selection runs. At most three bridge interfaces and one frozen review round. Stop after independent composition and documentation review; do not add a PKE wrapper or claim automatic success.
- **Outcomes and next actions:** A fully typed bridge survivor advances only to a separate reduction/construction batch. A reviewed observable-fiber collision or quantifier counterexample becomes a scoped obstruction for that interface. No survivor preserves this problem as open and reranks a materially distinct EndRing construction mechanism. Inconclusive source or proof gaps remain inconclusive. Tool or model failure is infrastructure signal only.
- **Recheck trigger:** Completion of `BATCH-44a1ce`, a new reviewed direct CEST-to-EndRing reduction, a new adaptive OneEnd coverage theorem matching the frozen transcript, or a replacement EigenX construction with a materially different recipient mechanism.

A planned step is not a completed experiment. Apply the existing execution, review, budget, and archival rules before acting on it.

## Prior discriminating step completed by BATCH-be2a37

- **Action or proof obligation:** `ENDRING-MATERIALLY-DISTINCT-RECIPIENT-MECHANISM` -- rerank and bound one materially different recipient mechanism whose exact public transcript has ring-identifying behavior beyond `EvalLine_(P,A)`.
- **Acceptance criteria:** Give executable honest algorithms and the exact real-key law; prove actual-message correctness; simulate the complete declared adversarial view from the exact EndRing challenge; extract a complete efficiently evaluable rank-four `End(E)` basis with quantified success loss, runtime, memory, and representation cost; then pass independent O1--O6 review.
- **Controls and exclusions:** Reject another wrapper around the same line evaluator; separate scalar transfer from evaluator reconstruction and complete-ring extraction; exercise malformed, repeated, wrong-key, pairing-line, CCA, classical-versus-quantum, and reverse-arrow controls; use no hidden path, orientation, ideal, torsion label, tag, or ring advice.
- **Execution limits:** One bounded construction-or-obstruction round, with no automatic implementation, scientific run, successor, or security claim. A scoped obstruction names its exact interface and leaves universal existence open.
- **Outcome routing:** A fully reviewed survivor may advance only to a separately authorized design/validation batch. A typed failure updates this problem at its exact scope. An unresolved definition, construction, simulator, extractor, or cost obligation remains inconclusive.
- **Recheck trigger:** A new reviewed mechanism satisfying those criteria, a new direct CEST-to-EndRing reduction on the exact real-key distribution, or a replacement construction that no longer factors through `EvalLine_(P,A)`.

## Next action and stop boundary

- **Action:** Close `BATCH-be2a37` after its terminal ledger archive.
- **Stop condition:** Do not rank, open, implement, run, or promote another EigenX/EndRing successor unless a new explicit Coordinator decision and user-authorized scope names it.
- **Recheck trigger:** Such a new explicit decision and scope, or new externally supplied evidence that directly meets one of the existing exit criteria. Mere completion of this problem record, the batch archive, or the conditional authenticated-CEST control does not clear the obstruction.

## Resolution and history

- **2026-10-13:** Created from the CEST/EigenX O5 gap and the reviewed `BATCH-12e6aa` adaptive-coverage gap. `BATCH-44a1ce` is the bounded next investigation. Unresolved. Creating or merging this record does not establish a construction, security theorem, or impossibility result.
- **2026-10-13:** `BATCH-44a1ce` completed with no surviving bridge, O3 as the sole reviewed discharge, O1/O2/O4/O5/O6 open, a scoped I3 break, and an exact frozen-syntax IND-CCA2 break. J6 passed after `TASK-20261013-1c2b7a` and `TASK-20261013-b61e2d` corrected the PDF arrows/links and link-count metadata. The problem remains investigating, its exit criteria remain unmet, and the only recorded continuation is `ENDRING-MATERIALLY-DISTINCT-RECIPIENT-MECHANISM` with no automatic launch.
- **2026-10-13:** `BATCH-be2a37` completed the one authorized materially different prescribed-path/torsion candidate. J1--J5 all break; O1/O2/O3/O6 remain open; O4/O5 are contradicted only for the exact interface; no obligation has a reviewed discharge. J5 attempt 1 was abandoned without an artifact and clean attempt 2 owns the source-overlap verdict and metadata corrections. J6 passed the report set. The problem remains investigating with unmet exit criteria, and the batch closes without an automatic successor.
