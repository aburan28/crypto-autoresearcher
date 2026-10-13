# EigenX adaptive-OneEnd bridge methodology

Date: 2026-10-13
Goal: `GOAL-SSI-2fa82a`
Batch: `BATCH-44a1ce`
Run class: zero scientific runs

## Question

Can a public-only polynomial interface satisfy the exact adaptive bounded-OneEnd oracle calls used by the sourced EndRing reconstruction, and if so does that interface repair the correctly directed reduction and six-obligation gaps for EigenX/CEST-PKE?

This round does not test parameters or implement a scheme. It is a bounded proof/construction search with independent joint ownership.

## Method

1. Re-derive the adaptive query transcript from the frozen primary-source packet. Record the initial input, every dependency of query `E_i`, the allowed oracle output, degree and representation bounds, stopping law, and total reconstruction cost.
2. Generate at most three materially distinct interfaces: a pointwise-total public sampler, a transcript-conditional distribution compiler, and a reduction-local answering or rerandomization route. Each interface must expose algorithms, exact quantifiers, success, retries, aborts, output law, support, and full cost.
3. In a separate producer packet, bind the user name EigenX to CEST-PKE and audit O1--O6. Attempt every arrow in `IND attacker -> transfer information -> adaptive OneEnd interface -> complete EndRing`; label a missing or reversed arrow instead of filling it by assumption.
4. Snapshot both producer packets before review. Reviewers own disjoint joints and remain blind from peer reports. A source-only reviewer re-derives the adaptive oracle contract, and a separate reviewer re-derives the load-bearing reduction direction without reading the producer's conclusion.
5. Compose without voting. Produce a source-linked report, editable Mermaid diagram, browser-faithful SVG, PDF, and visual inspection record. Independently audit the documentation before the ledger decision.

## Controls before belief

The single-distribution control checks that high mass under `D_ER` is not silently upgraded to every adaptive query. The advice control checks that per-instance existence is not called a uniform public algorithm. The reverse-arrow control checks that `EndRing solver -> decryptor` is not called a security reduction. The scalar slice checks whether the argument uses any ring-specific structure. The evaluator-only secret checks complete-ring necessity. Pairing and parsing controls expose public transcript structure and rejection behavior.

## Interpretation boundary

A surviving bridge is not a security theorem. A failed bridge is not a universal impossibility theorem. No attack found is not security evidence. A timeout or unavailable model is infrastructure signal. The closing record must state zero-run accounting and keep `CEST-XFER-KI` distinct from EndRing.

## Required search record

The final report must include positive, negative, and inconclusive routes; exact sources and inspected scopes; a typed correspondence/reduction diagram; an obligation table; limitations; and one next action. The SVG and every PDF page must be inspected, and the report set must be archived with the evidence and decision records.
