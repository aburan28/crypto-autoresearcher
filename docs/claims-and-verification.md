# Claims and Verification

This program produces **empirical evidence over tested instances**, never
mathematical proofs about ECDLP hardness. Two mechanisms keep claims honest:
a **claim-tier ceiling** on what any record may assert, and a
**certificate discipline** that independently re-checks every claimed solve or
relation. Together they are the closest tractable analogue to formal
verification for this domain.

## Why certificates are possible here

ECDLP is in NP: *finding* a discrete log is believed hard, but *checking* one
is trivial. Given a claimed `k`, computing `k*P` and comparing to `Q` costs
O(log k) group operations. Likewise a claimed decomposition
`R = P_{i_1} + ... + P_{i_m}` (a factor-base relation) is checked by summing
the named points and comparing to `R`. So every positive result this program
can produce is **cheaply and independently verifiable**, regardless of how it
was found.

This is the honest ceiling of "proof" available here: we cannot certify that
ECDLP is hard, but we can certify that every claimed *success* is real and not
a fabricated or buggy output. That directly answers the harness's worst
failure mode — an agent reporting a solve that never happened.

## Certificate discipline

Every run that claims a solve or a relation MUST emit a certificate, and the
run wrapper MUST re-verify it **with code independent of the solver** before
marking the run `completed_valid`.

```yaml
certificate:
  kind: discrete_log | decomposition | none
  # discrete_log: claim that k solves Q = k*P on the named curve
  curve_id: TOY-P<bits>-<hash>
  statement:
    P: [x, y]
    Q: [x, y]
    k: <integer>            # discrete_log
    # decomposition:
    target: [x, y]
    summands: [[x, y], ...]
  verified: true
  verifier: independent-recompute   # NOT the solver's own code path
  verifier_commit: <git-sha>
```

Rules:

- **Independence.** The verifier recomputes `k*P` (or the point sum) from
  scratch using the curve arithmetic module, not by trusting the solver's
  internal state. A solver bug that returns a wrong `k` must fail the check.
- **A failed certificate invalidates the run** as `invalid_measurement` (the
  solver claimed success but the witness is wrong) — it is NOT a
  `negative_observation`. A negative observation is a *valid* run that
  correctly reports "no solution found within budget."
- **`kind: none`** is used for pure measurement runs (e.g. recording Gröbner
  solving degree without claiming a solve); those have nothing to certify, and
  that is stated explicitly rather than left blank.
- Certificates are stored in the run's `raw-result.json` and summarized in the
  manifest's `result.certificate`. They are immutable like the rest of the run.

## Claim-tier ceiling

Every evidence record and synthesis statement carries a `claim_tier` bounding
the largest claim the data can support. A record may never assert above its
tier, and the tier is a function of the *instances actually tested*, not of
ambition.

| tier | tested scale | may assert | may NOT assert |
|---|---|---|---|
| `toy` | fields ≲ 32 bits, tiny factor bases | behavior on the tested toy distribution; trends worth a scaling study | anything about medium or cryptographic curves |
| `medium` | fields up to ~64–96 bits, multiple instances/seeds | a stable measured effect on the tested medium range | cryptographic-scale (P-256+) behavior |
| `crypto` | standardized/cryptographic-size curves | scoped claims about those exact curves | universal impossibility; claims beyond the tested curves |

Independent of tier, no record may make a **universal impossibility** claim
("index calculus cannot beat rho over prime fields") from bounded experiments
— that is the domain of `open-problems/`, and the negative-result phrasing in
`docs/evidence-and-reproducibility.md` is mandatory.

The tier a run contributes to is derived mechanically from its parameters:

- `toy`: max field bit size ≤ 32
- `medium`: 32 < max field bit size ≤ 96
- `crypto`: max field bit size > 96 on a recognized curve

A synthesis spanning several experiments takes the **minimum** tier of its
supporting evidence unless a dedicated scaling analysis justifies otherwise.

## Where this is enforced

- **Executor / run wrapper** (`harness/runner.py`): emits and independently
  re-verifies certificates; refuses `completed_valid` on a failed certificate.
- **Evidence records** (`templates/research-records.md`): carry `claim_tier`
  and `certificate_refs`; the Coordinator sets the tier during
  `/review-evidence`.
- **CI** (`tools/validate_ledger.py`): checks that any run claiming a solve has
  a `verified: true` certificate, and that no evidence record's `claim_tier`
  exceeds what its runs' parameters allow.

## What this does NOT provide

- No proof of ECDLP hardness or of any complexity lower bound.
- No certification that a *negative* result generalizes — a certificate proves
  a positive witness is real; absence of a witness within budget is only ever
  a scoped negative observation.
- No formal (machine-checked) proof of theorems. If the program ever makes a
  theoretical claim, it must be routed to an external proof assistant or human
  referee; this document covers empirical results only.
