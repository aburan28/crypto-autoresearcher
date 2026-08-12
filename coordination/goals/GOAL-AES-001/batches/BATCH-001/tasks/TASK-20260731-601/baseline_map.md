# Reduced-Round AES Baseline Map (rounds 3–7)

TASK-20260731-601 · GOAL-AES-001 · RQ-AES-001
Role: idea-generator. Claim tier ceiling: **toy / reduced-round only**.
Nothing in this document is a statement about full-round AES or about deployed
AES security.

---

## 0. Provenance and the honesty rule that governs every number below

**No primary source was read for this document.** Every complexity figure in
§§2–7 is **recalled from memory** and is tagged `unverified_from_memory`
together with a self-assessed recall confidence (`high` / `medium` / `low`).
A recalled number is a *working target to beat or re-derive*, never a citation.
Under AGENTS.md rule 9, presenting any of these as if a source had been read
would be a fabrication.

### 0.1 Network attempts actually made in this session, and what happened

| Attempt | Tool | Target | Actual result |
|---|---|---|---|
| 1 | WebSearch | `best known attack 7-round AES-128 meet-in-the-middle complexity Derbez Fouque Jean` | Returned. Result set was link titles plus a **secondary model-generated summary**. The summary asserted 2^105 chosen plaintexts / 2^99 work / 2^90 storage for the 7-round AES-128 DS-MITM attack. This is a search-engine summary, **not a read source**; it is recorded as weak corroboration of recall, not as a citation. |
| 2 | WebFetch | `https://eprint.iacr.org/2013/366` | **HTTP 403 Forbidden.** Body not retrieved. |
| 3 | WebFetch | `https://www.di.ens.fr/~fouque/pub/euro13b.pdf` | **HTTP 403 Forbidden.** Body not retrieved. |
| 4 | WebFetch | `https://www.di.ens.fr/~fouque/pub/fse13b.pdf` | **HTTP 403 Forbidden.** Body not retrieved. |

No primary cryptographic document was fetched. This matches the network policy
recorded in `GOAL-AES-001.environment_context` and `RQ-AES-001.provenance`.

### 0.2 In-corpus material actually read (and its own epistemic status)

- `knowledge/literature/KN-LIT-7593.md` — the Möbius-bridge 7-round AES report.
  Read in full **as a corpus note**. That note is itself `confidence: reported`
  and states explicitly that nothing in it has been re-derived or re-run by
  this program, and that the [DS08]/[DKS10]/[DFJ13]/[BKR11] complexities in it
  are *relayed from the Möbius paper's own account*, not checked. So a number
  taken from KN-LIT-7593 is second-hand-relayed and is tagged
  `unverified_from_memory (corpus-relayed)`.
- `knowledge/literature/KN-LIT-7595.md` — the discovery-session transcript note.
  Read in full. Source of the recorded per-byte closure argument and of five
  recorded negative closures, all of which this session treats as **prior art
  to deduplicate against**, not as verified mathematics.
- `knowledge/literature/KN-LIT-7594.md` — the program-level blog note. Read in
  full.

### 0.3 Specification pinning

The AES specification is **not** cited from a read document here. It is pinned
operationally by the FIPS-197 known-answer harness being built concurrently in
TASK-20260731-602. Every quantitative statement in the candidate report is
conditioned on that harness's declared reduced-round convention (which final
round transformations are retained at `r < full`), because the convention
changes the answers.

---

## 1. Object-first framing and the off-limits declaration

Per `docs/inventor-protocol.md` §1, an attack family is a choice of **tracked
object** — the thing followed through the computation.

| Family | Tracked object |
|---|---|
| Differential | an ordered pair of texts, projected to its XOR difference |
| Linear | a parity bit / GF(2)-linear functional and its correlation |
| Integral / square | a whole structured set, projected to a coordinate-wise sum |
| Division property / three-subset | the algebraic degree / monomial support of the set |
| Boomerang, retracing boomerang | adaptive two-directional oracle interaction, plus (retracing) a dependency between the two halves |
| Meet-in-the-middle / Demirci–Selçuk | a multiset fingerprint of a δ-set, used as a table key |
| Biclique | an independent-bicliques structure over the key space |
| Yoyo | an adaptively generated orbit under a cipher-induced involution |
| Differential-linear | a differential followed by a linear approximation, coupled at a junction |

**These nine families are declared OFF-LIMITS as the primary analytical lens
for this session.** In addition, the following two objects are declared prior
art inside this program's own corpus and are also off-limits as a primary lens:

- the **Möbius / projective (PGL(2,2^8)) invariant** on per-byte data, used to
  make a DS-MITM fingerprint invariant to a key byte (KN-LIT-7593);
- the five negative closures recorded in KN-LIT-7595 (χ-statistical bias at
  r ≥ 3; multiplicative-character bias at r ≥ 3; the GF(2^8) rank of the Δ-set
  matrix at r ≥ 4; GF(2)-flats ≡ second-order differentials; the state-rotation
  commutator).

KN-LIT-7595's closure argument also supplies the **residual classes** this
session works in: it argues (unverified here) that no sixth *per-byte
algebraic* lens survives both `Inv` and `L`, and names the classes that remain
open as **multi-byte-coupled, information-theoretic, and adaptive**. This
session generates against those three named residuals rather than re-treading
the enumerated families.

---

## 2. Round 3

| Family | Object at 3 rounds | Recalled parameters | Tag |
|---|---|---|---|
| Integral / square | Λ-set with one active byte; every state byte is balanced (XOR-sums to 0) after 3 rounds | 2^8 chosen plaintexts for the distinguisher | `unverified_from_memory`, recall **high** |
| Integral key recovery | above, extended by one round | ≈2^9 data, ≈2^9–2^11 time for 4-round AES-128 (see §3) | `unverified_from_memory`, recall medium |
| Impossible differential | truncated ID sub-paths inside the 4-round ID | — | `unverified_from_memory`, recall high (existence), low (parameters) |
| Division property | bit-based division property re-derives the 3-round integral property | — | `unverified_from_memory`, recall medium |
| Subspace trail / structural | 2 rounds of deterministic subspace/geometric structure; the corpus's own measurement (KN-LIT-7595) records `rounds_structure: 2` and a 3-round GF(2^8) rank-drop event at P ≈ 4/256 ≈ 1.5% | — | corpus-relayed, **not re-run here** |

Three rounds is not a meaningful cost frontier: it is broken by inspection.
Its role in this campaign is as the **positive-control regime** for any new
propagation object — a new statistic that does not fire at r ≤ 2 is measuring
the wrong thing.

## 3. Round 4

| Family | Object at 4 rounds | Recalled parameters | Tag |
|---|---|---|---|
| Integral / square | 3-round balanced property extended by guessing last-round key bytes | ≈2^9 chosen plaintexts, ≈2^11 time (AES-128) | `unverified_from_memory`, recall medium |
| Integral distinguisher | Λ-set with 4 active bytes; balanced after 4 rounds | 2^32 chosen plaintexts | `unverified_from_memory`, recall high |
| Impossible differential | miss-in-the-middle: one active byte in / one active byte out over 4 rounds is impossible | 4 rounds is the recalled maximum length of a *truncated* byte-level ID for AES | `unverified_from_memory`, recall high (existence), medium (maximality) |
| Yoyo | adaptive orbit; 4-round distinguisher with very few adaptive queries | ≈2^4–2^8 adaptive chosen texts | `unverified_from_memory`, recall medium (existence), low (parameters) |
| DS-MITM | the 4-round δ-set multiset fingerprint — the object that DKS10/DFJ13 tabulate | fingerprint determined by ≈25 parameter bytes [DS08], tightened to ≈10 [DFJ13] | `unverified_from_memory (corpus-relayed via KN-LIT-7593)`, recall medium |
| Division property | recalled to **fail to extend** the AES integral distinguisher beyond 4 rounds | — | `unverified_from_memory`, recall medium. **This is the single most important recalled obstruction for RQ object #1** and is flagged for re-derivation, not assumed. |

## 4. Round 5

Five rounds is the **practical** frontier and the most contested band.

| Family | Object at 5 rounds | Recalled parameters | Tag |
|---|---|---|---|
| Multiple-of-8 / subspace trail | a *counting congruence*: the number of pairs from a diagonal coset whose ciphertexts lie in the same coset of a mixed space is ≡ 0 mod 8 | 5-round secret-key distinguisher, 2^32 chosen plaintexts | `unverified_from_memory`, recall medium-high (statement), medium (data) |
| Yoyo | adaptive orbit | 5-round distinguisher ≈2^11–2^12 adaptive chosen texts; 5-round key recovery ≈2^31 | `unverified_from_memory`, recall medium |
| Mixture differential | quadruples exchanged between diagonal cosets | 5-round key recovery, order 2^21–2^24 time | `unverified_from_memory`, recall **low** — exponents deliberately given as a range |
| Practical-complexity key recovery | improved 5-round attacks with practical data *and* memory | ≈2^16–2^17 data, ≈2^16–2^17 memory, ≈2^21–2^23 time | `unverified_from_memory`, recall **low** on exponents, medium on existence |
| Impossible differential | 4-round ID plus one round | order 2^31 data, 2^33 time | `unverified_from_memory`, recall low |
| Integral / partial sums | 4-round distinguisher plus one key-recovery round | dominated at 5 rounds by the above | `unverified_from_memory`, recall low |

**Consequence for this campaign.** Any *new* 5-round distinguisher must be
compared against ≈2^32 chosen plaintexts (multiple-of-8) and against ≈2^11
adaptive queries (yoyo) simultaneously — two different Pareto axes. A candidate
that beats one and not the other is dominated.

## 5. Round 6

| Family | Object at 6 rounds | Recalled parameters | Tag |
|---|---|---|---|
| Integral + partial sums | the **partial-sum cost term**: an aggregation over ciphertexts, reorganized to peel one guessed key byte at a time | ≈6·2^32 chosen plaintexts, ≈2^44 time (AES-128) | `unverified_from_memory`, recall medium |
| Exchange attack | exchanged-difference structure | 6-round secret-key distinguisher, order 2^83–2^88 chosen plaintexts | `unverified_from_memory`, recall medium (existence), low (exponent) |
| Impossible differential | 4-round ID plus two rounds | order 2^91 time | `unverified_from_memory`, recall low |
| DS-MITM | 4-round fingerprint plus outer rounds; not the best at 6 | — | `unverified_from_memory`, recall low |

## 6. Round 7

This is the band where the campaign's own corpus already contains a very
recent result, so deduplication here is unusually sharp.

| Family | Object at 7 rounds | Recalled parameters | Tag |
|---|---|---|---|
| DS-MITM [DFJ13] | 4-round multiset fingerprint table, 10 parameter bytes, differential enumeration | 2^105 chosen plaintexts, 2^99 time, 2^90 memory (AES-128) | `unverified_from_memory (corpus-relayed via KN-LIT-7593)`, recall **high**; weakly corroborated by the §0.1 WebSearch summary, which is **not a read source** |
| DS-MITM + projective invariant (Möbius bridge, KN-LIT-7593) | the DS-MITM fingerprint made invariant to the key byte *below* the table as well as above it, via the `L ∘ Inv` factorization of the S-box | 2^105 chosen plaintexts, 2^89.3–2^91.4 time (range is an accounting-choice spread, not a measurement spread) | `unverified_from_memory (corpus-relayed)`, recall high; the corpus note itself states the attack **cannot be run** and was validated by a partial ladder |
| Impossible differential | 4-round ID plus outer rounds | ≈2^106 data, ≈2^110 time, ≈2^94 memory (AES-128) | `unverified_from_memory`, recall **low-medium**; exponents should be treated as ±2 |
| DKS10 | first 7-round AES-128 attack below exhaustive search; multiset fingerprint invariant to one key byte on the input side, table shrunk 2^200 → 2^127 by differential enumeration | ≈2^116 time | `unverified_from_memory (corpus-relayed)`, recall medium |
| AES-192 / AES-256 at 7 rounds | cheaper than AES-128 because more key material is available per round | **no exponents recalled with sufficient confidence to state** | not stated |

**Full-round AES and bicliques are out of scope** for this campaign
(`RQ-AES-001.scope.round_counts_out_of_scope`) and are named here only to mark
the boundary, with no parameters given.

---

## 7. Where the frontier actually sits, expressed as cost boundaries to beat

A candidate at round count *r* must be compared against **all** of the
following at that same *r*, with data, time, memory, precomputation, and
verification charged end to end:

- **r = 3, 4** — no meaningful boundary; use as instrument controls only.
- **r = 5** — beat *either* (2^32 CP, distinguisher) *or* (≈2^11 adaptive
  queries, distinguisher) *or* (≈2^17 data / ≈2^22 time, key recovery), without
  losing on the other axes.
- **r = 6** — beat (≈2^34 CP, ≈2^44 time) for key recovery, or (≈2^83–2^88 CP)
  for a secret-key distinguisher.
- **r = 7** — beat (2^105 CP, 2^89.3–2^91.4 time, ≈2^90 memory), i.e. the
  Möbius-bridge line, **not** the 2^99 DFJ13 line, since the corpus already
  records the improvement.

All figures `unverified_from_memory` as tagged above.

---

## 8. Standing obstructions recalled at the family level

These are the reasons the corresponding RQ-AES-001 objects are hard, recorded
so that a candidate must engage with them rather than route around them. Each
is `unverified_from_memory` and each is flagged as something to **re-derive
locally**, not to assume.

1. **Integral / division property (RQ object 1).** The bit-based division
   property is recalled to reproduce, and not to extend, the 4-round AES
   integral distinguisher. If true, the division-property lane at r ≥ 5 is
   closed *by an automated search that has already been run by others*, and a
   candidate in that lane must explain what its object sees that the division
   property cannot represent. Recall: medium. **Re-derivation route: none
   inside the local envelope** — a bit-based division-property propagation over
   AES needs MILP/SAT tooling that is not installed (no sage, no solver).
   Recorded as an obstruction that this campaign cannot itself check.
2. **Impossible differential (RQ object 5).** There is recalled to be a
   published *provable-security* result showing that, when the S-box is modeled
   as ideal, AES has **no truncated impossible differential covering 5 or more
   rounds**. Recall: medium. If true, the residual in this lane is exclusively
   *S-box-dependent* (non-truncated) impossible differentials — a much narrower
   and much less explored target. This is the most useful piece of forward
   guidance in this section.
3. **Key schedule (RQ object 2).** The AES-128 key schedule is a bijection on
   128-bit state with four new words produced per round from four old ones.
   There is therefore **no redundancy to exploit within one round transition**:
   an invariant cannot reduce the count of independent unknowns below the
   number of distinct master-key bits actually referenced. "Key bridging"
   works because *different positions in an attack reference the same master
   key bits*, which is a GF(2)-linear-span rank computation, and that
   computation is already exact in the published DS-MITM analyses. This
   argument is derived here, is checkable, and does **not** rest on recall.
4. **DS-MITM (RQ object 3).** The corpus's own KN-LIT-7593 already spent the
   most obvious remaining structural degree of freedom — making the fingerprint
   invariant to the key byte on the second side. It also records the
   generalizable caution that an invariance which eliminates a search dimension
   **is not a speedup until the cost of computing the invariant is charged**
   (there, naïve evaluation cost ≈2^19 lookups against a 2^8 saving, and the
   result existed only after three implementation optimizations paid it back).
5. **Partial sums (RQ object 4).** A reorganization of the key-guess
   aggregation is a *cost-term* improvement, not an exponent-mover in the sense
   of `docs/target-result-profile.md` A1. It should be proposed only with that
   classification stated up front.

---

## 9. What this map does not contain

- No verified citation of any kind.
- No AES-192/AES-256 exponents at 7 rounds (recall insufficient).
- No claim about full-round AES, biclique parameters, or deployed AES.
- No assertion that the recalled frontier is the true frontier. Recall drift of
  ±2 in an exponent is entirely plausible, and a candidate whose entire margin
  is smaller than ±2 bits **cannot be adjudicated in this environment** and must
  say so.
