# Generation of the B-163 seed is unknown

- **Status:** `open`
- **Kind:** unknown cause; missing historical generator program or run log. Also an implementation gap (native ports owed for the Python-only searches)
- **Affected work:** [KN-LIT-d2f917](../knowledge/literature/KN-LIT-d2f917.md) ("The B-163 seed is unexplained", and its 2026-10-22 addendum), [KN-FIND-cee88d](../knowledge/findings/KN-FIND-cee88d.md) (finding 2: "B-163 is not explained"), [provenance reproduction bundle](../research/nist_seed_provenance_20261016/README.md) ("Open"), [EV-SCURVE-e9d71b](../ledger/evidence/EV-SCURVE-e9d71b.yaml) (boundaries). Cross-repository: [aburan28/crypto PR #2410](https://github.com/aburan28/crypto/pull/2410), [B-163 searches T13 and T14](https://github.com/aburan28/crypto/blob/2275ed6ec3a53e1a7df8dcb0aa48d1ac59af9a79/research/nist_basepoint_provenance_20261017/README.md)
- **Next action owner:** unassigned. A run in this repository needs a Coordinator-approved contract.
- **Last updated:** 2026-10-22

## Problem

We cannot say how the B-163 seed `85E25BFE 5C86226C DB12016F 7553F9D0 E693A268` was produced, because no tested generator reproduces it and the 1998 generation code is unavailable, while the other four binary-curve seeds are explained.

B-233, B-283, B-409 and B-571 are five consecutive `lrand48()` words, big-endian in 32-bit slots, after `srand48(s)` with `2s` on 1998-04-17 (KN-FIND-cee88d, finding 2, replicated). B-163 matches no member of that reading family. The seed is the real one: in the follow-up, the normal-basis `b` of B-163 equals the SHA-1 output of this seed in exactly one orientation (`out/gnb.out`, PARI/GP, unvalidated). The seed value above is as listed in the follow-up's `snapshot/lib/others.py`; this Coordinator did not retrieve FIPS 186-2. This blocks a complete account of the binary-curve parameters. It blocks no ECDLP statement.

## Evidence and uncertainty

- **Observed (aburan28/crypto PR #2410, open and unmerged, branch head `2275ed6e` as read on 2026-10-22; no independent validation):** T13, C library generators (glibc and 4.3BSD `random()`, SysV, BSD and MSVC `rand()`), seeds equal to 1997-98 UNIX times `t` and `t/2`, depth 2048, byte and 16-bit layouts in both byte orders: the README reports 23,330 record lines, every hit line a planted control, 0 hits in the 12 target layouts (`out/b163_brute.out.gz`, C). T14, drand48 family with any single-byte edit, every short window at widths 8, 15, 16, 24, 31 and 32: no hit, and a one-byte-corrupted P-256 control found (`out/b163_edit.out`, Python snapshot, an observation even in aburan28/crypto until a native port reproduces it).
- **Earlier observation:** the bundle's seed-agnostic drand48-family and FreeLIP scan included the B-163 seed, with no hit (bundle README, "External analyses"; outside the repository, Python). `CORR-20261022-b3c8a5` does not affect this part.
- **Derived (checkable from the seed alone):** the first bytes of words 1, 3 and 5 are `0x85`, `0xDB` and `0xE6`, so those three words have their top bit set. `lrand48()` returns values below 2^31. So B-163 cannot be five unedited `lrand48()` words in 32-bit slots, the layout of its four siblings, and no single edit can make it one. Any generator whose outputs are below 2^31 is excluded in that layout without a search. The other four seeds have all twenty top bits clear. Whether the bundle's lrand48-slot lattice read only the low 31 bits of each word is not stated in the records read here.
- **Suspected explanations:** a different layout or generator from its siblings; more than one edit; a source that is not a seeded generator. Labelled conjectures; none is observed.
- **Missing capability:** the 1998 generation code or logs; native ports of the Python-only searches.
- **What this evidence does not establish:** that B-163 is not generator output, that it was chosen deliberately, or anything about ECDLP hardness. T13 and T14 cover only the drand48 family and the five C generators, with timestamp seeds for the latter; a B-163 seed from another source, or with more than one edit, is untested (follow-up "Caveats").

## What would unblock it

- [ ] Contemporaneous code, logs or documentation that, replayed from stated inputs, outputs the B-163 seed, with sound provenance.
- [ ] Or a generator and edit model declared before it is run, implemented natively in C or Rust, with planted controls found, that reproduces all 160 bits, or all bits outside a declared edit set, with a stated chance bound of at most 2^-64, then replicated by an independent session.

Either explains the seed. A model shared with B-233 to B-571 would also tie it to the same 1998-04-17 process. Neither bears on ECDLP.

## Next discriminating step

- **Action or proof obligation:** test the model "B-163 is the sibling `lrand48()` process with the top bit of some words set": recover a 48-bit state from the low 31 bits of each of the five words alone, natively in C or Rust, in both word orders, and, on a hit, walk back to the nearest `srand48`-form state and compare its date with the 1998-04-17 runs.
- **Inputs and controls:** the B-163 seed; the four sibling seeds with their top bits forced to 1 in words 1, 3 and 5 as positive controls, which must be recovered; random 160-bit strings as negative controls.
- **Execution limits and stop condition:** one lattice recovery per word order and alignment, as declared before running; stop at the first hit and preserve it.
- **Outcomes and next actions:** a hit says the seed is lrand48 output with three top bits set (a layout or edit fact) and gives a date to compare with its siblings; a null excludes this model, and the next step becomes the C generators of T13 over their full 32-bit seed space instead of timestamps only; a missed control means the detector is blind; an infrastructure failure supports no inference.
- **Recheck trigger:** PR #2410 merging, a native port of T14 or of the bundle's scan, or new primary-source material.

A planned step is not a completed experiment. Apply the existing execution, review, budget, and archival rules before acting on it.

## Resolution and history

2026-10-22 (Coordinator, DEC-20261022-4e7b19): Opened from searches T13 and T14 in aburan28/crypto PR #2410 and the top-bit observation above. Unresolved. This record is a named obstruction, not evidence. It changes no goal, hypothesis or SafeCurves status.
