ECDLP special-structure ledger: bounded pilots and experiment plans

Open report.html for the human-readable report. It includes an embedded coverage
plot and all 23 record dispositions, executed scopes, limitations and follow-ups.
summary.json and all-leads.csv provide concise machine-readable results.
experiment-plans.json supplies corrected hypotheses, steps, controls, measurements,
stopping rules and proposed initial CPU caps for every original record.

All 23 records received a finite pilot or control. This does NOT mean the original
23 full experiment protocols were executed. The JSON result files state exactly
what was measured and what remains unrun. General section coefficient solving,
certified high-rank and number-field descent, full generalized-Jacobian arithmetic,
large lattice/solver sweeps, and CADO polynomial selection remain unexecuted.
No sieving was performed. No deployed keys were used.

The authoritative results come from the resource-capped serial run described in
run-metadata.json. Development-run timings are superseded and are not packaged.
Timeout-bound Z3 outcomes and all timings may change on another machine.
Resolved-case timing comparisons condition on solver completion and do not count
censored cases as failures. No asymptotic exponent is inferred.

Reproduction

1. Use Python 3.12 on Linux in a fresh environment and install requirements.txt.
   For a local package directory, use:
     python -m pip install --target vendor -r requirements.txt
2. Run:
     python run_all.py
     MPLCONFIGDIR=/tmp/snfs-mpl python build_report.py
     python verify_evidence.py

The runner uses one BLAS thread and per-module resource limits: 240 CPU seconds
(soft), 300 wall seconds and 3 GiB address space. It runs modules serially and
records versions, source hashes and measured CPU/wall time. The reported RSS is a
high-water mark over completed child processes, not an isolated per-module peak.
The CPU and address-space limits apply per process and are inherited by workers;
the module wall cap bounds the whole module. Case-specific caps (Z3 one second;
lattice worker five seconds) are in the code.

The vendor directory is excluded from the archive; pinned requirements identify
the downloaded solver packages. The scripts otherwise use ordinary Python,
NumPy/SciPy/SymPy and Matplotlib. No pilot code makes network calls.

Inputs and identity

The original source ledger, normalized ledger, intake manifest and mathematical
audit are included under inputs/. Original hypothesis fields are retained.
Immutable hypothesis IDs remain unassigned. Provisional IDs have not been renamed
and no registry collisions have been claimed resolved. Seeds derive from local
staging candidates with a fixed namespace and case label; they are unique locally
but have not been reserved against the unavailable campaign registry.

Evidence boundaries

Original theorem-closed records retain receipt-only eligibility. A selected toy
family, a planted instance, an oracle-assisted search, an algebraic identity, or a
failed weak prototype does not establish subexponential ECDLP or a universal
obstruction. Oracle and blind methods are distinguished in every surface result.
Single-target cold costs and amortized costs must not be interchanged.

E3 remains the best open solver question after these pilots; it is not a
demonstrated faster attack. A revised compositional-factor-base A3 is second.
D4's original smoothness/kernel independence trigger must be retired because
B-smooth(W), W nonzero, and B<p imply p does not divide W.
