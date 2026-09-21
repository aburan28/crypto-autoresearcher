# Defect localization — TASK-20260824-dd5b5c

## Scope and executor boundary

This is an Executor observation package for `GOAL-SSI-001` / `BATCH-eb0a7e`.
It is arithmetic on committed literals and code reading, not an executed
attack, certificate, security assessment, standardized-parameter claim, or
asymptotic-complexity result. No hypothesis status or official research state
is changed here.

The frozen files were read only. In particular, no file under
`experiments/EXP-WESOVOW-001/` or
`experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-001/` was edited, moved,
regenerated, reformatted, or rerun. The existing
`corrected_charging.py` and `recomputed_table.json` were preserved unchanged
when this resumed package was written.

## Source statements and line-local comparison

The three frozen artifact statements that govern the defect check are quoted
verbatim below.

1. The implementation's serialized formula is:

   > `"T_w_vOW": "T_full / sqrt(min(w, M))",`

   Source: `experiments/EXP-WESOVOW-001/cost_model.py:236`.

2. The committed raw result repeats the same formula:

   > `"T_w_vOW": "T_full / sqrt(min(w, M))",`

   Source: `experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-001/raw-result.json:13`.

3. The frozen specification states the cap requirement:

   > `description: At w = M, vOW time must equal T_full exactly (cap check).`

   Source: `experiments/EXP-WESOVOW-001/specification.yaml:149`.

The executable implementation of the first statement is also explicit in
`experiments/EXP-WESOVOW-001/cost_model.py:265-276`; specifically, line 270
computes:

> `log2Tw = log2Tfull - 0.5 * min(lw, log2M) + overhead_bits`

The run's serialized rows therefore agree with the implementation's formula;
there is no evidence here of a code-versus-raw-result serialization
disagreement. The mismatch is between that repeated charging formula and the
specification's own `w=M` cap requirement.

For comparison, the committed independent red-team report records the source
time-memory statement as follows:

> “The time-memory tradeoff of van Oorschot–Wiener [43] solves a claw-finding
> problem of this size in time essentially `√(N³/w) =
> p^{1/2+o(1)}/w^{1/2}` with memory `w`. This allows one to interpolate between
> the `p^{1/3+o(1)}` high-memory algorithm presented here and the classic
> `p^{1/2+o(1)}` algorithms with polynomial memory like [21].”

Source: `coordination/goals/GOAL-SSI-001/batches/BATCH-b3c87f/reviews/TASK-20260806-9536f4/red_team_report.md:238-242`.
The same report gives the corresponding two-column charging convention:

> `T_A(P, w) = L_paper(P) + E(P) + S + c·√P + A + 0.5·max(0, L_mem(P) − log2 w)`
>
> `T_B(P, w) = P/2 + log2 k_DG + A            (memoryless; the paper's own column)`

Source: `coordination/goals/GOAL-SSI-001/batches/BATCH-b3c87f/reviews/TASK-20260806-9536f4/red_team_report.md:286-292`.

## Localization result

The defect is a single level/anchor error in the vOW charging law, propagated
consistently into the frozen raw result:

- The frozen expression divides `T_full` by the square root of a memory
  *count*, `min(w, M)`. In log2 coordinates this subtracts
  `0.5*min(log2w, log2M)` from the full-memory time.
- A ratio-anchored middle-memory law must instead add the memory penalty
  `0.5*max(0, log2M-log2w)` to the full-memory time. At `w=M`, the penalty is
  zero, so the result is exactly `T_full`.
- The standalone implementation applies this corrected, scoped form for each
  anchor:

  `log2T_corrected = log2T_full_anchor + c*sqrt(log2p) + 0.5*max(0, log2M_anchor-log2w)`.

The two anchors are kept separate in the machine-readable table:

| Anchor | Time source | Memory source |
|---|---|---|
| `fitted_opt` | `experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-001/raw-result.json`, each `per_field[log2p=*].optimal.log2T` | the corresponding `optimal.log2M` |
| `PAPER_PAIRS` | `experiments/EXP-WESOVOW-001/cost_model.py:60-65` | the corresponding literal pair's second component |

The full frozen grid is specified at
`experiments/EXP-WESOVOW-001/specification.yaml:108-129`: field sizes
`{256,384,512,576,768}`, memory budgets `log2 w` in
`{30,40,50,60,70,80}`, and overhead values `{0.0,0.5,1.0,2.0}`. The existing
table contains 240 rows: 120 rows for each named anchor, with every row
carrying its anchor name and source trace.

## What this does and does not establish

The observation localizes the arithmetic inconsistency between the frozen
implementation/raw formula and the frozen cap requirement. It does not
repair the frozen experiment, promote or reject a hypothesis, or establish a
cryptanalytic or security conclusion. The original run's own scope remains
the model's stated unit of `F_{p^2}` operations and table-entry memory; the
specification calls these model-conditional observations at
`experiments/EXP-WESOVOW-001/specification.yaml:155-159`.

The P=512 boundary is preserved verbatim:

> The `P=512` crossover value and its `w=2^80` sign are **NOT citation-eligible**. This task does not lift that prohibition. Only a committed Coordinator decision on independently reviewed evidence can lift it.

This package does not make a SQIsign, CSIDH, standardized-parameter,
security, or asymptotic claim.
