# Ideation expansion report — TASK-20260731-007 (GOAL-FAEST-001, BATCH-001)

Task: produce exactly three schema-complete IDEA-20260731-004..006 proposals
for RQ-FAEST-001, one per lane that BATCH-001's first ideation pass
(TASK-20260731-014) left undeveloped: (4) the QROM Fiat-Shamir extractor
loss, (5) algebraic attacks on the deployed AES constraint system given
partial VOLE openings, (6) the Even-Mansour OWF matched baseline. Executed
2026-07-31 under object-first discipline with the matched baseline written
down per idea. Proposals only: no hypothesis, experiment, evidence, or
decision record was created, and no official research state was changed.

## The three ideas

| ID | Title | Exact attack object | Class | novelty_status |
|----|-------|--------------------|-------|----------------|
| IDEA-20260731-004 | QROM Fiat-Shamir extractor loss: is FAEST's claimed category backed by the charged QROM bound at the deployed parameter sets? | The **QROM Fiat-Shamir extractor loss term L_QROM(tau, kappa, q, digest, |C|, eps_cc)** — the concrete reduction loss between a quantum forger's success with q hash queries and the extractor's witness recovery, compounded over the tau rounds and the grinding, and the charged QROM forgery bound it yields at the deployed set vs the claimed category | measurement | unverified |
| IDEA-20260731-005 | Algebraic attacks on the FAEST degree-3 AES constraint system under partial VOLE openings: a solving-degree census against the matched AES baseline | The **polynomial system S = (constraint family C, deployed field F, witness variables V incl. key/state/S-box auxiliaries) augmented with the partial-assignment set I_open** (positions a transcript's VOLE openings reveal), and the concrete cost of the best algebraic solve (Groebner F4/F5, XL, hybrid BooleanSolve/crossbred) of S union I_open | measurement | speculative |
| IDEA-20260731-006 | The faest_em_* Even-Mansour OWF matched baseline: is the best EM attack matched at the claimed category, and does the AES-based permutation add a structural shortcut? | (1) The **faest_em_* Even-Mansour one-way function f(k1,k2) = EM_{k1,k2}(x)** at its deployed definition (widths, key split, P, fixed inputs), and (2) the **AES-based public permutation P** — whether the best EM attack (slidex T*D = 2^n, MITM 2^n, Grover 2^n, ABK q_E*q_P^2 ~ 2^n) is matched at the claimed category and whether P admits a structural shortcut | measurement | adaptation |

All three are verification/barrier lanes, not attacks (matching
IDEA-20260731-019, IDEA-20260731-002..003): each names the exact soundness or reduction object,
states the falsification direction explicitly (a charged forgery/bound below
the claimed category or matched baseline), and is aimed at either exhibiting
that falsification or producing the scoped barrier statement for exactly one
named link of the chain. None claims an exponent move
(target-result-profile C1 = "no"), and each record says so in
`interpretation_limits`.

## Matched baselines written down (identical parameter set and cost convention)

Convention fixed in all three records (KN-TECH-040: the convention is part of
the claim): serial classical cost in **AES-128-equivalent evaluations**, hash
calls converted at the deployed hash's per-call AES count, **memory in bits
charged separately**, data charged, quantum baselines stated separately under
a depth-limited (MAXDEPTH) convention.

1. **IDEA-20260731-004 (quantum/QROM lane).** Parameter set faest_128f /
   faest_128s (spec v2.0, category-1, AES-128; deployed tau, kappa, field,
   digest, challenge space are UNVERIFIED placeholders — spec PDF text
   unread, KN-LIT-7637 limit). Because the adversary is a quantum (QROM)
   adversary, the matched comparison is the **quantum** AES baseline: Grover
   key search ~2^64 sequential AES evaluations (KN-LIT-679, archived query
   count), depth-limited charged ~2^85.8 and NIST gate-count ~2^143 (both
   UNVERIFIED in-repo); the classical 2^126.1 biclique (KN-LIT-2701) is
   recorded for completeness, with the RSF-1 caveat (one-pair OWF game;
   biclique published at ~2^88 chosen plaintexts = comparative lower bound on
   the one-pair cost). VOLEitH/FS-layer baseline: the generic QROM FS forgery
   bound with the extractor loss — exactly the object the idea reconstructs —
   with the loss shape from the corpus's QROM FS records (KN-LIT-6524,
   KN-LIT-969, KN-LIT-7137; KN-LIT-969 gives tight online extractability only
   for specific commit-and-open templates; KN-LIT-7137 documents generic FS
   bounds as often too weak for concrete instances) and the 2026
   Renyi-divergence retightening (unfiled, hard dependency). Exact deployed
   loss values UNVERIFIED until the sources are read.
2. **IDEA-20260731-005 (algebraic lane).** Parameter set faest_128f /
   faest_128s; convention identical. Matched baseline: 2^126.1 biclique
   (KN-LIT-2701) with the RSF-1 caveat, plus the algebraic-attack baseline
   itself: the full-AES-128 key-recovery ideal is zero-dimensional with a
   computable Groebner basis (Buchmann-Pyshkin-Weinmann, KN-LIT-2288), whose
   security implications were left open; no published full-AES-128 algebraic
   attack below 2^126.1 is known to this program (in-repo grep; UNVERIFIED
   beyond that scope). VOLEitH/FS-layer baseline: generic transcript forgery
   2^kappa * eps_cc^{-tau} * C_transcript (the object of
   IDEA-20260731-002); this idea attacks the witness-knowledge side — the
   concrete algebraic content of the claim that witness extraction is as hard
   as OWF inversion.
3. **IDEA-20260731-006 (EM lane).** Parameter set faest_em_128f /
   faest_em_128s (spec v2.0, category-1; the OWF definition, the 2n-bit key
   split, P, and the fixed inputs are UNVERIFIED placeholders — pinned from
   spec v2.0 + a pinned faest-ref commit, owf.c/h and aes.c/h per the
   KN-LIT-7619 layout). The matched baseline is derived from the construction,
   per the brief: for a two-block 2n-bit-output definition, MITM/slidex key
   recovery T*D = 2^n at D effectively 1 gives ~2^n P-evaluations (2^128 for
   n = 128) with negligible memory, or the DKS memoryless variant at
   D = 2^{n/2} (KN-LIT-4930); a single-block n-bit-output definition would
   make any-preimage inversion cost ~1 P-evaluation (a structural finding,
   not a baseline). Quantum: Grover ~2^n over the 2^{2n}-bit key space
   (charged form UNVERIFIED); ABK q_E * q_P^2 ~ 2^n (KN-LIT-5810);
   Simon/period attacks (KN-LIT-7574/6096) mapped out of the fixed-x OWF
   game by derivation (assumption H3 in the record). The headline structural
   observation: the EM baseline sits at 2^n = 2^128 for faest_em_128* —
   matched at the boundary with zero slack — so the EM variants' claimed
   category is backed only if the VOLEitH/FS layer is tight AND P has no
   shortcut; both are exactly what the record tests.

No number was fabricated: every figure is either archived (2^126.1
KN-LIT-2701; Grover 2^64 KN-LIT-679; T*D = 2^n and memoryless-variant
KN-LIT-4930; q_E*q_P^2 ~ 2^n KN-LIT-5810) or explicitly labeled UNVERIFIED
in place.

## Distinctness from IDEA-20260731-019, IDEA-20260731-002..003

- **IDEA-004 vs IDEA-001**: 001 measures the per-round consistency-check
  soundness error eps_cc (a classical per-round term at the deployed field).
  004 measures the QROM **transform** loss — the extractor/reduction loss of
  the Fiat-Shamir transform itself for a quantum adversary, which is a
  different link: eps_cc can be tight and the transform still lossy
  (no-cloning, measure-and-reprogram, Renyi divergence). 004's matched
  comparison is the quantum AES baseline; 001's is classical.
- **IDEA-004 vs IDEA-002**: 002 is the classical-ROM multi-round forgery
  cost model (2^kappa * eps_cc^{-tau} * C_transcript). 004 is the
  quantum/QROM side, which 002's own interpretation_limits explicitly
  declare out of scope ("The model does not address the QROM extractor
  question" — IDEA-20260731-002). 004 feeds 002 as its quantum side.
- **IDEA-004 vs IDEA-003**: 003 measures collision resistance of the
  LeafCommit/bAVC hash modes (a property of the commitment instantiation).
  004 asks whether the tight QROM **reduction template** (online
  extractability per KN-LIT-969) actually applies to that instantiation — a
  property of the proof structure, not of the hash mode's collision
  resistance.
- **IDEA-005 vs IDEA-001**: 001 measures the max per-round pass probability
  of error vectors against the Schwartz-Zippel bound (a soundness-error
  quantity). 005 measures the solving-degree indicators (d_reg / d_ff,
  Macaulay size) of the whole constraint system as a witness-recovery
  problem with partial openings — a different quantity (cost of extracting
  the key), different toolchain (the program's DREG solving-degree
  instrumentation), and a different dependency profile (openings as fixed
  variables). 001 was about the probability a bad witness passes a check;
  005 is about the cost of finding any witness from the system plus leaked
  positions.
- **IDEA-006 vs IDEA-001..003**: 001-003 all declare the EM variants "out of
  primary scope; baseline not established in-repo" — 006 is exactly the
  establishment of that baseline plus the AES-instantiation structural check.
  It is the only record of the six whose object is the OWF itself rather
  than the VOLEitH/FS/commitment layer.

## Prior-art search performed (novelty discipline)

Grepped `knowledge/` and `ledger/` for: qrom, fiat-shamir, QROM, Renyi,
extractor, groebner, Groebner, algebraic attack, linearization, XL,
even-mansour, Even-Mansour, EM variant, faest/FAEST, VOLEitH, first-fall
degree, solving degree, DREG.

Findings relevant to novelty verdicts:

- **QROM Fiat-Shamir corpus (for IDEA-004)**: KN-LIT-6524 (Don-Fehr-Majenz-
  Schaffner, generic QROM FS reduction), KN-LIT-969 (tight online
  extractability in QROM for commit-and-open, element-wise and Merkle
  templates), KN-LIT-7137 (concrete FS security, round-by-round soundness,
  generic bounds too weak), KN-LIT-6386 (SDitH QROM tight proof avoiding
  generic FS losses — the MPCitH sibling that shows the technique), plus the
  KN-LIT-387x/4046/7159/5807/6262/7517 lines. **None is FAEST-specific.** The
  FAEST sources (KN-LIT-7637, KN-LIT-7638, KN-LIT-7619..7620) are citation-level only; the 2026
  Renyi-divergence retightening named in RQ-FAEST-001 is NOT filed in
  knowledge/ — this is why IDEA-004's novelty_status is `unverified`: the
  tightest-known bound (the external ingredient the reconstruction depends
  on) cannot be checked until it is archived, so the record declines to
  claim adaptation of a bound it has not read.
- **Algebraic-attack corpus (for IDEA-005)**: KN-LIT-2288 (zero-dimensional
  Groebner basis for full AES-128 key recovery; security implications left
  open), KN-LIT-2396 (algebraic cryptanalysis of STARK-friendly designs —
  the ZK-constraint-representation attack line), KN-TECH-004/011 (d_reg /
  d_ff instrumentation), KN-TECH-053 (XL/BooleanSolve/crossbred bounds),
  KN-LIT-2645/3009/3344/4597/6741/6745 (AES/algebraic solving), KN-OPEN-002
  (d_ff vs d_reg question). The program's own solving-degree machinery
  (RQ-DREG-001, EXP-DREG-001..004, EV-DREG-001..004) is live and
  RQ-MQOM-001 plans its reuse for a sibling MPCitH scheme. **No record
  targets FAEST's deployed constraint family**; the previous ideation
  report's open-direction #2 (algebraic attacks given partial openings)
  explicitly deferred this lane on the unread-spec dependency. Novelty
  verdict `speculative`: the technique is established in-repo, the deployed
  family is unread, and whether the degree-3-with-auxiliaries representation
  under partial openings is algebraically weaker than the ANF system is
  genuinely open to this program.
- **Even-Mansour corpus (for IDEA-006)**: KN-LIT-4930 (DKS: Slidex matches
  T = Omega(2^n/D); single-key simplification; memoryless at D = 2^{n/2}),
  KN-LIT-5810 (Alagic-Bai-Katz: q_E * q_P^2 ~ 2^n in the classical-E /
  quantum-P setting), KN-LIT-4790 (low-memory 2-round EM via 3-XOR),
  KN-LIT-5121 (MITM key recovery on minimal 2-round EM below the birthday
  data bound), KN-LIT-7574/6096 (quantum period/Simon attacks on EM),
  KN-LIT-7134 (key-alternating/iterated-EM abstraction of AES), KN-LIT-2249/
  2699/3662/4478/4933/5003/5022/5550 (EM security lines). **No record
  analyzes FAEST's EM OWF instance**; the 001..003 records explicitly
  declared the EM baseline unestablished in-repo and out of their scope.
  Novelty verdict `adaptation`: the EM attack toolkit is classic and
  archived; applying it to the pinned faest_em_* definition and checking the
  AES-based P for a structural shortcut is a known-technique-on-a-new-
  instance lane, with the pinned definition's details honestly UNVERIFIED.
- **No prior IDEA record in `ledger/proposals/`** (beyond IDEA-20260731-019..
  003, read in full for distinctness) targets the QROM loss, the FAEST
  constraint system, or the EM OWF; the existing proposal corpus is
  ECDLP/isogeny/AES-cryptanalysis lanes.

On "the space is mined": FAEST security is an active, well-studied area (the
2026 QROM retightening is direct evidence the bound "moved once and can move
again"), and the EM baseline gap is a documented in-repo gap. Per
inventor-protocol §1/§4, saturation is a hypothesis about the search, not a
reason to decline to generate; each record names a specific link, a specific
falsifiable quantity, and its named obstruction (below).

## Enumerated closures and open directions (inventor-protocol §4)

The three lanes from BATCH-001's open-directions list are now covered; what
remains open, with named obstructions and forward guidance:

1. **RSF-5 — spec v2.0 PDF-text blocker (gating all six idea records).**
   Obstruction: the spec PDF body text was unextractable in the sources
   task (KN-LIT-7637 limit), so every deployed-parameter statement in every
   record is an UNVERIFIED placeholder. Forward guidance (unchanged from
   DEC-20260731-020): resolve via an alternate extraction path or adopt a
   pinned faest-ref commit as ground truth; no experiment design for any of
   the six ideas before that gate. IDEA-006's pinning surface is the
   smallest (faest-ref owf.c/h + aes.c/h), so it is the cheapest lane to
   unblock.
2. **2026 Renyi-divergence retightening work — unfiled (gates IDEA-004).**
   Obstruction: the tightest-known QROM bound for FAEST's FS instance is an
   external ingredient this program has not archived; without it the
   reconstruction cannot claim to use the current bound, which is why 004's
   novelty_status is `unverified`. Forward guidance: file it as a KN-LIT
   entry and read it before any 004 experiment; the SDitH-in-QROM line
   (KN-LIT-6386) is the in-corpus sibling technique for tight MPCitH QROM
   proofs.
3. **Round-3 tweak pending (2026-08-14).** The Round-3 FAEST spec does not
   exist as of 2026-07-31 (KN-LIT-7637 headline finding); all records are
   specified against v2.0 with the tweak tracked as a caveat. Re-verify the
   "no Round-3 spec" negative after 2026-08-14 if relied on (red-team
   C2-F5).
4. **Quantum side of IDEA-002's forgery model.** IDEA-004 produces the
   quantum-side bound; the assembly of the classical (002) and quantum (004)
   forgery costs into one charged picture is a natural BATCH-002+ synthesis
   task, dependent on both records' re-derivations.

## Pareto honesty (inventor-protocol §5)

- `dominated_by`: "n/a (no attack claimed)" for all three records. Checked
  against the rows on the frontier: the only "attacks" referenced are the
  baselines themselves (2^126.1 biclique; the generic transcript forgery;
  the EM T*D = 2^n class; Grover 2^64/2^n), which the records compare
  against rather than claim to beat. IDEA-006's baseline derivation
  re-derives known EM bounds (KN-LIT-4930/5810) on a new instance; the
  known results dominate the *derivation* but are the baseline being
  established, not a competing claim.
- `sota_delta`: "no attack; conceptual/measurement contribution only". The
  quantitative comparison each record commits to is the matched-baseline
  inequality (charged QROM bound vs the claimed category and the quantum AES
  baseline; extrapolated algebraic solve cost vs 2^126.1; derived EM
  inversion cost vs 2^n and the claimed category), with the falsification
  direction stated per record.

## Inference metadata

- requested_policy: `research-deep`
- resolved model identifier (per runtime): `opencode/deepseek-v4-flash-free`
- reasoning_effort: null (policy default)
- fallback_allowed: false; fallback_used: none
- degraded_allowed: false; no inference amendment requested
- independent_session_required: false (per handoff); session independence:
  this session executed only TASK-20260731-007; no lineage shared with any
  other task's session.

## Hard-rule confirmation

Exactly three IDEA records were created (IDEA-20260731-004..006), each
schema-complete (id, title, class, claim, mechanism, novelty_status,
assumptions, predictions with metric + direction + minimum_effect,
minimal_test with design + controls + required_metrics, falsification_conditions,
confounders, interpretation_limits, heuristic_assumptions with statement +
rigorous_support + validation_plan, matched_baseline with parameter_set +
convention + both baseline sides, target_complexity, estimated_cost,
recommended_priority), each naming an exact attack object (never "attack
FAEST"), each carrying the matched baseline under one cost convention with
the RSF-1 one-pair caveat, and each distinct from IDEA-20260731-019, IDEA-20260731-002..003 as
mapped above. The inventor-protocol §3 controls (unstructured control,
null-object control, scale/decay control) are present in every minimal test;
toy-tier labeling (AGENTS.md rule 7) and re-derivation-at-deployed-parameters
gates are present in every falsification condition; RSF-5 is carried as a
named assumption in every record. No hypothesis, experiment, evidence, or
decision record was created; no official research state was changed; nothing
outside the four declared write paths (the three IDEA files and this report)
was edited.
