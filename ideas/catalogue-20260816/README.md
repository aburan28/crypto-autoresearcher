# Idea and draft-contract batch, 2026-08-16

300 proposals in `ledger/proposals/`, each paired with one DRAFT experiment contract in `experiments/`. Generated in one session across 30 disjoint generation buckets.

## What these records are, and are not

- Every contract is `status: draft`, `frozen: false`, `execution_authorized: false`, `evidence_eligible: false`, `approved_by: null`. **Nothing here is approved and nothing has been run.** Only the Coordinator approves an experiment (AGENTS.md rule 1).
- Every contract carries `hypothesis_id: null` with a `hypothesis_id_note`. No hypothesis was minted: `/design-experiment` mints one from the parent proposal under Coordinator authority, and binding a fresh contract to an existing hypothesis it was not designed to test would be worse than binding it to none.
- Every proposal is `novelty_status: unverified`. No external source was reachable from this environment, so no record asserts what the literature does or does not contain. Novelty screens are greps over this repository and are reported as exactly that.
- No record claims an attack, a break, a speedup, or a security consequence. Each contract's `claim_ceiling` states the maximum a run could support and what does not follow from it.
- These are candidates for the Coordinator's queue, not results.

## How this batch was generated

Thirty generation agents, one per bucket, each given: its anchor research
questions to read in full; the openings those questions state themselves; a
consolidated anti-duplication blacklist drawn from a twelve-slice survey of the
committed corpus (`docs/portfolio-review-20260816.md`); and the record contract
above. Each agent ran its own novelty screen by grepping this repository before
writing, and each records what that screen found, including the record IDs it
collided with.

Buckets were chosen against measured coverage, not intuition. Eighteen of the
22 research questions that carried **zero** proposals are addressed here for
the first time. Three buckets sit where the survey found no contract at all
anywhere in the corpus: `FHEX` (no FHE contract exists), `SIDECH` (no contract
measures a cache-timing, power or EM side channel), and part of `ZKARG` (no
contract touches arithmetization primitives). `SIDECH` has no research question
of its own, which is itself the finding.

Identifiers were minted against the union of identifier-bearing paths that
`tools/allocate_id.py` scans, in one pass rather than one scan per identifier,
then verified free against that union and against each other. No identifier was
chosen by looking for the next free number (`CLAUDE.md`, Conventions).

### Two caveats, recorded rather than tidied away

**One generated record was dropped and not replaced in place.** A pipeline
smoke test earlier in the same session wrote ten records under this date and
removed them minutes later. A generator grepping during that window truthfully
reported a hit on `IDEA-20260816-982f7f`, which will never exist. The record
carrying that citation was dropped rather than patched: rewriting a generator's
own novelty screen to say something it did not observe would be the worse
error. A separate record was generated afterwards to complete the bucket, and
it is a different proposal, not a repair of the first.

**The guard that caught it was initially too blunt.** Its first form dropped any
record citing a same-date `IDEA-20260816-*` identifier, on the reasoning that
proposal IDs are minted after generation. That held for the first tranche and
failed for the second: 209 records were already committed when the remaining
buckets ran, so those agents legitimately found and cited real siblings, and the
blunt rule discarded 30 sound records. The guard now tests **existence** rather
than the date.

## Where the next batch should go

`docs/portfolio-review-20260816.md` §6 lists the openings this batch does *not*
cover, surfaced by the survey after the buckets were already committed. The
strongest are whole primitives with no question and no hypothesis — BIKE,
XMSS/LMS, the code-equivalence signatures (LESS, CROSS, PERK, RYDE, Mirath),
Wave, LPN/VOLE, arithmetization-oriented hashes, polynomial commitments,
OPRF/PAKE, VRFs — and classical ECDLP territory the program skipped:
hyperelliptic and genus-2 Jacobians, Weil descent/GHS, anomalous curves, and
point counting as a cost object.

## Coverage

| area | bucket | pairs | question(s) |
| --- | --- | ---: | --- |
| `AEADC` | AEAD composition and nonce-misuse surface | 10 | `RQ-AEADC-8db132` |
| `ALECF` | Quantum circuits and resource accounting | 10 | `RQ-ALECF-001`, `RQ-QRE-6dba8c` |
| `ALPF` | Prime-field decomposition candidates from toy campaigns | 10 | `RQ-ALPF-001` |
| `ALR` | Compact elliptic resultants and projector moments | 10 | `RQ-ALR-001`, `RQ-ALR-002` |
| `ARGON` | Argon2 and memory-hard function accounting | 10 | `RQ-ARGON-141710` |
| `ASCON` | Ascon standardization delta | 10 | `RQ-ASCON-2dfd8b` |
| `BLAKE` | BLAKE3 transfer argument and tree-mode separation | 10 | `RQ-BLAKE-584719` |
| `CODESD` | MPC-in-the-head signatures (SDitH, FAEST, MQOM) | 10 | `RQ-FAEST-001`, `RQ-MQOM-001`, `RQ-SDITH-001`, `RQ-WFS-e776b6` |
| `FALCON` | FN-DSA / Falcon sampler and precision | 10 | `RQ-FNDSA-001` |
| `FBG` | Structured factor-base geometry | 10 | `RQ-FBG-001` |
| `FHEX` | FHE noise and parameter honesty | 10 | `RQ-FHE-001` |
| `FRODOFO` | FrodoKEM and the FO transform | 10 | `RQ-FRODO-3260cc`, `RQ-FRODO-a2dbe2` |
| `HAWKL` | HAWK and module-LIP | 10 | `RQ-HAWK-001` |
| `HQCX` | HQC decoding failure and code structure | 10 | `RQ-HQC-001` |
| `LATDUAL` | LWE primal versus dual and the structure discount | 10 | `RQ-MLKEM-003` |
| `MCEGOP` | Classic McEliece and binary Goppa structure | 10 | `RQ-MCE-b38a8b`, `RQ-MCE-e65b3c`, `RQ-MCEQ-fcb504` |
| `MDFIVE` | MD5 collision/preimage asymmetry | 10 | `RQ-MDFIVE-6870c1` |
| `MULTIV` | Multivariate signatures (MAYO, UOV, QR-UOV, SNOVA) | 10 | `RQ-MAYO-001`, `RQ-QRUOV-001`, `RQ-SNOVA-001`, `RQ-UOV-001` |
| `NTRUL` | NTRU lattice structure | 10 | `RQ-NTRU-9015ee` |
| `PMA` | Principal-minor assignment and divisor parity | 10 | `RQ-PMA-001` |
| `POLYMAC` | GHASH and Poly1305 forgery-bound tightness | 10 | `RQ-POLYMAC-7c89e4` |
| `RSAPI` | RSA under partial information | 10 | `RQ-RSA-d46f02` |
| `SHAONE` | SHA-1 chosen-prefix cost model | 10 | `RQ-SHAONE-081e3a` |
| `SHATHREE` | SHA-3 / Keccak internal-differential frontier | 10 | `RQ-SHATHREE-cd2cb2` |
| `SHATWO` | Reduced-round SHA-256 frontier | 10 | `RQ-SHATWO-f196c7` |
| `SIDECH` | Side-channel and fault models as measurable predicates | 10 | `RQ-ECDSA-87625f`, `RQ-FNDSA-001`, `RQ-INSTR-f8faa0`, `RQ-SLHDSA-001` |
| `SIMSPK` | SIMON and SPECK rotation-constant space | 10 | `RQ-SIMSPK-f6a6c0` |
| `SLHDSA` | SLH-DSA and hash-based signatures | 10 | `RQ-SLHDSA-001` |
| `SNFS` | Special number field sieve and trapdoor detection | 10 | `RQ-RSA-afe33c`, `RQ-SNFS-005666` |
| `ZKARG` | Argument systems and Fiat-Shamir soundness accounting | 10 | `RQ-WFS-e776b6` |

**Total: 300 pairs.**

## Index

### `AEADC` — AEAD composition and nonce-misuse surface

- **`IDEA-20260816-3b00b0`** -> `EXP-AEADC-4db1f5` (composition, priority medium, `RQ-AEADC-8db132`)  
  Decide the generic-composition matrix by exhaustion rather than by argument: cross three orderings of encryption and authentication with four placements of the nonce and associated data, and for every cell enumerate a miniature mode completely to decide six finite predicates, producing a filled decision table with witnesses
- **`IDEA-20260816-52e00e`** -> `EXP-AEADC-483ad0` (mechanism, priority medium, `RQ-AEADC-8db132`)  
  The nonce is not always the nonce: audit the mode-level derivation that turns a variable-length nonce into an initial state, and grade the collision rate of that derived state as a function of the mix of nonce lengths a policy permits, with the compression step replaced by an ideal function
- **`IDEA-20260816-7fb48f`** -> `EXP-AEADC-22a7e9` (representation, priority high, `RQ-AEADC-8db132`)  
  Exhaustively enumerate the length-encoding block of an AEAD mode within a declared class and count, rather than argue about, how many distinct associated-data and ciphertext length pairs a mode maps to the same final authenticated block, treating the length field as a finite audit surface with a countable answer
- **`IDEA-20260816-9b2260`** -> `EXP-AEADC-5ead2b` (measurement, priority medium, `RQ-AEADC-8db132`)  
  The bound is stated per key and the deployment holds millions of them: measure the multi-key advantage of an AEAD mode directly at toy key widths and compare it against the naive union accounting, so the gap between u times the per-key bound and the measured multi-key quantity becomes a number rather than a folklore worry
- **`IDEA-20260816-9fbe84`** -> `EXP-AEADC-db683e` (representation, priority high, `RQ-AEADC-8db132`)  
  A second finite audit, of the header not the lengths: enumerate every string in a small declared alphabet and count exactly how many distinct vectors of associated-data components four serialization conventions map to the same authenticator input, so vector-input canonicalization becomes a decidable count rather than a design assumption
- **`IDEA-20260816-a1de9a`** -> `EXP-AEADC-ae634f` (tooling, priority high, `RQ-AEADC-8db132`)  
  One AEAD invocation is not a stream: build an auditor that takes a chunk-framing scheme and decides by exhaustion whether truncation, reordering, duplication and cross-stream splicing of sealed chunks are detectable, returning a witness sequence for every undetectable operation rather than a security opinion
- **`IDEA-20260816-bfa08e`** -> `EXP-AEADC-71fe6c` (theory, priority high, `RQ-AEADC-8db132`)  
  Count the mode's commitment budget before touching a primitive: express an AEAD composition as a dataflow of adversary-controlled variables against target-imposed constraints, derive one integer per mode that predicts how many colliding-context solutions exist, and check that integer against exhaustive search on toy analogues
- **`IDEA-20260816-ee3447`** -> `EXP-AEADC-2f5c62` (control, priority high, `RQ-AEADC-8db132`)  
  An instrument-validity ladder for every AEAD-mode measurement this program makes: run each measurement three times with an ideal permutation, a real block cipher and a deliberately structured weak permutation in the primitive slot, and report the measurement as mode-level only if the first two agree and the third moves
- **`IDEA-20260816-f0cdb2`** -> `EXP-AEADC-c669b3` (measurement, priority medium, `RQ-AEADC-8db132`)  
  Grade a repeated nonce by what it costs rather than by whether it happened: track the affine difference system that keystream reuse hands an adversary in a counter-mode AEAD, and measure recovered-plaintext yield as a graded function of repeat multiplicity and of the overlap profile of the repeated messages
- **`IDEA-20260816-f3ecc5`** -> `EXP-AEADC-a6d508` (mechanism, priority high, `RQ-AEADC-8db132`)  
  Turn release of unverified plaintext from an adjective into a counted predicate: build scaled-down analogues of three decryption pipelines, hand the adversary the plaintext of every rejected ciphertext, and measure the distinguishing advantage that release buys as a function of how many rejected queries are released

### `ALECF` — Quantum circuits and resource accounting

- **`IDEA-20260816-04bcb1`** -> `EXP-ALECF-209e02` (theory, priority medium, `RQ-QRE-6dba8c`)  
  A logical-layer circuit score is used as a proxy for physical cost, but whether it preserves the ordering of two circuits depends on the error-correction model it is quoted from; map the region of a named surface-code parameter space where the logical ranking and the physical ranking disagree, and report the boundary rather than a number.
- **`IDEA-20260816-15c21e`** -> `EXP-ALECF-f169f6` (composition, priority medium, `RQ-ALECF-001`)  
  The benchmark's interface makes the offset point classical bits while the target is qubits, so every submitted circuit is a classically-parameterized family and can precompute on the offset; measure the classicality dividend as the ratio of Toffoli and ancilla cost between classical-offset and fully quantum-offset reversible point addition.
- **`IDEA-20260816-23332f`** -> `EXP-ALECF-1ddb1a` (mechanism, priority high, `RQ-QRE-6dba8c`)  
  Peak ancilla width is a supremum of the live-qubit trace, but the error-correction bill is charged against the integral of that trace; build the allocation trace as a first-class measured object for reversible arithmetic and measure how often peak and integral disagree on which of two circuits is cheaper.
- **`IDEA-20260816-34782f`** -> `EXP-ALECF-36362d` (representation, priority high, `RQ-ALECF-001`)  
  The ALECF benchmark collapses a two-axis resource vector onto the scalar product Toffoli times peak qubits; treat that product as one scalarization among many, and measure over a population of reversible arithmetic circuits what fraction of circuit pairs reverse their ranking when the scalarization is changed.
- **`IDEA-20260816-37d5e8`** -> `EXP-ALECF-0d2ef0` (measurement, priority medium, `RQ-QRE-6dba8c`)  
  A per-call circuit score is quoted downstream as if cost were additive across calls, but composition reuses ancillas and re-routes registers; measure the non-additivity directly by building k-fold compositions of one fixed reversible point addition and reporting where Toffoli count is additive and peak width is not.
- **`IDEA-20260816-5e9358`** -> `EXP-ALECF-1e2283` (measurement, priority high, `RQ-ALECF-001`)  
  One fixed circuit does not have one score: enumerate the accounting choices the benchmark specification leaves implicit, and compute the interval of scores the identical circuit receives across that lattice, reporting the multiplier range rather than a point.
- **`IDEA-20260816-67a1b4`** -> `EXP-ALECF-bd6443` (measurement, priority high, `RQ-ALECF-001`)  
  The counted gate categories do not sum to the reported op stream in any committed ALECF log row, leaving between seven and thirty-one percent of operations in no bucket; make partition completeness a reported metric, measure the residual on the committed logs, and validate the metric where completeness is guaranteed by construction.
- **`IDEA-20260816-699a0f`** -> `EXP-ALECF-04d97b` (control, priority high, `RQ-ALECF-001`)  
  Three imported ALECF packages carry different scores, and the committed logs show their difference is partly a snapshot-time difference rather than a circuit difference; build a differencing procedure that splits a fork-to-fork score delta into circuit term, benchmark term, and unattributable residual, and measure the residual.
- **`IDEA-20260816-e93eb8`** -> `EXP-ALECF-34caeb` (control, priority high, `RQ-ALECF-001`)  
  Affine point addition has an exceptional set that uniform random sampling can never reach at cryptographic size, so a benchmark validating on 9024 random shots is silent about it; measure the exceptional set's density at toy scale and the exact miss probability of shot-based validation as a function of the caller's input distribution.
- **`IDEA-20260816-f9740c`** -> `EXP-ALECF-0f7253` (tooling, priority high, `RQ-ALECF-001`)  
  A classical basis-state simulator is the cheap correctness instrument for reversible arithmetic, but it has a detection boundary nobody measures; build the simulator and then attack it with a mutation suite, reporting per-checker detection rates so the instrument's blind spots are a table rather than an assumption.

### `ALPF` — Prime-field decomposition candidates from toy campaigns

- **`IDEA-20260816-0027ac`** -> `EXP-ALPF-c8b943` (mechanism, priority high, `RQ-ALPF-001`)  
  Every archived ALPF positive was measured on curves labelled only 'structured', so representation effect and curve-coefficient effect are perfectly confounded: run a factorial design crossing representation against a matched twist-and-isogeny-controlled curve sample and decompose the variance in the survival verdict.
- **`IDEA-20260816-6a7fa4`** -> `EXP-ALPF-9859ff` (control, priority high, `RQ-ALPF-001`)  
  The ALPF lane measured an algebraic degree and never checked whether that degree predicts the thing it stands in for: on the same toy instances, actually solve for a decomposition and verify its certificate, then report how often an early-fall cell yields a certified decomposition compared with a quiet cell.
- **`IDEA-20260816-746055`** -> `EXP-ALPF-1ed5d7` (measurement, priority high, `RQ-ALPF-001`)  
  The ALPF survival verdict is an instrument with an unmeasured false-positive rate: run the identical first-fall meter and survival labeller over an ensemble of null polynomial systems drawn to match each surviving cell's leading-form degree profile, and report the fraction that survive by chance.
- **`IDEA-20260816-a67f97`** -> `EXP-ALPF-1bd2d9` (theory, priority high, `RQ-ALPF-001`)  
  The ALPF meter reads homogeneous leading forms, not the systems themselves, so every survival verdict is a verdict about a truncation: test whether early fall on the leading forms predicts early fall on the full inhomogeneous Semaev system, and measure the disagreement rate directly.
- **`IDEA-20260816-ac9263`** -> `EXP-ALPF-b123eb` (tooling, priority high, `RQ-ALPF-001`)  
  Nothing in this lane can be re-run, because the archived meter is Sage and the harness has no first-fall implementation: build a dependency-free Macaulay-rank meter validated against the published control rows, wired so every cell it reports ships with its matched null from the same invocation.
- **`IDEA-20260816-bd49b9`** -> `EXP-ALPF-a378ad` (control, priority high, `RQ-ALPF-001`)  
  Before trusting any ALPF negative, establish that the screen can see a candidate that is really there: plant decomposition structure of a controlled, dialled magnitude into otherwise ordinary prime-field Semaev systems and measure the screen's detection probability as a function of planted magnitude.
- **`IDEA-20260816-c1314e`** -> `EXP-ALPF-357186` (measurement, priority high, `RQ-ALPF-001`)  
  Turn the ALPF lane's implicit toy-to-medium transfer hope into a pre-registered numeric prediction: fit the survivor's degree and cost curve on 13, 15 and 17 bit instances, freeze a written prediction for 21 and 25 bit instances before running them, then run them and report the signed residual.
- **`IDEA-20260816-c65293`** -> `EXP-ALPF-4ee364` (measurement, priority medium, `RQ-ALPF-001`)  
  The archived campaign's single celebrated positive is a maximum taken over many screened cells, so count the cells, estimate their effective independence by resampling the archived design, and report how many survivors a campaign of that exact shape produces when nothing is there.
- **`IDEA-20260816-da106b`** -> `EXP-ALPF-853fd9` (representation, priority medium, `RQ-ALPF-001`)  
  KN-OPEN-005 asks whether a non-generic representation is generic-group-model simulable; make that checkable for one concrete ALPF survivor by building the simulator and testing transcript equivalence, so the e-ring oracle either falls to a constructed simulator or resists it on a named input.
- **`IDEA-20260816-fe3526`** -> `EXP-ALPF-695642` (composition, priority medium, `RQ-ALPF-001`)  
  Compose the screen's measured error rates into the number a Coordinator actually needs: given a false-positive rate, a detection power and an assumed base rate of real candidates, report the posterior odds that a fired ALPF cell is real, and attribute the discrimination stage by stage across the pipeline.

### `ALR` — Compact elliptic resultants and projector moments

- **`IDEA-20260816-21ae6c`** -> `EXP-ALR-54f9fc` (control, priority high, `RQ-ALR-001`)  
  Check whether the ALR lane's central comparison is a comparison at all: resolve the base of the B in the represented-route exponent 7/2 and the base of the B in the 5/2 rho proxy back to primitive parameters, and report whether one substitution makes them commensurable
- **`IDEA-20260816-6a2bea`** -> `EXP-ALR-42b30c` (mechanism, priority high, `RQ-ALR-002`)  
  Measure what a truncated nested projector moment stream actually discards by counting the collision fiber: how many distinct weighted candidate configurations share the first j moments for every j below 2c, so that moment order becomes a measured lossiness curve rather than a threshold quoted from the reconstruction bound
- **`IDEA-20260816-6fc66c`** -> `EXP-ALR-33e5c8` (measurement, priority high, `RQ-ALR-001`)  
  Compute the monomial support and total degree of the compact target-divisor resultant symbolically at toy sizes before any solve, and compare its Newton polytope vertex set against the generic Minkowski-sum prediction that a random pair of the same bidegrees produces in the same invocation
- **`IDEA-20260816-778ba8`** -> `EXP-ALR-9a6112` (theory, priority high, `RQ-ALR-001`)  
  State the represented nN body and the compact target-divisor interface as two explicit size formulas in the divisor degrees n and N, the candidate count c and the characteristic p, tabulate their ratio at the three recorded toy curve families, and locate the parameter inequality at which the compact object stops being smaller than the body it claims to avoid
- **`IDEA-20260816-82de84`** -> `EXP-ALR-ba9ee8` (composition, priority medium, `RQ-ALR-001`)  
  Read the ALR chart-wise target-divisor elimination as a contraction tree over F_p and measure the exact rank of each bond tensor against a uniformly random tensor of identical shape, so that compactness of the resultant tree becomes a measured rank rather than an inherited expectation
- **`IDEA-20260816-93ea1e`** -> `EXP-ALR-37e9e7` (theory, priority medium, `RQ-ALR-001`)  
  Grade the difficulty of the open SLP-direct constructor by writing its input-plus-output information floor: show that softly O(n+N+c) is exactly the read-plus-write minimum, so the ALR lane is asking for an optimal-to-within-polylog algorithm, and state the compression factor a constructor must achieve
- **`IDEA-20260816-9a91df`** -> `EXP-ALR-9711e4` (tooling, priority medium, `RQ-ALR-002`)  
  Instrument the peak live-slot watermark of a straight-line program and of its transpose at matched toy sizes, because the transposition principle preserves operation count but not memory, so a moment stream obtained by transposing a composition program may reintroduce the very body the compact route exists to avoid
- **`IDEA-20260816-c80fdf`** -> `EXP-ALR-8960f7` (control, priority high, `RQ-ALR-002`)  
  Locate the exact parameter at which the nested projector weight stops being a weight: sweep total target degree across the characteristic and measure the first instance where a true candidate acquires multiplicity zero modulo p, against a matched random-integer-weight null of identical total mass
- **`IDEA-20260816-e8e809`** -> `EXP-ALR-784fee` (representation, priority medium, `RQ-ALR-001`)  
  Measure the displacement rank of the Sylvester matrix of the ALR target-divisor pair over F_p and its growth in the divisor degrees, against a uniformly random matrix of identical shape, separating structure that a generator representation could compress from structure that is merely a change of coordinates
- **`IDEA-20260816-efb9b3`** -> `EXP-ALR-84752d` (measurement, priority medium, `RQ-ALR-001`)  
  Measure the only step that actually shrinks the represented body: the duplicate-multiplicity profile of the target divisor, its deduplication ratio and its induced chart count, swept across strided, uniform and opposite-point-rich constructions against a uniform-on-curve null at matched size

### `ARGON` — Argon2 and memory-hard function accounting

- **`IDEA-20260816-0a95c8`** -> `EXP-ARGON-a34f5a` (mechanism, priority high, `RQ-ARGON-141710`)  
  Two candidate causes produce the same observable: build one synthetic variant with the RFC window structure and a uniform within-window draw, and another with a full-history window and the RFC offset transform, so the back-distance shape and any depth effect are attributed to segment geometry or to the transform rather than to whichever was named first.
- **`IDEA-20260816-1128f8`** -> `EXP-ARGON-e26dbb` (representation, priority medium, `RQ-ARGON-141710`)  
  The security argument counts graph nodes and the machine counts memory cells, and later passes overwrite in place so the map between them is many-to-one with multiplicity t; measure the induced cell-level cost of node-level removal sets, since deleting a node frees no cell whose index another surviving node still occupies.
- **`IDEA-20260816-2c1f20`** -> `EXP-ARGON-22e6bb` (measurement, priority medium, `RQ-ARGON-141710`)  
  The AT cost model charges Argon2 memory by peak capacity, but the block-fill loop is a streaming write-then-random-read workload; measure achieved bytes-per-second and the reuse-distance profile of a reduced-parameter run as m sweeps across the last-level-cache boundary, and locate which resource actually binds.
- **`IDEA-20260816-3effe4`** -> `EXP-ARGON-f2d827` (tooling, priority high, `RQ-ARGON-141710`)  
  The Argon2 lane graph is a chain plus exactly one backward edge per node, a structural class narrow enough that minimum depth-reducing set may be exactly computable by an interval dynamic program rather than approximated; test that hypothesis against exhaustive brute force at tiny scale before the whole lane commits to a greedy bound.
- **`IDEA-20260816-444f00`** -> `EXP-ARGON-9f2fd7` (theory, priority high, `RQ-ARGON-141710`)  
  Write the area-time cost model down as an explicit function with named parameters and find, symbolically and with zero compute, the surface on which its ranking of the honest evaluator against a memory-reducing strategy flips -- because a model whose verdict is unstable in a parameter nobody measured is not a cost model but a convention.
- **`IDEA-20260816-504122`** -> `EXP-ARGON-864e88` (measurement, priority medium, `RQ-ARGON-141710`)  
  Parallelism is the one deployed parameter nobody varies: at fixed total memory, compute exactly the native longest path and the maximum antichain width of the full multi-lane reference DAG as p sweeps, and check whether depth falls as 1/p or is held up by the cross-lane edges the segment structure permits.
- **`IDEA-20260816-7001ed`** -> `EXP-ARGON-8ab44d` (control, priority medium, `RQ-ARGON-141710`)  
  Run this lane's graph pipeline unchanged on scrypt's second-loop access pattern and on two degenerate designs whose answers are structurally forced, so that every Argon2 number arrives with nearby objects on both sides of it rather than as a bare figure with nothing to be compared against.
- **`IDEA-20260816-78c476`** -> `EXP-ARGON-b1d030` (representation, priority high, `RQ-ARGON-141710`)  
  For Argon2d the memory-access DAG is not one graph but a random variable indexed by the input; measure the input-invariant skeleton -- the edges that recur across many synthetic inputs -- with Argon2i, whose graph is input-independent by construction, as the perfect positive control and a fresh-uniform generator as the negative one.
- **`IDEA-20260816-839444`** -> `EXP-ARGON-41fd17` (control, priority high, `RQ-ARGON-141710`)  
  A depth-robustness ratio is defined by its denominator: run the identical measurement against a declared family of four different null graphs and report whether the sign and size of the effect survive the choice, because a conclusion that flips with the null is a fact about the comparison object rather than about Argon2.
- **`IDEA-20260816-b7f2fe`** -> `EXP-ARGON-8357f3` (mechanism, priority high, `RQ-ARGON-141710`)  
  In-degree zero is a free eviction: compute exactly, on the real per-lane reference DAG, the oracle-lookahead live-set profile -- how many blocks a clairvoyant evaluator must retain at each step -- and compare its time-integral against the peak-times-duration rectangle the AT model charges.

### `ASCON` — Ascon standardization delta

- **`IDEA-20260816-0e0e69`** -> `EXP-ASCON-746407` (measurement, priority high, `RQ-ASCON-2dfd8b`)  
  Pose the reduced-inter-block round count as a measurement over the REACHABLE INPUT SUBSPACE rather than over the permutation: measure the largest round depth at which a higher-order derivative still sums to zero when the summation cube is confined to the rate positions a duplex actually exposes, and compare that depth against unrestricted full-state cubes
- **`IDEA-20260816-1166e9`** -> `EXP-ASCON-494e1d` (control, priority medium, `RQ-ASCON-2dfd8b`)  
  Test whether the phrase r-round permutation is even well defined once the specification declares a schedule longer than the standard call: enumerate every admissible round-constant schedule slice, compute whether the resulting r-round functions coincide, differ by constants only, or differ structurally, and report the ambiguity as a named control on every round-indexed statement
- **`IDEA-20260816-1af57f`** -> `EXP-ASCON-2d34d8` (representation, priority high, `RQ-ASCON-2dfd8b`)  
  Decide computationally whether the bit-ordering change reported between the submission and SP 800-232 is a CONJUGATION of the permutation by a fixed bit-index permutation -- exhibiting the witness if it is -- because that single fact partitions every exploited property into re-indexable and re-derivable, and it can be settled without reading a single published attack
- **`IDEA-20260816-36e10a`** -> `EXP-ASCON-5c9ff7` (composition, priority medium, `RQ-ASCON-2dfd8b`)  
  Audit CROSS-MODE separation rather than intra-mode: the standard's AEAD, hash, XOF and customized-XOF algorithms share one permutation and are distinguished only by IV words and mode-level separator bits, so enumerate exhaustively whether any two modes can be driven to the same (initial state, absorb sequence) prefix within a declared class
- **`IDEA-20260816-50e103`** -> `EXP-ASCON-efcd85` (measurement, priority medium, `RQ-ASCON-2dfd8b`)  
  Quantify the new IV constants as an object by measuring, over ALL pairs of constants differing in the IV word rather than over the two specific values this program cannot pin, the round depth at which the induced initial-state difference reaches full diffusion, so that IV-dependence of an exploited property becomes a depth threshold instead of a judgement
- **`IDEA-20260816-76f564`** -> `EXP-ASCON-59ff1a` (theory, priority medium, `RQ-ASCON-2dfd8b`)  
  Derive from first principles, inside this program and citing no external bound, the EXACT finite-sum inner-collision probability for a duplex at a declared rate and capacity, tabulate the gap between it and its own birthday asymptotic across device-lifetime data volumes, and validate the exact expression by direct enumeration at toy capacities
- **`IDEA-20260816-7ea680`** -> `EXP-ASCON-65aaa0` (composition, priority medium, `RQ-ASCON-2dfd8b`)  
  Audit the optional 256-bit-key nonce-masking variant not by pinning it -- which this program cannot do -- but by enumerating the LATTICE OF ADMISSIBLE CONSTRUCTIONS consistent with the declared state size, key, nonce and tag widths, and computing per cell whether the capacity portion at first squeeze retains full key-dependent entropy
- **`IDEA-20260816-a14ea4`** -> `EXP-ASCON-4d3d00` (mechanism, priority medium, `RQ-ASCON-2dfd8b`)  
  Build an exact duplex STATE ACCOUNTANT that labels every state bit across a session as attacker-set, attacker-known, or unknown and propagates those labels conservatively through the reduced inter-block permutation, so that the mode's constraint on what can be injected and observed becomes a measured closure depth rather than a sentence
- **`IDEA-20260816-b03a6f`** -> `EXP-ASCON-7f675e` (tooling, priority high, `RQ-ASCON-2dfd8b`)  
  Treat each published Ascon result not as a result but as a DEPENDENCY SIGNATURE -- the finite set of specification features its exploited property reads -- and adjudicate transfer to SP 800-232 by intersecting that signature with the submission-to-standard delta set, so every cell defaults to UNDETERMINED and can only be resolved by a named, checkable feature-level dependency edge
- **`IDEA-20260816-cfe83d`** -> `EXP-ASCON-7a1602` (measurement, priority high, `RQ-ASCON-2dfd8b`)  
  Test whether the customized XOF mode's map from a (customization string, message) pair to the exact padded absorb sequence entering the permutation is INJECTIVE, by exhaustive enumeration over a declared short-length class, with a deliberately defect-injected variant of the same encoder as the null arm that the identical search must catch

### `BLAKE` — BLAKE3 transfer argument and tree-mode separation

- **`IDEA-20260816-074cba`** -> `EXP-BLAKE-c39930` (composition, priority medium, `RQ-BLAKE-584719`)  
  Track a single-bit difference injected into one chunk through the Merkle tree to the root chaining value with the compression function reduced to r rounds, and measure the propagation width -- how many chaining values carry a difference at each tree level -- against a sequential-mode baseline of the same input length.
- **`IDEA-20260816-0bbb70`** -> `EXP-BLAKE-ac02f6` (tooling, priority high, `RQ-BLAKE-584719`)  
  Require two independently written encodings of the same reduced-round BLAKE3 differential model -- one CNF for a SAT solver, one MILP -- to agree on every optimum they both reach, and publish the agreement table as the precondition any bound-per-round curve must clear before it is compared with another primitive's.
- **`IDEA-20260816-2dfc3a`** -> `EXP-BLAKE-7f9d51` (measurement, priority medium, `RQ-BLAKE-584719`)  
  Run one frozen trail-search encoding against the BLAKE3 permutation-with-schedule and the BLAKE2s permutation-with-schedule and report the two minimum-trail-weight-per-round curves side by side, so the BLAKE2-to-BLAKE3 margin transfer becomes a divergence this program measured rather than a design assertion it inherited.
- **`IDEA-20260816-3af456`** -> `EXP-BLAKE-eeaef8` (measurement, priority high, `RQ-BLAKE-584719`)  
  Compute the exact bit-level dependency matrix -- which output bits are functions of which input bits after r rounds -- by symbolic reachability rather than by statistical avalanche sampling, for BLAKE3, BLAKE2s and the message-injection-off round, and report the round at which each first reaches full dependency.
- **`IDEA-20260816-3d23e2`** -> `EXP-BLAKE-9f61cc` (theory, priority medium, `RQ-BLAKE-584719`)  
  Extend the injectivity audit to the OUTPUT side: enumerate whether two distinct root states, output-block indices, or modes can place identical bytes at identical stream offsets within a declared finite class, treating extendable output as a separate predicate from the fixed-length digest rather than as one object.
- **`IDEA-20260816-6e0226`** -> `EXP-BLAKE-a85617` (control, priority high, `RQ-BLAKE-584719`)  
  Treat the compression function's input tuple -- chaining value, block, block length, counter, flag word -- as an encoding map from semantic tree positions, and prove or refute its injectivity by exhaustive enumeration over a declared finite class of inputs, modes and tree shapes, with the class boundary written down before the enumeration starts.
- **`IDEA-20260816-75df2c`** -> `EXP-BLAKE-b75207` (mechanism, priority medium, `RQ-BLAKE-584719`)  
  Build the four chimeras that separate BLAKE3's message schedule from its round count and its finalization, run the identical trail-search and diffusion instrument on each, and attribute any BLAKE3-versus-BLAKE2s divergence to one named design change instead of to the pair of names.
- **`IDEA-20260816-7bab5e`** -> `EXP-BLAKE-868493` (theory, priority high, `RQ-BLAKE-584719`)  
  Measure the finalization as a separate object: the map that turns a permuted state into a chaining value or a digest, scored by exact counts of output-difference cancellation on its algebraic layer alone, for BLAKE3's chaining and root outputs against BLAKE2s's feed-forward, with a random map of the same shape as the null.
- **`IDEA-20260816-7dce27`** -> `EXP-BLAKE-c535d3` (representation, priority medium, `RQ-BLAKE-584719`)  
  Recast BLAKE3's modes as three separate predicates over one initialisation map rather than as one object: enumerate whether an unkeyed default, a keyed-mode key, and each stage of key derivation can ever present the same initial chaining value and flag word, over a declared class of keys and context strings.
- **`IDEA-20260816-e4d944`** -> `EXP-BLAKE-57a74e` (control, priority high, `RQ-BLAKE-584719`)  
  Use the message-injection-disabled BLAKE3 round -- the ChaCha-shaped nearby object obtained by forcing every injected message word to zero and holding it constant -- as the instrument's free control, and report how much of the measured per-round bound is carried by message freedom rather than by the permutation itself.

### `CODESD` — MPC-in-the-head signatures (SDitH, FAEST, MQOM)

- **`IDEA-20260816-2c83a3`** -> `EXP-CODESD-514d35` (measurement, priority high, `RQ-SDITH-001`)  
  Build a toy MPC-in-the-head protocol small enough that every transcript can be enumerated, run a genuinely optimal cheating prover against the complete challenge space, and compare the exhaustively measured soundness error against the per-repetition formula the paradigm budgets for it.
- **`IDEA-20260816-4df735`** -> `EXP-CODESD-fe8542` (composition, priority high, `RQ-FAEST-001`)  
  One proof shell, three relations: run the identical MPC-in-the-head machinery over a code-shaped relation, a Boolean-circuit-shaped relation and a quadratic-system-shaped relation with every proof-layer parameter held fixed, and attribute each measured difference to the relation rather than to the paradigm by construction.
- **`IDEA-20260816-722a94`** -> `EXP-CODESD-f9a900` (control, priority high, `RQ-WFS-e776b6`)  
  Calibrate the soundness-accounting instrument on protocols whose exact soundness is known in advance: a protocol with soundness identically one, one with soundness identically zero, and a family with hand-computable soundness, and report the instrument's recovered value against the known value before any unknown protocol is measured.
- **`IDEA-20260816-77e7d2`** -> `EXP-CODESD-dfc8a6` (control, priority high, `RQ-MQOM-001`)  
  One parameterized MPC-in-the-head accounting expression, three parameter shapes: instantiate the same soundness-and-size inequality with SDitH-shaped, FAEST-shaped and MQOM-shaped tuples, then classify every slack term as paradigm-level if it survives all three shapes or scheme-level if it survives exactly one.
- **`IDEA-20260816-8639e7`** -> `EXP-CODESD-544044` (mechanism, priority medium, `RQ-WFS-e776b6`)  
  Measure the reusable transcript prefix as a counted object: in a multi-round public-coin reference protocol, how many hash compression calls survive unchanged when a state-restoration attacker rewinds to round r, and how does that amortization change the per-attempt cost the grinding accounting charges?
- **`IDEA-20260816-8ee18f`** -> `EXP-CODESD-4771a1` (mechanism, priority high, `RQ-MQOM-001`)  
  Do repetitions actually multiply? Instrument the cheating-success indicator per repetition in a toy shell where repetitions share a salt and a commitment root, and measure the covariance between repetition-level success events against the independence the composition step assumes.
- **`IDEA-20260816-b3a6f0`** -> `EXP-CODESD-67614c` (theory, priority medium, `RQ-SDITH-001`)  
  A zero-compute forced value and a quantifier-order audit for seed-tree opening size: derive the exact worst case and the exact expectation of revealed nodes for a punctured tree, then check whether a size claim is stated for all hidden sets or only for typical ones, with an incomplete-tree family as the nearby-object control.
- **`IDEA-20260816-bbff88`** -> `EXP-CODESD-5baf70` (measurement, priority medium, `RQ-SDITH-001`)  
  Measure the signature-size versus soundness tradeoff curve instead of quoting it: emit real bytes from a toy MPC-in-the-head shell across a full (N, tau, tree-shape) grid, measure the exact soundness at each point by enumeration, and report the residue between measured bytes and the analytic size formula.
- **`IDEA-20260816-cdbe94`** -> `EXP-CODESD-52c6fe` (representation, priority high, `RQ-FAEST-001`)  
  Treat the punctured seed tree's revealed-node antichain as the tracked object and measure the distribution of its SHAPE, the per-level cardinality profile, against the hidden-leaf set that produced it, asking how many distinct hidden sets share each shape and what that many-to-one collapse costs the size accounting.
- **`IDEA-20260816-f05ef2`** -> `EXP-CODESD-b9c717` (measurement, priority high, `RQ-WFS-e776b6`)  
  Grinding as a counted object: with a budget of G counter values a forger does not obtain G fresh uniform challenges but the IMAGE of a fixed function on G points, so measure that image's coverage, its repeat structure and the realized maximum-over-image, against the fresh-uniform model the accounting assumes.

### `FALCON` — FN-DSA / Falcon sampler and precision

- **`IDEA-20260816-0e6599`** -> `EXP-FALCON-237190` (measurement, priority high, `RQ-FNDSA-001`)  
  Replace sampled goodness-of-fit with exhaustive enumeration: at lattice dimensions 2, 4 and 8 with small widths the Klein sampler's output support is finite, so the total variation between a p-bit-mantissa implementation and exact rational arithmetic is computed rather than estimated, and mantissa width becomes a swept variable with zero sampling noise.
- **`IDEA-20260816-5d0c27`** -> `EXP-FALCON-5535e4` (composition, priority high, `RQ-FNDSA-001`)  
  Measure the transfer law itself rather than assuming it: hold mantissa width fixed and sweep lattice dimension, fitting the exponent in divergence proportional to dimension raised to that exponent, because every toy-to-deployed extrapolation in this goal silently assumes a value nobody in this corpus has measured.
- **`IDEA-20260816-5dd256`** -> `EXP-FALCON-cad4fe` (theory, priority high, `RQ-FNDSA-001`)  
  Distinguishing is not recovering: run the observation-collision audit on the map from secret basis to defective output law, because if that map factors through the Gram-Schmidt norm profile then the whole distributional channel identifies at most a profile and never a key, and the ceiling is provable at zero compute with a toy-scale witness.
- **`IDEA-20260816-63811b`** -> `EXP-FALCON-04436a` (measurement, priority medium, `RQ-FNDSA-001`)  
  Treat the recursion's accumulated rounding error as a random walk and measure whether it grows like the square root of the tree depth or linearly in it, because an interval-arithmetic certificate charges the linear rate and the ratio between the two rates is exactly how loose every composed precision budget in this goal currently is.
- **`IDEA-20260816-724cc9`** -> `EXP-FALCON-90e215` (composition, priority medium, `RQ-FNDSA-001`)  
  Deterministic and randomized signing are two different objects for a distinguisher: under deterministic signing the transcript is a function of the message, so repeated messages yield no new samples and the binding resource becomes distinct messages rather than signatures, which changes the deviation-to-signature-count curve by a factor nobody in this corpus has counted.
- **`IDEA-20260816-8bdc64`** -> `EXP-FALCON-69b926` (representation, priority medium, `RQ-FNDSA-001`)  
  Change the representation from secret frame to public dual lattice: measure what fraction of the oracle log-likelihood-ratio's information a statistic built only from public dual vectors recovers, because that efficiency ratio is the named open successor of this corpus's own divergence hypothesis and it is estimable at toy scale.
- **`IDEA-20260816-c7ddc2`** -> `EXP-FALCON-537872` (mechanism, priority high, `RQ-FNDSA-001`)  
  Precision is not one number: split the sampler's floating point into three separable roles, the once-per-key tree constants, the per-signature recursion arithmetic, and the base sampler's comparison constants, then lower each alone to find which role carries the divergence and which can be cheapened for free.
- **`IDEA-20260816-e5c333`** -> `EXP-FALCON-4731ed` (mechanism, priority medium, `RQ-FNDSA-001`)  
  Count the decision flips instead of measuring the distribution: the divergence between a p-bit sampler and an exact one is carried entirely by the randomness tapes on which rounding changes a discrete decision, so the flip rate upper-bounds total variation and is countable at full 53-bit precision where the distance itself is unmeasurable.
- **`IDEA-20260816-e82331`** -> `EXP-FALCON-ed2bbd` (control, priority medium, `RQ-FNDSA-001`)  
  Every divergence statistic in this goal reads the entropy source and the sampler through one channel and reports one number, so substitute the randomness source across four grades while holding the sampler fixed and measure how much of any detected divergence the source alone can manufacture.
- **`IDEA-20260816-fa2fe6`** -> `EXP-FALCON-047e31` (control, priority high, `RQ-FNDSA-001`)  
  Audit the load-bearing heuristic instead of the sampler: H-FNDSA-6a9cbb's divergence bound rests on leaf centers being near-uniform and near-independent modulo one, and that assumption is directly measurable at toy scale, so measure the center distribution and report by how much the heuristic moves the bound it carries.

### `FBG` — Structured factor-base geometry

- **`IDEA-20260816-25269a`** -> `EXP-FBG-e60ccb` (composition, priority medium, `RQ-FBG-001`)  
  Charge every factor-base geometry for what it costs to build: measure coverage excess per unit of instrumented construction cost and per unit of construction memory, so that a geometry which buys a one percent excess with a quadratic search is placed on the same Pareto frontier as one that buys nothing for a linear scan
- **`IDEA-20260816-405086`** -> `EXP-FBG-1cb7b4` (measurement, priority high, `RQ-FBG-001`)  
  Replace the raw coverage ratio with a scale-free currency - the fraction of the exact combinatorial ceiling a geometry actually attains - and run the growth arm on THAT, asking whether any constructible geometry's attainment fraction rises with group size rather than merely its ratio against a random base
- **`IDEA-20260816-5ea9b4`** -> `EXP-FBG-8c93e7` (control, priority high, `RQ-FBG-001`)  
  Audit what a matched random factor base actually is: measure how much of every recorded structured-geometry excess is produced by the choice among three defensible matched nulls - matched nominal size, matched negation-collapsed effective size, and matched total multiset count - by computing all three in one invocation
- **`IDEA-20260816-62354d`** -> `EXP-FBG-477be4` (tooling, priority high, `RQ-FBG-001`)  
  Build one geometry-agnostic factor-base measurement module that takes any geometry as a constructor plus a membership predicate and emits a self-verifying certificate - realised sizes, exact coverage, matched-null excess and construction charge - with its matched random null executed inside the same call
- **`IDEA-20260816-98ab8e`** -> `EXP-FBG-c7b46b` (theory, priority medium, `RQ-FBG-001`)  
  Reproduce the bounded-degree factor-base obstruction as a measured curve rather than a theorem citation: build factor bases as image loci of plane curves of increasing degree, and test whether measured coverage genericity tracks the intersection degree the derivation says controls it
- **`IDEA-20260816-c9565d`** -> `EXP-FBG-f5a8d8` (control, priority high, `RQ-FBG-001`)  
  Calibrate the detection floor of factor-base geometry measurement by planting a tunable amount of structure into an otherwise random base and finding the smallest coverage excess the exact counter, its bootstrap intervals and its permutation null can actually resolve at each group size
- **`IDEA-20260816-d35a3e`** -> `EXP-FBG-b23342` (representation, priority high, `RQ-FBG-001`)  
  Split every factor-base geometry by the COORDINATE IT IS DEFINED IN - the exponent group reachable only through a discrete logarithm, versus the x-line reachable by a membership test - and measure coverage excess separately on each side, so that the realizability gap between the two is a number rather than an intuition
- **`IDEA-20260816-dca08c`** -> `EXP-FBG-155e2b` (measurement, priority medium, `RQ-FBG-001`)  
  Measure, rather than argue, the displacement rank of the relation-incidence matrix that an arithmetic-progression factor-base support induces, against a matched random support of identical size and identical density, and report the rank as a property of the geometry alone with no solver invoked
- **`IDEA-20260816-f49ad1`** -> `EXP-FBG-bf91e4` (mechanism, priority medium, `RQ-FBG-001`)  
  Test whether one scalar - the largest non-trivial character-sum modulus of the factor base's indicator function - predicts coverage excess across unrelated geometries, by fitting the law on one half of a geometry panel and validating it on a held-out half that was never seen during fitting
- **`IDEA-20260816-f50ee4`** -> `EXP-FBG-e25a2f` (theory, priority medium, `RQ-FBG-001`)  
  Restate the universal algebraic-factor-base no-go of KN-OPEN-020 as a decidable predicate over an explicit finite grammar of factor-base descriptions, attach a numbered escape list to it, and calibrate the classifier by running it on the six geometries whose exact yield and coverage EV-FBG-001 already measured

### `FHEX` — FHE noise and parameter honesty

- **`IDEA-20260816-28a7fb`** -> `EXP-FHEX-6d8dcf` (theory, priority medium, `RQ-FHE-001`)  
  A parameter set's security number is computed for an adversary given m samples, but a homomorphic evaluation releases ciphertexts throughout a circuit; write down the sample count a circuit actually publishes as a function of its shape and compare it, as a pure counting exercise, with the m the derivation assumed.
- **`IDEA-20260816-3fc7b2`** -> `EXP-FHEX-ea745a` (composition, priority medium, `RQ-FHE-001`)  
  Restate a parameter change as an operation count rather than a bit count: for a grid of secret densities and modulus chains, count the homomorphic multiplications and rotations a fixed bootstrapping-shaped pipeline consumes, and report the elasticity of that count with respect to the parameter being changed.
- **`IDEA-20260816-552e4c`** -> `EXP-FHEX-736606` (mechanism, priority high, `RQ-FHE-001`)  
  Treat an approximate scheme's decryption error as a communication channel rather than a precision issue: at toy parameters with an enumerable secret space, count in bits per released result how much the low-order error carries about the secret, and count the same for an exact scheme's rounding residual.
- **`IDEA-20260816-560157`** -> `EXP-FHEX-5e6e4f` (measurement, priority high, `RQ-FHE-001`)  
  Report the noise model as a ratio rather than a bound: instrument a fixed BFV-style multiplication chain so that at every level the measured noise magnitude is divided by the value the scheme's own worst-case recursion predicts, and follow that ratio sequence, not the noise, through the circuit.
- **`IDEA-20260816-63a0ea`** -> `EXP-FHEX-c44bb1` (composition, priority high, `RQ-FHE-001`)  
  Treat bootstrapping's insertion point as a measured quantity rather than a design choice: locate the level at which the transcribed noise model says decryption must fail and the level at which it actually fails, and report the gap in whole levels rather than in bits.
- **`IDEA-20260816-6fae7b`** -> `EXP-FHEX-484181` (mechanism, priority high, `RQ-FHE-001`)  
  Noise models treat the noise as independent of the message, but modulus switching rounds a message-scaled quantity; measure the decryption-noise variance conditioned on the plaintext, exhaustively over every plaintext at a tiny plaintext modulus, and report the spread across plaintext classes.
- **`IDEA-20260816-93ca21`** -> `EXP-FHEX-847eff` (tooling, priority high, `RQ-FHE-001`)  
  Before any measured-versus-modelled noise claim can be believed, the phrase 'the model' must name one object: implement two standard noise recursions, the worst-case infinity-norm one and the variance-plus-tail one, run both over the identical recorded ciphertext trace, and measure how far apart they are.
- **`IDEA-20260816-df7016`** -> `EXP-FHEX-f5db3b` (measurement, priority medium, `RQ-FHE-001`)  
  Noise flooding is calibrated from an estimate of the noise it must hide; measure, at toy parameters with two enumerable secrets, the total variation distance between flooded release distributions as a function of the flooding standard deviation, and locate the deviation at which the distance falls below measurement resolution.
- **`IDEA-20260816-ec9a47`** -> `EXP-FHEX-e14a38` (representation, priority medium, `RQ-FHE-001`)  
  The step from a noise variance to a noise infinity-norm assumes the N coefficients of the noise polynomial behave like independent draws; measure the eigenvalue spectrum of their covariance matrix in the DFT basis after each homomorphic operation and report how far from white it is.
- **`IDEA-20260816-ff04de`** -> `EXP-FHEX-cd8414` (control, priority high, `RQ-FHE-001`)  
  Stress the one independence assumption a homomorphic product's noise bound cannot do without: measure the empirical correlation between the noise vector of a ciphertext product and the noise vectors of its two factors, exhaustively at ring degrees where every plaintext and every secret can be enumerated.

### `FRODOFO` — FrodoKEM and the FO transform

- **`IDEA-20260816-1418f4`** -> `EXP-FRODOFO-cfc5b8` (control, priority high, `RQ-FRODO-3260cc`)  
  Measure the correlation matrix of per-coordinate decryption-failure indicators in an unstructured LWE encryption and in a negacyclic one at matched marginal failure probability and matched coordinate count, so that the correlation attributable to ring structure alone becomes a number with an error bar rather than an assumption.
- **`IDEA-20260816-32c366`** -> `EXP-FRODOFO-2ffb29` (measurement, priority high, `RQ-FRODO-a2dbe2`)  
  A per-ciphertext salt is a hash-input partition, so measure it as one: build the target-hit multiset of a multi-target hash search over U users and C ciphertexts each, with and without a salt of length s, and measure the exponent at which the number of targets hit per hash query stops growing.
- **`IDEA-20260816-3949c8`** -> `EXP-FRODOFO-7a2724` (theory, priority medium, `RQ-FRODO-3260cc`)  
  A Fujisaki-Okamoto argument wants a worst-case correctness error but a published delta is an average, so track the whole map from message to failure probability and measure its spread in an unstructured Frodo-shaped encoding, where translation invariance predicts a flat map, against a compressed encoding where it does not.
- **`IDEA-20260816-583998`** -> `EXP-FRODOFO-c7b77b` (theory, priority medium, `RQ-FRODO-a2dbe2`)  
  State the ROM-to-QROM gap for one transform as an integer vector, not as a sentence: extract the exponent of every input variable in each model, subtract, and convert the difference vector into a single bit-security movement at a frozen evaluation point, so that the gap becomes one auditable number per parameter set.
- **`IDEA-20260816-72e5e5`** -> `EXP-FRODOFO-f42257` (control, priority high, `RQ-FRODO-a2dbe2`)  
  Certify that a reduction-evaluation pipeline is an instrument and not a fixed-answer generator, using unstructured FrodoKEM as the free control: feed it two schemes matched on every input the bound actually consumes and demand that its output difference be exactly zero, then feed it deliberately mismatched inputs and demand that it move.
- **`IDEA-20260816-7b9457`** -> `EXP-FRODOFO-1978c5` (composition, priority medium, `RQ-FRODO-a2dbe2`)  
  Join the two FrodoKEM questions by propagating an interval, not a point: take an uncertainty range on the correctness error and push it through the reduction bound in certified interval arithmetic, then measure how much of the resulting bit-security width is real and how much is manufactured by the dependency problem of repeated occurrences.
- **`IDEA-20260816-8596af`** -> `EXP-FRODOFO-fc2bff` (measurement, priority medium, `RQ-FRODO-a2dbe2`)  
  A reduction quoted asymptotically and used as if tight has a ledger of forgiven factors: enumerate every constant, lower-order term and absorbed inequality dropped along a chain of game hops, multiply them, and report the accumulated amnesty as one number in bits with an audit trail naming where each factor was forgiven.
- **`IDEA-20260816-9bec34`** -> `EXP-FRODOFO-c8cea1` (tooling, priority medium, `RQ-FRODO-a2dbe2`)  
  Build an executable quantifier-order linter for reduction statements: encode a security claim as an ordered binder sequence with dependency edges, and have the tool flag every witness that is allowed to depend on something the claimed uniform conclusion forbids, calibrated on statements deliberately mis-ordered by construction.
- **`IDEA-20260816-adf2a2`** -> `EXP-FRODOFO-663058` (mechanism, priority high, `RQ-FRODO-a2dbe2`)  
  Implicit and explicit rejection are two different functions, not two styles: build both decapsulators for a toy unstructured-LWE KEM, enumerate the malformed-ciphertext classes, and measure on how many of them the two functions are functionally indistinguishable to an adversary who sees only outputs and never a timing.
- **`IDEA-20260816-d270bc`** -> `EXP-FRODOFO-43f33d` (representation, priority medium, `RQ-FRODO-a2dbe2`)  
  Treat the FrodoKEM IND-CCA bound not as a number but as a label field: over the grid of hash queries, decapsulation queries, failure rate, user count and ciphertext count, record only WHICH additive term is largest, and ask whether the resulting dominance partition has the small, piecewise-monotone cell structure a correctly transcribed reduction ledger must have.

### `HAWKL` — HAWK and module-LIP

- **`IDEA-20260816-6605ac`** -> `EXP-HAWKL-46ac46` (tooling, priority high, `RQ-HAWK-001`)  
  Every committed HAWK-lane record works on HAWK-SHAPED instances from a declared rule rather than on HAWK, and nothing has ever measured what that substitution costs; build a generator-fidelity battery that reports, per statistic, how far the declared rule is from a stated reference family.
- **`IDEA-20260816-79af89`** -> `EXP-HAWKL-b7fab1` (representation, priority medium, `RQ-HAWK-001`)  
  Treat the public quadratic form as the first rung of a projection ladder rather than as the instance, and find the first rung at which the re-randomisation action stops acting deterministically, delivering an honest lossy-projection verdict that names which rungs are mere changes of coordinates.
- **`IDEA-20260816-955659`** -> `EXP-HAWKL-9771b0` (theory, priority high, `RQ-HAWK-001`)  
  Write the module-LIP to nrd-PIP to subfield chain with explicit quantifier order and run the method-ceiling audit: does any witness depend on the instance in a way the uniform conclusion forbids, and what could the representation search prove even with density one?
- **`IDEA-20260816-b3478d`** -> `EXP-HAWKL-a26a1a` (control, priority high, `RQ-HAWK-001`)  
  Build module-LIP and plain-LIP instances as a matched pair in which module structure over the cyclotomic ring is the only difference, holding dimension, determinant, construction rule and seed fixed, and measure whether any eligible isometry invariant separates the two arms at all.
- **`IDEA-20260816-b6de60`** -> `EXP-HAWKL-8adc6a` (measurement, priority medium, `RQ-HAWK-001`)  
  Treat a HAWK-shaped signature transcript as a communication channel and count its leakage rate in bits per signature about the secret Gram matrix, using an estimator whose floor is measured in the same run on transcripts generated from a public-equivalent basis.
- **`IDEA-20260816-ddee51`** -> `EXP-HAWKL-844dd9` (composition, priority high, `RQ-HAWK-001`)  
  Compose the one mechanism that survived its cost correction with the one route that needs no heuristics: does conjugating the public form by short unimodular matrices ever lower the dimension of the exact-SVP call the unconditional reduction bottoms out in, or is n/2+1 a measured floor at toy degree?
- **`IDEA-20260816-e9ca55`** -> `EXP-HAWKL-a16195` (theory, priority high, `RQ-HAWK-001`)  
  Split the four numbered heuristics of the nrd-PIP route into a directed dependency graph of separately testable predicates, then determine which of the three survivors are load-bearing for anything beyond the density claim that already failed, so each survivor carries its own falsifier rather than inheriting a block verdict.
- **`IDEA-20260816-ebedd8`** -> `EXP-HAWKL-93da74` (mechanism, priority high, `RQ-HAWK-001`)  
  Read the failed density heuristic as a resource rather than an obstruction: the recorded measurement that the easy-instance density vanishes under bounded-denominator sampling is the shape of hypothesis a re-randomisation-as-mixing argument wants, and this entry names which theory takes it up and which cannot.
- **`IDEA-20260816-eed484`** -> `EXP-HAWKL-aebc3f` (control, priority medium, `RQ-HAWK-001`)  
  Is 'unusually easy instance' a predicate anyone can evaluate without running the solver, or is it defined only by the solver succeeding? Measure the predictive power of cheap pre-solve predicates against exact ground truth at toy scale, with label shuffling as the null.
- **`IDEA-20260816-f2575b`** -> `EXP-HAWKL-038e6c` (measurement, priority high, `RQ-HAWK-001`)  
  The Case C closure gives the SIGN of the easy-instance density decay and never its MAGNITUDE; measure the decay exponent directly by exact enumeration of bounded-denominator fractional ideals of fixed relative norm in small CM fields, without reopening any question KN-OPEN-028 closed.

### `HQCX` — HQC decoding failure and code structure

- **`IDEA-20260816-208783`** -> `EXP-HQCX-ecbf93` (mechanism, priority high, `RQ-HQC-001`)  
  EV-HQC-b71230 measured HQC's inner-block joint failure moments falling below the independence prediction at every order from k equals 2 to 18; propose the cheapest candidate mechanism - fixed-weight rather than Bernoulli sampling of the five inputs - and test it by ablating only the sampler in the same harness, leaving code, estimator and thresholds untouched
- **`IDEA-20260816-2e03d4`** -> `EXP-HQCX-54e990` (mechanism, priority medium, `RQ-HQC-001`)  
  The inner decoder resolves maximum-likelihood ties by a fixed deterministic rule rather than a coin, so every symmetry argument about HQC's failure statistics silently assumes something the deployed decoder does not do; measure the tie rate and run a random-tie-break arm beside the deterministic one to bound what the convention alone can move
- **`IDEA-20260816-3994ef`** -> `EXP-HQCX-7d27e5` (composition, priority high, `RQ-HQC-001`)  
  Separate the claim that HQC's failure model is wrong from the claim that its two-stage decoder is suboptimal by running a genuine maximum-likelihood decoder for the WHOLE concatenated code beside the deployed inner-then-outer decoder on identical error vectors, at reduced parameters where full maximum likelihood is affordable
- **`IDEA-20260816-50d270`** -> `EXP-HQCX-32e045` (tooling, priority medium, `RQ-HQC-001`)  
  Every decoding-failure number this campaign has produced rests on a single implementation of the concatenated decoder; build a second implementation from an independent derivation, cross-check the two bit-for-bit on a shared corpus, and calibrate the cross-check with seeded mutations whose effect size is predicted before injection
- **`IDEA-20260816-6536d7`** -> `EXP-HQCX-000e81` (tooling, priority medium, `RQ-HQC-001`)  
  The inner Reed-Muller decoder scores every codeword, so the block failure event is the sign of a continuous margin - best correlation minus runner-up; measure that margin's distribution and use it as a variance-reduced failure-rate estimator, validated against direct counting in the regime where both are affordable and refused outside it
- **`IDEA-20260816-6f9d8f`** -> `EXP-HQCX-acebc0` (representation, priority medium, `RQ-HQC-001`)  
  Take the cyclic autocorrelation profile of a secret support - the multiset of differences j minus i over ordered pairs of support positions - as the tracked object of HQC's quasi-cyclic ring, apply the lossy-projection test to it honestly, and measure at which step of the encryption pipeline it stops propagating: the integer convolution, the mod-2 reduction, or the truncation
- **`IDEA-20260816-967721`** -> `EXP-HQCX-c67e50` (control, priority medium, `RQ-HQC-001`)  
  Treat HQC's deployed fixed-weight sampler as an object with its own null: measure the position-index marginal, the gap distribution and the rejection statistics of the procedure actually specified, against an exact-uniform Fisher-Yates null at identical length and weight, with an exhaustive ground truth at sizes where every support can be enumerated
- **`IDEA-20260816-b0322a`** -> `EXP-HQCX-9cc3a7` (control, priority high, `RQ-HQC-001`)  
  Run HQC's deployed concatenated Reed-Muller/Reed-Solomon decoder twice in one invocation - once over the quasi-cyclic ring and once over a matched non-circulant random-linear surrogate of identical length, rate, weight profile and sampler - and ask whether the block-failure-count distribution moves at all, separating quasi-cyclicity as exploitable object from quasi-cyclicity as keysize optimisation
- **`IDEA-20260816-b336a3`** -> `EXP-HQCX-12b5f9` (measurement, priority high, `RQ-HQC-001`)  
  Count in bits how much information about the secret one observed HQC decoding failure carries, using the block-failure PATTERN vector rather than the scalar failure event, by bias-corrected empirical mutual-information estimation at reduced parameters, against a label-permutation null and a key-independent-failure null where the answer is forced to be zero
- **`IDEA-20260816-b68344`** -> `EXP-HQCX-b341c4` (theory, priority high, `RQ-HQC-001`)  
  HQC truncates its length-n error to the first N equals n_e times n_2 coordinates before decoding; take the coordinate covariance of the untruncated error as the tracked object, derive at zero compute that it is exactly circulant, and test the forced consequence that pairwise block-failure probabilities depend only on block separation while per-block marginals are exactly equal

### `LATDUAL` — LWE primal versus dual and the structure discount

- **`IDEA-20260816-08eda1`** -> `EXP-LATDUAL-269788` (tooling, priority high, `RQ-MLKEM-003`)  
  Treat the lattice estimator as an instrument under calibration rather than as a source of measurements: measure the signed residual between its predicted cost and the directly observed cost on instances whose recovery is run to completion, and report the residual's drift with dimension
- **`IDEA-20260816-58dfe7`** -> `EXP-LATDUAL-a6a0ce` (theory, priority high, `RQ-MLKEM-003`)  
  Build the convention-transport map KN-OPEN-016 names as its closure condition: derive, at zero compute, how much of the primal-minus-dual bit gap is contributed by the cost convention rather than by the attacks, and report whether the gap's sign is convention-stable
- **`IDEA-20260816-70e41d`** -> `EXP-LATDUAL-ebb197` (measurement, priority high, `RQ-MLKEM-003`)  
  Locate the enumeration/sieving crossover as a curve over a one-parameter memory price rather than as a single dimension quoted at free memory, by measuring step counts and peak list sizes for both algorithms on identical lattices and composing them with a priced cost functional
- **`IDEA-20260816-725f05`** -> `EXP-LATDUAL-89afec` (mechanism, priority medium, `RQ-MLKEM-003`)  
  The waterfall-floor as a tracked object: measure whether a dual distinguisher's success probability plateaus below one as the dual-vector budget grows, and whether that plateau survives the one control that can distinguish a real floor from a scoring artifact
- **`IDEA-20260816-7bc28c`** -> `EXP-LATDUAL-ebf3cf` (measurement, priority medium, `RQ-MLKEM-003`)  
  Price the sieve's memory by its access pattern rather than its size: measure the locality exponent of a Gauss-style sieve's near-neighbour list accesses, and report how the memory-charged crossover moves when the wiring model is chosen by measurement instead of assumption
- **`IDEA-20260816-b824af`** -> `EXP-LATDUAL-65c31b` (control, priority high, `RQ-MLKEM-003`)  
  Measure the module-structure discount as a ratio between matched structured and unstructured instances of identical dimension, modulus, secret law, error law and sample count, using the required BKZ blocksize for primal recovery as the per-instance observable where recovery actually happens
- **`IDEA-20260816-ba5bd8`** -> `EXP-LATDUAL-194b83` (measurement, priority high, `RQ-MLKEM-003`)  
  Replace the contested dual-attack probability model with an ordinal statistic: the rank of the true secret's FFT score among all enumerable candidates, measured directly at dimensions where the secret is known by construction, against the rank law the independence heuristic forces
- **`IDEA-20260816-bd7f26`** -> `EXP-LATDUAL-70b187` (measurement, priority medium, `RQ-MLKEM-003`)  
  Settle KN-OPEN-026's Q3 as an interaction term rather than a regime claim: run a two-factor design crossing structured versus unstructured with secret sparsity, and report whether the discount's dependence on sparsity is an interaction or an offset
- **`IDEA-20260816-f4ce0b`** -> `EXP-LATDUAL-57d3f4` (representation, priority low, `RQ-MLKEM-003`)  
  Represent the structure discount by the size of the instance's coefficient-isometry orbit rather than by the name of its ring, and test whether the discount obeys an amortisation law in that one integer across rings chosen to vary orbit size at fixed degree
- **`IDEA-20260816-fdc8e8`** -> `EXP-LATDUAL-3771b8` (composition, priority medium, `RQ-MLKEM-003`)  
  Pose KN-OPEN-026's growth question as a trend across technique quality rather than across dimension: measure the structured/unstructured blocksize ratio under three techniques of increasing strength on identical matched pairs, and report whether the discount is monotone in technique

### `MCEGOP` — Classic McEliece and binary Goppa structure

- **`IDEA-20260816-023239`** -> `EXP-MCEGOP-1a0c4f` (measurement, priority high, `RQ-MCE-e65b3c`)  
  Stop reporting the square-code dimension defect as a difference of means and measure it as a per-key decision: build the full empirical distribution of the defect over hundreds of toy Goppa keys and matched random codes at identical length and dimension, and report the ROC curve, the equal-error rate and the overlap region instead of a gap between averages.
- **`IDEA-20260816-0b8dff`** -> `EXP-MCEGOP-1bbd00` (measurement, priority medium, `RQ-MCE-b38a8b`)  
  Map the toy Goppa code's decoding region past its designed radius: for every error weight w = 0..2t measure the decoder's three outcomes -- correct, detected failure, silent miscorrection -- and compare the resulting profile against a coset-leader decoder on a matched random code, since the SHAPE of the failure cliff is a mathematical observable, not an implementation property.
- **`IDEA-20260816-118177`** -> `EXP-MCEGOP-eda5d6` (tooling, priority high, `RQ-MCE-b38a8b`)  
  Build and exhaustively certify a valid binary Goppa key pair at m in 4..6 in dependency-free Python -- support L, squarefree g, the GF(2^m) parity check, its GF(2) trace expansion, a syndrome decoder -- so that every later structural claim in this bucket has a hash-pinned fixture whose ground truth is known by enumeration rather than asserted in prose.
- **`IDEA-20260816-293dd3`** -> `EXP-MCEGOP-c1b8e1` (control, priority high, `RQ-MCE-b38a8b`)  
  The matched random code is an instrument too: measure whether the three obvious ways to sample a random binary [n,k] code -- rank-rejected parity check, rank-rejected generator, and the systematic form [I | A] that implementations actually use -- induce different distributions of hull dimension, square-code defect and minimum distance.
- **`IDEA-20260816-2b2ccd`** -> `EXP-MCEGOP-3eeba9` (representation, priority medium, `RQ-MCE-b38a8b`)  
  Count the fibre instead of assuming it: for a fixed toy Goppa public code, measure how many distinct secret parametrisations (L, g) generate exactly the same GF(2) row space, by exhaustive enumeration at the smallest field and by a bounded Monte Carlo collision search above it, and compare the measured count against the orbit size of the declared trivial-equivalence group.
- **`IDEA-20260816-554b67`** -> `EXP-MCEGOP-bbda24` (measurement, priority high, `RQ-MCE-e65b3c`)  
  Execute rather than tabulate: run Prange and Stern on the toy Goppa fixture and on matched random codes with planted errors at n = 16..64, count iterations, peak list memory and collisions per iteration, and report the measured ratio between the two arms, because structure-blindness of generic decoding has never been measured here.
- **`IDEA-20260816-576d70`** -> `EXP-MCEGOP-c82479` (theory, priority high, `RQ-MCE-e65b3c`)  
  Compile this program's own committed reading of the arXiv:2304.14757 boundary -- RQ-MCE-3f7c02's family exclusion as completed by RQ-MCE-f8fca0's present-tense, phase-scoped, explicitly-unproved qualification -- into a three-valued machine-checkable predicate over a parameter tuple, and lint every committed GOAL-MCE-001 deliverable sentence against it.
- **`IDEA-20260816-9c7e2d`** -> `EXP-MCEGOP-9006b1` (mechanism, priority medium, `RQ-MCE-e65b3c`)  
  A structural tell must persist under an operation that preserves the family: shorten the toy Goppa code one coordinate at a time and measure whether the square-code defect stays correlated down the chain while a random code's defect re-draws at every step -- the AUTOCORRELATION along the chain, not the value at any one point, is the object.
- **`IDEA-20260816-e36836`** -> `EXP-MCEGOP-b0b627` (tooling, priority medium, `RQ-MCEQ-fcb504`)  
  Before asking whether the two-sided matrix-code action blocks invariant-based distinguishers, measure what those distinguishers cost when they DO work: the false-positive rate, false-negative rate and stall rate of a hull-plus-weight-enumerator coordinate signature on random binary codes, as a function of hull dimension, with permuted copies as the positive control.
- **`IDEA-20260816-ef56f2`** -> `EXP-MCEGOP-541077` (composition, priority high, `RQ-MCE-e65b3c`)  
  Every structural claim in this bucket needs a null, so build the LADDER rather than a single null: random binary code, random alternant, Goppa with reducible g, Goppa with non-squarefree g, honest Goppa -- and report for each candidate statistic the exact rung at which it stops separating, as a statistic-by-rung separation matrix with a same-rung self-null in every cell.

### `MDFIVE` — MD5 collision/preimage asymmetry

- **`IDEA-20260816-13db82`** -> `EXP-MDFIVE-1b33df` (theory, priority high, `RQ-MDFIVE-6870c1`)  
  Before any method-ceiling claim is made about MD5, run the identifiability audit on the observable that would carry it: rewrite the claim with explicit quantifier order and hunt for two objects with the same observable lying on opposite sides of the intended conclusion.
- **`IDEA-20260816-3e6af3`** -> `EXP-MDFIVE-553fc2` (tooling, priority high, `RQ-MDFIVE-6870c1`)  
  Validate the condition-counting instrument itself before any MD5 claim rests on it: predict path probability from a sufficient-condition count on a primitive small enough to enumerate exhaustively, then measure the true probability and report the predicted-to-actual ratio as the instrument's error bar.
- **`IDEA-20260816-520dda`** -> `EXP-MDFIVE-5aae9d` (theory, priority high, `RQ-MDFIVE-6870c1`)  
  Measure the local steerability of a k-bit difference constraint against a k-bit value constraint at the same step of the same function, using one identical local-modification routine for both, and test whether the collision-preimage gap is a property of constraint type rather than of the primitive.
- **`IDEA-20260816-585c93`** -> `EXP-MDFIVE-1f842a` (measurement, priority high, `RQ-MDFIVE-6870c1`)  
  Count MD5's remaining degrees of freedom and its unsatisfied sufficient conditions as two separate running totals indexed by step, computed once under collision boundary conditions and once under preimage boundary conditions, and locate the exact step index where the two accountings first diverge.
- **`IDEA-20260816-79aec0`** -> `EXP-MDFIVE-835cd4` (composition, priority high, `RQ-MDFIVE-6870c1`)  
  Take Merkle-Damgard strengthening as the object: count exactly which message words the padding and length encoding pin in the final block, cross-reference them against the schedule to see which side of a split loses neutral words, and show the same pinning costs a collision path nothing.
- **`IDEA-20260816-85ce8c`** -> `EXP-MDFIVE-b843fb` (representation, priority medium, `RQ-MDFIVE-6870c1`)  
  Transfer the asymmetry question by changing one design axis only: compare the split statistics of a permutation-type message schedule, where sixteen words are each reused, against a recurrence-type schedule that expands sixteen words into many, holding step count and state size fixed, and name the transfer assumption.
- **`IDEA-20260816-9b3b6b`** -> `EXP-MDFIVE-4e2ea8` (measurement, priority medium, `RQ-MDFIVE-6870c1`)  
  Measure how a single-bit state perturbation spreads forward through MD5's step function versus backward through its exact inverse, treating the difference support as the tracked object, and test whether the carry direction of modular addition makes the two wavefronts structurally unequal.
- **`IDEA-20260816-c20a5b`** -> `EXP-MDFIVE-b8d369` (measurement, priority medium, `RQ-MDFIVE-6870c1`)  
  Build a scaled-down MD5-shaped hash with a 32-bit chaining state whose true collision and preimage costs are both exhaustively verifiable, and measure how the attacker's gain over the generic bound in each setting evolves as the round count is increased one round at a time.
- **`IDEA-20260816-d285e8`** -> `EXP-MDFIVE-b64111` (mechanism, priority high, `RQ-MDFIVE-6870c1`)  
  Treat MD5's 64-step message schedule alone as the object and measure, across random schedules with the same word-multiplicity profile, whether the collision-favourable statistic and the preimage-favourable statistic are correlated, then ask whether MD5 is an outlier in one coordinate but not the other.
- **`IDEA-20260816-e40ea1`** -> `EXP-MDFIVE-914bd3` (control, priority high, `RQ-MDFIVE-6870c1`)  
  Use MD4 and MD5 as a paired control to filter candidate mechanisms: require every proposed explanatory quantity to be computed by one identical instrument on both primitives and to move in the direction and rough magnitude that the reported difference between them demands, discarding those that do not.

### `MULTIV` — Multivariate signatures (MAYO, UOV, QR-UOV, SNOVA)

- **`IDEA-20260816-0a9533`** -> `EXP-MULTIV-0ac0a3` (measurement, priority medium, `RQ-SNOVA-001`)  
  Signatures without repetition as the tracked object: measure whether the empirical second-moment matrix of many honestly generated SNOVA-shaped signatures under one key is biased toward the secret oil module, against a null of uniformly resampled valid preimages of the same digests under the same key.
- **`IDEA-20260816-0f7694`** -> `EXP-MULTIV-18f7fa` (control, priority high, `RQ-QRUOV-001`)  
  Structure as a dose, not a switch: build keys in which only a controlled fraction of the blocks are quotient-ring linear, then measure solving degree and solver cost as a function of that fraction, so the zero-dose arm is the null and the full-dose arm is QR-UOV, in one continuous curve.
- **`IDEA-20260816-10e308`** -> `EXP-MULTIV-1f440b` (measurement, priority high, `RQ-UOV-001`)  
  Treat Kipnis-Shamir as an instrument rather than an attack: run its invariant-subspace test unchanged against random MQ systems, against structure-shaped systems with no oil space, and against genuine UOV keys, and publish its measured false-positive rate as a number with its parameter dependence.
- **`IDEA-20260816-347b82`** -> `EXP-MULTIV-c9200b` (composition, priority high, `RQ-UOV-001`)  
  One core, four transforms, sixteen composites: a zero-compute audit table stating for each ordered pair of the whipping, quotient-ring, noncommutative-ring and seed-compression transforms whether the composite is defined, what parameter triple and coefficient algebra it produces, and which composites are degenerate.
- **`IDEA-20260816-41ab94`** -> `EXP-MULTIV-8d2cc3` (tooling, priority high, `RQ-UOV-001`)  
  Build the shared instrument this bucket keeps assuming exists: one core UOV kernel plus four pluggable transforms and one matched null generator, with exhaustively verified ground truth at tiny parameters, so that any later measurement runs byte-identically on all four schemes and on nothing.
- **`IDEA-20260816-728064`** -> `EXP-MULTIV-5fc55b` (composition, priority medium, `RQ-MAYO-001`)  
  A zero-compute commuting-square audit of two transforms that both act on a UOV map: does whipping commute with Weil restriction to the prime field, and if the square fails to commute, is the discrepancy an object with its own parameter triple and its own oil module?
- **`IDEA-20260816-7fe6c0`** -> `EXP-MULTIV-c95670` (measurement, priority medium, `RQ-MAYO-001`)  
  Measure what whipping buys before pricing what it costs: the rank distribution of MAYO's signing linear system, the map x -> P-star-polar(v, x) restricted to the whipped oil space, as a function of the whipping factor k, against a matched uniform random matrix null of identical shape over the same field.
- **`IDEA-20260816-8c5f12`** -> `EXP-MULTIV-5a040c` (measurement, priority high, `RQ-UOV-001`)  
  Key recovery is not a point, it is a curve: measure solving degree and solver cost against the number of oil vectors already known, from zero to the full oil dimension, on toy UOV keys and on a random system with an identically planted partial solution, and report the whole gradient.
- **`IDEA-20260816-b0046a`** -> `EXP-MULTIV-3bfcc9` (representation, priority medium, `RQ-QRUOV-001`)  
  One statistic, four schemes, one null: measure the rank distribution of uniformly random elements of the F_q-span of a public key's coefficient matrices, and report it as a fingerprint per scheme against a matched random symmetric matrix space of identical dimension.
- **`IDEA-20260816-e810c8`** -> `EXP-MULTIV-6e5d90` (theory, priority medium, `RQ-SNOVA-001`)  
  Count the targets, not the haystack: measure the fibre of the key-generation map by exhaustively enumerating, at tiny parameters, how many distinct secret oil modules produce the identical public key in each of the four schemes, and compare that multiplicity against a matched plain UOV of the same flattened dimensions.

### `NTRUL` — NTRU lattice structure

- **`IDEA-20260816-00b29e`** -> `EXP-NTRUL-f76d97` (composition, priority medium, `RQ-NTRU-9015ee`)  
  Transport one fixed NTRU instance across the modulus axis by modulus switching instead of resampling it, and test whether the density signature follows the lattice or follows the sampling, since a transition that is a property of the parameter set and one that is a property of each drawn key are different objects
- **`IDEA-20260816-03a2f5`** -> `EXP-NTRUL-bfa848` (theory, priority high, `RQ-NTRU-9015ee`)  
  Locate the overstretched transition per instance and without any lattice reduction, as the modulus at which the argmax over sublattice rank of the covolume-density advantage function jumps from rank one to rank greater than one for the actually sampled key
- **`IDEA-20260816-0732fb`** -> `EXP-NTRUL-63a211` (measurement, priority medium, `RQ-NTRU-9015ee`)  
  Measure the successive-minima ladder of a toy NTRU lattice by exhaustive certified enumeration and count the multiplicity of the minimum, testing whether the unique-shortest-vector gap that uSVP reasoning assumes exists at all in a lattice whose secret comes with a full rotation orbit
- **`IDEA-20260816-2f344d`** -> `EXP-NTRUL-b69f49` (representation, priority medium, `RQ-NTRU-9015ee`)  
  Quantify the coordinate budget before any cross-ring comparison is believed: compute the distortion between coefficient and canonical embeddings for each candidate NTRU ring to certified precision, and declare that any measured cross-ring difference below that budget is a change of coordinates rather than a structural effect
- **`IDEA-20260816-36a599`** -> `EXP-NTRUL-57eaf9` (theory, priority medium, `RQ-NTRU-9015ee`)  
  Ask what a transition exponent fitted on a bounded dimension window can possibly identify: enumerate candidate laws for the transition location, compute the smallest dimension at which each pair becomes separable at a stated measurement precision, and report the window this program would need before an exponent means anything
- **`IDEA-20260816-49b818`** -> `EXP-NTRUL-7e521f` (mechanism, priority high, `RQ-NTRU-9015ee`)  
  Build a block-circulant family that interpolates continuously from matrix NTRU to ring NTRU at fixed dimension, determinant and secret norm, with the orbit rank as the only moving part, and measure the structure discount as a function of that rank rather than as a yes-or-no
- **`IDEA-20260816-6e6f2e`** -> `EXP-NTRUL-8183f2` (mechanism, priority high, `RQ-NTRU-9015ee`)  
  Reduce what ring structure buys to one scalar per instance: the log-determinant gap between the rotation orbit's correlation matrix and the matched Wishart correlation of an independent plant of identical rank and identical per-vector norm, and measure how that scalar grows with n
- **`IDEA-20260816-c01dc8`** -> `EXP-NTRUL-57a5b2` (tooling, priority high, `RQ-NTRU-9015ee`)  
  Make matched mean something: define a lattice-control matching certificate over seven computable invariants, then measure which invariants the obvious matched unstructured controls actually fail, so that every later NTRU-versus-generic comparison in this program carries a mismatch budget instead of an adjective
- **`IDEA-20260816-cc82fa`** -> `EXP-NTRUL-85c834` (control, priority high, `RQ-NTRU-9015ee`)  
  Before the reduction profile is used as an observable of an NTRU lattice, test whether it is one: reduce three provably identical lattices presented in three different bases at the same budget and measure how far apart the resulting Gram-Schmidt profiles are relative to the dense-sublattice kink they are meant to detect
- **`IDEA-20260816-f5ceb4`** -> `EXP-NTRUL-42b820` (mechanism, priority medium, `RQ-NTRU-9015ee`)  
  Factor the ring modulo q and ask whether its CRT idempotents produce short lifts: measure the coefficient norm of the shortest lift of each submodule the splitting provides, testing whether a split ring hands an attacker genuine low-rank dense sublattices or only long ones

### `PMA` — Principal-minor assignment and divisor parity

- **`IDEA-20260816-398c6b`** -> `EXP-PMA-69ebae` (composition, priority medium, `RQ-PMA-001`)  
  Turn the obstruction over per inventor-protocol section 4 by measuring it as a resource: certificate bits emitted against decider branches avoided, and the yield of a generator of prescribed tables that are certifiably non-realizable over k(t) yet realizable over a quadratic extension, which is what such an obstruction would be a supply of
- **`IDEA-20260816-5c040d`** -> `EXP-PMA-eeecbf` (measurement, priority high, `RQ-PMA-001`)  
  Decompose the square-class gate into its two independent halves, the divisor-parity vector over finite places plus infinity and the residual constant class in k-star modulo squares, and measure which half actually fires and how often, since the question names divisor parity but the gate as frozen is a conjunction of two different obstructions
- **`IDEA-20260816-6c0db3`** -> `EXP-PMA-1f2390` (mechanism, priority medium, `RQ-PMA-001`)  
  Run the nearby-object control on the divisor-parity gate by moving from ordinary to symmetric 4x4 matrices, where the same data q_ij equals a_ij times a_ji becomes a_ij squared and therefore must itself be a square, and test whether the gate can tell the two realizability questions apart at all
- **`IDEA-20260816-86a78d`** -> `EXP-PMA-399545` (control, priority high, `RQ-PMA-001`)  
  Measure the obstruction density of the divisor-parity gate against two nulls of the same shape -- tables pulled back from actual matrices over k(t), on which the gate must never fire, and uniformly sampled tables of matched degree profile, on which its firing rate is the background -- so that any claimed obstruction has a denominator
- **`IDEA-20260816-d202cf`** -> `EXP-PMA-8985bd` (control, priority high, `RQ-PMA-001`)  
  Test whether the divisor-parity obstruction verdict is invariant under the twenty-four index relabellings of the four-element index set and under all four anchor choices, since a verdict that depends on the frozen anchor-1 triple selection is a property of the gauge and not of the prescribed minor table
- **`IDEA-20260816-d5d520`** -> `EXP-PMA-940ef2` (control, priority high, `RQ-PMA-001`)  
  Audit the frozen EXP-PMA-001 parameter box for arithmetic satisfiability before any compute is spent: fifteen pairwise-distinct d_S values excluding zero and one cannot be drawn from F_3, F_5 or F_7, so decide by counting whether the frozen finite-field grid can be instantiated at all
- **`IDEA-20260816-e5cedd`** -> `EXP-PMA-657f3b` (theory, priority medium, `RQ-PMA-001`)  
  Write out the quantifier order of the divisor-parity claim and test the one direction that is actually valid, namely that a square over k(t) stays square under every regular specialization t to a, by measuring specialization agreement and by hunting an observation collision -- two tables with identical square-class certificates on opposite sides of realizability
- **`IDEA-20260816-fbc1d3`** -> `EXP-PMA-034093` (representation, priority medium, `RQ-PMA-001`)  
  Replace the characteristic-2 refusal with a measured analogue: in char 2 the orientation quadratic has no discriminant, but it has an Artin-Schreier class, so build the class in F modulo the image of x squared plus x, measure whether it obstructs, and report the boundary as a computed invariant rather than a scope exclusion
- **`IDEA-20260816-fbe304`** -> `EXP-PMA-7dd949` (measurement, priority high, `RQ-PMA-001`)  
  Census the complete image of the 3x3 principal-minor map over F_q for q in 3, 5, 7 by exhaustive enumeration of every matrix, and publish the realizable 7-tuple set as a finite measured object against which any PMA obstruction predicate can be scored with zero remaining ground-truth uncertainty
- **`IDEA-20260816-fd8f23`** -> `EXP-PMA-0dd955` (tooling, priority high, `RQ-PMA-001`)  
  Find and publish the exact exhaustion boundary for 4x4 principal-minor assignment over F_q by quotienting the enumeration by the diagonal-conjugation torus and transposition first, reporting the largest (n, q) actually completed and the projected cost of the first pair that fails

### `POLYMAC` — GHASH and Poly1305 forgery-bound tightness

- **`IDEA-20260816-20e5d1`** -> `EXP-POLYMAC-e0ebdf` (theory, priority high, `RQ-POLYMAC-7c89e4`)  
  A zero-compute proof-architecture audit of the forgery bound: rewrite it with explicit quantifier order over key, message, adversary and query schedule, then search for observation collisions - two toy parameter settings with the same bound value and provably different achievable optima - in both fields
- **`IDEA-20260816-258c69`** -> `EXP-POLYMAC-f5114e` (composition, priority medium, `RQ-POLYMAC-7c89e4`)  
  Treat key commitment and forgery as two predicates on the same key space and measure whether the keys that make one cheap are the keys that make the other cheap, computing the joint distribution exhaustively in both fields rather than reasoning about the two failures separately
- **`IDEA-20260816-4b35b0`** -> `EXP-POLYMAC-67de7b` (representation, priority high, `RQ-POLYMAC-7c89e4`)  
  The forger does not choose a polynomial, it chooses a message: measure the ACHIEVABLE difference-coefficient set that each construction's block encoding permits, and test whether a fully split polynomial is realisable in each field, since a bound assuming free coefficient choice is being compared against a forger who does not have it
- **`IDEA-20260816-4ea533`** -> `EXP-POLYMAC-8fdfc5` (tooling, priority high, `RQ-POLYMAC-7c89e4`)  
  Build the paired exhaustive forgery oracle as the deliverable and measure its own validity: a field-size ladder that tests whether the measured-to-bound ratio is scale-invariant, because if it is not, every scaled-down analogue in this campaign is disqualified from extrapolation and that disqualification is the result
- **`IDEA-20260816-51869a`** -> `EXP-POLYMAC-7f9436` (measurement, priority high, `RQ-POLYMAC-7c89e4`)  
  Obtain the optimal forgery probability EXACTLY by enumerating difference-polynomial root sets over the entire key space in matched scaled-down GHASH and Poly1305 analogues, and report the measured-to-bound RATIO as a surface over message length and query count in both fields from one invocation
- **`IDEA-20260816-5a8d47`** -> `EXP-POLYMAC-3939d7` (measurement, priority high, `RQ-POLYMAC-7c89e4`)  
  Measure the nonce-misuse cliff as a candidate-set collapse curve rather than as a warning: count how many authentication-key candidates survive after r repeated-nonce pairs, exhaustively and in both fields, under a self-supplied misuse model with self-generated keys and traffic only
- **`IDEA-20260816-7b4369`** -> `EXP-POLYMAC-c86946` (measurement, priority medium, `RQ-POLYMAC-7c89e4`)  
  Locate the bound's tight region as a geometric object in the message-length by query-count plane, by mapping where the measured-to-bound ratio is nearest one in each field, and report the two fields' tight regions as overlapping or disjoint sets rather than as advice
- **`IDEA-20260816-8cb64b`** -> `EXP-POLYMAC-d85614` (measurement, priority high, `RQ-POLYMAC-7c89e4`)  
  Count the weak-key structure of both authentication-key spaces exactly rather than citing it: the multiplicative-order divisor lattice of a binary extension field against the clamped residue set of a prime field, reported as densities at the same target exposure and as a paired asymmetry
- **`IDEA-20260816-9a1ae2`** -> `EXP-POLYMAC-591c3e` (mechanism, priority medium, `RQ-POLYMAC-7c89e4`)  
  Ablate clamping as an operator rather than describe it: run the identical forgery measurement with the prime arm's key constraint on and off, using the unclamped binary arm and a transported constraint as the nearby-object controls that separate what clamping does from what the field does
- **`IDEA-20260816-d7d873`** -> `EXP-POLYMAC-6395fb` (control, priority high, `RQ-POLYMAC-7c89e4`)  
  Authentication-key persistence is the structural difference the deployed pair confounds with the field: build the two-by-two of field crossed with per-nonce key refresh, measure how the multi-query forgery optimum grows in q in each cell, and report the interaction

### `RSAPI` — RSA under partial information

- **`IDEA-20260816-4a70f7`** -> `EXP-RSAPI-10864e` (representation, priority high, `RQ-RSA-d46f02`)  
  Leakage on an arbitrary position set rather than a contiguous window: measure the contiguous-equivalent bit count of random subsets, arithmetic-progression subsets, and block-interleaved subsets of the prime's bit positions, at moduli small enough for exhaustion to certify every cell.
- **`IDEA-20260816-684f4a`** -> `EXP-RSAPI-cbbbb6` (theory, priority high, `RQ-RSA-d46f02`)  
  Compute at zero compute the three exact regions of the dimension-by-leakage plane - information-theoretically impossible, guaranteed under an exact shortest-vector oracle, and undecided between them - and report what fraction of the plane theory leaves undecided at concrete modulus sizes.
- **`IDEA-20260816-736c60`** -> `EXP-RSAPI-6f1f24` (composition, priority medium, `RQ-RSA-d46f02`)  
  Do two partial leaks add? Supply bits of a prime and bits of the private exponent at the same time, hold the total leaked bit count fixed, and measure whether the joint construction recovers where either leak alone fails, or whether the second leak is worth less than the bits it contains.
- **`IDEA-20260816-7d1ed0`** -> `EXP-RSAPI-232457` (control, priority high, `RQ-RSA-d46f02`)  
  Completeness is the property the method actually sells: enumerate by exhaustion every root inside the declared window at moduli small enough to do so, and measure what fraction of them the implemented pipeline returns, at the window boundary and inside it.
- **`IDEA-20260816-7d747d`** -> `EXP-RSAPI-9f4c97` (tooling, priority high, `RQ-RSA-d46f02`)  
  Instrument-validity audit of every reach measurement in this bucket: hold the construction, instances and budget fixed and vary only the reduction implementation, its floating-point precision and its block size, to find how much of a reported achievable fraction is a property of the reducer rather than of the mathematics.
- **`IDEA-20260816-a321ac`** -> `EXP-RSAPI-0cbd60` (theory, priority high, `RQ-RSA-d46f02`)  
  Test whether achievable reach is a function of the Howgrave-Graham slack alone: hold the pair (lattice dimension, log determinant) fixed while changing which shift set realises it, and ask whether two constructions with equal slack recover equal unknown-bit fractions.
- **`IDEA-20260816-b4e5b7`** -> `EXP-RSAPI-89a419` (measurement, priority high, `RQ-RSA-d46f02`)  
  The achievability ratio R(n, D) = (largest unknown-prime-bit fraction actually recovered inside a declared lattice and reduction budget) divided by (the same construction's own asymptotic reach), measured as a curve in modulus bit-length from 64 to 1024 bits on known-answer instances.
- **`IDEA-20260816-b5b822`** -> `EXP-RSAPI-34c4b9` (mechanism, priority high, `RQ-RSA-d46f02`)  
  Locate the binding step of the small-root construction by ablation rather than argument: disable or degrade exactly one stage at a time - shift-set shape, modulus-power multiplicity, Howgrave-Graham scaling, reduction strength, root read-off - and report which single change moves the achieved unknown-bit fraction furthest.
- **`IDEA-20260816-c9e5d2`** -> `EXP-RSAPI-7aa1c5` (measurement, priority medium, `RQ-RSA-d46f02`)  
  The bound is quoted as a threshold, but success is a curve: measure the width of the success transition in the leaked fraction at each modulus size and lattice dimension, and test whether the width narrows with size as a threshold picture requires or stays open as an artifact picture predicts.
- **`IDEA-20260816-cddd6b`** -> `EXP-RSAPI-7d773f` (representation, priority medium, `RQ-RSA-d46f02`)  
  Leaked bits that are sometimes wrong: hold the position set contiguous and corrupt a declared fraction of the revealed values, then measure how fast the achievable window collapses and whether a small-root construction degrades gracefully or falls off a cliff at a locatable error rate.

### `SHAONE` — SHA-1 chosen-prefix cost model

- **`IDEA-20260816-1e36fa`** -> `EXP-SHAONE-5fa884` (representation, priority high, `RQ-SHAONE-081e3a`)  
  Treat the near-collision block chain as a counted object: define N(k), the number of admissible inter-block chaining-value difference states surviving after k chained near-collision blocks, and derive the chosen-prefix cost as an explicit minimization over k rather than as a quoted total.
- **`IDEA-20260816-389b1b`** -> `EXP-SHAONE-630aa1` (measurement, priority medium, `RQ-SHAONE-081e3a`)  
  Measure the hardware efficiency coefficient that every device-hour figure silently sets to one: the ratio of attack-loop compression-function throughput to the same device's peak straight-line hashing throughput, mapped against message-modification condition depth on the hardware this harness actually has.
- **`IDEA-20260816-3edd14`** -> `EXP-SHAONE-ceaedd` (theory, priority high, `RQ-SHAONE-081e3a`)  
  Count the detector's coverage instead of describing it: enumerate the disturbance-vector class as a finite indexed set generated by the local-collision recurrence, mark each element as covered or uncovered by the re-implemented criterion, and report coverage as a fraction with the uncovered elements named individually.
- **`IDEA-20260816-70b60d`** -> `EXP-SHAONE-febbd6` (control, priority high, `RQ-SHAONE-081e3a`)  
  Treat the deployed counter-cryptanalysis collision detector as a measuring instrument rather than a safety property: re-implement its predicate from primary specification and measure its false-positive rate on benign corpora and its true-positive rate on MD5-scale near-collision objects the harness can actually build.
- **`IDEA-20260816-71d4dd`** -> `EXP-SHAONE-536e2d` (measurement, priority high, `RQ-SHAONE-081e3a`)  
  Charge the birthday phase what it actually spends: measure the distinguished-point parallel collision search's achieved-versus-ideal efficiency as a function of table memory, node count and interconnect latency on a truncated-hash analogue where every collision can be exhaustively enumerated and verified.
- **`IDEA-20260816-8e0b9c`** -> `EXP-SHAONE-12ede4` (measurement, priority medium, `RQ-SHAONE-081e3a`)  
  Measure the identical-prefix to chosen-prefix cost ratio as a law rather than a folklore factor: run both attacks end to end at three scaled-down analogue widths where exhaustive verification is possible, and report the ratio and its trend with width against a random-target null.
- **`IDEA-20260816-962936`** -> `EXP-SHAONE-587147` (tooling, priority medium, `RQ-SHAONE-081e3a`)  
  Replace the dollar figure with an elasticity vector: build a cost model whose declared inputs are device price, device throughput, memory price, power and duty factor, compute each output's partial elasticity to each input, and report which single input carries most of the variance instead of quoting a number.
- **`IDEA-20260816-ade53e`** -> `EXP-SHAONE-5482c3` (mechanism, priority high, `RQ-SHAONE-081e3a`)  
  Charge the restarts: measure the distribution of abort depth in near-collision block search, test whether per-block cost is geometric as an expected-value cost model implicitly assumes, and report the tail index that determines how badly a mean-based budget under-provisions.
- **`IDEA-20260816-d3151e`** -> `EXP-SHAONE-3f4ee0` (measurement, priority medium, `RQ-SHAONE-081e3a`)  
  Decide semantic collision-exploitability as a two-level predicate over container-format grammars: for a named finite set of formats, mechanically test whether the SHA-1-hashed region admits an attacker-length-free uninterpreted field (P1) and whether that field is reachable and rendering-divergent (P2), then report the counts of passes and the enumerated reason each fail fails.
- **`IDEA-20260816-fa13f6`** -> `EXP-SHAONE-07376f` (mechanism, priority medium, `RQ-SHAONE-081e3a`)  
  Ask whether the birthday phase is reusable across targets: measure the marginal cost of the Nth chosen-prefix collision when the search state is retained, at analogue scale where all N collisions can be produced and verified, and report the amortization exponent against a cold-start baseline.

### `SHATHREE` — SHA-3 / Keccak internal-differential frontier

- **`IDEA-20260816-0a8d21`** -> `EXP-SHATHREE-665b36` (control, priority high, `RQ-SHATHREE-cd2cb2`)  
  The symmetry-decay curve depends on the round constants only through RC XOR tau(RC), so an entire 2^768 fiber of distinct constant schedules shares one curve exactly: hold the observable fixed, vary the forgotten structure, and test directly whether the curve identifies anything a search can feel
- **`IDEA-20260816-13b1ca`** -> `EXP-SHATHREE-d1158e` (control, priority high, `RQ-SHATHREE-cd2cb2`)  
  The nearby-object control this bucket cannot skip: build a random permutation of exactly Keccak's shape that is z-translation-equivariant by construction, run the identical symmetry-decay measurement on it, and determine whether the decay curve is a fact about SHA-3 or a fact about the shape
- **`IDEA-20260816-26ef21`** -> `EXP-SHATHREE-1ec801` (tooling, priority medium, `RQ-SHATHREE-cd2cb2`)  
  Before any frontier claim, calibrate the instrument: build a certificate-first round-reduced Keccak collision harness, then sweep its budget over four orders of magnitude with everything else frozen and report whether the reachable round count moves at all, which discriminates a budget-limited frontier from a structure-limited one
- **`IDEA-20260816-3c5b51`** -> `EXP-SHATHREE-c72fed` (composition, priority high, `RQ-SHATHREE-cd2cb2`)  
  Attack the sponge accounting rather than the permutation: the capacity is initialised to zero and therefore already symmetric, so an internal differential's usable freedom is exactly the symmetric part of the rate minus the padding constraint, giving a forced per-digest-size dimension that orders the four SHA-3 instances before any search runs
- **`IDEA-20260816-6ddf4e`** -> `EXP-SHATHREE-35ea76` (mechanism, priority high, `RQ-SHATHREE-cd2cb2`)  
  Chi is the only nonlinear step and it is row-local, so it cannot destroy translation symmetry at all: exhaust its 5-bit difference distribution table and measure, as an exact codimension per active row, the degrees of freedom an internal differential must spend there rather than assuming a uniform per-row charge
- **`IDEA-20260816-8640ad`** -> `EXP-SHATHREE-0f0eab` (theory, priority high, `RQ-SHATHREE-cd2cb2`)  
  Why translation by thirty-two and not by sixteen, eight or four: treat the whole divisor lattice of Z/64 as the parameter and compute, with zero search, the trade-off between symmetric degrees of freedom 25t and the injected asymmetry weight, then check whether t = 32 is the argmax it is assumed to be
- **`IDEA-20260816-97de1e`** -> `EXP-SHATHREE-e7dce7` (measurement, priority medium, `RQ-SHATHREE-cd2cb2`)  
  A reduced-round result is a property of a WINDOW, not of a count: the asymmetry a round injects is decided by two consecutive outputs of the eight-bit LFSR that generates the constants, so the cheapest four-round window is a forced value and is almost certainly not rounds zero to three
- **`IDEA-20260816-a54b82`** -> `EXP-SHATHREE-a2fec7` (theory, priority high, `RQ-SHATHREE-cd2cb2`)  
  Every step of Keccak-f[1600] except iota commutes with cyclic translation along the lane axis, so the entire symmetry decay of an internal differential is injected by twenty-four known constants: compute that injection and its linear spread as an exact per-round active-chi-row cost curve
- **`IDEA-20260816-b7f4f7`** -> `EXP-SHATHREE-75d3f1` (representation, priority medium, `RQ-SHATHREE-cd2cb2`)  
  Project the deviation onto its 320-bit column-parity vector: theta acts on that projection by an explicit fixed 320-by-320 matrix while rho destroys it, and the round constants inject asymmetry OUTSIDE the column-parity kernel, so theta amplifies it on the very next step -- all four facts computable with no search
- **`IDEA-20260816-edfb2a`** -> `EXP-SHATHREE-65e755` (composition, priority medium, `RQ-SHATHREE-cd2cb2`)  
  Compose theta's single-position z-shift with rho's twenty-five lane offsets and pi's lane routing into one combinatorial diffusion process on the sixty-four z-positions, compute the round at which the deviation's z-support saturates, and ask whether the triangular-number offsets diffuse faster or slower than random ones

### `SHATWO` — Reduced-round SHA-256 frontier

- **`IDEA-20260816-6df779`** -> `EXP-SHATWO-6444d3` (mechanism, priority medium, `RQ-SHATWO-f196c7`)  
  Replace SHA-256's two sigma rotation-and-shift triples by many sampled triples and measure the joint spectrum of the solver-free deficit and the solver-measured reachable step count across that family, because a design constant that moves one and not the other separates cipher from search
- **`IDEA-20260816-714bcb`** -> `EXP-SHATWO-f18b6e` (control, priority high, `RQ-SHATWO-f196c7`)  
  Before any frontier is read, plant characteristics of known satisfiability into the step-reduced search instrument and measure recovery rate against difficulty and false-positive rate against provably unsatisfiable twins, so that a failure here voids every other measurement in this bucket
- **`IDEA-20260816-74e42d`** -> `EXP-SHATWO-28902d` (control, priority high, `RQ-SHATWO-f196c7`)  
  Exhibit an invertible change of basis on the message block that provably leaves every linear invariant of the expanded schedule fixed while changing the primitive, and then measure whether a frozen instrument reaches a different step count on the two, which is an identifiability falsifier against the whole deficit programme
- **`IDEA-20260816-840ba6`** -> `EXP-SHATWO-79107d` (theory, priority medium, `RQ-SHATWO-f196c7`)  
  Treat the linearized SHA-256 message expansion as a code and measure the minimum-weight profile of its kernel per step count, reporting only upper bounds obtained by a declared bounded search, because a weight is a different object from a rank and the two need not move together
- **`IDEA-20260816-8d3980`** -> `EXP-SHATWO-4ce28b` (tooling, priority high, `RQ-SHATWO-f196c7`)  
  Build and self-test the step-reduced certificate machinery before any characteristic is searched for: a declared certificate schema, two independent verifiers, and a synthetic collision found by birthday search on a truncated step-reduced variant so the whole chain is exercised end to end today
- **`IDEA-20260816-8ee479`** -> `EXP-SHATWO-c4c28c` (measurement, priority medium, `RQ-SHATWO-f196c7`)  
  Hold the budget fixed and vary the word width instead: measure the gap between the solver-free predicted crossing and the measured reachable step count across SHA-256/w for w in 8, 12, 16 and 24, because a model that predicts a frontier must track it as the object is scaled
- **`IDEA-20260816-b7c821`** -> `EXP-SHATWO-917635` (representation, priority medium, `RQ-SHATWO-f196c7`)  
  Make the conditions half of the ledger mechanical: a canonical generalized-condition table for a step-reduced characteristic and an extractor that maps it to the integer pair inside and outside the message-modification window, validated by round-trip on synthetic tables whose counts are known by construction
- **`IDEA-20260816-c4e5e3`** -> `EXP-SHATWO-336c20` (theory, priority high, `RQ-SHATWO-f196c7`)  
  The free-message-bit dimension of the SHA-256 expanded message schedule computed exactly as a GF(2) rank over conditioned bit positions per step count s, turning the degrees-of-freedom half of the frontier ledger into a fixed integer sequence obtained before any characteristic search is attempted
- **`IDEA-20260816-d39a31`** -> `EXP-SHATWO-3d575a` (measurement, priority high, `RQ-SHATWO-f196c7`)  
  Vary only the solver budget against a frozen step-reduced SHA-256/16 encoding across eight doublings and read the shape of the reachable-step response curve, because a plateau and a persistent slope are the two different predictions that instrument-limited and deficit-limited frontiers make
- **`IDEA-20260816-f5dc22`** -> `EXP-SHATWO-37186f` (control, priority high, `RQ-SHATWO-f196c7`)  
  Run the identical solver-free rank pipeline on SHA-512 and on a deliberate chimera that wears SHA-512 word widths with SHA-256 rotation amounts, so the free nearby-object control decides whether the deficit integer tracks a design or merely tracks arithmetic shape

### `SIDECH` — Side-channel and fault models as measurable predicates

- **`IDEA-20260816-1b4b7d`** -> `EXP-SIDECH-3f3fde` (measurement, priority medium, `RQ-FNDSA-001`)  
  The nearest-plane recursion emits one comparison bit per level -- whether the drawn integer landed on the floor or the ceiling side of the level's center -- and that per-level rounding-bit vector is a control-flow observable distinct from the signature; enumerate its exact joint distribution with the secret basis at dimensions 2 and 4.
- **`IDEA-20260816-1c2177`** -> `EXP-SIDECH-a7400e` (tooling, priority medium, `RQ-INSTR-f8faa0`)  
  Reduce every leakage-or-fault assumption in this ledger to a five-slot predicate -- observable, granularity, error rate, observations per invocation, obtainability class -- write the machine checker for that normal form, and report the fraction of assumption-invoking records that currently instantiate all five slots, calibrated against records that invoke no such assumption.
- **`IDEA-20260816-2f049b`** -> `EXP-SIDECH-eccb19` (control, priority high, `RQ-INSTR-f8faa0`)  
  Before trusting any leak detector, measure its detection power as a surface: plant leaks of graded magnitude into an otherwise branch-free routine, sweep the plant size and the trace count, and report the minimum detectable leak curve together with the false-positive rate on an unplanted matched null.
- **`IDEA-20260816-49d0e2`** -> `EXP-SIDECH-74fede` (theory, priority high, `RQ-ECDSA-87625f`)  
  Compute exactly, by exhaustive enumeration over every scalar of a given bit-length, the conditional entropy H(scalar | operation string) for binary double-and-add, always-double-and-add, the Montgomery ladder and w-NAF at w=2..5, turning SPA-resistance from a design intent into a number with a forced value on two of the four.
- **`IDEA-20260816-698819`** -> `EXP-SIDECH-8e197f` (mechanism, priority medium, `RQ-SLHDSA-001`)  
  Grade simulated faults on a stateless hash-based signer by (how many bits, which field, transient or persistent) and measure, per grade, two rates that must be reported together: the probability the fault forces a few-time-key index collision, and the probability a cheap sign-then-verify self-check catches it first.
- **`IDEA-20260816-6bce56`** -> `EXP-SIDECH-fb2fa5` (representation, priority medium, `RQ-ECDSA-87625f`)  
  Treat the exceptional-case trigger of an incomplete addition formula as an observable in its own right: enumerate, over every scalar on a toy curve, the exact rate at which a doubling-detection or zero-coordinate special case fires during scalar multiplication, and the exact information that trigger vector carries about the scalar.
- **`IDEA-20260816-7b5bcf`** -> `EXP-SIDECH-8598df` (composition, priority medium, `RQ-ECDSA-87625f`)  
  Scalar blinding is always described as reducing per-trace leakage, never as changing how leakage ACCUMULATES: measure both at once by computing, on the same instrumented routine, the per-trace information and the joint information over m traces as a function of blinding width b, and report the accumulation exponent.
- **`IDEA-20260816-aaa4fa`** -> `EXP-SIDECH-f0e5d2` (representation, priority medium, `RQ-FNDSA-001`)  
  Coarsen the cumulative-distribution-table index of a lattice Gaussian base sampler to a granularity g, treat floor(index/g) as the entire observation, and measure exactly how many bits about the sampler's secret-dependent CENTER leak per sample as a function of g -- with an exact-center null that must leak zero.
- **`IDEA-20260816-acdc1d`** -> `EXP-SIDECH-572048` (measurement, priority high, `RQ-INSTR-f8faa0`)  
  Instrument this repository's own Python routines with a bytecode-level event tracer and report the mutual information, in bits per invocation, between the emitted (branch-outcome, container-index) event string and the secret input, with the estimator's own floor measured in the same run on a secret-independent arm.
- **`IDEA-20260816-e9caa7`** -> `EXP-SIDECH-58efa3` (mechanism, priority medium, `RQ-ECDSA-87625f`)  
  Every nonce-leakage attack takes (l bits, error rate e) as an input nobody in this program produces; build the missing map by running a SIMULATED Hamming-weight-plus-Gaussian-noise channel over an instrumented nonce-consuming routine and reporting, per assumed noise level, the induced posterior entropy of the nonce's top bits.

### `SIMSPK` — SIMON and SPECK rotation-constant space

- **`IDEA-20260816-0d490e`** -> `EXP-SIMSPK-fd009b` (tooling, priority high, `RQ-SIMSPK-f6a6c0`)  
  A solver timeout is a censored observation, not a bound, and the censoring here is informative rather than random: constants whose optimal-trail search times out are systematically the ones with better bounds, so a naive ranking orders constants by what the solver found easy. Measure that bias against known censoring on ground truth and give the ranking an interval-censored estimator.
- **`IDEA-20260816-29e596`** -> `EXP-SIMSPK-ff7ee8` (mechanism, priority high, `RQ-SIMSPK-f6a6c0`)  
  The longest miss-in-the-middle as a function of the rotation triple: propagate difference SUPPORT patterns forward and backward through the AND-RX round with a one-sided-sound union rule, verify that rule against exhaustive reachability at word sizes where reachability is computable, and report the impossible-differential reach of every constant as a distribution rather than a verdict.
- **`IDEA-20260816-29e9bc`** -> `EXP-SIMSPK-1a10f5` (mechanism, priority medium, `RQ-SIMSPK-f6a6c0`)  
  Algebraic-degree reach over the constant space: propagate the bit-based division property of the AND-RX round exhaustively at word sizes where the propagation set fits in memory, cross-check every symbolic result against a directly measured integral distinguisher over full structured plaintext sets, and place the standardized triple in the resulting distribution of balanced-bit round counts.
- **`IDEA-20260816-5552b8`** -> `EXP-SIMSPK-a82a61` (composition, priority high, `RQ-SIMSPK-f6a6c0`)  
  One constant set, five measures, one honest number: build the joint null distribution of the MAXIMUM standardized rank across the whole computable portfolio by scoring random constant sets through the identical pipeline, so that anomalous under some measure is tested as one test rather than five, and report the standardized triple's multiplicity-corrected position.
- **`IDEA-20260816-5c9c46`** -> `EXP-SIMSPK-0857d1` (control, priority high, `RQ-SIMSPK-f6a6c0`)  
  Run the control before the experiment and ask a different question of it: score structurally identical ciphers with uniformly drawn rotation constants through the entire portfolio FIRST, then publish each measure's RESOLUTION, meaning how many distinct values it takes over the whole space and in which round-count window, because a measure returning three integers over 4096 constants cannot rank them.
- **`IDEA-20260816-6125be`** -> `EXP-SIMSPK-2fdceb` (measurement, priority high, `RQ-SIMSPK-f6a6c0`)  
  Are the two published measures actually one measure? Compute the rank correlation between the optimal-differential and optimal-linear orderings of the whole SIMON32 rotation-constant space, track how that correlation moves with round count, and isolate the triples the two measures disagree about most, since only there can jointly optimal be distinguished from optimal on two measures.
- **`IDEA-20260816-74950b`** -> `EXP-SIMSPK-fbbf19` (measurement, priority high, `RQ-SIMSPK-f6a6c0`)  
  The same literal integers recur across every block and key size, so ask whether their RANK recurs too: compute the rank trajectory of each literal rotation triple as word size grows through the family's own sizes, and measure the transfer coefficient every toy-scale conclusion here silently assumes when extrapolating from word size 8 to 16 and beyond.
- **`IDEA-20260816-7e0030`** -> `EXP-SIMSPK-9aa7e3` (representation, priority high, `RQ-SIMSPK-f6a6c0`)  
  The rotation-constant space is not 4096 points but a set of orbits: test whether the unit-multiplier action u.(a,b,c) = (ua,ub,uc) on Z/n together with the AND-argument swap is an exact cipher-level conjugacy for SIMON-like round functions, and whether every portfolio measure is therefore a class function that must be evaluated once per orbit with its multiplicity carried alongside.
- **`IDEA-20260816-a6a224`** -> `EXP-SIMSPK-eca882` (mechanism, priority medium, `RQ-SIMSPK-f6a6c0`)  
  SPECK's rotation pair lives in a space of only n squared points, so exhaust it: score every (alpha, beta) by optimal rotational-XOR trail weight with the round-constant sequence first held as specified and then replaced by zeros and by random sequences, separating what the rotation pair contributes to rotational resistance from what the constant sequence contributes.
- **`IDEA-20260816-a96623`** -> `EXP-SIMSPK-ac655a` (control, priority high, `RQ-SIMSPK-f6a6c0`)  
  Before ranking anything, make the differential weight oracle earn its trust: re-derive the exact differential probability of the SIMON-like AND round as a function of the rotation triple, and verify it against a brute-force difference distribution table at word sizes where the whole table is computable, reporting the exact inputs where closed form and table disagree.

### `SLHDSA` — SLH-DSA and hash-based signatures

- **`IDEA-20260816-466631`** -> `EXP-SLHDSA-ca85bf` (composition, priority medium, `RQ-SLHDSA-001`)  
  Count the distinct tweaks a signer actually materializes over a transcript, separate that reachable count from the nominal address-space size, and measure whether a generic multi-target search against the tweaked family scales with the reachable count or the nominal one, with untweaked and maximally-tweaked signers as the two bracketing arms.
- **`IDEA-20260816-4f67d5`** -> `EXP-SLHDSA-ae5e66` (mechanism, priority medium, `RQ-SLHDSA-001`)  
  Track the set of Merkle nodes a transcript observer can compute under upward closure after q signatures, measure how that set grows against random node revelation of the same cardinality, and report the height at which the authentication-path pattern stops conferring any structural advantage over cardinality alone.
- **`IDEA-20260816-62210e`** -> `EXP-SLHDSA-15534b` (control, priority high, `RQ-SLHDSA-001`)  
  Build the null object this whole lane is missing: a scaled-down signer in which every tweakable-hash call is answered by a lazily sampled independent random oracle keyed by its address, so that any measurement in this bucket runs in a signal and an ideal arm inside one invocation, and validate the null against a second independently seeded copy of itself.
- **`IDEA-20260816-96af8d`** -> `EXP-SLHDSA-c26c49` (tooling, priority high, `RQ-SLHDSA-001`)  
  Before any number in this bucket is believed, establish that the toy signer can see a defect: build two independently written scaled-down signers, differential-test them on their call traces rather than only their outputs, and measure the detection rate over a catalogue of seeded structural mutations as the instrument-validity number every other entry must cite.
- **`IDEA-20260816-9f5bd3`** -> `EXP-SLHDSA-640dd9` (measurement, priority high, `RQ-SLHDSA-001`)  
  Measure the FORS few-time forgery probability as an exhaustive function of the reuse count, at parameters small enough to enumerate the entire revealed-index state space, and compare the measured curve against the occupancy law this program already derived analytically, arm by arm rather than as a headline.
- **`IDEA-20260816-a681fa`** -> `EXP-SLHDSA-942b3d` (theory, priority high, `RQ-SLHDSA-001`)  
  Count exhaustively, over the whole chain-position vector space at small Winternitz parameters, how many messages a single WOTS+ signature could be extended to sign under the componentwise dominance order, and report what the checksum block actually removes as an integer rather than as an assurance.
- **`IDEA-20260816-a7b433`** -> `EXP-SLHDSA-cccbb9` (theory, priority high, `RQ-SLHDSA-001`)  
  Build a finite layer-by-property requirement table for SLH-DSA in which each cell records which security property of the underlying keyed hash a given structural layer actually reads, with UNDETERMINED as a first-class cell value, then validate the table by breaking exactly one property in a toy instantiation and observing which layers fail.
- **`IDEA-20260816-cf82f2`** -> `EXP-SLHDSA-6c39f3` (representation, priority medium, `RQ-SLHDSA-001`)  
  Treat the map from the message randomizer to the selected hypertree leaf index as a distribution-valued object rather than a uniform idealization, measure its pushforward at digest widths where the whole randomizer domain is enumerable, and report its total-variation distance from uniform against a same-sample-size uniform null.
- **`IDEA-20260816-f061f1`** -> `EXP-SLHDSA-bafee8` (measurement, priority medium, `RQ-SLHDSA-001`)  
  When two signatures land on the same hypertree leaf the same one-time key signs two different roots; track the elementwise maximum of the chain-position vectors as a monotone accumulator, count its saturation horizon exhaustively at enumerable hypertree heights, and measure whether leaf collisions occur at the rate an idealized index predicts.
- **`IDEA-20260816-f9bfbd`** -> `EXP-SLHDSA-a06e73` (composition, priority medium, `RQ-SLHDSA-001`)  
  A layered signature's headline figure is a minimum over layers, but the layers share one public seed and one message digest; measure at scaled-down parameters whether per-layer forgery events are independent, using a signer with independently drawn per-layer seeds and digests as the executable control arm.

### `SNFS` — Special number field sieve and trapdoor detection

- **`IDEA-20260816-046ca8`** -> `EXP-SNFS-7f4c98` (measurement, priority high, `RQ-SNFS-005666`)  
  Census the base rate of accidental speciality: enumerate the forward map from bounded polynomials and bases to primes, count how many primes below a bound lie in the class C(d,H) anyway, and report the fibre-size distribution, since this number is the false-positive floor of every detector
- **`IDEA-20260816-4791a4`** -> `EXP-SNFS-ad6ec4` (theory, priority high, `RQ-SNFS-005666`)  
  Replace the inherited phrase detecting the trapdoor seems out of reach with an explicit triple of hypothesis class, adversary budget, and distinguishing advantage, and compute the exhaustive m-sweep detector cost exponent 1/d in log p for the class C(d,H) with a toy-size exact calibration of the sweep interval
- **`IDEA-20260816-76d133`** -> `EXP-SNFS-761081` (control, priority high, `RQ-SNFS-005666`)  
  Measure how much of any candidate distinguishing statistic separation between honest and SNFS-trapdoored primes is attributable to the prime generator rather than the trapdoor, by running the identical battery on two honest generators that differ only in incidental search strategy
- **`IDEA-20260816-7c9222`** -> `EXP-SNFS-802e85` (theory, priority medium, `RQ-SNFS-005666`)  
  Run the observation-collision audit on the whole detectability programme: search at toy sizes for pairs of primes, one inside and one outside the hypothesis class, that agree on every statistic in a frozen battery, since one such pair falsifies identifiability for that battery outright
- **`IDEA-20260816-938a96`** -> `EXP-SNFS-29b663` (tooling, priority medium, `RQ-RSA-afe33c`)  
  Build an exhaustive bounded-box detector for composite moduli of the shape N equal to r to the e plus or minus s with small s, report its coverage as an exact quantifier over the box, and measure its false-positive rate on random semiprimes of the same bit length
- **`IDEA-20260816-9cfbac`** -> `EXP-SNFS-465979` (mechanism, priority high, `RQ-SNFS-005666`)  
  Compute rather than quote the SNFS versus GNFS advantage as a function of special-form degree d and coefficient bound H by measuring the exact norm-bit distribution over a fixed sieve box, with a same-degree large-coefficient polynomial as the null object
- **`IDEA-20260816-a451fe`** -> `EXP-SNFS-30a32b` (composition, priority medium, `RQ-SNFS-005666`)  
  Since a special-form prime satisfies p equal to f of m, the integer p minus one is the value of f minus one at m, so any rational factorization of that polynomial forces algebraic factors into p minus one: measure whether the resulting factor-size profile separates the classes
- **`IDEA-20260816-b7a34b`** -> `EXP-SNFS-f62748` (control, priority high, `RQ-SNFS-005666`)  
  Calibrate the selection inflation of a K-statistic distinguishing battery before any trapdoored prime exists, by running the battery on two identically generated honest classes with fabricated labels and measuring the null distribution of the maximum separation over K, which fixes the threshold a real battery must clear
- **`IDEA-20260816-dd425d`** -> `EXP-SNFS-b5187e` (measurement, priority high, `RQ-SNFS-005666`)  
  Restate SNFS trapdoor detection as a decision problem over the hypothesis class C(d,H) of primes admitting a degree-d integer polynomial with coefficients bounded by H, and measure the power-lattice shortest-vector detector ROC against random primes of identical bit length
- **`IDEA-20260816-ddc377`** -> `EXP-SNFS-ffa309` (representation, priority medium, `RQ-SNFS-005666`)  
  Test a lattice-free detector for special-form primes: the minimum over a base grid of the largest centred digit of p written in base m, whose null distribution over random primes is available in closed form and therefore predicts its own false-positive rate

### `ZKARG` — Argument systems and Fiat-Shamir soundness accounting

- **`IDEA-20260816-130f15`** -> `EXP-ZKARG-1a879b` (measurement, priority high, `RQ-WFS-e776b6`)  
  For a small AIR over a toy prime field, exhaustively evaluate the quotient identity at every out-of-domain point against a constructed family of false traces, and report the measured false-acceptance rate as a function of constraint degree and trace length against the Schwartz-Zippel value the arithmetization budget assumes
- **`IDEA-20260816-30b3fd`** -> `EXP-ZKARG-7af954` (theory, priority high, `RQ-WFS-e776b6`)  
  Compute, with zero compute budget, the exact soundness bits lost when a Fiat-Shamir challenge is derived by reducing a k-bit hash output modulo a prime, tabulated as a signed bit discrepancy over named pairs of output length and field prime and over named repetition counts
- **`IDEA-20260816-49d3ea`** -> `EXP-ZKARG-2eba1e` (control, priority medium, `RQ-WFS-e776b6`)  
  Compute exactly, with no compute budget, how much soundness a query-phase sampler loses by drawing its t verifier queries with replacement rather than without, tabulated over named domain sizes, query counts and corruption rates, and identify the shapes where the difference exceeds a named bit threshold
- **`IDEA-20260816-500948`** -> `EXP-ZKARG-87485f` (mechanism, priority medium, `RQ-WFS-e776b6`)  
  When v claims are batched into one check by powers of a single challenge rather than by v independent challenges, measure the exact soundness gap between the two batching schemes by enumerating every challenge and every adversary error pattern in a toy field, as a function of v and the field size
- **`IDEA-20260816-65979d`** -> `EXP-ZKARG-a186ff` (mechanism, priority high, `RQ-WFS-e776b6`)  
  Fix one three-round public-coin toy argument whose whole transcript space is enumerable, then measure the exponent alpha in the Fiat-Shamir soundness loss eps_FS(Q) modelled as c times Q to the alpha, by running an exhaustively optimal Q-query cheating prover instead of assuming the union-bound value alpha equal to one
- **`IDEA-20260816-6f4272`** -> `EXP-ZKARG-0662d2` (theory, priority high, `RQ-WFS-e776b6`)  
  Take one fixed reference argument at fixed parameters and decompose its quoted bit level into every named term that enters it, compute each term exactly, then report the signed bit residual between the composed total and the headline number and the sensitivity of that total to the order in which the terms are combined
- **`IDEA-20260816-7269da`** -> `EXP-ZKARG-eae9f4` (measurement, priority medium, `RQ-WFS-e776b6`)  
  Measure one folding step of a low-degree test as a counted object: over a toy Reed-Solomon domain small enough to enumerate every function at a fixed distance, count how often a delta-far function folds to something strictly closer, and report the distance-preservation rate against the term the folding accounting charges
- **`IDEA-20260816-8e6e96`** -> `EXP-ZKARG-733374` (representation, priority medium, `RQ-WFS-e776b6`)  
  Treat an algebraic sponge over a tiny prime field as a challenge sampler and measure, round by round, how far the induced challenge distribution stays from uniform over the whole enumerable input domain, reporting the round count at which the deviation drops below the soundness term it is supposed to leave untouched
- **`IDEA-20260816-c50b84`** -> `EXP-ZKARG-41c4fa` (tooling, priority high, `RQ-WFS-e776b6`)  
  Map the frontier of what is exhaustively measurable: for a family of small argument protocols, measure how the cost of computing an attained cheating advantage by complete enumeration grows with challenge-space size, round count and prover branching, and publish the reachable region as a table future contracts must size themselves against
- **`IDEA-20260816-d1e544`** -> `EXP-ZKARG-ec0230` (composition, priority medium, `RQ-WFS-e776b6`)  
  Count the per-layer soundness loss of recursive composition as an integer ledger rather than a proof sketch: build a toy protocol that verifies its own predecessor for L layers, measure the attained cheating advantage exhaustively at each L, and report the measured compounding against the product the layered accounting charges

