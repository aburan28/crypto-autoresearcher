---
id: KN-TECH-023
type: technique
title: Lattice trapdoors, signature paradigms, and concrete-hardness estimation
tags: [lattice-trapdoor, gpv, fiat-shamir-with-aborts, lwe-estimator, bkz-cost-model, signature, post-quantum, adjacent]
confidence: reported
complexity: signatures ~O~(n) ring/module ops; security set by BKZ/sieving estimates targeting ~128/192/256-bit levels
applicability: constructing lattice signatures and choosing their parameters (post-quantum, adjacent to ECDLP)
source_refs: [KN-LIT-058, KN-LIT-059, KN-LIT-061]
added: 2026-07-23
superseded_by: null
---

## Method
Two dominant lattice-signature paradigms:
- **GPV hash-and-sign** (KN-LIT-058): a short trapdoor basis lets one sample a
  short preimage of a hashed message under the public function; discrete Gaussian
  sampling makes the signature distribution independent of the trapdoor. The
  gadget "G-trapdoor" (Micciancio-Peikert) is the standard efficient construction.
  Basis of Falcon.
- **Fiat-Shamir with aborts** (KN-LIT-059): a trapdoor-free
  commit-challenge-response with REJECTION SAMPLING that forces secret-independent
  transcripts. Basis of Dilithium.
Parameters are chosen with a **concrete-hardness estimator** (KN-LIT-061): run
every known attack (uSVP/embedding, decoding/BDD, dual) under a BKZ/sieving cost
model (KN-TECH-020) and pick parameters meeting a bit-security target.

## Relevance to this program
ADJACENT to the ECDLP mission -- these build and size the post-quantum signatures
that succeed ECDSA. Two genuine methodological links to the corpus: (1) the
estimator's "translate attacks into one fully-charged cost model" discipline
mirrors the program's ECDLP cost accounting; (2) the secret-independent transcript
of both paradigms is precisely the defense against the nonce-leakage lattice
attacks that break ECDSA (KN-TECH-019) -- a discrete-log lesson carried into
lattice design.

## Applicability limits
Concrete bit-security depends on the assumed SVP-oracle model and sieving
heuristics, so estimator outputs carry real uncertainty and shift as cryptanalysis
improves. GPV needs high-precision Gaussian sampling (constant-time floating point
is hard -- Falcon's main implementation risk). None of this bears on ECDLP; it is
recorded to map the replacement primitive's design and costing.
