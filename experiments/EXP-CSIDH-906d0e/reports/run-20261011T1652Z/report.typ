#set page(paper: "us-letter", margin: 0.75in)
#set text(font: "Libertinus Serif", size: 10pt)
= EXP-CSIDH-906d0e execution report

*Observation-only record for* `RUN-CSIDH-760fc4` (*ancilla-ratio-frozen-cell*).

== Scope and disposition

The supervisor returned `output_validated` and the independent checker returned
code 0. This report does not change the hypothesis, experiment, or goal status.

#image("graph.svg", width: 100%)

== Frozen inputs and custody

- Experiment: `EXP-CSIDH-906d0e`; trial: `ancilla-ratio-frozen-cell`; run: `RUN-CSIDH-760fc4`.
- Plan SHA-256: `d42d49a15c1d11d4f55e4cfac4c127ea927d60e74710507c53a47d78c478dfd3`.
- Execution checkout: `5a926654419a261409b03e4ab85e5f7d260ea3a9`.
- Dispatch-plan SHA-256: `763e9c9712275540a288360f0738230a82326554b44821fe876182e892fa731b`.
- Owner and lease: `executor-csidh-906d0e`, epoch `1`.
- Container: `crypto-ci-python:20261008`; network disabled.
- Receipt: `returncode: 0`; checker: `check_returncode: 0`; status: `output_validated`.

== Recorded observations

The recorded widths were `width_F = 732604` and `width_I = 1705307`. The exact
recorded ratio was `1705307/732604`; the producer also recorded decimal field
`2.327734`. The reading row was `ratio_at_least_two`.

Both frozen pairs agreed. Principal/reference checks, width and ancilla
accounting checks, and both discriminant `-60` refusal controls passed. The
producer recorded `attack_claimed=false`. The checker printed:

#raw(block: true, "check ok: row ratio_at_least_two, width_F 732604, width_I 1705307")

== Interpretation boundary

These are the recorded widths and controls for one discriminant, one encoding,
two frozen input pairs, and the named circuit construction. They do not by
themselves establish an end-to-end implementation advantage, an ECDLP cost
reduction, a quantum resource bound beyond this cell, or behavior at another
discriminant or encoding. All raw outputs and supervisor records remain under
the run directory.
