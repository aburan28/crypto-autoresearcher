# Explicit rationality circuits for complete signed charts

Implementation task TASK-20261031-112610. This component represents the reviewed nilpotent, slack and guard predicates as explicit quadratic field equations. It includes the F1 correction: an auxiliary square-root sign must not determine an unbalanced signed divisor.

`circuits.py` stores a polynomial as a dictionary from sorted variable-name tuples to coefficients while building. Exported equations use lists of `{coefficient, variables}` terms. Repetition of a name means its exponent (two repeats are a square). Terms, variable roles, local projection and obligation ownership are explicit. Fixture values are held in a separate assignment and never substituted into the exported equations. No degree or residual annotation is trusted by the checker.

`rationality.py` exposes `nilpotent_square_block(k,p,a,b,U=None,C=None)` and `linear_B_square_block(p,a,b,mode,A=None,B=None,beta=0)`. They return a circuit and a supplied-value assignment. An assignment may intentionally fail its equations; this supports fixed negative controls and is not an existential search. Modular-product quotients and remainders remain explicit, including zero values. The degree-one quotient is handled by the dedicated evaluation lift. The constant-nonzero B branch checks an inverse; zero B uses nilpotent rationality.

`construct_auxiliaries_from_checked_chart` requires supplied checked points. It interpolates C at distinct known support coordinates or supplies a known common-root ordinate. It never scans the field for a relation or square root. Signed recovery uses the archived residual-ratio mechanism, with root lifts only for balanced support. The interval and public target remain separate.

`checker.py` imports no circuit-builder arithmetic. It parses every IR field and every assignment before evaluation, derives total degrees from the monomials and recomputes all residuals. The caller supplies expected public parameters, input values and projection independently. Candidate chart checking binds normalized A/B, U, target, interval, k and B stratum, verifies membership/splitting and signed reconstruction. `reference_check` separately invokes the frozen full Euler/local-series checker; it is never substituted for candidate equation evaluation.

The IR is a field circuit, not a Boolean SAT instance. Prime p>3 is an explicit premise, and nonsingularity is checked. Complete finite-field bit ranges, carries, SAT transcript coverage and comparative solver work are subsequent obligations. Counts concern this rationality block only. No degree-of-regularity, timing or novelty claim follows from quadratic generators.

Software evidence is recorded in software-results.json. Read its actual attempt status; this README does not predeclare a passing result. All attempts, source snapshots, failure details and hashes are retained there. The prescribed suite has at most four attempts with a 240-second watchdog; no solver, random census, benchmark or remote job is authorized. Later independent software review uses its own evaluator and assertions.

The separate squarefree-stratum proposal is not implemented here. Existing source modules and the frozen four-arm contract remain unchanged.
