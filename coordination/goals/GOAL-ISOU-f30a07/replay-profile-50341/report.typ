#set page(paper:"a4", margin:20mm)
#set text(size:11pt)
= Same-map replay profiling
GOAL-ISOU-f30a07 / TASK-20261016-659e0a / archive TASK-20261016-b08ee1
#image("flow.svg", width:100%)
== Observed baseline
RUN-ISOU-f9546d constructed one partial-eigenline map in131134ms,7656861bytes. Independent replay reached its3600019ms watchdog with sampled peak153567232bytes, score null and CENSORED/TIMEOUT. Exact total CPU was not recorded. This is a right-censored replay duration, not a point runtime or mathematical rejection. Full raw evidence and the original shell INCOMPLETE fallback are preserved in terminal snapshot9e3309ffdb.
== Ranked implementation
Preserve the sealed map and existing acceptance predicates. Parent adds an opt-in absolute fresh JSONL trace with flushed begin/end/error markers, monotonic elapsed time, phase and PID. Stage boundaries cover loading, kernel GCD/torsion, inverse/composition, codomain, denominator equality, numerator-denominator GCD, exact substitution, subgroup order and20 transports. Unfinished stages remain unfinished after watchdog termination.
== Controls and gate
Fixed small valid/adversarial maps must have identical trace-off/on mathematical outcomes. Test existing-file refusal, explicit write failure and durable interruption markers. Keep default no-op observers compatible. Required repository checks and clean installed source/binary hashes precede a later separate scientific protocol. No50341 replay, regeneration, larger construction or M8191 execution is authorized by this implementation task.
== Limits
The internal bottleneck is unknown; current polynomial code already uses Karatsuba/reciprocal reduction and composition blocking. No speedup ratio follows from a censored baseline. A/A pairing and spread are mandatory for later timing claims. Concurrency1,3600s replay and8GiB sampled RSS are planned host-protection bounds for the later /run, not spending limits. No challenge score or canonical claim graph changes. This pipeline diagram is used because completed comparable replay measurements are unavailable.
