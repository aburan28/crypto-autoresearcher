# Validation notes — TASK-20260731-010 / EV-MLKEM-011 + EV-MLKEM-012

Independent of the Executor. Report id **VAL-20260731-002**. Package: heuristic-coverage + sensitivity. No official state changed. No git commit performed.

## Inference

- `requested_policy`: review-xhigh
- `resolved_model_id`: cursor-grok-4.5 (`fallback_used: true`)
- `independent_session`: true

## EXP-MLKEM-011 recomputation (archived left panel)

From vendor-lock `Pwrong_*N25971.out` / `Pgood_*N25971.out` (headers claim same score `F`; matching q/m/n/fft/β/N):

| quantity | recomputed | recorded |
|---|---:|---:|
| Pwrong last-positive T | 1802 | 1802 |
| log2(Pwrong) at floor | −35.70445229335197 | −35.70445229335197 |
| Pgood n / min / median / max | 4000 / 6667.67 / 11964.47 / 17822.81 | same |
| fraction Pgood inside Pwrong T-range | **0** | 0 |
| Kyber-512 floor gap (bits) | −83.8655 (~84) | −83.8655 |

H-MLKEM-011 predictions hold; falsification conditions do not fire.

## EXP-MLKEM-012 recomputation (Case A from CC intermediates)

`cost(Δ)=log2(2^Tsample + 2^(second_term+Δ))`; crossover Δ to NIST 143/207/272:

| set | second_term | Tsample | recomputed Δ | JSON Δ |
|---|---:|---:|---:|---:|
| Kyber-512 | 133.41 | 139.51 | 9.4555 | 9.46 |
| Kyber-768 | 192.64 | 194.81 | 14.3597 | 14.36 |
| Kyber-1024 | 257.24 | 259.35 | 14.7598 | 14.76 |

All < 15. Pickle CC second terms from EXP-MLKEM-010 agree (133.413 / 192.637 / 257.242). H-MLKEM-012 holds under HEUR-S1.

**Prose drift (qualification):** EV-012 / RUN-012 headline / DEC-004 say ~9.6/14.9/14.6; KN-FIND-013 (~9.5/14.4/14.8) matches JSON. Machine-readable fields are authoritative.

## Scope

- No ML-KEM / FIPS-203 break claim in EV, DEC, or KN-FIND.
- HEUR-S1 marked conditional (hypothesis, evidence, finding, DEC non-claims).
- Archived-data analysis vs missing G6K disclosed on RUN-011.

## Score-scale objection

Pwrong header: `P(F ≥ i)`; Pgood header: `F(solution)`; shared Fig 4.1 left-panel stem. Residual commensurability risk flagged — **not** an auto-reject given same-`F` file claims.

## Verdict

| Field | Value |
|-------|--------|
| verdict | **accept_with_qualifications** |
| blocks_ledger_record | **false** |
| id | VAL-20260731-002 |
