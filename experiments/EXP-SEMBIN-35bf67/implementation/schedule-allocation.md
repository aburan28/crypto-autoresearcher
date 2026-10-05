# Session-level allocation (executor scheduling; OP-CAPS / OP-ORDER)

Written 2026-10-05 ~06:50Z, after Stage 0 freeze and during the Stage-1 engine gate, BEFORE
any Stage-1 smoke or Stage-2/3 outcome existed. Based only on development timing
(implementation/dev-log.md D13-D16 and the exhaustive-search probe below). Its purpose is
to fix, in advance, how the handoff's 86,400 s session budget (advisory) is split, so that
sample sizes do not depend on observed outcomes. Frozen sample targets stay at their
specification values; counts not reached are recorded as shortfall, never invented.

Timing basis (development, this host: 4 vCPU Xeon 2.8 GHz, 15 GiB):
- SOLV4 per arm: (30,2,2,15) ~7-12 s; (40,2,2,20) ~330-400 s (one instance).
  Extrapolated (cost ~ M_le4^3): (40,2,2,21) ~11 min, (21,3,3,7) ~15-18 min,
  (40,2,2,22) ~20 min, (45,2,2,23) ~35 min, (50,2,2,25) ~1.5-3 h, (25,3,3,9) ~3-5 h,
  (25,3,3,10) ~6-10 h per arm-process (near or above the 8 CPU-h per-process cap).
- Exhaustive null s (exhaust.c): 2.8 ns per candidate (dev probe: N=34 quadratic 47 s;
  cubic 2^32 slice 12 s). N=40 quadratic ~3,000 CPU-s (~13 min on 4 processes);
  N=42 cubic ~12,300 CPU-s (~3.4 CPU-h) per null instance.

Allocation (wall hours on this host; two instances x two arms run concurrently):

| order | cell | arms | allocation | expected reach (not a target) |
|---|---|---|---|---|
| S1 | (40,2,2,20) smoke | primary | until 8 SAT + 8 UNSAT | complete |
| 1 | (30,2,2,15) | primary + null | 1.0 h (85% primary) | 100/100 primary, up to 100 null |
| 2 | (40,2,2,20) | primary + null | 6.5 h (55% primary, 45% null) | ~35/35 primary, ~9-10 null |
| 3 | (21,3,3,7) | primary | 2.0 h | ~8/8 primary; null NOT run (3.4 CPU-h per null instance) -> null shortfall 100 |
| 4 | (45,2,2,23) | primary | 3.5 h | ~6/6 primary; null O-CENSORED by OP-NULL (N = 46 > 42) |
| 5 | (25,3,3,9) | - | 0 h | not executed: per-arm cost ~3-5 h; shortfall |
| 6 | (50,2,2,25) | - | 0 h | not executed: per-arm cost ~1.5-3 h; shortfall |
| 7 | (40,2,2,21) | primary | 2.0 h | ~10/10 |
| 8 | (40,2,2,22) | primary | 2.5 h | ~7/7 |
| 9 | (25,3,3,10) | - | 0 h | not executed: per-arm cost near/above the 8 CPU-h cap; shortfall |

If wall time remains after item 8, cells 6 then 5 receive one SAT and one UNSAT instance
each, in that order, and the extra allocation is recorded in their run manifests.
Nothing in this table is revised in response to any observed SOLV4 outcome.
