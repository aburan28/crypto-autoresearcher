# EXP-CERTBIN-060020 verifier/

`verify_n19.py` is the separate-process verifier of specification
`object.verifier` (V1-V6). It imports only the standard library, numpy and
PyYAML. It imports nothing from `impl/`, from `crypto_autoresearcher` (any
module), from any archived impl/ or from any review directory. It asserts
this at start and at exit.

Its components are its own, written independently of impl/:
- field arithmetic by schoolbook multiplication and Fermat inversion;
- the S_3 descent by a hand-derived closed form;
- exhaustive s by full-width bit-sliced truth tables;
- the x(2E) test by an x-only Lopez-Dahab ladder;
- the arm replays with numpy 2.4.6 PCG64;
- multilinear certificate arithmetic;
- GF(2) elimination and float32 BLAS products mod 2 for ann-v1.

Outputs (in the run directory):
- certificate-verification.json (V4, C-CERT)
- annihilator-verification.json (V6)
- construction-verification.json (V1, V2, C-ORACLE2)
- draw-replay-verification.json (V3, C-DRAW)
- negative-controls-verification.json (V5, C-VERIFIER)

The verifier is code-independent of the engine and of impl/. It is NOT
author-independent of impl/, because the same executor wrote both.
Author-independent verification is the review round's.

    python3 verify_n19.py --run RUN_DIR --spec SPEC --out RUN_DIR

`--quotas` and `--seeds` exist for development dry-runs only.
