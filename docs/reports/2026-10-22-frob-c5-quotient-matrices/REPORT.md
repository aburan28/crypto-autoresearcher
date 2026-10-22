# FROB C5 archived quotient Frobenius matrix certificate

The [editable proof graph](proof.dot), [rendered SVG](proof.svg),
[PNG](proof.png), [figure PDF](proof-figure.pdf), and [two-page PDF report](report.pdf)
show the exact algebraic certificate and the remaining code-to-model boundary.
No scientific trial was rerun and no measured speed or attack-cost value changed.
The frozen run is `RUN-FROB-91ee9c-7119f2`.

## Frozen source and theorem

The [frozen C5 source-bound replay](../2026-10-22-frob-c5-factor-kernels/c5-matrix-replay.json)
has SHA-256 `22bcbdbdc6dd8c020456549cb1aa2edf887422cb10912105d9fa0508a6ee1005`.
It binds the three archived output hashes, quotient moduli, q-power matrices,
factor-kernel checks, and replay-checker source hash. The new
[generator](generate_quotient_matrix.py) checks that exact receipt and source
hash, independently divides `X^(q*j)` by each frozen modulus for `j=1,...,4`,
and requires all five remainder coefficients to equal the matching matrix
column. It refuses to overwrite the Lean source and `--check` compares bytes.
A CRLF edit to the Lean source and a changed receipt digest were both rejected;
optimized Python (`-O`) is rejected because the generator uses assertions. A
changed q11 matrix entry was also rejected after recomputing the test receipt's
digest, so the independent division check exercises the values as well as the
byte pin.

The generated [Lean file](../../../formal/CryptoResearch/FrobTrace/QuotientMatrices.lean)
has SHA-256 `9de7bc465a4a12f6e325ddd61b67dd275d8ef6f622307bd2244707aaf081c39b`
at source commit `c685c2951ac3a972a0fc07154609a37540187441`. Its
[formal target](../../../formal/targets/frob-c5-quotient-matrices.yaml) has
SHA-256 `31e5c02a9945fb7a3cd3b074277adbc0c83cb1cc508c0de38cdfa7f172d15c94`.
Lean checks 12 explicit quotient/remainder identities, their degree bounds,
and the 75 entries of the three `5×5` matrices through `AdjoinRoot`'s
power-basis representation. The aggregate theorem is
`CryptoResearch.FrobTrace.QuotientMatrices.all_quotient_frobenius_matrices`.

| Base field | Frozen modulus | Matrix source |
| --- | --- | --- |
| `ZMod 11` | `z^5 + 2z^4 + 1` | `FROB-SPLIT-q11n5` |
| `ZMod 13` | `z^5 + 8z^4 + 1` | `FROB-NOLATTICE-q13n5` |
| `ZMod 19` | `z^5 + 3z^4 + 1` | `FROB-EQDEG-q19n5` |

## Historical code-path inspection

The archived [Sage core](../../../experiments/EXP-FROB-91ee9c/runs/TASK-20260914-7119f2/work/core.py)
enumerates constant-first monic moduli (lines 13–25), reads polynomial
coefficients in that order (29–32), and places the q-power images of
`1,z,...,z^4` into matrix columns (54–62). The archived
[lattice code](../../../experiments/EXP-FROB-91ee9c/runs/TASK-20260914-7119f2/work/lattice.py)
evaluates factor polynomials in that matrix and takes right kernels (21–39).
The [driver](../../../experiments/EXP-FROB-91ee9c/runs/TASK-20260914-7119f2/implementation.py)
calls those functions. Their present file SHA-256 values match the three
source hashes in the replay receipt (`core.py` `9c86ae27…`, `lattice.py`
`20e10343…`, driver `b4896b12…`). This is a static code-path match; Sage is
unavailable on this host, and source custody for the original run remains
unverified.

## Verification

The pinned Lean 4.35.0-rc1 `lake env lean` compile passed locally with no
errors or `sorry`. The exact-source [formal verifier receipt](proof-verification.json)
has SHA-256 `8e3f1f32ad8453d91f929444d95c7d52dc152b76cfa6a87a5061941f928f7263`.
It records an 8,972-job full workspace build and a 3,092-job target build,
both successful; no forbidden constructs; and a passing global audit of 625
theorem declarations using standard axioms only. The exact requested theorem's
axiom audit also passed. The receipt status is `machine_verified`, with
independent semantic review pending.

## Interpretation limit

The theorem binds the frozen quotient moduli and recorded matrix entries to
mathematical q-power on the quotient basis. It does not prove that every path
through the historical Sage driver implements that operation, recover original
source custody, or identify every run input byte with this model. The
[canonical finite-field factor-kernel proof](../2026-10-22-frob-c5-factor-kernels/REPORT.md)
and characteristic-five boundary control have separate scopes. The
[open bridge problem](../../../problems/frob-c5-factor-kernel-and-model-bridge.md)
tracks independent semantic/code review and historical C5 adjudication. C8
and the full experiment success gate remain open.
