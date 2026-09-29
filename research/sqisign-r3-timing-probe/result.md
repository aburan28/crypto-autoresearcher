# SQIsign p324_3 signing timing: initial observation

**Status:** exploratory single-machine result, not an attack or a ledger
transition. Protocol frozen in local commit
3ca6016cc46ea35d2ac34b481dc5ed05c65792f6 before measurements;
the attached metadata records that commit and the protocol hash. The
GitHub branch was published after the run. Run 2026-09-27
01:06:49–01:07:30 UTC. Target
SQISign/the-sqisign commit
f417ebd4c2c336ad6a9feb6f9255f95fc03acc41, reference Release build,
p324_3, Ubuntu x86_64, GCC 13.3.0. The upstream KAT passed.

## Why this path

The Round 3 [SQIsign specification, version 3.0](https://sqisign.org/spec/sqisign-20260901.pdf),
§8.5 and introduction, identifies non-constant-time signing as an
implementation limitation. **Provenance: retrieved primary submission
2026-09-27.** In the inspected source at the pinned commit, signing calls
dim2id2iso_ideal_to_isogeny_qlapoty on ideal_skchall_aux
(src/signature/ref/lvlx/sign.c:327); that calls quat_qlapoty
(src/id2iso/ref/lvlx/dim2id2iso.c:35), whose norm-equation routine calls
quat_qlapoty_loop_two. The loop increments lambda until it finds a
solution. The ideal is secret-derived. **Provenance: retrieved upstream source
at the pinned commit, inspected 2026-09-27.**

This probes a concrete implementation surface in GOAL-SQISIGN-001. It does
not change the published endomorphism-ring hardness estimate or the
GOAL-SSI-001 mathematical attack analysis. The separate, published
supersingular-isogeny attack and its time/memory tradeoff are discussed in
§8.2 of the same specification; this run did not implement that attack.

## Prespecified results

All 256 signatures verified in each build; all 256 signed-message checksums
matched across the pristine and instrumented replay. The library's level-I
known-answer test passed. Raw observations and machine-readable analysis are
under [results](results/).

| Metric | Observation |
| --- | ---: |
| Pristine signing time, median (min–max) | 43.25 ms (37.82–87.88) |
| Loop-two iterations, median (min–max) | 410.5 (19–2,935) |
| Distinct loop counts in 256 signatures | 226 |
| Loop count vs instrumented signing time, Spearman | 0.420 |
| First vs second half per-key timing medians, Spearman | −0.690 |
| Fixed one-sided label permutation test, plus-one p | 0.9722 |

The local counter confirms variation in this secret-derived path and its
descriptive association with instrumented timing. The prespecified
repeated-key timing statistic **did not support distinguishing these eight
keys** in this 32-message sample. A large one-sided p-value is not proof of
constant-time behavior or of side-channel safety. This study tested neither
key recovery nor forgery.

## Exploratory follow-up after seeing the fixed result

Because instrumentation can perturb timing, posthoc.py pairs the two runs
by the exact deterministic signature checksum. Loop count versus **pristine**
signing time has Spearman 0.383; pristine versus instrumented signing time
has Spearman 0.742. The instrumented median is 42.46 ms. This was not in the
frozen analysis and carries **no significance claim**. It suggests the loop
variation is visible to some extent in local end-to-end timing, but the
association may include other deterministic work correlated with this loop.
The same deterministic test RNG sequence, CPU load, and 256-sample selection
limit generalization.

## What to investigate next

1. Replicate count-to-time prediction with fresh keys, independent RNG
   seeds, interleaved runs, and independent hosts, with a new frozen
   analysis and a null control. Estimate whether one can predict coarse
   counts from *unmodified* timings on held-out signatures, rather than
   inferring secret-key leakage from correlation alone.
2. Determine mathematically whether the measured Qlapoti iteration count
   constrains the static secret ideal after conditioning on the public
   message, challenge, and per-signature randomness. Specify an explicit
   recovery algorithm and its sample/time complexity before describing any
   result as key recovery.
3. Pursue the distinct GOAL-SSI-001 Frobenius/endomorphism-ring path under
   the Round 3 memory bound. Its cost model and this implementation
   measurement answer different questions.

No off-target system, production deployment, or third-party key was measured.
The code, frozen protocol, local-only instrumentation patch, exact raw CSVs,
command logs, seed, versions, timestamps and hashes are included. Run with
SQISIGN_UPSTREAM_DIR=/path/to/clean/f417ebd/checkout and a CMake-enabled PATH
followed by bash reproduce.sh. The script appends a laboratory target and
patches the upstream checkout after the pristine measurement, so use a
disposable checkout.
