# V9 Local Accepted Counterexamples

## Status

`NEGATIVE RESULT` | `MODEL-BOUND` | `ZERO-RUN`

These two isolated artifacts were produced from the immutable V9 review bundle
rooted at:

```text
b5426daa7d9ebf66db356ae2080780712e8318f03bec04c37d12b45580bd2b1c  tt-supervised-executor-v9-review-bundle/SHA256SUMS
```

The source bundle is unchanged. Each counterexample uses the unchanged frozen
independent verifier:

```text
e050b19ebd36858e42581f8fac0b17c80867a0f34b994b7876d8bddaa2d85c12  verify_v9_closed_kernel.mjs
```

## Recalculation Linkage

The mutation replaces the A2 recalculation's terminal and totals digests with
fabricated values, then relinks the recalculation, lock release, M008/M009
journals, and final roots. Exactly four durable records differ from the frozen
A2 universe.

```text
38bf002efc5c7fa02395f2875497c6ae5081f92fe583969be634151ad3cf093c  recalculation-linkage/supervised-executor-closed-kernel-v9.json
4890ae3c9f7dc8836f6e4fb8eb60a7ddf3cf4bab7a712fe2ae78922af9a0ef1a  recalculation-linkage/local-verification-v9.json
```

Observed verifier result: `PASS`, 132 checks, 2 traces, 211 steps, 26/26
regressions.

## Record Schema

The mutation changes only the final A2 action receipt's protocol schema literal,
canonically rehashes it, and updates the final journal/universe roots.

```text
e0bb1e384978f0e09dfc6bc9a36becac0dccfb54013144b0b7642f6a9282daac  record-schema/supervised-executor-closed-kernel-v9.json
2ec2e96b610ba64fddef519ada7740acf8f31d0508cf37c0227e5afcd1f9ffa8  record-schema/local-verification-v9.json
```

Observed verifier result: `PASS`, 132 checks, 2 traces, 211 steps, 26/26
regressions.

## Independent Red Team Cases

The independent Red Team additionally produced and accepted these fully
rehashed artifacts:

| Case | Artifact SHA-256 | PASS receipt SHA-256 |
|---|---|---|
| False late closure | `ccedc0f1c911bd8af14095a097ed3f2b10e06136268fc74a82e6c4709998930f` | `e8481a0157b3efffff9333b9a4a8bc60239a0f71feba62fc216ed3ca94b99f15` |
| Cross-phase Git | `c0d7fc6f41fd82a4979a55592da1fdb2f796cd7074bfc6c76d74f9c743ef49b5` | `a1af2534590f625d50bad46115b7d8d4f8283873a957d5535346f60ee0ce2bca` |
| Capability/launch relinking | `a0f72b00cfcf2c80724aade72d61e79641b29f450dcc1dec76783944739db4d8` | `2c4cdab4a2a879a202f67f66127ff15853ab0c112ef63c470ec7167135bc66c5` |
| Invalid resource observations | `6c500756102a1903202fd82cb94df62de0ce73e8356c95489b5d9f7b37e9c8d5` | `7212fddc28ffc8d0abe3fd27f4a4d1b3b5c5c0932d06e8756fbfc07d4b349b6b` |
| Sequence-zero known type | `42db1592d1cb145b6fa4e26d7b4d5b3df60fa8620548b92703c7f318abb98709` | `17ff8e66ec2208d0e99957bbc7b79f08cf8fd189ad99fc8632fe313b72c68b34` |
| Cross-phase terminal | `7e829935a4504ae33778d459068640bac23d0b6aed03540ff2b50c2e44545d8d` | `710de980ccad3f04f8210a5213c1bc65299aa54ec45b0807596db5c4f27ddd71` |
| Regression-suite substitution | `e0061d15975d2532435c8a991af51ea8113f242fdb13994e81facb28f8dbe3d5` | `92e92566908ebece8ee04c03cf8a7c3ac69ee4f36428f701973fda0cf557cc62` |
| Evidence symlink alias | `d86c360e83d3e1ec8defcd2320962becad9f60cc23980a700a2acd91c018fb22` | `7e5958c18be596420b911da83eec8d39483afe25b2df25f627cb2352e1c6bf16` |

The unlisted-publication case preserves the original top manifest and PASS
receipt alongside the payload omitted from that manifest.

## Boundaries

These are verifier-model counterexamples, not runtime exploits and not ECDLP
results. They do not authorize schema implementation or a mutation campaign.
The copied mutated artifacts are evidence; run the mutation scripts only on a
fresh mutable copy of the frozen V9 bundle.

## Next Concrete Action

Freeze this package and both independent NO-GO reports inside the rejected V9
snapshot, then use every accepted case as a pinned V10 negative control.
