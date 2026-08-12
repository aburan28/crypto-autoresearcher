# Derivation check — TASK-20260731-105 / RT-20260731-105

**Verdict: REVISE**  
**Freeze:** `303ae797` (H-IT-001 / EXP-IT-001)  
**Pivot bind:** DEC-20260731-024 @ `1aa3b957`; queue restore `d39ceeed`  
**Recommendation to TASK-106:** NOT APPROVED (no Executor)

## Scope of this check

Pre-execution review of the admitted isogeny-transfer design freeze only. No cells measured. No approval issued. No Executor authorization. Companion `contract_review.yaml` carries the full gate ledger and blocking defects **B-1–B-4**.

Out of scope (per DEC-024 / task card): abandoned structure-null-r2 / BATCH-024 stubs; H-DS-001 reopen; STR; SG-ECDLP-001 lane-death claims; crypto-scale extrapolation.

## What holds

| Check | Result |
| --- | --- |
| Freeze committed before review; hashes match TASK-096 receipt | Pass |
| Official pivot is DEC-024 → EXP-IT-001, not structure-null stubs | Pass |
| Toy claim ceiling; no crypto / asymptotic / GOAL / H-DS support smuggle | Pass |
| Matched Pollard rho + BSGS named; rho constant 0.886√N | Pass |
| HEUR-ISO-1 named; planted-path F2 / harness-void rule | Pass |
| F1 / F2 / F3 falsification shape present | Pass |
| H-DS-001 / H-IC-001 / H-STR-002 not modified or demanded closed | Pass |
| `approved_by: null` D-1 prophylaxis | Pass |

## What blocks APPROVE

1. **B-1 — F_hit not pre-registered.** KS/TAIL cite a “contract random-regular hitting-time CDF” without freezing regularity `d`, the `min_ell` abscissa (hops vs prime vs composite degree), or an explicit `F_hit` algorithm. HEUR-ISO-1 cannot be validated or independently recomputed.
2. **B-2 — Detectors / density universe incomplete.** Embedding-degree threshold unset; Weil-descent friendliness undefined; `rho_special` enumeration universe unnamed.
3. **B-3 — Cost ledger incomplete.** `C_path`, `C_special`, and `ell_max` semantics are not frozen to group-op formulas comparable to matched rho, so `R_xfer` is not decidable.
4. **B-4 — IDEA-011 null missing.** Isogeny-transfer null object / `R_null` bits are not in the freeze despite `CTRL-NULL-PACKAGING-GATE` and inventor-protocol controls-before-belief.

## Claim-honesty note

Even after B-1–B-4 are fixed, a toy RATE-ISO-1 pass (including censorship lower bounds) must remain **toy-tier gate-hold**, not crypto-scale generic-curve safety. The freeze already states this; REVISE does not challenge that ceiling — it challenges executability of the metrics under it.

## Disposition

TASK-106 should archive this REVISE and record **NOT APPROVED**. At most one protocol amendment may discharge B-1–B-4, then a new independent review. This session did not author the freeze and does not author repairs.
