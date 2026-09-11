# EXP-ECRANK-52d039 implementation note

The run package uses the stdlib-only producer in `source/producer.py`, an
independent stdlib-only verifier in `source/verifier.py`, and the bounded
three-run launcher in `source/run_experiment.py`. The verifier does not import
the producer. It reconstructs the frozen abstract matrices and interval LDL
factorisation, the named long-Weierstrass curve arithmetic, the exact rational
height enclosure, the exact C(E) derivation, and the R2 enclosure and pivot
records from the declarations and producer output.

The launcher invokes the producer and verifier in separate fresh Python
processes, preserves producer and verifier stdout/stderr, writes the required
run companions and nested `run:` manifests, then launches R3 as fresh-process
replays of R1 and R2. Replay comparison removes only operational timing fields;
verdicts, exact rational values, witness fields, and verifier reports remain in
the compared payload.

The producer's machine-protection guard is operational instrumentation, not a
protocol change. If exact coordinate growth reaches that guard, the run is
recorded as `failed_infrastructure` with its stop reason and raw partial
output. No result is inferred from that stop and no frozen input is amended.

No protocol fields, hypothesis status, ledger status, evidence, decision, or
approval record are changed by this implementation. The Coordinator owns the
snapshot archive and all later interpretation.
