# R3 — the calibration convention (31 versus 32) and convention identity across arms

TASK-20260904-0d66e3 (red team), EXP-PFDR-20ee58. Every integer below was
recomputed here from the committed fixture with `harness/macaulay_fp` at
snapshot `2d2083e5` (`pt_proves_too_much.py`, plus the two inline mixed-mode
runs quoted), and from the raw records only (`r0_regenerate.py`). Fixture
sha256 re-hashed: `62d89109f94ef658885ddb5289504df159de01ee4341852b34349d01724bf8e5`.

## 1. The two readings, and which one the frozen criterion names

The contract fixes the deficit as
`deficit(D) = rows(D) - rank(Mac_D) - koszul(D)` with cumulative multipliers
(`inputs.deficit_definition`), and separately fixes the calibration criterion
"deficit(3) = 1 and deficit(4) = 31 with null 0".

Applying the contract's own formula to the fixture gives, reproduced
independently here:

| D | rows | rank | koszul (66 pairs + 12 Frobenius) | `rows - rank - koszul` | graded increment |
|---|---|---|---|---|---|
| 2 | 12 | 12 | 0 | 0 | 0 |
| 3 | 312 | 311 | 0 | **1** | **1** |
| 4 | 3912 | 3802 | 78 | **32** | **31** |
| 5 | 31512 | 28096 | 2094 | 1322 | 1290 |

So the **literal cumulative formula gives 32 at D = 4, not 31**. The value 31 is
the graded per-degree increment. KN-FIND-006 itself states both
("deficit(D=4) = 8k - 1 … cumulative deficit at D=4 = 8k"), so 31 is
KN-FIND-006's per-degree reading and 32 is the contract's formula applied
cumulatively; they are the same measurement read two ways, and both were
recorded by the run (deviation D2) and reproduced by me.

**Does F3 fire?** F3 is "the binary calibration arm does not return 1 and 31:
the port is broken". Literally, under the contract's own deficit formula, the
arm returns 1 and 32. In substance the arm reproduces KN-FIND-006 exactly under
both readings, plus the archived cumulative 1322 at D = 5, so the port is not
broken and **F3 does not fire in substance**. The honest disposition is that the
contract text is internally inconsistent between `inputs.deficit_definition`
(cumulative) and `binary_calibration_arm` / `preregistered_prediction` (the
graded integers 1 and 31); the run disclosed the inconsistency rather than
resolving it silently, which is the correct handling. The composition should
record the criterion as met **under KN-FIND-006's graded convention**, with the
cumulative 32 stated beside it, and should not present "31" as an output of the
formula the twin arms use.

## 2. Same code path? Same convention? — partly

- The convention block in the manifest is **byte-identical across all fourteen
  runs** (I hashed the block in each manifest: one distinct value,
  `sha256[:12] = ad4e950bfbdc`), including the calibration run, and it states
  the twin's read field explicitly: `LayerResult.deficit_pairwise under
  convention='cumulative'`.
- The calibration's headline **31 is `deficit_graded`**, a different functional
  from the twin's headline 0, which is `deficit_pairwise` (cumulative). For the
  twin the two coincide (all zeros; I verified `deficit_series == deficit`
  on all 246 draws in R0), so nothing is affected — but the calibration integer
  and the twin integer are not the same quantity, and a composition that writes
  "the same convention returned 31 there and 0 here" would be overstating.
- The Frobenius term enters `koszul` only at p = 2 in the pure squarefree ring
  (`koszul.frobenius_count`), which is correct: (S2) shows the family is empty
  for p > 2. This is an object-dependent count, not a convention difference.

## 3. The mixed-mode derived expectation (1, 33) — correct, with a disclosed flag

The calibration run also puts the 24 Boolean generators into the **mixed** ring
with one unused free variable u and reports `deficit_pairwise(D = 2..4) =
[0, 1, 33]` matching a derived expectation `[0, 1, 33]`.

Verified here. The derivation is right: rows `u^k m' f` with distinct k occupy
disjoint column sets, the k-block at D is the squarefree cumulative layer at
D − k, and so
`deficit_mixed(D) = Σ_{k≥0} deficit_squarefree(D - k) = 0 + 1 + 32 = 33` at
D = 4 — **provided the Frobenius term is included in the mixed-mode Koszul
count**. It is not included by default: `default_frobenius` keys on the ring
(p = 2 AND `n_free == 0`), so the meter's default in mixed mode gives
`koszul = 66` and `deficit_pairwise = [0, 1, 45]`, which I reproduced. The run
forces `frobenius=True` for this check, which is disclosed in the run script's
comment and in `analysis.md` ("Frobenius count on") — and is mathematically
correct for that object, since those generators are u-free and Boolean so
`f^2 = f` genuinely holds.

Two consequences worth recording, neither of which invalidates anything:

1. The meter's Frobenius default is **ring-keyed, not generator-keyed**: at
   p = 2 in mixed mode with u-free Boolean generators it under-counts the
   trivial syzygies by one per generator. Harmless for the twin (p > 2), and
   correct for my p = 2 mixed twin object (whose generators contain u, so
   `f^2 ≠ f` and 0 is right), but it is an instrument property that should be
   named if the mixed p = 2 path is used again.
2. The mixed-mode check therefore runs at a flag setting the twin arms do not
   use. It exercises the code path, not the twin's exact configuration.

## 4. Result

R3 **holds**, with the disposition above: the calibration is reproduced under
KN-FIND-006's convention (1 and 31 graded; 32 cumulative; 1322 at D = 5), the
convention block is identical across all fourteen runs, the Frobenius term is
correctly restricted to p = 2 pure-squarefree, and the mixed-mode expectation is
right under its disclosed flag. The one thing that must not be carried forward
unqualified is the phrase "the calibration returned 1 and 31 under the same
convention": it returned 31 under the **graded** reading of that convention and
32 under the literal formula.
