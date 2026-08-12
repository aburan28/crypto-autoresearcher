# TASK-20260722-107 review package

## Purpose

Bind the immutable BATCH-001 producer artifacts and the failed
`TASK-20260722-102` snapshot receipt into a reviewable package without
rewriting history or changing producer substance.

## Integrity event

Commit `a5de43ed7a41313eda1abadbb6b8c47094c203d8` contains the producer
artifacts and a provisional receipt, but the harness verifier rejected it
because the commit message named the producer/record and not the archive
task ID `TASK-20260722-102`. Under AGENTS.md this is an evidence-integrity
failure, not a mathematical result about ECDLP.

`TASK-20260722-102` remains `invalid`. This repair does not convert that
gate into a success.

## Hash-bound artifacts

| Path | SHA-256 |
|---|---|
| `.../TASK-20260722-101/candidate_report.yaml` | `b3461bcf9f19a592fc73810a9f7237974628f84cbe3e7386e97c586a605abfdc` |
| `.../TASK-20260722-101/mechanism_note.md` | `37a59f20933655ce8baa7080dddd98ad38c1ac60956015de06df8200f438c47a` |
| `.../TASK-20260722-102/snapshot-receipt.json` | `a50de45d651221a0d6b310e82cb1e2547551c38d83e3611315586c0b4d9f88a6` |

## Producer content (unchanged)

The producer concluded:

- no new conjecture survived corpus deduplication;
- the narrowest open item is the known obligation
  `OBL-ZR-COMPACT-CONSTRUCTOR-001`;
- the cheapest next gate is a theorem-only typed dependency audit;
- scope is non-operational academic mathematics only.

No proposal, identity, or toy result is a cryptographically relevant
breakthrough.

## Review instruction

Independent red-team review may proceed only after `TASK-20260722-108`
archives this package with a verified Git receipt. Review should challenge
novelty, oracle assumptions, asymptotic accounting, and the cheapest
falsification gate, while preserving the failed-snapshot integrity note.
