# Controlled follow-up source review — TASK-20261029-182d42

J-math and J-radius hold within the assigned source-review scope; 17 independent fixture check groups passed. The sealed proof is preserved verbatim, including its explicitly reconciled raw-coefficient notation.

## Sealed independent derivation (sequence 1)

This proof was written before reading the new engine.py, constructor.py, curve.py, engine-source.md, or the old incremental prototype; before reading the earlier round's blind-derivation.md or design-audit.md. Inputs were the handoff/review-plan, decoder statement and parameters, and controls statement. Their algebra is checked below rather than adopted as an implementation.

Let E/F_p be nonsingular, p>3, and let the public subgroup have odd prime order r with r != p. Put t=-x/y at O. Define Z(R) as the coefficient of t in the normalized Miller function f_(r,R)=t^(-r)(1+Z(R)t+O(t^2)); take Z(O)=0. For a nonvertical chord/tangent of slope lambda, normalized line divided by the vertical line has expansion t^(-1)(1+lambda*t+O(t^2)). Its divisor is (R)+(S)-(R+S)-(O). Comparing normalized functions gives f_(r,R)f_(r,S)/f_(r,R+S)=(line/vertical)^r and hence

    Z(R+S)=Z(R)+Z(S)-r*lambda(R,S) mod p.

The sign is minus. For S=-R the line is vertical and has zero first normalized coefficient; Z(-R)=-Z(R). Identity additions have zero slope contribution. A tangent at y=0 is vertical and also contributes zero. These exceptions must use the group-law result and must never divide by zero. On the odd prime subgroup a nonidentity 2-torsion point cannot occur, but the arithmetic exception still needs defined behavior.

A fresh seed is not free: compute f_(r,R) by the binary Miller chain. Starting T=R and z=0, each scalar-chain doubling updates z <- 2z+lambda(T,T), T <- 2T; each required add-base step updates z <- z+lambda(T,R), T <- T+R, with the same vertical/identity conventions. At the final rR=O the accumulator is Z(R). Thus repeated query doubling instead uses Z(2R)=2Z(R)-r*lambda(R,R); replacing that minus by plus confuses the seed algorithm with the transport law. Missing seed construction, a zero seed, or an orbit/log-table seed is a different procedure. Every seed chain, slope and query remains charged.

For fixed public base B, let c=Z(B)/y(B), g(R)=Z(R)+c*y(R)*(alpha+beta*c*(x(R)-x(B))), and anchor=(1+alpha)Z(B). A ready setup requires valid public domain/base and nonzero denominators/anchor. Identity has its explicitly stipulated bit zero, separately from finite-point zero/undefined reasons. A zero normalized finite response is an erasure, not a bit selected for success. Undefined responses do not stop the fixed-L query schedule: point and Z continuation still advance through every position and every reason is retained.

For a coordinate isomorphism x'=u^2*x,y'=u^3*y with nonzero u, slope'=u*slope, and the same seed/transport recurrences imply Z'=u*Z. Hence c'=u^(-2)c, c'*(x'-x'(B))=c*(x-x(B)), g'=u*g, anchor'=u*anchor. The normalized response is identical with unchanged alpha,beta. Raw Z,g,anchor must be compared at their weight u; equal bits alone can miss an incorrect normalization. Zero/undefined branches transport under the same valid-domain assumptions.

For H(s)=floor(2s/r) on canonical 0<=s<r, write s_i=2^i*s mod r and h_i=H(s_i). Then s_(i+1)=2s_i-r*h_i, so by induction s/r=sum_(i=0..L-1) h_i/2^(i+1)+s_L/(r*2^L). Therefore V=sum h_i*2^(L-1-i)=floor(D*s/r), D=2^L, L=bit_length(r)+1. Each proposed word V corresponds to [rV/D,r(V+1)/D). Its length r/D<1, so the only possible scalar is s=ceil(rV/D)=(rV+D-1)//D. It exists iff 0<=s<r AND D*s<r*(V+1). The upper inequality is strict; V=0 includes s=0. Empty intervals are still generated, checked and charged.

If e positions are erased, assign each of their 2^e binary fillings and choose a subset of j<=min(t,L-e) distinct defined positions to flip. The words are pairwise distinct because their erased assignment and changed-defined subset are recoverable from the word. Thus the exact complete count, before interval rejection, is

    N=2^e * sum_(j=0..min(t,L-e)) binomial(L-e,j).

If e exceeds the fixed erasure cap, return a visible capped result after all L calls. With e within cap, enumerate the whole set once even after finding a success; duplicate, omitted or truncated words violate completeness independently of whether this target was recovered. The six prescribed cells t=0,1,2 crossed with e_max=0,2 share a trace, not independent queries. At t=0,e_max=0: any erasure gives the baseline undefined result; otherwise exactly one V is tested with the strict interval and both equations. This is the required embedding of the public fixed-L original ungated_attempt procedure, rather than an early-exit helper.

For P'=aP,Q'=bQ with nonzero public a,b modulo r and Q=xP, the transformed scalar is s=b*x/a and the original scalar is k=a*s/b modulo r. Verify BOTH [s]P'=Q' and [k]P=Q without short-circuiting one equation after the other fails. Conversion must use a*b^(-1), not b*a^(-1), a^(-1)b^(-1), or a*b. The zero candidate is legal as an interval point and incurs conversion/check costs, but it is excluded from the M distinct nonzero converted candidates used by a matched uniform-candidate reference. M is not the number of words, nonempty intervals with duplicates, or successful checks.

No marginal-bit independence follows. Hand control in Z/7: L=4; flip H only at {2,5}. Each doubling cycle {1,2,4} and {3,6,5} visits this error set within four queries, so all six nonzero starts have at least one wrong bit, q0=0, although marginal accuracy is 2/3 and (2/3)^4>0. This is hand derivation only, not executed abstract controls or a curve observation. A free choice of seed can counterfeit a recurrence locally; recurrence matching without a public seed chain is insufficient. Likewise accepting all residues as candidate fallback proves recovery for arbitrary predicates and invalidates any bounded-list attribution.

The algebra above is conditional on its stated normalized-function definition and public group assumptions. No primary Miller-function paper was retrieved in this stage; the definition and local Laurent expansion are exposed explicitly for subsequent source comparison. This is neither a proof that source implements the identities nor any scientific, complexity, exponent, or performance conclusion.

<!-- END SEALED PROOF -->

Sealed proof SHA-256: `d9ce34e707f04e8cfc7402738220192e2a3e936fb14c7f5687a6690aa9f6fb88`

Seal timestamp (UTC): `2026-10-29T18:57:55.239598+00:00`; event sequence 1. Hash covers exactly the UTF-8 proof section from its `## Sealed` heading through its final newline, excluding this metadata.

## Post-seal review

**J-math holds; J-radius holds**, within the assigned source/fixture scope and declared public-domain assumptions. No load-bearing defect was found in the actual candidate recurrence or bounded list implementation. This verdict does not compose J-isolation or J-delivery/J-metrics, admit a scientific study, or establish scientific, scalar-ordering, exponent or performance results.

### Normalization reconciliation and blindness limit

The sealed proof used Z for the raw first normalized Laurent coefficient C_r. Source constructor.py:14–33 instead defines Z_source=-C_r/r. This difference was discovered after sealing and is preserved rather than silently corrected in the proof. Applying that explicit scale to the sealed equation gives

    C_r(R+S)=C_r(R)+C_r(S)-r*lambda(R,S)
    Z_source(R+S)=Z_source(R)+Z_source(S)+lambda(R,S).

Engine.py:141–143 therefore correctly adds the slope. The binary seed chain accumulates C_r, then constructor.py:33 returns -r^(-1)C_r. At F11 P, the independent raw coefficient is 5 and source Z is 3; at F23 P they are 17 and 22. Negating the source transport slope gives F11's next Z=9 instead of 3 and fails trace equality.

The pre-seal derivation independently fixed the raw coefficient sign and scale, but did not use the source's naming convention. The source-named recurrence was reconciled after unblinding; this limits the blind notation match and is not a source-sign defect. The independent checker evaluates raw coefficients, scales them, and computes circuit values without producer arithmetic.

Sequence: public statements/governance; seal at 2026-10-29T18:57:55.239598+00:00 and hash sent to root; deliberate candidate source and prior-round derivation/audit reads; fixed-fixture checks. No current-round sibling report or outside sibling delivery was read. Initial broad filename discovery exposed paths only. The old incremental prototype was never opened, including after the seal.

### Source identity

All 26 source-file hashes in the snapshot receipt matched actual current bytes; the receipt itself has SHA-256 2c37b1860bce933f63b4529fedba2e8cbf5748b54c8a0187babdce4e105b110f. This makes 27 checked exact paths including the receipt. It names source commit d9e9ce106cdfbbf32a16120f84b028c21529d258 and code revision C=1b41962f1ae578b452319f1bf4b92f5388294093. Root supplied receipt commit f28bac0066 and pushed-input commit 16ef166fde. This session verified content bindings, not Git ancestry, push status or the claims token.

| Source under harness/classical_ecdlp_controlled_followup/ | Actual SHA-256 |
|---|---|
| engine.py | 22da83d6494ea66c520b0e58eaa4b54e621c822d8f0275deda8822c7179915fb |
| constructor.py | 31e58db07649df4e61ec2cbcaa1969789bc2c7f229c21f8555daaaaad8fdc451 |
| curve.py | 6ce0b50fcc78287de7091c36383b5ccefb5dbe208ba3d1ab1c80b1ddbc326400 |
| engine-interface.json | 3a7be27cbc28d1e0ddc062b640dbddac23b233bbfa8de3343b0963cb1e3e3cec |
| host/verify.py | 36ac222a98ba5567c7c050b13196ccf9b7cc0ba6ae8258c9f69c387b3c29b407 |

Other actual source/input hashes and read depths are in read-attestation.yaml and checks.json. Hash-only inventory is distinguished from source inspection. An independent AST comparison found engine.ungated_attempt identical to the historical harness/classical_ecdlp_transfer_successor/compute.py function, lines 114–171 (file hash 1a1a87ff84bfc748f6b86f893e53ea86979383c0adb0a68550c27eb9e8befad2). Constructor.py and curve.py are byte-identical to their historical counterparts. The early-exit conditional_recover was inspected and was not the matched reference.

### Observed fixed-fixture checks

The inline standard-library checker returned **RC0, 17/17 groups passed**. Its complete reproducible source and structured observations are retained in checks.json. It imports the candidate engine to exercise it; its expected arithmetic, raw Laurent coefficient, circuit, interval and list functions do not import producer arithmetic. This was software verification only. No VM, SDK, sampler, fresh nonce, cohort, old-cohort reanalysis, orbit/log table, benchmark or abstract Z7/Z31 control was executed.

Seven disclosed scenarios independently matched every non-counter field of original and incremental traces plus all six cells: F11 target (7,2) at a5/b1 and a5/b3; F11 base with circuit2; zero numerator at (5,2); zero anchor; wrong-root at (8,3); and F23 primary at P. F11 legacy recovers 7; its complete radius-two cell retains 16 words despite success at word index zero. F23's independently matched Z trace is (22,1,6,13,1,22), its bit trace is 001011, and its original attempt is REJECTED_FINAL_VERIFICATION. Failed, erased and empty outcomes remain in the check record.

The enumerator agreed with an independent exhaustive binary-word validator for **114 deterministic erasure/radius configurations**: 48 on fixed L5 F11, 66 on fixed L6 F23. Exact values, deterministic order, uniqueness and binomial count were checked. This exhaustive validator is restricted to the fixed software fixtures; the candidate uses bounded combinations rather than scanning all binary words.

| Control | Actual signature |
|---|---|
| Wrong transport sign | Second F11 Z becomes 9 rather than 3; paired equality rejects. |
| Zero seed | Full semantic trace differs. |
| Correct seed supplied free | Semantics agree; seed-call count drops from 1 to 0 and the seed-cost invariant rejects. |
| Stop on first undefined | Trace length becomes 1 despite declaring 5 calls; independent trace validation rejects. Correct source has 5 calls and 4 updates. |
| Omitted word | Engine raises enumeration count mismatch. |
| Equal-count duplicate replacement | Engine accepts 16 records with 15 unique values; independent complete ordered-word comparison rejects. |
| Stop after first success | One word differs from the required 16-word list. |
| Erasure-cap removal | Three erasures with cap2 produce 24 mutant words instead of a capped result. |
| Removed upper interval guard | At F11 V1, raw k1 becomes incorrectly legal and M changes from 0 to 1. |
| Wrong a/b conversion | At a5/b3, transformed scalar12 and word29 convert correctly to 7; b/a gives 2. Transformed check true, original false; both execute. |
| Zero word | Both equations fail, both scalar multiplications execute, zero_candidate_checks=1 and M=0. |
| Wrong coordinate beta weight | Normalized values 9 and 5 differ although both bits are 0. |
| Missing query row | Source rejects incomplete predicate trace. |

Normalization used field-weight arithmetic from the already disclosed F11 example and did not instantiate another curve. Identity, inverse/vertical and nonvertical tangent arithmetic were executed on disclosed points; F11 tangent slope is 8 and sum is (5,2). Valid order-two tangents and ZERO_BASE_Y are unreachable in these odd-order fixture subgroups: coverage there is source inspection and the domain argument, not an executed valid point. An injected zero seed is retained as ZERO_BASE_Z. The r=p domain mutation retains all five undefined calls.

### Strict-upper control limitation

Changing only the upper comparison from less-than to less-than-or-equal cannot change legal intervals here. Odd r is coprime to D=2^L. Equality Dk=r(V+1) forces r to divide k; 0<=k<r and V+1>=1 make this impossible. The endpoint k=r is already excluded by the range guard. An integer-only check of all 32 and 64 fixture words confirmed this expected equivalence. No failed equivalent mutant is fabricated. The inequivalent upper-guard removal above was rejected. Actual source retains the specified strict inequality at engine.py:298.

### Costs, defensive gap and next actions

Source retains setup, initial seed, shared-slope state updates, all L calls, conversion, list construction, empty intervals, zero candidates and both equations in separate cost families. The independent fixture checker checked limited invariants: one charged seed per ready incremental trace, L-1 updates, two scalar multiplications per legal word, word/bit payload counts, and M as distinct nonzero converted legal candidates. These checks are **not complete independent operation-counter execution replay**. Built-in integer internals, iterator/interpreter work, native allocation, RSS and I/O remain outside a fully qualified cost model, as disclosed by the interface. No counter or timing advantage is qualified.

No load-bearing actual-source defect was found on the assigned joints. One concrete defensive/test gap remains: engine.py:313 checks only count, allowing an equal-count duplicate mutation through its local assertion. Actual enumerate_words is unique by construction and passed independent coverage checks. Host/verify.py:384–400 statically reconstructs every ordered word, geometry, interval, conversion and equation and would reject this mutation. That host path was read but not executed here; its lifecycle belongs to another joint. Preserve the complete host comparison as a required gate and add an equal-count duplicate regression that executes it at the next source revision. The local count assertion alone is not a completeness certificate.

Root's next work is to compose the independent joint reports, retain source/input/runtime bindings, freeze future nonce namespaces/caps/exclusions/controls/counts/analysis/cost definitions, establish candidate-only execution with post-termination host work, and record source-bound protocol/preapproval/standing-authorization archive/checkpoint before a lawful run. No new study is frozen or launched by this review. Counter replay and qualified clocks require separately scoped evidence.

### Literature, provenance and independence limits

Public decoder/controls reports and design informed scope. Prior-round derivation/audit were read only after sealing. These are internal records, not newly retrieved primary evidence. No external theorem, AGS learner or statistical calibration result establishes the elementary recurrence/interval/list claims here. Primary Miller/AGS papers were not retrieved in this constrained review; no primary-proof completeness, novelty or historical-experiment reproduction is claimed. Knowledge-specific tools were absent in discovery. Hashes establish byte identity, not universal correctness or an error law.

The fresh child session /root/controlled_source_review did not originate the producer package. Requested policy is review-adversarial and requested effort xhigh. Actual serving backend, resolved model, usage, probe and achieved effort were not independently verified and remain null. Pairwise model/backend independence is unverified. The independence claim concerns the disclosed session/source/blindness procedure.

No canonical files, claims, Git state, credentials, releases or publication changed. The three assigned outside files are the complete delivery. The source-map diagram in engine-source.md was checked for relevance; no scientific graph changed. Root owns composed decision/PDF/canonical-graph publication within its assigned scope. The inline map is derived communication only.

```mermaid
flowchart LR
 A[Public statements and parameters] --> B[Sealed derivation]
 B --> C[Source read and explicit scale reconciliation]
 C --> D[Independent fixed-fixture controls]
 D --> E[Assigned joint verdicts for root composition]
```

## Review attestation

```yaml
{
  "review_attestation": {
    "blind_from_respected": true,
    "blind_from_respected_scope": "derivation phase only, as required by this staged plan; exact implementation reads are disclosed post-seal",
    "joint_verdicts": {
      "J-math: normalized public transport/seed and exact trace equality": "holds",
      "J-radius: complete/count/strict-interval/conversion semantics": "holds"
    },
    "joints_owned": [
      "J-math: normalized public transport/seed and exact trace equality",
      "J-radius: complete/count/strict-interval/conversion semantics"
    ],
    "read_sibling_reports": false,
    "sources_read": [
      "AGENTS.md",
      "agents/coordinator.md",
      "agents/red-team.md",
      "agents/validator.md",
      "docs/agent-contract-extended.md",
      "docs/lab-contract.md",
      "docs/skill-routing.md",
      ".claude/skills/route/SKILL.md",
      ".claude/skills/review-evidence/SKILL.md",
      "ledger/handoffs/TASK-20261029-182d42.yaml",
      "coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-2fe40f/review-plan.yaml",
      "coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-2fe40f/archives/TASK-20261029-b039c4/snapshot-receipt.json",
      "docs/reports/classical-ecdlp-further-leads-20261029/decoder/report.md",
      "docs/reports/classical-ecdlp-further-leads-20261029/decoder/experiment-design.json",
      "docs/reports/classical-ecdlp-further-leads-20261029/controls/report.md",
      "ledger/goals/GOAL-ECDLP-e70832/goal.yaml",
      "harness/classical_ecdlp_controlled_followup/engine.py",
      "harness/classical_ecdlp_controlled_followup/constructor.py",
      "harness/classical_ecdlp_controlled_followup/curve.py",
      "harness/classical_ecdlp_controlled_followup/test_engine.py",
      "harness/classical_ecdlp_controlled_followup/engine-interface.json",
      "harness/classical_ecdlp_controlled_followup/engine-delivery.json",
      "docs/reports/classical-ecdlp-controlled-followup-20261029/engine-source.md",
      "docs/reports/classical-ecdlp-further-leads-20261029/review/blind-derivation.md",
      "docs/reports/classical-ecdlp-further-leads-20261029/review/design-audit.md",
      "harness/classical_ecdlp_controlled_followup/host/verify.py",
      "harness/classical_ecdlp_transfer_successor/compute.py",
      "harness/classical_ecdlp_transfer_successor/constructor.py",
      "harness/classical_ecdlp_transfer_successor/curve.py",
      "docs/agent-contract-supplement.md",
      ".claude/skills/research-visuals/SKILL.md",
      "orchestration/roles.yaml",
      "orchestration/model-policies.yaml",
      "orchestration/model-bindings.yaml",
      "templates/research-records.md",
      "tools/check_review_independence.py",
      "docs/reports/classical-ecdlp-controlled-followup-20261029/transport-source.md",
      "docs/reports/classical-ecdlp-controlled-followup-20261029/verifier-source.md",
      "harness/classical_ecdlp_controlled_followup/cohort.py",
      "harness/classical_ecdlp_controlled_followup/controller.py",
      "harness/classical_ecdlp_controlled_followup/driver.py",
      "harness/classical_ecdlp_controlled_followup/host-source-manifest.json",
      "harness/classical_ecdlp_controlled_followup/host/reference.py",
      "harness/classical_ecdlp_controlled_followup/host/test_verify.py",
      "harness/classical_ecdlp_controlled_followup/host/verifier-delivery.json",
      "harness/classical_ecdlp_controlled_followup/host/verifier-interface.json",
      "harness/classical_ecdlp_controlled_followup/postrun/analysis.py",
      "harness/classical_ecdlp_controlled_followup/postrun/render_report.py",
      "harness/classical_ecdlp_controlled_followup/postrun/run_postrun.py",
      "harness/classical_ecdlp_controlled_followup/postrun/test_postrun.py",
      "harness/classical_ecdlp_controlled_followup/test_transport.py",
      "harness/classical_ecdlp_controlled_followup/transport-delivery.json",
      "harness/classical_ecdlp_controlled_followup/worker-source-manifest.json",
      "harness/classical_ecdlp_controlled_followup/worker_runtime.py",
      "skill://plugin_connector_1p_c5b7d5df5d7081918f2c4be5a633ed5d/cloud-environment-runtime/SKILL.md"
    ],
    "task_id": "TASK-20261029-182d42",
    "verdict": "holds"
  }
}
```
