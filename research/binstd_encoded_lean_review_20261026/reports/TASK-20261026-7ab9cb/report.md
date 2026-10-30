# Blind statement-only review: TASK-20261026-7ab9cb

**Judgment: holds for the five encoded finite predicates and the two degree-one controls as stated.** This judgment concerns the supplied bitmask algorithm. I did not inspect producer code, Lean statements or proofs, other reviewers' work, receipts, or the PR.

## Derivation and exact results

I interpreted bit `i` of a nonnegative integer as the coefficient of `X^i` over `F₂`. For each mask of degree `n`, `independent.py` enumerates every `d = 2^j + lower` with `1 ≤ j ≤ floor(n/2)` and `0 ≤ lower < 2^j`. It cancels the current leading bit by XOR with a shifted `d`, stopping only when the remainder has smaller degree than `d` or is zero. Every enumerated division finished within the statement's `n+1` step allowance. The output contains one row per tested candidate, with its remainder and step count.

| Mask | Degree | Candidate count | Zero-remainder divisors | Encoded predicate |
| ---: | ---: | ---: | --- | --- |
| 131081 | 17 | 510 | none | true |
| 313 | 8 | 30 | none | true |
| 471 | 8 | 30 | none | true |
| 131073 | 17 | 510 | 3, 313, 471 | false |
| 257 | 8 | 30 | 3, 5, 15, 17 | false |

The counts are `2 + 4 + ⋯ + 256 = 510` for degree 17 and `2 + 4 + 8 + 16 = 30` for degree 8. These include reducible monic candidate masks, as the statement requires. All three positive rows had zero zero-remainder candidates; the two negative rows have explicit witnesses shown above.

## Degree-one controls and boundary

Degree one enumerates lower masks `0` and `1`; the latter gives `d = 3 = X+1`. For `131073 = X^17+1`, the computed remainder by `3` is **0 after 17 XOR reductions** (fuel allowance 18). For `257 = X^8+1`, it is **0 after 8 reductions** (fuel allowance 9). Independently, evaluation at `X=1` gives zero in each case because each has two set coefficients, so the remainder modulo `X+1` is zero.

One boundary test is to require that the `(j=1, lower=1, d=3)` candidate is present and that these exact control divisions finish. With one fewer reduction than needed, `131073` leaves mask `3` after 16 steps and `257` leaves mask `3` after 7 steps; each is still unfinished. Algebraically, after `k<n` cancellations of `X^n+1` by `X+1`, the current polynomial is `X^(n-k)+1`, so the final cancellation is essential. The explicit candidate-presence check matters: both negative masks also have higher-degree zero-remainder divisors, so a predicate-only test could miss an omitted degree-one candidate.

## Scope

The finite truth values, candidate counts, candidate remainders, step counts, and control checks follow from the supplied encoded algorithm. A claim about a particular Lean definition, a proved theorem, or the equality of that implementation to `Polynomial` division requires a separate source-level and formal connection. Under the stated bit-to-polynomial interpretation, leading-bit cancellation is the usual long-division operation over `F₂`, and its degree strictly decreases at each step; this explains the `degree(p)+1` bound mathematically. This review does not establish that a specific formalization has proved that connection.

## Reproduction and artifacts

Run from this report directory:

```sh
python3 independent.py > output.json
sha256sum independent.py output.json
```

The successful command exited 0 and produced `output.json` with all 1,110 candidate rows, per-degree summaries, zero-remainder divisors, and both controls. The SHA-256 digests are:

```text
039368283855bf5856539d1d929896fd86edb3a24ede533ebed49b0cede27d80  independent.py
79aed2a77e4ca76876f60ea6c0083bce631fe03f51a56ca7cc2de9da3ac56d5a  output.json
```

The first local invocation failed because this interpreter lacks `int.bit_count`; I changed only the independent parity cross-check to `bin(mask).count("1")`, then reran successfully. No Lean build, scientific experiment, external job, or producer modification was performed.
