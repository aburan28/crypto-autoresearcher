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

## Incomplete primary panel

In the same 20-arm experiment, primary E1 (P29-floor-native,
RUN-ECTD-8231ef) ended with an infrastructure_error. The E2 and E3 random
arms (RUN-ECTD-d14263 and RUN-ECTD-45ca41) also ended with
infrastructure_error. The full panel therefore cannot form its registered
E2/E3-to-E1 comparison. These prior native E2/E3 results are secondary context
only; they do not use the graph study's committed target stream and are not
graph vertices or transported-base measurements.

## Graph study implication

The graph study should preserve E1 as its primary P29 floor. The existing E2
and E3 observations are available as historical secondary context. They do
not replace fresh E2/E3 observations if the frozen graph protocol requires
those endpoints to share the graph study's target root. The experiment
contract must state which scope it uses before target roots are issued; it
must not silently pool the prior and graph streams.

The graph [implementation report](../report.md) remains separate: it describes
schedule, admission, and readiness controls and contains no relation-yield
data.
