---
id: KN-LIT-7592
type: literature
<<<<<<< HEAD
title: Linear Descent for Rank-2 and Rank-4 Module-LIP
authors: [Anonymous]
year: null
venue: Anonymous submission (unrefereed; venue and date not stated in the text)
identifiers:
  eprint: null
  doi: null
  url: null
tags: [module-lip, hawk, lattice-isomorphism, linear-descent, symmetric-square, hodge-star, exterior-square, svp, cm-field, lenstra-silverberg, bambury-nguyen, pqc]
confidence: reported
citation_verified: full_text_supplied
added: 2026-07-28
superseded_by: null
---

> **Provenance caveat.** The full text was supplied directly by the user on
> 2026-07-28. The submission is anonymous and states no venue, date, ePrint
> number, or DOI, so **the citation cannot be independently resolved** and the
> results are unrefereed. Everything below is recorded as *reported by the
> paper*, not as verified. The cited prior work (Lenstra–Silverberg,
> Bambury–Nguyen, Luo et al., Mureau et al., HAWK) is separately checkable and
> is where the load-bearing external machinery sits.

> **ID allocation.** Filed as `KN-LIT-7592` because `main`'s literature corpus
> already occupies `KN-LIT-001`…`KN-LIT-7591` while this branch's runs only to
> `081`. Allocating the next local number would have created an add/add
> collision of exactly the kind `CORR-20260724-001` and `KN-LIT-081` already
> record. Chosen above `main`'s maximum so the note merges cleanly.

## Contribution

End-to-end **linear descents** for determinant-one Module-LIP in module ranks
two and four, over a CM extension `L/L+` with `d = [L+ : Q]`, `R = O_L`,
`S = O_{L+}`.

The framing is the paper's main methodological point: a smaller lattice is *not*
a search reduction. Three things must hold together —

1. the auxiliary lattice and metric are computable from public input and
   transported by every hidden isometry;
2. the relevant SVP output is **recognizable** inside that lattice; and
3. the recognized data **determines a transition** for the original instance,
   including its integral module structure.

The paper argues (2) and (3) are routinely blurred: an isometry of an auxiliary
lattice need not lie in the tensor representation of an isometry of the original
module, and independently recovered rank-one pieces need not glue integrally.

**Rank two (symmetric-square descent).** A conjugate-linear symmetry induces a
three-dimensional `L+`-fixed space in `Sym²_L(V)`. Its integral points form a
rank-`3d` lattice, identified via `Φ(u) = κ(u)J₂` with the integral trace-zero
self-adjoint endomorphisms. Cayley–Hamilton forces `X² = q·I₂` with `q` totally
positive, and the trace metric is minimized exactly at `q = 1` — so **the unit
shell consists exactly of involutions**. A matched source/target involution pair
exposes two rank-one submodules; two Lenstra–Silverberg recoveries plus exact
module and Hermitian tests reconstruct the transition. For the standard
power-of-two cyclotomic orbit the source shortest shell is explicit
(`{±D} ∪ {±E_j}`), with gap `√2` to the next length, so **one γ-SVP output with
γ < √2 suffices**.

**Rank four (Hodge descent).** The Hermitian Hodge involution on `Λ²_L V` gives a
rank-`6d` auxiliary lattice. For an orthogonal pseudobasis it decomposes as three
weighted rank-one ideal lattices. Given a matched exterior-square map `T = Λ²C`,
the spaces `T(e_i ∧ V)` recover four image lines by elementary wedge-annihilator
computations; four rank-one Lenstra–Silverberg calls plus exact module,
Hermitian, determinant and compound-matrix tests reconstruct `C`. For the
standard cyclotomic orbit the Hodge lattice is **hypercubic**, and the public
`S`-action of `s = ζ + ζ⁻¹` splits a recovered shortest basis into three signed
`N`-cycles, reducing basis matching to a **polynomial signed-cycle enumeration**
(at most `6(4N)³` candidates).

**Oracle-rank reduction.** Bambury–Nguyen is applied only *after* the direct
decoding chains close. Rank two: a calibrated primal–dual lattice with minima
product `1/2` puts the two required involution types in primal and dual shortest
shells, giving oracle calls of rank `≤ ⌊3d/2⌋ + 1`. Rank four: the hypercubic
algorithm recovers the shortest basis with calls of rank `≤ 3d + 1`.

## Verified scope, as the paper itself delimits it

The paper is unusually explicit about the boundary, and §5 should be read before
citing any result:

- **Complete SVP-to-Module-LIP reductions are proved only for the standard free
  power-of-two cyclotomic orbit** (Thm 20, Thm 36).
- The fixed-space constructions and matched-data decoders hold for **arbitrary
  projective modules**; the rank-four lattice shape is explicit for **every
  orthogonal pseudobasis**.
- **Open, and stated as the remaining obstacle:** completing generic SVP output
  on three weighted ideal summands to a list containing the hidden `S`-linear
  exterior-square map. Such a lattice **need not be hypercubic** and its shortest
  vectors **need not form a recognizable basis**.
- Determinant-one is part of the *normalized problem*, not a free assumption.
  Prop 4 handles free `GL_r(R)` branches via Lenstra–Silverberg norm recovery
  over finitely many root-of-unity branches; a general projective determinant
  line needs separate ideal and norm data.
- Bambury–Nguyen reduces oracle rank only. It performs **no** eigenline recovery,
  Hodge-basis completion, or Lenstra–Silverberg assembly.
- No claim rests on an auxiliary-lattice isometry alone: every candidate is
  checked against the original Module-LIP equations.

## Relevance to this program

**Directly relevant to the PQC lattice goals, not to ECDLP.** Rank-2 Module-LIP
over power-of-two cyclotomics is the structured problem underlying **HAWK**
(KN-LIT-4174), so this bears on `GOAL-MLKEM-001` / `GOAL-CRYPTO-001` and on
nothing in `RQ-ECDLP-002`. Filed for the corpus, not as an ECDLP frontier item.

**Methodological transfer worth flagging.** The paper's three-part standard for
when a descent becomes a reduction is close to the failure mode this campaign has
hit repeatedly, from the other direction:

- *"the SVP output must be recognizable"* ↔ `EXP-STR-002`'s `phi_alpha`, where
  the metric turned out to count row-insertion bookkeeping rather than
  φ-invariance (see `DEC-20260727-009`, `EV-STR-003`).
- *"the recognized data must determine a transition, including integral module
  structure"* ↔ the repeated finding that a quantity can be measured exactly and
  still license nothing, e.g. `EV-IC-002`'s crossover, where `K* = ∞` against the
  correct multi-target baseline regardless of the measured quantity.
- The paper's insistence that recovered rank-one pieces **need not glue
  integrally** is the same class of gap as `EXP-ENDO-001`'s witness lattice
  `W_r`, which is not attacker-constructible at all (`REF-20260728-002`).

The transferable rule: *a lower-dimensional invariant that is transported by the
hidden map is necessary but not sufficient; recognition and lifting are separate
obligations and each needs its own exact test.*

## External machinery relied on

- **Lenstra–Silverberg**, *Testing isomorphism of lattices over CM-orders*, SIAM
  J. Comput. 48(4):1300–1334 (2019) — rank-one norm-constrained generator
  recovery; solutions unique up to `µ(L)`.
- **Bambury–Nguyen**, PQCrypto 2024, LNCS 14771:343–370 — primal–dual and
  hypercubic oracle-rank reduction.
- **Luo–Jiang–Pan–Wang**, ASIACRYPT 2024, LNCS 15487:359–385 — rank-two
  symplectic automorphism eigenspace strategy, used as a black box.
- **Mureau–Pellet-Mary–Pliatsok–Wallet**, EUROCRYPT 2024; **Allombert–
  Pellet-Mary–van Woerden**, EUROCRYPT 2025; **Chevignard et al.**, EUROCRYPT
  2025 — prior rank-2 Module-LIP cryptanalysis under other hypotheses.
- **Ducas–Postlethwaite–Pulles–van Woerden**, ASIACRYPT 2022 — HAWK.

## Related corpus entries

`KN-LIT-4174` (HAWK), `KN-LIT-1356` (commitments from Module-LIP),
`KN-LIT-4314` (hull attacks on LIP), `KN-LIT-5513` (LIP, quadratic forms and
remarkable lattices) — all on `main`; this note is additive and does not
supersede them.

## Open questions this raises

1. Does the rank-four basis-completion obstacle admit a `HAWK`-relevant
   instantiation, or is it confined to non-cyclotomic weighted ideal families?
2. Is there a rank-`2^k` generalization, or do the symplectic (`r=2`) and Hodge
   (`r=4`) identities exhaust the exact determinant identities available?
3. Does the paper's recognition/lifting standard have a stateable analogue for
   index-calculus descents, where the "auxiliary lattice" is a relation matrix?
   This is the one thread with possible ECDLP contact, and it is speculative.
=======
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
citation_verified: web
added: "2026-07-28"
superseded_by: null
---

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
>>>>>>> origin/main
