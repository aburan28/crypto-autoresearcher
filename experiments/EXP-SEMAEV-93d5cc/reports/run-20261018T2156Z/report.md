# Matched legacy/repaired `s4_expr` rerun: run report

Observation-only run record for EXP-SEMAEV-93d5cc and its successors EXP-SEMAEV-88c46c and EXP-SEMAEV-6e9dcf (H-SEMAEV-94dab2, GOAL-ECDLP-001). No verdict; the evidence review decides. The typeset version with both figures is [`report.pdf`](report.pdf) (source [`report.typ`](report.typ)); the figures are drawn by [`chart.py`](chart.py) from [`plot-data.json`](plot-data.json).

Runs (all under `experiments/<EXP>/runs/`):

| Cell | Run | Archived run | Status |
| --- | --- | --- | --- |
| icinv-m4 | [RUN-SEMAEV-9cab7b](../../runs/RUN-SEMAEV-9cab7b/) | RUN-ICINV-e0cd8f-m3class (m4 stage) | output_validated |
| fib-004 | [RUN-SEMAEV-3e69b6](../../runs/RUN-SEMAEV-3e69b6/) | RUN-FIB-004 | output_validated |
| fib-005 | [RUN-SEMAEV-4be606](../../runs/RUN-SEMAEV-4be606/) | RUN-FIB-005 | output_validated |
| fib-decision | [RUN-SEMAEV-894e27](../../runs/RUN-SEMAEV-894e27/) | RUN-FIB-006C, -007 ratio, -008 gate | output_validated |
| mtic-007 | [RUN-SEMAEV-2a8498](../../runs/RUN-SEMAEV-2a8498/) | RUN-MTIC-007 | output_validated |
| mtic-008 | [RUN-SEMAEV-fcd67c](../../runs/RUN-SEMAEV-fcd67c/) | RUN-MTIC-008 | output_validated |
| mtic-010b | [RUN-SEMAEV-500a81](../../runs/RUN-SEMAEV-500a81/) | RUN-MTIC-010b | interrupted (container restart), preserved |
| mtic-010b | [EXP-SEMAEV-88c46c RUN-SEMAEV-980e8c](../../../EXP-SEMAEV-88c46c/runs/RUN-SEMAEV-980e8c/) | RUN-MTIC-010b | interrupted (container restart), preserved |
| mtic-010b | [EXP-SEMAEV-6e9dcf RUN-SEMAEV-0e5876](../../../EXP-SEMAEV-6e9dcf/runs/RUN-SEMAEV-0e5876/) | RUN-MTIC-010b | output_validated |

The per-cell values, controls and frozen conclusion fields are tabulated in the PDF. In brief, all recorded:

- **Legacy-arm reproduction control.** It passed in every completed cell, and every deterministic field equals the archive.
- **ICINV.** The repaired S4 changes every m4 record:
  - `s4_support` goes from 227 (225 or 210 on a few records) to 439 (391 on one curve and its gauge twin);
  - the singular-locus degree goes from 60 to 39 on all 552 records;
  - gauge agreement holds in both arms.
- **FIB C16-1.**
  - The repaired solves are about 63 times slower than the legacy rerun, with Groebner bases of 14 to 19 elements against 3 or 4.
  - The C16-1 Spearman rho_s moves from -0.024 (archived) or -0.097 (legacy rerun) to -0.366.
  - The frozen gate outcome is unchanged: no curve passes and RUN-FIB-008 stays cancelled.
  - C16-2 gets 31 capped solves instead of 75 because C16-1 now consumes the run cap.
- **MTIC.** Every attempted solve is capped at 60 s in both arms at 16, 20 and 24 bits, the same as the archive. In MTIC-010b the ablation solves (B = 52: 13 of 13; B = 115: 12 of 12) are all capped in both arms, and regime (i) with K* infinite holds under every accounting at 16, 20 and 24 bits, the same as the archive.
