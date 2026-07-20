# EXP-SIG-005 analysis — cascade-law falsifiable checks + residual_5 n-growth

Thread: **SIG asymptotics + DREG audit (2026-07-20)**. Numbers-only observation;
the status decision is in `ledger/DEC-20260720-001.yaml` (H-SIG-001) and
`ledger/DEC-20260720-002.yaml` (H-DREG-001). Evidence record: `ledger/EV-SIG-005.yaml`.

## P1 — the 2n/3+1 D4-residual law at n=24 (CONFIRMED)

On n=24 sem seeds 1,2,3 (`RUN-EXP-SIG-005-b`), zero within-size variance:

| quantity | prediction | measured |
|---|---|---|
| D3 non-Koszul count | 1 | 1 |
| D4 deficit | 8n/3 = 64 | 64 |
| D4 residual (pinned) | 2n/3+1 = 17 | 17 |
| D4 residual (canonical) | 17 | 17 (delta 0) |
| union cross-check rank | — | 47 == canonical |

Null arm (`RUN-c`) all-zero on all 3 seeds; determinism repeat (`RUN-d`) and
formal compare (`RUN-e`) identical modulo timing; gate (`RUN-a`) PASS. The
canonical D4 residual series is now `9/11/13/15/17` at `n=12/15/18/21/24` —
exactly `2n/3+1` across **six on-lattice sizes**. **Growth in n is linear.**

## residual_5 (D5-born component) — extended to n=18, found NON-MONOTONE

`residual_5 = extra_5 − A4_5` (D5-born non-rewritable dimensions after removing
the multiplication closure of the D3+D4 non-model syzygies):

| n | residual_5 | source |
|---|---|---|
| 9  | 344  | RUN-h (anomalous size) |
| 12 | 878  | RUN-h path / EV-SIG-003 |
| 15 | 1158 | EV-SIG-003 |
| 18 | **974** | RUN-j (seed 1) **and** RUN-m (seed 2) — **replicated, zero variance** |

Increments `+534 / +280 / −184`: the D5-born component rises through n=15 and
**drops at n=18**. It does **not** grow monotonically in n. Every cell is
null-validated (D5 null `extra=0`, `rank==sr_pred`).

Cross-instrument: the SIG D5 Macaulay deficit equals the independent EXP-DREG-001
block-m4ri deficit at every shared n — `1321/1322` (n=12), `1862` (n=15), `1999`
(n=18). On-lattice D5 deficit `909/1322/1862/1999` (n=9/12/15/18), increments
`+413/+540/+137` — monotone increasing, **sharply decelerating at n=18**.

## P2 — the D=6 birth law is INVALID (null control fails)

The support-matched null is exactly semi-regular through D3/D4/D5 (`extra=0`,
`rank==sr_pred`) but **breaks at D6** (`RUN-k`, n=9 null):

| | ncols | rank | sr_pred | deficit | extra | residual_6 |
|---|---|---|---|---|---|---|
| sem D6 (RUN-h) | 29332 | 27292 | 28068 | 776 | 8897 | 2615 |
| **null D6 (RUN-k)** | **31180** | **31179** | 28068 | **−3111** | **4986** | **4986** |

The two arms have **different column counts** (31180 vs 29332 — not comparable),
the null nearly saturates its own columns, and the shared `sr_pred=28068` matches
**neither** arm. `c5_null_zero_d6_extra_and_rank=False`,
`c5_null_residual6_zero=False`. Per the pre-registered C5 invalidation rule the
**entire D6 stage is invalid** — the sem `residual_6=2615` and `deficit_6=776`
are inadmissible. This is the "miscalibrated D6 null" pre-excluded in the
H-DREG-001 assumptions, now directly demonstrated. **The cascade characterization
is trustworthy only for D ≤ 5.**

## Infrastructure censoring (AGENTS rule 5 — not evidence)

- `RUN-o` (n=21 residual_5): the host **root disk reached 100% (ENOSPC)** during
  the n=21 D5 stage; the run directory was never created.
- `RUN-l` (n=12 null): D3/D4/D5 completed clean (`extra=0`); the D6 count was
  killed by the same ENOSPC before flushing — the n=12 D6-null replication is
  missing.
- `RUN-i` (n=12 sem residual_6): deliberately killed once `RUN-k` proved the D6
  stage invalid; retained as telemetry.
- `RUN-f`/`RUN-g` (prior-session n=12 D6): killed mid-D6; invalid.

Disk pressure originates from unrelated host data (`/private/tmp/ecdsafail-*`),
not this experiment. Recommend relocating Sage `TMPDIR` to the data volume before
the next heavy batch.

## What this establishes

At **D ≤ 5** (where the null is validly semi-regular) the cascade is real and its
n-growth is **weak and non-accelerating**: linear at D4 (confirmed to n=24),
non-monotone at D5 (drops at n=18). At **D = 6** the instrument cannot currently
measure the cascade (broken null baseline). The result therefore **sharpens**
H-SIG-001 for D ≤ 5 while **retracting** the D6 birth-law claim, and feeds
H-DREG-001 the finding that the one still-open (degree-axis) route is **not
validly measurable** until the D6 baseline is repaired.
