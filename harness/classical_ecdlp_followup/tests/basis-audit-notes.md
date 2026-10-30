# Basis-audit implementation and development checks

25 October 2026. Files owned by this implementation task are `src/basis_audit.cpp`, this note, and `theory/pin-obstruction.md`. No prior source, sealed pilot data, ledger status or scientific run is changed. The CLI `--run FIXTURES_TSV OUTPUT_JSONL` is reserved to root's source/protocol freeze and admitted execution. The grammar audit is global and curve-independent; the fixture argument is checked for existence/nonemptiness and does not supply hidden scalars.

## Implemented domains

- Exact reduced signed-64 rational arithmetic with checked product/sum/normalization overflow; no numerical rank or tolerance test.
- All625 matrices in [-2,2]^4 before singularity filtering:496 invertible arms,16 AND-only survivors,32 both-pin parity survivors,0 joint pin/AND survivors. All48 old coefficient-bound-one arms remain explicit checks.
- All6 uniform GL2(F2) matrices and216 independent leg triples; no parity-pure AND result.
- All96 uniform invertible matrices over F2[e]/(e²); no parity-pure AND result.
- Twenty-variable **ordinary** F2 polynomial expansion of the determinant covariance identity. Both normal forms contain32 monomials and the residual is zero. No x²=x reduction is used.
- Positive rational AND basis [[1,2],[1,0]], negative mixed CONST0, full wire/inverse-transpose checks, known Pfaffian/XOR signatures, a corrupted Pfaffian, a wrong wire convention, and a two-parity-summand AND representation.

The written derivation states why the finite pin result extends to arbitrary fields and why the symbolic identity covers nonzero commutative characteristic-two rings with unit determinants. It does not infer those statements from finite examples. The result applies to a specified local representation and is not an ECDLP complexity theorem or novelty claim.

## Output contract

Track `L4-audit`, fixture alias `shared_basis_audit`, scope `exploratory_toy_followup`. Exactly504 JSONL records are emitted:496 `per_basis` rational rows,6 `per_basis` F2 rows,one `symbolic_identity_certificate` andone `summary`. Each rational arm contains its integer matrix, rational determinant, both pin vectors, all8 transformed AND coefficients, parity/identity flags and first mixed tensor. The symbolic row records both32-term monomial lists with a full variable order and ordinary exponents. Independent-triple and single-tag controls are summarized rather than emitting additional rows. Every line is below60KiB.

`complete_valid` is an instrument-completion label. `joint_candidate_passed:false` is the separate outcome for the candidate basis model. The rational-only AND survivors are retained and not hidden by the joint obstruction. No full graph planarization, global Pfaffian decoder or characteristic-zero-to-tag-ring adapter is assumed.

## Commands and limitations

Compiler: g++14.2.0. Strict builds use C++20 with `-Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror`.

```sh
g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -Wconversion \
  -Wsign-conversion -Wshadow -Werror src/basis_audit.cpp \
  -o /tmp/classical-followup-basis-audit
/tmp/classical-followup-basis-audit --self-test
g++ -std=c++20 -O1 -g -Wall -Wextra -Wpedantic -Wconversion \
  -Wsign-conversion -Wshadow -Werror -fsanitize=address,undefined \
  -fno-omit-frame-pointer src/basis_audit.cpp \
  -o /tmp/classical-followup-basis-audit-sanitized
ASAN_OPTIONS=detect_leaks=0 /tmp/classical-followup-basis-audit-sanitized --self-test
```

Leak detection is explicitly disabled for the previously observed tracing limitation. Address/undefined-behavior instrumentation remains enabled. No leak-check success is claimed. No Lean executable is installed in this environment; no proof-assistant validation is claimed. A same-session read-only mathematical check supplied feedback, not a formal independent review.

The initial strict compile rejected two misleading-indentation layouts. Those were corrected. The initial shell lacked `set -e` and then attempted a nonexistent test binary; it exited127 and executed no binary. Later commands use `set -e` and distinct fresh binary names. An intermediate12-calibration source passed before adding the two-summand countercontrol; the final suite has13 calibrations. No intermediate run is attributed to final source bytes.

Final compiler/sanitizer/serialization receipts and source digest are appended below by this task before root freezes the source. Development `--self-test` exhausts this fixed algebraic grammar for instrument regression; no scientific `--run` of the new cohort was invoked.

## Final checked bytes

Final source SHA-256:
`6ebb3c621c9e500e91e8f9305eac2ff9a17860e389830edba4bb37cfac38f1ba`.

The final normal binary `/tmp/classical-followup-basis-audit-final-v5` and ASan/UBSan binary `/tmp/classical-followup-basis-audit-final-v5-sanitized` both exited0. Their identical self-test summary is:

```json
{"status":"pass","scope":"development_only","q_invertible":496,"q_and_only_survivors":16,"q_pins_and_survivors":0,"f2_uniform":6,"f2_independent":216,"single_tag_uniform":96,"symbolic_identity_terms":32,"symbolic_residual_terms":0,"calibrations":13}
```

A development-only serialization helper compiled this same source through an alternate main and called `audit::audit` on an output string stream; it did not invoke `--run` or use a curve cohort. Standard JSON parsing checked all504 lines, exact field/row-kind coverage, the two equal32-term certificate lists, ordinary degree8 and the empty residual. Both the normal helper and an ASan/UBSan helper exited0 and their complete output bytes matched.

- Output bytes:258,331.
- Maximum JSONL record:2,149 bytes (below60KiB).
- Output SHA-256:`41b3bc6a83b8df4a8f8ecc055b97c4dd51efaca29c5c4f721e208c6d2967ba54`.
- Temporary outputs:`/tmp/classical-basis-serialization-unit.jsonl` and `/tmp/classical-basis-serialization-unit-sanitized.jsonl`.
- Recorded ordinary polynomial certificate:20 variables,32 monomials on each side,degree8 per monomial,zero residual; no Boolean exponent reduction.

The helper uses `#define main basis_original_main` around inclusion of `src/basis_audit.cpp`, then `std::ostringstream s; audit::audit(&s); std::cout<<s.str();`. It changes neither production code nor its semantics. These outputs are implementation regression evidence; the root's later frozen admitted run supplies the scientific archive.
