#set page(paper: "us-letter", margin: 0.75in)
#set text(font: "Libertinus Serif", size: 10pt)
= EXP-CSIDH-f3c102 execution report

*Observation-only record for* `RUN-CSIDH-9d743d` (*truncation-vs-form-count*).

== Scope and disposition

The supervisor returned `output_validated` and the independent checker returned
code 0. This report does not change the hypothesis, experiment, or goal status.

#image("graph.svg", width: 100%)

== Frozen inputs and custody

- Experiment: `EXP-CSIDH-f3c102`; trial: `truncation-vs-form-count`; run: `RUN-CSIDH-9d743d`.
- Plan SHA-256: `0aa8207091fbd570bb36613b98abefaa23baca817b6f875060dd1958bacbc8c1`.
- Execution checkout: `9a62784add253f84452ee4abf63d32efc2f81c07`.
- Dispatch-plan SHA-256: `0984cd3d0fa32eb79032ef60db9bbcfdc179cc2f6bb73be4c74029ac81ecc526`.
- Owner and lease: `executor-csidh-f3c102`, epoch `1`.
- Container: `crypto-ci-python:20261008`; network disabled.
- Receipt: `returncode: 0`; checker: `check_returncode: 0`; status: `output_validated`.

== Recorded observations

The two frozen form enumerations agreed and each returned `h = 3`. The
interval-gated nearest integer was `r = 3`, with recorded `|r - h| = 0`.
The interval-length gate was true and the nearest-integer gate status was `ok`.

The exact rational truncation was:

#raw(block: true, "L30 = 2541037817707 / 2329089562800")

The recorded control bits were all true: `-83` fundamental, `-332`
non-fundamental, `-84` fundamental self-check, enumeration agreement,
`chi(1) = 1`, reduced-fraction status, and Kronecker implementation agreement.
`attack_claimed` was false. The checker printed:

#raw(block: true, "check ok: row match, gate ok, r 3, h 3")

== Interpretation boundary

These are the recorded values for one discriminant and one 30-term frozen
truncation under the named rational enclosure and controls. They do not by
themselves establish a class-number formula, a security level, an ECDLP-cost
reduction, or behavior at another discriminant or truncation length. The raw
result, manifest, reading, supervisor receipt, command, environment, and
checker logs remain under the run directory.
