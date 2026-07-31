---
id: KN-LIT-7261
type: literature
title: "An Elliptic Curve Trapdoor System"
authors:
  - "Edlyn Teske"
year: 2003
venue: "IACR Cryptology ePrint Archive 2003/058; Journal of Cryptology 19(1):115–133, 2006"
identifiers:
  eprint: "2003/058"
  doi: "10.1007/s00145-004-0328-3"
  arxiv: null
  url: "https://eprint.iacr.org/2003/058"
tags: [ecdlp, elliptic-curve, isogeny, weil-descent, ghs, trapdoor, key-escrow, binary-field, teske]
confidence: reported
citation_verified: true
added: "2026-07-24"
upgraded: "2026-07-31"
superseded_by: null
---

## Contribution

Constructs an elliptic-curve trapdoor / key-escrow system over $\mathbb{F}_{2^{161}}$:
a secret curve $E_s$ on which the Gaudry–Hess–Smart Weil-descent attack reduces
ECDLP to a feasible hyperelliptic Jacobian DLP (genus 7 or 8), and a public
isogenous curve $E_{\mathrm{pb}}$ for which the best known attack is parallel Pollard rho.
The trapdoor holder (trusted authority) is given $E_s$ (and path information) and
must still invest substantial computation to recover individual keys.

## Key claims (verified from eprint abstract + archived PDF)

- Public/secret pair $(E_s, E_{\mathrm{pb}})$ over $\mathbb{F}_{2^{161}}$ with $E_{\mathrm{pb}}$ isogenous to $E_s$.
- GHS on $E_s$ yields a genus-7/8 hyperelliptic DLP that is feasible but nontrivial.
- Best attack on $E_{\mathrm{pb}}$ is parallelized Pollard rho.
- Escrow design deliberately makes widespread wiretapping expensive even for the
  trapdoor holder.
- Construction uses techniques of Menezes–Qu to generate GHS-weak $E_s$ and
  Galbraith–Hess–Smart isogeny methods to reach a rho-hard public curve.

## Relevance to GOAL-ECTD-001

Canonical binary-field trapdoor architecture this goal seeks a prime-field analogue of.
Direct transfer to generic $\mathbb{F}_p$ fails because class invariants share order /
embedding degree and $\mathbb{F}_p$ has no proper subfields for Weil descent.

## Local copies

- `inputs/ECTD-TESKE-20260731/sources/teske-2003-058.pdf`
  (fetched 2026-07-31 via Wayback Machine mirror of eprint PDF; direct eprint
  returned HTTP 403 from this environment; sha256
  `8d889ae0b1b03f77a9b821aae04b255df235f8abc0831598ded7ff1c723f2646`, 16 pages)
- Prior stub referenced missing `downloads/teske.pdf`; that path remains absent.
- eprint abstract page fetched live: https://eprint.iacr.org/2003/058
