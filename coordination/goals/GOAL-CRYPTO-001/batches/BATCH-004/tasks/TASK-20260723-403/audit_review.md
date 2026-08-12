# Independent red-team review of the static cost audit

- `task_id`: `TASK-20260723-403`
- `goal_id`: `GOAL-CRYPTO-001`
- `batch_id`: `BATCH-004`
- `requested_policy`: `review-xhigh`
- `resolved_model_id`: `gpt-5.6-sol-xhigh`
- `reasoning_effort`: `xhigh`
- `fallback_used`: `false`
- `adapter_version`: `cursor-subagent-2026-07`
- `verdict`: `INCONCLUSIVE_COST_CLAIM`

This is non-operational academic mathematics. It contains no implementation,
run, real key, deployed-system analysis, standardized-curve execution, or
operational compromise instruction.

## Snapshot basis

The reviewed producer artifacts are the files committed by
`TASK-20260723-402` at
`404956b49584c69b531bf563852d23b0593b7031`, with parent
`30df6c48eddca6dcba45c4cc5f27a644383a3ef3`. The commit is reachable from the
review head, changes exactly the two producer artifacts plus the snapshot
receipt, and the three current file hashes match the task-card archive block.

There is one integrity caveat: the committed `snapshot-receipt.json` itself
still says `pending_post_commit` and has null commit and parent fields. The
subsequent Coordinator task-card archive block records the commit, parent, and
hashes, and direct Git checks confirm those values. Thus the snapshot used here
is immutable and verified, but the receipt alone is not a finalized
verification record.

## Independent exponent recomputation

Use the snapshot notation

\[
  B=\binom r d,\qquad
  M=\binom{r+d}{d},\qquad
  H=\binom{r+d}{d-1},\qquad r=\Theta(\log N).
\]

The central identity is exact:

\[
  \frac HM=\frac d{r+1}.
\]

For \(N>2r-1\),

\[
  \alpha=\frac{N-2r+1}{N(N-r+1)}<\frac1N,
\]

so the fixed-\(b\) endpoint existence model obeys

\[
  q_{\rm exist}=1-(1-\alpha)^M\le M\alpha<\frac MN.
\]

If every accepted public certificate is contained in these \(M\) events, the
same upper bound applies to public success. In a stationary low-success retry
model, however, charging \(H\) only to failed trials gives

\[
  \mathbb E[C_{\rm failures}]
  \ge \frac{1-q}{q}H,
\]

not \(H/q\) exactly. When \(q=o(1)\), the distinction is asymptotically
irrelevant and

\[
  \mathbb E[C_{\rm failures}]
  =\Omega\!\left(\frac{NH}{M}\right)
  =\Omega\!\left(\frac{Nd}{r+1}\right)
  =N^{1-o(1)}.
\]

The producer eventually restricts this cancellation to low success, so the
main verdict survives, but its unqualified appearances of \(H/q\) should not
be used for a constant-success or near-certain-success branch.

If \(d=o(r)\), then

\[
  \log M=d\log(1+r/d)+O(d)=o(r)=o(\log N),
\]

and \(M=N^{o(1)}\). For \(d\ge2\), \(H=N^{o(1)}\) as well, while the modeled
success is at most \(N^{-1+o(1)}\); the conditional retry lower-bound exponent
tends to one.

For \(d=\delta r\), \(r=\kappa\ln N\), and fixed \(0<\delta\le1\), Stirling's
formula gives

\[
  M=N^{\mu+o(1)},\quad
  \mu=\kappa\big((1+\delta)\ln(1+\delta)-\delta\ln\delta\big),
\]

and

\[
  B=N^{\beta+o(1)},\quad
  \beta=\kappa\big(-\delta\ln\delta-(1-\delta)\ln(1-\delta)\big).
\]

Since \(H/M=d/(r+1)\), \(H\) has exponent \(\mu\), and a full outer pass
\(BH\) has exponent \(\beta+\mu\). In particular, if \(BM=\Theta(N)\), then

\[
  BH=\Theta\!\left(\frac{Nd}{r+1}\right)=N^{1-o(1)}.
\]

If \(M=\Theta(N)\), then necessarily \(d=\Theta(r)\) and \(H=\Theta(N)\).
If the premise is merely \(M=\Omega(N)\), the correct statement is
\(H=\Omega(N)\), possibly superlinear. The producer's
`full_H_table_work_exponent: 1-o(1)` and analogous memory label therefore
understate the possible endpoint charge unless read only as lower bounds.

## Mechanism and end-to-end objections

The endpoint probability is not yet the success probability of one public
stopping process. An accepted branch must pass all of the following:

1. the \(a\)-restriction and fixed-\(b\) matrices have the required ranks;
2. two exact normalized penultimate vectors coincide;
3. their index union has cardinality \(d\);
4. the mapped maximal zero minor verifies;
5. sampled-point source coefficients are retained and reconstruct the
   relation;
6. the target coefficient is nonzero and the scalar orientation is valid; and
7. the final public group equality verifies.

The cited \(q_{\rm exist}\) does not include those conditions, and the
snapshot contains no theorem proving that every accepted certificate is
contained in the \(M\)-event family. Omitted failures can only reduce success,
but containment is still required before \(M/N\) can upper-bound the success
of this particular public interface.

The cheapest counterexample is the admitted \(d=1\) boundary:

\[
  M=r+1,\qquad H=1,\qquad q_{\rm exist}>0.
\]

A one-entry fixed-\(b\) table has no pair and cannot produce the stated
duplicate. This directly disproves equality of the two events at \(d=1\).
A special direct-completion branch could be studied, but it would be a
different, separately proved and charged process.

For \(d\ge2\), an equally cheap stopping-time mutation is to permute the same
\(H\) endpoint entries. The endpoint duplicate event, \(M\), and \(H\) stay
unchanged, while the first-duplicate position can change. Endpoint formulas
therefore do not determine early-stopped expected work. A prefix theorem tied
to the actual \(b/H\) order is indispensable.

The direct-relation interpretation does not require a separate factor-base
relation campaign, factor-log solve, or target descent. It does require the
complete source-recovery and oriented-scalar certificate path above. Exact
collision resolution and provenance require either an
\(\Theta(H(d\log N+\log H+\text{metadata}))\)-bit table up to representation
details or explicitly charged recomputation/I/O. Target-bearing rows and
retries cannot be amortized as curve-only preprocessing.

## Baselines

Pollard rho has expected aggregate work \(N^{1/2+o(1)}\) group operations and
small serial memory. BSGS has \(N^{1/2+o(1)}\) time and bit-memory exponent.
The conditionally aligned low-success signature route is
\(N^{1-o(1)}\), so it is asymptotically worse. Without event and stopping
alignment, the published route is unresolved, not evidence of an improvement.

The quoted 2018 Problem L probability gives \(N/\log^2N\) expected passes.
Its total work should be described as having exponent tending to one (or
\(N^{1+o(1)}\) after including a polynomial-in-\(\log N\) pass cost), rather
than conflating pass count with total bit work. The 2023/2025 minor-family
costs lack a matched large-\(N\), prime-field success law, so their end-to-end
exponent remains unknown. Neither specialized comparator supplies a
demonstrated sub-rho baseline.

## Verdict and one next action

`INCONCLUSIVE_COST_CLAIM` is upheld. The exact \(H/M\) cancellation and its
low-success near-linear conditional consequence are correct after restoring
the \((1-q)\) qualifier. They do not assign an exponent to the published
algorithm because acceptance containment, prefix stopping, rank, provenance,
orientation, and certificate conditions remain unproved; \(d=1\) is a direct
interface counterexample. This is not evidence of sub-rho work and not a
general lower bound for ECDLP or other zero-minor locators.

Recommended next action: produce one source-aligned \(d\ge2\) lemma mapping
every accepted fixed-\(b\) certificate to the \(M\) completion events and
proving a prefix success bound for the actual \(b/H\) order with all rank,
orientation, and verification conditions; if that lemma fails, retain
`INCONCLUSIVE_COST_CLAIM` and close only the failed interface.

## Safety scope

- `classification`: `non_operational_academic_mathematics`
- `activity`: immutable-snapshot formula, cost, and stopping-time review
- `compute_performed`: none
- `real_keys`: none
- `deployed_systems`: none
- `standardized_curve_execution`: none
- `key_recovery_software`: none
- `operational_compromise_instructions`: none
