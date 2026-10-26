# Input-preparation development checks

This is input preparation and fixed arithmetic development, not scientific solver measurement or independent-session review.

- Final strict build: `g++ -std=c++20 -O2 -Wall -Wextra -Wconversion -Werror src/prepare_cohort.cpp -o work/prepare-cohort`.
- `--self-test`:1,985 checks passed. These compare root-frequency, Euler and direct point enumeration on fixed tiny nonsingular curves; check fixed affine scalar arithmetic and factor selection; and reject a noncoprime cofactor case.
- Sanitized build: the same source with `-O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer`; `ASAN_OPTIONS=detect_leaks=0 ... --self-test` passed all1,985 checks. Leak detection is disabled because the managed host does not provide reliable leak-sanitizer operation.
- The final wrapper independently certified all48 accepted cardinalities and base-point orders, checked all768 public targets without reading private labels, checked exactly192core/576extension tags and reconstructed all2,094 history rows byte for byte.
- `final-input-consistency.json` records the read-only post-preparation source-hash, subset and history checks. Final source bytes still match the pre-target seal. Thirty curves admit the fifth-power feature; this is an input applicability count, not a measured solver outcome.
- The four separate development fixtures have independently matching Python Euler cardinalities; their16 edge scalars are intentionally public and do not enter confirmation.

Development attempts retained in session history include an initial warnings-as-errors failure from copying a range-loop fixture value (repaired to a const reference before successful generation), and two inline Python development-control syntax mistakes that failed before executing any code. Neither changed final source/input bytes, scientific results or private commitments. The completed24×32 input-only preparation is preserved separately and explicitly superseded by the final48×16 preparation.
