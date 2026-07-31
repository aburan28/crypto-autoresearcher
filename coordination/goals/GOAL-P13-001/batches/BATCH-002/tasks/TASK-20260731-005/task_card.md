# TASK-20260731-005 — Coordinator — Ledger archive, ALONE

**Goal** GOAL-P13-001 · **Batch** BATCH-002 · **Role** coordinator · **Priority** 70
**Depends on** TASK-20260731-003, TASK-20260731-004 · **Archive kind** `ledger`
**Budget** 1200 s wall clock · 2 GB · maximum_runs 1

> **The queue governs.** This card mirrors the `archive` and `handoff` blocks for
> TASK-20260731-005 in
> `coordination/goals/GOAL-P13-001/batches/BATCH-002/dispatch_queue.json`.

---

## Objective

Turn the validated and red-teamed NC-2 measurement into **scoped official ledger
state**, in one isolated commit the post-commit verifier accepts.

## Records to write

| Record | Path |
|---|---|
| Evidence | `ledger/evidence/EV-SSI-006.yaml` |
| Decision | `ledger/decisions/DEC-20260731-001.yaml` |
| Goal checkpoint | `ledger/goals/GOAL-P13-001.yaml` |
| Hypothesis update | `ledger/hypotheses/H-P13-001.yaml` |
| Receipt | `.../archives/TASK-20260731-005/ledger_commit_receipt.json` |

## The lineage must not be lost

`EV-SSI-006` **must carry, in an explicit field and not merely by reference**,
that it **continues the `EV-P13-001` lineage** despite the different area code,
and why:

- `EV-P13-002` **is malformed** — `tools/validate_ledger.py` requires
  `^EV-[A-Z]+-\d{3}$` and `P13` contains a digit — so `EV-P13-001` is
  **grandfathered legacy and is not extended**;
- `EV-ISO-002` was **declined** because the ISO area belongs to an unrelated
  line (`H-ISO-001` / `RQ-ISO-001` / `EXP-ISO-001`) and `EV-ISO-001` does not
  exist, so it would open a numbering hole in somebody else's area;
- `EV-SSI-006` is the **sequential successor** of the supersingular-isogeny
  evidence records and it validates.

Likewise `EXP-SSI-002` is recorded as the **direct successor of
`EXP-P13VOW-001`**.

## Before you interpret anything

**Verify validity first.** Expected run count, schema-complete manifests, seed
integrity, raw/summary agreement, control comparability. **If the validator
verdict is INCOMPLETE or INVALID, the run set is not evidence** — return it to
the Executor with the concrete defects **listed**, record the decision as such,
and **do not interpret the numbers**. An invalid run set **ends this task, not
the goal**.

## Honesty constraints on the records

- **Scope every conclusion** to the tested primes, `B` settings, variants,
  seeding, solver, host and budget. **Toy-scale evidence is never presented as
  crypto-scale validation.**
- Every NIST-I/III/V figure is labelled **EXTRAPOLATION** and carries
  EA-1..EA-6, with **EA-3 beside it**.
- **Report the result in whichever direction it fell**, using the reading that
  **fired** under the frozen pre-registration, and **do not re-frame it**. Carry
  the asymmetric-licensing statement (S-2) into the evidence record so that a
  comfortable result is not read as a safety claim.
- **Strength honestly.** One execution on one host is **not** `replicated`.
- **`reject_scoped` on a single unreplicated empirical-only run set is
  forbidden.** If a theory-weakening conclusion is warranted, use **`weaken`
  paired with replication**, and archive its refutation basis — counterexample
  certificate, then derivation note, then a declared `empirical_only` basis — in
  **this same commit**. An undeclared basis is the failure, not the absence of a
  proof.
- **Fill `knowledge_promotion` explicitly.** A KN-FIND is promoted only on
  `support` or `reject_scoped` at `replicated`/`strong` strength; on a single
  unreplicated one-host run set that bar is **not reached**, so a **concrete
  `not_warranted` reason naming exactly that** is the expected honest outcome.
  If a KN-FIND *is* promoted, its entry **and a regenerated
  `knowledge/INDEX.md`** go in this same commit.
- **`H-P13-001` stays at `analyzed`.** It may not move toward `supported` — all
  four asymptotic-claim promotion gates remain open. Update
  `adjudicated_positions.concrete_threat_nist1` to record what NC-2 found and at
  what scope; append `status_history` **only if a status actually changed**;
  carry `heuristic_1_status` **unchanged**.
- **Goal record**: BATCH-002 closing checkpoint beside the opening one, **exactly
  one `next_action`**, the prior one preserved under a `prior_next_action_*` key.
- **Do not set `GOAL-P13-001` to `completed`.** Closure requires a **three-model
  quorum with pairwise distinct `resolved_model_id` values**, which is **not
  available under this harness**. If the campaign runs out of budget without a
  completion criterion met, `closed_at_budget` or `paused` is the honest status.
  **Never record an attestation that was not obtained.**

## Carry unrepaired, in both the evidence and the decision

GAP-1; GAP-2; Section 4.1 UNVERIFIABLE-AS-WRITTEN; Heuristic 1 unproven and not
falsified with zero tail resolution at `u ~ 13`; the 0.05–3.51 bit partial
control failure of RUN-P13VOW-001; and the **shared-model fallback independence
limitation** (all roles resolve to `claude-opus-5`, `model_verified: false`) with
**CTRL-RT039-A's adversarial-mutation-selection rule named as the binding
mitigation practice**.

## Staging

- **RUN ALONE.** One commit.
- Stage **only** the declared paths: this receipt, the five ledger records, and
  the seven review artifacts of TASK-20260731-003 and TASK-20260731-004.
- Both the `ledger/evidence/` and `ledger/decisions/` paths are **declared
  unconditionally**. Any shortfall is handled as **declare-then-deviate at
  close**, recorded in the receipt **by name** — not by narrowing the
  declaration now, and never by creating a placeholder record.
- **Never rewrite history** over a pushed run record; supersede under a new
  identifier; any branch sync is a merge, never a rebase.
- **No official transition from uncommitted artifacts.** The post-commit
  verifier must accept the commit first.

## Completion gate

L1–L10 as stated in the queue's `handoff.completion_gate` for this task.
