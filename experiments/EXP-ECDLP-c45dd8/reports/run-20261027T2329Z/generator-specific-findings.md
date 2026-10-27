# Generator-specific scalar recoveries

Two fixed x-sensitive circuits returned the correct ordering bit for all13 targets for selected generators of the public curve y²=x³+x+6 over F11, of order13. The frozen independent verifier confirmed every fresh recovery trace.

| alpha | beta | Passing generators in the original coordinate model |
|---|---|---|
|1|-4|(3,5), (3,6)|
|-2|-1|(7,2), (7,9), (10,2), (10,9)|

Each of these six circuit/base pairs also passed in all10 predefined coordinate views. The60 passing groups produced780 verified scalar recoveries and3900 fresh predicate evaluations, five per target. Those totals include repeated coordinate views. The candidate never received scalar truth or a log table. The public all13-target gate, fresh setup, fresh evaluations and final public checks are charged separately; the gate uses O(r) work. Full tested-generator coverage remains0/40 templates; both the successful and failed domains are retained.

The next comparison keeps these two circuits fixed and tests larger, distinct curves and new public generators, with a declared generator-selection rule and its cost. A replacement base must be P'=aP with known public a, so a recovered x' converts to x=a x' mod r and is checked publicly; selecting a favorable unrelated base would hide another discrete log. Choosing coefficients after seeing that next panel would create a different exploratory study. This finite result is a working baseline on the named toy domains; it supplies no complexity exponent on larger domains.

A separate prospective arm can attempt five fresh predicate bits without the exhaustive gate, form a scalar candidate, and check it publicly on every attempt. That would measure success probability and complete cost per success against uniform-candidate and working solver baselines. It requires a new source/protocol; the completed gated observations are preserved as measured.
