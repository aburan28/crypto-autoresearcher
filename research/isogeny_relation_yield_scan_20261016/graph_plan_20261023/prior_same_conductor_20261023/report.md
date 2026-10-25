# Prior P29 same-conductor native observations

**Date:** 2026-10-23. This is a descriptive record audit of two already archived
native arms from EXP-ECTD-0cf008; it is not an evidence review or a graph-walk
measurement. The values below are copied from output-validated run receipts and
their raw-result.json records. The prior experiment remains incomplete.

## Curves and source records

All three secondary-panel models use F_p with p = 320092037, prime
subgroup order r = 320091991, and endomorphism conductor f_E = 8209. The
primary P29 floor curve E1 is
y^2 = x^3 + 101186781 x + 57596093, with G = (0,112219098).
The predeclared secondary curves are E2
y^2 = x^3 + 64570613 x + 54195252, with G = (0,5368294), and E3
y^2 = x^3 + 234001141 x + 79995391, with G = (5,53527325). These
identities and the same-field/order panel are bound by the existing
EXP-ECTD-0cf008 specification.

| Endpoint | Run ID | Supervisor status | Useful targets | Exact 99.75% endpoint interval | Rank at 512 / 2,048 / 8,192 / 32,768 |
| --- | --- | --- | ---: | --- | --- |
| E2 native | RUN-ECTD-c769f1 | output_validated | 2,204 / 32,768 | [0.06314751268846183, 0.07154457067169973] | 37 / 143 / 256 / 256 |
| E3 native | RUN-ECTD-f395a9 | output_validated | 2,191 / 32,768 | [0.06276232966654367, 0.07113645674170103] | 45 / 140 / 256 / 256 |

Derived observed fractions are 0.0672607422 for E2 and 0.0668640137 for E3.
Their difference is 13/32,768 = 0.0003967285 (about 0.0397 percentage
points). The plotted intervals overlap. This descriptive contrast does not
establish equality or a yield difference.

Both raw results record an independent ordered-count match and valid group-law
replay. Each reached rank 256 of 256 unknown columns by the 8,192-target
prefix. The [source run report](../../../../experiments/EXP-ECTD-0cf008/reports/run-20261016T0409Z/report.pdf)
retains the full attempt accounting, source digests, and failures. The
[editable plot source](draw.py) reads the sealed run outputs directly.

## Target-stream audit

The earlier specification says endpoint arms share a target vector. I
independently read the three committed native prepared inputs and hashed the
ordered `(alpha, beta)` coefficient pairs, excluding curve-dependent target
points. The first three pairs already differ:

| Endpoint | First three `(alpha, beta)` pairs | SHA-256 of all 32,768 ordered pairs |
| --- | --- | --- |
| P29 floor E1 | `(264673044,279640898)`, `(253871087,95189281)`, `(306981855,19898269)` | `64cd3756f380960a5a574e78f3d4a274f45dd70e841d31691a03bbbe588c51ca` |
| P29-E2 | `(306343046,290671108)`, `(172212597,306267709)`, `(6969290,67294454)` | `80d447c67d0d403e58614bdcef54cd260cab2ea3500be509c1982bf0cd3cb3c5` |
| P29-E3 | `(214677491,24330666)`, `(95793430,211520593)`, `(235839322,17706266)` | `2917b209cce21d597c9b1ecded06a4c9d484ca28d979a0efb65bf37bbe0fc7a3` |

These are three distinct coefficient streams, so the archived E2/E3 native
fractions are unpaired with E1 and with each other. They remain valid marginal
observations on their exact prepared inputs; they cannot be treated as
same-target secondary checks. The [frozen source specification](../../../../experiments/EXP-ECTD-0cf008/specification.yaml)
contains the common-target-vector requirement. Both E2/E3 execution environments bind the exact same legacy preparer SHA-256, `7bec20e2147641539d8dfdcc0ae0009581e485462396897f0751c879e4b32fef`. In the archived [preparer](../../../../research/conductor_relation_yield_20261014/prepare_input.py), `draw()` includes `endpoint_id` in the hash domain, and the `alpha` and `beta` calls pass the endpoint identifier. This explains the three observed streams and shows the shared-vector requirement was not met by those prepared inputs. The graph [preparer](../../preparation/prepare_graph_input.py) instead domain-separates target coefficients by `(stratum, stage, coefficient kind, index, retry)`; the [discovery selector](../../graph_selection_candidate_20261023/discovery_select.py) requires one coefficient digest across all arms in a stratum. Any new E2/E3 arms must use that same P29 stage stream or an explicitly endpoint-independent equivalent, and verify equality independently before interpreting paired contrasts.

## Incomplete primary panel

In the same 20-arm experiment, primary E1 (P29-floor-native,
RUN-ECTD-8231ef) ended with an infrastructure_error. The E2 and E3 random
arms (RUN-ECTD-d14263 and RUN-ECTD-45ca41) also ended with
infrastructure_error. The full panel therefore cannot form its registered
E2/E3-to-E1 comparison. These prior native E2/E3 results are secondary context
only; they use coefficient streams distinct from E1 and each other, do not use
the graph study's committed target stream, and are not graph vertices or
transported-base measurements. The graph study must generate one common
coefficient vector per stage for E1, E2, and E3 and verify its digest across
all corresponding arms.

## Graph study implication

The graph study should preserve E1 as its primary P29 floor. The existing E2
and E3 observations are available as historical marginal secondary context,
but the archived coefficient streams are not paired. They do not replace fresh
E2/E3 observations on the graph study's common P29 stream. The frozen staged
contract must bind a shared ordered coefficient stream for those controls and
verify the full coefficient sequence before reporting paired contrasts.

The graph [implementation report](../report.md) remains separate: it describes
schedule, admission, and readiness controls and contains no relation-yield
data.
