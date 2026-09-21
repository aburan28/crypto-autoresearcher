# Ideation report — TASK-20260731-014 (GOAL-FAEST-001, BATCH-001)

Task: produce exactly three schema-complete IDEA-20260731-019, IDEA-20260731-002..003 proposals for
RQ-FAEST-001 under object-first discipline, each naming an exact soundness or
reduction object and writing down the matched AES baseline. Executed 2026-07-31.
Proposals only: no hypothesis, experiment, evidence, or decision record was
created, and no official research state was changed.

## The three ideas

| ID | Title | Exact attack object | Class | novelty_status |
|----|-------|--------------------|-------|----------------|
| IDEA-20260731-019 | VOLEitH consistency-check soundness: deployed-field Schwartz–Zippel bound vs the AES degree-3 constraint structure | The **consistency-check error term eps_cc** = max over nonzero witness-error vectors of Pr[random linear check passes], vs the claimed Schwartz–Zippel bound deg(p)/|F| at the deployed field | measurement | adaptation |
| IDEA-20260731-002 | Multi-round forgery cost model: the grinding/repetition (kappa, tau) tradeoff, fully charged | The **grinding exponent kappa and repetition count tau** and the expected forgery cost 2^kappa · eps_cc^{-tau} · C_transcript, minimized over (kappa, tau) against the matched AES baseline | measurement | adaptation |
| IDEA-20260731-003 | The LeafCommit/bAVC collision term: is the AES-based commitment layer binding at 2^lambda, and does the soundness reduction actually need it? | The **LeafCommit collision term and the bAVC hash-collision term** — the named reduction links from commitment binding to VOLEitH soundness, plus the binding-property profile the extraction argument requires | measurement | speculative |

All three are verification/barrier lanes, not attacks: per GOAL-FAEST-001's
completion criteria they are aimed at either exhibiting a charged forgery below
the claimed category (the falsification direction, which each record states
explicitly) or producing the scoped barrier statement for exactly one named
link of the chain. None claims an exponent move (target-result-profile C1 =
"no"); they are the honest groundwork the goal's own completion criteria
require, and each record says so in `interpretation_limits`.

## Matched baselines written down (identical parameter set and cost convention)

Convention fixed in all three records (KN-TECH-040: the convention is part of
the claim): serial classical cost in **AES-128-equivalent evaluations**, hash
calls converted at the deployed hash's per-call AES count, **memory in bits
charged separately**, data charged, quantum baselines stated separately under a
depth-limited (MAXDEPTH) convention. Parameter set: **faest_128f / faest_128s
(spec v2.0, category-1, AES-128)**.

1. **Best known AES key recovery (the matched baseline every idea challenges):**
   full 10-round AES-128, single-key, known plaintext-ciphertext pair —
   **2^126.1** (biclique, Bogdanov–Khovratovich–Rechberger; archived
   KN-LIT-2701, confidence reported). Data ~2^88 chosen plaintexts, ~2^8
   memory: labeled **UNVERIFIED in-repo** (detail from memory of the paper,
   not stated in the archived entry). Quantum: Grover ~2^64 sequential AES
   evaluations (KN-LIT-679), depth-limited charged ~2^85.8 and NIST gate-count
   ~2^143: both labeled **UNVERIFIED in-repo** (not archived). FAEST's
   one-wayness assumption applies to the AES-based one-way function
   f(k) = AES_k(x) for fixed public x (KN-LIT-7637), i.e. inverting it is
   exactly the key-recovery problem the biclique attack addresses. The
   Even-Mansour variants (faest_em_*) use a different 2n-bit-key OWF; their
   baseline is not established in-repo and is declared out of primary scope in
   every record.
2. **Best known VOLEitH/Fiat-Shamir soundness-layer attack:** the generic
   multi-round transcript forgery, expected cost 2^kappa · eps_cc^{-tau} ·
   C_transcript — which is precisely the object IDEA-20260731-002 models. No
   structural attack on the consistency-check term, the grinding layer, or the
   LeafCommit/bAVC mode is published to this program's knowledge (prior-art
   grep below); the deployed (kappa, tau, eps_cc, field, digest) values are
   **UNVERIFIED placeholders** because the spec v2.0 PDF body text was not
   extractable by the sources task (KN-LIT-7637 limit) — every record flags
   that pinning them from spec v2.0 + eprint 2023/996 full text is a hard
   dependency before any experiment (RQ-FAEST-001 constraint).

No number was fabricated: every figure is either archived here (2^126.1,
KN-LIT-2701; 7-round 2^89.3–2^91.4, KN-LIT-7593; Grover query count,
KN-LIT-679) or explicitly labeled unverified in place.

## Prior-art search performed (novelty discipline)

Grepped `knowledge/` and `ledger/` for: faest/FAEST, VOLEitH,
VOLE-in-the-Head, AES one-wayness/key-recovery, Fiat-Shamir soundness,
grinding, MPCitH, bAVC, LeafCommit/leaf commitment, batch/vector commitment,
consistency check, biclique, Grover.

Findings relevant to novelty verdicts:

- **FAEST/VOLEitH primary sources** (KN-LIT-7637 spec v2.0, KN-LIT-7638
  eprint 2023/996, KN-LIT-7619 faest-ref, KN-LIT-7620 IR 8610) are filed but
  all are citation-level: the spec PDF text and the paper's full text have
  NOT been read by this program. The VOLEitH soundness mechanism itself is
  therefore *known* (published, CRYPTO 2023) but its exact deployed
  instantiation is unread — this is why all three novelty verdicts are
  adaptation/speculative rather than "known result": the records verify the
  exact deployed instance, not the mechanism's existence.
- **AES key recovery**: KN-LIT-2701 (biclique, 2^126.1) and KN-LIT-7593
  (7-round Möbius-bridge, 2^89.3–2^91.4, reduced rounds only) are archived.
  No repo record claims a full-AES-128 attack below 2^126.1. The matched
  baseline is solid.
- **Fiat-Shamir QROM/ROM soundness**: KN-LIT-6524 (Don–Fehr–Majenz–Schaffner),
  KN-LIT-7137, KN-LIT-6386, KN-LIT-7159, KN-LIT-4046 and the KN-LIT-387x
  series cover FS transform security; none is FAEST-specific.
- **VOLEitH-adjacent schemes**: KN-LIT-1726 (Lynx, VOLEitH-friendly
  primitive) and KN-LIT-6232 (ReSolveD, VOLEitH signature) exist; neither
  analyses FAEST's exact soundness terms.
- **Sibling goals in this program**: GOAL-SDITH-001/RQ-SDITH-001 and
  GOAL-MQOM-001/RQ-MQOM-001 target the same family-level objects (MPCitH
  grinding slack, ROM/QROM forgery bounds) for other Round-3 schemes; no
  IDEA records exist for them yet, and none exists for FAEST.
- **No prior IDEA record in `ledger/proposals/` targets FAEST, VOLEitH, or
  any MPCitH scheme** — the existing 48 proposals are ECDLP/isogeny/AES-
  cryptanalysis lanes. The three FAEST records are the program's first for
  this scheme.

On "the space is mined": FAEST/VOLEitH soundness is an active, well-studied
area (the 2026 QROM retightening work named in RQ-FAEST-001's motivation is
direct evidence the bound "moved once and can move again"). Per
inventor-protocol §1/§4, saturation is a hypothesis about the search, not a
reason to decline to generate; each record therefore names a *specific* link
and a *specific* falsifiable quantity, and the closure-standard discipline is
followed in the open-directions section below (a named obstruction, an
argument, forward guidance).

## Enumerated closures and open directions (inventor-protocol §4)

Two of RQ-FAEST-001's four targets are NOT covered by the three idea records,
deliberately; their named obstructions and forward guidance:

1. **QROM Fiat-Shamir extractor loss** (RQ target 3). Obstruction: the
   extractor-loss lane is a proof-theoretic question (Rényi-divergence /
   measure-and-reprogram bounds for multi-round FS with commitment-tree
   rewinding), and the 2026 retightening work cited in RQ-FAEST-001's
   motivation is not yet filed as a KN-LIT entry; the program cannot
   re-derive a bound it has not archived. Forward guidance: file the 2026
   retightening work (Rényi-divergence argument) as a KN-LIT entry, then
   reconstruct FAEST's QROM bound end to end; a concrete QROM-vs-ROM gap in
   the claimed category would feed IDEA-20260731-002's model as a quantum
   side. Not an idea record because its minimal discriminating test is a
   derivation with no toy-scale empirical component — the wrong shape for
   this batch's three slots.
2. **Algebraic attacks on the AES constraint system given partial VOLE
   openings** (RQ target 4). Obstruction: this lane depends on the exact
   degree-3 constraint system and the opening pattern, both unread (spec
   PDF). Forward guidance: once the constraint system is pinned, reuse this
   program's solving-degree instrumentation (RQ-DREG-001 / EV-DREG-001..004,
   as GOAL-MQOM-001 already plans for its own systems) to ask whether a
   partial assignment from opened positions allows an algebraic solve of the
   key faster than key recovery. It is a real lane, deferred on the
   unread-spec dependency.

Also enumerated: the Even-Mansour variants' matched baseline (different OWF,
baseline not established in-repo) is declared out of primary scope in all
three records; establishing it is a separate prerequisite if the EM variants
are ever targeted.

## Pareto honesty (inventor-protocol §5)

- `dominated_by`: "n/a (no attack claimed)". All three records are
  verification/barrier lanes; none claims a complexity result, so no
  best-known result dominates them on any cost axis. Checked against the
  rows on the frontier: the only "attacks" referenced are the baselines
  themselves (2^126.1 biclique; generic transcript forgery), which the
  records compare against rather than claim to beat.
- `sota_delta`: "no attack; conceptual/measurement contribution only". The
  quantitative comparison each record commits to is the matched-baseline
  inequality (charged forgery cost vs 2^126.1 and vs the scheme's claimed
  2^128), with the falsification direction stated per record.

## Inference metadata

- requested_policy: `research-deep`
- resolved model identifier (per runtime): `opencode/deepseek-v4-flash-free`
- reasoning_effort: null (policy default)
- fallback_allowed: false; fallback_used: none
- degraded_allowed: false; no inference amendment requested
- independent_session_required: false (per handoff); session independence:
  this session executed only TASK-20260731-014; no lineage shared with any
  other task's session.

## Hard-rule confirmation

Exactly three IDEA records were created (IDEA-20260731-019, IDEA-20260731-002..003), each
schema-complete, each naming an exact attack object and writing down the
matched baseline (AES-128 key recovery 2^126.1 per KN-LIT-2701 and the generic
VOLEitH/Fiat-Shamir transcript-forgery cost, same parameter set, same
convention). No hypothesis, experiment, evidence, or decision record was
created; no official research state was changed; nothing outside the two
declared write scopes (`ledger/proposals/` and
`coordination/goals/GOAL-FAEST-001/batches/BATCH-001/tasks/TASK-20260731-014/`)
was edited. Knowledge/INDEX.md was not touched.
