# F6 source review before implementation

26 October 2026. Reader: `/root/pass2_lattice_orbits`. No second-pass data has
been collected. The committed task is `TASK-20261026-2746d0`.

- **Retrieved and read:** Steven Galbraith, corrected extended *Mathematics
  of Public Key Cryptography*, [chapter 17](https://www.math.auckland.ac.nz/~sgal018/crypto-book/ch17.pdf),
  section 17.2, especially Theorem 17.2.12(5). For a full-rank, delta=3/4
  LLL-reduced row lattice of rank n, the first-vector bound is
  `2^((n-1)/4) det(L)^(1/n)`. This does not bound every reduced row by the
  first-vector expression, and is not a multivariate root-extraction theorem.
- **Retrieved and read:** the same author's corrected [chapter 19](https://www.math.auckland.ac.nz/~sgal018/crypto-book/ch19.pdf),
  section 19.2 and the related independence warning. Lifting small modular
  roots to common integer zeros leaves a separate independence/elimination
  obligation. The intended code therefore checks the actual norm of each
  returned polynomial and explicitly tests the resulting ideal/extractor.
- **Retrieved and read:** [SEC 2 version 2.0](https://www.secg.org/sec2-v2.pdf),
  section 2.4.2, the published secp256r1 parameters, standard generator,
  subgroup order and cofactor. Parameter use is not a regenerated primality
  or point-count proof.
- **Internal, read:** the immutable first-pass F6 `report.md`, `check_bounds.py`,
  `result.json`, and the relations-and-bounds review. The old rectangle and
  digit-box sufficient windows and its known-root translated control are
  reference observations. They are not ordinary-target extraction evidence.
- **Internal, read:** `AGENTS.md`, the literature-first and observation rules,
  `audit-curve`, `experiment-protocol`, and the second-pass execution gates.

The alternative family is a two-variable total-degree staircase. Its leading
monomial is `(2,2)`, and each shifted polynomial has a distinct graded-lex
leading monomial. Exact triangularity supplies its rank and determinant;
actual LLL reduction is confined prospectively to two explicitly listed small
matrices. Hash-derived offsets do not inspect a solution. A separate positive
control deliberately derives offsets from a known public solution and remains
labelled as such.

The guaranteed-window checks apply only to these shifts. Neither a failed
inequality nor an extraction stop proves a general small-root impossibility.
No new theorem is attributed to inaccessible original Coppersmith or Jutla
papers; Galbraith's retrieved exposition is the external source actually read.
No novelty or speed claim is in scope.
