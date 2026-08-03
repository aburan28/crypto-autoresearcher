# Falsification review — RT-20260730-129

- **Task:** TASK-20260730-129 (independent Red Team)
- **Reviews:** producer TASK-20260730-127 via snapshot archive TASK-20260730-128
- **Goal / batch:** GOAL-SSI-001 / BATCH-039
- **Snapshot commit:** `f877f812e6d8115ef4475b7901ec31567da32acc`
- **Bind commit (HEAD):** `f3a96545d77fa00bf70cc0b7492e8189754159bc`
- **Verdict:** **CONFIRM (scoped)** — honest protocol-toy / scaffold-scale
  instantiation that does **NOT** clear QUERY_MEMORY.
- **Session:** independent; resolved model `Cursor Agent (Claude Opus 4.8)`,
  `requested_policy: review-adversarial`, `fallback_used: true`,
  `model_verified: false`.

---

## 1. Snapshot integrity (independently verified)

- `git rev-parse f877f812e^` = `c36cad125…` — matches
  `snapshot-receipt.json.parent_sha`. ✔
- All **11** declared `source_path_sha256` entries recomputed via
  `git show f877f812e:<path> | shasum -a 256` — **all match** the receipt. ✔
- Snapshot commit changes exactly the 11 producer artifacts + the receipt
  (12 files, +1252), no scope expansion. ✔
- The receipt's `commit_sha` is `null` with
  `verification.status: pending_post_commit`. Acceptable at the snapshot stage
  (the dispatcher's post-commit verifier binds the SHA); flagged only so the
  ledger-archive step is not skipped.

## 2. Harness re-run and determinism

`cd …/TASK-20260730-127 && python3 -m instantiation_harness.run_harness`
→ **23/23 OK**, exit 0, `passed: true`.

The re-run **reproduced the committed `harness_receipt.json` byte-for-byte**
(`git status` clean afterward, no diff). The harness is deterministic and the
committed receipt matches a fresh full-tree run.

## 3. Numeric reproduction (no invented numerics)

Recomputed independently from the declared constants over BATCH-023 membership:

| Stage | members → weights | load |
| --- | --- | ---: |
| preparation | B2+B2+W8+R4 | 16 |
| sieve_attempt | B2+B2+W8+R4+B2 | 18 |
| recovery | B2+B2+B2+B2+T1 | 9 |
| tail_verification | B2+B2+B2+M16+B2 | **24** |

`peak = max(16,18,9,24) = 24` at `tail_verification`; mistaken cross-stage sum
`= 67`, rejected. Matches ledger and receipt exactly. BATCH-023
`stage_live_sets` membership matches `CANONICAL_STAGE_MEMBERSHIP` **verbatim**,
and BATCH-023 itself records `peak_byte_bound: unresolved` / `numeric_widths:
not_invented`, so the "discharges a previously-null placeholder at toy scale"
framing is accurate.

## 4. Adversarial probes I ran (beyond the producer's own tests)

1. **Coherent-width tamper** — set `W=16` **and** recompute every dependent
   number to internal self-consistency. **Rejected** ("slot_width_table does not
   match canonical protocol widths"). This confirms the harness pins to
   protocol-canonical constants, not merely to internal arithmetic consistency —
   the property that makes "no invented numerics" meaningful.
2. **Zero-weight coherent tamper** (`M=0`, all recomputed) — **rejected** (same
   canonical pin).
3. **Extra smuggled stage** — **rejected** by both the numerics check and the
   exact key-set check.
4. **String-valued clearance** (`summary.query_memory_cleared = "yes"`) —
   **rejected** (guard uses `is not False`, a positive pin).
5. **Novel clearance-like key** (`query_memory_solved: true`) — **NOT rejected**
   → see OBJ-1 below.

## 5. Mandate line items

| Threat | Finding |
| --- | --- |
| Invented / out-of-protocol numerics | **None.** Allowlist provenance scan + exact key-set + canonical pin, confirmed by coherent-tamper probe. |
| Illicit clearance | **None present.** `query_memory_clearance:false`, disposition retained, positively pinned. Denylist gap = OBJ-1 (non-blocking). |
| CollimationSieve API invention | **None.** `collimation_sieve_apis_invented:false`; pin `6f9188e4` untouched; no APIs called. |
| BATCH-014 equation | **Not equated** (`ttm_v2_equated_to_batch014:false`, `batch014_equated:false`). |
| Overclaim toy → crypto / QUERY_MEMORY | **None.** `scale_label: protocol_toy_scaffold_scale`, `cryptographic_scale:false`, strong §0/§6 disclaimers. |
| Fake τ | **None.** `tau_invented:false`, `joint_finiteness_established:false`, QM-STOPPING **FAIL** retained. |
| Breakthrough / completion creep | **None.** All honesty flags false; status names carry `protocol_toy`. |

## 6. Objections

- **OBJ-1 (minor).** The illicit-clearance truthy-key scan is a **denylist**
  (`_FORBIDDEN_TRUE_KEYS`). A novel key such as `query_memory_solved: true`
  passes. **Not** an actual overclaim here: no such key exists, and the
  disposition / scale / clearance fields are pinned by **positive** assertions
  that cannot be flipped without failure. Recommend hardening the clearance scan
  to an allowlist / truthiness scan symmetric with the numeric guard.
- **OBJ-2 (minor).** `peak_byte_bound=24` is **M-dominated**: `M_tail`
  (`M=16`) alone drives the peak stage; drop it and the peak flips to
  `sieve_attempt=18`. The peak-stage identity is an artifact of the stipulated
  ordering, not a structural memory fact. The two-level operator is genuinely
  exercised (within-stage sum → 18; `67>24` shows max-not-sum), but the headline
  number carries little information. Bounds the demonstration; does not
  invalidate it.
- **OBJ-3 (info).** The committed receipt is a **full-tree** artifact
  (`cross_batch023 found:true`), not the execution-time run the report describes
  (`found:false` at `c36cad125`). Honestly disclosed in report §5; my
  byte-identical re-run + verbatim membership check make the substance sound.
- **OBJ-4 (info).** `model_verified:false` — acceptable for a zero-compute
  scaffold gate; noted for ledger completeness.

## 7. Closure honesty (inventor-protocol §4)

The batch correctly does **not** close any lane and **retains** QM-STOPPING
FAIL rather than dressing it as an obstruction. But the FAIL has now been merely
*retained* across **8** batches (037/036/035/034/033/032/031/018) with no named
obstruction + argument. Repeated retention of a negative control is a **fatigue
report about the search**, not a statement about the problem. Meanwhile the
program keeps adding toy MEMORY-MAP gates beside the binding blocker
(QM-STOPPING) that those gates do not touch. This is the point to break the
pattern.

## 8. Baseline / Pareto

No Pollard-rho / BSGS / vOW baseline applies (no algorithmic claim, and none is
made). Against the prior scaffold state (`composition_aggregation_schema_partial`,
placeholders-only) this advances to
`numeric_composition_operator_protocol_toy_partial` **at toy scale only**.
Against the real GOAL-SSI-001 frontier: **`sota_delta = 0`**, fully
`dominated_by` existing state — zero curve/isogeny/quantum compute, QUERY_MEMORY
still blocked. Honestly stated by the producer.

## 9. Narrowest supported statement

Under `FC0-PEAKBYTE-TOY-PROTOCOL-R1`, the BATCH-023 composition/aggregation
lineage admits one internally-consistent, independently-recomputable numeric
instantiation (operator + `protocol_slot_bytes` units + toy width table +
peak-byte `24`) once stipulated placeholder constants are supplied —
reproducible (23/23, byte-identical receipt) and guarded against invented /
out-of-protocol numerics and the recognized illicit-clearance flags. **This
holds at protocol-toy / scaffold scale ONLY.** No cryptographic-scale bound, no
QUERY_MEMORY clearance, no τ / joint finiteness, no breakthrough / completion.
The value `24` is meaningless outside this document.

## 10. Next concrete action

- **Do NOT** attempt gate B (Verify-relative τ / joint finiteness) as a toy —
  that is the fake-τ / controlled-null-fatigue trap, and QM-STOPPING has FAILed
  8 times.
- **Do NOT** launch EXP-SSI-001.
- **Do NOT** iterate the toy peak-byte width lane again (operator instantiated,
  output M-dominated → no new information; fatigue risk).
- **DO** run one bounded, **zero-compute** batch that: (1) specifies the
  host-integration **width contract** — which CollimationSieve@`6f9188e4` /
  BATCH-022 scaffold hooks would emit real per-slot widths, in what units, and
  how the operator consumes them — inventing **no** value and launching
  **no** EXP, and pre-registers the real-width validation + falsification plan;
  and (2) begins the **QM-STOPPING obstruction analysis** to the closure
  standard (named obstruction + argument + what remains open). If (2) cannot yet
  name an obstruction, record it as `unverified`, never as a closure.
