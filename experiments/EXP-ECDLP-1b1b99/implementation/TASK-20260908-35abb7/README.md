# Corrected CM implementation — no scientific execution

This directory is the scoped implementation package for `TASK-20260908-35abb7`, archived by `TASK-20260908-163823`.  It implements the prospective corrected contract for `EXP-ECDLP-1b1b99`; it neither searches an approved CM fixture nor measures any protocol cell.

The normal command is deliberately inert:

```sh
/var/tmp/sage-10.9-current/local/bin/python3 driver.py --dry-run
```

The bounded regression command is also nonexperimental:

```sh
/var/tmp/sage-10.9-current/local/bin/python3 tests.py
```

It contains sixteen test methods on hand-chosen tiny objects and temporary paths.  It does not enumerate any frozen interval, create a `RUN-*` identifier, use a real launch signature, inspect a private key, or write artifacts in the campaign `runs/` tree.  The fixed F₇ curve in the tests checks finite formulas only; it is not a protocol fixture.

`driver.py` implements the future fixed pipeline only behind `run_authorized`.  That function is absent from the CLI and first requires all of the following: exact source and runtime bytes; a reviewed source ancestor; the fixed CyPari2/PARI lock; the fixed Ed25519 public PEM and OpenSSL verifier; a canonical detached payload; a Coordinator-bound future review/archive tuple; exact run path; and an unused 256-bit nonce.  A malformed, replayed, mismatched, or Bedrock-bearing payload returns a typed refusal before fixture work.

Arm 7 calls `cypari2.Pari.ellmul` under the exact Sage Python 3.14.3/CyPari2 2.2.4/PARI 2.17.1 binding.  It is never implemented through `Curve.mul`; construction, conversion, and output verification remain inside the charged future workload.  PARI backend operation counts remain explicitly unavailable rather than being fabricated as zero.

The package is an implementation artifact, not evidence.  A future Coordinator snapshot and fresh independent implementation/protocol review are still required before any launch admission or scientific conclusion.
