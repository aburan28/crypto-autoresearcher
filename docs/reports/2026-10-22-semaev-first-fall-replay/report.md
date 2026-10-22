# Semaev first-fall archive replay and trace-witness boundary — 2026-10-22

**Status:** scoped validation finding. The frozen measurement, formal target,
and Lean theorem are unchanged. No new cryptanalytic timing, hypothesis
promotion, or official research-state transition was made. This report checks
the historical toy Boolean model at `crypto-autoresearcher` main
`4db6ed753d3ff72749f6ce74220a69568558a8cf`.

## Observation

The original `ffd_semaev_measure.py` reproduced the committed
[`ffd_semaev_results.json`](../../../research/verification/ffd_semaev_results.json)
**byte for byte** (SHA-256 `64f6e34ceb16bd817c61c5974d2295c60197cf2b49f299663c3bc054333c99e7`).
Its eight cells use `n=4..7`, `n'=3,4`, ten Semaev seeds and 25 support-matched
null seeds per cell. The Semaev totals remain **70 draws with first fall at
degree two and ten at degree three**. The null distributions also match the
frozen table. The exact command, working directory, output hash and stdout are
in the [archive replay receipt](evidence/archive-replay.json) and
[log](evidence/archive-replay.log).

The new [per-draw record](evidence/draws.json) reconstructs the 80 Semaev
inputs, including seed, target abscissa, factor-base basis and Boolean equation
monomials. It also records 200 null-control seeds and their first-fall values.
The [independent checker](../../../research/verification/replay_ffd_semaev_20261022.py)
agreed with the archived result after **21,760 exhaustive finite-field product
comparisons**, **12,800 direct `S_3` truth-table assignments**, separate
projection-rank calculations through degree three on all 80 Semaev draws, and
support-profile and projection-rank checks through degree four on all 200 null
draws. The [checker log](evidence/replay.log) retains the five nonzero-target
exceptions. These are deterministic toy checks, not statistical estimates or
measurements on deployed curves.

| First fall in the archived Boolean model | Target `x_R` | Draws |
|:--|:--|--:|
| Degree two | Nonzero | 70 |
| Degree three | Nonzero | 5 |
| Degree three | Zero | 5 |

The [per-draw graphic](draws.svg) groups all 80 exact seeds by the trace
witness's status. Its [editable source](render.py) reads only the committed
per-draw record. The five zero-target draws fall outside the Lean theorem's
`x_R ≠ 0` premise. **Five degree-three draws have `x_R ≠ 0`**, so imposing that
premise alone does not establish the historical “degree two uniformly” wording.

## Checked mechanism and concrete finite example

The archived observable is
`new_falls(D) = dim(V_D ∩ R_{≤D−1}) − dim(V_{D−1})`, where `V_D` is the
degree-compatible span of Boolean monomial multiples of the descended
equations. The independent checker computes the intersection dimension as
`rank(full rows) − rank(degree-D projection)` using a second Gaussian
elimination routine. It also checks every descended equation against direct
evaluation of the binary `S_3` expression on all Boolean assignments. This
validates the recorded first-fall grades **within that exact model**.

The smallest nonzero-target degree-three example is `n=4`, `n'=4`, draw `s=1`:
seed `32201`, target `x_R=1`, basis `[9,3,2,12]` over the polynomial-basis
field with modulus `0b10011`. Its trace multiplier is `μ=x_R⁻²=1`.
The trace combination of the descended equations is the nonzero linear
Boolean polynomial `u₀ + u₃ + w₀ + w₃`; it is **already the fourth generator**.
The independent ranks give `dim V₁=1` and
`dim(V₂ ∩ R_{≤1})=1`, hence `new_falls(2)=0` even though trace cancels the
quadratic part. At degree three, `dim V₂=11` and
`dim(V₃ ∩ R_{≤2})=18`, so `new_falls(3)=7` and the first fall is three.
The exact four component equations and their monomial masks are in the
[draw record](evidence/draws.json).

Across the 75 nonzero-target draws, the trace residual represents a new class
modulo `V₁` in 67 degree-two draws. In three other degree-two draws it is
already in `V₁`, while a different relation produces the fall. In four
degree-three draws the nonzero trace residual is already in `V₁`; in the fifth
it is the zero polynomial. These are observations about this archived Boolean
model. They show why cancellation of quadratic coefficients, on its own, is
neither a certificate of a new degree-two class nor a full first-fall theorem.

## Proof and performance boundary

[`DegreeTwoFall.lean`](../../../formal/CryptoResearch/Semaev/DegreeTwoFall.lean)
proves the field and trace cancellation lemma under `x_R ≠ 0`; its own scope
comment says the nonzero quotient class is unproved. The
[frozen target](../../../formal/targets/semaev-s3-degree2-fall-witness.yaml)
and [historical note](../../../research/FFD_SEMAEV_MEASUREMENT1.md) use broader
wording. The finite example above contradicts universal degree-two first fall
**for the archived `V_D` observable**. It does not invalidate the narrower Lean
identity or prove anything about solving degree, general extension sizes,
ECDLP cost, or attack performance. A faithful Lean model of the Boolean
filtration and a checked rank counterexample remain to be written; the
[open problem](../../../problems/semaev-degree-two-fall-nonzero-bridge.md)
tracks those obligations.

No numerical performance dashboard was changed because this replay produced
no timing or attack-cost datum. The existing
[`fall_counts.svg`](../2026-10-20-formal-validation/fall_counts.svg) remains
numerically current: it already shows 70 degree-two and ten degree-three
draws. The new graphic adds the per-draw target and trace classification that
the earlier summary lacked.

## Reproduction and limits

Run Python 3.12 from a scratch working directory for the original script so
it does not rewrite the committed result. Then run the independent checker
from the repository root:

```sh
python3.12 /path/to/repo/research/verification/ffd_semaev_measure.py
python3.12 research/verification/replay_ffd_semaev_20261022.py \
  --output docs/reports/2026-10-22-semaev-first-fall-replay/evidence/draws.json
python3.12 docs/reports/2026-10-22-semaev-first-fall-replay/render.py
```

The source hashes, exact working directory and command for this replay are
bound in the two evidence JSON files. The checker uses the original sampler
and equation builder, but independently reimplements field multiplication,
direct `S_3` evaluation, and rank/intersection arithmetic; that is stronger
than rerunning the same aggregation and weaker than an independent Sage model
or a Lean proof of the full statement. The [PDF](report.pdf) embeds the graphic
and states the same claim boundary.
