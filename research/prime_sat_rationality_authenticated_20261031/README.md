# Additive rationality authentication

Implements TASK-20261031-c68432 under the frozen fixed software contract in coordination/prime_sat_rationality_authenticated_20261031/. The original builders and checker are imported unchanged. The new entry points authenticate the complete circuit against canonical builder output and check the exact outer chart degree before stratum selection.

`canonical_circuit` takes trusted public p/curve/kind/degree/projection, rebuilds symbolic equations with dummy assignments, and discards those assignments. `check_authenticated_assignment` authenticates content before calling the generic evaluator. `check_authenticated_chart` validates outer degree and monic quotient, authenticates the expected block, then delegates residual, membership and signed recovery checks to the frozen chart checker. No caller-supplied circuit metadata serves as the public descriptor.

Prime p>3 remains a caller premise. Canonical builder fidelity remains dependent on the independent symbolic review; content equality is not a new proof of those equations. Event counters separately retain canonical construction/comparison and original evaluator work. No time, solving degree or performance inference follows from them.

`test_authenticated.py` adapts the original producer fixture suite additively, preserving original tests and frozen source bytes, and adds malformed degree and equation-authentication controls. Every attempt is retained in software-results.json. No solver, census, parameter search or remote research job is authorized. Test results and independent review are pending; this README makes no passing claim.
