# Red Team Falsification Review
## TASK-20260805-9f2d71 reviewing TASK-20260805-a1c3f9 (GOAL-MLDSA-001 BATCH-001)

**Verdict:** `pass_with_constraints`  
**Reviewed:** 2026-08-05  
**Session:** Independent of producer session (same backend, different instance)  
**Policy:** review-adversarial (fallback: resolved to amazon-bedrock/us.anthropic.claude-sonnet-4-6)

---

## Preface

This review attacks the batch's own framing, not ML-DSA. The four named duties are:

1. Source-exhaustion check
2. Prejudgment check (inventor protocol §4)
3. Rule-7 discipline check
4. Scope-inflation check

Plus supplementary OBJs from the handoff brief: Pareto honesty, correction propagation, and minimum-for-next-batch assessment.

---

## Duty 1 — Source Exhaustion: Was FIPS 204 Actually Obtained?

### Producer's claim
> "CSRC publication page retrieved (HTTP 200); abstract, DOI, metadata verified. PDF served but not text-extractable via this tool."

### Independent verification

This review independently fetched four routes:

| Route | Attempted by producer? | Outcome |
|---|---|---|
| `https://csrc.nist.gov/pubs/fips/204/final` | YES | HTTP 200, CSRC page with title, abstract, keywords, document history. No standard body. **Confirms producer.** |
| `https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.204.pdf` | YES | Binary PDF byte stream (`%PDF-1.7` header visible). Not text-extractable. **Confirms producer.** |
| `https://doi.org/10.6028/NIST.FIPS.204` | NO | Returns only a citation metadata string: `"(Ed.). (2024). Module-lattice-based digital signature standard. National Institute of Standards and Technology (U.S.)."` Not document text. |
| `https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.204` (HTML route) | NO | HTTP 404. No HTML version of FIPS 204 exists at this path. |

**Finding: The binary PDF blocker is GENUINE.** All four routes independently fail to provide the standard body as extractable text. The barrier is a tool capability limitation (the `webfetch` tool returns raw PDF byte streams without text extraction), not a network or proxy block.

**Minor gap:** The producer's `source_access_log.yaml` declares only 2 routes. The DOI redirect and the no-extension HTML path were not declared. However, since this review independently tested and confirmed both additional routes also fail, the route-exhaustion outcome is the same. The log is incomplete as a formal record; the substance is correct.

**Objection OBJ-B [MINOR]:** Source access log should be augmented to record the DOI and HTML routes as tested-and-failed, completing the formal route-exhaustion record. This review's independent test log may serve that purpose. No reopening of producer work is required.

**Control:** Ledger archive task (TASK-20260805-c60b84) should note that this red team review completed route exhaustion via independent testing of 2 additional routes, both confirming no text-accessible FIPS 204 version.

**Pause condition analysis:** GOAL-MLDSA-001 pause condition 2 reads: "Neither the FIPS 204 text nor the primary fault-security proof can be obtained under the network policy after the declared source-preference order is exhausted." The blocker here is tool capability, not network policy — the PDF was served (HTTP 200), it simply cannot be decoded as text by the webfetch tool. This is materially different from a proxy CONNECT 403. The pause condition text says "network policy," which does not strictly include tool capability limits. The Coordinator must explicitly rule at the ledger archive whether this distinction matters for constraints[0] discharge.

---

## Duty 2 — Prejudgment Check (Inventor Protocol §4)

### Test: Does the batch treat SelfTargetMSIS as open in both directions?

**Reading corpus_dedup_report.md:** Scrupulously neutral. Every census entry verdict is limited to coverage/no-coverage of the priority sources. No inference about ML-DSA's security in either direction.

**Reading fault_literature_summary.md:** The summary's source characterizations:
- Source A (2026/1344): "recovery of the secret key enables forgery, but the attack is physical (clock glitching / fault injection), not an attack on MLWE, MSIS, or SelfTargetMSIS."
- Source B (2024/238): "Physical / implementation-level attack; does not break MLWE, MSIS, or SelfTargetMSIS as mathematical problems."
- Source C (2026/1188): "NOT a mathematical attack on MLWE, MSIS, or SelfTargetMSIS." Characterized as a leakage ceiling, not a security reduction.

The characterization of 2026/1188 as providing "the formal anchor that allows each published attack to be classified as inside or outside the formal guarantee" is accurate description of what a machine-checked proof's stated scope provides. It does not assert: "ML-DSA's fault resistance is sufficient," nor does it assert "ML-DSA is weak." It correctly relays the scope of one specific formal result.

**Batch-level framing:** The batch.yaml states the batch "asserts nothing about ML-DSA's security in either direction." The receipt.yaml states `states_a_finding: false`. The proposed KN-LIT entry for FIPS 204 marks all technical security claims `NOT_VERIFIED`.

**Finding: NO PREJUDGMENT.** Both directions remain genuinely open. The batch does not leak in either direction. **No objection.**

---

## Duty 3 — Rule-7 Discipline Check

### Test: Are fault attacks described (even loosely) as breaks of MLWE, MSIS, or SelfTargetMSIS?

**Explicit classification in fault_literature_summary.md:**

| Source | Classification given |
|---|---|
| ePrint 2026/1344 (Shin et al. DFA) | "IMPLEMENTATION / FAULT ATTACK" |
| ePrint 2024/238 (Jendral voltage glitch) | "IMPLEMENTATION / FAULT ATTACK" |
| ePrint 2026/1188 (Gupta rank ceiling) | "IMPLEMENTATION / FAULT — FORMAL LEAKAGE BOUND" |

Summary statement: "All three sources are IMPLEMENTATION/FAULT/SIDE-CHANNEL in character. None constitutes a mathematical attack on MLWE, MSIS, or SelfTargetMSIS."

**Formal proof boundary reporting:** The 2026/1188 boundary statement is relayed verbatim from the abstract: "No combination of twiddle-perturbation faults, however large, shrinks it further." The scope is reported as the source states it — NTT twiddle-perturbation faults only — without paraphrase into a broader or narrower claim.

**Key distinction preserved:** The dedup report correctly distinguishes KN-LIT-3907 ("Fixing and Mechanizing the Security Proof of FS-with-Aborts and Dilithium" — mathematical ROM/QROM CMA-to-NMA security reduction) from ePrint 2026/1188 (implementation NTT fault leakage bound). These address different proof obligations at different layers. Conflating them would have been a rule-7 violation. The batch avoids this.

**Finding: CLEAN.** Rule-7 discipline observed throughout. **No objection.**

---

## Duty 4 — Scope-Inflation Check

### Test: Does anything imply a claim above the toy/until-certified ceiling?

**FIPS 204 proposed entry:** `key_claims` are annotated with "(Source: CSRC abstract — standard body not read)" and the `not_verified` section explicitly enumerates what was not read (MLWE/MSIS/SelfTargetMSIS definitions, security proof structure, security theorem, which assumption binds at each parameter set). The entry's `confidence: reported` signals the appropriate claim tier.

**fips204_transcription.md honesty statement:**
> "The claims about MLWE, MSIS, and SelfTargetMSIS in RQ-MLDSA-001's motivation are flagged UNVERIFIED there. They remain unverified here."

**Batch scope:** "This batch runs no experiment, tests no hypothesis about MLWE, MSIS, or SelfTargetMSIS, and asserts nothing about ML-DSA's security in either direction."

**Finding: CLEAN.** Acquiring a text is never conflated with validating its content. Scope ceiling enforced. **No objection.**

---

## Supplementary OBJ-A — Pareto Honesty / dominated_by

**Finding: MODERATE GAP.**

None of the 5 proposed KN-LIT entries includes a `dominated_by` field. The inventor protocol §5 requires `dominated_by` for "every ideation or closure session" (this session's agent role is `idea-generator`). However, §5 defines `dominated_by` as "the best-known result that dominates this one, in the Pareto sense across every cost axis (time, memory, data/queries)" — a concept designed for algorithmic results, not bibliography entries. The natural KN-LIT analog for a superseded document is `superseded_by: null`, which all five entries carry.

The substantive concern is **Entry 4 (Ravi et al. 2022, ePrint 2022/737)**. The handoff explicitly flags it: "a fault-attack source from 2022 is potentially dominated by one from 2026." This review finds:

- The same proposal package contains two 2026-era targeted papers: 2026/1344 (DFA on ML-DSA challenge sampling) and 2026/1188 (formal NTT twiddle fault bound).
- The Ravi 2022 survey covers a broader taxonomy of SCA/FIA on Kyber and Dilithium (taxonomy and countermeasures at pqm4/Cortex-M4 level, IEEE Trans. Computers — venue UNCONFIRMED from ePrint record).
- For RQ-MLDSA-001's specific goal — placing published fault attacks inside or outside the formal proof boundary — the 2026-era targeted papers may cover all needed content, making the 2022 survey redundant.
- Alternatively, the survey's historical taxonomy and countermeasure analysis may be worth retaining even if the targeted papers are more specific.

**The batch leaves this unresolved.** Before filing Entry 4, the Coordinator must explicitly determine whether it is dominated by the 2026-era entries for the purposes of this research question, and must confirm or disclaim the IEEE Trans. Computers venue claim.

**Control (cheapest):** Before filing, answer: does the Ravi 2022 survey add, for RQ-MLDSA-001's specific goal, content not covered by 2026/1344 + 2026/1188? Record the answer. If yes: file with `dominated_by: null` and that justification. If no: defer filing.

---

## Supplementary OBJ-C — Correction Propagation

**Finding: MINOR GAP.**

Both corrections are correctly documented:
- `receipt.yaml` → `corrections_to_rq_mldsa_001_motivation`
- `fault_literature_summary.md` → Source B section
- `proposed_kn_lit_entries.md` → Entry 3 `year_correction_note` and `key_claims`

The batch correctly does NOT modify the immutable RQ-MLDSA-001.yaml record.

The gap is that the batch contains no explicit forward instruction naming: (a) which Coordinator task must create a superseding record or amendment, and (b) the consequence for any future agent that reads RQ-MLDSA-001 without reading this batch's artifacts (will see uncorrected values). No downstream ideation task currently exists, so there is no immediate harm. However, the ledger archive task (TASK-20260805-c60b84) needs an explicit annotation addressing this before any BATCH-002 ideation task is dispatched.

**Control:** The DEC-20260805-3d5f82 decision record at the ledger archive should state: "Two factual corrections to RQ-MLDSA-001 motivation are recorded in TASK-20260805-a1c3f9/receipt.yaml. A superseding RQ-MLDSA-001 record or equivalent amendment must be created before any BATCH-002 ideation task is dispatched. The corrected values are: (1) Jendral publication year = 2024, not 2026; (2) success probability = 0.582 (~58.2%), not ~53%."

---

## Objections Summary (ranked by severity)

| ID | Severity | Title | Blocks ledger archive? |
|---|---|---|---|
| OBJ-A | MODERATE | Ravi 2022 survey lacks dominated_by analysis; IEEE Trans. venue unconfirmed | No — constraint on filing |
| OBJ-B | MINOR | Source access log route exhaustion record is sparse | No — resolved by this review |
| OBJ-C | MINOR | No explicit forward note for correction propagation | No — ledger archive gate |

No blocking objections. All three objections carry cheapest controls in the `red_team_report.yaml`.

---

## Required Ledger Archive Gates

Before the ledger archive (TASK-20260805-c60b84) closes:

1. **[REQUIRED]** Coordinator must explicitly rule in DEC-20260805-3d5f82 whether the partial FIPS 204 entry (bibliography-level, standard body not read) satisfies RQ-MLDSA-001.constraints[0]. Two outcomes:
   - *Partial discharge only:* BATCH-002 first task must obtain FIPS 204 body via a PDF-text-capable tool.
   - *Full discharge for SelfTargetMSIS ideation:* Ideation may begin using KN-LIT-056 + KN-LIT-3907 (academic formulation already in corpus) plus the 5 newly proposed entries once filed.

2. **[REQUIRED]** DEC-20260805-3d5f82 must provide the correction propagation mechanism for RQ-MLDSA-001 (OBJ-C).

3. **[REQUIRED]** Coordinator must rule on whether to file Entry 4 (Ravi 2022) before or after resolving OBJ-A.

---

## Minimum for Next Batch

The FIPS 204 body gap does **not** automatically block ideation on the mathematical SelfTargetMSIS question, because:
- KN-LIT-056 (TCHES 2018, already in corpus) contains the original academic SelfTargetMSIS definition
- KN-LIT-3907 (mechanized proof, already in corpus) formalizes the security reduction
- FIPS 204 parameter values (n, q, k, l, γ1, γ2, etc.) are available from the academic sources

However, the FIPS 204 standardized parameter sets and formally standardized problem definitions would add value for experiment design at certified parameters. Whether the partial entry is sufficient for constraints[0] discharge is a Coordinator call, not a mathematical determination.

If the Coordinator rules "partial only": BATCH-002 first task = obtain FIPS 204 body via PDF text extraction.  
If the Coordinator rules "sufficient for SelfTargetMSIS ideation": BATCH-002 may proceed to ideation, provided:
- The two RQ-MLDSA-001 corrections are made canonical via a superseding record
- Entry 4 dominance is resolved
- The 5 proposed KN-LIT entries are filed with Coordinator-allocated IDs

---

## Non-findings (duties that found nothing)

- No fabricated commands, outputs, timings, statistics, or claims found.
- No ML-DSA security claim at any tier above literature-acquisition.
- No conflation of academic paper (KN-LIT-056) with standard document (FIPS 204).
- No description of fault attacks as mathematical breaks.
- No prejudgment of SelfTargetMSIS calibration in either direction.
- No scope inflation beyond what the batch's stated ceiling allows.
- Corrections recorded accurately without laundering.
- KN-LIT filing correctly deferred to Coordinator (no knowledge/ edits by producer).
