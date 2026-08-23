# Coordinator check: BATCH-541940 takes NO cell on ANY comparable metric

Author: orchestrating session (Coordinator), after TASK-20260823-416e78 returned.
Status: triage input for the ledger archive TASK-20260823-bd5f2f. NOT evidence.
HELD OUT OF THE REPOSITORY until both blind reviewers return, so neither sees it.
Same pattern as BATCH-da59ec's COORDINATOR-multimetric-check.md.

## Why

The producer measured against ONE metric, naive height, because that is what
H-ECQ-8b600d pre-declared. The frozen frontier keeps three: min_naive_height,
min_faltings_height, min_log_conductor. (It carries NO log|disc| metric; the
"four metrics" figure in earlier session notes was wrong about this file.) A
curve that misses on one metric can hold a cell on another, and not checking
would leave an obvious way to later claim a cell nobody pre-declared.

## Result

9 distinct curves (the 12 records contain 3 duplicate a-invariant sets), each
compared against the frozen cell AT ITS OWN certified rank threshold.

 r>= sgnD    naive h      cell     gap |    log N     cell    gap |    Falt    cell    gap
  12    +     86.774    69.339  +17.43 |    74.63    57.76 +16.87 |   5.268   3.811  +1.46
  11    +     74.121    61.507  +12.61 |    61.80    51.25 +10.56 |   4.105   3.041  +1.06
  10    -     68.639    54.349  +14.29 |    54.08    43.77 +10.31 |     n/a     n/a    n/a
   9    +     61.127    47.974  +13.15 |    47.04    38.01  +9.03 |   3.112   1.983  +1.13
   8    +     51.070    41.826   +9.24 |    37.40    33.15  +4.25 |   2.171   1.512  +0.66
   7    +     49.596    35.779  +13.82 |    32.61    26.67  +5.94 |   2.145   1.037  +1.11
   6    +     47.179    30.376  +16.80 |    24.82    22.37  +2.45 |   1.843   0.583  +1.26
   5    -     29.773    24.318   +5.45 |    17.36    16.76  +0.60 |     n/a     n/a    n/a
   2    +     25.430    13.525  +11.90 |     7.62     5.96  +1.65 |  -0.050  -0.815  +0.76

CELLS TAKEN: **NONE**, on any comparable metric at any threshold.
Closest approach anywhere: log conductor at r>=5, +0.60.

## A false positive I generated and then killed — record it, do not bury it

My first pass reported a HIT: Faltings 2.284 against the r>=10 cell 2.511, i.e.
-0.226 BELOW the incumbent. It is an artifact of my own arithmetic, not a cell.

I validated the convention `h = -1/2 log|Im(conj(w1) w2)|` on the minimal model
against the board's own published faltings_height, over all 289 frozen curves:

  disc > 0 : 156 curves, 156 reproduce the published value to < 1e-6
  disc < 0 : 133 curves,   0 reproduce it; offsets range -40.73 .. +0.72

The split is exactly on the sign of the discriminant. No constant convention
fixes it: I tested +/- (1/12)log|disc|, factors of 2 in the covolume both ways,
and the raw (non-minimalised) model. Zero matches on all five.

Our r>=10 candidate has disc < 0. So its Faltings value is computed in a
convention the board demonstrably does not use, and the "hit" is void. The
r>=10 INCUMBENT (id 60, David Renshaw) has disc > 0 and my formula reproduces
its published value exactly -- so the incumbent side was fine and the candidate
side was not, which is precisely how a spurious record claim gets made.

Faltings is therefore reported n/a for the 4 disc<0 candidates rather than
guessed. naive height and log conductor are exact integer computations and are
unaffected; I independently recomputed all 12 naive heights from minimal
a-invariants and they reproduce the producer's to < 1e-9.

## Standing point about C1'

Even had the r>=10 Faltings figure been real, it would NOT satisfy C1'. C1'
requires a cell PRE-DECLARED in the governing hypothesis before the curve
existed; H-ECQ-8b600d pre-declared naive_height at r>=12 and nothing else.
Fishing across metrics after seeing the data is the hollow closure the
BATCH-f2341e red team closed off. This check exists to KNOW, not to claim.

## Open item for the board's own data

133 of 289 frozen board entries carry a faltings_height this session cannot
reproduce from their own a-invariants under any convention tried, and the split
is exactly disc<0. That is a property of the ICARM data, not of this campaign,
and it bears on any future Faltings-metric claim. Worth an OPEN record if a
Faltings cell is ever pre-declared. Do NOT infer board error from this: the
likelier reading is a convention for disc<0 that I have not identified.

---

## ADDENDUM, written after the blind reviewers returned (both were blind to this note)

**The r>=5 row of the table above is WRONG in its attribution.** Validator F5 and red
team RT-C1-O1 both found, independently and unaided, that the curve giving 29.7728 at
thresholds r>=3, 4 and 5 is FROZEN ICARM BOARD CURVE id 108 -- a board curve
rediscovered, not a curve this program exhibited. best_candidates.json does record this;
report.md does not, and neither did I. Read that row as "the board's own curve, found
again", not as "our best". It could never have satisfied C1', which requires a curve
first exhibited by this program.

That is the second half of my own standing instruction -- "check it is not simply a board
curve rediscovered" -- firing on a real case. The precaution was right. I did not apply
it to my own table.

The r>=2 row (25.4297) needs the same check before it is quoted anywhere.

Nothing else in the table changes: no cell is taken on any comparable metric, and the
Faltings artifact analysis above stands as written.
