# Pre-freeze software correction

The first marked p101 test run completed three tests and failed one deliberate
corruption test. Setting the first cancellation weight to1 could leave it
unchanged or provide another valid certificate, so rejection was not guaranteed.
The test now perturbs the retained RHS by1 modulo the subgroup order, a
guaranteed invalid carried equation. The collector was unchanged by that test
correction. Standalone checker source-scalar/constraint-index guards and an
explicit elimination-allocation size gate were added before any native data.
No p4099 pool, witness or experiment was generated in these software checks.

The coordination full-ledger command refused because104579 tracked records are
off disk in this sparse checkout. This is not a passing full-ledger validation;
no ledger state is added or changed by the standalone PhaseB study. Native
source/input/protocol/release/checkpoint correctness guards remain mandatory.
