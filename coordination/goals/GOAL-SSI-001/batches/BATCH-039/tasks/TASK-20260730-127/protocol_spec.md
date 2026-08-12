# FC0 peak-byte toy protocol — `FC0-PEAKBYTE-TOY-PROTOCOL-R1`

**Task:** TASK-20260730-127 / BATCH-039 / GOAL-SSI-001
**Gate chosen:** **A** (numeric composition operator + bound units + numeric
width + peak-byte accounting under an explicit in-repo protocol).
**Decision authority:** DEC-20260730-036 / EV-SSI-038 / RT-20260730-125.

---

## 0. Scale disclaimer (read first)

This protocol is **protocol-toy / scaffold-scale**. Every numeric constant
below is a *stipulated placeholder unit weight* declared in this document. It
is **NOT** a byte width measured from any CSIDH/CSI-FiSh implementation, **NOT**
a security parameter, **NOT** a number of security bits, **NOT** derived from
any curve, isogeny, or quantum-circuit computation, and **NOT** a QUERY_MEMORY,
QM-MEMORY-MAP, QM-STOPPING, or QM-ERROR clearance.

The point of the gate is narrow and explicit: demonstrate that the
`composition_aggregation` / `global_memory_bound` lineage
(BATCH-023 → BATCH-038 placeholders) admits **one** internally-consistent,
independently-recomputable numeric instantiation *once an explicit protocol
supplies the missing conversion constants and composition rule* — as opposed to
yet another placeholders-only schema lane. It does not advance the real
cryptanalytic boundary.

Constants here are deliberately small integers so that no reader can mistake
them for real widths. Replacing them with real measured widths is explicitly
out of scope and would require EXP-SSI-001 (not launched here).

## 1. Source of the live-set structure (no invention)

The stages and their live member sets are taken **verbatim** from
BATCH-023 `peak_live_set_accounting.yaml` → `stage_live_sets`
(`TASK-20260730-063`), which itself walks the BATCH-022 `StageLiveSetTracker` /
`STAGE_LIVE_SETS` checklist against the BATCH-013 `recovery_spec.md`. This
protocol invents **no** new stages and **no** new members; it only supplies
conversion constants and a composition rule on top of the existing membership.

| Stage | Live members (from BATCH-023) |
| --- | --- |
| `preparation` | `B_input, B_attempt, W_label, R_label` |
| `sieve_attempt` | `B_input, B_attempt, W_sieve, R_sieve, B_sieve` |
| `recovery` | `B_input, B_attempt, B_post, B_recovery, accepted_transcript` |
| `tail_verification` | `B_input, B_attempt, B_recovery, M_tail, B_candidate` |

## 2. Slot classes and the class map

Each member is assigned to one of the named BATCH-023 peak-live-set slot
classes `{W, R, B, M}`, plus a transcript class `T` for `accepted_transcript`.
The class map is by explicit enumeration (not a fuzzy prefix guess):

```
B_input, B_attempt, B_sieve, B_post, B_recovery, B_candidate  -> B
W_label, W_sieve                                              -> W
R_label, R_sieve                                              -> R
M_tail                                                        -> M
accepted_transcript                                          -> T
```

Any member not in this map is **out of protocol** and the harness must reject a
ledger that references one.

## 3. Slot unit weights (the declared conversion factors) — `bound_units = protocol_slot_bytes`

These are the stipulated toy conversion constants. Unit: `protocol_slot_bytes`
(a fictional unit of this protocol, **not** real bytes).

| Slot class | Unit weight `w(class)` [protocol_slot_bytes] |
| --- | ---: |
| `W` | 8 |
| `R` | 4 |
| `B` | 2 |
| `M` | 16 |
| `T` | 1 |

Rationale for the *ordering only* (not the magnitudes, which are arbitrary toy
values): `M_tail` (tail-verification buffer) is stipulated heaviest, working
sets `W` next, relation labels `R`, block/basis handles `B` light, and a
transcript handle `T` lightest. The magnitudes carry no cryptographic meaning.

## 4. The numeric composition operator — `max_over_stages_of_sum_of_live_member_slot_widths`

The protocol composition operator has two levels, matching the physical fact
that within a stage the listed members are **concurrently live** (so their
costs add) while the stages themselves are **sequential** (so the peak is the
max, not the sum). This is exactly the BATCH-023 `peak = max-not-sum` rule,
now instantiated with byte widths instead of raw object counts.

1. **Within-stage aggregation (additive):**

   `stage_byte_load(s) = sum over members m live at stage s of w(class(m))`

2. **Across-stage composition (max, not sum):**

   `peak_byte_bound = max over stages s of stage_byte_load(s)`

3. **Mistaken-sum negative control:** the across-stage *sum*
   `sum over stages s of stage_byte_load(s)` is explicitly **rejected** as the
   peak (it double-counts sequential stages). The harness records it and asserts
   it is flagged `rejected_as_peak: true` and is strictly greater than the peak.

## 5. Worked instantiation (recomputed by the harness)

Applying §3 weights and the §2 class map to the §1 membership:

| Stage | Members → weights | `stage_byte_load` |
| --- | --- | ---: |
| `preparation` | B(2)+B(2)+W(8)+R(4) | **16** |
| `sieve_attempt` | B(2)+B(2)+W(8)+R(4)+B(2) | **18** |
| `recovery` | B(2)+B(2)+B(2)+B(2)+T(1) | **9** |
| `tail_verification` | B(2)+B(2)+B(2)+M(16)+B(2) | **24** |

- **`peak_byte_bound` = max(16, 18, 9, 24) = 24 `protocol_slot_bytes`**, attained
  at stage `tail_verification`.
- **mistaken cross-stage sum** = 16 + 18 + 9 + 24 = 67 `protocol_slot_bytes`,
  **rejected** as the peak.

Every number in `instantiation_ledger.yaml` (§ `slot_width_table`,
`stage_byte_loads`, `peak_byte_bound.value`, `mistaken_sum_across_stages.value`)
is recomputed from the constants in §2–§4 by
`instantiation_harness/ledger_checks.py`. A ledger value that disagrees with the
recomputation, an out-of-protocol slot width, an out-of-protocol member, an
invented numeric field (e.g. `security_bits`), or an illicit clearance flag
(`query_memory_cleared`, `clearance`, `pin_complete`, breakthrough/completion)
causes the harness to **fail**.

## 6. What this gate does and does NOT establish

**Does (at protocol-toy scale, this batch only):**

- Instantiates a named numeric **composition operator** (§4).
- Instantiates **bound units** (`protocol_slot_bytes`, §3).
- Instantiates a numeric **width** table and a numeric **peak-byte** accounting
  (§3, §5), discharging — *at toy scale* — the previously-null
  `composition_operator` / `numeric_width` / `peak_byte_bound` placeholders that
  BATCH-023..038 carried.

**Does NOT:**

- Clear QUERY_MEMORY. Disposition stays
  `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`; named blockers QM-STOPPING,
  QM-MEMORY-MAP, QM-ERROR remain unreconciled.
- Instantiate τ or establish joint Q/S/P/C(+H) finiteness. **QM-STOPPING remains
  open with `control_result: FAIL`** (BATCH-037/036/035/034/033/032/031/018
  retained). This is gate A, not gate B.
- Supply a *cryptographic-scale* memory bound. The widths are toy; the number 24
  is meaningless outside this document.
- Equate BATCH-014, invent CollimationSieve@6f9188e4 APIs, or modify the
  BATCH-022 scaffold. BATCH-020 `no_admissible_pin` is retained.

## 7. QM-MEMORY-MAP status transition

`composition_aggregation_schema_partial`
→ `numeric_composition_operator_protocol_toy_partial`

The new status name carries `protocol_toy` on its face precisely so it can never
be read as clearance. It records only that a numeric composition operator and a
peak-byte number now exist under an explicit, checkable, toy protocol.
