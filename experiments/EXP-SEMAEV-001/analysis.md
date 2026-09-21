# EXP-SEMAEV-001 — analysis

Strictly separated per docs/task-lifecycle.md step 8.

## 1. Observation
Six S_3 decomposition (gb) runs and six matched rho runs, all
`completed_valid`, all certificates independently verified.

| bits | seed | gb max-deg proxy | gb seconds | decomposition | rho group ops |
|---|---|---|---|---|---|
| 8  | 1 | 2 | 0.173 | yes (cert ok) | 15 |
| 8  | 2 | 4 | 0.160 | yes (cert ok) | 30 |
| 10 | 1 | 0 | 0.157 | no            | 6  |
| 10 | 2 | 2 | 0.167 | yes (cert ok) | 12 |
| 12 | 1 | 0 | 0.166 | no            | 15 |
| 12 | 2 | 0 | 0.161 | no            | 6  |

(max-deg proxy 0 == trivial ideal [1] == no decomposition over the factor base.)

## 2. Comparison to predefined criteria (H-SEMAEV-001)
- Predicted: reduced-basis max-degree proxy <= 6 across tested bits.
  Observed max = 4. **Met.**
- Predicted: gb wall time < 1.0s, not super-linear in bits.
  Observed range 0.157–0.173s, flat across 8→12 bits. **Met.**

## 3. Inference (compatible explanations)
At this toy range, the S_3 length-2 decomposition system's reduced Groebner
basis stays low-degree and cheap; the factor-base indicator degree (14) does
not inflate the *reduced* basis. The flat timing is consistent with the system
size being dominated by the fixed factor-base size rather than field bits over
8–12 bits. This does not establish a scaling law — the bit range is too narrow
and timing is sympy-bound.

## 4. Limitations
- Toy prime fields (8–12 bits) only; claim tier `toy`. Says nothing about
  medium/crypto scale or about the true degree of regularity.
- Only 2 seeds per bit size; decomposition incidence (3/6) is not a controlled
  measurement of decomposition probability.
- Absolute timings reflect sympy's unoptimized solver, not a cost model, and
  must not be compared to the rho op-counts without one.
