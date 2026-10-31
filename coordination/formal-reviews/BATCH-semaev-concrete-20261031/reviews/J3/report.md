# J3 blind Boolean derivation

## Scope and input

This is an independent finite calculation from `blind-input.yaml` at commit
`9419f7cc32f9e86d3b93f2f738a25fd0ffb71f06`. The card's SHA-256 is
`f3af5f1bdc04cb922ca5cf5fc79c98fce69f7b6fec7c4f72c73965a290be24b8`.
It specifies `F2[X]/(X^4+X+1)`, low-bit-first field coordinates, basis
`[9,3,2,12]` for each of `x1,x2`, `xR=1`, `a6=1`, and

`S3 = (x1*x2 + x1 + x2)^2 + x1*x2 + 1`.

Bit positions 0 through 3 select the stated basis for `x1`; positions 4
through 7 select it for `x2`. An ANF support mask `m` denotes the squarefree
monomial selected by those bit positions. In a 256-bit row vector, bit `m`
is its coefficient. All arithmetic below is over F2.

## Derived ANFs

In component order, the support masks are:

| Component | ANF support masks |
| --- | --- |
| 0 | 0, 1, 2, 8, 16, 17, 24, 32, 34, 36, 40, 66, 68, 128, 129, 130, 136 |
| 1 | 8, 17, 34, 68, 72, 128, 132 |
| 2 | 1, 2, 4, 8, 16, 18, 32, 33, 34, 64, 68, 128, 136 |
| 3 | 1, 8, 16, 128 |

`derive.py` evaluates the field formula at all 256 bit assignments and applies
the Boolean Möbius transform. It evaluates each resulting ANF at all 256
assignments again and asserts exact agreement with the field formula.

## Compatible row spaces

For component `k` and multiplier `m=0..255`, the row is the XOR of unit
vectors at positions `a|m` for each ANF mask `a`. It is retained at degree
`D` exactly when every nonzero output position has Hamming weight at most
`D`. Zero rows are discarded. `raw.json` records each compatible row and
its support.

| Degree bound | Nonzero compatible rows | F2 rank |
| --- | ---: | ---: |
| 2 | 12 | 11 |
| 3 | 64 | 53 |

The D=3 span contains a degree-at-most-two vector outside the D=2 span.
Its support masks are
`[1,2,4,8,9,10,12,16,18,20,32,40,48,64,65,128,144,192]`, and its
256-bit raw value is

`0x0000000000000001000000000001000100000000000000030001010100151716`.

XOR these 23 D=3 rows, listed as `(component, multiplier mask)`:

`(0,2), (0,4), (0,8), (0,32), (0,64), (0,128),
(1,1), (1,2), (1,8), (1,16), (1,32), (1,128),
(2,1), (2,2), (2,16), (2,32),
(3,3), (3,10), (3,20), (3,33), (3,34), (3,40), (3,65)`.

The full row values and their zero-based indices in `raw.json` are recorded
under `new_low_degree_class.row_combination`. The XOR has no cubic or
higher-degree bit. Reduction against an echelon basis of the D=2 rows leaves

`0x0000000000000000000000000000000000000000000100000001010200000522`,

which is nonzero. An independent linear separator is the dot product with
the 256-bit vector

`0x0000000000000000000000000000000000000000000000000000000000000408`.

Its only active monomial positions are `3` and `10`. It evaluates to zero
on all 12 D=2 rows and to one on the displayed witness. Thus the strict
containment claim has both an echelon remainder and a separating functional.

## Controls

For component 0 multiplied by mask 1, ANF input masks 0 and 1 both map to
output mask 1. Their two contributions cancel: raw count 2, parity 0, and
the retained row's coefficient at mask 1 is 0. This checks that Boolean
monomial multiplication uses XOR parity after squarefree reduction.

For a sensitivity control, flip the coefficient of monomial mask 1 in
component 0 only. The mutated spaces still have 12 D=2 rows of rank 11 and
64 D=3 rows of rank 53, but one D=2 row and nine D=3 rows change. For
example, component 0 multiplied by mask 0 changes from
`0x0000000000000000000000000000010700000000000000140000011501030107`
to
`0x0000000000000000000000000000010700000000000000140000011501030105`.
`raw.json` records the other changed-row examples. This is a row-level
sensitivity check; unchanged ranks alone would miss the mutation.

## Reproduction, resource use, and reading attestation

Run `python3 derive.py` in this directory. The implementation uses Python
3.9.25 standard library only, with 256-bit integer row vectors. The observed
repeat run used 14,692 KiB maximum resident memory and 0.07 seconds wall
time. No Lean, Lake, Cargo, scientific trial, cloud run, or heavy build was
used.

Before this report was frozen, the only scientific input read was the named
blind card. I also read repository `AGENTS.md` for governance, Conductor
T-1062 metadata and command help to claim the available task, and J3 files
that I created while checking the derivation. I did not read the plan,
input-bindings, Semaev source, reports, receipts, sibling outputs, or earlier
conversation. Conductor claim: T-1062, lease
`b2ab4629-48bf-4f84-b086-7617245c49bd`, epoch 1. The checkout was clean at
the named commit before writing J3 artifacts.

The script and raw JSON are the audit trail. Their SHA-256 digests are in
`SHA256SUMS`; this report is deliberately excluded from that manifest to
avoid a self-reference.
