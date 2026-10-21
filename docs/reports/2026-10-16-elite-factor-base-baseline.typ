#set page(paper: "a4", margin: (x: 16mm, y: 11mm))
#set text(font: "Arial", size: 8pt)
#set par(justify: true)

= Index-calculus baseline and factor-base search boundary

2026-10-16 · Source-linked assessment; no new scientific trial or speed claim. Corrected after PR #2309: later N53 baseline, tuple count and wide-entry size. Full source links: `2026-10-16-elite-factor-base-baseline.md`.

*Size correction, 2026-10-17.* The n=53 Koblitz comparator's target prime is
21,044,858,204,113 (bit length 45, log₂ r≈44.26). It measures a 53-bit
field, not a prime subgroup of order 2^50…2^63. Exact order screening finds
no such prime subgroup for the two standard binary Koblitz curves at field
degrees 50…63; see `2026-10-17-koblitz-size-screen.md`.

#image("2026-10-16-elite-factor-base-baseline.svg", width: 90%)

== Measured baseline

*Koblitz GF(2^53).* The latest reviewed complete implementation in this checkout is RUN-KIC-a15078: 24 fresh public known-answer targets, 96 valid four-arm processes, independent review and Coordinator decision DEC-20260921-6648da. The composed IC median cold wall was 3.080913 s; the paired IC/strengthened signed-Frobenius rho wall ratio was *3.294582* (bootstrap 95% interval [2.802517, 4.368945]). Its paired wall ratio against the larger-table full-rank IC control on the same panel was 0.820151. Median peak RSS was 773,734,400 bytes for IC and 88,391,680 bytes for strengthened rho. Earlier distinct panels measured allocation/density (RUN-KIC-e3dbed), table capacity (RUN-KIC-8b5038), and target-certificate stopping (RUN-KIC-56c897); their ratios cannot be chained.

*Prime field.* The complete checked solver has measured m=2..7 through 32 bits. At 32 bits the m=3..7 median S3-equivalent counts were 2.08e6, 1.71e7, 1.38e6, 7.75e6 and 1.78e6, versus 93,546 rho walk additions. These are different operation units. No complete 50–63-bit row or m=8 run is established by those receipts. The compact numpy path stops below 2^32.

*Ordinary binary.* No independently checked 50–63-bit same-point complete solve was identified in this checkout. A GF(2^51) conductor study has certified graph edges, while its required arity-3 enumerator/checker and general point-map evaluator remain open.

== Derived high-arity capacity model

The prime solver states h=ceil(m/2) and B≈((m!N)/2)^(1/m)/2. Its tail source gives a tuple-count upper bound U=2^(h−1)×binomial(B+h−1,h). The model S3-equivalent exponent is max(h,m−h+1)/m. The memory figures below multiply U by 16 bytes for a *hypothetical* wide array; they are derived payload upper bounds, not process measurements.

#table(
  columns: (auto, auto, auto, auto, auto),
  inset: 4pt,
  stroke: .4pt + gray,
  [m], [h], [Exponent], [50-bit upper], [63-bit upper],
  [2], [1], [1.000], [0.25 GiB (ref)], [22.63 GiB (ref)],
  [3], [2], [0.667], [83.86 GiB], [34,080.15 GiB],
  [4], [2], [0.750], [0.43 GiB], [39.19 GiB],
  [5], [3], [0.600], [15.63 GiB], [3,469.10 GiB],
  [6], [3], [0.667], [0.80 GiB], [71.75 GiB],
  [7], [4], [0.571], [11.32 GiB], [1,890.96 GiB],
  [8], [4], [0.625], [1.58 GiB], [136.96 GiB],
)

Ref = comparison-sized payload only: the m=2 engine does not allocate an h-point table of this kind. The upper bound does not prove the actual table needs that much memory. Setup, sorting, extra arrays, matrix, and process memory are additional; the current wide-prime fallback uses a Python map. m=7 has a lower model exponent than m=8 in this generic split. At 32 bits the measured m=7 count was still 1.3 times m=5. This is not a 50–63-bit timing forecast.

== Search and acceptance

The prime-field sparse-subgroup equation helped one m=2 algebraic cell but not m=3; complete small-scale relation supply was similar for size-matched small-x, random and subgroup bases. The next comparison pairs base and equation formulation, measuring construction, monomials, observed solving degree, misses, verified rows, useful rank, final solve and blind target work. The composed N53 Koblitz median internal query kernel is 1.844756 s and setup 0.761544 s, so a frozen own-process query profile is the existing Coordinator's first-ranked diagnostic before base/query co-design. Ordinary binary first needs its own complete baseline.

For m factor-base summands plus a target, a direct summation polynomial is `S_(m+1)`. Direct `S_8` means seven summands; eight summands require `S_9`. A chain of `S_3` constraints is a separate formulation. Each attempted construction and resource stop must be recorded.

A qualifying improvement needs unseen same-point targets, target-blind base selection, matched baseline and rho, full cold or genuinely amortized S, memory, independent replay, and a machine-readable progress-fidelity claim. The named implementation and measurement obstruction is `problems/full-width-ic-arity-grid-unmeasured.md`. This assessment leaves canonical scientific graphs unchanged.
