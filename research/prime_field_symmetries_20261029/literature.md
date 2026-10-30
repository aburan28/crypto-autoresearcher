# Sources checked before implementation

All repository references below are internal/retrieved, not novelty claims.

- `crypto-autoresearcher` original F1 source pin
  `cdd2150922211f180ab3d8c3f3b248356c78f025`, plus completed source pin
  `6164ec00d419cbe43520fbdda19f85f6bbde44cf` used for C1. Read the derivation,
  core/exterior construction, S4 expressions, fixed inputs, signed recovery,
  reference and prepared second-pass workflow. Target-x degree is visibly at
  most four in every frozen S4 coefficient. Low-degree membership is distinct
  from decomposition/extraction cost.
- Petit, Kosters, Messeng, *Algebraic approaches for the Elliptic Curve Discrete
  Logarithm Problem over prime fields*, PKC2016, sections2.4 and3.1–3.5:
  <https://people.maths.ox.ac.uk/petit/files/16PKC_primeECDLP.pdf>. Retrieved
  primary PDF digest `a53030a6cde720c354aebfb65b1eb01e07766ce2d26e543d77f2516c0a49ef5b`;
  direct prior reading and coordinator re-reading of section3.2/page8 are
  recorded in the C1 source notes. Solver and linear-algebra costs remain
  charged. No generic-prime scaling inference follows from a small fibre.
- [crypto ARCHIVE_FACTOR_BASE_COMPARISON.md](https://github.com/isogeny-labs/crypto/blob/f4f73e224a34b96aa5bbd7bb7bde6c6e51b6011f/docs/ic/ARCHIVE_FACTOR_BASE_COMPARISON.md),
  retrieved in full. Existing archive import verifies eigenvalues and signed
  coefficients, audits useful rank and target coefficients, preserves partials
  until elimination, and explicitly distinguishes torsion-coset domains.
  Narrow u64 archive widths are a real implementation boundary for P-256.
- [crypto GLV invariant-base notes](https://github.com/isogeny-labs/crypto/blob/f4f73e224a34b96aa5bbd7bb7bde6c6e51b6011f/research/notes/index-calculus/RESEARCH_GLV_INVARIANT_FACTOR_BASES.md),
  retrieved; read sections2 and8.7. Use the exact orbit-length, phase and
  cofactor-domain cautions. A torsion translation is not a scalar endomorphism
  on the prime subgroup before the stated projection. No random-overlap or
  random-graph yield model is adopted from these notes.
- [Sage official Weierstrass morphism source](https://github.com/sagemath/sage/blob/af5a560b31a73ad1957f925a2d5714a6d561a324/src/sage/schemes/elliptic_curves/weierstrass_morphism.py),
  retrieved/read `baseWI` and isomorphism enumeration. Its coordinate convention
  uses inverse u relative to this audit's point map. Coefficient obligations
  are independently derived by substitution; char2/3 cases are not imported.
- `research/prym_experiment_design_20261019/implementation/{census,independent,relations}.py`,
  `research/prym_rank_census_20261025/check_census.py`, and
  `research/prym_factor_base_width_20261025/check_inputs.py`: read complete target
  source semantics, canonical identities, zero completion and anchor projection.
- `docs/research/cross-isogeny-symmetry-index-calculus.md`: read S01–S14 and
  invariant/domain/phase conditions. Template caching and model switching have
  existing org workstreams; this prototype is implementation follow-through.

Org search also located the crypto factor-base arity literature review and
cryptanalysis factorbase-census curve-choice appendix. Search excerpts alone
are not primary-source support and were not used to transfer binary-field
performance or torsion claims to these prime-field cases. No KB connector or
exhaustive prior-art survey was available; unsuccessful retrieval is not an
absence-of-prior-work proof.
