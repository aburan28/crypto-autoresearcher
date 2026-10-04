# EXP-CERTBIN-c97c23 Stages 0-1 analysis

Reviewed under TASK-20261004-96b753 against REVIEW-CERTBIN-c97c23-20261004.
Scope is the Koblitz n=19 prime-subgroup labels, r=130873, m=3, cells
p_sparse and p_half. Amazon Bedrock was not selected. No Magma, Sage, or
AUXIN. No discrete logarithm was recovered.

## Observation

RUN-CERTBIN-6e4997 is Stage 0, status completed_valid, receipt
output_validated, check stdout `check ok stage0`, return code 0.
`archived_identity_ok` is true. The freeze row `nearby-p-half-identity`
records linearization error 1.0625 at p=1/2 and L=4, which is
`2-(1-(1/2)^4)`.

RUN-CERTBIN-8179be is Stage 1, status completed_valid, receipt
output_validated, check stdout `check ok stage1 O-ARTIFACT`, return code 0.
The raw outcome word is O-ARTIFACT. `certificate.kind` is `none` and
`verified` is true. That pair is an instrument note. It is not a
discrete-log certificate. `code.dirty` is true. The four implementation
SHA-256 values in both manifests match `git show` of
`5e8cb9c0d3179fdc753c7e42c9c75998b98998d7`. The dirty flag is the
uncommitted Stage-run artifact note.

From the Stage-1 raw cells, recomputed before any read of `implementation/`:

| cell | charged_ratio | below 1 | L=4 abs deviation | below 0.05 | below 0.15 | coverage_complete |
| --- | ---: | --- | ---: | --- | --- | --- |
| p_sparse | 8296.196579570447 | no | 0.04344622810527933 | yes | yes | false |
| p_half | 17864.96608580067 | no | 0.037942085967479056 | yes | yes | false |

p_half L=4 union frequency is 0.9. Distance to `L*0.5 = 2` is 1.1.
Distance to `L*p_hat = 1.5622779335691854` is 0.6622779335691854. Neither
distance is within 0.1. p_half `linearization_error` is
0.7002200195366645, equal to `L*p_hat` minus the L=4 prediction, and it
is below 1. `lossy_witness_pair_found` is true on every recorded union.
Uncharged ratios are 27.65398859856816 and 6.797932300532978. They are
not the headline.

A temp Stage-1 replay from a copy under `/tmp/review-certbin-c97c23`,
with run dir `/tmp/review-certbin-c97c23-run`, printed outcome
O-ARTIFACT. `check.py <run_dir>` exited 0 with stdout
`check ok stage1 O-ARTIFACT`. The replay kept both charged ratios and
the p_half linearization error. Its L=4 union frequencies were 0.11 and
0.86, so the absolute deviations moved to about 0.0334 and 0.00206 and
stayed inside 0.05. The repository experiment directory was not written
by that replay.

## Comparison

The pre-registered success sentence is O-RARE: Stage 0 identity holds,
both L=4 absolute deviations are below 0.05, p_half
`linearization_error` is at least 1, and both charged ratios are above
1. The identity and the L=4 band and the charged-ratio side hold. The
linearization side does not: the archived p_half field is below 1. The
nominal p=1/2 quantity 1.0625 is at least 1 and is not that archived
field. O-RARE is not licensed.

The O-BATCH sentence is a charged ratio below 1 at either cell. Both
charged ratios are above 1, by thousands. O-BATCH does not fire.
Uncharged ratios are a labelled column and are not a speedup.

The named O-ARTIFACT sentences outside `implementation/` are: p_half
measured union within 0.1 of `L*p`, union deviation above 0.15 after one
redraw, or Stage 0 identity failure. None of those fires. No frozen
sentence outside `implementation/` maps `linearization_error` below 1,
`coverage_complete` false, or `lossy_witness_pair_found` true onto
O-ARTIFACT. The archived outcome word is the instrument's label. It is
not adopted as a refutation.

Rho stays the reference only as the denominator of the charged ratio.
Both ratios sit above 1, so this package does not beat that estimate on
the charged column. No `S` and no exponent are computed.

## Inference

The package does not support O-RARE, does not call O-BATCH, and does not
weaken or reject the hypothesis. The L=4 rare-event band held inside
0.05, the charged ratios stayed above 1, and the named artifact triggers
did not fire, while O-RARE still fails its linearization threshold on
the archived p_half field. Direction is neutral. Strength is
inconclusive: one toy package, two cells, one Stage-1 seed, and the
instrument word is not a frozen trigger for the fields that failed
O-RARE. H-CERTBIN-a916e0 stays approved. EXP-CERTBIN-c97c23 moves from
approved to analyzed.

## Limitation

Tested scope is n=19, r=130873, m=3. Nothing here transfers to m=83 or
n>=131. No Stage 2 is authorized. `certificate.kind: none` with
`verified: true` does not certify a scalar. The L=4 band is one
unreplicated toy observation and is below replicated strength. The
replay's union frequencies are not bit-identical to the archived cells;
the required replay gate is the outcome word and the check exit code,
which both passed. A later protocol has to name which recorded field, if
any, turns this package into O-ARTIFACT before any relabel. This review
does not authorize a rerun.
