# Lean builds run by the sheriff session (bare `lean`, no Mathlib)

Disk allowed only the Mathlib-free import closures. Toolchain: formal/lean-toolchain
(leanprover/lean4:v4.35.0-rc1) via elan; modules compiled in dependency order with
`LEAN_PATH=<scratch>/out lean -o <olean> formal/CryptoResearch/<m>.lean` from a read-only
crypto-autoresearcher tree at e9b91d62a9 (sources.sha256).

- built, exit 0, no errors: Endosweep/{Discriminant,NistCertificates,DkExact,DkExactBatch4},
  Semaev/{BooleanParityFiniteCertificate,FiniteEquationSemantics} (build-*.log)
- axioms: `Audit.lean` prints axioms for all 30 theorems of DkExactBatch4,
  BooleanParityFiniteCertificate and FiniteEquationSemantics -> axioms.out:
  every one is "no axioms", [propext] or [propext, Classical.choice, Quot.sound]
- proves-too-much: ptm/RankMutant.lean (rank (rows 3) = 54, projectedRank 3 = 40) and
  ptm/DkMutant.lean (one digit of E-521's trace changed) both FAIL to elaborate, as required.

Not built (Mathlib.Tactic / Mathlib closure does not fit on disk): Binstd/*, FrobTrace/*, NCP/*,
Semaev/{Certificate,BooleanParitySemanticRank,DegreeThreeRank,Filtration}Certificate.
