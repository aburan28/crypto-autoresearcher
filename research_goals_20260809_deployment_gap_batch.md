# Research Goals 2026-08-09 — Ed25519, pairing curves, NTRU, committing AEAD, ROS, quantum resource estimates, CSIDH, Fiat–Shamir, class groups, threshold ECDSA, Argon2, hybrid KEM combiners

**Date anchor:** 2026-08-09

**Status:** Planning record. Twelve `draft` goals, twelve new research questions,
and 108 proposals. **Nothing here is evidence.** Every per-primitive technical
statement below and in the records is a **research target RECALLED FROM MODEL
MEMORY on 2026-08-09 — not web-searched, not read in primary text by this
program, and not filed as `KN-LIT`.** No source named anywhere in this batch has
been filed, and every goal carries a constraint forbidding experiment design (in
several cases, forbidding any recorded claim) until its primary sources are
filed. Companion precedents:
`research_goals_20260809_hash_symmetric_factoring_batch.md`,
`research_goals_20260804_five_primitive_batch.md`,
`research_goals_20260729_nist_pqc_selected.md`.

## 1. What was asked and what was created

The request was for at least ten cryptographically relevant goals and 100+ ideas
for them. Twelve goals were opened, each with one research question and nine
proposals — 108 proposals in total, one lane each.

| Goal | Question | Object under study | Ideas |
|---|---|---|---|
| `GOAL-EDDSA-001` | `RQ-EDDSA-9b8473` | Ed25519 verification semantics: the finite divergence matrix, with certificates classified by adversary control | 9 |
| `GOAL-PAIR-001` | `RQ-PAIR-f2e31f` | BLS12-381/BN254 target-field cost: exTNFS polynomial selection re-run, memory charged, sensitivity ranked | 9 |
| `GOAL-NTRU-001` | `RQ-NTRU-9015ee` | The NTRU fatigue point measured rather than inherited, and whether it transfers to the deployed ring shape | 9 |
| `GOAL-AEADC-001` | `RQ-AEADC-8db132` | Key-committing AEAD: certificates at full standard parameters, the k-way curve, the repair-by-precondition table | 9 |
| `GOAL-ROS-001` | `RQ-ROS-595c15` | ROS cost curve with literal forgeries, and which instantiation choice in each deployed two-round protocol is load-bearing | 9 |
| `GOAL-QRE-001` | `RQ-QRE-6dba8c` | Quantum resource estimates: reproduce the pipeline, then rank every assumption by how much of the headline it owns | 9 |
| `GOAL-CSIDH-001` | `RQ-CSIDH-64343f` | CSIDH's disputed quantum security: one switchable model, the disagreement kernel, the classical gate count | 9 |
| `GOAL-WFS-001` | `RQ-WFS-e776b6` | Fiat–Shamir transcript completeness as a decidable property, plus the measured grinding curve | 9 |
| `GOAL-CLGRP-001` | `RQ-CLGRP-66ab7f` | Class groups as trustless hidden-order groups: measured cost curve, honest interval, structural sub-case audit | 9 |
| `GOAL-TECDSA-001` | `RQ-TECDSA-8d340d` | Threshold ECDSA: each published extraction class as a certificate, with session-count curves and a verified fix map | 9 |
| `GOAL-ARGON-001` | `RQ-ARGON-141710` | Argon2: the tradeoff attack's real cost at the recommended parameters, and the frontier in the table's own coordinates | 9 |
| `GOAL-HYBRID-001` | `RQ-HYBRID-cdf2b2` | Hybrid KEM combiners: the binding table filled with a derivation or a certificate in every cell | 9 |

Goal identifiers use the legacy three-digit suffix because
`tools/validate_ledger.py` still pins `GOAL-[A-Z0-9]+-\d{3}`; questions and
proposals use random six-hex tokens minted with `tools/allocate_id.py --next`
and each verified free with `--check` before use (AGENTS.md rule 14). No token
was chosen by scanning committed state. `tools/validate_ledger.py` passes with
no new violations (5432 → 5564 records).

## 2. The selection criterion, stated so it can be argued with

Two filters were applied, in order.

**First: is the lane already occupied?** The ledger held 57 goals before this
batch. ECDLP, isogenies (post-SIDH), module lattices, code-based KEMs,
multivariate signatures, hash-based signatures, AES, the SHA family, Ascon,
SIMON/SPECK, GHASH/Poly1305, RSA and SNFS were all covered. Every goal here
takes a lane that was empty, and each carries a `non_duplication` block naming
the nearest occupied lane and the exact reason no result transfers.

**Second, and decisive: is there decisive evidence reachable inside a campaign
budget?** That filter pushed the set away from the obvious target in every case.
The obvious Ed25519 goal is a forgery; the obvious NTRU goal is a key recovery
at deployed parameters; the obvious pairing goal is a discrete logarithm in
GF(p^12). None is reachable and a campaign that opens on one produces nothing.

What survived both filters is a specific and nameable shape: **security
properties that live in a FINITE, ENUMERABLE object — and quantities computed
once and inherited ever since.** Seven goals target the first, five the second.

- **Ed25519** is the batch's sharpest instance of the first shape. The objects
  that separate two admissible verification readings live in an eight-element
  torsion subgroup and a finite set of non-canonical encodings. The enumeration
  is *complete*, it costs seconds, and the evidence is a certificate any reader
  checks in microseconds. Higher-level systems — consensus, transparency logs,
  reproducible builds — assume signature verification is a total function, and
  no official test vector exercises the assumption.
- **Committing AEAD** is the cheapest strong evidence available anywhere in this
  program: one ciphertext, two keys, two valid decryptions, at FULL standard
  parameters rather than reduced ones. The technique is published; the corpus
  contains no such artifact, and the repair-by-precondition table nobody has
  filled is a finite table this harness can fill.
- **Hybrid KEM combiners** went from proposal to browser default in a very short
  time. Their binding properties are decidable, the certificates are a few
  hundred bytes, and the space of key-derivation input choices is a finite
  lattice — so the table can be *completed* rather than sampled.
- **Fiat–Shamir transcript completeness** is a failure mode that is simple, fully
  understood, published repeatedly, and still recurring, because the correctness
  condition lives where no test vector looks. The research question is whether it
  can be made mechanically decidable; the certificate enumeration is the ground
  truth any candidate criterion is scored against, and a negative result there is
  publishable.
- **Threshold ECDSA** reached production ahead of standardization with a history
  of whole-key extraction from small omissions in auxiliary proofs. A reference
  implementation with a switchable proof set makes those preconditions
  enumerable, and the certificate — a recovered key producing a valid signature —
  is decisive.
- **ROS and concurrency** is the clearest recent case of a folklore-secure
  construction failing under concurrency and being replaced in the field within a
  few years. The residual risk has moved from the protocol to the instantiation,
  which is exactly what an ablatable reference implementation measures.
- **Class group structural sub-cases** are finite and constructible from genus
  theory in minutes, which is why `GOAL-CLGRP-001` opens on the assumption audit
  rather than on its cost sweep.

The other five target an inherited quantity:

- **Pairing curves.** BN254 is this program's cleanest historical example: a curve
  deployed at a quoted 128 bits, re-estimated near 100 by a cryptanalytic advance
  that changed no parameter. BLS12-381 was chosen in response, using the same
  class of estimate, and the entire zk and BLS-aggregation stack quotes the
  result. The recomputation is search and arithmetic.
- **NTRU's fatigue point.** sntrup761 executes in an enormous share of the world's
  SSH connections, and the argument for its parameters includes distance from the
  overstretched regime — a distance computed from an asymptotic law whose constant
  was fitted at small dimension *for a different ring shape than the one deployed*.
- **Quantum resource estimates.** Headline totals are single evaluations of a
  pipeline, quoted downstream as constants. The reproduction criterion is fully
  decidable and the sensitivity table nobody publishes is the thing everybody
  needs.
- **CSIDH's quantum security.** Published estimates for one parameter set span
  dozens of bits. A disagreement between careful people with explicit models must
  reduce to identifiable quantities, which makes it unusually tractable.
- **Argon2's recommended parameters.** A table read by non-specialists, justified
  by an asymptotic depth-robustness argument, with the concrete attack cost at
  those exact parameters unpublished in the coordinates the table uses.

## 3. Two spines hold the batch together

**Certificates where certificates exist.** Six goals — EDDSA, AEADC, ROS, WFS,
TECDSA, HYBRID — produce literal objects a reader verifies in milliseconds:
signature triples, colliding ciphertexts, forged proofs, extracted keys,
shared-secret collisions. That is the strongest evidence tier this program can
produce, and it costs nearly nothing. Every such record requires the artifact to
be re-verified by a second implementation, at least one of which did not
construct it.

**Intervals where only extrapolation exists.** Four goals — PAIR, NTRU, CLGRP,
QRE — extrapolate from what this program can run to parameters it cannot. In
each, the deliverable is stated as an interval with its model form and its
extrapolation distance, and in `GOAL-CLGRP-001` the interval's *width* is the
headline result rather than its centre. Cost is always reported as an
(operations, memory) pair, never as a scalar bit level.

## 4. Standing prohibitions written into the records

These are in the goal and question records, not left to judgement.

1. **No third-party system is examined anywhere in this batch.** No wallet,
   custodian, browser, TLS stack, library, service, device, chain, proof system,
   circuit, contract or repository is probed, fetched, tested, or named as having
   any property. Every key, signature, transcript, session and ciphertext is
   self-generated. Where a deployment pattern is described, it is described
   generically.
2. **Certificates against deliberately weakened reference implementations are
   labelled as such in the record's TITLE**, not only in its body. This binds
   ROS, WFS and TECDSA, where every forgery is against an instantiation this
   program chose.
3. **`GOAL-QRE-001` may not contain a date, a timeline, an arrival probability,
   or a migration recommendation** — in any record, from the first one. Its
   admissible output is "under these stated physical assumptions the pipeline
   gives X, and X moves by Y when assumption Z moves."
4. **`GOAL-CSIDH-001` may not record a verdict** on CSIDH's security level, and
   may not characterize any researcher's position beyond filed primary text. Its
   deliverable is the disagreement kernel, not an adjudication.
5. **`GOAL-ARGON-001` may not recommend or deprecate a parameter set**, and no
   real password, credential, leaked corpus or third-party dataset enters it at
   any stage. All inputs are synthetic and generated in-run.
6. **Disclosure precedes publication.** `GOAL-TECDSA-001`, `GOAL-CLGRP-001`,
   `GOAL-HYBRID-001` and `GOAL-EDDSA-001` each carry the rule that a finding
   appearing to affect a current published construction, rather than a
   deliberately weakened instantiation, is disclosed to its authors before any
   publication, and the precedence is recorded in the run package.
7. **Null objects are preconditions, not robustness checks.** Every goal that can
   report a negative carries a paired control: a construction that must yield
   nothing, and a deliberately weakened variant that must yield something — so
   that "we found nothing" is a bounded statement about measured detection power
   rather than an absence (AGENTS.md rule 3). This is `IDEA-20260809-1143bf`
   (Ristretto), `-47a08e` (reduction-based AEAD), `-57d3fb` (nonce commitment),
   `-7e45f5` (canonical transform), `-28289c` (planted lattice), `-a18df4` (fully
   proved threshold instantiation), `-d566b0` (hash-everything combiner) and
   `-bcf891` (depth-robust graph calibration).
8. **Provenance is stated as weak where it is weak.** Every source in this batch
   is RECALLED from model memory. Unlike the 2026-08-09 symmetric batch, which
   used web-search excerpts, **no retrieval of any kind was performed here.**
   Each question record's `provenance` field says so, and each carries a
   constraint blocking the work that depends on the unread text.

## 5. Dependency structure, and what to run first

The proposals are not a flat list. Each goal has a designated cheap first move
that gates the expensive ones, recorded in the goal's `next_action`:

- **EDDSA** — enumerate the torsion and encoding space *before reading anything*.
  It is fixed public mathematics and produces the matrix's row space plus
  candidate certificates with no specification text (`IDEA-20260809-022eb5`).
- **AEADC** — mint the first GCM certificate in batch one, before acquisition
  completes; the construction follows from the authenticator's algebra
  (`IDEA-20260809-313546`).
- **QRE** — count the arithmetic layer first; it needs nothing, and every
  published total is linear in it (`IDEA-20260809-593de3`).
- **CLGRP** — run the finite structural sub-case enumeration before the cost
  sweep; a surviving sub-case under a deployed countermeasure would be the goal's
  most valuable result and is reachable in batch one (`IDEA-20260809-83cbc7`).
- **NTRU** — run the smallest full sweep and record the *reduction profile*, not
  just recovery; if the event's signature is invisible at reachable dimensions,
  every later cell is uninterpretable (`IDEA-20260809-24eec3`).
- **TECDSA** — build the switchable reference implementation and prove its honest
  path correct before attacking it; the dominant failure mode is manufacturing
  attacks from one's own bugs (`IDEA-20260809-986269`).
- **ARGON** — build and measure the memory-access DAG before implementing any
  attack (`IDEA-20260809-a915ea`).
- **HYBRID** — establish the ML-KEM component binding baseline before
  implementing a single combiner; every row is a function of it
  (`IDEA-20260809-c13e6a`).
- **PAIR** — run the certified small-field calibration DL before the literature;
  without an owned anchor every extrapolation is a restatement of someone else's
  constants (`IDEA-20260809-15e1cd`).
- **ROS** — implement the solver at small group order and reproduce the cost
  curve's shape before building any protocol reference; an instantiation map from
  an uncalibrated solver is unfalsifiable (`IDEA-20260809-47bb6d`).
- **WFS** — build the smallest complete protocol and forge against it in batch
  one; the enumeration is the ground truth the decidability work is scored
  against (`IDEA-20260809-792aca`).
- **CSIDH** — build the reversible group-action circuit first, and specifically do
  *not* begin by tabulating who claims what, which is the failure mode this goal
  is most exposed to (`IDEA-20260809-666d3d`).

## 6. Honest accounting of novelty

Nine proposals are marked `novelty_status: known` and say so in their
`sota_delta`: `-313546` (GCM key collision), `-47bb6d` (ROS solver), `-593de3`
(reversible arithmetic counts), `-666d3d` (CSIDH reversible circuit), `-792aca`
(weak-FS forgeries), `-986816` and `-98c5ac` (threshold ECDSA extraction),
`-ac5947` (Argon2 tradeoff attack), `-c13e6a` (ML-KEM binding). In each the
contribution claimed is the *artifact inside this program plus a measured curve
or table*, not the technique — because these are the instruments the rest of
each goal is scored against, and a goal whose instrument is uncalibrated
produces nothing citable.

The remaining 99 are `novelty_status: unverified`, screened against the corpus
by grep and explicitly **not** screened against the literature. Every one says
`WEB NOT CHECKED`.

## 7. What was considered and not opened

Recorded so the omissions are arguable rather than invisible.

- **ECVRF and randomness beacons.** Output-uniqueness questions overlap
  `GOAL-EDDSA-001`'s cofactor and encoding objects closely enough that opening
  both would have blurred the boundary. The stronger candidate for a later batch.
- **Finite-field DH / FFDHE descent amortization.** Genuinely distinct from
  `GOAL-RSA-001` (factoring) and `GOAL-SNFS-001` (trapdoored primes), but the
  descent question is folded into `GOAL-PAIR-001` as `IDEA-20260809-217be0`,
  where it has a calibration to attach to.
- **FHE parameter selection and noise-growth accounting.** A large lane with real
  inherited quantities; deferred because it needs its own instrument calibration
  rather than sharing one.
- **Password-hashing alternatives (scrypt, bcrypt, balloon).** Used as nearby
  objects inside `GOAL-ARGON-001` rather than as separate goals.
- **Side-channel and fault attacks generally.** Excluded by the
  no-third-party-hardware constraint that binds this whole batch.
- **ChaCha20 as a standalone stream-cipher goal.** Still open to be filed; noted
  as deferred in the previous batch and not displaced here.

## 8. State

All twelve goals are `status: draft` with `dispatch_queue_path: null` — created,
not dispatched, and **not activated**. Activation is a Coordinator action taken
on explicit direction and recorded as such. No hypothesis, experiment, run,
evidence or decision record is created by this batch, and no proposal here
authorizes execution.
