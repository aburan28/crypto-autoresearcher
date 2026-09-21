# TASK-20260802-018 independent theorem applicability audit

**Verdict: `REVISE`.** The committed producer's bounded zero-survivor direction
is correct, but the package is not accurate enough to archive unchanged. The
material defect is `B22-T03`: Fiat–Naor/Hellman inversion is transformed into
`S*T≈N` with a balanced `N^1/2` point, while the cited function-inversion
results give a different tradeoff. Three smaller exactness and scope defects
also need correction in the Cheon, Diem, and Koutis rows.

After those corrections, the admissible survivor count remains zero. No
canonical ID, experiment, status transition, closure result, or breakthrough is
warranted. This review covers only `B22-T01..T04`.

## Committed-byte binding

Snapshot `4505c1d4da9ab154a357dec5f1b45eb756c16f82` is reachable
from review `HEAD` `5b10347a8c2b19db6d136cf4d80f3a16c4a57fca` and
has the sole parent `8cdbb4aed480ee5fae8eec5cac3207d3b8e7d7d4`.
The snapshot adds exactly three paths:

| Committed path | SHA-256 of `git show COMMIT:path` bytes |
|---|---|
| `.../TASK-20260802-016/ingredient_scout.yaml` | `28b27e272385582f75dee5acf602178a5c2f51eb96940223b9e10716a3b428cf` |
| `.../TASK-20260802-016/literature_map.md` | `c8b047d2e828792bb175ba8eb1101a0031c6534c200ee8e8eed8bb3e868c0d3c` |
| `.../TASK-20260802-017/snapshot_commit_receipt.json` | `c49b88830c534d398781c63ed9bd49f0ae027c50fcf82f96c15d709dcf5f4125` |

The receipt's internal `commit_sha: null` and empty `path_sha256` delegate the
post-commit binding to `dispatch_queue.json`. The queue records the same commit,
parent, paths, and hashes. This audit reviewed the producer bytes from the Git
object, never mutable working-tree copies.

## Primary-source result

| Handle | Source reopened | Independent theorem finding | Standard prime-field disposition |
|---|---|---|---|
| `B22-T01` | Cheon, [*Discrete Logarithm Problems with Auxiliary Inputs*](https://www.math.snu.ac.kr/~jhcheon/publications/2010/StrongDH_JoC_Final2.pdf), Theorems 1 and 2 and the setup discussion | The auxiliary-input complexities and storage are substantially quoted correctly. The deterministic scalar-field generator/factorization setup is not merely polylogarithmic once `d` is known. | Reject: `[k^d]P` or the `2d` auxiliary powers are target-dependent nonlinear inputs absent from standard ECDLP. |
| `B22-T02` | Diem, [*On the discrete logarithm problem in elliptic curves*](https://www.math.uni-leipzig.de/~diem/preprints/dlp-ell-curves.pdf), main theorem and Sections 1–2 | The main theorem is expected time `exp(O(max(log q,n^2)))`. The producer states the derived `(q_i^n_i)^o(1)` growing-`n` sequence result accurately but labels it the main theorem. | Reject: at `F_p`, `n=1`; the proper-subfield factor-base geometry and growing-`n` consequence disappear. |
| `B22-T03` | Fiat–Naor, [*Rigorous Time/Space Trade-offs for Inverting Functions*](https://doi.org/10.1137/S0097539795280512), and Hellman, [*A Cryptanalytic Time–Memory Trade-Off*](https://ee.stanford.edu/~hellman/publications/36.pdf) | Fiat–Naor gives `T*S^2=N^3*q(f)` and `T*S^3=N^3`. For a permutation `q(f)=1/N`, so `T*S^2=N^2`, balanced at `N^(2/3)`. Hellman's generic construction also balances at `N^(2/3)` after `N` preprocessing. | Reject after material correction: the cited theorem is costlier than reported and `a -> encode([a]P)` is not an iterable endofunction until a reduction/interface is supplied and charged. |
| `B22-T04` | Koutis, [*Faster algebraic algorithms for path and packing problems*](https://www.cs.cmu.edu/~jkoutis/papers/MultilinearDetection.pdf), Theorems 2.4 and 2.5 | Odd-coefficient degree-`k` square-free detection has one-sided constant success; a supplied modulo-`2^(k+1)` circuit costs `O((nk+t)2^k)` time and `O(nk+s)` space. It is a detector, not a circuit constructor or witness theorem. | Reject: the exact all-strata elliptic source circuit, parity isolation, witness recovery, rank, logs, and blind descent remain missing. |

The lower-bound use is appropriately scoped. Shoup's
[generic lower bound](https://www.shoup.net/papers/dlbounds1.pdf) is a strict
generic-model control, not a universal obstruction against public encodings.
Corrigan-Gibbs–Henzinger–Wu's official
[structured generic-group record](https://eprint.iacr.org/2026/384) states
`Omega(min(sqrt(N),1/delta))` only inside its defined oracle model. None of the
four rows specifies that oracle and computes `delta`, so this result cannot be
used as a turnkey rejection.

## `B22-T01` — Cheon auxiliary inputs

Cheon's Theorem 1 takes a prime-order abelian group, `d | (N-1)`, and
`P,[k]P,[k^d]P`. It deterministically recovers `k` in

```text
O(sqrt((N-1)/d) + sqrt(d))
```

group exponentiations with the corresponding maximum table storage. Theorem 2
takes `d | (N+1)`, powers through `2d`, and ERH for deterministic setup. Thus
the producer correctly identifies the useful object and the fatal standard-input
gap.

The correction is in setup accounting. Cheon's proof needs a generator of the
scalar-field multiplicative group; the paper discusses a deterministic
`N^(1/4+o(1))` scale given factorization and a heuristic `N^1/4` factorization
route. The producer's `polynomial/logarithmic arithmetic once d is known` is
not a complete description. Favorable divisor existence must also be stated as
an input-family condition. At the favorable `d=N^(1/2+o(1))` point, the setup
does not change the quarter-exponent conditional core, but it must be charged.

The complete standard path still fails before that core:

```text
construct(P,[k]P -> [k^d]P) + Cheon recovery + verify [k]P=Q.
```

Ordinary generic operations retain affine scalar labels and do not produce the
nonlinear auxiliary point. This is directly occupied by `ECDLP-IDEA-003` and
`008`. The random-auxiliary negative control, exact equality check, and audit
for `k`, DLP/CDH, pairing return, or target advice are appropriate. Supported
SOTA delta remains zero.

## `B22-T02` — Diem extension-field index calculus

Diem's exact main theorem is stronger and more precise than the row says:

```text
expected time = exp(O(max(log(q), n^2))) for E/F_(q^n).
```

The paper then derives `(q_i^n_i)^o(1)` when `n_i -> infinity` and
`n_i/log(q_i) -> 0`. The producer quotes that consequence correctly but calls
it the main theorem. The degree-two cover and its condition are part of the
algorithm's construction, not simply an external input hypothesis.

The native mechanism is real: the proper subfield defines an algebraic factor
base, the decomposition algorithm returns sources, and the index-calculus route
includes relations and individual logarithms. None of that yields the target
prime-field result. At `F_p`, `n=1`, the factor-base condition collapses and
the growing-degree consequence does not apply. Embedding `E(F_p)` into
`E(F_(p^n))` changes the ambient problem and gives no original-`N` bound below
rho for setup, decomposition probability, independent rank, factor logs, or
blind descent.

The row should therefore distinguish the main theorem from the sequence result
and mark prime-field memory/data/rank/log/descent bounds as uninstantiated,
rather than saying they are absorbed into an applicable target theorem. The
named obstruction, `n=1` control, zero SOTA delta, and forward search for a
directly prime-field subset are sound.

## `B22-T03` — Fiat–Naor/Hellman inversion

This row requires material correction. Fiat–Naor states

```text
T*S^2 = N^3*q(f),
T*S^3 = N^3  for the all-function/all-point guarantee.
```

For a permutation, `q(f)=1/N`, hence

```text
T*S^2 = N^2.
```

Writing `S=N^sigma` gives `T=N^(2-2*sigma)`, with balanced
`T=S=N^(2/3)`. Hellman's original generic cryptanalytic construction likewise
uses `N` preprocessing and balances online time and memory at `N^(2/3)` for a
random-function model. The stronger `T*M=N`, balanced `N^(1/2)` relation is
the structure-specific DLP/BSGS frontier mentioned in Hellman's introduction;
it is not the cited Hellman/Fiat–Naor function-inversion upper bound.

There is also a type error. A canonical injective point encoding does not make

```text
f(a) = encode([a]P)
```

an iterable endofunction on `[N]`. Hellman's method specifies a public reduction
from output encodings back to the input domain and applies it to the challenge.
For ECDLP, the reduction, collisions, coverage, false alarms, chain replay, and
final `[a]P=Q` verification must all be explicit. The same interface must be
used in the matched random-function control.

These corrections strengthen rejection. Fiat–Naor's balanced point is outside
the `lambda,mu<=0.45` rectangle, full Hellman preprocessing has exponent one,
BSGS separately gives the correct `N^(1/2),N^(1/2)` DLP control, and rho gives
`N^(1/2)` time with negligible memory. No standard-input gain survives.

The semantic lane is occupied but the dedup label is overstated.
`ECDLP-IDEA-374` inverts a five-deck endpoint function and requires
restriction-stable exact source replay; this row inverts a scalar-to-point map.
Both are function-inversion mechanisms and neither is admissible, but they are
not exact duplicates of the same function/interface.

## `B22-T04` — Koutis multilinear detection

The Koutis theorem core is accurate. Its load-bearing hypotheses are that the
arithmetic circuit already exists, a desired square-free degree-`k` monomial has
odd coefficient, and the circuit can be evaluated modulo `2^(k+1)` in the
stated `t,s`. The theorem neither constructs the circuit nor returns the
monomial's variable support.

Three composition details need correction:

1. A full six-list relation circuit has `k=6` and six colored `B`-sized
   variable decks. A fixed-target equation `A1+...+A5-R=O` has `k=5` if `R`
   is a constant. The distinction changes only constants here, but the object
   must be typed consistently.
2. `B^3` is the cost of the known explicit `3+3` construction/baseline. It is
   not a proved lower bound on every possible arithmetic circuit. Rejection
   rests on the absence of a compact exact constructor, not an unrestricted
   circuit lower bound.
3. Witness self-reduction would require restriction-stable circuits, repeated
   randomized detector calls, parity isolation, error amplification, and exact
   replay. Theorems 2.4 and 2.5 do not supply that composition, so its calls and
   success cost cannot be left implicit.

Even granting the detector, the full path lacks exact source output, `B`
duplicate-normalized independent rows, factor-base logs, identical masked-target
descent, relation data, verification, and circuit/relation memory. This is an
exact duplicate of the supplied-circuit multilinear lane in
`ECDLP-IDEA-280` and the `B21-P05` exterior/tensor frontier. The producer's
positive, negative, even-parity, matched-random, and explicit-enumerator controls
are appropriate. Supported SOTA delta remains zero.

## Full-cost and Pareto result

| Handle | Setup/object construction | Source/rank/log/descent path | Memory/data/communication | Pareto result |
|---|---|---|---|---|
| `T01` | Nonlinear target advice missing; scalar-field setup undercharged | Direct scalar return makes relation stages inapplicable only after valid advice | Auxiliary point(s), Cheon tables, and any external advice transfer charged | Standard input dominated by rho; conditional advice gain gets no SOTA credit |
| `T02` | Cover/factor base native only to extension-field regime | Native theorem includes index calculus; no original-`N` n=1 conversion | Prime-field bounds uninstantiated | Rho remains the complete target baseline |
| `T03` | `N`-scale Hellman preprocessing plus explicit reduction required | Direct scalar return after coverage/replay; no relation stages | Advice, online tables, coverage, replay, and target count charged | Corrected theorem is worse than reported; rho/BSGS are the matched controls |
| `T04` | Exact compact source circuit missing; known explicit baseline costs `B^3` | Detector supplies neither witnesses nor rank/log/descent | Circuit, randomized repetitions, relation matrix, and artifacts charged | Conditional detector overhead gets no SOTA credit |

The aggregate inventor accounting is honest after correction:

```text
dominated_by: n/a (no attack result claimed)
supported time-exponent improvement: 0.00
supported memory-exponent improvement: 0.00
supported data/query improvement: 0
cryptographic security bits reduced: 0
```

Per-handle `dominated_by` must refer to a complete cost point. In particular,
rho dominates the one-target T03 route once preprocessing is charged; BSGS is
the matched high-memory DLP control, not the Fiat–Naor theorem.

## Required revision and bounded forward guidance

Before archival, the producer package must:

- correct the Fiat–Naor/Hellman formulas, balanced exponents, preprocessing,
  and endofunction/reduction interface;
- separate Diem's main theorem from its growing-`n` consequence;
- charge Cheon's scalar-field setup and favorable-divisor condition;
- type the Koutis six-list and fixed-target circuits separately, restrict the
  `B^3` claim to known explicit constructions, and charge witness
  self-reduction/amplification; and
- refine `T03` from exact duplicate of `IDEA-374` to a neighboring occupied
  function-inversion family.

The corrected four-family obstruction map remains useful:

1. Cheon consumes the missing nonlinear target advice.
2. Diem consumes proper-subfield geometry absent at `n=1`.
3. Black-box function inversion needs the correct tradeoff, preprocessing, and
   iterable reduction; none beats the matched ECDLP baselines here.
4. Koutis consumes the missing exact source circuit and supplies no complete
   witness-to-descent path.

What remains open is narrower but nonempty: a non-permutation correspondence
defined directly over `F_p` with proved density/rank gain; an encoding-specific
inverse with explicit construction that beats matched random/rho/BSGS controls;
or a compact exact Abel–Jacobi circuit/separator theorem that is all-strata,
parity-safe, restriction-stable, and witness recoverable. `KN-OPEN-019` remains
open. Four rejected theorem families are not a theorem inventory, a saturation
argument, or evidence that generic prime-field ECDLP is closed.
