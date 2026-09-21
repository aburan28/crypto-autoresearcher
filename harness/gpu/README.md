# gpu — batched rho step throughput, CPU and CUDA from one definition

Measures how many Pollard-rho **steps per second** a machine sustains, so a
campaign cost model rests on a number from the hardware that would run it
rather than one inherited from somebody else's paper.

| file | role |
|---|---|
| `mont256.h` | 256-bit Montgomery field arithmetic + one affine r-adding step. Compiles **unchanged** as CUDA `__device__` code and as plain host C. |
| `rho_kernel.cu` | The CUDA kernel: one thread owns a group of walks and batch-inverts across them. |
| `mont256_selftest.c` | Runs `mont256.h` on the host and prints final walk state, for differential testing against Python. |
| `../bench_rho_throughput.py` | Driver: builds the instance, runs three implementations, checks them against each other, times them, emits a JSON record. |

## Why the header is dual-target

A GPU benchmark whose field arithmetic is subtly wrong reports a throughput
number for an operation nobody wanted. Because `mont256.h` also compiles as
host C, the exact arithmetic the kernel runs is differentially tested against
an independent Python implementation **on any machine, with no CUDA toolchain
and no GPU** — the same walk, compared limb for limb, including the scalar
accumulators and the distinguished-point count. Only the launch plumbing in
`rho_kernel.cu` is left untested by that, which is the smallest untested
surface this design admits.

The driver refuses to print any rate if the implementations disagree.

```sh
python -m harness.bench_rho_throughput --self-test          # verify only
python -m harness.bench_rho_throughput --seconds 5          # CPU
python -m harness.bench_rho_throughput --seconds 10 --gpu \
    --cpu-usd-per-hour 1.50 --gpu-usd-per-hour 0.60 --out bench.json
```

The GPU leg needs CuPy with a working CUDA runtime; NVRTC compiles the kernel
at run time, so no separate build step and no `nvcc` at install time.

## What the number means, and what it does not

Measured: branch selection, the affine add with batched inversion, the `(a, b)`
updates mod `n`, and the DP test, for walks already resident in memory.

**Not** measured: the host-side DP table, transferring DPs off the device, and
the collision search. At realistic DP rates those amortize to a small
correction, but they are not zero — so every rate here is an **upper bound** on
end-to-end campaign throughput. The emitted JSON says so in its `scope` field;
quote it with the rate, per AGENTS.md rule 4.

Two further honesty notes carried in the record itself:

- The all-cores CPU figure is an **extrapolation** by core count from a
  single-core measurement, not a measurement. Memory bandwidth and clock
  behaviour under full load will move it.
- `usd_per_hour` prices are **user-supplied inputs**. The cost ratio inherits
  their accuracy entirely and is not evidence about hardware.

## Known throughput left on the table

Deliberately not optimized, because correctness-first was the point and each of
these trades auditability for speed:

- **Memory layout.** Walk state is thread-contiguous, not a coalesced
  structure-of-arrays. On CUDA this is the first thing to fix.
- **Inversion.** Fermat (`a^(p-2)`, ~381 multiplications) rather than a binary
  extended-Euclid. Batched across `--walks-per-thread` walks it costs a few
  multiplications per walk either way, so the simpler one is kept.
- **Coordinates.** Affine, which is what makes batched inversion the whole
  story. A Jacobian/Montgomery-ladder variant changes the balance.
- **The negation map.** The standard √2 for rho on curves is not implemented;
  it interacts with fruitless cycles and deserves its own contract.

## Measurement protocol

Rho step rates are noisy under thermal and neighbour effects. For anything
headed to an evidence record: at least three runs on an otherwise idle machine,
report the median and the spread, record `machine` verbatim from the JSON, and
name the driver's commit. One run is an anecdote.
