# Red Team Objections — RT-20260731-130

**Under review:** RUN-IT-001-bounded-toy (EXP-IT-001, H-IT-001, GOAL-ECDLP-001 BATCH-028)
**Snapshot:** `a4561488d972895b1192cc4d0c99d86edc8a54f3` · **Claim ceiling:** toy
**Session:** independent (task TASK-20260731-130)

The task asked whether anything in this package could be read as a sub-rho
isogeny-transfer speedup, an H-DS-001 support, or a crypto-scale claim. The
short answer: the package's own *labels* are mostly honest
(`observations_only: true`, `no_support_reject_conclusion: true`,
`claim_tier: toy`), but the package's *validity claim* is not, and the
"0.0 everywhere" table is uninterpretable rather than null. The strongest
falsification routes are below, strongest first.

---

## 1. The run crashed and was archived as `completed_valid` (BLOCKING)

`stderr.log` (which the snapshot omits) shows the process died at
2026-07-31T23:17:32Z with a traceback —

```
TypeError: Object of type Integer is not JSON serializable
when serializing dict item 'version'
...
EXIT:1
```

— while dumping `heur_report` to `HEUR_ISO_1_report.json`. The archived
`HEUR_ISO_1_report.json` is exactly the 153-byte partial write of that dump:
it ends mid-value at `"version": ` and is not valid JSON. Yet
`manifest.json` and the execution report record `protocol_deviations: []`,
no crash anomaly, and `validity_status: completed_valid`. The rest of the
package (raw-result, manifest, summary, transfer/concrete/null reports) has
mtime 23:13:16Z; the HEUR file and stderr have mtime 23:17:32Z — the archived
set is a completed invocation's artifacts mixed with a second, crashed
invocation's corrupt file, with no annotation. Under AGENTS rule 5 and the
experiment state machine, this is `failed_infrastructure`, not
`completed_valid`. This single fact outranks every interpretation question:
**the archived record does not describe what actually ran.**

**Falsification route:** re-run `run_bounded_toy.py` on a clean tree at the
snapshot content; observe the same exit-1 crash; show the manifest would again
claim `completed_valid`. The bug is a Sage-`Integer` leaking into
`json.dump(heur_report)` — the serialization is a property of the code, not
of any mathematical signal.

## 2. Both controls void ⇒ the zeros are censorship, not "no signal" (BLOCKING)

- `planted_path_recovered=false` — the positive control never recovered a
  planted isogeny walk (`path_edges: []`, `n_hops_planted: 0`).
- `plant_detected=false` — the null-plant control never fired.
- All 21 unplanted cells are `mode=censorship_lower_bound` with
  `H_min=null`, `R_xfer=0.0`, `C_path` measured **0** — the BFS explored
  zero edges on every cell.

The manifest itself declares the consequence: *"harness void for sub-rho
claims per contract."* A harness that cannot find a transfer when one is
planted in it cannot detect the absence of transfers elsewhere. Every 0.0 is
a placeholder for "the search returned nothing," not a measurement of the
transfer ratio. Any sentence of the form "no curve showed a sub-rho
transfer," "rate of cheap transfers was 0/21," or "rho_special = 0 at toy
scale" drawn from this run overclaims.

Note the asymmetry: 20/24-bit `rho_special=0` come from exhaustive universe
scans (`scanned_j = p`) and are real observations about *those universes*;
the 28-bit `rho_special=0` is a sample estimate (847,433 of 536,870,923
j-invariants, ≈0.16%) with no confidence bounds and must not be quoted as a
density.

**Falsification route (cheapest):** fix nothing in the math — just make the
BFS neighbor enumeration actually enumerate. The fact that every cell,
planted and unplanted, yields `C_search=0` means the search instrument never
executed a single edge expansion in this run. A one-line fix that lets one
2-isogeny edge be explored will change the entire table from all-zero to
nonzero, demonstrating the table was an artifact of a dead code path.

## 3. `rate_iso_1` is a gate-hold computed over censored rows (HIGH — laundering risk)

The executed code computes

```
completed = [r for r in transfer_rows if r["R_xfer"] is not None]
ge1 = [r for r in completed if r["R_xfer"] >= 1.0]
rate_frac = len(ge1)/len(completed)   # 0/21 = 0.0
rate_pass = rate_frac >= 0.90         # False
```

Every one of the 21 rows carries `R_xfer = 0.0` — the *censored lower bound*,
which is trivially 0 because `C_search=0` — so "fraction ≥ 1" is vacuously
0.0. The driver's own comment says it: *"RATE under heavy censorship is a
gate-hold observation, not HEUR confirmation."* The frozen pre-search report
(`HEUR_ISO_1_report.freeze.json`, not archived) honestly holds
`rate_iso_1_pass: null`; `summary.json` ships `false` / `0.0` without the
caveat. KS/TAIL are null (zero uncensored samples < 20), so HEUR-ISO-1 was
never adjudicated in either direction.

**Laundering route to block:** an aggregator that keys on
`rate_iso_1_pass` / `rate_iso_1_fraction_R_ge_1` to conclude "HEUR-ISO-1
unsupported" — or, worse, feeds a negative into H-DS-001-style (S1_met)
scoring — would be reading a machine-censorship artifact as empirical
negative evidence. The summary's `no_support_reject_conclusion: true` and
`observations_only: true` are correct and must be enforced as a ceiling, not
treated as a formality.

## 4. The positive control failed because the `C_special` model is inverted (HIGH)

The planted control's endpoint is anomalous (`trace ≡ 1`, Smart attack
applies). Its transfer account: `H_min=0` (the endpoint is already special,
0 hops), `C_path=0` measured, `C_pullback=20` modeled, `C_special=7856`
modeled ⇒ `R_xfer = 9.24 ≥ 1` ⇒ control fails. The true cost to solve ECDLP
on an anomalous curve is O(log p) ≈ 20 group operations. Substitute it:

```
R_xfer ≈ (0 + 20 + 20) / 851.9 ≈ 0.047 < 0.7  →  control PASSES
```

The control's verdict flips under the real cost. The gate outcome is
therefore fully determined by an unvalidated modeled constant that is
wrong-direction for the one family the control actually exercised. Every
`R_xfer` in the package — including the censored cells' lower bounds —
inherits this model dependence. `concrete_cost_table.json` does flag
optimistic assumptions (c_iso=4·ell, MOV 1:1, tree-ball model, min-C_special),
which is honest labeling, but a flagged unvalidated constant is still an
unvalidated constant.

## 5. No per-attempt × inverse-success-probability bookkeeping (HIGH)

Nowhere in `transfer_gate_report.json` or the charging code does a success
probability appear. `R_xfer` is a deterministic modeled ratio. The exemplar
discipline (red-team contract §5; target-result-profile) requires total
expected cost = per-attempt cost × inverse success probability, with the
probability derived under the heuristic — never silently set to 1. Here the
gate does not even set it to 1; it omits the factor entirely. Under 100%
censorship the correct expected transfer cost is unbounded/undefined, and a
packaged 0.0 "lower bound" from `C_search=0` is information-free. The gate
must either add the success-probability factor or declare itself
deterministic-cost-only.

## 6. Null-object control is vacuous (MEDIUM)

The plant (`C_path_reported = floor(C_path_honest/4)`, amendment B-8) was
injected into the designated cell whose honest cost was already 0:
reported 0, recomputed 0, predicate `0 ≤ floor(0/4) ∧ 0 < 0` = false by
construction. `plant_detected=false` is a tautology, not a false-positive-free
certificate, and `plant_detection_eps=0` is hardcoded. The detector was never
handed a nonzero signal.

## 7. Certificate labeling (MEDIUM)

All unplanted cells are correctly `kind: none`, `verified: false` — no claimed
solve without a certificate (task point 4 satisfied). But the planted
control's `certificate_pass: true` is the certificate of a
**self-generated** ECDLP instance (the driver knows `k` and verifies with the
harness recompute). It proves the harness arithmetic, not a transfer, and it
must not be surfaced as transfer evidence anywhere downstream.

## 8. Snapshot integrity (MEDIUM)

Commit `a4561488` adds 9 files. Missing from it: `command.txt`,
`environment.json`, `stdout.log`, `stderr.log`, `console_tee.log` — all
declared in `manifest.artifact_paths` — and the valid
`HEUR_ISO_1_report.freeze.json`. The omitted stderr is the only record of the
exit-1 crash. A run executed on a dirty tree (4,731 dirty entries) whose
snapshot lacks the logs is not reproducible from the archive.

## 9. Minor items (LOW)

- `finished_at` 23:13:16Z / `wall_seconds` 1758.87 contradict the stderr
  timestamps and crash at 23:17:32Z.
- Executor inference: `fallback_used=true`, `model_verified=false`
  (recorded honestly; noted for the record).

## Checks discharged (no objection)

- **Claim tier:** everything is `toy` (≤28-bit fields); affected scope is
  correctly limited to generic ordinary prime-field curves at tested toy
  sizes; no crypto-scale or universal wording found.
- **Baselines:** `matched_rho=0.886√N`, `matched_bsgs=2⌈√N⌉` are standard and
  honestly labeled modeled.
- **Scope:** no H-DS-001 / H-IC-001 / H-STR-002 / EXP-DS-001 content touched;
  nothing here licenses an SG-ECDLP-001 lane-death claim.

---

## Recommended disposition

**`failed_infrastructure`** — the run crashed (exit 1), a declared artifact
is corrupt and invalid JSON, both controls are void, and 21/21 cells are
censored. The experiment state machine and AGENTS rule 5 put this in
`failed_infrastructure`/`invalid`, not `completed_valid`, and not
`inconclusive` (which would leave the zero-table hanging as a potential null
result). The *scientific* question (H-IT-001 sub-rho transfer) remains
untouched: `inconclusive` in the narrowest sense, with H-IT-001 staying
`specified` and no evidence record created.

## Binding constraints for the Coordinator

1. Reclassify `RUN-IT-001-bounded-toy` `validity_status` → `failed_infrastructure`
   via a decision record citing RT-20260731-130.
2. No promotion: this run may not be cited for or against H-IT-001,
   H-DS-001 (S1_met), HEUR-ISO-1 validation, or any sub-rho transfer claim;
   `observations_only`/`no_support_reject_conclusion` are the ceiling.
3. Authorize a scoped rerun (TASK-20260731-127 already flags
   `requires_rerun: true, protocol_complete: false`) gated on:
   - serialization fix (all declared artifacts valid JSON; exit codes recorded
     as deviations);
   - BFS that explores nonzero edges (`C_search > 0` on at least some cells);
   - positive control that recovers the planted path (`H_min ≥ 1`,
     non-empty `path_edges`, endpoint ≠ start) before any sub-rho reading;
   - `C_special` calibrated against true Smart/MOV cost (anomalous control
     passes at ~O(log p));
   - null-plant injected into a cell with nonzero honest cost;
   - per-attempt × inverse-success-probability term in the transfer
     accounting, or an explicit deterministic-only declaration.
4. Rerun snapshot must include stderr/stdout/console tee, command.txt,
   environment.json, and the freeze file; a corrupt artifact blocks promotion.
5. Claim ceiling stays `toy`; no SG-ECDLP-001 lane-death claim; no edits to
   H-DS-001 / H-IC-001 / H-STR-002 / EXP-DS-001.

**Narrowest supported statement:** the run measured nothing about
isogeny-transfer cost; it exercised a search instrument that never found a
path, controls that never fired, and a serializer that crashed. It supports
no claim, positive or negative, about sub-rho transfers, HEUR-ISO-1, or any
ECDLP improvement.
