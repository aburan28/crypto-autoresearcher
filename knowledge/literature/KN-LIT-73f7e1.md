---
id: KN-LIT-73f7e1
type: literature
title: Parallel Collision Search with Cryptanalytic Applications (read at source)
authors: [van Oorschot Paul C., Wiener Michael J.]
year: 1999
venue: Journal of Cryptology, 12(1):1-28 (read from the author-posted preprint dated 1996-09-23)
identifiers:
  eprint: null
  doi: 10.1007/PL00003816
  url: https://people.scs.carleton.ca/~paulv/papers/JoC97.pdf
  source_package: inputs/VOW-1996-PCS
tags: [pollard-rho, distinguished-points, parallel, collision-search, baseline, generic,
  discrete-logarithm, ecdlp, time-memory-tradeoff, memory-charged, heur-vow-curve,
  primary-source, retrieved]
confidence: established
citation_verified: read
provenance: retrieved
verified_by: coordinator session on cursor/semaev-2015-audit-program-5b8b, 2026-09-15 (DEC-20260915-fad1c1 next_actions[0]); frozen bytes and hashes in inputs/VOW-1996-PCS/provenance.json
added: 2026-09-15
superseded_by: null
complements: KN-LIT-012
---

## Why this record exists

`KN-LIT-012` records this paper from bibliographic data with the note "Full paper
not re-read". `HEUR-VOW-CURVE` — the time-memory tradeoff every memory-charged
crossover in `GOAL-SEMBIN-5078bc` is scored against (`COST-SEMBIN-8d123b`,
`COST-SEMBIN-e9960c`, `EV-SEMBIN-71e5cd`, `EV-SEMBIN-4125ec`) — was a restatement
from `KN-TECH-006` and `KN-LIT-012`, and no agent in this program had opened the
primary source. This record is the reading. It does not edit `KN-LIT-012`; it
supplies what that record says it lacks.

The frozen copy is the author-posted 1996 preprint (30 pp.), not the version of
record; section and equation numbers below are the preprint's. The derived text
(`paper_fulltext.md`) renders display equations as fragments, so every formula
below is a **restatement from the prose plus fragments**, marked (R), and prose is
quoted directly where it carries the claim.

## What the paper actually states (as read)

**Birthday bound (Section 2, Appendix A Lemma 1).** For a random function on a
set of size n, the expected number of elements selected before a duplicate is
(R) `E(X) ≈ sqrt(πn/2)`; "The error in approximating the sum with the integral is
at most 1".

**Distinguished points, single collision (Section 4.1).** m processors each run
trails from random starts until a distinguished point (proportion θ of the set),
contribute the DP to "a single common list for all processors and start again".
Quoted: "Let θ be the proportion of points ... trails have mean length 1/θ"; a
maximum trail length of 20/θ abandons looping trails (proportion ≈ e^-20). Run
time to the first useful collision, eq. (3) (R):

- `T = ( sqrt(πn/(2q)) / m + 1/θ ) · t` if collisions merely need to be detected;
- `T = ( sqrt(πn/(2q)) / m + 2.5/θ ) · t` if they must be located,

where q is the probability a collision is useful and t the time per iteration.
Quoted: "the terms 1/θ and 2.5/θ do not increase by a factor 1/q because all
other processors can go on working while a collision which has occurred is being
detected and located". The 1.5/θ locating term is Appendix B's expected maximum
of two geometrics.

**Discrete logarithms (Section 5.1).** Pollard's three-branch iteration, each
processor from `x0 = g^{a0} y^{b0}` with independent random exponents; DPs stored
as triples `(x_i, a_i, b_i)` in a list common to all processors; "collisions
merely need to be detected, not located" and q ≈ 1, so eq. (5) (R):

    T_ρ = ( sqrt(πp/2) / m + 1/θ ) · t        (group of prime order p)

The paper's constant is **sqrt(π/2) ≈ 1.2533** on `sqrt(p)`; there is no negation
map anywhere in it.

**Many collisions (Section 4.2).** With memory for w triples and overwriting,
"The required number of generated points per collision found is then nθ/w";
adding 2/θ to locate, the per-collision cost `nθ/w + 2/θ` is minimised at (R)
`θ = sqrt(2w/n)`. This is the golden-collision / meet-in-the-middle regime, **not**
the DL regime, and the paper itself says the simple analysis above is "flawed"
before refining it.

**Memory-limited search (Appendix A Lemma 2).** If only z elements can be stored,
(R) `E(Y) = Σ_{k=0}^{z-1} e^{-k²/2n} + (n/z)·e^{-z²/2n}`: the birthday sum up to z,
then a geometric tail with per-step success z/n. Section 6.1 applies it to the
rho machine "with z = w/θ and n = p": after the memory fills, "there are a total
of about w/θ points on the trails leading to the distinguished points in the
memory", and new DPs simply overwrite old ones.

**Machine design, elliptic curves over GF(2^155) (Section 6.1).** Costs: u = $0.36
per processor (75 processors per $27 chip), v = $0.0022 per memory element,
t = 13·155/(40 MHz) per curve addition. "Each memory element must hold a triple
consisting of a distinguished point x_i and two integers a_i and b_i" — 16 + 15 +
15 = **46 bytes** at p ≈ 10^36 with 32 leading zero bits of the DP not stored, at
99 % table occupancy. Budget constraint eq. (11) `mu + wv = B`, B = $10M. Run
time = eq. (5) combined with eq. (18); "Using numerical techniques to minimize
this expression ... we find that the run-time is a minimum of 32 days when
θ = (0.93)2^-32, m = 2.5×10^7, and w = 3.8×10^8. This is a total of 330000
processor chips and 16 Gbytes of memory." DP production rate mθ/t ≈ 10^7 per
second into a single memory controller.

## HEUR-VOW-CURVE scored against the source

`HEUR-VOW-CURVE` (H-SEMBIN-97ea23 `heuristic_assumptions`): "vOW total work
W = 0.886 × 2^{n/2} is independent of the store size w and the processor count M;
wall time is W(1/M + 1/w); memory is 3n·max(w, M) bits." Three constants and one
structural claim; each scored on the reading above.

1. **W = 0.886 · 2^{n/2} — half a bit BELOW the paper.** The paper's DL run time
   is `sqrt(πp/2)/m + 1/θ` iterations, constant 1.2533 on sqrt(p). 0.886 =
   sqrt(π/4) is the constant **with a negation map** (equivalence classes of
   size 2), which is not in this paper; it comes from Wiener–Zuccherato 1998 /
   Gallant–Lambert–Vanstone (`provenance: recalled` — neither has been opened
   here). So the heuristic's W is the paper's constant minus exactly 0.5 bits.
   `EV-SEMBIN-4125ec` and every crossover it reports therefore charge the vOW
   side **as a negation-map-equipped curve rho**, and the heuristic's own
   falsification condition ("more than the 0.5 bits separating the corpus's two
   walk constants") names precisely this gap. Not a falsification; a scope
   statement the heuristic text should carry and does not.

2. **Wall time W(1/M + 1/w) — the paper's eq. (5) under one identification the
   paper does not make.** Eq. (5) is `W/m + 1/θ` with θ a *free* design parameter.
   The heuristic's `W/w` term equals `1/θ` iff **θ = w/W**, i.e. the memory is
   sized to hold exactly the expected number of distinguished points the whole
   computation produces. The paper never sets θ this way: it optimises θ
   numerically under the dollar constraint mu + wv = B with the overflow penalty
   of Lemma 2. Its own optimum has `θW = 0.93·2^-32 · 1.2533·10^18 ≈ 2.7×10^8`
   against `w = 3.8×10^8`, i.e. **w ≈ 1.4·θW, within 0.5 bits of the
   identification** — so the identification is a good approximation to the
   paper's cost-optimal choice, not an exact statement of the model. Off it, the
   paper's model is two-parameter (θ, w): w < θW brings Lemma 2's `(n/z)
   e^{-z²/2n}` tail; w > θW is wasted memory. The heuristic collapses that to one
   parameter. Scored: **structurally supported, with the collapse disclosed**.

3. **Mem = 3n · max(w, M) bits — the right shape, an over-estimate by ≈ 0.3 bits
   at the paper's point.** The stored object is the triple (DP, a, b): one group
   element plus two exponents mod p, ≈ n + 2·log2(p) bits, and the paper drops
   the DP's known leading zero bits: 46 bytes = 368 bits at n = 155, log2 p ≈
   120, against 3n = 465 bits. For a prime-order curve with log2 p ≈ n, 3n is
   the natural upper bound. The `max(w, M)` clause (per-processor state as the
   floor) is not in the paper — processor state is inside the processor cost u,
   not in memory — but is of the same order and harmless. Scored: **supported as
   an upper-bound accounting**.

4. **Product invariance T·Mem = 6nW on the ray w = M, and the record point
   (M = 1, w = 2^30) being dominated.** Under items 2–3 the identity is
   arithmetic and the paper contributes nothing against it. But the paper's
   *own* design is off the ray: w/m = 3.8×10^8 / 2.5×10^7 ≈ 15.2 ≈ 2^3.9, because
   memory is 164× cheaper per unit than a processor (u/v). Under the product
   metric that point pays `3nW(w/m + 1)` against 6nW, i.e. **+3.0 bits**, and the
   record point in `COST-SEMBIN-8d123b` (w/M = 2^30) pays +29.0 bits
   (`EV-SEMBIN-4125ec` O-3). Both are off-ray in the same direction for the same
   reason — memory is cheaper than time — and neither is "unoccupiable": eq.
   (5) admits any (m, θ, w). So the heuristic's falsification clause "under which
   M = 1 with w = 2^30 is an occupiable point" is **met in the trivial sense**
   (it is occupiable) and **not met in the sense intended** (it remains dominated
   under T·Mem; the paper optimises a different, dollar-weighted objective under
   which it is simply a bad design). The clause should be reworded when C2/C3
   are restated (DEC-20260915-fad1c1 next_actions[2]).

**Net:** the primary source does **not** falsify `HEUR-VOW-CURVE`. It fixes the
W constant to sqrt(π/2)·2^{n/2} *without* a negation map (the heuristic silently
includes one, −0.5 bits), confirms the run-time shape `W/m + 1/θ`, supplies the
memory-overflow model the heuristic collapses, and adds one calibration row the
SEMBIN surface should carry: **vOW's own cost-optimal operating point has
w/M ≈ 2^3.9**, alongside sect113r2's 2^13.3 (`KN-TECH-036`) and the record's 2^30.
`supporting_results` of the heuristic may now list this record as `retrieved`;
its `status: unvalidated` in the frozen hypothesis is not edited — the
successor hypothesis carries the new status.

## What the paper does NOT say (so nobody cites it for these)

- Nothing about a negation map, equivalence classes, or the 0.886 constant.
- Nothing about Semaev summation polynomials, index calculus on curves, or any
  algebraic attack; index calculus is mentioned only for GF(p) subgroups (Schnorr,
  DSA) as the competing attack when p is small relative to q.
- No general "T × Mem" or "AT" cost metric; the paper's objective is wall time
  under a dollar budget `mu + wv = B`.
- The GF(2^155) design uses Floyd-free DP detection and a single shared memory;
  memory bandwidth (10^7 triples/s) is dismissed as easy, not modelled.

## Bibliographic note

`KN-LIT-012` is correct on venue, DOI and the qualitative claims; this record
adds the constants, equations and the machine-design numbers with line-level
provenance in `inputs/VOW-1996-PCS/paper_fulltext.md`. Teske 2001 (walk-quality
constant), Wiener–Zuccherato 1998 and Gallant–Lambert–Vanstone 2000 (negation
map) remain `recalled` pointers in this program.
