# Pre-registration and matched-null check — TASK-20260801-003

**Under review:** `PA-DS-001-v2-ctrl-matched-null` /
`experiments/EXP-DS-001/controls/CTRL-RT047-MATCHED-NULL.yaml` /
`experiments/EXP-DS-001/amendments/v2_ctrl_matched_null.yaml`
**Bound snapshot:** `8d28be76f688b0120e74449322723d7d3ce3011d` (parent `257a7b23f`)
**Verdict:** PASS. **Recommendation to TASK-20260801-004:** APPROVE.
**Role:** queue role `reviewer`, served by the red-team subagent (no dedicated
reviewer subagent exists in this harness). Independent session; this session did
not author TASK-20260801-001.

Everything below was checked against the committed snapshot and against archived
run records, not against the control's own prose. Where the control asserts a
number, I recomputed it.

---

## 0. Snapshot integrity (precondition)

| Check | Result |
| --- | --- |
| Working tree matches snapshot over `experiments/EXP-DS-001` and `ledger` | clean, no drift |
| Snapshot is additive | 4 files, 1244 insertions, **0 deletions** |
| Declared path count | 4, matches the receipt |
| `sha256(specification.v2.yaml)` recomputed | `898304bf…5a636a` — matches the declared parent hash, and matches the `contract.parent_sha256` archived in `RUN-DS-001-ctrl-unplanted/raw-result.json` |
| Matched-null run package exists? | **No.** `experiments/EXP-DS-001/runs/` holds only `-impl`, `-measure`, `-heur`, `-ctrl-unplanted` |

That last row is what makes the pre-registration checkable rather than asserted:
the map is hash-bound in a tree that provably contains none of its data.

---

## 1. Is the disposition map genuinely pre-registered? — **YES**

### 1.1 Exhaustive and mutually exclusive? Audited, not accepted

I did not take the author's `exhaustiveness_check` on assertion. I enumerated all
nine `(band(W), band(U))` cells and evaluated the four branch conditions as
literally written:

```
(LOW ,LOW ) -> [D-1]      (MID ,LOW ) -> [D-4]      (HIGH,LOW ) -> [D-4]
(LOW ,MID ) -> [D-4]      (MID ,MID ) -> [D-3]      (HIGH,MID ) -> [D-4]
(LOW ,HIGH) -> [D-4]      (MID ,HIGH) -> [D-4]      (HIGH,HIGH) -> [D-2]
unclassified: []          doubly-classified: []
```

**I could not construct an unclassifiable or a doubly-classified result at the
top level of the map.** D-5 pre-empts all four on inadmissibility. The count the
author claims (three matched cells plus six mixed) is correct.

### 1.2 But there *is* a gap one level down — DEF-1

D-1's sub-branches do **not** partition D-1. `D-1a` requires both proxies
*within* a factor of 2 of the live re-measure; `D-1b` requires a proxy to
*exceed* twice it. Nothing covers a proxy that falls **below half** of it:

> Witness: `W = 0.004`, `U = 0.002` against a live re-measure of `0.032 / 0.0147`.
> Both proxies are LOW, so D-1 fires. `0.004` is 8× *below* the re-measure, so it
> is neither within a factor of 2 nor in excess of twice it. **D-1 with no
> sub-branch.**

Severity minor: D-1a/D-1b differ only in mandated *wording*. The decision, the
status transition, the refutation artifact, the companions and the
knowledge-promotion expectation all live at D-1 level and are identical. The
uncovered corner is also the one most adverse to the structure claim (the null
outperforming the real object by more than the real object's own margin), so the
gap does not shelter the hypothesis. It is still a gap, and it admits a post-hoc
adjective.

### 1.3 Are 0.5 and 0.9 inherited, or reinvented at convenient values? — Inherited

Traced to source:

- **0.5** — `H-DS-001.predictions.per_relation_cost_ratio_R` (`R < 0.5`) and
  `H-DS-001.falsification_conditions[2]`: *"R_null < 0.5 whenever R < 0.5:
  apparent gain is an engine artifact, not Semaev structure"*. Also `S1` in
  `specification.v2.yaml`.
- **0.9** — `H-DS-001.statement` (*"R_null >= 0.9 whenever R < 0.5"*) and
  `specification.v2` `S1` / `F2`.

Both thresholds are stated on the **null ratio** in their sources and applied to
the **null ratio** here — the inheritance is on the same variable, not a quiet
transplant onto a different quantity. The three-band split is the forced
consequence of holding both frozen thresholds simultaneously; no fourth number
was introduced.

### 1.4 Is the MID band a real reading or a placeholder? — Real, but its stated reason is wrong (DEF-2)

D-3 commits: decision `inconclusive`, status unchanged, an explicit
`why_not_weaken`, an explicit `why_not_structure`, and a specific next action
(B-sweep **plus** an object-cost-parity measurement). That is a committing
reading, not a gap-filler.

Its **rationale is nonetheless inaccurate**, and inaccurate in the direction that
protects the hypothesis. `specification.v2` `F2` reads:

> `F2: R < 0.5 AND R_null < 0.9 on the matched null → structure gate fails.`
> *"This INCLUDES the former middle band `0.5 <= R_null < 0.9`; F2 is aligned with
> the S1 R_null gate so every R < 0.5 outcome is either S1-eligible on the null
> axis or F2."*

So under the frozen experiment contract, a MID/MID matched-null result (with
`R_real < 0.5`) **is F2_met**. D-3 instead says the falsifier "is stated at the
0.5 threshold and is NOT met in this band" and that a weaken "would be the
Coordinator inventing a threshold after the fact." The 0.9 threshold is not
invented — it is frozen in F2 and F2 already swallows the middle band. The
amendment's `non_changes` line *"Does not change the S1/F1/F2/F3 success criteria
of the v2 matrix"* is therefore inaccurate for this one cell.

Why this is not a REVISE:

1. F2's own prescribed disposition is `reject_scoped`, which `DEC-20260801-003`
   and the Coordinator contract independently forbid on a single unreplicated
   empirical-only run. `inconclusive` is the residual. D-3 reaches the right
   **action** by a wrong **route**.
2. The map is uniformly softer than F2's literal disposition — including at D-1,
   where it also declines `reject_scoped` and says why. This is not a
   MID-specific escape hatch.
3. MID/MID is a low-probability corner (see §3.3).

Resolution needs no edit to the frozen map: F2 binds of its own force, and the
run must record the `r1_observation_label` / F2 flag the way the BATCH-020
`raw-result.json` did. If MID/MID fires, the record says F2 as frozen is met and
that F2's prescribed `reject_scoped` is unavailable on an unreplicated run. That
makes the reading *stricter*.

### 1.5 Is any branch inconsistent with the campaign's prohibitions? — No

`forbidden_under_every_branch` covers S1_met, F1_met, structure_gate_passed,
support, asymptotic/crypto-scale claims, affected-scheme statements, HEUR-DS-1
validation or refutation, `reject_scoped` including as-impossibility, changes to
H-IC-001/H-STR-002, `dominated_by: null`, and any movement of G1–G4. I read every
branch body against that list; nothing breaches it.

**On D-1's `weaken` specifically — is the scoping honest, or does it smuggle in a
broader adverse transition?** Honest, with one recorded gap. The scoping is
load-bearing, not cosmetic: D-1 states affirmatively that a weaken is *not* a
finding that the mechanism fails, **because the mechanism was never exercised**
(`smoothness_abort=false`, `is_B_smooth` never called); it forbids
`reject_scoped`; it forbids lane closure with an explicit citation to the
premature-closure rule; it requires a refutation artifact archived in or before
the same ledger commit; and it mandates a replication at a second seed plus the
B-sweep. The confirm/falsify asymmetry — D-1 moves status, D-2 cannot — is the
*correct* asymmetry (one counterexample can weaken; support needs replication
across two bit sizes), and the contract gives that reason on the record.

The gap (**DEF-3**): H-DS-001's falsifier and v2's F2 both conjoin `R < 0.5` on
the **real** arm. D-1's condition is stated purely on the matched-null pair. If
the live re-measure landed at or above 0.5, D-1 would still fire, would still
assert that H-DS-001's own falsifier fired — false in that corner — and would
still prescribe `weakened` on that false premise. It would take a 15–34× host
deviation, so likelihood is low; low is not zero, and a status transition on a
false premise is what this review exists to catch. Fix without touching the map:
TASK-20260801-004 records that D-1's weaken is available only if the live
re-measure `R_real` is below 0.5 on **both** proxies, else the run reads as D-5
instrument signal. That only removes an adverse transition, so it cannot flatter
the hypothesis.

### 1.6 Could this map have been written *after* seeing a result? — No

The strongest evidence is not the commit ordering, it is the map's *shape*:

- The branch the author **predicts** (D-1, anchor `W≈0.03`, `U≈0.015`) is the one
  **adverse** to the lane's own claim, and is the only branch carrying a status
  transition.
- The **favourable** branch D-2 is deliberately built to be **non-promoting**:
  H-DS-001 stays `analyzed`, with the arithmetic reason spelled out (one bit size
  supplied against a two-bit-size criterion), explicitly "so that a favourable
  result cannot be promoted on enthusiasm."
- D-5 removes the possibility of reading a band off a defective run at all.

An author writing after a favourable number would not construct a map in which
the favourable outcome cannot help. This is genuine pre-registration.

---

## 2. Is the matched null a fair matched control? — **YES**

### 2.1 Matched axes, verified against the archived run record

| Axis | Preserved? | How I verified |
| --- | --- | --- |
| Group order | yes | `RUN-DS-001-ctrl-unplanted/raw-result.json` → `instance.full_group_order = 753848` (with `p = 752627`, `subgroup_order_n = 241`). `N = 753848` matches **exactly**. Order is not confounded with object. |
| Composition law | yes | abelian operation on a set of the same cardinality; negation `N-g` mirrors point negation |
| Factor-base geometry | yes | 64 unsigned / 128 signed, negation-closed — matches archived `factor_base_size = 64`, `signed_factor_base_size = 128`. The rejection of `g = N/2 = 376924` is correct and necessary: that element is its own negation and would collapse the signed base to 127. |
| Arity | yes | `m = 4` frozen |
| Representation density | yes | recomputed: `C(131,4) = 11,716,640` over `N = 753848` = **15.5** expected representations per uniform target. The control's "≈1.2e7" and "≈16" are accurate; the success-probability regime does not move. |
| **The algorithm** | yes | `algorithm_invariance` binds `naive_search`/`split_search` unchanged, freezes `smoothness_abort=false`, 200 relations, seed 101, `charge_backend_units` and its constant 40, the backend ID, the identity `encode_intermediate` (`D = 2^40` vs residues `< 2^20`), and the exact-equality `claw_key` join. Inability to parameterize the object without touching search logic **must** be declared as a deviation with the exact diff; D-5 fires on an undeclared code change. |

Destroyed, as required: curve, x-coordinate, point at infinity, summation
polynomial, degree, resultant, multihomogeneous grading, smoothness-bearing
intermediate. The prohibition on reusing curve x-coordinates as residues closes
the one route by which curve structure could leak back in.

### 2.2 The RT-20260731-047 defect — can it recur? **No, and it is closed three independent ways**

The previous null failed because `null_split_search` was a *different procedure*
that rebuilt a 4096-entry table inside every attempt, while the real split arm
built its table once (`table_build_reported_wall_seconds = 0.0119 s`, amortized
over 200 relations) — manufacturing `R_null = 111.4` out of an amortization
mismatch rather than out of structure.

This control specifies amortization parity explicitly enough that the same defect
cannot recur silently:

1. **`algorithm_invariance`** forbids a separate procedure at all — the
   once-built table comes from running the same code, not from a promise.
2. **D-5 fires and SUSPENDS the entire map** if "the matched-null split arm does
   not amortize its claw table once as the real split arm does." That is a
   pre-registered guard naming the exact prior defect, not a post-hoc note.
3. **`required_per_arm_fields`** makes `table_build_reported_wall_seconds` and
   `peak_claw_table_entries` mandatory for **every** arm — the legacy null
   recorded both as `null`, and that omission is now itself an admissibility
   failure — and `required_disclosures` forces an explicit yes/no on whether the
   matched-null split arm amortizes once.

That is sufficient. **This is not a REVISE.** A convenience strengthening (an
integer `claw_table_build_count` per arm asserted `== 1`) is recommended, not
required, since the two mandatory wall/entry fields already expose a per-attempt
rebuild.

### 2.3 Non-structural confounds I hunted for

- **CONF-1 — per-operation cost (modular add vs curve add).** Both arms get
  cheaper on the additive object, but the split arm's dict-build and hashing
  overhead does *not*, so its fixed overhead becomes a larger share of its wall
  time. This pushes `W` **up** for reasons with nothing to do with structure, i.e.
  toward D-2/D-3.
  **Largely neutralized, and by the contract's best design decision:** the
  charged-unit proxy is object-independent (constant 40 per membership call
  regardless of group), so the confound moves `W` and leaves `U` alone. Requiring
  D-2 to satisfy `W ≥ 0.9` **AND** `U ≥ 0.9` means the confound alone cannot
  manufacture a structure reading; a confound-driven split lands in D-4, which is
  correctly labelled a positive cost-model finding rather than an ambiguity to be
  resolved by picking a proxy. Residual (**DEF-4**): D-3 requires the
  object-cost-parity measurement, D-2 — the branch where the confound matters
  most — does not.
- **CONF-2 — base-selection policy is confounded with the object (DEF-5).** The
  real base is a *frozen deterministic subset* of `E(F_p)`; the null base is
  *random residues*, and structured bases are forbidden. So the null differs along
  **two** axes, not one. Unavoidable in variant (a), and harmless *a fortiori*
  under D-1 (if the advantage transfers, it transfers whichever difference carried
  it — either way it is not Semaev structure). Under D-2/D-3 it is a live
  alternative explanation the map does not name.
  **Cheapest discriminating control:** RT047-CTRL-1 **variant (b)** — keep
  `E(F_p)`, replace only the factor base with 64 uniformly random curve
  x-coordinates. One arm, essentially free, already written in RT-20260731-047.
- **CONF-3 — the two groups may be isomorphic.** If `E(F_p)` is cyclic of order
  753848 it is isomorphic to `Z/753848Z`. Not a defect: destroying the
  *representation* and the summation-polynomial machinery is the intended lesion,
  and preserving the composition law is a matched-control *requirement*. It does
  sharpen the prior — with abstractly isomorphic groups and a fixed algorithm, a
  D-2 outcome is more plausibly a cost or base-policy artifact than structure,
  which is a further argument for DEF-4 and DEF-5.

No accidental retained structure threatens the reading. Negation closure makes
`m`-sums non-uniform (terms `g + (−g)` cancel), and `N` is composite with proper
subgroups — but the archived curve object of the same order has both properties
too, so both are **matched**, not introduced.

The control also states itself that DLP in `Z/NZ` is trivial by one modular
inverse and draws the right consequence: it measures **algorithm cost only** and
claims nothing about hardness.

---

## 3. Also-checked items

### 3.1 `PER_TARGET_CAP_SECONDS` (Validator defect D-3) — PASS

Declared at `5.0 s`, with the bias direction stated **correctly**: the cap
truncates the slower naive arm first, shortening the numerator's competitor and
biasing `R` **downward**, in the direction that flatters the split arm. The guard
is pre-registered: any arm with `per_arm_capped_attempt_count > 0` **suspends the
disposition map**, the run is `cap_truncated`, the decision is `inconclusive` on
the instrument, and the repair is to raise the cap and re-run — routed as
AGENTS.md rule 5 infrastructure signal, never a mathematical negative in either
direction. Mandatory in `manifest.json`, `raw-result.json` and `summary.json`
with per-arm counts.

I verified the "never bound at BATCH-020" claim independently: the archived
`per_relation_wall_samples` on `real_naive` top out near `0.1196 s` against the
`5.0 s` cap. The contract's own caution — that this is a property of the cell, not
of the driver — is correct and retained.

### 3.2 Both proxies, neither privileged — PASS (with DEF-6)

`both_proxies_mandatory` makes every ratio an ordered pair and declares any
table, summary line or prose sentence giving one number without the other a
protocol violation. All three required ratios carry `proxies: [wall,
charged_units]`. D-4 refuses to resolve a disagreement by picking a proxy.

**DEF-6:** the charged-unit proxy is a *decision variable* of the map and its
formula is nowhere written. I recovered the intended definition by reproducing
the reference figures from the archived run — `1914080/130630800 = 0.014653`
(quoted 0.0147) and `465080/486040 = 0.95688` (quoted 0.9569) — so `U` is
`reported_backend_units` per arm over `n_usable`, the divisor cancelling at 200.
Not blocking: the two candidate definitions coincide whenever both arms reach 200
relations, and D-5 fires if any arm does not, so no analyst degree of freedom
survives to execution. It should still have been written down.

### 3.3 A caution the write-up must carry — DEF-7

`charge_backend_units` charges a constant per membership call regardless of the
group, and the algorithm, `B`, `m` and target count are all held fixed. `U` is
therefore close to a function of the enumeration counts rather than a measurement
*of the object*, and `U ≈ 0.0147` is close to a foregone conclusion. **The
discriminating limb is `W`.** The map is not wrong for requiring both — D-1
requires both and D-4 catches disagreement — but a write-up presenting "both
proxies agree" as two *independent* confirmations would overstate the evidence.
This is also why MID/MID (DEF-2's corner) is improbable.

### 3.4 Remaining checks — all PASS

- **Live plant excluded:** `forbidden: true`, `plant_divisor = 1.0` on every arm,
  `plant_applied: false`, `synthetic_known_answer_used: false`;
  `CTRL-RT025-PLANT-LIVE` stays UNDISCHARGED after this batch. The reason
  (RT047-B3: a threshold-free strict inequality on a split-only divisor gives
  `R_on/R_off = 1/4` by algebra, false-positive rate 1, no measured specificity)
  is accurate and the exclusion follows from it. RT047-CTRL-2/-3/-4 are named as
  deliberately not discharged, with reasons, rather than left to lapse.
- **Claim ceiling toy:** `claim_tier: toy`, `confirmatory_status:
  exploratory_control`, with G1–G4 held OPEN and RT038-B1..B7+M1 and
  RT047-B1..B5+M1 held binding under **every** branch.
- **`dominated_by` may not be null:** matched Pollard-rho (744 *measured* group
  ops) and BSGS (32 modeled ops / 16 stored elements) carried forward, plus the
  null object's own trivial baseline. Time, memory and stored-element axes all
  appear.
- **Parent binding:** recomputed `sha256` matches, and matches the value archived
  in the BATCH-020 run record — consistent across batches.
- **Immutable inputs:** untouched; the snapshot is additive only.
- **Supersession:** only the *forward reading* of the null axis is superseded;
  prior `R_null` figures stand as measurements that license no structure claim.
  Correction-by-new-record, per AGENTS.md rule 4.
- **Fidelity to the prescribed action:** compared clause by clause against
  RT047-CTRL-1 variant (a) and RT-047's `next_concrete_action`. Every element is
  present, `n_enum` included; the same-host re-measure arms are an addition RT-047
  did not ask for and are a genuine improvement.

---

## 4. Verdict and why it is not REVISE

**PASS. Recommend APPROVE to TASK-20260801-004.**

Under RC-21 a REVISE at any severity records BATCH-021 non-execution, so the
question is whether any defect found would corrupt the measurement or license an
unearned claim. **None does.** Both dominant questions pass on audited grounds:
the map is exhaustive and mutually exclusive over all nine two-proxy cells by
mechanical enumeration, its thresholds are traceable to H-DS-001 and to
`specification.v2`'s S1/F2 rather than invented, its middle band commits to a
decision and a next action, and its favourable branch is deliberately built to be
non-promoting. The matched null preserves order (verified at 753848 against the
archived run record), composition law, base geometry, arity, density (recomputed
at 15.5) and the algorithm, while destroying every elliptic and Semaev property —
and the specific failure named as REVISE-if-absent, the legacy null's per-attempt
table rebuild, is closed three independent ways including a pre-registered D-5
suspension naming that exact defect.

The eight recorded defects are labelling and rationale corners, each resolvable
by a *stricter* reading recorded at approval or decision time without editing any
hash-bound artifact, and none can produce a false positive for the hypothesis.
Blocking the single measurement that finally tests this lane's load-bearing
inference over corners of that kind would itself be a failure of proportion.

### Reading limits binding on TASK-20260801-009

1. **DEF-2** — `specification.v2` F2 binds independently of the map; the
   `r1_observation_label` / F2 flag must be recorded in the run package.
2. **DEF-3** — D-1's `weaken` requires the live re-measure `R_real < 0.5` on both
   proxies; otherwise read as D-5 instrument signal.
3. **DEF-4 / DEF-5** — a D-2 or D-3 reading requires the object-cost-parity
   measurement *and* RT047-CTRL-1 variant (b) before the word "structure" is used.
4. **DEF-7** — do not present two-proxy agreement as two independent
   confirmations.

### What would have forced REVISE (recorded so this PASS is falsifiable)

Any one of: the null failing to match the group order; amortization parity left
unspecified or unguarded; `PER_TARGET_CAP_SECONDS` undeclared or declared without
its bias direction; either proxy privileged; a branch prescribing S1_met, support,
`reject_scoped` or asymptotic movement; a gap or overlap at the **top** level of
the map, which I searched for mechanically and did not find; a live plant admitted
to this batch; or a `parent_contract_sha256` that did not reproduce.

### Prohibitions observed

No commit. No repair authored. No file written outside this review directory. No
hypothesis, ledger record, specification, control, amendment or BATCH-020
artifact modified. No run authorized — this review is not an approval.

### Inference (recorded honestly)

`requested_policy: review-xhigh` (alias of `review-adversarial`);
`resolved_model_id: claude-opus-5`; `fallback_used: true` (this harness cannot
resolve `orchestration/model-policies.yaml` identifiers);
`model_verified: false` (no `orchestration.adapter doctor --probe` was run in this
session); `independent_session: true`; `degraded_allowed: false`;
role requested `reviewer`, served by `red-team`.
