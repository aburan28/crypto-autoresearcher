#set page(paper: "a4", margin: 14mm)
#set text(size: 9.2pt)

= Prime-field 50-bit m=8 packed-tail engineering gate

*2026-10-17; TASK-20261017-08bc0f.* The bounded target-blind four-point tail
construction and independent table check passed. This is an engineering
observation, not a complete index-calculus comparison or a speed claim.

#align(center)[#image("diagram.svg", width: 86%)]

== Fixed input and arithmetic

The public prime-order curve is over p = 1125899798684033 with
a = 779030791575407, b = 827069435865303, and
r = 1125899778887903. The fixture SHA256 begins `849ded0bc55a`.
`small_x` selected 132 points before any target, in increasing x order,
with the smaller y. The point-list SHA256 begins `14c11ea0cde2`.
Base construction took 0.005979125 s. The point digest and exact
serialization are in `input-manifest.json`.
The subgroup order is 50 bits but slightly below the literal value 2^50.

The opt-in Numba producer uses a floating quotient estimate with an exact
64-bit residual correction for p < 2^50. A quotient error below one and a
signed residual of magnitude below 2p make the final modular product exact.
The C++ `__uint128_t` producer compiled, but fresh native executables stalled
before `main` on this host, including two independent hello controls.
That host obstruction affects wider fields; it is recorded separately.

== Observed construction counts

#table(
  columns: (auto, auto, auto, auto),
  inset: 5pt,
  [*Tail length*], [*Actual entries*], [*Upper entries*], [*Pair charges*],
  [2], [17,424], [17,556], [8,778],
  [3], [1,550,780], [1,568,336], [775,390],
  [4], [104,294,212], [105,862,680], [52,147,172],
)

The derived total is 52,931,340 S3-equivalent pair charges. The sorted
h=4 table occupies 1,668,707,392 bytes at 16 bytes per record. The producer
recorded 396 inversion batches and 264 exceptional same-x prepends.

Seven small-control tests passed for p=1019 and the same 50-bit curve at
h=2,3,4, plus altered-object rejection. The retained 50-bit B8 h4 table
contains 2,152 records, and an independent scalar checker replayed all
of them with no ordering, bound, or point-sum discrepancy.

== Complete-cost boundary

The task envelope was 8 GiB sampled process RSS, 12 GiB scratch, and
14,400 s wall. The wrapper took 982.639 s. Producer phases included
945.218 s for global sort and 18.884 s for final writing; the sort was
96.50% of producer wall. Peak RSS was 5.030 GB (4.684 GiB), and peak
scratch was 3.363 GB (3.132 GiB). The table remains in local-only custody
under the pinned workspace-volume scratch directory and is excluded from Git.

The independent checker scanned all 104,294,212 records for sort order and
bounds with zero failures. It found 101,227,632 distinct x keys and
3,066,580 extra records sharing an x. Its 105 chunk digests and full SHA256
`fa868fc32473...857828b02` match the retained table. Scalar replay passed
at 4,096 fixed hash-selected positions and the first and last 256 positions:
4,608 of 4,608 valid. Full scalar replay of every record was not attempted.

This table contains no degree-of-regularity measurement, sparse solver
input or runtime, verified relation, independent rank, linear algebra,
unseen-target reconstruction, matched rho, or complete end-to-end S.
Direct S8 represents seven summands plus the target; eight summands
require S9 or a chained formulation. The existing baseline and full-width
obstruction remain the comparison references. No canonical ECDLP frontier
graph changes from this engineering count chart.
