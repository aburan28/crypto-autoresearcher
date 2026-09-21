# Draft KN-FIND entries (TASK-20260725-693)

Status: **drafts only** under write_scope. Not yet written to `knowledge/findings/`.
Repairs: supersedes TASK-20260725-681 draft wording for RT-20260725-683 N1–N4.
Decision: DEC-20260725-021 (revise → repair before ledger PASS).

Inference: requested_policy=research-sol-max; resolved_model_id=cursor-grok-4.5-high-fast; fallback_used=true; authorization_ref=AMEND-PATH-001-001.

Theorem cross-note (N4, BKK/BKKMV rows): `proof_status` stays `empirical_only` for the EV-scoped claims below; `proof_refs` cite `research/THM_BKKMV1.md` and `DEC-20260722-003` for the m≤5 proved sectioned box-saturation / MV=box Bézout barrier. All-m law remains CONJECTURE C1 (open) per DEC-20260722-003 limitations.

---
id: KN-FIND-017
type: internal_finding
title: Scoped finding from EV-BKK-001
tags: [ecdlp, prime-field, toy, internal-finding]
confidence: reported
internal_refs: [EV-BKK-001, DEC-20260718-005, EXP-BKK-001, H-BKK-001, DEC-20260722-003]
proof_status: empirical_only
proof_refs: [research/THM_BKKMV1.md, DEC-20260722-003]
added: 2026-07-25
superseded_by: null
draft_of_task: TASK-20260725-693
repairs_draft_of: TASK-20260725-681
---

## Scoped claim
Toy p≤1009, m∈{3,4,5}: target-sectioned Semaev systems are Newton box-saturated (MV=multigraded Bézout); no support-aware BKK solve-cost advantage in tested scope.

## Provenance
- Evidence: `EV-BKK-001` (strength: replicated)
- Decision: `DEC-20260718-005` (reject_scoped)
- Experiment: `EXP-BKK-001`
- Hypothesis: `H-BKK-001`
- Later theorem upgrade (not restated as this EV claim): `THM_BKKMV1` / `DEC-20260722-003` prove the m≤5 sectioned barrier; C1 all-m gap remains open.

## Limits
Toy-scale only. Does not upgrade to medium/crypto claim tiers. Does not reopen closed mechanism families outside the cited scope. Corrections supersede; do not overwrite EV/DEC. Empirical EV claim is not itself the theorem; theorem covers m≤5 proved fragment only.

## Key claims (verified here)
- The Coordinator decision `DEC-20260718-005` closed the cited EV scope; this draft restates that scoped claim for knowledge promotion only.
- Cross-note: `DEC-20260722-003` / `THM_BKKMV1` later upgrade H-BKK-001's scoped rejection with a proved m≤5 barrier (N4).

## Not claimed
- Crypto-scale ECDLP advantage or impossibility
- Any result beyond the EV's recorded test boundary
- All-m box-saturation theorem (C1 open)


---
id: KN-FIND-018
type: internal_finding
title: Scoped finding from EV-BKKMV-001
tags: [ecdlp, prime-field, toy, internal-finding]
confidence: reported
internal_refs: [EV-BKKMV-001, DEC-20260718-011, EXP-BKKMV-001, H-BKKMV-001, DEC-20260722-003]
proof_status: empirical_only
proof_refs: [research/THM_BKKMV1.md, DEC-20260722-003]
added: 2026-07-25
superseded_by: null
draft_of_task: TASK-20260725-693
repairs_draft_of: TASK-20260725-681
---

## Scoped claim
Toy panel m=3,4,5: MV_m=(m−1)!·2^((m−1)(m−2)) exact with MV/Bézout_box=1; growth law certified on that range only, not m≥6.

## Provenance
- Evidence: `EV-BKKMV-001` (strength: replicated)
- Decision: `DEC-20260718-011` (supported_scoped)
- Experiment: `EXP-BKKMV-001`
- Hypothesis: `H-BKKMV-001`
- Later theorem upgrade (not restated as this EV claim): `THM_BKKMV1` / `DEC-20260722-003` prove the m≤5 sectioned barrier; C1 all-m gap remains open.

## Limits
Toy-scale only. Does not upgrade to medium/crypto claim tiers. Does not reopen closed mechanism families outside the cited scope. Corrections supersede; do not overwrite EV/DEC. Empirical EV claim is not itself the theorem; theorem covers m≤5 proved fragment only.

## Key claims (verified here)
- The Coordinator decision `DEC-20260718-011` closed the cited EV scope; this draft restates that scoped claim for knowledge promotion only.
- Cross-note: `DEC-20260722-003` / `THM_BKKMV1` prove m≤5 sectioned box-saturation ⇒ MV law (N4); do not treat this draft as proving m≥6.

## Not claimed
- Crypto-scale ECDLP advantage or impossibility
- Any result beyond the EV's recorded test boundary
- All-m box-saturation theorem (C1 open)


---
id: KN-FIND-019
type: internal_finding
title: Scoped finding from EV-BKKMV-002
tags: [ecdlp, prime-field, toy, internal-finding]
confidence: reported
internal_refs: [EV-BKKMV-002, DEC-20260722-003, EXP-BKKMV-002, H-BKKMV-001]
proof_status: empirical_only
proof_refs: [research/THM_BKKMV1.md, DEC-20260722-003]
added: 2026-07-25
superseded_by: null
draft_of_task: TASK-20260725-693
repairs_draft_of: TASK-20260725-681
---

## Scoped claim
Toy m=6 extension: MV_6=125829120=5!·2^20 on 6/6 with MV/Bézout_box=1; hulls box-saturated at finite p (2/30 sections lost 30–60 hull-interior monomials; corners intact; MV unchanged); literal support saturation is char-0/generic-t; beyond m=6 unmeasured; all-m law remains C1 open.

## Provenance
- Evidence: `EV-BKKMV-002` (strength: replicated)
- Decision: `DEC-20260722-003` (supported)
- Experiment: `EXP-BKKMV-002`
- Hypothesis: `H-BKKMV-001`
- Theorem track: `research/THM_BKKMV1.md` (m≤5 proved; m=6 certified empirically; C1 open)

## Limits
Toy-scale only. Does not upgrade to medium/crypto claim tiers. Does not reopen closed mechanism families outside the cited scope. Corrections supersede; do not overwrite EV/DEC. Finite-p saturation is a hull statement per DEC-20260722-003 / EV-BKKMV-002; literal full-box support is not claimed at m=6.

## Key claims (verified here)
- The Coordinator decision `DEC-20260722-003` closed the cited EV scope; this draft restates that scoped claim for knowledge promotion only.
- N1 repair: wording is hull/MV (DEC-20260722-003 limitations; EV-BKKMV-002 observations), not unqualified literal box saturation.
- N4 cross-note: THM_BKKMV1 proves m≤5; m=6 is certificate; C1 remains open.

## Not claimed
- Crypto-scale ECDLP advantage or impossibility
- Literal support saturation of every m=6 section at finite p
- All-m box-saturation theorem (C1 open)


---
id: KN-FIND-020
type: internal_finding
title: Scoped finding from EV-EQJ-001
tags: [ecdlp, prime-field, toy, internal-finding]
confidence: reported
internal_refs: [EV-EQJ-001, DEC-20260718-006, EXP-EQJ-001, H-EQJ-001]
proof_status: empirical_only
proof_refs: []
added: 2026-07-25
superseded_by: null
draft_of_task: TASK-20260725-693
repairs_draft_of: TASK-20260725-681
---

## Scoped claim
Toy p≤2^12, m=4 fibers: isotypic blocking yields no LA cost gain (full-rank survivors; 4× all-blocks cost); only orbit storage matching FHJRV symmetrization.

## Provenance
- Evidence: `EV-EQJ-001` (strength: replicated)
- Decision: `DEC-20260718-006` (reject_scoped)
- Experiment: `EXP-EQJ-001`
- Hypothesis: `H-EQJ-001`

## Limits
Toy-scale only (DEC-20260718-006: p≤2^12, m=4, 3 seeds). Does not upgrade to medium/crypto claim tiers. Does not reopen closed mechanism families outside the cited scope. Corrections supersede; do not overwrite EV/DEC.

## Key claims (verified here)
- The Coordinator decision `DEC-20260718-006` closed the cited EV scope; this draft restates that scoped claim for knowledge promotion only.
- N2 repair: `p≤2^12` is in the scoped claim sentence (DEC-20260718-006 limitations).

## Not claimed
- Crypto-scale ECDLP advantage or impossibility
- Any result beyond the EV's recorded test boundary


---
id: KN-FIND-021
type: internal_finding
title: Scoped finding from EV-FB-001
tags: [ecdlp, prime-field, toy, internal-finding]
confidence: reported
internal_refs: [EV-FB-001, DEC-20260716-004, EXP-FB-001, H-FB-001]
proof_status: empirical_only
proof_refs: []
added: 2026-07-25
superseded_by: null
draft_of_task: TASK-20260725-693
repairs_draft_of: TASK-20260725-681
---

## Scoped claim
Toy p~2^14, m=3, d≤12 (subgroup base excluded): tested FB structures leave d_reg, yield, and solve-cost scaling invariant vs random FB.

## Provenance
- Evidence: `EV-FB-001` (strength: replicated)
- Decision: `DEC-20260716-004` (reject_scoped)
- Experiment: `EXP-FB-001`
- Hypothesis: `H-FB-001`

## Limits
Toy-scale only. Does not upgrade to medium/crypto claim tiers. Does not reopen closed mechanism families outside the cited scope. Corrections supersede; do not overwrite EV/DEC. Subgroup base excluded per EV-FB-001 / DEC-20260716-004.

## Key claims (verified here)
- The Coordinator decision `DEC-20260716-004` closed the cited EV scope; this draft restates that scoped claim for knowledge promotion only.
- N2 repair: subgroup-base exclusion is in the scoped claim sentence (EV-FB-001 boundaries).

## Not claimed
- Crypto-scale ECDLP advantage or impossibility
- Any result beyond the EV's recorded test boundary
- Subgroup-base factor-base structures (excluded)


---
id: KN-FIND-022
type: internal_finding
title: Scoped finding from EV-NCP-001
tags: [ecdlp, prime-field, toy, internal-finding]
confidence: reported
internal_refs: [EV-NCP-001, DEC-20260718-009, EXP-NCP-001, H-NCP-001]
proof_status: empirical_only
proof_refs: []
added: 2026-07-25
superseded_by: null
draft_of_task: TASK-20260725-693
repairs_draft_of: TASK-20260725-681
---

## Scoped claim
Toy NC path-algebra harvest: no relations beyond commutative quotient; no sub-birthday charged-exponent trend on tested scope.

## Provenance
- Evidence: `EV-NCP-001` (strength: replicated)
- Decision: `DEC-20260718-009` (reject_scoped)
- Experiment: `EXP-NCP-001`
- Hypothesis: `H-NCP-001`

## Limits
Toy-scale only. Does not upgrade to medium/crypto claim tiers. Does not reopen closed mechanism families outside the cited scope. Corrections supersede; do not overwrite EV/DEC.

## Key claims (verified here)
- The Coordinator decision `DEC-20260718-009` closed the cited EV scope; this draft restates that scoped claim for knowledge promotion only.

## Not claimed
- Crypto-scale ECDLP advantage or impossibility
- Any result beyond the EV's recorded test boundary


---
id: KN-FIND-023
type: internal_finding
title: Scoped finding from EV-REP-002
tags: [ecdlp, prime-field, toy, internal-finding]
confidence: reported
internal_refs: [EV-REP-002, DEC-20260716-002, EXP-REP-002, H-REP-001]
proof_status: empirical_only
proof_refs: []
added: 2026-07-25
superseded_by: null
draft_of_task: TASK-20260725-693
repairs_draft_of: TASK-20260725-681
---

## Scoped claim
Toy Edwards-admitting curves, m=3: d_reg=2 invariant Weierstrass vs twisted Edwards; model not a solving-degree lever at that scope.

## Provenance
- Evidence: `EV-REP-002` (strength: replicated)
- Decision: `DEC-20260716-002` (reject_scoped)
- Experiment: `EXP-REP-002`
- Hypothesis: `H-REP-001`

## Limits
Toy-scale only. Does not upgrade to medium/crypto claim tiers. Does not reopen closed mechanism families outside the cited scope. Corrections supersede; do not overwrite EV/DEC.

## Key claims (verified here)
- The Coordinator decision `DEC-20260716-002` closed the cited EV scope; this draft restates that scoped claim for knowledge promotion only.

## Not claimed
- Crypto-scale ECDLP advantage or impossibility
- Any result beyond the EV's recorded test boundary


---
id: KN-FIND-024
type: internal_finding
title: Scoped finding from EV-SIG-002
tags: [ecdlp, prime-field, toy, internal-finding]
confidence: reported
internal_refs: [EV-SIG-002, DEC-20260718-017, EXP-SIG-002, H-SIG-001]
proof_status: empirical_only
proof_refs: []
added: 2026-07-25
superseded_by: null
draft_of_task: TASK-20260725-693
repairs_draft_of: TASK-20260725-681
---

## Scoped claim
Toy boolean Semaev t=3, n=12..21, D≤4: non-rewritable D4 residual exists, null residual=0, grows with n (counts later refined by EV-SIG-004).

## Provenance
- Evidence: `EV-SIG-002` (strength: replicated)
- Decision: `DEC-20260718-017` (supported_scoped)
- Experiment: `EXP-SIG-002`
- Hypothesis: `H-SIG-001`

## Limits
Toy-scale only. Does not upgrade to medium/crypto claim tiers. Does not reopen closed mechanism families outside the cited scope. Corrections supersede; do not overwrite EV/DEC. Exact D4 counts superseded by EV-SIG-004 / KN-FIND-026.

## Key claims (verified here)
- The Coordinator decision `DEC-20260718-017` closed the cited EV scope; this draft restates that scoped claim for knowledge promotion only.

## Not claimed
- Crypto-scale ECDLP advantage or impossibility
- Any result beyond the EV's recorded test boundary
- Canonical exact D4 residual series (see KN-FIND-026)


---
id: KN-FIND-025
type: internal_finding
title: Scoped finding from EV-SIG-003
tags: [ecdlp, prime-field, toy, internal-finding]
confidence: reported
internal_refs: [EV-SIG-003, DEC-20260718-019, EXP-SIG-003, H-SIG-001]
proof_status: empirical_only
proof_refs: []
added: 2026-07-25
superseded_by: null
draft_of_task: TASK-20260725-693
repairs_draft_of: TASK-20260725-681
---

## Scoped claim
Toy n=12,15 D=5: low-degree syzygy closure spans only ~34–38% of Macaulay deficit; most missing pivots are D5-born — SIG residual ≠ full DREG deficit object.

## Provenance
- Evidence: `EV-SIG-003` (strength: replicated)
- Decision: `DEC-20260718-019` (supported_scoped)
- Experiment: `EXP-SIG-003`
- Hypothesis: `H-SIG-001`

## Limits
Toy-scale only. Does not upgrade to medium/crypto claim tiers. Does not reopen closed mechanism families outside the cited scope. Corrections supersede; do not overwrite EV/DEC.

## Key claims (verified here)
- The Coordinator decision `DEC-20260718-019` closed the cited EV scope; this draft restates that scoped claim for knowledge promotion only.

## Not claimed
- Crypto-scale ECDLP advantage or impossibility
- Any result beyond the EV's recorded test boundary


---
id: KN-FIND-026
type: internal_finding
title: Scoped finding from EV-SIG-004
tags: [ecdlp, prime-field, toy, internal-finding]
confidence: reported
internal_refs: [EV-SIG-004, DEC-20260718-020, EXP-SIG-004, H-SIG-001]
proof_status: empirical_only
proof_refs: []
added: 2026-07-25
superseded_by: null
draft_of_task: TASK-20260725-693
repairs_draft_of: TASK-20260725-681
---

## Scoped claim
Canonical D4 residual 9/11/13/15 at n=12/15/18/21 (2n/3+1 on those sizes); EV-SIG-002 series is a lower bound; n=9 anomalous; count/rank only.

## Provenance
- Evidence: `EV-SIG-004` (strength: replicated)
- Decision: `DEC-20260718-020` (supported_scoped)
- Experiment: `EXP-SIG-004`
- Hypothesis: `H-SIG-001`

## Limits
Toy-scale only. Does not upgrade to medium/crypto claim tiers. Does not reopen closed mechanism families outside the cited scope. Corrections supersede; do not overwrite EV/DEC. Count/rank only; no d_reg or solver-impact claim.

## Key claims (verified here)
- The Coordinator decision `DEC-20260718-020` closed the cited EV scope; this draft restates that scoped claim for knowledge promotion only.

## Not claimed
- Crypto-scale ECDLP advantage or impossibility
- Any result beyond the EV's recorded test boundary


---
id: KN-FIND-027
type: internal_finding
title: Scoped finding from EV-SIG-005
tags: [ecdlp, prime-field, toy, internal-finding]
confidence: reported
internal_refs: [EV-SIG-005, DEC-20260720-001, EXP-SIG-005, H-SIG-001]
proof_status: empirical_only
proof_refs: []
added: 2026-07-25
superseded_by: null
draft_of_task: TASK-20260725-693
repairs_draft_of: TASK-20260725-681
---

## Scoped claim
Toy boolean Semaev t=3, n≤24: D4 law (2n/3+1) holds through n=24; D5-born residual non-monotone through n=18; D=6 null baseline invalid at tested n=9 (C5 fail) — cascade claims admissible only for D≤5.

## Provenance
- Evidence: `EV-SIG-005` (strength: replicated)
- Decision: `DEC-20260720-001` (supported_scoped)
- Experiment: `EXP-SIG-005`
- Hypothesis: `H-SIG-001`

## Limits
Toy-scale only (n≤24; cascade valid D≤5). Does not upgrade to medium/crypto claim tiers. Does not reopen closed mechanism families outside the cited scope. Corrections supersede; do not overwrite EV/DEC. Does not assert null invalidity for untested D>6 sizes.

## Key claims (verified here)
- The Coordinator decision `DEC-20260720-001` closed the cited EV scope; this draft restates that scoped claim for knowledge promotion only.
- N2 repair: toy / boolean-Semaev / n≤24 prefix is in the scoped claim sentence.
- N3 repair: cause is D=6 null C5 failure at n=9; cascade admissible only for D≤5 — not blanket “D≥6 null baseline invalid”.

## Not claimed
- Crypto-scale ECDLP advantage or impossibility
- Any result beyond the EV's recorded test boundary
- Null-baseline invalidity for all D≥6 / untested sizes
- D6 birth-law residual magnitudes (measurement retracted as invalid)
