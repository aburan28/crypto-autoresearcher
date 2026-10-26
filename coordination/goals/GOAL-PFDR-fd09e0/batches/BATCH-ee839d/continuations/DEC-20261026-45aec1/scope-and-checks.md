# CPU receipt correctness only

Pinned owner base:27fca7749299469bd93bad3a1eed8e7e6a3b6a75. The continuation
repairs software accounting, not admission authorization, algebra, failure
semantics of None/zero shifts, a mathematical hypothesis or attack performance.

Observed source: supervisor.hpp serializes tv_sec+'.'+unpadded tv_usec;
backend.hpp and cdd_ipc.hpp waitpid without usage; pipeline.hpp logs worker-only
std::clock. These observations do not require a scientific call. Existing cuso
semantics, prior reviewed native construction and frozen24-call plan stay intact.

Implement checked integer microseconds (sec*1000000+usec); validate range/overflow.
Add explicitly versioned usage receipt semantics, e.g.native-smallroot-cpu-v2.
Use wait4 for actual backend/helper reaping and retain status+user/system us
before any failure/codec exception. Preserve EINTR behavior and actual failures.
Record phase RUSAGE_SELF and RUSAGE_CHILDREN user/system deltas with their exact
scopes; on failure/unavailable counters record unknown, never invented zero.
Individual child receipts are diagnostics, never an extra addend to the already
counted phase waited-child delta. Full phase process-tree CPU remains unknown.
Any retained decimal-second fields must have correct six-digit microsecond
scaling and a version marker. Preserve published old receipts and output fields
needed for interpretation; no relabeling old values as corrected observations.

Root has acquired actual workspace-local T-2 reservation for the native
directory and today log; safe receipt is owner-reservation.json. Recheck its
live lease and exact task scope before edits. Append only today's project log; preserve
previous entries and exclude secrets/transcripts. No unrelated Rust repair.

The17 expected fixtures in expected-fixtures.json are fixed before checks.
Producer also seals the exact owner expectation source/hash before invoking
fixtures. Add a dedicated native cpu-accounting fixture target/helper, compile
with warnings as errors and run only these software fixtures. Fake children
return controlled codec/statuses and never interpret Singular/cdd scripts.
Do not invoke actual CAS, ideal/closure/bound/interpolation, D-sign, calibration,
root search, parameter search, approved-panel or cgroup supervisor entrypoints.
Pure formatter tests exercise supervisor receipt formatting without launching
its guarded workload. No production test bypass or environment escape hatch.
Update the stale README lines76-78 CPU paragraph only, preserving its warning
that full phase process-tree CPU remains unknown.
Dynamic OS CPU values need not be positive or match a prescribed timing; verify
units/nonnegative measured values and receipt/counter relationships, not speed.

Build main source and the new native tests in a fresh explicit BUILD directory;
add only the scoped Makefile target. Keep exact commands, stdout/stderr, exit/
signal, source/expected hashes and failed attempts in the new owner check dir.
Do not edit dependency locks or old check artifacts unless a separate scope
amendment is first published. No new dependency is planned.

Actual upstream Cargo attempt7 at this base exits101: unclosed delimiter in
src/cryptanalysis/binary_semaev_chain_sat.rs:1648, missing close near line628.
Blob3803524139ef5382d85f835107339d66d5909a6d matches HEAD/origin/main as
reported by parent. Log SHA256c5c5cf1a7ee6b111b654532f5e94d28a09453219696205221acd2cdaf935be14.
This unrelated Rust failure does not block the standalone C++ repair/build.
Report it honestly; do not claim a current clean library suite. Earlier b02
4862/0/121 is historical and must remain tied to that tree. Hosted Actions also
fail before running for account availability; no merge/check bypass is allowed.

After owner code publication, independent Reviewer checks unit conversion,
waited-child coverage, failures and no-double-count using the canonical plan.
Its attestation must use joints_owned:[cpu-units-coverage-and-failure-retention],
sources_read list, read_sibling_reports:false, blind_from_respected:true and
verdict holds|breaks|inconclusive. These instructions are prospective, not an
attestation. No scientific or global readiness claim may be inferred.
