# Full-round AES: baseline map and obstruction inventory

Prepared for the Coordinator-scoped question **RQ-AES-002** (full-round AES-128/192/256,
single-key model). Nothing in this file is a claim about AES security, a distinguisher,
a key recovery, a speedup, or a barrier statement. It is a *map of the search*, an
inventory of *named obstructions*, and an *honest accounting* of what dominates what.

---

## 0. Epistemic preamble — read before using any number below

**0.1 Timestamps.** The `Bash` tool is not enabled in this session, so no wall-clock UTC
stamp could be obtained. The harness-supplied date is **2026-08-01**. Section boundaries
below are marked by ordinal, not by timestamp. Writing an invented UTC time would be a
fabrication under `AGENTS.md` rule 9, so none is written. This is a real limitation of
this session's record and is stated rather than papered over.

**0.2 Sources.** No primary cryptographic source was read. `eprint.iacr.org`,
`csrc.nist.gov` and `arxiv.org` are unreachable under this campaign's network policy
(RQ-AES-001 provenance, EV-AES-001 boundaries, EV-AES-004 boundaries — all four evidence
records record this unchanged). `WebSearch` returned **secondary reporting** (search-engine
summaries and abstract/landing pages) which is recorded below as `secondary-summary` and
which is **not** a citation of a paper anyone here read. Every complexity figure carries an
explicit recall-confidence label. Two agreeing recollections are not a citation, and a
search-engine summary agreeing with a recollection is a third recollection, not a source.

**0.3 Specification.** FIPS-197 is pinned *operationally* in this repository by the
BATCH-001 harness whose full-round outputs agree three ways (own implementation,
pycryptodome, openssl CLI) under an independent validator's own seeds — EV-AES-001 A-3,
A-5. That is the strongest grounding available here and is weaker than a read document
(EV-AES-001 A-4). All S-box counts in §3 are derived from that operational pinning and are
re-derivable locally in seconds; they are *not* quoted from a document.

**0.4 What this session did not do.** No compute was run. No AES measurement of any kind
was taken. Every quantity marked "measured" below is measured in a *cited prior record* of
this repository, never here.

---

## 1. The reference to beat, charged end to end

The only reference that is **checkable in this environment** is exhaustive key search.

| Variant | Rounds | Time (AES evaluations) | Data | Memory | Verification |
|---|---|---|---|---|---|
| AES-128 | 10 | 2^128 | 2 known P/C pairs (unicity distance) | O(1) | 1 re-encryption |
| AES-192 | 12 | 2^192 | 2 known P/C pairs | O(1) | 1 re-encryption |
| AES-256 | 14 | 2^256 | 3 known P/C pairs | O(1) | 1 re-encryption |

Charging convention adopted for everything in this file, and binding on any candidate:
**time is in full-AES-equivalent evaluations of the *same variant*; precomputation is
charged; memory is stated beside time; data is stated in plaintext/ciphertext pairs and is
charged; the final verification of a recovered key against an independent implementation is
charged.** No free oracles. No uncharged preprocessing. A "2^126" that hides 2^128 of
precomputation is 2^128.

---

## 2. The published frontier — UNVERIFIED-FROM-MEMORY, with recall confidence

**Every row in this table is unverified from memory. No paper was read.** The
`secondary-summary` marker means a WebSearch result summary was consistent with the recall;
that raises confidence in the *recollection*, it does not create a citation.

| # | Mechanism | Variant | Time | Data | Memory | Recall confidence | Corroboration |
|---|---|---|---|---|---|---|---|
| R1 | Exhaustive key search | 128 | 2^128 | 2 KP | O(1) | n/a — definitional | checkable here |
| R2 | Biclique / splice-and-cut key recovery | 128 | 2^126.1 | ~2^88 CP (data figure recall LOW) | small (recall LOW) | MEDIUM-HIGH on the time figure | secondary-summary |
| R3 | Biclique variant, minimal data | 128 | 2^126.67 | 2 KP | small | LOW-MEDIUM | secondary-summary |
| R4 | Biclique variant, best time below full codebook | 128 | 2^126.16 | < 2^128 (a 2^64-data variant reported) | small | LOW-MEDIUM | secondary-summary |
| R5 | Biclique | 192 | 2^189.7 | not recalled | not recalled | MEDIUM | secondary-summary |
| R6 | Biclique | 256 | 2^254.4 | not recalled | not recalled | MEDIUM | secondary-summary |
| R7 | Time–memory(-data) tradeoff, fixed plaintext | 128 | online ~2^85, **precomputation 2^128**, memory ~2^85 | 1 CP | ~2^85 | MEDIUM on the shape, LOW on constants | none |
| R8 | Best reduced-round single-key key recovery | 128 | 7 rounds at ~2^100+ | large | large | LOW-MEDIUM | none |
| R9 | Best reduced-round single-key key recovery | 192 / 256 | 8 / 9 rounds | large | large | LOW | none |
| R10 | Best structural distinguisher depth | 128 | 6 rounds | large | large | LOW-MEDIUM | none |

**Reading of the frontier.** Under end-to-end charging, **R7 is dominated by R1** (its
precomputation alone is 2^128 and its memory is 2^85 against O(1)). R2–R4 are the only rows
that dominate R1, and they dominate it by **~1.3 to ~1.9 bits** — a factor between roughly
2.5 and 4. Nothing in this frontier is an exponent move: the exponent has been 128 since
1998 and the published work moves a constant factor. Under
`docs/target-result-profile.md` A1/C1 the *entire published full-round frontier for AES is
non-target-class*. That is not a criticism of it; it is the calibration this session works
against, and it is the reason §3's ceiling matters.

**Explicitly out of this frontier and out of scope:** related-key, chosen-key,
known-key and open-key models (not single-key breaks — a related-key result is not
comparable to R1 and must never be reported as one); side-channel, fault, and any
implementation model (this is a mathematical question); multi-target/multi-key amortization
(changes the problem, not the cipher).

---

## 3. The three object classes, and where each dies

Per `docs/inventor-protocol.md` §1, an attack family is a choice of **tracked object**.
For *full-round* AES the enumeration splits cleanly into three classes with three
completely different failure modes. This trichotomy is the main conceptual deliverable of
this session, because it explains *why* twenty years of work has produced a 1.9-bit gain and
where the only remaining room is.

### Class A — statistical objects in the data path

Tracked objects: differential pairs; truncated/impossible differential patterns; linear
masks; integral / balanced sets; division-property vectors; DS-MITM multisets; subspace
trails; mixture/exchange tuples; boomerang and retracing-boomerang quartets; yoyo pairs;
differential-linear connectors; invariant subspaces and nonlinear invariants.

**These objects die at 4–6 rounds and the cipher has 10–14.** They are the objects this
program's RQ-AES-001 campaign has spent four batches on, at 0.5–2 rounds of survival for
the ones it constructed itself (EV-AES-001 B-5: byte-activity statistics collapse to the
null at r ≥ 3; KN-FIND-017: `Inv` preserves GF(2^8)-collinearity but the affine layer `L`
breaks it, killing projective per-byte objects in half a round).

**Obstruction O-1 (wide trail, depth).** AES's MixColumns has branch number 5 and
ShiftRows is a byte permutation across columns; the standard consequence is that any
4-round differential *characteristic* activates at least 25 S-boxes. With the AES S-box's
maximum DDT entry 4/256 = 2^-6, a 4-round characteristic has probability ≤ 2^-150 and an
8-round characteristic ≤ 2^-300. With maximum absolute S-box correlation 2^-3, a 4-round
linear characteristic has correlation ≤ 2^-75 and an 8-round one ≤ 2^-150.
*Recall confidence:* HIGH on the 25-active-S-box statement and on the S-box uniformities;
still **unverified-from-memory** because no document was read. *Locally checkable:* the
branch number of the pinned MixColumns matrix, and the exact DDT/LAT maxima of the pinned
S-box, are computable from the BATCH-001 harness in seconds. Any session using O-1 should
recompute them rather than quote this paragraph.
*Scope limit, load-bearing:* these are bounds on **characteristics**, not on **differentials
or linear hulls**, which aggregate many characteristics. O-1 therefore does not by itself
forbid a 10-round statistical distinguisher; it forbids a 10-round *single-trail* one, and
it makes a hull-based one require an aggregation gain of >150 bits, which no known
aggregation mechanism approaches.

**Obstruction O-2 (the extension budget).** A distinguisher at depth d extends to a key
recovery at depth d + e by guessing key material at both ends. For AES the empirical
pattern (recall LOW-MEDIUM) is that one extra round at one end costs roughly 2^32 guesses
with partial-sum-style aggregation and the second extra round at the same end costs
essentially the whole key. For AES-128 that caps e at about 2–3. With d = 6 (row R10) this
lands at 8–9, and the published best is 7 (row R8). **To reach 10 rounds within a 2^128
budget one needs d ≥ 8, i.e. two more rounds of distinguisher than anyone has.** That is
the gap, and it is where every attempt in this class dies.

### Class B — amortization objects in the key-search computation graph

Tracked object: not a property of the cipher at all, but a property of the *enumeration*.
Concretely, the **recomputation set**: for a key-space enumeration order and a fixed
plaintext, the set of S-box instances (round, position) in the full computation — data path
*and* key schedule, forward from P and backward from C under splice-and-cut — whose value
changes when the enumeration moves from one candidate to the next. Biclique / splice-and-cut
lives here. So does every "partial matching" and "recomputation" trick.

**These objects survive all 10–14 rounds by construction** — they are defined on the whole
cipher and there is no depth at which they "die". That is the good news, and it is why this
is the only class that has ever produced a full-round result. The bad news is a hard ceiling.

**Obstruction O-3 (the amortization ceiling). This is the sharpest quantitative statement
in this file and it is derived here, not recalled.**

Define the class by the property that makes it a class: *the attack enumerates the key
space (or a set of candidates of size 2^κ) and pays at least one S-box-equivalent of
marginal work per candidate.* An attack that eliminates candidates in batches without
touching each one is not in class B; it is a class-A distinguisher attack and is governed
by O-1/O-2.

S-box counts per full AES evaluation, derived from the FIPS-197 key-schedule rule as
operationally pinned by the BATCH-001 harness:

| Variant | Data-path S-boxes | Key-schedule S-boxes | Total N_S |
|---|---|---|---|
| AES-128 | 10 × 16 = 160 | 10 SubWord calls × 4 = 40 | **200** |
| AES-192 | 12 × 16 = 192 | 8 SubWord calls × 4 = 32 | **224** |
| AES-256 | 14 × 16 = 224 | 13 SubWord calls × 4 = 52 | **276** |

(AES-256's 13 = 7 calls at `i mod 8 == 0` plus 6 at `i mod 8 == 4`, over `i = 8..59`.)

Then the class-B time floor in full-AES-equivalents is 2^κ / N_S:

| Variant | Ceiling with key schedule charged | Ceiling with key schedule free (optimistic) | Best published (R2/R5/R6) | Head-room left in the class |
|---|---|---|---|---|
| AES-128 | 2^128 / 200 = **2^120.36** | 2^128 / 160 = 2^120.68 | 2^126.1 | ≤ 5.7 bits |
| AES-192 | 2^192 / 224 = **2^184.19** | 2^192 / 192 = 2^184.42 | 2^189.7 | ≤ 5.5 bits |
| AES-256 | 2^256 / 276 = **2^247.89** | 2^256 / 224 = 2^248.19 | 2^254.4 | ≤ 6.5 bits |

**Consequences, stated plainly.**
1. Class B **cannot produce an exponent-moving result, ever**. Its total possible gain over
   exhaustive search is bounded by log2(N_S) ≈ 7.6 / 7.8 / 8.1 bits. Under
   `docs/target-result-profile.md` A1 the class is non-target-class *by construction*, not
   by accident and not for want of effort.
2. The published frontier sits within ~6 bits of its own class ceiling. A hypothetical
   perfect class-B attack would be reported as "AES-128 broken in 2^120.4" and would still
   leave AES-128 with 120 bits of security.
3. The ceiling is a statement **about the class**, not about AES. It is a theorem about the
   definition (one nonlinear operation per enumerated candidate), which is why it needs no
   heuristic. What it does *not* rule out is a hybrid that uses a class-A filter to avoid
   enumerating most candidates — and that hybrid is governed by O-1/O-2, not by O-3.

**Obstruction O-4 (deterministic-filter requirement).** The natural way to escape O-3 is to
eliminate 2^d candidates per unit of work using an offline key-difference structure: find a
key difference Δ and an output projection π (b bits) such that
π(E_K(P)) = π(E_{K⊕Δ}(P)) holds for essentially *all* K. Then one evaluation eliminates a
whole coset of ⟨Δ⟩. Note carefully: **this uses no related-key oracle** — both encryptions
are computed by the attacker offline — so it is a legitimate single-key mechanism, and it is
the mechanism bicliques already exploit in a short-trail form.

The requirement is q = Pr_K[π-invariance] ≈ 1, **not** merely q above random. A filter with
failure rate ε discards the true key with probability ε, so ε must be below ~2^-40 for a
usable attack. A q ≈ 1 projected invariance is a probability-one truncated key-differential
over the full round count; O-1's trail bound applies to the combined key-schedule/data-path
trail, and the AES key schedule diffuses a single-byte master-key difference to a
full-state round-key difference within about 3 rounds. The prediction is that q hits 2^-b
(the null) by round 3–4 and stays there. **This prediction has never been measured in this
program, at any round count, and measuring it is CAND-FR-2 in the companion report.**

### Class C — algebraic objects

Tracked object: the polynomial system itself — the ideal generated by the S-box relations
plus the affine layers, in state and key variables. XSL-style attacks, Gröbner-basis
attacks, the BES embedding, SAT/MILP-based algebraic key recovery.

**This is the only class whose object survives to round 10 with no loss whatsoever**, because
the system is an exact description of the cipher and gets *larger*, not weaker, with rounds.
Nothing "dies". What blocks it is solving complexity.

**Obstruction O-5 (the variable-count obstruction). Derived here.**
There exist generic algorithms solving quadratic systems over GF(2) in N variables in time
2^{cN} with c < 1 (the "polynomial method" line; recall MEDIUM-HIGH that such results exist,
LOW-MEDIUM on the constants, which I recall as c ≈ 0.9 and later c ≈ 0.88). *If* AES-128 key
recovery were a quadratic system in ~128 variables, such an algorithm would give ~2^115 and
would be a genuine exponent-adjacent result. It is not:

- A quadratic representation requires a **fresh variable for the output of every S-box**,
  because inversion is not quadratic in the input alone. AES-128 has 200 S-boxes.
- Equivalently, the state at each round boundary is 128 fresh bits. A quadratic system for
  10 rounds therefore needs **N ≥ 10 × 128 + 128 = 1408 GF(2) variables**.
- 2^{0.88 × 1408} = 2^{1239}. Even at c = 0.5 it is 2^704. **Generic MQ solving on AES-128
  costs at least five to ten times the exponent of exhaustive search.** The gap is not
  close and no constant-factor improvement in c touches it.
- Eliminating the 1280 state variables to get back to 128 key variables is exactly what
  destroys quadraticity: the degree of a single round in the key is already 7 per byte and
  saturates at the field bound within about 3 rounds.

**This is the precise trap XSL fell into** (recall MEDIUM: XSL's complexity estimate was
subsequently shown not to hold), and any future algebraic candidate must state where its
variable count sits before it states a complexity.

**Forward guidance for class C, since a closure must name what remains open.** The escape
route is an algorithm whose exponent is in a *structural parameter* of the equation
hypergraph rather than the raw variable count — treewidth, pathwidth, or a
separator-based dynamic program. The natural path decomposition of AES follows the rounds
and its bags contain the round-boundary state plus the running key material, i.e. width
≈ 128 + 128 = 256, giving a DP cost ≈ 2^256 — *worse* than exhaustive search. To beat 2^128
one needs width < 128, i.e. a separator of the round boundary smaller than the state. The
round function is a bijection on the full 128-bit state, so no proper subset of the state
determines the next state; that is a strong heuristic argument that no such separator
exists. **It is an argument, not a theorem: this session did not derive a rigorous treewidth
lower bound for the AES equation hypergraph, and that derivation is a concrete open item.**

---

## 4. Deduplication register

Every family the directive named, with its class and its verdict as the *primary lens* for
RQ-AES-002. All are **declared off-limits as a primary lens** per `docs/inventor-protocol.md`
§1; they appear here so that any future candidate can be checked against them.

| Family | Class | Tracked object | Verdict |
|---|---|---|---|
| Biclique / splice-and-cut | B | recomputation set + key-difference biclique | the incumbent (R2–R6); ceiling O-3 |
| MITM / Demirci–Selcuk | A (+B for the enumeration) | δ-set multiset / matching table | table parameter count exceeds the key size at 5 rounds (recall LOW); caps the family near 8–9 rounds |
| Integral / square | A | balanced set | dies at 4, extended to 5 by division property |
| Impossible differential | A | truncated-difference contradiction | dies at 4-round impossibility; key recovery to 7 |
| Boomerang / retracing boomerang | A | adaptive quartet | 5–6 rounds |
| Differential-linear (incl. DLCT) | A | connector between a differential and a linear part | 5–6 rounds |
| Division property / three-subset | A | monomial-support vector | refines integral; 5 rounds |
| Yoyo | A | adaptive pair orbit | 5 rounds |
| Invariant subspace / nonlinear invariant | A | a set or function preserved by the round | dies in ≤1 round on AES; Rcon and MDS destroy it; KN-FIND-017 is the local shadow of this |
| Algebraic / XSL | C | polynomial ideal | survives depth, blocked by O-5 |
| Related-key differential | — | key-difference trail with oracle queries | **not a single-key break**; out of scope as an attack, in scope only as an *offline* device (O-4), where no related-key query is made |
| Key schedule / slide | B | self-similarity of the round sequence | Rcon breaks self-similarity; AES-128 schedule is bijective |
| Side channel / fault | — | — | **out of scope: this is a mathematical question** |

Distinguisher and key-recovery depths in this table are UNVERIFIED-FROM-MEMORY at
recall confidence LOW-MEDIUM and are used only to locate the gap, never as baselines.

---

## 5. The lossy-projection test, applied before any experiment

Per `docs/inventor-protocol.md` §2. Costs no compute; run first. Four objects considered
this session, two of which failed here and were dropped before reaching the candidate list.

**5.1 `σ(K)` — the key-schedule S-box output vector. FAILS (not lossy).**
For AES-128 let σ = (s_1,…,s_10) ∈ GF(2^8)^40 be the four SubWord output bytes at each key
schedule step. Given σ, the whole expanded key is a *GF(2)-affine* function of the master
key: EK = A·K ⊕ B·σ ⊕ c, with A, B fixed and c carrying Rcon. This looks like a promising
linearization. It is not a new object: s_1 = SubWord(RotWord(W[3])) and both SubWord and
RotWord are bijections, so s_1 determines W[3]; the chain then determines the rest. **σ
determines K.** Nothing is discarded, so this is a change of coordinates, not an object. It
is recorded because it is exactly the shape a reader would plausibly mistake for leverage,
and because it is the honest reason "the key schedule is nearly linear" does not by itself
produce a single-key attack.

**5.2 The linear approximation with a key mask, ⟨α,P⟩ ⊕ ⟨β,C⟩ ⊕ ⟨γ,K⟩. FAILS (loses
nothing that shortens the path).** A key mask γ propagates through the key schedule almost
freely — only 40 S-boxes stand in its way for AES-128 — which is the intuition behind
"exploit the low key-schedule diffusion". But γ enters the computation only at AddRoundKey.
The approximation still needs a mask trail through the **full 10-round data path**, and O-1
bounds that trail regardless of what the key mask does. **Low key-schedule diffusion buys
nothing in the single-key linear model.** This is a clean closure of a direction the
directive explicitly flagged as a prompt, and it is stated so that the next session does not
spend a batch on it.

**5.3 The recomputation set (CAND-FR-1). PASSES.** The projection maps a full internal state
trajectory to the *support* of its difference under a key move — a 16-bit activity pattern
per round rather than 128 bits of value. It is massively lossy. It propagates
deterministically in the conservative direction (an inactive byte is certainly inactive; an
active byte may accidentally be inactive, which makes the count an upper bound and the
implied speedup a *lower* bound — the safe direction). What is discarded (values) is
discarded compatibly with AddRoundKey (acts trivially on differences), ShiftRows (permutes
supports) and MixColumns (support propagation by the branch-number rule); it is discarded
*conservatively* at SubBytes, which preserves support. Verdict: a genuine lossy projection.

**5.4 The projected key-difference invariance class (CAND-FR-2). PASSES.** The projection
maps a key K to the pair (coset K⊕⟨Δ⟩, π(E_K(P))) — it discards *which element of the coset*
K is, and it discards all but b bits of the ciphertext. Both discards are large. The
retained part propagates deterministically **iff** the invariance holds, which is exactly the
measured quantity; that is what makes the object testable rather than assumed. Verdict: a
genuine lossy projection, whose fidelity is the experiment.

---

## 6. Where the gap is, in one paragraph

For AES-128 the published statistical frontier reaches a 6-round distinguisher and a 7-round
key recovery; the cipher has 10 rounds. The extension budget (O-2) buys 2–3 rounds, so a
statistical break needs a **depth-8 distinguisher**, two rounds beyond anything published,
against a trail bound (O-1) that puts an 8-round characteristic at ≤ 2^-300. The only class
that reaches round 10 at all cheaply is class B, and it is capped at 7.6 bits of total gain
(O-3). The only class that reaches round 10 with no structural loss is class C, and it is
capped by a variable count nine times too large (O-5). **Every route to a full-round AES
break must therefore either produce a depth-8 statistical object, or produce an algebraic
solver parameterized by something other than variable count, or introduce a fourth object
class that this session did not find.** Naming that fourth class is the open problem.

---

## 7. Honest accounting for this session

- **Objects considered:** 6 (σ(K) linearization; key-masked linear approximation;
  recomputation set; projected key-difference invariance; the class-C polynomial ideal; the
  treewidth/separator object). 2 dropped at the lossy-projection test, 2 promoted to
  candidates, 2 recorded as closures with forward guidance.
- **`dominated_by`:** every candidate produced this session is dominated by row **R4**
  (2^126.16, data < 2^128) and by rows R2/R3, all of which dominate exhaustive search R1.
  Rows R1–R10 were each checked against each candidate on time, memory, and data/queries.
  `null` is not written anywhere.
- **`sota_delta`:** 0 bits predicted for both candidates. The *class ceiling* for the only
  class either candidate lives in is 5.7 bits below the best published figure for AES-128,
  and that ceiling is not an exponent move under `docs/target-result-profile.md` A1.
- **Closures enumerated:** O-1 (trail depth, scoped to characteristics not hulls), O-2
  (extension budget), O-3 (amortization ceiling — the one derived here), O-4 (deterministic
  filter requirement — predicted, measurable, and unmeasured), O-5 (variable count), plus
  the two lossy-projection failures §5.1 and §5.2.
- **Open directions for the next session:** (i) a rigorous treewidth/separator lower bound
  for the AES equation hypergraph — currently an argument, not a theorem; (ii) whether any
  aggregation mechanism can recover 150 bits between a characteristic bound and a hull, which
  is the only crack in O-1; (iii) a *fourth* object class — this session found none, and that
  is a statement about this session's search, not about AES; (iv) the class-C first-fall-degree
  measurement, which is **declared out of the 4-core / 15 GB / no-numpy / no-sage envelope**
  rather than estimated.
- **Novelty status of everything above:** `unverified`. Literature was not checkable. O-3 and
  O-5 were derived here but are elementary and the honest expectation is that both are well
  known to specialists.
