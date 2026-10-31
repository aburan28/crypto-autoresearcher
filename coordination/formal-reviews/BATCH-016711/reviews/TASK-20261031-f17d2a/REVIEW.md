# J1 archive and source review — TASK-20261031-f17d2a

**Verdict for J1: holds.** The one archived draw (n=4, n′=4, seed 32201, draw 1, xR=1, basis [9,3,2,12]) binds to the four literal Lean component equations and the indexed witness. This verdict concerns the archive and source representation joint only. J2 owns machine theorem and axiom review; J3 owns the blind derivation.

## Binding and derivation

The reviewed producer tree is `ad91212179e737d829076ca593d608261590ba89`. The archived `draws.json` has SHA-256 `f2c0bd08739c56f0dc24a3a67e4ab367319944c7a7868aef8c67508ac1ef13b2`. Exactly one entry has the tuple `(4,4,1,32201,1,[9,3,2,12])`. Its compact JSON equation list hashes to `89ab8e668c510572bbf9307f105b2eaf46858ad900f0b6b4a2fce8803e0ba6eb`, matching the entry and frozen binding.

A separate script evaluated all 256 Boolean assignments. It interpreted the eight variables as two field elements in the given basis, multiplied in F₂[X]/(X⁴+X+1), evaluated `((x1*x2) + x1 + x2)^2 + x1*x2 + 1`, and applied a Boolean Möbius transform to each of the four output bits. All 15 nonzero field elements had inverses. The resulting ordered component ANFs matched the archived lists and Lean's literal list exactly; term counts were 17, 7, 13 and 4. The full lists are in `raw-checks.json`.

## Ordered rows and witness

For each equation in order, I tried multiplier masks 0–255 in order, XORed duplicate output monomials after mask OR, and kept a row when all surviving masks had Boolean degree at most the requested bound. This matches the `equations.flatMap` and `List.range 256` order in `BooleanParityFiniteCertificate.lean`. There are 28 degree-two and 80 degree-three rows, with ranks 11 and 53. The Lean `comboMask` selects 23 zero-based degree-three row indices: 2, 3, 4, 6, 7, 8, 10, 11, 13, 14, 15, 17, 19, 20, 23, 24, 30, 36, 41, 44, 45, 47, 50. Their `(index, equation, multiplier)` triples are retained in `raw-checks.json`.

XOR of those rows is `6277101735386703064921270320751746415339343215057222047510`, exactly Lean's `witnessNat`. Its 18 present monomial masks all have degree at most two. The coefficient functional at masks 80 and 192 is zero on every degree-two row and one on the witness; adjoining it raises degree-two rank from 11 to 12 and leaves degree-three rank 53. This checks the source-to-Lean indexing and finite linear-algebra claim, without executing Lean.

## Controls and execution boundary

Changing the first archived component's first monomial from mask 0 to 1 changed the canonical equation hash to `48dcb1bbf7980c2fad289730bbb274dba8de7037c7e75c0cf491da7ee81d7657`; it no longer matched the bound hash or Lean literal. The pinned producer `check_source_binding.py`, run against a separate copied tree with Python 3.11.17, passed the unmodified baseline (exit 0) and rejected that changed archive at its equation hash assertion (exit 1). The first component multiplied by mask 1 has three extra monomials under set union, masks 1, 17 and 129; XOR parity removes them. A first attempt to run the pinned checker with the host's Python 3.9.25 failed on `int.bit_count`, so the successful baseline and mutation control used Python 3.11.17. This is an interpreter compatibility issue, not a source-binding result.

This review used no Lean or Cargo build, new scientific trial, cloud job or instance. The archived draw is a frozen finite input; the review does not establish transfer to another draw or parameters.

## Artifacts

`j1_check.py` is the separate calculation; `raw-checks.json` is its full output. `producer-baseline-py311.json` and its stdout/exit file capture the copied-tree producer baseline. `producer-mutation-py311-stderr.txt` and its exit file capture the changed-archive rejection. `review_attestation.yaml` lists all substantive reads. `SHA256SUMS` freezes artifact bytes.
