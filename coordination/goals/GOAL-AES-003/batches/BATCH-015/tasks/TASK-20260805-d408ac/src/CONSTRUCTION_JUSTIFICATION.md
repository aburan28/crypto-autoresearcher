# CONSTRUCTION_JUSTIFICATION — TASK-20260805-d408ac (BATCH-015)

Why the chosen construction (16-round balanced Feistel on two 64-bit halves,
SipRound-based round function, FRESH random 128-bit key per trial) is
expected to approximate a uniform random permutation closely enough at the
target exposure (2^30-2^33 trials). Per the task card and this campaign's
claim-tier discipline: this names a specific argument and its evaluation; it
does NOT claim indistinguishability from ideal as an established fact.

## 0. Citation provenance

Per AGENTS.md rule 9, every external citation below carries provenance
**`recalled`**: it comes from the executing model's own knowledge; no agent
in this program has opened these works during this task. They are pointers
for a reviewer, not support that has been checked here.

- Luby & Rackoff, "How to construct pseudorandom permutations from
  pseudorandom functions", SIAM Journal on Computing, 1988. (`recalled`)
- Patarin, "Improved proofs of security for the generalized Feistel network",
  ASIACRYPT 2008 (and the earlier CRYPTO 1993 / Eurocrypt 1996 line on
  concrete bounds for Feistel schemes). (`recalled`)
- Aumasson & Bernstein, "SipHash: a fast short-input PRF", INDOCRYPT 2012
  (SipRound definition; SipHash-2-4 PRF design and security goal).
  (`recalled`)
- Garwood, "Fiducial limits for the Poisson distribution", Biometrika, 1936
  (exact Poisson CI used in the analysis). (`recalled`)
- Internal (checked, in-repo): EV-AES-e4c091 (perm128's per-trial exact
  conditional law for the 4 oracle queries and its cross-trial birthday
  bound 2^-56), EV-AES-837cd8 (perm128 memory ceiling), BATCH-014
  rc8probe_feistel.c (RC-D, the construction this one must DIFFER from).

## 1. The argument, step by step

### 1.1 Structural bijectivity (derived, trivial)

Any balanced Feistel ladder is a bijection for ANY round function: each round
`(L,R) -> (R, L xor F(R, k_i))` is invertible given k_i, and decryption runs
the rounds backwards with the same F. So every per-trial key K yields a
genuine PERMUTATION on 128 bits, evaluated directly (O(1) memory per query),
with exact algebraic inversion — matching perm128's bijection semantics with
no injectivity bookkeeping and no stored table. Verified mechanically:
runs/SELFCHECK.json `ff_gate` (round-trip + 2-point injectivity under 4096
fresh keys, 0 failures) and the per-arm fresh-key gate before each
measurement arm.

### 1.2 The regime that matters: 4 queries per permutation instance

This is the load-bearing observation for the exposure question. Because the
key is RESAMPLED EVERY TRIAL, each trial consumes exactly FOUR oracle
queries (2 forward: enc(p0), enc(p1); 2 inverse: dec of the two swapped
ciphertexts) against ONE permutation instance, then discards it. The
2^30-2^33 exposure is a count of INDEPENDENT permutation draws, not an
accumulation of queries against a single permutation. Any
idealness-of-the-construction bound therefore enters PER TRIAL, at q = 4,
and the arm-level quantity is a union bound over independent trials — not a
birthday accumulation in q.

### 1.3 Round-count justification: Luby-Rackoff floor, Patarin-type concrete bound

Named argument (all `recalled`): for a balanced Feistel network on 2n bits
whose round functions are INDEPENDENT UNIFORM RANDOM functions:

- 3 rounds suffice for PRP (CPA) security; 4 rounds suffice for STRONG PRP
  (SPRP) security — the Luby-Rackoff theorem. Strong security is the
  relevant notion here because each trial's transcript includes INVERSE
  queries (the two decryptions), i.e. the distinguisher gets
  chosen-ciphertext access to the instance.
- Concrete bounds of the Patarin type bound the distinguishing advantage of
  any q-query adversary (adaptive, both directions) against a uniform random
  permutation, for 4 or more rounds, by a low-degree polynomial in q divided
  by 2^{2n} (the leading term is of order q^4/2^{2n} for balanced networks;
  we state the order, not a constant, since the exact constant is recalled
  and unchecked).

Evaluation at THIS task's parameters: q = 4 queries per instance, n = 64.
Per-trial advantage <= on the order of 4^4 / 2^128 = 2^-120. Union bound
over at most 2^33 independent trials: total deviation from the ideal
4-query transcript law <= on the order of 2^9 x 2^-120 = 2^-111 —
astronomically below any level this measurement could observe (the
statistic's own Monte-Carlo noise at 2^33 is ~sqrt(8)/8 ≈ 0.35 relative on
an ~8-event count). The round-count floor for the needed security notion is
4; FF_ROUNDS = 16 leaves a 4x margin and matches RC-D's geometry so the two
constructions differ in SEMANTICS (fresh vs fixed key) and ROUND FUNCTION
(SipRound vs fmix64), not in network size.

### 1.4 What is assumed, not proven, about the round function

The 1.3 bound is stated for IDEAL random round functions. The actual round
functions here are a keyed family built from SipRound (two compression
rounds of the SipHash-2-4 core, initialized from (x, k) with SipHash's
public IV constants and finalized by the four-word xor — `recalled`:
SipRound is the ARX core of a published, cryptographically analyzed
short-input PRF, and SipHash's design goal is PRF security). The step
"keyed SipRound family ~ random function family" is the standard
Luby-Rackoff reduction heuristic. It is a WORKING ASSUMPTION of this
toy-scale construction, NOT a theorem we establish, for two honest reasons:
(a) proving the SipRound family PRF-secure at concrete parameters is far
beyond this task; (b) at q = 4 queries per instance, even a much weaker
randomness property of F would already suffice, and the empirical battery
below probes the observable consequences directly.

### 1.5 Support-size caveat (why "transcript-level" is the honest claim)

The family has 128-bit keys, hence at most 2^128 distinct permutations,
versus (2^128)! total. The induced distribution is therefore NOT
statistically close to uniform over the full symmetric group — no keyed
128-bit family can be. The claim made here, and the one the statistic
consumes, is TRANSCRIPT-LEVEL closeness: for each trial, the joint law of
the 4-query transcript under a uniform key is close to the corresponding
law under a uniform random permutation, with the per-trial bound of 1.3.
This is exactly the level at which perm128 served in BATCH-009: EV-AES-e4c091
OBS-B9-2 records that perm128 realized "the exact conditional law of a
uniform random bijection given the four oracle queries per trial", with
cross-trial consistency bounded only by a birthday bound (2^-56 at <= 2^36
queries). The fresh-key Feistel matches that per-trial-transcript semantics
with direct evaluation instead of lazy sampling — which is precisely the
substitution this batch exists to make.

## 2. Empirical sanity battery (run 1, gates, not proof)

From runs/SELFCHECK.json (all gates passed before any measurement arm):

- `ff_gate`: round-trip inversion and 2-point injectivity under 4096 fresh
  keys — 0 failures (a fresh permutation per trial must be a bijection).
- `keycheck`: 4,194,304 keys drawn from the four actual per-thread key
  streams (2^20 each) are pairwise distinct — 0 duplicates; plus the
  within-thread PROOF (splitmix64 state advances by an odd constant on one
  2^64-cycle with a bijective output mix, so consecutive 128-bit key pairs
  cannot repeat within 2^64 draws >> 2^33).
- `qualcheck` (2^18 fresh-key trials, fixed inputs): output-byte histograms
  at positions {0,5,8,13} give chi-square [273.8, 269.5, 245.6, 253.3] on
  255 df (gate: < 400, i.e. no rejection at ~1e-5 level); byte-0 equality
  frequency between the two fixed inputs' ciphertexts is z = 1.16 against
  the ideal expectation N/256; zero full-128-bit output collisions (as a
  permutation must give). These are CONSISTENCY checks of the
  working assumption at observable scale; they do not and cannot establish
  idealness.
- Measurement arms additionally log the first 4 per-trial keys per thread
  and an order-sensitive digest over ALL drawn keys (runs/M1-FF-P30.json,
  runs/M2-FF-P33.json), and report the key-stream separation
  (stream_gap_min_log2_key_threads = 62, no key-stream seed equal to any
  plaintext-stream seed).

## 3. Bottom line

Working assumption, stated plainly: with a fresh 128-bit key per trial, a
16-round balanced Feistel whose round function is a keyed SipRound mix is
expected to give each trial's 4-query transcript a law within ~2^-120
(Patarin-type order bound, ideal-round-function version, evaluated at q=4,
n=64) of the uniform-random-permutation transcript law; the round-function
step is the standard Luby-Rackoff heuristic, sanity-checked empirically
above, not proven. This is a toy-scale assumption adequate to the campaign's
claim tier, and it is the CLOSEST available O(1)-memory match to perm128's
per-trial semantics. Any interpretation of the measurement belongs to the
Coordinator, not to this document.
