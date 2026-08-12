# INC-20260724-EXFAT-01 — checkpoint destruction incident, EXP-DREG-004

**What happened:** between 2026-07-24T23:34Z and 23:47Z, on the exFAT data volume
(`/dev/disk4s1 on /Volumes/Volume`, fskit mount), the entire EXP-DREG-004 artifact
tree was progressively destroyed while the executor session was active: all 33 run
receipt dirs, every top-level file (specification, analysis, summaries, probes), the
ledger entries EV-DREG-004 and EV-SIG-007, then `state.json`, then all 45 carry pkls
(1.38 GB), then a 1.49 GB emergency tar made in response. EXP-SIG-007 was pruned in
the same window. Older experiment dirs (e.g. EXP-DREG-001) survived. From ~23:47Z
directory reads began **flapping** (entries disappearing and reappearing), and
`state.json` was rescued during a visible window at 23:48:10Z. Root cause
undetermined: external deletion process or corrupt exFAT metadata. **Host
quarantine/diagnosis of the volume is required before any further measurement work.**

**Lost (asset):** the resumable checkpoint at 194,000/778,394 cols (24.93%) — ~2,545 s
instrument phase-work and ~9,700 s cumulative wall across 33 invocations / 5 sessions.
**Not lost:** no rank/deficit was ever claimed (none existed); the lineage record is
rescued and verified; the cell rebuilds deterministically (0.45 s + 39.6 s).

**Rescued lineage:** `STATE-RESCUE.json` (sha256
`436b7121ae2c0403236fe7694090c178c444621b5e03dadaf5e72ade3a1f497f`, rescue-copy md5
`755683c7292b9cb851ba88e572f842aa`; copies: this dir + `runtime/` +
`checkpoint-rescue-2.tar`). Verified content: next_col 194,000; rank_acc 188,122;
33 units; 45 carries listed with per-file sha256 (payloads destroyed);
sum(npiv) = 188,122 == rank_acc; secs_total 2,544.7; nrows 279,048; ncols 778,394;
pred 268,674; system_hash `0da7ff6aa40007e8834286005bf6f4e14054734de7939f8e0e161a385c5ebf10`
— independently recomputed from `build_system(21,3,0,2026)` + `monosets_hash`, exact match.

## Transcribed unit trajectory (all 33 units; timings units 1–32 from session logs, unit-33 timing from rescued state: secs_total 2544.7 − 2498.4 = 46.3 s)

| unit | cols | k | rank_acc | k/c | fill/red/ech/post (s) |
|---|---|---|---|---|---|
| 1 | 0–8,000 | 8,000 | 8,000 | 1.000 | 0.1/0.0/5.6/31.1 |
| 2 | 8,000–18,000 | 10,000 | 18,000 | 1.000 | 0.1/5.7/14.5/42.0 |
| 3 | 18,000–28,000 | 10,000 | 28,000 | 1.000 | 0.1/13.3/15.6/43.5 |
| 4 | 28,000–38,000 | 10,000 | 38,000 | 1.000 | 0.1/20.6/16.1/44.6 |
| 5 | 38,000–48,000 | 10,000 | 48,000 | 1.000 | 0.1/28.3/11.0/45.7 |
| 6 | 48,000–58,000 | 10,000 | 58,000 | 1.000 | 0.1/35.9/12.2/44.3 |
| 7 | 58,000–68,000 | 10,000 | 68,000 | 1.000 | 0.1/45.3/13.6/47.7 |
| 8 | 68,000–78,000 | 9,864 | 77,864 | 0.986 | 0.1/56.6/13.4/51.1 |
| 9 | 78,000–88,000 | 9,751 | 87,615 | 0.975 | 0.1/60.2/12.7/43.8 |
| 10 | 88,000–96,000 | 7,684 | 95,299 | 0.961 | 0.1/57.5/5.8/31.1 |
| 11 | 96,000–104,000 | 7,769 | 103,068 | 0.971 | 0.1/62.9/5.5/32.1 |
| 12 | 104,000–112,000 | 7,797 | 110,865 | 0.975 | 0.1/69.0/5.4/32.2 |
| 13 | 112,000–118,000 | 5,993 | 116,858 | 0.999 | 0.1/61.8/4.4/25.2 |
| 14 | 118,000–124,000 | 6,000 | 122,858 | 1.000 | 0.1/65.2/4.9/27.5 |
| 15 | 124,000–130,000 | 6,000 | 128,858 | 1.000 | 0.1/65.8/4.7/25.3 |
| 16 | 130,000–136,000 | 6,000 | 134,858 | 1.000 | 0.1/69.2/4.7/24.2 |
| 17 | 136,000–142,000 | 6,000 | 140,858 | 1.000 | 0.1/74.3/4.8/24.8 |
| 18 | 142,000–147,000 | 5,000 | 145,858 | 1.000 | 0.0/57.4/3.7/19.4 |
| 19 | 147,000–151,000 | 4,000 | 149,858 | 1.000 | 0.0/49.0/2.7/16.5 |
| 20 | 151,000–155,000 | 4,000 | 153,858 | 1.000 | 0.0/50.1/1.5/15.4 |
| 21 | 155,000–159,000 | 3,868 | 157,726 | 0.967 | 0.0/51.6/2.4/15.2 |
| 22 | 159,000–163,000 | 3,898 | 161,624 | 0.975 | 0.0/52.6/1.4/15.5 |
| 23 | 163,000–167,000 | 4,000 | 165,624 | 1.000 | 0.0/53.3/2.6/15.4 |
| 24 | 167,000–171,000 | 3,805 | 169,429 | 0.951 | 0.0/55.9/1.5/15.3 |
| 25 | 171,000–174,000 | 2,981 | 172,410 | 0.994 | 0.0/45.9/1.1/12.1 |
| 26 | 174,000–177,000 | 2,455 | 174,865 | 0.818 | 0.0/46.6/0.9/9.3 |
| 27 | 177,000–180,000 | 3,000 | 177,865 | 1.000 | 0.0/47.2/0.9/11.6 |
| 28 | 180,000–183,000 | 2,195 | 180,060 | 0.732 | 0.0/47.3/0.5/7.8 |
| 29 | 183,000–186,000 | 2,503 | 182,563 | 0.834 | 0.0/50.1/0.7/9.5 |
| 30 | 186,000–188,000 | 1,554 | 184,117 | 0.777 | 0.0/38.7/0.5/5.6 |
| 31 | 188,000–190,000 | 1,567 | 185,684 | 0.784 | 0.0/38.6/0.6/6.3 |
| 32 | 190,000–192,000 | 890 | 186,574 | 0.445 | 0.0/39.9/0.5/3.3 |
| 33 | 192,000–194,000 | 1,548 | 188,122 | 0.774 | (receipt lost; phases 46.3 s total) |

**Dependent-fraction answer to the turn-5 telemetry question:** the 44.5% at cols
190k–192k did **not** keep deepening — unit 33 (192k–194k) bounced to 77.4%. The
profile oscillates (full-pivot plateaus alternating with 73–98% and one 44.5% dip);
the n=18 late-column deficit zone (k/c ~ 0.001) was never entered by column 194k.

## Carrier-codec cost assessment (requested; measured 23:28–33Z, 44 blocks)

| component | measured |
|---|---|
| carry sha256 verify (all blocks) | 11.2 s |
| **carry unpickle (sage m4ri PNG pickle)** | **198.6 s (4.51 s/block, linear growth)** |
| pickle dump (save side, 3-block sample scaled) | ~5.3 s/block |
| adjacency cache load | 0.2 s |
| sage/python startup | ~15–20 s |
| save + state + gc + exit | ~15–20 s |
| raw-bit load estimate (6.51 GB at ~1.5 GB/s) | ~4–5 s |

Per-invocation wall 260–300 s = ~70% carrier unpickle+verify. A verification-gated
raw-bit carrier store (raw bytes + sha256 gate) cuts load/verify ~210 s → ~15 s:
invocation ≈ phases + ~40 s, chunk 8,000–16,000 fits the 300 s cap, ~9–10 chunks/turn
at ~10k cols ⇒ ~6–7 turns for the remaining ~584k cols instead of 35–45.
**Recovery: ~28–38 turns.** Matches the SIG-007 executor's independent estimate (~7
turns; same instrument family, unpickle 4.3 s/block at 33 blocks vs 4.51 s/block here).
Report-only: not implemented (src/ hash-pinned, outside executor write scope).

## Restart guide (healthy volume required)

Frozen cell rebuilds deterministically: `build_system(21,3,0,2026)` 0.45 s, adjacency
build 39.6 s; **system_hash must equal
`0da7ff6aa40007e8834286005bf6f4e14054734de7939f8e0e161a385c5ebf10`** and
`pred` must be 268,674 — built-in identity checks for any rebuild. Command pattern of
record: `sage -python src/h012c_block_m4ri.py --n-list 21 --t 3 --targets 1 --d 5
--seed 2026 --tag measure_n21_sem_a --budget 230 --max-units 1 --chunk-force
<cap-dependent> --which sem --results-dir <run>/work` from the repo root. Cost:
~3.5–4.5 h in one long session (chunk 24,000); ~35–45 turns at the 300 s cap;
~6–7 turns with the codec fix.
