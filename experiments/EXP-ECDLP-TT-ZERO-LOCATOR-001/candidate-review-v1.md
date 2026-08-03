# Direct five-source TT candidate review v1

## Decision boundary

All candidates below are paper-only. None is a breakthrough claim or an
implementation authorization. They are ranked by how directly they reduce the
remaining uncertainty after the v4 preflight.

## Ranked candidates

### 1. Gate-by-gate RCB central-rank theorem or counterexample

Status: `OPEN`, highest priority.

Mechanism: exploit the actual algebraic dependencies among complete projective
addition coordinates, Frobenius conjugates, and the norm-indicator chain to
construct small exact row spaces, or prove a dense minor at one named gate.

Why it matters: this decides the current route without hiding behind final
sparsity or generic counterexamples.

Kill condition: any required central rank `Omega(B)`, cumulative target
resource `Omega(B^2)`, or fixed advice `Omega(B^3)` under Tier B.

Next action: derive the unfolding of the first norm-Hadamard gate at the
`2|3` cut and search symbolically for either an explicit basis or a scalable
nonsingular minor.

### 2. Coordinate-specific sub-functions inspired by 3SUM-Indexing

Status: `OPEN`, representation change.

Mechanism: replace the integer residue splitter with a coordinate route that
supports cheap partner lookup, bounded collisions, and exact witness recovery
without materializing `D3`.

Why it matters: the 2026 Dinur-Golovnev paper demonstrates that
application-specific sub-functions can improve generic inversion, but direct
`D2/D3` substitution costs at least `O~(B^4)` advice and `O~(B^2)` query time.

Kill condition: random-hash behavior, an implicit discrete-log label,
`Omega(B^3)` source storage, or `Omega(B^2)` online partner work.

Next action: write one explicit route preflight with partner-query,
collision, advice, construction, traffic, and replay equations.

### 3. Balanced exact `D2+D3` incidence compiler

Status: `OPEN`, conservative extension.

Mechanism: treat the central additive intersection directly and seek a
coordinate incidence, multipoint, or batch reporting algorithm that avoids
enumerating either complete side.

Why it matters: the exact final TT rank theorem identifies the same additive
intersection that a direct compiler must solve. A theorem here would inform
both the positive algorithm and the structured-group barrier track.

Kill condition: all known constructions expose `D2` target outputs, retain
`D3` advice, or give only decision without signed source witnesses.

Next action: formalize the partner-reporting problem with unequal source sets,
then derive a coordinate energy/incidence quantity that controls output and
query work separately.

### 4. Six-mode batched-target tensor

Status: `CONJECTURE`, high-risk speculative.

Mechanism: add target index as a sixth mode so multiple relation attempts share
the complete addition and indicator structure before exact normalization.

Why it matters: shared Frobenius and row-space work could reduce amortized
traffic even if one-target ranks are too large.

Kill condition: target-mode rank grows linearly with batch size, concurrent
peak state reaches the same total as independent attempts, or certification
and history-conditioned rank yield remove the amortization.

Next action: derive the six-mode cut ranks and concurrent peak-state equation
for a symbolic batch before proposing code.

### 5. Reduced-polynomial zero map for the fixed circuit image

Status: `CONJECTURE`, high-risk representation change.

Mechanism: replace generic Fermat powering by an exact polynomial that agrees
with the zero indicator only on the attained value set of the EC circuit.

Why it matters: a small attained-value set or structured annihilator could
shorten the Hadamard chain and reduce intermediate ranks without changing the
zero set.

Kill condition: the attained values cover `Theta(p^2)` field elements, the
minimal exact separator has comparable degree, or computing the value-set
annihilator recreates five-sum enumeration.

Next action: prove a symbolic bound on the attained value set for one frozen
RCB gate; do not infer it from toy histograms.

## Recommendation

Run candidates 1 and 2 as parallel paper tracks. Candidate 1 is the shortest
decision path for the current tensor route. Candidate 2 is the best live
translation of the fixed-curve preprocessing lead. Keep candidates 4 and 5 as
high-risk theory branches only after their dimension ledgers exist.

## Handoff: ranked successor set

### Claim or task

Choose the next paper preflight without authorizing implementation.

### Status

`OPEN`

### Assumptions

- Random ordinary prime-field curves remain the target family.
- Every fixed-curve offline resource, online resource, witness, and success
  probability remains separately charged.

### Evidence so far

- V4 isolates intermediate central TT rank as the immediate unresolved gate.
- Direct application of the latest integer 3SUM-indexing theorem misses the
  fixed-curve advice and online thresholds.
- Exact final ranks identify an additive-incidence object worth studying
  independently of TT syntax.

### Failure modes

- Repackaging the same dense `D2/D3` object under a new solver name.
- Treating toy correctness or low final rank as compiler evidence.
- Omitting construction, traffic, certification, or rank-yield retries.

### Next concrete action

Freeze the first-gate central-rank proof/disproof contract against v4.

### Artifact paths

- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/candidate-review-v1.md`
- `notes/ecdlp_3sum_indexing_transfer_20260718.md`

