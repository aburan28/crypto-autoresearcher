# Software validation

The full-space differential test covers 144 deterministic small Boolean-system
fixtures. A separate set-based closure oracle and a highest-bit kernel checker
check the lifted maps. Four Semaev fixtures additionally pass the original
independent checker and match the dense native producer at the lifted degree.
Four constant-image corruptions fail that checker. Native certificate bytes,
inputs and checker transcripts are retained in `native-fixtures-20261029/`.
These are software tests, not measurements on the scientific frontier panel.

The first integration test attempted a field of size 8 and failed in the
original checker's `descend` self-test: it asserts fewer than three of fifty
random triples satisfy S3. That heuristic is unsuitable for such a small field.
The 144 full-space tests had passed in that invocation; the failure occurred
before the first native integration fixture. The integration fixtures were
changed to fields of sizes 16, 64, 256 and 1024 with small variable subspaces.
The checker itself was not changed or bypassed. Both subsequent five-test and
six-test outputs are retained. This is a test-fixture correction, not a repair
or reinterpretation of any archived scientific input.

The capacity profiler also has free-space, all-pivot and randomly thinned
monomial-set tests comparing both enumeration directions. No speed comparison
is inferred from unit-test durations.
