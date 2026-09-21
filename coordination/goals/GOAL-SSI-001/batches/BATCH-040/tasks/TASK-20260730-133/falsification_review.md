# Falsification review — BATCH-040 / TASK-20260730-133 (red-team)

- Reviews: TASK-20260730-131 (host-width contract + QM-STOPPING obstruction analysis, begun)
- Snapshot under review: `0802ff5a326d45443784168b2502bc031a636612` (bind `c9c87da95`)
- Report: `RT-20260730-133` · Role: red-team · Independent session: true
- Resolved model: Cursor Agent (Claude Opus 4.8), authorized fallback, `model_verified:false`
- **Verdict: CONFIRM_SCOPED** (no blocking objection; five non-blocking objections OBJ-1…OBJ-5)

## 0. Mandate

I was asked to try to break, specifically: invented numerics, illicit clearance,
CollimationSieve API invention, overclaim of the width contract as QUERY_MEMORY
clearance, and a fake obstruction closure (a §4-substandard obstruction dressed
as a closure, or a fatigue report dressed as an obstruction). I ran the
reproduction and independent structural probes below; I could not make any of
those failures stick. The claim survives as a boundary specification plus an
explicitly unverified obstruction analysis.

## 1. What I reproduced independently

**Snapshot ancestry + hashes.** `git` confirms `0802ff5a3` has parent
`912e45f90` (equal to the recorded `parent_sha`), changes exactly 12 files (11
producer artifacts + `snapshot-receipt.json`), and the bind commit `c9c87da95`
has parent `0802ff5a3`. I recomputed the sha256 of five key artifacts
(`host_width_contract.yaml`, `validation_falsification_plan.yaml`,
`stopping_obstruction_analysis.md`, `classification.yaml`,
`contract_harness/harness_receipt.json`) directly from the git tree; all five
equal the values in `snapshot-receipt.json`. No scope expansion.

**Harness.** Re-ran `python3 -m contract_harness.run_harness`: **34/34 OK**,
`harness_receipt.json` reproduced, and `git status` clean afterward (the
committed receipt is byte-identical to a fresh run).

**Structural cross-check against the untouched scaffold pin (the decisive one).**
The contract's structural claims are only meaningful if they are READ from the
BATCH-022 scaffold (pin `6f9188e4`) rather than asserted. I verified against
`scaffold/lifetime_hooks.py` and `scaffold/state_machine.py` directly:

- the twelve contract hooks equal `LifetimeRegistry.REQUIRED_HOOK_IDS` exactly;
- `birth_M_tail(..., width_decl, ...)` is the **only** `birth_*` hook carrying a
  `width_decl` parameter, and it raises
  `numeric_width_forbidden_in_zero_compute_scaffold` if `numeric_width` is
  present — so the "one symbolic-only emission channel, eleven with none" gap is
  a **real scaffold fact**, not a producer claim;
- `stage_live_sets` equals `STAGE_LIVE_SETS` verbatim;
- the scaffold is unmodified (git clean); the pin is untouched.

This is the load-bearing check: the emission gap the whole contract is organized
around is genuine.

## 2. The five falsification attacks I ran, and why they failed

**Attack A — invented numerics smuggled as real.** Every
`real_per_slot_width.{value,units}` is `null`, `composition_operator.peak.value`
is `null`, `bound_units` is `null`, and `tau`/`security_bits` are `null`. The
harness rejects, on independent re-run, an injected real width value, real units,
numeric peak, bound units, invented `security_bits`, and a source flipped to
`source_available:true`. **Failed to break.**

**Attack B — illicit clearance.** `query_memory_clearance:false` and
`query_memory_cleared:false` are positively pinned by
`check_no_illicit_clearance` and `check_memory_map_status`; flipping either fails
the harness. The BATCH-039 RT-129 OBJ-1 denylist gap is now hardened —
`_FORBIDDEN_TRUE_KEYS` includes `query_memory_solved`, `clearance`, `cleared`,
`problem_closed` — and `test_novel_clearance_like_key_rejected` passes.
**Failed to break** (residual denylist note is OBJ-5, non-blocking, because the
substantive state is positively pinned).

**Attack C — CollimationSieve API invention.** `collimation_sieve_apis_invented:
false`, `admissible_pin:false`, `batch020_pin_status:no_admissible_pin`; the pin
`6f9188e4` is untouched and no method name/signature/return is fabricated
anywhere. `check_pin_untouched` rejects a tampered pin/API/scaffold-modified
flag. **Failed to break.**

**Attack D — width contract overclaimed as clearance / MEMORY-MAP advancement.**
`scale_label: host_integration_boundary_specification_no_scale`,
`cryptographic_scale:false`, and `memory_map_status.advanced_this_batch:false`
(RETAINED, not advanced). A crypto-scale relabel and a disposition downgrade are
both rejected by the harness. The document repeatedly states this is a boundary
specification, not clearance. **Failed to break.**

**Attack E — fake obstruction closure.** `OBSTRUCTION_ANALYSIS_STATUS:
unverified`, `named_obstruction:false`, `meets_inventor_protocol_s4:false`,
`is_closure_claim:false`. §2 explicitly labels 8-batch FAIL retention a
*statement about the search, not the problem*, and §3–§4 run the §8 audits
(quantifier order `∀ hosts` untouched, method-ceiling / nearby-object control,
observation-collision) to show the candidate (*Verify-relativity of the stopping
time*) is an availability gap, not a proven barrier (AGENTS.md rule 5). The
harness rejects an obstruction write-up that overclaims a closure or omits
forward guidance. This is the correct handling — neither a fake closure nor a
fatigue report dressed as an obstruction. **Failed to break.**

## 3. Non-blocking objections

- **OBJ-1 (minor).** `composition_operator.invented:false` means
  "not-invented-in-this-batch"; the additive-within-stage / max-across-stage
  model is an unvalidated modeling assumption carried from the toy protocol.
  Honest because F1/F2/F3 pre-register exactly those falsifiers and all real
  values are null, but `invented:false` must not later be read as
  "host-sourced/validated operator."
- **OBJ-2 (minor).** The whole F1–F5 plan is gated on an admissible pin that does
  not exist (BATCH-020 `no_admissible_pin`), so no F-condition can fire now. The
  plan is falsifiable-in-principle but non-executable; the width lane yields no
  near-term discriminator. Honestly disclosed; feeds next action.
- **OBJ-3 (minor).** The "availability gap, not an obstruction" framing is
  correct but risks becoming a permanent excuse. The named §6 item-1
  host-independence reduction must actually be attempted next, else re-recording
  `unverified` is itself the fatigue mode the document diagnoses.
- **OBJ-4 (informational).** `model_verified:false`, authorized fallback to
  Cursor Agent (Claude Opus 4.8); acceptable for a zero-compute boundary spec
  (same posture as RT-129 OBJ-4).
- **OBJ-5 (informational).** Clearance guard is still a denylist (now expanded);
  a wholly novel key name could slip, but substantive clearance is positively
  pinned.

## 4. Baseline / Pareto honesty

No ECDLP/isogeny algorithmic claim, so rho/BSGS/vOW baselines do not apply and
none is made. Against QM-MEMORY-MAP the batch RETAINS
`numeric_composition_operator_protocol_toy_partial` (a contract spec with null
widths sources no real numeric, so no advancement is claimed). Against the real
GOAL-SSI-001 frontier: `sota_delta = 0`, `dominated_by` = fully dominated (zero
compute; QUERY_MEMORY still blocked by QM-STOPPING / QM-MEMORY-MAP / QM-ERROR).
The producer states this honestly (`stopping_obstruction_analysis.md` §7).

## 5. Recommended next action (see report `next_concrete_action`)

Do not launch EXP-SSI-001 and do not invent a pin/API/width to unblock the plan.
The one executable zero-compute lever is the QM-STOPPING **§6 item-1
host-independence reduction**: does τ's finiteness reduce to a host-independent
mixing-time / collision-distribution property statable without the full `Verify`
body? Either it does (candidate refuted, QM-STOPPING moves on with a falsifiable
criterion) or it is shown essential within a stated scope (discharging the
`∀ hosts` quantifier and earning a named §4 obstruction). If neither is
producible in a bounded step, PAUSE the QM-STOPPING lane with an explicit revisit
condition (an admissible CollimationSieve pin, or a host-independent
collision-distribution result) rather than record `unverified` a ninth time. No
toy width iteration, no fake-τ gate B; retain
FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED and QM-STOPPING FAIL.
