# AES campaign: publication-candidate assessment

Written 2026-08-02 by the dispatching session. Every claim below was **measured
or derived in this repository** and is reproducible from committed artifacts.

**The binding constraint on this whole document:** no primary source is
reachable from this environment (eprint.iacr.org, csrc.nist.gov, arxiv.org all
blocked). Novelty therefore cannot be adjudicated here **in either direction** —
I may not claim a result is new, and equally may not dismiss one as known.
Where I hold an unverified recollection, it is labelled as exactly that. Each
entry names the single check that would settle it.

---

## Tier 1 — plausibly novel, and cheap to check

### 1. The 5-round adaptive effect is *strictly all-or-nothing*
**Measured.** A graded statistic ("some plaintext word has ≥ k zero-difference
bytes") reads AES/PRP ratios of **0.9999, 0.9998, 0.9951** at k = 1, 2, 3 — and
**20.0** at k = 4. The effect leaks into no partial-zero event, to 0.05% at the
byte level and 0.64% at the two-byte level.

**Why it may matter:** the distinguisher itself is very likely known (see Tier
3), but this is a statement about its *internal structure*, not its existence.
It says the property is a strict 32-bit coincidence with no graded shadow — which
is what forecloses any cheaper statistic, and therefore bounds how efficient any
distinguisher of this family can be.

**Check:** does any published treatment give the graded/partial-zero profile
rather than only the all-zero rate? If not, this is a new structural fact about a
known object.
**Artifacts:** `coordination/goals/GOAL-AES-003/batches/BATCH-001/tasks/yoyo6/power.jsonl`

### 2. Iteration provably cannot amplify this object past r=4
**Measured, with a derived component I verified independently.** The A-step is an
**exact involution** — applying it twice with the same mask is the identity
(2000/2000 trials, r=1..10, `DISPATCHER-involution-check.c`). So naive iteration
has period 2 and carries zero information. Under an alternating two-mask yoyo,
zero-difference structure is preserved at **100% through 8 generations at r ≤ 4**
and drops to exactly the unconditional rate at r = 5, with the positive control
proving the instrument would have detected preservation had it existed.

**Why it may matter:** it converts "iteration didn't help" into "iteration cannot
help, and here is the round at which preservation fails."

**Check:** is the involution and the r=5 preservation failure stated anywhere?
**Artifacts:** `.../yoyo6/` (`pc2.jsonl`, `pc4.jsonl`, `iter5_aes.json`, `r5_corr.json`)

### 3. The excess grows in the active-byte count and fits NEITHER natural law
**Measured, and now resolved — the check flagged here has been run.** Three
independent runs (seeds 20260802 / 777333111 / 424242424; N = 2^30, 2^32, 2^34),
combined:

| k | events | null | ratio | ± | rel. to k=1 |
|---|---|---|---|---|---|
| 1 | 29 | 21 | 1.38 | 0.26 | 1.00 |
| 2 | 116 | 21 | 5.52 | 0.51 | 4.00 |
| 3 | 59 | 5 | 11.80 | 1.54 | 8.54 |
| 4 | 68 | 5 | 13.60 | 1.65 | 9.85 |

Observed (normalised) **1, 4.0, 8.6, 9.9** against k² (1,4,9,16) and 2^k
(1,2,4,8). At the discriminating point k=1 the data **disfavour 2^k** (z = −2.01)
and sit high of k² (z = +1.75). But at k=2 *both* laws predict 4.0 and the data
read 5.52, and growth **saturates** from k=3 to k=4 (11.8 → 13.6), which neither
law does.

**Result: neither candidate law describes the data across the range.** The
producer's post-hoc 2^k DDT explanation is disfavoured; no replacement is
asserted. The growth is sub-exponential and saturating, which is a genuine
measured constraint on any mechanism proposed for this effect.

**Check:** does any published treatment give the active-byte-count dependence
at all? This is a structural profile, not a rate.
**Artifacts:** `.../yoyo5/DISPATCHER-MECHANISM.json`, `DISPATCHER-mechanism-probe.c`

---

## Tier 2 — solid, useful, probably not publishable alone

- **Certified 5-round AES-128 key recovery**, full unrestricted 2^128 key space,
  ~26 s, verified on a randomly chosen key with a certificate under an
  independent implementation. Standard integral/square technique — near-certainly
  a rediscovery.
- **Certified 7-round key recovery on a 4-bit-cell analogue** (MINI-AES-64), full
  2^64 key space, replicated. **Provably does not transfer**: the 5-round balance
  it rests on exists only because the 4-bit S-box has degree 3 (27 < 32); AES's
  degree-7 S-box gives 343 > 128, so no chosen-plaintext set in a 128-bit block
  can supply it. Verified independently.
- **Tightened r=6 null**: 95% upper limit 1.79× single-config, 1.36× pooled.
- **Depth wall measured from scratch**: integral exact through r=4, dead at r=5.

## Tier 3 — measured, but I believe already known

- **The 5-round adaptive distinguisher itself.** Unverified recollection: a
  yoyo-type 5-round AES distinguisher exists in the literature and is *far* more
  data-efficient than this readout (ours needs ~2^28.25 trials to reach p<2^-20;
  I recall published versions using a few thousand adaptive queries). **This
  recollection may not be used to dismiss the measurement in the research record
  — it is recorded here because the user asked specifically about publishability.**

## Tier 4 — negative results, correctly scoped

- Algebraic lane does not reach 2^128 on **either** criterion (2^434–2^859).
- No exact MITM factorization exists at 10/12/14 rounds.
- O-3's premise is **measurably false**; its conclusion survives on
  state-distinctness grounds, so the 7.64-bit figure may not be cited as its
  justification.
- Sharing across structured key sets is **byte-local only**.

---

## The one action that unblocks everything

**Vendor the relevant primary sources into `inputs/` with recorded provenance.**
Every "unadjudicable" above becomes a decidable question in a single step. Tier 1
item 1 is the most likely to survive that check, because it is a structural
property of a known object rather than the object itself.

## Honest bottom line

**No result here is confirmed publication-worthy.** Tier 1 contains three
candidates whose novelty is genuinely open and none of which I can settle. The
strongest non-AES candidate in the corpus is `KN-FIND-029` — five distinct ways
an automated verification harness reports success on demonstrably broken code,
each found only by looking, three of them *inside the repair for the previous
one*. That is a methodological finding about automated research systems, and it
is the one thing here I have no recollection of being covered.
