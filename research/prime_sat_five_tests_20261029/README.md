# Five prime-field algebra and SAT tests

This implementation follows the five proposals from PR2673. It tests finite
mechanisms, correctness, certificates, and counted work on fixed tiny inputs.
It does not assert a cryptographic ECDLP improvement or a new intrinsic degree
of regularity bound. The original frozen contract is EXP-PFIVE-3ca920; its
interrupted trial is retained. Corrective EXP-PFIVE-e26798 completed the same
78 algebra fixtures and added all-target point validation on two tiny
prime-order curves. Its native receipt is `output_validated`, with all four
independent package checks valid.

1. `geometry/`: shared coefficient Graeffe membership, forward correspondence,
   and blind four-coefficient search with explicit exceptional charts.
2. `sat/solver.py`: an external finite-field theory-lemma loop around MiniSat.
   A clause can be learned only after checking a Boolean polynomial-calculus
   refutation of its forbidden prefix. Native cvc5 finite-field and Z3 modular
   bit-vector encodings are checked against the exact finite solution set.
3. `algebra/`: full and partial total/block Macaulay filtrations with retained
   ideal-span certificates; a source construction calibration is separate.
4. `algebra/`: syntax-selected backdoors tested on every legal assignment,
   with a fixed residual solver and explicit UNKNOWN branches.
5. `geometry/`: exact chart coverage and certified saturation compared with
   unsaturated and Rabinowitsch ideals, with independent finite model checks.

`core.py` implements sparse arithmetic in the Boolean quotient over F_p. The
SAT and algebra residuals are coordinate S3 equations. Even the SAT variant
with curve-x membership must pass a separate lift/sign check before a model
can be called a point decomposition. Some fixed residual targets have no
curve lift. The report preserves this distinction.

`driver.py` runs the three packages serially and retains completed package
artifacts if another package fails. It writes a raw summary and manifest;
the native supervisor supplies launch facts and invokes the independent
checks. Scientific runs require the frozen native protocol, source archive,
approval/readiness, ownership, and checkpoint gates documented in
`coordination/prime_sat_five_tests_20261029/ADMISSION.md`.

No source file contains a solution-dependent policy. Exhaustive model sets
are generated after candidate solving and used for verification or explicitly
charged root extraction. The published Multi-homogeneous XL algorithm is not
reproduced by the block-filtration prototype. Its transfer remains open.

The [completed finite-test report](../../experiments/EXP-PFIVE-e26798/reports/run-20261029T0454Z/report.md)
records all five leads, retained UNKNOWN outcomes, exact model checks and
instrument limits. The [original interruption report](../../experiments/EXP-PFIVE-3ca920/reports/run-20261029T0421Z/report.md)
remains a separate historical record. The corrective checker validated
44,460 basis certificates, all 1,560 branch assignments, 22 actual point
decompositions and 31 factor-base UNSAT target cells. These are tiny finite
correctness results; no regularity reduction or ECDLP speedup is established.

A separate [two-summand lifting derivation](../../experiments/EXP-PFIVE-e26798/reports/run-20261029T0454Z/two-summand-lift-lemma.md)
gives exact rational witnesses from S3 when the rational target is not
two-torsion. Its two polynomial identities were checked symbolically. This
does not amend the frozen experiment or establish a solver improvement.

Raw large artifacts were published and independently downloaded with matching
hashes. Native snapshot verification still lacks support for policy manifests;
the [custody integration gap](../../problems/native-snapshot-artifact-manifest-resolution.md)
and independent scientific review remain open. Reports do not change official
hypothesis status.

Primary implementation references:

- [Finite-field reasoning in Yices](https://arxiv.org/html/2402.17927v1)
- [cvc5 finite-field API](https://cvc5.github.io/docs/cvc5-1.4.2/examples/finite_field.html)
- [Author slides for monomial-of-regularity construction](https://pqcrypto.cs.ru.nl/ampqc/slides/Tuesday_Melvin.pdf)
- [Author implementation](https://github.com/LarsMath/monomial-of-regularity)

These sources motivate mechanisms; they do not establish their effectiveness
on prime-field elliptic-curve point decomposition.
