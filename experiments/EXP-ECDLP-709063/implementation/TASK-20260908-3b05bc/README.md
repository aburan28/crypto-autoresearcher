# Fixed BSGS source component — TASK-20260908-3b05bc

This directory is the eight-file producer package for the portable source
component required by the approved finite definition of `EXP-ECDLP-709063`.
It is deliberately not the experiment runner. It creates no shared instances,
does not allocate a `RUN-*`, does not invoke a rho solve, and records no
scientific or performance observation.

`table.py` contains the one-buffer physical table. The caller passes the only
`bytearray`, whose usable capacity is `E=floor(7*floor(C/16)/10)`. Logical
points, table-hash preimages, and physical slots use separate encoders:

| Domain | Canonical bytes |
| --- | --- |
| Logical point | `<BII`, 9 bytes; `O=(0,0,0)`, affine `(1,x,y)` |
| Hash preimage | `00` for `O`; `04 || uint32_be(x) || uint32_be(y)` for affine |
| Physical slot | `<IIII`, 16 bytes: `x,y,exponent,state`; states 0 empty, 1 affine, 2 `O` |

`bsgs.py` implements NULL 1, Arm A, and Arm B against a caller-supplied
complete public group interface. It accepts no known scalar. All `curve.add`
calls, including identity and doubling calls, are charged once; negation,
hashing, probing, and integer work remain separate. `rho-corrected.py` is the
exact pinned `harness/rho.py` byte sequence except for the approved nested
`_count_mul` replacement. Its hash and before/after span proof are in
`solver-source-bindings.json`.

Run the reserved source suite only through:

```sh
python3 tests.py --final check-receipt.json
```

The parent checker reserves all 320 fixed cases before it launches its worker,
redirects that worker's stdout and stderr before `Popen`, retains and polls the
process handle, and writes the command, terminal exit, individual cases,
actual CPU/wall/RSS telemetry, and complete captured tool output to
`check-receipt.json`. The fixed test group is arithmetic modulo a fixed small
integer and is not an elliptic curve or a declared experiment cell. Observed
RSS is recorded only as diagnostics; it does not claim a hard process guard.

The package requires Coordinator snapshot task `TASK-20260908-9d38e6` and a
fresh independent source review before any integration, shared-instance work,
or experiment launch.
