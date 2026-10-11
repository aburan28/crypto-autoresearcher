#set page(paper: "us-letter", margin: 0.75in)
#set text(font: "Libertinus Serif", size: 10pt)
= EXP-SSI-db46fa execution report

*Observation-only record for* `RUN-SSI-989893` (*orbit-deficit-p19*).

== Scope and disposition

The supervisor returned `output_validated` and the independent checker returned
code 0. This report does not change the hypothesis, experiment, or goal status.

#image("graph.svg", width: 100%)

== Frozen inputs and custody

- Experiment: `EXP-SSI-db46fa`; trial: `orbit-deficit-p19`; run: `RUN-SSI-989893`.
- Plan SHA-256: `416edcd45fda23da611669907c9e87e295047bf2c4559ce3c587f90bc623fe9d`.
- Execution checkout: `2a48c802b4f94d0d0c193b5441f79ac975a32187`.
- Dispatch-plan SHA-256: `ce02ea3ab0470a145e7126fcd67cffc027840a8ef540db99433bd9876c21a1ea`.
- Owner and lease: `executor-ssi-db46fa`, epoch `1`.
- Container: `crypto-ci-python:20261008`; network disabled.
- Receipt: `returncode: 0`; checker: `check_returncode: 0`; status: `output_validated`.

== Recorded observations

The producer recorded `size_S = 2`, `O = 2`, `D = 0`, `deficit_F19 = 0`, and
`deficit_instrument = 1`. The field was `F_19[z]/(z^2-2)` with membership
counts `[324, 400]`. Round-trip, duplicate, route-agreement, field, and
Frobenius controls were true. The checker returned code 0 with no stderr.

== Interpretation boundary

These are the recorded values for one finite field and one membership census.
They do not by themselves establish a hardness result, a security reduction,
an endomorphism-ring conclusion, or behavior at another field or parameter.
The raw result and supervisor records remain under the run directory.
