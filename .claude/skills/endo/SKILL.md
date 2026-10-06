---
name: endo
description: "Assess endomorphism rings, CM discriminants, conductors, GLV/GLS decompositions, Frobenius or tau-adic structure, and scalar multiplication cost claims using existing endosweep artifacts. Use for endomorphism analysis and implementation planning, not a discrete-log attack campaign. Run requests use run."
---

# Endomorphism analysis

Read `harness/endosweep/README.md`. Consult `harness/endosweep/targets.py`, `quadorder.py`, `lattice.py`, `costmodel.py`, and the relevant explicit map module as needed. Use `tools/isogeny_class_screen.py` for its documented invariant screen, not as evidence of a new logarithm algorithm.

1. Bind field, group/subgroup, Frobenius trace, order identification and its proof status. Distinguish D=t^2-4q, the fundamental discriminant, conductor, and actual endomorphism order.
2. Audit a candidate's ring relation, norm/degree, subgroup eigenvalue, exceptional points and field of definition. Keep map construction and point tests separate from a universal proof.
3. Check lattice congruences and scalar reconstruction with the supplied certificate. Account for map evaluation, additions, doublings, tables, conversion and preprocessing in the same operation model.
4. Label endosweep operation counts as modeled. Use bench for measured scalar-multiplication comparisons. A GLV scalar-multiplication gain is not automatically a rho or ECDLP gain.
5. Distinguish explicit implementations, structural registry entries, synthetic toy objects, and assumed cost-table rows. Check the current source before selecting a mode.
6. Return the formulas, implemented map/certificate paths, modeled and measured columns, and the next unresolved check. Route supplied-map transfers to transfer and actual existing trials to run.

Follow current `AGENTS.md` authority, provenance and immutable-record rules. This profile adds no prerequisite to `run`; preserve explicit execution requests.
