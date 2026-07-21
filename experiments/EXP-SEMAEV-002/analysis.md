# EXP-SEMAEV-002 — analysis

## 1. Observation
Exact decomposition counts over 300 targets (m=2, factor base size 20):

| bits | seed | n | found_random | found_interval | found_ap | ratio_int | ratio_ap |
|---|---|---|---|---|---|---|---|
| 12 | 1 | 31   | 60 | 71 | 67 | 1.18 | 1.12 |
| 12 | 2 | 37   | 66 | 68 | 66 | 1.03 | 1.00 |
| 12 | 3 | 2377 | 78 | 85 | 91 | 1.09 | 1.17 |
| 14 | 1 | 647  | 14 | 22 | 22 | 1.57 | 1.57 |
| 14 | 2 | 941  | 29 | 16 | 21 | 0.55 | 0.72 |
| 14 | 3 | 367  | 12 | 18 | 14 | 1.50 | 1.17 |
| 16 | 1 | 23   |  5 |  4 |  4 | 0.80 | 0.80 |
| 16 | 2 | 733  |  6 |  9 |  7 | 1.50 | 1.17 |
| 16 | 3 | 479  |  3 |  7 |  7 | 2.33 | 2.33 |

All certificates verified.

## 2. Comparison to predefined criteria (H-SEMAEV-002)
Success criterion was: all structured/random ratios <= 1.5x. This is NOT met as
stated: 4 cells reach or exceed 1.5x (b14s1 1.57, b14s3 1.50, b16s2 1.50, b16s3
2.33). The falsification_criterion (any ratio > 1.5x) is literally triggered by
b16s3.

## 3. Inference
The threshold excursions are consistent with sampling noise, not a structural
effect:
- They occur only where decomposition counts are tiny (b16s3 is 7 vs 3; b14s1
  is 22 vs 14). Poisson 95% intervals on such counts span 1.0 by a wide margin.
- The effect direction is inconsistent: at b14s2 the RANDOM base beats both
  structured bases (ratio 0.55), which a genuine structured advantage would not
  produce.
- At the only well-powered cells (bits=12, counts 60-91), all ratios are
  <= 1.18 -- a clean local corroboration of "no material structured advantage."

So the data do not discriminate "structured beats random by >1.5x" from "no
effect plus low-count noise." Reporting the raw threshold trip as a positive
structured-advantage finding would be a false positive.

## 4. Limitations
- The v1 protocol set a fixed 1.5x ratio threshold without a minimum-count /
  statistical-power gate; ratio variance explodes at low yield (high bits),
  making the threshold meaningless there. This is a design confound, recorded
  for redesign, not a mathematical result.
- Toy prime fields, m=2 only. Independent of, and not a substitute for, the
  campaign's m=3 EXP-FB-001 conclusion.
- claim tier: toy.
