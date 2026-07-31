# RT-20260730-003 — falsification review of EXP-STR-005 RT35-CTRL probe

**Task:** TASK-20260730-003 · **Goal/batch:** GOAL-ECDLP-001 / BATCH-015  
**Role:** red-team, independent session · **Do not commit**

**Bound snapshot:** `0122174582bff55f660e4488c55f1054d1ee333a` (parent `06f37d31…`), ancestor of HEAD `230a1734…`, branch `claude/ecdlp-b011`. SHA-256 of the three producer paths recomputed and matched to `dispatch_queue.json` archive hashes; Git blob identity matches the snapshot tree.

**Inference:** requested `review-adversarial` / `review-xhigh` at `xhigh`; resolved `cursor-grok-4.5-high-fast`; `fallback_used: true`; `independent_session: true`.

**Verdict: REVISE**

---

## 1. Producer claims vs independent reading

| Claim | Producer | This review |
|---|---|---|
| CTRL-1 | `PASS_CTRL4` at B=192,193 | **CONFIRM** |
| CTRL-2 | `FAIL_SUPPLY_OR_FB_SHORT` (3 cells shortfall≥2) | **REJECT as faithful RT35-CTRL-2** — budget non-faithful |
| `stand_down_basis_defective_on_committed_code` | `true` | **NOT LICENSED** |
| Claim tier / mechanism | `toy`; not H-STR-002 | **CONFIRM** — no tier inflation, no mechanism claim |

---

## 2. Focus 1 — collection budget (blocking)

RT35-CTRL-2 (BATCH-014 red team, adopted into DEC-20260729-004’s single next action) and EXP-STR-004 `collection_quota` require:

```text
num_targets = Q(B) = max(60, B + 10)
include_phi_orbits = False
compare len(relations) to R_base(B)
```

The harness loops at most `5 * num_targets` candidate slots and stops when `len(relations) >= num_targets`. The Q floor of 60 exists **because** small-B cells otherwise lack enough attempts to make R_base rows probable.

The probe instead called:

```text
_collect_relations(..., num_targets=R_base, ..., include_phi_orbits=False)
```

At the failing cells that is a ~12× under-sample:

| Cell / arm | R_base | attempts (cap) | hits | shortfall | Q / Q-cap |
|---|---:|---:|---:|---:|---|
| L12 / E_prime | 5 | 25 | 1 | 4 | 60 / 300 |
| L13 / A_prime | 6 | 30 | 4 | 2 | 60 / 300 |
| L13 / E_prime | 6 | 30 | 2 | 4 | 60 / 300 |

All three shortfall≥2 rows **exhausted** `5*R_base`. That is budget starvation, not an established supply collapse under the declared probe. Constant-rate extrapolation to 300 attempts predicts fills at all three cells. Larger-B and m=3 cells fill under the reduced budget — failure sits exactly where the Q floor was designed to protect.

**Conclusion:** `num_targets=R_base` is not a faithful reading of DEC-20260729-004 / RT35-CTRL-2. It under-samples and can falsely fire shortfall≥2.

---

## 3. Focus 2 — FAIL → reopen without mechanism claim

DEC-20260729-004 pre-registers: if CTRL-1 finds a short list at B=192/193, **or** CTRL-2 finds shortfall≥2 at any cell, then the stand-down basis is defective in substance and a successor must reopen the **execution question** — not adjudicate H-STR-002’s mechanism.

- **Shape:** correct. Producer fences alpha/ladder/driver/rank/cost and mechanism (`claim_tier: toy`, `what_this_is_not`).
- **Firing:** incorrect on this package. Because CTRL-2 was not the declared supply probe, `FAIL` must not reopen execution from these artifacts alone.

---

## 4. Focus 3 — overclaim / claim-tier inflation

- **Claim-tier inflation:** not found (`toy` is correct).
- **H-STR-002 mechanism overclaim:** not found.
- **Falsification-trigger inflation:** found. Setting `stand_down_basis_defective_on_committed_code=true` asserts the DEC falsifier on a non-faithful CTRL-2. That is the overclaim that matters for the ledger.

Minor: DEC also asked for measured distinct-target count; the probe omitted it.

---

## 5. Integrity (non-blocking on math)

- Snapshot commit exists, is an ancestor of HEAD, paths/hashes match.
- Working-tree receipt still shows `commit_sha: null` / `pending_post_commit` while the queue records the SHA — Coordinator hygiene, not a reason to distrust the blobs.

---

## 6. Narrowest supported statement

On snapshot `01221745…`, `_build_phi_invariant_factor_base` on CURVE-J12S1 satisfies CTRL-4 at B=192 and B=193. The same package’s supply collection used `num_targets=R_base` and observed shortfall≥2 at three small-B arm-cells under that reduced attempt cap. **That does not establish** a RT35-CTRL-2 / Q(B) supply shortfall, **does not license** `stand_down_basis_defective=true`, and **does not** speak to H-STR-002’s mechanism.

---

## 7. Required next action

Re-run CTRL-2 only (CTRL-1 may stand) with `num_targets=Q(B)=max(60,B+10)`, orbit closure off, report `len(relations)`, hits, attempts, distinct-target count, and shortfall vs `R_base`. Re-evaluate the pre-registered falsifier **after** that run. Until then, ledger archive must not treat the stand-down basis as defective on the strength of EXP-STR-005 as committed.
