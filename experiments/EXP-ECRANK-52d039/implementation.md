# EXP-ECRANK-52d039 implementation

Stdlib-only producer (`source/producer.py`) and an independent stdlib-only
verifier (`source/verifier.py`) that does not import the producer. The
launcher (`source/run_experiment.py`) runs producer and verifier in separate
processes, writes the nested `run:` companions, and dual-writes each run
directory to the handoff path `runs/RUN-ECRANK-52d039-R*` and the
BATCH-a9c273 queue path `runs/R1-abstract-gate` (and the R2/R3 analogues).
Paired files are byte copies.

Arithmetic is `fractions.Fraction` throughout the verdict path. Floating
point appears only in the R2 comparison-only regulator cross-check and is
never read into a verdict. Logarithms used on the verdict path are
certified rational intervals (artanh series with an exact remainder bound).

R2 machine protection follows the frozen caps only: 3600 s wall per run and
8 GiB RSS. There is no counted-op cap and no extra bit-size stop. If the
loop cannot reach `n_max = 60` inside those caps, the run is recorded as
`failed_infrastructure` with the stop n and coordinate bit sizes. That
stop is not a mathematical result.

No protocol field, hypothesis status, ledger status, evidence, decision, or
approval record is changed by this implementation. Observations only.
