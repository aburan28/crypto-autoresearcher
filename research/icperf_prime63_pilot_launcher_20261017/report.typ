#set page(width: 210mm, height: 297mm, margin: 17mm)
#set text(font: "New Computer Modern", size: 10pt)
#set heading(numbering: "1.")
= Prime63 pilot launcher engineering record

TASK-20261017-4d8c00 · GOAL-ICPERF-e6b6a4 · 2026-10-17

This document reports engineering observations only. Full-width planted and
archived natural ideals were not solved in this task.

#figure(image("diagram.svg", width: 100%), caption: [Preparation, independent replay, and bounded controls. The 21 natural systems are a future schedule.])

== Frozen inputs and checks

Six deterministic planted public inputs cover m=2 and m=8 for coset, random,
and small_x, each with the original 475-point base. Signed selections and
rejection streams are checker-only. Independent Sage replay passed all 6/6
full-point sums and polynomial-zero checks and rejected changed roots.

== Guard and supervisor

The leading-ideal standard-monomial guard stops at 65 before variety
enumeration. Both a 65-distinct-root and a repeated-root multiplicity-65
control returned model_cap_censored before variety. The repeated-root result
is conservative censoring. A 64-standard-monomial control remained under cap.

The future 27-cell schedule applies 300 s per call, 8 GiB sampled process-tree
RSS, 64 primary models, 4 h panel wall, and bounded SSD scratch/free space.
Mocks accounted for 27 attempted / 0 unattempted and, on deliberate first
failure, 1 attempted / 26 unattempted. Latest five tests passed.

An actual small-field worker returned two roots. In the latest pass, measured
wall was 11.982 s; sampled peak tree RSS was 204,324,864 bytes; sampled peak
scratch was 214,700 bytes; minimum SSD free was 540,807,798,784 bytes. A
timeout control was terminated and reaped at 0.618 s.

== Scope

Two failed engineering attempts and their tracebacks remain in the raw test
log. Observed full-width solving degree, natural relation yield, useful rank,
linear algebra, target discrete log, matched rho, and end-to-end delta are
unmeasured. A later experiment requires a source snapshot, a complete frozen
approved plan, positive replay, preapproval and a ready selector.

Exact inputs, commands, host state, and outcomes are bound in
input_manifest.json, command.txt, environment.json, and
engineering_validation.json beside this report.
