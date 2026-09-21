# TASK-20260731-134 — Derivation / protocol check for PA-DS-001-v2-ctrl-sparse-p-success

**Report:** `RT-20260731-134` (path + task id).
**Reviewed snapshot:** `0d6a1a9441418b58383645dbc7b973ca68be41df` (TASK-20260731-133; parent `baf21f96`).
**Parent contract:** `experiments/EXP-DS-001/specification.v2.yaml` (immutable; sha256 `898304bf…a5636a`; **not** in snapshot commit delta).
**Open decision:** DEC-20260731-037 opens BATCH-029 and selects SPARSE-P-SUCCESS as highest-EVPI residual after DEC-031 CI-IDENTITY close (does not authorize Executor run).
**Prior disposition:** DEC-20260731-031 closed BATCH-026 CI-IDENTITY as inconclusive (EV-DS-009; cell-local `ci_identity_pass`). RT047-B4 / RT118-B6 remained blocking on sparse p̂ / total-expected-cost accounting.
**Exact object under review:** PA-DS-001-v2-ctrl-sparse-p-success / CTRL-RT025-SPARSE-P-SUCCESS as admitted at `0d6a1a94` for possible `RUN-DS-001-ctrl-sparse-p-success` authorization by TASK-135.
**Session:** Independent `review-adversarial` (`fresh_session_after_stall: true`); `resolved_model_id` cursor-grok-4.5; `fallback_used: true`; xhigh not claimable. This session did not author the package.

**Question:** Is the frozen SPARSE-P-SUCCESS addendum executable and reviewable such that TASK-135 may APPROVE a sparse-yield control run?

## Verdict

**PASS.** RT047-B4 / RT118-B6 / RT101-B6 / RT079-B6 residual is addressed at protocol level:

1. **Executable status** — Both PA and CTRL set `status: executable` (not `abandoned_before_archive`, not `cancelled_before_approval`).
2. **Sparse semantics encoded** — `p_hat`, `p_hat_decay_observed`, `R_per_attempt`, `R_total_expected`, `total_expected_cost_split`, `total_expected_cost_naive`, `sparse_p_success_pass`, and `sparse_p_success_fail` are defined in CTRL and listed in PA `executable_markers.required_semantics_present`.
3. **Honest fail** — p̂ does not decay on the declared ladder, or required fields missing, or total-expected bookkeeping omitted ⇒ `sparse_p_success_fail` (not infra; not lane death / `reject_scoped`).
4. **Hygiene** — Toy ceiling; parent v2 immutable; BATCH-027/028 IT dominated_by/deferred; BATCH-028 remint documented; no EXP-IT launder; no STR; no H-IC/H-STR edits; `no_run_authorized_until_approval: true`; RC-28 one-cycle cap documented.

Toy ceiling and IT dominated_by naming hold. No measurement; no approval issued here. TASK-135 should APPROVE (this reviewer does not).

## Snapshot binding

| Path | sha256 at `0d6a1a94` | Notes |
|---|---|---|
| `experiments/EXP-DS-001/amendments/v2_ctrl_sparse_p_success.yaml` | `295474071454788abe9daf9ec447b805189a53db16a0d11d4519147db6f4ca63` | executable PA |
| `experiments/EXP-DS-001/controls/CTRL-RT025-SPARSE-P-SUCCESS.yaml` | `0ffae9d74057f58cda830450fddc20f7ff22284bf6930468d8442ae4e4f52cdf` | executable CTRL |
| `ledger/decisions/DEC-20260731-037.yaml` | `b2935df64a51b33944d971aef9a15fc752b8dc52a5c8e5ad0b5719772b33fb96` | batch open |
| `…/BATCH-029/SCOPE-DECISION.md` | `c183c7ec7e110147bff60e4169f819ae260570f6be717708468fd306527b2a01` | scope + dominated_by |
| `…/BATCH-029/QUEUE-AMEND-20260731-017.md` | `25c46704f6e73cd01dc28f9ddab1e0dcfecacee420ddf78338fc616a97ef3780` | RC-28 amend |
| `experiments/EXP-DS-001/specification.v2.yaml` | `898304bfc9225062e68c5d7977d1490cad95957e856847676ef7ae1423a5636a` | **not** in commit delta |

Commit name-only list excludes all `specification*.yaml`, H-IC/H-STR, and EXP-IT/H-IT freeze paths. Receipt `source_path_sha256` matches recomputed blobs; receipt `commit_sha` is `null` (informational process note I-1, not REVISE-forcing).

## Anti-tautology derivation (why PASS)

### RT047-B4 → sparse-yield control

EV-DS-009 closed CI-IDENTITY with cell-local `ci_identity_pass` at 20/64/4/101, but saturated unplanted p̂≈1.0 leaves total-expected-cost bookkeeping (per-attempt × 1/p̂) untested. RT047-B4 and RT118-B6 name this as the highest-EVPI residual: remeasure at parameters where p̂ clearly decays, charge total expected cost for split and naive arms, and test whether any R_per_attempt < 0.5 survives as R_total_expected < 0.5.

`CTRL-RT025-SPARSE-P-SUCCESS` encodes exactly that fix: require `p_hat_decay_observed`, report `R_per_attempt` and `R_total_expected` with explicit total_expected_cost fields, forbid reading saturated p̂≈1.0 as crypto yield, and allow honest `sparse_p_success_fail` when p̂ does not decay. Required report fields make the check Validator-decidable without post-freeze invention.

That is the scientific fix RT047-B4 demanded, encoded as decidable pass/fail bits. Empirical discharge still needs an APPROVED run — and under EV-DS-003 priors, `sparse_p_success_fail` is a plausible scientific outcome if p̂ remains saturated on the ladder, not an infra failure.

### vs CI-IDENTITY closure and IT parallel track

DEC-031 closed CI-IDENTITY; SPARSE is the named next_action with highest EVPI under SG-ECDLP-001. BATCH-027/028 IT Executor remains parallel on BATCH-028 (DEC-035) and is dominated_by for this batch — not cancelled, not laundered into EXP-DS-001. BATCH-028 id remint to BATCH-029 is documented and preserves DEC-031 scientific intent.

### Decision / scope

DEC-037 vocabulary: approve opens BATCH-029 and the executable addendum for independent RC-28 review — not Executor run, not H-DS-001 support, not lane death. SCOPE-DECISION / QUEUE-AMEND-017 agree. H-DS-001 remains analyzed.

## Card checklist

| # | Requirement | Status |
|---|---|---|
| 1 | `status: executable` on PA and CTRL | **met** |
| 2 | `p_hat` / `p_hat_decay_observed` / `R_total_expected` / `sparse_p_success_pass\|fail` present | **met** |
| 3 | Honest `sparse_p_success_fail` allowed (not infra / lane death) | **met** |
| 4 | Discharges RT047-B4 / RT118-B6 (and related RT079-B6 / RT101-B6) | **met** |
| 5 | Toy ceiling; IT dominated_by/deferred; no EXP-IT launder; no STR; no H-IC/H-STR edits | **met** |
| 6 | `no_run_authorized_until_approval`; parent v2 not in commit delta | **met** |
| 7 | RC-28 one-cycle; REVISE ⇒ non-execution understood | **met** |

## Scope of this check

Pre-execution review of the admitted SPARSE-P-SUCCESS snapshot only. No cells measured. No approval issued. No Executor authorization. Companion `contract_review.yaml` carries the full gate ledger. Protocol PASS does not assert empirical sparse-yield success.

## Coordinator handoff

On PASS: TASK-20260731-135 should record `APPROVAL_DETERMINATION: APPROVED` and may authorize `RUN-DS-001-ctrl-sparse-p-success` only against `CTRL-RT025-SPARSE-P-SUCCESS` into `results/ctrl_sparse_p_success`. Mark TASK-134 completed and regenerate the BATCH-029 plan outside this write_scope. Do not alter H-IC-001 / H-STR-002. Do not launder EXP-IT. Do not touch DEC-035/036 or BATCH-027/028 IT.

**Verdict: PASS**
