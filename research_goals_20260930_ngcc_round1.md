# Research Goals 2026-09-30 — Chinese NGCC round-1 algorithms

**Date anchor:** 2026-09-30

**Status:** Opening record for one active goal. Nothing here is evidence.
Published attacks named below are literature pointers. This program has not
reproduced any of them.

## What was asked

The user asked to make the Chinese NGCC algorithms targets, and supplied
Markku-Juhani O. Saarinen, *Chinese NGCC Algorithms: The First Week of AI
Cryptanalysis* (IACR ePrint 2026/2266, 2026-09-29).

ICCS published 119 first-round candidates on 2026-09-20: 34 signatures, 41
KEMs, 9 key-exchange protocols, and 35 hash functions. One goal owns that
population. One hundred nineteen empty campaigns would each have needed an
attack object invented before the specifications were read.

| Goal | Question | Population |
|---|---|---|
| `GOAL-NGCC-6c8a52` | `RQ-NGCC-f52138` | the 119 round-1 candidates |

Opened by `DEC-20260930-713445`. NGCC is excluded from the ECC area set.
The goal is ranked after every ECC goal that has a ranked task.

## Where the roster came from

`inputs/ngcc-round1-20260920/candidates.yaml` joins the public harness
tables retrieved 2026-09-30 from `ngcc-dev/ngcc-harness`:

- `downloads.csv` — stable id, official name, zip, download URL, page, forum
- `sign.csv`, `kem.csv`, `kex.csv`, `hash.csv` — official name and submitters

The join checks that each `sign-01` style id matches its category and
number, and that the algorithm name agrees across the two tables. The
counts are 34, 41, 9, and 35.

`paper_mentions.yaml` lists finding identifiers printed in ePrint 2026/2266
and joins them to roster ids by the identifier prefix (`sign-29-1` belongs
to `sign-29`). One paper name does not join: **HEP-QC** is not the name of
any roster row, so it is left unmatched. Family totals in the paper's
Table 1 are not copied onto unnamed candidates. The three SQIsign
submissions and NIIKE are the families the paper actually names.

## What this goal will not do first

The first ranked work is reproduction of a design-level primary break with
a small witness, not a sweep of implementation bugs and not a 2^256
shortfall against a 512-bit claim. The goal's `next_action` names Tins,
Facto-DSA-128, MoFang, Neulaser, and Chinith as the leads to rank. A
result that exists only against the ICCS placeholder hash is out of scope.

Isogeny attacks on the problem, rather than on the submitted NGCC parameter
sets, stay with `GOAL-SQISIGN-001`, `GOAL-SQISIGN-002`, `GOAL-SSI-001`, and
`GOAL-CSIDH-001`.
