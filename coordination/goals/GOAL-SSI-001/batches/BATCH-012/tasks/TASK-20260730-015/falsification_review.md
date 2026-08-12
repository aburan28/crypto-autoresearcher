# Falsification review: pinned collimation process extraction

## Verdict

**CONFIRM, narrowly.** Snapshot
`aedd55676f03032f1a74f2da5f815754affdad2a` supports retaining
`FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`. The extraction makes real local
progress: it pins the author simulator, exposes the conditional bin-selection
law, and excludes unbounded lexical retention of failed same-level simulator
vectors. It does not reconcile an end-to-end stopping law, quantum/runtime
memory, or final key-recovery error.

The snapshot is reachable from `HEAD` on
`cursor/supersingular-isogeny-goal-a9d5`, has parent
`00182a123b46b2dbf9eddd0c9ed510e737045449`, and changes exactly the five
producer artifacts plus the snapshot receipt. SHA-256 calculations over every
producer artifact obtained with `git show` match the receipt. The receipt
itself remains a pre-commit payload with `commit_sha: null` and
`pending_post_commit`; independent Git checks supply the durable verification.

Read-only checks of GitHub's commit API and immutable raw URLs corroborate
commit `6f9188e4eb5611bcfdf29a3e1ec3cd69a29a50e9`, tree
`5c30ea26233c6a5df4c50dc8099431bb764decaf`, the `Main.hs` control flow, the
system-entropy-seeded `HashDRBG` wrapper, and the README's vector/RAM warning.

## Is the kernel invented?

The combinatorial expression is supported, but “exact retry kernel” needs its
full qualifier. Conditional on already-returned child vectors \(v_1,v_2\), and
under the ideal-uniform interpretation of the two `getRandomR` index choices,

\[
K_{v_1,v_2}(q)=
\frac{\#\{(i,j):\lfloor(v_1[i]+v_2[j])/s\rfloor=q\}}
{|v_1||v_2|}
\]

is exactly the probability that `collimate` selects bin \(q\). Once \(q\) is
selected, keep versus discard is deterministic.

That is not an exact kernel for the concrete retry process. It conditions away
the recursive generation of \(v_1,v_2\), does not include the hidden and
advanced `HashDRBG` state, and does not describe recovery, verification, or a
terminal classical tail. After a discard, the code regenerates both children;
it does not merely resample \(q\) from fixed children. The producer explicitly
states the ideal-random and local qualifications, so the extraction is not
fabricated. Future summaries should call it an **ideal-random conditional
collimation-bin kernel and deterministic retry branch**, not an unqualified
exact retry or end-to-end transition kernel.

The kernel also does not prove progress. A sampled pair guarantees that the
selected bin is nonempty, but nonempty need not meet
\(\lceil\theta\ell\rceil\). No invariant in the repository supplies a
history-uniform positive keep probability. A discard rate printed after a
terminating run cannot fill that gap.

## C2: live only as an underdetermination control

C2 remains live in the only defensible sense: the pinned artifact does not
entail a summable complete stopping tail. It supplies neither a uniform
conditional keep bound at every reachable internal retry state nor recovery
and terminal-tail transitions. Finite joint \(Q/S/P/C\) expectations therefore
remain unproved.

The displayed law

\[
\Pr[\tau=n]=\frac{1}{n(n+1)}
\]

must not be attributed to the simulator. It is an abstract mutation showing
that local positive finite costs plus no tail premise do not imply finite total
expectation. In particular, the producer has not derived that exact
distribution from the finite-machine `HashDRBG` program. This distinction
matters: “the required tail implication is missing” is supported; “the pinned
implementation admits or exhibits this exact heavy tail” is not.

The cheapest discriminator is a small exact reachable-state audit. Enumerate
child-vector pairs for bounded internal instances, calculate every
\(p(v_1,v_2)\), and search for a reachable zero-progress witness. Such a
witness kills a geometric-tail inference immediately. Failure to find one at
small scale is diagnostic only; it does not prove a parameter- and
history-uniform lower bound.

## C3: one lexical subcase is rejected

The source shows that a failed local `v` is not stored and is not passed to the
same-level recursive retry. Fixed recursion depth also bounds the number of
completed sibling vectors named by active source frames. This rejects the
specific mutation in which every failed same-level simulator `PhaseVector`
remains lexically referenced.

It does not reject broad delayed-cleanup C3. Haskell source-level last use is
not a garbage-collector deadline or heap bound. Massiv/vector temporaries,
parallel evaluation, compiler retention, and other backing objects are
excluded. More importantly, the simulator contains no coherent workspace
\(W\), QRACM allocation contract \(R\), end-to-end backing schedule \(B\), or
terminal-tail memory \(M_{\rm tail}\). Recovery objects are absent entirely.

Accordingly, a bare summary “C3 rejected” would be claim creep even though the
producer's adjacent scope fields prevent that creep in the reviewed snapshot.
The durable wording should be:

> C3's lexical simulator-PhaseVector subcase is rejected; global delayed
> retention and the FC0 memory map remain unresolved.

This is enough to preserve `QM-MEMORY-MAP`; it is not memory clearance.

## Error map and premature QUERY_MEMORY clearance

Defining

\[
F_{\rm sim}=\{\text{the simulator fails to emit its declared report}\}
\]

is a useful typing step. It is not the required operational event. The normal
simulator output is a statistics report, not a recovered and independently
verified key. There is no implementation-derived implication from
\(F_{\rm sim}\) or \(F_{\rm sim}^{c}\) to

\[
F=\{\text{final end-to-end key recovery fails}\}.
\]

Oracle approximation, quantum realization, recovery, verification, and tail
paths remain absent or unmapped. `QM-ERROR` therefore remains blocking.

The same applies to `QM-STOPPING`: local counters do not charge the complete
random sum through recovery and terminal handling. `QM-MEMORY-MAP` remains
blocking because lexical vectors do not instantiate the global FC0 categories.
Rejecting one lexical C3 subcase cannot clear `QUERY_MEMORY` while all three
blockers remain.

## Baselines and claim creep

No complete attack row exists, so there is no admissible quantitative
comparison against Pollard rho or BSGS. The closest specialized baseline is
Peikert's own pinned collimation-sieve simulator and its paper accounting.
This batch extracts local implementation semantics; it does not produce a
competing attack, a finite end-to-end resource vector, a Pareto improvement,
or a `sota_delta`.

Representation, relation collection, rank, scalar orientation, source
recovery, target descent, and final verification are not instantiated. No
numeric-security, NIST-level, parameter, breakthrough, generic-ECDLP, or
goal-completion claim appears. No curve, isogeny, simulator, or quantum-circuit
execution occurred. Those boundaries are correctly preserved.

## Narrow conclusion and next action

The durable conclusion is only that the pinned simulator supports a local
ideal-random conditional collimation-bin law and rejects accumulation of failed
vectors as lexical simulator references. C2 and the error-map audit remain
live; broad C3 and the complete FC0 memory map remain unresolved.
`FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED` is supported.

Next, build a bounded exact reachable-state analyzer for small internal sieve
instances to seek zero-progress witnesses, and separately specify the complete
recovery procedure with explicit \(W/R/B/M_{\rm tail}\) births, deaths,
cleanup, widths, and one recovered-key verification event \(F\). Small-instance
coverage may find a counterexample or motivate a proof, but it must not be
promoted to a global tail bound.
