# YOYO-6 PRE-REGISTRATION (IMMUTABLE)

Written **before any cipher call in this session**.
Session start stamp: `2026-08-02T03:01:04Z`.
Halt boundary: start + 2700 s = `2026-08-02T03:46:04Z`.

**Frozen at the moment of writing. Never edited afterwards.** Any correction
appears as a separate `PREREG-AMENDMENT-<UTC>.md`, never as an edit here.

Role: Executor. Nothing here is a claim about AES security. `claim_tier: toy`
(reduced-round, own instrument). **No literature comparison in either
direction**; novelty is out of scope, neither claimed nor dismissed.

---

## 0. Governing-contract status

There is **no `experiments/<EXP-ID>/specification.yaml` with `status: approved`
and non-null `approved_by`** for this object. The governing input is a task
message. Under the Executor contract that is a `specification_error` for a
*ledger* experiment. This session therefore runs as an **exploratory scratchpad
probe** confined to
`/tmp/claude-0/-home-user-crypto-autoresearcher/42d1537b-7158-5124-bdad-0c8e3df17d46/scratchpad/yoyo6/`.
Nothing is written to the repo or the ledger; no `runs/<RUN-ID>/` package is
created; no evidence record is produced; nothing is committed.

Missing-from-a-formal-contract fields (reported, not repaired):
`experiment_id`, `status`, `approved_by`, `budget.memory_gb`,
`budget.maximum_runs`, `stopping_rules`, `required_artifacts`,
`certificate.kind`.

**Certificate discipline**: pure measurement run. `certificate.kind: none`, set
explicitly. No solve, no factor-base relation, no key recovery is claimed or
required.

---

## 1. Conventions, frozen (inherited, not re-derived)

Reduced-round convention (campaign-pinned):

```
E_K^r(p) = ARK_r . SR . SB . [ ARK_i . MC . SR . SB ]_{i=r-1..1} . ARK_0 (p)
```

round keys = first `r+1` of the untruncated FIPS-197 AES-128 expansion; final
round drops MixColumns; initial ARK not counted as a round. State column-major,
`state[row t][col c] = byte[4c+t]`. `D_K^r` is the exact inverse.

Word geometry (verified upstream in `DISPATCHER-REPLICATION.json`; inherited
here as a fact about the instrument, and re-checked by the `r=2` positive
control before belief):

- **Plaintext words = forward diagonals**
  `PW[j] = { 4*((j+t) mod 4) + t : t = 0..3 }`
  `PW[0]={0,5,10,15}`, `PW[1]={4,9,14,3}`, `PW[2]={8,13,2,7}`, `PW[3]={12,1,6,11}`.
- **Ciphertext words = inverse-ShiftRows diagonals**
  `CW[j] = { 4*((j-t) mod 4) + t : t = 0..3 }`
  `CW[0]={0,13,10,7}`, `CW[1]={4,1,14,11}`, `CW[2]={8,5,2,15}`, `CW[3]={12,9,6,3}`.

Getting `CW` wrong once produced a false null upstream. It is therefore
re-asserted here and guarded by V1.

---

## 2. Objects, frozen

### 2.1 Steps

- **A-step (ciphertext swap, mask `S`)**: on plaintext pair `(x0,x1)`, compute
  `c_i = E_K^r(x_i)`; exchange, for every `j in S`, the four bytes of `CW[j]`
  between `c0` and `c1`; decrypt both; output the new plaintext pair.
- **B-step (plaintext swap, mask `T`)**: on plaintext pair `(x0,x1)`, exchange,
  for every `j in T`, the four bytes of `PW[j]` between `x0` and `x1`.

Both steps preserve the XOR difference of the pair they act on (exchanging a
value block between the two members leaves `x0 XOR x1` unchanged on those
bytes). The object is therefore purely a **value-orbit** object at fixed
difference, which is why an ordinary differential readout cannot see it.

Admissible masks: `S, T` nonempty proper subsets of `{0,1,2,3}` (14 each).
`S in {empty, full}` is **degenerate by construction** (the pair maps to itself
or to its transposition), excluded, and recorded here so a maximal reading can
never be mistaken for a finding.

### 2.2 SINGLE object (the measured/replicated baseline)

Trial: draw `p0` uniform; draw `p1` equal to `p0` outside `A` and uniformly
re-randomised inside every word of `A`, rejecting any draw in which some word
of `A` has zero difference. One A-step. Record `d = p0' XOR p1'`.

### 2.3 ITERATED object (pre-registered upstream as item 6.8, NEVER RUN)

**PR-I0 (algebraic, pre-run, blocks the naive design).** Applying the A-step
twice in succession with the same mask `S` is the **identity**: the second
A-step re-encrypts to exactly `c'`, swaps `CW[j]` back, and decrypts. So the
naive "re-encrypt, swap again, decrypt again" iteration has **period 2** and
carries zero information beyond generation 1. This is asserted before running
and is **verified empirically as a pinning check** (P-4). If it does not read
as an exact involution, the instrument is broken.

The iterated object is therefore the **alternating** yoyo, which is the only
non-degenerate iteration of these two steps:

```
gen 1 :  A-step(S)                      -> record d_1
gen g :  B-step(T) then A-step(S)       -> record d_g      (g = 2..G)
```

with `G <= 8` generations as pre-registered. Default `T = S`. Because both
steps preserve the difference of their input pair, `d_g` changes only through
the encrypt/decrypt inside the A-step.

**Recorded per generation**: the full statistic set of section 3.

### 2.4 Conditional-persistence object (the amplification test)

The mechanism by which iteration can buy power *without buying data* is
**persistence**: if a generation-1 hit leaves the pair back inside the
structured input class, the next generation hits again with probability
`O(1)` instead of `2^-28`. Measured directly: every generation-1 hit found in
the main `r=5` sweep is carried forward through `G=8` generations and its
survival recorded. This costs nothing extra, since the hits are a by-product of
a sweep that must run anyway.

---

## 3. Statistics, frozen, with resolution defined

For a recorded difference `d` (16 bytes):

- `m_j = #{ t : d[i]=0, i in PW[j] }` for `j=0..3`, range 0..4.
- **G4 (the legacy indicator)**: `W = #{ j : m_j = 4 }`; event `W>=1`.
  Null `P(W>=1) = 4*2^-32 = 2^-30`.
- **G3**: event `max_j m_j >= 3`. Null `P = 4*(4*2^-24*(1-2^-8) + 2^-32)`
  `= 2^-19.9986`, i.e. `~2^-20`.
- **G2**: event `max_j m_j >= 2`. Null `P ~ 4*C(4,2)*2^-16 = 2^-11.4`.
- **G1**: event `max_j m_j >= 1`. Null `P ~ 1-(1-2^-8)^16 = 0.0607`.
- **Marginal table** `cnt[j][m]`, 4x5, full, always reported.
- `Z = #{ i : d[i]=0 }`, full 17-bin histogram (comparability with prior work).
- **Zero-word identity distribution**: which `j` attains `m_j=4`.
- **Iteration statistics**: per-generation `G1..G4` counts; **first-repeat
  index** (smallest `g2>g1` with the pair state repeating); **survival curve**
  `P(hit at gen g | hit at gen 1)`.

**Exact null probabilities are computed from the binomial before any run and
frozen in `NULL_PROBS.json`.**

### Resolution, two notions, both reported per arm

- **(R-rare)** For a rare-event indicator: the smallest per-trial probability
  detected with >=95% probability at `N` trials is `3/N`; resolution in bits is
  `log2(N/3)`.
- **(R-rel)** For a common event of null probability `q`: the smallest
  *relative* excess detected at 95% is `eps = 4/sqrt(N*q)`; reported as
  "detects a `100*eps`% excess on a `2^-x` event at `N=2^y`", together with the
  equivalent-bit figure `log2(N*q)/1` expressed as `log2(1/eps^2 ... )` is NOT
  used; only `eps` and `N*q` are reported, to avoid inventing a bit scale.

An arm whose resolution does not cover the null probability of the event it
reports is labelled **underpowered on the same line as the number**.

### Discriminating-power gate (checked, not assumed)

A statistic is admitted only if, at `r=2`, it separates AES from the PRP
control by many orders of magnitude. A statistic returning AES and PRP readings
within its own resolution is declared **non-discriminating** and its arm
carries no information. (This campaign has been bitten by a statistic reading
0.4995 vs 0.4996.)

---

## 4. Pre-registered predictions (frozen; never adjusted, never re-scored)

- **PR-0 (pinning).** The C AES-NI path and pycryptodome agree bit-for-bit at
  every round count used, in **both** directions, on the FIPS-197 KAT and on
  random vectors; `D_K^r(E_K^r(x)) = x` for all tested `x`, `r`.
- **PR-1 (positive control, deterministic).** At `r=2`, `A={0}`, any admissible
  `S`: `W=3` in **100%** of trials, at **every** generation of the iterated
  object. (Two-round AES is four parallel independent bijections in word
  coordinates, so the zero-difference word pattern is exactly preserved by both
  step types.) A single failure fires V1.
- **PR-2 (instrument sanity at r=4).** The upstream sweep read `r=4` as
  deterministic preservation. Reproduced here as a second positive control.
- **PR-3 (r=5 known signal).** At `r=5`, `A={0}`, `S={0}`, the G4 rate exceeds
  the `2^-30` null by a factor in the range measured upstream (12x-17.5x). If
  this session's instrument does not see it, **every r=6 null in this session
  is VOID** (V1b). This is the positive control that licenses all r=6 reporting.
- **PR-4 (the power question — the reason this session exists).** *If* the
  r=5 effect is a graded confinement of the word difference, then the cheaper
  events G3 and G2 also carry excess at `r=5`, and can be measured at
  `N << 2^32`. *If* the effect is strictly all-or-nothing, G2 and G3 read null
  at r=5 and **no cheap statistic exists**; in that case the correct action is
  to say so and stop rather than burn budget at r=6. Both outcomes are
  pre-registered as informative. The decision threshold: G2/G3 are admitted as
  the r=6 statistic **only if** they show a departure at r=5 exceeding their
  own R-rel resolution by >=5 sigma at `N <= 2^28`.
- **PR-5 (iteration).** *If* the object is a genuine invariant, then
  `P(hit at gen 2 | hit at gen 1) >> 2^-28` at `r=5` (persistence), the
  per-generation G4 rate is flat or rising in `g`, and the r=5 hit pairs have
  `W=3` (structure restored). *If* iteration is empty, the generation-1 hit
  leaves an unstructured pair (`W=1`, all other words active) and generations
  `>=2` read at the PRP rate. Both outcomes are pre-registered.
- **PR-6 (r=6).** The frozen claim under test: at `r=6` the AES arm agrees with
  the PRP arm within the achieved resolution. Its negation is the finding. The
  falsifiable content is **the exact largest r at which the AES arm departs
  from the PRP arm by more than the resolution**, and the **bound achieved at
  r=6** stated in bits.
- **PR-7 (decay / artifact tell).** At `r=10` the AES arm must read as the PRP
  arm. A signal flat across round counts, in particular present at `r=10`, is
  the canonical instrument fault, fires V4, and is not a finding.
- **PR-8 (monotone death).** Excess over the null is expected non-increasing in
  `r`. A non-monotone reading (dead at r, alive at r+1) is reported as an
  anomaly and treated as suspect, never as a finding.

### Decision rule, frozen

For each arm `(r, A, S, T, G)` report: `N`; the full `cnt[j][m]` table; the
full 17-bin `Z` histogram; G1..G4 counts with exact binomial/Poisson null
tails; the matched PRP arm at identical `N`, identical `G`, identical code
path; the resolution (R-rare and R-rel); and the Bonferroni factor = number of
arms tested, recorded explicitly.

"**Alive at r**" requires all three: (i) null probability of the AES reading
below `2^-20` **after** Bonferroni multiplication; (ii) the matched PRP arm
does not show it; (iii) the reading is not flat across rounds. No other
statistic may be substituted after the fact. Any statistic not listed in
section 3 is exploratory and is reported as exploratory.

---

## 5. VOID conditions

If any fires, the affected readings are **VOID**, classified
`invalid_measurement`, and are **never** reported as a negative observation.

- **V1**: PR-1 fails (`r=2` does not read `W=3` in 100% of trials, any
  generation). Instrument broken; execution stops. *Checked first.*
- **V1b**: PR-3 fails (this session cannot see the known r=5 signal). All r=6
  readings in this session are VOID.
- **V2**: any cross-implementation disagreement, either direction, any `r`.
- **V3**: `D_K^r(E_K^r(x)) != x` for any tested `x`, `r`.
- **V4**: the AES excess is flat across `r` including `r=10` (artifact tell).
- **V5**: the PRP control departs from its own exact null by more than its
  resolution. Then the harness, not the cipher, makes the reading, and every
  AES reading in the session is uninterpretable.
- **V6**: degenerate trial construction — `p0=p1`; `S` or `T` empty or full; a
  word of `A` with zero difference; **trivial (no-op) swap**, i.e. the swapped
  ciphertext words already equal, which upstream produced a spurious `W=3`.
  Counted separately in every arm; a nonzero *uncounted* occurrence voids it.
- **V7**: the PR-I0 involution check fails.
- **V8**: wall-clock halt at `2026-08-02T03:46:04Z`. Runs not started are
  reported as not run. **A budget halt is never reported as a null and never as
  evidence about AES.**

---

## 6. Planned run grid (priority order, executed top-down until halt)

1. **PIN** — C AES-NI vs pycryptodome, both directions, FIPS-197 KAT + random,
   `r=1..10`; round-trip; involution check PR-I0. Blocks everything.
2. **PC2** — PR-1 at `r=2`, `A={0}`, all 14 admissible `S`, `G=8`, `N>=10^4`.
3. **PC4** — PR-2 at `r=4`, same shape.
4. **PRP control** — matched `N`, matched `G`, `A={0}`, `S={0}`, and at the `N`
   of every AES arm reported.
5. **POWER PROBE at r=5** (PR-4) — G1/G2/G3 profile at `N=2^24..2^28`, AES vs
   PRP, `A={0}`, `S={0}`. Gate for everything below.
6. **r=5 iterated** (PR-5) — `G=8`, persistence and survival curve, plus the
   `W` of every hit pair.
7. **r=6** with whatever survived step 5, at the best `N` the budget buys.
8. **Swap-mask sweep** — all 14 admissible `S` at `r=5` then `r=6`.
9. **Active-mask sweep** — `A in {{0},{0,1},{0,1,2}}`, plus `A={0,1,2,3}` as
   the structure-destroying control.
10. **r=10** decay check (PR-7).

Achieved `N` is budget-limited; any shortfall is reported as achieved
resolution, not smoothed over.

---

## 7. Sources of randomness, frozen

Master seed **`20260803`** (distinct from the upstream `20260802`, so this is a
fresh-seed replication, not a re-read of the same stream). All keys, plaintexts
and per-trial randomness come from a documented deterministic `splitmix64`
stream seeded from `(master_seed, arm_index, thread_index)`; every arm records
its exact seed. No `rand()`, no `xorshift64` (prior-campaign confounder).
**Any run reported as a signal is repeated with a different master seed and a
different key before it is reported at all.**

---

## 8. What this session may not do

- May not conclude that a heuristic is validated or refuted.
- May not declare a hypothesis supported, rejected, or closed.
- May not assess novelty, in either direction.
- May not infer anything about full-round or deployed AES.
- May not report a budget halt or an infrastructure failure as mathematical
  evidence.
- May not substitute a post-hoc statistic for a pre-registered one.
