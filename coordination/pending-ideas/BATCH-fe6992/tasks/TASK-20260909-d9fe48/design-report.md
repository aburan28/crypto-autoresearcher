# Persistence design delivery — TASK-20260909-d9fe48

The corrected persistence proposal IDEA-20260905-d76d38 now has a complete, unrun finite certificate protocol under RQ-DREG-72c2b0: H-DREG-cdd4b0, EXP-DREG-68236e and the prospective scientific handoff TASK-20260909-42ee18. DEC-20260909-3eee78 records completion for fresh independent protocol review only. The experiment remains review_required with approved_by:null. No implementation, formal proof, scientific measurement or independent review occurred in this task.

The seven files are owned exclusively by this task. Parent validation and the separate design snapshot TASK-20260909-acfaea remain the next custody step. The source-audit maps 21 substantive source obligations to specification fields and binds the other six final files; the parent snapshot will bind all seven without a self-hash cycle.

## What is being certified

For an ordered presentation F in an ordinary polynomial ring over a declared field, V_F,E is the least linear space of degree at most E containing the eligible original generators and closed under all monomial products satisfying deg(g)+deg(mu)<=E. The complete one-shot span U_F,E of original-generator multiples is a separate object. A low-degree consequence can become available through iterated closure before it has a raw expanded representation at that same degree. The protocol retains the entire derivation history, so a consequence never becomes a free new input.

The reported finite object is every P_d,E=V_F,E intersect A_d for 0<=d<=K and 0<=E<=Emax, with full bases and inclusion maps in both indices. The full closed spaces and all fall slices V_F,E intersect A_(E-1) are also retained, even when E-1>K. A canonical basis adapted to the nested P_K,E spaces records exact birth degrees and all changes of basis. Complete spanning and coset-independence certificates justify the earliest degree of every linear combination in this finite target space. This is a complete finite bifiltration, without a claim to classify an infinite ideal or a general two-parameter barcode.

Every reported minimum for the same exact target f requires a positive derivation circuit and an exclusion certificate at every smaller integer E. A linear functional must annihilate a certified complete closed-space basis and take value 1 on f. Degrees below deg(f) retain an explicit out-of-degree coefficient and the full zero-column embedding. Soundness of a derivation is separate from completeness of the space: all original generators and every admissible product of every degree-filtered basis must be included, with exact transforms. Neither selected-column rank nor a failed search establishes nonmembership.

Boolean fixtures have two paired presentations. O is the ordinary F2 polynomial ring with explicit field equations. Q is the squarefree Boolean quotient, with multiplication admitted by the degree sum before normal-form reduction. Both retain the same normalized core generators. The quotient normalization, lift differences, and proposed maps carry explicit witnesses and costs. Their degree values and ranks are never silently identified.

Polynomial output degree, earliest iterated derivation delta, one-shot minimum E_raw, expanded witness degree E_exp, first and last observed closure fall, true last fall, reduced-basis output degree and solving degree remain separate metrics. A complete ordinary Gröbner basis and every relevant certified minimum are prerequisites for true global degree values. An incomplete endpoint or a quiet window leaves lower bounds or right-censored values. The ordinary theorem is not imported into Q without a separate interface proof.

## Fixed source panels and controls

The protocol contains 510 explicit parameter slots: 85 source slots and 425 null slots, split into 277 calibration and 233 holdout slots. The null total consists of 357 coefficient nulls, 20 exact-support identity nulls and 48 Boolean degree-histogram support nulls. There are no learned policies or result-driven changes between phases. The source specified the required kinds of controls and the later 8/10/12-bit S3 boundary, but did not specify these numerical counts; this design chooses and freezes them before review.

| Reserved run | Family and presentation | Slots | Target ceiling K | Degree window |
|---|---|---:|---|---|
| RUN-DREG-554a55 | SYN Q O | 16 | 3 | 0..6 |
| RUN-DREG-3a2468 | SYN F2 O | 8 | 3 | 0..6 |
| RUN-DREG-370ff9 | SYN F101 O | 16 | 3 | 0..6 |
| RUN-DREG-228749 | L F3 O | 4 | 2 | 0..6 |
| RUN-DREG-6d9440 | L F5 O | 4 | 4 | 0..10 |
| RUN-DREG-22fbf6 | L F7 O | 4 | 6 | 0..14 |
| RUN-DREG-39ad55 | BOOL F2 (n=2) O | 20 | 5 | 0..8 |
| RUN-DREG-3d43d1 | BOOL F2 (n=2) Q | 20 | 5 | 0..8 |
| RUN-DREG-b2520a | BOOL F2 (n=3) O | 20 | 6 | 0..9 |
| RUN-DREG-04abf9 | BOOL F2 (n=3) Q | 20 | 6 | 0..9 |
| RUN-DREG-78343f | S3 F251 O | 126 | 2, 4, 6 by base | 0..12 |
| RUN-DREG-c331f4 | S3 F1021 O | 126 | 2, 4, 6 by base | 0..12 |
| RUN-DREG-32cb95 | S3 F4093 O | 126 | 2, 4, 6 by base | 0..12 |

The synthetic controls use Q, F2 and F101. M=(x^2,y^3) preserves the corrected homogeneous monomial baseline: ideal membership is divisibility and an ideal monomial is derivable at its own degree. CI=(x^2,y^2) is a matched complete intersection with no degree falls. Matching means the declared field, ambient variables, generator count and degree/Hilbert profile; it does not assert equal roots or identical support.

The explicit pair A=(x^2,xy-1) and B=(x^2-1,x^2-2) has the same proposed reduced affine output basis {1}, while the manual control predictions are delta_A(1)=3 and delta_B(1)=2. In A, x=y*f1-x*f2 is a degree-3 consequence, after which multiplication and subtraction produce 1. Its expanded identity 1=y^2*f1-(xy+1)*f2 has raw product degree 4. The lower-degree exclusions are mandatory future certificates, not facts inferred from the displayed upper witnesses.

With a distinguished homogenizing variable h, the generated ideals J_A=(x^2,xy-h^2) and J_B=(x^2-h^2,x^2-2h^2)=(x^2,h^2) have the proposed common Hilbert series (1-t^2)^2/(1-t)^3. The intended regular-sequence argument is explicit: the second polynomial for J_A is monic in h over the quotient by x^2, and J_B has an invertible generator change to (x^2,h^2). A full exact regularity/Hilbert certificate is required. Agreement of a short prefix cannot replace it. These are generic synthetic control presentations; they do not establish the source conjecture about Semaev-related presentations or compact complete persistence certificates.

The native L family retains (x^2-x,xy-1,w^q-w,w^(q-1)*z^(q-1)-1) in ordinary F_q[w,x,y,z] for q=3,5,7, without additional field equations. The source predicts early degree 3 and later degree 2q-1. The separate native first-fall calculation uses the source homogeneous truncated ring and its complete trivial-syzygy quotient, including original shifted generator tags whose top forms map to zero. It is not a first closure cancellation with a renamed label. Finite members expose premature stabilization, while the generic family remains the source of the arbitrarily late-gap control.

BOOL uses genuine three-leaf chained S3 systems over F_(2^2) and F_(2^3), with the exact irreducible-polynomial candidates, curves, coefficient basis, leaf bits and internal coordinate fixed. Both O and Q receive identical normalized core draws. S3 uses prime fields 251, 1021 and 4093, three supplied curves, bases of sizes 2, 3 and 4, and two deterministic rational targets per cell. Every supplied field, curve and target condition must be checked. Missing target supply is an incomplete fixture, with no replacement or denominator reduction. Algebraic roots lacking compatible rational point lifts remain in the record; intermediate points at infinity are outside the affine Boolean-chain object.

Coefficient nulls preserve exact realized support after specialization in the actual field. F2 has no nonzero coefficient randomness on fixed support, so its identity null is explicitly degenerate. The separate Boolean support controls preserve each row's degree histogram and remain differently labelled. Rejection draws, duplicate polynomials, zero slots and failed eligibility checks are retained. No null is forced to have a desired rank, number of roots or semiregular behavior.

Five verifier mutations per natural run unit give 65 separate negative checks. They change a coefficient, omit a lower-rung certificate, delete a mandatory ambient column, omit a closure product, or alter the target/field/quotient/degree contract. They are additional controls within the 13 run units, not another 65 scientific fixture slots or five extra experiments per fixture.

## Completeness, cost and inference limits

The cold reference rebuilds each degree closure from the original presentation. The incremental candidate imports the prior closed basis with its original derivation circuits, then completes all current original rows and closure products. Every cache, transform, failed candidate and recheck is charged. The one-shot comparator has a separate certificate restriction. Endpoint data cannot select targets or guide either measured closure.

Independent endpoints use complete Gröbner certificates for synthetic/native ideals and complete finite-grid/CRT certificates for the membership-constrained S3 and Boolean systems. Every ideal-space equality requires both inclusions, not a root count or matching dimension. The proposed grid interpolation bounds and degree-compatible basis coverage are explicitly manual proof obligations. Complete endpoint bases are queried against the measured filtration before true ordinary last-fall or solving-degree labels can be supplied.

Full construction and checking cost includes field/curve/target acquisition, coordinate expansion, every ambient column, original row, admissible and failed product, closure pass, target intersection, lower-rung dual, basis map, derivation circuit, expanded original-generator witness, endpoint/point check, serialization and spill I/O. Field-operation counts and the unit-weight W proxy appear beside coefficient growth, CPU/wall, peak live/RSS, stored, witness and spill bytes. A compact circuit or smaller column count does not hide a large expansion. Single measured timings would be descriptive, not a replicated speedup claim. Each process is limited to 8 GiB and one worker; routine time estimates are advisory and the scientific counts stay fixed.

The primary definitions and theorem interface were actually read in Caminata–Gorla, arXiv:2112.05579v2, including the ordinary closure/minimum definitions, the basis/last-fall relation, the solving-degree theorem and native separation example. Only the input S3 formulas and their model assumptions are taken from Semaev, arXiv:1504.01175v1, Section 2. No first-fall assumption or attack estimate is adopted. Citation locations, versions and actual reader attribution are in the source-audit. The current eprint retrieval failure and absent KB tools are recorded honestly. [Caminata–Gorla primary paper](https://arxiv.org/pdf/2112.05579v2); [Semaev primary formulas](https://arxiv.org/pdf/1504.01175v1).

The hypothesis remains untested and the full time/memory/data frontier unresolved. A modeled column ratio supplies no measured cost gain. The Semaev-specific same-Hilbert and compactness conjectures remain open beyond any later finite certified observation. DREG's n=12,15,18 and at least three-seed completion requirements are not met by this panel. PATH remains advisory. SDEG still needs its separately governed verifier/precommit/launch and complete matched attack-cost chain. No goal or existing hypothesis status is changed.

## Prospective execution and review custody

The chain has 22 future cards using the reserved scientific task plus all 21 newly allocated tasks. Every card is prospective and blocked until actual adoption, prerequisite publication and a matching owner/epoch claim. The sequence is design snapshot, fresh protocol review and published review snapshot, a distinct approval producer and snapshot, implementation and snapshot, formal preparation and snapshot, formal work and snapshot, independent operational/semantic QA and its decision-only ledger, launch preparation and snapshot, scientific work and run snapshot, statement/claim packet and snapshot, three independent evidence roles, then the Coordinator ledger.

| Task | Role | Responsibility | Direct prerequisites |
|---|---|---|---|
| TASK-20260909-6e29ba | validator | Independently review full persistence protocol | TASK-20260909-d9fe48, TASK-20260909-acfaea |
| TASK-20260909-3ea56b | coordinator | Archive exact TASK-20260909-6e29ba | TASK-20260909-6e29ba |
| TASK-20260909-df9062 | coordinator | Record separate post-review persistence approval | TASK-20260909-3ea56b |
| TASK-20260909-523a4d | coordinator | Archive exact TASK-20260909-df9062 | TASK-20260909-df9062 |
| TASK-20260909-f3aaec | executor | Implement complete persistence and independent certificate engine | TASK-20260909-523a4d |
| TASK-20260909-432d38 | coordinator | Archive exact TASK-20260909-f3aaec | TASK-20260909-f3aaec |
| TASK-20260909-8b3a8a | coordinator | Freeze actual formal target and toolchain pins | TASK-20260909-432d38 |
| TASK-20260909-7e9ffa | coordinator | Archive exact TASK-20260909-8b3a8a | TASK-20260909-8b3a8a |
| TASK-20260909-b16af6 | executor | Formalize actual closure/minimum certificate and SYN A/B controls | TASK-20260909-7e9ffa |
| TASK-20260909-a723b1 | coordinator | Archive exact TASK-20260909-b16af6 | TASK-20260909-b16af6 |
| TASK-20260909-a52bc3 | validator | Independently qualify persistence engine, formal semantics and locked mapper | TASK-20260909-f3aaec, TASK-20260909-432d38, TASK-20260909-b16af6, TASK-20260909-a723b1 |
| TASK-20260909-21bf72 | coordinator | Archive exact TASK-20260909-a52bc3 | TASK-20260909-a52bc3 |
| TASK-20260909-61b5e8 | coordinator | Prepare actual persistence lock and separate scientific launch authority | TASK-20260909-21bf72 |
| TASK-20260909-73d469 | coordinator | Archive exact TASK-20260909-61b5e8 | TASK-20260909-61b5e8 |
| TASK-20260909-42ee18 | executor | Execute the complete locked persistence panel | TASK-20260909-73d469 |
| TASK-20260909-0dfd99 | coordinator | Archive exact TASK-20260909-42ee18 | TASK-20260909-42ee18 |
| TASK-20260909-b53a90 | coordinator | Freeze actual evidence-review claim and statement-only packet | TASK-20260909-0dfd99 |
| TASK-20260909-bacfc6 | coordinator | Archive exact TASK-20260909-b53a90 | TASK-20260909-b53a90 |
| TASK-20260909-8e381e | validator | Validate actual persistence custody and complete certificates | TASK-20260909-42ee18, TASK-20260909-0dfd99, TASK-20260909-bacfc6 |
| TASK-20260909-8ca312 | red-team | Challenge persistence full costs, controls and scope | TASK-20260909-42ee18, TASK-20260909-0dfd99, TASK-20260909-bacfc6 |
| TASK-20260909-9202ca | validator | Blindly derive the concrete persistence separation | TASK-20260909-42ee18, TASK-20260909-0dfd99, TASK-20260909-bacfc6 |
| TASK-20260909-d1bcdc | coordinator | Archive exact TASK-20260909-8e381e, TASK-20260909-8ca312, TASK-20260909-9202ca | TASK-20260909-8e381e, TASK-20260909-8ca312, TASK-20260909-9202ca |

The QA archive TASK-20260909-21bf72 owns DEC-20260909-a5669e and has no invented evidence record. Scientific approval is reserved for DEC-20260909-8228d6 after the actual protocol-review snapshot. The launch decision is DEC-20260909-b2d062. The final evidence/decision reservations are EV-DREG-e397ad and DEC-20260909-0e6b2a. None exists as a future verdict in these files.

Concrete formal work remains unmet. Formal preparation must freeze an actual available Lean toolchain, immutable library/dependency identities and exact statements before any verifier runs. The declared targets cover the actual polynomial closure/dual minimum interface and concrete A/B degree/Hilbert obligations. A theorem that simply assumes those identities or minima, or a compiler smoke test, cannot discharge them. Independent semantic QA must check the formal statements against this polynomial contract. Missing pins or definitions produce a precise preparation impediment without weakening the scientific claim.

Operational QA requires this experiment's exact finite-YAML mapping, complete immutable source closure, external expected LOCKED hash, case-specific filesystem/output behavior, native provenance and current claim checks. Twelve synthetic QA cases retain their actual before/after artifacts. Old shared-runner QA FAILs, separately owned repairs and test-only changes supply no readiness for this experiment. No raw unqualified script may bypass admission.

The protocol reviewer has a recorded prior, uniquely assigned joints and worked attack plans. Later evidence review uses an actual claim-bound plan and separately published statement-only packet. Validator, Red Team and blind re-deriver have direct scientific-producer dependencies as well as run/packet snapshots. The blind re-deriver receives raw A/B statements and parameters without expected minima, producer reports, code or peer verdicts. No future report or whole-claim verdict is filled in now. Breakthrough, closure or validated-evidence contradiction would require separately admitted undegradable review-breakthrough at max.

## Current custody and remaining action

The current owner claim is epoch 1 for coordinator-pending-ideas-swarm-20260907 under controller 01a07e0d-9f07-7382-a7d3-e2f0b4cf08de. Its declared expiry is 2026-09-09T09:21:26Z and it is reread before writing. The parent-produced live plan passed all 11 gates for the two disjoint designers. The source audit distinguishes the copied prospective metadata from actual canonical adoption and the live claim.

The directly read native capsule records OpenAI/gpt-6-astra at literal ultra in session 01a083fc-b86f-7000-91e0-df2fe6b9fe9b. model_verified remains false because no serving probe occurred. The task workdir is /Volumes/SSD990/1083/certificate-intake-20260909; metadata cwd is /Volumes/SSD990/1083/crypto-autoresearcher. Both are recorded. No fallback or degradation was used.

Parent preparation preflight, ledger and hygiene checks passed for the intake. The later parent intake ledger report accepted 11547 records with no new violations under its explicit baseline/index/supersession policy; it did not erase the recorded legacy issues. Those observations validate intake custody only. No harness command, test, numerical/symbolic sweep, implementation or formal check was executed by this designer, and no current-design validation pass is claimed. Parent must run the actual scoped checks on these stopped bytes and publish TASK-20260909-acfaea before fresh protocol review can begin.

## Prepublication administrative correction

On 2026-09-09T07:57:48.397Z, the parent requested the required nonempty knowledge_promotion.not_warranted field in DEC-20260909-3eee78. Its value states the existing reason that no validated scientific finding warrants knowledge promotion. The parent targeted-record check and full ledger log had reported exactly that one new schema error; the combined 26-card structural projection exited 0 with all 11 gates true, and the standalone scientific handoff matched its task card. These observations concern administrative consistency only. This revision adds the missing field and refreshes audit/report custody; the hypothesis, experiment, scientific handoff, proposed queue and all 510/13/65 scientific definitions remain byte-identical. Parent final record/ledger rechecks are still pending. The initial seven files are preserved losslessly in admission/persistence-initial-design-delivery-20260909.json.gz, parent publication commit 0bc556fdb4. No experiment, formal check or scientific approval follows from this correction.
