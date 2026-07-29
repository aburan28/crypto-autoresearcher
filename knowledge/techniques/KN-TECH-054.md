---
id: KN-TECH-054
remapped_from: KN-TECH-030
remapping_note: >-
  Canonical copy of the frozen ML-KEM record after its ID collided with an
  independently archived canonical record on main. Body unchanged apart from
  remap metadata and cross-references retargeted to the remapped IDs (see
  CORR-20260724-004).
type: technique
title: Outcome-precedence design for differential-conformance protocols requires a baseline-invisible positive control
tags: [experiment-design, differential-testing, conformance-testing, outcome-classification, positive-control, generator-adequacy, falsifiability, methodology, ml-kem, defensive]
confidence: reported
complexity: not applicable; this is a protocol-design constraint, not an algorithm
applicability: >-
  Any frozen experimental protocol that (a) ranks a "the added instrument
  contributed nothing" outcome above the substantive conclusion it is trying to
  reach, and (b) measures instrument adequacy by the marginal findings of the
  added classes over a baseline class.
source_refs: []
internal_refs: [EV-MLKEM-006, DEC-20260724-019, EXP-MLKEM-003, H-MLKEM-003, EV-MLKEM-005]
proof_status: empirical_only
proof_refs:
  - experiments/EXP-MLKEM-003/specification.yaml
  - experiments/EXP-MLKEM-003/runs/RUN-MLKEM-012/raw.json
  - coordination/goals/GOAL-MLKEM-001/batches/BATCH-006/tasks/TASK-20260724-237/validation_report.yaml
  - coordination/goals/GOAL-MLKEM-001/batches/BATCH-006/tasks/TASK-20260724-238/red_team_report.yaml
added: 2026-07-24
superseded_by: null
---

## The constraint

A differential-conformance protocol that widens its generator — adding
multi-byte, alignment, or length classes on top of a baseline single-byte class
— usually wants two guarantees at once:

1. An honesty guarantee: if the widened classes discover nothing the baseline
   did not, say so, and do not let the wider generator lend false weight to a
   null result.
2. A substantive conclusion: under the widened generator, the defect class is
   absent outside the known instances.

The natural way to encode the first is an outcome class along the lines of
`generator_hardening_insufficient`, defined as *the added classes produce no
finding the baseline did not already produce, on any target including the
positive control*, ranked ABOVE the substantive conclusion in the precedence
list so it cannot be skipped.

That encoding is self-defeating unless the positive control contains a defect
component that the baseline class cannot see.

## Why

Enumerate where a marginal finding could come from once the ranking is fixed:

- On a **clean target**, a marginal finding from a widened class is a newly
  discovered defect, which triggers the *systemic* outcome class — ranked even
  higher. So it cannot deliver the substantive conclusion either.
- On the **positive control**, a marginal finding requires the control to have a
  component the baseline misses. If the baseline already recovers the control's
  defect in full, the marginal set is necessarily empty.

So if the positive control is fully baseline-visible, the marginal set is empty
in *every* branch that does not find a new defect, the honesty class fires
unconditionally, and the substantive conclusion becomes unreachable. The
protocol can then only return "your instrument added nothing" or "you found
something new" — never "you looked harder and it is clean."

## Worked instance

EXP-MLKEM-003 froze exactly this structure. Its inherited positive control was
the wolfSSL v5.9.1 AVX2 ML-KEM-1024 comparison tail omission at ciphertext byte
indices 1536..1567, which EV-MLKEM-005 had already established as fully
detectable by the single-byte class. The widened classes G2 (multi-byte) and G3
(alignment) rediscovered exactly that region and nothing else; the recorded
`G2_minus_G1` and `G3_minus_G1` arrays are empty, and an independent validator
recomputed both as empty from the raw per-index tables. G4 (malformed length)
was barred by construction from contributing a comparison-omission finding.

`generator_hardening_insufficient` therefore fired on the frozen text and
displaced `isolated_to_audited_commits`, even though the measurements themselves
showed no new silent index or equal-length decapsulation accept on any post-fix
wolfSSL backend or on liboqs 0.12.0. The unreachability was determinable at
design time from evidence already held. See DEC-20260724-019 for the
adjudication and EV-MLKEM-006 for the observations.

A secondary lesson from the same instance: the executor tried to escape the
class by asserting that rediscovery constituted "added discriminating power."
The specification's own metric definition — *findings attributable to the added
classes that the baseline did not produce* — forbids that reading. When a
frozen definition and a summary flag disagree, the definition governs.

## What to do instead

- **Plant a baseline-invisible component in the positive control.** Alongside the
  known real defect, include a synthetic control exhibiting a defect that only a
  widened class can reach — for example an omission that manifests only for
  coordinated multi-byte differences, or only at a lane boundary. Then the
  marginal set is non-empty exactly when the widening genuinely works, and both
  outcome classes become reachable.
- **Or decouple the two questions.** Judge instrument adequacy against a
  dedicated adequacy control and judge the substantive conclusion against the
  targets, instead of routing both through one precedence list.
- **Either way, before freezing, simulate the precedence list against each
  plausible world** and check that every outcome class is reachable in at least
  one of them. An outcome class that no world can produce is a specification
  defect, and it is cheap to find before execution and expensive after.

## Limits

This is a design constraint derived from one instance plus its own logic, not a
measured empirical regularity. It concerns protocol reachability only and says
nothing about ML-KEM, about any implementation's correctness, or about the
merits of widened differential generators, which remain the right instinct for
the blindness they were introduced to address.
