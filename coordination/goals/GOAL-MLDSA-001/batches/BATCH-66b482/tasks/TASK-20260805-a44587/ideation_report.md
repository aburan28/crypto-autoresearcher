# Ideation Report — GOAL-MLDSA-001 BATCH-002
## Task: TASK-20260805-a44587
## Agent: idea-generator (amazon-bedrock/us.anthropic.claude-sonnet-4-6)
## Date: 2026-08-05
## states_a_finding: false

---

## 1. Context and Constraints

This task generates falsifiable proposals for RQ-MLDSA-001 under the constraints
established by BATCH-001 and DEC-20260805-0d59ff:

- **FIPS 204 standard body not read.** All proposals must be supportable from
  academic literature (KN-LIT-056, KN-LIT-059, KN-LIT-3907, fault papers
  KN-LIT-340675, KN-LIT-4f3b80, KN-LIT-8ce0b5).
- **DEC-20260805-0d59ff gate-1 ruling:** SelfTargetMSIS ideation from academic
  literature is permitted without the FIPS 204 body. FIPS 204 body required
  before designing a concrete experiment claiming to test a FIPS 204 parameter set.
- **Canonical corrections:** Jendral year is 2024 (not 2026); success probability
  is 58.2% (not ~53%). Applied throughout this report.
- **Claim ceiling:** Toy-tier until a certified instance at or above standardized
  parameter scale exists. AGENTS.md rule 7 applies throughout.

---

## 2. Literature Searched

**Sources consulted for this ideation task:**

| Source | Access level | Notes |
|--------|-------------|-------|
| KN-LIT-056 (CRYSTALS-Dilithium TCHES 2018) | Abstract + KN-LIT entry | Academic parameter tables referenced from memory; unverified exact values |
| KN-LIT-059 (Fiat-Shamir with Aborts, Lyubashevsky 2009) | KN-LIT entry | FS-with-aborts paradigm |
| KN-LIT-3907 (Barbosa et al., Fixing FS-with-Aborts proof) | KN-LIT entry + abstract | Local PDF available but not read in this session; full text needed for IDEA-9c1e04 |
| KN-LIT-4dadec (FIPS 204, NIST 2024) | Bibliographic only | Standard body not read |
| KN-LIT-340675 (Shin et al. DFA 2026/1344) | Abstract (primary ePrint page) | Challenge-sampling fault |
| KN-LIT-4f3b80 (Jendral 2024/238) | Abstract (primary ePrint page) | Hedged-mode glitch |
| KN-LIT-8ce0b5 (Gupta 2026/1188) | Abstract (primary ePrint page) | NTT twiddle formal bound |
| KN-LIT-180ad5 (Ravi et al. 2022/737) | Abstract (primary ePrint page) | SCA/FIA survey |
| BATCH-001 artifacts: fault_literature_summary.md | Full text | Detailed attack classification |
| DEC-20260805-0d59ff | Full text | Canonical gate-1/2/3 rulings |

**Sources not reachable/not read:**
- FIPS 204 standard body (binary PDF blocker, confirmed by BATCH-001 review)
- KN-LIT-3907 local PDF (not opened in this session; needed for IDEA-9c1e04 test)

---

## 3. What Was Found

### 3.1 SelfTargetMSIS calibration (Lane A)

The KN-LIT corpus establishes:
- The SelfTargetMSIS problem arises from the Fiat-Shamir-with-aborts proof structure
  (KN-LIT-059). It is the problem whose hardness is required to forge a signature
  without the secret key.
- The hardness estimate (KN-LIT-056) combines MSIS hardness at scheme dimensions
  with a hash-programmability cost log₂|C|, where C is the sparse challenge polynomial
  set with weight τ.
- Barbosa et al. (KN-LIT-3907) identified a gap in the CMA-to-NMA reduction and
  fixed it; their abstract states "the claimed security level is still valid after
  addressing the gap." The concrete tightness loss is not stated in the abstract
  and requires reading the full text.
- **Key gap:** No independent re-derivation of the SelfTargetMSIS hardness estimate
  at the three ML-DSA parameter sets was found in the corpus. The original Dilithium
  estimate from KN-LIT-056 is the only available concrete estimate.

### 3.2 Fault proof boundary (Lane B)

The fault_literature_summary.md (BATCH-001) established three distinct proof/attack
structures:

| Structure | Source | Scope | Notes |
|-----------|--------|-------|-------|
| Classical CMA security | KN-LIT-3907 (Barbosa et al.) | Mathematical adversary, no faults | ROM/QROM, EasyCrypt verified |
| NTT twiddle fault leakage | KN-LIT-8ce0b5 (Gupta) | Twiddle-perturbation faults on forward NTT only | Lean 4 verified; tight bound |
| Challenge-sampling faults | KN-LIT-340675 (Shin) | ATTACK paper; deterministic ML-DSA | No formal proof coverage |
| Seed-generation faults | KN-LIT-4f3b80 (Jendral) | ATTACK paper; hedged ML-DSA | No formal proof coverage |

**Key finding for proposal generation:** The Shin DFA and Jendral glitch both fall
OUTSIDE the Gupta formal proof scope (as explicitly stated in fault_literature_summary.md:
"Sources A and B fall OUTSIDE 2026/1188's scope"). Neither source falls within
the Barbosa et al. classical security proof (which models no faults). This creates
a well-defined, scoped coverage gap with named boundaries.

### 3.3 SelfTargetMSIS distinguishability (Lane C)

No corpus entry addresses whether SelfTargetMSIS is computationally distinguishable
from MLWE at any parameter scale. The Dilithium security proof assumes independence
of the MSIS and hash-programmability components; no experiment validates this
independence assumption at any scale. This creates a clean measurement target.

---

## 4. What Was NOT Found

- No independent concrete SelfTargetMSIS hardness estimate for ML-DSA-44/65/87
  in any corpus entry other than KN-LIT-056.
- No formal fault-security proof covering challenge-sampling faults (Shin DFA class).
- No formal fault-security proof covering seed-generation faults (Jendral class).
- No formal proof or analysis of hedged ML-DSA specifically under nonce-erasure
  adversaries.
- No toy-scale or full-scale experiment comparing BKZ costs for SelfTargetMSIS
  vs pure MSIS.
- No corpus entry analyzing the effect of challenge weight τ reduction on
  SelfTargetMSIS hardness.

**Corpus completeness caveat (AGENTS.md knowledge retrieval policy §bounds):**
"Absence of a search result is not evidence that something was not tried. Recall
is measured as a floor, not an estimate." The corpus covers KN-LIT entries indexed
as of this session. Papers outside the indexed corpus may address any of the above.

---

## 5. Proposals Generated

Five proposals were generated covering all three lanes:

| ID | Lane | Class | Title (abbreviated) | Requires FIPS 204 body |
|----|------|-------|---------------------|----------------------|
| IDEA-20260805-3f7ab2 | A | measurement | SelfTargetMSIS hardness margin re-derivation | No |
| IDEA-20260805-9c1e04 | A | mechanism | CMA-NMA proof gap impact on concrete estimate | No |
| IDEA-20260805-a8d531 | B | mechanism | Shin DFA challenge-sampling coverage gap | No |
| IDEA-20260805-2b6f17 | B | mechanism | Jendral nonce-erasure coverage gap | No |
| IDEA-20260805-e5c308 | C | measurement | Toy-scale SelfTargetMSIS vs MSIS BKZ comparison | No |

All five proposals have `requires_fips204_body: false` for ideation purposes per
DEC-20260805-0d59ff gate-1. Actual experiment design for proposals touching FIPS 204
parameter sets would require the standard body.

---

## 6. Pareto Frontier Analysis and `dominated_by` Audit

The inventor protocol §5 requires `dominated_by` to be set null only after checking
every row of the frontier across time, memory, and data/queries. These are analysis
and measurement proposals (not attacks), so the Pareto axes are:
- **Breadth of formal coverage** (how much of the proof gap does it close?)
- **Calibration accuracy** (how precisely does it quantify hardness?)
- **Cost** (implementation cost and compute)

**Frontier check for each proposal:**

**IDEA-3f7ab2 (Lane A re-derivation):**
Checked against: KN-LIT-056 (original estimate), KN-LIT-3907 (corrected proof),
KN-LIT-059 (FS-with-aborts paradigm). None of these provides an independent
re-derivation checking which assumption is binding at each parameter set. No
dominator found. `dominated_by: null` is defensible with the caveat that reading
KN-LIT-3907 full text may reveal a superseding concrete analysis.

**IDEA-9c1e04 (Lane A CMA-NMA gap):**
Checked against: KN-LIT-3907 (this IS the paper being analyzed). The proposal
is derivative — it asks a question whose answer exists in KN-LIT-3907 but has
not been extracted. KN-LIT-3907 does not dominate IDEA-9c1e04 because domination
requires an existing result, not a result that might be in an unread text.
`dominated_by: null` until KN-LIT-3907 full text is read.

**IDEA-a8d531 (Lane B Shin boundary):**
Checked against: KN-LIT-8ce0b5 (Gupta NTT twiddle — different fault class),
KN-LIT-180ad5 (Ravi survey — taxonomy, not formal proof). Neither dominates the
specific "placement of Shin DFA relative to formal proofs" question. `dominated_by: null`.

**IDEA-2b6f17 (Lane B Jendral boundary):**
Checked against: same as above, plus KN-LIT-4f3b80 (Jendral attack paper — describes
the attack, not the formal proof boundary). No dominator. `dominated_by: null`.

**IDEA-e5c308 (Lane C toy BKZ):**
Checked against: KN-LIT-056 (asserts decomposition but does not test it),
KN-LIT-3907 (corrects proof, does not test decomposition). No comparable experiment
found. `dominated_by: null`.

---

## 7. Priority Assessment

**High priority (recommended for BATCH-002 experiment design):**
- IDEA-3f7ab2: Directly addresses the core question of whether SelfTargetMSIS is
  the binding assumption. Low cost, immediate result.
- IDEA-a8d531: Establishes explicit formal proof boundaries. Low cost, high clarity.
- IDEA-2b6f17: Characterizes the Jendral gap formally. Low cost, high clarity.

**High priority but requires full-text read:**
- IDEA-9c1e04: Answers a quantitative question about the corrected proof's impact.
  The KN-LIT-3907 local PDF is available; this is a reading task, not a compute task.

**Medium priority (requires implementation):**
- IDEA-e5c308: Validates a structural assumption at toy scale. Requires code
  (BKZ implementation), but low compute. Important for Lane C but not blocking
  other lanes.

---

## 8. Open Directions Not Covered by These Proposals

The following directions were noted but not turned into proposals in this batch,
due to either (a) insufficient source material in the corpus or (b) falling below
the proposal quality bar:

1. **Hedged vs. deterministic mode security differential**: Whether any formal
   security guarantee differentiates the two modes (beyond operational arguments).
   Requires KN-LIT-3907 full text.

2. **Challenge weight τ as a security parameter**: Whether τ is sized to maximize
   security margin or was chosen for implementation reasons (constant-time sampling
   efficiency). This is a parameter design question requiring the FIPS 204 standard
   body or NIST submission documents.

3. **MLWE vs MSIS binding assumption audit**: Which of the three problems (MLWE,
   MSIS, SelfTargetMSIS) is actually binding at each parameter set is the direct
   answer to RQ-MLDSA-001's decision target. Proposals 1 and 2 partially address
   this; a third proposal directly comparing all three estimates was considered
   but deferred pending the IDEA-3f7ab2 re-derivation result.

4. **Ravi 2022 survey-based taxonomy**: KN-LIT-180ad5 may contain a more complete
   attack taxonomy than available from individual paper abstracts. Using the full
   survey text to enumerate additional fault classes not covered by Gupta's proof
   is a potential follow-on after IDEA-a8d531 is completed.

---

## 9. Constraints on Use of These Proposals

- All five proposals are ideation-tier. None constitutes an experiment design,
  hypothesis specification, or evidence record.
- Proposals 1–4 have low implementation cost and can be immediately dispatched as
  analysis tasks. Proposal 5 requires a simple BKZ implementation.
- All claims about exact parameter values (τ, γ₁, β, n, q, k, l) in the proposals
  are from memory or secondary sources and carry `novelty_status: unverified`.
  Exact values must be verified from KN-LIT-056 full text before any experiment.
- Toy-scale results from IDEA-e5c308 are NEVER presented as statements about
  standardized parameter sets (AGENTS.md rule 7).
- The Coordinator must determine which proposals to advance to hypothesis
  specification and experiment design. This report does not approve, reject, or
  prioritize on the Coordinator's behalf.
