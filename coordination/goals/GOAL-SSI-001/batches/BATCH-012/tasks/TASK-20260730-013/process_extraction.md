# FC0-R2 process extraction from Peikert's simulator

Task `TASK-20260730-013` · artifact commit
`6f9188e4eb5611bcfdf29a3e1ec3cd69a29a50e9` · zero simulator, curve,
isogeny, and circuit runs.

## Scope of the artifact

The pinned author repository implements one classical simulation of a
collimation-sieve invocation. `src/Main.hs` constructs a fixed interval
schedule, calls `sieve`, records query/node/discard counters, and computes
regular/punctured-state probability summaries. It does not implement repeated
secret-information recovery, terminal classical enumeration, key
verification, or a final key-recovery decision. Therefore the extraction below
is implementation-compatible for the local recursive sieve only; it is not an
invented completion of the missing end-to-end process.

## Explicit local transition kernel

The source anchors are `src/Main.hs` symbols `sieve`, its local function
`sieve'`, and `collimate`.

For fixed non-base call state
\[
x=(a,n,\theta,(s:s':\sigma),\ell),
\]
where \(a\) is `alwaysKeep`, \(\theta\) is `threshold`, and \(s<n\), the code
first recursively produces child vectors \(v_1,v_2\). Conditional on those
vectors, `collimate s (v1,v2)` samples indices
\[
I\sim U\{0,\ldots,|v_1|-1\},\qquad
J\sim U\{0,\ldots,|v_2|-1\}
\]
through two `getRandomR` calls. Put
\[
q=\left\lfloor\frac{v_1[I]+v_2[J]}s\right\rfloor
\]
and define the deterministic sorted output
\[
V_q=\operatorname{sort}\{(v_1[i]+v_2[j])\bmod s:
qs\le v_1[i]+v_2[j]<(q+1)s\}.
\]
For every attainable integer \(q\), the exact conditional kernel extracted
from the code is
\[
K_{v_1,v_2}(q)
=\frac{\#\{(i,j):\lfloor(v_1[i]+v_2[j])/s\rfloor=q\}}
{|v_1||v_2|}.
\]
The next control state is `return V_q` when
\[
a\ \lor\ |V_q|/\ell\ge\theta,
\]
and otherwise is a fresh recursive call with the same
\((\text{False},n,\theta,(s:s':\sigma),\ell)\). Counter updates are
deterministic given that branch: every attempt increments `numNodes`; a
discard also increments `numDiscarded`; leaf creation increments
`numQueries` by `round(log2 l)`.

At the base branch \(s\ge n\), the kernel is the distribution of the sorted
subset-sum vector generated from `round(log2 l)` independent-looking
`getRandomR (0,n-1)` draws, reduced modulo \(n\). `src/Random.hs` realizes the
random monad with a system-entropy-seeded `HashDRBG`. The repository gives no
formal probabilistic contract for the DRBG stream, so the displayed kernel is
the natural ideal-random interpretation of the calls, not a proved property of
the concrete generator.

One useful exact fact is that \(V_q\) is nonempty: it contains the sampled pair
\((I,J)\). This prevents a zero-length child from the collimation step, but it
does not imply the threshold condition.

## Progress and tail-bound attempt

Conditional on \(v_1,v_2\), define
\[
p(v_1,v_2)=
\sum_{q:\ a\lor |V_q|\ge\lceil\theta\ell\rceil}
K_{v_1,v_2}(q).
\]
This is the exact one-attempt progress probability exposed by the artifact.
For top-level `alwaysKeep=True`, it equals one after both recursive children
return. For internal calls it need not have an artifact-supplied positive
lower bound: the code contains no assertion or proof that some bin \(V_q\)
reaches \(\lceil\theta\ell\rceil\), and its empty test suite supplies no such
invariant.

If an external proof established
\[
\inf_{\text{reachable histories}}p(v_1,v_2)\ge\varepsilon>0
\]
at every retry site, then the conditional tail would satisfy
\(\Pr[T>t\mid\mathcal F_0]\le(1-\varepsilon)^t\), and the fixed finite recursion
depth would support finite retry moments and additive expectations. The pinned
artifact does not establish this premise. Empirical discard rates printed by
`main` are observations after a run, not uniform conditional bounds.

Accordingly, neither almost-sure termination nor finite expected
`numQueries`/`numNodes` follows from the artifact alone. The artifact also has
no counters for FC0-R2 postprocessing \(P\), classical work \(C\), recovery
runs, or terminal-tail work. Finite joint \(Q/S/P/C\) expectations are
therefore neither proved nor refuted.

## Source-reference object-lifetime trace

The following trace is a lexical-reference trace of `sieve'`, not a Haskell
runtime heap guarantee and not a quantum implementation schedule.

1. Enter a non-base frame; no child vector is yet rooted by the frame.
2. `v1 <- sieve' ...`: `v1` is born when the first child returns.
3. `v2 <- sieve' ...`: `v1` remains live while the second child runs; `v2` is
   born on return.
4. `v <- collimate s (v1,v2)`: `v1` and `v2` remain live; `v` and collimation
   temporaries are born.
5. After `vlen` and `keep` are computed, `v1` and `v2` have no later source
   uses and become unreachable subject to compiler/runtime retention.
6. On keep, `v` is returned. On discard, the counter update occurs and the
   same-level recursive call has no argument referencing `v`; `v` is
   source-unreachable before the retry.

For recursion depth \(D=|\texttt{ss}|-1\), an active descent can retain at most
one completed sibling vector per ancestor frame; a local collimation adds
`v1`, `v2`, and `v`. Thus failed attempts do not create an unbounded list of
source-reachable `PhaseVector` roots, and source-level root concurrency is
bounded by \(D+3\), excluding library temporaries, parallel workers, logging,
and garbage-collector retention. `strat = A.Par` permits intra-array
parallelism but does not add sibling sieve calls in the source.

This trace rejects C3 only for source-level simulator `PhaseVector`
references. It does not supply the widths or births/deaths of quantum coherent
workspace \(W\), QRACM \(R\), other attack backing \(B\), or terminal-tail
memory \(M_{\rm tail}\):

- \(W\): not represented by the classical simulator.
- \(R\): simulated by ordinary arrays only; no QRACM allocation/lifetime API.
- \(B\): Haskell arrays and runtime temporaries exist, but no hard heap or GC
  contract is supplied. The README warns that vectors may reach a package
  limit and very large RAM use.
- \(M_{\rm tail}\): absent because terminal classical search is absent.

## Failure paths and event map

Define the artifact-level event
\[
F_{\rm sim}=\{\text{the invocation does not emit its complete declared
simulator report for the supplied arguments}\}.
\]
All exposed simulator failure paths map to \(F_{\rm sim}\):

- malformed/missing arguments, failed `read`, or the three-element pattern
  match in `main`;
- `sieve: empty list of interval sizes`;
- DRBG construction/split/random errors propagated through `error . show`;
- invalid or empty random ranges if a violated invariant reaches `randomElt`;
- vector-package length limit, allocation failure, or other runtime/resource
  exception noted by the README;
- arithmetic/index exception or machine-`Int` overflow;
- nontermination in an internal discard/retry chain.

Normal report production maps to \(F_{\rm sim}^{c}\). The code has no
key-recovery output, verification predicate, oracle implementation, or
residual-tail procedure, so there is no implementation-derived implication
from \(F_{\rm sim}\) (or its complement) to the FC0-R2 event
\[
F=\{\text{final end-to-end key recovery fails}\}.
\]
Oracle approximation, quantum realization, recovery, verification, and tail
failure paths are outside the artifact. The common operational error map
therefore remains uninstantiated.

## Extraction result

The artifact pins an explicit local collimation/retry kernel and rejects
unbounded retention of failed simulator vectors at the source-reference level.
It does not provide a uniform progress/tail bound, an end-to-end stopping law,
finite joint \(Q/S/P/C\) expectations, an FC0 \(W/R/B/M_{\rm tail}\) schedule,
or a map to final key-recovery event \(F\). The narrow disposition remains
`FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`.
