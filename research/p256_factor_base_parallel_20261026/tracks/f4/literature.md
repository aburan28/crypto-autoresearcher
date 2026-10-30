# F4 source review before implementation

26 October 2026. Reader: `/root/pass2_divisors`. This review preceded the
second-pass implementation and any second-pass data. No novelty is claimed.

Sources actually read:

- **Internal:** the first-pass `tracks/f4/report.md`, `result.json`,
  `divisor.py`, `theory.py` and `independent_check.py`, under
  `research/p256_factor_base_parallel_20261025/`. The former source supplies
  exact norm-factor/local-multiplicity certificates and a dense cancellation
  oracle; its constructed coincidences do not estimate natural collisions.
  Published P-256 order, cofactor and field facts remain explicit inputs.
- **Retrieved primary source:** Thomas Zaslavsky,
  [Matrices in the Theory of Signed Simple Graphs](https://arxiv.org/pdf/1303.3083),
  sections I.F–G and IV.A–C, especially Theorem IV.1 and its proof. Read the
  incidence convention, switching argument and characteristic restriction.
  Over an odd-characteristic field the signed incidence rank depends on
  balanced components; an unsigned cycle count is insufficient. The new
  implementation allows unequal nonzero endpoint weights, so the ordinary
  signed-graph formula is used only for its signed controls. The weighted
  reducer has a separate linear-algebra argument in `theory.md`.
- **Retrieved primary source:** Claus Diem,
  [Index calculus with double large prime variation for curves of small genus
  with cyclic class group](https://arxiv.org/pdf/math/0606607), sections 1–2.
  Read the main theorem, FP/PP definitions, tree construction and substitution
  step. Its complexity theorem assumes fixed genus at least two and cyclic
  class group (or known structure). P-256 has genus one; that theorem supplies
  neither a P-256 cost estimate nor a yield law here. Tree recombination is
  established prior work, not a new attack mechanism.
- **Retrieved metadata only:** Gaudry, Thomé, Thériault and Diem,
  [ePrint 2004/153](https://eprint.iacr.org/2004/153). The landing page and
  abstract were read. The full PDF returned HTTP 403 through the web reader;
  its detailed proof is not represented as read. An attempted older Zaslavsky
  author-site PDF URL returned HTML, not a paper. Neither failure implies an
  absence of prior work.
- **Internal workflow:** `AGENTS.md`, its literature/observation rules,
  `docs/experiment-protocol.md`, the protocol/export schemas and checker,
  the committed F4 card `TASK-20261026-b71abe`, and
  `runtime/export-notes.md`. These require prospective freezing, source
  custody, retained failures and the real S3 checkpoint gate before data.

The work reuses the first-pass divisor producer read-only and adds a separate
polynomial/point consumer and a sparse weighted incidence reducer. No
independence of scientific sessions or canonical model admission follows from
having two arithmetic implementations.
