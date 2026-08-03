---
id: KN-LIT-48b4eb
type: literature
title: "Classic McEliece: conservative code-based cryptography: cryptosystem specification"
authors: []
authors_note: >-
  The document's title page carries no author list; it is issued by the Classic
  McEliece team. Authors NOT filled in from recall. The team roster is at
  https://classic.mceliece.org/people.html, which was not fetched.
year: 2022
venue: "Classic McEliece round-4 NIST PQC submission, document dated 23 October 2022"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: "https://classic.mceliece.org/mceliece-spec-20221023.pdf"
source_artifact:
  url: "https://classic.mceliece.org/mceliece-spec-20221023.pdf"
  sha256: "dcc6878852ef8a00a7bedd859da661770cf85d2c3d9239e06d25e4a0d365fd12"
  retrieved_by: TASK-20260803-f3aece
  committed_locally: false
tags: [code-based, mceliece, goppa, niederreiter, specification, parameters, kem, primary-source]
confidence: reported
citation_verified: read
citation_verified_note: >-
  `read` is earned by TASK-20260803-f3aece (GOAL-MCE-001 BATCH-001), which
  fetched this PDF from the designers' own site on 2026-08-03 (HTTP 200; URL,
  byte count and sha256 in that task's source_access_log.yaml) and extracted it
  with two independent extractors (pypdf and pdfminer.six) requiring agreement.
  Validator TASK-20260803-409c5e independently re-fetched it and recomputed
  every arithmetic claim below. ONLY SECTIONS 3, 6 AND 7 WERE READ CLOSELY. The
  agent that drafted this entry (TASK-20260803-a53f73) did NOT read the
  document; it worked from that task's committed transcription. No local copy
  is committed; the sha256 above is the integrity anchor.
added: "2026-08-03"
superseded_by: null
---

## Contribution
The official definition of Classic McEliece, so designated by the project's own
Specification page (*"The official definition of Classic McEliece is the
cryptosystem specification"*). 16 pages. Defines the KEM over binary Goppa codes
in Niederreiter form: parameters, matrix reduction and generation, encoding and
decoding subroutines, key generation, fixed-weight-vector generation,
encapsulation, decapsulation, byte-string representations, and ten selected
parameter sets.

## Key claims (as reported)
- Parameters are `(m, n, t)` with `q = 2^m`, `n ≤ q`, `t ≥ 2` and `mt < n`; the
  specification defines `k = n − mt` (Section 3). **Definitional, not a claim.**
- **Ten selected parameter sets (Section 7)** — five `(m, n, t)` triples, each in
  a plain and an "f" (semi-systematic, `(μ, ν) = (32, 64)`) variant:
  `(12, 3488, 64)`, `(13, 4608, 96)`, `(13, 6688, 128)`, `(13, 6960, 119)`,
  `(13, 8192, 128)`.
- **Resulting code rates `k/n`**, computed from the specification's own
  definition: `85/109 ≈ 0.779817`, `35/48 ≈ 0.729167`, `157/209 ≈ 0.751196`,
  `5413/6960 ≈ 0.777730`, `51/64 ≈ 0.796875`. The five rates of the
  **specification's own Section 7 sets** lie in `[0.729167, 0.796875]`.
  *(Phrased as the specification's sets rather than "the standardized sets": the
  ISO list is not identical — see the scoping note below and KN-LIT-209151.)*
- Symmetric parameters (Section 6.1): `l = 256`, `H` = first 256 bits of
  SHAKE256, `σ₁ = 16`, `σ₂ = 32`.
- Size formulas (Section 6.2): public key is `mt·⌈k/8⌉` bytes; ciphertext is
  `⌈mt/8⌉` bytes.
- **The document makes NO security-category claim and states NO numeric byte
  sizes**; it delegates both. See [[KN-LIT-7b78de]] and [[KN-LIT-b7f8f8]].
  Independently confirmed by the validator: the specification contains no
  occurrence of `categor*` and no byte sizes.

## Arithmetic verified by this program
`k = n − mt` and `k/n` in exact rationals for all five sets were **independently
recomputed 5/5** by `TASK-20260803-409c5e` from a re-fetched specification — on
`k`, on lowest-terms fractions, on gcds, and on 6-decimal-place values, with
`mt < n` everywhere and `5413` confirmed prime (`EV-MCE-332f99` O-1). This is
arithmetic on transcribed definitional values, **not** a reproduction of any
security claim.

## Relevance to this program
Primary source for `RQ-MCE-e65b3c` and `GOAL-MCE-001`. Supplies the rate `k/n`
that any rate-axis claim in the alternant/Goppa line ([[KN-LIT-c4c2ac]],
[[KN-LIT-6b5b72]], [[KN-LIT-819780]], [[KN-LIT-45b1b2]]) must be compared
against, and the exact `(n, k, t)` at which any memory-charged ISD baseline for
this goal must be computed.

**Scope discipline this entry must carry with it.** A rate comparison is only
meaningful once the axis is named: `KN-LIT-c4c2ac`'s restriction includes a
**code-family exclusion of Goppa codes** alongside its rate condition, and
`KN-LIT-819780`'s theorem is stated in the **dual** rate. This entry supplies a
**primal** rate `k/n`. Converting, and naming which axis is being compared, is
required before any arithmetic (`DEC-20260803-a5b9b1` D-2, D-4).

**Forecloses nothing on the attack side**, and asserts nothing about Classic
McEliece's security in either direction.

## Not verified here
Only Sections 3, 6 and 7 were read closely; the algorithm definitions in Sections
4 and 5 were **not audited**. No claim in this entry has been independently
reproduced beyond the arithmetic cross-check recorded above and the 10/10
size-formula control at
`coordination/goals/GOAL-MCE-001/batches/BATCH-001/tasks/TASK-20260803-f3aece/parameter_sets.md`
§5. **No implementation was run and no KAT was checked.** No local copy of the
PDF is committed.
