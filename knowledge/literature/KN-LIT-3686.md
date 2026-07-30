---
id: KN-LIT-3686
type: literature
title: "Energy-Efficient Software Implementation of Long Integer Modular Arithmetic?"
authors:
  - "Johann Großschädl"
  - "Roberto M. Avanzi"
  - "Erkay Savaş"
  - "Stefan Tillich"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, implementation, provable-security, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper investigates performance and energy characteristics of software algorithms for long integer arithmetic. We analyze and compare the number of RISC-like processor instructions (e.g. singleprecision multiplication, addition, load, and store instructions) required for the execution of different algorithms such as Schoolbook multiplication, Karatsuba and Comba multiplication, as well as Montgomery reduction.

## Key claims (as reported)
- Our analysis shows that a combination of Karatsuba-Comba multiplication and Montgomery reduction (the so-called KCM method) allows to achieve better performance than other algorithms for modular multiplication.
- Furthermore, we present a simple model to compare the energy-efficiency of arithmetic algorithms.
- This model considers the clock cycles and average current consumption of the base instructions to estimate the overall amount of energy consumed during the execution of an algorithm.
- Our experiments, conducted on a StrongARM SA-1100 processor, indicate that a 1024-bit KCM multiplication consumes about 22% less energy than other modular multiplication techniques.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/006 (1).pdf`
- `downloads/006 (2).pdf`
- `downloads/006 (3).pdf`
- `downloads/006.pdf`
