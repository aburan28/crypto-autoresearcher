# TT Source Supervised Development Preflight V7

## Status and claim boundary

Semantic status: `OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`.

Source producer/verifier supervision status: `GO` within
`runtime-boundary-decision-v1.md`.

Full experiment status: `REVISE`.

This checkpoint does not freeze source advice, authorize a campaign, produce a
locator, establish index calculus, improve Pollard rho, or establish an ECDLP
breakthrough. The experiment still has no `execution_plan`.

## Review sequence and repairs

An independent V21 review returned `REVISE` with two in-model fail-open paths
and one framing weakness:

1. A fabricated canonical static report could alter public policy fields or
   stale policy hashes without a complete parent replay.
2. Distinct output names could be hardlinks to one inode, allowing the receipt
   write to overwrite the accepted result.
3. Whitespace-only auxiliary verifier stderr was discarded rather than
   rejected.

V22 preserves that negative evidence and repairs all three findings:

- all six policy inputs are retained, hash-bound, replayed through the complete
  static audit, compared exactly, and retained a second time after replay;
- verifier stderr is one exact bounded canonical frame;
- output and receipt use individual atomic replacement, `O_NOFOLLOW` regular
  file reopening, exact byte verification, and final inode distinctness;
- deterministic policy-forgery, stale-hash, whitespace-framing, oversized-frame,
  and APFS hardlink controls fail closed.

The follow-up independent review returned `GO` for the three scoped findings.

## V22 evidence

All artifacts remain outside the repository and report
`artifact_freeze_authorized=false`.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `source-static-closure-audit-v22.json` | 222,385 | `27170d095aa6945f697a2b0cf12da33bf6054615f8d74ddd91c673fbe9592028` |
| `source-generator-staged-development-v22.json` | 138,592,835 | `cc7b3e0cf24e28976c11ef6bcbdfa1dd5fea36df42233783fe4a1fe81f36411e` |
| `source-generator-staging-receipt-development-v22.json` | 14,465 | `0a6ce2070abb005c1cb5ac5ce2e462bf09a4683f99440f9e72fd84c477e02a09` |
| `source-verifier-staged-development-v22.json` | 23,619 | `43e29ab085cb3819e08c402273eeadd5185e3b53c9d4a4bd20aaafd150c18502` |
| `source-verifier-staging-receipt-development-v22.json` | 23,087 | `247427782407aa0ee599a22799e4a89c9449b360bad442f0a410de7c4b47348d` |

Both parent receipts report:

- retained approved manifests equal to first stage snapshots;
- watched device/inode/type/size rows equal to pre-run and post-run paths;
- zero setup mutation events and zero run mutation events;
- matching pre/post runtime closure
  `f312a51165c62d3c510945658351b960ac63713f2c6dcdb8f7df16ae00944098`;
- no-follow publication with output/receipt inode distinctness.

The producer stage digest is
`d813003f6031e25456e9ee19f4ef88865b41d1f199122c8c034b24b38ebfafd6`.
Its parent-observed child wall time is 42.441 seconds and peak RSS is
1,272,135,680 bytes. The verifier stage digest is
`dadac0dd3de659b4282b31878110092c582918f6ae0d5be6ca39dd242325a944`.
Its parent-observed child wall time is 32.717 seconds and peak RSS is
1,056,178,176 bytes.

## Semantic invariants and accounting

The semantic candidate remains stable across the repair:

- control certificate:
  `b4ab406a8fd48b697584e03bb681d23be9562ea51a5e4684ac2ca206d6cbb06e`;
- retained advice:
  `adfacac64f7a143e9dec8c7f849b7bb9517ff07c7099b80279c7ca9a891c529e`.

The source-advice receipt changes to
`a6236ffb8583409b8d76a18691408c586663ff92235671fb2f36db30f1284b92`
because it binds the new static audit and run-specific runtime receipt. That is
expected provenance drift, not semantic advice drift.

The producer's independently replayed accounting remains:

```text
adds                              15,993,829
subs                              11,338,088
muls                              29,684,153
inversions                            32,318
reductions                        25,205,740
comparisons                       10,970,713
hash bytes                        15,212,273
copied words                       6,975,387
logical traffic words            107,717,332
peak live field words                 49,580
```

The independent verifier reports 55,380,898 logical traffic words, a
52,880-field-word peak, 12.805 CPU seconds, and exact binding to producer raw
SHA-256 `cc7b3e0cf24e28976c11ef6bcbdfa1dd5fea36df42233783fe4a1fe81f36411e`.

## Verification

- source-supervision controls: 17 tests passed;
- complete experiment suite: 64 tests passed in 5.134 seconds;
- repository suite: 144 tests passed in 263.132 seconds;
- independent V22 recheck: `GO` for audit authority, publication aliasing, and
  verifier framing.

The source producer and verifier remain separate staged closures. The verifier
stage excludes the compiler, backend attestor, and source runtime, while the
producer stage excludes the independent verifier and predecessor raw result.

## Remaining gates

- Freeze a runner-compatible producer envelope that preserves both child output
  and parent supervision receipt through the committed predecessor transition.
- Build and independently review the full 29-mutation live-source/live-record
  harness; the 22 synthetic target mutations are not a substitute.
- Create and separately approve an `execution_plan` only after those protocols
  and exact implementation hashes are frozen.
- Preserve the runtime/shared-cache and trusted-host exclusions in
  `runtime-boundary-decision-v1.md`.

## Next concrete action

Implement the runner-compatible source artifact envelope and a deterministic
test showing that a verifier cannot consume any raw result other than the exact
Git-committed predecessor envelope named by the execution plan.
