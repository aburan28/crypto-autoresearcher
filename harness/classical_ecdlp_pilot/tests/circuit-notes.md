# D and L4 implementation/development checks

Owner: implementation collaborator; 2026-10-25. No scientific `--run` invocation was performed by this collaborator. All outputs below are development self-tests, not accepted hypothesis results or a novelty/performance claim.

Final `src/circuit.cpp` SHA-256: `eae378ee807498f8550614e1e2ed26967f669319dd8b653817af1f4e206aea3a`.

## Implemented D instrument

The compiler constructs a strictly topological Boolean DAG from public curve/base/subgroup parameters. Its primitives are constants, assigned input bits, AND, XOR and NOT. Ripple addition/subtraction/borrow, conditional selection, modular multiplication by repeated add/double, and inversion by the public Fermat exponent implement field arithmetic. Point addition/doubling select identity, inverse and zero-y branches explicitly. Full point encodings include an infinity flag and canonical zero coordinates at infinity. Scalar range is tested before the target indicator is accepted. The compiler uses no scalar lookup table or supplied k.

Every gate has one uniquely determined value once inputs are assigned. Induction in gate order establishes unique internal extensions of the gate equations; malformed backward references are rejected by construction. The mutation tests are finite regressions for the witness checker, not a formal proof assistant result. `cnf_clause_count_if_tseitin_encoded` counts the corresponding primitive gate clauses; it excludes extra units asserting the target predicate or fixing input bits, and no CNF file or SAT solver was invoked.

For every fixture, all scalar bit words are evaluated, including words outside `[0,r)`. Every full-curve target is checked and the parity/tag response is compared to the canonical scalar truth. The reference orbit is enumerated and charged as instrumentation; it is not used to build the forward Boolean circuit. Malformed infinity, out-of-range coordinates and a canonical off-curve point are rejection controls. Input points to one/two-step blocks range over the entire rational curve, including identity, inverses and rational 2-torsion if present. Each local word's unique output is checked, then every full-curve outgoing boundary's constant and tag coefficients are compared with the known fixed-window control. Invalid block inputs are explicitly flagged; arbitrary invalid bit encodings are outside the valid-coordinate composition invariant.

Gate nodes, actual evaluated gate counts, witness mutations, scalar/target/boundary cases and tagged cells with zero constant coefficient are recorded. These counters do not charge host-side reference/certification arithmetic as gate evaluations; the runner's complete process time/storage includes that work. No EC-specific cancellation identity beyond known fixed-window arithmetic was invented. No low-width elimination, unknown-scalar recovery construction or complete solver gain is claimed.

## Implemented L4 finite grammar

Enumerate all 81 rational 2-by-2 matrices with entries in `{-1,0,1}`, retaining the 48 invertible matrices. Each directed output leg transforms by M, each input leg by its inverse transpose; 192 exact wire-contraction checks verify preservation. Test the fixed ordered signatures AND, XOR, NOT, COPY, EQUALITY, CONST0, CONST1 and FULL_ADDER. Every signature is checked for parity support and every Grassmann–Pluecker identity indexed by alpha/beta. Exact rational arithmetic uses reduced signed 64-bit fractions with checked multiplication/addition overflow; it performs no floating-point rank or numerical tolerance test. The domain is this bounded grammar, not arbitrary large coefficients.

Calibrations include equality, a three-leg odd matchgate, a nontrivial four-leg Pfaffian signature with pair coefficients `(1,2,3,4,5,6)` and full coefficient `8`, a four-leg exact Pfaffian violation, mixed parity, and frozen seeded random even/mixed negative signatures. The total is 199 calibration checks. The common-basis search checks 60,288 identities and has zero all-signature survivors; AND fails parity in every arm. Every rejected arm is preserved in the JSON row with its matrix, first failing signature, two exact nonzero even/odd coefficient witnesses, and a nonzero identity residual where present.

This rejects only the specified common-basis primitive-gate grammar. It does not close per-wire bases, larger coefficients, different tensor groupings, alternate leg orders, target-specific simplification, other coefficient domains or all matchgate ideas. A global planar realization and tag/rational-to-characteristic-two adapter remain absent. The original IC-specific proposal is not executed.

## Final development commands and outputs

Both final builds exited 0 and produced byte-identical JSONL outputs (11,847 bytes):

```sh
set -e
g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -Wconversion -Wshadow -Werror \
  src/circuit.cpp -o /tmp/classical-circuit-final-v3
/tmp/classical-circuit-final-v3 --self-test > /tmp/classical-circuit-final-v3-selftest.jsonl
g++ -std=c++20 -O1 -g -Wall -Wextra -Wpedantic -Wconversion -Wshadow -Werror \
  -fsanitize=address,undefined -fno-omit-frame-pointer src/circuit.cpp \
  -o /tmp/classical-circuit-final-v3-sanitized
ASAN_OPTIONS=detect_leaks=0 /tmp/classical-circuit-final-v3-sanitized --self-test \
  > /tmp/classical-circuit-final-v3-sanitized-selftest.jsonl
```

Leak detection was deliberately disabled for the known environment limitation; no leak-check pass is claimed. The compiler is g++ 14.2.0. Commands run with the lab root as logical source root; actual compilation used the absolute `src/circuit.cpp` path.

| Fixture | Gate nodes | Scalar words | Target cases | Tagged boundary cells | Corrupt gates rejected | Zero-parity/nonzero-tag cells |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| p=5, r=3, N=6 | 1,041 | 4 | 24 | 72 | 66 | 6 |
| p=17, r=19, N=19 | 69,307 | 32 | 608 | 722 | 65 | 0 |
| p=23, r=7, N=28 | 42,325 | 8 | 224 | 1,568 | 65 | 0 |

All field addition/subtraction/multiplication/inversion pairs over F17 are separately checked. All three fixtures are non-anomalous; p=5 is a special-j/cofactor/2-torsion exception control. The r=3 two-bit window supplies an exact case where parity cancellation alone loses a surviving tag.

Earlier development attempts are not final-source validation: Boost headers were unavailable; a checked local rational type replaced the dependency. Strict builds found a misleading-indentation warning and an inconsistent `auto` declaration, then one further misleading-indentation warning after adding failure witnesses; those were fixed. One pre-final shell command lacked `set -e` and invoked a stale existing test binary after compilation failed; that replay is not attributed to the final source. Final commands above use new binary names and `set -e`. Additional intermediate builds passed before the final extra calibration; their counts/hashes are superseded, not scientific evidence.

Public interface: `circuit --self-test` or `circuit --run FIXTURES_TSV OUTPUT_JSONL`. Scientific/pilot execution is reserved to the root's frozen protocol and runner. One D row is emitted per certified fixture; one L4 row covers the shared fixed grammar. No nested parallelism is used.
