# Point coverage and useful relation measurement

User-authorized additive follow-up to EXP-ECDLP-4c6a09. See plan.json and the
information-sharing addendum shared-relations-plan.json. Original coverage,
rank records and specifications remain immutable.

The principal result is benchmark-shared-attempt-01/raw-result.json: two toy
rational models, three common Solinas reduction primes, six subgroups, 16
synthetic targets per subgroup, and 90 method configurations. Shared generator
constraints are counted by global modular matrix rank, not by duplicate hits.
All 96 Solinas target recoveries were verified. The declared generic BSGS controls
used less group work in every cohort. This is a scoped comparison, not an ECDLP
complexity bound, a deployed-curve result, a negative result for every possible
algebraic relation, or a status promotion.

benchmark-attempt-01 is a separate cold-target boundary: each target resets its
generator-log constraints. Its relation counts are per isolated system and must
not be read as global batch rank. The additive shared phase reuses information
and one common query jump. No point set, target sample or watchdog cap changed.

point-preparation-attempt-02 contains exact number-field additions followed by
reduction, and three timing repetitions. Every full-group point was checked
against a second, cached finite-field generation. The first preparation attempt
failed on PARI's degree-one finite-field element type; its complete scripts,
logs and source snapshot are retained. The correction converts that element by
its degree-one trace. GP exit code zero alone is never accepted as success.

Costs count finite-field additions/doublings, inversions and multiplications
separately from modular relation algebra and verification. Group-call totals
include seed projection/construction, table building and all target queries.
Number-field additions are not equated to finite-field additions. CPU timings
include instrumented checks; exact-K timings include coordinate-bit measurement
and reductions include row output in the first repeat. Timings are observations,
not portable bounds. Prior rank/seed-discovery times remain separately recorded.
Synthetic scalar truth is reserved for validation; solver functions receive
public target points and permitted known seed labels only. These inputs are
public toy objects, not wallets or deployed NIST curves.

An isomorphic sign-control transports alpha=-beta and gives identical reductions,
coverage, relation ranks and recovery counts. It is not an independent field
sample. The random low-weight control has no degree-one reduction at two matched
primes, recorded as four unavailable model/prime comparisons. No replacement
prime or field was selected after inspecting outcomes.

Reproduction uses the retained source and PARI/GP 2.17.2 runtime. Copy to fresh
run/output locations; never overwrite completed records. Execute
rank_preparation.py, prepare_tables.py, benchmark.py, then shared_relations.py
with the exact recorded inputs and phase source snapshots. The driver source
uses the archived run-relative layout and selected local GP library paths.
See every phase launch.json and per-instance input.gp for exact commands.
GP source/provenance and GPL-2 license are retained. No independent review,
ledger transition, frontier update, GitHub push or PR occurred in this follow-up.
