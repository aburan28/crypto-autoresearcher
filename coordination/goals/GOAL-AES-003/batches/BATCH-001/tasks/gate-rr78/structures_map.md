# Structures that reach 7-8 rounds of AES-128: an object-first map with runnable gates

Session role: Idea Generator. Scope: `RQ-AES-001` / `RQ-AES-002` reduced-round lane.
Written to scratchpad only. **Nothing in this file is a claim about AES security, a
distinguisher that exists, a key recovery, a speedup, or a barrier statement.** No ledger
record is written, no state is changed, no evidence strength is assigned.

---

## 0. Epistemic preamble - read before using any number below

**0.1 Timestamps.** The `Bash` tool is **not enabled in this subagent session**. No
wall-clock UTC stamp could be obtained at start, at boundaries, or at halt. The
harness-supplied date is **2026-08-01**. Writing an invented UTC time would be a
fabrication under `AGENTS.md` rule 9, so none is written. Section boundaries below are
marked by ordinal. This is the same limitation `baseline_map.md` §0.1 recorded for the
GOAL-AES-002 ideation session and it is stated rather than papered over. The 2400 s budget
was therefore tracked by turn count and volume of work, not by clock, and the session
halted on judgement rather than on a measured boundary. **That is a weaker discipline than
the brief asked for and it is reported as such.**

**0.2 Sources.** No primary cryptographic source was read. No `WebSearch` was run this
session. Every recalled fact below carries an `UNVERIFIED-FROM-MEMORY` tag with a recall
confidence, and per `DEC-20260731-019` ruling 3 **no recalled figure is used either to
promote or to dismiss any candidate**. Where a recalled fact would otherwise be
load-bearing, it is replaced by a gate that decides the question on this machine. Two
agreeing recollections are not a citation.

**0.3 What this session did not do.** **Zero compute was run.** No AES measurement of any
kind was taken here. Every quantity marked "measured" is measured in a *cited prior record
of this repository*, never here. Every gate below is a **proposal**, and no gate outcome is
reported, predicted-as-observed, or implied.

**0.4 Inherited corrections that must not be re-broken.** Three campaign self-corrections
bind this document:

- `CORRECTION-influence-and-O3.json` F-2: **a statistic with no power reads as a closure.**
  Influence-support density 0.4996 at r=3 was read as death; a pure random function reads
  0.4995 on the same probe. Every gate below therefore states its **detection floor** and
  its **null object of the same shape**, and no "dead at round k" is asserted from a single
  projection.
- `CORRECTION-influence-and-O3.json` F-1 / `O3-resolution.json` / `O3-residual-closed.json`:
  O-3's premise (>= 1 S-box per candidate) is **measurably false** (mu falls 194 -> 125 ->
  12.3 as coset dimension rises), and its conclusion survives on the *different* ground
  that full-state and >=4-byte projections do not collide across a structured key set
  (4096/4096 distinct at every round, d=12). **The 7.64-bit figure is the wrong
  justification for the right bound.** No candidate below is promoted or dismissed by the
  7.64-bit ceiling.
- `DEC-20260731-017` / RT-9: **"I could not exhibit an upper bound" is a fact about the
  search, not an `IN_SCOPE_VACUOUS` verdict on the candidate.** Every candidate below that
  I cannot bound is recorded `DEFERRED_UNBOUNDED` and is kept **out** of any count of
  candidates ruled out. Interface counting follows the campaign-wide rule adopted in
  `DEC-20260731-017` §(ii): `n` counts consecutive **super-box interfaces** the object must
  survive; traversal of an invariance group at one fixed interface costs `n = 1`.

**0.5 The one closure standard in force.** `docs/inventor-protocol.md` §4. A lane is closed
only with a named obstruction, an argument, and forward guidance. A count of rejected
mechanisms is a fatigue report and its honest status is `unverified`. **This document
closes no lane.**

---

## 1. The depth budget, written as arithmetic

Total attacked rounds `R = d + t + b`:

- `d` = depth of the distinguisher (rounds over which the tracked object's signature
  survives against its matched null);
- `t` = rounds bought at the **top** by guessing key material that maps a chosen plaintext
  structure into the distinguisher's required input structure;
- `b` = rounds bought at the **bottom** by partially decrypting ciphertexts under guessed
  last-round key material back to the distinguisher's output position.

The two shapes the brief names:

| shape | d | t | b | R |
|---|---|---|---|---|
| integral | 4 | 1 | 2 | 7 |
| deeper distinguisher | 5 | 1 | 1 | 7 |
| the 8-round shape | 6 | 1 | 1 | 8 |
| the 8-round shape, alternative | 5 | 1 | 2 | 8 |

**The leverage is in `d` and in the *cost* of `t` and `b`, not in their existence.** `t` and
`b` are always *available*; what varies by three orders of magnitude is what they cost. The
whole of §3 is about `d`; the whole of §4 is about the price of `t` and `b`.

**What this campaign has already measured about `d`** (cited, not recalled):

| object | measured depth | source |
|---|---|---|
| 1-byte delta-set XOR balance | survives 3, null at 4 | `depth_wall_receipt.json` MEAS-GOAL-AES-002-002 |
| full-diagonal 2^32 delta-set XOR balance | **16/16 balanced at r=4, 0/16 at r=5** (2 keys) | same, `measurement_2_full_diagonal_AESNI` |
| per-cell key-bit influence bias | 43.84 sd at r=3, null at r=4 | `findings.yaml` MEAS-RT-B |
| mixture quadruple, **byte-collision readout** | matched null at r=4..10 | `findings.yaml` MEAS-RT-C |
| mixture quadruple, **round-1 difference identity** | **HOLDS, 2000/2000 quadruples** | same, TEST0 |

The last two rows are the single most important fact in this file and they must be read
together. The red team's own scope limit is binding: *"The object is verified to exist;
exactly ONE lossy readout of it was tested. Calling the object dead on this evidence would
be the fatigue report this red team exists to police."* Its byte-collision readout also
carried an **unexplained instrument artifact** (ratio 1.012-1.018 present *equally in the
null* at every round 4-10, mixture arm never above null). So: **the mixture object is
untested at depth, not dead.** §3.1 is built on exactly that opening.

---

## 2. Object enumeration, and what is declared off-limits

Per `docs/inventor-protocol.md` §1, an attack family is a choice of **tracked object**. The
established families for reduced-round AES are named in `baseline_map.md` §4 and are
**declared off-limits as the primary lens for this session**: raw differential pairs, raw
linear masks, raw integral balance, invariant subspaces, biclique recomputation sets,
related-key trails, XSL-style ideals.

What remains, enumerated as **objects** rather than as ideas, each scored on the three axes
`docs/inventor-protocol.md` §1 requires (new-vs-repackaging / concretely testable / how far
it survives):

| # | tracked object | new? | one-step propagation definable? | survival axis |
|---|---|---|---|---|
| O-A | **mixed-space pair-count residue** of a full diagonal-subspace coset | repackaging of a recalled family, but **never measured in this program** | yes, exactly (§3.1) | the experiment |
| O-B | **zero-difference pattern** of an adaptive pair orbit (yoyo) | repackaging, **never measured here** | yes (§3.2) | the experiment |
| O-C | **partial-sum register**: the running aggregate of a bottom-extension fold | genuinely new *as an object* (§4.1) | yes | by construction, all `b` rounds |
| O-D | **truncated activity support** (16-bit) under a miss-in-the-middle contradiction | repackaging; the campaign's `CAND-FR-1` §5.3 projection analysis applies verbatim | yes | 4 (claimed), the experiment |
| O-E | **DS-MITM parameter tuple** (not the sequence - see §3.5) | sharpened here | yes | table size binds, not depth |
| O-F | **null object**: the same objects on a same-shape random construction | mandatory control | yes | by construction |

Objects considered and **dropped at the lossy-projection test before any experiment**
(`docs/inventor-protocol.md` §2, costs no compute):

- **The 255-byte delta-set output sequence itself.** 255 bytes = 2040 bits > 128 bits of
  key. As a map from (key, structure) to sequence this is **not lossy** - it almost
  certainly *determines* the key. Under §2 that makes it a change of coordinates, not an
  object. **This is a real correction to how the DS-MITM family is usually framed here:**
  what makes DS-MITM work is not lossiness of the sequence, it is *precomputability* - the
  sequence factors through a small **parameter tuple**. The object is therefore O-E, the
  parameter tuple, and the lossiness is `state -> parameters`. This relabelling is what
  makes the binding cost (table size) visible instead of hidden. Recorded because it is
  exactly the shape §5.1 of `baseline_map.md` caught for `sigma(K)`.
- **The full ciphertext difference of a mixture quadruple.** Not lossy at all; tracking it
  is tracking the pair. The mixture object only becomes an object at a projection, which is
  why the readout choice (§3.1) is the entire content.

---

## 3. Depth: what actually reaches 5, and whether anything reaches 6

### 3.1 O-A - the mixed-space pair-count residue. **Highest-value object on this list.**

**Definition, self-contained, no literature input.** Work in `GF(2^8)^{4x4}` with the
FIPS-197 byte order operationally pinned by the BATCH-001 harness. For `I` a subset of
`{0,1,2,3}`:

- `D_I` = the **diagonal space**: states supported on the ShiftRows diagonals indexed by
  `I` (for `I = {0}`, byte positions `{0,5,10,15}`).
- `C_I` = the **column space**: states supported on columns `I`.
- `M_I = MC(C_I)` = the **mixed space**, the MixColumns image of a column space.

Two elementary facts, each **checkable on this machine in seconds and not recalled**:

1. `SR(D_I) = C_I` exactly (ShiftRows is a byte permutation carrying diagonals to columns),
   so a coset of `D_I` maps under one round to a coset of `C_I`: SubBytes acts bytewise and
   preserves *support*, ShiftRows relabels, MixColumns and AddRoundKey are `GF(2)`-affine.
2. Hence a coset of `D_I` maps under **two** rounds to a coset of `M_I`. This is a
   **deterministic 2-round property** and its mechanism is exactly the branch-number-free
   part of the wide-trail argument: no probability enters.

**The tracked object.** Take a full coset `V` of a diagonal subspace. Encrypt `r` rounds.
Fix a mixed space `M_J`. Define

```
n_r(K, V, J) = #{ unordered pairs {c, c'} subset of E_K^r(V) : c XOR c' in M_J }
```

The object is the **integer `n_r`**, and the signature tested is its **residue modulo a
small power of 2**, together with its magnitude against the null.

**Lossy-projection test (§2), applied before any experiment.** The projection maps `2^24`
full 128-bit ciphertexts (`2^31` bits of state) to **one integer**. It is maximally lossy.
What it discards - the values, the ordering, the identity of which pair hit `M_J` - is
discarded *compatibly* with the operations that generate the structure: the coset structure
of `V` is preserved by every affine layer, pair membership in `M_J` is a linear condition
invariant under AddRoundKey, and the pairing that would force a residue is an involution on
the pair set, which is a set-level and not a value-level notion. **PASSES**, and - this is
the honest part - *whether the residue still propagates deterministically past round 4 is
exactly the experiment*, not an assumption.

**Why a residue rather than a bias.** A residue is **deterministic**. It has no detection
floor, no sd, no sample-size argument, and therefore it is immune to the failure mode
`CORRECTION-influence-and-O3.json` F-2 records: a statistic with no power cannot masquerade
as a closure, because under the null the residue is uniform on 8 values and 20 independent
agreeing trials cost `8^-20 = 2^-60`. This is the single strongest reason to rank O-A
first.

**Recall marker, used for neither promotion nor dismissal.** That a "multiple-of-8" pair
count of this shape is a known property of 4- or 5-round AES is
**UNVERIFIED-FROM-MEMORY, recall confidence MEDIUM**; that the subspace-trail
diagonal/column/mixed vocabulary is standard is **UNVERIFIED-FROM-MEMORY, recall MEDIUM-HIGH**.
Neither is load-bearing: **facts 1 and 2 above are re-derivable locally in seconds, and the
gate decides the residue question by measurement.** If the recall is wrong the gate returns
a null and the candidate falls; if the recall is right the gate returns it in 0.2 s. That
is the correct handling under ruling 3.

**Depth it reaches, and why it stops.** Deterministically, 2 rounds (fact 2). The residue
claim is the assertion that a *pairing argument* extends the signature past the point where
the subspace trail itself dissolves. My honest position on where it stops: **the trail
dissolves at round 3** (a coset of `M_I` is not contained in any proper subspace after a
further round, because MixColumns applied to a full column space spans), so any depth
beyond 3 is carried entirely by the pairing/orbit argument and not by the trail. **I do not
know how far the pairing argument reaches and I decline to guess.** The gate measures
`r = 3, 4, 5, 6` at identical cost and the `r = 6` arm is **free**.

**Cost of the gate.** See `candidate_report.yaml` GATE-RR78-1. Stage 1 is `2^24`
encryptions (about 0.2 s on one core at the campaign's own measured 8.1e7 reduced-round
AES/s/core) plus one hash-table pass; a full stage-2 confirmation at `2^32` costs about
53 s/core plus a 4 GB counter array.

**What each outcome means - pre-registered, both directions.**

| stage-1 outcome | reading |
|---|---|
| residue 0 at r=2,3,4 and at r=5, null uniform | a **5-round deterministic signature** on this machine; O-A is the depth object and §4's extension arithmetic applies to `d = 5` |
| residue 0 through r=4, uniform at r=5 | depth pinned at 4; O-A adds nothing over the measured integral and `d = 4` stands |
| residue 0 at r=5 **and r=6** | the highest-value outcome available in this envelope; the 6-round question is answered affirmatively **for this object and this readout only**, and 8 rounds becomes the extension question of §4 |
| residue uniform already at r=3 | either the sub-coset of stage 1 broke the algebra (run stage 2) or the recalled family shape is wrong here; **either way a real answer** |
| residue 0 at every r including r=10 | **artifact tell** (`docs/inventor-protocol.md` §3): a quantity that fails to decay when the parameter meant to destroy it increases. Suspect the counting code, not AES. This is the MEAS-RT-C shape and it must be checked for explicitly |

**The mandatory null.** Identical measurement with (a) `r = 10` full AES as the
random-permutation surrogate, (b) the coset `V` replaced by `2^24` uniformly random
plaintexts of the same cardinality, (c) an independent-round-key variant of the same wiring
(same code path, key schedule replaced by fresh random round keys). Control (c) is the one
that separates "AES" from "AES-shaped", and it is the control MEAS-RT-C did not have.

### 3.2 O-B - the yoyo zero-difference pattern. **Cheapest gate in this file.**

**Definition.** Two rounds of AES are a "super-box" layer. For a pair of states `(x, y)`
define the **zero-difference pattern** `nu(x,y) in {0,1}^4`, bit `i` set iff the `i`-th
wide-trail cell (column after SR, or diagonal, depending on which side of the middle you
sit) of `x XOR y` is zero. The **yoyo swap** takes a pair `(c1, c2)` of ciphertexts and
produces `(c1', c2')` by exchanging a proper nonempty subset of the wide-trail cells
between them; the pair is then decrypted, re-paired, re-encrypted, adaptively.

**Lossy-projection test.** 128-bit difference -> 4-bit pattern. Massively lossy. The
discard is compatible: SubBytes preserves zero-ness bytewise (`S(a) = S(b) iff a = b`),
ShiftRows relabels cells, MixColumns acts within a column so a wholly-zero column stays
zero. **PASSES.** This is the *same* projection family as `CAND-FR-1` §5.3 - conservative
at SubBytes - which is why the campaign's own analysis transfers verbatim.

**Why it is not the mixture object.** MEAS-RT-C's mixture object is a **static**
pair-of-pairs constructed at the plaintext side. O-B is **adaptive and two-directional**:
it uses the decryption oracle, which the attacker owns here because the key is ours. That
is a different object under `docs/inventor-protocol.md` §1's enumeration (boomerang tracks
adaptive two-directional oracle interaction; integral tracks whole sets), and the campaign
has measured **neither** adaptive object. `depth_wall_receipt.json`'s own `not_established`
block names "BACKWARD/decryption-direction integral depth (53 s per sweep, **never run**)".

**Depth it reaches, and why it stops.** The pattern is preserved by the swap across a
super-box layer by the same bytewise argument; the mechanism that destroys it is
MixColumns *mixing a zero cell with a nonzero one at the next layer*, which the branch
number 5 makes generic after two mixing layers on each side of the middle. My derived
expectation is therefore that the object survives roughly `2 + 2` layers with the middle
free, i.e. around 5 rounds, **and I state that as a derivation to be measured, not as a
result.** Recall that a 5-round yoyo of this shape exists is
**UNVERIFIED-FROM-MEMORY, recall confidence LOW-MEDIUM**, and is used for neither promotion
nor dismissal - the gate decides.

**Cost of the gate.** `2^11` to `2^25` adaptive queries. **Seconds.** The entire cost is
implementation (encrypt and decrypt with AES-NI, `_mm_aesdec_si128` plus
`_mm_aesimc_si128` for the equivalent decryption schedule), not compute.

**Discrimination.** The measured quantity is `Pr[nu(swapped pair) = nu(original pair)]`
against the null of a random re-pairing. Both outcomes are informative: preservation well
above null at `r = 5` is a 5-round adaptive object; preservation at null from `r = 4`
onward pins the depth at 4 and is a genuine scoped negative closing this readout of this
object.

### 3.3 The 6-round question. **Straight answer.**

**Do I believe a 6-round distinguisher exists?**

*As a matter of what is in the literature:* I do not know, and I refuse to answer from
memory. `baseline_map.md` row R10 records "best structural distinguisher depth 6 rounds" at
recall confidence **LOW-MEDIUM** with data and time both recorded as "large". Per ruling 3
that row may not promote or dismiss anything, and I use it for neither.

*As a matter of what I can argue here:* my honest position is **a 6-round distinguisher is
plausible but the version that would matter almost certainly is not cheap**, and the
distinction is the whole answer. Here is the argument, and it is an argument and not a
theorem:

1. Every deterministic structure this machine can exhibit bottoms out in the subspace trail,
   which is worth **2 rounds** forward and **2 rounds** backward (§3.1 facts 1-2, applied in
   both directions). That is 4 rounds of *free* structure with nothing in the middle.
2. Every object that reaches 5 does so by adding a **pairing, orbit, or counting** argument
   that survives one further mixing layer *without* propagating a difference pattern -
   O-A's residue and O-B's swap are both exactly this, and so is the mixture identity the
   campaign verified 2000/2000.
3. To reach **6** an object must survive **three** mixing layers on one side of the middle.
   The branch number argument gives no handle there: after three layers every byte of the
   difference depends on every byte, so no support-based, coset-based, or cell-based
   projection is preserved. **What remains is only a counting argument that is insensitive
   to the values**, and I cannot name a mechanism that supplies one.
4. Therefore my expectation is that any 6-round distinguisher pays for the third layer in
   **data**, which is precisely why "large" is the honest entry in row R10 - and a
   distinguisher costing near-codebook data does **not** make 8 rounds a routine extension,
   because §4's extension multiplies data by the top structure and time by the guess space.
   **A 6-round distinguisher that does not fit in `2^128 / (extension cost)` buys nothing.**

**What I will not do is declare it impossible** (Idea Generator prohibition; and
`docs/inventor-protocol.md` §4 requires forward guidance rather than a verdict). The
concrete forward position is better than an opinion: **GATE-RR78-1 tests `r = 6` at zero
marginal cost.** The `r = 6` arm is the same program, the same coset, the same counter
pass, one extra AESENC. If the residue survives to 6, the answer is affirmative and it was
obtained in 0.2 s. If it does not, the answer is "not by this object", which is a scoped
negative and closes exactly one readout of one object. **That is the cheapest possible
purchase of an answer to the highest-value question in the brief, and it is why O-A is
ranked first.**

**Premature-closure guard.** Nothing above is a closure of the 6-round question. It has a
named difficulty (three mixing layers defeat every support-based projection I can construct)
but **no obstruction argument**, so under `docs/inventor-protocol.md` §4 its honest status
is `unverified` and it is recorded that way in `candidate_report.yaml`, **not** as a lane
closed.

---

## 4. The extension budget: what `t` and `b` actually cost

### 4.1 O-C - the partial-sum register, and what partial sums buys at the bottom

This is the part of the brief that asks for arithmetic rather than a name, so here is the
arithmetic, **derived here and not recalled**, with the derivation exposed so it can be
attacked.

**Setup.** A 4-round integral distinguisher asserts that a particular byte `z` of the round-4
output has `XOR_{x in V} z(x) = 0` over the `2^32`-text structure `V`. Attack 5 rounds:
each ciphertext byte must be partially decrypted through round 5 back to `z`. Writing the
last round as SB, SR, ARK (no MixColumns in the final round, the convention pinned in
GOAL-AES-001 BATCH-001), and folding `MC^{-1}` into an equivalent key `k'`, the target is

```
Sigma(k1..k4, k') = XOR_{x in V} S^{-1}( c1 . S^{-1}(x_1 XOR k1)
                                   XOR c2 . S^{-1}(x_2 XOR k2)
                                   XOR c3 . S^{-1}(x_3 XOR k3)
                                   XOR c4 . S^{-1}(x_4 XOR k4) XOR k' )
```

with `c1..c4` the fixed `MC^{-1}` row coefficients and `x_1..x_4` four ciphertext bytes.

**Naive cost.** `2^32` guesses of `(k1..k4)` times `2^8` of `k'` times `2^32` texts =
**`2^72`** per structure. That is the number partial sums exists to kill.

**The object.** Define the **partial-sum register** after folding `j` bytes:

```
y_0 = 0 ,   y_j = y_{j-1} XOR c_j . S^{-1}(x_j XOR k_j)
```

The tracked object is the tuple `(y_j, x_{j+1}, ..., x_4)` - the running aggregate plus the
*not-yet-folded* ciphertext bytes.

**Lossy-projection test.** At stage `j` the projection maps a text to
`(y_j, x_{j+1..4})`: `8 + 8(4-j)` bits retained out of the `32` bits of `(x_1..x_4)`, so at
`j = 1` nothing is lost (`8 + 24 = 32`), at `j = 2` it is `8 + 16 = 24` bits from `32`, at
`j = 3` it is `8 + 8 = 16`, at `j = 4` it is `8`. **Lossy from stage 2 onward, and the
discard is exactly compatible with the target: `Sigma` depends on the folded bytes only
through `y_j`, by construction.** PASSES - and note this is a projection defined on the
*computation*, not on the cipher, which is why it is an object in the class-B sense of
`baseline_map.md` §3 rather than the class-A sense.

**Cost, stage by stage, per structure.** A stage is a pass over the current table for each
guess of the newly folded key byte:

| stage | guesses so far | table size in | table size out | pass cost |
|---|---|---|---|---|
| 1 | `2^8` | `2^32` | `2^32` | `2^40` |
| 2 | `2^16` | `2^32` | `2^24` | `2^48` |
| 3 | `2^24` | `2^24` | `2^16` | `2^48` |
| 4 | `2^32` | `2^16` | `2^8` | `2^48` |

Total about `4 . 2^48 = 2^50` per structure, against `2^72` naive.

**So the honest answer to "what does the extension budget actually buy at the bottom" is:**

> Partial sums does **not** buy a round. It buys a **factor of about `2^22` on the price of
> the round you were already buying**, by converting `data x guesses` into a sequence of
> table passes each costing `max(data, accumulated guess space) x (guess space of the byte
> being folded)`. The round itself is bought by the `2^32` key guess and nothing else.

**And the sharp consequence for `b = 2`, which is the actual question at 7 rounds:** the
second bottom round requires the *whole* of `k_{10}` plus a diagonal of `k_9`. The AES-128
key schedule makes `k_9` a function of `k_{10}`, so the guess space is `2^128` on its face,
and the partial-sum fold does not reduce it - the fold reduces the cost *per guess*, not the
number of guesses. **I cannot exhibit an upper bound below `2^128` for `d=4, t=1, b=2`
without machinery I would have to recall.** Under the RT-9 correction that is recorded as
**`DEFERRED_UNBOUNDED`** - a fact about this session's search - and **not** as
`IN_SCOPE_VACUOUS`. It is emphatically **not** a statement that 7-round integral attacks do
not exist.

**Cost of the top round `t = 1`.** Guess 4 bytes of `k_0` (`2^32`) so that a chosen
plaintext structure is partitioned into sets that are diagonal cosets at the input to round
2. Time multiplies by `2^32`; data multiplies by the number of structures needed. **`t` is
cheap in data and expensive in time, `b` is the reverse.** This asymmetry is what makes the
`d=5, t=1, b=1` shape strictly better than `d=4, t=1, b=2` at equal `R = 7`, and it is the
second reason O-A is ranked first.

**GATE-RR78-3 measures this rather than arguing it.** See §5.

### 4.2 O-D - impossible differentials, and how many rounds key-guessing wraps around

**The object** is the 16-bit **truncated activity support**, and the property is a
*miss-in-the-middle*: a forward truncated pattern that holds with probability 1 for `a`
rounds and a backward one that holds with probability 1 for `b` rounds, whose middles are
incompatible, yielding an `(a+b)`-round **impossible** transition.

**Lossy-projection test.** Identical to `baseline_map.md` §5.3, which the campaign already
ran and passed: `128 -> 16` bits, discarded compatibly with ARK (trivial on differences),
SR (permutes supports), MC (branch-number support rule), and *conservatively* at SB
(support-preserving; an accidental cancellation makes the pattern an over-estimate, which is
the safe direction). **PASSES.**

**Depth, and why it stops.** From §3.1 fact 2 the deterministic reach is 2 rounds forward
and 2 backward, so `a + b = 4` is what the trail supplies and the contradiction has to sit
in the middle. **It stops at 4 for the same reason O-A's trail stops at 3 in one
direction:** MixColumns applied to a full column space spans, so there is no third
deterministic layer to harvest.

**What key-guessing wraps around it.** The distinctive economics of impossible differentials
is that the extension is a **sieve, not a sum**: each pair that *does* exhibit the impossible
pattern under a candidate key **eliminates** that key. So the cost is
`(pairs needed) x (partial decryption cost)` and the *number* of surviving candidates falls
geometrically, which lets `t` and `b` be larger than a summing attack tolerates - typically
`t + b = 3` on a `d = 4` core, reaching `R = 7`. **The binding resource is data, not time**,
because you need enough pairs to sieve `2^{key bits guessed}` candidates down to one.

**The gate that runs here.** The impossibility itself cannot be sampled directly: a
(1 active byte -> 1 active byte) 4-round transition has null probability `2^-120` and no
machine samples that. **The runnable substitute is to verify the two deterministic halves
and the middle contradiction separately** - each is a probability-1 statement over a coset
and each is exhaustively checkable on `2^24` texts in under a second - and then to measure
the *sievable* form: over a full diagonal coset at `r = 4`, count pairs whose difference
lies in the impossible set of density `2^-32`, where the null predicts about `2^15` hits and
the property predicts **exactly 0**. That is a huge, unambiguous effect and it **reuses
GATE-RR78-1's machinery byte for byte**. See GATE-RR78-4.

### 4.3 O-E - Demirci-Selcuk, where the table size is what binds

Per §2 the matching object is **not** the 255-byte sequence (not lossy, hence not an
object); it is the **parameter tuple** the sequence factors through. The attack is a
meet-in-the-middle over a precomputed table indexed by that tuple, so:

> **The binding cost is `2^{8p}` where `p` is the number of byte-parameters, and the family
> reaches exactly as deep as `8p` stays below the key size.**

Everything else - data, the online phase, the matching cost - is secondary. That is why the
family caps where it does and why differential enumeration (which *constrains* the parameter
tuple rather than the sequence) is the only lever that has ever moved it. Recall that the
4-round `p` is around 25 before enumeration and around 16 after is
**UNVERIFIED-FROM-MEMORY, recall confidence LOW**, and is used for neither promotion nor
dismissal.

**The gate that runs here, and it is a real one.** `p` is **exactly measurable** without any
literature: fix a delta-set and a target output byte, then for each candidate parameter byte
independently vary it and test whether the output difference sequence changes. A parameter
the sequence does not depend on is not a parameter. **This measures the true support, and a
support strictly below the structural count is a genuine finding that shrinks the table and
deepens the family's reach.** Cost: `256 x (candidates) x (trials)` AES calls - seconds.
Null object: the same wiring with independent random round keys, where the support should be
the full structural count. See GATE-RR78-5.

---

## 5. The gates, and what is inadmissible

**Machine envelope.** 4 cores, 15 GB, gcc with `-maes`, `7.5e7` AES/s/core (the campaign's
own `throughput_receipt.json` figure), python3, pycryptodome, **no numpy, no sage, no MILP,
no SAT**. Aggregate reach about `2^28.2` AES/s.

**Inadmissible here, stated plainly.** Any gate whose decision procedure is a MILP or SAT
solve is **not admissible on this machine**, and I do not propose one. That rules out, as
*gates*: automated search for the longest impossible differential, automated division-property
propagation for the exact integral bound, and automated bounding of the number of active
S-boxes. **The runnable substitutes I do propose:**

| solver task | inadmissible because | runnable substitute proposed here |
|---|---|---|
| MILP search for longest integral / division property | needs an ILP solver | **direct measurement**: GATE-RR78-1's `r`-sweep decides survival empirically at `2^24`-`2^32` texts, which is what the MILP would only predict |
| SAT/MILP search for impossible differentials | needs a solver | **GATE-RR78-4**: verify the two deterministic halves exhaustively over a coset and measure the sievable count against a `2^-32` null |
| MILP bound on active S-boxes | needs a solver | **exhaustive small-case enumeration**: the branch number and the DDT/LAT maxima of the pinned S-box and MixColumns are computable by brute force over `2^16` in seconds, and the 4-round 25-S-box count follows from them by hand |
| Groebner / first-fall degree | declared out of envelope by `baseline_map.md` §7(iv) | not proposed; left out of envelope rather than estimated |

The five gates are specified with full parameters, controls, memory and runtime in
`candidate_report.yaml`. In summary:

| gate | object | cost | memory | decides |
|---|---|---|---|---|
| **GATE-RR78-1** | O-A mixed-space residue | stage 1 ~0.2 s/trial; stage 2 ~53 s/core + 4 GB | 128 MB / 4 GB | depth of a deterministic 5-round signature, **and the 6-round question at zero marginal cost** |
| **GATE-RR78-2** | O-B yoyo zero-difference pattern | seconds | negligible | depth of an adaptive two-directional object, never measured in this program |
| **GATE-RR78-3** | O-C partial-sum register | minutes | < 1 GB | the *measured* cost ratio of the bottom extension, replacing §4.1's derived `2^22` with a number |
| **GATE-RR78-4** | O-D truncated support | shares GATE-RR78-1's sweep | 4 GB | whether the sievable impossible count is 0 against a `2^15` null |
| **GATE-RR78-5** | O-E parameter tuple | seconds | negligible | the true parameter support `p`, hence the true table size |

Every gate carries: a **null object of the same shape**, a **stated detection floor**, an
**artifact tell** (a quantity that fails to decay when rounds increase), and a
**pre-registered interpretation for every outcome including the uninformative one**. No gate
below has only one possible outcome.

---

## 6. Honest accounting for this session

Reproduced in machine-readable form at the foot of `candidate_report.yaml`.

- **Objects considered:** 6 tracked (O-A..O-F), 2 dropped at the lossy-projection test
  before any experiment (the 255-byte delta-set sequence; the full mixture-quadruple
  ciphertext difference), 5 promoted to candidates with gates, 0 lanes closed.
- **Compute run:** **zero**. No measurement was taken this session.
- **`dominated_by`:** **unresolvable in this environment**, written *instead of* `null`,
  because `null` would assert a row-by-row Pareto check across the published frontier that
  **cannot be performed here** - no primary source is reachable and every recalled frontier
  row in `baseline_map.md` §2 is unverified-from-memory. Writing `null` would be a
  fabrication under `AGENTS.md` rule 5. **Against the one adjudicable reference** -
  definitional exhaustive key search on the full cipher - checked axis by axis: nothing here
  claims an attack, so the reference dominates every item on **time**; every gate uses
  between negligible memory and 4 GB against the reference's `O(1)`, so every gate is
  **dominated on memory**; every gate uses **0 oracle queries** (all encryptions are offline
  and self-chosen), so nothing here is dominated on data.
- **`sota_delta`:** **0 bits.** This session produces no attack, no distinguisher, no
  speedup, and no measurement. Its quantitative content is: one derived partial-sums cost
  ladder (`2^72 -> ~2^50` per structure, §4.1, derived here and attackable), one object
  relabelling that makes the DS-MITM binding cost visible (§2, §4.3), and five specified
  gates with nulls and pre-registered readings.
- **Closures enumerated:** **none at the §4 standard.** One *difficulty* is named without an
  obstruction argument - that three mixing layers defeat every support-based projection I
  can construct (§3.3) - and its honest status is recorded as `unverified`, explicitly not
  as a closure of the 6-round question.
- **`DEFERRED_UNBOUNDED`, kept out of every count of rulings:** the `d=4, t=1, b=2` 7-round
  integral shape (§4.1); the extension arithmetic for O-B and O-D beyond the depths their
  gates measure.
- **Open directions for the next session:** (i) if GATE-RR78-1 returns a residue at
  `r = 5`, the immediate follow-on is the *magnitude* readout (`n_r` against its expectation)
  rather than the residue, since magnitude is what an attack consumes; (ii) the backward /
  decryption-direction integral depth, which `depth_wall_receipt.json` names as never run and
  which costs 53 s; (iii) integral depth for AES-192 and AES-256, whose conclusions are
  currently carried over from AES-128; (iv) whether the mixture object of MEAS-RT-C has a
  *non*-collision readout with power, which its own scope limit says is untested.

---

## 7. Non-claims - read this before citing

- **No claim about AES security of any kind, at any round count.** No distinguisher exists
  here, none is asserted to exist, and none was measured.
- **No impossibility claim and no barrier statement.** No lane is closed. The 6-round
  question is recorded `unverified`, not answered.
- **No evidence strength is assigned, no hypothesis status is changed, no ledger record is
  written, nothing is committed.** Those are the Coordinator's authority alone.
- **No literature figure is used to promote or to dismiss any candidate.** Every recalled
  fact carries an `UNVERIFIED-FROM-MEMORY` tag with a recall confidence. **No primary source
  is reachable in this environment and no citation implying one was read appears anywhere in
  this file.**
- **Every gate is a proposal.** No gate outcome is reported, predicted-as-observed, or
  implied. Reporting an imagined outcome is the Idea Generator's first prohibition.
- **Toy scale is toy scale.** Every gate here is `claim_tier: toy` under
  `docs/claims-and-verification.md` and would remain so however it returns.
