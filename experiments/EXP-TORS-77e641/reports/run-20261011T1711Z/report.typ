#set page(paper: "us-letter", margin: 0.75in)
#set text(font: "Libertinus Serif", size: 10pt)
= EXP-TORS-77e641 execution report

*Observation-only record for* `RUN-TORS-e2dcdc` (*psi7-factor-count*).

== Scope and disposition

The frozen factor-count computation completed in the pinned container and the
independent checker returned code 0. This report records the observation only;
it does not change the hypothesis, experiment, or goal status.

#image("graph.svg", width: 100%)

== Frozen inputs and custody

- Experiment: `EXP-TORS-77e641`; trial: `psi7-factor-count`; run: `RUN-TORS-e2dcdc`.
- Successor plan SHA-256: `b7039710cd01050a64d3d6fa2623d8ed8c9eda59476da8e89e8aa3fb0bf79c2f`.
- Execution checkout commit: `1fa531e33a8f811570a85ff57b619267044630fc`.
- Dispatch-plan SHA-256: `d37ee15636a41013ddc79b8cd57cdbb16fbd3390ed5dedbb2fe053aed1ae06f9`.
- Owner and lease: `executor-tors-77e641`, epoch `1`.
- Container: `crypto-ci-python:20261008`; network disabled; virtual-memory ceiling 512 MiB.
- Receipt: `returncode: 0`; checker: `check_returncode: 0`; status: `output_validated`.

== Recorded observations

At the frozen primary point `p = 23`, `A = 1`, `B = 1`, and `ell = 7`, the
multiplicity-weighted irreducible-factor counts were:

#raw(block: true, "I(E) = 10    I(E^c) = 10    absolute gap = 0    reading_row = counts_agree")

All eleven recorded controls were true, including degree 24 for each primary
polynomial, the c=1 count control, smallest-nonsquare selection (`c = 5`),
rebuild agreement, nonzero discriminants, and trace negation. The checker
returned code 0 and `attack_claimed` was false.

The secondary p=29 repeat was available with gap 0 and trace negation true. The
30 uniform null polynomials over `F_23` had multiplicity-weighted factor counts
between 2 and 8; these secondary values did not select the primary row.

== Interpretation boundary

This is one fixed curve/twist comparison at the declared primes and division
polynomial, with its named controls and null sample. It records equality of
the two primary counts for this scope and does not establish a general
factor-count law, an asymptotic conclusion, or a cryptanalytic advantage.
The raw result, manifest, reading, supervisor receipt, command, environment,
and checker logs remain under the run directory.
