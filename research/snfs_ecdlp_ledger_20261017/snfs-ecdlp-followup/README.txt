Special-structure ECDLP: selective follow-up, 2026-10-17

Open report.html. summary.json, all-lead-dispositions.json and next-experiments.json
give the evidence, all-23 disposition update and unrun gated experiments.
The earlier 23-record report and corrected plans are in the sibling directory.
The original full campaigns have not been executed. No asymptotic gain is claimed.

Reproduce in Python 3.12 on Linux, from the common parent directory:
  python -m pip install --target snfs-ecdlp-experiments/vendor -r snfs-ecdlp-followup/requirements.txt
  OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python snfs-ecdlp-followup/norm_decomposition.py
  OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python snfs-ecdlp-followup/norm_decomposition.py flint
  OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python snfs-ecdlp-followup/norm_decomposition.py flint extended
  OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python snfs-ecdlp-followup/blind_sections.py
  OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python snfs-ecdlp-followup/geometry_sections.py
  python snfs-ecdlp-followup/verify_followup.py

Run-metadata describes actual resource limits; the extended norm wrapper recorded
48 CPU seconds. Direct CLI reproduction does not install an outer resource cap.
E3 workers always enforce their own wall, CPU and address-space limits.
Timings and timeout outcomes may vary. Compare native arithmetic, cold and shared
setup separately. The two small norm grids repeat the same instances and are not
independent scientific samples. First-round files remain immutable.
