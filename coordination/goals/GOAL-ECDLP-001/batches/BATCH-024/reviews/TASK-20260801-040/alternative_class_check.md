# TASK-20260801-040 alternative-class and DESIGN-TRAP-1 check

Verdict: **REVISE**.

## Independent DESIGN-TRAP-1 derivation

For resolution K, let `A_i = bin_K(e1_i)`, `B_i = bin_K(e2_i)` and

`N[a,b] = sum_i 1{A_i=a and B_i=b}`.

Suppose a permutation maps e2 values only among indices in the same A stratum.
For each fixed a, it preserves the multiset `{B_i : A_i=a}`. Therefore

`N'[a,b] = sum_{i:A_i=a} 1{B_perm(i)=b} = N[a,b]`

for every a,b. The complete K-by-K table is identical, not merely equal in
expectation. Any statistic that sees only that table has exactly the same
source-versus-plant input at every rung. A nominal rejection rate would then
be guaranteed by construction and would say nothing about power. This is the
DESIGN-TRAP-1 invariance; I derived it from the count definition rather than
accepting the contract's prose.

## Source audit of C1, C2 and C3

### C1: Gaussian-copula reordering

`plant_copula` leaves e1 unchanged and returns `sort(e2)` indexed by global
ranks of `rho*z1 + sqrt(1-rho^2)*W`. It is therefore an exact permutation of
the e2 multiset. The permutation is not constrained within K=16 or K=64 e1
bins, so DESIGN-TRAP-1 invariance is not structural at either resolution.

The calibration measured only rho=0 and a separate comonotone anchor. At K=16
their mean source-versus-plant joint TV values are about 0.023 and 0.92. That
shows movement for those two objects only. No K=64 joint movement is computed,
and no actual C1 ladder rung below/at one was calibrated. The source makes
movement possible and overwhelmingly likely, but does not prove a nonzero
finite-sample table difference at every randomized rung.

### C2: paired cell exchange

`plant_cell` leaves e1 unchanged and exchanges e2 values across pairs whose
e1 K=16 bins differ. Because K=64 refines K=16, paired indices also differ in
their e1 K=64 bins. The e2 multiset is exactly preserved, so both marginals are
bit-identical.

However, the code does not require the two exchanged e2 values to occupy
different K=16 or K=64 bins. If their e2 bins coincide, that exchange changes
neither table. Even when individual exchanges move cells, multiple exchanges
can cancel at table level. Thus the construction avoids being confined to the
DESIGN-TRAP strata, but does not guarantee the claimed table movement. No C2
arm was calibrated. The measurement driver records only K=16 joint TV, leaving
the mandatory K=64 assertion untested.

### C3: two-stratum block permutation

`plant_block` splits records at the median e1 rank and permutes chosen e2
values within each half. Each half spans eight K=16 e1 bins and thirty-two
K=64 e1 bins, so the permutation is much coarser than either statistic grid
and is not DESIGN-TRAP invariant by definition. e1 is unchanged and e2 is
globally permuted, preserving both marginals exactly.

It is nevertheless possible for a realized permutation to remain inside fine
bins, exchange equal e2 bins, or cancel in aggregate. C3 has no calibration
endpoint at all. As with C2, source capability is not a measured movement
certificate, and K=64 source-versus-plant movement is absent from the driver.

## Resolution and certification reach

The driver constructs all three named families and thresholds CHI-16 and
CHI-64 at all frozen rungs. It also checks K=16 and K=64 *marginal* histograms,
but `induced_dependence` calls only `joint_tv_distance_k16`. A K=64 marginal
check cannot prove K=64 joint movement. Plant-versus-fresh-null CHI-64 can show
rejection power, but it does not isolate whether the paired source-to-plant
table moved; the fresh null itself fluctuates.

Consequently the certified list must not say the current design has verified
each construction moves both joint tables. Before measurement, either:

1. compute and freeze source-versus-plant K=16 and K=64 movement diagnostics
   for every family/rung/replicate, with a mechanical non-invariance gate; or
2. narrow the claim to measured detection power for the named randomized
   constructors without asserting per-resolution source-to-plant movement.

## U1 through U6

No silent claim to U1 through U6 was found in the specification or reading
rule. They are restated in full, with C1-C3 explicitly uncertified before a
valid measurement. In particular:

- U1 preserves the exact two-sample cancellation blind spot;
- U2 preserves sub-grid, sparse-cell and below-smallest-rung gaps;
- U3 preserves rank/cell-family shape gaps;
- U4 preserves fine e2-marginal coverage limits;
- U5 confines everything to two toy cells, Bfb=512, m=4 and INT-2;
- U6 preserves the deterministic-rule versus small-x-window confound.

That scope discipline is sound but does not cure the missing K=64 movement
check.

## Merit checks on cuts and comparison

rho_star=0.05 is openly declared conventional and the full curve is retained;
it is not a derived boundary. n=130816 gives average cell occupancy about 511
at K=16 and 31.9 at K=64, adequate for executing the frozen grids at toy scale.

eps_det and EV-EQD-001's delta=0.02 share only the unit “fraction of records
touched.” Their plants have different effect distributions. The ratio
eps_det/0.02 may be reported as a ratio of smallest detected rungs for the two
named constructors, but not as a general or geometry-free measure of how much
less sensitive the apparatus is to dependence.

