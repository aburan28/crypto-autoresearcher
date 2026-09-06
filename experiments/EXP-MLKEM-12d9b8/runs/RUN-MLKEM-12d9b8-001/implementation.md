# Implementation note: RUN-MLKEM-12d9b8-001

## What this run computes

Exact closed-form integer/rational arithmetic only, in `compute.py`
(Python 3.11 standard library, `fractions.Fraction` for exact rationals, no
floating point in any reported number). No ML-KEM implementation, no lattice
software, no quantum simulation, no attack of any kind was written or run.
Four stages, exactly as specification.yaml defines them and as amended by
`experiments/EXP-MLKEM-12d9b8/amendments/v1.yaml` (MLKEM-CHG-1/2/3):

1. Baseline-embedding control (variance formula at m=1, m=2).
2. Q table (exact integers, all three levels x all four swept c values).
3. Combinatorial ceiling, extreme-B check capped at B=q=3329 per MLKEM-CHG-2
   (no search beyond q was performed).
4. Realizability verdict on the combinatorial-ceiling axis, per level per c.

Stage 0 (noise-variance-to-faulty-rate conversion chain) was genuinely
attempted by re-reading all four sources specification.yaml names as
currently available (see `stage0-disposition.md` for exactly what was
checked and why it was insufficient) and disposed as
"NOT COMPUTED: conversion chain unavailable from available sources",
per the contract's own gating_rule -- not silently assumed in either
direction.

## Protocol deviations

1. **No `/usr/bin/time` on this host.** The contract's required_artifacts
   item 9 asks for "resource measurements ... per AGENTS.md's Artifact
   policy". `/usr/bin/time -v` is unavailable on this execution host
   (`ls /usr/bin/time` -> No such file or directory). Substituted Python's
   standard-library `resource.getrusage(RUSAGE_CHILDREN)` inside
   `run_wrapper.py`, which reports wall-clock (via `time.time()`
   before/after `subprocess.run`), user/system CPU seconds, and peak RSS
   (`ru_maxrss`, kilobytes on Linux) for the child process running
   `compute.py`. This is a like-for-like substitute (same underlying kernel
   accounting) recorded here as a deviation per this task's own standing
   instruction to report every deviation honestly rather than silently
   substitute. See `resource_usage.json` for the actual numbers: wall
   0.0247s, user CPU 0.0162s, system CPU 0.0081s, peak RSS 10976 KB -- all
   far inside the 1800s / 2GB budget ceiling.
2. **No other deviations.** All stage definitions, formulas, the c sweep
   {12,13,15,20}, the B grid {1, q=3329} (per MLKEM-CHG-2's operative
   ceiling), and every control specification.yaml names were implemented
   exactly as written, with the amendment's three changes (MLKEM-CHG-1/2/3)
   applied as superseding the corresponding frozen-specification text per
   the amendment's own `old_text_superseded_verbatim` / `new_text` pairs.

## Anomalies / unexpected observations

None. Every arithmetic check (BASELINE-EMBEDDING, TRIVIAL-FLOOR,
FALSIFYING/combinatorial-ceiling comparison, SENSITIVITY across the c sweep,
SYMBOL-COLLISION) resolved cleanly and matches the amendment's own disclosed
order-of-magnitude figure (independently reproduced here: at ML-KEM-1024,
c=12, B=q=3329, `combinatorial_ceiling = 1966237884282961` -- matching the
amendment's "~2x10^15" figure -- against `Q = 5444517870735015415413993718908291383296`,
a shortfall of 24 orders of magnitude by digit count, consistent with the
amendment's disclosed "roughly 20 orders of magnitude" at the same level and
c, computed independently and by different code than the amendment's own
red-team arithmetic).

## Claim ceiling discipline

This run's outputs are reported strictly within
specification.yaml `claim_ceiling.exact_scope_a_run_could_support`: exact
Q values, the variance formula and its baseline checks, the exact
combinatorial ceiling, and the reported "NOT COMPUTED" disposition for the
faulty-rate axis. No claim is made about Simon 2026's correctness, about an
ML-KEM attack, speedup, or security-margin revision, and no hypothesis or
goal status is changed by this run (both remain the Coordinator's authority
alone, per AGENTS.md rule 1).
