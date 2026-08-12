# Falsification review: FC0-R2 stopping and liveness

## Verdict

**CONFIRM**, narrowly. Snapshot
`442dbe6994d2c62dac286febc52b1ffeb369b3bc` supports retaining
`FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`. It does not support a claim that
Peikert's actual algorithm has infinite expected cost or unbounded implemented
memory. It supports only the accounting diagnosis that the cited source facts
do not instantiate the joint law and schedule required by FC0-R2.

The snapshot is reachable from `HEAD` on
`cursor/supersingular-isogeny-goal-a9d5`, has declared parent
`cf4468d02a25cf04b44bf0d4d732d8bfeb7da05b`, and changes exactly the four
producer artifacts plus the snapshot receipt. Fresh SHA-256 calculations over
each producer artifact obtained by `git show` match all four hashes in the
receipt.

## Invented stopping laws

The most tempting premature repair is to turn empirical regularization success
percentages into iid Bernoulli trials and then charge a geometric number of
retries. That move would instantiate finite expectations, but it is not
licensed by the reviewed source extraction. A realized least-frequency ratio,
expected recovered information per run, and empirical agreement with a
per-sieve query estimate do not imply independence between attempts or a
uniform conditional progress probability over the complete recovery history.

C2 exposes exactly this missing implication. The normalized law

\[
\Pr[\tau=n]=\frac{1}{n(n+1)}
\]

has \(\Pr[\tau\ge n]=1/n\) and hence infinite mean while every realized
invocation can retain positive finite per-run costs consistent with the local
source statements. This is not evidence that the paper's actual retries follow
that law. It is a discriminating mutation showing that the extracted local
facts alone do not entail finite total expectations. C2 is therefore correctly
reported as **not rejected by the source**.

The cheapest way to kill C2 is not another fitted average. It is a cited or
implementation-derived conditional tail bound: for every admissible history,
the procedure must have a uniform lower bound on progress or an equivalent
bound on the survival probability of the full retry/recovery process. That
bound must cover regularization discards, punctured attempts, fresh-sieve
recovery, and terminal-tail entry under one process.

## Incomplete liveness

Equation (3.5) and the Figure 1 hard
\(\widetilde L_{\max}=8L\) rule establish a narrow per-vector reusable-QRACM
bound. They do not enumerate all objects that are simultaneously live across
the oracle, recursive sieve, failed regularization, recovery, verification,
and terminal tail. In particular, they do not state births, deaths, cleanup,
reuse, or deterministic retry concurrency for coherent workspace, QRACM,
other classical backing, and tail state.

C3 preserves the per-vector cap while delaying cleanup of retry/recovery
backing objects. As with C2, this is an underdetermination control, not a claim
that the source mandates delayed cleanup. The word “discard” may justify
destroying a failed quantum vector, but it is not by itself a complete global
schedule for every associated classical table, transcript, recovery object,
oracle workspace, and tail object. Nor does “reusable QRACM” establish the
maximum overlap with all non-QRACM categories. C3 is therefore also correctly
reported as **not rejected by the cited source**.

To reject C3, a concrete schedule must list every relevant object with width,
birth, last use, cleanup, and reuse, and must prove a deterministic concurrency
bound. An expected number of retries is insufficient for a hard or
essential-supremum memory claim.

## Premature QUERY_MEMORY clearance

QUERY_MEMORY cannot be cleared by selecting compatible-looking estimates
independently:

1. \(\widetilde Q_{\rm total}\) must be identified with, or rigorously
   converted to, the expected random sum under the same stopping law used for
   all other additive costs.
2. Repeated-sieve, postprocessing, classical recovery, and terminal-tail work
   must be jointly finite under that law.
3. W/R/B/\(M_{\rm tail}\) must be bounded on one global timeline rather than
   inferred from a per-vector cap.
4. Oracle, sieve, postprocessing, recovery, verification, and tail errors must
   map to one declared final operational event before composition.

TASK-20260730-009 leaves each of these items visibly unresolved and names the
corresponding blockers `QM-STOPPING`, `QM-MEMORY`, and `QM-ERROR`. It does not
clear the gate by assertion.

## Claim-creep checks

No numeric-security, NIST-level, parameter, breakthrough, ECDLP, or
goal-completion claim appears in the producer artifacts. No complete attack
row exists to compare quantitatively against Pollard rho or BSGS. The closest
specialized baseline remains Peikert's own binary collimation-sieve Figure 1
accounting under its stated QRACM and optimistic-oracle assumptions; this batch
offers a gate diagnosis, not a Pareto improvement.

The O5 treatment is also scoped correctly. BATCH-010's hash-addressed
author-hosted verification of Equation (3.5), Equation (4.1), the hard 8L
language, and the conservative symbolic cap stands. BATCH-011 records HTTP 200
converted text from the canonical endpoint but no PDF bytes or canonical hash.
It therefore neither reopens the archived-host clearance nor claims canonical
byte identity.

The heavy-tail and overlap controls must not later be summarized as observed
behavior, and this control failure must not become an impossibility claim.
Failure to extract a joint law from the reviewed source leaves open the
possibility that a pinned implementation or a new derivation supplies one.

## Next falsification step

If the goal continues, pin the simulator or reference implementation control
flow and extract one transition kernel and one object-lifetime trace. Require
that artifact to provide a conditional progress/tail bound, finite joint
Q/S/P/C expectations, deterministic W/R/B/\(M_{\rm tail}\) concurrency and
cleanup, and complete maps to one final event \(F\). Rerun C2, C3, and the
error-map audit against that concrete artifact before reconsidering
QUERY_MEMORY.
