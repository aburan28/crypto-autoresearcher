# V9 A2 Recalculation Linkage Counterexample

## Status

`OBSERVATION` | `MODEL-BOUND` | `ZERO-RUN` | `INDEPENDENT-REVIEW-PENDING`

This is a local verifier-acceptance counterexample. It is not an ECDLP result,
does not authorize implementation or campaign execution, and does not alter the
frozen V9 review bundle.

## Frozen Source

- review bundle: `tt-supervised-executor-v9-review-bundle`
- external root: `b5426daa7d9ebf66db356ae2080780712e8318f03bec04c37d12b45580bd2b1c`
- frozen builder: `5b63cfe63c1c4634bfcbe0e39b022dc9e3aabc3079e83cb6fcce1d3b21ee1848`
- frozen independent verifier: `e050b19ebd36858e42581f8fac0b17c80867a0f34b994b7876d8bddaa2d85c12`
- frozen artifact: `e651f2c42c2ccc555ce33ada4e64aabd717bdc85e06c94a3e5d97fcae9e8a35c`

## Candidate Counterexample

The A2 trace's `recalculation_receipt` was changed to bind:

```text
campaign_terminal_sha256 = 0000000000000000000000000000000000000000000000000000000000000000
derived_totals_sha256    = ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
```

Neither digest names the required terminal or measured totals. The mutation
then canonically rehashed the recalculation record, relinked and rehashed the
`lock_release`, rehashed the M008 and M009 action receipts, and recomputed the
final journal and universe roots. No stale hash was left in the mutated closure
path.

## Observed Acceptance

The unchanged independent verifier returned:

```json
{"status":"PASS","receipt":"local-verification-v9.json","receipt_sha256":"4890ae3c9f7dc8836f6e4fb8eb60a7ddf3cf4bab7a712fe2ae78922af9a0ef1a","checks":132,"traces":2,"steps":211,"regressions":26}
```

Relevant hashes:

```text
f085eb9f58dc1570fe95a14a0f367fd12a2a45d29b267ac15ceee72f2848c324  mutate_recalculation_a2.mjs
0502781030adc14dec1bef5e95bdff1bf095c5571698c534d5acb1e8ddc98685  counterexample-summary.json
38bf002efc5c7fa02395f2875497c6ae5081f92fe583969be634151ad3cf093c  supervised-executor-closed-kernel-v9.json
e050b19ebd36858e42581f8fac0b17c80867a0f34b994b7876d8bddaa2d85c12  verify_v9_closed_kernel.mjs
4890ae3c9f7dc8836f6e4fb8eb60a7ddf3cf4bab7a712fe2ae78922af9a0ef1a  local-verification-v9.json
```

## Differential

The frozen builder validates recalculation and lock-release linkage at lines
669-676 of `build_v9_closed_kernel.mjs`. The frozen verifier returns from
`semanticAudit` at line 432, immediately after campaign-terminal checks, and
contains neither validation loop. This is an executable builder/verifier
differential, not merely an omitted stored mutation.

## Strongest Current Interpretation

If independently confirmed, V9 fails `V9-DIFFERENTIAL-01` and the closure part
of `V9-IDENTITY-01`: the journal proves that a trusted producer emitted exact
bytes, but the independent verifier does not prove that those closure bytes bind
the terminal and measured totals they claim to attest. The narrow V9 happy-path
observation remains true; the proposed implementation gate does not.

## Reproduction

```bash
node mutate_recalculation_a2.mjs
node verify_v9_closed_kernel.mjs
```

Run the mutator only on a fresh copy of the frozen V9 bundle.

## Next Concrete Action

Obtain independent Theory and Red Team reproduction and classification against
the frozen V9 root before preserving a V9 rejection snapshot or cutting V10.
