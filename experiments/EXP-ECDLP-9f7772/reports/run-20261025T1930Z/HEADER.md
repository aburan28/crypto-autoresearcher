# Larger classical ECDLP solver-validation report

AutoRho, Bernstein–Lange and BSGS each returned checked answers for all 768 targets. The candidate-then-rho composition also solved 768/768, using 3 candidate-only answers and 765 fallback answers. This observations-only report records correctness and measured cost comparisons without assigning hypothesis status. Novelty remains a separate assessment.

- Experiment: `EXP-ECDLP-9f7772`; run: `RUN-ECDLP-dba66e`.
- Measured source/claim commit: `747b96eed4298d5067976ee33c06426785792c09`.
- Raw records published before this report: `c4b940ac5360e17cb221772f968bab20f67266c3`.
- Verified archive commit: `1822ae0b7247c08dd9062eba62358b8bf19ff728`.
- Workload: 48 fresh ordinary non-anomalous curves, subgroup sizes 12/14/16/18 bits, six curves per size/stratum, 16 uniform targets with replacement per curve: 768 targets. The nested 192-target core overlaps the full panel; extension 576.
- Subgroup orders: 2,141–245,183; field primes: 2,251–491,581. Cofactor counts: `{'1': 11, '3': 11, '2': 26}`.
- Primary preset: x-mod-7, exact public prefixes, beam 8, four offset views, 2,048 unlabelled training samples. This preset was chosen from earlier data, before this fresh confirmation batch. The primary constructor omits unused diagnostics; the full secondary matrix retains them.
- Named references: actual upstream AutoRho and Bernstein–Lange from cryptanalysis commit `379faa0f1e38facd9c8fdfc527f0b89518cf2e70`, plus separately named complete BSGS. Rho A/A and hybrid fallback use the same target-specific random stream and separate charged state.
- Timing: 2026-10-25T19:30:38.606917+00:00 to 2026-10-25T19:31:33.785498+00:00; derived supervisor envelope 55.178581 seconds, including build, controls, measurement and output checking. Module wall intervals under three-worker concurrency are descriptive.
- Compiler: `g++ (Debian 14.2.0-19) 14.2.0`. Exact commands and source/input/binary digests remain in the sealed raw records.
- Verification: 15,744 candidate/final/prefix cases aligned to separately coded Jacobian verification and replay. This is implementation diversity, not an independent scientific review session.
- Custody: 2,882 receipt artifacts, 2,560 producer slots and all six original streams checked by hash/length; 1041 occupied producer slots. No sealed file was changed.
- Private synthetic scalar labels and generation seeds were not read by this analysis. Source-enforced input separation is not OS-isolated blindness.

The [earlier compiler-stopped attempt](../../../EXP-ECDLP-381959/reports/run-20261025T1906Z/HEADER.md) is reported separately. It dispatched no confirmation measurement jobs; this report covers the successful successor only.

[Report PDF](report.pdf) · [Complete observations](observations.md) · [Machine summary](data/summary.json) · [Runtime](data/runtime.json).

Editable figures are supplied as SVG/PDF pairs: [solver recovery](figures/solver-recovery.svg), [CPU costs](figures/cpu-costs.svg), [paired ratios](figures/paired-ratios.svg), [hybrid stages](figures/hybrid-stages.svg), and [execution timeline](figures/execution-timeline.svg). The small scatter offsets distinguish overlapping recorded values; they are not additional observations. `bash build.sh` rebuilds the document and figures from retained extracts and executes no EC experiment.

Rendering requires Python, NumPy, Matplotlib and PyMuPDF. Lossless PDF object compression preserves every rendered page pixel-for-pixel. Every report page and figure PDF is visually inspected before publication. All PDFs remain below 64KiB; renderer caches and inspection PNGs under `.inspection/` are not publication artifacts.
