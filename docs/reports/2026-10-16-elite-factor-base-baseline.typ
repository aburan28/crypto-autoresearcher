#set page(paper: "a4", margin: (x: 16mm, y: 11mm))
#set text(font: "Arial", size: 8pt)
#set par(justify: true)

= Index-calculus baseline and factor-base search boundary

2026-10-16 · Source-linked assessment; no new scientific trial or speed claim. Corrected after PR #2309: tuple count and wide-entry size. The complete report and its source links are in `2026-10-16-elite-factor-base-baseline.md`.

#image("2026-10-16-elite-factor-base-baseline.svg", width: 90%)

== Measured baseline

*Koblitz GF(2^53).* RUN-KIC-e3dbed used 24 held-out public known-answer targets, one cold process per IC/rho arm. The median paired IC/rho wall ratio was *3.511028* (bootstrap 95% interval [2.757893, 6.672955]); IC median process wall was 4.787709 s and signed-Frobenius rho median was 1.324306 s. An independent review checked the finite comparison. RUN-KIC-8b5038, on 24 different fresh targets, measured a 0.870771 candidate/baseline wall ratio after doubling active hash slots, while peak RSS ratio rose to 1.762315. Its candidate/rho paired wall ratio was 3.561202. These panels must remain distinct.

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

The prime-field sparse-subgroup equation helped one m=2 algebraic cell but not m=3; complete small-scale relation supply was similar for size-matched small-x, random and subgroup bases. The next comparison pairs base and equation formulation, measuring construction, monomials, observed solving degree, misses, verified rows, useful rank, final solve and blind target work. The Koblitz N53 query kernel and support setup are the measured first optimization targets. Ordinary binary first needs its own complete baseline.

For m factor-base summands plus a target, a direct summation polynomial is `S_(m+1)`. Direct `S_8` means seven summands; eight summands require `S_9`. A chain of `S_3` constraints is a separate formulation. Each attempted construction and resource stop must be recorded.

A qualifying improvement needs unseen same-point targets, target-blind base selection, matched baseline and rho, full cold or genuinely amortized S, memory, independent replay, and a machine-readable progress-fidelity claim. The named implementation and measurement obstruction is `problems/full-width-ic-arity-grid-unmeasured.md`. This assessment leaves canonical scientific graphs unchanged.

== Sources

Internal, retrieved from committed checkout: `research/cold_single_ic_20260921/REPORT.md`; `research/cold_capacity_ic_20260921/REPORT.md`; `src/crypto_autoresearcher/index_calculus/README.md` §§1–5; `research/conductor_relation_yield_20261014/OBSTRUCTION.md`; `research/factor_base_lab.md`. The Markdown report links each at its relevant claim.
