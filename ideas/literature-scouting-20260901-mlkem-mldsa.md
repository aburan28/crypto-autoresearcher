# Literature scouting note — ML-KEM / ML-DSA ideation round, 2026-09-01

Scratch note, NOT a knowledge entry. Written by the orchestrating session from
the two idea-generator subagents' reports (ML-KEM lane, ML-DSA lane) that
produced IDEA-20260901-7eb9e1 / -67f498 / -2f778b (RQ-MLKEM-001, -001, -003)
and IDEA-20260901-14f9a0 / -b66dbd / -1c87ca (RQ-MLDSA-001, -ffa0f5, -001).
Every item is a pointer for a `/curate-knowledge` pass by an agent that reads
the source at a stated provenance level; nothing here promotes a KN-LIT entry
and nothing here may back `novelty_status: known` or `adaptation`.

Provenance caveat that applies to the whole note: the harness's own network
path has recorded eprint.iacr.org and nist.gov as blocked (HTTP 403 in
DEC-20260805-79d745 and elsewhere). The subagents' WebFetch/WebSearch is a
different path. The ML-KEM generator reports abstract-level reads only; the
ML-DSA generator reports rendered-PDF full reads of four papers. Those reads
are attested by one generator each and were not re-verified by this session;
the six filed records carry them as `provenance: retrieved` with `verified_by`
naming the subagent and the date, per templates/research-records.md.

## ML-KEM lane (generator report, abstract-level or title-only)

1. Bernstein, "Asymptotics of hybrid primal lattice attacks", ePrint 2023/1892.
   Already KN-LIT-2598, seeded 2026-07-24 from a local PDF's first two pages;
   the listed local copy `downloads/hybrid-20231208.pdf` was NOT found in the
   tree by the generator. Abstract formulas (z0, rho, H0 = 1/(1 + lg w /
   (0.057981 z0))) are the relayed law consumed by IDEA-20260901-7eb9e1.
   Upgrade path: read the paper; extract the exact attack, the definition of
   w, the named heuristics, and the o(1) discussion. The entry's `relevance`
   field is a seeding artifact and should be rewritten on upgrade.
2. Bernstein, "Asymptotics for the standard block size in primal lattice
   attacks: second order, formally verified" (2024). Title only. Would bound
   the o(1) that 7eb9e1's heuristic H2 assumes. Not in the corpus.
3. Glaser, May, "How to Enumerate LWE Keys as Narrow as in Kyber/Dilithium",
   CANS 2023, ePrint 2022/1337. Abstract-level: heuristic 2^{0.36 N} time and
   memory for CBD(eta=2) keys. Supplies the c = 0.36 row in 7eb9e1 and the
   representation surplus 67f498's survival exponent must beat. Not in the
   corpus.
4. "Fast Slicer for Batch-CVP: Making Lattice Hybrid Attacks Practical",
   ePrint 2025/1910. Title only. A slicer replaces nearest-plane and changes
   67f498's object; read before dispatching either hybrid idea. Not in corpus.
5. "Cool + Cruel = Dual, and New Benchmarks for Sparse LWE" (2025/2026).
   Title only; adjacent to KN-TECH-082 and RQ-MLKEM-003 target 3.
6. Ducas, Pulles, "Accurate score prediction for dual-sieve attacks" (2023;
   recalled as ePrint 2023/1850, unverified). If it derives the norm-
   conditioned score law, IDEA-20260901-2f778b's law is `known` and its
   contribution is the pre-registered null/positive-control design only.

Corpus hygiene noticed by the ML-KEM generator (not literature): KN-LIT-2598,
KN-LIT-1789, KN-LIT-5045, KN-LIT-1974 carry an identical seeding-artifact
`relevance` sentence about pairing-based reductions that is wrong for all four.
KN-TECH-082 says hybrids "do not compete" against uniform secrets while
KN-LIT-2598 in the same corpus claims the opposite asymptotically; the tension
is unrecorded and is the generative seed of 7eb9e1.

## ML-DSA lane (generator report, rendered-PDF full reads attested by the generator)

1. ePrint 2023/246 (KN-LIT-3907), Barbosa et al., "Fixing and Mechanizing the
   Security Proof of Fiat-Shamir with Aborts and Dilithium", CRYPTO 2023.
   Reported read in full (40 pages): Theorems 2/3/4 give closed-form
   CMA-to-NMA losses L and L*; Lemma 7 cascades EF-NMA to MLWE +
   SelfTargetMSIS with zeta = max{gamma1 - beta, 2 gamma2 + 1 + tau 2^{d-1}};
   Fig 8 concrete loss table; Appendix A derives commitment min-entropy from
   the rank of A-circle via a random-matrix generating function. THIS IS THE
   PDF GOAL-MLDSA-001 IS HELD ON (next_action: "if and only if full-text
   access to ePrint 2023/246 becomes available"). Whether the hold lifts is a
   Coordinator decision after an agent files the read at stated provenance;
   IDEA-20260901-14f9a0 is the proposed un-gated lane.
2. ePrint 2023/245 (KN-LIT-2028), Devevey, Fallahpour, Passelegue, Stehle.
   Currently a title-only stub; abstract page read. The concurrent
   independent CMA-to-NMA fix (bounded and unbounded loop) and the
   cross-check partner for 2023/246. Body not rendered.
3. ePrint 2025/195, Azevedo-Oliveira, Calle Viera, Cogliati, Goubin, "Finding
   a Polytope: A Practical Fault Attack Against Dilithium", PKC 2025. NOT
   filed as KN-LIT. Reported read in full (22 pages): skipping the r0 test
   recovers s2 (spec signer: invalid; reference signer F-Sig_Ref: verifies,
   Assumption 2 / Remark 9); skipping the z test recovers s1 without t0;
   about 1.25M / 3.5M / 4M signatures at levels 2/3/5, about 3.6 percent
   exploitable. Discrepancy to record rather than average: 2025/195 cites
   2024/1373 as needing 4,000,000 signatures for t0, while 2024/1373's own
   abstract says 200,000 to 500,000 (RQ-MLDSA-ffa0f5 carries the latter).
4. ePrint 2019/956 (KN-LIT-6517), Aranha, Orlandi, Takahashi, Zaverucha,
   "Security of Hedged Fiat-Shamir Signatures under Fault Attacks",
   EUROCRYPT 2020. Currently a first-two-pages stub. Reported read in full
   (24 pages): the eleven-position f0..f10 hedged-FS fault taxonomy and the
   Table 1 tolerance boundary; covers plain FS (Schnorr, XEdDSA, Picnic2),
   NOT Fiat-Shamir-with-aborts or Dilithium. IDEA-20260901-1c87ca proposes
   the transplant onto ML-DSA's abort loop.

Still not filed, and still preconditions of GOAL-MLDSA-002 per
RQ-MLDSA-ffa0f5.constraints: the FIPS 204 body (KN-LIT-4dadec is
bibliographic identity only), ePrint 2024/1373 ("Uncompressing Dilithium's
public key"), and ePrint 2026/1333 ("Apples, Oranges, and Signatures").
