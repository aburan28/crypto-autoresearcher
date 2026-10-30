# F2 second-pass source review

26 October 2026. Task `TASK-20261026-e8fd72`. Author `/root/pass2_auxiliary`.
These notes precede implementation and any second-pass observation rows.

## Sources actually read

- **Retrieved primary:** Petit, Kosters and Messeng, *Algebraic approaches for
  ECDLP over prime fields*, PKC 2016,
  <https://people.maths.ox.ac.uk/petit/files/16PKC_primeECDLP.pdf>.
  Read PDF pages 5–11, including sections 3.1–3.5 and 4.1, through a read-only
  `curl | pdftotext` command in this session. Section 3.4 Lemma 1 proves the
  complete coset x-fibre when the image is not 2-torsion. Section 3.1 leaves
  a dedicated solver for its low-degree system uninvestigated. Section 3.2's
  cost model gives scalar multiplication and field arithmetic unit cost;
  its heuristic relation model is not a cost certificate for this work.
- **Internal, read:** the previous F2 `report.md`, `derivation.md`, `result.json`,
  `arithmetic.py`, `check_impl.py`, `verify_certificates.py`, and
  `relation_certificates.py` under
  `research/p256_factor_base_parallel_20261025/tracks/f2/`, together with the
  chain, generator, compact-full-chain and matched-domain receipts. These
  fix the existing inputs; they are not newly collected observations.
- **Retrieved primary parameter source:** SEC 2 document at
  <https://www.secg.org/sec2-v2.pdf>, section 2.4.2, read PDF pages 13–15 in
  this session using `curl | pdftotext`. Its page header identifies it as
  “SEC 2 (Draft) Ver. 2.0”; the exact secp256r1 p, a, b, standard G, n and
  h=1 were read and match the P-256 constants used below. No assertion about
  this document's final-publication status is made.
- **Internal, read:**
  `problems/pkm-isogeny-chain-factor-base-no-fast-decomposition.md`.
  Its historical chain/dense solver results are references, not rerun here.
  This pass must not claim to solve its large-base implicit-solver obligation.
- **Internal methodological sources, read:** `AGENTS.md` and its linked
  literature-first rule; `docs/experiment-protocol.md`; the
  `experiment-protocol`, `audit-curve` and `research-visuals` skill bodies;
  the frozen second-pass task card and `workflow/execution-gates.md`.

## Consequences for the implementation

The complete 65,536-element generic fibre has a retained coset certificate,
but its target lifts were not enumerated in the first pass. The new producer
will classify all its coordinates and preserve every rejected lift. The
independent checker will reconstruct the coset with different point formulas.

Finite-domain relation search uses the already fixed matched canonical sizes
26 and 121 in all three families. It enumerates unordered pairs of signed
target points, then joins a third point. A separate projective-arithmetic
oracle enumerates the corresponding pair/complement states. Their full
unordered signed solution sets must agree, including repeated points and
cancellation. Ordinary targets and deliberately constructed controls are
labelled separately. This is an explicit finite-domain reference algorithm;
it neither exploits the implicit chain nor avoids base enumeration.

The auxiliary curve has order p+1 and the target has published prime order r.
Their orders are coprime and their traces differ. Reinterpreting auxiliary
x-coordinates on P-256 supplies a selection rule, not a rational isogeny or
scalar-label transfer between those groups. Elliptic maps are unramified;
their induced x-coordinate maps have poles. The membership checker must
retain those poles and reject unsaturated finite-fibre membership.

## Assumptions and scope

The field and target parameters are the exact published P-256 parameters.
The planned target group-order check uses a nonzero standard generator of
prime order r and the unique multiple of r in the exact Hasse interval.
Primality is checked with FLINT's rigorous backend; this is not a serialized
portable primality proof. Once total order r and cofactor one are certified,
checking each lift's curve equation certifies its subgroup membership; the
producer will explicitly state that it does not perform a separate [r] test
on every lift.

No novelty, general yield, comparative performance, ECDLP advantage, official
scientific transition or canonical independent review is asserted. Native
Codex model binding is inherited and unprobed. S3 checkpoint disclosure and
the actual execution gate are root-owned; preparation does not release a run.
