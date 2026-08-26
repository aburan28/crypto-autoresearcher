# Legacy-hash frontier acquisition report

Task: `TASK-20260825-51dfe7`  
As of: 2026-08-25

This bounded pass produced 19 notion-separated rows: 17 have retrieved or
committed-internal primary-source support, while two remain ineligible pointers.
Fourteen rows are marked as frontier candidates *inside this shard and their
exact comparison key*. That marking is not a cross-corpus promotion; the
Coordinator and independent reviewers still have to check source completeness
and Pareto dominance before compilation into canonical knowledge.

No collision was generated, no differential path was searched, and no attack
code was executed.

## The SHA-1 scalar is not a frontier

The familiar statement “SHA-1 is about \(2^{61}\)” identifies one particular
row, not SHA-1 as a whole. The exact partition recovered from primary texts is:

| Cell | Paper-reported frontier candidate | Evidence and unit |
|---|---:|---|
| Identical-prefix collision, theoretical/expected work | \(2^{61.2}\) | SHA-1 equivalents on a GTX 970; Leurent–Peyrin, Table 1/Table 2 |
| Identical-prefix collision, demonstrated work | \(2^{63.1}\) | compression-function-call equivalent for SHAttered; about 6,500 CPU-years and 100 GPU-years |
| Chosen-prefix collision, theoretical/expected work | \(2^{63.4}\) | SHA-1 equivalents on a GTX 970; the paper gives \(2^{63.5}\) on a GTX 1060 |
| Chosen-prefix collision, demonstrated run | two months on 900 GTX 1060 GPUs | first realized chosen-prefix collision; authors report USD 75k realized rental cost |
| Collision detector / countercryptanalysis | 1.96× average slowdown | implemented detector covering 32 disturbance vectors under the paper's stated conjecture |
| Preimage | 57 of 80 steps, \(2^{158.8}\) | correctly padded two-block reduced-SHA-1 preimage |
| Second preimage | 34 of 80 steps, \(2^{42.25}\) | success greater than 1/2, but needs a given first preimage of about \(2^{42.25}\) blocks |

These rows are incomparable in several independent ways: collision versus
preimage, identical-prefix versus chosen-prefix, expected cost versus a realized
run, hardware-normalized SHA-1 equivalents versus compression calls, attack
versus detector, and full versus reduced round count. In particular, the
\(2^{61.2}\) estimate must not overwrite the \(2^{63.1}\) demonstrated result
or the \(2^{63.4}\) chosen-prefix estimate.

The detector row is also intentionally scoped. Stevens–Shumow describe a
detector for covered disturbance-vector attack classes and make the unavoidable
condition construction depend on a conjecture supported by the attack state of
the art. It is not a theorem that every future SHA-1 collision construction must
be detected.

## What ePrint 2026/1744 changes for RIPEMD-160

The supplied paper, Zhengrong Lu et al., *Improved Collision Attack on
RIPEMD-160*, advances the paper-reported practical **standard collision** reach
from 40 steps (the 2023 row in its Table 1) to 42 steps. The authors report:

- three colliding message pairs for 42-step RIPEMD-160;
- an uncontrolled-condition probability of approximately \(2^{-47.4}\), giving
  an expected time of approximately \(2^{47.4}\) reduced 42-step compression
  calls;
- a practical platform of 560 cores on 2.7 GHz Intel Xeon 6258R processors;
- first results for two starting blocks in 30 minutes and two hours,
  normalized by the authors to approximately \(2^{41.9}\) and \(2^{43.9}\)
  reduced compression calls.

The theoretical and demonstrated measurements are separate rows because their
success and cost conventions differ. RIPEMD-160 has 80 steps. The paper's own
conclusion says the result is for a reduced 42-step version and does not break
the full hash; this shard records `round_scope: reduced`, `rounds_attacked: 42`,
and `total_rounds: 80` in both rows.

The 44-step, \(2^{76.9}\) semi-free-start result shown in ePrint 2026/1744's
comparison table is a different security notion and target model: it gives the
attacker control of the initial value and concerns the compression function.
It therefore cannot dominate, or be dominated by, the 42-step standard hash
collision. Because this producer could not retrieve ePrint 2025/1531 itself,
the 44-step row remains a secondary pointer and is not frontier-eligible.

The producer's direct open of ePrint 2026/1744 was blocked by the web retrieval
layer. The driving Coordinator had already retrieved and read the exact 20-page
PDF, supplied its SHA-256
`9b903d0599f6f78b9534b7cb32e1ca74bf8d01bb0e896a3986b0e778c3d004b6`,
and transferred the exact abstract, Table 1, Section 3.3, conclusion, platform,
and artifact locators. The resulting rows use `provenance: internal` and name
the Coordinator as verifier. They require the planned independent re-fetch
before canonical promotion; this report does not pretend the producer opened
the PDF successfully.

## Other recovered rows

- MD4: a demonstrated full collision described by the source as hand
  calculable, with no invented \(2^N\) cost; full multi-block preimage tradeoff
  rows at \(2^{78.4}\) online work with \(2^{128}\) preprocessing and
  \(2^{81}\) storage versus \(2^{99.7}\) without precomputation; and a distinct
  one-block preimage row at \(2^{94.98}\).
- SHA-0: the later practical full collision result at measured complexity
  \(2^{33.6}\) hash calls and about one hour on an average 2008 PC, rather than
  retaining the earlier \(2^{51}\), \(2^{39}\), or \(2^{36}\) milestones as the
  frontier; plus a reduced 52-of-80-step preimage at \(2^{156.6}\) compression
  calls and \(2^{15}\) 160-bit words of memory.
- MD5: a quarantine-safe internal metadata row for the demonstrated collision,
  a 47-of-64-step compression-function preimage at \(2^{96}\) trials, and an
  explicitly ineligible recalled pointer to the \(2^{123.4}\) full-preimage
  result.

## Coverage states and gaps

| Primitive | Batch-1 state | Boundary of this pass |
|---|---|---|
| MD4 | `primary_source_partial` | Full collision and principal preimage tradeoffs covered; chosen-prefix, dedicated trail, distinguisher, and a fresh second-preimage sweep remain. |
| MD5 | `routed_to_another_goal` | GOAL-MD5-001 owns the content-sensitive frontier. The full-preimage primary chapter remains unavailable in the permitted metadata. |
| SHA-0 | `primary_source_partial` | Practical full collision and reduced preimage covered. No claim is made that unfilled chosen-prefix, second-preimage, or trail cells have no result. |
| SHA-1 | `primary_source_partial` | All six required partition cells have rows, but this is not an exhaustive enumeration of every reduced-round trail, free-start result, or historical attack. |
| RIPEMD-160 | `primary_source_partial` | The supplied 42-step collision result is captured. The 44-step semi-free-start paper and a complete preimage/distinguisher sweep still require primary-text acquisition. |

Every missing cost field has an explicit reason such as
`not_stated_by_source`, `not_applicable`, or `unresolved_transcription`.
“Practical” was never converted into a \(2^N\) value unless the source itself
provided that normalization.

The web search was bounded, and the idea-generator role prohibited shell-based
repository searches. Accordingly, this report makes no “no attack exists”
claim. Missing cells are acquisition gaps, not negative evidence.

## MD5 quarantine attestation

This producer read only the committed, permitted metadata file
`TASK-20260821-cbb510/frontier-ledger.yaml`. It did **not** fetch, open, read,
transcribe, reconstruct, or follow citations into:

- ePrint 2004/199;
- the GOAL-MD5-001 quarantined collision-path payload;
- HashClash path tables; or
- any other MD5 collision-path content.

The MD5 method summaries deliberately omit all path, pair, and message-word
payload. MD5 rows are not promoted by this shard and remain routed to their
owning goal.

## Prior/baseline corrections made during acquisition

Two scalar baselines were corrected without making a novelty claim:

1. “SHA-1 ≈ \(2^{61}\)” became a seven-cell, notion-separated partition. The
   scalar survives only as the GTX-970-normalized identical-prefix theoretical
   row \(2^{61.2}\).
2. The first retrieved SHA-0 full-collision milestone, \(2^{51}\), was not kept
   as the frontier after later primary-source searching found the demonstrated
   \(2^{33.6}\) result.

No Coordinator decision, goal status, or canonical knowledge record was changed
by this producer.
