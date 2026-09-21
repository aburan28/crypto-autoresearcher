---
id: KN-LIT-7592
type: literature
title: "HAWK-n Key Recovery Reduces to SVP in Dimension n/2 + 1"
authors:
  - "Zygimantas Straznickas"
  - "Stephen A. Weis"
year: 2026
venue: 'Anthropic technical report (released 2026-07-28; disclosed to the HAWK authors in June 2026 and to the NIST PQC mailing list)'
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: https://anthropic.com/document/hawk_key_recovery.pdf
tags: [hawk, lattice-isomorphism-problem, module-lip, cyclotomic, galois-automorphism, key-recovery, svp, nist-pqc, post-quantum, signature, llm-assisted-discovery, gate-count, cost-model]
confidence: reported
citation_verified: read
added: "2026-07-28"
superseded_by: null
---

> **`citation_verified` upgraded `web` → `read` on 2026-08-02** by
> TASK-20260802-004 (GOAL-HAWK-001 / BATCH-001), per the maintenance rule in
> `knowledge/SEEDING.md`. The full text was obtained from
> `https://anthropic.com/document/hawk_key_recovery.pdf`,
> `sha256:056faead316ea9a8eb01000cb9c548e79e21ad09a0684c3d52bbc1093183ac89`
> (748154 bytes), and read. **No claim below is edited** — the entry's existing
> body was checked against the full text and its characterization of the result
> as unconditional and heuristic-free is confirmed by a regex census
> (`Heuristic` ×0, `Conjecture` ×0; the single `Assumption` conditions the
> cost-comparison table on HAWK's own `[HAWK25, Table 8]` model, not the
> reduction).
>
> One fact the body does **not** carry, added by supersession-free annotation
> rather than by editing a claim: the paper states that proving the relevant
> lattice *exactly* near-hypercubic "upgrades the endgame from the heuristic
> pricing of [GP25, Thm. 1] to the unconditional accounting of Theorem 6.1" —
> i.e. it does not merely reuse van Gent–Pulles's descent ([[KN-LIT-7673]]), it
> **discharges that paper's Heuristic 1**. See
> `coordination/goals/GOAL-HAWK-001/batches/BATCH-001/tasks/TASK-20260802-004/disclosed_attack_transcription.md`.

## Contribution
An unconditional, deterministic polynomial-time reduction from HAWK-`n` key recovery
over `K_n = Q(ζ_{2^ℓ})` to `poly(n)` calls to an **exact-SVP oracle in dimension
`n/2 + 1`**, where `n = 2^{ℓ-1}` is the ring degree. Roughly halves HAWK's effective
key strength. Discovered semi-autonomously by Claude Mythos Preview in an agentic
harness (see [[KN-LIT-7594]]).

## Key claims (as reported)
- HAWK's secret key is a short basis `B ∈ SL_2(R_n)` of `R_n^2`; the public key is the
  Gram matrix `Q = B*B`. Key recovery is search module-LIP (smLIP) for the isometry
  class of `R_n^2`.
- Prior module-LIP cryptanalysis works with **complex conjugation** `c`, whose fixed
  field is totally real. This paper instead uses a **second order-2 Galois involution**
  `τ : ζ ↦ -ζ`, whose fixed field is the complex cyclotomic subfield `Q(ζ^2)`.
- The `τ`-cocycle `V_τ = B^{-1} τ(B)` is a shortest vector of a **publicly computable**
  rank-`n` lattice `Λ_B^{(τ)} ⊂ M_2(R_n)`, cut out by Q-linear constraints whose
  coefficients depend only on the public `Q` (Lemma 4.1, Lemma 4.3).
- That lattice is proved isometric to the near-hypercubic lattice
  `sqrt(n/4) Z^{n/2+1} ⊕ sqrt(n/2) Z^{n/2-1}` (Proposition 4.5), so **Ducas's block
  reduction** [Duc23; BN24] recovers all its shortest vectors with SVP calls in
  dimension only `n/2 + 1` (Theorem 5.1); `O(n^2 log n)` oracle calls suffice.
- Key recovery from `V_τ` is the **descent of van Gent and Pulles** [GP25]: the kernel
  sublattice `{x ∈ R_n^2 : τ(x) = V_τ^{-1} x}` is isometric to a scaled `Z^n`, and one
  further run of Ducas's algorithm returns an equivalent key. Exactly two of the
  `2(n/2+1)` shortest-vector candidates, `±V_τ`, satisfy `Y ≡ I (mod 2)`.
- Main result (Theorem 6.1): for every power of two `n ≥ 4`, HAWK-`n` key recovery
  reduces deterministically to `poly(n)` arithmetic operations and `poly(n)` exact-SVP
  calls in dimension at most `n/2 + 1`.
- In the **gate-count model of the HAWK specification** [AGPS20; HAWK25 §5.3], the
  reduction lowers key-recovery cost from `2^150` to at most `2^108` for HAWK-512 and
  from `2^288` to at most `2^182` for HAWK-1024. HAWK's designers had derived BKZ
  blocksizes `β_key ∈ {211, 452, 940}`.
- **Demonstrated end-to-end**: a practical implementation recovers a HAWK-256 secret key
  in a few hours on a single server; in practice a single progressive sieve sufficed for
  the dimension-`n/2+1` SVP step.
- **Scope of the attack.** The construction does **not** transfer to Falcon (Appendix F).
  Conductors `m ∈ {p^k, 2p^k}` for odd prime `p` — i.e. the `m > 4` with cyclic
  `(Z/m)^×` — evade it, because they have no second involution to use; the authors
  expect many other composite conductors do not evade it.
- The attack is exponential, not polynomial: it is a **faster exponential-time attack**.
  Per the accompanying blog post, the practical consequence is that HAWK key sizes must
  roughly double for the claimed security levels, which removes much of HAWK's
  compactness advantage as a PQC signature candidate.

## Relevance to this program
Recorded for three distinct reasons, which should not be conflated.

**1. As a target-profile exemplar, not an ECDLP result.** This is an
exponent/parameter-moving result on a central hard problem, validated at the scheme's
own parameter sets and costed in the specification's own gate-count model — the shape
`docs/target-result-profile.md` asks for. It is **stronger than the profile requires in
one respect**: the reduction is unconditional and deterministic, with no numbered
heuristics. It does **not** bear on the ECDLP: HAWK is a lattice scheme and the attack
is specific to the Galois structure of power-of-two cyclotomic fields.

**2. The transferable methodological move.** The attack's engine is: *the object
hiding the secret admits more than one order-2 symmetry, and the whole prior literature
used only one of them.* Prior smLIP cryptanalysis used complex conjugation; `τ` was
available the entire time and unexploited, and the payoff came from the fact that the
`τ`-cocycle lands in a lattice whose shape (near-hypercubic) already had a specialized
sub-exponential-advantage algorithm waiting for it. That two-part shape — *unused
symmetry* + *the resulting object falls into a class with a known better-than-generic
algorithm* — is the pattern worth carrying, and it is close kin to the composition
recorded in `KN-TECH-055`. It also supplies the sharpest available caution for this
program's own novelty discipline: a symmetry being "well known to exist" is not the same
as its consequences having been worked out.

**3. The scope statement is the model to copy.** The paper states exactly which
conductors evade the attack and why (cyclic `(Z/m)^×` ⇒ no second involution), and
explicitly checks and reports that Falcon is unaffected. That is `AGENTS.md` rule 4
practiced by an external group, and it is what an evidence record in this program should
look like.

**No ECDLP claim is made or implied here, and this entry must not be cited as bearing on
the elliptic-curve discrete logarithm.** Its ECDLP-adjacent value is methodological only.

## Not verified here
Full paper text retrieved from the official Anthropic URL above on 2026-07-28 and read
at the level of the abstract, introduction, and technical overview (§§1–2);
`confidence: reported`. The body sections (§§3–9) and appendices were not read line by
line, and **no claim in this entry has been independently re-derived or re-run by this
program**.

NOT verified here: Lemma 4.1, Lemma 4.3, Proposition 4.5 (the isometry to the
near-hypercubic class), Theorem 5.1, Proposition D.2, and Theorem 6.1; the `O(n^2 log n)`
oracle-call bound; the correctness of the cited Ducas block reduction and van Gent–Pulles
descent as used; the gate-count conversions `2^150 → 2^108` and `2^288 → 2^182`, which
inherit every modelling assumption of [AGPS20] and of the HAWK specification's own cost
model; the claimed end-to-end HAWK-256 recovery (the demonstration code was not fetched
or run); the Falcon non-transfer argument; and the conductor-based evasion criterion.
This is a preprint released by the discovering party — not peer-reviewed, no DOI or venue
as of this entry — though the blog post states the result was disclosed to the HAWK
authors in June 2026 and reviewed with outside academics. The HAWK team's response, if
any, is not recorded here.